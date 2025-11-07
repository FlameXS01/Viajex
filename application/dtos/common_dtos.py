from dataclasses import dataclass
from typing import List, Optional


@dataclass  
class DepartmentResponseDTO:
    id: int
    name: str

@dataclass
class RequestUserResponseDTO:
    id: int
    username: str
    fullname: str
    email: str
    ci: str
    department_id: int