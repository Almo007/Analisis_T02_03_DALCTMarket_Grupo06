from fastapi import APIRouter, Depends
from app.Caja.services.cajaService import CajaService
from app.Caja.schemas.cajaSchemas import *
from app.database import obtenerSesion
from app.configuracionGeneral.seguridadJWT import protegerRuta
from app.configuracionGeneral.schemasGenerales import respuestaApi

router = APIRouter()

@router.post("/abrir", tags=["Caja"], summary="Abrir caja", description="Abre una nueva caja para el usuario autenticado y registra la fecha de apertura y el monto inicial declarado.", status_code=201, response_model=respuestaApi)
async def abrir_caja(caja: CajaCrearSchema, dbSession=Depends(obtenerSesion), usuario=Depends(protegerRuta("Caja", "POST"))):
    return CajaService(dbSession).crearCajaHistorial(caja, usuario)

@router.post("/cerrar/{idCaja}", tags=["Caja"], summary="Cerrar caja", description="Cierra una caja abierta y registra la fecha de cierre (sistema), el monto final declarado y un detalle que indica quién cerró y si hubo alguna anomalía. Los Cajeros solo pueden cerrar su propia caja el mismo día; los Administradores pueden cerrar cualquier caja por id.", status_code=200, response_model=respuestaApi)
async def cerrar_caja(idCaja: int, cierre: CajaCerrarSchema, dbSession=Depends(obtenerSesion), usuario=Depends(protegerRuta("Caja","POST"))):
    return CajaService(dbSession).cerrarCaja(idCaja, cierre, usuario)

@router.get("/listar", tags=["Caja"], summary="Listar cajas (hoy)", description="Lista las cajas del día actual; los Administradores ven las de todos los usuarios y los Cajeros solo las suyas.", status_code=200, response_model=respuestaApi)
async def listar_cajas(dbSession=Depends(obtenerSesion), usuario=Depends(protegerRuta("Caja","GET"))):
    return CajaService(dbSession).listarCajasHoy(usuario)

@router.get("/listar/todas", tags=["Caja"], summary="Listar todas las cajas", description="Lista todas las cajas (histórico). Solo Administrador.", status_code=200, response_model=respuestaApi)
async def listar_cajas_todas(dbSession=Depends(obtenerSesion), usuario=Depends(protegerRuta("Caja", "GET"))):
    return CajaService(dbSession).listarTodasCajas(usuario)

@router.post("/reabrir/{idCaja}", tags=["Caja"], summary="Reabrir caja", description="Reabre una caja ya cerrada por su id. Solo el rol Administrador puede reabrir cajas cerradas.", status_code=200, response_model=respuestaApi)
async def reabrir_caja(idCaja: int, dbSession=Depends(obtenerSesion), usuario=Depends(protegerRuta("Caja", "POST"))):
    return CajaService(dbSession).reabrirCaja(idCaja, usuario)

# Nota: los endpoints de cierre pendiente y filtrado han sido eliminados. Sólo quedan: abrir (POST /abrir), cerrar (POST /cerrar/{idCaja}), listar (GET /listar).