# Timecell Intern Assessment — Diyen Pambhar

This project contains solutions for all 4 tasks of the Timecell AI + Fintech internship test.


---



#  Task 1 — Portfolio Risk Calculator

### What I built
A function that calculates key risk metrics for a portfolio:
- post-crash value
- runway (months survival)
- ruin test (PASS/FAIL)
- largest risk asset
- concentration warning

### How it works
- For each asset:
  - calculate value = total × allocation
  - simulate crash using expected crash %
- Sum all values → post-crash portfolio value
- Compute runway = post_crash_value / monthly_expenses

### Bonus features
- Moderate crash scenario (50% crash impact)
- CLI bar chart for allocation visualization

### AI usage
Used ChatGPT to:
- validate formulas
- improve edge case handling
- refine variable naming

---

# Task 2 — Live Market Data Fetch

### What I built
A script that fetches real-time prices of:
- NIFTY50 (stock index)
- BTC and ETH (crypto)

### Tools used
- `yfinance` → stock/index data
- `CoinGecko API` → crypto prices
- `requests` → API calls

### Features
- Clean CLI table output
- Timestamp included
- Error handling using try/except (script continues even if one API fails)

---

# Task 3 — AI Portfolio Explainer

### What I built
A system that explains portfolio risk using an LLM in plain English.

### API used
Currently used **Groq (Llama 3.1)** because:
- free and fast
- no billing issues

 If billing was available, I would use **Claude (Anthropic)** because:
- better structured output
- stronger reasoning
- more reliable for financial explanations

---

### Prompt Engineering Approach

I experimented with prompts and improved them step by step.

#### Initial attempt
- Simple instruction prompt
- Output was generic and lacked reasoning

#### Improved prompt (final)
I added:

- **Role prompting**
  - “You are a financial advisor”

- **Structured output**
  - SUMMARY
  - DOING_WELL
  - SHOULD_CHANGE
  - VERDICT

- **Constraints**
  - Use numbers from portfolio
  - Avoid generic statements
  - No hallucination

- **Reasoning instructions**
  - consider allocation %
  - crash impact
  - diversification

### Result
- Output became more:
  - specific
  - actionable
  - consistent


---

# Task 4 — Portfolio Health Score (Open Problem)

### Problem I solved
Wealth managers need a **quick “health score” (0–100)**  
to compare portfolios easily.

---

### What I built
A scoring system similar to a credit score.

### Output includes:
- health score (0–100)
- grade (A/B/C/D)
- crash survival %
- runway
- risk flags
- suggestions
- benchmark (Conservative / Balanced / Aggressive)

---

### Scoring Logic (IMPORTANT)

Score is based on 4 factors:

#### 1. Diversification
- classify assets into low / medium / high risk
- score based on distribution across tiers

#### 2. Crash Survival
- simulate crash
- check how much portfolio survives

#### 3. Runway
- months user can survive after crash

#### 4. Concentration Risk
- penalize if one asset dominates

---

### Why this is strong
- not random scoring
- based on financial reasoning
- gives actionable suggestions

---

### Example insight
Instead of just saying “portfolio is risky”:

It says:
- which asset is risky
- why it is risky
- what to change

---
