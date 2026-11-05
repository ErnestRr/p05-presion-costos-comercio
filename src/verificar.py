"""Verificación independiente de P05 (lectura directa de los CSV oficiales de los ZIP y recálculo con numpy). Uso: python src/verificar.py"""
import json
import zipfile
from pathlib import Path

import numpy as np
import pandas as pd

RAIZ = Path(__file__).resolve().parents[1]
RES = RAIZ / "resultados"
CE = RAIZ.parents[1] / "DATOS_COMPARTIDOS" / "censos_economicos_2024"
n = 0


def ok(c, m):
    global n
    assert c, m
    n += 1


def raw(ruta, anio, codigos):
    z = zipfile.ZipFile(ruta)
    nm = [x for x in z.namelist() if "conjunto_de_datos" in x and "bitacora" not in x and x.endswith(".csv")][0]
    v = ["UE", "H001A", "J000A", "M000A", "A111A", "A121A", "A131A"]
    if anio == 2024:
        d = pd.read_csv(z.open(nm), dtype=str, usecols=["CODIGO", "ID_ESTRATO"] + v)
    else:
        d = pd.read_csv(z.open(nm), dtype=str, encoding="cp1252", index_col=False)
        d.columns = [c.strip().lstrip("﻿ï»¿") for c in d.columns]
        d = d[["CODIGO", "ID_ESTRATO"] + v]
    d["CODIGO"] = d.CODIGO.fillna("").str.strip()
    d = d[(d.ID_ESTRATO.fillna("").str.strip() == "") & d.CODIGO.isin(codigos)].set_index("CODIGO")
    return d[v].apply(pd.to_numeric)


est = pd.read_csv(RES / "estructura_costos.csv", dtype={"codigo": str})
ex = pd.read_csv(RES / "exposicion.csv", dtype={"codigo": str}).set_index("codigo")
res = json.loads((RES / "resumen.json").read_text(encoding="utf-8"))
cod = ["43", "46", "461", "462", "464", "431", "434"]
for a, ruta in ((2019, CE / "nac19" / "ce2019_nac_csv.zip"), (2024, CE / "conjunto_de_datos_ce_nac_2024_csv.zip")):
    d = raw(ruta, a, cod)
    e = est[est.anio == a].set_index("codigo")
    for c in cod:
        x = d.loc[c]
        ok(abs(x.J000A / x.M000A * 100 - e.loc[c, "remuneraciones_pct"]) < 1e-3, ("remuneraciones/ingresos", a, c))
        ok(abs((x.A131A - x.J000A) / x.M000A * 100 - e.loc[c, "excedente_pct"]) < 1e-3, ("excedente", a, c))
        ok(abs((x.M000A - x.A111A) / x.M000A * 100 - e.loc[c, "mercancias_pct"]) < 1e-3, ("mercancías", a, c))
        ok(abs(x.A111A - x.A121A - x.A131A) / x.A111A < 0.005, ("identidad censal PB - CI = VACB", a, c))
        ok(abs(x.J000A * 0.01 / (x.A131A - x.J000A) * 100 - e.loc[c, "abs_salarios_1pct"]) < 1e-3, ("absorción salarios", a, c))
ok(res["max_error_suma"] < 1e-6, "los cuatro componentes suman 100")
# presión laboral: producto de la razón censal y el cambio EMEC (proyecto 04) recalculado
emec = pd.read_csv(RAIZ.parent / "04_costo_laboral_comercio" / "resultados" / "subsectores.csv", dtype={"codigo": str}).set_index("codigo")
for c in ("461", "462", "464"):
    ok(abs(ex.loc[c, "remuneraciones_pct"] * emec.loc[c, "costo_laboral_unitario_var_12m_pct"] / 100 - ex.loc[c, "presion_laboral_pp_ventas"]) < 1e-3, ("presión laboral", c))
tr = pd.read_csv(RAIZ.parent / "03_traspaso_costos_precios" / "resultados" / "traspaso.csv").set_index("par")
ok(abs(tr.loc["A", "traspaso_6m"] - res["traspaso_bienes_6m"]) < 1e-9, "traspaso del proyecto 03")
sub = ex.drop(index=["43", "46"])
ok(abs(sub.abs_salarios_1pct.median() - res["mediana_abs_salarios_1pct_subsectores"]) < 1e-3, "mediana")
ok(set(sub.cuadrante) <= {"expuesta y con presión", "expuesta, sin presión reciente", "poco expuesta, con presión", "poco expuesta, sin presión"} and sub.cuadrante.notna().all(), "cuadrantes")
h = (RAIZ / "visualizaciones" / "presion_costos.html").read_text(encoding="utf-8")
ok("Límites" in h and "Qué información empresarial faltaría" in h and f"{res['menudeo']['abs_mercancias_1pct']:.1f}%" in h, "texto HTML")
print(f"verificación correcta: {n} comprobaciones")
