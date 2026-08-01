#!/usr/bin/env python3
"""ADV-011: Vertiefungsfolien zur Optional Parameter Plan Optimization uebernehmen.

Das Werkzeug arbeitet ausschliesslich mit der Python-Standardbibliothek und
klont eine bestehende Inhaltsfolie des Decks als Vorlage. Aus der Vorlage
entstehen vier neue Folien fuer das Lernziel ``LO-M03-08``.

Eigenschaften:

* deterministisch - wiederholte Laeufe auf demselben Ausgangsdeck erzeugen
  byteidentische Ergebnisse und damit denselben SHA-256-Wert;
* idempotenzgesichert - ein bereits erweitertes Deck wird nicht erneut
  erweitert, sondern mit einer Fehlermeldung abgewiesen;
* additiv - bestehende Folien werden nur an einer Stelle veraendert: der
  Nenner der Fussnotenpaginierung wird von 98 auf 102 gesetzt.

Aufruf::

    python Tools/build_adv011_slides.py [--check]

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

BASE_SLIDE_COUNT = 98
NEW_SLIDE_COUNT = 4
TOTAL_SLIDE_COUNT = BASE_SLIDE_COUNT + NEW_SLIDE_COUNT
FIRST_SLIDE_ID = 354
"""Fortsetzung der ``p:sldId``-Nummerierung; ADV-010 endete bei 353."""

MODULE_LABEL = "3 · QUERY PATTERNS · VERTIEFUNG"
FOOTER_LEFT = "SQL Server Performance Grundlagen"
CLASSIFICATION_NOTE = (
    "Kennzeichnung: Dokumentierte Aussagen beruhen auf "
    "Microsoft-Learn-Primärdokumentation. Empirische Werte sind als solche zu "
    "messen und nicht als universelle Schwelle zu verwenden."
)
XML_DECLARATION = "<?xml version='1.0' encoding='UTF-8' standalone='yes'?>\n"
NEW_ENTRY_DATE = (2026, 7, 25, 0, 0, 0)
GUID_NAMESPACE = uuid.UUID("6ba7b811-9dad-11d1-80b4-00c04fd430c8")

SLIDES = [
    {
        "slide_id": "SLD-M03-131",
        "title": "Der belegte Parameter zahlt den offenen mit",
        "lead": (
            "Ein optionales Parameterprädikat erzwingt eine Planform, die für beide "
            "Parameterzustände gültig sein muss."
        ),
        "points": [
            "das Muster (Spalte = @p OR @p IS NULL) deckt zwei Parameterzustände in einem Querytext ab",
            "für den belegten Zustand wäre eine Suche gültig, für den offenen Zustand nicht",
            "es gibt deshalb keine Suchplanform, die für beide Zustände zugleich gültig wäre",
            "der belegte Aufruf trägt die Prüfbreite des offenen Aufrufs mit, unabhängig von der Reihenfolge",
        ],
        "note": (
            "Diese Folie trennt zwei Dinge, die im Alltag ständig vermischt werden. "
            "Bei OPT-009 ging es um Schiefe: dort existiert eine Suchplanform, sie "
            "passt nur nicht zu jedem Wert. Hier ist die Lage grundsätzlich anders. "
            "Die Demo OPT-010 arbeitet bewusst mit einer völlig gleichmäßigen "
            "Verteilung – 2 000 Agenten zu je genau 50 Zeilen –, damit niemand die "
            "Wirkung der Schiefe zuschreiben kann. Wir messen denselben Querytext in "
            "beiden Kompilierungsreihenfolgen und erhalten in beiden Fällen dieselbe "
            "Planform und dieselben Lesekosten für den belegten Parameter. Das ist "
            "der entscheidende Befund: Hier hilft kein günstiger Erstaufruf, weil es "
            "keine passende Planform gibt, die man treffen könnte."
        ),
        "claims": "–",
        "sources": "SRC-001, SRC-049",
        "demo": "OPT-010",
    },
    {
        "slide_id": "SLD-M03-132",
        "title": "Dispatcherplan mit optionalem Parameterprädikat",
        "lead": (
            "Optional Parameter Plan Optimization ersetzt die eine Planform durch "
            "einen Dispatcherplan mit einer Query Variant je NULL-Zustand."
        ),
        "points": [
            "der Dispatcherplan trägt je optionalem Prädikat ein Element OptionalParameterPredicate",
            "je Kombination der NULL-Zustände entsteht eine eigene Query Variant mit eigener QueryVariantID",
            "nach der Variantenauswahl wird das optionale Prädikat konstant gefaltet",
            "das Verfahren verändert die Kosten, niemals das Ergebnis",
        ],
        "note": (
            "Technisch sitzt das Verfahren auf derselben Infrastruktur wie die "
            "parametersensitive Planoptimierung: ein Dispatcherplan als Weiche, "
            "dahinter mehrere Varianten als vorbereitete Anweisungen. Der "
            "Unterschied steckt im Prädikatelement. Bei OPT-009 steht dort "
            "ParameterSensitivePredicate mit Kardinalitätsgrenzen; hier steht "
            "OptionalParameterPredicate mit einem Ausdruck der Form [@p] IS NULL. "
            "Genau daran macht die Demo ihre Zuordnung fest – sie zählt beide "
            "Elementarten getrennt und meldet eine Warnung, falls beide zugleich "
            "auftreten. Nach der Auswahl faltet der Optimierer das Prädikat "
            "konstant; die Variante für den belegten Zustand sieht schlicht eine "
            "Gleichheitsbedingung und darf deshalb eine Suche verwenden."
        ),
        "claims": "ADV-CLM-020",
        "sources": "SRC-026, SRC-049",
        "demo": "OPT-010",
    },
    {
        "slide_id": "SLD-M03-133",
        "title": "Voraussetzungen, Ausschlussgründe und Nachweis",
        "lead": (
            "Das Verfahren ist versionsgebunden und kennt dokumentierte "
            "Ausschlussgründe; die Eignung ist im Plan zu belegen."
        ),
        "points": [
            "Voraussetzung sind SQL Server 2025 und Compatibility Level 170",
            "unter Compatibility Level 170 ist OPTIONAL_PARAMETER_OPTIMIZATION standardmäßig eingeschaltet",
            "nicht angewendet bei lokalen Variablen, OPTION (RECOMPILE), ANSI_NULLS OFF und Autoparametrisierung",
            "ausbleibende Variantenbildung ist ein dokumentierter Befund, kein Anlass für Eingriffe",
        ],
        "note": (
            "Die vier Ausschlussgründe sind keine Randnotiz, sondern der häufigste "
            "Grund dafür, dass die Funktion im eigenen Code nicht greift. Besonders "
            "die ersten beiden treffen bestehende Anwendungen hart: Wer optionale "
            "Suchen mit lokalen Variablen aufbaut oder sie bislang mit OPTION "
            "(RECOMPILE) entschärft hat, erhält keine Varianten. Das ist kein "
            "Fehler, sondern dokumentiertes Verhalten – und es bedeutet, dass eine "
            "Migration auf SQL Server 2025 die Funktion nicht automatisch nutzbar "
            "macht. Die Demo OPT-010 behandelt Eignung deshalb als Messgröße: "
            "Findet sie trotz passender Version keinen Dispatcherplan mit optionalem "
            "Parameterprädikat, endet die Phase kontrolliert mit "
            "SKIP_EVIDENCE_MISSING und weist aus, was beobachtet wurde."
        ),
        "claims": "ADV-CLM-020",
        "sources": "SRC-007, SRC-026",
        "demo": "OPT-010",
    },
    {
        "slide_id": "SLD-M03-134",
        "title": "Steuerung, Abwahl und Abgrenzung",
        "lead": (
            "Die Optimierung ist auf Datenbank- und Abfrageebene steuerbar und "
            "ergänzt die klassischen Strategien, statt sie zu ersetzen."
        ),
        "points": [
            "Datenbankebene: ALTER DATABASE SCOPED CONFIGURATION SET OPTIONAL_PARAMETER_OPTIMIZATION",
            "Abfrageebene: USE HINT ('DISABLE_OPTIONAL_PARAMETER_OPTIMIZATION') überschreibt die Einstellung",
            "der Abfragehinweis wirkt unter jedem Compatibility Level und ist auch als Query-Store-Hinweis verfügbar",
            "Abgrenzung: OPT-009 entscheidet nach Kardinalität, OPT-010 nach dem NULL-Zustand",
        ],
        "note": (
            "Die Steuerung ist zweistufig: die Datenbankeinstellung für die Fläche, "
            "der Abfragehinweis für den Einzelfall. Die Demo weist das nach, indem "
            "sie bei eingeschalteter Datenbankeinstellung belegt, dass für die "
            "ausdrücklich abgewählte Abfrage kein Dispatcherplan entsteht – bei "
            "identischem Ergebnis. Merken Sie sich zum Abschluss die Trennlinie: Die "
            "parametersensitive Planoptimierung entscheidet anhand geschätzter "
            "Kardinalitätsunterschiede bei Gleichheits- oder Bereichsprädikaten, die "
            "Optional Parameter Plan Optimization anhand der Frage, ob ein Parameter "
            "NULL ist. Eine Abfrage kann von beiden profitieren, von einem oder von "
            "keinem. Damit schließt sich der Bogen zu QRY-004: Wo keines der beiden "
            "Verfahren greift, bleiben die dort verglichenen Strategien die "
            "tragfähige Antwort."
        ),
        "claims": "ADV-CLM-020",
        "sources": "SRC-026, SRC-049",
        "demo": "OPT-010",
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
            f'<p:sldId id="{FIRST_SLIDE_ID + offset}" r:id="{relationship_id}"'
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
    parser = argparse.ArgumentParser(description="ADV-011 Vertiefungsfolien uebernehmen")
    parser.add_argument("--check", action="store_true", help="nur Zustand pruefen")
    arguments = parser.parse_args()

    if not DECK.is_file():
        print("build-adv011-slides: FAIL (deck missing)")
        return 1
    if already_extended(DECK):
        digest = hashlib.sha256(DECK.read_bytes()).hexdigest()
        print(f"build-adv011-slides: SKIP (deck already extended; SHA-256 {digest})")
        return 0 if arguments.check else 1
    if arguments.check:
        print("build-adv011-slides: PENDING (deck not yet extended)")
        return 0

    digest = build(DECK)
    print(
        f"build-adv011-slides: PASS ({NEW_SLIDE_COUNT} slides added, "
        f"{TOTAL_SLIDE_COUNT} total; SHA-256 {digest})"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
