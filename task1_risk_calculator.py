def compute_risk_metrics(portfolio):
    total_value = portfolio["total_value_inr"]
    monthly_expenses = portfolio["monthly_expenses_inr"]
    assets = portfolio["assets"]

    #--- Calclate Post Crash Value ---
    post_crash_value = 0
    for asset in assets:
        asset_value = total_value * (asset["allocation_pct"] / 100)
        crash_multiplier = 1 + (asset["expected_crash_pct"] / 100)
        post_crash_asset_value = asset_value * crash_multiplier

        post_crash_value += post_crash_asset_value
    
    # --- Runway months ---
    runway_months = post_crash_value / monthly_expenses

    # --- Ruin test ---
    ruin_test = "PASS" if runway_months > 12 else "FAIL"

    # --- Largest risk asset ---
    largest_risk_asset = ""
    max_risk_score = 0
    for asset in assets:
        risk_score = asset["allocation_pct"] * abs(asset["expected_crash_pct"])
        if risk_score > max_risk_score:
            max_risk_score = risk_score
            largest_risk_asset = asset["name"]

    # --- Concentration warning ---
    concentration_warning = any(
        asset["allocation_pct"] > 40 for asset in assets
    )

    return {
        "post_crash_value": round(post_crash_value, 2),
        "runway_months": round(runway_months, 2),
        "ruin_test": ruin_test,
        "largest_risk_asset": largest_risk_asset,
        "concentration_warning": concentration_warning,
    }

#--- BONUS ---
def compute_moderate_crash(portfolio):

    moderate_portfolio = {
        "total_value_inr": portfolio["total_value_inr"],
        "monthly_expenses_inr": portfolio["monthly_expenses_inr"],
        "assets": [
            {
                **asset,
                "expected_crash_pct": asset["expected_crash_pct"] * 0.5
            }
            for asset in portfolio["assets"]
        ]
    }
    return compute_risk_metrics(moderate_portfolio)

def print_allocation_bar_chart(portfolio):

    print("\n Portfolio Allocation:")
    print("-" * 40)
    for asset in portfolio["assets"]:
        bar = "█" * asset["allocation_pct"]  # one block per 1%
        print(f"{asset['name']:10} -> {bar} {asset['allocation_pct']}%",end="\n\n")
    print("-" * 40)


if __name__ == "__main__":
    portfolio = {
        "total_value_inr": 10_000_000,
        "monthly_expenses_inr": 80_000,
        "assets": [
            {"name": "BTC",     "allocation_pct": 30, "expected_crash_pct": -80},
            {"name": "NIFTY50", "allocation_pct": 40, "expected_crash_pct": -40},
            {"name": "GOLD",    "allocation_pct": 20, "expected_crash_pct": -15},
            {"name": "CASH",    "allocation_pct": 10, "expected_crash_pct":   0},
        ]
    }

    print("-"*40)
    print("Risk Metrics:")
    risk_metrics = compute_risk_metrics(portfolio)
    for key, value in risk_metrics.items():
        print(f"{key}: {value}")    
    print("-"*40)
    print("Moderate Crash Risk Metrics:")
    moderate_metrics = compute_moderate_crash(portfolio)
    for key, value in moderate_metrics.items():
        print(f"{key}: {value}")
    print("-"*40)
    print_allocation_bar_chart(portfolio)