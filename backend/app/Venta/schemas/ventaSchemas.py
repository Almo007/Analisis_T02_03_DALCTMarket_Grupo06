from datetime import datetime
from app.Venta.schemas.detalleVentaSchemas import DetalleVentaRespuestaSchema
from app.Venta.schemas.detalleVentaSchemas import DetalleVentaCrearSchema
from app.Usuarios.schemas.usuarioSchemas import UsuarioPublicoSchema
from app.Clientes.schemas.clienteSchemas import ClienteRespuestaSchema
from pydantic import BaseModel, Field, field_validator
from typing import List, Literal
from app.Venta.schemas.detalleVentaSchemas import DetalleVentaCrearSchema

class VentaCrearSchema(BaseModel):
    idCliente: int
    metodoPago: Literal["Efectivo", "Tarjeta", "Transferencia"]
    descuentoGeneral: float = Field(0.0, ge=0.0, le=100.0)
    detalles: List[DetalleVentaCrearSchema]

    @field_validator("detalles")
    @classmethod
    def detalles_no_vacios(cls, v):
        
        if not v:
            raise ValueError("La lista de productos no puede estar vacía")
        return v

    model_config = {
        "json_schema_extra": {
            "example": {
                "idCliente": 1,
                "metodoPago": "Efectivo",
                "descuentoGeneral": 0.0,
                "detalles": [
                    {"idProducto": 1, "cantidadComprada": 10},
                    {"idProducto": 2, "cantidadComprada": 5}
                ]
            }
        }
    }

class VentaRespuestaSchema(BaseModel):
    idVenta: int
    idCaja: int
    usuario: UsuarioPublicoSchema
    cliente: ClienteRespuestaSchema
    fechaVenta: datetime
    subtotalVenta: float
    descuentoGeneral: float
    totalDescuento: float
    baseIVA: float
    totalIVA: float
    totalPagar: float
    metodoPago: str
    estadoVenta: str
    detalles: List[DetalleVentaRespuestaSchema] = []

    class Config:
        from_attributes = True
