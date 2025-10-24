from typing import Optional
from core.entities.user import User
from core.repositories.user_repository import UserRepository

class GetUserUseCase:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    def execute(self, user_id: int) -> Optional[User]:
        return self.user_repository.get_by_id(user_id)