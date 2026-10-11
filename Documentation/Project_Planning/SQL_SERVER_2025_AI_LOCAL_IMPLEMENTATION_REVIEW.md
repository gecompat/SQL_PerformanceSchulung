# Lokaler KI-Pfad – Implementierung und Qualifikation

Stand: 2026-10-11. Scope: QRY-014 bis QRY-017, TSK-004/TSK-005.
Branch: `codex/sql2025-ai-local-demos`; Basis `fb53157eba381d23022b9a91aaa36a359f609576`.
Status: IMPLEMENTED; aktueller Actions-/Integrationsgate noch offen. Dieser Schnitt
nimmt weder den gesamten Workstream noch TSK-004 mit allen Providerpfaden ab.

## Technischer Umfang

Vier kleine T-SQL-Demos zeigen float32-Vektoren, Distanz/Norm/Normalisierung,
versioniertes Chunking und relationale/lexikalische/exakte Suche. Sie verwenden
FWK-010-Phasen, FWK-011-Ergebnisverträge und den vorhandenen sqlcmd-Prozessadapter.
Keine Embeddings, generative Inferenz, Previewoptionen oder externen Endpoints.
Konstruierten Vektoren wird keine Sprachsemantik zugeschrieben.

Jede Demo erzeugt ihre eigene markierte Datenbank. Vor Änderungen werden alle vier
Marker vollständig als Unicode-Bytes verglichen; NULL, falsche Werte, nachgestellte
Leerzeichen und überlange Werte müssen scheitern. Auch die Fachphasen prüfen Marker
und aktuellen Datenbankkontext. Datenfile maximal 256 MiB, Logfile maximal 64 MiB;
regulär 180 Sekunden, eigener Cleanup 60 Sekunden. Vorhandene Datenbanken werden vom
Qualifikationsrunner nicht übernommen. Fehler im Cleanup sind dominant.

## Runtime-Evidenz und Grenzen

Die lokale Charakterisierung verwendete eigene Linux-Container mit vier CPUs und
acht GiB RAM. Build 17.0.5005.3, Enterprise Developer. Auf 2025 bestanden zunächst je
zwei Lifecycles, Idempotenz sowie 24 Eigentumsgegenproben je Demo. Auf 2019 und 2022
bestanden je zwei SKIP_VERSION-Prüfungen pro Demo vor Setup; alle 24 unabhängigen
DB-Abwesenheitsprüfungen und die drei eigenen Containerabbauten bestanden.

Die ersten Charakterisierungsfehler bleiben sichtbar: falscher MSSQL_PID-Wert beim
kleinen Featureprobe; Variableninitialisierung in QRY-015 und falscher Propertyname
im Full-Text-Zweig von QRY-017. Die eigenen Container wurden jeweils entfernt.
Die Korrekturen verändern keine numerischen Sollwerte oder Toleranzen.

Der unabhängige Quellenreview fand zusätzlich ungeschützte Chunk-Schreibphasen,
SQL-Stringpadding/Trunkierung, leere/NULL-Ergebnisse mit festen Sollwertausgaben und
verdecktes Full-Text-WARN. Der gebündelte Korrekturschnitt ergänzt vollständige
Byteprüfungen, Guards, gemessene Metriken und negative Ergebnisfixtures. Seine neue
2025-Qualifikation prüft 48 Markerfälle je QRY-014/015/017 sowie 80 bei QRY-016 und
zusätzlich falsche Quellenbereiche, leere Chunks und fehlende Top-Treffer.
Die neue 2025-Qualifikation bestand: je zwei Lifecycles pro Demo (QRY-017 mit dem
vorgesehenen Full-Text-WARN), alle 224 Markergegenproben, fünf fachliche
Negativkontrollen, Setup-Idempotenz und unabhängige DB-/Containerabwesenheit.
QRY-014/015 wurden vor der isolierten letzten QRY-016-Korrektur geprüft; deren
SQL-/Ergebnisbytes blieben dabei unverändert. Ein zusätzliches PRINT mit Subquery
wurde nach Fehler 1046 durch eine gemessene skalare Variable ersetzt; nur QRY-016
und die zuvor noch ausstehende QRY-017-Qualifikation wurden lokal neu ausgeführt.
Die unabhängige Korrekturkontrolle und aktuelle CI bleiben offen.

Fehlendes Full-Text bleibt WARN_OPTIONAL_EVIDENCE_SKIPPED. Der Runner trennt den
bestandenen Qualifikationstest vom aggregierten Demoergebnis; Versions-Skips sind
kein Nachweis einer Vektorfunktion. Windows, Podman, zusätzliche Editionen und der
installierte Full-Text-Zweig besitzen hier noch keine neue Runtimeabnahme.

Reproduktion auf einer explizit bereitgestellten Wegwerf-Containerinstanz:

```powershell
python Tests/Runtime/run_sql2025_ai_local.py --target docker --container '<eigener-container>' --expected-major 17
```

SQLCMDPASSWORD ist die einzige Passwortquelle. Kein Passwortargument, keine
Repository-Logs, keine Persistierung von Prompt-/Antwort-/Plan-/Hostinventardaten.

## Verarbeitung und CI-Aufwand

Die neue CI führt drei Versionsjobs aus, je vier Demos mit zwei Lifecycles; native
Ownership-/Ergebnisgegenproben sind auf 17.x begrenzt. Es gibt einen Implementierer
und einen unabhängigen Review für konkrete Safety-/Versions-/Ergebnisrisiken,
anschließend höchstens zwei gebündelte Reviewkorrekturwellen. Charakterisierung,
Qualifikation und Integration sind getrennt; unveränderte Fehler werden nicht
bis zum PASS wiederholt. Modell-/Tokenverbrauch ist unbekannt.

Die vorhandenen Katalogtrigger von OPT-017 und W-COV-001 können zusätzlich die
bestehenden 30 SQL-Jobs auswählen. Diese breitere bestehende Regression bleibt in
diesem Schnitt erhalten: Eine Änderung ihrer Abhängigkeitslogik wäre eine eigene
Workflowänderung mit gesonderten Negativkontrollen. Andere SQL-Workflows werden
durch die neuen Demopfade nicht ausgewählt. Die statischen Projektvalidatoren und
die zentralen Registry-/Governance-/Privacygates bleiben wirksam. Der neue Workflow
speichert keine Rohlogs und unterbricht laufende mutierende Jobs nicht automatisch;
Containerabbau prüft sein eigenes Label und anschließende Abwesenheit.

Die Lab-Katalogerweiterung erhöht die geplante vollständige Provider-/Versionsmatrix
von 264 auf 312 Runs. Das ist eine Planungssumme, kein ausgeführter Nachweis.
Keine neue Vollmatrixautomation oder wiederkehrende Modellarbeit wird aktiviert.
CI bewertet den aktuellen Head; Nachweise früherer Commits ersetzen diesen Gate nicht.

## Quellen und nächste Schritte

Produktverträge: SRC-070 bis SRC-075, SRC-100 und SRC-104 im Quellenregister.
Der [Modellpfad-Leitfaden](../HowTo/SQL_SERVER_2025_AI_MODEL_PATHS.md) verwendet die
öffentlichen SQL_Server_Lab-Verträge SRC-101 bis SRC-103. Die Anwendung kann lokal
HTTP verwenden, während SQL-seitige Modellaufrufe eine getrennte TLS-Strecke benötigen.
Für die anderen 14 Demoentwürfe bleibt der Workstreamplan maßgeblich. Ein echter WhatIf-Aufruf des öffentlichen lokalen RAG-Controllers ergab READY,
GenerationLane=local, Egress=denied und TopK=1. Es wurden keine Inferenz, SQL-
Mutation oder Secrets gelesen. Cloud-/Bezahl- und ONNX-Hosteffekte behalten ihre konkrete Freigabegrenze.
