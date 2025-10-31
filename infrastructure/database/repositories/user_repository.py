from sqlalchemy.orm import Session
from core.entities.user import User, UserRole
from core.repositories.user_repository import UserRepository
from infrastructure.database.models import UserModel
from datetime import datetime
from typing import Optional

class UserRepositoryImpl(UserRepository):
    """Implementación concreta del repositorio usando SQLAlchemy"""
    
    def __init__(self, db: Session):
        self.db = db

    def save(self, user: User) -> User:
        """Guarda un usuario en la base de datos"""
        db_user = UserModel(
            username=user.username,
            email=user.email,
            role=user.role.value,
            hash_password=user.hash_password,
            is_active=user.is_active
        )
        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)
        return self._to_entity(db_user)

    def get_by_id(self, user_id: int) -> Optional[User]:
        """Obtiene un usuario por ID desde la base de datos"""
        db_user = self.db.query(UserModel).filter(UserModel.id == user_id).first()
        return self._to_entity(db_user) if db_user else None

    def get_by_username(self, username: str) -> Optional[User]:
        """Obtiene un usuario por username desde la base de datos"""
        db_user = self.db.query(UserModel).filter(UserModel.username == username).first()
        return self._to_entity(db_user) if db_user else None

    def get_by_email(self, email: str) -> Optional[User]:
        """Obtiene un usuario por email desde la base de datos"""
        db_user = self.db.query(UserModel).filter(UserModel.email == email).first()
        return self._to_entity(db_user) if db_user else None

    def get_all(self) -> list[User]:
        """Obtiene todos los usuarios de la base de datos"""
        db_users = self.db.query(UserModel).all()
        return [self._to_entity(user) for user in db_users]

    def update(self, user: User) -> User:
        """Actualiza un usuario existente en la base de datos"""
        db_user = self.db.query(UserModel).filter(UserModel.id == user.id).first()
        if db_user:
            db_user.username = user.username                                # type: ignore
            db_user.email = user.email                                      # type: ignore
            db_user.role = user.role.value                                  # type: ignore
            db_user.hash_password = user.hash_password                      # type: ignore
            db_user.is_active = user.is_active                              # type: ignore
            self.db.commit()
            self.db.refresh(db_user)
        return self._to_entity(db_user)

    def delete(self, user_id: int) -> bool:
        """Elimina un usuario de la base de datos"""
        db_user = self.db.query(UserModel).filter(UserModel.id == user_id).first()
        if db_user:
            self.db.delete(db_user)
            self.db.commit()
            return True
        return False

    def _to_entity(self, db_user: UserModel) -> User:
        """Convierte el modelo de base de datos a entidad de dominio"""
        return User(
            id=db_user.id,                                              # type: ignore                    
            username=db_user.username,                                  # type: ignore
            email=db_user.email,                                        # type: ignore
            role=UserRole(db_user.role),
            hash_password=db_user.hash_password,                        # type: ignore
            created_at=db_user.created_at,                              # type: ignore
            is_active=db_user.is_active                                 # type: ignore
        )