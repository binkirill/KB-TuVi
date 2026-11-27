---
name: kb-tuvi
version: 2.0.0
description: Hệ thống Huyền Học & Mệnh Lý Tổng Hợp chuẩn Zero-Hallucination (Tử Vi Đẩu Số Đa Phái Việt Nam + Quốc tế iztro, Bát Tự Tứ Trụ 9 Cổ Thư, Kinh Dịch 64 Quẻ, Lục Hào Nạp Giáp, Mai Hoa Dịch Số & Kỳ Môn Độn Giáp Thời Gia). Tự động đổi lịch Vạn Niên thiên văn UTC+7, hiệu chỉnh Giờ Chân Thái Dương 63 tỉnh thành Việt Nam, kiểm chứng chéo Tử Vi × Bát Tự và xuất Lá Số / Mệnh Thư HTML sắc nét. Kích hoạt bất cứ khi nào người dùng hỏi xem tử vi, lập lá số, phân tích bát tự / tứ trụ, gieo quẻ kinh dịch / lục hào / mai hoa, kỳ môn độn giáp, xem vận hạn năm/tháng, chọn ngày giờ hướng tốt, nghiệm lý giờ sinh, hoặc gọi /kb-tuvi.
---

# ☯️ KB-TUVI — HỆ THỐNG HUYỀN HỌC & MỆNH LÝ TỔNG HỢP (ZERO-HALLUCINATION)

Skill này kết tinh kiến trúc tinh hoa nhất từ các kho mã nguồn huyền học hàng đầu thế giới (`jinchenma94/bazi-skill` 4.2k⭐, `SylarLong/iztro` 4.0k⭐, `FANzR-arch/Numerologist_skills` 2.2k⭐, `Linden-TR/ziwei-doushu-skill`, `dzcmemory-web/bazi-ziwei-skills`, `Johnson-Jia/liuyao-divination`) hòa quyện cùng đặc thù **Nam Phái Tử Vi & Lịch Vạn Niên `UTC+7` Việt Nam** (`Tuần – Triệt`, Vòng Thái Tuế, Bác Sĩ, tọa độ 63 tỉnh thành).

---

## 1. BA LUẬT SẮT BẮT BUỘC (IRON LAWS — TUYỆT ĐỐI KHÔNG VI PHẠM)

1. **LUẬT SỐ 1 — "CODE TÍNH TOÁN, AI LUẬN GIẢI" (ZERO MENTAL MATH):**
   - **CẤM 100%** tự nhẩm đổi lịch Dương ↔ Âm, tự nhẩm Tiết Khí, tự tính Can Chi Ngày/Giờ, tự an sao Tử Vi hay tự nạp giáp Lục Hào bằng trí nhớ ngôn ngữ của LLM.
   - **BẮT BUỘC** chạy script `scripts/huyenhoc_cli.py` trước khi phát biểu bất kỳ nhận định nào về lá số hay quẻ dịch. Kết quả JSON/HTML từ script là **Nguồn Sự Thật Duy Nhất (Single Source of Truth)**.
2. **LUẬT SỐ 2 — TUÂN THỦ TUYỆT ĐỐI CHÍNH SÁCH KASPERSKY / CẤM POWERSHELL:**
   - Chỉ gọi trực tiếp binary `python -X utf8` trên 1 dòng ngắn gọn trỏ vào `scripts/huyenhoc_cli.py`, **tuyệt đối không** dùng PowerShell cmdlets hay `python -c` inline phức tạp.
   - Mọi file JSON/HTML xuất tạm phải đặt gọn trong thư mục `_temp/` hoặc thư mục người dùng chỉ định.
3. **LUẬT SỐ 3 — TÁCH BẠCH HỆ THỐNG & CHỐNG ĐỘC ĐOÁN (ANTI-DOGMATISM):**
   - Khi phân tích độc lập từng hệ: **Không râu ông nọ cắm cằm bà kia** (đang phân tích thuần Tử Vi không lẫn "Thập Thần/Nhật Chủ"; đang phân tích thuần Bát Tự không lẫn "Cung Mệnh Vô Chính Diệu/Hóa Kỵ"). Chỉ đặt cạnh nhau tại mục **Kiểm Chứng Chéo (Cross-Validation)**.
   - **Cấm tuyệt đối** dùng ngôn từ hù dọa, định mệnh cực đoan (*"chắc chắn ly hôn"*, *"số tuyệt mạng"*, *"phá sản không cứu được"*). Luôn diễn đạt theo **xu hướng cấu trúc & xác suất**, chỉ rõ **cách chuyển hóa thực tế (Xu Cát Tỳ Hung)** như chọn nghề ứng sao, quản trị dòng tiền, khám sức khỏe định kỳ.

---

## 2. ĐỊNH TUYẾN CHẾ ĐỘ THEO NHU CẦU NGƯỜI DÙNG (INTENT ROUTING)

| Yêu cầu của người dùng | Chế độ `--mode` | Tài liệu `references/` cần đọc trước khi luận |
| :--- | :---: | :--- |
| Xem tổng quát cuộc đời, sự nghiệp, tài chính, hôn nhân, vận hạn năm (mặc định khuyên dùng!) | `--mode full` | Đọc `tuvi_schools_and_patterns.md` + `bazi_classics_methodology.md` + `han_viet_glossary.md` |
| Chỉ yêu cầu xem riêng Lá số Tử Vi (12 cung, chính phụ tinh, Tuần Triệt, Phi Tinh) | `--mode tuvi` | Đọc `tuvi_schools_and_patterns.md` + `han_viet_glossary.md` |
| Chỉ yêu cầu xem riêng Bát Tự / Tứ Trụ / Tử Bình / Khuyết Ngũ Hành | `--mode bazi` | Đọc `bazi_classics_methodology.md` + `han_viet_glossary.md` |
| Hỏi 1 sự việc cụ thể (đầu tư, hợp đồng, xin việc, tình cảm, tìm đồ, Cát/Hung ngắn hạn) | `--mode iching` | Đọc `iching_liuyao_qimen_guide.md` + `han_viet_glossary.md` |
| Chọn giờ đẹp, phương hướng xuất hành/đàm phán, bố cục chiến lược thời–không | `--mode qimen` | Đọc `iching_liuyao_qimen_guide.md` |
| Hồ sơ Đại Toàn Thư (vừa có ngày giờ sinh vừa hỏi quyết sách sự việc lớn ngay lúc này) | `--mode all` | Đọc cả 4 file trong `references/` |

---

## 3. QUY TRÌNH THỰC THI 5 BƯỚC CHUẨN QUỐC TẾ

### Bước 1: Kiểm Tra Đầu Vào & Xử Lý Mơ Hồ (Input Gate)
- **Để xem Tử Vi / Bát Tự (`full` / `tuvi` / `bazi`):** Cần tối thiểu **(1) Ngày tháng năm sinh** (ghi rõ Dương lịch hay Âm lịch), **(2) Giờ phút sinh** (hoặc canh giờ), **(3) Giới tính (Nam/Nữ)** và ưu tiên có **(4) Tỉnh/thành nơi sinh** (để hiệu chỉnh Giờ Chân Thái Dương, mặc định Hà Nội `105.85°E` nếu chưa rõ).
  - Nếu thiếu Giờ sinh: Có thể chạy `--mode bazi` (luận 3 trụ Năm–Tháng–Ngày) và giải thích rằng Tử Vi bắt buộc cần giờ sinh để định cung Mệnh (hoặc hỏi 2–3 biến cố quá khứ để dò giờ sinh).
- **Để gieo quẻ Kinh Dịch (`iching`):** Cần **Câu hỏi tập trung vào 1 việc cụ thể**. Nếu người dùng đã tự gieo xu/chọn số thì truyền `--iching-method manual_lines --lines ...` hoặc `--iching-method numbers --numbers ...`; nếu chưa có thì để engine gieo 3 đồng xu mật mã học (`--iching-method coins_random`) ngay tại thời điểm hỏi!

### Bước 2: Chạy Engine Định Danh (`scripts/huyenhoc_cli.py`)
Ưu tiên gọi từ `G:/My Drive/Antigravity/Skills/kb-tuvi/scripts/huyenhoc_cli.py` (hoặc bản đồng bộ tại `D:/AI/Skills/kb-tuvi/scripts/huyenhoc_cli.py`):

- **Lập Hồ sơ Song Hệ Tử Vi × Bát Tự + Xuất Lá Số HTML:**
  ```
  python -X utf8 "G:/My Drive/Antigravity/Skills/kb-tuvi/scripts/huyenhoc_cli.py" --mode full --name "Tên" --solar 1992-08-16 --time 09:30 --gender nam --place "Hà Nội" --target-year 2026 --html-out "_temp/laso_menhthu.html"
  ```
  *(Nếu người dùng đưa ngày Âm lịch, thay `--solar YYYY-MM-DD` bằng `--lunar YYYY-MM-DD` và thêm `--leap` nếu là tháng nhuận).*

- **Gieo Quẻ Kinh Dịch Lục Hào + Mai Hoa:**
  ```
  python -X utf8 "G:/My Drive/Antigravity/Skills/kb-tuvi/scripts/huyenhoc_cli.py" --mode iching --question "Hỏi về thương vụ hợp tác quý tới" --iching-method coins_random --html-out "_temp/que_dich.html"
  ```
  *(Hoặc truyền 6 hào từ hào 1 lên hào 6 với `6`=Lão Âm động, `7`=Thiếu Dương, `8`=Thiếu Âm, `9`=Lão Dương động: `--iching-method manual_lines --lines 7,8,9,7,6,8`; hoặc Mai Hoa số: `--iching-method numbers --numbers 16,28,5`).*

- **Lập Bàn Kỳ Môn Độn Giáp Thời Gia:**
  ```
  python -X utf8 "G:/My Drive/Antigravity/Skills/kb-tuvi/scripts/huyenhoc_cli.py" --mode qimen --solar 2026-11-27 --time 09:30 --question "Đàm phán ký kết hợp đồng" --html-out "_temp/kymon.html"
  ```

- **Khởi Chạy Giao Diện Đồ Họa Tương Tác (`KB-TUVI STUDIO GUI` — `react-iztro` × `YiSphere` style):**
  Khi người dùng muốn mở giao diện trực quan để tự click từng cung xem tia nối *Tam Phương Tứ Chính*, *Phi Tinh Tứ Hóa*, tự tung 3 đồng xu Lục Hào hoặc xuất PDF:
  ```
  python -X utf8 "G:/My Drive/Antigravity/Skills/kb-tuvi/scripts/gui_server.py" --port 8765
  ```
  *(Hỗ trợ tùy chọn đồng bộ quốc tế trên cả CLI và GUI: `--calendar-std vn|intl`, `--tuvi-school iztro|vn`, `--zi-sect 1|2`).*

### Bước 3: Kiểm Tra Cảnh Báo Biên Giới Giờ Sinh (`branch_boundary_warning` & `late_zi_warning`)
- Đọc kỹ trường `meta.branch_boundary_warning` và `bazi.late_zi_warning` từ output JSON:
  - Nếu `branch_boundary_warning` khác `null` (Giờ Đồng Hồ và Giờ Chân Thái Dương khác canh giờ) HOẶC sinh từ `23:00–23:59` (Dạ Tý): **Bắt buộc thông báo ngay đầu bài phân tích** và đưa ra 2–3 đặc điểm nhận diện ngoại hình/tính cách/biến cố của từng canh giờ để người dùng nghiệm lý xác nhận!

### Bước 4: Đọc Tài Liệu Tham Chiếu & Phân Tích Đa Tầng Chuyên Sâu
Dùng `read_file` mở đúng file hướng dẫn trong `references/` (theo Bảng Mục 2) để đối chiếu cổ pháp, tuyệt đối dùng thuật ngữ Hán–Việt chuẩn:

1. **Khi luận Tử Vi Đẩu Số (`tuvi_schools_and_patterns.md`):**
   - **Tầng Tiên Thiên:** Mệnh – Thân – Cục, Âm Dương Thuận/Nghịch lý, vị thế Vòng Thái Tuế.
   - **Tầng Cách Cục & Tam Phương Tứ Chính:** Phân tích cặp Đối Tinh theo Trung Châu Phái (ví dụ Thiên Phủ *Thực Khố vs Không Khố*, Thiên Tướng *Tài Ấm vs Hình Kỵ Giáp Ấn*), Lục Cát / Lục Sát, Giáp Cung và tác động lật ngược/chiết giảm của **Tuần – Triệt** theo độ tuổi trước & sau 30.
   - **Tầng Phi Tinh Tứ Hóa:** Giải mã đường đi của Sinh Niên Lộc – Quyền – Khoa – Kỵ và `flying_sihua` giữa Mệnh – Tài – Quan – Điền – Phu.
   - **Tầng Vận Hạn:** Khớp Đại Hạn 10 năm hiện tại (`active_dai_han`) + Lưu Niên Mệnh + Tiểu Hạn + Lưu Niên Tứ Hóa của `target_year`.

2. **Khi luận Bát Tự Tứ Trụ (`bazi_classics_methodology.md`):**
   - Định Cường Nhược Nhật Chủ qua *Đắc Lệnh – Đắc Địa (Tàng Can) – Đắc Thế*.
   - Phối hợp **Phù Ức Dụng Thần** với **Điều Hầu Dụng Thần (*Cùng Thông Bảo Giám*)** và **Thông Quan** để chốt Hỷ/Dụng/Kỵ Thần thực chất (không bao giờ chỉ đếm số lượng Ngũ hành bề nổi kiểu "thiếu gì bù nấy"!).
   - Giải mã Hợp/Xung/Hình/Hại giữa Tứ Trụ gốc với Đại Vận & Lưu Niên.

3. **Khi chạy Song Hệ (`--mode full`) — Kiểm Chứng Chéo (Cross-Validation):**
   Gắn nhãn độ tin cậy rõ ràng cho từng kết luận lớn:
   - `🟢 ĐỒNG THUẬN CAO`: Cả Tử Vi và Bát Tự cùng xác nhận một xu hướng (ví dụ Đại Vận Bát Tự đắc Hỷ Dụng Tài Tinh + Đại Hạn Tử Vi đắc Song Lộc/Lộc Mã).
   - `🟡 BÁN ĐỒNG THUẬN`: Một hệ báo thuận lợi cơ hội, một hệ báo áp lực/hao tổn (thành tựu đi kèm điều kiện quản trị rủi ro).
   - `🔴 PHÂN KỲ`: Hai hệ trái ngược nhau — nhắc kiểm tra lại độ chính xác phút sinh hoặc phân biệt *biểu hiện bên ngoài (Tử Vi)* vs *nội lực thực chất (Bát Tự)*.

4. **Khi giải quẻ Kinh Dịch / Kỳ Môn (`iching_liuyao_qimen_guide.md`):**
   - Chỉ đích danh **Dụng Thần**, xét sức mạnh dưới **Nguyệt Kiến & Nhật Thần**, kiểm tra **Tuần Không (Chân Không vs Giả Không)**, **Ám Động / Nguyệt Phá**, **Hào Động → Hào Biến** (Hồi đầu sinh/khắc, Tiến/Thoái thần), tương quan **Thế – Ứng** và chốt **Ứng Kỳ (thời điểm ứng nghiệm dự kiến)**.

### Bước 5: Trình Bày Kết Quả & Bàn Giao Lá Số HTML
Cấu trúc bài trả lời rõ ràng, sang trọng và dễ ứng dụng:
1. **Thông tin Định Danh & Hiệu Chỉnh Thời Gian** (Dương lịch, Giờ Chân Thái Dương, Âm lịch `UTC+7`, Tứ Trụ, Mệnh – Thân – Cục, link mở trực tiếp file Lá Số HTML đã tạo).
2. **Tổng Quan Cốt Cách & Điểm Mạnh Thiên Phú** (Cách cục nổi bật nhất).
3. **Phân Tích Chi Tiết Theo Trục Trọng Tâm** (Sự nghiệp & Quản trị Tài sản / Hôn nhân & Đối tác / Sức khỏe & Tâm thức).
4. **Bảng Kiểm Chứng Chéo & Dự Báo Vận Hạn Giai Đoạn Tới** (kèm nhãn `🟢 / 🟡 / 🔴` và các mốc năm/tháng then chốt).
5. **Chiến Lược Hành Động Thực Tiễn (Xu Cát Tỳ Hung)** (Ngành nghề/vai trò tối ưu, phương hướng/màu sắc/thói quen bổ khuyết Dụng thần, nguyên tắc đầu tư & giao tiếp).
6. *Dòng lưu ý văn hóa ngắn gọn cuối bài: Mệnh lý & Dịch học là bộ công cụ tham chiếu chiến lược nhân sinh, không thay thế quyết định y tế, pháp lý chuyên ngành.*
