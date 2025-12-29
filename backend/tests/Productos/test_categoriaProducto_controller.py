# Pruebas del controlador de CategoriaProducto (usando mocks)
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


def testListarCategoriasDevuelveListaMockeada():
    """Prueba: GET /categoriaproducto/ devuelve lista de categorías (mockeado CategoriaProductoService)."""
    client = TestClient(app)

    categoriasIniciales = [
        {"idCategoriaProducto": 1, "nombreCategoria": "Bebidas", "activoCategoria": True},
        {"idCategoriaProducto": 2, "nombreCategoria": "Snacks", "activoCategoria": True},
        {"idCategoriaProducto": 3, "nombreCategoria": "Abarrotes", "activoCategoria": True},
        {"idCategoriaProducto": 4, "nombreCategoria": "Aseo y Limpieza", "activoCategoria": True},
        {"idCategoriaProducto": 5, "nombreCategoria": "Higiene Personal", "activoCategoria": True},
    ]

    respuestaMock = respuestaApi(success=True, message="Categorias encontrados", data=categoriasIniciales)

    with patch("app.Productos.controllers.categoriaProductoController.CategoriaProductoService") as MockServicio, patch(
        "app.configuracionGeneral.seguridadJWT.verificarToken"
    ) as MockVerificarToken:
        MockServicio.return_value.listarCategorias.return_value = respuestaMock
        MockVerificarToken.return_value = _tokenAdmin()

        respuesta = client.get("/categoriaproducto/", headers=_encabezadosAuthAdmin())
        assert respuesta.status_code == 200
        cuerpo = respuesta.json()
        assert cuerpo["success"] is True
        assert isinstance(cuerpo["data"], list)
        assert len(cuerpo["data"]) == 5
        assert cuerpo["data"][0]["nombreCategoria"] == "Bebidas"


def testCrearCategoriaDevuelveCreadaMockeada():
    """Prueba: POST /categoriaproducto/ crea una categoría (mockeado CategoriaProductoService)."""
    client = TestClient(app)

    cuerpoCrear = {"nombreCategoria": "Bebidas"}

    respuestaMock = respuestaApi(
        success=True,
        message="Categoria creada",
        data={"idCategoriaProducto": 1, "nombreCategoria": "Bebidas", "activoCategoria": True},
    )

    with patch("app.Productos.controllers.categoriaProductoController.CategoriaProductoService") as MockServicio, patch(
        "app.configuracionGeneral.seguridadJWT.verificarToken"
    ) as MockVerificarToken:
        MockServicio.return_value.crearCategoria.return_value = respuestaMock
        MockVerificarToken.return_value = _tokenAdmin()

        respuesta = client.post("/categoriaproducto/", json=cuerpoCrear, headers=_encabezadosAuthAdmin())
        assert respuesta.status_code == 201
        cuerpo = respuesta.json()
        assert cuerpo["success"] is True
        assert cuerpo["data"]["nombreCategoria"] == "Bebidas"
