import flet as ft
import sqlite3
import datetime
import time
import math
from typing import Dict, List, Tuple, Optional

# =========================================================
# MOTOR DE IA MEJORADO - ANÁLISIS CONVERSACIONAL
# =========================================================
class MotorIA:
    """Motor de Inteligencia Artificial para análisis financiero conversacional"""
    
    @staticmethod
    def calcular_score_financiero(ingresos: float, gastos: float, ahorros: float, deudas: float) -> Dict:
        """Calcula un score financiero detallado (0-100) convertido a escala 0-10"""
        score = 50  # Base
        
        # Factor 1: Tasa de ahorro (30 puntos)
        if ingresos > 0:
            tasa_ahorro = (ingresos - gastos) / ingresos
            if tasa_ahorro >= 0.30:
                score += 30
            elif tasa_ahorro >= 0.20:
                score += 25
            elif tasa_ahorro >= 0.10:
                score += 20
            elif tasa_ahorro >= 0:
                score += 15
            else:
                score += max(0, 15 + (tasa_ahorro * 50))
        
        # Factor 2: Relación deuda/ingreso (20 puntos)
        if ingresos > 0:
            ratio_deuda = deudas / ingresos if ingresos > 0 else 0
            if ratio_deuda <= 0.1:
                score += 20
            elif ratio_deuda <= 0.3:
                score += 15
            elif ratio_deuda <= 0.5:
                score += 10
            else:
                score += max(0, 10 - (ratio_deuda * 10))
        
        # Factor 3: Disciplina de ahorro (20 puntos)
        if ingresos > 0:
            tasa_ahorros_meta = ahorros / (ingresos * 3) if ingresos > 0 else 0
            score += min(20, tasa_ahorros_meta * 100)
        
        score = max(0, min(100, score))
        
        # Convertir a escala 0-10
        score_10 = score / 10
        
        # Clasificación
        if score >= 85:
            nivel = "EXCELENTE"
            emoji = "🏆"
            color = "#10b981"
        elif score >= 70:
            nivel = "MUY BIEN"
            emoji = "💪"
            color = "#3b82f6"
        elif score >= 50:
            nivel = "BIEN"
            emoji = "✅"
            color = "#f59e0b"
        elif score >= 30:
            nivel = "MEJORABLE"
            emoji = "⚠️"
            color = "#f97316"
        else:
            nivel = "CRÍTICO"
            emoji = "🚨"
            color = "#ef4444"
        
        return {
            "score": round(score_10, 1),
            "score_100": round(score, 1),
            "nivel": nivel,
            "emoji": emoji,
            "color": color
        }
    
    @staticmethod
    def generar_resumen_ejecutivo(ingresos: float, gastos: float, balance: float) -> str:
        """Genera un resumen ejecutivo natural y conversacional"""
        if ingresos == 0 and gastos == 0:
            return "Aún no has registrado movimientos financieros. Comienza agregando tus ingresos y gastos para obtener un análisis personalizado."
        
        # Determinar estado financiero
        if balance > 0:
            if balance > ingresos * 0.5:
                estado = "excelente"
                adj = "muy sólida"
                emoji = "🌟"
            elif balance > ingresos * 0.3:
                estado = "muy buena"
                adj = "saludable"
                emoji = "💪"
            elif balance > ingresos * 0.1:
                estado = "buena"
                adj = "positiva"
                emoji = "👍"
            else:
                estado = "estable"
                adj = "moderada"
                emoji = "📊"
        else:
            estado = "preocupante"
            adj = "negativa"
            emoji = "⚠️"
        
        # Calcular tasa de ahorro
        tasa_ahorro = (balance / ingresos * 100) if ingresos > 0 else 0
        
        # Generar texto según contexto
        if ingresos > 0 and gastos == 0:
            return f"{emoji} Tu situación financiera es {adj}, con ingresos totales de {_fmt_money(ingresos)} y sin gastos registrados, lo que te deja un balance de {_fmt_money(balance)}. ¡Estás ahorrando el 100% de tus ingresos! Sin embargo, asegúrate de estar registrando todos tus gastos para tener una imagen real."
        
        elif gastos > ingresos:
            deficit = gastos - ingresos
            return f"{emoji} Alerta: tus gastos ({_fmt_money(gastos)}) superan tus ingresos ({_fmt_money(ingresos)}) por {_fmt_money(deficit)}. Es importante reducir gastos o aumentar ingresos para evitar deudas."
        
        else:
            return f"{emoji} Tu situación financiera actual es {adj}, con ingresos totales de {_fmt_money(ingresos)} y gastos controlados de {_fmt_money(gastos)}, lo que te deja un balance positivo de {_fmt_money(balance)}. Tu tasa de ahorro es del {tasa_ahorro:.1f}%."
    
    @staticmethod
    def generar_comparacion_mes_anterior(ingresos_actual: float, gastos_actual: float, 
                                        ingresos_anterior: float, gastos_anterior: float) -> str:
        """Compara el mes actual con el anterior de forma natural"""
        
        # Si no hay datos del mes anterior
        if ingresos_anterior == 0 and gastos_anterior == 0:
            if ingresos_actual > 0 or gastos_actual > 0:
                return f"Comparado con el mes anterior, has tenido una mejora del 100%, ya que en el mes anterior no reportaste ingresos ni gastos. Este mes, tus ingresos son {_fmt_money(ingresos_actual)} y tus gastos son {_fmt_money(gastos_actual)}."
            else:
                return "No hay datos suficientes para comparar con el mes anterior. Ambos meses no tienen movimientos registrados."
        
        # Calcular variaciones
        var_ingresos = ((ingresos_actual - ingresos_anterior) / ingresos_anterior * 100) if ingresos_anterior > 0 else 0
        var_gastos = ((gastos_actual - gastos_anterior) / gastos_anterior * 100) if gastos_anterior > 0 else 0
        balance_actual = ingresos_actual - gastos_actual
        balance_anterior = ingresos_anterior - gastos_anterior
        var_balance = ((balance_actual - balance_anterior) / balance_anterior * 100) if balance_anterior != 0 else 0
        
        # Generar frases según tendencias
        frases = []
        
        # Análisis de ingresos
        if var_ingresos > 20:
            frases.append(f"tus ingresos aumentaron significativamente ({var_ingresos:.0f}%)")
        elif var_ingresos > 5:
            frases.append(f"tus ingresos subieron un {var_ingresos:.0f}%")
        elif var_ingresos < -20:
            frases.append(f"tus ingresos cayeron drásticamente ({var_ingresos:.0f}%)")
        elif var_ingresos < -5:
            frases.append(f"tus ingresos disminuyeron un {var_ingresos:.0f}%")
        elif abs(var_ingresos) <= 5:
            frases.append("tus ingresos se mantuvieron estables")
        
        # Análisis de gastos
        if var_gastos > 20:
            frases.append(f"tus gastos se dispararon ({var_gastos:.0f}%)")
        elif var_gastos > 5:
            frases.append(f"tus gastos aumentaron un {var_gastos:.0f}%")
        elif var_gastos < -20:
            frases.append(f"redujiste tus gastos drásticamente ({var_gastos:.0f}%)")
        elif var_gastos < -5:
            frases.append(f"lograste reducir tus gastos un {var_gastos:.0f}%")
        elif abs(var_gastos) <= 5:
            frases.append("mantuviste tus gastos bajo control")
        
        # Análisis de balance
        if var_balance > 20:
            tendencia = "mucho mejor"
            emoji = "🎉"
        elif var_balance > 5:
            tendencia = "mejor"
            emoji = "📈"
        elif var_balance < -20:
            tendencia = "mucho peor"
            emoji = "📉"
        elif var_balance < -5:
            tendencia = "peor"
            emoji = "⚠️"
        else:
            tendencia = "similar"
            emoji = "➡️"
        
        # Construir oración
        if frases:
            analisis = f"{emoji} Comparado con el mes anterior, " + ", ".join(frases) + f". Tu situación financiera es {tendencia}, pasando de {_fmt_money(balance_anterior)} a {_fmt_money(balance_actual)}."
        else:
            analisis = f"{emoji} En comparación con el mes anterior, tu situación financiera es {tendencia}, con un balance de {_fmt_money(balance_actual)} vs {_fmt_money(balance_anterior)}."
        
        return analisis
    
    @staticmethod
    def generar_alertas_personalizadas(ingresos: float, gastos: float, ahorros: float, 
                                      deudas: float, metas_ahorro: List, tendencias: Dict = None) -> List[str]:
        """Genera alertas contextuales y personalizadas"""
        alertas = []
        
        # Alerta de ahorro cero
        if ahorros == 0 and ingresos > 0:
            alertas.append("No estás ahorrando nada actualmente, lo cual es crucial para tu estabilidad financiera a largo plazo.")
        
        # Alerta de gastos mayores a ingresos
        if gastos > ingresos and ingresos > 0:
            deficit = gastos - ingresos
            alertas.append(f"Estás gastando {_fmt_money(deficit)} más de lo que ganas. Revisa tus gastos urgentemente.")
        
        # Alerta de deudas altas
        if ingresos > 0 and deudas > ingresos * 0.4:
            alertas.append(f"Tus deudas ({_fmt_money(deudas)}) representan más del 40% de tus ingresos. Prioriza pagarlas.")
        
        # Alerta de metas de ahorro
        if metas_ahorro and ahorros == 0:
            meta = metas_ahorro[0]
            alertas.append(f"Tienes una meta de ahorro '{meta['nombre']}' pero aún no has comenzado a ahorrar para ella.")
        
        return alertas[:3]  # Máximo 3 alertas
    
    @staticmethod
    def analizar_categorias_gastos(categorias: Dict, total_gastos: float) -> List[Dict]:
        """Analiza categorías de gasto con insights detallados"""
        if not categorias or total_gastos == 0:
            return []
        
        analisis = []
        
        # Ordenar por monto
        categorias_ordenadas = sorted(categorias.items(), key=lambda x: x[1], reverse=True)
        
        for i, (cat, monto) in enumerate(categorias_ordenadas[:5], 1):
            porcentaje = (monto / total_gastos * 100)
            
            # Insight específico por categoría
            if cat == "ALIMENTACION" or cat == "ALIMENTACIÓN":
                insight = "Este gasto es esencial, pero podrías optimizarlo comparando precios o preparando más comidas en casa."
            elif cat == "TRANSPORTE":
                insight = "Considera opciones como transporte público o compartir viajes para reducir este gasto."
            elif cat == "ENTRETENIMIENTO":
                insight = "Está bien darse gustos, pero busca alternativas gratuitas o más económicas."
            elif cat == "SERVICIOS":
                insight = "Revisa si puedes reducir consumos o cambiar a planes más económicos."
            elif cat == "ROPA":
                insight = "Evalúa si son compras necesarias o si puedes esperar ofertas."
            elif cat == "SALUD":
                insight = "Invertir en salud es importante, revisa si tu seguro cubre más servicios."
            else:
                insight = "Revisa si este gasto se ajusta a tu presupuesto mensual."
            
            analisis.append({
                "categoria": cat,
                "monto": monto,
                "porcentaje": porcentaje,
                "insight": insight,
                "es_principal": i == 1
            })
        
        return analisis
    
    @staticmethod
    def generar_consejos_personalizados(ingresos: float, gastos: float, ahorros: float,
                                       deudas: float, categorias: List[Dict]) -> List[str]:
        """Genera consejos específicos basados en el perfil del usuario"""
        consejos = []
        
        # Consejos de ahorro
        if ahorros == 0 and ingresos > 0:
            consejos.append("Considere establecer una meta de ahorro mensual, aunque sea pequeña, para comenzar a construir un fondo de emergencias.")
            consejos.append(f"Ahorra al menos el 10% de tus ingresos mensuales, lo que sería {_fmt_money(ingresos * 0.1)} para el próximo mes.")
        elif ingresos > 0:
            tasa_ahorro = (ingresos - gastos) / ingresos * 100
            if tasa_ahorro < 10:
                consejos.append(f"Tu tasa de ahorro actual es del {tasa_ahorro:.1f}%. Intenta aumentarla gradualmente hasta llegar al 20%.")
        
        # Consejos de gastos
        if gastos > ingresos:
            consejos.append("Prioriza tus gastos esenciales y elimina aquellos que no sean necesarios temporalmente.")
        
        # Consejos por categorías
        for cat in categorias[:2]:  # Top 2 categorías
            if cat["categoria"] == "ALIMENTACION":
                consejos.append("Revisa tus gastos de alimentación para identificar oportunidades de compra más económicas o de preparar más comidas en casa.")
            elif cat["categoria"] == "ENTRETENIMIENTO":
                consejos.append("Busca opciones de entretenimiento gratuitas en tu ciudad: parques, museos, eventos culturales.")
            elif cat["categoria"] == "TRANSPORTE":
                consejos.append("Evalúa si puedes usar más transporte público o compartir viajes para reducir costos.")
        
        # Consejos de ingresos
        if ingresos < 1000:
            consejos.append("Considera buscar fuentes adicionales de ingresos: trabajos freelance, ventas por internet, o cursos para mejorar tus habilidades.")
        elif ingresos < 3000:
            consejos.append("Piensa en diversificar tus ingresos, tal vez explorando trabajos freelance o inversiones de bajo riesgo.")
        
        # Consejos generales
        consejos.append("Planea realizar una revisión mensual de tus finanzas para asegurar que mantienes el control de tus gastos y ahorros.")
        consejos.append("Usa la regla 50/30/20: 50% necesidades, 30% deseos, 20% ahorro e inversión.")
        
        # Eliminar duplicados y limitar
        consejos_unicos = []
        for c in consejos:
            if c not in consejos_unicos:
                consejos_unicos.append(c)
        
        return consejos_unicos[:5]  # Top 5 consejos
    
    @staticmethod
    def generar_meta_proximo_mes(ingresos: float, gastos: float, ahorros: float) -> str:
        """Genera una meta SMART para el próximo mes"""
        if ingresos == 0:
            return "Registra tus primeros ingresos este mes para comenzar tu camino financiero."
        
        balance = ingresos - gastos
        
        if balance <= 0:
            return "Tu meta para el próximo mes es reducir tus gastos para tener un balance positivo. Empieza identificando gastos no esenciales."
        else:
            ahorro_recomendado = balance * 0.5
            if ahorros == 0:
                return f"Ahorra al menos el 10% de tus ingresos mensuales, lo que sería {_fmt_money(ingresos * 0.1)} para el próximo mes."
            else:
                return f"Incrementa tu ahorro en un 20% el próximo mes. De {_fmt_money(ahorros)} a {_fmt_money(ahorros * 1.2)}."


# =========================================================
# UTILIDADES
# =========================================================
def _fmt_money(n: float) -> str:
    """Formatea número como dinero"""
    try:
        return f"${n:,.0f}"
    except:
        return "$0"


# =========================================================
# APLICACIÓN PRINCIPAL - VERSIÓN FINAL 100% CORREGIDA
# =========================================================
def main(page: ft.Page):
    # =========================================================
    # Configuración BÁSICA
    # =========================================================
    page.title = "Mi Bolsillo Pro"
    page.theme_mode = "dark"
    page.window_width = 450
    page.window_height = 900
    page.bgcolor = "#0f172a"
    page.padding = 0
    page.scroll = ft.ScrollMode.AUTO
    
    # =========================================================
    # PALETA DE COLORES - MEJORADA
    # =========================================================
    COLORES = {
        "bg": "#0f172a",
        "bg_secondary": "#1e293b",
        "card": "#1e293b",
        "card_hover": "#334155",
        "input": "#334155",
        "border": "#475569",
        "text": "#f1f5f9",
        "text_secondary": "#94a3b8",
        "text_disabled": "#64748b",
        "primary": "#3b82f6",
        "success": "#10b981",
        "warning": "#f59e0b",
        "danger": "#ef4444",
        "purple": "#8b5cf6",
        "pink": "#ec4899",
        "cyan": "#06b6d4"
    }
    
    # =========================================================
    # Base de datos
    # =========================================================
    conn = sqlite3.connect("mi_bolsillo_pro.db", check_same_thread=False)
    cursor = conn.cursor()
    
    # Crear tablas
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
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ahorros (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            meta_total REAL NOT NULL,
            ahorrado_actual REAL DEFAULT 0,
            icono TEXT DEFAULT '🐷',
            fecha_creacion TEXT
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS deudas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            monto_total REAL NOT NULL,
            monto_pagado REAL DEFAULT 0,
            tipo_deuda TEXT NOT NULL,
            fecha_creacion TEXT
        )
    """)
    
    conn.commit()
    
    # =========================================================
    # Estado global
    # =========================================================
    hoy = datetime.datetime.now()
    estado = {
        "mes": str(hoy.month).zfill(2),
        "anio": str(hoy.year),
        "dia": "",
        "vista_actual": "inicio"
    }
    
    motor_ia = MotorIA()
    
    # =========================================================
    # Funciones auxiliares
    # =========================================================
    def toast(mensaje: str, color: str = COLORES["primary"], duracion: int = 3000):
        """Muestra notificación toast con diseño mejorado"""
        page.snack_bar = ft.SnackBar(
            content=ft.Row(
                controls=[
                    ft.Container(
                        width=32, height=32,
                        bgcolor="#ffffff20",
                        border_radius=16,
                        content=ft.Text("✓" if color == COLORES["success"] else "ℹ", 
                                      color="white", size=16, text_align="center"),
                    ),
                    ft.Text(mensaje, color="white", weight="bold", size=14)
                ],
                spacing=12,
                vertical_alignment=ft.CrossAxisAlignment.CENTER
            ),
            bgcolor=color,
            duration=duracion,
            behavior=ft.SnackBarBehavior.FLOATING,
            margin=ft.margin.all(16),
            shape=ft.RoundedRectangleBorder(radius=16)
        )
        page.snack_bar.open = True
        page.update()
    
    def crear_boton(texto: str, icono: str, on_click, color: str = COLORES["primary"], expand: bool = False):
        """Crea botón estilizado"""
        return ft.Container(
            expand=expand,
            padding=ft.padding.symmetric(horizontal=20, vertical=12),
            bgcolor=color,
            border_radius=12,
            on_click=on_click,
            ink=True,
            content=ft.Row(
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=8,
                controls=[
                    ft.Text(icono, size=16),
                    ft.Text(texto, color="white", weight="bold", size=14)
                ]
            )
        )
    
    def crear_card(titulo: str, contenido, icono: str = ""):
        """Crea tarjeta estilizada"""
        return ft.Container(
            bgcolor=COLORES["card"],
            border_radius=16,
            padding=20,
            border=ft.border.all(1, COLORES["border"]),
            content=ft.Column(
                spacing=12,
                controls=[
                    ft.Row(
                        controls=[
                            ft.Text(icono, size=20) if icono else ft.Container(),
                            ft.Text(titulo, size=16, weight="bold", color=COLORES["text"])
                        ],
                        spacing=8
                    ) if titulo else ft.Container(height=0),
                    contenido
                ]
            )
        )
    
    # =========================================================
    # Dashboard Principal - COLORES CORREGIDOS
    # =========================================================
    txt_score = ft.Text("0", size=56, weight="bold", color=COLORES["text"])
    txt_nivel = ft.Text("Calculando...", size=14, color=COLORES["primary"], weight="bold")
    txt_emoji_score = ft.Text("💰", size=48)
    
    txt_ingresos_total = ft.Text("$0", size=20, weight="bold", color=COLORES["success"])
    txt_gastos_total = ft.Text("$0", size=20, weight="bold", color=COLORES["danger"])
    txt_balance = ft.Text("$0", size=16, weight="bold", color=COLORES["text"])
    
    card_score = ft.Container(
        margin=ft.margin.only(left=16, right=16, top=16, bottom=8),
        padding=ft.padding.all(24),
        border_radius=24,
        border=ft.border.all(1, COLORES["border"]),
        gradient=ft.LinearGradient(
            begin=ft.Alignment(-1, -1),
            end=ft.Alignment(1, 1),
            colors=["#1e293b", "#0f172a"]
        ),
        shadow=ft.BoxShadow(
            spread_radius=0,
            blur_radius=20,
            color="#00000040",
            offset=ft.Offset(0, 4)
        ),
        content=ft.Column(
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=12,
            controls=[
                ft.Container(
                    width=80, height=80,
                    bgcolor="#3b82f620",
                    border_radius=40,
                    content=txt_emoji_score,
                ),
                ft.Text("Tu calificación financiera", size=14, color=COLORES["text_secondary"]),
                ft.Row(
                    alignment=ft.MainAxisAlignment.CENTER,
                    vertical_alignment=ft.CrossAxisAlignment.END,
                    controls=[
                        txt_score,
                        ft.Text("/10", size=24, color=COLORES["text_disabled"])
                    ],
                    spacing=5
                ),
                txt_nivel,
                ft.Divider(height=1, color=COLORES["border"]),
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_EVENLY,
                    controls=[
                        ft.Column(
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                            spacing=4,
                            controls=[
                                ft.Text("💰 Ingresos", size=11, color=COLORES["text_secondary"]),
                                txt_ingresos_total
                            ]
                        ),
                        ft.Container(width=1, height=40, bgcolor=COLORES["border"]),
                        ft.Column(
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                            spacing=4,
                            controls=[
                                ft.Text("💸 Gastos", size=11, color=COLORES["text_secondary"]),
                                txt_gastos_total
                            ]
                        )
                    ]
                ),
                ft.Container(
                    padding=ft.padding.symmetric(horizontal=20, vertical=8),
                    bgcolor=COLORES["bg_secondary"],
                    border_radius=20,
                    content=ft.Row(
                        controls=[
                            ft.Text("Balance:", size=12, color=COLORES["text_secondary"]),
                            txt_balance
                        ],
                        spacing=8
                    )
                )
            ]
        )
    )
    
    # =========================================================
    # FILTROS
    # =========================================================
    dropdown_mes = ft.Dropdown(
        value=estado["mes"],
        expand=True,
        bgcolor=COLORES["input"],
        color=COLORES["text"],
        border_radius=12,
        border_color="transparent",
        text_size=13,
        height=48,
        options=[
            ft.dropdown.Option("01", "Enero"), ft.dropdown.Option("02", "Febrero"),
            ft.dropdown.Option("03", "Marzo"), ft.dropdown.Option("04", "Abril"),
            ft.dropdown.Option("05", "Mayo"), ft.dropdown.Option("06", "Junio"),
            ft.dropdown.Option("07", "Julio"), ft.dropdown.Option("08", "Agosto"),
            ft.dropdown.Option("09", "Septiembre"), ft.dropdown.Option("10", "Octubre"),
            ft.dropdown.Option("11", "Noviembre"), ft.dropdown.Option("12", "Diciembre")
        ]
    )
    
    txt_filtro_dia = ft.TextField(
        hint_text="Día",
        width=80,
        bgcolor=COLORES["input"],
        color=COLORES["text"],
        border_radius=12,
        border_color="transparent",
        text_size=13,
        height=48,
        keyboard_type=ft.KeyboardType.NUMBER
    )
    
    def aplicar_filtros(e):
        estado["mes"] = dropdown_mes.value
        estado["dia"] = txt_filtro_dia.value.strip().zfill(2) if txt_filtro_dia.value and txt_filtro_dia.value.isdigit() else ""
        cargar_vista_inicio()
    
    barra_filtros = ft.Container(
        margin=ft.margin.only(left=16, right=16, top=8, bottom=8),
        padding=16,
        bgcolor=COLORES["card"],
        border_radius=16,
        border=ft.border.all(1, COLORES["border"]),
        content=ft.Column(
            spacing=12,
            controls=[
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    controls=[
                        ft.Row(
                            controls=[
                                ft.Container(
                                    width=40, height=40,
                                    bgcolor=f"{COLORES['primary']}20",
                                    border_radius=12,
                                    content=ft.Text("📅", size=18, color=COLORES["primary"], text_align="center"),
                                ),
                                ft.Column(
                                    spacing=2,
                                    controls=[
                                        ft.Text(f"{dropdown_mes.value} {estado['anio']}", 
                                               size=16, weight="bold", color=COLORES["text"]),
                                        ft.Text("Filtrar movimientos", size=11, color=COLORES["text_secondary"])
                                    ]
                                )
                            ],
                            spacing=12
                        ),
                        ft.Container(
                            width=40, height=40,
                            bgcolor=f"{COLORES['success']}20",
                            border_radius=12,
                            content=ft.Text("📊", size=18, color=COLORES["success"], text_align="center"),
                        )
                    ]
                ),
                ft.Row(
                    spacing=8,
                    controls=[dropdown_mes, txt_filtro_dia]
                ),
                ft.Container(
                    padding=ft.padding.symmetric(horizontal=20, vertical=12),
                    bgcolor=COLORES["primary"],
                    border_radius=12,
                    on_click=aplicar_filtros,
                    ink=True,
                    content=ft.Row(
                        alignment=ft.MainAxisAlignment.CENTER,
                        spacing=8,
                        controls=[
                            ft.Text("🔍", size=16),
                            ft.Text("Aplicar Filtros", color="white", weight="bold", size=14)
                        ]
                    )
                )
            ]
        )
    )
    
    # =========================================================
    # FORMULARIO DE MOVIMIENTOS
    # =========================================================
    txt_descripcion = ft.TextField(
        hint_text="Descripción",
        bgcolor=COLORES["input"],
        color=COLORES["text"],
        border_radius=12,
        border_color="transparent",
        focused_border_color=COLORES["primary"],
        text_size=14,
        height=52,
    )
    
    txt_valor = ft.TextField(
        hint_text="$ Valor",
        bgcolor=COLORES["input"],
        color=COLORES["text"],
        border_radius=12,
        border_color="transparent",
        focused_border_color=COLORES["primary"],
        keyboard_type=ft.KeyboardType.NUMBER,
        text_size=14,
        height=52,
        expand=True,
    )
    
    dropdown_tipo = ft.Dropdown(
        value="GASTO",
        expand=True,
        bgcolor=COLORES["input"],
        color=COLORES["text"],
        border_radius=12,
        border_color="transparent",
        text_size=13,
        height=52,
        options=[
            ft.dropdown.Option("INGRESO", "💰 Ingreso"),
            ft.dropdown.Option("GASTO", "💸 Gasto")
        ]
    )
    
    txt_categoria = ft.TextField(
        hint_text="Categoría",
        bgcolor=COLORES["input"],
        color=COLORES["text"],
        border_radius=12,
        border_color="transparent",
        focused_border_color=COLORES["primary"],
        text_size=14,
        height=52,
        expand=True,
    )
    
    def guardar_movimiento(e):
        try:
            if not txt_valor.value or not txt_valor.value.strip():
                toast("⚠️ Ingresa un valor", COLORES["warning"])
                return
            
            valor = float(txt_valor.value.strip().replace(",", ""))
            if valor <= 0:
                toast("⚠️ El valor debe ser mayor a 0", COLORES["warning"])
                return
            
            desc = (txt_descripcion.value or "SIN DESCRIPCIÓN").strip().upper()
            tipo = dropdown_tipo.value
            cat = (txt_categoria.value or "OTROS").strip().upper()
            
            ahora = datetime.datetime.now()
            timestamp = int(ahora.timestamp())
            
            cursor.execute("""
                INSERT INTO movimientos 
                (tipo, descripcion, valor, fecha_full, fecha_corta, timestamp, categoria)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                tipo,
                desc,
                valor,
                ahora.strftime("%Y-%m-%d"),
                ahora.strftime("%d/%m"),
                timestamp,
                cat
            ))
            conn.commit()
            
            txt_valor.value = ""
            txt_descripcion.value = ""
            txt_categoria.value = ""
            
            toast("✅ Movimiento agregado", COLORES["success"])
            cargar_vista_inicio()
            
        except ValueError:
            toast("❌ Valor inválido", COLORES["danger"])
        except Exception as ex:
            toast(f"❌ Error: {str(ex)}", COLORES["danger"])
    
    formulario_movimiento = ft.Container(
        margin=ft.margin.only(left=16, right=16, top=8, bottom=8),
        padding=20,
        bgcolor=COLORES["card"],
        border_radius=16,
        border=ft.border.all(1, COLORES["border"]),
        content=ft.Column(
            spacing=16,
            controls=[
                ft.Row(
                    controls=[
                        ft.Container(
                            width=40, height=40,
                            bgcolor=f"{COLORES['primary']}20",
                            border_radius=12,
                            content=ft.Text("📝", size=20, color=COLORES["primary"], text_align="center"),
                        ),
                        ft.Text("Nuevo Movimiento", size=18, weight="bold", color=COLORES["text"])
                    ],
                    spacing=12
                ),
                txt_descripcion,
                ft.Row(spacing=8, controls=[dropdown_tipo, txt_categoria]),
                ft.Row(
                    spacing=8,
                    controls=[
                        txt_valor,
                        ft.Container(
                            width=52, height=52,
                            gradient=ft.LinearGradient(
                                begin=ft.Alignment(-1, -1),
                                end=ft.Alignment(1, 1),
                                colors=[COLORES["primary"], COLORES["purple"]]
                            ),
                            border_radius=16,
                            on_click=guardar_movimiento,
                            ink=True,
                            content=ft.Text("➕", size=24, color="white", text_align="center"),
                        )
                    ]
                )
            ]
        )
    )
    
    # =========================================================
    # LISTA DE MOVIMIENTOS
    # =========================================================
    lista_movimientos = ft.Column(spacing=8, scroll=ft.ScrollMode.AUTO, expand=True)
    
    def eliminar_movimiento(mov_id: int):
        def confirmar(e):
            cursor.execute("DELETE FROM movimientos WHERE id = ?", (mov_id,))
            conn.commit()
            toast("🗑️ Movimiento eliminado", COLORES["success"])
            cargar_vista_inicio()
            dialog.open = False
            page.update()
        
        def cancelar(e):
            dialog.open = False
            page.update()
        
        dialog = ft.AlertDialog(
            title=ft.Text("Confirmar eliminación", color=COLORES["text"], weight="bold"),
            content=ft.Text("¿Seguro que deseas eliminar este movimiento?", color=COLORES["text_secondary"]),
            bgcolor=COLORES["bg_secondary"],
            shape=ft.RoundedRectangleBorder(radius=16),
            actions=[
                ft.TextButton("Cancelar", on_click=cancelar),
                ft.TextButton("Eliminar", on_click=confirmar, style=ft.ButtonStyle(color=COLORES["danger"]))
            ],
            actions_alignment=ft.MainAxisAlignment.END
        )
        
        page.dialog = dialog
        dialog.open = True
        page.update()
    
    # =========================================================
    # Vista Inicio
    # =========================================================
    vista_inicio = ft.Container(
        expand=True,
        content=ft.Column(
            expand=True,
            spacing=0,
            controls=[
                ft.Container(
                    expand=True,
                    content=ft.Column(
                        expand=True,
                        scroll=ft.ScrollMode.AUTO,
                        controls=[
                            card_score,
                            barra_filtros,
                            formulario_movimiento,
                            ft.Container(
                                padding=ft.padding.symmetric(horizontal=16),
                                content=ft.Column(
                                    controls=[
                                        ft.Row(
                                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                            controls=[
                                                ft.Row(
                                                    controls=[
                                                        ft.Container(
                                                            width=32, height=32,
                                                            bgcolor=f"{COLORES['primary']}20",
                                                            border_radius=8,
                                                            content=ft.Text("📋", size=16, color=COLORES["primary"], text_align="center"),
                                                        ),
                                                        ft.Text("Historial", size=18, weight="bold", color=COLORES["text"])
                                                    ],
                                                    spacing=8
                                                ),
                                                ft.Container(
                                                    padding=ft.padding.symmetric(horizontal=10, vertical=4),
                                                    bgcolor=f"{COLORES['primary']}10",
                                                    border_radius=16,
                                                    content=ft.Text("0 movimientos", size=11, color=COLORES["primary"])
                                                )
                                            ]
                                        ),
                                        lista_movimientos
                                    ]
                                )
                            ),
                            ft.Container(height=20)
                        ]
                    )
                )
            ]
        )
    )
    
    # =========================================================
    # Función cargar_vista_inicio
    # =========================================================
    def cargar_vista_inicio():
        lista_movimientos.controls.clear()
        
        mes = estado["mes"]
        anio = estado["anio"]
        dia = estado["dia"]
        
        query = """
            SELECT id, tipo, descripcion, valor, fecha_corta, categoria
            FROM movimientos
            WHERE substr(fecha_full, 1, 4) = ? AND substr(fecha_full, 6, 2) = ?
        """
        params = [anio, mes]
        
        if dia:
            query += " AND substr(fecha_full, 9, 2) = ?"
            params.append(dia)
        
        query += " ORDER BY timestamp DESC"
        
        cursor.execute(query, params)
        movimientos = cursor.fetchall()
        
        ing_total = 0.0
        gas_total = 0.0
        categorias = {}
        
        for mov in movimientos:
            mov_id, tipo, desc, valor, fecha_corta, cat = mov
            valor = float(valor)
            
            if tipo == "INGRESO":
                ing_total += valor
                color = COLORES["success"]
                icono = "💰"
                signo = "+"
            else:
                gas_total += valor
                color = COLORES["danger"]
                icono = "💸"
                signo = "-"
                cat_nombre = cat or "OTROS"
                categorias[cat_nombre] = categorias.get(cat_nombre, 0) + valor
            
            card_mov = ft.Container(
                bgcolor=COLORES["card"],
                border_radius=12,
                padding=12,
                border=ft.border.all(1, COLORES["border"]),
                margin=ft.margin.only(bottom=8),
                content=ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    controls=[
                        ft.Row(
                            spacing=12,
                            controls=[
                                ft.Container(
                                    width=44, height=44,
                                    bgcolor=f"{color}20",
                                    border_radius=12,
                                    content=ft.Text(icono, size=22, color=color, text_align="center"),
                                ),
                                ft.Column(
                                    spacing=4,
                                    controls=[
                                        ft.Text(desc, size=14, weight="bold", color=COLORES["text"]),
                                        ft.Row(
                                            spacing=8,
                                            controls=[
                                                ft.Container(
                                                    padding=ft.padding.symmetric(horizontal=6, vertical=2),
                                                    bgcolor=f"{COLORES['primary']}20",
                                                    border_radius=4,
                                                    content=ft.Text(fecha_corta, size=10, color=COLORES["text_secondary"])
                                                ),
                                                ft.Container(
                                                    padding=ft.padding.symmetric(horizontal=6, vertical=2),
                                                    bgcolor=f"{COLORES['purple']}20",
                                                    border_radius=4,
                                                    content=ft.Text(cat or "OTROS", size=10, color=COLORES["text_secondary"])
                                                )
                                            ]
                                        )
                                    ]
                                )
                            ]
                        ),
                        ft.Row(
                            spacing=8,
                            controls=[
                                ft.Text(
                                    f"{signo}{_fmt_money(valor)}",
                                    size=16,
                                    weight="bold",
                                    color=color
                                ),
                                ft.Container(
                                    width=36, height=36,
                                    bgcolor=f"{COLORES['danger']}20",
                                    border_radius=10,
                                    on_click=lambda e, mid=mov_id: eliminar_movimiento(mid),
                                    ink=True,
                                    content=ft.Text("🗑️", size=16, color=COLORES["danger"], text_align="center"),
                                )
                            ]
                        )
                    ]
                )
            )
            lista_movimientos.controls.append(card_mov)
        
        # Actualizar contador de movimientos
        try:
            for control in vista_inicio.content.controls[0].content.controls[3].content.controls[0].controls[1].controls:
                if isinstance(control, ft.Container) and control.padding:
                    if hasattr(control, 'content') and isinstance(control.content, ft.Text):
                        control.content.value = f"{len(movimientos)} movimientos"
                        page.update()
        except:
            pass
        
        if not movimientos:
            lista_movimientos.controls.append(
                ft.Container(
                    padding=40,
                    content=ft.Column(
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        controls=[
                            ft.Container(
                                width=80, height=80,
                                bgcolor="#ffffff10",
                                border_radius=40,
                                content=ft.Text("📊", size=40, text_align="center"),
                            ),
                            ft.Container(height=16),
                            ft.Text("Sin movimientos", size=18, weight="bold", color=COLORES["text"]),
                            ft.Container(height=8),
                            ft.Text(
                                "Agrega tu primer ingreso o gasto",
                                size=13,
                                color=COLORES["text_secondary"],
                                text_align="center"
                            )
                        ]
                    )
                )
            )
        
        balance = ing_total - gas_total
        txt_ingresos_total.value = _fmt_money(ing_total)
        txt_gastos_total.value = _fmt_money(gas_total)
        txt_balance.value = _fmt_money(balance)
        
        cursor.execute("SELECT COALESCE(SUM(ahorrado_actual), 0) FROM ahorros")
        total_ahorros = float(cursor.fetchone()[0] or 0)
        
        cursor.execute("SELECT COALESCE(SUM(monto_total - monto_pagado), 0) FROM deudas WHERE tipo_deuda = 'YO_DEBO'")
        total_deudas = float(cursor.fetchone()[0] or 0)
        
        score_data = motor_ia.calcular_score_financiero(ing_total, gas_total, total_ahorros, total_deudas)
        
        txt_score.value = f"{score_data['score']:.0f}"
        txt_nivel.value = score_data['nivel']
        txt_emoji_score.value = score_data['emoji']
        
        card_score.gradient = ft.LinearGradient(
            begin=ft.Alignment(-1, -1),
            end=ft.Alignment(1, 1),
            colors=[score_data["color"], f"{score_data['color']}cc"]
        )
        card_score.bgcolor = None
        
        page.update()
    
    # =========================================================
    # VISTA AHORROS
    # =========================================================
    lista_ahorros = ft.Column(spacing=12, scroll=ft.ScrollMode.AUTO, expand=True)
    
    txt_nombre_meta = ft.TextField(
        hint_text="Nombre de la meta",
        bgcolor=COLORES["input"],
        color=COLORES["text"],
        border_radius=12,
        border_color="transparent",
        text_size=14,
        height=52,
        expand=True
    )
    
    txt_monto_meta = ft.TextField(
        hint_text="$ Meta",
        bgcolor=COLORES["input"],
        color=COLORES["text"],
        border_radius=12,
        border_color="transparent",
        keyboard_type=ft.KeyboardType.NUMBER,
        text_size=14,
        height=52,
        width=120
    )
    
    dropdown_icono_meta = ft.Dropdown(
        value="🐷",
        width=80,
        bgcolor=COLORES["input"],
        color=COLORES["text"],
        border_radius=12,
        border_color="transparent",
        text_size=16,
        height=52,
        options=[
            ft.dropdown.Option("🐷"), ft.dropdown.Option("🏠"), ft.dropdown.Option("🚗"),
            ft.dropdown.Option("✈️"), ft.dropdown.Option("🎓"), ft.dropdown.Option("💍"),
            ft.dropdown.Option("🎮"), ft.dropdown.Option("📱"), ft.dropdown.Option("💻")
        ]
    )
    
    dropdown_ahorro_seleccionado = ft.Dropdown(
        hint_text="Selecciona meta",
        expand=True,
        bgcolor=COLORES["input"],
        color=COLORES["text"],
        border_radius=12,
        border_color="transparent",
        text_size=13,
        height=52,
        options=[]
    )
    
    txt_monto_abonar = ft.TextField(
        hint_text="$ Abonar",
        bgcolor=COLORES["input"],
        color=COLORES["text"],
        border_radius=12,
        border_color="transparent",
        keyboard_type=ft.KeyboardType.NUMBER,
        text_size=14,
        height=52,
        width=120
    )
    
    def crear_meta_ahorro(e):
        try:
            if not txt_nombre_meta.value or not txt_monto_meta.value:
                toast("Completa los campos", COLORES["warning"])
                return
            
            nombre = txt_nombre_meta.value.strip().upper()
            monto = float(txt_monto_meta.value.strip().replace(",", ""))
            icono = dropdown_icono_meta.value
            
            cursor.execute("""
                INSERT INTO ahorros (nombre, meta_total, ahorrado_actual, icono, fecha_creacion)
                VALUES (?, ?, 0, ?, ?)
            """, (nombre, monto, icono, datetime.datetime.now().strftime("%Y-%m-%d")))
            conn.commit()
            
            txt_nombre_meta.value = ""
            txt_monto_meta.value = ""
            
            toast(f"🎯 Meta '{nombre}' creada", COLORES["success"])
            cargar_vista_ahorros()
            
        except ValueError:
            toast("Monto inválido", COLORES["danger"])
        except Exception as ex:
            toast(f"Error: {str(ex)}", COLORES["danger"])
    
    def abonar_a_meta(e):
        try:
            if not dropdown_ahorro_seleccionado.value or not txt_monto_abonar.value:
                toast("Selecciona meta y monto", COLORES["warning"])
                return
            
            meta_id = int(dropdown_ahorro_seleccionado.value)
            monto = float(txt_monto_abonar.value.strip().replace(",", ""))
            
            cursor.execute("UPDATE ahorros SET ahorrado_actual = ahorrado_actual + ? WHERE id = ?", (monto, meta_id))
            
            cursor.execute("SELECT nombre FROM ahorros WHERE id = ?", (meta_id,))
            nombre_meta = cursor.fetchone()[0]
            
            ahora = datetime.datetime.now()
            cursor.execute("""
                INSERT INTO movimientos 
                (tipo, descripcion, valor, fecha_full, fecha_corta, timestamp, categoria)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, ("GASTO", f"AHORRO: {nombre_meta}", monto, ahora.strftime("%Y-%m-%d"), ahora.strftime("%d/%m"), int(ahora.timestamp()), "AHORRO"))
            
            conn.commit()
            txt_monto_abonar.value = ""
            toast(f"💰 Abonaste {_fmt_money(monto)}", COLORES["success"])
            cargar_vista_ahorros()
            cargar_vista_inicio()
            
        except ValueError:
            toast("Monto inválido", COLORES["danger"])
        except Exception as ex:
            toast(f"Error: {str(ex)}", COLORES["danger"])
    
    def cargar_vista_ahorros():
        lista_ahorros.controls.clear()
        
        cursor.execute("""
            SELECT id, nombre, meta_total, ahorrado_actual, icono
            FROM ahorros
            ORDER BY fecha_creacion DESC
        """)
        metas = cursor.fetchall()
        
        dropdown_ahorro_seleccionado.options = [
            ft.dropdown.Option(str(m[0]), f"{m[4]} {m[1]}")
            for m in metas
        ]
        
        for meta in metas:
            meta_id, nombre, total, actual, icono = meta
            total = float(total)
            actual = float(actual)
            progreso = min(actual / total, 1.0) if total > 0 else 0
            faltante = max(total - actual, 0)
            
            if progreso >= 0.9:
                color_progreso = COLORES["success"]
            elif progreso >= 0.5:
                color_progreso = COLORES["primary"]
            else:
                color_progreso = COLORES["warning"]
            
            card_meta = ft.Container(
                bgcolor=COLORES["card"],
                border_radius=16,
                padding=20,
                border=ft.border.all(1, COLORES["border"]),
                content=ft.Column(
                    spacing=12,
                    controls=[
                        ft.Row(
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            controls=[
                                ft.Row(spacing=12, controls=[
                                    ft.Text(icono, size=32),
                                    ft.Column(spacing=2, controls=[
                                        ft.Text(nombre, size=16, weight="bold", color=COLORES["text"]),
                                        ft.Text(f"Meta: {_fmt_money(total)}", size=12, color=COLORES["text_secondary"])
                                    ])
                                ]),
                                ft.Text(f"{progreso*100:.1f}%", size=18, weight="bold", color=color_progreso)
                            ]
                        ),
                        ft.ProgressBar(value=progreso, color=color_progreso, bgcolor=COLORES["input"], height=12, border_radius=6),
                        ft.Text(f"Falta: {_fmt_money(faltante)}", size=11, color=COLORES["text_disabled"])
                    ]
                )
            )
            lista_ahorros.controls.append(card_meta)
        
        if not metas:
            lista_ahorros.controls.append(
                ft.Container(
                    padding=40,
                    content=ft.Column(
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        controls=[
                            ft.Text("🐷", size=64),
                            ft.Text("Sin metas de ahorro", size=18, weight="bold", color=COLORES["text"]),
                            ft.Text("Crea tu primera meta", size=13, color=COLORES["text_secondary"], text_align="center")
                        ]
                    )
                )
            )
        
        page.update()
    
    formulario_ahorros = ft.Container(
        margin=ft.margin.symmetric(horizontal=16, vertical=12),
        padding=20,
        bgcolor=COLORES["card"],
        border_radius=16,
        border=ft.border.all(1, COLORES["border"]),
        content=ft.Column(
            spacing=12,
            controls=[
                ft.Text("🎯 Nueva Meta", size=18, weight="bold", color=COLORES["text"]),
                ft.Row(spacing=8, controls=[dropdown_icono_meta, txt_nombre_meta]),
                ft.Row(spacing=8, controls=[txt_monto_meta, crear_boton("Crear", "➕", crear_meta_ahorro, COLORES["success"], True)]),
                ft.Divider(height=1, color=COLORES["border"]),
                ft.Text("💰 Abonar a Meta", size=16, weight="bold", color=COLORES["text"]),
                ft.Row(spacing=8, controls=[dropdown_ahorro_seleccionado]),
                ft.Row(spacing=8, controls=[txt_monto_abonar, crear_boton("Abonar", "💵", abonar_a_meta, COLORES["primary"], True)])
            ]
        )
    )
    
    vista_ahorros = ft.Container(
        expand=True,
        content=ft.Column(
            expand=True,
            scroll=ft.ScrollMode.AUTO,
            controls=[
                ft.Container(height=16),
                formulario_ahorros,
                ft.Container(expand=True, padding=ft.padding.symmetric(horizontal=16), content=lista_ahorros),
                ft.Container(height=80)
            ]
        )
    )
    
    # =========================================================
    # VISTA DEUDAS
    # =========================================================
    lista_deudas = ft.Column(spacing=12, scroll=ft.ScrollMode.AUTO, expand=True)
    
    txt_nombre_deuda = ft.TextField(
        hint_text="Nombre de la deuda",
        bgcolor=COLORES["input"],
        color=COLORES["text"],
        border_radius=12,
        border_color="transparent",
        text_size=14,
        height=52,
        expand=True
    )
    
    txt_monto_deuda = ft.TextField(
        hint_text="$ Monto total",
        bgcolor=COLORES["input"],
        color=COLORES["text"],
        border_radius=12,
        border_color="transparent",
        keyboard_type=ft.KeyboardType.NUMBER,
        text_size=14,
        height=52,
        width=130
    )
    
    dropdown_tipo_deuda = ft.Dropdown(
        value="YO_DEBO",
        bgcolor=COLORES["input"],
        color=COLORES["text"],
        border_radius=12,
        border_color="transparent",
        text_size=13,
        height=52,
        expand=True,
        options=[
            ft.dropdown.Option("ME_DEBEN", "💵 Me deben"),
            ft.dropdown.Option("YO_DEBO", "💳 Yo debo")
        ]
    )
    
    dropdown_deuda_seleccionada = ft.Dropdown(
        hint_text="Selecciona deuda",
        expand=True,
        bgcolor=COLORES["input"],
        color=COLORES["text"],
        border_radius=12,
        border_color="transparent",
        text_size=13,
        height=52,
        options=[]
    )
    
    txt_monto_abonar_deuda = ft.TextField(
        hint_text="$ Abonar",
        bgcolor=COLORES["input"],
        color=COLORES["text"],
        border_radius=12,
        border_color="transparent",
        keyboard_type=ft.KeyboardType.NUMBER,
        text_size=14,
        height=52,
        width=120
    )
    
    def crear_deuda(e):
        try:
            if not txt_nombre_deuda.value or not txt_monto_deuda.value:
                toast("Completa los campos", COLORES["warning"])
                return
            
            nombre = txt_nombre_deuda.value.strip().upper()
            monto = float(txt_monto_deuda.value.strip().replace(",", ""))
            tipo = dropdown_tipo_deuda.value
            
            cursor.execute("""
                INSERT INTO deudas (nombre, monto_total, monto_pagado, tipo_deuda, fecha_creacion)
                VALUES (?, ?, 0, ?, ?)
            """, (nombre, monto, tipo, datetime.datetime.now().strftime("%Y-%m-%d")))
            
            ahora = datetime.datetime.now()
            if tipo == "ME_DEBEN":
                cursor.execute("""
                    INSERT INTO movimientos 
                    (tipo, descripcion, valor, fecha_full, fecha_corta, timestamp, categoria)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, ("GASTO", f"PRÉSTAMO: {nombre}", monto, ahora.strftime("%Y-%m-%d"), ahora.strftime("%d/%m"), int(ahora.timestamp()), "PRÉSTAMO"))
            else:
                cursor.execute("""
                    INSERT INTO movimientos 
                    (tipo, descripcion, valor, fecha_full, fecha_corta, timestamp, categoria)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, ("INGRESO", f"PRÉSTAMO: {nombre}", monto, ahora.strftime("%Y-%m-%d"), ahora.strftime("%d/%m"), int(ahora.timestamp()), "PRÉSTAMO"))
            
            conn.commit()
            txt_nombre_deuda.value = ""
            txt_monto_deuda.value = ""
            toast(f"📒 Deuda '{nombre}' registrada", COLORES["success"])
            cargar_vista_deudas()
            cargar_vista_inicio()
            
        except ValueError:
            toast("Monto inválido", COLORES["danger"])
        except Exception as ex:
            toast(f"Error: {str(ex)}", COLORES["danger"])
    
    def abonar_deuda(e):
        try:
            if not dropdown_deuda_seleccionada.value or not txt_monto_abonar_deuda.value:
                toast("Selecciona deuda y monto", COLORES["warning"])
                return
            
            deuda_id = int(dropdown_deuda_seleccionada.value)
            monto = float(txt_monto_abonar_deuda.value.strip().replace(",", ""))
            
            cursor.execute("UPDATE deudas SET monto_pagado = monto_pagado + ? WHERE id = ?", (monto, deuda_id))
            
            cursor.execute("SELECT nombre, tipo_deuda FROM deudas WHERE id = ?", (deuda_id,))
            nombre_deuda, tipo_deuda = cursor.fetchone()
            
            ahora = datetime.datetime.now()
            if tipo_deuda == "ME_DEBEN":
                cursor.execute("""
                    INSERT INTO movimientos 
                    (tipo, descripcion, valor, fecha_full, fecha_corta, timestamp, categoria)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, ("INGRESO", f"PAGO: {nombre_deuda}", monto, ahora.strftime("%Y-%m-%d"), ahora.strftime("%d/%m"), int(ahora.timestamp()), "PAGO DEUDA"))
            else:
                cursor.execute("""
                    INSERT INTO movimientos 
                    (tipo, descripcion, valor, fecha_full, fecha_corta, timestamp, categoria)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, ("GASTO", f"PAGO: {nombre_deuda}", monto, ahora.strftime("%Y-%m-%d"), ahora.strftime("%d/%m"), int(ahora.timestamp()), "PAGO DEUDA"))
            
            conn.commit()
            txt_monto_abonar_deuda.value = ""
            toast(f"💰 Abonaste {_fmt_money(monto)}", COLORES["success"])
            cargar_vista_deudas()
            cargar_vista_inicio()
            
        except ValueError:
            toast("Monto inválido", COLORES["danger"])
        except Exception as ex:
            toast(f"Error: {str(ex)}", COLORES["danger"])
    
    def cargar_vista_deudas():
        lista_deudas.controls.clear()
        
        cursor.execute("""
            SELECT id, nombre, monto_total, monto_pagado, tipo_deuda
            FROM deudas
            ORDER BY fecha_creacion DESC
        """)
        deudas = cursor.fetchall()
        
        dropdown_deuda_seleccionada.options = [
            ft.dropdown.Option(str(d[0]), f"{'💵' if d[4]=='ME_DEBEN' else '💳'} {d[1]}")
            for d in deudas
        ]
        
        for deuda in deudas:
            deuda_id, nombre, total, pagado, tipo = deuda
            total = float(total)
            pagado = float(pagado)
            progreso = min(pagado / total, 1.0) if total > 0 else 0
            pendiente = max(total - pagado, 0)
            
            color_tipo = COLORES["success"] if tipo == "ME_DEBEN" else COLORES["danger"]
            icono_tipo = "💵" if tipo == "ME_DEBEN" else "💳"
            texto_tipo = "ME DEBEN" if tipo == "ME_DEBEN" else "YO DEBO"
            
            card_deuda = ft.Container(
                bgcolor=COLORES["card"],
                border_radius=16,
                padding=20,
                border=ft.border.all(1, COLORES["border"]),
                content=ft.Column(
                    spacing=12,
                    controls=[
                        ft.Row(
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            controls=[
                                ft.Column(spacing=4, controls=[
                                    ft.Row(spacing=8, controls=[
                                        ft.Text(icono_tipo, size=20),
                                        ft.Text(texto_tipo, size=11, weight="bold", color=color_tipo)
                                    ]),
                                    ft.Text(nombre, size=16, weight="bold", color=COLORES["text"]),
                                    ft.Text(f"Total: {_fmt_money(total)}", size=12, color=COLORES["text_secondary"])
                                ]),
                                ft.Text(f"{progreso*100:.1f}%", size=18, weight="bold", color=color_tipo)
                            ]
                        ),
                        ft.ProgressBar(value=progreso, color=color_tipo, bgcolor=COLORES["input"], height=12, border_radius=6),
                        ft.Text(f"Pendiente: {_fmt_money(pendiente)}", size=11, color=COLORES["text_disabled"])
                    ]
                )
            )
            lista_deudas.controls.append(card_deuda)
        
        if not deudas:
            lista_deudas.controls.append(
                ft.Container(
                    padding=40,
                    content=ft.Column(
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        controls=[
                            ft.Text("💳", size=64),
                            ft.Text("Sin deudas registradas", size=18, weight="bold", color=COLORES["text"]),
                            ft.Text("Registra tu primera deuda", size=13, color=COLORES["text_secondary"], text_align="center")
                        ]
                    )
                )
            )
        
        page.update()
    
    formulario_deudas = ft.Container(
        margin=ft.margin.symmetric(horizontal=16, vertical=12),
        padding=20,
        bgcolor=COLORES["card"],
        border_radius=16,
        border=ft.border.all(1, COLORES["border"]),
        content=ft.Column(
            spacing=12,
            controls=[
                ft.Text("📒 Nueva Deuda", size=18, weight="bold", color=COLORES["text"]),
                dropdown_tipo_deuda,
                ft.Row(spacing=8, controls=[txt_nombre_deuda]),
                ft.Row(spacing=8, controls=[txt_monto_deuda, crear_boton("Crear", "➕", crear_deuda, COLORES["purple"], True)]),
                ft.Divider(height=1, color=COLORES["border"]),
                ft.Text("💵 Abonar a Deuda", size=16, weight="bold", color=COLORES["text"]),
                ft.Row(spacing=8, controls=[dropdown_deuda_seleccionada]),
                ft.Row(spacing=8, controls=[txt_monto_abonar_deuda, crear_boton("Abonar", "💰", abonar_deuda, COLORES["primary"], True)])
            ]
        )
    )
    
    vista_deudas = ft.Container(
        expand=True,
        content=ft.Column(
            expand=True,
            scroll=ft.ScrollMode.AUTO,
            controls=[
                ft.Container(height=16),
                formulario_deudas,
                ft.Container(expand=True, padding=ft.padding.symmetric(horizontal=16), content=lista_deudas),
                ft.Container(height=80)
            ]
        )
    )
    
    # =========================================================
    # VISTA IA - CON BOTÓN ANALIZAR Y SIN ALIGNMENT ERRÓNEO
    # =========================================================
    columna_ia = ft.Column(spacing=12, scroll=ft.ScrollMode.AUTO, expand=True)
    
    def analizar_finanzas(e):
        """Función que se ejecuta al hacer clic en Analizar"""
        # Limpiar y mostrar loading
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
        
        # Pequeña pausa para efecto de carga
        time.sleep(0.5)
        
        # Limpiar y cargar el análisis REAL
        columna_ia.controls.clear()
        cargar_vista_ia()
        page.update()
    
    def cargar_vista_ia():
        columna_ia.controls.clear()
        
        mes = estado["mes"]
        anio = estado["anio"]
        
        # Datos del mes actual
        cursor.execute("""
            SELECT tipo, COALESCE(SUM(valor), 0) 
            FROM movimientos 
            WHERE substr(fecha_full, 1, 4) = ? AND substr(fecha_full, 6, 2) = ?
            GROUP BY tipo
        """, (anio, mes))
        datos_mes = {t: float(v) for t, v in cursor.fetchall()}
        ing_actual = datos_mes.get("INGRESO", 0)
        gas_actual = datos_mes.get("GASTO", 0)
        balance_actual = ing_actual - gas_actual
        
        # Datos del mes anterior
        mes_anterior_num = str(int(mes) - 1).zfill(2) if int(mes) > 1 else "12"
        anio_anterior = anio if int(mes) > 1 else str(int(anio) - 1)
        
        cursor.execute("""
            SELECT tipo, COALESCE(SUM(valor), 0) 
            FROM movimientos 
            WHERE substr(fecha_full, 1, 4) = ? AND substr(fecha_full, 6, 2) = ?
            GROUP BY tipo
        """, (anio_anterior, mes_anterior_num))
        datos_anterior = {t: float(v) for t, v in cursor.fetchall()}
        ing_anterior = datos_anterior.get("INGRESO", 0)
        gas_anterior = datos_anterior.get("GASTO", 0)
        
        # Ahorros y deudas
        cursor.execute("SELECT COALESCE(SUM(ahorrado_actual), 0) FROM ahorros")
        total_ahorros = float(cursor.fetchone()[0] or 0)
        
        cursor.execute("SELECT id, nombre, meta_total, ahorrado_actual, icono FROM ahorros")
        metas_ahorro_data = cursor.fetchall()
        metas_ahorro = []
        for m in metas_ahorro_data:
            metas_ahorro.append({
                "id": m[0],
                "nombre": m[1],
                "meta_total": float(m[2]),
                "ahorrado_actual": float(m[3]),
                "icono": m[4]
            })
        
        cursor.execute("SELECT COALESCE(SUM(monto_total - monto_pagado), 0) FROM deudas WHERE tipo_deuda = 'YO_DEBO'")
        total_deudas = float(cursor.fetchone()[0] or 0)
        
        # Categorías de gasto
        cursor.execute("""
            SELECT categoria, COALESCE(SUM(valor), 0)
            FROM movimientos
            WHERE tipo = 'GASTO' AND substr(fecha_full, 1, 4) = ? AND substr(fecha_full, 6, 2) = ?
            GROUP BY categoria
            ORDER BY SUM(valor) DESC
        """, (anio, mes))
        categorias_dict = {c: float(v) for c, v in cursor.fetchall()}
        
        # ===== GENERAR ANÁLISIS CONVERSACIONAL =====
        
        # Card: Mi Bolsillo - Título
        card_titulo = ft.Container(
            bgcolor=COLORES["bg_secondary"],
            border_radius=16,
            padding=20,
            margin=ft.margin.only(bottom=8),
            content=ft.Column(
                controls=[
                    ft.Text("# Mi Bolsillo", size=28, weight="bold", color=COLORES["text"]),
                    ft.Text("Tu asistente financiero", size=14, color=COLORES["text_secondary"])
                ]
            )
        )
        columna_ia.controls.append(card_titulo)
        
        # Card: Score
        score_data = motor_ia.calcular_score_financiero(ing_actual, gas_actual, total_ahorros, total_deudas)
        
        card_score_ia = ft.Container(
            bgcolor=score_data["color"],
            border_radius=24,
            padding=24,
            margin=ft.margin.only(bottom=8),
            shadow=ft.BoxShadow(
                spread_radius=0,
                blur_radius=30,
                color=f"{score_data['color']}40",
                offset=ft.Offset(0, 4)
            ),
            content=ft.Column(
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=12,
                controls=[
                    ft.Container(
                        width=70, height=70,
                        bgcolor="#ffffff20",
                        border_radius=35,
                        content=ft.Text(score_data["emoji"], size=40, text_align="center"),
                    ),
                    ft.Row(
                        alignment=ft.MainAxisAlignment.CENTER,
                        vertical_alignment=ft.CrossAxisAlignment.END,
                        controls=[
                            ft.Text(f"{score_data['score']:.0f}/10", size=48, weight="bold", color="white"),
                        ],
                        spacing=5
                    ),
                    ft.Text(score_data["nivel"], size=18, color="white", weight="bold"),
                    ft.Text("Tu calificación financiera", size=12, color="#ffffffcc"),
                ]
            )
        )
        columna_ia.controls.append(card_score_ia)
        
        # Card: Resumen Ejecutivo
        resumen = motor_ia.generar_resumen_ejecutivo(ing_actual, gas_actual, balance_actual)
        
        card_resumen = ft.Container(
            bgcolor=COLORES["card"],
            border_radius=16,
            padding=20,
            margin=ft.margin.only(bottom=8),
            border=ft.border.all(1, COLORES["border"]),
            content=ft.Column(
                controls=[
                    ft.Text("📋 Resumen Ejecutivo", size=18, weight="bold", color=COLORES["text"]),
                    ft.Container(height=8),
                    ft.Text(resumen, size=14, color=COLORES["text"])
                ]
            )
        )
        columna_ia.controls.append(card_resumen)
        
        # Card: vs Mes Anterior
        comparacion = motor_ia.generar_comparacion_mes_anterior(
            ing_actual, gas_actual, ing_anterior, gas_anterior
        )
        
        card_comparacion = ft.Container(
            bgcolor=COLORES["card"],
            border_radius=16,
            padding=20,
            margin=ft.margin.only(bottom=8),
            border=ft.border.all(1, COLORES["border"]),
            content=ft.Column(
                controls=[
                    ft.Text("📊 vs Mes Anterior", size=18, weight="bold", color=COLORES["text"]),
                    ft.Container(height=8),
                    ft.Text(comparacion, size=14, color=COLORES["text"])
                ]
            )
        )
        columna_ia.controls.append(card_comparacion)
        
        # Card: Alertas
        alertas = motor_ia.generar_alertas_personalizadas(
            ing_actual, gas_actual, total_ahorros, total_deudas, metas_ahorro, {}
        )
        
        if alertas:
            card_alertas = ft.Container(
                bgcolor="#7f1d1d",
                border_radius=16,
                padding=20,
                margin=ft.margin.only(bottom=8),
                content=ft.Column(
                    controls=[
                        ft.Text("🚨 Alertas", size=18, weight="bold", color="white"),
                        ft.Container(height=8),
                        ft.Column(
                            controls=[
                                ft.Container(
                                    padding=ft.padding.only(left=8),
                                    content=ft.Text(f"• {alerta}", size=14, color="white")
                                ) for alerta in alertas
                            ],
                            spacing=8
                        )
                    ]
                )
            )
            columna_ia.controls.append(card_alertas)
        
        # Card: Dónde gastas más
        analisis_categorias = motor_ia.analizar_categorias_gastos(categorias_dict, gas_actual)
        
        if analisis_categorias:
            card_categorias = ft.Container(
                bgcolor=COLORES["card"],
                border_radius=16,
                padding=20,
                margin=ft.margin.only(bottom=8),
                border=ft.border.all(1, COLORES["border"]),
                content=ft.Column(
                    controls=[
                        ft.Text("💰 Dónde gastas más", size=18, weight="bold", color=COLORES["text"]),
                        ft.Container(height=8),
                        ft.Column(
                            controls=[
                                ft.Container(
                                    padding=12,
                                    bgcolor=COLORES["input"],
                                    border_radius=12,
                                    margin=ft.margin.only(bottom=8),
                                    content=ft.Column(
                                        controls=[
                                            ft.Row(
                                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                                controls=[
                                                    ft.Text(f"{i+1}. {cat['categoria']}", 
                                                           size=16, weight="bold", 
                                                           color=COLORES["success"] if cat['es_principal'] else COLORES["text"]),
                                                    ft.Text(_fmt_money(cat['monto']), 
                                                           size=16, weight="bold", 
                                                           color=COLORES["danger"])
                                                ]
                                            ),
                                            ft.Text(f"{cat['porcentaje']:.1f}% de tus gastos", 
                                                   size=12, color=COLORES["text_secondary"]),
                                            ft.Container(height=4),
                                            ft.Text(cat['insight'], 
                                                   size=13, color=COLORES["text"], italic=True)
                                        ]
                                    )
                                ) for i, cat in enumerate(analisis_categorias)
                            ],
                            spacing=8
                        )
                    ]
                )
            )
            columna_ia.controls.append(card_categorias)
        
        # Card: Consejos para ti
        consejos = motor_ia.generar_consejos_personalizados(
            ing_actual, gas_actual, total_ahorros, total_deudas, analisis_categorias
        )
        
        card_consejos = ft.Container(
            bgcolor=COLORES["card"],
            border_radius=16,
            padding=20,
            margin=ft.margin.only(bottom=8),
            border=ft.border.all(1, COLORES["border"]),
            content=ft.Column(
                controls=[
                    ft.Text("💡 Consejos para ti", size=18, weight="bold", color=COLORES["text"]),
                    ft.Container(height=8),
                    ft.Column(
                        controls=[
                            ft.Container(
                                padding=ft.padding.only(left=8, bottom=4),
                                content=ft.Text(f"• {consejo}", size=14, color=COLORES["text"])
                            ) for consejo in consejos[:4]
                        ],
                        spacing=4
                    )
                ]
            )
        )
        columna_ia.controls.append(card_consejos)
        
        # Card: Meta para el próximo mes
        meta = motor_ia.generar_meta_proximo_mes(ing_actual, gas_actual, total_ahorros)
        
        card_meta = ft.Container(
            bgcolor=COLORES["primary"],
            border_radius=16,
            padding=20,
            margin=ft.margin.only(bottom=16),
            content=ft.Column(
                controls=[
                    ft.Text("🎯 Meta para el próximo mes", size=18, weight="bold", color="white"),
                    ft.Container(height=8),
                    ft.Text(meta, size=15, color="white")
                ]
            )
        )
        columna_ia.controls.append(card_meta)
        
        page.update()
    
    # Vista IA - CON BOTÓN ANALIZAR Y SIN ALIGNMENT PROBLEMÁTICO
    vista_ia = ft.Container(
        expand=True,
        content=ft.Column(
            expand=True,
            scroll=ft.ScrollMode.AUTO,
            controls=[
                ft.Container(height=16),
                ft.Container(
                    padding=ft.padding.symmetric(horizontal=16),
                    content=ft.Column([
                        # BOTÓN DE ANALIZAR - GRANDE Y BONITO
                        ft.Container(
                            padding=20,
                            bgcolor=COLORES["card"],
                            border_radius=16,
                            border=ft.border.all(1, COLORES["border"]),
                            margin=ft.margin.only(bottom=16),
                            content=ft.Column([
                                ft.Container(
                                    width=80, height=80,
                                    bgcolor=f"{COLORES['primary']}20",
                                    border_radius=40,
                                    content=ft.Text("🤖", size=40, color=COLORES["primary"], text_align="center"),
                                    # ALIGNMENT ELIMINADO - CORREGIDO
                                ),
                                ft.Container(height=8),
                                ft.Text("Análisis con IA", size=20, weight="bold", color=COLORES["text"]),
                                ft.Text("Obtén recomendaciones personalizadas basadas en tus movimientos", 
                                       size=14, color=COLORES["text_secondary"], text_align="center"),
                                ft.Container(height=8),
                                ft.Container(
                                    padding=ft.padding.symmetric(horizontal=30, vertical=15),
                                    bgcolor=COLORES["primary"],
                                    border_radius=30,
                                    on_click=analizar_finanzas,
                                    ink=True,
                                    content=ft.Row([
                                        ft.Text("🔍", size=20),
                                        ft.Text("Analizar Mis Finanzas", color="white", weight="bold", size=16)
                                    ], alignment=ft.MainAxisAlignment.CENTER, spacing=10)
                                )
                            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=8)
                        ),
                        # Resultados del análisis
                        columna_ia
                    ])
                ),
                ft.Container(height=80)
            ]
        )
    )
    
    # =========================================================
    # NAVEGACIÓN
    # =========================================================
    contenedor_vistas = ft.Container(
        expand=True,
        content=vista_inicio
    )
    
    def cambiar_vista(nueva_vista: str, e=None):
        if estado["vista_actual"] == nueva_vista:
            return
        
        vistas = {
            "inicio": vista_inicio,
            "ahorros": vista_ahorros,
            "deudas": vista_deudas,
            "ia": vista_ia
        }
        
        contenedor_vistas.content = vistas[nueva_vista]
        
        if nueva_vista == "inicio":
            cargar_vista_inicio()
        elif nueva_vista == "ahorros":
            cargar_vista_ahorros()
        elif nueva_vista == "deudas":
            cargar_vista_deudas()
        elif nueva_vista == "ia":
            # NO cargar análisis automáticamente
            columna_ia.controls.clear()
            pass
        
        estado["vista_actual"] = nueva_vista
        
        for btn_nombre, btn in botones_nav.items():
            if btn_nombre == nueva_vista:
                btn.bgcolor = f"{COLORES['primary']}20"
                btn.content.controls[0].color = COLORES["primary"]
                btn.content.controls[1].color = COLORES["text"]
                btn.content.controls[1].weight = "bold"
            else:
                btn.bgcolor = "transparent"
                btn.content.controls[0].color = COLORES["text_secondary"]
                btn.content.controls[1].color = COLORES["text_secondary"]
                btn.content.controls[1].weight = "normal"
        
        page.update()
    
    def crear_boton_nav(texto: str, icono: str, vista: str, activo: bool = False):
        return ft.Container(
            expand=True,
            padding=ft.padding.symmetric(vertical=12),
            on_click=lambda e: cambiar_vista(vista, e),
            bgcolor=f"{COLORES['primary']}20" if activo else "transparent",
            border_radius=12,
            ink=True,
            content=ft.Column(
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=4,
                controls=[
                    ft.Text(icono, size=22, color=COLORES["primary"] if activo else COLORES["text_secondary"]),
                    ft.Text(
                        texto,
                        size=11,
                        color=COLORES["text"] if activo else COLORES["text_secondary"],
                        weight="bold" if activo else "normal"
                    )
                ]
            )
        )
    
    botones_nav = {
        "inicio": crear_boton_nav("🏠", "Inicio", "inicio", True),
        "ahorros": crear_boton_nav("🐷", "Ahorros", "ahorros"),
        "deudas": crear_boton_nav("📒", "Deudas", "deudas"),
        "ia": crear_boton_nav("🤖", "IA", "ia")
    }
    
    barra_navegacion = ft.Container(
        bgcolor=COLORES["bg_secondary"],
        padding=ft.padding.only(left=8, right=8, top=8, bottom=16),
        border=ft.border.only(top=ft.BorderSide(1, COLORES["border"])),
        content=ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_AROUND,
            controls=list(botones_nav.values())
        )
    )
    
    # =========================================================
    # Layout principal
    # =========================================================
    page.add(
        ft.Column(
            expand=True,
            spacing=0,
            controls=[
                contenedor_vistas,
                barra_navegacion
            ]
        )
    )
    
    # Cargar vista inicial
    cargar_vista_inicio()


# =========================================================
# Punto de entrada
# =========================================================
if __name__ == "__main__":
    app = ft.app(target=main)