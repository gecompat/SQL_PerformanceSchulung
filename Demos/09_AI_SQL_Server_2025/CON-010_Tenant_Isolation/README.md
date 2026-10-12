# CON-010: Tenant-Isolation vor dem Vektorkontext

Status: IMPLEMENTED; lokale Consumer-/Versions-/Cleanupqualifikation PASS.
Aktuelle PR-/Main-Gates werden im zugehörigen PR nachgewiesen.
GREEN, eine Session, SQL Server 2025 (17.x), Kompatibilität 170; 2019/2022 liefern
SKIP_VERSION vor Setup. Kein Modell-, Provider- oder Cloudaufruf, kein ANN-Index.

Zwei synthetische Dokumente mit identischem VECTOR(3) erlauben dieselbe exakte
Cosine-Abfrage. RLS in `sec` bindet Tenant 1/2 an die WITHOUT LOGIN Benutzer
CON010_TenantA/B. CON010_Unmapped erhält keine Zeile. Die Quellen und Vektoren liegen
gemeinsam in der geschützten Tabelle; es gibt keinen ungeschützten Vektornebenbestand.
Der privilegierte dbo-Labowner wird im eingefrorenen Prädikat ausdrücklich zugelassen,
um Fixture, Grants und Cleanup zu verwalten. Der Kontrollharness läuft ausschließlich
unter diesem Owner. Die drei Querybenutzer erhalten SELECT auf die Dokumenttabelle
und den hier tatsächlich beobachteten CONNECT-Grant auf Datenbankebene. Alle sechs
Rechte werden einschließlich Klasse, Ziel, Grantor, Zustand und vollständigen
Permissionnamen geprüft; zusätzliche Rechte und explizite Rollen sind unzulässig.

Baseline liest tatsächlich eine vollständige Quelle je Tenant. Demonstration und
Vergleich lesen dieselben vollständigen Quellen/Vektoren mit Cosine-Distanz 0 unter
den drei Benutzerkontexten. Ein manipulierbarer Sessionwert CON010_TenantId=2 ändert
Tenant A nicht. Dynamische feste SELECT-Abfragen prüfen auch die SELECT-Rechte ohne
Eigentumsketten-Bypass. Policy-ALTER, fremde Impersonation und SELECT nach Owner-Revoke
müssen tatsächlich scheitern; der Grant und Sessionkontext werden auch im Fehlerpfad
zurückgesetzt. Vorher/nachher werden vollständige Fixturebytes, Funktionsdefinition,
aktive Policybindung und die sechs festen CONNECT-/SELECT-Grants geprüft.

Die erwarteten Metriken sind 2 Baselinezeilen, 2 erlaubte Quellenkontexte, 0 fremde
Zeilen, 3 Rechteverweigerungen, 0 Zeilen nach Revoke und 1 geprüfter Kontextreset.
Leere Ergebnisse ersetzen keine positiven Belege. Vier bytegenaue Eigentumsmarker
binden jede Phase und Cleanup ausschließlich an SQLPERF_LAB_CON010_<RunToken>.

Dieser Slice belegt EXECUTE AS-Kontextwechsel innerhalb einer Session. Serverlogins,
echtes Verbindungspooling, mehrere Sessions, ANN/Postfilterverhalten und allgemeine
Seitenkanalfreiheit bleiben UNQUALIFIED. Er behauptet keinen Schutz vor dem
privilegierten Owner und keine Modell- oder Prompt-Injection-Sicherheitsabnahme.
RLS filtert auch dbo, sofern die Policy ihn nicht ausdrücklich zulässt; siehe
[Microsoft RLS](https://learn.microsoft.com/en-us/sql/relational-databases/security/row-level-security?view=sql-server-ver17).

Ausführung: [FWK-010 Leitfaden](../../../Documentation/HowTo/DEMO_EXECUTION_GUIDE.md),
`manifest.json` und [Ergebnisvertrag](Expected/result-contract.json).
Abhängigkeiten: FWK-001 bis FWK-012; CUR-018/TSK-009.

## Voraussetzungen, Ressourcen und Abbruch

Die Demo benötigt den klassischen SQL Server Database Engine mit EngineEdition
2, 3 oder 4, primär Enterprise Developer, unter Linux oder Windows. Der
Kontrollbenutzer muss die eigene Datenbank anlegen und als dbo verwalten können;
die drei Querybenutzer besitzen ausschließlich die sechs beschriebenen Grants.
Sie sind WITHOUT LOGIN und werden per EXECUTE AS in einer Session geprüft.
Es wird keine minimale Serverloginrolle oder echte Verbindung authentifiziert.

Das kleine deterministische Datenprofil besteht aus zwei Rows und VECTOR(3).
Die eigene Datenbank wird auf CL 170, SIMPLE, AUTO_CLOSE/AUTO_SHRINK OFF gesetzt;
Dateigrenzen sind 256 MiB Data und 64 MiB Log, Growth jeweils 16 MiB. Keine
Instanzoption wird geändert. Reguläres Manifestbudget 180 s, einzelne Phase
höchstens 60 s, separates Cleanupbudget 60 s. Der lokale Entwicklungsnachweis
verwendet vier CPUs/sechs GiB für die isolierte Instanz; dies ist ein getestetes
Ressourcenprofil, keine vermessene Hardwareuntergrenze. Diese Demo erhebt
keinen Performanceclaim oder TP-PERF-Nachweis.

Bei Fehler stoppt FWK-010 die Folgephasen und versucht nach gestartetem Setup
das markergebundene Cleanup. Nach manuellem Abbruch genau dieselben Demo-/Run-/
Zielwerte aus dem Leitfaden für 90_Cleanup.sql verwenden und Abwesenheit prüfen.
Fehlende oder abweichende Marker dürfen nicht überschrieben werden, um eine
Datenbank dennoch zu löschen. Sessionkontext und temporärer SELECT-Revoke
werden im nativen Fehlerpfad zurückgesetzt; Serverlogins/Pooling bleiben offen.

Der [begrenzte private Wiederaufnahmenachweis](../../../Documentation/Project_Planning/SQL_SERVER_2025_AI_TENANT_RESUME_REVIEW.md)
bewahrt drei historische FAILs, den C4-Kollations-FAIL und zwei stabile C5-Läufe.
Quellen: Microsoft Learn RLS (SRC-093) und
[sys.database_permissions](https://learn.microsoft.com/en-us/sql/relational-databases/system-catalog-views/sys-database-permissions-transact-sql?view=sql-server-ver17),
Abruf 2026-10-12. Der [öffentliche Consumer-/Versionsnachweis](../../../Documentation/Project_Planning/SQL_SERVER_2025_AI_TENANT_IMPLEMENTATION_REVIEW.md)
belegt 192 Markerabweisungen über alle acht Phasen, 16 tatsächliche Fixture-
manipulationen je gegen Baseline/Comparison, Setupidempotenz und je zwei
2019-/2022-SKIPs vor Setup. Ein wirkungsloser erster Spaltengrant-Test blieb
FAIL; Spalten-DENY und tatsächliche Snapshotänderung qualifizierten C2.
Die anschließende öffentliche CI zeigte einen PRINT-/stderr-Fehler im
Consumer. C3 qualifizierte den Diagnostikkanal, scheiterte anschließend an
einer eingefrorenen gemeinsamen API-Abhängigkeit. C4 stellt die gemeinsame
API wieder her und projiziert nur die feste positive Consumersummary als
SELECT; alle Gegenproben mit tatsächlichem `sqlcmd -r 1` bestanden. Beide
CI-FAILs bleiben sichtbar. Alle 20 eigenen Qualifikationscontainer und ihre
Datenbanken sind abwesend.

## Schritt-für-Schritt-Anleitung

1. Eine freigegebene Testinstanz und `SQLCMDPASSWORD` gemäß Leitfaden wählen.
2. Die Demo manifestbasiert mit `python Demos/00_Framework/Tools/run_demo.py Demos/09_AI_SQL_Server_2025/CON-010_Tenant_Isolation/manifest.json` und den dokumentierten Zielargumenten ausführen.
3. Zwei vollständige positive Quellenkontexte, leeren unmapped Kontext und tatsächliche Rechtefehler prüfen; SKIP/WARN/FAIL sichtbar lassen.
4. Markergebundenes Cleanup und unabhängige Abwesenheit der eigenen Zieldatenbank prüfen.
