from fastapi import APIRouter, Depends
from app.configuracionGeneral.schemasGenerales import respuestaApi
from app.ParametrosSistema.services.parametroSistemaService import ParametroSistemaService
from app.ParametrosSistema.schemas.parametroSistemaSchemas import *
from app.database import obtenerSesion
from app.configuracionGeneral.seguridadJWT import protegerRuta

router = APIRouter(dependencies=[Depends(protegerRuta("ParametrosSistema", "ALL"))])

@router.get("/", tags=["ParametrosSistema"], summary="Obtener todos los parámetros", status_code=200, response_model=respuestaApi)
async def obtenerParametros(dbSession=Depends(obtenerSesion)):
    servicio = ParametroSistemaService(dbSession)
    return servicio.listarParametros()

@router.get("/{idParametro}", tags=["ParametrosSistema"], summary="Obtener un parámetro por id", status_code=200, response_model=respuestaApi)
async def obtenerParametroPorId(idParametro: int, dbSession=Depends(obtenerSesion)):
    servicio = ParametroSistemaService(dbSession)
    return servicio.obtenerParametroPorId(idParametro)

@router.post("/", tags=["ParametrosSistema"], summary="Crear un parámetro", status_code=201, response_model=respuestaApi)
async def crearParametro(parametro: ParametroSistemaCrearSchema, dbSession=Depends(obtenerSesion)):
    servicio = ParametroSistemaService(dbSession)
    return servicio.crearParametro(parametro)

@router.put("/{idParametro}", tags=["ParametrosSistema"], summary="Actualizar un parámetro", status_code=200, response_model=respuestaApi)
async def actualizarParametro(idParametro: int, parametro: ParametroSistemaActualizarSchema, dbSession=Depends(obtenerSesion)):
    servicio = ParametroSistemaService(dbSession)
    return servicio.modificarParametro(idParametro, parametro)

@router.delete("/{idParametro}", tags=["ParametrosSistema"], summary="Eliminar (soft delete) un parámetro por id", status_code=200, response_model=respuestaApi)
async def deshabilitarParametro(idParametro: int, dbSession=Depends(obtenerSesion)):
    servicio = ParametroSistemaService(dbSession)
    return servicio.deshabilitarParametro(idParametro)
