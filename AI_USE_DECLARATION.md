# Declaración de uso de inteligencia artificial · Unidad 01 (LAB00–LAB03)

Proyecto: `INF8239_U01` · Curso: INF-8239 Ciencia de Datos II · Fecha: 2026-11-02

## Herramientas utilizadas

- **Kilo** (asistente de IA en modo CLI, modelo MiniMax-M3) para leer el manual de la Unidad 01,
  estructurar el proyecto, escribir el código, ejecutar los experimentos y redactar la documentación.
- **Python 3.12 + scikit-learn 1.9 + pandas + matplotlib + Jupyter** (instalados con `uv` en esta
  máquina; el manual de la unidad usa `venv` + `requirements.txt`, y ambos caminos son equivalentes).
  No se usaron servicios en la nube, APIs externas ni datasets generados por IA.

## En qué ayudó

| Elemento | Detalle |
|---|---|
| Estructura del proyecto | `src/inf8239_u01/` (data, models, evaluation), `tests/`, `notebooks/`, `reports/`, `docs/`, `requirements.txt` y `.gitignore` |
| LAB01 | `build_svm` con `ValueError` si `C <= 0`, pipeline con `StandardScaler`, `GridSearchCV` con `StratifiedKFold(5, shuffle=True, random_state=42)` y `scoring="f1_macro"`, tabla de `cv_results_`, matriz de confusión, modelo guardado con `joblib` |
| LAB02 | Comparación verificada de dos candidatos de UCI (Adult y Bank Marketing) con descarga, auditoría y riesgo de fuga; `download_dataset` con validación de URL y de dataframe vacío; `ColumnTransformer` con `SimpleImputer`+`StandardScaler` y `SimpleImputer`+`OneHotEncoder`; contrato de datos con pruebas |
| LAB03 | `src/inf8239_u01/green.py` con el catálogo de ocho configuraciones, la medición repetida con mediana, la serialización y la frontera de Pareto; `notebooks/03_ensembles_green_ai.ipynb` ejecutado de principio a fin (PCA, dos t-SNE, frontera); `tests/test_green.py` |
| Documentación | `docs/ficha_dataset.md`, `docs/CONCLUSION_EJERCICIO_01.md`, `docs/CONCLUSION_EJERCICIO_02.md`, los dos PDF breves, este documento y el README |
| Revisión crítica | Se detectaron y corrigieron **tres errores propios** antes de entregar: el mapeo TP/TN/FN/FP del LAB01 (las clases son 0 = maligno, 1 = benigno), las cifras del baseline del LAB01 que en el README eran incorrectas, y en el LAB03 la leyenda duplicada de la figura t-SNE y la ausencia del panel de tamaño del modelo en la figura de Pareto. Las cifras actuales salen de `reports/svm_metrics.json`, `reports/dataset_svm_metrics.json`, `reports/green_ai_results.csv` y `reports/green_ai_decision.json` |

## Qué debe ejecutar y verificar el estudiante

- [ ] `python -m venv .venv` · `.venv\Scripts\Activate.ps1` · `pip install -r requirements.txt` · `$env:PYTHONPATH="src"`.
- [ ] `python -m pytest -q` → 21 passed (aquí: 21 passed).
- [ ] `python -m jupyter nbconvert --to notebook --execute --inplace notebooks/01_svm_guiada.ipynb`, el mismo con `02_dataset_svm.ipynb` y con `03_ensembles_green_ai.ipynb` (este último tarda 10–15 min en CPU): comprobar que las salidas coinciden con las de este repositorio. **Los tiempos pueden variar**: lo reproducible son las métricas.
- [ ] Revisar las figuras `reports/svm_confusion_matrix.png`, `reports/dataset_svm_confusion_matrix.png`, `reports/pareto.png`, `reports/pca_analysis.png` y `reports/tsne_two_seeds.png` (títulos legibles, sin textos encimados).
- [ ] Regenerar los PDF con `python scripts/build_ejercicio01_pdf.py` y `python scripts/build_ejercicio02_pdf.py`, y completar los campos `PENDIENTE` (nombre, matrícula y URL del repositorio) **antes** de entregarlos.
- [ ] Leer los 20 errores de `reports/dataset_svm_errors.csv` y **revisar o reetiquetar las categorías**
      a mano: las categorías actuales las propone una regla automática y son una hipótesis a verificar.
- [ ] Tomar las capturas de pantalla con `cls` antes de cada una y nombrarlas por laboratorio.

## Decisiones que el estudiante debe confirmar

1. **Aprobación del docente sobre el dataset del LAB02.** El manual de la Unidad 01 prohíbe continuar
   con el entrenamiento final sin ella. Se entrenó con la aprobación pendiente y así queda
   registrado en `reports/dataset_svm_metrics.json` (`aprobacion_docente: pendiente`). Hay que enviar
   `docs/ficha_dataset.md` al profesor y anotar la fecha de respuesta.
2. **Elección del dataset**: se eligió *Adult (Census Income)* por ser el único que cumple los cinco
   criterios de aceptación sin exigir excluir una variable por fuga de información; *Bank Marketing*
   queda documentado como alternativa (exige excluir `duration`).
3. **Exclusiones**: `fnlwgt`, `race`, `sex` y `native_country` quedan fuera por motivo semántico y de
   equidad, no porque su eliminación mejore la métrica. Si el docente exige otra decisión, se
   documenta en `docs/ficha_dataset.md`.
4. **Búsqueda de hiperparámetros del LAB02** sobre submuestra estratificada del 25 % (un ajuste
   completo sobre 39.073 filas tarda ~30 s), con rejuste final sobre todo el entrenamiento. Es una
   decisión de costo, explicada en el propio notebook.
5. **LAB03 · preprocesamiento denso para todo el catálogo**: el boosting y el PCA no admiten entradas
   dispersas, y se optó por usar el mismo preprocesamiento denso en las ocho configuraciones para que
   la comparación sea homogénea. El SVM del Ejercicio 01 usaba la versión dispersa; su F1 macro
   (0,7926) es consistente con el de entonces (0,7928).
6. **LAB03 · t-SNE sobre 6.000 casos**: por costo computacional se usa una submuestra estratificada
   con semilla fija, y se documenta en la figura y en la conclusión.

## Límites declarados

- Las cifras de este repositorio provienen de ejecuciones en esta máquina Linux; el estudiante debe
  reejecutarlas en su entorno de entrega (Windows, VS Code, PowerShell) antes de presentarlas.
- El asistente **no** redactó las conclusiones finales sin revisión: las versiones actuales se
  contrastaron contra los JSON y CSV generados (y dos cifras incorrectas se corrigieron), pero la
  revisión humana de los errores categorizados del LAB02 y de la interpretación de las figuras
  queda pendiente.
- No se afirma que los modelos sirvan para decisiones sobre personas: los resultados de LAB02
  corresponden a un censo de 1994–1996 de la población activa estadounidense.
