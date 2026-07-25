# Mutation Experiments Log

This document tracks all experimental mutations applied to successful Alpha cores to break the Self-Correlation (>0.9) barrier with `ZYKo6R78` or other overlapping alphas.

## Batch 8 - 4: Testing Outer Shell Variations

**Goal:** Modify the outer operators (the "trigger" or smoothing functions) of high-Sharpe base signals to force the new Alpha to trade on slightly different days, thereby lowering self-correlation without destroying predictive power.

**Base Core 1 (EV/CF Momentum):** `group_rank(-ts_zscore(enterprise_value/cashflow, 120), subindustry)`
**Base Core 2 (Volatility Momentum):** `rank(ts_backfill(implied_volatility_call_10, 5) / ts_backfill(parkinson_volatility_10, 5))`

### Tested Mutations

| Mutation | Description | Result for Core 1 (EV/CF) | Result for Core 2 (Vol) |
|---|---|---|---|
| **1A: Percent Return** | Replace `ts_rank` of 3-day close change with direct percentage return `(-ts_delta(close,5)/close)` | ❌ Sharpe: 0.35, Fit: 0.19 (`N1RR0www`) | ❌ Sharpe: 0.23, Fit: 0.11 (`N1RRvKgo`) |
| **1B: Medium Return** | Replace fast 3-day price momentum with medium 10-day pure return rank `ts_rank(-returns, 10)` | ✅ **Sharpe: 1.31, Fit: 1.07** (`88eebrYo`) | ❌ Sharpe: 1.02, Fit: 0.71 (`78nnE2Yv`) |
| **2: Pure Fundamental** | Remove price momentum entirely, smooth using exponential and linear moving averages | ❌ Sharpe: 0.59, Fit: 0.21 (`e7xxoOmd`) | ❌ Sharpe: -0.46, Fit: -0.17 (`pwKKA9dg`) |
| **3: Brain Neutralization** | Revert to price momentum trigger but change `Neutralization: NONE` to `INDUSTRY` | ❌ Sharpe: 1.45, Fit: 0.75 (`58kkoQLM`) | ❌ Sharpe: 1.27, Fit: 0.59 (`3qeeLZJ0`) |

### Key Insights
1. **Direct Percentage Returns are Too Noisy:** Multiplying raw percentage returns directly with fundamental ranks creates too much noise. WorldQuant favors non-linear transformations like `ts_rank` to robustify price inputs.
2. **Medium-Term Triggers (1B) work great:** Using `ts_rank(-returns, 10)` produced a SUBMITTABLE Alpha (`88eebrYo`) with 1.31 Sharpe! Because it relies on a 10-day return window instead of the 3-day `ts_delta` window used in `ZYKo6R78`, it is highly likely to pass the self-correlation test.
3. **Internal Brain Neutralization (3) destroys Fitness:** Switching to `Neutralization: INDUSTRY` keeps predictive power (Sharpe 1.45!) but drastically drops Fitness (Fit 0.75). This is likely because the internal engine's neutralization mechanism increases portfolio turnover or drops too many stocks, hurting the turnover/margin penalty of Fitness. Explicit `group_rank` is far superior.
4. **Pure Fundamental needs complex scaling:** Simply smoothing fundamental ratios (`ts_zscore` -> `ts_mean`) performs terribly (Sharpe < 0.6). Without a short-term price mean-reversion trigger, the alpha holds stale positions for too long.

### Next Action
- **Submit/Test `88eebrYo`:** Check self-correlation of `88eebrYo` against `ZYKo6R78` on the Brain platform.
- **Explore Alternative Triggers:** Next time, test `ts_zscore(-returns, 5)` or `ts_rank(volume, 5)` as orthogonal triggers.
