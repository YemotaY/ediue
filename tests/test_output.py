import json

import pytest

import ediue
from ediue.cli import main


def test_text_shows_the_order_at_a_glance(example_path):
    text = ediue.convert_file(example_path)

    for line in (
        "Bestellung Nr. 4500012345",
        "Belegdatum: 15.03.2024",
        "  Käufer",
        "    Muster Handels GmbH",
        "    10115 Berlin, Deutschland",
        "  Position 1 – Sechskantschraube M8x40 verzinkt",
        "    Bestellmenge: 500 Stück",
        "  Summe der Positionsbeträge: 211,30 EUR",
    ):
        assert line in text.splitlines()
    assert "Nicht ausgewertete Segmente" not in text


def test_text_lists_segments_that_were_not_interpreted():
    text = ediue.convert("UNH+1+ORDERS:D:96A:UN'BGM+220+1'LIN+1'GIN+BJ+3401'UNT+5+1'")

    assert text.endswith("Nicht ausgewertete Segmente\n---------------------------\n  GIN+BJ+3401'")


def test_markdown_escapes_data(example_path):
    markdown = ediue.convert(
        "UNH+1+ORDERS:D:96A:UN'BGM+220+A_1*'FTX+AAI+++siehe [Anhang]'UNT+4+1'", "markdown"
    )

    assert markdown.startswith("# Bestellung Nr. A\\_1\\*\n")
    assert "- **Allgemeine Information:** siehe \\[Anhang\\]" in markdown
    assert "### Käufer" in ediue.convert_file(example_path, "markdown")


def test_json_contains_every_document(example_path):
    (document,) = json.loads(ediue.convert_file(example_path, "json"))

    assert document["number"] == "4500012345"
    assert len(document["items"]) == 3


def test_segment_view_explains_every_segment(example_path):
    lines = ediue.convert_file(example_path, "segmente").splitlines()

    assert len(lines) == len(ediue.load(example_path).segments)
    assert "BGM  Beginn der Nachricht – Bestellung Nr. 4500012345, Original" in lines
    assert "QTY  Menge – Bestellmenge: 500 Stück" in lines


def test_segment_view_shows_unknown_segments_verbatim():
    text = ediue.convert("UNH+1+ORDERS:D:96A:UN'XYZ+1:2'UNT+3+1'", "segmente")

    assert "XYZ  Unbekanntes Segment – nicht ausgewertet: XYZ+1:2'" in text.splitlines()


def test_convert_accepts_bytes_in_the_declared_charset():
    data = "UNB+UNOC:3+A+B+240101:1200+1'UNH+1+ORDERS:D:96A:UN'FTX+AAI+++Grüße'UNT+3+1'UNZ+1+1'"

    assert "Allgemeine Information: Grüße" in ediue.convert(data.encode("iso-8859-1"))


def test_unknown_format_is_rejected():
    with pytest.raises(ValueError, match="Unbekanntes Format"):
        ediue.convert("UNH+1+ORDERS:D:96A:UN'UNT+2+1'", "pdf")


def test_cli_prints_the_order(example_path, capsys):
    assert main([str(example_path)]) == 0

    captured = capsys.readouterr()
    assert captured.out == ediue.convert_file(example_path) + "\n"
    assert captured.err == ""


def test_cli_writes_output_file_and_merges_json(example_path, tmp_path, capsys):
    target = tmp_path / "bestellungen.json"

    assert main(["-f", "json", "-o", str(target), str(example_path), str(example_path)]) == 0

    assert len(json.loads(target.read_text(encoding="utf-8"))) == 2
    assert capsys.readouterr().out == ""


def test_cli_reports_unreadable_files_and_continues(example_path, tmp_path, capsys):
    broken = tmp_path / "brief.txt"
    broken.write_text("Sehr geehrte Damen und Herren", encoding="utf-8")

    assert main([str(tmp_path / "fehlt.edi"), str(broken), str(example_path)]) == 1

    captured = capsys.readouterr()
    assert "fehlt.edi" in captured.err
    assert "brief.txt: Segment 1" in captured.err
    assert "Bestellung Nr. 4500012345" in captured.out


def test_cli_prints_warnings_to_stderr(tmp_path, capsys):
    path = tmp_path / "kurz.edi"
    path.write_text("UNH+1+ORDERS:D:96A:UN'BGM+220+1'UNT+7+1'", encoding="utf-8")

    assert main([str(path)]) == 0

    assert "Warnung: Nachricht 1: UNT nennt 7 Segmente" in capsys.readouterr().err
