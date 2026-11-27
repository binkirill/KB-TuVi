# -*- coding: utf-8 -*-
"""
engine_numerology.py — Engine Thần Số Học Đa Phái Chuẩn Zero-Hallucination (kb-tuvi v3.0)
Kết tinh tinh hoa từ các kho mã nguồn hàng đầu:
  - @nhatnguyet/than-so-hoc & vietanhdev/thansohoc : Chuẩn hóa dấu tiếng Việt NFD, phân loại động chữ Y, Nhân số học VN (giữ số 10, 11, 22/4)
  - compuuteio/numerology & evoluteur              : Hệ 20+ chỉ số Pythagoras quốc tế (Tam giác vàng, Trưởng thành, Thái độ, Cầu nối, Tiềm thức, 4 Bình diện)
  - LanderTome/numerologyCalculator & dakidarts    : Hệ Chaldean cổ đại (1..8 + Số Kép Huyền Bí 10..52) & Chấm điểm Tên gọi / Thương hiệu
  - lexterror/Pythagorean-Numerology-Calculator    : Biểu đồ Ngày sinh & Tổ hợp 3x3, 8 Mũi tên Đầy, 7 Mũi tên Trống, Ốc đảo cô đơn, Kim tự tháp 4 Đỉnh cao
  - sanzol-tech/destiny-matrix                     : Cốt lõi Ma trận Định mệnh (22 Arcana Core Octagram)

0 pip dependencies — tương thích Python 3.8+, sẵn sàng nhúng trực tiếp vào FastAPI / Flask / Django / CLI.
"""

from __future__ import annotations
import re
import unicodedata
from datetime import date, datetime
from typing import Any, Dict, List, Optional, Set, Tuple

# Bảng ánh xạ chữ cái Pythagoras (1..9)
PYTHAGOREAN_MAP: Dict[str, int] = {
    "A": 1, "J": 1, "S": 1,
    "B": 2, "K": 2, "T": 2,
    "C": 3, "L": 3, "U": 3,
    "D": 4, "M": 4, "V": 4,
    "E": 5, "N": 5, "W": 5,
    "F": 6, "O": 6, "X": 6,
    "G": 7, "P": 7, "Y": 7,
    "H": 8, "Q": 8, "Z": 8,
    "I": 9, "R": 9,
}

# Bảng ánh xạ rung động âm thanh Chaldean cổ đại (1..8, số 9 linh thiêng không gán chữ cái)
CHALDEAN_MAP: Dict[str, int] = {
    "A": 1, "I": 1, "J": 1, "Q": 1, "Y": 1,
    "B": 2, "K": 2, "R": 2,
    "C": 3, "G": 3, "L": 3, "S": 3,
    "D": 4, "M": 4, "T": 4,
    "E": 5, "H": 5, "N": 5, "X": 5,
    "U": 6, "V": 6, "W": 6,
    "O": 7, "Z": 7,
    "F": 8, "P": 8,
}

CORE_VOWELS: Set[str] = {"A", "E", "I", "O", "U"}
KARMIC_DEBT_NUMBERS: Dict[int, Dict[str, str]] = {
    13: {
        "code": "13/4",
        "title": "Nợ nghiệp 13/4 — Kỷ luật & Lao động chân chính",
        "lesson": "Tránh tâm lý đường tắt, trì hoãn hoặc bỏ cuộc giữa chừng; thành tựu bền vững đến từ sự tập trung, quy trình hóa và kiên trì từng bước.",
    },
    14: {
        "code": "14/5",
        "title": "Nợ nghiệp 14/5 — Tự do trong Chừng mực",
        "lesson": "Làm chủ cảm xúc và giác quan, tránh cả thèm chóng chán hoặc phân tán năng lượng; giữ cam kết dài hạn sẽ biến sự linh hoạt thành bứt phá lớn.",
    },
    16: {
        "code": "16/7",
        "title": "Nợ nghiệp 16/7 — Chuyển hóa Bản ngã & Thức tỉnh Nội tâm",
        "lesson": "Học sự khiêm nhường, lắng nghe sâu và xây dựng đời sống tinh thần vững chãi; mọi biến cố tái cấu trúc đều giúp gột rửa cái tôi để đạt trí tuệ cao hơn.",
    },
    19: {
        "code": "19/1",
        "title": "Nợ nghiệp 19/1 — Độc lập nhưng Biết Đón Nhận",
        "lesson": "Tự lực tự cường nhưng không độc đoán hay cô lập bản thân; học cách lắng nghe, chia sẻ quyền lực và hợp tác chân thành với tập thể.",
    },
}

# Ý nghĩa cốt lõi các con số chủ đạo & chỉ số nền tảng (hiển thị nhanh trên Web UI)
NUMBER_ARCHETYPES: Dict[str, Dict[str, Any]] = {
    "1": {
        "title": "Người Tiên Phong Độc Lập",
        "keywords": ["Lãnh đạo", "Bản lĩnh", "Độc lập", "Khởi xướng"],
        "element_affinity": ["Mộc", "Kim"],
        "strengths": "Tư duy quyết đoán, dám mở đường mới, tự chủ cao, có tố chất đứng mũi chịu sào.",
        "growth": "Cần rèn sự lắng nghe, kiềm chế cái tôi nóng vội và học cách trao quyền cho đồng đội.",
        "careers": "Quản trị điều hành, khởi nghiệp, công nghệ, chiến lược, kỹ sư trưởng, tư vấn độc lập.",
    },
    "2": {
        "title": "Người Hòa Giải & Kết Nối",
        "keywords": ["Thấu cảm", "Ngoại giao", "Tinh tế", "Hợp tác"],
        "element_affinity": ["Thủy", "Mộc"],
        "strengths": "Trực giác nhạy bén, giàu lòng trắc ẩn, giỏi lắng nghe và gắn kết tập thể êm thấm.",
        "growth": "Tránh cả nể, phụ thuộc cảm xúc hoặc suy nghĩ quá nhiều gây thiếu quyết đoán.",
        "careers": "Ngoại giao, nhân sự, tâm lý, chăm sóc khách hàng, cố vấn hậu phương, nghệ thuật.",
    },
    "3": {
        "title": "Người Truyền Cảm Hứng Sáng Tạo",
        "keywords": ["Ngôn từ", "Sáng tạo", "Lạc quan", "Biểu đạt"],
        "element_affinity": ["Hỏa", "Mộc"],
        "strengths": "Hoạt ngôn, tư duy linh hoạt, óc thẩm mỹ và khả năng khuấy động năng lượng tích cực.",
        "growth": "Cần kỷ luật quản lý tài chính và tập trung hoàn tất mục tiêu thay vì hứng khởi nhất thời.",
        "careers": "Truyền thông, giảng dạy, sáng tạo nội dung, marketing, thiết kế, diễn thuyết.",
    },
    "4": {
        "title": "Người Kiến Tạo Hệ Thống",
        "keywords": ["Kỷ luật", "Thực tế", "Chuẩn mực", "Bền bỉ"],
        "element_affinity": ["Thổ", "Kim"],
        "strengths": "Đáng tin cậy, tỉ mỉ, giỏi lập kế hoạch, xây nền móng quy trình và quản trị rủi ro.",
        "growth": "Tránh bảo thủ, cứng nhắc hoặc ôm đồm công việc quá mức quên chăm sóc cảm xúc.",
        "careers": "Tài chính - kế toán, kỹ thuật, xây dựng, vận hành hệ thống, pháp chế, kiểm toán.",
    },
    "5": {
        "title": "Người Tự Do & Đổi Mới",
        "keywords": ["Linh hoạt", "Đa tài", "Khám phá", "Thích nghi"],
        "element_affinity": ["Thủy", "Hỏa"],
        "strengths": "Nhạy bén với xu hướng mới, xoay xở cực nhanh, yêu tự do trải nghiệm và giao thương rộng.",
        "growth": "Cần neo giữ kỷ luật cốt lõi, tránh đứng núi này trông núi nọ hoặc quyết định bốc đồng.",
        "careers": "Thương mại quốc tế, du lịch, bán hàng, truyền thông số, đổi mới sản phẩm, đầu tư.",
    },
    "6": {
        "title": "Người Chăm Sóc & Phụng Sự",
        "keywords": ["Trách nhiệm", "Yêu thương", "Thẩm mỹ", "Gia đình"],
        "element_affinity": ["Thổ", "Hỏa"],
        "strengths": "Giàu tình thương, chu đáo, có gu thẩm mỹ hài hòa, luôn bảo vệ gia đình và cộng đồng.",
        "growth": "Tránh cầu toàn kiểm soát hoặc hy sinh quá mức dẫn tới kiệt sức và tủi thân ngầm.",
        "careers": "Giáo dục, y tế - trị liệu, thiết kế nội thất/thời trang, dịch vụ cao cấp, quản trị nhân văn.",
    },
    "7": {
        "title": "Nhà Triết Lý & Phân Tích Chuyên Sâu",
        "keywords": ["Trí tuệ", "Chiêm nghiệm", "Trực giác", "Chuyên gia"],
        "element_affinity": ["Kim", "Thủy"],
        "strengths": "Tư duy phân tích sắc sảo, không chấp nhận hời hợt, tự học xuất sắc qua trải nghiệm thực tế.",
        "growth": "Tránh khép kín, đa nghi thái quá hoặc xa rời đời sống giao tiếp ấm áp thường ngày.",
        "careers": "Nghiên cứu khoa học, dữ liệu/AI, chiến lược, y khoa chuyên sâu, luật, triết học - tâm thức.",
    },
    "8": {
        "title": "Nhà Điều Hành & Làm Chủ Vật Chất",
        "keywords": ["Tài chính", "Quyền lực", "Thực chiến", "Quy mô lớn"],
        "element_affinity": ["Kim", "Thổ"],
        "strengths": "Nhạy bén thương trường, bản lĩnh tổ chức lớn, tư duy hiệu suất và cân bằng nhân - quả.",
        "growth": "Cân bằng giữa tham vọng vật chất với đời sống tinh thần, giữ sự minh bạch và lòng biết ơn.",
        "careers": "Tài chính - ngân hàng, đầu tư, bất động sản, CEO/quản lý cấp cao, kinh doanh quy mô lớn.",
    },
    "9": {
        "title": "Người Gieo Hạt Nhân Văn",
        "keywords": ["Lý tưởng", "Bao dung", "Phụng sự", "Tầm nhìn rộng"],
        "element_affinity": ["Hỏa", "Thổ"],
        "strengths": "Trái tim rộng mở, giàu hoài bão cống hiến cho cộng đồng, có sức hút tinh thần tự nhiên.",
        "growth": "Học cách buông bỏ quá khứ, đặt ranh giới thực tế để không bị lợi dụng lòng tốt.",
        "careers": "Giáo dục, hoạt động xã hội, y dược, nghệ thuật truyền cảm hứng, lãnh đạo cộng đồng.",
    },
    "10": {
        "title": "Người Thích Nghi Linh Hoạt & Tiềm Năng Lãnh Đạo (Nhân Số Học VN)",
        "keywords": ["Quảng giao", "Thích nghi", "Bản lĩnh", "Tự tin"],
        "element_affinity": ["Hỏa", "Mộc"],
        "strengths": "Dễ hòa nhập mọi môi trường, vui vẻ phóng khoáng khi thuận lợi và có sức bật tiên phong của số 1.",
        "growth": "Tránh sống an phận trôi theo dòng nước (khía cạnh số 0 thụ động); cần xác lập mục tiêu rõ ràng.",
        "careers": "Kinh doanh dịch vụ, đối ngoại, thương mại, thiết kế, quản lý dự án đa ngành.",
    },
    "11/2": {
        "title": "Bậc Thầy Trực Giác & Khai Sáng Tâm Thức (Master 11/2)",
        "keywords": ["Trực giác cao", "Truyền cảm hứng", "Tâm linh", "Tinh tế"],
        "element_affinity": ["Thủy", "Hỏa"],
        "strengths": "Nhạy cảm siêu việt, khả năng thấu thị bản chất con người và dẫn dắt tinh thần đầy thuyết phục.",
        "growth": "Làm chủ hệ thần kinh nhạy cảm, giữ chân chạm đất bằng kỷ luật thực tế thay vì mơ mộng cực đoan.",
        "careers": "Khai vấn (Coaching), giáo dục khai phóng, tâm lý trị liệu, nghệ thuật, cố vấn chiến lược.",
    },
    "22/4": {
        "title": "Kiến Trúc Sư Đại Tài (Master 22/4)",
        "keywords": ["Tầm nhìn lớn", "Thực thi mạnh", "Di sản", "Tổ chức"],
        "element_affinity": ["Thổ", "Kim"],
        "strengths": "Kết hợp trực giác vĩ mô của 11 với kỷ luật thép của 4 — biến những ý tưởng lớn thành công trình thực tế.",
        "growth": "Vượt qua nỗi sợ thất bại hoặc áp lực tự đặt quá nặng; kiên nhẫn xây dựng từng viên gạch nền.",
        "careers": "Kiến tạo hạ tầng/công nghệ lớn, quản trị tập đoàn, hoạch định chính sách, giáo dục hệ thống.",
    },
    "33/6": {
        "title": "Người Chữa Lành & Dẫn Dắt Bằng Tình Thương (Master 33/6)",
        "keywords": ["Vị tha", "Chữa lành", "Giáo dưỡng", "Nâng đỡ"],
        "element_affinity": ["Hỏa", "Thổ"],
        "strengths": "Tần số từ bi và trách nhiệm cộng đồng rất cao, lan tỏa sự bình an và nâng đỡ tinh thần tập thể.",
        "growth": "Chăm sóc chính mình trước khi cứu giúp người khác; tránh gánh thay bài học nhân quả của người thân.",
        "careers": "Y đức, giáo dục nhân bản, từ thiện xã hội, trị liệu tâm thể, nghệ thuật chữa lành.",
    },
}

# Giải nghĩa Số Kép Huyền Bí Chaldean (10..52) — Dùng chấm điểm Tên Gọi / Nghệ Danh / Thương Hiệu
CHALDEAN_COMPOUNDS: Dict[int, Tuple[str, str, str]] = {
    10: ("Bánh Xe Vận Mệnh", "Cát", "Danh dự, tự tin và cơ hội vươn lên thuận lợi theo chu kỳ mới."),
    11: ("Sư Tử Ẩn Mình", "Cảnh báo", "Có sức mạnh ngầm nhưng dễ gặp mâu thuẫn nội tâm hoặc thử thách bất ngờ cần tỉnh táo."),
    12: ("Sự Hy Sinh", "Thận trọng", "Hay lo nghĩ gánh vác thay người khác, cần giữ ranh giới tài chính & cảm xúc rõ ràng."),
    13: ("Tái Sinh & Đổi Mới", "Trung tính", "Năng lượng biến đổi mạnh mẽ; thành công khi dám đổi mới triệt để và làm việc kỷ luật."),
    14: ("Dòng Chảy Giao Thương", "Khá Cát", "Thuận lợi truyền thông, dòng tiền lưu chuyển nhanh, hợp kinh doanh đại chúng."),
    15: ("Từ Trường Thu Hút", "Đại Cát", "Có duyên ăn nói, sức hút cá nhân lớn, dễ nhận tài lộc và sự ủng hộ từ quý nhân."),
    16: ("Tòa Tháp Thức Tỉnh", "Thận trọng", "Cảnh báo sự chủ quan; cần xây dựng kế hoạch phòng thủ vững vàng và sống khiêm tốn."),
    17: ("Ngôi Sao Bất Tử", "Đại Cát", "Biểu tượng bình an, trí tuệ vượt nghịch cảnh và để lại uy tín lâu bền."),
    18: ("Thử Thách Lý Trí", "Thận trọng", "Dễ vướng tranh chấp hoặc nóng nảy; hợp rèn luyện kỷ luật và tránh kiện tụng."),
    19: ("Hoàng Tử Thiên Đình", "Đại Cát", "Một trong những số tên đẹp nhất: thành tựu rực rỡ, danh tiếng và hạnh phúc viên mãn."),
    20: ("Sự Thức Tỉnh", "Khá Cát", "Mở ra sứ mệnh tinh thần và bước ngoặt giác ngộ ở nửa sau cuộc đời."),
    21: ("Vương Miện Vinh Quang", "Đại Cát", "Vượt qua thử thách đầu đời để đạt địa vị cao, uy quyền và thành công bền vững."),
    22: ("Ảo Ảnh & Cẩn Trọng", "Thận trọng", "Tránh cả tin người ngoài hoặc đặt mục tiêu thiếu thực tế; cần cố vấn tỉnh táo."),
    23: ("Ngôi Sao Hoàng Gia Sư Tử", "Thượng Cát", "Con số bảo trợ thượng hạng: quý nhân nâng đỡ từ cấp cao, cực vượng sự nghiệp & thương hiệu."),
    24: ("Tình Yêu & Thịnh Vượng", "Đại Cát", "Thuận lợi cả tài chính lẫn nhân duyên, được người khác phái và đối tác ưu ái hỗ trợ."),
    25: ("Trí Tuệ Qua Trải Nghiệm", "Khá Cát", "Càng va chạm thực tế càng sắc sảo, thành đạt vững chắc từ trung vận trở đi."),
    26: ("Cẩn Trọng Liên Danh", "Thận trọng", "Khi hùn hạp đầu tư cần hợp đồng chặt chẽ, tự chủ quyết định tài chính."),
    27: ("Quyền Trượng Lãnh Đạo", "Đại Cát", "Trí tuệ sáng tạo đi đôi quyền lực điều hành, rất hợp người làm chuyên môn cao & quản lý."),
    28: ("Tiềm Năng Kèm Ràng Buộc", "Trung tính", "Năng lực giỏi nhưng cần quản lý pháp lý chặt để giữ thành quả không phải làm lại từ đầu."),
    29: ("Thử Thách Cảm Xúc", "Thận trọng", "Nội tâm dễ dao động trước sóng gió nhân tình; cần điểm tựa tinh thần vững vàng."),
    30: ("Nhà Tư Tưởng Độc Lập", "Trung tính", "Trí tuệ vượt trội, thích hợp nghiên cứu học thuật hơn là bon chen danh lợi bề nổi."),
    31: ("Người Tự Lập Trầm Lặng", "Trung tính", "Năng lực chuyên môn sâu sắc nhưng hơi khép kín, cần chủ động mở rộng kết nối."),
    32: ("Truyền Thông Vạn Dặm", "Đại Cát", "Cùng dải kỳ diệu với 14 & 23: cực tốt cho thương hiệu đại chúng, mạng lưới quốc tế."),
    33: ("Phúc Khí Viên Mãn", "Đại Cát", "Tương đồng 24: thu hút tài lộc, bình an gia đạo và uy tín bền lâu."),
    34: ("Trưởng Thành Qua Rèn Luyện", "Khá Cát", "Tương đồng 25: nghị lực bền bỉ biến kinh nghiệm xương máu thành vị thế chuyên gia."),
    36: ("Tài Trí Thực Chiến", "Khá Cát", "Tự thân lập nghiệp thành công, càng đi xa quê hoặc mở rộng thị trường càng phát."),
    37: ("Tình Hữu Nghị Hoàng Kim", "Thượng Cát", "Cực kỳ may mắn trong đối tác, hôn nhân, khách hàng trung thành và nhân duyên tốt lành."),
    41: ("Từ Trường Thịnh Vượng", "Đại Cát", "Năng lượng thu hút cơ hội và danh tiếng rực rỡ giống dải 14 - 23 - 32."),
    42: ("Hài Hòa & Sung Túc", "Đại Cát", "Mang năng lượng cát tường của 24: thuận buồm xuôi gió về tài sản và thẩm mỹ."),
    45: ("Danh Tiếng & Trí Lực", "Đại Cát", "Đắc lợi nhờ trí tuệ tổ chức bài bản và uy tín chuyên môn."),
    46: ("Hợp Tác Đắc Lộc", "Đại Cát", "Thuận lợi nhân duyên và kết minh chiến lược giống 37."),
    50: ("Giải Phóng Trí Tuệ", "Đại Cát", "Mở rộng tầm nhìn lớn, thuận lợi giáo dục, xuất bản và phát triển đường dài."),
    51: ("Chiến Tướng Khai Mở", "Khá Cát", "Khí thế bứt phá mạnh mẽ, hợp dẫn đầu thị trường cạnh tranh cao."),
}

# 8 Mũi Tên Đầy & 7 Mũi Tên Trống trên Biểu Đồ Ngày Sinh 3x3 (Bố cục Pythagoras: 3-6-9 / 2-5-8 / 1-4-7)
ARROWS_DEFINITIONS: List[Tuple[Tuple[int, int, int], str, str, str, str]] = [
    (
        (1, 2, 3),
        "Mũi tên Kế Hoạch (1-2-3)",
        "Có tư duy tổ chức, làm việc có trình tự, tầm nhìn chiến lược rõ ràng.",
        "Mũi tên Hỗn Độ (Trống 1-2-3)",
        "Hay làm việc theo cảm hứng, cần rèn thói quen viết checklist và lập kế hoạch tuần.",
    ),
    (
        (4, 5, 6),
        "Mũi tên Ý Chí (4-5-6)",
        "Nghị lực phi thường, kiên định vượt nghịch cảnh hiếm ai sánh kịp.",
        "Mũi tên Nhạy Cảm / Dễ Nản (Trống 4-5-6)",
        "Dễ thất vọng khi kỳ vọng không như ý; cần học chấp nhận thực tại và chia nhỏ mục tiêu để hoàn thành.",
    ),
    (
        (7, 8, 9),
        "Mũi tên Hoạt Động (7-8-9)",
        "Ưa hành động thực tiễn, yêu trải nghiệm ngoài đời thực và dấn thân mạnh mẽ.",
        "Mũi tên Thụ Động / Trì Hoãn (Trống 7-8-9)",
        "Hay suy nghĩ nhiều trước khi bắt tay làm; cần đặt deadline hành động cụ thể mỗi ngày.",
    ),
    (
        (1, 4, 7),
        "Mũi tên Thực Tế (1-4-7)",
        "Khéo léo, thực tiễn, nắm bắt công việc chân tay và quản trị vật chất chắc chắn.",
        "Mũi tên Thiếu Thực Tế (Trống 1-4-7)",
        "Giàu ý tưởng nhưng đôi khi thiếu tính khả thi vật chất; cần gắn mọi dự án với bảng số liệu & ngân sách thực.",
    ),
    (
        (2, 5, 8),
        "Mũi tên Cân Bằng Cảm Xúc (2-5-8)",
        "Đời sống nội tâm sâu sắc, điềm tĩnh và thấu cảm tinh tế với người xung quanh.",
        "Mũi tên Nhạy Cảm Nội Tâm (Trống 2-5-8)",
        "Dễ tổn thương ngầm nhưng hay giấu kín; cần tập chia sẻ cảm xúc cởi mở và kết nối thiên nhiên.",
    ),
    (
        (3, 6, 9),
        "Mũi tên Trí Nhớ & Sáng Tạo (3-6-9)",
        "Trí tuệ sắc bén, tư duy học thuật nhanh nhạy và giàu sáng kiến.",
        "Mũi tên Đãng Trí Ngắn Hạn (Trống 3-6-9)",
        "Cần duy trì việc đọc sách, ghi chép hệ thống và rèn trí não thường xuyên.",
    ),
    (
        (1, 5, 9),
        "Mũi tên Quyết Tâm (1-5-9)",
        "Đã nhắm mục tiêu là theo đuổi bền bỉ tới cùng, sức bật sự nghiệp rất lớn.",
        "Mũi tên Trì Hoãn Quyết Định (Trống 1-5-9)",
        "Hay chần chừ khởi sự hoặc làm dở dang; cần rèn kỷ luật 'đã bắt đầu là dứt điểm'.",
    ),
    (
        (3, 5, 7),
        "Mũi tên Tâm Linh / Nhạy Bén (3-5-7)",
        "Trực giác tâm thức sâu sắc, thích tự trải nghiệm để đúc kết triết lý sống riêng.",
        "Mũi tên Hoài Nghi Thực Chứng (Trống 3-5-7)",
        "Chỉ tin khi có bằng chứng khoa học rõ ràng; nên kết hợp thêm lắng nghe trực giác và thiền định tĩnh tâm.",
    ),
]

# Chu kỳ 9 Năm Cá Nhân (Personal Year 1..9)
PERSONAL_YEAR_MEANINGS: Dict[int, Dict[str, str]] = {
    1: {"phase": "Gieo Hạt & Khởi Đầu Mới", "advice": "Mở hướng đi mới, học kỹ năng mới, chủ động độc lập đặt nền móng cho chu kỳ 9 năm."},
    2: {"phase": "Kết Nối & Ươm Mầm", "advice": "Kiên nhẫn bồi đắp quan hệ đối tác, lắng nghe trực giác, không nóng vội ép chín sớm."},
    3: {"phase": "Mở Rộng & Tỏa Sáng", "advice": "Đẩy mạnh học hỏi, giao tiếp, marketing bản thân và sáng tạo; kiểm soát chi tiêu cảm xúc."},
    4: {"phase": "Củng Cố Nền Tảng & Kỷ Luật", "advice": "Năm trũng kỹ thuật số 1: tập trung chuyên môn sâu, chuẩn hóa quy trình, chăm sóc sức khỏe, hạn chế đầu cơ mạo hiểm."},
    5: {"phase": "Bứt Phá & Chuyển Dịch", "advice": "Đón nhận thay đổi tích cực, mở rộng thị trường, đi xa hoặc nâng cấp mô hình công việc."},
    6: {"phase": "Gia Đình, Trách Nhiệm & Giá Trị", "advice": "Chăm chút tổ ấm, uy tín thương hiệu, các mối quan hệ cốt lõi và sự hài hòa nội tâm."},
    7: {"phase": "Chiêm Nghiệm & Nâng Cấp Nội Lực", "advice": "Năm trũng kỹ thuật số 2: lùi một bước để học sâu, nghiên cứu chiến lược, tĩnh tâm và sàng lọc nhận thức, tránh mở rộng ồ ạt."},
    8: {"phase": "Thu Hoạch Tài Chính & Quyền Lực", "advice": "Đỉnh sóng gặt hái vật chất và vị thế từ những gì đã gieo ở năm 1-6; quyết đoán thương thảo lớn."},
    9: {"phase": "Hoàn Tất, Thanh Lọc & Chuyển Giao", "advice": "Khép lại dự án/mối quan hệ cũ không còn phù hợp, cho đi giá trị nhân văn và dọn chỗ đón chu kỳ Năm số 1 kế tiếp."},
}

ARCANA_22_TITLES: Dict[int, str] = {
    1: "Nhà Kiến Tạo (The Magician) — Tiên phong & Ý chí khởi nguyên",
    2: "Nữ Tư Tế (High Priestess) — Trực giác, Hòa hợp & Thấu suốt",
    3: "Nữ Hoàng (The Empress) — Trù phú, Sáng tạo & Nuôi dưỡng",
    4: "Hoàng Đế (The Emperor) — Quyền uy, Trật tự & Trách nhiệm",
    5: "Giáo Hoàng (The Hierophant) — Tri thức chuẩn mực & Truyền thừa",
    6: "Tình Nhân (The Lovers) — Kết nối, Lựa chọn từ Trái tim & Thẩm mỹ",
    7: "Chiến Xa (The Chariot) — Tốc độ, Mục tiêu & Chinh phục",
    8: "Công Lý (Justice) — Nhân quả minh bạch & Cân bằng pháp độ",
    9: "Ẩn Sĩ (The Hermit) — Trí tuệ sâu lắng & Tự chiêm nghiệm",
    10: "Bánh Xe Số Phận (Wheel of Fortune) — Dòng chảy may mắn & Thuận thời",
    11: "Sức Mạnh (Strength) — Nội lực bền bỉ & Làm chủ bản năng",
    12: "Góc Nhìn Mới (Hanged Man) — Phụng sự vị tha & Tư duy đột phá",
    13: "Chuyển Hóa (Transformation) — Khép cũ mở mới, Tái cấu trúc mạnh mẽ",
    14: "Tiết Độ (Temperance) — Điềm tĩnh chữa lành, Nghệ thuật & Trung dung",
    15: "Thử Thách Hấp Dẫn (Manifestation) — Khí chất thu hút & Vượt cám dỗ vật chất",
    16: "Thức Tỉnh Tâm Thức (Tower) — Đập bỏ giới hạn cũ, Xây dựng lại bền vững",
    17: "Ngôi Sao Hy Vọng (The Star) — Tài năng tỏa sáng & Truyền cảm hứng",
    18: "Ánh Trăng (The Moon) — Tưởng tượng phong phú & Vượt qua nỗi sợ vô hình",
    19: "Mặt Trời (The Sun) — Thịnh vượng, Rạng rỡ, Hào sảng & Lãnh đạo",
    20: "Tiếng Gọi Gia Tộc (Judgement) — Thức tỉnh sứ mệnh & Chữa lành cội nguồn",
    21: "Thế Giới (The World) — Mở rộng toàn cầu, Tự do không biên giới",
    22: "Người Tự Do Thuần Khiết (The Fool) — Khởi đầu vô cực, Tin tưởng hành trình",
}


def strip_vn_accents(text: str) -> str:
    """Chuẩn hóa họ tên tiếng Việt về chữ cái Latin in hoa A-Z (NFD + Đ->D)."""
    if not text:
        return ""
    s = text.replace("Đ", "D").replace("đ", "d")
    s = unicodedata.normalize("NFD", s)
    s = "".join(ch for ch in s if unicodedata.category(ch) != "Mn")
    return s.upper()


def tokenize_clean_words(text: str) -> List[str]:
    """Tách chuỗi họ tên thành danh sách các từ chỉ chứa A-Z."""
    clean = strip_vn_accents(text)
    return re.findall(r"[A-Z]+", clean)


def classify_word_letters(word: str, y_mode: str = "contextual") -> List[Dict[str, Any]]:
    """
    Phân loại từng chữ cái trong 1 từ thành Nguyên âm ('V') hay Phụ âm ('C').
    Quy tắc 'contextual' (chuẩn học thuật Pitago cho cả tiếng Việt & tiếng Anh):
      - A, E, I, O, U luôn là Nguyên âm ('V').
      - Chữ Y là Phụ âm ('C') khi đứng liền kề (trước hoặc sau) một nguyên âm A/E/I/O/U trong cùng âm tiết
        (VD: NGUYEN, QUYNH, YEN, DUY, MAY -> Y là Phụ âm).
      - Chữ Y là Nguyên âm ('V') khi đứng độc lập hoặc hai bên không có nguyên âm A/E/I/O/U
        (VD: Y, MY, LY, KY, THY, VY, LYNN -> Y là Nguyên âm).
    """
    res: List[Dict[str, Any]] = []
    n = len(word)
    for i, ch in enumerate(word):
        if ch in CORE_VOWELS:
            role = "V"
        elif ch == "Y":
            if y_mode == "always_vowel":
                role = "V"
            elif y_mode == "always_consonant":
                role = "C"
            else:
                prev_is_vowel = i > 0 and word[i - 1] in CORE_VOWELS
                next_is_vowel = i < n - 1 and word[i + 1] in CORE_VOWELS
                role = "C" if (prev_is_vowel or next_is_vowel) else "V"
        else:
            role = "C"
        res.append({
            "char": ch,
            "role": role,
            "pythagorean": PYTHAGOREAN_MAP.get(ch, 0),
            "chaldean": CHALDEAN_MAP.get(ch, 0),
        })
    return res


def sum_digits(n: int) -> int:
    return sum(int(d) for d in str(abs(n)))


def reduce_number(
    n: int,
    keep_masters: Tuple[int, ...] = (11, 22, 33),
    keep_ten: bool = False,
) -> Tuple[int, int, List[int], Optional[int]]:
    """
    Rút gọn số theo chuẩn Thần số học:
    Trả về: (display_num, base_digit_1_to_9, steps_list, karmic_debt_or_none)
      - display_num: giữ lại 11, 22, 33 (hoặc 10 nếu keep_ten=True cho Số Chủ Đạo Nhân số học VN).
      - base_digit: chữ số gốc 1..9 (VD: 11->2, 22->4, 33->6, 10->1).
      - steps_list: chuỗi từng bước cộng trung gian để minh bạch 100% trên Web UI.
      - karmic_debt: nếu đi qua 13, 14, 16, 19 thì ghi nhận số nợ nghiệp.
    """
    curr = abs(int(n))
    steps = [curr]
    karmic: Optional[int] = curr if curr in KARMIC_DEBT_NUMBERS else None

    while curr > 9:
        if curr in keep_masters:
            break
        if keep_ten and curr == 10:
            break
        curr = sum_digits(curr)
        steps.append(curr)
        if karmic is None and curr in KARMIC_DEBT_NUMBERS:
            karmic = curr

    display_num = curr
    base = curr
    while base > 9:
        base = sum_digits(base)

    return display_num, base, steps, karmic


def format_num_code(display_num: int, base_digit: int) -> str:
    if display_num in (11, 22, 33):
        return f"{display_num}/{base_digit}"
    return str(display_num)


def reduce_arcana_22(n: int) -> int:
    """Rút gọn số về miền 1..22 chuẩn Ma trận Định mệnh (Matrix of Destiny)."""
    curr = abs(int(n))
    if curr == 0:
        return 22
    while curr > 22:
        curr = sum_digits(curr)
    return curr if curr > 0 else 22


def _build_3x3_grid(digits: List[int]) -> Dict[str, Any]:
    """
    Xây dựng Ma trận 3x3 chuẩn Pythagoras:
      Hàng Trí não (Top)    : 3 | 6 | 9
      Hàng Tâm hồn (Middle) : 2 | 5 | 8
      Hàng Thể chất (Bottom): 1 | 4 | 7
    """
    counts: Dict[int, int] = {i: 0 for i in range(1, 10)}
    for d in digits:
        if 1 <= d <= 9:
            counts[d] += 1

    cells_rows = [
        [{"digit": d, "count": counts[d], "text": str(d) * counts[d]} for d in (3, 6, 9)],
        [{"digit": d, "count": counts[d], "text": str(d) * counts[d]} for d in (2, 5, 8)],
        [{"digit": d, "count": counts[d], "text": str(d) * counts[d]} for d in (1, 4, 7)],
    ]

    present_arrows = []
    empty_arrows = []
    for combo, full_name, full_desc, empty_name, empty_desc in ARROWS_DEFINITIONS:
        a, b, c = combo
        if counts[a] > 0 and counts[b] > 0 and counts[c] > 0:
            present_arrows.append({"digits": list(combo), "name": full_name, "meaning": full_desc})
        elif counts[a] == 0 and counts[b] == 0 and counts[c] == 0:
            empty_arrows.append({"digits": list(combo), "name": empty_name, "meaning": empty_desc})

    # Kiểm tra 4 ốc đảo cô đơn ở 4 góc (1, 3, 7, 9) bị cô lập khi các ô kề cạnh (2,4 / 2,6 / 4,8 / 6,8) và ô 5 đều trống
    isolated_corners = []
    corner_neighbors = {
        1: (2, 4, 5),
        3: (2, 6, 5),
        7: (4, 8, 5),
        9: (6, 8, 5),
    }
    for corner, neighs in corner_neighbors.items():
        if counts[corner] > 0 and all(counts[nb] == 0 for nb in neighs):
            isolated_corners.append(corner)

    excess_digits = [d for d in range(1, 10) if counts[d] >= 3]

    return {
        "counts": {str(k): v for k, v in counts.items()},
        "rows_top_to_bottom": cells_rows,
        "present_arrows": present_arrows,
        "empty_arrows": empty_arrows,
        "isolated_corners": isolated_corners,
        "excess_digits": excess_digits,
    }


def _compute_name_metrics(name_str: str, y_mode: str = "contextual") -> Dict[str, Any]:
    """Tính toàn bộ chỉ số Họ tên theo cả Pythagoras và Chaldean."""
    words = tokenize_clean_words(name_str)
    if not words:
        return {
            "has_name": False,
            "raw_input": name_str,
            "clean_name": "",
            "words": [],
        }

    word_details = []
    all_pyth_digits: List[int] = []
    vowel_word_bases: List[int] = []
    cons_word_bases: List[int] = []
    expr_word_bases: List[int] = []
    first_letters_sum = 0
    chaldean_total = 0
    karmic_hits: Dict[int, List[str]] = {}

    def record_karmic(kd: Optional[int], source_label: str) -> None:
        if kd is not None:
            karmic_hits.setdefault(kd, [])
            if source_label not in karmic_hits[kd]:
                karmic_hits[kd].append(source_label)

    for w in words:
        letters = classify_word_letters(w, y_mode=y_mode)
        w_total = sum(x["pythagorean"] for x in letters)
        w_vowel = sum(x["pythagorean"] for x in letters if x["role"] == "V")
        w_cons = sum(x["pythagorean"] for x in letters if x["role"] == "C")
        w_chaldean = sum(x["chaldean"] for x in letters)

        w_disp, w_base, w_steps, w_kd = reduce_number(w_total)
        v_disp, v_base, v_steps, v_kd = reduce_number(w_vowel) if w_vowel > 0 else (0, 0, [0], None)
        c_disp, c_base, c_steps, c_kd = reduce_number(w_cons) if w_cons > 0 else (0, 0, [0], None)

        expr_word_bases.append(w_disp)
        vowel_word_bases.append(v_disp)
        cons_word_bases.append(c_disp)
        first_letters_sum += letters[0]["pythagorean"]
        chaldean_total += w_chaldean

        for x in letters:
            all_pyth_digits.append(x["pythagorean"])

        word_details.append({
            "word": w,
            "letters": letters,
            "pythagorean_sum": w_total,
            "pythagorean_reduced": format_num_code(w_disp, w_base),
            "vowel_sum": w_vowel,
            "consonant_sum": w_cons,
            "chaldean_sum": w_chaldean,
        })

    # 1. Sứ Mệnh (Expression): Rút gọn từng từ rồi cộng tổng (chuẩn Hans Decoz), đồng thời kiểm tra cả tổng thô để không sót Nợ nghiệp
    raw_expr_sum = sum(all_pyth_digits)
    _, _, _, kd_expr_raw = reduce_number(raw_expr_sum)
    expr_disp, expr_base, expr_steps, kd_expr = reduce_number(sum(expr_word_bases))
    record_karmic(kd_expr or kd_expr_raw, "Số Sứ Mệnh (Họ tên)")

    # 2. Linh Hồn (Soul Urge)
    raw_soul_sum = sum(w["vowel_sum"] for w in word_details)
    _, _, _, kd_soul_raw = reduce_number(raw_soul_sum)
    soul_disp, soul_base, soul_steps, kd_soul = reduce_number(sum(vowel_word_bases))
    record_karmic(kd_soul or kd_soul_raw, "Số Linh Hồn (Nguyên âm)")

    # 3. Nhân Cách (Personality)
    raw_pers_sum = sum(w["consonant_sum"] for w in word_details)
    _, _, _, kd_pers_raw = reduce_number(raw_pers_sum)
    pers_disp, pers_base, pers_steps, kd_pers = reduce_number(sum(cons_word_bases))
    record_karmic(kd_pers or kd_pers_raw, "Số Nhân Cách (Phụ âm)")

    # 4. Cân Bằng (Balance Number — tổng các chữ cái đầu mỗi từ)
    bal_disp, bal_base, bal_steps, _ = reduce_number(first_letters_sum, keep_masters=(11, 22))

    # 5. Số Khuyết (Karmic Lessons) & Đam mê ẩn giấu (Hidden Passion)
    freq: Dict[int, int] = {i: 0 for i in range(1, 10)}
    for d in all_pyth_digits:
        freq[d] += 1
    missing_numbers = [d for d in range(1, 10) if freq[d] == 0]
    subconscious_self = 9 - len(missing_numbers)
    max_freq = max(freq.values()) if freq else 0
    hidden_passions = [d for d, cnt in freq.items() if cnt == max_freq and max_freq >= 2]

    # 6. Bốn Bình Diện Biểu Đạt (Planes of Expression)
    total_letters = max(1, len(all_pyth_digits))
    mental_cnt = freq[1] + freq[8]
    emotional_cnt = freq[2] + freq[3] + freq[6]
    physical_cnt = freq[4] + freq[5]
    intuitive_cnt = freq[7] + freq[9]

    # 7. Tên gọi chính (từ cuối cùng trong họ tên Việt Nam, VD "Nguyễn Văn An" -> "AN")
    given_name_word = word_details[-1]

    # 8. Chaldean Compound Analysis
    ch_disp, ch_base, ch_steps, _ = reduce_number(chaldean_total, keep_masters=())
    compound_info = CHALDEAN_COMPOUNDS.get(chaldean_total)
    if compound_info is None and chaldean_total > 52:
        # Nếu tổng > 52, tra cứu ở bước cộng đầu tiên
        sub_c = sum_digits(chaldean_total)
        compound_info = CHALDEAN_COMPOUNDS.get(sub_c)

    return {
        "has_name": True,
        "raw_input": name_str,
        "clean_name": " ".join(words),
        "given_name": given_name_word["word"],
        "given_name_sum": given_name_word["pythagorean_sum"],
        "words": word_details,
        "all_pythagorean_digits": all_pyth_digits,
        "expression": {
            "code": format_num_code(expr_disp, expr_base),
            "display": expr_disp,
            "base": expr_base,
            "raw_sum": raw_expr_sum,
            "steps": expr_steps,
            "archetype": NUMBER_ARCHETYPES.get(format_num_code(expr_disp, expr_base), NUMBER_ARCHETYPES[str(expr_base)]),
        },
        "soul_urge": {
            "code": format_num_code(soul_disp, soul_base),
            "display": soul_disp,
            "base": soul_base,
            "raw_sum": raw_soul_sum,
            "steps": soul_steps,
            "archetype": NUMBER_ARCHETYPES.get(format_num_code(soul_disp, soul_base), NUMBER_ARCHETYPES[str(soul_base)]),
        },
        "personality": {
            "code": format_num_code(pers_disp, pers_base),
            "display": pers_disp,
            "base": pers_base,
            "raw_sum": raw_pers_sum,
            "steps": pers_steps,
            "archetype": NUMBER_ARCHETYPES.get(format_num_code(pers_disp, pers_base), NUMBER_ARCHETYPES[str(pers_base)]),
        },
        "balance": {
            "code": format_num_code(bal_disp, bal_base),
            "display": bal_disp,
            "base": bal_base,
            "steps": bal_steps,
        },
        "bridge_soul_personality": abs(soul_base - pers_base),
        "karmic_lessons_missing": missing_numbers,
        "subconscious_self": subconscious_self,
        "hidden_passions": hidden_passions,
        "digit_frequency": {str(k): v for k, v in freq.items()},
        "planes_of_expression": {
            "mental_1_8": {"count": mental_cnt, "pct": round(mental_cnt * 100 / total_letters, 1)},
            "emotional_2_3_6": {"count": emotional_cnt, "pct": round(emotional_cnt * 100 / total_letters, 1)},
            "physical_4_5": {"count": physical_cnt, "pct": round(physical_cnt * 100 / total_letters, 1)},
            "intuitive_7_9": {"count": intuitive_cnt, "pct": round(intuitive_cnt * 100 / total_letters, 1)},
        },
        "chaldean": {
            "compound_number": chaldean_total,
            "single_digit": ch_base,
            "steps": ch_steps,
            "compound_title": compound_info[0] if compound_info else f"Rung động tổng hợp {chaldean_total}/{ch_base}",
            "compound_rank": compound_info[1] if compound_info else "Trung tính",
            "compound_meaning": compound_info[2] if compound_info else "Mang đặc tính căn bản của con số đơn sau khi rút gọn.",
        },
        "karmic_hits": karmic_hits,
    }


def compute_numerology_profile(
    birth_date_solar: str,
    full_name: str = "",
    nickname: str = "",
    target_year: Optional[int] = None,
    target_month: Optional[int] = None,
    target_day: Optional[int] = None,
    school: str = "vn",
    y_mode: str = "contextual",
) -> Dict[str, Any]:
    """
    Hàm trung tâm tính trọn bộ Hồ sơ Thần Số Học Đa Phái (Web-Ready JSON):
      - birth_date_solar: 'YYYY-MM-DD' (Luôn tính trên ngày sinh Dương lịch)
      - full_name       : Họ và tên khai sinh đầy đủ có dấu (VD: 'Nguyễn Văn An')
      - nickname        : Tên thường gọi / Nghệ danh / Tên thương hiệu muốn chấm điểm (tùy chọn)
      - school          : 'vn' (Nhân số học Việt Nam — giữ Số Chủ Đạo 10, 11, 22/4) | 'intl' (Pythagoras Quốc tế — 3 trụ bảo toàn 11/2, 22/4, 33/6)
      - y_mode          : 'contextual' (chuẩn học thuật chữ Y linh hoạt) | 'always_vowel' | 'always_consonant'
    """
    now = datetime.now()
    t_year = int(target_year or now.year)
    t_month = int(target_month or now.month)
    t_day = int(target_day or now.day)

    parts = [int(x) for x in birth_date_solar.strip().split("-")]
    by, bm, bd = parts[0], parts[1], parts[2]
    b_date = date(by, bm, bd)

    karmic_registry: Dict[int, List[str]] = {}

    def add_karmic(kd: Optional[int], label: str) -> None:
        if kd is not None:
            karmic_registry.setdefault(kd, [])
            if label not in karmic_registry[kd]:
                karmic_registry[kd].append(label)

    # 1. Tính Số Chủ Đạo / Đường Đời theo CẢ 2 TRƯỜNG PHÁI để minh bạch tuyệt đối
    # (A) Chuẩn Quốc tế (3-Component Reduction: Rút gọn Năm + Rút gọn Tháng + Rút gọn Ngày)
    y_disp, y_base, y_steps, y_kd = reduce_number(sum_digits(by))
    m_disp, m_base, m_steps, m_kd = reduce_number(bm)
    d_disp, d_base, d_steps, d_kd = reduce_number(bd)
    add_karmic(d_kd, f"Ngày sinh ({bd})")

    intl_sum = y_disp + m_disp + d_disp
    lp_intl_disp, lp_intl_base, lp_intl_steps, lp_intl_kd = reduce_number(intl_sum, keep_masters=(11, 22, 33))
    add_karmic(lp_intl_kd, "Đường Đời (Chuẩn Quốc tế)")

    # (B) Chuẩn Nhân số học Việt Nam (David Phillips / Lê Đỗ Quỳnh Hương: Cộng tổng mọi chữ số YYYYMMDD, giữ 10, 11, 22/4)
    all_birth_digits = [int(c) for c in f"{by:04d}{bm:02d}{bd:02d}"]
    vn_raw_sum = sum(all_birth_digits)
    lp_vn_disp, lp_vn_base, lp_vn_steps, lp_vn_kd = reduce_number(
        vn_raw_sum, keep_masters=(11, 22, 33), keep_ten=True
    )
    add_karmic(lp_vn_kd, "Số Chủ Đạo (Tổng chữ số ngày sinh)")

    use_vn = (school == "vn")
    lp_disp = lp_vn_disp if use_vn else lp_intl_disp
    lp_base = lp_vn_base if use_vn else lp_intl_base
    lp_code = "10" if (use_vn and lp_disp == 10) else format_num_code(lp_disp, lp_base)
    lp_intl_code = format_num_code(lp_intl_disp, lp_intl_base)
    lp_vn_code = "10" if lp_vn_disp == 10 else format_num_code(lp_vn_disp, lp_vn_base)

    # 2. Chỉ số Ngày Sinh (Birthday) & Thái Độ (Attitude = Ngày + Tháng)
    att_disp, att_base, att_steps, att_kd = reduce_number(bd + bm, keep_masters=(11, 22))
    add_karmic(att_kd, "Số Thái Độ (Ngày + Tháng)")

    # 3. Phân tích Họ Tên Khai Sinh & Tên Thường Gọi / Nghệ Danh
    name_data = _compute_name_metrics(full_name, y_mode=y_mode)
    for kd_num, srcs in name_data.get("karmic_hits", {}).items():
        for s in srcs:
            add_karmic(kd_num, s)

    nick_data = _compute_name_metrics(nickname, y_mode=y_mode) if nickname.strip() else None

    # 4. Chỉ số Trưởng Thành (Maturity), Tư Duy Hợp Lý (Rational Thought) & Cầu Nối Đường Đời - Sứ Mệnh
    maturity_obj = None
    rational_obj = None
    bridge_lp_expr = None
    if name_data.get("has_name"):
        expr_disp = name_data["expression"]["display"]
        expr_base = name_data["expression"]["base"]
        mat_disp, mat_base, mat_steps, mat_kd = reduce_number(lp_base + expr_base, keep_masters=(11, 22, 33))
        add_karmic(mat_kd, "Số Trưởng Thành")
        mat_code = format_num_code(mat_disp, mat_base)
        maturity_obj = {
            "code": mat_code,
            "display": mat_disp,
            "base": mat_base,
            "steps": mat_steps,
            "activation_age": max(30, 36 - lp_base),
            "archetype": NUMBER_ARCHETYPES.get(mat_code, NUMBER_ARCHETYPES[str(mat_base)]),
        }

        rt_raw = name_data["given_name_sum"] + bd
        rt_disp, rt_base, rt_steps, _ = reduce_number(rt_raw, keep_masters=(11, 22))
        rational_obj = {
            "code": format_num_code(rt_disp, rt_base),
            "display": rt_disp,
            "base": rt_base,
            "given_name": name_data["given_name"],
            "steps": rt_steps,
        }
        bridge_lp_expr = abs(lp_base - expr_base)

    # 5. Biểu Đồ Ngày Sinh 3x3, Biểu Đồ Họ Tên & Biểu Đồ Tổ Hợp (Composite)
    non_zero_birth_digits = [d for d in all_birth_digits if d > 0]
    birth_grid = _build_3x3_grid(non_zero_birth_digits)
    name_digits = name_data.get("all_pythagorean_digits", []) if name_data.get("has_name") else []
    name_grid = _build_3x3_grid(name_digits) if name_digits else None
    composite_grid = _build_3x3_grid(non_zero_birth_digits + name_digits) if name_digits else birth_grid

    # Tính các con số từ Họ tên đã giúp "lấp đầy" ô trống của Biểu đồ Ngày sinh
    filled_gaps_by_name = []
    if name_digits:
        name_set = set(name_digits)
        birth_set = set(non_zero_birth_digits)
        filled_gaps_by_name = sorted(list(name_set - birth_set))

    # Nếu có nhập Tên thường gọi / Tên thương hiệu, đánh giá mức độ cộng hưởng bù khuyết
    nickname_synergy = None
    if nick_data and nick_data.get("has_name"):
        nick_digits = set(nick_data["all_pythagorean_digits"])
        birth_missing = {d for d in range(1, 10) if birth_grid["counts"][str(d)] == 0}
        filled_by_nick = sorted(list(birth_missing & nick_digits))
        nickname_synergy = {
            "nickname": nick_data["clean_name"],
            "expression_code": nick_data["expression"]["code"],
            "soul_urge_code": nick_data["soul_urge"]["code"],
            "personality_code": nick_data["personality"]["code"],
            "chaldean": nick_data["chaldean"],
            "fills_birth_chart_missing_digits": filled_by_nick,
        }

    # 6. Kim Tự Tháp 4 Đỉnh Cao Đời Người (Pinnacles) & 4 Thử Thách (Challenges)
    # Chuẩn Pythagoras & David Phillips: Đỉnh 1 kết thúc ở tuổi (36 - lp_base)
    p1_end_age = 36 - lp_base
    p2_end_age = p1_end_age + 9
    p3_end_age = p2_end_age + 9
    p4_peak_age = p3_end_age + 9

    p1_disp, p1_base, _, _ = reduce_number(m_base + d_base, keep_masters=(11, 22))
    p2_disp, p2_base, _, _ = reduce_number(d_base + y_base, keep_masters=(11, 22))
    p3_disp, p3_base, _, _ = reduce_number(p1_disp + p2_disp, keep_masters=(11, 22))
    p4_disp, p4_base, _, _ = reduce_number(m_base + y_base, keep_masters=(11, 22))

    # 4 Thử thách dùng chữ số gốc 1..9
    c1 = abs(m_base - d_base)
    c2 = abs(d_base - y_base)
    c3 = abs(c1 - c2)
    c4 = abs(m_base - y_base)

    current_age = max(0, t_year - by)
    pinnacles_raw = [
        (1, p1_disp, p1_base, c1, 0, p1_end_age, by, by + p1_end_age),
        (2, p2_disp, p2_base, c2, p1_end_age + 1, p2_end_age, by + p1_end_age + 1, by + p2_end_age),
        (3, p3_disp, p3_base, c3, p2_end_age + 1, p3_end_age, by + p2_end_age + 1, by + p3_end_age),
        (4, p4_disp, p4_base, c4, p3_end_age + 1, 99, by + p3_end_age + 1, by + p4_peak_age),
    ]
    pinnacles = []
    for idx, p_disp, p_b, ch_num, age_start, age_end, yr_start, yr_end in pinnacles_raw:
        is_act = age_start <= current_age <= age_end
        p_code = format_num_code(p_disp, p_b)
        pinnacles.append({
            "stage": idx,
            "pinnacle_code": p_code,
            "pinnacle_base": p_b,
            "challenge_number": ch_num,
            "peak_milestone_age": p1_end_age + (idx - 1) * 9,
            "peak_milestone_year": by + p1_end_age + (idx - 1) * 9,
            "age_range": f"{age_start}–{age_end} tuổi" if idx < 4 else f"Từ {age_start} tuổi trở đi (Đỉnh {p4_peak_age}t)",
            "year_range": f"{yr_start}–{yr_end}" if idx < 4 else f"Từ {yr_start} (Đỉnh năm {yr_end})",
            "is_current": is_act,
            "theme": NUMBER_ARCHETYPES.get(p_code, NUMBER_ARCHETYPES[str(p_b)])["title"],
        })

    # 7. Chu Kỳ Vận Niên 9 Năm (Personal Year / Month / Day) & Dải Sóng 9 Năm
    _, py_base, _, _ = reduce_number(d_base + m_base + sum_digits(t_year), keep_masters=())
    _, pm_base, _, _ = reduce_number(py_base + t_month, keep_masters=())
    _, pd_base, _, _ = reduce_number(pm_base + t_day, keep_masters=())

    nine_year_wave = []
    for yr in range(t_year - 2, t_year + 7):
        _, w_py, _, _ = reduce_number(d_base + m_base + sum_digits(yr), keep_masters=())
        nine_year_wave.append({
            "year": yr,
            "age": max(0, yr - by),
            "personal_year": w_py,
            "is_target_year": yr == t_year,
            "phase": PERSONAL_YEAR_MEANINGS[w_py]["phase"],
            "advice": PERSONAL_YEAR_MEANINGS[w_py]["advice"],
        })

    # 8. Cốt Lõi Ma Trận Định Mệnh 22 Arcana (Matrix of Destiny Core Octagram)
    dm_portrait = reduce_arcana_22(bd)              # Góc Trái (0 tuổi): Chân dung bản thể
    dm_heaven = reduce_arcana_22(bm)                # Góc Trên (20 tuổi): Kết nối Thiên mệnh / Trực giác
    dm_earth = reduce_arcana_22(sum_digits(by))     # Góc Phải (40 tuổi): Nghiệp Tài chính & Hiện thực
    dm_karmic_bottom = reduce_arcana_22(dm_portrait + dm_heaven + dm_earth)  # Góc Dưới (60 tuổi): Nút nghiệp quá khứ
    dm_comfort_center = reduce_arcana_22(dm_portrait + dm_heaven + dm_earth + dm_karmic_bottom)  # Tâm Ma trận
    dm_sky_line = reduce_arcana_22(dm_heaven + dm_karmic_bottom)
    dm_earth_line = reduce_arcana_22(dm_portrait + dm_earth)
    dm_purpose_personal = reduce_arcana_22(dm_sky_line + dm_earth_line)  # Mục đích cá nhân (20-40t)

    # 9. Danh sách Nợ Nghiệp đã phát hiện
    karmic_debts_list = [
        {
            "number": kd_num,
            "code": KARMIC_DEBT_NUMBERS[kd_num]["code"],
            "title": KARMIC_DEBT_NUMBERS[kd_num]["title"],
            "lesson": KARMIC_DEBT_NUMBERS[kd_num]["lesson"],
            "found_in": srcs,
        }
        for kd_num, srcs in sorted(karmic_registry.items())
    ]

    return {
        "meta": {
            "birth_date_solar": b_date.isoformat(),
            "full_name_input": full_name,
            "clean_name": name_data.get("clean_name", ""),
            "nickname_input": nickname,
            "target_date": f"{t_year:04d}-{t_month:02d}-{t_day:02d}",
            "school_used": "Nhân số học Việt Nam (David Phillips / Quỳnh Hương)" if use_vn else "Pythagoras Quốc tế (Hans Decoz)",
            "y_vowel_rule": y_mode,
        },
        "core_numbers": {
            "life_path": {
                "code": lp_code,
                "display": lp_disp,
                "base": lp_base,
                "vn_code": lp_vn_code,
                "intl_code": lp_intl_code,
                "vn_steps": lp_vn_steps,
                "intl_steps": lp_intl_steps,
                "school_diff_note": (
                    f"Theo Nhân số học VN là Số {lp_vn_code}; theo Pythagoras Quốc tế (rút gọn 3 trụ) là Số {lp_intl_code}."
                    if lp_vn_code != lp_intl_code else None
                ),
                "archetype": NUMBER_ARCHETYPES.get(lp_code, NUMBER_ARCHETYPES[str(lp_base)]),
            },
            "birthday": {
                "code": format_num_code(d_disp, d_base),
                "day_raw": bd,
                "base": d_base,
                "archetype": NUMBER_ARCHETYPES.get(format_num_code(d_disp, d_base), NUMBER_ARCHETYPES[str(d_base)]),
            },
            "attitude": {
                "code": format_num_code(att_disp, att_base),
                "base": att_base,
                "steps": att_steps,
            },
            "expression": name_data.get("expression"),
            "soul_urge": name_data.get("soul_urge"),
            "personality": name_data.get("personality"),
            "maturity": maturity_obj,
            "rational_thought": rational_obj,
            "balance": name_data.get("balance"),
            "subconscious_self": name_data.get("subconscious_self"),
            "bridges": {
                "life_path_to_expression": bridge_lp_expr,
                "soul_to_personality": name_data.get("bridge_soul_personality"),
            },
        },
        "name_breakdown": {
            "has_name": name_data.get("has_name", False),
            "words": name_data.get("words", []),
            "karmic_lessons_missing": name_data.get("karmic_lessons_missing", []),
            "hidden_passions": name_data.get("hidden_passions", []),
            "planes_of_expression": name_data.get("planes_of_expression"),
            "filled_birth_chart_gaps": filled_gaps_by_name,
        },
        "karmic_debts": karmic_debts_list,
        "grids_3x3": {
            "birth_chart": birth_grid,
            "name_chart": name_grid,
            "composite_chart": composite_grid,
        },
        "pinnacles": pinnacles,
        "personal_cycles": {
            "target_year": t_year,
            "personal_year": py_base,
            "personal_year_theme": PERSONAL_YEAR_MEANINGS[py_base],
            "personal_month": pm_base,
            "personal_day": pd_base,
            "nine_year_wave": nine_year_wave,
        },
        "chaldean_name": name_data.get("chaldean"),
        "nickname_synergy": nickname_synergy,
        "destiny_matrix_22": {
            "portrait_0y": {"arcana": dm_portrait, "title": ARCANA_22_TITLES[dm_portrait]},
            "spiritual_20y": {"arcana": dm_heaven, "title": ARCANA_22_TITLES[dm_heaven]},
            "material_40y": {"arcana": dm_earth, "title": ARCANA_22_TITLES[dm_earth]},
            "karmic_tail_60y": {"arcana": dm_karmic_bottom, "title": ARCANA_22_TITLES[dm_karmic_bottom]},
            "comfort_zone_center": {"arcana": dm_comfort_center, "title": ARCANA_22_TITLES[dm_comfort_center]},
            "personal_purpose_20_40": {"arcana": dm_purpose_personal, "title": ARCANA_22_TITLES[dm_purpose_personal]},
        },
    }
