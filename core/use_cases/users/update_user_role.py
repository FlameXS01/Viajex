from core.entities.user import User, UserRole
from core.repositories.user_repository import UserRepository

class UpdateUserRoleUseCase:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    def execute(self, user_id: int, new_role: UserRole) -> User:
        # Buscar el usuario por ID
        user = self.user_repository.get_by_id(user_id)
        if not user:
            raise ValueError("Usuario no encontrado")
        
        # Actualizar el rol
        user.role = new_role
        return self.user_repository.update(user)