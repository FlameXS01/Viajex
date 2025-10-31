from dataclasses import dataclass
from datetime import datetime
from core.entities.user import User

@dataclass
class Session:
    """
    Entidad que representa una sesión de usuario activa
    """
    user: User
    login_time: datetime
    is_active: bool = True

    def get_session_duration(self) -> float:
        """Retorna la duración de la sesión en segundos"""
        return (datetime.now() - self.login_time).total_seconds()