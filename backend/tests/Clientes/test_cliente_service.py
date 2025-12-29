import pytest
from unittest.mock import patch
from fastapi import HTTPException

from app.Clientes.services.clienteService import ClienteService
from app.Clientes.schemas.clienteSchemas import ClienteCrearSchema, ClienteActualizarSchema

from tests.mocks_models.clienteMock import crearClienteMock


def _clienteEjemploMock(
    idCliente: int = 1,
    nombreCliente: str = "María Gómez",
    cedulaCliente: str = "1712345678",
    telefonoCliente: str = "0998765432",
    direccionCliente: str = "Calle La Pradera N56-78, Quito, Ecuador",
    emailCliente: str = "maria.gomez@example.com",
    activoCliente: bool = True,
):
    return crearClienteMock(
        idCliente=idCliente,
        nombreCliente=nombreCliente,
        cedulaCliente=cedulaCliente,
        telefonoCliente=telefonoCliente,
        direccionCliente=direccionCliente,
        emailCliente=emailCliente,
        activoCliente=activoCliente,
    )


def testListarClientesDevuelveListaVaciaSiNoHayDatos():
    """Prueba: listarClientes devuelve data=[] si no existen clientes (repositorio retorna None)."""
    with patch("app.Clientes.services.clienteService.ClienteRepository") as MockRepo:
        MockRepo.return_value.listarClientes.return_value = None

        servicio = ClienteService(dbSession=None)
        respuesta = servicio.listarClientes()

        assert respuesta.success is True
        assert respuesta.data == []


def testListarClientesDevuelveListaDeClientes():
    """Prueba: listarClientes devuelve lista de clientes (from_orm) usando ejemplos iniciales."""
    cliente1Mock = _clienteEjemploMock(idCliente=1, nombreCliente="María Gómez", cedulaCliente="1712345678")
    cliente2Mock = _clienteEjemploMock(idCliente=6, nombreCliente="Consumidor Final", cedulaCliente="9999999999", telefonoCliente="0000000000", direccionCliente="No especifica", emailCliente="consumidor.final@ejemplo.com")

    with patch("app.Clientes.services.clienteService.ClienteRepository") as MockRepo:
        MockRepo.return_value.listarClientes.return_value = [cliente1Mock, cliente2Mock]

        servicio = ClienteService(dbSession=None)
        respuesta = servicio.listarClientes()

        assert respuesta.success is True
        assert isinstance(respuesta.data, list)
        assert len(respuesta.data) == 2
        assert respuesta.data[0].cedulaCliente == "1712345678"
        assert respuesta.data[1].nombreCliente == "Consumidor Final"


def testObtenerClientePorIdNoEncontradoLanza404():
    """Prueba: obtenerPorId lanza 404 si el cliente no existe."""
    with patch("app.Clientes.services.clienteService.ClienteRepository") as MockRepo:
        MockRepo.return_value.obtenerPorId.return_value = None

        servicio = ClienteService(dbSession=None)
        with pytest.raises(HTTPException) as excinfo:
            servicio.obtenerPorId(999)
        assert excinfo.value.status_code == 404
        assert excinfo.value.detail == "Cliente no encontrado"


def testObtenerClientePorIdExitoso():
    """Prueba: obtenerPorId retorna cliente si existe (from_orm)."""
    clienteMock = _clienteEjemploMock(idCliente=2, nombreCliente="Luis Torres", cedulaCliente="1721122233", telefonoCliente="0981122334", direccionCliente="Av. 10 de Agosto N23-45, Quito, Ecuador", emailCliente="luis.torres@example.com")

    with patch("app.Clientes.services.clienteService.ClienteRepository") as MockRepo:
        MockRepo.return_value.obtenerPorId.return_value = clienteMock

        servicio = ClienteService(dbSession=None)
        respuesta = servicio.obtenerPorId(2)

        assert respuesta.success is True
        assert respuesta.message == "Cliente encontrado"
        assert respuesta.data.idCliente == 2
        assert respuesta.data.cedulaCliente == "1721122233"


def testCrearClienteExitosoDevuelveClienteCreado():
    """Prueba: crearCliente retorna 'Cliente creado' cuando repo devuelve cliente."""
    clienteCreadoMock = _clienteEjemploMock(idCliente=1, nombreCliente="María Gómez", cedulaCliente="1712345678")

    with patch("app.Clientes.services.clienteService.ClienteRepository") as MockRepo:
        MockRepo.return_value.crearCliente.return_value = clienteCreadoMock

        servicio = ClienteService(dbSession=None)
        clienteCrear = ClienteCrearSchema(
            nombreCliente="María Gómez",
            cedulaCliente="1712345678",
            telefonoCliente="0998765432",
            direccionCliente="Calle La Pradera N56-78, Quito, Ecuador",
            emailCliente="maria.gomez@example.com",
        )

        respuesta = servicio.crearCliente(clienteCrear)
        assert respuesta.success is True
        assert respuesta.message == "Cliente creado"
        assert respuesta.data.cedulaCliente == "1712345678"


def testCrearClienteCedulaDuplicadaLanza400():
    """Prueba: crearCliente lanza 400 si la cédula ya está registrada (repo retorna None)."""
    with patch("app.Clientes.services.clienteService.ClienteRepository") as MockRepo:
        MockRepo.return_value.crearCliente.return_value = None

        servicio = ClienteService(dbSession=None)
        clienteCrear = ClienteCrearSchema(
            nombreCliente="María Gómez",
            cedulaCliente="1712345678",
            telefonoCliente="0998765432",
            direccionCliente="Calle La Pradera N56-78, Quito, Ecuador",
            emailCliente="maria.gomez@example.com",
        )

        with pytest.raises(HTTPException) as excinfo:
            servicio.crearCliente(clienteCrear)
        assert excinfo.value.status_code == 400
        assert excinfo.value.detail == "La cédula ya está registrada"


def testModificarClienteNoEncontradoLanza404():
    """Prueba: modificarCliente lanza 404 si no existe el cliente."""
    with patch("app.Clientes.services.clienteService.ClienteRepository") as MockRepo:
        MockRepo.return_value.modificarCliente.return_value = None

        servicio = ClienteService(dbSession=None)
        clienteActualizar = ClienteActualizarSchema(nombreCliente="Ana Morales")

        with pytest.raises(HTTPException) as excinfo:
            servicio.modificarCliente(999, clienteActualizar)
        assert excinfo.value.status_code == 404


def testModificarClienteExitosoDevuelveActualizado():
    """Prueba: modificarCliente retorna 'Cliente actualizado' cuando repo devuelve cliente actualizado."""
    clienteActualizadoMock = _clienteEjemploMock(idCliente=1, telefonoCliente="0990000000")

    with patch("app.Clientes.services.clienteService.ClienteRepository") as MockRepo:
        MockRepo.return_value.modificarCliente.return_value = clienteActualizadoMock

        servicio = ClienteService(dbSession=None)
        clienteActualizar = ClienteActualizarSchema(telefonoCliente="0990000000")

        respuesta = servicio.modificarCliente(1, clienteActualizar)
        assert respuesta.success is True
        assert respuesta.message == "Cliente actualizado"
        assert respuesta.data.telefonoCliente == "0990000000"


def testDeshabilitarClienteNoEncontradoLanza404():
    """Prueba: deshabilitarCliente lanza 404 si el cliente no existe."""
    with patch("app.Clientes.services.clienteService.ClienteRepository") as MockRepo:
        MockRepo.return_value.deshabilitarCliente.return_value = None

        servicio = ClienteService(dbSession=None)
        with pytest.raises(HTTPException) as excinfo:
            servicio.deshabilitarCliente(999)
        assert excinfo.value.status_code == 404


def testDeshabilitarClienteExitosoDevuelveClienteDeshabilitado():
    """Prueba: deshabilitarCliente retorna cliente con activoCliente=False (from_orm)."""
    clienteDeshabilitadoMock = _clienteEjemploMock(idCliente=1, activoCliente=False)

    with patch("app.Clientes.services.clienteService.ClienteRepository") as MockRepo:
        MockRepo.return_value.deshabilitarCliente.return_value = clienteDeshabilitadoMock

        servicio = ClienteService(dbSession=None)
        respuesta = servicio.deshabilitarCliente(1)

        assert respuesta.success is True
        assert respuesta.message == "Cliente deshabilitado"
        assert respuesta.data.activoCliente is False
