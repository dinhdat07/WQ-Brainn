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
