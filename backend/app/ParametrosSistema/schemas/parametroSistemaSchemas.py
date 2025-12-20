from pydantic import BaseModel, Field
from typing import Optional

class ParametroSistemaBaseSchema(BaseModel):
    claveParametro: str = Field(..., min_length=1, max_length=50, example="nombreNegocio")
    valorParametro: str = Field(..., min_length=0, max_length=500, example="DALCT Market")

class ParametroSistemaCrearSchema(ParametroSistemaBaseSchema):
    pass

class ParametroSistemaActualizarSchema(BaseModel):
    claveParametro: Optional[str] = Field(None, min_length=1, max_length=50, example="nombreNegocio")
    valorParametro: Optional[str] = Field(None, min_length=0, max_length=500, example="DALCT Market")
    activoParametro: Optional[bool] = None

class ParametroSistemaRespuestaSchema(BaseModel):
    idParametroSistema: int
    claveParametro: str
    valorParametro: str
    activoParametro: bool

    class Config:
        from_attributes = True
