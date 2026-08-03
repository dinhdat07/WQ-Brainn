# Alpha 9q7mwNed: Asset Turnover Intraday Reversion

## 1. Concept / Hypothesis
**Concept Name**: Fundamental Z-Score x Intraday Reversion
**Hypothesis**: High asset turnover companies (efficient use of assets to generate sales) that experienced intraday price drops (negative open-to-close returns) are strong candidates for a short-term reversion. By combining a slow-moving fundamental quality factor (`sales / assets`) with a fast-moving technical factor (`rank(-(close - open) / open)`), we create a high-Sharpe, high-Fitness orthogonal signal.

## 2. Formula & Code
```fastexpr
ts_decay_linear(
    group_zscore(
        (sales / assets) * rank(-(close - open) / open), 
        subindustry
    ), 
    5
)
```

## 3. Key Metrics
*   **Sharpe**: 2.0
*   **Fitness**: 1.15
*   **Turnover**: 0.3543
*   **Phase/Batch**: Phase 8, Batch 22

## 4. Why it works
The base intraday reversion signal `rank(-(close - open) / open)` is highly predictive but has excessive turnover and often low fitness. 
By multiplying it with `sales / assets` (Asset Turnover), the signal focuses its bets on companies with high operational efficiency. 
`group_zscore(..., subindustry)` ensures we are buying the most efficient companies within each subindustry that suffered a drop. 
Finally, `ts_decay_linear(..., 5)` slows down the fast intraday signal, bringing Turnover down to 35% and boosting Fitness to 1.15.
