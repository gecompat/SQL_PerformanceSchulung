# DGN-007 – gehaltener vollständiger Handshakeeingang vor Start

Stand: 20. Oktober 2026. Basis `256e43d6d4ca4ac7a248dadbe4c88e6923577ef4`
nach vollständig abgeschlossenem PR260. Status `SOURCE_TEST_PRE_PENDING`.
Der menschliche kontinuierliche Auftrag autorisiert diese eigene priorisierte
Voraussetzung für die spätere operative stdin-Anbindung. Der neue Schnitt
setzt weder historische C3/C4-Grenzen zurück noch wiederholt deren Tests.

## Rahmen und Abnahme

Ein Implementierungsowner, höchstens sechs stabile Quellen-/Testkandidaten,
Checkpoint nach dem zweiten, harte Grenze nach dem sechsten. Enthalten sind
ein unabhängiger Auswahl-PRE, ein Source/Test-PRE mit ausdrücklichem Lauf-GO
und höchstens fünf gezielte geänderte Befundnachläufe, passende lokale Tests,
aktuelle vollständige PR-/Main-Gates und Abschluss. Wiederholungen benötigen
geänderten relevanten Input oder ein fehlendes Gate; grüne unveränderte
Native-/SQL-Suiten werden lokal nicht wiederholt. Kein Kosten-/Tokenzähler
verfügbar, Verbrauch UNKNOWN. Nach Abschluss folgt ein neuer endlicher Schnitt.

Neue Quelle `Tests/Tools/dgn007_handshake_input_plan.py`, eigener Harness
`Tests/Static/test_dgn007_handshake_input_plan.py`, eigener Linux-/Python3.12-
Workflow. Bestehende fünfzehn Bootstrapbuilder, native Kanalquelle und Suite,
neun Runtimequellen, SQL und synthetisches Ledger bleiben unverändert.
Gemeinsame Kontrollpins/Encoder-/Provideranker werden ausdrücklich aus
`dgn007_session_channel._Control` verwendet; dies erzeugt keinen nativen Call.
Neue benötigte Namespacehelper müssen exakte eigene Funktionen sein und
werden durch dieselben Namespace-/Code-/Klassenpins gehalten.

## API und vollständige Bindung

`plan_handshake_inputs(namespace, selections, *, expected_format)` ist rein
und atomar. Jede exakte eingefrorene `HandshakeInputSelection` hält separat
Metadata-Chunks, neun Rawbodies, vollständiges I7, W6, K8 und R4. Exaktes Tupel
mit ein bis drei Slots; genau Runner/Proxy/Harness-Präfix und gemeinsame
vollständige Commit-/Raw27-/Sourceprofil-/Nonce-/D9-Werte. R4 entspricht separat
dem vollständigen K8 und S15/Controls/P11 des W6; keine Defaults aus Empfang.
Alle primitiven Callerformen sowie Chunk-/Bodytypen und Transportgrößen aller
Slots vor erstem JSON-Encoder-/SHA-Dispatch. Tatsächliche Metadataformen und
Semantiken bleiben je Slot im vorhandenen Bodyguard; keine doppelte Parsephase.

Der bestehende `_inline_receive_declared_bodies` prüft jeden tatsächlichen
Metadataeingang und alle neun Originalbodyhashes gegen separat gehaltenes
I7/W6/K8. Es gibt keine Body-LF-Normalisierung. Die ursprünglichen Rohobjekte
bleiben privat erhalten. Eine zusätzliche ganze R4-Bindung wird geprüft.
Keine Workerwahl wird aus einer selbst gemeldeten Kurzform ergänzt.

Vor Ausgabe eines Plans werden alle fünf vollständigen E4-Formen je Slot
unter ihren bestehenden Rollen tatsächlich kanonisch gerechnet: METADATA,
REPORTED und die drei eigenen Installation-/Worker-/Kontextpräbilder.
Jede einschließlich 16 Headerbytes höchstens 16384, die fünf Formen je Slot
einschließlich aller fünf Headeranteile gemeinsam höchstens65536.
Die kanonische METADATA ist bytegleich zum geprüften tatsächlichen
Eingang. Neue Rollen, Hashdomains, Header oder komprimierte Feldmengen sind
nicht vorgesehen. Dies prüft gegebene Deklarationen, keine frische S15/P11-
Aufnahme oder operative Inventur.

Die bestehenden Encoder erzeugen genau BODY_RELEASE, BODY_END, IMPORT_RELEASE
gegen das separat gehaltene volle K8, jeweils kanonisch und höchstens256Bytes.
Tatsächlicher Header+Metadata+neun Bodies+alle drei Commands zählen gemeinsam
vor Start: höchstens1064960Bytes je Slot, global höchstens3194880Bytes.
Commands erhalten kein Zusatzbudget. Der Plan hält einzelne Phasenstücke
getrennt; kein vorzeitiger Body-/Importversand wird dadurch ermöglicht.

Äußere Encoder-/Provideranker bleiben über alle Slots, Unterhelper, Encoding
und Fehlerpfade gehalten. Kein inneres Neubaselining heilt Drift. Bindungs-
POST vor Erfolg und nach Fehlern, Providerverlust vor Encoderverlust vor
erster anderer Ursache. Feste geschlossene Issues, keine Rohfehlerketten,
privaten Pfade, Payloads oder Partialpläne im öffentlichen Report.

Erfolg `PLANNED_DECLARED_HANDSHAKE_INPUTS` liefert ausschließlich die privat
gehaltenen geprüften Eingangs- und Commandbytes. `runtime_attested`,
`trust_attested`, `import_used_bytes_attested` und `method_approved` bleiben
false, `validation_scope=PROJECT_SEMANTIC`. Kein Popen/Datei-/Pipezugriff,
kein Send, kein Phasen-/Ledgertransition, keine Wiederaufnahme-/Replayauthority.
Ein späterer nativer Owner muss vor Vorbereitung seine gemeinsame Deadline
beginnen und diesen Plan innerhalb derselben Steuerung verbrauchen; der pure
Plan attestiert keine 20-s-Ausführung oder operative Empfangs-/Importfreigabe.

## Gegenproben und Aufwand

Unabhängige vorhandene Fixtureoracles nur als Harnessmethoden, keine Vererbung
alter Testmethoden. Geprüft werden alle drei Rollen, Originalbodyidentität,
kanonische Commands/eigene Kontextdomains, ganze separate I/W/K/R-Bindung,
beide D9/Originalhash/Rawhashes, Typ- und Größenfehler auch im letzten Slot
vor SHA, max Chunk-/Body-/Metadatalimits, alle fünf Rollen/Größen samt gemeinsamer
Kappe und eingeschlossene Commandkosten an der Transfergrenze. Keine
Partialausgabe bei spätem Fehler. Provider-/Encoder-/Namespaceverluste und
private sichere Fehler mit echtem Fixture-/Realcache-/Encoderrestore.

Der neue Workflow selektiert nur eigene Quelle/Harness/Nachweis/Workflow und
vollständige tatsächliche Importclosure einschließlich gemeinsamem _Control.
Keine Erweiterung der alten Offline-/SQL-Selektoren; zentrale Registry,
Governance und Privacy bleiben. Reine eigene Syntax-/Datenverarbeitung erlaubt
cancel-in-progress:true. Lokale vollständige neue Suite einmal auf Windows
und Linux3.12 nach unabhängigem Lauf-GO; CI am aktuellen Head/Base und Main
bleibt frisch erforderlich. Keine zusätzliche Automation oder Reviewkette.

## Nachweis

Auswahl-PRE auf Basis `256e43d6d4ca4ac7a248dadbe4c88e6923577ef4` und ursprünglichem
Plan-SHA256 `53e8fad6965bc836eebc9b2222febe4e460331f3069cf6df3c656bb4a04bde83`
ohne offene P1/P2/P3 freigegeben; die geforderten Präzisierungen sind übernommen.
Noch kein Source/Test-Lauf-GO; keine neue Suite oder native Probe ausgeführt.
C1 ergänzt ausschließlich die neue pure Quelle, eigene Suite/CI und den
aktuellen Dokumentstand. Vorprüfung statisch, noch keine Kandidatenimporte.
PR260 schloss mit acht PR-Gates und sechs Main-Workflows SUCCESS, nativer
16/16-Suite ohne SKIP, vollständiger Treegleichheit und sauber synchronem
Main ab. Eigener lokaler/Remote-Branch entfernt; konkrete Abschlussbindung
im [PR260](https://github.com/gecompat/SQL_PerformanceSchulung/pull/260).
Nachfolgend bleiben der tatsächlich nichtblockierende bidirektionale
Phasenowner, einmaliger Verbrauch, frische Workerprofile, echte Quellenloader-
Records und tatsächliche Import-/UsedBytesprovenienz eigene Abnahmegrenzen.
