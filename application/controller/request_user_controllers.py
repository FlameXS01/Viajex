from typing import Optional, List, Union
from application.services.request_service import UserRequestService
from application.dtos.request_user_dtos import (
    RequestUserCreateDTO, RequestUserResponseDTO, RequestUserUpdateDTO
)

class RequestUserController:
    def __init__(self, request_user_service: UserRequestService):
        self.request_user_service = request_user_service
        
    def create_user(self, username: str, fullname: str, email: str, ci: str, department_id: int) -> RequestUserResponseDTO:
        """
        
        Crea un nuevo usuario solicitante
        
        """
        user_data = RequestUserCreateDTO(username=username, fullname=fullname, email=email, ci=ci, department_id=department_id)
        return self.request_user_service.create_user(user_data)
    
    def get_user_by_id(self, user_id: int) -> Optional[RequestUserResponseDTO]:
        """
        
        Obtiene un usuario por ID
        
        """
        user = self.request_user_service.get_user_by_id(user_id)
        if user:
            return RequestUserResponseDTO(id=user.id, username=user.username, fullname=user.fullname, email=user.email, ci=user.ci, department_id=user.department_id)                           # type: ignore
        return None
    
    def get_user_by_identifier(self, identifier: Union[int, str]) -> Optional[RequestUserResponseDTO]:
        """
        
        Busca usuario por ID, username o email
        
        """
        user = self.request_user_service.get_user(identifier)
        if user:
            return RequestUserResponseDTO(id=user.id, username=user.username, fullname=user.fullname, email=user.email, ci=user.ci, department_id=user.department_id)                           # type: ignore
        return None
    
    def update_user(self, user_id: int, username: str, email: str, fullname: str, department_id: int) -> RequestUserResponseDTO:
        """
        
        Actualiza un usuario existente
        
        """
        user = self.request_user_service.update_user(user_id, username, email, fullname, department_id)
        return RequestUserResponseDTO(id=user.id, username=user.username, fullname=user.fullname, email=user.email, ci=user.ci, department_id=user.department_id)                               # type: ignore
    
    def delete_user(self, user_id: int) -> bool:
        """
        
        Elimina un usuario
        
        """
        return self.request_user_service.delete_user(user_id)

    def list_users(self) -> List[RequestUserResponseDTO]:
        """
        
        Lista todos los usuarios
        
        """
        users = self.request_user_service.get_all_users()
        return [
            RequestUserResponseDTO(id=user.id, username=user.username, fullname=user.fullname, email=user.email, ci=user.ci, department_id=user.department_id) for user in users        # type: ignore
        ]