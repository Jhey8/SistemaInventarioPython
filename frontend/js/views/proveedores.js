import { ProveedoresAPI } from "../api/inventario_api.js";
import { escapar, notificar, pintarTarjetas, badgeActivo, botonesAccion, confirmar } from "../utils/helpers.js";
import * as v from "../utils/validaciones.js";

let proveedores = [];
let modalProveedor = null;

export async function init() {
    modalProveedor = new bootstrap.Modal("#modal-proveedor");

    document.getElementById("btn-nuevo-prov").addEventListener("click", abrirNuevo);
    document.getElementById("btn-guardar-prov").addEventListener("click", guardar);
    document.getElementById("buscador-prov").addEventListener("input", filtrar);
    document.getElementById("form-proveedor").addEventListener("submit", (e) => {
        e.preventDefault();
        guardar();
    });
    v.filtrarEntrada(document.getElementById("prov-ruc"), "digitos");
    v.filtrarEntrada(document.getElementById("prov-telefono"), "digitos");
    v.filtrarEntrada(document.getElementById("prov-representante"), "texto");

    document.getElementById("cuerpo-proveedores").addEventListener("click", (e) => {
        const boton = e.target.closest("button[data-accion]");
        if (!boton) return;
        const id = Number(boton.dataset.id);
        if (boton.dataset.accion === "editar") abrirEditar(id);
        else if (boton.dataset.accion === "desactivar") cambiarEstado(id, 0);
        else if (boton.dataset.accion === "activar") cambiarEstado(id, 1);
        else if (boton.dataset.accion === "eliminar") eliminar(id);
    });

    await cargar();
}

async function cargar() {
    try {
        proveedores = await ProveedoresAPI.listar();
        if (!document.getElementById("cuerpo-proveedores")) return;
        render(proveedores);
        pintarResumen();
    } catch (e) {
        notificar(e.message, "danger");
    }
}

function pintarResumen() {
    const activos = proveedores.filter((p) => Number(p.estado) === 1).length;
    const conRuc = proveedores.filter((p) => p.ruc).length;
    const conCorreo = proveedores.filter((p) => p.correo).length;
    pintarTarjetas("tarjetas-proveedores", [
        { icono: "bi-truck", valor: proveedores.length, label: "Proveedores" },
        { icono: "bi-check-circle", valor: activos, label: "Activos" },
        { icono: "bi-slash-circle", valor: proveedores.length - activos, label: "Inactivos" },
        { icono: "bi-card-text", valor: conRuc, label: "Con RUC" },
        { icono: "bi-envelope", valor: conCorreo, label: "Con correo" },
    ]);
}

function render(lista) {
    const cuerpo = document.getElementById("cuerpo-proveedores");
    if (!lista.length) {
        cuerpo.innerHTML =
            '<tr><td colspan="8" class="text-center text-muted py-4">No hay proveedores registrados.</td></tr>';
        return;
    }
    cuerpo.innerHTML = lista.map((p) => `
    <tr class="${p.estado === 0 ? "text-muted" : ""}">
      <td class="text-muted">${p.id_proveedor}</td>
      <td class="fw-medium">${escapar(p.nombre_proveedor)}</td>
      <td>${escapar(p.ruc || "—")}</td>
      <td>${escapar(p.representante || "—")}</td>
      <td>${escapar(p.telefono || "—")}</td>
      <td class="small">${escapar(p.correo || "—")}</td>
      <td class="text-center">${badgeActivo(p.estado)}</td>
      <td class="text-end text-nowrap">${botonesAccion(p.id_proveedor, p.estado)}</td>
    </tr>`).join("");
}

function filtrar() {
    const texto = document.getElementById("buscador-prov").value.toLowerCase();
    render(proveedores.filter((p) =>
        p.nombre_proveedor.toLowerCase().includes(texto) ||
        (p.ruc || "").includes(texto)));
}

function abrirNuevo() {
    document.getElementById("form-proveedor").reset();
    document.getElementById("prov-id").value = "";
    document.getElementById("titulo-prov").textContent = "Nuevo proveedor";
    document.getElementById("error-prov").classList.add("d-none");
    modalProveedor.show();
}

function abrirEditar(id) {
    const p = proveedores.find((x) => x.id_proveedor === id);
    document.getElementById("prov-id").value = p.id_proveedor;
    document.getElementById("prov-nombre").value = p.nombre_proveedor;
    document.getElementById("prov-ruc").value = p.ruc || "";
    document.getElementById("prov-representante").value = p.representante || "";
    document.getElementById("prov-telefono").value = p.telefono || "";
    document.getElementById("prov-correo").value = p.correo || "";
    document.getElementById("prov-direccion").value = p.direccion || "";
    document.getElementById("titulo-prov").textContent = "Editar proveedor";
    document.getElementById("error-prov").classList.add("d-none");
    modalProveedor.show();
}

async function guardar() {
    const id = document.getElementById("prov-id").value;
    const nombre = document.getElementById("prov-nombre").value;
    const ruc = document.getElementById("prov-ruc").value;
    const representante = document.getElementById("prov-representante").value;
    const telefono = document.getElementById("prov-telefono").value;
    const correoValor = document.getElementById("prov-correo").value;

    const error = v.primerError([
        v.requerido(nombre, "Nombre"),
        v.digitos(ruc, "RUC", { longitud: 11 }),
        v.soloTexto(representante, "Representante", { obligatorio: false }),
        v.digitos(telefono, "Teléfono"),
        v.correo(correoValor),
    ]);
    if (error) return mostrarError(error);

    const datos = {
        nombre_proveedor: nombre.trim(),
        ruc: ruc.trim() || null,
        representante: representante.trim() || null,
        telefono: telefono.trim() || null,
        correo: correoValor.trim() || null,
        direccion: document.getElementById("prov-direccion").value.trim() || null,
    };
    try {
        if (id) {
            await ProveedoresAPI.actualizar(Number(id), datos);
            notificar("Proveedor actualizado.");
        } else {
            await ProveedoresAPI.crear(datos);
            notificar("Proveedor creado.");
        }
        modalProveedor.hide();
        await cargar();
    } catch (e) {
        mostrarError(e.message);
    }
}

function mostrarError(mensaje) {
    const alerta = document.getElementById("error-prov");
    alerta.textContent = mensaje;
    alerta.classList.remove("d-none");
}

async function cambiarEstado(id, estado) {
    const p = proveedores.find((x) => x.id_proveedor === id);
    const accion = estado === 1 ? "Activar" : "Desactivar";
    if (!(await confirmar(`¿${accion} al proveedor "${p.nombre_proveedor}"?`))) return;
    try {
        await ProveedoresAPI.cambiarEstado(id, estado);
        notificar(`Proveedor ${estado === 1 ? "activado" : "desactivado"}.`);
        await cargar();
    } catch (e) {
        notificar(e.message, "danger");
    }
}

async function eliminar(id) {
    const p = proveedores.find((x) => x.id_proveedor === id);
    if (!(await confirmar(`¿Eliminar al proveedor "${p.nombre_proveedor}"?`, "Dejará de aparecer en el sistema.", true))) return;
    try {
        await ProveedoresAPI.eliminar(id);
        notificar("Proveedor eliminado.");
        await cargar();
    } catch (e) {
        notificar(e.message, "danger");
    }
}
