"""Mock directo para la entidad Venta."""

from unittest.mock import MagicMock

from app.Venta.models.ventaModel import Venta


def crearVentaMock(
    idVenta: int = 1,
    idCaja: int = 1,
    idUsuarioVenta: int = 1,
    idCliente: int = 1,
    fechaVenta=None,
    subtotalVenta: float = 0.0,
    descuentoGeneral: float = 0.0,
    totalDescuento: float = 0.0,
    baseIVA: float = 0.0,
    totalIVA: float = 0.0,
    totalPagar: float = 0.0,
    metodoPago: str = "Efectivo",
    estadoVenta: str = "COMPLETADA",
    usuario=None,
    cliente=None,
    detalles=None,
):
    ventaMock = MagicMock(spec=Venta)
    ventaMock.idVenta = idVenta
    ventaMock.idCaja = idCaja
    ventaMock.idUsuarioVenta = idUsuarioVenta
    ventaMock.idCliente = idCliente
    ventaMock.fechaVenta = fechaVenta
    ventaMock.subtotalVenta = subtotalVenta
    ventaMock.descuentoGeneral = descuentoGeneral
    ventaMock.totalDescuento = totalDescuento
    ventaMock.baseIVA = baseIVA
    ventaMock.totalIVA = totalIVA
    ventaMock.totalPagar = totalPagar
    ventaMock.metodoPago = metodoPago
    ventaMock.estadoVenta = estadoVenta

    ventaMock.usuario = usuario
    ventaMock.cliente = cliente
    ventaMock.detalles = detalles if detalles is not None else []

    return ventaMock
