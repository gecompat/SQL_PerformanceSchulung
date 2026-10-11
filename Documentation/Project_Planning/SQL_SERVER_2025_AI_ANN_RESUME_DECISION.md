# TSK-006 – begrenzter Wiederaufnahmeentscheid nach dem ANN-FAIL

Stand: 2026-10-11. PENDING_USER_DECISION. Dieses Paket wird vorbereitet;
es autorisiert keine dritte Korrektur oder weitere SQL-Ausführung.
Die ursprüngliche [Effektfreigabe](SQL_SERVER_2025_AI_PREVIEW_DECISION.md)
bleibt gültig und unverändert. Der [Fehlercheckpoint](SQL_SERVER_2025_AI_ANN_PREVIEW_REVIEW.md)
bleibt FAIL; die bekannten eigenen Container sind abwesend.

## Empfehlung und Entscheidung

Empfohlen wird eine ausdrücklich neu begrenzte Wiederaufnahme der privaten
IDX-011-Vorbereitung mit höchstens zwei zusätzlichen kohärenten Korrekturkandidaten.
Jeder Kandidat bündelt die unten genannten Änderungen vor Prüfung; keine
unveränderten Wiederholungen. Höchstens vier neue eigene Container seriell,
je höchstens zwei vollständige Lifecycles eines stabilen Kandidaten. Nach dem
zweiten ungelösten Kandidaten bleibt der Schnitt mit Evidenz und Cleanup angehalten.
Ein Owner und ein enger unabhängiger Review der neuen Recovery-/Bindungsgrenzen;
keine Reviewkette oder automatische Rücksetzung durch den Heartbeat.
Modell-/Tokenverbrauch bleibt unbekannt.

Der Entscheid betrifft ausschließlich dieses zusätzliche Korrekturbudget.
Build 17.0.5005.3, vollständige lokale Image-ID, maximal 1000 synthetische Rows,
VECTOR(3), MAXDOP 1, vier CPUs/sechs GiB, Daten-/Loglimits und allein das
PREVIEW_FEATURES in der eigenen markierten Datenbank bleiben wie freigegeben.
Keine Cloud-, ONNX-, TLS-, Credential-, Host- oder ALLOW_STALE_VECTOR_INDEX-Erweiterung.
IDX-012 und die vollständigen FWK-/TP-PERF-Demopakete folgen erst nach einem
tragfähigen IDX-011-Beleg und ihren eigenen unveränderten Abnahmegrenzen.

## Konkreter Änderungskandidat vor neuer Runtime

| Offener Befund | Vorgesehene Änderung | Erforderliche Kontrolle |
|---|---|---|
| Fehler 529: direkte VECTOR→varbinary-Konvertierung | Die vollständige vom Typ unterstützte JSON-Zeichenrepräsentation des gespeicherten Vektors verwenden und deren Unicode-Bytes vergleichen. Keine Behauptung über interne VECTOR-Speicherbytes. | Vollständige Id-/Vektorbindung vor/nach Indexnutzung in beiden Richtungen; fehlende, zusätzliche und geänderte Rows ablehnen. Die Konversion am ausgewählten Build tatsächlich prüfen. |
| Unbekannter SQL-Recoveryfehler | Getrennte redigierte stdout-/stderr-Diagnostik, tatsächlichen Fehlercode und betroffene Phase erhalten. | Originalfehler und Recoveryfehler getrennt sichtbar; leere Ausgabe ist kein Recovery-PASS. Secrets verbleiben ausschließlich in der Umgebung. |
| Recovery-OSError könnte Containercleanup überspringen | SQL-Recovery in einen getrennten try/finally-Pfad stellen; erwartete Prozess-/Startfehler führen stets zur anschließenden ownergebundenen Containerbehandlung. | Lokale isolierte OSError-/Timeout-/SQL-Fehlerfixtures; keine Quelle verändert fremde oder nicht gebundene Container. Ein Cleanupfehler maskiert nicht den ursprünglichen Fehler. |
| 20 + 50 Sekunden überschreiten die freigegebenen 60 Sekunden | Gemeinsame monotone Cleanupdeadline für SQL-Recovery, Ownerprüfung, Remove und Abwesenheit; jeder Prozess erhält nur sein verbleibendes Teilbudget. Kein separater zusätzlicher SQL-Recoveryblock. | Calls zusammen auf höchstens 50 Sekunden begrenzen, zehn Sekunden für Start-/Fehler-/Nachbehandlung reservieren; die gemeinsame 60-Sekunden-Deadline bleibt absolut. Echte Laufzeit erfassen, Überschreitung bleibt FAIL. Keine unbeschränkte Prozesswartezeit oder Erfolgsausgabe nach Timeout. |
| Preview-Ausgangszustand/Restore nicht attestiert | Genau eine persistent gebundene Ausgangseinstellung 0/1 vor Enable erfassen; fehlende, NULL-, doppelte oder ungültige Baseline ablehnen. | Vollständige Eigentumsmarker vor Effekten; tatsächlicher Restoregleichstand vor DB-Abbau und anschließend separate DB-Abwesenheitsabfrage. Containerabwesenheit ersetzt diesen SQL-Beleg nicht. |

Die JSON-Darstellung ist durch SRC-072 dokumentiert:
[VECTOR](https://learn.microsoft.com/en-us/sql/t-sql/data-types/vector-data-type?view=sql-server-ver17),
geprüft am 2026-10-11. Der Typ kann als JSON-Zeichenfolge dargestellt werden.
Diese Dokumentation belegt weder die noch ausstehende lokale Konversion noch eine
identische interne Speicherform. Erwartete numerische Werte, Dimension/float32 und
die vollständige Darstellung sind gemeinsam zu kontrollieren; kein Count- oder
Digestersatz für die vollständige Bindung.

## Reihenfolge und Abnahmegrenze

1. Nach ausdrücklichem Entscheid beide bekannten P2 sowie Konversion und
   Diagnosepfad in einem stabilen privaten Kandidaten korrigieren.
2. Begrenzte lokale Recovery-/Deadline-/Baselinegegenfixtures und den engen
   Quellenreview durchführen. Keine SQL-Probe, solange diese Gates offen sind.
3. Frische eigene Instanz und Image-/Owner-/Loopbackbindung prüfen. Genau den
   ausgewählten Build verwenden; keine bestehende Instanz übernehmen.
4. Zwei vollständige Lifecycles des stabilen Kandidaten qualifizieren:
   Previewbindung, Indexgeneration vor Search, tatsächliche Exact-/ANN-Rows und
   Distanzkontrollen, gemessene Recalltreffer, vollständige Vor-/Nachbindung,
   Restore, vier bytegenaue Marker sowie unabhängige DB-/Containerabwesenheit.
5. Bei Fehler nur mit geänderten Eingaben und innerhalb des neu bestätigten
   Budgets fortsetzen. Gegebenenfalls eigener Fehlcheckpoint statt Ergebnisclaim.
6. Den tatsächlich erreichten begrenzten Beleg mit aktuellen Head-/Main-Gates,
   PR, Integration, Synchronisierung und eigenem Branchabbau abschließen.

Ein erfolgreicher privater Kandidat ist keine vollständige IDX-011-/IDX-012-Abnahme,
kein Plan-/Performanceclaim und keine allgemeine Recallgarantie. Ein fehlerhafter
Restore oder fehlende eigene DB-Abwesenheit bleibt FAIL, auch bei entferntem Container.
Der Gesamtworkstream und der Heartbeat bleiben offen, bis die kanonischen Tasks
regulär abgeschlossen sind.

## Warum der zusätzliche Entscheid benötigt wird

Die ursprüngliche Effektfreigabe begrenzt jeden zusammenhängenden Schnitt auf
„maximal zwei kohärente Korrekturwellen“. Der Fehlercheckpoint stellt ausdrücklich
fest: „Keine weitere Änderung oder Runtime darf durch stilles Zurücksetzen dieses
Korrekturbudgets erfolgen.“ Beide Wellen sind verbraucht. Deshalb ersetzt weder die
allgemeine autonome Entwicklung noch ein neuer Heartbeat diesen Budgetentscheid.
Bis zur Antwort bleiben die privaten ANN-Quellen unverändert; unabhängige autorisierte
Arbeit wird fortgesetzt. Eine Ablehnung belässt ANN angehalten und nimmt die bereits
genehmigten lokalen Effekte nicht als ausgeführt oder erfolgreich an.
