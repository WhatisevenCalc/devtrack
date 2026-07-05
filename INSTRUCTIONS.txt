DevTrack - Development Activity Tracker
Copyright (c) 2026 Ivan Timov. All rights reserved.
====================================================

WHAT IT DOES
  DevTrack tracks how long you use a specific application.
  - Select an app (e.g. code.exe, chrome.exe) from the dropdown menu
  - Click "Start Tracking" — timer runs while that app is in focus
  - Timer pauses when you switch away, resumes when you return
  - After set idle time, a desktop notification reminds you to get back
  - All sessions logged to a local SQLite database (~/.devtrack/)

QUICK START (portable — no install needed)
  1. Run DevTrack.exe (right-click → Run as administrator)
  2. Click the app dropdown → pick a process from the menu
  3. Set reminder interval (minutes)
  4. Click "Start Tracking" (green button)
  5. Close window to minimize to tray; use Exit to fully quit
  6. Stats button shows session history; Clear button deletes all data

INSTALLER (recommended — one-click setup)
  1. Open the setup folder
  2. Double-click setup\output\DevTrack_Installer_v1.0.exe
  3. Follow the wizard (Next → Install → Finish)
  4. DevTrack is installed to Program Files with Desktop and Start Menu shortcuts

  The installer automatically:
  - Detects if DevTrack is already installed and asks to upgrade
  - Kills any running DevTrack process before installing
  - Installs required Python packages
  - Registers for clean uninstall via Windows Add/Remove Programs

  To build the installer from source:
    setup\build_installer.bat   (auto-downloads Inno Setup and compiles)

SYSTEM REQUIREMENTS
  - Windows 10 / 11 (64-bit)
  - Python 3.8+ (installed automatically via installer)
  - Administrator rights (required for process tracking)

FILES
  DevTrack.exe              — Standalone executable
  resources/branding/       — Marketing assets (logos, banners)
  src/                      — Python source code
  setup/                    — Installer builder and wizard script
  ~/.devtrack/devtrack.db   — Session database (auto-created)

MARKETING ASSETS (resources/branding/)
  Logo sizes: 16px to 512px (PNG)
  Banners: social (1200x630), Twitter (1024x500),
           presentation (800x600), thumbnail (400x300)
