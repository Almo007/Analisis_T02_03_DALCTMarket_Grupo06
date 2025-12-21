from app.Productos.models.productoModel import Producto
from app.Productos.schemas.productoSchemas import *
from app.Productos.models.categoriaProductoModel import CategoriaProducto
from app.Productos.models.proveedorModel import Proveedor
from sqlalchemy.orm import joinedload

class ProductoRepository:
    def __init__(self, dbSession):
        self.dbSession = dbSession

    def listarProductos(self):
        return self.dbSession.query(Producto).options(joinedload(Producto.categoria), joinedload(Producto.proveedor)).all()

    def obtenerPorId(self, idProducto: int):
        return (self.dbSession.query(Producto)
                .options(joinedload(Producto.categoria), joinedload(Producto.proveedor))
                .filter(Producto.idProducto == idProducto).first())

    def validarProductoParaVenta(self, idProducto: int, cantidadSolicitada: float):
        """Valida que el producto exista, esté activo y tenga stock suficiente.
        Devuelve un dict con 'error' clave si hay problema, o un dict con keys:
        - producto: objeto Producto
        - precio: float (precioUnitarioVenta)
        - tieneIva: bool
        - inventario: objeto Inventario (si existe)
        """
        producto = self.obtenerPorId(idProducto)
        if not producto:
            return {"error": "producto_no_encontrado"}
        if not getattr(producto, "activoProducto", True):
            return {"error": "producto_inactivo"}
        try:
            from app.Inventario.repositories.inventarioRepository import InventarioRepository
            inv_repo = InventarioRepository(self.dbSession)
            inventario = inv_repo.obtenerPorProducto(idProducto)
        except Exception:
            inventario = None
        if not inventario or (inventario.cantidadDisponible or 0) < cantidadSolicitada:
            return {"error": "stock_insuficiente"}
        return {
            "producto": producto,
            "precio": float(producto.precioUnitarioVenta),
            "tieneIva": getattr(producto, "tieneIva", True),
            "inventario": inventario
        }

    def crearProducto(self, producto: ProductoCrearSchema):
        # Verificar fk existencia
        categoria = self.dbSession.query(CategoriaProducto).filter(CategoriaProducto.idCategoriaProducto == producto.idCategoriaProducto).first()
        proveedor = self.dbSession.query(Proveedor).filter(Proveedor.idProveedor == producto.idProveedor).first()
        missing = []
        if not categoria:
            missing.append("categoria")
        else:
            if not getattr(categoria, "activoCategoria", True):
                missing.append("categoria_inactiva")
        if not proveedor:
            missing.append("proveedor")
        else:
            if not getattr(proveedor, "activoProveedor", True):
                missing.append("proveedor_inactiva")
        # Validaciones de cantidades no negativas
        if getattr(producto, "cantidadDisponible", None) is not None and producto.cantidadDisponible < 0:
            missing.append("cantidad_disponible_negativa")
        if getattr(producto, "cantidadMinima", None) is not None and producto.cantidadMinima < 0:
            missing.append("cantidad_minima_negativa")
        if missing:
            return {"error": missing}
        # Crear producto (excluir campos de inventario si vienen)
        datos_producto = producto.model_dump(exclude={"cantidadDisponible","cantidadMinima"})
        # Por defecto activoProducto = True al crear (no se acepta en el schema crear)
        datos_producto.setdefault("activoProducto", True)
        nuevo = Producto(**datos_producto)
        self.dbSession.add(nuevo)
        # Obtener id antes de commit
        self.dbSession.flush()
        # Crear inventario automáticamente si no existe
        try:
            from app.Inventario.models.inventarioModel import Inventario
            existe_inv = self.dbSession.query(Inventario).filter(Inventario.idProducto == nuevo.idProducto).first()
            if not existe_inv:
                cantidadDisponible = getattr(producto, "cantidadDisponible", None)
                cantidadMinima = getattr(producto, "cantidadMinima", None)
                inv_datos = {
                    "idProducto": nuevo.idProducto,
                    "cantidadDisponible": cantidadDisponible if cantidadDisponible is not None else 0,
                    "cantidadMinima": cantidadMinima if cantidadMinima is not None else 0,
                    "activoInventario": True
                }
                nuevo_inv = Inventario(**inv_datos)
                self.dbSession.add(nuevo_inv)
                inventario_creado = True
            else:
                inventario_creado = False
        except Exception:
            inventario_creado = False
        self.dbSession.commit()
        self.dbSession.refresh(nuevo)
        # devolver flag para que el servicio pueda ajustar el mensaje
        return (nuevo, inventario_creado)

    def modificarProducto(self, idProducto: int, productoActualizar: ProductoActualizarSchema):
        producto = self.obtenerPorId(idProducto)
        if not producto:
            return None
        datos = productoActualizar.model_dump(exclude_unset=True)
        camposValidos = ["idCategoriaProducto","idProveedor","nombreProducto","descripcionProducto","precioUnitarioVenta","precioUnitarioCompra","tieneIva","activoProducto"]
        missing = []
        for campo, valor in datos.items():
            if campo in camposValidos:
                if campo == "idCategoriaProducto":
                    cat = self.dbSession.query(CategoriaProducto).filter(CategoriaProducto.idCategoriaProducto == valor).first()
                    if not cat:
                        missing.append("categoria")
                        continue
                if campo == "idProveedor":
                    prov = self.dbSession.query(Proveedor).filter(Proveedor.idProveedor == valor).first()
                    if not prov:
                        missing.append("proveedor")
                        continue
                setattr(producto, campo, valor)
        if missing:
            # quitar duplicados y devolver la lista de errores
            return {"error": list(dict.fromkeys(missing))}
        self.dbSession.commit()
        self.dbSession.refresh(producto)
        return producto

    def deshabilitarProducto(self, idProducto: int):
        producto = self.obtenerPorId(idProducto)
        if not producto:
            return None
        producto.activoProducto = False
        self.dbSession.commit()
        self.dbSession.refresh(producto)
        return producto

    def crearProductosIniciales(self):
        productos = [
            {"idCategoriaProducto": 1, "idProveedor": 1, "nombreProducto": "Cola 2 Litros", "descripcionProducto": "Bebida gaseosa sabor cola", "precioUnitarioVenta": 2.50, "precioUnitarioCompra": 1.80, "tieneIva": True, "activoProducto": True, "cantidadDisponible": 100, "cantidadMinima": 10},
            {"idCategoriaProducto": 1, "idProveedor": 1, "nombreProducto": "Jugo de Naranja 1L", "descripcionProducto": "Jugo natural pasteurizado", "precioUnitarioVenta": 1.80, "precioUnitarioCompra": 1.20, "tieneIva": False, "activoProducto": True, "cantidadDisponible": 80, "cantidadMinima": 10},
            {"idCategoriaProducto": 1, "idProveedor": 1, "nombreProducto": "Agua Mineral 600ml", "descripcionProducto": "Agua sin gas", "precioUnitarioVenta": 0.70, "precioUnitarioCompra": 0.40, "tieneIva": True, "activoProducto": True, "cantidadDisponible": 200, "cantidadMinima": 20},
            {"idCategoriaProducto": 1, "idProveedor": 1, "nombreProducto": "Bebida Energética", "descripcionProducto": "Bebida energizante lata", "precioUnitarioVenta": 2.20, "precioUnitarioCompra": 1.50, "tieneIva": True, "activoProducto": True, "cantidadDisponible": 60, "cantidadMinima": 8},
            {"idCategoriaProducto": 1, "idProveedor": 1, "nombreProducto": "Té Frío Limón", "descripcionProducto": "Té frío sabor limón", "precioUnitarioVenta": 1.50, "precioUnitarioCompra": 1.00, "tieneIva": True, "activoProducto": True, "cantidadDisponible": 90, "cantidadMinima": 10},

            {"idCategoriaProducto": 2, "idProveedor": 2, "nombreProducto": "Papas Fritas Clásicas", "descripcionProducto": "Papas fritas bolsa mediana", "precioUnitarioVenta": 1.25, "precioUnitarioCompra": 0.80, "tieneIva": True, "activoProducto": True, "cantidadDisponible": 120, "cantidadMinima": 15},
            {"idCategoriaProducto": 2, "idProveedor": 2, "nombreProducto": "Galletas de Chocolate", "descripcionProducto": "Galletas rellenas", "precioUnitarioVenta": 1.10, "precioUnitarioCompra": 0.75, "tieneIva": True, "activoProducto": True, "cantidadDisponible": 150, "cantidadMinima": 20},
            {"idCategoriaProducto": 2, "idProveedor": 2, "nombreProducto": "Maní Salado", "descripcionProducto": "Maní tostado y salado", "precioUnitarioVenta": 0.90, "precioUnitarioCompra": 0.50, "tieneIva": True, "activoProducto": True, "cantidadDisponible": 80, "cantidadMinima": 10},
            {"idCategoriaProducto": 2, "idProveedor": 2, "nombreProducto": "Chifles", "descripcionProducto": "Plátano frito en rodajas", "precioUnitarioVenta": 1.00, "precioUnitarioCompra": 0.65, "tieneIva": True, "activoProducto": True, "cantidadDisponible": 60, "cantidadMinima": 10},
            {"idCategoriaProducto": 2, "idProveedor": 2, "nombreProducto": "Barra de Cereal", "descripcionProducto": "Barra energética", "precioUnitarioVenta": 0.85, "precioUnitarioCompra": 0.55, "tieneIva": True, "activoProducto": True, "cantidadDisponible": 200, "cantidadMinima": 20},

            {"idCategoriaProducto": 3, "idProveedor": 3, "nombreProducto": "Arroz 5 Libras", "descripcionProducto": "Arroz blanco grano largo", "precioUnitarioVenta": 3.20, "precioUnitarioCompra": 2.60, "tieneIva": False, "activoProducto": True, "cantidadDisponible": 40, "cantidadMinima": 10},
            {"idCategoriaProducto": 3, "idProveedor": 3, "nombreProducto": "Azúcar 2 Libras", "descripcionProducto": "Azúcar refinada", "precioUnitarioVenta": 1.90, "precioUnitarioCompra": 1.40, "tieneIva": False, "activoProducto": True, "cantidadDisponible": 60, "cantidadMinima": 10},
            {"idCategoriaProducto": 3, "idProveedor": 3, "nombreProducto": "Aceite Vegetal 1L", "descripcionProducto": "Aceite comestible", "precioUnitarioVenta": 3.80, "precioUnitarioCompra": 3.10, "tieneIva": True, "activoProducto": True, "cantidadDisponible": 75, "cantidadMinima": 10},
            {"idCategoriaProducto": 3, "idProveedor": 3, "nombreProducto": "Fideos Spaghetti", "descripcionProducto": "Pasta seca", "precioUnitarioVenta": 1.40, "precioUnitarioCompra": 0.95, "tieneIva": True, "activoProducto": True, "cantidadDisponible": 120, "cantidadMinima": 20},
            {"idCategoriaProducto": 3, "idProveedor": 3, "nombreProducto": "Atún en Lata", "descripcionProducto": "Atún en aceite", "precioUnitarioVenta": 1.75, "precioUnitarioCompra": 1.20, "tieneIva": True, "activoProducto": True, "cantidadDisponible": 90, "cantidadMinima": 15},

            {"idCategoriaProducto": 4, "idProveedor": 4, "nombreProducto": "Detergente en Polvo", "descripcionProducto": "Detergente multiuso", "precioUnitarioVenta": 4.50, "precioUnitarioCompra": 3.60, "tieneIva": True, "activoProducto": True, "cantidadDisponible": 50, "cantidadMinima": 10},
            {"idCategoriaProducto": 4, "idProveedor": 4, "nombreProducto": "Cloro 1L", "descripcionProducto": "Desinfectante", "precioUnitarioVenta": 1.20, "precioUnitarioCompra": 0.80, "tieneIva": True, "activoProducto": True, "cantidadDisponible": 100, "cantidadMinima": 20},
            {"idCategoriaProducto": 4, "idProveedor": 4, "nombreProducto": "Esponjas", "descripcionProducto": "Esponjas para lavar", "precioUnitarioVenta": 1.00, "precioUnitarioCompra": 0.60, "tieneIva": True, "activoProducto": True, "cantidadDisponible": 250, "cantidadMinima": 30},
            {"idCategoriaProducto": 4, "idProveedor": 4, "nombreProducto": "Limpiavidrios", "descripcionProducto": "Limpieza de superficies", "precioUnitarioVenta": 2.30, "precioUnitarioCompra": 1.70, "tieneIva": True, "activoProducto": True, "cantidadDisponible": 60, "cantidadMinima": 10},
            {"idCategoriaProducto": 4, "idProveedor": 4, "nombreProducto": "Desinfectante Piso", "descripcionProducto": "Aroma floral", "precioUnitarioVenta": 2.80, "precioUnitarioCompra": 2.10, "tieneIva": True, "activoProducto": True, "cantidadDisponible": 40, "cantidadMinima": 8},

            {"idCategoriaProducto": 5, "idProveedor": 5, "nombreProducto": "Jabón de Baño", "descripcionProducto": "Jabón antibacterial", "precioUnitarioVenta": 1.10, "precioUnitarioCompra": 0.70, "tieneIva": True, "activoProducto": True, "cantidadDisponible": 180, "cantidadMinima": 30},
            {"idCategoriaProducto": 5, "idProveedor": 5, "nombreProducto": "Shampoo", "descripcionProducto": "Shampoo familiar", "precioUnitarioVenta": 4.20, "precioUnitarioCompra": 3.30, "tieneIva": True, "activoProducto": True, "cantidadDisponible": 45, "cantidadMinima": 8},
            {"idCategoriaProducto": 5, "idProveedor": 5, "nombreProducto": "Pasta Dental", "descripcionProducto": "Protección dental", "precioUnitarioVenta": 2.50, "precioUnitarioCompra": 1.90, "tieneIva": True, "activoProducto": True, "cantidadDisponible": 110, "cantidadMinima": 20},
            {"idCategoriaProducto": 5, "idProveedor": 5, "nombreProducto": "Papel Higiénico", "descripcionProducto": "Paquete 4 rollos", "precioUnitarioVenta": 3.60, "precioUnitarioCompra": 2.80, "tieneIva": True, "activoProducto": True, "cantidadDisponible": 70, "cantidadMinima": 10},
            {"idCategoriaProducto": 5, "idProveedor": 5, "nombreProducto": "Desodorante", "descripcionProducto": "Protección 24 horas", "precioUnitarioVenta": 3.90, "precioUnitarioCompra": 3.00, "tieneIva": True, "activoProducto": True, "cantidadDisponible": 65, "cantidadMinima": 10},
        ]

        for p in productos:
            existe = self.dbSession.query(Producto).filter(Producto.nombreProducto == p["nombreProducto"]).first() 
            if not existe:
                # Verificar fk antes de crear
                cat = self.dbSession.query(CategoriaProducto).filter(CategoriaProducto.idCategoriaProducto == p["idCategoriaProducto"]).first()
                prov = self.dbSession.query(Proveedor).filter(Proveedor.idProveedor == p["idProveedor"]).first()
                if cat and prov:
                    # Excluir campos de inventario al crear Producto
                    datos_producto = {k: v for k, v in p.items() if k not in ("cantidadDisponible", "cantidadMinima")}
                    datos_producto.setdefault("activoProducto", True)
                    nuevo = Producto(**datos_producto)
                    self.dbSession.add(nuevo)
                    # flush para obtener el idProducto y crear inventario inicial si no existe
                    self.dbSession.flush()
                    try:
                        from app.Inventario.models.inventarioModel import Inventario
                        existe_inv = self.dbSession.query(Inventario).filter(Inventario.idProducto == nuevo.idProducto).first()
                        if not existe_inv:
                            inv = Inventario(idProducto=nuevo.idProducto, cantidadDisponible=p.get("cantidadDisponible", 0), cantidadMinima=p.get("cantidadMinima", 0), activoInventario=True)
                            self.dbSession.add(inv)
                    except Exception:
                        # Si Inventario no existe o hay problema, skip
                        pass
        print("Productos por defecto creados...!")
        self.dbSession.commit()
        self.dbSession.close()