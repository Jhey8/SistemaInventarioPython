import { ReportesAPI, ProveedoresAPI } from "../../api/inventario_api.js";
import { dinero, escapar, notificar, pintarTarjetas, graficoBarras, descargarArchivo } from "../../utils/helpers.js";
import { rangoFechas } from "../../utils/validaciones.js";

let porProveedor = [];
let grafico = null;

export async function init() {
    document.getElementById("btn-aplicar").addEventListener("click", cargar);
    document.getElementById("btn-limpiar").addEventListener("click", limpiar);
    document.getElementById("f-buscar").addEventListener("input", aplicarCliente);
    document.getElementById("f-orden").addEventListener("input", aplicarCliente);
    document.getElementById("btn-excel").addEventListener("click", () =>
        descargarArchivo(ReportesAPI.urlExportar("compras", "excel", filtros())));
    document.getElementById("btn-pdf").addEventListener("click", () =>
        descargarArchivo(ReportesAPI.urlExportar("compras", "pdf", filtros())));

    await Promise.all([llenarProveedores(), cargar()]);
}

function filtros() {
    return {
        proveedor: document.getElementById("f-proveedor").value,
        desde: document.getElementById("f-desde").value,
        hasta: document.getElementById("f-hasta").value,
    };
}

async function cargar() {
    const f = filtros();
    const errorRango = rangoFechas(f.desde, f.hasta);
    if (errorRango) return notificar(errorRango, "danger");
    try {
        const datos = await ReportesAPI.compras(f);
        if (!document.getElementById("tabla-compras")) return;
        porProveedor = datos.por_proveedor;
        pintarResumen(datos.resumen);
        dibujarGrafico();
        aplicarCliente();
    } catch (e) {
        notificar(e.message, "danger");
    }
}

function limpiar() {
    ["f-proveedor", "f-desde", "f-hasta", "f-buscar"].forEach((id) =>
        (document.getElementById(id).value = ""));
    cargar();
}

function pintarResumen(r) {
    pintarTarjetas("tarjetas-compras", [
        { icono: "bi-truck", valor: porProveedor.length, label: "Proveedores" },
        { icono: "bi-box-arrow-in-down", valor: r.entradas, label: "Compras (entradas)" },
        { icono: "bi-stack", valor: r.unidades_entrada, label: "Unidades compradas" },
        { icono: "bi-cash-stack", valor: dinero(r.valor_comprado), label: "Total comprado" },
        { icono: "bi-receipt", valor: r.entradas ? dinero(r.valor_comprado / r.entradas) : dinero(0), label: "Ticket promedio" },
    ]);
}

function dibujarGrafico() {
    const top = [...porProveedor].sort((a, b) => b.total - a.total).slice(0, 8);
    grafico = graficoBarras("grafico-compras",
        top.map((p) => p.proveedor), top.map((p) => p.total), "Total comprado", grafico);
}

function aplicarCliente() {
    const buscar = document.getElementById("f-buscar").value.toLowerCase();
    const orden = document.getElementById("f-orden").value;
    const filas = porProveedor
        .filter((f) => f.proveedor.toLowerCase().includes(buscar))
        .sort((a, b) => b[orden] - a[orden]);
    render(filas);
}

function render(filas) {
    const cuerpo = document.getElementById("tabla-compras");
    if (!filas.length) {
        cuerpo.innerHTML = '<tr><td colspan="4" class="text-center text-muted py-4">Sin compras para los filtros seleccionados.</td></tr>';
        return;
    }
    cuerpo.innerHTML = filas.map((f) => `
    <tr>
      <td class="fw-medium">${escapar(f.proveedor)}</td>
      <td class="text-end">${f.movimientos}</td>
      <td class="text-end">${f.unidades}</td>
      <td class="text-end fw-medium">${dinero(f.total)}</td>
    </tr>`).join("");
}

async function llenarProveedores() {
    const select = document.getElementById("f-proveedor");
    try {
        const proveedores = await ProveedoresAPI.opciones();
        select.insertAdjacentHTML("beforeend", proveedores.map((p) =>
            `<option value="${p.id_proveedor}">${escapar(p.nombre_proveedor)}</option>`).join(""));
    } catch {  }
}
