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

# Sistema automÃ¡tico de retroalimentaciÃ³n
from . import feedback_system

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
    "categoria_detalle": "categoria_detalle",
    "categoria_confianza": "categoria_confianza",
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
    "excelente", "maravilloso", "espectacular", "perfecto", "extraordinario", "brutal",
    "impresionante", "fascinante", "top", "excelencia", "pedagogico", "calidez",
    "profesionalismo", "joya", "impecable", "recomendadisimo", "pedagogia", "supremo",
    "inmejorable", "asombroso", "ejemplar", "transformador", "humanista", "inspirador", "unico",
    "sobresaliente", "gratitud", "bendicion", "exito", "orgullo", "tradicion", "prestigio", "solido",
    "honesto", "seguro", "confiable", "amor", "dedicacion", "pasion", "entrega", "vocacion",
    "sabiduria", "luz", "guia", "armonia", "plenitud", "crecimiento", "futuro",
    "esperanza", "impacto", "genial", "epico", "inolvidable", "premium", "elite", "brillante",
    "experto", "dedicado", "carismatico", "empatico", "transparente", "autentico", "leal",
    "resiliente", "valiente", "audaz", "creativo", "innovador", "visionario", "culto", "preparado",
    "capaz", "eficiente", "responsable", "comprometido", "moral", "justo", "noble", "bondadoso",
    "generoso", "altruista", "solidario", "inigualable", "extraordinario", "magnifico", "imbatible",
    "insuperable", "sublime", "glorioso", "virtuoso", "humano", "corazon",
    "amo", "adoro", "adore", "extraordinaria", "extraordinario",
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
    "5 estrellas",
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
    "buen", "mejores", "buenisimo", "buenisima", "amplios", "adecuados", "capacitado", "capacitados",
    "bonitas", "amplia", "amplio", "cordial", "respetuoso", "incluyente", "apoyo",
    "contento", "contenta", "recomendada", "orgullosa", "alegre",
    "maravillosa", "maravilloso", "gratitud", "agradecido", "agradecida",
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
    "muy buen nivel academico",
    "mucho espacio verde",
    "gran cantidad de salones",
    "son bienvenidos siempre",
    "universidad con valores",
    "muy bonito todo",
    "experiencia muy bonita",
    "siempre al pendiente",
    "extrano mucho",
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
    "grosero", "grosera", "malos", "malas", "malisimo", "malisima", "triste", "decepciona",
    "ineficiente", "incumple", "peor", "molestias", "molesto", "problemas", "pagar",
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
    "deja mucho que desear",
    "no es la escuela para ustedes",
    "no funciona",
    "favoritismo evidente",
    "da mal la informacion",
    "solo son amables mientras",
    "no le permiten bajar",
    "no puede hacer nada",
    "otros lugares con mas accesibilidad",
    "otros lugares con mas accecibilidad",
    "hay universidades mejores",
    "algunos profesores buenos otros malos",
    "algunos son buenos pero otros malos",
    "les quedo grande el cargo",
    "ofrecen cosas que no pueden cumplir",
    "no se abriria",
    "rectora ineficiente",
    "no valen la pena",
    "no vale la pena",
}

VERY_NEGATIVE_WORDS = {
    "pesimo", "asco", "horrible", "desastre", "terrible", "inaceptable", "sucio", "fatal",
    "estafa", "vergonzoso", "robo", "peligroso", "insultante", "insalubre",
    "groseria", "fraude", "fraudulento", "fraudulenta", "mentira", "engano", "negligencia", "peligro", "riesgo", "inseguro",
    "asqueroso", "podrido", "vencido", "prepotente", "despota", "abusivo", "injusto", "carisimo",
    "inaccesible", "ineficiente", "tortuoso", "caotico", "abandono", "ruina", "inservible",
    "basura", "porqueria", "cuidado", "alerta", "denuncia", "demanda", "abogado", "queja",
    "reclamo", "maltrato", "humillacion", "discriminacion", "racismo", "clasismo", "machismo",
    "acoso", "violencia", "panico", "intoxicacion", "crudo", "quemado", "desastroso",
    "catastrofico", "patetico", "lamentable", "indignacion", "traumatico", "cloaca", "ratero",
    "nefasto", "nefasta", "impune", "corrupto", "indignante", "terror", "abusos",
    "arrogancia", "soberbia", "antivalores", "decepcion",
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
    "desaprovechenla totalmente",
    "desaprovechenla",
    "cafeteria con ratas",
    "encubren casos de acoso",
    "encubren al acosador",
    "sistema educativo en primera es malisimo",
    "si tienen la oportunidad de entrar ahi desaprovechenla",
    "si tienen la oportunidad desaprovechenla",
    "me hicieron bullying",
    "me hacian bullying",
    "me quisieron tirar",
}

# Terminos de riesgo critico: si aparecen, priorizar severidad maxima.
CRITICAL_ALERT_WORDS = {
    "abuso", "abusos", "abusaron", "abusador", "violacion", "violencia", "acoso",
    "maltrato", "negligencia", "corrupcion", "impune", "encubren", "encubrimiento",
    "clausurado", "clausurados", "clausura",
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
    "google review",
    "foto de",
    "universidad marista (propietario)",
    "editado hace",
    "opinion",
    "opiniones",
    "local guide",
    "me gusta",
    "responder",
    "ver mas",
}

SOCIAL_METADATA_EXACT = {
    "me gusta",
    "responder",
    "ver mas",
    "sem",
}

SOCIAL_NEGATIVE_PHRASES = {
    "pandemia no me dejo",
    "pandemia que me quito",
    "no me dejo disfrutar",
    "se me metio un",
    "descansa en paz",
    "ultimo ano",
    "ano perdido",
    "tiempo perdido",
    "me quito mi viaje",
}

SOCIAL_POSITIVE_PHRASES = {
    "por siempre",
    "amo amo",
    "gracias por tanto",
    "el mejor",
    "siempre el mejor",
    "viva el profe",
    "leyenda",
    "amamos",
}

SOCIAL_NOSTALGIA_POSITIVE_PHRASES = {
    "que recuerdos",
    "tantos recuerdos",
    "los mejores anos",
    "por siempre marista",
    "siempre en mi corazon",
    "los voy a extranar",
}

SOCIAL_TEACHER_PRAISE_PHRASES = {
    "maestro alejandro",
    "profe ale",
    "excelente maestro",
    "maestrazo",
    "el mejor maestro",
    "top globales",
}

POSITIVE_EMOJI = {
    "\u2764",
    "\u2764\ufe0f",
    "\U0001f499",
    "\U0001f49e",
    "\U0001f49d",
    "\U0001f49f",
    "\U0001f60d",
    "\U0001f970",
    "\U0001f973",
    "\U0001faf6",
    "\U0001f60a",
    "\U0001f929",
    "\U0001f44f",
    "\U0001f64c",
    "\U0001f389",
    "\U0001f31f",
    "\U0001f31e",
    "\U0001f3c6",
    "\U0001f393",
    "\U0001f44d",
}

NEGATIVE_EMOJI = {
    "\U0001f622",
    "\U0001f62d",
    "\U0001f614",
    "\U0001f625",
    "\U0001f494",
    "\U0001f97a",
    "\U0001f972",
    "\U0001fa79",
    "\U0001f612",
    "\U0001f61e",
    "\U0001f61f",
}

POSITIVE_EMOTICONS = {":)", ":d", "<3", "xd", "jaja", "jeje", "jiji"}
NEGATIVE_EMOTICONS = {":(", "):", "d:", "pff", "ouch"}

# Regex para patrones de boilerplate que no se pueden capturar con frases exactas.
# Ejemplos: "Hace 2 aÃ±os", "Hace 5 meses", "A. B.", "J. L. M."
_BOILERPLATE_REGEX = re.compile(
    r"(?i)^"
    r"(?:"
    r"hace\s+\d+\s+(?:ano|anos|mes|meses|semana|semanas|dia|dias|hora|horas|minuto|minutos)"  # Hace X aÃ±os/meses...
    r"|editado\s+hace\s+\d+\s+(?:ano|anos|mes|meses|semana|semanas|dia|dias)"
    r"|foto\s+\d+\s+de\s+la\s+opinion\s+de.*"
    r"|\d+\s+opinion(?:es)?(?:\s*Â·\s*\d+\s+foto(?:s)?)?"
    r"|[a-z]\.(?:\s+[a-z]\.)+\s*$"  # Iniciales normalizadas: a. b. / j. l. m.
    r"|(?:&#\d+;){2,}\d*"
    r"|\d+\s*sem(?:\s*\d+\s*me\s*gusta)?(?:\s*responder)?"
    r")"
)

# Bloques de reacciones compuestos solo por emojis/simbolos (sin texto semantico).
_EMOJI_ONLY_SPAM_REGEX = re.compile(
    r"^(?:[\U0001F1E6-\U0001F1FF\U0001F300-\U0001FAFF\u2600-\u27BF\u200d\ufe0f\s])+\d*$"
)

_MENTION_REGEX = re.compile(r"@[A-Za-z0-9_.]+")

# Nombre simple de perfil: "Pedro Is", "Lenin Tonatiuh Carbajal Ortega", "Manuel"
_PROFILE_NAME_REGEX = re.compile(r"^[A-ZÃÃ‰ÃÃ“ÃšÃ‘][A-Za-zÃÃ‰ÃÃ“ÃšÃ‘Ã¡Ã©Ã­Ã³ÃºÃ±]+(?:\s+[A-ZÃÃ‰ÃÃ“ÃšÃ‘][A-Za-zÃÃ‰ÃÃ“ÃšÃ‘Ã¡Ã©Ã­Ã³ÃºÃ±]+){0,4}$")

# Respuestas institucionales del propietario/escuela.
INSTITUTIONAL_RESPONSE_PHRASES = {
    "agradecemos tus comentarios",
    "seguimos a tus ordenes",
    "saludos cordiales",
    "quedamos a tus ordenes",
    "lamentamos leer tu comentario",
    "lamentamos que tu experiencia",
    "nos preocupa tu situacion",
    "recibe un cordial saludo",
    "gracias por tu comentario y calificacion",
    "hola ",
    "son bienvenidos siempre a esta su casa",
    "el anonimato no nos permite",
    "comunicate con nosotros y atenderemos",
    "apreciamos y valoramos profundamente la retroalimentacion",
    "derivaremos tu comentario",
    "nuestras puertas siempre estaran abiertas",
    "estamos siempre disponibles para atenderte",
    "nos alegra saber que disfrutas de nuestras instalaciones",
    "esperamos que hayas disfrutado tu estancia",
    "reiteramos nuestro compromiso",
    "te comparto nuestro link",
    "canal de denuncia se encuentra abierto",
    "comite de proteccion",
    "avanzando hacia la construccion de un ambiente libre",
    "nos alegra saber que valoras la educacion marista",
    "nos motiva saber que es un espacio que valoras",
    "confiando en que tu mensaje encontrara el eco que buscas",
}

# Prioridad de categorias multisectoriales: especificas primero, genericas al final.
# DiseÃ±ado para instituciones educativas mexicanas con metricas sociales.
# TIP: marista, humanista, valores â†’ prioritarios en Ambiente/Comunidad
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
            "accesibilidad", "accecibilidad",
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
            "permiso", "permiten", "permitir", "autorizar", "autorizan",
        },
    ),
    (
        "Ambiente/Comunidad",
        {
            "valores", "familia", "convivencia", "amigos", "marista", "seguridad", "respeto",
            "social", "integracion", "comunidad", "ambiente", "amistad", "compaÃ±erismo", "union",
            "fraternidad marista", "pastoral juvenil", "retiros espirituales", "integracion familiar",
            "sana convivencia", "inclusion educativa", "diversidad cultural", "sentido de pertenencia",
            "misiones de semana santa", "voluntariado estudiantil", "kermÃ©s anual", "olimpiadas familiares",
            "sociedad de alumnos", "ex alumnos", "valores institucionales", "ambiente libre de acoso",
            "jesuita", "salesiano", "benedictino", "humanista", "jesuitas",
            "claustro", "carisma", "tradicion", "historia", "futuro", "esperanza", "fe", "religion",
            "espiritualidad", "luz", "guia", "armonia", "plenitud", "crecimiento", "vida", "corazon",
            "valores maristas", "corazon de marista", "relacion", "grupo", "equipo", "hermandad",
            "fraternidad", "apoyo mutuo", "inclusion", "diversidad", "equidad", "genero", "paz",
            "alegria", "diversion", "recreacion", "socializacion", "fiestas", "eventos", "kermÃ©s",
            "misa", "pastoral", "retiro", "misiones", "servicio social", "voluntariado", "ecologia",
            "sustentabilidad", "conciencia social", "civica", "patriotismo", "moral", "justicia",
            "libertad", "verdad", "integridad", "responsabilidad", "pertenencia", "red", "contactos",
            "networking", "colaboracion", "sinergia", "participacion", "alumnos", "estudiantes",
            "egresados", "alumni", "clima escolar", "bullying", "acoso", "violencia", "discriminacion",
            "confianza", "lealtad", "fidelidad", "liderazgo", "ejemplo", "inspira",
        },
    ),
]

CATEGORY_KEYWORDS_MAP = {category_name: set(keywords) for category_name, keywords in CATEGORY_KEYWORDS}

# Taxonomia de segundo nivel (detalle) para clasificacion tematica por evidencia.
# Mantiene macro-categorias actuales, pero permite mayor especificidad analitica.
CATEGORY_DETAIL_RULES = [
    {
        "macro": "Academico/Calidad",
        "detail": "Docencia y Pedagogia",
        "phrases": {
            "nivel academico",
            "maestros muy preparados",
            "buen nivel academico",
            "plan de estudios",
        },
        "ngrams": {
            "nivel academico",
            "plan estudios",
            "metodo ensenanza",
            "clase dinamica",
        },
        "tokens": {
            "profesor", "profesores", "maestro", "maestros", "docente", "docentes",
            "pedagogia", "pedagogico", "ensenanza", "clase", "clases", "metodo", "didactica",
            "aprendizaje", "formacion", "academico", "academica", "tutoria", "asesoria",
        },
        "ambiguous_tokens": set(),
        "required_context": set(),
    },
    {
        "macro": "Academico/Calidad",
        "detail": "Evaluacion y Logros",
        "phrases": {
            "nivel de egreso",
            "certificaciones internacionales",
            "validez ante la sep",
        },
        "ngrams": {
            "nivel egreso",
            "pensamiento critico",
            "razonamiento logico",
        },
        "tokens": {
            "calificacion", "calificaciones", "evaluacion", "evaluaciones", "examen", "examenes",
            "promedio", "acreditacion", "certificacion", "certificaciones", "logro", "logros",
            "egreso", "ingles", "sep", "competencia", "competencias", "olimpiadas",
        },
        "ambiguous_tokens": set(),
        "required_context": set(),
    },
    {
        "macro": "Infraestructura",
        "detail": "Espacios Fisicos",
        "phrases": {
            "buenas instalaciones",
            "areas verdes",
            "gran cantidad de salones",
        },
        "ngrams": {
            "espacios fisicos",
            "aire acondicionado",
            "areas verdes",
            "estacionamiento salida",
        },
        "tokens": {
            "instalaciones", "aula", "aulas", "salon", "salones", "bano", "banos", "patio",
            "cancha", "canchas", "edificio", "estacionamiento", "entrada", "pasillos", "techo",
            "piso", "ventanas", "limpieza", "cafeteria", "comedor", "sombra", "remodelacion",
        },
        "ambiguous_tokens": {"limpieza"},
        "required_context": {"instalaciones", "edificio", "aula", "aulas", "salon", "salones", "banos", "patio", "cancha", "canchas"},
    },
    {
        "macro": "Infraestructura",
        "detail": "Equipamiento y Tecnologia",
        "phrases": {
            "centro de computo",
            "red de fibra optica",
            "proyectores inteligentes",
            "laboratorios de quimica",
        },
        "ngrams": {
            "equipamiento tecnologia",
            "laboratorio quimica",
            "aula magna",
            "fibra optica",
        },
        "tokens": {
            "laboratorio", "laboratorios", "computadora", "computadoras", "wifi", "internet",
            "tecnologia", "conectividad", "proyector", "proyectores", "software", "hardware",
            "plataforma", "digital", "equipo", "equipamiento", "red",
        },
        "ambiguous_tokens": {"red", "digital"},
        "required_context": {"wifi", "internet", "tecnologia", "laboratorio", "laboratorios", "software", "hardware", "proyector", "proyectores"},
    },
    {
        "macro": "Precio/Valor",
        "detail": "Colegiaturas y Tramites",
        "phrases": {
            "costo beneficio",
            "estado de cuenta",
            "pago referenciado",
            "recargos por mora",
        },
        "ngrams": {
            "costo beneficio",
            "estado cuenta",
            "calidad precio",
            "pago referenciado",
        },
        "tokens": {
            "costo", "costos", "precio", "precios", "colegiatura", "colegiaturas", "mensualidad", "mensualidades",
            "inscripcion", "reinscripcion", "tramite", "tramites", "pago", "pagos", "recargo", "recargos",
            "factura", "adeudo", "intereses", "cuota", "cuotas", "presupuesto", "cobranza",
        },
        "ambiguous_tokens": {"tramite", "tramites"},
        "required_context": {"costo", "costos", "precio", "precios", "colegiatura", "colegiaturas", "mensualidad", "mensualidades", "pago", "pagos", "cuota", "cuotas"},
    },
    {
        "macro": "Precio/Valor",
        "detail": "Becas y Apoyos",
        "phrases": {
            "apoyo financiero",
            "descuento por hermanos",
            "seguro de orfandad",
        },
        "ngrams": {
            "apoyo financiero",
            "apoyo economico",
            "descuento hermanos",
        },
        "tokens": {
            "beca", "becas", "descuento", "descuentos", "financiamiento", "credito", "apoyo",
            "economico", "economica", "apoyos", "beneficio", "beneficios", "convenio",
        },
        "ambiguous_tokens": {"apoyo", "beneficio"},
        "required_context": {"beca", "becas", "descuento", "descuentos", "financiamiento", "credito", "economico", "economica"},
    },
    {
        "macro": "Servicio/Atencion",
        "detail": "Gestion Administrativa",
        "phrases": {
            "control escolar",
            "atencion a padres",
            "secretaria academica",
            "mesa de ayuda",
        },
        "ngrams": {
            "gestion administrativa",
            "control escolar",
            "atencion padres",
            "respuesta rapida",
        },
        "tokens": {
            "gestion", "administrativa", "tramite", "tramites", "control", "escolar", "secretaria",
            "respuesta", "tiempo", "tiempos", "demora", "fila", "filas", "admisiones", "coordinacion",
            "direccion", "seguimiento", "informacion", "comunicacion",
        },
        "ambiguous_tokens": {"comunicacion", "informacion", "seguimiento"},
        "required_context": {"control", "escolar", "secretaria", "gestion", "tramite", "tramites", "admisiones", "coordinacion", "direccion"},
    },
    {
        "macro": "Servicio/Atencion",
        "detail": "Trato Humano",
        "phrases": {
            "trato humano",
            "personal amable",
            "atencion deficiente",
        },
        "ngrams": {
            "trato humano",
            "trato amable",
            "trato prepotente",
        },
        "tokens": {
            "amabilidad", "amable", "amables", "empatia", "paciencia", "calidez", "trato", "humano",
            "prepotente", "grosero", "grosera", "disposicion", "voluntad", "escucha", "asertividad",
            "profesionalismo", "actitud", "respeto",
        },
        "ambiguous_tokens": {"trato", "actitud"},
        "required_context": {"amabilidad", "amable", "amables", "empatia", "prepotente", "grosero", "grosera", "calidez", "respeto"},
    },
    {
        "macro": "Ambiente/Comunidad",
        "detail": "Identidad y Valores Maristas",
        "phrases": {
            "un solo corazon marista",
            "valores maristas",
            "fraternidad marista",
            "sentido de pertenencia",
        },
        "ngrams": {
            "valores maristas",
            "identidad marista",
            "sentido pertenencia",
            "pastoral juvenil",
        },
        "tokens": {
            "marista", "valores", "identidad", "fraternidad", "humanismo", "humanista", "orgullo",
            "pertenencia", "misiones", "retiro", "retiros", "pastoral", "espiritualidad", "carisma",
            "tradicion", "fe", "comunidad",
        },
        "ambiguous_tokens": {"comunidad", "tradicion"},
        "required_context": {"marista", "valores", "identidad", "fraternidad", "humanismo", "humanista", "pastoral", "misiones", "retiro", "retiros"},
    },
    {
        "macro": "Ambiente/Comunidad",
        "detail": "Clima Escolar",
        "phrases": {
            "ambiente libre de acoso",
            "sana convivencia",
            "clima escolar",
            "caso de bullying",
        },
        "ngrams": {
            "clima escolar",
            "sana convivencia",
            "ambiente acoso",
        },
        "tokens": {
            "convivencia", "bullying", "acoso", "violencia", "discriminacion", "inclusion", "amistad",
            "amigos", "equipo", "companerismo", "respeto", "equidad", "diversidad", "paz", "seguridad",
        },
        "ambiguous_tokens": {"equipo", "amigos", "seguridad"},
        "required_context": {"bullying", "acoso", "violencia", "discriminacion", "convivencia", "inclusion", "diversidad", "equidad"},
    },
]

CATEGORY_SCORING_WEIGHTS = {
    "phrase": 3,
    "ngram": 2,
    "token": 1,
}

CATEGORY_MIN_SCORE = 2

CLIMA_ESCOLAR_RISK_TERMS = {"bullying", "acoso", "violencia", "discriminacion"}

PRICE_VALUE_CONTEXT_TERMS_BASE = {
    "inscripcion", "reinscripcion", "mensualidad", "mensualidades", "colegiatura", "colegiaturas",
    "cuota", "cuotas", "pago", "pagos", "presupuesto", "factura", "adeudo", "costo", "costos",
    "precio", "precios",
}

PRICE_TRIGGER_WORDS = {
    "costo", "costos", "precio", "precios", "caro", "cara", "carisimo", "carisima",
    "cuota", "cuotas", "mensualidad", "mensualidades", "colegiatura", "colegiaturas",
    "pago", "pagos", "cobro", "cobros", "descuento", "descuentos", "beca", "becas",
    "dinero", "economico", "economica", "recargo", "recargos", "tarifa", "tarifas",
    "inversion", "inversiones", "barato", "barata", "gasto", "gastos",
}

PRICE_VALUE_CONTEXT_TERMS = PRICE_TRIGGER_WORDS.union(PRICE_VALUE_CONTEXT_TERMS_BASE)

ADVERSATIVE_WORDS = {"pero", "aunque", "sin", "embargo"}
NEGATION_WORDS = {"no", "tampoco", "nunca", "jamas"}

TOKEN_RE = re.compile(r"[a-zA-Z0-9_]+", re.UNICODE)
SYSTEM_ID_PATTERN = re.compile(r"\b[a-z0-9]{5,}\b")


def _detect_system_noise(text: str) -> bool:
    """Detecta ruido de sistema: IDs aleatorios sin suficientes vocales.

    Esta heuristica solo se aplica a lineas de una sola palabra (tipo token),
    para evitar falsos positivos en frases reales en espanol.

    Patrones esperados: m63gi9, 606ga6, rnpSostdeol.
    """
    candidate = text.strip().strip(".,;:!?()[]{}\"'")
    if not candidate:
        return False

    # Si hay espacios, es casi seguro que es un comentario real.
    if " " in candidate:
        return False

    if not candidate.isalnum() or len(candidate) < 5:
        return False

    vowels = sum(1 for c in candidate.lower() if c in "aeiouÃ¡Ã©Ã­Ã³Ãº")
    vowel_ratio = vowels / len(candidate)
    has_digit = any(ch.isdigit() for ch in candidate)

    # IDs alfanumericos con digitos y baja proporcion de vocales.
    if has_digit and vowel_ratio < 0.35:
        return True

    # Tokens largos sin digitos pero muy poco pronunciables.
    if not has_digit and vowel_ratio < 0.30:
        return True

    return False


def _detect_platform_boilerplate(text: str) -> bool:
    """Detecta frases boilerplate de Google Maps/Facebook/Instagram.

    Descarta:
    - Frases de la lista PLATFORM_BOILERPLATE (exactas, normalizadas)
    - Patrones regex: 'Hace X aÃ±os/meses', iniciales 'A. B.', 'J. L. M.'
    """
    normalized = normalize_text(text)
    stripped = text.strip()

    if not normalized:
        return False

    # Detectar respuestas del propietario por sufijo "(propietario)" o "(owner)"
    if "(propietario)" in normalized or "(owner)" in normalized:
        return True

    for phrase in PLATFORM_BOILERPLATE:
        # Evita descartar comentarios reales como "me gusta mucho esta escuela".
        if phrase in SOCIAL_METADATA_EXACT:
            if normalized == phrase:
                return True
            continue
        if phrase in normalized:
            return True

    for phrase in INSTITUTIONAL_RESPONSE_PHRASES:
        if phrase in normalized:
            return True

    if _BOILERPLATE_REGEX.match(normalized):
        return True

    # Reacciones puras tipo emojis/simbolos (+ opcional contador numerico).
    # Conserva mensajes emocionales cortos de 1-3 emojis.
    if _EMOJI_ONLY_SPAM_REGEX.match(stripped):
        has_digits = any(ch.isdigit() for ch in stripped)
        emoji_count = sum(text.count(emo) for emo in POSITIVE_EMOJI.union(NEGATIVE_EMOJI))
        if has_digits or emoji_count >= 6:
            return True

    if _PROFILE_NAME_REGEX.match(stripped):
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
    return [tok for tok in tokens if tok not in SPANISH_STOPWORDS or tok in NEGATION_WORDS]


def _find_subsequence_start(tokens: list[str], subsequence: list[str]) -> int | None:
    """Devuelve indice inicial de una subsecuencia exacta de tokens."""
    if not subsequence or len(subsequence) > len(tokens):
        return None
    limit = len(tokens) - len(subsequence) + 1
    for idx in range(limit):
        if tokens[idx: idx + len(subsequence)] == subsequence:
            return idx
    return None


def _has_negation_before(tokens: list[str], index: int, *, window: int = 7) -> bool:
    """Detecta negacion en una ventana de tokens previa a un indice."""
    start = max(0, index - window)
    for tok in tokens[start:index]:
        if tok in NEGATION_WORDS:
            return True
    return False


def _contains_sentiment_emoji(text: str) -> bool:
    return any(emo in text for emo in POSITIVE_EMOJI) or any(emo in text for emo in NEGATIVE_EMOJI)


def _strip_mentions(text: str) -> str:
    return _MENTION_REGEX.sub(" ", text)


def _segment_social_blob(raw_text: str) -> list[str]:
    """Segmenta bloques continuos exportados de redes sociales en lineas comentables."""
    text = _strip_invisible_chars(raw_text)
    if not text.strip():
        return []

    hint = normalize_text(text)
    looks_like_social_blob = ("responder" in hint and "sem" in hint)

    if looks_like_social_blob:
        # Delimitador comun de Instagram/Facebook en pegado continuo.
        text = re.sub(
            r"(?i)\s*\d+\s*sem(?:\s*\d+\s*me\s*gusta)?\s*responder\s*",
            "\n",
            text,
        )
        text = re.sub(r"(?i)\s+responder\s+", "\n", text)

    return [re.sub(r"\s+", " ", ln).strip() for ln in text.splitlines() if ln.strip()]


def _emoji_sentiment_score(text: str) -> int:
    """Calcula una contribucion ligera de sentimiento con emojis comunes."""
    lowered = text.lower()
    # Presencia por tipo para evitar sobrepeso por repeticion de un mismo emoji.
    positive = sum(1 for emo in POSITIVE_EMOJI if emo in text)
    negative = sum(1 for emo in NEGATIVE_EMOJI if emo in text)
    positive += sum(1 for emot in POSITIVE_EMOTICONS if emot in lowered)
    negative += sum(1 for emot in NEGATIVE_EMOTICONS if emot in lowered)
    return positive - negative


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

    # Regex para detectar lÃ­neas que son inequÃ­vocamente metadata de Google Maps
    # que aparecen justo despuÃ©s del nombre del revisor.
    # IMPORTANTE: Solo usar indicadores unÃ­vocos (N opiniones, Local Guide).
    # No incluir "Hace N tiempo" porque tambiÃ©n aparece despuÃ©s de reseÃ±as reales.
    _NEXT_LINE_IS_METADATA = re.compile(
        r"(?i)^(?:"
        r"\d+\s+opini[o\u00f3]n(?:es)?"    # "1 opiniÃ³n", "3 opiniones" (con/sin tilde)
        r"|local\s+guide"                  # "Local GuideÂ·..."
        r")"
    )

    # Regex para detectar nombres de usuario con caracteres no convencionales
    _USERNAME_PATTERN = re.compile(
        r"(?i)(?:[:;]v|xd|uwu|[xX][dD]|_[a-z]|[a-z]_[a-z]|:\)|:p|:v)"
    )

    unique_comments: list[str] = []
    seen: set[str] = set()
    descarte_detalles: list[tuple[str, str]] = []
    total_original = 0

    lines = _segment_social_blob(str(raw_text))
    total_original = len(lines)

    for idx, cleaned in enumerate(lines):
        normalized_cleaned = normalize_text(cleaned)

        # Filtro 0: metadata social exacta o compacta (IG/FB) sin contenido de opinion.
        if normalized_cleaned in SOCIAL_METADATA_EXACT:
            descarte_detalles.append(("metadata_social", cleaned))
            continue
        if re.fullmatch(r"(?i)\d+\s*sem(?:\s*\d+\s*me\s*gusta)?", normalized_cleaned):
            descarte_detalles.append(("metadata_social", cleaned))
            continue

        # Filtro 1: Longitud minima (permitir expresiones breves con carga emocional).
        if len(cleaned) < min_chars and not _contains_sentiment_emoji(cleaned):
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

        # Filtro 4 (look-ahead): Si la siguiente lÃ­nea no vacÃ­a es metadata,
        # esta lÃ­nea es un nombre de revisor â†’ descartar.
        next_non_empty = next(
            (lines[j] for j in range(idx + 1, min(idx + 4, len(lines))) if lines[j].strip()),
            None,
        )
        if next_non_empty and _NEXT_LINE_IS_METADATA.match(next_non_empty):
            descarte_detalles.append(("nombre_perfil_lookahead", cleaned))
            continue

        # Filtro 5: Nombre de usuario con caracteres especiales de internet
        if _USERNAME_PATTERN.search(cleaned) and len(cleaned.split()) <= 5:
            # Conservar menciones utiles cuando existe contenido semantico aparte del handle.
            semantic_text = _strip_mentions(cleaned)
            if not tokenize_spanish(normalize_text(semantic_text)):
                descarte_detalles.append(("username_especial", cleaned))
                continue

        # Filtro 6: Duplicados exactos
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
    original_text = _strip_invisible_chars(str(comment or ""))
    emoji_score = _emoji_sentiment_score(original_text)
    normalized = normalize_text(original_text)
    normalized_wo_mentions = normalize_text(_strip_mentions(original_text))
    if not normalized:
        if emoji_score >= 2:
            return "Muy Positivo", 5
        if emoji_score == 1:
            return "Positivo", 4
        if emoji_score <= -2:
            return "Muy Negativo", 1
        if emoji_score == -1:
            return "Negativo", 2
        return "Neutral", 3

    tokens = tokenize_spanish(normalized_wo_mentions)

    # Regla de seguridad: cualquier termino critico debe escalar a muy negativo.
    if any(term in normalized for term in CRITICAL_ALERT_WORDS):
        return "Muy Negativo", 1

    # PASO 1: Buscar frases muy negativas (mas precisas que palabras)
    for phrase in VERY_NEGATIVE_PHRASES:
        if phrase in normalized:
            return "Muy Negativo", 1

    for phrase in SOCIAL_NEGATIVE_PHRASES:
        if phrase in normalized:
            return "Negativo", 2

    if "pandemia" in normalized and "no" in tokens and "dejo" in tokens:
        return "Negativo", 2
    
    # PASO 2: Buscar frases muy positivas
    # Si hay palabras muy negativas en el texto, no retornar automáticamente Muy Positivo
    has_very_negative_word = any(word in normalized for word in VERY_NEGATIVE_WORDS)
    
    for phrase in VERY_POSITIVE_PHRASES:
        if phrase in normalized:
            # Verificar si hay adversativo + negativa después (sarcasmo)
            phrase_pos = normalized.find(phrase)
            text_after = normalized[phrase_pos + len(phrase):]
            
            has_adversative_after = any(f" {adv} " in f" {text_after} " for adv in ADVERSATIVE_WORDS)
            has_very_neg_after = any(word in text_after for word in VERY_NEGATIVE_WORDS)
            
            # Si hay sarcasmo O hay palabras muy negativas en el texto, no retornar
            if not (has_adversative_after and has_very_neg_after) and not has_very_negative_word:
                return "Muy Positivo", 5

    for phrase in SOCIAL_POSITIVE_PHRASES:
        if phrase in normalized:
            return "Positivo", 4

    for phrase in SOCIAL_NOSTALGIA_POSITIVE_PHRASES:
        if phrase in normalized:
            return "Positivo", 4

    for phrase in SOCIAL_TEACHER_PRAISE_PHRASES:
        if phrase in normalized:
            return "Muy Positivo", 5

    # PASO 3: Buscar frases negativas
    for phrase in NEGATIVE_PHRASES:
        if phrase in normalized:
            # Puede ser negado ("no le falta mucho" = positivo)
            phrase_tokens = tokenize_spanish(normalize_text(phrase))
            phrase_start = _find_subsequence_start(tokens, phrase_tokens)
            if phrase_start is None or not _has_negation_before(tokens, phrase_start):
                return "Negativo", 2
    
    # PASO 4: Buscar frases positivas
    for phrase in POSITIVE_PHRASES:
        if phrase in normalized:
            # Puede ser negado
            phrase_tokens = tokenize_spanish(normalize_text(phrase))
            phrase_start = _find_subsequence_start(tokens, phrase_tokens)
            if phrase_start is None or not _has_negation_before(tokens, phrase_start):
                return "Positivo", 4

    # PASO 5: Scoring basado en palabras individuales
    if not tokens:
        return "Neutral", 3

    very_negative_hits = sum(1 for tok in tokens if tok in VERY_NEGATIVE_WORDS)
    negative_hits = sum(1 for tok in tokens if tok in NEGATIVE_WORDS)
    positive_hits = sum(1 for tok in tokens if tok in POSITIVE_WORDS)
    very_positive_hits = sum(1 for tok in tokens if tok in VERY_POSITIVE_WORDS)

        # ==================================================================================
        # OPCIÃ“N 1: Detectar sarcasmo por estructura [POSITIVA] + [ADVERSATIVO] + [NEGATIVA]
        # ==================================================================================
    _has_adversative = any(f" {adv} " in f" {normalized} " for adv in ADVERSATIVE_WORDS)
    
    if _has_adversative and very_negative_hits > 0 and very_positive_hits > 0:
            # Buscar la posiciÃ³n del adversativo mÃ¡s cercano
        adversative_positions = []
        for adv in ADVERSATIVE_WORDS:
            idx = normalized.find(f" {adv} ")
            if idx >= 0:
                adversative_positions.append(idx)
        
            if adversative_positions:
                first_adversative_pos = min(adversative_positions)
                pre_text = normalized[:first_adversative_pos]
                post_text = normalized[first_adversative_pos:]
            
                # Si hay palabras muy positivas ANTES del adversativo
                # y palabras muy negativas DESPUÃ‰S â†’ estructura sarcÃ¡stica
                has_very_pos_before = any(word in pre_text for word in VERY_POSITIVE_WORDS)
                has_very_neg_after = any(word in post_text for word in VERY_NEGATIVE_WORDS)
            
                # OpciÃ³n 1: InversiÃ³n automÃ¡tica de sarcasmo
                if has_very_pos_before and has_very_neg_after:
                    very_positive_hits = 0
                    positive_hits = 0

        # ==================================================================================
        # OPCIÃ“N 2: Si hay VERY_NEGATIVE en el texto, contexto de pÃ¡rrafo â†’ ignorar positivas
        # ==================================================================================
        if very_negative_hits > 0 and (positive_hits > 0 or very_positive_hits > 0):
            # Las palabras positivas son sospechosas cuando hay muy_negativas en el contexto
            # (tÃ­picamente sarcasmo o contraste: "encantÃ³ pero [problema]")
            # Reducir el peso de las positivas proporcionalmente
            reduction_factor = min(very_negative_hits, 2)  # Max 2x reducciÃ³n
            very_positive_hits = max(0, very_positive_hits - reduction_factor)
            positive_hits = max(0, positive_hits - reduction_factor)

        # Penalidad por negaciÃ³n: AMPLIAR VENTANA de 5 a 20 tokens
    negation_penalty = 0
    for pos, tok in enumerate(tokens):
        if tok in POSITIVE_WORDS or tok in VERY_POSITIVE_WORDS:
            if _has_negation_before(tokens, pos, window=4):
                negation_penalty += 1

    # Si la negacion invalida una critica de pandemia ("no impacto", "no afecto"),
    # reducimos una unidad de negativo para evitar sobrecastigo.
    pandemic_markers = {"pandemia", "covid", "covid19", "cuarentena"}
    pandemic_impact_words = {"impacto", "afecto", "perjudico"}
    for idx, tok in enumerate(tokens):
        if tok in pandemic_markers:
            tail = tokens[idx: min(len(tokens), idx + 6)]
            if any(w in tail for w in pandemic_impact_words) and any(neg in tail for neg in NEGATION_WORDS):
                negative_hits = max(0, negative_hits - 1)
                break

    # Si hay contraste adversativo ("pero", "aunque") y seÃ±ales negativas,
    # reducimos el peso de lo positivo para evitar falsos "Muy Positivo".
    # NOTA: tokens son filtrados de stopwords ("pero" es stopword), por eso
    # verificamos en el texto normalizado directamente.
    if _has_adversative and (very_negative_hits > 0 or negative_hits > 0):
        positive_hits = max(0, positive_hits - 1)
        very_positive_hits = max(0, very_positive_hits - 1)

    weighted_score = (
        (2 * very_positive_hits + positive_hits)
        - (2 * very_negative_hits + negative_hits)
        - negation_penalty
        + emoji_score
    )

    if weighted_score >= 2:
        return "Muy Positivo", 5
    if weighted_score == 1:
        return "Positivo", 4
    if weighted_score <= -2:
        return "Muy Negativo", 1
    if weighted_score == -1:
        return "Negativo", 2
    return "Neutral", 3


# Expansion de lexico social (sin romper contrato de etiquetas).
VERY_POSITIVE_WORDS.update(
    {
        "amamos", "crack", "leyenda", "master", "rifado", "rifa", "epico", "goat", "wow", "omg",
        "tqm", "forever", "idolo", "chingon", "chingona", "maestrazo", "jefazo", "campeonas", "campeones", "exitazo",
        "joya", "insuperable", "inigualable", "inolvidable", "supremo", "espectacular", "fascinante", "bendicion",
        "impecable", "fregon", "fregona", "iconico", "icono", "reina", "rey", "deidad", "titan", "heroe",
        "heroina", "victoria", "invencible", "triunfador", "ganadores", "ganadoras", "incondicional", "infinito",
        "alucinante", "bestial", "gozada", "brutalidad",
        "chingonas", "chingones", "tops", "tatuado", "tatuaje", "lealtad",
    }
)

POSITIVE_WORDS.update(
    {
        "chido", "padre", "chida", "cool", "nice", "super", "tiernas", "cute", "nostalgia", "recuerdos",
        "bro", "hermano", "compa", "animo", "apoyo", "felicidades", "congrats", "talento", "luz", "progreso",
        "bonito", "lindo", "fino", "tierno", "alegria", "felicidad", "sonrisa", "divertido", "agradable", "agusto",
        "tranquilo", "calma", "relax", "gracioso", "chistoso", "genialidad", "brillante", "genio", "habil", "fuerte",
        "noble", "leal", "amiga", "cuate", "pana", "carnal", "carnala", "camarada", "yei", "yupi",
        "etapa", "etapas", "disfruten", "disfrutar", "prepa", "generacion", "cobertura", "presupuesto",
    }
)

NEGATIVE_WORDS.update(
    {
        "ouch", "rip", "sad", "pandemia", "cuarentena", "encierro", "estres", "llorando", "tristeza", "melancolia",
        "bajon", "duele", "aislamiento", "separacion", "temblor", "sismo", "chale", "chin", "lastima", "depre",
        "hueva", "flojera", "pesado", "dificil", "complicado", "raro", "cringe", "lloro", "gris", "apagado",
        "lento", "tardado", "demora", "atraso", "caro", "costoso", "molestia", "incomodo", "obsoleto", "anticuado",
        "susto", "temor", "duda", "confuso", "problema", "falla", "error", "perdido", "perdida", "vacio",
    }
)

VERY_NEGATIVE_WORDS.update(
    {
        "funa", "funado", "toxico", "redflag", "nefasto", "odio", "detesto", "corrupto", "impunidad", "humillacion",
        "asco", "estafa", "basura", "porqueria", "horrible", "terror", "infierno", "pesadilla", "atrocidad", "aberracion",
        "ratero", "ladrones", "acoso", "violencia", "encubrimiento", "cinico", "descarado", "vergonzoso", "insulto", "ofensa",
        "machista", "racista", "clasista", "prepotente", "arrogante", "infame", "delincuente", "criminal", "crimen", "muerte",
    }
)


def detect_categories(comment: str) -> str:
    """Detecta macro-categoria; mantiene compatibilidad con el contrato historico."""
    macro, _, _ = detect_category_with_detail(comment)
    return macro


def _count_ngram_hits(tokens: list[str], ngrams: set[str]) -> tuple[int, set[str]]:
    hits = 0
    matched: set[str] = set()
    for ngram in ngrams:
        gram_tokens = tokenize_spanish(normalize_text(ngram))
        if not gram_tokens:
            continue
        if _find_subsequence_start(tokens, gram_tokens) is not None:
            hits += 1
            matched.add(ngram)
    return hits, matched


def detect_category_with_detail(comment: str) -> tuple[str, str, int]:
    """Detecta categoria por scoring de evidencia y retorna macro, detalle y confianza."""
    normalized = normalize_text(comment)
    if not normalized:
        return "Otro", "", 0

    token_list = tokenize_spanish(normalized)
    token_set = set(token_list)
    if not token_set:
        return "Otro", "", 0

    candidates: list[tuple[int, int, int, int, str, str]] = []

    for priority, rule in enumerate(CATEGORY_DETAIL_RULES):
        phrase_hits = {phrase for phrase in rule["phrases"] if phrase in normalized}
        ngram_count, ngram_hits = _count_ngram_hits(token_list, rule["ngrams"])
        token_hits = token_set.intersection(rule["tokens"])

        score = (
            len(phrase_hits) * CATEGORY_SCORING_WEIGHTS["phrase"]
            + ngram_count * CATEGORY_SCORING_WEIGHTS["ngram"]
            + len(token_hits) * CATEGORY_SCORING_WEIGHTS["token"]
        )

        # Penaliza terminos ambiguos sin contexto suficiente de la misma subcategoria.
        ambiguous_hits = token_hits.intersection(rule["ambiguous_tokens"])
        if ambiguous_hits and not token_set.intersection(rule["required_context"]):
            score -= len(ambiguous_hits)

        # Precio/Valor requiere contexto economico para evitar falsos positivos.
        if rule["macro"] == "Precio/Valor":
            has_price_context = bool(token_set.intersection(PRICE_VALUE_CONTEXT_TERMS)) or "vale la pena" in normalized
            if not has_price_context:
                score = 0

        # Refuerzo de seguridad para riesgos de clima escolar.
        if rule["detail"] == "Clima Escolar" and token_set.intersection(CLIMA_ESCOLAR_RISK_TERMS):
            score += 2

        if score > 0:
            unique_hits = len(phrase_hits) + len(ngram_hits) + len(token_hits)
            candidates.append((score, len(phrase_hits), unique_hits, -priority, rule["macro"], rule["detail"]))

    if not candidates:
        return "Otro", "", 0

    # Desempate: score > frases > evidencia unica > prioridad estable.
    best = max(candidates)
    best_score, _, _, _, best_macro, best_detail = best

    if best_score < CATEGORY_MIN_SCORE:
        return "Otro", "", int(best_score)

    return best_macro, best_detail, int(best_score)


def detect_category_detail(comment: str) -> str:
    """Retorna detalle de categoria para analitica de segundo nivel."""
    _, detail, _ = detect_category_with_detail(comment)
    return detail


def detect_category_confidence(comment: str) -> int:
    """Retorna score de evidencia de categoria para auditoria."""
    _, _, confidence = detect_category_with_detail(comment)
    return int(confidence)


def add_category_analysis(df: pd.DataFrame, comment_column: str = "comentario_original") -> pd.DataFrame:
    """Agrega categoria macro, detalle y confianza sin romper contratos existentes."""
    if comment_column not in df.columns:
        raise ValueError(f"La columna requerida '{comment_column}' no existe en el DataFrame.")

    enriched = df.copy()
    payload = enriched[comment_column].fillna("").astype(str).map(detect_category_with_detail)
    enriched["categoria"] = payload.map(lambda item: item[0])
    enriched["categoria_detalle"] = payload.map(lambda item: item[1])
    enriched["categoria_confianza"] = payload.map(lambda item: int(item[2]))
    return enriched


def add_sentiment_analysis(df: pd.DataFrame, comment_column: str = "comentario_original") -> pd.DataFrame:
    """Agrega columnas de sentimiento de 5 niveles al DataFrame."""
    if comment_column not in df.columns:
        raise ValueError(f"La columna requerida '{comment_column}' no existe en el DataFrame.")

    enriched = df.copy()
    payload = enriched[comment_column].fillna("").astype(str).map(classify_sentiment)
    enriched["sentimiento_etiqueta"] = payload.map(lambda item: item[0])
    enriched["sentimiento_score"] = payload.map(lambda item: int(item[1]))
    return enriched


def collapse_sentiment_to_3_classes(label: str, score: int) -> tuple[str, int]:
    """Convierte el contrato canónico de 5 clases al contrato histórico de 3 clases.

    Mapeo:
    - Muy Positivo / Positivo -> positivo (3)
    - Neutral -> neutral (2)
    - Negativo / Muy Negativo -> negativo (1)
    """
    normalized_label = str(label).strip().lower()
    normalized_score = int(score) if score is not None else 3

    if normalized_label in {"muy positivo", "positivo"} or normalized_score >= 4:
        return "positivo", 3
    if normalized_label in {"muy negativo", "negativo"} or normalized_score <= 2:
        return "negativo", 1
    return "neutral", 2


def add_sentiment_analysis_legacy_3(df: pd.DataFrame, comment_column: str = "comentario_original") -> pd.DataFrame:
    """Wrapper de retrocompatibilidad: agrega sentimiento colapsado en 3 clases.

    Reutiliza la clasificación canónica de 5 clases y luego colapsa etiquetas/score
    para mantener compatibilidad con tableros y exportables históricos.
    """
    enriched = add_sentiment_analysis(df, comment_column=comment_column)
    payload = list(
        zip(
            enriched["sentimiento_etiqueta"].fillna("Neutral").astype(str),
            pd.to_numeric(enriched["sentimiento_score"], errors="coerce").fillna(3).astype(int),
        )
    )
    collapsed = [collapse_sentiment_to_3_classes(label, score) for label, score in payload]
    enriched["sentimiento_etiqueta"] = [item[0] for item in collapsed]
    enriched["sentimiento_score"] = [int(item[1]) for item in collapsed]
    return enriched


def create_dataframe_from_comments(
    comments: Iterable[str],
    source: str,
    *,
    load_date: datetime | None = None,
    include_category_detail: bool = False,
    include_category_confidence: bool = False,
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
    with_categories = add_category_analysis(with_sentiment, comment_column="comentario_original")

    output_columns = list(CSV_COLUMN_ORDER)
    if include_category_detail:
        output_columns.append("categoria_detalle")
    if include_category_confidence:
        output_columns.append("categoria_confianza")

    return with_categories[output_columns].copy()


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
    """Exporta CSV maestro con todas las columnas analizadas.

    Incluye al final un bloque de resumen ejecutivo para lectura rapida.
    """
    full_columns = list(CSV_COLUMN_ORDER)
    if "categoria_detalle" in df.columns:
        full_columns.append("categoria_detalle")
    if "categoria_confianza" in df.columns:
        full_columns.append("categoria_confianza")

    aligned = validate_and_align_columns(
        df,
        required_order=full_columns,
        header_mapping=header_mapping,
    )

    columns = list(aligned.columns)
    summary_rows = _build_executive_summary_rows(df, columns)

    output_df = aligned
    if summary_rows:
        blank_row = {col: "" for col in columns}
        output_df = pd.concat(
            [aligned, pd.DataFrame([blank_row]), pd.DataFrame(summary_rows)],
            ignore_index=True,
        )

    buffer = io.StringIO()
    output_df.to_csv(buffer, index=False, encoding="utf-8-sig")
    return buffer.getvalue().encode("utf-8-sig")


def _build_executive_summary_rows(df: pd.DataFrame, columns: list[str]) -> list[dict[str, str]]:
    """Construye filas de resumen ejecutivo para anexar al CSV completo."""
    if not columns:
        return []

    col0 = columns[0]
    col1 = columns[1] if len(columns) > 1 else columns[0]
    col2 = columns[2] if len(columns) > 2 else col1

    def _empty_row() -> dict[str, str]:
        return {col: "" for col in columns}

    total = int(len(df))

    avg_score = 0.0
    if "sentimiento_score" in df.columns and total > 0:
        avg_score = float(pd.to_numeric(df["sentimiento_score"], errors="coerce").fillna(0).mean())

    sentiment_counts = {}
    if "sentimiento_etiqueta" in df.columns:
        sentiment_counts = (
            df["sentimiento_etiqueta"]
            .fillna("Neutral")
            .value_counts()
            .to_dict()
        )

    top_category = "Sin categoria"
    if "categoria" in df.columns and total > 0:
        mode_values = df["categoria"].dropna().mode()
        if not mode_values.empty:
            top_category = str(mode_values.iloc[0])

    rows: list[dict[str, str]] = []

    row = _empty_row()
    row[col0] = "RESUMEN_EJECUTIVO"
    row[col1] = "Total comentarios"
    row[col2] = str(total)
    rows.append(row)

    row = _empty_row()
    row[col0] = "RESUMEN_EJECUTIVO"
    row[col1] = "Promedio sentimiento"
    row[col2] = f"{avg_score:.2f}/5"
    rows.append(row)

    for label in ["Muy Positivo", "Positivo", "Neutral", "Negativo", "Muy Negativo"]:
        row = _empty_row()
        row[col0] = "RESUMEN_EJECUTIVO"
        row[col1] = f"Sentimiento {label}"
        row[col2] = str(int(sentiment_counts.get(label, 0)))
        rows.append(row)

    row = _empty_row()
    row[col0] = "RESUMEN_EJECUTIVO"
    row[col1] = "Categoria principal"
    row[col2] = top_category
    rows.append(row)

    return rows


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


# ============================================================================
# WRAPPERS PARA SISTEMA AUTOMÃTICO DE RETROALIMENTACIÃ“N
# ============================================================================


def record_comment_feedback(
    comment: str,
    predicted_label: str,
    predicted_score: int,
    correct_label: str,
    correct_score: int,
) -> None:
    """Registra feedback sobre clasificaciÃ³n de sentimiento.

    El sistema automÃ¡ticamente aprende de los comentarios marcados como
    incorrectos y mejora con el tiempo.

    Ejemplo:
    --------
    >>> record_comment_feedback(
    ...     comment="Que decepciÃ³n de escuela",
    ...     predicted_label="Neutral",
    ...     predicted_score=3,
    ...     correct_label="Muy Negativo",
    ...     correct_score=1
    ... )
    """
    feedback_system.record_feedback(
        comment, predicted_label, predicted_score, correct_label, correct_score
    )


def get_feedback_stats() -> dict:
    """Retorna estadÃ­sticas del sistema de feedback.

    Returns
    -------
    dict
        Accuracy, total de comentarios, etc.
    """
    return feedback_system.get_feedback_stats()


def get_mispredictions_by_type() -> dict:
    """Retorna mispredictions agrupadas por tipo de error."""
    return feedback_system.get_mispredictions_by_type()


def get_improvement_suggestions() -> dict:
    """Genera sugerencias automÃ¡ticas de mejora basadas en feedback.

    El sistema analiza los comentarios mal clasificados e identifica
    palabras/frases que deberÃ­an agregarse a los diccionarios.

    Returns
    -------
    dict
        Sugerencias por categorÃ­a con palabras candidatas
    """
    return feedback_system.get_improvement_suggestions()


def apply_suggestions() -> None:
    """Aplica sugerencias automÃ¡ticamente al sistema.

    Actualiza VERY_POSITIVE_WORDS y VERY_NEGATIVE_WORDS
    con palabras sugeridas automÃ¡ticamente.
    """
    suggestions = feedback_system.get_improvement_suggestions()
    feedback_system.apply_suggestions_to_processor(suggestions)


def get_feedback_report() -> str:
    """Genera reporte human-readable del feedback acumulado."""
    return feedback_system.get_feedback_report()

