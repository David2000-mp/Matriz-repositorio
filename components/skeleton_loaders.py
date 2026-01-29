"""
Skeleton loaders para componentes en carga.
Proporciona placeholders animados mientras se cargan datos/gráficos.
"""
import streamlit as st


def show_kpi_skeleton(count=4):
    """
    Muestra skeleton loader para tarjetas KPI.
    
    Args:
        count: Número de tarjetas skeleton a mostrar
    """
    skeleton_cards = ''.join([f'<div class="kpi-skeleton"></div>' for _ in range(count)])
    
    st.markdown(f"""
        <div class="kpi-skeleton-container">
            {skeleton_cards}
        </div>
        <style>
        .kpi-skeleton-container {{
            display: flex;
            gap: 16px;
            margin-bottom: 20px;
            flex-wrap: wrap;
        }}
        .kpi-skeleton {{
            flex: 1 1 220px;
            height: 120px;
            background: linear-gradient(90deg, #F2F4F7 25%, #E0E4E7 50%, #F2F4F7 75%);
            background-size: 200% 100%;
            animation: skeleton-loading 1.5s infinite;
            border-radius: 12px;
            min-width: 200px;
        }}
        @keyframes skeleton-loading {{
            0% {{ background-position: 200% 0; }}
            100% {{ background-position: -200% 0; }}
        }}
        </style>
    """, unsafe_allow_html=True)


def show_chart_skeleton(height=400):
    """
    Muestra skeleton loader para gráficos Plotly.
    
    Args:
        height: Altura del skeleton en píxeles
    """
    st.markdown(f"""
        <div class="skeleton-chart" style="height: {height}px;">
            <div class="skeleton-title"></div>
            <div class="skeleton-bars">
                <div class="skeleton-bar" style="height: 60%"></div>
                <div class="skeleton-bar" style="height: 80%"></div>
                <div class="skeleton-bar" style="height: 40%"></div>
                <div class="skeleton-bar" style="height: 90%"></div>
                <div class="skeleton-bar" style="height: 70%"></div>
            </div>
        </div>
        <style>
        .skeleton-chart {{
            background: #F2F4F7;
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 20px;
        }}
        .skeleton-title {{
            width: 40%;
            height: 24px;
            background: linear-gradient(90deg, #E0E4E7 25%, #D0D4D7 50%, #E0E4E7 75%);
            background-size: 200% 100%;
            animation: skeleton-loading 1.5s infinite;
            border-radius: 4px;
            margin-bottom: 20px;
        }}
        .skeleton-bars {{
            display: flex;
            gap: 10px;
            align-items: flex-end;
            height: calc(100% - 50px);
        }}
        .skeleton-bar {{
            flex: 1;
            background: linear-gradient(90deg, #E0E4E7 25%, #D0D4D7 50%, #E0E4E7 75%);
            background-size: 200% 100%;
            animation: skeleton-loading 1.5s infinite;
            border-radius: 4px;
        }}
        </style>
    """, unsafe_allow_html=True)
