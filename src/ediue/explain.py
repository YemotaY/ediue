"""Segmentweise Erläuterung: jede Zeile einer EDIFACT-Datei in einem Satz.

Anders als :mod:`ediue.interpret` setzt diese Sicht keinen bestimmten
Nachrichtenaufbau voraus und eignet sich daher für jede EDIFACT-Datei.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from . import codes, interpret
from .syntax import Interchange, Message, Segment

__all__ = ["Explanation", "explain"]


@dataclass
class Explanation:
    """Ein Segment mit seinem Namen und seiner Bedeutung im Klartext."""

    segment: Segment
    name: str
    text: str
    """Leer, wenn das Segment nicht gedeutet werden kann."""

    def __str__(self) -> str:
        meaning = self.text or f"nicht ausgewertet: {self.segment}"
        return f"{self.segment.tag}  {self.name} – {meaning}"


def explain(interchange: Interchange) -> list[Explanation]:
    """Erläutert alle Segmente einer Übertragung in ihrer Reihenfolge."""
    explanations = []
    for segment in interchange.segments:
        reader = _READERS.get(segment.tag)
        name = codes.SEGMENTS.get(segment.tag, "Unbekanntes Segment")
        explanations.append(Explanation(segment, name, str(reader(segment)) if reader else ""))
    return explanations


def _listed(reader: Callable[[Segment], list]) -> Callable[[Segment], str]:
    return lambda seg: ", ".join(str(entry) for entry in reader(seg))


def _unh(seg: Segment) -> str:
    message = Message([seg])
    kind = codes.MESSAGES.get(message.type, "Nachricht")
    version = " ".join(part for part in (message.type, message.directory) if part)
    return f"{kind} ({version}), Referenz {message.reference}"


def _bgm(seg: Segment) -> str:
    document = interpret.build_document(Message([Segment("UNH"), seg]))
    return ", ".join(part for part in (document.title, document.function, document.response) if part)


def _cux(seg: Segment) -> str:
    rate = f", Kurs {seg.get(2)}" if seg.get(2) else ""
    return " → ".join(element[1] for element in seg.elements[:2] if len(element) > 1) + rate


def _uns(seg: Segment) -> str:
    return "Ende der Positionen, es folgen die Summen" if seg.get(0) == "S" else "Beginn der Positionen"


_READERS: dict[str, Callable[[Segment], object]] = {
    "ALC": interpret.read_allowance,
    "BGM": _bgm,
    "CNT": interpret.read_control,
    "COM": _listed(interpret.read_channels),
    "CTA": interpret.read_contact,
    "CUX": _cux,
    "DTM": interpret.read_date,
    "FTX": interpret.read_text,
    "IMD": interpret.read_description,
    "LIN": interpret.read_line,
    "LOC": interpret.read_location,
    "MEA": interpret.read_measurement,
    "MOA": interpret.read_amount,
    "NAD": interpret.read_party,
    "PAC": interpret.read_package,
    "PAT": interpret.read_payment_terms,
    "PCD": interpret.read_percentage,
    "PIA": _listed(interpret.read_product_ids),
    "PRI": interpret.read_price,
    "QTY": interpret.read_quantity,
    "RFF": interpret.read_reference,
    "SCC": interpret.read_schedule,
    "TAX": interpret.read_tax,
    "TDT": interpret.read_transport,
    "TOD": interpret.read_delivery_terms,
    "UNB": lambda seg: interpret.read_envelope(seg).text,
    "UNH": _unh,
    "UNS": _uns,
    "UNT": lambda seg: f"Anzahl Segmente: {seg.get(0)}, Referenz {seg.get(1)}",
    "UNZ": lambda seg: f"Anzahl Nachrichten bzw. Gruppen: {seg.get(0)}, Referenz {seg.get(1)}",
}
