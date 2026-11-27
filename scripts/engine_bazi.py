# -*- coding: utf-8 -*-
"""
engine_bazi.py — Engine Bát Tự Tứ Trụ Chuyên Sâu (chắt lọc từ jinchenma94/bazi-skill & 9 cổ thư)
- Lập Tứ Trụ chính xác đến từng phút Tiết Khí (Lập Xuân & 12 Tiết)
- Xử lý chuẩn Dạ Tý (23:00-23:59) & Tảo Tý (00:00-00:59)
- Thập Thần, Tàng Can (Bản/Trung/Dư khí), Nạp Âm, 12 Vòng Trường Sinh, Tuần Không, Thần Sát
- Tương tác Can Chi (Hợp, Xung, Hình, Hại, Phá, Tam Hợp, Tam Hội)
- Khởi Đại Vận chính xác Năm - Tháng giao vận & Lưu Niên
- Chấm điểm Cường Nhược Nhật Chủ & Gợi ý Dụng Thần (Điều Hầu Cùng Thông Bảo Giám + Phù Ức)
"""

from __future__ import annotations
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional

from core_calendar import (
    STEMS_VI, STEMS_ZH, STEM_ELEMENTS, STEM_YINYANG,
    BRANCHES_VI, BRANCHES_ZH, BRANCH_ELEMENTS,
    jd_from_date, get_solar_term_context, can_chi_name,
    nayin_for_stem_branch, tuan_khong_for_pillar,
)

# Tàng Can (Bản khí, Trung khí, Dư khí) kèm trọng số
HIDDEN_STEMS: Dict[int, List[Tuple[int, float]]] = {
    0:  [(9, 1.0)],                         # Tý: Quý
    1:  [(5, 0.6), (9, 0.25), (7, 0.15)],   # Sửu: Kỷ, Quý, Tân
    2:  [(0, 0.6), (2, 0.25), (4, 0.15)],   # Dần: Giáp, Bính, Mậu
    3:  [(1, 1.0)],                         # Mão: Ất
    4:  [(4, 0.6), (1, 0.25), (9, 0.15)],   # Thìn: Mậu, Ất, Quý
    5:  [(2, 0.6), (4, 0.25), (6, 0.15)],   # Tỵ: Bính, Mậu, Canh
    6:  [(3, 0.7), (5, 0.3)],               # Ngọ: Đinh, Kỷ
    7:  [(5, 0.6), (3, 0.25), (1, 0.15)],   # Mùi: Kỷ, Đinh, Ất
    8:  [(6, 0.6), (8, 0.25), (4, 0.15)],   # Thân: Canh, Nhâm, Mậu
    9:  [(7, 1.0)],                         # Dậu: Tân
    10: [(4, 0.6), (7, 0.25), (3, 0.15)],   # Tuất: Mậu, Tân, Đinh
    11: [(8, 0.7), (0, 0.3)],               # Hợi: Nhâm, Giáp
}

CHANGSHENG_NAMES = [
    "Trường Sinh", "Mộc Dục", "Quan Đới", "Lâm Quan",
    "Đế Vượng", "Suy", "Bệnh", "Tử", "Mộ", "Tuyệt", "Thai", "Dưỡng"
]

# Cung khởi Trường Sinh của 10 Thiên Can (Dương thuận, Âm nghịch chuẩn Tử Bình truyền thống)
STEM_CHANGSHENG_START = {
    0: (11, 1),  # Giáp: Hợi thuận
    1: (6, -1),  # Ất: Ngọ nghịch
    2: (2, 1),   # Bính: Dần thuận
    3: (9, -1),  # Đinh: Dậu nghịch
    4: (2, 1),   # Mậu: Dần thuận (Hỏa Thổ đồng cung)
    5: (9, -1),  # Kỷ: Dậu nghịch
    6: (5, 1),   # Canh: Tỵ thuận
    7: (0, -1),  # Tân: Tý nghịch
    8: (8, 1),   # Nhâm: Thân thuận
    9: (3, -1),  # Quý: Mão nghịch
}

ELEMENTS_ORDER = ["Mộc", "Hỏa", "Thổ", "Kim", "Thủy"]

# Cùng Thông Bảo Giám — Điều Hầu Dụng Thần ưu tiên theo Nhật Chủ (0..9) và Địa Chi Tháng (0..11)
QIONG_TONG_TIAOHOU: Dict[Tuple[int, int], str] = {
    # Giáp (0)
    (0, 2): "Bính, Quý (Xuân hàn cần Bính sưởi, Quý nhuận)",
    (0, 3): "Canh, Bính, Đinh (Dương Nhẫn vượng cần Canh tu tỉa, Đinh dẫn hỏa)",
    (0, 4): "Canh, Đinh, Nhâm (Mộc thoái khí, Kim khắc chế phối Đinh Nhâm)",
    (0, 5): "Quý, Đinh, Canh (Hạ Mộc khô khát cần Quý Thủy tưới trước)",
    (0, 6): "Quý, Đinh, Canh (Thương Quan sinh Tài hoặc Mộc Hỏa thông minh nhưng cần Quý nhuận)",
    (0, 7): "Quý, Canh, Đinh (Nửa đầu như tháng Ngọ dùng Quý, nửa sau dùng Canh Đinh)",
    (0, 8): "Canh, Đinh, Nhâm (Phách Giáp dẫn Đinh — đại quý cách)",
    (0, 9): "Đinh, Canh, Bính (Dùng Đinh chế Quan Sát, Bính điều hầu)",
    (0, 10): "Giáp, Đinh, Nhâm, Quý (Thổ táo cần Thủy nhuận, Giáp trợ thân, Đinh luyện Kim)",
    (0, 11): "Canh, Đinh, Bính, Mậu (Đông Thủy vượng cần Mậu ngăn nước, Bính sưởi ấm)",
    (0, 0): "Đinh, Canh, Bính (Hàn Mộc đóng băng, phi Bính Đinh bất noãn)",
    (0, 1): "Đinh, Canh, Bính (Đinh Hỏa thông căn tàng kỷ thổ, sưởi ấm hàn mộc)",
    # Ất (1)
    (1, 2): "Bính, Quý (Nắng ấm mưa xuân giúp hoa cỏ phồn vinh)",
    (1, 3): "Bính, Quý (Lộc vượng cần Bính tiết tú, Quý tưới gốc)",
    (1, 4): "Quý, Bính, Mậu (Thìn là kho nước, Bính Quý tương tế)",
    (1, 5): "Quý (Hoa cỏ mùa hạ khô héo, chuyên dùng Quý Thủy)",
    (1, 6): "Quý, Bính (Hạ chí về trước dùng Quý, về sau Bính Quý tịnh dụng)",
    (1, 7): "Quý, Bính (Nhuận thổ dưỡng mộc)",
    (1, 8): "Bính, Quý, Kỷ (Thu Kim nắm lệnh, dùng Kỷ lót gốc, Bính chế Kim, Quý hóa Sát)",
    (1, 9): "Quý, Bính, Đinh (Thu phân trước dùng Quý, sau dùng Bính)",
    (1, 10): "Quý, Tân (Mộc khô gặp kho hỏa cần Quý tưới)",
    (1, 11): "Bính, Mậu (Thủy phiếm mộc phù, dùng Bính sưởi, Mậu ngăn Thủy)",
    (1, 0): "Bính (Hàn cốc hồi xuân — chuyên lấy Bính Hỏa làm tôn)",
    (1, 1): "Bính (Đất lạnh sương giá, có Bính một hào cũng quý)",
    # Bính (2)
    (2, 2): "Nhâm, Canh (Nhật chiếu giang hồ — Nhâm Thủy phản chiếu rực rỡ)",
    (2, 3): "Nhâm, Kỷ (Ấn vượng dùng Nhâm tiết tú chế Kiêu)",
    (2, 4): "Nhâm, Giáp (Thực thần vượng dùng Nhâm phụ ánh sáng, Giáp sơ Thổ)",
    (2, 5): "Nhâm, Canh, Quý (Lửa hè rừng rực tối cần Nhâm Thủy + Canh phát nguồn)",
    (2, 6): "Nhâm, Canh (Dương Nhẫn cực viêm, không có Nhâm Canh dễ khô táo)",
    (2, 7): "Nhâm, Canh (Tam phục sinh hàn, vẫn lấy Nhâm Canh làm chủ)",
    (2, 8): "Nhâm, Mậu (Mặt trời chiều thu phản chiếu mặt sông)",
    (2, 9): "Nhâm, Quý (Tài vượng dùng Nhâm phụ trợ khí thế)",
    (2, 10): "Giáp, Nhâm (Tránh Thổ tối hỏa minh — dùng Giáp khơi Thổ sinh Bính, Nhâm rửa)",
    (2, 11): "Giáp, Mậu, Canh, Nhâm (Thất Sát đương quyền cần Giáp hóa Sát sinh thân)",
    (2, 0): "Nhâm, Mậu, Giáp (Đông Nhật cần Giáp sinh, Mậu chế Thủy)",
    (2, 1): "Nhâm, Giáp (Tuyết tan nắng ấm)",
    # Đinh (3)
    (3, 2): "Giáp, Canh (Canh Kim phách Giáp dẫn Đinh Hỏa cháy bền)",
    (3, 3): "Canh, Giáp (Ất Mộc cỏ khô khó giữ lửa lâu, cần Canh chẻ Giáp)",
    (3, 4): "Giáp, Canh (Thương quan vượng cần Giáp Ấn bội hộ)",
    (3, 5): "Giáp, Canh (Đế vượng Hỏa dùng Giáp Canh làm giàu nguồn nhiên liệu & tài)",
    (3, 6): "Nhâm, Canh, Quý (Hỏa quá vượng dùng Nhâm Canh Quý tế Hỏa tránh tự thiêu)",
    (3, 7): "Giáp, Nhâm, Canh (Mộc thoái khí cần Giáp sinh Đinh, Canh Nhâm điều tiết)",
    (3, 8): "Giáp, Canh, Bính (Thu Kim đắc lệnh, Đinh rèn Chân Kim, Giáp tiếp củi)",
    (3, 9): "Giáp, Canh, Bính (Tân Kim châu ngọc gặp Giáp Canh Đinh quý hiển)",
    (3, 10): "Giáp, Canh, Mậu (Thương Quan bội Ấn kiêm luyện Kim)",
    (3, 11): "Giáp, Canh (Đêm đông lạnh tuyệt đối không thể thiếu Giáp Mộc làm củi)",
    (3, 0): "Giáp, Canh (Thất Sát trùng trùng, Giáp Mộc hóa Sát sinh Đinh là cứu tinh)",
    (3, 1): "Giáp, Canh (Tài khố lạnh giá cần Giáp dẫn Đinh ấm cục)",
}


def ten_god_name(day_stem: int, other_stem: int) -> str:
    """Tính Thập Thần của other_stem đối với Nhật Chủ day_stem."""
    d_elem = ELEMENTS_ORDER.index(STEM_ELEMENTS[day_stem])
    o_elem = ELEMENTS_ORDER.index(STEM_ELEMENTS[other_stem])
    same_polarity = (day_stem % 2) == (other_stem % 2)
    diff = (o_elem - d_elem) % 5
    if diff == 0:
        return "Tỷ Kiên" if same_polarity else "Kiếp Tài"
    elif diff == 1:
        return "Thực Thần" if same_polarity else "Thương Quan"
    elif diff == 2:
        return "Thiên Tài" if same_polarity else "Chính Tài"
    elif diff == 3:
        return "Thất Sát" if same_polarity else "Chính Quan"
    else:
        return "Thiên Ấn" if same_polarity else "Chính Ấn"


def changsheng_stage(stem_idx: int, branch_idx: int) -> str:
    start_b, direction = STEM_CHANGSHENG_START[stem_idx]
    offset = ((branch_idx - start_b) * direction) % 12
    return CHANGSHENG_NAMES[offset]


def analyze_shen_sha(
    year_s: int, year_b: int, month_b: int, day_s: int, day_b: int, hour_b: int
) -> Dict[str, List[str]]:
    """Quét các Thần Sát trọng yếu trên 4 trụ (Năm, Tháng, Ngày, Giờ)."""
    pillars = [("Năm", year_b), ("Tháng", month_b), ("Ngày", day_b), ("Giờ", hour_b)]
    result: Dict[str, List[str]] = {"Năm": [], "Tháng": [], "Ngày": [], "Giờ": []}

    # 1. Thiên Ất Quý Nhân (lấy theo Can Ngày & Can Năm)
    thien_at_map = {
        0: (1, 7), 4: (1, 7), 6: (1, 7),  # Giáp Mậu Canh -> Sửu Mùi
        1: (0, 8), 5: (0, 8),             # Ất Kỷ -> Tý Thân
        2: (11, 9), 3: (11, 9),           # Bính Đinh -> Hợi Dậu
        8: (3, 5), 9: (3, 5),             # Nhâm Quý -> Mão Tỵ
        7: (6, 2),                        # Tân -> Ngọ Dần
    }
    # 2. Văn Xương Quý Nhân (theo Can Ngày)
    van_xuong_map = {0: 5, 1: 6, 2: 8, 3: 9, 4: 8, 5: 9, 6: 11, 7: 0, 8: 2, 9: 3}
    # 3. Lộc Thần & Dương Nhẫn (theo Can Ngày)
    loc_map = {0: 2, 1: 3, 2: 5, 3: 6, 4: 5, 5: 6, 6: 8, 7: 9, 8: 11, 9: 0}
    duong_nhan_map = {0: 3, 2: 6, 4: 6, 6: 9, 8: 0}  # Dương can kiến Đế Vượng

    # Dịch Mã, Đào Hoa, Hoa Cái, Tướng Tinh theo Tam Hợp Chi Năm & Chi Ngày
    def group_shen_sha(ref_b: int) -> Dict[str, int]:
        # Thân Tý Thìn (8,0,4) | Dần Ngọ Tuất (2,6,10) | Tỵ Dậu Sửu (5,9,1) | Hợi Mão Mùi (11,3,7)
        if ref_b in (8, 0, 4):
            return {"Dịch Mã": 2, "Đào Hoa": 9, "Hoa Cái": 4, "Tướng Tinh": 0}
        elif ref_b in (2, 6, 10):
            return {"Dịch Mã": 8, "Đào Hoa": 3, "Hoa Cái": 10, "Tướng Tinh": 6}
        elif ref_b in (5, 9, 1):
            return {"Dịch Mã": 11, "Đào Hoa": 6, "Hoa Cái": 1, "Tướng Tinh": 9}
        else:
            return {"Dịch Mã": 5, "Đào Hoa": 0, "Hoa Cái": 7, "Tướng Tinh": 3}

    y_grp = group_shen_sha(year_b)
    d_grp = group_shen_sha(day_b)

    # Cô Thần & Quả Tú theo Chi Năm
    if year_b in (11, 0, 1):
        co_than, qua_tu = 2, 10
    elif year_b in (2, 3, 4):
        co_than, qua_tu = 5, 1
    elif year_b in (5, 6, 7):
        co_than, qua_tu = 8, 4
    else:
        co_than, qua_tu = 11, 7

    for p_name, b in pillars:
        if b in thien_at_map[day_s] or b in thien_at_map[year_s]:
            result[p_name].append("Thiên Ất Quý Nhân")
        if b == van_xuong_map[day_s]:
            result[p_name].append("Văn Xương")
        if b == loc_map[day_s]:
            result[p_name].append("Lộc Thần")
        if day_s in duong_nhan_map and b == duong_nhan_map[day_s]:
            result[p_name].append("Dương Nhẫn")
        for s_label in ("Dịch Mã", "Đào Hoa", "Hoa Cái", "Tướng Tinh"):
            if (p_name != "Năm" and b == y_grp[s_label]) or (p_name != "Ngày" and b == d_grp[s_label]):
                if s_label not in result[p_name]:
                    result[p_name].append(s_label)
        if b == co_than:
            result[p_name].append("Cô Thần")
        if b == qua_tu:
            result[p_name].append("Quả Tú")

    # Khôi Canh tại trụ Ngày (Canh Thìn, Canh Tuất, Nhâm Thìn, Mậu Tuất)
    if (day_s, day_b) in [(6, 4), (6, 10), (8, 4), (4, 10)]:
        result["Ngày"].append("Khôi Canh Quý Cách")

    return result


def analyze_interactions(stems: List[int], branches: List[int]) -> List[str]:
    """Phát hiện Hợp, Xung, Hình, Hại, Tam Hợp, Tam Hội trên Tứ Trụ."""
    notes: List[str] = []
    p_labels = ["Năm", "Tháng", "Ngày", "Giờ"]

    # Thiên Can Ngũ Hợp & Xung
    stem_he = {(0, 5): "Hóa Thổ", (1, 6): "Hóa Kim", (2, 7): "Hóa Thủy", (3, 8): "Hóa Mộc", (4, 9): "Hóa Hỏa"}
    for i in range(4):
        for j in range(i + 1, 4):
            pair = tuple(sorted((stems[i], stems[j])))
            if pair in stem_he:
                notes.append(f"Thiên Can Hợp: {STEMS_VI[stems[i]]} ({p_labels[i]}) – {STEMS_VI[stems[j]]} ({p_labels[j]}) [{stem_he[pair]}]")
            elif abs(stems[i] - stems[j]) == 6:
                notes.append(f"Thiên Can Tương Xung: {STEMS_VI[stems[i]]} ({p_labels[i]}) – {STEMS_VI[stems[j]]} ({p_labels[j]})")

    # Địa Chi Lục Hợp, Lục Xung, Lục Hại
    luc_hop = {
        (0, 1): "Hóa Thổ", (2, 11): "Hóa Mộc", (3, 10): "Hóa Hỏa",
        (4, 9): "Hóa Kim", (5, 8): "Hóa Thủy", (6, 7): "Hóa Hỏa/Thổ"
    }
    luc_hai = {(0, 7), (1, 6), (2, 5), (3, 4), (8, 11), (9, 10)}
    tu_hinh = {4, 6, 9, 11}  # Thìn Ngọ Dậu Hợi tự hình

    for i in range(4):
        for j in range(i + 1, 4):
            pair = tuple(sorted((branches[i], branches[j])))
            b1, b2 = branches[i], branches[j]
            if pair in luc_hop:
                notes.append(f"Địa Chi Lục Hợp: {BRANCHES_VI[b1]} ({p_labels[i]}) – {BRANCHES_VI[b2]} ({p_labels[j]}) [{luc_hop[pair]}]")
            if abs(b1 - b2) == 6:
                notes.append(f"Địa Chi Lục Xung: {BRANCHES_VI[b1]} ({p_labels[i]}) – {BRANCHES_VI[b2]} ({p_labels[j]})")
            if pair in luc_hai:
                notes.append(f"Địa Chi Tương Hại: {BRANCHES_VI[b1]} ({p_labels[i]}) – {BRANCHES_VI[b2]} ({p_labels[j]})")
            if pair == (0, 3):
                notes.append(f"Vô Lễ Chi Hình: {BRANCHES_VI[b1]} ({p_labels[i]}) – {BRANCHES_VI[b2]} ({p_labels[j]})")
            if b1 == b2 and b1 in tu_hinh:
                notes.append(f"Tự Hình: {BRANCHES_VI[b1]} ({p_labels[i]}) – {BRANCHES_VI[b2]} ({p_labels[j]})")

    b_set = set(branches)
    # Tam Hợp Cục
    for trio, name in [((8, 0, 4), "Thân–Tý–Thìn Hợp Thủy Cục"),
                       ((11, 3, 7), "Hợi–Mão–Mùi Hợp Mộc Cục"),
                       ((2, 6, 10), "Dần–Ngọ–Tuất Hợp Hỏa Cục"),
                       ((5, 9, 1), "Tỵ–Dậu–Sửu Hợp Kim Cục")]:
        if set(trio).issubset(b_set):
            notes.append(f"Tam Hợp Toàn Cục: {name}")
    # Tam Hình
    if {2, 5, 8}.issubset(b_set):
        notes.append("Tam Hình Dần–Tỵ–Thân (Vô Ân Chi Hình)")
    if {1, 10, 7}.issubset(b_set):
        notes.append("Tam Hình Sửu–Tuất–Mùi (Trì Thế Chi Hình)")

    return notes


def compute_bazi_chart(
    dt_solar: datetime,
    gender: str = "nam",
    tz_hours: float = 7.0,
    target_year: Optional[int] = None,
    late_zi_mode: str = "split",  # "split" (sect=2): Dạ Tý giữ Can Ngày hiện tại, Can Giờ sang ngày kế; "next_day" (sect=1 lunar-python): từ 23:00 sang hẳn ngày hôm sau
    dt_clock_for_jieqi: Optional[datetime] = None,
) -> Dict[str, object]:
    """
    Tính toàn diện lá số Bát Tự Tứ Trụ:
    - Trụ Năm, Trụ Tháng & Đại Vận tính theo mốc vật lý tuyệt đối JD_UT của dt_clock_for_jieqi (đồng bộ 100% với 6tail/lunar-python & bazi-skill).
    - Trụ Ngày & Trụ Giờ tính theo dt_solar (Giờ Chân Thái Dương tại kinh độ nơi sinh, hoặc Giờ Đồng Hồ nếu tắt hiệu chỉnh).
    """
    if target_year is None:
        target_year = datetime.now().year
    if dt_clock_for_jieqi is None:
        dt_clock_for_jieqi = dt_solar

    solar_ctx = get_solar_term_context(dt_clock_for_jieqi, tz_hours)
    year_s = int(solar_ctx["year_stem"])
    year_b = int(solar_ctx["year_branch"])
    month_s = int(solar_ctx["month_stem"])
    month_b = int(solar_ctx["month_branch"])

    # Trụ Ngày & Trụ Giờ theo Giờ Mặt Trời tại địa phương (chú ý xử lý 23:00 - 23:59 Dạ Tý)
    jdn_today = jd_from_date(dt_solar.day, dt_solar.month, dt_solar.year)
    is_late_zi = dt_solar.hour == 23

    if is_late_zi and late_zi_mode == "next_day":
        jdn_for_day = jdn_today + 1
        jdn_for_hour_stem = jdn_today + 1
    elif is_late_zi and late_zi_mode == "split":
        jdn_for_day = jdn_today
        jdn_for_hour_stem = jdn_today + 1
    else:
        jdn_for_day = jdn_today
        jdn_for_hour_stem = jdn_today

    day_s = (jdn_for_day + 9) % 10
    day_b = (jdn_for_day + 1) % 12

    hour_b = ((dt_solar.hour + 1) // 2) % 12
    day_stem_for_hour = (jdn_for_hour_stem + 9) % 10
    # Ngũ Thử Độn tìm Can giờ từ Can ngày
    ty_hour_stem = (day_stem_for_hour % 5) * 2
    hour_s = (ty_hour_stem + hour_b) % 10

    stems = [year_s, month_s, day_s, hour_s]
    branches = [year_b, month_b, day_b, hour_b]
    p_keys = ["year", "month", "day", "hour"]
    p_titles = ["Năm", "Tháng", "Ngày", "Giờ"]

    shen_sha_map = analyze_shen_sha(year_s, year_b, month_b, day_s, day_b, hour_b)

    pillars_detail = {}
    for idx, (pk, pt) in enumerate(zip(p_keys, p_titles)):
        s, b = stems[idx], branches[idx]
        nayin_name, nayin_elem = nayin_for_stem_branch(s, b)
        tk1, tk2 = tuan_khong_for_pillar(s, b)
        hidden_list = []
        for hs, hw in HIDDEN_STEMS[b]:
            hidden_list.append({
                "stem": STEMS_VI[hs],
                "stem_zh": STEMS_ZH[hs],
                "element": STEM_ELEMENTS[hs],
                "ten_god": ten_god_name(day_s, hs),
                "weight": hw,
            })
        pillars_detail[pk] = {
            "label": pt,
            "can_chi": can_chi_name(s, b),
            "can_chi_zh": f"{STEMS_ZH[s]}{BRANCHES_ZH[b]}",
            "stem": STEMS_VI[s],
            "stem_element": STEM_ELEMENTS[s],
            "stem_yinyang": STEM_YINYANG[s],
            "stem_ten_god": "Nhật Chủ" if pk == "day" else ten_god_name(day_s, s),
            "branch": BRANCHES_VI[b],
            "branch_element": BRANCH_ELEMENTS[b],
            "hidden_stems": hidden_list,
            "nayin": nayin_name,
            "nayin_element": nayin_elem,
            "changsheng_from_day": changsheng_stage(day_s, b),
            "self_sitting": changsheng_stage(s, b),
            "tuan_khong": f"{BRANCHES_VI[tk1]} – {BRANCHES_VI[tk2]}",
            "shen_sha": shen_sha_map[pt],
        }

    # Chấm điểm Ngũ Hành & Cường Nhược Nhật Chủ
    elem_scores = {e: 0.0 for e in ELEMENTS_ORDER}
    # Trọng số: Can Năm (10), Can Tháng (12), Can Ngày (10 - bản thân), Can Giờ (10)
    # Chi Năm (10), Chi Tháng / Nguyệt Lệnh (32!), Chi Ngày (14), Chi Giờ (12) -> Tổng 110 điểm
    stem_weights = [10.0, 12.0, 10.0, 10.0]
    branch_weights = [10.0, 32.0, 14.0, 12.0]

    for i in range(4):
        elem_scores[STEM_ELEMENTS[stems[i]]] += stem_weights[i]
        for hs, hw in HIDDEN_STEMS[branches[i]]:
            elem_scores[STEM_ELEMENTS[hs]] += branch_weights[i] * hw

    day_elem = STEM_ELEMENTS[day_s]
    d_idx = ELEMENTS_ORDER.index(day_elem)
    resource_elem = ELEMENTS_ORDER[(d_idx - 1) % 5]  # Ấn
    output_elem = ELEMENTS_ORDER[(d_idx + 1) % 5]    # Thực Thương
    wealth_elem = ELEMENTS_ORDER[(d_idx + 2) % 5]    # Tài
    officer_elem = ELEMENTS_ORDER[(d_idx + 3) % 5]   # Quan Sát

    total_score = sum(elem_scores.values())
    support_score = elem_scores[day_elem] + elem_scores[resource_elem]
    support_pct = round((support_score / total_score) * 100.0, 1)

    if support_pct >= 78.0:
        strength_label = "Cực Vượng (Nghi xét Tòng Cường / Chuyên Vượng cách)"
        fuyi_favorable = [output_elem, wealth_elem, resource_elem]
        fuyi_unfavorable = [officer_elem]
    elif support_pct >= 52.0:
        strength_label = "Thân Vượng (Đủ lực gánh Tài Quan)"
        fuyi_favorable = [officer_elem, wealth_elem, output_elem]
        fuyi_unfavorable = [resource_elem, day_elem]
    elif support_pct >= 45.0:
        strength_label = "Trung Hòa Thiên Nhược / Cân Bằng"
        fuyi_favorable = [resource_elem, day_elem]
        fuyi_unfavorable = [wealth_elem, officer_elem]
    elif support_pct >= 20.0:
        strength_label = "Thân Nhược (Ưa Ấn Tỷ sinh phù)"
        fuyi_favorable = [resource_elem, day_elem]
        fuyi_unfavorable = [wealth_elem, officer_elem, output_elem]
    else:
        strength_label = "Cực Nhược (Nghi xét Tòng Nhược / Tòng Tài Sát Nhi)"
        fuyi_favorable = [wealth_elem, officer_elem, output_elem]
        fuyi_unfavorable = [day_elem, resource_elem]

    # Tra cứu Điều Hầu Cùng Thông Bảo Giám
    tiaohou_note = QIONG_TONG_TIAOHOU.get((day_s, month_b), "")
    if not tiaohou_note:
        if month_b in (11, 0, 1):
            tiaohou_note = "Sinh mùa Đông thủy hàn: Ưu tiên xét Bính/Đinh Hỏa điều hầu sưởi ấm cục."
        elif month_b in (5, 6, 7):
            tiaohou_note = "Sinh mùa Hạ hỏa táo: Ưu tiên xét Nhâm/Quý Thủy điều hầu nhuận cục."
        else:
            tiaohou_note = "Khí hậu Xuân/Thu ôn hòa: Trọng xét Phù Ức và Cách Cục Đề Cương."

    # Tính Khởi Đại Vận (Dương Nam Âm Nữ thuận hành -> tính tới Tiết sau; Âm Nam Dương Nữ nghịch hành -> tính lùi về Tiết trước)
    is_male = gender.strip().lower() in ("nam", "male", "m", "1")
    is_yang_year = (year_s % 2 == 0)
    forward = (is_male and is_yang_year) or ((not is_male) and (not is_yang_year))

    jd_ut = float(solar_ctx["jd_ut"])
    if forward:
        diff_days = max(0.0, float(solar_ctx["next_jie_jd"]) - jd_ut)
    else:
        diff_days = max(0.0, jd_ut - float(solar_ctx["prev_jie_jd"]))

    # 3 ngày = 1 năm (365.2425 ngày thực), 1 ngày = 4 tháng (120 ngày), 1 giờ = 5 ngày
    start_years_float = diff_days / 3.0
    start_age_years = int(start_years_float)
    rem_months_float = (start_years_float - start_age_years) * 12.0
    start_age_months = int(rem_months_float)
    start_age_days = int(round((rem_months_float - start_age_months) * 30.0))
    if start_age_days >= 30:
        start_age_days -= 30
        start_age_months += 1
    if start_age_months >= 12:
        start_age_months -= 12
        start_age_years += 1

    handover_dt = dt_clock_for_jieqi + timedelta(days=diff_days * 121.7475)  # 365.2425 / 3
    first_dayun_solar_year = handover_dt.year

    step_dir = 1 if forward else -1
    dayun_list = []
    for k in range(1, 10):
        dy_s = (month_s + k * step_dir) % 10
        dy_b = (month_b + k * step_dir) % 12
        sy = first_dayun_solar_year + (k - 1) * 10
        ey = sy + 9
        age_start = sy - dt_clock_for_jieqi.year + 1  # Tuổi mụ (hư tuế) truyền thống
        ny_name, _ = nayin_for_stem_branch(dy_s, dy_b)
        dayun_list.append({
            "step": k,
            "can_chi": can_chi_name(dy_s, dy_b),
            "can_chi_zh": f"{STEMS_ZH[dy_s]}{BRANCHES_ZH[dy_b]}",
            "stem_ten_god": ten_god_name(day_s, dy_s),
            "branch_main_ten_god": ten_god_name(day_s, HIDDEN_STEMS[dy_b][0][0]),
            "changsheng": changsheng_stage(day_s, dy_b),
            "nayin": ny_name,
            "solar_years": f"{sy}–{ey}",
            "start_year": sy,
            "end_year": ey,
            "nominal_age": f"{max(1, age_start)}–{max(1, age_start) + 9} tuổi mụ",
            "is_current": sy <= target_year <= ey,
        })

    # Lưu Niên năm mục tiêu (target_year)
    ln_s = (target_year + 6) % 10
    ln_b = (target_year + 8) % 12
    ln_nayin, _ = nayin_for_stem_branch(ln_s, ln_b)

    return {
        "gender": "Nam (Càn Tạo)" if is_male else "Nữ (Khôn Tạo)",
        "direction": "Thuận hành" if forward else "Nghịch hành",
        "late_zi_warning": (
            "Sinh vào giờ Dạ Tý (23:00–23:59): Đã áp dụng chuẩn Tý Chính/Dạ Tý (giữ Can Chi Ngày hiện tại, Can Giờ tính sang ngày kế). Nếu nghiệm lý thực tế lệch, hãy kiểm tra phương án sang hẳn ngày mới."
            if is_late_zi else None
        ),
        "solar_term_context": {
            "current_term": solar_ctx["current_solar_term"],
            "sun_longitude": solar_ctx["sun_longitude_deg"],
            "lap_xuan": solar_ctx["lap_xuan_local"],
            "prev_jie": f"{solar_ctx['prev_jie_name']} ({solar_ctx['prev_jie_local']})",
            "next_jie": f"{solar_ctx['next_jie_name']} ({solar_ctx['next_jie_local']})",
        },
        "pillars": pillars_detail,
        "day_master": {
            "stem": STEMS_VI[day_s],
            "stem_zh": STEMS_ZH[day_s],
            "element": day_elem,
            "yinyang": STEM_YINYANG[day_s],
            "support_percentage": support_pct,
            "strength_assessment": strength_label,
        },
        "five_elements_score": {
            k: {"score": round(v, 1), "pct": round((v / total_score) * 100.0, 1)}
            for k, v in elem_scores.items()
        },
        "yongshen_guidance": {
            "fuyi_favorable_elements": fuyi_favorable,
            "fuyi_unfavorable_elements": fuyi_unfavorable,
            "qiong_tong_tiaohou": tiaohou_note,
            "methodology_note": "Kết hợp Phù Ức + Điều Hầu (Cùng Thông Bảo Giám) + Thông Quan để chốt Dụng/Hỷ thần cuối cùng.",
        },
        "interactions": analyze_interactions(stems, branches),
        "dayun_handover": {
            "offset_after_birth": f"{start_age_years} năm {start_age_months} tháng {start_age_days} ngày",
            "exact_handover_date": handover_dt.strftime("%Y-%m-%d"),
            "first_dayun_year": first_dayun_solar_year,
        },
        "dayun": dayun_list,
        "target_liunian": {
            "year": target_year,
            "can_chi": can_chi_name(ln_s, ln_b),
            "stem_ten_god": ten_god_name(day_s, ln_s),
            "branch_main_ten_god": ten_god_name(day_s, HIDDEN_STEMS[ln_b][0][0]),
            "nayin": ln_nayin,
        },
    }
