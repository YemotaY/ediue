"""Zahlen und Zeitangaben aus EDIFACT lesen und in deutscher Schreibweise ausgeben."""

from __future__ import annotations

import re
from datetime import date, datetime
from decimal import Decimal

__all__ = ["format_decimal", "parse_datetime", "parse_decimal"]

_NUMBER = re.compile(r"[+-]?(\d+([.,]\d*)?|[.,]\d+)")
_SWAP_MARKS = str.maketrans(",.", ".,")

_MONTHS = (
    "Januar", "Februar", "März", "April", "Mai", "Juni",
    "Juli", "August", "September", "Oktober", "November", "Dezember",
)  # fmt: skip

# Formatcode (DE 2379) -> (strptime-Muster, Länge, Ausgabeformat)
_POINTS = {
    "101": ("%y%m%d", 6, "%d.%m.%Y"),
    "102": ("%Y%m%d", 8, "%d.%m.%Y"),
    "201": ("%y%m%d%H%M", 10, "%d.%m.%Y, %H:%M Uhr"),
    "202": ("%y%m%d%H%M%S", 12, "%d.%m.%Y, %H:%M:%S Uhr"),
    "203": ("%Y%m%d%H%M", 12, "%d.%m.%Y, %H:%M Uhr"),
    "204": ("%Y%m%d%H%M%S", 14, "%d.%m.%Y, %H:%M:%S Uhr"),
}
# Zeiträume: Formatcode -> Formatcode der beiden Eckpunkte
_PERIODS = {"717": "101", "718": "102", "719": "203"}
_DURATIONS = {
    "801": ("Jahr", "Jahre"),
    "802": ("Monat", "Monate"),
    "803": ("Woche", "Wochen"),
    "804": ("Tag", "Tage"),
    "805": ("Stunde", "Stunden"),
    "806": ("Minute", "Minuten"),
}
# Monat (609/610) oder Kalenderwoche (615/616) eines Jahres: Formatcode -> Länge
_YEAR_PARTS = {"609": 4, "610": 6, "615": 4, "616": 6}
_GUESSED = {8: "102", 12: "203", 14: "204"}


def parse_decimal(raw: str) -> Decimal | None:
    """Liest eine EDIFACT-Zahl (Punkt oder Komma als Dezimalzeichen)."""
    raw = raw.strip()
    if not _NUMBER.fullmatch(raw):
        return None
    return Decimal(raw.replace(",", "."))


def format_decimal(value: Decimal, min_decimals: int = 0) -> str:
    """Deutsche Schreibweise: ``1234.5`` wird ``1.234,5``; Nachkommastellen bleiben erhalten."""
    exponent = value.as_tuple().exponent
    decimals = max(-exponent, min_decimals) if isinstance(exponent, int) else min_decimals
    return f"{value:,.{decimals}f}".translate(_SWAP_MARKS)


def parse_datetime(raw: str, code: str = "") -> tuple[str, date | datetime | None]:
    """Deutet einen DTM-Wert anhand seines Formatcodes (DE 2379).

    Liefert den lesbaren Text und, bei Zeitpunkten und Zeiträumen, den Wert
    bzw. Beginn als ``date``/``datetime``. Unbekannte Formate und ungültige
    Werte werden unverändert als Text zurückgegeben.
    """
    raw = raw.strip()
    digits = raw.replace("-", "")
    if not code and raw.isdigit():
        code = _GUESSED.get(len(raw), "")

    if code in _POINTS:
        value = _point(raw, code)
        if value is not None:
            return _show(value, code), value
    elif code in _PERIODS:
        base = _PERIODS[code]
        length = _POINTS[base][1]
        start, end = _point(digits[:length], base), _point(digits[length:], base)
        if start is not None and end is not None:
            return f"{_show(start, base)} bis {_show(end, base)}", start
    elif code == "303" and len(raw) > 12:
        value = _point(raw[:12], "203")
        if value is not None:
            return f"{_show(value, '203')} ({raw[12:]})", value
    elif code in _DURATIONS and raw.isdigit():
        singular, plural = _DURATIONS[code]
        return f"{int(raw)} {singular if int(raw) == 1 else plural}", None
    elif code in _YEAR_PARTS and raw.isdigit() and len(raw) == _YEAR_PARTS[code]:
        year, part = int(raw[:-2]), int(raw[-2:])
        if len(raw) == 4:
            year += 1900 if year >= 69 else 2000  # Jahrhundertgrenze wie bei strptime
        if code in ("609", "610") and 1 <= part <= 12:
            return f"{_MONTHS[part - 1]} {year}", None
        if code in ("615", "616") and 1 <= part <= 53:
            return f"KW {part}/{year}", None
    elif code in ("401", "402") and raw.isdigit() and len(raw) == (4 if code == "401" else 6):
        clock = ":".join(raw[i : i + 2] for i in range(0, len(raw), 2))
        if raw[:2] < "24" and all(part < "60" for part in clock.split(":")[1:]):
            return f"{clock} Uhr", None
    return raw, None


def _point(raw: str, code: str) -> date | datetime | None:
    pattern, length, _ = _POINTS[code]
    if len(raw) != length or not raw.isdigit():
        return None
    try:
        value = datetime.strptime(raw, pattern)
    except ValueError:
        return None
    return value.date() if length <= 8 else value


def _show(value: date | datetime, code: str) -> str:
    return value.strftime(_POINTS[code][2])
