# infrastructure/database/repositories/diet_repository_impl.py
from typing import List, Optional
from datetime import date
from sqlalchemy.orm import Session
from sqlalchemy import exists, func
from core.entities.diet import Diet, DietStatus
from core.entities.enums import PaymentMethod
from core.repositories.diet_repository import DietRepository
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from infrastructure.database.models import CardModel, DietLiquidationModel, DietModel, DietServiceModel, RequestUserModel

class DietRepositoryImpl(DietRepository):
    """
    
    Implementación concreta del repositorio de dietas usando SQLAlchemy
    
    """
    
    def __init__(self, session: Session):
        self.session = session
    
    def create(self, diet: Diet) -> Diet:
        """
        Crea una nueva dieta.
        """
        try:
            user_exists = self.session.query(
                exists().where(RequestUserModel.id == diet.request_user_id)
            ).scalar()
            
            if not user_exists:
                raise Exception(f"No existe el solicitante con ID {diet.request_user_id}")
            
            service_exists = self.session.query(
                exists().where(DietServiceModel.id == diet.diet_service_id)
            ).scalar()
            
            if not service_exists:
                raise Exception(f"No existe el servicio de dieta con ID {diet.diet_service_id}")
            
            if diet.accommodation_card_id:
                card_exists = self.session.query(
                    exists().where(CardModel.card_id == diet.accommodation_card_id)
                ).scalar()
                
                if not card_exists:
                    raise Exception(f"No existe la tarjeta con ID {diet.accommodation_card_id}")
                
            if diet.start_date > diet.end_date:
                raise Exception("La fecha de inicio no puede ser mayor a la fecha de fin")
            
            advance_exists = self.session.query(
                exists().where(DietModel.advance_number == diet.advance_number)
            ).scalar()
            
            if advance_exists:
                raise Exception(f"Ya existe una dieta con el número de anticipo {diet.advance_number}")
            
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
        
        except IntegrityError as e:
            self.session.rollback()
            if "FOREIGN KEY constraint failed" in str(e):
                raise Exception(
                    f"Error de integridad: Verifique que existan "
                    f"el solicitante ({diet.request_user_id}), "
                    f"servicio de dieta ({diet.diet_service_id}) o "
                    f"tarjeta ({diet.accommodation_card_id})"
                )
            elif "UNIQUE constraint" in str(e):
                raise Exception(
                    f"Ya existe una dieta con el número de anticipo {diet.advance_number}"
                )
            raise Exception(f"Error de integridad al crear dieta: {str(e)}")
            
        except SQLAlchemyError as e:
            self.session.rollback()
            raise Exception(f"Error de base de datos al crear dieta: {str(e)}")
        
        except Exception as e:
            self.session.rollback()
            if any(msg in str(e) for msg in ["No existe", "Ya existe", "no está activa", "fecha"]):
                raise
            raise Exception(f"Error al crear dieta: {str(e)}")
    
    def get_by_id(self, diet_id: int) -> Optional[Diet]:
        """
        Obtiene una dieta por ID.
        """
        try:
            model = self.session.query(DietModel).filter(DietModel.id == diet_id).first()
            return self._to_entity(model) if model else None
        except SQLAlchemyError as e:
            raise Exception(f"Error al obtener dieta por ID: {str(e)}")
    
    def get_by_advance_number(self, advance_number: int) -> Optional[Diet]:
        """
        Obtiene una dieta por número de anticipo.
        """
        try:
            model = self.session.query(DietModel).filter(
                DietModel.advance_number == advance_number
            ).first()
            return self._to_entity(model) if model else None
        except SQLAlchemyError as e:
            raise Exception(f"Error al obtener dieta por número de anticipo: {str(e)}")
    
    def list_by_status(self, status: DietStatus) -> List[Diet]:
        """
        Lista dietas por estado.
        """
        try:
            models = self.session.query(DietModel).filter(
                DietModel.status == status.value
            ).order_by(DietModel.advance_number.desc()).all()
            return [self._to_entity(model) for model in models]
        except SQLAlchemyError as e:
            raise Exception(f"Error al listar dietas por estado: {str(e)}")
    
    def get_all(self) -> List[Diet]:
        """
        Obtiene todas las dietas.
        """
        try:
            models = self.session.query(DietModel).order_by(
                DietModel.advance_number.desc()
            ).all()
            return [self._to_entity(model) for model in models]
        except SQLAlchemyError as e:
            raise Exception(f"Error al obtener todas las dietas: {str(e)}")
    
    def list_by_request_user(self, request_user_id: int) -> List[Diet]:
        """
        Lista dietas por solicitante.
        """
        try:
            models = self.session.query(DietModel).filter(
                DietModel.request_user_id == request_user_id
            ).order_by(DietModel.start_date.desc()).all()
            return [self._to_entity(model) for model in models]
        except SQLAlchemyError as e:
            raise Exception(f"Error al listar dietas por solicitante: {str(e)}")
    
    def list_by_date_range(self, start_date: date, end_date: date) -> List[Diet]:
        """
        Lista dietas por rango de fechas.
        """
        try:
            models = self.session.query(DietModel).filter(
                DietModel.start_date >= start_date,
                DietModel.end_date <= end_date
            ).order_by(DietModel.start_date.asc()).all()
            return [self._to_entity(model) for model in models]
        except SQLAlchemyError as e:
            raise Exception(f"Error al listar dietas por rango de fecha: {str(e)}")
    
    def list_pending_liquidation(self) -> List[Diet]:
        """
        Lista dietas pendientes de liquidación.
        """
        try:
            models = self.session.query(DietModel).filter(
                DietModel.status == DietStatus.REQUESTED.value
            ).order_by(DietModel.start_date.asc()).all()
            return [self._to_entity(model) for model in models]
        except SQLAlchemyError as e:
            raise Exception(f"Error al listar dietas pendientes de liquidación: {str(e)}")
    
    def update(self, diet: Diet) -> Optional[Diet]:
        """
        Actualiza una dieta existente.
        """
        try:
            model = self.session.query(DietModel).filter(DietModel.id == diet.id).first()
            if not model:
                return None
            
            if hasattr(diet, 'status') and diet.status != model.status:
                has_liquidation = self.session.query(
                    exists().where(DietLiquidationModel.diet_id == diet.id)
                ).scalar()
                
                if has_liquidation:
                    raise Exception(
                        f"No se puede cambiar el estado de una dieta que ya tiene liquidación"
                    )
            if diet.diet_service_id != model.diet_service_id:
                service_exists = self.session.query(
                    exists().where(DietServiceModel.id == diet.diet_service_id)
                ).scalar()
                
                if not service_exists:
                    raise Exception(f"No existe el servicio de dieta con ID {diet.diet_service_id}")
            
            if diet.advance_number != model.advance_number:
                advance_exists = self.session.query(DietModel).filter(
                    DietModel.advance_number == diet.advance_number,
                    DietModel.id != diet.id
                ).first()
                
                if advance_exists:
                    raise Exception(f"Ya existe otra dieta con el número de anticipo {diet.advance_number}")
                
            if diet.start_date > diet.end_date:
                raise Exception("La fecha de inicio no puede ser mayor a la fecha de fin")
            
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
        
        except IntegrityError as e:
            self.session.rollback()
            if "FOREIGN KEY constraint failed" in str(e):
                raise Exception(
                    f"Error de integridad: Verifique que existan las referencias"
                )
            elif "UNIQUE constraint" in str(e):
                raise Exception(f"Ya existe una dieta con el número de anticipo {diet.advance_number}")
            raise Exception(f"Error de integridad al actualizar dieta: {str(e)}")
            
        except SQLAlchemyError as e:
            self.session.rollback()
            raise Exception(f"Error de base de datos al actualizar dieta: {str(e)}")
        
        except Exception as e:
            self.session.rollback()
            if any(msg in str(e) for msg in ["No se puede cambiar", "No existe", "Ya existe", "fecha"]):
                raise
            raise Exception(f"Error al actualizar dieta: {str(e)}")
        
    def update_status(self, id: int, status: DietStatus) -> Optional[Diet]:
        """
        Actualiza solo el estado de una dieta.
        """
        try:
            model = self.session.query(DietModel).filter(DietModel.id == id).first()
            if not model:
                return None
            
            if model.status == DietStatus.LIQUIDATED.value and status != DietStatus.LIQUIDATED:
                raise Exception("No se puede cambiar el estado de una dieta ya liquidada")
            
            if status == DietStatus.LIQUIDATED:
                has_liquidation = self.session.query(
                    exists().where(DietLiquidationModel.diet_id == id)
                ).scalar()
                
                if not has_liquidation:
                    raise Exception(
                        f"No se puede marcar como liquidada una dieta sin liquidación"
                    )
            
            model.status = status
            self.session.commit()
            self.session.refresh(model)
            return self._to_entity(model)
            
        except Exception as e:
            self.session.rollback()
            if any(msg in str(e) for msg in ["No se puede cambiar", "No se puede marcar"]):
                raise
            raise Exception(f"Error al actualizar estado de dieta: {str(e)}")
    
    def delete(self, diet_id: int) -> bool:
        """
        Elimina una dieta.
        """
        try:
            model = self.session.query(DietModel).filter(DietModel.id == diet_id).first()
            if not model:
                return False
            
            has_liquidation = self.session.query(
                exists().where(DietLiquidationModel.diet_id == diet_id)
            ).scalar()
            
            if has_liquidation:
                raise Exception(
                    f"No se puede eliminar la dieta #{model.advance_number} "
                    f"porque tiene una liquidación asociada. "
                    f"Elimine primero la liquidación."
                )
            
            if model.status == DietStatus.LIQUIDATED.value:
                raise Exception(
                    f"No se puede eliminar una dieta ya liquidada (#{model.advance_number})"
                )
            
            if model:
                self.session.delete(model)
                self.session.commit()
                return True
            return False
        except IntegrityError as e:
            self.session.rollback()
            if "FOREIGN KEY constraint failed" in str(e):
                raise Exception(
                    "No se puede eliminar la dieta porque está siendo referenciada "
                    "por otros registros."
                )
            raise Exception(f"Error de integridad al eliminar dieta: {str(e)}")
            
        except SQLAlchemyError as e:
            self.session.rollback()
            raise Exception(f"Error de base de datos al eliminar dieta: {str(e)}")
        
        except Exception as e:
            self.session.rollback()
            if "No se puede eliminar" in str(e):
                raise
            raise Exception(f"Error al eliminar dieta: {str(e)}")
    
    def card_on_the_road(self, card_id) -> bool:
        """
        Verifica si una tarjeta está en uso en dietas solicitadas.
        """
        try:
            return self.session.query(DietModel).filter(
                DietModel.status == DietStatus.REQUESTED.value,
                DietModel.accommodation_payment_method == PaymentMethod.CARD.value, 
                DietModel.accommodation_card_id == card_id
            ).first() is not None
        except SQLAlchemyError as e:
            raise Exception(f"Error al verificar uso de tarjeta: {str(e)}")
    
    def get_last_advance_number(self) -> int:
        """
        Obtiene el último número de anticipo.
        """
        try:
            result = self.session.query(func.max(DietModel.advance_number)).scalar()
            return result if result else 0
        except SQLAlchemyError as e:
            raise Exception(f"Error al obtener el último número de anticipo: {str(e)}")
    
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