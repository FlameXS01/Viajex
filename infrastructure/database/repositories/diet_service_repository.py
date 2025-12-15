from typing import List, Optional
from sqlalchemy import exists
from sqlalchemy.orm import Session
from core.entities.diet_service import DietService
from core.repositories.diet_service_repository import DietServiceRepository
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from infrastructure.database.models import DietServiceModel, DietModel, DietLiquidationModel

class DietServiceRepositoryImpl(DietServiceRepository):
    """
    
    Implementación concreta del repositorio de servicios de dieta usando SQLAlchemy
    
    """
    
    def __init__(self, session: Session):
        self.session = session
    
    def create(self, diet_service: DietService) -> DietService:
        """
        Crea un nuevo servicio de dieta.
        
        Nota: Solo deberían existir 2 servicios: local y no local.
        """
        try:
            existing_service = self.get_by_local(diet_service.is_local)
            if existing_service:
                raise Exception(
                    f"Ya existe un servicio de dieta para "
                    f"{'local' if diet_service.is_local else 'no local'}. "
                    f"ID: {existing_service.id}"
                )
            if diet_service.breakfast_price <= 0:
                raise Exception("El precio del desayuno debe ser mayor a 0")
            if diet_service.lunch_price <= 0:
                raise Exception("El precio del almuerzo debe ser mayor a 0")
            if diet_service.dinner_price <= 0:
                raise Exception("El precio de la cena debe ser mayor a 0")
            if diet_service.accommodation_cash_price <= 0:
                raise Exception("El precio de alojamiento en efectivo debe ser mayor a 0")
            if diet_service.accommodation_card_price <= 0:
                raise Exception("El precio de alojamiento con tarjeta debe ser mayor a 0")
            
            model = DietServiceModel(
                is_local=diet_service.is_local,
                breakfast_price=diet_service.breakfast_price,
                lunch_price=diet_service.lunch_price,
                dinner_price=diet_service.dinner_price,
                accommodation_cash_price=diet_service.accommodation_cash_price,
                accommodation_card_price=diet_service.accommodation_card_price
            )
            
            # 5. Guardar
            self.session.add(model)
            self.session.commit()
            self.session.refresh(model)
            return self._to_entity(model)
            
        except IntegrityError as e:
            self.session.rollback()
            if "UNIQUE constraint failed" in str(e) or "duplicate key" in str(e):
                raise Exception(
                    f"Ya existe un servicio de dieta para "
                    f"{'local' if diet_service.is_local else 'no local'}"
                )
            raise Exception(f"Error de integridad al crear servicio de dieta: {str(e)}")
            
        except SQLAlchemyError as e:
            self.session.rollback()
            raise Exception(f"Error de base de datos al crear servicio de dieta: {str(e)}")
        
        except Exception as e:
            self.session.rollback()
            if any(msg in str(e) for msg in ["Ya existe", "precio", "debe ser mayor", "no puede ser mayor"]):
                raise
            raise Exception(f"Error al crear servicio de dieta: {str(e)}")
            
    def get_by_id(self, diet_service_id: int) -> Optional[DietService]:
        """
        Obtiene un servicio de dieta por ID.
        """
        try:
            model = self.session.query(DietServiceModel).filter(
                DietServiceModel.id == diet_service_id
            ).first()
            return self._to_entity(model) if model else None
        except SQLAlchemyError as e:
            raise Exception(f"Error al obtener servicio de dieta por ID: {str(e)}")
    
    def get_by_local(self, is_local: bool) -> Optional[DietService]:
        """
        Obtiene el servicio de dieta por tipo (local/no local).
        """
        try:
            model = self.session.query(DietServiceModel).filter(
                DietServiceModel.is_local == is_local
            ).first()
            return self._to_entity(model) if model else None
        except SQLAlchemyError as e:
            raise Exception(f"Error al obtener servicio de dieta por tipo: {str(e)}")
    
    def list_all(self) -> List[DietService]:
        """
        Lista todos los servicios de dieta.
        """
        try:
            models = self.session.query(DietServiceModel).order_by(
                DietServiceModel.is_local.desc()  
            ).all()
            return [self._to_entity(model) for model in models]
        except SQLAlchemyError as e:
            raise Exception(f"Error al listar todos los servicios de dieta: {str(e)}")
    
    def update(self, diet_service: DietService) -> Optional[DietService]:
        """
        Actualiza un servicio de dieta existente.
        """
        try:
            model = self.session.query(DietServiceModel).filter(
                DietServiceModel.id == diet_service.id
            ).first()
            if not model:
                return None
            
            if model.is_local != diet_service.is_local:
                other_exists = self.session.query(DietServiceModel).filter(
                    DietServiceModel.is_local == diet_service.is_local,
                    DietServiceModel.id != diet_service.id
                ).first()
                
                if other_exists:
                    raise Exception(
                        f"Ya existe un servicio de dieta para "
                        f"{'local' if diet_service.is_local else 'no local'}. "
                        f"No se puede cambiar el tipo."
                    )
                
            if diet_service.breakfast_price <= 0:
                raise Exception("El precio del desayuno debe ser mayor a 0")
            if diet_service.lunch_price <= 0:
                raise Exception("El precio del almuerzo debe ser mayor a 0")
            if diet_service.dinner_price <= 0:
                raise Exception("El precio de la cena debe ser mayor a 0")
            if diet_service.accommodation_cash_price <= 0:
                raise Exception("El precio de alojamiento en efectivo debe ser mayor a 0")
            if diet_service.accommodation_card_price <= 0:
                raise Exception("El precio de alojamiento con tarjeta debe ser mayor a 0")
            
            model.is_local = diet_service.is_local
            model.breakfast_price = diet_service.breakfast_price
            model.lunch_price = diet_service.lunch_price
            model.dinner_price = diet_service.dinner_price
            model.accommodation_cash_price = diet_service.accommodation_cash_price
            model.accommodation_card_price = diet_service.accommodation_card_price
           
            self.session.commit()
            self.session.refresh(model)
            return self._to_entity(model)
        
        except IntegrityError as e:
            self.session.rollback()
            if "UNIQUE constraint failed" in str(e):
                raise Exception(
                    f"Ya existe un servicio de dieta para "
                    f"{'local' if diet_service.is_local else 'no local'}"
                )
            raise Exception(f"Error de integridad al actualizar servicio de dieta: {str(e)}")
            
        except SQLAlchemyError as e:
            self.session.rollback()
            raise Exception(f"Error de base de datos al actualizar servicio de dieta: {str(e)}")
        
        except Exception as e:
            self.session.rollback()
            if any(msg in str(e) for msg in ["Ya existe", "No se puede cambiar", "precio", "debe ser mayor", "no puede ser mayor"]):
                raise
            raise Exception(f"Error al actualizar servicio de dieta: {str(e)}")
    
    def delete(self, diet_service_id: int) -> bool:
        """
        Elimina un servicio de dieta.
        """
        try:
            model = self.session.query(DietServiceModel).filter(
                DietServiceModel.id == diet_service_id
            ).first()

            if not model:
                return False
            
            used_in_diets = self.session.query(
                exists().where(DietModel.diet_service_id == diet_service_id)
            ).scalar()
            
            used_in_liquidations = self.session.query(
                exists().where(DietLiquidationModel.diet_service_id == diet_service_id)
            ).scalar()
            
            if used_in_diets or used_in_liquidations:  
                raise Exception(
                    f"No se puede eliminar el servicio de dieta para "
                    f"{'local' if model.is_local else 'no local'}. "
                    f"Está siendo usado dieta(s) o  liquidación(es)."
                )
            
            self.session.delete(model)
            self.session.commit()
            return True
            
        except IntegrityError as e:
            self.session.rollback()
            if "FOREIGN KEY constraint failed" in str(e):
                raise Exception(
                    "No se puede eliminar el servicio de dieta porque está siendo usado "
                    "en dietas o liquidaciones."
                )
            raise Exception(f"Error de integridad al eliminar servicio de dieta: {str(e)}")
            
        except SQLAlchemyError as e:
            self.session.rollback()
            raise Exception(f"Error de base de datos al eliminar servicio de dieta: {str(e)}")
        
        except Exception as e:
            self.session.rollback()
            if "No se puede eliminar" in str(e):
                raise
            raise Exception(f"Error al eliminar servicio de dieta: {str(e)}")
    
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