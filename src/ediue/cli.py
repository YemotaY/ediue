"""Kommandozeile: ``ediue DATEI ...`` oder ``python -m ediue DATEI ...``."""

from __future__ import annotations

import argparse
import sys
from collections.abc import Sequence
from pathlib import Path

from . import __version__
from .render import FORMATS, render
from .syntax import EdifactError, decode, parse


def main(argv: Sequence[str] | None = None) -> int:
    """Übersetzt die genannten Dateien; Rückgabe 1, wenn eine davon nicht lesbar war."""
    parser = argparse.ArgumentParser(
        prog="ediue",
        description="Übersetzt EDIFACT-Dateien (z. B. ORDERS) in lesbare Bestellungen.",
    )
    parser.add_argument(
        "files", nargs="+", metavar="DATEI", help="EDIFACT-Datei; '-' liest die Standardeingabe"
    )
    parser.add_argument(
        "-f",
        "--format",
        choices=FORMATS,
        default="text",
        help="Ausgabeformat (Vorgabe: text); 'segmente' erläutert jedes Segment einzeln",
    )
    parser.add_argument("-o", "--output", metavar="DATEI", help="Ausgabe in diese Datei schreiben")
    parser.add_argument(
        "-e", "--encoding", help="Zeichensatz der Eingabe, z. B. iso-8859-1 (Vorgabe: automatisch)"
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    args = parser.parse_args(argv)

    interchanges = []
    status = 0
    for name in args.files:
        try:
            data = sys.stdin.buffer.read() if name == "-" else Path(name).read_bytes()
            interchange = parse(decode(data, args.encoding))
        except (OSError, EdifactError, UnicodeError, LookupError) as error:
            print(f"{name}: {error}", file=sys.stderr)
            status = 1
            continue
        for warning in interchange.warnings:
            print(f"{name}: Warnung: {warning}", file=sys.stderr)
        interchanges.append(interchange)

    if interchanges:
        text = render(interchanges, args.format) + "\n"
        if args.output:
            Path(args.output).write_text(text, encoding="utf-8")
        else:
            sys.stdout.write(text)
    return status
