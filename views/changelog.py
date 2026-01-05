"""
Vista de Historial de Versiones y Roadmap para CHAMPILYTICS.
Muestra el changelog completo con filtros y búsqueda, más el roadmap de desarrollo.
"""

import streamlit as st
from pathlib import Path
import re


def render(df=None):
    """Renderiza la vista de historial de versiones y roadmap.

    Firma compatible para aceptar un `df` aunque no se utilice.
    """
    st.title("📋 DOCUMENTACIÓN DEL PROYECTO")
    st.caption("Historial de versiones, roadmap de desarrollo y progreso actual")

    # Tabs principales
    tab_changelog, tab_roadmap = st.tabs(
        ["📝 Historial de Versiones", "🗺️ Roadmap de Desarrollo"]
    )

    # ===========================
    # TAB 1: CHANGELOG
    # ===========================
    with tab_changelog:
        render_changelog()

    # ===========================
    # TAB 2: ROADMAP
    # ===========================
    with tab_roadmap:
        render_roadmap()


def render_changelog():
    """Renderiza solo el changelog."""
    st.markdown("### 📜 Registro de Cambios")

    # Leer el archivo CHANGELOG.md
    changelog_path = Path(__file__).parent.parent / "CHANGELOG.md"

    if not changelog_path.exists():
        st.error("❌ No se encontró el archivo CHANGELOG.md")
        st.info("💡 El archivo debería estar en la raíz del proyecto")
        return

    try:
        with open(changelog_path, "r", encoding="utf-8") as f:
            changelog_content = f.read()
    except Exception as e:
        st.error(f"❌ Error al leer el changelog: {e}")
        return

    # Extraer versiones para el filtro
    import re

    version_pattern = r"## \[(\d+\.\d+\.\d+)\]"
    versions = re.findall(version_pattern, changelog_content)

    # Controles de filtrado
    st.markdown("---")
    col1, col2, col3 = st.columns([2, 2, 1])

    with col1:
        filter_version = st.selectbox(
            "Filtrar por versión",
            ["Todas las versiones"] + versions,
            key="version_filter",
        )

    with col2:
        search_term = st.text_input(
            "Buscar en el historial",
            placeholder="Ej: benchmarking, KPI, gráfica...",
            key="search_term",
        )

    with col3:
        st.markdown("<br>", unsafe_allow_html=True)
        show_roadmap = st.checkbox("Mostrar Roadmap", value=False)

    st.markdown("---")

    # Procesar y mostrar contenido
    if search_term:
        # Filtrar por término de búsqueda
        lines = changelog_content.split("\n")
        filtered_lines = []
        in_relevant_section = False

        for line in lines:
            if search_term.lower() in line.lower():
                in_relevant_section = True
                filtered_lines.append(line)
            elif line.startswith("##") and in_relevant_section:
                in_relevant_section = False
                filtered_lines.append(line)
            elif in_relevant_section:
                filtered_lines.append(line)

        content_to_show = "\n".join(filtered_lines)

        if not filtered_lines:
            st.warning(f"🔍 No se encontraron resultados para '{search_term}'")
            content_to_show = changelog_content

    elif filter_version != "Todas las versiones":
        # Filtrar por versión específica
        pattern = f"## \\[{re.escape(filter_version)}\\].*?(?=## \\[|$)"
        match = re.search(pattern, changelog_content, re.DOTALL)

        if match:
            content_to_show = f"# 📝 Historial de Cambios\n\n{match.group()}"
        else:
            st.warning(f"⚠️ No se encontró la versión {filter_version}")
            content_to_show = changelog_content

    else:
        content_to_show = changelog_content

    # Ocultar roadmap si está desactivado
    if not show_roadmap:
        roadmap_index = content_to_show.find("## Roadmap")
        if roadmap_index != -1:
            content_to_show = content_to_show[:roadmap_index]

    # Renderizar contenido
    st.markdown(content_to_show, unsafe_allow_html=False)

    # Información adicional
    st.markdown("---")
    st.markdown("### 📊 Estadísticas del Proyecto")

    col_a, col_b, col_c = st.columns(3)

    with col_a:
        total_versions = len(versions)
        st.metric("Versiones Publicadas", total_versions)

    with col_b:
        # Contar tipos de cambios
        features_count = changelog_content.count("✨ Agregado")
        st.metric("Nuevas Funcionalidades", features_count)

    with col_c:
        fixes_count = changelog_content.count("🐛 Corregido")
        st.metric("Correcciones de Bugs", fixes_count)

    # Sección de descarga
    st.markdown("---")
    st.markdown("### 📥 Exportar Historial")

    col_download_1, col_download_2 = st.columns(2)

    with col_download_1:
        st.download_button(
            label="📄 Descargar Changelog Completo (MD)",
            data=changelog_content,
            file_name="CHAMPILYTICS_Changelog.md",
            mime="text/markdown",
            width="stretch",
        )

    with col_download_2:
        # Convertir a texto plano sin markdown
        plain_text = re.sub(r"[#*`\[\]]", "", changelog_content)
        st.download_button(
            label="📝 Descargar como Texto Plano (TXT)",
            data=plain_text,
            file_name="CHAMPILYTICS_Changelog.txt",
            mime="text/plain",
            width="stretch",
        )

    # Footer informativo
    st.markdown("---")
    st.info("""
    **ℹ️ Sobre el Versionado Semántico**
    
    Este proyecto sigue el estándar [Semantic Versioning 2.0.0](https://semver.org/lang/es/):
    
    - **MAJOR** (X.0.0): Cambios incompatibles en la API
    - **MINOR** (x.Y.0): Nueva funcionalidad compatible hacia atrás
    - **PATCH** (x.y.Z): Correcciones de bugs compatibles
    """)


def render_roadmap():
    """Renderiza el roadmap de desarrollo con cálculo automático de progreso."""
    st.markdown("### 🗺️ Hoja de Ruta del Proyecto")

    # Leer el archivo ROADMAP.md
    roadmap_path = Path(__file__).parent.parent / "ROADMAP.md"

    if not roadmap_path.exists():
        st.error("❌ No se encontró el archivo ROADMAP.md")
        st.info("💡 El archivo debería estar en la raíz del proyecto")
        return

    try:
        with open(roadmap_path, "r", encoding="utf-8") as f:
            roadmap_content = f.read()
    except Exception as e:
        st.error(f"❌ Error al leer el roadmap: {e}")
        return

    # Calcular progreso global automáticamente
    total_tasks = roadmap_content.count("- [")
    completed_tasks = roadmap_content.count("- [x]")
    progress_percentage = (
        (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
    )

    # Header con métricas globales
    st.markdown("---")
    col_a, col_b, col_c, col_d = st.columns(4)

    with col_a:
        st.metric("📊 Progreso Global", f"{progress_percentage:.1f}%")

    with col_b:
        st.metric("✅ Tareas Completadas", completed_tasks)

    with col_c:
        st.metric("📋 Tareas Totales", total_tasks)

    with col_d:
        st.metric("⏳ Tareas Pendientes", total_tasks - completed_tasks)

    # Barra de progreso global
    st.progress(progress_percentage / 100)

    st.markdown("---")

    # Extraer sprints y calcular progreso individual
    sprint_pattern = r"## (.+?Sprint \d+:.+?)\n\*\*Status\*\*: (.+?)\n.*?(?=##|$)"
    sprints = re.findall(sprint_pattern, roadmap_content, re.DOTALL)

    # Mostrar resumen de sprints con lógica de colores
    st.markdown("### 📊 Estado de los Sprints")

    for sprint_full_text in re.finditer(
        r"## (.+?Sprint \d+:.+?)\n\*\*Status\*\*: (.+?) \*\*(.+?)\*\*.*?\n(.*?)(?=##|---|\Z)",
        roadmap_content,
        re.DOTALL,
    ):
        sprint_title = sprint_full_text.group(1).strip()
        status_emoji = sprint_full_text.group(2).strip()
        status_text = sprint_full_text.group(3).strip()
        sprint_content = sprint_full_text.group(4)

        # Calcular progreso del sprint
        sprint_total = sprint_content.count("- [")
        sprint_completed = sprint_content.count("- [x]")
        sprint_progress = (
            (sprint_completed / sprint_total * 100) if sprint_total > 0 else 0
        )

        # Ordenar tareas por estado (rojo, amarillo, verde)
        tasks = re.findall(
            r"- \[([ x])\] \*\*(.+?)\*\*:(.+?)(?=\n-|\n\n|$)", sprint_content, re.DOTALL
        )
        sorted_tasks = sorted(tasks, key=lambda t: (t[0] == " ", t[0] == "x"))

        # Expandible por sprint
        with st.expander(
            f"{status_emoji} {sprint_title} — {sprint_progress:.0f}%",
            expanded=(status_emoji == "🟡"),
        ):
            # Barra de progreso del sprint
            st.progress(sprint_progress / 100)
            st.caption(f"**{status_text}** • {sprint_completed}/{sprint_total} tareas")

            # Mostrar tareas del sprint con colores
            for checked, task_name, task_desc in sorted_tasks:
                is_done = checked == "x"
                checkbox_emoji = "✅" if is_done else ("🟡" if checked == " " else "🔴")
                st.markdown(
                    f"{checkbox_emoji} **{task_name.strip()}**: {task_desc.strip()}"
                )

    st.markdown("---")

    # Sección de prioridades actuales
    st.markdown("### 🎯 Prioridades Actuales")

    priority_section = re.search(
        r"## 🎯 Prioridades Actuales.*?\n(.*?)(?=##|---|\Z)", roadmap_content, re.DOTALL
    )
    if priority_section:
        st.markdown(priority_section.group(1))

    st.markdown("---")

    # Contenido completo en expandible
    with st.expander("📄 Ver Roadmap Completo", expanded=False):
        st.markdown(roadmap_content)

    # Botón de descarga
    st.markdown("---")
    st.markdown("### 📥 Exportar Roadmap")

    st.download_button(
        label="📊 Descargar Roadmap Completo (MD)",
        data=roadmap_content,
        file_name="CHAMPILYTICS_Roadmap.md",
        mime="text/markdown",
        use_container_width=True,
    )

    # Footer informativo
    st.markdown("---")
    st.info("""
    **ℹ️ Sobre la Metodología Ágil**

    Este proyecto sigue sprints de 2 semanas con objetivos claros y entregas incrementales.

    - **Sprint**: Ciclo de desarrollo de 2 semanas
    - **Backlog**: Lista priorizada de funcionalidades pendientes
    - **Retrospectiva**: Al final de cada sprint se evalúa qué mejorar

    El progreso se actualiza automáticamente al marcar tareas como completadas en `ROADMAP.md`.
    """)
