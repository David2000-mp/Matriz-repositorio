"""
Test de Plotly para verificar que las gráficas se renderizan correctamente.
Genera un archivo HTML para abrir en el navegador.
"""
import pandas as pd
import plotly.express as px
from utils.data_provider import data_provider
from utils.analytics import normalize_monthly_latest, apply_moving_average, detect_anomalies

# Cargar y procesar datos
df = data_provider.get_merged_data()
df_full = df.copy()

if "fecha" in df_full.columns:
    df_full["fecha"] = pd.to_datetime(df_full["fecha"], errors="coerce")
    df_full = df_full.dropna(subset=['fecha'])
    df_full = normalize_monthly_latest(df_full)

df_full = apply_moving_average(df_full, col="seguidores")

# Crear df_evo exactamente como en dashboard.py
df_evo = df_full.groupby(["fecha", "plataforma"])["seguidores"].max().reset_index()
df_evo["fecha"] = pd.to_datetime(df_evo["fecha"], errors="coerce")
df_evo = df_evo.dropna(subset=["fecha"]).sort_values(["plataforma", "fecha"])

print("Generando gráfica de prueba...")
print(f"Datos: {len(df_evo)} puntos")
print(df_evo)

# Crear gráfica con px.area (como en el código original)
fig_area = px.area(
    df_evo,
    x="fecha",
    y="seguidores",
    color="plataforma",
    title="TEST: Tendencia de Seguidores por Plataforma",
    markers=True
)

fig_area.update_layout(autosize=True)
fig_area.update_xaxes(type="date")

# Guardar como HTML
output_file = "test_grafica_area.html"
fig_area.write_html(output_file)
print(f"\n✓ Gráfica guardada en: {output_file}")
print("Abre este archivo en tu navegador para verificar visualmente.")

# También crear una gráfica de líneas para comparar
fig_line = px.line(
    df_evo,
    x="fecha",
    y="seguidores",
    color="plataforma",
    title="TEST: Línea de Seguidores por Plataforma",
    markers=True
)

fig_line.update_layout(autosize=True)
fig_line.update_xaxes(type="date")

output_file_line = "test_grafica_line.html"
fig_line.write_html(output_file_line)
print(f"✓ Gráfica de línea guardada en: {output_file_line}")

print("\nSi ambas gráficas muestran múltiples puntos en el navegador,")
print("entonces el problema está en cómo Streamlit renderiza Plotly.")
