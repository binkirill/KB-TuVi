# -*- coding: utf-8 -*-
"""
gemini_interpreter.py — Bộ kết nối Gemini API Free cho KB-TUVI v3.0 (5 Hệ Đông - Tây).
Kiến trúc Zero-Dependency Python 3 (dùng thuần urllib.request, không cần pip install).
- Hỗ trợ đủ 5 hệ: Tử Vi Đẩu Số + Bát Tự Tứ Trụ + Thần Số Học Đa Phái (Pythagoras/Chaldean/22 Arcana) + Kinh Dịch Lục Hào + Kỳ Môn Độn Giáp.
- Tự động nạp tài liệu cổ pháp từ references/ làm System Instruction theo chế độ luận giải.
- Auto-Fallback qua các model Free Tier: gemini-3.8-flash -> gemini-3.6-flash -> gemini-3.5-flash-lite -> gemini-2.5-flash.
- Hỗ trợ bảo vệ Quota: ACCESS_CODE + Rate limit theo IP/ngày + BYOK (bạn bè tự nhập key riêng).
"""

from __future__ import annotations
import json
import os
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
REF_DIR = os.path.join(PROJECT_ROOT, "references")

AVAILABLE_MODELS: List[Dict[str, str]] = [
    {"id": "gemini-3.8-flash", "label": "Gemini 3.8 Flash (Mặc định — Mạnh nhất, Free Tier)"},
    {"id": "gemini-3.6-flash", "label": "Gemini 3.6 Flash (Ổn định — Free Tier)"},
    {"id": "gemini-3.5-flash-lite", "label": "Gemini 3.5 Flash-Lite (Siêu nhanh — Tiết kiệm quota)"},
    {"id": "gemini-2.5-flash", "label": "Gemini 2.5 Flash (Dự phòng cho Key cũ)"},
]
ALLOWED_MODEL_IDS = [m["id"] for m in AVAILABLE_MODELS]
DEFAULT_MODEL = "gemini-3.8-flash"

_DAILY_USAGE: Dict[Tuple[str, str], int] = {}
_REF_CACHE: Dict[str, str] = {}
_ENV_LOADED = False


def load_local_dotenv() -> None:
    """Đọc file .env tại thư mục gốc nếu có (chỉ nạp biến chưa có trong os.environ)."""
    global _ENV_LOADED
    if _ENV_LOADED:
        return
    _ENV_LOADED = True
    env_path = os.path.join(PROJECT_ROOT, ".env")
    if not os.path.isfile(env_path):
        return
    try:
        with open(env_path, "r", encoding="utf-8") as f:
            for raw_line in f:
                line = raw_line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                key, val = line.split("=", 1)
                key = key.strip()
                val = val.strip().strip('"').strip("'")
                if key and key not in os.environ:
                    os.environ[key] = val
    except Exception:
        pass


def get_public_config() -> Dict[str, Any]:
    """Trả về cấu hình công khai cho frontend (KHÔNG bao giờ lộ API Key hay Access Code)."""
    load_local_dotenv()
    server_key = os.environ.get("GEMINI_API_KEY", "").strip()
    access_code = os.environ.get("ACCESS_CODE", "").strip()
    env_model = os.environ.get("GEMINI_MODEL", DEFAULT_MODEL).strip()
    if env_model not in ALLOWED_MODEL_IDS:
        env_model = DEFAULT_MODEL
    daily_limit = int(os.environ.get("DAILY_LIMIT_PER_IP", "20") or "20")
    return {
        "server_has_key": bool(server_key),
        "requires_access_code": bool(access_code),
        "default_model": env_model,
        "available_models": AVAILABLE_MODELS,
        "daily_limit_per_ip": daily_limit,
    }


def _read_ref(filename: str) -> str:
    if filename in _REF_CACHE:
        return _REF_CACHE[filename]
    path = os.path.join(REF_DIR, filename)
    if not os.path.isfile(path):
        return ""
    try:
        with open(path, "r", encoding="utf-8") as f:
            content = f.read().strip()
        _REF_CACHE[filename] = content
        return content
    except Exception:
        return ""


def _build_system_instruction(mode: str) -> str:
    """Nạp đúng các tài liệu cổ pháp theo chế độ luận giải Đông - Tây của KB-TUVI v3.0."""
    ref_map = {
        "full": [
            "tuvi_schools_and_patterns.md",
            "bazi_classics_methodology.md",
            "numerology_east_west_guide.md",
            "han_viet_glossary.md",
        ],
        "tuvi": ["tuvi_schools_and_patterns.md", "han_viet_glossary.md"],
        "bazi": ["bazi_classics_methodology.md", "han_viet_glossary.md"],
        "numerology": ["numerology_east_west_guide.md"],
        "iching": ["iching_liuyao_qimen_guide.md", "han_viet_glossary.md"],
        "qimen": ["iching_liuyao_qimen_guide.md", "han_viet_glossary.md"],
        "all": [
            "tuvi_schools_and_patterns.md",
            "bazi_classics_methodology.md",
            "numerology_east_west_guide.md",
            "iching_liuyao_qimen_guide.md",
            "han_viet_glossary.md",
        ],
    }
    files = ref_map.get(mode, ref_map["full"])
    ref_blocks = []
    for fn in files:
        txt = _read_ref(fn)
        if txt:
            ref_blocks.append(f"=== TÀI LIỆU CHUYÊN KHẢO: {fn} ===\n{txt}")

    core_rules = """Bạn là Chuyên gia Mệnh Lý Đông – Tây & Dịch Học cao cấp của hệ thống KB-TUVI v3.0 (Zero-Hallucination).

BA LUẬT SẮT BẮT BUỘC:
1. CHỈ LUẬN DỰA TRÊN JSON ĐƯỢC CUNG CẤP (ZERO MENTAL MATH):
   - Toàn bộ ngày Âm lịch, Giờ Chân Thái Dương, Tứ Trụ, 12 cung Tử Vi, chính phụ tinh, Tuần–Triệt, Phi Tinh Tứ Hóa, Thần Số Học (Pythagoras, Chaldean, Biểu đồ 3×3, 4 Đỉnh Cao, Ma trận 22 Arcana), Lục Hào và Kỳ Môn đã được tính chính xác 100% bằng thuật toán.
   - TUYỆT ĐỐI KHÔNG tự đổi lịch lại, KHÔNG cộng nhẩm lại số Thần số học, KHÔNG bịa sao hay tự sửa dữ liệu khác với JSON.
2. TÁCH BẠCH HỆ THỐNG & KIỂM CHỨNG CHÉO ĐÔNG × TÂY:
   - Khi luận độc lập từng hệ: không trộn lẫn thuật ngữ giữa Tử Vi, Bát Tự và Thần Số Học.
   - Khi chạy tổng hợp (`full` hoặc `all`): đặt mục **Bảng Kiểm Chứng Chéo Đông × Tây (Tử Vi × Bát Tự × Thần Số Học)** gắn nhãn độ tin cậy rõ ràng:
     - `🟢 ĐỒNG THUẬN CAO`
     - `🟡 BÁN ĐỒNG THUẬN`
     - `🔴 PHÂN KỲ`
3. CHỐNG ĐỘC ĐOÁN & HƯỚNG THIỆN (XU CÁT TỲ HUNG):
   - TUYỆT ĐỐI KHÔNG dùng ngôn từ hù dọa, định mệnh cực đoan (cấm nói "chắc chắn ly hôn", "số tuyệt mạng", "phá sản không cứu được").
   - Luôn diễn đạt theo xu hướng cấu trúc & xác suất, đi kèm giải pháp chuyển hóa thực tế (chọn nghề ứng sao/ứng số, quản trị tài chính, cân bằng sức khỏe, bổ khuyết hành/ô trống).
4. CẢNH BÁO BIÊN GIỚI GIỜ SINH:
   - Nếu trong JSON có `meta.branch_boundary_warning` khác null HOẶC `bazi.late_zi_warning` khác null: mở đầu bài luận bằng một hộp cảnh báo ngắn gọn và nêu 2–3 dấu hiệu nhận diện của 2 canh giờ giáp ranh để đương số nghiệm lý.

PHONG CÁCH TRÌNH BÀY:
- Tiếng Việt gần gũi, rõ ràng, dễ hiểu cho người bình thường nhưng vẫn giữ đúng chuẩn thuật ngữ chuyên môn, trình bày bằng Markdown đẹp mắt (tiêu đề, bảng đối chiếu, gạch đầu dòng sắc nét).
- Cuối bài luôn có 1 dòng lưu ý ngắn: *Mệnh lý & Dịch học là công cụ tham chiếu chiến lược nhân sinh, không thay thế quyết định y tế hay pháp lý chuyên ngành.*
"""
    return core_rules + "\n\n" + "\n\n".join(ref_blocks)


def _compact_payload(payload: Dict[str, Any], mode: str) -> Dict[str, Any]:
    """Lọc bỏ dữ liệu thừa (như export_html) để tối ưu tốc độ và token."""
    out: Dict[str, Any] = {"meta": payload.get("meta", {})}
    if mode in ("full", "tuvi", "all") and "tuvi" in payload:
        out["tuvi"] = payload["tuvi"]
    if mode in ("full", "bazi", "all") and "bazi" in payload:
        out["bazi"] = payload["bazi"]
    if mode in ("full", "numerology", "all") and "numerology" in payload:
        out["numerology"] = payload["numerology"]
    if mode in ("full", "all") and "cross_validation" in payload:
        out["cross_validation"] = payload["cross_validation"]
    if mode in ("iching", "all") and "iching" in payload:
        out["iching"] = payload["iching"]
    if mode in ("qimen", "all") and "qimen" in payload:
        out["qimen"] = payload["qimen"]
    return out


def _build_user_prompt(compact_data: Dict[str, Any], mode: str, focus_question: str) -> str:
    mode_prompts = {
        "full": (
            "Hãy lập **Hồ Sơ Luận Giải Đông – Tây Tổng Hợp (Tử Vi Đẩu Số × Bát Tự Tứ Trụ × Thần Số Học)** đầy đủ gồm 6 phần:\n"
            "1. Tổng quan Định danh, Cốt cách Tiên thiên & Điểm mạnh Thiên phú nổi bật nhất.\n"
            "2. Luận giải chuyên sâu **Tử Vi Đẩu Số** (Mệnh–Thân–Cục, Cách cục, Tam Phương Tứ Chính, Tuần–Triệt, Phi Tinh Tứ Hóa, Đại Hạn & Lưu Niên).\n"
            "3. Luận giải chuyên sâu **Bát Tự Tứ Trụ** (Cường Nhược Nhật Chủ, Phù Ức + Điều Hầu Dụng Thần, Đại Vận & Lưu Niên).\n"
            "4. Luận giải chuyên sâu **Thần Số Học Đa Phái** (Số Chủ Đạo, Sứ Mệnh, Linh Hồn, Mũi tên Biểu đồ 3×3, Đỉnh cao hiện tại, Năm cá nhân, Chaldean & Ma trận 22 Arcana).\n"
            "5. **Bảng Kiểm Chứng Chéo Đông × Tây (Tử Vi × Bát Tự × Thần Số Học)** theo 4 trục (Sự nghiệp, Tài chính, Tình cảm/Gia đạo, Sức khỏe) kèm nhãn `🟢 ĐỒNG THUẬN CAO` / `🟡 BÁN ĐỒNG THUẬN` / `🔴 PHÂN KỲ`.\n"
            "6. **Chiến lược Hành động Thực tiễn (Xu Cát Tỳ Hung)** cho giai đoạn tới."
        ),
        "tuvi": (
            "Hãy luận giải chuyên sâu **Thuần Tử Vi Đẩu Số** (không trộn thuật ngữ Bát Tự hay Thần Số Học), gồm:\n"
            "1. Tầng Tiên Thiên (Mệnh – Thân – Cục, Âm Dương Thuận/Nghịch lý, Vòng Thái Tuế).\n"
            "2. Cách Cục nổi bật, Tam Phương Tứ Chính & tác động của Tuần – Triệt.\n"
            "3. Luận Phi Tinh Tứ Hóa (Lộc – Quyền – Khoa – Kỵ) giữa Mệnh – Tài – Quan – Điền – Phu.\n"
            "4. Dự báo Đại Hạn hiện tại & Lưu Niên năm xem hạn.\n"
            "5. Gợi ý Xu Cát Tỳ Hung ứng sao thực tiễn."
        ),
        "bazi": (
            "Hãy luận giải chuyên sâu **Thuần Bát Tự Tứ Trụ**, gồm:\n"
            "1. Định Cường Nhược Nhật Chủ (Đắc Lệnh – Đắc Địa – Đắc Thế) & cấu trúc Tứ Trụ.\n"
            "2. Xác định Hỷ Thần – Dụng Thần – Kỵ Thần (Phù Ức + Điều Hầu Cùng Thông Bảo Giám + Thông Quan).\n"
            "3. Phân tích 4 trục: Sự nghiệp, Tài lộc, Hôn nhân/Quan hệ, Sức khỏe.\n"
            "4. Dự báo Đại Vận hiện tại & Lưu Niên năm xem hạn.\n"
            "5. Gợi ý bổ khuyết Dụng thần (ngành nghề, môi trường, phương hướng, thói quen)."
        ),
        "numerology": (
            "Hãy luận giải chuyên sâu **Thần Số Học Đa Phái (Pythagoras + Chaldean + Ma Trận 22 Arcana)**, gồm:\n"
            "1. Bản sắc cốt lõi: Số Chủ Đạo (so sánh VN vs Quốc tế nếu khác), Sứ Mệnh, Linh Hồn, Nhân Cách, Trưởng Thành.\n"
            "2. Giải mã Biểu đồ Ngày sinh 3×3 vs Biểu đồ Tổ hợp (Mũi tên đầy, Mũi tên trống và cách tên gọi bù khuyết).\n"
            "3. Nợ Nghiệp chuyển hóa (nếu có) & Tần số Tên theo Chaldean Babylon.\n"
            "4. Kim Tự Tháp 4 Đỉnh Cao + Sóng Chu Kỳ Năm Cá Nhân hiện tại + Ma Trận 22 Arcana.\n"
            "5. Lời khuyên nghề nghiệp, phát triển bản thân và hành động năm nay."
        ),
        "iching": (
            "Hãy luận giải chuyên sâu **Quẻ Kinh Dịch Lục Hào Nạp Giáp kết hợp Mai Hoa Dịch Số**, gồm:\n"
            "1. Xác định rõ Dụng Thần cho câu hỏi & bối cảnh Nhật Thần – Nguyệt Kiến – Tuần Không.\n"
            "2. Phân tích Hào Động → Hào Biến, Phục Thần & tương quan Thế – Ứng.\n"
            "3. Đối chiếu Thể – Dụng (Mai Hoa) và ý nghĩa Quẻ Chính – Quẻ Hổ – Quẻ Biến.\n"
            "4. Kết luận Cát/Hung rõ ràng, dự báo **Ứng Kỳ** và lời khuyên hành động."
        ),
        "qimen": (
            "Hãy luận giải chuyên sâu **Bàn Kỳ Môn Độn Giáp Thời Gia**, gồm:\n"
            "1. Xác định Độn Cục, Trực Phù, Trực Sử và Dụng Thần đại diện cho sự việc.\n"
            "2. So sánh Nhật Can vs Thời Can, Cát Môn (Khai–Hưu–Sinh) vs Hung Môn.\n"
            "3. Chỉ ra **Phương hướng & Khung giờ thuận lợi nhất** để hành động, đàm phán hoặc xuất hành.\n"
            "4. Chiến lược ứng biến cụ thể."
        ),
        "all": (
            "Hãy lập **Đại Toàn Thư Đông – Tây & Quyết Sách (5 Hệ: Tử Vi × Bát Tự × Thần Số Học × Kinh Dịch × Kỳ Môn)**:\n"
            "1. Phân tích cốt cách gốc & Bảng Kiểm chứng chéo Đông × Tây (gắn nhãn `🟢/🟡/🔴`).\n"
            "2. Giải quẻ Kinh Dịch Lục Hào cho câu hỏi hiện tại (chốt Cát/Hung & Ứng Kỳ).\n"
            "3. Đọc Bàn Kỳ Môn Độn Giáp để chọn phương hướng & thời điểm hành động tối ưu.\n"
            "4. Tổng hợp kế hoạch hành động Xu Cát Tỳ Hung toàn diện."
        ),
    }

    guide = mode_prompts.get(mode, mode_prompts["full"])
    focus_block = ""
    if focus_question.strip():
        focus_block = (
            f"\n\n### CÂU HỎI / TRỌNG TÂM ĐƯƠNG SỐ MUỐN HỎI KỸ:\n"
            f"> {focus_question.strip()}\n"
            f"(Hãy dành một mục riêng trả lời trực diện, sắc sảo và thực tế cho câu hỏi này dựa trên dữ liệu JSON!)\n"
        )

    return (
        f"{guide}{focus_block}\n\n"
        f"### DỮ LIỆU ĐỊNH DANH ZERO-HALLUCINATION (JSON):\n"
        f"```json\n{json.dumps(compact_data, ensure_ascii=False)}\n```"
    )


def _call_gemini_rest(
    api_key: str,
    model_id: str,
    system_instruction: str,
    user_prompt: str,
    timeout_sec: int = 55,
) -> Tuple[str, Dict[str, Any]]:
    """Gọi trực tiếp Gemini REST API generateContent bằng urllib.request (Zero-Dependency)."""
    url = (
        f"https://generativelanguage.googleapis.com/v1beta/models/"
        f"{model_id}:generateContent?key={api_key}"
    )
    body = {
        "system_instruction": {"parts": [{"text": system_instruction}]},
        "contents": [{"role": "user", "parts": [{"text": user_prompt}]}],
        "generationConfig": {
            "temperature": 0.65,
            "maxOutputTokens": 6500,
        },
    }
    raw = json.dumps(body, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=raw,
        headers={"Content-Type": "application/json; charset=utf-8"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=timeout_sec) as resp:
        resp_data = json.loads(resp.read().decode("utf-8"))

    candidates = resp_data.get("candidates") or []
    if not candidates:
        block_reason = resp_data.get("promptFeedback", {}).get("blockReason", "UNKNOWN")
        raise RuntimeError(f"Gemini không trả về nội dung (reason={block_reason}).")

    parts = candidates[0].get("content", {}).get("parts") or []
    text_chunks = [p.get("text", "") for p in parts if isinstance(p, dict) and not p.get("thought") and p.get("text")]
    text = "\n".join(text_chunks).strip()
    if not text:
        raise RuntimeError("Phản hồi từ Gemini bị trống.")

    usage = resp_data.get("usageMetadata") or {}
    return text, usage


def _check_and_increment_rate_limit(client_ip: str) -> Optional[str]:
    limit = int(os.environ.get("DAILY_LIMIT_PER_IP", "20") or "20")
    if limit <= 0:
        return None
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    old_keys = [k for k in _DAILY_USAGE if k[1] != today]
    for k in old_keys:
        _DAILY_USAGE.pop(k, None)

    key = (client_ip or "unknown", today)
    used = _DAILY_USAGE.get(key, 0)
    if used >= limit:
        return (
            f"Bạn đã dùng hết {limit} lượt luận giải AI miễn phí hôm nay trên máy chủ này. "
            f"Bạn có thể dán Gemini API Key miễn phí của riêng bạn ở mục '🔑 Dùng API Key riêng' để xem tiếp không giới hạn!"
        )
    _DAILY_USAGE[key] = used + 1
    return None


def interpret_with_gemini(
    req_data: Dict[str, Any],
    user_api_key: str = "",
    client_ip: str = "127.0.0.1",
) -> Dict[str, Any]:
    """Hàm xử lý chính cho endpoint POST /api/interpret."""
    load_local_dotenv()

    payload = req_data.get("payload")
    if not isinstance(payload, dict) or not payload.get("meta"):
        raise ValueError("Thiếu dữ liệu lá số/quẻ dịch. Hãy bấm 'Xem Lá Số Ngay' trước khi luận giải AI.")

    mode = str(req_data.get("mode", "full")).strip().lower()
    if mode not in ("full", "tuvi", "bazi", "numerology", "iching", "qimen", "all"):
        mode = "full"

    focus_question = str(req_data.get("focus_question", "")).strip()
    requested_model = str(req_data.get("model", "")).strip()
    provided_code = str(req_data.get("access_code", "")).strip()

    user_key = (user_api_key or "").strip()
    using_byok = bool(user_key)

    if using_byok:
        api_key = user_key
    else:
        api_key = os.environ.get("GEMINI_API_KEY", "").strip()
        if not api_key:
            raise PermissionError(
                "Máy chủ chưa cấu hình GEMINI_API_KEY. "
                "Vui lòng nhập Gemini API Key miễn phí của bạn tại mục '🔑 Dùng API Key riêng' "
                "(hoặc chủ web cấu hình biến GEMINI_API_KEY trên Vercel/Render)."
            )
        expected_code = os.environ.get("ACCESS_CODE", "").strip()
        if expected_code and provided_code != expected_code:
            raise PermissionError("Mã mời (Access Code) không đúng. Hãy hỏi chủ web để lấy mã hoặc nhập Gemini API Key riêng của bạn.")
        limit_err = _check_and_increment_rate_limit(client_ip)
        if limit_err:
            raise RuntimeError(limit_err)

    env_default = os.environ.get("GEMINI_MODEL", DEFAULT_MODEL).strip()
    primary_model = requested_model if requested_model in ALLOWED_MODEL_IDS else (
        env_default if env_default in ALLOWED_MODEL_IDS else DEFAULT_MODEL
    )

    models_to_try = [primary_model] + [m for m in ALLOWED_MODEL_IDS if m != primary_model]

    system_instruction = _build_system_instruction(mode)
    compact_data = _compact_payload(payload, mode)
    user_prompt = _build_user_prompt(compact_data, mode, focus_question)

    t0 = time.time()
    last_error = ""
    for model_id in models_to_try:
        try:
            markdown_text, usage = _call_gemini_rest(
                api_key=api_key,
                model_id=model_id,
                system_instruction=system_instruction,
                user_prompt=user_prompt,
            )
            elapsed = round(time.time() - t0, 2)
            return {
                "markdown": markdown_text,
                "model_used": model_id,
                "fallback_used": model_id != primary_model,
                "elapsed_sec": elapsed,
                "usage": usage,
                "key_source": "user_byok" if using_byok else "server_free",
            }
        except urllib.error.HTTPError as http_err:
            code = http_err.code
            try:
                err_body = http_err.read().decode("utf-8", errors="ignore")
                err_json = json.loads(err_body)
                err_msg = err_json.get("error", {}).get("message", err_body[:240])
            except Exception:
                err_msg = str(http_err)

            last_error = f"[{model_id}] HTTP {code}: {err_msg}"
            if code in (401, 403) or "API key not valid" in err_msg or "API_KEY_INVALID" in err_msg:
                raise PermissionError(f"Gemini API Key không hợp lệ hoặc chưa được kích hoạt: {err_msg}")
            if code in (404, 429, 500, 503):
                continue
            raise RuntimeError(last_error)
        except Exception as exc:
            last_error = f"[{model_id}] {exc}"
            continue

    raise RuntimeError(
        f"Tất cả các model Gemini Free hiện đều đang bận hoặc hết hạn mức tạm thời. Chi tiết: {last_error}"
    )
