@echo off
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
git commit -m "Initial commit — DevTrack v1.0"
if %errorlevel% neq 0 ( echo [ERROR] Commit failed. Check your Git configuration. & pause & exit /b )

echo [4/4] Pushing to GitHub...
git remote remove origin >nul 2>&1
git remote add origin https://github.com/WhatisevenCalc/devtrack.git
git branch -M main
git push -u origin main

if %errorlevel% neq 0 (
    echo.
    echo [ACTION REQUIRED] Push failed. You may need to authenticate.
    echo.
    echo   Option 1 — Personal Access Token:
    echo     git remote set-url origin https://YOUR_TOKEN@github.com/WhatisevenCalc/devtrack.git
    echo     git push -u origin main
    echo.
    echo   Option 2 — GitHub CLI:
    echo     gh auth login
    echo     git push -u origin main
    echo.
    pause
    exit /b
)

echo.
echo =============================================
echo  Successfully pushed to GitHub!
echo  https://github.com/WhatisevenCalc/devtrack
echo =============================================
echo.
pause
