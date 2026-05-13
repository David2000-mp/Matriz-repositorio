#!/usr/bin/env python3
"""
Diagnóstico de clasificación en comentarios REALES del usuario
"""
import sys
sys.path.insert(0, '/content')

from utils.comment_processor import classify_sentiment, normalize_text

# Comentarios REALES del usuario
test_comments = [
    # 1. Negativo: "Que decepción de escuela"
    {
        "text": "Que decepción de escuela, después de haber pasado 3 de mis mejores años de vida con ustedes (generación 75-78 secundaria). PROBLEMAS: 1) Respecto a los trámites, es increíble que no tengan terminal para pagar con tarjeta de crédito los uniformes u otros. Quieren que se haga por transferencia, enviar correo, mostrarlo en ventanilla, etc. etc. Que molestias para los papás. 2) Con respecto a deportes, la razón por la cual me encantó esa escuela, ahora hay que pagar por todo. Además prometen que va nadar y resulta que en todo el ciclo escolar 2022 - 2023 no pudo ir a la alberca ya que la rentan a otra institución u organización y los alumnos no pueden usarla. Entonces no presuman instalaciones que no van a poder usar. 3) No hay clase de música, siendo una herramienta principal de educación integral. 4) Los obligan a comprar boletos para las funciones de teatro, que son parte de la calificación. 5) El peor engaño es cuando dicen que en la materia de actividades deportivas llevará fútbol, voleibol, natación y basquetbol. Resulta que en todo el ciclo escolar 2022 - 2023 no llevó nada de eso al menos que pagara adicional para cada actividad.",
        "expected": "Muy Negativo",
        "key_words": ["decepción", "engaño", "molestias"]
    },
    # 2. Muy Negativo: "Nefasta administración"
    {
        "text": "Alvaro Ruiz Calvillo ya la niña lleva dos años en el colegio y no ha llevado actividad deportiva, dijeron el primer año que llevaría la materia que incluía varias actividades. Ahora se tiene que pagar aproximadamente 11,000 pesos adicionales para que haga alguna actividad. Por eso es que pocos se quieren seguir en la preparatoria. Nefasta administración !!",
        "expected": "Muy Negativo",
        "key_words": ["nefasta"]
    },
    # 3. Muy Negativo: antivalores, soberbia
    {
        "text": "Padres de familia, alumnos, colaboradores, pero sobre todo directivos de la provincia de México deberían de poner un ojo en el Colegio Cervantes Costa Rica en Guadalajara, Jalisco donde el Hno Raúl Fernando Lara Castro ha dejado de lado los valores maristas con su arrogancia, soberbia, dejando atrás sus votos de pobreza, humildad y castidad. Deben de revisar y evaluar constantemente si los directivos y su junta directiva realmente cumplen con la misión y visión de los Hermanos Maristas; ya que de lo contrario es simple mercadotécnica. Justo como sucede en el Colegio Cervantes en estos momentos de parte de su director, coordinadora y personal directivo en general del colegio, donde los antivalores católicos son lo que se vive todos los días. Los maestros estamos hartos del trato que se nos da y como mediante la compra de publicidad quieren hacer creer que los valores maristas se viven en este colegio.",
        "expected": "Muy Negativo",
        "key_words": ["arrogancia", "soberbia", "antivalores", "hartos"]
    },
    # 4. Positivo: "Extraordinaria guía", "orgullosa mamá Marista"
    {
        "text": "Extraordinaria guía para l@s chic@s, soy una orgullosa mamá Marista!!!",
        "expected": "Muy Positivo",
        "key_words": ["extraordinaria", "orgullosa"]
    },
    # 5. Positivo: "Una gran obra"
    {
        "text": "Una gran obra en constante transformación, para el cumplimiento y crecimiento de su Misión. Que la Comunidad de Hermanos Maristas han dado todo por vivir el evangelio al estilo de San Marcenilo Chmpagnat. Todo es una educación integral es decir para el desarrollo óptimo en diferentes áreas que un adolescente requiere para el éxito del hoy y mañana",
        "expected": "Muy Positivo",
        "key_words": ["gran obra", "desarrollo óptimo"]
    }
]

print("\n" + "="*80)
print("DIAGNÓSTICO: Clasificación de Comentarios REALES")
print("="*80)

for i, comment in enumerate(test_comments, 1):
    text = comment["text"]
    expected = comment["expected"]
    key_words = comment["key_words"]
    
    label, score = classify_sentiment(text)
    
    status = "✅" if label == expected else "❌"
    
    print(f"\n[{i}] {status} {expected}")
    print(f"    Predicción: {label} (score={score})")
    print(f"    Palabras clave esperadas: {', '.join(key_words)}")
    print(f"    Texto: {text[:100]}...")

print("\n" + "="*80)
print("ANÁLISIS DE PALABRAS FALTANTES")
print("="*80)

# Palabras que claramente faltan
missing_words = {
    "Muy Negativo": ["decepción", "decepcion", "engaño", "engano", "nefasta", "arrogancia", "soberbia", "antivalores", "hartos"],
    "Muy Positivo": ["extraordinaria", "orgullosa"]
}

print("\nPalabras críticas FALTANTES en diccionarios:")
for sentiment, words in missing_words.items():
    print(f"\n{sentiment}:")
    for word in words:
        print(f"  - {word}")

