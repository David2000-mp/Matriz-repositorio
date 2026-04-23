"""
Paquete de vistas para CHAMPILEAKS.
"""

# Importar explícitamente los submódulos para que `from views import X` funcione
from . import landing
from . import dashboard
from . import analytics
from . import data_entry
from . import settings
from . import changelog
from . import new_data_dashboard
from . import text_analysis_dashboard

__all__ = [
	"landing",
	"dashboard",
	"analytics",
	"data_entry",
	"settings",
	"changelog",
	"new_data_dashboard",
	"text_analysis_dashboard",
]
