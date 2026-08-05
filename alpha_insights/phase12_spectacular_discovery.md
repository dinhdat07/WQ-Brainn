# Phase 12: High Uniqueness & Low Turnover via IV x Kakushadze Microstructure

## The Problem
In Phase 11, we achieved SPECTACULAR Sharpe (2.55) by mixing Analyst Revisions with Mean Reversion, but Turnover was relatively high (19.47%, hovering close to the 20-30% danger zone). Furthermore, uniqueness was acceptable but trending higher (Correlation ~0.62). 
For Phase 12, the goal was to aggressively lower Turnover (< 15%) while maintaining a SPECTACULAR Sharpe (> 2.50) and pushing Return Correlation far below the 0.70 threshold.

## The Strategy: IV x Kakushadze 101
To guarantee orthogonality (Uniqueness) and low turnover, we merged two completely different realms: 
1. **Kakushadze's 101 Alphas**: Microstructure Price-Volume formulations (Alpha 6, 41, 54).
2. **Implied Volatility (IV)**: Options market pricing dimensions (IV Skew, Term Structure, Volatility Risk Premium).

By multiplying these cross-domain signals together and applying a massive outer smoothing layer (`ts_decay_linear(..., 80)`), we aimed to slow down the signal drastically while preserving predictive edges.

## Failed Experiments & Insights
- **Failed Components (Batch 09)**: Framework 2 (Alpha 41 + IV Term Structure) and Framework 3 (Alpha 54 + VRP) failed miserably, generating Sharpe ratios around 0.44 to 0.57. These components were either too noisy or fundamentally mismatched when multiplied.
- **The Golden Wrapper Failure (Batch 10)**: Framework 1 (Alpha 6 + IV Skew) yielded a solid base Sharpe of 1.71. We attempted to push it > 2.50 by applying the "Golden Wrapper" (`ts_zscore`, `group_rank` nested inside the decay). This **destroyed** the alpha, plunging Sharpe to -0.08. 
  - *Insight*: Applying deep non-linear rank/zscore transformations over a signal that is already smoothed/mixed can cause the output distribution to flatten entirely, losing all directional predictive power.

## The Breakthrough: Core Mutation
Instead of wrapping the final signal in more transformations, we tuned the "engine" inside the 80-day decay wrapper (Batch 11 & 12):
1. **Returns over Close**: We replaced `close` with `returns` in the `ts_corr` function. Time-series correlation on raw price tends to just measure long-term trending (cyclicality), whereas correlation on returns captures truer short-term dynamics. (This single change boosted Sharpe from 1.71 to 2.26).
2. **Reactivity Injection**: We shortened the lookback window of both the Price-Volume correlation and the IV Skew from 60 days down to **20 days**. This allowed the inner signal to react sharply to recent options flow, while the outer 80-day decay ensured the final turnover remained low.

## The Winning Alpha (3qpd8ee6)
- **Formula**: `-(ts_decay_linear(ts_corr(returns, volume, 20) * group_zscore(ts_backfill(implied_volatility_put_20 - implied_volatility_call_20, 20), subindustry), 80))`
- **Sharpe**: 2.52 (SPECTACULAR)
- **Fitness**: 3.31 (SPECTACULAR)
- **Turnover**: 11.77%
- **Max Return Correlation**: 0.3774 (Perfectly Unique)
