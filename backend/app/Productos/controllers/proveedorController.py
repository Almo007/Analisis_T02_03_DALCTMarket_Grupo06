from fastapi import APIRouter, Depends
from app.Productos.services.proveedorService import ProveedorService
from app.Productos.schemas.proveedorSchemas import *
from app.database import obtenerSesion
from app.configuracionGeneral.seguridadJWT import protegerRuta
from app.configuracionGeneral.schemasGenerales import respuestaApi

router = APIRouter(dependencies=[Depends(protegerRuta("Productos", "ALL"))])

@router.get("/", tags=["Proveedor"], summary="Obtener todos los proveedores", status_code=200, response_model=respuestaApi)
async def obtenerTodosLosProveedores(dbSession=Depends(obtenerSesion)):
    return ProveedorService(dbSession).listarProveedores()

@router.get("/{idProveedor}", tags=["Proveedor"], summary="Obtener un proveedor por id", status_code=200, response_model=respuestaApi)
async def obtenerProveedorPorId(idProveedor: int, dbSession=Depends(obtenerSesion)):
    return ProveedorService(dbSession).obtenerPorId(idProveedor)

@router.post("/", tags=["Proveedor"], description="Crear un nuevo proveedor", status_code=201, response_model=respuestaApi)
async def crearProveedor(proveedor: ProveedorCrearSchema, dbSession=Depends(obtenerSesion)):
    return ProveedorService(dbSession).crearProveedor(proveedor)

@router.put("/{idProveedor}", tags=["Proveedor"], summary="Actualizar un proveedor por id", status_code=200, response_model=respuestaApi)
async def actualizarProveedor(idProveedor: int, proveedor: ProveedorActualizarSchema, dbSession=Depends(obtenerSesion)):
    return ProveedorService(dbSession).modificarProveedor(idProveedor, proveedor)

@router.delete("/{idProveedor}", tags=["Proveedor"], summary="Deshabilitar un proveedor por id", status_code=200, response_model=respuestaApi)
async def deshabilitarProveedor(idProveedor: int, dbSession=Depends(obtenerSesion)):
    return ProveedorService(dbSession).deshabilitarProveedor(idProveedor)
