from __future__ import annotations

from dataclasses import dataclass

from backend.schemas.analysis import RiskFlag
from backend.schemas.extracted_terms import ExtractedTerms
from backend.schemas.common import LienPosition


@dataclass(frozen=True)
class AnalysisResult:
    metrics: dict[str, float | None]
    overall_triage: str
    risk_flags: list[RiskFlag]
    diligence_questions: list[str]


def compute_metrics(terms: ExtractedTerms) -> dict[str, float | None]:
    loan = terms.loan_amount
    lvr_appraised = None
    lvr_stressed = None

    if loan is not None and terms.collateral_value_appraised is not None and terms.collateral_value_appraised != 0:
        lvr_appraised = loan / terms.collateral_value_appraised
    if loan is not None and terms.collateral_value_stressed is not None and terms.collateral_value_stressed != 0:
        lvr_stressed = loan / terms.collateral_value_stressed

    equity_buffer = None
    if lvr_stressed is not None:
        equity_buffer = 1.0 - lvr_stressed
    elif lvr_appraised is not None:
        equity_buffer = 1.0 - lvr_appraised

    return {
        "LVR_appraised": lvr_appraised,
        "LVR_stressed": lvr_stressed,
        "equity_buffer": equity_buffer,
    }


def run_rules(terms: ExtractedTerms, metrics: dict[str, float | None]) -> list[RiskFlag]:
    flags: list[RiskFlag] = []

    def add(rule_id: str, severity: str, message: str) -> None:
        flags.append(RiskFlag(rule_id=rule_id, severity=severity, message=message))

    # Spec rules
    if not (terms.repayment_source or "").strip():
        add("repayment_source_missing", "HARD_STOP", "Repayment source is missing.")

    lvr_stressed = metrics.get("LVR_stressed")
    if lvr_stressed is not None and lvr_stressed > 0.70:
        add("lvr_stressed_gt_70", "HIGH", f"Stressed LVR is {lvr_stressed:.2%}, above 70%.")

    if terms.lien_position != LienPosition.first:
        add("lien_not_first", "HIGH", f"Lien position is {terms.lien_position.value} (not first).")

    if terms.enforcement_timeline_months is None:
        add("enforcement_timeline_missing", "MED", "Enforcement timeline is not provided.")

    if (
        terms.repayment_timeline_months is not None
        and terms.term_months is not None
        and terms.repayment_timeline_months > terms.term_months
    ):
        add(
            "repayment_after_term",
            "HIGH",
            "Repayment timeline exceeds stated loan term.",
        )

    if terms.collateral_value_stressed is None:
        add("missing_stress_value", "MED", "No stressed collateral value provided (stress missing).")

    return flags


def derive_diligence_questions(flags: list[RiskFlag]) -> list[str]:
    questions: list[str] = []

    for f in flags:
        if f.rule_id == "repayment_source_missing":
            questions.append("What is the verified repayment source and supporting evidence (contracts, refinance take-out, sale plan)?")
        elif f.rule_id == "lvr_stressed_gt_70":
            questions.append("Provide independent valuation and sensitivity showing stressed value support for requested leverage.")
        elif f.rule_id == "lien_not_first":
            questions.append("Confirm intercreditor/subordination terms and assess enforcement control given non-first position.")
        elif f.rule_id == "enforcement_timeline_missing":
            questions.append("What is the expected enforcement timeline and key legal steps in the stated jurisdiction?")
        elif f.rule_id == "repayment_after_term":
            questions.append("Align repayment timeline with term (or structure extension options/conditions).")
        elif f.rule_id == "missing_stress_value":
            questions.append("Provide a stressed collateral value or defined stress methodology for downside case.")

    # De-dup while preserving order
    out: list[str] = []
    seen = set()
    for q in questions:
        if q not in seen:
            out.append(q)
            seen.add(q)
    return out


def overall_triage(flags: list[RiskFlag]) -> str:
    severities = [f.severity for f in flags]
    if "HARD_STOP" in severities:
        return "Weak"

    high = sum(1 for s in severities if s == "HIGH")
    med = sum(1 for s in severities if s == "MED")

    if high >= 2:
        return "Weak"
    if high == 1 or med >= 2:
        return "Borderline"
    return "Strong"


def analyze(terms: ExtractedTerms) -> AnalysisResult:
    metrics = compute_metrics(terms)
    flags = run_rules(terms, metrics)
    triage = overall_triage(flags)
    questions = derive_diligence_questions(flags)
    return AnalysisResult(metrics=metrics, overall_triage=triage, risk_flags=flags, diligence_questions=questions)
