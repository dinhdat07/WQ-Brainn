# Phase 23: The Orthogonal Breakthrough (Constraint-First Alternative Data)

## 1. Goal
Following the success of Phase 22, the goal was to build an entirely new Alpha Model based on completely unexplored data fields to circumvent the `SELF_CORRELATION` (0.70) trap. The focus was to leverage "Alternative Data" and "Idiosyncratic Risk" that WorldQuant crowd-sourced users rarely optimize perfectly.

## 2. Hypothesis & Field Selection
We analyzed the `wq_data_fields_summary.md` and explicitly avoided previously successful variables (`sales/assets`, `close - open`, Options Put/Call Ratio). Instead, we targeted:
- **Analyst Revisions Derivative (`analyst_revision_rank_derivative`)**: Tracks the momentum of analyst upgrades/downgrades and price response. When inverted (`-analyst_revision_rank_derivative`), it yields a strong positive Sharpe.
- **Growth Potential Derivative (`growth_potential_rank_derivative`)**: Measures changes in future growth expectations.
- **Volatility Risk Premium (VRP) (`implied_volatility_call_60 - historical_volatility_60`)**: The spread between what the options market expects and what historically happened. When options are overpriced (high VRP), sellers generate alpha.

## 3. Iteration Process
1. **Batch 1-4 (Raw Constraints):** Tested raw Idiosyncratic Risk, Footnote Debt Issuance, and Analyst Estimate Dispersions. Most achieved Sharpe near 0.0 or 0.3. Raw isolated anomalies were too weak.
2. **Batch 5 (Inverted Derivatives):** Found that `analyst_revision_rank_derivative` natively had a Sharpe of -0.89. Inverting it flipped the signal into a stable generator (+0.89).
3. **Batch 7 (Smoothing Analysis):** Smoothed the derivatives using `ts_mean(..., 10)`. The signal was stable (Turnover dropped to 0.008) but Sharpe didn't exceed 1.0 alone.
4. **Batch 8 (The New Triad v1):** Created a Multi-Factor Additive Ensemble combining:
   - Analyst Revisions Derivative
   - VRP (Volatility Risk Premium)
   - Fast Price Reversion (`-ts_delta(close, 5)`)
   **Result:** Sharpe jumped to **1.88** and passed Sub-Universe tests natively without dropping.
5. **Batch 9 (Decay Tuning):** Reduced the final decay smoothing from 15 to 10 to speed up reaction times.
   **Result:** Sharpe maximized at **1.96** (Fitness 1.53, Turnover 17%).

## 4. Final Submitted Expression
```fastexpr
ts_decay_linear(
    group_rank(-analyst_revision_rank_derivative, subindustry) + 
    group_rank(-ts_delta(close, 5), subindustry) + 
    group_rank(implied_volatility_call_60 - historical_volatility_60, subindustry), 
    10
)
```

### Metrics:
- **Sharpe**: 1.96
- **Fitness**: 1.53
- **Turnover**: 17.13%
- **Sub-Universe Sharpe**: 1.23 (PASS > 0.8)
- **Self-Correlation**: Evaluated against OS constraints.

## 5. Key Learnings (Added to Dictionary)
- **Volatility Risk Premium (VRP)** is an excellent orthogonal replacement for traditional Options Skew (`IV Call - IV Put`). It captures the exact premium demanded by sellers.
- **Inverted Fundamental Derivatives**: The pre-calculated model factors (e.g., `analyst_revision_rank_derivative`) are highly potent if you analyze their correlation direction and invert them properly.
- **Decay Tuning on Fast Ensembles**: When combining fast signals (like `ts_delta(close, 5)` and daily derivatives), a tight decay (`decay=10`) preserves the Sharpe ratio better than the traditional `decay=15` or `decay=20`.
