from dataclasses import dataclass
from .request_user_dtos import RequestUserResponseDTO

@dataclass
class DepartmentCreateDTO:
    name: str

@dataclass  
class DepartmentResponseDTO:
    id: int
    name: str

@dataclass
class DepartmentWithUsersDTO:
    id: int
    name: str
    users: list[RequestUserResponseDTO]  