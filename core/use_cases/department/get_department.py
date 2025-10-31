from typing import Optional
from core.entities.department import Department
from core.repositories.department_repository import DepartmentRepository

class GetDepartmentUseCase:
    def __init__(self, department_repository: DepartmentRepository):
        self.department_repository = department_repository

    def execute(self, department_id: int) -> Optional[Department]:
        return self.department_repository.get_by_id(department_id)