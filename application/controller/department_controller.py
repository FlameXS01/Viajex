from typing import Optional
from application.services.department_service import DepartmentService
from application.dtos.department_dtos import *

class DepartmentController:
    def __init__(self, department_service: DepartmentService):
        self.department_service = department_service
        
    def create_department(
        self, 
        name: str,
    ) -> DepartmentCreateDTO:
        request = DepartmentCreateDTO(
            name=name
        )
        return self.department_service.create_department_f(request)     # type: ignore
    
    def get_dpto(
        self,
        name: str,
    ) -> DepartmentResponseDTO:
        request = DepartmentCreateDTO(
            name=name
        )
        return self.department_service.get_department_by_name(request)   # type: ignore
    
    def update_department(
        self,
        id: int,
        name: Optional[str] = None,
    ) -> DepartmentResponseDTO:
        request = DepartmentResponseDTO(
            id=id,
            name=name
        )
        return self.department_service.update_department_f(request)
    
    def delete_department(
        self,
        department_id: int
    ) -> bool:
        request = department_id
        
        return self.department_service.delete_department_f(department_id)

    def list_department(self) -> list[DepartmentResponseDTO]:
        return self.department_service.get_all_departments()