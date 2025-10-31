from core.entities.user import User, UserRole
from core.repositories.user_repository import UserRepository
from infrastructure.security.password_hasher import PasswordHasher

class CreateUserUseCase:
    """Caso de uso para la creación de nuevos usuarios"""
    
    def __init__(self, user_repository: UserRepository, password_hasher: PasswordHasher):
        self.user_repository = user_repository
        self.password_hasher = password_hasher

    def execute(self, username: str, email: str, password: str, role: UserRole = UserRole.USER) -> User:
        """
        Ejecuta el caso de uso para crear un usuario
        """
        # Verifica si el usuario ya existe
        if self.user_repository.get_by_username(username):
            raise ValueError("El nombre de usuario ya está en uso")
        
        if self.user_repository.get_by_email(email):
            raise ValueError("El email ya está registrado")

        # Hash de la contraseña
        hashed_password = self.password_hasher.hash_password(password)

        # Crea la entidad User
        user = User(
            id=None,# type: ignore
            username=username,
            email=email,
            role=role,
            hash_password=hashed_password,
            created_at=None,# type: ignore
            is_active=True
        )

        # Guarda el usuario en el repositorio
        return self.user_repository.save(user)