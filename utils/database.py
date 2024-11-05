from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.schema import ForeignKey

from utils.settings import DATABASE_URL, DB_POOL_CONFIG, SSL_CONFIG

# Crear el engine con configuración específica para Azure
engine = create_engine(
    DATABASE_URL,
    connect_args=SSL_CONFIG,
    **DB_POOL_CONFIG
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    created_at = Column(DateTime, default=datetime.now)
    activities = relationship("Activity", back_populates="user")


class Activity(Base):
    __tablename__ = "activities"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    date = Column(String, index=True)
    physical_activity = Column(Boolean, default=False)
    diet_nutrition = Column(Boolean, default=False)
    rest_recovery = Column(Boolean, default=False)
    personal_development = Column(Boolean, default=False)
    points = Column(Integer)

    user = relationship("User", back_populates="activities")


def get_db():
    """
    Función helper para obtener una sesión de base de datos
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """
    Inicializa la base de datos y crea las tablas
    """
    try:
        Base.metadata.create_all(bind=engine)
        print("Base de datos inicializada correctamente")
    except Exception as e:
        print(f"Error al inicializar la base de datos: {e}")
