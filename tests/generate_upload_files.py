"""
Generador de archivos de prueba para Carga Masiva.
Crea archivos en temp_test_files/ para pruebas de UI e integración.

Archivos generados:
- test_valido.csv: CSV válido con 5 registros.
- test_valido.xlsx: Excel válido con 5 registros (requiere openpyxl).
- test_error_columnas.csv: Falta 'seguidores'.
- test_error_vacio.csv: Encabezados sin datos.
"""
from __future__ import annotations
import os
from pathlib import Path
from datetime import date, timedelta
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent
OUT_DIR = BASE_DIR / "temp_test_files"


def ensure_out_dir() -> Path:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    return OUT_DIR


def build_valid_dataframe(rows: int = 5) -> pd.DataFrame:
    today = date.today()
    data = []
    plataformas = ["FB", "Instagram", "TikTok", "YouTube", "Twitter"]
    entidades = [
        "Colegio Marista Centro",
        "Colegio Marista Norte",
        "Colegio Marista Sur",
        "Colegio Marista Oriente",
        "Colegio Marista Poniente",
    ]
    for i in range(rows):
        data.append({
            "entidad": entidades[i % len(entidades)],
            "plataforma": plataformas[i % len(plataformas)],
            "fecha": (today - timedelta(days=i)).strftime("%Y-%m-%d"),
            "seguidores": 1000 + i * 50,
            "alcance": 3000 + i * 200,
            "interacciones": 120 + i * 10,
            "likes_promedio": round(25 + i * 1.5, 2),
            "engagement_rate": round(((120 + i * 10) / (1000 + i * 50)) * 100, 2),
        })
    return pd.DataFrame(data)


def build_missing_columns_dataframe(rows: int = 5) -> pd.DataFrame:
    """Devuelve un DataFrame que NO incluye 'seguidores' para validar error."""
    today = date.today()
    data = []
    plataformas = ["FB", "Instagram", "TikTok", "YouTube", "Twitter"]
    entidades = [
        "Colegio Marista Centro",
        "Colegio Marista Norte",
        "Colegio Marista Sur",
        "Colegio Marista Oriente",
        "Colegio Marista Poniente",
    ]
    for i in range(rows):
        data.append({
            "entidad": entidades[i % len(entidades)],
            "plataforma": plataformas[i % len(plataformas)],
            "fecha": (today - timedelta(days=i)).strftime("%Y-%m-%d"),
            # "seguidores" intencionalmente ausente
            "alcance": 3000 + i * 200,
            "interacciones": 120 + i * 10,
        })
    return pd.DataFrame(data)


def build_empty_dataframe() -> pd.DataFrame:
    """Encabezados correctos pero sin registros."""
    return pd.DataFrame({
        "entidad": pd.Series(dtype="string"),
        "plataforma": pd.Series(dtype="string"),
        "fecha": pd.Series(dtype="string"),
        "seguidores": pd.Series(dtype="int"),
    })


def main() -> None:
    out = ensure_out_dir()

    # 1) CSV válido
    df_valid_csv = build_valid_dataframe(rows=5)
    csv_valid_path = out / "test_valido.csv"
    df_valid_csv.to_csv(csv_valid_path, index=False)

    # 2) Excel válido (requiere openpyxl)
    xlsx_valid_path = out / "test_valido.xlsx"
    try:
        df_valid_xlsx = build_valid_dataframe(rows=5)
        df_valid_xlsx.to_excel(xlsx_valid_path, index=False)
    except Exception as e:
        print(f"[WARN] No se pudo generar test_valido.xlsx: {e}")
        print("       Instala openpyxl en tu entorno si necesitas el Excel.")

    # 3) CSV con error de columnas (falta 'seguidores')
    df_missing = build_missing_columns_dataframe(rows=5)
    csv_missing_path = out / "test_error_columnas.csv"
    df_missing.to_csv(csv_missing_path, index=False)

    # 4) CSV vacío (solo encabezados)
    df_empty = build_empty_dataframe()
    csv_empty_path = out / "test_error_vacio.csv"
    df_empty.to_csv(csv_empty_path, index=False)

    print("Archivos generados en:", out)
    for p in [csv_valid_path, xlsx_valid_path, csv_missing_path, csv_empty_path]:
        print(" -", p)


if __name__ == "__main__":
    main()
