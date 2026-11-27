"""ediue – übersetzt EDIFACT-Nachrichten in lesbare Bestellungen.

Der kürzeste Weg::

    import ediue

    print(ediue.convert_file("bestellung.edi"))

Für den Zugriff auf einzelne Angaben::

    interchange = ediue.load("bestellung.edi")
    for document in ediue.read_documents(interchange):
        print(document.title, document.party("BY").names)
"""

from __future__ import annotations

from pathlib import Path

from . import model
from .explain import Explanation, explain
from .interpret import build_document, read_documents
from .model import Document
from .render import FORMATS, render, render_markdown, render_text
from .syntax import (
    EdifactError,
    EdifactSyntaxError,
    Interchange,
    Message,
    Segment,
    Separators,
    decode,
    load,
    parse,
)

__version__ = "0.1.0"

__all__ = [
    "FORMATS",
    "Document",
    "EdifactError",
    "EdifactSyntaxError",
    "Explanation",
    "Interchange",
    "Message",
    "Segment",
    "Separators",
    "build_document",
    "convert",
    "convert_file",
    "decode",
    "explain",
    "load",
    "model",
    "parse",
    "read_documents",
    "render",
    "render_markdown",
    "render_text",
]


def convert(data: str | bytes, fmt: str = "text", encoding: str | None = None) -> str:
    """Übersetzt EDIFACT-Daten in das Format ``fmt`` (siehe :data:`FORMATS`).

    ``encoding`` gilt nur für ``bytes``; zur automatischen Wahl siehe :func:`decode`.
    """
    text = decode(data, encoding) if isinstance(data, bytes) else data
    return render([parse(text)], fmt)


def convert_file(path: str | Path, fmt: str = "text", encoding: str | None = None) -> str:
    """Wie :func:`convert`, liest aber aus einer Datei."""
    return render([load(path, encoding)], fmt)
