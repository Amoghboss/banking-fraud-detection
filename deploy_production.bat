@echo off
title Sentinel Production WSGI Deployment
color 0A
echo ======================================================================
echo    STARTING PRODUCTION WAITRESS WSGI SERVER (HIGH CONCURRENCY)
echo ======================================================================
echo.
echo [*] Working Directory: %~dp0
cd /d "%~dp0"
echo [*] Server Port: 5000 (Binding to 0.0.0.0 for Local & LAN Access)
echo [*] Default Login: admin / Admin@2026!
echo.
python wsgi.py
pause
