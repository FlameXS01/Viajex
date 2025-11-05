from dataclasses import dataclass
from typing import ClassVar
from decimal import Decimal

@dataclass
class Card:
    card_id: int
    card_number: str
    card_pin: str
    is_active: bool
    balance: Decimal  
    
    # Constantes de validación
    CARD_NUMBER_LENGTH: ClassVar[int] = 16
    PIN_LENGTH: ClassVar[int] = 4
    
    def __post_init__(self):
        self.validate()
    
    def validate(self):
        """Valida la integridad de la tarjeta"""
        if len(self.card_number) != self.CARD_NUMBER_LENGTH or not self.card_number.isdigit():
            raise ValueError(f"Card number must be {self.CARD_NUMBER_LENGTH} digits")
        
        if len(self.card_pin) != self.PIN_LENGTH or not self.card_pin.isdigit():
            raise ValueError(f"PIN must be {self.PIN_LENGTH} digits")
        
        if self.balance < Decimal('0'):
            raise ValueError("Balance cannot be negative")
    
    def activate(self) -> None:
        """Activa la tarjeta"""
        self.is_active = True
    
    def deactivate(self) -> None:
        """Desactiva la tarjeta"""
        self.is_active = False
    
    def recharge(self, amount: Decimal) -> None:
        """Recarga saldo en la tarjeta"""
        if amount <= Decimal('0'):
            raise ValueError("Recharge amount must be positive")
        self.balance += amount
    
    def charge(self, amount: Decimal) -> bool:
        """Realiza un cargo en la tarjeta"""
        if not self.is_active:
            raise ValueError("Cannot charge inactive card")
        
        if amount <= Decimal('0'):
            raise ValueError("Charge amount must be positive")
        
        if self.balance < amount:
            return False  
        
        self.balance -= amount
        return True  
    
    def has_sufficient_balance(self, amount: Decimal) -> bool:
        """Verifica si hay saldo suficiente"""
        return self.balance >= amount and self.is_active
    
    def get_mask_card_number(self) -> str:
        """Retorna el número de tarjeta enmascarado"""
        return f"****-****-****-{self.card_number[-4:]}"