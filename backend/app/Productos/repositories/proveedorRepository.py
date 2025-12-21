from app.Productos.models.proveedorModel import Proveedor
from app.Productos.schemas.proveedorSchemas import *

class ProveedorRepository:
    def __init__(self, dbSession):
        self.dbSession = dbSession

    def listarProveedores(self):
        return self.dbSession.query(Proveedor).all()

    def obtenerPorId(self, idProveedor: int):
        return self.dbSession.query(Proveedor).filter(Proveedor.idProveedor == idProveedor).first()

    def validarRucExistente(self, ruc: str):
        return self.dbSession.query(Proveedor).filter(Proveedor.ruc == ruc).first()

    def crearProveedor(self, proveedor: ProveedorCrearSchema):
        if self.validarRucExistente(proveedor.ruc):
            return None
        nuevo = Proveedor(
            razonSocial=proveedor.razonSocial,
            ruc=proveedor.ruc,
            direccionProveedor=proveedor.direccionProveedor,
            telefonoProveedor=proveedor.telefonoProveedor,
            emailProveedor=proveedor.emailProveedor,
            activoProveedor=True
        )
        self.dbSession.add(nuevo)
        self.dbSession.commit()
        self.dbSession.refresh(nuevo)
        return nuevo

    def modificarProveedor(self, idProveedor: int, proveedorActualizar: ProveedorActualizarSchema):
        proveedor = self.obtenerPorId(idProveedor)
        if not proveedor:
            return None
        datos = proveedorActualizar.model_dump(exclude_unset=True)
        camposValidos = ["razonSocial", "direccionProveedor", "telefonoProveedor", "emailProveedor", "activoProveedor"]
        for campo, valor in datos.items():
            if campo in camposValidos:
                setattr(proveedor, campo, valor)
        self.dbSession.commit()
        self.dbSession.refresh(proveedor)
        return proveedor

    def deshabilitarProveedor(self, idProveedor: int):
        proveedor = self.obtenerPorId(idProveedor)
        if not proveedor:
            return None
        # Verificar que no existan productos activos asociados
        from app.Productos.models.productoModel import Producto
        productoActivo = self.dbSession.query(Producto).filter(Producto.idProveedor == idProveedor, Producto.activoProducto == True).first()
        if productoActivo:
            return False
        proveedor.activoProveedor = False
        self.dbSession.commit()
        self.dbSession.refresh(proveedor)
        return proveedor

    def crearProveedoresIniciales(self):
        proveedores = [
            {"razonSocial": "Distribuidora Andina de Bebidas S.A.", "ruc": "1790012345001", "direccionProveedor": "Av. Maldonado y Morán Valverde, Quito", "telefonoProveedor": "0991234567", "emailProveedor": "ventas@andinabebidas.com", "activoProveedor": True},
            {"razonSocial": "Snacks del Valle Cía. Ltda.", "ruc": "1790023456001", "direccionProveedor": "Av. Galo Plaza Lasso, Quito", "telefonoProveedor": "0987654321", "emailProveedor": "contacto@snacksdelvalle.com", "activoProveedor": True},
            {"razonSocial": "Abarrotes Quito Comercial AQ S.A.", "ruc": "1790034567001", "direccionProveedor": "Av. América y Naciones Unidas, Quito", "telefonoProveedor": "0974567890", "emailProveedor": "ventas@abarrotesaq.com", "activoProveedor": True},
            {"razonSocial": "Limpieza Total Ecuador LT S.A.", "ruc": "1790045678001", "direccionProveedor": "Av. Mariscal Sucre, Quito", "telefonoProveedor": "0962345678", "emailProveedor": "ventas@limpiezatotal.com", "activoProveedor": True},
            {"razonSocial": "Higiene y Cuidado Personal HC S.A.", "ruc": "1790056789001", "direccionProveedor": "Av. Simón Bolívar, Quito", "telefonoProveedor": "0956781234", "emailProveedor": "contacto@higienepersonalhc.com", "activoProveedor": True},
        ]

        for p in proveedores:
            existe = self.validarRucExistente(p["ruc"]) 
            if not existe:
                nuevo = Proveedor(**p)
                self.dbSession.add(nuevo)
        print("Proveedores por defecto creados...!")
        self.dbSession.commit()
        self.dbSession.close()