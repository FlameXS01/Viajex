from core.entities.cards import Card
from core.repositories.card_repository import CardRepository

class UpdateCardUseCase:
    """Caso de uso para actualizar información de una tarjeta"""
    
    def __init__(self, card_repository: CardRepository):
        self.card_repository = card_repository

    def execute(self, card_id: int, card_number: str, card_pin: str) -> Card:
        """
        Actualiza la información básica de una tarjeta
        
        Args:
            card_id: ID de la tarjeta a actualizar
            card_number: Nuevo número de tarjeta
            card_pin: Nuevo PIN de la tarjeta
            
        Returns:
            Card: Tarjeta actualizada
            
        Raises:
            ValueError: Si la tarjeta no existe o hay conflictos
        """
        # Validar parámetros de entrada
        if not card_id or card_id <= 0:
            raise ValueError("ID de tarjeta inválido")
        
        if not card_number or len(card_number) != 16 or not card_number.isdigit():
            raise ValueError("El número de tarjeta debe tener 16 dígitos")
        
        if not card_pin or len(card_pin) != 4 or not card_pin.isdigit():
            raise ValueError("El PIN debe tener 4 dígitos")

        # Obtener tarjeta existente
        card = self.card_repository.get_by_id(card_id)
        if not card:
            raise ValueError("Tarjeta no encontrada")

        # Verificar si el nuevo número ya existe (excluyendo la tarjeta actual)
        existing_card = self.card_repository.get_by_card_number(card_number)
        if existing_card and existing_card.card_id != card_id:  # ✅ Corregido atributo
            raise ValueError("El número de tarjeta ya está en uso")

        # Verificar si realmente hay cambios para evitar operaciones innecesarias
        if card.card_number == card_number and card.card_pin == card_pin:
            return card  # No hay cambios necesarios

        # Actualizar campos (SOLO los que deben cambiar)
        card.card_number = card_number
        card.card_pin = card_pin  # ✅ Corregido: asignar PIN, no ID

        # La entidad se valida automáticamente en __post_init__ si está implementado

        return self.card_repository.update(card)