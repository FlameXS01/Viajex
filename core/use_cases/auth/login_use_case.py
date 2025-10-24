from typing import Optional, Tuple
from core.entities.user import User
from core.repositories.user_repository import UserRepository
from infrastructure.security.password_hasher import PasswordHasher

class LoginUseCase:
    def __init__(self, user_repository: UserRepository, password_hasher: PasswordHasher):
        self.user_repository = user_repository
        self.password_hasher = password_hasher

    def execute(self, email: str, password: str) -> Tuple[Optional[User], str]:
        # Buscar usuario por email
        user = self.user_repository.get_by_email(email)
        if not user:
            return None, "Usuario no encontrado"

        if not user.is_active:
            return None, "Usuario inactivo"

        # Verificar contraseña
        if not self.password_hasher.verify_password(password, user.hash_password):
            return None, "Contraseña incorrecta"

        return user, "Login exitoso"