# DevTrack - Development Activity Tracker
# Copyright (c) 2026 Ivan Timov. All rights reserved.
# Proprietary and confidential.

import sys, os
from datetime import datetime
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QLabel, QLineEdit, QPushButton,
                             QSystemTrayIcon, QMenu, QMessageBox,
                             QStyle, QFrame, QGraphicsDropShadowEffect)
from PyQt6.QtCore import QTimer, Qt
from PyQt6.QtGui import QAction, QColor, QPainter, QBrush, QRadialGradient, QPen, QIntValidator, QIcon
from src.database import db
from src.tracker import get_active_window_info, get_process_list
from src.config import Config
from src.reminder import Reminder


BG = "#0a0a0a"
CARD = "#111111"
RED = "#cc0000"
RED_LIGHT = "#ff1a1a"
RED_DARK = "#880000"
TEXT = "#e0e0e0"
TEXT_DIM = "#884444"
BORDER = "#220000"


class StatusDot(QLabel):
    def __init__(self, color="#444", size=14):
        super().__init__()
        self._color = color
        self._size = size
        self.setFixedSize(size + 4, size + 4)

    def set_color(self, color):
        self._color = color
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        gradient = QRadialGradient(self.width() / 2, self.height() / 2, self._size / 2)
        gradient.setColorAt(0, QColor(self._color))
        gradient.setColorAt(0.7, QColor(self._color).lighter(120))
        gradient.setColorAt(1, QColor(self._color).darker(140))
        painter.setBrush(QBrush(gradient))
        pen = QPen(QColor(self._color).lighter(150), 1)
        painter.setPen(pen)
        offset = (self.width() - self._size) / 2
        painter.drawEllipse(int(offset), int(offset), self._size, self._size)


class DevTrackWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self._tracking = False
        self._current_session_id = None
        self._idle_seconds = 0
        self._was_active = False

        self._tick_timer = QTimer()
        self._tick_timer.setInterval(1000)
        self._tick_timer.timeout.connect(self._tick)

        self._reminder_timer = QTimer()
        self._reminder_timer.setInterval(5000)
        self._reminder_timer.timeout.connect(self._check_reminder)

        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        self._init_ui()
        self._init_tray()
        self._load_settings()

    def _get_icon_path(self, name="clock.ico"):
        if getattr(sys, 'frozen', False):
            return os.path.join(sys._MEIPASS, "resources", name)
        return os.path.join(os.path.dirname(os.path.dirname(__file__)), "resources", name)

    def _init_ui(self):
        self.setMinimumSize(420, 460)
        self.setMaximumSize(500, 520)

        outer = QWidget()
        outer.setObjectName("outer")
        outer.setStyleSheet("QWidget#outer { background: transparent; }")
        self.setCentralWidget(outer)
        root = QVBoxLayout(outer)
        root.setContentsMargins(0, 0, 0, 0)

        container = QFrame()
        container.setObjectName("container")
        container.setStyleSheet(f"""
            QFrame#container {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 {BG}, stop:1 #0f0000);
                border: 1px solid {BORDER};
                border-radius: 14px;
            }}
        """)
        root.addWidget(container)

        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(40)
        shadow.setColor(QColor(0, 0, 0, 200))
        shadow.setOffset(0, 8)
        container.setGraphicsEffect(shadow)

        layout = QVBoxLayout(container)
        layout.setContentsMargins(18, 10, 18, 12)
        layout.setSpacing(8)

        title_row = QHBoxLayout()
        title_row.setContentsMargins(4, 0, 0, 2)
        title_label = QLabel("DevTrack")
        title_label.setStyleSheet(f"font-size: 17px; font-weight: 700; color: {RED}; background: transparent;")
        title_row.addWidget(title_label)
        title_row.addStretch()
        self._title_status = QLabel("Idle")
        self._title_status.setStyleSheet(f"font-size: 9px; color: {TEXT_DIM}; background: transparent; padding: 2px 8px;")
        title_row.addWidget(self._title_status)
        min_btn = QPushButton("—")
        min_btn.setFixedSize(24, 24)
        min_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        min_btn.setToolTip("Minimize to tray")
        min_btn.clicked.connect(self.hide)
        min_btn.setStyleSheet(f"""
            QPushButton {{ background: transparent; border: none; font-size: 13px; color: {TEXT_DIM}; font-weight: bold; }}
            QPushButton:hover {{ color: white; background: {BORDER}; border-radius: 12px; }}
        """)
        title_row.addWidget(min_btn)
        exit_btn = QPushButton("✕")
        exit_btn.setFixedSize(24, 24)
        exit_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        exit_btn.setToolTip("Exit DevTrack")
        exit_btn.clicked.connect(self._force_quit)
        exit_btn.setStyleSheet(f"""
            QPushButton {{ background: transparent; border: none; font-size: 11px; color: {TEXT_DIM}; }}
            QPushButton:hover {{ color: white; background: {RED}; border-radius: 12px; }}
        """)
        title_row.addWidget(exit_btn)
        layout.addLayout(title_row)

        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet(f"background: {BORDER}; max-height: 1px;")
        layout.addWidget(sep)

        status_card = QFrame()
        status_card.setStyleSheet(f"""
            QFrame {{ background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 {CARD}, stop:1 #1a0000); border: 1px solid {BORDER}; border-radius: 10px; }}
        """)
        sl = QVBoxLayout(status_card)
        sl.setSpacing(5)
        sl.setContentsMargins(12, 8, 12, 8)
        st = QHBoxLayout()
        self._status_dot = StatusDot("#444")
        st.addWidget(self._status_dot)
        self._status_label = QLabel("Not tracking")
        self._status_label.setStyleSheet(f"font-size: 13px; font-weight: 600; color: {TEXT_DIM}; background: transparent;")
        st.addWidget(self._status_label)
        st.addStretch()
        sl.addLayout(st)
        self._app_label = QLabel("Current window: —")
        self._app_label.setStyleSheet(f"font-size: 10px; color: {TEXT_DIM}; background: transparent;")
        sl.addWidget(self._app_label)
        tr = QHBoxLayout()
        self._timer_label = QLabel("00:00:00")
        self._timer_label.setStyleSheet(f"font-size: 28px; font-weight: 300; color: {TEXT}; background: transparent; letter-spacing: 2px; font-family: 'Segoe UI', monospace;")
        tr.addWidget(self._timer_label)
        tr.addStretch()
        tf = QFrame()
        tf.setStyleSheet(f"background: #1a0000; border: 1px solid {BORDER}; border-radius: 6px;")
        tl = QVBoxLayout(tf)
        tl.setSpacing(0)
        tl.setContentsMargins(8, 3, 8, 3)
        tls = QLabel("TOTAL")
        tls.setStyleSheet(f"font-size: 7px; color: {TEXT_DIM}; background: transparent; letter-spacing: 1px;")
        tl.addWidget(tls)
        self._total_label = QLabel("0h 0m")
        self._total_label.setStyleSheet(f"font-size: 13px; font-weight: 700; color: #00ff00; background: transparent;")
        tl.addWidget(self._total_label)
        tr.addWidget(tf)
        sl.addLayout(tr)
        layout.addWidget(status_card)

        app_card = QFrame()
        app_card.setStyleSheet(f"QFrame {{ background: {CARD}; border: 1px solid {BORDER}; border-radius: 10px; }}")
        al = QVBoxLayout(app_card)
        al.setSpacing(6)
        al.setContentsMargins(12, 8, 12, 8)
        al_title = QLabel("Tracked Application")
        al_title.setStyleSheet(f"font-size: 11px; font-weight: 600; color: {TEXT_DIM}; background: transparent; letter-spacing: 0.5px;")
        al.addWidget(al_title)
        app_dropdown_row = QHBoxLayout()
        self._app_btn = QPushButton("Select app...")
        self._app_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._app_btn.setMinimumHeight(34)
        self._app_btn.clicked.connect(self._show_app_menu)
        self._app_btn.setStyleSheet(f"""
            QPushButton {{ background: {BG}; color: {TEXT}; border: 1px solid {BORDER}; border-radius: 6px; padding: 6px 10px; font-size: 12px; text-align: left; }}
            QPushButton:hover {{ border-color: {RED}; }}
        """)
        app_dropdown_row.addWidget(self._app_btn)
        self._refresh_btn = QPushButton("↻")
        self._refresh_btn.setFixedSize(34, 34)
        self._refresh_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._refresh_btn.setToolTip("Refresh process list")
        self._refresh_btn.clicked.connect(self._rebuild_app_menu)
        self._refresh_btn.setStyleSheet(f"""
            QPushButton {{ background: {BG}; color: {RED}; border: 1px solid {BORDER}; border-radius: 17px; font-size: 15px; }}
            QPushButton:hover {{ background: {BORDER}; border-color: {RED}; }}
        """)
        app_dropdown_row.addWidget(self._refresh_btn)
        al.addLayout(app_dropdown_row)

        rr = QHBoxLayout()
        rl = QLabel("Remind every")
        rl.setStyleSheet(f"font-size: 11px; color: {TEXT_DIM}; background: transparent;")
        rr.addWidget(rl)
        self._reminder_input = QLineEdit("5")
        self._reminder_input.setFixedWidth(70)
        self._reminder_input.setValidator(QIntValidator(1, 999))
        self._reminder_input.setStyleSheet(f"""
            QLineEdit {{ background: {BG}; color: {TEXT}; border: 1px solid {BORDER}; border-radius: 6px; padding: 5px 8px; font-size: 12px; }}
            QLineEdit:focus {{ border-color: {RED}; }}
        """)
        rr.addWidget(self._reminder_input)
        min_label = QLabel("min")
        min_label.setStyleSheet(f"font-size: 11px; color: {TEXT_DIM}; background: transparent;")
        rr.addWidget(min_label)
        rr.addStretch()
        al.addLayout(rr)
        layout.addWidget(app_card)

        cl = QHBoxLayout()
        cl.setSpacing(8)
        cl.setContentsMargins(0, 2, 0, 0)
        self._toggle_btn = QPushButton("Start Tracking")
        self._toggle_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._toggle_btn.setMinimumHeight(36)
        self._toggle_btn.clicked.connect(self._toggle_tracking)
        self._toggle_btn.setStyleSheet(f"""
            QPushButton {{ background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #00cc00, stop:1 #00ff00); color: white; font-size: 13px; font-weight: 700; border: none; border-radius: 8px; padding: 8px 16px; }}
            QPushButton:hover {{ background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #00e600, stop:1 #33ff33); }}
            QPushButton:pressed {{ background: #009900; }}
            QPushButton:disabled {{ background: #1a0000; color: #441111; }}
        """)
        cl.addWidget(self._toggle_btn)
        self._stats_btn = QPushButton("Stats")
        self._stats_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._stats_btn.setMinimumHeight(36)
        self._stats_btn.clicked.connect(self._show_stats)
        self._stats_btn.setStyleSheet(f"""
            QPushButton {{ background: {CARD}; color: {RED}; font-size: 11px; font-weight: 600; border: 1px solid {BORDER}; border-radius: 8px; padding: 8px 12px; }}
            QPushButton:hover {{ background: {BORDER}; border-color: {RED}; }}
        """)
        cl.addWidget(self._stats_btn)
        self._clear_btn = QPushButton("Clear")
        self._clear_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._clear_btn.setMinimumHeight(36)
        self._clear_btn.clicked.connect(self._clear_stats)
        self._clear_btn.setStyleSheet(f"""
            QPushButton {{ background: transparent; color: {TEXT_DIM}; font-size: 10px; font-weight: 500; border: 1px solid {BORDER}; border-radius: 8px; padding: 8px 10px; }}
            QPushButton:hover {{ color: {RED}; border-color: {RED}; background: rgba(204,0,0,0.08); }}
        """)
        cl.addWidget(self._clear_btn)
        exit_btn2 = QPushButton("Exit")
        exit_btn2.setCursor(Qt.CursorShape.PointingHandCursor)
        exit_btn2.setMinimumHeight(36)
        exit_btn2.clicked.connect(self._force_quit)
        exit_btn2.setStyleSheet(f"""
            QPushButton {{ background: transparent; color: {TEXT_DIM}; font-size: 10px; font-weight: 500; border: 1px solid {BORDER}; border-radius: 8px; padding: 8px 10px; }}
            QPushButton:hover {{ color: {RED}; border-color: {RED}; background: rgba(204,0,0,0.08); }}
        """)
        cl.addWidget(exit_btn2)
        layout.addLayout(cl)

        cr = QLabel("Copyright © 2026 Ivan Timov. All rights reserved.")
        cr.setAlignment(Qt.AlignmentFlag.AlignCenter)
        cr.setStyleSheet(f"font-size: 8px; color: #331111; background: transparent; padding-top: 4px;")
        layout.addWidget(cr)

        self._app_menu = QMenu()
        self._rebuild_app_menu()

    def _rebuild_app_menu(self):
        self._app_menu.clear()
        self._app_menu.setStyleSheet(f"""
            QMenu {{ background: {BG}; color: {TEXT}; border: 1px solid {RED_DARK}; border-radius: 6px; padding: 4px; }}
            QMenu::item {{ padding: 6px 18px; border-radius: 4px; font-size: 11px; }}
            QMenu::item:selected {{ background: {BORDER}; color: {RED}; }}
            QMenu::separator {{ height: 1px; background: {BORDER}; margin: 4px 8px; }}
        """)
        processes = get_process_list()
        if not processes:
            self._app_menu.addAction("(no processes found)").setEnabled(False)
        else:
            current = Config.get_tracked_app()
            for p in processes:
                act = self._app_menu.addAction(p)
                act.setCheckable(True)
                act.setChecked(p == current)
                act.triggered.connect(lambda checked, name=p: self._select_app(name))
        self._app_menu.addSeparator()
        refresh_act = self._app_menu.addAction("↻ Refresh list")
        refresh_act.triggered.connect(self._rebuild_app_menu)

    def _show_app_menu(self):
        self._rebuild_app_menu()
        self._app_menu.exec(self._app_btn.mapToGlobal(self._app_btn.rect().bottomLeft()))

    def _select_app(self, name):
        Config.set_tracked_app(name)
        self._app_btn.setText(name)
        self._rebuild_app_menu()

    def _init_tray(self):
        self._tray_icon = QSystemTrayIcon(self)
        icon = QIcon(self._get_icon_path())
        self._tray_icon.setIcon(icon)
        self.setWindowIcon(icon)
        self._tray_icon.setToolTip("DevTrack")
        tray_menu = QMenu()
        tray_menu.setStyleSheet(f"""
            QMenu {{ background: {BG}; color: {TEXT}; border: 1px solid {RED_DARK}; border-radius: 7px; padding: 4px; }}
            QMenu::item {{ padding: 5px 18px; border-radius: 4px; font-size: 11px; }}
            QMenu::item:selected {{ background: {BORDER}; color: {RED}; }}
            QMenu::separator {{ height: 1px; background: {BORDER}; margin: 3px 8px; }}
        """)
        show_action = QAction("Show DevTrack", self)
        show_action.triggered.connect(self.show)
        tray_menu.addAction(show_action)
        self._tray_toggle = QAction("Start Tracking", self)
        self._tray_toggle.triggered.connect(self._toggle_tracking)
        tray_menu.addAction(self._tray_toggle)
        tray_menu.addSeparator()
        quit_action = QAction("Exit DevTrack", self)
        quit_action.triggered.connect(self._force_quit)
        tray_menu.addAction(quit_action)
        self._tray_icon.setContextMenu(tray_menu)
        self._tray_icon.activated.connect(self._tray_activated)
        self._tray_icon.show()

    def _tray_activated(self, reason):
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            self.show()
            self.raise_()

    def _load_settings(self):
        app = Config.get_tracked_app()
        if app:
            self._app_btn.setText(app)
        interval = Config.get_reminder_interval()
        self._reminder_input.setText(str(interval // 60 if interval >= 60 else 5))

    def _get_reminder_interval(self):
        try:
            return max(1, int(self._reminder_input.text())) * 60
        except ValueError:
            return 300

    def _toggle_tracking(self):
        if self._tracking:
            self._stop_tracking()
        else:
            self._start_tracking()

    def _start_tracking(self):
        app = Config.get_tracked_app()
        if not app:
            QMessageBox.warning(self, "Warning", "Select an app from the dropdown menu first.")
            return
        Config.set_reminder_interval(self._get_reminder_interval())
        self._tracking = True
        self._idle_seconds = 0
        self._was_active = False
        self._toggle_btn.setText("■ Stop")
        self._tray_toggle.setText("Stop Tracking")
        self._app_btn.setEnabled(False)
        self._refresh_btn.setEnabled(False)
        self._reminder_input.setEnabled(False)
        self._tick_timer.start()
        self._reminder_timer.start()

    def _stop_tracking(self):
        self._tracking = False
        if self._current_session_id:
            db.end_session(self._current_session_id)
            self._current_session_id = None
        self._tick_timer.stop()
        self._reminder_timer.stop()
        self._idle_seconds = 0
        self._toggle_btn.setText("Start Tracking")
        self._tray_toggle.setText("Start Tracking")
        self._app_btn.setEnabled(True)
        self._refresh_btn.setEnabled(True)
        self._reminder_input.setEnabled(True)
        self._tick()

    def _tick(self):
        app = Config.get_tracked_app()
        active_app, active_title = get_active_window_info()
        total = db.get_total_time(app)
        hours = total // 3600
        mins = (total % 3600) // 60
        self._total_label.setText(f"{hours}h {mins}m")
        if not self._tracking:
            self._status_dot.set_color("#444")
            self._status_label.setText("Not tracking")
            self._status_label.setStyleSheet(f"font-size: 13px; font-weight: 600; color: {TEXT_DIM}; background: transparent;")
            self._title_status.setText("Idle")
            self._app_label.setText("Current window: —")
            self._timer_label.setText("00:00:00")
            return
        if active_app:
            self._app_label.setText(f"Current window: {active_app} - {active_title[:50]}")
        is_active = active_app and active_app.lower() == app.lower()
        if is_active:
            if not self._was_active:
                self._current_session_id = db.start_session(app, active_title)
                self._was_active = True
            self._status_dot.set_color("#00ff00")
            self._status_label.setText(f"● Active — {app}")
            self._status_label.setStyleSheet(f"font-size: 13px; font-weight: 600; color: #00ff00; background: transparent;")
            self._title_status.setText("● Tracking")
        else:
            if self._was_active:
                if self._current_session_id:
                    db.end_session(self._current_session_id)
                    self._current_session_id = None
                self._was_active = False
            self._status_dot.set_color(RED_DARK)
            self._status_label.setText(f"◌ Paused — {app}")
            self._status_label.setStyleSheet(f"font-size: 13px; font-weight: 600; color: {RED_DARK}; background: transparent;")
            self._title_status.setText("◌ Paused")
        if self._current_session_id:
            session = db.get_active_session(app)
            if session:
                start = datetime.fromisoformat(session["start_time"])
                elapsed = int((datetime.now() - start).total_seconds())
                self._timer_label.setText(f"{elapsed // 3600:02d}:{(elapsed % 3600) // 60:02d}:{elapsed % 60:02d}")

    def _check_reminder(self):
        if self._was_active:
            self._idle_seconds = 0
            return
        self._idle_seconds += 5
        if self._idle_seconds >= Config.get_reminder_interval():
            self._idle_seconds = 0
            Reminder.fire()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_pos = event.globalPosition().toPoint()
            self._drag_offset = self._drag_pos - self.frameGeometry().topLeft()
            super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.MouseButton.LeftButton and hasattr(self, '_drag_offset'):
            self.move(event.globalPosition().toPoint() - self._drag_offset)
            event.accept()

    def closeEvent(self, event):
        event.ignore()
        self.hide()
        self._tray_icon.showMessage("DevTrack", "Minimized to tray. Use Exit to quit.", QSystemTrayIcon.MessageIcon.Information, 3000)

    def _force_quit(self):
        if self._tracking:
            self._stop_tracking()
        self._tray_icon.hide()
        QApplication.instance().quit()

    def _clear_stats(self):
        reply = QMessageBox.question(self, "Clear Data", "Delete all tracked session data?\nThis cannot be undone.", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            db.clear_sessions()
            self._tick()

    def _show_stats(self):
        app = Config.get_tracked_app()
        sessions = db.get_sessions(app, limit=20)
        total = db.get_total_time(app)
        total_h = total // 3600
        total_m = (total % 3600) // 60
        lines = [f"Total tracked: {total_h}h {total_m}m", ""]
        for s in sessions:
            dur = s["duration_seconds"]
            h = dur // 3600
            m = (dur % 3600) // 60
            sec = dur % 60
            lines.append(f"{s['start_time'][:19]}  →  {h:02d}:{m:02d}:{sec:02d}")
            if s["window_title"]:
                lines[-1] += f"  [{s['window_title'][:40]}]"
        msg = QMessageBox(self)
        msg.setWindowTitle("Session History")
        msg.setText("\n".join(lines) or "No sessions yet.")
        msg.setStyleSheet(f"""
            QMessageBox {{ background: {BG}; color: {TEXT}; }}
            QLabel {{ color: {TEXT}; font-size: 10px; font-family: monospace; }}
            QPushButton {{ background: {RED}; color: white; border: none; border-radius: 5px; padding: 5px 16px; font-size: 10px; }}
            QPushButton:hover {{ background: {RED_LIGHT}; }}
        """)
        msg.exec()
