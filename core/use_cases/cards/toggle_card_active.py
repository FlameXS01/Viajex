from core.entities.card import Card  # pyright: ignore[reportMissingImports] # ✅ PascalCase
from core.repositories.card_repository import CardRepository  # pyright: ignore[reportMissingImports] # ✅ PascalCase

class ToggleCardActiveUseCase:
    """
    Caso de uso para alternar el estado activo/inactivo de una tarjeta
    """
    
    def __init__(self, card_repository: CardRepository):
        self.card_repository = card_repository

    def execute(self, card_id: int) -> Card:
        """
        Alterna el estado activo/inactivo de una tarjeta
        
        Args:
            card_id: ID de la tarjeta a modificar
            
        Returns:
            Card: La tarjeta actualizada
            
        Raises:
            ValueError: Si la tarjeta no existe o no se puede modificar
        """
        if not card_id or card_id <= 0:
            raise ValueError("ID de tarjeta inválido")
        
        # Obtener la tarjeta (usando nombre diferente al import)
        found_card = self.card_repository.get_by_id(card_id)
        if not found_card:
            raise ValueError("Tarjeta no encontrada")
        
        # Validar reglas de negocio adicionales
        self._validate_can_toggle(found_card)
        
        # Alternar estado usando métodos de la entidad
        if found_card.is_active:
            found_card.deactivate()
        else:
            found_card.activate()
        
        # Guardar cambios
        return self.card_repository.update(found_card)
    
    def _validate_can_toggle(self, card: Card) -> None:
        """
        Valida si la tarjeta puede cambiar de estado
        
        Raises:
            ValueError: Si no se puede alternar el estado
        """
        # Ejemplo: No desactivar tarjetas con saldo positivo
        if card.is_active and card.balance > 0:
            raise ValueError("No se puede desactivar una tarjeta con saldo positivo")
        
        # Ejemplo: No reactivar tarjetas marcadas como bloqueadas permanentemente
        # if hasattr(card, 'is_permanently_blocked') and card.is_permanently_blocked:
        #     raise ValueError("No se puede reactivar una tarjeta bloqueada permanentemente")