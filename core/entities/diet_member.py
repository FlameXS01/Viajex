from dataclasses import dataclass
from typing import Optional


@dataclass
class DietMember:
    """

    Entidad de dominio DietMember que representa los miembros
    adicionales en dietas grupales.
    
    """
    diet_id: int
    request_user_id: int
    id: Optional[int] = None

    def __post_init__(self):
        """Validaciones después de la inicialización"""
        if self.diet_id < 1:
            raise ValueError("El ID de dieta debe ser válido")
        if self.request_user_id < 1:
            raise ValueError("El ID de solicitante debe ser válido")