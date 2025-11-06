from typing import Optional
from core.entities.cards import Card
from core.repositories.card_repository import CardRepository
from infrastructure.security.password_hasher import PasswordHasher

class CreateCardUseCase:
    def __init__(self, card_repository: CardRepository, password_hasher: PasswordHasher):
        self.card_repository = card_repository
        self.password_hasher = password_hasher

    def execute(self, card_number: str, card_pin: str, balance: float) -> Optional[Card]:
        # Validar que el número de tarjeta tenga entre 12 y 16 dígitos
        if len(card_number) < 12 or len(card_number) > 16 or not card_number.isdigit():
            raise ValueError("El número de tarjeta debe tener entre 12 y 16 dígitos")
        
        # Validar que el PIN tenga 4 dígitos
        if len(card_pin) != 4 or not card_pin.isdigit():
            raise ValueError("El PIN debe tener exactamente 4 dígitos")
        
        # Validar que el monto sea positivo
        if balance < 0:
            raise ValueError("El monto no puede ser negativo")
        
        # Verificar si la tarjeta ya existe
        if self.card_repository.get_by_card_number(card_number):
            raise ValueError("Ya existe una tarjeta con este número")
        
        # Hashear el PIN antes de guardarlo
        hashed_pin = self.password_hasher.hash(card_pin)
        
        # Crear la entidad Card
        card = Card(
            card_number=card_number,
            card_pin=hashed_pin,
            balance=balance,
            is_active=True
        )
        
        # Guardar en el repositorio
        return self.card_repository.save(card)