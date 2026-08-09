<truncated 41 lines>
*   **le33nmK5** (Batch 0 - 3)
*   **zqRRVZOO** (Batch 0 - 3)

---

## 🔬 2. Alpha Structures & Design Patterns

### The "Golden Wrapper" (Use with Caution)
```fastexpr
ts_decay_linear(ts_zscore(ts_decay_linear( [CORE_SIGNAL] , X), Y), Z)
```
*   **Why it works**: It standardizes the signal, smooths out noise, and strongly boosts Sharpe/Fitness.
*   **The Problem**: Applying this wrapper to *everything* forces all alphas to behave similarly, causing `>0.90` self-correlation. 
*   **Solution**: Only use this wrapper on highly distinct, uncorrelated Core Signals (e.g. Fundamental vs. Price vs. Sentiment).

### The Intraday Reversion Trigger
```fastexpr
-(close/open - 1)
```
*   **Concept**: Replaces standard momentum triggers `ts_delta(close, 3)`. It breaks correlation with end-of-day momentum strategies while retaining predictive power.

---

## 🚫 3. Failed Experiments (What NOT to do)

| Experiment | Issue / Result | Insight |
| :--- | :--- | :--- |
| **`ts_min`** | API Error | `ts_min` is not supported on the Brain API in FASTEXPR. Use `ts_rank` or other normalizations instead. |
| **Nested Z-Scores on Everything** | Self-Correlation > 0.90 | Non-linear transformations smooth out the signal so much that distinct inputs converge to the same output distribution. |
| **Additive & Conditional Models** (`rank(A) + rank(B)`) | Low Sharpe (< 1.0) | Tried in Batch 0 - 4. The raw signal without z-score/decay smoothing isn't robust enough to generate strong return predictability. |
| **Z-score on Non-Price Fields** | API Error / NaNs | `ts_zscore` on certain sparse fundamental data can lead to NaNs or errors due to zero variance over the window. |

---

## 💡 4. Future Concepts & Low Correlation Ideas (To Be Tested)

1.  **Time-Series Momentum**: `rank(ts_delta(close, 21))`
2.  **Mean Reversion to VWAP**: `rank(vwap - ts_mean(vwap, 5))`
3.  **Volatility-Adjusted Fundamentals**: `rank(capital_paidup) / ts_std_dev(returns, 20)`
4.  **Regime-Timing**: Flip momentum signals based on market conditions (e.g., using broad market trend as a switch).
5.  **Sentiment**: Utilize alternative data like news sentiment if available (`rank(ts_sum(news_sentiment, 60))`).

---

## 🛑 5. The Principal Component Trap (Phase 10 Insights)

*   **The Mathematical Wall**: In the USA TOP3000 universe, combining `Fundamental Value` (e.g., `sales/assets`, `fscore_bfl_momentum`), `Options Skew` (e.g., `implied_volatility_call - put`), and `Reversion` (`-(close-open)/open` or `-ts_delta(close, 3)`) yields the absolute peak of Sharpe ratio (usually > 2.50). 
*   **The Trap**: Because this "Holy Trinity" captures the vast majority of predictive variance in the dataset, *any* variation of it (adding new F-Scores, shifting temporal decays via Mixed Decays, or swapping technical indicators) collapses back to the exact same trading positions, leading to a **PnL Self-Correlation > 0.90**.
*   **Failed Bypasses**:
    *   **Changing Neutralization**: Switching from `subindustry` to `MARKET` or `SECTOR` breaks the correlation successfully, but immediately drops the Sharpe ratio below 2.0. The `sales/assets` factor only possesses alpha when evaluated against tight subindustry peers.
    *   **F-Score Substitution**: Replacing `sales/assets` with WorldQuant's proprietary `fscore_bfl_momentum` or `fscore_bfl_quality` creates strong models (Sharpe 2.08 to 2.59), but still fails the 0.70 correlation check due to collinearity.
*   **Strategic Conclusion**: To find orthogonal "Spectacular" models, one must completely abandon the Fundamental + Options paradigm and explore entirely novel datasets (e.g., Alternative Data, Supply Chain, Sentiment, or deep Statistical Arbitrage).

### 🚀 Batch 20 - 12 (Volatility & Intraday Turnover Reduction - Phase 6)
*   **d5RaEvVj**: Intraday Reversion (`ts_decay_linear(group_zscore(-(close - open) / open, subindustry), 10)`). **Sharpe 1.75 | Fit 1.04 | TO 0.54**. **🎉 SUBMITTED SUCCESSFULLY!**. Great success. By pushing decay from 5 to 10 on a strong intraday reversion signal, turnover dropped below 0.6 while keeping Sharpe very high.

### 🚀 Batch 21 - Phase 7 (Silver Alphas)
*   **Jjv1g3xO**: Implied Volatility Spread (`ts_decay_linear(trade_when(pcr_oi_270 < 1, (implied_volatility_call_270 - implied_volatility_put_270), -1), 10)`). **Sharpe 1.89 | Fit 1.97 | TO 0.18**. Excellent first run with Options Data.
*   **pwKZnmX6**: IV Skew Decay (`ts_decay_linear(ts_backfill((implied_volatility_call_180 - implied_volatility_put_180) / implied_volatility_mean_180, 20), 10)`). **Sharpe 2.21 | Fit 1.87 | TO 0.1691**. **🎉 SUBMITTED SUCCESSFULLY!**. Incredible performance from 6-month volatility skew.
*   **58keLvV6**: Invest Future Base (`ts_regression(ts_sum(ts_backfill(fnd6_newqv1300_ivltq, 60), 252), ts_step(1), 756, rettype = 2)`). **Sharpe 1.35 | Fit 1.06 | TO 0.0071**. **🎉 SUBMITTED SUCCESSFULLY!**. Extremely low turnover long term fundamental model.

### 🚀 Batch 22 - Phase 8 (Fundamental Z-Score x Fast Reversion)
*   **9q7mwNed**: Asset Turnover Intraday Reversion (`ts_decay_linear(group_zscore((sales / assets) * rank(-(close - open) / open), subindustry), 5)`). **Sharpe 2.0 | Fit 1.15 | TO 0.3543**. Extremely strong fundamental-momentum crossover!

### 🚀 Batch 33 - Phase 9 (Institutional Triad Breakthrough - Sub-Universe Master)
*   **88pomANl**: Institutional Triad (`ts_decay_linear(group_rank(sales / assets, subindustry) + group_rank(trade_when(ts_backfill(pcr_oi_270, 60) < 1, (ts_backfill(implied_volatility_call_270, 60) - ts_backfill(implied_volatility_put_270, 60)), -1), subindustry) + group_rank(-(close - open) / open, subindustry), 10)`). **Sharpe 2.69 | Fit 2.32 | TO 0.1775 | Margin 14.8 bps | Sub-Universe Sharpe: PASS (1.26 vs 1.16)**.

### 👑 Batch 36 - Phase 10 (Quad-Factor Institutional Spectacular Tier)
*   **RRm3ZdRg**: Quad-Factor Institutional Zenith (`ts_decay_linear(group_rank(sales / assets, subindustry) + group_rank(trade_when(ts_backfill(pcr_oi_270, 60) < 1, (ts_backfill(implied_volatility_call_270, 60) - ts_backfill(implied_volatility_put_270, 60)), -1), subindustry) + group_rank(est_cashflow_op / cap, subindustry) + group_rank(-(close - open) / open, subindustry), 15)`). **Sharpe 2.62 | Fit 2.62 | TO 0.1073 | Margin 20.4 bps | Max Drawdown 4.05% | Sub-Universe Sharpe: PASS (1.32 vs 1.13) | Max Self-Corr: 0.6141 (PASS) | Status: 100% SUBMITTABLE SPECTACULAR TIER**.
*   **QPGJrOqM**: Quad-Factor D20 (`decay = 20`). **Sharpe 2.56 | Fit 2.68 | TO 0.0984 (Sub-10%) | Margin 24.7 bps | Sub-Universe Sharpe: PASS (1.17 vs 1.10) | Max Self-Corr: 0.5846 (PASS)**.
*   **VkG9Ebk0**: Quad-Factor D24 (`decay = 24`). **Sharpe 2.52 | Fit 2.71 | TO 0.0847 | Margin 28.1 bps | Sub-Universe Sharpe: PASS (1.14 vs 1.09) | Max Self-Corr: 0.5657 (PASS)**.
*   **XgorPoGl**: Quad-Factor PCR 180d D18 (`pcr_oi_180, decay = 18`). **Sharpe 2.61 | Fit 2.64 | TO 0.1086 | Margin 23.3 bps | Max Drawdown 3.88% | Sub-Universe Sharpe: PASS (1.16 vs 1.12) | Max Self-Corr: 0.6042 (PASS)**.

### 🛡️ Batch 37 - Phase 10 (Correlation Breaker - Good Tier)
*   **2rpzj59P**: Market Neutral Triad (	s_decay_linear(group_rank(sales/assets, market) + group_rank(implied_volatility_call_270 - implied_volatility_put_270, market) + group_rank(-ts_delta(close, 3), market), 25)). **Settings:** Neutralization = MARKET. **Sharpe 1.71 | Fit 1.90 | TO 0.0762 | Status: SUBMITTED SUCCESSFULLY**. Changing Neutralization to MARKET successfully decoupled the signals from the Subindustry-neutralized principal component, allowing this to pass self-correlation constraints at the cost of peak Sharpe.


### 11. Options Term-Structure Resonance
- **Definition:** The empirical phenomenon where options market signals (implied volatility skew) must be synchronized with price/volume lookback windows matching the exact expiration horizon (10-day, 20-day, 60-day).
- **Inversion Characteristic:** 10-day options skew reflects retail panic hedging and produces a negative correlation (mean-reversion), whereas 20-day options skew reflects institutional positioning and produces a positive correlation (trend continuation).
