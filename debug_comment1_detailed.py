#!/usr/bin/env python3
"""
Debug detallado con conteo de hits
"""
import sys
sys.path.insert(0, '/content')

from utils.comment_processor import (
    normalize_text, tokenize_spanish, classify_sentiment,
    VERY_NEGATIVE_WORDS, NEGATIVE_WORDS, VERY_POSITIVE_WORDS, POSITIVE_WORDS,
)

comment = "Que decepción de escuela, después de haber pasado 3 de mis mejores años de vida con ustedes (generación 75-78 secundaria). PROBLEMAS: 1) Respecto a los trámites, es increíble que no tengan terminal para pagar con tarjeta de crédito los uniformes u otros. Quieren que se haga por transferencia, enviar correo, mostrarlo en ventanilla, etc. etc. Que molestias para los papás. 2) Con respecto a deportes, la razón por la cual me encantó esa escuela, ahora hay que pagar por todo. Además prometen que va nadar y resulta que en todo el ciclo escolar 2022 - 2023 no pudo ir a la alberca ya que la rentan a otra institución u organización y los alumnos no pueden usarla. Entonces no presuman instalaciones que no van a poder usar. 3) No hay clase de música, siendo una herramienta principal de educación integral. 4) Los obligan a comprar boletos para las funciones de teatro, que son parte de la calificación. 5) El peor engaño es cuando dicen que en la materia de actividades deportivas llevará fútbol, voleibol, natación y basquetbol. Resulta que en todo el ciclo escolar 2022 - 2023 no llevó nada de eso al menos que pagara adicional para cada actividad."

normalized = normalize_text(comment)
tokens = tokenize_spanish(normalized)

# Contar hits
very_negative_hits = [tok for tok in tokens if tok in VERY_NEGATIVE_WORDS]
negative_hits = [tok for tok in tokens if tok in NEGATIVE_WORDS]
very_positive_hits = [tok for tok in tokens if tok in VERY_POSITIVE_WORDS]
positive_hits = [tok for tok in tokens if tok in POSITIVE_WORDS]

print("\n📊 RESUMEN DE HITS:")
print(f"  Very Negative ({len(very_negative_hits)}): {set(very_negative_hits)}")
print(f"  Negative ({len(negative_hits)}): {set(negative_hits)}")
print(f"  Very Positive ({len(very_positive_hits)}): {set(very_positive_hits)}")
print(f"  Positive ({len(positive_hits)}): {set(positive_hits)}")

# Cálculo
score = (2 * len(very_positive_hits) + len(positive_hits)) - (2 * len(very_negative_hits) + len(negative_hits))
print(f"\n📐 CÁLCULO:")
print(f"  weighted_score = (2 * {len(very_positive_hits)} + {len(positive_hits)}) - (2 * {len(very_negative_hits)} + {len(negative_hits)})")
print(f"  weighted_score = {score}")

# Clasificación
label, final_score = classify_sentiment(comment)
print(f"\n🎯 RESULTADO: {label} (score={final_score})")

# Palabras faltantes que debería detectar
print(f"\n❌ PALABRAS QUE FALTAN (están en el texto pero no detectadas):")
missing = set()
for word in ["problemas", "molestias", "engano", "peor", "obligar"]:
    if word in normalized:
        is_very_neg = word in VERY_NEGATIVE_WORDS
        is_neg = word in NEGATIVE_WORDS
        if not is_very_neg and not is_neg:
            missing.add(word)
            print(f"   - '{word}' (está en texto pero NO en diccionarios)")

