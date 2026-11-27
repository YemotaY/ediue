import pytest

from ediue import EdifactSyntaxError, Segment, decode, parse

MESSAGE = "UNH+1+ORDERS:D:96A:UN:EAN008'BGM+220+123+9'UNT+3+1'"


def test_splits_segments_elements_and_components():
    interchange = parse(MESSAGE)

    assert [segment.tag for segment in interchange.segments] == ["UNH", "BGM", "UNT"]
    assert interchange.segments[0].elements == (("1",), ("ORDERS", "D", "96A", "UN", "EAN008"))


def test_message_exposes_header_fields_and_body():
    (message,) = parse(MESSAGE).messages

    assert (message.reference, message.type, message.directory) == ("1", "ORDERS", "D.96A")
    assert message.association == "EAN008"
    assert [segment.tag for segment in message.body] == ["BGM"]


def test_release_character_turns_separators_into_data():
    segment = parse("FTX+AAI+++a?+b?:c?'d??e'").segments[0]

    assert segment.get(3) == "a+b:c'd?e"


def test_una_defines_the_separators():
    interchange = parse("UNA;*,! |UNH*1*ORDERS;D;96A;UN|BGM*220*A!*B+C*9|UNT*3*1|")

    assert interchange.separators.decimal == ","
    assert interchange.messages[0].type == "ORDERS"
    assert interchange.segments[1].get(1) == "A*B+C"


def test_line_breaks_are_not_data():
    interchange = parse("UNH+1+ORDERS:D:96A:UN'\r\nBGM+220+12\n3+9'\nUNT+3+1'\n")

    assert interchange.segments[1].get(1) == "123"
    assert interchange.warnings == ["Die Datei enthält keinen Übertragungskopf (UNB)."]


def test_missing_values_read_as_empty_strings():
    segment = parse("NAD+BY+123::9'").segments[0]

    assert segment.get(1, 1) == ""
    assert segment.get(1, 7) == ""
    assert segment.get(9) == ""
    assert segment.components(9) == ()


def test_segment_str_escapes_separators():
    assert str(Segment("FTX", (("AAI",), ("a+b", "c'd?"), ("",)))) == "FTX+AAI+a?+b:c?'d??+'"


@pytest.mark.parametrize("text", ["", "   \n", "Hallo Welt", "Sehr geehrte Damen und Herren'"])
def test_rejects_input_that_is_not_edifact(text):
    with pytest.raises(EdifactSyntaxError):
        parse(text)


@pytest.mark.parametrize(
    ("text", "warning"),
    [
        ("UNH+1+ORDERS:D:96A:UN'BGM+220'UNT+9+1'", "UNT nennt 9 Segmente, enthalten sind 3"),
        ("UNH+1+ORDERS:D:96A:UN'BGM+220'UNT+3+2'", "Die Referenz in UNT lautet '2'"),
        ("UNH+1+ORDERS:D:96A:UN'BGM+220'UNH+2+ORDERS:D:96A:UN'UNT+2+2'", "Nachricht 1 hat kein"),
        ("UNH+1+ORDERS:D:96A:UN'BGM+220'UNT+3+1", "Das letzte Segment ist nicht abgeschlossen"),
        ("UNB+UNOA:3+A+B+240101:1200+R1'" + MESSAGE + "UNZ+5+R1'", "UNZ nennt 5"),
        ("UNB+UNOA:3+A+B+240101:1200+R1'" + MESSAGE + "UNZ+1+R2'", "Übertragungsreferenzen"),
        ("BGM+220'", "Segment BGM steht außerhalb einer Nachricht"),
        ("BGM+220'", "Die Datei enthält keine Nachricht"),
    ],
)
def test_structural_problems_become_warnings(text, warning):
    assert any(warning in entry for entry in parse(text).warnings)


def test_clean_interchange_has_no_warnings(example_path):
    assert parse(example_path.read_text(encoding="utf-8")).warnings == []


def test_message_without_unt_is_still_read():
    interchange = parse("UNH+1+ORDERS:D:96A:UN'BGM+220'UNZ+1+X'")

    assert [segment.tag for segment in interchange.messages[0].segments] == ["UNH", "BGM"]


def test_each_message_knows_its_envelope():
    text = (
        "UNB+UNOA:3+A+B+240101:1200+R1'" + MESSAGE + "UNZ+1+R1'"
        "UNB+UNOA:3+C+D+240101:1200+R2'" + MESSAGE + "UNZ+1+R2'"
    )

    first, second = parse(text).messages

    assert first.envelope.get(1) == "A"
    assert second.envelope.get(1) == "C"


def test_decode_prefers_utf8_and_falls_back_to_the_declared_charset():
    text = "UNB+UNOD:3+A+B'FTX+AAI+++Łódź'"

    assert decode(text.encode("utf-8")) == text
    assert decode(text.encode("iso-8859-2")) == text
    assert decode("UNB+UNOC:3'FTX+AAI+++Straße'".encode("iso-8859-1")).endswith("Straße'")
    assert decode(text.encode("cp1250"), encoding="cp1250") == text
