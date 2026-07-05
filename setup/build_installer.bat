@echo off
title DevTrack Installer Builder — Copyright (c) 2026 Ivan Timov. All rights reserved.
cd /d "%~dp0"

echo =============================================
echo  DevTrack Installer Builder
echo =============================================
echo.

set ISCC=
for %%X in (iscc.exe) do (set ISCC=%%~$PATH:X)
if not defined ISCC (
    if exist "%ProgramFiles(x86)%\Inno Setup 6\iscc.exe" set ISCC="%ProgramFiles(x86)%\Inno Setup 6\iscc.exe"
    if exist "%ProgramFiles%\Inno Setup 6\iscc.exe" set ISCC="%ProgramFiles%\Inno Setup 6\iscc.exe"
)
if not defined ISCC (
    echo [1/2] Downloading Inno Setup...
    powershell -Command "[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; Invoke-WebRequest -Uri 'https://jrsoftware.org/download.php/is.exe' -OutFile '%TEMP%\innosetup.exe' -UseBasicParsing"
    start /wait "" "%TEMP%\innosetup.exe" /VERYSILENT /SUPPRESSMSGBOXES /DIR="%ProgramFiles%\Inno Setup 6"
    set ISCC="%ProgramFiles%\Inno Setup 6\iscc.exe"
)
echo [2/2] Compiling installer...
%ISCC% installer.iss
if %errorlevel% neq 0 ( echo [ERROR] Compilation failed. & pause & exit /b )
echo.
echo =============================================
echo  Built: setup\output\DevTrack_Installer_v1.0.exe
echo =============================================
echo.
pause
