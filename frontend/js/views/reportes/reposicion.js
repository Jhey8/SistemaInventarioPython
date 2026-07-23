import { ReportesAPI } from "../../api/inventario_api.js";
import { escapar, notificar, pintarTarjetas, graficoBarras, descargarArchivo } from "../../utils/helpers.js";

let filas = [];
let grafico = null;

export async function init() {

    document.getElementById("f-ventana").addEventListener("change", cargar);
    document.getElementById("f-cobertura").addEventListener("change", cargar);

    ["f-buscar", "f-categoria", "f-solo"].forEach((id) =>
        document.getElementById(id).addEventListener("input", aplicar));
    document.getElementById("btn-excel").addEventListener("click", () =>
        descargarArchivo(ReportesAPI.urlExportar("reposicion", "excel", parametros())));
    document.getElementById("btn-pdf").addEventListener("click", () =>
        descargarArchivo(ReportesAPI.urlExportar("reposicion", "pdf", parametros())));

    await cargar();
}

function parametros() {
    return {
        dias: document.getElementById("f-ventana").value,
        cobertura: document.getElementById("f-cobertura").value,
    };
}

async function cargar() {
    try {
        const datos = await ReportesAPI.reposicion(parametros());
        if (!document.getElementById("tabla-reposicion")) return;
        filas = datos.productos;
        pintarResumen(datos.resumen);
        llenarCategorias();
        dibujarGrafico();
        aplicar();
    } catch (e) {
        notificar(e.message, "danger");
    }
}

function pintarResumen(r) {
    pintarTarjetas("tarjetas-reposicion", [
        { icono: "bi-boxes", valor: r.productos, label: "Productos" },
        { icono: "bi-alarm", valor: r.por_agotarse, label: "Se agotan (≤7 días)" },
        { icono: "bi-hourglass-split", valor: r.en_atencion, label: "En atención (≤15 días)" },
        { icono: "bi-moon", valor: r.sin_consumo, label: "Sin consumo" },
        { icono: "bi-cart-plus", valor: r.unidades_comprar, label: "Unidades a comprar" },
    ]);
}

function llenarCategorias() {
    const select = document.getElementById("f-categoria");
    const actual = select.value;
    const cats = [...new Set(filas.map((f) => f.categoria))].sort();
    select.innerHTML = '<option value="">Todas</option>' +
        cats.map((c) => `<option value="${escapar(c)}">${escapar(c)}</option>`).join("");
    select.value = actual;
}

function dibujarGrafico() {
    const top = filas.filter((f) => f.sugerido > 0)
        .sort((a, b) => b.sugerido - a.sugerido).slice(0, 8);
    grafico = graficoBarras("grafico-reposicion",
        top.map((f) => f.nombre), top.map((f) => f.sugerido), "Sugerido", grafico);
}

function aplicar() {
    const buscar = document.getElementById("f-buscar").value.toLowerCase();
    const categoria = document.getElementById("f-categoria").value;
    const soloSugerencia = document.getElementById("f-solo").checked;

    render(filas.filter((f) =>
        f.nombre.toLowerCase().includes(buscar) &&
        (!categoria || f.categoria === categoria) &&
        (!soloSugerencia || f.sugerido > 0)));
}

const BADGE = {
    "SIN STOCK": "text-bg-danger",
    "CRÍTICO": "text-bg-danger",
    "ATENCIÓN": "text-bg-warning",
    "SIN CONSUMO": "text-bg-light",
    "OK": "text-bg-success",
};

function render(lista) {
    const cuerpo = document.getElementById("tabla-reposicion");
    if (!lista.length) {
        cuerpo.innerHTML = '<tr><td colspan="7" class="text-center text-muted py-4">Sin resultados.</td></tr>';
        return;
    }
    cuerpo.innerHTML = lista.map((f) => `
    <tr>
      <td class="fw-medium">${escapar(f.nombre)}</td>
      <td><span class="badge rounded-pill text-bg-light">${escapar(f.categoria)}</span></td>
      <td class="text-end">${f.cantidad}</td>
      <td class="text-end">${f.consumo_diario}</td>
      <td class="text-end">${f.dias_restantes === null ? "—" : f.dias_restantes + " d"}</td>
      <td class="text-end fw-semibold">${f.sugerido > 0 ? f.sugerido : "—"}</td>
      <td class="text-center"><span class="badge ${BADGE[f.urgencia] || "text-bg-light"}">${escapar(f.urgencia)}</span></td>
    </tr>`).join("");
}
