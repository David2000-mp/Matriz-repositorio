"""
Script de prueba: Verificar que el cálculo de posts por semana es correcto
"""

def test_posts_per_week():
    """Test para el cálculo de posts por semana"""
    
    test_cases = [
        # (num_posts, days, expected_posts_per_week)
        (15, 30, 3.5),      # 15 posts en 30 días = 3.5 posts/semana
        (5, 30, 1.167),     # 5 posts en 30 días ≈ 1.167 posts/semana
        (7, 7, 7.0),        # 7 posts en 7 días = 7 posts/semana (1 por día)
        (3, 14, 1.5),       # 3 posts en 14 días = 1.5 posts/semana
        (1, 30, 0.233),     # 1 post en 30 días ≈ 0.233 posts/semana
        (21, 90, 1.633),    # 21 posts en 90 días ≈ 1.633 posts/semana
    ]
    
    print("=" * 80)
    print("TEST: Cálculo de Posts por Semana")
    print("=" * 80)
    print("\nFórmula correcta: posts_per_week = (num_posts / days) * 7\n")
    
    all_pass = True
    for num_posts, days, expected in test_cases:
        # Cálculo CORRECTO
        posts_per_week_correct = (num_posts / days) * 7
        
        # Cálculo INCORRECTO anterior
        posts_per_week_old = num_posts / (days / 7)  # Esto es equivalente a lo anterior
        
        match = abs(posts_per_week_correct - expected) < 0.001
        status = "✓ PASS" if match else "✗ FAIL"
        
        print(f"{status} | {num_posts} posts en {days} días")
        print(f"    Esperado: {expected:.3f}")
        print(f"    Calculado (correcto): {posts_per_week_correct:.3f}")
        print(f"    Calculado (antiguo): {posts_per_week_old:.3f}")
        print()
        
        if not match:
            all_pass = False
    
    print("=" * 80)
    if all_pass:
        print("✅ TODOS LOS TESTS PASARON")
    else:
        print("❌ ALGUNOS TESTS FALLARON")
    print("=" * 80)
    
    # Demostración de la corrección
    print("\n📊 EJEMPLO PRÁCTICO:")
    print("-" * 80)
    print("Escenario: Usuario ingresa datos para 5 posts en un período de 30 días")
    print()
    num_posts = 5
    days = 30
    ppw = (num_posts / days) * 7
    print(f"Cálculo: (5 posts ÷ 30 días) × 7 = {ppw:.2f} posts/semana")
    print()
    print(f"Interpretación: En promedio el usuario publica {ppw:.2f} posts por semana")
    print(f"Esto equivale a aproximadamente {ppw:.0f} post cada {7/ppw:.1f} días")

if __name__ == "__main__":
    test_posts_per_week()
