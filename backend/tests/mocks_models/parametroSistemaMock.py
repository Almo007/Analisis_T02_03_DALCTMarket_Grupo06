"""Mock directo para la entidad ParametroSistema."""

from unittest.mock import MagicMock

from app.ParametrosSistema.models.parametroSistemaModel import ParametroSistema


def crearParametroSistemaMock(
    idParametroSistema: int = 1,
    claveParametro: str = "CLAVE",
    valorParametro: str = "VALOR",
    activoParametro: bool = True,
):
    parametroMock = MagicMock(spec=ParametroSistema)
    parametroMock.idParametroSistema = idParametroSistema
    parametroMock.claveParametro = claveParametro
    parametroMock.valorParametro = valorParametro
    parametroMock.activoParametro = activoParametro
    return parametroMock
