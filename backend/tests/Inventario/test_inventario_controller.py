# Pruebas del controlador de Inventario (usando mocks)
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


def testListarInventariosDevuelveListaMockeada():
    """Prueba: GET /inventario/ devuelve lista de inventarios (mockeado InventarioService)."""
    client = TestClient(app)

    inventariosIniciales = [
        {
            "idInventario": 1,
            "cantidadDisponible": 50,
            "cantidadMinima": 10,
            "activoInventario": True,
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
        }
    ]

    respuestaMock = respuestaApi(success=True, message="Inventarios encontrados", data=inventariosIniciales)

    with patch("app.Inventario.controllers.inventarioController.InventarioService") as MockServicio, patch(
        "app.configuracionGeneral.seguridadJWT.verificarToken"
    ) as MockVerificarToken:
        MockServicio.return_value.listarInventarios.return_value = respuestaMock
        MockVerificarToken.return_value = _tokenAdmin()

        respuesta = client.get("/inventario/", headers=_encabezadosAuthAdmin())
        assert respuesta.status_code == 200
        cuerpo = respuesta.json()
        assert cuerpo["success"] is True
        assert isinstance(cuerpo["data"], list)
        assert len(cuerpo["data"]) == 1
        assert cuerpo["data"][0]["cantidadDisponible"] == 50


def testCrearInventarioDevuelveCreadoMockeado():
    """Prueba: POST /inventario/ crea inventario (mockeado InventarioService)."""
    client = TestClient(app)

    cuerpoCrear = {"idProducto": 1, "cantidadDisponible": 50, "cantidadMinima": 10}

    respuestaMock = respuestaApi(
        success=True,
        message="Inventario creado",
        data={
            "idInventario": 1,
            "cantidadDisponible": 50,
            "cantidadMinima": 10,
            "activoInventario": True,
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
        },
    )

    with patch("app.Inventario.controllers.inventarioController.InventarioService") as MockServicio, patch(
        "app.configuracionGeneral.seguridadJWT.verificarToken"
    ) as MockVerificarToken:
        MockServicio.return_value.crearInventario.return_value = (respuestaMock, 201)
        MockVerificarToken.return_value = _tokenAdmin()

        respuesta = client.post("/inventario/", json=cuerpoCrear, headers=_encabezadosAuthAdmin())
        assert respuesta.status_code == 201
        cuerpo = respuesta.json()
        assert cuerpo["success"] is True
        assert cuerpo["message"] == "Inventario creado"
        assert cuerpo["data"]["cantidadMinima"] == 10
