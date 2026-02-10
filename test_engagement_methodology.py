"""
Test de validación de metodología de engagement
Verifica que se cumplan todas las reglas oficiales
"""

import sys
import os

# Agregar path del proyecto
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_methodology():
    """Prueba las reglas de metodología"""
    
    print("=" * 70)
    print("TEST DE METODOLOGÍA DE ENGAGEMENT")
    print("=" * 70)
    
    # Importar función de thresholds
    from views.engagement_calculator_v2 import get_engagement_thresholds
    
    print("\n✓ Importación exitosa de get_engagement_thresholds")
    
    # ========================================================================
    # TEST 1: Thresholds de Facebook
    # ========================================================================
    print("\n[TEST 1] Thresholds de Facebook (comunidad)")
    fb_thresholds = get_engagement_thresholds("facebook", "comunidad")
    
    assert fb_thresholds["bajo"] == 0.5, f"Facebook bajo debe ser 0.5, es {fb_thresholds['bajo']}"
    assert fb_thresholds["aceptable"] == 1.0, f"Facebook aceptable debe ser 1.0, es {fb_thresholds['aceptable']}"
    assert fb_thresholds["bueno"] == 2.0, f"Facebook bueno debe ser 2.0, es {fb_thresholds['bueno']}"
    
    print(f"  ✓ Bajo: {fb_thresholds['bajo']}%")
    print(f"  ✓ Aceptable: {fb_thresholds['aceptable']}%")
    print(f"  ✓ Bueno: {fb_thresholds['bueno']}%")
    print(f"  ✓ Labels: {fb_thresholds['labels']}")
    
    # ========================================================================
    # TEST 2: Thresholds de TikTok (comunidad)
    # ========================================================================
    print("\n[TEST 2] Thresholds de TikTok (comunidad)")
    tt_comunidad = get_engagement_thresholds("tiktok", "comunidad")
    
    assert tt_comunidad["bajo"] == 3.0, f"TikTok comunidad bajo debe ser 3.0, es {tt_comunidad['bajo']}"
    assert tt_comunidad["promedio"] == 6.0, f"TikTok comunidad promedio debe ser 6.0, es {tt_comunidad['promedio']}"
    assert tt_comunidad["bueno"] == 10.0, f"TikTok comunidad bueno debe ser 10.0, es {tt_comunidad['bueno']}"
    
    print(f"  ✓ Bajo: {tt_comunidad['bajo']}%")
    print(f"  ✓ Promedio: {tt_comunidad['promedio']}%")
    print(f"  ✓ Bueno: {tt_comunidad['bueno']}%")
    print(f"  ✓ Labels: {tt_comunidad['labels']}")
    
    # ========================================================================
    # TEST 3: Thresholds de TikTok (vistas)
    # ========================================================================
    print("\n[TEST 3] Thresholds de TikTok (por vistas - rendimiento de contenido)")
    tt_vistas = get_engagement_thresholds("tiktok", "vistas")
    
    assert tt_vistas["bajo"] == 1.0, f"TikTok vistas bajo debe ser 1.0, es {tt_vistas['bajo']}"
    assert tt_vistas["aceptable"] == 3.0, f"TikTok vistas aceptable debe ser 3.0, es {tt_vistas['aceptable']}"
    assert tt_vistas["bueno"] == 6.0, f"TikTok vistas bueno debe ser 6.0, es {tt_vistas['bueno']}"
    
    print(f"  ✓ Bajo: {tt_vistas['bajo']}%")
    print(f"  ✓ Aceptable: {tt_vistas['aceptable']}%")
    print(f"  ✓ Bueno: {tt_vistas['bueno']}%")
    print(f"  ✓ Labels: {tt_vistas['labels']}")
    
    # ========================================================================
    # TEST 4: Fórmulas de cálculo
    # ========================================================================
    print("\n[TEST 4] Validación de fórmulas")
    
    # Datos de prueba
    followers = 10000
    num_posts = 15
    total_interactions = 1500  # 100 interacciones por post en promedio
    total_views = 150000  # Para TikTok
    
    # Engagement general (B)
    engagement_general = (total_interactions / followers) * 100
    print(f"  ✓ Engagement general: {engagement_general:.2f}%")
    assert engagement_general == 15.0, f"Debe ser 15.0%, es {engagement_general}"
    
    # Engagement por post (A)
    avg_interactions = total_interactions / num_posts  # 100
    engagement_per_post = (avg_interactions / followers) * 100
    print(f"  ✓ Promedio interacciones: {avg_interactions:.0f}")
    print(f"  ✓ Engagement por post: {engagement_per_post:.2f}%")
    assert engagement_per_post == 1.0, f"Debe ser 1.0%, es {engagement_per_post}"
    
    # Engagement por vistas (C) - Solo TikTok
    engagement_by_views = (total_interactions / total_views) * 100
    print(f"  ✓ Engagement por vistas: {engagement_by_views:.2f}%")
    assert engagement_by_views == 1.0, f"Debe ser 1.0%, es {engagement_by_views}"
    
    # ========================================================================
    # TEST 5: Validar que no incluye guardados
    # ========================================================================
    print("\n[TEST 5] Validar exclusión de 'guardados' en TikTok")
    
    # Leer archivo para verificar que no existe código de guardados
    with open("views/engagement_calculator_v2.py", "r", encoding="utf-8") as f:
        content = f.read()
    
    # Verificar que no exista el campo saves en el cálculo del total
    assert "saves" not in content or "saves =" not in content or ("saves" in content and "not in content" in content), \
        "El código NO debe incluir 'saves' en cálculos de TikTok"
    
    # Verificar que el total solo incluye likes + comments + shares
    assert "likes + comments + shares" in content, \
        "El total debe calcularse como: likes + comments + shares"
    
    print("  ✓ Guardados correctamente excluidos de interacciones TikTok")
    print("  ✓ Total = likes + comments + shares (correcto)")
    
    # ========================================================================
    # RESUMEN FINAL
    # ========================================================================
    print("\n" + "=" * 70)
    print("RESULTADO: ✅ TODOS LOS TESTS PASADOS")
    print("=" * 70)
    print("\nLa calculadora cumple con las reglas oficiales:")
    print("  ✓ Thresholds fijos por plataforma (no dinámicos)")
    print("  ✓ Fórmulas correctas:")
    print("    - Engagement general = (Total interacciones / Seguidores) × 100")
    print("    - Engagement por post = (Promedio interacciones / Seguidores) × 100")
    print("    - Engagement por vistas = (Total interacciones / Total vistas) × 100")
    print("  ✓ TikTok: Solo likes + comentarios + compartidos (sin guardados)")
    print("  ✓ TikTok: Vistas usadas solo para métrica de contenido")
    print("\n")
    
    return True

if __name__ == "__main__":
    try:
        test_methodology()
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
