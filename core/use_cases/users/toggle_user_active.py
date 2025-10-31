from core.entities.user import User
from core.repositories.user_repository import UserRepository

class ToggleUserActiveUseCase:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    def execute(self, user_id: int) -> User:
        user = self.user_repository.get_by_id(user_id)
        if not user:
            raise ValueError("Usuario no encontrado")
        
        # Cambiar el estado activo/inactivo
        user.is_active = not user.is_active
        return self.user_repository.update(user)