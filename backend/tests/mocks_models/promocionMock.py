"""Mock directo para la entidad Promocion."""

from unittest.mock import MagicMock

from app.Venta.models.promocionModel import Promocion


def crearPromocionMock(
    idPromocion: int = 1,
    idProducto: int = 1,
    nombrePromocion: str = "Promo",
    porcentajePromocion: float = 0.0,
    fechaInicioPromocion=None,
    fechaFinPromocion=None,
    activoPromocion: bool = True,
    producto=None,
    detallesVenta=None,
):
    promocionMock = MagicMock(spec=Promocion)
    promocionMock.idPromocion = idPromocion
    promocionMock.idProducto = idProducto
    promocionMock.nombrePromocion = nombrePromocion
    promocionMock.porcentajePromocion = porcentajePromocion
    promocionMock.fechaInicioPromocion = fechaInicioPromocion
    promocionMock.fechaFinPromocion = fechaFinPromocion
    promocionMock.activoPromocion = activoPromocion

    promocionMock.producto = producto
    promocionMock.detallesVenta = detallesVenta if detallesVenta is not None else []

    return promocionMock
