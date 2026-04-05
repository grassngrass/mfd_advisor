def analyze_portfolio(client, investments):
    if not investments:
        return {
            "total_invested": 0,
            "category_distribution": {},
            "diversification_score": 0,
            "insights": ["No investments found. Add funds to get analysis."],
            "alerts": [],
            "fund_count": 0
        }

    total = sum(i["amount"] for i in investments)
    
    # Category breakdown
    cat_totals = {}
    for inv in investments:
        cat = inv["category"]
        cat_totals[cat] = cat_totals.get(cat, 0) + inv["amount"]
    
    cat_dist = {
        cat: {"amount": amt, "percent": round(amt / total * 100, 2)}
        for cat, amt in cat_totals.items()
    }
    
    # Diversification score (0–100)
    num_categories = len(cat_totals)
    max_percent = max(v["percent"] for v in cat_dist.values())
    
    score = 0
    if num_categories >= 5:
        score += 40
    elif num_categories >= 3:
        score += 25
    elif num_categories >= 2:
        score += 10
    
    if max_percent <= 40:
        score += 60
    elif max_percent <= 50:
        score += 45
    elif max_percent <= 60:
        score += 30
    elif max_percent <= 70:
        score += 15
    else:
        score += 0

    score = min(score, 100)

    # Insights
    insights = []
    alerts = []

    for cat, data in cat_dist.items():
        pct = data["percent"]
        if pct > 60:
            alerts.append(f"🚨 Heavy concentration in {cat} ({pct:.1f}%) — consider rebalancing")
        elif pct > 50:
            insights.append(f"⚠️ Overexposed to {cat} ({pct:.1f}%) — moderate risk")
        elif pct < 5:
            insights.append(f"💡 {cat} is underweighted ({pct:.1f}%) — room to grow")

    if num_categories == 1:
        alerts.append("🚨 Single category portfolio — extremely high concentration risk")
    elif num_categories == 2:
        insights.append("⚠️ Only 2 categories — consider adding more fund types for diversification")

    if score >= 75:
        insights.append("✅ Well-diversified portfolio — good spread across categories")
    elif score >= 50:
        insights.append("📊 Moderately diversified — some rebalancing recommended")
    else:
        insights.append("📉 Poor diversification — significant rebalancing needed")

    # Find top fund
    top_fund = max(investments, key=lambda x: x["amount"])
    insights.append(f"🏆 Largest holding: {top_fund['fund_name']} (₹{top_fund['amount']:,.0f})")

    return {
        "total_invested": total,
        "category_distribution": cat_dist,
        "diversification_score": score,
        "insights": insights,
        "alerts": alerts,
        "fund_count": len(investments),
        "num_categories": num_categories,
        "top_category": max(cat_dist, key=lambda k: cat_dist[k]["amount"])
    }