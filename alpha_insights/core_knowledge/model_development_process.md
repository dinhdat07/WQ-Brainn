# Walkthrough: Phá vỡ bẫy Self-Correlation với Analyst Estimates (Alpha `le3WZmdl` - Batch 7 - 10)

## 1. Vấn đề cốt lõi (Bẫy Self-Correlation > 0.9)
Ban đầu, các Alpha đạt chuẩn (như `ZYKo6R78`) mang lại Sharpe và Fitness rất tốt nhưng lại dựa trên lõi **Price Momentum** (sử dụng giá `close`, `returns`, `vwap` kết hợp với các hàm `ts_decay_linear` lồng nhau). Hệ quả là khi đột biến (mutate) các mô hình này, chúng ta liên tục tạo ra các phiên bản "nhái", dẫn đến **Self-Correlation > 0.9** và không thể nộp thêm lên hệ thống.

## 2. Nguồn gốc ý tưởng (Idea #2)
Để bẻ gãy hoàn toàn sự tương quan (0.0 correlation), chúng ta phải sử dụng một tập dữ liệu hoàn toàn khác biệt. Mô hình này được xây dựng từ **Ý tưởng số 2 (Overpriced Stocks)** trong tài liệu `bronze_alpha_example.md` - sử dụng dữ liệu Dự báo của chuyên gia phân tích (Analyst Estimates).

**Giả thuyết:** 
Khi giá mục tiêu (`est_ptp` - Price Target) và dòng tiền tự do dự phóng (`est_fcf` - Free Cash Flow) di chuyển đồng pha (Tương quan dương cao), điều đó có nghĩa là thị trường đã phản ánh hết kỳ vọng (price-in). Cổ phiếu không còn dư địa tăng trưởng và dễ bị định giá quá cao (Overpriced). Do đó, chúng ta sẽ Bán khống (Short) những mã này.

Công thức gốc từ tài liệu: `-ts_corr(est_ptp, est_fcf, 252)`

## 3. Hành trình tinh chỉnh (Walkthrough)

### Bước 1: Kiểm định ý tưởng gốc (Batch 4 - 7)
Chúng ta đưa công thức `-ts_corr(est_ptp, est_fcf, 252)` vào chạy thử nghiệm. 
- **Kết quả:** Sharpe **1.23**, Fitness **0.78**. 
- **Đánh giá:** Mô hình có tiềm năng lớn (tương quan giá rất thấp), nhưng không vượt qua được bài test vì `Sharpe < 1.25` và `Fitness < 1.0`.

### Bước 2: Bơm Fitness và cải thiện tín hiệu (Batch 5 - 8 & Batch 6 - 9)
Để nâng Fitness lên mức tiêu chuẩn (> 1.0), chúng ta cần giảm độ nhiễu và kiểm soát Turnover (tần suất giao dịch) của mô hình. 
- **Giải pháp:** Sử dụng hàm `ts_decay_linear(..., 5)` bọc bên ngoài. Việc này giúp làm "mượt" các tín hiệu mua/bán, không bắt mô hình phải nhảy vọt liên tục, giúp tiết kiệm chi phí giao dịch.

### Bước 3: Rút ngắn chu kỳ và Chống tập trung vốn (Batch 7 - 10 - Thành công)
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

# Walkthrough: Xây dựng Core Signals Không Tương Quan & Tối Ưu Hóa (Phase 3 - Phase 7)

## 1. Tìm Kiếm Nguồn Dữ Liệu Độc Lập (Phase 3 & 4)
Sau khi khắc phục bẫy Self-Correlation ở Phase 1-2, chúng ta nhận ra rằng các tín hiệu dựa trên Giá/Khối lượng cuối ngày (End-of-Day Price/Volume) thường sẽ tự tương quan với nhau > 0.9 do bản chất bị đồng pha với thị trường chung (Beta).

- **Giải pháp (Phase 3):** Sử dụng các nguồn dữ liệu thay thế (Alternative Data) như Analyst Estimates (Dự báo phân tích). 
  - Mô hình e7x3P7gO khai thác phí bảo hiểm mục tiêu (est_ptp / close), áp dụng **Double Z-Score** (	s_zscore kết hợp group_zscore theo subindustry) để tạo ra Sharpe cực lớn (1.58).
- **Giải pháp (Phase 4):** Sử dụng dữ liệu Cơ bản (Fundamental Data). 
  - Mô hình RR1bxvea khai thác Asset Turnover (sales/assets). Điểm mấu chốt là **Nhân với tín hiệu động lượng ngắn hạn (Fast Reversion)** như 
ank(-(close/ts_mean(close, 5))). Điều này kết hợp ưu điểm của Fundamental (ổn định) và Fast Momentum (độ nhạy cao), đạt Sharpe 1.88 và tự tương quan cực thấp (0.31).

## 2. Blueprint Fundamental x Fast Momentum (Phase 5)
Kế thừa thành công từ Phase 4, chúng ta nhân bản Blueprint này sang các chỉ số cơ bản khác:
- **Operating Margin Reversion (88ePoPd7):** (sales / assets) * rank(-returns) -> Đạt Sharpe 1.95.
- **Sales Yield Reversion (ldOZEjr):** Giá trị doanh thu trên vốn hóa (sales / (close * sharesout)) * rank(-ts_delta(close, 3)) -> Đạt Sharpe 1.55.

**Kết luận:** Phương pháp tốt nhất để xây dựng mô hình Cơ bản mà vẫn giữ Sharpe cao là bắt các nhịp điều chỉnh ngắn hạn (Reversion) của các công ty có nền tảng cơ bản tốt.

## 3. Bài Toán Turnover và Phân Rã Biến Động (Phase 6)
Ở Phase 6, chúng ta quay lại với dữ liệu Volatility (Biến động) và Intraday (Biến động trong ngày), vốn tạo ra Sharpe rất khủng (lên tới 2.23) nhưng bị kẹt ở **Turnover > 0.7**, khiến Fitness bị hạ xuống dưới 1.0 (Không đạt tiêu chuẩn Submit).
- **Giải pháp:** Thay vì dùng hàm làm mượt nhẹ (	s_decay_linear(..., 5)), chúng ta tăng chu kỳ làm mượt lên **10, 15, và 20**.
- **Kết quả:** Mô hình d5RaEvVj (Intraday Reversion) sử dụng 	s_decay_linear(..., 10) đã nén Turnover từ 0.74 xuống 0.54, đẩy Fitness lên 1.04 và Sharpe 1.75. **Chìa khóa giảm Turnover cho các tín hiệu ngắn hạn là sử dụng Linear Decay với chu kỳ từ 10-15.**

## 4. Mô Hình Alpha Bạc (Silver Alphas - Phase 7)
Phase 7 chứng minh sức mạnh của Options Data. Thay vì sử dụng giá cổ phiếu, chúng ta giao dịch sự mất cân đối giữa quyền chọn mua và bán.
- **Mô hình Jjv1g3xO:** Đặt lệnh Mua (1) khi độ lệch hàm ý (Implied Volatility Spread giữa Call và Put) gia tăng trong lúc Khối lượng mở (Open Interest) của Call thấp hơn Put (pcr_oi_270 < 1).
- Bằng cách sử dụng 	s_decay_linear(..., 10), mô hình này dễ dàng chạm Sharpe 1.89 với Turnover chỉ **0.18**, hoàn toàn độc lập với thị trường chứng khoán cơ sở.
