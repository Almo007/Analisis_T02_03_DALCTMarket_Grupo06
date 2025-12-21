from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from app.database import Base

class Rol(Base):
    __tablename__ = "rol"
    idRol = Column(Integer, primary_key=True, autoincrement=True)
    nombreRol = Column(String(20), nullable=False)
