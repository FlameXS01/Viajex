from typing import Optional
from core.entities.diet_service import DietService
from core.repositories.diet_service_repository import DietServiceRepository


class EditDietServiceUseCase:
    """Caso de uso para editar un servicio de dieta existente"""

    def __init__(self, diet_service_repository: DietServiceRepository):
        self.diet_service_repository = diet_service_repository

    def execute(
        self,
        service_id: int,
        is_local: bool,
        breakfast_price: float,
        lunch_price: float,
        dinner_price: float,
        accommodation_cash_price: float,
        accommodation_card_price: float,
    ) -> Optional[DietService]:
        """
        Ejecuta el caso de uso para editar un servicio de dieta existente

        Args:
            is_local: Si el servicio es local o no
            breakfast_price: Precio del desayuno
            lunch_price: Precio del almuerzo
            dinner_price: Precio de la comida
            accommodation_cash_price: Precio de alojamiento en efectivo
            accommodation_card_price: Precio de alojamiento con tarjeta

        Returns:
            El servicio de dieta editado o None si no se encontró el servicio
        """
        # Validaciones de precios no negativos
        if breakfast_price < 0:
            raise ValueError("El precio del desayuno no puede ser negativo")

        if lunch_price < 0:
            raise ValueError("El precio del almuerzo no puede ser negativo")

        if dinner_price < 0:
            raise ValueError("El precio de la comida no puede ser negativo")

        if accommodation_cash_price < 0:
            raise ValueError(
                "El precio de alojamiento en efectivo no puede ser negativo"
            )

        if accommodation_card_price < 0:
            raise ValueError(
                "El precio de alojamiento con tarjeta no puede ser negativo"
            )

        # PRIMERO obtener el servicio existente
        existing_service = self.diet_service_repository.get_by_local(is_local)
        if not existing_service:
            return None

        # # Validar unicidad SOLO si se está cambiando el tipo (local/fuera de provincia)
        # if existing_service.is_local != is_local:
        #     existing_same_type = self.diet_service_repository.get_by_local(is_local)
        #     if existing_same_type and existing_same_type.id != service_id:
        #         raise ValueError(f"Ya existe un servicio {'local' if is_local else 'fuera de provincia'}. "
        #                        f"Modifique el existente (ID: {existing_same_type.id})")

        # # Verificar si hay conflicto con OTRO servicio del mismo tipo
        # else:
        #     # Si se mantiene el mismo tipo, verificar si hay otro servicio con el mismo tipo
        #     other_service_same_type = self.diet_service_repository.get_by_local(is_local)
        #     if other_service_same_type and other_service_same_type.id != service_id:
        #         raise ValueError(f"Ya existe un servicio {'local' if is_local else 'fuera de provincia'}. "
        #                        f"Modifique el existente (ID: {other_service_same_type.id})")

        # Actualizar los atributos del servicio
        existing_service.is_local = is_local
        existing_service.breakfast_price = breakfast_price
        existing_service.lunch_price = lunch_price
        existing_service.dinner_price = dinner_price
        existing_service.accommodation_cash_price = accommodation_cash_price
        existing_service.accommodation_card_price = accommodation_card_price

        # Guardar los cambios en el repositorio
        return self.diet_service_repository.update(existing_service)
