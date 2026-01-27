"""
Sistema de Logging Centralizado para Matriz de Redes Sociales.

Este módulo configura un sistema de logging robusto con:
- Logs de ERROR/CRITICAL en archivo oculto .app_errors.log
- Logs de INFO/DEBUG en consola
- Formato estructurado con timestamps y niveles
- Rotación automática de archivos para evitar crecimiento infinito

Uso:
    from utils.logger import get_logger

    logger = get_logger(__name__)
    logger.info("Operación exitosa")
    logger.error("Falló la conexión", exc_info=True)
"""

import logging
import sys
from pathlib import Path
from logging.handlers import RotatingFileHandler
from typing import Optional

# ===========================
# CONFIGURACIÓN GLOBAL
# ===========================

# Directorio base del proyecto
BASE_DIR = Path(__file__).parent.parent

# Archivo de errores (oculto en sistemas Unix/Linux con .)
ERROR_LOG_FILE = BASE_DIR / ".app_errors.log"

# Formato de logs
LOG_FORMAT = (
    "%(asctime)s | %(levelname)-8s | %(name)s | %(funcName)s:%(lineno)d | %(message)s"
)
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

# Configuración de rotación de archivos
# Máximo 5 MB por archivo, mantener 5 archivos históricos (total ~25 MB)
MAX_BYTES = 5 * 1024 * 1024  # 5 MB
BACKUP_COUNT = 5


# ===========================
# SINGLETON DEL LOGGER
# ===========================

_loggers_initialized = {}


def get_logger(name: str = "matriz_redes", level: int = logging.INFO) -> logging.Logger:
    """
    Obtiene o crea un logger configurado.

    Implementa patrón Singleton para evitar configuraciones duplicadas.
    Cada módulo que importe esta función obtendrá el mismo logger configurado.

    Args:
        name: Nombre del logger (generalmente __name__ del módulo que lo llama)
        level: Nivel mínimo de logging (default: INFO)

    Returns:
        Logger configurado con handlers de archivo y consola

    Ejemplo:
        >>> from utils.logger import get_logger
        >>> logger = get_logger(__name__)
        >>> logger.info("Aplicación iniciada")
        >>> logger.error("Error de conexión", exc_info=True)
    """

    # Si ya existe un logger configurado para este nombre, devolverlo
    if name in _loggers_initialized:
        return _loggers_initialized[name]

    # Crear nuevo logger
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Evitar propagación a root logger (evita duplicados)
    logger.propagate = False

    # Limpiar handlers existentes (por si se llama múltiples veces)
    if logger.hasHandlers():
        logger.handlers.clear()

    # ===========================
    # HANDLER 1: ARCHIVO DE ERRORES
    # ===========================
    # Solo guarda ERROR y CRITICAL

    try:
        # Crear directorio si no existe
        ERROR_LOG_FILE.parent.mkdir(parents=True, exist_ok=True)

        file_handler = RotatingFileHandler(
            ERROR_LOG_FILE,
            maxBytes=MAX_BYTES,
            backupCount=BACKUP_COUNT,
            encoding="utf-8",
        )
        file_handler.setLevel(logging.ERROR)  # Solo ERROR y CRITICAL

        # Formato detallado para archivos (incluye más contexto)
        file_formatter = logging.Formatter(fmt=LOG_FORMAT, datefmt=DATE_FORMAT)
        file_handler.setFormatter(file_formatter)

        logger.addHandler(file_handler)

    except Exception as e:
        # Si falla la creación del archivo (permisos, disco lleno, etc.)
        # No queremos que la app crashee, solo advertimos
        print(f"⚠️  WARNING: No se pudo crear archivo de logs: {e}", file=sys.stderr)

    # ===========================
    # HANDLER 2: CONSOLA
    # ===========================
    # Muestra INFO, WARNING, ERROR, CRITICAL
    # (DEBUG solo si se configura explícitamente)

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)  # INFO y superiores

    # Formato más limpio para consola
    console_formatter = logging.Formatter(
        fmt="%(levelname)-8s | %(name)s | %(message)s", datefmt=DATE_FORMAT
    )
    console_handler.setFormatter(console_formatter)

    logger.addHandler(console_handler)

    # Guardar en cache para no reconfigurar
    _loggers_initialized[name] = logger

    return logger


def set_production_mode() -> None:
    """
    Configura logging optimizado para producción (menos verboso).

    En producción (especialmente en la nube), reduce el logging a WARNING+
    para mejorar rendimiento y reducir costos de logs.
    """
    level = logging.WARNING  # Solo WARNING, ERROR, CRITICAL

    for logger in _loggers_initialized.values():
        logger.setLevel(level)

        # Actualizar nivel de console handler
        for handler in logger.handlers:
            if isinstance(handler, logging.StreamHandler) and not isinstance(
                handler, RotatingFileHandler
            ):
                handler.setLevel(level)

    # Log único de que se cambió a modo producción
    print("🔇 Logging configurado para producción (WARNING+)")


def set_debug_mode(enabled: bool = True) -> None:
    """
    Activa/desactiva modo DEBUG globalmente.

    En modo DEBUG, se muestran logs mucho más detallados en consola.
    Útil para desarrollo y troubleshooting.

    Args:
        enabled: True para activar DEBUG, False para volver a INFO

    Ejemplo:
        >>> from utils.logger import set_debug_mode
        >>> set_debug_mode(True)  # Activar modo DEBUG
        >>> # ... código con logs detallados ...
        >>> set_debug_mode(False)  # Volver a modo normal
    """
    level = logging.DEBUG if enabled else logging.INFO

    for logger in _loggers_initialized.values():
        logger.setLevel(level)

        # Actualizar nivel de console handler también
        for handler in logger.handlers:
            if isinstance(handler, logging.StreamHandler) and not isinstance(
                handler, RotatingFileHandler
            ):
                handler.setLevel(level)


def clear_error_log() -> bool:
    """
    Limpia el archivo de errores.

    Útil para testing o para hacer "reset" después de resolver problemas.

    Returns:
        True si se limpió exitosamente, False si hubo error

    Ejemplo:
        >>> from utils.logger import clear_error_log
        >>> clear_error_log()
        True
    """
    try:
        if ERROR_LOG_FILE.exists():
            ERROR_LOG_FILE.unlink()
            return True
        return True  # Si no existe, consideramos exitoso
    except Exception as e:
        print(f"⚠️  WARNING: No se pudo limpiar archivo de logs: {e}", file=sys.stderr)
        return False


def get_error_log_contents() -> Optional[str]:
    """
    Lee el contenido del archivo de errores.

    Útil para debugging o para mostrar errores recientes al usuario.

    Returns:
        Contenido del archivo como string, o None si no existe/no se puede leer

    Ejemplo:
        >>> from utils.logger import get_error_log_contents
        >>> errors = get_error_log_contents()
        >>> if errors:
        ...     print(f"Errores recientes:\\n{errors}")
    """
    try:
        if ERROR_LOG_FILE.exists():
            return ERROR_LOG_FILE.read_text(encoding="utf-8")
        return None
    except Exception as e:
        print(f"⚠️  WARNING: No se pudo leer archivo de logs: {e}", file=sys.stderr)
        return None


# ===========================
# CONFIGURACIÓN INICIAL
# ===========================

# Crear logger principal al importar el módulo
# Esto asegura que siempre haya un logger disponible
_main_logger = get_logger("matriz_redes")

# Log inicial para confirmar que el sistema de logging está activo
_main_logger.info("Sistema de logging inicializado correctamente")


# ===========================
# FUNCIONES DE UTILIDAD
# ===========================


def log_exception(logger: logging.Logger, message: str = "Excepción capturada") -> None:
    """
    Registra la excepción actual con traceback completo.

    Debe llamarse dentro de un bloque except.

    Args:
        logger: Logger a usar para registrar la excepción
        message: Mensaje descriptivo del contexto del error

    Ejemplo:
        >>> from utils.logger import get_logger, log_exception
        >>> logger = get_logger(__name__)
        >>>
        >>> try:
        ...     resultado = 10 / 0
        ... except Exception:
        ...     log_exception(logger, "Error en división")
    """
    logger.error(message, exc_info=True)


def log_function_call(logger: logging.Logger, func_name: str, **kwargs) -> None:
    """
    Registra la llamada a una función con sus argumentos.

    Útil para debugging de funciones críticas.

    Args:
        logger: Logger a usar
        func_name: Nombre de la función
        **kwargs: Argumentos de la función (se registran de forma segura)

    Ejemplo:
        >>> from utils.logger import get_logger, log_function_call
        >>> logger = get_logger(__name__)
        >>>
        >>> def guardar_datos(df, modo='completo'):
        ...     log_function_call(logger, "guardar_datos", modo=modo, rows=len(df))
        ...     # ... resto del código ...
    """
    # Sanitizar argumentos sensibles (no loguear credenciales)
    safe_kwargs = {}
    sensitive_keys = {"password", "token", "secret", "key", "credential"}

    for k, v in kwargs.items():
        if any(sensitive in k.lower() for sensitive in sensitive_keys):
            safe_kwargs[k] = "***REDACTED***"
        else:
            safe_kwargs[k] = v

    logger.debug(f"Llamada a {func_name}() con argumentos: {safe_kwargs}")


# ===========================
# EJEMPLO DE USO
# ===========================

if __name__ == "__main__":
    """
    Prueba del sistema de logging.
    Ejecutar: python -m utils.logger
    """

    # Crear logger de prueba
    test_logger = get_logger("test_module")

    # Diferentes niveles de logging
    test_logger.debug("Mensaje de DEBUG (solo visible si se activa modo debug)")
    test_logger.info("✅ Mensaje informativo")
    test_logger.warning("⚠️  Mensaje de advertencia")
    test_logger.error("❌ Mensaje de error")

    # Simular excepción
    try:
        resultado = 10 / 0
    except Exception:
        log_exception(test_logger, "Error intencional de prueba")

    # Verificar que se creó el archivo de errores
    print(f"\n📁 Archivo de errores creado en: {ERROR_LOG_FILE}")
    print(
        f"📊 Tamaño: {ERROR_LOG_FILE.stat().st_size if ERROR_LOG_FILE.exists() else 0} bytes"
    )

    # Mostrar contenido del archivo
    contenido = get_error_log_contents()
    if contenido:
        print(f"\n📄 Contenido del archivo de errores:\n{contenido}")
