# INF-8239 · Unidad 01 · Ejercicio 01 (LAB01 + LAB02)

Curso: Ciencia de Datos II (INF-8239) · Profesor: Edwin Ramón José Nolasco

Proyecto de los laboratorios guiados 00–03 de la Unidad 01. Este README documenta el **Ejercicio 01**
(entrega que integra LAB01 y LAB02). Los laboratorios 01 y 02 se resuelven en este mismo proyecto,
porque LAB03 reutiliza el dataset, el target y las exclusiones del LAB02.

## Instalación (Windows, PowerShell)

```powershell
cd C:\Proyectos\INF8239_U01
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
$env:PYTHONPATH="src"
python -m pytest -q
```

Resultado esperado: `21 passed`. Para ejecutar los notebooks se necesita además el kernel de Jupyter:

```powershell
python -m pip install -r requirements-dev.txt
python -m jupyter nbconvert --to notebook --execute --inplace notebooks/01_svm_guiada.ipynb
python -m jupyter nbconvert --to notebook --execute --inplace notebooks/02_dataset_svm.ipynb
python -m jupyter nbconvert --to notebook --execute --inplace notebooks/03_ensembles_green_ai.ipynb
```

> El notebook del Ejercicio 02 ajusta **ocho modelos tres veces cada uno**: tarda entre 10 y 15 minutos
> en CPU. Para regenerar solo la figura del Pareto a partir del CSV ya calculado, basta con volver a
> ejecutar esa celda.

Los PDF breves de las dos entregas se regeneran con `python scripts/build_ejercicio01_pdf.py` y
`python scripts/build_ejercicio02_pdf.py` (requieren `reportlab`, incluido en `requirements-dev.txt`).

## Descarga reproducible de los datos

Ninguno de los dos datasets requiere cuenta ni ruta personal: la descarga la hace un script que
valida la URL y registra el SHA-256 de los bytes obtenidos.

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
│   ├── CONCLUSION_EJERCICIO_02.md
│   ├── EJERCICIO_01_PDF_BRIEF.pdf
│   └── EJERCICIO_02_PDF_BRIEF.pdf
├── models/                  pipelines serializados (no versionados: *.joblib)
├── notebooks/
│   ├── 00_verificacion.ipynb      LAB00 · verificación del entorno
│   ├── 01_svm_guiada.ipynb        LAB01 · SVM con pipeline, GridSearchCV y evaluación
│   ├── 02_dataset_svm.ipynb       LAB02 · dataset público, auditoría y pipeline completo
│   └── 03_ensembles_green_ai.ipynb LAB03 · catálogo, PCA, t-SNE y frontera de Pareto
├── reports/                     métricas, tablas y figuras generadas
├── scripts/                    generadores de los PDF breves de entrega
├── src/inf8239_u01/
│   ├── data.py               carga, auditoría y descarga reproducible
│   ├── models.py             build_svm, build_baseline, ColumnTransformer, build_svm_pipeline
│   ├── evaluation.py         partición, métricas, matrices de confusión y figuras
│   └── green.py              catálogo de configuraciones, medición repetida y frontera de Pareto
├── tests/                    test_environment.py · test_models.py · test_data_contract.py · test_green.py
├── requirements.txt
├── requirements-dev.txt
└── AI_USE_DECLARATION.md
```

## Target y métrica

| Laboratorio | Dataset | Target (binario) | Métrica principal | Costo del error |
|---|---|---|---|---|
| LAB01 | Breast Cancer Wisconsin (diagnóstico) | `target`: 0 maligno · 1 benigno | F1 macro (media de las clases) | Falso negativo: maligno clasificado como benigno |
| LAB02 | UCI Adult (Census Income) | `income`: `<=50K` / `>50K` | F1 macro | Falso negativo: califica y no se detecta (posible denegación de crédito) |

## Ejecución

```bash
# LAB01
uv run python scripts/...   # o abrir notebooks/01_svm_guiada.ipynb y ejecutar todas las celdas
python -m pytest tests/test_models.py -q

# LAB02
python -m pytest tests/test_data_contract.py -q
```

Comandos equivalents para los notebooks: `python -m jupyter nbconvert --to notebook --execute --inplace notebooks/01_svm_guiada.ipynb` y el mismo para `02_dataset_svm.ipynb`.

## Resultados de referencia (2026-11-02)

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


## Ejercicio 02 · LAB03 (ensambles, reducción dimensional y Green AI)

### Qué se comparó

Ocho configuraciones homogéneas sobre el **mismo dataset, target y partición** del Ejercicio 01
(Adult / Census Income, UCI, CC BY 4.0; target `income`; partición estratificada 80/20 con semilla
42; 9.769 casos de prueba), con el mismo preprocesamiento dentro del pipeline:

| Configuración | Familia | F1 macro | Accuracy | Ajuste (s) | Inferencia (ms) | Tamaño (KB) | Pareto |
|---|---|---|---|---|---|---|---|
| `boost` | Boosting (HistGradientBoosting) | **0,8185** | 0,8753 | 0,56 | 24,4 | 360 | **sí** |
| `svm_c10` | SVM (C=10, gamma=scale) | 0,7926 | 0,8585 | 43,9 | 5.228,0 | 5.980 | no |
| `svm_c10_pca` | SVM + PCA (20 componentes) | 0,7888 | 0,8580 | 31,3 | 4.304,9 | 2.279 | no |
| `svm_c1` | SVM (C=1, gamma=scale) | 0,7876 | 0,8576 | 29,6 | 5.250,8 | 6.002 | no |
| `rf_300` | Random Forest (300 árboles) | 0,7834 | 0,8480 | 0,92 | 145,4 | 296.866 | no |
| `rf_100` | Random Forest (100 árboles) | 0,7823 | 0,8469 | 0,38 | 89,3 | 98.807 | **sí** |
| `logreg` | Regresión logística | 0,7792 | 0,8507 | 1,86 | 28,1 | 4 | no |
| `logreg_pca` | Regresión logística + PCA | 0,7749 | 0,8485 | 0,58 | 20,1 | 14 | no |

Tiempos y tamaños: **mediana de 3 repeticiones** de ajuste y de inferencia, y tamaño del pipeline
serializado. Fuente: `reports/green_ai_results.csv` y `reports/green_ai_decision.json`.

### Decisión cuantificada

Se entrega **`boost`**: F1 macro 0,8185 (la máxima del catálogo, diferencia absoluta 0,00 frente a la
mejor), 0,56 s de ajuste, 360 KB de modelo y 24,4 ms de inferencia. Frente a la otra configuración no
dominada (`rf_100`, 0,7823) gana 0,0363 de F1 macro con 0,18 s más de ajuste y **98,4 MB menos de
modelo**. El SVM infiere **214 veces más lento** que el boosting (5.228 s frente a 24,4 ms) y el
Random Forest de 300 árboles ocupa 296,9 MB para peor desempeño. El PCA reduce el costo del SVM
(31,3 s y 2,3 MB frente a 43,9 s y 6,0 MB) pero resta 0,0038 de F1 macro.

### Evidencia de reducción dimensional

| Figura | Archivo | Qué muestra |
|---|---|---|
| PCA: espectro y proyección 2D | `reports/pca_analysis.png` | ~18 componentes para el 90 % de la varianza; la proyección 2D separa solo parcialmente las clases |
| t-SNE con dos semillas | `reports/tsne_two_seeds.png` | Semillas 42 y 7 sobre 6.000 casos de prueba: la estructura de agrupamientos permanece, las coordenadas cambian |
| Frontera de Pareto | `reports/pareto.png` | F1 macro frente a tiempo de ajuste y frente a tamaño del modelo (escala logarítmica) |

### Limitaciones

- El tiempo de ajuste y el tamaño del modelo son **proxies contextuales de costo, no consumo
  energético**: las cifras solo valen en el hardware registrado en `reports/green_ai_decision.json`
  (Python 3.12.15, scikit-learn 1.9.1, x86_64, Linux).
- El preprocesamiento es denso porque el boosting y el PCA no admiten entradas dispersas: 48.842 × 58
  columnas float64 ≈ 21 MB, y el PCA con 20 componentes no conserva la señal de los ingresos altos.
- t-SNE se aplica a una submuestra estratificada de 6.000 casos por costo computacional; una
  separación visual no demuestra causalidad ni que el modelo use esa geometría.
- El recall de `>50K` sigue en 0,66 en todas las configuraciones: el problema es de datos, no de
  modelo.

## Documentos de la entrega

| Documento | Contenido |
|---|---|
| `docs/ficha_dataset.md` | Ficha comparativa de los dos datasets, criterios de aceptación, diccionario, sesgos y usos prohibidos |
| `docs/CONCLUSION_EJERCICIO_01.md` | Conclusión de 350 palabras que integra LAB01 y LAB02 |
| `docs/CONCLUSION_EJERCICIO_02.md` | Conclusión de 350 palabras del Ejercicio 02 con la decisión cuantificada |
| `docs/EJERCICIO_01_PDF_BRIEF.pdf` · `docs/EJERCICIO_02_PDF_BRIEF.pdf` | PDF breve de cada entrega (3 páginas) |
| `reports/green_ai_results.csv` · `reports/green_ai_decision.json` | Catálogo completo, tiempos, tamaños y decisión del LAB03 |
| `reports/pca_analysis.png` · `reports/tsne_two_seeds.png` · `reports/pareto.png` | Figuras de reducción dimensional y frontera de Pareto |
| `reports/svm_cv_results.csv` · `reports/dataset_svm_cv_results.csv` | Tablas de la búsqueda de hiperparámetros |
| `reports/*_confusion_matrix.png` · `reports/*_cv_results.png` | Figuras |
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
- Los modelos serializados de `models/` (hasta 296,9 MB el de Random Forest con 300 árboles) no se
  versionan: se regeneran ejecutando el notebook.
