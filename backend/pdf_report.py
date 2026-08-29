import os
import io
from typing import Dict, Any
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT, TA_RIGHT

def generate_pdf_report(report: Dict[str, Any]) -> io.BytesIO:
    """Generates a Turnitin-style PDF Similarity Report using ReportLab."""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    story = []
    styles = getSampleStyleSheet()

    # Custom Styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontSize=20,
        leading=24,
        textColor=colors.HexColor('#1A202C'),
        alignment=TA_LEFT,
        fontName='Helvetica-Bold'
    )
    
    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.HexColor('#718096'),
        alignment=TA_LEFT
    )

    score_badge_style = ParagraphStyle(
        'ScoreBadge',
        parent=styles['Heading1'],
        fontSize=28,
        leading=32,
        textColor=colors.HexColor('#C53030'),
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )

    body_style = ParagraphStyle(
        'BodyTextCustom',
        parent=styles['Normal'],
        fontSize=10,
        leading=15,
        alignment=TA_JUSTIFY,
        textColor=colors.HexColor('#2D3748')
    )

    header_table_data = [
        [
            Paragraph(f"<b>TURNITIN ORIGINALITY REPORT</b><br/><font size=12 color='#4A5568'>{report.get('document_title', 'Dokumen Tanpa Judul')}</font>", title_style),
            Paragraph(f"SIMILARITY INDEX<br/><font color='#C53030'><b>{report.get('similarity_score', 0)}%</b></font>", score_badge_style)
        ]
    ]

    header_table = Table(header_table_data, colWidths=[380, 160])
    header_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BACKGROUND', (1,0), (1,0), colors.HexColor('#FFF5F5')),
        ('BOX', (1,0), (1,0), 1, colors.HexColor('#FEB2B2')),
        ('PADDING', (1,0), (1,0), 10),
    ]))
    story.append(header_table)
    story.append(Spacer(1, 15))

    # Meta Info Table
    report_data = report.get('report_data', {})
    meta_data = [
        [
            Paragraph(f"<b>Penulis:</b> {report.get('author', 'Anonim')}", subtitle_style),
            Paragraph(f"<b>Total Kata:</b> {report.get('total_words', 0)} kata", subtitle_style),
            Paragraph(f"<b>Kata Mirip:</b> {report.get('matched_words', 0)} kata", subtitle_style),
            Paragraph(f"<b>Tanggal:</b> {report.get('created_at', '')[:10]}", subtitle_style)
        ]
    ]
    meta_table = Table(meta_data, colWidths=[135, 135, 135, 135])
    meta_table.setStyle(TableStyle([
        ('LINEBELOW', (0,0), (-1,-1), 1, colors.HexColor('#E2E8F0')),
        ('PADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(meta_table)
    story.append(Spacer(1, 15))

    # Primary Sources Breakdown
    story.append(Paragraph("<b>PRIMARY SOURCES / DAFTAR SUMBER KEMIRIPAN</b>", ParagraphStyle('SubHeader', parent=styles['Heading2'], fontSize=12, textColor=colors.HexColor('#2B6CB0'))))
    story.append(Spacer(1, 8))

    sources = report_data.get('sources', [])
    if sources:
        table_content = [
            [
                Paragraph("<b>No</b>", subtitle_style),
                Paragraph("<b>Judul Sumber Referensi</b>", subtitle_style),
                Paragraph("<b>Institusi / Repositori</b>", subtitle_style),
                Paragraph("<b>Kemiripan</b>", subtitle_style)
            ]
        ]

        for idx, src in enumerate(sources, start=1):
            color_hex = src.get('color', '#E53E3E')
            title_p = Paragraph(f"<font color='{color_hex}'><b>#{idx}</b></font> {src['title']}", body_style)
            inst_p = Paragraph(f"{src['institution']} ({src['author']})", subtitle_style)
            pct_p = Paragraph(f"<b><font color='{color_hex}'>{src['percentage']}%</font></b>", ParagraphStyle('RightPct', parent=styles['Normal'], alignment=TA_RIGHT))
            table_content.append([str(idx), title_p, inst_p, pct_p])

        sources_table = Table(table_content, colWidths=[30, 250, 180, 80])
        sources_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#EDF2F7')),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E0')),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('PADDING', (0,0), (-1,-1), 6),
        ]))
        story.append(sources_table)
    else:
        story.append(Paragraph("<i>Tidak ditemukan sumber kemiripan signifikan (0% Similarity). Dokumen dinyatakan original.</i>", body_style))

    story.append(Spacer(1, 20))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#CBD5E0')))
    story.append(Spacer(1, 15))

    # Annotated Document Text
    story.append(Paragraph("<b>TEKS DOKUMEN DENGAN PENYOROTAN KEMIRIPAN (HIGHLIGHTED TEXT)</b>", ParagraphStyle('SubHeader2', parent=styles['Heading2'], fontSize=12, textColor=colors.HexColor('#2B6CB0'))))
    story.append(Spacer(1, 10))

    annotated = report_data.get('annotated_sentences', [])
    formatted_html_parts = []

    for item in annotated:
        text = item['text']
        if item.get('matched') and item.get('color'):
            bg_color = item['color']
            source_title = item.get('source_title', 'Sumber')
            formatted_html_parts.append(
                f"<font color='white' backColor='{bg_color}'> <b>[{item.get('similarity')}% - {source_title[:20]}]</b> {text} </font>"
            )
        else:
            formatted_html_parts.append(text)

    full_text_html = " ".join(formatted_html_parts)
    story.append(Paragraph(full_text_html, body_style))

    # Build Document
    doc.build(story)
    buffer.seek(0)
    return buffer
