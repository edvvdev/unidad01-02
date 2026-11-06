#!/usr/bin/env python3
"""Verifica que las cifras publicadas coincidan con los artefactos de `reports/`.

Contrasta el README, `docs/CONCLUSION_EJERCICIO_02.md`, el notebook del LAB03 y el PDF breve del
Ejercicio 02 contra `reports/green_ai_results.csv`, `reports/green_ai_decision.json` y los informes
auxiliares que escribe el notebook. Sale con código 1 en cuanto una cifra publicada no coincide,
sobrevive una cifra de la corrida anterior o una figura apunta a un archivo inexistente.
"""

from __future__ import annotations

import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
REPORTS = ROOT / "reports"
sys.path.insert(0, str(ROOT / "src"))

from inf8239_u01 import informe

#: Números que aparecen en la prosa y no provienen de `reports/`, con su justificación.
CONTEXTUALES = {
    5: "folds de la validación cruzada (LAB01 y LAB02)",
    7: "minutos estimados de ejecución del LAB02",
    10: "minutos estimados de ejecución del LAB03",
    11: "mes de ejecución de la entrega",
    15: "minutos estimados de ejecución del LAB03",
    21: "pruebas del proyecto",
    25: "submuestra estratificada del 25 % usada en la búsqueda de hiperparámetros del LAB02",
    30: "muestras y variables del dataset de Wisconsin; orden de magnitud del ajuste completo del SVM",
    64: "arquitectura x86_64 registrada en reports/green_ai_decision.json",
    80: "porcentaje de entrenamiento de la partición 80/20",
    86: "arquitectura x86_64 registrada en reports/green_ai_decision.json",
    90: "porcentaje de varianza objetivo del PCA",
    95: "porcentaje de varianza objetivo del PCA",
    100: "número de árboles del Random Forest de 100 del catálogo",
    256: "longitud del resumen SHA-256 del dataset",
    300: "número de árboles del Random Forest de 300 del catálogo",
    350: "extensión de la conclusión en palabras",
    569: "muestras del dataset de Wisconsin (load_breast_cancer)",
    1994: "inicio del censo del dataset Adult",
    1996: "fin del censo del dataset Adult",
    2026: "año de ejecución de la entrega",
    8239: "código del curso INF-8239",
}

#: Cadenas de la corrida anterior que no deben sobrevivir en ningún documento publicado.
HEREDADAS = (
    "214 veces",
    "98,4 MB",
    "296,9 MB",
    "0,18 s",
    "31,3 s",
    "43,9 s",
    "5.228 s",
    "24,4 ms",
    "58 columnas",
    "0,66 en todas",
    "18 componentes",
    "elExercise",
)

#: Rótulo que no puede describir la submuestra de t-SNE (el muestreo es uniforme).
ROTULOS_ESTRATIFICADOS = (
    "submuestra estratificada de 6.000",
    "submuestra estratificada con semilla",
    "submuestra estratificada, semilla",
)

#: Archivos de `reports/` que deben existir y estar citados en los cuatro documentos.
FIGURAS_LAB03 = (
    "reports/pareto.png",
    "reports/pca_analysis.png",
    "reports/popular_top10.png",
    "reports/tsne_two_seeds.png",
)

#: Expresión regular que encuentra números escritos en la convención española o inglesa.
NUMERO = re.compile(r"(?<!\w)\d+(?:[.,]\d+)*")

#: Rutas a `reports/` citadas en los documentos.
RUTA_REPORTS = re.compile(r"reports/[\w.*-]+\.(?:png|csv|json)")

#: Bloque de código delimitado por comillas invertidas.
CODIGO = re.compile(r"```.*?```", re.DOTALL)


def es(valor: float, decimales: int) -> str:
    """Formatea un número con la convención española (la misma que usa la documentación)."""
    return informe.formatear(valor, decimales)


def py(valor: float, decimales: int) -> str:
    """Formatea un número como lo imprime Python (la convención de las salidas del notebook)."""
    return f"{valor:.{decimales}f}"


def limpiar(texto: str) -> str:
    """Quita bloques de código, filas de tabla sin datos, referencias y líneas con direcciones web."""
    texto = CODIGO.sub(" ", texto)
    lineas = []
    en_referencias = False
    for linea in texto.splitlines():
        if linea.lstrip().startswith(("## Referencias", "5. Referencias")):
            en_referencias = True
        if en_referencias or "http" in linea:
            continue
        if re.fullmatch(r"[\s|:\-]+", linea):
            continue
        lineas.append(linea)
    return "\n".join(lineas)


def candidatos(token: str) -> list[float]:
    """Interpretaciones posibles de un token numérico (millares con punto o decimal con coma)."""
    valores = []
    if re.fullmatch(r"\d{1,3}(?:\.\d{3})+", token):
        valores.append(float(token.replace(".", "")))
    if re.fullmatch(r"\d{1,3}(?:\.\d{3})+(?:,\d+)?", token):
        valores.append(float(token.replace(".", "").replace(",", ".")))
    if re.fullmatch(r"\d+(?:,\d+)?", token):
        valores.append(float(token.replace(",", ".")))
    if re.fullmatch(r"\d+\.\d+", token):
        valores.append(float(token))
    if re.fullmatch(r"\d+", token):
        valores.append(float(token))
    return valores


def recolectar(valor, acumulador: set[float]) -> None:
    """Suma un valor (o un diccionario/lista) al conjunto de números permitidos."""
    if isinstance(valor, bool):
        return
    if isinstance(valor, (int, float)):
        acumulador.add(float(valor))
    elif isinstance(valor, dict):
        for elemento in valor.values():
            recolectar(elemento, acumulador)
    elif isinstance(valor, list):
        for elemento in valor:
            recolectar(elemento, acumulador)
    elif isinstance(valor, str):
        try:
            acumulador.add(float(valor))
        except ValueError:
            return


def valores_permitidos() -> set[float]:
    """Números respaldados por los artefactos de `reports/` (más sus redondeos publicados)."""
    permitidos: set[float] = set()
    for ruta in sorted(REPORTS.glob("*.json")):
        recolectar(json.loads(ruta.read_text(encoding="utf-8")), permitidos)
    for ruta in sorted(REPORTS.glob("*.csv")):
        recolectar(pd.read_csv(ruta).to_numpy().tolist(), permitidos)
    permitidos.update(float(valor) for valor in CONTEXTUALES)
    redondeados = set(permitidos)
    for valor in permitidos:
        for decimales in range(7):
            redondeados.add(round(valor, decimales))
    return redondeados


def texto_pdf(ruta: Path) -> str | None:
    """Texto del PDF con `pdftotext` (si el programa no está instalado, devuelve None)."""
    if shutil.which("pdftotext") is None:
        return None
    resultado = subprocess.run(
        ["pdftotext", "-layout", str(ruta), "-"],
        capture_output=True,
        check=True,
        text=True,
    )
    return resultado.stdout


def celdas(notebook: Path) -> list[dict]:
    """Celdas de código del notebook con su fuente y sus salidas."""
    contenido = json.loads(notebook.read_text(encoding="utf-8"))
    encontradas = []
    for celda in contenido["cells"]:
        if celda["cell_type"] != "code":
            continue
        salidas = []
        for salida in celda.get("outputs", []):
            if "text" in salida:
                salidas.append("".join(salida["text"]))
            elif "data" in salida and "text/plain" in salida["data"]:
                salidas.append("".join(salida["data"]["text/plain"]))
        encontradas.append({
            "fuente": "".join(celda["source"]),
            "salida": "\n".join(salidas),
            "errores": [salida for salida in celda.get("outputs", []) if salida.get("output_type") == "error"],
        })
    return encontradas


def comprobar(condicion: bool, mensaje: str, fallos: list[str]) -> None:
    """Registra un fallo si la condición no se cumple."""
    if not condicion:
        fallos.append(mensaje)


def fila_de(resultados: pd.DataFrame, nombre: str) -> pd.Series:
    """Fila del catálogo que corresponde a una configuración."""
    coincidencia = resultados[resultados["configuracion"] == nombre]
    if coincidencia.empty:
        raise KeyError(f"La configuración {nombre} no está en reports/green_ai_results.csv")
    return coincidencia.iloc[0]


def cifras_catalogo(resultados: pd.DataFrame, formato) -> list[tuple[str, str]]:
    """Las cinco magnitudes de cada configuración, con el formato que publica cada documento."""
    cifras = []
    for _, fila in resultados.iterrows():
        nombre = str(fila["configuracion"])
        cifras.append((f"F1 macro de {nombre}", formato(fila["f1_macro"], 4)))
        cifras.append((f"accuracy de {nombre}", formato(fila["accuracy"], 4)))
        cifras.append((f"tiempo de ajuste de {nombre}", formato(fila["fit_time_median_s"], 2)))
        cifras.append((f"inferencia de {nombre}", formato(fila["predict_time_median_ms"], 1)))
        cifras.append((f"tamaño de {nombre}", formato(fila["model_size_kb"], 0)))
    return cifras


def cifras_catalogo_notebook(resultados: pd.DataFrame) -> list[tuple[str, str]]:
    """Cifras tal como las imprime la celda del catálogo del notebook."""
    cifras = []
    for _, fila in resultados.iterrows():
        nombre = str(fila["configuracion"])
        cifras.append((f"F1 macro de {nombre}", py(fila["f1_macro"], 4)))
        cifras.append((f"tiempo de ajuste de {nombre}", py(fila["fit_time_median_s"], 2)))
        cifras.append((f"inferencia de {nombre}", py(fila["predict_time_median_ms"], 1)))
        cifras.append((f"tamaño de {nombre}", py(fila["model_size_kb"], 1)))
    return cifras


def cifras_decision(decision: dict) -> list[tuple[str, str]]:
    """Cifras de la decisión cuantificada (presentes en todos los documentos narrativos)."""
    return [
        ("F1 macro de la configuración elegida", es(decision["f1_macro_elegida"], 4)),
        ("tiempo de ajuste de la elegida", es(decision["tiempo_elegida_s"], 2)),
        ("tamaño de la elegida", es(decision["tamano_elegida_kb"], 0)),
        ("inferencia de la elegida", es(decision["inferencia_elegida_ms"], 1)),
        ("diferencia absoluta de F1 macro", es(decision["diferencia_absoluta_f1"], 2)),
        ("diferencia de F1 macro frente a la alternativa", es(decision["diferencia_f1_vs_alternativa"], 4)),
        ("F1 macro de la alternativa de la frontera", es(decision["f1_macro_alternativa"], 4)),
        ("ratio de inferencia del SVM frente al boosting", es(decision["ratio_inferencia_svm_sobre_boost"], 0)),
        ("inferencia del SVM en ms", es(decision["inferencia_svm_c10_ms"], 1)),
        ("tamaño del Random Forest de 300 árboles en MB", es(decision["tamano_rf_300_kb"] / 1024, 1)),
    ]


def cifras_narrativa(resultados: pd.DataFrame, decision: dict, contexto: dict) -> list[tuple[str, str]]:
    """Cifras que aparecen en la prosa de la decisión y de la conclusión."""
    svm = fila_de(resultados, "svm_c10")
    svm_pca = fila_de(resultados, "svm_c10_pca")
    peor = resultados.loc[resultados["f1_macro"].idxmin()]
    recall_min = resultados.loc[resultados["recall_mas_50k"].idxmin()]
    recall_max = resultados.loc[resultados["recall_mas_50k"].idxmax()]
    alternativa = fila_de(resultados, decision["alternativa_en_la_frontera"])
    return [
        ("F1 macro mínimo del catálogo", es(peor["f1_macro"], 4)),
        ("recall de >50K mínimo", es(recall_min["recall_mas_50k"], 4)),
        ("recall de >50K máximo", es(recall_max["recall_mas_50k"], 4)),
        ("tiempo de ajuste de la alternativa de la frontera", es(alternativa["fit_time_median_s"], 2)),
        ("diferencia de tamaño frente a la alternativa en MB", es(
            abs(decision["diferencia_tamano_vs_alternativa_kb"]) / 1024, 1)),
        ("diferencia de F1 macro del PCA en el SVM", es(svm["f1_macro"] - svm_pca["f1_macro"], 4)),
        ("tiempo de ajuste del SVM", es(svm["fit_time_median_s"], 2)),
        ("tamaño del SVM en MB", es(svm["model_size_kb"] / 1024, 1)),
        ("tiempo de ajuste del SVM con PCA", es(svm_pca["fit_time_median_s"], 2)),
        ("tamaño del SVM con PCA en MB", es(svm_pca["model_size_kb"] / 1024, 1)),
        ("proporción de >50K en la submuestra de t-SNE", es(contexto["tsne_proporcion_mas_50k"] * 100, 2)),
        ("proporción de >50K en la prueba", es(contexto["proporcion_mas_50k_prueba"] * 100, 2)),
        ("porcentaje de filas con capital_gain en cero", es(contexto["capital_gain_cero_porcentaje"], 2)),
    ]


def cifras_limitaciones(contexto: dict) -> list[tuple[str, str]]:
    """Cifras de la matriz densa y de la submuestra de t-SNE."""
    return [
        ("filas de la matriz densa de entrenamiento", es(contexto["filas_entrenamiento"], 0)),
        ("columnas de la matriz densa de entrenamiento", es(contexto["columnas_matriz_densa"], 0)),
        ("tamaño de la matriz densa de entrenamiento en MB", es(contexto["matriz_densa_mb"], 1)),
        ("casos de la submuestra de t-SNE", es(contexto["tsne_casos"], 0)),
    ]


def comprobar_cifras_clave(exigidas: dict[str, list[tuple[str, str]]], artefactos: dict[str, str],
                           fallos: list[str]) -> None:
    """Cada cifra clave debe aparecer en el documento que la publica."""
    for nombre, cifras in exigidas.items():
        texto = artefactos.get(nombre, "")
        for etiqueta, valor in cifras:
            comprobar(valor in texto, f"{nombre}: falta la cifra {etiqueta} ({valor})", fallos)


def comprobar_cifras_heredadas(artefactos: dict[str, str], fallos: list[str]) -> None:
    """Ninguna cifra de la corrida anterior debe seguir publicada."""
    for nombre, texto in artefactos.items():
        for heredada in HEREDADAS:
            comprobar(heredada not in texto, f"{nombre}: sigue publicada la cifra heredada «{heredada}»", fallos)


def comprobar_barrido(artefactos: dict[str, str], permitidos: set[float], fallos: list[str]) -> None:
    """Cada número publicado debe estar respaldado por `reports/` o por el contexto justificado."""
    for nombre, texto in artefactos.items():
        for token in NUMERO.findall(limpiar(texto)):
            opciones = candidatos(token)
            if not opciones:
                continue
            respaldado = any(
                any(abs(opcion - permitido) <= max(1e-9, abs(permitido) * 1e-9) for permitido in permitidos)
                for opcion in opciones
            )
            comprobar(respaldado, f"{nombre}: el número «{token}» no está respaldado por reports/", fallos)


def comprobar_figuras(artefactos: dict[str, str], fallos: list[str]) -> None:
    """Las rutas de figuras deben existir y ser las mismas en los cuatro documentos."""
    for nombre, texto in artefactos.items():
        rutas = set(RUTA_REPORTS.findall(texto))
        for ruta in rutas:
            if "*" in ruta:
                continue
            comprobar((ROOT / ruta).exists(), f"{nombre}: la ruta «{ruta}» no existe", fallos)
        for figura in FIGURAS_LAB03:
            comprobar(figura in rutas, f"{nombre}: no cita la figura «{figura}»", fallos)


def comprobar_etiquetas(artefactos: dict[str, str], fallos: list[str]) -> None:
    """Etiquetas que el mandato exige corregir."""
    for nombre, texto in artefactos.items():
        for rotulo in ROTULOS_ESTRATIFICADOS:
            comprobar(rotulo not in texto, f"{nombre}: la submuestra de t-SNE sigue rotulada «{rotulo}»", fallos)
    pdf = artefactos.get("PDF")
    if pdf is not None:
        comprobar("PENDIENTE" not in pdf, "PDF: todavía contiene «PENDIENTE»", fallos)
        comprobar("elExercise" not in pdf, "PDF: todavía contiene «elExercise»", fallos)
        comprobar("Edwing Perez" in pdf, "PDF: falta el nombre del estudiante", fallos)
        comprobar("https://github.com/edvvdev/unidad01-02" in pdf, "PDF: falta la URL del repositorio", fallos)
    for nombre in ("README", "Conclusión", "notebook (conclusión)"):
        comprobar("uniforme" in artefactos[nombre], f"{nombre}: no explica que la submuestra de t-SNE es uniforme", fallos)


def main() -> int:
    """Ejecuta todas las comprobaciones y devuelve el código de salida."""
    fallos: list[str] = []
    resultados = pd.read_csv(REPORTS / "green_ai_results.csv")
    decision = json.loads((REPORTS / "green_ai_decision.json").read_text(encoding="utf-8"))
    contexto = {
        "tsne_proporcion_mas_50k": json.loads((REPORTS / "tsne_sample.json").read_text(encoding="utf-8"))[
            "proporcion_mas_50k_submuestra"],
        "proporcion_mas_50k_prueba": json.loads((REPORTS / "lab03_contexto.json").read_text(encoding="utf-8"))[
            "proporcion_mas_50k_prueba"],
        "capital_gain_cero_porcentaje": json.loads((REPORTS / "lab03_contexto.json").read_text(encoding="utf-8"))[
            "capital_gain_cero_porcentaje"],
        "filas_entrenamiento": json.loads((REPORTS / "lab03_contexto.json").read_text(encoding="utf-8"))[
            "filas_entrenamiento"],
        "columnas_matriz_densa": json.loads((REPORTS / "lab03_contexto.json").read_text(encoding="utf-8"))[
            "columnas_matriz_densa"],
        "matriz_densa_mb": json.loads((REPORTS / "lab03_contexto.json").read_text(encoding="utf-8"))[
            "matriz_densa_mb"],
        "tsne_casos": json.loads((REPORTS / "tsne_sample.json").read_text(encoding="utf-8"))["tamano_submuestra"],
    }
    permitidos = valores_permitidos()

    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    conclusion = (ROOT / "docs" / "CONCLUSION_EJERCICIO_02.md").read_text(encoding="utf-8")
    celdas_lab03 = celdas(ROOT / "notebooks" / "03_ensembles_green_ai.ipynb")
    catalogo = next((celda for celda in celdas_lab03 if "resultados.to_csv" in celda["fuente"]), None)
    cierre = next((celda for celda in celdas_lab03 if "actualizar_documentos" in celda["fuente"]), None)
    comprobar(catalogo is not None, "no se encuentra la celda del catálogo en el notebook del LAB03", fallos)
    comprobar(cierre is not None, "no se encuentra la celda de conclusión en el notebook del LAB03", fallos)
    for celda in celdas_lab03:
        comprobar(not celda["errores"], f"el notebook del LAB03 tiene una celda en error: {celda['errores']}", fallos)

    artefactos = {
        "README": readme,
        "Conclusión": conclusion,
        "notebook (catálogo)": catalogo["salida"] if catalogo else "",
        "notebook (conclusión)": cierre["salida"] if cierre else "",
    }
    textos_figuras = {
        nombre: texto for nombre, texto in artefactos.items() if not nombre.startswith("notebook")
    }
    textos_figuras["notebook (completo)"] = "\n".join(
        celda["fuente"] + "\n" + celda["salida"] for celda in celdas_lab03
    )
    pdf = texto_pdf(ROOT / "docs" / "EJERCICIO_02_PDF_BRIEF.pdf")
    if pdf is None:
        print("AVISO: `pdftotext` no está instalado; se omite la comprobación del PDF.")
    else:
        artefactos["PDF"] = pdf

    narrativa = cifras_narrativa(resultados, decision, contexto)
    narrativa_sin_contexto = [cifra for cifra in narrativa if "capital_gain" not in cifra[0]]
    exigidas = {
        "README": cifras_catalogo(resultados, es) + cifras_decision(decision) + narrativa_sin_contexto
                  + cifras_limitaciones(contexto),
        "Conclusión": cifras_decision(decision) + narrativa,
        "notebook (conclusión)": cifras_decision(decision) + narrativa,
        "notebook (catálogo)": cifras_catalogo_notebook(resultados),
    }
    if pdf is not None:
        exigidas["PDF"] = cifras_catalogo(resultados, es) + cifras_decision(decision) + narrativa

    for cifras in exigidas.values():
        for _, valor in cifras:
            for opcion in candidatos(valor):
                permitidos.add(opcion)

    comprobar_cifras_clave(exigidas, artefactos, fallos)
    comprobar_cifras_heredadas(artefactos, fallos)
    comprobar_barrido(artefactos, permitidos, fallos)
    comprobar_figuras(textos_figuras, fallos)
    comprobar_etiquetas(artefactos, fallos)

    if fallos:
        print(f"FALLO: {len(fallos)} inconsistencias entre lo publicado y reports/\n")
        for fallo in fallos:
            print(f"  - {fallo}")
        return 1
    print("OK: las cifras publicadas (README, conclusión, notebook y PDF) coinciden con reports/.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
