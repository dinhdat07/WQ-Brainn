# LLGPnvP2: Bounded Asset Turnover + Options Volatility Arbitrage (Additive)

## Core Concept
This model is the masterpiece of Phase 8, solving all 3 critical quality gates simultaneously:
1. **Self-correlation (<0.7)**: Completely independent of price mean-reversion by utilizing Options Implied Volatility as the momentum driver.
2. **Instrument Count / Sparsity**: `nanHandling: ON` backfills missing options data with neutral median (0.5), allowing every stock in TOP3000 to receive a meaningful score.
3. **Weight Concentration (<10%)**: Solved by replacing raw unbounded ratios `sales / assets` with bounded `group_rank(sales / assets, subindustry)` and using an **Additive Blend** (`[0,1] + [0,1]`). No single stock can ever produce an outlier score.

## Exact Formula
```fastexpr
ts_decay_linear(group_rank(sales / assets, subindustry) + rank(implied_volatility_call_120 / parkinson_volatility_120), 5)
```

## Settings
- **Universe**: TOP3000
- **Region**: USA
- **Instrument Type**: EQUITY
- **Delay**: 1
- **Decay**: 0 (Smoothing handled manually via `ts_decay_linear(..., 5)`)
- **Neutralization**: SUBINDUSTRY
- **Truncation**: 0.03 (Strictly limits any single instrument to max 3% weight)
- **Pasteurization**: ON
- **NaN Handling**: ON

## Performance Metrics (In-Sample)
- **Sharpe**: 1.59
- **Fitness**: 1.37
- **Turnover**: 0.1339 (13.39%)
- **Margin**: 0.001473 (14.7 bps)
- **Returns**: High and remarkably steady

## Why it works
- **Component 1 - Fundamental Rank**: `group_rank(sales / assets, subindustry)` ranks companies within their own subindustry by asset efficiency, uniformly distributed in `[0, 1]`.
- **Component 2 - Options Sentiment Rank**: `rank(implied_volatility_call_120 / parkinson_volatility_120)` ranks companies by call option speculation premium, uniformly distributed in `[0, 1]`.
- **Additive Synergy**: The sum ranges strictly between `[0, 2]`. A stock with top fundamentals and top option speculation gets `1.0 + 1.0 = 2.0`. A stock with missing options data gets `group_rank + 0.5`. 
- **Zero Heavy Tails**: Because both inputs are bounded ranks, the variance of the combined signal is completely controlled, making extreme weight spikes mathematical impossibilities.
