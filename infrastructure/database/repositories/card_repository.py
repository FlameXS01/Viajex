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
        """Guarda o actualiza una tarjeta en la base de datos"""
        existing_card = self.db.query(CardModel).filter(CardModel.card_id == card.id).first()
        
        if existing_card:
            return self._update_existing_card(existing_card, card)
        else:
            return self._create_new_card(card)
    
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
        db_card = self.db.query(CardModel).filter(CardModel.card_id == card_id).first()  
        return self._to_entity(db_card) if db_card else None
    
    def get_by_card_number(self, card_number: str) -> Optional[Card]:
        """Obtiene una tarjeta por card_number desde la base de datos"""
        db_card = self.db.query(CardModel).filter(CardModel.card_number == card_number).first()
        return self._to_entity(db_card) if db_card else None
    
    def get_all(self) -> List[Card]:  
        """Obtiene todos las tarjetas de la base de datos"""
        db_cards = self.db.query(CardModel).all()
        return [self._to_entity(card) for card in db_cards]
    
    def update(self, card: Card) -> Optional[Card]:  
        """Actualiza una tarjeta existente en la base de datos"""
        db_card = self.db.query(CardModel).filter(CardModel.card_id == card.id).first()  
        if db_card:
            return self._update_existing_card(db_card, card)
        return None
    
    def delete(self, card_id: int) -> bool:
        """Elimina una tarjeta de la base de datos"""
        db_card = self.db.query(CardModel).filter(CardModel.card_id == card_id).first()  
        if db_card:
            self.db.delete(db_card)
            self.db.commit()
            return True
        return False
    
    def exists_by_card_number(self, card_number: str) -> bool:
        """Verifica si existe una tarjeta por número de tarjeta"""
        return self.db.query(CardModel).filter(CardModel.card_number == card_number).first() is not None
    
    def get_active_cards(self, is_active: bool = True) -> List[Card]:
        """Obtiene las tarjetas activas o inactivas"""
        db_cards = self.db.query(CardModel).filter(CardModel.is_active == is_active).all()
        return [self._to_entity(card) for card in db_cards]
    
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