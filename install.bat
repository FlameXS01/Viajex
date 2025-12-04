@echo off
echo Instalando Dietas App...
echo.

:: Verificar si Python está instalado
python --version >nul 2>&1
if errorlevel 1 (
    echo Python no está instalado. Instalando Python...
    :: Descargar e instalar Python (ajusta la URL a la versión más reciente)
    powershell -Command "Invoke-WebRequest -Uri 'https://www.python.org/ftp/python/3.11.0/python-3.11.0-amd64.exe' -OutFile 'python_installer.exe'"
    echo Ejecutando instalador de Python...
    python_installer.exe /quiet InstallAllUsers=1 PrependPath=1
    echo Esperando a que Python se instale...
    timeout /t 10
)

:: Instalar dependencias
echo Instalando dependencias...
pip install -r requirements.txt

:: Compilar la aplicación
echo Compilando aplicación...
python build.py

echo.
echo ¡Instalación completada!
echo El ejecutable se encuentra en la carpeta 'dist'
echo.
pause