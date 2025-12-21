from app.Venta.models.promocionModel import Promocion
from app.Productos.models.productoModel import Producto
from sqlalchemy.orm import joinedload
from datetime import datetime, timezone, timedelta

class PromocionRepository:
    def __init__(self, dbSession):
        self.dbSession = dbSession

    def listarPromociones(self):
        return self.dbSession.query(Promocion).options(joinedload(Promocion.producto)).all()

    def obtenerPorId(self, idPromocion: int):
        return self.dbSession.query(Promocion).options(joinedload(Promocion.producto)).filter(Promocion.idPromocion == idPromocion).first()

    def crearPromocion(self, promocionCrear, idUsuarioCreador=None):
        # Validar producto
        producto = self.dbSession.query(Producto).filter(Producto.idProducto == promocionCrear.idProducto).first()
        if not producto:
            return {"error": "producto_no_encontrado"}
        if not getattr(producto, "activoProducto", True):
            return {"error": "producto_inactivo"}
        # Las fechas ya fueron validadas en el schema; construir datetimes con horas apropiadas
        quitoTZ = timezone(timedelta(hours=-5))
        now = datetime.now(quitoTZ)
        fecha_inicio = datetime.combine(promocionCrear.fechaInicioPromocion, now.time()).astimezone(quitoTZ)
        fecha_fin = datetime.combine(promocionCrear.fechaFinPromocion, datetime.max.time()).replace(hour=23, minute=59, second=59, microsecond=0).astimezone(quitoTZ)
        nuevo = Promocion(
            idProducto=promocionCrear.idProducto,
            nombrePromocion=promocionCrear.nombrePromocion,
            porcentajePromocion=promocionCrear.porcentajePromocion,
            fechaInicioPromocion=fecha_inicio,
            fechaFinPromocion=fecha_fin,
            activoPromocion=True
        )
        self.dbSession.add(nuevo)
        self.dbSession.commit()
        self.dbSession.refresh(nuevo)
        return nuevo

    def obtenerPromocionesActivasPorProducto(self, idProducto: int):
        tz = timezone(timedelta(hours=-5))
        ahora = datetime.now(tz)
        return (self.dbSession.query(Promocion)
                .filter(Promocion.idProducto == idProducto, Promocion.activoPromocion == True, Promocion.fechaInicioPromocion <= ahora, Promocion.fechaFinPromocion >= ahora)
                .all())

    def deshabilitarPromocion(self, idPromocion: int):
        promo = self.dbSession.query(Promocion).filter(Promocion.idPromocion == idPromocion).first()
        if not promo:
            return None
        promo.activoPromocion = False
        self.dbSession.commit()
        self.dbSession.refresh(promo)
        return promo

    def obtenerPromocionActivaMayorDescuento(self, idProducto: int):
        tz = timezone(timedelta(hours=-5))
        ahora = datetime.now(tz)
        promos = (self.dbSession.query(Promocion)
                  .filter(Promocion.idProducto == idProducto, Promocion.activoPromocion == True, Promocion.fechaInicioPromocion <= ahora, Promocion.fechaFinPromocion >= ahora)
                  .order_by(Promocion.porcentajePromocion.desc()).all())
        return promos[0] if promos else None

    def crearPromocionesIniciales(self):
        """Crea dos promociones de prueba si no existen promociones en la base:
        - Una promoción con fechas ya pasadas (start -60d / end -30d)
        - Una promoción que inicia hoy y finaliza en +30 días
        Las promociones usan los productos 'Cola 2 Litros' y 'Jugo de Naranja 1L' si existen.
        """
        existe = self.dbSession.query(Promocion).first()
        if existe:
            return
        # Buscar productos de prueba
        producto1 = self.dbSession.query(Producto).filter(Producto.nombreProducto == "Cola 2 Litros").first()
        producto2 = self.dbSession.query(Producto).filter(Producto.nombreProducto == "Jugo de Naranja 1L").first()
        if not producto1 or not producto2:
            return
        quitoTZ = timezone(timedelta(hours=-5))
        hoy = datetime.now(quitoTZ).date()
        # Promoción pasada
        inicio_pasado = hoy - timedelta(days=60)
        fin_pasado = hoy - timedelta(days=30)
        fecha_inicio_pasado = datetime.combine(inicio_pasado, datetime.now(quitoTZ).time()).astimezone(quitoTZ)
        fecha_fin_pasado = datetime.combine(fin_pasado, datetime.max.time()).replace(hour=23, minute=59, second=59, microsecond=0).astimezone(quitoTZ)
        promo_pasada = Promocion(
            idProducto=producto1.idProducto,
            nombrePromocion="Promoción Pasada",
            porcentajePromocion=10.0,
            fechaInicioPromocion=fecha_inicio_pasado,
            fechaFinPromocion=fecha_fin_pasado,
            activoPromocion=True
        )
        self.dbSession.add(promo_pasada)
        # Promoción vigente (hoy -> +30 días)
        inicio_act = hoy
        fin_act = hoy + timedelta(days=30)
        fecha_inicio_act = datetime.combine(inicio_act, datetime.now(quitoTZ).time()).astimezone(quitoTZ)
        fecha_fin_act = datetime.combine(fin_act, datetime.max.time()).replace(hour=23, minute=59, second=59, microsecond=0).astimezone(quitoTZ)
        promo_actual = Promocion(
            idProducto=producto2.idProducto,
            nombrePromocion="Promoción Actual",
            porcentajePromocion=25.0,
            fechaInicioPromocion=fecha_inicio_act,
            fechaFinPromocion=fecha_fin_act,
            activoPromocion=True
        )
        self.dbSession.add(promo_actual)
        self.dbSession.commit()
        self.dbSession.close()
        print("Promociones por defecto creadas...!")
