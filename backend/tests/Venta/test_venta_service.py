import pytest
from unittest.mock import MagicMock, patch
from fastapi import HTTPException

from datetime import datetime, timezone, timedelta, time

from app.Venta.services.ventaService import VentaService
from app.Venta.schemas.ventaSchemas import VentaCrearSchema
from app.Venta.schemas.detalleVentaSchemas import DetalleVentaCrearSchema

from tests.mocks_models.ventaMock import crearVentaMock
from tests.mocks_models.detalleVentaMock import crearDetalleVentaMock
from tests.mocks_models.cajaHistorialMock import crearCajaHistorialMock
from tests.mocks_models.productoMock import crearProductoMock
from tests.mocks_models.clienteMock import crearClienteMock
from tests.mocks_models.usuarioMock import crearUsuarioMock
from tests.mocks_models.rolMock import crearRolMock
from tests.mocks_models.inventarioMock import crearInventarioMock
from tests.mocks_models.promocionMock import crearPromocionMock


def _quitoTZ():
    return timezone(timedelta(hours=-5))


def _tokenAdmin():
    return {"idUsuario": 1, "rol": "Administrador", "nombreCompleto": "admin"}


def _tokenCajero():
    return {"idUsuario": 3, "rol": "Cajero", "nombreCompleto": "cajero"}


def _usuarioCajeroMock():
    rolMock = crearRolMock(idRol=3, nombreRol="Cajero")
    return crearUsuarioMock(idUsuario=3, idRol=3, nombreCompleto="cajero", cedulaUsuario="cajero", emailUsuario="cajero@example.com", rol=rolMock)


def _clienteMariaMock():
    return crearClienteMock(
        idCliente=1,
        nombreCliente="María Gómez",
        cedulaCliente="1712345678",
        telefonoCliente="0998765432",
        direccionCliente="Calle La Pradera N56-78, Quito, Ecuador",
        emailCliente="maria.gomez@example.com",
        activoCliente=True,
    )


def _cajaAbiertaHoyMock(idCaja: int = 2, idUsuarioCaja: int = 3):
    tzQuito = _quitoTZ()
    ahora = datetime.now(tzQuito).replace(microsecond=0)
    return crearCajaHistorialMock(
        idCaja=idCaja,
        idUsuarioCaja=idUsuarioCaja,
        fechaAperturaCaja=ahora,
        fechaCierreCaja=None,
        montoInicialDeclarado=10.0,
        montoCierreDeclarado=None,
        montoCierreSistema=None,
        diferenciaCaja=None,
        estadoCaja="ABIERTA",
        detalle=f"Apertura por {idUsuarioCaja}-cajero; montoInicialDeclarado: 10.0",
        usuario=_usuarioCajeroMock(),
    )


def _productoColaMock():
    return crearProductoMock(
        idProducto=1,
        idCategoriaProducto=1,
        idProveedor=1,
        nombreProducto="Cola 2 Litros",
        descripcionProducto="Bebida gaseosa sabor cola",
        precioUnitarioVenta=2.50,
        precioUnitarioCompra=1.80,
        tieneIva=True,
        activoProducto=True,
    )


def _productoJugoMock():
    return crearProductoMock(
        idProducto=2,
        idCategoriaProducto=1,
        idProveedor=1,
        nombreProducto="Jugo de Naranja 1L",
        descripcionProducto="Jugo natural de naranja 1 litro",
        precioUnitarioVenta=1.80,
        precioUnitarioCompra=1.60,
        tieneIva=False,
        activoProducto=True,
    )


def _promocionActualJugoMock():
    tzQuito = _quitoTZ()
    hoy = datetime.now(tzQuito).date()
    horaActual = datetime.now(tzQuito).time().replace(microsecond=0)
    fin = hoy + timedelta(days=30)
    return crearPromocionMock(
        idPromocion=2,
        idProducto=2,
        nombrePromocion="Promoción Actual",
        porcentajePromocion=25.0,
        fechaInicioPromocion=datetime.combine(hoy, horaActual, tzinfo=tzQuito),
        fechaFinPromocion=datetime.combine(fin, time(23, 59, 59, microsecond=0), tzinfo=tzQuito),
        activoPromocion=True,
        producto=None,
    )


def testCrearVentaExitosoTotalPagar53ConPromocionYDescuentoGeneral():
    """Prueba: crearVenta calcula totales (incluye promo 25% en jugo, descuentoGeneral 5% e IVA 15%) y da totalPagar=5.3."""
    dbSessionMock = MagicMock()

    clienteMock = _clienteMariaMock()
    cajaMock = _cajaAbiertaHoyMock(idCaja=2, idUsuarioCaja=3)

    productoCola = _productoColaMock()
    productoJugo = _productoJugoMock()

    inventarioCola = crearInventarioMock(idInventario=1, idProducto=1, cantidadDisponible=10, cantidadMinima=1)
    inventarioJugo = crearInventarioMock(idInventario=2, idProducto=2, cantidadDisponible=10, cantidadMinima=1)

    promoJugo = _promocionActualJugoMock()

    tzQuito = _quitoTZ()
    fechaVenta = datetime.now(tzQuito).replace(microsecond=0)

    detalleCola = crearDetalleVentaMock(
        idDetalleVenta=5,
        idVenta=3,
        idProducto=1,
        idPromocion=None,
        precioUnitarioVendido=2.5,
        cantidadVendida=1,
        subtotalProducto=2.5,
        valorDescuentoProducto=0.0,
        producto=productoCola,
        promocion=None,
    )
    detalleJugo = crearDetalleVentaMock(
        idDetalleVenta=6,
        idVenta=3,
        idProducto=2,
        idPromocion=2,
        precioUnitarioVendido=1.8,
        cantidadVendida=2,
        subtotalProducto=3.6,
        valorDescuentoProducto=0.9,
        producto=productoJugo,
        promocion=promoJugo,
    )

    ventaCreada = crearVentaMock(
        idVenta=3,
        idCaja=2,
        idUsuarioVenta=3,
        idCliente=1,
        fechaVenta=fechaVenta,
        subtotalVenta=6.1,
        descuentoGeneral=5.0,
        totalDescuento=1.16,
        baseIVA=15.0,
        totalIVA=0.36,
        totalPagar=5.3,
        metodoPago="Efectivo",
        estadoVenta="COMPLETADA",
        usuario=_usuarioCajeroMock(),
        cliente=clienteMock,
        detalles=[detalleCola, detalleJugo],
    )

    parametroIvaMock = MagicMock()
    parametroIvaMock.valorParametro = "15"

    ventaCrear = VentaCrearSchema(
        idCliente=1,
        metodoPago="Efectivo",
        descuentoGeneral=5.0,
        detalles=[
            DetalleVentaCrearSchema(idProducto=1, cantidadComprada=1),
            DetalleVentaCrearSchema(idProducto=2, cantidadComprada=2),
        ],
    )

    with patch("app.Venta.services.ventaService.ClienteRepository") as MockClienteRepo, patch(
        "app.Venta.services.ventaService.CajaRepository"
    ) as MockCajaRepo, patch("app.Venta.services.ventaService.ProductoRepository") as MockProductoRepo, patch(
        "app.Venta.services.ventaService.PromocionRepository"
    ) as MockPromRepo, patch("app.Venta.services.ventaService.ParametroSistemaRepository") as MockParamRepo, patch(
        "app.Venta.services.ventaService.InventarioRepository"
    ) as MockInvRepo, patch("app.Venta.services.ventaService.VentaRepository") as MockVentaRepo:
        MockClienteRepo.return_value.obtenerPorId.return_value = clienteMock
        MockCajaRepo.return_value.listarCajasHoy.return_value = [cajaMock]

        MockProductoRepo.return_value.validarProductoParaVenta.side_effect = [
            {"producto": productoCola, "precio": 2.5, "inventario": inventarioCola, "tieneIva": True},
            {"producto": productoJugo, "precio": 1.8, "inventario": inventarioJugo, "tieneIva": False},
        ]
        MockPromRepo.return_value.obtenerPromocionActivaMayorDescuento.side_effect = [None, promoJugo]
        MockParamRepo.return_value.validarClaveExistente.return_value = parametroIvaMock

        MockVentaRepo.return_value.crearVenta.return_value = ventaCreada
        MockInvRepo.return_value.obtenerPorProducto.side_effect = [inventarioCola, inventarioJugo]

        servicio = VentaService(dbSession=dbSessionMock)
        respuesta = servicio.crearVenta(ventaCrear, _tokenCajero())

        assert respuesta.success is True
        assert respuesta.data.totalPagar == 5.3
        assert respuesta.data.totalIVA == 0.36
        assert respuesta.data.totalDescuento == 1.16
        # Verifica que se intentó deducir inventario
        assert dbSessionMock.add.call_count >= 1


def testCrearVentaFallaSiNoHayCajaHoy():
    """Prueba: crearVenta lanza 400 si el usuario no abrió caja hoy."""
    dbSessionMock = MagicMock()

    ventaCrear = VentaCrearSchema(
        idCliente=1,
        metodoPago="Efectivo",
        descuentoGeneral=0.0,
        detalles=[DetalleVentaCrearSchema(idProducto=1, cantidadComprada=1)],
    )

    with patch("app.Venta.services.ventaService.ClienteRepository") as MockClienteRepo, patch(
        "app.Venta.services.ventaService.CajaRepository"
    ) as MockCajaRepo:
        MockClienteRepo.return_value.obtenerPorId.return_value = _clienteMariaMock()
        MockCajaRepo.return_value.listarCajasHoy.return_value = []

        servicio = VentaService(dbSession=dbSessionMock)
        with pytest.raises(HTTPException) as excinfo:
            servicio.crearVenta(ventaCrear, _tokenCajero())
        assert excinfo.value.status_code == 400
        assert "No se ha abierto una caja" in str(excinfo.value.detail)


def testCrearVentaFallaSiCajaEstaCerrada():
    """Prueba: crearVenta lanza 400 si hay cajas hoy pero ninguna está ABIERTA."""
    dbSessionMock = MagicMock()

    tzQuito = _quitoTZ()
    ahora = datetime.now(tzQuito).replace(microsecond=0)
    cajaCerrada = crearCajaHistorialMock(
        idCaja=2,
        idUsuarioCaja=3,
        fechaAperturaCaja=ahora - timedelta(hours=2),
        fechaCierreCaja=ahora - timedelta(hours=1),
        montoInicialDeclarado=10.0,
        montoCierreDeclarado=15.0,
        montoCierreSistema=15.0,
        diferenciaCaja=0.0,
        estadoCaja="CERRADA",
        detalle="Cierre por 3-cajero",
        usuario=_usuarioCajeroMock(),
    )

    ventaCrear = VentaCrearSchema(
        idCliente=1,
        metodoPago="Efectivo",
        descuentoGeneral=0.0,
        detalles=[DetalleVentaCrearSchema(idProducto=1, cantidadComprada=1)],
    )

    with patch("app.Venta.services.ventaService.ClienteRepository") as MockClienteRepo, patch(
        "app.Venta.services.ventaService.CajaRepository"
    ) as MockCajaRepo:
        MockClienteRepo.return_value.obtenerPorId.return_value = _clienteMariaMock()
        MockCajaRepo.return_value.listarCajasHoy.return_value = [cajaCerrada]

        servicio = VentaService(dbSession=dbSessionMock)
        with pytest.raises(HTTPException) as excinfo:
            servicio.crearVenta(ventaCrear, _tokenCajero())
        assert excinfo.value.status_code == 400
        assert "caja ya está cerrada" in str(excinfo.value.detail).lower()


def testListarVentasHoyDevuelveVaciaSiNoHayDatos():
    """Prueba: listarVentasHoy devuelve [] si el repositorio no retorna ventas."""
    dbSessionMock = MagicMock()

    with patch("app.Venta.services.ventaService.VentaRepository") as MockRepo:
        MockRepo.return_value.listarVentasHoy.return_value = []

        servicio = VentaService(dbSession=dbSessionMock)
        respuesta = servicio.listarVentasHoy(_tokenAdmin())

        assert respuesta.success is True
        assert respuesta.data == []
        assert respuesta.message == "No se encontraron ventas para hoy"


def testListarVentasHoyDevuelveVentasEncontradasSerializadas():
    """Prueba: listarVentasHoy devuelve Ventas encontradas y serializa con from_orm."""
    dbSessionMock = MagicMock()

    tzQuito = _quitoTZ()
    fechaVenta = datetime.now(tzQuito).replace(microsecond=0)
    ventaMock = crearVentaMock(
        idVenta=3,
        idCaja=2,
        idUsuarioVenta=3,
        idCliente=1,
        fechaVenta=fechaVenta,
        subtotalVenta=6.1,
        descuentoGeneral=5.0,
        totalDescuento=1.16,
        baseIVA=15.0,
        totalIVA=0.36,
        totalPagar=5.3,
        metodoPago="Efectivo",
        estadoVenta="COMPLETADA",
        usuario=_usuarioCajeroMock(),
        cliente=_clienteMariaMock(),
        detalles=[],
    )

    with patch("app.Venta.services.ventaService.VentaRepository") as MockRepo:
        MockRepo.return_value.listarVentasHoy.return_value = [ventaMock]

        servicio = VentaService(dbSession=dbSessionMock)
        respuesta = servicio.listarVentasHoy(_tokenAdmin())

        MockRepo.return_value.listarVentasHoy.assert_called_once_with(None, True)
        assert respuesta.success is True
        assert respuesta.message == "Ventas encontradas"
        assert isinstance(respuesta.data, list)
        assert len(respuesta.data) == 1
        assert respuesta.data[0].idVenta == 3
        assert respuesta.data[0].totalPagar == 5.3


def testListarHistoricoNoAdminLanza403():
    """Prueba: listarHistorico lanza 403 si el rol no es Administrador."""
    dbSessionMock = MagicMock()

    servicio = VentaService(dbSession=dbSessionMock)
    with pytest.raises(HTTPException) as excinfo:
        servicio.listarHistorico(_tokenCajero())
    assert excinfo.value.status_code == 403


def testListarHistoricoAdminDevuelveVaciaSiNoHayVentas():
    """Prueba: listarHistorico (Administrador) devuelve [] si no hay ventas."""
    dbSessionMock = MagicMock()

    with patch("app.Venta.services.ventaService.VentaRepository") as MockRepo:
        MockRepo.return_value.listarTodas.return_value = []

        servicio = VentaService(dbSession=dbSessionMock)
        respuesta = servicio.listarHistorico(_tokenAdmin())

        MockRepo.return_value.listarTodas.assert_called_once_with()
        assert respuesta.success is True
        assert respuesta.message == "No se encontraron ventas"
        assert respuesta.data == []


def testListarHistoricoAdminDevuelveVentasEncontradasSerializadas():
    """Prueba: listarHistorico (Administrador) devuelve Ventas encontradas y serializa con from_orm."""
    dbSessionMock = MagicMock()

    tzQuito = _quitoTZ()
    fechaVenta = datetime.now(tzQuito).replace(microsecond=0)
    ventaMock = crearVentaMock(
        idVenta=8,
        idCaja=2,
        idUsuarioVenta=3,
        idCliente=1,
        fechaVenta=fechaVenta,
        subtotalVenta=6.1,
        descuentoGeneral=5.0,
        totalDescuento=1.16,
        baseIVA=15.0,
        totalIVA=0.36,
        totalPagar=5.3,
        metodoPago="Efectivo",
        estadoVenta="COMPLETADA",
        usuario=_usuarioCajeroMock(),
        cliente=_clienteMariaMock(),
        detalles=[],
    )

    with patch("app.Venta.services.ventaService.VentaRepository") as MockRepo:
        MockRepo.return_value.listarTodas.return_value = [ventaMock]

        servicio = VentaService(dbSession=dbSessionMock)
        respuesta = servicio.listarHistorico(_tokenAdmin())

        MockRepo.return_value.listarTodas.assert_called_once_with()
        assert respuesta.success is True
        assert respuesta.message == "Ventas encontradas"
        assert isinstance(respuesta.data, list)
        assert len(respuesta.data) == 1
        assert respuesta.data[0].idVenta == 8
        assert respuesta.data[0].cliente.nombreCliente == "María Gómez"


def testAnularVentaNoEncontradaLanza404():
    """Prueba: anularVenta lanza 404 si la venta no existe."""
    dbSessionMock = MagicMock()

    with patch("app.Venta.services.ventaService.VentaRepository") as MockRepo:
        MockRepo.return_value.obtenerPorId.return_value = None

        servicio = VentaService(dbSession=dbSessionMock)
        with pytest.raises(HTTPException) as excinfo:
            servicio.anularVenta(999, _tokenAdmin())
        assert excinfo.value.status_code == 404


def testAnularVentaExitosoAdministradorMismoDia():
    """Prueba: anularVenta (Administrador) anula venta del día actual y devuelve success=True."""
    dbSessionMock = MagicMock()

    tzQuito = _quitoTZ()
    fechaVenta = datetime.now(tzQuito).replace(microsecond=0)

    ventaMock = crearVentaMock(
        idVenta=1,
        idCaja=2,
        idUsuarioVenta=3,
        idCliente=1,
        fechaVenta=fechaVenta,
        subtotalVenta=6.1,
        descuentoGeneral=5.0,
        totalDescuento=1.16,
        baseIVA=15.0,
        totalIVA=0.36,
        totalPagar=5.3,
        metodoPago="Efectivo",
        estadoVenta="COMPLETADA",
        usuario=_usuarioCajeroMock(),
        cliente=_clienteMariaMock(),
        detalles=[],
    )

    ventaAnulada = crearVentaMock(
        idVenta=1,
        idCaja=2,
        idUsuarioVenta=3,
        idCliente=1,
        fechaVenta=fechaVenta,
        subtotalVenta=6.1,
        descuentoGeneral=5.0,
        totalDescuento=1.16,
        baseIVA=15.0,
        totalIVA=0.36,
        totalPagar=5.3,
        metodoPago="Efectivo",
        estadoVenta="ANULADA",
        usuario=_usuarioCajeroMock(),
        cliente=_clienteMariaMock(),
        detalles=[],
    )

    with patch("app.Venta.services.ventaService.VentaRepository") as MockRepo:
        MockRepo.return_value.obtenerPorId.return_value = ventaMock
        MockRepo.return_value.anularVenta.return_value = ventaAnulada

        servicio = VentaService(dbSession=dbSessionMock)
        respuesta = servicio.anularVenta(1, _tokenAdmin())

        assert respuesta.success is True
        assert respuesta.data.estadoVenta == "ANULADA"


def testGenerarComprobanteVentaNoEncontradaLanza404():
    """Prueba: generarComprobanteVenta lanza 404 si la venta no existe."""
    dbSessionMock = MagicMock()

    with patch("app.Venta.services.ventaService.VentaRepository") as MockRepo:
        MockRepo.return_value.obtenerPorId.return_value = None

        servicio = VentaService(dbSession=dbSessionMock)
        with pytest.raises(HTTPException) as excinfo:
            servicio.generarComprobanteVenta(999, _tokenAdmin())
        assert excinfo.value.status_code == 404


def testGenerarComprobanteVentaDevuelveParametrosYVenta():
    """Prueba: generarComprobanteVenta devuelve parámetros del negocio y la venta serializada."""
    dbSessionMock = MagicMock()

    tzQuito = _quitoTZ()
    fechaVenta = datetime.now(tzQuito).replace(microsecond=0)

    ventaMock = crearVentaMock(
        idVenta=3,
        idCaja=2,
        idUsuarioVenta=3,
        idCliente=1,
        fechaVenta=fechaVenta,
        subtotalVenta=6.1,
        descuentoGeneral=5.0,
        totalDescuento=1.16,
        baseIVA=15.0,
        totalIVA=0.36,
        totalPagar=5.3,
        metodoPago="Efectivo",
        estadoVenta="COMPLETADA",
        usuario=_usuarioCajeroMock(),
        cliente=_clienteMariaMock(),
        detalles=[],
    )

    def parametro(clave, valor):
        p = MagicMock()
        p.claveParametro = clave
        p.valorParametro = valor
        return p

    with patch("app.Venta.services.ventaService.VentaRepository") as MockVentaRepo, patch(
        "app.Venta.services.ventaService.ParametroSistemaRepository"
    ) as MockParamRepo:
        MockVentaRepo.return_value.obtenerPorId.return_value = ventaMock

        # Simular que algunos parámetros existen y otros no
        MockParamRepo.return_value.validarClaveExistente.side_effect = [
            parametro("nombreNegocio", "DALCT Market"),
            parametro("direccionNegocio", "Quito"),
            parametro("telefonoNegocio", "0990000000"),
            parametro("correoNegocio", "contacto@dalct.com"),
        ]

        servicio = VentaService(dbSession=dbSessionMock)
        respuesta = servicio.generarComprobanteVenta(3, _tokenAdmin())

        assert respuesta.success is True
        assert respuesta.message == "Comprobante generado"
        assert "parametros" in respuesta.data
        assert "venta" in respuesta.data
