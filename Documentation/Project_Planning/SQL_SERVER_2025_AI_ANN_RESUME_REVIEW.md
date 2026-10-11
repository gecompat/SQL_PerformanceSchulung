# TSK-006 – FAIL der begrenzten ANN-Wiederaufnahme

Stand: 2026-10-11. Basis `4f74caeb55dcbdaabd9f2176e7ced9dd77c103dc`.
Der Benutzer genehmigte das [Zusatzpaket](SQL_SERVER_2025_AI_ANN_RESUME_DECISION.md)
ausdrücklich mit „Ja, Zusatzpaket freigeben (empfohlen)“. Beide zusätzlichen
Korrekturkandidaten wurden jeweils einmal auf einer neuen eigenen Instanz ausgeführt
und sind FAIL. Keine dritte Kandidatenänderung oder unveränderte Wiederholung.
IDX-011/IDX-012 bleiben PROPOSED; kein öffentliches FWK-Paket oder ANN-Abnahmeclaim.
Der [ursprüngliche Fehlercheckpoint](SQL_SERVER_2025_AI_ANN_PREVIEW_REVIEW.md) bleibt erhalten.

## Geänderte private Vorbereitung und Review

Separate Quellen unter dem ignorierten `Runtime/ANN_RESUME_CANDIDATE01/` ersetzen
die direkte VECTOR→varbinary-Konversion durch vollständiges nvarchar-JSON und
dessen Unicode-Bytes. Vorgesehen sind Dimension/float32-Metadaten, numerische
Koordinaten, JSON-Roundtrip, bidirektionale Sourcebindung, vollständige
Indexmetadaten sowie Host-/DB-Optionsvergleiche. Eine erfolgreiche Gesamtbindung
oder ANN-Runtime wird damit noch nicht behauptet.

Cleanup verwendet eine gemeinsame monotone 60-Sekunden-Deadline. Die maximalen
Prozessbudgets betragen zusammen 50 Sekunden: Recovery 8, separater SQL-Abwesenheits-
Client 4, Containerbestand 4, vollständige CID-/Image-/Ownerprüfung 6, Entfernen 18
und separate Containerabwesenheit 10. Zehn Sekunden sind für Nachbehandlung reserviert.
Tatsächliche Überschreitung bleibt FAIL; lokale Mocks sind keine empirische
Qualifikation hängender Betriebssystem-Prozessstarts. SQL-Recoveryfehler erreichen
über finally weiterhin den gebundenen Containercleanup. Original-/Recoveryfehler
und redigierte stdout-/stderr-Ausgaben bleiben getrennt sichtbar.

Sieben isolierte Python-Sicherheitsfixtures bestanden vor SQL: OSError, Timeout und
SQL-Fehler mit anschließendem Containerabbau, fremder Owner, veränderte CID/Image/Name,
vollständig verbrauchtes 50-Sekunden-Callbudget, tatsächliche Deadlineüberschreitung,
ungültige Baselines und leere Recoveryausgabe. Kein SQL- oder Containeraufruf in diesen
Fixtures. Ein erforderlicher enger unabhängiger Quellenreview fand P2: der Start
verwendete noch den veränderlichen Image-Tag. Der Fix startet unmittelbar die
freigegebene vollständige lokale Image-ID; der gezielte Nachcheck schloss den Befund.

## Tatsächliche Runtime und Fehler

Beide neuen seriellen eigenen Podmancontainer verwendeten ausschließlich Image-ID
`78eb6a93ef20501bd754282cc216188a0acee1cfa6119c33eef0b21599c1f726`, Build
17.0.5005.3, Enterprise Developer/EngineEdition 3, Linux Ubuntu 24.04, vier CPUs/sechs
GiB und ausschließlich ihren eigenen Loopbackport. Die Instanzen wurden unmittelbar
mit dieser ID gestartet, CID/Image/Owner danach erneut gebunden. Native SQLCMD nutzte
Passwörter ausschließlich aus der Umgebung. Eigene synthetische DBs hatten vier
vollständige Marker, CL170/SIMPLE und 256/64-MB-Dateilimits. Keine bestehende Instanz,
andere Repositoryquelle, Cloud-/ONNX-/Modell- oder Hostoption wurde verändert.

| Kandidat | Beobachtung | Cleanup |
|---|---|---|
| 01 | Python verwarf die Setupausgabe als fehlenden exakten Baselinebeleg, bevor die ANN-Probe aufgerufen wurde. Die erfolgreiche Setupausgabe wurde vor Interpretation nicht erhalten; die konkrete Ursache bleibt unbekannt. | Tatsächliches `RESTORED_0` und `DROP_CONFIRMED`; separater neuer SQL-Client bestätigte DB-Abwesenheit, gebundener Containerabbau und separate Abwesenheit bestanden. Gemessene gemeinsame Cleanupdauer 12,112 s. Kein Lifecycle-PASS. |
| 02 | Geänderte Auswertung toleriert ausschließlich den exakten eigenen SQLCMD-Kontextwechseltext; `-m 1` unterdrückt Meldungen der Severity 0. Setup-/Probeausgaben werden vor Interpretation erhalten. Tatsächlicher Baselinebeleg 0. Die dynamische `CREATE VECTOR INDEX`-DDL scheiterte mit Fehler 343, anschließend 51003 „Index identity missing“. | Tatsächlicher Restore auf die vorher erfasste 0 und `DROP_CONFIRMED`; separater SQL-Client bestätigte DB-Abwesenheit, gebundener Containerabbau und separate Abwesenheit bestanden. Gemeinsame Cleanupdauer 12,117 s. Kein Lifecycle-PASS. |

Für Kandidat 02 bestanden zwei betroffene lokale Baselinefixtures: fehlende/NULL-/
ungültige/doppelte/fremde Baselines bleiben abgewiesen; allein der exakte eigene
Kontextwechseltext ist zusätzlich zulässig. Fremde oder unbekannte Zusatzzeilen
werden nicht akzeptiert. Der enge unabhängige Deltareview fand keine weiteren P1/P2.
Die SQL-Quelle ist gegenüber Kandidat 01 byteidentisch. Der Meldungsfilter entspricht
der [SQLCMD-Dokumentation](https://learn.microsoft.com/en-us/sql/tools/sqlcmd/sqlcmd-utility?view=sql-server-ver17#error-reporting-options);
er beweist nicht die unbekannte Ursache des ersten Fehlversuchs.

Der erhaltene SQL-Fehler lautet „Unknown object type 'VECTOR' used in a CREATE,
DROP, or ALTER statement.“ Die dokumentierte Preview-DDL wurde in dynamischem SQL
nach dem vorgesehenen eigenen Preview-Enable versucht. Die tatsächliche Einstellung
unmittelbar vor der DDL wurde nicht separat attestiert. Ob Batch-/Sessiongrenzen,
Featurekonfiguration oder eine andere Buildgrenze den Parserfehler erklären, bleibt
offen. Kein stiller zusätzlicher GO-/Konfigurations-/Syntaxversuch innerhalb des
verbrauchten Budgets. [CREATE VECTOR INDEX](https://learn.microsoft.com/en-us/sql/t-sql/statements/create-vector-index-transact-sql?view=sql-server-ver17)
und [VECTOR_SEARCH](https://learn.microsoft.com/en-us/sql/t-sql/functions/vector-search-transact-sql?view=sql-server-ver17),
geprüft am 2026-10-11, ersetzen die fehlende lokale Featurequalifikation nicht.

Beide eigenen Container sind abwesend. Diesmal liegen unabhängige SQL-DB-
Abwesenheitsbelege und tatsächliche Recovery-Restoreausgaben vor; sie heben die
primären Fehler nicht auf. Keine gemessene Indexgeneration, ANN-Resultatmenge,
Recall-, Plan- oder Performanceabnahme und keine zwei stabilen positiven Lifecycles.
Vorgesehene Marker-/Result-/Sourcegegenfixtures sind keine vollständige FWK-Abnahme.

## Quellenbindung und endliches Budget

| Private Quelle | SHA256 |
|---|---|
| Kandidat 01, qualify.py | `45C69FF40BB6CBD5A2C6D490403E5D4806F8CBFF2CAB8AB568125D8F31B23D93` |
| Beide Kandidaten, sql_sources.py | `1D72CCF7C601A40FDD11B30BAE3FD69D3EF812F03C971CD86593A42A9576793F` |
| Kandidat 01, test_safety.py | `3F42DD87ACA8500FB645B9784BF79C36073244928DBCAD55317D54F7F31BF8C0` |
| Kandidat 02, qualify.py | `F4F2D13D1332D1CAF3406C127B8A5853A4126A6C71F87D66225E97F7FAC6B7CE` |
| Kandidat 02, test_safety.py | `53A5071C91169E6E19B3F3CD642559572D47E4C8A590AB84833672D0F1A70A00` |

Die drei historischen Prototypquellen und beide neuen Kandidaten bleiben erhalten.
Zwei von höchstens vier zusätzlichen Containern wurden verwendet; beide erlaubten
Kandidaten sind verbraucht. Die ungenutzten Containerplätze autorisieren keinen
dritten Korrekturkandidaten. Ein Implementierungsowner, ein unabhängiger Reviewer
mit gezielten Befund-/Kandidatdeltas; Modell-/Tokenverbrauch bleibt unbekannt.

Der ANN-Schnitt bleibt angehalten. Eine weitere Wiederaufnahme benötigt zunächst
ein konkretes Paket für den Parser-/Preview-Nachweis und einen neuen ausdrücklichen
Budgetentscheid. Erst danach sind zusätzliche SQL- oder Codekorrekturen zulässig;
die Effektfreigabe wird dadurch nicht erweitert. Unabhängige autorisierte
Lehrmaterialarbeit für die acht qualifizierten Offline-Demos bleibt zulässig.
Der Heartbeat bleibt als Wiederaufnahmeabsicherung aktiv und setzt dieses Budget
nicht zurück. Der Gesamtworkstream ist weiterhin offen.
