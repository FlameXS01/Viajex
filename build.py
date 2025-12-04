import os
import sys
import subprocess
from pathlib import Path

def build_app():
    current_dir = Path(__file__).parent
    app_name = "DietasApp"
    main_script = "main.py"
    
    # Opciones de PyInstaller SIN ICONO
    opts = [
        "pyinstaller",
        "--onefile",
        "--windowed",
        "--name", app_name,
        "--clean",
        "--noconfirm",
        "--add-data", f"core{os.pathsep}core",
        "--add-data", f"infrastructure{os.pathsep}infrastructure", 
        "--add-data", f"presentation{os.pathsep}presentation",
        "--add-data", f"application{os.pathsep}application",
        "--add-data", f"config{os.pathsep}config",
        "--hidden-import=tkinter",
        "--hidden-import=sqlalchemy",
        "--hidden-import=sqlalchemy.dialects.mysql",
        "--hidden-import=pymysql",
        "--hidden-import=bcrypt",
        "--hidden-import=email",
        "--hidden-import=email.mime",
        "--hidden-import=email.mime.text",
        "--hidden-import=email.mime.multipart",
        "--hidden-import=pandas",
        "--hidden-import=openpyxl",
        "--hidden-import=numpy",
        main_script
    ]
    
    # Ejecutar PyInstaller
    try:
        subprocess.run(opts, check=True)
        print("¡Compilación exitosa!")
    except subprocess.CalledProcessError as e:
        print(f"Error en la compilación: {e}")
        sys.exit(1)

if __name__ == "__main__":
    build_app()