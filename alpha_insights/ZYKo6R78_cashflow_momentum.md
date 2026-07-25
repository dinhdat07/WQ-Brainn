# Alpha ID: ZYKo6R78

## Chỉ số (Statistics)
- **Sharpe:** 1.51
- **Fitness:** 1.30
- **Turnover:** 40.89%
- **Returns:** 30.25%
- **Drawdown:** 25.34%

## Công thức (Formula)
```fastexpr
ts_decay_linear(ts_zscore(ts_decay_linear(group_rank(ts_rank(ts_delta(actual_cashflow_per_share_value_quarterly, 60), 60), subindustry) * ts_rank(-ts_delta(close, 3), 5), 3), 30), 5)
```

## Cài đặt (Settings)
- **Neutralization:** `NONE`
- **Truncation:** `0.08`
- **Delay:** `1`
- **Decay:** `0`
- **Pasteurization:** `ON`

## Khai thác Insight (Giải phẫu công thức)

1. **Ý tưởng cốt lõi (Core Idea)**:
   Mô hình kết hợp xung lượng (momentum) của dòng tiền thực tế (`actual_cashflow_per_share_value_quarterly`) với tín hiệu đảo chiều ngắn hạn (mean-reversion) của giá đóng cửa (`close`). Cổ phiếu có dòng tiền cải thiện nhưng vừa bị bán tháo sẽ được mua vào.

2. **Khống chế Nhiễu Bằng Double-Decay**:
   - `ts_decay_linear(..., 3)`: Làm mượt tín hiệu bên trong trước khi đưa vào hàm tính Z-score, giúp tránh các dao động nhiễu ngắn hạn do `ts_delta` tạo ra.
   - `ts_decay_linear(..., 5)`: Làm mượt tín hiệu Z-score ngoài cùng để giảm **Turnover**. Việc này đã đưa Turnover từ vùng rủi ro (>70%) xuống mức cực kỳ an toàn (40.89%), qua đó kéo Fitness tăng vọt lên 1.30.

3. **Cơ chế Neutralization: NONE**:
   Thay vì để hệ thống tự động loại bỏ rủi ro ngành (SUBINDUSTRY/SECTOR neutralization), công thức này sử dụng `group_rank(..., subindustry)` trực tiếp bên trong tín hiệu, và dùng `ts_zscore(..., 30)` để đồng nhất hóa phân phối.
   **Rút kinh nghiệm:** Khi sử dụng `ts_zscore`, việc để `neutralization` mặc định thường xuyên triệt tiêu tín hiệu mạnh, làm Fitness giảm sát về mốc 0.1-0.2. Thay đổi thành `NONE` đã mở khóa sức mạnh thực sự của mô hình.

4. **Trường dữ liệu hiệu quả cao**:
   Dòng tiền gộp (`actual_cashflow_per_share_value_quarterly`) có tính dự phóng (predictive power) vượt trội hơn hẳn so với Tổng tài sản (`assets`) hoặc Lợi nhuận HĐ (`oibdpq`).
