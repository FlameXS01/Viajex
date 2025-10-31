from typing import Optional
from application.services.request_service import UserRequestService
from application.dtos.request_user_dtos import (
    CreateRequestUser, GetRequestUserUpdate,
    RequestUserList, CreateRequestUserResponse, 
    GetUserRequest, GetUserResponse,
    DeleteUserRequest, DeleteUserResponse
)

class RequestUserController:
    def __init__(self, request_user_service: UserRequestService):
        self.request_user_service = request_user_service
        
    def create_user(
        self, 
        username: str,
        fullname: str,
        email: str,
        ci: str,
        department_id: int
    ) -> CreateRequestUserResponse:
        request = CreateRequestUser(
            username=username,
            fullname=fullname, 
            email=email,
            ci=ci,
            department_id=department_id
        )
        return self.request_user_service.create_user(request)
    
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
        return self.request_user_service.get_user(request)
    
    def update_user(
        self,
        id: int,
        username: Optional[str] = None,
        fullname: Optional[str] = None,
        email: Optional[str] = None,
        ci: Optional[str] = None,
        department_id: Optional[int] = None,
    ) -> GetRequestUserUpdate:
        request = CreateRequestUserResponse(
            id=id,
            username=username,  
            fullname=fullname,
            email=email,
            ci=ci,
            department_id=department_id
            
        )
        return self.request_user_service.update_user(request)
    
    def delete_user(self, user_id: int) -> DeleteUserResponse:
        request = DeleteUserRequest(user_id=user_id)
        
        return self.request_user_service.delete_user(request)

    def list_users(self) -> RequestUserList:
        return self.request_user_service.get_all_users()