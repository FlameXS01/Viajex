from dataclasses import dataclass
from datetime import datetime
from enum import Enum

class UserRole(Enum):
    """Enum que representa los roles disponibles para los usuarios"""
    
    ADMIN = "admin"
    MANAGER = "manager"
    USER = "user"

@dataclass
class User:
    """
    Entidad de dominio User que representa a un usuario en el sistema.
    Contiene la lógica de negocio y validaciones básicas.
    """
    id: int
    username: str
    email: str
    role: UserRole
    hash_password: str
    created_at: datetime
    is_active: bool = True

    def __post_init__(self):
        """Validaciones después de la inicialización"""
        if len(self.username) < 3:
            raise ValueError("Username debe tener al menos 3 caracteres")
        if "@" not in self.email:
            raise ValueError("Email debe ser válido")

    def activate(self):
        """Activa el usuario"""
        self.is_active = True

    def deactivate(self):
        """Desactiva el usuario"""
        self.is_active = False

    def has_role(self, role: UserRole) -> bool:
        """Verifica si el usuario tiene un rol específico"""
        return self.role == role