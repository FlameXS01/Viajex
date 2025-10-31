from dataclasses import dataclass
from typing import Optional

@dataclass
class RequestUser:
    """
    Entidad de dominio RequestUser que representa a un usuario beneficiado del sistema.
    """
    id: int
    username: str
    fullname: str
    email: str
    ci: str
    department_id: int

    def __post_init__(self):
        """Validaciones después de la inicialización"""
        if len(self.username) < 3:
            raise ValueError("Username debe tener al menos 3 caracteres")
        if len(self.ci) != 11:
            raise ValueError("CI debe tener entre 11 caracteres")