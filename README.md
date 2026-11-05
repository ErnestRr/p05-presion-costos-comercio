# P05. ¿Qué subsectores comerciales están más expuestos a un alza de costos?

**Pregunta empresarial.** Cuando suben los salarios o los costos de mercancías, ¿qué parte del excedente de cada subsector comercial absorbería el aumento si no se traslada al precio, y dónde coincide esa exposición con presión reciente?

**Enfoque.** Complementa el análisis de ritmos de precios (INPP frente a INPC) y de salarios (EMEC) con la **estructura de costos** de cada subsector (Censos Económicos): pasa de porcentajes de cambio a puntos del ingreso y a la parte del excedente afectada.

## Fuentes y fechas (INEGI)
- **Censos Económicos 2024 y 2019**, conjuntos nacionales (descarga pública del INEGI): ingresos, producción bruta, consumo intermedio, valor agregado censal bruto (VACB), remuneraciones, personal y unidades por subsector y estrato.
- **EMEC** (hasta ago 2026): costo laboral por peso de ingreso en 12 meses, (análisis previo de costo laboral en comercio).
- **INPP e INPC** (hasta sep 2026): traspaso medido de precios de bienes finales a mercancías, (análisis previo de traspaso de costos a precios).
- IMSS (salario base de cotización): no obtenible (su portal bloquea la descarga automatizada).

## Metodología
- Cada $100 de ingresos se descomponen en: mercancías y otros costos de venta (ingresos − producción bruta), consumo intermedio, remuneraciones y excedente (VACB − remuneraciones). Los cuatro suman 100 y se verificó la identidad censal producción bruta − consumo intermedio = VACB.
- Sensibilidad (aritmética, no pronóstico): % del excedente que absorbe un alza de 1% en salarios o en el costo de mercancías sin traslado al precio.
- Presión laboral observada = remuneraciones como % de ventas × cambio del costo laboral por peso de ingreso (EMEC, 12 meses), en puntos del ingreso. Cuadrantes con la mediana de exposición salarial de los 14 subsectores. Salarios en términos reales (sin tasas nominales).

## Hallazgos
1. De cada $100 de venta, el **menudeo** gasta $68.0 en mercancías y otros costos de venta, $7.9 en otros gastos, **$5.6 en salarios** y le quedan **$18.5** de excedente; el **mayoreo**, $71.2, $7.9, **$3.3** y **$17.7**.
2. Un alza de **1% en el costo de mercancías** sin traslado al precio absorbería **3.7%** del excedente del menudeo y **4.0%** del mayoreo; una de 1% en salarios, **0.30%** y **0.19%**: unas 12 y 22 veces menos. Mayor sensibilidad a mercancías: mayoreo de materias primas (7.1%), autoservicio y departamentales (5.0%) y menudeo de vehículos y combustibles (4.7%).
3. Los salarios pesan más en las ventas que en 2019: de **3.0% a 5.6%** en menudeo y de 2.4% a 3.3% en mayoreo (en parte, personal que pasó de subcontratado a la nómina).
4. Estructura más expuesta a salarios: menudeo de salud y cuidado personal (0.53% del excedente por cada 1%; salarios 9.7% de las ventas) y autoservicio y departamentales (0.47%); la menos expuesta, menudeo de abarrotes y alimentos (0.16%).
5. **Expuestos y con presión laboral reciente:** autoservicio y departamentales, menudeo de papelería y esparcimiento y mayoreo de camiones y refacciones. Menudeo de abarrotes, poco expuesto por estructura, tuvo la mayor presión (costo laboral por peso de ingreso +15.9% en 12 meses, 0.69 puntos de las ventas, 2.5% de su excedente).
6. Con el traspaso medido de bienes (0.56 a 6 meses, IC90 0.25 a 0.79; 0.90 a 12), el comercio de bienes recupera en el precio una parte del alza de mercancías en unos 3 a 12 meses; el resto se absorbe en ese lapso.

## Implicación para la gestión de costos
El costo de compra de mercancías, no la nómina, domina la sensibilidad del margen: conviene priorizar la renegociación y el traslado de costos de proveedor y, aparte, vigilar el ritmo salarial en los subsectores con estructura expuesta. Decisión que permite evaluar: dónde trasladar primero un aumento de costo y cuánto excedente queda para absorber el rezago.

## Información empresarial que faltaría para comprobar efectos sobre márgenes
Costos y márgenes por producto y cliente, mezcla y contratos de proveedores, nómina total incluida la subcontratada, rentas y costos de capital, capacidad de ajustar precios (elasticidad) y calendario de traslado de cada costo.

## Limitaciones
- El excedente es un residuo censal antes de depreciación, intereses, impuestos y utilidades; en micro-establecimientos incluye el ingreso del propietario. No es utilidad.
- Razones nacionales promedio por subsector, no de una empresa; sensibilidades sin traslado al precio; presión laboral y traspaso son asociaciones históricas, no causalidad.
- Censo 2019 (SCIAN 2018) y 2024 (SCIAN 2023); EMEC (SCIAN 2013) emparejada por código de 3 dígitos; menudeo por internet y subsectores pequeños no se incluyen.

## Reproducir
Requiere Python con pandas, numpy y plotly.
```
python src/graficar.py     # visualizaciones/presion_costos.html, a partir de resultados/
```
`src/calcular.py` y `src/verificar.py` regeneran y validan los resultados (78 comprobaciones) a partir de los microdatos del Censo Económico y de los resultados de costo laboral y traspaso de precios; esos insumos no se incluyen en este repositorio (ajusta las rutas al inicio de cada script).

## Contenido
- `resultados/`: tablas de estructura de costos, exposición por subsector y estrato, y resumen.
- `visualizaciones/presion_costos.html`: gráficas interactivas.
- `src/`: cálculo, gráficas y verificación.
