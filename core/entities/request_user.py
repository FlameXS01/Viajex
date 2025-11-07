from dataclasses import dataclass
from typing import Optional

@dataclass
class RequestUser:
    """
    Entidad de dominio RequestUser que representa a un usuario beneficiado del sistema.
    """
    username: str
    fullname: str
    email: str
    ci: str
    department_id: int
    id: Optional[int] = None

    def __post_init__(self):
        """Validaciones después de la inicialización"""
