#!/usr/bin/env python3
"""Test simple de get_id agnóstico (sin streamlit)"""

import hashlib

def get_id_agnostic(entidad: str, plataforma: str, usuario: str) -> str:
    """Versión simplificada de get_id para testing."""
    u_entidad = str(entidad).strip().lower()
    u_plataforma = str(plataforma).strip().lower()
    
    # Limpiar usuario
    u_usuario = str(usuario).strip()
    
    # Si es URL, extraer username
    if u_usuario.startswith(('http://', 'https://')):
        parts = u_usuario.rstrip('/').split('/')
        if len(parts) > 0:
            u_usuario = parts[-1]
    
    # Si es handle con @, removerlo
    if u_usuario.startswith('@'):
        u_usuario = u_usuario[1:]
    
    # Normalizar
    u_usuario = u_usuario.lower().strip()
    
    # Hash
    unique_str = f"{u_entidad}|{u_plataforma}|{u_usuario}"
    hash_id = hashlib.md5(unique_str.encode()).hexdigest()[:8]
    return str(hash_id)


# Tests
print("=" * 70)
print("TEST: get_id Agnóstico")
print("=" * 70)

# Test 1
id_url = get_id_agnostic("Centro Universitario México", "Facebook", "https://www.facebook.com/maristascum")
id_username = get_id_agnostic("Centro Universitario México", "Facebook", "maristascum")

print("\nTest 1: URL completa vs username limpio")
print(f"  ID URL:      {id_url}")
print(f"  ID username: {id_username}")
print(f"  {'✅ PASS' if id_url == id_username else '❌ FAIL'}")

# Test 2
id_handle = get_id_agnostic("Centro Universitario México", "Instagram", "@maristas_cum")
id_clean = get_id_agnostic("Centro Universitario México", "Instagram", "maristas_cum")

print("\nTest 2: Handle @ vs username")
print(f"  ID handle:   {id_handle}")
print(f"  ID username: {id_clean}")
print(f"  {'✅ PASS' if id_handle == id_clean else '❌ FAIL'}")

# Test 3
id_slash = get_id_agnostic("CUM", "IG", "https://www.instagram.com/maristas_cum/")
id_no_slash = get_id_agnostic("CUM", "IG", "https://www.instagram.com/maristas_cum")

print("\nTest 3: Trailing slash")
print(f"  ID slash:    {id_slash}")
print(f"  ID no slash: {id_no_slash}")
print(f"  {'✅ PASS' if id_slash == id_no_slash else '❌ FAIL'}")

# Test 4: Convergencia
formats = [
    "https://www.facebook.com/maristascum",
    "@maristascum",
    "maristascum",
]
ids = [get_id_agnostic("CUM", "FB", fmt) for fmt in formats]

print("\nTest 4: Convergencia")
for fmt, id_val in zip(formats, ids):
    print(f"  {fmt:45s} -> {id_val}")
print(f"  IDs únicos: {len(set(ids))}")
print(f"  {'✅ PASS - Todos iguales!' if len(set(ids)) == 1 else '❌ FAIL'}")

print("\n" + "=" * 70)
if all([
    id_url == id_username,
    id_handle == id_clean,
    id_slash == id_no_slash,
    len(set(ids)) == 1
]):
    print("[SUCCESS] ✅ get_id es completamente agnóstico!")
else:
    print("[FAIL] ❌ Algunos tests fallaron")
print("=" * 70)
