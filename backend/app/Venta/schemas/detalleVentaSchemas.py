from pydantic import BaseModel, Field
from typing import Optional
from app.Venta.schemas.promocionSchemas import PromocionResumenSchema
from app.Productos.schemas.productoSchemas import ProductoResumenSchema

class DetalleVentaCrearSchema(BaseModel):
    idProducto: int
    cantidadComprada: int = Field(..., example=10, ge=1)

class DetalleVentaRespuestaSchema(BaseModel):
    idDetalleVenta: int
    idVenta: int
    producto: ProductoResumenSchema
    promocion: Optional[PromocionResumenSchema] = None
    precioUnitarioVendido: float
    cantidadVendida: int
    subtotalProducto: float
    valorDescuentoProducto: float

    class Config:
        from_attributes = True