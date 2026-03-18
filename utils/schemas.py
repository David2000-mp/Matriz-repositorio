"""Schemas canonicos para analitica de engagement."""

from dataclasses import dataclass
from typing import Any


@dataclass
class CanonicalPost:
    """Modelo canonico de una publicacion para analitica y reporte."""

    post_id: int
    fecha: str
    plataforma: str
    seguidores_snapshot: int
    likes: int
    comments: int
    shares: int
    views: int
    categoria: str
    link_url: str
    comentario: str

    @property
    def interactions(self) -> int:
        """Interacciones base para formulas por plataforma."""
        return int(self.likes) + int(self.comments) + int(self.shares)


def canonical_post_from_row(row: dict[str, Any], default_platform: str = "facebook") -> CanonicalPost:
    """Convierte una fila flexible en CanonicalPost con defaults seguros."""
    return CanonicalPost(
        post_id=int(row.get("post_id", row.get("num", 0))),
        fecha=str(row.get("fecha", "")),
        plataforma=str(row.get("plataforma", default_platform)).lower(),
        seguidores_snapshot=int(row.get("seguidores_snapshot", row.get("followers", 0))),
        likes=int(row.get("likes", row.get("reactions", 0))),
        comments=int(row.get("comments", 0)),
        shares=int(row.get("shares", 0)),
        views=int(row.get("views", 0)),
        categoria=str(row.get("categoria", row.get("type", "Sin categoria"))),
        link_url=str(row.get("link_url", row.get("url", ""))),
        comentario=str(row.get("comentario", row.get("comment", ""))),
    )
