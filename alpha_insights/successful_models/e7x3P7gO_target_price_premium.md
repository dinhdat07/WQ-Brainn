# Successful Model: e7x3P7gO (Target_Price_Premium)
- **Phase**: 3 (Matrix Signal Optimization)
- **Expression**: `ts_decay_linear(group_zscore(ts_zscore(est_ptp / close, 252), subindustry), 5)`
- **Stats**: Sharpe: 1.58 | Fit: 1.18

## Description
This model uses alternative data (analyst estimates) to capture the premium between the target price (`est_ptp`) and the current price (`close`). A double z-score approach is used: it normalizes the signal temporally over 1 year (`ts_zscore(..., 252)`), and then cross-sectionally normalizes it within each subindustry (`group_zscore(..., subindustry)`). This orthogonalizes the signal completely from regular price/volume momentum, ensuring low self-correlation.
