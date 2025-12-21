from sqlalchemy import Column, Integer, Float, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class DetalleVenta(Base):
    __tablename__ = "detalleventa"
    idDetalleVenta = Column(Integer, primary_key=True, autoincrement=True)
    idVenta = Column(Integer, ForeignKey("venta.idVenta"), nullable=False)
    idProducto = Column(Integer, ForeignKey("producto.idProducto"), nullable=False)
    idPromocion = Column(Integer, ForeignKey("promocion.idPromocion"), nullable=True)
    precioUnitarioVendido = Column(Float, nullable=False)
    cantidadVendida = Column(Integer, nullable=False)
    subtotalProducto = Column(Float, nullable=False)
    valorDescuentoProducto = Column(Float, nullable=False)

    venta = relationship("Venta", back_populates="detalles")
    producto = relationship("Producto", back_populates="detallesVenta")
    promocion = relationship("Promocion", back_populates="detallesVenta")
