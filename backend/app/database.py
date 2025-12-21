import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


BASEDATOS_URL = os.getenv(
    "DATABASE_URL","postgresql://dalctuser:Dalct1234@servicio-bdpostgres:5432/dalctmarket"
)

engine = create_engine(BASEDATOS_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Obtener la sesión actual de la base de datos
def obtenerSesion():
    databaseSesion = SessionLocal()
    try:
        yield databaseSesion
    finally:
        databaseSesion.close()

def obtenerSesionDirecta():
    db = SessionLocal()
    return db


