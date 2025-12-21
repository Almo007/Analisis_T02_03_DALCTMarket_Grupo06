from app.Caja.repositories.cajaRepository import CajaRepository
from app.configuracionGeneral.schemasGenerales import respuestaApi
from app.configuracionGeneral.seguridadJWT import identificarUsuarioString
from app.Usuarios.repositories.usuarioRepository import UsuarioRepository
from fastapi import HTTPException

from app.Caja.schemas.cajaSchemas import *

class CajaService:
    def __init__(self, dbSession):
        self.dbSession = dbSession
        self.repo = CajaRepository(dbSession)

    def _attach_usuario(self, caja_obj):
        """Asegura que la relación `usuario` esté poblada en la entidad `CajaHistorial` para serializarla."""
        if not getattr(caja_obj, "usuario", None):
            usuario_entity = UsuarioRepository(self.dbSession).obtenerUsuarioPorId(caja_obj.idUsuarioCaja)
            if usuario_entity:
                caja_obj.usuario = usuario_entity
        return caja_obj

    def crearCajaHistorial(self, cajaCrear: CajaCrearSchema, usuario: dict):
        idUsuario = usuario.get("idUsuario")
        actor = identificarUsuarioString(usuario)
        # montoInicial es un número provisto por el cliente
        monto_calc = round(float(cajaCrear.montoInicial), 2)
        resultado = self.repo.crearCajaHistorial(monto_calc, idUsuario)
        if isinstance(resultado, dict) and resultado.get("error"):
            if resultado.get("error") == "caja_abierta_existente":
                raise HTTPException(status_code=400, detail=f"Ya existe una caja abierta para el usuario {actor}")
            if resultado.get("error") == "caja_ya_abierta_hoy":
                raise HTTPException(status_code=400, detail=f"Ya existe una caja para hoy para el usuario {actor}")
        # Añadir detalle con identificación del actor
        resultado.detalle = f"Apertura por {actor}; montoInicialDeclarado: {monto_calc}"
        self.dbSession.add(resultado)
        self.dbSession.commit()
        self.dbSession.refresh(resultado)
        # Adjuntar usuario para serializar en la respuesta
        resultado = self._attach_usuario(resultado)
        data = CajaHistorialRespuestaSchema.from_orm(resultado)
        mensaje = f"Caja abierta por {actor} (monto inicial: {data.montoInicialDeclarado})"
        return respuestaApi(success=True, message=mensaje, data=data)

    def cerrarCaja(self, idCaja: int, cerrar: CajaCerrarSchema, usuario: dict):
        # permisos: solo Cajero (propietario) o Administrador pueden cerrar
        rol = usuario.get("rol")
        idUsuario = usuario.get("idUsuario")
        caja = self.repo.obtenerPorId(idCaja)
        if not caja:
            raise HTTPException(status_code=404, detail="Caja no encontrada")
        # Si la caja ya está cerrada, devolver respuestaApi con success=False, mensaje y la caja en data
        if caja.estadoCaja == "CERRADA":
            caja = self._attach_usuario(caja)
            data = CajaHistorialRespuestaSchema.from_orm(caja)
            return respuestaApi(success=False, message="La caja ya está cerrada", data=data)
        monto_final = round(float(cerrar.montoFinal), 2)
        actor = identificarUsuarioString(usuario)

        # Cajero: solo puede cerrar SU caja abierta del día actual
        if rol != "Administrador":
            if caja.idUsuarioCaja != idUsuario:
                raise HTTPException(status_code=403, detail="No tiene permisos para cerrar esta caja")
            # Validar que la apertura sea hoy
            from datetime import datetime
            tz = datetime.now().astimezone()
            hoy = datetime.now(tz.tzinfo).date()
            if caja.fechaAperturaCaja.date() != hoy:
                raise HTTPException(status_code=400, detail=f"Solo puede cerrar cajas abiertas hoy. Usuario: {actor}")
            resultado = self.repo.cerrarCaja(idCaja, monto_final, closedBy=actor, admin=False)
        else:
            # Administrador: puede cerrar cualquier caja por id, enviando solo montoFinal
            resultado = self.repo.cerrarCaja(idCaja, monto_final, closedBy=actor, admin=True)

        if resultado is None:
            raise HTTPException(status_code=404, detail="Caja no encontrada")
        if isinstance(resultado, dict) and resultado.get("error") == "cierre_fuera_de_dia":
            raise HTTPException(status_code=400, detail="La caja fue abierta en un día distinto")
        if isinstance(resultado, dict) and resultado.get("error") == "caja_no_abierta":
            raise HTTPException(status_code=400, detail="La caja no está abierta")
        if isinstance(resultado, dict) and resultado.get("error") == "caja_ya_cerrada":
            caja_obj = resultado.get("caja")
            caja_obj = self._attach_usuario(caja_obj)
            data = CajaHistorialRespuestaSchema.from_orm(caja_obj)
            return respuestaApi(success=False, message="La caja ya está cerrada", data=data)
        resultado = self._attach_usuario(resultado)
        data = CajaHistorialRespuestaSchema.from_orm(resultado)
        mensaje = f"Caja cerrada por {actor} (monto cierre declarado: {data.montoCierreDeclarado})"
        return respuestaApi(success=True, message=mensaje, data=data)



    def listarCajas(self, usuario: dict):
        rol = usuario.get("rol")
        idUsuario = usuario.get("idUsuario")
        esAdmin = rol == "Administrador"
        cajas = self.repo.listarCajas(idUsuario if not esAdmin else None, esAdmin)
        if not cajas:
            return respuestaApi(success=True, message="No se encontraron cajas", data=[])
        # Adjuntar usuario en cada caja antes de serializar
        for c in cajas:
            self._attach_usuario(c)
        data = [CajaHistorialRespuestaSchema.from_orm(c) for c in cajas]
        return respuestaApi(success=True, message="Cajas encontradas", data=data)

    def listarCajasHoy(self, usuario: dict):
        rol = usuario.get("rol")
        idUsuario = usuario.get("idUsuario")
        esAdmin = rol == "Administrador"
        cajas = self.repo.listarCajasHoy(idUsuario if not esAdmin else None, esAdmin)
        if not cajas:
            return respuestaApi(success=True, message="No se han abierto cajas hoy", data=[])
        for c in cajas:
            self._attach_usuario(c)
        data = [CajaHistorialRespuestaSchema.from_orm(c) for c in cajas]
        return respuestaApi(success=True, message="Cajas del día encontradas", data=data)
    def listarTodasCajas(self, usuario: dict):
        rol = usuario.get("rol")
        if rol != "Administrador":
            raise HTTPException(status_code=403, detail="Solo Administrador puede listar todas las cajas")
        cajas = self.repo.listarCajas(None, True)
        if not cajas:
            return respuestaApi(success=True, message="No se encontraron cajas", data=[])
        for c in cajas:
            self._attach_usuario(c)
        data = [CajaHistorialRespuestaSchema.from_orm(c) for c in cajas]
        return respuestaApi(success=True, message="Cajas encontradas", data=data)

    def filtrarCaja(self, idUsuario: int, fecha: date, usuario: dict):
        # Solo Administrador puede usar este endpoint
        rol = usuario.get("rol")
        if rol != "Administrador":
            raise HTTPException(status_code=403, detail="Solo Administrador puede filtrar cajas")
        resultados = self.repo.filtrarCaja(idUsuario, fecha)
        if not resultados:
            return respuestaApi(success=True, message="No se encontraron cajas para los parámetros proporcionados", data=[])
        for r in resultados:
            self._attach_usuario(r)
        data = [CajaHistorialRespuestaSchema.from_orm(r) for r in resultados]
        return respuestaApi(success=True, message="Cajas encontradas", data=data)

    def reabrirCaja(self, idCaja: int, usuario: dict):
        # Solo Administrador puede reabrir cajas cerradas
        rol = usuario.get("rol")
        idUsuario = usuario.get("idUsuario")
        if rol != "Administrador":
            raise HTTPException(status_code=403, detail="Solo Administrador puede reabrir cajas")
        caja = self.repo.obtenerPorId(idCaja)
        if not caja:
            raise HTTPException(status_code=404, detail="Caja no encontrada")
        if caja.estadoCaja != "CERRADA":
            data = CajaHistorialRespuestaSchema.from_orm(caja)
            return respuestaApi(success=False, message="La caja no está cerrada", data=data)
        reabierta_por = identificarUsuarioString(usuario)
        resultado = self.repo.reabrirCaja(idCaja, reabiertaPor=reabierta_por)
        if resultado is None:
            raise HTTPException(status_code=404, detail="Caja no encontrada")
        if isinstance(resultado, dict) and resultado.get("error") == "caja_no_cerrada":
            caja_obj = resultado.get("caja")
            caja_obj = self._attach_usuario(caja_obj)
            data = CajaHistorialRespuestaSchema.from_orm(caja_obj)
            return respuestaApi(success=False, message=f"La caja no está cerrada. Usuario: {reabierta_por}", data=data)
        resultado = self._attach_usuario(resultado)
        data = CajaHistorialRespuestaSchema.from_orm(resultado)
        mensaje = f"Caja reabierta por {reabierta_por}"
        return respuestaApi(success=True, message=mensaje, data=data)