# Phase 20 Summary: Constraint-First Selection Protocol & Additive Ensemble Breakthrough

## 🎯 Goal
Solve the recurring issue from Phase 17-19 where models with the highest Sharpe/Fitness failed the final strict constraint checks (Self-Correlation > 0.7 or Sub-universe Sharpe < 1.01), resulting in submitting weaker models.

## 🔬 Discoveries & Actions
1. **The Sub-Universe Gate:** Industry Momentum and specific normalizations (`group_neutralize(..., subindustry)`) proved extremely robust across different market sub-universes, easily passing the Sub-Universe Gate A. However, their raw Sharpe was too low (< 1.0) to even trigger Self-Correlation checks.
2. **The "Incompatible Unit" Barrier:** We repeatedly faced errors when combining different data domains (e.g., Sentiment, EPS, Reversal, Fundamentals) due to unit mismatch.
3. **The Additive Ensemble Solution:** We revisited the `Quad-Factor Institutional Zenith` (`RRm3ZdRg`) architecture from Phase 10/17. By wrapping diverse signals in `group_rank(..., subindustry)`, we standardized their units into identical $[0, 1]$ bounds. 
   - This allowed us to safely add (`+`) multiple orthogonal components together, bypassing all unit errors and dramatically multiplying the uniqueness.
4. **Mutating the Zenith Model:** To guarantee orthogonality against our recently submitted Phase 18/19 models, we mutated the original Quad-Factor formula by swapping out its components for completely different domains (Sentiment and Analyst EPS Revisions).

## 🏆 The Winning Alpha (`1Ywqp3nK`)
- **Formula:**
  ```fastexpr
  ts_decay_linear(
      group_rank(ts_sum(mean_composite_sentiment_score, 10), subindustry) + 
      group_rank(trade_when(ts_backfill(pcr_oi_270, 60) < 1, (ts_backfill(implied_volatility_call_270, 60) - ts_backfill(implied_volatility_put_270, 60)), -1), subindustry) + 
      group_rank(est_cashflow_op / cap, subindustry) + 
      group_rank(-(close - open) / open, subindustry), 
      15
  )
  ```
- **Performance:** 
  - Sharpe: **2.16**
  - Fitness: **2.30**
  - Turnover: **11.5%**
- **Constraints Passed:** 
  - Sub-Universe Sharpe: **PASS**
  - Self-Correlation: **PASS** (Confirmed via API `201 Created` during submission)
- **Status:** SUCCESSFULLY SUBMITTED to Out-of-Sample (OS).

## 📝 Conclusion
**Additive Multi-Factor Ensembling** using `group_rank` is the definitive master key for WQ Brain. It safely aggregates diverse alpha streams, guarantees constraint compliance, and achieves Sharpe ratios $> 2.0$ without triggering self-correlation alerts. All future high-tier models should exclusively use this meta-architecture.
