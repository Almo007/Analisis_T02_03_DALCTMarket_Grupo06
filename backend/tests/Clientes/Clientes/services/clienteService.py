from app.Clientes.repositories.clienteRepository import ClienteRepository
from app.configuracionGeneral.schemasGenerales import respuestaApi
from fastapi import HTTPException
from app.Clientes.schemas.clienteSchemas import *

class ClienteService:
    def __init__(self, dbSession):
        self.dbSession = dbSession
        self.clienteRepository = ClienteRepository(dbSession)

    def listarClientes(self):
        clientes = self.clienteRepository.listarClientes()
        if clientes is None:
            return respuestaApi(success=True, message="No se encontraron clientes", data=[])
        clientes = [ClienteRespuestaSchema.from_orm(c) for c in clientes]
        return respuestaApi(success=True, message="Clientes encontrados", data=clientes)

    def obtenerPorId(self, idCliente: int):
        cliente = self.clienteRepository.obtenerPorId(idCliente)
        if not cliente:
            raise HTTPException(status_code=404, detail="Cliente no encontrado")
        cliente = ClienteRespuestaSchema.from_orm(cliente)
        return respuestaApi(success=True, message="Cliente encontrado", data=cliente)

    def crearCliente(self, cliente: ClienteCrearSchema):
        nuevo = self.clienteRepository.crearCliente(cliente)
        if nuevo is None:
            raise HTTPException(status_code=400, detail="La cédula ya está registrada")
        nuevo = ClienteRespuestaSchema.from_orm(nuevo)
        return respuestaApi(success=True, message="Cliente creado", data=nuevo)

    def modificarCliente(self, idCliente: int, cliente: ClienteActualizarSchema):
        actualizado = self.clienteRepository.modificarCliente(idCliente, cliente)
        if actualizado is None:
            raise HTTPException(status_code=404, detail="Cliente no encontrado")
        actualizado = ClienteRespuestaSchema.from_orm(actualizado)
        return respuestaApi(success=True, message="Cliente actualizado", data=actualizado)

    def deshabilitarCliente(self, idCliente: int):
        des = self.clienteRepository.deshabilitarCliente(idCliente)
        if des is None:
            raise HTTPException(status_code=404, detail="Cliente no encontrado")
        des = ClienteRespuestaSchema.from_orm(des)
        return respuestaApi(success=True, message="Cliente deshabilitado", data=des)
