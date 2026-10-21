# TSK-006 – begrenzte ANN-Filter- und Ergebnisdiagnose

Stand: 2026-10-11. [Zwei vollständige Filterlifecycles bestanden](SQL_SERVER_2025_AI_ANN_FILTER_REVIEW.md),
enger Filter mit sichtbarem Qualitätsverlust (null ANN- gegen fünf Exact-Rows).
Ein Kandidat/zwei Container, Umfang regulär abgeschlossen; kein allgemeiner Qualitätsclaim.
AUTHORIZED_BOUNDED_DIAGNOSIS durch die ausdrückliche zusätzliche
Benutzerfreigabe aller weiteren notwendigen lokalen Schritte dieser Entwicklungswelle.
Der [Actual-Planbefund](SQL_SERVER_2025_AI_ANN_PLAN_REVIEW.md) bindet die eigene
Indexnutzung nur an den bisher ungefilterten Suchaufruf. Historische Budgets/FAILs
bleiben erhalten; Generation UNKNOWN.

## Fester Umfang und Ergebnisvertrag vor SQL

Höchstens zwei neue kohärente Kandidaten/vier serielle eigene Container; höchstens
zwei vollständige Lifecycles des stabilen positiven Kandidaten. Jeder Retry braucht
geänderte Eingaben/neue Evidenz; nach zwei ungelösten Kandidaten Befund integrieren
und einen getrennten endlichen Wellenumfang auswählen. Ein Owner, enger erforderlicher
Methoden-/Quellenreview des tatsächlichen Filter-/Oracle-/Clientdeltas vor SQL.

Derselbe deterministische Korpus mit 1000 VECTOR(3)-float32-Rows, bestehender Queryvektor,
cosine/K=5. Drei feste Id-Fenster: 1–1000, 1–100 und 501–510. Je Fenster exaktes Top-5
mit identischer Kandidatenmenge/Metric und Id-Tiebreaker vor Indexbuild sichern.
Nach Build genau ein zusätzlicher fester Legacy-Suchaufruf je Fenster mit äußerem
WHERE-Prädikat. Kein Query-/Index-/Syntaxfallback bei SQLfehler, keine adaptive
Schwellenauswahl aus den danach erhaltenen Ergebnissen.

Alle Exact-Oracles enthalten fünf distanzgeprüfte Quell-IDs. Für die beiden breiten
Fenster vorab mindestens vier gültige Rows und vier Exact-Treffer (Recall@5 >= 0,8)
festlegen; tatsächliche Counts/Recall und IDs dennoch vollständig ausweisen.
Für das disjunkte enge Fenster wird gemäß der dokumentierten Legacy-Postfilterform
und dem bereits beobachteten ungefilterten Top-5-Korpus ein leeres Resultat erwartet,
während das gefilterte Exact-Oracle fünf Rows besitzt: sichtbarer Postfilterbefund
mit ROWS_BELOW_K/Recall 0, keine erfolgreiche Retrievalqualität. Ein anderes
Verhalten ist FAIL dieses festen Diagnoseprofils und wird als neuer Befund erhalten.

Alle tatsächlich zurückgegebenen Rows müssen zum festen Filterfenster und zur
vollständig gebundenen Quelle gehören; Distanzen gegen VECTOR_DISTANCE mit derselben
bereits qualifizierten Toleranz prüfen. Zusätzliche feste Fremd-/Filter-/Distanznegative
vor SQL binden. Vollständige Quellen-/Baseline-/Marker-/Indexmetadaten-/Konfigurations-
Nachkontrollen erhalten. Ein erfolgreicher Filterlauf allein behauptet keine
Indexnutzung dieser gefilterten Queries und keinen Performancevorteil.

## Unveränderte lokale Effekte und Abschluss

Gleiche volle Image-ID 78eb6a93ef20501bd754282cc216188a0acee1cfa6119c33eef0b21599c1f726,
SQL 17.0.5005.3/EngineEdition 3/Linux Ubuntu 24.04, vier CPUs/sechs GiB, eigener
Loopbackport, volle CID-/Image-/Ownerbindung und bytegenaue eigene DB-Marker.
CL170/SIMPLE, 256/64-MB-Dateilimits, eine aktive SQL-Session. Nur eigene Preview
ON/MAXDOP (Maximum Degree of Parallelism; konfigurierte Grenze für den Parallelitätsgrad) 1 nach vollständig persistierten tatsächlichen Baselines; getrennte
Set-/neue Attestclients und QUOTED_IDENTIFIER ON. Keine DML (Data Manipulation Language; Anweisungen zum Lesen oder Ändern von Daten), kein Stale-, Host-,
Cloud-/Provider-/ONNX-Effekt. Eigener Indexdrop, beide tatsächlichen Restores,
neue Attestierung vor DB-Drop und separate SQL-/Containerabwesenheit erforderlich.
Normale Deadline 300 Sekunden; Cleanup 60 Sekunden mit denselben 50 Call-Capsekunden
plus zehn Reserve. Secrets nur Umgebung, ausgeführte Kandidaten unverändert.

Vor SQL zusätzlich Integration des Planbefunds und betroffene lokale Tests;
nach Befund aktuelle Head-/Main-Gates, PR, Synchronisierung und eigener Branchcleanup.
SRC-078 am 2026-10-11 erneut geprüft: ältere Indexformen wenden Prädikate nach
Retrieval an; keine Azure-Iterativfilterannahme. Die beobachtete numerische Generation
bleibt UNKNOWN. Laufzeit-/IO-/CPUvergleich und volle IDX-011-/IDX-012-Abnahme bleiben
eigene Folgearbeit; der begrenzte Diagnose-PASS ersetzt diese Gates nicht.
