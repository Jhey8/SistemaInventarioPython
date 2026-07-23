import { MovimientosAPI, InventarioAPI, ProveedoresAPI } from "../api/inventario_api.js";
import { dinero, fechaHora, escapar, notificar, pintarTarjetas } from "../utils/helpers.js";
import * as v from "../utils/validaciones.js";

let productos = [];
let modalMovimiento = null;
let modalHistorial = null;

const MOTIVOS = {
    ENTRADA: ["COMPRA", "DEVOLUCIÓN", "AJUSTE INICIAL"],
    SALIDA: ["VENTA", "MERMA", "DEVOLUCIÓN"],
    AJUSTE: ["CONTEO FÍSICO", "CORRECCIÓN"],
};

export async function init() {
    modalMovimiento = new bootstrap.Modal("#modal-movimiento");
    modalHistorial = new bootstrap.Modal("#modal-historial");

    document.getElementById("btn-guardar-mov").addEventListener("click", guardar);
    document.getElementById("form-movimiento").addEventListener("submit", (e) => {
        e.preventDefault();
        guardar();
    });
    document.getElementById("buscador-inv").addEventListener("input", filtrar);
    document.querySelectorAll('input[name="tipo"]').forEach((radio) =>
        radio.addEventListener("change", alCambiarTipo));
    document.getElementById("mov-motivo").addEventListener("change", actualizarBloques);

    document.getElementById("cuerpo-inventario").addEventListener("click", (e) => {
        const boton = e.target.closest("button[data-accion]");
        if (!boton) return;
        const id = Number(boton.dataset.id);
        if (boton.dataset.accion === "movimiento") abrirMovimiento(id);
        else if (boton.dataset.accion === "historial") abrirHistorial(id);
    });

    await llenarProveedores();
    await cargar();
}

async function cargar() {
    try {
        productos = await InventarioAPI.opciones();
        if (!document.getElementById("cuerpo-inventario")) return;
        render(productos);
        pintarResumen();
    } catch (e) {
        notificar(e.message, "danger");
    }
}

function pintarResumen() {
    const unidades = productos.reduce((a, p) => a + p.cantidad, 0);
    const valor = productos.reduce((a, p) => a + (p.valor_total || 0), 0);
    const bajo = productos.filter((p) => p.necesita_reposicion).length;
    const sinStock = productos.filter((p) => p.cantidad === 0).length;
    pintarTarjetas("tarjetas-inventario", [
        { icono: "bi-boxes", valor: productos.length, label: "Productos" },
        { icono: "bi-stack", valor: unidades, label: "Unidades en stock" },
        { icono: "bi-exclamation-triangle", valor: bajo, label: "Bajo stock" },
        { icono: "bi-x-octagon", valor: sinStock, label: "Sin stock" },
        { icono: "bi-cash-stack", valor: dinero(valor), label: "Valor total" },
    ]);
}

function render(lista) {
    const cuerpo = document.getElementById("cuerpo-inventario");
    if (!lista.length) {
        cuerpo.innerHTML =
            '<tr><td colspan="7" class="text-center text-muted py-4">No hay productos registrados.</td></tr>';
        return;
    }
    cuerpo.innerHTML = lista.map((p) => `
    <tr class="${p.necesita_reposicion ? "fila-alerta" : ""}">
      <td class="text-muted">${p.id}</td>
      <td class="fw-medium">${escapar(p.nombre)}</td>
      <td><span class="badge rounded-pill text-bg-light">${escapar(p.categoria)}</span></td>
      <td class="text-end fw-semibold">${p.cantidad}</td>
      <td class="text-end text-muted">${p.stock_minimo}</td>
      <td class="text-center">${p.necesita_reposicion
            ? '<span class="badge text-bg-warning">Bajo stock</span>'
            : '<span class="badge text-bg-success">OK</span>'}</td>
      <td class="text-end text-nowrap">
        <button class="btn btn-sm btn-marca" data-accion="movimiento" data-id="${p.id}">
          <i class="bi bi-arrow-left-right me-1"></i>Movimiento</button>
        <button class="btn btn-sm btn-outline-primary" data-accion="historial" data-id="${p.id}" title="Historial">
          <i class="bi bi-clock-history"></i></button>
      </td>
    </tr>`).join("");
}

function filtrar() {
    const t = document.getElementById("buscador-inv").value.toLowerCase();
    render(productos.filter((p) =>
        p.nombre.toLowerCase().includes(t) || (p.categoria || "").toLowerCase().includes(t)));
}

function tipoSeleccionado() {
    return document.querySelector('input[name="tipo"]:checked').value;
}

function motivoSeleccionado() {
    return document.getElementById("mov-motivo").value;
}

function esSalidaVenta() {
    return tipoSeleccionado() === "SALIDA" && motivoSeleccionado() === "VENTA";
}

function alCambiarTipo() {
    const tipo = tipoSeleccionado();
    document.getElementById("label-cantidad").textContent =
        tipo === "AJUSTE" ? "Nuevo stock (conteo real)" : "Cantidad";
    document.getElementById("mov-cantidad").min = tipo === "AJUSTE" ? 0 : 1;
    llenarMotivos(tipo);
    actualizarBloques();
}

function actualizarBloques() {
    const tipo = tipoSeleccionado();
    const entrada = tipo === "ENTRADA";
    const conDocumento = entrada || esSalidaVenta();

    document.getElementById("bloque-entrada").classList.toggle("d-none", !entrada);
    document.getElementById("bloque-documento").classList.toggle("d-none", !conDocumento);
    document.getElementById("label-documento").textContent =
        esSalidaVenta() ? "N° documento de venta" : "N° documento";
}

function llenarMotivos(tipo) {
    document.getElementById("mov-motivo").innerHTML =
        MOTIVOS[tipo].map((m) => `<option value="${m}">${m}</option>`).join("");
}

function abrirMovimiento(id) {
    const p = productos.find((x) => x.id === id);
    document.getElementById("mov-id-producto").value = p.id;
    document.getElementById("mov-nombre-producto").textContent = p.nombre;
    document.getElementById("mov-stock-actual").textContent = p.cantidad;
    document.getElementById("form-movimiento").reset();
    document.getElementById("tipo-entrada").checked = true;
    document.getElementById("mov-cantidad").value = 1;
    document.getElementById("error-mov").classList.add("d-none");
    alCambiarTipo();
    modalMovimiento.show();
}

async function guardar() {
    const tipo = tipoSeleccionado();
    const cantidad = document.getElementById("mov-cantidad").value;
    const precio = document.getElementById("mov-precio").value;
    const documento = document.getElementById("mov-documento").value.trim();

    const errores = [
        v.noNegativo(cantidad, "Cantidad"),
        tipo !== "AJUSTE" && Number(cantidad) < 1 ? "La cantidad debe ser mayor que cero." : null,
    ];
    if (tipo === "ENTRADA") {
        errores.push(document.getElementById("mov-proveedor").value ? null : "Debes indicar el proveedor.");
        errores.push(precio !== "" ? v.noNegativo(precio, "Precio compra") : "El precio de compra es obligatorio.");
        errores.push(documento ? null : "El N° de documento es obligatorio.");
    }
    if (esSalidaVenta()) {
        errores.push(documento ? null : "El N° de documento de venta es obligatorio.");
    }
    const error = v.primerError(errores);
    if (error) return mostrarError(error);

    const datos = {
        id_producto: Number(document.getElementById("mov-id-producto").value),
        tipo_movimiento: tipo,
        cantidad: Number(cantidad),
        motivo: document.getElementById("mov-motivo").value,
        observacion: document.getElementById("mov-observacion").value.trim() || null,
    };
    if (tipo === "ENTRADA") {
        datos.id_proveedor = Number(document.getElementById("mov-proveedor").value) || null;
        datos.numero_documento = documento;
        datos.precio_compra = Number(precio);
    } else if (esSalidaVenta()) {
        datos.numero_documento = documento;
    }
    try {
        await MovimientosAPI.registrar(datos);
        notificar("Movimiento registrado.");
        modalMovimiento.hide();
        await cargar();
    } catch (e) {
        mostrarError(e.message);
    }
}

function mostrarError(mensaje) {
    const alerta = document.getElementById("error-mov");
    alerta.textContent = mensaje;
    alerta.classList.remove("d-none");
}

async function abrirHistorial(id) {
    const p = productos.find((x) => x.id === id);
    document.getElementById("hist-nombre-producto").textContent = p.nombre;
    document.getElementById("cuerpo-historial").innerHTML =
        '<tr><td colspan="7" class="text-center text-muted py-3">Cargando…</td></tr>';
    modalHistorial.show();
    try {
        const movimientos = await MovimientosAPI.listar({ producto: id });
        renderHistorial(movimientos);
    } catch (e) {
        notificar(e.message, "danger");
    }
}

function renderHistorial(movimientos) {
    const cuerpo = document.getElementById("cuerpo-historial");
    if (!movimientos.length) {
        cuerpo.innerHTML =
            '<tr><td colspan="7" class="text-center text-muted py-3">Este producto aún no tiene movimientos.</td></tr>';
        return;
    }
    const badge = { ENTRADA: "badge-entrada", SALIDA: "badge-salida", AJUSTE: "badge-ajuste" };
    const signo = { ENTRADA: "+", SALIDA: "−", AJUSTE: "" };
    cuerpo.innerHTML = movimientos.map((m) => `
    <tr>
      <td class="text-nowrap small">${fechaHora(m.fecha)}</td>
      <td class="text-center"><span class="badge ${badge[m.tipo_movimiento] || "text-bg-light"}">${escapar(m.tipo_movimiento)}</span></td>
      <td class="small">${escapar(m.motivo)}</td>
      <td class="text-end fw-medium">${signo[m.tipo_movimiento] || ""}${m.cantidad}</td>
      <td class="text-center text-nowrap small text-muted">${m.stock_anterior} → <strong>${m.stock_nuevo}</strong></td>
      <td class="small">${escapar(m.proveedor || "—")}</td>
      <td class="small text-muted">${escapar(m.usuario || "—")}</td>
    </tr>`).join("");
}

async function llenarProveedores() {
    const select = document.getElementById("mov-proveedor");
    try {
        const proveedores = await ProveedoresAPI.opciones();
        select.innerHTML = proveedores.map((p) =>
            `<option value="${p.id_proveedor}">${escapar(p.nombre_proveedor)}</option>`).join("");
    } catch {
        select.innerHTML = "";
    }
}
