import os
from datetime import datetime

def generate_pdf_report(client, investments, analysis, risk, recommendations, wealth_data):
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.lib import colors
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
        from reportlab.lib.units import inch, cm
        from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
    except ImportError:
        # Fallback: create a simple text file
        path = f"/tmp/report_{client['id']}.txt"
        with open(path, "w") as f:
            f.write(f"Portfolio Report - {client['name']}\n")
            f.write(f"Generated: {datetime.now().strftime('%d %b %Y')}\n\n")
            f.write(f"Total Invested: ₹{analysis['total_invested']:,.0f}\n")
            f.write(f"Risk Profile: {risk['profile']}\n")
        return path

    path = f"/tmp/report_{client['id']}.pdf"
    doc  = SimpleDocTemplate(path, pagesize=A4,
                              rightMargin=2*cm, leftMargin=2*cm,
                              topMargin=2*cm, bottomMargin=2*cm)

    # Colors
    NAVY    = colors.HexColor("#0f172a")
    BLUE    = colors.HexColor("#2563eb")
    TEAL    = colors.HexColor("#0d9488")
    AMBER   = colors.HexColor("#d97706")
    RED     = colors.HexColor("#dc2626")
    GREEN   = colors.HexColor("#16a34a")
    LGRAY   = colors.HexColor("#f1f5f9")
    MGRAY   = colors.HexColor("#94a3b8")

    styles = getSampleStyleSheet()
    title_style  = ParagraphStyle("title",  fontSize=22, textColor=NAVY,  fontName="Helvetica-Bold", spaceAfter=4)
    h2_style     = ParagraphStyle("h2",     fontSize=14, textColor=BLUE,  fontName="Helvetica-Bold", spaceAfter=6, spaceBefore=14)
    h3_style     = ParagraphStyle("h3",     fontSize=11, textColor=NAVY,  fontName="Helvetica-Bold", spaceAfter=4)
    body_style   = ParagraphStyle("body",   fontSize=9,  textColor=colors.HexColor("#334155"), leading=14)
    small_style  = ParagraphStyle("small",  fontSize=8,  textColor=MGRAY)
    center_style = ParagraphStyle("center", fontSize=9,  alignment=TA_CENTER)

    story = []

    # ── HEADER ──────────────────────────────────────────────────
    story.append(Paragraph("MFD Advisory Platform", ParagraphStyle("brand", fontSize=10, textColor=MGRAY)))
    story.append(Paragraph(f"Portfolio Analysis Report", title_style))
    story.append(Paragraph(f"Client: <b>{client['name']}</b> &nbsp;|&nbsp; {client['email']}", body_style))
    story.append(Paragraph(f"Generated on {datetime.now().strftime('%d %B %Y, %I:%M %p')}", small_style))
    story.append(HRFlowable(width="100%", thickness=2, color=BLUE, spaceAfter=10))

    # ── SUMMARY CARDS ────────────────────────────────────────────
    story.append(Paragraph("Portfolio Summary", h2_style))
    summary_data = [
        ["Total Invested", "Risk Profile", "Diversification", "Expected CAGR"],
        [
            f"₹{analysis['total_invested']:,.0f}",
            risk["profile"],
            f"{analysis['diversification_score']}/100",
            f"{wealth_data['cagr']:.1f}%"
        ]
    ]
    t = Table(summary_data, colWidths=[4*cm, 4*cm, 4*cm, 4*cm])
    t.setStyle(TableStyle([
        ("BACKGROUND",  (0,0), (-1,0), NAVY),
        ("TEXTCOLOR",   (0,0), (-1,0), colors.white),
        ("BACKGROUND",  (0,1), (-1,-1), LGRAY),
        ("FONTNAME",    (0,0), (-1,0), "Helvetica-Bold"),
        ("FONTNAME",    (0,1), (-1,-1), "Helvetica-Bold"),
        ("FONTSIZE",    (0,0), (-1,0), 9),
        ("FONTSIZE",    (0,1), (-1,-1), 13),
        ("ALIGN",       (0,0), (-1,-1), "CENTER"),
        ("VALIGN",      (0,0), (-1,-1), "MIDDLE"),
        ("ROWBACKGROUNDS", (0,1), (-1,-1), [LGRAY]),
        ("GRID",        (0,0), (-1,-1), 0.5, colors.white),
        ("ROWHEIGHT",   (0,0), (-1,-1), 28),
    ]))
    story.append(t)
    story.append(Spacer(1, 12))

    story.append(Paragraph("Client Details", h2_style))
    client_data = [
        ["Name", client["name"], "Age", str(client.get("age") or "—")],
        ["Email", client["email"], "Income", f"₹{client.get('income',0):,.0f}/yr" if client.get("income") else "—"],
        ["Risk Appetite", client.get("risk_appetite","—"), "Profile", risk["profile"]],
    ]
    ct = Table(client_data, colWidths=[3*cm, 6*cm, 3*cm, 5*cm])
    ct.setStyle(TableStyle([
        ("FONTNAME",  (0,0), (0,-1), "Helvetica-Bold"),
        ("FONTNAME",  (2,0), (2,-1), "Helvetica-Bold"),
        ("TEXTCOLOR", (0,0), (0,-1), BLUE),
        ("TEXTCOLOR", (2,0), (2,-1), BLUE),
        ("FONTSIZE",  (0,0), (-1,-1), 9),
        ("ROWBACKGROUNDS", (0,0), (-1,-1), [colors.white, LGRAY]),
        ("GRID", (0,0), (-1,-1), 0.3, colors.HexColor("#e2e8f0")),
        ("ROWHEIGHT", (0,0), (-1,-1), 20),
        ("VALIGN",    (0,0), (-1,-1), "MIDDLE"),
        ("LEFTPADDING",(0,0),(-1,-1), 6),
    ]))
    story.append(ct)
    story.append(Spacer(1, 12))

    story.append(Paragraph("Investment Holdings", h2_style))
    if investments:
        inv_data = [["Fund Name", "Category", "Amount (₹)", "Date", "Exp. Return"]]
        for inv in investments:
            inv_data.append([
                inv["fund_name"][:35],
                inv["category"],
                f"₹{inv['amount']:,.0f}",
                inv["date"],
                f"{inv.get('expected_return',12)}%"
            ])
        inv_data.append(["TOTAL", "", f"₹{analysis['total_invested']:,.0f}", "", ""])
        it = Table(inv_data, colWidths=[6.5*cm, 3.5*cm, 3*cm, 2.5*cm, 2*cm])
        style = [
            ("BACKGROUND",  (0,0), (-1,0), NAVY),
            ("TEXTCOLOR",   (0,0), (-1,0), colors.white),
            ("FONTNAME",    (0,0), (-1,0), "Helvetica-Bold"),
            ("FONTNAME",    (0,-1),(-1,-1),"Helvetica-Bold"),
            ("BACKGROUND",  (0,-1),(-1,-1), LGRAY),
            ("FONTSIZE",    (0,0), (-1,-1), 8),
            ("ALIGN",       (2,0), (4,-1), "RIGHT"),
            ("GRID",        (0,0), (-1,-1), 0.3, colors.HexColor("#e2e8f0")),
            ("ROWBACKGROUNDS",(0,1),(-2,-1), [colors.white, LGRAY]),
            ("ROWHEIGHT",   (0,0), (-1,-1), 18),
            ("LEFTPADDING", (0,0), (-1,-1), 5),
        ]
        it.setStyle(TableStyle(style))
        story.append(it)
    else:
        story.append(Paragraph("No investments recorded.", body_style))
    story.append(Spacer(1, 12))

    if analysis.get("category_distribution"):
        story.append(Paragraph("Category Distribution", h2_style))
        cat_data = [["Category", "Amount (₹)", "Allocation %"]]
        for cat, data in analysis["category_distribution"].items():
            cat_data.append([cat, f"₹{data['amount']:,.0f}", f"{data['percent']:.1f}%"])
        ctbl = Table(cat_data, colWidths=[7*cm, 5*cm, 4.5*cm])
        ctbl.setStyle(TableStyle([
            ("BACKGROUND", (0,0), (-1,0), TEAL),
            ("TEXTCOLOR",  (0,0), (-1,0), colors.white),
            ("FONTNAME",   (0,0), (-1,0), "Helvetica-Bold"),
            ("FONTSIZE",   (0,0), (-1,-1), 9),
            ("ALIGN",      (1,0), (2,-1), "RIGHT"),
            ("GRID",       (0,0), (-1,-1), 0.3, colors.HexColor("#e2e8f0")),
            ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.white, LGRAY]),
            ("ROWHEIGHT",  (0,0), (-1,-1), 18),
            ("LEFTPADDING",(0,0), (-1,-1), 6),
        ]))
        story.append(ctbl)
    story.append(Spacer(1, 12))

    story.append(Paragraph("Risk Profile Analysis", h2_style))
    story.append(Paragraph(f"<b>Profile: {risk['profile']}</b> (Score: {risk['score']}/100)", h3_style))
    story.append(Paragraph(risk["description"], body_style))
    story.append(Spacer(1, 8))

   
    story.append(Paragraph("Wealth Projection (10 Years)", h2_style))
    wp_data = [["Year", "Projected Value (₹)", "Total Gain (₹)", "Return %"]]
    for t in wealth_data["timeline"][::2]:  # every 2 years
        gain_pct = (t["gain"] / wealth_data["total_current"] * 100) if wealth_data["total_current"] else 0
        wp_data.append([
            f"Year {t['year']}",
            f"₹{t['value']:,.0f}",
            f"₹{t['gain']:,.0f}",
            f"{gain_pct:.1f}%"
        ])
    wt = Table(wp_data, colWidths=[3.5*cm, 5.5*cm, 5.5*cm, 3*cm])
    wt.setStyle(TableStyle([
        ("BACKGROUND",  (0,0), (-1,0), BLUE),
        ("TEXTCOLOR",   (0,0), (-1,0), colors.white),
        ("FONTNAME",    (0,0), (-1,0), "Helvetica-Bold"),
        ("FONTSIZE",    (0,0), (-1,-1), 9),
        ("ALIGN",       (1,0), (3,-1), "RIGHT"),
        ("GRID",        (0,0), (-1,-1), 0.3, colors.HexColor("#e2e8f0")),
        ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.white, LGRAY]),
        ("ROWHEIGHT",   (0,0), (-1,-1), 18),
        ("LEFTPADDING", (0,0), (-1,-1), 6),
    ]))
    story.append(wt)
    story.append(Spacer(1, 8))
    story.append(Paragraph(
        f"At {wealth_data['cagr']:.1f}% CAGR, your portfolio of ₹{wealth_data['total_current']:,.0f} "
        f"is projected to grow to <b>₹{wealth_data['total_future']:,.0f}</b> in {wealth_data['years']} years, "
        f"a gain of ₹{wealth_data['total_gain']:,.0f} ({wealth_data['gain_percent']:.1f}%).",
        body_style
    ))
    story.append(Spacer(1, 12))

    story.append(Paragraph("AI Recommendations", h2_style))
    for rec in recommendations.get("recommendations", [])[:6]:
        story.append(Paragraph(f"<b>{rec['icon']} {rec['title']}</b>", h3_style))
        story.append(Paragraph(rec["detail"], body_style))
        story.append(Spacer(1, 4))

    story.append(HRFlowable(width="100%", thickness=1, color=MGRAY, spaceAfter=8, spaceBefore=16))
    story.append(Paragraph(
        "<i>Disclaimer: This report is generated for informational purposes only and does not constitute financial advice. "
        "Past performance is not indicative of future results. Please consult a SEBI-registered investment advisor before making any investment decisions.</i>",
        ParagraphStyle("disclaimer", fontSize=7, textColor=MGRAY, leading=10)
    ))

    doc.build(story)
    return path