"""Mock directo para la entidad Pedido."""

from unittest.mock import MagicMock

from app.Pedido.models.pedidoModel import Pedido


def crearPedidoMock(
    idPedido: int = 1,
    idUsuarioCreador: int = 1,
    idUsuarioAprobador=None,
    totalCostoPedido: float = 0.0,
    fechaCreacion=None,
    estadoPedido: str = "PENDIENTE_REVISION",
    observaciones=None,
    detalles=None,
    usuarioCreador=None,
    usuarioAprobador=None,
):
    pedidoMock = MagicMock(spec=Pedido)
    pedidoMock.idPedido = idPedido
    pedidoMock.idUsuarioCreador = idUsuarioCreador
    pedidoMock.idUsuarioAprobador = idUsuarioAprobador
    pedidoMock.totalCostoPedido = totalCostoPedido
    pedidoMock.fechaCreacion = fechaCreacion
    pedidoMock.estadoPedido = estadoPedido
    pedidoMock.observaciones = observaciones

    pedidoMock.detalles = detalles if detalles is not None else []
    pedidoMock.usuarioCreador = usuarioCreador
    pedidoMock.usuarioAprobador = usuarioAprobador

    return pedidoMock
