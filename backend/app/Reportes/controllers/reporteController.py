from fastapi import APIRouter, Depends
from app.Reportes.services.reporteService import ReporteService
from app.Reportes.schemas.reporteSchemas import InventarioFiltro, VentasFiltro, CajaFiltro, ClientesFiltro
from app.database import obtenerSesion
from app.configuracionGeneral.seguridadJWT import protegerRuta
from app.configuracionGeneral.schemasGenerales import respuestaApi

router = APIRouter()

@router.post("/inventario", tags=["Reportes"], summary="Informe de inventario", description="Genera un informe del inventario actual. Filtros opcionales (se pueden combinar): idProducto (id exacto del producto), idCategoria (id de la categoría), nombreProducto (búsqueda parcial).", status_code=200, response_model=respuestaApi)
async def reporte_inventario(filtro: InventarioFiltro, dbSession=Depends(obtenerSesion), usuario=Depends(protegerRuta("Reportes","GET_Stock"))):
    return ReporteService(dbSession).reporteInventario(filtro, usuario)

@router.post("/ventas-producto-categoria", tags=["Reportes"], summary="Informe de ventas por producto y categoría", description="Genera reporte de ventas filtrado por producto/categoría y rango de fechas. Filtros: fechaInicio (YYYY-MM-DD) — obligatoria, fechaFin (YYYY-MM-DD) — obligatoria, idProducto (opcional), idCategoria (opcional). Debe proporcionar al menos idProducto o idCategoria.", status_code=200, response_model=respuestaApi)
async def reporte_ventas(filtro: VentasFiltro, dbSession=Depends(obtenerSesion), usuario=Depends(protegerRuta("Reportes","GET_Ventas"))):
    return ReporteService(dbSession).reporteVentasProductoCategoria(filtro, usuario)

@router.post("/resumen-caja", tags=["Reportes"], summary="Resumen de caja diaria", description="Consulta cierres de caja para un cajero en la fecha indicada. Filtros en body: fecha (YYYY-MM-DD) — fecha de referencia, idUsuarioCaja (id del usuario/cajero, obligatorio) — se buscarán todas las cajas abiertas por ese usuario en la fecha; retorna caja(s) y sus ventas con detalle.", status_code=200, response_model=respuestaApi)
async def resumen_caja(filtro: CajaFiltro, dbSession=Depends(obtenerSesion), usuario=Depends(protegerRuta("Reportes","GET_Caja"))):
    return ReporteService(dbSession).resumenCajaDiaria(filtro.fecha, filtro.idUsuarioCaja, usuario)

@router.post("/clientes-frecuentes", tags=["Reportes"], summary="Informe de clientes frecuentes", description="Identifica clientes frecuentes según parámetros en el body: dias (periodo en días, default 30), minVentas (mínimo número de ventas, default 3), minGasto (gasto mínimo en el periodo, default 100.0).", status_code=200, response_model=respuestaApi)
async def clientes_frecuentes(filtro: ClientesFiltro, dbSession=Depends(obtenerSesion), usuario=Depends(protegerRuta("Reportes","GET_Clientes"))):
    return ReporteService(dbSession).clientesFrecuentes(filtro, usuario)
