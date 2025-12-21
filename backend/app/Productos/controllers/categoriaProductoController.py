from fastapi import APIRouter, Depends
from app.Productos.services.categoriaProductoService import CategoriaProductoService
from app.Productos.schemas.categoriaProductoSchemas import *
from app.database import obtenerSesion
from app.configuracionGeneral.seguridadJWT import protegerRuta
from app.configuracionGeneral.schemasGenerales import respuestaApi

router = APIRouter(dependencies=[Depends(protegerRuta("Productos", "ALL"))])

@router.get("/", tags=["CategoriaProducto"], summary="Obtener todas las categorias", status_code=200, response_model=respuestaApi)
async def obtenerTodasLasCategorias(dbSession=Depends(obtenerSesion)):
    return CategoriaProductoService(dbSession).listarCategorias()

@router.get("/{idCategoria}", tags=["CategoriaProducto"], summary="Obtener una categoria por id", status_code=200, response_model=respuestaApi)
async def obtenerCategoriaPorId(idCategoria: int, dbSession=Depends(obtenerSesion)):
    return CategoriaProductoService(dbSession).obtenerPorId(idCategoria)

@router.post("/", tags=["CategoriaProducto"], description="Crear una nueva categoria", status_code=201, response_model=respuestaApi)
async def crearCategoria(categoria: CategoriaProductoCrearSchema, dbSession=Depends(obtenerSesion)):
    return CategoriaProductoService(dbSession).crearCategoria(categoria)

@router.put("/{idCategoria}", tags=["CategoriaProducto"], summary="Actualizar una categoria por id", status_code=200, response_model=respuestaApi)
async def actualizarCategoria(idCategoria: int, categoria: CategoriaProductoActualizarSchema, dbSession=Depends(obtenerSesion)):
    return CategoriaProductoService(dbSession).modificarCategoria(idCategoria, categoria)

@router.delete("/{idCategoria}", tags=["CategoriaProducto"], summary="Deshabilitar una categoria por id", status_code=200, response_model=respuestaApi)
async def deshabilitarCategoria(idCategoria: int, dbSession=Depends(obtenerSesion)):
    return CategoriaProductoService(dbSession).deshabilitarCategoria(idCategoria)
