# -*- coding: utf-8 -*-
"""
api/index.py — Vercel Python Serverless Entrypoint cho KB-TUVI Web Studio.
Sử dụng trực tiếp BaseHTTPRequestHandler chuẩn của Vercel Python Runtime (Zero-Dependency).
"""

from __future__ import annotations
import os
import sys

API_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(API_DIR)
SCRIPTS_DIR = os.path.join(PROJECT_ROOT, "scripts")

if SCRIPTS_DIR not in sys.path:
    sys.path.insert(0, SCRIPTS_DIR)

from gui_server import StudioRequestHandler


class handler(StudioRequestHandler):
    """Vercel tự động gọi class `handler` kế thừa BaseHTTPRequestHandler."""
    pass
