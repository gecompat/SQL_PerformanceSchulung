# QRY-017: automatisierte Volltextprobe

Stand: 19. Oktober 2026. Die beauftragte Ergänzung schließt den bisher nur
optional übersprungenen Volltextpfad von QRY-017 auf einer eigenen
SQL-Server-2025-/Linux-/Docker-Instanz ab. Der normale Kursaufruf darf bei
fehlender Komponente weiterhin `WARN_OPTIONAL_EVIDENCE_SKIPPED` melden.
Die historischen BASIS-, STANDARD- und VERTIEFUNG-Proben vom 18. Oktober
behalten ihren tatsächlich beobachteten WARN.

## Voraussetzung und getesteter Stand

Die Komponentenverwaltung übernimmt `SQL_Server_Lab`, einschließlich
automatisierter Aktivierung über `New-SqlServerLab -FullText $true` und
vollständiger Entfernung über `Remove-SqlServerLab`. Die Schulungsdemo
installiert keine Serverkomponenten. Die zugehörige Lab-Änderung ist
[PR806](https://github.com/gecompat/SQL_Server_Lab/pull/806); die zuvor
integrierte Bereinigungsänderung ist
[PR805](https://github.com/gecompat/SQL_Server_Lab/pull/805).

Die Probe verwendete den sauberen, eingefrorenen Lab-Kandidaten
`3560b746506e506e6e4d728a5746b7afeae41211`, Tree
`75633f60c8f102e912f28c9975bd2944647d92d3`, nach unabhängigem Lab-Review.
Vor der Schulungsintegration müssen die finale Lab-CI (Continuous Integration; automatisierte Integrationsprüfungen) und Main-Übernahme
bestätigt sein. Der native Nachweis selbst gilt für diesen exakten Quellstand.
Die anschließende Linux-CI fand eine veraltete Sperrfehlererwartung in
`Tests/Static/Fixtures/ResourceChangeGuidanceChecks.ps1`: Die gemeinsame
Sperre weist den Zugriff bereits mit `SQL_FEATURE_OPERATION_BUSY` ab,
während die Fixture ausschließlich `RESOURCE_CHANGE_BUSY` erwartet.
Nur diese statische Fixture darf gegenüber dem nativen Lab-Stand abweichen;
der finale Git-Vergleich muss alle Produkt-/SQL-Quellen unverändert bestätigen.
Diese Korrektur einer Testerwartung benötigt keine erneute Consumerprobe.

Tatsächlich gemessen: SQL Server **17.0.4075.5**, Major 17,
`IsFullTextInstalled=1`. Die eigene Instanz wurde über den öffentlichen
Lab-Einstieg mit Docker, Profil `compact`, zwei CPUs und 4096 MiB erstellt.
Die Freigabe des gemeinsamen Runtime-Slots wurde atomar geprüft. Es gab
einen nativen Abnahmeversuch mit zwei vorgesehenen Demo-Lifecycles;
keine Wiederholung bis zu einem gewünschten Ergebnis.

Die ausgeführten Schulungsquellen stammen aus Commit
`173d0b674ed25f268f0a41165108e4a6924ba99a`. Private SHA256- und
Git-Blob-Bindungen bestätigen unveränderte Runtimequellen während der Probe.
Anschließend wurde ausschließlich ein übersprungener zusätzlicher
Tenant-Gegenprobezweig aus dem Runner entfernt: `run_sql` liefert stdout,
der dort gesuchte PRINT-Nachweis lag wegen `sqlcmd -r 1` auf stderr.
Diese zusätzliche Gegenprobe wurde nicht ausgeführt und gilt nicht als
bestanden. Die ausgeführten SQL-Suchprüfungen und der normale
Ergebnisgegenfall bleiben unverändert; es wird dafür keine zweite native
Probe behauptet.

## Suchvertrag und tatsächliche Ergebnisse

Die neutrale Indexsprache `LANGUAGE 0` wird mit dem gespeicherten Wort `rote`
geprüft. Die SQL-Vergleichsphase verlangt exakt diese Ergebnismengen:

| Suchfall | Tenant | Erwartete IDs |
|---|---|---|
| CONTAINS, exaktes Wort `"rote"` | A | 1 und 3 |
| FREETEXT, `rote` | A | 1 und 3 |
| CONTAINSTABLE, exaktes Wort `"rote"` | A | 1 und 3; jeweils positiver Rang |
| CONTAINS, exaktes Wort `"rote"` | B | 4 |
| CONTAINS, fehlendes Wort `"quarzxyz"` | A | keine |

Zwei gerichtete Mengenvergleiche erkennen fehlende und zusätzliche Treffer.
Es gibt keinen festen Rangwert und keine Laufzeitbehauptung.
`fulltext_checks=5` wird erst nach allen fünf erfolgreichen Suchfällen
ausgegeben. Der Runner verlangt die Übereinstimmung von tatsächlicher
Komponentenverfügbarkeit, Suchnachweiszahl und PASS-/WARN-Ergebnis.
`--require-fulltext` weist einen optionalen WARN ausdrücklich ab und ist
nur für den SQL-2025-/QRY-017-Pfad zulässig.

| Tatsächlich ausgeführte Prüfung | Ergebnis |
|---|---|
| Vollständiger FWK-010-/FWK-011-Lifecycle 1 | PASS / OK; vier Ergebnisassertionen |
| Vollständiger FWK-010-/FWK-011-Lifecycle 2 | PASS / OK; vier Ergebnisassertionen |
| Fünf Volltext-Suchfälle je Lifecycle | bestanden |
| 48 Abweisungen fehlender/falscher Eigentumsmarker | bestanden |
| Setup-Idempotenz und Ergebnisgegenfall mit gelöschten Suchdaten | bestanden |
| Unabhängige DB-Abwesenheit und abschließend keine Benutzerdatenbank | bestätigt |

Der Gesamtabschluss lautet `AI_LOCAL_QUALIFICATION|PASS|EXPECTED_CONTRACTS_AND_CLEANUP`.
Runner und separater Workerprozess endeten jeweils tatsächlich mit Exitcode 0.
Die Probe dauerte einschließlich Einrichtung und Abbau rund 319 Sekunden;
dies ist keine Unterrichtszeit oder Suchperformancemessung.

## Bereinigung und übrige Validierung

Der öffentliche Lab-Abbau meldete `REMOVED`. Neue lesende Docker-Abfragen
bestätigten die Abwesenheit des exakten eigenen Containers und des einzigen
eigenen Volumes. Es gab keinen Probe- oder Cleanupfehler. Der Worker gab den
Runtime-Mutex ausdrücklich frei. Der eigene temporäre, saubere Lab-Worktree
wurde anschließend entfernt; fremde Worktrees wurden nicht verändert.
Kennwort, Ressourcenkennungen und rohe Logs bleiben privat und ignoriert.

Die 16 vorhandenen/erweiterten Runner-Unittests prüfen insbesondere fehlende,
unvollständige oder widersprüchliche Suchnachweise, den strengen WARN-Ausschluss,
zwei Lifecycles, den tatsächlichen Vier-Assertionen-Vertrag und unzulässige
Versions-/Demoauswahl vor Zielzugriff. Frameworkvertrag und Datenschutzprüfung
der veröffentlichten Dateien bestanden. Die finale PR-CI wird gegen den
aktuellen Schulungs-Head abgewartet; ihr Ergebnis gehört zur Mergeprüfung.

## Aussagegrenzen

Dieser Nachweis ergänzt ausschließlich QRY-017. Er qualifiziert weder alle
Lab-Provider noch Windows, SQL Server 2019/2022 oder andere Enginebuilds.
Die CI-Versionsmatrix und der optionale Pfad bleiben gesonderte Prüfungen.
Die synthetische Tenantfixture ersetzt keine vollständige CON-010-Abnahme.
Es gibt keine neue Embedding-/Modell-, Suchqualitäts- oder Performancefreigabe.
Teilnehmerpilot, gemessene Lehrzeiten und die übrigen offenen TSK-/Streamgates
bleiben unverändert im bestehenden Plan. Die ausdrücklich zurückgestellte
DGN-007-Arbeit wird durch diesen Abschluss nicht wiederaufgenommen.
