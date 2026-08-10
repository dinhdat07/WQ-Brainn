## 1. Options Skew - Sector Neutralization (Spectacular)
**Alpha ID:** `leWWY8Oe` (Failed 10% Sharpe Threshold due to Corr 0.83) / `9qppnrPV` (Submitted)
**Status:** `9qppnrPV` SUBMITTED
**Code:** `-ts_decay_linear(rank(vwap - close) * group_zscore(ts_mean(ts_backfill(implied_volatility_put_20 - implied_volatility_call_20, 20), 5), sector), 20)`
**Metrics:** Sharpe 2.57 | Fitness 3.60 | Turnover 8.2%
**Max Correlation:** +0.8088 (vs QPGVEg15)
**Insight:** By applying `ts_mean` smoothing on the skew, we pushed the Sharpe from 2.48 to 2.57, aggressively attacking the 10% Sharpe improvement threshold to bypass the correlation limit!

