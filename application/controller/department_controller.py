from typing import Optional, List
from application.services.department_service import DepartmentService
from application.dtos.common_dtos import DepartmentResponseDTO

class DepartmentController:
    def __init__(self, department_service: DepartmentService):
        self.department_service = department_service
        
    def create_department(self, name: str) -> DepartmentResponseDTO:
        """
        
        Crea un nuevo departamento
        
        """
        return self.department_service.create_department_f(name)
    
    def get_department_by_name(self, name: str) -> Optional[DepartmentResponseDTO]:
        """
        
        Obtiene un departamento por su nombre
        
        """
        return self.department_service.get_department_by_name(name)                                    # type: ignore
    
    def get_department_by_id(self, department_id: int) -> Optional[DepartmentResponseDTO]:
        """
        
        Obtiene un departamento por su ID
        
        """
        return self.department_service.get_department_by_id(department_id)
    
    def update_department(self, department_id: int, name: str) -> DepartmentResponseDTO:
        """
        
        Actualiza un departamento existente
        
        """
        department = self.department_service.update_department_f(department_id, name)
        return DepartmentResponseDTO(id=department.id, name=department.name)                            # type: ignore
    
    def delete_department(self, department_id: int) -> bool:
        """
        
        Elimina un departamento
        
        """
        return self.department_service.delete_department_f(department_id)

    def list_departments(self) -> List[DepartmentResponseDTO]:
        """
        
        Lista todos los departamentos
        
        """
        return self.department_service.get_all_departments()