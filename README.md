# ediue

Übersetzt EDIFACT-Dateien in lesbare Sprache. Aus einer Bestellung (ORDERS)
wird eine übersichtliche Darstellung mit Kopfdaten, Beteiligten, Konditionen,
Positionen und Summen – als Text, Markdown oder JSON. Reines Python ohne
Abhängigkeiten, nutzbar als Kommandozeilenprogramm und als Bibliothek.

```
UNH+1+ORDERS:D:96A:UN:EAN008'              Bestellung Nr. 4500012345
BGM+220+4500012345+9'                      Status: Original
DTM+137:20240315:102'              →       Belegdatum: 15.03.2024
NAD+BY+4012345000009::9++Muster ...        Käufer: Muster Handels GmbH ...
LIN+1++4000862141404:EN'                   Position 1 – Sechskantschraube M8x40
QTY+21:500:PCE'                            Bestellmenge: 500 Stück
```

## Installation

Benötigt Python 3.10 oder neuer. Lokal aus diesem Verzeichnis:

```sh
python3 -m venv .venv
.venv/bin/pip install -e ".[dev]"
```

Danach stehen das Kommando `.venv/bin/ediue` und das Paket `ediue` bereit.

## Kommandozeile

```sh
ediue examples/bestellung.edi                    # lesbarer Text
ediue -f markdown -o bestellung.md datei.edi     # Markdown in eine Datei
ediue -f json *.edi                              # alle Dokumente als eine JSON-Liste
ediue -f segmente datei.edi                      # jedes Segment einzeln erläutert
cat datei.edi | ediue -                          # von der Standardeingabe
```

| Option | Bedeutung |
| --- | --- |
| `-f`, `--format` | `text` (Vorgabe), `markdown`, `json` oder `segmente` |
| `-o`, `--output` | Ausgabe in eine Datei (UTF-8) statt auf den Bildschirm |
| `-e`, `--encoding` | Zeichensatz der Eingabe erzwingen, z. B. `iso-8859-1` |

Warnungen und Fehler erscheinen auf der Fehlerausgabe. Der Rückgabewert ist 1,
wenn eine der Dateien nicht gelesen werden konnte; die übrigen werden trotzdem
übersetzt.

Ausgabe für `examples/bestellung.edi` (gekürzt):

```
============================================================
Bestellung Nr. 4500012345
============================================================
Status: Original
Belegdatum: 15.03.2024
Lieferdatum (gewünscht): 22.03.2024
Währung: EUR
Nachricht: ORDERS D.96A (EAN008), Referenz 1

Beteiligte
----------
  Käufer
    Muster Handels GmbH
    Hauptstraße 1
    10115 Berlin, Deutschland
    GLN: 4012345000009
    USt-IdNr.: DE123456789
    Ansprechpartner Bestellung: Erika Mustermann (Telefon: 030 1234567, E-Mail: einkauf@muster.example)

Konditionen
-----------
  Skonto: 10 Tage nach Rechnungsdatum, Nachlass: 2 %
  Zahlungsbedingung: 30 Tage nach Rechnungsdatum
  Lieferbedingung: DAP (geliefert benannter Ort)

Positionen
----------
  Position 1 – Sechskantschraube M8x40 verzinkt
    EAN/GTIN: 4000862141404
    Artikelnummer des Lieferanten: SK-M8-40
    Artikelnummer des Käufers: 100234
    Bestellmenge: 500 Stück
    Nettopreis: 12,50 EUR je 100 Stück (Vertragspreis)
    Positionsbetrag: 62,50 EUR

Summen
------
  Summe der Positionsbeträge: 211,30 EUR
  Anzahl der Positionen: 3
```

Die Segmentansicht (`-f segmente`) funktioniert mit jeder EDIFACT-Datei,
unabhängig vom Nachrichtentyp:

```
BGM  Beginn der Nachricht – Bestellung Nr. 4500012345, Original
DTM  Datum/Zeit – Belegdatum: 15.03.2024
QTY  Menge – Bestellmenge: 500 Stück
```

## Verwendung als Bibliothek

In einem Schritt:

```python
import ediue

print(ediue.convert_file("examples/bestellung.edi"))             # Text
markdown = ediue.convert_file("examples/bestellung.edi", "markdown")
text = ediue.convert(b"UNH+1+ORDERS:D:96A:UN'BGM+220+4711+9'UNT+3+1'")
```

Mit Zugriff auf die einzelnen Angaben:

```python
import ediue

interchange = ediue.load("examples/bestellung.edi")
for warning in interchange.warnings:
    print("Warnung:", warning)

for order in ediue.read_documents(interchange):
    print(order.title)                          # Bestellung Nr. 4500012345
    print(order.date("137").value)              # 2024-03-15 (datetime.date)
    print(order.party("BY").names)              # ['Muster Handels GmbH']
    for item in order.items:
        quantity = item.quantities[0]
        print(item.number, item.descriptions, quantity.value, quantity.unit)
        print(item.prices[0])                   # Nettopreis: 12,50 EUR je 100 Stück (Vertragspreis)
    data = order.to_dict()                      # JSON-taugliche Struktur
```

### Aufbau

| Modul | Aufgabe | Wichtigste Namen |
| --- | --- | --- |
| `ediue.syntax` | Datei in Segmente und Nachrichten zerlegen | `parse`, `load`, `decode`, `Interchange`, `Message`, `Segment` |
| `ediue.interpret` | Nachricht fachlich auswerten | `read_documents`, `build_document` |
| `ediue.model` | Datenklassen des Ergebnisses | `Document`, `LineItem`, `Party`, `Quantity`, `Price`, ... |
| `ediue.render` | Ausgabe erzeugen | `render`, `render_text`, `render_markdown` |
| `ediue.explain` | Segmentansicht | `explain`, `Explanation` |
| `ediue.codes` | Codelisten im Klartext | `lookup`, `DATES`, `PARTIES`, `UNITS`, ... |

Ein `Document` enthält `dates`, `references`, `parties`, `texts`,
`payment_terms`, `delivery_terms`, `transports`, `allowances`, `taxes`,
`items`, `totals` und `controls`. Jedes Objekt darin hat eine Bezeichnung
(`label`) und einen lesbaren Wert (`text`); `str(objekt)` ergibt eine Zeile
wie `Belegdatum: 15.03.2024`. Codes und Rohwerte (`qualifier`, `raw`, `unit`
...) bleiben daneben erhalten, Zahlen stehen als `Decimal` in `value`.

Segmente greift man über Positionen ab 0 zu: `segment.get(1, 2)` ist die
dritte Komponente des zweiten Datenelements; fehlende Werte ergeben `""`.

## Was ausgewertet wird

| Bereich | Segmente |
| --- | --- |
| Umschlag | UNA, UNB, UNH, UNT, UNZ |
| Kopf | BGM, DTM, RFF, FTX, IMD, CUX |
| Beteiligte | NAD mit RFF, CTA, COM, LOC |
| Konditionen | PAT, PCD, TOD, TDT, ALC, TAX, MOA, PAC |
| Positionen | LIN, PIA, IMD, QTY, PRI, MOA, PCD, DTM, RFF, FTX, MEA, ALC, TAX, SCC, LOC, NAD, PAC |
| Summen | UNS, MOA, CNT |

Die Zuordnung folgt dem Aufbau von ORDERS, ORDRSP und ORDCHG: Ein DTM nach
einem RFF ist das Datum der Referenz, ein MOA nach einem ALC der Betrag des
Zu- oder Abschlags, ein RFF nach einem NAD gehört zum Beteiligten usw.
Fehlt bei einem Betrag oder Preis die Währung, wird die des Dokuments (CUX)
eingetragen.

## Grenzen

- Die Auswertung ist auf Bestellnachrichten ausgerichtet. Verwandte Nachrichten
  (DESADV, INVOIC ...) werden so weit gelesen, wie sie dieselben Segmente
  verwenden; für alles andere gibt es die Segmentansicht.
- Nicht ausgewertete Segmente (z. B. FII, DOC, GIN, PCI, EQD, ALI, PAI sowie
  TOD und TDT auf Positionsebene) gehen nicht verloren: Sie stehen in
  `Document.unhandled` und in der Ausgabe unter „Nicht ausgewertete Segmente“.
- Die Codelisten sind eine Auswahl der gebräuchlichsten Codes. Unbekannte
  Codes erscheinen als `Datum (Code 998)` statt zu verschwinden.
- Es findet keine Prüfung gegen das Nachrichtenverzeichnis statt
  (Pflichtsegmente, Feldlängen). Geprüft werden nur die Zähler und Referenzen
  in UNT und UNZ; Abweichungen stehen in `Interchange.warnings`.
- Der Wiederholungstrenner `*` der Syntaxversion 4 wird nicht aufgelöst,
  Nachrichtengruppen (UNG/UNE) werden übersprungen.
- Zeichensatz: Zuerst wird UTF-8 versucht, sonst gilt der im UNB genannte
  Zeichensatz (UNOC = ISO 8859-1 usw.). Die Beispieldatei ist UTF-8.
- Die Ausgabe ist deutsch.

## Entwicklung

```sh
.venv/bin/python -m pytest          # Tests
.venv/bin/pip install build
.venv/bin/python -m build           # Wheel und sdist nach dist/
```

Neue Codes gehören in `src/ediue/codes.py`. Ein weiteres Segment braucht eine
`read_*`-Funktion und eine gleichnamige Methode in `_Builder`
(`src/ediue/interpret.py`) sowie einen Eintrag in `_READERS`
(`src/ediue/explain.py`).

## Lizenz

MIT, siehe [LICENSE](LICENSE).
