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
`HAS_PERMS_BY_NAME(DB_NAME(),'DATABASE','SHOWPLAN')`, die vier verwendeten
Objekt-`SELECT`-Prüfungen und den Rechtefehlerzweig `SKIP_PERMISSION` mit
`RETURN` gebunden. Negativregressionen für fremden Datenbankscope, ausgelassene
Objektberechtigung und geänderten Skip-Code werden zurückgewiesen.

Die beiden Preflight-Summarys müssen exakt als
`QUALIFICATION_PREFLIGHT/PERMISSIONS/SKIP/SKIP_PERMISSION` und
`QUALIFICATION_PREFLIGHT/SUMMARY/PASS/OK` ausgegeben und jeweils vom passenden
`SQLPERF_SUMMARY`-Print begleitet werden. Negativfälle mit geändertem Skip-
Outcome, Erfolgs-Outcome oder Printmarker werden abgewiesen. Das prüft nur die
T-SQL-Textform; es erteilt keine Rechte und liest keine tatsächlichen
SQL-Server-Berechtigungen aus.

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
gelockerte Maximallänge binden. Der Nachweis bleibt auf Skripttext beschränkt.

Das prüft nur die statische Übereinstimmung des vorgeschlagenen Manifests mit
den im Validator festgelegten Werten. Es belegt weder die Ausführung dieser
Budgets durch einen Runtimeaufrufer noch Enginekompilierung, tatsächliche
Containerressourcen, Graph-Table-Semantik oder Messmethodik. ScriptDom-Parsen
ist keine Enginekompilierung.

QRY-023 bleibt nicht katalogisiert. Formale Harness-/T-SQL-Abnahme,
unabhängige Methodenfreigabe, aktuelle Image-/Buildbestätigung, Ressourcen-
Durchsetzung, Cleanupqualifikation und konkrete Runtimeautorisierung bleiben
getrennte Gates.
