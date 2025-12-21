from app.Venta.models.ventaModel import Venta
from app.Venta.models.detalleVentaModel import DetalleVenta
from app.Productos.models.productoModel import Producto
from app.Inventario.repositories.inventarioRepository import InventarioRepository
from app.Venta.repositories.promocionRepository import PromocionRepository
from app.Clientes.repositories.clienteRepository import ClienteRepository
from datetime import datetime, timezone, timedelta
from sqlalchemy.orm import joinedload

class VentaRepository:
    def __init__(self, dbSession):
        self.dbSession = dbSession

    def obtenerPorId(self, idVenta: int):
        # Cargar relaciones necesarias para respuestas completas
        return self.dbSession.query(Venta).options(
            joinedload(Venta.detalles),
            joinedload(Venta.usuario),
            joinedload(Venta.cliente)
        ).filter(Venta.idVenta == idVenta).first()

    def listarVentasHoy(self, idUsuario: int = None, esAdmin: bool = False):
        tz = timezone(timedelta(hours=-5))
        hoy = datetime.now(tz).date()
        inicio = datetime.combine(hoy, datetime.min.time()).astimezone(tz)
        fin = datetime.combine(hoy, datetime.max.time()).replace(hour=23, minute=59, second=59, microsecond=0).astimezone(tz)
        query = self.dbSession.query(Venta).options(joinedload(Venta.detalles)).filter(Venta.fechaVenta >= inicio, Venta.fechaVenta <= fin)
        if not esAdmin and idUsuario:
            query = query.filter(Venta.idUsuarioVenta == idUsuario)
        return query.all()

    def listarTodas(self):
        return self.dbSession.query(Venta).options(joinedload(Venta.detalles)).all()

    def crearVenta(self, venta: Venta, detalles: list):
        self.dbSession.add(venta)
        self.dbSession.commit()
        self.dbSession.refresh(venta)
        for d in detalles:
            d.idVenta = venta.idVenta
            self.dbSession.add(d)
        self.dbSession.commit()
        self.dbSession.refresh(venta)
        return venta

    def sumarVentasEfectivoNoAnuladasPorCaja(self, idCaja: int):
        """Devuelve la suma de totalPagar de las ventas en efectivo y no anuladas para una caja dada."""
        from sqlalchemy import func
        suma = self.dbSession.query(func.coalesce(func.sum(Venta.totalPagar), 0)).filter(
            Venta.idCaja == idCaja,
            Venta.metodoPago == "Efectivo",
            Venta.estadoVenta != "ANULADA"
        ).scalar()
        try:
            return float(suma or 0.0)
        except Exception:
            return 0.0

    def anularVenta(self, idVenta: int):
        venta = self.obtenerPorId(idVenta)
        if not venta:
            return None
        if venta.estadoVenta == "ANULADA":
            return {"error": "venta_ya_anulada", "venta": venta}
        venta.estadoVenta = "ANULADA"
        # revertir inventario
        invRepo = InventarioRepository(self.dbSession)
        for d in venta.detalles:
            inventario = invRepo.obtenerPorProducto(d.idProducto)
            if inventario:
                inventario.cantidadDisponible = (inventario.cantidadDisponible or 0) + (d.cantidadVendida or 0)
                self.dbSession.add(inventario)
        self.dbSession.commit()
        self.dbSession.refresh(venta)
        return venta