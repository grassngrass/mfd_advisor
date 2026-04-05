def calculate_risk_profile(client):
    age            = client.get("age") or 35
    income         = client.get("income") or 500000
    risk_appetite  = (client.get("risk_appetite") or "Moderate").lower()

    # Base profile from age
    if age < 30:
        age_profile = "Aggressive"
        age_score   = 80
    elif age < 45:
        age_profile = "Moderate"
        age_score   = 55
    elif age < 60:
        age_profile = "Conservative"
        age_score   = 35
    else:
        age_profile = "Very Conservative"
        age_score   = 15

    # Income score
    if income >= 2000000:
        income_score = 30
    elif income >= 1000000:
        income_score = 20
    elif income >= 500000:
        income_score = 10
    else:
        income_score = 5

    # Appetite score
    appetite_map = {"aggressive": 20, "moderate": 10, "conservative": 0}
    appetite_score = appetite_map.get(risk_appetite, 10)

    total_score = age_score * 0.5 + income_score + appetite_score

    # Final profile
    if total_score >= 65:
        profile = "Aggressive"
        color   = "#ef4444"
        description = "High-risk, high-reward. Suitable for equity-heavy portfolios with long investment horizons."
        suggested_allocation = {"Equity (Large Cap)": 25, "Equity (Mid Cap)": 30, "Equity (Small Cap)": 25, "Debt": 10, "Gold/Others": 10}
    elif total_score >= 40:
        profile = "Moderate"
        color   = "#f59e0b"
        description = "Balanced approach. Mix of equity and debt for steady growth with manageable risk."
        suggested_allocation = {"Equity (Large Cap)": 40, "Equity (Mid Cap)": 20, "Equity (Small Cap)": 10, "Debt": 25, "Gold/Others": 5}
    else:
        profile = "Conservative"
        color   = "#10b981"
        description = "Safety-first approach. Emphasis on capital preservation with stable returns."
        suggested_allocation = {"Equity (Large Cap)": 25, "Equity (Mid Cap)": 5, "Equity (Small Cap)": 0, "Debt": 55, "Gold/Others": 15}

    return {
        "profile": profile,
        "score": round(total_score, 1),
        "color": color,
        "description": description,
        "age_profile": age_profile,
        "suggested_allocation": suggested_allocation,
        "factors": {
            "age": age,
            "income": income,
            "risk_appetite": risk_appetite.capitalize()
        }
    }