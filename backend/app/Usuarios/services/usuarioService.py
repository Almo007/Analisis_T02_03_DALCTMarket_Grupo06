from app.Usuarios.repositories.usuarioRepository import UsuarioRepository
from app.configuracionGeneral.schemasGenerales import respuestaApi
from fastapi import HTTPException
from app.Usuarios.schemas.usuarioSchemas import *

class UsuarioService:
    def __init__(self, dbSession):
        self.dbSession = dbSession
        self.usuarioRepository = UsuarioRepository(dbSession)


    def validarCredenciales(self, cedula, password):
        print(cedula, password)
        usuario=self.usuarioRepository.validarCredenciales(cedula, password)
        print(usuario)
        if usuario is None:
            raise HTTPException(status_code=401, detail="Credenciales incorrectas")
      
        usuario=UsuarioRespuestaSchema.from_orm(usuario).model_dump()
        
     
        if usuario["activoUsuario"] == False:
            raise HTTPException(status_code=403, detail="El usuario esta deshabilitado")
        #devolver el idUsuario, cedula, nombreCompleto, idRol y rol como diccionario para el JWT
        usuario={
            "idUsuario": usuario["idUsuario"],
            "cedula": usuario["cedulaUsuario"],
            "nombreCompleto": usuario["nombreCompleto"],
            "idRol": usuario["rol"]["idRol"],
            "rol": usuario["rol"]["nombreRol"]
        }

        return usuario
        
    def listarUsuarios(self):
        usuarios=self.usuarioRepository.listarUsuarios()
        if usuarios is None:
            return respuestaApi(success=True, message="No se encontraron usuarios", data=[])
        usuarios=[UsuarioRespuestaSchema.from_orm(usuario) for usuario in usuarios]
        return respuestaApi(success=True, message="Usuarios encontrados", data=usuarios) 

    def obtenerPorId(self, idUsuario: int):
        usuario=self.usuarioRepository.obtenerUsuarioPorId(idUsuario)
        if usuario is None:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        usuario=UsuarioRespuestaSchema.from_orm(usuario)
        return respuestaApi(success=True, message="Usuario encontrado", data=usuario)   
    
    def crearUsuario(self, usuario: UsuarioCrearSchema):
        usuarioCreado=self.usuarioRepository.crearUsuario(usuario)
        if usuarioCreado is None:
            raise HTTPException(status_code=400, detail="La cedula ya esta registrada")
        
        usuarioCreado=UsuarioRespuestaSchema.from_orm(usuarioCreado)

        return respuestaApi(success=True, message="Usuario creado", data=usuarioCreado)
    
    def modificarUsuario(self, idUsuario: int, usuario: UsuarioActualizarSchema):
        usuarioActualizado=self.usuarioRepository.modificarUsuario(idUsuario, usuario)
        if usuarioActualizado is None:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        usuarioActualizado=UsuarioRespuestaSchema.from_orm(usuarioActualizado)
        return respuestaApi(success=True, message="Usuario actualizado", data=usuarioActualizado)

    def deshabilitarUsuario(self, idUsuario: int):
        usuarioDeshabilitado=self.usuarioRepository.deshabilitarUsuario(idUsuario)
        if usuarioDeshabilitado is None:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        usuarioDeshabilitado=UsuarioRespuestaSchema.from_orm(usuarioDeshabilitado)
        return respuestaApi(success=True, message="Usuario deshabilitado", data=usuarioDeshabilitado)
    
    
    
    
    
    