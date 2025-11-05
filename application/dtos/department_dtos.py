from dataclasses import dataclass
from .common_dtos import RequestUserResponseDTO

@dataclass
class DepartmentCreateDTO:
    name: str

@dataclass
class DepartmentWithUsersDTO:
    id: int
    name: str
    users: list[RequestUserResponseDTO]  