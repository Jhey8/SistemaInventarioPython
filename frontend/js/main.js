import { AuthAPI } from "./api/inventario_api.js";
import { iniciarRouter, navegar, construirMenu } from "./router.js";
import { notificar } from "./utils/helpers.js";
import * as v from "./utils/validaciones.js";

const pantallaLogin = () => document.getElementById("pantalla-login");
const app = () => document.getElementById("app");

let usuarioActual = null;
let modalMisDatos = null;
let modalCambiarClave = null;

document.addEventListener("DOMContentLoaded", async () => {
    configurarLogin();
    configurarApp();
    await verificarSesion();
});

async function verificarSesion() {
    try {
        const usuario = await AuthAPI.actual();
        await entrarAlSistema(usuario);
    } catch {
        mostrarLogin();
    }
}

function configurarLogin() {
    document.getElementById("form-login").addEventListener("submit", async (e) => {
        e.preventDefault();
        const usuario = document.getElementById("login-usuario").value.trim();
        const clave = document.getElementById("login-clave").value;
        const boton = document.getElementById("btn-login");
        const error = document.getElementById("error-login");
        boton.disabled = true;
        try {
            const datos = await AuthAPI.login(usuario, clave);
            error.classList.add("d-none");
            await entrarAlSistema(datos);
        } catch (err) {
            error.textContent = err.message;
            error.classList.remove("d-none");
        } finally {
            boton.disabled = false;
        }
    });
}

function configurarApp() {

    if (window.innerWidth <= 768) document.body.classList.add("sidebar-oculto");
    document.getElementById("btn-menu").addEventListener("click", () => {
        document.body.classList.toggle("sidebar-oculto");
    });
    document.getElementById("btn-logout").addEventListener("click", (e) => {
        e.preventDefault();
        cerrarSesion();
    });
    configurarCuenta();
}

function configurarCuenta() {
    modalMisDatos = new bootstrap.Modal("#modal-mis-datos");
    modalCambiarClave = new bootstrap.Modal("#modal-cambiar-clave");
    v.filtrarEntrada(document.getElementById("md-nombre"), "texto");

    document.getElementById("btn-mis-datos").addEventListener("click", (e) => {
        e.preventDefault();
        document.getElementById("md-usuario").value = usuarioActual?.usuario || "";
        document.getElementById("md-nombre").value = usuarioActual?.nombre || "";
        document.getElementById("md-correo").value = usuarioActual?.correo || "";
        document.getElementById("error-mis-datos").classList.add("d-none");
        modalMisDatos.show();
    });
    document.getElementById("btn-guardar-mis-datos").addEventListener("click", guardarMisDatos);
    document.getElementById("form-mis-datos").addEventListener("submit", (e) => {
        e.preventDefault();
        guardarMisDatos();
    });

    document.getElementById("btn-cambiar-clave").addEventListener("click", (e) => {
        e.preventDefault();
        document.getElementById("form-cambiar-clave").reset();
        document.getElementById("error-clave").classList.add("d-none");
        modalCambiarClave.show();
    });
    document.getElementById("btn-guardar-clave").addEventListener("click", guardarClave);
    document.getElementById("form-cambiar-clave").addEventListener("submit", (e) => {
        e.preventDefault();
        guardarClave();
    });
}

async function guardarMisDatos() {
    const nombre = document.getElementById("md-nombre").value;
    const correo = document.getElementById("md-correo").value;
    const error = v.primerError([
        v.soloTexto(nombre, "Nombre", { obligatorio: false }),
        v.correo(correo),
    ]);
    if (error) return mostrarErrorCuenta("error-mis-datos", error);
    try {
        usuarioActual = await AuthAPI.misDatos({ nombre: nombre.trim() || null, correo: correo.trim() || null });
        document.getElementById("nombre-usuario").textContent = usuarioActual.nombre || usuarioActual.usuario;
        modalMisDatos.hide();
        notificar("Datos actualizados.");
    } catch (e) {
        mostrarErrorCuenta("error-mis-datos", e.message);
    }
}

async function guardarClave() {
    const actual = document.getElementById("cc-actual").value;
    const nueva = document.getElementById("cc-nueva").value;
    const repetir = document.getElementById("cc-repetir").value;
    const error = v.primerError([
        actual ? null : "Ingresa tu contraseña actual.",
        v.claveMinima(nueva),
        nueva === repetir ? null : "Las contraseñas nuevas no coinciden.",
    ]);
    if (error) return mostrarErrorCuenta("error-clave", error);
    try {
        await AuthAPI.cambiarClave({ clave_actual: actual, clave_nueva: nueva });
        modalCambiarClave.hide();
        notificar("Contraseña actualizada.");
    } catch (e) {
        mostrarErrorCuenta("error-clave", e.message);
    }
}

function mostrarErrorCuenta(id, mensaje) {
    const alerta = document.getElementById(id);
    alerta.textContent = mensaje;
    alerta.classList.remove("d-none");
}

async function entrarAlSistema(usuario) {
    usuarioActual = usuario;
    document.getElementById("nombre-usuario").textContent =
        usuario.nombre || usuario.usuario;
    const perfil = document.getElementById("perfil-usuario");
    if (perfil) perfil.textContent = usuario.perfil ? `Perfil: ${usuario.perfil}` : "";
    pantallaLogin().classList.add("d-none");
    app().classList.remove("d-none");

    await construirMenu();
    iniciarRouter();
    navegar("dashboard");
}

function mostrarLogin() {
    app().classList.add("d-none");
    pantallaLogin().classList.remove("d-none");
    document.getElementById("form-login").reset();
    document.getElementById("login-usuario").focus();
}

async function cerrarSesion() {
    try {
        await AuthAPI.logout();
    } catch {

    }
    mostrarLogin();
    notificar("Sesión cerrada.");
}
