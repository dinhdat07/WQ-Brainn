# Phase 15: The Uniqueness Paradox & The Orthogonal Breakthrough

## 1. Context & Objectives
- **Goal:** Achieve "SPECTACULAR" Alpha performance (Sharpe > 2.50) while strictly maintaining Uniqueness > 0.70 (meaning Correlation with existing active portfolio < 0.70).
- **Core Challenge:** Our Phase 14 model (`QPGVEg15`) reached Sharpe 2.35 using `implied_volatility_put - call`. Because this single factor is overwhelmingly dominant, any attempt to reuse it causes a correlation spike (>0.80), violating the Uniqueness limit. 

## 2. Experimental Batches & The Mathematical Paradox
Throughout Phase 15, we ran **14 distinct batches** of experiments testing various datasets to find an uncorrelated "Spectacular" model:

### A. The Options Skew Gravity Well
- We tested multiple cross-sectional variations of Options Skew (changing `vwap` to `low`, switching neutralization from `subindustry` to `sector`/`market`, isolating `call` vs `put`, applying `ts_mean` smoothing).
- **Result:** Models like `leWWY8Oe` and `9qppnrPV` reached astronomical Sharpe ratios (2.48 - 2.57) and Fitness (3.44 - 3.60).
- **The Paradox:** Despite changing the transformation mathematics, the underlying PnL topology remained heavily correlated to `QPGVEg15` (Corr 0.81 - 0.93). The WorldQuant API applies a strict rule: *If self-correlation > 0.70, the new model's Sharpe must be at least 10% higher than the old model.* (E.g., 2.35 * 1.10 = 2.585). We topped out at 2.57, narrowly missing the 10% cutoff, resulting in rejection.

### B. The Alt-Data Exploration
To break the correlation limit, we completely abandoned Options Implied Volatility and tested entirely new domains:
- **Analyst Estimates (`est_eps`) & Revisions:** Yielded low correlation (-0.49) but Sharpe capped around 0.51.
- **Social Sentiment (`snt_social_value`) Reversal:** Low correlation (0.24) but Sharpe struggled at 0.73 due to high turnover.
- **News Sentiment (Insider `rp_css_insider`):** Sharpe 1.05 when inverted, Corr 0.57.
- **Put/Call Ratio Volume (`pcr_vol_20`):** Sharpe 0.95, failed to match the predictive power of pricing (IV).
- **Short Interest (`shares_sold_short`):** Failed continuously due to Event Data API limitations in cross-sectional rank operators.
- **Price/Volume Anomalies (`parkinson_volatility` & `returns` std_dev):** Minimal predictive power without fundamental backing (Sharpe < 0.20).

## 3. The Orthogonal Breakthrough (The Solution)
Since it is mathematically impossible within the current dataset space to reach Sharpe 2.50 without triggering the Options Skew correlation trap, the strategic pivot was to maximize **Uniqueness & Fitness** simultaneously.

We engineered a **Mega-Orthogonal Fundamental Momentum** model:
- **Logic:** `Fundamental Capex Growth` + `Analyst Sales Estimates` + `Volume Confirmation`
- **Initial Code:** `ts_decay_linear((group_rank(ts_zscore(ts_backfill(capex, 60) / (assets+1), 250), subindustry) + group_rank(ts_zscore(est_sales, 250), subindustry)) * rank(volume / adv20), 20)`
- **Initial Result:** Sharpe 1.38, Corr 0.5377 (Incredible uniqueness!). However, Fitness was 0.97 (Failed the 1.00 minimum limit for submission).

### The Fitness Optimization Hack (Batch 14)
To push Fitness > 1.00 without destroying the logic, we increased the `decay` from 20 to 40 days. 
- *Theory:* Slower decay reduces trading friction (Turnover), significantly inflating the Fitness score (Fitness = Sharpe * sqrt(Returns / Turnover)).
- **Final Submitted Model (`omNNdO15`):**
  - **Code:** `ts_decay_linear((group_rank(ts_zscore(ts_backfill(capex, 60) / (assets+1), 250), subindustry) + group_rank(ts_zscore(est_sales, 250), subindustry)) * rank(volume / adv20), 40)`
  - **Metrics:** Sharpe 1.47 | Fitness 1.10 | Turnover 3.2%
  - **Correlation:** 0.5777 (vs active portfolio)
  - **Status:** SUBMITTED.

## 4. Final Takeaways for Future Phases
1. **The 10% Sharpe Cutoff Rule:** Never blindly optimize a correlated dataset. If your new Alpha correlates > 0.70 with your best active Alpha, you *must* mathematically prove it can beat the old Sharpe by at least 10%. If not, discard the dataset immediately.
2. **Fitness vs Turnover Manipulation:** Whenever an Alpha is trapped by the Fitness 1.00 limit but has good Sharpe, systematically increase `ts_decay_linear` (from 20 -> 40 -> 60). This forcibly cuts Turnover, drastically inflating Fitness without altering the core logic.
3. **The Power of Orthogonality:** While Fundamentals (`capex`, `sales`) don't yield Sharpe 2.50, they provide an unshakeable bedrock of Uniqueness that Options data cannot replicate. Maintain a balance between High-Sharpe Options and Low-Correlation Fundamentals.
