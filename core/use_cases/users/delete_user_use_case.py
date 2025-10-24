from typing import Tuple
from core.repositories.user_repository import UserRepository

class DeleteUserUseCase:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    def execute(self, user_id: int) -> Tuple[bool, str]:
        user = self.user_repository.get_by_id(user_id)
        if not user:
            return False, "Usuario no encontrado"

        try:
            success = self.user_repository.delete(user_id)
            if success:
                return True, "Usuario eliminado exitosamente"
            else:
                return False, "Error al eliminar usuario"
        except Exception as e:
            return False, f"Error al eliminar usuario: {str(e)}"