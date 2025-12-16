from __future__ import annotations

import io

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas


def build_export_pdf(*, deal: dict, terms: dict | None, analysis: dict | None, draft: dict | None) -> bytes:
    """Generate a minimal PDF export for MVP."""

    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter

    y = height - 50

    def line(txt: str) -> None:
        nonlocal y
        c.drawString(50, y, txt[:140])
        y -= 14
        if y < 60:
            c.showPage()
            y = height - 50

    line("Deal Triage Export")
    line(f"Deal ID: {deal.get('id')}")
    line(f"Deal Name: {deal.get('name')}")
    line(f"Created At: {deal.get('created_at')}")
    line("")

    line("Extracted Terms")
    if terms:
        for k in sorted(terms.keys()):
            line(f"- {k}: {terms.get(k)}")
    else:
        line("(none)")
    line("")

    line("Analysis")
    if analysis:
        for k in sorted(analysis.keys()):
            line(f"- {k}: {analysis.get(k)}")
    else:
        line("(none)")
    line("")

    line("IC Draft")
    if draft:
        for k in sorted(draft.keys()):
            line(f"- {k}: {draft.get(k)}")
    else:
        line("(none)")

    c.showPage()
    c.save()

    return buffer.getvalue()
