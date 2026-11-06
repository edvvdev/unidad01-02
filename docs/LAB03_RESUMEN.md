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
