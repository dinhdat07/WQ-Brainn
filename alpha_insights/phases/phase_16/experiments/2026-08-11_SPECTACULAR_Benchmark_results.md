# Phase 16: The SPECTACULAR Benchmark (Uniqueness > 0.75)

**Goal**: Achieve a Sharpe > 2.5, Fitness > 2.8, and Uniqueness > 0.75 by moving away from strictly formulaic combinations and entering untapped data landscapes.

## Strategy Summary
We attempted to build composite ranks bridging 5 distinct domains:
1. Microstructure (Options Implied Volatility: `pcr_oi_270`)
2. Fundamental Value (Accruals: `capex/assets`)
3. Analyst Price Target Premium (`est_ptp / close`)
4. Analyst Estimates Revisions (`ts_delta(est_ebit, 60)`)
5. Fast Reversion (`-(close - open)/open`)

## Results
- **Phase16_Quad_D30 (Alpha: QPGVPzb5)**
  - Sharpe: 2.21
  - Fitness: 1.76
  - Turnover: 14.3%
  - **Result**: REJECTED due to Self-Correlation (0.78). 

## Insights
Despite mixing components across vastly different data vectors (options, fundamentals, analyst targets), they coalesce into a principal component very close to what we already submitted in Phase 10 (e.g. model `RRm3ZdRg`). We confirmed the user's initial suspicion: mixing the known `101 formulaic` logic domains continues to yield strong Sharpe but fails the Uniqueness/Self-Correlation checks. 

To achieve **SPECTACULAR** success in the next iteration, we must completely divorce our inputs from `close`, `open`, `volume`, and `est_ebit`/`sales` and dive entirely into alternative sentiment/ESG data or advanced non-linear machine learning signals.
