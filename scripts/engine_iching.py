# -*- coding: utf-8 -*-
"""
engine_iching.py — Engine Kinh Dịch Toàn Diện:
1. Chu Dịch 64 Quẻ (Tên Hán-Việt, Quái Từ, Tượng Quẻ, Triết lý hành động)
2. Lục Hào Nạp Giáp chuẩn Kinh Phòng / Tăng San Bốc Dịch (Thế/Ứng, Lục Thân, Lục Thần, Phục Thần, Tuần Không, Nguyệt Phá, Ám Động, Hồi Đầu Sinh/Khắc, Tiến/Thoái Thần)
3. Mai Hoa Dịch Số (Thể Quái - Dụng Quái - Hổ Quái - Biến Quái)
4. Kỳ Môn Độn Giáp Thời Gia (Sách Bổ pháp - Cửu Cung Lạc Thư, Dương/Âm Độn, Trực Phù, Trực Sử, Cửu Tinh, Bát Môn, Bát Thần)
"""

from __future__ import annotations
import secrets
from datetime import datetime
from typing import Dict, List, Tuple, Optional

from core_calendar import (
    STEMS_VI, BRANCHES_VI, BRANCH_ELEMENTS,
    jd_from_date, solar_to_lunar, get_solar_term_context,
    can_chi_name, tuan_khong_for_pillar,
)

# Bát Quái Tiên Thiên / Hậu Thiên: tuple 3 hào TỪ DƯỚI LÊN (hào 1, hào 2, hào 3): 1=Dương, 0=Âm
TRIGRAMS: Dict[Tuple[int, int, int], Dict[str, object]] = {
    (1, 1, 1): {"num_xt": 1, "name": "Càn",  "symbol": "☰", "nature": "Thiên (Trời)", "element": "Kim"},
    (1, 1, 0): {"num_xt": 2, "name": "Đoài", "symbol": "☱", "nature": "Trạch (Đầm)",  "element": "Kim"},
    (1, 0, 1): {"num_xt": 3, "name": "Ly",   "symbol": "☲", "nature": "Hỏa (Lửa)",    "element": "Hỏa"},
    (1, 0, 0): {"num_xt": 4, "name": "Chấn", "symbol": "☳", "nature": "Lôi (Sấm)",    "element": "Mộc"},
    (0, 1, 1): {"num_xt": 5, "name": "Tốn",  "symbol": "☴", "nature": "Phong (Gió)",  "element": "Mộc"},
    (0, 1, 0): {"num_xt": 6, "name": "Khảm", "symbol": "☵", "nature": "Thủy (Nước)",  "element": "Thủy"},
    (0, 0, 1): {"num_xt": 7, "name": "Cấn",  "symbol": "☶", "nature": "Sơn (Núi)",    "element": "Thổ"},
    (0, 0, 0): {"num_xt": 8, "name": "Khôn", "symbol": "☷", "nature": "Địa (Đất)",    "element": "Thổ"},
}

XT_NUM_TO_TRIGRAM = {v["num_xt"]: k for k, v in TRIGRAMS.items()}

# Nạp Giáp Kinh Phòng: (Nội quái 3 hào 1-2-3, Ngoại quái 3 hào 4-5-6) dưới dạng (stem_idx, branch_idx)
NAJIA_MAP: Dict[str, Tuple[List[Tuple[int, int]], List[Tuple[int, int]]]] = {
    "Càn":  ([(0, 0), (0, 2), (0, 4)],   [(8, 6), (8, 8), (8, 10)]),    # Nội Giáp Tý Dần Thìn | Ngoại Nhâm Ngọ Thân Tuất
    "Khôn": ([(1, 7), (1, 5), (1, 3)],   [(9, 1), (9, 11), (9, 9)]),    # Nội Ất Mùi Tỵ Mão | Ngoại Quý Sửu Hợi Dậu
    "Chấn": ([(6, 0), (6, 2), (6, 4)],   [(6, 6), (6, 8), (6, 10)]),    # Canh Tý Dần Thìn | Canh Ngọ Thân Tuất
    "Tốn":  ([(7, 1), (7, 11), (7, 9)],  [(7, 7), (7, 5), (7, 3)]),     # Tân Sửu Hợi Dậu | Tân Mùi Tỵ Mão
    "Khảm": ([(4, 2), (4, 4), (4, 6)],   [(4, 8), (4, 10), (4, 0)]),    # Mậu Dần Thìn Ngọ | Mậu Thân Tuất Tý
    "Ly":   ([(5, 3), (5, 1), (5, 11)],  [(5, 9), (5, 7), (5, 5)]),     # Kỷ Mão Sửu Hợi | Kỷ Dậu Mùi Tỵ
    "Cấn":  ([(2, 4), (2, 6), (2, 8)],   [(2, 10), (2, 0), (2, 2)]),    # Bính Thìn Ngọ Thân | Bính Tuất Tý Dần
    "Đoài": ([(3, 5), (3, 3), (3, 1)],   [(3, 11), (3, 9), (3, 7)]),    # Đinh Tỵ Mão Sửu | Đinh Hợi Dậu Mùi
}

# 64 Quẻ Chu Dịch ánh xạ từ (Thượng Quái, Hạ Quái) -> (Số Chu Dịch, Tên Hán-Việt, Lời khuyên cốt lõi)
HEXAGRAMS_64: Dict[Tuple[str, str], Tuple[int, str, str]] = {
    ("Càn", "Càn"):   (1,  "Thuần Càn", "Nguyên hanh lợi trinh — Cương kiện tự cường, thời vận sáng lớn nhưng tránh kiêu ngạo ở đỉnh cao."),
    ("Khôn", "Khôn"): (2,  "Thuần Khôn", "Hậu đức tải vật — Nhu thuận bao dung, lấy tĩnh chế động, đi sau đắc lợi."),
    ("Khảm", "Chấn"): (3,  "Thủy Lôi Truân", "Vạn sự khởi đầu nan — Kiên nhẫn củng cố nền móng, tìm người trợ lực, chớ nóng vội xuất kích."),
    ("Cấn", "Khảm"):  (4,  "Sơn Thủy Mông", "Khai mở mông muội — Cần học hỏi chuyên gia, làm rõ thông tin mập mờ trước khi quyết."),
    ("Khảm", "Càn"):  (5,  "Thủy Thiên Nhu", "Ẩn nhẫn chờ thời — Có thực lực nhưng thời chưa thông, cứ bình tĩnh chuẩn bị chu đáo."),
    ("Càn", "Khảm"):  (6,  "Thiên Thủy Tụng", "Tranh chấp bất đồng — Đề phòng kiện tụng khẩu thiệt; biết dừng giữa chừng thì cát, cố thắng tới cùng ắt hung."),
    ("Khôn", "Khảm"): (7,  "Địa Thủy Sư", "Quân luật nghiêm minh — Tổ chức quy củ, dùng người dày dạn kinh nghiệm thống lĩnh mới thành."),
    ("Khảm", "Khôn"): (8,  "Thủy Địa Tỷ", "Thân phụ đoàn kết — Chọn bạn/đối tác chân thành để liên minh sớm, chần chừ sẽ lỡ hội."),
    ("Tốn", "Càn"):   (9,  "Phong Thiên Tiểu Súc", "Tích tiểu thành đại — Mây dày chưa mưa, tạm tích lũy nguồn lực và tinh chỉnh chi tiết."),
    ("Càn", "Đoài"):  (10, "Thiên Trạch Lý", "Dẫm đuôi hổ chẳng cắn — Đi trong vùng rủi ro nhưng giữ lễ độ, cẩn trọng quy trình thì bình an đắc chí."),
    ("Khôn", "Càn"):  (11, "Địa Thiên Thái", "Thiên địa giao hòa — Tiểu vãng đại lai, vận khí hanh thông, hợp tác cực kỳ thuận lợi."),
    ("Càn", "Khôn"):  (12, "Thiên Địa Bĩ", "Âm dương bế tắc — Trên dưới bất đồng, nên thu mình bảo toàn vốn liếng, tránh phô trương."),
    ("Càn", "Ly"):    (13, "Thiên Hỏa Đồng Nhân", "Đồng tâm hiệp lực — Mở rộng hợp tác công minh ngoài xã hội thì vượt được mọi sông lớn."),
    ("Ly", "Càn"):    (14, "Hỏa Thiên Đại Hữu", "Mặt trời giữa trời — Tài lộc và danh vị dồi dào, giữ đức khiêm nhu và ngăn ác dương thiện."),
    ("Khôn", "Cấn"):  (15, "Địa Sơn Khiêm", "Núi ẩn trong đất — Quẻ duy nhất 6 hào đều cát: Càng khiêm nhường thực chất càng thành tựu bền lâu."),
    ("Chấn", "Khôn"): (16, "Lôi Địa Dự", "Sấm vang mặt đất — Tinh thần phấn khởi, thuận lợi phát động kế hoạch nhưng tránh ngủ quên trên vui thú."),
    ("Đoài", "Chấn"): (17, "Trạch Lôi Tùy", "Thuận thời mà theo — Linh hoạt thích ứng xu thế và lắng nghe người tài, bỏ cái tôi cứng nhắc."),
    ("Cấn", "Tốn"):   (18, "Sơn Phong Cổ", "Chỉnh đốn cái mục nát — Đã đến lúc cải tổ triệt để tồn đọng cũ, trước sau cân nhắc 3 ngày."),
    ("Khôn", "Đoài"): (19, "Địa Trạch Lâm", "Dương khí đang lên — Cơ hội tiến gần, chủ động sâu sát thực tế và quản trị chu kỳ dài hạn."),
    ("Tốn", "Khôn"):  (20, "Phong Địa Quan", "Quan sát chiêm nghiệm — Nhìn tổng thể khách quan trước khi hành động, lấy uy tín làm gương."),
    ("Ly", "Chấn"):   (21, "Hỏa Lôi Phệ Hạp", "Cắn vỡ vật ngáng — Có chướng ngại ở giữa, phải dùng kỷ luật/pháp lý dứt khoát xử lý mới thông."),
    ("Cấn", "Ly"):    (22, "Sơn Hỏa Bí", "Văn sức thanh nhã — Lợi về truyền thông, hình ảnh, việc nhỏ; việc cốt lõi lớn không nên chỉ trọng bề ngoài."),
    ("Cấn", "Khôn"):  (23, "Sơn Địa Bác", "Bóc mòn suy thoái — Nền móng bị bào mòn, tuyệt đối không mạo hiểm đầu tư mới, ưu tiên giữ gốc."),
    ("Khôn", "Chấn"): (24, "Địa Lôi Phục", "Nhất dương lai phục — Sau bế tắc ánh sáng đã quay lại, phục hồi từng bước vững chắc."),
    ("Càn", "Chấn"):  (25, "Thiên Lôi Vô Vọng", "Chân thực không vọng động — Cứ làm đúng đạo lý tự nhiên, đừng mưu cầu may rủi ngoài tầm kiểm soát."),
    ("Cấn", "Càn"):   (26, "Sơn Thiên Đại Súc", "Tích lũy chí lớn — Nội lực dày, nuôi dưỡng hiền tài, sẵn sàng cho việc lớn vượt biển."),
    ("Cấn", "Chấn"):  (27, "Sơn Lôi Di", "Cẩn ngôn tiết ẩm — Chú ý lời ăn tiếng nói, sức khỏe và nguồn nuôi dưỡng tài chính chân chính."),
    ("Đoài", "Tốn"):  (28, "Trạch Phong Đại Quá", "Rường cột quá tải — Áp lực vượt ngưỡng bình thường, cần hành động phi thường nhưng phải có điểm tựa êm."),
    ("Khảm", "Khảm"): (29, "Thuần Khảm", "Trùng trùng hiểm trở — Giữ chữ Tín và bản lĩnh như dòng nước chảy bền bỉ xuyên qua khe vực."),
    ("Ly", "Ly"):     (30, "Thuần Ly", "Quang minh bám tựa — Sáng suốt rực rỡ nhưng cần bám vào nền tảng chính đạo để lửa cháy lâu."),
    ("Đoài", "Cấn"):  (31, "Trạch Sơn Hàm", "Cảm ứng tự nhiên — Chân thành tương cảm, cực tốt cho tình duyên, đàm phán thiện chí."),
    ("Chấn", "Tốn"):  (32, "Lôi Phong Hằng", "Bền bỉ lâu dài — Kiên định phương hướng cốt lõi, không dao động bởi biến động ngắn hạn."),
    ("Càn", "Cấn"):   (33, "Thiên Sơn Độn", "Rút lui chiến lược — Biết thoái đúng lúc khi thế bất lợi mới là bậc trí giả bảo toàn đại cục."),
    ("Chấn", "Càn"):  (34, "Lôi Thiên Đại Tráng", "Khí thế hùng mạnh — Đang lúc thịnh vượng nhưng chớ dùng sức càn lướt, giữ chính trực mới bền."),
    ("Ly", "Khôn"):   (35, "Hỏa Địa Tấn", "Mặt trời mọc trên đất — Thăng tiến sáng rõ, được cấp trên ghi nhận và ban thưởng."),
    ("Khôn", "Ly"):   (36, "Địa Hỏa Minh Di", "Ánh sáng ẩn dưới đất — Giấu tài giữ mình (nội minh ngoại nhu) để vượt qua môi trường khắc nghiệt."),
    ("Tốn", "Ly"):    (37, "Phong Hỏa Gia Nhân", "ề nếp gia đạo/nội bộ — Ổn định quản trị nội bộ và gia đình trước thì việc ngoài tự thành."),
    ("Ly", "Đoài"):   (38, "Hỏa Trạch Khuê", "Khác biệt chia rẽ — Quan điểm trái chiều, tìm điểm chung trong dị biệt, lợi việc nhỏ hơn việc lớn."),
    ("Khảm", "Cấn"):  (39, "Thủy Sơn Kiển", "Trước mặt có hiểm — Tạm dừng xem xét lại hướng đi, quay về củng cố nội lực và tìm quý nhân."),
    ("Chấn", "Khảm"): (40, "Lôi Thủy Giải", "Mưa sấm giải hạn — Khó khăn được tháo gỡ; việc cần làm hãy giải quyết nhanh gọn dứt điểm."),
    ("Cấn", "Đoài"):  (41, "Sơn Trạch Tổn", "Bớt dưới thêm trên — Chấp nhận cắt giảm chi phí/thiệt thòi ngắn hạn để đổi lấy giá trị bền vững về sau."),
    ("Tốn", "Chấn"):  (42, "Phong Lôi Ích", "Gió sấm tương trợ — Thời điểm vàng để dấn thân đầu tư, mở rộng quy mô và giúp người lợi mình."),
    ("Đoài", "Càn"):  (43, "Trạch Thiên Quải", "Quyết đoán dứt khoát — Xử lý dứt điểm mầm họa nhỏ còn sót bằng sự minh bạch, không dùng bạo lực."),
    ("Càn", "Tốn"):   (44, "Thiên Phong Cấu", "Gặp gỡ bất ngờ — Có cơ duyên đột xuất nhưng cảnh giác yếu tố ngầm phát sinh khó kiểm soát."),
    ("Đoài", "Khôn"): (45, "Trạch Địa Tụy", "Tụ hội tinh hoa — Nhân tài và nguồn lực quy tụ, thuận lợi tổ chức sự kiện lớn nhưng cần dự phòng rủi ro."),
    ("Khôn", "Tốn"):  (46, "Địa Phong Thăng", "Cây mọc từ đất — Từng bước vươn cao vững chắc, gặp bậc đại nhân nâng đỡ tiến xa."),
    ("Đoài", "Khảm"): (47, "Trạch Thủy Khốn", "Đầm cạn hết nước — Giai đoạn thử thách bản lĩnh; nói nhiều không ai tin, chỉ hành động kiên cường mới thông."),
    ("Khảm", "Tốn"):  (48, "Thủy Phong Tỉnh", "Giếng nước nuôi người — Nguồn giá trị cốt lõi không đổi, hãy nâng cấp công cụ khai thác ('gàu & dây')."),
    ("Đoài", "Ly"):   (49, "Trạch Hỏa Cách", "Cải cách lột xác — Thay cũ đổi mới đúng thời điểm thì được mọi người tin phục, hối tiếc tiêu tan."),
    ("Ly", "Tốn"):    (50, "Hỏa Phong Đỉnh", "Vạc vàng luyện đan — Đại cát về định vị thương hiệu, thăng hoa trí tuệ, hợp tác tam giác vững chãi."),
    ("Chấn", "Chấn"): (51, "Thuần Chấn", "Sấm sét chấn động — Biến cố bất ngờ gây giật mình nhưng giữ bình tĩnh tự tỉnh thì 'cười nói như thường'."),
    ("Cấn", "Cấn"):   (52, "Thuần Cấn", "Núi đứng vững chãi — Biết dừng đúng giới hạn, tĩnh tâm định trí, không vọng tưởng ngoài vị trí."),
    ("Tốn", "Cấn"):   (53, "Phong Sơn Tiệm", "Cây lớn trên núi — Tuần tự tiệm tiến đúng quy trình, chậm mà cực kỳ chắc chắn (đại cát hôn nhân & sự nghiệp)."),
    ("Chấn", "Đoài"): (54, "Lôi Trạch Quy Muội", "Vội vàng lệch vị — Đề phòng cảm tính nhất thời hoặc vị thế phụ thuộc thiếu bền vững."),
    ("Chấn", "Ly"):   (55, "Lôi Hỏa Phong", "Thịnh đạt đỉnh cao — Quy mô rực rỡ như mặt trời giữa trưa, cần hành động ngay khi đang vượng."),
    ("Ly", "Cấn"):    (56, "Hỏa Sơn Lữ", "Lữ khách phương xa — Thuận cho công tác, dịch chuyển, việc ngắn hạn; thận trọng pháp lý nơi đất khách."),
    ("Tốn", "Tốn"):   (57, "Thuần Tốn", "Gió luồn thấm sâu — Mềm mỏng linh hoạt, kiên trì thuyết phục và bám sát người dẫn đường uy tín."),
    ("Đoài", "Đoài"): (58, "Thuần Đoài", "Đầm vui hòa duyệt — Đàm phán giao tiếp vui vẻ đắc lợi, nhưng giữ nguyên tắc không xu nịnh."),
    ("Tốn", "Khảm"):  (59, "Phong Thủy Hoán", "Gió thổi tan băng — Giải tỏa hiểu lầm, khơi thông dòng tiền/tắc nghẽn và liên kết tầm nhìn lớn."),
    ("Khảm", "Đoài"): (60, "Thủy Trạch Tiết", "Tiết chế chừng mực — Đặt ra kỷ luật chi tiêu & ranh giới hợp lý; tiết chế quá khổ lại phản tác dụng."),
    ("Tốn", "Đoài"):  (61, "Phong Trạch Trung Phu", "Chí thành cảm hóa — Lòng tin chân thật thấu tới tận cùng, đại lợi hợp tác và hóa giải nghi kỵ."),
    ("Chấn", "Cấn"):  (62, "Lôi Sơn Tiểu Quá", "Chim nhỏ bay thấp — Nên làm việc vừa sức, tỉ mỉ khiêm tốn; chưa phải lúc mưu đại sự vượt tầm."),
    ("Khảm", "Ly"):   (63, "Thủy Hỏa Ký Tế", "Việc đã hoàn thành — Đầu xuôi nhưng phải giữ đuôi lọt, phòng ngừa chủ quan sau khi đạt mục tiêu."),
    ("Ly", "Khảm"):   (64, "Hỏa Thủy Vị Tế", "Trước ngưỡng thành công — Còn bước cuối qua sông, thận trọng từng chi tiết thì tương lai mở rộng vô cùng."),
}

ELEMENTS_CYCLE = ["Mộc", "Hỏa", "Thổ", "Kim", "Thủy"]


def liuqin_name(palace_element: str, line_element: str) -> str:
    """Tính Lục Thân từ Ngũ hành Cung Bát Thuần và Ngũ hành Địa Chi Hào."""
    p_i = ELEMENTS_CYCLE.index(palace_element)
    l_i = ELEMENTS_CYCLE.index(line_element)
    diff = (l_i - p_i) % 5
    if diff == 0:
        return "Huynh Đệ"
    elif diff == 1:
        return "Tử Tôn"
    elif diff == 2:
        return "Thê Tài"
    elif diff == 3:
        return "Quan Quỷ"
    else:
        return "Phụ Mẫu"


def find_palace_and_shi_ying(lower_bits: Tuple[int, int, int], upper_bits: Tuple[int, int, int]) -> Tuple[str, int, int, str]:
    """
    Thuật toán Bát Cung Kinh Phòng xác định:
    - Quẻ thuộc Cung nào (Càn, Khôn, Chấn, Tốn, Khảm, Ly, Cấn, Đoài)
    - Vị trí Hào Thế (1..6) & Hào Ứng (1..6)
    - Thứ bậc quẻ trong cung (Bát Thuần, Nhất Thế..Ngũ Thế, Du Hồn, Quy Hồn)
    """
    b = list(lower_bits) + list(upper_bits)  # b[0]..b[5]

    def eq3(x: List[int], y: List[int]) -> bool:
        return x[0] == y[0] and x[1] == y[1] and x[2] == y[2]

    def inv3(x: List[int]) -> List[int]:
        return [1 - v for v in x]

    low, up = b[:3], b[3:]
    # 1. Bát Thuần: Thượng == Hạ -> Thế hào 6
    if eq3(low, up):
        p_name = str(TRIGRAMS[tuple(up)]["name"])
        return p_name, 6, 3, "Bát Thuần (Lục Xung)"

    # Thử biến lần lượt từ Bát Thuần gốc của mỗi cung để tìm chính xác 100% không bao giờ lệch!
    for root_bits, trig_info in TRIGRAMS.items():
        cur = list(root_bits) + list(root_bits)
        p_name = str(trig_info["name"])
        # Nhất thế -> Ngũ thế (biến hào 1..5)
        stage_names = ["Nhất Thế", "Nhị Thế", "Tam Thế", "Tứ Thế", "Ngũ Thế"]
        for idx_line in range(5):
            cur[idx_line] = 1 - cur[idx_line]
            if cur == b:
                shi = idx_line + 1
                ying = ((shi + 2) % 6) + 1
                return p_name, shi, ying, stage_names[idx_line]
        # Du Hồn: lật ngược hào 4 (index 3) -> Thế ở hào 4
        cur[3] = 1 - cur[3]
        if cur == b:
            return p_name, 4, 1, "Du Hồn"
        # Quy Hồn: lật ngược cả 3 hào nội quái (index 0, 1, 2) -> Thế ở hào 3
        cur[0] = 1 - cur[0]
        cur[1] = 1 - cur[1]
        cur[2] = 1 - cur[2]
        if cur == b:
            return p_name, 3, 6, "Quy Hồn"

    return "Càn", 6, 3, "Bát Thuần"


def six_beasts_for_day_stem(day_stem: int) -> List[str]:
    """An Lục Thần từ hào 1 lên hào 6 theo Can Ngày."""
    beasts = ["Thanh Long", "Chu Tước", "Câu Trần", "Đằng Xà", "Bạch Hổ", "Huyền Vũ"]
    if day_stem in (0, 1):      # Giáp Ất khởi Thanh Long
        start = 0
    elif day_stem in (2, 3):    # Bính Đinh khởi Chu Tước
        start = 1
    elif day_stem == 4:         # Mậu khởi Câu Trần
        start = 2
    elif day_stem == 5:         # Kỷ khởi Đằng Xà
        start = 3
    elif day_stem in (6, 7):    # Canh Tân khởi Bạch Hổ
        start = 4
    else:                       # Nhâm Quý khởi Huyền Vũ
        start = 5
    return [beasts[(start + i) % 6] for i in range(6)]


def cast_iching_full(
    dt_cast: datetime,
    method: str = "coins_random",  # "coins_random" | "manual_lines" | "numbers" | "time"
    manual_lines: Optional[List[int]] = None,  # 6 giá trị thuộc {6, 7, 8, 9} từ hào 1 -> hào 6
    numbers: Optional[List[int]] = None,
    question: str = "",
    tz_hours: float = 7.0,
) -> Dict[str, object]:
    """
    Lập quẻ Kinh Dịch tích hợp cả 3 tầng: Lục Hào Nạp Giáp + Mai Hoa Dịch Số + Chu Dịch 64 Quẻ.
    Giá trị hào chuẩn:
      6 = Lão Âm (---x---, Âm động biến Dương)
      7 = Thiếu Dương (-------, Dương tĩnh)
      8 = Thiếu Âm (--- ---, Âm tĩnh)
      9 = Lão Dương (---o---, Dương động biến Âm)
    """
    lunar = solar_to_lunar(dt_cast.day, dt_cast.month, dt_cast.year, tz_hours)
    solar_ctx = get_solar_term_context(dt_cast, tz_hours)
    jdn = jd_from_date(dt_cast.day, dt_cast.month, dt_cast.year)
    day_stem = (jdn + 9) % 10
    day_branch = (jdn + 1) % 12
    month_stem = int(solar_ctx["month_stem"])
    month_branch = int(solar_ctx["month_branch"])
    year_stem = int(solar_ctx["year_stem"])
    year_branch = int(solar_ctx["year_branch"])
    hour_branch = ((dt_cast.hour + 1) // 2) % 12
    hour_stem = ((day_stem % 5) * 2 + hour_branch) % 10
    tk_branches = tuan_khong_for_pillar(day_stem, day_branch)

    raw_lines: List[int] = []
    method_desc = ""

    if method == "manual_lines" and manual_lines and len(manual_lines) == 6:
        raw_lines = list(manual_lines)
        method_desc = f"Nhập trực tiếp 6 hào Lục Hào ({raw_lines})"
    elif method == "numbers" and numbers and len(numbers) >= 2:
        n1, n2 = abs(numbers[0]), abs(numbers[1])
        up_num = n1 % 8 or 8
        low_num = n2 % 8 or 8
        if len(numbers) >= 3:
            mov = abs(numbers[2]) % 6 or 6
        else:
            mov = (n1 + n2 + (hour_branch + 1)) % 6 or 6
        up_bits = XT_NUM_TO_TRIGRAM[up_num]
        low_bits = XT_NUM_TO_TRIGRAM[low_num]
        base_bits = list(low_bits) + list(up_bits)
        for i, bit in enumerate(base_bits):
            if (i + 1) == mov:
                raw_lines.append(9 if bit == 1 else 6)
            else:
                raw_lines.append(7 if bit == 1 else 8)
        method_desc = f"Mai Hoa Khởi Số ({numbers} -> Thượng {up_num}, Hạ {low_num}, Động hào {mov})"
    elif method == "time":
        y_num = ((lunar["year"] + 8) % 12) + 1  # Tý=1..Hợi=12
        m_num = lunar["month"]
        d_num = lunar["day"]
        h_num = hour_branch + 1
        up_num = (y_num + m_num + d_num) % 8 or 8
        low_num = (y_num + m_num + d_num + h_num) % 8 or 8
        mov = (y_num + m_num + d_num + h_num) % 6 or 6
        up_bits = XT_NUM_TO_TRIGRAM[up_num]
        low_bits = XT_NUM_TO_TRIGRAM[low_num]
        base_bits = list(low_bits) + list(up_bits)
        for i, bit in enumerate(base_bits):
            if (i + 1) == mov:
                raw_lines.append(9 if bit == 1 else 6)
            else:
                raw_lines.append(7 if bit == 1 else 8)
        method_desc = f"Mai Hoa Khởi Thời Gian Âm Lịch (Động hào {mov})"
    else:
        # Gieo 3 đồng xu chuẩn mật mã học (Mỗi đồng: Ngửa=3, Sấp=2 -> Tổng 6,7,8,9 đúng phân phối 1:3:3:1)
        for _ in range(6):
            coins = sum(3 if secrets.randbelow(2) == 1 else 2 for _ in range(3))
            raw_lines.append(coins)
        method_desc = f"Gieo 3 Đồng Xu Chuẩn Lục Hào ({raw_lines})"

    orig_bits = [1 if v in (7, 9) else 0 for v in raw_lines]
    changed_bits = [
        (0 if v == 9 else (1 if v == 6 else (1 if v == 7 else 0)))
        for v in raw_lines
    ]
    moving_indices = [i + 1 for i, v in enumerate(raw_lines) if v in (6, 9)]

    low_orig = tuple(orig_bits[:3])
    up_orig = tuple(orig_bits[3:])
    low_chg = tuple(changed_bits[:3])
    up_chg = tuple(changed_bits[3:])
    # Hổ Quái: Hạ Hổ = hào 2,3,4 (index 1,2,3); Thượng Hổ = hào 3,4,5 (index 2,3,4)
    low_hu = (orig_bits[1], orig_bits[2], orig_bits[3])
    up_hu = (orig_bits[2], orig_bits[3], orig_bits[4])

    low_orig_name = str(TRIGRAMS[low_orig]["name"])
    up_orig_name = str(TRIGRAMS[up_orig]["name"])
    low_chg_name = str(TRIGRAMS[low_chg]["name"])
    up_chg_name = str(TRIGRAMS[up_chg]["name"])
    low_hu_name = str(TRIGRAMS[low_hu]["name"])
    up_hu_name = str(TRIGRAMS[up_hu]["name"])

    hex_num, hex_name, hex_meaning = HEXAGRAMS_64[(up_orig_name, low_orig_name)]
    chg_num, chg_name, chg_meaning = HEXAGRAMS_64[(up_chg_name, low_chg_name)]
    hu_num, hu_name, _ = HEXAGRAMS_64[(up_hu_name, low_hu_name)]

    palace_name, shi_pos, ying_pos, palace_stage = find_palace_and_shi_ying(low_orig, up_orig)
    palace_elem = next(str(v["element"]) for v in TRIGRAMS.values() if v["name"] == palace_name)

    # Nạp Giáp cho Bản Quái, Biến Quái và Bát Thuần gốc (để tìm Phục Thần)
    orig_najia = NAJIA_MAP[low_orig_name][0] + NAJIA_MAP[up_orig_name][1]
    chg_najia = NAJIA_MAP[low_chg_name][0] + NAJIA_MAP[up_chg_name][1]
    pure_najia = NAJIA_MAP[palace_name][0] + NAJIA_MAP[palace_name][1]

    beasts = six_beasts_for_day_stem(day_stem)

    # Tiến thần / Thoái thần maps
    jin_shen = {(11, 0), (2, 3), (5, 6), (8, 9), (1, 4), (4, 7), (7, 10)}
    tui_shen = {(0, 11), (3, 2), (6, 5), (9, 8), (4, 1), (10, 7), (7, 4)}

    present_liuqin = set()
    lines_data = []
    for i in range(6):
        pos = i + 1
        val = raw_lines[i]
        is_moving = val in (6, 9)
        s_o, b_o = orig_najia[i]
        s_c, b_c = chg_najia[i]
        b_elem = BRANCH_ELEMENTS[b_o]
        lq = liuqin_name(palace_elem, b_elem)
        present_liuqin.add(lq)

        flags = []
        if b_o in tk_branches:
            flags.append("Tuần Không")
        if abs(b_o - month_branch) == 6:
            flags.append("Nguyệt Phá")
        if b_o == month_branch:
            flags.append("Lâm Nguyệt Kiến")
        if b_o == day_branch:
            flags.append("Lâm Nhật Thần")
        elif abs(b_o - day_branch) == 6:
            # Xét Vượng Tướng theo tháng để phân biệt Ám Động vs Nhật Phá
            m_elem = BRANCH_ELEMENTS[month_branch]
            m_idx = ELEMENTS_CYCLE.index(m_elem)
            l_idx = ELEMENTS_CYCLE.index(b_elem)
            is_prosperous = ((l_idx - m_idx) % 5) in (0, 1)
            if not is_moving:
                flags.append("Ám Động" if is_prosperous else "Nhật Phá")
            else:
                flags.append("Nhật Xung")

        change_note = None
        if is_moving:
            c_elem = BRANCH_ELEMENTS[b_c]
            c_lq = liuqin_name(palace_elem, c_elem)
            o_i = ELEMENTS_CYCLE.index(b_elem)
            c_i = ELEMENTS_CYCLE.index(c_elem)
            rel_tags = []
            if (b_o, b_c) in jin_shen:
                rel_tags.append("Hóa Tiến Thần")
            if (b_o, b_c) in tui_shen:
                rel_tags.append("Hóa Thoái Thần")
            if (o_i - c_i) % 5 == 1:
                rel_tags.append("Hồi Đầu Sinh")
            elif (o_i - c_i) % 5 == 2:
                rel_tags.append("Hồi Đầu Khắc")
            if abs(b_o - b_c) == 6:
                rel_tags.append("Phản Ngâm Hào")
            if b_c in tk_branches:
                rel_tags.append("Hóa Không")
            change_note = {
                "changed_can_chi": can_chi_name(s_c, b_c),
                "changed_element": c_elem,
                "changed_liuqin": c_lq,
                "tags": rel_tags,
            }

        symbol_str = {
            6: "---x--- (Lão Âm động)",
            7: "------- (Thiếu Dương)",
            8: "--- --- (Thiếu Âm)",
            9: "---o--- (Lão Dương động)",
        }[val]

        lines_data.append({
            "position": pos,
            "raw_value": val,
            "symbol": symbol_str,
            "is_yang": orig_bits[i] == 1,
            "is_moving": is_moving,
            "shi_ying": "Thế" if pos == shi_pos else ("Ứng" if pos == ying_pos else ""),
            "beast": beasts[i],
            "liuqin": lq,
            "can_chi": can_chi_name(s_o, b_o),
            "branch": BRANCHES_VI[b_o],
            "element": b_elem,
            "status_flags": flags,
            "changed_to": change_note,
            "fushen": None,
        })

    # Bổ sung Phục Thần cho các Lục Thân bị khuyết trên Bản Quái
    all_liuqin = {"Phụ Mẫu", "Huynh Đệ", "Tử Tôn", "Thê Tài", "Quan Quỷ"}
    missing_liuqin = all_liuqin - present_liuqin
    if missing_liuqin:
        for i in range(6):
            ps, pb = pure_najia[i]
            pe = BRANCH_ELEMENTS[pb]
            plq = liuqin_name(palace_elem, pe)
            if plq in missing_liuqin:
                lines_data[i]["fushen"] = f"{plq} {can_chi_name(ps, pb)} ({pe})"

    # Phân tích Mai Hoa Thể – Dụng (nếu có 1 hào động, hoặc tổng quát Thượng/Hạ)
    meihua_analysis = None
    if len(moving_indices) == 1:
        mov_pos = moving_indices[0]
        if mov_pos <= 3:
            ti_name, ti_elem = up_orig_name, str(TRIGRAMS[up_orig]["element"])
            yong_name, yong_elem = low_orig_name, str(TRIGRAMS[low_orig]["element"])
            ti_pos_label = "Thượng Quái"
        else:
            ti_name, ti_elem = low_orig_name, str(TRIGRAMS[low_orig]["element"])
            yong_name, yong_elem = up_orig_name, str(TRIGRAMS[up_orig]["element"])
            ti_pos_label = "Hạ Quái"

        t_i = ELEMENTS_CYCLE.index(ti_elem)
        y_i = ELEMENTS_CYCLE.index(yong_elem)
        diff = (y_i - t_i) % 5
        if diff == 0:
            verdict = "Thể Dụng Tỷ Hòa (Cát — Thuận lợi, đồng lòng hợp sức)"
        elif diff == 4:
            verdict = "Dụng Sinh Thể (Đại Cát — Việc tự thành, đắc lợi dễ dàng)"
        elif diff == 2:
            verdict = "Thể Khắc Dụng (Trung Cát — Làm chủ được việc nhưng cần bỏ công sức)"
        elif diff == 1:
            verdict = "Thể Sinh Dụng (Tiểu Hung — Hao tổn tâm sức/tiền bạc sinh xuất ra ngoài)"
        else:
            verdict = "Dụng Khắc Thể (Hung — Ngoại cảnh cản trở mạnh, nên thận trọng/tạm hoãn)"

        meihua_analysis = {
            "ti_gua": f"{ti_name} ({ti_elem}) [{ti_pos_label}]",
            "yong_gua": f"{yong_name} ({yong_elem})",
            "relation_verdict": verdict,
        }

    return {
        "question": question,
        "cast_method": method_desc,
        "cast_time": dt_cast.strftime("%Y-%m-%d %H:%M"),
        "pillars_at_cast": {
            "year": can_chi_name(year_stem, year_branch),
            "month": can_chi_name(month_stem, month_branch) + " (Nguyệt Kiến: " + BRANCHES_VI[month_branch] + ")",
            "day": can_chi_name(day_stem, day_branch) + " (Nhật Thần: " + BRANCHES_VI[day_branch] + ")",
            "hour": can_chi_name(hour_stem, hour_branch),
            "tuan_khong": f"{BRANCHES_VI[tk_branches[0]]} – {BRANCHES_VI[tk_branches[1]]}",
        },
        "primary_hexagram": {
            "number": hex_num,
            "name": hex_name,
            "upper_trigram": f"{up_orig_name} {TRIGRAMS[up_orig]['symbol']} ({TRIGRAMS[up_orig]['element']})",
            "lower_trigram": f"{low_orig_name} {TRIGRAMS[low_orig]['symbol']} ({TRIGRAMS[low_orig]['element']})",
            "palace": f"Cung {palace_name} ({palace_elem}) — {palace_stage}",
            "core_meaning": hex_meaning,
        },
        "mutual_hexagram": {"number": hu_num, "name": hu_name},
        "changed_hexagram": {
            "number": chg_num,
            "name": chg_name,
            "core_meaning": chg_meaning,
        } if moving_indices else None,
        "moving_lines": moving_indices,
        "missing_liuqin": sorted(list(missing_liuqin)),
        "lines_bottom_to_top": lines_data,
        "meihua_ti_yong": meihua_analysis,
    }


# ==============================================================================
# KỲ MÔN ĐỘN GIÁP THỜI GIA (Sách Bổ Pháp - Chai Bu, Chuyển Bàn Cửu Cung)
# ==============================================================================
# Bảng Cục Số (Thượng, Trung, Hạ nguyên) cho 24 Tiết Khí: (is_yang_dun, (thuong, trung, ha))
QIMEN_JU_TABLE: Dict[int, Tuple[bool, Tuple[int, int, int]]] = {
    270: (True,  (1, 7, 4)),  # Đông Chí
    285: (True,  (2, 8, 5)),  # Tiểu Hàn
    300: (True,  (3, 9, 6)),  # Đại Hàn
    315: (True,  (8, 5, 2)),  # Lập Xuân
    330: (True,  (9, 6, 3)),  # Vũ Thủy
    345: (True,  (1, 7, 4)),  # Kinh Trập
    0:   (True,  (3, 9, 6)),  # Xuân Phân
    15:  (True,  (4, 1, 7)),  # Thanh Minh
    30:  (True,  (5, 2, 8)),  # Cốc Vũ
    45:  (True,  (4, 1, 7)),  # Lập Hạ
    60:  (True,  (5, 2, 8)),  # Tiểu Mãn
    75:  (True,  (6, 3, 9)),  # Mang Chủng
    90:  (False, (9, 3, 6)),  # Hạ Chí
    105: (False, (8, 2, 5)),  # Tiểu Thử
    120: (False, (7, 1, 4)),  # Đại Thử
    135: (False, (2, 5, 8)),  # Lập Thu
    150: (False, (1, 4, 7)),  # Xử Thử
    165: (False, (9, 3, 6)),  # Bạch Lộ
    180: (False, (7, 1, 4)),  # Thu Phân
    195: (False, (6, 9, 3)),  # Hàn Lộ
    210: (False, (5, 8, 2)),  # Sương Giáng
    225: (False, (6, 9, 3)),  # Lập Đông
    240: (False, (5, 8, 2)),  # Tiểu Tuyết
    255: (False, (4, 7, 1)),  # Đại Tuyết
}

RING_PALACES = [1, 8, 3, 4, 9, 2, 7, 6]  # Chiều thuận kim đồng hồ quanh 8 cung ngoại vi Lạc Thư
PALACE_META = {
    1: ("Khảm 1", "Bắc", "Thủy"),
    2: ("Khôn 2", "Tây Nam", "Thổ"),
    3: ("Chấn 3", "Đông", "Mộc"),
    4: ("Tốn 4", "Đông Nam", "Mộc"),
    5: ("Trung 5 (Gửi Khôn 2)", "Trung Ương", "Thổ"),
    6: ("Càn 6", "Tây Bắc", "Kim"),
    7: ("Đoài 7", "Tây", "Kim"),
    8: ("Cấn 8", "Đông Bắc", "Thổ"),
    9: ("Ly 9", "Nam", "Hỏa"),
}
NINE_STARS_ORIG = {
    1: "Thiên Bồng", 8: "Thiên Nhậm", 3: "Thiên Xung", 4: "Thiên Phụ",
    9: "Thiên Anh", 2: "Thiên Nhuế", 7: "Thiên Trụ", 6: "Thiên Tâm", 5: "Thiên Cầm"
}
EIGHT_DOORS_ORIG = {
    1: "Hưu Môn", 8: "Sinh Môn", 3: "Thương Môn", 4: "Đỗ Môn",
    9: "Cảnh Môn", 2: "Tử Môn", 7: "Kinh Môn", 6: "Khai Môn"
}
EIGHT_GODS = ["Trực Phù", "Đằng Xà", "Thái Âm", "Lục Hợp", "Bạch Hổ", "Huyền Vũ", "Cửu Địa", "Cửu Thiên"]
SANQI_LIUYI = ["Mậu", "Kỷ", "Canh", "Tân", "Nhâm", "Quý", "Đinh", "Bính", "Ất"]


def compute_qimen_hourly(dt_cast: datetime, tz_hours: float = 7.0) -> Dict[str, object]:
    """Lập bàn Kỳ Môn Độn Giáp Thời Gia (Chuyển Bàn - Sách Bổ Pháp)."""
    solar_ctx = get_solar_term_context(dt_cast, tz_hours)
    sun_deg = float(solar_ctx["sun_longitude_deg"])
    term_deg = (int(sun_deg // 15) * 15) % 360
    is_yang, (ju_up, ju_mid, ju_low) = QIMEN_JU_TABLE[term_deg]

    jdn = jd_from_date(dt_cast.day, dt_cast.month, dt_cast.year)
    day_s = (jdn + 9) % 10
    day_b = (jdn + 1) % 12
    # Tìm chỉ số 0..59 của ngày trong 60 Hoa Giáp
    day_gz = next(idx for idx in range(60) if idx % 10 == day_s and idx % 12 == day_b)
    # Sách Bổ: Tìm Phù Đầu (Giáp Tý=0, Kỷ Mão=15, Giáp Ngọ=30, Kỷ Dậu=45, v.v. -> mỗi nguyên 5 ngày = 60 giờ -> idx // 5 % 3)
    yuan_idx = (day_gz // 5) % 3
    yuan_name = ["Thượng Nguyên", "Trung Nguyên", "Hạ Nguyên"][yuan_idx]
    ju_num = [ju_up, ju_mid, ju_low][yuan_idx]

    hour_b = ((dt_cast.hour + 1) // 2) % 12
    hour_s = ((day_s % 5) * 2 + hour_b) % 10
    hour_gz = next(idx for idx in range(60) if idx % 10 == hour_s and idx % 12 == hour_b)

    # Tuần Thủ của giờ hiện tại (0=Giáp Tý->Mậu, 10=Giáp Tuất->Kỷ, 20=Giáp Thân->Canh, 30=Giáp Ngọ->Tân, 40=Giáp Thìn->Nhâm, 50=Giáp Dần->Quý)
    xun_ord = hour_gz // 10
    xun_leader_yi = ["Mậu", "Kỷ", "Canh", "Tân", "Nhâm", "Quý"][xun_ord]
    xun_names = ["Giáp Tý (Mậu)", "Giáp Tuất (Kỷ)", "Giáp Thân (Canh)", "Giáp Ngọ (Tân)", "Giáp Thìn (Nhâm)", "Giáp Dần (Quý)"]
    steps_from_xun = hour_gz % 10  # Số canh giờ tính từ đầu Tuần Giáp

    # An Địa Bàn Tam Kỳ Lục Nghi (Dương Độn đi thuận 1->2->3..9, Âm Độn đi nghịch 9->8..1)
    earth_plate: Dict[int, str] = {}
    for k, stem_yi in enumerate(SANQI_LIUYI):
        p = ((ju_num - 1 + (k if is_yang else -k)) % 9) + 1
        earth_plate[p] = stem_yi

    # Cung gốc của Tuần Thủ (nếu rơi Trung 5 thì gửi sang Khôn 2)
    orig_leader_palace = next(p for p, st in earth_plate.items() if st == xun_leader_yi)
    eff_leader_palace = 2 if orig_leader_palace == 5 else orig_leader_palace

    zhifu_star = NINE_STARS_ORIG[orig_leader_palace]
    zhishi_door = EIGHT_DOORS_ORIG[eff_leader_palace]

    # Hào Can giờ hiện tại (nếu giờ Giáp -> ẩn dưới Lục Nghi Tuần Thủ)
    target_hour_stem_vi = xun_leader_yi if hour_s == 0 else STEMS_VI[hour_s]
    zhifu_target_palace = next(p for p, st in earth_plate.items() if st == target_hour_stem_vi)
    eff_zhifu_target = 2 if zhifu_target_palace == 5 else zhifu_target_palace

    # Xoay Cửu Tinh (Thiên Bàn) + Thiên Bàn Can theo Trực Phù tới eff_zhifu_target
    orig_ring_idx = RING_PALACES.index(eff_leader_palace)
    dest_ring_idx = RING_PALACES.index(eff_zhifu_target)
    star_shift = (dest_ring_idx - orig_ring_idx) % 8

    heaven_stars: Dict[int, str] = {}
    heaven_stems: Dict[int, str] = {}
    for idx_r, p in enumerate(RING_PALACES):
        src_p = RING_PALACES[(idx_r - star_shift) % 8]
        star_label = NINE_STARS_ORIG[src_p]
        stem_label = earth_plate[src_p]
        if src_p == 2:
            star_label += " (+Thiên Cầm)"
            stem_label += f"/{earth_plate[5]}"
        heaven_stars[p] = star_label
        heaven_stems[p] = stem_label

    # Phi cung Trực Sử (Nhân Bàn Bát Môn): từ orig_leader_palace đếm theo số cung Lạc Thư (Dương thuận, Âm nghịch)
    door_dest_raw = ((orig_leader_palace - 1 + (steps_from_xun if is_yang else -steps_from_xun)) % 9) + 1
    eff_door_dest = 2 if door_dest_raw == 5 else door_dest_raw
    door_shift = (RING_PALACES.index(eff_door_dest) - RING_PALACES.index(eff_leader_palace)) % 8

    doors_plate: Dict[int, str] = {}
    for idx_r, p in enumerate(RING_PALACES):
        src_p = RING_PALACES[(idx_r - door_shift) % 8]
        doors_plate[p] = EIGHT_DOORS_ORIG[src_p]

    # An Bát Thần: từ eff_zhifu_target đi thuận kim đồng hồ (Dương Độn) hoặc nghịch kim đồng hồ (Âm Độn)
    gods_plate: Dict[int, str] = {}
    for k, god_name in enumerate(EIGHT_GODS):
        r_idx = (dest_ring_idx + (k if is_yang else -k)) % 8
        gods_plate[RING_PALACES[r_idx]] = god_name

    palaces_out = []
    for p in [4, 9, 2, 3, 5, 7, 8, 1, 6]:  # Thứ tự hiển thị Cửu Cung chuẩn (Đông Nam - Nam - Tây Nam...)
        p_title, p_dir, p_elem = PALACE_META[p]
        if p == 5:
            palaces_out.append({
                "palace": p,
                "name": p_title,
                "direction": p_dir,
                "earth_stem": earth_plate[5],
                "note": "Ký gửi sang Cung Khôn 2",
            })
        else:
            palaces_out.append({
                "palace": p,
                "name": p_title,
                "direction": p_dir,
                "element": p_elem,
                "god": gods_plate[p],
                "star": heaven_stars[p],
                "door": doors_plate[p],
                "heaven_stem": heaven_stems[p],
                "earth_stem": earth_plate[p],
            })

    return {
        "dun_type": f"{'Dương Độn' if is_yang else 'Âm Độn'} {ju_num} Cục ({yuan_name})",
        "solar_term": solar_ctx["current_solar_term"],
        "hour_pillar": can_chi_name(hour_s, hour_b),
        "xun_shou": xun_names[xun_ord],
        "zhifu_star": f"{zhifu_star} (lạc cung {PALACE_META[eff_zhifu_target][0]} — {PALACE_META[eff_zhifu_target][1]})",
        "zhishi_door": f"{zhishi_door} (lạc cung {PALACE_META[eff_door_dest][0]} — {PALACE_META[eff_door_dest][1]})",
        "palaces": palaces_out,
    }
