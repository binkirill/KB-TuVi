# -*- coding: utf-8 -*-
"""
render_chart_html.py — Trình xuất Lá Số Tử Vi 12 Cung + Bát Tự Tứ Trụ + Quẻ Dịch ra file HTML đơn (Self-contained)
Thiết kế chuẩn thẩm mỹ Đông Phương cổ điển pha hiện đại, rõ nét để mở xem trên trình duyệt hoặc in PDF.
"""

from __future__ import annotations
import html
from typing import Dict, Optional, List


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


def render_full_html_report(payload: Dict[str, object], title: str = "Hồ Sơ Mệnh Lý Tổng Hợp — kb-tuvi") -> str:
    tuvi = payload.get("tuvi")
    bazi = payload.get("bazi")
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

        # Lưới 4x4 truyền thống:
        # Hàng 1: Tỵ (5), Ngọ (6), Mùi (7), Thân (8)
        # Hàng 2: Thìn (4), [Thiên Bàn 2x2], Dậu (9)
        # Hàng 3: Mão (3), [Thiên Bàn 2x2], Tuất (10)
        # Hàng 4: Dần (2), Sửu (1), Tý (0), Hợi (11)
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

    # 3. Bảng Quẻ Kinh Dịch Lục Hào
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
          <h2>III. Quẻ Kinh Dịch — Lục Hào Nạp Giáp & Mai Hoa</h2>
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

    # 4. Kỳ Môn Độn Giáp Cửu Cung
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
          <h2>IV. Bàn Kỳ Môn Độn Giáp Thời Gia</h2>
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
  .disclaimer {{ max-width: 1280px; margin: 12px auto 0; text-align: center; font-size: 12px; color: var(--muted); }}
</style>
</head>
<body>
  <h1>{_esc(title)}</h1>
  <div class="subtitle">Hệ thống tính toán định danh Zero-Hallucination (kb-tuvi) — Lịch Thiên Văn UTC+7 & Cổ Thư Đối Chiếu</div>
  {"".join(sections)}
  <div class="disclaimer">Lưu ý văn hóa: Mệnh lý & Dịch học phương Đông là hệ quy chiếu chiêm nghiệm nhân sinh, tâm lý và quản trị rủi ro; không thay thế chẩn đoán y khoa, tư vấn pháp lý hay cam kết đầu tư tài chính tuyệt đối.</div>
</body>
</html>"""
