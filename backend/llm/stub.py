from __future__ import annotations

import re

from backend.llm.base import LLMClient
from backend.utils.sanitize import sanitize_text


def _snippet(text: str, start: int, end: int, max_len: int = 200) -> str:
    s = text[max(0, start - 80) : min(len(text), end + 80)].strip()
    s = re.sub(r"\s+", " ", s)
    return s[:max_len]


class StubLLMClient(LLMClient):
    """Working local stub.

    Uses light regex heuristics so the app can be exercised without external calls.
    """

    async def complete_json(self, *, prompt: str, schema_name: str) -> dict:
        # The prompt contains the redacted deal text; heuristically extract a few obvious fields.
        text = sanitize_text(prompt)

        def find_money(label: str) -> tuple[float | None, str | None]:
            m = re.search(rf"{label}[^\n\r]*?(\$?\s*[0-9][0-9,\.]*)(?:\s*(AUD|USD|NZD))?", text, re.IGNORECASE)
            if not m:
                m = re.search(r"\$\s*([0-9][0-9,\.]+)", text)
            if not m:
                return None, None
            raw = m.group(1)
            amount = float(raw.replace(",", "")) if raw else None
            return amount, _snippet(text, m.start(), m.end())

        loan_amount, loan_amount_snip = find_money("loan amount|facility amount|principal")

        ir_m = re.search(r"\b(?:interest|coupon)\s*[:=]?\s*([0-9]+(?:\.[0-9]+)?)\s*%", text, re.IGNORECASE)
        interest_rate_pct = float(ir_m.group(1)) if ir_m else None
        interest_snip = _snippet(text, ir_m.start(), ir_m.end()) if ir_m else None

        term_m = re.search(r"\bterm\s*[:=]?\s*([0-9]{1,3})\s*(months|month|mos|mo)\b", text, re.IGNORECASE)
        term_months = int(term_m.group(1)) if term_m else None
        term_snip = _snippet(text, term_m.start(), term_m.end()) if term_m else None

        collateral_m = re.search(r"\bcollateral\s*[:=]?\s*([A-Za-z /-]{3,60})", text)
        collateral_type = collateral_m.group(1).strip() if collateral_m else "unknown"
        collateral_snip = _snippet(text, collateral_m.start(), collateral_m.end()) if collateral_m else None

        # Build a schema-shaped response.
        if schema_name == "ExtractedTerms":
            citations = {
                "loan_amount": [loan_amount_snip] if loan_amount_snip else None,
                "interest_rate_pct": [interest_snip] if interest_snip else None,
                "term_months": [term_snip] if term_snip else None,
                "collateral_type": [collateral_snip] if collateral_snip else None,
            }
            return {
                "loan_amount": loan_amount,
                "currency": "AUD",
                "term_months": term_months,
                "interest_rate_pct": interest_rate_pct,
                "fees": [],
                "collateral_type": collateral_type,
                "collateral_value_appraised": None,
                "collateral_value_as_is": None,
                "collateral_value_stressed": None,
                "lien_position": "unknown",
                "jurisdiction": None,
                "enforcement_timeline_months": None,
                "repayment_source": None,
                "repayment_timeline_months": None,
                "key_conditions": [],
                "notes": None,
                "citations": citations,
            }

        if schema_name == "ICDraft":
            return {
                "banner": "Decision support only. Not investment advice.",
                "ic_summary_3_lines": "Stub summary (no external LLM configured).",
                "top_risks_ranked": ["Insufficient confirmed repayment source."],
                "mitigants_or_conditions": ["Confirm repayment source and timing."],
                "diligence_questions": ["What is the verified repayment source for this facility?"],
                "what_changes_my_mind": "Provide independent collateral valuation and clear exit evidence.",
            }

        raise ValueError(f"Unknown schema_name: {schema_name}")
