# -*- coding: utf-8 -*-
"""
core_calendar.py — Bộ máy Thiên Văn Lịch Vạn Niên Việt Nam (UTC+7) & Quốc tế
Thuật toán chuẩn Jean Meeus (Astronomical Algorithms) & Hồ Ngọc Đức:
- Đổi Dương lịch <-> Âm lịch chính xác theo múi giờ (mặc định UTC+7 Việt Nam)
- Tính chính xác Hoàng kinh Mặt Trời (Solar Longitude) đến từng phút cho 24 Tiết Khí
- Quy đổi Giờ Chân Thái Dương (True Solar Time) theo kinh độ 63 tỉnh thành Việt Nam + Phương trình thời gian (EoT)
100% Python 3 Standard Library (Zero external dependencies).
"""

from __future__ import annotations
import math
from datetime import datetime, timedelta
from typing import Dict, Tuple, Optional, List

STEMS_VI = ["Giáp", "Ất", "Bính", "Đinh", "Mậu", "Kỷ", "Canh", "Tân", "Nhâm", "Quý"]
STEMS_ZH = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]
STEM_ELEMENTS = ["Mộc", "Mộc", "Hỏa", "Hỏa", "Thổ", "Thổ", "Kim", "Kim", "Thủy", "Thủy"]
STEM_YINYANG = ["Dương", "Âm", "Dương", "Âm", "Dương", "Âm", "Dương", "Âm", "Dương", "Âm"]

BRANCHES_VI = ["Tý", "Sửu", "Dần", "Mão", "Thìn", "Tỵ", "Ngọ", "Mùi", "Thân", "Dậu", "Tuất", "Hợi"]
BRANCHES_ZH = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]
BRANCH_ELEMENTS = ["Thủy", "Thổ", "Mộc", "Mộc", "Thổ", "Hỏa", "Hỏa", "Thổ", "Kim", "Kim", "Thổ", "Thủy"]
BRANCH_ANIMALS_VI = ["Chuột", "Trâu", "Hổ", "Mèo", "Rồng", "Rắn", "Ngựa", "Dê", "Khỉ", "Gà", "Chó", "Lợn"]

# 60 Hoa Giáp Nạp Âm (theo thứ tự 30 cặp từ Giáp Tý - Ất Sửu đến Nhâm Tuất - Quý Hợi)
NAYIN_30 = [
    ("Hải Trung Kim", "Kim"), ("Lư Trung Hỏa", "Hỏa"), ("Đại Lâm Mộc", "Mộc"),
    ("Lộ Bàng Thổ", "Thổ"), ("Kiếm Phong Kim", "Kim"), ("Sơn Đầu Hỏa", "Hỏa"),
    ("Giản Hạ Thủy", "Thủy"), ("Thành Đầu Thổ", "Thổ"), ("Bạch Lạp Kim", "Kim"),
    ("Dương Liễu Mộc", "Mộc"), ("Tuyền Trung Thủy", "Thủy"), ("Ốc Thượng Thổ", "Thổ"),
    ("Tích Lịch Hỏa", "Hỏa"), ("Tùng Bách Mộc", "Mộc"), ("Trường Lưu Thủy", "Thủy"),
    ("Sa Trung Kim", "Kim"), ("Sơn Hạ Hỏa", "Hỏa"), ("Bình Địa Mộc", "Mộc"),
    ("Bích Thượng Thổ", "Thổ"), ("Kim Bạch Kim", "Kim"), ("Phú Đăng Hỏa", "Hỏa"),
    ("Thiên Hà Thủy", "Thủy"), ("Đại Trạch Thổ", "Thổ"), ("Thoa Xuyến Kim", "Kim"),
    ("Tang Đố Mộc", "Mộc"), ("Đại Khê Thủy", "Thủy"), ("Sa Trung Thổ", "Thổ"),
    ("Thiên Thượng Hỏa", "Hỏa"), ("Thạch Lựu Mộc", "Mộc"), ("Đại Hải Thủy", "Thủy"),
]

# 24 Tiết Khí theo Hoàng kinh Mặt Trời (0° = Xuân Phân)
SOLAR_TERMS_24 = [
    (315, "Lập Xuân", "立春", 2),     # Khởi tháng Dần (1)
    (330, "Vũ Thủy", "雨水", 2),
    (345, "Kinh Trập", "惊蛰", 3),    # Khởi tháng Mão (2)
    (0,   "Xuân Phân", "春分", 3),
    (15,  "Thanh Minh", "清明", 4),   # Khởi tháng Thìn (3)
    (30,  "Cốc Vũ", "谷雨", 4),
    (45,  "Lập Hạ", "立夏", 5),       # Khởi tháng Tỵ (4)
    (60,  "Tiểu Mãn", "小满", 5),
    (75,  "Mang Chủng", "芒种", 6),   # Khởi tháng Ngọ (5)
    (90,  "Hạ Chí", "夏至", 6),
    (105, "Tiểu Thử", "小暑", 7),     # Khởi tháng Mùi (6)
    (120, "Đại Thử", "大暑", 7),
    (135, "Lập Thu", "立秋", 8),      # Khởi tháng Thân (7)
    (150, "Xử Thử", "处暑", 8),
    (165, "Bạch Lộ", "白露", 9),      # Khởi tháng Dậu (8)
    (180, "Thu Phân", "秋分", 9),
    (195, "Hàn Lộ", "寒露", 10),      # Khởi tháng Tuất (9)
    (210, "Sương Giáng", "霜降", 10),
    (225, "Lập Đông", "立冬", 11),    # Khởi tháng Hợi (10)
    (240, "Tiểu Tuyết", "小雪", 11),
    (255, "Đại Tuyết", "大雪", 0),    # Khởi tháng Tý (11)
    (270, "Đông Chí", "冬至", 0),
    (285, "Tiểu Hàn", "小寒", 1),     # Khởi tháng Sửu (12)
    (300, "Đại Hàn", "大寒", 1),
]

# 12 Tiết (Jie) chuyển tháng Bát Tự theo thứ tự Hoàng kinh
JIE_12_BOUNDARIES = [
    (315, 2, "Lập Xuân"),   # Dần
    (345, 3, "Kinh Trập"),  # Mão
    (15,  4, "Thanh Minh"), # Thìn
    (45,  5, "Lập Hạ"),     # Tỵ
    (75,  6, "Mang Chủng"), # Ngọ
    (105, 7, "Tiểu Thử"),   # Mùi
    (135, 8, "Lập Thu"),    # Thân
    (165, 9, "Bạch Lộ"),    # Dậu
    (195, 10, "Hàn Lộ"),    # Tuất
    (225, 11, "Lập Đông"),  # Hợi
    (255, 0, "Đại Tuyết"),  # Tý
    (285, 1, "Tiểu Hàn"),   # Sửu
]

VN_PROVINCE_LONGITUDES: Dict[str, float] = {
    "ha noi": 105.85, "hà nội": 105.85, "hn": 105.85,
    "ho chi minh": 106.63, "hồ chí minh": 106.63, "tphcm": 106.63, "sai gon": 106.63, "sài gòn": 106.63, "hcm": 106.63,
    "hai phong": 106.68, "hải phòng": 106.68,
    "da nang": 108.20, "đà nẵng": 108.20,
    "can tho": 105.78, "cần thơ": 105.78,
    "hue": 107.59, "huế": 107.59, "thua thien hue": 107.59,
    "quang ninh": 107.08, "quảng ninh": 107.08, "ha long": 107.08,
    "bac ninh": 106.07, "bắc ninh": 106.07,
    "hai duong": 106.33, "hải dương": 106.33,
    "hung yen": 106.05, "hưng yên": 106.05,
    "nam dinh": 106.17, "nam định": 106.17,
    "thai binh": 106.34, "thái bình": 106.34,
    "ninh binh": 105.97, "ninh bình": 105.97,
    "vinh phuc": 105.60, "vĩnh phúc": 105.60,
    "phu tho": 105.40, "phú thọ": 105.40,
    "thai nguyen": 105.84, "thái nguyên": 105.84,
    "bac giang": 106.19, "bắc giang": 106.19,
    "lang son": 106.76, "lạng sơn": 106.76,
    "cao bang": 106.26, "cao bằng": 106.26,
    "lao cai": 103.97, "lào cai": 103.97,
    "yen bai": 104.87, "yên bái": 104.87,
    "son la": 103.91, "sơn la": 103.91,
    "dien bien": 103.02, "điện biên": 103.02,
    "lai chau": 103.46, "lai châu": 103.46,
    "hoa binh": 105.34, "hòa bình": 105.34,
    "thanh hoa": 105.78, "thanh hóa": 105.78,
    "nghe an": 105.68, "nghệ an": 105.68, "vinh": 105.68,
    "ha tinh": 105.90, "hà tĩnh": 105.90,
    "quang binh": 106.62, "quảng bình": 106.62,
    "quang tri": 107.10, "quảng trị": 107.10,
    "quang nam": 108.47, "quảng nam": 108.47,
    "quang ngai": 108.80, "quảng ngãi": 108.80,
    "binh dinh": 109.22, "bình định": 109.22, "quy nhon": 109.22,
    "phu yen": 109.30, "phú yên": 109.30,
    "khanh hoa": 109.19, "khánh hòa": 109.19, "nha trang": 109.19,
    "ninh thuan": 108.99, "ninh thuận": 108.99,
    "binh thuan": 108.10, "bình thuận": 108.10,
    "kon tum": 108.00,
    "gia lai": 108.00, "pleiku": 108.00,
    "dak lak": 108.04, "đắk lắk": 108.04, "buon ma thuot": 108.04,
    "dak nong": 107.69, "đắk nông": 107.69,
    "lam dong": 108.44, "lâm đồng": 108.44, "da lat": 108.44, "đà lạt": 108.44,
    "binh phuoc": 106.89, "bình phước": 106.89,
    "tay ninh": 106.10, "tây ninh": 106.10,
    "binh duong": 106.65, "bình dương": 106.65,
    "dong nai": 106.82, "đồng nai": 106.82, "bien hoa": 106.82,
    "ba ria vung tau": 107.08, "vung tau": 107.08, "vũng tàu": 107.08,
    "long an": 106.41,
    "tien giang": 106.36, "tiền giang": 106.36,
    "ben tre": 106.38, "bến tre": 106.38,
    "tra vinh": 106.34, "trà vinh": 106.34,
    "vinh long": 105.97, "vĩnh long": 105.97,
    "dong thap": 105.63, "đồng tháp": 105.63,
    "an giang": 105.43,
    "kien giang": 105.08, "kiên giang": 105.08, "phu quoc": 103.96, "phú quốc": 103.96,
    "hau giang": 105.47, "hậu giang": 105.47,
    "soc trang": 105.97, "sóc trăng": 105.97,
    "bac lieu": 105.72, "bạc liêu": 105.72,
    "ca mau": 105.15, "cà mau": 105.15,
}


def jd_from_date(dd: int, mm: int, yy: int) -> int:
    """Số ngày Julian nguyên tại 12:00 UT của ngày Dương lịch dd/mm/yy."""
    a = (14 - mm) // 12
    y = yy + 4800 - a
    m = mm + 12 * a - 3
    jd = dd + (153 * m + 2) // 5 + 365 * y + y // 4 - y // 100 + y // 400 - 32045
    if jd < 2299161:
        jd = dd + (153 * m + 2) // 5 + 365 * y + y // 4 - 32083
    return jd


def date_from_jd(jd: int) -> Tuple[int, int, int]:
    """Đổi số ngày Julian nguyên sang (dd, mm, yy) Dương lịch."""
    if jd > 2299160:
        a = jd + 32044
        b = (4 * a + 3) // 146097
        c = a - (b * 146097) // 4
    else:
        b = 0
        c = jd + 32082
    d = (4 * c + 3) // 1461
    e = c - (1461 * d) // 4
    m = (5 * e + 2) // 153
    day = e - (153 * m + 2) // 5 + 1
    month = m + 3 - 12 * (m // 10)
    year = b * 100 + d - 4800 + m // 10
    return day, month, year


def datetime_to_jd_ut(dt: datetime, tz_hours: float = 7.0) -> float:
    """Đổi giờ địa phương (múi giờ tz_hours) sang Julian Day thực theo UT."""
    ut_dt = dt - timedelta(hours=tz_hours)
    jdn = jd_from_date(ut_dt.day, ut_dt.month, ut_dt.year)
    day_fraction = (ut_dt.hour - 12.0) / 24.0 + ut_dt.minute / 1440.0 + ut_dt.second / 86400.0
    return jdn + day_fraction


def jd_ut_to_datetime(jd_ut: float, tz_hours: float = 7.0) -> datetime:
    """Đổi Julian Day thực UT sang datetime địa phương theo tz_hours."""
    jd_local = jd_ut + tz_hours / 24.0 + 0.5
    z = int(math.floor(jd_local))
    f = jd_local - z
    dd, mm, yy = date_from_jd(z)
    total_seconds = int(round(f * 86400))
    if total_seconds >= 86400:
        total_seconds -= 86400
        dd, mm, yy = date_from_jd(z + 1)
    hh = total_seconds // 3600
    mi = (total_seconds % 3600) // 60
    ss = total_seconds % 60
    return datetime(yy, mm, dd, hh, mi, ss)


def new_moon_jd(k: int) -> float:
    """Julian Day (UT) của điểm Sóc thứ k tính từ Sóc 1900-01-01 (Jean Meeus)."""
    T = k / 1236.85
    T2 = T * T
    T3 = T2 * T
    dr = math.pi / 180.0
    Jd1 = 2415020.75933 + 29.53058868 * k + 0.0001178 * T2 - 0.000000155 * T3
    Jd1 += 0.00033 * math.sin((166.56 + 132.87 * T - 0.009173 * T2) * dr)
    M = 359.2242 + 29.10535608 * k - 0.0000333 * T2 - 0.00000347 * T3
    Mpr = 306.0253 + 385.81691806 * k + 0.0107306 * T2 + 0.00001236 * T3
    F = 21.2964 + 390.67050646 * k - 0.0016528 * T2 - 0.00000239 * T3
    C1 = (0.1734 - 0.000393 * T) * math.sin(M * dr) + 0.0021 * math.sin(2 * dr * M)
    C1 = C1 - 0.4068 * math.sin(Mpr * dr) + 0.0161 * math.sin(dr * 2 * Mpr)
    C1 = C1 - 0.0004 * math.sin(dr * 3 * Mpr)
    C1 = C1 + 0.0104 * math.sin(dr * 2 * F) - 0.0051 * math.sin(dr * (M + Mpr))
    C1 = C1 - 0.0074 * math.sin(dr * (M - Mpr)) + 0.0004 * math.sin(dr * (2 * F + M))
    C1 = C1 - 0.0004 * math.sin(dr * (2 * F - M)) - 0.0006 * math.sin(dr * (2 * F + Mpr))
    C1 = C1 + 0.0010 * math.sin(dr * (2 * F - Mpr)) + 0.0005 * math.sin(dr * (2 * Mpr + M))
    if T < -11:
        deltat = 0.001 + 0.000839 * T + 0.0002261 * T2 - 0.00000845 * T3 - 0.000000081 * T * T3
    else:
        deltat = -0.000278 + 0.000265 * T + 0.000262 * T2
    return Jd1 + C1 - deltat


def get_new_moon_day(k: int, tz_hours: float = 7.0) -> int:
    """Số ngày Julian nguyên (theo giờ địa phương tz_hours) chứa điểm Sóc thứ k."""
    return int(math.floor(new_moon_jd(k) + 0.5 + tz_hours / 24.0))


def sun_longitude_deg(jd_ut: float) -> float:
    """Hoàng kinh biểu kiến của Mặt Trời (0°..360°) tại thời điểm jd_ut (Jean Meeus Ch. 25)."""
    T = (jd_ut - 2451545.0) / 36525.0
    T2 = T * T
    dr = math.pi / 180.0
    L0 = 280.46646 + 36000.76983 * T + 0.0003032 * T2
    M = 357.52911 + 35999.05029 * T - 0.0001537 * T2
    C = (
        (1.914602 - 0.004817 * T - 0.000014 * T2) * math.sin(dr * M)
        + (0.019993 - 0.000101 * T) * math.sin(dr * 2 * M)
        + 0.000289 * math.sin(dr * 3 * M)
    )
    true_long = L0 + C
    omega = 125.04 - 1934.136 * T
    apparent_long = true_long - 0.00569 - 0.00478 * math.sin(dr * omega)
    return apparent_long % 360.0


def get_sun_longitude_sector(day_number: int, tz_hours: float = 7.0) -> int:
    """Cung Hoàng đạo Mặt Trời (0..11, mỗi cung 30°) tại 00:00 ngày kế tiếp (dùng xác định tháng nhuận Âm lịch)."""
    jd_midnight = day_number - 0.5 - tz_hours / 24.0
    return int(math.floor(sun_longitude_deg(jd_midnight) / 30.0))


def get_lunar_month11(yy: int, tz_hours: float = 7.0) -> int:
    """Tìm ngày mùng 1 tháng 11 Âm lịch (tháng chứa Đông Chí) của năm yy."""
    off = jd_from_date(31, 12, yy) - 2415021.0
    k = int(math.floor(off / 29.530588853))
    nm = get_new_moon_day(k, tz_hours)
    sun_long = get_sun_longitude_sector(nm, tz_hours)
    if sun_long >= 9:
        nm = get_new_moon_day(k - 1, tz_hours)
    return nm


def get_leap_month_offset(a11: int, tz_hours: float = 7.0) -> int:
    """Xác định vị trí tháng nhuận trong năm nhuận Âm lịch."""
    k = int(math.floor((a11 - 2415021.076998695) / 29.530588853 + 0.5))
    last = 0
    i = 1
    arc = get_sun_longitude_sector(get_new_moon_day(k + i, tz_hours), tz_hours)
    while True:
        last = arc
        i += 1
        arc = get_sun_longitude_sector(get_new_moon_day(k + i, tz_hours), tz_hours)
        if not (arc != last and i < 14):
            break
    return i - 1


def solar_to_lunar(dd: int, mm: int, yy: int, tz_hours: float = 7.0) -> Dict[str, int]:
    """
    Đổi Dương lịch -> Âm lịch chuẩn theo tz_hours (7.0 = Việt Nam, 8.0 = Trung Quốc/Quốc tế).
    Trả về dict: {day, month, year, is_leap, jd, month_days}
    """
    day_number = jd_from_date(dd, mm, yy)
    k = int(math.floor((day_number - 2415021.076998695) / 29.530588853))
    month_start = get_new_moon_day(k + 1, tz_hours)
    if month_start > day_number:
        month_start = get_new_moon_day(k, tz_hours)
        next_month_start = get_new_moon_day(k + 1, tz_hours)
    else:
        next_month_start = get_new_moon_day(k + 2, tz_hours)

    a11 = get_lunar_month11(yy, tz_hours)
    b11 = a11
    if a11 >= month_start:
        lunar_year = yy
        a11 = get_lunar_month11(yy - 1, tz_hours)
    else:
        lunar_year = yy + 1
        b11 = get_lunar_month11(yy + 1, tz_hours)

    lunar_day = day_number - month_start + 1
    diff = int(round((month_start - a11) / 29.0))
    lunar_leap = 0
    lunar_month = diff + 11
    if b11 - a11 > 365:
        leap_month_diff = get_leap_month_offset(a11, tz_hours)
        if diff >= leap_month_diff:
            lunar_month = diff + 10
            if diff == leap_month_diff:
                lunar_leap = 1
    if lunar_month > 12:
        lunar_month -= 12
    if lunar_month >= 11 and diff < 4:
        lunar_year -= 1

    return {
        "day": lunar_day,
        "month": lunar_month,
        "year": lunar_year,
        "is_leap": lunar_leap,
        "jd": day_number,
        "month_days": next_month_start - month_start,
    }


def lunar_to_solar(lunar_day: int, lunar_month: int, lunar_year: int, lunar_leap: int = 0, tz_hours: float = 7.0) -> Tuple[int, int, int]:
    """Đổi Âm lịch -> Dương lịch (dd, mm, yy) theo tz_hours."""
    if lunar_month < 11:
        a11 = get_lunar_month11(lunar_year - 1, tz_hours)
        b11 = get_lunar_month11(lunar_year, tz_hours)
    else:
        a11 = get_lunar_month11(lunar_year, tz_hours)
        b11 = get_lunar_month11(lunar_year + 1, tz_hours)
    k = int(math.floor(0.5 + (a11 - 2415021.076998695) / 29.530588853))
    off = lunar_month - 11
    if off < 0:
        off += 12
    if b11 - a11 > 365:
        leap_off = get_leap_month_offset(a11, tz_hours)
        leap_month = leap_off - 2
        if leap_month < 0:
            leap_month += 12
        if lunar_leap != 0 and lunar_month != leap_month:
            raise ValueError(f"Năm {lunar_year} không có tháng {lunar_month} nhuận!")
        elif lunar_leap != 0 or off >= leap_off:
            off += 1
    month_start = get_new_moon_day(k + off, tz_hours)
    return date_from_jd(month_start + lunar_day - 1)


def find_solar_term_jd_ut(approx_jd_ut: float, target_deg: float) -> float:
    """Tìm thời điểm chính xác (JD UT, sai số < 1 giây) khi Mặt Trời đạt Hoàng kinh target_deg."""
    jd = approx_jd_ut
    for _ in range(15):
        cur = sun_longitude_deg(jd)
        diff = (target_deg - cur + 180.0) % 360.0 - 180.0
        if abs(diff) < 1e-6:
            break
        # Tốc độ chuyển động biểu kiến trung bình Mặt Trời ~ 0.985647 độ/ngày
        jd += diff / 0.98564736
    return jd


def equation_of_time_minutes(jd_ut: float) -> float:
    """Phương trình thời gian (Equation of Time) tính bằng phút tại thời điểm jd_ut."""
    T = (jd_ut - 2451545.0) / 36525.0
    dr = math.pi / 180.0
    eps = 23.439291 - 0.0130042 * T
    L0 = (280.46646 + 36000.76983 * T) % 360.0
    e = 0.016708634 - 0.000042037 * T
    M = (357.52911 + 35999.05029 * T) % 360.0
    y = math.tan(dr * eps / 2.0) ** 2
    eot_rad = (
        y * math.sin(2 * dr * L0)
        - 2 * e * math.sin(dr * M)
        + 4 * e * y * math.sin(dr * M) * math.cos(2 * dr * L0)
        - 0.5 * y * y * math.sin(4 * dr * L0)
        - 1.25 * e * e * math.sin(2 * dr * M)
    )
    return (eot_rad / dr) * 4.0


def compute_true_solar_time(
    dt_clock: datetime,
    place: Optional[str] = None,
    longitude: Optional[float] = None,
    tz_hours: float = 7.0,
) -> Dict[str, object]:
    """
    Tính Giờ Chân Thái Dương (True Solar Time) và kiểm tra xem có bị nhảy canh giờ so với Giờ Đồng Hồ hay không.
    """
    std_meridian = tz_hours * 15.0  # UTC+7 -> 105.0°E
    resolved_long = longitude
    resolved_place = place or "Mặc định Việt Nam (105.85°E - Hà Nội)"
    if resolved_long is None:
        if place:
            key = place.strip().lower()
            for k_name, lon_val in VN_PROVINCE_LONGITUDES.items():
                if k_name in key or key in k_name:
                    resolved_long = lon_val
                    break
        if resolved_long is None:
            resolved_long = 105.85  # Mặc định Hà Nội

    jd_ut = datetime_to_jd_ut(dt_clock, tz_hours)
    lon_offset_min = (resolved_long - std_meridian) * 4.0
    eot_min = equation_of_time_minutes(jd_ut)
    total_offset_min = lon_offset_min + eot_min
    dt_true = dt_clock + timedelta(minutes=total_offset_min)

    clock_branch = ((dt_clock.hour + 1) // 2) % 12
    true_branch = ((dt_true.hour + 1) // 2) % 12

    return {
        "place": resolved_place,
        "longitude": round(resolved_long, 2),
        "standard_meridian": std_meridian,
        "longitude_offset_min": round(lon_offset_min, 2),
        "eot_min": round(eot_min, 2),
        "total_offset_min": round(total_offset_min, 2),
        "clock_time": dt_clock.strftime("%Y-%m-%d %H:%M"),
        "true_solar_time": dt_true.strftime("%Y-%m-%d %H:%M"),
        "true_datetime": dt_true,
        "clock_branch_idx": clock_branch,
        "clock_branch_name": BRANCHES_VI[clock_branch],
        "true_branch_idx": true_branch,
        "true_branch_name": BRANCHES_VI[true_branch],
        "branch_changed": clock_branch != true_branch,
    }


def build_time_sync_report(
    dt_clock: datetime,
    place: Optional[str] = None,
    longitude: Optional[float] = None,
    tz_hours: float = 7.0,
) -> Dict[str, object]:
    """
    Báo cáo đồng bộ hóa thời gian vật lý & lịch pháp giữa Việt Nam (UTC+7) và các GitHub quốc tế (UTC+8: iztro, 6tail/lunar, bazi-skill).
    - Mốc vật lý tuyệt đối (UTC & JD_UT): Dùng chung 100% toàn cầu để xét 24 Tiết Khí (Lập Xuân, 12 Tiết Bát Tự & Kỳ Môn).
    - Lịch Âm UTC+7 (Việt Nam - Hồ Ngọc Đức) vs Lịch Âm UTC+8 (Quốc tế - Tử Kim Sơn / iztro): Phát hiện tự động nếu ngày sinh rơi vào 0.3% ngày lệch Sóc/Nhuận.
    """
    tst = compute_true_solar_time(dt_clock, place=place, longitude=longitude, tz_hours=tz_hours)
    jd_ut = datetime_to_jd_ut(dt_clock, tz_hours)
    dt_utc = dt_clock - timedelta(hours=tz_hours)
    dt_beijing_instant = dt_utc + timedelta(hours=8.0)

    lunar_vn = solar_to_lunar(dt_clock.day, dt_clock.month, dt_clock.year, 7.0)
    lunar_intl = solar_to_lunar(dt_clock.day, dt_clock.month, dt_clock.year, 8.0)
    same_lunar = (
        lunar_vn["day"] == lunar_intl["day"]
        and lunar_vn["month"] == lunar_intl["month"]
        and lunar_vn["year"] == lunar_intl["year"]
        and lunar_vn["is_leap"] == lunar_intl["is_leap"]
    )

    return {
        "input_clock_local": dt_clock.strftime("%Y-%m-%d %H:%M"),
        "timezone_utc": tz_hours,
        "utc_instant": dt_utc.strftime("%Y-%m-%d %H:%M UTC"),
        "beijing_utc8_instant": dt_beijing_instant.strftime("%Y-%m-%d %H:%M (UTC+8)"),
        "jd_ut": round(jd_ut, 6),
        "true_solar_time_local": tst["true_solar_time"],
        "longitude_deg": tst["longitude"],
        "longitude_offset_min": tst["longitude_offset_min"],
        "equation_of_time_min": tst["eot_min"],
        "total_solar_offset_min": tst["total_offset_min"],
        "lunar_vn_utc7": f"{lunar_vn['day']:02d}/{lunar_vn['month']:02d}{'N' if lunar_vn['is_leap'] else ''}/{lunar_vn['year']}",
        "lunar_intl_utc8": f"{lunar_intl['day']:02d}/{lunar_intl['month']:02d}{'N' if lunar_intl['is_leap'] else ''}/{lunar_intl['year']}",
        "lunar_calendars_identical": same_lunar,
        "sync_note": (
            "Đồng bộ 100%: Lịch Âm Việt Nam (UTC+7) và Quốc tế (iztro/6tail UTC+8) trùng khớp hoàn toàn; mốc Tiết Khí Bát Tự khóa theo UTC tuyệt đối."
            if same_lunar else
            f"LƯU Ý LỆCH SÓC MÚI GIỜ: Ngày Dương lịch này tại Việt Nam (UTC+7) là {lunar_vn['day']:02d}/{lunar_vn['month']:02d}/{lunar_vn['year']} ÂL, nhưng trên lịch Trung Quốc/iztro (UTC+8) là {lunar_intl['day']:02d}/{lunar_intl['month']:02d}/{lunar_intl['year']} ÂL. Có thể chuyển đổi qua lại bằng --calendar-std vn|intl."
        ),
    }


def can_chi_name(stem_idx: int, branch_idx: int) -> str:
    return f"{STEMS_VI[stem_idx % 10]} {BRANCHES_VI[branch_idx % 12]}"


def nayin_for_stem_branch(stem_idx: int, branch_idx: int) -> Tuple[str, str]:
    """Tìm tên Nạp Âm và Ngũ hành Nạp Âm từ chỉ số Thiên Can (0..9) & Địa Chi (0..11)."""
    # Tìm vị trí 0..59 trong Lục Thập Hoa Giáp
    # stem_idx ≡ idx (mod 10), branch_idx ≡ idx (mod 12)
    for idx in range(60):
        if idx % 10 == (stem_idx % 10) and idx % 12 == (branch_idx % 12):
            return NAYIN_30[idx // 2]
    return ("Không xác định", "Thổ")


def tuan_khong_for_pillar(stem_idx: int, branch_idx: int) -> Tuple[int, int]:
    """Trả về 2 Địa Chi Tuần Không (Không Vong) của trụ (stem_idx, branch_idx)."""
    # Đầu tuần Giáp có địa chi là (branch_idx - stem_idx) % 12
    giap_branch = (branch_idx - stem_idx) % 12
    return ((giap_branch - 2) % 12, (giap_branch - 1) % 12)


def get_solar_term_context(dt_local: datetime, tz_hours: float = 7.0) -> Dict[str, object]:
    """
    Xác định chính xác vị trí Hoàng kinh Mặt Trời tại thời điểm sinh,
    Năm Can Chi theo Lập Xuân, Tháng Can Chi theo 12 Tiết, và khoảng cách tới Tiết trước/sau.
    """
    jd_ut = datetime_to_jd_ut(dt_local, tz_hours)
    sun_deg = sun_longitude_deg(jd_ut)

    # Tìm Lập Xuân (315°) của năm Dương lịch dt_local.year (thường rơi vào 3–5 tháng 2)
    approx_lap_xuan = datetime_to_jd_ut(datetime(dt_local.year, 2, 4, 12, 0), tz_hours)
    lap_xuan_jd = find_solar_term_jd_ut(approx_lap_xuan, 315.0)

    if jd_ut < lap_xuan_jd:
        bazi_year = dt_local.year - 1
    else:
        bazi_year = dt_local.year

    year_stem = (bazi_year + 6) % 10
    year_branch = (bazi_year + 8) % 12

    # Xác định đang nằm trong khoảng giữa 2 Tiết (Jie) nào
    # Chuyển hệ quy chiếu từ 315° làm gốc 0..360°
    shifted = (sun_deg - 315.0) % 360.0
    month_ord = int(math.floor(shifted / 30.0))  # 0=Dần, 1=Mão, ..., 11=Sửu
    month_branch = (2 + month_ord) % 12

    prev_jie_deg, _, prev_jie_name = JIE_12_BOUNDARIES[month_ord]
    next_jie_deg, _, next_jie_name = JIE_12_BOUNDARIES[(month_ord + 1) % 12]

    # Ước lượng JD của Tiết trước và Tiết sau từ góc chênh lệch
    deg_since_prev = (sun_deg - prev_jie_deg) % 360.0
    deg_to_next = (next_jie_deg - sun_deg) % 360.0

    prev_jie_jd = find_solar_term_jd_ut(jd_ut - deg_since_prev / 0.9856, prev_jie_deg)
    next_jie_jd = find_solar_term_jd_ut(jd_ut + deg_to_next / 0.9856, next_jie_deg)

    # Ngũ Hổ Độn tìm Can tháng từ Can năm Bát Tự
    dan_month_stem = ((year_stem % 5) * 2 + 2) % 10
    month_stem = (dan_month_stem + month_ord) % 10

    # Tiết khí hiện tại (24 tiết khí, mỗi tiết 15°)
    term24_ord = int(math.floor(((sun_deg - 315.0) % 360.0) / 15.0))
    cur_term_deg, cur_term_vi, cur_term_zh, _ = SOLAR_TERMS_24[term24_ord]

    return {
        "jd_ut": jd_ut,
        "sun_longitude_deg": round(sun_deg, 4),
        "current_solar_term": f"{cur_term_vi} ({cur_term_zh} - {cur_term_deg}°)",
        "bazi_year": bazi_year,
        "year_stem": year_stem,
        "year_branch": year_branch,
        "month_ord_from_dan": month_ord,
        "month_stem": month_stem,
        "month_branch": month_branch,
        "prev_jie_name": prev_jie_name,
        "prev_jie_local": jd_ut_to_datetime(prev_jie_jd, tz_hours).strftime("%Y-%m-%d %H:%M"),
        "prev_jie_jd": prev_jie_jd,
        "next_jie_name": next_jie_name,
        "next_jie_local": jd_ut_to_datetime(next_jie_jd, tz_hours).strftime("%Y-%m-%d %H:%M"),
        "next_jie_jd": next_jie_jd,
        "lap_xuan_local": jd_ut_to_datetime(lap_xuan_jd, tz_hours).strftime("%Y-%m-%d %H:%M"),
    }
