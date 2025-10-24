from typing import Optional, Tuple
from core.entities.dieta import DietaLiquidacion
from core.repositories.dieta_liquidacion_repository import DietaLiquidacionRepository
from core.repositories.dieta_anticipo_repository import DietaAnticipoRepository
from core.entities.enums import EstadoAnticipo
class CrearDietaLiquidacionUseCase:
    def __init__(self, dieta_liquidacion_repository: DietaLiquidacionRepository, 
                 dieta_anticipo_repository: DietaAnticipoRepository):
        self.dieta_liquidacion_repository = dieta_liquidacion_repository
        self.dieta_anticipo_repository = dieta_anticipo_repository

    def execute(self, anticipo_id: int, numero_liquidacion: str) -> tuple[Optional[DietaLiquidacion], str]:
        # Obtener el anticipo
        anticipo = self.dieta_anticipo_repository.get_by_id(anticipo_id)
        if not anticipo:
            return None, "Anticipo no encontrado"

        # Verificar que el anticipo esté liquidado
        if not anticipo.estado == EstadoAnticipo.LIQUIDADA:
            return None, "El anticipo debe estar liquidado para crear la liquidación"

        # Crear la liquidación a partir del anticipo
        liquidacion = DietaLiquidacion(
            en_territorio=anticipo.en_territorio,
            creada_at=anticipo.creada_at,
            descripcion=f"Liquidación de {anticipo.descripcion}",
            es_grupal=anticipo.es_grupal,
            cantidad_personas=anticipo.cantidad_personas,
            opciones=anticipo.opciones.copy()
        )

        try:
            # Liquidar la liquidación
            liquidacion.liquidar(numero_liquidacion)
            created_liquidacion = self.dieta_liquidacion_repository.create(liquidacion)
            return created_liquidacion, "Liquidación creada exitosamente"
        except Exception as e:
            return None, f"Error al crear liquidación: {str(e)}"