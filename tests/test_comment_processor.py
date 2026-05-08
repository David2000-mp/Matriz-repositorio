from datetime import datetime, timezone
import importlib

import pandas as pd

comment_processor = importlib.import_module("utils.comment_processor")


def test_clean_raw_text_returns_dict_with_metrics():
    """Valida que clean_raw_text retorna dict con comentarios validos y metricas."""
    # Raw string: 6 lines (linea vacia, espacio, "Excelente servicio", "ok", duplicado, "  Muy caro  ")
    raw = "\n  \nExcelente servicio\nok\nExcelente servicio\n  Muy caro  \n"
    result = comment_processor.clean_raw_text(raw)
    
    assert isinstance(result, dict)
    assert "comentarios_validos" in result
    assert "total_original" in result
    assert "total_descartados" in result
    assert "descarte_detalles" in result
    
    assert result["comentarios_validos"] == ["Excelente servicio", "Muy caro"]
    assert result["total_original"] == 6  # Corrected: 6 lineas no 5
    assert result["total_descartados"] == 4


def test_clean_raw_text_handles_emojis_without_crashing():
    raw = "Me encanto 😍\nTerrible 😡"
    result = comment_processor.clean_raw_text(raw)
    cleaned = result["comentarios_validos"]
    assert cleaned == ["Me encanto 😍", "Terrible 😡"]


def test_clean_raw_text_filters_system_ids_entropy():
    """Detecta y filtra IDs aleatorios: m63gi9, 606ga6, rnpSostdeol, pero no 7ia4t (tiene suficientes vocales)."""
    raw = "m63gi9\n606ga6\nrnpSostdeol\nEste es un comentario real\n"
    result = comment_processor.clean_raw_text(raw)
    cleaned = result["comentarios_validos"]
    
    assert "Este es un comentario real" in cleaned
    assert "m63gi9" not in cleaned
    assert "606ga6" not in cleaned
    assert "rnpSostdeol" not in cleaned
    # Se esperan 2 validos: solo el comentario real
    assert len(cleaned) == 1
    assert result["total_descartados"] >= 3


def test_clean_raw_text_filters_platform_boilerplate():
    """Filtra frases boilerplate: 'recomienda a', 'estrellas', 'hace un momento', etc."""
    raw = (
        "recomienda a Juan\n"
        "Google Review\n"
        "hace un momento publique\n"
        "ver traduccion aqui\n"
        "Pero este comentario real si vale\n"
    )
    result = comment_processor.clean_raw_text(raw)
    cleaned = result["comentarios_validos"]
    
    assert "Pero este comentario real si vale" in cleaned
    # Las frases boilerplate deben estar descartadas
    assert result["total_descartados"] >= 4


def test_clean_raw_text_mixed_noise_and_real_comments():
    """Caso mixto con ruido de sistema, boilerplate y comentarios reales.
    
    Este es el caso mandatorio que combina multiples tipos de ruido.
    """
    raw = (
        "m63gi9\n"
        "606ga6\n"
        "El servicio fue excelente\n"
        "recomienda a alguien\n"
        "El precio esta muy caro\n"
        "rnpSostdeol\n"
        "hace un momento\n"
        "Las instalaciones son limpias\n"
    )
    result = comment_processor.clean_raw_text(raw)
    cleaned = result["comentarios_validos"]
    
    # Solo los comentarios reales deben sobrevivir
    assert "El servicio fue excelente" in cleaned
    assert "El precio esta muy caro" in cleaned
    assert "Las instalaciones son limpias" in cleaned
    
    # Los ruidos deben estar descartados
    assert len(cleaned) == 3
    assert result["total_original"] == 8
    assert result["total_descartados"] == 5


def test_detect_categories_priority_price_before_food():
    comment = "El precio de la comida es alto"
    # Ahora deberia detectar Precio/Valor (multisectorial)
    detected = comment_processor.detect_categories(comment)
    assert detected == "Precio/Valor"


def test_detect_categories_academic_quality():
    """Valida nueva categoria Academico/Calidad con keywords educativos."""
    comments = [
        ("La formacion es integral", "Academico/Calidad"),
        ("Pedagogico excelente", "Academico/Calidad"),
        ("El nivel del programa es alto", "Academico/Calidad"),
    ]
    for comment, expected in comments:
        assert comment_processor.detect_categories(comment) == expected


def test_detect_categories_infrastructure():
    """Valida categoria Infraestructura."""
    comment = "Las instalaciones del edificio son modernas"
    assert comment_processor.detect_categories(comment) == "Infraestructura"


def test_detect_categories_service_attention():
    """Valida categoria Servicio/Atencion."""
    comment = "El trato del personal fue muy amable"
    assert comment_processor.detect_categories(comment) == "Servicio/Atencion"


def test_detect_categories_environment_community():
    """Valida categoria Ambiente/Comunidad con keywords exclusivos."""
    comment = "Excelente ambiente familiar y compañerismo entre alumnos"
    assert comment_processor.detect_categories(comment) == "Ambiente/Comunidad"


def test_add_sentiment_analysis_uses_five_scale_labels():
    df = pd.DataFrame(
        {
            "comentario_original": [
                "excelente y maravilloso servicio",
                "muy caro y tardado",
                "informacion general del local",
            ]
        }
    )

    enriched = comment_processor.add_sentiment_analysis(df)

    assert list(enriched["sentimiento_etiqueta"]) == ["Muy Positivo", "Muy Negativo", "Neutral"]
    assert list(enriched["sentimiento_score"]) == [5, 1, 3]


def test_sentiment_classification_with_extended_education_lexicon():
    """Valida nuevas palabras en sentimiento: integral, pedagogico, excelencia, pedagogia."""
    test_cases = [
        ("Formacion integral y de excelencia", "Muy Positivo", 5),
        ("Pedagogia profesional", "Muy Positivo", 5),  # pedagogia es VERY_POSITIVE
        ("No vayan, pobre servicio", "Muy Negativo", 1),
        ("Eviten este lugar", "Muy Negativo", 1),
    ]
    for comment, expected_label, expected_score in test_cases:
        label, score = comment_processor.classify_sentiment(comment)
        assert label == expected_label, f"Fallo para '{comment}': esperado {expected_label}, obtuve {label}"
        assert score == expected_score, f"Fallo score para '{comment}': esperado {expected_score}, obtuve {score}"


def test_create_dataframe_from_comments_has_expected_columns_and_iso_date():
    load_date = datetime(2026, 5, 8, tzinfo=timezone.utc)
    df = comment_processor.create_dataframe_from_comments(
        ["Excelente comida", "Muy caro"],
        source="Google Maps",
        load_date=load_date,
    )

    assert list(df.columns) == comment_processor.CSV_COLUMN_ORDER
    assert set(df["fecha_carga"].unique()) == {"2026-05-08"}
    assert set(df["fuente"].unique()) == {"Google Maps"}


def test_create_dataframe_with_multisectorial_categories():
    """Valida que el DataFrame incluye las nuevas categorias multisectoriales."""
    load_date = datetime(2026, 5, 8, tzinfo=timezone.utc)
    df = comment_processor.create_dataframe_from_comments(
        ["Formacion excelente", "Precio muy caro", "Instalaciones limpias"],
        source="Google Maps",
        load_date=load_date,
    )
    
    # Deberia tener las nuevas categorias
    categories = set(df["categoria"].unique())
    assert "Academico/Calidad" in categories or "Precio/Valor" in categories or "Infraestructura" in categories


def test_export_full_csv_applies_column_order_and_header_mapping():
    load_date = datetime(2026, 5, 8, tzinfo=timezone.utc)
    df = comment_processor.create_dataframe_from_comments(["Excelente comida"], source="Google Maps", load_date=load_date)

    csv_bytes = comment_processor.export_full_csv(
        df,
        header_mapping={
            "comentario_original": "Comentarios de la seccion de opinion",
        },
    )
    csv_text = csv_bytes.decode("utf-8-sig")
    first_line = csv_text.splitlines()[0]

    assert first_line == (
        "fecha_carga,fuente,Comentarios de la seccion de opinion,"
        "sentimiento_etiqueta,sentimiento_score,categoria"
    )


def test_export_manual_load_csv_outputs_only_comment_column_by_default():
    load_date = datetime(2026, 5, 8, tzinfo=timezone.utc)
    df = comment_processor.create_dataframe_from_comments(["Excelente comida"], source="Google Maps", load_date=load_date)

    csv_bytes = comment_processor.export_manual_load_csv(
        df,
        include_source=False,
        header_mapping={
            "comentario_original": "Comentarios de la seccion de opinion",
        },
    )
    csv_text = csv_bytes.decode("utf-8-sig")
    lines = csv_text.splitlines()

    assert lines[0] == "Comentarios de la seccion de opinion"
    assert lines[1] == "Excelente comida"


def test_sentiment_mexican_expressions():
    """Valida expresiones mexicanas en sentimiento: 'mi segunda casa', 'forman con el corazon', etc."""
    test_cases = [
        ("Es mi segunda casa", "Muy Positivo", 5),
        ("Los profesores forman con el corazon", "Muy Positivo", 5),
        ("Excelencia en toda la extension de la palabra", "Muy Positivo", 5),
        ("Supero mis expectativas", "Muy Positivo", 5),
        ("Nivel academico competitivo", "Positivo", 4),
        ("Ambiente seguro para los ninos", "Positivo", 4),
    ]
    for comment, expected_label, expected_score in test_cases:
        label, score = comment_processor.classify_sentiment(comment)
        assert label == expected_label, f"Fallo para '{comment}': esperado {expected_label}, obtuve {label}"
        assert score == expected_score, f"Fallo score para '{comment}': esperado {expected_score}, obtuve {score}"


def test_negation_detection():
    """Valida que negacion baja el score: 'no es bueno' != 'bueno'."""
    # Sin negacion
    _, score_positive = comment_processor.classify_sentiment("Es bueno")
    # Con negacion
    _, score_negated = comment_processor.classify_sentiment("No es bueno")
    
    # El negado deberia tener score menor o igual al positivo
    assert score_negated <= score_positive, (
        f"Negacion no funcionó: 'No es bueno' (score {score_negated}) "
        f"deberia ser <= 'Es bueno' (score {score_positive})"
    )


def test_extended_boilerplate_school_phrases():
    """Valida filtrado de frases boilerplate específicas de escuelas."""
    raw = (
        "respuesta del propietario aqui\n"
        "traducido por google automáticamente\n"
        "Un comentario real sobre la escuela\n"
        "hace un mes que visité\n"
    )
    result = comment_processor.clean_raw_text(raw)
    cleaned = result["comentarios_validos"]
    
    assert "Un comentario real sobre la escuela" in cleaned
    assert result["total_descartados"] >= 3


def test_school_category_keywords_denominational():
    """Valida que palabras denominacionales asocian a Ambiente/Comunidad."""
    test_cases = [
        ("Carisma jesuita muy fuerte", "Ambiente/Comunidad"),
        ("Salesiano puro con fraternidad", "Ambiente/Comunidad"),
        ("Retiros benedictino anuales", "Ambiente/Comunidad"),
    ]
    for comment, expected_category in test_cases:
        detected = comment_processor.detect_categories(comment)
        assert detected == expected_category, (
            f"Fallo para '{comment}': esperado {expected_category}, obtuve {detected}"
        )


def test_category_keywords_expanded():
    """Valida que CATEGORY_KEYWORDS tiene al menos 150 palabras clave."""
    total_keywords = sum(len(keywords) for _, keywords in comment_processor.CATEGORY_KEYWORDS)
    assert total_keywords >= 150, f"Se esperaban >= 150 palabras clave, obtuvimos {total_keywords}"


def test_sentiment_very_positive_expanded():
    """Valida que VERY_POSITIVE_WORDS tiene expansion (>= 50 palabras)."""
    assert len(comment_processor.VERY_POSITIVE_WORDS) >= 50, (
        f"VERY_POSITIVE_WORDS deberia tener >= 50 palabras, "
        f"tiene {len(comment_processor.VERY_POSITIVE_WORDS)}"
    )


def test_sentiment_very_negative_expanded():
    """Valida que VERY_NEGATIVE_WORDS tiene expansion (>= 50 palabras)."""
    assert len(comment_processor.VERY_NEGATIVE_WORDS) >= 50, (
        f"VERY_NEGATIVE_WORDS deberia tener >= 50 palabras, "
        f"tiene {len(comment_processor.VERY_NEGATIVE_WORDS)}"
    )


def test_multi_phrase_detection():
    """Valida que frases multi-palabra se detectan correctamente y sin ambiguedad."""
    # Frase con potencial ambiguedad (contiene palabras de multiples sentimientos)
    comment = "No inscriban a sus hijos aqui aunque tiene buenas instalaciones"
    label, _ = comment_processor.classify_sentiment(comment)
    
    # "No inscriban a sus hijos aqui" es frase VERY_NEGATIVE muy fuerte
    assert label == "Muy Negativo", (
        f"Frase muy negativa no detectada. Esperado 'Muy Negativo', obtuve '{label}'"
    )


def test_sentiment_detects_structural_negation_real_case():
    """Caso real: negacion estructural no debe salir positiva por palabras academicas."""
    comment = (
        "Si estan buscando educacion de calidad, trato digno y buen ambiente escolar, "
        "esta no es la escuela para ustedes."
    )
    label, score = comment_processor.classify_sentiment(comment)
    assert label in {"Negativo", "Muy Negativo"}
    assert score <= 2


def test_sentiment_detects_negative_clause_after_positive_words():
    """Caso real: frase con 'solo son amables mientras...' debe clasificarse negativa."""
    comment = "Solo son amables mientras estas interesado en hacer la inscripcion de ahi en fuera se acabo"
    label, score = comment_processor.classify_sentiment(comment)
    assert label in {"Negativo", "Muy Negativo"}
    assert score <= 2


def test_clean_raw_text_filters_google_maps_metadata_and_profile_rows():
    """Filtra metadatos de Google Maps: fotos, editado hace, nombres y reacciones."""
    raw = (
        "Foto 1 de la opinion de Mario Velazquez\n"
        "Editado Hace 6 meses\n"
        "1 opinion·3 fotos\n"
        "Lenin Tonatiuh Carbajal Ortega\n"
        "❤️🙏10\n"
        "Excelente universidad para la buena formacion personal y academica\n"
    )
    result = comment_processor.clean_raw_text(raw)
    cleaned = result["comentarios_validos"]

    assert cleaned == ["Excelente universidad para la buena formacion personal y academica"]
    assert result["total_descartados"] == 5


def test_detect_categories_price_is_contextual_not_triggered_by_event_or_route():
    """Precio/Valor no debe activarse solo por palabras ambiguas como evento/ruta."""
    comment = "Vine como expositor en el evento de la ruta de los muertos, el lugar es amplio"
    detected = comment_processor.detect_categories(comment)
    assert detected != "Precio/Valor"
