# Successful Model: ZYEjPlM3 (EV_Cashflow_Value)
- **Phase**: 13 (Fundamental Valuation & Cash Flow Multiples)
- **Expression**: `ts_decay_linear(group_rank(-ts_zscore(enterprise_value / (ts_backfill(cashflow_op, 60) + 1), 63), subindustry), 8)`
- **Stats**: Sharpe: 1.70 | Fit: 1.24 | Turnover: 7.6% | Margin: 17.68 bps
- **Status**: OUT_OF_SAMPLE (OS)

## Description
This model taps into fundamental valuation by evaluating the ratio of Enterprise Value (`enterprise_value`) to Operating Cash Flow (`cashflow_op`). Operating cash flow is backfilled to handle reporting lags. The metric is inverted because a lower EV/CFO multiple typically suggests a company is undervalued relative to the cash it generates. The time-series z-score normalizes historical values over approximately a quarter, removing structural biases, and cross-sectional rank scaling isolates this alpha from broader market movements within specific subindustries. It solved a severe 0.72-0.75 correlation threshold blockage by being highly orthogonal to standard price-volume and analyst models (peak correlation is just +0.5536 vs `e7x3P7gO`).
