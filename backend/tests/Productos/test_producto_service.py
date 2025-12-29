import pytest
from unittest.mock import patch
from fastapi import HTTPException

from app.Productos.services.productoService import ProductoService
from app.Productos.schemas.productoSchemas import ProductoCrearSchema, ProductoActualizarSchema

from tests.mocks_models.productoMock import crearProductoMock
from tests.mocks_models.categoriaProductoMock import crearCategoriaProductoMock
from tests.mocks_models.proveedorMock import crearProveedorMock


def _productoBaseMock(
    idProducto: int = 1,
    activoProducto: bool = True,
    idCategoriaProducto: int = 1,
    idProveedor: int = 1,
    nombreProducto: str = "Cola 2 Litros",
):
    """Crea un Producto mock con categoria y proveedor para soportar ProductoRespuestaSchema.from_orm."""
    categoriaMock = crearCategoriaProductoMock(idCategoriaProducto=idCategoriaProducto, nombreCategoria="Bebidas", activoCategoria=True)
    proveedorMock = crearProveedorMock(
        idProveedor=idProveedor,
        razonSocial="Distribuidora Andina de Bebidas S.A.",
        ruc="1790012345001",
        direccionProveedor="Av. Maldonado y Morán Valverde, Quito",
        telefonoProveedor="0991234567",
        emailProveedor="ventas@andinabebidas.com",
        activoProveedor=True,
    )

    return crearProductoMock(
        idProducto=idProducto,
        idCategoriaProducto=idCategoriaProducto,
        idProveedor=idProveedor,
        nombreProducto=nombreProducto,
        descripcionProducto="Bebida gaseosa sabor cola",
        precioUnitarioVenta=2.50,
        precioUnitarioCompra=1.80,
        tieneIva=True,
        activoProducto=activoProducto,
        categoria=categoriaMock,
        proveedor=proveedorMock,
    )


def testListarProductosDevuelveListaVaciaSiNoHayDatos():
    """Prueba: listarProductos devuelve data=[] si no existen productos (repositorio retorna None)."""
    with patch("app.Productos.services.productoService.ProductoRepository") as MockRepo:
        MockRepo.return_value.listarProductos.return_value = None

        servicio = ProductoService(dbSession=None)
        respuesta = servicio.listarProductos()

        assert respuesta.success is True
        assert respuesta.data == []


def testListarProductosDevuelveListaDeProductos():
    """Prueba: listarProductos devuelve lista de productos con categoria y proveedor (from_orm)."""
    productoMock = _productoBaseMock(idProducto=1, nombreProducto="Cola 2 Litros")

    with patch("app.Productos.services.productoService.ProductoRepository") as MockRepo:
        MockRepo.return_value.listarProductos.return_value = [productoMock]

        servicio = ProductoService(dbSession=None)
        respuesta = servicio.listarProductos()

        assert respuesta.success is True
        assert isinstance(respuesta.data, list)
        assert len(respuesta.data) == 1
        assert respuesta.data[0].idProducto == 1
        assert respuesta.data[0].categoria.nombreCategoria == "Bebidas"
        assert respuesta.data[0].proveedor.ruc == "1790012345001"


def testObtenerProductoPorIdNoEncontradoLanza404():
    """Prueba: obtenerPorId lanza 404 si el producto no existe."""
    with patch("app.Productos.services.productoService.ProductoRepository") as MockRepo:
        MockRepo.return_value.obtenerPorId.return_value = None

        servicio = ProductoService(dbSession=None)
        with pytest.raises(HTTPException) as excinfo:
            servicio.obtenerPorId(999)
        assert excinfo.value.status_code == 404
        assert excinfo.value.detail == "Producto no encontrado"


def testObtenerProductoPorIdExitoso():
    """Prueba: obtenerPorId retorna producto si existe (from_orm)."""
    productoMock = _productoBaseMock(idProducto=2, nombreProducto="Agua Mineral 600ml")

    with patch("app.Productos.services.productoService.ProductoRepository") as MockRepo:
        MockRepo.return_value.obtenerPorId.return_value = productoMock

        servicio = ProductoService(dbSession=None)
        respuesta = servicio.obtenerPorId(2)

        assert respuesta.success is True
        assert respuesta.data.idProducto == 2
        assert respuesta.data.nombreProducto == "Agua Mineral 600ml"


def testCrearProductoExitosoDevuelveProductoCreado():
    """Prueba: crearProducto retorna 'Producto creado' cuando repo devuelve producto."""
    productoCreadoMock = _productoBaseMock(idProducto=1, nombreProducto="Cola 2 Litros")

    with patch("app.Productos.services.productoService.ProductoRepository") as MockRepo:
        MockRepo.return_value.crearProducto.return_value = productoCreadoMock

        servicio = ProductoService(dbSession=None)
        productoCrear = ProductoCrearSchema(
            idCategoriaProducto=1,
            idProveedor=1,
            nombreProducto="Cola 2 Litros",
            descripcionProducto="Bebida gaseosa sabor cola",
            precioUnitarioVenta=2.50,
            precioUnitarioCompra=1.80,
            tieneIva=True,
        )

        respuesta = servicio.crearProducto(productoCrear)
        assert respuesta.success is True
        assert respuesta.message == "Producto creado"
        assert respuesta.data.idProducto == 1


def testCrearProductoExitosoConInventarioCreadoDevuelveMensajeEspecial():
    """Prueba: crearProducto retorna 'Producto e inventario creados' cuando repo devuelve (producto, True)."""
    productoCreadoMock = _productoBaseMock(idProducto=1, nombreProducto="Cola 2 Litros")

    with patch("app.Productos.services.productoService.ProductoRepository") as MockRepo:
        MockRepo.return_value.crearProducto.return_value = (productoCreadoMock, True)

        servicio = ProductoService(dbSession=None)
        productoCrear = ProductoCrearSchema(
            idCategoriaProducto=1,
            idProveedor=1,
            nombreProducto="Cola 2 Litros",
            descripcionProducto="Bebida gaseosa sabor cola",
            precioUnitarioVenta=2.50,
            precioUnitarioCompra=1.80,
            tieneIva=True,
            cantidadDisponible=50,
            cantidadMinima=10,
        )

        respuesta = servicio.crearProducto(productoCrear)
        assert respuesta.success is True
        assert respuesta.message == "Producto e inventario creados"
        assert respuesta.data.idProducto == 1


def testCrearProductoCategoriaYProveedorNoExistenLanza400():
    """Prueba: crearProducto lanza 400 si categoria y proveedor no existen (error combinado)."""
    with patch("app.Productos.services.productoService.ProductoRepository") as MockRepo:
        MockRepo.return_value.crearProducto.return_value = {"error": ["categoria", "proveedor"]}

        servicio = ProductoService(dbSession=None)
        productoCrear = ProductoCrearSchema(
            idCategoriaProducto=999,
            idProveedor=999,
            nombreProducto="Cola 2 Litros",
            descripcionProducto="Bebida gaseosa sabor cola",
            precioUnitarioVenta=2.50,
            precioUnitarioCompra=1.80,
            tieneIva=True,
        )

        with pytest.raises(HTTPException) as excinfo:
            servicio.crearProducto(productoCrear)
        assert excinfo.value.status_code == 400
        assert excinfo.value.detail == "Categoria y Proveedor no existen"


def testCrearProductoCategoriaNoExisteLanza400():
    """Prueba: crearProducto lanza 400 si la categoria no existe (mapeo desde repo)."""
    with patch("app.Productos.services.productoService.ProductoRepository") as MockRepo:
        MockRepo.return_value.crearProducto.return_value = {"error": ["categoria"]}

        servicio = ProductoService(dbSession=None)
        productoCrear = ProductoCrearSchema(
            idCategoriaProducto=999,
            idProveedor=1,
            nombreProducto="Cola 2 Litros",
            descripcionProducto="Bebida gaseosa sabor cola",
            precioUnitarioVenta=2.50,
            precioUnitarioCompra=1.80,
            tieneIva=True,
        )

        with pytest.raises(HTTPException) as excinfo:
            servicio.crearProducto(productoCrear)
        assert excinfo.value.status_code == 400
        assert excinfo.value.detail == "Categoria no existe"


def testCrearProductoProveedorNoExisteLanza400():
    """Prueba: crearProducto lanza 400 si el proveedor no existe (mapeo desde repo)."""
    with patch("app.Productos.services.productoService.ProductoRepository") as MockRepo:
        MockRepo.return_value.crearProducto.return_value = {"error": ["proveedor"]}

        servicio = ProductoService(dbSession=None)
        productoCrear = ProductoCrearSchema(
            idCategoriaProducto=1,
            idProveedor=999,
            nombreProducto="Cola 2 Litros",
            descripcionProducto="Bebida gaseosa sabor cola",
            precioUnitarioVenta=2.50,
            precioUnitarioCompra=1.80,
            tieneIva=True,
        )

        with pytest.raises(HTTPException) as excinfo:
            servicio.crearProducto(productoCrear)
        assert excinfo.value.status_code == 400
        assert excinfo.value.detail == "Proveedor no existe"


def testCrearProductoCategoriaInactivaLanza400():
    """Prueba: crearProducto lanza 400 si la categoria está inactiva (mapeo desde repo)."""
    with patch("app.Productos.services.productoService.ProductoRepository") as MockRepo:
        MockRepo.return_value.crearProducto.return_value = {"error": ["categoria_inactiva"]}

        servicio = ProductoService(dbSession=None)
        productoCrear = ProductoCrearSchema(
            idCategoriaProducto=1,
            idProveedor=1,
            nombreProducto="Cola 2 Litros",
            descripcionProducto="Bebida gaseosa sabor cola",
            precioUnitarioVenta=2.50,
            precioUnitarioCompra=1.80,
            tieneIva=True,
        )

        with pytest.raises(HTTPException) as excinfo:
            servicio.crearProducto(productoCrear)
        assert excinfo.value.status_code == 400
        assert excinfo.value.detail == "Categoria deshabilitada"


def testCrearProductoProveedorInactivoLanza400():
    """Prueba: crearProducto lanza 400 si el proveedor está inactivo (mapeo desde repo)."""
    with patch("app.Productos.services.productoService.ProductoRepository") as MockRepo:
        MockRepo.return_value.crearProducto.return_value = {"error": ["proveedor_inactiva"]}

        servicio = ProductoService(dbSession=None)
        productoCrear = ProductoCrearSchema(
            idCategoriaProducto=1,
            idProveedor=1,
            nombreProducto="Cola 2 Litros",
            descripcionProducto="Bebida gaseosa sabor cola",
            precioUnitarioVenta=2.50,
            precioUnitarioCompra=1.80,
            tieneIva=True,
        )

        with pytest.raises(HTTPException) as excinfo:
            servicio.crearProducto(productoCrear)
        assert excinfo.value.status_code == 400
        assert excinfo.value.detail == "Proveedor deshabilitado"


def testCrearProductoCantidadMinimaNegativaDesdeRepoLanza400():
    """Prueba: crearProducto mapea error de repo a mensaje de cantidadMinima negativa."""
    with patch("app.Productos.services.productoService.ProductoRepository") as MockRepo:
        MockRepo.return_value.crearProducto.return_value = {"error": ["cantidad_minima_negativa"]}

        servicio = ProductoService(dbSession=None)
        productoCrear = ProductoCrearSchema(
            idCategoriaProducto=1,
            idProveedor=1,
            nombreProducto="Cola 2 Litros",
            descripcionProducto="Bebida gaseosa sabor cola",
            precioUnitarioVenta=2.50,
            precioUnitarioCompra=1.80,
            tieneIva=True,
            cantidadDisponible=0,
            cantidadMinima=0,
        )

        with pytest.raises(HTTPException) as excinfo:
            servicio.crearProducto(productoCrear)
        assert excinfo.value.status_code == 400
        assert "cantidadMinima no puede ser negativa" in str(excinfo.value.detail)


def testCrearProductoConcatenacionMensajesConPuntoYComaLanza400():
    """Prueba: crearProducto concatena mensajes cuando hay múltiples errores del repo."""
    with patch("app.Productos.services.productoService.ProductoRepository") as MockRepo:
        MockRepo.return_value.crearProducto.return_value = {"error": ["categoria", "proveedor_inactiva"]}

        servicio = ProductoService(dbSession=None)
        productoCrear = ProductoCrearSchema(
            idCategoriaProducto=999,
            idProveedor=1,
            nombreProducto="Cola 2 Litros",
            descripcionProducto="Bebida gaseosa sabor cola",
            precioUnitarioVenta=2.50,
            precioUnitarioCompra=1.80,
            tieneIva=True,
        )

        with pytest.raises(HTTPException) as excinfo:
            servicio.crearProducto(productoCrear)
        assert excinfo.value.status_code == 400
        assert excinfo.value.detail == "Categoria no existe; Proveedor deshabilitado"


def testCrearProductoCantidadDisponibleNegativaDesdeRepoLanza400():
    """Prueba: crearProducto mapea error de repo a mensaje de cantidadDisponible negativa."""
    with patch("app.Productos.services.productoService.ProductoRepository") as MockRepo:
        MockRepo.return_value.crearProducto.return_value = {"error": ["cantidad_disponible_negativa"]}

        servicio = ProductoService(dbSession=None)
        productoCrear = ProductoCrearSchema(
            idCategoriaProducto=1,
            idProveedor=1,
            nombreProducto="Cola 2 Litros",
            descripcionProducto="Bebida gaseosa sabor cola",
            precioUnitarioVenta=2.50,
            precioUnitarioCompra=1.80,
            tieneIva=True,
            cantidadDisponible=0,
            cantidadMinima=0,
        )

        with pytest.raises(HTTPException) as excinfo:
            servicio.crearProducto(productoCrear)
        assert excinfo.value.status_code == 400
        assert "cantidadDisponible no puede ser negativa" in str(excinfo.value.detail)


def testCrearProductoRepoRetornaNoneLanza400():
    """Prueba: crearProducto lanza 400 si el repositorio retorna None."""
    with patch("app.Productos.services.productoService.ProductoRepository") as MockRepo:
        MockRepo.return_value.crearProducto.return_value = None

        servicio = ProductoService(dbSession=None)
        productoCrear = ProductoCrearSchema(
            idCategoriaProducto=1,
            idProveedor=1,
            nombreProducto="Cola 2 Litros",
            descripcionProducto="Bebida gaseosa sabor cola",
            precioUnitarioVenta=2.50,
            precioUnitarioCompra=1.80,
            tieneIva=True,
        )

        with pytest.raises(HTTPException) as excinfo:
            servicio.crearProducto(productoCrear)
        assert excinfo.value.status_code == 400
        assert excinfo.value.detail == "Error al crear producto"


def testModificarProductoNoEncontradoLanza404():
    """Prueba: modificarProducto lanza 404 si no existe el producto."""
    with patch("app.Productos.services.productoService.ProductoRepository") as MockRepo:
        MockRepo.return_value.modificarProducto.return_value = None

        servicio = ProductoService(dbSession=None)
        productoActualizar = ProductoActualizarSchema(nombreProducto="Cola 2 Litros")

        with pytest.raises(HTTPException) as excinfo:
            servicio.modificarProducto(999, productoActualizar)
        assert excinfo.value.status_code == 404
        assert excinfo.value.detail == "Producto no encontrado"


def testModificarProductoCategoriaDeshabilitadaLanza400():
    """Prueba: modificarProducto lanza 400 si categoria está deshabilitada (mapeo desde repo)."""
    with patch("app.Productos.services.productoService.ProductoRepository") as MockRepo:
        MockRepo.return_value.modificarProducto.return_value = {"error": ["categoria_inactiva"]}

        servicio = ProductoService(dbSession=None)
        productoActualizar = ProductoActualizarSchema(idCategoriaProducto=1)

        with pytest.raises(HTTPException) as excinfo:
            servicio.modificarProducto(1, productoActualizar)
        assert excinfo.value.status_code == 400
        assert "Categoria deshabilitada" in str(excinfo.value.detail)


def testModificarProductoProveedorDeshabilitadoLanza400():
    """Prueba: modificarProducto lanza 400 si proveedor está deshabilitado (mapeo desde repo)."""
    with patch("app.Productos.services.productoService.ProductoRepository") as MockRepo:
        MockRepo.return_value.modificarProducto.return_value = {"error": ["proveedor_inactiva"]}

        servicio = ProductoService(dbSession=None)
        productoActualizar = ProductoActualizarSchema(idProveedor=1)

        with pytest.raises(HTTPException) as excinfo:
            servicio.modificarProducto(1, productoActualizar)
        assert excinfo.value.status_code == 400
        assert excinfo.value.detail == "Proveedor deshabilitado"


def testModificarProductoCategoriaNoExisteLanza400():
    """Prueba: modificarProducto lanza 400 si la categoria no existe (mapeo desde repo)."""
    with patch("app.Productos.services.productoService.ProductoRepository") as MockRepo:
        MockRepo.return_value.modificarProducto.return_value = {"error": ["categoria"]}

        servicio = ProductoService(dbSession=None)
        productoActualizar = ProductoActualizarSchema(idCategoriaProducto=999)

        with pytest.raises(HTTPException) as excinfo:
            servicio.modificarProducto(1, productoActualizar)
        assert excinfo.value.status_code == 400
        assert excinfo.value.detail == "Categoria no existe"


def testModificarProductoProveedorNoExisteLanza400():
    """Prueba: modificarProducto lanza 400 si el proveedor no existe (mapeo desde repo)."""
    with patch("app.Productos.services.productoService.ProductoRepository") as MockRepo:
        MockRepo.return_value.modificarProducto.return_value = {"error": ["proveedor"]}

        servicio = ProductoService(dbSession=None)
        productoActualizar = ProductoActualizarSchema(idProveedor=999)

        with pytest.raises(HTTPException) as excinfo:
            servicio.modificarProducto(1, productoActualizar)
        assert excinfo.value.status_code == 400
        assert excinfo.value.detail == "Proveedor no existe"


def testModificarProductoCategoriaYProveedorNoExistenLanza400():
    """Prueba: modificarProducto lanza 400 si categoria y proveedor no existen (error combinado)."""
    with patch("app.Productos.services.productoService.ProductoRepository") as MockRepo:
        MockRepo.return_value.modificarProducto.return_value = {"error": ["categoria", "proveedor"]}

        servicio = ProductoService(dbSession=None)
        productoActualizar = ProductoActualizarSchema(idCategoriaProducto=999, idProveedor=999)

        with pytest.raises(HTTPException) as excinfo:
            servicio.modificarProducto(1, productoActualizar)
        assert excinfo.value.status_code == 400
        assert excinfo.value.detail == "Categoria y Proveedor no existen"


def testModificarProductoExitosoDevuelveActualizado():
    """Prueba: modificarProducto retorna 'Producto actualizado' cuando repo devuelve producto actualizado."""
    productoActualizadoMock = _productoBaseMock(idProducto=1, nombreProducto="Cola 2 Litros")

    with patch("app.Productos.services.productoService.ProductoRepository") as MockRepo:
        MockRepo.return_value.modificarProducto.return_value = productoActualizadoMock

        servicio = ProductoService(dbSession=None)
        productoActualizar = ProductoActualizarSchema(nombreProducto="Cola 2 Litros")

        respuesta = servicio.modificarProducto(1, productoActualizar)
        assert respuesta.success is True
        assert respuesta.message == "Producto actualizado"
        assert respuesta.data.idProducto == 1


def testDeshabilitarProductoNoEncontradoLanza404():
    """Prueba: deshabilitarProducto lanza 404 si el producto no existe."""
    with patch("app.Productos.services.productoService.ProductoRepository") as MockRepo:
        MockRepo.return_value.deshabilitarProducto.return_value = None

        servicio = ProductoService(dbSession=None)
        with pytest.raises(HTTPException) as excinfo:
            servicio.deshabilitarProducto(999)
        assert excinfo.value.status_code == 404
        assert excinfo.value.detail == "Producto no encontrado"


def testDeshabilitarProductoExitosoDevuelveProductoDeshabilitado():
    """Prueba: deshabilitarProducto retorna producto deshabilitado (from_orm)."""
    productoDeshabilitadoMock = _productoBaseMock(idProducto=1, activoProducto=False)

    with patch("app.Productos.services.productoService.ProductoRepository") as MockRepo:
        MockRepo.return_value.deshabilitarProducto.return_value = productoDeshabilitadoMock

        servicio = ProductoService(dbSession=None)
        respuesta = servicio.deshabilitarProducto(1)

        assert respuesta.success is True
        assert respuesta.message == "Producto deshabilitado"
        assert respuesta.data.activoProducto is False
