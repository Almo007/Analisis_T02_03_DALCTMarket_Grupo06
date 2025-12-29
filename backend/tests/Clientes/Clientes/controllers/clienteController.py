from fastapi import APIRouter, Depends
from app.Clientes.services.clienteService import ClienteService
from app.Clientes.schemas.clienteSchemas import *
from app.database import obtenerSesion
from app.configuracionGeneral.seguridadJWT import protegerRuta
from app.configuracionGeneral.schemasGenerales import respuestaApi

router = APIRouter(dependencies=[Depends(protegerRuta("Cliente", "ALL"))])

@router.get("/", tags=["Clientes"], summary="Obtener todos los clientes", status_code=200, response_model=respuestaApi)
async def obtenerTodosLosClientes(dbSession=Depends(obtenerSesion)):
    return ClienteService(dbSession).listarClientes()

@router.get("/{idCliente}", tags=["Clientes"], summary="Obtener un cliente por id", status_code=200, response_model=respuestaApi)
async def obtenerCliente(idCliente: int, dbSession=Depends(obtenerSesion)):
    return ClienteService(dbSession).obtenerPorId(idCliente)

@router.post("/", tags=["Clientes"], description="Crear un nuevo cliente", status_code=201, response_model=respuestaApi)
async def crearCliente(cliente: ClienteCrearSchema, dbSession=Depends(obtenerSesion)):
    return ClienteService(dbSession).crearCliente(cliente)

@router.put("/{idCliente}", tags=["Clientes"], summary="Actualizar un cliente por id", status_code=200, response_model=respuestaApi)
async def actualizarCliente(idCliente: int, cliente: ClienteActualizarSchema, dbSession=Depends(obtenerSesion)):
    return ClienteService(dbSession).modificarCliente(idCliente, cliente)

@router.delete("/{idCliente}", tags=["Clientes"], summary="Deshabilitar un cliente por id", status_code=200, response_model=respuestaApi)
async def deshabilitarCliente(idCliente: int, dbSession=Depends(obtenerSesion)):
    return ClienteService(dbSession).deshabilitarCliente(idCliente)
