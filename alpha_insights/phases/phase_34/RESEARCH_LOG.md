# RESEARCH LOG - Báo cáo Tổng hợp Các Hướng Thử Nghiệm

> Mục tiêu: Tìm kiếm một mô hình vượt mốc Sharpe 1.35, vượt qua Self-correlation (<0.70), Fitness (>1.0), và Sub-universe Sharpe (>0.60).

Tài liệu này tổng hợp toàn bộ các hướng nghiên cứu từ Batch đầu tiên của Phase 34 cho đến hiện tại. Do chưa có mô hình nào thỏa mãn *toàn bộ* các điều kiện để được coi là "thành công", mọi nỗ lực đều được quy về Phase 34.

## 1. Hướng tiếp cận 1: Tối ưu hóa F-Score và Cấu trúc Smoothing (Các Batch cũ)
- **Ý tưởng:** Sử dụng bộ dữ liệu kinh điển `fscore_value`, `fscore_bfl_momentum` kết hợp với `rp_nip_insider` (Giao dịch nội bộ) hoặc `mean_composite_sentiment_score` (Tâm lý tin tức).
- **Thử nghiệm:** Thay đổi các hàm làm mượt (smoothing) như `ts_decay_linear`, `ts_step`, `ts_mean`, đổi cửa sổ thời gian từ 10 đến 60 ngày.
- **Kết quả:** **THẤT BẠI**.
- **Lý do:** Mặc dù tạo ra nhiều mô hình có Sharpe rất cao (vượt 1.40) và Fitness tốt, nhưng chúng liên tục vướng phải ngưỡng **Self-correlation 0.72 - 0.74**. Nguyên nhân do các thành phần dữ liệu cốt lõi (F-score, Insider) đã được sử dụng quá nhiều ở các mô hình đã đỗ trước đó (trong Phase 32, 33), dẫn đến rủi ro trùng lặp yếu tố thị trường.

## 2. Hướng tiếp cận 2: Sử dụng Dữ liệu Cơ bản mới (Sales Estimate, Operating Margin)
- **Ý tưởng:** Chuyển hướng sang các trường dữ liệu ít bị khai thác như Ước tính doanh thu (`sales_estimate_value`) hoặc Biên lợi nhuận hoạt động (`operating_margin`).
- **Thử nghiệm:** Khớp các trường này vào hàm `ts_corr`.
- **Kết quả:** **THẤT BẠI KỸ THUẬT**.
- **Lý do:** Hệ thống báo lỗi "Operator ts_corr does not support event inputs". Các trường dữ liệu dạng sự kiện (Event) không thể kết hợp trực tiếp bằng `ts_corr`.

## 3. Hướng tiếp cận 3: Tâm lý Mạng Xã Hội (Sự kiện Đột phá)
- **Ý tưởng:** Tránh hoàn toàn Phân tích cơ bản và Tin tức truyền thống. Chuyển sang Dữ liệu Mạng Xã Hội (`scl12_sentiment`) kết hợp với Quyền chọn (`pcr_vol`).
- **Thử nghiệm:** `ts_corr(scl12_sentiment, pcr_vol_30, 40)`.
- **Kết quả:** Đạt Sharpe 1.38. Độc bản 100%. Vượt qua rào cản Self-correlation nhưng **THẤT BẠI FITNESS** (Fitness < 1.0 do Turnover cao).

## 4. Hướng tiếp cận 4: Cứu Fitness bằng cách Kéo dài Chu kỳ
- **Ý tưởng:** Tăng hàm làm mượt (Smoothing) lên 90 - 120 ngày để giảm Turnover cho mô hình Mạng xã hội.
- **Thử nghiệm:** `ts_mean(group_rank(ts_corr(scl12_sentiment, pcr_vol_60, 90), subindustry), 90)`.
- **Kết quả:** Sharpe tăng vọt lên **1.78**, Fitness đạt **1.07** (PASS). Tuy nhiên, **THẤT BẠI SUB-UNIVERSE SHARPE** (Chỉ đạt 0.29 so với ngưỡng 0.77).
- **Lý do:** Dữ liệu mạng xã hội phân bổ không đều (sôi động ở nhóm Công nghệ/Tiêu dùng, đóng băng ở Tiện ích/Nguyên vật liệu), khiến lợi nhuận bị lệch về một số ngành.

## 5. Hướng tiếp cận 5: Cứu Sub-universe bằng Neutralization (Đang thực hiện)
- **Ý tưởng:** Giữ nguyên mô hình Sharpe 1.78. Tuy nhiên, thay vì phân bổ vốn theo Tiểu ngành (`SUBINDUSTRY`), ta ép mô hình phân bổ vốn cân bằng trên toàn Ngành (`SECTOR`), Thị trường (`MARKET`), hoặc Liên ngành (`INDUSTRY`). Hoặc kết hợp Mạng xã hội với thanh khoản (Volume).
- **Kết quả hiện tại (Mới nhất):**
  - Neutralize theo SECTOR (Alpha `le8JY1xA`): Sharpe 1.62, Fitness 1.01.
  - Neutralize theo MARKET (Alpha `N1QkG89g`): Sharpe 1.64, Fitness 1.14.
  - Neutralize theo INDUSTRY (Alpha `blR7gg3p`): Sharpe 1.77, Fitness 1.11.
- **Trạng thái:** Đang chờ người dùng kiểm tra Sub-universe Sharpe.
