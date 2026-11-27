# -*- coding: utf-8 -*-
"""Vercel Serverless Endpoint: POST /api/numerology"""

from __future__ import annotations
import os
import sys

SCRIPTS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "scripts")
if SCRIPTS_DIR not in sys.path:
    sys.path.insert(0, SCRIPTS_DIR)

from gui_server import StudioRequestHandler, dispatch_post


class handler(StudioRequestHandler):
    def do_POST(self) -> None:
        length = int(self.headers.get("Content-Length", "0") or "0")
        body = self.rfile.read(length) if length > 0 else b"{}"
        status, content_type, raw = dispatch_post(
            "/api/numerology", body, self.headers, client_ip=self._extract_client_ip()
        )
        self._write_response(status, content_type, raw)
