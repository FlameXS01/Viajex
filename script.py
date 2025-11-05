import pandas as pd
import sys
import os
from core.use_cases.department.create_department import CreateDepartmentUseCase
from application.dtos.department_dtos import DepartmentCreateDTO
from infrastructure.database.session import get_db

def main():
    # Leer el archivo Excel
    df = pd.read_excel("Files/Maestro de trabajadores cierre septiembre.xlsx", skiprows=3)
    dirty_unidades = df['Unidad'].value_counts()  
    unidades = []
    for value, unidad in enumerate(dirty_unidades.index):
        unidades.append(unidad)

    # Obtener la sesión de base de datos (depende de tu configuración)
    db = next(get_db())

    # Inicializar el use case con sus dependencias (esto puede variar en tu app)
    # Asumiendo que tienes una función que te da el use case:
    create_department_use_case = CreateDepartmentUseCase(
        department_repository=...  # Aquí debes inyectar el repositorio
    )

    # Otra opción: si tienes un contenedor de dependencias o una fábrica, úsalo.

    # Crear departamentos
    for unidad_nombre in unidades:
        # Crear el DTO
        department_dto = DepartmentCreateDTO(name=unidad_nombre)
        
        # Llamar al use case
        try:
            result = create_department_use_case.execute(department_dto)
            print(f"Departamento creado: {unidad_nombre}")
        except Exception as e:
            print(f"Error al crear el departamento {unidad_nombre}: {e}")

if __name__ == "__main__":
    main()