from sqlalchemy import Column, Integer, Float, DateTime, String, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class CajaHistorial(Base):
    __tablename__ = "cajahistorial"
    idCaja = Column(Integer, primary_key=True, autoincrement=True)
    idUsuarioCaja = Column(Integer, ForeignKey("usuario.idUsuario"), nullable=False)
    fechaAperturaCaja = Column(DateTime, nullable=False)
    fechaCierreCaja = Column(DateTime, nullable=True)
    montoInicialDeclarado = Column(Float, nullable=False)
    montoCierreDeclarado = Column(Float, nullable=True)
    montoCierreSistema = Column(Float, nullable=True)
    diferenciaCaja = Column(Float, nullable=True)
    estadoCaja = Column(String(20), nullable=False, default="ABIERTA")
    detalle = Column(String(500), nullable=True)

    usuario = relationship("Usuario", back_populates="cajas")