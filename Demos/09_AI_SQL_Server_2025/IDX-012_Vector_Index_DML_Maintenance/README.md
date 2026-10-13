# IDX-012 – Begrenzte DML-Grenzenvorstufe

Stand: 2026-10-11. Öffentliche Implementierungsvorstufe aus TSK-006/DEC-074,
keine freigegebene Demo, kein manifest.json und keine TP-PERF-Abnahme.
Der [kanonische Ausführungsstand](../../../Documentation/Project_Planning/CURRENT_EXECUTION_STATUS.md)
enthält die konkrete weitere lokale Wellenfreigabe, Budgets und Checkpoints.

Lernziel: gültige DML-Operationen vor Indexbau von tatsächlich verweigerten
Operationen am festen lokalen Indexprofil unterscheiden. Generation bleibt
UNKNOWN; weder eine Herstellerbeschreibung noch Fehler 42231 beweist eine
numerische Indexgeneration. Freshness und Storage sind weitere eigene Schritte.

## Voraussetzungen und Grenzen

- SQL Server 2025 Developer, tatsächlich 17.0.5005.3, Linux, CL 170;
  eigener isolierter Testcontainer mit vier CPUs/sechs GiB.
- Eigene DB SQLPERF_LAB_IDX012_<16HEX> mit vollständigen FWK-002-Markern,
  synthetische float32 VECTOR(3)-Rows und clustered INT-PK.
- YELLOW: beide expliziten Isolations-/High-Impact-Bestätigungen erforderlich.
  Nur eigene PREVIEW_FEATURES/MAXDOP, mit tatsächlich persistierten Baselines
  und getrennten Enable-, Restore- und Attestationsclients. Keine zusätzliche
  Scoped-Option, keine Host-, Cloud-, Modell- oder ONNX-Wirkung.
- 999 Ausgangsrows; gültiger INSERT der fehlenden Id 1000 erreicht höchstens
  1000 Rows innerhalb der Transaktion. UPDATE/DELETE/MERGE betreffen Id 23.
  Sämtliche DML-Änderungen werden zurückgerollt; kein Commit geänderter Vektoren.
- Ein Arbeitsclient nach dem anderen, normales Budget 300 s; bei Provisionierung
  muss dessen tatsächliche Deadline einschließlich Startup übergeben werden.
  SQL-Recovery 20 s; lokaler Parent begrenzt SQL und Containercleanup gemeinsam
  auf 60 s. Dateien/Log bleiben gemäß eigenem Setup begrenzt; kein Cacheflush/Pull.
- Der vorläufige Setup-/Prüfkontext verwendet sa im eigenen Container.
  Minimalrollen- und Hard-Abort-Abnahme bleiben offen.

## Eingeschränkter Ausführungskontext

Der eigene Operator benötigt für DB-Erstellung und Performance-DMVs
CREATE ANY DATABASE und VIEW SERVER PERFORMANCE STATE; er wird Owner
seiner eigenen Testdatenbank. Der Preflight hält bei fehlenden Rechten vor
Setup mit SKIP_PERMISSION an. Keine automatische Grantvergabe.
Im bestätigten eigenen Lab kann dessen Admin die beiden Rechte einem eigenen
vorbereiteten SQL-Login gewähren:

```sql
GRANT CREATE ANY DATABASE TO [LabDemoLogin];
GRANT VIEW SERVER PERFORMANCE STATE TO [LabDemoLogin];
```

Der tatsächliche erste vollständige Operatorlauf scheiterte am Indexbuild:
2571 wegen internen DBCC TRACEON, anschließend 42234. Beide einzeln
entzogenen Rechte, Setup, Kosten-BEFORE, vier NO_INDEX-DML-Kontrollen und
vollständiger DB-/Login-/Containercleanup sind belegt. Für den unveränderten
vollständigen CLI-Pfad bleibt daher der eigene sa-Kontext erforderlich.
Passwörter ausschließlich als SQLCMDPASSWORD-ENV bereitstellen. Der
[Rollennachweis](../../../Documentation/Project_Planning/SQL_SERVER_2025_AI_IDX012_ROLE_REVIEW.md)
belegt nach zwei erhaltenen FAIL-Kandidaten mit zwei vollständigen C3-
Lifecycles im selben erweiterten Ledger die feste lokale Trennung: ausschließlich die beiden Indexbuilds unter Admin, DML und
Beobachtung vor/nach ihnen unter tatsächlich attestiertem Operator. Dies ist
ein begrenzter lokaler Nachweis mit eigener literaler Eingabe; der neue feste öffentliche
Rollenmodus ist zunächst ein getrennt vorbereiteter Quellenstand.
Beide einzeln entzogenen Rechte halten tatsächlich vor Setup an; Grantrestore,
eigene Ownerbindung, acht geordnete Kontext-/SID-Records, alle DML-/Rebuild-/
Source-/Storage-/Kostenkontrollen und unabhängiger DB-/Login-/Containercleanup
bestanden. Öffentliche Ergebnisse bleiben WARN/Generation UNKNOWN,
runtime_qualification NOT_ESTABLISHED. Beide tatsächlichen FAILs bleiben erhalten.
Keine Behauptung der absolut kleinsten möglichen Rechtekombination.

## Ausführung und Ergebnis

Der öffentliche Controller führt keine Provisionierung und beim Import kein SQL
aus. Der Aufrufer stellt SQLCMDPASSWORD ausschließlich als Umgebung bereit.
Passwörter gehören weder in CLI-Argumente noch Quelltexte oder PRs.

```powershell
python Demos/09_AI_SQL_Server_2025/IDX-012_Vector_Index_DML_Maintenance/run_profile.py --server localhost,1433 --username sa --run-token ABCDEF0123456789 --confirm-isolated-lab --high-impact-confirmed
```

Die eigene Ziel-DB darf vor Setup nicht vorhanden sein. Der Beispieltoken ist
synthetisch; der Aufrufer vergibt einen neuen eigenen vollständigen Token.
Die Phasen verwenden die öffentlichen Framework-APIs build_sqlcmd_command,
start_sqlcmd und collect_process. -y 0 ohne -W/-h schützt vollständige begrenzte
JSON-Spalten; diese begründete FWK-010-Abweichung besitzt eigene Gegenproben.

1. 00_Preflight prüft die feste Version/Edition, Berechtigung, eigene Zielnamen
   und Bestätigungen vor Setup. Nicht passende Versionen bleiben SKIP vor Setup;
   tatsächliche 2019-/2022-Lifecycles dieses neuen Scopes sind noch offen.
2. 10_Setup erstellt ausschließlich eigene DB/Marker und persistiert tatsächlich
   Preview/MAXDOP. Separate Clients prüfen vollständige Snapshots vor/nach Enable.
3. 20_Baseline erzeugt 999 deterministische Vektoren, persistiert alle Quellbytes
   und Exact-Oracle. Der Client prüft sämtliche Vektoren und Cosinedistanzen
   unabhängig, in zehn begrenzten Quellenblöcken, letzter Block mit 99 Rows.
4. 30_DmlBoundary führt die vier festen Operationen zuerst ohne Vektorindex aus:
   jeweils eine tatsächliche Änderung, erwartete Rowzahl und übrige Quellbytes
   müssen vor Rollback stimmen. Dann wird ausschließlich der eigene DiskANN/
   COSINE-Index gebaut; Buildzeit und vollständige Indexmetadaten werden erfasst.
   Dieselben vier gültigen Operationen müssen tatsächlich 42231/State 1 liefern.
   Vollständige Quellbytes, gesicherte Transaktionswerte vor JSON und vollständige
   Indexmetadaten müssen nach jedem Rollback unverändert sein. Andere Resultate
   sind FAIL; ihre tatsächlichen Rohdatensätze bleiben beim lokalen Parent erhalten.
5. 40_SourceAfter liest über eine neue Verbindung alle 999 tatsächlichen Vektoren/
   Distanzen und vollständige Indexmetadaten. Der Controller vergleicht sämtliche
   Vektortexte und Metadaten exakt mit der vorherigen eigenen Aufnahme.
6. 90_Restore, 91_AttestDrop und 92_Absence verwenden getrennte neue Clients:
   tatsächlich beide Optionen restaurieren, unabhängig vor Drop attestieren,
   markergebunden eigene DB entfernen und separat DB-Abwesenheit bestätigen.

Bei erfülltem technischen Vertrag bleibt WARN_OPTIONAL_EVIDENCE_SKIPPED wegen
Generation UNKNOWN und fehlender vollständiger Demoabnahme. Ein Ergebnisfehler
stoppt den normalen Pfad; Recovery läuft in finally. Fehlende Baselines dürfen
nicht geraten werden; ein fehlender tatsächlicher Restore verhindert den Drop
im SQL-Controller. Bei Abbruch müssen die drei Recoveryphasen mit demselben
vollständigen Token und tatsächlich erfasster OriginalPreview in derselben
Reihenfolge ausgeführt werden. Der lokale Parent bestätigt zusätzlich seine
vollständige eigene CID-/Image-/Label-/Ressourcenbindung und Containerabwesenheit.

Kein allgemeiner DML-/Freshness-/Indexgenerationsbeweis, keine Benchmarkserie,
kein ANN-Geschwindigkeitsvorteil und keine vollständigen Build-/Storagekosten.
Der [konkrete Runtimebefund](../../../Documentation/Project_Planning/SQL_SERVER_2025_AI_IDX012_DML_BOUNDARY_REVIEW.md)
belegt nach unabhängigem Quellenreview zwei vollständige eigene Lifecycles:
je vier erfolgreiche Kontrollen ohne Index und vier tatsächliche Verweigerungen
42231/State 1 mit Index, vollständige Quellen-/Metadatenprüfung und Cleanup.
Generation UNKNOWN, Freshness NOT_TESTED und Runtimequalifikation NOT_ESTABLISHED
bleiben erhalten; keine vollständige Demoabnahme.

## Tests, Quellen und Traceability

Der getrennte Modus `--mode drop-rebuild` führt nach den unveränderten DML-
Kontrollen zusätzlich 50_DropRebuild und eine neue vollständige Quellenaufnahme
aus. Er entfernt ausschließlich den eigenen Index, ändert genau Id 999 dauerhaft
auf VECTOR(3) [1,0,0] und baut denselben eigenen DiskANN/COSINE-Index neu auf.
Fünf tatsächliche Suchkontrollen prüfen Baseline-Exact/ANN, Exact nach Änderung
ohne Index und Exact/ANN nach Rebuild gegen sämtliche tatsächlichen 999 Distanzen.
Id 999 darf vorher nicht Top-5 sein und muss anschließend distanzgeprüfter Top-1
mit Distanz null sein; ANN-Recall@5 muss in den beiden festen Aufnahmen 1 betragen.
Ein neuer Client prüft alle übrigen 998 Vektortexte unverändert und vollständige
Rebuildmetadaten. Der Default bleibt `dml-boundary` ohne dauerhafte Änderung.
Freshness ist dabei ausschließlich OBSERVED_AFTER_REBUILD_ONLY; keine allgemeine
Updateunterstützung, laufende Indexaktualisierung oder neue numerische Generation.
Dieser zusätzliche Modus benötigt seinen eigenen Quellen-/Runtimebefund;
frühere DML-Läufe attestieren ihn nicht.
Der [Rebuildcheckpoint](../../../Documentation/Project_Planning/SQL_SERVER_2025_AI_IDX012_REBUILD_REVIEW.md)
erhält zwei tatsächliche FAILs und belegt anschließend beide vollständig
abgeschlossenen Compile-Lifecycles: tatsächlicher Drop, Commit exakt Id 999,
fünf distanzgeprüfte Suchkontrollen, Recall@5 1, vollständige neue Quellen-/
Metadatenprüfung sowie Restores/DB-/Containerabwesenheit. Freshness ausschließlich
OBSERVED_AFTER_REBUILD_ONLY; vollständige Runtimequalifikation NOT_ESTABLISHED.

```powershell
python Tests/Static/test_idx012_profile.py
python Tests/Static/test_idx012_dml_boundary.py
python Tests/Static/test_idx012_lifecycle.py
python Tests/Static/test_idx012_storage.py
python Tests/Static/test_idx012_costs.py
```

Diese synthetischen Offlineprüfungen attestieren keine SQL-Runtime. Aktuelle
Head-/Main-Gates und Cleanup bleiben zusätzliche Integrationspflichten.
Quelle SRC-077:
[CREATE VECTOR INDEX](https://learn.microsoft.com/en-us/sql/t-sql/statements/create-vector-index-transact-sql?view=sql-server-ver17),
Abruf 2026-10-11. Herstellerdokumentation unterscheidet frühere und neuere
Indexformate; ihr aktueller DML-Pfad wird nicht auf diesen festen Build übertragen.
Projektprofil: DEC-074; Traceability: IDX-012, CUR-019/CUR-020, TSK-006,
FWK-001–005/008–012, TP-RUN/TP-PERF. Abweichung: vollständige CLI-JSON-Spalten
über -y 0; alle noch fehlenden Abnahmen bleiben ausdrücklich offen.

## Optionale vollständige DB-Speicheraufnahme

Zusätzlich --mode drop-rebuild --capture-storage erfasst drei neue read-only
Katalogaufnahmen nach Baseline, erstem Indexbau und Rebuild. Der Default führt
keine Speicheraufnahme aus; --capture-storage ohne drop-rebuild wird vor jedem
SQL-Aufruf abgewiesen. 22_Storage.sql bindet Marker, Baselines, Optionen und
Stage vollständig; der Client prüft eigene DB/Token/Fixture, tatsächliche 999
Rows, Indexcounts 0/1/1, Transaktionswerte 0/0 und sämtliche begrenzten Datei-,
internen Tabellen- und Partitionsrows. Überschrittene Grenzen sind FAIL statt
Trunkierung. FILEPROPERTY null, fehlender Wert und gemessene null Seiten bleiben
verschieden; DMV-row_count ist APPROXIMATE. Seitenwerte haben 8192 Bytes.

Dies sind DB-weite Punktaufnahmen einschließlich der zwischenzeitlichen DML-
Kontrollen und des Drop-/Commit-/Rebuilds. Sie beweisen keine isolierten Index-
oder Buildkosten. Indexstorageattribuierung NOT_ESTABLISHED, Writes-/TempDB-/
Worker-Kosten NOT_CAPTURED. Der [Speichernachweis](../../../Documentation/Project_Planning/SQL_SERVER_2025_AI_IDX012_STORAGE_REVIEW.md)
führt genaue Methode, Primärquellen, Budget, Review und tatsächlichen Laufstand.
Die erste zusätzliche Runtimeaufnahme scheiterte vor Indexbau am Grenzguard;
Originalrestores und eigener Cleanup bestanden. Das Budget ist geschlossen.
Die getrennte Capturefolge mit tatsächlichen Guardwerten
lieferte anschließend 199 Baselinepartitionen bei Limit 128; Transaktion 0/0,
43 interne Tabellen und zwei Dateien. Auch dieser FAIL ist geschlossen mit
beiden Restores und eigenem Cleanup. Eine getrennte Katalogfolge begrenzt die
vollständige Aufnahme auf 512 Partitionen/120000 UTF-16-Bytes; beide Grenzen
gelten gleichzeitig, ein größerer Datensatz bleibt FAIL. Übrige Grenzen
unverändert. Danach bestanden zwei vollständige eigene Katalog-/DML-/Rebuild-
Lifecycles mit drei Aufnahmen je Lauf: 199/203/203 vollständige Partitionen,
43/45/45 interne Tabellen, tatsächliche Restores 0/0 und unabhängiger eigener
Cleanup. Alle Scalars bleiben unter 120000 UTF-16-Bytes und Clientbreite 65535.
Isolierte Indexkosten und vollständige Runtimequalifikation bleiben offen. Der Guardrecord
STORAGE_GUARD ist keine vollständige Speicheraufnahme und ersetzt keine Prüfung.

## Kontrollierte Fehler- und Recoveryfälle

Die feste Python-API-Option fault='after_setup' oder fault='after_index_build'
prüft kontrollierte FAIL_EXECUTION-Fälle. Der Buildfehler wird erst nach
geprüftem Index, Snapshot und unabhängiger vollständiger Quellen-/Distanz-
kontrolle ausgelöst; der Tag lautet AFTER_INDEX_BUILD_AND_SOURCE_CHECK.
Rebuild wird dabei nicht begonnen. Danach müssen tatsächliche Original-
restores, neue Attestation vor markergebundenem Drop und DB-Abwesenheit
bestehen. Ein früherer Fehler erfüllt diesen kontrollierten Fall nicht.
Der [Recoveryvertrag](../../../Documentation/Project_Planning/SQL_SERVER_2025_AI_IDX012_RECOVERY_REVIEW.md)
begrenzt vier feste eigene serielle Fälle sowie Quellenreview und Budget.
Alle vier festen Fälle desselben stabilen Kandidaten bestanden auf tatsächlichem
17.0.5005.3: erwartetes FAIL_EXECUTION mit vollständigen Originalrestores 0/0,
neuer DB-Abwesenheit und eigener vollständiger CID-/Namensabwesenheit.
Die öffentlichen Ergebnisse bleiben FAIL; der Parent attestiert den Fehlerfall
samt Recovery, keine vollständige Demoabnahme.
Default unverändert; Hard-Abort und Minimalrollen bleiben zusätzlich offen.

## Optionale tatsächliche Phasenkosten

Der dritte qualifizierte Kandidat für `--mode drop-rebuild --capture-storage
--capture-costs` nimmt vor/nach vollständigen DML-/Rebuildphasen rohe Session-,
TempDB- und eigene DB-Dateicounter auf. Beide Punkte jeder Phase kommen aus
derselben Verbindung. Der Controller assembliert ausschließlich feste
öffentliche Quellen mit vier GO-Grenzen in einer einzelnen eigenen
temporären SQL-Datei unter Runtime, höchstens 160000 UTF-8-Bytes.
Die ursprüngliche Arbeitsphase steht einmal, der Kostenframe zweimal in
der Eingabe. Native :r-Dateinamenauflösung entfällt. Die eigene Datei wird
nach bestätigt beendetem Client auch bei Fehler entfernt. Ungeklärtes
Prozessende erhält die Datei und meldet FAIL_CLEANUP. Geerbtes SQLCMDINI wird entfernt.
Eigene Executoradapter verwenden execution_input(command) und
client_environment(command, environment). Default und bestehende
Storage-/Drop-/Rebuildmodi bleiben verfügbar. Kosten ohne expliziten
Storage-/Rebuildmodus oder nichtboolesche Optionen werden vor SQL abgewiesen.

Session-writes bedeutet Dirty-Page-Markierungen, keine tatsächlichen Datei-
Writes. TempDB umfasst abgeschlossene Tasks derselben Session ohne IAM und
laufende Tasks. Datei-Writes/-Bytes/-Stallzeit gehören allen Writern der eigenen
DB zwischen zwei Punkten einschließlich Hintergrundarbeit. Fehlend/null/Reset
sind FAIL; gemessene null bleibt null. Die Phasen enthalten Kontrollen,
Beobachtung und Instrumentierung; isolierte Indexbaukosten und vollständige
Worker-/TP-PERF-Abnahme bleiben NOT_ESTABLISHED.

Der [Kostennachweis](../../../Documentation/Project_Planning/SQL_SERVER_2025_AI_IDX012_COST_REVIEW.md)
bindet Primärquellen, Quellenreview und tatsächlichen Laufstand. Die ersten
beiden Kandidaten scheiterten vor Kosten-SQL an nativen Clientpfaden;
beide Originalrestores und unabhängiger eigener Cleanup bestanden. PR 177
integrierte die damalige Sperre vollständig. Die ausdrückliche
Benutzererweiterung erlaubt jetzt sechs Kandidaten/höchstens zwölf serielle
eigene Container im selben Ledger einschließlich C1/C2. Kein Reset und kein
unveränderter Fehlversuch. C3 bestand danach zwei vollständige eigene Lifecycles auf 17.0.5005.3
mit tatsächlichen Session-/TempDB-/Dateikostenpunkten, allen DML-/Rebuild-
Kontrollen, Originalrestores 0/0 und unabhängiger DB-/CID-/Namensabwesenheit.
Temporäre Eingabedateien sind entfernt. Session CPU DML 1676/1650 ms,
Rebuild 1142/1083 ms; alle Werte umfassen ganze Phasen samt Kontrollen.
Der Kostennachweis erhält die einzelnen Dateidifferenzen und Grenzen;
eine Manifest-/Demo-/TP-PERF-Freigabe ist damit nicht verbunden.


## Begrenzter Containerabbruch nach fertigem Index

Der [eigene Containerabbruch](../../../Documentation/Project_Planning/SQL_SERVER_2025_AI_IDX012_HARD_ABORT_REVIEW.md)
bestand zweimal auf identischem 17.0.5005.3-Quellstand: tatsächlicher SIGKILL
erst nach qualifiziertem Index-/Source-/Snapshotcheckpoint und beendetem
Arbeitsclient, tatsächlicher Exit 137 ohne OOM, neuer Start desselben gebundenen
CID und neue Readiness. Neue read-only Clients bestätigten den vollständigen
identischen Snapshot samt persistierter Originalbaseline und alle 999
Vektortexte/Distanzen/Indexmetadaten. Tatsächliche Originalrestores 0/0,
markergebundener Drop und neue DB-/CID-/Namensabwesenheit bestanden innerhalb
derselben 60-s-Deadline ab vor Kill. Öffentliche kontrollierte FAILs bleiben
FAIL; der Parent attestiert nur diesen eigenen Containerabbruch mit Recovery.
Abbruch während aktiver Build-/DML-/Rebuildphase und vollständige
Hard-Abort-/Runtime-/TP-PERF-Abnahme bleiben offen.

## Fester öffentlicher Rollenmodus: Quellenstand

DML und Indexbau benötigen in diesem festen Profil unterschiedliche Rechte.
Der ausdrücklich gewählte Modus `operator-admin-build` erhält deshalb die
Kostenphasen als jeweils einen Client und eine Session. Sie starten mit dem
gehaltenen Adminlogin `sa`, wechseln sofort zum festen Operator und kehren nur
für den einen eigenen Indexbuild zu `sa` zurück. Danach folgt derselbe Operator.
Alle übrigen Phasen authentifizieren direkt als Operator. Dies ist keine
Aufteilung von BEFORE/Build/AFTER auf verschiedene Verbindungen.

Der Modus verlangt `drop-rebuild`, Storage und Kostenaufnahme. Operatorname ist
`SQLPERF_IDX012_ROLE_<RUN_TOKEN>`; vollständige gehaltene Operator-SID (16 Bytes)
und tatsächliche Admin-SID werden mit `--role-sid`/`--admin-sid` gebunden.
Es gibt keinen geratenen Admin-SID-Default. Der Aufrufer benötigt bereits die
beiden eigenen vorbereiteten Identitäten im isolierten Lab. Loginanlage und
Rechtevergabe gehören nicht zu dieser API.

`IDX012_OPERATOR_PASSWORD` enthält ausschließlich privat das Operatorcredential,
`SQLCMDPASSWORD` das Admincredential. Beide müssen unterschiedlich sein und aus
40–80 ASCII-Buchstaben/Ziffern beziehungsweise `!` bestehen. Die neue Auswahl
setzt pro Client ausschließlich das passende SQLCMDPASSWORD; keine Passwörter
als Argument, Connectionstring oder Quelldatei. SQLCMDINI und fremde ENV-Werte
werden nicht übernommen. Fehlende/widersprüchliche Rollenparameter, andere
Ziele als eigenes Loopback und freie Executor-/Ordneroverrides werden abgewiesen.
Ohne Rollenmodus bleiben die bisherigen Ein-Kontext-Aufrufe bestehen.

Je Kostenphase prüfen vier geordnete Records Operatorstart, Adminbuild,
Operatorrückkehr und Operatorende. Vollständige Login-/SID-/OriginalLogin-/
Privileg-/DB-/Sessionbindung muss zu beiden Kostenframes passen. DML-, Rebuild-,
Marker-, Source- und Restoreoracles bleiben erforderlich. Die Kosten und Buildzeit
enthalten Rollenwrapper und Attestation; sie sind keine isolierten DDL-/Workerkosten.

Der APIresult erhält nur nach Credentialprüfung sichere tatsächliche Clientkanäle
und Input-/Sourcebindungen; diese vollständigen Records bleiben privat. Die CLI
meldet begrenzte Status-/Phasen-/Contextcounts. Unbestätigtes Clientende bleibt
UNKNOWN, kein weiterer SQL- oder Principalcleanup; eigene Recoveryeingaben bleiben
erhalten. Ein bekanntes Prozessende ist kein Server-/TDS-Endbeleg.

Dieser neue öffentliche Modus ist SOURCE_ONLY und besitzt noch keinen eigenen
Nativenachweis. Die historischen zwei Rollenlifecycles qualifizieren ihn nicht
nachträglich. Kein absoluter Minimalrollen-, allgemeiner Runtime-, Demo- oder
TP-PERF-PASS. Der konkrete [Rollen-API-Vertrag](../../../Documentation/Project_Planning/SQL_SERVER_2025_AI_IDX012_ROLE_API_REVIEW.md)
enthält Abnahmegrenzen und den erforderlichen eigenen Folgeentscheid.
