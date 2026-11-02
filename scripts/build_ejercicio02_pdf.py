"""Genera el PDF breve del Ejercicio 02 (entrega del mandato)."""

from __future__ import annotations

import json
import os
import re
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_JUSTIFY
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import Image, PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

#: URL del repositorio donde se publica esta entrega (se puede sobrescribir con la variable
#: de entorno REPO_URL al regenerar el PDF).
REPO_URL = os.getenv("REPO_URL", "")

ROOT = Path("/home/trek/source/uasd/cienciadedatos/tareas/Unidad_1/INF8239_U01")
REPORTS = ROOT / "reports"

resultados = json.loads((REPORTS / "green_ai_decision.json").read_text(encoding="utf-8"))
import pandas as pd

tabla = pd.read_csv(REPORTS / "green_ai_results.csv")
conclusion = (ROOT / "docs/CONCLUSION_EJERCICIO_02.md").read_text(encoding="utf-8")
cuerpo = conclusion.split("**Qué se comparó.**", 1)[1]
cuerpo = "**Qué se comparó.**" + cuerpo.split("**Pendiente crítico:**", 1)[0]


def negritas(texto: str) -> str:
    """Convierte **negrita** de Markdown en <b>...</b> para reportlab."""
    return re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", texto)

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
    ["Estudiante", "PENDIENTE: nombre completo y matrícula"],
    ["Correo institucional", "PENDIENTE: ID+USUARIO@users.noreply.github.com"],
    ["Profesor", "Edwin Ramón José Nolasco"],
    ["Repositorio", REPO_URL or "PENDIENTE: enlace de GitHub (publicar antes de entregar)"],
    ["Dataset (Ejercicio 01)", "Adult (Census Income) · UCI · CC BY 4.0"],
    ["Fecha de ejecución", "2026-11-02"],
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
    "one-hot dentro del pipeline) y mismo conjunto de prueba de 9.769 casos. Exclusiones "
    "semánticas: <font face='Courier'>fnlwgt, race, sex, native_country</font>.", styles["BodyJ"]))
story.append(Spacer(1, 6))

story.append(Paragraph("2. Tabla principal de resultados", styles["H1s"]))
filas = [["Configuración", "Familia", "F1 macro", "Accuracy", "Ajuste (s)", "Inferencia (ms)", "Tamaño (KB)", "Pareto"]]
for _, fila in tabla.sort_values("f1_macro", ascending=False).iterrows():
    filas.append([
        fila["configuracion"], fila["familia"], f"{fila['f1_macro']:.4f}", f"{fila['accuracy']:.4f}",
        f"{fila['fit_time_median_s']:.1f}", f"{fila['predict_time_median_ms']:.1f}",
        f"{fila['model_size_kb']:.0f}", "sí" if fila["is_pareto"] else "",
    ])
tabla_res = Table(filas, colWidths=[2.6 * cm, 3.0 * cm, 1.7 * cm, 1.7 * cm, 1.7 * cm, 2.2 * cm, 2.0 * cm, 1.3 * cm],
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
    f"Tiempos y tamaños: mediana de <b>3 repeticiones</b> de ajuste y de inferencia, y tamaño del "
    f"pipeline serializado. Configuración elegida en la frontera de Pareto: "
    f"<b>{resultados['configuracion_elegida']}</b> (F1 macro {resultados['f1_macro_elegida']:.4f}). "
    f"Diferencia absoluta frente a la mejor utilidad: {resultados['diferencia_absoluta_f1']:.4f} de F1 macro; "
    f"ahorro de tiempo: {resultados['ahorro_tiempo_porcentaje']:.1f} %; "
    f"diferencia de tamaño: {resultados['diferencia_tamano_kb']:.0f} KB. "
    f"Entorno: Python {resultados['entorno']['python']}, scikit-learn {resultados['entorno']['scikit_learn']}, "
    f"{resultados['entorno']['procesador']}, {resultados['entorno']['sistema']}.", styles["Small"]))
story.append(Spacer(1, 8))

story.append(Paragraph("3. Figuras", styles["H1s"]))
story.append(Paragraph("Figura 1. Frontera de Pareto: F1 macro frente a tiempo de ajuste (mediana de 3 repeticiones).", styles["Small"]))
story.append(Image(str(REPORTS / "pareto.png"), width=14.5 * cm, height=9.2 * cm))
story.append(Spacer(1, 4))
story.append(Paragraph("Figura 2. PCA: espectro de varianza y proyección 2D del conjunto de prueba.", styles["Small"]))
story.append(Image(str(REPORTS / "pca_analysis.png"), width=14.5 * cm, height=5.6 * cm))
story.append(Spacer(1, 4))
story.append(Paragraph("Figura 3. Dos mapas t-SNE sobre 6.000 casos de prueba, con semillas 42 y 7.", styles["Small"]))
story.append(Image(str(REPORTS / "tsne_two_seeds.png"), width=14.5 * cm, height=6.3 * cm))
story.append(Spacer(1, 4))

story.append(PageBreak())
story.append(Paragraph("4. Conclusión", styles["H1s"]))
for parrafo in cuerpo.strip().split("\n\n"):
    texto = negritas(parrafo.strip().replace("\n", " "))
    if texto:
        story.append(Paragraph(texto, styles["BodyJ"]))
        story.append(Spacer(1, 4))

story.append(Spacer(1, 6))
story.append(Paragraph(
    "<b>Estado pendiente:</b> la aprobación del docente sobre el dataset sigue sin recibirse (arrastrada "
    "del Ejercicio 01) y elExercise 02 se ejecutó con esa aprobación pendiente. El tiempo de ajuste y "
    "el tamaño del modelo son proxies contextuales de costo, <b>no</b> una medición de consumo "
    "energético: las cifras solo valen en el hardware registrado. El dataset es un censo de 1994–1996 y "
    "el recall de la clase <b>&gt;50K</b> sigue siendo el punto débil de todas las configuraciones.",
    styles["Small"]))

target = ROOT / "docs/EJERCICIO_02_PDF_BRIEF.pdf"
document = SimpleDocTemplate(str(target), pagesize=LETTER, title="Ejercicio 02 · INF-8239",
                              leftMargin=1.5 * cm, rightMargin=1.5 * cm, topMargin=1.5 * cm, bottomMargin=1.5 * cm)
document.build(story)
print("PDF generado:", target)
