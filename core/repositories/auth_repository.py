from abc import ABC, abstractmethod
from core.entities.session import Session

class AuthRepository(ABC):
    """Interfaz abstracta para el repositorio de autenticación"""
    
    @abstractmethod
    def create_session(self, session: Session) -> Session:
        """Crea una nueva sesión de usuario"""
        pass

    @abstractmethod
    def get_session(self, user_id: int) -> Session:
        """Obtiene la sesión activa de un usuario"""
        pass

    @abstractmethod
    def delete_session(self, user_id: int) -> bool:
        """Elimina la sesión de un usuario (logout)"""
        pass