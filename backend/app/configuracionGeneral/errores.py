from fastapi import status

class ErrorBase:
    def __init__(self, codigoHttp: int, mensaje: str):
        self.codigoHttp = codigoHttp
        self.mensaje = mensaje

# JWT / Autenticación
ERROR_TOKEN_INVALIDO = ErrorBase(
    status.HTTP_401_UNAUTHORIZED,
    "Token inválido o expirado"
)

# Negocio
ERROR_CREDENCIALES = ErrorBase(
    status.HTTP_401_UNAUTHORIZED,
    "Credenciales incorrectas"
)



