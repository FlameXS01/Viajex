from dataclasses import dataclass
from typing import Optional

@dataclass
class RequestUserCreateDTO:
    """DTO para crear un nuevo RequestUser"""
    username: str
    fullname: str
    email: str
    ci: str
    department_id: int

@dataclass
class RequestUserUpdateDTO:
    """DTO para actualizar un RequestUser existente"""
    username: Optional[str] = None
    fullname: Optional[str] = None
    email: Optional[str] = None
    ci: Optional[str] = None
    department_id: Optional[int] = None

@dataclass
class RequestUserResponseDTO:
    """DTO para responder con datos de RequestUser"""
    id: int
    username: str
    fullname: str
    email: str
    ci: str
    department_id: int
    department_name: Optional[str] = None  # Para incluir info del departamento
    
    @classmethod
    def from_entity(cls, entity, department_name: Optional[str] = None):
        """Constructor desde la entidad de dominio"""
        return cls(
            id=entity.id,
            username=entity.username,
            fullname=entity.fullname,
            email=entity.email,
            ci=entity.ci,
            department_id=entity.department_id,
            department_name=department_name
        )

@dataclass
class RequestUserListDTO:
    """DTO para listar múltiples RequestUsers"""
    users: list[RequestUserResponseDTO]
    total: int
    page: int
    size: int