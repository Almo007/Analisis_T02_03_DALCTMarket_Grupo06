# Pruebas del controlador de Clientes (usando mocks)
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
    # Base de usuarios del proyecto
    return {"idUsuario": 1, "rol": "Administrador", "nombreCompleto": "admin"}


def testListarClientesDevuelveListaMockeada():
    """Prueba: GET /clientes/ devuelve lista de clientes (mockeado ClienteService)."""
    client = TestClient(app)

    clientes = [
        {
            "idCliente": 1,
            "nombreCliente": "María Gómez",
            "cedulaCliente": "1712345678",
            "telefonoCliente": "0998765432",
            "direccionCliente": "Calle La Pradera N56-78, Quito, Ecuador",
            "emailCliente": "maria.gomez@example.com",
            "activoCliente": True,
        },
        {
            "idCliente": 2,
            "nombreCliente": "Consumidor Final",
            "cedulaCliente": "9999999999",
            "telefonoCliente": "0000000000",
            "direccionCliente": "No especifica",
            "emailCliente": "consumidor.final@ejemplo.com",
            "activoCliente": True,
        },
    ]

    respuestaMock = respuestaApi(success=True, message="Clientes encontrados", data=clientes)

    with patch("app.Clientes.controllers.clienteController.ClienteService") as MockServicio, patch(
        "app.configuracionGeneral.seguridadJWT.verificarToken"
    ) as MockVerificarToken:
        MockServicio.return_value.listarClientes.return_value = respuestaMock
        MockVerificarToken.return_value = _tokenAdmin()

        respuesta = client.get("/clientes/", headers=_encabezadosAuthAdmin())
        assert respuesta.status_code == 200
        cuerpo = respuesta.json()
        assert cuerpo["success"] is True
        assert isinstance(cuerpo["data"], list)
        assert len(cuerpo["data"]) == 2
        assert cuerpo["data"][0]["cedulaCliente"] == "1712345678"


def testCrearClienteDevuelveCreadoMockeado():
    """Prueba: POST /clientes/ crea un cliente (mockeado ClienteService)."""
    client = TestClient(app)

    cuerpoCrear = {
        "nombreCliente": "María Gómez",
        "cedulaCliente": "1712345678",
        "telefonoCliente": "0998765432",
        "direccionCliente": "Calle La Pradera N56-78, Quito, Ecuador",
        "emailCliente": "maria.gomez@example.com",
    }

    respuestaMock = respuestaApi(
        success=True,
        message="Cliente creado",
        data={
            "idCliente": 1,
            **cuerpoCrear,
            "activoCliente": True,
        },
    )

    with patch("app.Clientes.controllers.clienteController.ClienteService") as MockServicio, patch(
        "app.configuracionGeneral.seguridadJWT.verificarToken"
    ) as MockVerificarToken:
        MockServicio.return_value.crearCliente.return_value = respuestaMock
        MockVerificarToken.return_value = _tokenAdmin()

        respuesta = client.post("/clientes/", json=cuerpoCrear, headers=_encabezadosAuthAdmin())
        assert respuesta.status_code == 201
        cuerpo = respuesta.json()
        assert cuerpo["success"] is True
        assert cuerpo["message"] == "Cliente creado"
        assert cuerpo["data"]["cedulaCliente"] == "1712345678"
