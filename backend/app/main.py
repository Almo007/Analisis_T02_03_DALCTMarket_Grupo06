from fastapi import FastAPI, Depends
from fastapi.exceptions import HTTPException
from fastapi.responses import JSONResponse
from fastapi.requests import Request
from app.configuracionGeneral.seguridadJWT import protegerRuta
from app.database import Base,engine,obtenerSesionDirecta

# Librerias de rutas
from app.Usuarios.controllers.usuarioController import router as controladorUsuarios
from app.Usuarios.controllers.usuarioController import publicRouter as controladorUsuariosPublic
from app.Usuarios.repositories.usuarioRepository import UsuarioRepository
from app.Usuarios.controllers.rolController import router as controladorRoles
from app.Usuarios.repositories.rolRepository import RolRepository
from app.ParametrosSistema.controllers.parametroSistemaController import router as controladorParametrosSistema
from app.ParametrosSistema.repositories.parametroSistemaRepository import ParametroSistemaRepository
from app.Productos.controllers.categoriaProductoController import router as controladorCategoriasProducto
from app.Productos.repositories.categoriaProductoRepository import CategoriaProductoRepository
from app.Productos.controllers.proveedorController import router as controladorProveedores
from app.Productos.repositories.proveedorRepository import ProveedorRepository
from app.Productos.controllers.productoController import router as controladorProductos
from app.Productos.repositories.productoRepository import ProductoRepository
from app.Inventario.controllers.inventarioController import router as controladorInventario
from app.Inventario.repositories.inventarioRepository import InventarioRepository
from app.Pedido.controllers.pedidoController import router as controladorPedidos
from app.Pedido.repositories.pedidoRepository import PedidoRepository
from app.Clientes.controllers.clienteController import router as controladorClientes
from app.Clientes.repositories.clienteRepository import ClienteRepository
from app.Venta.controllers.promocionController import router as controladorPromociones
from app.Venta.repositories.promocionRepository import PromocionRepository
from app.Caja.controllers.cajaController import router as controladorCaja
from app.Venta.controllers.ventaController import router as controladorVenta
from app.Reportes.controllers.reporteController import router as controladorReportes


app = FastAPI(
    title="API DALCT Market",
    description="Backend de DALCT Market",
    version="0.1",
)

@app.on_event("startup")
async def startup_event():
    print("Iniciando API DALCT Market...")
    print("Conectando a la base de datos...")
    Base.metadata.create_all(bind=engine)
    print("Base de datos conectada...")
    #Crear datos por defecto
    RolRepository(obtenerSesionDirecta()).crearRolesPorDefecto()
    UsuarioRepository(obtenerSesionDirecta()).crearUsuariosIniciales()
    ParametroSistemaRepository(obtenerSesionDirecta()).crearParametrosIniciales()
    # Clientes por defecto
    ClienteRepository(obtenerSesionDirecta()).crearClientesIniciales()
    # Categorías de producto por defecto
    CategoriaProductoRepository(obtenerSesionDirecta()).crearCategoriasIniciales()
    # Proveedores por defecto
    ProveedorRepository(obtenerSesionDirecta()).crearProveedoresIniciales()
    # Productos por defecto
    ProductoRepository(obtenerSesionDirecta()).crearProductosIniciales()
    # Pedidos de ejemplo (admin auto-aprobado y pedido pendiente de bodeguero)
    PedidoRepository(obtenerSesionDirecta()).crearPedidosIniciales()
    # Promociones de ejemplo (una pasada y otra vigente)
    PromocionRepository(obtenerSesionDirecta()).crearPromocionesIniciales()

@app.get("/", tags=["Inicio"], summary="Inicio", status_code=200, description="API DALCT Market")
def inicio():
    return {"mensaje": "API DALCT Market está lista...!"}


# Registrar rutas

# Usuarios
app.include_router(controladorUsuariosPublic,prefix="/usuarios", tags=["Usuarios"])
app.include_router(controladorUsuarios,prefix="/usuarios", tags=["Usuarios"])

# Roles
app.include_router(controladorRoles,prefix="/roles", tags=["Roles"])

# Parametros de sistema
app.include_router(controladorParametrosSistema,prefix="/parametrosistema", tags=["ParametrosSistema"])


# Productos - CategoriaProducto
app.include_router(controladorCategoriasProducto,prefix="/categoriaproducto", tags=["CategoriaProducto"])

# Productos - Proveedor
app.include_router(controladorProveedores,prefix="/proveedor", tags=["Proveedor"])

# Productos - Producto
app.include_router(controladorProductos,prefix="/producto", tags=["Producto"])

# Inventario
app.include_router(controladorInventario,prefix="/inventario", tags=["Inventario"])

# Pedidos
app.include_router(controladorPedidos,prefix="/pedido", tags=["Pedido"])

# Clientes
app.include_router(controladorClientes,prefix="/clientes", tags=["Clientes"])

# Promociones
app.include_router(controladorPromociones, prefix="/promocion", tags=["Promocion"])

# Caja
app.include_router(controladorCaja, prefix="/caja", tags=["Caja"])

# Ventas
app.include_router(controladorVenta, prefix="/venta", tags=["Venta"])

# Reportes
app.include_router(controladorReportes, prefix="/reportes", tags=["Reportes"])

# Configurar errores globales
# 🔴 ERRORES HTTP
@app.exception_handler(HTTPException)
async def manejarErroresHttp(request: Request, exc: HTTPException):
    # Cambiamos el mensaje si viene de OAuth2
    mensaje = exc.detail
    if mensaje == "Not authenticated":
        mensaje = "No autenticado, debe iniciar sesión y proporcionar un token JWT"
    return JSONResponse(
        status_code=exc.status_code,
        content={"success": False, "message": mensaje, "data": None}
    )


# 🔴 ERRORES INTERNOS
@app.exception_handler(Exception)
async def manejarErroresGenerales(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"success": False, "message": "errorInternoServidor", "data": None}
    )