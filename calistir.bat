@echo off
chcp 65001 > nul
title Turkce Ozel Isim Tanima

echo ============================================
echo   Turkce Ozel Isim Tanima - Baslatiliyor
echo ============================================
echo.

:: Bat dosyasinin bulundugu klasore git
cd /d "%~dp0"

:: ------------------------------------------------------------------
:: Python'u bul: once 'py' launcher, sonra 'python', sonra 'python3'
:: Son care: bilinen Microsoft Store / Windows Python yollarini tara
:: ------------------------------------------------------------------
set PYTHON_CMD=

:: 1) py launcher (Windows Python Launcher - en guvenilir)
set PY_LAUNCHER=%LOCALAPPDATA%\Microsoft\WindowsApps\PythonSoftwareFoundation.PythonManager_3847v3x7pw1km\py.exe
if exist "%PY_LAUNCHER%" (
    set PYTHON_CMD="%PY_LAUNCHER%"
    goto :python_found
)

:: 2) WindowsApps klasorundeki python.exe (eger stub degilse)
set WA_PYTHON=%LOCALAPPDATA%\Microsoft\WindowsApps\python.exe
if exist "%WA_PYTHON%" (
    "%WA_PYTHON%" --version > nul 2>&1
    if not errorlevel 1 (
        set PYTHON_CMD="%WA_PYTHON%"
        goto :python_found
    )
)

:: 3) PATH'deki python
python --version > nul 2>&1
if not errorlevel 1 (
    set PYTHON_CMD=python
    goto :python_found
)

:: 4) PATH'deki python3
python3 --version > nul 2>&1
if not errorlevel 1 (
    set PYTHON_CMD=python3
    goto :python_found
)

:: 5) Tipik kurulum klasorleri
for %%V in (313 314 312 311 310 39 38) do (
    if exist "%LOCALAPPDATA%\Programs\Python\Python%%V\python.exe" (
        set PYTHON_CMD="%LOCALAPPDATA%\Programs\Python\Python%%V\python.exe"
        goto :python_found
    )
)

echo [HATA] Python bulunamadi!
echo.
echo Lutfen asagidaki adimlardan birini yapiniz:
echo   1) https://python.org adresinden Python yukleyiniz
echo      (Kurulum sirasinda "Add Python to PATH" secenegini isaretleyiniz)
echo   2) Veya Microsoft Store'dan Python'u yukleyiniz
echo.
pause
exit /b 1

:python_found
echo [OK] Python bulundu: %PYTHON_CMD%

:: pip var mi kontrol et
%PYTHON_CMD% -m pip --version > nul 2>&1
if errorlevel 1 (
    echo [HATA] pip bulunamadi! Python kurulumunuzu kontrol edin.
    pause
    exit /b 1
)

:: Gerekli paketleri kur (ilk calistirmada)
echo [*] Gerekli kutuphaneler kontrol ediliyor...
%PYTHON_CMD% -m pip install -r requirements.txt --quiet
if errorlevel 1 (
    echo [UYARI] Bazi paketler yuklenemedi, devam ediliyor...
)

echo.
echo [*] Sunucu baslatiliyor... Lutfen bekleyin.
echo     Model ilk kez kullaniliyorsa indirme suresi uzun olabilir.
echo.
echo [*] Tarayici otomatik acilacak (uygulama hazir oldugunda).
echo.

:: Flask uygulamasini baslatiyoruz; app.py kendi tarayici aciyor
%PYTHON_CMD% app.py

:: Uygulama kapanirsa kullaniciya bildir
echo.
echo Uygulama kapatildi. Cikis icin bir tusa basin...
pause > nul
