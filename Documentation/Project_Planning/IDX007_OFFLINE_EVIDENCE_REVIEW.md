# IDX-007 – Fachliche Prüfung des Offline-Evidenzvertrags

| Merkmal | Wert |
|---|---|
| Prüfart | lokale Vertragsprüfung, nicht unabhängig |
| Geprüfter Vertrag | `Tests/Static/idx007_last_page_contract.py` |
| Geltungsbereich | Konsistenz caller-gelieferter Wait- und Seitenfelder |
| Laufstatus | keine SQL-, Lab- oder Runtimeausführung |

## Gebundene Evidenz

Microsoft beschreibt `PAGELATCH_EX` als konkurrierenden Zugriff auf eine im
Bufferpool gehaltene Seite und grenzt ihn von `PAGEIOLATCH_EX` für I/O ab.
Für Last-Page-Insert-Contention nennt die Diagnose mehrere Sessions und die
Identifikation der betroffenen Datenbank-/Datei-/Seitenressource. Ein
sequentieller Indexschlüssel allein genügt nicht als Diagnose. `SRC-072` und
`SRC-073` begründen diese Trennung und die workloadabhängige Eignung von
`OPTIMIZE_FOR_SEQUENTIAL_KEY`.

`sys.dm_os_waiting_tasks` liefert wartende Tasks mit `session_id`, `wait_type`,
Wartezeit und Ressourcenbeschreibung. Für Latch-Owner nennt Microsoft die
Form `dbid:fileid:page`; die `pagelock`-Form gehört dagegen zur Lock-Ressource
(`SRC-147`). `sys.dm_db_page_info` liefert unter anderem `page_level`, Objekt-/
Indexkennung und vorherige/nächste Seitenkennung. Die Funktion arbeitet auf
einer einzelnen angefragten Seite und liefert Headerdaten; sie belegt allein
weder eine stabile aktuelle Rechtsaußenposition noch deren Verlauf
(`SRC-148`). Eine passende Seitenkettenauflösung bleibt ein separates
empirisches Gate.

## Prüferbefund

Der Offline-Prüfer ist bewusst nur ein Konsistenzfilter: zwei unterschiedliche
Sessionkennungen, identische Seitenadresse und derselbe RFC-3339-Zeitpunkt,
Blattebene sowie eine
separat gelieferte Rechtsaußen-Aussage reichen für `PASS`. Da alle Werte vom
Caller stammen, ist das weder authentische Beobachtung noch ein Laufzeit- oder
Engpassnachweis.

Eine Lücke lag in der Unterscheidung zwischen fehlender und widersprechender
Rechtsaußen-Evidenz. `rightmost_leaf=None` bedeutet, dass die Position nicht
belegt ist, und bleibt `NOT_PROVEN`. `rightmost_leaf=False` ist ein expliziter
Gegenbeleg zur für diesen Vertrag erforderlichen Rechtsaußen-Seite und wird nun
als `FAIL` gewertet. Das verhindert, dass ein bekannter Widerspruch wie bloße
Abwesenheit von Evidenz erscheint. Ein synthetischer Regressionstest bindet
beide Zustände getrennt. Zeitstempel müssen jetzt ein gültiges RFC-3339-Datum
mit explizitem Offset enthalten; Gleichheit wird über den normalisierten
Zeitpunkt statt über die Schreibweise bestimmt. Synthetische Fälle decken
ungültige Kalenderdaten, fehlenden oder als unbekannt markierten Offset und
gleichwertige Offsetdarstellungen ab. Ein gültiger lokaler Zeitwert, dessen
Offsetnormalisierung den unterstützten Datumsbereich verlässt, wird als
ungültig abgewiesen, statt die Auswertung mit einer Ausnahme zu beenden.

## Verbleibende Gates

Der Vertrag authentifiziert weder Herkunft noch Vollständigkeit der Wait-
Momentaufnahme. Er misst keine Warteüberlappung über längere Zeit, keinen
Durchsatz und keine Performancewirkung. Ein späterer Lauf muss die echten
Wait-Ressourcen den konkreten Indexseiten zuordnen, Rechtsaußenstatus durch
geeignete aktuelle Seitenketten-/Metadatenevidenz belegen und den Vergleich
mit identischer Workload kontrollieren. Eine unabhängige Methoden-/Quellen-
freigabe, ein konkreter Demo-/Cleanupvertrag und eine getrennte
Runtimeautorisierung bleiben erforderlich. Diese Prüfung erteilt keine davon.
