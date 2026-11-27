"""Codelisten: Klartext zu den gebräuchlichsten EDIFACT-Codes.

Die Tabellen sind bewusst eine Auswahl. Unbekannte Codes gehen nicht
verloren, sondern erscheinen in der Ausgabe als ``… (Code X)``.
"""

from __future__ import annotations


def lookup(table: dict[str, str], code: str, kind: str) -> str:
    """Klartext zu ``code``; unbekannte Codes bleiben mit ``kind`` sichtbar."""
    if code in table:
        return table[code]
    return f"{kind} (Code {code})" if code else kind


# Nachrichtentypen (UNH, DE 0065)
MESSAGES = {
    "APERAK": "Anwendungsfehler- und Bestätigungsmeldung",
    "CONTRL": "Syntax- und Servicebericht",
    "DELFOR": "Lieferabruf",
    "DELJIT": "Feinabruf",
    "DESADV": "Lieferavis",
    "IFTMIN": "Transportauftrag",
    "IFTSTA": "Transportstatusmeldung",
    "INVOIC": "Rechnung",
    "INVRPT": "Lagerbestandsbericht",
    "ORDCHG": "Bestelländerung",
    "ORDERS": "Bestellung",
    "ORDRSP": "Bestellantwort",
    "OSTENQ": "Bestellstatusanfrage",
    "OSTRPT": "Bestellstatusbericht",
    "PARTIN": "Partnerstammdaten",
    "PRICAT": "Preisliste/Katalog",
    "PRODAT": "Produktstammdaten",
    "QUOTES": "Angebot",
    "RECADV": "Wareneingangsmeldung",
    "REMADV": "Zahlungsavis",
    "REQOTE": "Angebotsanfrage",
    "SLSRPT": "Verkaufsdatenbericht",
}

# Segmentnamen
SEGMENTS = {
    "ALC": "Zu- oder Abschlag",
    "ALI": "Zusatzinformation",
    "BGM": "Beginn der Nachricht",
    "CNT": "Kontrollsumme",
    "COM": "Kommunikationsverbindung",
    "CPS": "Packfolge",
    "CTA": "Ansprechpartner",
    "CUX": "Währung",
    "DGS": "Gefahrgut",
    "DOC": "Dokumentenangaben",
    "DTM": "Datum/Zeit",
    "EQD": "Transportmittel/Behälter",
    "FII": "Bankverbindung",
    "FTX": "Freitext",
    "GIN": "Identifikationsnummern",
    "HAN": "Handhabungshinweise",
    "IMD": "Artikelbeschreibung",
    "LIN": "Position",
    "LOC": "Ortsangabe",
    "MEA": "Maße und Gewichte",
    "MOA": "Geldbetrag",
    "NAD": "Name und Anschrift",
    "PAC": "Verpackung",
    "PAI": "Zahlungsanweisung",
    "PAT": "Zahlungsbedingungen",
    "PCD": "Prozentangabe",
    "PCI": "Packstückkennzeichnung",
    "PIA": "Zusätzliche Artikelkennung",
    "PRI": "Preis",
    "QTY": "Menge",
    "QVR": "Mengenabweichung",
    "RFF": "Referenz",
    "RNG": "Bereichsangabe",
    "SCC": "Liefereinteilung",
    "TAX": "Steuer/Zoll/Gebühr",
    "TDT": "Transportangaben",
    "TOD": "Lieferbedingungen",
    "UNB": "Übertragungskopf",
    "UNE": "Gruppenende",
    "UNG": "Gruppenkopf",
    "UNH": "Nachrichtenkopf",
    "UNS": "Abschnittstrenner",
    "UNT": "Nachrichtenende",
    "UNZ": "Übertragungsende",
}

# Kennzeichnung der Partner im UNB (DE 0007)
PARTNER_IDS = {"1": "DUNS", "14": "GLN", "ZZ": "bilateral vereinbart", "ZZZ": "bilateral vereinbart"}

# Verantwortliche Stelle einer Kennung (DE 3055)
AGENCIES = {
    "9": "GLN",
    "16": "DUNS",
    "91": "Nummer (vom Lieferanten vergeben)",
    "92": "Nummer (vom Käufer vergeben)",
}

# Dokumentenart (BGM, DE 1001)
DOCUMENTS = {
    "105": "Bestellung",
    "220": "Bestellung",
    "221": "Rahmenbestellung",
    "224": "Eilbestellung",
    "226": "Abrufbestellung",
    "227": "Konsignationsbestellung",
    "228": "Musterbestellung",
    "230": "Bestelländerung",
    "231": "Bestellantwort",
    "241": "Lieferplan",
    "270": "Lieferschein",
    "325": "Proformarechnung",
    "351": "Lieferavis",
    "380": "Handelsrechnung",
    "381": "Gutschrift",
    "383": "Belastungsanzeige",
}

# Nachrichtenfunktion (BGM, DE 1225)
FUNCTIONS = {
    "1": "Stornierung",
    "2": "Ergänzung",
    "3": "Löschung",
    "4": "Änderung",
    "5": "Ersatz",
    "6": "Bestätigung",
    "7": "Duplikat",
    "9": "Original",
    "13": "Anfrage",
    "16": "Vorschlag",
    "27": "Nicht angenommen",
    "29": "Ohne Änderung angenommen",
    "31": "Kopie",
    "46": "Vorläufig",
    "47": "Endgültig",
}

# Art der gewünschten bzw. gegebenen Antwort (BGM, DE 4343)
RESPONSES = {
    "AB": "Empfangsbestätigung",
    "AC": "Bestätigung mit Details und Änderungen",
    "AI": "Bestätigung nur der Änderungen",
    "AP": "Angenommen",
    "CA": "Unter Vorbehalt angenommen",
    "NA": "Keine Bestätigung erforderlich",
    "RE": "Abgelehnt",
}

# Bedeutung einer Zeitangabe (DTM, DE 2005)
DATES = {
    "2": "Lieferdatum (gewünscht)",
    "3": "Rechnungsdatum",
    "4": "Bestelldatum",
    "7": "Wirksamkeitsdatum",
    "8": "Bestelleingang",
    "9": "Bearbeitungsdatum",
    "10": "Versanddatum (gewünscht)",
    "11": "Versanddatum",
    "12": "Skontofälligkeit",
    "13": "Nettofälligkeit",
    "17": "Lieferdatum (voraussichtlich)",
    "35": "Lieferdatum (tatsächlich)",
    "36": "Verfallsdatum",
    "50": "Wareneingangsdatum",
    "63": "Lieferdatum (spätestens)",
    "64": "Lieferdatum (frühestens)",
    "69": "Lieferdatum (zugesagt)",
    "76": "Lieferdatum (geplant)",
    "94": "Herstellungsdatum",
    "131": "Steuerzeitpunkt",
    "132": "Ankunft (voraussichtlich)",
    "133": "Abfahrt (voraussichtlich)",
    "137": "Belegdatum",
    "140": "Zahlungsfälligkeit",
    "157": "Gültig ab",
    "171": "Referenzdatum",
    "191": "Lieferdatum (erwartet)",
    "194": "Beginn",
    "200": "Abholdatum",
    "206": "Ende",
    "263": "Abrechnungszeitraum",
    "273": "Gültigkeitszeitraum",
    "361": "Mindesthaltbarkeitsdatum",
}

# Rolle eines Beteiligten (NAD, DE 3035)
PARTIES = {
    "AB": "Einkaufsagent",
    "BT": "Rechnungsempfänger (abweichend)",
    "BY": "Käufer",
    "CA": "Frachtführer",
    "CN": "Warenempfänger",
    "CO": "Unternehmenszentrale",
    "CZ": "Versender",
    "DP": "Lieferanschrift",
    "FW": "Spediteur",
    "II": "Rechnungssteller",
    "IV": "Rechnungsempfänger",
    "MF": "Hersteller",
    "MR": "Nachrichtenempfänger",
    "MS": "Nachrichtenabsender",
    "OB": "Besteller",
    "PE": "Zahlungsempfänger",
    "PR": "Zahlungspflichtiger",
    "PW": "Abholadresse",
    "SE": "Verkäufer",
    "SF": "Versandort",
    "SN": "Filiale",
    "ST": "Warenempfänger (Lieferort)",
    "SU": "Lieferant",
    "UC": "Endempfänger",
    "UD": "Endkunde",
    "WH": "Lagerhalter",
}

# Art einer Referenz (RFF, DE 1153)
REFERENCES = {
    "AAA": "Auftragsbestätigungsnummer",
    "AAB": "Proformarechnungsnummer",
    "AAG": "Angebotsnummer",
    "AAJ": "Lieferauftragsnummer",
    "AAK": "Lieferavisnummer",
    "AAN": "Lieferplannummer",
    "AAS": "Transportdokumentnummer",
    "ACD": "Zusätzliche Referenznummer",
    "ACE": "Nummer des zugehörigen Dokuments",
    "ADE": "Kontonummer",
    "AHP": "Steuernummer",
    "API": "Zusätzliche Partnerkennung",
    "BM": "Konnossementnummer",
    "BO": "Rahmenbestellnummer",
    "CN": "Referenz des Frachtführers",
    "CO": "Bestellnummer des Käufers",
    "CR": "Kundenreferenz",
    "CT": "Vertragsnummer",
    "CU": "Referenz des Versenders",
    "DQ": "Lieferscheinnummer",
    "FC": "Steuernummer",
    "FF": "Referenz des Spediteurs",
    "GN": "Behördliche Referenz",
    "IA": "Lieferantennummer (intern)",
    "IT": "Kundennummer (intern)",
    "IV": "Rechnungsnummer",
    "LI": "Positionsreferenz",
    "ON": "Bestellnummer",
    "OP": "Ursprüngliche Bestellnummer",
    "PD": "Aktionsnummer",
    "PK": "Packlistennummer",
    "PL": "Preislistennummer",
    "POR": "Nummer der Bestellantwort",
    "PP": "Nummer der Bestelländerung",
    "PQ": "Zahlungsreferenz",
    "SRN": "Sendungsreferenz",
    "SS": "Referenz des Verkäufers",
    "UC": "Referenz des Endkunden",
    "VA": "USt-IdNr.",
    "VN": "Auftragsnummer des Lieferanten",
    "XA": "Handelsregisternummer",
    "ZZZ": "Referenz (bilateral vereinbart)",
}

# Funktion eines Ansprechpartners (CTA, DE 3139)
CONTACTS = {
    "AD": "Ansprechpartner Buchhaltung",
    "AP": "Ansprechpartner Kreditoren",
    "AR": "Ansprechpartner Debitoren",
    "CR": "Kundenbetreuung",
    "DL": "Ansprechpartner Lieferung",
    "GR": "Ansprechpartner Wareneingang",
    "IC": "Ansprechpartner für Auskünfte",
    "NT": "Zu benachrichtigen",
    "OC": "Ansprechpartner Bestellung",
    "PD": "Ansprechpartner Einkauf",
    "SR": "Vertriebsmitarbeiter",
    "SU": "Ansprechpartner Lieferant",
    "TR": "Ansprechpartner Transport",
    "WH": "Ansprechpartner Lager",
}

# Kommunikationskanal (COM, DE 3155)
CHANNELS = {
    "AH": "Web",
    "AL": "Mobil",
    "EI": "EDI",
    "EM": "E-Mail",
    "FX": "Fax",
    "MA": "Post",
    "TE": "Telefon",
    "TL": "Telex",
    "XF": "X.400",
}

# Gegenstand eines Freitexts (FTX, DE 4451)
TEXTS = {
    "AAA": "Warenbeschreibung",
    "AAB": "Zahlungsbedingungen",
    "AAI": "Allgemeine Information",
    "AAK": "Preiskonditionen",
    "AAR": "Lieferbedingungen",
    "ACB": "Zusätzliche Information",
    "CHG": "Änderungshinweis",
    "COI": "Bestellinformation",
    "CUR": "Anmerkung des Kunden",
    "DEL": "Lieferinformation",
    "DIN": "Lieferanweisung",
    "INV": "Rechnungshinweis",
    "LIN": "Positionstext",
    "MKS": "Zusätzliche Markierungen",
    "ORI": "Bestellhinweis",
    "PAC": "Verpackungshinweis",
    "PMD": "Zahlungsdetails",
    "PMT": "Zahlungsinformation",
    "PRD": "Produktinformation",
    "PUR": "Einkaufsinformation",
    "REG": "Rechtlicher Hinweis",
    "SIN": "Besondere Anweisung",
    "SUR": "Anmerkung des Lieferanten",
    "TRA": "Transportinformation",
    "TXD": "Steuerhinweis",
    "ZZZ": "Hinweis",
}

# Art einer Artikelnummer (LIN/PIA, DE 7143)
PRODUCT_IDS = {
    "BP": "Teilenummer des Käufers",
    "CG": "Warengruppe",
    "CV": "Zollartikelnummer",
    "EN": "EAN/GTIN",
    "HS": "Zolltarifnummer (HS)",
    "IB": "ISBN",
    "IN": "Artikelnummer des Käufers",
    "IS": "ISSN",
    "MF": "Artikelnummer des Herstellers",
    "MN": "Modellnummer",
    "NB": "Chargennummer",
    "PV": "Aktionsvariante",
    "SA": "Artikelnummer des Lieferanten",
    "SK": "Lagerartikelnummer (SKU)",
    "SN": "Seriennummer",
    "SRV": "GTIN",
    "ST": "Stilnummer",
    "UA": "Artikelnummer des Endkunden",
    "UP": "UPC",
    "VP": "Teilenummer des Lieferanten",
    "ZZZ": "Artikelnummer (bilateral vereinbart)",
}

# Zweck einer zusätzlichen Artikelkennung (PIA, DE 4347); nur Ersetzungen werden benannt
PRODUCT_ID_FUNCTIONS = {"3": "Ersatzartikel", "4": "ersetzter Artikel"}

# Was mit einer Position geschieht (LIN, DE 1229)
LINE_ACTIONS = {
    "1": "Hinzugefügt",
    "2": "Gelöscht",
    "3": "Geändert",
    "4": "Unverändert",
    "5": "Ohne Änderung angenommen",
    "6": "Mit Änderung angenommen",
    "7": "Nicht angenommen",
}

# Codierte Artikelbeschreibung nach EANCOM (IMD, DE 7009)
ITEM_TYPES = {
    "CU": "Verbrauchereinheit",
    "DU": "Versandeinheit",
    "RC": "Mehrwegbehälter",
    "TU": "Handelseinheit",
    "VQ": "Mengenvariabler Artikel",
}

# Art einer Menge (QTY, DE 6063)
QUANTITIES = {
    "1": "Einzelmenge",
    "11": "Teilmenge",
    "12": "Versandmenge",
    "21": "Bestellmenge",
    "46": "Gelieferte Menge",
    "47": "Berechnete Menge",
    "52": "Menge je Packung",
    "59": "Verbrauchereinheiten je Handelseinheit",
    "61": "Rücksendemenge",
    "83": "Rückstandsmenge",
    "113": "Zu liefernde Menge",
    "192": "Naturalrabattmenge",
    "194": "Angenommene Menge",
}

# Maßeinheiten (DE 6411, UN/ECE-Empfehlung 20)
UNITS = {
    "ANN": "Jahr(e)",
    "BE": "Bündel",
    "BG": "Beutel",
    "BO": "Flasche",
    "BX": "Schachtel",
    "C62": "Stück",
    "CA": "Dose",
    "CEN": "Hundert",
    "CLT": "cl",
    "CMT": "cm",
    "CS": "Kiste",
    "CT": "Karton",
    "DAY": "Tag(e)",
    "DMQ": "dm³",
    "DR": "Fass",
    "DZN": "Dutzend",
    "EA": "Stück",
    "GRM": "g",
    "H87": "Stück",
    "HLT": "hl",
    "HUR": "Std.",
    "KGM": "kg",
    "KMT": "km",
    "KWH": "kWh",
    "LM": "lfd. m",
    "LTR": "l",
    "MGM": "mg",
    "MIL": "Tausend",
    "MIN": "Min.",
    "MLT": "ml",
    "MMT": "mm",
    "MON": "Monat(e)",
    "MTK": "m²",
    "MTQ": "m³",
    "MTR": "m",
    "NAR": "Stück",
    "NMP": "Packungen",
    "NPR": "Paar",
    "NRL": "Rollen",
    "PA": "Päckchen",
    "PCE": "Stück",
    "PF": "Palette",
    "PK": "Packung",
    "PR": "Paar",
    "RO": "Rolle",
    "SA": "Sack",
    "SET": "Set",
    "ST": "Blatt",
    "TNE": "t",
    "TU": "Tube",
    "WEE": "Woche(n)",
}

# Art eines Preises (PRI, DE 5125)
PRICES = {
    "AAA": "Nettopreis",
    "AAB": "Bruttopreis",
    "AAE": "Informationspreis (inkl. Steuern)",
    "AAF": "Informationspreis (ohne Steuern)",
    "CAL": "Kalkulationspreis",
    "INF": "Informationspreis",
    "INV": "Rechnungspreis",
}

# Preisherkunft (PRI, DE 5375) und Preisangabe (PRI, DE 5387)
PRICE_TYPES = {"CA": "Katalogpreis", "CT": "Vertragspreis"}
PRICE_SPECS = {
    "PRP": "Aktionspreis",
    "RTP": "Einzelhandelspreis",
    "SRP": "Unverbindliche Preisempfehlung",
}

# Art eines Geldbetrags (MOA, DE 5025)
AMOUNTS = {
    "8": "Zu-/Abschlagsbetrag",
    "9": "Zahlbetrag",
    "23": "Zuschlagsbetrag",
    "25": "Bemessungsgrundlage für Zu-/Abschlag",
    "39": "Rechnungsgesamtbetrag",
    "66": "Warenwert der Position",
    "77": "Rechnungsbetrag",
    "79": "Summe der Positionsbeträge",
    "86": "Gesamtbetrag",
    "113": "Vorauszahlung",
    "124": "Steuerbetrag",
    "125": "Steuerpflichtiger Betrag",
    "128": "Gesamtbetrag",
    "129": "Skontofähiger Betrag",
    "131": "Summe der Zu-/Abschläge",
    "146": "Stückpreis",
    "150": "Umsatzsteuerbetrag",
    "176": "Summe der Steuern und Abgaben",
    "203": "Positionsbetrag",
    "204": "Abschlagsbetrag",
    "259": "Summe der Zuschläge",
    "260": "Summe der Abschläge",
    "402": "Verkaufswert gesamt",
}

# Art einer Prozentangabe (PCD, DE 5245)
PERCENTAGES = {
    "1": "Abschlag",
    "2": "Zuschlag",
    "3": "Zu-/Abschlag",
    "7": "Anteil am Rechnungsbetrag",
    "12": "Nachlass",
    "15": "Vertragsstrafe",
}

# Steuerart (TAX, DE 5153) und Steuerkategorie (TAX, DE 5305)
TAX_TYPES = {
    "ENV": "Umweltabgabe",
    "EXC": "Verbrauchsteuer",
    "GST": "Waren- und Dienstleistungssteuer",
    "VAT": "Umsatzsteuer",
}
TAX_CATEGORIES = {
    "AA": "ermäßigter Satz",
    "AE": "Umkehrung der Steuerschuld",
    "E": "steuerbefreit",
    "G": "steuerfreie Ausfuhr",
    "H": "erhöhter Satz",
    "K": "innergemeinschaftliche Lieferung",
    "O": "nicht steuerbar",
    "S": "Normalsatz",
    "Z": "Nullsatz",
}

# Zu- oder Abschlag (ALC, DE 5463) und sein Grund (ALC, DE 7161)
ALLOWANCE_KINDS = {"A": "Abschlag", "C": "Zuschlag"}
SERVICES = {
    "AA": "Werbekostenzuschuss",
    "ABL": "Zusatzverpackung",
    "DI": "Rabatt",
    "FC": "Frachtkosten",
    "HD": "Handling",
    "IN": "Versicherung",
    "PC": "Verpackung",
    "RAA": "Rückvergütung",
    "TD": "Handelsrabatt",
}

# Zahlungsbedingungen (PAT): Art (DE 4279), Bezugsdatum (DE 2475),
# Verhältnis zum Bezugsdatum (DE 2009), Zeiteinheit (DE 2151, Einzahl/Mehrzahl)
PAYMENT_TERMS = {
    "1": "Zahlungsbedingung",
    "3": "Zahlung zum festen Termin",
    "20": "Verzugsregelung",
    "21": "Ratenzahlung",
    "22": "Skonto",
}
TIME_REFERENCES = {
    "1": "Bestelldatum",
    "5": "Rechnungsdatum",
    "9": "Rechnungseingang",
    "21": "Wareneingang",
    "29": "Lieferdatum",
}
TIME_RELATIONS = {"1": "zum", "2": "vor", "3": "nach"}
PERIODS = {
    "CD": ("Kalendertag", "Kalendertage"),
    "D": ("Tag", "Tage"),
    "M": ("Monat", "Monate"),
    "W": ("Woche", "Wochen"),
    "WD": ("Arbeitstag", "Arbeitstage"),
    "Y": ("Jahr", "Jahre"),
}

# Lieferbedingungen (TOD): Funktion (DE 4055) und Incoterms (DE 4053)
DELIVERY_FUNCTIONS = {
    "1": "Preisbedingung",
    "2": "Versandbedingung",
    "3": "Preis- und Versandbedingung",
    "4": "Abholung durch den Kunden",
    "5": "Transportbedingung",
    "6": "Lieferbedingung",
}
INCOTERMS = {
    "CFR": "Kosten und Fracht",
    "CIF": "Kosten, Versicherung und Fracht",
    "CIP": "frachtfrei versichert",
    "CPT": "frachtfrei",
    "DAP": "geliefert benannter Ort",
    "DAT": "geliefert Terminal",
    "DDP": "geliefert verzollt",
    "DDU": "geliefert unverzollt",
    "DPU": "geliefert benannter Ort entladen",
    "EXW": "ab Werk",
    "FAS": "frei Längsseite Schiff",
    "FCA": "frei Frachtführer",
    "FOB": "frei an Bord",
}

# Transport (TDT): Abschnitt (DE 8051) und Verkehrsart (DE 8067, UN/ECE-Empfehlung 19)
TRANSPORT_STAGES = {"10": "Vorlauf", "20": "Hauptlauf", "30": "Nachlauf"}
TRANSPORT_MODES = {
    "1": "Seeverkehr",
    "2": "Schienenverkehr",
    "3": "Straßenverkehr",
    "4": "Luftverkehr",
    "5": "Postsendung",
    "6": "Kombinierter Verkehr",
    "8": "Binnenschifffahrt",
    "10": "Seeverkehr",
    "20": "Schienenverkehr",
    "30": "Straßenverkehr",
    "40": "Luftverkehr",
    "50": "Postsendung",
    "60": "Kombinierter Verkehr",
    "80": "Binnenschifffahrt",
}

# Art eines Packstücks (PAC, DE 7065)
PACKAGES = {
    "08": "Einwegpalette",
    "09": "Mehrwegpalette",
    "200": "Halbpalette",
    "201": "Europalette",
    "BE": "Bündel",
    "BG": "Beutel",
    "BO": "Flasche",
    "BX": "Schachtel",
    "CA": "Dose",
    "CR": "Verschlag",
    "CS": "Kiste",
    "CT": "Karton",
    "DR": "Fass",
    "PA": "Päckchen",
    "PK": "Paket",
    "PX": "Palette",
    "RO": "Rolle",
    "SA": "Sack",
    "TU": "Tube",
}

# Gemessene Größe (MEA, DE 6313)
MEASUREMENTS = {
    "AAA": "Nettogewicht je Einheit",
    "AAB": "Bruttogewicht je Einheit",
    "AAC": "Nettogewicht gesamt",
    "AAD": "Bruttogewicht gesamt",
    "AAW": "Bruttovolumen",
    "ABJ": "Volumen",
    "G": "Bruttogewicht",
    "HT": "Höhe",
    "LN": "Länge",
    "WD": "Breite",
}

# Bedeutung eines Orts (LOC, DE 3227)
LOCATIONS = {
    "1": "Ort der Lieferbedingung",
    "5": "Abgangsort",
    "7": "Lieferort",
    "8": "Bestimmungsort",
    "9": "Ladeort",
    "11": "Entladeort",
    "18": "Lager",
    "19": "Werk",
    "27": "Ursprungsland",
    "28": "Bestimmungsland",
    "35": "Ausfuhrland",
    "162": "Verkaufsort",
}

# Verbindlichkeit einer Liefereinteilung (SCC, DE 4017)
SCHEDULES = {"1": "fest", "4": "Planung"}

# Kontrollwerte (CNT, DE 6069)
CONTROLS = {"1": "Summe der Mengen", "2": "Anzahl der Positionen"}

# Länder (ISO 3166-1 alpha-2), Auswahl
COUNTRIES = {
    "AT": "Österreich",
    "BE": "Belgien",
    "BG": "Bulgarien",
    "CA": "Kanada",
    "CH": "Schweiz",
    "CN": "China",
    "CZ": "Tschechien",
    "DE": "Deutschland",
    "DK": "Dänemark",
    "EE": "Estland",
    "ES": "Spanien",
    "FI": "Finnland",
    "FR": "Frankreich",
    "GB": "Vereinigtes Königreich",
    "GR": "Griechenland",
    "HR": "Kroatien",
    "HU": "Ungarn",
    "IE": "Irland",
    "IT": "Italien",
    "JP": "Japan",
    "LI": "Liechtenstein",
    "LT": "Litauen",
    "LU": "Luxemburg",
    "LV": "Lettland",
    "NL": "Niederlande",
    "NO": "Norwegen",
    "PL": "Polen",
    "PT": "Portugal",
    "RO": "Rumänien",
    "SE": "Schweden",
    "SI": "Slowenien",
    "SK": "Slowakei",
    "TR": "Türkei",
    "US": "USA",
}
