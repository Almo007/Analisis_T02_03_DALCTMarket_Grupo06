# Pruebas del servicio de Usuarios (usando mocks)
import pytest
from unittest.mock import patch
from fastapi import HTTPException
from app.Usuarios.services.usuarioService import UsuarioService
from app.Usuarios.schemas.usuarioSchemas import UsuarioCrearSchema, UsuarioActualizarSchema
from tests.mocks_models.rolMock import crearRolMock
from tests.mocks_models.usuarioMock import crearUsuarioMock

def testValidarCredencialesYListarUsuariosMockeados():
    """Prueba: validarCredenciales retorna datos de usuario y listarUsuarios devuelve lista (mockeado)"""
    # Arrange: rol Administrador (idRol=1) y usuario activo
    rolAdministradorMock = crearRolMock(idRol=1, nombreRol="Administrador")
    usuarioModelo = crearUsuarioMock(
        idUsuario=1,
        idRol=1,
        nombreCompleto="Administrador",
        cedulaUsuario="admin",
        emailUsuario="admin@example.com",
        passwordUsuario="1234",
        activoUsuario=True,
        rol=rolAdministradorMock,
    )

    with patch('app.Usuarios.services.usuarioService.UsuarioRepository') as MockRepo:
        instanciaRepo = MockRepo.return_value
        instanciaRepo.validarCredenciales.return_value = usuarioModelo
        instanciaRepo.listarUsuarios.return_value = [usuarioModelo]

        servicio = UsuarioService(dbSession=None)

        # Validar credenciales
        usuarioDatos = servicio.validarCredenciales('admin', '1234')
        assert isinstance(usuarioDatos, dict)
        assert usuarioDatos['cedula'] == 'admin'
        assert 'idUsuario' in usuarioDatos

        # Listar usuarios
        respuestaListar = servicio.listarUsuarios()
        assert respuestaListar.success is True
        assert isinstance(respuestaListar.data, list)


def testCrudUsuarioServicioMockeado():
    """Prueba: crear, obtener, modificar y deshabilitar un usuario mediante el servicio (mockeado)"""
    # Arrange: rol Cajero (idRol=3)
    rolCajeroMock = crearRolMock(idRol=3, nombreRol="Cajero")
    usuarioNuevoModelo = crearUsuarioMock(
        idUsuario=50,
        idRol=3,
        nombreCompleto="Usuario Prueba",
        cedulaUsuario="9999999999",
        emailUsuario="prueba@example.com",
        passwordUsuario="Prueba123",
        activoUsuario=True,
        rol=rolCajeroMock,
    )
    usuarioModificadoModelo = crearUsuarioMock(
        idUsuario=50,
        idRol=3,
        nombreCompleto="Usuario Prueba Modificado",
        cedulaUsuario="9999999999",
        emailUsuario="prueba@example.com",
        passwordUsuario="Prueba123",
        activoUsuario=True,
        rol=rolCajeroMock,
    )
    usuarioDeshabilitadoModelo = crearUsuarioMock(
        idUsuario=50,
        idRol=3,
        nombreCompleto="Usuario Prueba Modificado",
        cedulaUsuario="9999999999",
        emailUsuario="prueba@example.com",
        passwordUsuario="Prueba123",
        activoUsuario=False,
        rol=rolCajeroMock,
    )

    with patch('app.Usuarios.services.usuarioService.UsuarioRepository') as MockRepo:
        instanciaRepo = MockRepo.return_value
        instanciaRepo.crearUsuario.return_value = usuarioNuevoModelo
        instanciaRepo.obtenerUsuarioPorId.return_value = usuarioNuevoModelo
        instanciaRepo.modificarUsuario.return_value = usuarioModificadoModelo
        instanciaRepo.deshabilitarUsuario.return_value = usuarioDeshabilitadoModelo

        servicio = UsuarioService(dbSession=None)

        # Crear
        usuarioCrear = UsuarioCrearSchema(
            nombreCompleto='Usuario Prueba',
            cedulaUsuario='9999999999',
            emailUsuario='prueba@example.com',
            passwordUsuario='Prueba123',
            idRol=3
        )
        respuestaCrear = servicio.crearUsuario(usuarioCrear)
        assert respuestaCrear.success is True
        usuarioCreado = respuestaCrear.data
        assert usuarioCreado.idUsuario == 50

        # Obtener por id
        respuestaObtener = servicio.obtenerPorId(50)
        assert respuestaObtener.success is True
        usuarioObtenido = respuestaObtener.data
        assert usuarioObtenido.idUsuario == 50

        # Modificar
        usuarioActualizar = UsuarioActualizarSchema(nombreCompleto='Usuario Prueba Modificado')
        respuestaModificar = servicio.modificarUsuario(50, usuarioActualizar)
        assert respuestaModificar.success is True
        usuarioModificado = respuestaModificar.data
        assert usuarioModificado.nombreCompleto == 'Usuario Prueba Modificado'

        # Deshabilitar
        respuestaDeshabilitar = servicio.deshabilitarUsuario(50)
        assert respuestaDeshabilitar.success is True
        usuarioDeshabilitado = respuestaDeshabilitar.data
        assert usuarioDeshabilitado.activoUsuario is False


def testCrearUsuarioMockeadoExitoso():
    """Prueba: crear un usuario nuevo debe ser exitoso (mockeado) y devuelve id real mockeado"""

    with patch('app.Usuarios.services.usuarioService.UsuarioRepository') as MockRepo:
        instanciaRepo = MockRepo.return_value
        rolCajeroMock = crearRolMock(idRol=3, nombreRol="Cajero")
        nuevoModelo = crearUsuarioMock(
            idUsuario=100,
            idRol=3,
            nombreCompleto="Usuario Nuevo",
            cedulaUsuario="1000000000",
            emailUsuario="nuevo@example.com",
            passwordUsuario="Nueva123",
            activoUsuario=True,
            rol=rolCajeroMock,
        )
        instanciaRepo.crearUsuario.return_value = nuevoModelo

        servicio = UsuarioService(dbSession=None)

        usuarioCrear = UsuarioCrearSchema(
            nombreCompleto='Usuario Nuevo',
            cedulaUsuario='1000000000',
            emailUsuario='nuevo@example.com',
            passwordUsuario='Nueva123',
            idRol=3
        )

        respuestaCrear = servicio.crearUsuario(usuarioCrear)
        assert respuestaCrear.success is True
        usuarioCreado = respuestaCrear.data
        assert usuarioCreado.idUsuario == 100


def testCrearUsuarioDuplicadoLanzaErrorMockeado():
    """Prueba: crear usuario con cédula duplicada lanza HTTPException 400"""
    with patch('app.Usuarios.services.usuarioService.UsuarioRepository') as MockRepo:
        instanciaRepo = MockRepo.return_value
        instanciaRepo.crearUsuario.return_value = None  # simula cédula duplicada

        servicio = UsuarioService(dbSession=None)

        usuarioCrear = UsuarioCrearSchema(
            nombreCompleto='Usuario Duplicado',
            cedulaUsuario='1000000000',
            emailUsuario='dup@example.com',
            passwordUsuario='Dup12345',
            idRol=3
        )

        with pytest.raises(HTTPException) as excinfo:
            servicio.crearUsuario(usuarioCrear)
        assert excinfo.value.status_code == 400


def testObtenerPorIdNoEncontradoMockeado():
    """Prueba: obtenerPorId con id inexistente lanza HTTPException 404"""
    with patch('app.Usuarios.services.usuarioService.UsuarioRepository') as MockRepo:
        instanciaRepo = MockRepo.return_value
        instanciaRepo.obtenerUsuarioPorId.return_value = None

        servicio = UsuarioService(dbSession=None)

        with pytest.raises(HTTPException) as excinfo:
            servicio.obtenerPorId(9999)
        assert excinfo.value.status_code == 404


def testModificarUsuarioNoEncontradoMockeado():
    """Prueba: modificarUsuario con id inexistente lanza HTTPException 404"""
    with patch('app.Usuarios.services.usuarioService.UsuarioRepository') as MockRepo:
        instanciaRepo = MockRepo.return_value
        instanciaRepo.modificarUsuario.return_value = None

        servicio = UsuarioService(dbSession=None)

        usuarioActualizar = UsuarioActualizarSchema(nombreCompleto='No existe')
        with pytest.raises(HTTPException) as excinfo:
            servicio.modificarUsuario(9999, usuarioActualizar)
        assert excinfo.value.status_code == 404


def testDeshabilitarUsuarioNoEncontradoMockeado():
    """Prueba: deshabilitarUsuario con id inexistente lanza HTTPException 404"""
    with patch('app.Usuarios.services.usuarioService.UsuarioRepository') as MockRepo:
        instanciaRepo = MockRepo.return_value
        instanciaRepo.deshabilitarUsuario.return_value = None

        servicio = UsuarioService(dbSession=None)

        with pytest.raises(HTTPException) as excinfo:
            servicio.deshabilitarUsuario(9999)
        assert excinfo.value.status_code == 404


def testValidarCredencialesIncorrectasMockeado():
    """Prueba: validarCredenciales con credenciales incorrectas lanza HTTPException 401"""
    with patch('app.Usuarios.services.usuarioService.UsuarioRepository') as MockRepo:
        instanciaRepo = MockRepo.return_value
        instanciaRepo.validarCredenciales.return_value = None

        servicio = UsuarioService(dbSession=None)

        with pytest.raises(HTTPException) as excinfo:
            servicio.validarCredenciales('noexiste', 'wrong')
        assert excinfo.value.status_code == 401


def testValidarCredencialesUsuarioDeshabilitadoMockeado():
    """Prueba: validarCredenciales para usuario deshabilitado lanza HTTPException 403"""
    rolCajeroMock = crearRolMock(idRol=3, nombreRol="Cajero")
    usuarioDeshabilitadoModelo = crearUsuarioMock(
        idUsuario=3,
        idRol=3,
        nombreCompleto="Deshabilitado",
        cedulaUsuario="desh",
        emailUsuario="desh@example.com",
        passwordUsuario="1234",
        activoUsuario=False,
        rol=rolCajeroMock,
    )

    with patch('app.Usuarios.services.usuarioService.UsuarioRepository') as MockRepo:
        instanciaRepo = MockRepo.return_value
        instanciaRepo.validarCredenciales.return_value = usuarioDeshabilitadoModelo

        servicio = UsuarioService(dbSession=None)

        with pytest.raises(HTTPException) as excinfo:
            servicio.validarCredenciales('desh', '1234')
        assert excinfo.value.status_code == 403


def testListarUsuariosSinDatosDevuelveListaVaciaYMensaje():
    """Prueba: listarUsuarios devuelve data=[] cuando no hay usuarios (lista vacía)."""
    with patch('app.Usuarios.services.usuarioService.UsuarioRepository') as MockRepo:
        instanciaRepo = MockRepo.return_value
        instanciaRepo.listarUsuarios.return_value = []

        servicio = UsuarioService(dbSession=None)
        respuesta = servicio.listarUsuarios()

        assert respuesta.success is True
        assert respuesta.message == "Usuarios encontrados"
        assert respuesta.data == []


def testListarUsuariosRepoNoneDevuelveListaVaciaYMensajeNoEncontrados():
    """Prueba: listarUsuarios devuelve mensaje 'No se encontraron usuarios' cuando el repo retorna None."""
    with patch('app.Usuarios.services.usuarioService.UsuarioRepository') as MockRepo:
        instanciaRepo = MockRepo.return_value
        instanciaRepo.listarUsuarios.return_value = None

        servicio = UsuarioService(dbSession=None)
        respuesta = servicio.listarUsuarios()

        assert respuesta.success is True
        assert respuesta.message == "No se encontraron usuarios"
        assert respuesta.data == []


