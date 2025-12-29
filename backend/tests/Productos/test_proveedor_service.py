# Pruebas del servicio de Proveedor (usando mocks)
import pytest
from unittest.mock import patch
from fastapi import HTTPException

from app.Productos.services.proveedorService import ProveedorService
from app.Productos.schemas.proveedorSchemas import ProveedorCrearSchema, ProveedorActualizarSchema
from tests.mocks_models.proveedorMock import crearProveedorMock


def testCrudCompletoProveedorServicioMockeado():
    """Prueba: flujo completo del servicio (listar -> obtenerPorId -> modificar -> deshabilitar) (mockeado)."""
    proveedorBaseMock = crearProveedorMock(
        idProveedor=1,
        razonSocial="Distribuidora Andina de Bebidas S.A.",
        ruc="1790012345001",
        direccionProveedor="Av. Maldonado y Morán Valverde, Quito",
        telefonoProveedor="0991234567",
        emailProveedor="ventas@andinabebidas.com",
        activoProveedor=True,
    )

    with patch("app.Productos.services.proveedorService.ProveedorRepository") as MockRepo:
        instanciaRepo = MockRepo.return_value
        instanciaRepo.listarProveedores.return_value = [proveedorBaseMock]
        instanciaRepo.obtenerPorId.return_value = proveedorBaseMock
        instanciaRepo.modificarProveedor.return_value = crearProveedorMock(
            idProveedor=1,
            razonSocial="Distribuidora Andina de Bebidas S.A.",
            ruc="1790012345001",
            direccionProveedor="Av. Maldonado y Morán Valverde, Quito",
            telefonoProveedor="0991234567",
            emailProveedor="ventas@andinabebidas.com",
            activoProveedor=True,
        )
        instanciaRepo.deshabilitarProveedor.return_value = crearProveedorMock(
            idProveedor=1,
            razonSocial="Distribuidora Andina de Bebidas S.A.",
            ruc="1790012345001",
            direccionProveedor="Av. Maldonado y Morán Valverde, Quito",
            telefonoProveedor="0991234567",
            emailProveedor="ventas@andinabebidas.com",
            activoProveedor=False,
        )

        servicio = ProveedorService(dbSession=None)

        # Listar
        respuestaListar = servicio.listarProveedores()
        assert respuestaListar.success is True
        assert isinstance(respuestaListar.data, list)
        assert len(respuestaListar.data) == 1

        # Obtener por id
        respuestaPorId = servicio.obtenerPorId(1)
        assert respuestaPorId.success is True
        assert respuestaPorId.data.idProveedor == 1

        # Modificar
        proveedorActualizar = ProveedorActualizarSchema(telefonoProveedor="0991234567")
        respuestaModificar = servicio.modificarProveedor(1, proveedorActualizar)
        assert respuestaModificar.success is True
        assert respuestaModificar.data.ruc == "1790012345001"

        # Deshabilitar
        respuestaDeshabilitar = servicio.deshabilitarProveedor(1)
        assert respuestaDeshabilitar.success is True
        assert respuestaDeshabilitar.data.activoProveedor is False


def testListarProveedoresDevuelveListaVaciaSiNoHayDatos():
    """Prueba: listarProveedores devuelve data=[] si no existen proveedores (repositorio retorna None)."""
    with patch("app.Productos.services.proveedorService.ProveedorRepository") as MockRepo:
        MockRepo.return_value.listarProveedores.return_value = None

        servicio = ProveedorService(dbSession=None)
        respuesta = servicio.listarProveedores()

        assert respuesta.success is True
        assert respuesta.data == []


def testObtenerProveedorPorIdNoEncontradoLanza404():
    """Prueba: obtenerPorId lanza 404 si el proveedor no existe."""
    with patch("app.Productos.services.proveedorService.ProveedorRepository") as MockRepo:
        MockRepo.return_value.obtenerPorId.return_value = None

        servicio = ProveedorService(dbSession=None)
        with pytest.raises(HTTPException) as excinfo:
            servicio.obtenerPorId(999)
        assert excinfo.value.status_code == 404


def testCrearProveedorExitosoUsandoEjemploRepositorio():
    """Prueba: crearProveedor crea un proveedor usando el ejemplo de crearProveedoresIniciales."""
    proveedorCreadoMock = crearProveedorMock(
        idProveedor=1,
        razonSocial="Distribuidora Andina de Bebidas S.A.",
        ruc="1790012345001",
        direccionProveedor="Av. Maldonado y Morán Valverde, Quito",
        telefonoProveedor="0991234567",
        emailProveedor="ventas@andinabebidas.com",
        activoProveedor=True,
    )

    with patch("app.Productos.services.proveedorService.ProveedorRepository") as MockRepo:
        MockRepo.return_value.crearProveedor.return_value = proveedorCreadoMock

        servicio = ProveedorService(dbSession=None)
        proveedorCrear = ProveedorCrearSchema(
            razonSocial="Distribuidora Andina de Bebidas S.A.",
            ruc="1790012345001",
            direccionProveedor="Av. Maldonado y Morán Valverde, Quito",
            telefonoProveedor="0991234567",
            emailProveedor="ventas@andinabebidas.com",
        )
        respuesta = servicio.crearProveedor(proveedorCrear)

        assert respuesta.success is True
        assert respuesta.data.ruc == "1790012345001"


def testCrearProveedorRucDuplicadoLanza400():
    """Prueba: crearProveedor lanza 400 si el RUC ya está registrado."""
    with patch("app.Productos.services.proveedorService.ProveedorRepository") as MockRepo:
        MockRepo.return_value.crearProveedor.return_value = None

        servicio = ProveedorService(dbSession=None)
        proveedorCrear = ProveedorCrearSchema(
            razonSocial="Distribuidora Andina de Bebidas S.A.",
            ruc="1790012345001",
            direccionProveedor="Av. Maldonado y Morán Valverde, Quito",
            telefonoProveedor="0991234567",
            emailProveedor="ventas@andinabebidas.com",
        )

        with pytest.raises(HTTPException) as excinfo:
            servicio.crearProveedor(proveedorCrear)
        assert excinfo.value.status_code == 400


def testModificarProveedorNoEncontradoLanza404():
    """Prueba: modificarProveedor lanza 404 si no existe el proveedor."""
    with patch("app.Productos.services.proveedorService.ProveedorRepository") as MockRepo:
        MockRepo.return_value.modificarProveedor.return_value = None

        servicio = ProveedorService(dbSession=None)
        proveedorActualizar = ProveedorActualizarSchema(telefonoProveedor="0991234567")

        with pytest.raises(HTTPException) as excinfo:
            servicio.modificarProveedor(999, proveedorActualizar)
        assert excinfo.value.status_code == 404


def testDeshabilitarProveedorConProductosActivosLanza400():
    """Prueba: deshabilitarProveedor lanza 400 si existen productos activos asociados."""
    with patch("app.Productos.services.proveedorService.ProveedorRepository") as MockRepo:
        MockRepo.return_value.deshabilitarProveedor.return_value = False

        servicio = ProveedorService(dbSession=None)

        with pytest.raises(HTTPException) as excinfo:
            servicio.deshabilitarProveedor(1)
        assert excinfo.value.status_code == 400


def testDeshabilitarProveedorNoEncontradoLanza404():
    """Prueba: deshabilitarProveedor lanza 404 si no existe el proveedor."""
    with patch("app.Productos.services.proveedorService.ProveedorRepository") as MockRepo:
        MockRepo.return_value.deshabilitarProveedor.return_value = None

        servicio = ProveedorService(dbSession=None)

        with pytest.raises(HTTPException) as excinfo:
            servicio.deshabilitarProveedor(999)
        assert excinfo.value.status_code == 404
