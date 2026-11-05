"""P05. Exposición de los subsectores comerciales a presiones de costos: estructura de costos censal y presión laboral observada.

Pregunta diferenciada de los proyectos 03 (traspaso INPP-INPC) y 04 (costo laboral EMEC): aquí se mide cuánto pesa cada costo en el ingreso de cada subsector
(Censos Económicos 2024 y 2019) y cuánto del excedente absorbería un alza de 1% en salarios o en mercancías; se combina con la presión laboral observada (04) y el traspaso medido (03).
Uso (desde la raíz del proyecto):  python src/calcular.py
Salidas en resultados/: estructura_costos.csv, exposicion.csv, estratos.csv, resumen.json
Descomposición de cada peso de ingreso (M000A): mercancías y otros costos de venta (ingresos - producción bruta), consumo intermedio (A121A), remuneraciones (J000A) y excedente (VACB - remuneraciones).
El excedente es un residuo censal antes de depreciación, intereses, impuestos y utilidades: no es utilidad ni margen financiero.
"""
import json
from pathlib import Path

import numpy as np
import pandas as pd

RAIZ = Path(__file__).resolve().parents[1]
NUEVOS = RAIZ.parent
SH = RAIZ.parents[1] / "DATOS_COMPARTIDOS" / "procesados"
RES = RAIZ / "resultados"
SUBS = {"431": "Mayoreo de abarrotes, alimentos, bebidas y tabaco", "432": "Mayoreo de textiles y calzado", "433": "Mayoreo de farmacia, perfumería y electrodomésticos",
        "434": "Mayoreo de materias primas y materiales", "435": "Mayoreo de maquinaria y equipo", "436": "Mayoreo de camiones y refacciones",
        "461": "Menudeo de abarrotes, alimentos y bebidas", "462": "Autoservicio y tiendas departamentales", "463": "Menudeo de textiles, ropa y calzado",
        "464": "Menudeo de salud y cuidado personal", "465": "Menudeo de papelería, esparcimiento y otros", "466": "Menudeo de enseres domésticos y mobiliario",
        "467": "Menudeo de ferretería, tlapalería y vidrios", "468": "Menudeo de vehículos, refacciones y combustibles"}
TOTALES = {"43": "Comercio al por mayor (total)", "46": "Comercio al por menor (total)"}
ESTRATOS = {"1": "0 a 10 personas", "2": "11 a 50", "3": "51 a 250", "4": "251 y más"}
EMEC_04 = NUEVOS / "04_costo_laboral_comercio" / "resultados" / "subsectores.csv"
TRASPASO_03 = NUEVOS / "03_traspaso_costos_precios" / "resultados" / "traspaso.csv"


def estructura(df):
    x = df.copy()
    x["mercancias_pct"] = (x.ingresos_mdp - x.produccion_bruta_mdp) / x.ingresos_mdp * 100
    x["consumo_intermedio_pct"] = x.consumo_intermedio_mdp / x.ingresos_mdp * 100
    x["remuneraciones_pct"] = x.remuneraciones_mdp / x.ingresos_mdp * 100
    x["excedente_pct"] = (x.vacb_mdp - x.remuneraciones_mdp) / x.ingresos_mdp * 100
    x["suma_pct"] = x.mercancias_pct + x.consumo_intermedio_pct + x.remuneraciones_pct + x.excedente_pct
    x["remuneraciones_sobre_vacb_pct"] = x.remuneraciones_mdp / x.vacb_mdp * 100
    x["abs_salarios_1pct"] = x.remuneraciones_pct * 0.01 / x.excedente_pct * 100          # % del excedente que absorbe un alza de 1% en salarios sin traspaso
    x["abs_mercancias_1pct"] = x.mercancias_pct * 0.01 / x.excedente_pct * 100            # idem para un alza de 1% en el costo de mercancías
    x["ingreso_por_persona_mdp"] = x.ingresos_mdp / x.personal
    return x


def construir():
    RES.mkdir(exist_ok=True)
    nac = pd.read_csv(SH / "ce_nacional_comercio.csv", dtype={"codigo": str, "estrato": str})
    nom = {**TOTALES, **SUBS}
    filas = []
    for a in (2019, 2024):
        t = nac[(nac.anio == a) & (nac.estrato == "T") & nac.codigo.isin(list(nom))]
        e = estructura(t).assign(actividad=lambda d: d.codigo.map(nom))
        filas.append(e)
    est = pd.concat(filas)
    cols = ["anio", "codigo", "actividad", "ue", "personal", "ingresos_mdp", "mercancias_pct", "consumo_intermedio_pct", "remuneraciones_pct", "excedente_pct", "suma_pct",
            "remuneraciones_sobre_vacb_pct", "abs_salarios_1pct", "abs_mercancias_1pct", "ingreso_por_persona_mdp"]
    est[cols].round(4).to_csv(RES / "estructura_costos.csv", index=False, encoding="utf-8-sig")
    # exposición: estructura 2024 + presión laboral observada (EMEC, proyecto 04) + traspaso medido (INPP-INPC, proyecto 03)
    e24 = est[est.anio == 2024].set_index("codigo")
    e19 = est[est.anio == 2019].set_index("codigo")
    emec = pd.read_csv(EMEC_04, dtype={"codigo": str}).set_index("codigo")
    ex = e24[["actividad", "personal", "ingresos_mdp", "remuneraciones_pct", "excedente_pct", "abs_salarios_1pct", "abs_mercancias_1pct"]].copy()
    ex["remuneraciones_pct_2019"] = e19.remuneraciones_pct
    ex["cambio_remuneraciones_pp"] = ex.remuneraciones_pct - ex.remuneraciones_pct_2019
    cols_e = ["remuneracion_media_var_12m_pct", "productividad_var_12m_pct", "costo_laboral_unitario_var_12m_pct", "costo_laboral_unitario_vs_2018_pct"]
    ex = ex.join(emec[cols_e], how="left")
    ex["presion_laboral_pp_ventas"] = ex.remuneraciones_pct * ex.costo_laboral_unitario_var_12m_pct / 100       # variación del costo laboral por peso de ingreso, en puntos del ingreso
    ex["presion_laboral_pct_excedente"] = ex.presion_laboral_pp_ventas / ex.excedente_pct * 100
    mediana_abs = float(ex.loc[list(SUBS)].abs_salarios_1pct.median())
    ex["estructura_expuesta"] = ex.abs_salarios_1pct > mediana_abs
    ex["presion_observada"] = ex.costo_laboral_unitario_var_12m_pct > 0
    ex["cuadrante"] = np.where(ex.estructura_expuesta & ex.presion_observada, "expuesta y con presión", np.where(ex.estructura_expuesta, "expuesta, sin presión reciente",
                              np.where(ex.presion_observada, "poco expuesta, con presión", "poco expuesta, sin presión")))
    ex.reset_index().round(4).to_csv(RES / "exposicion.csv", index=False, encoding="utf-8-sig")
    # tamaño de establecimiento (nacional, mayoreo y menudeo)
    es = nac[(nac.anio == 2024) & (nac.estrato.isin(list(ESTRATOS))) & nac.codigo.isin(["43", "46"])]
    et = estructura(es).assign(actividad=lambda d: d.codigo.map(TOTALES), estrato_desc=lambda d: d.estrato.map(ESTRATOS))
    et[["codigo", "actividad", "estrato", "estrato_desc", "ue", "personal", "mercancias_pct", "consumo_intermedio_pct", "remuneraciones_pct", "excedente_pct", "abs_salarios_1pct", "abs_mercancias_1pct"]].round(4).to_csv(
        RES / "estratos.csv", index=False, encoding="utf-8-sig")
    tr = pd.read_csv(TRASPASO_03).set_index("par")
    s = ex.loc[list(SUBS)]
    res = {"mediana_abs_salarios_1pct_subsectores": mediana_abs, "menudeo": {k: round(float(e24.loc["46", k]), 3) for k in ("mercancias_pct", "consumo_intermedio_pct", "remuneraciones_pct", "excedente_pct", "abs_salarios_1pct", "abs_mercancias_1pct")},
           "mayoreo": {k: round(float(e24.loc["43", k]), 3) for k in ("mercancias_pct", "consumo_intermedio_pct", "remuneraciones_pct", "excedente_pct", "abs_salarios_1pct", "abs_mercancias_1pct")},
           "remuneraciones_pct_2019": {c: round(float(e19.loc[c, "remuneraciones_pct"]), 3) for c in ("43", "46")},
           "mas_expuesto_salarios": [s.sort_values("abs_salarios_1pct").iloc[-1].actividad, float(s.abs_salarios_1pct.max())],
           "menos_expuesto_salarios": [s.sort_values("abs_salarios_1pct").iloc[0].actividad, float(s.abs_salarios_1pct.min())],
           "cuadrantes": s.cuadrante.value_counts().to_dict(), "traspaso_bienes_6m": float(tr.loc["A", "traspaso_6m"]), "traspaso_bienes_12m": float(tr.loc["A", "traspaso_12m"]),
           "traspaso_bienes_6m_ic90": [float(tr.loc["A", "traspaso_6m_ic90_bajo"]), float(tr.loc["A", "traspaso_6m_ic90_alto"])], "max_error_suma": float((est.suma_pct - 100).abs().max())}
    (RES / "resumen.json").write_text(json.dumps(res, indent=1, ensure_ascii=False), encoding="utf-8")
    return est, ex, et, res


if __name__ == "__main__":
    est, ex, et, res = construir()
    print(json.dumps(res, ensure_ascii=False))
    pd.set_option("display.width", 250)
    print(ex.loc[list(TOTALES) + list(SUBS)][["actividad", "remuneraciones_pct", "excedente_pct", "abs_salarios_1pct", "abs_mercancias_1pct", "costo_laboral_unitario_var_12m_pct", "presion_laboral_pp_ventas", "cuadrante"]].assign(actividad=lambda d: d.actividad.str[:34]).round(2).to_string())
    print(et.round(1)[["codigo", "estrato_desc", "mercancias_pct", "remuneraciones_pct", "excedente_pct", "abs_salarios_1pct"]].to_string(index=False))
