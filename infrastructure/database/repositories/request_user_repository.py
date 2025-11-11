from sqlalchemy.orm import Session
from core.entities.request_user import RequestUser
from core.repositories.request_user_repository import RequestUserRepository
from infrastructure.database.models import RequestUserModel

class RequestUserRepositoryImpl(RequestUserRepository):
    
    def __init__(self, db: Session):
        self.db = db

    def save(self, req_user: RequestUser) -> RequestUser:
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

    def get_by_id(self, req_user_id: int) -> RequestUser:
        db_request_user = self.db.query(RequestUserModel).filter(RequestUserModel.id == req_user_id).first()
        return self._to_entity(db_request_user) if db_request_user else None

    def get_by_username(self, username: str) -> RequestUser:
        db_request_user = self.db.query(RequestUserModel).filter(RequestUserModel.username == username).first()
        return self._to_entity(db_request_user) if db_request_user else None

    def get_by_email(self, email: str) -> RequestUser:
        db_request_user = self.db.query(RequestUserModel).filter(RequestUserModel.email == email).first()
        return self._to_entity(db_request_user) if db_request_user else None

    def get_by_ci(self, ci: str) -> RequestUser:
        db_request_user = self.db.query(RequestUserModel).filter(RequestUserModel.ci == ci).first()
        return self._to_entity(db_request_user) if db_request_user else None

    # def get_all(self) -> list[RequestUser]:
    #     db_request_users = self.db.query(RequestUserModel).all()
    #     return [self._to_entity(user) for user in db_request_users]

    def get_all(self) -> list[RequestUser]:
        db_request_users = self.db.query(RequestUserModel).order_by(RequestUserModel.fullname.asc()).all()
        return [self._to_entity(user) for user in db_request_users]

    def update(self, req_user: RequestUser) -> RequestUser:
        db_request_user = self.db.query(RequestUserModel).filter(RequestUserModel.id == req_user.id).first()
        if db_request_user:
            db_request_user.username = req_user.username
            db_request_user.fullname = req_user.fullname
            db_request_user.email = req_user.email
            db_request_user.ci = req_user.ci
            db_request_user.department_id = req_user.department_id
            self.db.commit()
            self.db.refresh(db_request_user)
        return self._to_entity(db_request_user)

    def delete(self, req_user_id: int) -> bool:
        db_request_user = self.db.query(RequestUserModel).filter(RequestUserModel.id == req_user_id).first()
        if db_request_user:
            self.db.delete(db_request_user)
            self.db.commit()
            return True
        return False

    def _to_entity(self, db_request_user: RequestUserModel) -> RequestUser:
        return RequestUser(
            id=db_request_user.id,
            username=db_request_user.username,
            fullname=db_request_user.fullname,
            email=db_request_user.email,
            ci=db_request_user.ci,
            department_id=db_request_user.department_id
        )