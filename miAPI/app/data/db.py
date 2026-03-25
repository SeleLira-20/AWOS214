from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os

#1.definimos la URL de la BD
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://admin:123456@postgres:5432/DB_miapi"
)

#2.Creamos el motor de conexión
engine= create_engine(DATABASE_URL)

#3.Creamos gestionador de sesiones
SessionLocal= sessionmaker(
    autocommit= False,
    autoflush= False,
    bind= engine
)

#4. Base declarativa para modelos
Base= declarative_base()

#5. Funcion de para la sesion en cada peticion
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()