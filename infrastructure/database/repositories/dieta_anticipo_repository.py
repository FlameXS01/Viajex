from sqlalchemy.orm import Session, joinedload
from typing import List, Optional
from core.entities.dieta import DietaAnticipo
from core.entities.opciones import OpcionLocal, OpcionForeign
from core.repositories.dieta_anticipo_repository import DietaAnticipoRepository
from core.entities.enums import EstadoAnticipo, TipoServicio, MetodoPagoHospedaje
from infrastructure.database.models import DietaAnticipoModel, OpcionModel

class SQLAlchemyDietaAnticipoRepository(DietaAnticipoRepository):
    
    def __init__(self, session: Session):
        self.session = session
    
    def get_by_id(self, anticipo_id: int) -> Optional[DietaAnticipo]:
        dieta_model = self.session.query(DietaAnticipoModel)\
            .options(joinedload(DietaAnticipoModel.opciones))\
            .filter_by(id=anticipo_id).first()
        return self._to_entity(dieta_model) if dieta_model else None
    
    def get_by_numero_anticipo(self, numero_anticipo: str) -> Optional[DietaAnticipo]:
        dieta_model = self.session.query(DietaAnticipoModel)\
            .options(joinedload(DietaAnticipoModel.opciones))\
            .filter_by(numero_anticipo=numero_anticipo).first()
        return self._to_entity(dieta_model) if dieta_model else None
    
    def get_all(self) -> List[DietaAnticipo]:
        dieta_models = self.session.query(DietaAnticipoModel)\
            .options(joinedload(DietaAnticipoModel.opciones)).all()
        return [self._to_entity(model) for model in dieta_models]
    
    def create(self, anticipo: DietaAnticipo) -> DietaAnticipo:
        # Crear el modelo de anticipo
        anticipo_model = DietaAnticipoModel(
            en_territorio=anticipo.en_territorio,
            creada_at=anticipo.creada_at,
            descripcion=anticipo.descripcion,
            es_grupal=anticipo.es_grupal,
            cantidad_personas=anticipo.cantidad_personas,
            estado_anticipo=EstadoAnticipo(anticipo.estado.value),
            numero_anticipo=anticipo.numero_anticipo,
            user_id=getattr(anticipo, 'user_id', None)
        )
        self.session.add(anticipo_model)
        self.session.flush()  # Para obtener el ID sin commit
        
        # Crear las opciones
        for opcion in anticipo.opciones:
            opcion_model = OpcionModel(
                tipo_servicio=opcion.tipo_servicio,
                metodo_pago=opcion.metodo_pago,
                tipo_opcion='local' if isinstance(opcion, OpcionLocal) else 'foreign',
                dieta_id=anticipo_model.id
            )
            self.session.add(opcion_model)
        
        self.session.commit()
        self.session.refresh(anticipo_model)
        return self._to_entity(anticipo_model)
    
    def update(self, anticipo: DietaAnticipo) -> DietaAnticipo:
        anticipo_model = self.session.query(DietaAnticipoModel)\
            .filter_by(id=anticipo.id).first()
        if not anticipo_model:
            raise Exception("Anticipo no encontrado")
        
        # Actualizar campos
        anticipo_model.en_territorio = anticipo.en_territorio                       # type: ignore
        anticipo_model.creada_at = anticipo.creada_at                               # type: ignore
        anticipo_model.descripcion = anticipo.descripcion                           # type: ignore
        anticipo_model.es_grupal = anticipo.es_grupal                               # type: ignore
        anticipo_model.cantidad_personas = anticipo.cantidad_personas               # type: ignore
        anticipo_model.estado_anticipo = EstadoAnticipo(anticipo.estado.value)      # type: ignore
        anticipo_model.numero_anticipo = anticipo.numero_anticipo                   # type: ignore
        anticipo_model.user_id = getattr(anticipo, 'user_id', None)                 # type: ignore
        
        # Eliminar opciones existentes y crear nuevas
        self.session.query(OpcionModel).filter_by(dieta_id=anticipo.id).delete()
        for opcion in anticipo.opciones:
            opcion_model = OpcionModel(
                tipo_servicio=opcion.tipo_servicio,
                metodo_pago=opcion.metodo_pago,
                tipo_opcion='local' if isinstance(opcion, OpcionLocal) else 'foreign',
                dieta_id=anticipo.id
            )
            self.session.add(opcion_model)
        
        self.session.commit()
        self.session.refresh(anticipo_model)
        return self._to_entity(anticipo_model)
    
    def delete(self, anticipo_id: int) -> bool:
        anticipo_model = self.session.query(DietaAnticipoModel).filter_by(id=anticipo_id).first()
        if not anticipo_model:
            return False
        
        self.session.delete(anticipo_model)
        self.session.commit()
        return True
    
    def get_by_estado(self, estado: EstadoAnticipo) -> List[DietaAnticipo]:
        dieta_models = self.session.query(DietaAnticipoModel)\
            .options(joinedload(DietaAnticipoModel.opciones))\
            .filter_by(estado_anticipo=estado).all()
        return [self._to_entity(model) for model in dieta_models]
    
    def get_pendientes(self) -> List[DietaAnticipo]:
        return self.get_by_estado(EstadoAnticipo.PENDIENTE)
    
    def get_liquidadas(self) -> List[DietaAnticipo]:
        return self.get_by_estado(EstadoAnticipo.LIQUIDADA)
    
    def liquidar_anticipo(self, anticipo_id: int, numero_anticipo: str) -> bool:
        anticipo_model = self.session.query(DietaAnticipoModel).filter_by(id=anticipo_id).first()
        if not anticipo_model:
            return False
        
        anticipo_model.estado_anticipo = EstadoAnticipo.LIQUIDADA    # type: ignore
        anticipo_model.numero_anticipo = numero_anticipo             # type: ignore
        self.session.commit()
        return True
    
    def get_anticipos_para_liquidar(self) -> List[DietaAnticipo]:
        return self.get_pendientes()
    
    def _to_entity(self, model: DietaAnticipoModel) -> DietaAnticipo:
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
        
        return DietaAnticipo(
            id=model.id,                                        # type: ignore
            en_territorio=model.en_territorio,                  # type: ignore
            creada_at=model.creada_at,                          # type: ignore
            descripcion=model.descripcion,                      # type: ignore
            es_grupal=model.es_grupal,                          # type: ignore
            cantidad_personas=model.cantidad_personas,          # type: ignore
            opciones=opciones,
            estado=EstadoAnticipo(model.estado_anticipo.value),
            numero_anticipo=model.numero_anticipo               # type: ignore
        )