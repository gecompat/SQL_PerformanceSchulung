# TSK-006 – einzelner Parser-/Previewdiagnoseentscheid

Stand: 2026-10-11. PENDING_USER_DECISION. Keine neue SQL-Ausführung oder
Korrekturquelle. Der [Wiederaufnahmecheckpoint](SQL_SERVER_2025_AI_ANN_RESUME_REVIEW.md)
bleibt FAIL; beide zusätzlichen Kandidaten sind verbraucht und ihre Container
abwesend. Ungenutzte Containerplätze setzen das Kandidatenbudget nicht zurück.

## Empfehlung und enger Entscheid

Empfohlen wird genau ein neuer privater Diagnosekandidat, ein neuer eigener
Container und höchstens zwei feste Parseraufrufe mit identischem SQL-Text.
Keine Korrekturwelle oder zusätzliche Probe bei Fehler. Kein Indexbuild,
VECTOR_SEARCH, Performanceversuch oder automatischer Übergang in eine vollständige
ANN-Implementierung. Auch ein positiver Parserbefund benötigt danach einen neuen
begründeten Implementierungsumfang; IDX-011/IDX-012 bleiben PROPOSED.

Ziel ist ausschließlich festzustellen, ob die dokumentierte CREATE-VECTOR-INDEX-
Syntax am freigegebenen Build vor/nach Preview-Enable von einem frischen seriellen
SQL-Client geparst wird. Die letzte Probe enthielt Enable und dynamische DDL im
gleichen äußeren Batch und erfasste den tatsächlichen Previewwert unmittelbar vor
DDL nicht separat. Eine Batch-/Sessionursache ist eine Hypothese, kein Befund.

[SET PARSEONLY, SRC-105](https://learn.microsoft.com/en-us/sql/t-sql/statements/set-parseonly-transact-sql?view=sql-server-ver17)
prüft Syntax ohne Kompilierung oder Ausführung. Die Herstellerbeispiele für
[PREVIEW_FEATURES, SRC-107](https://learn.microsoft.com/sql/sql-server/preview-features-faq)
trennen Enable und Abfrage durch GO. Dies belegt keine Ursache des beobachteten
Fehlers 343, begründet aber den geänderten, kontrollierbaren Diagnoseeingang.
Ein Syntaxbefund belegt weder Objektbindung noch Indexbau oder Suchfähigkeit.

## Effekte und harte Grenzen

Es gelten weiterhin vollständige lokale Image-ID
`78eb6a93ef20501bd754282cc216188a0acee1cfa6119c33eef0b21599c1f726`, Build
17.0.5005.3, Enterprise Developer/EngineEdition 3, Linux Ubuntu 24.04, vier CPUs/
sechs GiB, eigene Loopbackbindung, CL170/SIMPLE sowie 256/64-MB-Dateilimits.
Start unmittelbar mit der Image-ID, danach vollständige CID-/Image-/Ownerprüfung.
Keine vorhandene Instanz oder andere Repositoryquelle verändern.

Nur eigene SQLPERF_LAB_IDX011_<RunToken> mit vier vollständigen bytegenauen Markern,
vollständiger persistenter Previewbaseline 0/1 und höchstens einer gleichzeitig
aktiven SQL-Session. Der einzige vorübergehende DB-Konfigurationseffekt bleibt
PREVIEW_FEATURES=ON; anschließend tatsächlicher Restore auf den gespeicherten Wert.
Die Baseline erfordert genau eine eigene gebundene Row. Kein Default 0 bei fehlender,
NULL-, doppelter oder ungültiger Baseline. Keine Cloud-/ONNX-/Credential-/TLS-/Host-
oder ALLOW_STALE_VECTOR_INDEX-Erweiterung und kein zusätzlicher MAXDOP-Effekt.

Die eigene DB enthält ausschließlich die notwendige persistente Baseline und
Markierung. `lab.VectorFixture` und alle Vector Indizes müssen vor/nach jedem
Parseraufruf tatsächlich abwesend sein. Es werden keine Vektordaten geladen;
maximal eine synthetische Baseline-Row. Die geparste DDL referenziert bewusst die
abwesende Tabelle: auch ein versehentlicher Ausführungsversuch kann hier keinen
Index auf vorhandenem Datenbestand bauen. PARSEONLY wird ausschließlich im eigenen
kurzlebigen Client gesetzt, nicht in einer Prozedur oder einem Trigger.

## Festgelegte Diagnosefolge

1. Quellen-/Effektreview vor SQL: tatsächlicher PARSEONLY-Text und Clientauswahl,
   Marker/Baseline und unveränderte gemeinsame Cleanupgrenzen. Vorhandene gültige
   Recovery-/Deadlineanalyse wiederverwenden; neue Deltas eng prüfen.
2. Genau eine neue eigene Instanz erzeugen, Build/Edition/OS/Image/CID/Owner/Loopback
   prüfen. Eigene DB markieren, Baseline persistent sichern und ihre tatsächliche
   0/1 ausgeben. Noch kein Preview-Enable und kein Fixture-/Indexbuild.
3. Tatsächlichen Previewwert und DB-Kontext in einem separaten neuen Client binden.
   Bei Baseline 0 die erste feste Parserprobe im Ausgangszustand ausführen. Bei
   Baseline 1 bleibt diese ausgeschaltet-gegen-eingeschaltet-Kontrolle SKIP; kein
   künstliches OFF erzwingen. Rückgabecode und redigierte Fehlerausgabe erhalten.
   Im gebundenen Ausgangszustand 0 ist Fehler 343 ein zulässiger beobachteter
   Parsergegenbefund; er erlaubt ausschließlich den bereits festgelegten zweiten
   Aufruf nach Enable. Andere Prozess-/SQL-/Bindungsfehler stoppen die Diagnose.
4. Alle Marker/Baseline erneut prüfen, PREVIEW_FEATURES=ON in einem eigenen
   abgeschlossenen Client setzen. Ein neuer Client muss danach genau die eigene
   DB und genau einen tatsächlichen Previewwert 1 belegen. Fehlender oder anderer
   Wert ergibt FAIL vor dem zweiten Parseraufruf.
5. Dieselbe feste Parserprobe genau einmal mit diesem frischen gebundenen
   DB-Kontext ausführen. Code/Fehlerausgabe und unabhängige tatsächliche Abwesenheit
   von Fixture und Vector Indizes erhalten. Keine Syntaxänderung oder dritte Probe.
6. Tatsächlichen Source-/Baselinebestand sowie vollständige Host-/DB-Optionsbindung
   vergleichen; allein die vorher genehmigte Previewdifferenz vor Restore zulassen.
   Danach eigenen Restore, markergebundenen DB-Abbau, neuen SQL-Abwesenheitsclient
   und gebundenen Containerabbau mit separater Abwesenheitsprüfung durchführen.
7. Befund wahrheitsgemäß als Parserdiagnose mit aktuellen Head-/Main-Gates, PR,
   Integration, Synchronisierung und eigenem Branchcleanup abschließen. Nicht
   geparste oder fehlende Phasen, fehlender Restore und Residuen bleiben sichtbar.

Der feste Parsertext lautet; der Client wird bereits an die vollständig gebundene
eigene DB angeschlossen. Vorher-/Nachherprüfungen laufen außerhalb PARSEONLY:

```sql
SET PARSEONLY ON;
GO
CREATE VECTOR INDEX IDX011_OwnVector ON lab.VectorFixture(V)
WITH(METRIC='cosine',TYPE='DiskANN',MAXDOP=1);
GO
SET PARSEONLY OFF;
GO
```

Das reguläre gemeinsame Lifecyclebudget beträgt höchstens 300 Sekunden, der
gesamte separate Cleanup höchstens 60 Sekunden mit zusammen höchstens 50 Sekunden
Prozessbudgets und zehn Sekunden Reserve. OSError/Timeout/SQL-Fehler erreichen
weiterhin den Container-finally-Pfad; Original- und Recoveryfehler werden getrennt
erhalten. Ein Cleanupfehler maskiert keinen primären Fehler und ergibt keinen PASS.
Secrets bleiben ausschließlich in der Umgebung. Ein Owner, ein enger erforderlicher
Review, ein Diagnosekandidat/ein Container; Modell-/Tokenverbrauch bleibt unbekannt.

## Neue Ressourceninformation und verbleibendes Gate

[SQL Server 2025 known issues, SRC-106](https://learn.microsoft.com/en-us/sql/sql-server/sql-server-2025-known-issues?view=sql-server-ver17#vector-index)
führt den ignorierten MAXDOP-Parameter bei CREATE VECTOR INDEX/VECTOR_SEARCH und
nennt Server- oder DB-Konfiguration als Alternative. Dies ist Herstellerdokumentation,
kein empirischer DOP-Befund am ausgewählten Image. Die gescheiterte DDL hat keinen
erfolgreichen Indexbuild oder tatsächlichen DOP-Nachweis geliefert.

Deshalb umfasst dieser Entscheid ausschließlich Parsing. Die DDL-Zeichenfolge
MAXDOP=1 ist keine Garantie eines späteren Builds mit DOP 1. Ein tatsächlicher
Indexbuild/Suchlauf bleibt zusätzlich an einen wirksamen freigegebenen DOP-1-Pfad
gebunden; insbesondere ein zusätzlicher DB-scoped-MAXDOP-Set/Restore-Effekt ist
jetzt nicht freigegeben. Kein Server-/Host-Workaround wird ausgeführt.

Die drei Primärquellen wurden am 2026-10-11 geprüft. Nach Abschluss oder Fehler
dieser einzelnen Diagnose wird angehalten; der Heartbeat startet keine weitere
Korrektur durch Namenswechsel oder Umdeutung des Befunds. Unabhängige autorisierte
Offlinearbeit bleibt zulässig. Ohne den neuen ausdrücklichen Budgetentscheid
erfolgt keine weitere ANN-Korrektur oder SQL-Runtime.

Der enge unabhängige Review dieses Entscheidungsentwurfs fand keine konkreten
P1/P2. Er prüfte ausschließlich Parser-/Effekt-/Budget-/Claimgrenzen; keine
Korrekturquelle oder Runtime und keine erneute Vollanalyse der bisherigen Helper.
Das Entwurfs-Quellengate ist geschlossen, der Benutzerentscheid bleibt ausstehend.
