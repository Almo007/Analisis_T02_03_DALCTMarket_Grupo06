"""Mock directo para la entidad Inventario."""

from unittest.mock import MagicMock

from app.Inventario.models.inventarioModel import Inventario


def crearInventarioMock(
    idInventario: int = 1,
    idProducto: int = 1,
    cantidadDisponible: int = 0,
    cantidadMinima: int = 0,
    activoInventario: bool = True,
    producto=None,
):
    inventarioMock = MagicMock(spec=Inventario)
    inventarioMock.idInventario = idInventario
    inventarioMock.idProducto = idProducto
    inventarioMock.cantidadDisponible = cantidadDisponible
    inventarioMock.cantidadMinima = cantidadMinima
    inventarioMock.activoInventario = activoInventario
    inventarioMock.producto = producto
    return inventarioMock
