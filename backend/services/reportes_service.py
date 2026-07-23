from functools import reduce
from math import ceil
from datetime import date

import pandas as pd

def valor_total_inventario(productos):
    return round(reduce(lambda acc, p: acc + p.valor_total, productos, 0.0), 2)

def unidades_totales(productos):
    return reduce(lambda acc, p: acc + p.cantidad, productos, 0)

def productos_bajo_stock(productos):
    return list(filter(lambda p: p.necesita_reposicion, productos))

def valor_por_categoria(productos):
    return reduce(
        lambda acc, p: {
            **acc,
            p.categoria: round(acc.get(p.categoria, 0.0) + p.valor_total, 2),
        },
        productos,
        {},
    )

def conteo_por_categoria(productos):
    return reduce(
        lambda acc, p: {**acc, p.categoria: acc.get(p.categoria, 0) + 1}, productos, {}
    )

def generar_resumen(productos):
    bajo_stock = productos_bajo_stock(productos)
    venc = reporte_vencimientos(productos)["resumen"]
    return {
        "total_productos": len(productos),
        "unidades_totales": unidades_totales(productos),
        "valor_total": valor_total_inventario(productos),
        "categorias": len(conteo_por_categoria(productos)),
        "productos_bajo_stock": len(bajo_stock),
        "nombres_bajo_stock": [p.nombre for p in bajo_stock],
        "valor_por_categoria": valor_por_categoria(productos),
        "vencidos": venc["vencidos"],
        "por_vencer": venc["por_vencer"],
    }

def analisis_pandas(productos):
    if not productos:
        return {"por_categoria": [], "top_productos": [], "totales": {}}

    df = pd.DataFrame([p.to_dict() for p in productos])

    por_categoria = (
        df.groupby("categoria")
        .agg(
            productos=("nombre", "count"),
            unidades=("cantidad", "sum"),
            valor=("valor_total", "sum"),
            precio_promedio=("precio", "mean"),
        )
        .round(2)
        .reset_index()
        .sort_values("valor", ascending=False)
    )

    top = df.sort_values("valor_total", ascending=False).head(5)[
        ["nombre", "categoria", "valor_total"]
    ]

    totales = {
        "valor_total": round(float(df["valor_total"].sum()), 2),
        "unidades": int(df["cantidad"].sum()),
        "productos": int(len(df)),
    }
    return {
        "por_categoria": por_categoria.to_dict(orient="records"),
        "top_productos": top.to_dict(orient="records"),
        "totales": totales,
    }

def _suma(movimientos, condicion, campo):
    return reduce(
        lambda acc, m: acc + (getattr(m, campo) or 0 if condicion(m) else 0),
        movimientos, 0,
    )

def resumen_movimientos(movimientos):
    es = lambda t: (lambda m: m.tipo_movimiento == t)
    entradas = list(filter(es("ENTRADA"), movimientos))
    salidas = list(filter(es("SALIDA"), movimientos))
    ajustes = list(filter(es("AJUSTE"), movimientos))
    valor_comprado = round(
        reduce(lambda acc, m: acc + float(m.subtotal or 0), entradas, 0.0), 2
    )
    return {
        "total": len(movimientos),
        "entradas": len(entradas),
        "salidas": len(salidas),
        "ajustes": len(ajustes),
        "unidades_entrada": _suma(movimientos, es("ENTRADA"), "cantidad"),
        "unidades_salida": _suma(movimientos, es("SALIDA"), "cantidad"),
        "valor_comprado": valor_comprado,
    }

def compras_por_proveedor(movimientos):
    entradas = [m for m in movimientos if m.tipo_movimiento == "ENTRADA"]
    if not entradas:
        return {"por_proveedor": [], "resumen": resumen_movimientos([])}

    df = pd.DataFrame([{
        "proveedor": m.proveedor_nombre or "—",
        "movimientos": 1,
        "unidades": m.cantidad,
        "total": float(m.subtotal or 0),
    } for m in entradas])

    por_proveedor = (
        df.groupby("proveedor")
        .agg(movimientos=("movimientos", "sum"),
             unidades=("unidades", "sum"),
             total=("total", "sum"))
        .round(2)
        .reset_index()
        .sort_values("total", ascending=False)
    )
    return {
        "por_proveedor": por_proveedor.to_dict(orient="records"),
        "resumen": resumen_movimientos(entradas),
    }

def resumen_bajo_stock(productos):
    bajo = [p for p in productos if p.necesita_reposicion]
    sin_stock = [p for p in bajo if p.cantidad == 0]
    faltante = reduce(
        lambda acc, p: acc + max(0, p.stock_minimo - p.cantidad), bajo, 0
    )
    return {
        "total_productos": len(productos),
        "bajo_stock": len(bajo),
        "sin_stock": len(sin_stock),
        "unidades_faltantes": faltante,
    }

def _urgencia(cantidad, consumo_diario, dias_restantes):
    if cantidad == 0:
        return "SIN STOCK"
    if consumo_diario == 0:
        return "SIN CONSUMO"
    if dias_restantes <= 7:
        return "CRÍTICO"
    if dias_restantes <= 15:
        return "ATENCIÓN"
    return "OK"

def prediccion_reposicion(productos, salidas, ventana_dias=30, cobertura_dias=30):
    ventana_dias = max(1, int(ventana_dias))

    consumo = reduce(
        lambda acc, m: {**acc, m.id_producto: acc.get(m.id_producto, 0) + m.cantidad},
        salidas, {},
    )

    filas = []
    for p in productos:
        vendidas = consumo.get(p.id, 0)
        diario = round(vendidas / ventana_dias, 2)
        dias_restantes = int(p.cantidad / diario) if diario > 0 else None
        if diario > 0:
            sugerido = max(0, ceil(diario * cobertura_dias - p.cantidad))
        else:
            sugerido = max(0, p.stock_minimo - p.cantidad)
        filas.append({
            "id": p.id,
            "nombre": p.nombre,
            "categoria": p.categoria,
            "cantidad": p.cantidad,
            "stock_minimo": p.stock_minimo,
            "consumo_diario": diario,
            "dias_restantes": dias_restantes,
            "sugerido": sugerido,
            "urgencia": _urgencia(p.cantidad, diario, dias_restantes),
        })

    filas.sort(key=lambda f: (f["dias_restantes"] is None,
                              f["dias_restantes"] if f["dias_restantes"] is not None else 0))

    por_agotarse = [f for f in filas if f["dias_restantes"] is not None and f["dias_restantes"] <= 7]
    atencion = [f for f in filas if f["dias_restantes"] is not None and 7 < f["dias_restantes"] <= 15]
    sin_consumo = [f for f in filas if f["consumo_diario"] == 0]
    return {
        "productos": filas,
        "resumen": {
            "productos": len(filas),
            "por_agotarse": len(por_agotarse),
            "en_atencion": len(atencion),
            "sin_consumo": len(sin_consumo),
            "unidades_comprar": sum(f["sugerido"] for f in filas),
        },
    }

def movimientos_por_mes(movimientos, meses=6):
    hoy = date.today()
    etiquetas = []
    anio, mes = hoy.year, hoy.month
    for _ in range(meses):
        etiquetas.append(f"{anio:04d}-{mes:02d}")
        mes -= 1
        if mes == 0:
            mes, anio = 12, anio - 1
    etiquetas.reverse()

    entradas = {e: 0 for e in etiquetas}
    salidas = {e: 0 for e in etiquetas}
    for m in movimientos:
        clave = m.fecha.strftime("%Y-%m") if hasattr(m.fecha, "strftime") else str(m.fecha)[:7]
        if clave in entradas:
            if m.tipo_movimiento == "ENTRADA":
                entradas[clave] += m.cantidad
            elif m.tipo_movimiento == "SALIDA":
                salidas[clave] += m.cantidad
    return {
        "meses": etiquetas,
        "entradas": [entradas[e] for e in etiquetas],
        "salidas": [salidas[e] for e in etiquetas],
    }

def _estado_vencimiento(dias, dias_alerta):
    if dias < 0:
        return "VENCIDO"
    if dias <= dias_alerta:
        return "POR VENCER"
    return "VIGENTE"

def reporte_vencimientos(productos, dias_alerta=30):
    hoy = date.today()
    filas = []
    for p in productos:
        fecha = getattr(p, "fecha_vencimiento", None)
        if not fecha:
            continue
        try:
            dias = (date.fromisoformat(fecha) - hoy).days
        except (ValueError, TypeError):
            continue
        filas.append({
            "id": p.id,
            "nombre": p.nombre,
            "categoria": p.categoria,
            "cantidad": p.cantidad,
            "fecha_vencimiento": fecha,
            "dias_restantes": dias,
            "estado_venc": _estado_vencimiento(dias, dias_alerta),
        })

    filas.sort(key=lambda f: f["dias_restantes"])
    vencidos = [f for f in filas if f["estado_venc"] == "VENCIDO"]
    por_vencer = [f for f in filas if f["estado_venc"] == "POR VENCER"]
    vigentes = [f for f in filas if f["estado_venc"] == "VIGENTE"]
    return {
        "productos": filas,
        "resumen": {
            "perecederos": len(filas),
            "vencidos": len(vencidos),
            "por_vencer": len(por_vencer),
            "vigentes": len(vigentes),
            "unidades_riesgo": sum(f["cantidad"] for f in vencidos + por_vencer),
        },
    }
