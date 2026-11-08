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

## Aussagegrenzen und weitere Gates

Das prüft nur die statische Übereinstimmung des vorgeschlagenen Manifests mit
den im Validator festgelegten Werten. Es belegt weder die Ausführung dieser
Budgets durch einen Runtimeaufrufer noch Enginekompilierung, tatsächliche
Containerressourcen, Graph-Table-Semantik oder Messmethodik. ScriptDom-Parsen
ist keine Enginekompilierung.

QRY-023 bleibt nicht katalogisiert. Formale Harness-/T-SQL-Abnahme,
unabhängige Methodenfreigabe, aktuelle Image-/Buildbestätigung, Ressourcen-
Durchsetzung, Cleanupqualifikation und konkrete Runtimeautorisierung bleiben
getrennte Gates.
