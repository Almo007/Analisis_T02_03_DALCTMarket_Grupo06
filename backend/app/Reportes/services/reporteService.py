from app.Reportes.repositories.reporteRepository import ReporteRepository
from app.Reportes.schemas.reporteSchemas import *
from app.configuracionGeneral.schemasGenerales import respuestaApi
from fastapi import HTTPException
from datetime import datetime
from app.Inventario.schemas.inventarioSchemas import InventarioRespuestaSchema

class ReporteService:
    def __init__(self, dbSession):
        self.dbSession = dbSession
        self.repo = ReporteRepository(dbSession)

    def reporteInventario(self, filtro: InventarioFiltro, usuario: dict):
        rol = usuario.get('rol')
        if rol not in ["Administrador", "Bodeguero"]:
            raise HTTPException(status_code=403, detail="No tienes permiso para generar este reporte")
        invs = self.repo.reporte_inventario(idProducto=filtro.idProducto, idCategoria=filtro.idCategoria, nombreProducto=filtro.nombreProducto)
        items = [InventarioRespuestaSchema.from_orm(inv) for inv in invs]
        return respuestaApi(success=True, message="Reporte de inventario generado", data=InventarioReporteRespuesta(items=items))

    def reporteVentasProductoCategoria(self, filtro: VentasFiltro, usuario: dict):
        rol = usuario.get('rol')
        if rol != "Administrador":
            raise HTTPException(status_code=403, detail="Solo Administrador puede generar este reporte")
        # Validar fechas obligatorias
        if not filtro.fechaInicio or not filtro.fechaFin:
            raise HTTPException(status_code=400, detail="fechaInicio y fechaFin son obligatorias")
        # Requerir idProducto o idCategoria
        if filtro.idProducto is None and filtro.idCategoria is None:
            raise HTTPException(status_code=400, detail="Debe proporcionar idProducto o idCategoria")
        rows = self.repo.reporte_ventas_por_producto_categoria(filtro.fechaInicio, filtro.fechaFin, filtro.idProducto, filtro.idCategoria)
        items = []
        for r in rows:
            items.append(VentasPorProductoItem(
                idProducto=r.idProducto,
                nombreProducto=r.nombreProducto,
                idCategoria=r.idCategoriaProducto,
                nombreCategoria=r.nombreCategoria,
                cantidadVendida=int(r.cantidadVendida or 0),
                ingresos=float(round(r.ingresos or 0.0,2))
            ))
        return respuestaApi(success=True, message="Reporte de ventas por producto/categoría generado", data=VentasReporteRespuesta(items=items))

    def resumenCajaDiaria(self, fecha: datetime.date, idUsuarioCaja: int | None, usuario: dict):
        rol = usuario.get('rol')
        if rol != "Administrador":
            raise HTTPException(status_code=403, detail="Solo Administrador puede generar este reporte")
        if idUsuarioCaja is None:
            raise HTTPException(status_code=400, detail="idUsuarioCaja es obligatorio")
        cajas = self.repo.resumen_caja_diaria(fecha, idUsuarioCaja)
        items = []
        for c in cajas:
            ventas = getattr(c, 'ventas', []) or []
            items.append(ResumenCajaItem(
                idCaja=c.idCaja,
                usuario=(UsuarioPublicoSchema.from_orm(c.usuario) if getattr(c, 'usuario', None) else None),
                fechaAperturaCaja=c.fechaAperturaCaja,
                fechaCierreCaja=c.fechaCierreCaja,
                montoInicialDeclarado=c.montoInicialDeclarado or 0.0,
                montoCierreDeclarado=c.montoCierreDeclarado,
                montoCierreSistema=c.montoCierreSistema,
                diferenciaCaja=c.diferenciaCaja,
                estadoCaja=c.estadoCaja,
                ventas=[VentaRespuestaSchema.from_orm(v) for v in ventas]
            ))
        return respuestaApi(success=True, message="Resumen de caja generado", data=ResumenCajaRespuesta(items=items))

    def clientesFrecuentes(self, filtro: ClientesFiltro, usuario: dict):
        rol = usuario.get('rol')
        if rol != "Administrador":
            raise HTTPException(status_code=403, detail="Solo Administrador puede generar este reporte")
        rows = self.repo.clientes_frecuentes(dias=filtro.dias, minVentas=filtro.minVentas, minGasto=filtro.minGasto)
        items = []
        for r in rows:
            items.append(ClienteFrecuenteItem(
                cliente=ClienteRespuestaSchema.from_orm(r['cliente']),
                ventasCount=int(r['ventasCount']),
                totalGastado=float(round(r['totalGastado'] or 0.0,2)),
                historialVentas=[VentaRespuestaSchema.from_orm(v) for v in r['historial']]
            ))
        return respuestaApi(success=True, message="Reporte de clientes frecuentes generado", data=ClientesFrecuentesRespuesta(items=items))