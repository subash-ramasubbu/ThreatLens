from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import ParagraphStyle
import io
from datetime import datetime


def generate_pdf_report(summary: dict, threats: list) -> bytes:
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []

    title_style = ParagraphStyle(
        "Title",
        parent=styles["Heading1"],
        fontSize=24,
        textColor=colors.HexColor("#1e3a5f"),
        spaceAfter=12,
    )
    heading_style = ParagraphStyle(
        "Heading",
        parent=styles["Heading2"],
        fontSize=14,
        textColor=colors.HexColor("#1e3a5f"),
        spaceAfter=8,
    )

    story.append(Paragraph("ThreatLens Intelligence Report", title_style))
    story.append(Paragraph(
        f"Generated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}",
        styles["Normal"]
    ))
    story.append(Spacer(1, 0.3 * inch))

    story.append(Paragraph("Executive Summary", heading_style))
    summary_data = [
        ["Metric", "Value"],
        ["Total Threats", str(summary.get("total", 0))],
        ["Critical Threats", str(summary.get("critical", 0))],
        ["High Threats", str(summary.get("high", 0))],
        ["Medium Threats", str(summary.get("medium", 0))],
        ["Average Risk Score", str(summary.get("avg_risk_score", 0))],
    ]

    summary_table = Table(summary_data, colWidths=[3 * inch, 3 * inch])
    summary_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1e3a5f")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f0f4f8")]),
        ("PADDING", (0, 0), (-1, -1), 8),
    ]))
    story.append(summary_table)
    story.append(Spacer(1, 0.3 * inch))

    story.append(Paragraph("Top Critical Threats", heading_style))
    threat_data = [["Value", "Type", "Risk Score", "Source", "Tags"]]
    for t in threats[:15]:
        threat_data.append([
            str(t.get("value", ""))[:30],
            str(t.get("type", "")),
            str(t.get("risk_score", "")),
            str(t.get("source", "")),
            str(t.get("tags", ""))[:30],
        ])

    threat_table = Table(
        threat_data,
        colWidths=[2 * inch, 0.8 * inch, 0.8 * inch, 1 * inch, 1.6 * inch]
    )
    threat_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#ef4444")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#fef2f2")]),
        ("PADDING", (0, 0), (-1, -1), 6),
    ]))
    story.append(threat_table)

    doc.build(story)
    return buffer.getvalue()