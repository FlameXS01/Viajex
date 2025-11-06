from core.entities.cards import Card
from core.repositories.card_repository import CardRepository
from decimal import Decimal

class CreateCardUseCase:
    """Caso de uso para la creación de nuevas tarjetas"""
    
    def __init__(self, card_repository: CardRepository):
        self.card_repository = card_repository
    
    def execute(self, card_number: str, card_pin: str, initial_balance: float = 0.0) -> Card:
        """
        Ejecuta el caso de uso para crear una tarjeta
        
        Args:
            card_number: Número de la tarjeta (16 dígitos)
            card_pin: PIN de la tarjeta (4 dígitos)
            initial_balance: Saldo inicial (opcional, default 0.0)
            
        Returns:
            Card: La tarjeta creada
            
        Raises:
            ValueError: Si la tarjeta ya existe o datos inválidos
        """
        # Verificar si la tarjeta ya existe
        existing_card = self.card_repository.get_by_card_number(card_number)
        if existing_card:
            raise ValueError("El número de la tarjeta ya está en uso")
        
        # Validaciones básicas
        if len(card_number) != 16 or not card_number.isdigit():
            raise ValueError("El número de tarjeta debe tener 16 dígitos")
        
        if len(card_pin) != 4 or not card_pin.isdigit():
            raise ValueError("El PIN debe tener 4 dígitos")
        
        if initial_balance < 0:
            raise ValueError("El saldo inicial no puede ser negativo")
        
        # Crear la tarjeta
        # El card_id será asignado por el repositorio
        card = Card(
            card_id=0,  # Temporal, se asignará al guardar
            card_number=card_number,
            card_pin=card_pin,
            is_active=True,
            balance=Decimal(str(initial_balance))
        )
        
        # Guardar en el repositorio
        return self.card_repository.save(card)