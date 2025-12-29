# Pruebas del controlador de Proveedor (usando mocks)
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
    return {"idUsuario": 1, "rol": "Administrador", "nombreCompleto": "Admin"}


def testListarProveedoresDevuelveListaMockeada():
    """Prueba: GET /proveedor/ devuelve lista de proveedores (mockeado ProveedorService)."""
    client = TestClient(app)

    proveedoresIniciales = [
        {
            "idProveedor": 1,
            "razonSocial": "Distribuidora Andina de Bebidas S.A.",
            "ruc": "1790012345001",
            "direccionProveedor": "Av. Maldonado y Morán Valverde, Quito",
            "telefonoProveedor": "0991234567",
            "emailProveedor": "ventas@andinabebidas.com",
            "activoProveedor": True,
        },
        {
            "idProveedor": 2,
            "razonSocial": "Snacks del Valle Cía. Ltda.",
            "ruc": "1790023456001",
            "direccionProveedor": "Av. Galo Plaza Lasso, Quito",
            "telefonoProveedor": "0987654321",
            "emailProveedor": "contacto@snacksdelvalle.com",
            "activoProveedor": True,
        },
        {
            "idProveedor": 3,
            "razonSocial": "Abarrotes Quito Comercial AQ S.A.",
            "ruc": "1790034567001",
            "direccionProveedor": "Av. América y Naciones Unidas, Quito",
            "telefonoProveedor": "0974567890",
            "emailProveedor": "ventas@abarrotesaq.com",
            "activoProveedor": True,
        },
        {
            "idProveedor": 4,
            "razonSocial": "Limpieza Total Ecuador LT S.A.",
            "ruc": "1790045678001",
            "direccionProveedor": "Av. Mariscal Sucre, Quito",
            "telefonoProveedor": "0962345678",
            "emailProveedor": "ventas@limpiezatotal.com",
            "activoProveedor": True,
        },
        {
            "idProveedor": 5,
            "razonSocial": "Higiene y Cuidado Personal HC S.A.",
            "ruc": "1790056789001",
            "direccionProveedor": "Av. Simón Bolívar, Quito",
            "telefonoProveedor": "0956781234",
            "emailProveedor": "contacto@higienepersonalhc.com",
            "activoProveedor": True,
        },
    ]

    respuestaMock = respuestaApi(success=True, message="Proveedores encontrados", data=proveedoresIniciales)

    with patch("app.Productos.controllers.proveedorController.ProveedorService") as MockServicio, patch(
        "app.configuracionGeneral.seguridadJWT.verificarToken"
    ) as MockVerificarToken:
        MockServicio.return_value.listarProveedores.return_value = respuestaMock
        MockVerificarToken.return_value = _tokenAdmin()

        respuesta = client.get("/proveedor/", headers=_encabezadosAuthAdmin())
        assert respuesta.status_code == 200
        cuerpo = respuesta.json()
        assert cuerpo["success"] is True
        assert isinstance(cuerpo["data"], list)
        assert len(cuerpo["data"]) == 5
        assert cuerpo["data"][0]["ruc"] == "1790012345001"


def testCrearProveedorDevuelveCreadoMockeado():
    """Prueba: POST /proveedor/ crea un proveedor (mockeado ProveedorService)."""
    client = TestClient(app)

    cuerpoCrear = {
        "razonSocial": "Distribuidora Andina de Bebidas S.A.",
        "ruc": "1790012345001",
        "direccionProveedor": "Av. Maldonado y Morán Valverde, Quito",
        "telefonoProveedor": "0991234567",
        "emailProveedor": "ventas@andinabebidas.com",
    }

    respuestaMock = respuestaApi(
        success=True,
        message="Proveedor creado",
        data={
            "idProveedor": 1,
            "razonSocial": cuerpoCrear["razonSocial"],
            "ruc": cuerpoCrear["ruc"],
            "direccionProveedor": cuerpoCrear["direccionProveedor"],
            "telefonoProveedor": cuerpoCrear["telefonoProveedor"],
            "emailProveedor": cuerpoCrear["emailProveedor"],
            "activoProveedor": True,
        },
    )

    with patch("app.Productos.controllers.proveedorController.ProveedorService") as MockServicio, patch(
        "app.configuracionGeneral.seguridadJWT.verificarToken"
    ) as MockVerificarToken:
        MockServicio.return_value.crearProveedor.return_value = respuestaMock
        MockVerificarToken.return_value = _tokenAdmin()

        respuesta = client.post("/proveedor/", json=cuerpoCrear, headers=_encabezadosAuthAdmin())
        assert respuesta.status_code == 201
        cuerpo = respuesta.json()
        assert cuerpo["success"] is True
        assert cuerpo["data"]["ruc"] == "1790012345001"
