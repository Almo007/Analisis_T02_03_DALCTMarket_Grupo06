from pydantic import BaseModel, Field
from typing import Optional, List
from app.Productos.schemas.categoriaProductoSchemas import CategoriaProductoRespuestaSchema
from app.Productos.schemas.proveedorSchemas import ProveedorRespuestaSchema

class ProductoBaseSchema(BaseModel):
    idCategoriaProducto: int = Field(..., example=1)
    idProveedor: int = Field(..., example=1)
    nombreProducto: str = Field(..., min_length=1, max_length=100, example="Cola 2 Litros")
    descripcionProducto: Optional[str] = Field(None, max_length=255, example="Bebida gaseosa sabor cola")
    precioUnitarioVenta: float = Field(..., gt=0, example=2.50)
    precioUnitarioCompra: float = Field(..., gt=0, example=1.80)
    tieneIva: bool = Field(..., example=True)

class ProductoCrearSchema(ProductoBaseSchema):
    cantidadDisponible: Optional[int] = Field(None, example=0, ge=0)
    cantidadMinima: Optional[int] = Field(None, example=0, ge=0)

class ProductoActualizarSchema(BaseModel):
    idCategoriaProducto: Optional[int] = Field(None, example=1)
    idProveedor: Optional[int] = Field(None, example=1)
    nombreProducto: Optional[str] = Field(None, min_length=1, max_length=100, example="Cola 2 Litros")
    descripcionProducto: Optional[str] = Field(None, max_length=255, example="Bebida gaseosa sabor cola")
    precioUnitarioVenta: Optional[float] = Field(None, gt=0, example=2.50)
    precioUnitarioCompra: Optional[float] = Field(None, gt=0, example=1.80)
    tieneIva: Optional[bool] = None
    activoProducto: Optional[bool] = None

class ProductoRespuestaSchema(BaseModel):
    idProducto: int
    idCategoriaProducto: int
    idProveedor: int
    nombreProducto: str
    descripcionProducto: Optional[str] = None
    precioUnitarioVenta: float
    precioUnitarioCompra: float
    tieneIva: bool
    activoProducto: bool
    categoria: CategoriaProductoRespuestaSchema
    proveedor: ProveedorRespuestaSchema

    class Config:
        from_attributes = True


class ProductoResumenSchema(BaseModel):
    idProducto: int
    nombreProducto: str
    precioUnitarioVenta: float
    tieneIva: bool
    activoProducto: bool

    class Config:
        from_attributes = True
