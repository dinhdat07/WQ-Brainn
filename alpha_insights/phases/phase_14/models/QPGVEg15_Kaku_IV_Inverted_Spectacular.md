# Alpha QPGVEg15: The SPECTACULAR "Kakushadze IV Hybrid Inverted" (Phase 14)

## Meta Data
- **Alpha ID:** QPGVEg15
- **Status:** ACTIVE (OS Testing)
- **Author/Phase:** Phase 14
- **Universe:** USA TOP3000
- **Delay:** 1

## Performance Metrics
- **Sharpe Ratio:** 2.35
- **Fitness:** 2.31
- **Turnover:** 11.1%
- **Max Return Correlation:** 0.6179 (vs Jjv1g3xO)

## The Signal
```fastexpr
-ts_decay_linear(
    rank(vwap - close) * 
    group_zscore(
        ts_backfill(implied_volatility_put_20 - implied_volatility_call_20, 20), 
        subindustry
    ), 
    20
)
```

## Idea & Mechanics
- **Component 1 (Microstructure Crash):** `rank(vwap - close)` captures intraday crashes. A higher rank means the stock closed significantly lower than its volume-weighted average price (VWAP) for the day.
- **Component 2 (Options Skew):** `group_zscore(ts_backfill(implied_volatility_put_20 - implied_volatility_call_20, 20), subindustry)` captures the normalized volatility skew. When positive, Puts are more expensive than Calls, indicating high market fear or bearish options flow.
- **The "Double Mean Reversion" Discovery:** When testing the direct multiplication of these two bearish indicators (Microstructure crash + Options fear), we discovered it resulted in a massively negative Sharpe (-2.13). This means when BOTH markets agree on a severe crash/fear state, the stock consistently bounces back up (Mean Reversion) over the next few weeks.
- **The Inversion:** By negating the entire formula (`-ts_decay_linear(...)`), we mathematically flip the negative Sharpe into a **+2.35 Sharpe**.
- **Decay Optimization:** We extended the `ts_decay_linear` to 20 days (from the standard 10 days used in Phase 14). This slowed down the turnover to a pristine 11.1% while allowing the slower-moving Options Implied Volatility Mean Reversion to play out fully, pushing the Sharpe to spectacular heights.
