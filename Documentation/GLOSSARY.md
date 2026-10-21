# Begriffe, Abkürzungen und Kennungen

Hier finden Sie kurze Erklärungen zu den Kürzeln der Schulung. Kennungen dienen
der eindeutigen Zuordnung; das Thema und die Beschreibung erklären den Inhalt.

## Fachbegriffe

| Kürzel | Langform | Bedeutung |
|---|---|---|
| ADR | Accelerated Database Recovery | beschleunigte Datenbankwiederherstellung. |
| ANN | Approximate Nearest Neighbor | näherungsweise Suche nach ähnlichen Vektoren. |
| API | Application Programming Interface | Programmierschnittstelle. |
| CE | Cardinality Estimation | Schätzung der Zeilenanzahl. |
| CI | Continuous Integration | automatisierte Integrationsprüfungen. |
| CPU | Central Processing Unit | Prozessor. |
| CTE | Common Table Expression | benannter Abfrageausdruck innerhalb einer Anweisung. |
| CU | Cumulative Update | kumulatives Produktupdate. |
| DDL | Data Definition Language | Anweisungen zum Definieren und Ändern von Datenbankobjekten. |
| DML | Data Manipulation Language | Anweisungen zum Lesen oder Ändern von Daten. |
| DMV | Dynamic Management View | dynamische Verwaltungssicht für Diagnoseinformationen. |
| DMVs | Dynamic Management Views | dynamische Verwaltungssichten für Diagnoseinformationen. |
| DOP | Degree of Parallelism | Parallelitätsgrad einer Ausführung. |
| EOF | End of File | Ende eines Eingabestroms. |
| FK | Foreign Key | Fremdschlüssel. |
| GA | General Availability | allgemeine Produktverfügbarkeit. |
| HTTP | Hypertext Transfer Protocol | Protokoll zur Übertragung von Webanfragen und Antworten. |
| I/O | Input/Output | Ein- und Ausgabezugriffe. |
| IQP | Intelligent Query Processing | SQL-Server-Funktionen zur intelligenten Abfrageverarbeitung. |
| JSON | JavaScript Object Notation | strukturiertes Textformat. |
| KI | künstliche Intelligenz | Verfahren für Aufgaben wie Textverarbeitung oder Vorhersagen. |
| LAQ | Lock After Qualification | Sperren erst nach Prüfung der Zeilenqualifikation. |
| LLM | Large Language Model | großes Sprachmodell. |
| MAXDOP | Maximum Degree of Parallelism | konfigurierte Grenze für den Parallelitätsgrad. |
| MCP | Model Context Protocol | Protokoll zur Anbindung von Werkzeugen und Kontextquellen. |
| MSTVF | Multi-Statement Table-Valued Function | tabellenliefernde Funktion mit mehreren Anweisungen. |
| OLAP | Online Analytical Processing | analytische Datenverarbeitung. |
| OLTP | Online Transaction Processing | transaktionsorientierte Datenverarbeitung. |
| ONNX | Open Neural Network Exchange | Austauschformat für Modelle. |
| OPPO | Optional Parameter Plan Optimization | Planoptimierung für optionale Parameter. |
| OS | Operating System | Betriebssystem. |
| PID | Process Identifier | Prozesskennung. |
| PK | Primary Key | Primärschlüssel. |
| PSP | Parameter Sensitive Plan Optimization | Planoptimierung für unterschiedliche Parameterwerte. |
| RAG | Retrieval-Augmented Generation | Antworterzeugung mit zuvor ausgewählten Quellen. |
| RAM | Random Access Memory | Arbeitsspeicher. |
| RCSI | Read Committed Snapshot Isolation | zeilenversionierte Variante von READ COMMITTED. |
| REST | Representational State Transfer | Architekturstil für Webschnittstellen. |
| RID | Row Identifier | physischer Zeilenverweis. |
| RLS | Row-Level Security | zeilenbezogene Zugriffskontrolle. |
| SARGability | Search ARGument-able | Eigenschaft eines Prädikats, als Suchargument für einen Indexzugriff nutzbar zu sein. |
| SDK | Software Development Kit | Entwicklungswerkzeuge und Bibliotheken. |
| SSMS | SQL Server Management Studio | Verwaltungs- und Abfragewerkzeug. |
| T-SQL | Transact-SQL | SQL-Server-Dialekt der Abfragesprache SQL. |
| TDS | Tabular Data Stream | Übertragungsprotokoll zwischen SQL-Client und Server. |
| TID | Transaction ID | Transaktionskennung. |
| TLS | Transport Layer Security | Verschlüsselungsprotokoll für Verbindungen. |
| TVF | Table-Valued Function | tabellenliefernde Funktion. |
| TVP | Table-Valued Parameter | tabellenwertiger Parameter. |
| UDF | User-Defined Function | benutzerdefinierte Funktion. |
| VLF | Virtual Log File | interner Abschnitt einer Transaktionslogdatei. |
| VLFs | Virtual Log Files | interne Abschnitte einer Transaktionslogdatei. |
| XE | Extended Events | gezielte Ereigniserfassung in SQL Server. |
| XML | Extensible Markup Language | Format zur strukturierten Darstellung von Daten. |

## Kennungen lesen

| Familie | Bedeutung |
|---|---|
| OPT | Demos zu Optimizer, Statistiken und Ausführungsplänen. |
| QRY | Demos zu Abfragemustern und SQL-Lösungen. |
| IDX | Demos zu Indizes und ihren Kosten. |
| STL | Demos zu Speicherung, Datenseiten und Transaktionslog. |
| CON | Demos zu Parallelzugriffen, Sperren und Isolation. |
| DGN | Demos zu Diagnose und Beobachtung. |
| RES | Demos zu Ressourcenverbrauch und Wartezeiten. |
| FWK | Gemeinsamer technischer Vertrag für Demos. |
| CUR / LO | Curriculumeinheit beziehungsweise Lernziel (Learning Objective). |
| SRC / CLM | Fachquelle beziehungsweise fachliche Aussage (Claim). |
| PRS / TST | Präsentations- beziehungsweise Testarbeitspaket. |
| TSK / DEC | Entwicklungsaufgabe beziehungsweise dokumentierte Projektentscheidung. |
| TP | Testprofil; TP-PERF ergänzt Laufprüfungen um Performanceerwartungen und Abbruchgrenzen. |

Beispiel: `QRY-001` bezeichnet die Demo zu indexfreundlichen Suchbedingungen.
Die Ziffern sind eine stabile Zuordnung und keine Ausführungsreihenfolge.
Die konkreten Themen stehen im [Demo-Katalog](Demo_Catalog/README.md);
die Zuordnung der Lernziele und Testprofile steht in der
[Traceability-Matrix](Curriculum/TRACEABILITY_MATRIX.md).

## Vertiefung und Quellen

Die Begriffshilfe ersetzt keine Versions-, Berechtigungs- oder Ausführungsvoraussetzungen.
Produktbegriffe folgen den zugeordneten Primärquellen. Geprüft am 21. Oktober 2026:

- [Indexfreundliche Suchbedingungen und SARGability](https://learn.microsoft.com/en-us/troubleshoot/sql/performance/troubleshoot-high-cpu-usage-issues).
- [Parametersensitive Planoptimierung](https://learn.microsoft.com/en-us/sql/relational-databases/performance/parameter-sensitivity-plan-optimization?view=sql-server-ver17).
- [Planoptimierung für optionale Parameter](https://learn.microsoft.com/en-us/sql/relational-databases/performance/optional-parameter-optimization?view=sql-server-ver17).
- [Zeilenbezogene Zugriffskontrolle](https://learn.microsoft.com/en-us/sql/relational-databases/security/row-level-security?view=sql-server-ver17).
- [Virtuelle Abschnitte des Transaktionslogs](https://learn.microsoft.com/en-us/sql/relational-databases/system-dynamic-management-objects/sys-dm-db-log-info-transact-sql?view=sql-server-ver17).
- [Optimized Locking, Transaktionskennungen und Sperren nach Qualifikation](https://learn.microsoft.com/en-us/sql/relational-databases/performance/optimized-locking?view=sql-server-ver17).
- [ONNX-Modellaustauschformat](https://onnx.ai/onnx/intro/).
- [Model Context Protocol](https://modelcontextprotocol.io/docs/getting-started/intro).
- [Ausführliches Begriffsglossar zum Offline-KI-Kurs](HowTo/SQL_SERVER_2025_AI_OFFLINE_GLOSSARY.md).
