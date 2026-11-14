# QRY-023 – Lokale Coverage-Prüfung des Proposed Harness

| Merkmal | Wert |
|---|---|
| Prüfart | lokaler statischer Coverage-Review, nicht unabhängig |
| Geprüfte Artefakte | Proposed-Manifest, Offlinevalidator, synthetische Regressionen, SQL-Dateizuordnung |
| Laufstatus | keine SQL-, Lab- oder Runtimeausführung |
| Katalogstatus | `PROPOSED`; kein ausführbarer Runtimeeintrag |

## Befund zur Manifestbindung

Der vorhandene Validator prüfte Phase-IDs und -Reihenfolge und verlangte, dass
die jeweils angegebene Scriptdatei existiert. Er band aber eine Phase nicht an
ihre vorgesehene Scriptdatei und Zieldatenbank. Ein gültiger, aber vertauschter
Scriptpfad konnte damit den statischen Contract überstehen. Auch die globale
Laufzeitobergrenze, die Cleanup-Zielbindung an `master` und die exakte
Cleanupfrist wurden zuvor nicht gegen die im Entwurf festgelegten Werte
geprüft.

Der Validator bindet jetzt jede Phase als exaktes Tupel aus ID, Reihenfolge,
Script, Datenbank und vorgesehenem Zeitlimit. Cleanup ist fest an
`90_Cleanup.sql` in `master` mit 90 Sekunden, erforderlicher Summary und
Pflichtstatus gebunden. Das Manifest bleibt auf höchstens 900 Sekunden
reguläre Laufzeit plus 90 Sekunden Cleanup begrenzt. Fehlgeformte Phasen- und
Manifestwurzelwerte werden als Validierungsfehler gemeldet, statt den Validator
mit einem Attribut- oder Pfadtypfehler abzubrechen.

Die Regressionen decken nun falsche Script-/Datenbank-/Zeitzuordnung,
fehlerhafte Phasenrecords, nicht-objektförmige Manifestwurzel sowie veränderte
Lauf-/Cleanupbudgets ab. Der feste aktuelle Entwurf bleibt `PROPOSED` und
erfüllt diese Prüfungen.

## Befund zur Messmetrikabdeckung

Der Messlauf erfasste FWK-004-`Reads` und `Writes` bereits als Rohwerte, fasste
Median und Streuung gepaarter Differenzen aber nur für CPU, Logical Reads und
Elapsed zusammen. Die Designbeschreibung verlangte eine gepaarte
Profilzusammenfassung der erfassten Messwerte und grenzte den Overhead der
Messprozedur ein. `40_Measurement.sql` weist jetzt fehlende Reads-/Writes-Werte
zurück und nimmt beide in die fünf Metrikdeltas auf. Der Offlinevalidator
verlangt dafür die Messwertspalten in FWK-004 und die Metriknamen in der
Zusammenfassung; synthetische Gegenfälle schützen diese Bindung.

Die Reads-/Writes-Zähler bleiben FWK-004-Sessiondeltas einschließlich
Messprozedur-Overhead. Sie werden nicht als isolierte Statement- oder
I/O-Gerätemessung interpretiert.

## Aussagegrenzen und weitere Gates

Die separate Actual-Plan-Phase schaltet `STATISTICS XML` jetzt im Erfolgszweig
und in `CATCH` ab und reicht den Fehler mit `THROW` weiter. Der statische
Validator und eine Regression schützen beide Abschaltpfade. Das folgt dem
Cleanupmuster aus `Demos/00_Framework/Templates/40_Plan_Statistics_Evidence.sql`.
Es ist eine Skriptstrukturprüfung: sie belegt weder Engineverhalten bei
Verbindungsabbruch noch eine tatsächlich erfolgte Rücksetzung in einer
SQL-Session.

Die zwei Plan-`COUNT_BIG`-Statements werden jetzt in Anzahl und Reihenfolge
gegen die entsprechenden Graph- und Relationsstatements der Messprozedur
verglichen. Nach Entfernen von Whitespace, Vereinheitlichung der Großschreibung
und Normalisierung des Ausgabeziels (`@PathCount` gegenüber `PathCount`) muss
der übrige Statementtext übereinstimmen. Zwei Negativregressionen schützen die
Graphpfad- und relationale Zieljoinform. Dies bindet Skriptformen, berechnet
aber weder Ergebnisse noch beweist es die unabhängig geprüfte
Tripelgleichheit erneut.

Der Validator prüft außerdem, dass das Plan-Summary und der PASS-Print genau
einmal nach dem Erfolgszweig mit `STATISTICS XML OFF` sowie nach dem rethrowing
`CATCH` stehen. Eine Negativregression fügt beide Erfolgsausgaben vor dem
erfolgreichen Abschaltpunkt ein und muss die Datei ablehnen. Damit wird
Textreihenfolge geschützt, nicht die Wirkung einer tatsächlichen
SQL-Server-Session oder das Verhalten bei Verbindungsabbruch.

Die Summaryzeile wird nun mit den festen Statusfeldern
`PLAN_EVIDENCE`/`SUMMARY`/`PASS`/`OK` und einem korrespondierenden
`SQLPERF_SUMMARY|PASS|OK`-Marker gebunden. Gegenproben mit `WARN`-Outcome oder
abweichendem Statuscode werden zurückgewiesen. Das belegt nur das deklarierte
Skriptformat und keinen fachlichen Erfolg einer tatsächlichen Diagnose.

Beide query-shape-gebundenen Diagnoseabfragen müssen außerdem innerhalb des
`TRY` zwischen `SET STATISTICS XML ON` und dem erfolgreichen `OFF` liegen. Eine
Gegenprobe, die beide Abfragen vor `BEGIN TRY` verschiebt, wird abgelehnt. Diese
Prüfung bindet statische Positionen; sie belegt weder, dass ein Client das
Skript tatsächlich ausführt, noch dass ein Engineplan ausgegeben wird.

Der vorgeschaltete Qualifikationspreflight wird jetzt exakt auf
`HAS_PERMS_BY_NAME(DB_NAME(),'DATABASE','SHOWPLAN')`, die acht von der
Korrektheitsphase verwendeten Objekt-`SELECT`-Prüfungen, `SELECT` auf `lab.MeasurementRun`, `EXECUTE` auf
`lab.USP_Qry023MeasureVariant` und den Rechtefehlerzweig `SKIP_PERMISSION` mit
`RETURN` gebunden. Die beiden Messrechte wurden ergänzt, nachdem die Prüfung
von `40_Measurement.sql` zeigte, dass das Skript den Mess-Wrapper aufruft und
`lab.MeasurementRun` direkt liest. Negativregressionen für fremden
Datenbankscope, ausgelassene Objektberechtigungen und geänderten Skip-Code
werden zurückgewiesen. Die tatsächliche Ownership Chain und effektive
Serverrechte bleiben unbewiesene Laufzeitbedingungen.

#### READER-Phasen: Abgleich der Objektabhängigkeiten

Der Validator leitet direkte `dbo`-/`lab`-Objektreferenzen aus allen
Manifestphasen mit Profil `READER` ab und verlangt für Tabellenquellen
einschließlich Tabellenwertfunktionen `SELECT` beziehungsweise für direkte
Prozeduraufrufe `EXECUTE` im
Qualifikationspreflight. Schemaqualifizierte Referenzen, die der begrenzte
Textscanner keiner Abfrage, keinem Aufruf oder expliziten
`HAS_PERMS_BY_NAME`-Literal zuordnen kann, datenbankqualifizierte
`OtherDb.dbo...`-/`OtherDb.lab...`-Namen und dynamisches SQL führen zur
Ablehnung. Die direkten READER-Aufrufe sind zusätzlich auf
`lab.USP_Qry023MeasureVariant` begrenzt. Synthetische Regressionen fügen ein
ungeprüftes sowie datenbankqualifiziertes Objekt ein und bestätigen die
Ablehnung. Die Berechtigungszuordnung wird für jede Fundstelle im lokalen
Skriptkontext geprüft; Komma-Tabellen werden nur aus dem `FROM`-Abschnitt
erkannt. Ein gleichnamiger Tabellenzugriff an anderer Stelle deckt keine
schemaqualifizierte Funktion oder sonstige Referenz ab.

Eine zweite Textprüfung erlaubt direkt erkennbare schreibende Ziele in
READER-Skripten nur für lokale Tabellenvariablen und weist erkannte persistente
DML-, `SELECT INTO`-, `BULK INSERT`-, DDL-, Rechte- und DBCC-Anweisungen,
erkennbare `USE`-/`SETUSER`-/`REVERT`-Kontextwechsel sowie SQLCMD-Controlzeilen
außer dem exakt gebundenen `:setvar SQLCMDMAXVARTYPEWIDTH 0` zurück.
Diese eine SQLCMD-Direktive ist zusätzlich auf `50_Plan_Evidence.sql`
beschränkt; sie wird in den übrigen READER-Phasen abgewiesen.
Gegenproben mit `DELETE` (mit und ohne `FROM`), `SELECT INTO`,
`CREATE OR ALTER`, DBCC und `USE master` schützen diese Grenze. Die Prüfung gilt für direkte
Schreiboperationen im Skripttext; Auswirkungen der ausdrücklich zugelassenen
Messprozedur über deren Ownership Chain bleiben ein separates Laufzeitgate.
Diese Prüfungen sind fail-closed für die erkannten Textformen, aber keine
T-SQL-AST-Analyse und keine vollständige
Semantik für Kommentare, SQLCMD-Expansion, indirekte Aufrufe oder alle
Syntaxvarianten. Sie belegen weder effektive Berechtigungen noch
Nichtveränderung auf einer SQL-Server-Engine. Der bestehende ScriptDom-Parse
prüft Grammatik separat; Engine- und Laufzeitgates bleiben offen.

Die beiden Preflight-Summarys müssen exakt als
`QUALIFICATION_PREFLIGHT/PERMISSIONS/SKIP/SKIP_PERMISSION` und
`QUALIFICATION_PREFLIGHT/SUMMARY/PASS/OK` ausgegeben und jeweils vom passenden
`SQLPERF_SUMMARY`-Print begleitet werden. Negativfälle mit geändertem Skip-
Outcome, Erfolgs-Outcome oder Printmarker werden abgewiesen. Das prüft nur die
T-SQL-Textform; es erteilt keine Rechte und liest keine tatsächlichen
SQL-Server-Berechtigungen aus.

Eine erneute Rechteinventur fand einen bisher fehlenden Check: `30_Correctness.sql`
liest neben den vier Graph-/Relations-Querytabellen auch `OraclePerson`,
`OracleFriendOf`, `OracleRelPerson` und `OracleRelFriend`. Der frühere
Qualifikationspreflight prüfte diese vier Oracleobjekte nicht und konnte deshalb
vor der Korrektheitsphase `PASS` liefern, obwohl dort `SELECT` fehlte. Der
Preflight prüft jetzt alle acht Tabellen vor jeder Queryphase; das Proposed-
Manifest und der Offlinevalidator binden dieselbe Liste. Eine Negativregression
entfernt die `SELECT`-Prüfzeile für `OracleFriendOf` aus dem Preflightskript;
der statische Validator muss diesen Vertragsverlust zurückweisen. Der Test
verändert keine SQL-Berechtigung und führt kein SQL aus. Script-/Testprüfung
belegt weder tatsächliche Grants noch SQL-Server-Laufzeit.

Vor den Rechteprüfungen muss der Qualifikationspreflight außerdem
Systemdatenbanken (`DB_ID()<=4`) ausschließen und `DB_NAME()` exakt an den
manifestierten `@TargetDatabase`-Wert binden. Gegenproben, die den Ausschluss
entfernen oder den Vergleich umkehren, werden abgewiesen. Zusammen mit der
Manifestbindung bleibt dies eine Textprüfung; ein tatsächlicher Verbindungskontext
wird nicht hergestellt.

Die vier Extended-Property-Marker werden vor der Rechteauswertung jetzt
statisch an ihre Zuweisungen aus `sys.extended_properties` und an vollständige
Vergleiche gebunden: Projektname, Vertragsversion, Demo-ID und RunToken. Die
Vergleiche enthalten die festgelegte binäre Kollation und `DATALENGTH`-Prüfung;
der RunToken wird gegen den Harnessparameter verglichen. Gegenproben mit
verändertem Projektwert oder umgekehrter RunToken-Gleichheit werden abgewiesen.
Es werden keine realen Datenbankmarker erfasst.

Der read-only Serverpreflight leitet `@ExpectedDatabase` deterministisch aus
dem QRY-023-Demo-ID-Präfix und dem RunToken ab. Der Eingabe-RunToken wird auf
eine Länge von 1 bis 20 Zeichen sowie ausschließlich `A-Z`, `0-9` und `_`
beschränkt; der manifeste Zielname muss exakt dem abgeleiteten Namen
entsprechen. Eine zusätzliche statische Prüfung soll diese Formel und Guards
mit Gegenproben gegen einen geänderten Zielpräfix, umgekehrten Vergleich und
gelockerte Maximallänge binden. Der Validator bindet dies nun zusammen mit den
SQLCMD-gebundenen Variablen; die drei Negativregressionen werden abgewiesen.
Der Nachweis bleibt auf Skripttext beschränkt.

Als anschließende Validatorergänzung wird die Verknüpfung der
Preflight-Vertragsguards geprüft. Das bloße Vorkommen aller Bedingungen
garantiert nicht, dass jede fehlerhafte Einzelbedingung den Fehlerzweig
auslöst. Der Validator bindet nun die vollständige Klausel samt Reihenfolge und
`OR`-Verknüpfungen; eine Gegenprobe mit `AND` wird abgewiesen. Das belegt die
statische Textform, nicht die Ausführung durch SQL Server.

## RunToken-Format und nachgestellte Leerzeichen

Der bisherige RunToken-Guard kombiniert `LEN(@RunToken)` mit ASCII-
`LIKE`. Microsoft Learn dokumentiert, dass `LEN` nachgestellte Leerzeichen
ausschließt und ASCII-`LIKE` nachgestellte Leerzeichen im Ausdruck ignoriert.
Die vorgeschlagene `varchar(20)`-Eingabe kann daher am Ende Leerzeichen
enthalten, ohne dass diese beiden Prüfungen sie zuverlässig als ungültige
Zeichen erkennen. Da der erlaubte Zeichensatz ASCII ist, soll der Preflight
zusätzlich `DATALENGTH(@RunToken) BETWEEN 1 AND 20` verlangen. Der statische
Validator bindet diese Bedingung samt Reihenfolge im OR-Guard; eine
Negativregression lockert die Byte-Obergrenze und wird abgewiesen. Dies ist eine
statische Prüfung und keine tatsächliche LIKE-/LEN-Auswertung durch SQL Server.

Quellen (abgerufen am 8. November 2026): Microsoft Learn, [`LEN` (Transact-SQL)](https://learn.microsoft.com/en-us/sql/t-sql/functions/len-transact-sql?view=sql-server-ver17) und [`LIKE` (Transact-SQL)](https://learn.microsoft.com/en-us/sql/t-sql/language-elements/like-transact-sql?view=sql-server-ver17).

## SQLCMD-Eingabegrenze

Die Phasenskripte verwenden `$(DemoId)`, `$(RunToken)` und
`$(TargetDatabase)` innerhalb von SQL-Literalen. Microsoft dokumentiert
SQLCMD-Skriptvariablen und zeigt deren Expansion an den Vorkommen im Skript,
auch innerhalb eines Zeichenliterals. Daraus folgt für diesen Entwurf die
Sicherheitsinferenz, dass unsichere Quote-/Batch-Inhalte die T-SQL-Guards
erreichen können, nachdem die Skriptstruktur bereits beeinflusst wurde. Der
read-only Preflight ist daher keine SQLCMD-Injectiongrenze. Vor jeder späteren
Aufnahme in einen ausführbaren Harness muss der Aufrufer die Demo-ID exakt auf
`QRY-023`, den RunToken auf `A-Z`, `0-9`, `_` mit 1–20 ASCII-Bytes und einem
alphanumerischen ersten Zeichen sowie den Zielnamen auf die deterministische
Formel vor SQLCMD allowlisten. Der FWK-010-Caller setzt diese Eingabeprüfung
jetzt um; QRY-023 selbst bleibt dennoch nicht katalogisiert und ungefahren.

`manifest.proposed.json` bindet diese Anforderung jetzt im Feld
`sqlcmd_input_validation`: exakte Demo-ID, ASCII-RunToken-Zeichensatz und
Bytegrenzen, deterministische Zielnamenschablone sowie Prüfung vor
SQLCMD-Expansion. Der Validator vergleicht das ganze Vertragsobjekt gegen die
Sollstruktur; Gegenproben für Validierungszeitpunkt und Zeichensatz werden
abgewiesen. Das Manifestfeld allein implementiert keinen Aufrufer; die optionale
Prüfung in FWK-010 setzt es für diesen Caller durch. Das ersetzt weder die
QRY-023-Runtimequalifikation noch eine Engineausführung.

`Demos/00_Framework/Tools/run_demo.py` setzt das optionale Vertragsobjekt jetzt
beim Manifestladen durch. Ungültige Vertragswerte und ein SQL-Injection-
ähnlicher RunToken scheitern vor `resolve_sqlcmd` und vor dem ersten
Prozessstart; synthetische Caller-Tests schützen diesen Ablauf. Der QRY-023-
Entwurf bleibt aus dem Katalog ausgeschlossen und wurde nicht gegen SQL Server
ausgeführt.

Quelle (abgerufen am 8. November 2026): Microsoft Learn, [Use sqlcmd with scripting variables](https://learn.microsoft.com/en-us/sql/tools/sqlcmd/sqlcmd-use-scripting-variables?view=sql-server-ver15). Die Ableitung zur Eingabesicherheit ist eine Projektinferenz aus dem dokumentierten Expansionsverhalten.

## Actual-Plan-Ausgabegrenze

Die unabhängige QRY-023-Nachprüfung vom 12. November 2026 fand, dass sqlcmd
XML-Datentypen standardmäßig bei 256 Zeichen abschneidet, während der
FWK-010-Phasenstatus nur die Summary auswertet. `50_Plan_Evidence.sql` setzt
jetzt vor `STATISTICS XML ON` die dokumentierte Skriptvariable
`SQLCMDMAXVARTYPEWIDTH` auf `0`. Die Ausgabe ist auf zwei `COUNT_BIG`-
Diagnoseabfragen begrenzt; Plan-Dateien werden nicht gespeichert. Der
Strukturvalidator schützt die Direktive samt Position, eine Negativregression
weist den Grenzwert 256 zurück und der ScriptDom-Parser entfernt nach separater
Prüfung nur diese Nicht-T-SQL-Direktive vor dem Grammatikparse. Die Registry
benennt nun dieselbe vorgeschlagene 10.000-/30.000-/20.000-Messlast wie ihr
`measurement_gate`.

Die unabhängige Nachprüfung fand keine P1/P2 und erreichte die Review-Schwelle
für diesen Offline-Fix. Sie qualifiziert weder den konkreten sqlcmd-Client noch
die vollständige Demo-Methode. Runtimevollständigkeit und Ressourcenwirkung,
formale Harness-/T-SQL-Abnahme, aktuelle Images/Builds, Ressourcenisolation,
Cleanup sowie Ausführungsautorisierung bleiben offen.

Eine anschließende unabhängige Prüfung fand einen Validator-P2: eine weitere
`SQLCMDMAXVARTYPEWIDTH`-Direktive konnte den zuvor geprüften Wert `0` vor
`STATISTICS XML ON` wieder auf `256` setzen. Der Validator bindet jetzt den
letzten Wert vor der Aktivierung; die Regression `0` gefolgt von `256` wird
abgewiesen. Die unabhängige Nachprüfung des Korrekturschnitts bestätigte die
Schließung ohne neue P1/P2. Das Skript selbst enthält weiterhin den korrekten
Wert `0`. Laufzeit- und Gesamtmethodengates bleiben unverändert offen.

## Gesamtprüfung des Offlinevorschlags

Die unabhängige Gesamtprüfung vom 12. November 2026 an Main `b48269a` bestätigte
die Daten-, Queryform-, Messreihen- und Planabfragebindungen, fand jedoch zwei
P2-Gates: eine einzelne FWK-010-Anmeldung bleibt über Setup/Lesen/Cleanup
wirksam, und Größen-, Session- sowie Abbruchgrenzen nach FWK-008 waren noch
nicht vollständig gebunden. Das Manifest und der Lesepfad legen jetzt die
Phasenrechte, die vorgeschlagenen 1-GiB-Datenbank-/TempDB-Grenzen, eine
gleichzeitige Session, Stoptrigger und mögliche Restzustände offen. Der
vorhandene FWK-010-Prozesspfad wurde dafür nicht geändert: PR-Checks zeigen,
dass mehrere qualifizierte Sourceprofile (einschließlich DGN-007 und CON-010)
die gemeinsamen Runtime-Dateien fest binden. Diese Bindungen werden in dieser
QRY-023-Arbeit weder umgangen noch neu qualifiziert. Abbruch, bestätigtes
Prozessende und Cleanup-Reihenfolge bleiben daher im vorhandenen Caller
ungeprüft.

Beim damaligen Gesamtreview blieb die phasenspezifische Identitätsdurchsetzung
`OPEN`, weil der allgemeine Caller nur eine Anmeldung annahm. Die vorgeschlagenen
Größenwerte waren nicht gemessen; der Runtimecaller musste sie technisch
erzwingen. Bis die jeweiligen Prüfungen bestehen, gilt keine vollständige
Harness-/Methodenfreigabe. Kein SQL oder Runtime wurde ausgeführt.

### Nachtrag vom 12. November 2026: SQL-Anmeldungsprofile je Phase

FWK-010 unterstützt jetzt optionale `credential_profiles` mit einer expliziten
`credential_profile`-Zuordnung je SQL-Phase. Der Runner verlangt in diesem Modus
SQL-Authentifizierung, vollständige Anmeldedaten vor SQLCMD-Auflösung und
unterschiedliche Benutzernamen. Das Kennwort des ausgewählten Profils wird nur
als `SQLCMDPASSWORD` an dessen Prozess übergeben; andere profilgebundene
Kennwortvariablen werden entfernt. Synthetische Runner-Regressionen prüfen die
Phasenzuordnung und die Prozessumgebungen. QRY-023 ordnet ADMIN und READER den
vorgesehenen Phasen zu.

Dieser Offlinebefund schließt nur die Client-seitige Identitätsauswahl. Er
belegt weder Existenz oder SID der SQL-Server-Prinzipale noch deren effektive
Rechte. Minimalrechte, tatsächliche Ablehnung überprivilegierter Profile,
Serverversionen, Ressourcenbegrenzung, Abbruch-/Reap-Reihenfolge und Runtime
bleiben offene Gates.

### Rechteprüfung: Rollenmitgliedschaft ist kein Minimalrechtnachweis

Ein weiterer Offlineabgleich prüfte, ob `IS_SRVROLEMEMBER('sysadmin')` und
`IS_ROLEMEMBER('db_owner')` als einfacher Ausschluss für überprivilegierte
READER-Anmeldungen ergänzt werden sollten. Microsoft beschreibt beide
Funktionen als Rollenmitgliedschaftsprüfungen, nicht als Abfrage der
zugrunde liegenden effektiven Rechte. Beide Funktionen benötigen außerdem
`VIEW DEFINITION` auf der jeweiligen Rolle; ohne diese Sicht kann das Ergebnis
`NULL` sein. Eine solche Prüfung würde weder andere direkte oder geerbte
Grants erfassen noch ohne zusätzliche Rechte verlässlich laufen. Sie wird
deshalb nicht als Minimalrechte-Gate ergänzt.

Der bestehende Preflight bleibt auf den nötigen positiven `SELECT`-,
`EXECUTE`- und `SHOWPLAN`-Rechten fail-closed. Die Existenz der beiden
Anmeldungen, ihre effektive Berechtigungsmenge, zusätzliche Rollen oder Grants
und die Ownership Chain müssen in einer späteren qualifizierten Umgebung
geprüft werden; das Gate bleibt `OPEN`. Quellen, abgerufen am 12. November
2026: [IS_SRVROLEMEMBER (Transact-SQL)](https://learn.microsoft.com/en-us/sql/t-sql/functions/is-srvrolemember-transact-sql)
und [IS_ROLEMEMBER (Transact-SQL)](https://learn.microsoft.com/en-us/sql/t-sql/functions/is-rolemember-transact-sql).

#### Nächster Offline-Prüfansatz

Für den Soll-Ist-Abgleich ist `sys.fn_my_permissions` im tatsächlichen
`READER`-Verbindungskontext ein geeigneter Designkandidat: Microsoft beschreibt
die Ausgabe als effektive Berechtigungen des aktuellen Sicherheitskontexts für
das angegebene sicherbare Objekt. Ein künftiger Vertrag muss vorab eine
vollständige, phasengenaue Sollmenge für Server, Ziel-Datenbank, betroffene
Schemas und jedes erzeugte QRY-023-Objekt festlegen. Die vorgesehenen positiven
Rechte `SELECT`, `EXECUTE` und `SHOWPLAN` sind kein vollständiger Allowlist-
Nachweis. Der Abgleich muss fehlgeschlagene oder nicht auswertbare Abfragen und
jede zusätzliche effektive Berechtigung fail-closed behandeln. `fn_my_permissions`
wertet ausschließlich den Aufruferkontext aus; damit ist keine Prüfung anderer
Principals oder ein Nachweis der internen Ownership Chain verbunden. Beides
bleibt offen bis zu einer getrennten Laufzeitqualifikation. Der Ansatz ist
DESIGNED, nicht implementiert oder enginequalifiziert. Quelle, abgerufen am
12. November 2026: [sys.fn_my_permissions (Transact-SQL)](https://learn.microsoft.com/en-us/sql/relational-databases/system-functions/sys-fn-my-permissions-transact-sql?view=sql-server-ver17).
Die Aufzählung der QRY-023-eigenen Objekte beweist außerdem nicht, dass auf
anderen Datenbank- oder Instanzobjekten keine zusätzlichen Rechte bestehen.
Ein vollständiger Minimalrechtnachweis muss sämtliche relevanten Securables
einschließlich Spaltenrechten inventarisieren oder den Aussageumfang auf eine
qualifizierte dedizierte Wegwerfinstanz mit gebundenem Objektbestand begrenzen.

#### FWK-004-Wartezeitrechte im QRY-023-Readerpfad

Der Aufruf von `lab.USP_Qry023MeasureVariant` bindet
`@CaptureSessionWaits=0` an `fwk.USP_BeginMeasurement`. FWK-004 liest für die
Sessiondeltas `sys.dm_exec_sessions` mit `session_id = @@SPID`; Microsoft
dokumentiert, dass jeder Principal die eigene Session sehen kann. Die
bedingten Abfragen auf `sys.dm_exec_session_wait_stats` werden bei diesem
Parameter übersprungen. Für diese DMV verlangt SQL Server 2022 und neuer das
Serverrecht `VIEW SERVER PERFORMANCE STATE`; es ist deshalb kein notwendiger
Bestandteil des QRY-023-READER-Profils und darf nicht als Umgehung für eine
aktivierte Wait-Erfassung ergänzt werden. Die bestehende Vertragsprüfung bindet
den Literalwert `0`; eine zusätzliche Negativregression muss den Wechsel auf
`1` zurückweisen. Das ist ein statischer Quellen-/Codepfadbefund, kein
Engine-Nachweis der übrigen Minimalrechte. Quellen, abgerufen am 12. November
2026: [sys.dm_exec_sessions](https://learn.microsoft.com/en-us/sql/relational-databases/system-dynamic-management-views/sys-dm-exec-sessions-transact-sql?view=sql-server-ver17), [sys.dm_exec_session_wait_stats](https://learn.microsoft.com/en-us/sql/relational-databases/system-dynamic-management-views/sys-dm-exec-session-wait-stats-transact-sql?view=sql-server-ver17).

Die erste PR-CI-Prüfung zeigte, dass DGN-007 zusätzlich den AST von
`run_demo.py` fest bindet. Die Bindung enthält jetzt den exakten Python-3.12-
AST-Digest der erweiterten Runnerdatei; alle übrigen DGN-007-AST-Digests bleiben
unverändert. `sqlcmd_process.py` ist unverändert, damit der getrennte CON-010-
Collectorvertrag seine zwei bisher qualifizierten Zeilenendungsvarianten
weiterhin exakt prüfen kann. Die DGN-007-Offline-Gegenproben laufen erneut;
bis zum erfolgreichen Workflow bleibt diese Requalifikation offen.

Das prüft nur die statische Übereinstimmung des vorgeschlagenen Manifests mit
den im Validator festgelegten Werten. Es belegt weder die Ausführung dieser
Budgets durch einen Runtimeaufrufer noch Enginekompilierung, tatsächliche
Containerressourcen, Graph-Table-Semantik oder Messmethodik. ScriptDom-Parsen
ist keine Enginekompilierung.

QRY-023 bleibt nicht katalogisiert. Formale Harness-/T-SQL-Abnahme,
unabhängige Methodenfreigabe, aktuelle Image-/Buildbestätigung, Ressourcen-
Durchsetzung, Cleanupqualifikation und konkrete Runtimeautorisierung bleiben
getrennte Gates.

Der nachfolgende Offlinevalidator bindet inzwischen die geordnete
Runtime-Matrix aus Jahr, Produktmajor und Image-Digest exakt an die drei Profile
des vorgeschlagenen Image-Locks. Damit ist die statische Drift zwischen Lock
und fest codiertem Workflow ausgeschlossen. Der Workflow konsumiert die
Lockdatei weiterhin nicht; dieser Paritätscheck gewährt keine Ausführungsrechte
und ersetzt weder die Runtimequalifikation noch ein Review.
