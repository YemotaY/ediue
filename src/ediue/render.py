"""Ausgabe: ausgewertete Dokumente als Text, Markdown oder JSON."""

from __future__ import annotations

import json
import re
from collections.abc import Iterable
from dataclasses import dataclass, field

from .explain import explain
from .interpret import read_documents
from .model import Document, LineItem, Party
from .syntax import Interchange

__all__ = ["FORMATS", "render", "render_markdown", "render_text"]

FORMATS = ("text", "markdown", "json", "segmente")
"""Ausgabeformate von :func:`render`."""

# Eine Ausgabezeile: (Bezeichnung, Wert); die Bezeichnung darf leer sein.
_Line = tuple[str, str]


@dataclass
class _Block:
    """Überschrift mit Zeilen und Unterblöcken; die gemeinsame Vorstufe aller Textformate."""

    title: str
    lines: list[_Line] = field(default_factory=list)
    blocks: list[_Block] = field(default_factory=list)


def render(interchanges: Iterable[Interchange], fmt: str = "text") -> str:
    """Gibt alle Nachrichten der Übertragungen im Format ``fmt`` aus (siehe :data:`FORMATS`)."""
    if fmt == "segmente":
        return "\n\n".join("\n".join(map(str, explain(entry))) for entry in interchanges)
    documents = [document for entry in interchanges for document in read_documents(entry)]
    if fmt == "text":
        return "\n\n\n".join(map(render_text, documents))
    if fmt == "markdown":
        return "\n\n---\n\n".join(map(render_markdown, documents))
    if fmt == "json":
        return json.dumps([doc.to_dict() for doc in documents], ensure_ascii=False, indent=2)
    raise ValueError(f"Unbekanntes Format {fmt!r}; möglich sind: {', '.join(FORMATS)}.")


def render_text(document: Document) -> str:
    """Ein Dokument als gegliederter Klartext."""
    root = _outline(document)
    rule = "=" * max(60, len(root.title))
    out = [rule, root.title, rule, *map(_plain_line, root.lines)]
    for section in root.blocks:
        out += ["", section.title, "-" * len(section.title)]
        out += [f"  {_plain_line(line)}" for line in section.lines]
        for index, block in enumerate(section.blocks):
            if index or section.lines:
                out.append("")
            out += _indented(block, 1)
    return "\n".join(out)


def render_markdown(document: Document) -> str:
    """Ein Dokument als Markdown mit Überschriften und Listen."""
    return "\n".join(_markdown(_outline(document), 1)).rstrip()


def _plain_line(line: _Line) -> str:
    label, value = line
    return f"{label}: {value}" if label else value


def _indented(block: _Block, depth: int) -> list[str]:
    pad = "  " * depth
    out = [pad + block.title]
    out += [f"{pad}  {_plain_line(line)}" for line in block.lines]
    for child in block.blocks:
        out += _indented(child, depth + 1)
    return out


def _escape(text: str) -> str:
    return re.sub(r"[\\`*_<\[\]|]", r"\\\g<0>", text)


def _markdown(block: _Block, level: int) -> list[str]:
    out = [f"{'#' * level} {_escape(block.title)}", ""]
    for label, value in block.lines:
        out.append(f"- **{_escape(label)}:** {_escape(value)}" if label else f"- {_escape(value)}")
    if block.lines:
        out.append("")
    for child in block.blocks:
        out += _markdown(child, level + 1)
    return out


def _pairs(entries: Iterable) -> list[_Line]:
    return [(entry.label, entry.text) for entry in entries]


def _outline(doc: Document) -> _Block:
    message = " ".join(part for part in (doc.message_type, doc.directory) if part)
    if doc.association:
        message += f" ({doc.association})"
    if doc.message_reference:
        message += f", Referenz {doc.message_reference}"
    head = [
        ("Status", doc.function),
        ("Antwort", doc.response),
        *_pairs(doc.dates),
        ("Währung", doc.currency),
        ("Nachricht", message),
        ("Übertragung", doc.envelope.text if doc.envelope else ""),
    ]
    conditions = [
        *doc.payment_terms,
        *doc.delivery_terms,
        *doc.transports,
        *doc.allowances,
        *doc.taxes,
        *doc.packages,
        *doc.locations,
    ]
    sections = [
        _Block("Referenzen", _pairs(doc.references)),
        _Block("Beteiligte", blocks=[_party_block(party) for party in doc.parties]),
        _Block("Konditionen", _pairs(conditions)),
        _Block("Hinweise", [("", text) for text in doc.descriptions] + _pairs(doc.texts)),
        _Block("Positionen", blocks=[_item_block(item) for item in doc.items]),
        _Block("Summen", _pairs([*doc.totals, *doc.controls])),
        _Block("Nicht ausgewertete Segmente", [("", str(segment)) for segment in doc.unhandled]),
    ]
    return _Block(
        doc.title,
        [line for line in head if line[1]],
        [section for section in sections if section.lines or section.blocks],
    )


def _party_block(party: Party) -> _Block:
    lines = [("", line) for line in party.address]
    if party.id:
        lines.append((party.id_kind or "Kennung", party.id))
    lines += _pairs([*party.references, *party.contacts, *party.locations])
    return _Block(party.label, lines)


def _item_block(item: LineItem) -> _Block:
    first, *more = item.descriptions or [""]
    lines = [("Beschreibung", text) for text in more]
    if item.action:
        lines.append(("Status", item.action))
    lines += _pairs(
        [
            *item.product_ids,
            *item.quantities,
            *item.prices,
            *item.percentages,
            *item.allowances,
            *item.taxes,
            *item.amounts,
            *item.dates,
            *item.schedules,
            *item.locations,
            *item.references,
            *item.measurements,
            *item.packages,
            *item.texts,
        ]
    )
    return _Block(
        f"{item.label} – {first}" if first else item.label,
        lines,
        [_party_block(party) for party in item.parties],
    )
