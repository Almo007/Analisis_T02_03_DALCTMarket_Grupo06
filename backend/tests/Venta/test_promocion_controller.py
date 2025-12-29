# Pruebas del controlador de Promocion (usando mocks)
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


def _tokenAdmin():
    return {"idUsuario": 1, "rol": "Administrador", "nombreCompleto": "admin"}


def _fechaHoyQuito():
    tzQuito = timezone(timedelta(hours=-5))
    return datetime.now(tzQuito).date()


def _quitoTZ():
    return timezone(timedelta(hours=-5))


def testListarPromocionesDevuelveListaMockeada():
    """Prueba: GET /promocion/ devuelve lista de promociones (mockeado PromocionService)."""
    client = TestClient(app)

    tzQuito = _quitoTZ()
    hoy = datetime.now(tzQuito).date()
    horaActual = datetime.now(tzQuito).time().replace(microsecond=0)

    inicioPasado = hoy - timedelta(days=60)
    finPasado = hoy - timedelta(days=30)
    inicioAct = hoy
    finAct = hoy + timedelta(days=30)

    promociones = [
        {
            "idPromocion": 1,
            "producto": {
                "idProducto": 1,
                "idCategoriaProducto": 1,
                "idProveedor": 1,
                "nombreProducto": "Cola 2 Litros",
                "descripcionProducto": "Bebida gaseosa sabor cola",
                "precioUnitarioVenta": 2.50,
                "precioUnitarioCompra": 1.80,
                "tieneIva": True,
                "activoProducto": True,
                "categoria": {"idCategoriaProducto": 1, "nombreCategoria": "Bebidas", "activoCategoria": True},
                "proveedor": {
                    "idProveedor": 1,
                    "razonSocial": "Distribuidora Andina de Bebidas S.A.",
                    "ruc": "1790012345001",
                    "direccionProveedor": "Av. Maldonado y Morán Valverde, Quito",
                    "telefonoProveedor": "0991234567",
                    "emailProveedor": "ventas@andinabebidas.com",
                    "activoProveedor": True,
                },
            },
            "nombrePromocion": "Promoción Pasada",
            "porcentajePromocion": 10.0,
            "fechaInicioPromocion": datetime.combine(inicioPasado, horaActual, tzinfo=tzQuito).isoformat(),
            "fechaFinPromocion": datetime.combine(finPasado, time(23, 59, 59, microsecond=0), tzinfo=tzQuito).isoformat(),
            "activoPromocion": True,
        },
        {
            "idPromocion": 2,
            "producto": {
                "idProducto": 2,
                "idCategoriaProducto": 1,
                "idProveedor": 1,
                "nombreProducto": "Jugo de Naranja 1L",
                "descripcionProducto": "Jugo natural de naranja 1 litro",
                "precioUnitarioVenta": 2.20,
                "precioUnitarioCompra": 1.60,
                "tieneIva": True,
                "activoProducto": True,
                "categoria": {"idCategoriaProducto": 1, "nombreCategoria": "Bebidas", "activoCategoria": True},
                "proveedor": {
                    "idProveedor": 1,
                    "razonSocial": "Distribuidora Andina de Bebidas S.A.",
                    "ruc": "1790012345001",
                    "direccionProveedor": "Av. Maldonado y Morán Valverde, Quito",
                    "telefonoProveedor": "0991234567",
                    "emailProveedor": "ventas@andinabebidas.com",
                    "activoProveedor": True,
                },
            },
            "nombrePromocion": "Promoción Actual",
            "porcentajePromocion": 25.0,
            "fechaInicioPromocion": datetime.combine(inicioAct, horaActual, tzinfo=tzQuito).isoformat(),
            "fechaFinPromocion": datetime.combine(finAct, time(23, 59, 59, microsecond=0), tzinfo=tzQuito).isoformat(),
            "activoPromocion": True,
        },
    ]

    respuestaMock = respuestaApi(success=True, message="Promociones encontradas", data=promociones)

    with patch("app.Venta.controllers.promocionController.PromocionService") as MockServicio, patch(
        "app.configuracionGeneral.seguridadJWT.verificarToken"
    ) as MockVerificarToken:
        MockServicio.return_value.listarPromociones.return_value = respuestaMock
        MockVerificarToken.return_value = _tokenAdmin()

        respuesta = client.get("/promocion/", headers=_encabezadosAuth())
        assert respuesta.status_code == 200
        cuerpo = respuesta.json()
        assert cuerpo["success"] is True
        assert isinstance(cuerpo["data"], list)
        assert len(cuerpo["data"]) == 2
        assert cuerpo["data"][1]["nombrePromocion"] == "Promoción Actual"


def testCrearPromocionDevuelveCreadoMockeado():
    """Prueba: POST /promocion/ crea una promoción (mockeado PromocionService)."""
    client = TestClient(app)

    tzQuito = _quitoTZ()
    hoy = datetime.now(tzQuito).date()
    fin = hoy + timedelta(days=30)
    horaActual = datetime.now(tzQuito).time().replace(microsecond=0)

    cuerpoCrear = {
        "idProducto": 2,
        "nombrePromocion": "Promoción Actual",
        "porcentajePromocion": 25.0,
        "fechaInicioPromocion": str(hoy),
        "fechaFinPromocion": str(fin),
    }

    respuestaMock = respuestaApi(
        success=True,
        message="Promoción creada",
        data={
            "idPromocion": 2,
            "producto": {
                "idProducto": 2,
                "idCategoriaProducto": 1,
                "idProveedor": 1,
                "nombreProducto": "Jugo de Naranja 1L",
                "descripcionProducto": "Jugo natural de naranja 1 litro",
                "precioUnitarioVenta": 2.20,
                "precioUnitarioCompra": 1.60,
                "tieneIva": True,
                "activoProducto": True,
                "categoria": {"idCategoriaProducto": 1, "nombreCategoria": "Bebidas", "activoCategoria": True},
                "proveedor": {
                    "idProveedor": 1,
                    "razonSocial": "Distribuidora Andina de Bebidas S.A.",
                    "ruc": "1790012345001",
                    "direccionProveedor": "Av. Maldonado y Morán Valverde, Quito",
                    "telefonoProveedor": "0991234567",
                    "emailProveedor": "ventas@andinabebidas.com",
                    "activoProveedor": True,
                },
            },
            "nombrePromocion": "Promoción Actual",
            "porcentajePromocion": 25.0,
            "fechaInicioPromocion": datetime.combine(hoy, horaActual, tzinfo=tzQuito).isoformat(),
            "fechaFinPromocion": datetime.combine(fin, time(23, 59, 59, microsecond=0), tzinfo=tzQuito).isoformat(),
            "activoPromocion": True,
        },
    )

    with patch("app.Venta.controllers.promocionController.PromocionService") as MockServicio, patch(
        "app.configuracionGeneral.seguridadJWT.verificarToken"
    ) as MockVerificarToken:
        MockServicio.return_value.crearPromocion.return_value = respuestaMock
        MockVerificarToken.return_value = _tokenAdmin()

        respuesta = client.post("/promocion/", json=cuerpoCrear, headers=_encabezadosAuth())
        assert respuesta.status_code == 201
        cuerpo = respuesta.json()
        assert cuerpo["success"] is True
        assert cuerpo["message"] == "Promoción creada"
        assert cuerpo["data"]["porcentajePromocion"] == 25.0
