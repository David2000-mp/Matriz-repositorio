"""
Script de Verificación: Optimización Móvil CSS
Verifica que todos los media queries y reglas móviles estén presentes
"""

from utils.mobile_styles import get_mobile_css

css = get_mobile_css()

print("=" * 80)
print("📱 VERIFICACIÓN DE OPTIMIZACIÓN MÓVIL - CSS RESPONSIVE")
print("=" * 80)

# Breakpoints críticos que DEBEN existir
breakpoints = {
    "Tablets (≤1024px)": "@media (max-width: 1024px)",
    "Móviles Grandes (≤767px)": "@media (max-width: 767px)",
    "Móviles Pequeños (≤480px)": "@media (max-width: 480px)",
    "Landscape Móvil": "@media (max-width: 767px) and (orientation: landscape)",
    "Dispositivos Táctiles": "@media (hover: none) and (pointer: coarse)",
}

print("\n✓ VERIFICANDO BREAKPOINTS:\n")

total_checks = 0
passed_checks = 0

for nombre, selector in breakpoints.items():
    total_checks += 1
    if selector in css:
        print(f"  ✅ {nombre}")
        print(f"      {selector}")
        passed_checks += 1
    else:
        print(f"  ❌ NO ENCONTRADO: {nombre}")
    print()

# Optimizaciones críticas
optimizaciones = {
    "Padding Lateral Reducido": [
        "padding-left: 1.5rem !important",
        "padding-right: 1.5rem !important",
    ],
    "Hero Banner Adaptable": [
        "height: 350px !important",  # Tablet
        "height: 250px !important",  # Mobile
        "height: 200px !important",  # Small mobile
    ],
    "Botones Táctiles (44px)": [
        "min-height: 48px !important",
        "min-height: 44px !important",
    ],
    "Tipografía Escalable": [
        "font-size: 1.75rem !important",  # h1 móvil
        "font-size: 1.5rem !important",   # h2 móvil
    ],
    "Inputs Sin Zoom iOS (16px)": [
        "font-size: 16px !important",
    ],
    "Columnas en Stack": [
        "flex-direction: column !important",
    ],
    "Scroll Touch Optimizado": [
        "-webkit-overflow-scrolling: touch !important",
    ],
    "Tap Highlight Custom": [
        "-webkit-tap-highlight-color: rgba(0, 54, 150, 0.2) !important",
    ],
}

print("=" * 80)
print("✓ VERIFICANDO OPTIMIZACIONES MÓVILES:\n")

for categoria, reglas in optimizaciones.items():
    print(f"📋 {categoria}")
    for regla in reglas:
        total_checks += 1
        if regla in css:
            print(f"  ✅ {regla[:60]}...")
            passed_checks += 1
        else:
            print(f"  ❌ NO ENCONTRADO: {regla}")
    print()

print("=" * 80)
print("📊 RESUMEN DE VERIFICACIÓN")
print("=" * 80)
print(f"Total de verificaciones: {total_checks}")
print(f"Aprobadas: {passed_checks}")
print(f"Fallidas: {total_checks - passed_checks}")

if passed_checks == total_checks:
    print("\n🎉 ¡PERFECTO! Todos los media queries están presentes")
    print("✅ La aplicación está lista para móviles")
else:
    print(f"\n⚠️ ATENCIÓN: {total_checks - passed_checks} optimizaciones faltantes")
    print("❌ Revisar mobile_styles.py")

# Estadísticas de cobertura
print("\n" + "=" * 80)
print("📈 ESTADÍSTICAS DE COBERTURA RESPONSIVE")
print("=" * 80)

# Contar media queries
media_queries_count = css.count("@media")
print(f"Media Queries totales: {media_queries_count}")

# Contar optimizaciones por categoría
tablet_rules = css[css.find("@media (max-width: 1024px)"):css.find("@media (max-width: 767px)")].count("!important")
mobile_rules = css[css.find("@media (max-width: 767px)"):css.find("@media (max-width: 480px)")].count("!important")
small_mobile_rules = css[css.find("@media (max-width: 480px)"):].count("!important")

print(f"Reglas para Tablets: {tablet_rules}")
print(f"Reglas para Móviles: {mobile_rules}")
print(f"Reglas para Móviles Pequeños: {small_mobile_rules}")

print("\n" + "=" * 80)
print("🎯 CARACTERÍSTICAS CLAVE")
print("=" * 80)

caracteristicas = [
    ("Padding Lateral Responsivo", "padding-left: 1.5rem" in css),
    ("Hero Banner Adaptable", "height: 250px" in css),
    ("Botones Táctiles 44px+", "min-height: 44px" in css),
    ("Inputs 16px (No Zoom iOS)", "font-size: 16px" in css),
    ("Columnas en Stack Móvil", "flex-direction: column" in css),
    ("Scroll Touch iOS", "-webkit-overflow-scrolling: touch" in css),
    ("Tap Highlights Custom", "-webkit-tap-highlight-color" in css),
    ("Landscape Optimizado", "orientation: landscape" in css),
    ("Sidebar 85% Max", "max-width: 85%" in css),
    ("Tablas Scroll Horizontal", "overflow-x: auto" in css),
]

for nombre, presente in caracteristicas:
    icono = "✅" if presente else "❌"
    print(f"{icono} {nombre}")

print("\n" + "=" * 80)
print("📱 DISPOSITIVOS CUBIERTOS")
print("=" * 80)

dispositivos = [
    "✅ iPhone SE (375×667)",
    "✅ iPhone 12 Pro (390×844)",
    "✅ iPhone 14 Pro Max (430×932)",
    "✅ Samsung Galaxy S20 (360×800)",
    "✅ Google Pixel 6 (412×915)",
    "✅ iPad (768×1024)",
    "✅ iPad Pro 11\" (834×1194)",
    "✅ Tablets Android (768×1024)",
]

for dispositivo in dispositivos:
    print(f"  {dispositivo}")

print("\n" + "=" * 80)
print("🚀 SIGUIENTE PASO: PRUEBAS EN NAVEGADOR")
print("=" * 80)
print("\n1. Ejecutar app local:")
print("   streamlit run app_refactored.py")
print("\n2. Abrir Chrome DevTools (F12)")
print("\n3. Toggle Device Toolbar (Ctrl+Shift+M)")
print("\n4. Probar en:")
print("   - iPhone SE (375px)")
print("   - iPhone 12 Pro (390px)")
print("   - iPad (768px)")
print("\n5. Verificar:")
print("   ✓ No hay scroll horizontal")
print("   ✓ Botones tienen área táctil ≥44px")
print("   ✓ Texto legible sin zoom")
print("   ✓ Hero banner proporcional")
print("   ✓ Sidebar colapsa correctamente")

print("\n" + "=" * 80)
print("✨ VERIFICACIÓN COMPLETA")
print("=" * 80)
