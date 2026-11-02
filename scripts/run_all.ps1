# Ejecuta todo el flujo de la Unidad 01 (Ejercicio 01 y Ejercicio 02) en Windows / PowerShell.
# Uso:
#   .\scripts\run_all.ps1              # todo (incluye el notebook lento del LAB03)
#   $env:SKIP_EJ02="1"; .\scripts\run_all.ps1   # omite notebooks\03_ensembles_green_ai.ipynb

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root
$env:PYTHONPATH = "src"

if (-not (Test-Path ".venv\Scripts\python.exe")) {
    Write-Error "No existe el entorno .venv. Créalo con:`n  python -m venv .venv`n  .venv\Scripts\Activate.ps1`n  python -m pip install -r requirements.txt -r requirements-dev.txt"
}

Write-Host "==> 1/5. Dataset (se descarga una vez; el notebook también lo hace solo)" -ForegroundColor Cyan
python -c "from inf8239_u01.data import download_dataset; print('adult:', download_dataset('adult', 'data/raw')); print('bank (candidato alterno):', download_dataset('bank', 'data/raw'))"

Write-Host "==> 2/5. Pruebas (esperado: 21 passed)" -ForegroundColor Cyan
python -m pytest -q

Write-Host "==> 3/5. Notebooks" -ForegroundColor Cyan
foreach ($nb in @("00_verificacion.ipynb", "01_svm_guiada.ipynb", "02_dataset_svm.ipynb")) {
    python -m jupyter nbconvert --to notebook --execute --inplace --ExecutePreprocessor.timeout=3600 "notebooks\$nb"
}
if ($env:SKIP_EJ02 -ne "1") {
    Write-Host "    (LAB03: 8 modelos x 3 repeticiones; 10-15 min en CPU)" -ForegroundColor DarkGray
    python -m jupyter nbconvert --to notebook --execute --inplace --ExecutePreprocessor.timeout=3600 "notebooks\03_ensembles_green_ai.ipynb"
} else {
    Write-Host "    OMITIDO por SKIP_EJ02=1" -ForegroundColor DarkGray
}

Write-Host "==> 4/5. PDF breves de entrega" -ForegroundColor Cyan
python scripts\build_ejercicio01_pdf.py
python scripts\build_ejercicio02_pdf.py

Write-Host "==> 5/5. Resumen de cifras generadas" -ForegroundColor Cyan
python -c @"
import json
from pathlib import Path
reports = Path('reports')
svm = json.loads((reports / 'svm_metrics.json').read_text())
adult = json.loads((reports / 'dataset_svm_metrics.json').read_text())
decision = json.loads((reports / 'green_ai_decision.json').read_text())
print(f'LAB01  accuracy={svm["accuracy"]:.4f}  f1_macro={svm["f1_macro"]:.4f}  recall_maligno={svm["recall_maligno"]:.4f}')
print(f'LAB02  accuracy={adult["accuracy"]:.4f}  f1_macro={adult["f1_macro"]:.4f}  recall_mas_50k={adult["recall_mas_50k"]:.4f}')
print(f'LAB03  elegida={decision["configuracion_elegida"]}  f1_macro={decision["f1_macro_elegida"]:.4f}  tiempo={decision["tiempo_elegida_s"]:.2f}s  tamano={decision["tamano_elegida_kb"]:.0f}KB')
print('Revisa que estas cifras coincidan con README, cards, conclusiones y PDF.')
"@

Write-Host "Listo. Revisa 'git status' y publica cuando hayas completado los campos PENDIENTE de los PDF." -ForegroundColor Green
