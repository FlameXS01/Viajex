from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
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

    
class RequestUserModel(Base):
    """
    Modelo de SQLAlchemy para la tabla request.
    Representa la estructura de la tabla Solicitantes en la base de datos
    """
    __tablename__ = "requests"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    fullname = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    ci = Column(String(15), unique=True, nullable=False)
    department_id = Column(Integer, ForeignKey("department.id"), nullable=False)

    department = relationship("DepartmentModel", back_populates="requests")
    
class DepartmentModel(Base):
    """
    Modelo de SQLAlchemy para la tabla department.
    Representa la estructura de la tabla Departamentos en la base de datos
    """
    __tablename__ = "department"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, index=True, nullable=False)
    
    requests = relationship("RequestUserModel", back_populates="department")
    
