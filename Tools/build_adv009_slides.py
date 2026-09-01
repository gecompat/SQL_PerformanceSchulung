#!/usr/bin/env python3
"""ADV-009: Vertiefungsfolien in das aktive Foliendeck uebernehmen.

Das Werkzeug arbeitet ausschliesslich mit der Python-Standardbibliothek und
klont eine bestehende Inhaltsfolie des Decks als Vorlage. Aus der Vorlage
entstehen zehn neue Folien fuer die Lernziele ``LO-M03-07`` und ``LO-M03-08``.

Eigenschaften:

* deterministisch - wiederholte Laeufe auf demselben Ausgangsdeck erzeugen
  byteidentische Ergebnisse und damit denselben SHA-256-Wert;
* idempotenzgesichert - ein bereits erweitertes Deck wird nicht erneut
  erweitert, sondern mit einer Fehlermeldung abgewiesen;
* additiv - bestehende Folien werden nur an einer Stelle veraendert: der
  Nenner der Fussnotenpaginierung wird von 84 auf 94 gesetzt.

Aufruf::

    python Tools/build_adv009_slides.py [--check]

``--check`` prueft nur, ob das Deck bereits erweitert ist.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
from pathlib import Path
import re
import shutil
import sys
import uuid
import xml.etree.ElementTree as ET
import zipfile

ROOT = Path(__file__).resolve().parents[1]
DECK = (
    ROOT
    / "Presentations"
    / "Performance_Schulung_Chat_2026-07-23_2146_SQL_Server_Performance_Grundlagen.pptx"
)

P_NS = "http://schemas.openxmlformats.org/presentationml/2006/main"
A_NS = "http://schemas.openxmlformats.org/drawingml/2006/main"
R_NS = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
A16_NS = "http://schemas.microsoft.com/office/drawing/2014/main"
P = f"{{{P_NS}}}"
A = f"{{{A_NS}}}"
A16 = f"{{{A16_NS}}}"

TEMPLATE_SLIDE = 32
"""Vorlagenfolie der Familie ``lead`` + ``points`` mit genau vier Aufzaehlungen."""

BASE_SLIDE_COUNT = 84
NEW_SLIDE_COUNT = 10
TOTAL_SLIDE_COUNT = BASE_SLIDE_COUNT + NEW_SLIDE_COUNT

MODULE_LABEL = "3 · QUERY PATTERNS · VERTIEFUNG"
FOOTER_LEFT = "SQL Server Performance Grundlagen"
CLASSIFICATION_NOTE = (
    "Kennzeichnung: Dokumentierte Aussagen beruhen auf "
    "Microsoft-Learn-Primärdokumentation. Empirische Werte sind als solche zu "
    "messen und nicht als universelle Schwelle zu verwenden."
)
XML_DECLARATION = "<?xml version='1.0' encoding='UTF-8' standalone='yes'?>\n"
NEW_ENTRY_DATE = (2026, 7, 24, 0, 0, 0)
GUID_NAMESPACE = uuid.UUID("6ba7b811-9dad-11d1-80b4-00c04fd430c8")

SLIDES = [
    {
        "slide_id": "SLD-M03-101",
        "title": "Anwendung langsam, Werkzeug schnell ist eine Beobachtung, keine Ursache",
        "lead": (
            "Die Differenz zwischen zwei Clients ist ein Evidenzproblem und "
            "erfordert eine mehrdimensionale Kontextdiagnose."
        ),
        "points": [
            "gleicher Querytext bedeutet nicht gleiche Ausführungsbedingungen",
            "zu prüfen: Datenbankkontext, SET-Optionen, Parameterwerte, Planidentität",
            "Ein-Ursachen-Hypothese erst nach Widerlegung der übrigen Dimensionen",
            "zwei dokumentierte Sessionprofile statt Vermutungen über Clientdefaults",
        ],
        "note": (
            "Die verbreitete Formulierung „in der Anwendung langsam, in SSMS "
            "schnell“ beschreibt eine Beobachtung, keine Ursache. Wir benennen "
            "bewusst keine Clientdefaults, weil Treiber- und Werkzeugversionen "
            "unterschiedliche Vorgaben setzen. Stattdessen arbeiten wir mit zwei "
            "explizit gesetzten, neutralen Sessionprofilen. Das Ziel dieser Folie "
            "ist die Haltung: erst Kontext erheben, dann Hypothesen bilden. Die "
            "Demo QRY-013 widerlegt später genau eine solche voreilige Hypothese."
        ),
        "claims": "ADV-CLM-014",
        "sources": "SRC-001, SRC-027, SRC-046",
        "demo": "QRY-013",
    },
    {
        "slide_id": "SLD-M03-102",
        "title": "Cachekontext und SET-Optionen erzeugen zusätzliche Cacheeinträge",
        "lead": (
            "Cachekontext und SET-Optionen können zusätzliche Cacheeinträge für "
            "dasselbe Objekt erzeugen. Das fachliche Ergebnis bleibt identisch; "
            "unterschiedlich ist der Weg dorthin."
        ),
        "points": [
            "Cacheschlüssel umfasst mehr als den Anweisungstext",
            "abweichende SET-Optionen ergeben getrennte Cacheeinträge desselben Objekts",
            "getrennte Einträge bedeuten getrennte Kompilierungen mit eigenen Werten",
            "sichtbar über sys.dm_exec_plan_attributes, Attribut set_options",
        ],
        "note": (
            "Sichtbar wird das über sys.dm_exec_plan_attributes, insbesondere über "
            "das Attribut set_options, ausgewertet für ein einzelnes Demoobjekt. "
            "Wichtig ist die Reihenfolge der Aussagen: Der zusätzliche Cacheeintrag "
            "ist eine gesicherte Beobachtung, ein daraus abgeleiteter "
            "Laufzeitunterschied ist es nicht. In QRY-013 unterscheiden sich die "
            "beiden Profile ausschließlich in ARITHABORT; das Ergebnis bleibt "
            "bitgleich, die Anzahl der Cacheeinträge steigt von eins auf zwei. Eine "
            "pauschale Empfehlung zu einer einzelnen SET-Option leiten wir daraus "
            "nicht ab."
        ),
        "claims": "ADV-CLM-013",
        "sources": "SRC-001, SRC-040, SRC-046",
        "demo": "QRY-013, OPT-007",
    },
    {
        "slide_id": "SLD-M03-103",
        "title": "Parameter Sensitivity folgt der Planwiederverwendung",
        "lead": (
            "Ein wiederverwendeter Plan wurde für einen konkreten Parameterwert "
            "kompiliert. Trifft er auf eine andere Verteilung, ändert sich die "
            "Arbeitsmenge, nicht das Ergebnis."
        ),
        "points": [
            "Plan entsteht für den kompilierten Wert und wird danach wiederverwendet",
            "andere Verteilung verändert die Arbeitsmenge, nicht das Ergebnis",
            "Effekt tritt auch bei vollständig identischem Sessionkontext auf",
            "Parameterdimension ist unabhängig von der Kontextdimension nachweisbar",
        ],
        "note": (
            "Diese Folie ist das Gegengewicht zur vorherigen. In der Demo halten wir "
            "das Sessionprofil konstant und ändern nur den Parameterwert von einem "
            "seltenen auf einen häufigen Wert. Die logischen Lesevorgänge steigen "
            "deutlich, obwohl kein zusätzlicher Cacheeintrag entsteht. Genau hier "
            "bricht die Hypothese „es liegt an den SET-Optionen“ zusammen. Bleibt "
            "die Arbeitsmenge in einer Umgebung wider Erwarten gleich, meldet die "
            "Demo WARN_EMPIRICAL_VARIANCE statt eine Verschlechterung zu behaupten."
        ),
        "claims": "ADV-CLM-015",
        "sources": "SRC-007, SRC-047",
        "demo": "QRY-013, OPT-008",
    },
    {
        "slide_id": "SLD-M03-104",
        "title": "Parameter, Variablen, Literale und Recompile liefern unterschiedliche Information",
        "lead": (
            "Die vier Varianten sind keine Rangfolge, sondern ein Tauschverhältnis "
            "zwischen Planqualität, Wiederverwendung und Kompilierarbeit."
        ),
        "points": [
            "Parameter: Schätzung anhand des kompilierten Werts, Plan wird wiederverwendet",
            "lokale Variable: kein bekannter Wert zur Kompilierzeit, Schätzung ohne Wertbezug",
            "Literal: Wert zur Kompilierzeit bekannt, dafür eigener Cacheeintrag je Wert",
            "OPTION (RECOMPILE): Wert bekannt, dafür Kompilierarbeit je Ausführung",
        ],
        "note": (
            "Die vier Varianten sind keine Rangfolge, sondern ein Tauschverhältnis "
            "zwischen Planqualität, Wiederverwendung und Kompilierarbeit. Wer die "
            "Diagnose aus SLD-M03-101 ernst nimmt, muss wissen, welche Variante im "
            "Verdachtsfall tatsächlich vorliegt: Eine Anwendung sendet häufig "
            "parametrisierte Aufrufe, ein Werkzeugfenster häufig Literale. Damit "
            "unterscheiden sich beide bereits in der Information, die dem Optimierer "
            "zur Verfügung steht – unabhängig von jeder SET-Option. Die belastbare "
            "Bewertung von OPTION (RECOMPILE) erfolgt in QRY-004 über mehrere "
            "Ausführungen, nicht über eine einzelne schnelle Messung."
        ),
        "claims": "ADV-CLM-016",
        "sources": "SRC-001, SRC-007, SRC-045, SRC-046",
        "demo": "QRY-004, OPT-008",
    },
    {
        "slide_id": "SLD-M03-105",
        "title": "Die Diagnose ist erst abgeschlossen, wenn jede Dimension belegt oder ausgeschlossen ist",
        "lead": (
            "Erst wenn alle Proben dieselbe Ergebnischecksumme liefern, vergleichen "
            "wir Laufzeiten und nicht unterschiedliche Arbeit."
        ),
        "points": [
            "Erheben: Datenbankkontext, wirksame SET-Optionen, Parameterwerte, Planidentität",
            "Trennen: Kontextdimension und Parameterdimension getrennt messen",
            "Angleichen: genau eine Dimension verändern und erneut messen",
            "Bewerten: Ergebnisgleichheit sichern, bevor Laufzeiten verglichen werden",
        ],
        "note": (
            "Diese Folie leitet unmittelbar in QRY-013 über. Der Ablauf der Demo ist "
            "die Evidenzkette dieser Folie: Baseline mit Profil A, Demonstration mit "
            "Profil B, Observation mit Profil A und anderem Parameterwert, Mitigation "
            "mit Angleichung genau einer Dimension, Comparison mit erneuter Messung. "
            "Entscheidend ist die letzte Zeile: Wir vergleichen erst dann Laufzeiten, "
            "wenn alle Proben dieselbe Ergebnischecksumme liefern. Andernfalls "
            "vergleichen wir unterschiedliche Arbeiten und nicht unterschiedliche "
            "Bedingungen."
        ),
        "claims": "ADV-CLM-013, ADV-CLM-014, ADV-CLM-015, ADV-CLM-016",
        "sources": "SRC-001, SRC-027, SRC-040, SRC-046",
        "demo": "QRY-013",
    },
    {
        "slide_id": "SLD-M03-111",
        "title": "Ein statischer Querytext bindet sich an eine einzige Planform",
        "lead": (
            "Optionale Prädikate erzeugen eine Planform, die für alle Selektivitäten "
            "gleichermaßen gilt – das ist kein Fehler, sondern die Folge bewusster "
            "Wiederverwendung."
        ),
        "points": [
            "optionale Prädikate der Form @Wert IS NULL OR Spalte = @Wert sind nicht sargfähig",
            "eine Planform muss jede Filterkombination bedienen",
            "Wiederverwendung unabhängig davon, ob ein Filter 20 oder 20 000 Zeilen trifft",
            "genau ein Cacheeintrag, dafür keine Anpassung an die Selektivität",
        ],
        "note": (
            "Wichtig ist die Wortwahl: Wir nennen das Catch-all-Muster nicht falsch. "
            "Es ist wartbar, es liefert korrekte Ergebnisse und es erzeugt genau "
            "einen Cacheeintrag. Der Preis ist die fehlende Anpassung an die "
            "Selektivität. In der Demo QRY-004 messen wir das an drei Kombinationen "
            "mit 20, 19 980 und 4 000 Trefferzeilen; die Zahl der Planformen bleibt "
            "dabei bei eins. Erst diese Messung macht die anschließende "
            "Strategiediskussion belastbar."
        ),
        "claims": "–",
        "sources": "SRC-001, SRC-045, SRC-049",
        "demo": "QRY-004",
    },
    {
        "slide_id": "SLD-M03-112",
        "title": "OPTION (RECOMPILE) ist ein Tauschgeschäft, keine pauschale Lösung",
        "lead": (
            "OPTION (RECOMPILE) ermöglicht laufzeitnahe Optimierung und gibt dafür "
            "die Planwiederverwendung auf."
        ),
        "points": [
            "der konkrete Wert ist bei jeder Ausführung bekannt, unbenutzte Zweige entfallen",
            "dafür entsteht bei jeder Ausführung Kompilierarbeit",
            "Nutzen wächst mit der Schwankung der Selektivität, Kosten mit der Frequenz",
            "Bewertung erfordert mehrere Ausführungen, nicht eine einzelne Messung",
        ],
        "note": (
            "Diese Folie korrigiert zwei gegenläufige Vereinfachungen: „Recompile ist "
            "die Lösung“ und „Recompile ist zu teuer“. Beide sind ohne Kontext "
            "falsch. In QRY-004 prüfen wir den möglichen Nutzen für den selektiven "
            "Wert und danach den Preis anhand von 25 ungefilterten Wiederholungen je "
            "Variante bei identischer Arbeitsmenge. Die validierte "
            "2019/2022/2025-Matrix erzeugte für den selektiven Wert keinen "
            "Read-Vorteil und meldete deshalb wahrheitsgemäß "
            "WARN_EMPIRICAL_VARIANCE. Die Demo behauptet weder eine Verbesserung "
            "noch eine Verschlechterung, die sich nicht von der Messstreuung trennen "
            "lässt."
        ),
        "claims": "ADV-CLM-017",
        "sources": "SRC-001, SRC-045",
        "demo": "QRY-004",
    },
    {
        "slide_id": "SLD-M03-113",
        "title": "Dynamische Suchbedingungen entstehen aus einer Positivliste",
        "lead": (
            "Prädikatsbausteine stammen aus einer festen Positivliste; Werte werden "
            "gebunden, nicht in den Statementtext konkateniert."
        ),
        "points": [
            "Prädikatsbausteine ausschließlich aus einer festen Positivliste im Code",
            "Werte über sys.sp_executesql binden, nie in den Text konkatenieren",
            "Objektbezeichner mit QUOTENAME behandeln, nie roh einsetzen",
            "unbekannte Filterdefinition führt zu kontrolliertem Abbruch",
        ],
        "note": (
            "Sicherheit ist hier kein Nebenthema, sondern ein eigenständiges "
            "Abnahmekriterium. Die Demo prüft zwei Dinge unabhängig voneinander: "
            "Erstens enthält kein zwischengespeicherter Statementtext einen "
            "Filterwert – das belegt die Parameterbindung. Zweitens wird eine "
            "Filterdefinition außerhalb der Positivliste abgewiesen. Wer stattdessen "
            "Benutzereingaben in den Text konkateniert, baut eine Injektionsfläche "
            "und zusätzlich eine unbegrenzte Zahl von Statementformen. Beide Probleme "
            "entstehen aus derselben Entscheidung."
        ),
        "claims": "ADV-CLM-018",
        "sources": "SRC-001, SRC-045",
        "demo": "QRY-004",
    },
    {
        "slide_id": "SLD-M03-114",
        "title": "Sicher parameterisiertes dynamisches SQL bleibt wiederverwendbar",
        "lead": (
            "Die Zahl der Statementformen folgt der Zahl der Filterformen, nicht der "
            "Zahl der Aufrufe. Sie ist zu messen, nicht anzunehmen."
        ),
        "points": [
            "gleiche Filterform mit unterschiedlichen Werten nutzt dieselbe Statementform",
            "normalisierte Prädikatsreihenfolge verhindert unnötige Formvarianten",
            "drei Ausführungen in QRY-004 ergeben genau zwei Statementformen",
            "teuer wird dynamisches SQL durch unkontrollierte Textvarianten",
        ],
        "note": (
            "In der Demo führen drei Ausführungen zu genau zwei Statementformen: "
            "zweimal Filter auf die Kategorie mit unterschiedlichen Werten, einmal "
            "Filter auf den Status. Die Prädikatsreihenfolge wird im Code "
            "normalisiert, damit Kategorie und Status in beliebiger Angabereihenfolge "
            "denselben Text ergeben. Ohne diese Normalisierung wächst die Zahl der "
            "Formen kombinatorisch. Das ist der Punkt, an dem dynamisches SQL "
            "tatsächlich teuer wird – nicht durch die Technik selbst, sondern durch "
            "unkontrollierte Textvarianten."
        ),
        "claims": "ADV-CLM-018",
        "sources": "SRC-001, SRC-045",
        "demo": "QRY-004",
    },
    {
        "slide_id": "SLD-M03-115",
        "title": "Strategie auswählen statt Rangfolge lernen",
        "lead": (
            "Die Auswahl folgt Verteilung, Ausführungsfrequenz, Sicherheit und "
            "Wartbarkeit; alle Strategien müssen ergebnisgleich sein."
        ),
        "points": [
            "stabile Selektivität und hohe Frequenz: statischer Querytext mit Wiederverwendung",
            "stark schwankende Selektivität und geringe Frequenz: OPTION (RECOMPILE)",
            "viele Filterkombinationen mit begrenzten Formen: sicheres dynamisches SQL",
            "Ergebnisgleichheit ist Voraussetzung des Laufzeitvergleichs, nicht dessen Resultat",
        ],
        "note": (
            "Diese Folie leitet in QRY-004 über und schließt den Bogen. Die Demo "
            "vergleicht die drei Strategien unter identischer Datenverteilung und "
            "prüft für jede Filterkombination Zeilenzahl und Ergebnischecksumme, "
            "bevor sie über Lesevorgänge oder CPU spricht. Der Ausblick gehört "
            "ausdrücklich in die folgenden Demos: Parameter Sensitive Plan "
            "Optimization in OPT-009 und Optional Parameter Plan Optimization in "
            "OPT-010 lösen jeweils eine eigene Problemform und sind an Version, "
            "Compatibility Level und Eligibility gebunden. Sie ersetzen keine der "
            "drei hier verglichenen Strategien."
        ),
        "claims": "ADV-CLM-017, ADV-CLM-018",
        "sources": "SRC-001, SRC-007, SRC-045, SRC-049",
        "demo": "QRY-004",
    },
]


def register_namespaces() -> None:
    ET.register_namespace("p", P_NS)
    ET.register_namespace("a", A_NS)
    ET.register_namespace("r", R_NS)
    ET.register_namespace("a16", A16_NS)


def stable_guid(seed: str) -> str:
    return "{" + str(uuid.uuid5(GUID_NAMESPACE, seed)).upper() + "}"


def shape_by_name(tree: ET.Element, name: str) -> ET.Element:
    for shape in tree.findall(f"{P}sp"):
        cnv = shape.find(f"{P}nvSpPr/{P}cNvPr")
        if cnv is not None and cnv.get("name") == name:
            return shape
    raise KeyError(f"shape not found: {name}")


def set_paragraph_texts(shape: ET.Element, texts: list[str]) -> None:
    paragraphs = shape.findall(f"{P}txBody/{A}p")
    if len(paragraphs) != len(texts):
        raise ValueError(
            f"paragraph count mismatch: template={len(paragraphs)} content={len(texts)}"
        )
    for paragraph, text in zip(paragraphs, texts):
        runs = paragraph.findall(f"{A}r")
        if not runs:
            raise ValueError("template paragraph without run")
        for extra in runs[1:]:
            paragraph.remove(extra)
        text_element = runs[0].find(f"{A}t")
        if text_element is None:
            raise ValueError("template run without text element")
        text_element.text = text


def build_slide_xml(template: bytes, spec: dict, display_number: int) -> bytes:
    root = ET.fromstring(template)
    tree = root.find(f"{P}cSld/{P}spTree")
    if tree is None:
        raise ValueError("template slide has no shape tree")

    set_paragraph_texts(shape_by_name(tree, "module-label"), [MODULE_LABEL])
    set_paragraph_texts(shape_by_name(tree, "slide-title"), [spec["title"]])
    set_paragraph_texts(shape_by_name(tree, "footer-left"), [FOOTER_LEFT])
    set_paragraph_texts(
        shape_by_name(tree, "footer-page"), [f"{display_number} / {TOTAL_SLIDE_COUNT}"]
    )
    set_paragraph_texts(shape_by_name(tree, "lead"), [spec["lead"]])
    set_paragraph_texts(shape_by_name(tree, "points"), spec["points"])

    shape_id = 2
    for shape in tree.findall(f"{P}sp"):
        cnv = shape.find(f"{P}nvSpPr/{P}cNvPr")
        cnv.set("id", str(shape_id))
        for creation_id in cnv.iter(f"{A16}creationId"):
            creation_id.set("id", stable_guid(f"{spec['slide_id']}/{cnv.get('name')}"))
        shape_id += 1

    return (XML_DECLARATION + ET.tostring(root, encoding="unicode")).encode("utf-8")


def build_notes_xml(template: bytes, spec: dict) -> bytes:
    root = ET.fromstring(template)
    tree = root.find(f"{P}cSld/{P}spTree")
    if tree is None:
        raise ValueError("template notes slide has no shape tree")
    shape = shape_by_name(tree, "Notes Placeholder 2")
    body = shape.find(f"{P}txBody")
    paragraphs = body.findall(f"{A}p")
    if not paragraphs:
        raise ValueError("template notes slide has no paragraph")
    prototype = copy.deepcopy(paragraphs[0])
    for paragraph in paragraphs:
        body.remove(paragraph)

    note_paragraphs = [
        f"[SLIDE-ID: {spec['slide_id']}] {spec['note']}",
        (
            f"Quellen: {spec['sources']} · Demo: {spec['demo']} · "
            f"Claims: {spec['claims']} · Tiefe: VERTIEFUNG"
        ),
        CLASSIFICATION_NOTE,
    ]
    for text in note_paragraphs:
        paragraph = copy.deepcopy(prototype)
        runs = paragraph.findall(f"{A}r")
        for extra in runs[1:]:
            paragraph.remove(extra)
        runs[0].find(f"{A}t").text = text
        body.append(paragraph)

    return (XML_DECLARATION + ET.tostring(root, encoding="unicode")).encode("utf-8")


def slide_rels_xml(slide_number: int) -> bytes:
    layout_id = "R" + hashlib.sha256(f"layout/{slide_number}".encode()).hexdigest()[:16]
    notes_id = "R" + hashlib.sha256(f"notes/{slide_number}".encode()).hexdigest()[:16]
    return (
        '<?xml version="1.0" encoding="utf-8"?>'
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
        '<Relationship Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideLayout"'
        f' Target="/ppt/slideLayouts/slideLayout1.xml" Id="{layout_id}" />'
        '<Relationship Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/notesSlide"'
        f' Target="/ppt/notesSlides/notesSlide{slide_number}.xml" Id="{notes_id}" />'
        "</Relationships>"
    ).encode("utf-8")


def notes_rels_xml(slide_number: int) -> bytes:
    slide_id = "R" + hashlib.sha256(f"slide/{slide_number}".encode()).hexdigest()[:16]
    master_id = "R" + hashlib.sha256(f"notesmaster/{slide_number}".encode()).hexdigest()[:16]
    return (
        '<?xml version="1.0" encoding="utf-8"?>'
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
        '<Relationship Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slide"'
        f' Target="/ppt/slides/slide{slide_number}.xml" Id="{slide_id}" />'
        '<Relationship Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/notesMaster"'
        f' Target="/ppt/notesMasters/notesMaster1.xml" Id="{master_id}" />'
        "</Relationships>"
    ).encode("utf-8")


def patch_content_types(data: bytes) -> bytes:
    text = data.decode("utf-8")
    additions = []
    for offset in range(NEW_SLIDE_COUNT):
        number = BASE_SLIDE_COUNT + 1 + offset
        additions.append(
            f'<Override PartName="/ppt/slides/slide{number}.xml" ContentType='
            '"application/vnd.openxmlformats-officedocument.presentationml.slide+xml" />'
            f'<Override PartName="/ppt/notesSlides/notesSlide{number}.xml" ContentType='
            '"application/vnd.openxmlformats-officedocument.presentationml.notesSlide+xml" />'
        )
    return text.replace("</Types>", "".join(additions) + "</Types>").encode("utf-8")


def patch_presentation_rels(data: bytes, relationship_ids: list[str]) -> bytes:
    text = data.decode("utf-8")
    additions = []
    for offset, relationship_id in enumerate(relationship_ids):
        number = BASE_SLIDE_COUNT + 1 + offset
        additions.append(
            '<Relationship Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slide"'
            f' Target="/ppt/slides/slide{number}.xml" Id="{relationship_id}" />'
        )
    return text.replace(
        "</Relationships>", "".join(additions) + "</Relationships>"
    ).encode("utf-8")


def patch_presentation(data: bytes, relationship_ids: list[str]) -> bytes:
    text = data.decode("utf-8")
    marker = "<p:sldId "
    last = text.rindex(marker)
    additions = []
    for offset, relationship_id in enumerate(relationship_ids):
        additions.append(
            f'<p:sldId id="{340 + offset}" r:id="{relationship_id}"'
            ' xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" />'
        )
    return (text[:last] + "".join(additions) + text[last:]).encode("utf-8")


def patch_footer_denominator(data: bytes) -> bytes:
    text = data.decode("utf-8")
    patched = re.sub(
        r"(<a:t>\d+) / %d(</a:t>)" % BASE_SLIDE_COUNT,
        r"\1 / %d\2" % TOTAL_SLIDE_COUNT,
        text,
    )
    return patched.encode("utf-8")


def already_extended(deck: Path) -> bool:
    with zipfile.ZipFile(deck) as archive:
        return f"ppt/slides/slide{BASE_SLIDE_COUNT + 1}.xml" in set(archive.namelist())


def build(deck: Path) -> str:
    register_namespaces()
    with zipfile.ZipFile(deck) as archive:
        entries = [(info, archive.read(info)) for info in archive.infolist()]
        slide_template = archive.read(f"ppt/slides/slide{TEMPLATE_SLIDE}.xml")
        notes_template = archive.read(f"ppt/notesSlides/notesSlide{TEMPLATE_SLIDE}.xml")

    relationship_ids = [
        "R" + hashlib.sha256(f"presentation/{spec['slide_id']}".encode()).hexdigest()[:16]
        for spec in SLIDES
    ]

    new_parts: list[tuple[str, bytes]] = []
    for offset, spec in enumerate(SLIDES):
        number = BASE_SLIDE_COUNT + 1 + offset
        display = BASE_SLIDE_COUNT + offset
        new_parts.append(
            (f"ppt/slides/slide{number}.xml", build_slide_xml(slide_template, spec, display))
        )
        new_parts.append((f"ppt/slides/_rels/slide{number}.xml.rels", slide_rels_xml(number)))
        new_parts.append(
            (f"ppt/notesSlides/notesSlide{number}.xml", build_notes_xml(notes_template, spec))
        )
        new_parts.append(
            (f"ppt/notesSlides/_rels/notesSlide{number}.xml.rels", notes_rels_xml(number))
        )

    target = deck.with_suffix(".pptx.tmp")
    with zipfile.ZipFile(target, "w", zipfile.ZIP_DEFLATED) as output:
        for info, payload in entries:
            name = info.filename
            if name == "[Content_Types].xml":
                payload = patch_content_types(payload)
            elif name == "ppt/_rels/presentation.xml.rels":
                payload = patch_presentation_rels(payload, relationship_ids)
            elif name == "ppt/presentation.xml":
                payload = patch_presentation(payload, relationship_ids)
            elif re.fullmatch(r"ppt/slides/slide\d+\.xml", name):
                payload = patch_footer_denominator(payload)
            new_info = zipfile.ZipInfo(name, date_time=info.date_time)
            new_info.compress_type = zipfile.ZIP_DEFLATED
            new_info.external_attr = info.external_attr
            output.writestr(new_info, payload)
        for name, payload in new_parts:
            new_info = zipfile.ZipInfo(name, date_time=NEW_ENTRY_DATE)
            new_info.compress_type = zipfile.ZIP_DEFLATED
            output.writestr(new_info, payload)

    shutil.move(str(target), str(deck))
    return hashlib.sha256(deck.read_bytes()).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description="ADV-009 Vertiefungsfolien uebernehmen")
    parser.add_argument("--check", action="store_true", help="nur Zustand pruefen")
    arguments = parser.parse_args()

    if not DECK.is_file():
        print("build-adv009-slides: FAIL (deck missing)")
        return 1
    if already_extended(DECK):
        digest = hashlib.sha256(DECK.read_bytes()).hexdigest()
        print(f"build-adv009-slides: SKIP (deck already extended; SHA-256 {digest})")
        return 0 if arguments.check else 1
    if arguments.check:
        print("build-adv009-slides: PENDING (deck not yet extended)")
        return 0

    digest = build(DECK)
    print(
        f"build-adv009-slides: PASS ({NEW_SLIDE_COUNT} slides added, "
        f"{TOTAL_SLIDE_COUNT} total; SHA-256 {digest})"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
