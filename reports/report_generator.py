"""
NeuroSpeak – PDF Report Generator
Generates professional clinical-style PDF reports using ReportLab.
"""

import os
from datetime import datetime


def generate_pdf_report(analysis_id: str, result: dict) -> str:
    """
    Generate a PDF report for an EEG analysis.

    Args:
        analysis_id: Unique analysis identifier
        result: Dict with analysis data from /api/analyze

    Returns:
        Path to the generated PDF file
    """
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import cm
    from reportlab.lib import colors
    from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer,
                                    Table, TableStyle, HRFlowable)
    from reportlab.lib.enums import TA_CENTER, TA_LEFT

    # ── Colors ──────────────────────────────────────────────────────────────
    CYAN   = colors.HexColor('#00E5FF')
    PURPLE = colors.HexColor('#7B61FF')
    DARK   = colors.HexColor('#0B1020')
    GREEN  = colors.HexColor('#00FF9D')
    WHITE  = colors.white
    LIGHT  = colors.HexColor('#E8EAF6')

    os.makedirs('reports', exist_ok=True)
    short_id = analysis_id[:8].upper()
    pdf_path = f"reports/NeuroSpeak_Report_{short_id}.pdf"

    doc = SimpleDocTemplate(
        pdf_path,
        pagesize=A4,
        rightMargin=2*cm, leftMargin=2*cm,
        topMargin=2*cm, bottomMargin=2*cm
    )

    styles = getSampleStyleSheet()
    story  = []

    # ─── Custom Styles ───────────────────────────────────────────────────────
    title_style = ParagraphStyle('Title', parent=styles['Title'],
                                 textColor=DARK, fontSize=22, spaceAfter=4,
                                 alignment=TA_CENTER, fontName='Helvetica-Bold')
    subtitle_style = ParagraphStyle('Sub', parent=styles['Normal'],
                                    textColor=PURPLE, fontSize=11,
                                    alignment=TA_CENTER, spaceAfter=8)
    h2_style = ParagraphStyle('H2', parent=styles['Heading2'],
                               textColor=PURPLE, fontSize=13,
                               fontName='Helvetica-Bold', spaceBefore=14, spaceAfter=6)
    body_style = ParagraphStyle('Body', parent=styles['Normal'],
                                fontSize=10, leading=16, spaceAfter=4)
    small_style = ParagraphStyle('Small', parent=styles['Normal'],
                                 fontSize=8, textColor=colors.grey)

    # ─── Header ──────────────────────────────────────────────────────────────
    story.append(Paragraph("🧠 NeuroSpeak", title_style))
    story.append(Paragraph("Brain Signal to Text Communication System", subtitle_style))
    story.append(Paragraph("EEG Analysis Report", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=2, color=CYAN))
    story.append(Spacer(1, 0.4*cm))

    # ─── Meta Info Table ─────────────────────────────────────────────────────
    meta_data = [
        ['Report ID',   short_id,
         'Subject ID',  result.get('subject_id', 'N/A')],
        ['Date',        datetime.utcnow().strftime('%Y-%m-%d'),
         'Time (UTC)',  datetime.utcnow().strftime('%H:%M:%S')],
        ['Model',       'NeuroSpeak-CNN-LSTM v2.3.1',
         'Status',      '✓ Completed'],
    ]
    meta_table = Table(meta_data, colWidths=[3*cm, 6*cm, 3*cm, 5*cm])
    meta_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), LIGHT),
        ('TEXTCOLOR',  (0, 0), (0, -1), PURPLE),
        ('TEXTCOLOR',  (2, 0), (2, -1), PURPLE),
        ('FONTNAME',   (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE',   (0, 0), (-1, -1), 9),
        ('GRID',       (0, 0), (-1, -1), 0.5, colors.white),
        ('ROWBACKGROUNDS', (0, 0), (-1, -1), [LIGHT, colors.HexColor('#D1D5F0')]),
        ('VALIGN',     (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(meta_table)
    story.append(Spacer(1, 0.5*cm))

    # ─── Signal Metrics ───────────────────────────────────────────────────────
    story.append(Paragraph("Signal Metrics", h2_style))
    metrics_data = [
        ['Metric', 'Value', 'Metric', 'Value'],
        ['Signal Quality', f"{result.get('signal_quality', 'N/A')} μV",
         'Channels', str(result.get('channels', 64))],
        ['Duration', f"{result.get('duration', 'N/A')} s",
         'Sampling Rate', '160 Hz'],
        ['Attention Level', f"{result.get('attention_level', 'N/A')}%",
         'Focus Score', f"{result.get('focus_score', 'N/A')}%"],
    ]
    _add_table(story, metrics_data, PURPLE, LIGHT)

    # ─── Frequency Band Analysis ──────────────────────────────────────────────
    story.append(Spacer(1, 0.3*cm))
    story.append(Paragraph("Frequency Band Analysis", h2_style))
    freq_data = [
        ['Band', 'Range', 'Power', 'Function'],
        ['Delta',  '0.5–4 Hz',   f"{result.get('delta_power', 0.18):.3f}",  'Deep sleep, repair'],
        ['Theta',  '4–8 Hz',     f"{result.get('theta_power', 0.22):.3f}",  'Creativity, memory'],
        ['Alpha',  '8–13 Hz',    f"{result.get('alpha_power', 0.45):.3f}",  'Relaxed focus'],
        ['Beta',   '13–30 Hz',   f"{result.get('beta_power', 0.31):.3f}",   'Active thinking'],
        ['Gamma',  '30–45 Hz',   '0.082',                                    'Cognitive processing'],
    ]
    _add_table(story, freq_data, CYAN, LIGHT)

    # ─── AI Prediction ────────────────────────────────────────────────────────
    story.append(Spacer(1, 0.3*cm))
    story.append(Paragraph("AI Prediction Results", h2_style))
    pred_data = [
        ['Generated Text',  result.get('generated_text', 'N/A')],
        ['Confidence Score', f"{result.get('confidence', 0)}%"],
        ['Model Accuracy',   f"{result.get('accuracy', 0)}%"],
        ['Inference Time',   f"{result.get('latency_ms', 0)} ms"],
        ['Predictions',      ', '.join(result.get('predictions', [])[:10])],
    ]
    pred_table = Table(pred_data, colWidths=[5*cm, 12*cm])
    pred_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), PURPLE),
        ('TEXTCOLOR',  (0, 0), (0, -1), WHITE),
        ('BACKGROUND', (1, 0), (1, -1), LIGHT),
        ('FONTNAME',   (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE',   (0, 0), (-1, -1), 9),
        ('GRID',       (0, 0), (-1, -1), 0.5, WHITE),
        ('VALIGN',     (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 7),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 7),
    ]))
    story.append(pred_table)

    # ─── Recommendations ─────────────────────────────────────────────────────
    story.append(Spacer(1, 0.5*cm))
    story.append(Paragraph("Clinical Recommendations", h2_style))
    recommendations = [
        "1. Continue regular EEG monitoring sessions for longitudinal analysis.",
        "2. Ensure proper electrode gel application and impedance < 5kΩ for optimal signal quality.",
        "3. Minimize electromagnetic interference (turn off nearby devices) during recording.",
        "4. Perform motor imagery training exercises to improve signal clarity.",
        "5. Consult a licensed neurologist for clinical interpretation of these results.",
        "6. Consider increasing session duration to 5+ minutes for better model confidence.",
    ]
    for rec in recommendations:
        story.append(Paragraph(rec, body_style))

    # ─── Doctor Notes ─────────────────────────────────────────────────────────
    story.append(Spacer(1, 0.5*cm))
    story.append(Paragraph("Physician Notes", h2_style))
    story.append(HRFlowable(width="100%", thickness=0.5, color=colors.grey))
    story.append(Spacer(1, 2.5*cm))
    story.append(HRFlowable(width="100%", thickness=0.5, color=colors.grey))
    story.append(Paragraph("Signature: _______________________     Date: _______________", small_style))

    # ─── Footer ───────────────────────────────────────────────────────────────
    story.append(Spacer(1, 0.5*cm))
    story.append(HRFlowable(width="100%", thickness=1, color=CYAN))
    story.append(Paragraph(
        "Generated by NeuroSpeak AI Platform | For Research Purposes Only | Not a Medical Diagnostic Tool",
        ParagraphStyle('footer', parent=styles['Normal'], fontSize=8,
                       textColor=colors.grey, alignment=TA_CENTER, spaceAfter=0)
    ))

    doc.build(story)
    print(f"[Report] Generated: {pdf_path}")
    return pdf_path


def _add_table(story, data, header_color, row_color):
    from reportlab.lib import colors
    from reportlab.platypus import Table, TableStyle

    WHITE = colors.white
    t = Table(data)
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), header_color),
        ('TEXTCOLOR',  (0, 0), (-1, 0), WHITE),
        ('FONTNAME',   (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTNAME',   (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE',   (0, 0), (-1, -1), 9),
        ('BACKGROUND', (0, 1), (-1, -1), row_color),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [row_color, colors.HexColor('#D1D5F0')]),
        ('GRID',       (0, 0), (-1, -1), 0.5, WHITE),
        ('VALIGN',     (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(t)
