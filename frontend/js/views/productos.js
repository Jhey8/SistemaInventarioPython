import { InventarioAPI, CategoriasAPI } from "../api/inventario_api.js";
import { dinero, escapar, notificar, pintarTarjetas, botonesAccion, confirmar } from "../utils/helpers.js";
import * as v from "../utils/validaciones.js";

let productos = [];
let modalProducto = null;

export async function init() {
    modalProducto = new bootstrap.Modal("#modal-producto");

    document.getElementById("btn-nuevo").addEventListener("click", abrirNuevo);
    document.getElementById("buscador").addEventListener("input", filtrar);
    document.getElementById("btn-guardar").addEventListener("click", guardar);
    document.getElementById("form-producto").addEventListener("submit", (e) => {
        e.preventDefault();
        guardar();
    });

    v.soloNumero(document.getElementById("campo-cantidad"));
    v.soloNumero(document.getElementById("campo-precio"), true);
    v.soloNumero(document.getElementById("campo-minimo"));
    document.getElementById("campo-vencimiento").min = v.hoyISO();

    document.getElementById("cuerpo-tabla").addEventListener("click", (e) => {
        const boton = e.target.closest("button[data-accion]");
        if (!boton) return;
        const id = Number(boton.dataset.id);
        if (boton.dataset.accion === "editar") abrirEditar(id);
        else if (boton.dataset.accion === "desactivar") cambiarEstado(id, 0);
        else if (boton.dataset.accion === "activar") cambiarEstado(id, 1);
        else if (boton.dataset.accion === "eliminar") eliminar(id);
    });

    await Promise.all([llenarCategorias(), cargar()]);
}

async function cargar() {
    try {
        productos = await InventarioAPI.listar();
        if (!document.getElementById("cuerpo-tabla")) return;
        render(productos);
        pintarResumen();
    } catch (e) {
        notificar(e.message, "danger");
    }
}

function pintarResumen() {
    const unidades = productos.reduce((a, p) => a + p.cantidad, 0);
    const valor = productos.reduce((a, p) => a + p.valor_total, 0);
    const bajo = productos.filter((p) => p.necesita_reposicion).length;
    const categorias = new Set(productos.map((p) => p.categoria)).size;
    pintarTarjetas("tarjetas-productos", [
        { icono: "bi-boxes", valor: productos.length, label: "Productos" },
        { icono: "bi-stack", valor: unidades, label: "Unidades en stock" },
        { icono: "bi-cash-stack", valor: dinero(valor), label: "Valor total" },
        { icono: "bi-exclamation-triangle", valor: bajo, label: "Bajo stock" },
        { icono: "bi-tags", valor: categorias, label: "Categorías" },
    ]);
}

function render(lista) {
    const cuerpo = document.getElementById("cuerpo-tabla");
    cuerpo.innerHTML = lista.map((p) => `
    <tr class="${p.estado === 0 ? "text-muted" : (p.necesita_reposicion ? "fila-alerta" : "")}">
      <td class="text-muted">${p.id}</td>
      <td class="fw-medium">${escapar(p.nombre)}
        ${p.estado === 0 ? '<span class="badge text-bg-secondary ms-1">Inactivo</span>' : ""}</td>
      <td><span class="badge rounded-pill text-bg-light">${escapar(p.categoria)}</span></td>
      <td class="text-end">${p.cantidad}</td>
      <td class="text-end">${dinero(p.precio)}</td>
      <td class="text-end fw-medium">${dinero(p.valor_total)}</td>
      <td class="text-center">${p.necesita_reposicion
            ? '<span class="badge text-bg-warning">Bajo stock</span>'
            : '<span class="badge text-bg-success">OK</span>'}</td>
      <td class="text-end text-nowrap">${botonesAccion(p.id, p.estado)}</td>
    </tr>`).join("");
}

function filtrar() {
    const texto = document.getElementById("buscador").value.toLowerCase();
    render(productos.filter((p) =>
        p.nombre.toLowerCase().includes(texto) || (p.categoria || "").toLowerCase().includes(texto)));
}

function abrirNuevo() {
    document.getElementById("form-producto").reset();
    document.getElementById("producto-id").value = "";
    document.getElementById("titulo-modal").textContent = "Nuevo producto";
    document.getElementById("error-form").classList.add("d-none");
    modalProducto.show();
}

function abrirEditar(id) {
    const p = productos.find((x) => x.id === id);
    document.getElementById("producto-id").value = p.id;
    document.getElementById("campo-nombre").value = p.nombre;
    document.getElementById("campo-categoria").value = p.categoria_id;
    document.getElementById("campo-cantidad").value = p.cantidad;
    document.getElementById("campo-precio").value = p.precio;
    document.getElementById("campo-minimo").value = p.stock_minimo;
    document.getElementById("campo-vencimiento").value = p.fecha_vencimiento || "";
    document.getElementById("titulo-modal").textContent = "Editar producto";
    document.getElementById("error-form").classList.add("d-none");
    modalProducto.show();
}

async function guardar() {
    const id = document.getElementById("producto-id").value;
    const nombre = document.getElementById("campo-nombre").value;
    const cantidad = document.getElementById("campo-cantidad").value;
    const precio = document.getElementById("campo-precio").value;
    const minimo = document.getElementById("campo-minimo").value;

    const vencimiento = document.getElementById("campo-vencimiento").value;
    const esNuevo = !id;
    const error = v.primerError([
        v.requerido(nombre, "Nombre"),
        document.getElementById("campo-categoria").value ? null : "Debes seleccionar una categoría.",
        v.noNegativo(cantidad, "Cantidad"),
        v.noNegativo(precio, "Precio"),
        v.noNegativo(minimo, "Stock mínimo"),
        esNuevo ? v.fechaNoPasada(vencimiento) : null,
    ]);
    if (error) {
        const alerta = document.getElementById("error-form");
        alerta.textContent = error;
        alerta.classList.remove("d-none");
        return;
    }

    const datos = {
        nombre: nombre.trim(),
        categoria_id: Number(document.getElementById("campo-categoria").value),
        cantidad: Number(cantidad),
        precio: Number(precio),
        stock_minimo: Number(minimo),
        fecha_vencimiento: document.getElementById("campo-vencimiento").value || null,
    };
    try {
        if (id) {
            await InventarioAPI.actualizar(Number(id), datos);
            notificar("Producto actualizado.");
        } else {
            await InventarioAPI.crear(datos);
            notificar("Producto creado.");
        }
        modalProducto.hide();
        await cargar();
    } catch (e) {
        const alerta = document.getElementById("error-form");
        alerta.textContent = e.message;
        alerta.classList.remove("d-none");
    }
}

async function cambiarEstado(id, estado) {
    const p = productos.find((x) => x.id === id);
    const accion = estado === 1 ? "Activar" : "Desactivar";
    if (!(await confirmar(`¿${accion} el producto "${p.nombre}"?`))) return;
    try {
        await InventarioAPI.cambiarEstado(id, estado);
        notificar(`Producto ${estado === 1 ? "activado" : "desactivado"}.`);
        await cargar();
    } catch (e) {
        notificar(e.message, "danger");
    }
}

async function eliminar(id) {
    const p = productos.find((x) => x.id === id);
    if (!(await confirmar(`¿Eliminar el producto "${p.nombre}"?`, "Dejará de aparecer en el sistema.", true))) return;
    try {
        await InventarioAPI.eliminar(id);
        notificar("Producto eliminado.");
        await cargar();
    } catch (e) {
        notificar(e.message, "danger");
    }
}

async function llenarCategorias() {
    const select = document.getElementById("campo-categoria");
    try {
        const cats = await CategoriasAPI.opciones();
        select.innerHTML = cats.map((c) =>
            `<option value="${c.id}">${escapar(c.nombre)}</option>`).join("");
    } catch {
        select.innerHTML = "";
    }
}
