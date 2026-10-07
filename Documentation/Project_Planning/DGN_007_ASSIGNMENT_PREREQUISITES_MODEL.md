# DGN-007 – Deklaratives Voraussetzungenmodell

| Merkmal | Wert |
|---|---|
| Stand | 2026-10-07 |
| Status | `IMPLEMENTED` – reines Modell mit lokaler synthetischer Prüfung |
| geprüfte Repositorybasis | `abeabbf2c97d3ea49c0b1f065ff764c957a0ae92` nach PR70 |
| Grundlage | [Mess-/Zuordnungsgegenentwurf](DGN_007_CAPTURE_ASSIGNMENT_DESIGN.md), Abschnitt 6 |
| Geltungsbereich | `PROJECT_SEMANTIC`, synthetische Eingaben |
| Abnahmegrenze | Keine Methodenentscheidung, SQL-Erfassung, Herkunftsattestation oder Incidentfreigabe |

## Zweck und Ergebnisgrenze

Das [Modell](../../Tests/Contracts/dgn007_assignment_prerequisites.py) prüft
deklarierte Voraussetzungen und die Konsistenz einer vollständigen
Familienbilanz. Es ist ein separates Entwurfswerkzeug ohne Anbindung an den
bestehenden v1-Decoder, Evaluator oder Runner. Es öffnet keine Dateien,
startet keine Prozesse und stellt keine SQL-Verbindung her.

Das Ergebnis unterscheidet widersprüchliche Eingaben, fehlende Voraussetzungen
und bedingte Konsistenz. Jede positive Modellfolgerung gilt ausschließlich
unter ausdrücklich benannten **deklarativen Modellannahmen**. Unbekannte
Ausführungsdisziplin, Basisvollständigkeit, Erfassungseignung, Intervallaktivierung
oder vollständige Sichtbarkeit werden weder aus Counts noch aus JSON-Feldern
abgeleitet. Auch eine ausdrücklich deklarierte Annahme ist kein tatsächlicher
Nachweis. Alle Ergebnisse lassen `runtime_attested`,
`exact_time_inclusion_claimed` und `method_approved` falsch.

Ein fehlender geplanter Call und ein kompensierender ungeplanter Familiencall
können denselben Count vier liefern. Ein reines Modell kann einen außerhalb
seines Inputs liegenden Call nicht erkennen. Die Gegenproben unterscheiden
deshalb einen identischen Ledger mit unbekannter Herkunft von einem im
Input sichtbaren zusätzlichen Call. Nur der zweite Fall enthält selbst einen
prüfbaren Sequenzwiderspruch. Auch ein bedingt konsistenter Input weist keine
individuelle Request→Plan-Zuordnung nach.

Die sechs Felder von `Premises` sind `execution_discipline`,
`source_and_scope_eligibility`, `qs_activation`, `complete_visibility`,
`baseline_completion` und `truthful_request_completion`. Jedes Feld benötigt
explizit `DECLARED_MODEL_ASSUMPTION`; `UNKNOWN` und `MISSING` verhindern
bedingte Konsistenz. Ausgabe-Status sind `INCONSISTENT`, `NOT_ESTABLISHED` und
`CONDITIONAL_CONSISTENCY`. Feste `Issue`-Werte enthalten keine Eingabedaten
und definieren keine neuen FWK-012-Statuscodes.

## Modellierte Konsistenz

Die vollständige finale Parent-/Variant-Familie wird auf jede frühere
Capturestufe rückgebunden. Eine explizit deklarierte frühere Abwesenheit und
eine unbekannte Zuordnung bleiben getrennt. Fehlende Daten werden nicht als
Null ergänzt. Die Basis B kann null oder positiv sein. Die Bilanz
`B → B+4 → B+8` wird zusätzlich gruppenweise geprüft; passende Gesamtsummen
dürfen Wachstum, Rückgang oder Verschwinden alter Gruppen nicht verdecken.

Die Reihenfolge verwendet eigene deklarierte Ereignisordinale für Vorher-
und Nachher-Captures, Requestabschlüsse und den finalen Vergleich. Damit wird
T0-Capture vor T1 geprüft, ohne QS- und SYSUTC-Werte als gemeinsame Clock
auszugeben. Counts, Metriken und Metadaten werden an eine deklarierte
Capturegeneration gebunden. Als exemplarische gewichtete Metrik verwendet das
Modell ausschließlich `avg_rows`; CPU, Duration, Reads und Planhashes werden
hier nicht vollständig abgebildet. Stabilitätsvergleiche betreffen die
modellierten Gruppenwerte. Dies attestiert weder tatsächliche Materialisierung
noch einen transaktionalen Snapshot.

QS-Endzeiten, QS-Kataloggrenzen und SYSUTC-Requestklammer behalten separate
Relationen und unveränderte Integer-Ticks. Die ausgegebenen arithmetischen
Relationen verwenden geschlossene Requestklammern und halboffene
Kataloggrenzen ausschließlich zur Modellcharakterisierung; sie entscheiden
keine zukünftige SQL-Prüfmethode, Inklusivität oder Toleranz. Positive
Modellfragmente bestimmen die Zeitrelation; Zero-Fragmente liefern keine
Ausführungen. Diese Modellregel ersetzt keine bestehenden SQL-/v1-Extrema.
Das Modell behauptet keinen exakten Zeiteinschluss.
Insbesondere heilt ein vollständiger Ledger den v1-G13-Fehler bei
QS-First einen Tick vor SYSUTC-Start nicht.

Größenlimits dieses Modells begrenzen ausschließlich synthetische Fixtures:
sechs Snapshots, zwölf deklarierte Requests einschließlich vier Vorabrequests,
zwei Fenster, höchstens 16 Familienmitglieder, 64 Fragmente je Snapshot und
1.000 Ausführungen je Gruppe. Die vier Vorabrequests erhalten keinen erfundenen
QS-Erfassungsstatus oder gemessene Ergebniszahlen; die acht Fensterrequests
prüfen den bestehenden Vierermix samt Ergebniszahlen.
Diese Modellgrenzen legen keine zukünftigen SQL-Ledger-, Poll- oder Capturebudgets fest.
Modellierte Timeout-, Cleanup- und erste Abwesenheitsfehler bleiben sichtbar;
deklarierter Recovery-Erfolg ersetzt keinen ersten erfolgreichen Abschluss.

## Prüfung und nächste Arbeit

Die [Gegenproben](../../Tests/Static/test_dgn007_assignment_prerequisites.py)
decken positive Null- und Nichtnullbasen sowie die Gegenbeispiele des Entwurfs
ab. Der [CI-Workflow](../../.github/workflows/dgn007-assignment-prerequisites.yml)
führt ausschließlich synthetische Python-Prüfungen aus. Der unveränderte
prospektive v1-Vertrag wurde zusätzlich lokal geprüft: sein Validator und
alle 34 Fixtures bestanden unverändert. Am 2026-10-07 bestanden alle 42
Modelltestmethoden, einschließlich der unabhängigen Review-Gegenproben
zu partieller Coverage, Plan-ID-Bindung, Metrik-/Extremadrift und malformed
Records. Die elf Governance-/Projektvalidatoren sowie die fünf vorhandenen
Frameworkprüfungen bestanden ebenfalls. Diese Ergebnisse validieren nur
die ausgeführten synthetischen beziehungsweise statischen Prüfungen,
keine SQL-Sichtbarkeit oder Ausführungsmethode.

Die getrennte [Quellen-/Ausführungspfadprüfung](DGN_007_PREMISE_SOURCE_REVIEW.md)
ist abgeschlossen. Der konkrete [Beobachtungsentwurf](DGN_007_OBSERVATION_PROVENANCE_CONTRACT_DESIGN.md)
und der [Suffizienzreview](DGN_007_SATURATION_CONTINUITY_SUFFICIENCY_REVIEW.md) liegen inzwischen vor. Injektive
Sättigung aus unabhängig geschlossenem tatsächlichem Callumfang kann Erfassung
tragen; kontinuierliches RW/ALL folgt nicht daraus. Freeze-/Zugangs-/Hostgrenze,
Acquisition-/Floatregel und Kostenmachbarkeit bleiben offen. Als Nächstes
prüft ein getrenntes begrenztes synthetisches Sättigungs-/Acquisition-Gegenmodell
den expliziten Zählschluss; Tokens sind ausschließlich Modelloracle, keine
reale QS-Einzelidentität. Danach benötigt die alternative Beweisart eine
explizite Methodenentscheidung. Erst die spätere gemeinsam versionierte Umsetzung
verbindet SQL21/35, Quellenfreeze, Transport, Records, Evaluator und Coordinator.

G13, v1, DEC-068, bekannte CI-Fehler und die fehlende PR68-Mergefreigabe bleiben
unverändert. Der lokale API-Schnitt bleibt zurückgestellt. Incident-,
Ursachen-, Mitigations-, Capstone-, Teilnehmer- und Szenarioabnahme bleiben offen.
