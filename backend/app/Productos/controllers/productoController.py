from fastapi import APIRouter, Depends
from app.Productos.services.productoService import ProductoService
from app.Productos.schemas.productoSchemas import *
from app.database import obtenerSesion
from app.configuracionGeneral.seguridadJWT import protegerRuta
from app.configuracionGeneral.schemasGenerales import respuestaApi

router = APIRouter()

@router.get("/", tags=["Producto"], summary="Obtener todos los productos", status_code=200, response_model=respuestaApi)
async def obtenerTodosLosProductos(dbSession=Depends(obtenerSesion), usuario=Depends(protegerRuta("Productos", "GET"))):
    return ProductoService(dbSession).listarProductos()

@router.get("/{idProducto}", tags=["Producto"], summary="Obtener un producto por id", status_code=200, response_model=respuestaApi)
async def obtenerProductoPorId(idProducto: int, dbSession=Depends(obtenerSesion), usuario=Depends(protegerRuta("Productos", "GET"))):
    return ProductoService(dbSession).obtenerPorId(idProducto)

@router.post("/", tags=["Producto"], description="Crear un nuevo producto. Si se envía 'cantidadDisponible' y/o 'cantidadMinima', se creará automáticamente el inventario con esas cantidades; si no se envían, se crearán con 0 y podrán ajustarse luego mediante el endpoint /inventario.", status_code=201, response_model=respuestaApi)
async def crearProducto(producto: ProductoCrearSchema, dbSession=Depends(obtenerSesion), usuario=Depends(protegerRuta("Productos", "ALL"))):
    return ProductoService(dbSession).crearProducto(producto)

@router.put("/{idProducto}", tags=["Producto"], summary="Actualizar un producto por id", status_code=200, response_model=respuestaApi)
async def actualizarProducto(idProducto: int, producto: ProductoActualizarSchema, dbSession=Depends(obtenerSesion), usuario=Depends(protegerRuta("Productos", "ALL"))):
    return ProductoService(dbSession).modificarProducto(idProducto, producto)

@router.delete("/{idProducto}", tags=["Producto"], summary="Deshabilitar un producto por id", status_code=200, response_model=respuestaApi)
async def deshabilitarProducto(idProducto: int, dbSession=Depends(obtenerSesion), usuario=Depends(protegerRuta("Productos", "ALL"))):
    return ProductoService(dbSession).deshabilitarProducto(idProducto)
