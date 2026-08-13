# Model QPGVPzb5: Phase16_Quad_D30
- **Status:** REJECTED
- **Rejection Reason:** SELF_CORRELATION (0.7816 > 0.70)

## Metrics
- **Sharpe:** 2.21
- **Fitness:** 1.76
- **Turnover:** 0.1432

## Formula
`ts_decay_linear(group_rank(trade_when(ts_backfill(pcr_oi_270, 60) < 1, (ts_backfill(implied_volatility_call_270, 60) - ts_backfill(implied_volatility_put_270, 60)), -1), subindustry) + (group_rank(ts_zscore(ts_backfill(capex, 60) / (assets+1), 250), subindustry) + group_rank(ts_zscore(est_sales, 250), subindustry)) + group_zscore(ts_zscore(est_ptp / close, 252), subindustry) + group_rank(ts_delta(est_ebit, 60) / (abs(est_ebit) + 1), subindustry) + group_rank(-(close - open) / open, subindustry), 30)`

## Analysis
Even though we pushed the Sharpe ratio to 2.21 and Fitness to 1.76 with low turnover (14.3%), mixing established strong components (Options IV skew, Intraday Reversion, Fundamental Accruals) still yields high correlation with previously submitted models (0.78 self-correlation). We must explore entirely novel alternative datasets that don't overlap with these domains to achieve true Uniqueness.
