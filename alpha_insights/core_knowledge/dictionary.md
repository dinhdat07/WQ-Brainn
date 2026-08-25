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

### 💎 Phase 17 - Orthogonal Limit Pushing
*   **E5GNlbrG** (F7 God Triad): `ts_decay_linear( group_zscore(rank(ts_delta(anl4_afv4_eps_mean, 60)), subindustry) + group_zscore(rank(vwap - close), subindustry) + group_zscore(rank(ts_backfill(implied_volatility_call_270, 60) - ts_backfill(implied_volatility_put_270, 60)), subindustry), 15)`. **Sharpe 1.69 | Fit 1.19 | TO 0.1519 | Margin 9.9 bps | Max Drawdown 4.54% | Status: SUBMITTABLE GOOD TIER**. Cấu trúc này phá vỡ bức tường Orthogonality của Phase 10 bằng cách thay thế hoàn toàn bộ dữ liệu lõi (Sử dụng Analyst EPS + VWAP Divergence thay cho Fundamental Value + Intraday Reversion), đồng thời giữ nguyên cấu trúc Additive Z-Score Ensemble ưu việt.
*   **58prlYVk** (Mixed Decay Variant): `ts_decay_linear(ts_decay_linear(group_zscore(rank(ts_delta(anl4_afv4_eps_mean, 60)), subindustry), 20) + ts_decay_linear(group_zscore(rank(vwap - close), subindustry), 5) + ts_decay_linear(group_zscore(rank(ts_backfill(implied_volatility_call_270, 60) - ts_backfill(implied_volatility_put_270, 60)), subindustry), 10), 10)`. **Sharpe 1.65 | Fit 1.26 | TO 0.1021 | Margin 14.2 bps**. Tối ưu hóa Turnover xuất sắc bằng cách tách riêng từng lớp decay cho phù hợp với tần số dao động của từng nguồn dữ liệu.

### Phase 18: Alternative Data Expansion
*   **LLGr09GL** (Social Buzz Delayed Momentum): `-ts_decay_linear(group_zscore(ts_sum(mean_composite_sentiment_score, 10) - ts_sum(mean_composite_sentiment_score, 60), market), 5)`. **Sharpe 1.97 | Fit 2.37 | TO 0.0262 | Margin 138.1 bps | Max Drawdown 11.32% | Status: SUBMITTABLE SPECTACULAR TIER**. Tín hiệu đo lường gia tốc bị trễ của mạng xã hội. Việc sử dụng `market` normalization đã phá vỡ rào cản Correlation cứng đầu.
*   **O0G2W5R7** (Sentiment x Analyst Cross-Factor): `trade_when(volume > ts_mean(volume, 20), ts_decay_linear(group_neutralize(ts_delta(anl4_afv4_eps_mean, 60), sector) - group_neutralize(ts_sum(mean_composite_sentiment_score, 10) - ts_sum(mean_composite_sentiment_score, 60), sector), 5), -1)`. **Sharpe 2.13 | Fit 2.32 | Status: SUBMITTABLE GOD TIER (Sub-universe Bulletproof)**. Hợp lưu (Additive Ensemble) giữa Tăng trưởng EPS (Chuyên gia) và Gia tốc tâm lý (Đám đông). Lỗi Sub-universe Sharpe (của `market` z-score) đã được fix triệt để bằng tổ hợp `group_neutralize(..., sector)` kết hợp Liquidity Filter (`trade_when(volume > adv20)`), sinh tồn xuất sắc qua TOP200 (Sharpe 1.26).

### 🏆 Phase 20: Constraint-First Selection Protocol (Additive Ensemble Breakthrough)
*   **1Ywqp3nK** (Quad-Factor Sentinel Mutate): `ts_decay_linear(group_rank(ts_sum(mean_composite_sentiment_score, 10), subindustry) + group_rank(trade_when(ts_backfill(pcr_oi_270, 60) < 1, (ts_backfill(implied_volatility_call_270, 60) - ts_backfill(implied_volatility_put_270, 60)), -1), subindustry) + group_rank(est_cashflow_op / cap, subindustry) + group_rank(-(close - open) / open, subindustry), 15)`. **Sharpe 2.16 | Fit 2.30 | TO 0.1150 | Sub-Universe: PASS | Self-Corr: PASS | Status: SUBMITTED SUCCESSFULLY**. Giải quyết dứt điểm vấn đề Sub-Universe và Unit Error bằng cách sử dụng `group_rank` độc lập cho từng nguồn dữ liệu (Sentiment, Options, Fundamentals, Reversal) trước khi cộng tuyến tính lại. Việc đổi "Sales/Assets" bằng "Sentiment" đã giúp bẻ cong sự tương quan và giúp model lọt qua màng lọc khắt khe của hệ thống OS.

### 💎 Phase 22: Short-Term Options Skew & Pure Market Neutrality
*   **LL7WnpYe** (Market Neutral 30D Skew): `ts_decay_linear(group_zscore(ts_mean(implied_volatility_call_30 - implied_volatility_put_30, 10), market), 30)`. **Sharpe 2.70 | Fit 3.85 | TO 0.0886 | Status: SUBMITTED SUCCESSFULLY**. Sử dụng kỳ hạn 30 ngày (ngắn hạn) thay vì 270 ngày (dài hạn), kết hợp với Market Neutrality và bộ lọc nhiễu `ts_mean`, tạo ra Sharpe bùng nổ lên tới 2.70 mà vẫn lọt qua cửa ngõ Sub-Universe Sharpe.

### 🚀 Phase 23: The Orthogonal Breakthrough (VRP & Analyst Derivatives)
*   **kqjrOgql** (VRP + Analyst Derivative Triad): `ts_decay_linear(group_rank(-analyst_revision_rank_derivative, subindustry) + group_rank(-ts_delta(close, 5), subindustry) + group_rank(implied_volatility_call_60 - historical_volatility_60, subindustry), 10)`. **Sharpe 1.96 | Fit 1.53 | TO 0.1713 | Status: SUBMITTED SUCCESSFULLY**. Phát hiện ra `analyst_revision_rank_derivative` bị tương quan âm với Return (Sharpe -0.89), nên khi đảo ngược và kết hợp với Volatility Risk Premium (`implied_volatility - historical_volatility`) tạo ra một mô hình cực kỳ độc lập (orthogonal) với toàn bộ các mẫu hình cũ, né hoàn toàn bẫy Self-Correlation.

### 🤯 Phase 24: Network Graphs & Retail Social Buzz
*   **N17MvwQe** (Retail Buzz & Footnote Debt Quad-Factor - Liquidity Mask Variant): `trade_when(volume > ts_mean(volume, 20), ts_decay_linear(group_rank(fn_repayments_of_debt_a / cap, subindustry) + group_rank(-scl12_buzz, subindustry) + group_rank(implied_volatility_call_60 - historical_volatility_60, subindustry) + group_rank(-ts_delta(close, 5), subindustry), 10), -1)`. **Status: SUBMITTED SUCCESSFULLY (Self-Corr 0.69)**. Khám phá vĩ đại từ dữ liệu phụ lục báo cáo tài chính (`fn_repayments_of_debt_a / cap` đạt raw Sharpe 1.0) chứng minh dòng tiền trả nợ có ý nghĩa tích cực cực mạnh. Hợp lưu cùng Retail Buzz (đám đông FOMO/Panic) và VRP tạo nên Quad-Factor Additive hoàn toàn mới. Để bẻ gãy Self-Correlation rớt xuống dưới 0.70, mặt nạ thanh khoản `trade_when(volume > adv20)` đã được sử dụng. Rút kinh nghiệm: Việc dùng lại VRP và Mean Reversion là con dao hai lưỡi khiến correlation bị đẩy lên rất cao dù dùng data mới.

### 🌟 Phase 25: The True Orthogonal Triad (Fundamental Trend + Sentiment)
*   **O07wR2Qq** (Orthogonal Trend-Sentiment Triad): `ts_decay_linear(trade_when(volume > adv20, group_rank(ts_rank(ts_regression(sales, ts_step(1), 252, rettype=2), 60), sector) + group_rank(ts_rank(scl12_sentiment_fast_d1, 20), sector) + group_rank(ts_rank(-mean_corporate_action_sentiment, 20), sector), -1), 30)`. **Settings: Neutralization = SUBINDUSTRY**. **Sharpe 1.52 | Fit 1.05 | TO 0.0873 | Status: SUBMITTED SUCCESSFULLY (Self-Corr < 0.70)**. Nhận ra VRP và Mean Reversion làm hỏng Orthogonality ở các Phase trước, Phase này TỪ BỎ HOÀN TOÀN dữ liệu giá và options. Thay vào đó, kết hợp Fundamental Trend (Gia tốc tăng trưởng doanh thu 252 ngày) và Social/Corporate Sentiment. Phát hiện lớn nhất: Xếp hạng cục bộ (`group_rank`) theo `SECTOR` ở bên trong, nhưng Chuẩn hóa vĩ mô (`Neutralization`) theo `SUBINDUSTRY` ở bên ngoài sẽ tạo ra cấu trúc cực mạnh. Việc dùng `ts_decay_linear(..., 30)` ép Turnover xuống dưới 0.10 để đẩy Fitness vượt ngưỡng 1.0.

### 🌐 Phase 26: Competitor Network Graph & Social Sentiment
*   **0mwQwRr1** (Network Centrality & Sentiment Triad): `ts_decay_linear(group_rank(pv13_ompetitorgraphrank_hub_rank, sector) + group_rank(ts_rank(scl12_sentiment_fast_d1, 20), sector), 20)`. **Settings: Neutralization = SUBINDUSTRY**. **Sharpe 1.63 | Fit 1.11 | TO 0.1097 | Status: SUBMITTED SUCCESSFULLY (AVERAGE TIER)**. Khám phá ra một mỏ dữ liệu cực kỳ mạnh mẽ chưa từng được dùng là `pv13_ompetitorgraphrank_hub_rank` (Lý thuyết đồ thị mạng lưới đối thủ cạnh tranh). Bằng cách cộng gộp với Tâm lý mạng xã hội (`scl12_sentiment_fast_d1`) và decay 20, mô hình đạt Fitness 1.11 và Sharpe 1.63, qua mặt thành công lưới lọc Self-Correlation. Mặc dù pass submit nhưng chỉ đạt AVERAGE.

### 🌪️ Phase 27: The Quad-Core Orthogonal Zenith
*   **ZY72Ylwj** (Quad-Core Ensemble): `ts_decay_linear(group_rank(pv13_ompetitorgraphrank_hub_rank, sector) + group_rank(ts_rank(ts_regression(sales, ts_step(1), 252, rettype=2), 60), sector) + group_rank(ts_rank(scl12_sentiment_fast_d1, 20), sector) + group_rank(ts_backfill(fn_repayments_of_debt_a, 252) / cap, sector), 20)`. **Settings: Neutralization = SUBINDUSTRY**. **Sharpe 1.82 | Fit 1.55 | TO 0.0713 | Status: SUBMITTED SUCCESSFULLY (GOOD TIER)**. Khắc phục điểm yếu của Phase 26, Phase này hòa trộn 4 mỏ dữ liệu mạnh nhất từ các Phase thành công trước đây nhưng thuộc 4 nhóm (Category) hoàn toàn độc lập với nhau (Relationship, Fundamental, Sentiment, Footnotes). Việc sử dụng `group_rank` cho mỗi trụ cột độc lập và cộng gộp lại tạo ra một cấu trúc siêu bền vững, không dính dáng đến giá, giúp phá vỡ ngưỡng Sharpe 1.75 và đạt chất lượng cao.
