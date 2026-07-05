@echo off
setlocal enabledelayedexpansion
title Push DevTrack to GitHub
cd /d "%~dp0"

echo =============================================
echo  Pushing DevTrack to GitHub
echo =============================================
echo.

where git >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Git is not installed. Download from: https://git-scm.com/downloads
    pause
    exit /b
)

if not exist ".git" (
    echo [1/4] Initializing Git repository...
    git init
) else (
    echo [1/4] Git repository already initialized.
)

echo [2/4] Adding files to Git...
git add .
if %errorlevel% neq 0 ( echo [ERROR] Failed to add files. & pause & exit /b )

echo [3/4] Committing files...
git diff --cached --quiet
if %errorlevel% equ 0 (
    echo         No changes to commit.
) else (
    git commit -m "Initial commit — DevTrack v1.0"
    if %errorlevel% neq 0 ( echo [ERROR] Commit failed. Check your Git configuration. & pause & exit /b )
    echo         Commit successful.
)

echo [4/4] Pushing to GitHub...
git remote remove origin >nul 2>&1
git remote add origin https://github.com/WhatisevenCalc/devtrack.git
git branch -M main

echo         Pushing to remote...
call :PushWithFallback main

if %errorlevel% neq 0 (
    echo.
    echo [ERROR] Could not push to GitHub.
    echo.
    echo   Manual steps:
    echo     1. git pull --rebase origin main
    echo     2. git push -u origin main
    echo.
    pause
    exit /b
)

goto :Success

:PushWithFallback
git push -u origin %1
if %errorlevel% equ 0 exit /b 0

:: Check if rejection was due to remote having existing commits
echo         Checking rejection reason...
git ls-remote origin HEAD >nul 2>&1
if %errorlevel% equ 0 (
    echo         Remote has existing commits. Pulling and rebasing...
    git pull --rebase origin %1
    if %errorlevel% equ 0 (
        git push -u origin %1
        if !errorlevel! equ 0 exit /b 0
    )
)

:: Force push as last resort
echo         Forcing push...
git push --force -u origin %1
exit /b %errorlevel%

:Success

echo.
echo =============================================
echo  Successfully pushed to GitHub!
echo  https://github.com/WhatisevenCalc/devtrack
echo =============================================
echo.
pause
