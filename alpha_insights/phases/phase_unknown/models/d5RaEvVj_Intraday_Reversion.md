# Successful Model: d5RaEvVj (Intraday_Reversion)
- **Phase**: 6
- **Expression**: `ts_decay_linear(group_zscore(-(close - open) / open, subindustry), 10)`
- **Stats**: Sharpe: 1.75 | Fit: 1.04 | TO: 0.54

## Description
A price/volume anomaly model capturing intraday mean reversion. If a stock rises from open to close, it is predicted to revert downwards. A 10-day decay is used to lower turnover.
