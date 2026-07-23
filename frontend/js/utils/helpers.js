export function dinero(n) {
    return "S/ " + Number(n || 0).toLocaleString("es-PE", { minimumFractionDigits: 2 });
}

export function fechaHora(valor) {
    if (!valor) return "—";
    const f = new Date(valor);
    if (isNaN(f)) return valor;
    return f.toLocaleString("es-PE", {
        day: "2-digit", month: "2-digit", year: "numeric",
        hour: "2-digit", minute: "2-digit",
    });
}

export function escapar(texto) {
    return String(texto ?? "").replace(/[&<>"']/g, (c) => ({
        "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;",
    }[c]));
}

export function tarjetas(lista) {
    return `<div class="row g-3 mb-4">` + lista.map((t) => `
        <div class="col-12 col-sm-6 col-lg">
            <div class="card tarjeta-stat h-100">
                <div class="stat-cab">
                    <span class="stat-label">${escapar(t.label)}</span>
                    <i class="bi ${t.icono} stat-ic"></i>
                </div>
                <div class="stat-valor">${t.valor}</div>
            </div>
        </div>`).join("") + `</div>`;
}

export function pintarTarjetas(idContenedor, lista) {
    const cont = document.getElementById(idContenedor);
    if (cont) cont.innerHTML = tarjetas(lista);
}

export function descargarArchivo(url) {
    const enlace = document.createElement("a");
    enlace.href = url;
    document.body.appendChild(enlace);
    enlace.click();
    enlace.remove();
}

export const PALETA_GRAFICO =
    ["#2f6fed", "#6f9bf2", "#22456e", "#8a8a8d", "#a9b8cf", "#4f7a8a", "#b0c4de"];

export function graficoBarras(idCanvas, etiquetas, valores, titulo, previo) {
    if (previo) previo.destroy();
    const ctx = document.getElementById(idCanvas);
    if (!ctx) return null;
    return new Chart(ctx, {
        type: "bar",
        data: { labels: etiquetas, datasets: [{ label: titulo, data: valores, backgroundColor: "#2f6fed", borderRadius: 4 }] },
        options: { plugins: { legend: { display: false } }, scales: { y: { beginAtZero: true } } },
    });
}

export function graficoDona(idCanvas, etiquetas, valores, previo) {
    if (previo) previo.destroy();
    const ctx = document.getElementById(idCanvas);
    if (!ctx) return null;
    return new Chart(ctx, {
        type: "doughnut",
        data: { labels: etiquetas, datasets: [{ data: valores, backgroundColor: PALETA_GRAFICO, borderColor: "#fff", borderWidth: 2 }] },
        options: { plugins: { legend: { position: "bottom" } }, cutout: "58%" },
    });
}

export function badgeActivo(estado) {
    return Number(estado) === 1
        ? '<span class="badge text-bg-success">Activo</span>'
        : '<span class="badge text-bg-secondary">Inactivo</span>';
}

export function botonesAccion(id, estado) {
    const activo = Number(estado) === 1;
    const toggle = activo
        ? `<button class="btn btn-sm btn-outline-warning" data-accion="desactivar" data-id="${id}" title="Desactivar"><i class="bi bi-slash-circle"></i></button>`
        : `<button class="btn btn-sm btn-outline-success" data-accion="activar" data-id="${id}" title="Activar"><i class="bi bi-check-circle"></i></button>`;
    return `
        <button class="btn btn-sm btn-outline-primary" data-accion="editar" data-id="${id}" title="Editar"><i class="bi bi-pencil"></i></button>
        ${toggle}
        <button class="btn btn-sm btn-outline-danger" data-accion="eliminar" data-id="${id}" title="Eliminar"><i class="bi bi-trash"></i></button>`;
}

export async function confirmar(titulo, texto = "", peligro = false) {
    const resultado = await Swal.fire({
        title: titulo,
        text: texto,
        icon: "warning",
        showCancelButton: true,
        confirmButtonText: peligro ? "Sí, eliminar" : "Sí, continuar",
        cancelButtonText: "Cancelar",
        confirmButtonColor: peligro ? "#c0392b" : "#2f6fed",
        cancelButtonColor: "#8a8a8d",
        reverseButtons: true,
    });
    return resultado.isConfirmed;
}

export function notificar(mensaje, tipo = "success") {
    const contenedor = document.getElementById("contenedor-toasts");
    const id = "t" + Date.now();
    contenedor.insertAdjacentHTML("beforeend", `
        <div id="${id}" class="toast align-items-center text-bg-${tipo} border-0" role="alert">
        <div class="d-flex">
            <div class="toast-body">${escapar(mensaje)}</div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
        </div>
        </div>`);
    new bootstrap.Toast(document.getElementById(id), { delay: 3500 }).show();
}
