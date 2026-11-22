# Deadlockvarianten am Konfliktgraph unterscheiden

Diese Lehrnotiz ergänzt `LO-M05-03` in der
[Curriculumarchitektur](CURRICULUM_ARCHITECTURE.md). Sie unterscheidet den
Deadlock aus Gegenreihenfolge, Sperrumwandlung und gekreuzten Einfügungen in
getrennte Schlüsselbereiche. Das
[CON-006-Demo](../../Demos/07_Concurrency/CON-006_Deadlock_Cycle/README.md)
enthält für alle drei Varianten eigene Phasen und Gegenproben. Die vollständige
Runtime-Qualifikation der aktuellen Demo ist für SQL Server 2019, 2022 und 2025
bestanden. Die tatsächlichen Graphen werden pro Lauf gebunden geprüft;
synthetische Graphprüfungen ersetzen diese Laufzeitevidenz nicht.

## Gegenreihenfolge und Sperrumwandlung

Beim bekannten Gegenreihenfolgefall halten zwei Transaktionen jeweils eine
exklusive Sperre auf unterschiedlichen Ressourcen und fordern anschließend die
Ressource der anderen an. Der Zyklus verläuft über zwei Ressourcen.

Bei einem Sperrumwandlungsfall können zwei Transaktionen unter `REPEATABLE READ`
oder `SERIALIZABLE` dieselbe Zeile zunächst mit einer gemeinsamen `S`-Sperre
lesen und diese Sperre bis zum Transaktionsende behalten. Wenn beide danach
dieselbe Zeile ändern wollen, benötigt jede eine exklusive `X`-Sperre. Jede
`X`-Anforderung wartet dann auf die noch gehaltene `S`-Sperre der jeweils
anderen Transaktion. Der Zyklus entsteht durch die Umwandlungsanforderungen an
derselben Ressource, nicht durch eine umgekehrte Reihenfolge zweier Zeilen.
In der CON-006-Variante stammen die konkrete Zeilenidentität und die beiden
Zugriffe auf `RowId=1` aus den fixierten Session-Skripten. Der Deadlockgraph
bestätigt Datenbank, Objekt, Index und HoBT sowie die gegenläufigen Modi; er
enthält in diesem Vertrag keinen ausgewerteten Schlüsselwert. Ein reiner
Graph-PASS darf deshalb nicht als eigenständiger Beleg derselben Zeile gelesen
werden.

Microsoft beschreibt `UPDLOCK` beim Lesen der später zu ändernden Zeile als
mögliche Gegenmaßnahme für dieses Muster: Eine `U`-Sperre serialisiert die
konkurrierende Änderungsabsicht früher, bevor beide Transaktionen eine `S`-zu-`X`-
Umwandlung anfordern. Das ist keine allgemeine Deadlockfreiheit-Garantie.
Isolation, Zeilenversionierung, Indizes und Optimized Locking können das
beobachtete Sperrbild beeinflussen. Prüfen Sie die Wirkung im konkreten
Workload und ändern Sie keine Sperrhinweise pauschal.

## Eine Variante braucht eigene Evidenz

Ein Szenariotitel, ein `UPDATE`-Statement oder ein synthetisches XML-Fragment
beweist keinen bestimmten Konfliktgraphen. Für eine reale Variante müssen
Deadlockereignis und beide Teilnehmer an denselben Lauf gebunden werden. Der
Graph muss die tatsächlichen Ressourcen, gehaltenen und angeforderten
Sperrmodi sowie das Opfer zeigen. Für das Opfer ist Fehler 1205 zuzuordnen;
der Gegenpart muss nach dem Ereignis erfolgreich oder mit seinem tatsächlichen
Status nachgewiesen werden. Ein fehlender Graph in einer begrenzten
`system_health`-Sichtung ist kein Beweis, dass kein Deadlock aufgetreten ist.

Der vorhandene CON-006-Gegenreihenfolgefall bleibt der praktische Einstieg.
Die ergänzte Sperrumwandlungsvariante prüft denselben Datensatz: beide
Transaktionen lesen ihn unter `REPEATABLE READ`, bevor beide ein Update
anfordern. Die anschließende Gegenprobe verwendet `UPDLOCK` beim Lesen, sodass
die Änderungsabsicht vor der Konkurrenz um `X` serialisiert wird. Das ist eine
gezielte Mustergegenprobe, keine allgemeine Garantie gegen Deadlocks. Der
separate
[Offline-Review](../Project_Planning/CON006_OFFLINE_EVIDENCE_REVIEW.md)
prüft nur synthetisch übergebene Daten und attestiert keine SQL-Server-Evidenz.
Der ausführbare Offlinevertrag liegt in
[`con006_conversion_graph_contract.py`](../../Tests/Static/con006_conversion_graph_contract.py);
seine 20 synthetischen Regressionen stehen in
[`test_con006_conversion_graph_contract.py`](../../Tests/Static/test_con006_conversion_graph_contract.py).
Beide prüfen die Struktur und innere Konsistenz caller-gelieferter Werte; sie
lesen keine `system_health`-Ereignisse und qualifizieren kein Enginebuild.

## Schlüsselbereichs-Deadlock

Der geplante `CON-002`-Fall soll zeigen, wie ein `SERIALIZABLE`-Bereichsschutz
einen einzelnen Einfügeversuch blockiert, bis die Lesetransaktion endet. Die
CON-006-Rangevariante zeigt einen anderen Ablauf: Zwei Transaktionen lesen
getrennte leere Bereiche, deren Einfügungen auf unterschiedlichen
Indexressourcen blockieren. Der Beobachter bestätigt beide KEY-Range-Sperren,
gibt A frei, sieht A auf B warten und gibt erst danach B frei. Der Zyklus,
das Opfer und der Survivor werden aus dem tatsächlichen Deadlockgraphen und
den Actorresultaten bestätigt.

Unterschiedliche Prädikate beweisen weder getrennte noch gemeinsame
Sperrressourcen. Maßgeblich sind die im jeweiligen Lauf gebundenen KEY-Ressourcen
und Sperrmodi im Deadlockgraphen. Der
[Range-Methoden- und Qualifikationsnachweis](../Project_Planning/CON006_RANGE_DEADLOCK_METHOD.md)
beschreibt den Ablauf und die Grenzen der drei Buildläufe.

Die Herstellerdokumentation bezeichnet `RangeS-S` als Sperre einer
`SERIALIZABLE`-Bereichslesung und `RangeI-N` als Einfügebereichsprüfung; für
überlappende Bereiche sind diese Modi inkompatibel (`SRC-004`). Das erklärt,
warum der Konflikt plausibel ist, ersetzt aber nicht den laufgebundenen Nachweis
der tatsächlichen KEY-Ressourcen und Wait-Kanten. Für SQL Server 2025 wird der
Optimized-Locking-Zustand in der isolierten Machbarkeitsmatrix zusätzlich
festgehalten; die konkrete Graphausgabe bleibt bei jedem Demo-Lauf Pflicht.

## Quellen

- Microsoft Learn, [Transaction locking and row versioning guide](https://learn.microsoft.com/en-us/sql/relational-databases/sql-server-transaction-locking-and-row-versioning-guide?view=sql-server-ver17): zurückgehaltene gemeinsame Sperren, Konversion zu `X`, `UPDLOCK`-Muster und Schlüsselbereichssperren.
- Microsoft Learn, [Deadlocks guide](https://learn.microsoft.com/en-us/sql/relational-databases/sql-server-deadlocks-guide?view=sql-server-ver17): Deadlockgraph, `xml_deadlock_report` und Opferfehler 1205.
- Das [Quellenregister](../Research/SOURCE_REGISTER.md) führt die Deadlock-, Sperr- und `system_health`-Quellen unter `SRC-004`, `SRC-066` und `SRC-068`; die konkreten Aussage- und Provenienzgrenzen fasst der [CON-006-Offline-Review](../Project_Planning/CON006_OFFLINE_EVIDENCE_REVIEW.md) zusammen.

Die Erklärung ergänzt den Lernpfad und beschreibt die drei buildqualifizierten
CON-006-Varianten. Der Range-Deadlock erweitert nicht den geplanten
CON-002-Einzelwait.
