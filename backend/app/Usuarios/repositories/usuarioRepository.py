from app.Usuarios.models.usuarioModel import Usuario
from app.Usuarios.schemas.usuarioSchemas import *
from sqlalchemy.orm import joinedload
class UsuarioRepository:
    def __init__(self, dbSession):
        self.dbSession = dbSession
    
    def validarCredenciales(self, cedula, password):
        return self.dbSession.query(Usuario).filter(Usuario.cedulaUsuario == cedula, Usuario.passwordUsuario == password).first()

    def listarUsuarios(self):
        return self.dbSession.query(Usuario).options(joinedload(Usuario.rol)).all()
    
    def obtenerUsuarioPorId(self, idUsuario: int):
        return (self.dbSession.query(Usuario)
                .options(joinedload(Usuario.rol)).filter(Usuario.idUsuario == idUsuario).first())

    def validarCedulaExistente(self, cedula):#Verificar si la cedula ya esta registrada
        return self.dbSession.query(Usuario).filter(Usuario.cedulaUsuario == cedula).first()
    
    def crearUsuario(self, usuario: UsuarioCrearSchema):
        usuario = Usuario(
            idRol=usuario.idRol,
            nombreCompleto=usuario.nombreCompleto,
            cedulaUsuario=usuario.cedulaUsuario,
            emailUsuario=usuario.emailUsuario,
            passwordUsuario=usuario.passwordUsuario,
            activoUsuario=True
        )

        if self.validarCedulaExistente(usuario.cedulaUsuario):
            return None
        self.dbSession.add(usuario)
        self.dbSession.commit()
        self.dbSession.refresh(usuario)       
        return usuario
    
    def modificarUsuario(self, idUsuario: int, usuarioActualizar: UsuarioActualizarSchema):
        usuario = self.obtenerUsuarioPorId(idUsuario)
        if not usuario:
            return None
        
        usuarioData=usuarioActualizar.model_dump(exclude_unset=True)
        camposValidos = ["idRol", "nombreCompleto", "emailUsuario", "passwordUsuario", "activoUsuario"]
        
        for campo, valor in usuarioData.items():
            if campo in camposValidos:
                setattr(usuario, campo, valor)
        
        self.dbSession.commit()
        self.dbSession.refresh(usuario)
        return usuario
    
    def deshabilitarUsuario(self, idUsuario: int):
        usuario = self.obtenerUsuarioPorId(idUsuario)
        if not usuario:
            return None
        usuario.activoUsuario = False
        self.dbSession.commit()
        self.dbSession.refresh(usuario)
        return usuario
    
    def crearUsuariosIniciales(self): #Crea datos para pruebas iniciales
        usuariosIniciales = [
            {"nombreCompleto": "admin", "cedulaUsuario": "admin", "emailUsuario": "admin@example.com", "passwordUsuario": "1234", "idRol": 1},
            {"nombreCompleto": "bodeguero", "cedulaUsuario": "bodeguero", "emailUsuario": "bodeguero@example.com", "passwordUsuario": "1234", "idRol": 2},
            {"nombreCompleto": "cajero", "cedulaUsuario": "cajero", "emailUsuario": "cajero@example.com", "passwordUsuario": "1234", "idRol": 3},
            {"nombreCompleto": "Damian Barahona", "cedulaUsuario": "1750834515", "emailUsuario": "damian@example.com", "passwordUsuario": "1234", "idRol": 1},
            {"nombreCompleto": "Kenin Cayambe", "cedulaUsuario": "1750834516", "emailUsuario": "kenin@example.com", "passwordUsuario": "1234", "idRol": 2},
            {"nombreCompleto": "Sthalin Chasipanta", "cedulaUsuario": "1750834517", "emailUsuario": "sthali@example.com", "passwordUsuario": "1234", "idRol": 2},
            {"nombreCompleto": "Cristian Licto", "cedulaUsuario": "1750834518", "emailUsuario": "cristian@example.com", "passwordUsuario": "1234", "idRol": 3},
            {"nombreCompleto": "Juan Tandazo", "cedulaUsuario": "1750834519", "emailUsuario": "juan@example.com", "passwordUsuario": "1234", "idRol": 3},

        ]

        for usuario in usuariosIniciales:
            existe=self.validarCedulaExistente(usuario["cedulaUsuario"])
            if not existe:
                usuario = Usuario(**usuario)
                self.dbSession.add(usuario)
        print("Usuarios por defecto creados...!")
        self.dbSession.commit()
        self.dbSession.close()
        

        