import { CategoriasAPI, InventarioAPI } from "../api/inventario_api.js";
import { escapar, notificar, pintarTarjetas, badgeActivo, botonesAccion, confirmar } from "../utils/helpers.js";

let categorias = [];
let modalCategoria = null;

export async function init() {
    modalCategoria = new bootstrap.Modal("#modal-categoria");
    document.getElementById("btn-nueva-cat").addEventListener("click", abrirNueva);
    document.getElementById("btn-guardar-cat").addEventListener("click", guardar);
    document.getElementById("form-categoria").addEventListener("submit", (e) => {
        e.preventDefault();
        guardar();
    });

    document.getElementById("cuerpo-categorias").addEventListener("click", (e) => {
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
        const [cats, productos] = await Promise.all([
            CategoriasAPI.listar(),
            InventarioAPI.opciones().catch(() => []),
        ]);
        if (!document.getElementById("cuerpo-categorias")) return;
        categorias = cats;
        render(categorias);
        pintarResumen(productos);
    } catch (e) {
        notificar(e.message, "danger");
    }
}

function pintarResumen(productos) {
    const conProductos = new Set(productos.map((p) => p.categoria)).size;
    const conDescripcion = categorias.filter((c) => c.descripcion).length;
    const promedio = categorias.length
        ? (productos.length / categorias.length).toFixed(1) : 0;
    pintarTarjetas("tarjetas-categorias", [
        { icono: "bi-tags", valor: categorias.length, label: "Categorías" },
        { icono: "bi-boxes", valor: productos.length, label: "Productos" },
        { icono: "bi-diagram-3", valor: conProductos, label: "Con productos" },
        { icono: "bi-bar-chart", valor: promedio, label: "Prod. por categoría" },
        { icono: "bi-card-text", valor: conDescripcion, label: "Con descripción" },
    ]);
}

function render(lista) {
    document.getElementById("cuerpo-categorias").innerHTML = lista.map((c) => `
    <tr class="${c.estado === 0 ? "text-muted" : ""}">
      <td class="text-muted">${c.id}</td>
      <td class="fw-medium">${escapar(c.nombre)}</td>
      <td class="text-muted">${escapar(c.descripcion || "—")}</td>
      <td class="text-center">${badgeActivo(c.estado)}</td>
      <td class="text-end text-nowrap">${botonesAccion(c.id, c.estado)}</td>
    </tr>`).join("");
}

function abrirNueva() {
    document.getElementById("form-categoria").reset();
    document.getElementById("cat-id").value = "";
    document.getElementById("titulo-cat").textContent = "Nueva categoría";
    document.getElementById("error-cat").classList.add("d-none");
    modalCategoria.show();
}

function abrirEditar(id) {
    const c = categorias.find((x) => x.id === id);
    document.getElementById("cat-id").value = c.id;
    document.getElementById("cat-nombre").value = c.nombre;
    document.getElementById("cat-descripcion").value = c.descripcion || "";
    document.getElementById("titulo-cat").textContent = "Editar categoría";
    document.getElementById("error-cat").classList.add("d-none");
    modalCategoria.show();
}

async function guardar() {
    const id = document.getElementById("cat-id").value;
    const datos = {
        nombre: document.getElementById("cat-nombre").value.trim(),
        descripcion: document.getElementById("cat-descripcion").value.trim() || null,
    };
    try {
        if (id) {
            await CategoriasAPI.actualizar(Number(id), datos);
            notificar("Categoría actualizada.");
        } else {
            await CategoriasAPI.crear(datos);
            notificar("Categoría creada.");
        }
        modalCategoria.hide();
        await cargar();
    } catch (e) {
        const alerta = document.getElementById("error-cat");
        alerta.textContent = e.message;
        alerta.classList.remove("d-none");
    }
}

async function cambiarEstado(id, estado) {
    const c = categorias.find((x) => x.id === id);
    const accion = estado === 1 ? "activar" : "desactivar";
    if (!(await confirmar(`¿${accion.charAt(0).toUpperCase() + accion.slice(1)} la categoría "${c.nombre}"?`))) return;
    try {
        await CategoriasAPI.cambiarEstado(id, estado);
        notificar(`Categoría ${estado === 1 ? "activada" : "desactivada"}.`);
        await cargar();
    } catch (e) {
        notificar(e.message, "danger");
    }
}

async function eliminar(id) {
    const c = categorias.find((x) => x.id === id);
    if (!(await confirmar(`¿Eliminar la categoría "${c.nombre}"?`, "Dejará de aparecer en el sistema.", true))) return;
    try {
        await CategoriasAPI.eliminar(id);
        notificar("Categoría eliminada.");
        await cargar();
    } catch (e) {
        notificar(e.message, "danger");
    }
}
