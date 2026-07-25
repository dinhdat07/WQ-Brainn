# Walkthrough: Phá vỡ bẫy Self-Correlation với Analyst Estimates (Alpha `le3WZmdl`)

## 1. Vấn đề cốt lõi (Bẫy Self-Correlation > 0.9)
Ban đầu, các Alpha đạt chuẩn (như `ZYKo6R78`) mang lại Sharpe và Fitness rất tốt nhưng lại dựa trên lõi **Price Momentum** (sử dụng giá `close`, `returns`, `vwap` kết hợp với các hàm `ts_decay_linear` lồng nhau). Hệ quả là khi đột biến (mutate) các mô hình này, chúng ta liên tục tạo ra các phiên bản "nhái", dẫn đến **Self-Correlation > 0.9** và không thể nộp thêm lên hệ thống.

## 2. Nguồn gốc ý tưởng (Idea #2)
Để bẻ gãy hoàn toàn sự tương quan (0.0 correlation), chúng ta phải sử dụng một tập dữ liệu hoàn toàn khác biệt. Mô hình này được xây dựng từ **Ý tưởng số 2 (Overpriced Stocks)** trong tài liệu `bronze_alpha_example.md` - sử dụng dữ liệu Dự báo của chuyên gia phân tích (Analyst Estimates).

**Giả thuyết:** 
Khi giá mục tiêu (`est_ptp` - Price Target) và dòng tiền tự do dự phóng (`est_fcf` - Free Cash Flow) di chuyển đồng pha (Tương quan dương cao), điều đó có nghĩa là thị trường đã phản ánh hết kỳ vọng (price-in). Cổ phiếu không còn dư địa tăng trưởng và dễ bị định giá quá cao (Overpriced). Do đó, chúng ta sẽ Bán khống (Short) những mã này.

Công thức gốc từ tài liệu: `-ts_corr(est_ptp, est_fcf, 252)`

## 3. Hành trình tinh chỉnh (Walkthrough)

### Bước 1: Kiểm định ý tưởng gốc (Batch 7)
Chúng ta đưa công thức `-ts_corr(est_ptp, est_fcf, 252)` vào chạy thử nghiệm. 
- **Kết quả:** Sharpe **1.23**, Fitness **0.78**. 
- **Đánh giá:** Mô hình có tiềm năng lớn (tương quan giá rất thấp), nhưng không vượt qua được bài test vì `Sharpe < 1.25` và `Fitness < 1.0`.

### Bước 2: Bơm Fitness và cải thiện tín hiệu (Batch 8 & 9)
Để nâng Fitness lên mức tiêu chuẩn (> 1.0), chúng ta cần giảm độ nhiễu và kiểm soát Turnover (tần suất giao dịch) của mô hình. 
- **Giải pháp:** Sử dụng hàm `ts_decay_linear(..., 5)` bọc bên ngoài. Việc này giúp làm "mượt" các tín hiệu mua/bán, không bắt mô hình phải nhảy vọt liên tục, giúp tiết kiệm chi phí giao dịch.

### Bước 3: Rút ngắn chu kỳ và Chống tập trung vốn (Batch 10 - Thành công)
- **Rút ngắn chu kỳ (Lookback):** Chu kỳ 252 ngày (1 năm) là quá chậm chạp để phản ứng với những đợt điều chỉnh giá cổ phiếu. Chúng ta đã rút ngắn mạnh tay xuống **20 ngày** (1 tháng) để chớp được những tín hiệu nhạy bén nhất của thị trường.
- **Tránh lỗi Concentrated Weight:** Thay vì phân nhóm cổ phiếu theo ngành (`group_rank(..., sector)`), chúng ta dùng hàm `rank(...)` trên toàn bộ tập thị trường `TOP3000`. Cấu trúc này ép phân bổ trọng số danh mục (weights) đều cho tất cả các mã, giải quyết dứt điểm rủi ro một mã chiếm quá 10% danh mục.

## 4. Công thức chốt (The Holy Grail)
Sau 3 bước, chúng ta có công thức cuối cùng:
`ts_decay_linear(rank(-ts_corr(est_ptp, est_fcf, 20)), 5)`

**Chỉ số:** 
- Sharpe: **1.71**
- Fitness: **1.41**
- Tương quan (Self-Correlation): **0.0**

Hoàn toàn phá vỡ các giới hạn của nền tảng!
