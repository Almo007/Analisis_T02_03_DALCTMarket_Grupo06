from app.Venta.repositories.promocionRepository import PromocionRepository
from app.configuracionGeneral.schemasGenerales import respuestaApi
from fastapi import HTTPException
from app.Venta.schemas.promocionSchemas import PromocionCrearSchema, PromocionRespuestaSchema
from datetime import datetime

class PromocionService:
    def __init__(self, dbSession):
        self.dbSession = dbSession
        self.repo = PromocionRepository(dbSession)

    def listarPromociones(self):
        promos = self.repo.listarPromociones()
        if not promos:
            return respuestaApi(success=True, message="No se encontraron promociones", data=[])
        data = [PromocionRespuestaSchema.from_orm(p) for p in promos]
        return respuestaApi(success=True, message="Promociones encontradas", data=data)

    def obtenerPorId(self, idPromocion: int):
        promo = self.repo.obtenerPorId(idPromocion)
        if not promo:
            raise HTTPException(status_code=404, detail="Promoción no encontrada")
        data = PromocionRespuestaSchema.from_orm(promo)
        return respuestaApi(success=True, message="Promoción encontrada", data=data)

    def crearPromocion(self, promocion: PromocionCrearSchema, usuario: dict):
        # validaciones adicionales: porcentaje en rango (ya en schema), fechas válidas en esquema
        resultado = self.repo.crearPromocion(promocion, idUsuarioCreador=usuario.get("idUsuario"))
        if isinstance(resultado, dict) and resultado.get("error"):
            if resultado.get("error") == "producto_no_encontrado":
                raise HTTPException(status_code=400, detail="Producto no encontrado")
            if resultado.get("error") == "producto_inactivo":
                raise HTTPException(status_code=400, detail="Producto inactivo")
            raise HTTPException(status_code=400, detail=resultado)
        data = PromocionRespuestaSchema.from_orm(resultado)
        return respuestaApi(success=True, message="Promoción creada", data=data)

    def obtenerActivasPorProducto(self, idProducto: int):
        promos = self.repo.obtenerPromocionesActivasPorProducto(idProducto)
        if not promos:
            return respuestaApi(success=True, message="No se encontraron promociones activas para este producto", data=[])
        data = [PromocionRespuestaSchema.from_orm(p) for p in promos]
        return respuestaApi(success=True, message="Promociones activas encontradas", data=data)

    def deshabilitarPromocion(self, idPromocion: int):
        des = self.repo.deshabilitarPromocion(idPromocion)
        if des is None:
            raise HTTPException(status_code=404, detail="Promoción no encontrada")
        data = PromocionRespuestaSchema.from_orm(des)
        return respuestaApi(success=True, message="Promoción deshabilitada", data=data)

    def obtenerPromocionAplicable(self, idProducto: int):
        promo = self.repo.obtenerPromocionActivaMayorDescuento(idProducto)
        if promo is None:
            return respuestaApi(success=True, message="No hay promociones aplicables", data=None)
        data = PromocionRespuestaSchema.from_orm(promo)
        return respuestaApi(success=True, message="Promoción aplicable", data=data)
