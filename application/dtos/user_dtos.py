from dataclasses import dataclass
from typing import Optional
from core.entities.value_objects import UserRole

@dataclass
class CreateUserRequest:
    username: str
    email: str
    password: str
    role: UserRole

@dataclass
class CreateUserResponse:
    id: Optional[int]
    username: str
    email: str
    role: UserRole
    message: str

@dataclass
class GetUserRequest:
    user_id: int

@dataclass
class GetUserResponse:
    id: int
    username: str
    email: str
    role: UserRole
    is_active: bool
    created_at: str

@dataclass
class UpdateUserRequest:
    user_id: int
    username: str
    email: str
    role: UserRole
    is_active: bool

@dataclass
class UpdateUserResponse:
    id: int
    username: str
    email: str
    role: UserRole
    is_active: bool
    message: str

@dataclass
class DeleteUserRequest:
    user_id: int

@dataclass
class DeleteUserResponse:
    message: str

@dataclass
class ListUsersResponse:
    users: list  # Lista de GetUserResponse