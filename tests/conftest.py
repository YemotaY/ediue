from pathlib import Path

import pytest

import ediue

EXAMPLE = Path(__file__).parent.parent / "examples" / "bestellung.edi"


@pytest.fixture
def example_path() -> Path:
    return EXAMPLE


@pytest.fixture
def order() -> ediue.Document:
    """Die Beispielbestellung aus ``examples/``."""
    (document,) = ediue.read_documents(ediue.load(EXAMPLE))
    return document


@pytest.fixture
def build():
    """Baut aus einzelnen Segmenten eine ORDERS-Nachricht und wertet sie aus."""

    def _build(*segments: str) -> ediue.Document:
        body = "".join(f"{segment}'" for segment in segments)
        text = f"UNH+1+ORDERS:D:96A:UN'{body}UNT+{len(segments) + 2}+1'"
        (document,) = ediue.read_documents(ediue.parse(text))
        return document

    return _build
