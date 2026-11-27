# -*- coding: utf-8 -*-
"""
huyenhoc_cli.py — CLI Điều Phối Tổng Hợp của Skill kb-tuvi
Chạy độc lập bằng Python 3 Standard Library (0 pip dependencies, 0 PowerShell):
  - mode = full   : Chạy đồng thời Tử Vi Đẩu Số + Bát Tự Tứ Trụ + Kiểm chứng chéo (Cross-Validation)
  - mode = tuvi   : Chỉ chạy Tử Vi Đẩu Số
  - mode = bazi   : Chỉ chạy Bát Tự Tứ Trụ
  - mode = iching : Gieo & lập quẻ Kinh Dịch (Lục Hào Nạp Giáp + Mai Hoa + 64 Quẻ)
  - mode = qimen  : Lập bàn Kỳ Môn Độn Giáp Thời Gia
  - mode = all    : Chạy toàn bộ Tử Vi + Bát Tự + Kinh Dịch + Kỳ Môn

Ví dụ gọi chuẩn:
  python -X utf8 "G:/My Drive/Antigravity/Skills/kb-tuvi/scripts/huyenhoc_cli.py" --mode full --solar 1990-05-15 --time 09:30 --gender nam --place "Hà Nội" --target-year 2026 --html-out "_temp/laso.html"
"""

from __future__ import annotations
import argparse
import json
import os
import sys
from datetime import datetime
from typing import Dict, Optional

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

from core_calendar import lunar_to_solar, compute_true_solar_time, build_time_sync_report
from engine_tuvi import compute_tuvi_chart
from engine_bazi import compute_bazi_chart
from engine_iching import cast_iching_full, compute_qimen_hourly
from render_chart_html import render_full_html_report


def build_cross_validation(tuvi_data: Dict[str, object], bazi_data: Dict[str, object]) -> Dict[str, object]:
    """Tạo bảng tổng hợp Kiểm Chứng Chéo (Cross-Validation) giữa Tử Vi & Bát Tự."""
    dm = bazi_data["day_master"]  # type: ignore
    ys = bazi_data["yongshen_guidance"]  # type: ignore
    prof = tuvi_data["profile"]  # type: ignore
    tf = tuvi_data["target_year_fortune"]  # type: ignore

    active_dayun = next((d for d in bazi_data.get("dayun", []) if d.get("is_current")), None)  # type: ignore
    active_daihan = tf.get("active_dai_han")  # type: ignore

    return {
        "bazi_anchor": f"Nhật Chủ {dm['stem']} ({dm['element']}) — {dm['strength_assessment']}; Hỷ/Dụng Phù Ức: {', '.join(ys['fuyi_favorable_elements'])}; Điều hầu: {ys['qiong_tong_tiaohou']}",
        "tuvi_anchor": f"Bản mệnh {prof['ban_menh_nayin']}, {prof['cuc']}, Mệnh tại {prof['menh_palace']}, {prof['than_cu']}",
        "current_decade_sync": {
            "bazi_dayun": f"{active_dayun['can_chi']} ({active_dayun['solar_years']} — {active_dayun['stem_ten_god']}/{active_dayun['branch_main_ten_god']})" if active_dayun else "Chưa khởi Đại vận",
            "tuvi_daihan": f"{active_daihan['can_chi']} cung {active_daihan['palace_origin']} ({active_daihan['age_range']})" if active_daihan else "Chưa vào Đại hạn",
        },
        "cross_check_protocol": [
            "1. So khớp Khí chất & Nghề nghiệp: Đối chiếu Cách cục Tam Phương Tứ Chính Tử Vi với Thập Thần Đề Cương & Dụng Thần Bát Tự.",
            "2. So khớp Chu kỳ Tài - Quan: Nếu cả Đại Vận Bát Tự đắc Hỷ/Dụng VÀ Đại Hạn Tử Vi đắc Lộc/Quyền/Khoa -> Gắn nhãn [🟢 ĐỒNG THUẬN CAO].",
            "3. Nếu một hệ báo Cát, một hệ báo Kỵ/Xung -> Gắn nhãn [🟡 BÁN ĐỒNG THUẬN: Có thành tựu kèm áp lực/điều kiện].",
            "4. Nếu đương số sinh sát mốc giao canh giờ mà biến cố quá khứ lệch -> Gắn nhãn [🔴 CẦN NGHIỆM LÝ ĐỊNH GIỜ SINH].",
        ],
    }


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="kb-tuvi — Engine Huyền Học Định Danh Zero-Hallucination")
    p.add_argument("--mode", choices=["full", "tuvi", "bazi", "iching", "qimen", "all"], default="full")
    p.add_argument("--name", default="", help="Họ tên hoặc biệt danh đương số")
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
    p.add_argument("--zi-sect", type=int, choices=[1, 2], default=2, help="Chế độ Dạ Tý 23:00-23:59 cho Bát Tự: 2=Giữ Can Ngày (Tử Bình truyền thống), 1=Sang ngày mới (lunar-python default)")
    p.add_argument("--use-clock-time", action="store_true", help="Dùng thẳng giờ đồng hồ thay vì Giờ Chân Thái Dương")
    p.add_argument("--target-year", type=int, default=datetime.now().year, help="Năm Dương lịch cần xem Lưu niên / Vận hạn")
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

    dt_clock = datetime(sy, sm, sd, hh, mm_time)
    tst_info = compute_true_solar_time(dt_clock, place=args.place, longitude=args.longitude, tz_hours=args.tz)
    sync_report = build_time_sync_report(dt_clock, place=args.place, longitude=args.longitude, tz_hours=args.tz)
    dt_eff: datetime = dt_clock if args.use_clock_time else tst_info["true_datetime"]  # type: ignore

    payload: Dict[str, object] = {
        "meta": {
            "name": args.name,
            "mode": args.mode,
            "gender": args.gender,
            "place": tst_info["place"],
            "longitude": tst_info["longitude"],
            "timezone_utc": args.tz,
            "calendar_std": args.calendar_std,
            "tuvi_school": args.tuvi_school,
            "zi_sect": args.zi_sect,
            "clock_time": tst_info["clock_time"],
            "true_solar_time": tst_info["true_solar_time"],
            "time_mode_used": "Giờ Đồng Hồ" if args.use_clock_time else "Giờ Chân Thái Dương",
            "total_solar_offset_min": tst_info["total_offset_min"],
            "time_sync_verification": sync_report,
            "branch_boundary_warning": (
                f"CẢNH BÁO GIÁP RANH CANH GIỜ: Giờ đồng hồ là giờ {tst_info['clock_branch_name']}, nhưng Giờ Chân Thái Dương là giờ {tst_info['true_branch_name']}! Bắt buộc hỏi đương số 2-3 sự kiện quá khứ để nghiệm lý định giờ sinh!"
                if tst_info["branch_changed"] else None
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

    if "tuvi" in payload and "bazi" in payload:
        payload["cross_validation"] = build_cross_validation(payload["tuvi"], payload["bazi"])  # type: ignore

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
        payload["meta"]["html_report_saved"] = os.path.abspath(args.html_out)  # type: ignore

    sys.stdout.reconfigure(encoding="utf-8")  # type: ignore
    print(json.dumps(payload, ensure_ascii=False, indent=2, default=str))


if __name__ == "__main__":
    main()
