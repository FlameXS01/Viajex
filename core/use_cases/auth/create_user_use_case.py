from typing import Optional
from core.entities.user import User
from core.repositories.user_repository import UserRepository
from infrastructure.security.password_hasher import PasswordHasher
from entities.value_objects import Email, UserRole

class CreateUserUseCase:
    def __init__(self, user_repository: UserRepository, password_hasher: PasswordHasher):
        self.user_repository = user_repository
        self.password_hasher = password_hasher

    def execute(self, username: str, email: Email, password: str, role: UserRole) -> tuple[Optional[User], str]:
        # Verificar si el usuario ya existe
        if self.user_repository.exists_by_email(email):              # type: ignore
            return None, "El email ya está registrado"

        # Hash de la contraseña
        hashed_password = self.password_hasher.hash_password(password)

        # Crear el usuario
        user = User(
            username=username,
            email=email,
            role=role,
            hash_password=hashed_password 
        )

        try:
            created_user = self.user_repository.save(user)
            return created_user, "Usuario creado exitosamente"
        except Exception as e:
            return None, f"Error al crear usuario: {str(e)}"