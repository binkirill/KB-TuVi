---
name: kb-tuvi
version: 3.0.0
description: Hệ thống Huyền Học Đông – Tây & Thần Số Học Đa Phái chuẩn Zero-Hallucination & Web-Ready (Tử Vi Đẩu Số Đa Phái Việt Nam + Quốc tế iztro, Bát Tự Tứ Trụ 9 Cổ Thư, Thần Số Học Pythagoras Việt Nam/Quốc tế + Chaldean Cổ Đại + Ma Trận Định Mệnh 22 Arcana + Chấm Điểm Đặt Tên/Thương Hiệu, Kinh Dịch 64 Quẻ Lục Hào Nạp Giáp, Mai Hoa Dịch Số & Kỳ Môn Độn Giáp Thời Gia). Tự động đổi lịch Vạn Niên thiên văn UTC+7, hiệu chỉnh Giờ Chân Thái Dương 63 tỉnh thành Việt Nam, kiểm chứng chéo Đông × Tây (Tử Vi × Bát Tự × Thần Số Học), xuất Lá Số / Mệnh Thư HTML, cung cấp REST API CORS & JS SDK cho dự án Web. Kích hoạt bất cứ khi nào người dùng hỏi xem tử vi, bát tự / tứ trụ, thần số học / nhân số học, con số chủ đạo / đường đời / sứ mệnh / linh hồn, biểu đồ ngày sinh, kim tự tháp 4 đỉnh cao, năm cá nhân, ma trận định mệnh, đặt tên con / nghệ danh / thương hiệu, gieo quẻ kinh dịch / lục hào / kỳ môn độn giáp, hoặc gọi /kb-tuvi.
---

# ☯️ × 🔢 KB-TUVI v3.0 — HỆ THỐNG HUYỀN HỌC & THẦN SỐ HỌC ĐÔNG–TÂY (ZERO-HALLUCINATION & WEB-READY)

Skill này kết tinh kiến trúc tinh hoa nhất từ các kho mã nguồn huyền học phương Đông & Thần số học phương Tây hàng đầu thế giới:
- **Phương Đông:** `jinchenma94/bazi-skill` (4.2k⭐), `SylarLong/iztro` (4.0k⭐), `FANzR-arch/Numerologist_skills` (2.2k⭐), `Johnson-Jia/liuyao-divination` + đặc thù **Nam Phái Tử Vi & Lịch Vạn Niên `UTC+7` Việt Nam** (`Tuần – Triệt`, Vòng Thái Tuế, Bác Sĩ, tọa độ 63 tỉnh thành).
- **Phương Tây (Thần Số Học Đa Phái):** `@nhatnguyet/than-so-hoc` & `vietanhdev/thansohoc` (chuẩn dấu tiếng Việt NFD, phân loại động chữ `Y`, Nhân số học VN giữ Số `10`), `compuuteio/numerology` & `evoluteur/motivational-numerology` (20+ chỉ số Pythagoras quốc tế), `LanderTome/numerologyCalculator` (hệ Chaldean Babylon cổ đại `1..8` & Số Kép Huyền Bí `10..52` chấm điểm tên gọi), `lexterror` (Ma trận `3×3` & 15 Mũi tên Đầy/Trống), `sanzol-tech/destiny-matrix` (Ma trận Định mệnh 22 Arcana).
- **Web-Ready Architecture:** Tích hợp sẵn REST API bật CORS (`gui_server.py`) và thư viện JS/TS độc lập (`scripts/web_numerology_sdk.js`) để nhúng thẳng vào dự án Web (`Next.js / React / FastAPI`).

---

## 1. BA LUẬT SẮT BẮT BUỘC (IRON LAWS — TUYỆT ĐỐI KHÔNG VI PHẠM)

1. **LUẬT SỐ 1 — "CODE TÍNH TOÁN, AI LUẬN GIẢI" (ZERO MENTAL MATH):**
   - **CẤM 100%** tự nhẩm đổi lịch Dương ↔ Âm, tự nhẩm Tiết Khí, tự an sao Tử Vi, tự nạp giáp Lục Hào, hay **tự cộng nhẩm chữ cái Họ tên / Ngày sinh ra chỉ số Thần số học** bằng trí nhớ LLM.
   - **BẮT BUỘC** chạy script `scripts/huyenhoc_cli.py` trước khi phát biểu bất kỳ nhận định nào. Kết quả JSON/HTML từ script là **Nguồn Sự Thật Duy Nhất (Single Source of Truth)**.
2. **LUẬT SỐ 2 — TUÂN THỦ TUYỆT ĐỐI CHÍNH SÁCH KASPERSKY / CẤM POWERSHELL:**
   - Chỉ gọi trực tiếp binary `python -X utf8` trên 1 dòng ngắn gọn trỏ vào `scripts/huyenhoc_cli.py` (hoặc `scripts/gui_server.py`), **tuyệt đối không** dùng PowerShell cmdlets hay `python -c` inline phức tạp.
   - Mọi file JSON/HTML xuất tạm phải đặt gọn trong thư mục `_temp/` hoặc thư mục người dùng chỉ định.
3. **LUẬT SỐ 3 — TÁCH BẠCH HỆ THỐNG & CHỐNG ĐỘC ĐOÁN (ANTI-DOGMATISM):**
   - Khi phân tích từng hệ: **Không râu ông nọ cắm cằm bà kia** (đang phân tích Tử Vi không lẫn thuật ngữ Bát Tự/Thần số học; chỉ đối chiếu giao thoa tại mục **Kiểm Chứng Chéo Đông × Tây**).
   - **Cấm tuyệt đối** dùng ngôn từ hù dọa cực đoan (*"số tuyệt mạng"*, *"nợ nghiệp nặng không ngóc đầu lên được"*, *"mũi tên uất hận đời bất hạnh"*). Luôn diễn đạt theo **xu hướng cấu trúc & bài học chuyển hóa thực tế**.

---

## 2. ĐỊNH TUYẾN CHẾ ĐỘ THEO NHU CẦU NGƯỜI DÙNG (INTENT ROUTING)

| Yêu cầu của người dùng | Chế độ `--mode` | Tài liệu `references/` cần đọc trước khi luận |
| :--- | :---: | :--- |
| Xem tổng quát cuộc đời Đông × Tây (Tử Vi + Bát Tự + Thần Số Học + Kiểm chứng chéo — **mặc định khuyên dùng!**) | `--mode full` | `tuvi_schools_and_patterns.md` + `bazi_classics_methodology.md` + `numerology_east_west_guide.md` |
| Chỉ xem **Thần số học / Nhân số học**, Biểu đồ ngày sinh, 4 Đỉnh cao, Năm cá nhân, Ma trận 22 Arcana, hoặc **chưa rõ giờ sinh** | `--mode numerology` | `numerology_east_west_guide.md` |
| Chỉ yêu cầu xem riêng Lá số Tử Vi (12 cung, chính phụ tinh, Tuần Triệt, Phi Tinh) | `--mode tuvi` | `tuvi_schools_and_patterns.md` + `han_viet_glossary.md` |
| Chỉ yêu cầu xem riêng Bát Tự / Tứ Trụ / Tử Bình / Khuyết Ngũ Hành | `--mode bazi` | `bazi_classics_methodology.md` + `han_viet_glossary.md` |
| Hỏi 1 sự việc cụ thể (đầu tư, hợp đồng, xin việc, tình cảm, Cát/Hung ngắn hạn) | `--mode iching` | `iching_liuyao_qimen_guide.md` + `han_viet_glossary.md` |
| Chọn giờ đẹp, phương hướng xuất hành/đàm phán, bố cục chiến lược thời–không | `--mode qimen` | `iching_liuyao_qimen_guide.md` |
| Hồ sơ Đại Toàn Thư 5 Hệ (Tử Vi + Bát Tự + Thần Số Học + Kinh Dịch + Kỳ Môn) | `--mode all` | Đọc trọn bộ tài liệu trong `references/` |

---

## 3. QUY TRÌNH THỰC THI 5 BƯỚC CHUẨN QUỐC TẾ

### Bước 1: Kiểm Tra Đầu Vào & Xử Lý Mơ Hồ (Input Gate)
- **Để xem Đông × Tây Toàn diện (`full`):** Cần **(1) Họ và tên khai sinh đầy đủ có dấu** (để mở khóa trọn vẹn Sứ mệnh, Linh hồn, Nhân cách & Chaldean), **(2) Ngày tháng năm sinh** (ghi rõ Dương lịch hay Âm lịch), **(3) Giờ phút sinh**, **(4) Giới tính** và ưu tiên **(5) Tỉnh/thành nơi sinh** (mặc định Hà Nội `105.85°E`).
- **Nếu thiếu Giờ sinh:** Vẫn chạy được ngay `--mode numerology` (100% độ chính xác trên Họ tên & Ngày sinh Dương lịch) kết hợp `--mode bazi` (3 trụ Năm–Tháng–Ngày)!
- **Nếu tư vấn Đặt tên con / Nghệ danh / Tên thương hiệu:** Truyền thêm `--nickname "Tên Dự Kiến"` hoặc dùng API `evaluate_candidate_names` để so sánh hàng loạt tên.

### Bước 2: Chạy Engine Định Danh (`scripts/huyenhoc_cli.py`)
Ưu tiên gọi từ `G:/My Drive/Antigravity/Skills/kb-tuvi/scripts/huyenhoc_cli.py` (đồng bộ tại `D:/AI/Skills/kb-tuvi/scripts/huyenhoc_cli.py`):

- **Lập Hồ sơ Hội Tụ Đông × Tây (Tử Vi × Bát Tự × Thần Số Học) + Xuất Báo Cáo HTML:**
  ```
  python -X utf8 "G:/My Drive/Antigravity/Skills/kb-tuvi/scripts/huyenhoc_cli.py" --mode full --name "Nguyễn Minh Quân" --nickname "Leo Quân" --solar 1992-08-16 --time 09:30 --gender nam --place "Hà Nội" --target-year 2026 --html-out "_temp/hoso_dongtay.html"
  ```

- **Xem Chuyên Sâu Thần Số Học Đa Phái (Không bắt buộc giờ sinh):**
  ```
  python -X utf8 "G:/My Drive/Antigravity/Skills/kb-tuvi/scripts/huyenhoc_cli.py" --mode numerology --name "Nguyễn Minh Quân" --nickname "Leo Quân" --solar 1992-08-16 --num-school vn --target-year 2026 --html-out "_temp/thansohoc.html"
  ```
  *(Tùy chọn `--num-school vn` giữ Số Chủ Đạo `10` theo Nhân số học VN; `--num-school intl` rút gọn 3 trụ theo chuẩn Quốc tế; engine luôn tự xuất kèm đối chiếu giữa 2 chuẩn).*

- **Gieo Quẻ Kinh Dịch Lục Hào + Mai Hoa / Bàn Kỳ Môn Độn Giáp:**
  ```
  python -X utf8 "G:/My Drive/Antigravity/Skills/kb-tuvi/scripts/huyenhoc_cli.py" --mode iching --question "Hỏi về thương vụ hợp tác quý tới" --iching-method coins_random --html-out "_temp/que_dich.html"
  ```

- **Khởi Chạy Web Studio GUI & Máy Chủ REST API Cho Dự Án Web (`gui_server.py`):**
  ```
  python -X utf8 "G:/My Drive/Antigravity/Skills/kb-tuvi/scripts/gui_server.py" --port 8765
  ```
  - Giao diện trực quan 6 Tab: **Lá Số Tử Vi SVG** • **Ngũ Hành Bát Tự** • **Thần Số Học & Công Cụ Chấm Điểm Đặt Tên** • **Quẻ Kinh Dịch** • **Kỳ Môn Hướng Tốt** • **Đông-Tây & Prompt AI**.
  - Các REST API mở sẵn CORS cho dự án Web: `POST /api/analyze`, `POST /api/numerology`, `POST /api/name-check`, `GET /sdk/numerology.js` (kèm thư viện độc lập `scripts/web_numerology_sdk.js` cho Next.js/React).

### Bước 3: Kiểm Tra Cảnh Báo Biên Giới Giờ Sinh & Đối Chiếu Trường Phái
- Với Tử Vi / Bát Tự: Kiểm tra `meta.branch_boundary_warning` và `bazi.late_zi_warning` — nếu khác `null`, thông báo ngay đầu bài để nghiệm lý giờ sinh.
- Với Thần Số Học: Kiểm tra `numerology.core_numbers.life_path.school_diff_note` — nếu khác `null` (VD: tổng `28` là Số `10` Nhân số học VN kiêm Số `1` Quốc tế), giải thích rõ sự kết hợp của cả hai tầng năng lượng.

### Bước 4: Đọc Tài Liệu Tham Chiếu & Phân Tích Đa Tầng Chuyên Sâu
Dùng `read_file` mở đúng cẩm nang trong `references/` theo Bảng Mục 2:
1. **Tử Vi (`tuvi_schools_and_patterns.md`):** Tiên thiên Mệnh–Thân–Cục, Cách cục Đối tinh Trung Châu, Tuần–Triệt trước/sau 30t, Phi Tinh Tứ Hóa, Đại hạn & Lưu niên.
2. **Bát Tự (`bazi_classics_methodology.md`):** Cường nhược Nhật Chủ (*Đắc lệnh – Đắc địa – Đắc thế*), Phù Ức + Điều Hầu (*Cùng Thông Bảo Giám*), Hợp/Xung/Hình/Hại với Đại vận.
3. **Thần Số Học & Giao Thoa Đông–Tây (`numerology_east_west_guide.md`):**
   - Giải mã **Tam Giác Vàng** (`Đường Đời – Sứ Mệnh – Linh Hồn`), **Nhân Cách**, **Số Trưởng Thành**, độ lệch **Cầu Nối Nội Tâm**.
   - Đọc **Biểu Đồ Ngày Sinh & Tổ Hợp 3×3**, các **Mũi Tên Đầy/Trống**, **Nợ Nghiệp (`13/4, 14/5, 16/7, 19/1`)** và chỉ ra **Họ tên đã lấp được những ô trống nào**.
   - Khớp **Kim Tự Tháp 4 Đỉnh Cao** với **Sóng Chu Kỳ 9 Năm Cá Nhân** (lưu ý hai đáy tích lũy nội lực năm `4` và `7`), rung động âm thanh **Chaldean** và **Ma trận 22 Arcana**.
   - Khi chạy `--mode full`: Thực hiện **Kiểm Chứng Chéo Đông × Tây** gắn nhãn `🟢 ĐỒNG THUẬN CAO` / `🟡 BỔ KHUYẾT CHÉO` / `🔴 PHÂN KỲ` giữa Dụng Thần Bát Tự, Đại Hạn Tử Vi và Năm Cá Nhân Thần Số Học.
4. **Kinh Dịch & Kỳ Môn (`iching_liuyao_qimen_guide.md`):** Dụng Thần Lục Hào, Nhật/Nguyệt, Tuần Không, Hào Động → Biến, Thế – Ứng và Ứng Kỳ.

### Bước 5: Trình Bày Kết Quả & Bàn Giao Hồ Sơ HTML
1. **Thông tin Định Danh & Đồng Bộ Đông–Tây** (Dương lịch, Giờ Chân Thái Dương, Âm lịch `UTC+7`, Tứ Trụ, Mệnh–Thân–Cục, Số Chủ Đạo & Năm Cá Nhân, link mở trực tiếp file HTML báo cáo).
2. **Tổng Quan Cốt Cách & Thiên Phú** (Cách cục Đông phương × Tam Giác Vàng Tây phương).
3. **Phân Tích Chuyên Sâu Theo Trục** (Sự nghiệp & Quản trị Tài chính / Tình cảm & Đối tác / Nội tâm & Bài học Chuyển hóa).
4. **Kiểm Chứng Chéo Đông × Tây & Bản Đồ Thời Vận Năm Xem** (kèm nhãn `🟢 / 🟡 / 🔴`).
5. **Chiến Lược Hành Động Thực Tiễn (Xu Cát Tỳ Hung)** (Nghề nghiệp tối ưu, phương hướng/ngũ hành bổ khuyết, thói quen rèn Mũi tên trống & gợi ý Tên gọi/Thương hiệu nếu có).
6. *Lưu ý văn hóa cuối bài: Mệnh lý phương Đông & Thần số học phương Tây là công cụ tham chiếu nhận thức bản thân và chiến lược nhân sinh, không thay thế quyết định y tế, pháp lý chuyên ngành.*
