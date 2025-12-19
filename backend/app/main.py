from fastapi import FastAPI, Depends
from fastapi.exceptions import HTTPException
from fastapi.responses import JSONResponse
from fastapi.requests import Request
from app.configuracionGeneral.seguridadJWT import protegerRuta


# Libreria de Usuarios
from app.Usuarios.controllers.usuarioController import router as controladorUsuarios


app = FastAPI(
    title="API DALCT Market",
    description="Backend de DALCT Market",
    version="0.1",
)

@app.get("/")
def inicio(usuarioActual=Depends(protegerRuta("Prueba", "ALL"))):
    print(usuarioActual)
    return {"mensaje": "API DALCT Market está lista...!"}


# Registrar rutas
app.include_router(controladorUsuarios,prefix="/usuarios", tags=["Usuarios"])





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