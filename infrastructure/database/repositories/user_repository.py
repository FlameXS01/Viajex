from sqlalchemy.orm import Session
from core.entities.user import User, UserRole
from core.repositories.user_repository import UserRepository
from infrastructure.database.models import UserModel
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy import exists, func
from datetime import datetime
from typing import Optional

class UserRepositoryImpl(UserRepository):
    """Implementación concreta del repositorio usando SQLAlchemy"""
    
    def __init__(self, db: Session):
        self.db = db

    def save(self, user: User) -> User:
        """Guarda un usuario en la base de datos"""

        try:

            username_exists = self.db.query(
                exists().where(UserModel.username == user.username)
            ).scalar()
            
            if username_exists:
                raise Exception(f"Ya existe un usuario con el username '{user.username}'")
            
            if user.role not in [UserRole.ADMIN, UserRole.MANAGER, UserRole.USER]:
                raise Exception(f"Rol '{user.role}' no válido. Roles permitidos: {[r.value for r in UserRole]}")
            
            if not user.hash_password or len(user.hash_password.strip()) == 0:
                raise Exception("La contraseña no puede estar vacía")
            
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
        
        except IntegrityError as e:
            self.db.rollback()
            error_msg = str(e).lower()
            
            if "unique constraint" in error_msg or "duplicate" in error_msg:
                if "username" in error_msg or "users.username" in error_msg:
                    raise Exception(f"Ya existe un usuario con el username '{user.username}'")
                elif "email" in error_msg or "users.email" in error_msg:
                    raise Exception(f"Ya existe un usuario con el email '{user.email}'")
                else:
                    raise Exception(f"Error de unicidad: {str(e)}")
            
            raise Exception(f"Error de integridad al guardar usuario: {str(e)}")
            
        except SQLAlchemyError as e:
            self.db.rollback()
            raise Exception(f"Error de base de datos al guardar usuario: {str(e)}")
        
        except Exception as e:
            self.db.rollback()
            if any(msg in str(e) for msg in ["Ya existe", "no válido", "no puede estar vacía"]):
                raise
            raise Exception(f"Error al guardar usuario: {str(e)}")
        
    def get_by_id(self, user_id: int) -> Optional[User]:
        """Obtiene un usuario por ID desde la base de datos"""
        try:
            db_user = self.db.query(UserModel).filter(UserModel.id == user_id).first()
            return self._to_entity(db_user) if db_user else None
        except SQLAlchemyError as e:
            raise Exception(f"Error al obtener usuario por ID: {str(e)}")

    def get_by_username(self, username: str) -> Optional[User]:
        """Obtiene un usuario por username desde la base de datos"""
        try:
            db_user = self.db.query(UserModel).filter(UserModel.username == username).first()
            return self._to_entity(db_user) if db_user else None
        except SQLAlchemyError as e:
            raise Exception(f"Error al obtener usuario por username: {str(e)}")

    def get_by_email(self, email: str) -> Optional[User]:
        """Obtiene un usuario por email desde la base de datos"""
        try:
            db_user = self.db.query(UserModel).filter(UserModel.email == email).first()
            return self._to_entity(db_user) if db_user else None
        except SQLAlchemyError as e:
            raise Exception(f"Error al obtener usuario por email: {str(e)}")

    def get_all(self) -> list[User]:
        """Obtiene todos los usuarios de la base de datos"""
        try:
            db_users = self.db.query(UserModel).order_by(
                UserModel.username.asc()
            ).all()
            return [self._to_entity(user) for user in db_users]
        except SQLAlchemyError as e:
            raise Exception(f"Error al obtener todos los usuarios: {str(e)}")

    def update(self, user: User) -> Optional[User]:
        """Actualiza un usuario existente en la base de datos"""
        try:
            db_user = self.db.query(UserModel).filter(UserModel.id == user.id).first()
            if not db_user:
                return None
            
            if user.username and user.username != db_user.username:
                username_exists = self.db.query(
                    exists().where(
                        UserModel.username == user.username,
                        UserModel.id != user.id
                    )
                ).scalar()
                
                if username_exists:
                    raise Exception(f"Ya existe otro usuario con el username '{user.username}'")
            
            if user.email and user.email != db_user.email:
                email_exists = self.db.query(
                    exists().where(
                        UserModel.email == user.email,
                        UserModel.id != user.id
                    )
                ).scalar()
                
                if email_exists:
                    raise Exception(f"Ya existe otro usuario con el email '{user.email}'")
           
            if user.role not in [UserRole.ADMIN, UserRole.MANAGER, UserRole.USER]:
                raise Exception(f"Rol '{user.role}' no válido")
            
            if not user.is_active and db_user.role == UserRole.ADMIN.value:
                active_admin_count = self.db.query(UserModel).filter(
                    UserModel.role == UserRole.ADMIN.value,
                    UserModel.is_active == True,
                    UserModel.id != user.id
                ).count()
                
                if active_admin_count == 0:
                    raise Exception(
                        "No se puede desactivar el último administrador activo. "
                        "Debe haber al menos un administrador activo en el sistema."
                    )  
                
            db_user.username = user.username                                # type: ignore
            db_user.email = user.email                                      # type: ignore
            db_user.role = user.role.value                                  # type: ignore
            db_user.hash_password = user.hash_password                      # type: ignore
            db_user.is_active = user.is_active                              # type: ignore
            
            self.db.commit()
            self.db.refresh(db_user)
            return self._to_entity(db_user)

        except IntegrityError as e:
            self.db.rollback()
            error_msg = str(e).lower()
            
            if "unique constraint" in error_msg or "duplicate" in error_msg:
                if "username" in error_msg or "users.username" in error_msg:
                    raise Exception(f"Ya existe un usuario con el username '{user.username}'")
                elif "email" in error_msg or "users.email" in error_msg:
                    raise Exception(f"Ya existe un usuario con el email '{user.email}'")
                else:
                    raise Exception(f"Error de unicidad: {str(e)}")
            
            raise Exception(f"Error de integridad al actualizar usuario: {str(e)}")
            
        except SQLAlchemyError as e:
            self.db.rollback()
            raise Exception(f"Error de base de datos al actualizar usuario: {str(e)}")
        
        except Exception as e:
            self.db.rollback()
            if any(msg in str(e) for msg in ["Ya existe", "no válido", "No se puede desactivar"]):
                raise
            raise Exception(f"Error al actualizar usuario: {str(e)}")
        
    def delete(self, user_id: int) -> bool:
        """Elimina un usuario de la base de datos"""
        try:
            
            db_user = self.db.query(UserModel).filter(UserModel.id == user_id).first()
            if not db_user:
                return False
            
            if db_user.role == UserRole.ADMIN.value and db_user.is_active:
                active_admin_count = self.db.query(UserModel).filter(
                    UserModel.role == UserRole.ADMIN.value,
                    UserModel.is_active == True
                ).count()
                
                if active_admin_count <= 1:
                    raise Exception(
                        "No se puede eliminar el último administrador activo. "
                        "Desactive el usuario en lugar de eliminarlo, o promocione a otro usuario a administrador."
                    )
            
            self.db.delete(db_user)
            self.db.commit()
            return True
        
        except IntegrityError as e:
            self.db.rollback()
            if "foreign key constraint" in str(e).lower():
                raise Exception(
                    "No se puede eliminar el usuario porque está siendo referenciado por otros registros."
                )
            raise Exception(f"Error de integridad al eliminar usuario: {str(e)}")
            
        except SQLAlchemyError as e:
            self.db.rollback()
            raise Exception(f"Error de base de datos al eliminar usuario: {str(e)}")
        
        except Exception as e:
            self.db.rollback()
            if "No se puede eliminar" in str(e):
                raise
            raise Exception(f"Error al eliminar usuario: {str(e)}")

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