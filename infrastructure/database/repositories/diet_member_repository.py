# infrastructure/database/repositories/diet_member_repository_impl.py
from typing import List, Optional
from sqlalchemy.orm import Session
from core.entities.diet_member import DietMember
from core.repositories.diet_member_repository import DietMemberRepository
from infrastructure.database.models import DietMemberModel

class DietMemberRepositoryImpl(DietMemberRepository):
    """
    
    Implementación concreta del repositorio de miembros de dieta usando SQLAlchemy
    
    """
    
    def __init__(self, session: Session):
        self.session = session
    
    def create(self, diet_member: DietMember) -> DietMember:
        model = DietMemberModel(
            diet_id=diet_member.diet_id,
            request_user_id=diet_member.request_user_id
        )
        self.session.add(model)
        self.session.commit()
        self.session.refresh(model)
        return self._to_entity(model)
    
    def get_by_id(self, member_id: int) -> Optional[DietMember]:
        model = self.session.query(DietMemberModel).filter(DietMemberModel.id == member_id).first()
        return self._to_entity(model) if model else None
    
    def list_by_diet(self, diet_id: int) -> List[DietMember]:
        models = self.session.query(DietMemberModel).filter(DietMemberModel.diet_id == diet_id).all()
        return [self._to_entity(model) for model in models]
    
    def list_by_request_user(self, request_user_id: int) -> List[DietMember]:
        models = self.session.query(DietMemberModel).filter(DietMemberModel.request_user_id == request_user_id).all()
        return [self._to_entity(model) for model in models]
    
    def delete(self, member_id: int) -> bool:
        model = self.session.query(DietMemberModel).filter(DietMemberModel.id == member_id).first()
        if model:
            self.session.delete(model)
            self.session.commit()
            return True
        return False
    
    def delete_by_diet(self, diet_id: int) -> bool:
        try:
            self.session.query(DietMemberModel).filter(DietMemberModel.diet_id == diet_id).delete()
            self.session.commit()
            return True
        except Exception:
            self.session.rollback()
            return False
    
    def is_member_in_diet(self, diet_id: int, request_user_id: int) -> bool:
        model = self.session.query(DietMemberModel).filter(
            DietMemberModel.diet_id == diet_id,
            DietMemberModel.request_user_id == request_user_id
        ).first()
        return model is not None
    
    def _to_entity(self, model: DietMemberModel) -> DietMember:
        return DietMember(
            id=model.id,
            diet_id=model.diet_id,
            request_user_id=model.request_user_id
        )