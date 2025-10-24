from sqlalchemy.orm import Session
from sqlalchemy import  func
from typing import List, Optional
from core.entities.opciones import OpcionBase, OpcionLocal, OpcionForeign
from core.repositories.opcion_repository import OpcionRepository
from core.entities.enums import TipoServicio, MetodoPagoHospedaje
from infrastructure.database.models import OpcionModel

class SQLAlchemyOpcionRepository(OpcionRepository):
    
    def __init__(self, session: Session):
        self.session = session
    
    def get_by_id(self, opcion_id: int) -> Optional[OpcionBase]:
        opcion_model = self.session.query(OpcionModel).filter_by(id=opcion_id).first()
        return self._to_entity(opcion_model) if opcion_model else None
    
    def get_by_dieta_id(self, dieta_id: int) -> List[OpcionBase]:
        opcion_models = self.session.query(OpcionModel).filter_by(dieta_id=dieta_id).all()
        return [self._to_entity(model) for model in opcion_models]
    
    def get_by_tipo_servicio(self, tipo_servicio: TipoServicio) -> List[OpcionBase]:
        opcion_models = self.session.query(OpcionModel).filter_by(tipo_servicio=tipo_servicio).all()
        return [self._to_entity(model) for model in opcion_models]
    
    def create(self, opcion: OpcionBase, dieta_id: int) -> OpcionBase:
        opcion_model = OpcionModel(
            tipo_servicio=opcion.tipo_servicio,
            metodo_pago=opcion.metodo_pago,
            tipo_opcion='local' if isinstance(opcion, OpcionLocal) else 'foreign',
            dieta_id=dieta_id
        )
        self.session.add(opcion_model)
        self.session.commit()
        self.session.refresh(opcion_model)
        return self._to_entity(opcion_model)
    
    def update(self, opcion: OpcionBase) -> OpcionBase:
        if not hasattr(opcion, 'id') or not opcion.id:
            raise ValueError("La opción debe tener un ID para ser actualizada")
        
        opcion_model = self.session.query(OpcionModel).filter_by(id=opcion.id).first()
        if not opcion_model:
            raise Exception("Opción no encontrada")
        
        opcion_model.tipo_servicio = opcion.tipo_servicio                   # type: ignore
        opcion_model.metodo_pago = opcion.metodo_pago                       # type: ignore
        opcion_model.tipo_opcion = 'local' if isinstance(opcion, OpcionLocal) else 'foreign'        # type: ignore
        
        self.session.commit()
        self.session.refresh(opcion_model)
        return self._to_entity(opcion_model)
    
    def delete(self, opcion_id: int) -> bool:
        opcion_model = self.session.query(OpcionModel).filter_by(id=opcion_id).first()
        if not opcion_model:
            return False
        
        self.session.delete(opcion_model)
        self.session.commit()
        return True
    
    def delete_by_dieta_id(self, dieta_id: int) -> bool:
        result = self.session.query(OpcionModel).filter_by(dieta_id=dieta_id).delete()
        self.session.commit()
        return result > 0
    
    def get_precios_por_servicio(self, tipo_servicio: TipoServicio) -> dict:
        # Este método podría necesitar una lógica más compleja dependiendo de lo que se necesite
        # Por ahora, contamos las opciones por tipo_opcion para un servicio dado
        counts = self.session.query(
            OpcionModel.tipo_opcion, 
            func.count(OpcionModel.id)
        ).filter_by(
            tipo_servicio=tipo_servicio
        ).group_by(
            OpcionModel.tipo_opcion
        ).all()
        
        return {tipo_opcion: count for tipo_opcion, count in counts}
    
    def _to_entity(self, model: OpcionModel) -> OpcionBase:
        if model.tipo_opcion.value == 'local':
            return OpcionLocal(
                tipo_servicio=model.tipo_servicio,  # type: ignore
                metodo_pago=model.metodo_pago       # type: ignore
            )
        else:
            return OpcionForeign(
                tipo_servicio=model.tipo_servicio,      # type: ignore
                metodo_pago=model.metodo_pago           # type: ignore
            )