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

Das prüft nur die statische Übereinstimmung des vorgeschlagenen Manifests mit
den im Validator festgelegten Werten. Es belegt weder die Ausführung dieser
Budgets durch einen Runtimeaufrufer noch Enginekompilierung, tatsächliche
Containerressourcen, Graph-Table-Semantik oder Messmethodik. ScriptDom-Parsen
ist keine Enginekompilierung.

QRY-023 bleibt nicht katalogisiert. Formale Harness-/T-SQL-Abnahme,
unabhängige Methodenfreigabe, aktuelle Image-/Buildbestätigung, Ressourcen-
Durchsetzung, Cleanupqualifikation und konkrete Runtimeautorisierung bleiben
getrennte Gates.
