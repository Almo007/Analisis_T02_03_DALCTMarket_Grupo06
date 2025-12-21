from sqlalchemy import Column, Integer, Float, DateTime, String, ForeignKey, func
from sqlalchemy.orm import relationship
from app.database import Base

class Venta(Base):
    __tablename__ = "venta"
    idVenta = Column(Integer, primary_key=True, autoincrement=True)
    idCaja = Column(Integer, ForeignKey("cajahistorial.idCaja"), nullable=False)
    idUsuarioVenta = Column(Integer, ForeignKey("usuario.idUsuario"), nullable=False)
    idCliente = Column(Integer, ForeignKey("cliente.idCliente"), nullable=False)
    fechaVenta = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    subtotalVenta = Column(Float, nullable=False)
    descuentoGeneral = Column(Float, nullable=False)
    totalDescuento = Column(Float, nullable=False)
    baseIVA = Column(Float, nullable=False)
    totalIVA = Column(Float, nullable=False)
    totalPagar = Column(Float, nullable=False)
    metodoPago = Column(String(50), nullable=False)
    estadoVenta = Column(String(30), nullable=False)

    usuario = relationship("Usuario", back_populates="ventas")
    cliente = relationship("Cliente", back_populates="ventas")
    detalles = relationship("DetalleVenta", back_populates="venta")
