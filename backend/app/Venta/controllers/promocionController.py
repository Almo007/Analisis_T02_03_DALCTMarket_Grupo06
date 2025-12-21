from fastapi import APIRouter, Depends
from app.Venta.services.promocionService import PromocionService
from app.Venta.schemas.promocionSchemas import *
from app.database import obtenerSesion
from app.configuracionGeneral.seguridadJWT import protegerRuta
from app.configuracionGeneral.schemasGenerales import respuestaApi

router = APIRouter()

@router.get("/", tags=["Promocion"], summary="Listar todas las promociones", description="Devuelve todas las promociones registradas (activas e inactivas). Útil para administradores y cajeros para aplicar sobre las ventas.", status_code=200, response_model=respuestaApi)
async def listar_promociones(dbSession=Depends(obtenerSesion), usuario=Depends(protegerRuta("Promocion", "GET"))):
    return PromocionService(dbSession).listarPromociones()

@router.post("/", tags=["Promocion"], summary="Crear promoción", description="Crear una nueva promoción. Sólo el rol Administrador puede crear promociones.", status_code=201, response_model=respuestaApi)
async def crear_promocion(promocion: PromocionCrearSchema, dbSession=Depends(obtenerSesion), usuario=Depends(protegerRuta("Promocion", "POST"))):
    return PromocionService(dbSession).crearPromocion(promocion, usuario)

@router.get("/{idPromocion}", tags=["Promocion"], summary="Obtener promoción por id", description="Obtener los detalles de una promoción específica por su id.", status_code=200, response_model=respuestaApi)
async def obtener_promocion(idPromocion: int, dbSession=Depends(obtenerSesion), usuario=Depends(protegerRuta("Promocion", "GET"))):
    return PromocionService(dbSession).obtenerPorId(idPromocion)

@router.get("/producto/{idProducto}", tags=["Promocion"], summary="Obtener promociones activas por producto", description="Devuelve las promociones activas para un producto (aquellas cuya fecha de fin no ha pasado).", status_code=200, response_model=respuestaApi)
async def promociones_por_producto(idProducto: int, dbSession=Depends(obtenerSesion), usuario=Depends(protegerRuta("Promocion", "GET"))):
    return PromocionService(dbSession).obtenerActivasPorProducto(idProducto)

@router.delete("/{idPromocion}", tags=["Promocion"], summary="Deshabilitar promoción", description="Deshabilitar una promoción existente. Sólo el rol Administrador puede deshabilitar promociones.", status_code=200, response_model=respuestaApi)
async def deshabilitar_promocion(idPromocion: int, dbSession=Depends(obtenerSesion), usuario=Depends(protegerRuta("Promocion", "DELETE"))):
    return PromocionService(dbSession).deshabilitarPromocion(idPromocion)

@router.get("/aplicable/{idProducto}", tags=["Promocion"], summary="Obtener promoción aplicable (activa y mayor descuento) para un producto", description="Devuelve la promoción activa aplicable para un producto: la promoción activa con mayor porcentaje de descuento.", status_code=200, response_model=respuestaApi)
async def promocion_aplicable(idProducto: int, dbSession=Depends(obtenerSesion), usuario=Depends(protegerRuta("Promocion", "GET"))):
    return PromocionService(dbSession).obtenerPromocionAplicable(idProducto)
