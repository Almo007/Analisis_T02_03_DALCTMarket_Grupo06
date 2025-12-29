from datetime import datetime, timezone, timedelta, date

from fastapi.testclient import TestClient
from unittest.mock import patch

from app.database import obtenerSesion
from app.main import app
from app.configuracionGeneral.schemasGenerales import respuestaApi


# Usar la app real (app.main) pero sin disparar startup_event (evita BD)
app.router.on_startup.clear()
app.router.on_shutdown.clear()


def _mockObtenerSesion():
    yield None


app.dependency_overrides[obtenerSesion] = _mockObtenerSesion


def _encabezadosAuth():
    return {"Authorization": "Bearer tokenPrueba"}


def _quitoTZ():
    return timezone(timedelta(hours=-5))


def _tokenAdmin():
    return {"idUsuario": 1, "rol": "Administrador", "nombreCompleto": "admin"}


def testReporteInventarioController200ConMockAdmin():
    """Prueba controller: POST /reportes/inventario retorna respuestaApi mockeada."""
    client = TestClient(app)

    respuestaMock = respuestaApi(
        success=True,
        message="Reporte de inventario generado",
        data={
            "items": [
                {
                    "idInventario": 1,
                    "cantidadDisponible": 10,
                    "cantidadMinima": 1,
                    "activoInventario": True,
                    "producto": {
                        "idProducto": 1,
                        "idCategoriaProducto": 1,
                        "idProveedor": 1,
                        "nombreProducto": "Cola 2 Litros",
                        "descripcionProducto": "Bebida gaseosa",
                        "precioUnitarioVenta": 2.5,
                        "precioUnitarioCompra": 1.8,
                        "tieneIva": True,
                        "activoProducto": True,
                        "categoria": {"idCategoriaProducto": 1, "nombreCategoria": "Bebidas", "activoCategoria": True},
                        "proveedor": {
                            "idProveedor": 1,
                            "razonSocial": "Distribuidora Andina",
                            "ruc": "1790012345001",
                            "direccionProveedor": "Quito",
                            "telefonoProveedor": "0991234567",
                            "emailProveedor": "ventas@andinabebidas.com",
                            "activoProveedor": True,
                        },
                    },
                }
            ]
        },
    )

    with patch("app.Reportes.controllers.reporteController.ReporteService") as MockServicio, patch(
        "app.configuracionGeneral.seguridadJWT.verificarToken"
    ) as MockVerificarToken:
        MockServicio.return_value.reporteInventario.return_value = respuestaMock
        MockVerificarToken.return_value = _tokenAdmin()

        respuesta = client.post("/reportes/inventario", json={}, headers=_encabezadosAuth())
        assert respuesta.status_code == 200
        cuerpo = respuesta.json()
        assert cuerpo["success"] is True
        assert cuerpo["message"] == "Reporte de inventario generado"
        assert len(cuerpo["data"]["items"]) == 1


def testResumenCajaDiariaController200ConMockAdminVentasTotal53():
    """Prueba controller: POST /reportes/resumen-caja retorna resumen con venta total 5.3 (mock)."""
    client = TestClient(app)

    tzQuito = _quitoTZ()
    hoy = datetime.now(tzQuito).date()
    ahora = datetime.now(tzQuito).replace(microsecond=0)

    respuestaMock = respuestaApi(
        success=True,
        message="Resumen de caja generado",
        data={
            "items": [
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
                    "fechaAperturaCaja": ahora,
                    "fechaCierreCaja": ahora,
                    "montoInicialDeclarado": 10.0,
                    "montoCierreDeclarado": 15.3,
                    "montoCierreSistema": 15.3,
                    "diferenciaCaja": 0.0,
                    "estadoCaja": "CERRADA",
                    "ventas": [
                        {
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
                            "fechaVenta": ahora,
                            "subtotalVenta": 6.1,
                            "descuentoGeneral": 5.0,
                            "totalDescuento": 1.16,
                            "baseIVA": 15.0,
                            "totalIVA": 0.36,
                            "totalPagar": 5.3,
                            "metodoPago": "Efectivo",
                            "estadoVenta": "COMPLETADA",
                            "detalles": [],
                        }
                    ],
                }
            ]
        },
    )

    with patch("app.Reportes.controllers.reporteController.ReporteService") as MockServicio, patch(
        "app.configuracionGeneral.seguridadJWT.verificarToken"
    ) as MockVerificarToken:
        MockServicio.return_value.resumenCajaDiaria.return_value = respuestaMock
        MockVerificarToken.return_value = _tokenAdmin()

        respuesta = client.post(
            "/reportes/resumen-caja",
            json={"fecha": hoy.isoformat(), "idUsuarioCaja": 3},
            headers=_encabezadosAuth(),
        )
        assert respuesta.status_code == 200
        cuerpo = respuesta.json()
        assert cuerpo["success"] is True
        assert cuerpo["data"]["items"][0]["ventas"][0]["totalPagar"] == 5.3
        assert "-05:00" in cuerpo["data"]["items"][0]["ventas"][0]["fechaVenta"]
