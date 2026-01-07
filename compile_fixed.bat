@echo off
chcp 65001 >nul
echo Compilando Dietas App...
echo.

:: Verificar Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python no está instalado o no está en el PATH.
    echo Por favor, instala Python 3.8+ desde https://www.python.org/
    pause
    exit /b 1
)

:: Verificar estructura básica
if not exist "main.py" (
    echo ERROR: No se encuentra main.py
    pause
    exit /b 1
)

:: Verificar dependencias
echo Verificando dependencias...
pip install -r requirements.txt >nul 2>&1
if errorlevel 1 (
    echo Advertencia: No se pudo instalar dependencias automáticamente.
    echo Por favor, ejecuta manualmente: pip install -r requirements.txt
)

:: Cerrar la aplicación si está en ejecución
echo Cerrando aplicación si está abierta...
taskkill /f /im VIAJEX.exe >nul 2>&1
timeout /t 2 >nul

:: Limpiar compilaciones anteriores
if exist "build" rmdir /s /q "build"
if exist "dist" rmdir /s /q "dist"
if exist "VIAJEX.spec" del "VIAJEX.spec"

:: Compilar
echo Compilando aplicación...
pyinstaller --onefile --windowed --name "VIAJEX" ^
--icon "icon.ico" ^
--add-data "core;core" ^
--add-data "infrastructure;infrastructure" ^
--add-data "presentation;presentation" ^
--add-data "application;application" ^
--add-data "config;config" ^
--hidden-import=tkinter ^
--hidden-import=sqlalchemy ^
--hidden-import=sqlalchemy.dialects.mysql ^
--hidden-import=pymysql ^
--hidden-import=bcrypt ^
--hidden-import=email ^
--hidden-import=email.mime ^
--hidden-import=email.mime.text ^
--hidden-import=email.mime.multipart ^
--hidden-import=pandas ^
--hidden-import=openpyxl ^
--hidden-import=numpy ^
--clean ^
--noconfirm ^
main.py

if exist "dist\VIAJEX.exe" (
    echo.
    echo ¡COMPILACIÓN EXITOSA!
    echo Ejecutable creado en: dist\VIAJEX.exe
    echo.
    echo Para ejecutar: dist\VIAJEX.exe
) else (
    echo.
    echo ERROR: No se pudo crear el ejecutable
)

echo.
pause