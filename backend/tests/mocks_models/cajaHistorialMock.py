"""Mock directo para la entidad CajaHistorial."""

from unittest.mock import MagicMock

from app.Caja.models.cajaHistorialModel import CajaHistorial


def crearCajaHistorialMock(
    idCaja: int = 1,
    idUsuarioCaja: int = 1,
    fechaAperturaCaja=None,
    fechaCierreCaja=None,
    montoInicialDeclarado: float = 0.0,
    montoCierreDeclarado=None,
    montoCierreSistema=None,
    diferenciaCaja=None,
    estadoCaja: str = "ABIERTA",
    detalle=None,
    usuario=None,
):
    cajaMock = MagicMock(spec=CajaHistorial)
    cajaMock.idCaja = idCaja
    cajaMock.idUsuarioCaja = idUsuarioCaja
    cajaMock.fechaAperturaCaja = fechaAperturaCaja
    cajaMock.fechaCierreCaja = fechaCierreCaja
    cajaMock.montoInicialDeclarado = montoInicialDeclarado
    cajaMock.montoCierreDeclarado = montoCierreDeclarado
    cajaMock.montoCierreSistema = montoCierreSistema
    cajaMock.diferenciaCaja = diferenciaCaja
    cajaMock.estadoCaja = estadoCaja
    cajaMock.detalle = detalle
    cajaMock.usuario = usuario
    return cajaMock
