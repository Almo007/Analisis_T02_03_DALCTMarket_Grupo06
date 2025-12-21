# SGM-DALCT Backend
Repositorio del backend del Sistema de Gestión de Minimercado DALCT Market (SGM-DALCT) para la tarea de Ingeniería de Software 02.03.
Incluye funcionalidades de usuarios, roles, productos, inventario, proveedores, ventas, caja y reportes.
# SGM-DALCT (Tarea 02.03)-Documentación del Backend

## 1. Introducción

El presente documento tiene como objetivo documentar de manera clara y estructurada la arquitectura del backend del sistema **SGM-DALCT Market**, detallando las tecnologías empleadas, la organización de los módulos y la estructura del código fuente. Esta documentación está orientada a facilitar la comprensión del funcionamiento interno del sistema, así como su mantenimiento, escalabilidad y futura extensión.

El backend puede ser accedido mediante la documentación interactiva **Swagger (OpenAPI)**, la cual permite explorar y probar los endpoints disponibles. Dicha documentación se encuentra disponible en el siguiente enlace:
https://t02-03-dalctmarket-grupo06.onrender.com/docs

> **Nota:** El backend se encuentra desplegado en **Render**. Al acceder por primera vez, es posible que el servicio tarde algunos segundos en responder mientras se reactiva el contenedor (cold start) o sino se pude ejecutar localmente.


---

## 2. Tecnologías y herramientas utilizadas
- Lenguaje de programación: **Python 3.12+**
- Framework Web: **FastAPI** (documentación automática y rapidez para APIs REST)
- Gestión de datos: **SQLAlchemy** + **Pydantic**
- Base de datos: **PostgreSQL 17**
- Contenerización: **Docker**
- Documentación/Interfaz: **Swagger** (endpoints en `/docs`)

---

## 3. Arquitectura del código
El backend está estructurado siguiendo un esquema modular basado en modelo/repositorio/servicio/controlador:
- **Modelo:** Entidades y relaciones (Usuario, Producto, Inventario, Venta, Cliente, Caja, Pedido, etc.).
- **Repositorio:** Interacción con la base de datos (CRUD, consultas especializadas).
- **Servicio:** Lógica de negocio (cálculo de totales, validaciones, aplicación de promociones, apertura/cierre de caja, etc.).
- **Controlador / Router:** Endpoints REST que consumen los servicios y validan entradas.

Cada módulo funcional está agrupado en su propia carpeta con subcarpetas `models`, `repositories`, `services` y `controllers` según corresponda, lo que facilita la división del trabajo y el mantenimiento.

---

## 4. Módulos del sistema
1. Módulo ParametrosSistema
   - Carpeta: app/ParametrosSistema
   - Función: Gestión de parámetros generales del sistema.
   - Entidad trabajada:
     - ParametroSistema

2. Módulo Usuarios
   - Carpeta: app/Usuarios
   - Función: Gestión de usuarios del sistema y roles. Autenticación y autorización mediante JWT.
   - Entidades trabajadas:
     - Usuario
     - Rol

3. Módulo Productos
   - Carpeta: app/Productos
   - Función: Gestión de productos, categorías y proveedores.
   - Entidades trabajadas:
     - Producto
     - CategoriaProducto
     - Proveedor

4. Módulo Inventario
   - Carpeta: app/Inventario
   - Función: Control de stock, cantidades disponibles y mínimos.
   - Entidad trabajada:
     - Inventario

5. Módulo Pedido
   - Carpeta: app/Pedido
   - Función: Registro y gestión de pedidos de abastecimiento.
   - Entidades trabajadas:
     - Pedido
     - DetallePedido


6. Módulo Clientes
   - Carpeta: app/Clientes
   - Función: Registro y administración de clientes.
   - Entidad trabajada:
     - Cliente

7. Módulo Venta
   - Carpeta: app/Venta
   - Función: Registro de ventas y aplicación de promociones.
   - Entidades trabajadas:
     - Venta
     - DetalleVenta
     - Promocion

8. Módulo Caja
   - Carpeta: app/Caja
   - Función: Apertura, cierre y control de caja.
   - Entidad trabajada:
     - CajaHistorial

9. Módulo Reportes
   - Carpeta: app/Reportes
   - Función: Generación de reportes a partir de la información del sistema.
   - No maneja entidades propias, consume datos de otros módulos.

10. Configuración General
   - Carpeta: app/configuracionGeneral
   - Función: Configuración transversal del sistema.
   - Componentes:
     - Seguridad JWT
     - Manejo de errores
     - Esquemas generales
---

## 5. Organización de carpetas (recomendación)

Estructura real del backend:

backend/
 ├── Dockerfile
 ├── requerimientos.txt
 └── app/
     ├── main.py
     ├── database.py
     ├── Caja/
     ├── Clientes/
     ├── configuracionGeneral/
     ├── Inventario/
     ├── ParametrosSistema/
     ├── Pedido/
     ├── Productos/
     ├── Reportes/
     ├── Usuarios/
     └── Venta/

Cada módulo sigue la estructura:

Estructura por módulo:
```
<modulo>/
  models/ 
  repositories/ 
  services/
  controllers/
  schemas/
```

---

## 6. Variables de entorno

Variables de entorno utilizadas por el backend del sistema **SGM-DALCT Market** para su correcta configuración y funcionamiento:

- **`DATABASE_URL`**: Cadena de conexión a la base de datos PostgreSQL. Es utilizada por SQLAlchemy para establecer comunicación con el servidor de base de datos.  
  **Ejemplo:** `postgresql://dalctuser:Dalct1234@servicio-bdpostgres:5432/dalctmarket`

- **`SECRET_KEY`**: Clave secreta utilizada para firmar y validar los tokens JWT, garantizando la seguridad y autenticidad en los procesos de autenticación y autorización.  
  **Ejemplo:** `A1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6`

- **`ALGORITHM`**: Algoritmo criptográfico empleado para la firma de los tokens JWT.  
  **Ejemplo:** `HS256`

- **`ACCESS_TOKEN_EXPIRE_MINUTES`**: Define el tiempo (en minutos) durante el cual un token de acceso es válido antes de expirar.  
  **Ejemplo:** `30`

- **`TZ`**: Zona horaria configurada para el sistema, utilizada para el manejo correcto de fechas y horas en registros, ventas y auditorías.  
  **Ejemplo:** `America/Guayaquil`

Estas variables permiten separar la configuración del código fuente, fortaleciendo la seguridad y facilitando el despliegue del backend en distintos entornos.



## 7. Repositorio de Código
- **Enlace:** [Repositorio](https://github.com/Damian2044/T02_03_DALCTMarket_Grupo06.git)

### 7.1 Clonación y uso
##### 7.1.1 Clonar y acceder al backend:
```bash
git clone https://github.com/Damian2044/T02_03_DALCTMarket_Grupo06.git
cd T02_03_DALCTMarket_Grupo06
```

#### 7.1.2 Ejecutar con Docker Compose (recomendado):
```bash
docker compose up --build
# o en segundo plano:
# docker compose up -d --build
```
Este método levanta automáticamente el backend junto con la base de datos PostgreSQL, evitando configuraciones manuales y asegurando un entorno consistente.

#### 7.1.3 Ejecución local:
También puede ejecutarse de forma local, pero en este caso se debe crear y configurar manualmente la base de datos PostgreSQL y definir correctamente las variables de entorno.

#### 7.1.3.1 Instalar dependencias:
```bash
pip install -r requerimientos.txt
```

#### 7.1.3.2 Iniciar el proyecto:
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## 8. Documentación interactiva:
- Local: http://localhost:8000/docs
- Deploy: https://t02-03-dalctmarket-grupo06.onrender.com/docs

Nota: El backend está desplegado en Render, por lo que al acceder por primera vez puede existir un tiempo de espera mientras el servicio se reactiva (cold start).

## 8. Datos de prueba 

El sistema incluye **usuarios por defecto** con el objetivo de facilitar las pruebas funcionales y el acceso inicial a la aplicación.  
El **método de autenticación** se realiza mediante la **cédula del usuario** (`cedulaUsuario`).

> **Nota:** Todos los usuarios listados utilizan la misma contraseña por defecto:  
> **`1234`**

### Tabla de usuarios por defecto

| Nombre completo         | Usuario / Cédula (login) | Rol |
|-------------------------|--------------------------|-----|
| admin                   | `admin`                  | Administrador |
| bodeguero               | `bodeguero`              | Bodeguero |
| cajero                  | `cajero`                 | Cajero |
| Damian Barahona         | `1750834515`             | Administrador |
| Kenin Cayambe           | `1750834516`             | Bodeguero |
| Sthalin Chasipanta      | `1750834517`             | Bodeguero |
| Cristian Licto          | `1750834518`             | Cajero |
| Juan Tandazo            | `1750834519`             | Cajero |


Además de los usuarios, el sistema inicializa automáticamente **datos básicos de otros módulos**, con el fin de permitir el uso inmediato de la aplicación sin configuraciones manuales adicionales. Entre estos datos se incluyen:
- **Parámetros del sistema:** valores iniciales de configuración general.
- **Roles de usuario:** Administrador(id=1), Bodeguero(id=2) y Cajero(id=3).
- **Categorías de productos:** categorías base para la gestión del inventario.
- **Productos de ejemplo:** productos asociados a cada categoría.
- **Clientes de prueba:** registros básicos para pruebas de ventas.

Estos datos se crean automáticamente durante la inicialización del sistema y están destinados para **entornos de desarrollo y pruebas**.
---

## 9. Distribución de tareas por integrante:

| Integrante            | Tareas |
|-----------------------|--------|
| **Damian Barahona**   | • Configuración inicial de FastAPI, Pydantic y SQLAlchemy.<br>• Desarrollo completo del módulo **Parámetros del Sistema** y **Usuarios**. |
| **Kenin Cayambe**     | • Desarrollo completo del módulo **Clientes** (models, repositories, services y controllers). |
| **Sthalin Chasipanta**| • Desarrollo completo de los módulos **Pedido** y **Venta** (models, repositories, services y controllers). |
| **Cristian Licto**    | • Desarrollo del **PDF**, incluyendo descripción de la aplicación, tecnologías utilizadas, arquitectura, repositorio y funcionamiento de los servicios. |
| **Juan Tandazo**     | • Desarrollo completo de los módulos **Productos**, **Inventario**, **Caja** y **Reportes** (services y controllers, consumo de datos de otros módulos). |


---