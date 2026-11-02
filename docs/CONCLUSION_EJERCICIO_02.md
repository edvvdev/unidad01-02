# Conclusión · Ejercicio 02 (LAB03)

Proyecto: `INF8239_U01` · Unidad 01 · Fecha: 2026-11-02 · Extensión: 350 palabras

**Qué se comparó.** Ocho configuraciones homogéneas sobre el dataset, el target y la partición
aprobados en el Ejercicio 01 (Adult / Census Income, UCI, CC BY 4.0; target `income`; partición
estratificada 80/20 con semilla 42; 9.769 casos de prueba): regresión logística, SVM con `C=1` y
`C=10`, Random Forest de 100 y 300 árboles, boosting (`HistGradientBoosting`) y dos variantes con
reducción por PCA de 20 componentes. Cada configuración se ajustó **tres veces** y se reporta la
**mediana** del tiempo de ajuste y de la inferencia, más el tamaño del pipeline serializado.

**Resultado.** El F1 macro va de 0,7749 (`logreg_pca`) a **0,8185 (`boost`)**. El boosting gana con
0,56 s de ajuste, 360 KB de modelo y 24,4 ms de inferencia: es simultáneamente la mejor utilidad y una
de las opciones más baratas, por lo que la diferencia absoluta de F1 macro frente a la mejor
configuración es 0,00. Frente a la otra configuración no dominada (`rf_100`, 0,7823) gana 0,0363 de F1
macro con 0,18 s más de ajuste y **98,4 MB menos de modelo**. El SVM, en cambio, infiere **214 veces más
lento** (5.228 s frente a 24,4 ms para las mismas 9.769 filas) y el Random Forest de 300 árboles ocupa
**296,9 MB** para peor desempeño. El PCA reduce el costo del SVM (31,3 s y 2,3 MB frente a 43,9 s y
6,0 MB) pero **resta** 0,0038 de F1 macro: el 90 % de varianza que retiene no incluye la señal que
separa los ingresos altos. Los dos mapas t-SNE (semillas 42 y 7) conservan los mismos agrupamientos
aunque cambian las coordenadas: la estructura persiste, la representación no.

**Decisión y defensa.** Se entrega `boost`: máxima utilidad y costo entre los más bajos. El tiempo de
ajuste y el tamaño del modelo son **proxies contextuales de costo, no consumo energético**; las
cifras solo valen en el hardware registrado (Python 3.12.15, scikit-learn 1.9.1, x86_64, Linux). La
limitación de fondo es la del Ejercicio 01: `capital_gain` está ausente en el 91,74 % de las filas y el
recall de `>50K` sigue en 0,66 en todas las configuraciones. Ninguna frontera de Pareto arregla un
problema de datos.

**Pendiente crítico:** la aprobación del docente sobre el dataset sigue sin recibirse (arrastrada del
Ejercicio 01) y este ejercicio se ejecutó con esa aprobación pendiente, tal como consta en
`reports/green_ai_decision.json`.
