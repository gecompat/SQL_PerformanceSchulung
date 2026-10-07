# DGN-007 – Quellen- und Ausführungspfadprüfung der Voraussetzungen

| Merkmal | Wert |
|---|---|
| Status | `PROJECT_SEMANTIC` – geprüfte Quellen-/Codeabgrenzung, Voraussetzungen weiterhin offen |
| Stand und Quellenabruf | 2026-10-07 |
| geprüfte Repositorybasis | `57e4c7faf9c3d3ec17d7f98d430ebf5c5dd18712` nach PR71 |
| Arbeitspaket | bestehender automatisierter DGN-007-Schnitt |
| Gegenstand | sechs Voraussetzungen des [deklarativen Modells](DGN_007_ASSIGNMENT_PREREQUISITES_MODEL.md) und des [Methodenentwurfs](DGN_007_CAPTURE_ASSIGNMENT_DESIGN.md) |
| Abnahmegrenze | Primärquellen, tatsächlich gelesener Codepfad und unabhängiger Review; keine neue SQL-Runtime oder Methodenentscheidung |

## 1. Ergebnis und Aussagebasis

Die sechs Modellannahmen sind durch den vorhandenen Pfad noch nicht vollständig
belegt. Der Harness prüft tatsächliche eigene Phasen, Requests, Ergebnisse und
ersten Cleanupabschluss. Er liefert jedoch keinen vollständigen Herkunftsbeleg
für die vorgeschlagene kontrollierte Kollektivzuordnung. Dokumentierte
Query-Store-Eigenschaften erlauben die weitere Ausarbeitung eines begrenzten
Nachweispfads; aus den offenen Voraussetzungen folgt keine allgemeine
Unmöglichkeit.

`DOKUMENTIERT` bezeichnet unten Microsoft-Primärquellen, `CODEBEFUND` den Stand
der oben gebundenen Repositorybasis. `INFERENZ` benennt die daraus hergeleitete
Grenze. Ein künftiger Recordvorschlag ist `PROPOSED` und attestiert heute nichts.
Es wurden keine SQL-Prozesse, Container oder neuen Ressourcen gestartet.

## 2. Dokumentierte Eigenschaften und ihre Grenzen

| Primärquelle | unmittelbar dokumentiert | Grenze für diesen Entwurf |
|---|---|---|
| [ALTER DATABASE SET Options](https://learn.microsoft.com/en-us/sql/t-sql/statements/alter-database-transact-sql-set-options?view=sql-server-ver17) | Statements innerhalb Stored Procedures werden unter `ALL`, `AUTO` und `CUSTOM` erfasst. `NONE` erfasst keine neuen Queries, sammelt aber weiter für bereits erfasste Queries. Normales QS-OFF hat einen synchronen Flush; `FORCED` überspringt ihn. | Ad-hoc-AUTO-Schwellen erklären keine ignorierten `usp_CaseSearch`-Vorabrequests. OFF wäre eine andere Zustandsoperation, keine im bestehenden READ_WRITE-Pfad vorhandene Stagebarriere. |
| [How Query Store collects data](https://learn.microsoft.com/en-us/sql/relational-databases/performance/how-query-store-collects-data?view=sql-server-ver17) | Kompilierung liefert Query-/Planinformationen; Ausführung liefert Runtime-Statistiken für das aktive Intervall. Persistenz erfolgt asynchron. Lesen vereinigt Memory und Disk transparent. Terminierte/abgebrochene Sessions sowie Clientneustart/-absturz können die Statistikerfassung verhindern. | Asynchrone Persistenz darf nicht als dokumentierte asynchrone Publikation nach erfolgreichem Requestabschluss ausgegeben werden. Reguläres erfolgreiches Verbindungsende wird hier nicht als Verlustmechanismus behauptet. Eine maximale Publikationslatenz oder vollständige historische Familienabschlussquittung wird nicht zugesagt. |
| [Runtime-Statistiken](https://learn.microsoft.com/en-us/sql/relational-databases/system-catalog-views/sys-query-store-runtime-stats-transact-sql?view=sql-server-ver17) | Aktive Gruppen können mehrere Disk-/Memory-Zeilen besitzen; nach Plan, Intervall und ExecutionType aggregieren. Type `0` bedeutet erfolgreich beendet. First/Last sind Ausführungs-Endzeiten. | Korrekte Aggregation ist erforderlich, beweist aber allein weder vollständige Herkunft noch kohärente Aufnahme aller Familien-/Plan-/Runtime-Views. |
| [Intervallkatalog](https://learn.microsoft.com/en-us/sql/relational-databases/system-catalog-views/sys-query-store-runtime-stats-interval-transact-sql?view=sql-server-ver17) | ID, Start, Ende und stets NULL als Kommentar. | Kein dokumentiertes Active-, Sealed- oder Complete-Feld. Kataloggrenzen liefern keine eigene Abschlussquittung. |
| [sp_query_store_flush_db](https://learn.microsoft.com/en-us/sql/relational-databases/system-stored-procedures/sp-query-store-flush-db-transact-sql?view=sql-server-ver17) | Schreibt den In-memory-Anteil auf Disk; Returncode `0`/`1`. | Keine dort zugesagte Request-Watermark, versiegelte Familienmenge oder atomare historische Sicht. Flush bleibt eine Persistenzoperation. |
| [QS-Optionen](https://learn.microsoft.com/en-us/sql/relational-databases/system-catalog-views/sys-database-query-store-options-transact-sql?view=sql-server-ver17) | Tatsächlicher Zustand kann vom gewünschten abweichen; automatische READ_ONLY-/Fehlerzustände, Retention, Cleanup und Planlimits sind gesondert ausgewiesen. | Ein einzelner Zustandssnapshot belegt keine kontinuierliche Erfassung. Limits und Zustandsänderungen gehören in einen späteren Belegpfad. |
| [Monitoring Query Store](https://learn.microsoft.com/en-us/sql/relational-databases/performance/monitoring-performance-by-using-the-query-store?view=sql-server-ver17) | Neue SQL-Server-2022+-Datenbanken haben Query Store standardmäßig READ_WRITE; SQL Server 2019 aktiviert ihn standardmäßig nicht. | Defaults ersetzen keine tatsächlichen Zustandsbelege während der Vorabrequests; eine frische Datenbank bedeutet nicht versionsübergreifend OFF. |
| [Query-Variants](https://learn.microsoft.com/en-us/sql/relational-databases/system-catalog-views/sys-query-store-query-variant?view=sql-server-ver17) | Parent-, Dispatcher- und Variantbindung ab SQL Server 2022; Dispatcher besitzen selbst keine Runtime-Statistiken. | Die Familie bleibt versionsgebunden; ein später sichtbares Mitglied darf in früheren Captures nicht ohne Beleg als abwesend gelten. |

Die negativen Grenzen gelten für die hier geprüften Quellen. Sie behaupten
keine universelle Nichtexistenz einer anderen dokumentierten oder später
validierten Methode. Exakte QS/SYSUTC-Vergleichbarkeit bleibt wie im
Methodenentwurf ungeklärt; verlustfreie 100-ns-Ticks erhöhen keine Genauigkeit.

## 3. Tatsächliche Phasen- und Requestfolge

`CODEBEFUND`: [Setup10](../../Demos/07_Query_Store_Extended_Events/DGN-007_Time_Bounded_Search_Incident/Automated/10_Setup.sql)
erstellt die eigene synthetische Datenbank ohne explizites QS-OFF. Die
Suchprozedur führt das markergebundene SELECT aus und schreibt anschließend
eine datenbanklokale Request-ID mit `RequestedUtc datetime2(0)`; dieser Wert
ist kein präziser SELECT-Endzeitbeleg. Die
[Datenassertion40](../../Demos/07_Query_Store_Extended_Events/DGN-007_Time_Bounded_Search_Incident/Automated/40_Data_Assertion.sql)
führt vier Vorabrequests mit vollständigem Ergebnisvergleich aus. Ihre
Cursorquelle besitzt kein `ORDER BY`; die Parameter-Mengenbindung liefert
keine garantierte Vorabreihenfolge.

[SQL21](../../Demos/07_Query_Store_Extended_Events/DGN-007_Time_Bounded_Search_Incident/Automated/21_Controlled_Query_Store_Windows.sql)
prüft erst danach die Konfiguration (Zeilen 79–99), akzeptiert tatsächliches
OFF oder READ_WRITE und aktiviert RW/ALL (146–152). Die Pulseausführung zählt
die zwölf Gruppen; ihre Intervallwahl verwendet Kataloggrenzen und SYSUTC
(185–196, 235–247). Sie liest keine eigene RuntimeStats-Intervallzuordnung
des Pulses. T0 und T1 laufen vor dem gemeinsamen Capture (269–387).

Vor jedem Fenster markiert SQL21 die eigene Suchprozedur mit `sp_recompile`
für die nächste Neukompilierung (268). Die dokumentierte Neukompilierung
unter zuvor aktiviertem RW/ALL bereitet Query-/Planregistrierung vor;
sie liefert keine zusätzliche Sichtbarkeits- oder Abschlussquittung.
[sp_recompile](https://learn.microsoft.com/en-us/sql/relational-databases/system-stored-procedures/sp-recompile-transact-sql?view=sql-server-ver17).

Die eigenen Fensterrequests sind konkret gebunden: `INSERT #Actual EXEC`,
vollständiger bidirektionaler Ergebnisvergleich, genau eine passende neue
Requestlogzeile und tatsächlich gezählter `COUNT_BIG(#Actual)` (283–315).
[SQL35](../../Demos/07_Query_Store_Extended_Events/DGN-007_Time_Bounded_Search_Incident/Automated/35_Control_Evidence.sql)
rekonstruiert die Folge aus IDs und bindet gemessene Ergebnisse an Fenster,
Ordinal und Request-ID (308–328, 445–447). Das prüft den eigenen Callabschluss
unter intaktem ausgeführtem Code. Requestlogs zählen keine QS-Erfassung und
attestieren keine individuelle Request→Plan-Zuordnung oder externe Exklusivität.

Der Profilecapture filtert auf zwei Zielintervalle und ExecutionType `0`.
Der spätere Livevergleich und die exportierte verwendete Familie mit
Parentankern liefern keinen früheren Gesamtledger `B` über sämtliche
Familien-/Intervall-/ExecutionType-Gruppen. Ein T0-Capture vor T1 fehlt.
Das sind Lücken der vorgeschlagenen alternativen Beweisart; dieser Review
erfindet daraus keine zusätzlichen v1-Vertragsfehler.

## 4. Coordinatorgrenze des bestehenden Harness

| Bereich und tatsächlich geprüfter Code | verwendbarer Bestandteil | noch nicht attestiert |
|---|---|---|
| [Runner](../../Tests/Runtime/run_dgn007_automated_setup.py), 181–196, 507–583 | feste Manifest-/Script-/Selector-/Budgetmetadaten, geordnete Pflichtsummaries und Captureframing ausschließlich aus CONTROL_EVIDENCE/stderr, Bodyversion und MEASURED-Bindung | vollständiger geschlossener Ausführungsumfang oder Ausschluss zusätzlicher Clients |
| [Harness](../../Demos/00_Framework/Tools/run_demo.py), 214–255, 290–351 | eigene Phasen seriell; Ergebnis an Phase gebunden; monotones Hostbudget, Stop bei FAIL/Pflicht-SKIP und eigenes Cleanup | durchgehend identische SQL-Session; jede SQL-Phase nutzt eine neue Verbindung. Serieller eigener Client beweist keine Exklusivität. |
| [Quellenvalidator](../../Tests/Static/validate_dgn007_prospective_acceptance.py), 33–43; Runner 714 | statischer Vergleich von 14 tatsächlichen SQL-/Manifesthashes; Runtime lädt den erwarteten Vertrag | unveränderlicher, vor Ausführung geprüfter Runtimefreeze einschließlich ausführender Helfer. Vertragsdigests und extern ergänzte Capture-Digests sind Bindungen, keine Ausführungsattestation. |
| [CI-Workflow](../../.github/workflows/dgn007-automated-setup.yml), 126–168 | eigene rungebundene CID/Labels, vier CPU und 8 GiB als Containerlimits, keine veröffentlichten Ports oder Mounts | gemessene Host-/Ressourcenuntergrenze und physische Gesamtbelegung. Drei Versionsjobs und konfigurierbarer Runner bilden keinen Hostlock. |
| Runner 650–677; CI 260–274 | erste unabhängige DBabwesenheit; Recovery heilt deren Fehler nicht. Eigene CID wird separat entfernt und Abwesenheit geprüft. | positive Herkunft durch späteres Cleanup oder Cleanupgarantie bei harter Unterbrechung |

Fester Datenbankname und wiederverwendeter `AUTO`-Marker sind keine eindeutige
Lifecycle-/DBgeneration. Der bestehende Body enthält keine CID-/Generation-/
Block-/Slotbindung. Die SQL-Zeitbudgets verwenden SYSUTC-Wallclock; monotone
Hostbudgets und verlustfreie SQL-Ticks sind getrennte Belege.

Der Body entsteht vor Cleanup in SQL35 und durchläuft die tatsächliche
Phasen-/Kanalbindung. Der Runner decodiert die gepufferte Ausgabe nach Ende
des Kindprozesses; er liest die entfernte Datenbank nicht erneut. Die lokale,
unveröffentlichte API am Branchstand `83f08fb…` kann diesen Body mit geprüften
Phasen und erstem erfolgreichem Abwesenheitscheck erhalten. Sie ergänzt keine
Freeze-, Ressourcen-, Exklusivitäts- oder Herkunftsattestation und bleibt bis
zur G13-Messvertragsklärung zurückgestellt.

## 5. Suffizienz der sechs Modellvoraussetzungen

| Voraussetzung | Bewertung des jetzigen Pfads | vor positiver alternativer Zuordnung erforderlich |
|---|---|---|
| `execution_discipline` | eigene Calls und Phasen begrenzt; geschlossener Zugang nicht belegt | vertrauenswürdiger quellen-/zielgebundener Actor, vollständige tatsächliche Aufruf-/Statefolge und definierter exklusiver Zugang; ein Sessionlimit oder JSON-Flag genügt nicht |
| `source_and_scope_eligibility` | Proceduremarker, tatsächliche Requests und versionsgebundene Varianten vorbereitet | unveränderlicher Freeze, Generation, kontinuierliche Erfassung und vollständige tatsächliche Parent-/Variant-/Plan-/Intervall-/ExecutionType-Bindung |
| `qs_activation` | Katalog-/SYSUTC-Wahl und Pulsresultat vorhanden | QS-interner Aktivierungs-/Rotationsbeleg sowie begründete Kontinuität während aller vier Calls |
| `complete_visibility` | aktive Rows korrekt gruppiert, aber kein vollständiger früher Ledger | begründete vollständige Acquisition-/Abschlussregel, begrenzte Generation und finale Rückbindung der ganzen Familie; gleiche Polls allein genügen nicht |
| `baseline_completion` | QS-Konfiguration erst nach Vorabcalls, kein gebundener Abschluss der Basis | tatsächlicher Vorabzustand und vollständiger Abschluss/Ausschluss früherer Familienstatistik ohne nachträgliches Anpassen von `B` |
| `truthful_request_completion` | konkrete Ergebnismessung und Log-/Phasenabschluss nutzbar | quellen-/generationgebundene erfolgreiche Calls ohne Unterbrechung und spätere Bindung an den geschlossenen Scope; Logerfolg allein beweist keine QS-Erfassung |

Ein kompensierter Count ist eine **bedingte logische Gegenprobe**: Solange
Basis-, Erfassungs- oder Intervallkontinuität unbekannt sind, kann eine
zusätzliche Priorstatistik fehlende Fensterstatistik rechnerisch ersetzen.
Das behauptet keinen normalen Verlust unter belegtem kontinuierlichem
READ_WRITE/ALL und keine empirisch beobachtete Publikationsverzögerung.
Lägen ältere QS-Intervalle und deren vollständige Bilanz bereits belegt vor,
würde zusätzliche alte Statistik dort auffallen. Dieser Gegenfall ist daher
kein Beweis einer trotz erfüllter Voraussetzungen unvermeidlichen Kompensation.
Der getrennte Gegenfall eines ungeplanten Familiencalls bleibt durch reine
Count-/Metrikgleichheit ebenfalls nicht ausgeschlossen.

## 6. Nächster zulässiger Schnitt

Als Nächstes wird ein **begrenzter Beobachtungs- und Herkunftsvertrag** als
prüfbarer Entwurf ausgearbeitet, bevor ausführbare Änderungen entstehen:

1. Zustandsrecords vor/nach den unveränderten vier Vorabcalls und vor T0:
   tatsächlicher/gewünschter QS-Zustand, Capturemode, Readonlyreason, Retention,
   Cleanup-/Planlimits, Sourcefreeze, Zielgeneration und Ereignisordinal.
2. Begrenzter vollständiger Familienledger je Stage mit Plan→Query-Bindung,
   allen Intervallen/ExecutionTypes und getrennten positiven/Zero-/NULL-/
   Negativefragmenten. Finale Familie auf alle früheren Captures rückbinden;
   Counts und sämtliche Vertragsmetriken an dieselbe Generation binden.
3. Tatsächliche Call-/Ergebnis-/Abschlussfolge sowie T0-Capture vor T1 und
   konkrete vertrauenswürdige Coordinatorgrenze einschließlich Ressourcen,
   monotone Budgets und erster unabhängiger Abwesenheit.
4. Separat quellengebundener Puls mit beobachtetem positiven RuntimeStats-
   Countdelta in seinem tatsächlichen Intervall. `INFERENZ`: Das belegt
   retrospektiv Aktivität dieses Pulses, allein weder fortdauernde Aktivierung
   für Suchcalls noch Abschluss der Basis. Pollanzahl, Größen und Observerkosten
   innerhalb 180 Sekunden regulär/60 Sekunden Cleanup sind vorab zu begrenzen.

Ein tatsächlich belegter OFF-Zustand vor allen Vorabcalls und ein bereits
READ_WRITE-erfassender Zustand bleiben getrennte Zweige. `B=4` wäre nur mit
zusätzlich belegtem geschlossenem Call-/Erfassungspfad ein prüfbarer
Vollständigkeitskandidat. Weder OFF/CLEAR noch zusätzliche Suchcalls,
Warmupprofile, universelle Acht-/Zwölfersummen oder Budgetvergrößerung werden
hier beschlossen. Beobachtung allein macht keine offene Prämisse wahr.

Danach benötigt die Beweisart eine explizite Methodenentscheidung; erst eine
gemeinsam versionierte Umsetzung kann SQL21/35, Freeze, Transport, Records,
Evaluator und Coordinator verbinden. Vor Runtime sind genaue eigene
Wegwerfinstanz, Grenzen und unabhängig überprüfbarer Cleanup festzulegen.
Die Matrix bleibt 2019/150, 2022/160 und 2025/170. G13, v1, DEC-068, bisherige
FAILs und die fehlende PR68-Mergefreigabe bleiben unverändert. Incident-,
Ursachen-, Mitigations-, Capstone-, Teilnehmer- und Szenariofreigabe bleiben offen.

Der konkrete [Beobachtungs-/Herkunftsvertrag](DGN_007_OBSERVATION_PROVENANCE_CONTRACT_DESIGN.md)
liegt inzwischen als PROPOSED vor. Er bindet acht Stages, Raw-/Gruppen-/
Coverage-/Callrecords und die Coordinatorgrenze an endliche Entwurfsbounds.
Sättigung, Zustands-/Intervallkontinuität und tatsächliche Vertrauensmechanik
bleiben gezielt auf Suffizienz zu prüfen; keine Methoden- oder Runtimefreigabe.
