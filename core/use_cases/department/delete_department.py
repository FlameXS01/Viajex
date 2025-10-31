from core.repositories.department_repository import DepartmentRepository

class DeleteDepartmentUseCase:
    def __init__(self, department_repository: DepartmentRepository):
        self.department_repository = department_repository

    def execute(self, depto_id: int) -> bool:
        return self.department_repository.delete(depto_id)