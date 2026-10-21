# CON-010 – begrenzter Implementierungscheckpoint

Stand: 2026-10-11. TSK-009/CUR-018. Basis
`05e4228d77170c316a7cca231e36e5610e1764ec`.
Status: FAIL / angehalten nach zwei kohärenten Korrekturwellen. CON-010 bleibt PROPOSED;
kein ausführbares Demopaket, kein unabhängiger Quellenreview und keine Runtimefreigabe
wurden integriert. Die bereits bestandene private Identitätsvorprobe ist im
[QRY-019-Checkpoint](SQL_SERVER_2025_AI_SQL_INPUT_REVIEW.md#nächster-checkpoint-private-con-010-vorbereitung)
getrennt geführt.

## Versuch und konkrete Abbruchgrenze

Ein Implementierungsverantwortlicher erzeugte einen lokalen FWK-010/FWK-011-Kandidaten
mit zwei synthetischen Quellen und identischen VECTOR(3)-Werten. Drei WITHOUT LOGIN
Benutzer sollten RLS (Row-Level Security; zeilenbezogene Zugriffskontrolle), manipulierten Sessionkontext, Policy-ALTER, fremde Impersonation
und Owner-Revoke kontrollieren. Der privilegierte dbo-Labowner war im Prädikat
ausdrücklich erlaubt. Quellen und Vektoren lagen gemeinsam unter RLS; feste dynamische
SELECTs sollten SELECT-Berechtigungen ohne Eigentumsketten-Bypass prüfen.

Der erste vollständige 17.x-Lauf scheiterte in SETUP mit Fehler 2760: die statische
Policy-DDL (Data Definition Language; Anweisungen zum Definieren und Ändern von Datenbankobjekten) wurde vor der im Batch dynamisch erzeugten sec-Schema-/Funktionsbindung
kompiliert. Korrekturwelle 1 verschob diese DDL in ein festes dynamisches Batch.
Der zweite Lauf erreichte BASELINE und scheiterte mit 51003/FAIL_RESULT_CONTRACT an
der exakten Policydefinition. Eine gesonderte begrenzte Metadatenprobe zeigte die
tatsächliche Definition `([sec].[TenantPredicate]([TenantId]))`, predicate_type 0 und
operation NULL. Korrekturwelle 2 band diese vollständigen Bytes und ergänzte die
vom Guidevalidator geforderten Anleitungselemente.

Der dritte vollständige Lauf bestand SETUP sowie die RLS- und Quellenbindung und
scheiterte in BASELINE mit 51003/FAIL_RESULT_CONTRACT an der eingefrorenen Rechtefixture.
Eine neue reine Metadatenprobe zeigte die Ursache: CREATE USER WITHOUT LOGIN erzeugt
hier je Benutzer einen CONNECT-Grant auf Datenbankebene zusätzlich zum ausdrücklich
erteilten SELECT-Grant auf lab.Documents. Der Kandidat erwartete ausschließlich drei
SELECT-Einträge statt der tatsächlich vorhandenen sechs genau zu bindenden Einträge.
Alle drei Benutzer hatten type S und authentication_type 0 / NONE.

Das ist eine fehlerhafte Kontrollfixture, kein bestandener Tenant-/Revocationnachweis.
Keine dritte Korrektur oder unveränderte Wiederholung wurde ausgeführt. Die vereinbarte
Grenze von zwei Korrekturwellen hält diesen Slice an. Ein künftiger neu abgegrenzter
Schnitt benötigt die vorliegende neue Metadatenevidenz, vollständige CONNECT-/SELECT-
Bindung, erfolgreiche fachliche Lifecycles und den erforderlichen unabhängigen Review.
Eine bloße Erhöhung oder Entfernung der Rechtezählung ist keine Sicherheitsabnahme.

## Evidenz, Cleanup und Aufwand

Jeder vollständige Fehlversuch beendete markergebundenes CLEANUP mit PASS/OK; der
Runtimeadapter prüfte die unabhängige DB-Abwesenheit vor Ergebnisbewertung. Beide
Metadatenproben bauten ihre eigene Datenbank ab. Alle fünf eigenen Container wurden
nach exakter Ownerlabelbindung entfernt und ihre Abwesenheit separat geprüft.
Keine andere Instanz, kein anderes Repository, Provider oder Modell wurde verändert.

Die Kandidatquellen, vollständige lokale Änderungspatch und Wiederaufnahmehelper sind
unter dem ignorierten Runtime-Verzeichnis gesichert; sie sind keine kanonische
Backlogwahrheit oder integrierte Demo. Die erfolgten Katalog-/Manifestregistrierungen
wurden vollständig zurückgenommen. Die integrierte Matrix bleibt bei 29 Demopaketen
und 336 geplanten Provider-/Versionsläufen; es wurden keine neuen Matrixläufe behauptet.

Frameworkprüfung, sieben vorhandene KI-Runner-Unitmethoden, 30-Demo-Pfadvalidator und
348-Lauf-Katalogvalidator bestanden am verworfenen Kandidaten; der Guidevalidator
meldete zunächst drei fehlende Anleitungsanforderungen. Diese Prüfergebnisse validieren
keinen Tenant-SQL-Lifecycle. Kein unabhängiger Review wurde für den instabilen Kandidaten
verbraucht. Modell-/Tokenverbrauch bleibt unbekannt. Eine Implementierung, zwei
Korrekturwellen, drei vollständige Fehlversuche und zwei begrenzte neue Metadatenproben
bilden den abgeschlossenen Aufwand dieses Checkpoints.

Serverlogin, echte Verbindungspools, mehrere Sessions, ANN (Approximate Nearest Neighbor; näherungsweise Suche nach ähnlichen Vektoren)/Postfilterverhalten und
allgemeine Seitenkanalfreiheit bleiben UNQUALIFIED. Live-Lab-RAG (Retrieval-Augmented Generation; Antworterzeugung mit zuvor ausgewählten Quellen) bleibt am bestehenden
DEC-033-Secretgate blockiert; Cloud-/Bezahl- und ONNX-/rote Hoständerungen sind nicht
freigegeben. Der nächste unabhängige zulässige Schritt ist die synthetische Offline-
Vorbereitung von DGN-009 gemäß registriertem Demoentwurf, ohne Live-Modellaufruf.

Der reine FAIL-Checkpoint wurde über [PR 140](https://github.com/gecompat/SQL_PerformanceSchulung/pull/140)
integriert: sieben Headprüfungen auf `79ab040711187d95a0cf7d2f2272996e826e9453` und
fünf Main-Workflows auf Squash `26461f9f9716da3e83f0a807c9e0d64acdf7a45e` bestanden.
Vollständige Tree-Identität, main-Synchronisierung und eigener lokaler/remote
Branchabbau wurden geprüft. Diese Dokumentintegration ändert den fachlichen FAIL
nicht. Der anschließende DGN-009-Schnitt ist im [eigenen Nachweis](SQL_SERVER_2025_AI_INJECTION_REVIEW.md)
abgeschlossen; die nächste DGN-008-Vorbereitung wird getrennt geführt.
