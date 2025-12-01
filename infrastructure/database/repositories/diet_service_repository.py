from typing import List, Optional
from sqlalchemy.orm import Session
from core.entities.diet_service import DietService
from core.repositories.diet_service_repository import DietServiceRepository
from infrastructure.database.models import DietServiceModel

class DietServiceRepositoryImpl(DietServiceRepository):
    """
    
    Implementación concreta del repositorio de servicios de dieta usando SQLAlchemy
    
    """
    
    def __init__(self, session: Session):
        self.session = session
    
    def create(self, diet_service: DietService) -> DietService:
        service = self.get_by_local(diet_service.is_local)
        if not service:
            model = DietServiceModel(
                is_local=diet_service.is_local,
                breakfast_price=diet_service.breakfast_price,
                lunch_price=diet_service.lunch_price,
                dinner_price=diet_service.dinner_price,
                accommodation_cash_price=diet_service.accommodation_cash_price,
                accommodation_card_price=diet_service.accommodation_card_price
            )
            self.session.add(model)
            self.session.commit()
            self.session.refresh(model)
            return self._to_entity(model)
            
    
    def get_by_id(self, diet_service_id: int) -> Optional[DietService]:
        model = self.session.query(DietServiceModel).filter(DietServiceModel.id == diet_service_id).first()
        return self._to_entity(model) if model else None
    
    def get_by_local(self, is_local: bool) -> DietService:
        model = self.session.query(DietServiceModel).filter(DietServiceModel.is_local == is_local).first()
        return self._to_entity(model) if model else None
    
    def list_all(self) -> List[DietService]:
        models = self.session.query(DietServiceModel).all()
        return [self._to_entity(model) for model in models]
    
    def update(self, diet_service: DietService) -> DietService:
        model = self.session.query(DietServiceModel).filter(DietServiceModel.id == diet_service.id).first()
        if model:
            model.is_local = diet_service.is_local
            model.breakfast_price = diet_service.breakfast_price
            model.lunch_price = diet_service.lunch_price
            model.dinner_price = diet_service.dinner_price
            model.accommodation_cash_price = diet_service.accommodation_cash_price
            model.accommodation_card_price = diet_service.accommodation_card_price
            self.session.commit()
            self.session.refresh(model)
        return self._to_entity(model)
    
    def delete(self, diet_service_id: int) -> bool:
        model = self.session.query(DietServiceModel).filter(DietServiceModel.id == diet_service_id).first()
        if model:
            self.session.delete(model)
            self.session.commit()
            return True
        return False
    
    def _to_entity(self, model: DietServiceModel) -> DietService:
        return DietService(
            id=model.id,
            is_local=model.is_local,
            breakfast_price=model.breakfast_price,
            lunch_price=model.lunch_price,
            dinner_price=model.dinner_price,
            accommodation_cash_price=model.accommodation_cash_price,
            accommodation_card_price=model.accommodation_card_price
        )