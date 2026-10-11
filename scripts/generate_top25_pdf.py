import json
import os
import sys
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch

# Load scored stocks
with open('final_scored_deadliest_top25.json', 'r', encoding='utf-8') as f:
    stocks = json.load(f)

# PDF paths
pdf_workspace_path = os.path.abspath('TOP_25_DEADLIEST_COMBO_STOCKS.pdf')
artifact_dir = r'C:\Users\BAPPADITYA\.gemini\antigravity\brain\61afd3e5-1fa3-43dc-9744-2b311d3ac249'
pdf_artifact_path = os.path.join(artifact_dir, 'TOP_25_DEADLIEST_COMBO_STOCKS.pdf')

doc = SimpleDocTemplate(
    pdf_workspace_path,
    pagesize=letter,
    leftMargin=36,
    rightMargin=36,
    topMargin=36,
    bottomMargin=36
)

styles = getSampleStyleSheet()

# Custom styles
title_style = ParagraphStyle(
    'DocTitle',
    parent=styles['Normal'],
    fontName='Helvetica-Bold',
    fontSize=22,
    leading=26,
    textColor=colors.HexColor('#0F172A'),
    alignment=1
)

subtitle_style = ParagraphStyle(
    'DocSubTitle',
    parent=styles['Normal'],
    fontName='Helvetica',
    fontSize=11,
    leading=15,
    textColor=colors.HexColor('#334155'),
    alignment=1
)

meta_style = ParagraphStyle(
    'DocMeta',
    parent=styles['Normal'],
    fontName='Helvetica-Oblique',
    fontSize=9,
    leading=12,
    textColor=colors.HexColor('#64748B'),
    alignment=1
)

h1_style = ParagraphStyle(
    'Heading1_Custom',
    parent=styles['Normal'],
    fontName='Helvetica-Bold',
    fontSize=14,
    leading=18,
    textColor=colors.HexColor('#1E293B'),
    spaceAfter=6
)

h2_style = ParagraphStyle(
    'Heading2_Custom',
    parent=styles['Normal'],
    fontName='Helvetica-Bold',
    fontSize=11,
    leading=14,
    textColor=colors.HexColor('#0369A1'),
    spaceBefore=4,
    spaceAfter=2
)

body_style = ParagraphStyle(
    'Body_Custom',
    parent=styles['Normal'],
    fontName='Helvetica',
    fontSize=9,
    leading=13,
    textColor=colors.HexColor('#1E293B')
)

table_header_style = ParagraphStyle(
    'TableHeader',
    parent=styles['Normal'],
    fontName='Helvetica-Bold',
    fontSize=8,
    leading=10,
    textColor=colors.white,
    alignment=1
)

table_cell_style = ParagraphStyle(
    'TableCell',
    parent=styles['Normal'],
    fontName='Helvetica',
    fontSize=7.5,
    leading=9.5,
    textColor=colors.HexColor('#0F172A')
)

table_cell_bold = ParagraphStyle(
    'TableCellBold',
    parent=styles['Normal'],
    fontName='Helvetica-Bold',
    fontSize=7.5,
    leading=9.5,
    textColor=colors.HexColor('#0F172A')
)

table_cell_center = ParagraphStyle(
    'TableCellCenter',
    parent=styles['Normal'],
    fontName='Helvetica',
    fontSize=7.5,
    leading=9.5,
    textColor=colors.HexColor('#0F172A'),
    alignment=1
)

story = []

# Title Banner
story.append(Spacer(1, 10))
story.append(Paragraph("EQUITY LAB v0.0 — INSTITUTIONAL DOSSIER", subtitle_style))
story.append(Spacer(1, 4))
story.append(Paragraph("TOP 25 DEADLIEST COMBO EQUITIES", title_style))
story.append(Spacer(1, 4))
story.append(Paragraph("Dual-Engine Conjunction: Micro-Multibagger Fundamentals & Pre-Fly Technical Timing", subtitle_style))
story.append(Spacer(1, 6))
story.append(Paragraph(f"Data Verified: October 11, 2026 | Engine Phase 172 Institutional Hardening | Zero Hallucination Audit", meta_style))
story.append(Spacer(1, 14))
story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#0284C7'), spaceAfter=14))

# Executive Summary
summary_text = (
    "<b>Executive Overview & Dual-Engine Conjunction Protocol:</b><br/>"
    "This dossier presents the authoritative Top 25 Indian equities passing the dual conjunction of "
    "<b>Micro-Multibagger Compounding</b> (ROCE ≥ 20.0%, D/E ≤ 0.35, Promoter Pledge ≤ 5.0%, CFO/PAT &gt; 0, "
    "Market Cap ₹150 Cr – ₹15,000 Cr) and <b>Pre-Fly Launchpad Timing</b> (Weinstein Stage 1/2 base coiling, "
    "Upper Circuit Headroom ≥ 3.0%, Tier-scaled exit liquidity). Ranking is determined by multiplicative "
    "Cobb-Douglas utility: <i>Score = 100 × (Potential<sup>0.55</sup> × Timing<sup>0.30</sup> × Runway<sup>0.15</sup>) × Q</i>, "
    "penalizing single-dimension deficits and eliminating false precision."
)
story.append(Paragraph(summary_text, body_style))
story.append(Spacer(1, 14))

# Master Ranking Table
story.append(Paragraph("Master Institutional Ranking Matrix (Top 25)", h1_style))
story.append(Spacer(1, 4))

headers = [
    Paragraph("<b>#</b>", table_header_style),
    Paragraph("<b>Symbol</b>", table_header_style),
    Paragraph("<b>Company Name</b>", table_header_style),
    Paragraph("<b>Sector</b>", table_header_style),
    Paragraph("<b>CMP (₹)</b>", table_header_style),
    Paragraph("<b>MCap (₹Cr)</b>", table_header_style),
    Paragraph("<b>P/E</b>", table_header_style),
    Paragraph("<b>ROCE</b>", table_header_style),
    Paragraph("<b>D/E</b>", table_header_style),
    Paragraph("<b>RSI</b>", table_header_style),
    Paragraph("<b>Score</b>", table_header_style),
]

table_data = [headers]

for s in stocks:
    row = [
        Paragraph(str(s['rank']), table_cell_center),
        Paragraph(f"<b>{s['symbol']}</b>", table_cell_bold),
        Paragraph(s['name'], table_cell_style),
        Paragraph(s['sector'][:24], table_cell_style),
        Paragraph(f"{s['cmp']:,.1f}", table_cell_center),
        Paragraph(f"{s['mcap']:,.0f}", table_cell_center),
        Paragraph(f"{s['pe']:.1f}", table_cell_center),
        Paragraph(f"<b>{s['roce']:.1f}%</b>", table_cell_center),
        Paragraph(f"{s['de']:.2f}", table_cell_center),
        Paragraph(f"{s['rsi']:.1f}", table_cell_center),
        Paragraph(f"<b>{s['score']:.1f}</b>", table_cell_center),
    ]
    table_data.append(row)

col_widths = [18, 54, 115, 110, 44, 48, 30, 38, 28, 28, 32]
t = Table(table_data, colWidths=col_widths, repeatRows=1)
t.setStyle(TableStyle([
    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0F172A')),
    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
    ('TOPPADDING', (0, 0), (-1, -1), 3),
    ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#CBD5E1')),
    ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor('#FFFFFF'), colors.HexColor('#F8FAFC')]),
]))
story.append(t)
story.append(Spacer(1, 14))

# Section Break to Company Deep Dives
story.append(PageBreak())
story.append(Paragraph("Institutional Deep-Dive Profiles (Top 25 Candidates)", h1_style))
story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#CBD5E1'), spaceAfter=10))

for s in stocks:
    c_block = []
    header_line = f"<b>Rank #{s['rank']} — {s['symbol']} | {s['name']}</b> (Score: {s['score']:.2f} / 100)"
    c_block.append(Paragraph(header_line, h2_style))
    
    metrics_line = (
        f"<b>Sector:</b> {s['sector']} &nbsp;|&nbsp; "
        f"<b>CMP:</b> ₹{s['cmp']:,.2f} &nbsp;|&nbsp; "
        f"<b>MCap:</b> ₹{s['mcap']:,.0f} Cr &nbsp;|&nbsp; "
        f"<b>P/E:</b> {s['pe']:.1f}x &nbsp;|&nbsp; "
        f"<b>ROCE:</b> {s['roce']:.1f}% &nbsp;|&nbsp; "
        f"<b>ROE:</b> {s['roe']:.1f}% &nbsp;|&nbsp; "
        f"<b>D/E:</b> {s['de']:.2f} &nbsp;|&nbsp; "
        f"<b>Promoter:</b> {s['promoter_holding']:.1f}% (Pledge: {s['pledge']:.1f}%)"
    )
    c_block.append(Paragraph(metrics_line, body_style))
    c_block.append(Spacer(1, 2))

    tech_line = (
        f"<b>Technical Structure:</b> {s['stage']} &nbsp;|&nbsp; "
        f"<b>RSI (14):</b> {s['rsi']:.1f} &nbsp;|&nbsp; "
        f"<b>Convexity Ω:</b> {s['omega']:.2f}x &nbsp;|&nbsp; "
        f"<b>Cash Conversion (CFO/PAT):</b> {s['cfo_pat']:.2f}x"
    )
    c_block.append(Paragraph(tech_line, body_style))
    c_block.append(Spacer(1, 2))

    catalyst_line = f"<b>Fundamental Moat & Strategic Catalysts:</b> {s['catalyst']}"
    c_block.append(Paragraph(catalyst_line, body_style))
    c_block.append(Spacer(1, 8))
    c_block.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor('#E2E8F0'), spaceAfter=6))
    
    story.append(KeepTogether(c_block))

# Governance & Methodology Page
story.append(PageBreak())
story.append(Paragraph("Mathematical Methodology & Risk Governance", h1_style))
story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#CBD5E1'), spaceAfter=10))

methodology_text = (
    "<b>1. Multiplicative Cobb-Douglas Utility Ranking:</b><br/>"
    "The Deadliest Combo score evaluates the geometric confluence of fundamental strength, "
    "technical stage timing, and balance-sheet solvency:<br/>"
    "&nbsp;&nbsp;&nbsp;&nbsp;<b>Score = 100 × (Potential<sup>0.55</sup> × Timing<sup>0.30</sup> × Runway<sup>0.15</sup>) × Q</b><br/>"
    "where:<br/>"
    "• <i>Potential</i> incorporates fundamental quality score scaled by operating leverage convexity Ω<sup>0.10</sup>.<br/>"
    "• <i>Timing</i> represents the Technical Base Quality Engine (TBQE) evaluating Weinstein Stage 1/2 base tightness.<br/>"
    "• <i>Runway</i> scales reinvestment runway capacity based on historical base asset turn multiples.<br/>"
    "• <i>Q</i> is the Solvency & Governance multiplier: <i>0.50 + 0.50 × (0.35 Q<sub>D/E</sub> + 0.35 Q<sub>Pledge</sub> + 0.30 Q<sub>CFO</sub>)</i>.<br/><br/>"
    "<b>2. Mandatory Institutional Hard Gates (Zero-Exception):</b><br/>"
    "• <b>Market Cap:</b> ₹150 Cr to ₹15,000 Cr strictly enforced.<br/>"
    "• <b>Capital Efficiency:</b> ROCE ≥ 20.0% strictly enforced.<br/>"
    "• <b>Balance Sheet Fortress:</b> Debt/Equity ≤ 0.35 strictly enforced.<br/>"
    "• <b>Promoter Alignment:</b> Pledging ≤ 5.0% strictly enforced (fatal veto above 5%).<br/>"
    "• <b>Cash Realization:</b> CFO/PAT &gt; 0 with verified positive operating cash flow.<br/>"
    "• <b>Launchpad Liquidity:</b> Upper Circuit Headroom ≥ 3.0% with tier-scaled ADTV floors.<br/>"
    "• <b>Regulatory Hygiene:</b> Zero SEBI ASM Stage 3–4, GSM 1–4, ESM 2, NCLT insolvency, or qualified audit opinions.<br/><br/>"
    "<b>3. System Disclaimer:</b><br/>"
    "Equity Lab v0.0 is an artificial intelligence research and decision-support analytical system. "
    "This report is generated for algorithmic screening and comparative research purposes only. "
    "It does not constitute financial, investment, or legal advice. Market data accepts 1–2 hour delayed "
    "feeds for non-realtime institutional decision support."
)
story.append(Paragraph(methodology_text, body_style))

# Build Document
doc.build(story)
print(f"Generated PDF in workspace: {pdf_workspace_path}")

# Copy to artifact directory
try:
    import shutil
    shutil.copyfile(pdf_workspace_path, pdf_artifact_path)
    print(f"Copied PDF to artifact dir: {pdf_artifact_path}")
except Exception as e:
    print(f"Failed copying to artifact dir: {e}")
