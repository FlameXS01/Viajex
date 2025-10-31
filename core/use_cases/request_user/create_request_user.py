from core.entities.request_user import RequestUser
from core.repositories.request_user_repository import RequestUserRepository

class CreateRequestUserUseCase:
    """Caso de uso para la creación de nuevos usuarios solicitantes"""
    
    def __init__(self, request_user_repository: RequestUserRepository):
        self.request_user_repository = request_user_repository

    def execute(self, ci: str, username: str, fullname: str, email: str, department_id: int) -> RequestUser:
        """
        Ejecuta el caso de uso para crear un usuario solicitante
        """
            
        req_user = RequestUser(
            id=None,# type: ignore
            username=username,
            email=email,
            fullname=fullname,
            ci=ci,
            department_id=department_id,
        )

        return self.request_user_repository.save(req_user)
