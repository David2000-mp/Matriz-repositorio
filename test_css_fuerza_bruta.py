"""
Script de verificación: Fuerza Bruta CSS para Streamlit Cloud
Verifica que todos los selectores críticos estén presentes
"""

from utils.theme_styles import get_theme_css

css = get_theme_css()

print("=" * 80)
print("🛡️ VERIFICACIÓN DE FUERZA BRUTA CSS - STREAMLIT CLOUD")
print("=" * 80)

# Selectores críticos que DEBEN existir
selectores_criticos = {
    "Anclaje de Contenido Principal": [
        "div[data-testid=\"stAppViewBlockContainer\"] p",
        "-webkit-font-smoothing: antialiased !important",
        "text-rendering: optimizeLegibility !important",
    ],
    "Blindaje de Widgets": [
        "[data-testid=\"stWidgetLabel\"]",
        "font-weight: 600 !important",
    ],
    "Persistencia entre Menús": [
        "div[data-baseweb=\"tab-panel\"]",
        "[role=\"tabpanel\"]",
    ],
    "Labels de Captura/Configuración": [
        ".stTextInput [data-testid=\"stWidgetLabel\"] p",
        ".stNumberInput [data-testid=\"stWidgetLabel\"] p",
    ],
    "Última Línea de Defensa": [
        "🛡️ ÚLTIMA LÍNEA DE DEFENSA",
        "section[data-testid=\"stMain\"] *:not([data-testid=\"stSidebar\"]",
    ],
    "Anti-Gris": [
        "ANTI-GRIS",
        "opacity: 1 !important",
    ],
}

print("\n✓ VERIFICANDO SELECTORES CRÍTICOS:\n")

total_checks = 0
passed_checks = 0

for categoria, selectores in selectores_criticos.items():
    print(f"📋 {categoria}")
    for selector in selectores:
        total_checks += 1
        if selector in css:
            print(f"  ✅ {selector[:60]}...")
            passed_checks += 1
        else:
            print(f"  ❌ NO ENCONTRADO: {selector}")
    print()

print("=" * 80)
print("📊 RESUMEN")
print("=" * 80)
print(f"Total de verificaciones: {total_checks}")
print(f"Aprobadas: {passed_checks}")
print(f"Fallidas: {total_checks - passed_checks}")

if passed_checks == total_checks:
    print("\n🎉 ¡PERFECTO! Todos los selectores de fuerza bruta están presentes")
    print("✅ La aplicación debería verse IDÉNTICA en local y Streamlit Cloud")
else:
    print(f"\n⚠️ ATENCIÓN: {total_checks - passed_checks} selectores faltantes")
    print("❌ Pueden haber diferencias entre local y cloud")

# Contar reglas de color
print("\n" + "=" * 80)
print("📈 ESTADÍSTICAS DE COLOR")
print("=" * 80)

main_section = css[css.find("BLINDAJE DE CONTENIDO PRINCIPAL"):css.find("=== SIDEBAR")]
color_negro = main_section.count("color: #212529 !important")
color_blanco_sidebar = css[css.find("=== SIDEBAR"):css.find("=== CARDS")].count("color: #FFFFFF")

print(f"Reglas con 'color: #212529' en contenido principal: {color_negro}")
print(f"Reglas con 'color: #FFFFFF' en sidebar: {color_blanco_sidebar}")

print("\n" + "=" * 80)
print("🔍 BLOQUES DE PROTECCIÓN ENCONTRADOS")
print("=" * 80)

bloques = [
    "🔒 BLINDAJE DE CONTENIDO PRINCIPAL (FUERZA BRUTA)",
    "🔒 BLINDAJE DE TABS Y NAVEGACIÓN",
    "🔒 BLINDAJE DE WIDGETS ESPECÍFICOS",
    "🔒 PERSISTENCIA - RE-INYECCIÓN EN CADA RENDER",
    "🛡️ ÚLTIMA LÍNEA DE DEFENSA",
]

for bloque in bloques:
    if bloque in css:
        print(f"✅ {bloque}")
    else:
        print(f"❌ {bloque}")

print("\n" + "=" * 80)
print("✨ VERIFICACIÓN COMPLETA")
print("=" * 80)
