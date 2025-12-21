from fastapi import APIRouter, Depends
from app.Venta.services.ventaService import VentaService
from app.Venta.schemas.ventaSchemas import VentaCrearSchema
from app.database import obtenerSesion
from app.configuracionGeneral.seguridadJWT import protegerRuta
from app.configuracionGeneral.schemasGenerales import respuestaApi

router = APIRouter()

@router.post("/crear", tags=["Venta"], summary="Crear venta", description="Registra una venta y sus detalles; valida stock, promociones y caja abierta.", status_code=201, response_model=respuestaApi)
async def crear_venta(venta: VentaCrearSchema, dbSession=Depends(obtenerSesion), usuario=Depends(protegerRuta("Venta","POST"))):
    return VentaService(dbSession).crearVenta(venta, usuario)

@router.get("/", tags=["Venta"], summary="Listar ventas (hoy)", description="Lista ventas del día actual; Administrador ve todas, Cajero sus ventas.", status_code=200, response_model=respuestaApi)
async def listar_ventas(dbSession=Depends(obtenerSesion), usuario=Depends(protegerRuta("Venta","GET"))):
    return VentaService(dbSession).listarVentasHoy(usuario)

@router.get("/historico", tags=["Venta"], summary="Histórico de ventas", description="Lista todas las ventas (histórico). Solo Administrador.", status_code=200, response_model=respuestaApi)
async def listar_historico(dbSession=Depends(obtenerSesion), usuario=Depends(protegerRuta("Venta","GET"))):
    return VentaService(dbSession).listarHistorico(usuario)

@router.delete("/{idVenta}", tags=["Venta"], summary="Anular venta", description="Anula una venta (Administrador cualquier venta; Cajero solo las suyas).", status_code=200, response_model=respuestaApi)
async def anular_venta(idVenta: int, dbSession=Depends(obtenerSesion), usuario=Depends(protegerRuta("Venta","DELETE"))):
    return VentaService(dbSession).anularVenta(idVenta, usuario)

@router.get("/generar-comprobante/{idVenta}", tags=["Venta"], summary="Generar comprobante de venta", description="Genera un comprobante con parámetros del negocio y datos de la venta.", status_code=200, response_model=respuestaApi)
async def generar_comprobante(idVenta: int, dbSession=Depends(obtenerSesion), usuario=Depends(protegerRuta("Venta","GET"))):
    return VentaService(dbSession).generarComprobanteVenta(idVenta, usuario)
