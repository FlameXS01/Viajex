from core.entities.department import Department
from core.repositories.department_repository import DepartmentRepository

class CreateDepartmentUseCase:
    """Caso de uso para la creación de nuevos departamentos"""
    
    def __init__(self, department_repository: DepartmentRepository):
        self.department_repository = department_repository

    def execute(self, name: str) -> Department:
        """
        Ejecuta el caso de uso para crear un departamentos
        """
            
        
        depto = Department(
            id=None,# type: ignore
            name=name,
        )

        return self.department_repository.save(depto)
