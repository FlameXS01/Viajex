from core.entities.user import User
from core.entities.session import Session
from core.repositories.user_repository import UserRepository
from core.use_cases.auth.login import LoginUseCase
from infrastructure.security.password_hasher import PasswordHasher
from datetime import datetime

class AuthService:
    """Servicio de aplicación para autenticación"""
    
    def __init__(self, user_repository: UserRepository, login_use_case: LoginUseCase):
        self.user_repository = user_repository
        self.login_use_case = login_use_case
        self.current_session = None

    def login(self, username: str, password: str) -> Session:
        """
        Realiza el login de un usuario y crea una sesión
        
        Returns:
            Session: La sesión creada
        """
        user = self.login_use_case.execute(username, password)
        
        # Crear sesión
        session = Session(user=user, login_time=datetime.now())
        self.current_session = session
        
        return session

    def logout(self) -> bool:
        """Cierra la sesión actual"""
        if self.current_session:
            self.current_session = None
            return True
        return False

    def get_current_user(self) -> User:
        """Obtiene el usuario actualmente autenticado"""
        if self.current_session:
            return self.current_session.user
        return None

    def is_authenticated(self) -> bool:
        """Verifica si hay un usuario autenticado"""
        return self.current_session is not None and self.current_session.is_active