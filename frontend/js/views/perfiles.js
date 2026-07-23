import { PerfilesAPI, ModulosAPI } from "../api/inventario_api.js";
import { escapar, notificar, pintarTarjetas, badgeActivo, botonesAccion, confirmar } from "../utils/helpers.js";
import * as v from "../utils/validaciones.js";

let perfiles = [];
let modulos = [];
let modalPerfil = null;

export async function init() {
    modalPerfil = new bootstrap.Modal("#modal-perfil");

    document.getElementById("btn-nuevo-perfil").addEventListener("click", abrirNuevo);
    document.getElementById("btn-guardar-perfil").addEventListener("click", guardar);
    document.getElementById("form-perfil").addEventListener("submit", (e) => {
        e.preventDefault();
        guardar();
    });
    v.filtrarEntrada(document.getElementById("perfil-nombre"), "texto");

    document.getElementById("cuerpo-perfiles").addEventListener("click", (e) => {
        const boton = e.target.closest("button[data-accion]");
        if (!boton) return;
        const id = Number(boton.dataset.id);
        if (boton.dataset.accion === "editar") abrirEditar(id);
        else if (boton.dataset.accion === "desactivar") cambiarEstado(id, 0);
        else if (boton.dataset.accion === "activar") cambiarEstado(id, 1);
        else if (boton.dataset.accion === "eliminar") eliminar(id);
    });

    await Promise.all([cargarModulos(), cargar()]);
    pintarResumen();
}

async function cargar() {
    try {
        perfiles = await PerfilesAPI.listar();
        if (!document.getElementById("cuerpo-perfiles")) return;
        render(perfiles);
        pintarResumen();
    } catch (e) {
        notificar(e.message, "danger");
    }
}

function pintarResumen() {
    const totalAsignados = perfiles.reduce((a, p) => a + p.modulos.length, 0);
    const promedio = perfiles.length ? (totalAsignados / perfiles.length).toFixed(1) : 0;
    const maximo = perfiles.reduce((a, p) => Math.max(a, p.modulos.length), 0);
    const conDescripcion = perfiles.filter((p) => p.descripcion).length;
    pintarTarjetas("tarjetas-perfiles", [
        { icono: "bi-shield-lock", valor: perfiles.length, label: "Perfiles" },
        { icono: "bi-grid", valor: modulos.length, label: "Módulos disponibles" },
        { icono: "bi-bar-chart", valor: promedio, label: "Módulos por perfil" },
        { icono: "bi-arrow-up-circle", valor: maximo, label: "Máx. módulos" },
        { icono: "bi-card-text", valor: conDescripcion, label: "Con descripción" },
    ]);
}

async function cargarModulos() {
    try {
        modulos = await ModulosAPI.todos();
    } catch {
        modulos = [];
    }
}

function render(lista) {
    const cuerpo = document.getElementById("cuerpo-perfiles");
    if (!lista.length) {
        cuerpo.innerHTML =
            '<tr><td colspan="6" class="text-center text-muted py-4">No hay perfiles registrados.</td></tr>';
        return;
    }
    cuerpo.innerHTML = lista.map((p) => `
    <tr class="${p.estado === 0 ? "text-muted" : ""}">
      <td class="text-muted">${p.id_perfil}</td>
      <td class="fw-medium">${escapar(p.nombre)}</td>
      <td class="text-muted">${escapar(p.descripcion || "—")}</td>
      <td class="text-center"><span class="badge text-bg-light">${p.modulos.length} módulo(s)</span></td>
      <td class="text-center">${badgeActivo(p.estado)}</td>
      <td class="text-end text-nowrap">${botonesAccion(p.id_perfil, p.estado)}</td>
    </tr>`).join("");
}

function pintarCheckboxes(seleccionados = []) {
    document.getElementById("lista-modulos").innerHTML = modulos.map((m) => `
    <div class="col">
      <div class="form-check">
        <input class="form-check-input" type="checkbox" value="${m.id_modulo}"
               id="mod-${m.id_modulo}" ${seleccionados.includes(m.id_modulo) ? "checked" : ""}>
        <label class="form-check-label" for="mod-${m.id_modulo}">
          <i class="bi ${escapar(m.icono)} me-1"></i>${escapar(m.nombre)}
        </label>
      </div>
    </div>`).join("");
}

function modulosSeleccionados() {
    return [...document.querySelectorAll("#lista-modulos input:checked")]
        .map((c) => Number(c.value));
}

function abrirNuevo() {
    document.getElementById("form-perfil").reset();
    document.getElementById("perfil-id").value = "";
    document.getElementById("titulo-perfil").textContent = "Nuevo perfil";
    document.getElementById("error-perfil").classList.add("d-none");
    pintarCheckboxes([]);
    modalPerfil.show();
}

function abrirEditar(id) {
    const p = perfiles.find((x) => x.id_perfil === id);
    document.getElementById("perfil-id").value = p.id_perfil;
    document.getElementById("perfil-nombre").value = p.nombre;
    document.getElementById("perfil-descripcion").value = p.descripcion || "";
    document.getElementById("titulo-perfil").textContent = "Editar perfil";
    document.getElementById("error-perfil").classList.add("d-none");
    pintarCheckboxes(p.modulos);
    modalPerfil.show();
}

async function guardar() {
    const nombre = document.getElementById("perfil-nombre").value;
    const seleccionados = modulosSeleccionados();

    const error = v.primerError([
        v.soloTexto(nombre, "Nombre"),
        seleccionados.length ? null : "Selecciona al menos un módulo para el perfil.",
    ]);
    if (error) return mostrarError(error);

    const datos = {
        nombre: nombre.trim(),
        descripcion: document.getElementById("perfil-descripcion").value.trim() || null,
        modulos: seleccionados,
    };
    const id = document.getElementById("perfil-id").value;
    try {
        if (id) {
            await PerfilesAPI.actualizar(Number(id), datos);
            notificar("Perfil actualizado.");
        } else {
            await PerfilesAPI.crear(datos);
            notificar("Perfil creado.");
        }
        modalPerfil.hide();
        await cargar();
    } catch (e) {
        mostrarError(e.message);
    }
}

function mostrarError(mensaje) {
    const alerta = document.getElementById("error-perfil");
    alerta.textContent = mensaje;
    alerta.classList.remove("d-none");
}

async function cambiarEstado(id, estado) {
    const p = perfiles.find((x) => x.id_perfil === id);
    const accion = estado === 1 ? "Activar" : "Desactivar";
    if (!(await confirmar(`¿${accion} el perfil "${p.nombre}"?`))) return;
    try {
        await PerfilesAPI.cambiarEstado(id, estado);
        notificar(`Perfil ${estado === 1 ? "activado" : "desactivado"}.`);
        await cargar();
    } catch (e) {
        notificar(e.message, "danger");
    }
}

async function eliminar(id) {
    const p = perfiles.find((x) => x.id_perfil === id);
    if (!(await confirmar(`¿Eliminar el perfil "${p.nombre}"?`, "Dejará de aparecer en el sistema.", true))) return;
    try {
        await PerfilesAPI.eliminar(id);
        notificar("Perfil eliminado.");
        await cargar();
    } catch (e) {
        notificar(e.message, "danger");
    }
}
