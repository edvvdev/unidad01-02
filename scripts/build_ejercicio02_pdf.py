"""Genera el PDF breve del Ejercicio 02 (entrega del mandato).

Todas las cifras salen de `reports/` (misma fuente que el README y la conclusión) y el texto de la
conclusión se toma del documento que genera `scripts/generar_conclusion.py`, de modo que el PDF no
pueda contradecir a los artefactos de la corrida.
"""

from __future__ import annotations

import os
import re
import sys
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_JUSTIFY
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (
    Image,
    KeepTogether,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from inf8239_u01 import informe

#: URL del repositorio donde se publica esta entrega. Se puede sobrescribir con la variable de
#: entorno REPO_URL al regenerar el PDF.
REPO_URL = os.getenv("REPO_URL", "https://github.com/edvvdev/unidad01-02")

REPORTS = ROOT / "reports"
DOCS = ROOT / "docs"

cifras = informe.cargar_cifras(REPORTS)
valores = cifras.valores()
entorno = valores["entorno"]

documento_conclusion = (DOCS / "CONCLUSION_EJERCICIO_02.md").read_text(encoding="utf-8")
cuerpo = documento_conclusion.split(informe.MARCADOR_CUERPO_INICIO, 1)[1]
cuerpo = cuerpo.split(informe.MARCADOR_CUERPO_FIN, 1)[0]
referencias = documento_conclusion.split("## Referencias", 1)[1].split("## Figuras", 1)[0]


def markdown(texto: str) -> str:
    """Convierte el Markdown de la documentación en etiquetas que entienda reportlab."""
    escapado = texto.replace("&", "&amp;")
    escapado = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", escapado)
    escapado = re.sub(r"`(.+?)`", r"<font face='Courier'>\1</font>", escapado)
    escapado = re.sub(r"\*(.+?)\*", r"<i>\1</i>", escapado)
    return escapado


styles = getSampleStyleSheet()
styles.add(ParagraphStyle(name="Title2", parent=styles["Title"], fontSize=17, spaceAfter=6))
styles.add(ParagraphStyle(name="H1s", parent=styles["Heading1"], fontSize=12.5, spaceBefore=10, spaceAfter=4))
styles.add(ParagraphStyle(name="BodyJ", parent=styles["BodyText"], alignment=TA_JUSTIFY, leading=13.5, fontSize=9.6))
styles.add(ParagraphStyle(name="Small", parent=styles["BodyText"], fontSize=8.2, leading=10.5))

story = []
story.append(Paragraph("Ejercicio 02 · Ensambles, reducción dimensional y Green AI", styles["Title2"]))
story.append(Paragraph(
    "INF-8239 Ciencia de Datos II (UASD) · Unidad 01 · Integración de LAB03 · Código U01.E02",
    styles["Small"]))
story.append(Spacer(1, 6))

identificacion = [
    ["Estudiante", "Edwing Perez"],
    ["Profesor", "Edwin Ramón José Nolasco"],
    ["Repositorio", REPO_URL],
    ["Dataset (Ejercicio 01)", "Adult (Census Income) · UCI · CC BY 4.0"],
    ["Fecha de ejecución", valores["fecha"]],
]
tabla_id = Table(identificacion, colWidths=[4.6 * cm, 11.2 * cm])
tabla_id.setStyle(TableStyle([
    ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#94a3b8")),
    ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#f1f5f9")),
    ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
    ("FONTSIZE", (0, 0), (-1, -1), 8.4),
    ("LEFTPADDING", (0, 0), (-1, -1), 5),
    ("TOPPADDING", (0, 0), (-1, -1), 3),
]))
story.append(tabla_id)
story.append(Spacer(1, 10))

story.append(Paragraph("1. Identificación del dataset y protocolo", styles["H1s"]))
story.append(Paragraph(
    "<b>Adult (Census Income)</b> · UCI Machine Learning Repository · licencia <b>CC BY 4.0</b> · "
    "<font face='Courier'>https://archive.ics.uci.edu/static/public/2/adult.zip</font>.<br/>"
    "Target <b>income</b> (<=50K / >50K). Se conservan <b>dataset, target y partición estratificada "
    "80/20 con semilla 42 del Ejercicio 01</b>: mismo preprocesamiento (imputación, estandarización y "
    f"one-hot dentro del pipeline) y mismo conjunto de prueba de {informe.formatear(valores['filas_prueba'], 0)} casos. "
    "Exclusiones semánticas: <font face='Courier'>fnlwgt, race, sex, native_country</font>.", styles["BodyJ"]))
story.append(Spacer(1, 6))

story.append(Paragraph("2. Tabla principal de resultados", styles["H1s"]))
filas = [["Configuración", "Familia", "F1 macro", "Accuracy", "Ajuste (s)", "Inferencia (ms)", "Tamaño (KB)", "Pareto"]]
for _, fila in cifras.resultados.sort_values("f1_macro", ascending=False).iterrows():
    filas.append([
        fila["configuracion"],
        informe.DESCRIPCIONES_CORTAS.get(str(fila["configuracion"]), fila["familia"]),
        informe.formatear(fila["f1_macro"]),
        informe.formatear(fila["accuracy"]),
        informe.formatear(fila["fit_time_median_s"], informe.DECIMALES_TIEMPO),
        informe.formatear(fila["predict_time_median_ms"], informe.DECIMALES_INFERENCIA),
        informe.formatear(fila["model_size_kb"], informe.DECIMALES_TAMANO),
        "sí" if fila["is_pareto"] else "",
    ])
tabla_res = Table(filas, colWidths=[2.3 * cm, 3.3 * cm, 1.6 * cm, 1.7 * cm, 1.6 * cm, 2.2 * cm, 2.0 * cm, 1.5 * cm],
                   repeatRows=1)
tabla_res.setStyle(TableStyle([
    ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#94a3b8")),
    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0f7c7b")),
    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
    ("FONTSIZE", (0, 0), (-1, -1), 7.6),
    ("ALIGN", (2, 1), (-1, -1), "CENTER"),
    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f8fafc")]),
    ("TOPPADDING", (0, 0), (-1, -1), 3),
    ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
]))
story.append(tabla_res)
story.append(Spacer(1, 4))
story.append(Paragraph(
    "Tiempos y tamaños: mediana de <b>3 repeticiones</b> de ajuste y de inferencia, y tamaño del "
    f"pipeline serializado. Configuración elegida en la frontera de Pareto: "
    f"<b>{valores['elegida']}</b> (F1 macro {informe.formatear(valores['f1_elegida'])}). "
    f"Diferencia absoluta frente a la mejor utilidad: {informe.formatear(valores['diferencia_absoluta_f1'], 2)} de F1 macro; "
    f"ahorro de tiempo: {informe.formatear(cifras.decision['ahorro_tiempo_porcentaje'], 1)} %; "
    f"diferencia de tamaño: {informe.formatear(cifras.decision['diferencia_tamano_kb'], 0)} KB. "
    f"El SVM infiere {informe.formatear(valores['ratio_inferencia_svm'], 0)} veces más lento que el boosting "
    f"({informe.formatear(valores['inferencia_svm_ms'], 1)} ms frente a "
    f"{informe.formatear(valores['inferencia_elegida_ms'], 1)} ms) y el recall de "
    f"<b>&gt;50K</b> va de {informe.formatear(valores['recall_minimo'])} "
    f"(<font face='Courier'>{valores['configuracion_recall_minimo']}</font>) a "
    f"{informe.formatear(valores['recall_maximo'])} "
    f"(<font face='Courier'>{valores['configuracion_recall_maximo']}</font>). "
    f"Entorno: Python {entorno['python']}, scikit-learn {entorno['scikit_learn']}, "
    f"{entorno['procesador']}, {entorno['sistema']}.", styles["Small"]))
story.append(Spacer(1, 8))

story.append(PageBreak())
story.append(Paragraph("3. Figuras", styles["H1s"]))
story.append(KeepTogether([
    Paragraph(
        "Figura 1. Frontera de Pareto: F1 macro frente a tiempo de ajuste (mediana de 3 repeticiones) y frente "
        "al tamaño del modelo (<font face='Courier'>reports/pareto.png</font>).", styles["Small"]),
    Image(str(REPORTS / "pareto.png"), width=14.5 * cm, height=8.6 * cm),
]))
story.append(Spacer(1, 6))
story.append(KeepTogether([
    Paragraph(
        "Figura 2. PCA: espectro de varianza y proyección 2D del conjunto de prueba "
        f"(<font face='Courier'>reports/pca_analysis.png</font>); hacen falta "
        f"{valores['componentes_90']} componentes para el 90 % de la varianza y "
        f"{valores['componentes_95']} para el 95 %.", styles["Small"]),
    Image(str(REPORTS / "pca_analysis.png"), width=14.5 * cm, height=5.4 * cm),
]))

story.append(PageBreak())
story.append(KeepTogether([
    Paragraph(
        f"Figura 3. Dos mapas t-SNE sobre {informe.formatear(valores['tsne_casos'], 0)} casos de prueba con "
        "submuestra <b>uniforme</b> (no estratificada), con semillas 42 y 7 "
        f"(<font face='Courier'>reports/tsne_two_seeds.png</font>).", styles["Small"]),
    Image(str(REPORTS / "tsne_two_seeds.png"), width=14.5 * cm, height=6.1 * cm),
]))
story.append(Spacer(1, 6))
story.append(KeepTogether([
    Paragraph(
        "Figura 4. Perfil de las diez categorías más frecuentes de <font face='Courier'>occupation</font> y "
        "proporción de <b>&gt;50K</b> en cada una "
        "(<font face='Courier'>reports/popular_top10.png</font>).", styles["Small"]),
    Image(str(REPORTS / "popular_top10.png"), width=14.5 * cm, height=5.4 * cm),
]))

story.append(PageBreak())
story.append(Paragraph("4. Conclusión", styles["H1s"]))
for parrafo in cuerpo.strip().split("\n\n"):
    texto = markdown(parrafo.strip().replace("\n", " "))
    if texto:
        story.append(Paragraph(texto, styles["BodyJ"]))
        story.append(Spacer(1, 4))

story.append(Spacer(1, 4))
story.append(Paragraph("5. Referencias", styles["H1s"]))
for linea in referencias.strip().split("\n"):
    if linea.strip().startswith("-"):
        story.append(Paragraph(markdown(linea.strip()[1:].strip()), styles["Small"]))
        story.append(Spacer(1, 2))

story.append(Spacer(1, 6))
story.append(Paragraph(
    "<b>Estado pendiente y alcance.</b> La aprobación del docente sobre el dataset sigue pendiente, tal como "
    "se detalla en el último párrafo de la conclusión. El dataset es un censo de 1994–1996 de la población "
    "activa estadounidense: los resultados no son extrapolables a la población actual y no autorizan decisiones "
    "sobre personas. Los tiempos de ajuste y de inferencia y el tamaño de los pipelines son <b>proxies "
    "contextuales de costo</b> medidos en esta máquina: en otro hardware cambian, y la cifra vigente está "
    "siempre en <font face='Courier'>reports/green_ai_results.csv</font> y "
    "<font face='Courier'>reports/green_ai_decision.json</font>.", styles["Small"]))

target = DOCS / "EJERCICIO_02_PDF_BRIEF.pdf"
document = SimpleDocTemplate(str(target), pagesize=LETTER, title="Ejercicio 02 · INF-8239",
                              leftMargin=1.5 * cm, rightMargin=1.5 * cm, topMargin=1.5 * cm, bottomMargin=1.5 * cm)
document.build(story)
print("PDF generado:", target)
