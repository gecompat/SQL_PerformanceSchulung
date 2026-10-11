# QRY-018 – Offline-RAG und Quellenprüfung

Stand: 2026-10-11. TSK-008, CUR-017/CUR-022, TP-RUN.
Basis: `0b6743f14f855103dfa63b0b67ffc75426f1ad1f`;
Branch: `codex/sql2025-ai-offline-rag`. Status IMPLEMENTED, aktuelle Gates offen.

## Umfang und Ergebnisvertrag

Der Schnitt ergänzt ein FWK-010/FWK-011-Demopaket mit eigener markierter Datenbank,
read-only Preflight, getrennten SQL-Phasen und unabhängigem Cleanup. Drei synthetische
Quellenversionen werden importiert und mit FIXED64 ohne Overlap gechunkt. Konstruierte
Geometrievektoren zeigen Exact Retrieval mit einer begrenzten erlaubten Quellenmenge.
Zehn eingefrorene Antworten werden gegen aktuellen tatsächlich retrievten Kontext geprüft:
eine gestützte Antwort, sieben abgelehnte Antworten und zwei begründete Nichtantworten.
Baseline enthält sieben unüberprüfte Claims. Alle vier Metriken werden tatsächlich gezählt.

Die Claimprüfung ist ausdrücklich auf die feste Aufbewahrungssatzform begrenzt, kein
allgemeiner Entailmentprüfer. Token-/Inferenzzeit ist N/A. Kein Modell, externer Endpoint,
Cloudkosten-, Preview- oder Hosteffekt. Live-RAG bleibt durch die im
[Modellpfad-Leitfaden](../HowTo/SQL_SERVER_2025_AI_MODEL_PATHS.md) dokumentierte Secret-Grenze
von SQL_Server_Lab separat angehalten. Andere Repositories bleiben unverändert.

## Qualifikation und Review

Die lokale 17.x-Qualifikation bestand zwei Lifecycles und anschließende unabhängige
DB-Abwesenheit. Auch Setup-Idempotenz bestand, dazu
80 Markerfälle (vier Marker, vier Abweichungen, fünf Phasen) sowie sieben fachliche
Negativkontrollen hinzu. Geprüft werden falscher Claim, alte Quellen-ID, leere Chunks,
falscher Chunktext, fehlende aktuelle Version, leerer Replaybestand und falsches Faktmetadatum.
Jede scheiterte am erwarteten FAIL_RESULT_CONTRACT. Der eigene Linux-Container mit vier
CPUs und sechs GiB RAM wurde danach entfernt; seine Abwesenheit wurde unabhängig geprüft.
Cleanupfehler bleiben dominant. Auf 2019/2022 bestanden je zwei SKIP_VERSION-Lifecycles
vor Setup, jeweils mit unabhängiger DB-Abwesenheit und eigenem Containerabbau.
Der erste Ausführungsleitfaden-Check vermisste zwei verpflichtende Runbookbegriffe;
die Anleitung wurde präzisiert und besteht. Keine SQL-Ergebnis-/Oraclekorrektur erforderlich.

Der unabhängige Quellenreview schloss diese Ergebnis-/Safety-/Versionsprüfung ohne
konkrete offene Findings ab. Keine Reviewkorrekturwelle erforderlich; weiterhin höchstens
zwei kohärente Korrekturwellen je Schnitt. Quellenreview ist keine zusätzliche Runtimeattestation.
Windows, Podman, weitere Editionen, reale Sprachqualität und Livegeneration bleiben offen.

## Verarbeitung und CI-Aufwand

Ein Implementierungsverantwortlicher ergänzt den vorhandenen Runner und Workflow;
kein zweites Provisionierungssystem oder zusätzliche Modellarbeit. Der endliche Schnitt
ist eine Demo mit zwei Lifecycles pro Version, einem Review und höchstens zwei Korrekturwellen.
Checkpoints: lokale Qualifikation, stabiler Reviewkandidat, aktuelle CI und Integration.
Fehlende Verbrauchsmessung bleibt unbekannt; der unveränderte allgemeine Workstreamumfang
und seine begrenzte Reviewanzahl bleiben maßgeblich.

Die vorhandene KI-Matrix bleibt bei drei Versionsjobs. Änderungen an ihren Runtimeinputs
rechtfertigen neue aktuelle Runs; frühere QRY-014–017-PASSs ersetzen diese nicht. Der neue
Katalogeintrag erhöht die geplante Docker-/Podman-Vollmatrix von 312 auf 324 Runs, keine
ausgeführte Abnahme. Die bestehende breitere Katalogregression bleibt erhalten; es gibt
keine zusätzliche Vollmatrixautomation, keinen Rohlogexport und keine Reviewkette.
Static-only Folgedokumentation verlangt keine erneute SQL-Qualifikation am gleichen Input.
Eine nachträgliche konkrete Secret-Grenze betraf den bestehenden KI-Readiness-Schritt:
Docker erhielt den Passwortwert als -e-Prozessargument. Der korrigierte Schritt übergibt
nur SQLCMDPASSWORD als Namen und übernimmt den Wert aus der Prozessumgebung, wie die
vorhandenen Runtimeadapter und alle lokalen Qualifikationen. Eine statische Regression
schützt diese Grenze. Die neue Runtimeblockänderung rechtfertigt einen frischen Head-/CI-Gate;
laufende mutierende Jobs werden bis zu ihrem Cleanup erhalten. Keine SQL-/Oraclekorrektur.

## Reproduktion und nächste Schritte

```powershell
python Tests/Runtime/run_sql2025_ai_local.py --target docker --container '<eigener-container>' --expected-major 17 --demo QRY-018
```

SQLCMDPASSWORD ist die einzige Passwortquelle. Source IDs, SourceVersion und Quellenbereiche
sind ausschließlich synthetisch; Prompts, Hostinventar und Modellantworten werden nicht persistiert.
Produkt-/Architekturquellen: SRC-073, SRC-079 und SRC-095; am 2026-10-11 erneut geprüft.
Aktuelle PR-/Main-Evidenz und vollständige Integration bleiben vor Abschluss erforderlich.
