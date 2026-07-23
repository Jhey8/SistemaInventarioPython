import { ModulosAPI } from "./api/inventario_api.js";
import { escapar } from "./utils/helpers.js";

const SUBREPORTES = [
    { ruta: "reportes/valorizado", icono: "bi-cash-stack", nombre: "Valorizado" },
    { ruta: "reportes/movimientos", icono: "bi-arrow-left-right", nombre: "Movimientos" },
    { ruta: "reportes/reposicion", icono: "bi-graph-up-arrow", nombre: "Reposición" },
    { ruta: "reportes/vencimientos", icono: "bi-calendar-x", nombre: "Vencimientos" },
    { ruta: "reportes/bajo-stock", icono: "bi-exclamation-triangle", nombre: "Bajo stock" },
    { ruta: "reportes/compras", icono: "bi-truck", nombre: "Compras" },
];

const V = Date.now();

const rutas = {
    dashboard: { html: "views/dashboard.html", js: "./views/dashboard.js" },
    productos: { html: "views/productos.html", js: "./views/productos.js" },
    inventario: { html: "views/inventario.html", js: "./views/inventario.js" },
    proveedores: { html: "views/proveedores.html", js: "./views/proveedores.js" },
    categorias: { html: "views/categorias.html", js: "./views/categorias.js" },
    perfiles: { html: "views/perfiles.html", js: "./views/perfiles.js" },
    usuarios: { html: "views/usuarios.html", js: "./views/usuarios.js" },

    reportes: { redirigir: "reportes/valorizado" },
    "reportes/valorizado": { html: "views/reportes/valorizado.html", js: "./views/reportes/valorizado.js" },
    "reportes/movimientos": { html: "views/reportes/movimientos.html", js: "./views/reportes/movimientos.js" },
    "reportes/reposicion": { html: "views/reportes/reposicion.html", js: "./views/reportes/reposicion.js" },
    "reportes/vencimientos": { html: "views/reportes/vencimientos.html", js: "./views/reportes/vencimientos.js" },
    "reportes/bajo-stock": { html: "views/reportes/bajo_stock.html", js: "./views/reportes/bajo_stock.js" },
    "reportes/compras": { html: "views/reportes/compras.html", js: "./views/reportes/compras.js" },
};

let vistaInicial = "dashboard";

const SECCIONES = [
    { titulo: "Principal", rutas: ["dashboard"] },
    { titulo: "Operaciones", rutas: ["productos", "inventario", "categorias", "proveedores"] },
    { titulo: "Análisis", rutas: ["reportes"] },
    { titulo: "Administración", rutas: ["perfiles", "usuarios"] },
];

export async function construirMenu() {
    const menu = document.getElementById("menu-lateral");
    let modulos = [];
    try {
        modulos = await ModulosAPI.menu();
    } catch {
        modulos = [];
    }

    const asignados = new Set();
    let html = "";
    SECCIONES.forEach((seccion) => {
        const propios = modulos.filter((m) => seccion.rutas.includes(m.ruta));
        if (!propios.length) return;
        propios.forEach((m) => asignados.add(m.ruta));
        html += `<div class="sidebar-seccion">${seccion.titulo}</div>` +
            propios.map(pintarItem).join("");
    });
    const restantes = modulos.filter((m) => !asignados.has(m.ruta));
    if (restantes.length) {
        html += `<div class="sidebar-seccion">Otros</div>` + restantes.map(pintarItem).join("");
    }

    menu.innerHTML = html;
    vistaInicial = modulos.length ? modulos[0].ruta : "dashboard";
}

function pintarItem(m) {
    if (m.ruta === "reportes") return pintarGrupoReportes(m);
    return `
        <a href="javascript:void(0)" class="enlace-nav" data-vista="${escapar(m.ruta)}">
            <i class="bi ${escapar(m.icono)}"></i><span>${escapar(m.nombre)}</span>
        </a>`;
}

function pintarGrupoReportes(m) {
    const subs = SUBREPORTES.map((s) => `
        <a href="javascript:void(0)" class="enlace-nav enlace-sub" data-vista="${s.ruta}">
            <i class="bi ${s.icono}"></i><span>${s.nombre}</span>
        </a>`).join("");
    return `
        <a class="enlace-nav" data-bs-toggle="collapse" href="#submenu-reportes" role="button">
            <i class="bi ${escapar(m.icono)}"></i><span>${escapar(m.nombre)}</span>
            <i class="bi bi-chevron-down ms-auto small"></i>
        </a>
        <div class="collapse" id="submenu-reportes">${subs}</div>`;
}

export async function navegar(nombre) {
    let ruta = rutas[nombre] || rutas[vistaInicial] || rutas.dashboard;
    if (ruta.redirigir) {
        return navegar(ruta.redirigir);
    }
    const contenido = document.getElementById("contenido");
    try {
        const [html, modulo] = await Promise.all([
            fetch(`${ruta.html}?v=${V}`).then((r) => r.text()),
            import(`${ruta.js}?v=${V}`),
        ]);
        contenido.innerHTML = html;
        mostrarCargaEnTablas(contenido);
        if (modulo.init) await modulo.init();
        contenido.querySelectorAll(".fila-cargando").forEach((f) => f.remove());
        marcarActivo(nombre);
    } catch (e) {
        contenido.innerHTML =
            `<div class="alert alert-danger">No se pudo cargar la vista: ${escapar(e.message)}</div>`;
    }
}

function mostrarCargaEnTablas(contenido) {
    contenido.querySelectorAll("table tbody").forEach((cuerpo) => {
        if (cuerpo.children.length) return;
        const columnas = cuerpo.closest("table").querySelectorAll("thead th").length || 1;
        cuerpo.innerHTML = `
            <tr class="fila-cargando"><td colspan="${columnas}" class="text-center text-muted py-4">
                <div class="spinner-border spinner-border-sm me-2" role="status"></div>Cargando datos…
            </td></tr>`;
    });
}

function marcarActivo(nombre) {
    document.querySelectorAll("[data-vista]").forEach((el) => {
        el.classList.toggle("active", el.dataset.vista === nombre);
    });

    if (nombre.startsWith("reportes/")) {
        document.getElementById("submenu-reportes")?.classList.add("show");
    }
}

let routerIniciado = false;

function cerrarSidebarEnMovil() {
    if (window.innerWidth <= 768) document.body.classList.add("sidebar-oculto");
}

function prepararTablasResponsivas() {
    const contenido = document.getElementById("contenido");

    const procesar = () => {
        contenido.querySelectorAll("table").forEach((tabla) => {
            tabla.classList.add("tabla-plegable");
            const encabezados = [...tabla.querySelectorAll("thead th")];
            const titulos = encabezados.map((th) => th.textContent.trim());
            if (titulos.length < 3) return;
            const inicio = titulos[0] === "ID" ? 1 : 0;
            const ultimaEsAccion = titulos[titulos.length - 1] === "Acciones";
            const visibles = new Set([inicio, ultimaEsAccion ? titulos.length - 1 : inicio + 1]);

            encabezados.forEach((th, i) => {
                if (!visibles.has(i)) th.classList.add("celda-oculta-movil");
            });

            tabla.querySelectorAll("tbody > tr").forEach((fila) => {
                if (fila.classList.contains("fila-detalle") || fila.dataset.plegable) return;
                fila.dataset.plegable = "1";
                const celdas = [...fila.children];
                if (celdas.length < 3 || celdas[0].hasAttribute("colspan")) return;

                celdas.forEach((celda, i) => {
                    if (!visibles.has(i)) {
                        celda.classList.add("celda-oculta-movil");
                        celda.dataset.label = titulos[i] || "";
                    }
                });
                celdas[inicio].insertAdjacentHTML("afterbegin",
                    `<button type="button" class="btn-expandir" title="Ver más"><i class="bi bi-plus"></i></button>`);
            });
        });
    };

    const observador = new MutationObserver(() => {
        observador.disconnect();
        procesar();
        observador.observe(contenido, { childList: true, subtree: true });
    });
    procesar();
    observador.observe(contenido, { childList: true, subtree: true });

    contenido.addEventListener("click", (e) => {
        const boton = e.target.closest(".btn-expandir");
        if (!boton) return;
        const fila = boton.closest("tr");
        let detalle = fila.nextElementSibling;
        if (!detalle || !detalle.classList.contains("fila-detalle")) {
            detalle = document.createElement("tr");
            detalle.className = "fila-detalle";
            const ocultas = [...fila.querySelectorAll("td.celda-oculta-movil")];
            detalle.innerHTML = `<td colspan="${fila.children.length}">` + ocultas.map((c) =>
                `<div class="detalle-item"><span>${c.dataset.label}</span><span>${c.innerHTML}</span></div>`).join("") + `</td>`;
            fila.after(detalle);
        }
        const abierta = detalle.classList.toggle("abierta");
        boton.classList.toggle("abierto", abierta);
        boton.innerHTML = `<i class="bi ${abierta ? "bi-dash" : "bi-plus"}"></i>`;
    });
}

export function iniciarRouter() {
    if (routerIniciado) return;
    routerIniciado = true;

    document.getElementById("menu-lateral").addEventListener("click", (e) => {
        const enlace = e.target.closest("[data-vista]");
        if (!enlace) return;
        e.preventDefault();
        navegar(enlace.dataset.vista);
        cerrarSidebarEnMovil();
    });

    document.addEventListener("click", (e) => {
        const enlace = e.target.closest("[data-nav]");
        if (!enlace) return;
        e.preventDefault();
        navegar(enlace.dataset.nav);
        cerrarSidebarEnMovil();
    });

    prepararTablasResponsivas();
}
