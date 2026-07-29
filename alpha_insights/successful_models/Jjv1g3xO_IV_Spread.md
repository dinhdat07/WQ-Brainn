# Successful Model: Jjv1g3xO (IV_Spread)
- **Phase**: 7
- **Expression**: `ts_decay_linear(trade_when(pcr_oi_270 < 1, (implied_volatility_call_270 - implied_volatility_put_270), -1), 10)`
- **Stats**: Sharpe: 1.89 | Fit: 1.97 | TO: 0.18

## Description
An options data model predicting upward movement based on the spread between Call and Put Implied Volatility when Call Open Interest is lower than Put Open Interest.
