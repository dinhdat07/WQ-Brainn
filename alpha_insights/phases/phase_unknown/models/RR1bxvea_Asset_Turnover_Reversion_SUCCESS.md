# Successful Model: RR1bxvea (Asset_Turnover_Reversion)
- **Phase**: 4
- **Expression**: `ts_decay_linear(group_zscore((sales/assets) * rank(-(close/ts_mean(close, 5))), subindustry), 5)`
- **Stats**: Sharpe: 1.88 | Fit: 1.22 | TO: 0.63

## Description
A model combining a fundamental quality signal (Asset Turnover: sales/assets) with a fast price momentum reversal signal (5-day mean reversion). This creates a very strong Sharpe ratio by catching fundamentally strong companies during short-term pullbacks.
