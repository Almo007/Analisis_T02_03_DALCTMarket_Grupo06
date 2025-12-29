# Pruebas del servicio de Roles (usando mocks)

import pytest
from unittest.mock import patch
from fastapi import HTTPException

from app.Usuarios.services.rolService import RolService
from tests.mocks_models.rolMock import crearRolMock


def testCrudCompletoRolServicioMockeado():
    """Prueba: flujo completo del servicio de roles (listar -> obtenerPorId -> obtenerPorNombre) (mockeado)."""
    # Arrange: roles por defecto del sistema
    rolAdministradorMock = crearRolMock(idRol=1, nombreRol="Administrador")
    rolBodegueroMock = crearRolMock(idRol=2, nombreRol="Bodeguero")
    rolCajeroMock = crearRolMock(idRol=3, nombreRol="Cajero")

    with patch("app.Usuarios.services.rolService.RolRepository") as MockRepo:
        instanciaRepo = MockRepo.return_value
        instanciaRepo.obtenerTodos.return_value = [rolAdministradorMock, rolBodegueroMock, rolCajeroMock]
        instanciaRepo.obtenerPorId.return_value = rolAdministradorMock
        instanciaRepo.obtenerPorNombre.return_value = rolCajeroMock

        servicio = RolService(dbSession=None)

        # Listar
        respuestaListar = servicio.obtenerTodos()
        assert respuestaListar.success is True
        assert isinstance(respuestaListar.data, list)
        assert len(respuestaListar.data) == 3
        assert {r.idRol for r in respuestaListar.data} == {1, 2, 3}

        # Obtener por id
        respuestaPorId = servicio.obtenerPorId(1)
        assert respuestaPorId.success is True
        assert respuestaPorId.data.idRol == 1
        assert respuestaPorId.data.nombreRol == "Administrador"

        # Obtener por nombre
        respuestaPorNombre = servicio.obtenerPorNombre("Cajero")
        assert respuestaPorNombre.success is True
        assert respuestaPorNombre.data.idRol == 3
        assert respuestaPorNombre.data.nombreRol == "Cajero"


def testObtenerTodosRolesDevuelveListaMockeada():
    """Prueba: obtenerTodos devuelve lista cuando hay roles (mockeado RolRepository)."""
    rolAdministradorMock = crearRolMock(idRol=1, nombreRol="Administrador")
    rolBodegueroMock = crearRolMock(idRol=2, nombreRol="Bodeguero")
    rolCajeroMock = crearRolMock(idRol=3, nombreRol="Cajero")

    with patch("app.Usuarios.services.rolService.RolRepository") as MockRepo:
        instanciaRepo = MockRepo.return_value
        instanciaRepo.obtenerTodos.return_value = [rolAdministradorMock, rolBodegueroMock, rolCajeroMock]

        servicio = RolService(dbSession=None)
        respuesta = servicio.obtenerTodos()

        assert respuesta.success is True
        assert isinstance(respuesta.data, list)
        assert len(respuesta.data) == 3
        assert respuesta.data[0].idRol == 1


def testObtenerTodosRolesSinDatosDevuelveListaVacia():
    """Prueba: obtenerTodos devuelve lista vacía cuando no hay roles (mockeado RolRepository)."""
    with patch("app.Usuarios.services.rolService.RolRepository") as MockRepo:
        instanciaRepo = MockRepo.return_value
        instanciaRepo.obtenerTodos.return_value = []

        servicio = RolService(dbSession=None)
        respuesta = servicio.obtenerTodos()

        assert respuesta.success is True
        assert respuesta.data == []


def testObtenerRolPorIdDevuelveRolMockeado():
    """Prueba: obtenerPorId devuelve rol cuando existe (mockeado RolRepository)."""
    rolAdministradorMock = crearRolMock(idRol=1, nombreRol="Administrador")

    with patch("app.Usuarios.services.rolService.RolRepository") as MockRepo:
        instanciaRepo = MockRepo.return_value
        instanciaRepo.obtenerPorId.return_value = rolAdministradorMock

        servicio = RolService(dbSession=None)
        respuesta = servicio.obtenerPorId(1)

        assert respuesta.success is True
        assert respuesta.data.idRol == 1
        assert respuesta.data.nombreRol == "Administrador"


def testObtenerRolPorIdNoEncontradoLanzaError():
    """Prueba: obtenerPorId lanza HTTPException 404 si no existe el rol."""
    with patch("app.Usuarios.services.rolService.RolRepository") as MockRepo:
        instanciaRepo = MockRepo.return_value
        instanciaRepo.obtenerPorId.return_value = None

        servicio = RolService(dbSession=None)

        with pytest.raises(HTTPException) as excinfo:
            servicio.obtenerPorId(999)
        assert excinfo.value.status_code == 404


def testObtenerRolPorNombreDevuelveRolMockeado():
    """Prueba: obtenerPorNombre devuelve rol cuando existe (mockeado RolRepository)."""
    rolCajeroMock = crearRolMock(idRol=3, nombreRol="Cajero")

    with patch("app.Usuarios.services.rolService.RolRepository") as MockRepo:
        instanciaRepo = MockRepo.return_value
        instanciaRepo.obtenerPorNombre.return_value = rolCajeroMock

        servicio = RolService(dbSession=None)
        respuesta = servicio.obtenerPorNombre("Cajero")

        assert respuesta.success is True
        assert respuesta.data.idRol == 3
        assert respuesta.data.nombreRol == "Cajero"


def testObtenerRolPorNombreNoEncontradoLanzaError():
    """Prueba: obtenerPorNombre lanza HTTPException 404 si no existe el rol."""
    with patch("app.Usuarios.services.rolService.RolRepository") as MockRepo:
        instanciaRepo = MockRepo.return_value
        instanciaRepo.obtenerPorNombre.return_value = None

        servicio = RolService(dbSession=None)

        with pytest.raises(HTTPException) as excinfo:
            servicio.obtenerPorNombre("NoExiste")
        assert excinfo.value.status_code == 404
