from application.dtos.common_dtos import RequestUserResponseDTO
from core.entities.request_user import RequestUser
from core.repositories.request_user_repository import RequestUserRepository
from core.use_cases.request_user.create_request_user import CreateRequestUserUseCase
from core.use_cases.request_user.update_user_request import UpdateRequestUserUseCase 
from core.use_cases.request_user.get_request_user import GetRequestUserUseCase
from core.use_cases.request_user.delete_request_user import DeleteRequestUserUseCase 
from core.use_cases.request_user.list_users_request import ListRequestUsersUseCase 
from application.dtos.request_user_dtos import *
from typing import Optional, Union

class UserRequestService:
    def __init__(self, 
                 request_user_repository: RequestUserRepository, 
                 create_request_user: CreateRequestUserUseCase,
                 update_user_request: UpdateRequestUserUseCase,
                 get_user_request: GetRequestUserUseCase,
                 get_user_request_list: ListRequestUsersUseCase,
                 delete_user_request: DeleteRequestUserUseCase):
        self.request_user_repository = request_user_repository
        self.create_request_user = create_request_user
        self.update_user_request = update_user_request
        self.delete_user_request = delete_user_request
        self.get_user_request = get_user_request
        self.get_user_request_list = get_user_request_list

    def create_user(self, user_data: RequestUserCreateDTO) -> RequestUserResponseDTO:
        user = self.create_request_user.execute(
            ci=user_data.ci,
            username=user_data.username, 
            fullname=user_data.fullname,
            email=user_data.email,
            department_id=user_data.department_id
        )
        return RequestUserResponseDTO(
            id=user.id,                                                                             # type: ignore
            username=user.username,
            fullname=user.fullname,
            email=user.email, 
            ci=user.ci,
            department_id=user.department_id
        )
    
    def get_user(self, user_data: Union[int, str]) -> Optional[RequestUser]:
        """Busca usuario por ID, username o email"""
        user = None
        
        if isinstance(user_data, int):
            user = self.request_user_repository.get_by_id(user_data)
        
        if isinstance(user_data, str) and not user:
            user = self.request_user_repository.get_by_username(user_data)
        
        if isinstance(user_data, str) and not user:
            user = self.request_user_repository.get_by_email(user_data)
            
        return user
    
    def get_user_by_id(self, user_id: int)-> Optional[RequestUser]:
        return self.get_user_request.execute(user_id)
    
    def get_user_by_ci(self, ci: str)-> Optional[RequestUser]:
        return self.request_user_repository.get_by_ci(ci)
    
    def get_user_by_username(self, username: str) -> Optional[RequestUser]:
        return self.request_user_repository.get_by_username(username)
    
    def get_all_users(self) -> list[RequestUser]:
        return self.get_user_request_list.execute()
    
    def update_user(self, req_user_id: int, username: str, email: str, fullname: str, department_id: int) -> RequestUser:
        return self.update_user_request.execute(req_user_id, username, email, fullname, department_id )

    def delete_user(self, user_id: int) -> bool:
        return self.delete_user_request.execute(user_id)
    
    