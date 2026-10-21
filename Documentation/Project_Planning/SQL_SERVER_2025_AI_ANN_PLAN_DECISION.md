# TSK-006 – begrenzte tatsächliche ANN-Planausgabe

Stand: 2026-10-11. [Einzelne Planausgabe bestanden](SQL_SERVER_2025_AI_ANN_PLAN_REVIEW.md),
eigener Vector Index Seek mit fünf tatsächlichen Rows, Generation UNKNOWN.
Diagnoseumfang nach einem Kandidaten/Container regulär abgeschlossen.
AUTHORIZED_BOUNDED_DIAGNOSIS gemäß ausdrücklicher
Benutzerautorisierung aller weiteren notwendigen lokalen Schritte dieser
Entwicklungswelle. Der [Legacy-Ergebnisnachweis](SQL_SERVER_2025_AI_ANN_LEGACY_TRIAL_REVIEW.md)
belegt Ergebnisse, aber keine Indexnutzung. Historische Budgets und FAILs bleiben erhalten.
Der erforderliche enge Methoden-/Quellenreview des tatsächlichen ersten privaten
Kandidaten fand keine P1/P2; fünf bestehende und sechs neue betroffene lokale Tests
bestanden vor SQL. Suchbefund PR 163 vollständig integriert; Quellengate geschlossen.
Keine Plan-/Runtimeattestation durch den Review.

## Frage und endlicher Umfang

Genau die bewährte feste Legacy-Suchsignatur am bestehenden festen Build wird
einmal je Kandidat mit SET STATISTICS XML (Extensible Markup Language; Format zur strukturierten Darstellung von Daten) ON/OFF ausgeführt. Höchstens zwei neue
Kandidaten und zwei neue eigene Container seriell; je Kandidat ein Lifecycle.
Der zweite Kandidat braucht geänderte Eingaben oder neue Evidenz. Nach zwei
ungelösten Kandidaten Befund integrieren und einen getrennten endlichen Folgescope
aus der erteilten Wellenautorisierung auswählen, kein stilles Budgetreset.

Der private Client prüft vollständiges begrenztes XML, aktuelle Build-/Statementbindung
und tatsächlich vorhandene Laufzeitinformationen. Ein Cache-/Estimated-Plan zählt
nicht als Actual-Plan. Beobachtete Operatoren und Objekt-/Indexbindung werden getrennt
ausgewiesen; allein ein erfolgreicher Search, ein Indexname im Text oder ein geschätzter
Operator beweist keine tatsächliche Indexnutzung. Fehlendes XML/Laufzeit-/Bindingmaterial
ergibt FAIL der Aufnahme. Bei tatsächlichem Plan ohne hinreichende eigene Vector-
Indexbindung bleibt Indexnutzung UNKNOWN bzw. beobachteter Fallback separat sichtbar.
Numeric Generation bleibt UNKNOWN, solange kein neuer belastbarer Nachweis vorliegt.

## Unveränderte lokale Grenzen

Volle Image-ID 78eb6a93ef20501bd754282cc216188a0acee1cfa6119c33eef0b21599c1f726,
SQL 17.0.5005.3/EngineEdition 3/Linux Ubuntu 24.04, vier CPUs/sechs GiB,
vollständige CID-/Image-/Ownerbindung, eigener Loopbackport und voll markierte DB.
CL170/SIMPLE, 256/64-MB-Dateilimits, 1000 synthetische VECTOR(3)-float32-Rows,
cosine/K=5, eine aktive SQL-Session. Nur eigene Preview ON/MAXDOP (Maximum Degree of Parallelism; konfigurierte Grenze für den Parallelitätsgrad) 1 nach persistierter
vollständiger tatsächlicher Baseline 0/1 und MAXDOP 0; getrennte Set-/Attestclients,
QUOTED_IDENTIFIER ON. Keine DML (Data Manipulation Language; Anweisungen zum Lesen oder Ändern von Daten), kein ALLOW_STALE_VECTOR_INDEX, keine Provider-/Cloud-/
ONNX-/Hostwirkung. STATISTICS XML ist eine Option der eigenen Querysession gemäß FWK-005.

Volle aktuelle Indexmetadaten und eindeutiges beobachtetes DiskANN/COSINE-/
Versionsschlüssel-fehlt-Profil vor Search; vollständige Quell-, Marker-, Baseline-,
Index-/Host-/DB-scoped-Konfigurationsbindungen und tatsächliche Ergebnis-/Negativkontrollen
bleiben erhalten. Eigener Indexdrop, beide tatsächlichen Restores, neue Attestierung
vor DB-Drop und separate SQL-/Containerabwesenheit bleiben erforderlich.
Normale Deadline 300 Sekunden, Cleanup 60 Sekunden mit unveränderten 50 Call-Capsekunden
und zehn Reserve. Secrets ausschließlich Umgebung; ausgeführte Kandidaten unverändert.

## Gates und begrenzte Aussage

Vor SQL: Integration des Suchbefunds, betroffene lokale Planparser-/Manipulationsprüfungen
und enger unabhängiger Review des tatsächlichen Plan-/Clientdeltas. Vollständige private
Rohplanaufnahme bleibt unversioniert; nur geprüfte synthetische Zusammenfassung und
Quellen-/Logbindung gehen ins Repository. Kein automatischer Rohplanexport ins Repository.
Aktuelle Head-/Main-Gates, PR, Synchronisierung und eigener Branchcleanup schließen den
begrenzten Befund ab. Keine Performance-, Worker-DOP-, allgemeine Recall- oder volle
IDX-011-/IDX-012-Abnahme durch diese einzelne Planausgabe.
