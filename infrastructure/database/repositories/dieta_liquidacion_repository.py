from sqlalchemy.orm import Session, joinedload
from typing import List, Optional
from core.entities.dieta import DietaLiquidacion
from core.entities.opciones import OpcionLocal, OpcionForeign
from core.repositories.dieta_liquidacion_repository import DietaLiquidacionRepository
from core.entities.enums import EstadoLiquidacion, TipoServicio, MetodoPagoHospedaje
from infrastructure.database.models import DietaLiquidacionModel, OpcionModel

class SQLAlchemyDietaLiquidacionRepository(DietaLiquidacionRepository):
    
    def __init__(self, session: Session):
        self.session = session
    
    def get_by_id(self, liquidacion_id: int) -> Optional[DietaLiquidacion]:
        dieta_model = self.session.query(DietaLiquidacionModel)\
            .options(joinedload(DietaLiquidacionModel.opciones))\
            .filter_by(id=liquidacion_id).first()
        return self._to_entity(dieta_model) if dieta_model else None
    
    def get_by_numero_liquidacion(self, numero_liquidacion: str) -> Optional[DietaLiquidacion]:
        dieta_model = self.session.query(DietaLiquidacionModel)\
            .options(joinedload(DietaLiquidacionModel.opciones))\
            .filter_by(numero_liquidacion=numero_liquidacion).first()
        return self._to_entity(dieta_model) if dieta_model else None
    
    def get_all(self) -> List[DietaLiquidacion]:
        dieta_models = self.session.query(DietaLiquidacionModel)\
            .options(joinedload(DietaLiquidacionModel.opciones)).all()
        return [self._to_entity(model) for model in dieta_models]
    
    def create(self, liquidacion: DietaLiquidacion) -> DietaLiquidacion:
        liquidacion_model = DietaLiquidacionModel(
            en_territorio=liquidacion.en_territorio,
            creada_at=liquidacion.creada_at,
            descripcion=liquidacion.descripcion,
            es_grupal=liquidacion.es_grupal,
            cantidad_personas=liquidacion.cantidad_personas,
            estado_liquidacion=EstadoLiquidacion(liquidacion.estado.value),
            numero_liquidacion=liquidacion.numero_liquidacion,
            user_id=getattr(liquidacion, 'user_id', None)
        )
        self.session.add(liquidacion_model)
        self.session.flush()
        
        for opcion in liquidacion.opciones:
            opcion_model = OpcionModel(
                tipo_servicio=opcion.tipo_servicio,
                metodo_pago=opcion.metodo_pago,
                tipo_opcion='local' if isinstance(opcion, OpcionLocal) else 'foreign',
                dieta_id=liquidacion_model.id
            )
            self.session.add(opcion_model)
        
        self.session.commit()
        self.session.refresh(liquidacion_model)
        return self._to_entity(liquidacion_model)
    
    def update(self, liquidacion: DietaLiquidacion) -> DietaLiquidacion:
        liquidacion_model = self.session.query(DietaLiquidacionModel)\
            .filter_by(id=liquidacion.id).first()
        if not liquidacion_model:
            raise Exception("Liquidación no encontrada")
        
        liquidacion_model.en_territorio = liquidacion.en_territorio                                     # type: ignore
        liquidacion_model.creada_at = liquidacion.creada_at                                             # type: ignore
        liquidacion_model.descripcion = liquidacion.descripcion                                         # type: ignore
        liquidacion_model.es_grupal = liquidacion.es_grupal                                             # type: ignore
        liquidacion_model.cantidad_personas = liquidacion.cantidad_personas                             # type: ignore
        liquidacion_model.estado_liquidacion = EstadoLiquidacion(liquidacion.estado.value)              # type: ignore
        liquidacion_model.numero_liquidacion = liquidacion.numero_liquidacion                           # type: ignore                            
        
        self.session.query(OpcionModel).filter_by(dieta_id=liquidacion.id).delete()
        for opcion in liquidacion.opciones:
            opcion_model = OpcionModel(
                tipo_servicio=opcion.tipo_servicio,
                metodo_pago=opcion.metodo_pago,
                tipo_opcion='local' if isinstance(opcion, OpcionLocal) else 'foreign',
                dieta_id=liquidacion.id
            )
            self.session.add(opcion_model)
        
        self.session.commit()
        self.session.refresh(liquidacion_model)
        return self._to_entity(liquidacion_model)
    
    def delete(self, liquidacion_id: int) -> bool:
        liquidacion_model = self.session.query(DietaLiquidacionModel).filter_by(id=liquidacion_id).first()
        if not liquidacion_model:
            return False
        
        self.session.delete(liquidacion_model)
        self.session.commit()
        return True
    
    def get_by_estado(self, estado: EstadoLiquidacion) -> List[DietaLiquidacion]:
        dieta_models = self.session.query(DietaLiquidacionModel)\
            .options(joinedload(DietaLiquidacionModel.opciones))\
            .filter_by(estado_liquidacion=estado).all()
        return [self._to_entity(model) for model in dieta_models]
    
    def get_pendientes(self) -> List[DietaLiquidacion]:
        return self.get_by_estado(EstadoLiquidacion.PENDIENTE)
    
    def get_liquidadas(self) -> List[DietaLiquidacion]:
        return self.get_by_estado(EstadoLiquidacion.LIQUIDADA)
    
    def liquidar_liquidacion(self, liquidacion_id: int, numero_liquidacion: str) -> bool:
        liquidacion_model = self.session.query(DietaLiquidacionModel).filter_by(id=liquidacion_id).first()
        if not liquidacion_model:
            return False
        
        liquidacion_model.estado_liquidacion = EstadoLiquidacion.LIQUIDADA              # type: ignore
        liquidacion_model.numero_liquidacion = numero_liquidacion                       # type: ignore
        self.session.commit()
        return True
    
    def get_liquidaciones_para_liquidar(self) -> List[DietaLiquidacion]:
        return self.get_pendientes()
    
    def get_by_anticipo_id(self, anticipo_id: int) -> Optional[DietaLiquidacion]:
        # Asumiendo que hay un campo anticipo_id en DietaLiquidacionModel, si no, habría que ajustar
        liquidacion_model = self.session.query(DietaLiquidacionModel)\
            .options(joinedload(DietaLiquidacionModel.opciones))\
            .filter_by(anticipo_id=anticipo_id).first()
        return self._to_entity(liquidacion_model) if liquidacion_model else None
    
    def _to_entity(self, model: DietaLiquidacionModel) -> DietaLiquidacion:
        opciones = []
        for opcion_model in model.opciones:
            if opcion_model.tipo_opcion.value == 'local':
                opcion = OpcionLocal(
                    tipo_servicio=opcion_model.tipo_servicio,
                    metodo_pago=opcion_model.metodo_pago
                )
            else:
                opcion = OpcionForeign(
                    tipo_servicio=opcion_model.tipo_servicio,
                    metodo_pago=opcion_model.metodo_pago
                )
            opciones.append(opcion)
        
        return DietaLiquidacion(
            id=model.id,                                            # type: ignore
            en_territorio=model.en_territorio,                      # type: ignore
            creada_at=model.creada_at,                              # type: ignore
            descripcion=model.descripcion,                          # type: ignore
            es_grupal=model.es_grupal,                              # type: ignore
            cantidad_personas=model.cantidad_personas,              # type: ignore
            opciones=opciones,
            estado=EstadoLiquidacion(model.estado_liquidacion.value),
            numero_liquidacion=model.numero_liquidacion             # type: ignore
        )