from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Enum, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
Base = declarative_base()

# Enums para SQLAlchemy
class UserRoleEnum(enum.Enum):
    ADMIN = "admin"
    MANAGER = "manager"
    USER = "user"

class EstadoAnticipoEnum(enum.Enum):
    PENDIENTE = "pendiente"
    LIQUIDADA = "liquidada"

class EstadoLiquidacionEnum(enum.Enum):
    PENDIENTE = "pendiente"
    LIQUIDADA = "liquidada"

class TipoServicioEnum(enum.Enum):
    DESAYUNO = "desayuno"
    ALMUERZO = "almuerzo"
    COMIDA = "comida"
    HOSPEDAJE = "hospedaje"

class MetodoPagoHospedajeEnum(enum.Enum):
    EFECTIVO = "efectivo"
    TARJETA = "tarjeta"

class TipoOpcionEnum(enum.Enum):
    LOCAL = "local"
    FOREIGN = "foreign"

class UserModel(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    role = Column((String), default=UserRoleEnum.USER, nullable=False)
    hash_password = Column(String(255))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    is_active = Column(Boolean, default=True)
    
    # Relaciones
    dietas = relationship("DietaBaseModel", back_populates="user")
    
    def __repr__(self):
        return f"<UserModel(id={self.id}, username='{self.username}', email='{self.email}')>"

class DietaBaseModel(Base):
    __tablename__ = "dietas_base"
    
    id = Column(Integer, primary_key=True, index=True)
    tipo = Column(String(20), nullable=False)  # 'anticipo' o 'liquidacion'
    
    # Campos comunes de DietaBase
    en_territorio = Column(Boolean, nullable=False)
    creada_at = Column(String(10), nullable=False)  # Formato "dd-mm-yy"
    descripcion = Column(Text, nullable=False)
    es_grupal = Column(Boolean, nullable=False)
    cantidad_personas = Column(Integer)
    
    # Campos específicos para DietaAnticipo
    estado_anticipo = Column(String())
    numero_anticipo = Column(String(50))
    
    # Campos específicos para DietaLiquidacion
    estado_liquidacion = Column(String())
    numero_liquidacion = Column(String(50))
    
    # Relaciones
    user_id = Column(Integer, ForeignKey("users.id"))
    user = relationship("UserModel", back_populates="dietas")
    opciones = relationship("OpcionModel", back_populates="dieta", cascade="all, delete-orphan")
    
    # Para mapeo polimórfico
    __mapper_args__ = {
        'polymorphic_identity': 'dieta_base',
        'polymorphic_on': tipo
    }
    
    def __repr__(self):
        return f"<DietaBaseModel(id={self.id}, tipo='{self.tipo}', descripcion='{self.descripcion}')>"

class DietaAnticipoModel(DietaBaseModel):
    __tablename__ = "dietas_anticipo"
    
    id = Column(Integer, ForeignKey('dietas_base.id'), primary_key=True)
    
    __mapper_args__ = {
        'polymorphic_identity': 'anticipo',
    }
    
    def __repr__(self):
        return f"<DietaAnticipoModel(id={self.id}, estado='{self.estado_anticipo}')>"

class DietaLiquidacionModel(DietaBaseModel):
    __tablename__ = "dietas_liquidacion"
    
    id = Column(Integer, ForeignKey('dietas_base.id'), primary_key=True)
    
    __mapper_args__ = {
        'polymorphic_identity': 'liquidacion',
    }
    
    def __repr__(self):
        return f"<DietaLiquidacionModel(id={self.id}, estado='{self.estado_liquidacion}')>"

class OpcionModel(Base):
    __tablename__ = "opciones"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Campos comunes de OpcionBase
    tipo_servicio = Column(String(), nullable=False)
    metodo_pago = Column(String())
    tipo_opcion = Column(String(), nullable=False)  # 'local' o 'foreign'
    
    # Relaciones
    dieta_id = Column(Integer, ForeignKey("dietas_base.id"), nullable=False)
    dieta = relationship("DietaBaseModel", back_populates="opciones")
    
    def __repr__(self):
        return f"<OpcionModel(id={self.id}, tipo_servicio='{self.tipo_servicio}', tipo_opcion='{self.tipo_opcion}')>"