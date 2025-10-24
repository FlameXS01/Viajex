from core.repositories.dieta_anticipo_repository import DietaAnticipoRepository

class LiquidarDietaAnticipoUseCase:
    def __init__(self, dieta_anticipo_repository: DietaAnticipoRepository):
        self.dieta_anticipo_repository = dieta_anticipo_repository

    def execute(self, anticipo_id: int, numero_anticipo: str) -> tuple[bool, str]:
        anticipo = self.dieta_anticipo_repository.get_by_id(anticipo_id)
        if not anticipo:
            return False, "Anticipo no encontrado"

        if not anticipo.puede_liquidar:
            return False, "El anticipo no puede ser liquidado"

        try:
            success = self.dieta_anticipo_repository.liquidar_anticipo(anticipo_id, numero_anticipo)
            if success:
                return True, "Anticipo liquidado exitosamente"
            else:
                return False, "Error al liquidar anticipo"
        except Exception as e:
            return False, f"Error al liquidar anticipo: {str(e)}"