# -*- coding: utf-8 -*-
"""
gemini_interpreter.py — Bộ kết nối Gemini API Free cho KB-TUVI v3.9 (5 Hệ Đông - Tây).
Kiến trúc Zero-Dependency Python 3 (dùng thuần urllib.request, không cần pip install).
- Hỗ trợ đủ 5 hệ: Tử Vi Đẩu Số + Bát Tự Tứ Trụ + Thần Số Học Đa Phái (Pythagoras/Chaldean/22 Arcana) + Kinh Dịch Lục Hào + Kỳ Môn Độn Giáp.
- Tự động nạp tài liệu cổ pháp từ references/ làm nền tảng phân tích Zero-Hallucination, nhưng diễn đạt đầu ra theo giọng thầy xem trò chuyện tự nhiên, mạch lạc, dễ hiểu cho người bình thường.
- Auto-Fallback qua các model Free Tier tối ưu nhất: gemini-4-hydrogen -> gemini-3.8-flash -> gemini-3.6-flash -> gemini-3.5-flash-lite.
- Hỗ trợ bảo vệ Quota: ACCESS_CODE + Rate limit theo IP/ngày + BYOK (bạn bè tự nhập key riêng).
"""

from __future__ import annotations
import hashlib
import hmac
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
    {"id": "gemini-4-hydrogen", "label": "Gemini 4 Hydrogen (Mặc định — Mạnh nhất gói Free, diễn đạt tiếng Việt tự nhiên & ít ảo giác nhất)"},
    {"id": "gemini-3.8-flash", "label": "Gemini 3.8 Flash (Dự phòng 1 Free Tier — Flash thông minh nhất đời 3)"},
    {"id": "gemini-3.6-flash", "label": "Gemini 3.6 Flash (Dự phòng 2 Free Tier — Cân bằng tốc độ & văn phong)"},
    {"id": "gemini-3.5-flash-lite", "label": "Gemini 3.5 Flash-Lite (Dự phòng cuối Free Tier — Siêu nhẹ, quota rộng)"},
]
ALLOWED_MODEL_IDS = [m["id"] for m in AVAILABLE_MODELS]
DEFAULT_MODEL = "gemini-4-hydrogen"

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


def _get_server_api_key() -> str:
    """Đọc API Key từ biến môi trường (hỗ trợ cả GEMINI_API_KEY và GOOGLE_API_KEY, tự lọc dấu nháy thừa)."""
    raw = (
        os.environ.get("GEMINI_API_KEY")
        or os.environ.get("GOOGLE_API_KEY")
        or os.environ.get("GEMINI_KEY")
        or ""
    )
    return raw.strip().strip('"').strip("'")


def get_public_config() -> Dict[str, Any]:
    """Trả về cấu hình công khai cho frontend (KHÔNG bao giờ lộ API Key hay Access Code)."""
    load_local_dotenv()
    server_key = _get_server_api_key()
    access_code = os.environ.get("ACCESS_CODE", "").strip().strip('"').strip("'")
    daily_limit = int(os.environ.get("DAILY_LIMIT_PER_IP", "20") or "20")
    return {
        "server_has_key": bool(server_key),
        "requires_access_code": bool(access_code),
        "default_model": DEFAULT_MODEL,
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

    core_rules = """Bạn là một vị thầy xem Tử Vi, Mệnh Lý và Dịch Học giàu kinh nghiệm, điềm đạm, sâu sắc nhưng nói chuyện vô cùng gần gũi, dễ hiểu của hệ thống KB-TUVI.

NHIỆM VỤ CỐT LÕI:
Bạn đọc và thẩm thấu dữ liệu JSON cùng tài liệu cổ pháp bên dưới trong đầu để nắm thật chính xác bản chất lá số/quẻ dịch, sau đó **dịch toàn bộ ra lời trò chuyện tự nhiên, ấm áp, liền mạch cho người bình thường đọc là hiểu ngay** — giống như đang ngồi uống trà đối diện giải thích cặn kẽ từng khía cạnh cuộc sống của họ.

NĂM NGUYÊN TẮC BẮT BUỘC:
1. CHÍNH XÁC TUYỆT ĐỐI THEO DỮ LIỆU JSON (ZERO-HALLUCINATION):
   - Toàn bộ Âm lịch, Tứ Trụ, 12 cung, chính phụ tinh, Tuần–Triệt, Tứ Hóa, Thần Số Học, Lục Hào và Kỳ Môn đã được tính chính xác 100% bằng thuật toán.
   - TUYỆT ĐỐI KHÔNG tự tính lại lịch, KHÔNG cộng nhẩm lại số, KHÔNG bịa thêm sao hoặc tự sửa dữ liệu trái với JSON.

2. GIỌNG ĐIỆU THẦY XEM TRÒ CHUYỆN LIỀN MẠCH — GIẢM TỐI ĐA GẠCH ĐẦU DÒNG:
   - Xưng hô ấm áp, thân tình: gọi người xem là **"bạn"** (hoặc gọi tên riêng nhẹ nhàng), tránh cách xưng khô cứng kiểu "Đương số", "Chủ mệnh".
   - **Viết chủ yếu bằng các đoạn văn xuôi liền mạch (3–5 câu mỗi đoạn)**, có câu nối chuyển ý tự nhiên giữa các đoạn để người đọc thấy trôi chảy như đang nghe thầy kể chuyện và phân tích, TUYỆT ĐỐI không viết kiểu báo cáo ngắt quãng, liệt kê rời rạc.
   - **Hạn chế tối đa gạch đầu dòng:** Ít nhất 85% bài luận phải là văn xuôi chia đoạn rõ ràng. Các phần nói về tính cách, công việc, tiền bạc, tình cảm, gia đình, sức khỏe, vận hạn năm nay **KHÔNG dùng gạch đầu dòng** và **KHÔNG kẻ bảng rườm rà**. Chỉ được phép dùng duy nhất **1 danh sách ngắn gọn (3–4 ý)** ở phần lời khuyên thực tế cuối bài nếu cần chốt việc nên làm ngay.

3. BỚT TÊN CÁC CUNG & BỎ THUẬT NGỮ HÁN–VIỆT NẶNG NỀ:
   - Người đọc là người bình thường, không rành chuyên môn. Vì vậy **hạn chế tối đa việc gọi tên các cung Tử Vi** (tránh lặp đi lặp lại kiểu "cung Mệnh ở Tý", "cung Tài Bạch ở Thân", "cung Quan Lộc", "cung Điền Trạch", "cung Phu Thê", "cung Nô Bộc", "cung Thiên Di", "cung Phúc Đức"...).
   - Thay vì nêu tên cung hay tên sao phụ/công thức phức tạp (như Tam Phương Tứ Chính, Phi Tinh Tự Hóa Kỵ nhập Quan, Đắc Lệnh Thất Địa, Điều Hầu Cùng Thông Bảo Giám, Lục Thân, Phục Thần...), hãy **nói thẳng vào ý nghĩa đời thực**: thay bằng "về đường tiền bạc", "trong công việc và sự nghiệp", "chuyện tình cảm, gia đình", "chuyện nhà cửa đất đai", "các mối quan hệ xung quanh", "nhịp vận năm nay"...
   - Chỉ thi thoảng nhắc nhẹ 1–2 điểm neo quen thuộc nhất (ví dụ tên 1 ngôi sao nổi bật, con số chủ đạo hoặc tên quẻ chính) để tăng sự tin cậy, và hễ nhắc tới là giải thích nôm na ngay trong câu đó.

4. TÁCH BẠCH KHI XEM RIÊNG & HƯỚNG THIỆN (XU CÁT TỲ HUNG):
   - Khi xem riêng một bộ môn (chỉ Tử Vi, chỉ Bát Tự, hay chỉ Thần Số Học) thì không pha trộn khái niệm của bộ môn khác.
   - Khi xem tổng hợp nhiều hệ, hãy đan cài các góc nhìn thật mượt thành một câu chuyện thống nhất, và dành 1 đoạn văn ngắn tổng kết những điểm trùng khớp rõ nhất (có thể điểm nhẹ nhãn `🟢 ĐỒNG THUẬN CAO` hoặc `🟡 BÁN ĐỒNG THUẬN` ngay trong câu).
   - TUYỆT ĐỐI KHÔNG dùng lời lẽ hù dọa, phán định mệnh cực đoan (cấm nói "chắc chắn ly hôn", "số tuyệt mạng", "phá sản không cứu được"). Luôn nói theo xu hướng và kèm cách ứng xử, điều chỉnh thiết thực để hóa giải và phát huy điểm mạnh.

5. LƯU Ý GIỜ SINH GIÁP RANH & KẾT BÀI:
   - Nếu trong JSON có `meta.branch_boundary_warning` khác null HOẶC `bazi.late_zi_warning` khác null: mở đầu bằng một lời nhắn nhỏ nhẹ nhàng (dùng blockquote `>`) nhắc bạn rằng giờ sinh nằm sát mốc chuyển canh giờ, kèm 2–3 nét tính cách dễ đối chiếu để bạn tự kiểm chứng xem lá số đã khớp với mình chưa.
   - Cuối bài luôn khép lại nhẹ nhàng bằng 1 dòng nghiêng ngắn: *Mệnh lý và Dịch học là góc nhìn tham khảo giúp bạn hiểu mình và chủ động hơn trong cuộc sống, không thay thế các quyết định y tế hay pháp lý chuyên ngành.*
"""
    return core_rules + "\n\n" + "\n\n".join(ref_blocks)


def _compact_payload(payload: Dict[str, Any], mode: str) -> Dict[str, Any]:
    """Lọc bỏ dữ liệu thừa (như export_html, time_sync_verification) để tối ưu tốc độ và token."""
    raw_meta = dict(payload.get("meta") or {})
    raw_meta.pop("time_sync_verification", None)
    out: Dict[str, Any] = {"meta": raw_meta}
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


def _detect_deep_topic(deep_topic: str, focus_question: str) -> str:
    """Xác định chủ đề xem chuyên sâu từ nút chọn hoặc câu hỏi của người dùng."""
    t = (deep_topic or "").strip().lower()
    if t in ("money", "realestate", "career", "love", "fortune12", "overview"):
        return t
    q = (focus_question or "").strip().lower()
    if not q:
        return "overview"
    if any(k in q for k in ("điền trạch", "đất đai", "nhà cửa", "bất động sản", "mua đất", "bán đất", "tích sản")):
        return "realestate"
    if any(k in q for k in ("tài bạch", "tiền bạc", "dòng tiền", "đầu tư", "tài chính", "giữ lộc", "kiếm tiền")):
        return "money"
    if any(k in q for k in ("quan lộc", "sự nghiệp", "công danh", "công việc", "thăng tiến", "đổi việc", "chuyển việc")):
        return "career"
    if any(k in q for k in ("phu thê", "tình cảm", "tình duyên", "hôn nhân", "gia đạo", "vợ chồng", "người yêu")):
        return "love"
    if any(k in q for k in ("vận hạn", "12 tháng", "từng tháng", "sức khỏe", "tật ách", "hóa giải", "chú ý", "lưu ý")):
        return "fortune12"
    return "overview"


def _build_deep_topic_prompt(
    topic: str,
    mode: str,
    target_year: Any,
    style_reminder: str,
) -> Optional[str]:
    """Tạo dàn ý LUẬN CHUYÊN SÂU THỰC SỰ cho từng mảng (phân tích gốc rễ + vận lớn + đủ 12 tháng + vận hạn & lưu ý)."""
    scope_note = {
        "tuvi": "chỉ sử dụng dữ liệu Tử Vi (bao gồm `target_year_fortune.monthly_fortunes_12`), không trộn thuật ngữ Bát Tự hay Thần Số Học",
        "bazi": "chỉ sử dụng dữ liệu Bát Tự Ngũ Hành (bao gồm `target_liunian.monthly_liuyue_12`), không trộn thuật ngữ Tử Vi hay Thần Số Học",
        "numerology": "chỉ sử dụng dữ liệu Thần Số Học (bao gồm `personal_cycles.personal_months_12`), không trộn sang Tử Vi hay Bát Tự",
        "full": "hòa quyện tự nhiên góc nhìn Tử Vi, Bát Tự Ngũ Hành và Thần Số Học (kết hợp dữ liệu 12 tháng của các hệ trong JSON)",
        "all": "hòa quyện tự nhiên góc nhìn bản mệnh (Tử Vi, Bát Tự, Thần Số Học) cùng dữ liệu 12 tháng và quẻ dịch/hướng đẹp hiện tại",
    }.get(mode, "dựa 100% trên dữ liệu JSON được cung cấp")

    topic_specs = {
        "money": {
            "title": f"CHUYÊN SÂU TIỀN BẠC, DÒNG TIỀN & ĐẦU TƯ NĂM {target_year}",
            "root": (
                "Phân tích thật sâu và cặn kẽ về bản chất tài lộc của bạn: bạn có duyên kiếm tiền từ nguồn nào "
                "(làm chuyên môn, kinh doanh tự do, thương mại, đầu tư hay hợp tác), tiền vào mạnh hay đều đặn, "
                "đâu là thói quen hoặc kẽ hở khiến tiền dễ thất thoát, và cách bạn nên quản lý dòng tiền, tích lũy, phân bổ vốn cho chắc tay."
            ),
            "year_big": (
                f"Phân tích kỹ bức tranh tài chính của chặng vận lớn hiện tại và cả năm {target_year}: "
                "năm nay là năm nên mở rộng kiếm tiền, đầu tư mới hay ưu tiên thu hồi vốn và giữ tiền mặt? Có cơ hội bất ngờ hay áp lực chi tiêu lớn nào đang chờ?"
            ),
            "monthly_focus": (
                "dòng tiền, cơ hội kiếm lộc, ký kết hợp đồng, đầu tư/góp vốn và những tháng dễ hao tiền tốn của hoặc nên giữ chặt ví"
            ),
            "risks": (
                "Chỉ thật rõ các vận hạn & rủi ro tiền bạc cần đề phòng trong năm (ví dụ: bẫy cho vay mượn khó đòi, hùn hạp thiếu rõ ràng, "
                "đầu tư theo cảm xúc/tất tay, chi tiêu phát sinh vì gia đình hay giấy tờ), nêu dấu hiệu nhận biết sớm và cách giữ lộc an toàn."
            ),
        },
        "realestate": {
            "title": f"CHUYÊN SÂU NHÀ CỬA, ĐẤT ĐAI & TÍCH SẢN NĂM {target_year}",
            "root": (
                "Phân tích thật sâu duyên nhà cửa, đất đai và khả năng tích lũy tài sản lâu dài của bạn: "
                "bạn hợp mua ở an cư, tích sản dài hạn hay xoay vòng mua bán/đầu tư bất động sản; "
                "tài sản thường tự tay gây dựng hay có lộc gia đình/đối tác; điểm mạnh và điểm dễ vướng khi đi xem đất, thương lượng, giữ sổ."
            ),
            "year_big": (
                f"Đánh giá kỹ vận nhà đất trong giai đoạn hiện tại và riêng năm {target_year}: "
                "năm nay có tín hiệu thay đổi chỗ ở, sửa sang nhà cửa, mua vào hay chốt lời bán ra không? Mức độ thuận lợi về vốn và đòn bẩy ra sao?"
            ),
            "monthly_focus": (
                "việc đi xem nhà đất, đặt cọc, mua bán, sang tên giấy tờ, sửa chữa/xây dựng và những tháng dễ gặp trục trặc pháp lý, tranh chấp giá hoặc chôn vốn"
            ),
            "risks": (
                "Nêu rõ các vận hạn & điều cần đặc biệt lưu ý về nhà cửa, đất đai trong năm (pháp lý sổ sách, ranh giới, hợp đồng đặt cọc, "
                "vay mượn mua nhà quá sức, tranh cãi với người cùng góp vốn hay hàng xóm) và cách kiểm tra phòng ngừa chắc chắn."
            ),
        },
        "career": {
            "title": f"CHUYÊN SÂU CÔNG VIỆC, SỰ NGHIỆP & THĂNG TIẾN NĂM {target_year}",
            "root": (
                "Phân tích thật kỹ con đường sự nghiệp và vai trò giúp bạn tỏa sáng nhất: "
                "bạn hợp làm lãnh đạo/tự mở riêng, làm chuyên gia nòng cốt hay phát triển trong tổ chức lớn; "
                "phong cách làm việc, cách ứng xử với cấp trên – đồng nghiệp – đối tác, và những bước ngoặt nghề nghiệp đặc trưng của bạn."
            ),
            "year_big": (
                f"Phân tích sâu thế vận công việc giai đoạn hiện tại và riêng năm {target_year}: "
                "năm nay có nên đổi việc, nhảy sang mảng mới, mở rộng kinh doanh hay tập trung củng cố vị thế hiện tại? Quý nhân hỗ trợ đến từ đâu và áp lực KPI/cạnh tranh nằm ở chỗ nào?"
            ),
            "monthly_focus": (
                "tiến độ công việc, cơ hội thăng tiến/nhận dự án mới, thời điểm đẹp để đàm phán lương/chuyển hướng và những tháng dễ gặp áp lực, tiểu nhân, hiểu lầm nơi công sở"
            ),
            "risks": (
                "Chỉ rõ các vận hạn & điều cần lưu ý trong sự nghiệp năm nay (thị phi lời ăn tiếng nói, ký kết văn bản/hợp đồng, "
                "nóng vội bỏ việc khi chưa đủ nền, cạnh tranh ngầm hoặc quá tải kiệt sức) cùng cách xử lý khôn khéo."
            ),
        },
        "love": {
            "title": f"CHUYÊN SÂU TÌNH CẢM, HÔN NHÂN & GIA ĐẠO NĂM {target_year}",
            "root": (
                "Phân tích thật thấm thía về cách bạn yêu thương, gắn bó và xây dựng gia đình: "
                "mẫu người bạn dễ bị thu hút, điều bạn thực sự cần ở một mối quan hệ bền lâu, "
                "những điểm dễ tạo khoảng cách hoặc hiểu lầm giữa hai người (cái tôi, cách giao tiếp, áp lực tài chính hay sự can thiệp từ bên ngoài)."
            ),
            "year_big": (
                f"Phân tích sâu vận tình cảm và không khí gia đạo trong giai đoạn này và năm {target_year} cho cả hai tình huống: "
                "nếu đang độc thân thì cơ duyên gặp gỡ người phù hợp đến từ môi trường nào; nếu đã có đôi/có gia đình thì năm nay tình cảm ấm lên hay cần cùng nhau vượt qua thử thách gì?"
            ),
            "monthly_focus": (
                "nhân duyên gặp gỡ, sự gắn kết vợ chồng/người yêu, chuyện hỷ sự/con cái/người thân trong nhà và những tháng dễ nóng nảy, hiểu lầm hoặc có người thứ ba/áp lực bên ngoài xen vào"
            ),
            "risks": (
                "Nêu rõ các vận hạn & điều cần đặc biệt giữ gìn trong chuyện tình cảm, gia đạo năm nay "
                "(lời nói lúc nóng giận, ghen tuông suy diễn, lạnh nhạt vì mải lo công việc, chuyện sức khỏe/hòa khí người thân trong nhà) kèm cách hóa giải nhẹ nhàng, tinh tế."
            ),
        },
        "fortune12": {
            "title": f"CHUYÊN SÂU VẬN HẠN, SỨC KHỎE & LỘ TRÌNH CHI TIẾT 12 THÁNG NĂM {target_year}",
            "root": (
                "Phân tích tổng thể sức đề kháng của bản mệnh và nhịp vận lớn 10 năm bạn đang đi qua: "
                "giai đoạn này nhìn chung đang đi lên, đi ngang tích lũy hay đang ở khúc cua chuyển đổi? "
                "Điểm mạnh giúp bạn vượt sóng và điểm yếu về thể chất, tinh thần hay thói quen sinh hoạt cần đặc biệt chăm sóc."
            ),
            "year_big": (
                f"Mổ xẻ thật kỹ toàn bộ vận hạn năm {target_year}: "
                "đâu là 2–3 điểm sáng may mắn lớn nhất trong năm, đâu là 2–3 thử thách trọng tâm phải chuẩn bị tâm thế trước "
                "(tiền bạc, công việc, sức khỏe, đi lại, gia đạo, giấy tờ pháp lý)."
            ),
            "monthly_focus": (
                "đầy đủ vận khí tổng thể từng tháng: công việc, tài lộc, sức khỏe, đi lại, mối quan hệ và điều cần đặc biệt lưu ý tránh rủi ro"
            ),
            "risks": (
                "Dành một phần thật rõ ràng, cụ thể cho **Các vận hạn & điều cần đặc biệt chú ý trong năm**: "
                "sức khỏe (những bộ phận/thói quen dễ xuống sức, giấc ngủ, căng thẳng), đi lại/xe cộ, giấy tờ pháp lý, thị phi và chuyện người thân — "
                "giải thích điềm tĩnh, thực tế, tuyệt đối không hù dọa, kèm cách phòng tránh và hóa giải đời thường."
            ),
        },
    }

    spec = topic_specs.get(topic)
    if not spec:
        return None

    return (
        f"Hãy viết một bài **LUẬN GIẢI CHUYÊN SÂU THỰC SỰ: {spec['title']}** ({scope_note}).\n"
        f"{style_reminder}\n"
        "YÊU CẦU CHIỀU SÂU BẮT BUỘC (TUYỆT ĐỐI KHÔNG VIẾT SƠ SÀI HAY LƯỚT CHUNG CHUNG):\n"
        "- Vì người xem đã chủ động chọn mục chuyên sâu này, hãy dành toàn bộ tâm huyết và chiều sâu phân tích thật kỹ, thật thấm, sát đời thực cho đúng chủ đề này.\n"
        "- Đọc kỹ dữ liệu 12 tháng đã tính sẵn trong JSON (`monthly_fortunes_12` / `monthly_liuyue_12` / `personal_months_12`) để luận chính xác từng tháng, tuyệt đối không bỏ sót tháng nào và không bịa dữ liệu.\n\n"
        "Bố cục 5 phần đầy đặn, mạch lạc (dùng tiêu đề `##` tự nhiên):\n"
        f"1. **Nền tảng gốc & câu chuyện dài hạn của bạn:** {spec['root']}\n"
        f"2. **Bức tranh vận lớn hiện tại & tổng quan năm {target_year}:** {spec['year_big']}\n"
        f"3. **Lộ trình diễn biến chi tiết đủ 12 tháng năm {target_year} (Tháng 1 đến Tháng 12):** "
        f"Chia thành 4 tiểu mục theo 4 quý (`### Quý 1: Tháng 1 – Tháng 3`, `### Quý 2: Tháng 4 – Tháng 6`, `### Quý 3: Tháng 7 – Tháng 9`, `### Quý 4: Tháng 10 – Tháng 12`). "
        f"Trong mỗi quý, hãy kể liền mạch bằng văn xuôi tự nhiên đi qua **từng tháng một** (ghi rõ Tháng 1, Tháng 2... kèm khoảng tháng Dương lịch nếu là lịch Âm để người xem dễ đối chiếu), phân tích kỹ về {spec['monthly_focus']}. "
        "Chốt rõ tháng nào là điểm sáng đẹp nhất để hành động và tháng nào cần giảm tốc giữ an toàn.\n"
        f"4. **Những vận hạn, rủi ro & điều cần đặc biệt lưu ý trong năm {target_year}:** {spec['risks']}\n"
        "5. **Lời khuyên thực tế & kế hoạch hành động để giữ lộc, hóa giải rủi ro:** Chốt lại 4–5 việc cụ thể, dễ làm ngay từ hôm nay."
    )


def _build_user_prompt(
    compact_data: Dict[str, Any],
    mode: str,
    focus_question: str,
    deep_topic: str = "",
) -> str:
    style_reminder = (
        "Hãy viết bằng giọng điệu ấm áp, tự nhiên, liền mạch như thầy xem ngồi đối diện trò chuyện và giải thích cho người bình thường dễ hiểu. "
        "Chia thành các đoạn văn xuôi trôi chảy có câu nối mượt mà, hạn chế tối đa gạch đầu dòng (chỉ dùng 3–5 ý ngắn ở phần lời khuyên cuối cùng nếu cần), "
        "không kẻ bảng rườm rà, không liệt kê hàng loạt tên cung hay thuật ngữ Hán–Việt nặng nề mà hãy chuyển hóa thẳng sang ngôn ngữ đời sống thực tế."
    )

    target_year = (
        (compact_data.get("tuvi") or {}).get("target_year_fortune", {}).get("target_solar_year")
        or (compact_data.get("bazi") or {}).get("target_liunian", {}).get("year")
        or (compact_data.get("numerology") or {}).get("personal_cycles", {}).get("target_year")
        or datetime.now().year
    )

    resolved_topic = _detect_deep_topic(deep_topic, focus_question)
    if mode in ("full", "tuvi", "bazi", "numerology", "all") and resolved_topic != "overview":
        deep_guide = _build_deep_topic_prompt(resolved_topic, mode, target_year, style_reminder)
        if deep_guide:
            focus_block = ""
            if focus_question.strip():
                focus_block = (
                    f"\n\n### TRỌNG TÂM / CÂU HỎI CỤ THỂ NGƯỜI XEM GỬI KÈM:\n"
                    f"> {focus_question.strip()}\n"
                    f"(Hãy lồng ghép và giải đáp trực diện, sâu sát từng khía cạnh câu hỏi này trong bài luận!)\n"
                )
            return (
                f"{deep_guide}{focus_block}\n\n"
                f"### DỮ LIỆU TÍNH TOÁN CHÍNH XÁC (JSON — CHỈ DÙNG ĐỂ ĐỌC HIỂU, KHÔNG LẶP LẠI THÔ):\n"
                f"```json\n{json.dumps(compact_data, ensure_ascii=False)}\n```"
            )

    mode_prompts = {
        "full": (
            f"Hãy viết một bài luận giải tổng hợp **thật kỹ, sâu sắc và dễ hiểu** cho năm {target_year} "
            f"(hòa quyện ngầm tinh hoa Tử Vi, Bát Tự Ngũ Hành và Thần Số Học thành một mạch kể chuyện thống nhất). {style_reminder}\n\n"
            "Bố cục gồm 6 phần đầy đặn, liền mạch (dùng tiêu đề `##` tự nhiên, thân thiện):\n"
            "1. **Con người, khí chất và điểm sáng tự nhiên của bạn:** Phân tích sâu nét tính cách cốt lõi, điểm mạnh trời phú và những trăn trở nội tâm bạn hay gặp.\n"
            "2. **Công việc, tiền bạc và nhà cửa/tài sản:** Phân tích kỹ cách bạn làm việc, kiếm tiền, giữ tiền, duyên đất đai tích sản và kiểu môi trường giúp bạn phát huy tốt nhất.\n"
            "3. **Tình cảm, gia đình và nhịp sức khỏe:** Chia sẻ sâu về cách bạn yêu thương, xây dựng tổ ấm, các mối quan hệ quý nhân và điểm sức khỏe nên chăm chút.\n"
            f"4. **Nhịp vận năm {target_year} & Lộ trình chi tiết 12 tháng (Tháng 1 đến Tháng 12):** "
            "Dựa vào dữ liệu 12 tháng đã tính sẵn trong JSON, chia thành 4 tiểu mục (`### Quý 1: Tháng 1 – Tháng 3`, `### Quý 2: Tháng 4 – Tháng 6`, `### Quý 3: Tháng 7 – Tháng 9`, `### Quý 4: Tháng 10 – Tháng 12`), kể liền mạch từng tháng một xem tháng nào thuận để đẩy mạnh, tháng nào nên đi chậm giữ chắc, kèm điểm trùng khớp nổi bật giữa các góc nhìn (có thể điểm nhẹ `🟢 ĐỒNG THUẬN CAO` hoặc `🟡 BÁN ĐỒNG THUẬN` ngay trong câu).\n"
            f"5. **Những vận hạn & điều cần đặc biệt lưu ý trong năm {target_year}:** Chỉ rõ các rủi ro dễ gặp về tiền bạc, giấy tờ, thị phi, đi lại và sức khỏe cùng cách phòng tránh nhẹ nhàng.\n"
            "6. **Vài lời nhắn gửi thiết thực cho chặng đường sắp tới:** Chốt lại 4–5 lời khuyên thật đời thường, dễ áp dụng ngay."
        ),
        "tuvi": (
            f"Hãy luận giải lá số Tử Vi **thật kỹ, sâu sắc và dễ hiểu** cho năm {target_year} (chỉ dùng dữ liệu Tử Vi, không trộn sang Bát Tự hay Thần Số Học). {style_reminder}\n"
            "Đặc biệt lưu ý: bớt tối đa việc nhắc tên 12 cung (Mệnh, Tài Bạch, Quan Lộc, Điền Trạch, Phu Thê...) và sao phụ rườm rà; hãy nói thẳng vào từng khía cạnh đời sống để người nghe thấy rõ chính mình.\n\n"
            "Bố cục gồm 6 phần đầy đặn, liền mạch:\n"
            "1. **Nét tính cách và cốt cách con người bạn:** Phân tích sâu tính cách bên ngoài, nội tâm bên trong, điểm mạnh nổi trội và điểm dễ tự làm mình mệt mỏi.\n"
            "2. **Đường công việc, sự nghiệp, tiền bạc và tài sản:** Cách bạn kiếm tiền, giữ tiền, duyên nhà cửa đất đai và những bước ngoặt thường gặp trong sự nghiệp.\n"
            "3. **Chuyện tình cảm, gia đạo và các mối quan hệ xung quanh:** Cách bạn đối đãi với người thương, không khí gia đình và cách nhận diện quý nhân, đối tác hợp vía.\n"
            f"4. **Vận trình giai đoạn hiện tại & Lộ trình 12 tháng năm {target_year}:** "
            "Phân tích kỹ đại vận 10 năm đang đi qua và bức tranh năm nay; dựa vào `monthly_fortunes_12` trong JSON, chia 4 tiểu mục (`### Quý 1: Tháng 1 – Tháng 3` đến `### Quý 4: Tháng 10 – Tháng 12`) kể liền mạch từng tháng Âm lịch (kèm khoảng tháng Dương tương ứng) xem tháng nào sáng lộc, tháng nào nên thận trọng.\n"
            f"5. **Những vận hạn & điều cần đặc biệt chú ý trong năm {target_year}:** Chỉ rõ các lưu ý về sức khỏe, tiền bạc, giấy tờ, lời ăn tiếng nói và cách ứng xử êm đẹp.\n"
            "6. **Lời khuyên thực tế để mọi việc hanh thông hơn:** Chốt 4–5 gợi ý dễ làm ngay."
        ),
        "bazi": (
            f"Hãy luận giải Bát Tự Ngũ Hành **thật kỹ, sâu sắc và dễ hiểu** cho năm {target_year} (chỉ dùng dữ liệu Bát Tự). {style_reminder}\n"
            "Không dùng các cụm chuyên môn nặng nề kiểu 'Đắc Lệnh Thất Địa', 'Điều Hầu Cùng Thông Bảo Giám'; hãy diễn giải thành câu chuyện về khí chất, sự cân bằng năng lượng và cách sống thuận tự nhiên.\n\n"
            "Bố cục gồm 6 phần đầy đặn, liền mạch:\n"
            "1. **Khí chất bẩm sinh và nguồn năng lượng cốt lõi của bạn.**\n"
            "2. **Công việc, tài lộc và môi trường giúp bạn phát triển thuận nhất.**\n"
            "3. **Chuyện tình cảm, các mối quan hệ và sức khỏe cần lưu ý.**\n"
            f"4. **Nhịp vận 10 năm hiện tại & Diễn biến 12 tháng năm {target_year}:** "
            "Dựa vào `monthly_liuyue_12` trong JSON, chia 4 quý (`### Quý 1` đến `### Quý 4`) kể liền mạch từng tháng (chỉ rõ tháng nào hợp năng lượng để bứt phá, tháng nào xung động cần điềm tĩnh giữ nhịp).\n"
            f"5. **Những vận hạn & điều cần đặc biệt lưu ý trong năm {target_year}:** Nêu rõ điểm dễ mất cân bằng về sức khỏe, tài chính, quan hệ và cách cân bằng lại.\n"
            "6. **Cách nuôi dưỡng năng lượng thuận lợi trong đời sống hàng ngày** (ngành nghề, môi trường, thói quen, màu sắc/hướng dễ ứng dụng)."
        ),
        "numerology": (
            f"Hãy luận giải hồ sơ Thần Số Học **thật sâu sắc, truyền cảm và chi tiết** cho năm {target_year} (chỉ dùng dữ liệu Thần Số Học). {style_reminder}\n\n"
            "Bố cục gồm 5 phần đầy đặn, liền mạch:\n"
            "1. **Bản sắc cốt lõi và tiếng nói bên trong bạn:** Kể liền mạch về con người bạn qua Con số Chủ đạo, khát khao nội tâm, cách bạn tỏa sáng ra bên ngoài và bài học trưởng thành quan trọng.\n"
            "2. **Dấu ấn từ tên gọi (và Nickname nếu có):** Giải thích kỹ xem tên khai sinh và tên gọi hàng ngày đang cộng hưởng, bù đắp điểm nào cho ngày sinh của bạn.\n"
            f"3. **Chặng đỉnh cao hiện tại & Lộ trình 12 tháng cá nhân năm {target_year}:** "
            "Dựa vào `personal_months_12` trong JSON, chia 4 quý (`### Quý 1: Tháng 1 – Tháng 3` đến `### Quý 4: Tháng 10 – Tháng 12`), kể liền mạch từng tháng Dương lịch xem tháng nào nên khởi động, tháng nào nên kết nối, tháng nào nên thu hoạch và tháng nào nên chậm lại nghỉ ngơi.\n"
            f"4. **Những điểm dễ vấp & điều cần lưu ý trong năm {target_year}:** Chỉ rõ những cái bẫy cảm xúc, tài chính hoặc quyết định vội vàng cần tránh trong nhịp năm cá nhân này.\n"
            "5. **Gợi ý nghề nghiệp và vài điều nên ưu tiên sắp tới:** Chốt 4–5 gợi ý gọn gàng, thực tế."
        ),
        "iching": (
            f"Hãy giải quẻ Kinh Dịch **thật kỹ, sâu sắc và thực tế** như một người thầy điềm đạm ngồi phân tích cặn kẽ từng lớp nghĩa cho người đang băn khoăn. {style_reminder}\n"
            "Không liệt kê khô cứng các thuật ngữ Lục Thân, Can Chi, Nhật Thần, Nguyệt Kiến, Phục Thần; hãy dịch thẳng sang diễn biến thực tế để người hỏi đọc xong hiểu rõ đường đi nước bước.\n\n"
            "Bố cục gồm 4 phần đầy đặn, liền mạch:\n"
            "1. **Trả lời thẳng vào điều bạn đang hỏi:** Chốt rõ ngay từ đầu xu hướng hiện tại đang thuận, cần chờ thêm hay nên thận trọng, và phần trăm thuận lợi nghiêng về phía nào.\n"
            "2. **Bối cảnh hiện tại, diễn biến ngầm & chiều hướng sắp tới:** Kể sâu vì sao sự việc đang ở trạng thái này, tâm thế của bạn và đối phương ra sao, nút thắt thật sự nằm ở đâu và giai đoạn tới sẽ xoay chuyển thế nào.\n"
            "3. **Thời điểm chuyển biến (Ứng kỳ) & Những rủi ro cần đặc biệt chú ý:** Chỉ rõ mốc thời gian (theo ngày/tuần/tháng) dễ thấy kết quả hoặc bước ngoặt, đồng thời cảnh báo những sơ suất, hiểu lầm hay rủi ro ngầm cần phòng trước.\n"
            "4. **Lời khuyên xử lý từng bước thực tế:** Chốt 4–5 việc cụ thể nên làm ngay để xoay chuyển cục diện theo hướng có lợi nhất."
        ),
        "qimen": (
            f"Hãy đọc bàn Kỳ Môn Độn Giáp **thật kỹ và thực tế** bằng ngôn ngữ đời thường để người bình thường áp dụng ngay được. {style_reminder}\n\n"
            "Bố cục gồm 4 phần đầy đặn, liền mạch:\n"
            "1. **Đánh giá sâu thế cục sự việc lúc này:** Tình thế đang nghiêng về phía bạn hay phía đối tác, có quý nhân hay trở lực ngầm nào không.\n"
            "2. **Phương hướng & khung thời gian đẹp nhất để hành động:** Chỉ rõ nên ưu tiên xuất hành, gặp gỡ, xem đất hay đàm phán theo hướng nào, tránh hướng nào.\n"
            "3. **Những rủi ro & điều cần đặc biệt lưu ý khi giao dịch/gặp gỡ:** Điểm nào dễ bị ép giá, chậm trễ hay hiểu sai ý.\n"
            "4. **Chiến lược ứng xử, đàm phán khéo léo:** Chốt 3–4 bước hành động cụ thể."
        ),
        "all": (
            f"Hãy viết một bài luận tổng hợp **thật sâu sắc, trọn vẹn và dễ hiểu** cho năm {target_year} "
            "(hòa quyện bức tranh bản mệnh dài hạn, lộ trình 12 tháng, vận hạn cần chú ý cùng câu trả lời trực diện từ quẻ dịch và phương hướng thuận lợi hiện tại). "
            f"{style_reminder}\n\n"
            "Bố cục gồm 5 phần đầy đặn, liền mạch:\n"
            "1. **Bức tranh con người, công việc, tiền bạc và tình cảm của bạn** (kèm đoạn đúc kết những điểm trùng khớp rõ nhất giữa các góc nhìn).\n"
            f"2. **Lộ trình 12 tháng năm {target_year} (chia 4 quý từ Tháng 1 đến Tháng 12):** Dựa vào dữ liệu 12 tháng trong JSON, điểm rõ từng tháng thuận lợi và từng tháng cần đi chậm lại.\n"
            f"3. **Những vận hạn & điều cần đặc biệt chú ý trong năm {target_year}** (sức khỏe, tiền bạc, giấy tờ, thị phi, gia đạo).\n"
            "4. **Giải đáp thẳng vào việc bạn đang băn khoăn lúc này** (xu hướng thuận hay chưa thuận, thời điểm chuyển biến và phương hướng đẹp để hành động).\n"
            "5. **Lời khuyên hành động thực tế** (4–5 ý ngắn gọn, dễ áp dụng ngay)."
        ),
    }

    guide = mode_prompts.get(mode, mode_prompts["full"])
    focus_block = ""
    if focus_question.strip():
        focus_block = (
            f"\n\n### CÂU HỎI / ĐIỀU NGƯỜI XEM ĐANG QUAN TÂM NHẤT:\n"
            f"> {focus_question.strip()}\n"
            f"(Hãy dành một phần trả lời thật thẳng thắn, tự nhiên, sâu sát và thực tế cho câu hỏi này dựa trên dữ liệu JSON, viết thành đoạn văn liền mạch dễ hiểu!)\n"
        )

    return (
        f"{guide}{focus_block}\n\n"
        f"### DỮ LIỆU TÍNH TOÁN CHÍNH XÁC (JSON — CHỈ DÙNG ĐỂ ĐỌC HIỂU, KHÔNG LẶP LẠI THÔ):\n"
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
    gen_cfg: Dict[str, Any] = {"maxOutputTokens": 16384}
    if model_id.startswith(("gemini-4", "gemini-3")):
        gen_cfg["thinkingConfig"] = {"thinkingLevel": "LOW"}
    elif model_id.startswith("gemini-2.5"):
        gen_cfg["temperature"] = 0.7
        gen_cfg["thinkingConfig"] = {"thinkingBudget": 0}
    else:
        gen_cfg["temperature"] = 0.7

    body = {
        "system_instruction": {"parts": [{"text": system_instruction}]},
        "contents": [{"role": "user", "parts": [{"text": user_prompt}]}],
        "generationConfig": gen_cfg,
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
    deep_topic = str(req_data.get("deep_topic", "")).strip().lower()
    requested_model = str(req_data.get("model", "")).strip()
    provided_code = str(req_data.get("access_code", "")).strip()

    user_key = (user_api_key or "").strip()
    using_byok = bool(user_key)

    if using_byok:
        api_key = user_key.strip('"').strip("'")
    else:
        api_key = _get_server_api_key()
        if not api_key:
            raise PermissionError(
                "Máy chủ chưa cấu hình GEMINI_API_KEY. "
                "Vui lòng nhập Gemini API Key miễn phí của bạn tại mục '🔑 Dùng API Key riêng' "
                "(hoặc chủ web cấu hình biến GEMINI_API_KEY trên Vercel/Render rồi bấm Redeploy)."
            )
        expected_code = os.environ.get("ACCESS_CODE", "").strip().strip('"').strip("'")
        if expected_code and provided_code != expected_code:
            raise PermissionError("Mã mời (Access Code) chưa đúng hoặc đang để trống. Hãy nhập đúng ACCESS_CODE đã cài trên Vercel (hoặc xóa biến ACCESS_CODE trên Vercel nếu muốn mở công khai không cần mã).")
        limit_err = _check_and_increment_rate_limit(client_ip)
        if limit_err:
            raise RuntimeError(limit_err)

    primary_model = DEFAULT_MODEL
    models_to_try = [primary_model] + [m for m in ALLOWED_MODEL_IDS if m != primary_model]

    system_instruction = _build_system_instruction(mode)
    compact_data = _compact_payload(payload, mode)
    user_prompt = _build_user_prompt(compact_data, mode, focus_question, deep_topic=deep_topic)

    # Chế độ "prepare": Trả siêu tốc (< 80ms) gói prompt đã ký HMAC để Vercel Edge Function stream SSE không bao giờ timeout!
    if str(req_data.get("action", "")).strip().lower() == "prepare":
        ts = int(time.time())
        sig = ""
        if not using_byok:
            sys_h = hashlib.sha256(system_instruction.encode("utf-8")).hexdigest()
            usr_h = hashlib.sha256(user_prompt.encode("utf-8")).hexdigest()
            msg = f"{ts}:{mode}:{sys_h}:{usr_h}".encode("ascii")
            sig = hmac.new(api_key.encode("utf-8"), msg, hashlib.sha256).hexdigest()
        return {
            "prepared": True,
            "mode": mode,
            "primary_model": primary_model,
            "models_to_try": models_to_try,
            "system_instruction": system_instruction,
            "user_prompt": user_prompt,
            "using_byok": using_byok,
            "ts": ts,
            "sig": sig,
        }

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
