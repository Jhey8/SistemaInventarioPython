# Sistema de Inventario

> **Nota de uso:** este documento sigue la estructura solicitada. Reemplaza los campos entre corchetes `[ ]` con tus datos y agrega las capturas donde se indica. Puedes abrirlo en Word (o copiar/pegar) para darle el formato final.

---

## 1. Carátula

**[NOMBRE DE LA UNIVERSIDAD / INSTITUCIÓN]**
**[FACULTAD / ESCUELA]**

**Proyecto:** Sistema de Inventario
**Curso:** Programación Multiparadigma
**Docente:** [Nombre del docente]
**Integrante(s):** [Tus nombres y apellidos]
**Ciclo / Sección:** [ ]
**Fecha:** [ ]

---

## 2. Introducción

El presente informe describe el desarrollo del **Sistema de Inventario**, una aplicación web orientada a la gestión de productos, movimientos de stock y reportes para un almacén o negocio. El proyecto se enmarca en el curso de Programación Multiparadigma, por lo que su objetivo académico central es **aplicar y contrastar distintos paradigmas de programación** (estructurada, orientada a objetos y funcional) dentro de un mismo software funcional.

El sistema permite registrar productos y categorías, administrar proveedores, controlar entradas y salidas de mercadería con su respectivo historial (kardex), gestionar usuarios con permisos por perfil y generar reportes analíticos con exportación a Excel y PDF. Adicionalmente, incorpora funcionalidades innovadoras como la **predicción de reposición** de stock y las **alertas de vencimiento** de productos perecederos.

A lo largo del documento se detalla el problema que resuelve, la justificación, los objetivos, la arquitectura, las tecnologías empleadas y —de forma especial— cómo cada paradigma de programación se aplica en partes concretas del código.

---

## 3. Planteamiento del problema

En muchos negocios pequeños y medianos el control de inventario se realiza de forma **manual (cuadernos u hojas de cálculo)**, lo que genera problemas frecuentes:

- **Pérdida de información** y falta de trazabilidad: no se sabe quién movió el stock, cuándo ni por qué.
- **Quiebres de stock** (productos agotados) o **sobre-stock**, por no anticipar el consumo.
- **Productos vencidos** que no se detectan a tiempo, generando pérdidas.
- **Errores humanos** al calcular valores, cantidades o al registrar datos inconsistentes.
- **Falta de control de acceso**: cualquiera puede modificar la información, sin roles ni responsabilidades.

El problema central es entonces: **¿cómo llevar un control de inventario confiable, seguro y que además ayude a tomar decisiones (qué comprar, qué está por vencer) en lugar de solo registrar datos?**

---

## 4. Justificación

El desarrollo de este sistema se justifica en tres planos:

- **Académico:** es un caso real y completo para demostrar la aplicación práctica de los tres paradigmas del curso. La lógica de negocio (modelos con herencia), el flujo de peticiones (estructurado) y los cálculos de reportes (funcional con `map/filter/reduce`) conviven de forma natural, lo que permite comparar sus ventajas.
- **Práctico:** resuelve una necesidad concreta de cualquier negocio con almacén, automatizando el control de stock, reduciendo errores y agilizando la generación de reportes.
- **Tecnológico:** utiliza tecnologías vigentes y una **arquitectura por capas** que separa responsabilidades, haciendo el sistema mantenible, seguro y escalable. Además, se desplegó en la nube, demostrando que es un producto usable y no solo un ejercicio local.

---

## 5. Objetivos

### 5.1 Objetivo general

Desarrollar un sistema web de gestión de inventario que permita administrar productos, controlar movimientos de stock y generar reportes, aplicando de manera integrada los paradigmas de programación estructurada, orientada a objetos y funcional.

### 5.2 Objetivos específicos

- Implementar un **CRUD completo** de productos, categorías, proveedores, usuarios y perfiles.
- Registrar **entradas, salidas y ajustes** de stock de forma transaccional, manteniendo un **historial (kardex)** por producto.
- Aplicar **programación orientada a objetos** en el modelado del dominio (con herencia y polimorfismo).
- Aplicar **programación funcional** en el cálculo de métricas y reportes.
- Generar **reportes** con filtros, gráficos y **exportación a Excel y PDF**.
- Incorporar funcionalidades de valor agregado: **predicción de reposición** y **alertas de vencimiento**.
- Garantizar la **seguridad** mediante autenticación, contraseñas cifradas y **permisos por perfil**.
- Implementar **validaciones** robustas y un **manejo de excepciones** consistente.
- **Desplegar** el sistema en un entorno en la nube.

---

## 6. Descripción del sistema

El Sistema de Inventario es una **aplicación web tipo SPA** (Single Page Application): la interfaz se carga una sola vez y la navegación entre módulos ocurre sin recargar la página. Está compuesto por:

- Un **backend** en Python con Flask que expone una **API REST** y sirve la interfaz.
- Un **frontend** en JavaScript (módulos ES) que consume la API.
- Una **base de datos MySQL** que almacena toda la información.

El usuario inicia sesión y, según su **perfil**, ve solo los módulos a los que tiene permiso. Desde ahí puede gestionar el catálogo, registrar movimientos de inventario, consultar reportes y —si es administrador— gestionar usuarios y perfiles. Toda variación de stock queda registrada con su fecha, usuario responsable y documento asociado, lo que garantiza trazabilidad total.

---

## 7. Tecnologías y herramientas utilizadas

| Categoría | Herramienta | Uso en el proyecto |
|---|---|---|
| Lenguaje backend | **Python 3.12** | Lógica del servidor |
| Framework web | **Flask** | API REST y servidor de la aplicación |
| Servidor producción | **Gunicorn** | Ejecución del backend en la nube |
| Base de datos | **MySQL / MariaDB** | Almacenamiento de datos |
| Conector BD | **mysql-connector-python** | Conexión + *pool* de conexiones |
| Análisis de datos | **pandas** | Agrupaciones y cálculos de reportes |
| Exportación | **openpyxl** (Excel), **fpdf2** (PDF) | Descarga de reportes |
| Seguridad | **werkzeug.security** | Hash de contraseñas |
| Lenguaje frontend | **JavaScript (módulos ES)** | Interactividad de la interfaz |
| Estilos / UI | **Bootstrap 5**, **Bootstrap Icons** | Diseño responsivo |
| Gráficos | **Chart.js** | Visualizaciones de reportes y dashboard |
| Diálogos | **SweetAlert2** | Confirmaciones de acciones |
| Control de versiones | **Git / GitHub** | Versionado del código |
| Despliegue | **Render** (app) + **Aiven** (MySQL) | Sistema en la nube |
| Editor | **Visual Studio Code** | Desarrollo |

---

## 8. Funcionalidades principales del software

- **Autenticación y sesión**: inicio de sesión con usuario y contraseña cifrada; cierre de sesión; cambio de contraseña propia.
- **Permisos por perfil**: cada perfil ve y accede solo a los módulos que tiene asignados.
- **Gestión de productos**: CRUD, con soporte para productos **perecederos** (fecha de vencimiento). Indicador de bajo stock.
- **Gestión de categorías y proveedores**: CRUD con validaciones (RUC con dígito verificador, teléfono, correo).
- **Inventario (movimientos)**: registro de **entradas, salidas y ajustes** por producto; actualización de stock **transaccional**; **historial/kardex** por producto.
- **Reportes** (6): inventario valorizado, movimientos/kardex, **reposición sugerida**, **vencimientos**, bajo stock y compras por proveedor. Con filtros, gráficos y **exportación a Excel y PDF**.
- **Predicción de reposición**: a partir del consumo histórico estima días hasta agotarse y cantidad sugerida de compra.
- **Alertas de vencimiento**: identifica productos vencidos o próximos a vencer.
- **Gestión de usuarios y perfiles**: CRUD con reglas de seguridad (los administradores se protegen entre sí).
- **Eliminación lógica**: los registros no se borran físicamente; se manejan tres estados (activo, inactivo, eliminado), conservando el historial.
- **Dashboard**: tarjetas de resumen, gráficos y paneles de bajo stock y últimos movimientos.

---

## 9. Arquitectura y estructura del sistema

El sistema utiliza una **arquitectura por capas** que separa responsabilidades. Cada capa tiene una única función y solo se comunica con la contigua.

```
                       NAVEGADOR (usuario)
                              │
        ┌─────────────────────▼─────────────────────┐
        │              FRONTEND  (SPA)               │
        │                                            │
        │   index.html                               │
        │     ├─ router.js   →  navegación           │
        │     ├─ api/        →  llamadas a la API     │
        │     ├─ utils/      →  helpers y validación  │
        │     └─ views/      →  lógica de cada módulo │
        └─────────────────────┬─────────────────────┘
                              │
                     Peticiones HTTP (JSON)
                              │
        ┌─────────────────────▼─────────────────────┐
        │        BACKEND  (API REST - Flask)         │
        │                                            │
        │   routes/        →  URLs + permisos        │
        │        │                                   │
        │        ▼                                   │
        │   controllers/   →  reciben y devuelven JSON│
        │        │                                   │
        │        ▼                                   │
        │   services/      →  reglas de negocio       │
        │        │             (usan  models/ = POO)  │
        │        ▼                                   │
        │   repositories/  →  acceso a datos (SQL)    │
        └─────────────────────┬─────────────────────┘
                              │
                              ▼
                    BASE DE DATOS  (MySQL)
```

**Flujo de una petición (de arriba hacia abajo y de regreso):**

1. El **frontend** llama a la API.
2. La capa **routes** valida que el perfil tenga permiso.
3. El **controller** recibe los datos.
4. El **service** aplica las reglas de negocio, apoyándose en los **models** (POO).
5. El **repository** ejecuta el SQL en MySQL.
6. La respuesta regresa por el mismo camino y vuelve al frontend como **JSON**.

Esta separación hace que, por ejemplo, las rutas no conozcan SQL y los repositorios no conozcan HTTP, lo que facilita el mantenimiento. (Ver la estructura de carpetas completa en el archivo `README.md` y el diagrama entidad-relación en la sección de Anexos.)

---

## 10. Aplicación de los paradigmas de programación

### 10.1 Programación estructurada

Se aplica en el **flujo de control** de las capas de rutas, controladores y repositorios: secuencias de pasos, condicionales y bucles bien definidos.

El caso más representativo es el **registro de un movimiento de stock** (`repositories/movimiento_repository.py`), que ejecuta una **transacción** paso a paso:

1. Bloquea la fila del producto (`SELECT ... FOR UPDATE`).
2. Calcula el nuevo stock.
3. Actualiza el producto.
4. Inserta el movimiento.
5. Confirma (`commit`) o revierte (`rollback`) si algo falla.

También es estructurada la lógica de las rutas (`routes/`), donde cada endpoint sigue una secuencia clara: recibir la petición → delegar → responder.

### 10.2 Programación orientada a objetos

Se aplica en la capa **models**, donde cada entidad del dominio es una **clase** que encapsula sus datos y reglas.

- **Encapsulación:** cada modelo (`Producto`, `Proveedor`, `Usuario`, `Movimiento`, etc.) valida sus propios datos en el método `validar()` al construirse.
- **Herencia:** `ProductoPerecedero` **hereda** de `Producto` y añade el atributo `fecha_vencimiento` y la propiedad `esta_vencido`.
- **Polimorfismo:** la propiedad `tipo` y el método `to_dict()` se **sobrescriben** en la subclase; el resto del sistema los usa sin saber qué clase concreta recibe.
- **Propiedades calculadas** (`@property`): `valor_total`, `necesita_reposicion`, `esta_vencido`.
- **Método con regla de negocio:** `Movimiento.aplicar_a_stock()` encapsula cómo cada tipo de movimiento (entrada/salida/ajuste) afecta el stock.

### 10.3 Programación funcional

Se aplica en la capa de **reportes** (`services/reportes_service.py`), con **funciones puras** que transforman colecciones sin modificar el estado.

- `reduce`: para sumar el valor total del inventario, las unidades totales y agrupar valores por categoría.
- `filter` + `lambda`: para obtener los productos bajo stock o clasificar movimientos por tipo.
- `map` / comprensiones de listas: para transformar objetos en diccionarios (`[p.to_dict() for p in productos]`).
- Las métricas reciben la lista de datos y devuelven un resultado nuevo, con la misma salida para la misma entrada (sin efectos secundarios).

En el **frontend** también se usa el estilo funcional (`map`, `filter`, `reduce`, `sort`) para filtrar tablas y construir gráficos y tarjetas en el cliente.

---

## 11. Manejo de excepciones

El sistema define una **jerarquía de excepciones propias** en `exceptions/errores.py`, donde cada error del dominio lleva su **código HTTP** correspondiente:

- `InventarioError` (base, 400)
  - `DatosInvalidosError` (400) — datos que no cumplen una validación.
  - `ProductoNoEncontradoError`, `CategoriaNoEncontradaError`, etc. (404).
  - `StockInsuficienteError` (409) — se intenta retirar más stock del disponible.
  - `CredencialesInvalidasError` (401), `NoAutenticadoError` (401), `NoAutorizadoError` (403).

En `app.py` hay dos **manejadores globales**:

1. Para los errores de negocio (`InventarioError`): devuelve el mensaje al usuario con su código HTTP (mensajes seguros y claros, como *"No hay stock suficiente"*).
2. Para cualquier error inesperado: **registra el detalle en el log** del servidor pero devuelve al cliente un mensaje genérico *"Ocurrió un error interno"*, evitando exponer información sensible.

Además, cada operación del frontend está envuelta en `try/catch`, mostrando el error mediante notificaciones (*toasts*) sin romper la aplicación.

---

## 12. Evaluación de la eficiencia y pertinencia de los paradigmas

| Paradigma | Dónde se usó | Por qué fue el más pertinente |
|---|---|---|
| **Estructurada** | Rutas, controladores, transacción de movimientos | Ideal para **flujos secuenciales** con pasos claros y control de errores (ej. la transacción de stock, donde el orden importa). |
| **Orientada a objetos** | Modelos del dominio | Ideal para **representar entidades del mundo real** y sus reglas. La herencia (`Producto`→`ProductoPerecedero`) evitó duplicar código y el polimorfismo simplificó el resto del sistema. |
| **Funcional** | Cálculos de reportes y métricas | Ideal para **transformar y agregar datos** sin efectos secundarios. Con `reduce/map/filter` los cálculos quedaron cortos, legibles y fáciles de probar. |

**Conclusión de la evaluación:** ningún paradigma es "mejor" en absoluto; cada uno es más **eficiente y pertinente** según el tipo de problema. La combinación de los tres permitió un sistema más limpio que si se hubiera usado uno solo: OOP para el dominio, funcional para los cálculos y estructurada para el flujo. La eficiencia también se cuidó a nivel técnico con un **pool de conexiones** a la base de datos y la **paralelización** de llamadas en el frontend, que redujeron los tiempos de carga.

---

## 13. Demostración del funcionamiento del sistema

> *(Insertar aquí capturas de pantalla de cada flujo. Sugerencia de secuencia:)*

1. **Inicio de sesión** — pantalla de login. *(captura)*
2. **Dashboard** — tarjetas de resumen y gráficos. *(captura)*
3. **Productos** — listado, crear/editar producto. *(captura)*
4. **Inventario** — registrar una entrada y una salida; ver el kardex. *(captura)*
5. **Reporte de reposición** — mostrando la sugerencia de compra. *(captura)*
6. **Reporte de vencimientos** — productos por vencer. *(captura)*
7. **Exportación** — un Excel y un PDF descargados. *(captura)*
8. **Usuarios y perfiles** — creación de un perfil con módulos y un usuario. *(captura)*
9. **Validaciones** — ejemplo de un mensaje de error (RUC inválido, stock insuficiente). *(captura)*

**Sistema en línea:** [URL de Render] — Usuario de prueba: `admin` / `[contraseña]`.

---

## 14. Resultados

- Se obtuvo un **sistema web funcional y desplegado en la nube**, accesible desde cualquier navegador.
- Se implementaron **8 módulos** de gestión y **6 reportes** con exportación a Excel y PDF.
- Se integraron los **tres paradigmas** de forma clara y justificada dentro del mismo software.
- Se incorporaron **funcionalidades innovadoras** (predicción de reposición y alertas de vencimiento) que aportan valor más allá del simple registro.
- Se logró un sistema **seguro** (contraseñas cifradas, permisos por perfil, protección entre administradores) y con **~60 validaciones** en doble capa (frontend + backend).
- Se cuidó la **eficiencia** (pool de conexiones, carga en paralelo) y la **experiencia de usuario** (diseño responsivo, sin recargas, confirmaciones).

---

## 15. Conclusiones

- El proyecto cumplió el objetivo académico de **aplicar e integrar los tres paradigmas** de programación en un software real, evidenciando que cada uno es más adecuado para cierto tipo de problema.
- La **arquitectura por capas** resultó clave para mantener el código organizado y para que los paradigmas convivieran sin mezclarse.
- Un buen **manejo de excepciones y validaciones** en el backend es indispensable para la integridad de los datos, ya que las validaciones del frontend por sí solas pueden ser evadidas.
- Incorporar **funcionalidades que ayudan a decidir** (predicción, alertas) transforma un simple registro de datos en una herramienta útil de gestión.

---

## 16. Recomendaciones

- Cambiar la **contraseña por defecto** del administrador antes de un uso real.
- Para un entorno productivo, añadir **límite de intentos de login** y **expiración de sesión**.
- Agregar **pruebas automatizadas** (pytest) sobre la capa de servicios para asegurar las reglas de negocio ante futuros cambios.
- A futuro, ampliar con un **módulo de clientes** y reportes de rentabilidad (precio de compra vs. venta).
- Considerar **paginación** en las tablas cuando el volumen de datos crezca.

---

## 17. Referencias bibliográficas

> *(Formato APA. Ajusta las fechas de consulta.)*

- Pallets Projects. (s. f.). *Flask Documentation*. https://flask.palletsprojects.com/
- Oracle. (s. f.). *MySQL Connector/Python Developer Guide*. https://dev.mysql.com/doc/connector-python/en/
- The pandas development team. (s. f.). *pandas documentation*. https://pandas.pydata.org/docs/
- Bootstrap. (s. f.). *Bootstrap 5 Documentation*. https://getbootstrap.com/
- Chart.js. (s. f.). *Chart.js Documentation*. https://www.chartjs.org/docs/
- Mozilla. (s. f.). *MDN Web Docs — JavaScript*. https://developer.mozilla.org/es/docs/Web/JavaScript
- SUNAT. (s. f.). *Estructura del Registro Único de Contribuyentes (RUC)*. https://www.sunat.gob.pe/

---

## 18. Anexos

- **Anexo A:** Diagrama entidad-relación de la base de datos *(ver `README.md`, se genera con el bloque Mermaid)*.
- **Anexo B:** Diagrama de la arquitectura por capas *(sección 9)*.
- **Anexo C:** Script de la base de datos (`schema.sql`).
- **Anexo D:** Guía detallada de paradigmas con referencias a archivos (`docs/PARADIGMAS.md`).
- **Anexo E:** Capturas de pantalla del sistema en funcionamiento.
- **Anexo F:** Enlace al repositorio de código (GitHub) y a la aplicación desplegada (Render).
