from app.Productos.models.categoriaProductoModel import CategoriaProducto
from app.Productos.schemas.categoriaProductoSchemas import *
from app.Productos.models.productoModel import Producto

class CategoriaProductoRepository:
    def __init__(self, dbSession):
        self.dbSession = dbSession

    def listarCategorias(self):
        return self.dbSession.query(CategoriaProducto).all()

    def obtenerPorId(self, idCategoria: int):
        return self.dbSession.query(CategoriaProducto).filter(CategoriaProducto.idCategoriaProducto == idCategoria).first()

    def validarNombreExistente(self, nombre: str, excluirId: int = None):
        query = self.dbSession.query(CategoriaProducto).filter(CategoriaProducto.nombreCategoria == nombre)
        if excluirId is not None:
            query = query.filter(CategoriaProducto.idCategoriaProducto != excluirId)
        return query.first()

    def crearCategoria(self, categoria: CategoriaProductoCrearSchema):
        if self.validarNombreExistente(categoria.nombreCategoria):
            return None
        nuevo = CategoriaProducto(nombreCategoria=categoria.nombreCategoria, activoCategoria=True)
        self.dbSession.add(nuevo)
        self.dbSession.commit()
        self.dbSession.refresh(nuevo)
        return nuevo

    def modificarCategoria(self, idCategoria: int, categoriaActualizar: CategoriaProductoActualizarSchema):
        categoria = self.obtenerPorId(idCategoria)
        if not categoria:
            return None
        datos = categoriaActualizar.model_dump(exclude_unset=True)
        # Validar nombre: si existe y pertenece a otro id => conflicto
        if "nombreCategoria" in datos:
            nombreNuevo = datos["nombreCategoria"]
            existente = self.validarNombreExistente(nombreNuevo)
            if existente and existente.idCategoriaProducto != idCategoria:
                return False
        for campo, valor in datos.items():
            if campo in ["nombreCategoria", "activoCategoria"]:
                setattr(categoria, campo, valor)
        self.dbSession.commit()
        self.dbSession.refresh(categoria)
        return categoria

    def deshabilitarCategoria(self, idCategoria: int):
        categoria = self.obtenerPorId(idCategoria)
        if not categoria:
            return None
        # Verificar que no existan productos activos asociados
        productoActivo = self.dbSession.query(Producto).filter(Producto.idCategoriaProducto == idCategoria, Producto.activoProducto == True).first()
        if productoActivo:
            return False
        categoria.activoCategoria = False
        self.dbSession.commit()
        self.dbSession.refresh(categoria)
        return categoria

    def crearCategoriasIniciales(self):
        categorias = [
            {"nombreCategoria": "Bebidas", "activoCategoria": True},
            {"nombreCategoria": "Snacks", "activoCategoria": True},
            {"nombreCategoria": "Abarrotes", "activoCategoria": True},
            {"nombreCategoria": "Aseo y Limpieza", "activoCategoria": True},
            {"nombreCategoria": "Higiene Personal", "activoCategoria": True},
        ]

        for c in categorias:
            existe = self.validarNombreExistente(c["nombreCategoria"]) 
            if not existe:
                nuevo = CategoriaProducto(**c)
                self.dbSession.add(nuevo)
        print("Categorías por defecto creadas...!")
        self.dbSession.commit()
        self.dbSession.close()
