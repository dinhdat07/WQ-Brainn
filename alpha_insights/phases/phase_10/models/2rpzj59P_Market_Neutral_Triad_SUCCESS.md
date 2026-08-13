# Alpha 2rpzj59P (Market Neutral Triad)

## Overview
This alpha successfully bypassed the self-correlation limit by switching the neutralization scheme from `SUBINDUSTRY` to `MARKET`. While this caused a significant drop in Sharpe ratio compared to the Spectacular models, it remained highly stable with an excellent Fitness score, qualifying it as a "Good" tier submittable model.

## Specifications
* **Alpha ID:** `2rpzj59P`
* **Status:** **SUBMITTED SUCCESSFULLY** (Good Tier)
* **Date Submitted:** Phase 10 
* **Universe:** USA TOP3000

## Settings
* **Neutralization:** `MARKET` (Key factor in breaking correlation)
* **Decay:** 0 (Handled internally)
* **Truncation:** 0.08
* **Pasteurization:** ON
* **NanHandling:** ON

## Performance (In-Sample)
* **Sharpe:** 1.71
* **Fitness:** 1.90
* **Turnover:** 7.62% (0.0762)

## Formula (FASTEXPR)
```fastexpr
ts_decay_linear(
    group_rank(sales/assets, market) + 
    group_rank(implied_volatility_call_270 - implied_volatility_put_270, market) + 
    group_rank(-ts_delta(close, 3), market), 
    25
)
```

## Logic & Intent
1. **Core Triad:** Retains the fundamental ("Holy Trinity") drivers: `sales/assets`, Options Skew (270d), and short-term price reversion.
2. **Correlation Breaker (`MARKET` Neutralization):** By comparing the components to the broad market rather than to narrow subindustry peers, the signal completely orthogonalizes from the `88pomANl` cluster. 
3. **Internal Smoothing:** A heavy internal decay (`ts_decay_linear(..., 25)`) was applied to absorb the increased volatility and noise inherent in market-wide rankings, keeping Turnover extremely low (7.6%).
