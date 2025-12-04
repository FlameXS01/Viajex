from typing import List, Optional
from datetime import date
from sqlalchemy.orm import Session
from sqlalchemy import func
from core.entities.diet_liquidation import DietLiquidation
from core.repositories.diet_liquidation_repository import DietLiquidationRepository
from infrastructure.database.models import DietLiquidationModel

class DietLiquidationRepositoryImpl(DietLiquidationRepository):
    """
    
    Implementación concreta del repositorio de liquidaciones usando SQLAlchemy
    
    """
    
    def __init__(self, session: Session):
        self.session = session
    
    def create(self, diet_liquidation: DietLiquidation) -> DietLiquidation:
        model = DietLiquidationModel(
            diet_id=diet_liquidation.diet_id,
            liquidation_number=diet_liquidation.liquidation_number,
            breakfast_count_liquidated=diet_liquidation.breakfast_count_liquidated,
            lunch_count_liquidated=diet_liquidation.lunch_count_liquidated,
            dinner_count_liquidated=diet_liquidation.dinner_count_liquidated,
            accommodation_count_liquidated=diet_liquidation.accommodation_count_liquidated,
            accommodation_payment_method=diet_liquidation.accommodation_payment_method,
            diet_service_id=diet_liquidation.diet_service_id,
            accommodation_card_id=diet_liquidation.accommodation_card_id
        )
        self.session.add(model)
        self.session.commit()
        self.session.refresh(model)
        return self._to_entity(model)
    
    def get_by_id(self, liquidation_id: int) -> Optional[DietLiquidation]:
        model = self.session.query(DietLiquidationModel).filter(DietLiquidationModel.id == liquidation_id).first()
        return self._to_entity(model) if model else None
    
    def get_by_liquidation_number(self, liquidation_number: int) -> Optional[DietLiquidation]:
        model = self.session.query(DietLiquidationModel).filter(DietLiquidationModel.liquidation_number == liquidation_number).first()
        return self._to_entity(model) if model else None
    
    def get_by_diet_id(self, diet_id: int) -> Optional[DietLiquidation]:
        model = self.session.query(DietLiquidationModel).filter(DietLiquidationModel.diet_id == diet_id).first()
        return self._to_entity(model) if model else None
    
    def list_by_date_range(self, start_date: date, end_date: date) -> List[DietLiquidation]:
        models = self.session.query(DietLiquidationModel).filter(
            DietLiquidationModel.liquidation_date >= start_date,
            DietLiquidationModel.liquidation_date <= end_date
        ).all()
        return [self._to_entity(model) for model in models]
    
    def list_all(self) -> List[DietLiquidation]:
        models = self.session.query(DietLiquidationModel).all()
        return [self._to_entity(model) for model in models]
    
    
    def update(self, diet_liquidation: DietLiquidation) -> DietLiquidation:
        model = self.session.query(DietLiquidationModel).filter(DietLiquidationModel.id == diet_liquidation.id).first()
        if model:
            model.diet_id = diet_liquidation.diet_id
            model.liquidation_number = diet_liquidation.liquidation_number
            model.breakfast_count_liquidated = diet_liquidation.breakfast_count_liquidated
            model.lunch_count_liquidated = diet_liquidation.lunch_count_liquidated
            model.dinner_count_liquidated = diet_liquidation.dinner_count_liquidated
            model.accommodation_count_liquidated = diet_liquidation.accommodation_count_liquidated
            model.accommodation_payment_method = diet_liquidation.accommodation_payment_method
            model.diet_service_id = diet_liquidation.diet_service_id
            model.accommodation_card_id = diet_liquidation.accommodation_card_id
            self.session.commit()
            self.session.refresh(model)
        return self._to_entity(model)
    
    def delete(self, liquidation_id: int) -> bool:
        model = self.session.query(DietLiquidationModel).filter(DietLiquidationModel.id == liquidation_id).first()
        if model:
            self.session.delete(model)
            self.session.commit()
            return True
        return False
    
    def get_last_liquidation_number(self) -> int:
        result = self.session.query(func.max(DietLiquidationModel.liquidation_number)).scalar()
        return result if result else 0
    
    def reset_liquidation_numbers(self) -> bool:
        try:
            self.session.execute("DELETE FROM sqlite_sequence WHERE name='diet_liquidations'")
            self.session.commit()
            return True
        except Exception:
            self.session.rollback()
            return False
    
    def _to_entity(self, model: DietLiquidationModel) -> DietLiquidation:
        from core.entities.diet_liquidation import PaymentMethod
        
        return DietLiquidation(
            id=model.id,
            diet_id=model.diet_id,
            liquidation_number=model.liquidation_number,
            liquidation_date=model.liquidation_date,
            breakfast_count_liquidated=model.breakfast_count_liquidated,
            lunch_count_liquidated=model.lunch_count_liquidated,
            dinner_count_liquidated=model.dinner_count_liquidated,
            accommodation_count_liquidated=model.accommodation_count_liquidated,
            accommodation_payment_method=model.accommodation_payment_method.value,
            diet_service_id=model.diet_service_id,
            accommodation_card_id=model.accommodation_card_id
        )