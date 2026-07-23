import { InventarioAPI } from "../api/inventario_api.js";
import { dinero, fechaHora, escapar, notificar } from "../utils/helpers.js";

let grafico = null;
let graficoMes = null;

export async function init() {
    try {
        const r = await InventarioAPI.resumen();
        if (!document.getElementById("stat-total")) return;
        document.getElementById("stat-total").textContent = r.total_productos;
        document.getElementById("stat-unidades").textContent = r.unidades_totales;
        document.getElementById("stat-valor").textContent = dinero(r.valor_total);
        document.getElementById("stat-bajo").textContent = r.productos_bajo_stock;
        document.getElementById("stat-categorias").textContent = r.categorias;
        renderAlertaVencimientos(r);
        renderGrafico(r.valor_por_categoria);
        renderGraficoMes(r.por_mes);
        renderBajoStock(r.bajo_stock_detalle);
        renderUltimos(r.ultimos_movimientos);
    } catch (e) {
        notificar(e.message, "danger");
    }
}

function renderGraficoMes(porMes) {
    const ctx = document.getElementById("grafico-mes");
    if (!ctx || !porMes) return;
    if (graficoMes) graficoMes.destroy();
    graficoMes = new Chart(ctx, {
        type: "line",
        data: {
            labels: porMes.meses,
            datasets: [
                { label: "Entradas", data: porMes.entradas, borderColor: "#2f6fed", backgroundColor: "rgba(47,111,237,.12)", tension: 0.3, fill: true },
                { label: "Salidas", data: porMes.salidas, borderColor: "#c0392b", backgroundColor: "rgba(192,57,43,.10)", tension: 0.3, fill: true },
            ],
        },
        options: { plugins: { legend: { position: "bottom" } }, scales: { y: { beginAtZero: true } } },
    });
}

function renderBajoStock(lista) {
    const cuerpo = document.getElementById("tabla-bajo-stock");
    if (!cuerpo) return;
    if (!lista || !lista.length) {
        cuerpo.innerHTML = '<tr><td colspan="4" class="text-center text-muted py-3">Todo con stock suficiente 👍</td></tr>';
        return;
    }
    cuerpo.innerHTML = lista.map((p) => `
    <tr class="fila-alerta">
      <td class="fw-medium">${escapar(p.nombre)}</td>
      <td><span class="badge rounded-pill text-bg-light">${escapar(p.categoria)}</span></td>
      <td class="text-end fw-semibold">${p.cantidad}</td>
      <td class="text-end text-muted">${p.stock_minimo}</td>
    </tr>`).join("");
}

function renderUltimos(lista) {
    const cuerpo = document.getElementById("tabla-ultimos");
    if (!cuerpo) return;
    if (!lista || !lista.length) {
        cuerpo.innerHTML = '<tr><td colspan="4" class="text-center text-muted py-3">Aún no hay movimientos.</td></tr>';
        return;
    }
    const badge = { ENTRADA: "badge-entrada", SALIDA: "badge-salida", AJUSTE: "badge-ajuste" };
    const signo = { ENTRADA: "+", SALIDA: "−", AJUSTE: "" };
    cuerpo.innerHTML = lista.map((m) => `
    <tr>
      <td class="text-nowrap small">${fechaHora(m.fecha)}</td>
      <td class="fw-medium">${escapar(m.producto)}</td>
      <td class="text-center"><span class="badge ${badge[m.tipo_movimiento] || "text-bg-light"}">${escapar(m.tipo_movimiento)}</span></td>
      <td class="text-end fw-medium">${signo[m.tipo_movimiento] || ""}${m.cantidad}</td>
    </tr>`).join("");
}

function renderAlertaVencimientos(r) {
    const cont = document.getElementById("alerta-vencimientos");
    if (!cont) return;
    const vencidos = r.vencidos || 0;
    const porVencer = r.por_vencer || 0;
    if (vencidos === 0 && porVencer === 0) {
        cont.innerHTML = "";
        return;
    }
    const partes = [];
    if (vencidos) partes.push(`<strong>${vencidos}</strong> vencido(s)`);
    if (porVencer) partes.push(`<strong>${porVencer}</strong> por vencer`);
    const tipo = vencidos ? "danger" : "warning";
    cont.innerHTML = `
        <div class="alert alert-${tipo} d-flex align-items-center justify-content-between">
            <span><i class="bi bi-calendar-x me-2"></i>Atención: ${partes.join(" y ")} en los próximos 30 días.</span>
            <a href="javascript:void(0)" data-nav="reportes/vencimientos" class="btn btn-sm btn-outline-${tipo}">Ver detalle</a>
        </div>`;
}

function renderGrafico(valorPorCategoria) {
    const ctx = document.getElementById("grafico-categorias");
    if (!ctx) return;
    const etiquetas = Object.keys(valorPorCategoria);
    const valores = Object.values(valorPorCategoria);
    const colores = ["#2f6fed", "#6f9bf2", "#8a8a8d", "#22456e", "#a9b8cf", "#4f7a8a"];

    if (grafico) grafico.destroy();
    if (etiquetas.length === 0) return;

    grafico = new Chart(ctx, {
        type: "doughnut",
        data: {
            labels: etiquetas,
            datasets: [{ data: valores, backgroundColor: colores, borderColor: "#fff", borderWidth: 2 }],
        },
        options: { plugins: { legend: { position: "bottom" } }, cutout: "58%" },
    });
}
