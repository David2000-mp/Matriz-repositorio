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
from . import demographic_geographic_analysis
from . import cross_intelligence_view
from . import statistical_registry_dashboard
from . import audience_risk_view

__all__ = [
	"landing",
	"dashboard",
	"analytics",
	"data_entry",
	"settings",
	"changelog",
	"new_data_dashboard",
	"text_analysis_dashboard",
	"demographic_geographic_analysis",
	"cross_intelligence_view",
	"statistical_registry_dashboard",
	"audience_risk_view",
]
