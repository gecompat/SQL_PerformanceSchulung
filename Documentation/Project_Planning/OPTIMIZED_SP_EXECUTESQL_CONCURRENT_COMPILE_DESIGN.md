# Methodenentwurf: konkurrierende Kompilierung mit `OPTIMIZED_SP_EXECUTESQL`

| Merkmal | Wert |
|---|---|
| Status | `METHOD_DRAFT` – keine Implementierungs- oder Runtimefreigabe |
| Geltungsbereich | Separater, isolierter SQL-Server-2025-Versuch zu gleichzeitigen `sp_executesql`-Aufrufen |
| Bestehende Demo | `QRY-004` bleibt unverändert und qualifiziert dieses Verhalten nicht |
| Produktquellen | `SRC-059`, `SRC-161`, `SRC-162`, `SRC-163` |

## Ziel und Grenze

Dieser Entwurf beschreibt, welche Bedingungen ein späterer Versuch erfüllen muss, bevor eine separate Demo entworfen oder ausgeführt werden kann. Er aktiviert keine Datenbankoption, führt kein SQL aus und behauptet weder eine beobachtete Serialisierung noch einen Leistungsgewinn. Die bestehende Entscheidung `DEFER` in der [SQL-Server-2025-Delta-Prüfung](SQL_SERVER_2025_DELTA_REVIEW.md) bleibt bestehen.

Microsoft dokumentiert, dass die datenbankbezogene Option ab SQL Server 2025 standardmäßig `OFF` ist und die Kompilierung identischer `sp_executesql`-Batchtexte serialisiert. Die verfügbaren Microsoft-Hinweise zu Compile-Locks beschreiben jedoch konkrete Sperrressourcen für Prozeduren und Trigger; daraus folgt keine belegte XE-Ereignis-/Feldzuordnung für dynamische `sp_executesql`-Batches. Diese Zuordnung ist ein vorgelagertes offenes Gate.

## Versuchsdesign nach Methodenfreigabe

1. **Getrennte Arme:** für jede gepaarte Wiederholung zwei frische, markergebundene Datenbanken derselben isolierten SQL Server 2025-Instanz. Schema, synthetische Daten, Kompatibilitätsstufe, Rechte, Statistiken und sonstige Optionen sind identisch; ausschließlich `OPTIMIZED_SP_EXECUTESQL` unterscheidet `OFF` und `ON`. Beide Zustände werden vor und nach jedem Arm verifiziert. Keine serverweite Konfiguration und kein globales Leeren des Plancaches.
2. **Feste Aufrufmenge:** derselbe byteidentische, parametrisierte dynamische Batchtext und dieselbe Parameterdefinition in allen Actors. Parameterwerte variieren dürfen, Batchtext und Datenbankkontext nicht. Eine zweite, absichtlich andere Batchtextgruppe dient nur als Negativkontrolle für die dokumentierte Gleichheitsbedingung.
3. **Synchronisierte Konkurrenz:** feste Actorzahl und Versuchszahl, gemeinsamer Client-Startbarrier, begrenzte Zeitüberschreitung und alternierende Reihenfolge der OFF-/ON-Arme. Die Daten bleiben während der Messfenster unverändert; jede Wiederholung nutzt ein neu provisioniertes, gepaartes Datenbankpaar mit leerem, dokumentiertem Datenbankplanbestand vor dem Startbarrier. Es wird kein Instanzcache geleert. Kein `DBCC FREEPROCCACHE`.
4. **Statistiken:** `AUTO_UPDATE_STATISTICS`- und Async-Einstellungen werden explizit erfasst und in beiden Armen gleich gehalten. Bei aktivierter automatischer Statistikaktualisierung wird die dokumentierte Empfehlung zu `AUTO_UPDATE_STATISTICS_ASYNC` und `ASYNC_STATS_UPDATE_WAIT_AT_LOW_PRIORITY` im Methodenreview bewertet. Statistikfrische und ein möglicher Lauf mit asynchron veralteten Statistiken dürfen nicht verschwiegen oder zwischen Armen vermischt werden.
5. **Evidenzbindung:** vor Implementierung ist auf dem exakten Enginebuild zu verifizieren, welche unterstützten Extended-Events (XE; gezielte SQL-Server-Ereigniserfassung) und Felder Kompilierung, Datenbank, Batchidentität, Session, Zeitfenster und relevante Waits zuverlässig binden. Die Session muss eng gefiltert, zeitlich begrenzt und nachweislich gestoppt/entfernt werden. Plan-Cache-Evidenz wird nur als ergänzende Zuordnung verwendet; sie allein beweist keine Zahl gleichzeitiger Kompilierungen.
6. **Auswertung:** OFF muss im ausgerichteten Zeitfenster mehrere tatsächliche Kompilierungen für die identische Batchgruppe nachweisen, bevor die Kontrollbehauptung zulässig ist. Für ON sind konkurrierende Compile-Waits und anschließende Planwiederverwendung mit batch- und zeitgebundener Evidenz zu belegen. Die abweichende Batchtextgruppe prüft, dass nicht fälschlich alle Texte als identisch behandelt werden. Ergebnisse, Fehler, Latenzverteilung, Compileaktivität und Waits werden getrennt berichtet; es gibt keinen vorab behaupteten Gewinner oder absoluten Performancegrenzwert.
7. **Abbruch und Cleanup:** fehlende Ereignisfelder, nicht eindeutige Batchzuordnung, fehlgeschlagene Barriere, Timeout, unerwartete Abweichung zwischen Armen oder unvollständiger Cleanup ergeben `NOT_PROVEN` beziehungsweise einen expliziten Skip-/Failstatus. Vorher-/Nachherzustand aller Datenbankoptionen, XE-Session, Datenbanken und Testobjekte wird geprüft. Der Cleanup darf nur vollständige Projekt-/Vertrags-/Demo-/RunToken-Marker entfernen.

## Gates vor einer Implementierung

- Unabhängiger Methodenreview bestätigt Buildbindung, Ereignis-/Feldvertrag, Auswertungsregeln, Statistikbehandlung, Sicherheitsklasse und Restore.
- Ein Wegwerfziel mit SQL Server 2025 und reproduzierbarem Cleanup ist verfügbar. SQL Server 2019/2022 führen keinen Versuch aus; falls sie im späteren Runner auftauchen, muss der Versions-Skip vor jeder Mutation erfolgen.
- Der vollständige Versuch ist auf dem freigegebenen Build zunächst pilotiert. Fehlende oder mehrdeutige Evidenz bleibt `NOT_PROVEN`; sie darf nicht durch eine Quelltextannahme oder ältere `QRY-004`-Ergebnisse ersetzt werden.
- Erst nach bestandenen Gates werden eigene Demo-ID, ausführbarer Vertrag, Tests und Runtime-Matrix vorgeschlagen. Dieser Entwurf erteilt diese Freigaben nicht.

## Quellen und Aussagegrenzen

- `SRC-059` dokumentiert Option, Verfügbarkeit, Default, gleiche Batchtexte und Statistikempfehlung.
- `SRC-161` beschreibt Compile-Lock-Diagnosebeispiele für Prozeduren/Trigger. Es ist keine Evidenz für die exakte dynamische Batchressource.
- `SRC-162` weist auf möglichen Diagnoseoverhead breit erfasster Compile-/Showplan-Ereignisse hin; daher sind Filterung und Zeitbegrenzung Teil des Designs.
- `SRC-163` dokumentiert, wie Extended-Events-Pakete, Ereignisse, Actions und deren Metadaten aus den XE-Systemkatalogen gelesen werden. Die neue [read-only Katalogabfrage](../../Tests/Runtime/optsp_xe_catalog_probe.sql) prüft diese Metadaten auf SQL Server 2025 in einem kurzlebigen CI-Container. Selbst ein erfolgreicher Kataloglauf belegt nur verfügbare Ereignis-/Action-Schemas auf genau diesem Build; er belegt weder, dass ein Ereignis bei `sp_executesql` feuert, noch konkurrierende Compile-Waits oder Planwiederverwendung.

Der Entwurf ist ein prüfbarer Methodenstand, keine Produkt- oder Enginequalifikation. Die menschliche Generalprobe ist ausgeschlossen.
