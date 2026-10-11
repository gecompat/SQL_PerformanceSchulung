# DGN-008 – External-Model-Metadaten und getrennte Offline-Rechte

Status: IMPLEMENTED; lokaler Runtime-/Review-/Integrationsgate offen.
GREEN, eine Session, SQL Server 2025 (17.x), Kompatibilität 170. 2019/2022 liefern
SKIP_VERSION vor Setup. Kein Modell-/REST-Aufruf, keine echten Credentials.

Der dbo-Labowner besitzt den Kontrollharness. Drei eigene Datenbankrollen und drei
WITHOUT LOGIN Benutzer trennen Setup, Ingestion und Retrieval. Die Setupidentität
erstellt tatsächlich ein EXTERNAL MODEL, bleibt dessen Owner und erhält ausschließlich
CREATE EXTERNAL MODEL über ihre Rolle. Der reservierte feste HTTPS-Endpoint und der
synthetische Modellname sind Metadaten. SYNTHETIC_NO_SECRET ist nur eine Tabellenattrappe;
es gibt kein DATABASE SCOPED CREDENTIAL und keinen Secretwert.

Der Reader liest tatsächlich die synthetische Quellrow mit FactDays 7. Ingestion führt
zwei fest parametrisierte Updates 7→8→7 mit tatsächlich erfassten OUTPUT-Rows aus.
Beide Rollen haben initial EXECUTE am Modell; HAS_PERMS_BY_NAME prüft dieses Recht
ausschließlich als Metadatenrecht. Die Demo ruft keine Embeddingfunktion auf.
Initial darf Retrieval die synthetische Endpoint-/Aliaspolicy lesen. Mitigation nimmt
diesen SELECT- und den Modell-EXECUTE-Grant zurück; der erlaubte Quell-SELECT bleibt
tatsächlich funktionsfähig, Ingestion behält ihre beiden Writes und ihr Metadatenrecht.

Feste Gegenproben laufen tatsächlich unter den eingeschränkten Identitäten: Reader-
und Ingestion-CREATE EXTERNAL MODEL scheitern jeweils mit 262, Reader-UPDATE und
Ingestion-Policy-SELECT mit 229, nach Grantreduktion auch Reader-Policy-SELECT mit 229.
REVERT schützt Erfolg und Fehler. Vier vollständig eingefrorene Endpointstrings liefern
1 erlaubte und 3 abgelehnte Fälle (HTTP, fremdes HTTPS-Ziel, nachgestelltes Leerzeichen).
Dies ist eine Bytepolicy ohne echten Abfluss, kein DNS-/Firewall-/Egressnachweis.

Vor-/Nachkontrollen binden volle Modellmetadaten einschließlich IDs und Zeitstempeln,
kanonische Modellwerte, Quellen-/Endpointbytes, direkte User-/Rollenrechte, genau drei
Rollenmitgliedschaften und unveränderte Hostoptionen. Die neun Ergebnisassertions
prüfen positive Rows/Writes, fünf tatsächliche Verweigerungen und Policy-/Metadatenwerte.
Fehlende positive Bestände ergeben FAIL. Der dbo-Harness ist nicht an Queryrollen
freigegeben; er validiert keinen authentifizierten Anwendungsservice oder Verbindungspool.

Inferenz, echte Endpoint-/Credentialnutzung, allgemeiner Datenabflussschutz und
Providerabnahme bleiben UNQUALIFIED. Modell-/Tokenverbrauch: N/A für die Offlinefixture.
Live-Lab-RAG, Cloud-/Bezahl- und ONNX-Pfade behalten ihre separaten Gates.

## Schritt-für-Schritt-Anleitung

Siehe [Ausführungsleitfaden](../../../Documentation/HowTo/DEMO_EXECUTION_GUIDE.md).

1. Freigegebene Testinstanz auswählen und SQLCMDPASSWORD gemäß Leitfaden setzen.
2. Demo manifestbasiert mit `python Demos/00_Framework/Tools/run_demo.py Demos/09_AI_SQL_Server_2025/DGN-008_Offline_Model_Rights/manifest.json` und den Zielargumenten des Leitfadens ausführen.
3. Setupowner, tatsächlich erlaubte Rows/Writes, Rechtefehler und neun Assertions prüfen; FAIL/WARN/SKIP sichtbar lassen. EXECUTE-Metadaten nicht als Modellaufruf werten.
4. Cleanup bleibt markergebunden an alle vier vollständigen bytegenauen Eigentumsmarker; die unabhängige DB-Abwesenheit prüfen.

Zieldatenbank: SQLPERF_LAB_DGN008_<RunToken>. Dateien sind auf 256/64 MB und 16-MB-Wachstum
begrenzt. Cleanup entfernt ausschließlich die eigene vollständig markierte Datenbank
einschließlich ihrer Rollen und Modellobjekte; Hostoptionen werden nicht verändert.
Abhängigkeiten: FWK-001–FWK-012, CUR-016/CUR-018/CUR-022, TSK-005/TSK-009; Live zusätzlich
TSK-007. Quellen: SRC-080/SRC-082/SRC-091/SRC-096.
[CREATE EXTERNAL MODEL](https://learn.microsoft.com/en-us/sql/t-sql/statements/create-external-model-transact-sql?view=sql-server-ver17)
und [sys.external_models](https://learn.microsoft.com/en-us/sql/relational-databases/system-catalog-views/sys-external-models-transact-sql?view=sql-server-ver17)
beschreiben die Rechte- und Metadatenverträge; lokale Belege werden getrennt geführt.
