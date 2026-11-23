# SQL-Server-Runtime-Matrix

## Status

| Merkmal | Wert |
|---|---|
| Status | `VALIDATED` |
| Prüfdatum | 2026-07-24 |
| Validierter GitHub-Actions-Lauf | `30099942191` |
| Geprüfter Commit | `e3f37e0c96a6d9a0c02c4e89181ceef564e1ae57` |

## Zweck

Dieser Bereich validiert die implementierten Framework-Komponenten gegen reale, ephemere SQL-Server-Instanzen. Die GitHub-Actions-Matrix verwendet getrennte Container für SQL Server 2019, 2022 und 2025. Pro Job läuft genau eine SQL-Server-Version.

## Gebundener Vergleich für `OPTIMIZED_SP_EXECUTESQL`

Der [OPTSP-Traineraufruf](../../Documentation/Project_Planning/OPTIMIZED_SP_EXECUTESQL_CONCURRENT_COMPILE_DESIGN.md#gebundenen-vergleich-ausführen)
führt zwei OFF/ON-Paare und zwei Kontrollen auf dem festgeschriebenen
SQL-Server-2025-Build aus. Er betreibt genau einen eigenen Container
mit Loopback-Port und meldet den Befund nach geprüftem Abbau.

## Matrix

| SQL Server | Container-Tag | erwartete Major Version | Compatibility Level | Ergebnis |
|---|---|---:|---:|---|
| 2019 | `mcr.microsoft.com/mssql/server:2019-latest` | 15 | 150 | `PASS` |
| 2022 | `mcr.microsoft.com/mssql/server:2022-latest` | 16 | 160 | `PASS` |
| 2025 | `mcr.microsoft.com/mssql/server:2025-latest` | 17 | 170 | `PASS` |

Die Tags werden vor jeder Ausführung neu aus der Microsoft Container Registry bezogen. Das Ergebnis bezieht sich deshalb auf den zum Laufzeitpunkt ausgelieferten aktuellen Containerstand und nicht auf ein dauerhaft festgeschriebenes CU (Cumulative Update; kumulatives Produktupdate).

## Ausgeführte Prüfungen

Der stufenberichtende Matrix-Entry-Point prüft je Version:

1. Engine-Major-Version und unterstützte Engine Edition,
2. `FWK-002` (Namens-, Schutz- und Lifecycle-Vertrag für Testdatenbanken) mit `CREATE`, Markerprüfung und `DROP`,
3. `FWK-001` (Preflight-Vertrag) gegen die erzeugte Testdatenbank,
4. Installation und zweimalige deterministische Ausführung von `FWK-003` (Vertrag für synthetische Testdaten),
5. Installation sowie Begin/End-Messung von `FWK-004` (Messvertrag),
6. Statistikproperties, Histogramm und Actual-Plan-Ausgabe aus `FWK-005` (Vertrag für Plan- und Statistikevidenz),
7. Installation und reale parallele Sessions aus `FWK-006` (Multi-Session-Orchestrierungsvertrag),
8. Query-Store-Status, Enable und Restore aus `FWK-007` (Query-Store- und Extended-Events-Vertrag),
9. XE-Status, Create, Start, Stop und Drop aus `FWK-007`,
10. einen realen `FWK-010` (Runtime-Harness-Vertrag)-Harness-Lauf über den containerinternen `sqlcmd`-Proxy.

Alle Testdatenbanken verwenden die FWK-002-Marker und werden im `finally`-Pfad entfernt. Ein Cleanup-Finding lässt den Matrixjob fehlschlagen.

## Zugangsdaten und Datenschutz

Das SA-Kennwort wird ausschließlich zur Laufzeit aus GitHub-Run-Kennungen erzeugt, sofort maskiert und über Umgebungsvariablen an Container und `sqlcmd` übergeben. Es wird nicht im Repository gespeichert. Der Container besitzt keine veröffentlichte Host-Portzuordnung und kein persistentes Volume.

Der Proxy `docker_sqlcmd_proxy.py` legt kein Kennwort auf die Kommandozeile. Er liest repositorylokale SQL-Dateien und überträgt sie über Standard Input an das im Container enthaltene Microsoft-Tool `sqlcmd`.

Die kurzlebigen Matrixdiagnosen enthalten nur Teststufen, Summarycodes und gekürzte Fehlerkontexte. Sie werden drei Tage aufbewahrt und enthalten keine Zugangsdaten oder vollständigen SQL-Resultsets.

## Durch die Matrix identifizierte Korrekturen

- Die Manifestspalte `[RowCount]` muss wegen des Schlüsselworts `ROWCOUNT` gequotet werden.
- Die Query-Store-Katalogsicht verwendet `flush_interval_seconds`; `DATA_FLUSH_INTERVAL_SECONDS` ist der Name der `ALTER DATABASE`-Option.
- Bei `sqlcmd -r 1` können Informationsmeldungen auf Standard Error erscheinen. Die Matrix wertet deshalb beide Streams aus, während der Prozess-Returncode das Ausführungsfehlersignal bleibt.

## Grenzen

Die Matrix validiert SQL Server auf Linux in offiziellen Microsoft-Containern. Sie ersetzt keine separate Prüfung Windows-spezifischer Funktionen, Editionen oder OS-Metriken. Die `latest`-Tags eignen sich zur laufenden Kompatibilitätsprüfung; ein späterer Release benötigt zusätzlich dokumentierte konkrete Image-Digests oder CU-Stände.

## IDX-007-Erhebungspilot

[`idx007_hot_leaf_pilot.py`](idx007_hot_leaf_pilot.py) ist ein getrennter,
begrenzter Engineering-Pilot für die Wait-/Seitenbindung der IDX-007-Lehrnotiz.
Er ist keine Frameworkkomponente, Demo oder Leistungsqualifikation. Er startet
für einen Aufruf einen eigenen SQL-Server-Developercontainer ohne Netzwerk,
Ports oder persistente Volumes und begrenzt ihn auf 2 CPUs und 4 GiB RAM. Die
synthetische Datenbank hat einen pro Lauf erzeugten Namen und die vier
Framework-Ownershipmarker; Cleanup prüft sie vor `DROP` und entfernt danach
den eigenen Container.

Die verwendbare, katalogisierte Vorführdemo liegt unter [`Demos/04_Rowstore_Columnstore/IDX-007_Last_Page_Insert_Contention/`](../../Demos/04_Rowstore_Columnstore/IDX-007_Last_Page_Insert_Contention/README.md). Sie verwendet das gemeinsame Manifest-Framework mit einer eng begrenzten `idx007_container`-Phase; der Runner erlaubt diesen Ausführungstyp ausschließlich für IDX-007. Der Aufruf benötigt keinen Host-SQL-Server und keinen Host-`sqlcmd`.

Der Engineering-Pilot selbst bleibt der Runtime-Unterbau. Ein Aufruf verwendet einen dieser Majorwerte:

```text
python Tests/Runtime/idx007_hot_leaf_pilot.py 15
python Tests/Runtime/idx007_hot_leaf_pilot.py 16
python Tests/Runtime/idx007_hot_leaf_pilot.py 17
```

Der Lauf prüft den konkreten Engine-Build, Compatibility Level und XE-Feld-
beziehungsweise Actionbestand. Vor jedem Insertschub hält der Reader einen
exklusiven, sitzungsgebundenen `sp_getapplock`; die Actors fordern nach ihrer
Bereitschaft jeweils einen Shared-Lock auf derselben Ressource an. Der Reader
wartet auf alle Bereitschaftsrecords, setzt dann den XE-Startmarker und löst
den Lock. Die Steuerung signalisiert nach bestätigtem Zeilenzuwachs
`lab.BurstDone`; der Reader wartet im markierten Fenster auf dieses Signal und
liest danach die Seitenkette. Eine zusätzliche DMV-Abfrage der wartenden
Lock-Anfragen wird nicht als Freigabebedingung verwendet.
Die Markerereignisse filtern direkt auf das XE-Feld `statement`, nicht auf den
gesamten Batch-Text. `package0.event_sequence` ordnet die
Latch-Beginn- und -Endereignisse; zwei getrennte Insertschübe müssen
verschachtelte exklusive `BUF`-Latch-Waits verschiedener Actor-Requests auf
einer zu diesem Capture-Rand bestätigten rechten Blattseite zeigen. Das
buildgebunden beschriebene `duration`-Feld bleibt begrenzt und wird diagnostisch
ausgegeben; gerundete UTC-Zeitstempel bestimmen die Überlappung nicht. Die
Zielseite darf sich
zwischen den Schüben durch eine Seitenaufteilung ändern; jeder Rand wird
unabhängig gegen Blattkette und Rücklink geprüft. Ein fehlender oder
widersprüchlicher Nachweis endet als `NOT_PROVEN`; ein Cleanupfehler lässt den
Lauf fehlschlagen.

Der Workflow
[`idx007-live-capture.yml`](../../.github/workflows/idx007-live-capture.yml)
führt die statischen Verträge auf Pull Requests aus und lässt die drei
digest-gepinnten Runtime-Builds dort seriell laufen. `workflow_dispatch` kann
dieselbe Matrix manuell erneut ausführen. Die paketierte Vorführdemo wird über den getrennten manifestbasierten Einstieg
qualifiziert. Ein erfolgreicher Engineering-Pilot oder Demo-Lauf ändert den
`METHOD_DRAFT`-Status nicht und ist keine allgemeine Leistungsqualifikation.

Der Kettenleser wird vor der Actorfreigabe gestartet und wartet in derselben
SQL-Session auf die Burstbarriere. XE erfasst zusätzlich markierte
`sql_statement_starting`-/`sql_statement_completed`-Ereignisse für diesen
synthetischen Batch. Ein Burst zählt nur, wenn zwei erfolgreiche exklusive
`BUF`-Waits verschiedener Requests auf derselben Seite überlappen und ihre
gemeinsame Waitzeit in das markierte Kettenlesefenster fällt. Die Kettenprüfung
liest die zu diesem Zeitpunkt allozierten Blattkandidaten und bindet die
Waitseite an Objekt, Index, Partition, Blattebene, terminalen Nachfolger und
Vorgänger-Rücklink. Das ist eine geordnete empirische Klammer auf den drei
konkreten Builds, keine atomare DMV-Snapshotgarantie und kein Nachweis für
gleichzeitige Page-Splits.

Der Pilot verwendet je Build eine konkret erprobte Indexform: SQL Server
2019/2022 verwenden 501 Seeds, `FILLFACTOR=100` und 80 Actors; SQL Server
2025 verwendet 501 Seeds, `FILLFACTOR=10` und 56 Actors. Je Actor erfolgt ein
Insert pro Burst. Die physische Vorabprüfung bindet Seitenzahl und Reserve an
den tatsächlichen Lauf. Der geforderte Wait- und Terminalnachweis bleibt für
jeden Build unverändert. Actor-Sessions werden vor dem Burst registriert;
Fortschritts-Updates auf der gemeinsamen Steuerungstabelle während der
Messfenster entfallen. Der Harness erkennt Burstabschlüsse am Zeilenzuwachs der
Zieltabelle, damit die Steuerung nicht selbst konkurrierende Seiten-Waits
erzeugt. Der Kettenleser hält das markierte Fenster mit fünfzig Millisekunden
Pause nach jeder Blattseitenprobe offen, ohne zusätzliche Schreiblast zu
erzeugen.

CI führt pro Build höchstens drei vollständige, voneinander getrennte Versuche
mit identischen Grenzen aus. Ein Build-Job besteht, sobald mindestens ein
Versuch beide Bursts vollständig nachweist; `NOT_PROVEN`-Versuche und ihre
Cleanup-Ausgaben bleiben im Kurzzeit-Artefakt sichtbar. Besteht keiner der
drei Versuche, schlägt der Job fehl. Das prüft, dass der Beleg auf dem Build
erreichbar ist, und behauptet keine deterministische Erfolgsquote.
