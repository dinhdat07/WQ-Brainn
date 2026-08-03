# Nhật Ký Thất Bại (Failed Experiments Log)

Cuốn nhật ký này ghi lại những giả thuyết đã thử nghiệm nhưng không mang lại kết quả tốt (hoặc bị hệ thống Brain reject). Việc hiểu tại sao một Alpha thất bại quan trọng không kém việc tìm ra một siêu Alpha.

## 1. Vấn đề với Neutralization và ts_zscore

- **Giả thuyết**: Dùng `ts_zscore` để chuẩn hóa phân phối tín hiệu, kết hợp với cài đặt `Neutralization: SUBINDUSTRY` mặc định để hệ thống tự động loại bỏ rủi ro thị trường/ngành.
- **Thực tế**: Các Alpha tạo ra bị sụt giảm Fitness thê thảm (từ 0.98 xuống còn 0.20), nguyên nhân do hệ thống Neutralization đã triệt tiêu luôn phần tín hiệu tốt (alpha signal) khi tín hiệu đó đã được phân phối chuẩn. Thêm vào đó, việc lọc kép làm cho Turnover tăng đột biến.
- **Bài học (Insight)**: Nếu đã dùng các hàm cross-sectional (như `group_rank`, `ts_zscore`) bên trong công thức thì nên thiết lập **`Neutralization: NONE`** ở Settings để bảo toàn tính toàn vẹn của tín hiệu.

## 2. Vấn đề "Double Decay" (Làm mượt kép)
- **Giả thuyết**: Chỉ cần dùng `ts_decay_linear` ở ngoài cùng để ép Turnover xuống.
- **Thực tế**: Turnover giảm nhưng Sharpe lại tụt xuống 1.10. Lý do là phần lõi `ts_delta` quá nhiễu, việc làm mượt một cục nhiễu lớn ở đầu ra không bù đắp được sự biến động.
- **Bài học (Insight)**: Phải áp dụng chiến thuật **Double-Decay**. Một `ts_decay_linear(..., 3)` nhỏ bên trong để làm mượt dữ liệu thô, và một `ts_decay_linear(..., 5)` bên ngoài để ổn định tín hiệu Z-score. Cấu trúc này tối ưu rủi ro và đẩy Sharpe lên 1.51.

## 3. Các toán tử không hợp lệ (Invalid Operators)
- **Vấn đề**: Việc kết hợp dữ liệu bằng phép nhân phân số phức tạp hoặc dùng các toán tử điều kiện kiểu Python.
- **Bài học (Insight)**: FASTEXPR rất nghiêm ngặt. Tránh dùng các phép toán số học như `a / b` mà chưa qua bước xếp hạng. Thay vào đó, dùng `rank(a) * rank(b)` hoặc `ts_rank(a, d) * ts_rank(b, d)` sẽ an toàn và tạo tín hiệu ổn định hơn.

## 4. Dữ liệu Fundamental có tần suất thấp
- **Vấn đề**: Các biến như tài sản (`assets`), nợ (`liabilities`) thường chỉ cập nhật hàng quý (90 ngày). Nếu dùng `ts_delta(..., 3)` cho các biến này thì 87 ngày sẽ trả về 0, dẫn tới tín hiệu nhiễu cực mạnh và bị hệ thống phạt Fitness vì tín hiệu rời rạc.
- **Bài học (Insight)**: Đối với dữ liệu fundamental hàng quý, luôn dùng window từ 60 ngày trở lên cho `ts_delta` (ví dụ `ts_delta(..., 60)`) để bắt trend thay vì bắt dao động ngày.

## 5. Thất bại do Tương quan nội bộ (Self-Correlation Trap): N1bXbxxe
- **Mô hình**: `N1bXbxxe`
- **Công thức**: `ts_decay_linear(group_rank(sales / assets, subindustry) + rank((ts_backfill(implied_volatility_call_180, 60) - ts_backfill(implied_volatility_put_180, 60)) / ts_backfill(implied_volatility_mean_180, 60)), 10)`
- **Chỉ số IS**: Sharpe 1.71 | Fit 1.42 | TO 0.0942 | Margin 18.4 bps
- **Lý do thất bại**: Bị từ chối khi submit với thông báo: `Self-correlation 0.8673 is above cutoff of 0.7 and Sharpe not better by 10.0% or more`.
- **Nguyên nhân cốt lõi**: Trong danh mục đã nộp (Phase 7), mô hình **`pwKZnmX6`** (`ts_decay_linear(ts_backfill((implied_volatility_call_180 - implied_volatility_put_180) / implied_volatility_mean_180, 20), 10)`) đã đạt **Sharpe 2.21**. Việc `N1bXbxxe` kết hợp cộng thêm fundamental vẫn giữ nguyên độ lệch skew liên tục 180 ngày nên tương quan tới 0.8673. Do Sharpe của `N1bXbxxe` (1.71) thấp hơn 2.21, hệ thống chặn submit.
- **Bài học (Insight)**: Khi một nhóm tín hiệu (như Options 180d IV Skew) đã có một mô hình Sharpe rất cao (>2.0) được nộp, KHÔNG NÊN tiếp tục dùng dạng skew liên tục của cùng kỳ hạn đó. Phải chuyển sang:
  1. Dạng điều kiện rời rạc (`trade_when(pcr_oi < 1, spread, -1)`).
  2. Kỳ hạn khác hoàn toàn (270d) kết hợp với bộ lọc dữ liệu khác.
  3. Nhóm nhân tố hoàn toàn mới (Short Interest, Accruals, Analyst Revisions).

## 6. Thất bại do Sub-Universe Sharpe: LLGWQvYm & vRN8Q6av
- **Các mô hình**:
  - `LLGWQvYm`: `ts_decay_linear(group_rank(trade_when(ts_backfill(pcr_oi_180, 60) < 1, (call_180 - put_180), -1), subindustry), 10)` (Sharpe 2.04 | Fit 1.57).
  - `vRN8Q6av`: `ts_decay_linear(group_rank(sales / assets, subindustry) + group_rank(trade_when(ts_backfill(pcr_oi_270, 60) < 1, (call_270 - put_270), -1), subindustry), 10)` (Sharpe 1.83 | Fit 1.55).
- **Lý do thất bại khi Submit**:
  - `LLGWQvYm`: `Sub-universe Sharpe of 0.52 is below cutoff of 0.88`.
  - `vRN8Q6av`: `Sub-universe Sharpe of 0.64 is below cutoff of 0.79`.
- **Nguyên nhân cốt lõi (Root Cause)**:
  1. Dữ liệu Quyền chọn (`pcr_oi`, `implied_volatility`) chỉ tập trung dày đặc ở nhóm vốn hóa lớn (Large/Mega caps). Ở nhóm vốn hóa nhỏ (Top 2000 - Top 3000), dữ liệu giao dịch options bị thưa thớt (sparse).
  2. Khi chạy kiểm thử trên các phân khúc vốn hóa nhỏ (Sub-universes), hàm `trade_when(..., -1)` trả về giá trị `-1` cho hàng trăm cổ phiếu không có quyền chọn. Điều này làm tín hiệu bị san phẳng (tied rank 0.5), khiến Sharpe ở các phân khúc này bị tụt xuống dưới ngưỡng yêu cầu.
- **Giải pháp khắc phục thành công (The Fix)**:
  - Xây dựng **Kiến trúc Tam Giác Thể Chế (3-Pillar Institutional Triad - `88pomANl`)**: Bổ sung trụ cột dòng tiền trong ngày `group_rank(-(close - open) / open, subindustry)`. Trụ cột này hoạt động mạnh mẽ nhất ở nhóm Mid/Small caps, bù đắp hoàn hảo khoảng trống dữ liệu quyền chọn và đẩy Sub-Universe Sharpe lên **1.26 (PASS)**!
