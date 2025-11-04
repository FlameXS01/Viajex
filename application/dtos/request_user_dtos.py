from dataclasses import dataclass
from typing import List, Optional
from .common_dtos import DepartmentResponseDTO

@dataclass
class RequestUserCreateDTO:
    username: str
    fullname: str  
    email: str
    ci: str
    department_id: int

@dataclass
class RequestUserUpdateDTO:
    username: Optional[str] = None
    fullname: Optional[str] = None
    email: Optional[str] = None
    department_id: Optional[int] = None


@dataclass
class RequestUserDetailDTO:
    id: int
    username: str
    fullname: str
    email: str
    ci: str
    department: DepartmentResponseDTO