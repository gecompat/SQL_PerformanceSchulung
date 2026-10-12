# TSK-008: lokale SQL-Persistenz und Exact Retrieval des festen Modellkorpus

Stand: 2026-10-12. Status: SOURCE_REVIEW_CLOSED; Native C1 anschließend lokal bestanden; Integrationsgates offen. Basis nach vollständig geschlossenem
[PR 216](https://github.com/gecompat/SQL_PerformanceSchulung/pull/216):
`914f8b72f61ab3d538c3898c2b56db4c8dbc4cf8`, acht Head-/sechs Main-Workflows
PASS, voller identischer Tree, lokales main synchronisiert und sauber,
eigener lokaler und Remote-Branch entfernt.

## Aussage und Grenze

Dieser selbständige private Komponentenschnitt übernimmt ausschließlich die
bereits tatsächlich erzeugten vier vollständigen Vektoren des
[festen Dokument-/Fragekorpus](SQL_SERVER_2025_AI_MODEL_CORPUS_REVIEW.md).
Receipt und unabhängiger Vollrecordnachweis werden an ihre vollständigen
Dateihashes gebunden. Keine erneute Inferenz, keine Lab-RAG-/Privatfunktions-
oder Secretumgehung. Die registrierte QRY-018-Demo bleibt ein Offline-Replay;
dieser zusätzliche Entwicklungstest deutet sie nicht zur Live-RAG-Abnahme um.

Drei Dokumente und ein Fragevektor sollen als VECTOR(768) mit tatsächlichem
float32-Basistyp in der eigenen Testdatenbank gespeichert und vollständig
zurückgelesen werden. Das vorab eingefrorene Dokument A muss auch beim
SQL-Exact-Retrieval eindeutiges Top1 sein. Alle drei Cosine-Scores werden gegen
eine unabhängige vollständige Pythonberechnung geprüft; feste Toleranz 1e-5.
Metadaten allein, ein leeres Ergebnis oder ein abgeschnittener Vektor genügen
nicht. Länge und SHA256 binden den vollständigen nativen JSON-Transport;
das ist kein pauschaler Nachweis physischer VECTORbytes. Die tatsächliche
float32-Projektion und Koordinatenprüfung sind gesondert auszuweisen.

## Eigener Umfang, Gegenproben und Cleanup

Ein bereits vorhandenes festes Image
`78eb6a93ef20501bd754282cc216188a0acee1cfa6119c33eef0b21599c1f726`,
beobachteter Zielbuild 17.0.5005.3, MSSQL_PID=Developer und tatsächlicher EngineEdition3, CL170. Kein aus der
Buildnummer geratener CU-Claim. Ein serieller neuer eigener Testcontainer je
Quellenkandidat, vier CPU/6 GiB und ausschließlich Loopback; kein allgemeiner
Provisioner, keine Änderungen an anderen Repositories oder Diensten.
Kein Preview, MAXDOP-, Trust-, Host-, Cloud- oder ONNX-Effekt.

Eigene feste Datenbank SQLPERF_LAB_QRY018_CORPUSSQL. Vor Mutation und Cleanup
müssen alle vier vollständigen Frameworkmarker bytegenau stimmen:
SQLPERF.Project=SQL_PerformanceSchulung, SQLPERF.ContractVersion=1.0,
SQLPERF.DemoId=QRY-018, SQLPERF.RunToken=CORPUSSQL. Keine verkürzten Marker,
Leerzeichen- oder Typaliasvergleiche. Vor Setup ist echte DB-Abwesenheit Pflicht.

Nach einer tatsächlichen positiven Ergebnisprüfung folgen gezielte Gegenproben
zu fehlender Quelle, fehlendem Record und falschem erwarteten Top1. Vier
falsche Eigentumsmarker müssen Mutation und Cleanup vor ihrem Effekt abweisen.
Vollständige Vorher-/Nachherzustände und tatsächliche markergebundene Repairs
sind Pflicht; historische FAILs werden nicht überschrieben. Cleanup prüft
erneut vollständige Eigentümerschaft, führt den echten Drop aus und belegt
DB-Abwesenheit frisch sowie zusätzlich unabhängig im Parent. Eigener voller
Container-CID und Name müssen danach als abwesend belegt sein. SQLinputdateien
werden nur bei bestätigtem Clientende entfernt; UNKNOWN sperrt weitere SQL-
Aufrufe und bewahrt die eigenen Recoveryinputs. Ein bloßer Cleanupversuch ist
kein PASS.

## Endliches Budget und Nachweis

Ein Implementierungsverantwortlicher und Rootreview ausschließlich der neuen
Inputs, Ergebnisoracles, Ownership-/Negativ-/Restore- und Budgetbindungen.
Vorhandener qualifizierter KnownEnd-/SQLCMDPASSWORD-/Readiness-/Containerpfad
wird quellgebunden wiederverwendet. Keine erneute breite Legacyanalyse,
Reviewkette oder unveränderte Runtimewiederholung.

Höchstens sechs kohärente Quellenkandidaten und sechs serielle eigene Container,
ein Profil je Kandidat, Dreiercheckpoint und harter Stopp nach sechs. Retry
setzt einen geschlossenen FAIL und relevant geänderte Ausführungsquellen voraus;
kein Folgelauf nach PASS. Je Kandidat 300 Sekunden einschließlich Startup und
eine gemeinsame separate Cleanupdeadline von 60 Sekunden, ohne Reset pro Phase.
Nach unbekanntem Client-/Containerende keine neue Admission. Rohvektoren,
Prompts, Nativeausgaben, tatsächliche Infrastrukturmetadaten und Ledger bleiben
im ignorierten Runtime. Modell-/Tokenverbrauch unbekannt; dieser Schnitt plant
null neue Modellaufrufe.

Primärquellen SRC-072 (VECTOR/float32/JSON), SRC-073 (VECTOR_DISTANCE),
SRC-076 (VECTORPROPERTY) sowie die bestehenden SRC-112/SRC-113 zur getrennten
Modellherkunft; keine neue Kennung. Allgemeine Retrieval-/Deutsch-/Domänen-/
Antwortqualität, generative Antwort, SQL-HTTPS, voller Live-RAG, TP-PERF,
TSK-007/008 und Workstreamabnahme bleiben offen. Quellenreview, fokussierte
reine Tests, tatsächliches C1-Ergebnis und aktuelle PR-/Head-/Main-/Tree-/FF-/
Ownbranchgates folgen vor Abschluss.

## Unabhängiger Quellenabschluss vor Native

Ein Implementierungsverantwortlicher; Root hat neue vollständige Input-/
Transport-/Koordinaten-/Cosine-/Source-/Ownership-/Restore-/Cleanup- und
Budgetbindungen geprüft. Drei konkrete Befundgruppen vor Admission geschlossen:
unbelegte feste DATALENGTH-Gesamtbytezahl, importkontextabhängige Sourcemenge
und SELECT-Header/PRINT-Diagnosekanal im Vollscalarpfad. Die aktuelle Population
bindet29 ausdrücklich ausgewählte Quellen, zehn vollständig gerenderte feste
ReviewSQLs und unveränderte qualifizierte Parent-/Readiness-/Containerbasis.
Frames benutzen bounded PRINT im tatsächlich gelesenen Diagnosekanal; alle
Outputstellen einschließlich unabhängiger Identityprobe sind gebunden.
Keine offenen P1/P2 und keine Reviewkette.

Acht fokussierte reine Methoden Normal/-O bestanden; nach dem engen PRINTfix
drei tatsächlich betroffene Transport-/Source-/Identitymethoden bestanden.
Anfängliche lokale Testimportpfadfehler und die Legacy-Modulnamenskollision
wurden vor Admission behoben; keine Runtimeeffekte. Keine unveränderte breite
Legacytestwiederholung. C1 reserviert einen eigenen Container; ein gemeinsames
20s-SQL-Recoveryfenster liegt innerhalb derselben einmaligen60s-Cleanupdeadline.
Native SQLsyntax, tatsächlicher Roundtrip und Cleanup sind bis C1 unbelegt.


## Tatsächliches C1-Ergebnis

C1 auf genau einem neuen eigenen Container lokal bestanden. Tatsächlicher
Build17.0.5005.3/EngineEdition3/CL170, konfigurierte Developer-Testinstanz.
69 Nativephasen ohne Bootstrap, 29 vollständige tatsächliche Zustände,
vier gespeicherte und vollständig zurückgelesene VECTOR768/float32-Records
mit3072 endlichen Koordinaten. Die eigenständige Rootprüfung bindet alle29
ausgeführten Quellen, die vollständigen69 Nativeausgaben und jeden Zustand
an die Profilevidenz. Keine weitere SQL- oder Modellqualifikation hierfür.

| Dokument | Tatsächlicher SQL-Cosine-Score (1 minus Distance) |
|---|---:|
| A | 0.8031306862831116 |
| B | 0.7859511971473694 |
| C | 0.7826607823371887 |

Dokument A ist eindeutiges Top1. Root berechnet zusätzlich alle Cosines aus
den tatsächlich zurückgelesenen vollständigen Koordinaten neu; sämtliche
Abweichungen liegen innerhalb der vorher festgelegten1e-5-Toleranz.
Maximale Koordinatendifferenz zum ursprünglichen Modelreceipt
4.0000000117723644e-9; zur unabhängig berechneten float32-Projektion
4.020118710146292e-9. Dies ist ein numerischer tolerierter Roundtrip,
kein bitgenauer Nachweis physischer VECTORbytes. Tatsächliches DATALENGTH
je Vektor3080Bytes in genau diesem Lauf; JSON-Darstellung und elementare
Koordinatengröße werden davon getrennt. Keine allgemeine Speicherformel.

Nach positiver Kontrolle wurden fehlender Resultatrecord, falsches erwartetes
Top1 und tatsächlich gelöschte Quelle dreimal nativ mit51003 abgewiesen.
Die vollständige Quelle wurde tatsächlich wiederhergestellt. Vier falsche
Marker lösten vor Persist/Delete/Restore/Cleanup insgesamt16 echte51004 aus;
alle vollständigen Vorher-/Nachherzustände blieben gleich. Vier tatsächliche
Markerrepairs stellten jeweils den vollständigen ursprünglichen Zustand her.

Eigentumsgebundener Drop tatsächlich ausgeführt, DB-Abwesenheit neu im Probe
und unabhängig im Parent geprüft. Eigener voller CID und Name nach Cleanup
zusätzlich frisch durch Root als abwesend bestätigt, eigene SQLinputdateien0,
kein UNKNOWN. Ein Kandidat/ein Container verbraucht, kein Retry nach PASS.
Null neue Inferenz-/Metadatenrequests; Modell-/Tokenverbrauch unbekannt.
Startup zeigte regulär behandelte vorübergehende Readinessfehler. Ein erster
Root-Recordreader erwartete bei Setup/Drop keinen benignen Contextwechseltext;
nach enger Bindung genau dieser zwei tatsächlich erhaltenen Meldungen bestand
die reine Prüfung. Kein Native-Retry, keine Umdeutung eines Runtime-FAIL.

Dies bleibt ein einzelner synthetischer englischer Persistenz-/Suchfall;
allgemeine Retrieval-/Deutsch-/Domänen-/Antwortqualität, Generator, SQL-HTTPS,
voller Live-RAG und TSK007/008-/Workstreamabnahme offen. Aktuelle Head-/Main-/
Tree-/FF-/Ownbranchgates folgen vor Abschluss.
