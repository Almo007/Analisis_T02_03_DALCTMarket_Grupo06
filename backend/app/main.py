from fastapi import FastAPI, Depends
from fastapi.exceptions import HTTPException
from fastapi.responses import JSONResponse
from fastapi.requests import Request
from app.configuracionGeneral.seguridadJWT import protegerRuta
from app.database import Base,engine,obtenerSesionDirecta

# Librerias de rutas
from app.Usuarios.controllers.usuarioController import router as controladorUsuarios
from app.Usuarios.controllers.usuarioController import publicRouter as controladorUsuariosPublic
from app.Usuarios.repositories.usuarioRepository import UsuarioRepository
from app.Usuarios.controllers.rolController import router as controladorRoles
from app.Usuarios.repositories.rolRepository import RolRepository
# Parametros de sistema
from app.ParametrosSistema.controllers.parametroSistemaController import router as controladorParametrosSistema
from app.ParametrosSistema.repositories.parametroSistemaRepository import ParametroSistemaRepository


app = FastAPI(
    title="API DALCT Market",
    description="Backend de DALCT Market",
    version="0.1",
)

@app.on_event("startup")
async def startup_event():
    print("Iniciando API DALCT Market...")
    print("Conectando a la base de datos...")
    Base.metadata.create_all(bind=engine)
    print("Base de datos conectada...")
    #Crear datos por defecto
    RolRepository(obtenerSesionDirecta()).crearRolesPorDefecto()
    UsuarioRepository(obtenerSesionDirecta()).crearUsuariosIniciales()
    ParametroSistemaRepository(obtenerSesionDirecta()).crearParametrosIniciales()

@app.get("/")
def inicio(usuarioActual=Depends(protegerRuta("Prueba", "ALL"))):
    print(usuarioActual)
    return {"mensaje": "API DALCT Market está lista...!"}


# Registrar rutas
app.include_router(controladorUsuariosPublic,prefix="/usuarios", tags=["Usuarios"])
app.include_router(controladorUsuarios,prefix="/usuarios", tags=["Usuarios"])
app.include_router(controladorRoles,prefix="/roles", tags=["Roles"])
app.include_router(controladorParametrosSistema,prefix="/parametrosistema", tags=["ParametrosSistema"])





# Configurar errores globales
# 🔴 ERRORES HTTP
@app.exception_handler(HTTPException)
async def manejarErroresHttp(request: Request, exc: HTTPException):
    # Cambiamos el mensaje si viene de OAuth2
    mensaje = exc.detail
    if mensaje == "Not authenticated":
        mensaje = "No autenticado, debe iniciar sesión y proporcionar un token JWT"
    return JSONResponse(
        status_code=exc.status_code,
        content={"success": False, "message": mensaje, "data": None}
    )


# 🔴 ERRORES INTERNOS
@app.exception_handler(Exception)
async def manejarErroresGenerales(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"success": False, "message": "errorInternoServidor", "data": None}
    )