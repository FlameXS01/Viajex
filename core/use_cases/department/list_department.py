from core.entities.department import Department
from core.repositories.department_repository import DepartmentRepository

class ListRequestUsersUseCase:
    def __init__(self, department_repository: DepartmentRepository):
        self.department_repository = department_repository

    def execute(self) -> list[Department]:
        """
        Lista todos los departamentos
        """
        return self.department_repository.get_all()