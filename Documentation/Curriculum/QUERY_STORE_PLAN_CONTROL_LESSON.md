# Query-Store-Plansteuerung richtig einordnen

Diese Lehrnotiz ergänzt `LO-M06-04` und `LO-M06-08` in der
[Curriculumarchitektur](CURRICULUM_ARCHITECTURE.md). Sie erklärt den Unterschied
zwischen einer angeforderten Planerzwingung und dem Nachweis, welcher Plan bei
einer konkreten Ausführung tatsächlich verwendet wurde. Sie ist eine
Quellenerklärung mit schematischen Beispielen, keine freigegebene Demo und keine
Laufzeitqualifikation.

## Drei verschiedene Aussagen

Query Store speichert Abfrage-, Plan- und Laufzeitinformationen. Für eine
konkrete Diagnose sind drei Aussagen getrennt zu halten:

1. **Plan gespeichert:** Ein Plan ist im Query Store vorhanden.
2. **Planerzwingung angefordert:** `sys.query_store_plan.is_forced_plan = 1`
   zeigt den Forcing-Zustand an. Das garantiert nicht, dass genau dieser Plan
   erfolgreich kompiliert und verwendet wird.
3. **Plan bei einer Ausführung beobachtet:** Ein actual execution plan
   (tatsächlicher Ausführungsplan) oder eine passend gebundene Laufzeitevidenz
   muss zur konkreten Abfrage und Ausführung gehören. Eine erfolgreiche Antwort
   von `sp_query_store_force_plan` allein belegt diese Verwendung nicht.

Eine lesende Ausgangsprüfung kann die gespeicherten Pläne und ihren Status
anzeigen:

```sql
SELECT q.query_id, p.plan_id, p.is_forced_plan,
       p.force_failure_count, p.last_force_failure_reason_desc
FROM sys.query_store_query AS q
JOIN sys.query_store_plan AS p ON p.query_id = q.query_id
WHERE q.query_id = @query_id
ORDER BY p.plan_id;
```

`@query_id` steht hier für eine zuvor eindeutig aufgelöste Abfragekennung. Die
Abfrage allein löst weder eine eindeutige Identität auf noch beweist sie eine
aktuelle Ausführung. In einem kontrollierten Änderungsvorgang muss die
Abfrage-/Plan-Zuordnung zur richtigen Datenbank, zum Modul, vollständigen
Statementtext und Kontext passen; ein Hash oder ein beliebiger erster Treffer
reicht dafür nicht.

## Erzwingen und zurücknehmen

Die dokumentierte Prozedur `sys.sp_query_store_force_plan` fordert die
Erzwingung eines Query-/Plan-Paars an. Eine erfolgreiche Prozedurantwort ist
eine Annahme der Anforderung, keine Garantie des späteren Kompilierungs- oder
Ausführungsplans. Bei einem Fehler kann die Engine regulär optimieren; den
Fehlerzustand muss man im passenden Query-Store-Kontext prüfen.

`sys.sp_query_store_unforce_plan` nimmt die Erzwingung für das angegebene Paar
zurück. Ein sicherer Ablauf prüft vor der Änderung die exakte Zuordnung und den
vorhandenen Steuerzustand, protokolliert die Rücknahme und kontrolliert danach
den Status. Auch der Rücknahmewert allein belegt nicht, dass alle anderen
Steuerungswege entfernt oder verändert wurden.

Die Prozeduraufrufe sind hier absichtlich nicht als ausführbare Vorlage
abgedruckt: Die verfügbaren Argumente und Berechtigungen sind versionsabhängig.
Insbesondere optionale Argumente neuerer SQL-Server-Versionen dürfen nicht
ungeprüft auf ältere Versionen übertragen werden. Für jede Zielversion gelten
die verlinkten Herstellerreferenzen.

## Fehlerzustand und Aussagegrenze

`force_failure_count` und `last_force_failure_reason_desc` helfen, einen
fehlgeschlagenen Erzwingungsversuch einzuordnen. Der Zähler ist kein
Ausführungszähler; sein Zurücksetzen beim Übergang von nicht erzwungen zu
erzwungen schafft eine neue Zählepochen-Grenze. Ein gespeicherter Fehlergrund
oder ein gesetztes Force-Flag ersetzt nicht den Planbeleg der konkreten
Ausführung.

Diese Lehrnotiz behandelt ausschließlich klassische Planerzwingung und den
Kontrollzustand eines Inline-Hints. Sie behauptet weder einen Replay-Erfolg
noch einen Performancegewinn oder eine kausale Wirkung des Hints. Vergleiche
optimierter Replay-Verfahren, gespeicherte Query-Store-Hints und weitere
Fehlerklassen sind gesonderte, zurückgestellte Erweiterungen.

## Quellen und Geltungsbereich

- Microsoft Learn, [`sys.query_store_plan`](https://learn.microsoft.com/en-us/sql/relational-databases/system-catalog-views/sys-query-store-plan-transact-sql?view=sql-server-ver17): Planstatus und Forcing-Fehlerinformationen.
- Microsoft Learn, [`sp_query_store_force_plan`](https://learn.microsoft.com/en-us/sql/relational-databases/system-stored-procedures/sp-query-store-force-plan-transact-sql?view=sql-server-ver17): Erzwingungsanforderung und versionsabhängige Argumente.
- Microsoft Learn, [`sp_query_store_unforce_plan`](https://learn.microsoft.com/en-us/sql/relational-databases/system-stored-procedures/sp-query-store-unforce-plan-transact-sql?view=sql-server-ver17): Rücknahme und Berechtigungen.
- Das [Quellenregister SRC-027](../Research/SOURCE_REGISTER.md#dgn-004-detailverweise-zum-bestehenden-query-store-quellenumfang-src-027) enthält den projektspezifischen Aussagebezug und seine Grenzen.

Die Erklärung ändert keinen Demo- oder Runtime-Status. Die DGN-004-Laufzeit- und
Buildqualifikation bleibt offen, solange das YELLOW-Vorstartgate nicht erfüllt
ist.
