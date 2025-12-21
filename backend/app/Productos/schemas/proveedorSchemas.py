from pydantic import BaseModel, Field, EmailStr
from typing import Optional

class ProveedorBaseSchema(BaseModel):
    razonSocial: str = Field(..., min_length=3, max_length=100, example="Distribuidora Andina de Bebidas S.A.")
    ruc: str = Field(..., min_length=13, max_length=13, example="1790012345001")
    direccionProveedor: str = Field(..., max_length=100, example="Av. Maldonado y Morán Valverde, Quito")
    telefonoProveedor: str = Field(..., min_length=10, max_length=10, example="0991234567")
    emailProveedor: EmailStr = Field(..., example="ventas@andinabebidas.com")

class ProveedorCrearSchema(ProveedorBaseSchema):
    pass

class ProveedorActualizarSchema(BaseModel):
    razonSocial: Optional[str] = Field(None, min_length=3, max_length=100, example="Distribuidora Andina de Bebidas S.A.")
    direccionProveedor: Optional[str] = Field(None, max_length=100, example="Av. Maldonado y Morán Valverde, Quito")
    telefonoProveedor: Optional[str] = Field(None, min_length=10, max_length=10, example="0991234567")
    emailProveedor: Optional[EmailStr] = Field(None, example="ventas@andinabebidas.com")
    activoProveedor: Optional[bool] = None

class ProveedorRespuestaSchema(BaseModel):
    idProveedor: int
    razonSocial: str
    ruc: str
    direccionProveedor: str
    telefonoProveedor: str
    emailProveedor: EmailStr
    activoProveedor: bool

    class Config:
        from_attributes = True
