# Alpha 3qpd8ee6: Kakushadze Microstructure x IV Skew (Phase 12 Spectacular)

## Meta Data
- **Alpha ID:** 3qpd8ee6
- **Status:** SPECTACULAR
- **Author/Phase:** Phase 12

## Performance Metrics
- **Sharpe Ratio:** 2.52
- **Fitness:** 3.31
- **Turnover:** 11.77%
- **Max Return Correlation:** 0.3774 (vs Jjv1g3xO)

## The Signal
```fastexpr
-(ts_decay_linear(ts_corr(returns, volume, 20) * group_zscore(ts_backfill(implied_volatility_put_20 - implied_volatility_call_20, 20), subindustry), 80))
```

## Idea & Mechanics
- **Component 1 (Price-Volume Dynamics):** `ts_corr(returns, volume, 20)` measures the short-term correlation between returns and volume, inspired by Kakushadze's Alpha 6. By using `returns` instead of `close`, the signal reacts quicker and sheds long-term cyclicality.
- **Component 2 (IV Skew):** `group_zscore(ts_backfill(implied_volatility_put_20 - implied_volatility_call_20, 20), subindustry)` captures the short-term volatility bias between puts and calls, representing smart-money options flow.
- **The Magic:** Instead of using deep, non-linear wrappers (`group_rank`, `ts_zscore` applied to the final signal) which destroy the distribution, we *mutated the core*. By multiplying these two wildly different domains (options market vs equity microstructure) over a tight 20-day reactive window, and then smoothing it out with an 80-day linear decay, we achieved incredible Sharpe and Fitness while keeping turnover strictly under control and remaining statistically uncorrelated with all past alphas.
