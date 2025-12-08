from abc import ABC, abstractmethod
from typing import List, Optional
from core.entities.cards import Card


class CardRepository(ABC):
    """
    Interfaz abstracta para el repositorio de Tarjetas.
    Define los métodos que cualquier implementación debe tener.
    """
    
    @abstractmethod
    def save(self, card: Card) -> Card:
        """Guarda una nueva tarjeta o actualiza una existente"""
        pass
    
    @abstractmethod
    def get_by_id(self, card_id: int) -> Optional[Card]:
        """Obtiene una tarjeta por su ID"""
        pass
    
    @abstractmethod
    def get_by_card_number(self, card_number: str) -> Optional[Card]:
        """Obtiene una Tarjeta por su número de Tarjeta"""
        pass
    
    @abstractmethod
    def get_all(self) -> List[Card]:
        """Obtiene todas las Tarjetas del sistema"""
        pass
    
    @abstractmethod
    def update(self, card: Card) -> Card:
        """Actualiza una tarjeta existente"""
        pass
    
    @abstractmethod
    def delete(self, card_id: int) -> bool:  
        """Elimina una Tarjeta por su ID"""
        pass

    @abstractmethod
    def recharge(self, card_id: int, amount: float) -> bool:  
        """Recarga una Tarjeta"""
        pass

    @abstractmethod
    def discount(self, card_id: int, amount: float) -> bool:  
        """Descarga una Tarjeta"""
        pass
    
    @abstractmethod
    def get_active_cards(self) -> List[Card]:
        """Obtiene todas las tarjetas activas"""
        pass
    
    @abstractmethod
    def get_by_status(self, is_active: bool) -> List[Card]:
        """Obtiene tarjetas filtradas por estado activo/inactivo"""
        pass
    
    @abstractmethod
    def exists_by_card_number(self, card_number: str) -> bool:
        """Verifica si existe una tarjeta con el número dado"""
        pass