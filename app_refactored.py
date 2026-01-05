"""
App refactorizado para CHAMPILYTICS.
Provee enrutamiento limpio a las vistas y asegura inyección de estilos.
"""
import streamlit as st
import pandas as pd
from utils import load_data
from utils.data_manager import COLEGIOS_MARISTAS
from components import inject_custom_css
from views import landing, dashboard, analytics, data_entry, settings, changelog
from utils.helpers import load_image


def main():
    st.set_page_config(page_title="CHAMPILYTICS", layout="wide", page_icon="Ⓜ️")
    try:
        inject_custom_css()
    except Exception as e:
        try:
            st.warning(f"No se pudo aplicar CSS personalizado: {e}")
        except Exception:
            # En entornos no interactivos, registrar en la consola
            import logging

            logging.warning(f"No se pudo mostrar warning de CSS: {e}")

    # Sincronizar navegación desde la landing (permite botones que escriben `st.session_state['page']`)
    if "page" in st.session_state:
        st.session_state["page_selection"] = st.session_state.page
        del st.session_state["page"]


    # Sidebar: El ÚNICO lugar para filtrar
    with st.sidebar:
        # Logo Marista
        logo_b64 = load_image("logo_maristas.png")
        if logo_b64:
            st.markdown(f'<img src="data:image/png;base64,{logo_b64}" style="width:100px; height:auto; margin-bottom:10px;">', unsafe_allow_html=True)
        
        st.title("CHAMPILYTICS")

        page_key = "page_selection"

        # Modern navigation: compact selectbox with emojis
        display_to_canonical = {
            "🏠 Inicio": "Inicio",
            "📊 Dashboard Global": "Dashboard Global",
            "📈 Comparativas": "Comparativas",
            "📝 Captura": "Captura",
            "⚙️ Configuración": "Configuración",
        }
        display_labels = list(display_to_canonical.keys())
        canonical_to_display = {v: k for k, v in display_to_canonical.items()}

        # Compute current display label from session state (keeps navigation in sync)
        current_canonical = st.session_state.get(page_key, "Inicio")
        current_display = canonical_to_display.get(current_canonical, display_labels[0])

        st.subheader("Navegación")
        selected_display = st.selectbox("Seleccionar página", display_labels, index=display_labels.index(current_display), label_visibility="hidden")
        # Sync canonical value into session_state for the router
        st.session_state[page_key] = display_to_canonical.get(selected_display, "Inicio")
        selected = st.session_state[page_key]

        st.markdown("---")
        st.subheader("Filtros Globales")

        # Cargar datos con feedback visual y manejo de errores explícito
        cuentas = pd.DataFrame()
        metricas = pd.DataFrame()
        status = st.status("Validando credenciales...", expanded=False)
        try:
            status.update(label="Sincronizando con Google Sheets...", state="running")
            cuentas, metricas = load_data()
            status.update(label="Calculando tendencias...", state="running")
            status.update(label="Datos listos", state="complete")
        except Exception as e:
            status.update(label="Error al cargar datos", state="error")
            try:
                st.error("Error al cargar datos. Contacte al administrador.")
                st.exception(e)
            except Exception:
                import logging

                logging.exception("Error al mostrar error en Streamlit")
        # Mostrar toast según el origen de los datos (cloud/local)
        try:
            origin = st.session_state.get("data_origin", "local")
            if origin == "cloud":
                try:
                    st.toast("🌐 Conectado a la nube", icon="Ⓜ️")
                except Exception:
                    st.info("🌐 Conectado a la nube")
            else:
                try:
                    st.toast("💾 Usando datos locales (Modo Offline)", icon="Ⓜ️")
                except Exception:
                    st.info("💾 Usando datos locales (Modo Offline)")
        except Exception:
            pass

        # Asegurar que `id_cuenta` sea string en ambos DataFrames antes del merge
        if not cuentas.empty and "id_cuenta" in cuentas.columns:
            cuentas["id_cuenta"] = cuentas["id_cuenta"].astype(str)
        if not metricas.empty and "id_cuenta" in metricas.columns:
            metricas["id_cuenta"] = metricas["id_cuenta"].astype(str)

        # Filtro 1: Institución
        entidades = sorted(cuentas["entidad"].unique().tolist()) if not cuentas.empty else []
        entidad_sel = st.selectbox("Colegio", ["Todas"] + entidades, key="filtro_entidad")

        # Filtro 2: Mes (se mantiene la selección visual aquí, pero NO se aplica
        # como filtro global en el `main`. El dashboard recibirá todo el histórico
        # para poder calcular YoY correctamente).
        if not metricas.empty:
            metricas['fecha'] = pd.to_datetime(metricas['fecha'])
            # Deduplicar metricas por snapshot mensual: mantener solo el último
            # registro por id_cuenta cada mes (último snapshot del mes).
            # Deduplicado eficiente: tomar el snapshot más reciente por id_cuenta y mes
            if 'id_cuenta' in metricas.columns and 'fecha' in metricas.columns:
                metricas['fecha'] = pd.to_datetime(metricas['fecha'], errors='coerce')
                metricas['period'] = metricas['fecha'].dt.to_period('M')  # type: ignore
                try:
                    idx = metricas.groupby(['id_cuenta', 'period'], sort=False)['fecha'].idxmax()
                    metricas = (
                        metricas.loc[idx.dropna()]
                        .drop(columns=['period'])
                        .reset_index(drop=True)
                    )
                except Exception as e:
                    try:
                        st.warning(f"No fue posible deduplicar métricas por mes: {e}")
                    except Exception:
                        import logging

                        logging.exception("No fue posible mostrar warning de dedup")

            meses = sorted(metricas["fecha"].dt.strftime("%Y-%m").unique(), reverse=True)  # type: ignore
            mes_sel = st.selectbox("Periodo", meses, key="filtro_mes")

        # Botón de Reset Filtros
        if st.button("Reset Filtros", help="Limpia los filtros y devuelve a 'Todos los Colegios'"):
            if "filtro_entidad" in st.session_state:
                del st.session_state["filtro_entidad"]
            if "filtro_mes" in st.session_state:
                del st.session_state["filtro_mes"]
            st.rerun()

        st.divider()
        st.caption("v2.1.0 • Maristas")

    # --- Lógica de Filtrado Centralizada ---
    df_filtrado = None
    if not metricas.empty and not cuentas.empty:
        # Merge robusto: `id_cuenta` ya fue coercionado a str arriba
        df_global = pd.merge(metricas, cuentas, on="id_cuenta", how="left")

        # Normalizar columnas resultantes de merges: preferir entidad_y > entidad_x > entidad
        for logical in ("entidad", "plataforma", "usuario_red"):
            if logical in df_global.columns:
                continue
            for suff in (f"{logical}_y", f"{logical}_x", f"{logical}"):
                if suff in df_global.columns:
                    df_global.rename(columns={suff: logical}, inplace=True)
                    break

        # Asegurar tipo datetime para 'fecha' si existe
        if "fecha" in df_global.columns:
            df_global["fecha"] = pd.to_datetime(df_global["fecha"], errors="coerce")

        # Aplicar solo filtro por entidad (drill-down) y mantener TODO el histórico.
        if entidad_sel != "Todas":
            df_filtrado = df_global[df_global["entidad"] == entidad_sel].copy()
        else:
            df_filtrado = df_global.copy()

    # Empty state amigable si no hay datos tras el merge/filtrado
    try:
        if df_filtrado is not None and getattr(df_filtrado, "empty", False):
            st.info("Parece que aún no hay datos para este colegio. ¡Empieza capturando uno!")
    except Exception:
        # No crítico; continuar sin bloquear la app
        pass

    # Router Simple
    if selected == "Inicio":
        landing.render()
    elif selected == "Dashboard Global":
        dashboard.render(df_filtrado)
    elif selected == "Comparativas":
        analytics.render(df_filtrado)
    elif selected == "Captura":
        data_entry.render(df_filtrado)
    elif selected == "Configuración":
        settings.render()
    else:
        landing.render()


if __name__ == "__main__":
    main()
