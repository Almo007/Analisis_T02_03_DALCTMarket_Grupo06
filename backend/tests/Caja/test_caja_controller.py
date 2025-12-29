# Pruebas del controlador de Caja (usando mocks)
from datetime import datetime, timezone, timedelta

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


def _encabezadosAuth():
    return {"Authorization": "Bearer tokenPrueba"}


def _quitoTZ():
    return timezone(timedelta(hours=-5))


def _tokenAdmin():
    return {"idUsuario": 1, "rol": "Administrador", "nombreCompleto": "admin"}


def _tokenCajero():
    return {"idUsuario": 3, "rol": "Cajero", "nombreCompleto": "cajero"}


def testListarCajasHoyDevuelveListaMockeadaDinamicaQuito():
    """Prueba: GET /caja/listar devuelve cajas del día con fechas dinámicas en zona Quito."""
    client = TestClient(app)

    tzQuito = _quitoTZ()
    ahora = datetime.now(tzQuito).replace(microsecond=0)

    cajas = [
        {
            "idCaja": 1,
            "usuario": {
                "idUsuario": 1,
                "nombreCompleto": "admin",
                "cedulaUsuario": "admin",
                "emailUsuario": "admin@example.com",
                "rol": {"idRol": 1, "nombreRol": "Administrador"},
                "activoUsuario": True,
            },
            "fechaAperturaCaja": ahora - timedelta(hours=8),
            "fechaCierreCaja": ahora - timedelta(hours=6),
            "montoInicialDeclarado": 10.0,
            "montoCierreDeclarado": 14.0,
            "montoCierreSistema": 22.68,
            "diferenciaCaja": -8.68,
            "estadoCaja": "CERRADA",
            "detalle": "Cierre por 1-admin; montoFinalDeclarado: 14.0; montoCierreSistema: 22.68; montoInicialDeclarado: 10.0",
        },
        {
            "idCaja": 2,
            "usuario": {
                "idUsuario": 3,
                "nombreCompleto": "cajero",
                "cedulaUsuario": "cajero",
                "emailUsuario": "cajero@example.com",
                "rol": {"idRol": 3, "nombreRol": "Cajero"},
                "activoUsuario": True,
            },
            "fechaAperturaCaja": ahora - timedelta(hours=3),
            "fechaCierreCaja": ahora - timedelta(hours=2, minutes=30),
            "montoInicialDeclarado": 10.0,
            "montoCierreDeclarado": 15.3,
            "montoCierreSistema": 15.3,
            "diferenciaCaja": 0.0,
            "estadoCaja": "CERRADA",
            "detalle": "Cierre: cerrado por 3-cajero en la jornada correcta; montoFinalDeclarado: 15.3; montoCierreSistema: 15.3; montoInicialDeclarado: 10.0",
        },
        {
            "idCaja": 3,
            "usuario": {
                "idUsuario": 1,
                "nombreCompleto": "admin",
                "cedulaUsuario": "admin",
                "emailUsuario": "admin@example.com",
                "rol": {"idRol": 1, "nombreRol": "Administrador"},
                "activoUsuario": True,
            },
            "fechaAperturaCaja": ahora,
            "fechaCierreCaja": None,
            "montoInicialDeclarado": 95.0,
            "montoCierreDeclarado": None,
            "montoCierreSistema": None,
            "diferenciaCaja": None,
            "estadoCaja": "ABIERTA",
            "detalle": "Apertura por 1-admin; montoInicialDeclarado: 95.0",
        },
    ]

    respuestaMock = respuestaApi(success=True, message="Cajas del día encontradas", data=cajas)

    with patch("app.Caja.controllers.cajaController.CajaService") as MockServicio, patch(
        "app.configuracionGeneral.seguridadJWT.verificarToken"
    ) as MockVerificarToken:
        MockServicio.return_value.listarCajasHoy.return_value = respuestaMock
        MockVerificarToken.return_value = _tokenAdmin()

        respuesta = client.get("/caja/listar", headers=_encabezadosAuth())
        assert respuesta.status_code == 200
        cuerpo = respuesta.json()

        assert cuerpo["success"] is True
        assert isinstance(cuerpo["data"], list)
        assert len(cuerpo["data"]) == 3
        assert cuerpo["data"][2]["estadoCaja"] == "ABIERTA"
        # Validar que se serializa con offset de Quito (-05:00)
        assert "-05:00" in cuerpo["data"][0]["fechaAperturaCaja"]


def testAbrirCajaDevuelveCreadoMockeadoCajero():
    """Prueba: POST /caja/abrir abre una caja (mockeado CajaService) usando token de cajero."""
    client = TestClient(app)

    tzQuito = _quitoTZ()
    ahora = datetime.now(tzQuito).replace(microsecond=0)

    cuerpoCrear = {"montoInicial": 95.0}

    respuestaMock = respuestaApi(
        success=True,
        message="Caja abierta por 3-cajero (monto inicial: 95.0)",
        data={
            "idCaja": 3,
            "usuario": {
                "idUsuario": 3,
                "nombreCompleto": "cajero",
                "cedulaUsuario": "cajero",
                "emailUsuario": "cajero@example.com",
                "rol": {"idRol": 3, "nombreRol": "Cajero"},
                "activoUsuario": True,
            },
            "fechaAperturaCaja": ahora,
            "fechaCierreCaja": None,
            "montoInicialDeclarado": 95.0,
            "montoCierreDeclarado": None,
            "montoCierreSistema": None,
            "diferenciaCaja": None,
            "estadoCaja": "ABIERTA",
            "detalle": "Apertura por 3-cajero; montoInicialDeclarado: 95.0",
        },
    )

    with patch("app.Caja.controllers.cajaController.CajaService") as MockServicio, patch(
        "app.configuracionGeneral.seguridadJWT.verificarToken"
    ) as MockVerificarToken:
        MockServicio.return_value.crearCajaHistorial.return_value = respuestaMock
        MockVerificarToken.return_value = _tokenCajero()

        respuesta = client.post("/caja/abrir", json=cuerpoCrear, headers=_encabezadosAuth())
        assert respuesta.status_code == 201
        cuerpo = respuesta.json()

        assert cuerpo["success"] is True
        assert "Caja abierta" in cuerpo["message"]
        assert cuerpo["data"]["estadoCaja"] == "ABIERTA"
        assert "-05:00" in cuerpo["data"]["fechaAperturaCaja"]
