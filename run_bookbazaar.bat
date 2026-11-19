@echo off
title BookBazaar - FYP Server Launcher
color 0A
echo ========================================================
echo   BookBazaar - Pakistan's Used Books Marketplace
echo   Starting Web Application Server...
echo ========================================================
echo.

cd /d "%~dp0"

echo [1/4] Ensuring PostgreSQL 18 is running...
netstat -ano | findstr ":5432 " >nul
if %errorlevel% neq 0 (
    echo [Info] Starting PostgreSQL daemon on port 5432...
    start /B "" "C:\Users\Microsoft\PostgreSQL\18\bin\postgres.exe" -D "C:\Users\Microsoft\PostgreSQL\18\data"
    timeout /t 3 /nobreak >nul
) else (
    echo [OK] PostgreSQL server is active and listening on port 5432.
)

echo.
echo [2/4] Checking Database Migrations...
python manage.py migrate --noinput

echo.
echo [3/4] Opening BookBazaar in your default web browser...
start http://127.0.0.1:8000/

echo.
echo [4/4] Starting Django Server at http://127.0.0.1:8000/
echo Press Ctrl + C to stop the server anytime.
echo ========================================================
python manage.py runserver 127.0.0.1:8000
pause
