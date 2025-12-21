from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import date, datetime, timezone, timedelta
from app.Productos.schemas.productoSchemas import ProductoRespuestaSchema

class PromocionCrearSchema(BaseModel):
    idProducto: int = Field(..., example=1)
    nombrePromocion: str = Field(..., example="Promo Verano")
    porcentajePromocion: float = Field(..., gt=0, le=100, example=20.0)
    fechaInicioPromocion: date = Field(..., example="2025-12-01")
    fechaFinPromocion: date = Field(..., example="2025-12-31")

    @validator("fechaInicioPromocion")
    def check_inicio_not_past(cls, v):
        # fecha de inicio debe ser hoy o mayor en la zona de Quito (UTC-5)
        quito_now = datetime.now(timezone(timedelta(hours=-5))).date()
        if v < quito_now:
            raise ValueError("fechaInicioPromocion debe ser igual o posterior al día actual")
        return v

    @validator("fechaFinPromocion")
    def check_dates(cls, v, values):
        inicio = values.get("fechaInicioPromocion")
        if inicio and v < inicio:
            raise ValueError("fechaFinPromocion debe ser igual o posterior a fechaInicioPromocion")
        return v

class PromocionRespuestaSchema(BaseModel):
    idPromocion: int
    producto: ProductoRespuestaSchema
    nombrePromocion: str
    porcentajePromocion: float
    fechaInicioPromocion: datetime
    fechaFinPromocion: datetime
    activoPromocion: bool

    class Config:
        from_attributes = True

class PromocionResumenSchema(BaseModel):
    idPromocion: int
    idProducto: int
    nombrePromocion: str
    porcentajePromocion: float
    fechaInicioPromocion: datetime
    fechaFinPromocion: datetime
    activoPromocion: bool

    class Config:
        from_attributes = True

class PromocionListaSchema(BaseModel):
    promociones: List[PromocionRespuestaSchema] = []

    class Config:
        from_attributes = True
