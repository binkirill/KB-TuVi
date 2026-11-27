# 📋 AI_HANDOFF_README — HỒ SƠ TIẾP QUẢN DỰ ÁN `KB-TUVI` (v3.4 Kuang Bin Studio · Scroll-Craft Edition)

Tài liệu bàn giao chuẩn hóa giúp bất kỳ phiên hội thoại / mô hình AI mới nào đọc vào là nắm trọn 100% kiến trúc, thông số đã khóa và tiếp quản công việc ngay lập tức mà không phải dò lại từ đầu.

---

## 1. Thời Điểm Cập Nhật & Trạng Thái Hiện Tại
- **Thời điểm cập nhật:** `2026-11-27 12:45 (UTC+7)`
- **Trạng thái dừng:** **ĐÃ NÂNG CẤP KUANG BIN STUDIO v3.4: THAY ẢNH Ô 3 BẰNG `guide_3_lgbt.jpg` (TỪ `3.png` TRONG DOWNLOAD MAKE-UP CẦU VỒNG LGBT) + THU NHỎ 3 KHUNG ẢNH GỌN VÀO TRUNG TÂM (`max-width: 820px`) + HIỆU ỨNG Ô ẢNH HƠI MỜ KHI NGHỈ, RÊ CHUỘT VÀO MỚI RÕ NÉT & CHẠY ANIMATION + KHẮC PHỤC TRIỆT ĐỂ FONT TIẾNG VIỆT BẰNG `Be Vietnam Pro` + VÍ DỤ NICKNAME VUI NHỘN (`Dủng Dỉnh, Sâm Héo, Hoàng Mười, Hải Ly...`) + HIỆU ỨNG CHIỀU SÂU `/scroll-craft` (MULTI-PLANE POINTER PARALLAX, SPOTLIGHT, MAGNET, ASTROLABE WHEEL THEO CUỘN TRANG) & ĐỒNG BỘ LÊN GITHUB/VERCEL.**
- **Thư mục Nguồn Sự Thật Duy Nhất (Single Source of Truth):**
  - Bản gốc chỉnh sửa chính: `G:\My Drive\Antigravity\Skills\kb-tuvi\`
  - Bản đồng bộ nạp Skill hệ thống: `D:\AI\Skills\kb-tuvi\`
  - Skill `scroll-craft` đã tích hợp độc lập: `G:\My Drive\Antigravity\Skills\scroll-craft\` & `D:\AI\Skills\scroll-craft\`
  - Bản đồng bộ Web / Vercel (`https://kb-tu-vi.vercel.app`): `G:\My Drive\Antigravity\kb-tuvi-web\`
- **Máy chủ Localhost kiểm thử:** `http://127.0.0.1:8765` (chạy qua `scripts/gui_server.py`).

---

## 2. Checklist Tiến Độ (`[x]` Đã Hoàn Thành — Cấm Làm Lại | `[ ]` Mở Rộng Tiếp Theo)

### Đã hoàn thành 100% (`[x]`)
- `[x]` **Tích hợp trọn bộ Skill `nateherkai/scroll-craft`:** Đã cài đặt nguyên bản (`SKILL.md`, `engine/scrollcraft.js`, `engine/scrollcraft.css`, `references/*`, `scripts/*`, `templates/*`) vào cả `G:\My Drive\Antigravity\Skills\scroll-craft\` và `D:\AI\Skills\scroll-craft\`.
- `[x]` **Bộ chỉ thị trung tâm Skill v3.0 & 5 Engine tính toán chuẩn Zero-Hallucination:** `SKILL.md`, `scripts/core_calendar.py`, `scripts/engine_tuvi.py`, `scripts/engine_bazi.py`, `scripts/engine_numerology.py`, `scripts/web_numerology_sdk.js`, `scripts/engine_iching.py`, `scripts/gemini_interpreter.py`, `assets/gemini_ai_addon.js`, và kho cổ thư `references/`.
- `[x]` **Bộ ảnh minh họa Gen-Z Huyền Học mới + Make-up vui tươi 3 ảnh đại diện (`assets/images/`):**
  - `assets/images/bg_mystic_pattern.jpg`: Ảnh nền sáng màu kem ngọc trai vẽ hoa văn vân mây cát tường, hoa sen, nhật nguyệt & vòng tinh bàn vàng champagne tinh xảo.
  - `assets/images/hero_genz_sky.jpg` & `assets/images/elements_genz_banner.jpg`: Trời mây pastel & 5 bùa Ngũ Hành hiện đại.
  - `assets/images/guide_1_cool.jpg`: Make-up từ `user_photo_1.png` (Nam Thần Tử Vi & Tài Lộc).
  - `assets/images/guide_2_cheer.jpg`: Make-up từ `user_photo_2.png` (Nam Thần Gieo Quẻ).
  - `assets/images/guide_3_lgbt.jpg`: Make-up từ `C:\Users\Quang\Downloads\3.png` (nhân vật áo đen JUMP tô son đỏ bấm điện thoại, xóa sạch timestamp góc phải dưới, bọc viền sticker kem trắng trên nền cầu vồng 7 màu, trái tim LGBT & tinh bàn Thần Số Học).
  - *(Giữ nguyên các ảnh cũ `hero_celestial.jpg`, `five_elements.jpg`, `iching_oracle.jpg`, `guide_3_love.jpg`, `user_photo_1..3.png` để bảo toàn tương thích ngược 100%).*
- `[x]` **Thiết kế giao diện Kuang Bin Studio v3.4 chuẩn `scroll-craft` (`assets/studio_gui.html` + `assets/scrollcraft/scrollcraft.css` & `scrollcraft.js`):**
  - **Typography Tiếng Việt Sắc Nét Tuyệt Đối:** Chuyển toàn bộ tiêu đề tiếng Việt, nút bấm (`Click mở khung Tử Vi`, `Click mở khung Gieo Quẻ`, `Click mở Thần Số Học`), nhãn & nội dung sang **`Be Vietnam Pro`** (`letter-spacing: 0`, không dùng `preserve-3d` hay `backdrop-filter` làm nhòe bitmap chữ tiếng Việt), giữ `Baloo 2` cho logo chữ Latin `Kuang Bin Studio`.
  - **Bố cục 3 Khung Ảnh Thu Nhỏ Gọn Giữa Tâm & Hover Focus-Reveal:**
    - Gom cụm `.guides-grid` vào trung tâm (`max-width: 820px; margin-inline: auto; gap: 1.15rem;`), tỷ lệ khung gọn gàng vừa tầm mắt trên mọi màn hình laptop/PC.
    - Mặc định khi chưa rê chuột (desktop fine pointer): 3 ô ảnh hơi mờ nhẹ (`opacity: 0.68; filter: blur(1.3px) saturate(0.76);`) và **tạm dừng toàn bộ animation** (`animation-play-state: paused`). Khi rê chuột vào ô nào, ô đó lập tức rõ nét 100% (`opacity: 1; filter: none`), nổi bật lên và kích hoạt đồng bộ vòng hào quang xoay, bùa lắc lư, sao lấp lánh, tia sáng lướt qua ảnh và mũi tên nhấp nháy.
  - **Hiệu ứng Chiều Sâu `/scroll-craft` Nâng Cao:**
    - Multi-plane pointer parallax (`--mx`, `--my` nội suy mượt `0.08` trên `requestAnimationFrame`) dịch chuyển đa lớp giữa tầng Mandala sâu (`-24px`), tầng bùa nổi (`+18px`) và vầng hào quang sân khấu 3 thẻ (`guides-stage-aura`).
    - Tích hợp `data-sc-spotlight` quét vầng sáng theo chuột trên khung nhập liệu & thẻ chào mừng, `data-sc-magnet="0.22"` hút nhẹ nút điều hướng đầu trang, `data-sc-stagger="90"` xuất hiện tuần tự, thanh tiến trình cuộn 7 màu (ở chế độ 3) và bánh xe tinh bàn `.astrolabe-wheel` xoay đồng bộ theo độ cuộn trang (`--sc-scroll-deg`).
  - **Kịch bản Bật Lò Xo + Pháo Hoa Liên Tục / Mưa Tim 7 Màu LGBT (Click Mới Thu Nhỏ) & 3 Bộ Form Chuyên Biệt:**
    - Ô 1 (`thuc-chien`): Hiện 100% trường bắt buộc Tử Vi / Tài Bạch / Điền Trạch (không giấu trong thu gọn), bắn pháo hoa liên tục.
    - Ô 2 (`gieo-que`): Ẩn Họ tên & Ngày sinh, cung cấp 6 phương pháp khởi quẻ Kinh Dịch đa dạng, bắn pháo hoa liên tục.
    - Ô 3 (`tinh-duyen`): Nhân vật LGBT (`Bà Hoàng Thần Số Học 🏳️‍🌈💅`), bắn mưa trái tim 7 màu cầu vồng bay lung tung khắp màn hình, giải thích rõ **Ngày sinh + Tên thật + Nickname**, tích hợp sẵn bộ ví dụ & chip chọn nhanh **`Dủng Dỉnh, Sâm Héo, Hoàng Mười, Hải Ly...`** ở cả ô nhập Nickname lẫn bàn chấm điểm Nickname cuối trang.
- `[x]` **Nâng cấp `gui_server.py`, `sync_from_skill.py`, `gemini_interpreter.py` & `gemini_ai_addon.js` (v3.4.1):**
  - Tự phục vụ và đồng bộ đầy đủ `/assets/scrollcraft/*` & `/assets/images/*` sang `public/assets/` cho Vercel CDN.
  - Tự động đọc cả `GEMINI_API_KEY` lẫn `GOOGLE_API_KEY` (lọc dấu nháy thừa), gỡ bỏ tham số `temperature` đã deprecated trên dòng model `gemini-3.*` (`gemini-3.8-flash`, `gemini-3.6-flash`, `gemini-3.5-flash-lite`), và hiển thị trực tiếp hộp trạng thái `🟢 Đã nhận Gemini API Key trên Server` kèm ô nhập nhanh `ACCESS_CODE` (nếu có bật trên Vercel) ngay dưới nút AI ở cột trái.

### Các hướng có thể triển khai tiếp theo yêu cầu anh (`[ ]`)
- `[ ]` Bổ sung hiệu ứng âm thanh vui nhộn nhẹ (tiếng pháo nổ / tiếng lắc xu, có nút bật/tắt) nếu anh muốn.
- `[ ]` Tích hợp thêm tính năng check độ hợp đôi hoặc Tab Xem Tuổi Mua Nhà / Hướng Đất Bát Trạch cho Hội BĐS Đồ Sơn.

---

## 3. Các Thông Số & Quy Chuẩn Đã Khóa Cứng (Bắt Buộc Giữ Nguyên)

1. **Chân trang Bản quyền Chính chủ:** **`❤️ From K.B - Hội BĐS Đồ Sơn ❤️`**
2. **UX Phổ thông + Gen-Z:** Giữ `Hải Phòng` đầu danh sách 63 tỉnh thành, ẩn tuyệt đối thuật ngữ kỹ thuật (`UTC+7`, `EoT`, `Giờ Chân Thái Dương`, `Sect 1/2`), không tự nạp lá số 1990 khi mới mở trang.
3. **Hook Plugin Gemini AI (`assets/gemini_ai_addon.js`):** Giữ `<script src="/api/addon"></script>`, `window.STATE = STATE`, `.sidebar .btn-primary`, `.toolbar-right`, `#pane-ai`, `window.renderAiPane`, `window.downloadHtmlReport`.
4. **Chính sách Kaspersky & Cấm PowerShell Tuyệt Đối (ZERO TOLERANCE):** Không dùng PowerShell/cmdlets/inline phức tạp; mọi script lưu file `.py` chạy `python -X utf8`.

---

## 4. Lệnh Vận Hành Nhanh Cho Agent Tiếp Quản

- **Chạy thử Localhost (`http://127.0.0.1:8765`):**
  ```
  python -X utf8 "G:/My Drive/Antigravity/Skills/kb-tuvi/scripts/gui_server.py" --port 8765
  ```
- **Đồng bộ & đẩy thẳng lên Vercel (`https://kb-tu-vi.vercel.app`):**
  ```
  python -X utf8 "G:/My Drive/Antigravity/kb-tuvi-web/sync_from_skill.py" --push -m "v3.4 Kuang Bin Studio update"
  ```

---

## 5. Resume Prompt Mẫu

```text
Đọc ngay file bàn giao G:\My Drive\Antigravity\Skills\kb-tuvi\AI_HANDOFF_README.md và G:\My Drive\Antigravity\Skills\kb-tuvi\SKILL.md để tiếp quản dự án KB-TUVI v3.4 (Kuang Bin Studio chuẩn scroll-craft với 3 nhân vật đại diện 3 phong cách xem). Giữ nguyên mọi mục [x] đã hoàn thành, tuân thủ nghiêm ngặt luật cấm PowerShell, và thực hiện yêu cầu tiếp theo của anh: [NHẬP YÊU CẦU MỚI]
```
