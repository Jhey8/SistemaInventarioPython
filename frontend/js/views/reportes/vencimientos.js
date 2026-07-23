import { ReportesAPI } from "../../api/inventario_api.js";
import { fechaHora, escapar, notificar, pintarTarjetas, graficoDona, descargarArchivo } from "../../utils/helpers.js";

let filas = [];
let grafico = null;

export async function init() {
    document.getElementById("f-dias").addEventListener("change", cargar);
    ["f-estado", "f-buscar", "f-categoria"].forEach((id) =>
        document.getElementById(id).addEventListener("input", aplicar));
    document.getElementById("btn-excel").addEventListener("click", () =>
        descargarArchivo(ReportesAPI.urlExportar("vencimientos", "excel", parametros())));
    document.getElementById("btn-pdf").addEventListener("click", () =>
        descargarArchivo(ReportesAPI.urlExportar("vencimientos", "pdf", parametros())));

    await cargar();
}

function parametros() {
    return { dias: document.getElementById("f-dias").value };
}

async function cargar() {
    try {
        const datos = await ReportesAPI.vencimientos(parametros());
        if (!document.getElementById("tabla-vencimientos")) return;
        filas = datos.productos;
        pintarResumen(datos.resumen);
        llenarCategorias();
        dibujarGrafico(datos.resumen);
        aplicar();
    } catch (e) {
        notificar(e.message, "danger");
    }
}

function pintarResumen(r) {
    pintarTarjetas("tarjetas-vencimientos", [
        { icono: "bi-calendar-check", valor: r.perecederos, label: "Perecederos" },
        { icono: "bi-x-octagon", valor: r.vencidos, label: "Vencidos" },
        { icono: "bi-hourglass-split", valor: r.por_vencer, label: "Por vencer" },
        { icono: "bi-check-circle", valor: r.vigentes, label: "Vigentes" },
        { icono: "bi-box", valor: r.unidades_riesgo, label: "Unidades en riesgo" },
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

function dibujarGrafico(r) {
    grafico = graficoDona("grafico-vencimientos",
        ["Vencidos", "Por vencer", "Vigentes"],
        [r.vencidos, r.por_vencer, r.vigentes], grafico);
}

function aplicar() {
    const estado = document.getElementById("f-estado").value;
    const buscar = document.getElementById("f-buscar").value.toLowerCase();
    const categoria = document.getElementById("f-categoria").value;
    render(filas.filter((f) =>
        (!estado || f.estado_venc === estado) &&
        f.nombre.toLowerCase().includes(buscar) &&
        (!categoria || f.categoria === categoria)));
}

const BADGE = {
    "VENCIDO": "text-bg-danger",
    "POR VENCER": "text-bg-warning",
    "VIGENTE": "text-bg-success",
};

function textoDias(dias) {
    if (dias < 0) return `venció hace ${Math.abs(dias)} d`;
    if (dias === 0) return "vence hoy";
    return `en ${dias} d`;
}

function render(lista) {
    const cuerpo = document.getElementById("tabla-vencimientos");
    if (!lista.length) {
        cuerpo.innerHTML = '<tr><td colspan="6" class="text-center text-muted py-4">Sin productos perecederos para estos filtros.</td></tr>';
        return;
    }
    cuerpo.innerHTML = lista.map((f) => `
    <tr class="${f.estado_venc === "VENCIDO" ? "fila-critica" : (f.estado_venc === "POR VENCER" ? "fila-alerta" : "")}">
      <td class="fw-medium">${escapar(f.nombre)}</td>
      <td><span class="badge rounded-pill text-bg-light">${escapar(f.categoria)}</span></td>
      <td class="text-end">${f.cantidad}</td>
      <td class="text-center small">${fechaHora(f.fecha_vencimiento).split(",")[0]}</td>
      <td class="text-end small">${textoDias(f.dias_restantes)}</td>
      <td class="text-center"><span class="badge ${BADGE[f.estado_venc] || "text-bg-light"}">${escapar(f.estado_venc)}</span></td>
    </tr>`).join("");
}
