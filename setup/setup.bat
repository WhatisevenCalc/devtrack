@echo off
title DevTrack Setup — Copyright (c) 2026 Ivan Timov. All rights reserved.
setlocal enabledelayedexpansion

echo =============================================
echo  DevTrack — Development Activity Tracker
echo  Copyright (c) 2026 Ivan Timov
echo  All rights reserved.
echo =============================================
echo.

net session >nul 2>&1
if %errorlevel% neq 0 (
    echo [INFO] Requesting administrator privileges...
    powershell -Command "Start-Process '%~f0' -Verb RunAs"
    exit /b
)
cd /d "%~dp0"

set INSTALL_DIR=%ProgramFiles%\DevTrack
set EXISTING_INSTALL=0
if exist "%INSTALL_DIR%\DevTrack.exe" set EXISTING_INSTALL=1

if !EXISTING_INSTALL! equ 1 (
    echo [INFO] DevTrack is already installed at: !INSTALL_DIR!
    echo.
    tasklist /FI "IMAGENAME eq DevTrack.exe" 2>nul | find /I "DevTrack.exe" >nul
    if !errorlevel! equ 0 (
        echo [INFO] Stopping running DevTrack...
        taskkill /IM DevTrack.exe /F /T >nul 2>&1
        timeout /t 1 /nobreak >nul
    )
    echo   [U] Uninstall and reinstall
    echo   [O] Overwrite (keep settings)
    echo   [C] Cancel
    set choice=
    set /p choice=Type U, O, or C:
    if /i "!choice!"=="C" ( echo Setup cancelled. & pause & exit /b )
    if /i "!choice!"=="U" (
        rmdir /S /Q "!INSTALL_DIR!" >nul 2>&1
        if exist "%USERPROFILE%\Desktop\DevTrack.lnk" del "%USERPROFILE%\Desktop\DevTrack.lnk" >nul 2>&1
        if exist "%APPDATA%\Microsoft\Windows\Start Menu\Programs\DevTrack.lnk" del "%APPDATA%\Microsoft\Windows\Start Menu\Programs\DevTrack.lnk" >nul 2>&1
    )
    echo.
)

echo [1/5] Checking Python...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python not installed. Download from: https://www.python.org/downloads/
    pause & exit /b
)
for /f "tokens=2" %%v in ('python --version 2^>^&1') do set pyver=%%v
echo         Found Python !pyver!

echo [2/5] Installing packages...
python -m pip install --upgrade pip -q
python -m pip install PyQt6 pywin32 psutil plyer -q
if %errorlevel% neq 0 ( echo [ERROR] Package install failed. & pause & exit /b )
echo         Done.

echo [3/5] Installing DevTrack...
if not exist "%INSTALL_DIR%" mkdir "%INSTALL_DIR%"
xcopy /E /I /Y "%~dp0files\*" "%INSTALL_DIR%" >nul
echo         Installed to %INSTALL_DIR%

echo [4/5] Creating shortcuts...
set SCRIPT=%TEMP%\DevTrackShortcut.vbs
echo Set WshShell = WScript.CreateObject("WScript.Shell") > "%SCRIPT%"
echo Set sc = WshShell.CreateShortcut(WshShell.SpecialFolders("Desktop") ^& "\DevTrack.lnk") >> "%SCRIPT%"
echo sc.TargetPath = "%INSTALL_DIR%\DevTrack.exe" >> "%SCRIPT%"
echo sc.WorkingDirectory = "%INSTALL_DIR%" >> "%SCRIPT%"
echo sc.Description = "DevTrack — Development Activity Tracker" >> "%SCRIPT%"
echo sc.IconLocation = "%INSTALL_DIR%\DevTrack.exe, 0" >> "%SCRIPT%"
echo sc.Save >> "%SCRIPT%"
echo Set sc2 = WshShell.CreateShortcut(WshShell.SpecialFolders("StartMenu") ^& "\Programs\DevTrack.lnk") >> "%SCRIPT%"
echo sc2.TargetPath = "%INSTALL_DIR%\DevTrack.exe" >> "%SCRIPT%"
echo sc2.WorkingDirectory = "%INSTALL_DIR%" >> "%SCRIPT%"
echo sc2.Description = "DevTrack — Development Activity Tracker" >> "%SCRIPT%"
echo sc2.IconLocation = "%INSTALL_DIR%\DevTrack.exe, 0" >> "%SCRIPT%"
echo sc2.Save >> "%SCRIPT%"
cscript //nologo "%SCRIPT%"
del "%SCRIPT%"
echo         Done.

echo.
echo =============================================
echo  DevTrack installed successfully!
echo  Launch from Desktop shortcut or Start Menu.
echo =============================================
echo.
pause
