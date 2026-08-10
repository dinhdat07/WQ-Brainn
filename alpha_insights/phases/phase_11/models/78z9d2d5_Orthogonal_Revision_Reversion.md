# Alpha 78z9d2d5: Mean Reversion & Analyst Revision Orthogonal Mix (Phase 11 Spectacular)

## Meta Data
- **Alpha ID:** 78z9d2d5
- **Status:** SPECTACULAR
- **Author/Phase:** Phase 11

## Performance Metrics
- **Sharpe Ratio:** 2.55
- **Fitness:** 1.88
- **Turnover:** 19.47%

## The Signal
```fastexpr
ts_decay_linear(group_zscore(-(close - open) / open, subindustry) + 3 * group_rank(ts_delta(est_fcf, 60), subindustry), 10)
```

## Idea & Mechanics
- **Component 1 (Mean Reversion):** `group_zscore(-(close - open) / open, subindustry)` acts as a classic fast-reverting intraday price momentum signal.
- **Component 2 (Analyst Revision):** `3 * group_rank(ts_delta(est_fcf, 60), subindustry)` captures fundamental momentum (changes in estimated free cash flow).
- **The Magic:** These two components are statistically orthogonal (correlation ~0.00). By aggressively weighting the low-turnover, highly-unique fundamental signal (3x) against the high-turnover mean reversion signal (1x), we preserved the massive combined Sharpe while simultaneously keeping turnover < 20% and driving Self-Correlation against past models down below 0.70.
