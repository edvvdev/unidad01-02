# Declaración de uso de inteligencia artificial · Unidad 01 (LAB00–LAB03)

Proyecto: `INF8239_U01` · Curso: INF-8239 Ciencia de Datos II · Fecha: 2026-11-05

## Herramientas utilizadas

- **Kilo** (asistente de IA en modo CLI, modelo MiniMax-M3) para leer el manual de la Unidad 01,
  estructurar el proyecto, escribir el código, ejecutar los experimentos y redactar la documentación.
- **Python 3.12 + scikit-learn 1.9 + pandas + matplotlib + Jupyter** (instalados con `uv` en esta
  máquina; el manual de la unidad usa `venv` + `requirements.txt`, y ambos caminos son equivalentes).
  No se usaron servicios en la nube, APIs externas ni datasets generados por IA.

## En qué ayudó

| Elemento | Detalle |
|---|---|
| Estructura del proyecto | `src/inf8239_u01/` (data, models, evaluation, green, informe), `tests/`, `notebooks/`, `reports/`, `docs/`, `requirements.txt` y `.gitignore` |
| LAB01 | `build_svm` con `ValueError` si `C <= 0`, pipeline con `StandardScaler`, `GridSearchCV` con `StratifiedKFold(5, shuffle=True, random_state=42)` y `scoring="f1_macro"`, tabla de `cv_results_`, matriz de confusión, modelo guardado con `joblib` |
| LAB02 | Comparación verificada de dos candidatos de UCI (Adult y Bank Marketing) con descarga, auditoría y riesgo de fuga; `download_dataset` con validación de URL y de dataframe vacío; `ColumnTransformer` con `SimpleImputer`+`StandardScaler` y `SimpleImputer`+`OneHotEncoder`; contrato de datos con pruebas |
| LAB03 | `src/inf8239_u01/green.py` con el catálogo de ocho configuraciones, la medición repetida con mediana, la serialización y la frontera de Pareto; `notebooks/03_ensembles_green_ai.ipynb` ejecutado de principio a fin (PCA, dos t-SNE, perfil de clases, frontera); `tests/test_green.py` |
| Documentación | `docs/ficha_dataset.md`, `docs/CONCLUSION_EJERCICIO_01.md`, `docs/CONCLUSION_EJERCICIO_02.md`, los dos PDF breves, este documento y el README |
| Automatización de la entrega | `scripts/generar_conclusion.py` (redacta la narrativa del LAB03 desde `reports/`), `scripts/verify_cifras.py` (contrasta lo publicado contra `reports/`), `src/inf8239_u01/informe.py` (motor de redacción) y los builders de los PDF |

## Correcciones aplicadas en esta revisión (Ejercicio 02 · LAB03)

La entrega anterior publicaba una **narrativa de una corrida previa**: la tabla del PDF sí se
generaba desde `reports/`, pero el README, `docs/CONCLUSION_EJERCICIO_02.md`, la celda de conclusión
del notebook y la sección 4 del PDF seguían con las cifras viejas, de modo que el PDF se contradecía
a sí mismo. La afirmación anterior de este documento («las cifras actuales se contrastaron contra
los JSON y CSV generados y dos cifras incorrectas se corrigieron») **era inexacta**: los desfases eran
más de una decena. Esta es la lista real de correcciones:

| # | Defecto detectado | Corrección aplicada |
|---|---|---|
| 1 | Tiempos de ajuste e inferencia de las ocho configuraciones desfasados (README, conclusión, notebook y PDF) | Toda la narrativa se **genera** desde `reports/green_ai_results.csv` y `reports/green_ai_decision.json` con `scripts/generar_conclusion.py` |
| 2 | «El SVM infiere 214 veces más lento (5.228 s frente a 24,4 ms)» | El ratio vigente es `ratio_inferencia_svm_sobre_boost` del JSON, y **5.228 son milisegundos**, no segundos |
| 3 | «98,4 MB menos de modelo» | El JSON expresa KB (`diferencia_tamano_vs_alternativa_kb`); la cifra en MB estaba mal convertida |
| 4 | «El Random Forest de 300 árboles ocupa 296,9 MB» | El CSV lo da en KB (`model_size_kb`); la conversión a MB se recalcula |
| 5 | «Gana 0,0363 de F1 macro con 0,18 s más de ajuste» | La diferencia de tiempo de ajuste se recalcula con los valores vigentes |
| 6 | «El PCA reduce el costo del SVM (31,3 s y 2,3 MB frente a 43,9 s y 6,0 MB)» | Se usan los valores vigentes del CSV para las dos configuraciones |
| 7 | «El recall de `>50K` sigue en 0,66 en todas las configuraciones» | El rango real va de 0,5778 (`logreg_pca`) a 0,6600 (`boost`): solo una configuración llega a 0,66 |
| 8 | «48.842 × 58 columnas float64 ≈ 21 MB» | La matriz densa de entrenamiento es (39.073, 56) ≈ 16,7 MB; queda en `reports/lab03_contexto.json` |
| 9 | «~18 componentes para el 90 % de la varianza» | El notebook calcula **19** componentes (y 26 para el 95 %) y los guarda en `reports/pca_variance.json` |
| 10 | La submuestra de t-SNE estaba rotulada como «estratificada» | El muestreo es **uniforme** (`np.random.default_rng(42).choice`): se corrige el rótulo en el README, en este documento, en el notebook y en el título de `reports/tsne_two_seeds.png`, y se explica que el muestreo uniforme puede desbalancear las clases (23,07 % de `>50K` frente al 23,93 % de la prueba) |
| 11 | Erratas del PDF: «elExercise 02» y el bloque final que repetía literalmente el último párrafo de la conclusión | Typo corregido y bloque final reescrito sin repetir la conclusión |
| 12 | El PDF se regeneraba sin el enlace al repositorio («PENDIENTE: enlace de GitHub») | Los builders usan **por defecto** la URL de publicación (`https://github.com/edvvdev/unidad01-02` y `https://github.com/edvvdev/unidad01-01`); `REPO_URL` la sobrescribe |
| 13 | La rúbrica pide referencias bibliográficas y el repositorio no tenía ninguna | Sección **Referencias** en el README, en la conclusión y en el PDF (Strubell et al. 2019; Dodge et al. 2022; documentación de scikit-learn para `SVC` y `TfidfVectorizer`; manual de la Unidad 01; cita del dataset de UCI) |
| 14 | `uv run ruff check .` no existía porque `ruff` no estaba declarado | `ruff` añadido al grupo `dev` de `pyproject.toml` (con `uv.lock` actualizado) y corregidos los 23 hallazgos heredados |
| 15 | Las cifras dependían de que alguien las actualizara a mano | `scripts/verify_cifras.py` compara README, conclusión, notebook y PDF contra `reports/` y **falla** si no coinciden; `scripts/run_all.sh` lo ejecuta al final |

## Qué debe ejecutar y verificar el estudiante

- [x] `python -m venv .venv` · `.venv\Scripts\Activate.ps1` · `pip install -r requirements.txt` · `$env:PYTHONPATH="src"`. En esta máquina se verificó la variante equivalente con `uv sync`, que fija las versiones en `uv.lock`.
- [x] `python -m pytest -q` → **21 passed** (salida real: `21 passed in 1.26s`).
- [x] `uv run ruff check .` → **All checks passed!**
- [x] `uv run python scripts/verify_cifras.py` → **OK: las cifras publicadas (README, conclusión, notebook y PDF) coinciden con reports/.**
- [x] `uv run python -m jupyter nbconvert --to notebook --execute --inplace notebooks/01_svm_guiada.ipynb`, el mismo con `02_dataset_svm.ipynb` y con `03_ensembles_green_ai.ipynb` → los tres se ejecutaron de principio a fin **sin ninguna celda en error**.
- [x] Revisar las figuras `reports/svm_confusion_matrix.png`, `reports/dataset_svm_confusion_matrix.png`, `reports/pareto.png`, `reports/pca_analysis.png`, `reports/tsne_two_seeds.png` y `reports/popular_top10.png` (títulos legibles, sin textos encimados).
- [x] Regenerar los PDF con `python scripts/build_ejercicio01_pdf.py` y `python scripts/build_ejercicio02_pdf.py`: ambos llevan el nombre del estudiante y la URL del repositorio y **no queda ningún campo `PENDIENTE`**. La matrícula y el correo institucional no se publican: se eliminaron a propósito y no hay que completarlos.
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
6. **LAB03 · t-SNE sobre 6.000 casos con submuestra uniforme**: por costo computacional se usa un
   muestreo **uniforme** con semilla fija (`np.random.default_rng(42).choice`), que **no** es estratificado
   y por eso puede desbalancear las clases: midió 23,07 % de `>50K` en la submuestra frente al 23,93 %
   de la prueba. Se documenta en la figura, en el README y en la conclusión.
7. **LAB03 · la narrativa se genera**: el README, la conclusión y el PDF se redactan con
   `scripts/generar_conclusion.py` a partir de `reports/`, y `scripts/verify_cifras.py` falla si
   dejan de coincidir. Editar esas cifras a mano es contraproducente.

## Límites declarados

- Las cifras de este repositorio provienen de ejecuciones en esta máquina Linux; el estudiante debe
  reejecutarlas en su entorno de entrega (Windows, VS Code, PowerShell) antes de presentarlas.
- El asistente **no** redactó las conclusiones finales sin revisión: en el LAB03 la conclusión se
  genera desde `reports/` y `scripts/verify_cifras.py` comprueba que lo publicado coincide con esos
  artefactos, pero la revisión humana de los errores categorizados del LAB02 y de la interpretación de
  las figuras queda pendiente.
- La revisión anterior **sí** arrastraba cifras desfasadas del LAB03 (más de una decena, listadas
  arriba): la afirmación previa de que solo se habían corregido dos cifras era inexacta y queda
  sustituida por la tabla de correcciones.
- No se afirma que los modelos sirvan para decisiones sobre personas: los resultados de LAB02
  corresponden a un censo de 1994–1996 de la población activa estadounidense.
