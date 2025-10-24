from typing import List
from core.entities.user import User
from core.repositories.user_repository import UserRepository

class ListUsersUseCase:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    def execute(self) -> List[User]:
        """
        Lista todos los usuarios
        """
        return self.user_repository.get_all()