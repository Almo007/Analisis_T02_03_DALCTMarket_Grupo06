"""Mock directo para la entidad Producto."""

from unittest.mock import MagicMock

from app.Productos.models.productoModel import Producto


def crearProductoMock(
    idProducto: int = 1,
    idCategoriaProducto: int = 1,
    idProveedor: int = 1,
    nombreProducto: str = "Producto",
    descripcionProducto=None,
    precioUnitarioVenta: float = 1.0,
    precioUnitarioCompra: float = 1.0,
    tieneIva: bool = True,
    activoProducto: bool = True,
    categoria=None,
    proveedor=None,
    inventario=None,
    detallesPedido=None,
    promociones=None,
    detallesVenta=None,
):
    productoMock = MagicMock(spec=Producto)
    productoMock.idProducto = idProducto
    productoMock.idCategoriaProducto = idCategoriaProducto
    productoMock.idProveedor = idProveedor
    productoMock.nombreProducto = nombreProducto
    productoMock.descripcionProducto = descripcionProducto
    productoMock.precioUnitarioVenta = precioUnitarioVenta
    productoMock.precioUnitarioCompra = precioUnitarioCompra
    productoMock.tieneIva = tieneIva
    productoMock.activoProducto = activoProducto

    productoMock.categoria = categoria
    productoMock.proveedor = proveedor
    productoMock.inventario = inventario
    productoMock.detallesPedido = detallesPedido if detallesPedido is not None else []
    productoMock.promociones = promociones if promociones is not None else []
    productoMock.detallesVenta = detallesVenta if detallesVenta is not None else []

    return productoMock
