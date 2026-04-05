from modules.analyzer import analyze_portfolio
from modules.risk import calculate_risk_profile

FUND_SUGGESTIONS = {
    "Large Cap":    ["Mirae Asset Large Cap Fund", "Axis Bluechip Fund", "HDFC Top 100 Fund", "SBI Bluechip Fund"],
    "Mid Cap":      ["Kotak Emerging Equity Fund", "Axis Midcap Fund", "HDFC Mid-Cap Opportunities", "DSP Midcap Fund"],
    "Small Cap":    ["SBI Small Cap Fund", "Nippon India Small Cap Fund", "Axis Small Cap Fund", "Canara Robeco Small Cap"],
    "ELSS":         ["Mirae Asset Tax Saver Fund", "Axis Long Term Equity Fund", "DSP Tax Saver Fund"],
    "Debt":         ["HDFC Short Term Debt Fund", "Kotak Bond Fund", "SBI Magnum Medium Duration"],
    "Index":        ["UTI Nifty 50 Index Fund", "HDFC Index Fund Nifty 50", "Mirae Asset Nifty 50 ETF"],
    "Hybrid":       ["HDFC Balanced Advantage Fund", "ICICI Pru Balanced Advantage", "Kotak Balanced Advantage"],
    "International":["Motilal Oswal Nasdaq 100 FOF", "Mirae Asset NYSE FANG+ ETF", "Franklin India Feeder US Opportunities"],
    "Gold":         ["SBI Gold Fund", "HDFC Gold Fund", "Axis Gold Fund"],
    "Flexi Cap":    ["Parag Parikh Flexi Cap Fund", "Axis Flexi Cap Fund", "Kotak Flexi Cap Fund"],
}

IDEAL_ALLOCATION = {
    "Aggressive":    {"Large Cap": 25, "Mid Cap": 30, "Small Cap": 25, "Debt": 10, "Gold": 5, "Index": 5},
    "Moderate":      {"Large Cap": 40, "Mid Cap": 20, "Small Cap": 10, "Debt": 20, "Gold": 5, "Hybrid": 5},
    "Conservative":  {"Large Cap": 30, "Mid Cap": 5,  "Small Cap": 0,  "Debt": 50, "Gold": 10, "Hybrid": 5},
}

def generate_recommendations(client, investments):
    analysis = analyze_portfolio(client, investments)
    risk     = calculate_risk_profile(client)
    profile  = risk["profile"]
    
    recs = []
    fund_suggestions = []
    rebalancing = []

    if not investments:
        recs.append({
            "type": "info",
            "icon": "💡",
            "title": "Start Your Portfolio",
            "detail": "No investments found. Add your first mutual fund to get personalized recommendations."
        })
        return {"recommendations": recs, "fund_suggestions": [], "rebalancing": [], "profile": profile}

    total = analysis["total_invested"]
    cat_dist = analysis["category_distribution"]
    ideal    = IDEAL_ALLOCATION.get(profile, IDEAL_ALLOCATION["Moderate"])

    for cat, data in cat_dist.items():
        pct    = data["percent"]
        ideal_pct = ideal.get(cat, ideal.get(cat.split()[0], 0) if " " in cat else 0)
        diff   = pct - ideal_pct

        if diff > 15:
            amount_excess = (diff / 100) * total
            recs.append({
                "type": "warning",
                "icon": "⚠️",
                "title": f"Reduce {cat} Exposure",
                "detail": f"You have {pct:.1f}% in {cat} vs ideal {ideal_pct}% for your {profile} profile. Consider moving ₹{amount_excess:,.0f} to better-diversified options."
            })
            rebalancing.append({
                "from_cat": cat,
                "current_pct": pct,
                "ideal_pct": ideal_pct,
                "amount": amount_excess,
                "action": "reduce"
            })

    missing = [c for c in ideal if ideal[c] > 5 and not any(
        cat.lower().startswith(c.lower()) or c.lower() in cat.lower()
        for cat in cat_dist
    )]
    for cat in missing:
        target_pct = ideal[cat]
        target_amt = (target_pct / 100) * total
        recs.append({
            "type": "suggestion",
            "icon": "💡",
            "title": f"Consider Adding {cat} Funds",
            "detail": f"Your {profile} profile recommends {target_pct}% in {cat}. That's approximately ₹{target_amt:,.0f} based on your portfolio size."
        })
        suggestions = FUND_SUGGESTIONS.get(cat, [])[:2]
        for f in suggestions:
            fund_suggestions.append({"category": cat, "fund": f, "reason": f"Ideal for {profile} investors"})


    score = analysis["diversification_score"]
    if score >= 75:
        recs.append({
            "type": "success",
            "icon": "✅",
            "title": "Excellent Diversification",
            "detail": f"Your portfolio has a diversification score of {score}/100. Keep maintaining this balance."
        })
    
   
    has_elss = any("elss" in i["category"].lower() or "elss" in i["fund_name"].lower() for i in investments)
    if not has_elss:
        recs.append({
            "type": "tax",
            "icon": "🏛️",
            "title": "Tax Saving Opportunity",
            "detail": "You have no ELSS funds. Investing up to ₹1.5L in ELSS gives tax deduction under Section 80C."
        })
        fund_suggestions.extend([
            {"category": "ELSS", "fund": f, "reason": "Tax saving under 80C"} 
            for f in FUND_SUGGESTIONS["ELSS"][:2]
        ])

   
    has_intl = any("international" in i["category"].lower() or "global" in i["category"].lower() for i in investments)
    if not has_intl and profile == "Aggressive":
        recs.append({
            "type": "suggestion",
            "icon": "🌍",
            "title": "International Diversification",
            "detail": "As an aggressive investor, consider 5-10% in international funds to hedge currency risk and access global growth."
        })

   
    recs.append({
        "type": "info",
        "icon": "📅",
        "title": "SIP Strategy Tip",
        "detail": f"For your risk profile ({profile}), monthly SIPs in equity funds can help rupee-cost averaging and compound wealth over time."
    })

    return {
        "recommendations": recs,
        "fund_suggestions": fund_suggestions[:8],
        "rebalancing": rebalancing,
        "profile": profile
    }