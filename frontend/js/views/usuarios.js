import { UsuariosAPI, PerfilesAPI } from "../api/inventario_api.js";
import { escapar, notificar, pintarTarjetas, botonesAccion, confirmar } from "../utils/helpers.js";
import * as v from "../utils/validaciones.js";

let usuarios = [];
let perfiles = [];
let modalUsuario = null;

export async function init() {
    modalUsuario = new bootstrap.Modal("#modal-usuario");

    document.getElementById("btn-nuevo-usuario").addEventListener("click", abrirNuevo);
    document.getElementById("btn-guardar-usuario").addEventListener("click", guardar);
    document.getElementById("form-usuario").addEventListener("submit", (e) => {
        e.preventDefault();
        guardar();
    });
    v.filtrarEntrada(document.getElementById("usuario-usuario"), "usuario");
    v.filtrarEntrada(document.getElementById("usuario-nombre"), "texto");

    document.getElementById("cuerpo-usuarios").addEventListener("click", (e) => {
        const boton = e.target.closest("button[data-accion]");
        if (!boton) return;
        const id = Number(boton.dataset.id);
        if (boton.dataset.accion === "editar") abrirEditar(id);
        else if (boton.dataset.accion === "desactivar") cambiarEstado(id, 0);
        else if (boton.dataset.accion === "activar") cambiarEstado(id, 1);
        else if (boton.dataset.accion === "eliminar") eliminar(id);
    });

    await cargarPerfiles();
    await cargar();
}

async function cargar() {
    try {
        usuarios = await UsuariosAPI.listar();
        if (!document.getElementById("cuerpo-usuarios")) return;
        render(usuarios);
        pintarResumen();
    } catch (e) {
        notificar(e.message, "danger");
    }
}

function pintarResumen() {
    const activos = usuarios.filter((u) => Number(u.estado) === 1).length;
    const conCorreo = usuarios.filter((u) => u.correo).length;
    const perfilesDistintos = new Set(usuarios.map((u) => u.perfil).filter(Boolean)).size;
    pintarTarjetas("tarjetas-usuarios", [
        { icono: "bi-people", valor: usuarios.length, label: "Usuarios" },
        { icono: "bi-person-check", valor: activos, label: "Activos" },
        { icono: "bi-person-slash", valor: usuarios.length - activos, label: "Inactivos" },
        { icono: "bi-shield-lock", valor: perfilesDistintos, label: "Perfiles en uso" },
        { icono: "bi-envelope", valor: conCorreo, label: "Con correo" },
    ]);
}

async function cargarPerfiles() {
    const select = document.getElementById("usuario-perfil");
    try {
        perfiles = await PerfilesAPI.opciones();
        select.innerHTML = perfiles.map((p) =>
            `<option value="${p.id_perfil}">${escapar(p.nombre)}</option>`).join("");
    } catch {
        perfiles = [];
        select.innerHTML = "";
    }
}

function render(lista) {
    const cuerpo = document.getElementById("cuerpo-usuarios");
    if (!lista.length) {
        cuerpo.innerHTML =
            '<tr><td colspan="7" class="text-center text-muted py-4">No hay usuarios registrados.</td></tr>';
        return;
    }
    cuerpo.innerHTML = lista.map((u) => `
    <tr>
      <td class="text-muted">${u.id_usuario}</td>
      <td class="fw-medium">${escapar(u.usuario)}</td>
      <td>${escapar(u.nombre || "—")}</td>
      <td class="small">${escapar(u.correo || "—")}</td>
      <td><span class="badge text-bg-light">${escapar(u.perfil || "—")}</span></td>
      <td class="text-center">${Number(u.estado) === 1
            ? '<span class="badge text-bg-success">Activo</span>'
            : '<span class="badge text-bg-secondary">Inactivo</span>'}</td>
      <td class="text-end text-nowrap">${botonesAccion(u.id_usuario, u.estado)}</td>
    </tr>`).join("");
}

function abrirNuevo() {
    document.getElementById("form-usuario").reset();
    document.getElementById("usuario-id").value = "";
    document.getElementById("titulo-usuario").textContent = "Nuevo usuario";
    document.getElementById("error-usuario").classList.add("d-none");

    document.getElementById("asterisco-clave").classList.remove("d-none");
    document.getElementById("ayuda-clave").textContent = "Mínimo 4 caracteres.";
    modalUsuario.show();
}

function abrirEditar(id) {
    const u = usuarios.find((x) => x.id_usuario === id);
    document.getElementById("usuario-id").value = u.id_usuario;
    document.getElementById("usuario-usuario").value = u.usuario;
    document.getElementById("usuario-nombre").value = u.nombre || "";
    document.getElementById("usuario-correo").value = u.correo || "";
    document.getElementById("usuario-perfil").value = u.id_perfil || "";
    document.getElementById("usuario-estado").value = String(u.estado ?? 1);
    document.getElementById("usuario-clave").value = "";
    document.getElementById("titulo-usuario").textContent = "Editar usuario";
    document.getElementById("error-usuario").classList.add("d-none");

    document.getElementById("asterisco-clave").classList.add("d-none");
    document.getElementById("ayuda-clave").textContent =
        "Déjala vacía para conservar la clave actual.";
    modalUsuario.show();
}

async function guardar() {
    const id = document.getElementById("usuario-id").value;
    const esNuevo = !id;
    const usuario = document.getElementById("usuario-usuario").value;
    const nombre = document.getElementById("usuario-nombre").value;
    const correoValor = document.getElementById("usuario-correo").value;
    const clave = document.getElementById("usuario-clave").value;
    const perfil = document.getElementById("usuario-perfil").value;

    const error = v.primerError([
        v.usuario(usuario),
        v.soloTexto(nombre, "Nombre", { obligatorio: false }),
        v.correo(correoValor),
        perfil ? null : "Debes seleccionar un perfil.",

        (esNuevo || clave) ? v.claveMinima(clave, { obligatorio: esNuevo }) : null,
    ]);
    if (error) return mostrarError(error);

    const datos = {
        usuario: usuario.trim(),
        nombre: nombre.trim() || null,
        correo: correoValor.trim() || null,
        id_perfil: Number(perfil),
        estado: Number(document.getElementById("usuario-estado").value),
    };
    if (clave) datos.clave = clave;

    try {
        if (id) {
            await UsuariosAPI.actualizar(Number(id), datos);
            notificar("Usuario actualizado.");
        } else {
            await UsuariosAPI.crear(datos);
            notificar("Usuario creado.");
        }
        modalUsuario.hide();
        await cargar();
    } catch (e) {
        mostrarError(e.message);
    }
}

function mostrarError(mensaje) {
    const alerta = document.getElementById("error-usuario");
    alerta.textContent = mensaje;
    alerta.classList.remove("d-none");
}

async function cambiarEstado(id, estado) {
    const u = usuarios.find((x) => x.id_usuario === id);
    const accion = estado === 1 ? "Activar" : "Desactivar";
    if (!(await confirmar(`¿${accion} al usuario "${u.usuario}"?`))) return;
    try {
        await UsuariosAPI.cambiarEstado(id, estado);
        notificar(`Usuario ${estado === 1 ? "activado" : "desactivado"}.`);
        await cargar();
    } catch (e) {
        notificar(e.message, "danger");
    }
}

async function eliminar(id) {
    const u = usuarios.find((x) => x.id_usuario === id);
    if (!(await confirmar(`¿Eliminar al usuario "${u.usuario}"?`, "Dejará de aparecer en el sistema.", true))) return;
    try {
        await UsuariosAPI.eliminar(id);
        notificar("Usuario eliminado.");
        await cargar();
    } catch (e) {
        notificar(e.message, "danger");
    }
}
