# 📚 WorldQuant Brain Alpha Dictionary & Insights

This dictionary tracks successful alphas, failed experiments, core structures, and research insights to systematically build stronger models.

## 🌟 1. Hall of Fame (Successful Alphas)
These alphas achieved excellent metrics (Sharpe > 1.25, Fitness > 1.0) and represent strong concepts.

### 🏆 Batch 1 - 20 (Strong Fundamentals)
*   **RR125qWg**: (Concept: TBD)
*   **LLdgKw7M**: (Concept: TBD)

### 🏆 Batch 2 - 8 (Volume/Price Dynamics)
*   **Vk3OaKmJ**
*   **pwK8RXJg**
*   **88en30Qo**
*   **P0OvZxeW**

### 🏆 Batch 3 - 24 (New Alternative Data)
*   **A17kVk5w**
*   **xAdRrqZq**
*   **JjvbPPeO**
*   **le3rM69A**

### 🌱 Batch 7 - 10 (Research-Driven Alternative Concepts)
*   **le3WZmdl**: Analyst Overpriced Stocks (Short Lookback) (`ts_decay_linear(rank(-ts_corr(est_ptp, est_fcf, 20)), 5)`). **Sharpe 1.71 | Fit 1.41**. **🎉 SUBMITTED SUCCESSFULLY! (Self-Correlation 0.0)**
*   **GreGv8oQ**: Volatility Arbitrage + Backfill (`ts_decay_linear(group_rank(ts_backfill(implied_volatility_call_120, 60) / parkinson_volatility_120, sector), 5)`). Sharpe 1.32 | Fit 1.64.

### 🔥 Batch 15 - 10 (Matrix Signal Optimization - Phase 3)
*   **e7x3P7gO**: Target Price Premium Double Z-Score (`ts_decay_linear(group_zscore(ts_zscore(est_ptp / close, 252), subindustry), 5)`). **Sharpe 1.58 | Fit 1.18**. Very strong candidate for submission due to alternative data orthogonal to price/volume momentum.

### 🚀 Batch 17 - 10 (Fundamentals + Momentum Mutation - Phase 4)
*   **RR1bxvea**: Asset Turnover + Fast Reversion (`ts_decay_linear(group_zscore((sales/assets) * rank(-(close/ts_mean(close, 5))), subindustry), 5)`). **Sharpe 1.88 | Fit 1.22 | Self-Corr: 0.312**. **🎉 SUBMITTED SUCCESSFULLY! (Massive Success)**. Mảnh ghép hoàn hảo giữa tín hiệu cơ bản (chậm) và tín hiệu động lượng (nhanh).

### 🚀 Batch 18 - 10 (Quality Fundamentals x Fast Momentum - Phase 5)
*   **88ePoPd7**: Operating Margin Reversion (`ts_decay_linear(group_zscore((sales / assets) * rank(-returns), subindustry), 5)`). **Sharpe 1.95 | Fit 1.13**. Asset Turnover with 1-day mean reversion.
*   **bldOZEjr**: Sales Yield Reversion (`ts_decay_linear(group_zscore((sales / (close * sharesout)) * rank(-ts_delta(close, 3)), subindustry), 5)`). **Sharpe 1.55 | Fit 1.35**. Price-to-Sales (inverse) with 3-day mean reversion. **🎉 SUBMITTED SUCCESSFULLY!**

### ⚠️ The Self-Correlation Trap (High Correlation Alphas)
These alphas have excellent individual stats but fail due to `> 0.9` correlation with each other.
*   **ZYKo6R78**: Submitted alpha with high fitness/Sharpe but high self-correlation.
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

### 🚀 Batch 20 - 12 (Volatility & Intraday Turnover Reduction - Phase 6)
*   **d5RaEvVj**: Intraday Reversion (`ts_decay_linear(group_zscore(-(close - open) / open, subindustry), 10)`). **Sharpe 1.75 | Fit 1.04 | TO 0.54**. **🎉 SUBMITTED SUCCESSFULLY!**. Great success. By pushing decay from 5 to 10 on a strong intraday reversion signal, turnover dropped below 0.6 while keeping Sharpe very high.

### 🚀 Batch 21 - Phase 7 (Silver Alphas)
*   **Jjv1g3xO**: Implied Volatility Spread (`ts_decay_linear(trade_when(pcr_oi_270 < 1, (implied_volatility_call_270 - implied_volatility_put_270), -1), 10)`). **Sharpe 1.89 | Fit 1.97 | TO 0.18**. Excellent first run with Options Data.
*   **pwKZnmX6**: IV Skew Decay (`ts_decay_linear(ts_backfill((implied_volatility_call_180 - implied_volatility_put_180) / implied_volatility_mean_180, 20), 10)`). **Sharpe 2.21 | Fit 1.87 | TO 0.1691**. **🎉 SUBMITTED SUCCESSFULLY!**. Incredible performance from 6-month volatility skew.
*   **58keLvV6**: Invest Future Base (`ts_regression(ts_sum(ts_backfill(fnd6_newqv1300_ivltq, 60), 252), ts_step(1), 756, rettype = 2)`). **Sharpe 1.35 | Fit 1.06 | TO 0.0071**. **🎉 SUBMITTED SUCCESSFULLY!**. Extremely low turnover long term fundamental model.
