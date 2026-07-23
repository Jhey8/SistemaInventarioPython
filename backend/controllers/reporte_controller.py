from datetime import date, timedelta

import pandas as pd
from flask import jsonify, send_file

from services.inventario_service import InventarioService
from services.movimiento_service import MovimientoService
from services import reportes_service, exportacion_service
from exceptions.errores import DatosInvalidosError

COLUMNAS = {
    "movimientos": [
        ("fecha", "Fecha"), ("producto", "Producto"), ("tipo_movimiento", "Tipo"),
        ("motivo", "Motivo"), ("cantidad", "Cantidad"),
        ("stock_anterior", "Stock anterior"), ("stock_nuevo", "Stock nuevo"),
        ("proveedor", "Proveedor"), ("subtotal", "Subtotal"), ("usuario", "Usuario"),
    ],
    "bajo_stock": [
        ("nombre", "Producto"), ("categoria", "Categoría"), ("cantidad", "Stock actual"),
        ("stock_minimo", "Stock mínimo"), ("faltante", "Faltante"),
    ],
    "por_categoria": [
        ("categoria", "Categoría"), ("productos", "Productos"), ("unidades", "Unidades"),
        ("precio_promedio", "Precio promedio"), ("valor", "Valor"),
    ],
    "top_productos": [
        ("nombre", "Producto"), ("categoria", "Categoría"), ("valor_total", "Valor"),
    ],
    "compras": [
        ("proveedor", "Proveedor"), ("movimientos", "N° compras"),
        ("unidades", "Unidades"), ("total", "Total comprado"),
    ],
    "reposicion": [
        ("nombre", "Producto"), ("categoria", "Categoría"), ("cantidad", "Stock"),
        ("consumo_diario", "Consumo/día"), ("dias_restantes", "Días restantes"),
        ("sugerido", "Sugerido comprar"), ("urgencia", "Urgencia"),
    ],
    "vencimientos": [
        ("nombre", "Producto"), ("categoria", "Categoría"), ("cantidad", "Stock"),
        ("fecha_vencimiento", "Vence"), ("dias_restantes", "Días restantes"),
        ("estado_venc", "Estado"),
    ],
}

def _df(records, clave_columnas):
    columnas = COLUMNAS[clave_columnas]
    titulos = [t for _, t in columnas]
    if not records:
        return pd.DataFrame(columns=titulos)
    origen = pd.DataFrame(records)
    return pd.DataFrame({t: origen[c] if c in origen else None for c, t in columnas})

class ReporteController:

    def __init__(self):
        self.inventario = InventarioService()
        self.movimientos = MovimientoService()

    def resumen(self):
        productos = self.inventario.listar_productos(solo_activos=True)
        resumen = reportes_service.generar_resumen(productos)

        movimientos = self.movimientos.listar_movimientos(500)
        resumen["por_mes"] = reportes_service.movimientos_por_mes(movimientos)
        resumen["ultimos_movimientos"] = [m.to_dict() for m in movimientos[:6]]

        bajos = sorted(
            (p for p in productos if p.necesita_reposicion),
            key=lambda p: p.stock_minimo - p.cantidad, reverse=True,
        )[:6]
        resumen["bajo_stock_detalle"] = [{
            "nombre": p.nombre, "categoria": p.categoria,
            "cantidad": p.cantidad, "stock_minimo": p.stock_minimo,
        } for p in bajos]
        return jsonify(resumen)

    def analisis(self):
        productos = self.inventario.listar_productos(solo_activos=True)
        return jsonify(reportes_service.analisis_pandas(productos))

    def movimientos_reporte(self, filtros):
        movimientos = self.movimientos.listar_filtrado(filtros)
        return jsonify({
            "movimientos": [m.to_dict() for m in movimientos],
            "resumen": reportes_service.resumen_movimientos(movimientos),
        })

    def compras(self, filtros):
        filtros = dict(filtros or {}, tipo_movimiento="ENTRADA")
        movimientos = self.movimientos.listar_filtrado(filtros)
        return jsonify(reportes_service.compras_por_proveedor(movimientos))

    def bajo_stock(self):
        productos = self.inventario.listar_productos(solo_activos=True)
        bajos = [p.to_dict() for p in productos if p.necesita_reposicion]
        return jsonify({
            "productos": bajos,
            "resumen": reportes_service.resumen_bajo_stock(productos),
        })

    def reposicion(self, filtros):
        return jsonify(self._datos_reposicion(filtros))

    def vencimientos(self, filtros):
        return jsonify(self._datos_vencimientos(filtros))

    def _datos_vencimientos(self, filtros):
        dias = int((filtros or {}).get("dias") or 30)
        productos = self.inventario.listar_productos(solo_activos=True)
        return reportes_service.reporte_vencimientos(productos, dias)

    def _datos_reposicion(self, filtros):
        ventana = int((filtros or {}).get("dias") or 30)
        cobertura = int((filtros or {}).get("cobertura") or 30)
        productos = self.inventario.listar_productos(solo_activos=True)
        desde = (date.today() - timedelta(days=ventana)).isoformat()
        salidas = self.movimientos.listar_filtrado(
            {"tipo_movimiento": "SALIDA", "fecha_desde": desde}
        )
        return reportes_service.prediccion_reposicion(productos, salidas, ventana, cobertura)

    def exportar(self, reporte, formato, filtros):
        titulo, tablas = self._tablas(reporte, filtros)
        if formato == "excel":
            archivo = exportacion_service.generar_excel(tablas)
            return self._enviar(archivo, f"{reporte}.xlsx",
                                 "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        if formato == "pdf":
            archivo = exportacion_service.generar_pdf(titulo, tablas)
            return self._enviar(archivo, f"{reporte}.pdf", "application/pdf")
        raise DatosInvalidosError("Formato inválido (use 'excel' o 'pdf').")

    def _enviar(self, archivo, nombre, mimetype):
        return send_file(archivo, mimetype=mimetype, as_attachment=True, download_name=nombre)

    def _tablas(self, reporte, filtros):
        if reporte == "valorizado":
            productos = self.inventario.listar_productos(solo_activos=True)
            datos = reportes_service.analisis_pandas(productos)
            return "Reporte de inventario valorizado", [
                ("Por categoría", _df(datos["por_categoria"], "por_categoria")),
                ("Top productos por valor", _df(datos["top_productos"], "top_productos")),
            ]
        if reporte == "movimientos":
            movimientos = self.movimientos.listar_filtrado(filtros)
            registros = [m.to_dict() for m in movimientos]
            return "Reporte de movimientos (Kardex)", [
                ("Movimientos", _df(registros, "movimientos")),
            ]
        if reporte == "bajo-stock":
            productos = self.inventario.listar_productos(solo_activos=True)
            bajos = []
            for p in productos:
                if p.necesita_reposicion:
                    fila = p.to_dict()
                    fila["faltante"] = max(0, p.stock_minimo - p.cantidad)
                    bajos.append(fila)
            return "Reporte de productos bajo stock", [
                ("Productos bajo stock", _df(bajos, "bajo_stock")),
            ]
        if reporte == "compras":
            filtros = dict(filtros or {}, tipo_movimiento="ENTRADA")
            movimientos = self.movimientos.listar_filtrado(filtros)
            datos = reportes_service.compras_por_proveedor(movimientos)
            return "Reporte de compras por proveedor", [
                ("Compras por proveedor", _df(datos["por_proveedor"], "compras")),
            ]
        if reporte == "reposicion":
            datos = self._datos_reposicion(filtros)
            return "Reporte de reposición sugerida", [
                ("Reposición sugerida", _df(datos["productos"], "reposicion")),
            ]
        if reporte == "vencimientos":
            datos = self._datos_vencimientos(filtros)
            return "Reporte de vencimientos", [
                ("Vencimientos", _df(datos["productos"], "vencimientos")),
            ]
        raise DatosInvalidosError("Reporte desconocido.")
