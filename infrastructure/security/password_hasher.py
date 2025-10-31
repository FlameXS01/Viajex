import bcrypt
from abc import ABC, abstractmethod

class PasswordHasher(ABC):
    """Interfaz abstracta para el hasheo de contraseñas"""
    
    @abstractmethod
    def hash_password(self, password: str) -> str:
        pass
    
    @abstractmethod
    def verify_password(self, password: str, hashed: str) -> bool:
        pass

class BCryptPasswordHasher(PasswordHasher):
    """Implementación usando bcrypt para el hasheo seguro de contraseñas"""
    
    def hash_password(self, password: str) -> str:
        """Genera hash seguro de la contraseña usando bcrypt"""
        # Genera salt y hash la contraseña
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')

    def verify_password(self, password: str, hashed: str) -> bool:
        """Verifica si la contraseña coincide con el hash almacenado"""
        return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))