import { ReportesAPI, InventarioAPI, ProveedoresAPI } from "../../api/inventario_api.js";
import { dinero, fechaHora, escapar, notificar, pintarTarjetas, graficoDona, descargarArchivo } from "../../utils/helpers.js";

let grafico = null;

export async function init() {
    document.getElementById("btn-aplicar").addEventListener("click", cargar);
    document.getElementById("btn-limpiar").addEventListener("click", limpiar);
    document.getElementById("btn-excel").addEventListener("click", () =>
        descargarArchivo(ReportesAPI.urlExportar("movimientos", "excel", filtros())));
    document.getElementById("btn-pdf").addEventListener("click", () =>
        descargarArchivo(ReportesAPI.urlExportar("movimientos", "pdf", filtros())));

    await Promise.all([llenarProductos(), llenarProveedores()]);
    await cargar();
}

function filtros() {
    return {
        producto: document.getElementById("f-producto").value,
        tipo: document.getElementById("f-tipo").value,
        proveedor: document.getElementById("f-proveedor").value,
        desde: document.getElementById("f-desde").value,
        hasta: document.getElementById("f-hasta").value,
    };
}

async function cargar() {
    try {
        const datos = await ReportesAPI.movimientos(filtros());
        if (!document.getElementById("tabla-movimientos")) return;
        pintarResumen(datos.resumen);
        grafico = graficoDona("grafico-movimientos",
            ["Entradas", "Salidas", "Ajustes"],
            [datos.resumen.entradas, datos.resumen.salidas, datos.resumen.ajustes], grafico);
        render(datos.movimientos);
    } catch (e) {
        notificar(e.message, "danger");
    }
}

function limpiar() {
    ["f-producto", "f-tipo", "f-proveedor", "f-desde", "f-hasta"].forEach((id) =>
        (document.getElementById(id).value = ""));
    cargar();
}

function pintarResumen(r) {
    pintarTarjetas("tarjetas-movimientos", [
        { icono: "bi-clock-history", valor: r.total, label: "Movimientos" },
        { icono: "bi-box-arrow-in-down", valor: r.entradas, label: `Entradas (${r.unidades_entrada} u.)` },
        { icono: "bi-box-arrow-up", valor: r.salidas, label: `Salidas (${r.unidades_salida} u.)` },
        { icono: "bi-sliders", valor: r.ajustes, label: "Ajustes" },
        { icono: "bi-cash-stack", valor: dinero(r.valor_comprado), label: "Valor comprado" },
    ]);
}

function render(movimientos) {
    const cuerpo = document.getElementById("tabla-movimientos");
    if (!movimientos.length) {
        cuerpo.innerHTML =
            '<tr><td colspan="9" class="text-center text-muted py-4">Sin movimientos para los filtros seleccionados.</td></tr>';
        return;
    }
    const badge = { ENTRADA: "badge-entrada", SALIDA: "badge-salida", AJUSTE: "badge-ajuste" };
    const signo = { ENTRADA: "+", SALIDA: "−", AJUSTE: "" };
    cuerpo.innerHTML = movimientos.map((m) => `
    <tr>
      <td class="text-nowrap small">${fechaHora(m.fecha)}</td>
      <td class="fw-medium">${escapar(m.producto)}</td>
      <td class="text-center"><span class="badge ${badge[m.tipo_movimiento] || "text-bg-light"}">${escapar(m.tipo_movimiento)}</span></td>
      <td class="small">${escapar(m.motivo)}</td>
      <td class="text-end fw-medium">${signo[m.tipo_movimiento] || ""}${m.cantidad}</td>
      <td class="text-center text-nowrap small text-muted">${m.stock_anterior} → <strong>${m.stock_nuevo}</strong></td>
      <td class="small">${escapar(m.proveedor || "—")}</td>
      <td class="text-end">${m.subtotal != null ? dinero(m.subtotal) : "—"}</td>
      <td class="small text-muted">${escapar(m.usuario || "—")}</td>
    </tr>`).join("");
}

async function llenarProductos() {
    const select = document.getElementById("f-producto");
    try {
        const productos = await InventarioAPI.opciones();
        select.insertAdjacentHTML("beforeend", productos.map((p) =>
            `<option value="${p.id}">${escapar(p.nombre)}</option>`).join(""));
    } catch {  }
}

async function llenarProveedores() {
    const select = document.getElementById("f-proveedor");
    try {
        const proveedores = await ProveedoresAPI.opciones();
        select.insertAdjacentHTML("beforeend", proveedores.map((p) =>
            `<option value="${p.id_proveedor}">${escapar(p.nombre_proveedor)}</option>`).join(""));
    } catch {  }
}
