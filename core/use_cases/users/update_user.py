from core.entities.user import User, UserRole
from core.repositories.user_repository import UserRepository

class UpdateUserUseCase:
    """Caso de uso para actualizar información de usuario"""
    
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    def execute(self, user_id: int, username: str, email: str, role: UserRole) -> User:
        """
        Actualiza la información básica de un usuario
        
        Args:
            user_id: ID del usuario a actualizar
            username: Nuevo nombre de usuario
            email: Nuevo email
            role: Nuevo rol
            
        Returns:
            User: Usuario actualizado
            
        Raises:
            ValueError: Si el usuario no existe o hay conflictos
        """
        user = self.user_repository.get_by_id(user_id)
        if not user:
            raise ValueError("Usuario no encontrado")

        # Verificar si el nuevo username ya existe (excluyendo el usuario actual)
        existing_user = self.user_repository.get_by_username(username)
        if existing_user and existing_user.id != user_id:
            raise ValueError("El nombre de usuario ya está en uso")

        # Verificar si el nuevo email ya existe (excluyendo el usuario actual)
        existing_user = self.user_repository.get_by_email(email)
        if existing_user and existing_user.id != user_id:
            raise ValueError("El email ya está registrado")

        # Actualizar campos
        user.username = username
        user.email = email
        user.role = role

        return self.user_repository.update(user)