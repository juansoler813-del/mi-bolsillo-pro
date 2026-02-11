import flet as ft
import sqlite3
import datetime
import time
import math
from typing import Dict, List, Tuple, Optional

# =========================================================
# MOTOR DE IA
# =========================================================
class MotorIA:
    @staticmethod
    def calcular_score_financiero(ingresos: float, gastos: float, ahorros: float, deudas: float) -> Dict:
        score = 50
        if ingresos > 0:
            tasa_ahorro = (ingresos - gastos) / ingresos
            if tasa_ahorro >= 0.30: score += 30
            elif tasa_ahorro >= 0.20: score += 25
            elif tasa_ahorro >= 0.10: score += 20
            elif tasa_ahorro >= 0: score += 15
            else: score += max(0, 15 + (tasa_ahorro * 50))
        
        if ingresos > 0:
            ratio_deuda = deudas / ingresos if ingresos > 0 else 0
            if ratio_deuda <= 0.1: score += 20
            elif ratio_deuda <= 0.3: score += 15
            elif ratio_deuda <= 0.5: score += 10
            else: score += max(0, 10 - (ratio_deuda * 10))
        
        if ingresos > 0:
            tasa_ahorros_meta = ahorros / (ingresos * 3) if ingresos > 0 else 0
            score += min(20, tasa_ahorros_meta * 100)
        
        score = max(0, min(100, score))
        score_10 = score / 10
        
        if score >= 85: nivel, emoji, color = "EXCELENTE", "🏆", "#10b981"
        elif score >= 70: nivel, emoji, color = "MUY BIEN", "💪", "#3b82f6"
        elif score >= 50: nivel, emoji, color = "BIEN", "✅", "#f59e0b"
        elif score >= 30: nivel, emoji, color = "MEJORABLE", "⚠️", "#f97316"
        else: nivel, emoji, color = "CRÍTICO", "🚨", "#ef4444"
        
        return {"score": round(score_10, 1), "nivel": nivel, "emoji": emoji, "color": color}
    
    @staticmethod
    def generar_resumen_ejecutivo(ingresos: float, gastos: float, balance: float) -> str:
        if ingresos == 0 and gastos == 0:
            return "Aún no has registrado movimientos. Comienza agregando tus ingresos y gastos."
        if balance > 0:
            return f"🌟 Balance positivo de ${balance:,.0f}. Tus ingresos son ${ingresos:,.0f} y tus gastos ${gastos:,.0f}."
        else:
            return f"⚠️ Tus gastos (${gastos:,.0f}) superan tus ingresos (${ingresos:,.0f}) por ${abs(balance):,.0f}."
    
    @staticmethod
    def generar_comparacion_mes_anterior(ing_act: float, gas_act: float, ing_ant: float, gas_ant: float) -> str:
        if ing_ant == 0 and gas_ant == 0:
            if ing_act > 0 or gas_act > 0:
                return f"🎉 Mejora del 100%. Este mes: ingresos ${ing_act:,.0f}, gastos ${gas_act:,.0f}"
            return "Sin datos del mes anterior"
        
        var_ing = ((ing_act - ing_ant) / ing_ant * 100) if ing_ant > 0 else 0
        var_gas = ((gas_act - gas_ant) / gas_ant * 100) if gas_ant > 0 else 0
        balance_act = ing_act - gas_act
        balance_ant = ing_ant - gas_ant
        
        if balance_act > balance_ant: emoji = "📈"
        else: emoji = "📉"
        
        return f"{emoji} Ingresos: {var_ing:+.0f}%, Gastos: {var_gas:+.0f}%, Balance: ${balance_act:,.0f} vs ${balance_ant:,.0f}"
    
    @staticmethod
    def generar_alertas_personalizadas(ingresos: float, gastos: float, ahorros: float, deudas: float, metas_ahorro: List) -> List[str]:
        alertas = []
        if ahorros == 0 and ingresos > 0:
            alertas.append("No estás ahorrando nada actualmente")
        if gastos > ingresos and ingresos > 0:
            alertas.append(f"Gastas ${gastos - ingresos:,.0f} más de lo que ganas")
        if ingresos > 0 and deudas > ingresos * 0.4:
            alertas.append(f"Tus deudas (${deudas:,.0f}) superan el 40% de tus ingresos")
        return alertas[:3]
    
    @staticmethod
    def analizar_categorias_gastos(categorias: Dict, total_gastos: float) -> List[Dict]:
        if not categorias or total_gastos == 0: return []
        analisis = []
        for i, (cat, monto) in enumerate(sorted(categorias.items(), key=lambda x: x[1], reverse=True)[:5], 1):
            porcentaje = (monto / total_gastos * 100)
            insight = "Gasto esencial - optimiza con compras inteligentes" if cat in ["ALIMENTACION", "ALIMENTACIÓN"] else "Revisa si puedes reducir este gasto"
            analisis.append({"categoria": cat, "monto": monto, "porcentaje": porcentaje, "insight": insight, "es_principal": i == 1})
        return analisis
    
    @staticmethod
    def generar_consejos_personalizados(ingresos: float, gastos: float, ahorros: float, deudas: float, categorias: List[Dict]) -> List[str]:
        consejos = []
        if ahorros == 0 and ingresos > 0:
            consejos.append("🪙 Crea un fondo de emergencia (3-6 meses de gastos)")
            consejos.append(f"🎯 Meta: ahorra ${ingresos * 0.1:,.0f} el próximo mes")
        if gastos > ingresos:
            consejos.append("📉 Prioriza gastos esenciales")
        consejos.append("📊 Revisa tus finanzas semanalmente")
        consejos.append("📱 Usa la regla 50/30/20")
        return list(dict.fromkeys(consejos))[:5]
    
    @staticmethod
    def generar_meta_proximo_mes(ingresos: float, gastos: float, ahorros: float) -> str:
        if ingresos == 0: return "Registra tus primeros ingresos"
        balance = ingresos - gastos
        if balance <= 0: return "Reduce tus gastos para tener balance positivo"
        if ahorros == 0: return f"Ahorra ${ingresos * 0.1:,.0f} (10% de tus ingresos) el próximo mes"
        return f"Incrementa tu ahorro a ${ahorros * 1.2:,.0f} el próximo mes"


def _fmt_money(n: float) -> str:
    try: return f"${n:,.0f}"
    except: return "$0"


# =========================================================
# APLICACIÓN PRINCIPAL
# =========================================================
def main(page: ft.Page):
    page.title = "Mi Bolsillo Pro"
    page.theme_mode = "dark"
    page.window_width = 450
    page.window_height = 900
    page.bgcolor = "#0f172a"
    page.padding = 0
    page.scroll = ft.ScrollMode.AUTO
    
    COLORES = {
        "bg": "#0f172a", "bg_secondary": "#1e293b", "card": "#1e293b",
        "card_hover": "#334155", "input": "#334155", "border": "#475569",
        "text": "#f1f5f9", "text_secondary": "#94a3b8", "text_disabled": "#64748b",
        "primary": "#3b82f6", "success": "#10b981", "warning": "#f59e0b",
        "danger": "#ef4444", "purple": "#8b5cf6"
    }
    
    conn = sqlite3.connect("mi_bolsillo.db", check_same_thread=False)
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS movimientos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tipo TEXT NOT NULL,
            descripcion TEXT NOT NULL,
            valor REAL NOT NULL,
            fecha_full TEXT NOT NULL,
            fecha_corta TEXT,
            timestamp INTEGER NOT NULL,
            categoria TEXT
        )
    """)
    conn.commit()
    
    hoy = datetime.datetime.now()
    estado = {
        "mes": str(hoy.month).zfill(2),
        "anio": str(hoy.year),
        "dia": "",
        "vista_actual": "inicio"
    }
    
    motor_ia = MotorIA()
    
    # =========================================================
    # FUNCIONES AUXILIARES
    # =========================================================
    def toast(msg, color=COLORES["primary"]):
        page.snack_bar = ft.SnackBar(
            content=ft.Row([
                ft.Container(
                    width=32, height=32, bgcolor="#ffffff20", border_radius=16,
                    content=ft.Text("✓" if color == COLORES["success"] else "ℹ", 
                                  color="white", size=16, text_align="center"),
                ),
                ft.Text(msg, color="white", weight="bold", size=14)
            ], spacing=12, vertical_alignment=ft.CrossAxisAlignment.CENTER),
            bgcolor=color, duration=3000,
            behavior=ft.SnackBarBehavior.FLOATING,
            margin=ft.margin.all(16), shape=ft.RoundedRectangleBorder(radius=16)
        )
        page.snack_bar.open = True
        page.update()
    
    def crear_boton(texto, icono, on_click, color=COLORES["primary"], expand=False):
        return ft.Container(
            expand=expand, padding=ft.padding.symmetric(horizontal=20, vertical=12),
            bgcolor=color, border_radius=12, on_click=on_click, ink=True,
            content=ft.Row([
                ft.Text(icono, size=16),
                ft.Text(texto, color="white", weight="bold", size=14)
            ], alignment=ft.MainAxisAlignment.CENTER, spacing=8)
        )
    
    # =========================================================
    # DASHBOARD
    # =========================================================
    txt_score = ft.Text("0", size=56, weight=ft.FontWeight.BOLD, color=COLORES["text"])
    txt_nivel = ft.Text("Calculando...", size=14, color=COLORES["primary"], weight=ft.FontWeight.BOLD)
    txt_emoji_score = ft.Text("💰", size=48)
    txt_ingresos = ft.Text("$0", size=20, weight=ft.FontWeight.BOLD, color=COLORES["success"])
    txt_gastos = ft.Text("$0", size=20, weight=ft.FontWeight.BOLD, color=COLORES["danger"])
    txt_balance = ft.Text("$0", size=16, weight=ft.FontWeight.BOLD, color=COLORES["text"])
    
    card_score = ft.Container(
        margin=ft.margin.only(left=16, right=16, top=16, bottom=8),
        padding=ft.padding.all(24), border_radius=24,
        border=ft.border.all(1, COLORES["border"]),
        gradient=ft.LinearGradient(
            begin=ft.Alignment(-1, -1), end=ft.Alignment(1, 1),
            colors=["#1e293b", "#0f172a"]
        ),
        content=ft.Column([
            ft.Container(width=80, height=80, bgcolor="#3b82f620", border_radius=40, content=txt_emoji_score),
            ft.Text("Tu calificación financiera", size=14, color=COLORES["text_secondary"]),
            ft.Row([txt_score, ft.Text("/10", size=24, color=COLORES["text_disabled"])], 
                   alignment=ft.MainAxisAlignment.CENTER, spacing=5),
            txt_nivel,
            ft.Divider(height=1, color=COLORES["border"]),
            ft.Row([
                ft.Column([ft.Text("💰 Ingresos", size=11, color=COLORES["text_secondary"]), txt_ingresos], 
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                ft.Container(width=1, height=40, bgcolor=COLORES["border"]),
                ft.Column([ft.Text("💸 Gastos", size=11, color=COLORES["text_secondary"]), txt_gastos],
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER)
            ], alignment=ft.MainAxisAlignment.SPACE_EVENLY),
            ft.Container(
                padding=ft.padding.symmetric(horizontal=20, vertical=8),
                bgcolor=COLORES["bg_secondary"], border_radius=20,
                content=ft.Row([ft.Text("Balance:", size=12, color=COLORES["text_secondary"]), txt_balance], spacing=8)
            )
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=12)
    )
    
    # =========================================================
    # FILTROS
    # =========================================================
    dropdown_mes = ft.Dropdown(
        value=estado["mes"], expand=True,
        bgcolor=COLORES["input"], color=COLORES["text"],
        border_radius=12, border_color=ft.colors.TRANSPARENT,
        text_size=14, height=48,
        options=[
            ft.dropdown.Option("01", "Ene"), ft.dropdown.Option("02", "Feb"),
            ft.dropdown.Option("03", "Mar"), ft.dropdown.Option("04", "Abr"),
            ft.dropdown.Option("05", "May"), ft.dropdown.Option("06", "Jun"),
            ft.dropdown.Option("07", "Jul"), ft.dropdown.Option("08", "Ago"),
            ft.dropdown.Option("09", "Sep"), ft.dropdown.Option("10", "Oct"),
            ft.dropdown.Option("11", "Nov"), ft.dropdown.Option("12", "Dic")
        ]
    )
    
    txt_filtro_dia = ft.TextField(
        hint_text="Día", width=80,
        bgcolor=COLORES["input"], color=COLORES["text"],
        border_radius=12, border_color=ft.colors.TRANSPARENT,
        text_size=14, height=48,
        keyboard_type=ft.KeyboardType.NUMBER
    )
    
    def aplicar_filtros(e):
        estado["mes"] = dropdown_mes.value
        estado["dia"] = txt_filtro_dia.value.strip().zfill(2) if txt_filtro_dia.value and txt_filtro_dia.value.isdigit() else ""
        cargar_dashboard()
    
    barra_filtros = ft.Container(
        margin=ft.margin.only(left=16, right=16, top=8, bottom=8),
        padding=16, bgcolor=COLORES["card"], border_radius=16,
        border=ft.border.all(1, COLORES["border"]),
        content=ft.Column([
            ft.Row([
                ft.Column([
                    ft.Text(f"{dropdown_mes.value} {estado['anio']}", size=16, weight=ft.FontWeight.BOLD, color=COLORES["text"]),
                    ft.Text("Filtrar movimientos", size=11, color=COLORES["text_secondary"])
                ])
            ]),
            ft.Row([dropdown_mes, txt_filtro_dia], spacing=8),
            ft.Container(
                padding=ft.padding.symmetric(horizontal=20, vertical=12),
                bgcolor=COLORES["primary"], border_radius=12,
                on_click=aplicar_filtros, ink=True,
                content=ft.Row([
                    ft.Text("🔍", size=16),
                    ft.Text("Aplicar Filtros", color="white", weight=ft.FontWeight.BOLD, size=14)
                ], alignment=ft.MainAxisAlignment.CENTER, spacing=8)
            )
        ], spacing=12)
    )
    
    # =========================================================
    # FORMULARIO
    # =========================================================
    txt_descripcion = ft.TextField(
        hint_text="Descripción", expand=True,
        bgcolor=COLORES["input"], color=COLORES["text"],
        border_radius=12, border_color=ft.colors.TRANSPARENT,
        focused_border_color=COLORES["primary"],
        text_size=14, height=52
    )
    
    txt_valor = ft.TextField(
        hint_text="$ Valor", expand=True,
        bgcolor=COLORES["input"], color=COLORES["text"],
        border_radius=12, border_color=ft.colors.TRANSPARENT,
        focused_border_color=COLORES["primary"],
        keyboard_type=ft.KeyboardType.NUMBER, text_size=14, height=52
    )
    
    dropdown_tipo = ft.Dropdown(
        value="GASTO", expand=True,
        bgcolor=COLORES["input"], color=COLORES["text"],
        border_radius=12, border_color=ft.colors.TRANSPARENT,
        text_size=14, height=52,
        options=[
            ft.dropdown.Option("INGRESO", "💰 Ingreso"),
            ft.dropdown.Option("GASTO", "💸 Gasto")
        ]
    )
    
    txt_categoria = ft.TextField(
        hint_text="Categoría", expand=True,
        bgcolor=COLORES["input"], color=COLORES["text"],
        border_radius=12, border_color=ft.colors.TRANSPARENT,
        focused_border_color=COLORES["primary"],
        text_size=14, height=52
    )
    
    def guardar_movimiento(e):
        try:
            if not txt_valor.value:
                toast("⚠️ Ingresa un valor", COLORES["warning"])
                return
            valor = float(txt_valor.value.replace(",", ""))
            if valor <= 0:
                toast("⚠️ El valor debe ser mayor a 0", COLORES["warning"])
                return
            
            desc = (txt_descripcion.value or "SIN DESCRIPCIÓN").strip().upper()
            tipo = dropdown_tipo.value
            cat = (txt_categoria.value or "OTROS").strip().upper()
            
            ahora = datetime.datetime.now()
            cursor.execute("""
                INSERT INTO movimientos 
                (tipo, descripcion, valor, fecha_full, fecha_corta, timestamp, categoria)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (tipo, desc, valor, ahora.strftime("%Y-%m-%d"),
                  ahora.strftime("%d/%m"), int(ahora.timestamp()), cat))
            conn.commit()
            
            txt_valor.value = ""
            txt_descripcion.value = ""
            txt_categoria.value = ""
            
            toast("✅ Movimiento agregado", COLORES["success"])
            cargar_dashboard()
        except ValueError:
            toast("❌ Valor inválido", COLORES["danger"])
        except Exception as ex:
            toast(f"❌ Error: {str(ex)}", COLORES["danger"])
    
    formulario_movimiento = ft.Container(
        margin=ft.margin.only(left=16, right=16, top=8, bottom=8),
        padding=20, bgcolor=COLORES["card"], border_radius=16,
        border=ft.border.all(1, COLORES["border"]),
        content=ft.Column([
            ft.Text("📝 Nuevo Movimiento", size=18, weight=ft.FontWeight.BOLD, color=COLORES["text"]),
            txt_descripcion,
            ft.Row([dropdown_tipo, txt_categoria], spacing=8),
            ft.Row([
                txt_valor,
                ft.Container(
                    width=52, height=52, bgcolor=COLORES["primary"], border_radius=16,
                    on_click=guardar_movimiento, ink=True,
                    content=ft.Text("➕", size=24, color="white", text_align="center"),
                )
            ], spacing=8)
        ], spacing=16)
    )
    
    # =========================================================
    # LISTA MOVIMIENTOS
    # =========================================================
    lista_movimientos = ft.Column(spacing=8, scroll=ft.ScrollMode.AUTO)
    
    def eliminar_movimiento(mov_id):
        def confirmar(e):
            cursor.execute("DELETE FROM movimientos WHERE id = ?", (mov_id,))
            conn.commit()
            toast("🗑️ Eliminado", COLORES["success"])
            cargar_dashboard()
            dlg.open = False
            page.update()
        
        def cancelar(e):
            dlg.open = False
            page.update()
        
        dlg = ft.AlertDialog(
            title=ft.Text("Confirmar", color=COLORES["text"], weight=ft.FontWeight.BOLD),
            content=ft.Text("¿Eliminar este movimiento?", color=COLORES["text_secondary"]),
            bgcolor=COLORES["bg_secondary"], shape=ft.RoundedRectangleBorder(radius=16),
            actions=[
                ft.TextButton("Cancelar", on_click=cancelar),
                ft.TextButton("Eliminar", on_click=confirmar, style=ft.ButtonStyle(color=COLORES["danger"]))
            ],
            actions_alignment=ft.MainAxisAlignment.END
        )
        page.dialog = dlg
        dlg.open = True
        page.update()
    
    # =========================================================
    # VISTA IA
    # =========================================================
    columna_ia = ft.Column(spacing=16, scroll=ft.ScrollMode.AUTO)
    
    def analizar_finanzas(e):
        columna_ia.controls.clear()
        columna_ia.controls.append(
            ft.Container(
                padding=40,
                content=ft.Column([
                    ft.ProgressRing(width=50, height=50, stroke_width=4),
                    ft.Container(height=16),
                    ft.Text("Analizando tus finanzas...", size=16, color=COLORES["text"])
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER)
            )
        )
        page.update()
        time.sleep(0.5)
        columna_ia.controls.clear()
        cargar_vista_ia()
        page.update()
    
    def cargar_vista_ia():
        columna_ia.controls.clear()
        
        mes, anio = estado["mes"], estado["anio"]
        
        cursor.execute("""
            SELECT tipo, COALESCE(SUM(valor), 0) 
            FROM movimientos WHERE substr(fecha_full,1,4)=? AND substr(fecha_full,6,2)=?
            GROUP BY tipo
        """, (anio, mes))
        datos = {t: float(v) for t, v in cursor.fetchall()}
        ing, gas = datos.get("INGRESO", 0), datos.get("GASTO", 0)
        balance = ing - gas
        
        cursor.execute("SELECT COALESCE(SUM(ahorrado_actual),0) FROM ahorros")
        ahorros = float(cursor.fetchone()[0] or 0)
        
        cursor.execute("""
            SELECT categoria, SUM(valor)
            FROM movimientos WHERE tipo='GASTO' AND substr(fecha_full,1,4)=? AND substr(fecha_full,6,2)=?
            GROUP BY categoria ORDER BY SUM(valor) DESC
        """, (anio, mes))
        categorias = {c: float(v) for c, v in cursor.fetchall()}
        
        score = motor_ia.calcular_score_financiero(ing, gas, ahorros, 0)
        
        columna_ia.controls.append(
            ft.Container(
                margin=ft.margin.only(bottom=8),
                content=ft.Column([
                    ft.Text("# Mi Bolsillo", size=28, weight=ft.FontWeight.BOLD, color=COLORES["text"]),
                    ft.Text("Tu asistente financiero", size=14, color=COLORES["text_secondary"])
                ])
            )
        )
        
        columna_ia.controls.append(
            ft.Container(
                padding=24, bgcolor=score["color"], border_radius=24, margin=ft.margin.only(bottom=16),
                content=ft.Column([
                    ft.Container(
                        width=70, height=70, bgcolor="#ffffff20", border_radius=35,
                        content=ft.Text(score["emoji"], size=40, text_align="center"),
                    ),
                    ft.Row([ft.Text(f"{score['score']}/10", size=48, weight=ft.FontWeight.BOLD, color="white")], 
                          alignment=ft.MainAxisAlignment.CENTER),
                    ft.Text(score["nivel"], size=18, color="white", weight=ft.FontWeight.BOLD),
                    ft.Text("Tu calificación financiera", size=12, color="#ffffffcc")
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=8)
            )
        )
        
        columna_ia.controls.append(
            ft.Container(
                padding=20, bgcolor=COLORES["card"], border_radius=16,
                border=ft.border.all(1, COLORES["border"]), margin=ft.margin.only(bottom=8),
                content=ft.Column([
                    ft.Row([
                        ft.Container(
                            width=40, height=40, bgcolor=f"{COLORES['primary']}20", border_radius=20,
                            content=ft.Text("📋", size=20, color=COLORES["primary"], text_align="center"),
                        ),
                        ft.Text("Resumen Ejecutivo", size=18, weight=ft.FontWeight.BOLD, color=COLORES["text"])
                    ]),
                    ft.Container(height=8),
                    ft.Text(motor_ia.generar_resumen_ejecutivo(ing, gas, balance), 
                           size=14, color=COLORES["text_secondary"])
                ])
            )
        )
        
        mes_ant = str(int(mes)-1).zfill(2) if int(mes) > 1 else "12"
        anio_ant = anio if int(mes) > 1 else str(int(anio)-1)
        cursor.execute("""
            SELECT tipo, COALESCE(SUM(valor), 0) 
            FROM movimientos WHERE substr(fecha_full,1,4)=? AND substr(fecha_full,6,2)=?
            GROUP BY tipo
        """, (anio_ant, mes_ant))
        ant = {t: float(v) for t, v in cursor.fetchall()}
        
        columna_ia.controls.append(
            ft.Container(
                padding=20, bgcolor=COLORES["card"], border_radius=16,
                border=ft.border.all(1, COLORES["border"]), margin=ft.margin.only(bottom=8),
                content=ft.Column([
                    ft.Row([
                        ft.Container(
                            width=40, height=40, bgcolor=f"{COLORES['success']}20", border_radius=20,
                            content=ft.Text("📊", size=20, color=COLORES["success"], text_align="center"),
                        ),
                        ft.Text("vs Mes Anterior", size=18, weight=ft.FontWeight.BOLD, color=COLORES["text"])
                    ]),
                    ft.Container(height=8),
                    ft.Text(
                        motor_ia.generar_comparacion_mes_anterior(ing, gas, ant.get("INGRESO",0), ant.get("GASTO",0)),
                        size=14, color=COLORES["text_secondary"]
                    )
                ])
            )
        )
        
        metas = [{"nombre": m[0]} for m in cursor.execute("SELECT nombre FROM ahorros").fetchall()]
        alertas = motor_ia.generar_alertas_personalizadas(ing, gas, ahorros, 0, metas)
        if alertas:
            columna_ia.controls.append(
                ft.Container(
                    padding=20, bgcolor="#7f1d1d", border_radius=16,
                    border=ft.border.all(1, "#991b1b"), margin=ft.margin.only(bottom=8),
                    content=ft.Column([
                        ft.Row([
                            ft.Container(
                                width=40, height=40, bgcolor="#ffffff20", border_radius=20,
                                content=ft.Text("🚨", size=20, color="white", text_align="center"),
                            ),
                            ft.Text("Alertas", size=18, weight=ft.FontWeight.BOLD, color="white")
                        ]),
                        ft.Container(height=8),
                        ft.Column([
                            ft.Row([ft.Text("•", size=16, color="white"), ft.Text(a, size=13, color="white", expand=True)])
                            for a in alertas
                        ], spacing=8)
                    ])
                )
            )
        
        cats = motor_ia.analizar_categorias_gastos(categorias, gas)
        if cats:
            columna_ia.controls.append(
                ft.Container(
                    padding=20, bgcolor=COLORES["card"], border_radius=16,
                    border=ft.border.all(1, COLORES["border"]), margin=ft.margin.only(bottom=8),
                    content=ft.Column([
                        ft.Row([
                            ft.Container(
                                width=40, height=40, bgcolor=f"{COLORES['warning']}20", border_radius=20,
                                content=ft.Text("💰", size=20, color=COLORES["warning"], text_align="center"),
                            ),
                            ft.Text("Dónde gastas más", size=18, weight=ft.FontWeight.BOLD, color=COLORES["text"])
                        ]),
                        ft.Container(height=8),
                        ft.Column([
                            ft.Container(
                                padding=16, bgcolor=COLORES["input"], border_radius=12,
                                margin=ft.margin.only(bottom=8),
                                content=ft.Column([
                                    ft.Row([
                                        ft.Text(f"{i+1}. {c['categoria']}", size=16, weight=ft.FontWeight.BOLD, color=COLORES["text"]),
                                        ft.Text(_fmt_money(c['monto']), size=16, weight=ft.FontWeight.BOLD, color=COLORES["danger"])
                                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                                    ft.Text(f"{c['porcentaje']:.1f}% de tus gastos", size=12, color=COLORES["text_secondary"]),
                                    ft.Text(c['insight'], size=12, color=COLORES["text_secondary"], italic=True)
                                ])
                            ) for i, c in enumerate(cats[:3])
                        ])
                    ])
                )
            )
        
        consejos = motor_ia.generar_consejos_personalizados(ing, gas, ahorros, 0, cats)
        columna_ia.controls.append(
            ft.Container(
                padding=20, bgcolor=COLORES["card"], border_radius=16,
                border=ft.border.all(1, COLORES["border"]), margin=ft.margin.only(bottom=8),
                content=ft.Column([
                    ft.Row([
                        ft.Container(
                            width=40, height=40, bgcolor=f"{COLORES['purple']}20", border_radius=20,
                            content=ft.Text("💡", size=20, color=COLORES["purple"], text_align="center"),
                        ),
                        ft.Text("Consejos para ti", size=18, weight=ft.FontWeight.BOLD, color=COLORES["text"])
                    ]),
                    ft.Container(height=8),
                    ft.Column([
                        ft.Row([
                            ft.Container(width=6, height=6, bgcolor=COLORES["purple"], border_radius=3, margin=ft.margin.only(right=8)),
                            ft.Text(c, size=13, color=COLORES["text_secondary"], expand=True)
                        ]) for c in consejos[:4]
                    ], spacing=12)
                ])
            )
        )
        
        columna_ia.controls.append(
            ft.Container(
                padding=20,
                gradient=ft.LinearGradient(
                    begin=ft.Alignment(-1, -1), end=ft.Alignment(1, 1),
                    colors=[COLORES["success"], "#059669"]
                ),
                border_radius=16, margin=ft.margin.only(bottom=16),
                content=ft.Column([
                    ft.Row([
                        ft.Container(
                            width=48, height=48, bgcolor="#ffffff20", border_radius=24,
                            content=ft.Text("🎯", size=24, color="white", text_align="center"),
                        ),
                        ft.Column([
                            ft.Text("Meta para el próximo mes", size=18, weight=ft.FontWeight.BOLD, color="white"),
                            ft.Text(motor_ia.generar_meta_proximo_mes(ing, gas, ahorros), 
                                   size=14, color="#ffffffdd")
                        ], spacing=4)
                    ], spacing=16)
                ])
            )
        )
        
        page.update()
    
    # =========================================================
    # VISTA IA CON BOTÓN
    # =========================================================
    vista_ia = ft.Container(
        expand=True,
        content=ft.Column([
            ft.Container(height=16),
            ft.Container(
                padding=ft.padding.symmetric(horizontal=16),
                content=ft.Column([
                    ft.Container(
                        padding=20, bgcolor=COLORES["card"], border_radius=16,
                        border=ft.border.all(1, COLORES["border"]), margin=ft.margin.only(bottom=16),
                        content=ft.Column([
                            ft.Container(
                                width=80, height=80, bgcolor=f"{COLORES['primary']}20", border_radius=40,
                                content=ft.Text("🤖", size=40, color=COLORES["primary"], text_align="center"),
                            ),
                            ft.Container(height=8),
                            ft.Text("Análisis con IA", size=20, weight=ft.FontWeight.BOLD, color=COLORES["text"]),
                            ft.Text("Obtén recomendaciones personalizadas", 
                                   size=14, color=COLORES["text_secondary"], text_align="center"),
                            ft.Container(height=8),
                            ft.Container(
                                padding=ft.padding.symmetric(horizontal=30, vertical=15),
                                bgcolor=COLORES["primary"], border_radius=30,
                                on_click=analizar_finanzas, ink=True,
                                content=ft.Row([
                                    ft.Text("🔍", size=20),
                                    ft.Text("Analizar Mis Finanzas", color="white", weight=ft.FontWeight.BOLD, size=16)
                                ], alignment=ft.MainAxisAlignment.CENTER, spacing=10)
                            )
                        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=8)
                    ),
                    columna_ia
                ])
            ),
            ft.Container(height=80)
        ], scroll=ft.ScrollMode.AUTO)
    )
    
    # =========================================================
    # CARGAR DASHBOARD
    # =========================================================
    def cargar_dashboard():
        lista_movimientos.controls.clear()
        
        mes, anio, dia = estado["mes"], estado["anio"], estado["dia"]
        query = """
            SELECT id, tipo, descripcion, valor, fecha_corta, categoria
            FROM movimientos
            WHERE substr(fecha_full,1,4)=? AND substr(fecha_full,6,2)=?
        """
        params = [anio, mes]
        if dia:
            query += " AND substr(fecha_full,9,2)=?"
            params.append(dia)
        query += " ORDER BY timestamp DESC"
        
        cursor.execute(query, params)
        movs = cursor.fetchall()
        
        ing_total = gas_total = 0
        
        for mov in movs:
            mid, tipo, desc, val, fecha, cat = mov
            val = float(val)
            
            if tipo == "INGRESO":
                ing_total += val
                color, icono, signo = COLORES["success"], "💰", "+"
            else:
                gas_total += val
                color, icono, signo = COLORES["danger"], "💸", "-"
            
            lista_movimientos.controls.append(
                ft.Container(
                    bgcolor=COLORES["card"], border_radius=12, padding=12,
                    border=ft.border.all(1, COLORES["border"]), margin=ft.margin.only(bottom=8),
                    content=ft.Row([
                        ft.Row([
                            ft.Container(
                                width=44, height=44, bgcolor=f"{color}20", border_radius=12,
                                content=ft.Text(icono, size=22, color=color, text_align="center"),
                            ),
                            ft.Column([
                                ft.Text(desc, size=14, weight=ft.FontWeight.BOLD, color=COLORES["text"]),
                                ft.Row([
                                    ft.Container(
                                        padding=ft.padding.symmetric(horizontal=6, vertical=2),
                                        bgcolor=f"{COLORES['primary']}20", border_radius=4,
                                        content=ft.Text(fecha, size=10, color=COLORES["text_secondary"])
                                    ),
                                    ft.Container(
                                        padding=ft.padding.symmetric(horizontal=6, vertical=2),
                                        bgcolor=f"{COLORES['purple']}20", border_radius=4,
                                        content=ft.Text(cat or "OTROS", size=10, color=COLORES["text_secondary"])
                                    )
                                ], spacing=8)
                            ], spacing=4)
                        ], spacing=12),
                        ft.Row([
                            ft.Text(f"{signo}{_fmt_money(val)}", size=16, weight=ft.FontWeight.BOLD, color=color),
                            ft.Container(
                                width=36, height=36, bgcolor=f"{COLORES['danger']}20", border_radius=10,
                                on_click=lambda e, mid=mid: eliminar_movimiento(mid), ink=True,
                                content=ft.Text("🗑️", size=16, color=COLORES["danger"], text_align="center"),
                            )
                        ], spacing=8)
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
                )
            )
        
        if not movs:
            lista_movimientos.controls.append(
                ft.Container(
                    padding=40,
                    content=ft.Column([
                        ft.Container(
                            width=80, height=80, bgcolor="#ffffff10", border_radius=40,
                            content=ft.Text("📊", size=40, text_align="center"),
                        ),
                        ft.Container(height=16),
                        ft.Text("Sin movimientos", size=18, weight=ft.FontWeight.BOLD, color=COLORES["text"]),
                        ft.Text("Agrega tu primer movimiento", size=13, color=COLORES["text_secondary"])
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER)
                )
            )
        
        balance = ing_total - gas_total
        txt_ingresos.value = _fmt_money(ing_total)
        txt_gastos.value = _fmt_money(gas_total)
        txt_balance.value = _fmt_money(balance)
        
        cursor.execute("SELECT COALESCE(SUM(ahorrado_actual),0) FROM ahorros")
        ahorros = float(cursor.fetchone()[0] or 0)
        
        score = motor_ia.calcular_score_financiero(ing_total, gas_total, ahorros, 0)
        txt_score.value = f"{score['score']}"
        txt_nivel.value = score["nivel"]
        txt_emoji_score.value = score["emoji"]
        
        page.update()
    
    # =========================================================
    # VISTAS
    # =========================================================
    vista_inicio = ft.Container(
        expand=True,
        content=ft.Column([
            card_score,
            barra_filtros,
            formulario_movimiento,
            ft.Container(
                padding=ft.padding.symmetric(horizontal=16),
                content=ft.Column([
                    ft.Row([
                        ft.Text("Historial", size=18, weight=ft.FontWeight.BOLD, color=COLORES["text"]),
                        ft.Text(f"{len(movs) if 'movs' in dir() else 0} movimientos", 
                               size=12, color=COLORES["text_secondary"])
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    lista_movimientos
                ])
            ),
            ft.Container(height=20)
        ], scroll=ft.ScrollMode.AUTO)
    )
    
    vista_ahorros = ft.Container(
        expand=True,
        content=ft.Column([
            ft.Container(height=100),
            ft.Container(
                width=120, height=120,
                gradient=ft.LinearGradient(
                    begin=ft.Alignment(-1, -1), end=ft.Alignment(1, 1),
                    colors=[COLORES["success"], "#059669"]
                ),
                border_radius=60,
                content=ft.Text("🎯", size=60, color="white", text_align="center"),
            ),
            ft.Container(height=24),
            ft.Text("Próximamente", size=28, weight=ft.FontWeight.BOLD, color=COLORES["text"]),
            ft.Text("Sección de ahorros", size=14, color=COLORES["text_secondary"], text_align="center")
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER)
    )
    
    vista_deudas = ft.Container(
        expand=True,
        content=ft.Column([
            ft.Container(height=100),
            ft.Container(
                width=120, height=120,
                gradient=ft.LinearGradient(
                    begin=ft.Alignment(-1, -1), end=ft.Alignment(1, 1),
                    colors=[COLORES["danger"], "#dc2626"]
                ),
                border_radius=60,
                content=ft.Text("💳", size=60, color="white", text_align="center"),
            ),
            ft.Container(height=24),
            ft.Text("Próximamente", size=28, weight=ft.FontWeight.BOLD, color=COLORES["text"]),
            ft.Text("Sección de deudas", size=14, color=COLORES["text_secondary"], text_align="center")
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER)
    )
    
    # =========================================================
    # NAVEGACIÓN
    # =========================================================
    contenedor = ft.Container(expand=True, content=vista_inicio)
    
    def cambiar_vista(vista, e=None):
        if estado["vista_actual"] == vista:
            return
        
        if vista == "inicio":
            contenedor.content = vista_inicio
            cargar_dashboard()
        elif vista == "ahorros":
            contenedor.content = vista_ahorros
        elif vista == "deudas":
            contenedor.content = vista_deudas
        elif vista == "ia":
            contenedor.content = vista_ia
            columna_ia.controls.clear()
        
        estado["vista_actual"] = vista
        page.update()
    
    def crear_boton_nav(icono, texto, vista, activo=False):
        return ft.Container(
            expand=True,
            padding=ft.padding.symmetric(vertical=12),
            on_click=lambda e: cambiar_vista(vista, e),
            bgcolor=f"{COLORES['primary']}20" if activo else "transparent",
            border_radius=12,
            ink=True,
            content=ft.Column([
                ft.Text(icono, size=22, color=COLORES["primary"] if activo else COLORES["text_secondary"]),
                ft.Text(texto, size=11, color=COLORES["text"] if activo else COLORES["text_secondary"])
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=4)
        )
    
    botones = {
        "inicio": crear_boton_nav("🏠", "Inicio", "inicio", True),
        "ahorros": crear_boton_nav("🎯", "Ahorros", "ahorros"),
        "deudas": crear_boton_nav("📒", "Deudas", "deudas"),
        "ia": crear_boton_nav("🤖", "IA", "ia")
    }
    
    barra_nav = ft.Container(
        bgcolor=COLORES["bg_secondary"],
        padding=ft.padding.only(left=8, right=8, top=8, bottom=16),
        border=ft.border.only(top=ft.BorderSide(1, COLORES["border"])),
        content=ft.Row(list(botones.values()), alignment=ft.MainAxisAlignment.SPACE_AROUND)
    )
    
    page.add(ft.Column([contenedor, barra_nav], expand=True, spacing=0))
    cargar_dashboard()


# =========================================================
# PARA RENDER - NIVEL SUPERIOR
# =========================================================
app = ft.app(target=main)
