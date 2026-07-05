# DevTrack - Development Activity Tracker
# Copyright (c) 2026 Ivan Timov. All rights reserved.
# Proprietary and confidential.

from plyer import notification
from src.config import Config


class Reminder:
    @staticmethod
    def fire():
        app_name = Config.get_tracked_app()
        try:
            notification.notify(
                title="DevTrack Reminder",
                message=f"Time to get back to {app_name or 'work'}!",
                app_name="DevTrack",
                timeout=10
            )
        except Exception:
            pass
