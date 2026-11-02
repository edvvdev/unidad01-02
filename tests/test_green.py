"""Pruebas del catálogo de modelos, la medición repetida y la frontera de Pareto (LAB03)."""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest
from sklearn.decomposition import PCA
from sklearn.ensemble import HistGradientBoostingClassifier, RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.svm import SVC

from inf8239_u01.green import (
    CATALOGUE,
    PCA_COMPONENTS,
    build_configuration,
    build_preprocessor,
    fit_and_measure,
    median_time,
    pareto_flags,
    serialized_size_kb,
)


@pytest.fixture(scope="module")
def sample_features() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "age": [23.0, 45.0, 31.0, 52.0, 39.0, 27.0, 61.0, 34.0],
            "workclass": ["Privado", "Público", None, "Privado", "Privado", "Público", None, "Privado"],
            "hours_per_week": [40, 45, 30, 50, 35, 60, 22, 48],
            "capital_gain": [0, 5000, 0, 0, 200, 0, 0, 900],
        }
    )


def test_catalogue_has_at_least_six_configurations():
    assert len(CATALOGUE) >= 6
    familias = {spec["family"] for spec in CATALOGUE.values()}
    assert {"SVM", "Random Forest", "Boosting"} <= familias


def test_every_configuration_builds_a_valid_pipeline(sample_features):
    for name in CATALOGUE:
        pipeline = build_configuration(name, sample_features)
        assert isinstance(pipeline, Pipeline)
        steps = [step for step, _ in pipeline.steps]
        assert steps[0] == "preprocessor"
        assert steps[-1] == "model"
        if CATALOGUE[name]["reduce_pca"]:
            assert "pca" in steps
            assert isinstance(pipeline.named_steps["pca"], PCA)
            assert pipeline.named_steps["pca"].n_components == PCA_COMPONENTS
        model = pipeline.named_steps["model"]
        if name.startswith("svm"):
            assert isinstance(model, SVC)
        elif name.startswith("rf"):
            assert isinstance(model, RandomForestClassifier)
        elif name == "boost":
            assert isinstance(model, HistGradientBoostingClassifier)
        elif name.startswith("logreg"):
            assert isinstance(model, LogisticRegression)


def test_measurements_use_median_of_repetitions(sample_features):
    features = sample_features
    target = pd.Series([0, 1, 0, 1, 0, 1, 0, 1])
    resultado = fit_and_measure("logreg", features, target, features, repetitions=3)
    assert resultado["repeticiones"] == 3
    assert resultado["fit_time_median_s"] > 0
    assert resultado["fit_time_min_s"] <= resultado["fit_time_median_s"] <= resultado["fit_time_max_s"]
    assert resultado["predict_time_median_ms"] > 0
    assert resultado["model_size_kb"] > 0
    assert len(resultado["predictions"]) == len(features)


def test_median_time_returns_median_of_runs():
    def dummy() -> None:
        return None

    mediana, tiempos = median_time(dummy, repetitions=5)
    assert len(tiempos) == 5
    assert mediana == pytest.approx(float(np.median(tiempos)))


def test_pareto_flags_detect_dominated_configurations():
    tabla = pd.DataFrame(
        {
            "f1_macro": [0.70, 0.80, 0.75, 0.80],
            "fit_time_median_s": [10.0, 20.0, 10.0, 30.0],
        }
    )
    flags = pareto_flags(tabla).tolist()
    # 0.70@10s está dominada por 0.75@10s y 0.80@30s está dominada por 0.80@20s
    assert flags == [False, True, True, False]


def test_preprocessor_is_fitted_only_on_training_data(sample_features):
    """El preprocesador dentro del pipeline se ajusta con el subconjunto recibido, no con todo."""
    preprocessor = build_preprocessor(sample_features)
    subconjunto = sample_features.iloc[:4]
    ajustado = preprocessor.fit_transform(subconjunto)
    assert ajustado.shape[0] == 4
    assert ajustado.shape[1] > 4
    assert serialized_size_kb(preprocessor) > 0
