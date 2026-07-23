const PATRON_TEXTO = /^[A-Za-zÁÉÍÓÚÜáéíóúüÑñ .,'\-]+$/;
const PATRON_USUARIO = /^[A-Za-z0-9._-]+$/;
const PATRON_CORREO = /^[^@\s]+@[^@\s]+\.[^@\s]+$/;
const PATRON_DIGITOS = /^\d+$/;

export function requerido(valor, campo) {
    if (!valor || !valor.trim()) return `El campo '${campo}' es obligatorio.`;
    return null;
}

export function soloTexto(valor, campo, { obligatorio = true } = {}) {
    valor = (valor || "").trim();
    if (!valor) return obligatorio ? `El campo '${campo}' es obligatorio.` : null;
    if (!PATRON_TEXTO.test(valor)) return `El campo '${campo}' solo admite letras y espacios.`;
    return null;
}

export function usuario(valor) {
    valor = (valor || "").trim();
    if (valor.length < 3) return "El usuario debe tener al menos 3 caracteres.";
    if (!PATRON_USUARIO.test(valor))
        return "El usuario solo admite letras, números, punto, guion y guion bajo.";
    return null;
}

export function correo(valor, { obligatorio = false } = {}) {
    valor = (valor || "").trim();
    if (!valor) return obligatorio ? "El correo es obligatorio." : null;
    if (!PATRON_CORREO.test(valor)) return "El correo no tiene un formato válido.";
    return null;
}

export function digitos(valor, campo, { longitud = null, obligatorio = false } = {}) {
    valor = (valor || "").trim();
    if (!valor) return obligatorio ? `El campo '${campo}' es obligatorio.` : null;
    if (!PATRON_DIGITOS.test(valor)) return `El campo '${campo}' solo admite números.`;
    if (longitud && valor.length !== longitud)
        return `El campo '${campo}' debe tener ${longitud} dígitos.`;
    return null;
}

export function claveMinima(valor, { obligatorio = true, minimo = 4 } = {}) {
    valor = valor || "";
    if (!valor) return obligatorio ? "La clave es obligatoria." : null;
    if (valor.length < minimo) return `La clave debe tener al menos ${minimo} caracteres.`;
    return null;
}

export function noNegativo(valor, campo) {
    if (valor === "" || valor === null || valor === undefined)
        return `El campo '${campo}' es obligatorio.`;
    const numero = Number(valor);
    if (Number.isNaN(numero)) return `El campo '${campo}' debe ser un número.`;
    if (numero < 0) return `El campo '${campo}' no puede ser negativo.`;
    return null;
}

export function primerError(errores) {
    return errores.find((e) => e) || null;
}

export function filtrarEntrada(input, tipo) {
    const patrones = {
        texto: /[^A-Za-zÁÉÍÓÚÜáéíóúüÑñ .,'\-]/g,
        usuario: /[^A-Za-z0-9._-]/g,
        digitos: /[^\d]/g,
    };
    input.addEventListener("input", () => {
        const limpio = input.value.replace(patrones[tipo], "");
        if (limpio !== input.value) input.value = limpio;
    });
}
