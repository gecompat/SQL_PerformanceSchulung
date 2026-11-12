# DGN-004: unabhängige Quellenprüfung und Vorstartstatus

Stand: 2026-11-12. Der Review ist an den integrierten Quellstand `1c3465f`
gebunden; die anschließenden Korrekturen sind in PR #518 (`9ce0c0f`) enthalten.

## Ergebnis der unabhängigen Prüfung

Der unabhängige, read-only Methoden-/Quellen-/Zuordnungs-/Transport-/Messreview
prüfte den aktiven `classical_forcing_hint_control_plan`. Er fand zunächst zwei
P2-Lücken im statischen Force-Fehlerzählervertrag: wiederverwendete
Force-Epochen und ein positiver Zähler direkt nach Force konnten bestehen.
PR #518 schließt beide Lücken. Jede erzwungene Anforderung verlangt nun eine
eigene Epoche und einen Zählerstand von null unmittelbar nach Force; ein
späterer Zähleranstieg bleibt ein Fehler. Der Reviewer bestätigte die Fixes.
Im geprüften Umfang bleiben keine P1/P2 offen.

Die Prüfung bestätigt die dokumentierten Grenzen des Source-only-Stands:
caller-gelieferte Identitätswerte sind keine authentifizierte Serveraufnahme,
der Frame- und XML-Prüfer belegt keine aktuelle Ausführung oder
Handle-Provenienz, und es gibt noch keine SQL-/Build-/Lifecycle-Qualifikation.
Der enge Scope bleibt `CLASSICAL_FORCING_AND_HINT_CONTROL`; Replay-Marker und
die frühere Replay-Abnahme bleiben getrennt offen.

## Integrierte statische Gegenproben

- PR #516 ergänzt die H-Quelle, in der der einzige Hint nur auskommentiert ist.
- PR #517 prüft Objekt-, Query-Text- und Kontextidentitätsdrift innerhalb
  derselben Rolle.
- PR #518 prüft eindeutige Force-Fehlerzählepochen und den Nullzähler nach
  Force.
- Die ergänzende Hash-Gegenprobe hält `query_hash` und `query_plan_hash` als
  rohe 8-Byte-Werte fest. Gleiche Hashes zwischen getrennten Rollen und ein
  Hashwechsel bei stabiler ID-Bindung werden akzeptiert; falsche Länge wird
  abgelehnt. Der unabhängige Reviewer bestätigte, dass Hashes keine
  Identitätsschlüssel sind.

Die vollständige DGN-004-Statiksuite besteht unter Windows mit 68 Tests und
einem plattformspezifischen Skip sowie unter Linux/WSL mit 68 Tests ohne Skip.
Die vier Repositoryprüfungen der drei PRs bestanden. Diese Ergebnisse sind
keine Runtimeevidenz.

## Vorstartstatus

Die beiden im aktiven Plan gebundenen Docker-Image-Digests sind lokal vorhanden:
SQL Server 2022 `sha256:ba4c8329f48fb8f02e1416be6a930ebfd71268caee78aa985f3af4315e457c89`
und SQL Server 2025
`sha256:4bab24f36c1ecd48e85f7d37df26e6bf301641d84c3fe652f9a0dcc947d512e1`.
Es wurde kein Image heruntergeladen oder gestartet.

Der Hostcheck am 2026-11-12 fand fünf bereits aktive, DGN-004 nicht
zugeordnete SQL-Server-Container. Eine einzelne Momentaufnahme zeigte zusammen
rund 33 % CPU und 7,4 GiB Speicherverbrauch. Diese Momentaufnahme belegt keine
kontrollierte Optimiererlast oder ausreichende Reserve. Der unabhängige
Reviewer beurteilt das YELLOW-Isolationsgate daher als **nicht erfüllt**;
Ressourcenlimits für einen neuen Container würden die Konkurrenzlast nicht
auflösen. Die bestehenden Container und Dienste wurden nicht verändert.

## Noch offene Gates

Vor dem ersten DGN-004-Container müssen eine kontrollierte Optimiererlast und
die isolierte Wegwerfumgebung belegbar sein. Danach bleiben die exakte Engine-
Build-/Edition-/Compatibility-Prüfung, Rechte, Ausgangsoptionen, vier
vollständige Eigentumsmarker und alle sequenziellen Capture-/Ergebnis-/Unforce-
/Cleanupbelege Pflicht. Der aktive Plan begrenzt den Lauf auf zwei eigene,
sequenzielle Container, neun Nutzaufrufe je Build, insgesamt 900 Sekunden
reguläre Laufzeit und höchstens 60 Sekunden Cleanup je Container. Keine
Wiederholung nach einem Fehler oder unbekannten Pflichtbeleg.

Die Nutzeranweisung vom 2026-11-12 autorisiert die offenen Punkte innerhalb
dieses bestehenden Scopes. Sie hebt weder das YELLOW-Gate noch die übrigen
Qualifikationsgrenzen auf. Menschliche Generalprobe, Replay-Erweiterung und
SQL Server 2019 bleiben ausgeschlossen.
