from typing import Optional
from application.services.user_service import UserService
from application.dtos.user_dtos import (
    CreateUserRequest, CreateUserResponse,
    GetUserRequest, GetUserResponse,
    UpdateUserRequest, UpdateUserResponse,
    DeleteUserRequest, DeleteUserResponse,
    ListUsersResponse
)
from core.entities.user import UserRole

class UserController:
    def __init__(self, user_service: UserService):
        self.user_service = user_service

    def create_user(
        self, 
        username: str, 
        email: str, 
        password: str, 
        role: UserRole = UserRole.USER
    ) -> CreateUserResponse:
        request = CreateUserRequest(
            username=username,
            email=email,
            password=password,
            role=role
        )
        return self.user_service.create_user(request)

    def get_user(
        self,
        user_id: Optional[int] = None,
        username: Optional[str] = None,
        email: Optional[str] = None
    ) -> GetUserResponse:
        request = GetUserRequest(
            user_id=user_id,
            username=username,
            email=email
        )
        return self.user_service.get_user(request)

    def update_user(
        self,
        user_id: int,
        username: Optional[str] = None,
        email: Optional[str] = None,
        password: Optional[str] = None,
        role: Optional[UserRole] = None,
        is_active: Optional[bool] = None
    ) -> UpdateUserResponse:
        request = UpdateUserRequest(
            user_id=user_id,
            username=username,
            email=email,
            password=password,
            role=role,
            is_active=is_active
        )
        return self.user_service.update_user(request)

    def delete_user(self, user_id: int) -> DeleteUserResponse:
        request = DeleteUserRequest(user_id=user_id)
        return self.user_service.delete_user(request)

    def list_users(self) -> ListUsersResponse:
        return self.user_service.list_users()