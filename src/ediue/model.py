"""Datenmodell: der fachliche Inhalt einer Nachricht als einfache Datenklassen.

Fast alle Klassen tragen eine Bezeichnung (``label``) und einen lesbaren Wert
(``text``); ``str(objekt)`` verbindet beides zu einer Zeile wie
``Belegdatum: 15.03.2024``. Die Rohwerte und Codes bleiben daneben erhalten.
"""

from __future__ import annotations

import dataclasses
from dataclasses import dataclass, field
from datetime import date, datetime
from decimal import Decimal
from typing import Any

from .formatting import format_decimal
from .syntax import Segment


def _number(value: Decimal | None, raw: str, min_decimals: int = 0) -> str:
    return raw if value is None else format_decimal(value, min_decimals)


def _joined(*parts: object) -> str:
    return ", ".join(str(part) for part in parts if part)


class _Labelled:
    """Gemeinsame Textform aller Klassen mit ``label`` und ``text``."""

    def __str__(self) -> str:
        return f"{self.label}: {self.text}" if self.text else self.label


@dataclass
class DateInfo(_Labelled):
    """Zeitangabe (DTM)."""

    qualifier: str
    label: str
    raw: str
    format: str
    text: str
    value: date | datetime | None = None
    """Zeitpunkt bzw. Beginn eines Zeitraums, falls der Wert lesbar war."""


@dataclass
class Reference(_Labelled):
    """Referenz auf einen anderen Vorgang (RFF) mit zugehörigen Zeitangaben."""

    qualifier: str
    label: str
    number: str
    line: str = ""
    dates: list[DateInfo] = field(default_factory=list)

    @property
    def text(self) -> str:
        return _joined(self.number, f"Position {self.line}" if self.line else "", *self.dates)


@dataclass
class Quantity(_Labelled):
    """Menge (QTY)."""

    qualifier: str
    label: str
    raw: str
    value: Decimal | None = None
    unit: str = ""
    unit_label: str = ""

    @property
    def text(self) -> str:
        return f"{_number(self.value, self.raw)} {self.unit_label or self.unit}".rstrip()


@dataclass
class Amount(_Labelled):
    """Geldbetrag (MOA). Fehlt die Währung, gilt die des Dokuments."""

    qualifier: str
    label: str
    raw: str
    value: Decimal | None = None
    currency: str = ""

    @property
    def text(self) -> str:
        return f"{_number(self.value, self.raw, 2)} {self.currency}".rstrip()


@dataclass
class Percentage(_Labelled):
    """Prozentangabe (PCD)."""

    qualifier: str
    label: str
    raw: str
    value: Decimal | None = None

    @property
    def text(self) -> str:
        return f"{_number(self.value, self.raw)} %"


@dataclass
class Price(_Labelled):
    """Preis (PRI). Fehlt die Währung, gilt die des Dokuments."""

    qualifier: str
    label: str
    raw: str
    value: Decimal | None = None
    kind: str = ""
    """Preisherkunft im Klartext, z. B. ``Vertragspreis``."""
    basis: Decimal | None = None
    """Menge, auf die sich der Preis bezieht (Preiseinheit)."""
    unit: str = ""
    unit_label: str = ""
    currency: str = ""
    dates: list[DateInfo] = field(default_factory=list)

    @property
    def text(self) -> str:
        text = f"{_number(self.value, self.raw, 2)} {self.currency}".rstrip()
        unit = self.unit_label or self.unit
        if self.basis is not None and self.basis != 1:
            text += f" je {format_decimal(self.basis)} {unit}".rstrip()
        elif unit:
            text += f" je {unit}"
        if self.kind:
            text += f" ({self.kind})"
        return _joined(text, *self.dates)


@dataclass
class FreeText(_Labelled):
    """Freitext (FTX)."""

    qualifier: str
    label: str
    text: str


@dataclass
class ProductId(_Labelled):
    """Artikelnummer (LIN, PIA)."""

    number: str
    kind: str
    label: str

    @property
    def text(self) -> str:
        return self.number


@dataclass
class Measurement(_Labelled):
    """Maß oder Gewicht (MEA)."""

    dimension: str
    label: str
    raw: str
    value: Decimal | None = None
    unit: str = ""
    unit_label: str = ""

    @property
    def text(self) -> str:
        return f"{_number(self.value, self.raw)} {self.unit_label or self.unit}".rstrip()


@dataclass
class Location(_Labelled):
    """Ort (LOC), auf Positionsebene ggf. mit Mengen und Terminen für diesen Ort."""

    qualifier: str
    label: str
    id: str = ""
    name: str = ""
    quantities: list[Quantity] = field(default_factory=list)
    dates: list[DateInfo] = field(default_factory=list)

    @property
    def text(self) -> str:
        place = f"{self.name} ({self.id})" if self.name and self.id else self.name or self.id
        return _joined(place, *self.quantities, *self.dates)


@dataclass
class Channel(_Labelled):
    """Telefonnummer, E-Mail-Adresse o. Ä. (COM)."""

    kind: str
    label: str
    text: str


@dataclass
class Contact(_Labelled):
    """Ansprechpartner (CTA) mit Erreichbarkeiten (COM)."""

    function: str
    label: str
    name: str = ""
    department: str = ""
    channels: list[Channel] = field(default_factory=list)

    @property
    def text(self) -> str:
        who = self.name or self.department
        how = _joined(*self.channels)
        return f"{who} ({how})" if who and how else who or how


@dataclass
class Party(_Labelled):
    """Beteiligter (NAD) mit Referenzen, Ansprechpartnern und Orten."""

    qualifier: str
    label: str
    id: str = ""
    id_kind: str = ""
    """Art der Kennung im Klartext, z. B. ``GLN``."""
    names: list[str] = field(default_factory=list)
    address_lines: list[str] = field(default_factory=list)
    """Unstrukturierte Anschrift (C058), falls der Absender sie so sendet."""
    street: list[str] = field(default_factory=list)
    postcode: str = ""
    city: str = ""
    region: str = ""
    country: str = ""
    country_name: str = ""
    references: list[Reference] = field(default_factory=list)
    contacts: list[Contact] = field(default_factory=list)
    locations: list[Location] = field(default_factory=list)

    @property
    def address(self) -> list[str]:
        """Name und Anschrift, zeilenweise wie auf einem Briefumschlag."""
        place = f"{self.postcode} {self.city}".strip()
        last = _joined(place, self.region, self.country_name or self.country)
        return [*self.names, *self.address_lines, *self.street, *([last] if last else [])]

    @property
    def text(self) -> str:
        identity = f"{self.id_kind or 'Kennung'}: {self.id}" if self.id else ""
        return _joined(*self.address, identity)


@dataclass
class Tax(_Labelled):
    """Steuer, Zoll oder Gebühr (TAX)."""

    kind: str
    label: str
    raw: str = ""
    rate: Decimal | None = None
    category: str = ""
    category_label: str = ""
    amounts: list[Amount] = field(default_factory=list)

    @property
    def text(self) -> str:
        rate = f"{_number(self.rate, self.raw)} %" if self.raw else ""
        category = self.category_label or (f"Kategorie {self.category}" if self.category else "")
        return _joined(rate, category, *self.amounts)


@dataclass
class AllowanceCharge(_Labelled):
    """Zu- oder Abschlag (ALC)."""

    kind: str
    label: str
    service: str = ""
    description: str = ""
    percentages: list[Percentage] = field(default_factory=list)
    amounts: list[Amount] = field(default_factory=list)
    dates: list[DateInfo] = field(default_factory=list)

    @property
    def text(self) -> str:
        return _joined(self.description, *self.percentages, *self.amounts, *self.dates)


@dataclass
class PaymentTerms(_Labelled):
    """Zahlungsbedingung (PAT)."""

    qualifier: str
    label: str
    description: str = ""
    """Frist im Klartext, z. B. ``30 Tage nach Rechnungsdatum``."""
    percentages: list[Percentage] = field(default_factory=list)
    amounts: list[Amount] = field(default_factory=list)
    dates: list[DateInfo] = field(default_factory=list)

    @property
    def text(self) -> str:
        return _joined(self.description, *self.percentages, *self.amounts, *self.dates)


@dataclass
class DeliveryTerms(_Labelled):
    """Lieferbedingung (TOD)."""

    function: str
    label: str
    code: str = ""
    description: str = ""

    @property
    def text(self) -> str:
        if self.code and self.description:
            return f"{self.code} ({self.description})"
        return self.code or self.description


@dataclass
class Transport(_Labelled):
    """Transportangaben (TDT)."""

    stage: str
    label: str
    mode: str = ""
    mode_label: str = ""
    means: str = ""
    carrier: str = ""

    @property
    def text(self) -> str:
        mode = self.mode_label or (f"Verkehrsart {self.mode}" if self.mode else "")
        return _joined(mode, self.means, f"Frachtführer: {self.carrier}" if self.carrier else "")


@dataclass
class Package(_Labelled):
    """Packstücke (PAC)."""

    count: str
    kind: str = ""
    description: str = ""
    label: str = "Packstücke"

    @property
    def text(self) -> str:
        return " × ".join(part for part in (self.count, self.description) if part)


@dataclass
class Schedule(_Labelled):
    """Liefereinteilung einer Position (SCC) mit Mengen und Terminen."""

    status: str
    label: str
    quantities: list[Quantity] = field(default_factory=list)
    dates: list[DateInfo] = field(default_factory=list)

    @property
    def text(self) -> str:
        return _joined(*self.quantities, *self.dates)


@dataclass
class Control(_Labelled):
    """Kontrollwert (CNT)."""

    qualifier: str
    label: str
    raw: str
    value: Decimal | None = None

    @property
    def text(self) -> str:
        return _number(self.value, self.raw)


@dataclass
class LineItem(_Labelled):
    """Eine Position (LIN) mit allem, was ihr untergeordnet ist."""

    number: str
    action: str = ""
    """Bearbeitungsstand im Klartext, z. B. ``Geändert`` (vor allem bei ORDRSP)."""
    product_ids: list[ProductId] = field(default_factory=list)
    descriptions: list[str] = field(default_factory=list)
    quantities: list[Quantity] = field(default_factory=list)
    prices: list[Price] = field(default_factory=list)
    percentages: list[Percentage] = field(default_factory=list)
    amounts: list[Amount] = field(default_factory=list)
    dates: list[DateInfo] = field(default_factory=list)
    references: list[Reference] = field(default_factory=list)
    texts: list[FreeText] = field(default_factory=list)
    measurements: list[Measurement] = field(default_factory=list)
    taxes: list[Tax] = field(default_factory=list)
    allowances: list[AllowanceCharge] = field(default_factory=list)
    schedules: list[Schedule] = field(default_factory=list)
    locations: list[Location] = field(default_factory=list)
    packages: list[Package] = field(default_factory=list)
    parties: list[Party] = field(default_factory=list)

    @property
    def label(self) -> str:
        return f"Position {self.number}".rstrip()

    @property
    def text(self) -> str:
        return _joined(*self.product_ids, self.action)


@dataclass
class Envelope:
    """Angaben aus dem Übertragungskopf (UNB)."""

    sender: str
    recipient: str
    sender_kind: str = ""
    recipient_kind: str = ""
    prepared: str = ""
    """Erstellungszeitpunkt im Klartext."""
    reference: str = ""
    test: bool = False

    @property
    def text(self) -> str:
        sender = f"{self.sender} ({self.sender_kind})" if self.sender_kind else self.sender
        recipient = (
            f"{self.recipient} ({self.recipient_kind})" if self.recipient_kind else self.recipient
        )
        return _joined(
            f"von {sender} an {recipient}",
            f"erstellt am {self.prepared}" if self.prepared else "",
            f"Referenz {self.reference}" if self.reference else "",
            "Testübertragung" if self.test else "",
        )


@dataclass
class Document:
    """Der Inhalt einer Nachricht: Kopf, Beteiligte, Positionen und Summen."""

    message_type: str = ""
    message_label: str = ""
    directory: str = ""
    association: str = ""
    message_reference: str = ""
    envelope: Envelope | None = None

    code: str = ""
    """Dokumentenart als Code (BGM), z. B. ``220``."""
    name: str = ""
    """Dokumentenart im Klartext, z. B. ``Bestellung``."""
    number: str = ""
    function: str = ""
    """Nachrichtenfunktion im Klartext, z. B. ``Original``."""
    response: str = ""
    currency: str = ""

    dates: list[DateInfo] = field(default_factory=list)
    references: list[Reference] = field(default_factory=list)
    parties: list[Party] = field(default_factory=list)
    descriptions: list[str] = field(default_factory=list)
    texts: list[FreeText] = field(default_factory=list)
    payment_terms: list[PaymentTerms] = field(default_factory=list)
    delivery_terms: list[DeliveryTerms] = field(default_factory=list)
    transports: list[Transport] = field(default_factory=list)
    allowances: list[AllowanceCharge] = field(default_factory=list)
    taxes: list[Tax] = field(default_factory=list)
    packages: list[Package] = field(default_factory=list)
    locations: list[Location] = field(default_factory=list)
    items: list[LineItem] = field(default_factory=list)
    totals: list[Amount] = field(default_factory=list)
    controls: list[Control] = field(default_factory=list)
    unhandled: list[Segment] = field(default_factory=list)
    """Segmente, die nicht ausgewertet wurden; nichts geht stillschweigend verloren."""

    @property
    def title(self) -> str:
        name = self.name or self.message_label or self.message_type or "Dokument"
        return f"{name} Nr. {self.number}" if self.number else name

    def party(self, qualifier: str) -> Party | None:
        """Erster Beteiligter mit dieser Rolle (Kopfebene), z. B. ``"BY"`` für den Käufer."""
        return next((party for party in self.parties if party.qualifier == qualifier), None)

    def date(self, qualifier: str) -> DateInfo | None:
        """Erste Zeitangabe mit dieser Bedeutung (Kopfebene), z. B. ``"137"`` für das Belegdatum."""
        return next((entry for entry in self.dates if entry.qualifier == qualifier), None)

    def to_dict(self) -> dict[str, Any]:
        """Der gesamte Inhalt als verschachtelte, JSON-taugliche Struktur."""
        return _plain(self)


def _plain(value: Any) -> Any:
    if isinstance(value, Segment):
        return str(value)
    if dataclasses.is_dataclass(value) and not isinstance(value, type):
        return {f.name: _plain(getattr(value, f.name)) for f in dataclasses.fields(value)}
    if isinstance(value, list):
        return [_plain(entry) for entry in value]
    if isinstance(value, Decimal):
        return str(value)
    if isinstance(value, (date, datetime)):
        return value.isoformat()
    return value
