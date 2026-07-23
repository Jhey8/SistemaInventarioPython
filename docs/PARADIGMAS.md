# Guía de paradigmas del proyecto

Este documento señala **dónde está aplicado cada paradigma** en el código, con archivos y ejemplos concretos, como apoyo para la sustentación.

## 1. Programación Orientada a Objetos (POO)

Vive en la capa **models** del backend: cada entidad es una clase que encapsula sus datos y sus reglas.

| Concepto | Dónde | Detalle |
|---|---|---|
| **Clases y encapsulación** | `backend/models/*.py` | `Producto`, `Categoria`, `Proveedor`, `Usuario`, `Perfil`, `Movimiento`, `Modulo`: cada una valida sus propios datos en `validar()` al construirse. |
| **Herencia** | `backend/models/producto.py` | `ProductoPerecedero(Producto)` extiende al producto base agregando `fecha_vencimiento` y `esta_vencido`. |
| **Polimorfismo** | `backend/models/producto.py` | La propiedad `tipo` y el método `to_dict()` se **sobreescriben** en la subclase; el resto del sistema los usa sin saber qué clase concreta recibe. |
| **Propiedades calculadas** | `backend/models/producto.py`, `movimiento.py` | `valor_total`, `necesita_reposicion`, `activo`, `esta_vencido` (con `@property`); `Movimiento.aplicar_a_stock()` encapsula la regla de cómo cada tipo de movimiento afecta el stock. |
| **Fábricas** | todos los models | Funciones `crear_producto(datos)`, `crear_movimiento(datos)`, etc., que construyen el objeto correcto a partir de un diccionario (en productos decide entre `Producto` y `ProductoPerecedero`). |

## 2. Programación Funcional

Vive en la capa de **reportes**: funciones puras que transforman colecciones sin modificar estado.

| Técnica | Dónde | Ejemplo |
|---|---|---|
| **`reduce`** | `backend/services/reportes_service.py` | `valor_total_inventario`, `unidades_totales`, `valor_por_categoria`, `conteo_por_categoria`; y la agregación del consumo por producto en `prediccion_reposicion`. |
| **`filter` + lambdas** | mismo archivo | `productos_bajo_stock = filter(lambda p: p.necesita_reposicion, productos)`; clasificación de movimientos por tipo en `resumen_movimientos`. |
| **`map` / comprensiones** | services y controllers | Transformación de objetos a diccionarios (`[p.to_dict() for p in productos]`), proyecciones de columnas para exportar. |
| **Funciones puras** | `reportes_service.py` | Todas las métricas reciben la lista y devuelven un resultado nuevo, sin efectos secundarios — misma entrada, misma salida. |
| **Funcional en JS** | `frontend/js/views/*.js` | `map`/`filter`/`reduce`/`sort` para filtrar tablas, calcular tarjetas y armar los gráficos en el cliente. |

## 3. Librería externa: pandas

| Uso | Dónde |
|---|---|
| Análisis tabular (agrupar por categoría, promedios, rankings) | `reportes_service.analisis_pandas` — `DataFrame`, `groupby`, `agg`, `sort_values`. |
| Compras por proveedor | `reportes_service.compras_por_proveedor`. |
| Exportación a Excel | `backend/services/exportacion_service.py` — `pd.ExcelWriter` con motor `openpyxl`. |

Otras librerías: **Flask** (web), **werkzeug.security** (hash de contraseñas), **fpdf2** (PDF), **Chart.js / SweetAlert2 / Bootstrap** (frontend).

## 4. Programación estructurada / imperativa

Las capas **controllers**, **routes** y **repositories** siguen un flujo imperativo claro: recibir la petición → validar → ejecutar SQL → responder. Ejemplo destacado: `movimiento_repository.registrar()` ejecuta una **transacción** paso a paso (bloquear fila con `FOR UPDATE`, calcular stock, actualizar, insertar, `commit`/`rollback`).

## 5. Programación orientada a eventos (frontend)

Toda la interfaz reacciona a eventos del DOM: `addEventListener` para clics, formularios (`submit` con `preventDefault` — por eso nada recarga la página), filtros en vivo (`input`), y un `MutationObserver` que adapta las tablas al modo móvil cada vez que se repintan (`frontend/js/router.js`).

## 6. Arquitectura por capas (separación de responsabilidades)

```
routes  →  controllers  →  services  →  repositories  →  MySQL
 (URLs)     (HTTP↔JSON)    (reglas de     (SQL puro)
                            negocio)
                 ↑
              models (POO: entidades y validación)
```

Cada capa tiene **una sola responsabilidad**: las rutas no conocen SQL, los repositorios no conocen HTTP, y las reglas de negocio están concentradas en services y models. El frontend replica la idea: `api/` (única capa que llama al backend), `views/` (lógica de cada pantalla), `utils/` (helpers compartidos), `router.js` (navegación SPA).
