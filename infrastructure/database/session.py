from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from infrastructure.database.models import Base
import os
from typing import Optional

class DatabaseSession:
    def __init__(self, db_url: Optional[str] = None):
        if db_url is None:
            db_url = os.getenv("DATABASE_URL", "sqlite:///./dietas_app.db")
        
        self.engine = create_engine(
            db_url,
            connect_args={"check_same_thread": False} if "sqlite" in db_url else {},
            poolclass=StaticPool if "sqlite" in db_url else None,
            echo=False  
        )
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        
        # Crear tablas
        self._create_tables()
    
    def _create_tables(self):
        """Crea todas las tablas si no existen"""
        Base.metadata.create_all(bind=self.engine)
    
    def get_session(self) -> Session:
        """Retorna una nueva sesión de base de datos"""
        return self.SessionLocal()
    
    def close_session(self, session: Session):
        """Cierra una sesión"""
        session.close()

# Instancia global (podría moverse a inyección de dependencias)
db_session = DatabaseSession()

# Función helper para obtener sesión
def get_db():
    session = db_session.get_session()
    try:
        yield session
    finally:
        db_session.close_session(session)