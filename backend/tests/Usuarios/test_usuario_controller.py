# Pruebas del controlador de Usuarios (usando mocks)

from fastapi.testclient import TestClient
from unittest.mock import patch

from app.configuracionGeneral.schemasGenerales import respuestaApi
from app.database import obtenerSesion
from app.main import app


# Usar la app real (app.main) pero sin disparar startup_event (evita BD)
app.router.on_startup.clear()
app.router.on_shutdown.clear()


def _mockObtenerSesion():
    # Evita crear sesión real de BD
    yield None


app.dependency_overrides[obtenerSesion] = _mockObtenerSesion


client = TestClient(app)


def testLoginJsonDevuelveTokenMockeado():
    """Prueba: POST /usuarios/login con JSON devuelve token (mockeado UsuarioService y crearTokenJWT)"""
    datosLogin = {"username": "admin", "password": "1234"}

    with patch('app.Usuarios.controllers.usuarioController.UsuarioService') as MockService, patch('app.Usuarios.controllers.usuarioController.crearTokenJWT') as MockCrearToken:
        instanciaServicio = MockService.return_value
        instanciaServicio.validarCredenciales.return_value = {
            "idUsuario": 1,
            "cedula": "admin",
            "nombreCompleto": "admin",
            "idRol": 1,
            "rol": "Administrador"
        }
        MockCrearToken.return_value = "tokenPrueba"

        respuesta = client.post("/usuarios/login", json=datosLogin)
        assert respuesta.status_code == 200
        cuerpo = respuesta.json()
        # Debe contener token de acceso
        assert "access_token" in cuerpo
        assert cuerpo["token_type"] == "bearer"


def testLoginSwaggerYAccesoRutaProtegidaMockeado():
    """Prueba: POST /usuarios/loginSwagger (form) y acceso a GET /usuarios/ usando override de dependencia (sin DB)"""
    datosForm = {"username": "admin", "password": "1234"}

    with patch('app.Usuarios.controllers.usuarioController.UsuarioService') as MockService, patch('app.Usuarios.controllers.usuarioController.crearTokenJWT') as MockCrearToken, patch('app.configuracionGeneral.seguridadJWT.verificarToken') as MockVerificarToken:
        instanciaServicio = MockService.return_value
        instanciaServicio.validarCredenciales.return_value = {
            "idUsuario": 1,
            "cedula": "admin",
            "nombreCompleto": "admin",
            "idRol": 1,
            "rol": "Administrador"
        }
        instanciaServicio.listarUsuarios.return_value = respuestaApi(success=True, message="Usuarios encontrados", data=[{"idUsuario":1,"nombreCompleto":"admin","cedulaUsuario":"admin"}])
        MockCrearToken.return_value = "tokenPrueba"
        MockVerificarToken.return_value = {"idUsuario":1, "rol":"Administrador", "nombreCompleto":"admin"}

        # Hacemos login por /loginSwagger
        respuestaForm = client.post("/usuarios/loginSwagger", data=datosForm)
        assert respuestaForm.status_code == 200
        cuerpoForm = respuestaForm.json()
        assert "access_token" in cuerpoForm
        token = cuerpoForm["access_token"]

        encabezados = {"Authorization": f"Bearer {token}"}
        respuestaProtegida = client.get("/usuarios/", headers=encabezados)
        assert respuestaProtegida.status_code == 200
        cuerpoProtegida = respuestaProtegida.json()
        assert cuerpoProtegida["success"] is True
        assert isinstance(cuerpoProtegida["data"], list)
