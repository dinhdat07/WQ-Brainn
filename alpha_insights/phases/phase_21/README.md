# Phase 21: Orthogonal Domain Pivot (Fundamental Scores)

## Goal
Escape the 0.7 Self-Correlation trap that plagued Phase 17-20 by pivoting entirely to unused orthogonal domains.

## Actions
1. **Data Field Survey:** Extracted all available WQ Brain datasets into `research-doc/wq_data_fields_summary.md`. Identified `Fundamental Scores`, `Systematic Risk`, and `Social Media Buzz` as orthogonal candidates.
2. **Batch 1 & 2 Testing:** Tested standalone orthogonal factors to gauge baseline Sharpe and Sub-universe validity.
   - `ts_decay_linear(group_rank(-unsystematic_risk_last_30_days, subindustry), 10)` -> Sharpe: 0.33, Turnover: 0.08
   - `ts_decay_linear(group_rank(ts_sum(snt_social_value, 5), subindustry), 10)` -> Sharpe: 0.31, Turnover: 0.19
   - `ts_decay_linear(group_rank(fscore_bfl_value, subindustry), 10)` -> **Sharpe: 0.87, Turnover: 0.0093. PASSES SUB-UNIVERSE SHARPE.**
   - `ts_decay_linear(group_rank(fscore_bfl_momentum, subindustry), 10)` -> Sharpe: 0.61, Turnover: 0.02
   - (*Note: Event-driven inputs like `sales_estimate_value` and `optimal_position_indicator` threw errors because `ts_backfill` and arithmetic operators don't natively support sparse event inputs.*)

3. **Batch 3 Combos:** Combined the strong, slow fundamental signal (`fscore_bfl_value`) with a fast, proven technical signal (`intraday reversal`) to boost Sharpe above the 1.25 cutoff.
   - **Idea 1 (`vRjKrolA`):** `ts_decay_linear(group_rank(fscore_bfl_value, subindustry) + group_rank(-(close - open) / open, subindustry), 10)`
     - **Sharpe: 1.95** (Massive improvement)
     - **Fitness: 1.45**
     - **Turnover: 0.2205**
     - **Drawdown: 0.0583** (Extremely low risk)
     - **Constraint Status:** Passes LOW_SHARPE, Passes LOW_SUB_UNIVERSE_SHARPE.

## Outcome: SUCCESS!
- Alpha **vRjKrolA** achieved a **Self-Correlation of 0.6644**, cleanly passing the 0.70 cutoff!
- The Alpha has been successfully **SUBMITTED** and its status is now **ACTIVE**.
- By combining a brand new fundamental data domain (`fscore_bfl_value`) with technical volume/price momentum, we broke the correlation ceiling that had blocked us in previous phases.

## Key Learnings
- **The Value of Fundamentals:** `fscore_bfl_value` is an incredibly stable signal. Its standalone turnover is < 1%, meaning it acts as a very strong "anchor" that prevents the alpha from clustering in a single Sub-Universe (which purely technical alphas often do).
- **Fast + Slow Combo:** By summing a slow anchor (`fscore_bfl_value`) with a fast trigger (`intraday reversal`), we achieve the best of both worlds: high Sharpe, sufficient turnover (~22%), and excellent Sub-Universe balance.
- **Event Inputs:** Analyst Estimates and News datasets use sparse events. Standard operators like `group_rank` and `ts_decay_linear` will fail with "Operator does not support event inputs". We must use event-specific syntax or stick to regular fields.
