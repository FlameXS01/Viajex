# infrastructure/database/session.py
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from contextlib import contextmanager
from typing import Generator

# Configuración de la base de datos SQLite
SQLALCHEMY_DATABASE_URL = "sqlite:///./dietas_app.db"

# Crear motor de base de datos
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, 
    connect_args={"check_same_thread": False}
)

# Crear sesión local
SessionLocal = sessionmaker(
    autocommit=False, 
    autoflush=False, 
    bind=engine,
    class_=Session
)

# Base para los modelos
Base = declarative_base()

# Gestor de contexto para sesiones
@contextmanager
def get_db() -> Generator[Session, None, None]:
    """
    Context manager para obtener sesiones de base de datos.
    Maneja automáticamente commit, rollback y cierre.
    
    Uso:
        with get_db() as db:
            # operaciones con db
            db.query(...)
            # commit automático al salir (si no hay error)
    """
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()

def get_db_session() -> Session:
    """
    Obtiene una nueva sesión para casos especiales donde
    necesitas control manual (usar con cuidado).
    """
    return SessionLocal()

def reset_all_sessions():
    """
    Limpia todas las sesiones existentes.
    Útil después de errores críticos.
    """
    # SQLAlchemy maneja esto internamente
    # Esta función es principalmente para documentación
    pass