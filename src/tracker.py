# DevTrack - Development Activity Tracker
# Copyright (c) 2026 Ivan Timov. All rights reserved.
# Proprietary and confidential.

import win32gui
import win32process
import psutil
from typing import Tuple, Optional


def get_active_window_info() -> Tuple[Optional[str], Optional[str]]:
    hwnd = win32gui.GetForegroundWindow()
    if not hwnd:
        return None, None
    try:
        window_title = win32gui.GetWindowText(hwnd)
        _, pid = win32process.GetWindowThreadProcessId(hwnd)
        process = psutil.Process(pid)
        app_name = process.name()
        return app_name, window_title
    except (psutil.NoSuchProcess, psutil.AccessDenied):
        return None, None


def get_process_list() -> list:
    processes = []
    for proc in psutil.process_iter(["pid", "name"]):
        try:
            info = proc.info
            if info["name"]:
                processes.append(info["name"])
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
    return sorted(set(processes))