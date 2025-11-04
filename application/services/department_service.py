from core.entities.department import Department
from core.repositories.department_repository import DepartmentRepository
from core.use_cases.department.create_department import CreateDepartmentUseCase
from core.use_cases.department.update_department import UpdateDepartmentUseCase 
from core.use_cases.department.get_department import GetDepartmentUseCase
from core.use_cases.department.delete_department import DeleteDepartmentUseCase 
from core.use_cases.department.list_department import ListDepartmentUseCase 
from application.dtos.department_dtos import DepartmentCreateDTO 
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

    def create_department_f(self, name: str) -> DepartmentCreateDTO:
        return self.create_department.execute(name)
    
    def get_department_by_id(self, department_id: int)-> Optional[Department]:
        return self.get_department.execute(department_id)
    
    def get_department_by_name(self, name: str) -> Optional[Department]:
        return self.department_repository.get_by_name(name)
    
    def get_all_departments(self) -> list[Department]:
        return self.get_department_list.execute()
    
    def update_department_f(self, department_id: int, name: str) -> Department:
        return self.update_department.execute(department_id, name)

    def delete_department_f(self, user_id: int) -> bool:
        return self.delete_department.execute(user_id)