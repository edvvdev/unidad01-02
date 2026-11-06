"""Redacción de la narrativa del LAB03 a partir de los artefactos de `reports/`.

La prosa del Ejercicio 02 (README, `docs/CONCLUSION_EJERCICIO_02.md` y PDF breve) se genera aquí
con las mismas cifras que `reports/green_ai_results.csv` y `reports/green_ai_decision.json`, de modo
que ninguna cifra publicada pueda quedar desfasada respecto de la corrida real. El módulo también
expone las cifras derivadas para que `scripts/verify_cifras.py` pueda contrastarlas de forma
independiente.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path

import pandas as pd

#: Marcadores que delimitan un bloque generado dentro de un archivo de texto.
MARCADOR_INICIO = "<!-- BEGIN: {nombre} -->"
MARCADOR_FIN = "<!-- END: {nombre} -->"

#: Bloques generados que este módulo escribe en el README.
BLOQUE_RESUMEN = "LAB03-RESUMEN"
BLOQUE_LIMITACIONES = "LAB03-LIMITACIONES"

#: Marcadores que delimitan el cuerpo de la conclusión (lo que el PDF reproduce en su sección 4).
MARCADOR_CUERPO_INICIO = "<!-- INICIO CUERPO -->"
MARCADOR_CUERPO_FIN = "<!-- FIN CUERPO -->"

#: Descripción legible de cada configuración del catálogo (el CSV solo trae la familia).
DESCRIPCIONES = {
    "boost": "Boosting (`HistGradientBoosting`)",
    "logreg": "Regresión logística",
    "logreg_pca": "Regresión logística + PCA",
    "rf_100": "Random Forest (100 árboles)",
    "rf_300": "Random Forest (300 árboles)",
    "svm_c1": "SVM (`C=1`, `gamma=scale`)",
    "svm_c10": "SVM (`C=10`, `gamma=scale`)",
    "svm_c10_pca": "SVM (`C=10`) + PCA",
}

#: Descripción breve de cada configuración (para las tablas estrechas del PDF).
DESCRIPCIONES_CORTAS = {
    "boost": "Boosting",
    "logreg": "Logística",
    "logreg_pca": "Logística + PCA",
    "rf_100": "Random Forest 100",
    "rf_300": "Random Forest 300",
    "svm_c1": "SVM (C=1)",
    "svm_c10": "SVM (C=10)",
    "svm_c10_pca": "SVM (C=10) + PCA",
}

#: Referencias bibliográficas de la entrega (se repiten en el README y en la conclusión).
REFERENCIAS = (
    (
        "Becker, B. y Kohavi, R. (1996). *Adult* [Conjunto de datos]. UCI Machine Learning Repository. "
        "https://doi.org/10.24432/C5XW20"
    ),
    (
        "Dodge, J., Schwartz, R., Strubell, E., et al. (2022). *A Green AI*. arXiv:2211.05859. "
        "https://arxiv.org/abs/2211.05859"
    ),
    (
        "Strubell, E., Ganesh, A. y McCallum, A. (2019). Energy and Policy Considerations for Deep Learning "
        "in NLP. En *Proceedings of the 57th Annual Meeting of the Association for Computational "
        "Linguistics* (págs. 4135-4148). Association for Computational Linguistics. "
        "https://doi.org/10.18653/v1/N19-1423"
    ),
    (
        "Universidad Autónoma de Santo Domingo (UASD). (2026). *Manual de la Unidad 01: modelos de "
        "aprendizaje automático, ensembles y Green AI*. INF-8239 Ciencia de Datos II, Prof. Edwin Ramón "
        "José Nolasco."
    ),
    (
        "scikit-learn. (2026). *Documentación de scikit-learn 1.9*: `SVC` "
        "(https://scikit-learn.org/stable/modules/svm.html) y `TfidfVectorizer` "
        "(https://scikit-learn.org/stable/modules/feature_extraction.html#text-vectorizer)."
    ),
)

#: Decimales con los que se publica cada magnitud.
DECIMALES_METRICA = 4
DECIMALES_TIEMPO = 2
DECIMALES_INFERENCIA = 1
DECIMALES_TAMANO = 0
DECIMALES_MB = 1
DECIMALES_PORCENTAJE = 2


def formatear(valor: float, decimales: int = DECIMALES_METRICA) -> str:
    """Formatea un número con la convención española: coma decimal y punto de millar."""
    return f"{valor:,.{decimales}f}".replace(",", "\x00").replace(".", ",").replace("\x00", ".")


@dataclass(frozen=True)
class Cifras:
    """Cifras del LAB03 leídas de `reports/` (fuente de verdad de la entrega)."""

    resultados: pd.DataFrame
    decision: dict
    pca: dict
    tsne: dict
    contexto: dict

    def fila(self, nombre: str) -> pd.Series:
        """Devuelve la fila del catálogo que corresponde a una configuración."""
        coincidencias = self.resultados[self.resultados["configuracion"] == nombre]
        if coincidencias.empty:
            raise KeyError(f"La configuración {nombre} no está en reports/green_ai_results.csv")
        return coincidencias.iloc[0]

    @property
    def elegida(self) -> pd.Series:
        """Fila de la configuración elegida en la frontera de Pareto."""
        return self.fila(self.decision["configuracion_elegida"])

    def valores(self) -> dict:
        """Cifras derivadas que aparecen en la narrativa, con su formato publicado."""
        elegida = self.elegida
        alternativa = self.fila(self.decision["alternativa_en_la_frontera"])
        svm = self.fila("svm_c10")
        svm_pca = self.fila("svm_c10_pca")
        peor_utilidad = self.resultados.loc[self.resultados["f1_macro"].idxmin()]
        recall_min = self.resultados.loc[self.resultados["recall_mas_50k"].idxmin()]
        recall_max = self.resultados.loc[self.resultados["recall_mas_50k"].idxmax()]
        componentes = self.pca["componentes_para_varianza"]
        return {
            "elegida": self.decision["configuracion_elegida"],
            "f1_elegida": self.decision["f1_macro_elegida"],
            "accuracy_elegida": float(elegida["accuracy"]),
            "tiempo_elegida_s": self.decision["tiempo_elegida_s"],
            "tamano_elegida_kb": self.decision["tamano_elegida_kb"],
            "inferencia_elegida_ms": self.decision["inferencia_elegida_ms"],
            "diferencia_absoluta_f1": self.decision["diferencia_absoluta_f1"],
            "alternativa": self.decision["alternativa_en_la_frontera"],
            "f1_alternativa": self.decision["f1_macro_alternativa"],
            "diferencia_f1_alternativa": self.decision["diferencia_f1_vs_alternativa"],
            "tiempo_alternativa_s": float(alternativa["fit_time_median_s"]),
            "diferencia_tiempo_alternativa_s": (
                float(elegida["fit_time_median_s"]) - float(alternativa["fit_time_median_s"])
            ),
            "diferencia_tamano_alternativa_mb": (
                abs(self.decision["diferencia_tamano_vs_alternativa_kb"]) / 1024
            ),
            "ratio_inferencia_svm": self.decision["ratio_inferencia_svm_sobre_boost"],
            "inferencia_svm_ms": self.decision["inferencia_svm_c10_ms"],
            "rf_300_mb": self.decision["tamano_rf_300_kb"] / 1024,
            "svm_tiempo_s": float(svm["fit_time_median_s"]),
            "svm_mb": float(svm["model_size_kb"]) / 1024,
            "svm_pca_tiempo_s": float(svm_pca["fit_time_median_s"]),
            "svm_pca_mb": float(svm_pca["model_size_kb"]) / 1024,
            "diferencia_f1_pca": float(svm["f1_macro"]) - float(svm_pca["f1_macro"]),
            "f1_minimo": float(peor_utilidad["f1_macro"]),
            "configuracion_f1_minimo": str(peor_utilidad["configuracion"]),
            "recall_minimo": float(recall_min["recall_mas_50k"]),
            "configuracion_recall_minimo": str(recall_min["configuracion"]),
            "recall_maximo": float(recall_max["recall_mas_50k"]),
            "configuracion_recall_maximo": str(recall_max["configuracion"]),
            "configuraciones_con_recall_066": int((self.resultados["recall_mas_50k"] >= 0.6595).sum()),
            "componentes_80": componentes["0.80"],
            "componentes_90": componentes["0.90"],
            "componentes_95": componentes["0.95"],
            "componentes_pca_catalogo": self.pca["componentes_del_pca_del_catalogo"],
            "matriz_filas": self.contexto["filas_entrenamiento"],
            "matriz_columnas": self.contexto["columnas_matriz_densa"],
            "matriz_mb": self.contexto["matriz_densa_mb"],
            "filas_prueba": self.contexto["filas_prueba"],
            "proporcion_prueba_mas_50k": self.contexto["proporcion_mas_50k_prueba"],
            "capital_gain_cero_pct": self.contexto["capital_gain_cero_porcentaje"],
            "tsne_casos": self.tsne["tamano_submuestra"],
            "tsne_proporcion_mas_50k": self.tsne["proporcion_mas_50k_submuestra"],
            "fecha": self.decision["fecha_ejecucion"],
            "entorno": self.decision["entorno"],
        }


def cargar_cifras(reports: Path) -> Cifras:
    """Lee los artefactos de `reports/` que respaldan la narrativa del LAB03."""
    reports = Path(reports)
    return Cifras(
        resultados=pd.read_csv(reports / "green_ai_results.csv"),
        decision=json.loads((reports / "green_ai_decision.json").read_text(encoding="utf-8")),
        pca=json.loads((reports / "pca_variance.json").read_text(encoding="utf-8")),
        tsne=json.loads((reports / "tsne_sample.json").read_text(encoding="utf-8")),
        contexto=json.loads((reports / "lab03_contexto.json").read_text(encoding="utf-8")),
    )


def render_tabla(cifras: Cifras) -> str:
    """Tabla markdown con el catálogo completo, ordenada por F1 macro descendente."""
    orden = cifras.resultados.sort_values("f1_macro", ascending=False)
    lineas = [
        "| Configuración | Familia | F1 macro | Accuracy | Ajuste (s) | Inferencia (ms) | Tamaño (KB) | Pareto |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for _, fila in orden.iterrows():
        nombre = str(fila["configuracion"])
        f1 = formatear(fila["f1_macro"])
        if nombre == cifras.decision["configuracion_elegida"]:
            f1 = f"**{f1}**"
        linea = (
            f"| `{nombre}` | {DESCRIPCIONES.get(nombre, fila['familia'])} | {f1} | "
            f"{formatear(fila['accuracy'])} | {formatear(fila['fit_time_median_s'], DECIMALES_TIEMPO)} | "
            f"{formatear(fila['predict_time_median_ms'], DECIMALES_INFERENCIA)} | "
            f"{formatear(fila['model_size_kb'], DECIMALES_TAMANO)} | "
            f"{'**sí**' if fila['is_pareto'] else 'no'} |"
        )
        lineas.append(linea)
    return "\n".join(lineas)


def render_decision(cifras: Cifras) -> str:
    """Párrafo con la decisión cuantificada del LAB03."""
    v = cifras.valores()
    return (
        f"**Decisión cuantificada (LAB03).** Se entrega **`{v['elegida']}`**: F1 macro "
        f"{formatear(v['f1_elegida'])} (la máxima del catálogo, diferencia absoluta "
        f"{formatear(v['diferencia_absoluta_f1'], 2)} frente a la mejor), "
        f"{formatear(v['tiempo_elegida_s'], DECIMALES_TIEMPO)} s de ajuste, "
        f"{formatear(v['tamano_elegida_kb'], DECIMALES_TAMANO)} KB de modelo y "
        f"{formatear(v['inferencia_elegida_ms'], DECIMALES_INFERENCIA)} ms de inferencia. Frente a la otra "
        f"configuración no dominada (`{v['alternativa']}`, {formatear(v['f1_alternativa'])}), gana "
        f"{formatear(v['diferencia_f1_alternativa'])} de F1 macro con un tiempo de ajuste de "
        f"{formatear(v['tiempo_elegida_s'], DECIMALES_TIEMPO)} s frente a "
        f"{formatear(v['tiempo_alternativa_s'], DECIMALES_TIEMPO)} s de `{v['alternativa']}` y "
        f"**{formatear(v['diferencia_tamano_alternativa_mb'], DECIMALES_MB)} MB menos de modelo**. El SVM "
        f"infiere **{formatear(v['ratio_inferencia_svm'], 0)} veces más lento** que el boosting "
        f"({formatear(v['inferencia_svm_ms'], DECIMALES_INFERENCIA)} ms frente a "
        f"{formatear(v['inferencia_elegida_ms'], DECIMALES_INFERENCIA)} ms) y el Random Forest de 300 árboles "
        f"ocupa **{formatear(v['rf_300_mb'], DECIMALES_MB)} MB** para peor desempeño. El PCA reduce el costo "
        f"del SVM ({formatear(v['svm_pca_tiempo_s'], DECIMALES_TIEMPO)} s y "
        f"{formatear(v['svm_pca_mb'], DECIMALES_MB)} MB frente a "
        f"{formatear(v['svm_tiempo_s'], DECIMALES_TIEMPO)} s y {formatear(v['svm_mb'], DECIMALES_MB)} MB) pero "
        f"**resta** {formatear(v['diferencia_f1_pca'])} de F1 macro: el 90 % de varianza que retiene no incluye "
        f"la señal de los ingresos altos. El recall de `>50K` no es constante: va de "
        f"{formatear(v['recall_minimo'])} (`{v['configuracion_recall_minimo']}`) a "
        f"{formatear(v['recall_maximo'])} (`{v['configuracion_recall_maximo']}`), de modo que solo "
        f"{v['configuraciones_con_recall_066']} de las ocho configuraciones llega a 0,66."
    )


def render_evidencia(cifras: Cifras) -> str:
    """Tabla con las figuras del LAB03 y su ruta (todas existen en `reports/`)."""
    v = cifras.valores()
    return "\n".join(
        [
            "| Figura | Archivo | Qué muestra |",
            "|---|---|---|",
            (
                f"| PCA: espectro y proyección 2D | `reports/pca_analysis.png` | {v['componentes_90']} "
                f"componentes para el 90 % de la varianza y {v['componentes_95']} para el 95 %; la proyección "
                "2D separa solo parcialmente las clases |"
            ),
            (
                f"| t-SNE con dos semillas | `reports/tsne_two_seeds.png` | Semillas 42 y 7 sobre "
                f"{formatear(v['tsne_casos'], 0)} casos de prueba con submuestra **uniforme** (no "
                "estratificada): la estructura de agrupamientos permanece, las coordenadas cambian |"
            ),
            (
                "| Perfil de las categorías más frecuentes | `reports/popular_top10.png` | Los 10 valores "
                "más frecuentes de `occupation` en la prueba y su proporción de `>50K`: el desbalance es del "
                "dato, no del modelo |"
            ),
            (
                "| Frontera de Pareto | `reports/pareto.png` | F1 macro frente a tiempo de ajuste y frente a "
                "tamaño del modelo (escala logarítmica) |"
            ),
        ]
    )


def render_resumen(cifras: Cifras) -> str:
    """Fragmento compartido por el README y los documentos de la entrega."""
    return "\n\n".join(
        [
            "**LAB03** (`reports/green_ai_results.csv`, `reports/green_ai_decision.json`):",
            render_tabla(cifras),
            (
                "Tiempos y tamaños: **mediana de 3 repeticiones** de ajuste y de inferencia, y tamaño del "
                "pipeline serializado."
            ),
            render_decision(cifras),
            "### Evidencia de reducción dimensional (LAB03)",
            render_evidencia(cifras),
        ]
    )


def render_limitaciones(cifras: Cifras) -> str:
    """Limitaciones del LAB03 que dependen de cifras medidas."""
    v = cifras.valores()
    return "\n".join(
        [
            (
                "- El preprocesamiento del LAB03 es denso porque el boosting y el PCA no admiten entradas "
                f"dispersas: la matriz de entrenamiento tiene {formatear(v['matriz_filas'], 0)} × "
                f"{v['matriz_columnas']} columnas float64 ≈ {formatear(v['matriz_mb'], DECIMALES_MB)} MB, y el "
                f"PCA con {v['componentes_pca_catalogo']} componentes no conserva del todo la señal de los "
                "ingresos altos."
            ),
            (
                "- t-SNE se aplica a una submuestra **uniforme** (muestreo uniforme sin reposición con "
                f"semilla 42, no estratificado) de {formatear(v['tsne_casos'], 0)} casos de prueba: por eso "
                "puede desbalancear las clases "
                f"({formatear(v['tsne_proporcion_mas_50k'] * 100, DECIMALES_PORCENTAJE)} % de `>50K` en la submuestra "
                f"frente a {formatear(v['proporcion_prueba_mas_50k'] * 100, DECIMALES_PORCENTAJE)} % en la prueba) "
                "y una separación visual no demuestra causalidad ni que el modelo use esa geometría."
            ),
            (
                "- El recall de `>50K` no es el mismo en todas las configuraciones: va de "
                f"{formatear(v['recall_minimo'])} (`{v['configuracion_recall_minimo']}`) a "
                f"{formatear(v['recall_maximo'])} (`{v['configuracion_recall_maximo']}`) y solo "
                f"{v['configuraciones_con_recall_066']} de las ocho configuraciones llega a 0,66; el problema "
                "es de datos, no de modelo."
            ),
            (
                "- Los modelos serializados de `models/` (hasta "
                f"{formatear(v['rf_300_mb'], DECIMALES_MB)} MB el de Random Forest con 300 árboles) no se "
                "versionan: se regeneran ejecutando el notebook."
            ),
        ]
    )


def render_cuerpo_conclusion(cifras: Cifras) -> str:
    """Cuerpo de la conclusión (350 palabras) del Ejercicio 02."""
    v = cifras.valores()
    entorno = v["entorno"]
    return "\n\n".join(
        [
            (
                "**Qué se comparó.** Ocho configuraciones homogéneas sobre el dataset, el target y la "
                "partición aprobados en el Ejercicio 01 (Adult / Census Income, UCI, CC BY 4.0; target "
                f"`income`; partición estratificada 80/20 con semilla 42; {formatear(v['filas_prueba'], 0)} "
                "casos de prueba): regresión logística, SVM con `C=1` y `C=10`, Random Forest de 100 y 300 "
                "árboles, boosting (`HistGradientBoosting`) y dos variantes con reducción por PCA de "
                f"{v['componentes_pca_catalogo']} componentes. Cada configuración se ajustó **tres veces** y "
                "se reporta la **mediana** del tiempo de ajuste y de la inferencia, más el tamaño del "
                "pipeline serializado."
            ),
            (
                "**Resultado.** El F1 macro va de "
                f"{formatear(v['f1_minimo'])} (`{v['configuracion_f1_minimo']}`) a "
                f"**{formatear(v['f1_elegida'])} (`{v['elegida']}`)**. El boosting gana con "
                f"{formatear(v['tiempo_elegida_s'], DECIMALES_TIEMPO)} s de ajuste, "
                f"{formatear(v['tamano_elegida_kb'], DECIMALES_TAMANO)} KB de modelo y "
                f"{formatear(v['inferencia_elegida_ms'], DECIMALES_INFERENCIA)} ms de inferencia: es "
                "simultáneamente la mejor utilidad y una de las opciones más baratas, por lo que la "
                f"diferencia absoluta de F1 macro frente a la mejor configuración es "
                f"{formatear(v['diferencia_absoluta_f1'], 2)}. Frente a la otra configuración no dominada "
                f"(`{v['alternativa']}`, {formatear(v['f1_alternativa'])}) gana "
                f"{formatear(v['diferencia_f1_alternativa'])} de F1 macro con un tiempo de ajuste de "
                f"{formatear(v['tiempo_elegida_s'], DECIMALES_TIEMPO)} s frente a "
                f"{formatear(v['tiempo_alternativa_s'], DECIMALES_TIEMPO)} s de `{v['alternativa']}` y "
                f"**{formatear(v['diferencia_tamano_alternativa_mb'], DECIMALES_MB)} MB menos de modelo**. "
                "El SVM, en cambio, infiere "
                f"**{formatear(v['ratio_inferencia_svm'], 0)} veces más lento** "
                f"({formatear(v['inferencia_svm_ms'], DECIMALES_INFERENCIA)} ms frente a "
                f"{formatear(v['inferencia_elegida_ms'], DECIMALES_INFERENCIA)} ms para las mismas "
                f"{formatear(v['filas_prueba'], 0)} filas) y el Random Forest de 300 árboles ocupa "
                f"**{formatear(v['rf_300_mb'], DECIMALES_MB)} MB** para peor desempeño. El PCA reduce el "
                f"costo del SVM ({formatear(v['svm_pca_tiempo_s'], DECIMALES_TIEMPO)} s y "
                f"{formatear(v['svm_pca_mb'], DECIMALES_MB)} MB frente a "
                f"{formatear(v['svm_tiempo_s'], DECIMALES_TIEMPO)} s y "
                f"{formatear(v['svm_mb'], DECIMALES_MB)} MB) pero **resta** "
                f"{formatear(v['diferencia_f1_pca'])} de F1 macro: el 90 % de varianza que retiene no incluye "
                "la señal que separa los ingresos altos. Los dos mapas t-SNE (semillas 42 y 7) conservan los "
                "mismos agrupamientos aunque cambian las coordenadas: la estructura persiste, la "
                "representación no."
            ),
            (
                "**Decisión y defensa.** Se entrega `boost`: máxima utilidad y costo entre los más bajos. El "
                "tiempo de ajuste y el tamaño del modelo son **proxies contextuales de costo, no consumo "
                f"energético**; las cifras solo valen en el hardware registrado (Python {entorno['python']}, "
                f"scikit-learn {entorno['scikit_learn']}, {entorno['procesador']}, "
                f"{entorno['sistema'].split('-')[0]}). La limitación de fondo es la del Ejercicio 01: "
                f"`capital_gain` está ausente en el {formatear(v['capital_gain_cero_pct'], 2)} % de las filas "
                f"y el recall de `>50K` va de {formatear(v['recall_minimo'])} "
                f"(`{v['configuracion_recall_minimo']}`) a {formatear(v['recall_maximo'])} "
                f"(`{v['configuracion_recall_maximo']}`): ninguna frontera de Pareto arregla un problema de "
                "datos. La submuestra de t-SNE es **uniforme**, no estratificada, de modo que puede "
                "desbalancear las clases "
                f"({formatear(v['tsne_proporcion_mas_50k'] * 100, DECIMALES_PORCENTAJE)} % de `>50K` frente a "
                f"{formatear(v['proporcion_prueba_mas_50k'] * 100, DECIMALES_PORCENTAJE)} % de la prueba)."
            ),
            (
                "**Pendiente crítico:** la aprobación del docente sobre el dataset sigue sin recibirse "
                "(arrastrada del Ejercicio 01) y este ejercicio se ejecutó con esa aprobación pendiente, "
                "tal como consta en `reports/green_ai_decision.json`."
            ),
        ]
    )


def render_conclusion(cifras: Cifras) -> str:
    """Documento completo `docs/CONCLUSION_EJERCICIO_02.md`."""
    v = cifras.valores()
    referencias = "\n".join(f"- {referencia}" for referencia in REFERENCIAS)
    return (
        "# Conclusión · Ejercicio 02 (LAB03)\n\n"
        f"Proyecto: `INF8239_U01` · Unidad 01 · Fecha: {v['fecha']} · Extensión: 350 palabras\n\n"
        f"{MARCADOR_CUERPO_INICIO}\n\n"
        f"{render_cuerpo_conclusion(cifras)}\n\n"
        f"{MARCADOR_CUERPO_FIN}\n\n"
        "## Referencias\n\n"
        f"{referencias}\n\n"
        "## Figuras\n\n"
        "| Figura | Archivo |\n"
        "|---|---|\n"
        "| Frontera de Pareto | `reports/pareto.png` |\n"
        "| PCA: espectro y proyección 2D | `reports/pca_analysis.png` |\n"
        "| t-SNE con dos semillas | `reports/tsne_two_seeds.png` |\n"
        "| Perfil de las categorías más frecuentes | `reports/popular_top10.png` |\n\n"
        "> Documento generado por `scripts/generar_conclusion.py` a partir de `reports/green_ai_results.csv`, "
        "`reports/green_ai_decision.json` y los informes auxiliares del notebook. No editar a mano: las "
        "cifras se vuelven a escribir en cada ejecución.\n"
    )


def escribir(ruta: Path, texto: str) -> None:
    """Escribe un archivo de forma atómica (archivo temporal y reemplazo)."""
    ruta = Path(ruta)
    ruta.parent.mkdir(parents=True, exist_ok=True)
    temporal = ruta.with_name(ruta.name + ".tmp")
    temporal.write_text(texto, encoding="utf-8")
    temporal.replace(ruta)


def reemplazar_bloque(texto: str, nombre: str, contenido: str) -> str:
    """Reemplaza el bloque generado `nombre` de un texto por `contenido`."""
    inicio = MARCADOR_INICIO.format(nombre=nombre)
    fin = MARCADOR_FIN.format(nombre=nombre)
    if inicio not in texto or fin not in texto:
        raise ValueError(f"El archivo no contiene los marcadores del bloque {nombre}")
    patron = re.compile(re.escape(inicio) + ".*?" + re.escape(fin), re.DOTALL)
    bloque = f"{inicio}\n{contenido.strip()}\n{fin}"
    return patron.sub(lambda _coincidencia: bloque, texto, count=1)


def actualizar_documentos(root: Path) -> list[Path]:
    """Regenera la conclusión, el fragmento compartido y los bloques del README."""
    root = Path(root)
    cifras = cargar_cifras(root / "reports")
    documentos = []

    conclusion = root / "docs" / "CONCLUSION_EJERCICIO_02.md"
    escribir(conclusion, render_conclusion(cifras))
    documentos.append(conclusion)

    fragmento = root / "docs" / "LAB03_RESUMEN.md"
    escribir(fragmento, render_resumen(cifras) + "\n")
    documentos.append(fragmento)

    readme = root / "README.md"
    texto = readme.read_text(encoding="utf-8")
    texto = reemplazar_bloque(texto, BLOQUE_RESUMEN, render_resumen(cifras))
    texto = reemplazar_bloque(texto, BLOQUE_LIMITACIONES, render_limitaciones(cifras))
    escribir(readme, texto)
    documentos.append(readme)

    return documentos
