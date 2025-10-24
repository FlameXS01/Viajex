from typing import Optional
from .enums import EstadoAnticipo, TipoServicio, MetodoPagoHospedaje
from .dieta import DietaAnticipo, DietaLiquidacion
from .opciones import OpcionBase

class DietaFactory:
    """Factory para crear dietas con configuraciones comunes"""
    
    @staticmethod
    def crear_anticipo_local(
        creada_at: str,
        descripcion: str,
        es_grupal: bool = False,
        cantidad_personas: int = 1,
        servicios: list[TipoServicio] = []
        
    ) -> DietaAnticipo:
        """Crea un anticipo en territorio local"""
        dieta = DietaAnticipo(
            en_territorio=True,
            creada_at=creada_at,
            descripcion=descripcion,
            es_grupal=es_grupal,
            cantidad_personas=cantidad_personas
        )
        
        if servicios is None:
            servicios = [TipoServicio.DESAYUNO, TipoServicio.ALMUERZO, TipoServicio.COMIDA]
        
        for servicio in servicios:
            metodo_pago = MetodoPagoHospedaje.EFECTIVO if servicio == TipoServicio.HOSPEDAJE else None
            dieta.agregar_opcion(servicio, metodo_pago)
        
        return dieta
    
    @staticmethod
    def crear_anticipo_foreign(
        creada_at: str,
        descripcion: str,
        es_grupal: bool = False,
        cantidad_personas: int = 1,
        servicios: list[TipoServicio] = []
    ) -> DietaAnticipo:
        """Crea un anticipo fuera del territorio"""
        dieta = DietaAnticipo(
            en_territorio=True,
            creada_at=creada_at,
            descripcion=descripcion,
            es_grupal=es_grupal,
            cantidad_personas=cantidad_personas
        )
        
        if servicios is None:
            servicios = [TipoServicio.DESAYUNO, TipoServicio.ALMUERZO, TipoServicio.COMIDA, TipoServicio.HOSPEDAJE]
        
        for servicio in servicios:
            metodo_pago = MetodoPagoHospedaje.EFECTIVO if servicio == TipoServicio.HOSPEDAJE else None
            dieta.agregar_opcion(servicio, metodo_pago)
        
        return dieta
    
    @staticmethod
    def crear_liquidacion_desde_anticipo(anticipo: DietaAnticipo, numero_liquidacion: str) -> DietaLiquidacion:
        """Crea una liquidación basada en un anticipo existente"""
        if anticipo.estado != EstadoAnticipo.LIQUIDADA:
            raise ValueError("El anticipo debe estar liquidado para crear liquidación")
        
        liquidacion = DietaLiquidacion(
            en_territorio=anticipo.en_territorio,
            creada_at=anticipo.creada_at,
            descripcion=f"Liquidación de {anticipo.descripcion}",
            es_grupal=anticipo.es_grupal,
            cantidad_personas=anticipo.cantidad_personas,
            opciones=anticipo.opciones.copy()
        )
        
        liquidacion.liquidar(numero_liquidacion)
        return liquidacion