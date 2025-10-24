from typing import  Optional
from core.use_cases.auth.create_user_use_case import CreateUserUseCase
from core.use_cases.users.get_user_use_case import GetUserUseCase
from core.use_cases.users.update_user_use_case import UpdateUserUseCase
from core.use_cases.users.delete_user_use_case import DeleteUserUseCase
from core.use_cases.users.list_users_use_case import ListUsersUseCase
from application.dtos.user_dtos import (
    CreateUserRequest, CreateUserResponse,
    GetUserRequest, GetUserResponse,
    UpdateUserRequest, UpdateUserResponse,
    DeleteUserRequest, DeleteUserResponse,
    ListUsersResponse
)
from core.entities.user import User

class CreateUserController:
    def __init__(self, create_user_use_case: CreateUserUseCase):
        self.create_user_use_case = create_user_use_case

    def execute(self, request: CreateUserRequest) -> CreateUserResponse:
        user, message = self.create_user_use_case.execute(
            username=request.username,
            email=request.email,             # type: ignore
            password=request.password,
            role=request.role
        )
        if user:
            return CreateUserResponse(
                id=user.id,
                username=user.username,
                email=user.email.value,
                role=user.role,
                message=message
            )
        else:
            return CreateUserResponse(
                id=None,
                username=request.username,
                email=request.email,
                role=request.role,
                message=message
            )

class GetUserController:
    def __init__(self, get_user_use_case: GetUserUseCase):
        self.get_user_use_case = get_user_use_case

    def execute(self, request: GetUserRequest) -> Optional[GetUserResponse]:
        user = self.get_user_use_case.execute(request.user_id)
        if user:
            return GetUserResponse(
                id=user.id,                                                                  # type: ignore
                username=user.username,
                email=user.email.value,
                role=user.role,
                is_active=user.is_active,
                created_at=user.created_at.isoformat() if user.created_at else None      # type: ignore
            )
        else:
            return None

class UpdateUserController:
    def __init__(self, update_user_use_case: UpdateUserUseCase):
        self.update_user_use_case = update_user_use_case

    def execute(self, request: UpdateUserRequest) -> UpdateUserResponse:
        user, message = self.update_user_use_case.execute(
            user_id=request.user_id,
            username=request.username,
            email=request.email,
            role=request.role                # type: ignore
            
        )
        if user:
            return UpdateUserResponse(
                id=user.id,                  # type: ignore
                username=user.username,
                email=user.email.value,
                role=user.role,
                is_active=user.is_active,
                message=message
            )
        else:
            return UpdateUserResponse(
                id=request.user_id,
                username=request.username,
                email=request.email,
                role=request.role,
                is_active=request.is_active,
                message=message
            )

class DeleteUserController:
    def __init__(self, delete_user_use_case: DeleteUserUseCase):
        self.delete_user_use_case = delete_user_use_case

    def execute(self, request: DeleteUserRequest) -> DeleteUserResponse:
        success, message = self.delete_user_use_case.execute(request.user_id)
        return DeleteUserResponse(message=message)

class ListUsersController:
    def __init__(self, list_users_use_case: ListUsersUseCase):
        self.list_users_use_case = list_users_use_case

    def execute(self) -> ListUsersResponse:
        users = self.list_users_use_case.execute()
        user_responses = []
        for user in users:
            user_responses.append(
                GetUserResponse(
                    id=user.id,                             # type: ignore
                    username=user.username,
                    email=user.email.value,
                    role=user.role,
                    is_active=user.is_active,
                    created_at=user.created_at.isoformat() if user.created_at else None         # type: ignore
                )
            )
        return ListUsersResponse(users=user_responses)