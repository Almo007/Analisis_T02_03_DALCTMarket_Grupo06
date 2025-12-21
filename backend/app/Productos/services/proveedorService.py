from app.Productos.repositories.proveedorRepository import ProveedorRepository
from app.configuracionGeneral.schemasGenerales import respuestaApi
from fastapi import HTTPException
from app.Productos.schemas.proveedorSchemas import *

class ProveedorService:
    def __init__(self, dbSession):
        self.dbSession = dbSession
        self.proveedorRepository = ProveedorRepository(dbSession)

    def listarProveedores(self):
        proveedores = self.proveedorRepository.listarProveedores()
        if proveedores is None:
            return respuestaApi(success=True, message="No se encontraron proveedores", data=[])
        proveedores = [ProveedorRespuestaSchema.from_orm(p) for p in proveedores]
        return respuestaApi(success=True, message="Proveedores encontrados", data=proveedores)

    def obtenerPorId(self, idProveedor: int):
        proveedor = self.proveedorRepository.obtenerPorId(idProveedor)
        if proveedor is None:
            raise HTTPException(status_code=404, detail="Proveedor no encontrado")
        proveedor = ProveedorRespuestaSchema.from_orm(proveedor)
        return respuestaApi(success=True, message="Proveedor encontrado", data=proveedor)

    def crearProveedor(self, proveedor: ProveedorCrearSchema):
        creado = self.proveedorRepository.crearProveedor(proveedor)
        if creado is None:
            raise HTTPException(status_code=400, detail="El RUC ya está registrado")
        creado = ProveedorRespuestaSchema.from_orm(creado)
        return respuestaApi(success=True, message="Proveedor creado", data=creado)

    def modificarProveedor(self, idProveedor: int, proveedor: ProveedorActualizarSchema):
        actualizado = self.proveedorRepository.modificarProveedor(idProveedor, proveedor)
        if actualizado is None:
            raise HTTPException(status_code=404, detail="Proveedor no encontrado")
        actualizado = ProveedorRespuestaSchema.from_orm(actualizado)
        return respuestaApi(success=True, message="Proveedor actualizado", data=actualizado)

    def deshabilitarProveedor(self, idProveedor: int):
        des = self.proveedorRepository.deshabilitarProveedor(idProveedor)
        if des is None:
            raise HTTPException(status_code=404, detail="Proveedor no encontrado")
        if des is False:
            raise HTTPException(status_code=400, detail="No se puede deshabilitar el proveedor: existen productos activos asociados")
        des = ProveedorRespuestaSchema.from_orm(des)
        return respuestaApi(success=True, message="Proveedor deshabilitado", data=des)