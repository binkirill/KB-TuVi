@echo off
chcp 65001 >nul
cd /d "%~dp0"
python -X utf8 scripts\gui_server.py --port 8765
pause
