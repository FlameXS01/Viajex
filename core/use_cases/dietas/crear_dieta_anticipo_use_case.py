from typing import Optional
from core.entities.dieta import DietaAnticipo
from core.entities.opciones import OpcionLocal, OpcionForeign
from core.repositories.dieta_anticipo_repository import DietaAnticipoRepository
from core.entities.enums import TipoServicio, MetodoPagoHospedaje

class CrearDietaAnticipoUseCase:
    def __init__(self, dieta_anticipo_repository: DietaAnticipoRepository):
        self.dieta_anticipo_repository = dieta_anticipo_repository

    def execute(self, en_territorio: bool, creada_at: str, descripcion: str, 
                es_grupal: bool, cantidad_personas: int, servicios: list) -> tuple[Optional[DietaAnticipo], str]:
        # Crear la dieta base
        anticipo = DietaAnticipo(
            
            en_territorio=en_territorio,
            creada_at=creada_at,
            descripcion=descripcion,
            es_grupal=es_grupal,
            cantidad_personas=cantidad_personas
        )

        # Agregar opciones según el territorio
        for servicio in servicios:
            # Aquí podrías tener lógica para determinar el método de pago si es hospedaje
            metodo_pago = MetodoPagoHospedaje.EFECTIVO if servicio == TipoServicio.HOSPEDAJE else None
            anticipo.agregar_opcion(servicio, metodo_pago)

        try:
            created_anticipo = self.dieta_anticipo_repository.create(anticipo)
            return created_anticipo, "Anticipo de dieta creado exitosamente"
        except Exception as e:
            return None, f"Error al crear anticipo: {str(e)}"