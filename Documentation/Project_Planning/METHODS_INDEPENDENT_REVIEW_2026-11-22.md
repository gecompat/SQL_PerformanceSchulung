# Unabhängige Methodenreviews: DGN-007, CON-006 und IDX-007

| Merkmal | Wert |
|---|---|
| Datum | 22. November 2026 |
| Prüfumfang | aktuelle Methodenentwürfe, dazugehörige Offlineverträge und ausgewählte Primärquellen |
| Prüfform | drei getrennte, read-only Reviews und unabhängige Nachprüfung der Korrekturen |
| SQL-/Engineausführung | keine |
| Gesamtbefund | keine offenen P1/P2 im geprüften Methodenumfang; alle drei Varianten bleiben Draft/Proposed mit getrennten Build-/Runtimegates |

Die Reviewer bearbeiteten DGN-007, CON-006 und IDX-007 separat und änderten
keine Dateien. Die erste Gegenprüfung bezog sich auf `origin/main` bei
`13086b28`; Folgereviews prüften die in diesem Branch vorgenommenen Korrekturen
read-only. Die Offlineprüfungen und lokalen Regressionen im Folgenden führte
der Implementierungsverantwortliche aus; sie sind keine Reviewer-Läufe.

## DGN-007 – Fensterzuordnung über Extended Events

**Erstbefunde.** Der erste Entwurf zählte nur Statement-Abschlüsse zwischen
Fenstermarkern. Ein Request aus einem vorherigen Fenster hätte nach dem nächsten
Beginmarker abschließen und falsch zugeordnet werden können. Zusätzlich war
nicht konkret ausgeschlossen, dass ein XE-Target Statementtext oder
parameterhaltige Daten speichert.

**Korrektur.** Der Entwurf verlangt nun vor jedem Beginmarker idle Actor-
Verbindungen, je erwarteten Request Start- und Abschlussereignisse innerhalb
desselben Markerpaares und dieselbe Session-/Requestbindung. Cross-window-
Paare, fehlende Events, nicht-idle Actors und mehrdeutige Zuordnung werden
`NOT_PROVEN`; Folgefenster warten auf bestätigten Drain/Reset. Eine pro Build
geprüfte Event-/Action-Allowlist muss Statementtext, Parameter, Eingabepuffer,
Showplan und andere vertrauliche Payload ausschließen. Wenn das Event diese
Felder zwingend speichert, ist der Kandidat unter der aktuellen Datenschutz-
grenze nicht verwendbar. Targets und eigene Session benötigen begrenztes
Cleanup auf jedem Ausgangspfad.

**Nachprüfung.** Keine offenen P1/P2 im geprüften Draft. Ungeprüft bleiben
Ereignis-/Actionverfügbarkeit, `event_sequence`-Ordnung, Verlustanzeigen,
Hashkardinalität, Query-Store-Sichtbarkeit, Datenschutz-Allowlist und Cleanup
auf jedem Zielbuild. `METHOD_DRAFT` bleibt bestehen; keine XE-Session wurde
erstellt.

## CON-006 – Range-Deadlockvariante

**Erstbefunde.** Der Graphchecker akzeptierte beliebige nichtleere
`requestType`-Werte, ohne deren Bedeutung zu prüfen. Außerdem prüfte die
Range-Captureevidenz zwar Graphopfer/Survivor, aber nicht Rollback und finalen
Tabellenzustand des Deadlockarms. Für den späteren Pilot fehlten konkrete
Zeit- und Recoverygrenzen.

**Korrektur.** Das Rangeprofil akzeptiert ausschließlich
`requestType="wait"`; Konversionsanforderungen gehören nicht zu diesem
Kandidaten. Der neue `RangeCaptureEvidence`-Vertrag bindet die beiden
Actorinsertionsschlüssel, erwartet Opferrollback mit Fehler 1205, bestätigte
Survivor-Einfügung und den vollständigen Endbestand aus Anfangsbestand plus
Survivor-Schlüssel. Der Draft schlägt je Mehrsessionarm höchstens 45 Sekunden,
180 Sekunden Gesamtlaufzeit und 60 Sekunden Cleanup vor. Actorclients werden
zuerst begrenzt abgebrochen; eine Sessionterminierung darf nie auf einer
gespeicherten SPID allein beruhen, sondern erfordert eine frische Marker-,
Login-, Datenbank- und SPIDprüfung. Bleibt Rollback aktiv, kann nur der frisch
verifizierte eigene Wegwerfcontainer entfernt werden. Ziele ohne verifizierbaren
Containerbesitz erhalten keinen automatischen Force-Recovery-Pfad.

**Nachprüfung.** Keine offenen P1/P2 im geprüften Draft. Ein reales Engine-
Deadlockgraph, Insertresultate, Buildmatrix, Actorabbruch, Rollback und Cleanup
sind nicht ausgeführt oder belegt. Die vorgeschlagenen Grenzen müssen vor einem
Pilot eingehalten und als Runtimevertrag implementiert werden. Status bleibt
`PROPOSED`.

## IDX-007 – Wait-/Blattkettenvertrag

**Erstbefunde.** Ein caller-gelieferter Endmarker konnte eine synthetisch
konsistente Kette als `PASS` markieren, ohne die Terminalsemantik eines
SQL-Server-Builds nachzuweisen. Der Waitchecker bildete auch die im Methoden-
entwurf verlangten zwei Waitränder nicht ab. Schließlich prüfte er
caller-gelieferte Request-/Taskfelder, obwohl dafür die Task-/Requestzuordnung
bei der künftigen DMV-Erhebung noch nicht spezifiziert war.

**Korrektur.** Die Checker heißen jetzt
`evaluate_supplied_page_chain_consistency` und
`evaluate_last_page_wait_snapshot_consistency`; Rückgaben benennen die
Callerwerte als intern konsistent und attestieren weder Herkunft, echte
Terminalsemantik noch Mehrsampleüberlappung. Die Taskzuordnung im Methodendraft
verlangt den eindeutigen Join
`sys.dm_os_waiting_tasks.waiting_task_address` →
`sys.dm_os_tasks.task_address`; `request_id` stammt aus dem Taskdatensatz.
`SRC-174` registriert die Microsoft-Quelle. Die Offlinerecords besitzen keine
Taskadresse und verifizieren diesen Join ausdrücklich nicht. `rightmost_leaf_claim`
ist nur eine Callerbehauptung.

**Nachprüfung.** Keine offenen P1/P2 im geprüften Draft und der benannten
Offlineverträge. Zwei geordnete Waitcapturen, der Taskadressjoin im Build,
Terminalkodierung, Split-/Mutationsverhalten, Seiten-/Zeit-/Ausgabegrenzen,
Berechtigungen und Cleanup bleiben ungeprüfte Implementierungs- und
Runtimegates. Die Variante bleibt `METHOD_DRAFT`.

## Quellen, Grenzen und lokale Prüfungen

Die Prüfer stützten die Aussagen auf die registrierten Primärquellen: Microsoft
[Deadlocks guide](https://learn.microsoft.com/en-us/sql/relational-databases/sql-server-deadlocks-guide?view=sql-server-ver17),
[Locking and row versioning guide](https://learn.microsoft.com/en-us/sql/relational-databases/sql-server-transaction-locking-and-row-versioning-guide?view=sql-server-ver17),
[Extended Events quickstart](https://learn.microsoft.com/en-us/sql/relational-databases/extended-events/quick-start-extended-events-in-sql-server?view=sql-server-ver17),
[sys.dm_os_tasks](https://learn.microsoft.com/en-us/sql/relational-databases/system-dynamic-management-views/sys-dm-os-tasks-transact-sql?view=sql-server-ver17),
[sys.dm_os_waiting_tasks](https://learn.microsoft.com/en-us/sql/relational-databases/system-dynamic-management-views/sys-dm-os-waiting-tasks-transact-sql?view=sql-server-ver17)
und [sys.dm_db_page_info](https://learn.microsoft.com/en-us/sql/relational-databases/system-dynamic-management-views/sys-dm-db-page-info-transact-sql?view=sql-server-ver17).
Die physischen Range-Keyzuordnungen, XE-Marker-/Hashkardinalität, Taskjoin-
Zeitstabilität, Seitenendkodierung und laufende Cleanupwirkung bleiben
Empiriefragen; aus Dokumentation oder synthetischem PASS folgt kein
Enginebefund.

Nach den Korrekturen bestanden 16 CON-006-Rangegraphregressionen, 20
CON-006-Konversionsregressionen und 20 IDX-007-Vertragsregressionen. Außerdem
bestanden Identifier-Registration, Repository-Continuity, Framework-Contracts,
Foundation-Integration und `git diff --check`. Es gab keine SQL- oder
Runtimeausführung.
