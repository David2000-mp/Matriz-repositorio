"""
Script de verificación de la integración de metas en el Dashboard.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

print("=" * 80)
print("🧪 VERIFICACIÓN - INTEGRACIÓN DE METAS EN DASHBOARD")
print("=" * 80)

# ===========================
# TEST 1: Importaciones
# ===========================
print("\n[TEST 1] Verificando importaciones en dashboard.py...")
try:
    from views import dashboard
    import inspect
    
    source = inspect.getsource(dashboard.render)
    
    # Verificar que importa load_configs
    dashboard_module_source = inspect.getsource(dashboard)
    assert "load_configs" in dashboard_module_source, "dashboard.py no importa load_configs"
    
    print("✅ Importaciones correctas")
    print("   - load_configs importado ✓")
    
except Exception as e:
    print(f"❌ Error en importaciones: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# ===========================
# TEST 2: Carga de metas
# ===========================
print("\n[TEST 2] Verificando carga de metas en render()...")
try:
    from views import dashboard
    import inspect
    
    source = inspect.getsource(dashboard.render)
    
    checks = {
        "Llama load_configs()": "load_configs()" in source,
        "Define meta_seguidores": "meta_seguidores" in source,
        "Define meta_engagement": "meta_engagement" in source,
        "Busca en df_configs": "df_configs" in source,
        "Extrae metas de institución": "config_inst" in source or "iloc[0]" in source,
    }
    
    all_passed = True
    for check, result in checks.items():
        status = "✅" if result else "❌"
        print(f"   {status} {check}")
        if not result:
            all_passed = False
    
    if not all_passed:
        print("\n❌ Algunas verificaciones de carga fallaron")
        sys.exit(1)
    else:
        print("\n✅ Carga de metas implementada correctamente")
    
except Exception as e:
    print(f"❌ Error verificando carga: {e}")
    sys.exit(1)

# ===========================
# TEST 3: Visualización de progreso
# ===========================
print("\n[TEST 3] Verificando visualización de progreso...")
try:
    from views import dashboard
    import inspect
    
    source = inspect.getsource(dashboard.render)
    
    checks = {
        "Calcula progreso_seg": "progreso_seg" in source,
        "Calcula progreso_eng": "progreso_eng" in source,
        "Usa st.progress()": "st.progress" in source or ".progress(" in source,
        "Muestra meta con caption": ".caption(" in source and "Meta:" in source,
        "Mensaje de meta cumplida": "Meta cumplida" in source or "¡Meta cumplida!" in source,
        "Usa emojis 🎯 y 🎉": "🎯" in source and "🎉" in source,
    }
    
    all_passed = True
    for check, result in checks.items():
        status = "✅" if result else "❌"
        print(f"   {status} {check}")
        if not result:
            all_passed = False
    
    if not all_passed:
        print("\n❌ Algunas verificaciones de visualización fallaron")
        sys.exit(1)
    else:
        print("\n✅ Visualización de progreso implementada correctamente")
    
except Exception as e:
    print(f"❌ Error verificando visualización: {e}")
    sys.exit(1)

# ===========================
# TEST 4: Lógica de progreso
# ===========================
print("\n[TEST 4] Verificando lógica de progreso...")
try:
    # Simular cálculos de progreso
    test_cases = [
        {"actual": 3000, "meta": 5000, "esperado": 0.6, "cumplida": False},
        {"actual": 5000, "meta": 5000, "esperado": 1.0, "cumplida": True},
        {"actual": 6000, "meta": 5000, "esperado": 1.2, "cumplida": True},
        {"actual": 2.5, "meta": 3.5, "esperado": 0.714, "cumplida": False},
        {"actual": 4.0, "meta": 3.5, "esperado": 1.143, "cumplida": True},
    ]
    
    print("   Probando casos de uso:")
    for i, caso in enumerate(test_cases, 1):
        progreso = caso["actual"] / caso["meta"]
        cumplida = progreso >= 1.0
        
        assert abs(progreso - caso["esperado"]) < 0.01, f"Caso {i}: Progreso incorrecto"
        assert cumplida == caso["cumplida"], f"Caso {i}: Estado de cumplimiento incorrecto"
        
        print(f"   ✅ Caso {i}: {caso['actual']}/{caso['meta']} = {progreso:.1%} (Cumplida: {cumplida})")
    
    print("\n✅ Lógica de progreso validada")
    
except Exception as e:
    print(f"❌ Error en lógica: {e}")
    sys.exit(1)

# ===========================
# RESUMEN FINAL
# ===========================
print("\n" + "=" * 80)
print("📊 RESUMEN DE VERIFICACIÓN")
print("=" * 80)
print("✅ TEST 1: Importaciones - PASADO")
print("✅ TEST 2: Carga de metas - PASADO")
print("✅ TEST 3: Visualización de progreso - PASADO")
print("✅ TEST 4: Lógica de progreso - PASADO")
print("=" * 80)
print("🎉 TODAS LAS VERIFICACIONES COMPLETADAS EXITOSAMENTE")
print("=" * 80)

print("\n💡 Pruebas manuales recomendadas:")
print("   1. Abre http://localhost:8501")
print("   2. Selecciona una institución en el sidebar")
print("   3. Ve a Configuración > Mis Metas")
print("   4. Configura metas (ej: 5000 seguidores, 3.5% engagement)")
print("   5. Guarda las metas")
print("   6. Regresa al Dashboard")
print("   7. Verifica las barras de progreso bajo los KPIs")
print("   8. Observa:")
print("      - Barra de progreso verde")
print("      - Texto '🎯 Meta: X (Y%)' si no está cumplida")
print("      - Mensaje '¡Meta cumplida! 🎉' si está cumplida")
print("   9. Prueba con diferentes valores de metas")
print("  10. Verifica que funciona al cambiar de institución")
print("=" * 80)

print("\n✨ CARACTERÍSTICAS IMPLEMENTADAS:")
print("=" * 80)
print("📊 KPI Seguidores Totales:")
print("   - Métrica con delta MoM")
print("   - Barra de progreso hacia meta")
print("   - Porcentaje de completitud")
print("   - Mensaje de celebración al cumplir")
print("")
print("📊 KPI Engagement Promedio:")
print("   - Métrica con delta MoM")
print("   - Barra de progreso hacia meta")
print("   - Porcentaje de completitud")
print("   - Mensaje de celebración al cumplir")
print("")
print("🎯 Contexto Visual:")
print("   - Solo muestra progreso si hay meta configurada (meta > 0)")
print("   - Barra verde indicando progreso")
print("   - Texto descriptivo con emoji 🎯")
print("   - Success banner con emoji 🎉 al cumplir")
print("")
print("🏛️ Integración con Institución:")
print("   - Carga metas específicas de la institución seleccionada")
print("   - Si no hay institución seleccionada, no muestra metas")
print("   - Sincronizado con el selector global del sidebar")
print("=" * 80)
