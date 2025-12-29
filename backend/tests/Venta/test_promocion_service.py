import pytest
from unittest.mock import patch
from fastapi import HTTPException

from datetime import datetime, timezone, timedelta, time

from app.Venta.services.promocionService import PromocionService
from app.Venta.schemas.promocionSchemas import PromocionCrearSchema

from tests.mocks_models.promocionMock import crearPromocionMock
from tests.mocks_models.productoMock import crearProductoMock
from tests.mocks_models.categoriaProductoMock import crearCategoriaProductoMock
from tests.mocks_models.proveedorMock import crearProveedorMock


def _quitoTZ():
    return timezone(timedelta(hours=-5))


def _hoyQuito():
    return datetime.now(_quitoTZ()).date()


def _horaActualQuito():
    return datetime.now(_quitoTZ()).time().replace(microsecond=0)


def _productoColaMock():
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
        idProducto=1,
        idCategoriaProducto=1,
        idProveedor=1,
        nombreProducto="Cola 2 Litros",
        descripcionProducto="Bebida gaseosa sabor cola",
        precioUnitarioVenta=2.50,
        precioUnitarioCompra=1.80,
        tieneIva=True,
        activoProducto=True,
        categoria=categoriaMock,
        proveedor=proveedorMock,
    )


def _productoJugoMock():
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
        idProducto=2,
        idCategoriaProducto=1,
        idProveedor=1,
        nombreProducto="Jugo de Naranja 1L",
        descripcionProducto="Jugo natural de naranja 1 litro",
        precioUnitarioVenta=2.20,
        precioUnitarioCompra=1.60,
        tieneIva=True,
        activoProducto=True,
        categoria=categoriaMock,
        proveedor=proveedorMock,
    )


def _tokenAdmin():
    return {"idUsuario": 1, "rol": "Administrador", "nombreCompleto": "admin"}


def _promocionPasadaMock():
    hoy = _hoyQuito()
    inicioPasado = hoy - timedelta(days=60)
    finPasado = hoy - timedelta(days=30)
    horaActual = _horaActualQuito()

    productoMock = _productoColaMock()
    return crearPromocionMock(
        idPromocion=1,
        idProducto=1,
        nombrePromocion="Promoción Pasada",
        porcentajePromocion=10.0,
        fechaInicioPromocion=datetime.combine(inicioPasado, horaActual, tzinfo=_quitoTZ()),
        fechaFinPromocion=datetime.combine(finPasado, time(23, 59, 59, microsecond=0), tzinfo=_quitoTZ()),
        activoPromocion=True,
        producto=productoMock,
    )


def _promocionActualMock():
    hoy = _hoyQuito()
    fin = hoy + timedelta(days=30)
    horaActual = _horaActualQuito()

    productoMock = _productoJugoMock()
    return crearPromocionMock(
        idPromocion=2,
        idProducto=2,
        nombrePromocion="Promoción Actual",
        porcentajePromocion=25.0,
        fechaInicioPromocion=datetime.combine(hoy, horaActual, tzinfo=_quitoTZ()),
        fechaFinPromocion=datetime.combine(fin, time(23, 59, 59, microsecond=0), tzinfo=_quitoTZ()),
        activoPromocion=True,
        producto=productoMock,
    )


def testListarPromocionesDevuelveListaVaciaSiNoHayDatos():
    """Prueba: listarPromociones devuelve data=[] si repositorio retorna lista vacía/None."""
    with patch("app.Venta.services.promocionService.PromocionRepository") as MockRepo:
        MockRepo.return_value.listarPromociones.return_value = []

        servicio = PromocionService(dbSession=None)
        respuesta = servicio.listarPromociones()

        assert respuesta.success is True
        assert respuesta.data == []


def testListarPromocionesDevuelveListaDePromociones():
    """Prueba: listarPromociones devuelve lista de promociones y mensaje correcto."""
    promoMock = _promocionActualMock()

    with patch("app.Venta.services.promocionService.PromocionRepository") as MockRepo:
        MockRepo.return_value.listarPromociones.return_value = [promoMock]

        servicio = PromocionService(dbSession=None)
        respuesta = servicio.listarPromociones()

        assert respuesta.success is True
        assert respuesta.message == "Promociones encontradas"
        assert isinstance(respuesta.data, list)
        assert len(respuesta.data) == 1
        assert respuesta.data[0].idPromocion == 2
        assert respuesta.data[0].producto.nombreProducto == "Jugo de Naranja 1L"


def testObtenerPromocionPorIdNoEncontradoLanza404():
    """Prueba: obtenerPorId lanza 404 si la promoción no existe."""
    with patch("app.Venta.services.promocionService.PromocionRepository") as MockRepo:
        MockRepo.return_value.obtenerPorId.return_value = None

        servicio = PromocionService(dbSession=None)
        with pytest.raises(HTTPException) as excinfo:
            servicio.obtenerPorId(999)
        assert excinfo.value.status_code == 404


def testObtenerPromocionPorIdExitoso():
    """Prueba: obtenerPorId devuelve la promoción y mensaje correcto."""
    promoMock = _promocionActualMock()

    with patch("app.Venta.services.promocionService.PromocionRepository") as MockRepo:
        MockRepo.return_value.obtenerPorId.return_value = promoMock

        servicio = PromocionService(dbSession=None)
        respuesta = servicio.obtenerPorId(1)

        assert respuesta.success is True
        assert respuesta.message == "Promoción encontrada"
        assert respuesta.data.idPromocion == 2
        assert respuesta.data.producto.idProducto == 2


def testCrearPromocionExitosoDevuelvePromocionCreadaFechasQuito():
    """Prueba: crearPromocion retorna 'Promoción creada' y respeta fechas válidas (Quito)."""
    hoy = _hoyQuito()
    fin = hoy + timedelta(days=30)

    promoCreadaMock = _promocionActualMock()

    with patch("app.Venta.services.promocionService.PromocionRepository") as MockRepo:
        MockRepo.return_value.crearPromocion.return_value = promoCreadaMock

        servicio = PromocionService(dbSession=None)
        promocionCrear = PromocionCrearSchema(
            idProducto=2,
            nombrePromocion="Promoción Actual",
            porcentajePromocion=25.0,
            fechaInicioPromocion=hoy,
            fechaFinPromocion=fin,
        )

        respuesta = servicio.crearPromocion(promocionCrear, _tokenAdmin())
        assert respuesta.success is True
        assert respuesta.message == "Promoción creada"
        assert respuesta.data.idPromocion == 2
        assert respuesta.data.producto.nombreProducto == "Jugo de Naranja 1L"


def testCrearPromocionProductoNoEncontradoLanza400():
    """Prueba: crearPromocion lanza 400 si el producto no existe."""
    hoy = _hoyQuito()
    fin = hoy + timedelta(days=30)

    with patch("app.Venta.services.promocionService.PromocionRepository") as MockRepo:
        MockRepo.return_value.crearPromocion.return_value = {"error": "producto_no_encontrado"}

        servicio = PromocionService(dbSession=None)
        promocionCrear = PromocionCrearSchema(
            idProducto=999,
            nombrePromocion="Promo",
            porcentajePromocion=10.0,
            fechaInicioPromocion=hoy,
            fechaFinPromocion=fin,
        )

        with pytest.raises(HTTPException) as excinfo:
            servicio.crearPromocion(promocionCrear, _tokenAdmin())
        assert excinfo.value.status_code == 400
        assert excinfo.value.detail == "Producto no encontrado"


def testCrearPromocionProductoInactivoLanza400():
    """Prueba: crearPromocion lanza 400 si el producto está inactivo."""
    hoy = _hoyQuito()
    fin = hoy + timedelta(days=30)

    with patch("app.Venta.services.promocionService.PromocionRepository") as MockRepo:
        MockRepo.return_value.crearPromocion.return_value = {"error": "producto_inactivo"}

        servicio = PromocionService(dbSession=None)
        promocionCrear = PromocionCrearSchema(
            idProducto=1,
            nombrePromocion="Promo",
            porcentajePromocion=10.0,
            fechaInicioPromocion=hoy,
            fechaFinPromocion=fin,
        )

        with pytest.raises(HTTPException) as excinfo:
            servicio.crearPromocion(promocionCrear, _tokenAdmin())
        assert excinfo.value.status_code == 400
        assert excinfo.value.detail == "Producto inactivo"


def testObtenerActivasPorProductoDevuelveListaVaciaSiNoHayDatos():
    """Prueba: obtenerActivasPorProducto devuelve data=[] si no hay promociones activas."""
    with patch("app.Venta.services.promocionService.PromocionRepository") as MockRepo:
        MockRepo.return_value.obtenerPromocionesActivasPorProducto.return_value = []

        servicio = PromocionService(dbSession=None)
        respuesta = servicio.obtenerActivasPorProducto(1)

        assert respuesta.success is True
        assert respuesta.data == []


def testObtenerActivasPorProductoDevuelveLista():
    """Prueba: obtenerActivasPorProducto devuelve promociones activas y mensaje correcto."""
    promoMock = _promocionActualMock()

    with patch("app.Venta.services.promocionService.PromocionRepository") as MockRepo:
        MockRepo.return_value.obtenerPromocionesActivasPorProducto.return_value = [promoMock]

        servicio = PromocionService(dbSession=None)
        respuesta = servicio.obtenerActivasPorProducto(2)

        assert respuesta.success is True
        assert respuesta.message == "Promociones activas encontradas"
        assert isinstance(respuesta.data, list)
        assert len(respuesta.data) == 1
        assert respuesta.data[0].producto.nombreProducto == "Jugo de Naranja 1L"


def testDeshabilitarPromocionNoEncontradaLanza404():
    """Prueba: deshabilitarPromocion lanza 404 si la promoción no existe."""
    with patch("app.Venta.services.promocionService.PromocionRepository") as MockRepo:
        MockRepo.return_value.deshabilitarPromocion.return_value = None

        servicio = PromocionService(dbSession=None)
        with pytest.raises(HTTPException) as excinfo:
            servicio.deshabilitarPromocion(999)
        assert excinfo.value.status_code == 404


def testDeshabilitarPromocionExitosoDevuelveDeshabilitada():
    """Prueba: deshabilitarPromocion retorna promoción deshabilitada y mensaje correcto."""
    promoDeshabilitadaMock = _promocionActualMock()
    promoDeshabilitadaMock.activoPromocion = False

    with patch("app.Venta.services.promocionService.PromocionRepository") as MockRepo:
        MockRepo.return_value.deshabilitarPromocion.return_value = promoDeshabilitadaMock

        servicio = PromocionService(dbSession=None)
        respuesta = servicio.deshabilitarPromocion(1)

        assert respuesta.success is True
        assert respuesta.message == "Promoción deshabilitada"
        assert respuesta.data.activoPromocion is False


def testObtenerPromocionAplicableNoHayDevuelveNone():
    """Prueba: obtenerPromocionAplicable devuelve data=None si no hay promociones aplicables."""
    with patch("app.Venta.services.promocionService.PromocionRepository") as MockRepo:
        MockRepo.return_value.obtenerPromocionActivaMayorDescuento.return_value = None

        servicio = PromocionService(dbSession=None)
        respuesta = servicio.obtenerPromocionAplicable(1)

        assert respuesta.success is True
        assert respuesta.data is None
        assert respuesta.message == "No hay promociones aplicables"


def testObtenerPromocionAplicableExitosoDevuelvePromocion():
    """Prueba: obtenerPromocionAplicable retorna promoción aplicable si existe."""
    promoMock = _promocionActualMock()

    with patch("app.Venta.services.promocionService.PromocionRepository") as MockRepo:
        MockRepo.return_value.obtenerPromocionActivaMayorDescuento.return_value = promoMock

        servicio = PromocionService(dbSession=None)
        respuesta = servicio.obtenerPromocionAplicable(1)

        assert respuesta.success is True
        assert respuesta.message == "Promoción aplicable"
        assert respuesta.data.porcentajePromocion == 25.0
