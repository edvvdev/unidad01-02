# Conclusión · Ejercicio 02 (LAB03)

Proyecto: `INF8239_U01` · Unidad 01 · Fecha: 2026-11-05 · Extensión: 350 palabras

<!-- INICIO CUERPO -->

**Qué se comparó.** Ocho configuraciones homogéneas sobre el dataset, el target y la partición aprobados en el Ejercicio 01 (Adult / Census Income, UCI, CC BY 4.0; target `income`; partición estratificada 80/20 con semilla 42; 9.769 casos de prueba): regresión logística, SVM con `C=1` y `C=10`, Random Forest de 100 y 300 árboles, boosting (`HistGradientBoosting`) y dos variantes con reducción por PCA de 20 componentes. Cada configuración se ajustó **tres veces** y se reporta la **mediana** del tiempo de ajuste y de la inferencia, más el tamaño del pipeline serializado.

**Resultado.** El F1 macro va de 0,7749 (`logreg_pca`) a **0,8185 (`boost`)**. El boosting gana con 0,59 s de ajuste, 360 KB de modelo y 16,8 ms de inferencia: es simultáneamente la mejor utilidad y una de las opciones más baratas, por lo que la diferencia absoluta de F1 macro frente a la mejor configuración es 0,00. Frente a la otra configuración no dominada (`rf_100`, 0,7823) gana 0,0363 de F1 macro con un tiempo de ajuste de 0,59 s frente a 0,42 s de `rf_100` y **96,1 MB menos de modelo**. El SVM, en cambio, infiere **309 veces más lento** (5.211,1 ms frente a 16,8 ms para las mismas 9.769 filas) y el Random Forest de 300 árboles ocupa **289,9 MB** para peor desempeño. El PCA reduce el costo del SVM (31,85 s y 2,2 MB frente a 40,97 s y 5,8 MB) pero **resta** 0,0039 de F1 macro: el 90 % de varianza que retiene no incluye la señal que separa los ingresos altos. Los dos mapas t-SNE (semillas 42 y 7) conservan los mismos agrupamientos aunque cambian las coordenadas: la estructura persiste, la representación no.

**Decisión y defensa.** Se entrega `boost`: máxima utilidad y costo entre los más bajos. El tiempo de ajuste y el tamaño del modelo son **proxies contextuales de costo, no consumo energético**; las cifras solo valen en el hardware registrado (Python 3.12.15, scikit-learn 1.9.1, x86_64, Linux). La limitación de fondo es la del Ejercicio 01: `capital_gain` está ausente en el 91,74 % de las filas y el recall de `>50K` va de 0,5778 (`logreg_pca`) a 0,6600 (`boost`): ninguna frontera de Pareto arregla un problema de datos. La submuestra de t-SNE es **uniforme**, no estratificada, de modo que puede desbalancear las clases (23,07 % de `>50K` frente a 23,93 % de la prueba).

**Pendiente crítico:** la aprobación del docente sobre el dataset sigue sin recibirse (arrastrada del Ejercicio 01) y este ejercicio se ejecutó con esa aprobación pendiente, tal como consta en `reports/green_ai_decision.json`.

<!-- FIN CUERPO -->

## Referencias

- Becker, B. y Kohavi, R. (1996). *Adult* [Conjunto de datos]. UCI Machine Learning Repository. https://doi.org/10.24432/C5XW20
- Dodge, J., Schwartz, R., Strubell, E., et al. (2022). *A Green AI*. arXiv:2211.05859. https://arxiv.org/abs/2211.05859
- Strubell, E., Ganesh, A. y McCallum, A. (2019). Energy and Policy Considerations for Deep Learning in NLP. En *Proceedings of the 57th Annual Meeting of the Association for Computational Linguistics* (págs. 4135-4148). Association for Computational Linguistics. https://doi.org/10.18653/v1/N19-1423
- Universidad Autónoma de Santo Domingo (UASD). (2026). *Manual de la Unidad 01: modelos de aprendizaje automático, ensembles y Green AI*. INF-8239 Ciencia de Datos II, Prof. Edwin Ramón José Nolasco.
- scikit-learn. (2026). *Documentación de scikit-learn 1.9*: `SVC` (https://scikit-learn.org/stable/modules/svm.html) y `TfidfVectorizer` (https://scikit-learn.org/stable/modules/feature_extraction.html#text-vectorizer).

## Figuras

| Figura | Archivo |
|---|---|
| Frontera de Pareto | `reports/pareto.png` |
| PCA: espectro y proyección 2D | `reports/pca_analysis.png` |
| t-SNE con dos semillas | `reports/tsne_two_seeds.png` |
| Perfil de las categorías más frecuentes | `reports/popular_top10.png` |

> Documento generado por `scripts/generar_conclusion.py` a partir de `reports/green_ai_results.csv`, `reports/green_ai_decision.json` y los informes auxiliares del notebook. No editar a mano: las cifras se vuelven a escribir en cada ejecución.
