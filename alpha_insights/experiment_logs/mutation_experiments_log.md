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

---

## Batch 11 - 3: Alternative Data Exploration (Phase 3)

**Goal:** Apply 101-Alpha structures (Alpha#42, Alpha#6) to Alternative Data (Analyst, Sentiment) and fix `GreGv8oQ` (Vol Arb) concentrated weight.

| Model | Core Signal | Wrapper/Modifiers | Result (Sharpe / Fitness / Turnover) | Insight / Next Step |
| :--- | :--- | :--- | :--- | :--- |
| **1_Analyst_vs_Price** | `rank(est_ptp - close) / rank(est_ptp + close)` | `ts_decay_linear(..., 5)` on TOP3000 | **0.62 / 1.02** | LOW_SHARPE. The static spread between price target and close lacks predictive power. Needs a dynamic element (e.g., `ts_delta(est_ptp)`). |
| **2_Sentiment_Corr** | `-ts_corr(open, ts_backfill(composite_sentiment_score_2, 10), 10)` | `ts_decay_linear(rank(...), 5)` | **ERROR** | API Error: `ts_backfill` does not support event inputs. Must use `ts_sum` or `ts_mean` to convert event to matrix. |
| **3_Flat_Vol_Arb** | `ts_backfill(implied_volatility_call_120, 60) / parkinson_volatility_120` | `ts_decay_linear(rank(...), 5)` on TOP3000 | **0.83 / 1.47** | LOW_SHARPE. Flattening the rank to TOP3000 destroyed the Sharpe from the original `group_rank(..., sector)` (which had 1.32). Sector-neutrality is strictly required for this signal. We must return to `group_rank` but use `truncation: 0.05` to fix CONCENTRATED_WEIGHT. |

### Result: Fail. All 3 models did not pass. Proceeding to Batch 12 to iterate on the findings.

### Next Action
- **Submit/Test `88eebrYo`:** Check self-correlation of `88eebrYo` against `ZYKo6R78` on the Brain platform.
- **Explore Alternative Triggers:** Next time, test `ts_zscore(-returns, 5)` or `ts_rank(volume, 5)` as orthogonal triggers.

## Batch 12 - 3: Alternative Data Exploration (Phase 3) - Iteration 2

**Goal:** Fix the issues encountered in Batch 11. Specifically, add dynamic element to Analyst Delta, use truncation + sector neutrality for Vol Arb, and use `ts_mean` for Sentiment.

| Model | Core Signal | Wrapper/Modifiers | Result (Sharpe / Fitness / Turnover) | Insight / Next Step |
| :--- | :--- | :--- | :--- | :--- |
| **1_Analyst_Delta** | `rank(ts_delta(est_ptp, 5))` | `ts_decay_linear(..., 5)` on TOP3000 | **0.77 / 1.31** | LOW_SHARPE. Better than `est_ptp - close` (0.62), but still lacks predictive power. |
| **2_Options_Vol_Truncated** | `group_rank(ts_backfill(implied_volatility_call_120, 60) / parkinson_volatility_120, sector)` | `ts_decay_linear(..., 5)` with Truncation 0.05 on TOP3000 | **0.83 / 1.47** | LOW_SHARPE. Surprisingly, this scored exactly the same as the flattened version (0.83). The `group_rank` did not restore the 1.32 Sharpe. This implies the base signal's efficacy has dropped or the specific settings (TOP3000 vs USA) changed. |
| **3_Sentiment_Event** | `-ts_corr(open, ts_mean(composite_sentiment_score_2, 10), 10)` | `ts_decay_linear(rank(...), 5)` | **ERROR** | API Error: `ts_mean` does not support event inputs. We cannot use `ts_*` functions on event data directly. We must use event-specific functions or avoid time-series ops on them. |

### Result: Fail. All 3 models did not pass. Proceeding to Batch 13.

## Batch 13 - 10: Alternative Data Exploration (Phase 3) - Iteration 3

**Goal:** Test 10 new formulas using Alternative Data (Analyst estimates, Options implied volatility, Sentiment, Fundamentals) to find a high-Sharpe signal without self-correlation. Apply dynamic elements (`ts_delta`, `ts_decay_linear`) to alternative metrics.

| Model | Core Signal | Result (Sharpe / Fitness) | Insight / Next Step |
| :--- | :--- | :--- | :--- |
| **1_Analyst_Revisions** | `anl4_fs_basic_splt_v4_nd_eps_estimate - close` | **ERROR** | API Error: `subtract` does not support event inputs. Cannot subtract `close` (matrix) from `anl4` (event) directly. |
| **2_Options_Volatility** | `ts_backfill(implied_volatility_call_120, 60) / parkinson_volatility_120` | **0.83 / 1.47** | LOW_SHARPE. |
| **3_Sentiment_Divergence** | `-ts_corr(open, ts_backfill(composite_sentiment_score_2, 10), 10)` | **ERROR** | API Error: `ts_backfill` does not support event inputs. |
| **4_EBITDA_Reversion** | `-ts_delta(anl4_ebitda_mean, 60)` | **0.75 / 1.29** | LOW_SHARPE. |
| **5_RD_Intensity** | `fnd6_newa2v1300_rdip` | **0.78 / 1.34** | LOW_SHARPE. |
| **6_Short_Indicators_vs_Price** | `-ts_corr(best_position_indicator, close, 20)` | **ERROR** | API Error: `ts_corr` does not support event inputs. |
| **7_Earnings_Quality** | `anl4_fs_basic_splt_v4_nd_sales_estimate / close` | **ERROR** | API Error: `divide` does not support event inputs. |
| **8_Cash_Accumulation** | `ts_delta(cash_st, 60)` | **0.79 / 1.36** | LOW_SHARPE. |
| **9_Analyst_Holds_Ratio** | `-anl4_hold` | **ERROR** | API Error: `multiply` does not support event inputs (from negative sign). |
| **10_Target_Price_Acceleration** | `ts_delta(est_ptp, 5)` | **0.77 / 1.31** | LOW_SHARPE. |

### Result: Fail.
All 10 models did not pass (either ERROR due to event-input constraints or LOW_SHARPE).

### Next Action:
The `anl4`, `composite_sentiment_score`, and `best_position_indicator` datasets are event-based. We cannot apply standard math or time-series operators directly on them unless we cast them to vectors (e.g., using `vec_avg`) or use specialized event operators. We need to revise the formulas to either use matrix datasets or handle event data properly.

## Batch 14 - 10: Matrix Alternative Data (Phase 3) - Iteration 4

**Goal:** Test 10 new models using Matrix versions of Alternative Data (e.g., `mean_composite_sentiment_score`, `anl4_afv4_eps_mean`, `est_ptp`) to avoid the event-data errors from Batch 13, and assess their baseline predictive power.

| Model | Core Signal | Result (Sharpe / Fitness) | Insight / Next Step |
| :--- | :--- | :--- | :--- |
| **1_Options_Vol_Arb_Pure** | `group_rank(implied_volatility_call_120 / parkinson_volatility_120, sector)` | **0.84 / 1.15** | (ID: `N1RbNOVe`) LOW_SHARPE. |
| **2_Options_Vol_Spread** | `ts_decay_linear(rank(implied_volatility_call_120 - implied_volatility_put_120), 5)` | **0.79 / 1.28** | (ID: `kqZPNJZg`) LOW_SHARPE. |
| **3_Sentiment_Momentum** | `ts_decay_linear(rank(ts_delta(mean_composite_sentiment_score, 10)), 5)` | **0.81 / 0.77** | (ID: `mLV5oWa1`) LOW_SHARPE. |
| **4_Sentiment_Reversal** | `ts_decay_linear(rank(-ts_corr(open, mean_composite_sentiment_score, 10)), 5)` | **0.78 / 1.30** | (ID: `2rNp5knN`) LOW_SHARPE. |
| **5_Target_Price_Premium** | `ts_decay_linear(rank(est_ptp / close), 5)` | **0.90 / 1.62** | (ID: `JjvG8paW`) **HIGHEST IN BATCH**. Target price vs current price divergence shows promise. |
| **6_Target_Price_Revision** | `ts_decay_linear(rank(ts_delta(est_ptp, 20)), 5)` | **0.80 / 1.38** | (ID: `2rNp59kN`) LOW_SHARPE. |
| **7_EPS_Revision** | `ts_decay_linear(rank(ts_delta(anl4_afv4_eps_mean, 20)), 5)` | **0.80 / 1.37** | (ID: `np8Najxx`) LOW_SHARPE. |
| **8_Normalized_EPS_Revision** | `ts_decay_linear(rank(ts_delta(anl4_afv4_eps_mean / close, 10)), 5)` | **0.79 / 1.38** | (ID: `88epGA77`) LOW_SHARPE. |
| **9_Options_PutCall_Volume** | `ts_decay_linear(rank(pcr_vol_10), 5)` | **0.78 / 1.05** | (ID: `qM6N5g5O`) LOW_SHARPE. |
| **10_EPS_vs_Price_Divergence**| `ts_decay_linear(rank(-ts_corr(close, anl4_afv4_eps_mean, 20)), 5)` | **0.80 / 1.30** | (ID: `O0xG66X7`) LOW_SHARPE. |

### Result: Matrix Conversion Successful. Base signals need more smoothing/normalization.
All 10 models simulated successfully (no syntax errors). The shift to `Matrix` alternative data (like `mean_composite_sentiment_score` and `anl4_afv4_eps_mean`) bypassed the Event limitations. 
However, Sharpe ratios hovered around 0.80 - 0.90. The most promising base signal is **Target Price Premium** (`est_ptp / close`), which scored 0.90. 

### Next Action:
In Batch 15, we will take the best concepts (`est_ptp / close` and Options Volatility Arbitrage) and apply advanced statistical scaling (e.g., `ts_zscore`, `group_rank` with different neutralization), aiming to push Sharpe from ~0.90 to >1.25.

## Batch 15 - 10: Matrix Signal Optimization (Phase 3) - Iteration 5

**Goal:** Push the Sharpe ratio of our two best Alternative Data matrix signals (`est_ptp / close` and `implied_volatility_call_120 / parkinson_volatility_120`) above 1.25 using combinations of `ts_zscore`, `group_rank`, `group_zscore`, and various lookback windows (63, 126, 252).

| Model | Core Signal | Result (Sharpe / Fitness) | Insight / Next Step |
| :--- | :--- | :--- | :--- |
| **1_Target_Price_ZScore_63_Sector** | `ts_decay_linear(group_rank(ts_zscore(est_ptp / close, 63), sector), 5)` | **0.85 / 1.53** | LOW_SHARPE. |
| **2_Target_Price_ZScore_126_Ind** | `ts_decay_linear(group_rank(ts_zscore(est_ptp / close, 126), industry), 5)` | **0.83 / 1.48** | LOW_SHARPE. |
| **3_Target_Price_ZScore_252_SubInd**| `ts_decay_linear(group_zscore(ts_zscore(est_ptp / close, 252), subindustry), 5)` | **1.58 / 1.18** | (ID: `e7x3P7gO`) **🔥 MASSIVE SUCCESS!** Passed all thresholds. |
| **4_Target_Price_ZScore_63_NeutInd**| `ts_decay_linear(rank(ts_zscore(est_ptp / close, 63)), 5)` (Neut: Industry) | **ERROR** | Neutralization `Industry` is invalid in FASTEXPR. Use `INDUSTRY`. |
| **5_Target_Price_ZScore_126_NeutMkt**| `ts_decay_linear(rank(ts_zscore(est_ptp / close, 126)), 5)` (Neut: Market) | **ERROR** | Neutralization `Market` is invalid. Use `MARKET`. |
| **6_OptVol_ZScore_63_Sector** | `ts_decay_linear(group_rank(ts_zscore(implied_volatility_call_120 / parkinson_volatility_120, 63), sector), 5)` | **0.79 / 1.37** | LOW_SHARPE. |
| **7_OptVol_ZScore_126_Industry** | `ts_decay_linear(group_rank(ts_zscore(implied_volatility_call_120 / parkinson_volatility_120, 126), industry), 5)` | **0.77 / 1.33** | LOW_SHARPE. |
| **8_OptVol_ZScore_63_SubInd** | `ts_decay_linear(group_zscore(ts_zscore(implied_volatility_call_120 / parkinson_volatility_120, 63), subindustry), 5)` | **1.19 / 0.52** | ALMOST PASSED. `group_zscore` + `subindustry` is a very strong operator. |
| **9 & 10 (OptVol Neut)** | rank + Neutralization | **ERROR** | Invalid Neutralization string casing. |

### Result: 1 Massive Success (ID: `e7x3P7gO`).
We successfully pushed the `est_ptp / close` concept to a Sharpe of 1.58 and Fitness 1.18 by applying a double z-score (`group_zscore(..., subindustry)` on top of `ts_zscore(..., 252)`). This strongly normalizes the analyst target price premium against peers in the same subindustry over a 1-year window.

### Next Action:
Since `e7x3P7gO` is built entirely on Alternative Data (Analyst estimates) and normalized differently, it is extremely likely to have `< 0.7` self-correlation with our previous Volatility/Fundamentals base models (like `ZYKo6R78`). 
We need to run a correlation check and submit `e7x3P7gO`.

## Batch 16 - 10: Orthogonal Liquidity & Accruals (Phase 4) - Base Cores

**Goal:** Find new uncorrelated Base Cores using Liquidity anomalies (Amihud, Volume Surprise) and Advanced Fundamentals (Accruals, Working Capital, PEG) to achieve Sharpe > 1.25.

| Model | Core Signal | Result (Sharpe / Fitness) | Insight / Next Step |
| :--- | :--- | :--- | :--- |
| **16_1_Amihud_Illiquidity** | `ts_decay_linear(group_rank(ts_mean(abs(returns) / volume, 20), sector), 5)` | **0.66 / 1.06** | LOW_SHARPE. |
| **16_2_Turnover_Value** | `ts_decay_linear(group_rank(1 / ts_mean(sharesout / volume, 20), industry), 5)` | **0.76 / 1.34** | LOW_SHARPE. High fitness due to low turnover (0.019). |
| **16_3_Volume_Surprise** | `ts_decay_linear(rank(-ts_delta(volume, 5) * sign(returns)), 5)` | **0.77 / 1.11** | LOW_SHARPE. Turnover is higher (0.17). |
| **16_4_Vol_Adj_Reversion** | `ts_decay_linear(rank(-(close / ts_mean(close, 20)) * rank(ts_delta(volume, 5))), 5)` | **0.75 / 1.06** | LOW_SHARPE. |
| **16_5_Liquidity_Trend**| `ts_decay_linear(group_rank(ts_delta(volume / sharesout, 10), sector), 5)` | **0.75 / 1.13** | LOW_SHARPE. |
| **16_6_Low_Accruals** | `ts_decay_linear(group_rank(-(assets - cash - liabilities), sector), 5)` | **0.66 / 1.10** | LOW_SHARPE. |
| **16_7_Working_Capital_Ratio**| `ts_decay_linear(group_rank(-((assets - cash) / assets), industry), 5)` | **0.67 / 1.10** | LOW_SHARPE. |
| **16_8_ROE_Quality_Rank** | `ts_decay_linear(group_zscore(ts_zscore(income / equity, 63), subindustry), 5)` | **0.58 / 0.20** | VERY LOW SHARPE & FIT. |
| **16_9_PEG_Yield** | `ts_decay_linear(group_rank((income / close) * ts_delta(income, 252), sector), 5)` | **0.81 / 1.41** | LOW_SHARPE. Highest fitness of the batch (1.41). |
| **16_10_Asset_Turnover** | `ts_decay_linear(group_rank(sales / assets, industry), 5)` | **0.83 / 1.44** | LOW_SHARPE. Highest Sharpe (0.83) and Fitness (1.44). |

### Result: 0 Successes.
None of the 10 base models achieved a Sharpe > 1.25. The Liquidity signals (16_1 - 16_5) maxed out at 0.77 Sharpe. The Advanced Fundamentals signals (16_6 - 16_10) performed slightly better in Fitness, with Asset Turnover (`16_10`) reaching Sharpe 0.83 and Fitness 1.44.

### Next Action:
According to the Decision Matrix (`wq-alpha-workflow`), LOW_SHARPE implies the signal reacts too slowly. However, for fundamental signals like Asset Turnover and PEG, the data updates infrequently (quarterly/annually). To boost Sharpe, we need to combine these slow-moving quality signals with a fast-moving price/volume signal (e.g., Short-term Mean Reversion or Volume Surprise), or heavily optimize the cross-sectional ranking (e.g. `group_zscore` with `subindustry` instead of `industry`).
In Batch 17, we will take the top 3 concepts (`16_10`, `16_9`, `16_3`) and apply `group_zscore` and shorter lookbacks.

## Batch 17 - 10: Fundamentals + Momentum Mutation (Phase 4)

**Goal:** Mutate the base fundamentals/liquidity ideas from Batch 16 by combining them with fast-moving reversion components and applying strict `group_zscore` on the `subindustry` level to push Sharpe > 1.25.

| Model | Core Signal | Result (Sharpe / Fitness) | Insight / Next Step |
| :--- | :--- | :--- | :--- |
| **17_1_Asset_Turnover_Fast_Reversion** | `ts_decay_linear(group_zscore((sales/assets) * rank(-(close/ts_mean(close, 5))), subindustry), 5)` | **1.88 / 1.22** | **MASSIVE SUCCESS!** Combined slow turnover with fast reversion. |
| **17_2_PEG_Volume_Spike** | `...` | **0.06 / 0.01** | Failed. |
| **17_3_Volume_Surprise_ZScore** | `...` | **1.06 / 0.31** | Good Sharpe but low Fitness due to high Turnover. |
| **17_4_Liquidity_Trend_Accel** | `...` | **0.04 / 0.00** | Failed. |
| **17_5_High_Accruals_Short** | `...` | **0.04 / 0.01** | Failed. |
| **17_6_Operating_CF_Price_Mom** | `...` | **-0.76 / -0.57** | Failed (Inverse relation). |
| **17_7_Asset_vs_Price_Growth** | `...` | **0.62 / 0.50** | LOW_SHARPE. |
| **17_8_Cap_Weighted_Reversion** | `...` | **1.86 / 0.77** | Excellent Sharpe but Fit < 1.0 due to high Turnover (0.77). |
| **17_9_Vol_Adj_Reversion_Sub** | `...` | **0.64 / 0.15** | LOW_SHARPE. |
| **17_10_Amihud_Spike** | `...` | **0.45 / 0.07** | LOW_SHARPE. |

### Result: 1 Massive Success (`RR1bxvea`)
The strategy of multiplying a fundamental ratio (`sales/assets`) by a fast-momentum ranking (`rank(-(close/ts_mean(close, 5)))`) worked flawlessly. 
The OS test was run on `RR1bxvea`, and it **PASSED** the Self-Correlation check with an incredibly low correlation of **0.312**. This proves it is entirely orthogonal to our previous Volatility/Analyst models!

### Phase 4 Complete!
We successfully found a low-correlation, high-performance model for Phase 4 using matrix data.
Next phase will either explore deeper into Alternative Datasets or build more variations of the "Fundamental x Momentum" blueprint!


