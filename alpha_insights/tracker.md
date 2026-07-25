# Alpha Tracker and Insights

## Successful Alphas
These are alphas that successfully passed IS and OS criteria with good Sharpe/Fitness metrics, although they might suffer from self-correlation later. 

### High Performance, High Self-Correlation (>0.9)
- **ZYKo6R78**: Submitted alpha with high fitness/Sharpe but high self-correlation.
- **le33nmK5** (Batch 3)
- **zqRRVZOO** (Batch 3)

### Promising Alphas from Batches
*Batch 8*:
- **Vk3OaKmJ**
- **pwK8RXJg**
- **88en30Qo**
- **P0OvZxeW**

*Batch 20*:
- **RR125qWg**
- **LLdgKw7M**

*Batch 24*:
- **A17kVk5w**
- **xAdRrqZq**
- **JjvbPPeO**
- **le3rM69A**

## Insights from Unsuccessful Trials
- **Nested ts_zscore and ts_decay**: Using `ts_decay(ts_zscore(ts_decay(A*B, x), y), z)` repeatedly leads to high self-correlation with previous successful models. The non-linear transformations get smoothed out and behave similarly.
- **ts_min issue**: `ts_min` is not accessible on the Brain API, leading to compilation errors. Avoid using it directly or replace it with other transformations.
- **Non-price z-scores**: `ts_zscore` on non-price fields can result in ERROR due to unsupported data types or specific checks in the Brain environment. 
- **Additive and Conditional Models (Batch 4)**: Attempted to break correlation by using `rank(A) + rank(B)` and `if > threshold then A else 0`. These successfully ran but resulted in poor Sharpe ratios (< 1.0). The signal wasn't robust enough to generate return predictability on its own without the nested z-score momentum structure.

## Low Correlation Strategies to Explore (From Deep Research)
1. **Time-Series Momentum**: `rank(ts_delta(close, 21))`
2. **Mean Reversion to VWAP**: `rank(vwap - ts_mean(vwap, 5))`
3. **Volatility-Based**: `rank(ts_stddev(close, 10))`
4. **Fundamental Valuation**: `rank(capital_paidup / revenue)` (Requires proper field names)
5. **Regime-Timing**: Flip momentum based on VIX or market conditions.
6. **Sentiment**: `rank(ts_sum(news_sentiment, 60))`
