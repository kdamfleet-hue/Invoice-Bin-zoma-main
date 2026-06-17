@echo off
chcp 65001 > nul
title Fleet Management System - BIN ZOMAH INTL.
color 0A

echo.
echo  ╔══════════════════════════════════════════╗
echo  ║   Fleet Management System - BIN ZOMAH   ║
echo  ╚══════════════════════════════════════════╝
echo.

:: Check if .env exists
if not exist ".env" (
    echo  [ERROR] ملف .env غير موجود!
    echo  انسخ .env.example الى .env واملا البيانات.
    echo.
    pause
    exit /b 1
)

:: Activate virtual environment if it exists
if exist "venv\Scripts\activate.bat" (
    echo  [INFO] تفعيل البيئة الافتراضية...
    call venv\Scripts\activate.bat
) else if exist ".venv\Scripts\activate.bat" (
    call .venv\Scripts\activate.bat
)

:: Install requirements if needed
echo  [INFO] التحقق من المكتبات...
python -m pip install -r requirements.txt -q --disable-pip-version-check

:: Start Flask
echo.
echo  [INFO] بدء تشغيل الخادم...
echo  [INFO] افتح المتصفح على: http://localhost:5000
echo  [INFO] اضغط Ctrl+C للإيقاف
echo.
python app.py

pause
