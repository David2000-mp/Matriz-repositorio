"""
Test: Verificar cálculos en calculadora de engagement
- Posts por semana basado en días
- Porcentaje y engagement promedio por tipo de contenido
"""

# Simular datos de engagment
num_posts = 15
days = 30
followers = 2500

# Simular posts mixtos (videos e imágenes)
posts = [
    {"type": "🎥 Video", "interactions": 200},
    {"type": "🎥 Video", "interactions": 180},
    {"type": "🎥 Video", "interactions": 150},
    {"type": "📸 Imagen", "interactions": 80},
    {"type": "📸 Imagen", "interactions": 75},
    {"type": "📸 Imagen", "interactions": 90},
    {"type": "📸 Imagen", "interactions": 60},
    {"type": "📸 Imagen", "interactions": 70},
    {"type": "📹 Carrusel", "interactions": 120},
    {"type": "📹 Carrusel", "interactions": 140},
    {"type": "📹 Carrusel", "interactions": 110},
    {"type": "📹 Carrusel", "interactions": 100},
    {"type": "🎥 Video", "interactions": 0},
    {"type": "📸 Imagen", "interactions": 0},
    {"type": "📹 Carrusel", "interactions": 0},
]

print("=" * 80)
print("TEST: Calculadora de Engagement v2")
print("=" * 80)

# Calcular totales
total_interactions = sum(p["interactions"] for p in posts)
print(f"\n📊 DATOS INGRESADOS:")
print(f"  Posts: {num_posts}")
print(f"  Días: {days}")
print(f"  Seguidores: {followers:,}")
print(f"  Total interacciones: {total_interactions}")

# Engagement general
engagement_pct = (total_interactions / followers) * 100
avg_interactions = total_interactions / num_posts
engagement_per_post = (avg_interactions / followers) * 100
posts_per_week = (num_posts / days) * 7

print(f"\n✅ CÁLCULOS PRINCIPALES:")
print(f"  Engagement general: {engagement_pct:.2f}%")
print(f"  Engagement promedio/post: {engagement_per_post:.2f}%")
print(f"  Posts por semana ({num_posts}/{days}*7): {posts_per_week:.2f}")

# Análisis por tipo
content_stats = {}
for post in posts:
    ctype = post["type"]
    if ctype not in content_stats:
        content_stats[ctype] = {
            "total_interactions": 0,
            "posts": 0,
            "pct": 0,
            "avg_engagement": 0
        }
    content_stats[ctype]["total_interactions"] += post["interactions"]
    content_stats[ctype]["posts"] += 1

# Calcular porcentajes y engagement
for ctype in content_stats:
    posts_count = content_stats[ctype]["posts"]
    content_stats[ctype]["pct"] = (posts_count / num_posts) * 100
    content_stats[ctype]["avg_engagement"] = (content_stats[ctype]["total_interactions"] / posts_count / followers) * 100

print(f"\n📊 ANÁLISIS POR TIPO DE CONTENIDO:")
print("-" * 80)
for ctype, stats in sorted(content_stats.items(), key=lambda x: x[1]["avg_engagement"], reverse=True):
    pct = stats["pct"]
    eng = stats["avg_engagement"]
    posts = stats["posts"]
    interactions = stats["total_interactions"]
    print(f"  {ctype}:")
    print(f"    - Posts: {posts} ({pct:.0f}% del total)")
    print(f"    - Interacciones totales: {interactions}")
    print(f"    - Engagement promedio/post: {eng:.2f}%")
    print()

# Encontrar mejor tipo
best_type = sorted(content_stats.items(), key=lambda x: x[1]["avg_engagement"], reverse=True)[0]
print(f"⭐ MEJOR RENDIMIENTO:")
print(f"  Tipo: {best_type[0]}")
print(f"  Engagement promedio: {best_type[1]['avg_engagement']:.2f}% por post")
print(f"  Representa el {int(best_type[1]['pct'])}% de tu contenido")
print(f"  Es {best_type[1]['avg_engagement']/engagement_per_post:.1f}x más efectivo que tu promedio")

print("\n" + "=" * 80)
print("✅ TEST COMPLETADO")
print("=" * 80)
