"""
Backward-compatible launcher.

Este archivo queda como wrapper ligero que delega la ejecución a
`app_refactored.py`. Mantener aquí solo un aviso deprecatorio para orientar
al equipo a usar el entrypoint refactorizado.
"""
import warnings

warnings.warn("app.py está deprecado. Usa app_refactored.py como entrypoint principal.")

from app_refactored import main

if __name__ == "__main__":
    main()
