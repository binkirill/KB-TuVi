# 📋 AI_HANDOFF_README — HỒ SƠ TIẾP QUẢN DỰ ÁN `KB-TUVI` (v3.1 Gen-Z Playful Mystic Scroll-Craft)

Tài liệu bàn giao chuẩn hóa giúp bất kỳ phiên hội thoại / mô hình AI mới nào đọc vào là nắm trọn 100% kiến trúc, thông số đã khóa và tiếp quản công việc ngay lập tức mà không phải dò lại từ đầu.

---

## 1. Thời Điểm Cập Nhật & Trạng Thái Hiện Tại
- **Thời điểm cập nhật:** `2026-11-27 12:13 (UTC+7)`
- **Trạng thái dừng:** **ĐÃ NÂNG CẤP KB-TUVI v3.2: HIỆU ỨNG NAM THẦN BẬT LÒ XO + PHÁO BÔNG HÀI HƯỚC RỒI THU NHỎ KHI CLICK + TÁCH RIÊNG 3 BỘ FORM CHUYÊN BIỆT CHO (1) TỬ VI/TÀI BẠCH, (2) GIEO QUẺ 6 KIỂU, (3) THẦN SỐ HỌC TÊN THẬT × NICKNAME, VÀ ĐẨY LÊN GITHUB/VERCEL.**
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
  - `assets/images/hero_genz_sky.jpg`: Nền trời mây pastel ngọc trai + vòng tinh bàn vàng champagne sáng thoáng (Risograph-gouache).
  - `assets/images/elements_genz_banner.jpg`: 5 bùa Ngũ Hành (Kim–Mộc–Thủy–Hỏa–Thổ) phong cách pastel hiện đại.
  - `assets/images/guide_1_cool.jpg`: Make-up từ `user_photo_1.png` (giữ nguyên khuôn mặt & dáng kính râm ngược cực ngầu, thêm viền sticker trắng, tia sao vàng trên mắt kính, la bàn & chòm sao nền san hô – kem nắng).
  - `assets/images/guide_2_cheer.jpg`: Make-up từ `user_photo_2.png` (giữ nguyên biểu cảm hài hước dễ thương, xóa sạch chữ cũ, thêm nền tia nắng xanh bạc hà, 3 đồng xu Kinh Dịch vàng lấp lánh & tua rua đỏ may mắn).
  - `assets/images/guide_3_love.jpg`: Make-up từ `user_photo_3.png` (giữ nguyên cặp đôi ngọt ngào, xóa sạch chữ cũ, thêm viền sticker, bướm phát sáng, trái tim bokeh & chòm sao nền hồng phấn – tím oải hương).
  - *(Giữ nguyên 6 ảnh cũ `hero_celestial.jpg`, `five_elements.jpg`, `iching_oracle.jpg`, `user_photo_1..3.png` để bảo toàn tương thích ngược 100%).*
- `[x]` **Thiết kế lại giao diện Gen-Z Playful Mystic chuẩn `scroll-craft` (`assets/studio_gui.html` + `assets/scrollcraft/scrollcraft.css` & `scrollcraft.js`):**
  - Nhúng engine thật `scrollcraft.js` + `scrollcraft.css` (không sửa core engine; theme hoàn toàn qua design tokens nền sáng `#FAF8F4`, mực tím than `#1C1635`, 2 font chuẩn tiếng Việt `Baloo 2` + `Nunito`, `box-sizing: border-box` nội tuyến chống dính ô input, zero gradient text, zero em-dash, zero neon nặng nề).
  - **Kịch bản Peak + Hiệu ứng Nam Thần Lò Xo Pháo Bông + 3 Bộ Form Chuyên Biệt:**
    - Khi bấm vào bất kỳ ô ảnh Nam Thần nào ở trên: trang tự cuộn mượt xuống khu vực nhập liệu, Nam Thần bật nảy lò xo to giữa màn hình kèm pháo bông confetti + icon hài hước (`💰💎🏡` / `🎲🍀🔥` / `💖🦋✨`) và câu thoại vui nhộn trong ~1.65s rồi tự thu nhỏ bay gọn vào khung đầu form.
    1. **Ô 1 — Soi Tử Vi, Tài Bạch & Điền Trạch (`guide_1_cool.jpg`, đỏ san hô `#D93848`):** Hiện trực tiếp 100% các trường bắt buộc (Họ tên, Giới tính, Loại lịch + Tháng nhuận, Ngày sinh, Giờ phút sinh + chọn nhanh 12 Canh Giờ, Nơi sinh 63 tỉnh thành với `Hải Phòng` đầu bảng, Năm xem hạn, Chủ đề soi sâu Tài Bạch/Điền Trạch/Quan Lộc/Phu Thê) — không giấu trong thu gọn.
    2. **Ô 2 — Gieo Quẻ Hỏi Việc (`guide_2_cheer.jpg`, xanh ngọc `#0D8A74`):** Ẩn hoàn toàn Họ tên & Ngày sinh; cung cấp chip câu hỏi gợi ý nhanh và **6 phương pháp khởi quẻ đa dạng** (*Vũ trụ gieo hộ 3 xu*, *Tự tung 3 xu trên web có đồng xu lật trực quan*, *Nhập xu thật ngoài đời*, *Chọn con số bất kỳ Mai Hoa*, *Gõ 2 chữ đầu tiên Mai Hoa Tự Số*, *Khởi quẻ theo Giờ động tâm*).
    3. **Ô 3 — Giải Mã Thần Số Học (`guide_3_love.jpg`, hồng berry `#C8337B`):** Giải thích rõ vai trò 3 tầng dữ liệu: **Ngày sinh (Bắt buộc)** + **Họ tên thật trên khai sinh (Mở Linh hồn, Sứ mệnh, Nhân cách)** + **Tên thường gọi / Nickname (Đo cộng hưởng & bù khuyết ô số trống)**, kèm công cụ chấm điểm so sánh nhiều Nickname mới.
  - Đã kiểm thử bằng headless Chrome trên Desktop (`1440×900`, `1440×3200`) & Tablet (`768px`), xác nhận 0 lỗi JS/API, nút Gemini AI (`#kb-sidebar-ai-btn`, `#kb-toolbar-ai-btn`) hòa hợp 100%, và giữ nguyên chân trang **`❤️ From K.B - Hội BĐS Đồ Sơn ❤️`**.
- `[x]` **Nâng cấp `gui_server.py` & `sync_from_skill.py`:** Tự phục vụ và đồng bộ thêm `/assets/scrollcraft/*` sang `public/assets/scrollcraft/` cho Vercel CDN.

### Các hướng có thể triển khai tiếp theo yêu cầu anh (`[ ]`)
- `[ ]` Bổ sung thêm câu thoại hài hước riêng hoặc hiệu ứng âm thanh tung đồng xu nhẹ (có nút bật/tắt) khi gieo quẻ ở Hệ Hỏi Vũ Trụ.
- `[ ]` Tích hợp thêm tính năng check độ hợp đôi (2 ngày sinh/tên) cho Hệ Tình Duyên & Vibe hoặc Tab Xem Tuổi Mua Nhà / Hướng Đất Bát Trạch cho Hội BĐS Đồ Sơn.

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
  python -X utf8 "G:/My Drive/Antigravity/kb-tuvi-web/sync_from_skill.py" --push -m "Gen-Z playful mystic scroll-craft UI with 3 stylized persona guides"
  ```

---

## 5. Resume Prompt Mẫu

```text
Đọc ngay file bàn giao G:\My Drive\Antigravity\Skills\kb-tuvi\AI_HANDOFF_README.md và G:\My Drive\Antigravity\Skills\kb-tuvi\SKILL.md để tiếp quản dự án KB-TUVI v3.1 (giao diện Gen-Z vui tươi chuẩn scroll-craft với 3 Sư Huynh đại diện 3 phong cách xem). Giữ nguyên mọi mục [x] đã hoàn thành, tuân thủ nghiêm ngặt luật cấm PowerShell, và thực hiện yêu cầu tiếp theo của anh: [NHẬP YÊU CẦU MỚI]
```
