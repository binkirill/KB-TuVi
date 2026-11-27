# -*- coding: utf-8 -*-
"""Vercel Serverless Endpoint: GET /api/health"""

from __future__ import annotations
import os
import sys

SCRIPTS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "scripts")
if SCRIPTS_DIR not in sys.path:
    sys.path.insert(0, SCRIPTS_DIR)

from gui_server import StudioRequestHandler, dispatch_get


class handler(StudioRequestHandler):
    def do_GET(self) -> None:
        status, content_type, raw = dispatch_get("/api/health")
        self._write_response(status, content_type, raw)
