# IDX-011/IDX-012 – Eng gebundenes ANN-Profil ohne numerische Generation

Stand: 2026-10-11. DEC-074 aus der ausdrücklich erteilten
weiteren lokalen Wellenfreigabe. Keine neue SQL-/Provider-/Hostwirkung. Frühere
Generationguard-FAILs und Diagnosebudgets bleiben unverändert; keine rückwirkende
Demoabnahme aus privaten Diagnose-PASSs.

## Fachliche Entscheidung

Die beiden Demoentwürfe dürfen für ausschließlich SQL Server 17.0.5005.3 unter
dem bereits getesteten Linux-/Developer-/CL-170-Profil einen zweiten, expliziten
Qualifikationspfad verwenden: vollständige empirische Build-/Index-/Syntax- und
Verhaltensbindung bei Generation UNKNOWN/WARN. Dies ersetzt in diesem engen
Pfad die Voraussetzung einer bekannten numerischen Indexgeneration, keine der
Eigentums-, Versions-, Qualitäts-, Plan-, Mess-, Ressourcen- oder Recoveryregeln.
Andere Builds/Plattformen bekommen daraus keine Qualifikation.

Der Originalpfad für tatsächlich belegte numerische Generationen bleibt getrennt.
Fehlende Werte werden weder zu 1/2/3 ergänzt noch aus erfolgreichem TOP_N, DML-
Verweigerung, Herstellerbeispielen oder Builddatum hergeleitet. Das neue Profil
heißt gebundenes Legacy-TOP_N-Profil, keine numerische Generation oder GA-Garantie.

## Verpflichtende Grenzen des neuen Pfads

- Read-only Versions-/Build-/Edition-/OS-/CL-Prüfung vor Setup. SQL 2019/2022
  bleiben SKIP_VERSION; andere unqualifizierte 17.x-Profile melden den vorhandenen
  FWK-012-Code SKIP_CONFIGURATION mit Detail PROFILE_UNQUALIFIED. Kein neuer Statuscode.
  Kein Syntaxfallback, kein Herunterstufen eines Runtimefehlers zu SKIP.
- Nur eigene synthetische markierte Datenbank, 1000 nichtdegenerierte float32-
  VECTOR(3)-Rows, clustered INT-PK (Primary Key; Primärschlüssel), cosine und K=5. Derselbe Korpus/Queryvektor,
  Metric und vorab fixierte Tie- und Kandidatenregeln für Exact/ANN (Approximate Nearest Neighbor; näherungsweise Suche nach ähnlichen Vektoren).
- Vollständige gebundene sys.vector_indexes-Row: eigener DB-/Schema-/Tabellen-/
  Indexbezug, type VECTOR, DiskANN/COSINE, aktiv/nicht hypothetisch; korrekte
  Texttypen und vollständige Unicodebytevergleiche. build_parameters tatsächlich
  JSON-Objekt und Versionskey in allen Casevarianten abwesend. Vollständige rohe
  Metadaten vor/nach Ergebnisphasen vergleichen. Abweichung FAIL, kein Fallback.
- Genau die empirisch belegte öffentliche TOP_N-Signatur. Keine WITH APPROXIMATE-
  oder Azure-Iterativfilterannahme. Vollständige gültige Rows und Distanzkontrolle;
  Qualitätsschwellen vor SQL festlegen. Selektiver Postfilterverlust bleibt
  ROWS_BELOW_K/Recall 0, kein versteckter PASS für Retrievalqualität.
- Tatsächliche Planausgabe an das konkrete Statement binden; Indexverwendung nur
  bei vollständigem eigenen Objektbezug und positiven tatsächlichen Rows am
  zugehörigen Operator. Ohne solchen Beleg INDEX_USAGE_UNPROVEN, keine angenommene
  Nutzung aus Katalogexistenz oder erfolgreichem Suchaufruf. Ein Plan belegt nur
  seine konkrete Query, keine Indexnutzung aller gemessenen oder gefilterten Queries.
- Generation UNKNOWN/WARN in Preflight, Ergebnis und Dokumentation bleibt immer
  sichtbar. Leistungswerte einschließlich Null/Quantisierung und Kostenbereiche
  wahrheitsgemäß; kein fester Speedup. TP-PERF und der kanonische Benchmarkvertrag
  bleiben Pflicht. Die kleine private Messdiagnose ersetzt ihn nicht.
- IDX-012 benötigt weiterhin den vollständigen eigenen Build-/Storage-/DML-/
  Freshness-/Drop-Recreate-/Abbruchvertrag. Der einzelne zurückgerollte UPDATE mit
  42231/State 1 ersetzt weder INSERT/DELETE/MERGE-Proben noch Freshness-/Buildkosten.
  ALLOW_STALE_VECTOR_INDEX war tatsächlich ABSENT; kein OFF-Wert wird erfunden.
- PREVIEW_FEATURES und MAXDOP (Maximum Degree of Parallelism; konfigurierte Grenze für den Parallelitätsgrad) nur in eigener DB mit tatsächlichen persistierten
  Baselines, konkreten begrenzten Effekten und tatsächlichem Restore. MAXDOP=1-
  Konfiguration ist kein tatsächlicher Such-DOP-Beweis. Unveränderte Ressourcen,
  vollständige Eigentumsmarker und unabhängiger DB-/Containercleanup bleiben Pflicht.

## Evidenz und Abnahme

[Metadaten](SQL_SERVER_2025_AI_ANN_METADATA_REVIEW.md),
[Legacy-Signatur](SQL_SERVER_2025_AI_ANN_LEGACY_TRIAL_REVIEW.md),
[tatsächlicher Plan](SQL_SERVER_2025_AI_ANN_PLAN_REVIEW.md),
[Filterverlust](SQL_SERVER_2025_AI_ANN_FILTER_REVIEW.md),
[Messgrenzen](SQL_SERVER_2025_AI_ANN_MEASUREMENT_REVIEW.md) und
[einzelne UPDATE-Verweigerung](SQL_SERVER_2025_AI_ANN_DML_REVIEW.md) liefern die
engen empirischen Grundlagen. SRC-077/078/097/106/108/110/111 tragen ihre jeweils
begrenzten Herstellerverträge. Die widersprüchlichen früheren Kandidaten bleiben
FAIL; neue Verträge ändern ihre damalige Auswertung nicht.

Der erforderliche unabhängige fachliche Methodenreview dieses konkreten Entwurfs
schloss ohne offene P1/P2; keine Korrektur notwendig. Die Entscheidung wird im
selben Schnitt registriert und scopebezogen auf beide Demoentwürfe und den
Workstreamplan angewendet; vor Integration bleibt die Registrierung vorläufig.
Die vollständige öffentliche Demoimplementierung und Runtimeabnahme bleiben eigene
Schritte. Keine globale Frameworklockerung oder Cloud-/ONNX-Freigabe.

Verarbeitungsaufwand: ein Owner/ein notwendiger fachlicher Reviewer, keine neue
Runtime oder erneute unveränderte Diagnoseläufe. Registryvalidierung und betroffene
Projektsemantik plus aktuelle Head-/Main-/Privacygates; keine Review-of-Review-Kette.
Die tatsächliche CI-Auswahl und deren Abschluss werden bei Integration belegt.
Modell-/Tokenverbrauch bleibt unbekannt.
