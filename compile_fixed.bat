@echo off
chcp 65001 >nul
echo Compilando Dietas App (versión corregida)...
echo.

:: Verificar Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python no está instalado o no está en el PATH.
    pause
    exit /b 1
)

:: Limpiar compilaciones anteriores
if exist "build" rmdir /s /q "build"
if exist "dist" rmdir /s /q "dist"
if exist "DietasApp.spec" del "DietasApp.spec"

:: Compilar directamente
pyinstaller --onefile --windowed --name "DietasApp" ^
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
main.py

if exist "dist\DietasApp.exe" (
    echo.
    echo ¡COMPILACIÓN EXITOSA!
    echo Ejecutable creado: dist\DietasApp.exe
    echo Tamaño: 
    for %%F in (dist\DietasApp.exe) do echo   %%~zF bytes
) else (
    echo.
    echo ERROR: No se pudo crear el ejecutable
)

echo.
pause