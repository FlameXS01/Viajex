from abc import ABC, abstractmethod
from typing import Optional
from core.entities.request_user import RequestUser

class RequestUserRepository(ABC):
    """
    Interfaz abstracta para el repositorio de usuarios solicitantes.
    Define los métodos que cualquier implementación debe tener.
    """
    
    @abstractmethod
    def save(self, req_user: RequestUser) -> RequestUser:
        """Guarda un nuevo solicitante en el repositorio"""
        pass

    @abstractmethod
    def get_by_id(self, req_user_id: int) -> Optional[RequestUser]:
        """Obtiene un solicitante por su ID"""
        pass
    
    @abstractmethod
    def get_by_username(self, username: str) -> Optional[RequestUser]:
        """Obtiene un solicitante por su nombre de usuario"""
        pass

    @abstractmethod
    def get_by_email(self, email: str) -> Optional[RequestUser]:
        """Obtiene un solicitante por su email"""
        pass

    @abstractmethod
    def get_all(self) -> list[RequestUser]:
        """Obtiene todos los solicitantes del sistema"""
        pass

    @abstractmethod
    def update(self, req_user: RequestUser) -> RequestUser:
        """Actualiza un solicitante existente"""
        pass

    @abstractmethod
    def delete(self, req_user_id: int) -> bool:
        """Elimina un solicitante por su ID"""
        pass