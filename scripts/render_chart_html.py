# -*- coding: utf-8 -*-
"""
render_chart_html.py — Trình xuất Hồ Sơ Đông - Tây Toàn Thư (Tử Vi 12 Cung + Bát Tự Tứ Trụ + Thần Số Học Đa Phái + Quẻ Dịch + Kỳ Môn) ra file HTML đơn (Self-contained)
Thiết kế chuẩn thẩm mỹ Á - Âu sang trọng, rõ nét để mở xem trên trình duyệt hoặc in PDF.
"""

from __future__ import annotations
import html
from typing import Any, Dict, List


def _esc(s: object) -> str:
    return html.escape(str(s)) if s is not None else ""


def _render_palace_cell(p: Dict[str, object]) -> str:
    cls = ["palace-cell"]
    if p.get("is_menh"):
        cls.append("is-menh")
    elif p.get("is_than"):
        cls.append("is-than")

    badges = []
    if p.get("is_than"):
        badges.append('<span class="badge badge-than">THÂN</span>')
    if p.get("has_triet"):
        badges.append('<span class="badge badge-triet">TRIỆT</span>')
    if p.get("has_tuan"):
        badges.append('<span class="badge badge-tuan">TUẦN</span>')

    majors_html = ""
    majors = p.get("major_stars", [])
    if not majors:
        majors_html = '<div class="vcd">(Vô Chính Diệu)</div>'
    else:
        items = []
        for m in majors:  # type: ignore
            b_code = m["brightness_code"]
            b_cls = "br-good" if b_code in ("M", "V", "Đ") else ("br-bad" if b_code == "H" else "br-mid")
            items.append(
                f'<div class="major-star {b_cls}">{_esc(m["name"])} <span class="br-tag">({b_code})</span></div>'
            )
        majors_html = "".join(items)

    ausp = [f'<span class="star-cat">{_esc(x["name"])}</span>' for x in p.get("auspicious_stars", [])]  # type: ignore
    shas = [f'<span class="star-sat">{_esc(x["name"])}</span>' for x in p.get("sha_stars", [])]  # type: ignore
    minors = [f'<span class="star-phu">{_esc(x)}</span>' for x in p.get("minor_stars", [])]  # type: ignore

    sihua_tags = []
    for sh in p.get("natal_sihua", []):  # type: ignore
        sh_cls = "sh-ky" if "Hóa Kỵ" in sh else "sh-cat"
        sihua_tags.append(f'<span class="sh-pill {sh_cls}">{_esc(sh)}</span>')
    for lsh in p.get("liunian_sihua", []):  # type: ignore
        sihua_tags.append(f'<span class="sh-pill sh-luu">{_esc(lsh)}</span>')

    return f"""
    <div class="{' '.join(cls)}">
      <div class="p-header">
        <span class="p-canchi">{_esc(p['can_chi'])}</span>
        <span class="p-name">{_esc(p['palace_name'])}</span>
        <span class="p-daihan">ĐH: {_esc(p['dai_han'])}</span>
      </div>
      <div class="p-badges">{''.join(badges)}</div>
      <div class="p-majors">{majors_html}</div>
      <div class="p-sihua">{''.join(sihua_tags)}</div>
      <div class="p-stars-grid">
        <div class="p-col-good">{' '.join(ausp + minors[:7])}</div>
        <div class="p-col-bad">{' '.join(shas + minors[7:])}</div>
      </div>
      <div class="p-footer">
        <span>{_esc(p['vong_thai_tue'])}</span>
        <span>{_esc(p['vong_bac_si'])}</span>
        <span class="p-ts">{_esc(p['vong_truong_sinh'])}</span>
      </div>
    </div>
    """


def _render_3x3_box(grid_obj: Dict[str, Any], label: str) -> str:
    rows_html = ""
    for row in grid_obj.get("rows_top_to_bottom", []):
        cells = ""
        for c in row:
            active_cls = "num-cell-has" if c["count"] > 0 else "num-cell-empty"
            val_txt = _esc(c["text"]) if c["count"] > 0 else f'<span style="color:#ccc;">({c["digit"]})</span>'
            cells += f'<div class="num-cell {active_cls}">{val_txt}</div>'
        rows_html += f'<div class="num-row">{cells}</div>'
    return f"""
    <div class="num-grid-card">
      <div class="num-grid-title">{_esc(label)}</div>
      <div class="num-grid-3x3">{rows_html}</div>
    </div>
    """


def _render_numerology_section(num: Dict[str, Any], cross_val: Any = None) -> str:
    cn = num["core_numbers"]
    lp = cn["life_path"]
    bd = cn["birthday"]
    att = cn["attitude"]
    expr = cn.get("expression")
    soul = cn.get("soul_urge")
    pers = cn.get("personality")
    mat = cn.get("maturity")
    chal = num.get("chaldean_name")
    dm22 = num["destiny_matrix_22"]
    pc = num["personal_cycles"]

    cards = [
        ("Số Chủ Đạo (Đường Đời)", lp["code"], lp["archetype"]["title"]),
        ("Năng Lực Ngày Sinh", bd["code"], f"Ngày sinh gốc {bd['day_raw']}"),
        ("Số Thái Độ Phản Xạ", att["code"], "Ấn tượng đầu tiên"),
    ]
    if expr and soul and pers and mat:
        cards.extend([
            ("Số Sứ Mệnh (Họ Tên)", expr["code"], expr["archetype"]["title"]),
            ("Số Linh Hồn (Nội Tâm)", soul["code"], soul["archetype"]["title"]),
            ("Số Nhân Cách (Vỏ Bọc)", pers["code"], pers["archetype"]["title"]),
            ("Số Trưởng Thành (Tuổi 35+)", mat["code"], mat["archetype"]["title"]),
            ("Sức Mạnh Tiềm Thức", f"{cn.get('subconscious_self', 0)}/9", f"Cầu nối LH-NC: {cn['bridges']['soul_to_personality']}"),
        ])

    cards_html = "".join(
        f"""<div class="num-stat-card">
              <div class="nsc-lbl">{_esc(lbl)}</div>
              <div class="nsc-val">{_esc(val)}</div>
              <div class="nsc-sub">{_esc(sub)}</div>
            </div>"""
        for lbl, val, sub in cards
    )

    diff_banner = (
        f'<div class="ys-box" style="margin-bottom:10px;"><strong>Đối chiếu song chuẩn:</strong> {_esc(lp["school_diff_note"])}</div>'
        if lp.get("school_diff_note") else ""
    )

    # Bảng chữ cái Họ tên & Chaldean
    name_html = ""
    if num["name_breakdown"].get("has_name"):
        word_chips = []
        for w in num["name_breakdown"]["words"]:
            lets = "".join(
                f'<span class="let-chip {"let-v" if l["role"] == "V" else "let-c"}">{_esc(l["char"])}<small>{l["pythagorean"]}</small></span>'
                for l in w["letters"]
            )
            word_chips.append(f'<div class="word-block">{lets}<div class="word-sum">{_esc(w["word"])} = {_esc(w["pythagorean_reduced"])}</div></div>')

        missing_str = ", ".join(str(x) for x in num["name_breakdown"]["karmic_lessons_missing"]) or "Không khuyết con số nào (Đủ 1–9)"
        passion_str = ", ".join(str(x) for x in num["name_breakdown"]["hidden_passions"]) or "Cân bằng"
        filled_str = ", ".join(str(x) for x in num["name_breakdown"]["filled_birth_chart_gaps"]) or "—"

        chal_box = ""
        if chal:
            chal_box = (
                f"<div><strong>Chaldean Cổ Đại (Rung động âm thanh):</strong> Số kép <strong>{chal['compound_number']}/{chal['single_digit']}</strong> — "
                f"<strong>{_esc(chal['compound_title'])}</strong> [{_esc(chal['compound_rank'])}]: {_esc(chal['compound_meaning'])}</div>"
            )

        nick_box = ""
        if num.get("nickname_synergy"):
            ns = num["nickname_synergy"]
            nc = ns["chaldean"]
            nick_box = (
                f"<div style='margin-top:4px;'><strong>Chấm điểm Tên thường gọi / Thương hiệu ({_esc(ns['nickname'])}):</strong> "
                f"Sứ mệnh {ns['expression_code']} • Linh hồn {ns['soul_urge_code']} • Chaldean <strong>{nc['compound_number']}/{nc['single_digit']} ({_esc(nc['compound_title'])} - {_esc(nc['compound_rank'])})</strong> "
                f"• Lấp thêm số trống ngày sinh: {', '.join(str(x) for x in ns['fills_birth_chart_missing_digits']) or '—'}</div>"
            )

        name_html = f"""
        <div style="margin: 12px 0;">
          <div style="font-size:12.5px;color:var(--muted);margin-bottom:6px;">
            <strong>Giải phẫu Họ Tên ({_esc(num['meta']['clean_name'])}):</strong> Ô nền hồng = Nguyên âm (Linh hồn), Ô nền xám = Phụ âm (Nhân cách)
          </div>
          <div class="words-wrap">{''.join(word_chips)}</div>
          <div class="ys-box" style="margin-top:8px;">
            <div><strong>Số Khuyết (Bài học nghiệp):</strong> {_esc(missing_str)} | <strong>Đam mê ẩn giấu:</strong> {_esc(passion_str)} | <strong>Số Họ tên bù vào Ngày sinh:</strong> {_esc(filled_str)}</div>
            {chal_box}
            {nick_box}
          </div>
        </div>
        """

    # Ma trận 3x3 & Mũi tên
    b_grid = num["grids_3x3"]["birth_chart"]
    c_grid = num["grids_3x3"]["composite_chart"]
    arrows_present = "".join(f"<li><strong style='color:var(--jade)'>✓ {_esc(a['name'])}:</strong> {_esc(a['meaning'])}</li>" for a in b_grid["present_arrows"]) or "<li>Không có mũi tên đầy nguyên bản (cần kết hợp lực bù từ Họ tên).</li>"
    arrows_empty = "".join(f"<li><strong style='color:var(--accent)'>○ {_esc(a['name'])}:</strong> {_esc(a['meaning'])}</li>" for a in b_grid["empty_arrows"]) or "<li>Không bị mũi tên trống nào trên biểu đồ ngày sinh.</li>"

    karmic_html = ""
    if num.get("karmic_debts"):
        kd_items = "".join(
            f"<li><strong>{_esc(k['title'])}</strong> (tại {_esc(', '.join(k['found_in']))}): {_esc(k['lesson'])}</li>"
            for k in num["karmic_debts"]
        )
        karmic_html = f'<div class="ys-box" style="border-left-color:var(--accent);background:#fff5f4;"><strong>Bài học Nợ Nghiệp Chuyển Hóa:</strong><ul style="margin:4px 0 0 18px;">{kd_items}</ul></div>'

    # 4 Đỉnh cao & Sóng 9 năm
    pin_rows = "".join(
        f"""<tr class="{'moving-row' if p['is_current'] else ''}">
              <td><strong>Đỉnh #{p['stage']}</strong> {'(Hiện tại)' if p['is_current'] else ''}</td>
              <td><strong class="bz-big">{_esc(p['pinnacle_code'])}</strong></td>
              <td>Thử thách <strong>{p['challenge_number']}</strong></td>
              <td>{_esc(p['age_range'])}</td>
              <td>{_esc(p['year_range'])}</td>
              <td style="text-align:left;">{_esc(p['theme'])}</td>
            </tr>"""
        for p in num["pinnacles"]
    )

    wave_cards = "".join(
        f"""<div class="dy-box {'dy-active' if w['is_target_year'] else ''}">
              <div class="dy-yr">Năm {w['year']} ({w['age']}t)</div>
              <div class="dy-cc">Số {w['personal_year']}</div>
              <div style="font-size:10.5px;">{_esc(w['phase'])}</div>
            </div>"""
        for w in pc["nine_year_wave"]
    )

    ew_box = ""
    if isinstance(cross_val, dict) and cross_val.get("east_west_synthesis"):
        ews = cross_val["east_west_synthesis"]
        ew_box = f"""
        <div class="ys-box" style="margin-top:12px; border-left-color:var(--navy); background:#f1f6fd;">
          <div style="font-weight:800;color:var(--navy);margin-bottom:4px;">☯️ × 🔢 HỘI TỤ ĐÔNG – TÂY (Tử Vi × Bát Tự × Thần Số Học):</div>
          <div>• {_esc(ews['element_number_resonance'])}</div>
          <div>• {_esc(ews['annual_rhythm_alignment'])}</div>
        </div>
        """

    return f"""
    <section class="card-section">
      <h2>Thần Số Học Đa Phái (Pythagoras × Chaldean × Ma Trận 22 Arcana)</h2>
      <p class="sub-info">
        <strong>Trường phái:</strong> {_esc(num['meta']['school_used'])} |
        <strong>Năm Cá Nhân {pc['target_year']}:</strong> <strong>Số {pc['personal_year']} — {_esc(pc['personal_year_theme']['phase'])}</strong> ({_esc(pc['personal_year_theme']['advice'])})
      </p>
      {diff_banner}
      <div class="num-stats-grid">{cards_html}</div>
      {name_html}
      <div class="num-grids-layout">
        {_render_3x3_box(b_grid, "Biểu Đồ Ngày Sinh (3×3)")}
        {_render_3x3_box(c_grid, "Biểu Đồ Tổ Hợp (Ngày Sinh + Họ Tên)")}
        <div style="flex:1;min-width:280px;font-size:12.5px;">
          <strong>Các Mũi Tên Nổi Trội & Bài Học Rèn Luyện:</strong>
          <ul style="margin:6px 0 8px 18px;">{arrows_present}{arrows_empty}</ul>
        </div>
      </div>
      {karmic_html}
      <h3 style="font-size:15px;color:var(--navy);margin:14px 0 6px;">Kim Tự Tháp 4 Đỉnh Cao Đời Người & 4 Thử Thách</h3>
      <table class="bazi-table">
        <thead><tr><th>Giai đoạn</th><th>Số Đỉnh Cao</th><th>Số Thử Thách</th><th>Độ tuổi</th><th> Giai đoạn năm</th><th>Chủ đề trọng tâm</th></tr></thead>
        <tbody>{pin_rows}</tbody>
      </table>
      <h3 style="font-size:15px;color:var(--navy);margin:14px 0 6px;">Chu Kỳ Sóng 9 Năm Cá Nhân</h3>
      <div class="dayun-strip">{wave_cards}</div>
      <div class="ys-box" style="margin-top:12px;">
        <strong>Ma Trận Định Mệnh (22 Arcana Core):</strong>
        Bản thể (0t): <strong>#{dm22['portrait_0y']['arcana']}</strong> |
        Thiên mệnh (20t): <strong>#{dm22['spiritual_20y']['arcana']}</strong> |
        Tài chính (40t): <strong>#{dm22['material_40y']['arcana']}</strong> |
        Nút nghiệp (60t): <strong>#{dm22['karmic_tail_60y']['arcana']}</strong> |
        Tâm Vùng Thoải Mái: <strong>#{dm22['comfort_zone_center']['arcana']} ({_esc(dm22['comfort_zone_center']['title'])})</strong>
      </div>
      {ew_box}
    </section>
    """


def render_full_html_report(payload: Dict[str, object], title: str = "Hồ Sơ Mệnh Lý & Thần Số Học Đông-Tây — kb-tuvi") -> str:
    tuvi = payload.get("tuvi")
    bazi = payload.get("bazi")
    numerology = payload.get("numerology")
    cross_val = payload.get("cross_validation")
    iching = payload.get("iching")
    qimen = payload.get("qimen")
    meta = payload.get("meta", {})

    sections: List[str] = []

    # 1. Bảng Thiên Bàn & Địa Bàn 12 Cung Tử Vi
    if isinstance(tuvi, dict):
        prof = tuvi["profile"]  # type: ignore
        by_b = {p["branch_idx"]: p for p in tuvi["palaces_by_branch"]}  # type: ignore
        tf = tuvi["target_year_fortune"]  # type: ignore
        patterns_html = "".join(
            f'<li><strong>{_esc(pt["name"])}</strong> <em>({_esc(pt["rank"])})</em>: {_esc(pt["desc"])}</li>'
            for pt in tuvi.get("classic_patterns", [])  # type: ignore
        )

        tuvi_grid = f"""
        <section class="card-section">
          <h2>I. Lá Số Tử Vi Đẩu Số (Nam Phái VN × Trung Châu × Phi Tinh)</h2>
          <div class="tuvi-board">
            {_render_palace_cell(by_b[5])}
            {_render_palace_cell(by_b[6])}
            {_render_palace_cell(by_b[7])}
            {_render_palace_cell(by_b[8])}

            {_render_palace_cell(by_b[4])}
            <div class="thien-ban">
              <div class="tb-title">THIÊN BÀN MỆNH SỐ</div>
              <div class="tb-grid">
                <div><strong>Đương số:</strong> {_esc(meta.get('name') or 'Ẩn danh')} ({_esc(prof['gender_polarity'])})</div>
                <div><strong>Dương lịch:</strong> {_esc(meta.get('clock_time', ''))}</div>
                <div><strong>Chân Thái Dương:</strong> {_esc(meta.get('true_solar_time', ''))} ({_esc(meta.get('place', ''))})</div>
                <div><strong>Âm lịch (UTC+7):</strong> {_esc(prof['lunar_date'])} — {_esc(prof['birth_hour'])}</div>
                <div><strong>Bản Mệnh:</strong> {_esc(prof['ban_menh_nayin'])}</div>
                <div><strong>Cục:</strong> {_esc(prof['cuc'])}</div>
                <div><strong>Mệnh / Thân:</strong> Mệnh tại {_esc(prof['menh_palace'])} | {_esc(prof['than_cu'])}</div>
                <div><strong>Mệnh Chủ / Thân Chủ:</strong> {_esc(prof['menh_chu'])} / {_esc(prof['than_chu'])}</div>
                <div><strong>Tuần / Triệt:</strong> Tuần [{_esc(prof['tuan_khong'])}] | Triệt [{_esc(prof['triet_lo'])}]</div>
                <div><strong>Năm hạn {_esc(tf['target_solar_year'])}:</strong> {_esc(tf['liunian_can_chi'])} ({_esc(tf['nominal_age'])} tuổi mụ) — {_esc(tf['liunian_menh_palace'])}</div>
              </div>
              <div class="tb-patterns">
                <strong>Cách cục nổi bật:</strong>
                <ul>{patterns_html}</ul>
              </div>
            </div>
            {_render_palace_cell(by_b[9])}

            {_render_palace_cell(by_b[3])}
            {_render_palace_cell(by_b[10])}

            {_render_palace_cell(by_b[2])}
            {_render_palace_cell(by_b[1])}
            {_render_palace_cell(by_b[0])}
            {_render_palace_cell(by_b[11])}
          </div>
        </section>
        """
        sections.append(tuvi_grid)

    # 2. Bảng Bát Tự Tứ Trụ
    if isinstance(bazi, dict):
        pillars = bazi["pillars"]  # type: ignore
        cols = ["year", "month", "day", "hour"]
        rows_thap_than = "".join(f"<td><strong>{_esc(pillars[c]['stem_ten_god'])}</strong></td>" for c in cols)
        rows_stem = "".join(f"<td class='bz-big'>{_esc(pillars[c]['stem'])} <small>({_esc(pillars[c]['stem_element'])})</small></td>" for c in cols)
        rows_branch = "".join(f"<td class='bz-big'>{_esc(pillars[c]['branch'])} <small>({_esc(pillars[c]['branch_element'])})</small></td>" for c in cols)
        rows_hidden = "".join(
            "<td>" + "<br>".join(f"{_esc(h['stem'])} ({_esc(h['ten_god'])})" for h in pillars[c]["hidden_stems"]) + "</td>"
            for c in cols
        )
        rows_nayin = "".join(f"<td>{_esc(pillars[c]['nayin'])}</td>" for c in cols)
        rows_cs = "".join(f"<td>{_esc(pillars[c]['changsheng_from_day'])}</td>" for c in cols)
        rows_ss = "".join(f"<td>{_esc(', '.join(pillars[c]['shen_sha']) or '—')}</td>" for c in cols)

        dayun_cards = "".join(
            f"""<div class="dy-box {'dy-active' if d['is_current'] else ''}">
                  <div class="dy-yr">{_esc(d['solar_years'])}</div>
                  <div class="dy-cc">{_esc(d['can_chi'])}</div>
                  <div class="dy-tg">{_esc(d['stem_ten_god'])} / {_esc(d['branch_main_ten_god'])}</div>
                  <div class="dy-age">{_esc(d['nominal_age'])}</div>
                </div>"""
            for d in bazi.get("dayun", [])  # type: ignore
        )

        dm = bazi["day_master"]  # type: ignore
        ys = bazi["yongshen_guidance"]  # type: ignore
        bazi_sec = f"""
        <section class="card-section">
          <h2>II. Tứ Trụ Bát Tự & Đại Vận (Chuẩn Tiết Khí Thiên Văn)</h2>
          <p class="sub-info">
            <strong>Nhật Chủ:</strong> {_esc(dm['stem'])} ({_esc(dm['element'])}) — <strong>{_esc(dm['strength_assessment'])}</strong> (Tỷ/Ấn chiếm {_esc(dm['support_percentage'])}%) |
            <strong>Khởi vận:</strong> {_esc(bazi['dayun_handover']['offset_after_birth'])} (Giao vận {_esc(bazi['dayun_handover']['exact_handover_date'])})
          </p>
          <table class="bazi-table">
            <thead><tr><th>Hạng mục</th><th>Trụ Năm</th><th>Trụ Tháng (Đề Cương)</th><th>Trụ Ngày (Bản Thân)</th><th>Trụ Giờ</th></tr></thead>
            <tbody>
              <tr><td>Thập Thần</td>{rows_thap_than}</tr>
              <tr><td>Thiên Can</td>{rows_stem}</tr>
              <tr><td>Địa Chi</td>{rows_branch}</tr>
              <tr><td>Tàng Can</td>{rows_hidden}</tr>
              <tr><td>Nạp Âm</td>{rows_nayin}</tr>
              <tr><td>Vòng Trường Sinh</td>{rows_cs}</tr>
              <tr><td>Thần Sát</td>{rows_ss}</tr>
            </tbody>
          </table>
          <div class="ys-box">
            <div><strong>Hành Hỷ/Dụng (Phù Ức):</strong> {_esc(', '.join(ys['fuyi_favorable_elements']))} | <strong>Hành Kỵ:</strong> {_esc(', '.join(ys['fuyi_unfavorable_elements']))}</div>
            <div><strong>Điều Hầu (Cùng Thông Bảo Giám):</strong> {_esc(ys['qiong_tong_tiaohou'])}</div>
          </div>
          <div class="dayun-strip">{dayun_cards}</div>
        </section>
        """
        sections.append(bazi_sec)

    # 3. Thần Số Học Đa Phái & Kiểm Chứng Chéo Đông - Tây
    if isinstance(numerology, dict):
        sections.append(_render_numerology_section(numerology, cross_val=cross_val))

    # 4. Bảng Quẻ Kinh Dịch Lục Hào
    if isinstance(iching, dict):
        ph = iching["primary_hexagram"]  # type: ignore
        ch = iching.get("changed_hexagram")
        pc = iching["pillars_at_cast"]  # type: ignore
        lines_rev = list(reversed(iching["lines_bottom_to_top"]))  # type: ignore
        line_rows = ""
        for ln in lines_rev:
            chg_txt = ""
            if ln.get("changed_to"):
                ct = ln["changed_to"]
                chg_txt = f"{_esc(ct['changed_liuqin'])} {_esc(ct['changed_can_chi'])} ({_esc(', '.join(ct['tags']))})"
            line_rows += f"""
            <tr class="{'moving-row' if ln['is_moving'] else ''}">
              <td>Hào {_esc(ln['position'])}</td>
              <td>{_esc(ln['beast'])}</td>
              <td><small>{_esc(ln['fushen'] or '')}</small></td>
              <td><strong>{_esc(ln['liuqin'])} {_esc(ln['can_chi'])}</strong></td>
              <td class="hex-sym">{_esc(ln['symbol'])}</td>
              <td><strong>{_esc(ln['shi_ying'])}</strong></td>
              <td>{_esc(', '.join(ln['status_flags']))}</td>
              <td>{chg_txt}</td>
            </tr>
            """
        iching_sec = f"""
        <section class="card-section">
          <h2>Quẻ Kinh Dịch — Lục Hào Nạp Giáp & Mai Hoa</h2>
          <p class="sub-info">
            <strong>Câu hỏi:</strong> {_esc(iching.get('question') or 'Tổng quan sự việc')} |
            <strong>Tứ Trụ giờ gieo:</strong> Năm {_esc(pc['year'])} - Tháng {_esc(pc['month'])} - Ngày {_esc(pc['day'])} - Giờ {_esc(pc['hour'])} (Tuần Không: {_esc(pc['tuan_khong'])})
          </p>
          <p class="sub-info">
            <strong>Bản Quái:</strong> Quẻ #{_esc(ph['number'])} <strong>{_esc(ph['name'])}</strong> ({_esc(ph['palace'])})
            {f" ➔ <strong>Biến Quái:</strong> Quẻ #{_esc(ch['number'])} <strong>{_esc(ch['name'])}</strong>" if ch else " (Quẻ Tĩnh)"}
          </p>
          <table class="bazi-table">
            <thead><tr><th>Hào</th><th>Lục Thần</th><th>Phục Thần</th><th>Lục Thân & Nạp Giáp</th><th>Tượng Hào</th><th>Thế/Ứng</th><th>Trạng Thái Nhật/Nguyệt</th><th>Hào Biến</th></tr></thead>
            <tbody>{line_rows}</tbody>
          </table>
        </section>
        """
        sections.append(iching_sec)

    # 5. Kỳ Môn Độn Giáp Cửu Cung
    if isinstance(qimen, dict):
        qm_cells = ""
        for cp in qimen.get("palaces", []):  # type: ignore
            if cp["palace"] == 5:
                qm_cells += f"""<div class="qm-cell qm-center"><strong>{_esc(cp['name'])}</strong><br>Địa bàn: {_esc(cp['earth_stem'])}<br><small>{_esc(cp['note'])}</small></div>"""
            else:
                qm_cells += f"""
                <div class="qm-cell">
                  <div class="qm-top"><span>{_esc(cp['name'])} ({_esc(cp['direction'])})</span><span>{_esc(cp['god'])}</span></div>
                  <div class="qm-mid"><strong>{_esc(cp['door'])}</strong> | {_esc(cp['star'])}</div>
                  <div class="qm-bot">Thiên: <strong>{_esc(cp['heaven_stem'])}</strong> / Địa: <strong>{_esc(cp['earth_stem'])}</strong></div>
                </div>
                """
        sections.append(f"""
        <section class="card-section">
          <h2>Bàn Kỳ Môn Độn Giáp Thời Gia</h2>
          <p class="sub-info"><strong>Cục:</strong> {_esc(qimen['dun_type'])} | <strong>Trực Phù:</strong> {_esc(qimen['zhifu_star'])} | <strong>Trực Sử:</strong> {_esc(qimen['zhishi_door'])}</p>
          <div class="qm-grid">{qm_cells}</div>
        </section>
        """)

    return f"""<!DOCTYPE html>
<html lang="vi">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{_esc(title)}</title>
<style>
  :root {{
    --bg: #f8f5ee; --card: #fffdf9; --ink: #1e1b18; --muted: #655d53;
    --border: #d8cebe; --accent: #8b1e1e; --gold: #a67c2e; --jade: #1b6b52; --navy: #1f4673;
  }}
  * {{ box-sizing: border-box; }}
  body {{ margin: 0; padding: 24px; background: var(--bg); color: var(--ink); font-family: "Segoe UI", system-ui, sans-serif; line-height: 1.45; }}
  h1 {{ text-align: center; color: var(--accent); margin: 0 0 6px; letter-spacing: 0.5px; }}
  .subtitle {{ text-align: center; color: var(--muted); font-size: 13px; margin-bottom: 22px; }}
  .card-section {{ max-width: 1280px; margin: 0 auto 28px; background: var(--card); border: 1px solid var(--border); border-radius: 10px; padding: 18px; box-shadow: 0 4px 14px rgba(0,0,0,0.04); }}
  h2 {{ margin: 0 0 12px; font-size: 18px; color: var(--accent); border-bottom: 2px solid #efe6d8; padding-bottom: 6px; }}
  .tuvi-board {{ display: grid; grid-template-columns: repeat(4, 1fr); grid-template-rows: repeat(4, minmax(195px, auto)); gap: 6px; }}
  .thien-ban {{ grid-column: 2 / 4; grid-row: 2 / 4; border: 2px double var(--gold); border-radius: 8px; padding: 14px 16px; background: #fffaf0; display: flex; flex-direction: column; justify-content: space-between; }}
  .tb-title {{ text-align: center; font-weight: 800; color: var(--accent); font-size: 16px; letter-spacing: 1px; margin-bottom: 8px; }}
  .tb-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 6px 14px; font-size: 12.5px; }}
  .tb-patterns {{ margin-top: 10px; font-size: 12px; background: #fff; border: 1px solid #eadfce; border-radius: 6px; padding: 8px 10px; max-height: 160px; overflow-y: auto; }}
  .tb-patterns ul {{ margin: 4px 0 0 16px; padding: 0; }}
  .palace-cell {{ border: 1px solid var(--border); border-radius: 6px; padding: 7px 8px; background: #fff; display: flex; flex-direction: column; justify-content: space-between; font-size: 11.5px; }}
  .palace-cell.is-menh {{ border: 2px solid var(--accent); background: #fff8f6; }}
  .palace-cell.is-than {{ border: 1.5px solid var(--gold); }}
  .p-header {{ display: flex; justify-content: space-between; align-items: center; border-bottom: 1px dashed #e5dccd; padding-bottom: 3px; font-size: 11px; }}
  .p-canchi {{ color: var(--muted); font-weight: 600; }}
  .p-name {{ font-weight: 800; color: var(--navy); font-size: 12.5px; }}
  .p-daihan {{ color: var(--gold); font-weight: 700; }}
  .p-badges {{ margin: 3px 0; min-height: 16px; display: flex; gap: 4px; flex-wrap: wrap; }}
  .badge {{ font-size: 9.5px; font-weight: 800; padding: 1px 5px; border-radius: 3px; color: #fff; }}
  .badge-than {{ background: var(--gold); }}
  .badge-triet {{ background: #222; }}
  .badge-tuan {{ background: #5a4a78; }}
  .p-majors {{ text-align: center; margin: 3px 0; min-height: 36px; }}
  .major-star {{ font-size: 13.5px; font-weight: 800; }}
  .br-good {{ color: var(--accent); }}
  .br-mid {{ color: var(--navy); }}
  .br-bad {{ color: #6c757d; }}
  .br-tag {{ font-size: 10.5px; font-weight: 600; }}
  .vcd {{ color: #999; font-style: italic; font-size: 11.5px; padding-top: 6px; }}
  .p-sihua {{ display: flex; flex-wrap: wrap; gap: 3px; margin: 2px 0; }}
  .sh-pill {{ font-size: 10px; padding: 1px 5px; border-radius: 3px; font-weight: 700; }}
  .sh-cat {{ background: #e6f4ee; color: var(--jade); border: 1px solid #b7e1ce; }}
  .sh-ky {{ background: #fdeaea; color: #b01e1e; border: 1px solid #f5c2c2; }}
  .sh-luu {{ background: #eef3fb; color: var(--navy); border: 1px solid #c9daf6; }}
  .p-stars-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 4px; margin: 4px 0; line-height: 1.35; flex: 1; }}
  .star-cat {{ color: var(--jade); font-weight: 700; display: inline-block; margin-right: 4px; }}
  .star-sat {{ color: #b01e1e; font-weight: 700; display: inline-block; margin-right: 4px; }}
  .star-phu {{ color: #444; display: inline-block; margin-right: 4px; }}
  .p-footer {{ display: flex; justify-content: space-between; border-top: 1px dashed #e5dccd; padding-top: 3px; font-size: 10.5px; color: var(--muted); font-weight: 600; }}
  .p-ts {{ color: var(--navy); }}
  .bazi-table {{ width: 100%; border-collapse: collapse; font-size: 13px; margin-top: 8px; }}
  .bazi-table th, .bazi-table td {{ border: 1px solid var(--border); padding: 7px 10px; text-align: center; }}
  .bazi-table th {{ background: #f3ece0; color: var(--ink); }}
  .bz-big {{ font-size: 16px; font-weight: 800; color: var(--accent); }}
  .ys-box {{ margin-top: 10px; padding: 10px 12px; background: #f8f4eb; border-left: 4px solid var(--gold); font-size: 13px; }}
  .dayun-strip {{ display: grid; grid-template-columns: repeat(9, 1fr); gap: 6px; margin-top: 12px; }}
  .dy-box {{ border: 1px solid var(--border); border-radius: 6px; padding: 6px; text-align: center; font-size: 11.5px; background: #fff; }}
  .dy-box.dy-active {{ border: 2px solid var(--accent); background: #fff5f3; }}
  .dy-cc {{ font-weight: 800; font-size: 14px; color: var(--navy); margin: 2px 0; }}
  .moving-row {{ background: #fff7eb; }}
  .hex-sym {{ font-family: Consolas, monospace; font-weight: 700; }}
  .qm-grid {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 8px; margin-top: 10px; }}
  .qm-cell {{ border: 1px solid var(--border); border-radius: 6px; padding: 10px; background: #fff; font-size: 12.5px; }}
  .qm-center {{ background: #faf6ed; text-align: center; display: flex; flex-direction: column; justify-content: center; }}
  .qm-top {{ display: flex; justify-content: space-between; color: var(--muted); font-size: 11.5px; margin-bottom: 6px; }}
  .qm-mid {{ font-size: 14px; color: var(--accent); margin-bottom: 6px; }}
  .sub-info {{ font-size: 13px; margin: 4px 0 8px; }}
  /* Numerology Styles */
  .num-stats-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(175px, 1fr)); gap: 8px; margin: 10px 0; }}
  .num-stat-card {{ border: 1px solid var(--border); border-radius: 8px; padding: 10px; background: #fff; text-align: center; }}
  .nsc-lbl {{ font-size: 11.5px; color: var(--muted); font-weight: 700; }}
  .nsc-val {{ font-size: 24px; font-weight: 900; color: var(--accent); margin: 3px 0; }}
  .nsc-sub {{ font-size: 11px; color: var(--navy); }}
  .words-wrap {{ display: flex; flex-wrap: wrap; gap: 10px; }}
  .word-block {{ border: 1px dashed var(--border); border-radius: 7px; padding: 6px 8px; background: #fff; }}
  .let-chip {{ display: inline-flex; flex-direction: column; align-items: center; padding: 2px 6px; margin-right: 3px; border-radius: 4px; font-weight: 700; font-size: 12px; }}
  .let-v {{ background: #fdecec; color: var(--accent); border: 1px solid #f4c2c2; }}
  .let-c {{ background: #f2f4f7; color: #333; border: 1px solid #d5dbe3; }}
  .word-sum {{ font-size: 11px; color: var(--muted); text-align: center; margin-top: 4px; font-weight: 700; }}
  .num-grids-layout {{ display: flex; flex-wrap: wrap; gap: 16px; align-items: flex-start; margin: 12px 0; }}
  .num-grid-card {{ border: 1px solid var(--border); border-radius: 8px; padding: 10px 12px; background: #fff; }}
  .num-grid-title {{ font-size: 12px; font-weight: 800; color: var(--navy); text-align: center; margin-bottom: 6px; }}
  .num-grid-3x3 {{ display: flex; flex-direction: column; gap: 4px; }}
  .num-row {{ display: grid; grid-template-columns: repeat(3, 62px); gap: 4px; }}
  .num-cell {{ height: 48px; display: flex; align-items: center; justify-content: center; border: 1px solid var(--border); border-radius: 6px; font-weight: 800; font-size: 15px; }}
  .num-cell-has {{ background: #fff8ec; color: var(--accent); border-color: var(--gold); }}
  .num-cell-empty {{ background: #fafafa; font-weight: 400; font-size: 12px; }}
  .disclaimer {{ max-width: 1280px; margin: 12px auto 0; text-align: center; font-size: 12px; color: var(--muted); }}
</style>
</head>
<body>
  <h1>{_esc(title)}</h1>
  <div class="subtitle">Hệ thống xem Tử Vi, Bát Tự, Thần Số Học &amp; Kinh Dịch chuẩn Lịch Vạn Niên Việt Nam</div>
  {"".join(sections)}
  <div class="disclaimer">Lưu ý văn hóa: Mệnh lý phương Đông &amp; Thần số học phương Tây là bộ công cụ tham chiếu nhận thức bản thân, tâm lý và quản trị chiến lược; không thay thế chẩn đoán y khoa, tư vấn pháp lý hay cam kết đầu tư tài chính tuyệt đối.<br><strong style="color:#8b1e1e;font-size:13.5px;display:inline-block;margin-top:8px;">❤️ From K.B - Hội BĐS Đồ Sơn ❤️</strong></div>
</body>
</html>"""
