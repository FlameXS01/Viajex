from core.entities.user import User
from core.entities.session import Session
from core.repositories.user_repository import UserRepository
from infrastructure.security.password_hasher import PasswordHasher
from datetime import datetime

class LoginUseCase:
    """Caso de uso para el login de usuarios"""
    
    def __init__(self, user_repository: UserRepository, password_hasher: PasswordHasher):
        self.user_repository = user_repository
        self.password_hasher = password_hasher

    def execute(self, username: str, password: str) -> User:
        """
        Autentica un usuario con username y password
        
        Args:
            username: Nombre de usuario
            password: Contraseña en texto plano
            
        Returns:
            User: El usuario autenticado
            
        Raises:
            ValueError: Si las credenciales son incorrectas o el usuario está inactivo
        """
        # Buscar usuario por username
        user = self.user_repository.get_by_username(username)
        if not user:
            raise ValueError("Usuario no encontrado")
        
        # Verificar si el usuario está activo
        if not user.is_active:
            raise ValueError("El usuario está desactivado")
        
        # Verificar contraseña
        if not self.password_hasher.verify_password(password, user.hash_password):
            raise ValueError("Contraseña incorrecta")
        
        return user