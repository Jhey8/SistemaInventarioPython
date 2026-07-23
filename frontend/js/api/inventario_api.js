const BASE = "/api";

async function pedir(url, opciones = {}) {
    const respuesta = await fetch(url, {
        headers: { "Content-Type": "application/json" },
        credentials: "same-origin",
        ...opciones,
    });
    const datos = await respuesta.json().catch(() => ({}));
    if (!respuesta.ok) {
        const error = new Error(datos.error || "Ocurrió un error en el servidor.");
        error.status = respuesta.status;
        throw error;
    }
    return datos;
}

export const AuthAPI = {
    login: (usuario, clave) =>
        pedir(`${BASE}/auth/login`, { method: "POST", body: JSON.stringify({ usuario, clave }) }),
    logout: () => pedir(`${BASE}/auth/logout`, { method: "POST" }),
    actual: () => pedir(`${BASE}/auth/actual`),
    misDatos: (d) => pedir(`${BASE}/auth/mis-datos`, { method: "PUT", body: JSON.stringify(d) }),
    cambiarClave: (d) => pedir(`${BASE}/auth/cambiar-clave`, { method: "POST", body: JSON.stringify(d) }),
};

export const ModulosAPI = {
    menu: () => pedir(`${BASE}/modulos`),
    todos: () => pedir(`${BASE}/modulos/todos`),
};

export const PerfilesAPI = {
    listar: () => pedir(`${BASE}/perfiles`),
    opciones: () => pedir(`${BASE}/perfiles/opciones`),
    crear: (p) => pedir(`${BASE}/perfiles`, { method: "POST", body: JSON.stringify(p) }),
    actualizar: (id, p) => pedir(`${BASE}/perfiles/${id}`, { method: "PUT", body: JSON.stringify(p) }),
    eliminar: (id) => pedir(`${BASE}/perfiles/${id}`, { method: "DELETE" }),
    cambiarEstado: (id, estado) => pedir(`${BASE}/perfiles/${id}/estado`, { method: "PUT", body: JSON.stringify({ estado }) }),
};

export const UsuariosAPI = {
    listar: () => pedir(`${BASE}/usuarios`),
    crear: (u) => pedir(`${BASE}/usuarios`, { method: "POST", body: JSON.stringify(u) }),
    actualizar: (id, u) => pedir(`${BASE}/usuarios/${id}`, { method: "PUT", body: JSON.stringify(u) }),
    eliminar: (id) => pedir(`${BASE}/usuarios/${id}`, { method: "DELETE" }),
    cambiarEstado: (id, estado) => pedir(`${BASE}/usuarios/${id}/estado`, { method: "PUT", body: JSON.stringify({ estado }) }),
};

export const InventarioAPI = {
    listar: () => pedir(`${BASE}/productos`),
    opciones: () => pedir(`${BASE}/productos/opciones`),
    crear: (p) => pedir(`${BASE}/productos`, { method: "POST", body: JSON.stringify(p) }),
    actualizar: (id, p) => pedir(`${BASE}/productos/${id}`, { method: "PUT", body: JSON.stringify(p) }),
    eliminar: (id) => pedir(`${BASE}/productos/${id}`, { method: "DELETE" }),
    cambiarEstado: (id, estado) => pedir(`${BASE}/productos/${id}/estado`, { method: "PUT", body: JSON.stringify({ estado }) }),
    resumen: () => pedir(`${BASE}/reportes/resumen`),
    analisis: () => pedir(`${BASE}/reportes/analisis`),
};

export const CategoriasAPI = {
    listar: () => pedir(`${BASE}/categorias`),
    opciones: () => pedir(`${BASE}/categorias/opciones`),
    crear: (c) => pedir(`${BASE}/categorias`, { method: "POST", body: JSON.stringify(c) }),
    actualizar: (id, c) => pedir(`${BASE}/categorias/${id}`, { method: "PUT", body: JSON.stringify(c) }),
    eliminar: (id) => pedir(`${BASE}/categorias/${id}`, { method: "DELETE" }),
    cambiarEstado: (id, estado) => pedir(`${BASE}/categorias/${id}/estado`, { method: "PUT", body: JSON.stringify({ estado }) }),
};

export const ProveedoresAPI = {
    listar: () => pedir(`${BASE}/proveedores`),
    opciones: () => pedir(`${BASE}/proveedores/opciones`),
    crear: (p) => pedir(`${BASE}/proveedores`, { method: "POST", body: JSON.stringify(p) }),
    actualizar: (id, p) => pedir(`${BASE}/proveedores/${id}`, { method: "PUT", body: JSON.stringify(p) }),
    eliminar: (id) => pedir(`${BASE}/proveedores/${id}`, { method: "DELETE" }),
    cambiarEstado: (id, estado) => pedir(`${BASE}/proveedores/${id}/estado`, { method: "PUT", body: JSON.stringify({ estado }) }),
};

function consulta(filtros = {}) {
    const params = new URLSearchParams();
    Object.entries(filtros).forEach(([k, val]) => {
        if (val !== "" && val !== null && val !== undefined) params.append(k, val);
    });
    const s = params.toString();
    return s ? `?${s}` : "";
}

export const MovimientosAPI = {
    listar: (f) => pedir(`${BASE}/movimientos${consulta(f)}`),
    registrar: (m) => pedir(`${BASE}/movimientos`, { method: "POST", body: JSON.stringify(m) }),
};

export const ReportesAPI = {
    analisis: () => pedir(`${BASE}/reportes/analisis`),
    movimientos: (f) => pedir(`${BASE}/reportes/movimientos${consulta(f)}`),
    compras: (f) => pedir(`${BASE}/reportes/compras${consulta(f)}`),
    bajoStock: () => pedir(`${BASE}/reportes/bajo-stock`),
    reposicion: (f) => pedir(`${BASE}/reportes/reposicion${consulta(f)}`),
    vencimientos: (f) => pedir(`${BASE}/reportes/vencimientos${consulta(f)}`),

    urlExportar: (reporte, formato, f) =>
        `${BASE}/reportes/exportar/${reporte}${consulta({ formato, ...f })}`,
};
