"""Mock directo para la entidad DetalleVenta."""

from unittest.mock import MagicMock

from app.Venta.models.detalleVentaModel import DetalleVenta


def crearDetalleVentaMock(
    idDetalleVenta: int = 1,
    idVenta: int = 1,
    idProducto: int = 1,
    idPromocion=None,
    precioUnitarioVendido: float = 1.0,
    cantidadVendida: int = 1,
    subtotalProducto: float = 1.0,
    valorDescuentoProducto: float = 0.0,
    venta=None,
    producto=None,
    promocion=None,
):
    detalleMock = MagicMock(spec=DetalleVenta)
    detalleMock.idDetalleVenta = idDetalleVenta
    detalleMock.idVenta = idVenta
    detalleMock.idProducto = idProducto
    detalleMock.idPromocion = idPromocion
    detalleMock.precioUnitarioVendido = precioUnitarioVendido
    detalleMock.cantidadVendida = cantidadVendida
    detalleMock.subtotalProducto = subtotalProducto
    detalleMock.valorDescuentoProducto = valorDescuentoProducto

    detalleMock.venta = venta
    detalleMock.producto = producto
    detalleMock.promocion = promocion

    return detalleMock
