@echo off
title Sentinel Banking Fraud Detection System
color 0B
echo ======================================================================
echo           SENTINEL BANKING FRAUD DETECTION SYSTEM
echo ======================================================================
echo.
echo [*] Checking Python environment...
python --version
echo.
echo [*] Launching Sentinel Server on http://127.0.0.1:5000 ...
echo [*] Login Credentials:
echo     Username: admin
echo     Password: Admin@2026!
echo.
echo Press CTRL+C to stop the server at any time.
echo ======================================================================
python app.py
pause
