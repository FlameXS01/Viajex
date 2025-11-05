from core.repositories.request_user_repository import RequestUserRepository

class DeleteRequestUserUseCase:
    def __init__(self, request_user_repository: RequestUserRepository):
        self.request_user_repository = request_user_repository

    def execute(self, request_user_id: int) -> bool:
        return self.request_user_repository.delete(request_user_id)