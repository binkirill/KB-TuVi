# Cẩm Nang Luận Giải Thần Số Học Đa Phái & Kiểm Chứng Chéo Đông – Tây (`kb-tuvi` v3.0)

Tài liệu này quy định chuẩn luận giải khi chạy `--mode numerology`, `--mode full` hoặc `--mode all` trong `kb-tuvi`, đồng thời hướng dẫn nhúng các module vào dự án Web thực tế.

---

## 1. Nguyên Tắc Bất Di Bất Dịch Về Toán Học Thần Số Học

1. **Luôn tính trên Ngày Sinh Dương Lịch:** Khác với Tử Vi (dùng Âm lịch) và Bát Tự (dùng lịch Tiết Khí Mặt Trời), Thần số học phương Tây luôn tính trên **Ngày tháng năm sinh Dương lịch ghi trên giấy khai sinh** (hoặc ngày sinh Dương lịch thực tế nếu giấy tờ bị ghi lệch hẳn sang năm khác — khi đó có thể chạy so sánh 2 ngày).
2. **Giải quyết triệt để tranh cãi giữa 2 trường phái tại Việt Nam (`vn` vs `intl`):**
   - **Nhân số học Việt Nam (`--num-school vn`, theo David Phillips / Lê Đỗ Quỳnh Hương):** Cộng tổng liền mạch từng chữ số của `YYYYMMDD`. Dải Số Chủ Đạo từ **`2` đến `11` và `22/4`** — đặc biệt **giữ nguyên Số `10`** (tổng `19 -> 10`, `28 -> 10`, `37 -> 10`, `46 -> 10`), không rút gọn về `1`.
   - **Pythagoras Quốc tế (`--num-school intl`, theo Hans Decoz / Matthew Goodwin):** Rút gọn riêng 3 thành phần **Năm + Tháng + Ngày** trước rồi mới cộng lại (để bảo toàn *Master Numbers* `11/2, 22/4, 33/6` nằm ở Tháng/Ngày/Năm), và `10` rút gọn về **Đường Đời `1`**.
   - **Quy tắc luận giải khôn ngoan:** Nếu trường `core_numbers.life_path.school_diff_note` khác `null` (ví dụ tổng `28` vừa là **Số `10` Nhân số học VN** vừa là **Đường Đời `1` Quốc tế**), hãy giải thích ngắn gọn sự giao thoa: *"Nền tảng cốt lõi là năng lượng độc lập tiên phong của Số 1, được bao bọc bởi sự linh hoạt, quảng giao và khả năng thích nghi cao của Số 10"*.
3. **Quy tắc chữ `Y` trong Họ Tên Tiếng Việt (`contextual`):**
   - Chữ `Y` mang giá trị `7` trong bảng Pythagoras (`1` trong bảng Chaldean).
   - Chữ `Y` là **Phụ âm** khi đứng liền trước hoặc liền sau một nguyên âm `A, E, I, O, U` trong cùng từ (*Nguyễn, Quỳnh, Yến, Duy, May*).
   - Chữ `Y` là **Nguyên âm** khi đứng độc lập hoặc kẹp giữa các phụ âm (*Ý, My, Mỹ, Lý, Kỳ, Thy, Vy*).

---

## 2. Cấu Trúc Luận Giải 5 Tầng Chuyên Sâu (Thuần Thần Số Học)

### Tầng 1: Tam Giác Vàng Bản Mệnh & Độ Lệch Nội Tâm
- **Số Chủ Đạo / Đường Đời (`life_path`):** Bài học lớn nhất xuyên suốt cuộc đời và "con đường cao tốc" thuận tự nhiên nhất.
- **Số Sứ Mệnh (`expression`):** Bộ công cụ năng lực chuyên môn từ Họ tên khai sinh để thực hiện Đường đời.
- **Số Linh Hồn (`soul_urge`):** Khao khát thầm kín bên trong (điều thực sự làm đương số hạnh phúc khi ở một mình).
- **Số Nhân Cách (`personality`):** Khí chất bề ngoài người lạ cảm nhận trong 5 phút đầu gặp mặt.
- **Phân tích Cầu Nối (`bridges`):**
  - Nếu `soul_to_personality == 0`: Trong ngoài đồng nhất, sống thật với cảm xúc.
  - Nếu `soul_to_personality >= 3`: Có khoảng cách lớn giữa vẻ ngoài (VD Nhân cách `8` lạnh lùng quyết đoán) và nội tâm thật (VD Linh hồn `2` nhạy cảm cần vỗ về) — giúp đương số cảm thấy "được đọc vị trúng tim đen".
- **Số Trưởng Thành (`maturity`):** Năng lượng trỗi dậy mạnh từ tuổi `36 - life_path.base` trở đi (hậu vận phương Tây).

### Tầng 2: Biểu Đồ Ngày Sinh `3×3`, Mũi Tên & Tác Dụng Bù Khuyết Của Họ Tên
- Không bao giờ dọa nạt về **Mũi tên trống**! Ví dụ:
  - *Trống 4-5-6*: Đừng gọi nặng nề là "Mũi tên Uất hận", hãy phân tích là *"Nhạy cảm với kỳ vọng cao — cần học cách chia nhỏ mục tiêu và trao đổi thẳng thắn thay vì giữ ấm ức trong lòng"*.
  - *Trống 1-5-9*: *"Cần kỷ luật hoàn tất (Finish what you start) và lập deadline ngắn 25 phút"*.
- Kiểm tra mảng `filled_birth_chart_gaps`: Chỉ rõ những con số từ **Họ tên khai sinh** (hoặc **Tên thường gọi / Nghệ danh**) đã lấp đầy thành công ô trống nào trên biểu đồ ngày sinh!

### Tầng 3: Bốn Nợ Nghiệp (`13/4, 14/5, 16/7, 19/1`) & Số Khuyết (`Karmic Lessons`)
- Nợ nghiệp không phải "trừng phạt", mà là **môn học nâng cao bắt buộc**: vượt qua `13/4` đạt thành tựu quy trình xuất chúng; vượt `14/5` làm chủ tự do tài chính & kỷ luật bản thân; vượt `16/7` đạt trí tuệ tâm thức sâu sắc; vượt `19/1` trở thành nhà lãnh đạo tự chủ biết lắng nghe.

### Tầng 4: Bản Đồ Thời Vận — Kim Tự Tháp 4 Đỉnh Cao × Sóng 9 Năm Cá Nhân
- Kết hợp **Đỉnh cao đang hoạt động (`is_current: true`)** + **Thử thách đi kèm** với **Năm Cá Nhân (`personal_year 1..9`)**:
  - **Năm `1, 3, 5, 8`:** Pha Dương — mở rộng, khởi sự, ra mắt sản phẩm, chuyển việc, đàm phán tài chính.
  - **Năm `4` & `7`:** Hai đáy kỹ thuật cần đặc biệt lưu ý theo quy luật hình sin — không có nghĩa là xui xẻo, mà là **năm học sâu, chuẩn hóa hệ thống, khám sức khỏe, giữ tiền mặt, tránh vay nợ đầu cơ lướt sóng**.
  - **Năm `2, 6, 9`:** Pha Kết nối đối tác (`2`), Chăm sóc gia đình & thương hiệu uy tín (`6`), Thanh lọc dọn dẹp cái cũ & phụng sự (`9`).

### Tầng 5: Chấm Điểm Tên Gọi Chaldean & Ma Trận Định Mệnh 22 Arcana
- **Chaldean (`chaldean_name`):** Dựa trên rung động âm thanh thực tế. Các số kép **Thượng Cát / Đại Cát** như `15, 17, 19, 21, 23, 24, 27, 32, 33, 37, 41, 42, 45, 46, 50` rất lý tưởng khi tư vấn đặt Nghệ danh, Tên tiếng Anh, Tên công ty/sản phẩm hoặc Tên con.
- **Ma Trận Định Mệnh (`destiny_matrix_22`):** Dùng `comfort_zone_center` làm "trạm sạc năng lượng" mỗi khi đương số mất phương hướng, và `material_40y` cho chìa khóa mở khóa dòng tiền.

---

## 3. Giao Thoa & Kiểm Chứng Chéo Đông × Tây (`Tử Vi × Bát Tự × Thần Số Học`)

Khi chạy `--mode full` hoặc `--mode all`, đặt 3 hệ thống lên cùng bàn cân theo nguyên tắc **"Tách bạch thuật ngữ khi phân tích riêng — Hội tụ bản chất khi tổng kết"**:

| Trục đối chiếu | Hệ Đông Phương (`Tử Vi` + `Bát Tự`) | Hệ Tây Phương (`Thần Số Học` + `22 Arcana`) | Cách kết luận Thực Chiến |
| :--- | :--- | :--- | :--- |
| **1. Cốt cách & Vai trò** | Chính tinh cung Mệnh/Quan + Thập Thần Đề Cương (VD: *Sát Phá Tham* / *Thất Sát, Thương Quan*) | Số Chủ Đạo & Sứ Mệnh (VD: Số `1, 5, 8`) | Nếu khớp nhau ➔ **Đồng thuận 100% thiên hướng tiên phong/kinh doanh**. Nếu Đông phương ôn hòa (*Thiên Đồng/Chính Ấn*) mà Tây phương là Số `8` ➔ *Nội lực mềm mỏng nhân văn nhưng bài học cuộc đời buộc phải đứng ra quản trị tài chính*. |
| **2. Bù khuyết Năng lượng** | **Hỷ / Dụng Thần Ngũ Hành** (`fuyi_favorable_elements` + Điều hầu) | **Mũi Tên Trống** + **Số Khuyết Họ Tên** | Chọn nghề nghiệp, thói quen và Nghệ danh vừa mang hành Hỷ/Dụng vừa lấp đúng con số đang trống trên Biểu đồ 3×3! |
| **3. Quyết sách Năm Xem** | Lưu Niên Tử Vi (Lộc/Quyền/Kỵ) + Lưu Niên/Đại Vận Bát Tự | **Năm Cá Nhân (`1..9`)** + **Đỉnh Cao Hiện Tại** | • Đông Cát + Năm cá nhân `1,3,5,8`: **Tổng tiến công**.<br>• Đông Cát + Năm cá nhân `4,7`: **Thắng nhờ chiều sâu chuyên môn, không đánh quả ngắn hạn**.<br>• Đông Kỵ/Xung + Năm cá nhân `4,7,9`: **Tuyệt đối phòng thủ, bảo toàn vốn & sức khỏe**. |

---

## 4. Hướng Dẫn Nhúng Trực Tiếp Vào Dự Án Web Của Anh

Bộ mã nguồn trong `scripts/` được thiết kế chuẩn **Dual-Stack Web Architecture**:

1. **Nếu Backend Web dùng Python (`FastAPI` / `Flask` / `Django`):**
   Copy trực tiếp các file `core_calendar.py`, `engine_tuvi.py`, `engine_bazi.py`, `engine_iching.py`, `engine_numerology.py` vào thư mục backend và gọi hàm thuần:
   ```python
   from engine_numerology import compute_numerology_profile
   data = compute_numerology_profile(birth_date_solar="1992-08-16", full_name="Nguyễn Minh Quân", school="vn")
   ```
   Hoặc chạy sẵn microservice REST API có hỗ trợ CORS:
   - `POST /api/analyze` — Trọn bộ 5 hệ Đông–Tây + Kiểm chứng chéo.
   - `POST /api/numerology` — Riêng Thần số học siêu tốc (`< 2ms`, không cần giờ sinh).
   - `POST /api/name-check` — Chấm điểm & xếp hạng hàng loạt phương án đặt tên con / thương hiệu.

2. **Nếu Frontend / Edge dùng `Next.js` / `React` / `Vue` / `Cloudflare Workers`:**
   Import thẳng `scripts/web_numerology_sdk.js` (`0 npm dependencies`, hỗ trợ đầy đủ tiếng Việt có dấu) để tính tức thì trên trình duyệt hoặc Edge Runtime không tốn tài nguyên server!
