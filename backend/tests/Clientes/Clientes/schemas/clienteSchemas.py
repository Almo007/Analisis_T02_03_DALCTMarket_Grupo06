from pydantic import BaseModel, Field, EmailStr
from typing import Optional


class ClienteBaseSchema(BaseModel):
    nombreCliente: str = Field(..., min_length=3, max_length=50, example="Jorge Pérez")
    cedulaCliente: str = Field(..., min_length=10, max_length=10, example="1723456789")
    telefonoCliente: str = Field(..., min_length=10, max_length=10, example="0987654321")
    direccionCliente: str = Field(..., max_length=100, example="Av. Amazonas N12-34, Quito, Ecuador")
    emailCliente: EmailStr = Field(..., example="jorge.perez@example.com")


class ClienteCrearSchema(ClienteBaseSchema):
    pass


class ClienteActualizarSchema(BaseModel):
    nombreCliente: Optional[str] = Field(None, min_length=3, max_length=50, example="Jorge Pérez")
    telefonoCliente: Optional[str] = Field(None, min_length=10, max_length=10, example="0987654321")
    direccionCliente: Optional[str] = Field(None, max_length=100, example="Av. Amazonas N12-34, Quito, Ecuador")
    emailCliente: Optional[EmailStr] = Field(None, example="jorge.perez@example.com")
    activoCliente: Optional[bool] = None


class ClienteRespuestaSchema(BaseModel):
    idCliente: int
    nombreCliente: str
    cedulaCliente: str
    telefonoCliente: str
    direccionCliente: str
    emailCliente: EmailStr
    activoCliente: bool

    class Config:
        from_attributes = True
