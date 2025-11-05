from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.sql import func
from infrastructure.database.session import Base 

class UserModel(Base):
    """
    Modelo de SQLAlchemy para la tabla users.
    Representa la estructura de la tabla en la base de datos.
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

class CardModel(Base):
    __tablename__ = "cards"
    
    card_id = Column(Integer, primary_key=True, index=True)
    card_number = Column(String(16), unique=True, index=True, nullable=False) 
    card_pin = Column(String(255), nullable=False)  
    is_active = Column(Boolean, default=True)
    with_money = Column(bool, default=True)
    balance = Column(float())
    def __repr__(self): 
        return f"<CardModel(card_id={self.card_id}, card_number='{self.card_number}')>"