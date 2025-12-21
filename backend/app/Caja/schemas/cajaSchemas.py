from pydantic import BaseModel, Field, validator
from typing import Dict, Optional, List
from datetime import datetime, date
from app.Usuarios.schemas.usuarioSchemas import UsuarioPublicoSchema

class CajaCrearSchema(BaseModel):
    # Enviar únicamente el monto inicial como número (ej. 95.0)
    montoInicial: float = Field(..., example=95.0)

    class Config:
        schema_extra = {
            "example": {
                "montoInicial": 95.0,
                "montoFinal": 120.5
            }
        }

class CajaCerrarSchema(BaseModel):
    # Enviar únicamente el monto final declarado como número (ej. 120.5)
    montoFinal: float = Field(..., example=120.5)

class CajaHistorialRespuestaSchema(BaseModel):
    idCaja: int
    usuario: Optional[UsuarioPublicoSchema] = None
    fechaAperturaCaja: datetime
    fechaCierreCaja: Optional[datetime] = None
    montoInicialDeclarado: float
    montoCierreDeclarado: Optional[float] = None
    montoCierreSistema: Optional[float] = None
    diferenciaCaja: Optional[float] = None
    estadoCaja: str
    detalle: Optional[str] = None

    class Config:
        from_attributes = True

class CajaListaRespuestaSchema(BaseModel):
    cajas: List[CajaHistorialRespuestaSchema] = []

    class Config:
        from_attributes = True