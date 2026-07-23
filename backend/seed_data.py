from repositories.database import get_connection
from services.usuario_service import UsuarioService
from services.categoria_service import CategoriaService
from services.inventario_service import InventarioService
from services.proveedor_service import ProveedorService

MODULOS = [
    ("Dashboard", "bi-speedometer2", "dashboard", 1),
    ("Productos", "bi-boxes", "productos", 2),
    ("Inventario", "bi-arrow-left-right", "inventario", 3),
    ("Proveedores", "bi-truck", "proveedores", 4),
    ("Reportes", "bi-graph-up", "reportes", 5),
    ("Categorías", "bi-tags", "categorias", 6),
    ("Perfiles", "bi-shield-lock", "perfiles", 7),
    ("Usuarios", "bi-people", "usuarios", 8),
]

USUARIO_ADMIN = {
    "usuario": "admin",
    "clave": "admin123",
    "nombre": "Administrador",
    "correo": "admin@inventario.local",
}

PROVEEDORES = [
    {
        "nombre_proveedor": "Distribuidora Tecnológica SAC",
        "ruc": "20123456786",
        "representante": "Juan Pérez",
        "telefono": "987654321",
        "correo": "ventas@distectec.pe",
        "direccion": "Av. Industrial 123, Lima",
    },
    {
        "nombre_proveedor": "Importaciones del Sur EIRL",
        "ruc": "20456789014",
        "representante": "María López",
        "telefono": "912345678",
        "correo": "contacto@impsur.pe",
        "direccion": "Jr. Comercio 456, Arequipa",
    },
]

CATEGORIAS = [
    {"nombre": "Tecnología", "descripcion": "Equipos y accesorios electrónicos"},
    {"nombre": "Papelería", "descripcion": "Útiles de oficina y escritura"},
    {"nombre": "Alimentos", "descripcion": "Productos de consumo"},
    {"nombre": "Limpieza", "descripcion": "Artículos de aseo y limpieza"},
]

PRODUCTOS = [
    {"nombre": "Laptop 14''", "categoria": "Tecnología", "cantidad": 12, "precio": 2500.0, "stock_minimo": 5},
    {"nombre": "Mouse inalámbrico", "categoria": "Tecnología", "cantidad": 3, "precio": 60.0, "stock_minimo": 10},
    {"nombre": "Teclado mecánico", "categoria": "Tecnología", "cantidad": 15, "precio": 180.0, "stock_minimo": 5},
    {"nombre": "Monitor 24''", "categoria": "Tecnología", "cantidad": 7, "precio": 650.0, "stock_minimo": 4},
    {"nombre": "Cuaderno A4", "categoria": "Papelería", "cantidad": 120, "precio": 4.5, "stock_minimo": 30},
    {"nombre": "Lapicero azul", "categoria": "Papelería", "cantidad": 8, "precio": 1.2, "stock_minimo": 20},
    {"nombre": "Resma de papel", "categoria": "Papelería", "cantidad": 40, "precio": 22.0, "stock_minimo": 15},
    {"nombre": "Leche entera 1L", "categoria": "Alimentos", "cantidad": 40, "precio": 5.0, "stock_minimo": 15, "fecha_vencimiento": "2026-08-30"},
    {"nombre": "Café molido 500g", "categoria": "Alimentos", "cantidad": 25, "precio": 22.0, "stock_minimo": 10, "fecha_vencimiento": "2026-12-15"},
    {"nombre": "Arroz 5kg", "categoria": "Alimentos", "cantidad": 60, "precio": 28.0, "stock_minimo": 20},
    {"nombre": "Detergente 1kg", "categoria": "Limpieza", "cantidad": 30, "precio": 15.0, "stock_minimo": 12},
    {"nombre": "Jabón líquido", "categoria": "Limpieza", "cantidad": 4, "precio": 9.5, "stock_minimo": 10},
]

def _tabla_vacia(tabla):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(f"SELECT COUNT(*) FROM {tabla}")
        return cursor.fetchone()[0] == 0
    finally:
        cursor.close()
        conn.close()

def _sembrar_perfil_usuario_y_menu():
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO perfiles (nombre, descripcion) VALUES (%s, %s)",
            ("Administrador", "Acceso total al sistema"),
        )
        id_perfil = cursor.lastrowid

        for nombre, icono, ruta, orden in MODULOS:
            cursor.execute(
                "INSERT INTO modulos (nombre, icono, ruta, orden) VALUES (%s, %s, %s, %s)",
                (nombre, icono, ruta, orden),
            )
            cursor.execute(
                "INSERT INTO perfil_modulo (id_perfil, id_modulo) VALUES (%s, %s)",
                (id_perfil, cursor.lastrowid),
            )
        conn.commit()
    finally:
        cursor.close()
        conn.close()

    datos_admin = dict(USUARIO_ADMIN, id_perfil=id_perfil)
    UsuarioService().crear_usuario(datos_admin)

def sembrar_datos_si_vacio():
    if _tabla_vacia("usuarios"):
        _sembrar_perfil_usuario_y_menu()
        print(f"Menú y usuario 'admin' creados (clave: {USUARIO_ADMIN['clave']}).")

    if _tabla_vacia("proveedores"):
        proveedor_service = ProveedorService()
        for datos in PROVEEDORES:
            proveedor_service.crear_proveedor(datos)
        print(f"{len(PROVEEDORES)} proveedores de ejemplo cargados.")

    if _tabla_vacia("categorias"):
        categoria_service = CategoriaService()
        producto_service = InventarioService()
        mapa_categorias = {}
        for categoria in CATEGORIAS:
            creada = categoria_service.crear_categoria(categoria)
            mapa_categorias[creada.nombre] = creada.id
        for producto in PRODUCTOS:
            datos = dict(producto)
            datos["categoria_id"] = mapa_categorias[datos.pop("categoria")]
            producto_service.crear_producto(datos)
        print(
            f"{len(CATEGORIAS)} categorías y {len(PRODUCTOS)} productos de ejemplo cargados."
        )
