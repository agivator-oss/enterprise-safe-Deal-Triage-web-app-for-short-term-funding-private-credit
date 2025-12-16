from backend.schemas.extracted_terms import ExtractedTerms
from backend.services.analysis import analyze


def test_lvr_and_equity_buffer_prefers_stressed():
    terms = ExtractedTerms(
        loan_amount=700_000,
        collateral_type="property",
        collateral_value_appraised=1_200_000,
        collateral_value_stressed=1_000_000,
        lien_position="first",
        repayment_source="sale",
    )

    res = analyze(terms)

    assert res.metrics["LVR_appraised"] == 700_000 / 1_200_000
    assert res.metrics["LVR_stressed"] == 700_000 / 1_000_000
    assert res.metrics["equity_buffer"] == 1 - (700_000 / 1_000_000)


def test_rules_hard_stop_for_missing_repayment_source():
    terms = ExtractedTerms(
        loan_amount=500_000,
        collateral_type="property",
        collateral_value_appraised=1_000_000,
        lien_position="first",
        repayment_source=None,
    )

    res = analyze(terms)

    assert any(f.severity == "HARD_STOP" for f in res.risk_flags)
    assert res.overall_triage == "Weak"
