from pydantic import BaseModel

# Esquema de Autenticación
class IniciarSesionRequest(BaseModel):
    username: str 
    password: str

