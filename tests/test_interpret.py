from datetime import date
from decimal import Decimal


def tags(document):
    return [segment.tag for segment in document.unhandled]


def test_order_header(order):
    assert order.title == "Bestellung Nr. 4500012345"
    assert (order.message_type, order.directory, order.association) == ("ORDERS", "D.96A", "EAN008")
    assert (order.function, order.currency) == ("Original", "EUR")
    assert order.date("137").value == date(2024, 3, 15)
    assert str(order.date("2")) == "Lieferdatum (gewünscht): 22.03.2024"
    assert order.unhandled == []


def test_order_envelope(order):
    assert order.envelope.sender == "4012345000009"
    assert order.envelope.sender_kind == "GLN"
    assert order.envelope.prepared == "15.03.2024, 10:30 Uhr"
    assert order.envelope.test is True


def test_date_after_reference_belongs_to_the_reference(order):
    (contract,) = order.references

    assert str(contract) == "Vertragsnummer: V-2024-17, Referenzdatum: 01.01.2024"
    assert [entry.qualifier for entry in order.dates] == ["137", "2"]


def test_parties_collect_their_references_and_contacts(order):
    buyer = order.party("BY")

    assert [party.label for party in order.parties] == ["Käufer", "Lieferant", "Lieferanschrift"]
    assert buyer.address == ["Muster Handels GmbH", "Hauptstraße 1", "10115 Berlin, Deutschland"]
    assert (buyer.id, buyer.id_kind) == ("4012345000009", "GLN")
    assert [str(reference) for reference in buyer.references] == ["USt-IdNr.: DE123456789"]
    assert [str(contact) for contact in buyer.contacts] == [
        "Ansprechpartner Bestellung: Erika Mustermann "
        "(Telefon: 030 1234567, E-Mail: einkauf@muster.example)"
    ]
    assert order.party("DP").names == ["Muster Handels GmbH", "Zentrallager"]
    assert order.party("XX") is None


def test_terms(order):
    assert [str(terms) for terms in order.payment_terms] == [
        "Skonto: 10 Tage nach Rechnungsdatum, Nachlass: 2 %",
        "Zahlungsbedingung: 30 Tage nach Rechnungsdatum",
    ]
    assert [str(terms) for terms in order.delivery_terms] == [
        "Lieferbedingung: DAP (geliefert benannter Ort)"
    ]


def test_line_items(order):
    first, second, third = order.items

    assert first.label == "Position 1"
    assert first.descriptions == ["Sechskantschraube M8x40 verzinkt"]
    assert [str(entry) for entry in first.product_ids] == [
        "EAN/GTIN: 4000862141404",
        "Artikelnummer des Lieferanten: SK-M8-40",
        "Artikelnummer des Käufers: 100234",
    ]
    assert first.quantities[0].value == Decimal("500")
    assert str(first.quantities[0]) == "Bestellmenge: 500 Stück"
    assert str(first.prices[0]) == "Nettopreis: 12,50 EUR je 100 Stück (Vertragspreis)"
    assert str(first.amounts[0]) == "Positionsbetrag: 62,50 EUR"
    assert [str(entry) for entry in second.dates] == ["Lieferdatum (gewünscht): 29.03.2024"]
    assert third.descriptions == ["Montagepaste 250 ml: hitzebeständig"]
    assert str(third.prices[0]) == "Nettopreis: 8,90 EUR"


def test_summary_amounts_are_totals_not_line_amounts(order):
    assert [str(total) for total in order.totals] == ["Summe der Positionsbeträge: 211,30 EUR"]
    assert [str(control) for control in order.controls] == ["Anzahl der Positionen: 3"]
    assert len(order.items[-1].amounts) == 1


def test_allowances_and_taxes_keep_their_percentages_and_amounts(build):
    document = build(
        "LIN+1+3+4000862141404:EN",
        "QTY+21:10:PCE",
        "PRI+AAB:100",
        "ALC+A++++DI",
        "PCD+1:10",
        "MOA+204:100",
        "TAX+7+VAT+++:::19+S",
        "MOA+124:171:EUR",
    )
    (item,) = document.items

    assert item.action == "Geändert"
    assert [str(entry) for entry in item.allowances] == [
        "Abschlag: Rabatt, Abschlag: 10 %, Abschlagsbetrag: 100,00"
    ]
    assert [str(entry) for entry in item.taxes] == [
        "Umsatzsteuer: 19 %, Normalsatz, Steuerbetrag: 171,00 EUR"
    ]
    assert item.amounts == []
    assert item.percentages == []


def test_schedules_split_a_line_into_deliveries(build):
    document = build(
        "LIN+1",
        "QTY+21:100:PCE",
        "SCC+1",
        "QTY+113:60:PCE",
        "DTM+2:20240401:102",
        "SCC+1",
        "QTY+113:40:PCE",
        "DTM+2:20240501:102",
    )
    (item,) = document.items

    assert [str(entry) for entry in item.quantities] == ["Bestellmenge: 100 Stück"]
    assert item.dates == []
    assert [str(entry) for entry in item.schedules] == [
        "Liefereinteilung (fest): Zu liefernde Menge: 60 Stück, Lieferdatum (gewünscht): 01.04.2024",
        "Liefereinteilung (fest): Zu liefernde Menge: 40 Stück, Lieferdatum (gewünscht): 01.05.2024",
    ]


def test_line_level_location_takes_quantity_and_date(build):
    document = build("LIN+1", "QTY+21:10:PCE", "LOC+7+4012345000092::9", "QTY+11:4:PCE", "DTM+2:20240401:102")
    (item,) = document.items

    assert len(item.quantities) == 1
    assert [str(entry) for entry in item.locations] == [
        "Lieferort: 4012345000092, Teilmenge: 4 Stück, Lieferdatum (gewünscht): 01.04.2024"
    ]


def test_line_level_party_and_reference(build):
    document = build("NAD+BY+1::9", "LIN+1", "RFF+ON:4711:2", "NAD+DP+2::9", "RFF+API:77")
    (item,) = document.items

    assert [party.qualifier for party in document.parties] == ["BY"]
    assert [str(reference) for reference in item.references] == ["Bestellnummer: 4711, Position 2"]
    assert [str(reference) for reference in item.parties[0].references] == [
        "Zusätzliche Partnerkennung: 77"
    ]


def test_document_currency_applies_where_none_is_given(build):
    document = build("CUX+2:CHF:9", "LIN+1", "PRI+AAA:5", "UNS+S", "MOA+86:10", "MOA+86:11:EUR")

    assert document.items[0].prices[0].currency == "CHF"
    assert [total.currency for total in document.totals] == ["CHF", "EUR"]


def test_uninterpreted_groups_are_reported_not_misattributed(build):
    document = build(
        "BGM+220+1+9",
        "EQD+CN+ABCU1234567",
        "MEA+AAE+G+KGM:5",
        "DTM+7:20240101:102",
        "NAD+BY+1::9",
        "LIN+1",
        "GIN+BJ+340123450000000014",
        "DTM+2:20240401:102",
        "TOD+6++EXW",
        "LOC+1+DEHAM",
    )

    assert tags(document) == ["EQD", "MEA", "DTM", "GIN", "TOD", "LOC"]
    assert document.dates == []
    assert document.delivery_terms == []
    assert [str(entry) for entry in document.items[0].dates] == ["Lieferdatum (gewünscht): 01.04.2024"]


def test_contact_without_party_is_not_guessed(build):
    document = build("CTA+OC+:Max", "COM+1:TE")

    assert tags(document) == ["CTA", "COM"]


def test_unknown_codes_stay_visible(build):
    document = build("BGM+999:::Sonderbeleg+7+88", "DTM+998:20240101:102", "NAD+QQ+1", "LIN+1", "QTY+997:3:XYZ")

    assert document.title == "Sonderbeleg Nr. 7"
    assert document.function == "Funktion (Code 88)"
    assert str(document.dates[0]) == "Datum (Code 998): 01.01.2024"
    assert str(document.parties[0]) == "Beteiligter (Code QQ): Kennung: 1"
    assert str(document.items[0].quantities[0]) == "Menge (Code 997): 3 XYZ"


def test_document_without_bgm_is_named_after_its_message_type(build):
    assert build("DTM+137:20240101:102").title == "Bestellung"


def test_new_packing_level_ends_the_line_item(build):
    document = build("CPS+1", "PAC+2++201", "LIN+1", "QTY+12:5:PCE", "CPS+2+1", "PAC+1++CT")

    assert [str(package) for package in document.packages] == [
        "Packstücke: 2 × Europalette",
        "Packstücke: 1 × Karton",
    ]
    assert document.items[0].packages == []
    assert tags(document) == ["CPS", "CPS"]


def test_to_dict_is_plain_data(order):
    data = order.to_dict()

    assert data["dates"][0]["value"] == "2024-03-15"
    assert data["items"][0]["quantities"][0]["value"] == "500"
    assert data["parties"][0]["contacts"][0]["channels"][1]["text"] == "einkauf@muster.example"
