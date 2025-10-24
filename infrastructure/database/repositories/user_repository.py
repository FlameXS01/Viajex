from sqlalchemy.orm import Session
from typing import List, Optional
from core.entities.user import User
from core.repositories.user_repository import UserRepository
from infrastructure.database.models import UserModel
from core.entities.value_objects import Email, UserRole

class SQLAlchemyUserRepository(UserRepository):
    
    def __init__(self, session: Session):
        self.session = session
    
    def get_by_id(self, user_id: int) -> Optional[User]:
        user_model = self.session.query(UserModel).filter_by(id=user_id).first()
        return self._to_entity(user_model) if user_model else None
    
    def get_by_email(self, email: str) -> Optional[User]:
        user_model = self.session.query(UserModel).filter_by(email=email).first()
        return self._to_entity(user_model) if user_model else None
    
    def get_all(self) -> List[User]:
        user_models = self.session.query(UserModel).all()
        return [self._to_entity(model) for model in user_models]
    
    def create(self, user: User) -> User:
        user_model = UserModel(
            username=user.username,
            email=user.email.value,                                 # Extraer el string del Value Object
            role=user.role.value,                                   # Extraer el string del Enum
            created_at=user.created_at,
            is_active=user.is_active
        )
        self.session.add(user_model)
        self.session.commit()
        self.session.refresh(user_model)
        return self._to_entity(user_model)
    
    def update(self, user: User) -> User:
        user_model = self.session.query(UserModel).filter_by(id=user.id).first()
        if not user_model:
            raise Exception("Usuario no encontrado")
        
        user_model.username = user.username             # type: ignore
        user_model.email = user.email.value             # type: ignore
        user_model.role = user.role.value               # type: ignore
        user_model.is_active = user.is_active           # type: ignore
        
        self.session.commit()
        self.session.refresh(user_model)
        return self._to_entity(user_model)
    
    def delete(self, user_id: int) -> bool:
        user_model = self.session.query(UserModel).filter_by(id=user_id).first()
        if not user_model:
            return False
        
        self.session.delete(user_model)
        self.session.commit()
        return True
    
    def exists_by_email(self, email: str) -> bool:
        return self.session.query(UserModel).filter_by(email=email).first() is not None
    
    def _to_entity(self, model: UserModel) -> User:
        return User(
            id=model.id,                                    # type: ignore
            username=model.username,                        # type: ignore
            email=Email(model.email),                       # type: ignore
            role=UserRole(model.role),
            created_at=model.created_at,                    # type: ignore
            is_active=model.is_active                       # type: ignore
        )

    def get_by_username(self, username: str) -> User | None:
        raise NotImplementedError

    def save(self, user: User) -> User:
        raise NotImplementedError


       