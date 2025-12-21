from pydantic import BaseModel,Field,EmailStr,field_validator
from typing import Optional,Literal
from app.Usuarios.schemas.rolSchemas import RolSchema
# Esquema de Autenticación
class IniciarSesionRequest(BaseModel):
    username: str 
    password: str





# Esquema de Usuario

def validarPassword(v: str) -> str:
    if len(v) < 8:
        raise ValueError("La contraseña debe tener al menos 8 caracteres")
    if not any(c.islower() for c in v):
        raise ValueError("Debe contener al menos una letra minúscula")
    if not any(c.isupper() for c in v):
        raise ValueError("Debe contener al menos una letra mayúscula")
    if not any(c.isdigit() for c in v):
        raise ValueError("Debe contener al menos un número")
    return v

class UsuarioBaseSchema(BaseModel):
    nombreCompleto: str = Field(..., min_length=3, max_length=50,example="Juan Perez")
    cedulaUsuario: str = Field(..., min_length=10, max_length=10,example="1750834515")
    emailUsuario: EmailStr = Field(..., example="juan.perez@example.com")
    passwordUsuario: str = Field(..., min_length=8,example="Cl@veSegura123")

    @field_validator("passwordUsuario")
    def validar_password(cls, v: str) -> str:
        return validarPassword(v)


class UsuarioCrearSchema(UsuarioBaseSchema):
    idRol: Literal[1, 2, 3] = Field(..., example=1)

class UsuarioActualizarSchema(BaseModel):
    idRol: Optional[Literal[1, 2, 3]] = Field(None, example=1)
    nombreCompleto: Optional[str] = Field(None, min_length=3, max_length=50,example="Juan Perez")
    emailUsuario: Optional[EmailStr] = Field(None, example="juan.perez@example.com")
    passwordUsuario: Optional[str] = Field(None, min_length=8,example="Cl@veSegura123")
    activoUsuario: Optional[bool] = None
    @field_validator("passwordUsuario")
    def validar_password(cls, v: str) -> str:
        return validarPassword(v)


class UsuarioRespuestaSchema(BaseModel):
    idUsuario: int
    nombreCompleto: str
    cedulaUsuario: str
    emailUsuario: EmailStr
    passwordUsuario: str
    rol: RolSchema
    activoUsuario: bool
    class Config:
        from_attributes = True


# Schema público paralelo que NO devuelve la contraseña
class UsuarioPublicoSchema(BaseModel):
    idUsuario: int
    nombreCompleto: str
    cedulaUsuario: str
    emailUsuario: EmailStr
    rol: RolSchema
    activoUsuario: bool
    class Config:
        from_attributes = True



    
    

