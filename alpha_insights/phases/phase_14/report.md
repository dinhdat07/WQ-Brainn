# Phase 14: The 101 Alphas Extraction & The Implied Volatility Skew Discovery

## 1. Context & Objectives
- **Goal:** Phase 14 was initiated to break into the elusive "SPECTACULAR" tier (Sharpe > 2.0). 
- **Methodology:** We tapped into the seminal paper "101 Formulaic Alphas" by Zura Kakushadze. The plan was to extract non-linear patterns, adapt them to the WorldQuant FastExpr API, and overlay them with premium institutional datasets like Options Implied Volatility.

## 2. Experimental Journey
During Phase 14, we built an extraction and conversion pipeline to translate theoretical alphas into the WorldQuant execution environment.

### A. The 101 Alphas Transpilation
We reviewed several of the 101 alphas, specifically targeting those that used combinations of:
- Intraday price action (`close - open`, `vwap - close`)
- High-frequency mean reversion indicators
- Cross-sectional operations (`group_rank`, `group_zscore`)

Many pure price/volume formulations from the paper resulted in Average (Sharpe ~1.2) or Good (Sharpe ~1.5) models due to market adaptation over the years. To push the boundary to Spectacular, we needed an informational edge that wasn't widely available when the paper was published.

### B. The Integration of Options Skew
We decided to replace traditional volume/price momentum factors in the Kakushadze formulas with **Options Implied Volatility (IV)** data.
Specifically, we engineered the **IV Skew** metric:
`implied_volatility_put_20 - implied_volatility_call_20`

When Put IV is significantly higher than Call IV, it indicates extreme institutional fear (or hedging demand) for downside protection. We normalized this fear metric across peers using `group_zscore(..., subindustry)`.

## 3. The "Double Mean Reversion" Discovery (QPGVEg15)
We crossed the Kakushadze microstructure crash factor (`rank(vwap - close)`) with our proprietary Options IV Skew.

- **The Setup:** Multiply `rank(vwap - close)` (Intraday bleeding) by the IV Skew (Institutional fear).
- **The Finding:** When simulating this combination, we received a massive negative Sharpe ratio (-2.13). This meant the logic was structurally sound but directionally opposite. When both the equity market (VWAP > Close) and the options market (Puts > Calls) flash extreme panic, the asset is actually deeply oversold and poised for a violent mean reversion upward.
- **The Inversion:** We inverted the signal by placing a negative sign in front of the decay block:
  `-ts_decay_linear(rank(vwap - close) * group_zscore(ts_backfill(implied_volatility_put_20 - implied_volatility_call_20, 20), subindustry), 20)`

## 4. Final Results & Alpha Extraction
By tuning the `ts_decay_linear` window to 20 days (allowing the slower options market sentiment to fully price in), the inverted model achieved incredible performance metrics:
- **Alpha ID:** `QPGVEg15`
- **Sharpe Ratio:** 2.35 (Spectacular)
- **Fitness:** 2.31
- **Turnover:** 11.1%
- **Correlation:** Safely below 0.70 against prior active portfolio (0.6179 max).

Phase 14 concluded with a massive triumph, yielding 3 Average/Good models and 1 Spectacular model (`QPGVEg15`), successfully propelling the account's overall performance tier and setting up the grueling Correlation/Uniqueness battles of Phase 15.
