# Alpha Profile: le3WZmdl (Analyst Overpriced Stocks)

## Metadata
- **Alpha ID:** `le3WZmdl`
- **Batch:** Batch 7 - 10
- **Submission Status:** SUCCESS (Self-Correlation 0.0)
- **Concept:** Analyst Estimates / Overpriced Stocks

## Metrics (In-Sample)
- **Sharpe:** 1.71
- **Fitness:** 1.41
- **Turnover:** ~18%

## The Core Formula
```fastexpr
ts_decay_linear(rank(-ts_corr(est_ptp, est_fcf, 20)), 5)
```

## Logic & Hypothesis
- `est_ptp`: Estimated Price Target
- `est_fcf`: Estimated Free Cash Flow
- **Hypothesis:** When analysts' price targets and free cash flow estimates move in tandem (high positive correlation), the stock is fully "priced in" by the market. There is little room for upward surprises, making the stock prone to being overpriced. Thus, we short these highly correlated stocks (hence the negative sign `-ts_corr`).
- **Lookback (20 days):** A short lookback period of 1 month (20 days) ensures the model reacts quickly to the *current* cycle of analyst revisions, maximizing the Sharpe ratio.
- **Normalization (rank):** `rank` is used across the entire TOP3000 universe to evenly distribute capital, bypassing the `CONCENTRATED_WEIGHT` API error that often plagues group-based rankings (`group_rank`) on alternative data.
- **Smoothing (ts_decay_linear 5):** The 5-day decay smooths out day-to-day noise, drastically improving the Fitness score by lowering turnover.

## Key Takeaways
- This alpha successfully broke a massive self-correlation block (>0.9) caused by previous price momentum alphas. 
- It proves that moving from Price/Volume data to Alternative Data (Analyst Estimates) is the ultimate solution to passing the 0.7 self-correlation threshold.
