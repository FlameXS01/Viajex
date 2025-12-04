@echo off
chcp 65001 >nul
echo Verificando estructura del proyecto...
echo.

if not exist "main.py" (
    echo ERROR: No se encuentra main.py
    goto error
)

if not exist "core" (
    echo ERROR: No se encuentra carpeta core/
    goto error
)

if not exist "infrastructure" (
    echo ERROR: No se encuentra carpeta infrastructure/
    goto error
)

if not exist "presentation" (
    echo ERROR: No se encuentra carpeta presentation/
    goto error
)

if not exist "application" (
    echo ERROR: No se encuentra carpeta application/
    goto error
)

if not exist "config" (
    echo ERROR: No se encuentra carpeta config/
    goto error
)

echo Estructura del proyecto OK
echo.
echo Archivos Python encontrados:
dir /s /b *.py | find /c "/" >nul && echo ✅ Hay archivos Python

echo.
echo Presiona una tecla para compilar...
pause >nul

call compile_fixed.bat

:error
pause