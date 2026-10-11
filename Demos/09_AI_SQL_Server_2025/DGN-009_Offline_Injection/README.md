# DGN-009 – Manipulierte Quellen und feste Offline-Toolpolicy

Status: IMPLEMENTED; lokaler Review-/Runtime-/Integrationsnachweis offen.
GREEN, eine Session, SQL Server 2025 (17.x), Kompatibilität 170. 2019/2022 liefern
SKIP_VERSION vor Setup. Keine Modellgenerierung, Provider- oder Netzwerkaufrufe.

Drei vollständig eingefrorene synthetische Dokumente haben denselben VECTOR(3):
aktuell/vertrauenswürdig mit 7 Tagen, aktuell/untrusted mit einer Anweisung zur
CONTROL-Rechteänderung und einer 99-Tage-Behauptung sowie eine alte widersprüchliche
9-Tage-Version. Die exakte Cosine-Abfrage liefert tatsächlich Quelle 1 und den
manipulierten Inhalt aus Quelle 2. Dies demonstriert die Weitergabe untrusted Contents;
Trust/Current sind feste vom Labowner gesetzte Policymerkmale.

Die saubere Baseline liest tatsächlich 7 Tage. Vier Inline-Antwortfixtures liefern
1 akzeptierte / 3 abgelehnte Antworten: falsche Behauptung, untrusted Citation und
veraltete Quelle scheitern. Vier Inline-Toolfixtures liefern 1 erlaubten / 3 abgelehnte
Versuche: GrantControl, ReadFact auf untrusted Quelle und ein Toolname mit Leerzeichen
scheitern an voller Byteallowlist und Quellenpolicy. Nur ReadFact auf Quelle 1 wird
mit festem SQL und separatem int-Parameter unter DGN009_reader ausgeführt.

Der privilegierte dbo-Harness kontrolliert Setup und Nachzustand. WITHOUT LOGIN
DGN009_reader hat genau CONNECT und SELECT auf lab.Documents, das separate Toolziel
DGN009_sink nur CONNECT. Feste GRANT CONTROL- und UPDATE-Gegenproben laufen unter dem
Reader und müssen mit 4613/229 scheitern. Die GRANT-Probe betrifft den separaten Sink,
damit ein allgemeines Self-GRANT-Verbot keinen Rechteerfolg vortäuscht. Content und
Modellfixtures werden niemals zu SQL konkateniert. REVERT schützt Erfolgs-/Fehlerpfade;
volle Source-/Vektorbytes und vollständige direkte Benutzerrechte bleiben erhalten.

Ergebnisvertrag: 1 Baselinezeile; 2 retrievte Quellen; 1/3 akzeptierte/abgelehnte
Antworten; 1/3 erlaubte/abgelehnte Tools; 2 tatsächliche Rechteverweigerungen und
1 tatsächliche positive Toolrow. Fehlende positive Rows ergeben FAIL.

Dieser Offlinefall ist kein Live-LLM-, allgemeiner Entailment-, Egress-, Tenant- oder
Prompt-Injection-Sicherheitsnachweis. Quellenvertrauen wird nicht automatisch erkannt;
serverseitige Policy und minimale Rechte begrenzen die deklarierten festen Fälle.
DGN-008-External-Model-/Endpoint-/Credentialabnahme und optionale Livegeneration bleiben
getrennt offen. Modell-/Tokenverbrauch: N/A für diese Fixture.

## Schritt-für-Schritt-Anleitung

Siehe [Ausführungsleitfaden](../../../Documentation/HowTo/DEMO_EXECUTION_GUIDE.md).

1. Freigegebene Testinstanz auswählen und SQLCMDPASSWORD gemäß Leitfaden setzen.
2. Demo manifestbasiert ausführen: `python Demos/00_Framework/Tools/run_demo.py Demos/09_AI_SQL_Server_2025/DGN-009_Offline_Injection/manifest.json` mit den Zielargumenten des Leitfadens.
3. Tatsächliche Quellenidentitäten, Antwort-/Toolflags, Rechtefehler und acht Ergebnisassertions prüfen; FAIL/WARN/SKIP sichtbar lassen.
4. Cleanup bleibt markergebunden. Alle vier vollen Eigentumsmarker müssen bytegenau passen; die unabhängige DB-Abwesenheit prüfen.

Zieldatenbank: SQLPERF_LAB_DGN009_<RunToken>. Dateien sind auf 256/64 MB und 16-MB-Wachstum
begrenzt. Cleanup entfernt ausschließlich die vollständig markierte eigene Datenbank.
Abhängigkeiten: FWK-001–FWK-012; CUR-018/CUR-022, TSK-009 und QRY-018; die lokale minimale
SQL-Rolle deckt einen Offline-Unterfall von DGN-008 ab, keine External-Model-Rechte.

Quellen: SRC-090/SRC-091/SRC-095 im Quellenregister. GRANT benötigt passende Grantor-
Rechte, siehe [Microsoft GRANT](https://learn.microsoft.com/en-us/sql/relational-databases/security/authentication-access/grant-a-permission-to-a-principal?view=sql-server-ver17);
Fehler 4613 bezeichnet fehlendes GRANT-Recht gemäß
[Microsoft Fehlerkatalog](https://learn.microsoft.com/en-us/sql/relational-databases/errors-events/database-engine-events-and-errors-4000-to-4999?view=sql-server-ver17).
