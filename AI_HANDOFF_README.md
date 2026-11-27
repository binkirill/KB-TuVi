# 📋 AI_HANDOFF_README — HỒ SƠ TIẾP QUẢN DỰ ÁN `KB-TUVI` (v3.0 Scroll-Craft Edition)

Tài liệu bàn giao chuẩn hóa giúp bất kỳ phiên hội thoại / mô hình AI mới nào đọc vào là nắm trọn 100% kiến trúc, thông số đã khóa và tiếp quản công việc ngay lập tức mà không phải dò lại từ đầu.

---

## 1. Thời Điểm Cập Nhật & Trạng Thái Hiện Tại
- **Thời điểm cập nhật:** `2026-11-27 11:33 (UTC+7)`
- **Trạng thái dừng:** **ĐÃ HOÀN TẤT NÂNG CẤP GIAO DIỆN `SCROLL-CRAFT` + FORM NHẬP THÔNG TIN (NICKNAME & 4 CHẾ ĐỘ GIEO QUẺ KINH DỊCH) VÀ ĐẨY BẢN MỚI NHẤT LÊN GITHUB/VERCEL.**
- **Thư mục Nguồn Sự Thật Duy Nhất (Single Source of Truth):**
  - Bản gốc chỉnh sửa chính: `G:\My Drive\Antigravity\Skills\kb-tuvi\`
  - Bản đồng bộ nạp Skill hệ thống: `D:\AI\Skills\kb-tuvi\`
  - Bản đồng bộ Web / Vercel (`https://kb-tu-vi.vercel.app`): `G:\My Drive\Antigravity\kb-tuvi-web\`
- **Máy chủ Localhost kiểm thử:** `http://127.0.0.1:8765` (chạy qua `scripts/gui_server.py`).

---

## 2. Checklist Tiến Độ (`[x]` Đã Hoàn Thành — Cấm Làm Lại | `[ ]` Mở Rộng Tiếp Theo)

### Đã hoàn thành 100% (`[x]`)
- `[x]` **Bộ chỉ thị trung tâm Skill v3.0:** `SKILL.md` (định tuyến 7 chế độ `full`, `numerology`, `tuvi`, `bazi`, `iching`, `qimen`, `all`).
- `[x]` **Engine Thiên Văn & Lịch Vạn Niên `UTC+7`:** `scripts/core_calendar.py` (Jean Meeus + Hồ Ngọc Đức, 24 Tiết khí chính xác đến phút theo `JD_UT`, Giờ Chân Thái Dương cho đủ **63/63 tỉnh thành Việt Nam**).
- `[x]` **Engine Tử Vi Đẩu Số Đa Phái:** `scripts/engine_tuvi.py` (12 cung, >105 sao khớp 100% `SylarLong/iztro`, Quốc Ấn/Đường Phù/Thiên Thương/Thiên Sứ/Nguyệt Giải/Đẩu Quân, **Tuần – Triệt chuẩn Việt Nam**, Phi Tinh Tứ Hóa 12 cung, Đại hạn/Tiểu hạn/Lưu niên, quét Cách cục tự động).
- `[x]` **Engine Bát Tự Tứ Trụ 9 Cổ Thư:** `scripts/engine_bazi.py` (khóa `JD_UT` cho Lập Xuân & 12 Tiết, tách bạch Giờ Mặt Trời cho Ngày/Giờ, Thập Thần, Tàng Can, Thần Sát, Đại Vận, Dụng Thần kép *Phù Ức + Cùng Thông Bảo Giám*).
- `[x]` **Engine Thần Số Học Đa Phái & Web SDK:** `scripts/engine_numerology.py` & `scripts/web_numerology_sdk.js` (Nhân số học VN Số `10` + Pythagoras Quốc tế, Chaldean cổ đại chấm điểm tên gọi/thương hiệu, Biểu đồ 3×3 & 15 Mũi tên, 4 Đỉnh cao, Sóng 9 năm cá nhân, Ma trận Định mệnh 22 Arcana).
- `[x]` **Engine Kinh Dịch Toàn Diện:** `scripts/engine_iching.py` (64 Quẻ Chu Dịch chuẩn thứ tự hào dưới lên trên, Lục Hào Nạp Giáp Kinh Phòng, Thế/Ứng, Phục Thần, Ám Động/Nguyệt Phá, Mai Hoa Thể–Dụng & Kỳ Môn Độn Giáp Thời Gia Cửu Cung).
- `[x]` **Trạm Luận Giải AI Gemini Độc Lập:** `scripts/gemini_interpreter.py` & plugin frontend không xâm lấn `assets/gemini_ai_addon.js` (hỗ trợ cả Key máy chủ có Mã mời lẫn chế độ BYOK cá nhân).
- `[x]` **Giao diện Web Studio chuẩn `nateherkai/scroll-craft`:** `assets/studio_gui.html` + `scripts/render_chart_html.py` + `scripts/gui_server.py`:
  - Kiến trúc cuộn 4 Hồi (*Dimensional Hero 3 lớp parallax + vòng tinh bàn xoay theo cuộn* → *Tam Đại Cao Nhân Trấn Sơn* → *Điện Khai Mệnh 1 khung nhập duy nhất* → *Chân trang bản quyền*).
  - Đã nhúng đủ **6 bức ảnh mỹ thuật & nhân vật** trong `assets/images/`:
    - 3 tranh AI Đông Phương thếp vàng: `assets/images/hero_celestial.jpg`, `assets/images/five_elements.jpg`, `assets/images/iching_oracle.jpg`.
    - 3 ảnh PNG tách nền từ `Downloads` của hội: `assets/images/user_photo_1.png`, `assets/images/user_photo_2.png`, `assets/images/user_photo_3.png`.
- `[x]` **Kho Cổ Thư Tham Chiếu (`references/`):** `tuvi_schools_and_patterns.md`, `bazi_classics_methodology.md`, `iching_liuyao_qimen_guide.md`, `numerology_east_west_guide.md`, `han_viet_glossary.md`.
- `[x]` **Công cụ Đồng bộ 3 chiều (`Skill gốc -> D:\AI -> kb-tuvi-web`):** `G:\My Drive\Antigravity\kb-tuvi-web\sync_from_skill.py` (đã nâng cấp đồng bộ đệ quy cả `assets/images/` và `public/assets/images/` cho Vercel CDN).
- `[x]` **Nâng cấp Khung Nhập Thông Tin & Kinh Dịch (`assets/studio_gui.html`):**
  - Đổi nhãn `Tên gọi / Thương hiệu` → **`Nickname`** (tùy chọn).
  - Làm rõ nhãn **`Việc cần hỏi thêm (Xem quẻ Kinh Dịch — không bắt buộc)`**.
  - Khôi phục & nâng cấp trọn bộ 4 lựa chọn **Cách gieo quẻ Kinh Dịch**: (1) *Hệ thống gieo hộ (3 đồng xu tự động)*, (2) *Tự gieo 3 đồng xu (6 lần) / Nhập kết quả* (hỗ trợ cả tung xu trên web, 4 nút chọn nhanh kết quả 3 xu thật ngoài đời `3 Sấp (6)` / `2 Sấp 1 Ngửa (7)` / `1 Sấp 2 Ngửa (8)` / `3 Ngửa (9)` và ô gõ tay 6 hào), (3) *Chọn 2 số yêu thích (Mai Hoa Dịch Số)* kèm số thứ 3 tùy chọn + nút lấy ngẫu nhiên, và (4) *Gieo theo ngày giờ hiện tại*.
- `[x]` **Xuất bản lên GitHub & Vercel (`https://kb-tu-vi.vercel.app`):** Đã chạy kiểm thử tự động PASS 100% (`sync_from_skill.py --push`) đẩy toàn bộ bản `v3.0 Scroll-Craft` + 6 ảnh + form Kinh Dịch mới lên `origin/main`.

### Các hướng có thể triển khai tiếp theo yêu cầu anh (`[ ]`)
- `[ ]` Tinh chỉnh câu chữ / danh hiệu của 3 thẻ *Tam Đại Cao Nhân* hoặc bổ sung thêm thành viên mới của **Hội BĐS Đồ Sơn** nếu anh muốn.
- `[ ]` Mở rộng thêm tính năng chuyên biệt cho BĐS (ví dụ: Tab *Xem Tuổi Mua Nhà / Động Thổ / Hướng Đất Hợp Mệnh Bát Trạch* tích hợp thẳng cho anh em Hội BĐS Đồ Sơn).

---

## 3. Các Thông Số & Quy Chuẩn Đã Khóa Cứng (Bắt Buộc Giữ Nguyên)

1. **Chân trang Bản quyền Chính chủ (Cả trên Web lẫn File HTML xuất về):**
   - Chuỗi bắt buộc: **`❤️ From K.B - Hội BĐS Đồ Sơn ❤️`**
2. **Quy tắc UX cho Người Dùng Phổ Thông Việt Nam:**
   - Cột nhập liệu bên trái **chỉ giữ DUY NHẤT 1 khung `👤 Thông Tin Đương Số`** gọn dễ hiểu (đưa `Hải Phòng` lên đầu danh sách 63 tỉnh thành).
   - **TUYỆT ĐỐI KHÔNG** phơi các thuật ngữ kỹ thuật rối rắm như `UTC+7`, `UTC+8`, `EoT`, `Giờ Chân Thái Dương`, `Sect 1 / Sect 2`, `Càn Tạo / Khôn Tạo` ra mặt tiền giao diện. Mọi hiệu chỉnh giờ Mặt Trời theo tỉnh thành đều tự chạy ngầm (`use_true_solar: true`, `calendar_std: "vn"`, `tuvi_school: "iztro"`, `zi_sect: 2`).
   - Khi mới mở trang không tự động nạp sẵn lá số năm 1990 gây hiểu nhầm (chỉ nạp khi người dùng bấm nút *Xem thử 1 lá số mẫu* hoặc tự nhập ngày sinh).
3. **Bảo toàn Hook của Plugin Gemini AI (`assets/gemini_ai_addon.js`):**
   - Trong `assets/studio_gui.html` luôn phải giữ thẻ `<script src="/api/addon"></script>` ngay trước `</body>`, biến `window.STATE = STATE`, class `.sidebar .btn-primary`, `.toolbar-right`, `#pane-ai` và hàm `window.renderAiPane` / `window.downloadHtmlReport`.
4. **Chính sách Kaspersky & Cấm PowerShell Tuyệt Đối (ZERO TOLERANCE):**
   - **Cấm 100%** gọi `powershell`, `pwsh`, `.ps1`, cmdlets hoặc `python -c` inline phức tạp.
   - Mọi script kiểm tra/tự động hóa phải lưu ra file `.py` trước rồi chạy 1 dòng ngắn: `python -X utf8 "duong_dan_script.py"`.

---

## 4. Lệnh Vận Hành Nhanh Cho Agent Tiếp Quản

- **Chạy thử giao diện Localhost (`http://127.0.0.1:8765`):**
  ```
  python -X utf8 "G:/My Drive/Antigravity/Skills/kb-tuvi/scripts/gui_server.py" --port 8765
  ```
- **Đồng bộ từ Bản Gốc sang `D:\AI\Skills\kb-tuvi` và `kb-tuvi-web` (chỉ kiểm thử local, chưa push):**
  ```
  python -X utf8 "G:/My Drive/Antigravity/kb-tuvi-web/sync_from_skill.py"
  ```
- **Đồng bộ VÀ đẩy thẳng lên Web Vercel (`https://kb-tu-vi.vercel.app`) khi anh yêu cầu:**
  ```
  python -X utf8 "G:/My Drive/Antigravity/kb-tuvi-web/sync_from_skill.py" --push -m "Update scroll-craft UI & Hoi BDS Do Son branding"
  ```

---

## 5. Resume Prompt Mẫu (Copy Dán Vào Hội Thoại Mới Là Làm Tiếp Được Ngay)

```text
Đọc ngay file bàn giao G:\My Drive\Antigravity\Skills\kb-tuvi\AI_HANDOFF_README.md và G:\My Drive\Antigravity\Skills\kb-tuvi\SKILL.md để nắm toàn bộ trạng thái dự án KB-TUVI v3.0 (bản giao diện scroll-craft của Hội BĐS Đồ Sơn). Không làm lại các mục [x] đã hoàn thành, tuân thủ nghiêm ngặt luật cấm PowerShell, và thực hiện yêu cầu tiếp theo của anh: [NHẬP YÊU CẦU MỚI CỦA ANH TẠI ĐÂY — VD: đẩy bản mới lên Vercel / sửa danh hiệu 3 ảnh cao nhân / thêm tab Phong thủy Bát trạch xem hướng đất...]
```
