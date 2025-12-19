from fastapi import APIRouter, HTTPException, Depends
from app.configuracionGeneral.errores import ERROR_CREDENCIALES
from app.configuracionGeneral.schemasGenerales import respuestaApi
from app.Usuarios.schemas.usuarioSchemas import IniciarSesionRequest
from app.configuracionGeneral.seguridadJWT import crearTokenJWT
from fastapi.security import OAuth2PasswordRequestForm 


router = APIRouter() # Definir el enrutador

#Validador para login con swagger y manual

def validarLogin(username,password):
    if username != "admin" or password != "admin":
        raise HTTPException(
            status_code=ERROR_CREDENCIALES.codigoHttp,
            detail=ERROR_CREDENCIALES.mensaje
        )
    token=crearTokenJWT({"username": username, "rol": "Administrador"})
    return {"access_token": token, "token_type": "bearer"}

# Login Público - Swagger
@router.post("/loginSwagger",
             summary="Iniciar sesión con OAuth2PasswordBearer (OAuth2, password)",
             description="Iniciar sesión y obtener un token de acceso JWT directamente desde Swagger")
def iniciarSesion(request: OAuth2PasswordRequestForm = Depends()):# Usa form-data en swagger
    return validarLogin(request.username, request.password)


# Login Público - Manual JSON
@router.post("/login",
             summary="Iniciar sesión",
             description="Iniciar sesión y obtener un token de acceso JWT si se lo hace manualmente con cuerpo JSON")
def iniciarSesion(request: IniciarSesionRequest):# Usa body JSON
    return validarLogin(request.username, request.password)



