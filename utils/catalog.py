"""
Catálogo centralizado de instituciones y plataformas.

Este módulo reemplaza definiciones dispersas y expone constantes
que deben usarse desde las vistas y utilidades.
"""
from typing import Dict

# Plataformas estándar
PLATAFORMAS_REQUERIDAS = ["Facebook", "Instagram", "TikTok", "Twitter"]

# Catálogo maestro (copiado desde utils.data_manager original)
COLEGIOS_MARISTAS: Dict[str, Dict[str, str]] = {
    "Centro Universitario México": {
        "Facebook": "https://www.facebook.com/maristascum",
        "Instagram": "https://www.instagram.com/maristas_cum/",
        "Twitter": "https://twitter.com/maristas_cum"
    },
    "Colegio México Bachillerato": {
        "Facebook": "https://www.facebook.com/colegio.mexico.bachillerato.acoxpa.oficial",
        "Instagram": "https://www.instagram.com/cmbacoxpa/",
        "Twitter": "https://twitter.com/cmorieduu"
    },
    "Instituto México Secundaria": {
        "Facebook": "https://www.facebook.com/InstitutoMexicoSecundaria",
        "Instagram": "https://www.instagram.com/institutomexicosecundaria/",
        "Twitter": "https://twitter.com/marista_imss"
    },
    "Instituto México Primaria": {
        "Facebook": "https://www.facebook.com/imprimaria",
        "Instagram": "https://www.instagram.com/institutomexicoprimaria/",
        "Twitter": "https://twitter.com/imprimaria"
    },
    "Colegio México Roma": {
        "Facebook": "https://www.facebook.com/ColegioMexicoRoma",
        "Instagram": "https://www.instagram.com/institutomexicosecundaria/",
        "Twitter": "https://twitter.com/ColegioMexicoDF"
    },
    "Instituto México Toluca": {
        "Facebook": "https://www.facebook.com/InstitutoMexicodeToluca",
        "Instagram": "https://www.instagram.com/imt.secuprepa/",
    },
    "Instituto México Toluca Primaria": {
        "Facebook": "",
        "Instagram": "",
        "TikTok": "",
        "Twitter": "",
    },
    "Instituto Hidalguense": {
        "Facebook": "https://www.facebook.com/MaristasIH",
        "Instagram": "https://www.instagram.com/maristas_ih/",
        "Twitter": "https://twitter.com/Ins_Hidalguense"
    },
    "Colegio México Orizaba": {
        "Facebook": "https://www.facebook.com/cmoriedu",
        "Instagram": "https://www.instagram.com/cmoriedu/"
    },
    "Instituto Potosino": {
        "Facebook": "https://www.facebook.com/Oficialpotosino",
        "Instagram": "https://www.instagram.com/institutopotosino/",
        "Twitter": "https://twitter.com/PotosinoMarista"
    },
    "Instituto Queretano San Javier": {
        "Facebook": "https://www.facebook.com/MaristaSanJavier",
        "Instagram": "https://www.instagram.com/iqm_qro/",
        "Twitter": "https://twitter.com/San_Javier"
    },
    "Colegio Lic. Manuel Concha": {
        "Facebook": "https://www.facebook.com/ColegioManuelConcha",
        "Instagram": "https://www.instagram.com/marista_celaya/",
        "Twitter": "https://twitter.com/MaristaCelaya"
    },
    "Colegio Pedro Martínez Vázquez": {
        "Facebook": "https://www.facebook.com/maristasirapuato",
        "Instagram": "https://www.instagram.com/maristasirapuato/",
        "Twitter": "https://twitter.com/maristairapuatoo"
    },
    "Colegio Jacona": {
        "Facebook": "https://www.facebook.com/CJMarista",
        "Instagram": "https://www.instagram.com/maristas_jacona/",
        "Twitter": "https://twitter.com/MaristasJaconac"
    },
    "Instituto Sahuayense": {
        "Instagram": "https://www.instagram.com/sahuayensemarista/"
    },
    "Universidad Marista de México": {
        "Facebook": "https://www.facebook.com/umaristamx",
        "Instagram": "https://www.instagram.com/umarista_mx/",
        "Twitter": "https://twitter.com/umaristaa"
    },
    "Universidad Marista de Querétaro": {
        "Instagram": "https://www.instagram.com/umaristaqro"
    },
    "Universidad Marista SLP": {
        "Instagram": "https://www.instagram.com/universidadmaristaslp/"
    },
    "Maristas México Central": {
        "Facebook": "https://www.facebook.com/MaristasMexicoCentral",
        "Instagram": "https://www.instagram.com/maristas_mexicocentral/",
        "Twitter": "https://twitter.com/MaristasCentral",
        "TikTok": "https://www.tiktok.com/@maristascentral"
    }
}

# Normalizar catálogo: asegurar que TODAS las instituciones tengan
# las 4 plataformas estándar aunque estén pendientes de URL.
for _school, _platforms in COLEGIOS_MARISTAS.items():
    for _plat in PLATAFORMAS_REQUERIDAS:
        _platforms.setdefault(_plat, "")
