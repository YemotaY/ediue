"""Fachliche Auswertung: aus den Segmenten einer Nachricht wird ein :class:`Document`.

Die ``read_*``-Funktionen deuten je ein Segment. :func:`build_document`
ordnet die Ergebnisse dem Kopf, den Beteiligten, den Positionen oder den
Summen zu und folgt dabei dem Aufbau der Nachrichten ORDERS, ORDRSP und
ORDCHG; verwandte Nachrichten (DESADV, INVOIC ...) werden so weit gelesen,
wie sie dieselben Segmente verwenden.
"""

from __future__ import annotations

import dataclasses
from collections.abc import Sequence

from . import codes
from .codes import lookup
from .formatting import parse_datetime, parse_decimal
from .model import (
    AllowanceCharge,
    Amount,
    Channel,
    Contact,
    Control,
    DateInfo,
    DeliveryTerms,
    Document,
    Envelope,
    FreeText,
    LineItem,
    Location,
    Measurement,
    Package,
    Party,
    PaymentTerms,
    Percentage,
    Price,
    ProductId,
    Quantity,
    Reference,
    Schedule,
    Tax,
    Transport,
)
from .syntax import Interchange, Message, Segment

__all__ = ["build_document", "read_documents"]


def _filled(values: Sequence[str]) -> list[str]:
    return [value for value in values if value]


# --- einzelne Segmente ------------------------------------------------------


def read_envelope(seg: Segment) -> Envelope:
    """UNB: Absender, Empfänger, Erstellungszeitpunkt."""
    stamp = seg.get(3) + seg.get(3, 1)
    prepared, _ = parse_datetime(stamp, {6: "101", 8: "102", 10: "201", 12: "203"}.get(len(stamp), ""))
    return Envelope(
        sender=seg.get(1),
        recipient=seg.get(2),
        sender_kind=codes.PARTNER_IDS.get(seg.get(1, 1), ""),
        recipient_kind=codes.PARTNER_IDS.get(seg.get(2, 1), ""),
        prepared=prepared,
        reference=seg.get(4),
        test=seg.get(10) == "1",
    )


def read_date(seg: Segment) -> DateInfo:
    qualifier, raw, code = seg.get(0), seg.get(0, 1), seg.get(0, 2)
    text, value = parse_datetime(raw, code)
    return DateInfo(qualifier, lookup(codes.DATES, qualifier, "Datum"), raw, code, text, value)


def read_reference(seg: Segment) -> Reference:
    qualifier = seg.get(0)
    return Reference(
        qualifier, lookup(codes.REFERENCES, qualifier, "Referenz"), seg.get(0, 1), seg.get(0, 2)
    )


def read_party(seg: Segment) -> Party:
    qualifier, country = seg.get(0), seg.get(8)
    return Party(
        qualifier=qualifier,
        label=lookup(codes.PARTIES, qualifier, "Beteiligter"),
        id=seg.get(1),
        id_kind=codes.AGENCIES.get(seg.get(1, 2), ""),
        names=_filled(seg.components(3)[:5]),
        address_lines=_filled(seg.components(2)),
        street=_filled(seg.components(4)),
        postcode=seg.get(7),
        city=seg.get(5),
        region=seg.get(6, 3) or seg.get(6),
        country=country,
        country_name=codes.COUNTRIES.get(country, ""),
    )


def read_contact(seg: Segment) -> Contact:
    function = seg.get(0)
    return Contact(
        function=function,
        label=lookup(codes.CONTACTS, function, "Ansprechpartner"),
        name=seg.get(1, 1),
        department=seg.get(1, 0),
    )


def read_channels(seg: Segment) -> list[Channel]:
    """COM: ein Segment kann mehrere Erreichbarkeiten nennen."""
    channels = []
    for index in range(len(seg.elements)):
        number, kind = seg.get(index), seg.get(index, 1)
        if number:
            channels.append(Channel(kind, lookup(codes.CHANNELS, kind, "Kontakt"), number))
    return channels


def read_text(seg: Segment) -> FreeText:
    qualifier = seg.get(0)
    text = " ".join(_filled(seg.components(3)[:5])) or seg.get(2)
    return FreeText(qualifier, lookup(codes.TEXTS, qualifier, "Text"), text)


def read_line(seg: Segment) -> LineItem:
    action = seg.get(1)
    item = LineItem(number=seg.get(0), action=lookup(codes.LINE_ACTIONS, action, "Status") if action else "")
    if seg.get(2):
        item.product_ids.append(_product_id(seg.components(2)))
    return item


def read_product_ids(seg: Segment) -> list[ProductId]:
    """PIA: bis zu fünf weitere Artikelnummern."""
    function = codes.PRODUCT_ID_FUNCTIONS.get(seg.get(0), "")
    return [_product_id(element, function) for element in seg.elements[1:] if element and element[0]]


def _product_id(components: Sequence[str], function: str = "") -> ProductId:
    kind = components[1] if len(components) > 1 else ""
    label = lookup(codes.PRODUCT_IDS, kind, "Artikelnummer")
    return ProductId(components[0], kind, f"{label} ({function})" if function else label)


def read_description(seg: Segment) -> str:
    """IMD: Freitext, sonst die codierte Beschreibung im Klartext."""
    text = " ".join(_filled(seg.components(2)[3:5]))
    code = seg.get(2)
    return text or codes.ITEM_TYPES.get(code) or (f"Code {code}" if code else "")


def read_quantity(seg: Segment) -> Quantity:
    qualifier, raw, unit = seg.get(0), seg.get(0, 1), seg.get(0, 2)
    return Quantity(
        qualifier,
        lookup(codes.QUANTITIES, qualifier, "Menge"),
        raw,
        parse_decimal(raw),
        unit,
        codes.UNITS.get(unit, ""),
    )


def read_price(seg: Segment) -> Price:
    qualifier, raw, unit = seg.get(0), seg.get(0, 1), seg.get(0, 5)
    return Price(
        qualifier,
        lookup(codes.PRICES, qualifier, "Preis"),
        raw,
        parse_decimal(raw),
        kind=codes.PRICE_TYPES.get(seg.get(0, 2)) or codes.PRICE_SPECS.get(seg.get(0, 3), ""),
        basis=parse_decimal(seg.get(0, 4)),
        unit=unit,
        unit_label=codes.UNITS.get(unit, ""),
    )


def read_amount(seg: Segment) -> Amount:
    qualifier, raw = seg.get(0), seg.get(0, 1)
    return Amount(
        qualifier, lookup(codes.AMOUNTS, qualifier, "Betrag"), raw, parse_decimal(raw), seg.get(0, 2)
    )


def read_percentage(seg: Segment) -> Percentage:
    qualifier, raw = seg.get(0), seg.get(0, 1)
    return Percentage(
        qualifier, lookup(codes.PERCENTAGES, qualifier, "Prozentsatz"), raw, parse_decimal(raw)
    )


def read_tax(seg: Segment) -> Tax:
    kind, raw, category = seg.get(1), seg.get(4, 3), seg.get(5)
    return Tax(
        kind=kind,
        label=codes.TAX_TYPES.get(kind) or kind or "Steuer",
        raw=raw,
        rate=parse_decimal(raw),
        category=category,
        category_label=codes.TAX_CATEGORIES.get(category, ""),
    )


def read_allowance(seg: Segment) -> AllowanceCharge:
    kind, service = seg.get(0), seg.get(4)
    return AllowanceCharge(
        kind=kind,
        label=codes.ALLOWANCE_KINDS.get(kind, "Zu-/Abschlag"),
        service=service,
        description=" ".join(_filled(seg.components(4)[3:5])) or codes.SERVICES.get(service, service),
    )


def read_payment_terms(seg: Segment) -> PaymentTerms:
    qualifier = seg.get(0)
    reference, relation, period, count = (seg.get(2, index) for index in range(4))
    parts = []
    if count:
        singular, plural = codes.PERIODS.get(period, (period, period))
        parts.append(f"{count} {singular if count == '1' else plural}".rstrip())
    if reference or relation:
        parts.append(codes.TIME_RELATIONS.get(relation, ""))
        parts.append(lookup(codes.TIME_REFERENCES, reference, "Bezugsdatum"))
    description = ", ".join(_filled([" ".join(_filled(parts)), *seg.components(1)[3:5]]))
    return PaymentTerms(
        qualifier, lookup(codes.PAYMENT_TERMS, qualifier, "Zahlungsbedingung"), description
    )


def read_delivery_terms(seg: Segment) -> DeliveryTerms:
    function, code = seg.get(0), seg.get(2)
    description = ", ".join(_filled([codes.INCOTERMS.get(code, ""), *seg.components(2)[3:5]]))
    return DeliveryTerms(
        function, codes.DELIVERY_FUNCTIONS.get(function, "Lieferbedingung"), code, description
    )


def read_transport(seg: Segment) -> Transport:
    stage, mode = seg.get(0), seg.get(2)
    return Transport(
        stage=stage,
        label=codes.TRANSPORT_STAGES.get(stage, "Transport"),
        mode=mode,
        mode_label=seg.get(2, 1) or codes.TRANSPORT_MODES.get(mode, ""),
        means=seg.get(3, 1),
        carrier=seg.get(4, 3) or seg.get(4),
    )


def read_package(seg: Segment) -> Package:
    kind = seg.get(2)
    return Package(seg.get(0), kind, seg.get(2, 3) or codes.PACKAGES.get(kind, kind))


def read_measurement(seg: Segment) -> Measurement:
    dimension, unit, raw = seg.get(1), seg.get(2), seg.get(2, 1)
    return Measurement(
        dimension,
        lookup(codes.MEASUREMENTS, dimension, "Maß"),
        raw,
        parse_decimal(raw),
        unit,
        codes.UNITS.get(unit, ""),
    )


def read_location(seg: Segment) -> Location:
    qualifier = seg.get(0)
    return Location(qualifier, lookup(codes.LOCATIONS, qualifier, "Ort"), seg.get(1), seg.get(1, 3))


def read_schedule(seg: Segment) -> Schedule:
    status = seg.get(0)
    binding = codes.SCHEDULES.get(status)
    return Schedule(status, f"Liefereinteilung ({binding})" if binding else "Liefereinteilung")


def read_control(seg: Segment) -> Control:
    qualifier, raw = seg.get(0), seg.get(0, 1)
    return Control(qualifier, lookup(codes.CONTROLS, qualifier, "Kontrollwert"), raw, parse_decimal(raw))


# --- ganze Nachrichten --------------------------------------------------------

# Segmente, die zur Gruppe eines Beteiligten (NAD) gehören können.
_PARTY_GROUP = {"NAD", "LOC", "FII", "RFF", "DTM", "DOC", "CTA", "COM"}
# Nicht ausgewertete Segmente, die eine eigene Gruppe eröffnen.
_OPAQUE_GROUPS = {"APR", "CCI", "DGS", "DOC", "EQD", "HAN", "PCI", "RCS", "STG"}
# Platzhalter: Die laufende Gruppe wird nicht ausgewertet.
_SKIPPED = object()


class _Builder:
    """Liest die Segmente einer Nachricht der Reihe nach und merkt sich den Zusammenhang.

    ``item`` ist die laufende Position, ``party`` der Beteiligte, zu dessen
    Gruppe das aktuelle Segment noch gehören kann, und ``group`` das Objekt,
    dem abhängige Segmente (DTM, MOA, PCD ...) zugeordnet werden.
    """

    def __init__(self, message: Message) -> None:
        self.doc = Document(
            message_type=message.type,
            message_label=codes.MESSAGES.get(message.type, ""),
            directory=message.directory,
            association=message.association,
            message_reference=message.reference,
            envelope=read_envelope(message.envelope) if message.envelope else None,
        )
        self.item: LineItem | None = None
        self.party: Party | None = None
        self.group: object = None

    @property
    def owner(self) -> Document | LineItem:
        return self.item or self.doc

    def feed(self, seg: Segment) -> None:
        """Wertet ein Segment aus; was sich nicht zuordnen lässt, landet in ``unhandled``."""
        if seg.tag not in _PARTY_GROUP:
            self.party = None
        handler = getattr(self, f"_{seg.tag.lower()}", None)
        if handler is None:
            self._unhandled(seg, skip_group=seg.tag in _OPAQUE_GROUPS)
        else:
            handler(seg)

    def _unhandled(self, seg: Segment, skip_group: bool = False) -> None:
        """Vermerkt ein Segment als nicht ausgewertet, auf Wunsch samt den ihm untergeordneten."""
        self.doc.unhandled.append(seg)
        if skip_group:
            self.group = _SKIPPED

    # Ab hier je Segment eine Methode gleichen Namens.

    def _bgm(self, seg: Segment) -> None:
        doc = self.doc
        function, response = seg.get(2), seg.get(3)
        doc.code = seg.get(0)
        doc.name = codes.DOCUMENTS.get(doc.code) or seg.get(0, 3)
        doc.number = seg.get(1)
        doc.function = lookup(codes.FUNCTIONS, function, "Funktion") if function else ""
        doc.response = lookup(codes.RESPONSES, response, "Antwort") if response else ""
        self.group = None

    def _dtm(self, seg: Segment) -> None:
        if self.group is _SKIPPED:
            return self._unhandled(seg)
        dated = (Reference, Location, Schedule, PaymentTerms, Price, AllowanceCharge)
        target = self.group if isinstance(self.group, dated) else self.owner
        target.dates.append(read_date(seg))

    def _rff(self, seg: Segment) -> None:
        if self.group is _SKIPPED:
            return self._unhandled(seg)
        self.group = read_reference(seg)
        (self.party or self.owner).references.append(self.group)

    def _nad(self, seg: Segment) -> None:
        self.party = self.group = read_party(seg)
        self.owner.parties.append(self.party)

    def _cta(self, seg: Segment) -> None:
        if self.party is None:
            return self._unhandled(seg, skip_group=True)
        self.group = read_contact(seg)
        self.party.contacts.append(self.group)

    def _com(self, seg: Segment) -> None:
        if not isinstance(self.group, Contact):
            if self.party is None:
                return self._unhandled(seg)
            self.group = Contact(function="", label="Kontakt")
            self.party.contacts.append(self.group)
        self.group.channels.extend(read_channels(seg))

    def _loc(self, seg: Segment) -> None:
        if self.group is _SKIPPED:
            return self._unhandled(seg)
        self.group = read_location(seg)
        (self.party or self.owner).locations.append(self.group)

    def _ftx(self, seg: Segment) -> None:
        self.owner.texts.append(read_text(seg))

    def _imd(self, seg: Segment) -> None:
        description = read_description(seg)
        if not description:
            return self._unhandled(seg)
        self.owner.descriptions.append(description)

    def _cux(self, seg: Segment) -> None:
        currency = seg.get(0, 1)
        if isinstance(self.group, Price):
            self.group.currency = currency
        elif self.item is None and not self.doc.currency:
            self.doc.currency = currency
            self.group = None
        else:
            self._unhandled(seg)

    def _pat(self, seg: Segment) -> None:
        self.group = read_payment_terms(seg)
        self.doc.payment_terms.append(self.group)

    def _tod(self, seg: Segment) -> None:
        if self.item is not None:
            return self._unhandled(seg, skip_group=True)
        self.group = read_delivery_terms(seg)
        self.doc.delivery_terms.append(self.group)

    def _tdt(self, seg: Segment) -> None:
        if self.item is not None:
            return self._unhandled(seg, skip_group=True)
        self.group = read_transport(seg)
        self.doc.transports.append(self.group)

    def _tax(self, seg: Segment) -> None:
        self.group = read_tax(seg)
        self.owner.taxes.append(self.group)

    def _alc(self, seg: Segment) -> None:
        self.group = read_allowance(seg)
        self.owner.allowances.append(self.group)

    def _pac(self, seg: Segment) -> None:
        self.group = read_package(seg)
        self.owner.packages.append(self.group)

    def _pcd(self, seg: Segment) -> None:
        if isinstance(self.group, (PaymentTerms, AllowanceCharge)):
            self.group.percentages.append(read_percentage(seg))
        elif self.item is not None and self.group is not _SKIPPED:
            self.item.percentages.append(read_percentage(seg))
        else:
            self._unhandled(seg)

    def _moa(self, seg: Segment) -> None:
        if self.group is _SKIPPED:
            self._unhandled(seg)
        elif isinstance(self.group, (PaymentTerms, AllowanceCharge, Tax)):
            self.group.amounts.append(read_amount(seg))
        elif self.item is not None:
            self.item.amounts.append(read_amount(seg))
        else:
            self.doc.totals.append(read_amount(seg))

    def _lin(self, seg: Segment) -> None:
        self.item = read_line(seg)
        self.doc.items.append(self.item)
        self.group = None

    def _pia(self, seg: Segment) -> None:
        if self.item is None:
            return self._unhandled(seg)
        self.item.product_ids.extend(read_product_ids(seg))

    def _qty(self, seg: Segment) -> None:
        if isinstance(self.group, (Schedule, Location)):
            self.group.quantities.append(read_quantity(seg))
        elif self.item is not None and not (
            self.group is _SKIPPED or isinstance(self.group, (AllowanceCharge, Package))
        ):
            self.item.quantities.append(read_quantity(seg))
        else:
            self._unhandled(seg)

    def _pri(self, seg: Segment) -> None:
        if self.item is None:
            return self._unhandled(seg)
        self.group = read_price(seg)
        self.item.prices.append(self.group)

    def _mea(self, seg: Segment) -> None:
        if self.item is None or self.group is _SKIPPED or isinstance(self.group, Package):
            return self._unhandled(seg)
        self.item.measurements.append(read_measurement(seg))

    def _scc(self, seg: Segment) -> None:
        if self.item is None:
            return self._unhandled(seg, skip_group=True)
        self.group = read_schedule(seg)
        self.item.schedules.append(self.group)

    def _cps(self, seg: Segment) -> None:
        # Neue Packebene (DESADV): Was folgt, gehört nicht mehr zur letzten Position.
        self.item = None
        self.group = None
        self._unhandled(seg)

    def _uns(self, seg: Segment) -> None:
        if seg.get(0) == "S":
            self.item = None
        self.group = None

    def _cnt(self, seg: Segment) -> None:
        self.doc.controls.append(read_control(seg))


def _fill_currency(node: object, currency: str) -> None:
    """Trägt die Dokumentwährung bei allen Beträgen und Preisen ohne eigene Währung ein."""
    if isinstance(node, list):
        for entry in node:
            _fill_currency(entry, currency)
    elif isinstance(node, (Amount, Price)):
        node.currency = node.currency or currency
    elif dataclasses.is_dataclass(node):
        for field in dataclasses.fields(node):
            _fill_currency(getattr(node, field.name), currency)


def build_document(message: Message) -> Document:
    """Wertet eine Nachricht aus."""
    builder = _Builder(message)
    for segment in message.body:
        builder.feed(segment)
    if builder.doc.currency:
        _fill_currency(builder.doc, builder.doc.currency)
    return builder.doc


def read_documents(interchange: Interchange) -> list[Document]:
    """Wertet alle Nachrichten einer Übertragung aus."""
    return [build_document(message) for message in interchange.messages]
