from typing import Optional
from application.services.department_service import DepartmentService
from application.dtos.department_dtos import *

class DepartmentController:
    def __init__(self, department_service: DepartmentService):
        self.department_service = department_service
        
    def create_department(
        self, 
        name: str,
    ) -> DepartmentCreateDTO:
        request = DepartmentCreateDTO(
            name=name
        )
        return self.department_service.create_department_f(request)
    
    def get_dpto(
        self,
        depto_id: Optional[int] = None,
        name: Optional[str] = None,
    ) -> DepartmentResponseDTO:
        request = DepartmentCreateDTO(
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