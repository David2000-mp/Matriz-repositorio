"""
Paquete de vistas para CHAMPILYTICS.
"""

# Importar explícitamente los submódulos para que `from views import X` funcione
from . import landing
from . import dashboard
from . import analytics
from . import data_entry
from . import settings
from . import changelog

__all__ = [
	"landing",
	"dashboard",
	"analytics",
	"data_entry",
	"settings",
	"changelog",
]
