from app.Productos.repositories.categoriaProductoRepository import CategoriaProductoRepository
from app.configuracionGeneral.schemasGenerales import respuestaApi
from fastapi import HTTPException
from app.Productos.schemas.categoriaProductoSchemas import *

class CategoriaProductoService:
    def __init__(self, dbSession):
        self.dbSession = dbSession
        self.categoriaRepository = CategoriaProductoRepository(dbSession)

    def listarCategorias(self):
        categorias = self.categoriaRepository.listarCategorias()
        if categorias is None:
            return respuestaApi(success=True, message="No se encontraron categorias", data=[])
        categorias = [CategoriaProductoRespuestaSchema.from_orm(c) for c in categorias]
        return respuestaApi(success=True, message="Categorias encontrados", data=categorias)

    def obtenerPorId(self, idCategoria: int):
        categoria = self.categoriaRepository.obtenerPorId(idCategoria)
        if categoria is None:
            raise HTTPException(status_code=404, detail="Categoria no encontrada")
        categoria = CategoriaProductoRespuestaSchema.from_orm(categoria)
        return respuestaApi(success=True, message="Categoria encontrada", data=categoria)

    def crearCategoria(self, categoria: CategoriaProductoCrearSchema):
        creado = self.categoriaRepository.crearCategoria(categoria)
        if creado is None:
            raise HTTPException(status_code=400, detail="La categoria ya existe")
        creado = CategoriaProductoRespuestaSchema.from_orm(creado)
        return respuestaApi(success=True, message="Categoria creada", data=creado)

    def modificarCategoria(self, idCategoria: int, categoria: CategoriaProductoActualizarSchema):
        actualizado = self.categoriaRepository.modificarCategoria(idCategoria, categoria)
        if actualizado is None:
            raise HTTPException(status_code=404, detail="Categoria no encontrada")
        if actualizado is False:
            raise HTTPException(status_code=400, detail="El nombre de categoria ya existe")
        actualizado = CategoriaProductoRespuestaSchema.from_orm(actualizado)
        return respuestaApi(success=True, message="Categoria actualizada", data=actualizado)

    def deshabilitarCategoria(self, idCategoria: int):
        des = self.categoriaRepository.deshabilitarCategoria(idCategoria)
        if des is None:
            raise HTTPException(status_code=404, detail="Categoria no encontrada")
        if des is False:
            raise HTTPException(status_code=400, detail="No se puede deshabilitar la categoría: existen productos activos asociados")
        des = CategoriaProductoRespuestaSchema.from_orm(des)
        return respuestaApi(success=True, message="Categoria deshabilitada", data=des)
