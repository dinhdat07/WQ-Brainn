# Alpha Insight: Assets & Sales Momentum (3qeeYzj6 & rKPP6291)

## Thông tin Alpha
- **3qeeYzj6 (Assets)**: Sharpe 1.44 | Fit 1.23
- **rKPP6291 (Sales)**: Sharpe 1.46 | Fit 1.25
- **Kiến trúc lõi**: `ts_decay_linear(ts_zscore(ts_decay_linear(group_rank(ts_rank(CORE_DATA, 60), subindustry) * ts_rank(-ts_delta(close, 3), 5), 3), 30), 5)`
- **Loại dữ liệu**: Fundamental (Assets / Sales) kết hợp Price Trigger (Mean Reversion).

## Ý tưởng & Cơ sở lý thuyết
Đây là sự tiến hóa trực tiếp từ siêu phẩm `ZYKo6R78` (Cashflow Momentum). 
Ý tưởng chính là: **Sử dụng Z-score và Double-Decay để thuần hóa Turnover và tối ưu Fitness, đồng thời giữ được Sharpe > 1.25**. 
Tuy nhiên, để vượt qua bài kiểm tra **Self-Correlation < 0.7** với `ZYKo6R78`, chúng ta đã thay đổi hoàn toàn "hệ trục tọa độ" của lõi Fundamental. 
Thay vì dùng Cashflow, chúng ta sử dụng `assets` (Tổng tài sản) và `sales` (Doanh thu). Do đây là các metrics cơ bản khác biệt về mặt bản chất tài chính so với Cashflow, chúng tạo ra tín hiệu giao dịch độc lập đủ lớn để không bị tương quan quá cao với alpha cũ, nhưng vẫn giữ được khả năng sinh lời mạnh mẽ nhờ Price Trigger `-ts_delta(close, 3)`.

## Quy trình Thử nghiệm & Thất bại (Lessons Learned)
Trước khi đạt được 2 Alpha này, chúng tôi đã trải qua nhiều thử nghiệm thất bại (được ghi nhận trong các script bị loại bỏ):

1. **Orthogonal Generator (Dữ liệu Alternative thuần túy)**:
   - Thử nghiệm Sentiment, Analyst Revisions, Options (PCR).
   - Kết quả: Sharpe lẹt đẹt < 0.85. 
   - Bài học: Dữ liệu Alternative độc lập không đủ sức mạnh (Sharpe) nếu đứng một mình.

2. **Blended Generator (Kết hợp Alternative + Price)**:
   - Thử nghiệm: `rank(Sentiment) * rank(PriceDelta)`
   - Kết quả: Có cải thiện, Sharpe lên ~0.85, Fit cao, nhưng không thể vượt mốc 1.25.
   - Bài học: Phân phối của Alternative data quá nhiễu, việc nhân rank trực tiếp chưa tạo ra điểm nổ đột phá.

3. **Ultimate Orthogonal (Ép Alternative vào bộ khung Z-score)**:
   - Thử nghiệm: Áp dụng Z-score và Double-Decay của `ZYKo6R78` vào Sentiment / Analyst.
   - Kết quả: Sharpe rớt thảm hại xuống 0.2 - 0.4.
   - Bài học: **Cực kỳ quan trọng**. Kỹ thuật `ts_zscore` hoạt động rất tốt để chuẩn hóa các dữ liệu Fundamental (có tính chu kỳ, ổn định), nhưng lại PHÁ HỎNG hoàn toàn phân phối của dữ liệu Alternative/Sentiment vốn dĩ đã có độ nhiễu cao. 

4. **Assets Optimizer (Thay đổi Price Trigger)**:
   - Thử nghiệm: Giữ lõi Fundamental (`assets`) nhưng đổi Price Trigger thành VWAP Reversion, HighLow Reversion.
   - Kết quả: Khá khẩm hơn, HighLow Reversion đạt Sharpe 1.33 nhưng Fit rớt xuống 0.94 (không đủ chuẩn).
   - Bài học: `-ts_delta(close, 3)` vẫn là Price Trigger ổn định nhất khi kết hợp với bộ khung Z-score.

## Kế hoạch tương lai
- Hãy sử dụng bộ khung Z-score này cho các dữ liệu **Fundamental (Báo cáo tài chính)** khác: `ebit`, `net_income`, `debt`, v.v.
- Tuyệt đối **không** dùng `ts_zscore` cho dữ liệu Sentiment/Options. Với các dữ liệu đó, cần xây dựng bộ khung phân tích tĩnh (Cross-sectional rank) đơn giản hơn.
