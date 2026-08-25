# Phase 22 Summary: Data-Field-First Exploration (Orthogonal Search)

## Mục tiêu
Loại bỏ hoàn toàn các anchor/formulas cũ đã được submit ở các Phase trước. Tìm kiếm Data Field chưa từng xuất hiện trên WQ Brain để tránh bẫy Self-Correlation.

## Các nhánh đã khám phá:
1. **Analyst Estimates & Fundamentals (Batch 1,2,3)**:
   - Các trường như `est_eps`, `est_sales`, `gross_income`, `free_cash_flow`...
   - **Kết quả**: Sharpe cực thấp (0.1 - 0.7), Turnover quá cao hoặc Sub-universe Sharpe âm. Hầu hết các field cơ bản đã bị hệ thống arbitrage triệt để.

2. **Sentiment & Social Media (Batch 4,5)**:
   - `snt_social_value`, `news_sentiment`.
   - **Kết quả**: Sharpe quanh mức 1.2 - 1.4, Sub-Universe Sharpe thường < 0.5. Tín hiệu News thường có chu kỳ ngắn (1-3 ngày), khiến Turnover tăng mạnh và không bền vững với hàm `ts_decay_linear(20)`.

3. **Options Implied Volatility Skew (Batch 6,7,8,9,10)**:
   - Data field chủ đạo: `implied_volatility_call_30` và `implied_volatility_put_30`.
   - Logic: Sử dụng độ lệch (Skew) giữa Call và Put IV để định lượng kỳ vọng tăng/giảm giá mạnh từ thị trường phái sinh.
   - **Thách thức**: Sharpe dễ dàng đạt > 2.0 (cao nhất 2.28) nhưng Sub-universe Sharpe liên tục kẹt ở mức 0.5 - 0.8 (không qua mức Cut-off).
   - **Đột phá (Batch 10 - LL7WnpYe)**: 
     - Biểu thức: `ts_decay_linear(group_zscore(ts_mean(implied_volatility_call_30 - implied_volatility_put_30, 10), market), 30)`
     - Bằng cách áp dụng `ts_mean(10)` để làm mượt dữ liệu trước, rồi kết hợp Neutralization theo cụm `market` và Decay siêu dài 30 ngày.
     - Kết quả: Sharpe = 2.7, Fitness = 3.85, Turnover = 8.86%, Sub-Universe Sharpe = 1.47. Pass TẤT CẢ tiêu chí cứng.

## Kết luận Phase 22
- Tín hiệu Options (đặc biệt là Implied Volatility) chứa lượng Alpha khổng lồ và đặc biệt là RẤT ĐỘC ĐÁO (Unique) vì rất ít Quant researchers dùng trực tiếp raw IV field để xây dựng Core Model trên Top3000 (do nhiễu lớn).
- Phương pháp Smoothing kép (ts_mean + ts_decay_linear) là chìa khoá để thuần phục các Data Field có tính biến động cao như Options hay Volatility.
