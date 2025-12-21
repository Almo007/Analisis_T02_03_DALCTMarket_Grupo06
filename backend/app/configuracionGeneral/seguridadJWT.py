# Librerias para manejar JWT
import os
from datetime import datetime, timedelta, timezone
from jose import JWTError, jwt # Librerias para manejar JWT

from fastapi import Depends, HTTPException,Request
from fastapi.security import OAuth2PasswordBearer


from app.configuracionGeneral.errores import ERROR_TOKEN_INVALIDO



SECRET_KEY = os.environ.get("SECRET_KEY","secreto")
ALGORITHM = os.environ.get("ALGORITHM","HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = os.environ.get("ACCESS_TOKEN_EXPIRE_MINUTES", 30)
#Todas las funciones con camelCase y español

def crearTokenJWT(datos:dict)->str:
    quitoTZ=timezone(timedelta(hours=-5)) # Se obtiene la zona horaria de Ecuador
    payload = datos.copy() # Datos iniciales para el token
    fechaActual = datetime.now(quitoTZ)
    expira = fechaActual + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    # Agregar al payload del token las fechas 
    payload["exp"] = expira
    payload["iat"] = fechaActual

    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return token

def verificarToken(token: str) -> dict:
    return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])


oauth2Scheme = OAuth2PasswordBearer(tokenUrl="/usuarios/loginSwagger",auto_error=False)




#Validador de token y permisos según el rol
permisos = {
    "Prueba": {"Administrador": "ALL", "Bodeguero": "ALL", "Cajero": "ALL"},
    "ParametrosSistema": {"Administrador": "ALL", "Bodeguero": [], "Cajero": []},
    "Usuarios": {"Administrador": "ALL", "Bodeguero": [], "Cajero": []},
    "Productos": {"Administrador": "ALL", "Bodeguero": "ALL", "Cajero": ["GET"]},
    "Inventario": {"Administrador": ["ALL","GET","POST","PUT","DELETE"], "Bodeguero": ["GET","POST","PUT"], "Cajero": ["GET"]},
    "Pedido": {"Administrador": ["ALL","GET","POST","PUT","DELETE"], "Bodeguero": ["ALL","GET","POST","PUT","DELETE"], "Cajero": []},
    "Promocion": {"Administrador": ["ALL","GET","POST","PUT","DELETE"], "Bodeguero": [], "Cajero": ["GET"]},
    "Venta": {"Administrador": ["ALL","GET","POST","PUT","DELETE"], "Bodeguero": [], "Cajero": ["ALL","GET","POST","PUT","DELETE"]},
    "Cliente": {"Administrador": "ALL", "Bodeguero": [], "Cajero": "ALL"},
    "Caja": {"Administrador": ["ALL","GET","POST","PUT","DELETE"], "Bodeguero": [], "Cajero": ["GET","POST","PUT"]},
    "Reportes": {
        "Administrador": ["GET_Stock","GET_Ventas","GET_Caja","GET_Clientes"],
        "Bodeguero": ["GET_Stock"],
        "Cajero": []
    },
}

    
def identificarUsuarioString(usuario: dict) -> str:
    """Devuelve la identificación formateada como 'id-Nombre Completo' si es posible."""
    if not usuario:
        return ""
    idu = usuario.get("idUsuario")
    nombre = usuario.get("nombreCompleto") or usuario.get("usuario") or usuario.get("email") or ""
    if idu is None:
        return nombre
    return f"{idu}-{nombre}"


def protegerRuta(modulo: str, accion: str):
    def dependencia(token: str = Depends(oauth2Scheme)):
        if token is None:
            raise HTTPException(
                status_code=ERROR_TOKEN_INVALIDO.codigoHttp,
                detail=ERROR_TOKEN_INVALIDO.mensaje
            )
        try:
            usuario=verificarToken(token)
        except JWTError:
            raise HTTPException(
                status_code=ERROR_TOKEN_INVALIDO.codigoHttp,
                detail=ERROR_TOKEN_INVALIDO.mensaje
            )
        rol=usuario.get("rol")
        print(rol)
        rolPermiso=permisos.get(modulo, {}).get(rol, [])
        print(rolPermiso)
        if rolPermiso=="ALL" or accion in rolPermiso:
            return usuario
        else:
            raise HTTPException(
                status_code=403,
                detail="No tienes permiso para acceder a esta ruta"
            )
    return dependencia
    
    