from abc import ABC, abstractmethod
from typing import Optional
from core.entities.user import User

class UserRepository(ABC):
    """
    Interfaz abstracta para el repositorio de usuarios.
    Define los métodos que cualquier implementación debe tener.
    """
    
    @abstractmethod
    def save(self, user: User) -> User:
        """Guarda un nuevo usuario en el repositorio"""
        pass

    @abstractmethod
    def get_by_id(self, user_id: int) -> Optional[User]:
        """Obtiene un usuario por su ID"""
        pass
    
    @abstractmethod
    def get_by_username(self, username: str) -> Optional[User]:
        """Obtiene un usuario por su nombre de usuario"""
        pass

    @abstractmethod
    def get_by_email(self, email: str) -> Optional[User]:
        """Obtiene un usuario por su email"""
        pass

    @abstractmethod
    def get_all(self) -> list[User]:
        """Obtiene todos los usuarios del sistema"""
        pass

    @abstractmethod
    def update(self, user: User) -> User:
        """Actualiza un usuario existente"""
        pass

    @abstractmethod
    def delete(self, user_id: int) -> bool:
        """Elimina un usuario por su ID"""
        pass