import pytest
from unittest.mock import MagicMock, patch
from fastapi import HTTPException

from datetime import datetime, timezone, timedelta, date

from app.Caja.services.cajaService import CajaService
from app.Caja.schemas.cajaSchemas import CajaCrearSchema, CajaCerrarSchema

from tests.mocks_models.cajaHistorialMock import crearCajaHistorialMock
from tests.mocks_models.usuarioMock import crearUsuarioMock
from tests.mocks_models.rolMock import crearRolMock


def _quitoTZ():
    return timezone(timedelta(hours=-5))


def _tokenAdmin():
    return {"idUsuario": 1, "rol": "Administrador", "nombreCompleto": "admin"}


def _tokenCajero():
    return {"idUsuario": 3, "rol": "Cajero", "nombreCompleto": "cajero"}


def _usuarioAdminMock():
    rolMock = crearRolMock(idRol=1, nombreRol="Administrador")
    return crearUsuarioMock(idUsuario=1, idRol=1, nombreCompleto="admin", cedulaUsuario="admin", emailUsuario="admin@example.com", rol=rolMock)


def _usuarioCajeroMock():
    rolMock = crearRolMock(idRol=3, nombreRol="Cajero")
    return crearUsuarioMock(idUsuario=3, idRol=3, nombreCompleto="cajero", cedulaUsuario="cajero", emailUsuario="cajero@example.com", rol=rolMock)


def _cajaAbiertaHoyMock(idCaja: int = 3, idUsuarioCaja: int = 3, usuario=None):
    tzQuito = _quitoTZ()
    ahora = datetime.now(tzQuito).replace(microsecond=0)
    return crearCajaHistorialMock(
        idCaja=idCaja,
        idUsuarioCaja=idUsuarioCaja,
        fechaAperturaCaja=ahora,
        fechaCierreCaja=None,
        montoInicialDeclarado=95.0,
        montoCierreDeclarado=None,
        montoCierreSistema=None,
        diferenciaCaja=None,
        estadoCaja="ABIERTA",
        detalle="Apertura: montoInicialDeclarado: 95.0",
        usuario=usuario,
    )


def testCrearCajaHistorialExitosoAdjuntaUsuarioYRedondeaMonto():
    """Prueba: crearCajaHistorial crea caja, agrega detalle con actor y adjunta usuario para serialización."""
    dbSessionMock = MagicMock()

    cajaMock = _cajaAbiertaHoyMock(idCaja=3, idUsuarioCaja=3, usuario=None)
    usuarioCajeroMock = _usuarioCajeroMock()

    with patch("app.Caja.services.cajaService.CajaRepository") as MockRepo, patch(
        "app.Caja.services.cajaService.UsuarioRepository"
    ) as MockUsuarioRepo:
        MockRepo.return_value.crearCajaHistorial.return_value = cajaMock
        MockUsuarioRepo.return_value.obtenerUsuarioPorId.return_value = usuarioCajeroMock

        servicio = CajaService(dbSession=dbSessionMock)
        respuesta = servicio.crearCajaHistorial(CajaCrearSchema(montoInicial=95.001), _tokenCajero())

        assert respuesta.success is True
        assert "Caja abierta por 3-cajero" in respuesta.message
        assert respuesta.data.estadoCaja == "ABIERTA"
        assert respuesta.data.usuario.emailUsuario == "cajero@example.com"
        assert respuesta.data.montoInicialDeclarado == 95.0


def testCrearCajaHistorialCajaAbiertaExistenteLanza400():
    """Prueba: crearCajaHistorial lanza 400 si ya existe caja ABIERTA para el usuario."""
    dbSessionMock = MagicMock()

    with patch("app.Caja.services.cajaService.CajaRepository") as MockRepo:
        MockRepo.return_value.crearCajaHistorial.return_value = {"error": "caja_abierta_existente"}

        servicio = CajaService(dbSession=dbSessionMock)
        with pytest.raises(HTTPException) as excinfo:
            servicio.crearCajaHistorial(CajaCrearSchema(montoInicial=10.0), _tokenCajero())
        assert excinfo.value.status_code == 400


def testCerrarCajaNoEncontradaLanza404():
    """Prueba: cerrarCaja lanza 404 si la caja no existe."""
    dbSessionMock = MagicMock()

    with patch("app.Caja.services.cajaService.CajaRepository") as MockRepo:
        MockRepo.return_value.obtenerPorId.return_value = None

        servicio = CajaService(dbSession=dbSessionMock)
        with pytest.raises(HTTPException) as excinfo:
            servicio.cerrarCaja(999, CajaCerrarSchema(montoFinal=10.0), _tokenAdmin())
        assert excinfo.value.status_code == 404


def testCerrarCajaYaCerradaDevuelveSuccessFalse():
    """Prueba: cerrarCaja devuelve success=False si la caja ya está cerrada."""
    dbSessionMock = MagicMock()

    tzQuito = _quitoTZ()
    ahora = datetime.now(tzQuito).replace(microsecond=0)
    cajaCerradaMock = crearCajaHistorialMock(
        idCaja=1,
        idUsuarioCaja=1,
        fechaAperturaCaja=ahora - timedelta(hours=3),
        fechaCierreCaja=ahora - timedelta(hours=1),
        montoInicialDeclarado=10.0,
        montoCierreDeclarado=14.0,
        montoCierreSistema=22.68,
        diferenciaCaja=-8.68,
        estadoCaja="CERRADA",
        detalle="Cierre por 1-admin",
        usuario=_usuarioAdminMock(),
    )

    with patch("app.Caja.services.cajaService.CajaRepository") as MockRepo:
        MockRepo.return_value.obtenerPorId.return_value = cajaCerradaMock

        servicio = CajaService(dbSession=dbSessionMock)
        respuesta = servicio.cerrarCaja(1, CajaCerrarSchema(montoFinal=14.0), _tokenAdmin())

        assert respuesta.success is False
        assert respuesta.message == "La caja ya está cerrada"
        assert respuesta.data.estadoCaja == "CERRADA"


def testCerrarCajaCajeroNoPropietarioLanza403():
    """Prueba: cerrarCaja lanza 403 si el cajero intenta cerrar caja de otro usuario."""
    dbSessionMock = MagicMock()

    cajaOtroUsuario = _cajaAbiertaHoyMock(idCaja=5, idUsuarioCaja=1, usuario=_usuarioAdminMock())

    with patch("app.Caja.services.cajaService.CajaRepository") as MockRepo:
        MockRepo.return_value.obtenerPorId.return_value = cajaOtroUsuario

        servicio = CajaService(dbSession=dbSessionMock)
        with pytest.raises(HTTPException) as excinfo:
            servicio.cerrarCaja(5, CajaCerrarSchema(montoFinal=10.0), _tokenCajero())
        assert excinfo.value.status_code == 403


def testCerrarCajaExitosoAdministrador():
    """Prueba: cerrarCaja (Administrador) cierra caja y devuelve respuesta success=True."""
    dbSessionMock = MagicMock()

    cajaAbierta = _cajaAbiertaHoyMock(idCaja=3, idUsuarioCaja=3, usuario=_usuarioCajeroMock())

    cajaCerrada = crearCajaHistorialMock(
        idCaja=3,
        idUsuarioCaja=3,
        fechaAperturaCaja=cajaAbierta.fechaAperturaCaja,
        fechaCierreCaja=datetime.now(_quitoTZ()).replace(microsecond=0),
        montoInicialDeclarado=95.0,
        montoCierreDeclarado=110.0,
        montoCierreSistema=100.0,
        diferenciaCaja=10.0,
        estadoCaja="CERRADA",
        detalle="Cierre por 1-admin",
        usuario=_usuarioCajeroMock(),
    )

    with patch("app.Caja.services.cajaService.CajaRepository") as MockRepo:
        MockRepo.return_value.obtenerPorId.return_value = cajaAbierta
        MockRepo.return_value.cerrarCaja.return_value = cajaCerrada

        servicio = CajaService(dbSession=dbSessionMock)
        respuesta = servicio.cerrarCaja(3, CajaCerrarSchema(montoFinal=110.0), _tokenAdmin())

        assert respuesta.success is True
        assert "Caja cerrada por 1-admin" in respuesta.message
        assert respuesta.data.estadoCaja == "CERRADA"


def testListarCajasHoyDevuelveVaciaSiNoHayDatos():
    """Prueba: listarCajasHoy devuelve data=[] si no hay cajas hoy."""
    dbSessionMock = MagicMock()

    with patch("app.Caja.services.cajaService.CajaRepository") as MockRepo:
        MockRepo.return_value.listarCajasHoy.return_value = []

        servicio = CajaService(dbSession=dbSessionMock)
        respuesta = servicio.listarCajasHoy(_tokenAdmin())

        assert respuesta.success is True
        assert respuesta.data == []
        assert respuesta.message == "No se han abierto cajas hoy"


def testListarTodasCajasNoAdminLanza403():
    """Prueba: listarTodasCajas lanza 403 si el rol no es Administrador."""
    dbSessionMock = MagicMock()

    servicio = CajaService(dbSession=dbSessionMock)
    with pytest.raises(HTTPException) as excinfo:
        servicio.listarTodasCajas(_tokenCajero())
    assert excinfo.value.status_code == 403


def testReabrirCajaNoAdminLanza403():
    """Prueba: reabrirCaja lanza 403 si el rol no es Administrador."""
    dbSessionMock = MagicMock()

    servicio = CajaService(dbSession=dbSessionMock)
    with pytest.raises(HTTPException) as excinfo:
        servicio.reabrirCaja(1, _tokenCajero())
    assert excinfo.value.status_code == 403


def testReabrirCajaExitosoAdministrador():
    """Prueba: reabrirCaja (Administrador) reabre una caja cerrada y devuelve success=True."""
    dbSessionMock = MagicMock()

    tzQuito = _quitoTZ()
    ahora = datetime.now(tzQuito).replace(microsecond=0)
    cajaCerrada = crearCajaHistorialMock(
        idCaja=1,
        idUsuarioCaja=1,
        fechaAperturaCaja=ahora - timedelta(hours=2),
        fechaCierreCaja=ahora - timedelta(hours=1),
        montoInicialDeclarado=10.0,
        montoCierreDeclarado=15.0,
        montoCierreSistema=15.0,
        diferenciaCaja=0.0,
        estadoCaja="CERRADA",
        detalle="Cierre por 1-admin",
        usuario=_usuarioAdminMock(),
    )
    cajaReabierta = crearCajaHistorialMock(
        idCaja=1,
        idUsuarioCaja=1,
        fechaAperturaCaja=cajaCerrada.fechaAperturaCaja,
        fechaCierreCaja=None,
        montoInicialDeclarado=10.0,
        montoCierreDeclarado=None,
        montoCierreSistema=None,
        diferenciaCaja=None,
        estadoCaja="ABIERTA",
        detalle="Cierre por 1-admin; Reabierta por 1-admin",
        usuario=_usuarioAdminMock(),
    )

    with patch("app.Caja.services.cajaService.CajaRepository") as MockRepo:
        MockRepo.return_value.obtenerPorId.return_value = cajaCerrada
        MockRepo.return_value.reabrirCaja.return_value = cajaReabierta

        servicio = CajaService(dbSession=dbSessionMock)
        respuesta = servicio.reabrirCaja(1, _tokenAdmin())

        assert respuesta.success is True
        assert respuesta.data.estadoCaja == "ABIERTA"
        assert "Caja reabierta" in respuesta.message


def testListarCajasCajeroDevuelveCajasYAdjuntaUsuario():
    """Prueba: listarCajas (Cajero) devuelve sus cajas y adjunta usuario para serialización."""
    dbSessionMock = MagicMock()

    caja1 = _cajaAbiertaHoyMock(idCaja=10, idUsuarioCaja=3, usuario=None)
    usuarioCajeroMock = _usuarioCajeroMock()

    with patch("app.Caja.services.cajaService.CajaRepository") as MockRepo, patch(
        "app.Caja.services.cajaService.UsuarioRepository"
    ) as MockUsuarioRepo:
        MockRepo.return_value.listarCajas.return_value = [caja1]
        MockUsuarioRepo.return_value.obtenerUsuarioPorId.return_value = usuarioCajeroMock

        servicio = CajaService(dbSession=dbSessionMock)
        respuesta = servicio.listarCajas(_tokenCajero())

        MockRepo.return_value.listarCajas.assert_called_once_with(3, False)
        assert respuesta.success is True
        assert respuesta.message == "Cajas encontradas"
        assert isinstance(respuesta.data, list)
        assert len(respuesta.data) == 1
        assert respuesta.data[0].usuario.nombreCompleto == "cajero"


def testListarCajasAdminDevuelveVaciaSiNoHayDatos():
    """Prueba: listarCajas (Administrador) devuelve lista vacía si no hay cajas."""
    dbSessionMock = MagicMock()

    with patch("app.Caja.services.cajaService.CajaRepository") as MockRepo:
        MockRepo.return_value.listarCajas.return_value = []

        servicio = CajaService(dbSession=dbSessionMock)
        respuesta = servicio.listarCajas(_tokenAdmin())

        MockRepo.return_value.listarCajas.assert_called_once_with(None, True)
        assert respuesta.success is True
        assert respuesta.message == "No se encontraron cajas"
        assert respuesta.data == []


def testListarTodasCajasAdminDevuelveVaciaSiNoHayDatos():
    """Prueba: listarTodasCajas (Administrador) devuelve [] si no existen cajas."""
    dbSessionMock = MagicMock()

    with patch("app.Caja.services.cajaService.CajaRepository") as MockRepo:
        MockRepo.return_value.listarCajas.return_value = []

        servicio = CajaService(dbSession=dbSessionMock)
        respuesta = servicio.listarTodasCajas(_tokenAdmin())

        MockRepo.return_value.listarCajas.assert_called_once_with(None, True)
        assert respuesta.success is True
        assert respuesta.message == "No se encontraron cajas"
        assert respuesta.data == []


def testListarTodasCajasAdminDevuelveListaYAdjuntaUsuario():
    """Prueba: listarTodasCajas (Administrador) serializa lista y adjunta usuario."""
    dbSessionMock = MagicMock()

    cajaAdmin = _cajaAbiertaHoyMock(idCaja=1, idUsuarioCaja=1, usuario=None)
    cajaCajero = _cajaAbiertaHoyMock(idCaja=2, idUsuarioCaja=3, usuario=None)
    usuarioAdminMock = _usuarioAdminMock()
    usuarioCajeroMock = _usuarioCajeroMock()

    with patch("app.Caja.services.cajaService.CajaRepository") as MockRepo, patch(
        "app.Caja.services.cajaService.UsuarioRepository"
    ) as MockUsuarioRepo:
        MockRepo.return_value.listarCajas.return_value = [cajaAdmin, cajaCajero]

        def obtenerUsuarioPorIdSideEffect(idUsuario):
            return usuarioAdminMock if idUsuario == 1 else usuarioCajeroMock

        MockUsuarioRepo.return_value.obtenerUsuarioPorId.side_effect = obtenerUsuarioPorIdSideEffect

        servicio = CajaService(dbSession=dbSessionMock)
        respuesta = servicio.listarTodasCajas(_tokenAdmin())

        assert respuesta.success is True
        assert respuesta.message == "Cajas encontradas"
        assert len(respuesta.data) == 2
        assert respuesta.data[0].usuario is not None
        assert respuesta.data[1].usuario is not None


def testFiltrarCajaNoAdminLanza403():
    """Prueba: filtrarCaja lanza 403 si el rol no es Administrador."""
    dbSessionMock = MagicMock()

    servicio = CajaService(dbSession=dbSessionMock)
    with pytest.raises(HTTPException) as excinfo:
        servicio.filtrarCaja(3, date.today(), _tokenCajero())
    assert excinfo.value.status_code == 403


def testFiltrarCajaAdminDevuelveVaciaSiNoHayResultados():
    """Prueba: filtrarCaja (Administrador) devuelve [] si no hay coincidencias."""
    dbSessionMock = MagicMock()
    fechaFiltro = date.today()

    with patch("app.Caja.services.cajaService.CajaRepository") as MockRepo:
        MockRepo.return_value.filtrarCaja.return_value = []

        servicio = CajaService(dbSession=dbSessionMock)
        respuesta = servicio.filtrarCaja(3, fechaFiltro, _tokenAdmin())

        MockRepo.return_value.filtrarCaja.assert_called_once_with(3, fechaFiltro)
        assert respuesta.success is True
        assert respuesta.message == "No se encontraron cajas para los parámetros proporcionados"
        assert respuesta.data == []


def testFiltrarCajaAdminDevuelveListaYAdjuntaUsuario():
    """Prueba: filtrarCaja (Administrador) adjunta usuario en cada caja y serializa respuesta."""
    dbSessionMock = MagicMock()
    fechaFiltro = date.today()

    cajaFiltrada = _cajaAbiertaHoyMock(idCaja=7, idUsuarioCaja=3, usuario=None)
    usuarioCajeroMock = _usuarioCajeroMock()

    with patch("app.Caja.services.cajaService.CajaRepository") as MockRepo, patch(
        "app.Caja.services.cajaService.UsuarioRepository"
    ) as MockUsuarioRepo:
        MockRepo.return_value.filtrarCaja.return_value = [cajaFiltrada]
        MockUsuarioRepo.return_value.obtenerUsuarioPorId.return_value = usuarioCajeroMock

        servicio = CajaService(dbSession=dbSessionMock)
        respuesta = servicio.filtrarCaja(3, fechaFiltro, _tokenAdmin())

        assert respuesta.success is True
        assert respuesta.message == "Cajas encontradas"
        assert len(respuesta.data) == 1
        assert respuesta.data[0].usuario.nombreCompleto == "cajero"
