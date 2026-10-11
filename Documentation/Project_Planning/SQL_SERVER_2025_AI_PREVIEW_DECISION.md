# TSK-006 – konkretes Freigabepaket für den lokalen ANN-Preview-Slice

Stand: 2026-10-11. AUTHORIZED: Der Benutzer hat im Orchestrator-Chat ausdrücklich
„Ja, lokalen ANN-Slice freigeben“ für dieses unveränderte Paket bestätigt.
Die Freigabe umfasst ausschließlich die nachfolgend gebundenen Effekte und Limits;
sie attestiert keine Index-/Recall-/DML-Runtime. Unabhängige Offlinearbeit bleibt zulässig.

## Ausgewählter Effekt und harte Grenzen

Vorgeschlagen wird die begrenzte lokale Qualifikation von IDX-011/IDX-012 auf einer
neuen eigenen wegwerfbaren SQL-17.x-Containerinstanz. Ausgewählter bereits lokal
vorhandener Microsoft-Tag: 2025-CU9-ubuntu-24.04, tatsächlich gemessener Build
17.0.5005.3 und lokale Image-ID
`78eb6a93ef20501bd754282cc216188a0acee1cfa6119c33eef0b21599c1f726` auf Podman.
Die Ausführung bindet diese vollständige ID erneut; ein Tagwechsel benötigt neue
Buildqualifikation. Docker ist nur nach eigener identischer Build-/Imagequalifikation
zulässig. Vorhandene SQL-Instanzen oder Podman-Maschinen werden nicht verändert.

Pro Demo: eine Session, höchstens 1000 rein synthetische Rows, VECTOR(3) oder VECTOR(32),
4 CPU/6 GB Containerlimit, MAXDOP 1, Daten-/Loglimits zusammen höchstens 512 MiB.
Pro Lifecycle höchstens 300 Sekunden plus 60 Sekunden eigener Cleanup; je zwei
zusammengehörige Lifecycles und erforderliche Marker-/Resultgegenfixtures. Ein Owner,
ein erforderlicher enger unabhängiger Review und maximal zwei kohärente Korrekturwellen
je zusammenhängendem Implementierungsschnitt. Unbekannter Modell-/Tokenverbrauch
bleibt unbekannt; keine Modellaufrufe, externen Payloads oder Kosten-APIs.

Die einzige zusätzlich freigegebene Konfigurationsänderung lautet in der neuen
eigenen Testdatenbank:

```sql
ALTER DATABASE SCOPED CONFIGURATION SET PREVIEW_FEATURES = ON;
```

Die gespeicherte Ausgangseinstellung wird gebunden und vor DB-Abbau restauriert.
Kein sp_configure, Server-/Host-/TLS-/Credential-/ONNX-Effekt. Setup und Cleanup
prüfen vor jeder Bestandsänderung alle vier vollständigen Eigentumsmarker bytegenau:
Project SQL_PerformanceSchulung, ContractVersion 1.0, zutreffende DemoId IDX-011/IDX-012
und eigener RunToken. Nur SQLPERF_LAB_IDX011_<RunToken> beziehungsweise
SQLPERF_LAB_IDX012_<RunToken> darf verwendet und abgebaut werden. Vorhandene fremde
oder nicht exakt markierte Bestände ergeben FAIL ohne Änderung.

## Freigegebener fachlicher Schnitt

IDX-011 legt ausschließlich einen eigenen DiskANN-Index auf der synthetischen
Labtabelle an, bindet die tatsächliche Indexgeneration aus sys.vector_indexes und
vergleicht ausgewählte ANN-Ergebnisse gegen eine tatsächlich ausgeführte Exact-kNN-
Oracle. Recall, zurückgegebene Rowzahl, Ranking und Ressourcen bleiben Messwerte;
ein fehlender erwarteter Top-k-Bestand oder unbekannte Generation ergibt keinen PASS.
Keine Performanceverbesserung wird vor Messung zugesagt.

Die zu qualifizierende DDL ist:

```sql
CREATE VECTOR INDEX IDX011_OwnVector
ON lab.VectorFixture (V)
WITH (METRIC='cosine', TYPE='DiskANN', MAXDOP=1);
```

IDX-012 prüft anschließend nur die für die tatsächlich beobachtete Generation
gültigen DML-/Stale-/Drop-/Rebuild-Grenzen mit eigener Fixture. Neue Indexgeneration
und Cloud-Dokumentation werden nicht pauschal auf SQL Server 2025 übertragen;
unbekannte Syntax/Featuregrenzen bleiben sichtbar. ALLOW_STALE_VECTOR_INDEX wird
nicht durch diese Freigabe eingeschlossen: ein erforderlicher weiterer Effekt
benötigt zunächst ein eigenes konkret abgegrenztes Paket.

Vor-/Nachkontrollen binden vollständige Source-/Vektorbytes, Indexidentität und
DB-/Hostoptionen; tatsächliche positive Rows und Negative sind erforderlich. Abbruch
an Phasengrenzen und unabhängige eigene DB-/Containerabwesenheit gehören zum Abschluss.
Kein vollständiger Performance-, ANN-Tenant-/RLS-, Seitenkanal- oder Providerclaim
aus diesem kleinen synthetischen Profil. Ohne Freigabe bleibt PREVIEW_FEATURES unverändert.

## Grundlage und Grenze der konkreten Entscheidung

Der [kanonische Workstreamplan §12](SQL_SERVER_2025_AI_WORKSTREAM_PLAN.md#12-priorisierte-arbeitspakete-und-abhängigkeiten)
führt TSK-006 mit der Abhängigkeit „Previewentscheid“. Der
[gemeinsame Demo-Vertrag](../Demo_Catalog/SQL_SERVER_2025_AI_DEMO_DESIGNS.md#gemeinsamer-vertrag-aller-folgenden-entwürfe)
verlangt im Previewprofil „vorher genehmigtes PREVIEW_FEATURES in eigener DB“.
Die allgemeine autonome Entwicklungsfreigabe ersetzt diesen noch offenen konkreten
Previewumfang nicht. Der konkrete Benutzerentscheid ist jetzt erfolgt;
Cloud-/Bezahl-, ONNX- und rote Hostfreigaben bleiben getrennt.

Die am 2026-10-11 geprüften Primärquellen
[CREATE VECTOR INDEX](https://learn.microsoft.com/en-us/sql/t-sql/statements/create-vector-index-transact-sql?view=sql-server-ver17)
und [VECTOR_SEARCH](https://learn.microsoft.com/en-us/sql/t-sql/functions/vector-search-transact-sql?view=sql-server-ver17)
führen SQL Server 2025 weiter als Preview und unterscheiden Indexgenerationen.
Sie ersetzen die noch nicht ausgeführte tatsächliche Build-/Index-/Ergebnisqualifikation nicht.
