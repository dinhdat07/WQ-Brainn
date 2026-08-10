# 6Xpn9V2L: Asset Turnover + Backfilled Volatility Arbitrage

## Overview
- **Phase**: Phase 8 Finale
- **Model ID**: `6Xpn9V2L`
- **Concept**: Bounded Asset Turnover combined with 60-day Backfilled Options Implied Volatility to Parkinson Volatility ratio.
- **Key Breakthrough**: Solved the `10.53% on 1/25/2022` data gap outlier by applying `ts_backfill(..., 60)` to both implied and realized volatility terms.

## Formula
```fastexpr
ts_decay_linear(group_rank(sales / assets, subindustry) + rank(ts_backfill(implied_volatility_call_120, 60) / ts_backfill(parkinson_volatility_120, 60)), 5)
```

## Settings
- **Universe**: TOP3000
- **Region**: USA
- **Delay**: 1
- **Neutralization**: SUBINDUSTRY
- **Truncation**: 0.05
- **Pasteurization**: ON
- **NaN Handling**: ON

## Performance Metrics
- **Sharpe**: 1.56
- **Fitness**: 1.37
- **Turnover**: 0.0946 (9.46%)
- **Margin**: 0.002029 (20.3 bps)
- **Weight Test**: PASSED (No data gap spikes)
