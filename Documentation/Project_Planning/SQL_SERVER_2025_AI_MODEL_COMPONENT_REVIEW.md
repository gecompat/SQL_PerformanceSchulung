# TSK-007: begrenzte öffentliche lokale Embeddingkomponente

Stand: 2026-10-12, Basis `1f4b0f8f9435631977918122d62c337a6665afcd`.
Die öffentliche Invoke-SqlServerLabAiModel-API (Application Programming Interface; Programmierschnittstelle) kann ein vorhandenes lokales Modell
ohne SQL-Verbindung aufrufen. Dieser getrennte Komponentenschnitt prüft genau
diese API; er ersetzt den [weiter blockierten RAG-Pfad](../HowTo/SQL_SERVER_2025_AI_MODEL_PATHS.md#offene-secret-grenze-vor-live-rag)
nicht. QRY-020 verlangt zusätzlich SQL-seitige REST-/HTTPS-/Credential-/
Persistenzgegenproben und bleibt PROPOSED. Keine neue Demo-ID oder Umdeutung.

## Vor Admission gebundener Scope

Ein privater Caller verwendet ausschließlich die öffentliche Funktion des sauberen
Lab-Commits `f4c9fcd30c397e25c95e57d7aeecc98dc194063e`. Nach explizitem Import
bindet er ein exportiertes CommandInfo an Modulname, tatsächlichen Modulpfad und
öffentliche Funktionsdatei. Keine Privatfunktionsaufrufe, Overrides oder Labänderung.
Vorhandenes nomic-embed-text:latest, lokaler Katalogkey
ollama-nomic-embed-text-v1-5, Dimension768. Fester synthetischer kurzer Dokumenttext
mit explizitem search_document:-Präfix; die eigenständige API ergänzt dieses
Retrievalpräfix nicht selbst. Modellkarte/Katalog nennen Apache-2.0; konkrete
Live-Digestbindung ersetzt keine vollständige Artefakt-/Supply-Chain-Abnahme.

WhatIf-Plan muss lokale Lane, Embeddingzweck, Dimension768, Port11434, Egress denied,
fehlenden CredentialRef und genau einen Versuch/Retry0 liefern. Feste Loopback-
Metadaten ohne Proxy oder Redirect prüfen Version, exakten Tag, eindeutigen Digest,
fehlende Remote-Felder, Embedding-Capability und tatsächliche Dimension. Dieselbe
Bindung vor und nach jedem Inferenzaufruf; keine atomare Sperre des fremd verwalteten
vorbestehenden Diensts behauptet. Die bereits vorhandenen Gewichte dürfen für
Inferenz geladen werden; Cache-/RAMzustand und Geräteausführung werden nicht attestiert.
Keine Modell-/Dienstinstallation, Neustarts, Downloads, Truständerung oder Cloudfallback.

Genau zwei öffentliche Aufrufe mit identischem Input, je Timeout30Sekunden und
Retry0. Jede vollständige Rückgabe muss SUCCEEDED, richtigen Key/Plan und Attempts1
liefern; exakt768 numerische endliche Werte und positive endliche Norm. Identische
Eingabe darf zwischen beiden Vektoren maximal1e-5 absoluten Koordinatenunterschied
zeigen. Dies ist ein Integritäts-/Wiederholungsoracle, keine allgemeine semantische
Qualitäts-, Retrieval- oder Antwortabnahme. Vollvektoren und tatsächliche Bindungen
bleiben ausschließlich im ignorierten Runtime-Nachweis; öffentliche Counts/Aggregate
enthalten kein Hostinventar, Prompt, Querytext oder generierte Antwort.

## Budget, Review und Cleanup

Sechs kohärente Quellenkandidaten maximal, Checkpoint3/hard6; höchstens zwölf
öffentliche Inferenzaufrufe und90 Metadatenrequests über diesen Komponentenschnitt.
C1 reserviert zwei Inferenzaufrufe und15 Metadatenrequests mit jeweils5Sekunden.
Ein äußerer eigener NoProfile-Prozess hat150Sekunden reguläres Budget und genau
einen gemeinsamen5Sekunden-Reapingpfad. Kill betrifft ausschließlich dessen
gespeicherten eigenen Prozesshandle, niemals den vorbestehenden Modelldienst.
Nach Collectorfehler/Timeout bleibt serverseitiges Modellrequestende UNKNOWN,
auch wenn das eigene Kind anschließend beendet ist; keine weitere Inferenzadmission.
Ein tatsächlicher Timeout-/Killfall ist durch Mocktests nicht empirisch qualifiziert.

Ein Implementierungsverantwortlicher und ein enger unabhängiger Quellenreview.
P2 zu unqualifizierter Commandauflösung, nicht vollständig behandeltem Collector-
Recoverypfad und optimierbaren assert-Sicherheitsgates vor Nativeadmission geschlossen.
Ein Restpunkt zu blockierendem Stream-Close im UNKNOWN-Pfad ebenfalls entfernt;
keine Reviewkette oder Reviewer-Runtime. Zwei positive/neun negative reine Binding-/
Vektorfälle und sieben Parentmockmethoden unter normalem Python und -O bestanden.
Geänderte vorbereitende Quellen/Tests geprüft, keine unveränderte Runtimewiederholung.
Modell-/Tokenverbrauch unbekannt. Exklusive Admission-/Receiptdateien verhindern
unveränderten Retry. Eigener Prozess muss bestätigt beendet sein; keine eigenen
DBs, Container, Volumes, Credentials, Gateways oder Dienstobjekte erzeugt.

Quellen SRC-112/SRC-113, Abruf2026-10-12. Native C1-Ergebnis, eigene Prozessclosure
sowie aktuelle PR-/Head-/Main-/Tree-/FF-/Ownbranchgates folgen vor Abschluss.
TSK-007, Live-RAG (Retrieval-Augmented Generation; Antworterzeugung mit zuvor ausgewählten Quellen), SQL-HTTPS, QRY-020, volle Demo-/Modul-/Workstreamabnahme offen.

## Tatsächliches C1-Ergebnis

C1 lieferte zwei vollständige erfolgreiche öffentliche lokale Embeddingrückgaben.
Beide768-dimensionale Vektoren, zusammen1536 numerische endliche Koordinaten,
positive endliche Normen. Identischer fester Input, gleicher tatsächlicher
Modell-/Digest-/Versions-/Plan-Key, maximaler tatsächlicher Koordinatenunterschied0.
Ausgeführte Caller-/Launcher- und sechs Labquellen bytegebunden; beide Vollvektoren,
Normen und wiederholte Bindungen anschließend rein unabhängig neu ausgewertet.
Null weitere Modell-/SQLaufrufe für diese reine Ergebnisprüfung.

Eigener Callerprozess bestätigt beendet, kein Timeout/Collectorfehler/UNKNOWN.
Vorhandener Dienst bleibt erhalten; keine eigenen SQL-/Container-/Gateway-/
Credential-/Dienstobjekte entstanden. Lab-Checkout bleibt am gebundenen Commit
sauber/unverändert. Begrenzte lokale Entwicklungsevidenz PASS_COMPONENT_ONLY;
keine GitHub-Modellruntime-, Geräte-, Sprach-/Retrieval-/Antwortqualitäts-,
RAG-/SQL-HTTPS-/QRY020-/Supply-Chain- oder Workstreamabnahme.
Zwei öffentliche Inferenzaufrufe verbraucht, keine Retrywelle. Modell-/Tokenverbrauch
unbekannt; tatsächlicher Timeoutnachweis weiterhin NOT_ESTABLISHED. Aktuelle
Head-/Main-/Integrations-/Tree-/FF-/Ownbranchgates folgen vor regulärem Abschluss.
