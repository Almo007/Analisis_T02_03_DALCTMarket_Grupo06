# Pruebas del controlador de Producto (usando mocks)
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


def testListarProductosDevuelveListaMockeada():
    """Prueba: GET /producto/ devuelve lista de productos (mockeado ProductoService)."""
    client = TestClient(app)

    productosIniciales = [
        {
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
        {
            "idProducto": 2,
            "idCategoriaProducto": 1,
            "idProveedor": 1,
            "nombreProducto": "Agua Mineral 600ml",
            "descripcionProducto": "Agua mineral sin gas",
            "precioUnitarioVenta": 0.90,
            "precioUnitarioCompra": 0.60,
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
    ]

    respuestaMock = respuestaApi(success=True, message="Productos encontrados", data=productosIniciales)

    with patch("app.Productos.controllers.productoController.ProductoService") as MockServicio, patch(
        "app.configuracionGeneral.seguridadJWT.verificarToken"
    ) as MockVerificarToken:
        MockServicio.return_value.listarProductos.return_value = respuestaMock
        MockVerificarToken.return_value = _tokenAdmin()

        respuesta = client.get("/producto/", headers=_encabezadosAuthAdmin())
        assert respuesta.status_code == 200
        cuerpo = respuesta.json()
        assert cuerpo["success"] is True
        assert isinstance(cuerpo["data"], list)
        assert len(cuerpo["data"]) == 2
        assert cuerpo["data"][0]["nombreProducto"] == "Cola 2 Litros"


def testCrearProductoDevuelveCreadoMockeado():
    """Prueba: POST /producto/ crea un producto (mockeado ProductoService)."""
    client = TestClient(app)

    cuerpoCrear = {
        "idCategoriaProducto": 1,
        "idProveedor": 1,
        "nombreProducto": "Cola 2 Litros",
        "descripcionProducto": "Bebida gaseosa sabor cola",
        "precioUnitarioVenta": 2.50,
        "precioUnitarioCompra": 1.80,
        "tieneIva": True,
    }

    respuestaMock = respuestaApi(
        success=True,
        message="Producto creado",
        data={
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
    )

    with patch("app.Productos.controllers.productoController.ProductoService") as MockServicio, patch(
        "app.configuracionGeneral.seguridadJWT.verificarToken"
    ) as MockVerificarToken:
        MockServicio.return_value.crearProducto.return_value = respuestaMock
        MockVerificarToken.return_value = _tokenAdmin()

        respuesta = client.post("/producto/", json=cuerpoCrear, headers=_encabezadosAuthAdmin())
        assert respuesta.status_code == 201
        cuerpo = respuesta.json()
        assert cuerpo["success"] is True
        assert cuerpo["message"] == "Producto creado"
        assert cuerpo["data"]["nombreProducto"] == "Cola 2 Litros"
