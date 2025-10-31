from core.entities.request_user import RequestUser
from core.repositories.request_user_repository import RequestUserRepository

class ListUsersUseCase:
    def __init__(self, request_user_repository: RequestUserRepository):
        self.request_user_repository = request_user_repository

    def execute(self) -> list[RequestUser]:
        """
        Lista todos los solicitantes
        """
        return self.request_user_repository.get_all()