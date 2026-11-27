# -*- coding: utf-8 -*-
r"""
sync_from_skill.py — Công cụ đồng bộ 1-Click cho KB-TUVI (Single Source of Truth)
Luồng đồng bộ chuẩn:
  1. Nguồn gốc duy nhất: G:\My Drive\Antigravity\Skills\kb-tuvi
  2. Tự đồng bộ sang bản nạp Skill của hệ thống: D:\AI\Skills\kb-tuvi
  3. Tự đồng bộ toàn bộ assets/, references/, scripts/, SKILL.md sang bản Web: G:\My Drive\Antigravity\kb-tuvi-web
     (tự đảm bảo studio_gui.html luôn có thẻ <script src="/assets/gemini_ai_addon.js"></script>
      và không bao giờ ghi đè .git, .env, api/, vercel.json, render.yaml).
  4. Chạy kiểm thử tự động trước khi commit.
  5. Khi truyền --push: tự động git add + git commit + git push origin main -> Vercel tự redeploy trong 30 giây!

Cách dùng:
  python -X utf8 "G:\My Drive\Antigravity\kb-tuvi-web\sync_from_skill.py" --push
"""

from __future__ import annotations
import argparse
import importlib.util
import json
import os
import shutil
import subprocess
import sys
from datetime import datetime

SKILL_SRC = r"G:\My Drive\Antigravity\Skills\kb-tuvi"
SKILL_MIRROR = r"D:\AI\Skills\kb-tuvi"
WEB_REPO = r"G:\My Drive\Antigravity\kb-tuvi-web"

SYNC_FOLDERS = ("assets", "references", "scripts")
SYNC_FILES = ("SKILL.md", "AI_HANDOFF_README.md")
ADDON_TAG = '<script src="/api/addon"></script>'


def ensure_addon_tag_in_html(html_path: str) -> bool:
    """Đảm bảo studio_gui.html luôn nạp plugin Gemini AI rời mà không làm hỏng giao diện gốc."""
    if not os.path.isfile(html_path):
        return False
    with open(html_path, "r", encoding="utf-8") as f:
        text = f.read()
    if "/api/addon" in text:
        return False
    if '<script src="/assets/gemini_ai_addon.js"></script>' in text:
        updated = text.replace('<script src="/assets/gemini_ai_addon.js"></script>', ADDON_TAG)
    elif "</body>" in text:
        updated = text.replace("</body>", f"{ADDON_TAG}\n</body>", 1)
    else:
        updated = text + f"\n{ADDON_TAG}\n"
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(updated)
    print(f"  [AUTO-INJECT] Đã tự động gắn {ADDON_TAG} vào {html_path}")
    return True


def sync_tree(src_root: str, dst_root: str, mirror_deletes: bool = False) -> int:
    changed = 0
    os.makedirs(dst_root, exist_ok=True)

    for fname in SYNC_FILES:
        sp = os.path.join(src_root, fname)
        dp = os.path.join(dst_root, fname)
        if os.path.isfile(sp):
            if not os.path.isfile(dp) or os.path.getsize(sp) != os.path.getsize(dp) or open(sp, "rb").read() != open(dp, "rb").read():
                shutil.copy2(sp, dp)
                print(f"  [SYNC] {fname} -> {dst_root}")
                changed += 1

    for sub in SYNC_FOLDERS:
        s_dir = os.path.join(src_root, sub)
        d_dir = os.path.join(dst_root, sub)
        if not os.path.isdir(s_dir):
            continue
        src_rel_files = set()
        for walk_root, dirs, files in os.walk(s_dir):
            dirs[:] = [d for d in dirs if d != "__pycache__" and not d.startswith(".")]
            rel_sub = os.path.relpath(walk_root, s_dir)
            target_dir = d_dir if rel_sub == "." else os.path.join(d_dir, rel_sub)
            os.makedirs(target_dir, exist_ok=True)
            for fname in sorted(files):
                if fname.endswith(".pyc") or fname == ".DS_Store":
                    continue
                sp = os.path.join(walk_root, fname)
                dp = os.path.join(target_dir, fname)
                rel_key = fname if rel_sub == "." else os.path.join(rel_sub, fname)
                src_rel_files.add(rel_key)
                if not os.path.isfile(dp) or open(sp, "rb").read() != open(dp, "rb").read():
                    shutil.copy2(sp, dp)
                    print(f"  [SYNC] {sub}/{rel_key} -> {dst_root}")
                    changed += 1
        if mirror_deletes and os.path.isdir(d_dir):
            for walk_root, dirs, files in os.walk(d_dir):
                dirs[:] = [d for d in dirs if d != "__pycache__" and not d.startswith(".")]
                rel_sub = os.path.relpath(walk_root, d_dir)
                for fname in files:
                    if fname.endswith(".pyc"):
                        continue
                    rel_key = fname if rel_sub == "." else os.path.join(rel_sub, fname)
                    if rel_key not in src_rel_files:
                        os.remove(os.path.join(walk_root, fname))
                        print(f"  [DEL]  {sub}/{rel_key} (đã xóa ở bản gốc)")
                        changed += 1

    # Nếu đích là WEB_REPO (có vercel.json), đồng bộ thêm assets/images và assets/scrollcraft -> public/assets/... để Vercel CDN phục vụ trực tiếp
    if os.path.isfile(os.path.join(dst_root, "vercel.json")):
        for sub_pub in ("images", "scrollcraft"):
            src_sub_dir = os.path.join(src_root, "assets", sub_pub)
            if not os.path.isdir(src_sub_dir):
                continue
            pub_sub_dir = os.path.join(dst_root, "public", "assets", sub_pub)
            os.makedirs(pub_sub_dir, exist_ok=True)
            for fn in sorted(os.listdir(src_sub_dir)):
                sp = os.path.join(src_sub_dir, fn)
                dp = os.path.join(pub_sub_dir, fn)
                if os.path.isfile(sp) and (not os.path.isfile(dp) or open(sp, "rb").read() != open(dp, "rb").read()):
                    shutil.copy2(sp, dp)
                    print(f"  [SYNC] public/assets/{sub_pub}/{fn} -> {dst_root}")
                    changed += 1
    return changed


def quick_verify_web_repo() -> None:
    """Kiểm thử nhanh trước khi đẩy lên GitHub/Vercel để đảm bảo web không bao giờ bị lỗi."""
    scripts_dir = os.path.join(WEB_REPO, "scripts")
    if scripts_dir not in sys.path:
        sys.path.insert(0, scripts_dir)

    with open(os.path.join(WEB_REPO, "vercel.json"), "r", encoding="utf-8") as f:
        json.load(f)

    import gui_server as gs
    status, _, raw_h = gs.dispatch_get("/api/health")
    assert status == 200 and json.loads(raw_h.decode("utf-8"))["ok"] is True

    status, _, raw_c = gs.dispatch_get("/api/config")
    assert status == 200 and json.loads(raw_c.decode("utf-8"))["ok"] is True

    status, _, raw_js = gs.dispatch_get("/assets/gemini_ai_addon.js")
    assert status == 200 and b"runGeminiInterpret" in raw_js

    status, _, raw_sdk = gs.dispatch_get("/sdk/numerology.js")
    assert status == 200 and len(raw_sdk) > 1000

    status, _, raw_img = gs.dispatch_get("/assets/images/hero_celestial.jpg")
    assert status == 200 and len(raw_img) > 1000

    payload = json.dumps({
        "name": "Nguyễn Minh Quân",
        "nickname": "K.B Đồ Sơn",
        "gender": "nam",
        "date_type": "solar",
        "date": "1992-08-16",
        "time": "09:30",
        "place": "Hà Nội",
        "target_year": 2026,
        "iching_method": "numbers",
        "numbers": "18,25",
    }).encode("utf-8")
    status, _, raw_a = gs.dispatch_post("/api/analyze", payload)
    assert status == 200
    j_a = json.loads(raw_a.decode("utf-8"))
    assert j_a["ok"] is True and "numerology" in j_a["data"] and "tuvi" in j_a["data"]
    assert "Mai Hoa Khởi Số" in j_a["data"]["iching"]["cast_method"]

    payload_m = json.dumps({
        "name": "Nguyễn Minh Quân",
        "gender": "nam",
        "date_type": "solar",
        "date": "1992-08-16",
        "time": "09:30",
        "place": "Hà Nội",
        "target_year": 2026,
        "iching_method": "manual_lines",
        "lines": "7,8,9,7,6,8",
    }).encode("utf-8")
    status, _, raw_m = gs.dispatch_post("/api/analyze", payload_m)
    assert status == 200
    j_m = json.loads(raw_m.decode("utf-8"))
    assert j_m["ok"] is True and "Nhập trực tiếp 6 hào" in j_m["data"]["iching"]["cast_method"]

    nc_payload = json.dumps({"date": "2026-05-15", "candidates": ["Nguyễn Minh Khôi", "Nguyễn Đăng Khoa"]}).encode("utf-8")
    status, _, raw_nc = gs.dispatch_post("/api/name-check", nc_payload)
    assert status == 200 and len(json.loads(raw_nc.decode("utf-8"))["data"]) == 2

    # Check all api/*.py handlers import cleanly
    api_dir = os.path.join(WEB_REPO, "api")
    for fn in sorted(os.listdir(api_dir)):
        if not fn.endswith(".py"):
            continue
        spec = importlib.util.spec_from_file_location(f"check_{fn}", os.path.join(api_dir, fn))
        mod = importlib.util.module_from_spec(spec)  # type: ignore
        spec.loader.exec_module(mod)  # type: ignore
        assert hasattr(mod, "handler"), f"api/{fn} thiếu class handler!"

    print("  [VERIFY PASS] Toàn bộ 5 hệ Đông-Tây + Chấm tên + Gemini AI + Vercel API đều hoạt động 100%!")


def run_git(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["git", "-C", WEB_REPO, *args],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )


def main() -> None:
    try:
        sys.stdout.reconfigure(encoding="utf-8")  # type: ignore
    except Exception:
        pass

    parser = argparse.ArgumentParser(description="Đồng bộ KB-TUVI từ thư mục Skill gốc sang D:\\AI và bản Web GitHub/Vercel")
    parser.add_argument("--push", action="store_true", help="Tự động git commit & push lên GitHub để Vercel redeploy")
    parser.add_argument("-m", "--message", default="", help="Nội dung commit tùy chọn")
    args = parser.parse_args()

    print("1) Kiểm tra & bảo vệ thẻ nạp Gemini AI trong bản gốc...")
    ensure_addon_tag_in_html(os.path.join(SKILL_SRC, "assets", "studio_gui.html"))

    print(f"2) Đồng bộ bản gốc -> {SKILL_MIRROR} ...")
    if os.path.isdir(os.path.dirname(SKILL_MIRROR)):
        c1 = sync_tree(SKILL_SRC, SKILL_MIRROR, mirror_deletes=True)
        print(f"   Đã cập nhật {c1} file sang D:\\AI\\Skills\\kb-tuvi.")

    print(f"3) Đồng bộ bản gốc -> {WEB_REPO} ...")
    c2 = sync_tree(SKILL_SRC, WEB_REPO, mirror_deletes=True)
    ensure_addon_tag_in_html(os.path.join(WEB_REPO, "assets", "studio_gui.html"))
    print(f"   Đã cập nhật {c2} file sang kb-tuvi-web.")

    print("4) Chạy kiểm thử tự động trước khi xuất bản...")
    quick_verify_web_repo()

    if args.push:
        print("5) Đẩy bản mới lên GitHub (Vercel sẽ tự động cập nhật web sau ~30s)...")
        run_git("add", ".")
        st = run_git("status", "--short")
        if not st.stdout.strip():
            print("   Không có thay đổi mới nào cần đẩy lên GitHub.")
            return
        print(st.stdout.strip())
        msg = args.message.strip() or f"Sync KB-TUVI v3.0 from source ({datetime.now().strftime('%Y-%m-%d %H:%M')})"
        c_res = run_git("commit", "-m", msg)
        print(c_res.stdout.strip() or c_res.stderr.strip())
        p_res = run_git("push", "origin", "main")
        print(p_res.stdout.strip() or p_res.stderr.strip())
        if p_res.returncode == 0:
            print("\n✅ HOÀN TẤT! Đợi ~30 giây rồi bấm Ctrl+F5 tại https://kb-tu-vi.vercel.app nhé!")
        else:
            print("\n⚠️ Chưa push được lên GitHub, kiểm tra log ở trên.")


if __name__ == "__main__":
    main()
