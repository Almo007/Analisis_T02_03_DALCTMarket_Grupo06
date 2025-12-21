from sqlalchemy import Column, Integer, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class Inventario(Base):
    __tablename__ = "inventario"
    idInventario = Column(Integer, primary_key=True, autoincrement=True)
    idProducto = Column(Integer, ForeignKey("producto.idProducto"), unique=True)
    cantidadDisponible = Column(Integer, nullable=False)
    cantidadMinima = Column(Integer, nullable=False, default=0)
    activoInventario = Column(Boolean, default=True)

    producto = relationship("Producto", back_populates="inventario")
