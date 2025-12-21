from app.Inventario.repositories.inventarioRepository import InventarioRepository
from app.Productos.models.productoModel import Producto
from app.Productos.models.categoriaProductoModel import CategoriaProducto
from app.Venta.models.detalleVentaModel import DetalleVenta
from app.Venta.models.ventaModel import Venta
from app.Caja.models.cajaHistorialModel import CajaHistorial
from app.Clientes.modells.clienteModel import Cliente
from sqlalchemy import func
from datetime import datetime, timedelta
from sqlalchemy.orm import joinedload

class ReporteRepository:
    def __init__(self, dbSession):
        self.dbSession = dbSession

    def reporte_inventario(self, idProducto=None, idCategoria=None, nombreProducto=None):
        """Filtros opcionales: se pueden combinar. Se aplican de forma conjunta (AND) si se envían varios."""
        invRepo = InventarioRepository(self.dbSession)
        inventarios = invRepo.listarInventarios()
        resultados = []
        for inv in inventarios:
            p = getattr(inv, 'producto', None)
            if idProducto is not None and inv.idProducto != idProducto:
                continue
            if idCategoria is not None and not (p and p.idCategoriaProducto == idCategoria):
                continue
            if nombreProducto and not (p and nombreProducto.lower() in (p.nombreProducto or '').lower()):
                continue
            resultados.append(inv)
        return resultados

    def reporte_ventas_por_producto_categoria(self, fechaInicio, fechaFin, idProducto=None, idCategoria=None):
        # construir rango de fechas (fechas ya validadas por el servicio)
        q = self.dbSession.query(
            DetalleVenta.idProducto,
            Producto.nombreProducto,
            Producto.idCategoriaProducto,
            CategoriaProducto.nombreCategoria,
            func.coalesce(func.sum(DetalleVenta.cantidadVendida),0).label('cantidadVendida'),
            func.coalesce(func.sum(DetalleVenta.subtotalProducto - DetalleVenta.valorDescuentoProducto),0).label('ingresos')
        ).join(Producto, Producto.idProducto == DetalleVenta.idProducto)
        q = q.join(CategoriaProducto, CategoriaProducto.idCategoriaProducto == Producto.idCategoriaProducto)
        q = q.join(Venta, Venta.idVenta == DetalleVenta.idVenta)
        inicio = datetime.combine(fechaInicio, datetime.min.time())
        fin = datetime.combine(fechaFin, datetime.max.time())
        q = q.filter(Venta.fechaVenta >= inicio, Venta.fechaVenta <= fin)
        if idProducto is not None:
            q = q.filter(DetalleVenta.idProducto == idProducto)
        if idCategoria is not None:
            q = q.filter(Producto.idCategoriaProducto == idCategoria)
        q = q.group_by(DetalleVenta.idProducto, Producto.nombreProducto, Producto.idCategoriaProducto, CategoriaProducto.nombreCategoria)
        return q.all()

    def resumen_caja_diaria(self, fecha: datetime.date, idUsuarioCaja: int):
        from datetime import datetime
        tz = datetime.now().astimezone().tzinfo
        inicio = datetime.combine(fecha, datetime.min.time()).astimezone(tz)
        fin = datetime.combine(fecha, datetime.max.time()).replace(hour=23, minute=59, second=59, microsecond=0).astimezone(tz)
        # Buscar la(s) caja(s) del cajero en la fecha
        query = self.dbSession.query(CajaHistorial).filter(CajaHistorial.fechaAperturaCaja >= inicio, CajaHistorial.fechaAperturaCaja <= fin, CajaHistorial.idUsuarioCaja == idUsuarioCaja)
        cajas = query.options(joinedload(CajaHistorial.usuario)).all()
        # Para cada caja, traer las ventas y sus detalles
        for c in cajas:
            ventas = self.dbSession.query(Venta).options(joinedload(Venta.detalles)).filter(Venta.idCaja == c.idCaja).all()
            c.ventas = ventas
        return cajas

    def clientes_frecuentes(self, dias=30, minVentas=3, minGasto=100.0):
        desde = datetime.now() - timedelta(days=dias)
        # sumar ventas por cliente
        q = self.dbSession.query(
            Venta.idCliente,
            func.count(Venta.idVenta).label('ventasCount'),
            func.coalesce(func.sum(Venta.totalPagar),0).label('totalGastado')
        ).filter(Venta.fechaVenta >= desde).group_by(Venta.idCliente).having(func.count(Venta.idVenta) >= minVentas, func.sum(Venta.totalPagar) >= minGasto)
        clientes = q.all()
        # obtener historial completo para cada cliente
        resultados = []
        for c in clientes:
            cliente_entity = self.dbSession.query(Cliente).filter(Cliente.idCliente == c.idCliente).first()
            ventas = self.dbSession.query(Venta).options(joinedload(Venta.detalles)).filter(Venta.idCliente == c.idCliente, Venta.fechaVenta >= desde).all()
            resultados.append({'cliente': cliente_entity, 'ventasCount': c.ventasCount, 'totalGastado': float(c.totalGastado or 0.0), 'historial': ventas})
        return resultados