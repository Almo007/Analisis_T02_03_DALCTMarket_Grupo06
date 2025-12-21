from app.Productos.repositories.productoRepository import ProductoRepository
from app.configuracionGeneral.schemasGenerales import respuestaApi
from fastapi import HTTPException
from app.Productos.schemas.productoSchemas import *

class ProductoService:
    def __init__(self, dbSession):
        self.dbSession = dbSession
        self.productoRepository = ProductoRepository(dbSession)

    def listarProductos(self):
        productos = self.productoRepository.listarProductos()
        if productos is None:
            return respuestaApi(success=True, message="No se encontraron productos", data=[])
        productos = [ProductoRespuestaSchema.from_orm(p) for p in productos]
        return respuestaApi(success=True, message="Productos encontrados", data=productos)

    def obtenerPorId(self, idProducto: int):
        producto = self.productoRepository.obtenerPorId(idProducto)
        if producto is None:
            raise HTTPException(status_code=404, detail="Producto no encontrado")
        producto = ProductoRespuestaSchema.from_orm(producto)
        return respuestaApi(success=True, message="Producto encontrado", data=producto)

    def crearProducto(self, producto: ProductoCrearSchema):
        creado = self.productoRepository.crearProducto(producto)
        if isinstance(creado, dict) and "error" in creado:
            missing = creado["error"]
            # Mapear códigos a mensajes
            mensajes = []
            if "categoria" in missing and "proveedor" in missing:
                raise HTTPException(status_code=400, detail="Categoria y Proveedor no existen")
            if "categoria" in missing:
                mensajes.append("Categoria no existe")
            if "proveedor" in missing:
                mensajes.append("Proveedor no existe")
            if "categoria_inactiva" in missing:
                mensajes.append("Categoria deshabilitada")
            if "proveedor_inactiva" in missing:
                mensajes.append("Proveedor deshabilitado")
            if "cantidad_disponible_negativa" in missing:
                mensajes.append("cantidadDisponible no puede ser negativa")
            if "cantidad_minima_negativa" in missing:
                mensajes.append("cantidadMinima no puede ser negativa")
            raise HTTPException(status_code=400, detail="; ".join(mensajes))
        if creado is None:
            raise HTTPException(status_code=400, detail="Error al crear producto")
        inventario_creado = False
        producto_obj = creado
        # Si el repo devuelve una tupla (producto, inventario_creado)
        if isinstance(creado, tuple):
            producto_obj, inventario_creado = creado
        producto_resp = ProductoRespuestaSchema.from_orm(producto_obj)
        if inventario_creado:
            return respuestaApi(success=True, message="Producto e inventario creados", data=producto_resp)
        return respuestaApi(success=True, message="Producto creado", data=producto_resp)

    def modificarProducto(self, idProducto: int, producto: ProductoActualizarSchema):
        actualizado = self.productoRepository.modificarProducto(idProducto, producto)
        if actualizado is None:
            raise HTTPException(status_code=404, detail="Producto no encontrado")
        if isinstance(actualizado, dict) and "error" in actualizado:
            missing = actualizado["error"]
            mensajes = []
            if "categoria" in missing and "proveedor" in missing:
                raise HTTPException(status_code=400, detail="Categoria y Proveedor no existen")
            if "categoria" in missing:
                mensajes.append("Categoria no existe")
            if "proveedor" in missing:
                mensajes.append("Proveedor no existe")
            if "categoria_inactiva" in missing:
                mensajes.append("Categoria deshabilitada")
            if "proveedor_inactiva" in missing:
                mensajes.append("Proveedor deshabilitado")
            raise HTTPException(status_code=400, detail="; ".join(mensajes))
        actualizado = ProductoRespuestaSchema.from_orm(actualizado)
        return respuestaApi(success=True, message="Producto actualizado", data=actualizado)

    def deshabilitarProducto(self, idProducto: int):
        des = self.productoRepository.deshabilitarProducto(idProducto)
        if des is None:
            raise HTTPException(status_code=404, detail="Producto no encontrado")
        des = ProductoRespuestaSchema.from_orm(des)
        return respuestaApi(success=True, message="Producto deshabilitado", data=des)