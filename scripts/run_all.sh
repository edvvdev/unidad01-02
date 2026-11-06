#!/usr/bin/env bash
# Ejecuta todo el flujo de la Unidad 01 (Ejercicios 01 y 02) en Linux/macOS.
#
# Usa uv si está disponible; si no, recurre al entorno virtual con venv + requirements.txt
# (el procedimiento que describe el manual de la Unidad 01).
#
#   ./scripts/run_all.sh              # todo (incluye el notebook lento del LAB03)
#   SKIP_EJ02=1 ./scripts/run_all.sh  # omite notebooks/03_ensembles_green_ai.ipynb
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

if command -v uv >/dev/null 2>&1; then
  echo "==> Entorno: uv (uv sync)"
  uv sync
  RUN=(uv run)
  export REPO_URL_E01="${REPO_URL_E01:-https://github.com/edvvdev/unidad01-01}"
  export REPO_URL_E02="${REPO_URL_E02:-https://github.com/edvvdev/unidad01-02}"
else
  PY=".venv/bin/python"
  if [ ! -x "$PY" ]; then
    echo "No hay uv ni entorno .venv. Elige una de estas dos opciones:" >&2
    echo "  a) uv sync                      (recomendado)" >&2
    echo "  b) python3 -m venv .venv && .venv/bin/pip install -r requirements.txt -r requirements-dev.txt" >&2
    exit 1
  fi
  echo "==> Entorno: .venv (venv + requirements.txt)"
  export PYTHONPATH="src"
  RUN=("$PY")
  export REPO_URL_E01="${REPO_URL_E01:-https://github.com/edvvdev/unidad01-01}"
  export REPO_URL_E02="${REPO_URL_E02:-https://github.com/edvvdev/unidad01-02}"
fi

echo "==> 1/6. Dataset (se descarga una vez; el notebook también lo hace solo)"
"${RUN[@]}" - <<'CODE'
from inf8239_u01.data import download_dataset
print("adult:", download_dataset("adult", "data/raw"))
print("bank (candidato alterno):", download_dataset("bank", "data/raw"))
CODE

echo "==> 2/6. Pruebas (esperado: 21 passed)"
"${RUN[@]}" -m pytest -q

echo "==> 3/6. Lint (esperado: All checks passed!)"
"${RUN[@]}" -m ruff check .

echo "==> 4/6. Notebooks"
"${RUN[@]}" -m jupyter nbconvert --to notebook --execute --inplace \
  --ExecutePreprocessor.timeout=3600 notebooks/00_verificacion.ipynb
"${RUN[@]}" -m jupyter nbconvert --to notebook --execute --inplace \
  --ExecutePreprocessor.timeout=3600 notebooks/01_svm_guiada.ipynb
"${RUN[@]}" -m jupyter nbconvert --to notebook --execute --inplace \
  --ExecutePreprocessor.timeout=3600 notebooks/02_dataset_svm.ipynb
if [ "${SKIP_EJ02:-0}" != "1" ]; then
  echo "    (LAB03: 8 modelos x 3 repeticiones; 10-15 min en CPU)"
  "${RUN[@]}" -m jupyter nbconvert --to notebook --execute --inplace \
    --ExecutePreprocessor.timeout=3600 notebooks/03_ensembles_green_ai.ipynb
else
  echo "    OMITIDO por SKIP_EJ02=1"
fi

echo "==> 5/6. Documentación y PDF breves de entrega"
REPO_URL="$REPO_URL_E01" "${RUN[@]}" python scripts/build_ejercicio01_pdf.py
REPO_URL="$REPO_URL_E02" "${RUN[@]}" python scripts/generar_conclusion.py
REPO_URL="$REPO_URL_E02" "${RUN[@]}" python scripts/build_ejercicio02_pdf.py

echo "==> 6/6. Verificación de las cifras publicadas contra reports/"
"${RUN[@]}" python scripts/verify_cifras.py

echo "==> Resumen de cifras generadas"
"${RUN[@]}" - <<'CODE'
import json
from pathlib import Path

reports = Path("reports")
svm = json.loads((reports / "svm_metrics.json").read_text())
adult = json.loads((reports / "dataset_svm_metrics.json").read_text())
decision = json.loads((reports / "green_ai_decision.json").read_text())
print(f"LAB01  accuracy={svm['accuracy']:.4f}  f1_macro={svm['f1_macro']:.4f}  recall_maligno={svm['recall_maligno']:.4f}")
print(f"LAB02  accuracy={adult['accuracy']:.4f}  f1_macro={adult['f1_macro']:.4f}  recall_mas_50k={adult['recall_mas_50k']:.4f}")
print(f"LAB03  elegida={decision['configuracion_elegida']}  f1_macro={decision['f1_macro_elegida']:.4f}  "
      f"tiempo={decision['tiempo_elegida_s']:.2f}s  tamano={decision['tamano_elegida_kb']:.0f}KB")
print("Estas cifras son las que publican README, conclusión, notebook y PDF (verificado en el paso anterior).")
CODE

echo "Listo. Revisa 'git status' antes de publicar."
