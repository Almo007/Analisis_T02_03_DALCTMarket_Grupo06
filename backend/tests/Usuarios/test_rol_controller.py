# Pruebas del controlador de Roles (usando mocks)

from fastapi.testclient import TestClient
from unittest.mock import patch

from app.database import obtenerSesion
from app.main import app
from app.configuracionGeneral.schemasGenerales import respuestaApi


# Usar la app real (app.main) pero sin disparar startup_event (evita BD)
app.router.on_startup.clear()
app.router.on_shutdown.clear()


def _mockObtenerSesion():
    # Evita crear sesión real de BD
    yield None


app.dependency_overrides[obtenerSesion] = _mockObtenerSesion


def testObtenerTodosLosRolesDevuelveListaMockeada():
    """Prueba: GET /roles/ devuelve lista de roles (mockeado RolService)."""
    client = TestClient(app)

    respuestaMock = respuestaApi(
        success=True,
        message="Roles encontrados",
        data=[
            {"idRol": 1, "nombreRol": "Administrador"},
            {"idRol": 2, "nombreRol": "Bodeguero"},
            {"idRol": 3, "nombreRol": "Cajero"},
        ],
    )

    with patch("app.Usuarios.controllers.rolController.RolService") as MockRolService:
        instanciaServicio = MockRolService.return_value
        instanciaServicio.obtenerTodos.return_value = respuestaMock

        respuesta = client.get("/roles/")
        assert respuesta.status_code == 200
        cuerpo = respuesta.json()
        assert cuerpo["success"] is True
        assert isinstance(cuerpo["data"], list)
        assert len(cuerpo["data"]) == 3


def testObtenerRolPorIdDevuelveRolMockeado():
    """Prueba: GET /roles/{idRol} devuelve un rol (mockeado RolService)."""
    client = TestClient(app)

    respuestaMock = respuestaApi(
        success=True,
        message="Rol encontrado",
        data={"idRol": 1, "nombreRol": "Administrador"},
    )

    with patch("app.Usuarios.controllers.rolController.RolService") as MockRolService:
        instanciaServicio = MockRolService.return_value
        instanciaServicio.obtenerPorId.return_value = respuestaMock

        respuesta = client.get("/roles/1")
        assert respuesta.status_code == 200
        cuerpo = respuesta.json()
        assert cuerpo["success"] is True
        assert cuerpo["data"]["idRol"] == 1
        assert cuerpo["data"]["nombreRol"] == "Administrador"
