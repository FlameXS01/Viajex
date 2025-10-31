from dataclasses import dataclass
from typing import Optional

@dataclass
class CreateRequestUser:
    """DTO para crear un nuevo RequestUser"""
    username: str
    fullname: str
    email: str
    ci: str
    department_id: int

@dataclass
class CreateRequestUserResponse:
    id: Optional[int]
    username: Optional[str]
    email: Optional[str]
    ci: Optional[str]
    fullname: Optional[str]
    department_id: Optional[int]

@dataclass
class GetRequestUserUpdate:
    """DTO para actualizar un RequestUser existente"""
    username: Optional[str] = None
    fullname: Optional[str] = None
    email: Optional[str] = None
    ci: Optional[str] = None
    department_id: Optional[int] = None

@dataclass
class GetUserResponse:
    """DTO para responder con datos de RequestUser"""
    id: int
    username: str
    fullname: str
    email: str
    ci: str
    department_id: int
    
@dataclass
class RequestUserList:
    """DTO para listar múltiples RequestUsers"""
    users: list[GetUserResponse]
    total: int
    page: int
    size: int
    
@dataclass
class GetUserRequest:
    user_id: Optional[int] = None
    username: Optional[str] = None
    ci: Optional[str] = None
    email: Optional[str] = None
    
@dataclass
class DeleteUserRequest:
    user_id: int

@dataclass
class DeleteUserResponse:
    success: bool
    message: str
