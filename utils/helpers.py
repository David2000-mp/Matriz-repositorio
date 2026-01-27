"""
Módulo de utilidades generales para CHAMPILEAKS.
Incluye funciones para manejo de imágenes, generación de reportes y simulación de datos.
"""

import pandas as pd
import base64
import random
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import logging

# Intentar obtener colores institucionales desde components
try:
    from components import COLOR_PRIMARY, COLOR_MAP
except Exception:
    COLOR_PRIMARY = "#003696"
    COLOR_MAP = {
        "Facebook": "#1877F2",
        "Instagram": "#E1306C",
        "TikTok": "#000000",
    }

# Configuración de directorio base
BASE_DIR = Path(__file__).parent.parent
IMAGES_DIR = BASE_DIR / "images"

# ===========================
# FUNCIONES DE IMÁGENES
# ===========================


def get_image_base64(image_path: Path) -> str:
    """
    Convierte una imagen a base64 para embeber en HTML/CSS.

    Args:
        image_path: Ruta al archivo de imagen

    Returns:
        String en formato base64
    """
    try:
        with open(image_path, "rb") as f:
            data = f.read()
        return base64.b64encode(data).decode()
    except Exception as e:
        logging.error(f"Error al codificar imagen {image_path}: {e}")
        return ""


def load_image(filename: str) -> Optional[str]:
    """
    Carga una imagen desde el directorio images/ y la convierte a base64.

    Args:
        filename: Nombre del archivo (ej: 'logo.png')

    Returns:
        String base64 o None si no existe
    """
    image_path = IMAGES_DIR / filename
    if image_path.exists():
        return get_image_base64(image_path)
    else:
        logging.warning(f"Imagen no encontrada: {image_path}")
        return None


def get_banner_css(image_filename: str, height: str = "200px") -> str:
    """
    Genera CSS para un banner con imagen de fondo.

    Args:
        image_filename: Nombre del archivo de imagen
        height: Altura del banner (CSS)

    Returns:
        String con CSS para el banner
    """
    img_b64 = load_image(image_filename)
    if img_b64:
        return f"""
        background-image: url(data:image/png;base64,{img_b64});
        background-size: cover;
        background-position: center;
        height: {height};
        border-radius: 10px;
        margin-bottom: 20px;
        """
    return ""


# ===========================
# SIMULACIÓN DE DATOS
# ===========================


def simular(
    n: int = 100,
    colegios_maristas: Dict[str, Dict[str, str]] = None,
    generar_metas: bool = True,
    months: int = 12,
) -> tuple:
    """
    Genera datos sintéticos para testing.
    Integrado con nuevo flujo de guardar_datos() que auto-inserta cuentas faltantes.

    Args:
        n: Número de registros a generar
        colegios_maristas: Diccionario de instituciones y sus redes
        generar_metas: Si True, también genera metas aleatorias para cada institución
        months: Número de meses históricos a generar

    Returns:
        Tupla (datos, metas) donde:
        - datos: DataFrame con métricas simuladas (para pruebas)
        - metas: Lista de diccionarios con metas por institución (vacía si generar_metas=False)
    """
    if colegios_maristas is None:
        from .data_manager import COLEGIOS_MARISTAS
        colegios_maristas = COLEGIOS_MARISTAS

    # Importar funciones necesarias para generación
    from .data_saver import get_id, guardar_datos
    from .data_manager import load_data

    # Cache de cuentas existentes para evitar duplicados
    cuentas_cache, _ = load_data()

    # ========================================================================
    # GENERAR CUENTAS A PARTIR DEL CATÁLOGO COLEGIOS_MARISTAS
    # ========================================================================
    cuentas = []
    for entidad, redes in colegios_maristas.items():
        for plataforma, usuario in redes.items():
            # Generar ID único para esta cuenta (determinístico)
            id_cuenta = get_id(entidad, plataforma, usuario, df_cuentas_cache=cuentas_cache)
            cuentas.append({
                "id_cuenta": id_cuenta,
                "entidad": entidad,
                "plataforma": plataforma,
                "usuario_red": usuario,
            })

    logging.info(f"Catálogo: {len(cuentas)} cuentas únicas generadas para {len(colegios_maristas)} instituciones")

    # ========================================================================
    # GENERAR SERIE HISTÓRICA DE MÉTRICAS
    # ========================================================================
    # Generar serie de fechas (inicio de mes) hacia atrás
    end = datetime.now().replace(day=1)
    months_list = []
    for m in range(months - 1, -1, -1):
        month_dt = (end - pd.DateOffset(months=m)).to_pydatetime()
        months_list.append(month_dt)

    data: List[Dict] = []

    # Para cada cuenta, generar serie histórica con crecimiento realista
    for c in cuentas:
        seguidores_prev = random.randint(1000, 10000)
        
        for month_dt in months_list:
            # Crecimiento mensual entre -1% y +5% (más realista para redes educativas)
            growth = random.uniform(-0.01, 0.05)
            seguidores_actual = max(0, int(round(seguidores_prev * (1 + growth))))

            # Engagement rate entre 0.5% y 4%
            engagement_rate = random.uniform(0.005, 0.04)
            interacciones = int(round(seguidores_actual * engagement_rate))

            # Alcance proporcional
            alcance = int(round(seguidores_actual * random.uniform(0.1, 0.5)))

            # Likes promedio como fracción de interacciones
            likes_promedio = int(round(interacciones * random.uniform(0.6, 0.9)))

            # Añadir registro de métrica
            data.append({
                "id_cuenta": c["id_cuenta"],
                "entidad": c["entidad"],
                "plataforma": c["plataforma"],
                "usuario_red": c["usuario_red"],
                "fecha": month_dt,
                "seguidores": seguidores_actual,
                "alcance": alcance,
                "interacciones": interacciones,
                "likes_promedio": likes_promedio,
                "engagement_rate": round(engagement_rate * 100, 2),
            })

            seguidores_prev = seguidores_actual

    logging.info(f"Simulación generada: {len(data)} registros de métricas")

    # ========================================================================
    # GUARDAR DATOS USANDO NUEVO FLUJO CON AUTO-UPSERT
    # ========================================================================
    df_datos = pd.DataFrame(data)
    
    # Asegurar que los tipos de datos sean correctos antes de guardar
    df_datos['fecha'] = pd.to_datetime(df_datos['fecha'], errors='coerce')
    df_datos['seguidores'] = pd.to_numeric(df_datos['seguidores'], errors='coerce').fillna(0).astype(int)
    df_datos['alcance'] = pd.to_numeric(df_datos['alcance'], errors='coerce').fillna(0).astype(int)
    df_datos['interacciones'] = pd.to_numeric(df_datos['interacciones'], errors='coerce').fillna(0).astype(int)
    df_datos['likes_promedio'] = pd.to_numeric(df_datos['likes_promedio'], errors='coerce').fillna(0).astype(int)
    df_datos['engagement_rate'] = pd.to_numeric(df_datos['engagement_rate'], errors='coerce').fillna(0.0)
    
    # Guardar usando nuevo flujo (auto-upsert + blindaje de columnas)
    guardar_datos(df_datos, modo="append")
    logging.info(f"Datos guardados en Google Sheets mediante guardar_datos() con auto-upsert")

    # ========================================================================
    # GENERAR METAS SI SE SOLICITA
    # ========================================================================
    metas = []
    if generar_metas:
        entidades_unicas = list(set(d["entidad"] for d in data))
        for entidad in entidades_unicas:
            # Calcular seguidores promedio de esta institución
            seguidores_entidad = [
                d["seguidores"] for d in data if d["entidad"] == entidad
            ]
            promedio_seguidores = (
                sum(seguidores_entidad) // len(seguidores_entidad)
                if seguidores_entidad
                else 10000
            )

            # Meta entre 110% y 150% del promedio actual
            meta_seguidores = int(promedio_seguidores * random.uniform(1.1, 1.5))

            # Meta de engagement entre 3% y 8% (valores realistas)
            meta_engagement = round(random.uniform(3.0, 8.0), 2)

            metas.append({
                "entidad": entidad,
                "meta_seguidores": meta_seguidores,
                "meta_engagement": meta_engagement,
            })

        logging.info(
            f"Metas generadas: {len(metas)} instituciones con objetivos personalizados"
        )

    # Return both datos y metas
    return df_datos, metas


# ===========================
# GENERACIÓN DE REPORTES
# ===========================


def generar_reporte_html(df: pd.DataFrame, titulo: str = "Reporte de Métricas") -> str:
    """
    Genera un reporte HTML descargable con análisis de métricas.

    Args:
        df: DataFrame con las métricas
        titulo: Título del reporte

    Returns:
        String con HTML completo
    """
    if df.empty:
        return "<html><body><h1>No hay datos para el reporte</h1></body></html>"

    # Preparar estadísticas
    total_cuentas = df["id_cuenta"].nunique() if "id_cuenta" in df.columns else 0
    total_registros = len(df)

    fecha_min = (
        df["fecha"].min().strftime("%Y-%m-%d") if "fecha" in df.columns else "N/A"
    )
    fecha_max = (
        df["fecha"].max().strftime("%Y-%m-%d") if "fecha" in df.columns else "N/A"
    )

    # Estadísticas por métrica
    stats_html = ""
    metricas_numericas = [
        "seguidores",
        "alcance",
        "interacciones",
        "likes_promedio",
        "engagement_rate",
    ]

    for metrica in metricas_numericas:
        if metrica in df.columns:
            promedio = df[metrica].mean()
            maximo = df[metrica].max()
            minimo = df[metrica].min()
            stats_html += f"""
            <tr>
                <td><strong>{metrica.replace("_", " ").title()}</strong></td>
                <td>{promedio:,.2f}</td>
                <td>{maximo:,.2f}</td>
                <td>{minimo:,.2f}</td>
            </tr>
            """

    # Tabla de datos
    tabla_datos = df.to_html(index=False, classes="table table-striped", border=0)

    # Intentar incluir logo si existe en IMAGES_DIR
    logo_b64 = None
    for name in ("logo_maristas.png", "logo.png", "logo_maristas.jpg", "logo.png"):
        logo_b64 = load_image(name)
        if logo_b64:
            break

    # HTML completo
    logo_html = ""
    if logo_b64:
        logo_html = f"<img src=\"data:image/png;base64,{logo_b64}\" alt=\"Logo\" style=\"height:60px; margin-right:16px; vertical-align:middle;\">"
    else:
        # SVG placeholder usando colores institucionales para evitar reporte roto
        accent = list(COLOR_MAP.values())[0] if COLOR_MAP else "#1877F2"
        svg = f'''<svg width="140" height="60" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Logo ChampiLeaks">
            <defs>
                <linearGradient id="g" x1="0" x2="1">
                    <stop stop-color="{COLOR_PRIMARY}" offset="0"/>
                    <stop stop-color="{accent}" offset="1"/>
                </linearGradient>
            </defs>
            <rect rx="8" width="140" height="60" fill="url(#g)" />
            <text x="16" y="38" font-family="Montserrat, Arial, sans-serif" font-size="20" fill="#ffffff" font-weight="700">CHAMPILEAKS</text>
        </svg>'''
        logo_html = svg

    html = f"""
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <title>{titulo}</title>
        <style>
            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                margin: 40px;
                background-color: #f5f5f5;
            }}
            .header {{
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 30px;
                border-radius: 10px;
                margin-bottom: 30px;
            }}
            h1 {{
                margin: 0;
                font-size: 28px;
            }}
            .stats {{
                background: white;
                padding: 20px;
                border-radius: 8px;
                margin-bottom: 20px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }}
            table {{
                width: 100%;
                border-collapse: collapse;
                background: white;
                border-radius: 8px;
                overflow: hidden;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }}
            th {{
                background-color: #667eea;
                color: white;
                padding: 12px;
                text-align: left;
            }}
            td {{
                padding: 10px;
                border-bottom: 1px solid #eee;
            }}
            tr:hover {{
                background-color: #f8f9fa;
            }}
            .footer {{
                margin-top: 30px;
                text-align: center;
                color: #666;
                font-size: 12px;
            }}
        </style>
    </head>
    <body>
        <div class="header" style="display:flex; align-items:center; gap:12px;">
            {logo_html}
            <div>
                <h1>📊 {titulo}</h1>
                <p style="margin:0;">Generado el {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
            </div>
        </div>
        
        <div class="stats">
            <h2>Resumen General</h2>
            <p><strong>Total de cuentas:</strong> {total_cuentas}</p>
            <p><strong>Total de registros:</strong> {total_registros}</p>
            <p><strong>Período:</strong> {fecha_min} a {fecha_max}</p>
            
            <h3>Estadísticas por Métrica</h3>
            <table>
                <thead>
                    <tr>
                        <th>Métrica</th>
                        <th>Promedio</th>
                        <th>Máximo</th>
                        <th>Mínimo</th>
                    </tr>
                </thead>
                <tbody>
                    {stats_html}
                </tbody>
            </table>
        </div>
        
        <div class="stats">
            <h2>Datos Completos</h2>
            {tabla_datos}
        </div>
        
        <div class="footer">
            <p>CHAMPILEAKS - Matriz de Redes Sociales Maristas</p>
        </div>
    </body>
    </html>
    """

    return html


def generate_social_url(platform, username_or_url):
    """
    Generate or return social media URLs.
    
    If username_or_url already starts with 'http', return it directly.
    Otherwise, construct the URL based on platform.

    Args:
        platform: The social media platform (e.g., 'Facebook', 'Instagram', 'TikTok')
        username_or_url: Username handle or full URL for the account

    Returns:
        The full URL string or None if platform is not supported
    """
    # If already a URL, return it directly (literal mode)
    if isinstance(username_or_url, str) and username_or_url.startswith('http'):
        return username_or_url
    
    # Otherwise, construct URL from platform and username (legacy mode)
    platform_lower = platform.lower()
    if platform_lower == 'facebook':
        return f"https://www.facebook.com/{username_or_url}"
    elif platform_lower == 'instagram':
        return f"https://www.instagram.com/{username_or_url}"
    elif platform_lower == 'twitter':
        return f"https://twitter.com/{username_or_url}"
    elif platform_lower == 'tiktok':
        return f"https://www.tiktok.com/@{username_or_url}"
    else:
        return None
