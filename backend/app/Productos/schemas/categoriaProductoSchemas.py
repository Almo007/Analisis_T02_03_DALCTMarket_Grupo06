from pydantic import BaseModel, Field
from typing import Optional

class CategoriaProductoBaseSchema(BaseModel):
    nombreCategoria: str = Field(..., min_length=1, max_length=50, example="Bebidas")

class CategoriaProductoCrearSchema(CategoriaProductoBaseSchema):
    pass

class CategoriaProductoActualizarSchema(BaseModel):
    nombreCategoria: Optional[str] = Field(None, min_length=1, max_length=50, example="Bebidas")
    activoCategoria: Optional[bool] = None

class CategoriaProductoRespuestaSchema(BaseModel):
    idCategoriaProducto: int
    nombreCategoria: str
    activoCategoria: bool

    class Config:
        from_attributes = True
