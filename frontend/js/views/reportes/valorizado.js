import { ReportesAPI } from "../../api/inventario_api.js";
import { dinero, escapar, notificar, pintarTarjetas, graficoBarras, descargarArchivo } from "../../utils/helpers.js";

let porCategoria = [];
let topProductos = [];
let grafico = null;

export async function init() {
    ["f-buscar", "f-orden", "f-direccion", "f-min", "f-top"].forEach((id) =>
        document.getElementById(id).addEventListener("input", aplicar));
    document.getElementById("btn-excel").addEventListener("click", () =>
        descargarArchivo(ReportesAPI.urlExportar("valorizado", "excel")));
    document.getElementById("btn-pdf").addEventListener("click", () =>
        descargarArchivo(ReportesAPI.urlExportar("valorizado", "pdf")));

    try {
        const datos = await ReportesAPI.analisis();
        if (!document.getElementById("tabla-categorias")) return;
        porCategoria = datos.por_categoria;
        topProductos = datos.top_productos;
        pintarResumen(datos.totales);
        dibujarGrafico();
        aplicar();
    } catch (e) {
        notificar(e.message, "danger");
    }
}

function dibujarGrafico() {
    const orden = [...porCategoria].sort((a, b) => b.valor - a.valor).slice(0, 8);
    grafico = graficoBarras("grafico-valorizado",
        orden.map((c) => c.categoria), orden.map((c) => c.valor), "Valor", grafico);
}

function pintarResumen(t) {
    pintarTarjetas("tarjetas-valorizado", [
        { icono: "bi-cash-stack", valor: dinero(t.valor_total || 0), label: "Valor total" },
        { icono: "bi-stack", valor: t.unidades || 0, label: "Unidades" },
        { icono: "bi-boxes", valor: t.productos || 0, label: "Productos" },
        { icono: "bi-tags", valor: porCategoria.length, label: "Categorías" },
        { icono: "bi-trophy", valor: topProductos.length ? dinero(topProductos[0].valor_total) : "—", label: "Mayor producto" },
    ]);
}

function aplicar() {
    const buscar = document.getElementById("f-buscar").value.toLowerCase();
    const orden = document.getElementById("f-orden").value;
    const dir = document.getElementById("f-direccion").value;
    const min = Number(document.getElementById("f-min").value) || 0;
    const top = Number(document.getElementById("f-top").value) || 5;

    let filas = porCategoria
        .filter((f) => f.categoria.toLowerCase().includes(buscar) && f.valor >= min)
        .sort((a, b) => dir === "asc" ? a[orden] - b[orden] : b[orden] - a[orden]);

    renderCategorias(filas);
    renderTop(topProductos.slice(0, top));
}

function renderCategorias(filas) {
    const cuerpo = document.getElementById("tabla-categorias");
    if (!filas.length) {
        cuerpo.innerHTML = '<tr><td colspan="5" class="text-center text-muted py-4">Sin resultados.</td></tr>';
        return;
    }
    cuerpo.innerHTML = filas.map((f) => `
    <tr>
      <td class="fw-medium">${escapar(f.categoria)}</td>
      <td class="text-end">${f.productos}</td>
      <td class="text-end">${f.unidades}</td>
      <td class="text-end">${dinero(f.precio_promedio)}</td>
      <td class="text-end fw-medium">${dinero(f.valor)}</td>
    </tr>`).join("");
}

function renderTop(filas) {
    document.getElementById("tabla-top").innerHTML = filas.map((f, i) => `
    <tr>
      <td>${i + 1}</td>
      <td class="fw-medium">${escapar(f.nombre)}</td>
      <td class="text-end fw-medium">${dinero(f.valor_total)}</td>
    </tr>`).join("");
}
