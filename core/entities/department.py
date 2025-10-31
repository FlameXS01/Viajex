from dataclasses import dataclass

@dataclass
class Department:
    """
    Entidad de dominio Department que representa la Unidad organizativa.
    """
    id: int
    name: str