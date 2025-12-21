from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class Usuario(Base):
    __tablename__ = "usuario"
    idUsuario = Column(Integer, primary_key=True, autoincrement=True)
    idRol = Column(Integer, ForeignKey("rol.idRol"), nullable=False)
    nombreCompleto = Column(String(50), nullable=False)
    cedulaUsuario = Column(String(20), nullable=False, unique=True)
    emailUsuario = Column(String(100), nullable=False)
    passwordUsuario = Column(String(255), nullable=False)
    activoUsuario = Column(Boolean, default=True)

    rol = relationship("Rol")
    ventas = relationship("Venta", back_populates="usuario")
    cajas = relationship("CajaHistorial", back_populates="usuario")
    pedidosCreados = relationship(
        "Pedido",
        foreign_keys="Pedido.idUsuarioCreador",
        back_populates="usuarioCreador"
    )

    pedidosAprobados = relationship(
        "Pedido",
        foreign_keys="Pedido.idUsuarioAprobador",
        back_populates="usuarioAprobador"
    )