import pytest
from unittest.mock import patch
from fastapi import HTTPException

from app.Pedido.services.pedidoService import PedidoService
from app.Pedido.schemas.pedidoSchemas import (
    PedidoCrearSchema,
    DetallePedidoCrearSchema,
    RevisarPedidoSchema,
    RecepcionDetalleSchema,
)

from tests.mocks_models.pedidoMock import crearPedidoMock
from tests.mocks_models.detallePedidoMock import crearDetallePedidoMock
from tests.mocks_models.usuarioMock import crearUsuarioMock
from tests.mocks_models.rolMock import crearRolMock
from tests.mocks_models.productoMock import crearProductoMock
from tests.mocks_models.categoriaProductoMock import crearCategoriaProductoMock
from tests.mocks_models.proveedorMock import crearProveedorMock


def _usuarioAdminMock():
    rolMock = crearRolMock(idRol=1, nombreRol="Administrador")
    return crearUsuarioMock(
        idUsuario=1,
        idRol=1,
        nombreCompleto="admin",
        cedulaUsuario="admin",
        emailUsuario="admin@example.com",
        passwordUsuario="1234",
        activoUsuario=True,
        rol=rolMock,
    )


def _usuarioBodegueroMock():
    rolMock = crearRolMock(idRol=2, nombreRol="Bodeguero")
    return crearUsuarioMock(
        idUsuario=2,
        idRol=2,
        nombreCompleto="bodeguero",
        cedulaUsuario="bodeguero",
        emailUsuario="bodeguero@example.com",
        passwordUsuario="1234",
        activoUsuario=True,
        rol=rolMock,
    )


def _tokenAdmin():
    return {"idUsuario": 1, "rol": "Administrador", "nombreCompleto": "admin"}


def _tokenBodeguero():
    return {"idUsuario": 2, "rol": "Bodeguero", "nombreCompleto": "bodeguero"}


def _tokenCajero():
    return {"idUsuario": 3, "rol": "Cajero", "nombreCompleto": "cajero"}


def _productoBaseMock(idProducto: int, nombreProducto: str, precioUnitarioCompra: float = 1.0):
    categoriaMock = crearCategoriaProductoMock(idCategoriaProducto=1, nombreCategoria="Bebidas", activoCategoria=True)
    proveedorMock = crearProveedorMock(
        idProveedor=1,
        razonSocial="Distribuidora Andina de Bebidas S.A.",
        ruc="1790012345001",
        direccionProveedor="Av. Maldonado y Morán Valverde, Quito",
        telefonoProveedor="0991234567",
        emailProveedor="ventas@andinabebidas.com",
        activoProveedor=True,
    )
    return crearProductoMock(
        idProducto=idProducto,
        idCategoriaProducto=1,
        idProveedor=1,
        nombreProducto=nombreProducto,
        descripcionProducto="",
        precioUnitarioVenta=precioUnitarioCompra * 1.3,
        precioUnitarioCompra=precioUnitarioCompra,
        tieneIva=True,
        activoProducto=True,
        categoria=categoriaMock,
        proveedor=proveedorMock,
    )


def _pedidoConDosDetallesMock(estadoPedido: str = "PENDIENTE_REVISION", estadoDetalles: str = "PENDIENTE_REVISION"):
    usuarioCreadorMock = _usuarioBodegueroMock()
    usuarioAprobadorMock = None

    producto1Mock = _productoBaseMock(1, "Cola 2 Litros", precioUnitarioCompra=1.80)
    producto2Mock = _productoBaseMock(2, "Jugo de Naranja 1L", precioUnitarioCompra=2.00)

    detalle1Mock = crearDetallePedidoMock(
        idDetallePedido=1,
        idPedido=1,
        idProducto=1,
        cantidadSolicitada=2,
        precioUnitarioCompra=1.80,
        estadoDetalle=estadoDetalles,
        producto=producto1Mock,
        usuarioReceptor=None,
    )
    detalle2Mock = crearDetallePedidoMock(
        idDetallePedido=2,
        idPedido=1,
        idProducto=2,
        cantidadSolicitada=1,
        precioUnitarioCompra=2.00,
        estadoDetalle=estadoDetalles,
        producto=producto2Mock,
        usuarioReceptor=None,
    )

    pedidoMock = crearPedidoMock(
        idPedido=1,
        idUsuarioCreador=2,
        idUsuarioAprobador=None,
        totalCostoPedido=1.80 * 2 + 2.00 * 1,
        estadoPedido=estadoPedido,
        detalles=[detalle1Mock, detalle2Mock],
        usuarioCreador=usuarioCreadorMock,
        usuarioAprobador=usuarioAprobadorMock,
    )

    detalle1Mock.pedido = pedidoMock
    detalle2Mock.pedido = pedidoMock
    return pedidoMock, detalle1Mock, detalle2Mock


def testListarPedidosDevuelveListaVaciaSiNoHayDatos():
    """Prueba: listarPedidos devuelve data=[] si repositorio retorna lista vacía/None."""
    with patch("app.Pedido.services.pedidoService.PedidoRepository") as MockRepo:
        MockRepo.return_value.listarPedidos.return_value = []

        servicio = PedidoService(dbSession=None)
        respuesta = servicio.listarPedidos()

        assert respuesta.success is True
        assert respuesta.data == []


def testObtenerPedidoPorIdNoEncontradoLanza404():
    """Prueba: obtenerPorId lanza 404 si el pedido no existe."""
    with patch("app.Pedido.services.pedidoService.PedidoRepository") as MockRepo:
        MockRepo.return_value.obtenerPorId.return_value = None

        servicio = PedidoService(dbSession=None)
        with pytest.raises(HTTPException) as excinfo:
            servicio.obtenerPorId(999)
        assert excinfo.value.status_code == 404


def testListarPedidosPendientesDevuelveListaVaciaSiNoHayDatos():
    """Prueba: listarPedidosPendientes devuelve data=[] si no hay pedidos pendientes."""
    with patch("app.Pedido.services.pedidoService.PedidoRepository") as MockRepo:
        MockRepo.return_value.listarPedidosPendientes.return_value = []

        servicio = PedidoService(dbSession=None)
        respuesta = servicio.listarPedidosPendientes()

        assert respuesta.success is True
        assert respuesta.data == []


def testCrearPedidoExitosoDevuelvePedidoCreadoPendienteRevision():
    """Prueba: crearPedido retorna 'Pedido creado' y el estado inicial debe ser PENDIENTE_REVISION (si crea Bodeguero)."""
    pedidoMock, _, _ = _pedidoConDosDetallesMock(estadoPedido="PENDIENTE_REVISION", estadoDetalles="PENDIENTE_REVISION")

    with patch("app.Pedido.services.pedidoService.PedidoRepository") as MockRepo:
        MockRepo.return_value.crearPedido.return_value = pedidoMock

        servicio = PedidoService(dbSession=None)
        pedidoCrear = PedidoCrearSchema(
            detalles=[
                DetallePedidoCrearSchema(idProducto=1, cantidadSolicitada=2),
                DetallePedidoCrearSchema(idProducto=2, cantidadSolicitada=1),
            ]
        )

        respuesta = servicio.crearPedido(pedidoCrear, _tokenBodeguero())
        assert respuesta.success is True
        assert respuesta.message == "Pedido creado"
        assert respuesta.data.estadoPedido == "PENDIENTE_REVISION"
        assert len(respuesta.data.detalles) == 2


def testCrearPedidoConErroresDeProductosLanza400():
    """Prueba: crearPedido lanza 400 si el repo devuelve {error: [...]} (productos faltantes/inactivos)."""
    with patch("app.Pedido.services.pedidoService.PedidoRepository") as MockRepo:
        MockRepo.return_value.crearPedido.return_value = {"error": [{"idProducto": 99, "error": "producto_no_encontrado"}]}

        servicio = PedidoService(dbSession=None)
        pedidoCrear = PedidoCrearSchema(detalles=[DetallePedidoCrearSchema(idProducto=99, cantidadSolicitada=1)])

        with pytest.raises(HTTPException) as excinfo:
            servicio.crearPedido(pedidoCrear, _tokenBodeguero())
        assert excinfo.value.status_code == 400


def testRevisarPedidoSoloAdminPuedeRevisarLanza403():
    """Prueba: revisarPedido lanza 403 si rol no es Administrador."""
    pedidoMock, _, _ = _pedidoConDosDetallesMock()

    with patch("app.Pedido.services.pedidoService.PedidoRepository") as MockRepo:
        MockRepo.return_value.obtenerPorId.return_value = pedidoMock

        servicio = PedidoService(dbSession=None)
        revisar = RevisarPedidoSchema(estadoPedido="APROBADO", observaciones=None)

        with pytest.raises(HTTPException) as excinfo:
            servicio.revisarPedido(1, revisar, _tokenBodeguero())
        assert excinfo.value.status_code == 403


def testRevisarPedidoEstadoInvalidoLanza400():
    """Prueba: revisarPedido lanza 400 si el estadoPedido no es APROBADO/RECHAZADO."""
    pedidoMock, _, _ = _pedidoConDosDetallesMock()

    with patch("app.Pedido.services.pedidoService.PedidoRepository") as MockRepo:
        MockRepo.return_value.obtenerPorId.return_value = pedidoMock

        servicio = PedidoService(dbSession=None)
        revisar = RevisarPedidoSchema(estadoPedido="APROBADO", observaciones=None)
        revisar.estadoPedido = "OTRO"  # forzar caso inválido

        with pytest.raises(HTTPException) as excinfo:
            servicio.revisarPedido(1, revisar, _tokenAdmin())
        assert excinfo.value.status_code == 400


def testRevisarPedidoRepoRetornaPedidoNoModificableLanza400():
    """Prueba: revisarPedido lanza 400 si el pedido ya fue revisado (repo error pedido_no_modificable)."""
    pedidoMock, _, _ = _pedidoConDosDetallesMock()

    with patch("app.Pedido.services.pedidoService.PedidoRepository") as MockRepo:
        instanciaRepo = MockRepo.return_value
        instanciaRepo.obtenerPorId.return_value = pedidoMock
        instanciaRepo.revisarPedido.return_value = {"error": "pedido_no_modificable"}

        servicio = PedidoService(dbSession=None)
        revisar = RevisarPedidoSchema(estadoPedido="APROBADO", observaciones=None)

        with pytest.raises(HTTPException) as excinfo:
            servicio.revisarPedido(1, revisar, _tokenAdmin())
        assert excinfo.value.status_code == 400


def testRevisarPedidoExitosoDevuelvePedidoRevisado():
    """Prueba: revisarPedido retorna 'Pedido revisado' cuando el admin aprueba."""
    pedidoPendienteMock, detalle1Mock, detalle2Mock = _pedidoConDosDetallesMock(estadoPedido="PENDIENTE_REVISION", estadoDetalles="PENDIENTE_REVISION")

    pedidoAprobadoMock, _, _ = _pedidoConDosDetallesMock(estadoPedido="APROBADO", estadoDetalles="PENDIENTE_RECEPCION")
    pedidoAprobadoMock.usuarioAprobador = _usuarioAdminMock()

    with patch("app.Pedido.services.pedidoService.PedidoRepository") as MockRepo:
        instanciaRepo = MockRepo.return_value
        instanciaRepo.obtenerPorId.return_value = pedidoPendienteMock
        instanciaRepo.revisarPedido.return_value = pedidoAprobadoMock

        servicio = PedidoService(dbSession=None)
        revisar = RevisarPedidoSchema(estadoPedido="APROBADO", observaciones="OK")

        respuesta = servicio.revisarPedido(1, revisar, _tokenAdmin())
        assert respuesta.success is True
        assert respuesta.message == "Pedido revisado"
        assert respuesta.data.estadoPedido == "APROBADO"
        assert len(respuesta.data.detalles) == 2
        assert respuesta.data.detalles[0].estadoDetalle == "PENDIENTE_RECEPCION"


def testListarDetallesPorPedidoDevuelveListaVaciaSiNoHayDatos():
    """Prueba: listarDetallesPorPedido devuelve data=[] si no existen detalles para el pedido."""
    with patch("app.Pedido.services.pedidoService.PedidoRepository") as MockRepo:
        MockRepo.return_value.listarDetallesPorPedido.return_value = []

        servicio = PedidoService(dbSession=None)
        respuesta = servicio.listarDetallesPorPedido(1)

        assert respuesta.success is True
        assert respuesta.data == []


def testObtenerDetallePorIdNoEncontradoLanza404():
    """Prueba: obtenerDetallePorId lanza 404 si el detalle no existe."""
    with patch("app.Pedido.services.pedidoService.PedidoRepository") as MockRepo:
        MockRepo.return_value.obtenerDetallePorId.return_value = None

        servicio = PedidoService(dbSession=None)
        with pytest.raises(HTTPException) as excinfo:
            servicio.obtenerDetallePorId(999)
        assert excinfo.value.status_code == 404


def testRealizarRecepcionDetalleRolSinPermisoLanza403():
    """Prueba: realizarRecepcionDetalle lanza 403 si el rol no es Bodeguero/Administrador."""
    with patch("app.Pedido.services.pedidoService.PedidoRepository") as MockRepo:
        MockRepo.return_value.registrarRecepcionDetalle.return_value = None

        servicio = PedidoService(dbSession=None)
        recepcion = RecepcionDetalleSchema(confirmar=True)

        with pytest.raises(HTTPException) as excinfo:
            servicio.realizarRecepcionDetalle(1, recepcion, _tokenCajero())
        assert excinfo.value.status_code == 403


def testRealizarRecepcionDetalleConfirmarFalseLanza400():
    """Prueba: realizarRecepcionDetalle lanza 400 si confirmar es False."""
    with patch("app.Pedido.services.pedidoService.PedidoRepository") as MockRepo:
        MockRepo.return_value.registrarRecepcionDetalle.return_value = None

        servicio = PedidoService(dbSession=None)
        recepcion = RecepcionDetalleSchema(confirmar=False)

        with pytest.raises(HTTPException) as excinfo:
            servicio.realizarRecepcionDetalle(1, recepcion, _tokenBodeguero())
        assert excinfo.value.status_code == 400


def testRealizarRecepcionDetalleDetalleNoEncontradoLanza404():
    """Prueba: realizarRecepcionDetalle lanza 404 si el repo retorna None."""
    with patch("app.Pedido.services.pedidoService.PedidoRepository") as MockRepo:
        MockRepo.return_value.registrarRecepcionDetalle.return_value = None

        servicio = PedidoService(dbSession=None)
        recepcion = RecepcionDetalleSchema(confirmar=True)

        with pytest.raises(HTTPException) as excinfo:
            servicio.realizarRecepcionDetalle(999, recepcion, _tokenBodeguero())
        assert excinfo.value.status_code == 404


def testRealizarRecepcionDetalleYaRecibidoLanza409():
    """Prueba: realizarRecepcionDetalle lanza 409 si el detalle ya fue recibido (repo ya_recibido)."""
    with patch("app.Pedido.services.pedidoService.PedidoRepository") as MockRepo:
        MockRepo.return_value.registrarRecepcionDetalle.return_value = {"error": "ya_recibido"}

        servicio = PedidoService(dbSession=None)
        recepcion = RecepcionDetalleSchema(confirmar=True)

        with pytest.raises(HTTPException) as excinfo:
            servicio.realizarRecepcionDetalle(1, recepcion, _tokenBodeguero())
        assert excinfo.value.status_code == 409


def testRealizarRecepcionDetalleExitosoDevuelveDetalleRecibido():
    """Prueba: realizarRecepcionDetalle retorna 'Recepción registrada' con detalle en estado RECIBIDO."""
    pedidoMock, detalle1Mock, _ = _pedidoConDosDetallesMock(estadoPedido="APROBADO", estadoDetalles="PENDIENTE_RECEPCION")
    detalleRecibidoMock = crearDetallePedidoMock(
        idDetallePedido=1,
        idPedido=pedidoMock.idPedido,
        idProducto=detalle1Mock.idProducto,
        cantidadSolicitada=detalle1Mock.cantidadSolicitada,
        precioUnitarioCompra=detalle1Mock.precioUnitarioCompra,
        estadoDetalle="RECIBIDO",
        producto=detalle1Mock.producto,
        usuarioReceptor=_usuarioBodegueroMock(),
    )

    with patch("app.Pedido.services.pedidoService.PedidoRepository") as MockRepo:
        MockRepo.return_value.registrarRecepcionDetalle.return_value = detalleRecibidoMock

        servicio = PedidoService(dbSession=None)
        recepcion = RecepcionDetalleSchema(confirmar=True)

        respuesta = servicio.realizarRecepcionDetalle(1, recepcion, _tokenBodeguero())
        assert respuesta.success is True
        assert respuesta.message == "Recepción registrada"
        assert respuesta.data.estadoDetalle == "RECIBIDO"


def testSeguimientoDePedidosYComprasAProveedoresAdminYBodeguero():
    """Prueba: seguimiento completo (bodeguero crea -> admin aprueba -> bodeguero recepciona -> pedido completamente recibido)."""
    pedidoPendienteMock, detalle1Mock, detalle2Mock = _pedidoConDosDetallesMock(estadoPedido="PENDIENTE_REVISION", estadoDetalles="PENDIENTE_REVISION")

    pedidoAprobadoMock, _, _ = _pedidoConDosDetallesMock(estadoPedido="APROBADO", estadoDetalles="PENDIENTE_RECEPCION")
    pedidoAprobadoMock.usuarioAprobador = _usuarioAdminMock()

    detalle1RecibidoMock = crearDetallePedidoMock(
        idDetallePedido=1,
        idPedido=1,
        idProducto=1,
        cantidadSolicitada=detalle1Mock.cantidadSolicitada,
        precioUnitarioCompra=detalle1Mock.precioUnitarioCompra,
        estadoDetalle="RECIBIDO",
        producto=detalle1Mock.producto,
        usuarioReceptor=_usuarioBodegueroMock(),
    )
    detalle2RecibidoMock = crearDetallePedidoMock(
        idDetallePedido=2,
        idPedido=1,
        idProducto=2,
        cantidadSolicitada=detalle2Mock.cantidadSolicitada,
        precioUnitarioCompra=detalle2Mock.precioUnitarioCompra,
        estadoDetalle="RECIBIDO",
        producto=detalle2Mock.producto,
        usuarioReceptor=_usuarioBodegueroMock(),
    )

    pedidoEstadoActual = {"estado": "PENDIENTE_REVISION"}

    def _obtenerPorIdSideEffect(idPedido):
        if pedidoEstadoActual["estado"] == "PENDIENTE_REVISION":
            return pedidoPendienteMock
        if pedidoEstadoActual["estado"] == "APROBADO":
            return pedidoAprobadoMock
        # al finalizar la recepción, simulamos que el repo ya actualizó el pedido
        pedidoFinalMock, _, _ = _pedidoConDosDetallesMock(estadoPedido="COMPLETAMENTE_RECIBIDO", estadoDetalles="RECIBIDO")
        pedidoFinalMock.usuarioAprobador = _usuarioAdminMock()
        return pedidoFinalMock

    def _registrarRecepcionSideEffect(idDetalle, confirmar, idUsuario):
        if idDetalle == 1:
            pedidoEstadoActual["estado"] = "PARCIALMENTE_RECIBIDO"
            return detalle1RecibidoMock
        pedidoEstadoActual["estado"] = "COMPLETAMENTE_RECIBIDO"
        return detalle2RecibidoMock

    with patch("app.Pedido.services.pedidoService.PedidoRepository") as MockRepo:
        instanciaRepo = MockRepo.return_value
        # 1) Bodeguero crea pedido
        instanciaRepo.crearPedido.return_value = pedidoPendienteMock
        # 2) Admin lista pendientes
        instanciaRepo.listarPedidosPendientes.return_value = [pedidoPendienteMock]
        # 3) Revisar pedido
        instanciaRepo.obtenerPorId.side_effect = _obtenerPorIdSideEffect
        instanciaRepo.revisarPedido.return_value = pedidoAprobadoMock
        # 4) Recepcionar detalles
        instanciaRepo.registrarRecepcionDetalle.side_effect = _registrarRecepcionSideEffect

        servicio = PedidoService(dbSession=None)

        pedidoCrear = PedidoCrearSchema(
            detalles=[
                DetallePedidoCrearSchema(idProducto=1, cantidadSolicitada=2),
                DetallePedidoCrearSchema(idProducto=2, cantidadSolicitada=1),
            ]
        )
        respuestaCrear = servicio.crearPedido(pedidoCrear, _tokenBodeguero())
        assert respuestaCrear.success is True
        assert respuestaCrear.data.estadoPedido == "PENDIENTE_REVISION"

        respuestaPendientes = servicio.listarPedidosPendientes()
        assert respuestaPendientes.success is True
        assert len(respuestaPendientes.data) == 1

        respuestaRevisar = servicio.revisarPedido(1, RevisarPedidoSchema(estadoPedido="APROBADO", observaciones="OK"), _tokenAdmin())
        assert respuestaRevisar.success is True
        assert respuestaRevisar.data.estadoPedido == "APROBADO"

        respuestaRecep1 = servicio.realizarRecepcionDetalle(1, RecepcionDetalleSchema(confirmar=True), _tokenBodeguero())
        assert respuestaRecep1.success is True
        assert respuestaRecep1.data.estadoDetalle == "RECIBIDO"

        respuestaRecep2 = servicio.realizarRecepcionDetalle(2, RecepcionDetalleSchema(confirmar=True), _tokenBodeguero())
        assert respuestaRecep2.success is True
        assert respuestaRecep2.data.estadoDetalle == "RECIBIDO"

        # Verificación final de estado del pedido: COMPLETAMENTE_RECIBIDO
        respuestaFinal = servicio.obtenerPorId(1)
        assert respuestaFinal.success is True
        assert respuestaFinal.data.estadoPedido == "COMPLETAMENTE_RECIBIDO"
