from core.entities.request_user import RequestUser
from core.repositories.request_user_repository import RequestUserRepository

class UpdateRequestUserUseCase:
    """Caso de uso para actualizar información de usuario"""
    
    def __init__(self, request_user_repository: RequestUserRepository):
        self.request_user_repository = request_user_repository

    def execute(self, req_user_id: int, username: str, email: str, fullname: str, department_id: int) -> RequestUser:
        """
        Actualiza la información básica de un solicitante
        
        Args:
            user_id: ID del usuario a actualizar
            username: Nuevo nombre de usuario
            email: Nuevo email
            fullname: Nuevo nombre completo
            department_id: Nueva unidad organizativa
            
        Returns:
            RequestUser: Solicitante actualizado
            
        Raises:
            ValueError: Si el solicitante no existe o hay conflictos
        """
        req_user = self.request_user_repository.get_by_id(req_user_id)
        if not req_user:
            raise ValueError("Solicitante no encontrado")

        existing = self.request_user_repository.get_by_username(username)
        if existing and existing.id != req_user_id:
            raise ValueError("El nombre de usuario ya está en uso")
            
        existing = self.request_user_repository.get_by_email(email)
        if existing and existing.id != req_user_id:
            raise ValueError("El email ya está registrado")

        req_user.username = username
        req_user.email = email
        req_user.fullname = fullname
        req_user.department_id = department_id
        
        return self.request_user_repository.update(req_user)