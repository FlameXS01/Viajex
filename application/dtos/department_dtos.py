from dataclasses import dataclass
from typing import Optional
from .request_user_dtos import RequestUserListDTO, RequestUserResponseDTO

@dataclass
class DepartmentCreateDTO:
    """DTO para crear un nuevo Department"""
    name: str

@dataclass
class DepartmentUpdateDTO:
    """DTO para actualizar un Department existente"""
    name: Optional[str] = None

@dataclass
class DepartmentResponseDTO:
    """DTO para responder con datos de Department"""
    id: int
    name: str
    user_count: Optional[int] = None  
    
    @classmethod
    def from_entity(cls, entity, user_count: Optional[int] = None):
        """Constructor desde la entidad de dominio"""
        return cls(
            id=entity.id,
            name=entity.name,
            user_count=user_count
        )

@dataclass
class DepartmentListDTO:
    """DTO para listar múltiples Departments"""
    departments: list[DepartmentResponseDTO]
    total: int
    page: int
    size: int
    
@dataclass
class DepartmentWithUsersDTO:
    """DTO para Department con sus usuarios incluidos"""
    id: int
    name: str
    users: list[RequestUserResponseDTO]

@dataclass
class RequestUserWithDepartmentDTO:
    """DTO para RequestUser con información completa del departamento"""
    id: int
    username: str
    fullname: str
    email: str
    ci: str
    department: DepartmentResponseDTO  # Objeto completo del departamento
    
    @classmethod
    def from_entity(cls, user_entity, department_entity):
        """Constructor desde las entidades de dominio"""
        return cls(
            id=user_entity.id,
            username=user_entity.username,
            fullname=user_entity.fullname,
            email=user_entity.email,
            ci=user_entity.ci,
            department=DepartmentResponseDTO(
                id=department_entity.id,
                name=department_entity.name
            )
        )