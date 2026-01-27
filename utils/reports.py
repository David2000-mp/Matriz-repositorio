"""
Módulo para generación de reportes PDF para CHAMPILEAKS.
Utiliza FPDF para crear reportes ejecutivos con datos de métricas sociales.
"""

from fpdf import FPDF
from typing import List, Dict, Any
import pandas as pd
import unicodedata


def _sanitize_text(s: Any) -> str:
    """Sanitiza texto para FPDF: convierte tildes/ñ y otros a ASCII-latin1 compatibles.

    Usa `unidecode` si está disponible; si no, cae a `unicodedata` y elimina diacríticos.
    Devuelve `str` seguro para colocar en el PDF.
    """
    if s is None:
        return ''
    try:
        # prefer unidecode if installed
        from unidecode import unidecode  # type: ignore

        out = unidecode(str(s))
        # FPDF doesn't support some control chars; strip them
        return ''.join(ch for ch in out if ord(ch) >= 32)
    except Exception:
        # fallback: normalize and remove diacritics
        try:
            txt = str(s)
            nfkd = unicodedata.normalize('NFKD', txt)
            ascii_txt = ''.join([c for c in nfkd if not unicodedata.combining(c)])
            # keep only printable characters
            return ''.join(ch for ch in ascii_txt if ord(ch) >= 32)
        except Exception:
            return str(s)


class PDF(FPDF):
    def header(self):
        # Título centrado con color Marista
        self.set_font('Arial', 'B', 16)
        self.set_text_color(0, 40, 85)
        self.cell(0, 10, 'CHAMPILEAKS - Reporte Ejecutivo', 0, 1, 'C')
        self.ln(4)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.set_text_color(100, 100, 100)
        self.cell(0, 10, f'Página {self.page_no()}', 0, 0, 'C')


def _safe_number(x):
    try:
        return float(x)
    except Exception:
        return None


def generate_pdf_report(school_name: str, period: str, kpis: Dict[str, Dict[str, Any]], anomalies: List[Any], health_score: float) -> bytes:
    """Genera un PDF ejecutivo con encabezado, salud, KPIs y hallazgos.

    Args:
        school_name: nombre del colegio
        period: periodo (YYYY-MM o similar)
        kpis: diccionario con keys como 'seguidores', 'interacciones', 'alcance', 'engagement'
              cada valor puede ser dict {'valor':..., 'delta':...} o un número
        anomalies: lista de strings o dicts describiendo anomalías
        health_score: número 0-100

    Returns:
        bytes: contenido del PDF
    """
    pdf = PDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)

    # Header
    pdf.set_font('Arial', 'B', 14)
    pdf.set_text_color(0, 40, 85)
    pdf.cell(0, 8, _sanitize_text(school_name), 0, 1)
    pdf.set_font('Arial', '', 11)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(0, 6, f'Periodo: {_sanitize_text(period)}', 0, 1)
    pdf.ln(6)

    # Salud destacada
    pdf.set_font('Arial', 'B', 12)
    pdf.set_text_color(0, 40, 85)
    pdf.cell(0, 8, 'Salud Digital', 0, 1)
    pdf.ln(2)
    pdf.set_font('Arial', 'B', 28)
    score_color = (46, 204, 113) if (health_score or 0) > 80 else (241, 196, 15) if (health_score or 0) > 60 else (231, 76, 60)
    pdf.set_text_color(*score_color)
    try:
        pdf.cell(0, 18, _sanitize_text(f'{float(health_score):.0f}/100'), 0, 1)
    except Exception:
        pdf.cell(0, 18, _sanitize_text(str(health_score or 'N/A')), 0, 1)
    pdf.set_text_color(0, 0, 0)
    pdf.ln(6)

    # KPIs section (compact table)
    pdf.set_font('Arial', 'B', 12)
    pdf.set_text_color(0, 40, 85)
    pdf.cell(0, 8, 'KPIs Principales', 0, 1)
    pdf.ln(2)

    # Table header
    pdf.set_font('Arial', 'B', 10)
    pdf.cell(60, 8, 'Métrica', 1)
    pdf.cell(50, 8, 'Valor', 1)
    pdf.cell(60, 8, 'Variación', 1)
    pdf.ln()

    pdf.set_font('Arial', '', 10)
    ordered_metrics = ['seguidores', 'interacciones', 'alcance', 'engagement']
    for m in ordered_metrics:
        if m in (kpis or {}):
            v = kpis[m]
            if isinstance(v, dict):
                val = v.get('valor', 'N/A')
                delta = v.get('delta', v.get('prev_delta', ''))
            else:
                val = v
                delta = ''
            disp = m.capitalize() if m != 'engagement' else 'Engagement %'
            pdf.cell(60, 8, _sanitize_text(disp), 1)
            pdf.cell(50, 8, _sanitize_text(val), 1) if isinstance(val, str) else pdf.cell(50, 8, _sanitize_text(str(val)), 1)
            pdf.cell(60, 8, _sanitize_text(delta), 1) if isinstance(delta, str) else pdf.cell(60, 8, _sanitize_text(str(delta)), 1)
            pdf.ln()

    # Findings / Hallazgos
    pdf.ln(6)
    pdf.set_font('Arial', 'B', 12)
    pdf.set_text_color(0, 40, 85)
    pdf.cell(0, 8, 'Hallazgos y Anomalías', 0, 1)
    pdf.ln(2)
    pdf.set_font('Arial', '', 10)
    if not anomalies:
        pdf.cell(0, 7, _sanitize_text('No se detectaron anomalías significativas en este periodo.'), 0, 1)
    else:
        for a in anomalies:
            if isinstance(a, dict):
                entidad = _sanitize_text(a.get('entidad') or a.get('nombre') or '')
                plataforma = _sanitize_text(a.get('plataforma') or '')
                txt = []
                if a.get('anomalia_seguidores'):
                    txt.append('Caida en Seguidores')
                if a.get('anomalia_interacciones'):
                    txt.append('Interacciones atipicas')
                msg = _sanitize_text(f"- {entidad} {(' | ' + plataforma) if plataforma else ''}: {', '.join(txt)}")
                pdf.multi_cell(0, 7, msg)
            else:
                pdf.multi_cell(0, 7, _sanitize_text(f'- {str(a)}'))

    pdf.ln(6)
    pdf.set_font('Arial', 'I', 8)
    pdf.set_text_color(120, 120, 120)
    pdf.cell(0, 6, 'Reporte generado por CHAMPILEAKS', 0, 1)

    pdf_bytes = pdf.output(dest='S')
    return pdf_bytes.encode('latin-1', errors='replace')


def generate_html_report(school_name: str,
                         period: str,
                         kpis: Dict[str, Dict[str, Any]] = None,
                         anomalies: List[Dict[str, Any]] = None,
                         detail_df: pd.DataFrame = None,
                         health_score: float = None) -> str:
    """Genera un HTML tipo dashboard con identidad Marista.

    El layout genera:
    - Banner principal con color #003696
    - Fila de 3 tarjetas (Salud Global, Crecimiento, Engagement)
    - Bloque "Alertas Críticas" (solo si hay anomalías relevantes)
    - Tabla de detalle con columnas internas ocultas
    """
    kpis = kpis or {}
    anomalies = anomalies or []

    # Convertir anomalies/lista de dicts a detail_df si aplica
    if detail_df is None and anomalies and isinstance(anomalies, list) and isinstance(anomalies[0], dict):
        try:
            detail_df = pd.DataFrame(anomalies)
        except Exception:
            detail_df = None

    if detail_df is not None and not isinstance(detail_df, pd.DataFrame):
        try:
            detail_df = pd.DataFrame(detail_df)
        except Exception:
            detail_df = None

    # Detectar si hay alertas críticas
    show_alerts = any(isinstance(a, dict) and (a.get('anomalia_seguidores') or a.get('anomalia_interacciones')) for a in anomalies)

    # Helper para extraer KPIs
    def _kpiv(key):
        try:
            v = kpis.get(key, {})
            if isinstance(v, dict):
                return v.get('valor') if v.get('valor') is not None else v.get('value')
            return v
        except Exception:
            return None

    salud = health_score if health_score is not None else (_kpiv('health_score') or 'N/A')
    crecimiento = _kpiv('seguidores') or _kpiv('followers') or 'N/A'
    engagement = _kpiv('engagement_rate') or _kpiv('engagement') or 'N/A'

    # CSS Marista WCAG AA (contraste mínimo 4.5:1)
    css = """
        <style>
            :root{
                --marista-blue:#003696; 
                --marista-amber:#FFB81C; 
                --alert-red:#C82333; 
                --alert-green:#1E7E34;
                --text-primary:#1A1A1A;
                --text-secondary:#4A5568;
            }
            body{font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial; color:var(--text-primary); background:#f6f8fa; padding:16px; font-size:16px; line-height:1.6;}
            .banner{background:var(--marista-blue); color: white; padding:20px 24px; border-radius:8px; margin-bottom:18px}
            .banner h1{margin:0; font-size:22px; font-weight:700;}
            .meta{color:rgba(255,255,255,0.95); font-size:15px; margin-top:8px}
            .kpi-row{display:flex; gap:14px; margin:14px 0 20px 0}
            .kpi-card{flex:1; background:#fff; border-radius:8px; padding:16px; box-shadow:0 4px 8px rgba(0,0,0,0.08); border-left:4px solid var(--marista-amber); color:var(--marista-blue)}
            .kpi-title{font-size:15px; color:var(--marista-blue); margin-bottom:8px; font-weight:600;}
            .kpi-value{font-size:26px; font-weight:800; color:var(--text-primary)}
            .kpi-subtitle{font-size:14px; color:var(--text-secondary); margin-top:8px}
            .kpi-amber{color:var(--marista-amber); font-weight:700;}
            .alerts{padding:14px; border-radius:8px; margin-bottom:18px}
            .alert-item{padding:10px 14px; border-radius:6px; color:white; margin-bottom:10px; font-size:15px; font-weight:600;}
            .details-table{width:100%; border-collapse:collapse; margin-top:14px; font-size:15px}
            .details-table thead th{background:var(--marista-blue); color:#fff; position:sticky; top:0; z-index:2; font-weight:700; padding:12px;}
            .details-table th, .details-table td{border:1px solid #E5E7EB; padding:12px; text-align:left; vertical-align:middle}
            .details-table tbody tr:nth-child(even){background:#FAFAFA}
            .details-table tbody tr:hover{background:#EFF6FF}
            .details-table td.num{ text-align:right; font-variant-numeric:tabular-nums }
            .details-card{background:#fff; padding:14px; border-radius:8px; box-shadow:0 6px 20px rgba(0,0,0,0.06)}
            .school-title{background:#EFF6FF; padding:10px 12px; border-radius:6px; margin-top:12px; font-weight:700; color:var(--text-primary);}
            .summary-row{background:#F3F4F6; font-weight:700}
            @media (max-width:800px){.kpi-row{flex-direction:column}}
        </style>
        """

    parts = []
    parts.append('<!doctype html><html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">')
    parts.append(css)
    parts.append('</head><body>')

    parts.append(f'<div class="banner"><h1>Reporte Ejecutivo — {school_name}</h1><div class="meta">Periodo: {period}</div></div>')

    # KPI cards
    parts.append('<div class="kpi-row">')
    parts.append(f'<div class="kpi-card"><div class="kpi-title">Salud Global</div><div class="kpi-value">{salud}</div></div>')
    parts.append(f'<div class="kpi-card"><div class="kpi-title">Crecimiento (Seguidores)</div><div class="kpi-value kpi-amber">{crecimiento}</div></div>')
    parts.append(f'<div class="kpi-card"><div class="kpi-title">Engagement Promedio</div><div class="kpi-value">{engagement}</div></div>')
    parts.append('</div>')

    # Executive summary and alerts
    parts.append('<div class="details-card">')
    parts.append('<h2>Resumen Ejecutivo</h2>')

    # Engagement narrative
    eng_curr = None
    eng_prev = None
    try:
        if isinstance(kpis, dict) and 'engagement_rate' in kpis:
            eng_curr = kpis['engagement_rate'].get('valor') or kpis['engagement_rate'].get('value')
            eng_prev = kpis['engagement_rate'].get('prev')
    except Exception:
        eng_curr = eng_prev = None

    if eng_curr is not None:
        try:
            delta_txt = ''
            if eng_prev is not None:
                delta = (float(eng_curr) - float(eng_prev)) / float(eng_prev) * 100 if float(eng_prev) != 0 else None
                if delta is not None:
                    sign = '+' if delta >= 0 else ''
                    delta_txt = f' ({sign}{delta:.1f}% vs periodo anterior)'
            parts.append(f'<p>Engagement promedio: <strong>{float(eng_curr):.2f}%</strong>{delta_txt}.</p>')
        except Exception:
            parts.append(f'<p>Engagement promedio: <strong>{eng_curr}</strong>.</p>')
    else:
        parts.append('<p>Engagement promedio: N/A.</p>')

    # Alerts block
    if show_alerts:
        parts.append('<div class="alerts">')
        parts.append('<h3>Alertas Críticas</h3>')
        for a in anomalies:
            if not isinstance(a, dict):
                parts.append(f'<div class="alert-item" style="background:var(--alert-red)">{str(a)}</div>')
                continue
            entidad = a.get('entidad') or a.get('nombre') or ''
            plataforma = a.get('plataforma') or ''
            if a.get('anomalia_seguidores'):
                parts.append(f'<div class="alert-item" style="background:var(--alert-red)">{entidad} — {plataforma}: Caída de Seguidores</div>')
            if a.get('anomalia_interacciones'):
                parts.append(f'<div class="alert-item" style="background:var(--alert-green)">{entidad} — {plataforma}: Interacciones atípicas</div>')
        parts.append('</div>')
    else:
        parts.append('<p>No se detectaron alertas críticas en este periodo.</p>')

    parts.append('</div>')

    # Detail table: agrupado por colegio (entidad/nombre)
    if detail_df is not None and not detail_df.empty:
        hide_cols = [c for c in ['id_cuenta', 'seguidores_ma3', 'interacciones_ma3'] if c in detail_df.columns]
        hide_cols += [c for c in detail_df.columns if str(c).startswith('anomalia')]
        table_df = detail_df.drop(columns=hide_cols, errors='ignore').copy()

        # Prefer columns ordering and identify colegio column
        cols = list(table_df.columns)
        prefer = ['entidad', 'nombre', 'plataforma', 'fecha', 'date']
        ordered = [c for c in prefer if c in cols] + [c for c in cols if c not in prefer]
        table_df = table_df[ordered]

        # Determine grouping column (entidad or nombre)
        group_col = None
        for candidate in ['entidad', 'nombre']:
            if candidate in table_df.columns:
                group_col = candidate
                break

        parts.append('<div class="details-card" style="margin-top:18px">')
        parts.append('<h2>Detalle de Métricas</h2>')

        if group_col:
            # Render a subtable per colegio with formatted numbers and a summary row
            for colegio, gdf in table_df.groupby(group_col):
                parts.append(f'<div class="school-title">{colegio}</div>')
                # For clarity, remove the group_col from the display columns
                display_cols = [c for c in gdf.columns if c != group_col]

                # Detect numeric columns for formatting and summary
                num_cols = []
                for c in display_cols:
                    try:
                        if pd.api.types.is_numeric_dtype(gdf[c]):
                            num_cols.append(c)
                    except Exception:
                        pass

                def fmt(val, col=None):
                    if pd.isna(val):
                        return ''
                    try:
                        if col in num_cols:
                            # Integers vs floats
                            if float(val).is_integer():
                                return f"{int(val):,}"
                            return f"{float(val):,.1f}"
                    except Exception:
                        pass
                    return str(val)

                parts.append('<table class="details-table">')
                parts.append('<thead><tr>')
                for c in display_cols:
                    parts.append(f'<th>{str(c).replace("_"," ").title()}</th>')
                parts.append('</tr></thead>')
                parts.append('<tbody>')

                # Summary row (totals) for numeric columns
                if num_cols:
                    parts.append('<tr class="summary-row">')
                    for c in display_cols:
                        if c in num_cols:
                            total = gdf[c].sum() if not gdf[c].isnull().all() else ''
                            parts.append(f'<td class="num">{fmt(total,c)}</td>')
                        else:
                            parts.append('<td></td>')
                    parts.append('</tr>')

                for _, row in gdf.iterrows():
                    parts.append('<tr>')
                    for c in display_cols:
                        val = row[c]
                        cell = fmt(val, c)
                        cls = 'num' if c in num_cols else ''
                        parts.append(f'<td class="{cls}">{cell}</td>')
                    parts.append('</tr>')
                parts.append('</tbody></table>')
        else:
            # Fallback: render single table if no colegio column
            parts.append('<table class="details-table">')
            parts.append('<thead><tr>')
            for c in table_df.columns:
                parts.append(f'<th>{c}</th>')
            parts.append('</tr></thead>')
            parts.append('<tbody>')
            for _, row in table_df.iterrows():
                parts.append('<tr>')
                for c in table_df.columns:
                    val = row[c]
                    parts.append(f'<td>{val if pd.notna(val) else ""}</td>')
                parts.append('</tr>')
            parts.append('</tbody></table>')

        parts.append('</div>')
    else:
        parts.append('<p><em>No hay detalle disponible para mostrar.</em></p>')

    parts.append('<footer style="margin-top:20px;color:#666;font-size:12px">Reporte generado por CHAMPILEAKS</footer>')
    parts.append('</body></html>')

    return ''.join(parts)