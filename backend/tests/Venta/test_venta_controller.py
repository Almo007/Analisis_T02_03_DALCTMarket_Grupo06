# Pruebas del controlador de Venta (usando mocks)
from datetime import datetime, timezone, timedelta, time

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


def testListarVentasHoyDevuelveListaMockeadaAdmin():
    """Prueba: GET /venta/ lista ventas de hoy (mockeado VentaService) con rol Administrador."""
    client = TestClient(app)

    tzQuito = _quitoTZ()
    hoy = datetime.now(tzQuito).date()
    horaActual = datetime.now(tzQuito).time().replace(microsecond=0)
    fechaVenta = datetime.combine(hoy, horaActual, tzinfo=tzQuito)

    venta = {
        "idVenta": 3,
        "idCaja": 2,
        "usuario": {
            "idUsuario": 3,
            "nombreCompleto": "cajero",
            "cedulaUsuario": "cajero",
            "emailUsuario": "cajero@example.com",
            "rol": {"idRol": 3, "nombreRol": "Cajero"},
            "activoUsuario": True,
        },
        "cliente": {
            "idCliente": 1,
            "nombreCliente": "María Gómez",
            "cedulaCliente": "1712345678",
            "telefonoCliente": "0998765432",
            "direccionCliente": "Calle La Pradera N56-78, Quito, Ecuador",
            "emailCliente": "maria.gomez@example.com",
            "activoCliente": True,
        },
        "fechaVenta": fechaVenta,
        "subtotalVenta": 6.1,
        "descuentoGeneral": 5.0,
        "totalDescuento": 1.16,
        "baseIVA": 15.0,
        "totalIVA": 0.36,
        "totalPagar": 5.3,
        "metodoPago": "Efectivo",
        "estadoVenta": "COMPLETADA",
        "detalles": [
            {
                "idDetalleVenta": 5,
                "idVenta": 3,
                "producto": {"idProducto": 1, "nombreProducto": "Cola 2 Litros", "precioUnitarioVenta": 2.5, "tieneIva": True, "activoProducto": True},
                "promocion": None,
                "precioUnitarioVendido": 2.5,
                "cantidadVendida": 1,
                "subtotalProducto": 2.5,
                "valorDescuentoProducto": 0.0,
            },
            {
                "idDetalleVenta": 6,
                "idVenta": 3,
                "producto": {"idProducto": 2, "nombreProducto": "Jugo de Naranja 1L", "precioUnitarioVenta": 1.8, "tieneIva": False, "activoProducto": True},
                "promocion": {
                    "idPromocion": 2,
                    "idProducto": 2,
                    "nombrePromocion": "Promoción Actual",
                    "porcentajePromocion": 25.0,
                    "fechaInicioPromocion": fechaVenta,
                    "fechaFinPromocion": datetime.combine(hoy + timedelta(days=30), time(23, 59, 59, microsecond=0), tzinfo=tzQuito),
                    "activoPromocion": True,
                },
                "precioUnitarioVendido": 1.8,
                "cantidadVendida": 2,
                "subtotalProducto": 3.6,
                "valorDescuentoProducto": 0.9,
            },
        ],
    }

    respuestaMock = respuestaApi(success=True, message="Ventas encontradas", data=[venta])

    with patch("app.Venta.controllers.ventaController.VentaService") as MockServicio, patch(
        "app.configuracionGeneral.seguridadJWT.verificarToken"
    ) as MockVerificarToken:
        MockServicio.return_value.listarVentasHoy.return_value = respuestaMock
        MockVerificarToken.return_value = _tokenAdmin()

        respuesta = client.get("/venta/", headers=_encabezadosAuth())
        assert respuesta.status_code == 200
        cuerpo = respuesta.json()

        assert cuerpo["success"] is True
        assert cuerpo["data"][0]["totalPagar"] == 5.3
        assert "-05:00" in cuerpo["data"][0]["fechaVenta"]


def testCrearVentaDevuelveCreadoMockeadoCajeroTotal53():
    """Prueba: POST /venta/crear registra venta (mockeado VentaService) y totalPagar=5.3."""
    client = TestClient(app)

    tzQuito = _quitoTZ()
    hoy = datetime.now(tzQuito).date()
    horaActual = datetime.now(tzQuito).time().replace(microsecond=0)

    cuerpoCrear = {
        "idCliente": 1,
        "metodoPago": "Efectivo",
        "descuentoGeneral": 5.0,
        "detalles": [
            {"idProducto": 1, "cantidadComprada": 1},
            {"idProducto": 2, "cantidadComprada": 2},
        ],
    }

    respuestaMock = respuestaApi(
        success=True,
        message="Venta registrada por 3-cajero",
        data={
            "idVenta": 3,
            "idCaja": 2,
            "usuario": {
                "idUsuario": 3,
                "nombreCompleto": "cajero",
                "cedulaUsuario": "cajero",
                "emailUsuario": "cajero@example.com",
                "rol": {"idRol": 3, "nombreRol": "Cajero"},
                "activoUsuario": True,
            },
            "cliente": {
                "idCliente": 1,
                "nombreCliente": "María Gómez",
                "cedulaCliente": "1712345678",
                "telefonoCliente": "0998765432",
                "direccionCliente": "Calle La Pradera N56-78, Quito, Ecuador",
                "emailCliente": "maria.gomez@example.com",
                "activoCliente": True,
            },
            "fechaVenta": datetime.combine(hoy, horaActual, tzinfo=tzQuito),
            "subtotalVenta": 6.1,
            "descuentoGeneral": 5.0,
            "totalDescuento": 1.16,
            "baseIVA": 15.0,
            "totalIVA": 0.36,
            "totalPagar": 5.3,
            "metodoPago": "Efectivo",
            "estadoVenta": "COMPLETADA",
            "detalles": [],
        },
    )

    with patch("app.Venta.controllers.ventaController.VentaService") as MockServicio, patch(
        "app.configuracionGeneral.seguridadJWT.verificarToken"
    ) as MockVerificarToken:
        MockServicio.return_value.crearVenta.return_value = respuestaMock
        MockVerificarToken.return_value = _tokenCajero()

        respuesta = client.post("/venta/crear", json=cuerpoCrear, headers=_encabezadosAuth())
        assert respuesta.status_code == 201
        cuerpo = respuesta.json()

        assert cuerpo["success"] is True
        assert cuerpo["data"]["totalPagar"] == 5.3
        assert "-05:00" in cuerpo["data"]["fechaVenta"]
