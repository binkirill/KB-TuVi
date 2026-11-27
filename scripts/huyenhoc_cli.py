# -*- coding: utf-8 -*-
"""
huyenhoc_cli.py — CLI Điều Phối Tổng Hợp Đông - Tây của Skill kb-tuvi v3.0
Chạy độc lập bằng Python 3 Standard Library (0 pip dependencies, 0 PowerShell):
  - mode = full       : Chạy đồng thời Tử Vi Đẩu Số + Bát Tự Tứ Trụ + Thần Số Học + Kiểm chứng chéo Đông × Tây
  - mode = numerology : Chỉ chạy Thần Số Học Đa Phái (Pythagoras VN/Quốc tế + Chaldean + Ma trận 22 Arcana — không bắt buộc giờ sinh)
  - mode = tuvi       : Chỉ chạy Tử Vi Đẩu Số
  - mode = bazi       : Chỉ chạy Bát Tự Tứ Trụ
  - mode = iching     : Gieo & lập quẻ Kinh Dịch (Lục Hào Nạp Giáp + Mai Hoa + 64 Quẻ)
  - mode = qimen      : Lập bàn Kỳ Môn Độn Giáp Thời Gia
  - mode = all        : Chạy toàn bộ 5 hệ (Tử Vi + Bát Tự + Thần Số Học + Kinh Dịch + Kỳ Môn)

Ví dụ gọi chuẩn:
  python -X utf8 "G:/My Drive/Antigravity/Skills/kb-tuvi/scripts/huyenhoc_cli.py" --mode full --name "Nguyễn Minh Quân" --solar 1992-08-16 --time 09:30 --gender nam --place "Hà Nội" --target-year 2026 --html-out "_temp/laso.html"
  python -X utf8 "G:/My Drive/Antigravity/Skills/kb-tuvi/scripts/huyenhoc_cli.py" --mode numerology --name "Nguyễn Minh Quân" --nickname "Leo Quân" --solar 1992-08-16 --target-year 2026 --html-out "_temp/thansohoc.html"
"""

from __future__ import annotations
import argparse
import json
import os
import sys
from datetime import datetime
from typing import Any, Dict, List, Optional

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

from core_calendar import lunar_to_solar, compute_true_solar_time, build_time_sync_report
from engine_tuvi import compute_tuvi_chart
from engine_bazi import compute_bazi_chart
from engine_iching import cast_iching_full, compute_qimen_hourly
from engine_numerology import compute_numerology_profile
from render_chart_html import render_full_html_report


def build_cross_validation(
    tuvi_data: Optional[Dict[str, Any]],
    bazi_data: Optional[Dict[str, Any]],
    numerology_data: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Tạo bảng tổng hợp Kiểm Chứng Chéo Đông × Tây (Tử Vi × Bát Tự × Thần Số Học)."""
    result: Dict[str, Any] = {}

    if tuvi_data and bazi_data:
        dm = bazi_data["day_master"]
        ys = bazi_data["yongshen_guidance"]
        prof = tuvi_data["profile"]
        tf = tuvi_data["target_year_fortune"]

        active_dayun = next((d for d in bazi_data.get("dayun", []) if d.get("is_current")), None)
        active_daihan = tf.get("active_dai_han")

        result["bazi_anchor"] = (
            f"Nhật Chủ {dm['stem']} ({dm['element']}) — {dm['strength_assessment']}; "
            f"Hỷ/Dụng Phù Ức: {', '.join(ys['fuyi_favorable_elements'])}; Điều hầu: {ys['qiong_tong_tiaohou']}"
        )
        result["tuvi_anchor"] = (
            f"Bản mệnh {prof['ban_menh_nayin']}, {prof['cuc']}, Mệnh tại {prof['menh_palace']}, {prof['than_cu']}"
        )
        result["current_decade_sync"] = {
            "bazi_dayun": (
                f"{active_dayun['can_chi']} ({active_dayun['solar_years']} — {active_dayun['stem_ten_god']}/{active_dayun['branch_main_ten_god']})"
                if active_dayun else "Chưa khởi Đại vận"
            ),
            "tuvi_daihan": (
                f"{active_daihan['can_chi']} cung {active_daihan['palace_origin']} ({active_daihan['age_range']})"
                if active_daihan else "Chưa vào Đại hạn"
            ),
        }

    if numerology_data:
        cn = numerology_data["core_numbers"]
        lp = cn["life_path"]
        expr = cn.get("expression")
        soul = cn.get("soul_urge")
        py = numerology_data["personal_cycles"]["personal_year"]
        py_theme = numerology_data["personal_cycles"]["personal_year_theme"]["phase"]
        active_pin = next((p for p in numerology_data.get("pinnacles", []) if p.get("is_current")), None)

        result["numerology_anchor"] = (
            f"Số Chủ Đạo {lp['code']} ({lp['archetype']['title']})"
            + (f" | Sứ Mệnh {expr['code']} | Linh Hồn {soul['code']}" if expr and soul else "")
            + f" | Năm Cá Nhân số {py} ({py_theme})"
            + (f" | Đỉnh Cao #{active_pin['stage']}: Số {active_pin['pinnacle_code']} (Thử thách {active_pin['challenge_number']})" if active_pin else "")
        )

        # Kiểm chứng chéo Đông × Tây (Bát Tự × Tử Vi × Thần Số Học)
        if bazi_data and tuvi_data:
            fav_elems = set(bazi_data["yongshen_guidance"]["fuyi_favorable_elements"])
            lp_elems = set(lp["archetype"].get("element_affinity", []))
            expr_elems = set(expr["archetype"].get("element_affinity", [])) if expr else set()

            elem_overlap = sorted(list(fav_elems & (lp_elems | expr_elems)))
            expansion_py = py in (1, 3, 5, 8)
            consolidation_py = py in (2, 4, 6, 7, 9)

            empty_arrows = [a["name"] for a in numerology_data["grids_3x3"]["birth_chart"]["empty_arrows"]]
            missing_nums = numerology_data["name_breakdown"].get("karmic_lessons_missing", [])

            result["east_west_synthesis"] = {
                "element_number_resonance": (
                    f"🟢 CỘNG HƯỞNG TỐT: Năng lượng Số Chủ Đạo/Sứ Mệnh tương thông với Hỷ/Dụng Thần Bát Tự ({', '.join(elem_overlap)})."
                    if elem_overlap else
                    f"🟡 BỔ KHUYẾT CHÉO: Số Chủ Đạo {lp['code']} thiên về ({', '.join(lp['archetype']['element_affinity'])}), cần chủ động bồi đắp thêm Hỷ/Dụng Thần Bát Tự ({', '.join(fav_elems)}) trong môi trường sống & nghề nghiệp."
                ),
                "annual_rhythm_alignment": (
                    f"Năm Cá Nhân số {py} ({py_theme}) thuộc pha {'MỞ RỘNG / BỨT PHÁ (1-3-5-8)' if expansion_py else 'TÍCH LŨY / CHỐT NỀN / CHIÊM NGHIỆM (2-4-6-7-9)'} — "
                    f"cần đặt cạnh Lưu Niên Tử Vi ({tuvi_data['target_year_fortune']['liunian_menh_palace']}) & Đại Vận Bát Tự để quyết định tốc độ tiến/thủ."
                ),
                "blindspot_remedy": {
                    "birth_chart_empty_arrows": empty_arrows,
                    "name_missing_numbers": missing_nums,
                    "chaldean_name_rank": numerology_data["chaldean_name"]["compound_rank"] if numerology_data.get("chaldean_name") else None,
                },
            }

    result["cross_check_protocol"] = [
        "1. Khí chất & Thiên hướng: Đối chiếu Tam Phương Tứ Chính Tử Vi × Thập Thần Đề Cương Bát Tự × Tam Giác Vàng (Đường Đời - Sứ Mệnh - Linh Hồn).",
        "2. Nhịp điệu Năm Xem: Khi Đại Hạn/Lưu Niên Đông Phương đắc Lộc/Quyền/Hỷ Dụng VÀ Năm Cá Nhân Thần Số Học rơi vào sóng 1, 3, 5, 8 -> Nhãn [🟢 ĐẠI ĐỒNG THUẬN ĐÔNG - TÂY].",
        "3. Nếu Đông Phương báo Cát nhưng Năm Cá Nhân rơi vào năm trũng 4 hoặc 7 -> Nhãn [🟡 THÀNH TỰU QUA KỶ LUẬT & CHIỀU SÂU CHUYÊN MÔN, TRÁNH ĐẦU CƠ NÓNG VỘI].",
        "4. Bù khuyết thực tiễn: Kết hợp Dụng Thần Ngũ Hành với bài tập lấp Mũi Tên Trống & Số Khuyết Họ Tên.",
    ]
    return result


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="kb-tuvi v3.0 — Engine Huyền Học & Thần Số Học Đông-Tây Zero-Hallucination")
    p.add_argument("--mode", choices=["full", "numerology", "tuvi", "bazi", "iching", "qimen", "all"], default="full")
    p.add_argument("--name", default="", help="Họ tên khai sinh đầy đủ có dấu (VD: Nguyễn Minh Quân)")
    p.add_argument("--nickname", default="", help="Tên thường gọi / Nghệ danh / Tên thương hiệu cần chấm điểm (tùy chọn)")
    p.add_argument("--num-school", choices=["vn", "intl"], default="vn", help="Trường phái Thần số học: vn (Nhân số học VN giữ số 10) | intl (Pythagoras Quốc tế 3 trụ)")
    p.add_argument("--y-mode", choices=["contextual", "always_vowel", "always_consonant"], default="contextual", help="Quy tắc phân loại chữ Y nguyên âm/phụ âm")
    p.add_argument("--solar", default="", help="Ngày sinh Dương lịch YYYY-MM-DD")
    p.add_argument("--lunar", default="", help="Ngày sinh Âm lịch YYYY-MM-DD (nếu không nhớ Dương lịch)")
    p.add_argument("--leap", action="store_true", help="Đánh dấu tháng Âm lịch là tháng Nhuận")
    p.add_argument("--time", default="12:00", help="Giờ phút sinh HH:MM (24h)")
    p.add_argument("--gender", default="nam", help="nam / nu")
    p.add_argument("--place", default="Hà Nội", help="Tỉnh/thành nơi sinh (để hiệu chỉnh Giờ Chân Thái Dương)")
    p.add_argument("--longitude", type=float, default=None, help="Kinh độ Đông cụ thể (nếu ngoài VN)")
    p.add_argument("--tz", type=float, default=7.0, help="Múi giờ đồng hồ đầu vào (mặc định 7.0 = Việt Nam)")
    p.add_argument("--calendar-std", choices=["vn", "intl"], default="vn", help="Chuẩn lịch Âm cho Tử Vi: vn (UTC+7 Hồ Ngọc Đức) hoặc intl (UTC+8 iztro/6tail)")
    p.add_argument("--tuvi-school", choices=["iztro", "vn"], default="iztro", help="Quy tắc an Hỏa/Linh: iztro (Toàn Thư quốc tế) hoặc vn (Nam Phái VN)")
    p.add_argument("--zi-sect", type=int, choices=[1, 2], default=2, help="Chế độ Dạ Tý 23:00-23:59 cho Bát Tự: 2=Giữ Can Ngày, 1=Sang ngày mới")
    p.add_argument("--use-clock-time", action="store_true", help="Dùng thẳng giờ đồng hồ thay vì Giờ Chân Thái Dương")
    p.add_argument("--target-year", type=int, default=datetime.now().year, help="Năm Dương lịch cần xem Lưu niên / Năm cá nhân")
    p.add_argument("--question", default="", help="Câu hỏi cụ thể khi gieo quẻ Kinh Dịch / Kỳ Môn")
    p.add_argument("--iching-method", choices=["coins_random", "manual_lines", "numbers", "time"], default="coins_random")
    p.add_argument("--lines", default="", help="6 hào từ dưới lên phân cách dấu phẩy, VD: 7,8,9,7,6,8")
    p.add_argument("--numbers", default="", help="2 hoặc 3 con số cho Mai Hoa Dịch Số, VD: 18,25,7")
    p.add_argument("--json-out", default="", help="Đường dẫn lưu file JSON kết quả")
    p.add_argument("--html-out", default="", help="Đường dẫn lưu file HTML Lá số & Mệnh thư")
    return p.parse_args()


def main() -> None:
    args = parse_args()

    hh, mm_time = 12, 0
    if args.time:
        parts = args.time.strip().split(":")
        hh = int(parts[0])
        mm_time = int(parts[1]) if len(parts) > 1 else 0

    if args.solar:
        sy, sm, sd = [int(x) for x in args.solar.strip().split("-")]
    elif args.lunar:
        ly, lm, ld = [int(x) for x in args.lunar.strip().split("-")]
        cal_tz = 8.0 if args.calendar_std == "intl" else args.tz
        sd, sm, sy = lunar_to_solar(ld, lm, ly, 1 if args.leap else 0, cal_tz)
    else:
        now = datetime.now()
        sy, sm, sd, hh, mm_time = now.year, now.month, now.day, now.hour, now.minute

    solar_iso = f"{sy:04d}-{sm:02d}-{sd:02d}"
    dt_clock = datetime(sy, sm, sd, hh, mm_time)
    tst_info = compute_true_solar_time(dt_clock, place=args.place, longitude=args.longitude, tz_hours=args.tz)
    sync_report = build_time_sync_report(dt_clock, place=args.place, longitude=args.longitude, tz_hours=args.tz)
    dt_eff: datetime = dt_clock if args.use_clock_time else tst_info["true_datetime"]  # type: ignore

    payload: Dict[str, Any] = {
        "meta": {
            "name": args.name,
            "nickname": args.nickname,
            "mode": args.mode,
            "gender": args.gender,
            "solar_date": solar_iso,
            "place": tst_info["place"],
            "longitude": tst_info["longitude"],
            "timezone_utc": args.tz,
            "calendar_std": args.calendar_std,
            "tuvi_school": args.tuvi_school,
            "numerology_school": args.num_school,
            "zi_sect": args.zi_sect,
            "clock_time": tst_info["clock_time"],
            "true_solar_time": tst_info["true_solar_time"],
            "time_mode_used": "Giờ Đồng Hồ" if args.use_clock_time else "Giờ Chân Thái Dương",
            "total_solar_offset_min": tst_info["total_offset_min"],
            "time_sync_verification": sync_report,
            "branch_boundary_warning": (
                f"CẢNH BÁO GIÁP RANH CANH GIỜ: Giờ đồng hồ là giờ {tst_info['clock_branch_name']}, nhưng Giờ Chân Thái Dương là giờ {tst_info['true_branch_name']}! Bắt buộc hỏi đương số 2-3 sự kiện quá khứ để nghiệm lý định giờ sinh!"
                if (args.mode in ("full", "tuvi", "bazi", "all") and tst_info["branch_changed"]) else None
            ),
        }
    }

    if args.mode in ("full", "tuvi", "all"):
        payload["tuvi"] = compute_tuvi_chart(
            dt_effective=dt_eff,
            gender=args.gender,
            tz_hours=args.tz,
            target_year=args.target_year,
            calendar_std=args.calendar_std,
            tuvi_school=args.tuvi_school,
        )

    if args.mode in ("full", "bazi", "all"):
        payload["bazi"] = compute_bazi_chart(
            dt_solar=dt_eff,
            gender=args.gender,
            tz_hours=args.tz,
            target_year=args.target_year,
            late_zi_mode="next_day" if args.zi_sect == 1 else "split",
            dt_clock_for_jieqi=dt_clock,
        )

    if args.mode in ("full", "numerology", "all"):
        # Thần số học luôn tính trên Ngày sinh Dương lịch trên giấy tờ/đồng hồ (solar_iso)
        payload["numerology"] = compute_numerology_profile(
            birth_date_solar=solar_iso,
            full_name=args.name,
            nickname=args.nickname,
            target_year=args.target_year,
            school=args.num_school,
            y_mode=args.y_mode,
        )

    if ("tuvi" in payload and "bazi" in payload) or ("numerology" in payload and ("tuvi" in payload or "bazi" in payload)):
        payload["cross_validation"] = build_cross_validation(
            payload.get("tuvi"),
            payload.get("bazi"),
            payload.get("numerology"),
        )

    if args.mode in ("iching", "all"):
        manual_lines = [int(x.strip()) for x in args.lines.split(",") if x.strip()] if args.lines else None
        num_list = [int(x.strip()) for x in args.numbers.split(",") if x.strip()] if args.numbers else None
        payload["iching"] = cast_iching_full(
            dt_cast=dt_clock,
            method=args.iching_method,
            manual_lines=manual_lines,
            numbers=num_list,
            question=args.question,
            tz_hours=args.tz,
        )

    if args.mode in ("qimen", "all"):
        payload["qimen"] = compute_qimen_hourly(dt_clock, tz_hours=args.tz)

    if args.json_out:
        os.makedirs(os.path.dirname(os.path.abspath(args.json_out)), exist_ok=True)
        with open(args.json_out, "w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, indent=2, default=str)

    if args.html_out:
        os.makedirs(os.path.dirname(os.path.abspath(args.html_out)), exist_ok=True)
        html_str = render_full_html_report(payload)
        with open(args.html_out, "w", encoding="utf-8") as f:
            f.write(html_str)
        payload["meta"]["html_report_saved"] = os.path.abspath(args.html_out)

    sys.stdout.reconfigure(encoding="utf-8")  # type: ignore
    print(json.dumps(payload, ensure_ascii=False, indent=2, default=str))


if __name__ == "__main__":
    main()
