from sqlalchemy.orm import Session
from core.entities.request_user import RequestUser
from sqlalchemy import exists
from core.repositories.request_user_repository import RequestUserRepository
from infrastructure.database.models import RequestUserModel, DepartmentModel, DietModel
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

class RequestUserRepositoryImpl(RequestUserRepository):
    
    def __init__(self, db: Session):
        self.db = db

    def save(self, req_user: RequestUser) -> RequestUser:
        """
        Guarda un nuevo solicitante con validaciones completas.
        """
        try:
            department_exists = self.db.query(
                exists().where(DepartmentModel.id == req_user.department_id)
            ).scalar()
            
            if not department_exists:
                raise Exception(f"No existe el departamento con ID {req_user.department_id}")
            if req_user.ci:
                ci_exists = self.db.query(
                    exists().where(RequestUserModel.ci == req_user.ci)
                ).scalar()
                
                if ci_exists:
                    raise Exception(f"Ya existe un solicitante con el CI {req_user.ci}")
            
            if req_user.email:
                email_exists = self.db.query(
                    exists().where(RequestUserModel.email == req_user.email)
                ).scalar()
                
                if email_exists:
                    raise Exception(f"Ya existe un solicitante con el email {req_user.email}")    
            if req_user.username:
                username_exists = self.db.query(
                    exists().where(RequestUserModel.username == req_user.username)
                ).scalar()
                
                if username_exists:
                    raise Exception(f"Ya existe un solicitante con el username {req_user.username}")
            
            db_request_user = RequestUserModel(
                username=req_user.username,
                fullname=req_user.fullname,
                email=req_user.email,
                ci=req_user.ci,
                department_id=req_user.department_id
            )
            self.db.add(db_request_user)
            self.db.commit()
            self.db.refresh(db_request_user)
            return self._to_entity(db_request_user)
        
        except IntegrityError as e:
            self.db.rollback()
            error_msg = str(e).lower()
            
            if "unique constraint" in error_msg or "duplicate" in error_msg:
                if "ci" in error_msg or "requests.ci" in error_msg:
                    raise Exception(f"Ya existe un solicitante con el CI {req_user.ci}")
                elif "email" in error_msg or "requests.email" in error_msg:
                    raise Exception(f"Ya existe un solicitante con el email {req_user.email}")
                elif "username" in error_msg or "requests.username" in error_msg:
                    raise Exception(f"Ya existe un solicitante con el username {req_user.username}")
                else:
                    raise Exception(f"Error de unicidad: {str(e)}")
            
            elif "foreign key constraint" in error_msg:
                raise Exception(f"El departamento con ID {req_user.department_id} no existe")
            
            raise Exception(f"Error de integridad al guardar solicitante: {str(e)}")
            
        except SQLAlchemyError as e:
            self.db.rollback()
            raise Exception(f"Error de base de datos al guardar solicitante: {str(e)}")
        
        except Exception as e:
            self.db.rollback()
            if any(msg in str(e) for msg in ["No existe", "Ya existe"]):
                raise
            raise Exception(f"Error al guardar solicitante: {str(e)}")

    def get_by_id(self, req_user_id: int) -> RequestUser:
        """
        Obtiene un solicitante por ID.
        """
        try:
            db_request_user = self.db.query(RequestUserModel).filter(
                RequestUserModel.id == req_user_id
            ).first()
            return self._to_entity(db_request_user) if db_request_user else None
        except SQLAlchemyError as e:
            raise Exception(f"Error al obtener solicitante por ID: {str(e)}")

    def get_by_username(self, username: str) -> RequestUser:
        """
        Obtiene un solicitante por username.
        """
        try:
            db_request_user = self.db.query(RequestUserModel).filter(
                RequestUserModel.username == username
            ).first()
            return self._to_entity(db_request_user) if db_request_user else None
        except SQLAlchemyError as e:
            raise Exception(f"Error al obtener solicitante por username: {str(e)}")

    def get_by_email(self, email: str) -> RequestUser:
        """
        Obtiene un solicitante por email.
        """
        try:
            db_request_user = self.db.query(RequestUserModel).filter(
                RequestUserModel.email == email
            ).first()
            return self._to_entity(db_request_user) if db_request_user else None
        except SQLAlchemyError as e:
            raise Exception(f"Error al obtener solicitante por email: {str(e)}")

    def get_by_ci(self, ci: str) -> RequestUser:
        """
        Obtiene un solicitante por CI.
        """
        try:
            db_request_user = self.db.query(RequestUserModel).filter(
                RequestUserModel.ci == ci
            ).first()
            return self._to_entity(db_request_user) if db_request_user else None
        except SQLAlchemyError as e:
            raise Exception(f"Error al obtener solicitante por CI: {str(e)}")

    def get_all(self) -> list[RequestUser]:
        """
        Obtiene todos los solicitantes ordenados por nombre.
        """
        try:
            db_request_users = self.db.query(RequestUserModel).order_by(
                RequestUserModel.fullname.asc()
            ).all()
            return [self._to_entity(user) for user in db_request_users]
        except SQLAlchemyError as e:
            raise Exception(f"Error al obtener todos los solicitantes: {str(e)}")

    def update(self, req_user: RequestUser) -> RequestUser:
        """
        Actualiza un solicitante existente.
        """
        try:
            db_request_user = self.db.query(RequestUserModel).filter(
                RequestUserModel.id == req_user.id
            ).first()
            
            if not db_request_user:
                return None
            
            if req_user.department_id != db_request_user.department_id:
                department_exists = self.db.query(
                    exists().where(DepartmentModel.id == req_user.department_id)
                ).scalar()
                
                if not department_exists:
                    raise Exception(f"No existe el departamento con ID {req_user.department_id}")
            
            if req_user.ci and req_user.ci != db_request_user.ci:
                ci_exists = self.db.query(
                    exists().where(
                        RequestUserModel.ci == req_user.ci,
                        RequestUserModel.id != req_user.id
                    )
                ).scalar()
                
                if ci_exists:
                    raise Exception(f"Ya existe otro solicitante con el CI {req_user.ci}")
        
            db_request_user.username = req_user.username
            db_request_user.fullname = req_user.fullname
            db_request_user.email = req_user.email
            db_request_user.ci = req_user.ci
            db_request_user.department_id = req_user.department_id
            
            self.db.commit()
            self.db.refresh(db_request_user)
            return self._to_entity(db_request_user)
        
        except IntegrityError as e:
            self.db.rollback()
            error_msg = str(e).lower()
            
            if "unique constraint" in error_msg or "duplicate" in error_msg:
                if "ci" in error_msg or "requests.ci" in error_msg:
                    raise Exception(f"Ya existe un solicitante con el CI {req_user.ci}")
                elif "email" in error_msg or "requests.email" in error_msg:
                    raise Exception(f"Ya existe un solicitante con el email {req_user.email}")
                elif "username" in error_msg or "requests.username" in error_msg:
                    raise Exception(f"Ya existe un solicitante con el username {req_user.username}")
                else:
                    raise Exception(f"Error de unicidad: {str(e)}")
            
            elif "foreign key constraint" in error_msg:
                raise Exception(f"El departamento con ID {req_user.department_id} no existe")
            
            raise Exception(f"Error de integridad al actualizar solicitante: {str(e)}")
            
        except SQLAlchemyError as e:
            self.db.rollback()
            raise Exception(f"Error de base de datos al actualizar solicitante: {str(e)}")
        
        except Exception as e:
            self.db.rollback()
            if any(msg in str(e) for msg in ["No existe", "Ya existe"]):
                raise
            raise Exception(f"Error al actualizar solicitante: {str(e)}")

    def delete(self, req_user_id: int) -> bool:
        """
        Elimina un solicitante con validaciones.
        """
        try:
            db_request_user = self.db.query(RequestUserModel).filter(
                    RequestUserModel.id == req_user_id
                ).first()
            if not db_request_user:
                return False
            
            has_diets = self.db.query(
                exists().where(DietModel.request_user_id == req_user_id)
            ).scalar()
            
            if has_diets:
                raise Exception(
                    f"No se puede eliminar el solicitante '{db_request_user.fullname}'. "
                    f"Tiene  dieta(s) asociada(s). "
                )
            
            self.db.delete(db_request_user)
            self.db.commit()
            return True
        
        except IntegrityError as e:
            self.db.rollback()
            if "foreign key constraint" :
                raise Exception(
                    f"No se puede eliminar el solicitante porque tiene dietas asociadas. "
                )
            raise Exception(f"Error de integridad al eliminar solicitante: {str(e)}")
            
        except SQLAlchemyError as e:
            self.db.rollback()
            raise Exception(f"Error de base de datos al eliminar solicitante: {str(e)}")
        
        except Exception as e:
            self.db.rollback()
            if "No se puede eliminar" in str(e):
                raise
            raise Exception(f"Error al eliminar solicitante: {str(e)}")
        
    def _to_entity(self, db_request_user: RequestUserModel) -> RequestUser:
        return RequestUser(
            id=db_request_user.id,
            username=db_request_user.username,
            fullname=db_request_user.fullname,
            email=db_request_user.email,
            ci=db_request_user.ci,
            department_id=db_request_user.department_id
        )