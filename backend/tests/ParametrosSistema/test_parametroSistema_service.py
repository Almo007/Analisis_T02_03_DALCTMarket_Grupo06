# Pruebas del servicio de ParametrosSistema (usando mocks)
import pytest
from unittest.mock import patch
from fastapi import HTTPException

from app.ParametrosSistema.services.parametroSistemaService import ParametroSistemaService
from app.ParametrosSistema.schemas.parametroSistemaSchemas import (
    ParametroSistemaCrearSchema,
    ParametroSistemaActualizarSchema,
)
from tests.mocks_models.parametroSistemaMock import crearParametroSistemaMock


def testCrudCompletoParametroSistemaServicioMockeado():
    """Prueba: flujo completo del servicio (listar -> obtenerPorId -> modificar -> deshabilitar) (mockeado)."""
    parametroIvaMock = crearParametroSistemaMock(
        idParametroSistema=5,
        claveParametro="IVA",
        valorParametro="15",
        activoParametro=True,
    )

    with patch("app.ParametrosSistema.services.parametroSistemaService.ParametroSistemaRepository") as MockRepo:
        instanciaRepo = MockRepo.return_value
        instanciaRepo.listarParametros.return_value = [parametroIvaMock]
        instanciaRepo.obtenerPorId.return_value = parametroIvaMock
        instanciaRepo.modificarParametro.return_value = crearParametroSistemaMock(
            idParametroSistema=5,
            claveParametro="IVA",
            valorParametro="16",
            activoParametro=True,
        )
        instanciaRepo.deshabilitarParametro.return_value = crearParametroSistemaMock(
            idParametroSistema=5,
            claveParametro="IVA",
            valorParametro="16",
            activoParametro=False,
        )

        servicio = ParametroSistemaService(dbSession=None)

        # Listar
        respuestaListar = servicio.listarParametros()
        assert respuestaListar.success is True
        assert isinstance(respuestaListar.data, list)
        assert len(respuestaListar.data) == 1

        # Obtener por id
        respuestaPorId = servicio.obtenerParametroPorId(5)
        assert respuestaPorId.success is True
        assert respuestaPorId.data.idParametroSistema == 5

        # Modificar
        parametroActualizar = ParametroSistemaActualizarSchema(valorParametro="16")
        respuestaModificar = servicio.modificarParametro(5, parametroActualizar)
        assert respuestaModificar.success is True
        assert respuestaModificar.data.valorParametro == "16"

        # Deshabilitar
        respuestaDeshabilitar = servicio.deshabilitarParametro(5)
        assert respuestaDeshabilitar.success is True
        assert respuestaDeshabilitar.data.activoParametro is False


def testListarParametrosDevuelveListaVaciaSiNoHayDatos():
    """Prueba: listarParametros devuelve data=[] si no existen parámetros."""
    with patch("app.ParametrosSistema.services.parametroSistemaService.ParametroSistemaRepository") as MockRepo:
        MockRepo.return_value.listarParametros.return_value = []

        servicio = ParametroSistemaService(dbSession=None)
        respuesta = servicio.listarParametros()

        assert respuesta.success is True
        assert respuesta.data == []


def testObtenerParametroPorIdNoEncontradoLanza404():
    """Prueba: obtenerParametroPorId lanza 404 si el parámetro no existe."""
    with patch("app.ParametrosSistema.services.parametroSistemaService.ParametroSistemaRepository") as MockRepo:
        MockRepo.return_value.obtenerPorId.return_value = None

        servicio = ParametroSistemaService(dbSession=None)
        with pytest.raises(HTTPException) as excinfo:
            servicio.obtenerParametroPorId(999)
        assert excinfo.value.status_code == 404


def testCrearParametroExitosoUsandoEjemploIva():
    """Prueba: crearParametro crea el parámetro IVA usando el ejemplo del diccionario de datos."""
    parametroCreadoMock = crearParametroSistemaMock(
        idParametroSistema=5,
        claveParametro="IVA",
        valorParametro="15",
        activoParametro=True,
    )

    with patch("app.ParametrosSistema.services.parametroSistemaService.ParametroSistemaRepository") as MockRepo:
        instanciaRepo = MockRepo.return_value
        instanciaRepo.crearParametro.return_value = parametroCreadoMock

        servicio = ParametroSistemaService(dbSession=None)
        parametroCrear = ParametroSistemaCrearSchema(claveParametro="IVA", valorParametro="15")
        respuesta = servicio.crearParametro(parametroCrear)

        assert respuesta.success is True
        assert respuesta.data.claveParametro == "IVA"
        assert respuesta.data.valorParametro == "15"


def testCrearParametroClaveDuplicadaLanza400():
    """Prueba: crearParametro lanza 400 si la clave ya existe."""
    with patch("app.ParametrosSistema.services.parametroSistemaService.ParametroSistemaRepository") as MockRepo:
        MockRepo.return_value.crearParametro.return_value = None

        servicio = ParametroSistemaService(dbSession=None)
        parametroCrear = ParametroSistemaCrearSchema(claveParametro="IVA", valorParametro="15")

        with pytest.raises(HTTPException) as excinfo:
            servicio.crearParametro(parametroCrear)
        assert excinfo.value.status_code == 400


def testModificarParametroExitosoActualizaValor():
    """Prueba: modificarParametro actualiza valorParametro correctamente."""
    parametroActualizadoMock = crearParametroSistemaMock(
        idParametroSistema=5,
        claveParametro="IVA",
        valorParametro="16",
        activoParametro=True,
    )

    with patch("app.ParametrosSistema.services.parametroSistemaService.ParametroSistemaRepository") as MockRepo:
        instanciaRepo = MockRepo.return_value
        instanciaRepo.modificarParametro.return_value = parametroActualizadoMock

        servicio = ParametroSistemaService(dbSession=None)
        parametroActualizar = ParametroSistemaActualizarSchema(valorParametro="16")
        respuesta = servicio.modificarParametro(5, parametroActualizar)

        assert respuesta.success is True
        assert respuesta.data.valorParametro == "16"


def testModificarParametroClaveDuplicadaLanza400():
    """Prueba: modificarParametro lanza 400 si la clave ya existe en otro registro."""
    with patch("app.ParametrosSistema.services.parametroSistemaService.ParametroSistemaRepository") as MockRepo:
        MockRepo.return_value.modificarParametro.return_value = False

        servicio = ParametroSistemaService(dbSession=None)
        parametroActualizar = ParametroSistemaActualizarSchema(claveParametro="IVA")

        with pytest.raises(HTTPException) as excinfo:
            servicio.modificarParametro(5, parametroActualizar)
        assert excinfo.value.status_code == 400


def testModificarParametroNoEncontradoLanza404():
    """Prueba: modificarParametro lanza 404 si no existe el parámetro."""
    with patch("app.ParametrosSistema.services.parametroSistemaService.ParametroSistemaRepository") as MockRepo:
        MockRepo.return_value.modificarParametro.return_value = None

        servicio = ParametroSistemaService(dbSession=None)
        parametroActualizar = ParametroSistemaActualizarSchema(valorParametro="16")

        with pytest.raises(HTTPException) as excinfo:
            servicio.modificarParametro(999, parametroActualizar)
        assert excinfo.value.status_code == 404


def testDeshabilitarParametroNoEncontradoLanza404():
    """Prueba: deshabilitarParametro lanza 404 si no existe el parámetro."""
    with patch("app.ParametrosSistema.services.parametroSistemaService.ParametroSistemaRepository") as MockRepo:
        MockRepo.return_value.deshabilitarParametro.return_value = None

        servicio = ParametroSistemaService(dbSession=None)

        with pytest.raises(HTTPException) as excinfo:
            servicio.deshabilitarParametro(999)
        assert excinfo.value.status_code == 404
