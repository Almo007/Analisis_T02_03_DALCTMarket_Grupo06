# Pruebas del servicio de CategoriaProducto (usando mocks)
import pytest
from unittest.mock import patch
from fastapi import HTTPException

from app.Productos.services.categoriaProductoService import CategoriaProductoService
from app.Productos.schemas.categoriaProductoSchemas import (
    CategoriaProductoCrearSchema,
    CategoriaProductoActualizarSchema,
)
from tests.mocks_models.categoriaProductoMock import crearCategoriaProductoMock


def testCrudCompletoCategoriaProductoServicioMockeado():
    """Prueba: flujo completo del servicio (listar -> obtenerPorId -> modificar -> deshabilitar) (mockeado)."""
    categoriaBebidasMock = crearCategoriaProductoMock(idCategoriaProducto=1, nombreCategoria="Bebidas", activoCategoria=True)

    with patch("app.Productos.services.categoriaProductoService.CategoriaProductoRepository") as MockRepo:
        instanciaRepo = MockRepo.return_value
        instanciaRepo.listarCategorias.return_value = [categoriaBebidasMock]
        instanciaRepo.obtenerPorId.return_value = categoriaBebidasMock
        instanciaRepo.modificarCategoria.return_value = crearCategoriaProductoMock(
            idCategoriaProducto=1, nombreCategoria="Bebidas", activoCategoria=True
        )
        instanciaRepo.deshabilitarCategoria.return_value = crearCategoriaProductoMock(
            idCategoriaProducto=1, nombreCategoria="Bebidas", activoCategoria=False
        )

        servicio = CategoriaProductoService(dbSession=None)

        # Listar
        respuestaListar = servicio.listarCategorias()
        assert respuestaListar.success is True
        assert isinstance(respuestaListar.data, list)
        assert len(respuestaListar.data) == 1

        # Obtener por id
        respuestaPorId = servicio.obtenerPorId(1)
        assert respuestaPorId.success is True
        assert respuestaPorId.data.idCategoriaProducto == 1

        # Modificar
        categoriaActualizar = CategoriaProductoActualizarSchema(nombreCategoria="Bebidas")
        respuestaModificar = servicio.modificarCategoria(1, categoriaActualizar)
        assert respuestaModificar.success is True
        assert respuestaModificar.data.nombreCategoria == "Bebidas"

        # Deshabilitar
        respuestaDeshabilitar = servicio.deshabilitarCategoria(1)
        assert respuestaDeshabilitar.success is True
        assert respuestaDeshabilitar.data.activoCategoria is False


def testListarCategoriasDevuelveListaVaciaSiNoHayDatos():
    """Prueba: listarCategorias devuelve data=[] si no existen categorías."""
    with patch("app.Productos.services.categoriaProductoService.CategoriaProductoRepository") as MockRepo:
        MockRepo.return_value.listarCategorias.return_value = None

        servicio = CategoriaProductoService(dbSession=None)
        respuesta = servicio.listarCategorias()

        assert respuesta.success is True
        assert respuesta.data == []


def testObtenerCategoriaPorIdNoEncontradaLanza404():
    """Prueba: obtenerPorId lanza 404 si la categoría no existe."""
    with patch("app.Productos.services.categoriaProductoService.CategoriaProductoRepository") as MockRepo:
        MockRepo.return_value.obtenerPorId.return_value = None

        servicio = CategoriaProductoService(dbSession=None)
        with pytest.raises(HTTPException) as excinfo:
            servicio.obtenerPorId(999)
        assert excinfo.value.status_code == 404


def testCrearCategoriaExitosoUsandoEjemploBebidas():
    """Prueba: crearCategoria crea la categoría Bebidas usando el ejemplo de crearCategoriasIniciales."""
    categoriaCreadaMock = crearCategoriaProductoMock(idCategoriaProducto=1, nombreCategoria="Bebidas", activoCategoria=True)

    with patch("app.Productos.services.categoriaProductoService.CategoriaProductoRepository") as MockRepo:
        instanciaRepo = MockRepo.return_value
        instanciaRepo.crearCategoria.return_value = categoriaCreadaMock

        servicio = CategoriaProductoService(dbSession=None)
        categoriaCrear = CategoriaProductoCrearSchema(nombreCategoria="Bebidas")
        respuesta = servicio.crearCategoria(categoriaCrear)

        assert respuesta.success is True
        assert respuesta.data.nombreCategoria == "Bebidas"


def testCrearCategoriaDuplicadaLanza400():
    """Prueba: crearCategoria lanza 400 si la categoría ya existe."""
    with patch("app.Productos.services.categoriaProductoService.CategoriaProductoRepository") as MockRepo:
        MockRepo.return_value.crearCategoria.return_value = None

        servicio = CategoriaProductoService(dbSession=None)
        categoriaCrear = CategoriaProductoCrearSchema(nombreCategoria="Bebidas")

        with pytest.raises(HTTPException) as excinfo:
            servicio.crearCategoria(categoriaCrear)
        assert excinfo.value.status_code == 400


def testModificarCategoriaExitosoActualizaNombre():
    """Prueba: modificarCategoria actualiza nombreCategoria correctamente."""
    categoriaActualizadaMock = crearCategoriaProductoMock(idCategoriaProducto=1, nombreCategoria="Snacks", activoCategoria=True)

    with patch("app.Productos.services.categoriaProductoService.CategoriaProductoRepository") as MockRepo:
        instanciaRepo = MockRepo.return_value
        instanciaRepo.modificarCategoria.return_value = categoriaActualizadaMock

        servicio = CategoriaProductoService(dbSession=None)
        categoriaActualizar = CategoriaProductoActualizarSchema(nombreCategoria="Snacks")
        respuesta = servicio.modificarCategoria(1, categoriaActualizar)

        assert respuesta.success is True
        assert respuesta.data.nombreCategoria == "Snacks"


def testModificarCategoriaNombreDuplicadoLanza400():
    """Prueba: modificarCategoria lanza 400 si el nombre ya existe en otra categoría."""
    with patch("app.Productos.services.categoriaProductoService.CategoriaProductoRepository") as MockRepo:
        MockRepo.return_value.modificarCategoria.return_value = False

        servicio = CategoriaProductoService(dbSession=None)
        categoriaActualizar = CategoriaProductoActualizarSchema(nombreCategoria="Bebidas")

        with pytest.raises(HTTPException) as excinfo:
            servicio.modificarCategoria(1, categoriaActualizar)
        assert excinfo.value.status_code == 400


def testModificarCategoriaNoEncontradaLanza404():
    """Prueba: modificarCategoria lanza 404 si no existe la categoría."""
    with patch("app.Productos.services.categoriaProductoService.CategoriaProductoRepository") as MockRepo:
        MockRepo.return_value.modificarCategoria.return_value = None

        servicio = CategoriaProductoService(dbSession=None)
        categoriaActualizar = CategoriaProductoActualizarSchema(nombreCategoria="Bebidas")

        with pytest.raises(HTTPException) as excinfo:
            servicio.modificarCategoria(999, categoriaActualizar)
        assert excinfo.value.status_code == 404


def testDeshabilitarCategoriaConProductosActivosLanza400():
    """Prueba: deshabilitarCategoria lanza 400 si existen productos activos asociados."""
    with patch("app.Productos.services.categoriaProductoService.CategoriaProductoRepository") as MockRepo:
        MockRepo.return_value.deshabilitarCategoria.return_value = False

        servicio = CategoriaProductoService(dbSession=None)

        with pytest.raises(HTTPException) as excinfo:
            servicio.deshabilitarCategoria(1)
        assert excinfo.value.status_code == 400


def testDeshabilitarCategoriaNoEncontradaLanza404():
    """Prueba: deshabilitarCategoria lanza 404 si no existe la categoría."""
    with patch("app.Productos.services.categoriaProductoService.CategoriaProductoRepository") as MockRepo:
        MockRepo.return_value.deshabilitarCategoria.return_value = None

        servicio = CategoriaProductoService(dbSession=None)

        with pytest.raises(HTTPException) as excinfo:
            servicio.deshabilitarCategoria(999)
        assert excinfo.value.status_code == 404
