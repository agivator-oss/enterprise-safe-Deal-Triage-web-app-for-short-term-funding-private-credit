from __future__ import annotations

from fastapi import APIRouter, Depends, File, HTTPException, Request, UploadFile
from fastapi.responses import Response
from sqlalchemy.orm import Session

from backend.core.config import settings
from backend.db.session import get_db
from backend.llm import get_llm_client
from backend.models import Deal, DealAnalysis, DealDraft, DealTerms, Document, LLMRun
from backend.schemas import (
    AnalysisResponse,
    DealCreate,
    DealOut,
    DocumentOut,
    ExtractedTerms,
    ICDraft,
    TermsUpdate,
)
from backend.services.analysis import analyze
from backend.services.audit import audit
from backend.services.export_pdf import build_export_pdf
from backend.services.prompts import ensure_prompt_version, load_prompt_template
from backend.services.redaction import redact, redact_obj
from backend.services.text_extraction import extract_text
from backend.storage.local import LocalStorage
from backend.utils.hashing import sha256_bytes, sha256_text
from backend.utils.sanitize import sanitize_text

router = APIRouter(prefix="/deals", tags=["deals"])


def _actor(request: Request) -> str:
    return getattr(request.state, "actor", "anonymous")


def _get_deal(db: Session, deal_id: str) -> Deal:
    deal = db.query(Deal).filter(Deal.id == deal_id).one_or_none()
    if not deal:
        raise HTTPException(status_code=404, detail="Deal not found")
    return deal


def _storage() -> LocalStorage:
    return LocalStorage(root=settings.storage_root)


@router.post("", response_model=DealOut)
def create_deal(payload: DealCreate, request: Request, db: Session = Depends(get_db)):
    deal = Deal(name=payload.name)
    db.add(deal)
    db.flush()

    audit(db, actor=_actor(request), action="create_deal", deal_id=deal.id, metadata={"name": payload.name})
    db.commit()

    return DealOut(id=deal.id, name=deal.name, created_at=deal.created_at.isoformat())


@router.get("", response_model=list[DealOut])
def list_deals(db: Session = Depends(get_db)):
    deals = db.query(Deal).order_by(Deal.created_at.desc()).all()
    return [DealOut(id=d.id, name=d.name, created_at=d.created_at.isoformat()) for d in deals]


@router.get("/{deal_id}")
def deal_detail(deal_id: str, db: Session = Depends(get_db)):
    deal = _get_deal(db, deal_id)

    docs = db.query(Document).filter(Document.deal_id == deal_id).order_by(Document.created_at.desc()).all()
    terms = db.query(DealTerms).filter(DealTerms.deal_id == deal_id).one_or_none()
    analysis = db.query(DealAnalysis).filter(DealAnalysis.deal_id == deal_id).one_or_none()
    draft = db.query(DealDraft).filter(DealDraft.deal_id == deal_id).one_or_none()

    return {
        "deal": {"id": deal.id, "name": deal.name, "created_at": deal.created_at.isoformat()},
        "documents": [
            {
                "id": d.id,
                "deal_id": d.deal_id,
                "filename": d.filename,
                "sha256": d.sha256,
                "created_at": d.created_at.isoformat(),
            }
            for d in docs
        ],
        "terms": terms.terms_json if terms else None,
        "citations": terms.citations_json if terms else None,
        "confirmed_fields": terms.confirmed_fields_json if terms else None,
        "analysis": {
            "metrics": analysis.metrics_json,
            "overall_triage": analysis.overall_triage,
            "risk_flags": analysis.risk_flags_json,
            "diligence_questions": analysis.diligence_questions_json,
        }
        if analysis
        else None,
        "draft": draft.draft_json if draft else None,
    }


@router.get("/{deal_id}/documents", response_model=list[DocumentOut])
def list_documents(deal_id: str, db: Session = Depends(get_db)):
    _get_deal(db, deal_id)
    docs = db.query(Document).filter(Document.deal_id == deal_id).order_by(Document.created_at.desc()).all()
    return [
        DocumentOut(
            id=d.id,
            deal_id=d.deal_id,
            filename=d.filename,
            sha256=d.sha256,
            created_at=d.created_at.isoformat(),
        )
        for d in docs
    ]


@router.post("/{deal_id}/documents")
async def upload_document(
    deal_id: str,
    request: Request,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    _get_deal(db, deal_id)

    if not file.filename:
        raise HTTPException(status_code=400, detail="Missing filename")

    suffix = file.filename.lower().rsplit(".", 1)[-1]
    if suffix not in {"pdf", "docx", "txt"}:
        raise HTTPException(status_code=400, detail="Unsupported file type. Use PDF/DOCX/TXT.")

    raw = await file.read()
    if len(raw) > 100 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="File too large (max 100MB)")

    sha256 = sha256_bytes(raw)

    path = _storage().save(deal_id, file.filename, raw)

    try:
        extracted_text = extract_text(path)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to extract text: {e}")

    # Store redacted extracted text (MVP). TODO: store raw text encrypted-at-rest.
    redacted_text = redact(extracted_text)

    doc = Document(
        deal_id=deal_id,
        filename=file.filename,
        storage_path=str(path),
        sha256=sha256,
        extracted_text=redacted_text,
        metadata_json={
            "content_type": file.content_type,
            "size_bytes": len(raw),
            "suffix": suffix,
        },
    )
    db.add(doc)
    db.flush()

    audit(
        db,
        actor=_actor(request),
        action="upload_doc",
        deal_id=deal_id,
        metadata={"filename": file.filename, "sha256": sha256},
    )

    db.commit()

    return {
        "document_id": doc.id,
        "filename": file.filename,
        "sha256": sha256,
    }


@router.post("/{deal_id}/extract")
async def extract_terms(deal_id: str, request: Request, db: Session = Depends(get_db)):
    _get_deal(db, deal_id)

    docs = db.query(Document).filter(Document.deal_id == deal_id).all()
    if not docs:
        raise HTTPException(status_code=400, detail="No documents uploaded")

    combined = "\n\n".join([f"--- {d.filename} ---\n{d.extracted_text}" for d in docs])
    combined = sanitize_text(combined)

    prompt_name = "extract_terms"
    prompt_version = "v1"
    template = load_prompt_template(prompt_name, prompt_version)
    prompt = template.format(deal_text=combined)

    llm = get_llm_client()

    # Redaction before LLM call (already redacted docs, but keep the belt-and-suspenders approach)
    prompt_for_llm = redact(prompt)

    output = await llm.complete_json(prompt=prompt_for_llm, schema_name="ExtractedTerms")

    # Validate and redact output before persistence
    parsed = ExtractedTerms.model_validate(output)
    redacted_output = redact_obj(parsed.model_dump())

    pv = ensure_prompt_version(db, name=prompt_name, version=prompt_version, content=template)

    existing = db.query(DealTerms).filter(DealTerms.deal_id == deal_id).one_or_none()
    if existing:
        existing.terms_json = redacted_output
        existing.citations_json = redacted_output.get("citations", {})
    else:
        db.add(
            DealTerms(
                deal_id=deal_id,
                terms_json=redacted_output,
                citations_json=redacted_output.get("citations", {}),
                confirmed_fields_json={},
            )
        )

    db.add(
        LLMRun(
            deal_id=deal_id,
            prompt_name=prompt_name,
            prompt_version=prompt_version,
            model=settings.llm_model,
            temperature=settings.llm_temperature,
            input_hash=sha256_text(prompt_for_llm),
            output_json=redacted_output,
        )
    )

    audit(db, actor=_actor(request), action="extract", deal_id=deal_id, metadata={"prompt": f"{prompt_name}:{prompt_version}"})

    db.commit()

    return redacted_output


@router.put("/{deal_id}/terms")
def update_terms(deal_id: str, payload: TermsUpdate, request: Request, db: Session = Depends(get_db)):
    _get_deal(db, deal_id)

    existing = db.query(DealTerms).filter(DealTerms.deal_id == deal_id).one_or_none()
    if not existing:
        existing = DealTerms(deal_id=deal_id, terms_json={}, citations_json={}, confirmed_fields_json={})
        db.add(existing)

    terms_dump = payload.terms.model_dump()
    existing.terms_json = redact_obj(terms_dump)
    existing.citations_json = redact_obj(payload.terms.citations)
    existing.confirmed_fields_json = payload.confirmed_fields

    audit(db, actor=_actor(request), action="edit_terms", deal_id=deal_id, metadata={"confirmed_fields": payload.confirmed_fields})

    db.commit()
    return {"status": "ok"}


@router.post("/{deal_id}/analyze", response_model=AnalysisResponse)
def analyze_deal(deal_id: str, request: Request, db: Session = Depends(get_db)):
    _get_deal(db, deal_id)

    terms_row = db.query(DealTerms).filter(DealTerms.deal_id == deal_id).one_or_none()
    if not terms_row:
        raise HTTPException(status_code=400, detail="No extracted/confirmed terms")

    terms = ExtractedTerms.model_validate(terms_row.terms_json)

    res = analyze(terms)

    existing = db.query(DealAnalysis).filter(DealAnalysis.deal_id == deal_id).one_or_none()
    if existing:
        existing.metrics_json = res.metrics
        existing.risk_flags_json = [f.model_dump() for f in res.risk_flags]
        existing.diligence_questions_json = res.diligence_questions
        existing.overall_triage = res.overall_triage
    else:
        db.add(
            DealAnalysis(
                deal_id=deal_id,
                metrics_json=res.metrics,
                risk_flags_json=[f.model_dump() for f in res.risk_flags],
                diligence_questions_json=res.diligence_questions,
                overall_triage=res.overall_triage,
            )
        )

    audit(db, actor=_actor(request), action="analyze", deal_id=deal_id, metadata={"overall_triage": res.overall_triage})

    db.commit()

    return AnalysisResponse(
        metrics=res.metrics,
        overall_triage=res.overall_triage,
        risk_flags=res.risk_flags,
        diligence_questions=res.diligence_questions,
    )


def _draft_allowed(terms: ExtractedTerms, confirmed: dict[str, bool]) -> tuple[bool, str | None]:
    required = {"loan_amount", "lien_position", "repayment_source"}
    for f in required:
        if not confirmed.get(f):
            return False, f"Field '{f}' must be confirmed before drafting"

    if not (confirmed.get("collateral_value_stressed") or confirmed.get("collateral_value_appraised")):
        return False, "Collateral value (stressed or appraised) must be confirmed before drafting"

    return True, None


@router.post("/{deal_id}/draft", response_model=ICDraft)
async def draft_ic(deal_id: str, request: Request, db: Session = Depends(get_db)):
    _get_deal(db, deal_id)

    terms_row = db.query(DealTerms).filter(DealTerms.deal_id == deal_id).one_or_none()
    if not terms_row:
        raise HTTPException(status_code=400, detail="No extracted/confirmed terms")

    analysis_row = db.query(DealAnalysis).filter(DealAnalysis.deal_id == deal_id).one_or_none()
    if not analysis_row:
        raise HTTPException(status_code=400, detail="Run analysis first")

    terms = ExtractedTerms.model_validate(terms_row.terms_json)
    allowed, reason = _draft_allowed(terms, terms_row.confirmed_fields_json or {})
    if not allowed:
        raise HTTPException(status_code=400, detail=reason)

    prompt_name = "ic_draft"
    prompt_version = "v1"
    template = load_prompt_template(prompt_name, prompt_version)

    input_obj = {
        "terms": terms.model_dump(),
        "analysis": {
            "metrics": analysis_row.metrics_json,
            "overall_triage": analysis_row.overall_triage,
            "risk_flags": analysis_row.risk_flags_json,
            "diligence_questions": analysis_row.diligence_questions_json,
        },
    }

    prompt = template.format(input_json=input_obj)
    prompt_for_llm = redact(prompt)

    llm = get_llm_client()
    output = await llm.complete_json(prompt=prompt_for_llm, schema_name="ICDraft")

    parsed = ICDraft.model_validate(output)
    redacted_output = redact_obj(parsed.model_dump())

    ensure_prompt_version(db, name=prompt_name, version=prompt_version, content=template)

    existing = db.query(DealDraft).filter(DealDraft.deal_id == deal_id).one_or_none()
    if existing:
        existing.draft_json = redacted_output
        existing.prompt_name = prompt_name
        existing.prompt_version = prompt_version
    else:
        db.add(
            DealDraft(
                deal_id=deal_id,
                draft_json=redacted_output,
                prompt_name=prompt_name,
                prompt_version=prompt_version,
            )
        )

    db.add(
        LLMRun(
            deal_id=deal_id,
            prompt_name=prompt_name,
            prompt_version=prompt_version,
            model=settings.llm_model,
            temperature=settings.llm_temperature,
            input_hash=sha256_text(prompt_for_llm),
            output_json=redacted_output,
        )
    )

    audit(db, actor=_actor(request), action="draft", deal_id=deal_id, metadata={"prompt": f"{prompt_name}:{prompt_version}"})

    db.commit()

    return ICDraft.model_validate(redacted_output)


@router.get("/{deal_id}/export")
def export_pdf(deal_id: str, request: Request, db: Session = Depends(get_db)):
    deal = _get_deal(db, deal_id)

    terms_row = db.query(DealTerms).filter(DealTerms.deal_id == deal_id).one_or_none()
    analysis_row = db.query(DealAnalysis).filter(DealAnalysis.deal_id == deal_id).one_or_none()
    draft_row = db.query(DealDraft).filter(DealDraft.deal_id == deal_id).one_or_none()

    pdf_bytes = build_export_pdf(
        deal={"id": deal.id, "name": deal.name, "created_at": deal.created_at.isoformat()},
        terms=terms_row.terms_json if terms_row else None,
        analysis={
            "metrics": analysis_row.metrics_json,
            "overall_triage": analysis_row.overall_triage,
            "risk_flags": analysis_row.risk_flags_json,
            "diligence_questions": analysis_row.diligence_questions_json,
        }
        if analysis_row
        else None,
        draft=draft_row.draft_json if draft_row else None,
    )

    audit(db, actor=_actor(request), action="export", deal_id=deal_id, metadata={"bytes": len(pdf_bytes)})
    db.commit()

    return Response(content=pdf_bytes, media_type="application/pdf")
