"""P05. Visualizaciones de exposición a presiones de costos. Uso: python src/graficar.py (después de src/calcular.py)"""
import json
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.offline import get_plotlyjs

RAIZ = Path(__file__).resolve().parents[1]
RES, VIS = RAIZ / "resultados", RAIZ / "visualizaciones"
AZUL, ROJO, GRIS, AMBAR, NEGRO, CLARO = "#1f78d1", "#c8161d", "#6b7280", "#d98e04", "#111827", "#c9ced6"
FUENTE = "Fuente: elaboración propia con datos de INEGI (Censos Económicos 2019 y 2024, EMEC, INPP e INPC)."
CORTO = {"43": "Mayoreo (total)", "46": "Menudeo (total)", "431": "Mayoreo de abarrotes y alimentos", "432": "Mayoreo de textiles y calzado", "433": "Mayoreo de farmacia y electrodomésticos",
         "434": "Mayoreo de materias primas", "435": "Mayoreo de maquinaria y equipo", "436": "Mayoreo de camiones y refacciones", "461": "Menudeo de abarrotes y alimentos",
         "462": "Autoservicio y departamentales", "463": "Menudeo de textiles y calzado", "464": "Menudeo de salud y cuidado personal", "465": "Menudeo de papelería y esparcimiento",
         "466": "Menudeo de enseres y mobiliario", "467": "Menudeo de ferretería y vidrios", "468": "Menudeo de vehículos y combustibles"}


def s(v, d=1, pct=False):
    return f'{"+" if v > 0 else ("−" if v < 0 else "")}{abs(v):.{d}f}{"%" if pct else ""}'


def base(fig, titulo, sub, alto=520, b=130, l=70):
    fig.update_layout(template="plotly_white", height=alto, margin=dict(l=l, r=30, t=115, b=b), font=dict(family="Segoe UI, Arial", size=13),
                      title=dict(text=f"<b>{titulo}</b><br><span style='font-size:13px;color:{GRIS}'>{sub}</span>", x=0, xanchor="left", y=0.95),
                      legend=dict(orientation="h", y=-0.13, x=0, yanchor="top"), plot_bgcolor="#f4f4f4")
    fig.update_xaxes(gridcolor="white", gridwidth=2)
    fig.update_yaxes(gridcolor="white", gridwidth=2)
    fig.add_annotation(text=FUENTE, xref="paper", yref="paper", x=0, y=0, yshift=-(b - 15), showarrow=False, xanchor="left", yanchor="top", font=dict(size=11, color=GRIS))
    return fig


def figuras():
    r = json.loads((RES / "resumen.json").read_text(encoding="utf-8"))
    est = pd.read_csv(RES / "estructura_costos.csv", dtype={"codigo": str})
    ex = pd.read_csv(RES / "exposicion.csv", dtype={"codigo": str}).set_index("codigo")
    e24 = est[est.anio == 2024].set_index("codigo")
    orden = e24.sort_values("excedente_pct").index.tolist()
    nombres = [CORTO[c] for c in orden]
    f1 = go.Figure()
    for col, n, c in (("mercancias_pct", "Mercancías y otros costos de venta", GRIS), ("consumo_intermedio_pct", "Otros gastos de operación (consumo intermedio)", CLARO),
                      ("remuneraciones_pct", "Remuneraciones", ROJO), ("excedente_pct", "Excedente (antes de depreciación, intereses, impuestos y utilidades)", AZUL)):
        f1.add_bar(y=nombres, x=e24.loc[orden, col], orientation="h", name=n, marker_color=c, text=[f"{v:.1f}" if v >= 6 else "" for v in e24.loc[orden, col]], textposition="inside", insidetextanchor="middle", textangle=0)
    f1.update_layout(barmode="stack")
    m, w = r["menudeo"], r["mayoreo"]
    base(f1, f"De cada $100 de venta, el menudeo gasta ${m['mercancias_pct']:.0f} en mercancías y ${m['remuneraciones_pct']:.1f} en salarios; le quedan ${m['excedente_pct']:.1f}",
         f"Censos Económicos 2024, nacional, por cada $100 de ingresos. Mayoreo: ${w['mercancias_pct']:.0f} en mercancías, ${w['remuneraciones_pct']:.1f} en salarios y ${w['excedente_pct']:.1f} de excedente. El excedente es un residuo censal, no utilidad", alto=720, b=170, l=240)
    f1.update_xaxes(title_text="Pesos por cada $100 de ventas", range=[0, 100])
    f1.update_layout(legend=dict(orientation="h", y=-0.1, x=0, yanchor="top", font=dict(size=11)))
    # cuadrante
    sub = ex.loc[[c for c in CORTO if c not in ("43", "46")]].copy()
    sub["nombre"] = [CORTO[c] for c in sub.index]
    col = {"expuesta y con presión": ROJO, "expuesta, sin presión reciente": AMBAR, "poco expuesta, con presión": AZUL, "poco expuesta, sin presión": GRIS}
    f2 = go.Figure()
    for q, c in col.items():
        x = sub[sub.cuadrante == q]
        f2.add_trace(go.Scatter(x=x.abs_salarios_1pct, y=x.costo_laboral_unitario_var_12m_pct, mode=("markers+text" if q in ("expuesta y con presión", "poco expuesta, con presión") else "markers"), name=q, text=x.nombre, textposition="top center", textfont=dict(size=10),
                                marker=dict(size=np.clip(np.sqrt(x.personal) / 18, 8, 40), color=c, opacity=0.85, line=dict(color="white", width=1)),
                                customdata=x[["remuneraciones_pct", "excedente_pct", "presion_laboral_pp_ventas"]], hovertemplate="<b>%{text}</b><br>1% más de salarios absorbe %{x:.2f}% del excedente<br>Costo laboral por peso de ingreso, 12 meses: %{y:+.1f}%<br>Salarios: %{customdata[0]:.1f}% de las ventas<extra></extra>"))
    f2.add_vline(x=r["mediana_abs_salarios_1pct_subsectores"], line_dash="dash", line_color=NEGRO, annotation_text="Mediana", annotation_position="top")
    f2.add_hline(y=0, line_color=NEGRO)
    base(f2, f"{r['cuadrantes'].get('expuesta y con presión', 0)} subsectores combinan estructura expuesta a salarios y presión laboral reciente",
         "Eje x: % del excedente que absorbería un alza de 1% en salarios sin traspaso (Censo 2024). Eje y: cambio del costo laboral por peso de ingreso, 12 meses (EMEC). Tamaño: personal ocupado", alto=640)
    f2.update_xaxes(title_text="% del excedente absorbido por +1% en salarios")
    f2.update_yaxes(title_text="Δ% del costo laboral por peso de ingreso, 12 meses")
    # 2019 vs 2024
    f3 = go.Figure()
    e19 = est[est.anio == 2019].set_index("codigo")
    ord3 = e24.loc[[c for c in CORTO]].sort_values("remuneraciones_pct").index.tolist()
    for c in ord3:
        f3.add_trace(go.Scatter(x=[e19.loc[c, "remuneraciones_pct"], e24.loc[c, "remuneraciones_pct"]], y=[CORTO[c]] * 2, mode="lines", line=dict(color="#999", width=3), showlegend=False, hoverinfo="skip"))
    f3.add_trace(go.Scatter(x=e19.loc[ord3, "remuneraciones_pct"], y=[CORTO[c] for c in ord3], mode="markers", name="Censo 2019", marker=dict(size=11, color=GRIS)))
    f3.add_trace(go.Scatter(x=e24.loc[ord3, "remuneraciones_pct"], y=[CORTO[c] for c in ord3], mode="markers+text", name="Censo 2024", marker=dict(size=11, color=ROJO),
                            text=[f"{v:.1f}" for v in e24.loc[ord3, "remuneraciones_pct"]], textposition="middle right", textfont=dict(size=10)))
    r19 = r["remuneraciones_pct_2019"]
    base(f3, f"Los salarios pesan más en las ventas: de {r19['46']:.1f}% a {m['remuneraciones_pct']:.1f}% en menudeo y de {r19['43']:.1f}% a {w['remuneraciones_pct']:.1f}% en mayoreo",
         "Censos 2019 y 2024: remuneraciones ÷ ingresos de cada censo (pesos del mismo año). Parte del cambio refleja personal que pasó de subcontratado a la nómina", alto=720, l=240)
    f3.update_xaxes(title_text="Remuneraciones, % de los ingresos")
    # 4) mercancías frente a salarios
    f4 = go.Figure()
    ord4 = e24.loc[[c for c in CORTO]].sort_values("abs_mercancias_1pct").index.tolist()
    f4.add_bar(y=[CORTO[c] for c in ord4], x=e24.loc[ord4, "abs_mercancias_1pct"], orientation="h", name="+1% en el costo de las mercancías", marker_color=GRIS, text=[f"{v:.1f}%" for v in e24.loc[ord4, "abs_mercancias_1pct"]], textposition="outside")
    f4.add_bar(y=[CORTO[c] for c in ord4], x=e24.loc[ord4, "abs_salarios_1pct"], orientation="h", name="+1% en salarios", marker_color=ROJO, text=[f"{v:.2f}%" for v in e24.loc[ord4, "abs_salarios_1pct"]], textposition="outside")
    base(f4, f"Un alza de 1% en mercancías sin traspaso absorbe {m['abs_mercancias_1pct']:.1f}% del excedente del menudeo; uno de 1% en salarios, {m['abs_salarios_1pct']:.2f}%",
         f"Mayoreo: {w['abs_mercancias_1pct']:.1f}% y {w['abs_salarios_1pct']:.2f}%. % del excedente absorbido si no se recupera en el precio. Traspaso de precios medido (INPP finales a INPC mercancías): {r['traspaso_bienes_6m']:.2f} a 6 meses (IC90 {r['traspaso_bienes_6m_ic90'][0]:.2f} a {r['traspaso_bienes_6m_ic90'][1]:.2f}) y {r['traspaso_bienes_12m']:.2f} a 12", alto=720, l=240)
    f4.update_xaxes(title_text="% del excedente absorbido", range=[0, e24.abs_mercancias_1pct.max() * 1.15])
    f4.update_layout(barmode="group")
    return [f1, f2, f3, f4], r, ex


CSS = """body{margin:0;font-family:Segoe UI,Arial,sans-serif;background:#ebebeb;color:#1f2937}header{background:#14284b;color:#fff;padding:18px 28px}
h1{margin:0;font-size:22px}.sub{color:#f0c36d;margin-top:4px}main{max-width:1100px;margin:18px auto;padding:0 16px}
.p{background:#fff;border:1px solid #d4d4d4;margin-bottom:16px;padding:8px 12px}.nota{background:#fff;border-left:5px solid #d98e04;padding:10px 16px;margin-bottom:16px}
.nota h2{font-size:16px;margin:4px 0 6px}li{margin:4px 0}"""


def construir():
    VIS.mkdir(exist_ok=True)
    figs, r, ex = figuras()
    sec = "".join(f'<section class="p">{f.to_html(full_html=False, include_plotlyjs=False, config={"displaylogo": False})}</section>' for f in figs)
    cu = ex[ex.cuadrante == "expuesta y con presión"].drop(index=["43", "46"], errors="ignore")
    nombres = ", ".join(CORTO[c].lower() for c in cu.index)
    cuerpo = f"""{sec}
<section class="nota"><h2>Qué significa para la empresa (interpretación)</h2><ul>
<li>El costo de las mercancías pesa mucho más que los salarios en el margen: por cada 1% de alza sin trasladar al precio, el costo de mercancías absorbe unas {r['menudeo']['abs_mercancias_1pct'] / r['menudeo']['abs_salarios_1pct']:.0f} veces más excedente que el salarial en menudeo y unas {r['mayoreo']['abs_mercancias_1pct'] / r['mayoreo']['abs_salarios_1pct']:.0f} veces más en mayoreo. El control de costos y de precios de compra es la palanca principal; los salarios importan por su ritmo de aumento.</li>
<li>Subsectores con estructura más expuesta a salarios y presión laboral reciente: {nombres}. Los más expuestos por estructura son {r['mas_expuesto_salarios'][0].lower()} ({r['mas_expuesto_salarios'][1]:.2f}% del excedente por cada 1% de salarios) y autoservicio y departamentales.</li>
<li>La presión laboral reciente más alta está en menudeo de abarrotes, alimentos y bebidas (el costo laboral por peso de ingreso subió 15.9% en 12 meses), aunque su estructura es la menos expuesta; el peso de los salarios en las ventas casi se duplicó entre censos en menudeo (efecto, en parte, de la nómina propia frente a la subcontratación).</li>
<li>Decisión que permite evaluar: dónde un aumento de costo de proveedor o de nómina debe trasladarse al precio primero, y qué margen de excedente queda para absorber un rezago de unos 3 meses en el traspaso (ver proyecto de traspaso de costos).</li></ul></section>
<section class="nota"><h2>Qué información empresarial faltaría para comprobar efectos sobre márgenes</h2><ul>
<li>Costos y márgenes reales por producto y cliente, con su mezcla de proveedores y contratos de precio; inventarios y rotación.</li>
<li>Nómina total incluyendo personal subcontratado, prestaciones y horas; rentas y costos de capital.</li>
<li>Capacidad de ajustar precios (elasticidad de la demanda y competencia local) y la fecha en que cada costo se traslada al precio.</li></ul></section>
<section class="nota"><h2>Límites</h2><ul>
<li>El excedente (valor agregado censal bruto menos remuneraciones) es un residuo antes de depreciación, intereses, impuestos y utilidades; en establecimientos micro incluye el ingreso del propietario que trabaja sin remuneración. No es utilidad ni margen financiero.</li>
<li>Los costos de mercancías son ingresos menos producción bruta (margen de comercialización) del censo; son razones nacionales promedio, no de una empresa. Las sensibilidades suponen que el alza no se traslada al precio: son aritmética del censo, no pronósticos.</li>
<li>Presión laboral observada con la EMEC (índices reales, a agosto de 2026; proyecto de costo laboral) y traspaso de precios con INPP e INPC (a septiembre de 2026; proyecto de traspaso): asociaciones históricas, no causalidad. Las remuneraciones se muestran en términos reales (sin tasas nominales).</li>
<li>El salario base de cotización del IMSS no se pudo obtener (su portal bloquea la descarga automatizada). Subsectores de EMEC (SCIAN 2013) y Censo 2024 (SCIAN 2023) se emparejan por código de 3 dígitos. Menudeo por internet no se incluye.</li></ul></section>"""
    html = (f'<!doctype html><html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Presión sobre los costos del comercio</title><style>{CSS}</style></head><body>'
            f'<script>{get_plotlyjs()}</script><header><h1>¿Qué subsectores comerciales están más expuestos a un alza de costos?</h1>'
            f'<div class="sub">Estructura de costos del Censo Económico, presión laboral reciente y traspaso de precios · INEGI</div></header><main>{cuerpo}</main></body></html>')
    (VIS / "presion_costos.html").write_text(html, encoding="utf-8")


if __name__ == "__main__":
    construir()
    print("listo")
