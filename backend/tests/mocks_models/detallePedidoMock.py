"""Mock directo para la entidad DetallePedido."""

from unittest.mock import MagicMock

from app.Pedido.models.detallePedidoModel import DetallePedido


def crearDetallePedidoMock(
    idDetallePedido: int = 1,
    idPedido: int = 1,
    idProducto: int = 1,
    idUsuarioReceptor=None,
    cantidadSolicitada: int = 1,
    precioUnitarioCompra: float = 1.0,
    estadoDetalle: str = "PENDIENTE_REVISION",
    fechaRecepcion=None,
    pedido=None,
    producto=None,
    usuarioReceptor=None,
):
    detalleMock = MagicMock(spec=DetallePedido)
    detalleMock.idDetallePedido = idDetallePedido
    detalleMock.idPedido = idPedido
    detalleMock.idProducto = idProducto
    detalleMock.idUsuarioReceptor = idUsuarioReceptor
    detalleMock.cantidadSolicitada = cantidadSolicitada
    detalleMock.precioUnitarioCompra = precioUnitarioCompra
    detalleMock.estadoDetalle = estadoDetalle
    detalleMock.fechaRecepcion = fechaRecepcion

    detalleMock.pedido = pedido
    detalleMock.producto = producto
    detalleMock.usuarioReceptor = usuarioReceptor

    return detalleMock
