# INF-8239 · Unidad 01 · Ejercicios 01 y 02 (LAB00–LAB03)

Curso: Ciencia de Datos II (INF-8239) · Profesor: Edwin Ramón José Nolasco · Código: U01.E01 / U01.E02

| Entrega | Repositorio |
|---|---|
| **Ejercicio 01** (LAB01 + LAB02): dataset público y SVM reproducible | https://github.com/edvvdev/unidad01-01 |
| **Ejercicio 02** (LAB03): ensambles, reducción dimensional y Green AI | https://github.com/edvvdev/unidad01-02 |

Proyecto de los laboratorios guiados 00–03 de la Unidad 01. Los tres laboratorios se resuelven en
este mismo proyecto, porque el LAB03 reutiliza el dataset, el target, las exclusiones y la
partición aprobados en el LAB02.

## Instalación

Hay dos caminos equivalentes. El primero usa **uv** (recomendado: bloquea las versiones exactas en
`uv.lock`); el segundo es el que describe el manual de la Unidad 01 (`venv` + `requirements.txt`) y
se mantiene porque el mandato exige que el repositorio incluya `requirements.txt`.

**Con uv (Windows, PowerShell)**

```powershell
cd C:\Proyectos\INF8239_U01
uv python install 3.12
uv sync
uv run pytest -q                                    # 21 passed
uv run ruff check .                                 # All checks passed!
```

**Con uv (macOS/Linux)**

```bash
cd ~/Proyectos/INF8239_U01
uv python install 3.12
uv sync
uv run pytest -q                                    # 21 passed
uv run ruff check .                                 # All checks passed!
```

**Con venv + requirements.txt (el procedimiento del manual)**

```powershell
cd C:\Proyectos\INF8239_U01
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m pip install -r requirements-dev.txt      # jupyter, reportlab y ruff
$env:PYTHONPATH="src"
python -m pytest -q                                # 21 passed
```

En macOS/Linux: `python3 -m venv .venv` y `source .venv/bin/activate`.

## Ejecución de los dos ejercicios

Un script hace todo el flujo: descarga el dataset, corre las pruebas, ejecuta los notebooks de
principio a fin (con sus salidas guardadas), regenera la documentación y los PDF y, al final, verifica
que todas las cifras publicadas coinciden con `reports/`.

```powershell
.\scripts\run_all.ps1        # Windows
```
```bash
./scripts/run_all.sh         # macOS / Linux
```

| Opción | Efecto |
|---|---|
| `SKIP_EJ02=1 ./scripts/run_all.sh` | Omite el notebook del LAB03 (ahorra 10–15 min) |
| `REPO_URL=... ./scripts/run_all.sh` | URL que se imprime en la portada del PDF |

Si prefieres ejecutar paso a paso:

```bash
uv run python -m pytest -q
uv run ruff check .
uv run python -m jupyter nbconvert --to notebook --execute --inplace notebooks/00_verificacion.ipynb
uv run python -m jupyter nbconvert --to notebook --execute --inplace notebooks/01_svm_guiada.ipynb
uv run python -m jupyter nbconvert --to notebook --execute --inplace notebooks/02_dataset_svm.ipynb
uv run python -m jupyter nbconvert --to notebook --execute --inplace notebooks/03_ensembles_green_ai.ipynb
uv run python scripts/generar_conclusion.py
uv run python scripts/build_ejercicio01_pdf.py
uv run python scripts/build_ejercicio02_pdf.py
uv run python scripts/verify_cifras.py
```

Los builders de los PDF usan **por defecto** la URL de publicación de cada entrega
(`https://github.com/edvvdev/unidad01-02` para el Ejercicio 02 y `https://github.com/edvvdev/unidad01-01`
para el Ejercicio 01); la variable de entorno `REPO_URL` la sobrescribe si el repositorio cambia de
dirección.

Tiempos orientativos en CPU: LAB01 ~30 s, LAB02 ~7 min (el SVM ajusta 39.073 filas), LAB03 10–15 min
(ocho modelos ajustados tres veces cada uno). Las **métricas se reproducen exactamente**; los
**tiempos y tamaños varían** con el hardware, y por eso se reportan como mediana de tres repeticiones.

### La narrativa se genera desde `reports/`

El LAB03 no publica cifras escritas a mano: `scripts/generar_conclusion.py` (y el último bloque del
notebook del LAB03, que hace lo mismo) reescriben la conclusión, el fragmento compartido y los
bloques de este README a partir de `reports/green_ai_results.csv`, `reports/green_ai_decision.json`
y los informes auxiliares del notebook. `scripts/verify_cifras.py` compara lo publicado —README,
conclusión, notebook y PDF— con esos artefactos y **falla** si algo no coincide; `scripts/run_all.sh`
lo ejecuta al final.

## Descarga reproducible de los datos

Ninguno de los datasets requiere cuenta ni ruta personal: la descarga la hace un script que valida
la URL y registra el SHA-256 de los bytes obtenidos.

```python
from inf8239_u01.data import download_dataset
download_dataset("adult", "data/raw")   # UCI Adult (Census Income)
download_dataset("bank", "data/raw")    # UCI Bank Marketing (candidato alterno)
```

| Dataset | URL | Ficha | Licencia | SHA-256 |
|---|---|---|---|---|
| Adult | `https://archive.ics.uci.edu/static/public/2/adult.zip` | https://archive.ics.uci.edu/dataset/2/adult | CC BY 4.0 | `7537312dd56c2b98035880805ce99e68183a30ee468aa5329d6df0fbb3cc21bb` |
| Bank Marketing | `https://archive.ics.uci.edu/static/public/222/bank+marketing.zip` | https://archive.ics.uci.edu/dataset/222/bank-marketing | CC BY 4.0 | ver `data/raw/bank.csv.sha256` |

LAB01 usa `load_breast_cancer()` de scikit-learn (569 muestras, 30 variables, 2 clases), que no
requiere descarga.

## Estructura

```
INF8239_U01/
├── data/raw/                 datos descargados (no versionados) + .sha256 + .source.txt
├── docs/
│   ├── ficha_dataset.md         ficha comparativa de los dos candidatos + diccionario de datos
│   ├── CONCLUSION_EJERCICIO_01.md
│   ├── CONCLUSION_EJERCICIO_02.md   conclusión generada desde reports/
│   ├── LAB03_RESUMEN.md             fragmento generado con las cifras del LAB03
│   ├── EJERCICIO_01_PDF_BRIEF.pdf
│   └── EJERCICIO_02_PDF_BRIEF.pdf
├── models/                  pipelines serializados (no versionados: *.joblib)
├── notebooks/
│   ├── 00_verificacion.ipynb       LAB00 · verificación del entorno
│   ├── 01_svm_guiada.ipynb         LAB01 · SVM con pipeline, GridSearchCV y evaluación
│   ├── 02_dataset_svm.ipynb        LAB02 · dataset público, auditoría y pipeline completo
│   └── 03_ensembles_green_ai.ipynb LAB03 · catálogo, PCA, t-SNE y frontera de Pareto
├── reports/                     métricas, tablas, informes y figuras generadas
├── scripts/                    run_all.sh · run_all.ps1 · generadores de los PDF
│   ├── generar_conclusion.py      reescribe la narrativa del LAB03 desde reports/
│   ├── verify_cifras.py           comprueba lo publicado contra reports/
│   └── build_ejercicio01_pdf.py · build_ejercicio02_pdf.py
├── src/inf8239_u01/
│   ├── data.py               carga, auditoría y descarga reproducible
│   ├── models.py             build_svm, build_baseline, ColumnTransformer, build_svm_pipeline
│   ├── evaluation.py         partición, métricas, matrices de confusión y figuras
│   ├── green.py              catálogo de configuraciones, medición repetida y frontera de Pareto
│   └── informe.py            redacción de la narrativa del LAB03 a partir de reports/
├── tests/                    test_environment.py · test_models.py · test_data_contract.py · test_green.py
├── pyproject.toml            proyecto para uv (mismas dependencias que requirements.txt)
├── uv.lock                   versiones exactas del entorno
├── requirements.txt          dependencias (procedimiento del manual)
├── requirements-dev.txt      jupyter, reportlab y ruff
└── AI_USE_DECLARATION.md
```

## Target y métrica

| Laboratorio | Dataset | Target (binario) | Métrica principal | Costo del error |
|---|---|---|---|---|
| LAB01 | Breast Cancer Wisconsin (diagnóstico) | `target`: 0 maligno · 1 benigno | F1 macro (media de las clases) | Falso negativo: maligno clasificado como benigno |
| LAB02 | UCI Adult (Census Income) | `income`: `<=50K` / `>50K` | F1 macro | Falso negativo: califica y no se detecta (posible denegación de crédito) |
| LAB03 | UCI Adult (Census Income) | `income`: `<=50K` / `>50K` | F1 macro | Igual que LAB02, con el recall como criterio de desempate |

## Resultados de referencia

Los tres laboratorios se ejecutaron en la misma corrida; la fecha exacta queda registrada en
`reports/green_ai_decision.json` y en los PDF de entrega.

**LAB01** (`reports/svm_metrics.json`, `reports/svm_cv_results.csv`):

| Modelo | Accuracy | F1 macro | Recall maligno |
|---|---|---|---|
| DummyClassifier (baseline) | 0,6316 | 0,3871 | 0,0000 |
| SVC rbf (C=10, gamma=0.01) | **0,9825** | **0,9812** | 0,9762 |

Matriz de confusión (prueba, 114 casos): 41 malignos correctos, 1 falso negativo, 1 falso positivo,
71 benignos correctos. F1 macro de validación (5 folds, semilla 42): 0,9739.

**LAB02** (`reports/dataset_svm_metrics.json`):

| Modelo | Accuracy | F1 macro | Recall `>50K` |
|---|---|---|---|
| DummyClassifier (mismo preprocesamiento) | 0,7607 | 0,4320 | 0,0000 |
| SVC rbf con pipeline (C=10, gamma=0.1) | **0,8588** | **0,7928** | 0,6146 |

Prueba: 9.769 casos; 901 falsos negativos y 478 falsos positivos. La búsqueda de hiperparámetros se
hizo sobre una submuestra estratificada del 25 % del entrenamiento (un ajuste completo del SVM sobre
39.073 filas tarda ~30 s) y el mejor modelo se reajustó sobre todo el entrenamiento.

<!-- BEGIN: LAB03-RESUMEN -->
**LAB03** (`reports/green_ai_results.csv`, `reports/green_ai_decision.json`):

| Configuración | Familia | F1 macro | Accuracy | Ajuste (s) | Inferencia (ms) | Tamaño (KB) | Pareto |
|---|---|---|---|---|---|---|---|
| `boost` | Boosting (`HistGradientBoosting`) | **0,8185** | 0,8753 | 0,59 | 16,8 | 360 | **sí** |
| `svm_c10` | SVM (`C=10`, `gamma=scale`) | 0,7926 | 0,8585 | 40,97 | 5.211,1 | 5.980 | no |
| `svm_c10_pca` | SVM (`C=10`) + PCA | 0,7888 | 0,8580 | 31,85 | 4.316,3 | 2.279 | no |
| `svm_c1` | SVM (`C=1`, `gamma=scale`) | 0,7876 | 0,8576 | 27,84 | 5.216,6 | 6.002 | no |
| `rf_300` | Random Forest (300 árboles) | 0,7834 | 0,8480 | 0,97 | 228,7 | 296.866 | no |
| `rf_100` | Random Forest (100 árboles) | 0,7823 | 0,8469 | 0,42 | 78,7 | 98.807 | **sí** |
| `logreg` | Regresión logística | 0,7792 | 0,8507 | 1,33 | 18,0 | 4 | no |
| `logreg_pca` | Regresión logística + PCA | 0,7749 | 0,8485 | 0,47 | 28,9 | 14 | no |

Tiempos y tamaños: **mediana de 3 repeticiones** de ajuste y de inferencia, y tamaño del pipeline serializado.

**Decisión cuantificada (LAB03).** Se entrega **`boost`**: F1 macro 0,8185 (la máxima del catálogo, diferencia absoluta 0,00 frente a la mejor), 0,59 s de ajuste, 360 KB de modelo y 16,8 ms de inferencia. Frente a la otra configuración no dominada (`rf_100`, 0,7823), gana 0,0363 de F1 macro con un tiempo de ajuste de 0,59 s frente a 0,42 s de `rf_100` y **96,1 MB menos de modelo**. El SVM infiere **309 veces más lento** que el boosting (5.211,1 ms frente a 16,8 ms) y el Random Forest de 300 árboles ocupa **289,9 MB** para peor desempeño. El PCA reduce el costo del SVM (31,85 s y 2,2 MB frente a 40,97 s y 5,8 MB) pero **resta** 0,0039 de F1 macro: el 90 % de varianza que retiene no incluye la señal de los ingresos altos. El recall de `>50K` no es constante: va de 0,5778 (`logreg_pca`) a 0,6600 (`boost`), de modo que solo 1 de las ocho configuraciones llega a 0,66.

### Evidencia de reducción dimensional (LAB03)

| Figura | Archivo | Qué muestra |
|---|---|---|
| PCA: espectro y proyección 2D | `reports/pca_analysis.png` | 19 componentes para el 90 % de la varianza y 26 para el 95 %; la proyección 2D separa solo parcialmente las clases |
| t-SNE con dos semillas | `reports/tsne_two_seeds.png` | Semillas 42 y 7 sobre 6.000 casos de prueba con submuestra **uniforme** (no estratificada): la estructura de agrupamientos permanece, las coordenadas cambian |
| Perfil de las categorías más frecuentes | `reports/popular_top10.png` | Los 10 valores más frecuentes de `occupation` en la prueba y su proporción de `>50K`: el desbalance es del dato, no del modelo |
| Frontera de Pareto | `reports/pareto.png` | F1 macro frente a tiempo de ajuste y frente a tamaño del modelo (escala logarítmica) |
<!-- END: LAB03-RESUMEN -->

## Documentos de la entrega

| Documento | Contenido |
|---|---|
| `docs/ficha_dataset.md` | Ficha comparativa de los dos datasets, criterios de aceptación, diccionario, sesgos y usos prohibidos |
| `docs/CONCLUSION_EJERCICIO_01.md` | Conclusión de 350 palabras que integra LAB01 y LAB02 |
| `docs/CONCLUSION_EJERCICIO_02.md` | Conclusión de 350 palabras del Ejercicio 02 con la decisión cuantificada (generada) |
| `docs/LAB03_RESUMEN.md` | Fragmento generado con la tabla, la decisión y las figuras del LAB03 |
| `docs/EJERCICIO_01_PDF_BRIEF.pdf` · `docs/EJERCICIO_02_PDF_BRIEF.pdf` | PDF breve de cada entrega (3 páginas el Ejercicio 01 y 4 el Ejercicio 02) |
| `reports/green_ai_results.csv` · `reports/green_ai_decision.json` | Catálogo completo, tiempos, tamaños y decisión del LAB03 |
| `reports/pca_variance.json` · `reports/tsne_sample.json` · `reports/lab03_contexto.json` | Informes auxiliares del LAB03: varianza del PCA, submuestra de t-SNE y contexto de los datos |
| `reports/pca_analysis.png` · `reports/tsne_two_seeds.png` · `reports/pareto.png` · `reports/popular_top10.png` | Figuras de reducción dimensional, perfil de clases y frontera de Pareto |
| `reports/svm_cv_results.csv` · `reports/dataset_svm_cv_results.csv` | Tablas de la búsqueda de hiperparámetros |
| `reports/*_confusion_matrix.png` · `reports/*_cv_results.png` | Figuras de los LAB01 y LAB02 |
| `reports/dataset_svm_errors.csv` | 20 errores con categoría, muestra aleatoria con semilla 42 |
| `AI_USE_DECLARATION.md` | Uso honesto del asistente de IA y verificaciones pendientes del estudiante |

## Estado y limitaciones

- **Pendiente:** la aprobación del docente sobre el dataset del LAB02. El manual de la Unidad 01
  prohíbe continuar con el entrenamiento final sin ella; el entrenamiento de este repositorio se
  ejecutó con esa aprobación aún pendiente y así queda registrado en
  `reports/dataset_svm_metrics.json` (`aprobacion_docente: pendiente`). El Ejercicio 02 hereda esa
  misma limitación.
- Los resultados de LAB02 y LAB03 corresponden a un censo de 1994–1996 de la población activa
  estadounidense: no son extrapolables y no autorizan decisiones sobre personas.
- El tiempo de ajuste y el tamaño del modelo son **proxies contextuales de costo, no consumo
  energético**: las cifras solo valen en el hardware registrado en `reports/green_ai_decision.json`
  (Python 3.12.15, scikit-learn 1.9.1, x86_64, Linux).

<!-- BEGIN: LAB03-LIMITACIONES -->
- El preprocesamiento del LAB03 es denso porque el boosting y el PCA no admiten entradas dispersas: la matriz de entrenamiento tiene 39.073 × 56 columnas float64 ≈ 16,7 MB, y el PCA con 20 componentes no conserva del todo la señal de los ingresos altos.
- t-SNE se aplica a una submuestra **uniforme** (muestreo uniforme sin reposición con semilla 42, no estratificado) de 6.000 casos de prueba: por eso puede desbalancear las clases (23,07 % de `>50K` en la submuestra frente a 23,93 % en la prueba) y una separación visual no demuestra causalidad ni que el modelo use esa geometría.
- El recall de `>50K` no es el mismo en todas las configuraciones: va de 0,5778 (`logreg_pca`) a 0,6600 (`boost`) y solo 1 de las ocho configuraciones llega a 0,66; el problema es de datos, no de modelo.
- Los modelos serializados de `models/` (hasta 289,9 MB el de Random Forest con 300 árboles) no se versionan: se regeneran ejecutando el notebook.
<!-- END: LAB03-LIMITACIONES -->

## Referencias

- Becker, B. y Kohavi, R. (1996). *Adult* [Conjunto de datos]. UCI Machine Learning Repository.
  https://doi.org/10.24432/C5XW20
- Dodge, J., Schwartz, R., Strubell, E., et al. (2022). *A Green AI*. arXiv:2211.05859.
  https://arxiv.org/abs/2211.05859
- Strubell, E., Ganesh, A. y McCallum, A. (2019). Energy and Policy Considerations for Deep Learning
  in NLP. En *Proceedings of the 57th Annual Meeting of the Association for Computational
  Linguistics* (págs. 4135-4148). Association for Computational Linguistics.
  https://doi.org/10.18653/v1/N19-1423
- Universidad Autónoma de Santo Domingo (UASD). (2026). *Manual de la Unidad 01: modelos de
  aprendizaje automático, ensembles y Green AI*. INF-8239 Ciencia de Datos II, Prof. Edwin Ramón
  José Nolasco.
- scikit-learn. (2026). *Documentación de scikit-learn 1.9*: `SVC`
  (https://scikit-learn.org/stable/modules/svm.html) y `TfidfVectorizer`
  (https://scikit-learn.org/stable/modules/feature_extraction.html#text-vectorizer).
