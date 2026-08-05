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

## 7. The Orthogonality Barrier (Phase 9 & 10)
- **Vấn đề**: Trong Phase 9 và 10, chúng tôi đặt mục tiêu tìm kiếm các mô hình đạt mức "Spectacular" (Sharpe > 2.50) nhưng phải hoàn toàn trực giao (Self-Correlation < 0.70) với các mô hình siêu hạng đã nộp trước đó (đặc biệt là nhóm `88pomANl` - The Institutional Triad).
- **Thực tế**: Các thử nghiệm bằng F-Scores (`fscore_bfl_momentum`), Neutralization Pivots (đổi sang `MARKET` hoặc `SECTOR`), và Mixed Decays (áp dụng decay độc lập) đã tạo ra hàng loạt mô hình siêu hạng (ví dụ: `wpax90oY` đạt Sharpe 2.59, `RRmQEx0j` đạt 2.17, `MPGR115L` đạt 2.08). 
- **Lý do thất bại**: **TẤT CẢ** các mô hình đạt Sharpe > 2.0 đều có PnL Self-Correlation > 0.90 với mô hình cũ. Mọi nỗ lực ép độ tương quan (Correlation) xuống dưới 0.70 bằng cách loại bỏ 1 trong 3 trụ cột (Fundamental, Options Skew, Reversion) hoặc đổi Neutralization sang Market/Sector đều làm Sharpe rớt thẳng đứng (xuống mức 1.71, 1.30, hoặc 1.14).
- **Bài học (Insight)**: Bất kỳ biến thể nào giữ lại lõi dự đoán của bộ dữ liệu sinh lời cực mạnh trong USA TOP3000 đều hội tụ về một danh mục vị thế (Positions) giống hệt nhau.

## 8. The Principal Component Trap (Bẫy Thành Phần Chính)
- **Vấn đề**: Alpha (tín hiệu dự báo) trong một tập vũ trụ cụ thể là hữu hạn. Bộ ba `sales/assets` + `Options Skew` + `Reversion` đã hấp thụ tối đa phương sai dự báo (predictive variance) tồn tại trong dữ liệu truyền thống.
- **Bài học (Insight)**: Việc cố gắng "vắt" thêm Sharpe > 2.50 từ những tập dữ liệu này mà mong muốn nó không tương quan với mô hình cũ là bất khả thi về mặt toán học. Tín hiệu quá mạnh sẽ lấn át mọi sự tùy chỉnh (decays, truncation, f-scores) ở bước cuối, khiến thành phần chính (Principal Component) của lợi nhuận mô hình mới bị chi phối hoàn toàn bởi mô hình cũ.

## 9. Sentiment Momentum (Phase 11)
- **V?n �?**: Vi?c k?t h?p d? li?u �? nh?y (Sentiment) nh� 
ews_sentiment v?i c?u tr�c Momentum (	s_delta, 	s_corr) t?o ra k?t qu? �m (Sharpe -0.06). 
- **B�i h?c (Insight)**: Sentiment data r?t nhi?u v� d? b? �?o chi?u ng?n h?n, n?u kh�ng c� b? l?c m?nh ho?c kh�ng d�ng Neutralize c?n th?n, n� s? c?n ng�?c l?i PnL.

## 10. B?y The Golden Wrapper (Phase 12)
- **V?n �?**: Trong Batch 10 c?a Phase 12, ch�ng t�i c? g?ng c�?ng h�a m?t m� h?nh c� Sharpe 1.71 (Microstructure Price-Volume + IV Skew) b?ng c�ch b?c n� trong m?t l?p 	s_zscore ho?c group_rank b�n trong h�m decay 80 ng�y. K?t qu?: Sharpe r?t th?m h?a xu?ng -0.08.
- **B�i h?c (Insight)**: �p d?ng c�c ph�p bi?n �?i phi tuy?n t�nh (non-linear transformation) n?ng �� l�n m?t t�n hi?u v?n �? ��?c l�m m�?t (smoothed) s? b? g?y ho�n to�n ph�n ph?i c?a t�n hi?u d? b�o, l�m n� m?t �i ph��ng h�?ng (directional predictive power).

