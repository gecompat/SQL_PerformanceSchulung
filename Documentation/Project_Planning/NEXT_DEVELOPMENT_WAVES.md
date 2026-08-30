# Nächste Entwicklungswellen

| Merkmal | Wert |
|---|---|
| Status | `ACTIVE` |
| Stand | 2026-08-30 |
| Ausgangsstand | `c75d7a25e966d28abeb8225779e7cc48939159fe` auf `origin/main` |
| Bezug | [CURRENT_EXECUTION_STATUS.md](CURRENT_EXECUTION_STATUS.md), `.ai/BACKLOG.md`, `MASTER_IMPLEMENTATION_PLAN.md` |
| Zweck | priorisierte, kleine Folgepakete; keine Aussage, dass die beschriebenen Inhalte bereits umgesetzt sind |

## 1. Planungsgrundlagen

- `QRY-013`, `OPT-009` und `OPT-010` besitzen aktuelle Matrixnachweise aus GitHub Actions. `QRY-004` besitzt keinen Freigabenachweis: Sein Lauf beendet die SQL-Phasen und das Cleanup erfolgreich, wird aber wegen `WARN_EMPIRICAL_VARIANCE` als fehlgeschlagen bewertet.
- Der lokale Stand besteht aus erfolgreichen statischen Validatoren, neun Unit-Tests und einem erfolgreichen Privacy-Scan. Das ersetzt keine neue Runtime-Ausführung.
- Die Curriculum-Analyse verlangt kein neues Hauptmodul. Neue Arbeit erweitert deshalb nur bestehende Lernziele und Demo-IDs.
- Jede Welle ist ein eigenständiger, kleiner Pull Request mit klarer Runtime-, Quellen- und Safety-Grenze. Öffentliche Herstellerdokumentation wird erst nach dem Source-Register-Delta-Review zu Lehrinhalt.

## 2. Priorisierte Wellen

| Reihenfolge | Welle | Ziel und abgegrenzter Umfang | Akzeptanzkriterium |
|---:|---|---|---|
| 1 | `W-STA-001` | `QRY-004`-Runner-Konflikt analysieren und korrigieren. Nur Bewertungs- und Nachweislogik ändern, wenn sie den tatsächlichen SQL-Erfolg falsch abbildet. | Die 2019/2022/2025-Matrix läuft erneut; Ergebnis, erwartete Warnungen und Workflow-Status sind widerspruchsfrei dokumentiert. |
| 2 | `W-DGN-001` | Kleinen Query-Store-/Extended-Events-Pilot für `DGN-003` und `DGN-005` erstellen. SQL Server 2025-spezifische Optionen, etwa zeitgebundene XE-Sessions, nur versionsbewusst und mit explizitem Skip behandeln. | Wiederholbarer Nachweis für Erfassung, Auswertung, Cleanup und Feature-Skips; erst danach darf `DGN-007` geplant werden. |
| 3 | `W-SCN-001` | `CON-004` als ersten gelben, isolationspflichtigen interaktiven `LABSCN-003`-Vertical-Slice ausführen: Auswahl, Provisionierung, fachliche Vorbereitung, `READY_FOR_USER`, Reset und Remove. | Ein Benutzer kann den vollständigen Lifecycle nachvollziehen; die automatisierte Testmatrix bleibt davon getrennt. |
| 4 | `W-ADV-017` | `OPT-017` als isoliertes Paket für gelbe parallele Pläne und Ressourcenprofilierung umsetzen. | Safety-Gate, synthetische Last, Zeitbudget, Cleanup und Matrixnachweis sind vor der Freigabe belegt. |
| 5 | `W-SQL25-001` | Source-Register-Delta-Review für relevante SQL-Server-2025-Funktionen. Bestehende Ziele zuerst zuordnen, statt neue Features pauschal in die Schulung aufzunehmen. | Jede übernommene Aussage besitzt Quelle, Versionsbereich, Claim-Bezug, Entscheidung und gegebenenfalls Demo-ID. |
| 6 | `W-PRS-001` | `PRS-012`/`TST-011`, danach `PRS-013`/`TST-012` abschließen und die offenen Vertiefungsfolien visuell rendern. | Renderartefakte, Layoutprüfung und aktualisierte Lehrmittelabnahme liegen vor. |
| 7 | `W-COV-001` | Danach die verbleibende curriculare Abdeckung sequenziell angehen: zuerst `OPT-003`/`OPT-005`, dann `CON-006`/`CON-009`, `IDX-006`/`IDX-010`, `STL-008`/`STL-009` und `RES-007`. | Jede Demo wird einzeln gegen Curriculum, Source Register, Demo-Vertrag und geeignete Testmatrix abgenommen. |

## 2.1 Umsetzungsstand der Wellen

| Welle | Status | Evidenzgrenze |
|---|---|---|
| `W-STA-001` | `IMPLEMENTED` | Runnervertrag und Regressionstests sind grün; die zweifache 2019/2022/2025-Matrix bleibt offen. |
| `W-DGN-001` | `IMPLEMENTED` | Query-Store- und XE-Pilot sind statisch vollständig; die Runtime-Matrix bleibt offen. |
| `W-SCN-001` | `VALIDATED` | Project Adapter `0.1` und vollständiger SQL-Server-2025-Lifecycle sind auf Docker und Podman praktisch validiert. |
| `W-ADV-017` | `IMPLEMENTED` | Demo, Runner und Workflow liegen vor; die zweifache Parallelitätsmatrix bleibt offen. |
| `W-SQL25-001` | `VALIDATED` | Quellen-, Claim- und Entscheidungsgrundlage ist abgeschlossen; daraus folgt keine neue Featuredemo. |
| `W-PRS-001` | `VALIDATED` | 102 SlideKeys, drei Custom Shows, Build 41/66/102 und vollständige Master-/Profilrender liegen vor. |
| `W-COV-001` | `PARTIAL` | Acht Demos sind nach je zwei 2019/2022/2025-Läufen validiert; `CON-009` bleibt wegen fehlender interner Task-Allokation auf SQL Server 2019 `IMPLEMENTED`. |

## 3. SQL-Server-2025-Delta: Prüfreihenfolge, keine Vorabzusage

Der Delta-Review soll zunächst diese Zuordnung prüfen:

| Herstellerfunktion | mögliche bestehende Anknüpfung | vorläufige Entscheidung |
|---|---|---|
| Cardinality Estimation Feedback für Ausdrücke | `OPT-006` | Quellen- und Unterrichtsnutzen prüfen |
| Optimiertes `sp_executesql` | `QRY-004`, `OPT-007` | erst nach Stabilisierung von `QRY-004` bewerten |
| zeitgebundene Extended-Events-Sessions | `DGN-005` | als optionaler 2025-Pfad im Pilot prüfen |
| tempdb-Space-Resource-Governance | `CON-009`, `RES-004` | nur mit gelb/roter Infrastruktur- und Safety-Bewertung prüfen |
| geordnete nonclustered Columnstore-Indizes | `IDX-010` | Nutzen und Edition/Version vor einer Demo prüfen |
| Query Store auf lesbaren Secondary Replicas | kein unmittelbarer Slice | vorerst zurückstellen: Preview- und Mehrinstanzabhängigkeit |

Vector- und KI-Funktionen liegen außerhalb des derzeitigen Curriculumzuschnitts. Der Review verwendet als Ausgangspunkt die offiziellen Microsoft-Dokumentationen zu [SQL Server 2025](https://learn.microsoft.com/sql/sql-server/what-s-new-in-sql-server-2025?view=sql-server-ver17), [Extended Events](https://learn.microsoft.com/sql/relational-databases/extended-events/sql-server-extended-events-sessions?view=sql-server-ver17) und [Query Store auf Secondary Replicas](https://learn.microsoft.com/sql/relational-databases/performance/query-store-for-secondary-replicas?view=sql-server-ver17); vor einer Inhaltsübernahme muss der Projekt-Quellenregisterprozess durchlaufen werden.

## 4. Abhängigkeits- und Stop-Regeln

```text
QRY-004 stabil -> V3 vervollständigen
Query Store/XE-Pilot -> DGN-007 zulässig
CON-004 Vertical Slice -> weitere interaktive Szenarien
Source-Delta-Review -> mögliche SQL-2025-Inhalte
Renderprüfung -> Gate V4
```

- Kein `DGN-007` ohne validierten Query-Store-/XE-Pilot.
- Keine rote oder gelbe Lastdemo ohne bestehende Safety-Gates, Wegwerfinfrastruktur, Kill-Switch und Laufzeitbudget.
- Keine Änderung an `SQL_Server_Lab` ohne dokumentierte Fähigkeitslücke und ausdrückliche Freigabe.
- Keine Statusanhebung aus statischem Testbestand allein; Runtime-Status benötigt einen konkreten Laufnachweis.

## 5. Nächster belegpflichtiger Schritt

Die Entwicklungsfolge ist implementiert. `W-SCN-001` besitzt vollständige Docker- und Podman-Runtimenachweise. Als nächster W-COV-Schritt ist `CON-009` auf SQL Server 2019 evidenzseitig zu stabilisieren; daneben bleiben weitere Runtime-Evidenzmatrizen früherer Wellen offen. Kein `IMPLEMENTED`-Eintrag wird allein aufgrund statischer Ergebnisse auf `VALIDATED` gesetzt.
