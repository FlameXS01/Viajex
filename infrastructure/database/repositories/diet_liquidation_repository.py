from traceback import print_exc
import traceback
from typing import List, Optional
from datetime import date
from sqlalchemy.orm import Session
from core.entities.diet_liquidation import DietLiquidation
from core.repositories.diet_liquidation_repository import DietLiquidationRepository
from infrastructure.database.models import DietLiquidationModel, DietModel
from sqlalchemy import func, exists
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

class DietLiquidationRepositoryImpl(DietLiquidationRepository):
    """
    
    Implementación concreta del repositorio de liquidaciones usando SQLAlchemy
    
    """
    
    def __init__(self, session: Session):
        self.session = session
    
    def create(self, diet_liquidation: DietLiquidation) -> DietLiquidation:
        """
        
        Crea una nueva liquidación con validaciones.
        
        """
        try:
            diet_exists = self.session.query(
                exists().where(DietModel.id == diet_liquidation.diet_id)
            ).scalar()
            
            if not diet_exists:
                raise Exception(f"No existe la dieta con ID {diet_liquidation.diet_id}")
            
            existing_liquidation = self.session.query(DietLiquidationModel).filter(
                DietLiquidationModel.diet_id == diet_liquidation.diet_id
            ).first()

            if existing_liquidation:
                raise Exception(
                    f"Ya existe una liquidación para la dieta."
                )
            
            model = DietLiquidationModel(
                diet_id=diet_liquidation.diet_id,
                liquidation_number=diet_liquidation.liquidation_number,
                breakfast_count_liquidated=diet_liquidation.breakfast_count_liquidated,
                lunch_count_liquidated=diet_liquidation.lunch_count_liquidated,
                dinner_count_liquidated=diet_liquidation.dinner_count_liquidated,
                accommodation_count_liquidated=diet_liquidation.accommodation_count_liquidated,
                accommodation_payment_method=diet_liquidation.accommodation_payment_method,
                diet_service_id=diet_liquidation.diet_service_id,
                accommodation_card_id=diet_liquidation.accommodation_card_id,
                total_pay=diet_liquidation.total_pay
            )
            self.session.add(model)
            self.session.commit()
            self.session.refresh(model)
            return self._to_entity(model)
        
        except IntegrityError as e:
            self.session.rollback()
            if "FOREIGN KEY constraint failed" in str(e):
                raise Exception(
                    f"Error de integridad: Verifique que existan "
                )
            elif "UNIQUE constraint" in str(e):
                raise Exception(
                    f"Ya existe una liquidación con el número {diet_liquidation.liquidation_number}"
                )
            raise Exception(f"Error de integridad al crear liquidación: {str(e)}")
            
        except SQLAlchemyError as e:
            self.session.rollback()
            raise Exception(f"Error de base de datos al crear liquidación: {str(e)}")
        
        except Exception as e:
            self.session.rollback()
            if "No existe" in str(e) or "Ya existe" in str(e):
                raise
            raise Exception(f"Error al crear liquidación: {str(e)}")
    
    def get_by_id(self, liquidation_id: int) -> Optional[DietLiquidation]:
        """
        Obtiene una liquidación por ID.
        """
        try:
            model = self.session.query(DietLiquidationModel).filter(
                DietLiquidationModel.id == liquidation_id
            ).first()
            return self._to_entity(model) if model else None
        except SQLAlchemyError as e:
            raise Exception(f"Error al obtener liquidación por ID: {str(e)}")
    
    def get_by_liquidation_number(self, liquidation_number: int) -> Optional[DietLiquidation]:
        """
        Obtiene una liquidación por número de liquidación.
        """
        try:
            model = self.session.query(DietLiquidationModel).filter(
                DietLiquidationModel.liquidation_number == liquidation_number
            ).first()
            return self._to_entity(model) if model else None
        except SQLAlchemyError as e:
            raise Exception(f"Error al obtener liquidación por número: {str(e)}")
    
    def get_by_diet_id(self, diet_id: int) -> Optional[DietLiquidation]:
        """
        Obtiene la liquidación asociada a una dieta.
        """
        try:
            model = self.session.query(DietLiquidationModel).filter(
                DietLiquidationModel.diet_id == diet_id
            ).first()
            return self._to_entity(model) if model else None
        except SQLAlchemyError as e:
            raise Exception(f"Error al obtener liquidación por dieta: {str(e)}")
    
    def list_by_date_range(self, start_date: date, end_date: date) -> List[DietLiquidation]:
        """
        Lista liquidaciones por rango de fechas.
        """
        try:
            models = self.session.query(DietLiquidationModel).filter(
                DietLiquidationModel.liquidation_date >= start_date,
                DietLiquidationModel.liquidation_date <= end_date
            ).order_by(DietLiquidationModel.liquidation_date.desc()).all()
            return [self._to_entity(model) for model in models]
        except SQLAlchemyError as e:
            raise Exception(f"Error al listar liquidaciones por rango de fecha: {str(e)}")
    
    def list_all(self) -> List[DietLiquidation]:
        """
        Lista todas las liquidaciones.
        """
        try:
            models = self.session.query(DietLiquidationModel).order_by(
                DietLiquidationModel.liquidation_date.desc()
            ).all()
            return [self._to_entity(model) for model in models]
        except SQLAlchemyError as e:
            raise Exception(f"Error al listar todas las liquidaciones: {str(e)}")
      
    def update(self, diet_liquidation: DietLiquidation) -> DietLiquidation:
        """
        Actualiza una liquidación existente.
        """
        try:
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
                model.total_pay = diet_liquidation.total_pay
                model.id = diet_liquidation.id
                self.session.commit()
                self.session.refresh(model)

            return self._to_entity(model)
        
        except IntegrityError as e:
            self.session.rollback()
            if "FOREIGN KEY constraint failed" in str(e):
                raise Exception(
                    f"Error de integridad: Verifique que existan "
                    f"los servicios o tarjetas relacionados."
                )
            raise Exception(f"Error de integridad al actualizar liquidación: {str(e)}")
            
        except SQLAlchemyError as e:
            self.session.rollback()
            raise Exception(f"Error de base de datos al actualizar liquidación: {str(e)}")
        
        except Exception as e:
            self.session.rollback()
            if any(msg in str(e) for msg in ["No se puede cambiar", "Ya existe"]):
                raise
            traceback.print_exc()
            raise Exception(f"Error al actualizar liquidación: {str(e)}")
    
    def delete(self, liquidation_id: int) -> bool:
        """
        Elimina una liquidación.
        
        """
        try:

            model = self.session.query(DietLiquidationModel).filter(
                DietLiquidationModel.id == liquidation_id
            ).first()
            
            if not model:
                return False
            
            model = self.session.query(DietLiquidationModel).filter(DietLiquidationModel.id == liquidation_id).first()
            if model:
                self.session.delete(model)
                self.session.commit()
                return True
            return False
        
        except IntegrityError as e:
            self.session.rollback()
            if "FOREIGN KEY constraint failed" in str(e):
                raise Exception(
                    "No se puede eliminar la liquidación porque está siendo referenciada "
                    "por otros registros."
                )
            raise Exception(f"Error de integridad al eliminar liquidación: {str(e)}")
            
        except SQLAlchemyError as e:
            self.session.rollback()
            raise Exception(f"Error de base de datos al eliminar liquidación: {str(e)}")
        
        except Exception as e:
            self.session.rollback()
            raise Exception(f"Error al eliminar liquidación: {str(e)}")
    
    def get_last_liquidation_number(self) -> int:
        """
        Obtiene el último número de liquidación.
        """
        try:
            result = self.session.query(func.max(DietLiquidationModel.liquidation_number)).scalar()
            return result if result else 0
        except SQLAlchemyError as e:
            raise Exception(f"Error al obtener el último número de liquidación: {str(e)}")
      
    def _to_entity(self, model: DietLiquidationModel) -> DietLiquidation:
        
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
            accommodation_card_id=model.accommodation_card_id,
            total_pay=model.total_pay
        )