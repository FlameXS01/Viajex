from sqlalchemy.orm import Session
from core.entities.cards import Card  
from core.repositories.card_repository import CardRepository
from infrastructure.database.models import CardModel
from typing import Optional, List
from decimal import Decimal

class CardRepositoryImpl(CardRepository):
    """Implementación concreta del repositorio usando SQLAlchemy"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def save(self, card: Card) -> Card:
        """Guarda una tarjeta en la base de datos"""
        db_card = CardModel(
            card_id=card.card_id,
            card_number=card.card_number,
            card_pin=card.card_pin,  # ✅ Coma añadida
            is_active=card.is_active,
            balance=card.balance  
        )
        self.db.add(db_card)
        self.db.commit()
        self.db.refresh(db_card)
        return self._to_entity(db_card)
    
    def get_by_id(self, card_id: int) -> Optional[Card]:
        """Obtiene una tarjeta por ID desde la base de datos"""
        db_card = self.db.query(CardModel).filter(CardModel.card_id == card_id).first()  # ✅ Filtro corregido
        return self._to_entity(db_card) if db_card else None
    
    def get_by_card_number(self, card_number: str) -> Optional[Card]:
        """Obtiene una tarjeta por card_number desde la base de datos"""
        db_card = self.db.query(CardModel).filter(CardModel.card_number == card_number).first()
        return self._to_entity(db_card) if db_card else None
    
    def get_all(self) -> List[Card]:  # ✅ Tipo corregido
        """Obtiene todos las tarjetas de la base de datos"""
        db_cards = self.db.query(CardModel).all()
        return [self._to_entity(card) for card in db_cards]
    
    def update(self, card: Card) -> Card:  # ✅ Tipo corregido
        """Actualiza una tarjeta existente en la base de datos"""
        db_card = self.db.query(CardModel).filter(CardModel.card_id == card.card_id).first()  # ✅ Filtro corregido
        if db_card:
            db_card.card_number = card.card_number
            db_card.card_pin = card.card_pin  # ✅ Campo añadido
            db_card.balance = card.balance  # ✅ Campo añadido
            db_card.is_active = card.is_active
            self.db.commit()
            self.db.refresh(db_card)
        return self._to_entity(db_card)
    
    def delete(self, card_id: int) -> bool:
        """Elimina una tarjeta de la base de datos"""
        db_card = self.db.query(CardModel).filter(CardModel.card_id == card_id).first()  # ✅ Filtro corregido
        if db_card:
            self.db.delete(db_card)
            self.db.commit()
            return True
        return False
    
    def _to_entity(self, db_card: CardModel) -> Card:
        """Convierte el modelo de base de datos a entidad de dominio"""
        return Card(
            card_id=db_card.card_id,  # ✅ Campo corregido
            card_number=db_card.card_number,
            card_pin=db_card.card_pin,  # ✅ Campo añadido
            is_active=db_card.is_active,
            amount=Decimal(str(db_card.amount)) if db_card.amount else Decimal('0')  # ✅ Campo añadido
        )
    
    
    
    def exists_by_card_number() -> List[Card]:
        pass
    def get_active_cards(is_active: bool) -> List[Card]:
        pass
    def get_by_status(card_number: str) -> bool:
        pass
    