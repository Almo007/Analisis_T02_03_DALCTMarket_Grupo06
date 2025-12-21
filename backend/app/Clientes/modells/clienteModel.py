from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import relationship
from app.database import Base

class Cliente(Base):
    __tablename__ = "cliente"
    idCliente = Column(Integer, primary_key=True, autoincrement=True)
    nombreCliente = Column(String(50), nullable=False)
    cedulaCliente = Column(String(20), nullable=False, unique=True)
    telefonoCliente = Column(String(20), nullable=False)
    direccionCliente = Column(String(100), nullable=False)
    emailCliente = Column(String(100), nullable=False)
    activoCliente = Column(Boolean, default=True)

    ventas = relationship("Venta", back_populates="cliente")
