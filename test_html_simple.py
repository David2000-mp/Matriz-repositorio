#!/usr/bin/env python3
"""Test simple de HTML"""

# Simular datos
total_seguidores = 236
delta_pct = 0
breakdown_text = "Facebook: 236"
banner_css = "background: #fff;"
delta_text = ""

# HTML sin indentación inicial (como en landing.py corregido)
html_code = f"""<div class="hero-banner" style="{banner_css}">
    <div class="hero-content">
        <h1>CHAMPILEAKS</h1>
        <div class="followers-counter">{total_seguidores:,}</div>
        <div class="followers-delta">{delta_text}</div>
        <div class="followers-breakdown">{breakdown_text}</div>
        <div class="followers-label">Seguidores Totales Red Marista</div>
    </div>
</div>"""

print("HTML Generado:")
print(html_code)
print("\n" + "=" * 70)
print(f"Etiquetas <div>: {html_code.count('<div')}")
print(f"Etiquetas </div>: {html_code.count('</div>')}")
print("=" * 70)

if html_code.count('<div') == html_code.count('</div>'):
    print("✅ ESTRUCTURA BALANCEADA")
else:
    print("❌ ERROR: Estructura desbalanceada")

# Verificar que no haya indentación inicial problemática
if html_code.startswith('<div'):
    print("✅ Sin espacios iniciales (correcto para Streamlit)")
else:
    print("⚠️  Tiene espacios/saltos de línea iniciales")
