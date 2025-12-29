"""Mock directo para la entidad Rol."""

from unittest.mock import MagicMock

from app.Usuarios.models.rolModel import Rol


def crearRolMock(idRol: int = 1, nombreRol: str = "Administrador"):
    # Crea un mock con spec del modelo real
    rolMock = MagicMock(spec=Rol)
    rolMock.idRol = idRol
    rolMock.nombreRol = nombreRol
    return rolMock
