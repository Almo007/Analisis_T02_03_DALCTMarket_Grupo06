"""Mock directo para la entidad Cliente."""

from unittest.mock import MagicMock

from app.Clientes.modells.clienteModel import Cliente


def crearClienteMock(
    idCliente: int = 1,
    nombreCliente: str = "Cliente",
    cedulaCliente: str = "0100000000",
    telefonoCliente: str = "0999999999",
    direccionCliente: str = "Dirección",
    emailCliente: str = "cliente@example.com",
    activoCliente: bool = True,
    ventas=None,
):
    clienteMock = MagicMock(spec=Cliente)
    clienteMock.idCliente = idCliente
    clienteMock.nombreCliente = nombreCliente
    clienteMock.cedulaCliente = cedulaCliente
    clienteMock.telefonoCliente = telefonoCliente
    clienteMock.direccionCliente = direccionCliente
    clienteMock.emailCliente = emailCliente
    clienteMock.activoCliente = activoCliente
    clienteMock.ventas = ventas if ventas is not None else []
    return clienteMock
