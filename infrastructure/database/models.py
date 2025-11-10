from sqlalchemy import Column, Integer, String, Boolean, DateTime, Numeric, ForeignKey, Float, Date, Enum, Text
from sqlalchemy.sql import func
from infrastructure.database.session import Base 
from sqlalchemy.orm import relationship
import enum

class DietStatus(enum.Enum):
    """
    Enum que define los posibles estados de una dieta.
    
    Valores:
        REQUESTED: Dieta solicitada/anticipada
        LIQUIDATED: Dieta completamente liquidada
        PARTIALLY_LIQUIDATED: Dieta parcialmente liquidada
    """
    REQUESTED = "requested"
    LIQUIDATED = "liquidated"
    PARTIALLY_LIQUIDATED = "partially_liquidated"

class PaymentMethod(enum.Enum):
    """
    Enum que define los métodos de pago para el alojamiento.
    
    Valores:
        CASH: Pago en efectivo
        CARD: Pago con tarjeta
    """
    CASH = "cash"
    CARD = "card"

class DietServiceModel(Base):
    """
    Modelo de SQLAlchemy para la tabla diet_services.
    
    Representa los precios de los servicios de dieta según la localidad
    (local o no local). Solo existen 2 registros en esta tabla.
    
    Campos:
        id: Identificador único
        is_local: Boolean que indica si es local (True) o no local (False)
        breakfast_price: Precio del desayuno
        lunch_price: Precio del almuerzo
        dinner_price: Precio de la comida
        accommodation_cash_price: Precio de alojamiento en efectivo
        accommodation_card_price: Precio de alojamiento con tarjeta
    """
    __tablename__ = "diet_services"
    
    id = Column(Integer, primary_key=True, index=True)
    is_local = Column(Boolean, nullable=False)
    breakfast_price = Column(Float, nullable=False)
    lunch_price = Column(Float, nullable=False)
    dinner_price = Column(Float, nullable=False)
    accommodation_cash_price = Column(Float, nullable=False)
    accommodation_card_price = Column(Float, nullable=False)
    
    # Relaciones
    diets = relationship("DietModel", back_populates="diet_service")
    diet_liquidations = relationship("DietLiquidationModel", back_populates="diet_service")

class DietModel(Base):
    """
    Modelo de SQLAlchemy para la tabla diets.
    
    Representa un anticipo de dieta (solicitud inicial) con todos los
    servicios y cantidades planeadas. Esta entidad mantiene el registro
    original de lo que se solicitó.
    
    Campos:
        id: Identificador único
        is_local: Boolean que indica si la dieta es local
        start_date: Fecha de inicio de la dieta
        end_date: Fecha de fin de la dieta
        description: Descripción de la dieta
        advance_number: Número secuencial del anticipo
        is_group: Boolean que indica si es dieta grupal
        status: Estado actual de la dieta (DietStatus)
        breakfast_count: Cantidad de desayunos solicitados
        lunch_count: Cantidad de almuerzos solicitados
        dinner_count: Cantidad de comidas solicitadas
        accommodation_count: Cantidad de alojamientos solicitados
        accommodation_payment_method: Método de pago para alojamiento
        request_user_id: FK al solicitante principal
        diet_service_id: FK a los precios aplicables
        accommodation_card_id: FK a la tarjeta (si el pago es con tarjeta)
        created_at: Fecha de creación del registro
    """
    __tablename__ = "diets"
    
    id = Column(Integer, primary_key=True, index=True)
    is_local = Column(Boolean, nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    description = Column(Text)
    advance_number = Column(Integer, nullable=False)
    is_group = Column(Boolean, default=False)
    status = Column(Enum(DietStatus), default=DietStatus.REQUESTED)
    
    # Cantidades solicitadas
    breakfast_count = Column(Integer, default=0)
    lunch_count = Column(Integer, default=0)
    dinner_count = Column(Integer, default=0)
    accommodation_count = Column(Integer, default=0)
    accommodation_payment_method = Column(Enum(PaymentMethod))
    
    # Foreign Keys
    request_user_id = Column(Integer, ForeignKey("requests.id"), nullable=False)
    diet_service_id = Column(Integer, ForeignKey("diet_services.id"), nullable=False)
    accommodation_card_id = Column(Integer, ForeignKey("cards.card_id"), nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relaciones
    request_user = relationship("RequestUserModel", back_populates="diets")
    diet_service = relationship("DietServiceModel", back_populates="diets")
    accommodation_card = relationship("CardModel")
    diet_members = relationship("DietMemberModel", back_populates="diet", cascade="all, delete-orphan")
    liquidations = relationship("DietLiquidationModel", back_populates="diet")

    

class DietLiquidationModel(Base):
    """
    Modelo de SQLAlchemy para la tabla diet_liquidations.
    
    Representa la liquidación de una dieta, conteniendo las cantidades
    reales que fueron liquidadas. Mantiene una relación con el anticipo
    original (DietModel) para permitir comparaciones.
    
    Campos:
        id: Identificador único
        liquidation_number: Número secuencial de liquidación
        liquidation_date: Fecha en que se realizó la liquidación
        breakfast_count_liquidated: Cantidad real de desayunos liquidados
        lunch_count_liquidated: Cantidad real de almuerzos liquidados
        dinner_count_liquidated: Cantidad real de comidas liquidadas
        accommodation_count_liquidated: Cantidad real de alojamientos liquidados
        accommodation_payment_method: Método de pago real usado
        diet_id: FK al anticipo original (DietModel)
        diet_service_id: FK a los precios aplicados en la liquidación
        accommodation_card_id: FK a la tarjeta usada (si aplica)
    """
    __tablename__ = "diet_liquidations"
    
    id = Column(Integer, primary_key=True, index=True)
    liquidation_number = Column(Integer, nullable=False)
    liquidation_date = Column(DateTime(timezone=True), server_default=func.now())
    
    # Cantidades liquidadas
    breakfast_count_liquidated = Column(Integer, default=0)
    lunch_count_liquidated = Column(Integer, default=0)
    dinner_count_liquidated = Column(Integer, default=0)
    accommodation_count_liquidated = Column(Integer, default=0)
    accommodation_payment_method = Column(Enum(PaymentMethod))
    
    # Foreign Keys
    diet_id = Column(Integer, ForeignKey("diets.id"), nullable=False)
    diet_service_id = Column(Integer, ForeignKey("diet_services.id"), nullable=False)
    accommodation_card_id = Column(Integer, ForeignKey("cards.card_id"), nullable=True)
    
    # Relaciones
    diet = relationship("DietModel", back_populates="liquidations")
    diet_service = relationship("DietServiceModel", back_populates="diet_liquidations")
    accommodation_card = relationship("CardModel")

class DietMemberModel(Base):
    """
    Modelo de SQLAlchemy para la tabla diet_members.
    
    Representa los miembros adicionales en dietas grupales. Solo se utiliza
    cuando is_group = True en la dieta principal.
    
    Campos:
        id: Identificador único
        diet_id: FK a la dieta grupal
        request_user_id: FK al solicitante que es miembro del grupo
    """
    __tablename__ = "diet_members"
    
    id = Column(Integer, primary_key=True, index=True)
    diet_id = Column(Integer, ForeignKey("diets.id"), nullable=False)
    request_user_id = Column(Integer, ForeignKey("requests.id"), nullable=False)
    
    # Relaciones
    diet = relationship("DietModel", back_populates="diet_members")
    request_user = relationship("RequestUserModel", back_populates="diet_memberships")

class RequestUserModel(Base):
    """
    Modelo de SQLAlchemy para la tabla requests.
    
    Representa la estructura de la tabla Solicitantes en la base de datos.
    
    Campos:
        id: Identificador único
        username: Nombre de usuario único
        fullname: Nombre completo único
        email: Email único
        ci: Carnet de identidad único
        department_id: FK al departamento
    """
    __tablename__ = "requests"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=True)
    fullname = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=True)
    ci = Column(String(15), unique=True, nullable=False)
    department_id = Column(Integer, ForeignKey("department.id"), nullable=False)

    # Relaciones existentes
    department = relationship("DepartmentModel", back_populates="requests")
    
    # NUEVAS relaciones para dietas
    diets = relationship("DietModel", back_populates="request_user")
    diet_memberships = relationship("DietMemberModel", back_populates="request_user")

class DepartmentModel(Base):
    """
    Modelo de SQLAlchemy para la tabla department.
    
    Representa la estructura de la tabla Departamentos en la base de datos.
    
    Campos:
        id: Identificador único
        name: Nombre del departamento (único)
    """
    __tablename__ = "department"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, index=True, nullable=False)
    
    requests = relationship("RequestUserModel", back_populates="department")

class CardModel(Base):
    """
    Modelo de SQLAlchemy para la tabla cards.
    
    Representa las tarjetas disponibles para pagos de alojamiento.
    
    Campos:
        card_id: Identificador único
        card_number: Número de tarjeta (único)
        card_pin: PIN de la tarjeta (hasheado)
        is_active: Boolean que indica si la tarjeta está activa
        with_money: Boolean que indica si la tarjeta tiene fondos
        balance: Monto disponible en la tarjeta
    """
    __tablename__ = "cards"
    
    card_id = Column(Integer, primary_key=True, index=True)
    card_number = Column(String(16), unique=True, index=True, nullable=False) 
    card_pin = Column(String(255), nullable=False)  
    is_active = Column(Boolean, default=True)
    with_money = Column(Boolean, default=True)
    balance = Column(Float)
    
    def __repr__(self):  
        return f"<CardModel(card_id={self.card_id}, card_number='{self.card_number}')>"

    
class UserModel(Base):
    """
    Modelo de SQLAlchemy para la tabla users del sistema.
    
    Representa la estructura de la tabla en la base de datos.
    
    Campos:
        id: Identificador único
        username: Nombre de usuario único
        email: Email único
        role: Rol del usuario (admin, manager, user)
        hash_password: Contraseña hasheada
        created_at: Fecha de creación
        is_active: Boolean que indica si el usuario está activo
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    role = Column(String(20), nullable=False)
    hash_password = Column(String(255))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    is_active = Column(Boolean, default=True)

    def __repr__(self):
        return f"<UserModel(id={self.id}, username='{self.username}')>"


    
       
