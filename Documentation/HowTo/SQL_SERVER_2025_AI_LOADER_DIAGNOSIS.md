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

## Den ersten Checkpoint lesen

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

## Die geänderte Gegenprobe vergleichen

Danach wurde der neue Probehost um sichere Namen und tatsächlich erfasste
Host-Suchinformationen ergänzt. In der flachen C2-Variante scheiterte das Laden
erneut, jetzt mit sicherem Namen Microsoft.Data.SqlClient/PARTIAL_DISPLAY.
Die eigene erwartete flache DLL war vorhanden; ihr erwarteter Pfad stand nicht
in der erfassten TPA-Liste. Das schließt einen anderen gleichnamigen TPA-Eintrag
nicht aus. TPA enthält die vom Host verwendeten Assemblypfade.

Für C3 blieb das Programm bytegleich. Fünf DLLs wurden in einem neuen eigenen
Bestand ausschließlich an ihren wörtlichen runtimeTargets-Unterpfaden abgelegt.
Depsdatei, Runtimeversion und DLL-Bytes blieben gleich. Eine neue Kompilierung
war nicht erforderlich.

| Beobachtung | C2: flacher Bestand | C3: fünf relative Unterpfade |
|---|---|---|
| Anzahl TPA-Einträge | 201 | 201 |
| Erwarteter eigener Clientpfad in TPA | false | true |
| Load-Aufruf | FileNotFoundException/THREW | RETURNED |
| Geladene eigene DLL und SHA | Nicht nachgewiesen | Vollständig gebunden |
| SqlConnection-/SqlVector`1-Typmetadaten | Nicht erreicht | Beide bestätigt |
| SQL-Verbindung/Abfrage | Keine | Keine |

Empirisch funktioniert dieses konkrete relative Layout für den benannten
Probehost. Das ist keine allgemeine Deploymentempfehlung: andere Publishes,
Runtime- und Paketgraphen können andere Suchinformationen erzeugen. Der
erfolgreiche Typnachweis führt noch keine SqlVector-Konstruktion oder
SQL-Parameterübertragung aus. Native SNI, TDS und SQL bleiben ungeprüft.
Die verlorenen Fehlermetadaten des ursprünglichen C6-Clients werden nicht
nachträglich als bestätigt dargestellt.

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
