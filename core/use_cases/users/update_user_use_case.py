from typing import Optional, Tuple
from core.entities.user import User
from core.repositories.user_repository import UserRepository

class UpdateUserUseCase:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    def execute(self, user_id: int, username: str, email: str, role: str) -> Tuple[Optional[User], str]:
        user = self.user_repository.get_by_id(user_id)
        if not user:
            return None, "Usuario no encontrado"

        # Actualizar campos
        user.username = username
        user.email = email          # type: ignore
        user.role = role            # type: ignore

        try:
            updated_user = self.user_repository.update(user)
            return updated_user, "Usuario actualizado exitosamente"
        except Exception as e:
            return None, f"Error al actualizar usuario: {str(e)}"