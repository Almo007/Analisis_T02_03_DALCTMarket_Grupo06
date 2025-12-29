# Pruebas del controlador de Pedido (usando mocks)
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


def _tokenBodeguero():
    return {"idUsuario": 2, "rol": "Bodeguero", "nombreCompleto": "bodeguero"}


def testListarPedidosPendientesDevuelveListaMockeada():
    """Prueba: GET /pedido/pendientes devuelve pedidos pendientes (mockeado PedidoService)."""
    client = TestClient(app)

    pedidosPendientes = [
        {
            "idPedido": 1,
            "usuarioCreador": {
                "idUsuario": 2,
                "nombreCompleto": "bodeguero",
                "cedulaUsuario": "bodeguero",
                "emailUsuario": "bodeguero@example.com",
                "rol": {"idRol": 2, "nombreRol": "Bodeguero"},
                "activoUsuario": True,
            },
            "usuarioAprobador": None,
            "totalCostoPedido": 12.60,
            "fechaCreacion": None,
            "estadoPedido": "PENDIENTE_REVISION",
            "observaciones": None,
            "detalles": [],
        }
    ]

    respuestaMock = respuestaApi(success=True, message="Pedidos pendientes encontrados", data=pedidosPendientes)

    with patch("app.Pedido.controllers.pedidoController.PedidoService") as MockServicio, patch(
        "app.configuracionGeneral.seguridadJWT.verificarToken"
    ) as MockVerificarToken:
        MockServicio.return_value.listarPedidosPendientes.return_value = respuestaMock
        MockVerificarToken.return_value = _tokenAdmin()

        respuesta = client.get("/pedido/pendientes", headers=_encabezadosAuth())
        assert respuesta.status_code == 200
        cuerpo = respuesta.json()
        assert cuerpo["success"] is True
        assert isinstance(cuerpo["data"], list)
        assert len(cuerpo["data"]) == 1
        assert cuerpo["data"][0]["estadoPedido"] == "PENDIENTE_REVISION"


def testCrearPedidoDevuelveCreadoMockeado():
    """Prueba: POST /pedido/ crea un pedido (mockeado PedidoService)."""
    client = TestClient(app)

    cuerpoCrear = {"detalles": [{"idProducto": 1, "cantidadSolicitada": 2}, {"idProducto": 2, "cantidadSolicitada": 1}]}

    respuestaMock = respuestaApi(
        success=True,
        message="Pedido creado",
        data={
            "idPedido": 1,
            "usuarioCreador": {
                "idUsuario": 2,
                "nombreCompleto": "bodeguero",
                "cedulaUsuario": "bodeguero",
                "emailUsuario": "bodeguero@example.com",
                "rol": {"idRol": 2, "nombreRol": "Bodeguero"},
                "activoUsuario": True,
            },
            "usuarioAprobador": None,
            "totalCostoPedido": 12.60,
            "fechaCreacion": None,
            "estadoPedido": "PENDIENTE_REVISION",
            "observaciones": None,
            "detalles": [
                {
                    "idDetallePedido": 1,
                    "idPedido": 1,
                    "cantidadSolicitada": 2,
                    "precioUnitarioCompra": 1.80,
                    "estadoDetalle": "PENDIENTE_REVISION",
                    "fechaRecepcion": None,
                    "producto": None,
                    "usuarioReceptor": None,
                },
                {
                    "idDetallePedido": 2,
                    "idPedido": 1,
                    "cantidadSolicitada": 1,
                    "precioUnitarioCompra": 6.00,
                    "estadoDetalle": "PENDIENTE_REVISION",
                    "fechaRecepcion": None,
                    "producto": None,
                    "usuarioReceptor": None,
                },
            ],
        },
    )

    with patch("app.Pedido.controllers.pedidoController.PedidoService") as MockServicio, patch(
        "app.configuracionGeneral.seguridadJWT.verificarToken"
    ) as MockVerificarToken:
        MockServicio.return_value.crearPedido.return_value = respuestaMock
        MockVerificarToken.return_value = _tokenBodeguero()

        respuesta = client.post("/pedido/", json=cuerpoCrear, headers=_encabezadosAuth())
        assert respuesta.status_code == 201
        cuerpo = respuesta.json()
        assert cuerpo["success"] is True
        assert cuerpo["message"] == "Pedido creado"
        assert cuerpo["data"]["estadoPedido"] == "PENDIENTE_REVISION"
        assert len(cuerpo["data"]["detalles"]) == 2
