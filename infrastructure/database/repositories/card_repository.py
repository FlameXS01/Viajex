from sqlalchemy.orm import Session
from core.entities.cards import Card  
from core.repositories.card_repository import CardRepository
from infrastructure.database.models import CardModel, DietLiquidationModel, DietModel
from typing import Optional, List
from sqlalchemy.exc import IntegrityError, SQLAlchemyError


class CardRepositoryImpl(CardRepository):
    """Implementación concreta del repositorio usando SQLAlchemy"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def save(self, card: Card) -> Card:
        """Guarda o actualiza una tarjeta en la base de datos"""
        try:
            existing_card = self.db.query(CardModel).filter(CardModel.card_id == card.id).first()
            
            if existing_card:
                return self._update_existing_card(existing_card, card)
            else:
                return self._create_new_card(card)
        except IntegrityError as e:
            self.db.rollback()
            if "UNIQUE constraint failed" in str(e):
                raise Exception(f"Ya existe una tarjeta con el número {card.card_number}")
            raise Exception(f"Error de integridad al guardar tarjeta: {str(e)}")
        except SQLAlchemyError as e:
            self.db.rollback()
            raise Exception(f"Error de base de datos al guardar tarjeta: {str(e)}")
    
    def _create_new_card(self, card: Card) -> Card:
        """Crea una nueva tarjeta"""
        db_card = CardModel(
            card_id=card.id,
            card_number=card.card_number,
            card_pin=card.card_pin,  
            is_active=card.is_active,
            with_money=getattr(card, 'with_money', True),  
            balance=float(card.balance) if card.balance is not None else 0.0
        )
        self.db.add(db_card)
        self.db.commit()
        self.db.refresh(db_card)
        return self._to_entity(db_card)
    
    def _update_existing_card(self, db_card: CardModel, card: Card) -> Card:
        """Actualiza una tarjeta existente"""
        db_card.card_number = card.card_number
        db_card.card_pin = card.card_pin  
        db_card.balance = float(card.balance) if card.balance is not None else db_card.balance
        db_card.is_active = card.is_active
        db_card.with_money = getattr(card, 'with_money', db_card.with_money)
        
        self.db.commit()
        self.db.refresh(db_card)
        return self._to_entity(db_card)
    
    def get_by_id(self, card_id: int) -> Optional[Card]:
        """Obtiene una tarjeta por ID desde la base de datos"""
        try:
            db_card = self.db.query(CardModel).filter(CardModel.card_id == card_id).first()  
            return self._to_entity(db_card) if db_card else None
        except SQLAlchemyError as e:
            raise Exception(f"Error al obtener tarjeta por ID: {str(e)}")
    
    def get_by_card_number(self, card_number: str) -> Optional[Card]:
        """Obtiene una tarjeta por card_number desde la base de datos"""
        try:
            db_card = self.db.query(CardModel).filter(CardModel.card_number == card_number).first()
            return self._to_entity(db_card) if db_card else None
        except SQLAlchemyError as e:
            raise Exception(f"Error al obtener tarjeta por número: {str(e)}")
    
    def get_all(self) -> List[Card]:  
        """Obtiene todos las tarjetas de la base de datos"""
        try:
            db_cards = self.db.query(CardModel).order_by(CardModel.card_number.asc()).all()
            return [self._to_entity(card) for card in db_cards]
        except SQLAlchemyError as e:
            raise Exception(f"Error al obtener todas las tarjetas: {str(e)}")
    
    def get_aviable(self) -> List[Card]:  
        """Obtiene todas las tarjetas activas de la base de datos"""
        try:
            db_cards = self.db.query(CardModel).filter(CardModel.is_active).all()
            return [self._to_entity(card) for card in db_cards]
        except SQLAlchemyError as e:
            raise Exception(f"Error al obtener tarjetas disponibles: {str(e)}")
    
    def update(self, card: Card) -> Optional[Card]:  
        """Actualiza una tarjeta existente en la base de datos"""
        try:
            db_card = self.db.query(CardModel).filter(CardModel.card_id == card.id).first()  
            if db_card:
                return self._update_existing_card(db_card, card)
            return None
        except IntegrityError as e:
            self.db.rollback()
            if "UNIQUE constraint failed" in str(e):
                raise Exception(f"Ya existe una tarjeta con el número {card.card_number}")
            raise Exception(f"Error de integridad al actualizar tarjeta: {str(e)}")
        except SQLAlchemyError as e:
            self.db.rollback()
            raise Exception(f"Error de base de datos al actualizar tarjeta: {str(e)}")
    
    def delete(self, card_id: int) -> bool:
        """Elimina una tarjeta de la base de datos con validaciones"""
        try:
            db_card = self.db.query(CardModel).filter(CardModel.card_id == card_id).first()  
            if not db_card:
                return False
            
            used_in_diet = self.db.query(DietModel).filter(
                DietModel.accommodation_card_id == card_id
            ).first() is not None
            
            used_in_liquidation = self.db.query(DietLiquidationModel).filter(
                DietLiquidationModel.accommodation_card_id == card_id
            ).first() is not None
            
            if used_in_diet or used_in_liquidation:
                raise Exception(
                    f"No se puede eliminar la tarjeta '{db_card.card_number}'. "
                )
            
            if db_card.balance and db_card.balance > 0:
                raise Exception(
                    f"No se puede eliminar la tarjeta '{db_card.card_number}'. "
                    f"Tiene un saldo de ${db_card.balance:.2f}. "
                    f"Transfiera o retire el saldo primero."
                )
            
            self.db.delete(db_card)
            self.db.commit()
            return True
            
        except Exception as e:
            self.db.rollback()
            if "No se puede eliminar" in str(e):
                raise
            if "IntegrityError" in str(type(e).__name__):
                raise Exception(
                    f"No se puede eliminar la tarjeta porque está siendo usada en operaciones. "
                    f"Elimine o modifique las operaciones relacionadas primero."
                )
            raise Exception(f"Error al eliminar tarjeta: {str(e)}")
    
    def recharge(self, card_id: int, amount: float) -> bool:
        """Recarga una tarjeta"""
        try:
            db_card = self.db.query(CardModel).filter(CardModel.card_id == card_id).first()  
            if db_card:
                if not db_card.is_active:
                    raise Exception("No se puede recargar una tarjeta inactiva")
                
                if amount <= 0:
                    raise Exception("El monto a recargar debe ser mayor a cero")
                
                db_card.balance += amount
                self.db.commit()
                return True
            return False
        except Exception as e:
            self.db.rollback()
            if "No se puede recargar" in str(e):
                raise
            raise Exception(f"Error al recargar tarjeta: {str(e)}")
                
    def discount(self, card_id: int, amount: float) -> bool:
        """Recarga una tarjeta"""
        try:
            db_card = self.db.query(CardModel).filter(CardModel.card_id == card_id).first()  
            if db_card:
                db_card.balance -= amount
                self.db.commit()
                return True
            return False
        except Exception as e:
            self.db.rollback()
            if any(msg in str(e) for msg in ["No se puede descontar", "Saldo insuficiente"]):
                raise
            raise Exception(f"Error al descontar de tarjeta: {str(e)}")
        
    def exists_by_card_number(self, card_number: str) -> bool:
        """Verifica si existe una tarjeta por número de tarjeta"""
        try:
            return self.db.query(CardModel).filter(CardModel.card_number == card_number).first() is not None
        except SQLAlchemyError as e:
            raise Exception(f"Error al verificar existencia de tarjeta: {str(e)}")
    
    def get_active_cards(self, is_active: bool = True) -> List[Card]:
        """Obtiene las tarjetas activas o inactivas"""
        try:
            db_cards = self.db.query(CardModel).filter(CardModel.is_active == is_active).all()
            return [self._to_entity(card) for card in db_cards]
        except SQLAlchemyError as e:
            raise Exception(f"Error al obtener tarjetas por estado: {str(e)}")
    
    def get_by_status(self, is_active: bool) -> List[Card]:
        """Obtiene tarjetas por estado (alias de get_active_cards)"""
        return self.get_active_cards(is_active)
    
    def _to_entity(self, db_card: CardModel) -> Card:
        if not db_card:
            return None
            
        return Card(
            id=db_card.card_id,  
            card_number=db_card.card_number,
            card_pin=db_card.card_pin,  
            is_active=db_card.is_active,
            balance=float(db_card.balance) if db_card.balance is not None else 0.0
        )