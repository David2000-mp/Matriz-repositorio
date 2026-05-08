"""Procesamiento de comentarios para carga estandarizada en Google Sheets.

Este modulo convierte texto bruto pegado por el usuario en un DataFrame
estructurado con analisis de sentimiento (5 escalas) y categoria.
"""

from __future__ import annotations

import io
import re
import unicodedata
from datetime import datetime, timezone
from typing import Iterable

import pandas as pd

# Orden de exportacion completa (archivo maestro).
CSV_COLUMN_ORDER = [
    "fecha_carga",
    "fuente",
    "comentario_original",
    "sentimiento_etiqueta",
    "sentimiento_score",
    "categoria",
]

# Orden minimal para carga manual simple en Google Sheets.
CSV_MANUAL_LOAD_ORDER = [
    "comentario_original",
]

# Encabezados por defecto del CSV (se pueden sobrescribir via mapeo).
CSV_HEADERS_DEFAULT = {
    "fecha_carga": "fecha_carga",
    "fuente": "fuente",
    "comentario_original": "comentario_original",
    "sentimiento_etiqueta": "sentimiento_etiqueta",
    "sentimiento_score": "sentimiento_score",
    "categoria": "categoria",
}

SPANISH_STOPWORDS = {
    "a", "al", "algo", "algun", "alguna", "algunas", "alguno", "algunos", "alli", "ambos",
    "ante", "antes", "aquel", "aquella", "aquellas", "aquello", "aquellos", "aqui", "asi",
    "aun", "aunque", "bajo", "cada", "casi", "como", "con", "contra", "cual", "cuales",
    "cualquier", "cuando", "cuanto", "de", "del", "desde", "donde", "dos", "el", "ella",
    "ellas", "ello", "ellos", "en", "entre", "era", "eran", "eres", "es", "esa", "esas",
    "ese", "eso", "esos", "esta", "estaba", "estado", "estais", "estamos", "estan", "estar",
    "estas", "este", "esto", "estos", "fue", "fueron", "ha", "hace", "hacia", "han", "hasta",
    "hay", "la", "las", "le", "les", "lo", "los", "mas", "me", "mi", "mientras", "mis",
    "mucho", "muy", "nada", "ni", "no", "nos", "nosotros", "nuestra", "nuestro", "o", "os",
    "otra", "otras", "otro", "otros", "para", "pero", "poco", "por", "porque", "que", "quien",
    "quienes", "se", "sea", "ser", "si", "siempre", "sin", "sobre", "son", "su", "sus", "tal",
    "tambien", "te", "tener", "tiene", "tienen", "todo", "todos", "tu", "tus", "un", "una",
    "unas", "uno", "unos", "usted", "ustedes", "ya",
}

# NIVEL 5: MUY POSITIVO (Embajadores de Marca)
VERY_POSITIVE_WORDS = {
    "excelente", "increible", "maravilloso", "espectacular", "perfecto", "extraordinario", "brutal",
    "impresionante", "fascinante", "top", "integral", "excelencia", "pedagogico", "calidez",
    "profesionalismo", "joya", "impecable", "recomendadisimo", "pedagogia", "supremo",
    "inmejorable", "asombroso", "ejemplar", "transformador", "humanista", "inspirador", "unico",
    "sobresaliente", "gratitud", "bendicion", "exito", "orgullo", "tradicion", "prestigio", "solido",
    "honesto", "seguro", "confiable", "amor", "dedicacion", "pasion", "entrega", "vocacion",
    "sabiduria", "luz", "guia", "armonia", "plenitud", "crecimiento", "vida", "futuro",
    "esperanza", "impacto", "genial", "epico", "inolvidable", "premium", "elite", "brillante",
    "experto", "dedicado", "carismatico", "empatico", "transparente", "autentico", "leal", "fiel",
    "resiliente", "valiente", "audaz", "creativo", "innovador", "visionario", "culto", "preparado",
    "capaz", "eficiente", "responsable", "comprometido", "moral", "justo", "noble", "bondadoso",
    "generoso", "altruista", "solidario", "inigualable", "extraordinario", "magnifico", "imbatible",
    "insuperable", "sublime", "glorioso", "virtuoso", "humano", "corazon",
}

VERY_POSITIVE_PHRASES = {
    "mi segunda casa", "como en mi casa", "siempre como en mi casa", "me siento como en mi casa",
    "forman con el corazon", "un solo corazon marista", "profesores con verdadera vocacion",
    "la mejor inversion para mis hijos", "excelencia en toda la extension de la palabra",
    "calidez humana inigualable", "ambiente de valores solido",
    "trato personalizado desde el primer dia", "orgulloso de pertenecer a esta institucion",
    "supero mis expectativas", "educacion de vanguardia", "marco mi vida para siempre",
    "humanismo puro", "los mejores anos", "gratitud infinita a los docentes",
    "formacion integral real", "comunidad muy unida", "semillero de lideres",
    "buen recibimiento", "buena educacion", "buenos maestros", "convivir con los papas",
}

POSITIVE_WORDS = {
    "bueno", "bien", "rico", "agradable", "delicioso", "recomendado", "genial", "sabroso", "amable",
    "rapido", "limpio", "correcto", "mejor", "funcional", "util", "atento", "ordenado",
    "puntual", "adecuado", "lindo", "bonito", "comodo", "servicial", "practico", "facil",
    "sencillo", "claro", "directo", "justo", "suficiente", "bastante", "aceptable", "recomendable",
    "estable", "constante", "presente", "activo", "dinamico", "alegre", "divertido", "ameno",
    "interesante", "curioso", "nuevo", "fresco", "moderno", "clasico", "tradicional", "autentico",
    "natural", "sano", "saludable", "balanceado", "equilibrado", "armonico", "estetico", "bienestar",
    "confort", "calidad", "oportuno", "pertinente", "valido", "legitimo", "genuino", "nutritivo",
    "suculento", "apetecible", "artesanal", "cuidado", "detallista", "coherente", "diestro",
    "inteligente", "prudente", "cauteloso", "pulcro", "feliz", "alegria",
    "recibimiento", "convivir", "buenos", "buena", "bueno", "amables", "atencion", "recomienda",
}

POSITIVE_PHRASES = {
    "nivel academico competitivo",
    "maestros muy preparados",
    "ambiente seguro para los ninos",
    "buenas instalaciones en general",
    "atencion rapida en secretaria",
    "cumplen con lo que prometen",
    "clases dinamicas",
    "siempre hay comunicacion",
    "buen seguimiento psicopedagogico",
    "hijo feliz en su escuela",
    "opcion solida en la zona",
    "limpieza constante",
    "eventos bien organizados",
    "personal amable",
    "mantenimiento regular",
    "buen balance entre estudio y deporte",
    "recomienda colegio",
    "recomienda jacona",
}

NEGATIVE_WORDS = {
    "mal", "tardado", "frio", "caro", "decepcionante", "lento", "regular", "malo", "demora",
    "descuidado", "insipido", "ruidoso", "deficiente", "limitado", "escaso", "pobre", "bajo",
    "flojo", "demorado", "atrasado", "impuntual", "confuso", "complejo", "dificil", "pesado",
    "aburrido", "monotono", "gris", "distante", "seco", "tosco", "rudo", "cortante",
    "impaciente", "intolerante", "rigido", "estricto", "costoso", "excesivo", "falta", "carece",
    "necesita", "mejorar", "cambio", "ajuste", "correccion", "revision", "pendiente", "inconcluso",
    "incompleto", "dudoso", "incierto", "inseguro", "inestable", "debil", "fragil", "roto",
    "danado", "manchado", "obsoleto", "molesto", "incomodo", "apretado", "chico", "pequeno",
    "angosto", "oscuro", "sofocante", "simple", "comun", "ordinario", "mediocre", "repetitivo",
    "cansado", "agobiante", "estresante", "presionado", "apurado", "insuficiente", "desorganizado",
    "tedioso", "impersonal", "burocratico", "viejo",
}

NEGATIVE_PHRASES = {
    "mucha tarea y poco aprendizaje",
    "clases muy teoricas",
    "dificil estacionarse a la salida",
    "burocracia para todo",
    "maestros que faltan mucho",
    "instalaciones que necesitan pintura",
    "banos sin papel",
    "cafeteria muy cara",
    "poca sombra en el patio",
    "falta de comunicacion de direccion",
    "coordinacion algo desorganizada",
    "reglas demasiado estrictas",
    "clases aburridas",
    "sistema algo obsoleto",
    "les falta tecnologia",
    "podria mejorar",
    "no me convencio",
    "le falta mucho",
    "servicio regular",
    "atencion deficiente",
    "instalaciones viejas",
}

VERY_NEGATIVE_WORDS = {
    "pesimo", "asco", "horrible", "desastre", "terrible", "inaceptable", "sucio", "fatal",
    "nunca", "jamas", "estafa", "vergonzoso", "robo", "peligroso", "insultante", "insalubre",
    "groseria", "fraude", "mentira", "engano", "negligencia", "peligro", "riesgo", "inseguro",
    "asqueroso", "podrido", "vencido", "prepotente", "despota", "abusivo", "injusto", "carisimo",
    "inaccesible", "ineficiente", "tortuoso", "caotico", "abandono", "ruina", "inservible",
    "basura", "porqueria", "cuidado", "alerta", "denuncia", "demanda", "abogado", "queja",
    "reclamo", "maltrato", "humillacion", "discriminacion", "racismo", "clasismo", "machismo",
    "acoso", "violencia", "panico", "intoxicacion", "crudo", "quemado", "desastroso",
    "catastrofico", "patetico", "lamentable", "indignacion", "traumatico", "cloaca", "ratero",
    "nefasto", "impune", "corrupto", "indignante", "terror", "abusos",
}

VERY_NEGATIVE_PHRASES = {
    "caso de bullying que ignoraron",
    "solo les interesa el dinero",
    "maestros mediocres y groseros",
    "administracion prepotente",
    "instalaciones inseguras",
    "el peor trato que he recibido",
    "no inscriban a sus hijos aqui",
    "fraude con las becas",
    "discriminacion por parte de directivos",
    "pesimo manejo de conflictos",
    "ambiente toxico entre alumnos",
    "secretarias despotas",
    "cero etica profesional",
    "negligencia total",
    "mienten con el nivel de ingles",
    "jamas vuelvo",
    "nunca vuelvo",
    "no vuelvo",
    "muy malo",
    "muy mal",
    "eviten este lugar",
    "no vayan",
    "pobre servicio",
    "lo peor",
    "huyan",
    "pesimo lugar",
    "asco de lugar",
    "peor escuela",
    "fraude total",
    "dinero tirado",
    "tiempo perdido",
    "cero estrellas",
}

# Frases boilerplate de plataformas (Google Maps, Facebook, etc) + escuelas
PLATFORM_BOILERPLATE = {
    "recomienda a",
    "hace un momento",
    "hace unas horas",
    "hace unas minutos",
    "hace un ano",
    "compartir",
    "ver traduccion",
    "calificacion original",
    "recomendado por el",
    "opiniones",
    "clasificacion original",
    "ver en google",
    "respuesta del propietario",
    "calificar",
    "foto de perfil",
    "traducido por google",
    "hace un mes",
    "hace una semana",
    "hace un dia",
    "facebook",
}

# Prioridad de categorias multisectoriales: especificas primero, genericas al final.
# Diseñado para instituciones educativas mexicanas con metricas sociales.
# TIP: marista, humanista, valores → prioritarios en Ambiente/Comunidad
CATEGORY_KEYWORDS = [
    (
        "Academico/Calidad",
        {
            "formacion", "educacion", "pedagogico", "nivel", "aprendizaje", "integral", "programa",
            "metodo", "tareas", "ensenanza", "escuela", "colegio", "maestro", "profesor", "clase",
            "propedeutico", "bilingue", "pensamiento critico", "habilidades blandas",
            "razonamiento logico", "olimpiadas", "feria de ciencias", "lectoescritura", "razonamiento verbal",
            "constructivista", "humanista", "certificaciones internacionales", "nivel de egreso",
            "curriculo enriquecido", "planeacion didactica", "portafolio de evidencias", "evaluacion continua",
            "consejo tecnico", "acreditacion oficial", "validez ante la sep", "docentes", "especialistas",
            "diplomado", "especialidad", "licenciatura", "maestria", "doctorado", "posgrado", "tecnico",
            "carrera", "primaria", "secundaria", "bachillerato", "preparatoria", "preescolar", "inicial",
            "calificacion", "notas", "promedio", "evaluacion", "examen", "acreditacion", "certificacion",
            "retroalimentacion", "tutoria", "asesoria", "biblioteca", "libros", "recursos", "didactica",
            "ciencia", "tecnologia", "innovacion", "investigacion", "proyectos", "tesis", "competencia",
            "desarrollo", "habilidades", "valores", "conocimiento", "rigor", "exigencia",
            "catholico", "religion",
        },
    ),
    (
        "Infraestructura",
        {
            "instalaciones", "edificio", "patio", "banos", "salones", "aula", "alberca", "estacionamiento",
            "clima", "entrada", "fachada", "remodelacion", "espacio", "decoracion", "local",
            "mesa", "sillas", "musica", "parqueadero", "canchas empastadas", "domo deportivo",
            "centro de computo", "laboratorios de quimica", "aula magna", "auditorio equipado",
            "rampas de acceso", "bebederos", "lockers", "talleres de arte", "alberca techada",
            "estancia infantil", "cafeteria saludable", "areas de juegos", "muros perimetrales",
            "circuito cerrado", "zona de pick up", "mobiliario ergonomico", "proyectores inteligentes",
            "red de fibra optica", "laboratorio", "auditorio", "teatro", "foro", "oficinas", "sala juntas",
            "computadoras", "wifi", "internet", "red", "conectividad", "hardware", "software", "equipo",
            "cafeteria", "comedor", "cocina", "agua potable", "drenaje", "plomeria", "seguridad",
            "camaras", "vigilancia", "guardias", "barda", "elevador", "escaleras", "pasillos",
            "aire acondicionado", "calefaccion", "luz", "electricidad", "impermeabilizante", "techo",
            "piso", "ventanas", "cortinas", "persianas", "areas verdes", "plantas", "arboles", "sombra",
            "diseno", "arquitectura", "renovado", "moderno", "funcional",
        },
    ),
    (
        "Precio/Valor",
        {
            "costo", "mensualidad", "colegiatura", "caro", "cara", "barato", "accesible", "beca",
            "precio", "precios", "inscripcion", "inversion", "promocion", "dinero", "economico", "oferta",
            "cuota", "reinscripcion", "credito", "financiamiento", "contado", "meses", "plazos",
            "transferencia", "deposito", "nomina", "apoyo financiero", "descuento", "seguro de orfandad",
            "materiales didacticos", "cuota de padres", "gastos de graduacion", "examen de admision",
            "tramites de titulacion", "reposicion de credencial", "uniformes deportivos", "kit de robotica",
            "plataforma digital", "pago referenciado", "recargos por mora", "descuento por hermanos",
            "convenio empresarial", "inversion educativa", "transparencia de costos", "donativos institucionales",
            "libros", "uniformes", "materiales", "transporte", "ruta", "comedor", "eventos", "viajes",
            "excursiones", "graduacion", "tramites", "titulos", "certificados", "papeleria", "copias",
            "impresiones", "mantenimiento", "recibo", "factura", "adeudo", "intereses", "prorroga",
            "convenio", "anticipado", "efectivo", "tarjeta", "beneficio", "calidad precio", "mercado",
            "competencia", "presupuesto", "estado cuenta", "costo beneficio", "utilidad", "rentabilidad",
            "patrimonio", "finanzas", "administracion", "contabilidad", "tesoreria", "cobranza",
            "vale la pena",
        },
    ),
    (
        "Servicio/Atencion",
        {
            "servicio", "atencion", "personal", "maestros", "profesores", "recepcionista",
            "amabilidad", "trato", "respuesta", "gestion", "tramites", "demora", "rapidez",
            "control escolar", "departamento psicopedagogico", "prefectura", "orientacion educativa",
            "enfermeria escolar", "coordinacion de grado", "secretaria academica", "direccion general",
            "mesa de ayuda", "atencion a padres", "seguimiento de egresados", "admisiones",
            "admisiones y becas", "servicio medico", "vigilancia interna", "brigadas de seguridad",
            "proteccion civil escolar", "directivos", "coordinador", "prefecto", "orientador",
            "psicologo", "medico", "enfermeria", "intendencia", "conserje", "guardia", "vigilancia",
            "transporte", "chofer", "cocina", "cocinero", "mesero", "limpieza", "humanista",
            "camarero", "mesera", "camarera", "secretaria", "asistente", "comunicacion", "informacion",
            "aviso", "circular", "noticia", "evento", "invitacion", "cita", "entrevista", "reunion",
            "junta", "telefono", "correo", "email", "whatsapp", "redes sociales", "mensaje", "chat",
            "bot", "ayuda", "soporte", "queja", "sugerencia", "reclamo", "felicitacion", "buzon",
            "seguimiento", "puntualidad", "asistencia", "presencia", "imagen", "uniforme", "actitud",
            "disposicion", "voluntad", "compromiso", "etica", "profesionalismo", "vocacion",
            "paciencia", "tolerancia", "asertividad", "calidez", "trato humano", "personalizado",
            "escucha", "empatia", "solucion", "problemas", "agilidad", "prontitud", "velocidad",
        },
    ),
    (
        "Ambiente/Comunidad",
        {
            "valores", "familia", "convivencia", "amigos", "marista", "seguridad", "respeto",
            "social", "integracion", "comunidad", "ambiente", "amistad", "compañerismo", "union",
            "fraternidad marista", "pastoral juvenil", "retiros espirituales", "integracion familiar",
            "sana convivencia", "inclusion educativa", "diversidad cultural", "sentido de pertenencia",
            "misiones de semana santa", "voluntariado estudiantil", "kermés anual", "olimpiadas familiares",
            "sociedad de alumnos", "ex alumnos", "valores institucionales", "ambiente libre de acoso",
            "jesuita", "salesiano", "benedictino", "humanista", "jesuitas",
            "claustro", "carisma", "tradicion", "historia", "futuro", "esperanza", "fe", "religion",
            "espiritualidad", "luz", "guia", "armonia", "plenitud", "crecimiento", "vida", "corazon",
            "valores maristas", "corazon de marista", "relacion", "grupo", "equipo", "hermandad",
            "fraternidad", "apoyo mutuo", "inclusion", "diversidad", "equidad", "genero", "paz",
            "alegria", "diversion", "recreacion", "socializacion", "fiestas", "eventos", "kermés",
            "misa", "pastoral", "retiro", "misiones", "servicio social", "voluntariado", "ecologia",
            "sustentabilidad", "conciencia social", "civica", "patriotismo", "moral", "justicia",
            "libertad", "verdad", "integridad", "responsabilidad", "pertenencia", "red", "contactos",
            "networking", "colaboracion", "sinergia", "participacion", "alumnos", "estudiantes",
            "egresados", "alumni", "clima escolar", "bullying", "acoso", "violencia", "discriminacion",
            "confianza", "lealtad", "fidelidad", "liderazgo", "ejemplo", "inspira",
        },
    ),
]

TOKEN_RE = re.compile(r"[a-zA-Z0-9_]+", re.UNICODE)
SYSTEM_ID_PATTERN = re.compile(r"\b[a-z0-9]{5,}\b")


def _detect_system_noise(text: str) -> bool:
    """Detecta ruido de sistema: IDs aleatorios sin suficientes vocales.
    
    Patrones: m63gi9, 606ga6, 7ia4t, rnpSostdeol
    Logica: palabras alphanumericas con <35% vocales = probable ID de sistema.
    """
    words = text.split()
    for word in words:
        if len(word) >= 5 and word.isalnum():
            vowels = sum(1 for c in word.lower() if c in "aeiouáéíóú")
            vowel_ratio = vowels / len(word)
            if vowel_ratio < 0.35:  # Menos del 35% vocales
                return True
    return False


def _detect_platform_boilerplate(text: str) -> bool:
    """Detecta frases boilerplate de Google Maps/Facebook/Instagram.
    
    Descarta frases como: 'recomienda a X', 'estrellas', 'hace un momento'.
    """
    normalized = normalize_text(text)
    for phrase in PLATFORM_BOILERPLATE:
        if phrase in normalized:
            return True
    return False


def _strip_invisible_chars(text: str) -> str:
    """Elimina caracteres de control/invisibles sin romper emojis visibles."""
    return "".join(ch for ch in text if unicodedata.category(ch) not in {"Cf", "Cc"} or ch in {"\n", "\t"})


def _to_ascii_fold(text: str) -> str:
    normalized = unicodedata.normalize("NFD", text)
    return "".join(ch for ch in normalized if unicodedata.category(ch) != "Mn")


def normalize_text(value: object) -> str:
    """Normaliza texto para NLP basico: lowercase, sin tildes y con espacios compactos."""
    if value is None:
        return ""
    text = _strip_invisible_chars(str(value)).strip().lower()
    if not text or text == "nan":
        return ""
    text = _to_ascii_fold(text)
    text = re.sub(r"\s+", " ", text)
    return text


def tokenize_spanish(text: str) -> list[str]:
    """Tokeniza y elimina stopwords/ruido para analisis lexicografico."""
    if not text:
        return []
    tokens = [tok for tok in TOKEN_RE.findall(text) if len(tok) >= 2 and not tok.isdigit()]
    return [tok for tok in tokens if tok not in SPANISH_STOPWORDS]


def _detect_negation(text: str, pos: int) -> bool:
    """Detecta si hay negacion (no, tampoco, nunca, jamas) antes de una palabra positiva.
    
    Busca negaciones en una ventana de 15 caracteres antes de la posición actual.
    """
    start = max(0, pos - 15)
    prefix = text[start:pos]
    negation_words = {"no", "tampoco", "nunca", "jamas"}
    tokens_prefix = prefix.split()
    return len(tokens_prefix) > 0 and tokens_prefix[-1] in negation_words


def clean_raw_text(raw_text: str, *, min_chars: int = 4) -> dict:
    """Limpia texto pegado por bloque, filtra ruido y devuelve metricas detalladas.

    Aplica multiples filtros agresivos:
    - Minimo 4 palabras (por defecto).
    - Detecta y filtra IDs aleatorios de sistema (e.g., m63gi9, 7ia4t).
    - Filtra frases boilerplate de plataformas (Google Maps, Facebook, etc.).
    - Elimina duplicados exactos.

    Parameters
    ----------
    raw_text:
        Bloque de texto con saltos de linea.
    min_chars:
        Longitud minima de comentario para conservarlo (aprox. caracteres).

    Returns
    -------
    dict
        {"comentarios_validos": list[str],
         "total_original": int,
         "total_descartados": int,
         "descarte_detalles": list[tuple(motivo, texto)]}
    """
    if raw_text is None:
        return {
            "comentarios_validos": [],
            "total_original": 0,
            "total_descartados": 0,
            "descarte_detalles": [],
        }

    unique_comments: list[str] = []
    seen: set[str] = set()
    descarte_detalles: list[tuple[str, str]] = []
    total_original = 0

    for line in str(raw_text).splitlines():
        cleaned = _strip_invisible_chars(line).strip()
        cleaned = re.sub(r"\s+", " ", cleaned)
        total_original += 1

        # Filtro 1: Longitud minima
        if len(cleaned) < min_chars:
            descarte_detalles.append(("longitud_insuficiente", cleaned))
            continue

        # Filtro 2: Detectar ruido de sistema (entropy-based)
        if _detect_system_noise(cleaned):
            descarte_detalles.append(("ruido_sistema", cleaned))
            continue

        # Filtro 3: Detectar boilerplate de plataforma
        if _detect_platform_boilerplate(cleaned):
            descarte_detalles.append(("boilerplate_plataforma", cleaned))
            continue

        # Filtro 4: Duplicados exactos
        if cleaned in seen:
            descarte_detalles.append(("duplicado_exacto", cleaned))
            continue

        seen.add(cleaned)
        unique_comments.append(cleaned)

    return {
        "comentarios_validos": unique_comments,
        "total_original": total_original,
        "total_descartados": len(descarte_detalles),
        "descarte_detalles": descarte_detalles,
    }


def classify_sentiment(comment: str) -> tuple[str, int]:
    """Clasifica sentimiento en 5 escalas: 1 (muy negativo) a 5 (muy positivo).
    
    Estrategia:
    1. Busca frases exactas (multi-palabra) de muy negativo y muy positivo
    2. Busca frases exactas negativas y positivas
    3. Busca palabras individuales con scoring
    4. Detecta negaciones para bajar score de palabras positivas
    """
    normalized = normalize_text(comment)
    if not normalized:
        return "Neutral", 3

    # PASO 1: Buscar frases muy negativas (mas precisas que palabras)
    for phrase in VERY_NEGATIVE_PHRASES:
        if phrase in normalized:
            return "Muy Negativo", 1
    
    # PASO 2: Buscar frases muy positivas
    for phrase in VERY_POSITIVE_PHRASES:
        if phrase in normalized:
            return "Muy Positivo", 5
    
    # PASO 3: Buscar frases negativas
    for phrase in NEGATIVE_PHRASES:
        if phrase in normalized:
            # Puede ser negado ("no le falta mucho" = positivo)
            pos = normalized.find(phrase)
            if not _detect_negation(normalized, pos):
                return "Negativo", 2
    
    # PASO 4: Buscar frases positivas
    for phrase in POSITIVE_PHRASES:
        if phrase in normalized:
            # Puede ser negado
            pos = normalized.find(phrase)
            if not _detect_negation(normalized, pos):
                return "Positivo", 4

    # PASO 5: Scoring basado en palabras individuales
    tokens = tokenize_spanish(normalized)
    if not tokens:
        return "Neutral", 3

    very_negative_hits = sum(1 for tok in tokens if tok in VERY_NEGATIVE_WORDS)
    negative_hits = sum(1 for tok in tokens if tok in NEGATIVE_WORDS)
    positive_hits = sum(1 for tok in tokens if tok in POSITIVE_WORDS)
    very_positive_hits = sum(1 for tok in tokens if tok in VERY_POSITIVE_WORDS)

    # Penalidad si hay negacion antes de palabra positiva
    negation_penalty = 0
    for pos, tok in enumerate(tokens):
        if tok in POSITIVE_WORDS or tok in VERY_POSITIVE_WORDS:
            # Reconstruir posición en texto normalizado
            if _detect_negation(normalized, pos * 10):
                negation_penalty += 1

    weighted_score = (2 * very_positive_hits + positive_hits) - (2 * very_negative_hits + negative_hits) - negation_penalty

    if weighted_score >= 2:
        return "Muy Positivo", 5
    if weighted_score == 1:
        return "Positivo", 4
    if weighted_score <= -2:
        return "Muy Negativo", 1
    if weighted_score == -1:
        return "Negativo", 2
    return "Neutral", 3


def detect_categories(comment: str) -> str:
    """Detecta categoria con prioridad de busqueda especifica -> generica."""
    normalized = normalize_text(comment)
    if not normalized:
        return "Otro"

    tokens = set(tokenize_spanish(normalized))

    for category_name, keywords in CATEGORY_KEYWORDS:
        if tokens.intersection(keywords):
            return category_name

    return "Otro"


def add_sentiment_analysis(df: pd.DataFrame, comment_column: str = "comentario_original") -> pd.DataFrame:
    """Agrega columnas de sentimiento de 5 niveles al DataFrame."""
    if comment_column not in df.columns:
        raise ValueError(f"La columna requerida '{comment_column}' no existe en el DataFrame.")

    enriched = df.copy()
    payload = enriched[comment_column].fillna("").astype(str).map(classify_sentiment)
    enriched["sentimiento_etiqueta"] = payload.map(lambda item: item[0])
    enriched["sentimiento_score"] = payload.map(lambda item: int(item[1]))
    return enriched


def create_dataframe_from_comments(
    comments: Iterable[str],
    source: str,
    *,
    load_date: datetime | None = None,
) -> pd.DataFrame:
    """Construye DataFrame estructurado desde comentarios limpios.
    
    Nota: Si `comments` es el resultado de clean_raw_text(), pasa
    el valor de 'comentarios_validos' (la lista).
    """
    comments_list = [str(comment).strip() for comment in comments if str(comment).strip()]

    if load_date is None:
        load_date = datetime.now(timezone.utc)

    base = pd.DataFrame(
        {
            "fecha_carga": [load_date.date().isoformat()] * len(comments_list),
            "fuente": [str(source).strip() or "Otra"] * len(comments_list),
            "comentario_original": comments_list,
        }
    )

    if base.empty:
        for col in CSV_COLUMN_ORDER:
            if col not in base.columns:
                base[col] = pd.Series(dtype="object")
        return base[CSV_COLUMN_ORDER].copy()

    with_sentiment = add_sentiment_analysis(base, comment_column="comentario_original")
    with_sentiment["categoria"] = with_sentiment["comentario_original"].map(detect_categories)

    return with_sentiment[CSV_COLUMN_ORDER].copy()


def validate_and_align_columns(
    df: pd.DataFrame,
    *,
    required_order: list[str] | None = None,
    header_mapping: dict[str, str] | None = None,
) -> pd.DataFrame:
    """Valida columnas requeridas, reordena y renombra para salida consistente."""
    required = required_order or CSV_COLUMN_ORDER
    missing = [col for col in required if col not in df.columns]
    if missing:
        raise ValueError(
            "Faltan columnas requeridas para exportacion: " + ", ".join(missing)
        )

    aligned = df[required].copy()
    mapping = dict(CSV_HEADERS_DEFAULT)
    if header_mapping:
        mapping.update(header_mapping)

    aligned = aligned.rename(columns={col: mapping.get(col, col) for col in required})
    return aligned


def export_to_csv(
    df: pd.DataFrame,
    *,
    required_order: list[str] | None = None,
    header_mapping: dict[str, str] | None = None,
) -> bytes:
    """Exporta DataFrame a CSV UTF-8-SIG compatible con Excel/Google Sheets."""
    aligned = validate_and_align_columns(
        df,
        required_order=required_order,
        header_mapping=header_mapping,
    )
    buffer = io.StringIO()
    aligned.to_csv(buffer, index=False, encoding="utf-8-sig")
    return buffer.getvalue().encode("utf-8-sig")


def export_full_csv(df: pd.DataFrame, *, header_mapping: dict[str, str] | None = None) -> bytes:
    """Exporta CSV maestro con todas las columnas analizadas."""
    return export_to_csv(
        df,
        required_order=CSV_COLUMN_ORDER,
        header_mapping=header_mapping,
    )


def export_manual_load_csv(
    df: pd.DataFrame,
    *,
    include_source: bool = False,
    header_mapping: dict[str, str] | None = None,
) -> bytes:
    """Exporta CSV simplificado para carga manual rapida.

    Parameters
    ----------
    include_source:
        Si True, incluye columna `fuente` junto con `comentario_original`.
    """
    required_order = ["comentario_original", "fuente"] if include_source else CSV_MANUAL_LOAD_ORDER
    return export_to_csv(
        df,
        required_order=required_order,
        header_mapping=header_mapping,
    )
