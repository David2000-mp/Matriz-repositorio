"""Utilidades para analisis demografico y geografico de colegios."""

from __future__ import annotations

import unicodedata
from typing import Optional, Tuple

import pandas as pd


MEXICO_CENTER = {"lat": 23.6345, "lon": -102.5528}
CITY_IMPACT_ORDER = ["Impacto bajo", "Impacto medio", "Impacto alto"]
CITY_IMPACT_COLORS = {
    "Impacto bajo": "#D62828",
    "Impacto medio": "#0756C9",
    "Impacto alto": "#FFB81C",
}

# Coordenadas aproximadas para principales ciudades y localidades de Mexico.
MEXICO_CITY_COORDS = {
    # Zonas Metropolitanas y Ciudades Principales
    "ciudad de mexico": (19.4326, -99.1332),
    "cdmx": (19.4326, -99.1332),
    "guadalajara": (20.6597, -103.3496),
    "monterrey": (25.6866, -100.3161),
    "puebla": (19.0414, -98.2063),
    "puebla de zaragoza": (19.0453, -98.1975),
    "toluca": (19.2826, -99.6557),
    "toluca de lerdo": (19.2925, -99.6569),
    "tijuana": (32.5149, -117.0382),
    "leon": (21.1220, -101.6805),
    "ciudad juarez": (31.7450, -106.4850),
    "torreon": (25.5428, -103.4068),
    "queretaro": (20.5888, -100.3899),
    "santiago de queretaro": (20.5888, -100.3899),
    "merida": (20.9674, -89.5926),
    "san luis potosi": (22.1565, -100.9855),
    "aguascalientes": (21.8853, -102.2916),
    "mexicali": (32.6245, -115.4523),
    "saltillo": (25.4267, -100.9954),
    "cuernavaca": (18.9242, -99.2216),
    "culiacan": (24.8091, -107.3940),
    "chihuahua": (28.6320, -106.0691),
    "morelia": (19.7008, -101.1844),
    "hermosillo": (29.0729, -110.9559),
    "cancun": (21.1619, -86.8515),
    "veracruz": (19.1738, -96.1342),
    "xalapa": (19.5438, -96.9102),
    "tuxtla gutierrez": (16.7516, -93.1166),
    "oaxaca": (17.0732, -96.7266),
    "oaxaca de juarez": (17.0678, -96.7200),
    "villahermosa": (17.9892, -92.9475),
    "pachuca": (20.1011, -98.7591),
    "tlaxcala": (19.3139, -98.2404),
    "zacatecas": (22.7709, -102.5832),
    "tepic": (21.5095, -104.8957),
    "victoria de durango": (24.0277, -104.6532),
    "durango": (24.0277, -104.6532),
    "ciudad victoria": (23.7369, -99.1411),
    "chetumal": (18.5002, -88.2961),
    "campeche": (19.8301, -90.5349),
    "san francisco de campeche": (19.8301, -90.5349),
    "colima": (19.2452, -103.7241),
    "la paz": (24.1426, -110.3127),
    "chilpancingo": (17.5500, -99.5000),

    # Municipios del Estado de Mexico y Zona Metropolitana
    "nezahualcoyotl": (19.4081, -99.0186),
    "ecatepec de morelos": (19.6097, -99.0600),
    "metepec": (19.2511, -99.6047),
    "chimalhuacan": (19.4375, -98.9542),
    "naucalpan de juarez": (19.4753, -99.2378),
    "tlalnepantla": (19.5400, -99.1900),
    "cuautitlan izcalli": (19.6439, -99.2161),
    "atizapan de zaragoza": (19.5558, -99.2492),
    "san miguel zinacantepec": (19.2908, -99.7389),
    "san andres ocotlan": (19.1869, -99.5801),
    "san mateo atenco": (19.2673, -99.5327),
    "chalco": (19.2611, -98.8978),
    "valle de chalco": (19.2889, -98.9419),
    "municipio de tecamac": (19.7125, -98.9678),
    "tecamac": (19.7125, -98.9678),
    "la magdalena chichicaspa": (19.4125, -99.3242),
    "lopez mateos": (19.5558, -99.2492),
    "ciudad lopez mateos": (19.5558, -99.2492),
    "ixtapaluca": (19.3181, -98.8825),
    "municipio de almoloya de juarez": (19.3667, -99.7611),
    "almoloya de juarez": (19.3667, -99.7611),
    "lerma": (19.2908, -99.5113),
    "ocoyoacac": (19.2731, -99.4600),

    # Jalisco y zonas aledanas
    "zapopan": (20.7203, -103.3919),
    "tlaquepaque": (20.6397, -103.3153),
    "tonala": (20.6242, -103.2411),
    "puerto vallarta": (20.6534, -105.2253),
    "arandas": (20.7053, -102.3461),
    "tepatitlan de morelos": (20.8142, -102.7689),
    "tepatitlan": (20.8142, -102.7689),

    # Norte y Frontera
    "ensenada": (31.8667, -116.5964),
    "nogales": (31.3086, -110.9422),
    "nuevo laredo": (27.4763, -99.5164),
    "reynosa": (26.0806, -98.2883),
    "matamoros": (25.8797, -97.5042),
    "tampico": (22.2533, -97.8636),
    "monclova": (26.9078, -101.4222),
    "piedras negras": (28.7062, -100.5226),
    "los mochis": (25.7928, -108.9902),

    # Centro y Bajio (Guanajuato, Michoacan, etc)
    "celaya": (20.5222, -100.8122),
    "irapuato": (20.6736, -101.3508),
    "salamanca": (20.5728, -101.1969),
    "guanajuato": (21.0190, -101.2574),
    "san miguel de allende": (20.9142, -100.7436),
    "comonfort": (20.7189, -100.7606),
    "apaseo el grande": (20.5469, -100.6867),
    "cortazar": (20.4828, -100.9611),
    "santa cruz de juventino rosas": (20.6433, -100.9942),
    "juventino rosas": (20.6433, -100.9942),
    "uruapan": (19.3967, -102.0392),
    "zamora": (19.9831, -102.2858),
    "abasolo": (20.4497, -101.5308),
    "cuchicuato": (20.6408, -101.4022),

    # Bloque Hidalgo
    "chapantongo": (20.2858, -99.4125),
    "san agustin tlaxiaca": (20.1167, -98.8833),
    "carboneras": (20.1245, -98.7183),
    "municipio de zempoala": (19.9142, -98.6678),
    "zempoala": (19.9142, -98.6678),
    "pachuquilla": (20.0717, -98.6947),
    "zapotlan de juarez": (19.9722, -98.8611),
    "santiago tulantepec": (20.0381, -98.4086),
    "santa maria la calera": (20.0989, -98.7667),
    "epazoyucan": (20.0167, -98.6333),
    "tulancingo de bravo": (20.0825, -98.3697),
    "tulancingo": (20.0825, -98.3697),
    "tepatepec": (20.2411, -99.0713),

    # Bloque Sahuayo / Michoacan
    "sahuayo de morelos": (20.0569, -102.7236),
    "sahuayo": (20.0569, -102.7236),
    "jiquilpan": (19.9839, -102.7039),
    "jiquilpan de juarez": (19.9839, -102.7039),
    "venustiano carranza": (20.1111, -102.6667),
    "villamar": (20.0208, -102.6000),
    "gomez": (19.9333, -102.2333),
    "jacona": (19.9511, -102.3044),
    "jacona de plancarte": (19.9511, -102.3044),
    "chavinda": (20.0067, -102.4589),
    "villa chavinda": (20.0067, -102.4589),
    "tangancicuaro": (19.8886, -102.2056),
    "chilchota": (19.8519, -102.1808),

    # Bloque Queretaro
    "el marques": (20.6628, -100.3189),
    "corregidora": (20.5364, -100.4439),
    "san jose el alto": (20.6406, -100.3958),
    "san juan del rio": (20.3889, -99.9969),
    "juriquilla": (20.6894, -100.4464),
    "tlacote el bajo": (20.6453, -100.5186),
    "salitre": (20.6611, -100.4222),
    "el salitre": (20.6611, -100.4222),
    "colon": (20.7856, -100.0522),
    "pedro escobedo": (20.5019, -100.1417),
    "cadereyta": (20.6978, -99.8139),
    "cadereyta de montes": (20.6978, -99.8139),
    "tequisquiapan": (20.5186, -99.8958),
    "santa rosa jauregui": (20.7431, -100.4456),

    # Bloque San Luis Potosi
    "escalerillas": (22.1111, -101.0772),
    "soledad diez gutierrez": (22.1833, -100.9333),
    "soledad de graciano sanchez": (22.1833, -100.9333),
    "mexquitic": (22.2706, -101.1147),
    "mexquitic de carmona": (22.2706, -101.1147),
    "pozos": (22.0944, -100.8806),
    "villa de pozos": (22.0944, -100.8806),
    "arista": (22.6508, -100.8447),
    "villa de arista": (22.6508, -100.8447),
    "ciudad valles": (21.9847, -99.0172),
    "tamazunchale": (21.2603, -98.7881),
    "cerritos": (22.4272, -100.2764),
    "santa maria del rio": (21.7981, -100.7336),
    "matehuala": (23.6489, -100.6425),

    # Puebla y Veracruz (Bloque Orizaba-Cordoba)
    "tehuacan": (18.4608, -97.3942),
    "ciudad avila camacho": (20.3850, -97.8767),
    "orizaba": (18.8497, -97.1036),
    "municipio de ixtaczoquitlan": (18.8488, -97.0601),
    "ixtaczoquitlan": (18.8488, -97.0601),
    "rio blanco": (18.8350, -97.1472),
    "mariano escobedo": (18.9167, -97.1333),
    "cordoba": (18.8844, -96.9255),
    "camerino z. mendoza": (18.8155, -97.1819),
    "camerino z mendoza": (18.8155, -97.1819),
    "rafael delgado": (18.8180, -97.0752),
    "coatzacoalcos": (18.1333, -94.4333),
    "minatitlan": (18.0000, -94.5500),

    # Sur y Peninsula
    "acapulco": (16.8531, -99.8236),
    "potoichan": (17.4470, -98.6650),
    "tapachula": (14.9080, -92.2617),
    "las margaritas": (16.3158, -91.9817),
    "san cristobal de las casas": (16.7370, -92.6375),
    "santo domingo tehuantepec": (16.3236, -95.2408),
    "playa del carmen": (20.6296, -87.0739),
    "ciudad del carmen": (18.6450, -91.8217),

    # Internacionales (añadido por solicitud)
    "maracaibo": (10.6417, -71.6295),
}

# Fallback por nombre crudo tal como suele venir en hojas (con acentos y forma oficial).
RAW_CITY_COORDS = {
    # Estado de Mexico y CDMX
    "Toluca de Lerdo": (19.2925, -99.6569),
    "Nezahualcóyotl": (19.4081, -99.0186),
    "Ecatepec de Morelos": (19.6097, -99.0600),
    "Metepec": (19.2511, -99.6047),
    "Chimalhuacán": (19.4375, -98.9542),
    "Naucalpan de Juárez": (19.4753, -99.2378),
    "Tlalnepantla de Baz": (19.5400, -99.1900),
    "Cuautitlán Izcalli": (19.6439, -99.2161),
    "Atizapán de Zaragoza": (19.5558, -99.2492),
    "San Miguel Zinacantepec": (19.2908, -99.7389),
    "San Andrés Ocotlán": (19.1869, -99.5801),
    "San Mateo Atenco": (19.2673, -99.5327),
    "Municipio de Tecámac": (19.7125, -98.9678),
    "La Magdalena Chichicaspa": (19.4125, -99.3242),
    "López Mateos": (19.5558, -99.2492),
    "Ixtapaluca": (19.3181, -98.8825),
    "Municipio de Almoloya de Juárez": (19.3667, -99.7611),
    "Lerma": (19.2908, -99.5113),
    "Ocoyoacac": (19.2731, -99.4600),

    # Resto del pais
    "Puebla de Zaragoza": (19.0453, -98.1975),
    "Zapopan": (20.7203, -103.3919),
    "Arandas": (20.7053, -102.3461),
    "Tepatitlán de Morelos": (20.8142, -102.7689),
    "Uruapan": (19.3967, -102.0392),
    "Ciudad Juárez": (31.7450, -106.4850),
    "Oaxaca de Juárez": (17.0678, -96.7200),
    "Santo Domingo Tehuantepec": (16.3236, -95.2408),
    "Santiago de Querétaro": (20.5888, -100.3899),
    "León de los Aldama": (21.1220, -101.6805),
    "San Luis Potosí": (22.1565, -100.9855),
    "Santa María del Río": (21.7981, -100.7336),
    "Matehuala": (23.6489, -100.6425),
    "Victoria de Durango": (24.0277, -104.6532),
    "San Francisco de Campeche": (19.8301, -90.5349),
    "San Cristóbal de las Casas": (16.7370, -92.6375),
    "Potoichán": (17.4470, -98.6650),
    "Las Margaritas": (16.3158, -91.9817),
    "Comonfort": (20.7189, -100.7606),
    "Apaseo el Grande": (20.5469, -100.6867),
    "Cortazar": (20.4828, -100.9611),
    "Santa Cruz de Juventino Rosas": (20.6433, -100.9942),
    "Juventino Rosas": (20.6433, -100.9942),
    "Abasolo": (20.4497, -101.5308),
    "Cuchicuato": (20.6408, -101.4022),
    "Sahuayo de Morelos": (20.0569, -102.7236),
    "Sahuayo": (20.0569, -102.7236),
    "Jiquilpan": (19.9839, -102.7039),
    "Jiquilpan de Juárez": (19.9839, -102.7039),
    "Venustiano Carranza": (20.1111, -102.6667),
    "Villamar": (20.0208, -102.6000),
    "Gómez": (19.9333, -102.2333),
    "Jacona": (19.9511, -102.3044),
    "Jacona de Plancarte": (19.9511, -102.3044),
    "Chavinda": (20.0067, -102.4589),
    "Villa Chavinda": (20.0067, -102.4589),
    "Tangancicuaro": (19.8886, -102.2056),
    "Chilchota": (19.8519, -102.1808),
    "El Marqués": (20.6628, -100.3189),
    "Corregidora": (20.5364, -100.4439),
    "San José el Alto": (20.6406, -100.3958),
    "San Juan del Río": (20.3889, -99.9969),
    "Escalerillas": (22.1111, -101.0772),
    "Juriquilla": (20.6894, -100.4464),
    "Ciudad Ávila Camacho": (20.3850, -97.8767),
    "Orizaba": (18.8497, -97.1036),
    "Soledad Díez Gutiérrez": (22.1833, -100.9333),
    "Soledad de Graciano Sánchez": (22.1833, -100.9333),
    "Mexquitic": (22.2706, -101.1147),
    "Mexquitic de Carmona": (22.2706, -101.1147),
    "Pozos": (22.0944, -100.8806),
    "Villa de Pozos": (22.0944, -100.8806),
    "Tlacote el Bajo": (20.6453, -100.5186),
    "Salitre": (20.6611, -100.4222),
    "El Salitre": (20.6611, -100.4222),
    "Colón": (20.7856, -100.0522),
    "Pedro Escobedo": (20.5019, -100.1417),
    "Cadereyta": (20.6978, -99.8139),
    "Cadereyta de Montes": (20.6978, -99.8139),
    "Arista": (22.6508, -100.8447),
    "Villa de Arista": (22.6508, -100.8447),
    "Tequisquiapan": (20.5186, -99.8958),
    "Santa Rosa Jáuregui": (20.7431, -100.4456),
    "Ciudad Valles": (21.9847, -99.0172),
    "Tamazunchale": (21.2603, -98.7881),
    "Cerritos": (22.4272, -100.2764),
    "Los Mochis": (25.7928, -108.9902),

    # Agregados Hidalgo
    "Chapantongo": (20.2858, -99.4125),
    "San Agustín Tlaxiaca": (20.1167, -98.8833),
    "Carboneras": (20.1245, -98.7183),
    "Municipio de Zempoala": (19.9142, -98.6678),
    "Pachuquilla": (20.0717, -98.6947),
    "Zapotlán de Juárez": (19.9722, -98.8611),
    "Santiago Tulantepec": (20.0381, -98.4086),
    "Santa María La Calera": (20.0989, -98.7667),
    "Epazoyucan": (20.0167, -98.6333),
    "Tulancingo de Bravo": (20.0825, -98.3697),
    "Tepatepec": (20.2411, -99.0713),

    # Agregados Veracruz / Zonas limítrofes
    "Municipio de Ixtaczoquitlán": (18.8488, -97.0601),
    "Río Blanco": (18.8350, -97.1472),
    "Mariano Escobedo": (18.9167, -97.1333),
    "Córdoba": (18.8844, -96.9255),
    "Camerino Z. Mendoza": (18.8155, -97.1819),
    "Rafael Delgado": (18.8180, -97.0752),

    # Internacional
    "Monasterio de Yuste": (40.1142, -5.7389),
    "Maracaibo": (10.6417, -71.6295),
}

AGE_ORDER = [
    "13-17",
    "18-24",
    "25-34",
    "35-44",
    "45-54",
    "55-64",
    "65+",
]

OTHER_AGE_LABEL = "Otros"


def _filter_nonnegative_values(df: pd.DataFrame) -> pd.DataFrame:
    """Conserva solo filas con un valor numerico valido y no negativo."""
    local = df.copy()
    local["valor"] = pd.to_numeric(local["valor"], errors="coerce")
    return local[local["valor"].notna() & (local["valor"] >= 0)].copy()


def _prepare_demographic_categories(df: pd.DataFrame) -> pd.DataFrame:
    """Limpia sexo/edad y agrupa rangos no catalogados bajo ``Otros``."""
    local = df[df["edad"].notna() & df["sexo"].notna()].copy()
    local["edad"] = local["edad"].astype(str).str.strip()
    local["sexo"] = local["sexo"].astype(str).str.strip()
    local = local[(local["edad"] != "") & (local["sexo"] != "")].copy()
    local.loc[~local["edad"].isin(AGE_ORDER), "edad"] = OTHER_AGE_LABEL
    return local


def normalize_text(value: str) -> str:
    """Normaliza texto para comparaciones robustas."""
    value = str(value or "").strip().lower()
    value = unicodedata.normalize("NFKD", value)
    value = "".join(ch for ch in value if not unicodedata.combining(ch))
    # Conserva alfanumericos y espacios para evitar fallos por signos/formatos heterogeneos.
    value = "".join(ch if (ch.isalnum() or ch.isspace()) else " " for ch in value)
    return " ".join(value.split())


CITY_COORDS = {
    **MEXICO_CITY_COORDS,
    **{normalize_text(name): coords for name, coords in RAW_CITY_COORDS.items()},
}


def _resolve_city_coords(city_norm: str):
    """Resuelve coordenadas exactas tras normalizar variantes controladas."""
    if not city_norm:
        return pd.NA, pd.NA

    if city_norm in CITY_COORDS:
        return CITY_COORDS[city_norm]

    candidates = [city_norm]

    qualifiers = [
        "estado de mexico",
        "edomex",
        "estado de",
        "municipio de",
    ]
    for cand in list(candidates):
        cleaned = cand
        for q in qualifiers:
            cleaned = cleaned.replace(q, " ")
        cleaned = " ".join(cleaned.split())
        if cleaned and cleaned not in candidates:
            candidates.append(cleaned)

    for cand in candidates:
        if cand in CITY_COORDS:
            return CITY_COORDS[cand]

    return pd.NA, pd.NA


def apply_demographic_filters(
    df: pd.DataFrame,
    colegio: Optional[str] = None,
    plataforma: Optional[str] = None,
    start_date: Optional[pd.Timestamp] = None,
    end_date: Optional[pd.Timestamp] = None,
) -> pd.DataFrame:
    """Aplica filtros de colegio, plataforma y fecha sobre base demografica."""
    if df is None or df.empty:
        return pd.DataFrame(columns=df.columns if df is not None else None)

    filtered = df.copy()

    if "valor" in filtered.columns:
        filtered = _filter_nonnegative_values(filtered)

    if "fecha_reporte" in filtered.columns:
        filtered["fecha_reporte"] = pd.to_datetime(
            filtered["fecha_reporte"], errors="coerce", format="mixed"
        )

    if colegio and colegio != "Todos":
        filtered = filtered[filtered["colegio"].astype(str) == str(colegio)]

    if plataforma and plataforma != "Todas":
        filtered = filtered[filtered["plataforma"].astype(str) == str(plataforma)]

    if start_date is not None:
        start_date = pd.to_datetime(start_date).normalize()
        filtered = filtered[filtered["fecha_reporte"] >= start_date]

    if end_date is not None:
        # Streamlit entrega una fecha a medianoche. Usar un limite exclusivo al
        # inicio del dia siguiente conserva registros con cualquier hora del fin.
        end_exclusive = pd.to_datetime(end_date).normalize() + pd.Timedelta(days=1)
        filtered = filtered[filtered["fecha_reporte"] < end_exclusive]

    return filtered


def build_demography_base(df: pd.DataFrame) -> pd.DataFrame:
    """Construye agregacion de Demografia base por edad y sexo."""
    if df is None or df.empty:
        return pd.DataFrame(columns=["edad", "sexo", "valor", "participacion_pct"])

    local = _filter_nonnegative_values(df)
    local["criterio_norm"] = local["criterio"].apply(normalize_text)
    local = local[local["criterio_norm"] == "demografia base"]
    local = _prepare_demographic_categories(local)

    if local.empty:
        return pd.DataFrame(columns=["edad", "sexo", "valor", "participacion_pct"])

    agg = (
        local.groupby(["edad", "sexo"], as_index=False)["valor"]
        .sum()
        .sort_values(["edad", "sexo"])
    )

    total = float(agg["valor"].sum())
    agg["participacion_pct"] = (agg["valor"] / total * 100.0) if total else 0.0

    age_categories = [*AGE_ORDER, OTHER_AGE_LABEL]
    agg["edad"] = pd.Categorical(agg["edad"], categories=age_categories, ordered=True)
    agg = agg.sort_values(["edad", "sexo"]).reset_index(drop=True)
    agg["edad"] = agg["edad"].astype(str)
    return agg


def build_city_report(df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Construye reporte por ciudad y separa ciudades mapeadas/no mapeadas.

    Returns:
        Tuple[mapped_df, unmapped_df]
    """
    if df is None or df.empty:
        empty = pd.DataFrame(columns=["ubicacion", "valor_total", "participacion_pct", "lat", "lon"])
        return empty, empty

    local = _filter_nonnegative_values(df)
    local["criterio_norm"] = local["criterio"].apply(normalize_text)
    local = local[local["criterio_norm"] == "ciudad"]
    local = local[local["ubicacion"].astype(str).str.strip() != ""]

    if local.empty:
        empty = pd.DataFrame(columns=["ubicacion", "valor_total", "participacion_pct", "lat", "lon"])
        return empty, empty

    city = (
        local.groupby("ubicacion", as_index=False)["valor"]
        .sum()
        .rename(columns={"valor": "valor_total"})
        .sort_values("valor_total", ascending=False)
    )
    total = float(city["valor_total"].sum())
    city["participacion_pct"] = (city["valor_total"] / total * 100.0) if total else 0.0

    city["city_norm"] = city["ubicacion"].apply(normalize_text)
    city[["lat", "lon"]] = city["city_norm"].apply(
        lambda city_name: pd.Series(_resolve_city_coords(city_name))
    )

    mapped = city.dropna(subset=["lat", "lon"]).copy()
    unmapped = city[city["lat"].isna() | city["lon"].isna()].copy()

    mapped = mapped.drop(columns=["city_norm"]).reset_index(drop=True)
    unmapped = unmapped.drop(columns=["city_norm"]).reset_index(drop=True)
    return mapped, unmapped


def classify_city_impact(values: pd.Series) -> pd.Series:
    """Clasifica ciudades por terciles ordinales sin perder empates ni filas.

    El menor impacto se pinta rojo, el intermedio azul y el mayor amarillo.
    Para uno o dos registros se preservan los extremos visuales esperados.
    """
    numeric = pd.to_numeric(values, errors="coerce").fillna(0.0)
    if numeric.empty:
        return pd.Series(index=values.index, dtype="object")

    labels = pd.Series("Impacto medio", index=values.index, dtype="object")
    total = len(numeric)

    if total == 1:
        labels.iloc[0] = "Impacto alto"
        return labels
    if total == 2:
        ordered_index = numeric.sort_values(kind="stable").index.tolist()
        if numeric.nunique() == 1:
            labels.loc[ordered_index] = "Impacto medio"
            return labels
        labels.loc[ordered_index[0]] = "Impacto bajo"
        labels.loc[ordered_index[1]] = "Impacto alto"
        return labels

    percentiles = numeric.rank(method="average", pct=True)
    labels.loc[percentiles <= 1 / 3] = "Impacto bajo"
    labels.loc[percentiles > 2 / 3] = "Impacto alto"
    return labels


def build_network_comparison(df: pd.DataFrame, selected_school: str) -> pd.DataFrame:
    """
    Compara distribucion de colegio seleccionado vs promedio de red.

    Regla critica: el promedio de red excluye siempre al colegio seleccionado.
    """
    if df is None or df.empty or not selected_school:
        return pd.DataFrame(
            columns=[
                "edad",
                "sexo",
                "segmento",
                "colegio_valor",
                "colegio_pct",
                "red_valor",
                "red_pct",
                "delta_pp",
            ]
        )

    local = _filter_nonnegative_values(df)
    local["criterio_norm"] = local["criterio"].apply(normalize_text)
    base = local[local["criterio_norm"] == "demografia base"].copy()
    base = _prepare_demographic_categories(base)
    if base.empty:
        return pd.DataFrame()

    selected = base[base["colegio"].astype(str) == str(selected_school)].copy()
    network = base[base["colegio"].astype(str) != str(selected_school)].copy()

    if selected.empty or network.empty:
        return pd.DataFrame()

    selected_agg = (
        selected.groupby(["edad", "sexo"], as_index=False)["valor"]
        .sum()
        .rename(columns={"valor": "colegio_valor"})
    )
    network_agg = (
        network.groupby(["edad", "sexo"], as_index=False)["valor"]
        .sum()
        .rename(columns={"valor": "red_valor"})
    )

    selected_total = float(selected_agg["colegio_valor"].sum())
    network_total = float(network_agg["red_valor"].sum())

    selected_agg["colegio_pct"] = (selected_agg["colegio_valor"] / selected_total * 100.0) if selected_total else 0.0
    network_agg["red_pct"] = (network_agg["red_valor"] / network_total * 100.0) if network_total else 0.0

    merged = pd.merge(selected_agg, network_agg, on=["edad", "sexo"], how="outer").fillna(0)
    merged["delta_pp"] = merged["colegio_pct"] - merged["red_pct"]
    merged["segmento"] = merged["edad"].astype(str) + " | " + merged["sexo"].astype(str)
    age_categories = [*AGE_ORDER, OTHER_AGE_LABEL]
    merged["edad"] = pd.Categorical(merged["edad"], categories=age_categories, ordered=True)
    merged = merged.sort_values(["edad", "sexo"]).reset_index(drop=True)
    merged["edad"] = merged["edad"].astype(str)
    return merged
