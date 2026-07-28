"""Repositorio aislado para las fuentes granulares del Módulo Satélite.

Este módulo no importa ni consulta el proveedor histórico de ChampiLeaks.
Su única responsabilidad es cargar, tipar y validar tres archivos CSV:

- ``cuentas_satellite.csv``
- ``publicaciones_satellite.csv``
- ``comentarios_satellite.csv``

Ante un error estructural o de tipos, la carga completa falla de forma
cerrada y devuelve tres DataFrames vacíos con el contrato esperado.
Las relaciones huérfanas se registran en logs, pero no se descartan.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Final

import pandas as pd
import streamlit as st

from utils.logger import get_logger


logger = get_logger(__name__)

DEFAULT_SATELLITE_DIR: Final[Path] = (
    Path(__file__).resolve().parent.parent / "data" / "satellite"
)


class SatelliteDataContractError(ValueError):
    """Error fatal de esquema, tipado o integridad dentro de una tabla."""


@dataclass(frozen=True)
class TableSpec:
    """Contrato físico de una tabla satélite."""

    name: str
    filename: str
    columns: tuple[str, ...]
    string_columns: tuple[str, ...] = ()
    datetime_columns: tuple[str, ...] = ()
    integer_columns: tuple[str, ...] = ()
    float_columns: tuple[str, ...] = ()
    non_nullable_columns: tuple[str, ...] = ()
    primary_key: str = ""
    nonnegative_columns: tuple[str, ...] = ()


CUENTAS_SPEC: Final[TableSpec] = TableSpec(
    name="df_cuentas_satellite",
    filename="cuentas_satellite.csv",
    columns=("id_cuenta", "colegio_id", "colegio_nombre", "plataforma"),
    string_columns=("id_cuenta", "colegio_id", "colegio_nombre", "plataforma"),
    non_nullable_columns=("id_cuenta", "colegio_id", "colegio_nombre", "plataforma"),
    primary_key="id_cuenta",
)

PUBLICACIONES_SPEC: Final[TableSpec] = TableSpec(
    name="df_publicaciones",
    filename="publicaciones_satellite.csv",
    columns=(
        "id_publicacion",
        "id_cuenta",
        "plataforma",
        "mes_clave",
        "fecha_publicacion",
        "tipo_contenido",
        "url_publicacion",
        "titulo_o_extracto",
        "visualizaciones",
        "alcance",
        "interacciones",
        "fecha_carga",
        "batch_id",
    ),
    string_columns=(
        "id_publicacion",
        "id_cuenta",
        "plataforma",
        "mes_clave",
        "tipo_contenido",
        "url_publicacion",
        "titulo_o_extracto",
        "batch_id",
    ),
    datetime_columns=("fecha_publicacion", "fecha_carga"),
    integer_columns=("visualizaciones", "alcance", "interacciones"),
    non_nullable_columns=(
        "id_publicacion",
        "id_cuenta",
        "plataforma",
        "mes_clave",
        "fecha_publicacion",
        "tipo_contenido",
        "fecha_carga",
        "batch_id",
    ),
    primary_key="id_publicacion",
    nonnegative_columns=("visualizaciones", "alcance", "interacciones"),
)

COMENTARIOS_SPEC: Final[TableSpec] = TableSpec(
    name="df_comentarios",
    filename="comentarios_satellite.csv",
    columns=(
        "id_comentario",
        "id_publicacion",
        "texto",
        "sentimiento",
        "sentimiento_score",
        "sentimiento_confianza",
        "categoria",
        "tema_alerta",
        "tema_alerta_confianza",
        "metodo_clasificacion",
        "version_clasificador",
        "fecha_comentario",
        "fecha_carga",
        "batch_id",
    ),
    string_columns=(
        "id_comentario",
        "id_publicacion",
        "texto",
        "sentimiento",
        "categoria",
        "tema_alerta",
        "metodo_clasificacion",
        "version_clasificador",
        "batch_id",
    ),
    datetime_columns=("fecha_comentario", "fecha_carga"),
    integer_columns=("sentimiento_score",),
    float_columns=("sentimiento_confianza", "tema_alerta_confianza"),
    non_nullable_columns=(
        "id_comentario",
        "id_publicacion",
        "texto",
        "sentimiento",
        "sentimiento_score",
        "sentimiento_confianza",
        "categoria",
        "metodo_clasificacion",
        "version_clasificador",
        "fecha_comentario",
        "fecha_carga",
        "batch_id",
    ),
    primary_key="id_comentario",
)

SATELLITE_SPECS: Final[tuple[TableSpec, ...]] = (
    CUENTAS_SPEC,
    PUBLICACIONES_SPEC,
    COMENTARIOS_SPEC,
)


@dataclass(frozen=True)
class SatelliteData:
    """Snapshot coherente de las tres tablas satélite."""

    cuentas: pd.DataFrame
    publicaciones: pd.DataFrame
    comentarios: pd.DataFrame

    def copy(self) -> "SatelliteData":
        """Entrega copias profundas para impedir mutaciones del snapshot."""
        return SatelliteData(
            cuentas=self.cuentas.copy(deep=True),
            publicaciones=self.publicaciones.copy(deep=True),
            comentarios=self.comentarios.copy(deep=True),
        )

    def as_dict(self) -> dict[str, pd.DataFrame]:
        """Expone copias usando los nombres físicos definidos por el contrato."""
        return {
            "df_cuentas_satellite": self.cuentas.copy(deep=True),
            "df_publicaciones": self.publicaciones.copy(deep=True),
            "df_comentarios": self.comentarios.copy(deep=True),
        }


def _empty_frame(spec: TableSpec) -> pd.DataFrame:
    """Construye un DataFrame vacío conservando columnas y tipos anulables."""
    typed_columns: dict[str, pd.Series] = {}

    for column in spec.columns:
        if column in spec.datetime_columns:
            dtype = "datetime64[ns]"
        elif column in spec.integer_columns:
            dtype = "Int64"
        elif column in spec.float_columns:
            dtype = "Float64"
        else:
            dtype = "string"
        typed_columns[column] = pd.Series(dtype=dtype)

    return pd.DataFrame(typed_columns, columns=list(spec.columns))


def empty_satellite_data() -> SatelliteData:
    """Retorna el contrato vacío usado para fallos cerrados."""
    return SatelliteData(
        cuentas=_empty_frame(CUENTAS_SPEC),
        publicaciones=_empty_frame(PUBLICACIONES_SPEC),
        comentarios=_empty_frame(COMENTARIOS_SPEC),
    )


def _nonempty_mask(series: pd.Series) -> pd.Series:
    """Distingue valores presentes de nulos y cadenas vacías."""
    normalized = series.astype("string").str.strip()
    return normalized.notna() & normalized.ne("")


def _parse_datetime_strict(
    frame: pd.DataFrame,
    column: str,
    *,
    table_name: str,
) -> pd.Series:
    raw = frame[column].astype("string").str.strip()
    present = _nonempty_mask(raw)

    try:
        parsed = pd.to_datetime(raw.where(present, pd.NA), errors="coerce", format="mixed")
    except (TypeError, ValueError):
        # Compatibilidad con versiones de Pandas sin ``format="mixed"``.
        parsed = pd.to_datetime(raw.where(present, pd.NA), errors="coerce")

    invalid = present & parsed.isna()
    if invalid.any():
        rows = frame.index[invalid].tolist()[:10]
        raise SatelliteDataContractError(
            f"{table_name}.{column}: {int(invalid.sum())} fechas inválidas; "
            f"índices de ejemplo={rows}"
        )
    return parsed.astype("datetime64[ns]")


def _parse_numeric_strict(
    frame: pd.DataFrame,
    column: str,
    *,
    table_name: str,
    dtype: str,
) -> pd.Series:
    raw = frame[column].astype("string").str.strip()
    present = _nonempty_mask(raw)
    normalized = raw.str.replace("\u00a0", "", regex=False).str.replace(" ", "", regex=False)
    normalized = normalized.str.replace(",", ".", regex=False)
    parsed = pd.to_numeric(normalized.where(present, pd.NA), errors="coerce")

    invalid = present & parsed.isna()
    if invalid.any():
        rows = frame.index[invalid].tolist()[:10]
        raise SatelliteDataContractError(
            f"{table_name}.{column}: {int(invalid.sum())} valores numéricos inválidos; "
            f"índices de ejemplo={rows}"
        )

    if dtype == "Int64":
        non_integer = parsed.notna() & parsed.mod(1).ne(0)
        if non_integer.any():
            rows = frame.index[non_integer].tolist()[:10]
            raise SatelliteDataContractError(
                f"{table_name}.{column}: {int(non_integer.sum())} valores no enteros; "
                f"índices de ejemplo={rows}"
            )

    return parsed.astype(dtype)


def _validate_non_nullable(frame: pd.DataFrame, spec: TableSpec) -> None:
    for column in spec.non_nullable_columns:
        series = frame[column]
        if column in spec.string_columns:
            missing = ~_nonempty_mask(series)
        else:
            missing = series.isna()

        if missing.any():
            rows = frame.index[missing].tolist()[:10]
            raise SatelliteDataContractError(
                f"{spec.name}.{column}: {int(missing.sum())} valores obligatorios vacíos; "
                f"índices de ejemplo={rows}"
            )


def _validate_primary_key(frame: pd.DataFrame, spec: TableSpec) -> None:
    if not spec.primary_key or frame.empty:
        return

    duplicate_mask = frame[spec.primary_key].duplicated(keep=False)
    if duplicate_mask.any():
        examples = (
            frame.loc[duplicate_mask, spec.primary_key]
            .astype("string")
            .dropna()
            .unique()
            .tolist()[:10]
        )
        raise SatelliteDataContractError(
            f"{spec.name}.{spec.primary_key}: {int(duplicate_mask.sum())} filas con "
            f"llave duplicada; IDs de ejemplo={examples}"
        )


def _validate_nonnegative(frame: pd.DataFrame, spec: TableSpec) -> None:
    for column in spec.nonnegative_columns:
        negative = frame[column].notna() & frame[column].lt(0)
        if negative.any():
            rows = frame.index[negative].tolist()[:10]
            raise SatelliteDataContractError(
                f"{spec.name}.{column}: {int(negative.sum())} valores negativos; "
                f"índices de ejemplo={rows}"
            )


def _validate_comment_scores(frame: pd.DataFrame) -> None:
    if frame.empty:
        return

    score = frame["sentimiento_score"]
    invalid_score = score.notna() & ~score.between(1, 5, inclusive="both")
    if invalid_score.any():
        examples = frame.loc[invalid_score, "id_comentario"].astype("string").tolist()[:10]
        raise SatelliteDataContractError(
            "df_comentarios.sentimiento_score debe estar entre 1 y 5; "
            f"comentarios de ejemplo={examples}"
        )

    for column in ("sentimiento_confianza", "tema_alerta_confianza"):
        confidence = frame[column]
        invalid_confidence = confidence.notna() & ~confidence.between(
            0.0, 1.0, inclusive="both"
        )
        if invalid_confidence.any():
            examples = (
                frame.loc[invalid_confidence, "id_comentario"]
                .astype("string")
                .tolist()[:10]
            )
            raise SatelliteDataContractError(
                f"df_comentarios.{column} debe estar entre 0 y 1; "
                f"comentarios de ejemplo={examples}"
            )


def _validate_publication_month(frame: pd.DataFrame) -> None:
    if frame.empty:
        return

    valid_format = frame["mes_clave"].str.fullmatch(r"\d{4}-(0[1-9]|1[0-2])", na=False)
    if (~valid_format).any():
        examples = (
            frame.loc[~valid_format, ["id_publicacion", "mes_clave"]]
            .astype("string")
            .to_dict("records")[:10]
        )
        raise SatelliteDataContractError(
            "df_publicaciones.mes_clave contiene valores fuera del formato YYYY-MM; "
            f"ejemplos={examples}"
        )

    derived_month = frame["fecha_publicacion"].dt.strftime("%Y-%m").astype("string")
    mismatch = frame["mes_clave"].ne(derived_month)
    if mismatch.any():
        examples = frame.loc[
            mismatch,
            ["id_publicacion", "mes_clave", "fecha_publicacion"],
        ].to_dict("records")[:10]
        raise SatelliteDataContractError(
            "df_publicaciones: mes_clave no coincide con fecha_publicacion en "
            f"{int(mismatch.sum())} filas; ejemplos={examples}"
        )


class SatelliteDataRepository:
    """Carga el snapshot granular sin acceder al núcleo mensual."""

    def __init__(
        self,
        base_dir: str | Path | None = None,
        *,
        cuentas_filename: str = CUENTAS_SPEC.filename,
        publicaciones_filename: str = PUBLICACIONES_SPEC.filename,
        comentarios_filename: str = COMENTARIOS_SPEC.filename,
    ) -> None:
        self.base_dir = Path(base_dir) if base_dir is not None else DEFAULT_SATELLITE_DIR
        self._specs = (
            TableSpec(**{**CUENTAS_SPEC.__dict__, "filename": cuentas_filename}),
            TableSpec(**{**PUBLICACIONES_SPEC.__dict__, "filename": publicaciones_filename}),
            TableSpec(**{**COMENTARIOS_SPEC.__dict__, "filename": comentarios_filename}),
        )

    def _load_table(self, spec: TableSpec) -> pd.DataFrame:
        path = self.base_dir / spec.filename
        if not path.is_file():
            raise SatelliteDataContractError(
                f"{spec.name}: archivo no encontrado: {path}"
            )

        try:
            source = pd.read_csv(
                path,
                dtype="string",
                encoding="utf-8-sig",
                keep_default_na=False,
            )
        except Exception as exc:
            raise SatelliteDataContractError(
                f"{spec.name}: no se pudo leer {path}: {exc}"
            ) from exc

        source.columns = source.columns.astype(str).str.strip()
        missing_columns = [column for column in spec.columns if column not in source.columns]
        if missing_columns:
            raise SatelliteDataContractError(
                f"{spec.name}: faltan columnas requeridas={missing_columns}; "
                f"disponibles={source.columns.tolist()}"
            )

        extra_columns = [column for column in source.columns if column not in spec.columns]
        if extra_columns:
            logger.warning(
                "%s: se ignorarán columnas fuera del contrato: %s",
                spec.name,
                extra_columns,
            )

        frame = source.loc[:, list(spec.columns)].copy()

        for column in spec.string_columns:
            frame[column] = frame[column].astype("string").str.strip()
            frame.loc[frame[column].eq(""), column] = pd.NA

        for column in spec.datetime_columns:
            frame[column] = _parse_datetime_strict(
                frame,
                column,
                table_name=spec.name,
            )

        for column in spec.integer_columns:
            frame[column] = _parse_numeric_strict(
                frame,
                column,
                table_name=spec.name,
                dtype="Int64",
            )

        for column in spec.float_columns:
            frame[column] = _parse_numeric_strict(
                frame,
                column,
                table_name=spec.name,
                dtype="Float64",
            )

        _validate_non_nullable(frame, spec)
        _validate_primary_key(frame, spec)
        _validate_nonnegative(frame, spec)

        logger.info("%s: %s filas válidas cargadas desde %s", spec.name, len(frame), path)
        return frame.reset_index(drop=True)

    @staticmethod
    def _log_referential_warnings(data: SatelliteData) -> None:
        publication_ids = set(
            data.publicaciones["id_publicacion"].dropna().astype(str)
        )
        comment_ids = data.comentarios["id_publicacion"].dropna().astype(str)
        orphan_comments = data.comentarios.loc[
            ~comment_ids.isin(publication_ids),
            "id_comentario",
        ]
        if not orphan_comments.empty:
            logger.warning(
                "df_comentarios: %s comentarios huérfanos; se conservan sin "
                "descartarlos. id_comentario de ejemplo=%s",
                len(orphan_comments),
                orphan_comments.astype(str).tolist()[:10],
            )

        account_ids = set(data.cuentas["id_cuenta"].dropna().astype(str))
        publication_account_ids = data.publicaciones["id_cuenta"].dropna().astype(str)
        orphan_publications = data.publicaciones.loc[
            ~publication_account_ids.isin(account_ids),
            "id_publicacion",
        ]
        if not orphan_publications.empty:
            logger.warning(
                "df_publicaciones: %s publicaciones apuntan a id_cuenta ausentes "
                "de la dimensión; se conservan. id_publicacion de ejemplo=%s",
                len(orphan_publications),
                orphan_publications.astype(str).tolist()[:10],
            )

        if data.cuentas.empty or data.publicaciones.empty:
            return

        platform_lookup = data.cuentas.set_index("id_cuenta")["plataforma"]
        expected_platform = data.publicaciones["id_cuenta"].map(platform_lookup)
        platform_mismatch = expected_platform.notna() & data.publicaciones[
            "plataforma"
        ].ne(expected_platform)
        if platform_mismatch.any():
            examples = data.publicaciones.loc[
                platform_mismatch,
                ["id_publicacion", "id_cuenta", "plataforma"],
            ].to_dict("records")[:10]
            logger.warning(
                "df_publicaciones: %s plataformas no coinciden con la dimensión "
                "de cuentas; las filas se conservan. ejemplos=%s",
                int(platform_mismatch.sum()),
                examples,
            )

    def load(self) -> SatelliteData:
        """Carga las tres tablas como una unidad coherente y falla de forma cerrada."""
        try:
            cuentas = self._load_table(self._specs[0])
            publicaciones = self._load_table(self._specs[1])
            comentarios = self._load_table(self._specs[2])

            _validate_publication_month(publicaciones)
            _validate_comment_scores(comentarios)

            data = SatelliteData(
                cuentas=cuentas,
                publicaciones=publicaciones,
                comentarios=comentarios,
            )
            self._log_referential_warnings(data)

            logger.info(
                "Snapshot satélite cargado: cuentas=%s, publicaciones=%s, comentarios=%s",
                len(cuentas),
                len(publicaciones),
                len(comentarios),
            )
            return data.copy()
        except SatelliteDataContractError as exc:
            logger.error("Carga satélite rechazada por contrato: %s", exc)
            return empty_satellite_data()
        except Exception:
            logger.exception("Error inesperado durante la carga del Módulo Satélite")
            return empty_satellite_data()


@st.cache_data(ttl=300, show_spinner=False)
def load_satellite_data(
    base_dir: str | None = None,
    *,
    cuentas_filename: str = CUENTAS_SPEC.filename,
    publicaciones_filename: str = PUBLICACIONES_SPEC.filename,
    comentarios_filename: str = COMENTARIOS_SPEC.filename,
) -> SatelliteData:
    """Carga cacheada externa; Streamlit entrega una copia por consumidor."""
    repository = SatelliteDataRepository(
        base_dir=base_dir,
        cuentas_filename=cuentas_filename,
        publicaciones_filename=publicaciones_filename,
        comentarios_filename=comentarios_filename,
    )
    return repository.load().copy()
