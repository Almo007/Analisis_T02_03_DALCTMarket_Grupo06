# Pruebas del controlador de ParametrosSistema (usando mocks)
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


def _encabezadosAuthAdmin():
    return {"Authorization": "Bearer tokenPrueba"}


def _tokenAdmin():
    # El middleware de permisos lee la clave "rol"
    return {"idUsuario": 1, "rol": "Administrador", "nombreCompleto": "Admin"}


def testListarParametrosDevuelveListaMockeada():
    """Prueba: GET /parametrosistema/ devuelve lista de parámetros (mockeado ParametroSistemaService)."""
    client = TestClient(app)

    parametrosIniciales = [
        {"idParametroSistema": 1, "claveParametro": "nombreNegocio", "valorParametro": "DALCT Market", "activoParametro": True},
        {"idParametroSistema": 2, "claveParametro": "direccionNegocio", "valorParametro": "Quito, Av. Morán Valverde y OE3H", "activoParametro": True},
        {"idParametroSistema": 3, "claveParametro": "telefonoNegocio", "valorParametro": "02-3450538", "activoParametro": True},
        {"idParametroSistema": 4, "claveParametro": "correoNegocio", "valorParametro": "contacto@dalctmarket.com", "activoParametro": True},
        {"idParametroSistema": 5, "claveParametro": "IVA", "valorParametro": "15", "activoParametro": True},
        {"idParametroSistema": 6, "claveParametro": "logoNegocio", "valorParametro": "/static/logo.png", "activoParametro": True},
    ]

    respuestaMock = respuestaApi(success=True, message="Parámetros encontrados", data=parametrosIniciales)

    with patch("app.ParametrosSistema.controllers.parametroSistemaController.ParametroSistemaService") as MockServicio, patch(
        "app.configuracionGeneral.seguridadJWT.verificarToken"
    ) as MockVerificarToken:
        MockServicio.return_value.listarParametros.return_value = respuestaMock
        MockVerificarToken.return_value = _tokenAdmin()

        respuesta = client.get("/parametrosistema/", headers=_encabezadosAuthAdmin())
        assert respuesta.status_code == 200
        cuerpo = respuesta.json()
        assert cuerpo["success"] is True
        assert isinstance(cuerpo["data"], list)
        assert len(cuerpo["data"]) == 6
        assert cuerpo["data"][0]["claveParametro"] == "nombreNegocio"


def testObtenerParametroPorIdDevuelveParametroMockeado():
    """Prueba: GET /parametrosistema/{id} devuelve un parámetro (mockeado ParametroSistemaService)."""
    client = TestClient(app)

    respuestaMock = respuestaApi(
        success=True,
        message="Parámetro encontrado",
        data={
            "idParametroSistema": 5,
            "claveParametro": "IVA",
            "valorParametro": "15",
            "activoParametro": True,
        },
    )

    with patch("app.ParametrosSistema.controllers.parametroSistemaController.ParametroSistemaService") as MockServicio, patch(
        "app.configuracionGeneral.seguridadJWT.verificarToken"
    ) as MockVerificarToken:
        MockServicio.return_value.obtenerParametroPorId.return_value = respuestaMock
        MockVerificarToken.return_value = _tokenAdmin()

        respuesta = client.get("/parametrosistema/5", headers=_encabezadosAuthAdmin())
        assert respuesta.status_code == 200
        cuerpo = respuesta.json()
        assert cuerpo["success"] is True
        assert cuerpo["data"]["claveParametro"] == "IVA"
