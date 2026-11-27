# -*- coding: utf-8 -*-
"""
gui_server.py — Máy chủ Web Studio & REST API Đông - Tây (KB-TUVI v3.0 WEB-READY + GEMINI AI)
Kiến trúc Zero-Dependency Python 3 Standard Library (ThreadingHTTPServer + CORS JSON REST API + Vanilla SVG/HTML5):
  - Hỗ trợ trọn bộ 5 Engine: Tử Vi Đẩu Số + Bát Tự Tứ Trụ + Thần Số Học Đa Phái + Kinh Dịch Lục Hào + Kỳ Môn Độn Giáp.
  - Tích hợp sẵn Gemini API Free (/api/config, /api/interpret) và plugin giao diện (/assets/gemini_ai_addon.js).
  - Chạy đồng nhất 1 mã nguồn duy nhất cho cả Localhost, Render.com và Vercel Serverless.
"""

from __future__ import annotations
import argparse
import json
import os
import sys
import webbrowser
from datetime import datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any, Dict, List, Tuple

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SKILL_ROOT = os.path.dirname(SCRIPT_DIR)
GUI_HTML_PATH = os.path.join(SKILL_ROOT, "assets", "studio_gui.html")
AI_ADDON_JS_PATH = os.path.join(SKILL_ROOT, "assets", "gemini_ai_addon.js")
JS_SDK_PATH = os.path.join(SCRIPT_DIR, "web_numerology_sdk.js")

if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

from core_calendar import lunar_to_solar, compute_true_solar_time, build_time_sync_report
from engine_tuvi import compute_tuvi_chart
from engine_bazi import compute_bazi_chart
from engine_iching import cast_iching_full, compute_qimen_hourly
from engine_numerology import compute_numerology_profile
from huyenhoc_cli import build_cross_validation
from render_chart_html import render_full_html_report
from gemini_interpreter import get_public_config, interpret_with_gemini, load_local_dotenv


def compute_studio_payload(req: Dict[str, Any]) -> Dict[str, Any]:
    """Hàm xử lý trung tâm nhận JSON từ Web/GUI và trả về trọn bộ dữ liệu 5 hệ Đông - Tây."""
    name = str(req.get("name", "")).strip()
    nickname = str(req.get("nickname", "")).strip()
    num_school = str(req.get("num_school", "vn")).strip()
    y_mode = str(req.get("y_mode", "contextual")).strip()
    gender = str(req.get("gender", "nam")).strip()
    cal_input_type = str(req.get("date_type", "solar")).strip()  # "solar" | "lunar"
    date_str = str(req.get("date", "1990-05-15")).strip()
    is_leap = bool(req.get("is_leap", False))
    time_str = str(req.get("time", "09:30")).strip()
    place = str(req.get("place", "Hà Nội")).strip()
    lon_raw = req.get("longitude")
    longitude = float(lon_raw) if (lon_raw is not None and str(lon_raw).strip() != "") else None
    tz_hours = float(req.get("tz", 7.0))
    use_true_solar = bool(req.get("use_true_solar", True))
    calendar_std = str(req.get("calendar_std", "vn")).strip()
    tuvi_school = str(req.get("tuvi_school", "iztro")).strip()
    zi_sect = int(req.get("zi_sect", 2))
    target_year = int(req.get("target_year", datetime.now().year))

    t_parts = time_str.split(":")
    hh = int(t_parts[0]) if t_parts and t_parts[0] else 12
    mm_t = int(t_parts[1]) if len(t_parts) > 1 else 0

    d_parts = [int(x) for x in date_str.split("-")]
    if cal_input_type == "lunar":
        ly, lm, ld = d_parts[0], d_parts[1], d_parts[2]
        cal_tz = 8.0 if calendar_std == "intl" else tz_hours
        sd, sm, sy = lunar_to_solar(ld, lm, ly, 1 if is_leap else 0, cal_tz)
    else:
        sy, sm, sd = d_parts[0], d_parts[1], d_parts[2]

    solar_iso = f"{sy:04d}-{sm:02d}-{sd:02d}"
    dt_clock = datetime(sy, sm, sd, hh, mm_t)
    tst_info = compute_true_solar_time(dt_clock, place=place, longitude=longitude, tz_hours=tz_hours)
    sync_report = build_time_sync_report(dt_clock, place=place, longitude=longitude, tz_hours=tz_hours)
    dt_eff = tst_info["true_datetime"] if use_true_solar else dt_clock

    tuvi_data = compute_tuvi_chart(
        dt_effective=dt_eff,  # type: ignore
        gender=gender,
        tz_hours=tz_hours,
        target_year=target_year,
        calendar_std=calendar_std,
        tuvi_school=tuvi_school,
    )
    bazi_data = compute_bazi_chart(
        dt_solar=dt_eff,  # type: ignore
        gender=gender,
        tz_hours=tz_hours,
        target_year=target_year,
        late_zi_mode="next_day" if zi_sect == 1 else "split",
        dt_clock_for_jieqi=dt_clock,
    )
    numerology_data = compute_numerology_profile(
        birth_date_solar=solar_iso,
        full_name=name if name and name != "Bạn" else "",
        nickname=nickname,
        target_year=target_year,
        school=num_school,
        y_mode=y_mode,
    )

    cast_dt_str = str(req.get("cast_datetime", "")).strip()
    dt_cast = datetime.strptime(cast_dt_str, "%Y-%m-%dT%H:%M") if cast_dt_str else datetime.now()

    iching_method = str(req.get("iching_method", "coins_random")).strip()
    lines_raw = str(req.get("lines", "")).strip()
    nums_raw = str(req.get("numbers", "")).strip()
    question = str(req.get("question", "")).strip()

    manual_lines = [int(x.strip()) for x in lines_raw.split(",") if x.strip()] if lines_raw else None
    num_list = [int(x.strip()) for x in nums_raw.split(",") if x.strip()] if nums_raw else None

    iching_data = cast_iching_full(
        dt_cast=dt_cast,
        method=iching_method,
        manual_lines=manual_lines,
        numbers=num_list,
        question=question,
        tz_hours=tz_hours,
    )
    qimen_data = compute_qimen_hourly(dt_cast, tz_hours=tz_hours)

    payload: Dict[str, Any] = {
        "meta": {
            "name": name or "Đương Số",
            "nickname": nickname,
            "gender": gender,
            "solar_date": solar_iso,
            "place": tst_info["place"],
            "longitude": tst_info["longitude"],
            "timezone_utc": tz_hours,
            "calendar_std": calendar_std,
            "tuvi_school": tuvi_school,
            "numerology_school": num_school,
            "zi_sect": zi_sect,
            "clock_time": tst_info["clock_time"],
            "true_solar_time": tst_info["true_solar_time"],
            "time_mode_used": "Giờ Chân Thái Dương" if use_true_solar else "Giờ Đồng Hồ",
            "total_solar_offset_min": tst_info["total_offset_min"],
            "time_sync_verification": sync_report,
            "branch_boundary_warning": (
                f"CẢNH BÁO GIÁP RANH CANH GIỜ: Giờ đồng hồ là giờ {tst_info['clock_branch_name']}, nhưng Giờ Chân Thái Dương là giờ {tst_info['true_branch_name']}! Hãy đối chiếu 2-3 sự kiện quá khứ để nghiệm lý định giờ sinh!"
                if tst_info["branch_changed"] else None
            ),
        },
        "tuvi": tuvi_data,
        "bazi": bazi_data,
        "numerology": numerology_data,
        "cross_validation": build_cross_validation(tuvi_data, bazi_data, numerology_data),
        "iching": iching_data,
        "qimen": qimen_data,
    }
    payload["export_html"] = render_full_html_report(payload, title=f"Hồ Sơ Đông-Tây — {name or 'Đương Số'}")
    return payload


def evaluate_candidate_names(req: Dict[str, Any]) -> List[Dict[str, Any]]:
    """API chấm điểm hàng loạt Tên dự kiến (đặt tên con / nghệ danh / thương hiệu) theo Ngày sinh."""
    birth_date = str(req.get("date", "2026-01-01")).strip()
    candidates = req.get("candidates", [])
    school = str(req.get("num_school", "vn")).strip()
    y_mode = str(req.get("y_mode", "contextual")).strip()

    ranked: List[Dict[str, Any]] = []
    rank_scores = {"Thượng Cát": 30, "Đại Cát": 24, "Cát": 18, "Khá Cát": 14, "Trung tính": 6, "Cảnh báo": -8, "Thận trọng": -12}

    for cand in candidates:
        cname = str(cand).strip()
        if not cname:
            continue
        prof = compute_numerology_profile(birth_date_solar=birth_date, full_name=cname, school=school, y_mode=y_mode)
        cn = prof["core_numbers"]
        chal = prof.get("chaldean_name") or {}
        filled = prof["name_breakdown"].get("filled_birth_chart_gaps", [])
        karmic_cnt = len(prof.get("karmic_debts", []))
        bridge_lp_ex = cn["bridges"].get("life_path_to_expression") or 0

        score = 60
        score += rank_scores.get(chal.get("compound_rank", "Trung tính"), 0)
        score += min(15, len(filled) * 4)
        score -= karmic_cnt * 10
        if bridge_lp_ex in (0, 1, 2):
            score += 8
        score = max(10, min(100, score))

        ranked.append({
            "name": cname,
            "score_100": score,
            "life_path": cn["life_path"]["code"],
            "expression": cn["expression"]["code"] if cn.get("expression") else "",
            "soul_urge": cn["soul_urge"]["code"] if cn.get("soul_urge") else "",
            "personality": cn["personality"]["code"] if cn.get("personality") else "",
            "chaldean_compound": f"{chal.get('compound_number', '')}/{chal.get('single_digit', '')}",
            "chaldean_rank": chal.get("compound_rank", ""),
            "chaldean_title": chal.get("compound_title", ""),
            "filled_birth_gaps": filled,
            "karmic_debts": [k["code"] for k in prof.get("karmic_debts", [])],
        })

    ranked.sort(key=lambda x: x["score_100"], reverse=True)
    return ranked


def dispatch_get(path: str) -> Tuple[int, str, bytes]:
    """Router GET dùng chung cho cả Localhost, Render và Vercel Serverless."""
    clean_path = path.split("?", 1)[0].rstrip("/") or "/"
    if clean_path in ("/", "/index.html", "/api/index", "/api/index.py"):
        with open(GUI_HTML_PATH, "rb") as f:
            return 200, "text/html; charset=utf-8", f.read()
    if clean_path in ("/assets/gemini_ai_addon.js", "/api/addon", "/api/addon.py"):
        with open(AI_ADDON_JS_PATH, "rb") as f:
            return 200, "application/javascript; charset=utf-8", f.read()
    if clean_path.startswith("/assets/images/"):
        img_name = os.path.basename(clean_path)
        img_path = os.path.join(SKILL_ROOT, "assets", "images", img_name)
        if os.path.isfile(img_path):
            ext = os.path.splitext(img_name)[1].lower()
            mime = {
                ".png": "image/png",
                ".jpg": "image/jpeg",
                ".jpeg": "image/jpeg",
                ".webp": "image/webp",
                ".gif": "image/gif",
                ".svg": "image/svg+xml",
            }.get(ext, "application/octet-stream")
            with open(img_path, "rb") as f:
                return 200, mime, f.read()
    if clean_path in ("/sdk/numerology.js", "/api/sdk-numerology", "/api/sdk-numerology.py"):
        with open(JS_SDK_PATH, "rb") as f:
            return 200, "application/javascript; charset=utf-8", f.read()
    if clean_path == "/api/health":
        raw = json.dumps({
            "ok": True,
            "service": "kb-tuvi-studio-v3",
            "engines": ["tuvi", "bazi", "numerology", "iching", "qimen", "east_west_cross_validation", "gemini_ai"],
        }, ensure_ascii=False).encode("utf-8")
        return 200, "application/json; charset=utf-8", raw
    if clean_path == "/api/config":
        raw = json.dumps({"ok": True, "config": get_public_config()}, ensure_ascii=False).encode("utf-8")
        return 200, "application/json; charset=utf-8", raw
    raw = json.dumps({"ok": False, "error": f"Not Found: {clean_path}"}, ensure_ascii=False).encode("utf-8")
    return 404, "application/json; charset=utf-8", raw


def dispatch_post(
    path: str,
    body_bytes: bytes,
    headers: Any = None,
    client_ip: str = "127.0.0.1",
) -> Tuple[int, str, bytes]:
    """Router POST dùng chung cho cả Localhost, Render và Vercel Serverless."""
    clean_path = path.split("?", 1)[0].rstrip("/") or "/"
    try:
        body_text = body_bytes.decode("utf-8") if body_bytes else "{}"
        req_data = json.loads(body_text) if body_text.strip() else {}
    except Exception as exc:
        raw = json.dumps({"ok": False, "error": f"JSON không hợp lệ: {exc}"}, ensure_ascii=False).encode("utf-8")
        return 400, "application/json; charset=utf-8", raw

    if clean_path == "/api/analyze":
        try:
            result = compute_studio_payload(req_data)
            raw = json.dumps({"ok": True, "data": result}, ensure_ascii=False, default=str).encode("utf-8")
            return 200, "application/json; charset=utf-8", raw
        except Exception as exc:
            raw = json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False).encode("utf-8")
            return 400, "application/json; charset=utf-8", raw

    if clean_path == "/api/numerology":
        try:
            prof = compute_numerology_profile(
                birth_date_solar=str(req_data.get("date", "1992-08-16")).strip(),
                full_name=str(req_data.get("name", "")).strip(),
                nickname=str(req_data.get("nickname", "")).strip(),
                target_year=int(req_data.get("target_year", datetime.now().year)),
                school=str(req_data.get("num_school", "vn")).strip(),
                y_mode=str(req_data.get("y_mode", "contextual")).strip(),
            )
            raw = json.dumps({"ok": True, "data": prof}, ensure_ascii=False, default=str).encode("utf-8")
            return 200, "application/json; charset=utf-8", raw
        except Exception as exc:
            raw = json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False).encode("utf-8")
            return 400, "application/json; charset=utf-8", raw

    if clean_path in ("/api/name-check", "/api/name_check"):
        try:
            ranked = evaluate_candidate_names(req_data)
            raw = json.dumps({"ok": True, "data": ranked}, ensure_ascii=False, default=str).encode("utf-8")
            return 200, "application/json; charset=utf-8", raw
        except Exception as exc:
            raw = json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False).encode("utf-8")
            return 400, "application/json; charset=utf-8", raw

    if clean_path == "/api/interpret":
        try:
            user_api_key = ""
            if headers is not None:
                user_api_key = headers.get("X-Gemini-Api-Key", "") or headers.get("x-gemini-api-key", "") or ""
            result = interpret_with_gemini(req_data, user_api_key=user_api_key, client_ip=client_ip)
            raw = json.dumps({"ok": True, "data": result}, ensure_ascii=False, default=str).encode("utf-8")
            return 200, "application/json; charset=utf-8", raw
        except PermissionError as exc:
            raw = json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False).encode("utf-8")
            return 401, "application/json; charset=utf-8", raw
        except ValueError as exc:
            raw = json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False).encode("utf-8")
            return 400, "application/json; charset=utf-8", raw
        except Exception as exc:
            raw = json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False).encode("utf-8")
            return 502, "application/json; charset=utf-8", raw

    raw = json.dumps({"ok": False, "error": f"Not Found: {clean_path}"}, ensure_ascii=False).encode("utf-8")
    return 404, "application/json; charset=utf-8", raw


class StudioRequestHandler(BaseHTTPRequestHandler):
    def log_message(self, format: str, *args: Any) -> None:
        pass

    def _extract_client_ip(self) -> str:
        xff = self.headers.get("X-Forwarded-For", "")
        if xff:
            return xff.split(",")[0].strip()
        if self.client_address:
            return str(self.client_address[0])
        return "127.0.0.1"

    def _write_response(self, status: int, content_type: str, raw: bytes) -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(raw)))
        if content_type.startswith("text/html"):
            self.send_header("Cache-Control", "no-store, no-cache, must-revalidate, max-age=0")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization, X-Gemini-Api-Key")
        self.end_headers()
        self.wfile.write(raw)

    def do_OPTIONS(self) -> None:
        self._write_response(204, "text/plain; charset=utf-8", b"")

    def do_GET(self) -> None:
        status, content_type, raw = dispatch_get(self.path)
        self._write_response(status, content_type, raw)

    def do_POST(self) -> None:
        length = int(self.headers.get("Content-Length", "0") or "0")
        body = self.rfile.read(length) if length > 0 else b"{}"
        status, content_type, raw = dispatch_post(
            self.path, body, self.headers, client_ip=self._extract_client_ip()
        )
        self._write_response(status, content_type, raw)


def main() -> None:
    load_local_dotenv()
    default_port = int(os.environ.get("PORT", "8765") or "8765")
    default_host = "0.0.0.0" if os.environ.get("PORT") else "127.0.0.1"

    parser = argparse.ArgumentParser(description="Khởi chạy giao diện đồ họa & REST API KB-TUVI STUDIO v3.0")
    parser.add_argument("--host", default=default_host)
    parser.add_argument("--port", type=int, default=default_port)
    parser.add_argument("--no-browser", action="store_true", help="Không tự động mở trình duyệt")
    args = parser.parse_args()

    server = ThreadingHTTPServer((args.host, args.port), StudioRequestHandler)
    display_host = "127.0.0.1" if args.host == "0.0.0.0" else args.host
    url = f"http://{display_host}:{args.port}"
    try:
        sys.stdout.reconfigure(encoding="utf-8")  # type: ignore
    except Exception:
        pass
    print(f"☯️ KB-TUVI STUDIO v3.0 (Tử Vi × Bát Tự × Thần Số Học × Kinh Dịch × Gemini AI) đang chạy tại: {url}")
    if not args.no_browser and not os.environ.get("PORT"):
        webbrowser.open(url)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nĐã dừng KB-TUVI STUDIO.")
        server.server_close()


if __name__ == "__main__":
    main()
