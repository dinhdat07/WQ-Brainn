import os

# Update Mutation Log
log_path = 'E:/CODING/MMO/wq-brain/WQ-Brainn/alpha_insights/experiment_logs/mutation_experiments_log.md'
with open(log_path, 'a', encoding='utf-8') as f:
    f.write('*   **22_8_AssetTurn_RevIntra**: `ts_decay_linear(group_zscore((sales / assets) * rank(-(close - open) / open), subindustry), 5)` -> **SUCCESS** (Sharpe 2.0, Fit 1.15, TO 0.3543). Fantastic model! Asset turnover times Intraday Reversion creates strong, high fitness alpha.\n')
    f.write('*   **22_9_FCFPrice_Rev3d**: `ts_decay_linear(group_zscore(((income + depreciation - capex) / (sharesout * close)) * rank(-ts_delta(close, 3)), subindustry), 5)` -> **FAILED** (API Error: unknown variable "depreciation")\n')
    f.write('*   **22_10_GrossMargin_RevIntra**: `ts_decay_linear(group_zscore(((sales - cogs) / sales) * rank(-(close - open) / open), subindustry), 5)` -> **FAILED** (Sharpe 1.39, Fit 0.64, TO 0.4046). Fitness too low.\n')

# Create Successful Model Document
doc_path = 'E:/CODING/MMO/wq-brain/WQ-Brainn/alpha_insights/successful_models/9q7mwNed_AssetTurn_RevIntra.md'
success_md = """# Alpha 9q7mwNed: Asset Turnover Intraday Reversion

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
"""
with open(doc_path, 'w', encoding='utf-8') as f:
    f.write(success_md)
