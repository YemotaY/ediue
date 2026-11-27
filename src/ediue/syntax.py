"""EDIFACT-Syntax (ISO 9735): Zerlegen einer Übertragung in Segmente und Nachrichten.

Dieses Modul kennt nur die Struktur der Daten, nicht ihre fachliche Bedeutung.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

__all__ = [
    "EdifactError",
    "EdifactSyntaxError",
    "Interchange",
    "Message",
    "Segment",
    "Separators",
    "decode",
    "load",
    "parse",
]

_TAG = re.compile(r"[A-Z][A-Z0-9]{2}")
_ENVELOPE_TAGS = {"UNB", "UNG", "UNE", "UNZ"}
_UNB_SYNTAX = re.compile(rb"UNB.(UNO[A-Z])")
_CHARSETS = {
    "UNOD": "iso-8859-2",
    "UNOE": "iso-8859-5",
    "UNOF": "iso-8859-7",
    "UNOG": "iso-8859-3",
    "UNOH": "iso-8859-4",
    "UNOI": "iso-8859-6",
    "UNOJ": "iso-8859-8",
    "UNOK": "iso-8859-9",
    "UNOL": "iso-8859-15",
}


class EdifactError(Exception):
    """Basisklasse aller Fehler dieser Bibliothek."""


class EdifactSyntaxError(EdifactError):
    """Die Eingabe ist keine lesbare EDIFACT-Übertragung."""


@dataclass(frozen=True)
class Separators:
    """Trennzeichen einer Übertragung; die Vorgabe entspricht ``UNA:+.? '``."""

    component: str = ":"
    element: str = "+"
    decimal: str = "."
    release: str = "?"
    terminator: str = "'"

    @classmethod
    def from_una(cls, una: str) -> Separators:
        """Liest die Trennzeichen aus einem neun Zeichen langen UNA-Segment."""
        if len(una) != 9 or not una.startswith("UNA"):
            raise EdifactSyntaxError("Das UNA-Segment ist unvollständig.")
        component, element, decimal, release, _reserved, terminator = una[3:]
        if len({component, element, release, terminator}) != 4:
            raise EdifactSyntaxError("Das UNA-Segment nennt ein Trennzeichen mehrfach.")
        # Ein Leerzeichen bedeutet: Es gibt kein Freigabezeichen.
        return cls(component, element, decimal, release.strip(), terminator)


@dataclass(frozen=True)
class Segment:
    """Ein Segment: Bezeichner plus Datenelemente, jedes als Tupel seiner Komponenten."""

    tag: str
    elements: tuple[tuple[str, ...], ...] = ()

    def get(self, element: int, component: int = 0) -> str:
        """Wert einer Komponente (beide Indizes ab 0); fehlende Werte ergeben ``""``."""
        try:
            return self.elements[element][component]
        except IndexError:
            return ""

    def components(self, element: int) -> tuple[str, ...]:
        """Alle Komponenten eines Datenelements; ``()`` wenn es fehlt."""
        return self.elements[element] if element < len(self.elements) else ()

    def __str__(self) -> str:
        """Das Segment in EDIFACT-Schreibweise mit Standard-Trennzeichen."""
        parts = [self.tag]
        for element in self.elements:
            parts.append(":".join(re.sub(r"[?:+']", r"?\g<0>", value) for value in element))
        return "+".join(parts) + "'"


@dataclass
class Message:
    """Eine Nachricht: alle Segmente von UNH bis einschließlich UNT."""

    segments: list[Segment]
    envelope: Segment | None = None
    """Das UNB-Segment der umgebenden Übertragung, falls vorhanden."""

    @property
    def reference(self) -> str:
        return self.segments[0].get(0)

    @property
    def type(self) -> str:
        """Nachrichtentyp, z. B. ``ORDERS``."""
        return self.segments[0].get(1, 0)

    @property
    def directory(self) -> str:
        """Verzeichnisversion, z. B. ``D.96A``."""
        header = self.segments[0]
        return ".".join(part for part in (header.get(1, 1), header.get(1, 2)) if part)

    @property
    def association(self) -> str:
        """Kennung des Subsets, z. B. ``EAN008`` bei EANCOM."""
        return self.segments[0].get(1, 4)

    @property
    def body(self) -> list[Segment]:
        """Die Segmente ohne UNH und UNT."""
        return [segment for segment in self.segments[1:] if segment.tag != "UNT"]


@dataclass
class Interchange:
    """Eine eingelesene Datei: Segmente, Nachrichten und Auffälligkeiten."""

    separators: Separators
    segments: list[Segment]
    messages: list[Message]
    warnings: list[str] = field(default_factory=list)
    """Verstöße gegen die Syntax, die das Lesen nicht verhindert haben."""

    @property
    def header(self) -> Segment | None:
        """Das erste UNB-Segment, falls vorhanden."""
        return next((segment for segment in self.segments if segment.tag == "UNB"), None)


def parse(text: str) -> Interchange:
    """Zerlegt EDIFACT-Text in Segmente und Nachrichten.

    Zeilenumbrüche werden ignoriert, ein UNA-Segment wird berücksichtigt.
    Strukturfehler (fehlendes UNT, falsche Zähler ...) landen als Text in
    ``Interchange.warnings``; nur unlesbare Eingaben lösen
    :class:`EdifactSyntaxError` aus.
    """
    text = text.lstrip("\ufeff \t\r\n")
    separators = Separators()
    if text.startswith("UNA"):
        separators = Separators.from_una(text[:9])
        text = text[9:]

    raw_segments, unterminated = _split(text, separators)
    segments = []
    for number, raw in enumerate(raw_segments, start=1):
        tag = raw[0][0].strip()
        if not tag and len(raw) == 1 and len(raw[0]) == 1:
            continue
        if not _TAG.fullmatch(tag):
            raise EdifactSyntaxError(
                f"Segment {number}: {tag[:20]!r} ist kein gültiger Segmentbezeichner."
            )
        segments.append(Segment(tag, tuple(tuple(element) for element in raw[1:])))
    if not segments:
        raise EdifactSyntaxError("Die Eingabe enthält keine EDIFACT-Segmente.")

    warnings = []
    if unterminated:
        warnings.append("Das letzte Segment ist nicht abgeschlossen.")
    messages = _messages(segments, warnings)
    return Interchange(separators, segments, messages, warnings)


def decode(data: bytes, encoding: str | None = None) -> str:
    """Wandelt Dateiinhalt in Text.

    Ohne ``encoding`` wird zuerst UTF-8 versucht (viele Dateien sind so
    gespeichert, auch wenn sie UNOC angeben), danach der im UNB genannte
    Zeichensatz, ersatzweise ISO 8859-1.
    """
    if encoding:
        return data.decode(encoding)
    try:
        return data.decode("utf-8-sig")
    except UnicodeDecodeError:
        pass
    match = _UNB_SYNTAX.search(data[:200])
    declared = match.group(1).decode("ascii") if match else ""
    return data.decode(_CHARSETS.get(declared, "iso-8859-1"), errors="replace")


def load(path: str | Path, encoding: str | None = None) -> Interchange:
    """Liest eine EDIFACT-Datei; zur Zeichensatzwahl siehe :func:`decode`."""
    return parse(decode(Path(path).read_bytes(), encoding))


def _split(text: str, separators: Separators) -> tuple[list[list[list[str]]], bool]:
    """Zerlegt Text in rohe Segmente; der zweite Wert meldet ein offenes letztes Segment."""
    segments = []
    elements: list[list[str]] = [[]]
    value: list[str] = []
    escaped = False
    for char in text:
        if escaped:
            value.append(char)
            escaped = False
        elif char == separators.release:
            escaped = True
        elif char in (separators.terminator, separators.element, separators.component):
            elements[-1].append("".join(value))
            value.clear()
            if char == separators.element:
                elements.append([])
            elif char == separators.terminator:
                segments.append(elements)
                elements = [[]]
        elif char not in "\r\n":
            value.append(char)

    rest = "".join(value).strip()
    unterminated = bool(rest) or elements != [[]]
    if unterminated:
        elements[-1].append(rest)
        segments.append(elements)
    return segments, unterminated


def _messages(segments: list[Segment], warnings: list[str]) -> list[Message]:
    """Fasst Segmente zu Nachrichten zusammen und prüft die Zähler der Endesegmente."""
    messages: list[Message] = []
    current: list[Segment] | None = None
    envelope: Segment | None = None
    count = groups = 0

    if not any(segment.tag == "UNB" for segment in segments):
        warnings.append("Die Datei enthält keinen Übertragungskopf (UNB).")

    for segment in segments:
        tag = segment.tag
        if current is not None and (tag == "UNH" or tag in _ENVELOPE_TAGS):
            warnings.append(f"Nachricht {current[0].get(0)} hat kein Endesegment (UNT).")
            messages.append(Message(current, envelope))
            current = None

        if tag == "UNH":
            current = [segment]
            count += 1
        elif current is not None:
            current.append(segment)
            if tag == "UNT":
                _check_unt(current, warnings)
                messages.append(Message(current, envelope))
                current = None
        elif tag == "UNB":
            envelope = segment
            count = groups = 0
        elif tag == "UNG":
            groups += 1
        elif tag == "UNZ":
            _check_unz(segment, envelope, groups or count, warnings)
            envelope = None
        elif tag != "UNE":
            warnings.append(f"Segment {tag} steht außerhalb einer Nachricht.")

    if current is not None:
        warnings.append(f"Nachricht {current[0].get(0)} hat kein Endesegment (UNT).")
        messages.append(Message(current, envelope))
    if not messages:
        warnings.append("Die Datei enthält keine Nachricht (UNH).")
    return messages


def _check_unt(message: list[Segment], warnings: list[str]) -> None:
    header, trailer = message[0], message[-1]
    reference = header.get(0)
    declared = trailer.get(0)
    if declared.isdigit() and int(declared) != len(message):
        warnings.append(
            f"Nachricht {reference}: UNT nennt {declared} Segmente, enthalten sind {len(message)}."
        )
    if trailer.get(1) != reference:
        warnings.append(f"Nachricht {reference}: Die Referenz in UNT lautet {trailer.get(1)!r}.")


def _check_unz(
    trailer: Segment, envelope: Segment | None, expected: int, warnings: list[str]
) -> None:
    declared = trailer.get(0)
    if declared.isdigit() and int(declared) != expected:
        warnings.append(f"UNZ nennt {declared} Nachrichten bzw. Gruppen, enthalten sind {expected}.")
    if envelope is not None and trailer.get(1) != envelope.get(4):
        warnings.append("Die Übertragungsreferenzen in UNB und UNZ stimmen nicht überein.")
