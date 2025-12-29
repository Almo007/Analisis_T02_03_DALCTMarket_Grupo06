import pytest
from unittest.mock import patch
from fastapi import HTTPException

from app.Inventario.services.inventarioService import InventarioService
from app.Inventario.schemas.inventarioSchemas import InventarioCrearSchema, InventarioActualizarSchema

from tests.mocks_models.inventarioMock import crearInventarioMock
from tests.mocks_models.productoMock import crearProductoMock
from tests.mocks_models.categoriaProductoMock import crearCategoriaProductoMock
from tests.mocks_models.proveedorMock import crearProveedorMock


def _productoBaseMock():
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


def _tokenAdmin():
    return {"idUsuario": 1, "rol": "Administrador", "nombreCompleto": "Admin"}


def _tokenBodeguero():
    return {"idUsuario": 2, "rol": "Bodeguero", "nombreCompleto": "Bodeguero"}


def testListarInventariosDevuelveListaVaciaSiNoHayDatos():
    """Prueba: listarInventarios devuelve data=[] si no existen inventarios (repositorio retorna None)."""
    with patch("app.Inventario.services.inventarioService.InventarioRepository") as MockRepo:
        MockRepo.return_value.listarInventarios.return_value = None

        servicio = InventarioService(dbSession=None)
        respuesta = servicio.listarInventarios()

        assert respuesta.success is True
        assert respuesta.data == []


def testListarInventariosDevuelveListaSerializada():
    """Prueba: listarInventarios serializa InventarioRespuestaSchema.from_orm y retorna 'Inventarios encontrados'."""
    productoMock = _productoBaseMock()
    invCola = crearInventarioMock(
        idInventario=1,
        idProducto=1,
        cantidadDisponible=50,
        cantidadMinima=10,
        activoInventario=True,
        producto=productoMock,
    )
    invCola2 = crearInventarioMock(
        idInventario=2,
        idProducto=1,
        cantidadDisponible=5,
        cantidadMinima=1,
        activoInventario=True,
        producto=productoMock,
    )

    with patch("app.Inventario.services.inventarioService.InventarioRepository") as MockRepo:
        MockRepo.return_value.listarInventarios.return_value = [invCola, invCola2]

        servicio = InventarioService(dbSession=None)
        respuesta = servicio.listarInventarios()

        assert respuesta.success is True
        assert respuesta.message == "Inventarios encontrados"
        assert isinstance(respuesta.data, list)
        assert len(respuesta.data) == 2
        assert respuesta.data[0].idInventario == 1
        assert respuesta.data[0].producto.nombreProducto == "Cola 2 Litros"
        assert respuesta.data[0].producto.categoria.nombreCategoria == "Bebidas"


def testObtenerInventarioPorIdNoEncontradoLanza404():
    """Prueba: obtenerPorId lanza 404 si el inventario no existe."""
    with patch("app.Inventario.services.inventarioService.InventarioRepository") as MockRepo:
        MockRepo.return_value.obtenerPorId.return_value = None

        servicio = InventarioService(dbSession=None)
        with pytest.raises(HTTPException) as excinfo:
            servicio.obtenerPorId(999)
        assert excinfo.value.status_code == 404


def testObtenerInventarioPorIdExitosoDevuelveInventarioEncontradoSerializado():
    """Prueba: obtenerPorId serializa InventarioRespuestaSchema.from_orm y retorna 'Inventario encontrado'."""
    productoMock = _productoBaseMock()
    inventarioMock = crearInventarioMock(
        idInventario=10,
        idProducto=1,
        cantidadDisponible=12,
        cantidadMinima=3,
        activoInventario=True,
        producto=productoMock,
    )

    with patch("app.Inventario.services.inventarioService.InventarioRepository") as MockRepo:
        MockRepo.return_value.obtenerPorId.return_value = inventarioMock

        servicio = InventarioService(dbSession=None)
        respuesta = servicio.obtenerPorId(10)

        assert respuesta.success is True
        assert respuesta.message == "Inventario encontrado"
        assert respuesta.data.idInventario == 10
        assert respuesta.data.producto.nombreProducto == "Cola 2 Litros"


def testObtenerInventarioPorProductoNoEncontradoLanza404():
    """Prueba: obtenerPorProducto lanza 404 si no existe inventario para el producto."""
    with patch("app.Inventario.services.inventarioService.InventarioRepository") as MockRepo:
        MockRepo.return_value.obtenerPorProducto.return_value = None

        servicio = InventarioService(dbSession=None)
        with pytest.raises(HTTPException) as excinfo:
            servicio.obtenerPorProducto(999)
        assert excinfo.value.status_code == 404


def testObtenerInventarioPorProductoExitosoDevuelveInventarioEncontradoSerializado():
    """Prueba: obtenerPorProducto serializa InventarioRespuestaSchema.from_orm y retorna 'Inventario encontrado'."""
    productoMock = _productoBaseMock()
    inventarioMock = crearInventarioMock(
        idInventario=11,
        idProducto=1,
        cantidadDisponible=25,
        cantidadMinima=5,
        activoInventario=True,
        producto=productoMock,
    )

    with patch("app.Inventario.services.inventarioService.InventarioRepository") as MockRepo:
        MockRepo.return_value.obtenerPorProducto.return_value = inventarioMock

        servicio = InventarioService(dbSession=None)
        respuesta = servicio.obtenerPorProducto(1)

        assert respuesta.success is True
        assert respuesta.message == "Inventario encontrado"
        assert respuesta.data.idInventario == 11
        assert respuesta.data.producto.nombreProducto == "Cola 2 Litros"


def testCrearInventarioDevuelveExistenteSiYaExisteIdempotente():
    """Prueba: crearInventario retorna 200 e 'Inventario existente' si ya existe inventario del producto."""
    productoMock = _productoBaseMock()
    inventarioExistenteMock = crearInventarioMock(
        idInventario=1,
        idProducto=1,
        cantidadDisponible=50,
        cantidadMinima=10,
        activoInventario=True,
        producto=productoMock,
    )

    with patch("app.Inventario.services.inventarioService.InventarioRepository") as MockRepo:
        instanciaRepo = MockRepo.return_value
        instanciaRepo.obtenerPorProducto.return_value = inventarioExistenteMock

        servicio = InventarioService(dbSession=None)
        inventarioCrear = InventarioCrearSchema(idProducto=1, cantidadDisponible=50, cantidadMinima=10)

        respuesta, status = servicio.crearInventario(inventarioCrear)
        assert status == 200
        assert respuesta.success is True
        assert respuesta.message == "Inventario existente"
        assert respuesta.data.idInventario == 1


def testCrearInventarioExitosoDevuelve201():
    """Prueba: crearInventario crea inventario si no existe y devuelve 201."""
    productoMock = _productoBaseMock()
    inventarioCreadoMock = crearInventarioMock(
        idInventario=1,
        idProducto=1,
        cantidadDisponible=50,
        cantidadMinima=10,
        activoInventario=True,
        producto=productoMock,
    )

    with patch("app.Inventario.services.inventarioService.InventarioRepository") as MockRepo:
        instanciaRepo = MockRepo.return_value
        instanciaRepo.obtenerPorProducto.return_value = None
        instanciaRepo.crearInventario.return_value = inventarioCreadoMock

        servicio = InventarioService(dbSession=None)
        inventarioCrear = InventarioCrearSchema(idProducto=1, cantidadDisponible=50, cantidadMinima=10)

        respuesta, status = servicio.crearInventario(inventarioCrear)
        assert status == 201
        assert respuesta.success is True
        assert respuesta.message == "Inventario creado"
        assert respuesta.data.cantidadDisponible == 50


def testCrearInventarioProductoNoExisteLanza400():
    """Prueba: crearInventario lanza 400 si el producto no existe."""
    with patch("app.Inventario.services.inventarioService.InventarioRepository") as MockRepo:
        instanciaRepo = MockRepo.return_value
        instanciaRepo.obtenerPorProducto.return_value = None
        instanciaRepo.crearInventario.return_value = {"error": ["producto"]}

        servicio = InventarioService(dbSession=None)
        inventarioCrear = InventarioCrearSchema(idProducto=999, cantidadDisponible=10, cantidadMinima=0)

        with pytest.raises(HTTPException) as excinfo:
            servicio.crearInventario(inventarioCrear)
        assert excinfo.value.status_code == 400


def testCrearInventarioProductoDeshabilitadoLanza400():
    """Prueba: crearInventario lanza 400 si el producto está deshabilitado (mapeo desde repo)."""
    with patch("app.Inventario.services.inventarioService.InventarioRepository") as MockRepo:
        instanciaRepo = MockRepo.return_value
        instanciaRepo.obtenerPorProducto.return_value = None
        instanciaRepo.crearInventario.return_value = {"error": ["producto_inactiva"]}

        servicio = InventarioService(dbSession=None)
        inventarioCrear = InventarioCrearSchema(idProducto=1, cantidadDisponible=10, cantidadMinima=0)

        with pytest.raises(HTTPException) as excinfo:
            servicio.crearInventario(inventarioCrear)
        assert excinfo.value.status_code == 400
        assert excinfo.value.detail == "Producto deshabilitado"


def testModificarInventarioBodegueroNoPuedeCambiarCantidadDisponibleLanza403():
    """Prueba: modificarInventario lanza 403 si rol=Bodeguero intenta cambiar cantidadDisponible."""
    with patch("app.Inventario.services.inventarioService.InventarioRepository") as MockRepo:
        MockRepo.return_value.modificarInventario.return_value = None

        servicio = InventarioService(dbSession=None)
        inventarioActualizar = InventarioActualizarSchema(cantidadDisponible=999)

        with pytest.raises(HTTPException) as excinfo:
            servicio.modificarInventario(1, inventarioActualizar, _tokenBodeguero())
        assert excinfo.value.status_code == 403


def testModificarInventarioNoEncontradoLanza404():
    """Prueba: modificarInventario lanza 404 si el inventario no existe."""
    with patch("app.Inventario.services.inventarioService.InventarioRepository") as MockRepo:
        MockRepo.return_value.modificarInventario.return_value = None

        servicio = InventarioService(dbSession=None)
        inventarioActualizar = InventarioActualizarSchema(cantidadMinima=5)

        with pytest.raises(HTTPException) as excinfo:
            servicio.modificarInventario(999, inventarioActualizar, _tokenAdmin())
        assert excinfo.value.status_code == 404


def testModificarInventarioExitosoDevuelveActualizadoSerializado():
    """Prueba: modificarInventario serializa InventarioRespuestaSchema.from_orm y retorna 'Inventario actualizado'."""
    productoMock = _productoBaseMock()
    inventarioActualizadoMock = crearInventarioMock(
        idInventario=1,
        idProducto=1,
        cantidadDisponible=50,
        cantidadMinima=8,
        activoInventario=True,
        producto=productoMock,
    )

    with patch("app.Inventario.services.inventarioService.InventarioRepository") as MockRepo:
        MockRepo.return_value.modificarInventario.return_value = inventarioActualizadoMock

        servicio = InventarioService(dbSession=None)
        inventarioActualizar = InventarioActualizarSchema(cantidadMinima=8)

        respuesta = servicio.modificarInventario(1, inventarioActualizar, _tokenAdmin())
        assert respuesta.success is True
        assert respuesta.message == "Inventario actualizado"
        assert respuesta.data.idInventario == 1
        assert respuesta.data.cantidadMinima == 8


def testDeshabilitarInventarioNoEncontradoLanza404():
    """Prueba: deshabilitarInventario lanza 404 si el inventario no existe."""
    with patch("app.Inventario.services.inventarioService.InventarioRepository") as MockRepo:
        MockRepo.return_value.deshabilitarInventario.return_value = None

        servicio = InventarioService(dbSession=None)
        with pytest.raises(HTTPException) as excinfo:
            servicio.deshabilitarInventario(999)
        assert excinfo.value.status_code == 404


def testDeshabilitarInventarioProductoHabilitadoLanza400():
    """Prueba: deshabilitarInventario lanza 400 si el producto aún está habilitado (repo retorna False)."""
    with patch("app.Inventario.services.inventarioService.InventarioRepository") as MockRepo:
        MockRepo.return_value.deshabilitarInventario.return_value = False

        servicio = InventarioService(dbSession=None)
        with pytest.raises(HTTPException) as excinfo:
            servicio.deshabilitarInventario(1)
        assert excinfo.value.status_code == 400


def testDeshabilitarInventarioExitosoDevuelveInventarioDeshabilitadoSerializado():
    """Prueba: deshabilitarInventario serializa InventarioRespuestaSchema.from_orm y retorna 'Inventario deshabilitado'."""
    productoMock = _productoBaseMock()
    inventarioDeshabilitadoMock = crearInventarioMock(
        idInventario=1,
        idProducto=1,
        cantidadDisponible=0,
        cantidadMinima=0,
        activoInventario=False,
        producto=productoMock,
    )

    with patch("app.Inventario.services.inventarioService.InventarioRepository") as MockRepo:
        MockRepo.return_value.deshabilitarInventario.return_value = inventarioDeshabilitadoMock

        servicio = InventarioService(dbSession=None)
        respuesta = servicio.deshabilitarInventario(1)

        assert respuesta.success is True
        assert respuesta.message == "Inventario deshabilitado"
        assert respuesta.data.idInventario == 1
        assert respuesta.data.activoInventario is False
