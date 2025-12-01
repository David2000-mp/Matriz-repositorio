"""
Generador de archivos de prueba (Smoke Test) para Carga Masiva.
Crea archivos en test_files/ para validar la integración Frontend-Backend.

Archivos:
- 01_valido.csv: CSV válido con 5 registros (fechas de este mes).
- 02_valido.xlsx: Excel válido con 5 registros (requiere openpyxl).
- 03_error_columnas.csv: Falta 'seguidores'.
- 04_datos_sucios.csv: Nombres de plataforma con mayúsculas mezcladas para probar normalización.
"""
from __future__ import annotations
from pathlib import Path
from datetime import date, timedelta
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent
OUT_DIR = BASE_DIR / "test_files"


def ensure_out_dir() -> Path:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    return OUT_DIR


def build_month_dataframe(rows: int = 5) -> pd.DataFrame:
    today = date.today()
    # Fechas en el mismo mes actual
    start_day = 1
    data = []
    entidades = [
        "Colegio Marista Centro",
        "Colegio Marista Norte",
        "Colegio Marista Sur",
        "Colegio Marista Oriente",
        "Colegio Marista Poniente",
    ]
    plataformas = ["FB", "Instagram", "TikTok", "YouTube", "Twitter"]
    for i in range(rows):
        day = min(start_day + i, 28)  # evitar meses con menos días
        fecha = today.replace(day=day).strftime("%Y-%m-%d")
        seguidores = 1000 + i * 100
        interacciones = 80 + i * 15
        alcance = 2500 + i * 300
        likes_promedio = round(20 + i * 1.2, 2)
        engagement_rate = round((interacciones / seguidores) * 100, 2)
        data.append({
            "entidad": entidades[i % len(entidades)],
            "plataforma": plataformas[i % len(plataformas)],
            "fecha": fecha,
            "seguidores": seguidores,
            "alcance": alcance,
            "interacciones": interacciones,
            "likes_promedio": likes_promedio,
            "engagement_rate": engagement_rate,
        })
    return pd.DataFrame(data)


def build_missing_column_df(rows: int = 5) -> pd.DataFrame:
    df = build_month_dataframe(rows)
    # Remover la columna requerida 'seguidores'
    return df.drop(columns=["seguidores"])


def build_dirty_platforms_df(rows: int = 5) -> pd.DataFrame:
    df = build_month_dataframe(rows)
    # Mezclar mayúsculas/minúsculas y nombres amigables
    sucios = ["FaceBook", "InstaGram", "tiktok", "YouTube ", " TWITTER"]
    df["plataforma"] = sucios[:rows]
    return df


def main() -> None:
    out = ensure_out_dir()

    # 01 CSV válido
    df_valid_csv = build_month_dataframe(5)
    path_01 = out / "01_valido.csv"
    df_valid_csv.to_csv(path_01, index=False)

    # 02 Excel válido
    path_02 = out / "02_valido.xlsx"
    try:
        df_valid_xlsx = build_month_dataframe(5)
        df_valid_xlsx.to_excel(path_02, index=False)
    except Exception as e:
        print(f"[WARN] No se pudo generar 02_valido.xlsx: {e}")
        print("       Instala openpyxl en tu entorno (pip install openpyxl).")

    # 03 CSV con columnas faltantes
    df_missing = build_missing_column_df(5)
    path_03 = out / "03_error_columnas.csv"
    df_missing.to_csv(path_03, index=False)

    # 04 CSV con plataformas 'sucias'
    df_dirty = build_dirty_platforms_df(5)
    path_04 = out / "04_datos_sucios.csv"
    df_dirty.to_csv(path_04, index=False)

    print("Archivos generados en:", out)
    for p in [path_01, path_02, path_03, path_04]:
        print(" -", p)


if __name__ == "__main__":
    main()
