def predict_wealth(investments, years=10):
    if not investments:
        return {"years": years, "timeline": [], "total_current": 0, "total_future": 0, "total_gain": 0, "cagr": 0}

    total_invested = sum(i["amount"] for i in investments)
    
    # Weighted average return
    weighted_return = sum(i["amount"] * i.get("expected_return", 12.0) for i in investments) / total_invested
    r = weighted_return / 100

    # Lumpsum projection: A = P(1+r)^t
    timeline = []
    for t in range(1, years + 1):
        future_value = total_invested * ((1 + r) ** t)
        gain = future_value - total_invested
        timeline.append({
            "year": t,
            "value": round(future_value, 2),
            "gain": round(gain, 2),
            "invested": round(total_invested, 2)
        })

    final = timeline[-1]["value"]
    total_gain = final - total_invested
    
    # SIP projection (assume monthly SIP = 5% of total invested / 12)
    monthly_sip = total_invested * 0.05 / 12
    r_monthly = r / 12
    n = years * 12
    sip_fv = monthly_sip * (((1 + r_monthly) ** n - 1) / r_monthly) * (1 + r_monthly)

    # Category-wise future value
    cat_futures = {}
    for inv in investments:
        cat = inv["category"]
        inv_r = inv.get("expected_return", 12.0) / 100
        fv = inv["amount"] * ((1 + inv_r) ** years)
        cat_futures[cat] = cat_futures.get(cat, 0) + fv

    return {
        "years": years,
        "timeline": timeline,
        "total_current": round(total_invested, 2),
        "total_future": round(final, 2),
        "total_gain": round(total_gain, 2),
        "gain_percent": round((total_gain / total_invested) * 100, 2),
        "cagr": round(weighted_return, 2),
        "sip_suggestion": {
            "monthly_amount": round(monthly_sip, 2),
            "future_value": round(sip_fv, 2)
        },
        "category_futures": {k: round(v, 2) for k, v in cat_futures.items()}
    }