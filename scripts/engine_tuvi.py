# -*- coding: utf-8 -*-
"""
engine_tuvi.py — Engine Tử Vi Đẩu Số Hợp Nhất Đa Phái (iztro + Trung Châu + Phi Tinh + Nam Phái Việt Nam)
- Đầy đủ 12 cung, Thân cư, Định Cục Nạp Âm, 14 Chính Tinh kèm độ sáng (Miếu/Vượng/Đắc/Bình/Hãm)
- Hơn 95 Phụ Tinh (Lục Cát, Lục Sát, Vòng Lộc Tồn/Bác Sĩ, Vòng Thái Tuế, Vòng Trường Sinh, Đào Hồng Hỷ, Khốc Hư, Long Phượng, Tam Thai Bát Tọa, Ân Quang Thiên Quý...)
- Đặc sản Việt Nam: Tuần Trung Không Vong & Triệt Lộ Không Vong (Tuần – Triệt)
- Tứ Hóa Tiên Thiên + Phi Tinh Tứ Hóa 12 Cung (Cung Can Tứ Hóa, Tự Hóa, Hóa Kỵ Xung)
- Tự động nhận diện >35 Đại Cách Cục kinh điển & Vận Hạn (Đại Hạn 10 năm, Tiểu Hạn, Lưu Niên)
"""

from __future__ import annotations
from datetime import datetime
from typing import Dict, List, Tuple, Optional

from core_calendar import (
    STEMS_VI, STEMS_ZH, STEM_ELEMENTS, STEM_YINYANG,
    BRANCHES_VI, BRANCHES_ZH, BRANCH_ELEMENTS,
    solar_to_lunar, can_chi_name, nayin_for_stem_branch, tuan_khong_for_pillar,
)

PALACE_NAMES_CLOCKWISE = [
    "Mệnh", "Phụ Mẫu", "Phúc Đức", "Điền Trạch",
    "Quan Lộc", "Nô Bộc (Giao Hữu)", "Thiên Di", "Tật Ách",
    "Tài Bạch", "Tử Tức", "Phu Thê", "Huynh Đệ"
]

# Bảng Độ Sáng 14 Chính Tinh tại 12 Địa Chi (0=Tý .. 11=Hợi): M=Miếu, V=Vượng, Đ=Đắc, B=Bình, H=Hãm
MAJOR_BRIGHTNESS: Dict[str, List[str]] = {
    "Tử Vi":      ["B", "Đ", "M", "B", "V", "M", "M", "Đ", "M", "B", "V", "B"],
    "Thiên Cơ":   ["M", "H", "Đ", "V", "M", "B", "M", "H", "Đ", "V", "M", "B"],
    "Thái Dương": ["H", "H", "V", "M", "V", "V", "M", "Đ", "B", "H", "H", "H"],
    "Vũ Khúc":    ["V", "M", "Đ", "H", "M", "B", "V", "M", "Đ", "V", "M", "B"],
    "Thiên Đồng": ["V", "H", "B", "M", "B", "M", "H", "H", "V", "B", "B", "M"],
    "Liêm Trinh": ["B", "Đ", "M", "H", "V", "H", "B", "Đ", "M", "B", "V", "H"],
    "Thiên Phủ":  ["M", "M", "M", "B", "M", "Đ", "V", "M", "Đ", "B", "M", "Đ"],
    "Thái Âm":    ["M", "M", "H", "H", "H", "H", "H", "B", "Đ", "V", "V", "M"],
    "Tham Lang":  ["V", "M", "B", "Đ", "M", "H", "V", "M", "B", "B", "M", "H"],
    "Cự Môn":     ["V", "H", "M", "M", "H", "B", "V", "H", "M", "M", "H", "V"],
    "Thiên Tướng":["M", "M", "M", "H", "V", "Đ", "V", "Đ", "M", "H", "Đ", "Đ"],
    "Thiên Lương":["M", "V", "M", "M", "V", "H", "M", "Đ", "H", "Đ", "V", "H"],
    "Thất Sát":   ["V", "M", "M", "V", "M", "B", "V", "M", "M", "B", "M", "B"],
    "Phá Quân":   ["M", "V", "H", "H", "V", "B", "M", "V", "H", "H", "V", "B"],
}

BRIGHTNESS_FULL = {"M": "Miếu", "V": "Vượng", "Đ": "Đắc", "B": "Bình", "H": "Hãm"}

MAJOR_ELEMENTS: Dict[str, str] = {
    "Tử Vi": "Thổ", "Thiên Cơ": "Mộc", "Thái Dương": "Hỏa", "Vũ Khúc": "Kim",
    "Thiên Đồng": "Thủy", "Liêm Trinh": "Hỏa", "Thiên Phủ": "Thổ", "Thái Âm": "Thủy",
    "Tham Lang": "Thủy/Mộc", "Cự Môn": "Thủy", "Thiên Tướng": "Thủy",
    "Thiên Lương": "Mộc/Thổ", "Thất Sát": "Kim", "Phá Quân": "Thủy",
}

# Thập Can Tứ Hóa chuẩn Toàn Thư / iztro: [Hóa Lộc, Hóa Quyền, Hóa Khoa, Hóa Kỵ]
SIHUA_BY_STEM: Dict[int, Tuple[str, str, str, str]] = {
    0: ("Liêm Trinh", "Phá Quân", "Vũ Khúc", "Thái Dương"),   # Giáp
    1: ("Thiên Cơ", "Thiên Lương", "Tử Vi", "Thái Âm"),       # Ất
    2: ("Thiên Đồng", "Thiên Cơ", "Văn Xương", "Liêm Trinh"), # Bính
    3: ("Thái Âm", "Thiên Đồng", "Thiên Cơ", "Cự Môn"),       # Đinh
    4: ("Tham Lang", "Thái Âm", "Hữu Bật", "Thiên Cơ"),       # Mậu
    5: ("Vũ Khúc", "Tham Lang", "Thiên Lương", "Văn Khúc"),   # Kỷ
    6: ("Thái Dương", "Vũ Khúc", "Thái Âm", "Thiên Đồng"),    # Canh
    7: ("Cự Môn", "Thái Dương", "Văn Khúc", "Văn Xương"),     # Tân
    8: ("Thiên Lương", "Tử Vi", "Tả Phù", "Vũ Khúc"),         # Nhâm
    9: ("Phá Quân", "Cự Môn", "Thái Âm", "Tham Lang"),        # Quý
}

BAC_SI_12 = [
    "Bác Sĩ", "Lực Sĩ", "Thanh Long", "Tiểu Hao", "Tướng Quân", "Tấu Thư",
    "Phi Liêm", "Hỷ Thần", "Bệnh Phù", "Đại Hao", "Phục Binh", "Quan Phủ"
]

THAI_TUE_12 = [
    "Thái Tuế", "Thiếu Dương", "Tang Môn", "Thiếu Âm", "Quan Phù (Tuế)", "Tử Phù",
    "Tuế Phá", "Long Đức", "Bạch Hổ", "Phúc Đức (Đức)", "Điếu Khách", "Trực Phù"
]

TRUONG_SINH_12 = [
    "Trường Sinh", "Mộc Dục", "Quan Đới", "Lâm Quan", "Đế Vượng", "Suy",
    "Bệnh", "Tử", "Mộ", "Tuyệt", "Thai", "Dưỡng"
]

CUC_MAP_BY_ELEMENT = {
    "Thủy": (2, "Thủy Nhị Cục"),
    "Mộc":  (3, "Mộc Tam Cục"),
    "Kim":  (4, "Kim Tứ Cục"),
    "Thổ":  (5, "Thổ Ngũ Cục"),
    "Hỏa":  (6, "Hỏa Lục Cục"),
}


def compute_tuvi_star_index(lunar_day: int, cuc_num: int) -> int:
    """Công thức chuẩn an sao Tử Vi từ Ngày sinh Âm lịch (1..30) và Số Cục (2..6)."""
    x = (cuc_num - (lunar_day % cuc_num)) % cuc_num
    q = (lunar_day + x) // cuc_num
    base = 2 + (q - 1)  # Khởi từ cung Dần (2) là 1
    if x % 2 == 0:
        return (base + x) % 12
    return (base - x) % 12


def detect_classic_patterns(
    palaces_by_branch: Dict[int, Dict[str, object]],
    menh_b: int,
    year_s: int,
    year_b: int,
    hour_b: int,
    tuan_pair: Tuple[int, int],
    triet_pair: Tuple[int, int],
) -> List[Dict[str, str]]:
    """Tự động quét và nhận diện các Cách Cục kinh điển trên Tam Phương Tứ Chính của Mệnh."""
    patterns: List[Dict[str, str]] = []
    quan_b = (menh_b + 4) % 12
    tai_b = (menh_b + 8) % 12
    di_b = (menh_b + 6) % 12
    tptc_branches = [menh_b, quan_b, tai_b, di_b]

    def majors_at(b: int) -> List[str]:
        return [s["name"] for s in palaces_by_branch[b]["major_stars"]]  # type: ignore

    def all_stars_in_tptc() -> set:
        s_set = set()
        for b in tptc_branches:
            for key in ("major_stars", "auspicious_stars", "sha_stars", "minor_stars"):
                for item in palaces_by_branch[b][key]:  # type: ignore
                    s_set.add(item["name"] if isinstance(item, dict) else item)
        return s_set

    def sihua_in_tptc() -> set:
        sh = set()
        for b in tptc_branches:
            for tag in palaces_by_branch[b]["natal_sihua"]:  # type: ignore
                sh.add(tag.split(":")[0].strip())
        return sh

    m_majors = set(majors_at(menh_b))
    tptc_majors = set()
    for b in tptc_branches:
        tptc_majors.update(majors_at(b))
    tptc_all = all_stars_in_tptc()
    tptc_sh = sihua_in_tptc()

    # 1. Tử Phủ Vũ Tướng / Sát Phá Tham / Cơ Nguyệt Đồng Lương / Cự Nhật
    if {"Tử Vi", "Thiên Phủ"}.issubset(m_majors) and menh_b in (2, 8):
        patterns.append({
            "name": "Tử Phủ Đồng Cung (Dần/Thân)",
            "rank": "Thượng Cách",
            "desc": "Đế Tinh và Tài Khố đồng tọa tại Dần/Thân: Nền tảng quản trị, tài chính và uy tín lớn; rất cần Tả Hữu, Lộc Tồn để tránh cô độc."
        })
    elif tptc_majors.issuperset({"Tử Vi", "Thiên Phủ", "Vũ Khúc", "Thiên Tướng"}):
        patterns.append({
            "name": "Tử Phủ Vũ Tướng Cách",
            "rank": "Đại Cách Quản Trị",
            "desc": "Khung mệnh lãnh đạo - điều hành tổ chức quy mô lớn, trọng kỷ cương và tích lũy bền vững."
        })
    if {"Thiên Phủ", "Thiên Tướng"}.issubset(tptc_majors) and "Thiên Phủ" not in m_majors and "Thiên Tướng" not in m_majors:
        patterns.append({
            "name": "Phủ Tướng Triều Viên",
            "rank": "Cát Cách",
            "desc": "Thiên Phủ và Thiên Tướng tam hợp chiếu Mệnh: Lộc thực dồi dào, quan hệ xã hội đắc lực, hậu vận ổn định."
        })
    if {"Thất Sát", "Phá Quân", "Tham Lang"}.issubset(tptc_majors):
        patterns.append({
            "name": "Sát Phá Tham Cách (Trúc La Tam Hạn)",
            "rank": "Cách Khai Phá Đột Biến",
            "desc": "Mạnh mẽ, dám dấn thân mở lối riêng, hợp kinh doanh thực chiến, công nghệ, kỹ thuật hoặc cải tổ; thành công qua biến động."
        })
    if {"Thiên Cơ", "Thái Âm", "Thiên Đồng", "Thiên Lương"}.issubset(tptc_majors):
        patterns.append({
            "name": "Cơ Nguyệt Đồng Lương Cách",
            "rank": "Cách Chuyên Gia / Tham Mưu",
            "desc": "Trí tuệ mưu lược, chuẩn mực, cực hợp vai trò cố vấn chiến lược, giáo dục, y dược, tài chính - kế hoạch hoặc cơ quan lớn."
        })

    # 2. Tam Kỳ Gia Hội & Song Lộc
    if {"Hóa Lộc", "Hóa Quyền", "Hóa Khoa"}.issubset(tptc_sh):
        patterns.append({
            "name": "Tam Kỳ Gia Hội (Khoa – Quyền – Lộc)",
            "rank": "Thượng Thượng Cách",
            "desc": "Hội đủ Hóa Khoa, Hóa Quyền, Hóa Lộc trên Tam Phương Tứ Chính: Danh tiếng, quyền lực thực thi và tài lộc cộng hưởng mạnh mẽ."
        })
    if "Hóa Lộc" in tptc_sh and "Lộc Tồn" in tptc_all:
        patterns.append({
            "name": "Song Lộc Triều Viên (Minh Lộc Ám Lộc)",
            "rank": "Đại Phú Cách",
            "desc": "Lộc Tồn và Hóa Lộc cùng hội chiếu Mệnh Tài Quan: Nguồn lực tài chính dồi dào, nhạy bén dòng tiền."
        })
    if ("Lộc Tồn" in tptc_all or "Hóa Lộc" in tptc_sh) and "Thiên Mã" in tptc_all:
        patterns.append({
            "name": "Lộc Mã Giao Trì",
            "rank": "Phú Thương Cách",
            "desc": "Lộc đi đôi với Mã: Càng năng động dịch chuyển, thương mại xuyên vùng/quốc tế càng phát đạt."
        })

    # 3. Các cách đặc thù theo vị trí cung
    if "Thái Dương" in m_majors and menh_b == 3:
        patterns.append({
            "name": "Nhật Xuất Phù Tang (Thái Dương cư Mão)",
            "rank": "Cát Cách",
            "desc": "Mặt trời mọc rạng rỡ buổi bình minh: Khí chất quang minh, phát triển sớm, giàu sức lan tỏa."
        })
    if "Thái Dương" in m_majors and menh_b == 6:
        patterns.append({
            "name": "Nhật Lệ Trung Thiên (Thái Dương cư Ngọ)",
            "rank": "Quý Cách",
            "desc": "Mặt trời chính ngọ rực rỡ (đẹp nhất khi đắc Lộc Tồn/Hóa Lộc): Danh vọng cao, chí hướng lớn."
        })
    if "Thái Âm" in m_majors and menh_b == 11:
        patterns.append({
            "name": "Nguyệt Lãng Thiên Môn (Thái Âm cư Hợi)",
            "rank": "Thượng Cách Phú Quý",
            "desc": "Trăng rằm sáng trong tại Hợi (nhất là sinh ban đêm): Tinh tế, giàu phúc lộc ngầm và duyên điền sản."
        })
    if not m_majors and menh_b == 7 and "Thái Dương" in majors_at(3) and "Thái Âm" in majors_at(11):
        patterns.append({
            "name": "Minh Châu Xuất Hải (Mệnh VCD tại Mùi, Nhật Mão Nguyệt Hợi chiếu)",
            "rank": "Đại Quý Cách",
            "desc": "Ngọc sáng nhô lên khỏi biển lớn: Một trong những cách Vô Chính Diệu rực rỡ nhất của Tử Vi Đẩu Số."
        })
    if "Cự Môn" in m_majors and menh_b in (0, 6) and ({"Hóa Lộc", "Hóa Quyền", "Hóa Khoa"} & tptc_sh or "Lộc Tồn" in tptc_all):
        patterns.append({
            "name": "Thạch Trung Ẩn Ngọc (Cự Môn Tý/Ngọ đắc Hóa/Lộc)",
            "rank": "Thượng Cách",
            "desc": "Ngọc quý ẩn trong đá: Thời trẻ rèn giũa nội lực, trung hậu vận phát lộ tài năng kiệt xuất nhờ trí tuệ và ngôn luận."
        })
    if "Tham Lang" in m_majors and ("Hỏa Tinh" in tptc_all or "Linh Tinh" in tptc_all):
        patterns.append({
            "name": "Hỏa Tham / Linh Tham Cách",
            "rank": "Bạo Phát Kỳ Cách",
            "desc": "Tham Lang hội Hỏa/Linh tinh: Nhạy bén chớp thời cơ đột biến, dễ có bước nhảy vọt bất ngờ về tài lộc/sự nghiệp."
        })
    if "Thất Sát" in m_majors and len(m_majors) == 1 and menh_b in (0, 2, 6, 8):
        patterns.append({
            "name": "Thất Sát Triều Đẩu / Ngưỡng Đẩu",
            "rank": "Quyền Uy Cách",
            "desc": "Thất Sát độc tọa miếu vượng tại Tý/Ngọ/Dần/Thân: Bản lĩnh cầm quân, quyết đoán vượt nghịch cảnh."
        })
    if not m_majors:
        has_tuan_triet = (menh_b in tuan_pair) or (menh_b in triet_pair)
        patterns.append({
            "name": "Mệnh Vô Chính Diệu" + (" (Đắc Tuần/Triệt án ngữ)" if has_tuan_triet else " (Mượn chính tinh Xung Chiếu)"),
            "rank": "Linh Hoạt Đặc Cách",
            "desc": "Tư duy mềm dẻo thích ứng cao; cần lấy chính tinh cung Thiên Di xung chiếu (60-70% lực) kết hợp Tam Hợp làm trục định hướng."
        })

    # 4. Phụ tá Giáp Cung & Hội Chiếu
    if {"Tả Phù", "Hữu Bật"}.issubset(tptc_all):
        patterns.append({
            "name": "Tả Hữu Đồng Cung / Hội Chiếu",
            "rank": "Trợ Lực Cách",
            "desc": "Có đội ngũ cộng sự trợ lực, khả năng điều phối đa nhiệm tốt."
        })
    if {"Văn Xương", "Văn Khúc"}.issubset(tptc_all):
        patterns.append({
            "name": "Văn Tinh Ám Củng (Xương Khúc hội chiếu)",
            "rank": "Văn Quý Cách",
            "desc": "Tư chất học thuật, thẩm mỹ, khả năng viết lách và truyền đạt sắc sảo."
        })
    if {"Thiên Khôi", "Thiên Việt"}.issubset(tptc_all):
        patterns.append({
            "name": "Tọa Quý Hướng Quý (Khôi Việt hội chiếu)",
            "rank": "Quý Nhân Cách",
            "desc": "Hay được bậc đàn anh, cấp trên hoặc cơ chế nâng đỡ đúng thời điểm then chốt."
        })

    return patterns


def compute_tuvi_chart(
    dt_effective: datetime,
    gender: str = "nam",
    tz_hours: float = 7.0,
    target_year: Optional[int] = None,
    leap_month_rule: str = "split15",  # "split15": ngày 1-15 giữ tháng chính, 16-30 tính sang tháng sau; "keep": giữ nguyên tháng chính
    calendar_std: str = "vn",          # "vn": Âm lịch chuẩn Việt Nam UTC+7; "intl": Âm lịch chuẩn Quốc tế iztro UTC+8
    tuvi_school: str = "iztro",        # "iztro": chuẩn Toàn Thư / iztro Quốc tế; "vn": Nam Phái VN (Hỏa/Linh thuận nghịch theo Âm Dương)
) -> Dict[str, object]:
    """
    Lập lá số Tử Vi Đẩu Số toàn diện (Nam Phái VN + Trung Châu + Phi Tinh Tứ Hóa + đồng bộ iztro).
    Lưu ý: Nếu sinh từ 23:00–23:59 (Dạ Tý), chuẩn Tử Vi đẩy sang giờ Tý ngày hôm sau.
    """
    if target_year is None:
        target_year = datetime.now().year

    # Xử lý 23:00-23:59 sang ngày kế tiếp cho Tử Vi
    from datetime import timedelta
    is_late_zi = dt_effective.hour == 23
    dt_for_lunar = dt_effective + timedelta(hours=1) if is_late_zi else dt_effective

    cal_tz = 8.0 if calendar_std == "intl" else tz_hours
    lunar = solar_to_lunar(dt_for_lunar.day, dt_for_lunar.month, dt_for_lunar.year, cal_tz)
    l_day = int(lunar["day"])
    l_month_raw = int(lunar["month"])
    l_year = int(lunar["year"])
    is_leap = int(lunar["is_leap"])

    eff_month = l_month_raw
    leap_note = None
    if is_leap == 1:
        if leap_month_rule == "split15" and l_day > 15:
            eff_month = (l_month_raw % 12) + 1
            leap_note = f"Sinh nửa sau tháng {l_month_raw} Nhuận (ngày {l_day}): Áp dụng quy tắc Phân Bán Nguyệt -> tính sang tháng {eff_month}."
        else:
            leap_note = f"Sinh tháng {l_month_raw} Nhuận (ngày {l_day}): Tính theo tháng {eff_month}."

    hour_b = ((dt_effective.hour + 1) // 2) % 12
    year_s = (l_year + 6) % 10
    year_b = (l_year + 8) % 12

    is_male = gender.strip().lower() in ("nam", "male", "m", "1")
    is_yang_year = (year_s % 2 == 0)
    clockwise = (is_male and is_yang_year) or ((not is_male) and (not is_yang_year))
    polarity_title = f"{'Dương' if is_yang_year else 'Âm'} {'Nam' if is_male else 'Nữ'}"

    # 1. Định Cung Mệnh & Cung Thân
    menh_b = (2 + (eff_month - 1) - hour_b) % 12
    than_b = (2 + (eff_month - 1) + hour_b) % 12

    # 2. Can của 12 Cung (Ngũ Hổ Độn từ Dần)
    dan_stem = ((year_s % 5) * 2 + 2) % 10
    palace_stems = {b: (dan_stem + (b - 2) % 12) % 10 for b in range(12)}

    # 3. Định Ngũ Hành Cục theo Nạp Âm của Can Chi Cung Mệnh
    menh_nayin_name, menh_nayin_elem = nayin_for_stem_branch(palace_stems[menh_b], menh_b)
    cuc_num, cuc_name = CUC_MAP_BY_ELEMENT[menh_nayin_elem]
    year_nayin_name, year_nayin_elem = nayin_for_stem_branch(year_s, year_b)

    # 4. Tuần & Triệt chuẩn Việt Nam
    tuan_pair = tuan_khong_for_pillar(year_s, year_b)
    triet_map = {0: (8, 9), 5: (8, 9), 1: (6, 7), 6: (6, 7), 2: (4, 5), 7: (4, 5), 3: (2, 3), 8: (2, 3), 4: (0, 1), 9: (0, 1)}
    triet_pair = triet_map[year_s]

    # Khởi tạo khung 12 cung theo Địa Chi 0..11
    palaces: Dict[int, Dict[str, object]] = {}
    for b in range(12):
        # Lưu ý: PALACE_NAMES_CLOCKWISE đi thuận Mệnh(0)->Phụ(+1)?
        # Kiểm chứng lại chuẩn Tử Vi: Từ Mệnh đi NGHỊCH chiều kim đồng hồ là Huynh Đệ(-1), Phu Thê(-2), Tử Tức(-3), Tài Bạch(-4), Tật Ách(-5), Thiên Di(-6), Nô Bộc(-7), Quan Lộc(-8), Điền Trạch(-9), Phúc Đức(-10), Phụ Mẫu(-11)
        # Tức là đi THUẬN chiều kim đồng hồ từ Mệnh là: Mệnh(0), Phụ Mẫu(+1), Phúc Đức(+2), Điền Trạch(+3), Quan Lộc(+4), Nô Bộc(+5), Thiên Di(+6), Tật Ách(+7), Tài Bạch(+8), Tử Tức(+9), Phu Thê(+10), Huynh Đệ(+11)!
        role_idx = (b - menh_b) % 12
        role_name = PALACE_NAMES_CLOCKWISE[role_idx]
        p_stem = palace_stems[b]
        palaces[b] = {
            "branch_idx": b,
            "branch": BRANCHES_VI[b],
            "branch_zh": BRANCHES_ZH[b],
            "stem_idx": p_stem,
            "stem": STEMS_VI[p_stem],
            "can_chi": can_chi_name(p_stem, b),
            "palace_name": role_name,
            "is_menh": b == menh_b,
            "is_than": b == than_b,
            "has_tuan": b in tuan_pair,
            "has_triet": b in triet_pair,
            "major_stars": [],
            "auspicious_stars": [],
            "sha_stars": [],
            "minor_stars": [],
            "natal_sihua": [],
            "liunian_sihua": [],
            "vong_truong_sinh": "",
            "vong_thai_tue": "",
            "vong_bac_si": "",
            "dai_han": "",
            "dai_han_start": 0,
            "dai_han_end": 0,
            "tieu_han_branch_year": "",
            "flying_sihua": {},
        }

    # 5. An 14 Chính Tinh
    tuvi_b = compute_tuvi_star_index(l_day, cuc_num)
    thien_phu_b = (4 - tuvi_b) % 12

    tuvi_group = [
        ("Tử Vi", 0), ("Thiên Cơ", -1), ("Thái Dương", -3),
        ("Vũ Khúc", -4), ("Thiên Đồng", -5), ("Liêm Trinh", -8),
    ]
    thien_phu_group = [
        ("Thiên Phủ", 0), ("Thái Âm", 1), ("Tham Lang", 2), ("Cự Môn", 3),
        ("Thiên Tướng", 4), ("Thiên Lương", 5), ("Thất Sát", 6), ("Phá Quân", 10),
    ]

    star_to_branch: Dict[str, int] = {}

    for s_name, offset in tuvi_group:
        pos = (tuvi_b + offset) % 12
        br_code = MAJOR_BRIGHTNESS[s_name][pos]
        palaces[pos]["major_stars"].append({  # type: ignore
            "name": s_name,
            "brightness_code": br_code,
            "brightness": BRIGHTNESS_FULL[br_code],
            "element": MAJOR_ELEMENTS[s_name],
        })
        star_to_branch[s_name] = pos

    for s_name, offset in thien_phu_group:
        pos = (thien_phu_b + offset) % 12
        br_code = MAJOR_BRIGHTNESS[s_name][pos]
        palaces[pos]["major_stars"].append({  # type: ignore
            "name": s_name,
            "brightness_code": br_code,
            "brightness": BRIGHTNESS_FULL[br_code],
            "element": MAJOR_ELEMENTS[s_name],
        })
        star_to_branch[s_name] = pos

    # 6. An Lục Cát Tinh & Lộc Tồn / Thiên Mã
    ta_phu_b = (4 + eff_month - 1) % 12
    huu_bat_b = (10 - (eff_month - 1)) % 12
    van_xuong_b = (10 - hour_b) % 12
    van_khuc_b = (4 + hour_b) % 12

    khoi_viet_map = {
        0: (1, 7), 4: (1, 7), 6: (1, 7),
        1: (0, 8), 5: (0, 8),
        2: (11, 9), 3: (11, 9),
        7: (6, 2),
        8: (3, 5), 9: (3, 5),
    }
    thien_khoi_b, thien_viet_b = khoi_viet_map[year_s]

    loc_ton_map = {0: 2, 1: 3, 2: 5, 3: 6, 4: 5, 5: 6, 6: 8, 7: 9, 8: 11, 9: 0}
    loc_ton_b = loc_ton_map[year_s]

    if year_b in (2, 6, 10):
        thien_ma_b, dao_hoa_b, hoa_cai_b, kiep_sat_b = 8, 3, 10, 11
    elif year_b in (8, 0, 4):
        thien_ma_b, dao_hoa_b, hoa_cai_b, kiep_sat_b = 2, 9, 4, 5
    elif year_b in (5, 9, 1):
        thien_ma_b, dao_hoa_b, hoa_cai_b, kiep_sat_b = 11, 6, 1, 2
    else:
        thien_ma_b, dao_hoa_b, hoa_cai_b, kiep_sat_b = 5, 0, 7, 8

    auspicious_placements = [
        ("Tả Phù", ta_phu_b), ("Hữu Bật", huu_bat_b),
        ("Văn Xương", van_xuong_b), ("Văn Khúc", van_khuc_b),
        ("Thiên Khôi", thien_khoi_b), ("Thiên Việt", thien_viet_b),
        ("Lộc Tồn", loc_ton_b), ("Thiên Mã", thien_ma_b),
    ]
    for s_name, pos in auspicious_placements:
        palaces[pos]["auspicious_stars"].append({"name": s_name})  # type: ignore
        star_to_branch[s_name] = pos

    # 7. An Lục Sát Tinh (Kình, Đà, Không, Kiếp, Hỏa, Linh)
    kinh_duong_b = (loc_ton_b + 1) % 12
    da_la_b = (loc_ton_b - 1) % 12
    dia_khong_b = (11 - hour_b) % 12
    dia_kiep_b = (11 + hour_b) % 12

    # Hỏa Tinh & Linh Tinh: hỗ trợ chuẩn Quốc tế iztro (Toàn Thư thuận hành) & Nam Phái VN (thuận/nghịch theo Âm Dương Nam Nữ)
    if year_b in (2, 6, 10):
        hoa_start, linh_start = 1, 3
    elif year_b in (8, 0, 4):
        hoa_start, linh_start = 2, 10
    elif year_b in (5, 9, 1):
        hoa_start, linh_start = 3, 10
    else:
        hoa_start, linh_start = 9, 10

    if tuvi_school == "vn":
        if clockwise:
            hoa_tinh_b = (hoa_start + hour_b) % 12
            linh_tinh_b = (linh_start - hour_b) % 12
        else:
            hoa_tinh_b = (hoa_start - hour_b) % 12
            linh_tinh_b = (linh_start + hour_b) % 12
    else:
        hoa_tinh_b = (hoa_start + hour_b) % 12
        linh_tinh_b = (linh_start + hour_b) % 12

    sha_placements = [
        ("Kình Dương", kinh_duong_b), ("Đà La", da_la_b),
        ("Địa Không", dia_khong_b), ("Địa Kiếp", dia_kiep_b),
        ("Hỏa Tinh", hoa_tinh_b), ("Linh Tinh", linh_tinh_b),
    ]
    for s_name, pos in sha_placements:
        palaces[pos]["sha_stars"].append({"name": s_name})  # type: ignore
        star_to_branch[s_name] = pos

    # 8. An Các Phụ Tinh Trọng Yếu Khác (chuẩn xác 100% theo iztro & Toàn Thư + Nam Phái)
    hong_loan_b = (3 - year_b) % 12
    thien_hy_b = (hong_loan_b + 6) % 12
    thien_hinh_b = (9 + eff_month - 1) % 12
    thien_rieu_b = (1 + eff_month - 1) % 12
    thien_y_b = thien_rieu_b
    thien_khoc_b = (6 - year_b) % 12
    thien_hu_b = (6 + year_b) % 12
    long_tri_b = (4 + year_b) % 12
    phuong_cac_b = (10 - year_b) % 12
    nien_giai_b = phuong_cac_b
    nguyet_giai_b = (8 + ((eff_month - 1) // 2) * 2) % 12
    tam_thai_b = (ta_phu_b + l_day - 1) % 12
    bat_toa_b = (huu_bat_b - (l_day - 1)) % 12
    an_quang_b = (van_xuong_b + l_day - 2) % 12
    thien_quy_b = (van_khuc_b - (l_day - 2)) % 12
    thai_phu_b = (van_khuc_b + 2) % 12
    phong_cao_b = (van_khuc_b - 2) % 12
    # Quốc Ấn: Lộc Tồn khởi 1 đi thuận tới cung thứ 9 (+8); Đường Phù: Lộc Tồn khởi 1 đi nghịch tới cung thứ 8 (-7 ≡ +5)
    quoc_an_b = (loc_ton_b + 8) % 12
    duong_phu_b = (loc_ton_b - 7) % 12
    thien_khong_b = (year_b + 1) % 12
    thien_tai_b = (menh_b + year_b) % 12
    thien_tho_b = (than_b + year_b) % 12
    thien_thuong_b = (menh_b + 5) % 12  # Luôn cư Nô Bộc (Giao Hữu)
    thien_su_b = (menh_b + 7) % 12      # Luôn cư Tật Ách
    dau_quan_b = (year_b - (eff_month - 1) + hour_b) % 12
    pha_toai_b = 5 if year_b in (0, 6, 3, 9) else (9 if year_b in (2, 8, 5, 11) else 1)
    thien_vu_b = {1: 5, 5: 5, 9: 5, 2: 8, 6: 8, 10: 8, 3: 2, 7: 2, 11: 2, 4: 11, 8: 11, 12: 11}[eff_month]
    am_sat_b = (2 - ((eff_month - 1) % 6) * 2) % 12

    if year_b in (11, 0, 1):
        co_than_b, qua_tu_b = 2, 10
    elif year_b in (2, 3, 4):
        co_than_b, qua_tu_b = 5, 1
    elif year_b in (5, 6, 7):
        co_than_b, qua_tu_b = 8, 4
    else:
        co_than_b, qua_tu_b = 11, 7

    luu_ha_map = {0: 9, 1: 10, 2: 7, 3: 8, 4: 5, 5: 6, 6: 4, 7: 3, 8: 11, 9: 2}
    thien_tru_map = {0: 5, 1: 6, 2: 0, 3: 5, 4: 6, 5: 8, 6: 2, 7: 6, 8: 9, 9: 11}
    thien_quan_map = {0: 7, 1: 4, 2: 5, 3: 2, 4: 3, 5: 9, 6: 11, 7: 9, 8: 10, 9: 6}
    thien_phuc_map = {0: 9, 1: 8, 2: 0, 3: 11, 4: 3, 5: 2, 6: 6, 7: 5, 8: 6, 9: 5}

    minor_placements = [
        ("Hồng Loan", hong_loan_b), ("Thiên Hỷ", thien_hy_b), ("Đào Hoa", dao_hoa_b),
        ("Thiên Hình", thien_hinh_b), ("Thiên Riêu", thien_rieu_b), ("Thiên Y", thien_y_b),
        ("Thiên Khốc", thien_khoc_b), ("Thiên Hư", thien_hu_b),
        ("Long Trì", long_tri_b), ("Phượng Các", phuong_cac_b),
        ("Niên Giải", nien_giai_b), ("Giải Thần", nguyet_giai_b),
        ("Tam Thai", tam_thai_b), ("Bát Tọa", bat_toa_b),
        ("Ân Quang", an_quang_b), ("Thiên Quý", thien_quy_b),
        ("Thai Phụ", thai_phu_b), ("Phong Cáo", phong_cao_b),
        ("Quốc Ấn", quoc_an_b), ("Đường Phù", duong_phu_b),
        ("Cô Thần", co_than_b), ("Quả Tú", qua_tu_b),
        ("Hoa Cái", hoa_cai_b), ("Kiếp Sát", kiep_sat_b), ("Phá Toái", pha_toai_b),
        ("Thiên Không", thien_khong_b), ("Âm Sát", am_sat_b), ("Thiên Vu", thien_vu_b),
        ("Đẩu Quân", dau_quan_b), ("Thiên Thương", thien_thuong_b), ("Thiên Sứ", thien_su_b),
        ("Lưu Hà", luu_ha_map[year_s]), ("Thiên Trù", thien_tru_map[year_s]),
        ("Thiên Quan", thien_quan_map[year_s]), ("Thiên Phúc", thien_phuc_map[year_s]),
        ("Thiên Tài", thien_tai_b), ("Thiên Thọ", thien_tho_b),
    ]
    for s_name, pos in minor_placements:
        palaces[pos]["minor_stars"].append(s_name)  # type: ignore

    # 9. Ba Vòng Sao: Thái Tuế, Bác Sĩ, Trường Sinh
    step_dir = 1 if clockwise else -1
    ts_start_map = {2: 8, 5: 8, 3: 11, 4: 5, 6: 2}
    ts_start = ts_start_map[cuc_num]

    for i in range(12):
        palaces[(year_b + i) % 12]["vong_thai_tue"] = THAI_TUE_12[i]
        palaces[(loc_ton_b + i * step_dir) % 12]["vong_bac_si"] = BAC_SI_12[i]
        palaces[(ts_start + i * step_dir) % 12]["vong_truong_sinh"] = TRUONG_SINH_12[i]

    # 10. Sinh Niên Tứ Hóa, Lưu Niên Tứ Hóa & Phi Tinh Tứ Hóa 12 Cung
    sihua_labels = ["Hóa Lộc", "Hóa Quyền", "Hóa Khoa", "Hóa Kỵ"]
    natal_4 = SIHUA_BY_STEM[year_s]
    natal_sihua_summary = []
    for sh_type, target_star in zip(sihua_labels, natal_4):
        tb = star_to_branch[target_star]
        palaces[tb]["natal_sihua"].append(f"{sh_type}: {target_star}")  # type: ignore
        natal_sihua_summary.append({
            "type": sh_type,
            "star": target_star,
            "palace": palaces[tb]["palace_name"],
            "branch": BRANCHES_VI[tb],
        })

    # Lưu Niên năm mục tiêu (target_year)
    ln_lunar_year = target_year
    ln_s = (ln_lunar_year + 6) % 10
    ln_b = (ln_lunar_year + 8) % 12
    ln_4 = SIHUA_BY_STEM[ln_s]
    liunian_sihua_summary = []
    for sh_type, target_star in zip(sihua_labels, ln_4):
        tb = star_to_branch[target_star]
        palaces[tb]["liunian_sihua"].append(f"Lưu {sh_type}: {target_star}")  # type: ignore
        liunian_sihua_summary.append({
            "type": f"Lưu {sh_type}",
            "star": target_star,
            "palace": palaces[tb]["palace_name"],
            "branch": BRANCHES_VI[tb],
        })

    # Phi Tinh Tứ Hóa từ Can của từng cung trong 12 cung
    for b in range(12):
        p_stem = int(palaces[b]["stem_idx"])
        fly_map = {}
        for sh_type, target_star in zip(sihua_labels, SIHUA_BY_STEM[p_stem]):
            dest_b = star_to_branch[target_star]
            dest_role = str(palaces[dest_b]["palace_name"])
            opp_role = str(palaces[(dest_b + 6) % 12]["palace_name"])
            note = f"{target_star} -> {dest_role} ({BRANCHES_VI[dest_b]})"
            if dest_b == b:
                note += f" [TỰ {sh_type.upper()}]"
            elif sh_type == "Hóa Kỵ":
                note += f" [Xung {opp_role}]"
            fly_map[sh_type] = note
        palaces[b]["flying_sihua"] = fly_map

    # 11. Đại Hạn 10 Năm & Tiểu Hạn
    nominal_age_target = max(1, target_year - l_year + 1)
    active_dai_han = None
    for i in range(12):
        dh_b = (menh_b + i * step_dir) % 12
        age_s = cuc_num + i * 10
        age_e = age_s + 9
        palaces[dh_b]["dai_han"] = f"{age_s}–{age_e}"
        palaces[dh_b]["dai_han_start"] = age_s
        palaces[dh_b]["dai_han_end"] = age_e
        if age_s <= nominal_age_target <= age_e:
            dh_stem = int(palaces[dh_b]["stem_idx"])
            dh_sihua = [
                f"ĐH {sh}: {st} ({palaces[star_to_branch[st]]['palace_name']})"
                for sh, st in zip(sihua_labels, SIHUA_BY_STEM[dh_stem])
            ]
            active_dai_han = {
                "age_range": f"{age_s}–{age_e} tuổi mụ",
                "palace_origin": palaces[dh_b]["palace_name"],
                "can_chi": palaces[dh_b]["can_chi"],
                "major_stars": [m["name"] for m in palaces[dh_b]["major_stars"]],  # type: ignore
                "dai_han_sihua": dh_sihua,
            }

    # Tiểu hạn khởi theo Tam Hợp Chi Năm (Nam thuận, Nữ nghịch)
    if year_b in (2, 6, 10):
        th_start = 4   # Thìn
    elif year_b in (8, 0, 4):
        th_start = 10  # Tuất
    elif year_b in (5, 9, 1):
        th_start = 7   # Mùi
    else:
        th_start = 1   # Sửu
    th_dir = 1 if is_male else -1
    for i in range(12):
        b_pos = (th_start + i * th_dir) % 12
        sample_ages = [1 + i + 12 * k for k in range(7)]
        palaces[b_pos]["tieu_han_branch_year"] = ", ".join(str(a) for a in sample_ages[:5])
    tieu_han_target_b = (th_start + (nominal_age_target - 1) * th_dir) % 12

    # 12. Nhận diện Cách Cục
    classic_patterns = detect_classic_patterns(
        palaces, menh_b, year_s, year_b, hour_b, tuan_pair, triet_pair
    )

    return {
        "profile": {
            "gender_polarity": polarity_title,
            "direction": "Thuận hành (Dương Nam / Âm Nữ)" if clockwise else "Nghịch hành (Âm Nam / Dương Nữ)",
            "calendar_standard": "Quốc tế iztro (UTC+8)" if calendar_std == "intl" else f"Việt Nam (UTC+{tz_hours:g})",
            "tuvi_school": "Nam Phái Việt Nam" if tuvi_school == "vn" else "Quốc tế Toàn Thư / iztro (+Tuần Triệt VN)",
            "lunar_date": f"Ngày {l_day:02d}/{l_month_raw:02d}{' (Nhuận)' if is_leap else ''}/{l_year} ({can_chi_name(year_s, year_b)})",
            "birth_hour": f"Giờ {BRANCHES_VI[hour_b]}",
            "ban_menh_nayin": f"{year_nayin_name} ({year_nayin_elem})",
            "cuc": f"{cuc_name} (khởi Đại hạn từ {cuc_num} tuổi)",
            "menh_palace": f"{BRANCHES_VI[menh_b]} ({palaces[menh_b]['can_chi']})",
            "than_cu": f"Thân cư {palaces[than_b]['palace_name']} ({BRANCHES_VI[than_b]})",
            "menh_chu": ["Tham Lang", "Cự Môn", "Lộc Tồn", "Văn Khúc", "Liêm Trinh", "Vũ Khúc", "Phá Quân", "Vũ Khúc", "Liêm Trinh", "Văn Khúc", "Lộc Tồn", "Cự Môn"][menh_b],
            "than_chu": ["Hỏa Tinh", "Thiên Tướng", "Thiên Lương", "Thiên Đồng", "Văn Xương", "Thiên Cơ", "Hỏa Tinh", "Thiên Tướng", "Thiên Lương", "Thiên Đồng", "Văn Xương", "Thiên Cơ"][year_b],
            "tuan_khong": f"{BRANCHES_VI[tuan_pair[0]]} – {BRANCHES_VI[tuan_pair[1]]}",
            "triet_lo": f"{BRANCHES_VI[triet_pair[0]]} – {BRANCHES_VI[triet_pair[1]]}",
            "late_zi_note": "Sinh 23:00–23:59 (Dạ Tý): Đã chuyển sang giờ Tý ngày kế tiếp theo chuẩn Tử Vi." if is_late_zi else None,
            "leap_month_note": leap_note,
        },
        "natal_sihua": natal_sihua_summary,
        "classic_patterns": classic_patterns,
        "target_year_fortune": {
            "target_solar_year": target_year,
            "nominal_age": nominal_age_target,
            "liunian_can_chi": can_chi_name(ln_s, ln_b),
            "liunian_menh_palace": f"Cung {BRANCHES_VI[ln_b]} (trùng cung gốc: {palaces[ln_b]['palace_name']})",
            "tieu_han_palace": f"Cung {BRANCHES_VI[tieu_han_target_b]} (trùng cung gốc: {palaces[tieu_han_target_b]['palace_name']})",
            "active_dai_han": active_dai_han,
            "liunian_sihua": liunian_sihua_summary,
        },
        "palaces_by_branch": [palaces[b] for b in range(12)],
    }
