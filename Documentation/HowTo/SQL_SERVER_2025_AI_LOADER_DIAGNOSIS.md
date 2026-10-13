# Eine KI-Clientverbindung schrittweise einordnen

Bevor ein Programm einen Vektor an SQL Server senden kann, muss seine lokale
Runtime die benötigten Bibliotheken finden und laden. Ein Fehler an dieser
Stelle sagt noch nichts über Datenbankrechte, Vektordaten oder die Antwort
des SQL Servers aus. Für Anwender:innen hilft die folgende Reihenfolge:

| Schritt | Konkrete Frage | Geeigneter Nachweis |
|---|---|---|
| Dateibestand | Sind die erwarteten Dateien und Versionen vorhanden? | Vollständige Originaldatei- und SHA-Bindung |
| Runtime und Laden | Läuft der passende Host und findet er die Bibliothek? | Tatsächliche Runtimeversion, Load-Aufruf und dessen Ende |
| Typen und lokale API | Sind die benötigten Typen verfügbar und funktioniert die konkrete API? | Typmetadaten und anschließend getrennte API-Ergebnisprüfung |
| SQL-Transport | Erreicht der Client die eigene Testdatenbank mit den richtigen Parametern? | Tatsächliche Client-/Serverenden, Typ- und Ergebnisnachweis |

Ein Dateiname im Programmordner beantwortet nur die erste Frage teilweise.
Die Depsdatei und der aktive Load-Kontext beeinflussen die Suche. Dokumentiert:
[Default probing](https://learn.microsoft.com/en-us/dotnet/core/dependency-loading/default-probing)
und [Managed assembly loading algorithm](https://learn.microsoft.com/en-us/dotnet/core/dependency-loading/loading-managed),
abgerufen am 2026-10-13. Deshalb bedeutet ein fehlender wörtlicher Deps-Unterpfad
allein noch keinen bewiesenen Ladefehler.

## Den aktuellen Befund lesen

Empirisch im begrenzten Windows-Probehost: SDK-Paketmetadaten 10.0.401,
tatsächlich gemeldete Runtime .NET 10.0.12, erhaltener SqlClient-Paketgraph
6.1.4. Das neue Programm verwendet ausschließlich Reflection und erstellt
keine Connection, keinen Command und keine Credentials.

| Phase | Tatsächliche Beobachtung | Einordnung |
|---|---|---|
| HOST_ENTRY | Main-Einstieg erfasst; Runtime 10.0.12 | Dieser Probehost hat seine Main erreicht |
| LOAD_SQLCLIENT | FileNotFoundException; API-Ende THREW | Laden in diesem Default-Kontext fehlgeschlagen |
| TYPE_CONNECTION / TYPE_VECTOR | Nicht erreicht | Typmetadaten nicht qualifiziert |
| SQL | Keine Verbindung oder Abfrage gestartet | Transport und Datenbankergebnis nicht geprüft |

Der Name der fehlenden Assembly ist UNKNOWN. Die sichere Ausgabe akzeptiert
nur geprüfte einfache Namen und enthält keine freien Fehlermeldungen,
Stacktraces oder Hostpfade. UNKNOWN wird nicht durch einen geratenen Namen
ersetzt. Die frühere FileNotFoundException des anderen SQL-Clients bleibt
ebenfalls unaufgeklärt; die neue Probe reproduziert dessen Ablauf nicht.

## Daraus den nächsten Schritt ableiten

Zuerst den aktuellen Paketgraphen und die Originalbytes sichern. Danach den
konkreten Load-Kontext und sichere Fehlermetadaten mit einer begrenzten Probe
prüfen. Eine Gegenprobe braucht eine benannte Änderung, beispielsweise einen
geänderten eigenen Dateibestand; ein unveränderter Wiederholungsversuch schafft
keinen neuen Befund. Erst nach erfolgreichem Laden und getrennten Typ-/API-
Prüfungen folgt eine eigene, ausdrücklich begrenzte SQL-Transportprüfung.

Die hier dokumentierte Diagnose ist ein Entwicklungscheckpoint, keine
freigegebene ausführbare Demo. Sie verlangt keine Änderungen an Instanz,
Firewall, Zertifikatsspeicher oder globaler .NET-Konfiguration. Native SNI-,
TDS-, SQL-, Provider- und Performancequalifikation bleiben offen. Weitere
Gültigkeitsgrenzen stehen im [VECTOR-Kompatibilitätsguide](SQL_SERVER_2025_AI_VECTOR_COMPATIBILITY.md)
und der erhaltene Dateibefund im [Clientlayoutguide](SQL_SERVER_2025_AI_VECTOR_CLIENT_LAYOUT.md).
