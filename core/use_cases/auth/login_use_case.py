from typing import Tuple, Optional
from ...entities.user import User
from ...repositories.user_repository import UserRepository
from infrastructure.security.password_hasher import PasswordHasher

class LoginUseCase:
    def __init__(self, user_repository: UserRepository, password_hasher: PasswordHasher):
        self.user_repository = user_repository
        self.password_hasher = password_hasher
    
    def execute(self, username: str, password: str) -> Tuple[bool, Optional[User], str]:
        user = self.user_repository.get_by_username(username)
        
        if not user:
            return False, None, "Usuario no encontrado"
        
        if not user.is_active:
            return False, None, "Usuario inactivo"
        
       
        if not self.password_hasher.verify(password, user.password_hash):
            return False, None, "Contraseña incorrecta"
        
        return True, user, "Login exitoso"

