from core.entities.department import Department
from core.repositories.department_repository import DepartmentRepository

class UpdateDepartmentUseCase:
    """Caso de uso para actualizar información de un departamento"""
    
    def __init__(self, department_repository: DepartmentRepository):
        self.department_repository = department_repository

    def execute(self, department_id: int, name: str) -> Department:
        """
        Actualiza la información básica de un solicitante
        
        Args:
            department_id: ID del department a actualizar
            name: Nuevo nombre 
        Returns:
            Department: Unidad organizativa actualizada
            
        Raises:
            ValueError: Si el departamento no existe o hay conflictos
        """
        depto = self.department_repository.get_by_id(department_id)
        if not depto:
            raise ValueError("Departamento no encontrado")

        # AGREGAR: Validar que el nuevo nombre no exista en otro departamento
        existing = self.department_repository.get_by_name(name)
        if existing and existing.id != department_id:
            raise ValueError("Ya existe un departamento con ese nombre")

        depto.name = name
        return self.department_repository.update(depto)