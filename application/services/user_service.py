from core.entities.user import User, UserRole
from core.repositories.user_repository import UserRepository
from core.use_cases.users.create_user import CreateUserUseCase
from core.use_cases.users.update_user_role import UpdateUserRoleUseCase
from core.use_cases.users.update_user_password import UpdateUserPasswordUseCase
from core.use_cases.users.toggle_user_active import ToggleUserActiveUseCase
from core.use_cases.users.update_user import UpdateUserUseCase
from core.use_cases.users.delete_user import DeleteUserUseCase
from typing import Optional

class UserService:
    def __init__(self, 
                 user_repository: UserRepository, 
                 create_user_use_case: CreateUserUseCase,
                 update_user_role_use_case: UpdateUserRoleUseCase,
                 update_user_use_case: UpdateUserUseCase,
                 update_user_password_use_case: UpdateUserPasswordUseCase,
                 toggle_user_active_use_case: ToggleUserActiveUseCase,
                 delete_user_use_case: DeleteUserUseCase):
        self.user_repository = user_repository
        self.create_user_use_case = create_user_use_case
        self.update_user_role_use_case = update_user_role_use_case
        self.update_user_use_case = update_user_use_case 
        self.update_user_password_use_case = update_user_password_use_case
        self.toggle_user_active_use_case = toggle_user_active_use_case
        self.delete_user_use_case = delete_user_use_case

    def create_user(self, username: str, email: str, password: str, role: UserRole) -> User:
        return self.create_user_use_case.execute(username, email, password, role)

    def get_user(self, user_data) -> Optional[User]:
        user = None
        try:
            user = self.user_repository.get_by_id(user_data)
            if not user:
                user = self.user_repository.get_by_username(user_data)
            if not user:
                user = self.user_repository.get_by_email(user_data)
            return user
        finally:
            return user
    
    def get_user_by_id(self, user_id: int) -> Optional[User]:
        return self.user_repository.get_by_id(user_id)
    
    def get_user_by_email(self, email: str) -> Optional[User]:
        return self.user_repository.get_by_email(email)
    
    def get_user_by_username(self, username: str) -> Optional[User]:
        return self.user_repository.get_by_username(username)

    def get_all_users(self) -> list[User]:
        return self.user_repository.get_all()

    def update_user_role(self, user_id: int, new_role: UserRole) -> User:
        return self.update_user_role_use_case.execute(user_id, new_role)

    def update_user_password(self, user_id: int, current_password: str, new_password: str) -> User:
        return self.update_user_password_use_case.execute(user_id, current_password, new_password)

    def toggle_user_active(self, user_id: int) -> User:
        return self.toggle_user_active_use_case.execute(user_id)
    
    def update_user(self, user_id: int, username: str, email: str, role: UserRole) -> User:
        return self.update_user_use_case.execute(user_id, username, email, role)

    def delete_user(self, user_id: int) -> bool:
        return self.delete_user_use_case.execute(user_id)