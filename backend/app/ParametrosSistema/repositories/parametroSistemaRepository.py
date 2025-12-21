from app.ParametrosSistema.models.parametroSistemaModel import ParametroSistema
from app.ParametrosSistema.schemas.parametroSistemaSchemas import *

class ParametroSistemaRepository:
    def __init__(self, dbSession):
        self.dbSession = dbSession

    def listarParametros(self):
        return self.dbSession.query(ParametroSistema).all()

    def obtenerPorId(self, idParametro: int):
        return self.dbSession.query(ParametroSistema).filter(ParametroSistema.idParametroSistema == idParametro).first()

    def validarClaveExistente(self, clave: str, excluirId: int = None):
        query = self.dbSession.query(ParametroSistema).filter(ParametroSistema.claveParametro == clave)
        if excluirId is not None:
            query = query.filter(ParametroSistema.idParametroSistema != excluirId)
        return query.first()

    def crearParametro(self, parametro: ParametroSistemaCrearSchema):
        if self.validarClaveExistente(parametro.claveParametro):
            return None
        nuevo = ParametroSistema(claveParametro=parametro.claveParametro, valorParametro=parametro.valorParametro)
        self.dbSession.add(nuevo)
        self.dbSession.commit()
        self.dbSession.refresh(nuevo)
        return nuevo

    def modificarParametro(self, idParametro: int, parametroActualizar: ParametroSistemaActualizarSchema):
        parametro = self.obtenerPorId(idParametro)
        if not parametro:
            return None
        datos = parametroActualizar.model_dump(exclude_unset=True)
        # Validar que la nueva clave (si viene) no exista en otro registro
        if "claveParametro" in datos:
            claveNueva = datos["claveParametro"]
            # Buscar por clave sin excluir y verificar explícitamente el id
            existente = self.validarClaveExistente(claveNueva)
            if existente and existente.idParametroSistema != idParametro:
                # Retornar bandera False para indicar conflicto de clave
                return False
        for campo, valor in datos.items():
            if campo in ["claveParametro", "valorParametro"]:
                setattr(parametro, campo, valor)
        self.dbSession.commit()
        self.dbSession.refresh(parametro)
        return parametro

    def deshabilitarParametro(self, idParametro: int):
        parametro = self.obtenerPorId(idParametro)
        if not parametro:
            return None
        parametro.activoParametro = False
        self.dbSession.commit()
        self.dbSession.refresh(parametro)
        return parametro

    def crearParametrosIniciales(self):
        parametrosIniciales = [
            {"claveParametro": "nombreNegocio", "valorParametro": "DALCT Market"},
            {"claveParametro": "direccionNegocio", "valorParametro": "Quito, Av. Morán Valverde y OE3H"},
            {"claveParametro": "telefonoNegocio", "valorParametro": "02-3450538"},
            {"claveParametro": "correoNegocio", "valorParametro": "contacto@dalctmarket.com"},
            {"claveParametro": "IVA", "valorParametro": "15"},
            {"claveParametro": "logoNegocio", "valorParametro": "/static/logo.png"},
        ]

        for p in parametrosIniciales:
            existe = self.validarClaveExistente(p["claveParametro"])
            if not existe:
                nuevo = ParametroSistema(**p)
                self.dbSession.add(nuevo)
        print("Parámetros por defecto creados...!")
        self.dbSession.commit()
        self.dbSession.close()
