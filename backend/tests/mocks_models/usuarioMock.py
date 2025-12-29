"""Mock directo para la entidad Usuario."""

from unittest.mock import MagicMock

from app.Usuarios.models.usuarioModel import Usuario


def crearUsuarioMock(
    idUsuario: int = 1,
    idRol: int = 1,
    nombreCompleto: str = "admin",
    cedulaUsuario: str = "admin",
    emailUsuario: str = "admin@example.com",
    passwordUsuario: str = "1234",
    activoUsuario: bool = True,
    rol=None,
    ventas=None,
    cajas=None,
    pedidosCreados=None,
    pedidosAprobados=None,
):
    # Crea un mock con spec del modelo real
    usuarioMock = MagicMock(spec=Usuario)
    usuarioMock.idUsuario = idUsuario
    usuarioMock.idRol = idRol
    usuarioMock.nombreCompleto = nombreCompleto
    usuarioMock.cedulaUsuario = cedulaUsuario
    usuarioMock.emailUsuario = emailUsuario
    usuarioMock.passwordUsuario = passwordUsuario
    usuarioMock.activoUsuario = activoUsuario

    # Relaciones (listas simuladas)
    usuarioMock.rol = rol
    usuarioMock.ventas = ventas if ventas is not None else []
    usuarioMock.cajas = cajas if cajas is not None else []
    usuarioMock.pedidosCreados = pedidosCreados if pedidosCreados is not None else []
    usuarioMock.pedidosAprobados = pedidosAprobados if pedidosAprobados is not None else []

    return usuarioMock
