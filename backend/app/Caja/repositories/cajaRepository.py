from datetime import datetime, timezone, timedelta, date

from app.Inventario.repositories.inventarioRepository import InventarioRepository
from app.Productos.models.productoModel import Producto
from app.Caja.models.cajaHistorialModel import CajaHistorial
class CajaRepository:
    def __init__(self, dbSession):
        self.dbSession = dbSession

    def crearCajaHistorial(self, montoInicialDeclarado: float, idUsuarioCaja: int):
        # Verificar que no haya una caja ABIERTA para ese usuario
        abierta = self.dbSession.query(CajaHistorial).filter(CajaHistorial.idUsuarioCaja == idUsuarioCaja, CajaHistorial.estadoCaja == "ABIERTA").first()
        if abierta:
            return {"error": "caja_abierta_existente"}
        # Verificar que no exista ya una caja del mismo dia para el usuario
        quitoTZ = timezone(timedelta(hours=-5))
        hoy = datetime.now(quitoTZ).date()
        existe_hoy = self.dbSession.query(CajaHistorial).filter(CajaHistorial.idUsuarioCaja == idUsuarioCaja).filter(CajaHistorial.fechaAperturaCaja >= datetime.combine(hoy, datetime.min.time()).astimezone(quitoTZ)).first()
        if existe_hoy:
            return {"error": "caja_ya_abierta_hoy"}
        nuevo = CajaHistorial(
            idUsuarioCaja=idUsuarioCaja,
            fechaAperturaCaja=datetime.now(quitoTZ),
            montoInicialDeclarado=montoInicialDeclarado,
            estadoCaja="ABIERTA",
            detalle=f"Apertura: montoInicialDeclarado: {montoInicialDeclarado}"
        )
        # Nota: el detalle específico (actor) se puede completar por el servicio si se dispone del usuario que realiza la acción.
        self.dbSession.add(nuevo)
        self.dbSession.commit()
        self.dbSession.refresh(nuevo)
        return nuevo

    def cerrarCaja(self, idCaja: int, montoFinalDeclarado: float, closedBy: str | None = None, admin: bool = False):
        caja = self.obtenerPorId(idCaja)
        if not caja:
            return None
        if caja.estadoCaja != "ABIERTA":
            if caja.estadoCaja == "CERRADA":
                return {"error": "caja_ya_cerrada", "caja": caja}
            return {"error": "caja_no_abierta"}
        tz = timezone(timedelta(hours=-5))
        hoy = datetime.now(tz).date()
        fecha_cierre_dt = datetime.now(tz)
        if not admin:
            # Usuario normal: solo cerrar si la apertura fue hoy
            if caja.fechaAperturaCaja.date() != hoy:
                return {"error": "cierre_fuera_de_dia"}
            detalle_base = f"Cierre: cerrado por {closedBy} en la jornada correcta" if closedBy else "Cierre"
        else:
            # Admin: puede cerrar cualquier caja; si difiere de la jornada, marcar anomalía
            if caja.fechaAperturaCaja.date() != hoy:
                detalle_base = f"Cierre con anomalías (fecha cierre: {hoy.isoformat()})"
            else:
                detalle_base = "Cierre"
            if closedBy:
                detalle_base += f" por {closedBy}"
        caja.fechaCierreCaja = fecha_cierre_dt
        caja.montoCierreDeclarado = montoFinalDeclarado
        # Calcular montoCierreSistema: montoInicialDeclarado + suma de ventas en efectivo y no anuladas asociadas a esta caja
        try:
            from app.Venta.repositories.ventaRepository import VentaRepository
            venta_repo = VentaRepository(self.dbSession)
            ventas_efectivo = venta_repo.sumarVentasEfectivoNoAnuladasPorCaja(caja.idCaja)
        except Exception:
            ventas_efectivo = 0.0
        monto_inicial = caja.montoInicialDeclarado or 0.0
        monto_sistema = round(monto_inicial + (ventas_efectivo or 0.0), 2)
        caja.montoCierreSistema = monto_sistema
        caja.diferenciaCaja = round(montoFinalDeclarado - monto_sistema, 2)
        caja.estadoCaja = "CERRADA"
        caja.detalle = f"{detalle_base}; montoFinalDeclarado: {montoFinalDeclarado}; montoCierreSistema: {monto_sistema}; montoInicialDeclarado: {monto_inicial}"
        self.dbSession.commit()
        self.dbSession.refresh(caja)
        return caja

    def cerrarCajaPendiente(self, idCaja: int, montoFinalDeclarado: float, comentario: str | None = None, montoCierreSistema: float | None = None):
        caja = self.obtenerPorId(idCaja)
        if not caja:
            return None
        if caja.estadoCaja != "ABIERTA":
            if caja.estadoCaja == "CERRADA":
                return {"error": "caja_ya_cerrada", "caja": caja}
            return {"error": "caja_no_abierta"}
        # Permitir cerrar aunque sea otro dia
        tz = timezone(timedelta(hours=-5))
        caja.fechaCierreCaja = datetime.now(tz)
        caja.montoCierreDeclarado = montoFinalDeclarado
        # Si no se pasó montoCierreSistema, calcularlo (montoInicialDeclarado + ventas en efectivo no anuladas)
        if montoCierreSistema is None:
            try:
                from app.Venta.repositories.ventaRepository import VentaRepository
                venta_repo = VentaRepository(self.dbSession)
                ventas_efectivo = venta_repo.sumarVentasEfectivoNoAnuladasPorCaja(caja.idCaja)
            except Exception:
                ventas_efectivo = 0.0
            monto_inicial = caja.montoInicialDeclarado or 0.0
            montoCierreSistema = round(monto_inicial + (ventas_efectivo or 0.0), 2)
        caja.montoCierreSistema = montoCierreSistema
        caja.diferenciaCaja = round(montoFinalDeclarado - (montoCierreSistema or 0), 2)
        caja.estadoCaja = "CERRADA"
        detalle = f"Cierre fuera de tiempo"
        if comentario:
            detalle += f": {comentario}"
        detalle += f"; montoFinalDeclarado: {montoFinalDeclarado}; montoCierreSistema: {montoCierreSistema}"
        caja.detalle = detalle
        self.dbSession.commit()
        self.dbSession.refresh(caja)
        return caja

    def obtenerPorId(self, idCaja: int):
        return self.dbSession.query(CajaHistorial).filter(CajaHistorial.idCaja == idCaja).first()

    def reabrirCaja(self, idCaja: int, reabiertaPor: str | None = None):
        caja = self.obtenerPorId(idCaja)
        if not caja:
            return None
        if caja.estadoCaja != "CERRADA":
            return {"error": "caja_no_cerrada", "caja": caja}
        # Reabrir: limpiar campos de cierre y dejar ABIERTA
        caja.fechaCierreCaja = None
        caja.montoCierreDeclarado = None
        caja.montoCierreSistema = None
        caja.diferenciaCaja = None
        caja.estadoCaja = "ABIERTA"
        detalle_prev = caja.detalle or ""
        detalle_nuevo = detalle_prev + ("; "+f"Reabierta por {reabiertaPor}" if reabiertaPor else "; Reabierta")
        caja.detalle = detalle_nuevo
        self.dbSession.commit()
        self.dbSession.refresh(caja)
        return caja


    def listarCajasHoy(self, idUsuario: int = None, esAdmin: bool = False):
        tz = timezone(timedelta(hours=-5))
        hoy = datetime.now(tz).date()
        inicio = datetime.combine(hoy, datetime.min.time()).astimezone(tz)
        fin = datetime.combine(hoy, datetime.max.time()).replace(hour=23, minute=59, second=59, microsecond=0).astimezone(tz)
        query = self.dbSession.query(CajaHistorial).filter(CajaHistorial.fechaAperturaCaja >= inicio, CajaHistorial.fechaAperturaCaja <= fin)
        if not esAdmin and idUsuario:
            query = query.filter(CajaHistorial.idUsuarioCaja == idUsuario)
        return query.all()

    def listarCajas(self, idUsuario: int = None, esAdmin: bool = False):
        if esAdmin:
            return self.dbSession.query(CajaHistorial).all()
        return self.dbSession.query(CajaHistorial).filter(CajaHistorial.idUsuarioCaja == idUsuario).all()

    def filtrarCaja(self, idUsuario: int, fecha: date):
        tz = timezone(timedelta(hours=-5))
        inicio = datetime.combine(fecha, datetime.min.time()).astimezone(tz)
        fin = datetime.combine(fecha, datetime.max.time()).replace(hour=23, minute=59, second=59, microsecond=0).astimezone(tz)
        return self.dbSession.query(CajaHistorial).filter(CajaHistorial.idUsuarioCaja == idUsuario, CajaHistorial.fechaAperturaCaja >= inicio, CajaHistorial.fechaAperturaCaja <= fin).all()