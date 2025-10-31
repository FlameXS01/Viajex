from typing import Optional
from core.entities.request_user import RequestUser
from core.repositories.request_user_repository import RequestUserRepository

class GetUserUseCase:
    def __init__(self, request_user_repository: RequestUserRepository):
        self.request_user_repository = request_user_repository

    def execute(self, req_user_id: int) -> Optional[RequestUser]:
        return self.request_user_repository.get_by_id(req_user_id)