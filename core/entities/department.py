from dataclasses import dataclass
from typing import Optional

@dataclass
class Department:
    """
    Entidad de dominio Department que representa la Unidad organizativa.
    """
    name: str
    id: Optional[int] = None