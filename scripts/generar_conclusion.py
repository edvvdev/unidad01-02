#!/usr/bin/env python3
"""Regenera la narrativa del LAB03 (README, conclusión y PDF) desde `reports/`.

Las cifras publicadas se derivan de `reports/green_ai_results.csv`,
`reports/green_ai_decision.json` y de los informes auxiliares que escribe el notebook del LAB03, de
modo que la documentación no pueda quedar desfasada respecto de la corrida real.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from inf8239_u01 import informe


def main() -> int:
    """Regenera los documentos y los bloques del README."""
    cifras = informe.cargar_cifras(ROOT / "reports")
    documentos = informe.actualizar_documentos(ROOT)
    for documento in documentos:
        print("Actualizado:", documento.relative_to(ROOT))
    valores = cifras.valores()
    print(
        f"LAB03 · {valores['elegida']} | F1 macro {informe.formatear(valores['f1_elegida'])} | "
        f"ajuste {informe.formatear(valores['tiempo_elegida_s'], 2)} s | "
        f"inferencia {informe.formatear(valores['inferencia_elegida_ms'], 1)} ms | "
        f"tamaño {informe.formatear(valores['tamano_elegida_kb'], 0)} KB"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
