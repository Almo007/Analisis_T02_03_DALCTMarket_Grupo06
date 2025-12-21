from app.Inventario.repositories.inventarioRepository import InventarioRepository
from app.configuracionGeneral.schemasGenerales import respuestaApi
from fastapi import HTTPException
from app.Inventario.schemas.inventarioSchemas import *

class InventarioService:
    def __init__(self, dbSession):
        self.dbSession = dbSession
        self.inventarioRepository = InventarioRepository(dbSession)

    def listarInventarios(self):
        invs = self.inventarioRepository.listarInventarios()
        if invs is None:
            return respuestaApi(success=True, message="No se encontraron inventarios", data=[])
        data = [InventarioRespuestaSchema.from_orm(i) for i in invs]
        return respuestaApi(success=True, message="Inventarios encontrados", data=data)

    def obtenerPorId(self, idInventario: int):
        inv = self.inventarioRepository.obtenerPorId(idInventario)
        if inv is None:
            raise HTTPException(status_code=404, detail="Inventario no encontrado")
        data = InventarioRespuestaSchema.from_orm(inv)
        return respuestaApi(success=True, message="Inventario encontrado", data=data)

    def obtenerPorProducto(self, idProducto: int):
        inv = self.inventarioRepository.obtenerPorProducto(idProducto)
        if inv is None:
            raise HTTPException(status_code=404, detail="Inventario no encontrado")
        data = InventarioRespuestaSchema.from_orm(inv)
        return respuestaApi(success=True, message="Inventario encontrado", data=data)

    def crearInventario(self, inventario: InventarioCrearSchema):
        # si ya existe inventario para el producto -> devolver existente (idempotente)
        existente = self.inventarioRepository.obtenerPorProducto(inventario.idProducto)
        if existente:
            data = InventarioRespuestaSchema.from_orm(existente)
            return respuestaApi(success=True, message="Inventario existente", data=data), 200
        creado = self.inventarioRepository.crearInventario(inventario)
        if isinstance(creado, dict) and "error" in creado:
            missing = creado["error"]
            mensajes = []
            if "producto" in missing:
                mensajes.append("Producto no existe")
            if "producto_inactiva" in missing:
                mensajes.append("Producto deshabilitado")
            raise HTTPException(status_code=400, detail="; ".join(mensajes))
        creado = InventarioRespuestaSchema.from_orm(creado)
        return respuestaApi(success=True, message="Inventario creado", data=creado), 201

    def modificarInventario(self, idInventario: int, inventario: InventarioActualizarSchema, usuario: dict):
        # restricciones por rol: Bodeguero no puede modificar cantidadDisponible
        datos = inventario.model_dump(exclude_unset=True)
        rol = usuario.get("rol")
        if rol == "Bodeguero" and "cantidadDisponible" in datos:
            raise HTTPException(status_code=403, detail="No tienes permiso para modificar la cantidad disponible")
        actualizado = self.inventarioRepository.modificarInventario(idInventario, inventario)
        if actualizado is None:
            raise HTTPException(status_code=404, detail="Inventario no encontrado")
        actualizado = InventarioRespuestaSchema.from_orm(actualizado)
        return respuestaApi(success=True, message="Inventario actualizado", data=actualizado)

    def deshabilitarInventario(self, idInventario: int):
        des = self.inventarioRepository.deshabilitarInventario(idInventario)
        if des is None:
            raise HTTPException(status_code=404, detail="Inventario no encontrado")
        if des is False:
            raise HTTPException(status_code=400, detail="No se puede deshabilitar inventario mientras el producto esté habilitado")
        des = InventarioRespuestaSchema.from_orm(des)
        return respuestaApi(success=True, message="Inventario deshabilitado", data=des)
