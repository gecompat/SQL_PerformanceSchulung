# TSK-006 – begrenzter Legacy-Signaturversuch bei unbekannter Generation

Stand: 2026-10-11. AUTHORIZED_BOUNDED_DIAGNOSIS durch die ausdrückliche zusätzliche
Benutzerfreigabe „auch alle weiteren Freigaben zur Durchführung dieser Entwicklungswelle“.
Dies ist ein neuer Diagnoseumfang nach Integration der
[einzelnen Metadatenaufnahme](SQL_SERVER_2025_AI_ANN_METADATA_REVIEW.md).
Historische Generationsstopps/FAILs und Budgets bleiben erhalten.

Der enge unabhängige Methoden-/tatsächliche Quellenreview fand keine konkreten
P1/P2 im neuen privaten Kandidaten. Fünf betroffene lokale Tests bestanden;
das Quellengate ist geschlossen. SQL-Start bleibt bis zur abgeschlossenen
Integration der Metadatendiagnose ausgeschlossen. Dies attestiert keinen Runtime-PASS.

## Fachliche Frage und unveränderte Unsicherheit

Die tatsächlichen Buildparameter am eigenen 17.0.5005.3-Index besitzen keinen
Version-Schlüssel. Die numerische Generation bleibt UNKNOWN. SRC-077 zeigt ein
Version-Migrationsbeispiel; SRC-097 bezeichnet die Buildparameter als intern.
SRC-078 dokumentiert die Legacy-VECTOR_SEARCH-Signatur mit TOP_N für frühere
Indexformate und führt SQL Server 2025 im Geltungsbereich. Diese Quellen belegen
keine aktuelle numerische Generation und keine tatsächliche Indexnutzung.

Die neue private Diagnose fragt deshalb ausschließlich: Liefert die konkret
festgelegte dokumentierte Legacy-Signatur an diesem festen Build mit tatsächlich
erstelltem eigenem Index fünf gültige, distanzgeprüfte Quellrows? Ein positives
Ergebnis ist SEARCH_RESULT_PASS_AT_FIXED_BUILD, GENERATION_UNKNOWN und
INDEX_USAGE_UNPROVEN. Es ist keine generationsqualifizierte Demoabnahme.
Kein Rückgriff auf die aktuelle Azure-WITH-APPROXIMATE-Signatur und kein automatischer
Syntaxfallback. Ein unerwarteter Metadatenwert/SQLfehler beendet den Kandidaten.

## Endlicher Umfang und Effektgrenzen

Höchstens zwei neue kohärente Kandidaten und vier neue eigene Container seriell;
je stabilem positiven Kandidaten höchstens zwei vollständige Lifecycles. Nach zwei
ungelösten Kandidaten aktuellen Befund integrieren und einen neuen endlichen
Scope aus der erteilten Wellenautorisierung auswählen; kein stilles Budgetreset.
Jeder Retry benötigt geänderte Eingaben oder neue Evidenz. Ein Owner und enger
unabhängiger Review des tatsächlichen Metadaten-/Suchdeltas vor SQL.

Dieselbe volle Image-ID
`78eb6a93ef20501bd754282cc216188a0acee1cfa6119c33eef0b21599c1f726`, SQL
17.0.5005.3/EngineEdition 3/Linux Ubuntu 24.04, vier CPUs/sechs GiB, eigener
Loopbackport, volle CID-/Image-/Ownerbindung, eigene voll markierte DB,
CL170/SIMPLE und 256/64-MB-Dateilimits. Höchstens 1000 VECTOR(3)-float32-Rows,
cosine, K=5, eine aktive SQL-Session, keine Provider-/Modellcalls.

Nur eigene PREVIEW_FEATURES=ON/MAXDOP=1 nach vollständiger tatsächlicher persistenter
Baseline 0/1 und MAXDOP 0. Getrennte Setclients und frische Attestierung beider Werte,
QUOTED_IDENTIFIER ON in eigener Buildsession. Kein Host-/Cloud-/TLS-/ONNX- oder
ALLOW_STALE_VECTOR_INDEX-Effekt. Beide tatsächlichen Restores und neue Attestierung
vor DB-Drop bleiben unverändert erforderlich.

## Feste Diagnosefolge

1. Beide Baselines/Marker/Build-/Ressourcenprofil binden; 1000 feste Quellrows und
   vollständige unterstützte JSON-Bytes/numerische Werte sichern. Exakte fünf
   Vergleichsrows mit cosine-Distanz und deterministischem Id-Tiebreaker vor Build.
2. Eigenen Index erstellen und **zuerst** die volle aktuelle Indexrow aufnehmen.
   Genau ein eigener Index, Typ VECTOR/DiskANN, tatsächliche Metric COSINE,
   nicht disabled/hypothetical. Gültige Buildparameter ohne Version-Feld bestätigen.
   Ein vorhandenes, NULL-enthaltendes oder anderes Version-Feld/unerwartetes Profil
   stoppt diesen festen Diagnoseumfang vor Search. Keine neue Generation ableiten.
3. Nach vollständiger Source-/Baseline-/Marker-/Konfigurationsbindung genau die
   feste Legacy-Signatur VECTOR_SEARCH mit TABLE/COLUMN/SIMILAR_TO/METRIC und TOP_N=5
   ausführen. Keine zweite alternative Syntax bei Fehler. Fünf eindeutige tatsächliche
   Quell-IDs, exakte Distanzkontrolle und tatsächliche Schnittmenge mit Exactoracle
   erfassen. Fehlende/fremde/geänderte Resultatfixtures ablehnen; kein Recallversprechen.
4. Alle vollständigen Quell-/Baseline-/Marker-/Index-/Konfigurationsbindungen
   vor/nach Search vergleichen, eigenen Index entfernen und Abwesenheit bestätigen.
   Keine DML-/Stale-/Plan-/Performanceprobe; IDX-012 bleibt eigener Folgeumfang.
5. Beide gespeicherten Originalwerte tatsächlich wiederherstellen, neuer Client
   attestiert vor eigener DB-Entfernung, separater SQL-Abwesenheitsclient und voll
   gebundener Containerabbau mit separater Abwesenheit.

Gemeinsame normale Deadline 300 Sekunden, getrennt Cleanup absolute 60 Sekunden:
Caps 6/6/4/4/6/16/8 ergeben 50 plus zehn Reserve, monotone gemeinsame Begrenzung,
finally auch bei OSError/Timeout/SQL-/Restorefehler. Secrets ausschließlich Umgebung.
Betroffene lokale Tests, aktuelle Head-/Main-Gates, PR, Integration, Synchronisierung
und eigener Cleanup schließen den tatsächlich begrenzten Befund ab. UNKNOWN bleibt
UNKNOWN; ein positiver Querybefund ersetzt keine numerische Generationsqualifikation.
