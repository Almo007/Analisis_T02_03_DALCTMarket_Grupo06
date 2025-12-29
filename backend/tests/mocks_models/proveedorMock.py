"""Mock directo para la entidad Proveedor."""

from unittest.mock import MagicMock

from app.Productos.models.proveedorModel import Proveedor


def crearProveedorMock(
    idProveedor: int = 1,
    razonSocial: str = "Proveedor",
    ruc: str = "0000000000001",
    direccionProveedor: str = "Dirección",
    telefonoProveedor: str = "0999999999",
    emailProveedor: str = "proveedor@example.com",
    activoProveedor: bool = True,
    productos=None,
):
    proveedorMock = MagicMock(spec=Proveedor)
    proveedorMock.idProveedor = idProveedor
    proveedorMock.razonSocial = razonSocial
    proveedorMock.ruc = ruc
    proveedorMock.direccionProveedor = direccionProveedor
    proveedorMock.telefonoProveedor = telefonoProveedor
    proveedorMock.emailProveedor = emailProveedor
    proveedorMock.activoProveedor = activoProveedor
    proveedorMock.productos = productos if productos is not None else []
    return proveedorMock
