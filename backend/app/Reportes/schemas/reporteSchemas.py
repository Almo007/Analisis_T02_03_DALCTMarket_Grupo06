from pydantic import BaseModel, Field, field_validator
from typing import Optional, List
from datetime import date, datetime
from app.Usuarios.schemas.usuarioSchemas import UsuarioPublicoSchema
from app.Clientes.schemas.clienteSchemas import ClienteRespuestaSchema
from app.Venta.schemas.ventaSchemas import VentaRespuestaSchema
from app.Inventario.schemas.inventarioSchemas import InventarioRespuestaSchema

# Filtros
class InventarioFiltro(BaseModel):
    # Filtros opcionales (se pueden enviar cualquiera de los tres y se combinarán): idProducto, idCategoria, nombreProducto
    idProducto: Optional[int] = None
    idCategoria: Optional[int] = None
    nombreProducto: Optional[str] = None

class VentasFiltro(BaseModel):
    # Fechas obligatorias
    fechaInicio: date
    fechaFin: date
    idProducto: Optional[int] = None
    idCategoria: Optional[int] = None

    @field_validator("fechaFin")
    @classmethod
    def validar_fechas(cls, v, info):
        fechaInicio = info.data.get("fechaInicio")
        if fechaInicio and v < fechaInicio:
            raise ValueError("fechaFin debe ser mayor o igual a fechaInicio")
        return v

class CajaFiltro(BaseModel):
    fecha: date
    idUsuarioCaja: int

class ClientesFiltro(BaseModel):
    dias: int = Field(30, description="Periodo en días para considerar actividad")
    minVentas: int = Field(3, description="Mínimo número de ventas para ser frecuente")
    minGasto: float = Field(100.0, description="Gasto mínimo en el periodo")

# Respuestas
class InventarioReporteRespuesta(BaseModel):
    items: List[InventarioRespuestaSchema] = []

class VentasPorProductoItem(BaseModel):
    idProducto: int
    nombreProducto: str
    idCategoria: int
    nombreCategoria: str
    cantidadVendida: int
    ingresos: float

class VentasReporteRespuesta(BaseModel):
    items: List[VentasPorProductoItem] = []

class ResumenCajaItem(BaseModel):
    idCaja: int
    usuario: Optional[UsuarioPublicoSchema] = None
    fechaAperturaCaja: datetime
    fechaCierreCaja: Optional[datetime] = None
    montoInicialDeclarado: float
    montoCierreDeclarado: Optional[float] = None
    montoCierreSistema: Optional[float] = None
    diferenciaCaja: Optional[float] = None
    estadoCaja: str
    ventas: List[VentaRespuestaSchema] = []

class ResumenCajaRespuesta(BaseModel):
    items: List[ResumenCajaItem] = []

class ClienteFrecuenteItem(BaseModel):
    cliente: ClienteRespuestaSchema
    ventasCount: int
    totalGastado: float
    historialVentas: List[VentaRespuestaSchema] = []

class ClientesFrecuentesRespuesta(BaseModel):
    items: List[ClienteFrecuenteItem] = []
