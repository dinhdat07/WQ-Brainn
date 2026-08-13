## 2. Fundamental Orthogonal (Uncorrelated)
**Alpha ID:** `omNNdO15`
**Status:** SUBMITTED
**Code:** `ts_decay_linear((group_rank(ts_zscore(ts_backfill(capex, 60) / (assets+1), 250), subindustry) + group_rank(ts_zscore(est_sales, 250), subindustry)) * rank(volume / adv20), 40)`
**Metrics:** Sharpe 1.47 | Fitness 1.10 | Turnover 3.2%
**Max Correlation:** +0.5777 (vs 6Xpn9V2L)
**Insight:** By increasing `decay` from 20 to 40, we halved the turnover, boosting the Fitness from 0.97 to 1.10 (passing the 1.00 minimum threshold). This is a completely orthogonal Alpha (<0.70) that will massively boost the portfolio's Uniqueness!
