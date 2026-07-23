import { ReportesAPI } from "../../api/inventario_api.js";
import { escapar, notificar, pintarTarjetas, graficoBarras, descargarArchivo } from "../../utils/helpers.js";

let productos = [];
let grafico = null;

export async function init() {
    ["f-buscar", "f-categoria", "f-orden", "f-min", "f-sinstock"].forEach((id) =>
        document.getElementById(id).addEventListener("input", aplicar));
    document.getElementById("btn-excel").addEventListener("click", () =>
        descargarArchivo(ReportesAPI.urlExportar("bajo-stock", "excel")));
    document.getElementById("btn-pdf").addEventListener("click", () =>
        descargarArchivo(ReportesAPI.urlExportar("bajo-stock", "pdf")));

    try {
        const datos = await ReportesAPI.bajoStock();
        if (!document.getElementById("tabla-bajo")) return;
        productos = datos.productos.map((p) => ({ ...p, faltante: Math.max(0, p.stock_minimo - p.cantidad) }));
        pintarResumen(datos.resumen);
        llenarCategorias();
        dibujarGrafico();
        aplicar();
    } catch (e) {
        notificar(e.message, "danger");
    }
}

function dibujarGrafico() {
    const top = [...productos].sort((a, b) => b.faltante - a.faltante).slice(0, 8);
    grafico = graficoBarras("grafico-bajo",
        top.map((p) => p.nombre), top.map((p) => p.faltante), "Faltante", grafico);
}

function pintarResumen(r) {
    pintarTarjetas("tarjetas-bajo", [
        { icono: "bi-boxes", valor: r.total_productos, label: "Productos totales" },
        { icono: "bi-exclamation-triangle", valor: r.bajo_stock, label: "Bajo stock" },
        { icono: "bi-x-octagon", valor: r.sin_stock, label: "Sin stock" },
        { icono: "bi-arrow-down-up", valor: r.unidades_faltantes, label: "Unidades faltantes" },
        { icono: "bi-percent", valor: r.total_productos ? Math.round(r.bajo_stock / r.total_productos * 100) + "%" : "0%", label: "% bajo stock" },
    ]);
}

function llenarCategorias() {
    const cats = [...new Set(productos.map((p) => p.categoria))].sort();
    document.getElementById("f-categoria").insertAdjacentHTML("beforeend",
        cats.map((c) => `<option value="${escapar(c)}">${escapar(c)}</option>`).join(""));
}

function aplicar() {
    const buscar = document.getElementById("f-buscar").value.toLowerCase();
    const categoria = document.getElementById("f-categoria").value;
    const orden = document.getElementById("f-orden").value;
    const min = Number(document.getElementById("f-min").value) || 0;
    const soloSinStock = document.getElementById("f-sinstock").checked;

    let filas = productos.filter((p) =>
        p.nombre.toLowerCase().includes(buscar) &&
        (!categoria || p.categoria === categoria) &&
        p.faltante >= min &&
        (!soloSinStock || p.cantidad === 0));

    filas.sort((a, b) => orden === "nombre"
        ? a.nombre.localeCompare(b.nombre)
        : b[orden] - a[orden]);

    render(filas);
}

function render(filas) {
    const cuerpo = document.getElementById("tabla-bajo");
    if (!filas.length) {
        cuerpo.innerHTML = '<tr><td colspan="6" class="text-center text-muted py-4">Sin resultados.</td></tr>';
        return;
    }
    cuerpo.innerHTML = filas.map((p) => `
    <tr class="${p.cantidad === 0 ? "fila-critica" : "fila-alerta"}">
      <td class="fw-medium">${escapar(p.nombre)}</td>
      <td><span class="badge rounded-pill text-bg-light">${escapar(p.categoria)}</span></td>
      <td class="text-end">${p.cantidad}</td>
      <td class="text-end">${p.stock_minimo}</td>
      <td class="text-end fw-medium">${p.faltante}</td>
      <td class="text-center">${p.cantidad === 0
            ? '<span class="badge text-bg-danger">Sin stock</span>'
            : '<span class="badge text-bg-warning">Bajo</span>'}</td>
    </tr>`).join("");
}
