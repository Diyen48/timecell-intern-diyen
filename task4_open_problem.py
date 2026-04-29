"""
TASK 4 — Portfolio Health Score (Improved)

Problems fixed:
1. Oversimplification → scoring now based on WHAT assets are, not just how many
2. Arbitrary scoring  → each factor has a financial rationale (explained in comments)
3. No actionable insight → every low score generates a specific suggestion

New addition:
- Benchmarking against 3 model portfolios (Conservative / Balanced / Aggressive)
"""


# ---------------------------------------------------------------------------
# ASSET RISK CLASSIFICATION
# Based on standard financial risk tiers used by wealth managers
# ---------------------------------------------------------------------------
ASSET_RISK_TIER = {
    # Low risk
    "CASH": 1, "FD": 1, "BONDS": 1, "DEBT": 1,
    # Medium risk
    "GOLD": 2, "NIFTY50": 2, "SENSEX": 2, "INDEX": 2,
    # High risk
    "BTC": 3, "ETH": 3, "CRYPTO": 3, "SMALLCAP": 3,
}

def get_risk_tier(asset_name):
    """
    Returns risk tier 1/2/3 for an asset.
    Defaults to tier 2 (medium) if asset is unknown.
    """
    return ASSET_RISK_TIER.get(asset_name.upper(), 2)


# ---------------------------------------------------------------------------
# MODEL PORTFOLIOS FOR BENCHMARKING
# These are standard allocations used in Indian wealth management
# ---------------------------------------------------------------------------
MODEL_PORTFOLIOS = {
    "Conservative": {
        "low_risk_pct":  60,   # majority in safe assets
        "mid_risk_pct":  30,
        "high_risk_pct": 10,
        "min_runway":    24,   # 2 years buffer
    },
    "Balanced": {
        "low_risk_pct":  25,
        "mid_risk_pct":  45,
        "high_risk_pct": 30,
        "min_runway":    12,   # 1 year buffer
    },
    "Aggressive": {
        "low_risk_pct":  10,
        "mid_risk_pct":  30,
        "high_risk_pct": 60,
        "min_runway":    6,    # 6 months buffer
    },
}


# ---------------------------------------------------------------------------
# FACTOR 1: DIVERSIFICATION (25 pts)
# Logic: We measure HOW RISKY the mix is, not just how many assets
#
# A portfolio of 5 crypto assets is NOT diversified.
# A portfolio of 3 assets (cash + index + gold) IS diversified.
#
# We reward having allocation spread across all 3 risk tiers.
# ---------------------------------------------------------------------------
def score_diversification(assets):
    tier_allocations = {1: 0, 2: 0, 3: 0}

    for asset in assets:
        tier = get_risk_tier(asset["name"])
        tier_allocations[tier] += asset["allocation_pct"]

    score = 0
    flags = []
    suggestions = []

    # Reward for having each tier present (up to 8 pts each = 24 pts)
    # +1 bonus point if all three tiers are present
    tiers_present = 0
    for tier, alloc in tier_allocations.items():
        if alloc > 0:
            tiers_present += 1
            tier_score = min(alloc / 100 * 16, 8)  # proportional, max 8 per tier
            score += tier_score

    if tiers_present == 3:
        score += 1  # bonus for true diversification

    score = min(round(score, 1), 25)

    # Generate flags
    if tier_allocations[1] < 10:
        flags.append("Less than 10% in safe assets (cash/bonds/FD)")
        suggestions.append("Add 10–20% in low-risk assets like debt funds or FD")

    if tier_allocations[3] > 50:
        flags.append(f"{tier_allocations[3]}% in high-risk assets (crypto/smallcap)")
        suggestions.append("Consider reducing high-risk exposure below 40%")

    if tiers_present < 2:
        flags.append("Portfolio concentrated in a single risk tier")
        suggestions.append("Spread across at least 2–3 asset types")

    status = "✔" if score >= 15 else "❌"
    return score, status, flags, suggestions, tier_allocations


# ---------------------------------------------------------------------------
# FACTOR 2: CRASH SURVIVAL (25 pts)
# Logic: What % of portfolio survives the worst-case crash?
#
# Financial basis: A portfolio that retains >60% after crash is considered
# resilient. Below 40% is dangerous for long-term recovery.
#
# Thresholds based on historical bear market data:
# >70% retained → excellent (2008 crash: balanced portfolios lost ~30%)
# 50–70% retained → acceptable
# 30–50% retained → risky
# <30% retained → critical
# ---------------------------------------------------------------------------
def score_crash_survival(assets, total_value):
    post_crash = sum(
        total_value * (a["allocation_pct"] / 100) * (1 + a["expected_crash_pct"] / 100)
        for a in assets
    )
    retained_pct = (post_crash / total_value) * 100

    flags = []
    suggestions = []

    if retained_pct >= 70:
        score = 25
    elif retained_pct >= 50:
        score = 18
    elif retained_pct >= 30:
        score = 10
    else:
        score = 3

    # Find which assets are dragging the score down
    biggest_losers = sorted(
        assets,
        key=lambda a: a["allocation_pct"] * abs(a["expected_crash_pct"]),
        reverse=True
    )

    if retained_pct < 50:
        worst = biggest_losers[0]
        flags.append(
            f"{worst['name']} ({worst['allocation_pct']}% allocated, "
            f"{worst['expected_crash_pct']}% crash) is your biggest risk"
        )
        suggestions.append(
            f"Reduce {worst['name']} allocation or hedge with safer assets"
        )

    if retained_pct < 30:
        flags.append("Portfolio would lose over 70% in a crash — recovery could take 10+ years")
        suggestions.append("Shift at least 20% into stable assets immediately")

    status = "✔" if score >= 15 else "❌"
    return score, status, flags, suggestions, round(post_crash), round(retained_pct, 1)


# ---------------------------------------------------------------------------
# FACTOR 3: RUNWAY (25 pts)
# Logic: How many months can you live off post-crash portfolio?
#
# Financial basis:
# Standard emergency fund = 6 months (basic safety)
# Wealth management standard = 12 months minimum
# Conservative target = 24+ months
# Why post-crash? Because the crash is exactly when you'd need the money most
# ---------------------------------------------------------------------------
def score_runway(post_crash_value, monthly_expenses):
    runway = post_crash_value / monthly_expenses

    flags = []
    suggestions = []

    if runway >= 36:
        score = 25
    elif runway >= 24:
        score = 20
    elif runway >= 12:
        score = 12
    elif runway >= 6:
        score = 6
    else:
        score = 0

    if runway < 6:
        flags.append(f"Only {round(runway, 1)} months of expenses covered after crash")
        suggestions.append("Increase cash/liquid allocation to cover at least 6 months")
    elif runway < 12:
        flags.append(f"{round(runway, 1)} months runway is below the 12-month safety threshold")
        suggestions.append("Target 12+ months runway — increase stable asset allocation")

    status = "✔" if score >= 12 else "❌"
    return score, status, flags, suggestions, round(runway, 1)


# ---------------------------------------------------------------------------
# FACTOR 4: CONCENTRATION RISK (25 pts)
# Logic: Is too much money in one single asset?
#
# Financial basis:
# >50% in one asset = dangerous (company/sector collapse risk)
# 30–50% = elevated risk
# <30% = acceptable concentration
# Rule of thumb: "no single position > 20–25%" (standard wealth mgmt rule)
# ---------------------------------------------------------------------------
def score_concentration(assets):
    max_asset = max(assets, key=lambda a: a["allocation_pct"])
    max_alloc = max_asset["allocation_pct"]

    flags = []
    suggestions = []

    if max_alloc <= 25:
        score = 25
    elif max_alloc <= 35:
        score = 18
    elif max_alloc <= 50:
        score = 10
    else:
        score = 3

    if max_alloc > 35:
        flags.append(f"{max_asset['name']} takes up {max_alloc}% of your portfolio")
        suggestions.append(
            f"Reduce {max_asset['name']} to below 30% and redistribute to other assets"
        )

    status = "✔" if score >= 15 else "❌"
    return score, status, flags, suggestions


# ---------------------------------------------------------------------------
# BENCHMARKING
# Compare the portfolio's risk tier mix against model portfolios
# Returns which model portfolio this is closest to
# ---------------------------------------------------------------------------
def benchmark_portfolio(tier_allocations, runway_months):
    scores = {}

    for model_name, model in MODEL_PORTFOLIOS.items():
        # How close is this portfolio to the model's tier allocation?
        low_diff  = abs(tier_allocations[1] - model["low_risk_pct"])
        mid_diff  = abs(tier_allocations[2] - model["mid_risk_pct"])
        high_diff = abs(tier_allocations[3] - model["high_risk_pct"])
        runway_diff = abs(runway_months - model["min_runway"])

        # Lower total difference = closer match
        total_diff = low_diff + mid_diff + high_diff + runway_diff
        scores[model_name] = total_diff

    closest = min(scores, key=scores.get)
    return closest, scores


def compute_health_score(portfolio):
    total    = portfolio["total_value_inr"]
    expenses = portfolio["monthly_expenses_inr"]
    assets   = portfolio["assets"]

    all_flags       = []
    all_suggestions = []

    # Score each factor
    d_score, d_status, d_flags, d_sugg, tier_alloc = score_diversification(assets)
    c_score, c_status, c_flags, c_sugg, post_crash, retained_pct = score_crash_survival(assets, total)
    r_score, r_status, r_flags, r_sugg, runway = score_runway(post_crash, expenses)
    k_score, k_status, k_flags, k_sugg = score_concentration(assets)

    all_flags       = d_flags + c_flags + r_flags + k_flags
    all_suggestions = d_sugg  + c_sugg  + r_sugg  + k_sugg

    total_score = round(d_score + c_score + r_score + k_score, 1)

    # Grade
    if total_score >= 85:
        grade = "A 🟢 Excellent"
    elif total_score >= 70:
        grade = "B 🟡 Good"
    elif total_score >= 50:
        grade = "C 🟠 Needs Work"
    else:
        grade = "D 🔴 High Risk"

    # Benchmark
    closest_model, benchmark_scores = benchmark_portfolio(tier_alloc, runway)

    return {
        "total_score": total_score,
        "grade": grade,
        "breakdown": {
            "Diversification":    (d_score, 25, d_status),
            "Crash Survival":     (c_score, 25, c_status),
            "Runway":             (r_score, 25, r_status),
            "Concentration Risk": (k_score, 25, k_status),
        },
        "post_crash_value": post_crash,
        "retained_pct":     retained_pct,
        "runway_months":    runway,
        "flags":            all_flags,
        "suggestions":      all_suggestions,
        "closest_model":    closest_model,
        "tier_allocation":  tier_alloc,
    }


def print_health_report(name, portfolio):
    r = compute_health_score(portfolio)

    print(f"\n{'='*55}")
    print(f"  📊 Portfolio: {name}")
    print(f"  Health Score : {r['total_score']} / 100  |  {r['grade']}")
    print(f"  Closest To   : {r['closest_model']} model portfolio")
    print(f"{'='*55}")

    print(f"\n  Post-crash value : ₹{r['post_crash_value']:,}  ({r['retained_pct']}% retained)")
    print(f"  Runway           : {r['runway_months']} months of expenses covered\n")

    print("  Score Breakdown:")
    print(f"  {'Factor':<22} {'Score':>6}   {'Bar'}")
    print("  " + "-" * 50)
    for factor, (score, max_score, status) in r["breakdown"].items():
        bar = "█" * int(score) + "░" * int(max_score - score)
        print(f"  {status} {factor:<20} {score:>4}/{max_score}  {bar}")

    print(f"\n  Risk Tier Mix:")
    print(f"    Low risk  (cash/bonds/FD) : {r['tier_allocation'][1]}%")
    print(f"    Mid risk  (index/gold)    : {r['tier_allocation'][2]}%")
    print(f"    High risk (crypto)        : {r['tier_allocation'][3]}%")

    if r["flags"]:
        print(f"\n  ⚠️  Top Risks:")
        for flag in r["flags"]:
            print(f"    - {flag}")

    if r["suggestions"]:
        print(f"\n  💡 Suggestions:")
        for suggestion in r["suggestions"]:
            print(f"    → {suggestion}")

    print()


if __name__ == "__main__":
    portfolios = {
        "Aggressive (BTC Heavy)": {
            "total_value_inr": 10_000_000,
            "monthly_expenses_inr": 80_000,
            "assets": [
                {"name": "BTC",  "allocation_pct": 60, "expected_crash_pct": -80},
                {"name": "ETH",  "allocation_pct": 30, "expected_crash_pct": -70},
                {"name": "CASH", "allocation_pct": 10, "expected_crash_pct":   0},
            ]
        },
        "Balanced Portfolio": {
            "total_value_inr": 10_000_000,
            "monthly_expenses_inr": 80_000,
            "assets": [
                {"name": "BTC",     "allocation_pct": 30, "expected_crash_pct": -80},
                {"name": "NIFTY50", "allocation_pct": 40, "expected_crash_pct": -40},
                {"name": "GOLD",    "allocation_pct": 20, "expected_crash_pct": -15},
                {"name": "CASH",    "allocation_pct": 10, "expected_crash_pct":   0},
            ]
        },
        "Conservative Portfolio": {
            "total_value_inr": 10_000_000,
            "monthly_expenses_inr": 80_000,
            "assets": [
                {"name": "GOLD",    "allocation_pct": 30, "expected_crash_pct": -15},
                {"name": "BONDS",   "allocation_pct": 40, "expected_crash_pct":  -5},
                {"name": "NIFTY50", "allocation_pct": 10, "expected_crash_pct": -40},
                {"name": "CASH",    "allocation_pct": 20, "expected_crash_pct":   0},
            ]
        },
    }

    print("\nTIMECELL PORTFOLIO HEALTH SCORE REPORT")
    print("=" * 55)

    for name, portfolio in portfolios.items():
        print_health_report(name, portfolio)