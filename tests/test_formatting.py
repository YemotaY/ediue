from datetime import date, datetime
from decimal import Decimal

import pytest

from ediue.formatting import format_decimal, parse_datetime, parse_decimal


@pytest.mark.parametrize(
    ("raw", "code", "text"),
    [
        ("20240315", "102", "15.03.2024"),
        ("240315", "101", "15.03.2024"),
        ("202403151430", "203", "15.03.2024, 14:30 Uhr"),
        ("20240315143005", "204", "15.03.2024, 14:30:05 Uhr"),
        ("202403151430CET", "303", "15.03.2024, 14:30 Uhr (CET)"),
        ("2024031520240320", "718", "15.03.2024 bis 20.03.2024"),
        ("20240315-20240320", "718", "15.03.2024 bis 20.03.2024"),
        ("202403", "610", "März 2024"),
        ("2403", "609", "März 2024"),
        ("202412", "616", "KW 12/2024"),
        ("30", "804", "30 Tage"),
        ("1", "802", "1 Monat"),
        ("1430", "401", "14:30 Uhr"),
        ("20240315", "", "15.03.2024"),
    ],
)
def test_known_formats_are_written_out(raw, code, text):
    assert parse_datetime(raw, code)[0] == text


@pytest.mark.parametrize(
    ("raw", "code"),
    [("20241345", "102"), ("2024", "102"), ("202413", "610"), ("2570", "401"), ("bald", "ZZZ")],
)
def test_unreadable_values_are_passed_through(raw, code):
    assert parse_datetime(raw, code) == (raw, None)


def test_points_in_time_come_with_a_python_value():
    assert parse_datetime("20240315", "102")[1] == date(2024, 3, 15)
    assert parse_datetime("202403151430", "203")[1] == datetime(2024, 3, 15, 14, 30)
    assert parse_datetime("2024031520240320", "718")[1] == date(2024, 3, 15)


@pytest.mark.parametrize(
    ("raw", "value"),
    [("12.5", "12.5"), ("12,5", "12.5"), ("-3", "-3"), (".5", "0.5"), ("abc", None), ("NaN", None)],
)
def test_parse_decimal(raw, value):
    assert parse_decimal(raw) == (None if value is None else Decimal(value))


@pytest.mark.parametrize(
    ("value", "min_decimals", "text"),
    [
        ("1234.5", 0, "1.234,5"),
        ("1234.5", 2, "1.234,50"),
        ("1000", 0, "1.000"),
        ("0.12345", 2, "0,12345"),
        ("-1234567.8", 2, "-1.234.567,80"),
    ],
)
def test_format_decimal(value, min_decimals, text):
    assert format_decimal(Decimal(value), min_decimals) == text
