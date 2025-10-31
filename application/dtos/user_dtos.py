from dataclasses import dataclass
from typing import Optional, List
from datetime import datetime
from core.entities.user import UserRole

@dataclass
class CreateUserRequest:
    username: str
    email: str
    password: str
    role: UserRole = UserRole.USER

@dataclass
class CreateUserResponse:
    id: int
    username: str
    email: str
    role: UserRole
    created_at: datetime

@dataclass
class GetUserRequest:
    user_id: Optional[int] = None
    username: Optional[str] = None
    email: Optional[str] = None

@dataclass
class GetUserResponse:
    id: int
    username: str
    email: str
    role: UserRole
    created_at: datetime
    is_active: bool

@dataclass
class UpdateUserRequest:
    user_id: int
    username: Optional[str] = None
    email: Optional[str] = None
    password: Optional[str] = None
    role: Optional[UserRole] = None
    is_active: Optional[bool] = None

@dataclass
class UpdateUserResponse:
    id: int
    username: str
    email: str
    role: UserRole
    is_active: bool

@dataclass
class DeleteUserRequest:
    user_id: int

@dataclass
class DeleteUserResponse:
    success: bool
    message: str

@dataclass
class ListUsersResponse:
    users: List[GetUserResponse]