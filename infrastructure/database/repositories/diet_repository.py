# infrastructure/database/repositories/diet_repository_impl.py
from typing import List, Optional
from datetime import date
from sqlalchemy.orm import Session
from sqlalchemy import func
from core.entities.diet import Diet, DietStatus
from core.entities.enums import PaymentMethod
from core.repositories.diet_repository import DietRepository
from infrastructure.database.models import DietModel

class DietRepositoryImpl(DietRepository):
    """
    
    Implementación concreta del repositorio de dietas usando SQLAlchemy
    
    """
    
    def __init__(self, session: Session):
        self.session = session
    
    def create(self, diet: Diet) -> Diet:
        model = DietModel(
            is_local=diet.is_local,
            start_date=diet.start_date,
            end_date=diet.end_date,
            description=diet.description,
            advance_number=diet.advance_number,
            is_group=diet.is_group,
            status=diet.status.value,
            request_user_id=diet.request_user_id,
            diet_service_id=diet.diet_service_id,
            breakfast_count=diet.breakfast_count,
            lunch_count=diet.lunch_count,
            dinner_count=diet.dinner_count,
            accommodation_count=diet.accommodation_count,
            accommodation_payment_method=diet.accommodation_payment_method.upper(),
            accommodation_card_id=diet.accommodation_card_id
        )
        self.session.add(model)
        self.session.commit()
        self.session.refresh(model)
        return self._to_entity(model)
    
    def get_by_id(self, diet_id: int) -> Optional[Diet]:
        model = self.session.query(DietModel).filter(DietModel.id == diet_id).first()
        return self._to_entity(model) if model else None
    
    def get_by_advance_number(self, advance_number: int) -> Optional[Diet]:
        model = self.session.query(DietModel).filter(DietModel.advance_number == advance_number).first()
        return self._to_entity(model) if model else None
    
    def list_by_status(self, status: DietStatus) -> List[Diet]:
        models = self.session.query(DietModel).filter(DietModel.status == status.value).all()
        return [self._to_entity(model) for model in models]
    
    def get_all(self) -> List[Diet]:
        models = self.session.query(DietModel).all()
        return [self._to_entity(model) for model in models]
    
    def list_by_request_user(self, request_user_id: int) -> List[Diet]:
        models = self.session.query(DietModel).filter(DietModel.request_user_id == request_user_id).all()
        return [self._to_entity(model) for model in models]
    
    def list_by_date_range(self, start_date: date, end_date: date) -> List[Diet]:
        models = self.session.query(DietModel).filter(
            DietModel.start_date >= start_date,
            DietModel.end_date <= end_date
        ).all()
        return [self._to_entity(model) for model in models]
    
    def list_pending_liquidation(self) -> List[Diet]:
        models = self.session.query(DietModel).filter(DietModel.status == DietStatus.REQUESTED.value).all()
        return [self._to_entity(model) for model in models]
    
    def update(self, diet: Diet) -> Diet:
        model = self.session.query(DietModel).filter(DietModel.id == diet.id).first()
        
        if model:
            model.is_local = diet.is_local
            model.start_date = diet.start_date
            model.end_date = diet.end_date
            model.description = diet.description
            model.advance_number = diet.advance_number
            model.is_group = diet.is_group
            model.status = diet.status.upper()
            model.request_user_id = diet.request_user_id
            model.diet_service_id = diet.diet_service_id
            model.breakfast_count = diet.breakfast_count
            model.lunch_count = diet.lunch_count
            model.dinner_count = diet.dinner_count
            model.accommodation_count = diet.accommodation_count
            model.accommodation_payment_method = diet.accommodation_payment_method.upper()
            model.accommodation_card_id = diet.accommodation_card_id
            self.session.commit()
            self.session.refresh(model)
        return self._to_entity(model)
    
    def update_status(self, id: int, status: DietStatus) -> Optional[Diet]:
        model = self.session.query(DietModel).filter(DietModel.id == id).first()
        if model:  
            model.status = status
            self.session.commit()
            self.session.refresh(model)
        return self._to_entity(model) if model else None
    
    def delete(self, diet_id: int) -> bool:
        model = self.session.query(DietModel).filter(DietModel.id == diet_id).first()
        if model:
            self.session.delete(model)
            self.session.commit()
            return True
        return False
    
    def card_on_the_road(self, card_id) -> bool:
        return self.session.query(DietModel).filter(
             DietModel.status == DietStatus.REQUESTED.value,
             DietModel.accommodation_payment_method == PaymentMethod.CARD.value, 
             DietModel.accommodation_card_id == card_id
        ).first() is not None
    
    def get_last_advance_number(self) -> int:
        result = self.session.query(func.max(DietModel.advance_number)).scalar()
        return result if result else 0
    
    def reset_advance_numbers(self) -> bool:
        pass
    
    def _to_entity(self, model: DietModel) -> Diet:        
        return Diet(
            id=model.id,
            is_local=model.is_local,
            start_date=model.start_date,
            end_date=model.end_date,
            description=model.description,
            advance_number=model.advance_number,
            is_group=model.is_group,
            status=model.status.value,
            request_user_id=model.request_user_id,
            diet_service_id=model.diet_service_id,
            breakfast_count=model.breakfast_count,
            lunch_count=model.lunch_count,
            dinner_count=model.dinner_count,
            accommodation_count=model.accommodation_count,
            accommodation_payment_method=model.accommodation_payment_method.value,
            accommodation_card_id=model.accommodation_card_id
        )