import pytest
from unittest.mock import MagicMock, patch
from fastapi import HTTPException

from datetime import datetime, timezone, timedelta, date

from app.Reportes.services.reporteService import ReporteService
from app.Reportes.schemas.reporteSchemas import (
    InventarioFiltro,
    VentasFiltro,
    ClientesFiltro,
)

from tests.mocks_models.inventarioMock import crearInventarioMock
from tests.mocks_models.productoMock import crearProductoMock
from tests.mocks_models.categoriaProductoMock import crearCategoriaProductoMock
from tests.mocks_models.proveedorMock import crearProveedorMock

from tests.mocks_models.cajaHistorialMock import crearCajaHistorialMock
from tests.mocks_models.usuarioMock import crearUsuarioMock
from tests.mocks_models.rolMock import crearRolMock

from tests.mocks_models.ventaMock import crearVentaMock
from tests.mocks_models.clienteMock import crearClienteMock


def _quitoTZ():
    return timezone(timedelta(hours=-5))


def _tokenAdmin():
    return {"idUsuario": 1, "rol": "Administrador", "nombreCompleto": "admin"}


def _tokenBodeguero():
    return {"idUsuario": 2, "rol": "Bodeguero", "nombreCompleto": "bodeguero"}


def _tokenCajero():
    return {"idUsuario": 3, "rol": "Cajero", "nombreCompleto": "cajero"}


def _usuarioCajeroMock():
    rolMock = crearRolMock(idRol=3, nombreRol="Cajero")
    return crearUsuarioMock(
        idUsuario=3,
        idRol=3,
        nombreCompleto="cajero",
        cedulaUsuario="cajero",
        emailUsuario="cajero@example.com",
        rol=rolMock,
    )


def _usuarioAdminMock():
    rolMock = crearRolMock(idRol=1, nombreRol="Administrador")
    return crearUsuarioMock(
        idUsuario=1,
        idRol=1,
        nombreCompleto="admin",
        cedulaUsuario="admin",
        emailUsuario="admin@example.com",
        rol=rolMock,
    )


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


def _ventaTotal53Mock(idVenta: int = 3, idCaja: int = 2):
    tzQuito = _quitoTZ()
    fechaVenta = datetime.now(tzQuito).replace(microsecond=0)
    return crearVentaMock(
        idVenta=idVenta,
        idCaja=idCaja,
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


def _ventaMockConTotal(totalPagar: float, idVenta: int, idCaja: int = 2):
    """Crea una venta mock mínima con un totalPagar específico (para tests de reportes)."""
    tzQuito = _quitoTZ()
    fechaVenta = datetime.now(tzQuito).replace(microsecond=0)
    return crearVentaMock(
        idVenta=idVenta,
        idCaja=idCaja,
        idUsuarioVenta=3,
        idCliente=1,
        fechaVenta=fechaVenta,
        subtotalVenta=float(totalPagar),
        descuentoGeneral=0.0,
        totalDescuento=0.0,
        baseIVA=0.0,
        totalIVA=0.0,
        totalPagar=float(totalPagar),
        metodoPago="Efectivo",
        estadoVenta="COMPLETADA",
        usuario=_usuarioCajeroMock(),
        cliente=_clienteMariaMock(),
        detalles=[],
    )


def testReporteInventarioProhibeCajero403():
    """Prueba: reporteInventario bloquea rol Cajero."""
    dbSessionMock = None
    servicio = ReporteService(dbSession=dbSessionMock)
    with pytest.raises(HTTPException) as excinfo:
        servicio.reporteInventario(InventarioFiltro(), _tokenCajero())
    assert excinfo.value.status_code == 403


def testReporteInventarioAdminDevuelveItemsConProductoCompleto():
    """Prueba: reporteInventario (Admin) serializa InventarioRespuestaSchema.from_orm con producto+categ+proveedor."""
    dbSessionMock = None

    categoriaBebidas = crearCategoriaProductoMock(idCategoriaProducto=1, nombreCategoria="Bebidas")
    proveedor = crearProveedorMock(idProveedor=1, razonSocial="Distribuidora Andina")

    cola = crearProductoMock(
        idProducto=1,
        idCategoriaProducto=1,
        idProveedor=1,
        nombreProducto="Cola 2 Litros",
        descripcionProducto="Bebida gaseosa sabor cola",
        precioUnitarioVenta=2.5,
        precioUnitarioCompra=1.8,
        tieneIva=True,
        activoProducto=True,
        categoria=categoriaBebidas,
        proveedor=proveedor,
    )
    jugo = crearProductoMock(
        idProducto=2,
        idCategoriaProducto=1,
        idProveedor=1,
        nombreProducto="Jugo de Naranja 1L",
        descripcionProducto="Jugo natural",
        precioUnitarioVenta=1.8,
        precioUnitarioCompra=1.6,
        tieneIva=False,
        activoProducto=True,
        categoria=categoriaBebidas,
        proveedor=proveedor,
    )

    invCola = crearInventarioMock(idInventario=1, idProducto=1, cantidadDisponible=10, cantidadMinima=1, activoInventario=True, producto=cola)
    invJugo = crearInventarioMock(idInventario=2, idProducto=2, cantidadDisponible=10, cantidadMinima=1, activoInventario=True, producto=jugo)

    with patch("app.Reportes.services.reporteService.ReporteRepository") as MockRepo:
        MockRepo.return_value.reporte_inventario.return_value = [invCola, invJugo]

        servicio = ReporteService(dbSession=dbSessionMock)
        respuesta = servicio.reporteInventario(InventarioFiltro(nombreProducto=""), _tokenAdmin())

        assert respuesta.success is True
        assert respuesta.message == "Reporte de inventario generado"
        assert hasattr(respuesta.data, "items")
        assert len(respuesta.data.items) == 2
        assert respuesta.data.items[0].producto.nombreProducto in ["Cola 2 Litros", "Jugo de Naranja 1L"]
        assert respuesta.data.items[0].producto.categoria.nombreCategoria == "Bebidas"


def testReporteInventarioBodegueroPermitido():
    """Prueba: reporteInventario permite rol Bodeguero."""
    dbSessionMock = None

    categoriaBebidas = crearCategoriaProductoMock(idCategoriaProducto=1, nombreCategoria="Bebidas")
    proveedor = crearProveedorMock(idProveedor=1, razonSocial="Distribuidora Andina")
    cola = crearProductoMock(
        idProducto=1,
        idCategoriaProducto=1,
        idProveedor=1,
        nombreProducto="Cola 2 Litros",
        descripcionProducto="Bebida gaseosa",
        precioUnitarioVenta=2.5,
        precioUnitarioCompra=1.8,
        tieneIva=True,
        activoProducto=True,
        categoria=categoriaBebidas,
        proveedor=proveedor,
    )
    invCola = crearInventarioMock(idInventario=1, idProducto=1, cantidadDisponible=10, cantidadMinima=1, activoInventario=True, producto=cola)

    with patch("app.Reportes.services.reporteService.ReporteRepository") as MockRepo:
        MockRepo.return_value.reporte_inventario.return_value = [invCola]

        servicio = ReporteService(dbSession=dbSessionMock)
        respuesta = servicio.reporteInventario(InventarioFiltro(idCategoria=1), _tokenBodeguero())

        assert respuesta.success is True
        assert len(respuesta.data.items) == 1


def testReporteVentasProductoCategoriaValidaRolAdmin403():
    """Prueba: reporteVentasProductoCategoria requiere rol Administrador."""
    dbSessionMock = None
    servicio = ReporteService(dbSession=dbSessionMock)

    with pytest.raises(HTTPException) as excinfo:
        servicio.reporteVentasProductoCategoria(
            VentasFiltro(fechaInicio=date.today(), fechaFin=date.today(), idProducto=1),
            _tokenCajero(),
        )
    assert excinfo.value.status_code == 403


def testReporteVentasProductoCategoriaRequiereProductoOCategoria400():
    """Prueba: reporteVentasProductoCategoria exige idProducto o idCategoria."""
    dbSessionMock = None
    servicio = ReporteService(dbSession=dbSessionMock)

    with pytest.raises(HTTPException) as excinfo:
        servicio.reporteVentasProductoCategoria(
            VentasFiltro(fechaInicio=date.today(), fechaFin=date.today(), idProducto=None, idCategoria=None),
            _tokenAdmin(),
        )
    assert excinfo.value.status_code == 400


def testReporteVentasProductoCategoriaFaltaFechaInicioFin400():
    """Prueba: reporteVentasProductoCategoria lanza 400 si faltan fechaInicio/fechaFin.
    """
    dbSessionMock = None
    servicio = ReporteService(dbSession=dbSessionMock)

    filtroMock = MagicMock()
    filtroMock.fechaInicio = None
    filtroMock.fechaFin = None
    filtroMock.idProducto = 1
    filtroMock.idCategoria = None

    with pytest.raises(HTTPException) as excinfo:
        servicio.reporteVentasProductoCategoria(filtroMock, _tokenAdmin())
    assert excinfo.value.status_code == 400
    assert "fechaInicio y fechaFin son obligatorias" in str(excinfo.value.detail)


def testReporteVentasProductoCategoriaDevuelveItems():
    """Prueba: reporteVentasProductoCategoria construye items desde filas repo (ej. Cola/Jugo)."""
    dbSessionMock = None

    filaCola = MagicMock()
    filaCola.idProducto = 1
    filaCola.nombreProducto = "Cola 2 Litros"
    filaCola.idCategoriaProducto = 1
    filaCola.nombreCategoria = "Bebidas"
    filaCola.cantidadVendida = 1
    filaCola.ingresos = 2.5

    filaJugo = MagicMock()
    filaJugo.idProducto = 2
    filaJugo.nombreProducto = "Jugo de Naranja 1L"
    filaJugo.idCategoriaProducto = 1
    filaJugo.nombreCategoria = "Bebidas"
    filaJugo.cantidadVendida = 2
    # ingresos netos (con promo 25%): 3.6 - 0.9 = 2.7
    filaJugo.ingresos = 2.7

    filtro = VentasFiltro(
        fechaInicio=date.today() - timedelta(days=1),
        fechaFin=date.today(),
        idCategoria=1,
        idProducto=None,
    )

    with patch("app.Reportes.services.reporteService.ReporteRepository") as MockRepo:
        MockRepo.return_value.reporte_ventas_por_producto_categoria.return_value = [filaCola, filaJugo]

        servicio = ReporteService(dbSession=dbSessionMock)
        respuesta = servicio.reporteVentasProductoCategoria(filtro, _tokenAdmin())

        assert respuesta.success is True
        assert respuesta.message == "Reporte de ventas por producto/categoría generado"
        assert len(respuesta.data.items) == 2
        assert respuesta.data.items[0].nombreCategoria == "Bebidas"


def testResumenCajaDiariaNoAdmin403():
    """Prueba: resumenCajaDiaria requiere rol Administrador."""
    dbSessionMock = None
    servicio = ReporteService(dbSession=dbSessionMock)

    with pytest.raises(HTTPException) as excinfo:
        servicio.resumenCajaDiaria(date.today(), 3, _tokenCajero())
    assert excinfo.value.status_code == 403


def testResumenCajaDiariaRequiereIdUsuarioCaja400():
    """Prueba: resumenCajaDiaria requiere idUsuarioCaja."""
    dbSessionMock = None
    servicio = ReporteService(dbSession=dbSessionMock)

    with pytest.raises(HTTPException) as excinfo:
        servicio.resumenCajaDiaria(date.today(), None, _tokenAdmin())
    assert excinfo.value.status_code == 400


def testResumenCajaDiariaDevuelveCajaConVentasSerializadas():
    """Prueba: resumenCajaDiaria serializa UsuarioPublicoSchema y VentaRespuestaSchema en ventas."""
    dbSessionMock = None

    tzQuito = _quitoTZ()
    ahora = datetime.now(tzQuito).replace(microsecond=0)

    caja = crearCajaHistorialMock(
        idCaja=2,
        idUsuarioCaja=3,
        fechaAperturaCaja=ahora - timedelta(hours=3),
        fechaCierreCaja=ahora - timedelta(hours=1),
        montoInicialDeclarado=10.0,
        montoCierreDeclarado=15.3,
        montoCierreSistema=15.3,
        diferenciaCaja=0.0,
        estadoCaja="CERRADA",
        detalle="Cierre: cerrado por 3-cajero",
        usuario=_usuarioCajeroMock(),
    )
    caja.ventas = [_ventaTotal53Mock(idVenta=3, idCaja=2)]

    with patch("app.Reportes.services.reporteService.ReporteRepository") as MockRepo:
        MockRepo.return_value.resumen_caja_diaria.return_value = [caja]

        servicio = ReporteService(dbSession=dbSessionMock)
        respuesta = servicio.resumenCajaDiaria(date.today(), 3, _tokenAdmin())

        assert respuesta.success is True
        assert respuesta.message == "Resumen de caja generado"
        assert len(respuesta.data.items) == 1
        assert respuesta.data.items[0].idCaja == 2
        assert len(respuesta.data.items[0].ventas) == 1
        assert respuesta.data.items[0].ventas[0].totalPagar == 5.3


def testClientesFrecuentesNoAdmin403():
    """Prueba: clientesFrecuentes requiere rol Administrador."""
    dbSessionMock = None
    servicio = ReporteService(dbSession=dbSessionMock)

    with pytest.raises(HTTPException) as excinfo:
        servicio.clientesFrecuentes(ClientesFiltro(), _tokenCajero())
    assert excinfo.value.status_code == 403


def testClientesFrecuentesDevuelveItemsConHistorialVentas():
    """Prueba: clientesFrecuentes arma items desde dict repo (cliente + historial)."""
    dbSessionMock = None

    cliente = _clienteMariaMock()
    # 3 ventas para que el historial sea consistente con ventasCount=3 y totalGastado=120.5
    # 5.3 + 55.0 + 60.2 = 120.5
    historial = [
        _ventaTotal53Mock(idVenta=3, idCaja=2),
        _ventaMockConTotal(totalPagar=55.0, idVenta=4, idCaja=2),
        _ventaMockConTotal(totalPagar=60.2, idVenta=5, idCaja=2),
    ]

    fila = {"cliente": cliente, "ventasCount": 3, "totalGastado": 120.5, "historial": historial}

    with patch("app.Reportes.services.reporteService.ReporteRepository") as MockRepo:
        MockRepo.return_value.clientes_frecuentes.return_value = [fila]

        servicio = ReporteService(dbSession=dbSessionMock)
        respuesta = servicio.clientesFrecuentes(ClientesFiltro(dias=30, minVentas=3, minGasto=100.0), _tokenAdmin())
        assert respuesta.success is True
        assert respuesta.message == "Reporte de clientes frecuentes generado"
        assert len(respuesta.data.items) == 1
        assert respuesta.data.items[0].cliente.nombreCliente == "María Gómez"
        assert respuesta.data.items[0].ventasCount == 3
        assert len(respuesta.data.items[0].historialVentas) == 3

        totalesHistorial = [v.totalPagar for v in respuesta.data.items[0].historialVentas]
        assert round(sum(totalesHistorial), 2) == 120.5
        assert sorted(totalesHistorial) == [5.3, 55.0, 60.2]
