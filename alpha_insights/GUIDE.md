# Hướng dẫn Lưu trữ & Quản lý Kiến thức (Alpha Insights Guide)

Tài liệu này quy định **Convention** (quy chuẩn) bắt buộc cho việc lưu trữ toàn bộ các mô hình, nhật ký thử nghiệm và kiến thức rút ra trong quá trình nghiên cứu WorldQuant Brain. Mục tiêu là đảm bảo tính nhất quán, dễ tra cứu và bảo toàn bối cảnh (context) cho từng Phase.

## 1. Cấu trúc Thư mục (Directory Structure)

Thư mục `alpha_insights/` được cấu trúc trực tiếp theo **Phase**:

```text
alpha_insights/
├── GUIDE.md                 # Tài liệu hướng dẫn này
├── core_knowledge/          # Kiến thức nền tảng, bất biến qua các Phase
│   ├── dictionary.md        # Từ điển các trường dữ liệu và mô tả
│   ├── model_development_process.md # Quy trình chuẩn phát triển model
│   ├── failed_experiments_log.md    # Log các hướng đi thất bại tổng thể
│   └── mutation_experiments_log.md  # Log các phép biến đổi toán học
└── phases/                  # Không gian làm việc chính
    ├── phase_X/
    │   ├── report.md        # Báo cáo tổng kết Phase
    │   └── models/          # Các mô hình thành công của riêng Phase X
    │       ├── [AlphaID]_[Tên_Ngắn].md
    │       └── ...
```

---

## 2. Quy chuẩn Báo cáo Phase (`report.md`)

Vào cuối mỗi Phase (hoặc khi đạt được đột phá/kết thúc chiến dịch), Agent **BẮT BUỘC** phải tạo file `report.md` tại `phases/phase_X/report.md`.

**Cấu trúc bắt buộc của `report.md`:**
1. **Context & Objectives (Bối cảnh & Mục tiêu):** Ghi rõ mục tiêu của Phase (vd: Đạt Sharpe > 2.0, hay giảm Correlation < 0.70).
2. **Experimental Journey (Hành trình Khám phá):** Liệt kê các Batch, các bộ dữ liệu (dataset) đã thử nghiệm. Ghi nhận cả thành công và thất bại.
3. **The Breakthrough (Đột phá/Giải pháp):** Giải thích chi tiết về thuật toán, ý tưởng hoặc "cú hack" giúp vượt qua điểm nghẽn (ví dụ: dùng `ts_decay_linear` để ép Fitness).
4. **Final Takeaways (Bài học rút ra):** Đúc kết thành quy luật/kiến thức để các Phase sau không lặp lại sai lầm.

---

## 3. Quy chuẩn Lưu trữ Mô hình (`models/`)

Chỉ lưu các Alpha thành công hoặc có giá trị nghiên cứu cao. Mỗi Alpha phải được lưu thành **MỘT FILE ĐỘC LẬP** (Không gộp nhiều model vào 1 file).

**Tên file:** `[AlphaID]_[Tên_Ngắn_Gọn].md` (Vd: `9qppnrPV_Options_Skew_Smoothed.md`)
**Vị trí:** `phases/phase_X/models/`

**Cấu trúc bắt buộc bên trong file Model:**
```markdown
# Alpha [AlphaID]: [Tên Mô hình]

## Meta Data
- **Alpha ID:** [ID]
- **Status:** [ACTIVE / PENDING / FAILED_CORR]
- **Author/Phase:** Phase [X]
- **Universe:** [TOP3000 / ...]
- **Delay:** [1]

## Performance Metrics
- **Sharpe Ratio:** [X.XX]
- **Fitness:** [X.XX]
- **Turnover:** [X.X%]
- **Max Correlation:** [X.XXXX] (vs [ID_Khác])

## The Signal
`[Công thức FastExpr (được format cẩn thận để dễ đọc)]`

## Idea & Mechanics
- Phân tích từng thành phần của công thức. Tại sao dùng `rank()`? Tại sao dùng `ts_backfill`?

## Insight
- Điểm mấu chốt tạo nên thành công của mô hình này (Vd: Thay đổi `decay` làm giảm Turnover).
```

---

## 4. Quản lý Kiến thức Cốt lõi (`core_knowledge/`)

Nếu bạn phát hiện ra một **quy luật vĩnh cửu** của nền tảng WorldQuant (Ví dụ: "Dữ liệu Event không hoạt động với cross-sectional operators", hoặc "Luật 10% Sharpe Improvement khi Correlation > 0.70"), hãy:
1. Ghi nhận nó vào `report.md` của Phase hiện tại.
2. Cập nhật nó vào `model_development_process.md` hoặc `dictionary.md` để trở thành **Core Knowledge**.

> [!WARNING]
> Không bao giờ tạo các thư mục rác (như `successful_models/` hay `experiment_logs/` ngoài `alpha_insights/`). Hãy luôn tuân thủ nguyên tắc đóng gói theo Phase!
