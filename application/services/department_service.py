from application.dtos.common_dtos import DepartmentResponseDTO
from core.entities.department import Department
from core.repositories.department_repository import DepartmentRepository
from core.use_cases.department.create_department import CreateDepartmentUseCase
from core.use_cases.department.update_department import UpdateDepartmentUseCase 
from core.use_cases.department.get_department import GetDepartmentUseCase
from core.use_cases.department.delete_department import DeleteDepartmentUseCase 
from core.use_cases.department.list_department import ListDepartmentUseCase 
from application.dtos.department_dtos import *
from typing import Optional

class DepartmentService:
    def __init__(self, 
                 department_repository: DepartmentRepository, 
                 create_department: CreateDepartmentUseCase,
                 update_department: UpdateDepartmentUseCase,
                 get_department: GetDepartmentUseCase,
                 delete_department: DeleteDepartmentUseCase,
                 get_department_list: ListDepartmentUseCase):
        self.department_repository = department_repository
        self.create_department = create_department
        self.update_department = update_department
        self.delete_department = delete_department
        self.get_department = get_department
        self.get_department_list = get_department_list

    def create_department_f(self, name: str) -> DepartmentResponseDTO:
        try:
            department = self.create_department.execute(name)
            return DepartmentResponseDTO(id=department.id, name=department.name)                                # type: ignore
        except Exception as e:
            raise Exception(f"Error al crear departamento: {str(e)}")
        
    def get_department_by_id(self, department_id: int) -> Optional[DepartmentResponseDTO]:
        try:
            department = self.get_department.execute(department_id)
            return DepartmentResponseDTO(id=department.id, name=department.name) if department else None        # type: ignore
        except Exception as e:
            raise Exception(f"Error al obtener departamento: {str(e)}")
        
    def get_department_by_name(self, name: str) -> Optional[Department]:
        try:
            return self.department_repository.get_by_name(name)
        except Exception as e:
            raise Exception(f"Error al buscar departamento por nombre: {str(e)}")
        
    def get_all_departments(self) -> list[DepartmentResponseDTO]:
        try:
            departments = self.get_department_list.execute()
            return [DepartmentResponseDTO(id=dept.id, name=dept.name) for dept in departments]                  # type: ignore
        except Exception as e:
            raise Exception(f"Error al obtener todos los departamentos: {str(e)}")
        
    def update_department_f(self, department_id: int, name: str) -> Department:
        try:
            return self.update_department.execute(department_id, name)
        except Exception as e:
            raise Exception(f"Error al actualizar departamento: {str(e)}")
        
    def delete_department_f(self, department_id: int) -> bool:
        try:
            return self.delete_department.execute(department_id)    
        except Exception as e:
            raise