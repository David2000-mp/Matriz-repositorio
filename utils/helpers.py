"""
Módulo de utilidades generales para CHAMPILYTICS.
Incluye funciones para manejo de imágenes, generación de reportes y simulación de datos.
"""

import pandas as pd
import base64
import random
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import logging

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
        <div style="
            background-image: url(data:image/png;base64,{img_b64});
            background-size: cover;
            background-position: center;
            height: {height};
            border-radius: 10px;
            margin-bottom: 20px;
        "></div>
        """
    return ""


# ===========================
# SIMULACIÓN DE DATOS
# ===========================

def simular(n: int = 100, colegios_maristas: Dict[str, Dict[str, str]] = None, generar_metas: bool = True) -> tuple:
    """
    Genera datos sintéticos para testing.
    
    Args:
        n: Número de registros a generar
        colegios_maristas: Diccionario de instituciones y sus redes
        generar_metas: Si True, también genera metas aleatorias para cada institución
        
    Returns:
        Tupla (datos, metas) donde:
        - datos: Lista de diccionarios con métricas simuladas
        - metas: Lista de diccionarios con metas por institución (vacía si generar_metas=False)
    """
    if colegios_maristas is None:
        from .data_manager import COLEGIOS_MARISTAS
        colegios_maristas = COLEGIOS_MARISTAS
    
    # Importar get_id para generar IDs válidos
    from .data_manager import get_id
    
    data: List[Dict] = []
    base = datetime.now() - timedelta(days=n)
    
    # Precargar cuentas para optimizar get_id
    from .data_manager import load_data
    cuentas_cache, _ = load_data()
    
    for i in range(n):
        entidad = random.choice(list(colegios_maristas.keys()))
        redes_disponibles = colegios_maristas[entidad]
        plataforma = random.choice(list(redes_disponibles.keys()))
        usuario = redes_disponibles[plataforma]
        
        # Generar ID válido (reutilizar IDs existentes si ya hay cuentas creadas)
        id_cuenta = get_id(entidad, plataforma, usuario, df_cuentas_cache=cuentas_cache)
        
        # Métricas simuladas con distribución realista
        seguidores = random.randint(500, 50000)
        alcance = int(seguidores * random.uniform(0.1, 0.5))  # 10-50% del alcance
        interacciones = int(alcance * random.uniform(0.02, 0.08))  # 2-8% de engagement
        likes_promedio = int(interacciones * random.uniform(0.6, 0.9))  # 60-90% likes del total
        engagement_rate = round((interacciones / seguidores * 100), 2) if seguidores > 0 else 0
        
        data.append({
            "id_cuenta": id_cuenta,
            "entidad": entidad,
            "plataforma": plataforma,
            "usuario_red": usuario,
            "fecha": base + timedelta(days=i),
            "seguidores": seguidores,
            "alcance": alcance,
            "interacciones": interacciones,
            "likes_promedio": likes_promedio,
            "engagement_rate": engagement_rate
        })
    
    logging.info(f"Simulación generada: {n} registros para {len(set(d['entidad'] for d in data))} entidades")
    
    # Generar metas aleatorias si se solicita
    metas = []
    if generar_metas:
        entidades_unicas = list(set(d['entidad'] for d in data))
        for entidad in entidades_unicas:
            # Calcular seguidores promedio de esta institución para generar meta realista
            seguidores_entidad = [d['seguidores'] for d in data if d['entidad'] == entidad]
            promedio_seguidores = sum(seguidores_entidad) // len(seguidores_entidad) if seguidores_entidad else 10000
            
            # Meta entre 110% y 150% del promedio actual
            meta_seguidores = int(promedio_seguidores * random.uniform(1.1, 1.5))
            
            # Meta de engagement entre 3% y 8% (valores realistas)
            meta_engagement = round(random.uniform(3.0, 8.0), 2)
            
            metas.append({
                "entidad": entidad,
                "meta_seguidores": meta_seguidores,
                "meta_engagement": meta_engagement
            })
        
        logging.info(f"Metas generadas: {len(metas)} instituciones con objetivos personalizados")
    
    return data, metas


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
    total_cuentas = df['id_cuenta'].nunique() if 'id_cuenta' in df.columns else 0
    total_registros = len(df)
    
    fecha_min = df['fecha'].min().strftime('%Y-%m-%d') if 'fecha' in df.columns else "N/A"
    fecha_max = df['fecha'].max().strftime('%Y-%m-%d') if 'fecha' in df.columns else "N/A"
    
    # Estadísticas por métrica
    stats_html = ""
    metricas_numericas = ['seguidores', 'alcance', 'interacciones', 'likes_promedio', 'engagement_rate']
    
    for metrica in metricas_numericas:
        if metrica in df.columns:
            promedio = df[metrica].mean()
            maximo = df[metrica].max()
            minimo = df[metrica].min()
            stats_html += f"""
            <tr>
                <td><strong>{metrica.replace('_', ' ').title()}</strong></td>
                <td>{promedio:,.2f}</td>
                <td>{maximo:,.2f}</td>
                <td>{minimo:,.2f}</td>
            </tr>
            """
    
    # Tabla de datos
    tabla_datos = df.to_html(index=False, classes='table table-striped', border=0)
    
    # HTML completo
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
        <div class="header">
            <h1>📊 {titulo}</h1>
            <p>Generado el {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
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
            <p>CHAMPILYTICS - Matriz de Redes Sociales Maristas</p>
        </div>
    </body>
    </html>
    """
    
    return html
