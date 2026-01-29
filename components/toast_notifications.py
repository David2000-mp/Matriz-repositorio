"""
Toast Notifications - Sistema de Notificaciones Flotantes para CHAMPILEAKS
Sprint 2 - Semana 3: Sistema de Toasts

Wrapper unificado sobre st.toast para reemplazar st.success/error/warning/info
con notificaciones que desaparecen automáticamente.

Uso:
    from components.toast_notifications import show_toast, ToastType
    
    show_toast("Datos guardados correctamente", ToastType.SUCCESS)
    show_toast("Error al conectar", ToastType.ERROR, duration=5)
"""

import streamlit as st
from enum import Enum
from typing import Optional
from utils.logger import get_logger

logger = get_logger(__name__)


class ToastType(Enum):
    """Tipos de notificaciones toast"""
    SUCCESS = "success"
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


# Configuración de íconos por tipo
TOAST_ICONS = {
    ToastType.SUCCESS: "✅",
    ToastType.ERROR: "❌",
    ToastType.WARNING: "⚠️",
    ToastType.INFO: "ℹ️",
}

# Duración por defecto en segundos por tipo
TOAST_DURATIONS = {
    ToastType.SUCCESS: 3,
    ToastType.ERROR: 5,
    ToastType.WARNING: 4,
    ToastType.INFO: 3,
}


def show_toast(
    message: str,
    toast_type: ToastType = ToastType.INFO,
    duration: Optional[int] = None,
    icon: Optional[str] = None,
) -> None:
    """
    Muestra una notificación toast flotante que desaparece automáticamente.
    
    Reemplaza st.success/error/warning/info con una API unificada y
    notificaciones menos invasivas que desaparecen solas.
    
    Args:
        message: Texto de la notificación
        toast_type: Tipo de toast (SUCCESS, ERROR, WARNING, INFO)
        duration: Duración en segundos (None = usar duración por defecto del tipo)
        icon: Ícono personalizado (None = usar ícono del tipo)
    
    Examples:
        >>> show_toast("Datos guardados", ToastType.SUCCESS)
        >>> show_toast("Error de conexión", ToastType.ERROR, duration=10)
        >>> show_toast("Procesando...", ToastType.INFO, icon="⏳")
    """
    
    # Obtener duración según tipo si no se especifica
    if duration is None:
        duration = TOAST_DURATIONS.get(toast_type, 3)
    
    # Obtener ícono según tipo si no se especifica
    if icon is None:
        icon = TOAST_ICONS.get(toast_type, "")
    
    # Formatear mensaje con ícono
    formatted_message = f"{icon} {message}" if icon else message
    
    # Mostrar toast usando API de Streamlit
    try:
        st.toast(formatted_message, icon=icon or None)
        logger.debug(f"Toast mostrado: [{toast_type.value}] {message}")
    except Exception as e:
        # Fallback a st.write si st.toast falla
        logger.warning(f"Error al mostrar toast: {e}. Usando fallback.")
        _fallback_notification(message, toast_type)


def _fallback_notification(message: str, toast_type: ToastType):
    """
    Fallback a notificaciones estándar si st.toast no está disponible.
    
    Usado para compatibilidad con versiones antiguas de Streamlit o si
    st.toast presenta problemas.
    """
    icon = TOAST_ICONS.get(toast_type, "")
    formatted_message = f"{icon} {message}"
    
    if toast_type == ToastType.SUCCESS:
        st.success(formatted_message)
    elif toast_type == ToastType.ERROR:
        st.error(formatted_message)
    elif toast_type == ToastType.WARNING:
        st.warning(formatted_message)
    else:  # INFO
        st.info(formatted_message)


# ============================================
# HELPERS ESPECÍFICOS POR TIPO
# ============================================

def toast_success(message: str, duration: int = 3) -> None:
    """
    Muestra toast de éxito (verde).
    
    Args:
        message: Mensaje de éxito
        duration: Duración en segundos
    
    Example:
        >>> toast_success("¡Registro guardado exitosamente!")
    """
    show_toast(message, ToastType.SUCCESS, duration)


def toast_error(message: str, duration: int = 5) -> None:
    """
    Muestra toast de error (rojo).
    
    Args:
        message: Mensaje de error
        duration: Duración en segundos
    
    Example:
        >>> toast_error("No se pudo conectar a Google Sheets")
    """
    show_toast(message, ToastType.ERROR, duration)


def toast_warning(message: str, duration: int = 4) -> None:
    """
    Muestra toast de advertencia (amarillo).
    
    Args:
        message: Mensaje de advertencia
        duration: Duración en segundos
    
    Example:
        >>> toast_warning("Algunos datos podrían estar desactualizados")
    """
    show_toast(message, ToastType.WARNING, duration)


def toast_info(message: str, duration: int = 3) -> None:
    """
    Muestra toast informativo (azul).
    
    Args:
        message: Mensaje informativo
        duration: Duración en segundos
    
    Example:
        >>> toast_info("Cargando datos...")
    """
    show_toast(message, ToastType.INFO, duration)


# ============================================
# TOASTS ESPECIALIZADOS (Casos de Uso Comunes)
# ============================================

def toast_data_saved(entity_name: str = "Registro") -> None:
    """
    Toast especializado para confirmación de guardado de datos.
    
    Args:
        entity_name: Nombre de la entidad guardada
    
    Example:
        >>> toast_data_saved("Universidad A")
    """
    show_toast(f"¡{entity_name} guardado exitosamente!", ToastType.SUCCESS)


def toast_filter_applied(filter_description: str) -> None:
    """
    Toast especializado para confirmación de aplicación de filtro.
    
    Args:
        filter_description: Descripción del filtro aplicado
    
    Example:
        >>> toast_filter_applied("Filtrado por Instagram")
    """
    show_toast(f"Filtro aplicado: {filter_description}", ToastType.INFO, duration=2)


def toast_data_loading(message: str = "Cargando datos...") -> None:
    """
    Toast especializado para operaciones de carga.
    
    Args:
        message: Mensaje de carga personalizado
    
    Example:
        >>> toast_data_loading("Sincronizando con Google Sheets...")
    """
    show_toast(message, ToastType.INFO, icon="⏳", duration=2)


def toast_validation_error(field_name: str, error_message: str) -> None:
    """
    Toast especializado para errores de validación.
    
    Args:
        field_name: Nombre del campo con error
        error_message: Descripción del error
    
    Example:
        >>> toast_validation_error("URL", "Formato inválido para Instagram")
    """
    show_toast(f"{field_name}: {error_message}", ToastType.ERROR, duration=4)


def toast_operation_complete(operation_name: str, count: Optional[int] = None) -> None:
    """
    Toast especializado para completar operaciones masivas.
    
    Args:
        operation_name: Nombre de la operación
        count: Número de elementos procesados (opcional)
    
    Example:
        >>> toast_operation_complete("Generación de reportes", 150)
    """
    if count is not None:
        message = f"¡{operation_name} completado! ({count:,} elementos)"
    else:
        message = f"¡{operation_name} completado!"
    
    show_toast(message, ToastType.SUCCESS, duration=4)


def toast_connection_status(connected: bool, service_name: str = "Servicio") -> None:
    """
    Toast especializado para estado de conexión.
    
    Args:
        connected: True si conectado, False si desconectado
        service_name: Nombre del servicio
    
    Example:
        >>> toast_connection_status(True, "Google Sheets")
    """
    if connected:
        show_toast(f"✓ Conectado a {service_name}", ToastType.SUCCESS, duration=2)
    else:
        show_toast(f"✗ Desconectado de {service_name}", ToastType.ERROR, duration=5)


# ============================================
# TOASTS CON ACCIONES (Experimental)
# ============================================

def toast_with_undo(message: str, undo_callback=None) -> None:
    """
    Toast con opción de deshacer (experimental).
    
    Nota: Streamlit no soporta botones en toasts nativamente,
    esta función es un placeholder para futuras versiones.
    
    Args:
        message: Mensaje del toast
        undo_callback: Función a ejecutar si se deshace la acción
    
    Example:
        >>> def undo_delete():
        ...     restore_data()
        >>> toast_with_undo("Registro eliminado", undo_delete)
    """
    # Por ahora, solo mostrar el toast sin funcionalidad de undo
    show_toast(message, ToastType.WARNING, duration=5)
    logger.debug(f"Toast con undo solicitado (no implementado): {message}")
    
    # TODO: Implementar cuando Streamlit soporte botones en toasts
    # o usar componente personalizado


# ============================================
# UTILIDADES DE DEBUGGING
# ============================================

def toast_debug(message: str, show_in_production: bool = False) -> None:
    """
    Toast de debugging (solo en desarrollo).
    
    Args:
        message: Mensaje de debug
        show_in_production: Si True, muestra también en producción
    
    Example:
        >>> toast_debug("Estado actual: filtros activos")
    """
    # Solo mostrar en desarrollo o si se fuerza
    if show_in_production or _is_development_mode():
        show_toast(f"🐛 DEBUG: {message}", ToastType.INFO, duration=5)


def _is_development_mode() -> bool:
    """Detecta si la app está en modo desarrollo"""
    # Heurística simple: si hay parámetros de query o puerto no estándar
    try:
        import os
        return os.getenv("STREAMLIT_ENV", "production") == "development"
    except:
        return False


# ============================================
# BATCH TOASTS (Cola de notificaciones)
# ============================================

class ToastQueue:
    """
    Sistema de cola para mostrar múltiples toasts secuencialmente.
    
    Útil cuando hay múltiples operaciones que generan notificaciones
    para evitar overlap visual.
    
    Example:
        >>> queue = ToastQueue()
        >>> queue.add("Validando datos...", ToastType.INFO)
        >>> queue.add("Guardando en Google Sheets...", ToastType.INFO)
        >>> queue.add("¡Completado!", ToastType.SUCCESS)
        >>> queue.show_all()
    """
    
    def __init__(self):
        """Inicializa cola vacía"""
        self._queue = []
    
    def add(self, message: str, toast_type: ToastType = ToastType.INFO, 
            duration: Optional[int] = None, icon: Optional[str] = None):
        """
        Añade un toast a la cola.
        
        Args:
            message: Mensaje del toast
            toast_type: Tipo de toast
            duration: Duración personalizada
            icon: Ícono personalizado
        """
        self._queue.append({
            "message": message,
            "toast_type": toast_type,
            "duration": duration,
            "icon": icon,
        })
    
    def show_all(self, delay_between: float = 0):
        """
        Muestra todos los toasts en la cola secuencialmente.
        
        Args:
            delay_between: Retraso entre toasts (no implementado en Streamlit)
        """
        for toast_config in self._queue:
            show_toast(**toast_config)
        
        # Limpiar cola después de mostrar
        self._queue.clear()
    
    def clear(self):
        """Limpia la cola sin mostrar los toasts"""
        self._queue.clear()
    
    def count(self) -> int:
        """Retorna número de toasts en cola"""
        return len(self._queue)
