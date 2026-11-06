"""Catálogo de modelos, medición repetida y frontera de Pareto (LAB03 · Ejercicio 02).

Reglas del protocolo congelado del Ejercicio 01:
- mismo dataset (Adult, UCI), mismo target (`income`) y misma partición estratificada 80/20;
- las transformaciones (imputación, escala, one-hot y PCA) viven **dentro** del pipeline, de modo
  que se ajustan solo con datos de entrenamiento;
- el tiempo se mide repetidas veces y se reporta la mediana; el tamaño es el del pipeline serializado.
"""

from __future__ import annotations

import pickle
import platform
from time import perf_counter

import numpy as np
import pandas as pd
import sklearn
from sklearn.compose import ColumnTransformer
from sklearn.decomposition import PCA
from sklearn.ensemble import HistGradientBoostingClassifier, RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.svm import SVC

PCA_COMPONENTS = 20
REPETITIONS = 3
RANDOM_STATE = 42

#: Catálogo homogéneo: al menos seis configuraciones sobre el mismo preprocesamiento y la misma
#: partición. `reduce_pca` indica si la variante incluye la reducción por PCA.
CATALOGUE: dict[str, dict] = {
    "logreg": {"family": "lineal", "reduce_pca": False,
               "estimator": lambda: LogisticRegression(max_iter=1000, random_state=RANDOM_STATE)},
    "logreg_pca": {"family": "lineal + PCA", "reduce_pca": True,
                   "estimator": lambda: LogisticRegression(max_iter=1000, random_state=RANDOM_STATE)},
    "svm_c1": {"family": "SVM", "reduce_pca": False,
               "estimator": lambda: SVC(C=1.0, gamma="scale", cache_size=2000)},
    "svm_c10": {"family": "SVM", "reduce_pca": False,
                "estimator": lambda: SVC(C=10.0, gamma="scale", cache_size=2000)},
    "svm_c10_pca": {"family": "SVM + PCA", "reduce_pca": True,
                    "estimator": lambda: SVC(C=10.0, gamma="scale", cache_size=2000)},
    "rf_100": {"family": "Random Forest", "reduce_pca": False,
               "estimator": lambda: RandomForestClassifier(n_estimators=100, random_state=RANDOM_STATE, n_jobs=-1)},
    "rf_300": {"family": "Random Forest", "reduce_pca": False,
               "estimator": lambda: RandomForestClassifier(n_estimators=300, random_state=RANDOM_STATE, n_jobs=-1)},
    "boost": {"family": "Boosting", "reduce_pca": False,
              "estimator": lambda: HistGradientBoostingClassifier(random_state=RANDOM_STATE)},
}


def build_preprocessor(features: pd.DataFrame) -> ColumnTransformer:
    """Preprocesamiento único para todo el catálogo.

    Numéricas: imputación por mediana + estandarización. Categóricas: imputación por moda +
    codificación one-hot **densa**. La salida es densa porque el boosting (HistGradientBoosting) y
    el PCA no admiten matrices dispersas; el costo en memoria (48.842 x 58 float64 ≈ 21 MB) queda
    documentado en el informe y es una de las razones por las que la reducción por PCA se evalúa.
    """
    numeric = [column for column in features.columns if pd.api.types.is_numeric_dtype(features[column])]
    categorical = [column for column in features.columns if column not in numeric]
    return ColumnTransformer(
        transformers=[
            ("numeric", Pipeline(steps=[("imputer", SimpleImputer(strategy="median")), ("scaler", StandardScaler())]), numeric),
            (
                "categorical",
                Pipeline(
                    steps=[
                        ("imputer", SimpleImputer(strategy="most_frequent")),
                        ("encoder", OneHotEncoder(handle_unknown="ignore", sparse_output=False)),
                    ]
                ),
                categorical,
            ),
        ]
    )


def build_configuration(name: str, features: pd.DataFrame) -> Pipeline:
    """Construye el pipeline completo de una configuración del catálogo.

    La reducción por PCA (cuando aplica) se coloca dentro del pipeline: el PCA se ajusta solo con
    el conjunto de entrenamiento, de modo que no hay fuga de información.
    """
    if name not in CATALOGUE:
        raise ValueError(f"Configuración desconocida: {name}. Opciones: {sorted(CATALOGUE)}")
    spec = CATALOGUE[name]
    steps: list[tuple[str, object]] = [("preprocessor", build_preprocessor(features))]
    if spec["reduce_pca"]:
        steps.append(("pca", PCA(n_components=PCA_COMPONENTS, random_state=RANDOM_STATE)))
    steps.append(("model", spec["estimator"]()))
    return Pipeline(steps=steps)


def median_time(function, repetitions: int = REPETITIONS) -> tuple[float, list[float]]:
    """Ejecuta `function` varias veces y devuelve (mediana, tiempos individuales)."""
    durations = []
    for _ in range(repetitions):
        start = perf_counter()
        function()
        durations.append(perf_counter() - start)
    return float(np.median(durations)), durations


def serialized_size_kb(pipeline) -> float:
    """Tamaño en KB del pipeline serializado con pickle."""
    return len(pickle.dumps(pipeline)) / 1024


def fit_and_measure(name: str, features_train: pd.DataFrame, target_train: pd.Series,
                    features_test: pd.DataFrame, repetitions: int = REPETITIONS) -> dict:
    """Ajusta una configuración N veces, mide tiempo, inferencia y tamaño, y devuelve su fila."""
    pipeline = build_configuration(name, features_train)
    fit_seconds, fit_runs = median_time(lambda: pipeline.fit(features_train, target_train), repetitions)
    predictions = pipeline.predict(features_test)

    def predict_once() -> None:
        pipeline.predict(features_test)

    predict_seconds, _ = median_time(predict_once, repetitions)
    return {
        "configuracion": name,
        "familia": CATALOGUE[name]["family"],
        "reduce_pca": CATALOGUE[name]["reduce_pca"],
        "fit_time_median_s": fit_seconds,
        "fit_time_min_s": min(fit_runs),
        "fit_time_max_s": max(fit_runs),
        "predict_time_median_ms": predict_seconds * 1000,
        "model_size_kb": serialized_size_kb(pipeline),
        "repeticiones": repetitions,
        "pipeline": pipeline,
        "predictions": predictions,
    }


def pareto_flags(frame: pd.DataFrame, utility: str = "f1_macro", cost: str = "fit_time_median_s") -> pd.Series:
    """Marca las configuraciones no dominadas.

    Una configuración está dominada si existe otra con utilidad igual o mejor y costo igual o
    menor (al menos una de las dos desigualdades estricta).
    """
    flags = []
    for _, row in frame.iterrows():
        dominated = (
            (frame[utility] >= row[utility])
            & (frame[cost] <= row[cost])
            & ((frame[utility] > row[utility]) | (frame[cost] < row[cost]))
        ).any()
        flags.append(not bool(dominated))
    return pd.Series(flags, index=frame.index)


def environment_report() -> dict:
    """Entorno de ejecución: el tiempo es contextual, no una medición de energía."""
    return {
        "python": platform.python_version(),
        "sistema": platform.platform(),
        "procesador": platform.processor() or platform.machine(),
        "scikit_learn": sklearn.__version__,
        "numpy": np.__version__,
        "pandas": pd.__version__,
    }
