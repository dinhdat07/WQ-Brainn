# Implementation Plan: Phase 22 - Fresh Exploration (Data-Field-First)

## 1. Context & Objective
The goal of Phase 22 is to strictly explore new data domains that have **never** been used in any submitted alphas from Phase 1-21, completely avoiding all legacy components (EPS, Sentiment, IV Skew, `fscore_bfl_value`, and the standard `intraday reversal` pattern). Success is measured by uniqueness and an orthogonal approach, with a target Sharpe > 1.5.

## 2. Extraction of Unused Fields
From `wq_data_fields_summary.md`, I have excluded all previously used fields. Below are the completely untouched categories and a selection of fields with >95% coverage (to avoid the sparse event input errors from Phase 21):

- **Model (Systematic Risk):** `beta_last_30_days_spy` (Coverage 97.6%)
- **Model (Fundamental Score):** `earnings_certainty_rank_derivative` (Coverage 100%)
- **Option Analytics:** `option_breakeven_30` (Coverage 98.3%)
- **Social Media Data:** `snt_social_volume` (Coverage 100%)

## 3. Selected Fields & Economic Intuitions

### Field 1: `beta_last_30_days_spy` (Systematic Risk)
- **Economic Intuition:** The "Betting Against Beta" anomaly. High-beta stocks are systematically overpriced because retail and constrained investors overpay for lottery-like payoff profiles. By shorting high-beta and going long low-beta, we capture a robust market-neutral premium.
- **Novel Formula (Interaction with Volatility):** Instead of standard linear addition, we will scale the low-beta preference by its short-term price stability.
  - `Idea 1`: `ts_decay_linear(group_zscore(-beta_last_30_days_spy, subindustry) * ts_rank(-historical_volatility_10, 20), 10)`

### Field 2: `earnings_certainty_rank_derivative` (Fundamental Scores)
- **Economic Intuition:** This field measures the acceleration (derivative) of earnings certainty. Markets are slow to price in risk reduction. When earnings certainty is increasing (positive derivative), the stock is progressively de-risked in analysts' models, commanding a multiple expansion (price increase).
- **Novel Formula (Time-Series Acceleration):** We look for stocks where the certainty is not just high, but actively accelerating against their own historical baseline.
  - `Idea 2`: `ts_decay_linear(group_rank(earnings_certainty_rank_derivative - ts_mean(earnings_certainty_rank_derivative, 20), sector), 10)`

### Field 3: `option_breakeven_30` (Options Analytics)
- **Economic Intuition:** The options breakeven represents the collective market-maker breakeven. If `option_breakeven_30` is heavily disconnected from the current `close`, it implies the derivatives market is heavily positioned for a directional move. The ratio of Breakeven to Close captures this built-in expectation.
- **Novel Formula (Breakeven Premium):** 
  - `Idea 3`: `ts_decay_linear(group_rank(option_breakeven_30 / close, subindustry), 5)`

### Field 4: `snt_social_volume` (Social Media)
- **Economic Intuition:** Extreme social media volume reflects retail frenzy, typically marking local tops (over-buying) before severe mean reversion. Boring stocks with low tweet volume slowly compound via institutional buying without the hype penalty.
- **Novel Formula (Attention Penalty Factor):**
  - `Idea 4`: `trade_when(snt_social_volume < ts_mean(snt_social_volume, 60), group_rank(-snt_social_volume, market), -1)` 

## 4. Execution Steps
1. **Simulation:** Run the 4 ideas directly in WorldQuant Brain using `test_phase22_fresh_explore.py`.
2. **Hard Gates:** Filter out any alpha failing `Sub-universe Sharpe >= 0.8` and `Self-Correlation >= 0.65`.
3. **Review:** Log exact metrics (Sharpe, Fitness, Turnover) for each and submit the best one that survives the correlation gate.

## User Review Required
> [!IMPORTANT]
> Please review the 4 selected orthogonal fields and the novel formulas proposed above. Are these distinct enough from past configurations? Do the intuitions align with your expectations for Phase 22?
