from app.Venta.repositories.ventaRepository import VentaRepository
from app.Inventario.repositories.inventarioRepository import InventarioRepository
from app.Productos.repositories.productoRepository import ProductoRepository
from app.Venta.repositories.promocionRepository import PromocionRepository
from app.ParametrosSistema.repositories.parametroSistemaRepository import ParametroSistemaRepository
from app.Clientes.repositories.clienteRepository import ClienteRepository
from app.Caja.repositories.cajaRepository import CajaRepository
from app.configuracionGeneral.schemasGenerales import respuestaApi
from app.configuracionGeneral.seguridadJWT import identificarUsuarioString
from app.Venta.schemas.ventaSchemas import VentaCrearSchema, VentaRespuestaSchema
from app.Venta.schemas.detalleVentaSchemas import DetalleVentaCrearSchema, DetalleVentaRespuestaSchema
from fastapi import HTTPException
from datetime import datetime

class VentaService:
    def __init__(self, dbSession):
        self.dbSession = dbSession
        self.repo = VentaRepository(dbSession)
        self.prodRepo = ProductoRepository(dbSession)
        self.invRepo = InventarioRepository(dbSession)
        self.promRepo = PromocionRepository(dbSession)
        self.paramRepo = ParametroSistemaRepository(dbSession)
        self.cliRepo = ClienteRepository(dbSession)
        self.cajaRepo = CajaRepository(dbSession)

    def crearVenta(self, ventaCrear: VentaCrearSchema, usuario: dict):
        # validar cliente
        idUsuario = usuario.get("idUsuario")
        cliente = None
        # validar cliente: debe existir (idCliente obligatorio)
        cliente = self.cliRepo.obtenerPorId(ventaCrear.idCliente)
        if not cliente:
            raise HTTPException(status_code=400, detail="Cliente no encontrado")
        # validar caja abierta del usuario (debe existir una caja ABIERTA hoy)
        cajas_hoy = self.cajaRepo.listarCajasHoy(idUsuario, False)
        if not cajas_hoy:
            # No se abrió ninguna caja hoy para el usuario
            actor = identificarUsuarioString(usuario)
            raise HTTPException(status_code=400, detail=f"No se ha abierto una caja para hoy para el usuario {actor}")
        caja_obj = None
        for c in cajas_hoy:
            if getattr(c, 'estadoCaja', '') == 'ABIERTA':
                caja_obj = c
                break
        if not caja_obj:
            # Existe caja(s) hoy pero todas están cerradas -> no se permiten ventas
            raise HTTPException(status_code=400, detail="La caja ya está cerrada; no se pueden registrar ventas porque se realizó el arqueo")

        # validar descuentos
        if ventaCrear.descuentoGeneral < 0 or ventaCrear.descuentoGeneral > 100:
            raise HTTPException(status_code=400, detail="descuentoGeneral debe estar entre 0 y 100")

        # Validar productos y calcular subtotales (recolectar errores como en Pedido)
        detalles_objs = []
        subtotalVenta = 0.0
        totalPromos = 0.0
        taxable_base = 0.0
        missing = []
        for item in ventaCrear.detalles:
            cantidad = item.cantidadComprada
            # Usar el helper de ProductoRepository que unifica validaciones (existencia, activo, stock)
            val = self.prodRepo.validarProductoParaVenta(item.idProducto, cantidad)
            if isinstance(val, dict) and val.get("error"):
                missing.append({"idProducto": item.idProducto, "error": val.get("error")})
                continue
            producto = val.get("producto")
            precio = val.get("precio")
            inventario = val.get("inventario")
            subtotalProducto = round(precio * cantidad, 2)
            promo = self.promRepo.obtenerPromocionActivaMayorDescuento(item.idProducto)
            valorDescPromo = 0.0
            promo_summary = None
            idPromo = None
            if promo:
                valorDescPromo = round((promo.porcentajePromocion / 100.0) * subtotalProducto, 2)
                idPromo = promo.idPromocion
                # crear resumen de promocion para la respuesta
                from app.Venta.schemas.promocionSchemas import PromocionResumenSchema
                promo_summary = PromocionResumenSchema.from_orm(promo)
            subtotalVenta += subtotalProducto
            totalPromos += valorDescPromo
            if val.get("tieneIva", True):
                taxable_base += subtotalProducto - valorDescPromo
            # construir resumen del producto para la respuesta
            from app.Productos.schemas.productoSchemas import ProductoResumenSchema
            producto_summary = ProductoResumenSchema.from_orm(producto)
            detalle = DetalleVentaRespuestaSchema(
                idDetalleVenta=0,
                idVenta=0,
                producto=producto_summary,
                promocion=promo_summary,
                precioUnitarioVendido=precio,
                cantidadVendida=cantidad,
                subtotalProducto=subtotalProducto,
                valorDescuentoProducto=valorDescPromo
            )
            detalles_objs.append(detalle)
        if missing:
            # Mantener el mismo formato que Pedido: raise HTTPException con detail estructurado
            raise HTTPException(status_code=400, detail={"error": missing})

        subtotalVenta = round(subtotalVenta, 2)
        subtotalDespuesPromos = round(subtotalVenta - totalPromos, 2)
        descuentoGeneralMonto = round((ventaCrear.descuentoGeneral / 100.0) * subtotalDespuesPromos, 2)
        totalDescuento = round(totalPromos + descuentoGeneralMonto, 2)

        # calcular IVA
        param_iva = self.paramRepo.validarClaveExistente("IVA")
        if not param_iva:
            baseIVA = 0.0
        else:
            baseIVA = float(param_iva.valorParametro) / 100.0
        # aplicar parte proporcional del descuento general a la porcion taxable
        taxable_after_general = 0.0
        if subtotalDespuesPromos > 0:
            # proporción del descuento general que afecta la porción taxable
            descuento_general_aplicado_a_taxable = (taxable_base / subtotalDespuesPromos) * descuentoGeneralMonto if subtotalDespuesPromos > 0 else 0
            taxable_after_general = taxable_base - descuento_general_aplicado_a_taxable
        totalIVA = round(taxable_after_general * baseIVA, 2)

        totalPagar = round(subtotalDespuesPromos - descuentoGeneralMonto + totalIVA, 2)

        # crear objetos de ORM Venta y DetalleVenta
        from app.Venta.models.ventaModel import Venta
        from app.Venta.models.detalleVentaModel import DetalleVenta
        venta_obj = Venta(
            idCaja=caja_obj.idCaja,
            idUsuarioVenta=idUsuario,
            idCliente=cliente.idCliente,
            subtotalVenta=subtotalVenta,
            descuentoGeneral=ventaCrear.descuentoGeneral,
            totalDescuento=totalDescuento,
            baseIVA=baseIVA * 100.0,
            totalIVA=totalIVA,
            totalPagar=totalPagar,
            metodoPago=ventaCrear.metodoPago,
            estadoVenta="COMPLETADA"
        )
        detalle_orms = []
        for d in detalles_objs:
            detalle_orms.append(DetalleVenta(
                idProducto=d.producto.idProducto,
                idPromocion=(d.promocion.idPromocion if d.promocion else None),
                precioUnitarioVendido=d.precioUnitarioVendido,
                cantidadVendida=d.cantidadVendida,
                subtotalProducto=d.subtotalProducto,
                valorDescuentoProducto=d.valorDescuentoProducto
            ))

        creado = self.repo.crearVenta(venta_obj, detalle_orms)
        # deducir inventario
        for d in creado.detalles:
            inventario = self.invRepo.obtenerPorProducto(d.idProducto)
            if inventario:
                inventario.cantidadDisponible = (inventario.cantidadDisponible or 0) - (d.cantidadVendida or 0)
                self.dbSession.add(inventario)
        self.dbSession.commit()
        data = VentaRespuestaSchema.from_orm(creado)
        actor = identificarUsuarioString(usuario)
        return respuestaApi(success=True, message=f"Venta registrada por {actor}", data=data)

    def listarVentasHoy(self, usuario: dict):
        rol = usuario.get("rol")
        idUsuario = usuario.get("idUsuario")
        esAdmin = rol == "Administrador"
        ventas = self.repo.listarVentasHoy(idUsuario if not esAdmin else None, esAdmin)
        if not ventas:
            return respuestaApi(success=True, message="No se encontraron ventas para hoy", data=[])
        data = [VentaRespuestaSchema.from_orm(v) for v in ventas]
        return respuestaApi(success=True, message="Ventas encontradas", data=data)

    def listarHistorico(self, usuario: dict):
        rol = usuario.get("rol")
        if rol != "Administrador":
            raise HTTPException(status_code=403, detail="Solo Administrador puede ver el histórico")
        ventas = self.repo.listarTodas()
        if not ventas:
            return respuestaApi(success=True, message="No se encontraron ventas", data=[])
        data = [VentaRespuestaSchema.from_orm(v) for v in ventas]
        return respuestaApi(success=True, message="Ventas encontradas", data=data)

    def anularVenta(self, idVenta: int, usuario: dict):
        rol = usuario.get("rol")
        idUsuario = usuario.get("idUsuario")
        venta = self.repo.obtenerPorId(idVenta)
        if not venta:
            raise HTTPException(status_code=404, detail="Venta no encontrada")
        # Solo se permiten anulaciones de ventas del día actual (zona de Quito)
        from datetime import datetime, timezone, timedelta
        quitoTZ = timezone(timedelta(hours=-5))
        venta_fecha = venta.fechaVenta
        try:
            venta_fecha_local = venta_fecha.astimezone(quitoTZ).date()
        except Exception:
            venta_fecha_local = venta_fecha.date()
        hoy = datetime.now(quitoTZ).date()
        if venta_fecha_local != hoy:
            raise HTTPException(status_code=400, detail="Solo se pueden anular ventas del día actual")
        if rol != "Administrador" and venta.idUsuarioVenta != idUsuario:
            raise HTTPException(status_code=403, detail="No tiene permisos para anular esta venta")
        # Restricción adicional para Cajero: la caja asociada a la venta debe estar abierta hoy
        if rol != "Administrador":
            cajas_hoy = self.cajaRepo.listarCajasHoy(idUsuario, False)
            if not cajas_hoy:
                raise HTTPException(status_code=400, detail="No se ha abierto una caja para hoy; no se pueden anular ventas")
            caja_abierta = None
            for c in cajas_hoy:
                if getattr(c, 'idCaja', None) == venta.idCaja and getattr(c, 'estadoCaja', '') == 'ABIERTA':
                    caja_abierta = c
                    break
            if not caja_abierta:
                raise HTTPException(status_code=400, detail="La caja asociada a esta venta no está abierta; no se pueden anular ventas")
        res = self.repo.anularVenta(idVenta)
        if res is None:
            raise HTTPException(status_code=404, detail="Venta no encontrada")
        if isinstance(res, dict) and res.get("error") == "venta_ya_anulada":
            data = VentaRespuestaSchema.from_orm(res.get("venta"))
            return respuestaApi(success=False, message="La venta ya está anulada", data=data)
        data = VentaRespuestaSchema.from_orm(res)
        actor = identificarUsuarioString(usuario)
        return respuestaApi(success=True, message=f"Venta anulada por {actor}", data=data)

    def generarComprobanteVenta(self, idVenta: int, usuario: dict):
        """Genera un comprobante con parámetros del sistema y la venta indicada."""
        venta = self.repo.obtenerPorId(idVenta)
        if not venta:
            raise HTTPException(status_code=404, detail="Venta no encontrada")
        # preparar parámetros solicitados
        keys = ["nombreNegocio", "direccionNegocio", "telefonoNegocio", "correoNegocio"]
        parametros = []
        for k in keys:
            p = self.paramRepo.validarClaveExistente(k)
            parametros.append({"claveParametro": k, "valorParametro": (p.valorParametro if p else None)})
        # serializar venta con detalle
        venta_data = VentaRespuestaSchema.from_orm(venta)
        return respuestaApi(success=True, message="Comprobante generado", data={"parametros": parametros, "venta": venta_data})