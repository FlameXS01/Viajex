from core.entities.request_user import RequestUser
from core.repositories.request_user_repository import RequestUserRepository

class CreateUserUseCase:
    """Caso de uso para la creación de nuevos usuarios solicitantes"""
    
    def __init__(self, request_user_repository: RequestUserRepository):
        self.request_user_repository = request_user_repository

    def execute(self, username: str, email: str, fullname: str, ci: str, department_id: int) -> RequestUser:
        """
        Ejecuta el caso de uso para crear un usuario solicitante
        """
            
        # Crea la entidad User
        request_user = RequestUser(
            id=None,# type: ignore
            username=username,
            fullname=fullname,
            email=email,
            ci=ci,
            department_id=department_id
        )

        # Guarda el usuario en el repositorio
        return self.request_user_repository.save(request_user)
