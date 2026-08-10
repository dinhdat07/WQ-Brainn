# Intraday Reversion Layering with Rank Groupings

## Alphas
1. **JjvvA5o2** 
   - Formula: `ts_decay_linear(ts_zscore(ts_decay_linear(group_rank(ts_rank(assets, 60), subindustry) * ts_rank(-(close/open - 1), 5), 3), 30), 8)`
   - Settings: UNV: TOP3000, REGION: USA, DELAY: 1
   - Performance: Sharpe: 1.42, Fitness: 1.12, Margin: 0.0003
2. **qM66aXqZ**
   - Formula: `ts_decay_linear(ts_zscore(ts_decay_linear(group_rank(ts_rank(sales, 60), subindustry) * ts_rank(-(close/open - 1), 5), 3), 30), 8)`
   - Settings: UNV: TOP3000, REGION: USA, DELAY: 1
   - Performance: Sharpe: 1.42, Fitness: 1.11, Margin: 0.0003

## Idea & Insights
- **The Core Signal**: We started with `ZYKo6R78` which used a core of `group_rank(ts_rank(DATA, 60), subindustry)` combined with a `ts_delta(close, 3)` price trigger. However, variants using `ts_delta` were highly correlated (>0.9) with `ZYKo6R78`.
- **The Solution (Intraday Reversion)**: To break self-correlation while retaining high predictive power, we swapped the Price Trigger from `ts_delta(close, 3)` (which is a longer term momentum/reversion indicator depending on the sign) to an Intraday Reversion trigger: `-(close/open - 1)`.
- **Why Intraday Reversion works**: It captures micro-reversals within the day's session. A stock that closes significantly higher than its open often experiences a slight mean reversion on the following day (since DELAY=1). Combining this fast mean reversion with a slow fundamentals filter (like `assets` or `sales` grouped by `subindustry`) creates a powerful alpha that is distinct enough from the standard close-to-close momentum to pass self-correlation checks.
- **Fitness Improvement**: We found that increasing the final `ts_decay_linear` window (the smoothing layer at the end of the formula) from 5 to 8 (or 10) significantly improved the Fitness score (pushing it from ~0.9 to > 1.1) by reducing turnover.

## Key Learnings for Future Mutants
1. **Price Trigger Variation is Key**: When stuck with high self-correlation on a good base formula, change the Price Trigger. `(high+low)/2 - close` and `-(close/open - 1)` are excellent alternatives to `ts_delta`.
2. **Smoothing for Fitness**: If an alpha has good Sharpe but Fitness < 1.0 (or Turnover > 70%), increasing the outermost `ts_decay_linear` layer's window by a few days (e.g., from 5 to 8 or 10) often fixes the Fitness without destroying the Sharpe.
3. **Sentiment/Alternative Data Nuance**: DO NOT use `ts_zscore` blindly with Sentiment or News Alternative data. Standardizing non-price, non-continuous data often destroys the signal. These require gentler transformations (like direct `ts_rank` or no cross-sectional transformations at all).
