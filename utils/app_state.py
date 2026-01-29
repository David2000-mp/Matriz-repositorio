"""
AppState - Sistema Centralizado de Estado para CHAMPILEAKS
Sprint 2 - Semana 3: Arquitectura de Estado

Gestiona todo el estado de sesión de manera centralizada y type-safe.
Reemplaza acceso directo a st.session_state con una API consistente.

Uso:
    from utils.app_state import get_app_state
    
    state = get_app_state()
    state.set_filter_entity("Universidad A")
    entity = state.get_filter_entity()
"""

import streamlit as st
from dataclasses import dataclass, field
from typing import Optional, Any, Dict, List
from datetime import date, datetime
from utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class FilterState:
    """Estado de filtros globales"""
    entidad: Optional[str] = "Todas"
    mes: Optional[str] = "Todos"
    plataforma: Optional[str] = "Todas"
    fecha_inicio: Optional[date] = None
    fecha_fin: Optional[date] = None
    
    # Filtros de comparación
    entidad_comparacion: Optional[str] = None
    plataforma_comparacion: Optional[str] = None


@dataclass
class NavigationState:
    """Estado de navegación"""
    page: str = "Inicio"
    previous_page: Optional[str] = None


@dataclass
class FormState:
    """Estado de formularios (persistencia entre envíos)"""
    capture_entidad_default: Optional[str] = None
    capture_fecha_default: Optional[date] = None
    capture_plataforma_default: Optional[str] = None


@dataclass
class PaginationState:
    """Estado de paginación de tablas"""
    pages: Dict[str, int] = field(default_factory=dict)
    
    def get_page(self, key: str) -> int:
        """Obtiene número de página para una tabla específica"""
        return self.pages.get(key, 0)
    
    def set_page(self, key: str, page: int):
        """Establece número de página"""
        self.pages[key] = max(0, page)


@dataclass
class DataCacheState:
    """Estado de datos cacheados"""
    app_data: Optional[Any] = None
    global_entities: List[str] = field(default_factory=list)
    global_months: List[str] = field(default_factory=list)
    last_refresh: Optional[datetime] = None


class AppState:
    """
    Sistema centralizado de gestión de estado de la aplicación.
    
    Proporciona acceso type-safe a st.session_state con valores por defecto
    y validación automática. Mantiene compatibilidad con acceso directo
    a st.session_state durante migración.
    
    Attributes:
        filters: Estado de filtros globales y comparación
        navigation: Estado de navegación entre páginas
        forms: Estado de formularios para persistencia
        pagination: Estado de paginación de tablas
        data_cache: Estado de datos cacheados
    """
    
    # Claves de session_state (compatibilidad backward)
    _FILTER_ENTIDAD = "filtro_entidad"
    _FILTER_MES = "filtro_mes"
    _FILTER_PLATAFORMA = "filtro_plataforma"
    _NAV_PAGE = "page"
    _NAV_PAGE_SELECTION = "page_selection"
    
    def __init__(self):
        """Inicializa AppState y sincroniza con st.session_state existente"""
        self._ensure_initialized()
    
    def _ensure_initialized(self):
        """Asegura que todos los estados base estén inicializados"""
        if "_app_state_initialized" not in st.session_state:
            logger.debug("Inicializando AppState por primera vez")
            
            # Inicializar estados base
            st.session_state["_filters"] = FilterState()
            st.session_state["_navigation"] = NavigationState()
            st.session_state["_forms"] = FormState()
            st.session_state["_pagination"] = PaginationState()
            st.session_state["_data_cache"] = DataCacheState()
            
            st.session_state["_app_state_initialized"] = True
            
            # Migrar datos existentes si los hay
            self._migrate_legacy_state()
    
    def _migrate_legacy_state(self):
        """Migra datos de st.session_state legacy a nueva estructura"""
        try:
            # Migrar filtros
            if self._FILTER_ENTIDAD in st.session_state:
                self.filters.entidad = st.session_state[self._FILTER_ENTIDAD]
            if self._FILTER_MES in st.session_state:
                self.filters.mes = st.session_state[self._FILTER_MES]
            
            # Migrar navegación
            if self._NAV_PAGE in st.session_state:
                self.navigation.page = st.session_state[self._NAV_PAGE]
            
            # Migrar formularios
            if "capture_entidad_default" in st.session_state:
                self.forms.capture_entidad_default = st.session_state["capture_entidad_default"]
            if "capture_fecha_default" in st.session_state:
                self.forms.capture_fecha_default = st.session_state["capture_fecha_default"]
            if "capture_plataforma_default" in st.session_state:
                self.forms.capture_plataforma_default = st.session_state["capture_plataforma_default"]
            
            logger.debug("Migración de estado legacy completada")
        except Exception as e:
            logger.warning(f"Error en migración de estado legacy: {e}")
    
    # ============================================
    # PROPERTIES - Acceso a estados
    # ============================================
    
    @property
    def filters(self) -> FilterState:
        """Acceso al estado de filtros"""
        return st.session_state.get("_filters", FilterState())
    
    @property
    def navigation(self) -> NavigationState:
        """Acceso al estado de navegación"""
        return st.session_state.get("_navigation", NavigationState())
    
    @property
    def forms(self) -> FormState:
        """Acceso al estado de formularios"""
        return st.session_state.get("_forms", FormState())
    
    @property
    def pagination(self) -> PaginationState:
        """Acceso al estado de paginación"""
        return st.session_state.get("_pagination", PaginationState())
    
    @property
    def data_cache(self) -> DataCacheState:
        """Acceso al estado de caché de datos"""
        return st.session_state.get("_data_cache", DataCacheState())
    
    # ============================================
    # FILTROS - API de alto nivel
    # ============================================
    
    def get_filter_entity(self) -> str:
        """Obtiene filtro de entidad actual"""
        return self.filters.entidad or "Todas"
    
    def set_filter_entity(self, entity: str):
        """Establece filtro de entidad"""
        self.filters.entidad = entity
        # Mantener compatibilidad con código legacy
        st.session_state[self._FILTER_ENTIDAD] = entity
        logger.debug(f"Filtro de entidad actualizado: {entity}")
    
    def get_filter_month(self) -> str:
        """Obtiene filtro de mes actual"""
        return self.filters.mes or "Todos"
    
    def set_filter_month(self, month: str):
        """Establece filtro de mes"""
        self.filters.mes = month
        st.session_state[self._FILTER_MES] = month
        logger.debug(f"Filtro de mes actualizado: {month}")
    
    def get_filter_platform(self) -> str:
        """Obtiene filtro de plataforma actual"""
        return self.filters.plataforma or "Todas"
    
    def set_filter_platform(self, platform: str):
        """Establece filtro de plataforma"""
        self.filters.plataforma = platform
        logger.debug(f"Filtro de plataforma actualizado: {platform}")
    
    def get_date_range(self) -> tuple[Optional[date], Optional[date]]:
        """Obtiene rango de fechas de filtro"""
        return (self.filters.fecha_inicio, self.filters.fecha_fin)
    
    def set_date_range(self, start: Optional[date], end: Optional[date]):
        """Establece rango de fechas de filtro"""
        self.filters.fecha_inicio = start
        self.filters.fecha_fin = end
        logger.debug(f"Rango de fechas actualizado: {start} - {end}")
    
    def reset_filters(self):
        """Resetea todos los filtros a valores por defecto"""
        self.filters.entidad = "Todas"
        self.filters.mes = "Todos"
        self.filters.plataforma = "Todas"
        self.filters.fecha_inicio = None
        self.filters.fecha_fin = None
        self.filters.entidad_comparacion = None
        self.filters.plataforma_comparacion = None
        
        # Limpiar session_state legacy
        if self._FILTER_ENTIDAD in st.session_state:
            st.session_state[self._FILTER_ENTIDAD] = "Todas"
        if self._FILTER_MES in st.session_state:
            st.session_state[self._FILTER_MES] = "Todos"
        
        logger.info("Filtros reseteados")
    
    # ============================================
    # COMPARACIÓN - Filtros lado a lado
    # ============================================
    
    def get_comparison_entity(self) -> Optional[str]:
        """Obtiene entidad de comparación"""
        return self.filters.entidad_comparacion
    
    def set_comparison_entity(self, entity: str):
        """Establece entidad de comparación"""
        self.filters.entidad_comparacion = entity
        logger.debug(f"Entidad de comparación actualizada: {entity}")
    
    def get_comparison_platform(self) -> Optional[str]:
        """Obtiene plataforma de comparación"""
        return self.filters.plataforma_comparacion
    
    def set_comparison_platform(self, platform: str):
        """Establece plataforma de comparación"""
        self.filters.plataforma_comparacion = platform
        logger.debug(f"Plataforma de comparación actualizada: {platform}")
    
    def is_comparison_active(self) -> bool:
        """Verifica si hay una comparación activa"""
        return (
            self.filters.entidad_comparacion is not None or
            self.filters.plataforma_comparacion is not None
        )
    
    # ============================================
    # NAVEGACIÓN
    # ============================================
    
    def get_current_page(self) -> str:
        """Obtiene página actual"""
        # Priorizar page_selection sobre page
        if self._NAV_PAGE_SELECTION in st.session_state:
            return st.session_state[self._NAV_PAGE_SELECTION]
        return self.navigation.page
    
    def set_current_page(self, page: str):
        """Establece página actual"""
        self.navigation.previous_page = self.navigation.page
        self.navigation.page = page
        
        # Mantener compatibilidad
        st.session_state[self._NAV_PAGE] = page
        if self._NAV_PAGE_SELECTION in st.session_state:
            st.session_state[self._NAV_PAGE_SELECTION] = page
        
        logger.debug(f"Navegación: {self.navigation.previous_page} → {page}")
    
    def get_previous_page(self) -> Optional[str]:
        """Obtiene página anterior"""
        return self.navigation.previous_page
    
    # ============================================
    # FORMULARIOS
    # ============================================
    
    def get_form_defaults(self) -> dict:
        """Obtiene valores por defecto de formularios"""
        return {
            "entidad": self.forms.capture_entidad_default,
            "fecha": self.forms.capture_fecha_default or date.today(),
            "plataforma": self.forms.capture_plataforma_default,
        }
    
    def set_form_defaults(self, entidad: Optional[str] = None, 
                         fecha: Optional[date] = None,
                         plataforma: Optional[str] = None):
        """Establece valores por defecto de formularios"""
        if entidad is not None:
            self.forms.capture_entidad_default = entidad
            st.session_state["capture_entidad_default"] = entidad
        if fecha is not None:
            self.forms.capture_fecha_default = fecha
            st.session_state["capture_fecha_default"] = fecha
        if plataforma is not None:
            self.forms.capture_plataforma_default = plataforma
            st.session_state["capture_plataforma_default"] = plataforma
        
        logger.debug("Defaults de formulario actualizados")
    
    # ============================================
    # PAGINACIÓN
    # ============================================
    
    def get_table_page(self, table_key: str) -> int:
        """Obtiene número de página de una tabla"""
        # Compatibilidad con keys legacy
        if table_key in st.session_state:
            return st.session_state[table_key]
        return self.pagination.get_page(table_key)
    
    def set_table_page(self, table_key: str, page: int):
        """Establece número de página de una tabla"""
        self.pagination.set_page(table_key, page)
        st.session_state[table_key] = page
    
    # ============================================
    # CACHÉ DE DATOS
    # ============================================
    
    def get_cached_data(self) -> Optional[Any]:
        """Obtiene datos cacheados"""
        return self.data_cache.app_data
    
    def set_cached_data(self, data: Any):
        """Establece datos cacheados"""
        self.data_cache.app_data = data
        self.data_cache.last_refresh = datetime.now()
        st.session_state["app_data"] = data
    
    def get_available_entities(self) -> List[str]:
        """Obtiene lista de entidades disponibles"""
        if self.data_cache.global_entities:
            return self.data_cache.global_entities
        return st.session_state.get("global_entities", [])
    
    def set_available_entities(self, entities: List[str]):
        """Establece lista de entidades disponibles"""
        self.data_cache.global_entities = entities
        st.session_state["global_entities"] = entities
    
    def get_available_months(self) -> List[str]:
        """Obtiene lista de meses disponibles"""
        if self.data_cache.global_months:
            return self.data_cache.global_months
        return st.session_state.get("global_months", [])
    
    def set_available_months(self, months: List[str]):
        """Establece lista de meses disponibles"""
        self.data_cache.global_months = months
        st.session_state["global_months"] = months
    
    # ============================================
    # UTILIDADES
    # ============================================
    
    def clear_all(self):
        """Limpia todo el estado (útil para logout o reset completo)"""
        logger.warning("Limpiando todo el estado de la aplicación")
        
        # Limpiar estados internos
        st.session_state["_filters"] = FilterState()
        st.session_state["_navigation"] = NavigationState()
        st.session_state["_forms"] = FormState()
        st.session_state["_pagination"] = PaginationState()
        st.session_state["_data_cache"] = DataCacheState()
        
        # Limpiar session_state legacy selectivamente
        keys_to_clear = [
            self._FILTER_ENTIDAD, self._FILTER_MES,
            "capture_entidad_default", "capture_fecha_default",
            "capture_plataforma_default", "app_data"
        ]
        for key in keys_to_clear:
            if key in st.session_state:
                del st.session_state[key]
    
    def to_dict(self) -> dict:
        """Exporta el estado completo como diccionario (para debugging)"""
        return {
            "filters": {
                "entidad": self.filters.entidad,
                "mes": self.filters.mes,
                "plataforma": self.filters.plataforma,
                "fecha_inicio": str(self.filters.fecha_inicio) if self.filters.fecha_inicio else None,
                "fecha_fin": str(self.filters.fecha_fin) if self.filters.fecha_fin else None,
                "entidad_comparacion": self.filters.entidad_comparacion,
                "plataforma_comparacion": self.filters.plataforma_comparacion,
            },
            "navigation": {
                "page": self.navigation.page,
                "previous_page": self.navigation.previous_page,
            },
            "forms": {
                "entidad_default": self.forms.capture_entidad_default,
                "fecha_default": str(self.forms.capture_fecha_default) if self.forms.capture_fecha_default else None,
                "plataforma_default": self.forms.capture_plataforma_default,
            },
            "pagination": {
                "pages": self.pagination.pages,
            },
            "cache": {
                "has_data": self.data_cache.app_data is not None,
                "entities_count": len(self.data_cache.global_entities),
                "months_count": len(self.data_cache.global_months),
                "last_refresh": str(self.data_cache.last_refresh) if self.data_cache.last_refresh else None,
            }
        }


# ============================================
# INSTANCIA GLOBAL (Singleton pattern)
# ============================================

def get_app_state() -> AppState:
    """
    Obtiene instancia global de AppState.
    
    Uso recomendado:
        from utils.app_state import get_app_state
        
        state = get_app_state()
        state.set_filter_entity("Universidad A")
    """
    return AppState()
