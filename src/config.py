# DevTrack - Development Activity Tracker
# Copyright (c) 2026 Ivan Timov. All rights reserved.
# Proprietary and confidential.

from src.database import db


class Config:
    TRACKED_APP_KEY = "tracked_app"
    REMINDER_INTERVAL_KEY = "reminder_interval"
    DEFAULT_REMINDER_INTERVAL = "300"

    @staticmethod
    def get_tracked_app() -> str:
        return db.get_setting(Config.TRACKED_APP_KEY, "")

    @staticmethod
    def set_tracked_app(app_name: str):
        db.set_setting(Config.TRACKED_APP_KEY, app_name)

    @staticmethod
    def get_reminder_interval() -> int:
        val = db.get_setting(Config.REMINDER_INTERVAL_KEY, Config.DEFAULT_REMINDER_INTERVAL)
        return int(val)

    @staticmethod
    def set_reminder_interval(seconds: int):
        db.set_setting(Config.REMINDER_INTERVAL_KEY, str(seconds))