"""
Módulo para la generación de reportes personalizados en formato PDF y HTML.
Contiene ReportBuilder (PDF) y generate_engagement_report_html (HTML).
"""

from fpdf import FPDF
from datetime import datetime
import base64
import os
import pandas as pd
import uuid


# ============================================================================
# CLASE: ReportBuilder (PDF)
# ============================================================================

class ReportBuilder(FPDF):
    def __init__(self, df: pd.DataFrame, entity_name: str = "Reporte"):
        """
        Inicializa el reporte con los datos (DF) y el nombre de la entidad.
        """
        super().__init__()
        self.df = df
        # Validación de seguridad: Si entity_name es None, usar string por defecto
        self.entity_name = entity_name if entity_name else "Entidad Desconocida"
        self.output_path = f"reporte_temp_{uuid.uuid4().hex}.pdf"  # Nombre único para evitar colisiones

        # Configuración inicial del PDF
        self.set_auto_page_break(auto=True, margin=15)
        self.add_page()
        self.set_font("Arial", size=12)

    def header(self):
        # Encabezado en todas las páginas
        self.set_font("Arial", "B", 10)
        self.cell(
            0,
            10,
            f"Reporte de Desempeño: {self.encode_text(self.entity_name)}",
            0,
            1,
            "R",
        )
        self.ln(5)

    def encode_text(self, text):
        """Manejo robusto de codificación (latin-1) evitando errores NoneType."""
        if text is None:
            return ""
        if not isinstance(text, str):
            text = str(text)
        try:
            return text.encode("latin-1", "replace").decode("latin-1")
        except Exception:
            return text  # Fallback si falla la codificación

    def add_cover_page(self):
        """Agrega una portada al reporte."""
        print("Paso 1: Generando portada...")
        # (Ya estamos en la página 1 por el __init__)
        self.ln(60)
        self.set_font("Arial", size=24, style="B")
        self.cell(0, 10, self.encode_text(self.entity_name), ln=True, align="C")
        self.ln(10)
        self.set_font("Arial", size=16)
        self.cell(0, 10, "Reporte Mensual de Redes Sociales", ln=True, align="C")
        self.add_page()  # Salto de página para lo siguiente

    def add_kpis_table(self):
        """Agrega una tabla de KPIs basada en el DF."""
        print("Paso 2: Generando tabla de KPIs...")
        self.set_font("Arial", size=14, style="B")
        self.cell(0, 10, "Tabla de Datos", ln=True, align="L")
        self.ln(5)

        # Seleccionar columnas clave para que quepan
        cols_to_show = [
            c
            for c in self.df.columns
            if c
            in ["fecha", "plataforma", "seguidores", "interacciones", "engagement_rate"]
        ]
        if not cols_to_show:
            cols_to_show = self.df.columns[:5]  # Fallback

        df_table = self.df[cols_to_show].head(
            15
        )  # Solo las primeras 15 filas para no saturar

        # Configuración de celdas
        col_width = 190 / len(cols_to_show)
        self.set_font("Arial", size=10, style="B")

        # Cabeceras
        for col in cols_to_show:
            self.cell(col_width, 10, self.encode_text(col.upper()), border=1, align="C")
        self.ln()

        # Filas
        self.set_font("Arial", size=10)
        for _, row in df_table.iterrows():
            for col in cols_to_show:
                val = str(row[col])
                # Truncar si es muy largo
                if len(val) > 15:
                    val = val[:12] + "..."
                self.cell(col_width, 10, self.encode_text(val), border=1, align="C")
            self.ln()

        self.add_page()

    def add_analysis_summary(self):
        """
        Agrega un resumen analítico comparando el primer y último mes registrado.
        """
        print("Paso 2.5: Generando resumen analítico...")
        try:
            # Ordenar por fecha para obtener el primer y último registro
            self.df = self.df.sort_values(by="fecha")
            first_row = self.df.iloc[0]
            last_row = self.df.iloc[-1]

            # Extraer métricas clave
            seguidores_inicio = first_row["seguidores"]
            seguidores_fin = last_row["seguidores"]
            crecimiento = (
                ((seguidores_fin - seguidores_inicio) / seguidores_inicio) * 100
                if seguidores_inicio > 0
                else 0
            )

            # Agregar texto al PDF
            self.set_font("Arial", size=12)
            self.cell(0, 10, "Análisis Automático", ln=True, align="L")
            self.ln(5)
            self.set_font("Arial", size=10)
            self.multi_cell(
                0,
                10,
                self.encode_text(
                    f"La institución {self.entity_name} inició con {seguidores_inicio:,} seguidores y finalizó con {seguidores_fin:,}, "
                    f"representando un crecimiento del {crecimiento:.2f}%."
                ),
            )
            self.ln(10)
        except Exception as e:
            print(f"   [ERROR ANALISIS]: {e}")
            self.set_text_color(255, 0, 0)
            self.cell(0, 10, f"No se pudo generar el análisis: {str(e)}", ln=True)
            self.set_text_color(0, 0, 0)

    def add_trend_graphs(self):
        """
        Genera gráficas simples usando Plotly y las inserta con manejo de errores.
        """
        print("Paso 3: Intentando generar gráficas...")
        try:
            import plotly.express as px
            import plotly.io as pio

            # Gráfica 1: Seguidores
            fig1 = px.line(
                self.df, x="fecha", y="seguidores", title="Evolución de Seguidores"
            )
            img_path1 = "temp_chart_1.png"
            pio.write_image(fig1, img_path1, format="png", width=800, height=400)

            self.set_font("Arial", size=14, style="B")
            self.cell(0, 10, "Tendencias Gráficas", ln=True)
            self.image(img_path1, x=10, w=190)
            self.ln(10)

            os.remove(img_path1)
            print("   -> Gráfica 1 insertada")

        except Exception as e:
            print(f"   [ERROR GRAFICAS]: {e}")
            self.set_text_color(255, 0, 0)
            self.cell(0, 10, f"No se pudieron generar las gráficas: {str(e)}", ln=True)
            self.set_text_color(0, 0, 0)

    def generate(self, sections: list):
        """
        Orquesta la generación del reporte y retorna los BYTES del PDF.
        """
        print(f"Paso 0: Iniciando reporte para secciones: {sections}")

        # Lógica de secciones
        # Siempre ponemos portada
        self.add_cover_page()

        if "kpis" in sections:
            self.add_kpis_table()

        if "graficas" in sections:
            self.add_trend_graphs()

        if "analisis" in sections:
            self.add_analysis_summary()

        # Finalizar y guardar temporalmente
        print("Paso 4: Guardando archivo temporal...")
        self.output(self.output_path, "F")

        # Leer los bytes para devolverlos a Streamlit
        print("Paso 5: Leyendo bytes para descarga...")
        with open(self.output_path, "rb") as f:
            pdf_bytes = f.read()

        # Limpieza (borrar el archivo temp del servidor)
        if os.path.exists(self.output_path):
            os.remove(self.output_path)

        return pdf_bytes


# ============================================================================
# FUNCIÓN: generate_engagement_report_html (HTML)
# ============================================================================


def get_logo_b64():
    """Intenta cargar el logo Marista en base64, retorna placeholder si no existe."""
    try:
        logo_path = os.path.join("images", "logo_maristas.png")
        if os.path.exists(logo_path):
            with open(logo_path, "rb") as f:
                return base64.b64encode(f.read()).decode()
    except Exception:
        pass
    return None


def generate_engagement_report_html(
    platform: str,
    followers: int,
    days: int,
    posts_list: list,
    engagement_pct: float,
    engagement_per_post: float,
    engagement_by_views: float,
    posts_per_week: float,
    diagnosis: str,
    content_stats: dict,
    growth_scenarios: dict,
    expected: dict
) -> str:
    """
    Genera un reporte HTML profesional con toda la información del análisis.
    
    Args:
        platform: "facebook" o "tiktok"
        followers: número de seguidores
        days: período de análisis en días
        posts_list: lista de posts con datos
        engagement_pct: porcentaje de engagement general
        engagement_per_post: engagement promedio por post
        engagement_by_views: engagement por vistas (solo TikTok)
        posts_per_week: frecuencia de posts
        diagnosis: diagnóstico (ej: "🟢 EXCELENTE")
        content_stats: diccionario con estadísticas por tipo de contenido
        growth_scenarios: escenarios de crecimiento
        expected: benchmarks esperados
    
    Returns:
        String HTML completo
    """
    
    timestamp = datetime.now().strftime("%d de %B de %Y a las %H:%M")
    
    # Detectar diagnóstico nivel
    if "EXCELENTE" in diagnosis or "🟢" in diagnosis:
        diagnosis_color = "#0A7D35"
        diagnosis_bg = "#0A7D315"
        diagnosis_level = "excellent"
    elif "BUENO" in diagnosis or "🟡" in diagnosis:
        diagnosis_color = "#003696"
        diagnosis_bg = "#00369615"
        diagnosis_level = "good"
    elif "MODERADO" in diagnosis or "⚠️" in diagnosis:
        diagnosis_color = "#CC7000"
        diagnosis_bg = "#CC700015"
        diagnosis_level = "moderate"
    else:
        diagnosis_color = "#B42318"
        diagnosis_bg = "#B4231815"
        diagnosis_level = "poor"
    
    # Tabla de publicaciones
    posts_table_html = ""
    for post in posts_list:
        validation = None
        icon = "❓"
        
        if post["total"] == 0:
            validation = "Sin datos"
            icon = "⚪"
        else:
            engagement = (post["total"] / followers * 100) if followers > 0 else 0
            if engagement >= expected["typical"] * 1.5:
                validation = "Excelente"
                icon = "🟢"
            elif engagement >= expected["typical"] * 0.7:
                validation = "Normal"
                icon = "🟡"
            else:
                validation = "Bajo"
                icon = "🔴"
        
        posts_table_html += f"""
        <tr>
            <td style='padding: 10px; border-bottom: 1px solid #DEE2E6;'>{post['num']}</td>
            <td style='padding: 10px; border-bottom: 1px solid #DEE2E6;'>{post['type']}</td>
            <td style='padding: 10px; border-bottom: 1px solid #DEE2E6;'>{post['total']}</td>
            <td style='padding: 10px; border-bottom: 1px solid #DEE2E6;'>{icon} {validation}</td>
        </tr>
        """
    
    # Tabla de contenido
    content_table_html = ""
    for ctype, stats in sorted(content_stats.items(), key=lambda x: x[1]["engagement"], reverse=True):
        content_table_html += f"""
        <tr>
            <td style='padding: 10px; border-bottom: 1px solid #DEE2E6;'>{ctype}</td>
            <td style='padding: 10px; border-bottom: 1px solid #DEE2E6;'>{stats['posts']}</td>
            <td style='padding: 10px; border-bottom: 1px solid #DEE2E6;'>{stats['total_interactions']}</td>
            <td style='padding: 10px; border-bottom: 1px solid #DEE2E6;'><strong>{stats['engagement']:.2f}%</strong></td>
        </tr>
        """
    
    # Recomendaciones basadas en diagnosis
    if diagnosis_level == "excellent":
        recommendations = """
        <h3 style='color: #0A7D35; margin-top: 0;'>✅ Recomendaciones</h3>
        <ul style='line-height: 1.8; color: #495057;'>
            <li><strong>Mantén la consistencia:</strong> Continúa con la misma frecuencia de publicación</li>
            <li><strong>Repite el éxito:</strong> Analiza qué formatos funcionan mejor y crea más contenido similar</li>
            <li><strong>Experimenta:</strong> Con tu engagement actual, puedes probar nuevos formatos sin riesgo</li>
            <li><strong>Monetiza:</strong> Considera opciones de monetización disponibles en la plataforma</li>
        </ul>
        """
    elif diagnosis_level == "good":
        recommendations = """
        <h3 style='color: #003696; margin-top: 0;'>💡 Recomendaciones</h3>
        <ul style='line-height: 1.8; color: #495057;'>
            <li><strong>Incrementa frecuencia:</strong> Pasa de publicar cada algunos días a 4-5 veces por semana</li>
            <li><strong>Enfócate en lo que funciona:</strong> Replica los formatos de mejor desempeño</li>
            <li><strong>Mejora tus CTA:</strong> Invita explícitamente a comentar, reaccionar y compartir</li>
            <li><strong>Analiza el timing:</strong> Publica en los horarios cuando tu audiencia está más activa</li>
        </ul>
        """
    elif diagnosis_level == "moderate":
        recommendations = """
        <h3 style='color: #CC7000; margin-top: 0;'>🎯 Recomendaciones Urgentes</h3>
        <ul style='line-height: 1.8; color: #495057;'>
            <li><strong>🔴 CRÍTICO - Aumenta frecuencia:</strong> Publica diario o casi diariamente</li>
            <li><strong>Revisa tu contenido:</strong> ¿Es relevante para tu audiencia? Haz investigación de mercado</li>
            <li><strong>Prueba nuevos formatos:</strong> Especialmente los que mostrad mejor desempeño histórico</li>
            <li><strong>Crea comunidad:</strong> Responde TODOS los comentarios, haz preguntas directas</li>
            <li><strong>Usa hashtags:</strong> Investiga hashtags relevantes para tu nicho</li>
        </ul>
        """
    else:  # poor
        recommendations = """
        <h3 style='color: #B42318; margin-top: 0;'>⚠️ Acciones Inmediatas Necesarias</h3>
        <ul style='line-height: 1.8; color: #495057;'>
            <li><strong>🔴 CRÍTICO:</strong> Tu engagement está muy bajo. Necesitas cambios significativos YA</li>
            <li><strong>Aumenta a 5-7 posts/semana:</strong> Mínimo diario para romper este ciclo</li>
            <li><strong>Rediseña tu contenido:</strong> Estudia competidores exitosos en tu nicho</li>
            <li><strong>Enfócate SOLO en lo que funciona:</strong> Desecha formatos que no generan engagement</li>
            <li><strong>Interactúa como comunidad:</strong> Sigue, comenta, comparte - sé visible</li>
            <li><strong>Usa CTAs explícitos:</strong> "¿Qué opinas?" vs solo publicar contenido</li>
            <li><strong>Considera trabajar con otros:</strong> Colaboraciones y guest posts pueden traer audiencia</li>
        </ul>
        """
    
    html = f"""
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Reporte de Engagement - {'Facebook' if platform == 'facebook' else 'TikTok'}</title>
        <style>
            * {{
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }}
            
            body {{
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
                background: #FFFFFF;
                color: #212529;
                line-height: 1.6;
            }}
            
            .container {{
                max-width: 900px;
                margin: 0 auto;
                padding: 40px 20px;
            }}
            
            .header {{
                background: linear-gradient(135deg, #003696 0%, #002566 100%);
                color: white;
                padding: 40px;
                border-radius: 12px;
                margin-bottom: 40px;
                text-align: center;
            }}
            
            .header h1 {{
                font-size: 28px;
                margin-bottom: 10px;
            }}
            
            .header p {{
                font-size: 14px;
                opacity: 0.9;
            }}
            
            .logo {{
                width: 60px;
                margin-bottom: 20px;
            }}
            
            .metrics {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 20px;
                margin-bottom: 40px;
            }}
            
            .metric-card {{
                background: #F2F4F7;
                padding: 20px;
                border-radius: 10px;
                border-left: 4px solid #003696;
            }}
            
            .metric-label {{
                color: #6C757D;
                font-size: 12px;
                text-transform: uppercase;
                font-weight: 600;
                margin-bottom: 8px;
            }}
            
            .metric-value {{
                color: #003696;
                font-size: 32px;
                font-weight: bold;
                margin-bottom: 4px;
            }}
            
            .metric-desc {{
                color: #495057;
                font-size: 12px;
            }}
            
            .section {{
                margin-bottom: 40px;
            }}
            
            .section h2 {{
                color: #003696;
                font-size: 20px;
                margin-bottom: 20px;
                padding-bottom: 10px;
                border-bottom: 2px solid #DEE2E6;
            }}
            
            .diagnosis-box {{
                background: {diagnosis_bg};
                border-left: 5px solid {diagnosis_color};
                padding: 20px;
                border-radius: 8px;
                margin-bottom: 20px;
            }}
            
            .diagnosis-box h3 {{
                color: {diagnosis_color};
                margin-bottom: 10px;
                margin-top: 0;
            }}
            
            .diagnosis-box p {{
                color: #495057;
                margin-bottom: 15px;
            }}
            
            table {{
                width: 100%;
                border-collapse: collapse;
                margin: 20px 0;
            }}
            
            th {{
                background: #003696;
                color: white;
                padding: 12px;
                text-align: left;
                font-weight: 600;
            }}
            
            td {{
                padding: 10px;
                border-bottom: 1px solid #DEE2E6;
            }}
            
            tr:last-child td {{
                border-bottom: none;
            }}
            
            .growth-grid {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
                gap: 15px;
                margin: 20px 0;
            }}
            
            .growth-card {{
                background: #F2F4F7;
                padding: 15px;
                border-radius: 8px;
                border-left: 4px solid #003696;
                text-align: center;
            }}
            
            .growth-improvement {{
                font-weight: bold;
                color: #003696;
                margin-bottom: 8px;
            }}
            
            .growth-value {{
                font-size: 24px;
                color: #0A7D35;
                font-weight: bold;
                margin-bottom: 8px;
            }}
            
            .growth-desc {{
                font-size: 12px;
                color: #495057;
            }}
            
            .footer {{
                border-top: 2px solid #DEE2E6;
                padding-top: 20px;
                margin-top: 40px;
                color: #6C757D;
                font-size: 12px;
                text-align: center;
            }}
            
            .recommendation-box {{
                background: white;
                border: 1px solid #DEE2E6;
                padding: 20px;
                border-radius: 8px;
                margin-bottom: 20px;
            }}
            
            .recommendation-box ul {{
                margin: 0;
                padding-left: 20px;
            }}
            
            .recommendation-box li {{
                margin-bottom: 10px;
            }}
            
            .content-stats {{
                background: #F2F4F7;
                padding: 15px;
                border-radius: 8px;
                margin-bottom: 20px;
            }}
            
            .benchmark {{
                background: #E8F4F8;
                border-left: 4px solid #0056B3;
                padding: 15px;
                border-radius: 8px;
                margin: 20px 0;
            }}
            
            .benchmark strong {{
                color: #0056B3;
            }}
            
            @media print {{
                body {{
                    background: white;
                }}
                
                .container {{
                    padding: 0;
                }}
                
                .header {{
                    page-break-after: avoid;
                }}
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <!-- HEADER -->
            <div class="header">
                <h1>📊 Reporte de Engagement</h1>
                <p>Análisis completo de tu estrategia de contenido en {'Facebook' if platform == 'facebook' else 'TikTok'}</p>
                <p style='margin-top: 10px; font-size: 12px;'>Generado el {timestamp}</p>
            </div>
            
            <!-- INFORMACIÓN BÁSICA -->
            <div class="section">
                <h2>📋 Información del Análisis</h2>
                <div style='background: #F2F4F7; padding: 20px; border-radius: 8px;'>
                    <p><strong>Plataforma:</strong> {'Facebook' if platform == 'facebook' else 'TikTok'}</p>
                    <p><strong>Seguidores:</strong> {followers:,}</p>
                    <p><strong>Período analizado:</strong> {days} días</p>
                    <p><strong>Publicaciones analizadas:</strong> {len(posts_list)}</p>
                    <p><strong>Frecuencia:</strong> {posts_per_week:.1f} posts por semana</p>
                </div>
            </div>
            
            <!-- DIAGNÓSTICO -->
            <div class="section">
                <h2>🎯 Diagnóstico General</h2>
                <div class="diagnosis-box">
                    <h3>{diagnosis}</h3>
                    <p>
                        Tu engagement actual es de <strong>{engagement_pct:.2f}%</strong>.
                        Para tu tamaño de audiencia ({followers:,} seguidores), 
                        el rango esperado es de <strong>{expected['min']:.1f}% - {expected['max']:.1f}%</strong> 
                        ({expected['label']}).
                    </p>
                </div>
            </div>
            
            <!-- MÉTRICAS PRINCIPALES -->
            <div class="section">
                <h2>📈 Métricas Principales</h2>
                <div class="metrics">
                    <div class="metric-card">
                        <div class="metric-label">Engagement General</div>
                        <div class="metric-value">{engagement_pct:.2f}%</div>
                        <div class="metric-desc">Porcentaje de tu audiencia que interactuó</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-label">Engagement por Post</div>
                        <div class="metric-value">{engagement_per_post:.2f}%</div>
                        <div class="metric-desc">Promedio por publicación</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-label">Interacciones Totales</div>
                        <div class="metric-value">{sum([p['total'] for p in posts_list])}</div>
                        <div class="metric-desc">Likes, comentarios, shares</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-label">Frecuencia</div>
                        <div class="metric-value">{posts_per_week:.1f}</div>
                        <div class="metric-desc">Posts por semana</div>
                    </div>
                </div>
            </div>
            
            <!-- ANÁLISIS POR TIPO DE CONTENIDO -->
            <div class="section">
                <h2>📊 Rendimiento por Tipo de Contenido</h2>
                <p style='margin-bottom: 15px; color: #495057;'>
                    Análisis detallado de cómo cada tipo de contenido performa con tu audiencia.
                </p>
                <table>
                    <thead>
                        <tr>
                            <th>Tipo de Contenido</th>
                            <th>Posts</th>
                            <th>Total Interacciones</th>
                            <th>Engagement %</th>
                        </tr>
                    </thead>
                    <tbody>
                        {content_table_html}
                    </tbody>
                </table>
                <div class="benchmark">
                    <strong>💡 Insight:</strong> Enfócate en los tipos de contenido con mayor engagement.
                    Los primeros en la lista son los que mejor funcionan con tu audiencia.
                </div>
            </div>
            
            <!-- TABLA DE PUBLICACIONES -->
            <div class="section">
                <h2>📑 Detalle de Publicaciones</h2>
                <table>
                    <thead>
                        <tr>
                            <th>#</th>
                            <th>Tipo</th>
                            <th>Interacciones</th>
                            <th>Estado</th>
                        </tr>
                    </thead>
                    <tbody>
                        {posts_table_html}
                    </tbody>
                </table>
            </div>
            
            <!-- POTENCIAL DE CRECIMIENTO -->
            <div class="section">
                <h2>📈 Potencial de Crecimiento</h2>
                <p style='margin-bottom: 15px; color: #495057;'>
                    Si mejoras tu engagement, aquí está el potencial de crecimiento en 3 meses:
                </p>
                <div class="growth-grid">
    """
    
    for improvement, scenario in sorted(growth_scenarios.items()):
        html += f"""
                    <div class="growth-card">
                        <div class="growth-improvement">+{improvement}% Engagement</div>
                        <div class="growth-value">+{scenario['growth_pct']:.0f}%</div>
                        <div class="growth-desc">
                            {followers:,} → {scenario['followers_3m']:,} seguidores
                        </div>
                    </div>
        """
    
    html += f"""
                </div>
                <div class="benchmark">
                    <strong>📌 Nota:</strong> Estas proyecciones están basadas en la relación histórica
                    entre engagement y crecimiento en redes sociales. Los resultados varían según la calidad
                    del contenido y la consistencia de la estrategia.
                </div>
            </div>
            
            <!-- RECOMENDACIONES -->
            <div class="section">
                <div class="recommendation-box">
                    {recommendations}
                </div>
            </div>
            
            <!-- PRÓXIMOS PASOS -->
            <div class="section">
                <h2>✅ Próximos Pasos</h2>
                <div style='background: #E8F4F8; padding: 20px; border-radius: 8px; border-left: 4px solid #0056B3;'>
                    <ol style='color: #495057; line-height: 1.8;'>
                        <li><strong>Esta semana:</strong> Implementa las recomendaciones prioritarias arriba</li>
                        <li><strong>Próximas 2 semanas:</strong> Observa los cambios en tu engagement</li>
                        <li><strong>Próximo mes:</strong> Reanaliza con esta herramienta para medir progreso</li>
                        <li><strong>Cada mes:</strong> Ajusta estrategia basado en datos, no en intuición</li>
                    </ol>
                </div>
            </div>
            
            <!-- FOOTER -->
            <div class="footer">
                <p>
                    Este reporte fue generado automáticamente por la Calculadora de Engagement de CHAMPILEAKS.
                    <br>
                    Los datos y recomendaciones se basan en mejores prácticas de social media marketing.
                    <br>
                    © 2026 Maristas - CHAMPILEAKS Analytics
                </p>
            </div>
        </div>
    </body>
    </html>
    """
    
    return html
