from core.repositories.user_repository import UserRepository
from core.entities.user import User
from infrastructure.security.password_hasher import PasswordHasher

class UpdateUserPasswordUseCase:
    """Caso de uso para actualizar la contraseña de un usuario con verificación de seguridad"""
    
    def __init__(self, user_repository: UserRepository, password_hasher: PasswordHasher):
        self.user_repository = user_repository
        self.password_hasher = password_hasher

    def execute(self, user_id: int, current_password: str, new_password: str) -> User:
        """
        Actualiza la contraseña de un usuario verificando la contraseña actual primero
        
        Args:
            user_id: ID del usuario
            current_password: Contraseña actual para verificación
            new_password: Nueva contraseña en texto plano
            
        Returns:
            User: Usuario actualizado
            
        Raises:
            ValueError: Si la contraseña actual no es correcta
        """
        user = self.user_repository.get_by_id(user_id)
        if not user:
            raise ValueError("Usuario no encontrado")
        
        # VERIFICACIÓN DE SEGURIDAD: Confirmar que la contraseña actual es correcta
        if not self.password_hasher.verify_password(current_password, user.hash_password):
            raise ValueError("La contraseña actual no es correcta")
        
        # Verificar que la nueva contraseña es diferente
        if current_password == new_password:
            raise ValueError("La nueva contraseña debe ser diferente a la actual")
        
        # Validar fortaleza de la nueva contraseña
        if len(new_password) < 8:
            raise ValueError("La nueva contraseña debe tener al menos 6 caracteres")
        
        # Hashea la nueva contraseña
        hashed_password = self.password_hasher.hash_password(new_password)
        user.hash_password = hashed_password
        
        return self.user_repository.update(user)