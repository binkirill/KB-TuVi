# ☯️ KB-TUVI Web Studio + Gemini AI (Free Tier)

Ứng dụng web tương tác **Tử Vi Đẩu Số × Bát Tự Tứ Trụ × Kinh Dịch Lục Hào × Kỳ Môn Độn Giáp** chuẩn **Zero-Hallucination** (*Code tính toán thiên văn UTC+7 chính xác 100%, AI Gemini luận giải theo cổ pháp*).

- **Zero-Dependency Python 3:** Không cần cài đặt bất kỳ thư viện ngoài nào (`requirements.txt` trống).
- **Bảo mật API Key:** `GEMINI_API_KEY` chỉ đặt trong Environment Variables của máy chủ (Vercel/Render), không bao giờ lộ ra trình duyệt.
- **Bảo vệ Quota Free khi chia sẻ cho bạn bè:** Hỗ trợ **Mã mời (`ACCESS_CODE`)**, giới hạn lượt/IP/ngày (`DAILY_LIMIT_PER_IP`), tự động fallback qua các model Free Tier (`gemini-3.8-flash` → `gemini-3.6-flash` → `gemini-3.5-flash-lite`), và chế độ **BYOK** (bạn bè tự dán Gemini API Key miễn phí của riêng họ ngay trên web).

---

## 1. Chạy thử trên máy tính (Localhost)

```bash
# (Tùy chọn) Tạo file .env từ mẫu rồi dán GEMINI_API_KEY vào
copy .env.example .env

# Chạy máy chủ web
python -X utf8 scripts/gui_server.py --port 8765
```
Mở trình duyệt tại `http://127.0.0.1:8765`.

---

## 2. Đẩy mã nguồn lên GitHub

1. Tạo một repository mới trên [GitHub](https://github.com/new) (đặt tên `kb-tuvi-web`, chọn **Private** hoặc **Public** đều an toàn).
2. Mở Terminal tại thư mục `kb-tuvi-web` và chạy:

```bash
git init
git add .
git commit -m "Initial release: KB-TUVI Web Studio + Gemini AI"
git branch -M main
git remote add origin https://github.com/<TEN-GITHUB-CUA-BAN>/kb-tuvi-web.git
git push -u origin main
```

---

## 3. Deploy miễn phí 100% lên Web

### Cách 1: Vercel (Khuyên dùng — Nhanh, không ngủ đông)
1. Lấy **Gemini API Key miễn phí** tại [Google AI Studio](https://aistudio.google.com/apikey).
2. Đăng nhập [vercel.com](https://vercel.com) bằng tài khoản GitHub → **Add New → Project** → chọn repo `kb-tuvi-web` → **Import**.
3. Mở mục **Environment Variables**, thêm:
   - `GEMINI_API_KEY` = `AIzaSy...` *(bắt buộc nếu muốn bạn bè dùng chung Key miễn phí của bạn)*
   - `ACCESS_CODE` = *(tùy chọn, ví dụ `tuvi2026` để chỉ bạn bè có mã mới gọi được AI)*
   - `DAILY_LIMIT_PER_IP` = `20` *(tùy chọn)*
4. Bấm **Deploy** → đợi ~30 giây nhận link `https://kb-tuvi-web.vercel.app` gửi cho bạn bè!

### Cách 2: Render.com (Không giới hạn timeout cho bài luận rất dài)
1. Đăng nhập [render.com](https://render.com) bằng GitHub → **New → Blueprint** (tự đọc sẵn `render.yaml`) hoặc **New → Web Service** chọn repo `kb-tuvi-web`.
2. Điền biến môi trường `GEMINI_API_KEY` (và `ACCESS_CODE` nếu muốn).
3. Bấm **Deploy** và chia sẻ link `*.onrender.com`.
