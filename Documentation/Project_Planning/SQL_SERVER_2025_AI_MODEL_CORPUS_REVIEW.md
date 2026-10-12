# TSK-008/007: begrenzter lokaler Dokument-/Fragekorpus

Stand: 2026-10-12. Basis nach vollständig geschlossenem PR215:
`1ed895bb8bbebef286aeb46cffd4c1c97cdf6d2b`. Status: SOURCE_REVIEW_CLOSED,
Native C1 anschließend lokal bestanden; Integrationsgates offen. Dieser eigene Folgeschnitt erweitert die
[lokale AiModel-Komponente](SQL_SERVER_2025_AI_MODEL_COMPONENT_REVIEW.md) um
vier unterschiedliche feste Eingaben und ein unabhängig eingefrorenes
synthetisches Rangoracle. TSK-007 und TSK-008 bleiben offen.

## Frisch geschlossene Vorgrenze

PR215 ist vollständig integriert: neun aktuelle Head-/sieben Main-Workflows
PASS, Squash `1ed895bb8bbebef286aeb46cffd4c1c97cdf6d2b`, voller identischer
Tree `3b38543fbefe0584f5da57326ba9840669cacba1`, main per Fast-forward
synchronisiert und sauber, eigener lokaler und Remote-Branch entfernt.
Die vorherigen zwei lokalen 768-Vektorrückgaben und das bestätigte eigene
Prozessende bleiben separate Komponentenevidenz. Kein zusätzlicher Modellaufruf
für deren reine Ergebnis-/Integrationsprüfung; keine Umdeutung zur Korpusabnahme.

## Fester Input- und Ergebnisvertrag

Die öffentliche `Invoke-SqlServerLabAiModel`-API am sauberen Lab-Commit
`f4c9fcd30c397e25c95e57d7aeecc98dc194063e` bleibt der einzige Inferenzweg.
Der Caller bindet ein exportiertes CommandInfo an Modulname, tatsächlichen
Modulpfad und öffentliche Funktionsdatei; keine Privatfunktionsaufrufe oder
Overrides. Vorhandenes `nomic-embed-text:latest`, Katalogkey
`ollama-nomic-embed-text-v1-5`, lokale Lane, Port11434, Dimension768, Egress
denied und kein CredentialRef. Keine Änderung an Labcheckout, Modell-/Dienst-
installation, Downloads, Neustarts, Trust, Container oder Cloudfallback.
Die vorhandenen Gewichte dürfen für die freigegebene Inferenz geladen werden;
Geräte-, Cache- und RAMzustand werden nicht qualifiziert.

Vier feste unterschiedliche synthetische englische Eingaben, in dieser Reihenfolge:

| ID | Vollständiger übergebener Text |
|---|---|
| A | `search_document: Synthetic module A contains red building blocks.` |
| B | `search_document: Synthetic module B contains blue building blocks.` |
| C | `search_document: Synthetic module C contains green building blocks.` |
| QUERY | `search_query: Which synthetic module stores crimson building blocks?` |

Die API ergänzt die Retrievalpräfixe nicht selbst. Dokument A ist vor Admission
als erwartetes Top1 eingefroren, unabhängig von später beobachteten Scores.
Vier tatsächliche erfolgreiche Rückgaben müssen richtigen Modell-/Plan-Key,
Attempts1 und jeweils alle768 numerischen endlichen Koordinaten liefern.
Positive endliche Normen werden aus den vollständigen Vektoren neu berechnet.
Die Records binden Ordinal, ID, UTF8-Input-SHA256, Dimension, Norm und dieselbe
beobachtete Modell-/Digest-/Versions-/Planidentität.

Das reine Pythonoracle berechnet Cosine aus sämtlichen Koordinaten. Alle vier
Vektoren müssen unterschiedlich sein. Dokument A muss eindeutiges Top1 sein;
auch ein Gleichstand auf den unteren Rängen ist FAIL. Ein Scoreabstand von
höchstens1e-12 zählt als Tie. Fehlende/falsche Population, Input-/Typ-/Boolalias-,
NaN-/Infinity-/Nullnorm-, Modell-/Plan- oder Rangabweichung wird verworfen.
`CAPTURED_CORPUS_ONLY` ist nur vollständiger Capture; erst das unabhängige
Rangoracle kann `PASS_SYNTHETIC_CORPUS_ONLY` liefern. Das ist ein einziger
didaktischer Dokument-/Synonymfall, keine allgemeine Modell- oder Retrievalqualität.

## Lokale Bindung und endlicher Umfang

Feste Loopback-Requests ohne Proxy/Redirect lesen version/tags/show. Exakter Tag,
eindeutiger vollständiger Live-Digest, fehlende remote_host/remote_model-Felder,
Embedding-Capability und tatsächliche Dimension sind vor und nach jedem
Inferenzcall gebunden. Diese Beobachtungen sperren den fremd verwalteten
vorbestehenden Dienst nicht atomar; keine solche Prozess-/Artefaktattestation.
Modellkarte und öffentliche API werden über SRC-112/SRC-113 wiederverwendet;
keine neue Source-ID. Der Live-Digest ist keine vollständige Supply-Chain-Abnahme.

Ein Implementierungsverantwortlicher, Root als unabhängiger Reviewer der neuen
Risiken. Maximal sechs kohärente Quellenkandidaten, Dreiercheckpoint/hard6,
höchstens24 öffentliche Inferenzcalls und162 Metadatenrequests über diese Welle.
Ein Profil je Kandidat. Jede Admission reserviert konservativ4+27; auch FAILs
zählen weiter. Folge nur nach geschlossenem FAIL und relevant geänderten
Ausführungsquellen, kein unveränderter Retry oder Folgekandidat nach PASS.
Kandidat4 benötigt den registrierten Dreiercheckpoint am SHA256 des vollständigen
vorherigen Ledgers. UNKNOWN oder unbestätigtes Kindende sperren Folgeadmission.

C1: vier APIcalls, Retry0, je30Sekunden; genau27 Metadatenadmissions, je höchstens
5Sekunden (drei initial plus je drei vor/nach jedem der vier Calls). Ein eigener
NoProfile-Caller besitzt300Sekunden Parentbudget einschließlich Startup und
genau eine gemeinsame5Sekunden-Reapingdeadline. Kill betrifft ausschließlich
seinen gespeicherten Childhandle, niemals den vorbestehenden Modelldienst.
Collector-/Timeout-/Kill-/Reapingfehler bleiben fail-closed. Auch bei später
bestätigtem Kindende wird UNKNOWN nicht zu Inferenz-PASS. Keine zusätzlichen
blockierenden Stream-Close-/Threadjoin-Aufrufe und kein Deadline-Reset.
Ein real provozierter Timeout-/Killfall ist NOT_ESTABLISHED.

## Quellenreview, Vorbereitung und ausführbarer Ablauf

Die bekannten CommandInfo-/LabSource-/Loopback-/LocalBinding-/Secret-/UNKNOWN-
Grenzen aus dem vorherigen Komponentenschnitt werden bei gebundenen Quellen
wiederverwendet, keine erneute breite Helper-/Runtimeanalyse. Root hat die neuen
vier Inputs, Counter, vollständige Recordpopulation, Cosine-/Tie-/Identitätsoracle,
300s+5s und seriellen Ledger/Checkpoint unabhängig geprüft: keine offenen P1/P2.
13 fokussierte reine Pythonmethoden und PS-SelfTest INPUTS_4/COUNTER_NEGATIVE_4
bestanden. Parent-Popen war ausschließlich Mock; keine echte Modell-/Metadata-
oder SQLausführung durch die Vorbereitung. Modell-/Tokenverbrauch unbekannt.

`Runtime/AI_MODEL_CORPUS/prepare.py` bindet die fünf geprüften aktuellen
Corpusdateien, sauberen Lab-Commit und sechs bekannte vollständige Labquellbytes,
registriert privaten budget/source-proof und diese genau fünf Dokumentupdates.
Erst nach deren vollständiger Bindung schreibt es die exklusive C1-Admission.
Der Parent verlangt kanonischen Scope und tatsächliche Caller-/Launcher-/
Oracle-SHAs, erzeugt exklusiv sein Kandidatenverzeichnis und reserviert den
Ledger vor Popen. Der Caller verlangt die gebundene Parentadmission.

```powershell
# Ausschließlich Root nach Quellenabschluss; keine APIcalls im prepare-Schritt:
python Runtime/AI_MODEL_CORPUS/prepare.py
# Erst danach genau ein tatsächlich aufgenommenes C1-Profil:
python Runtime/AI_MODEL_CORPUS/launch.py
```

Vollvektoren, Inputhashes, Bindungen, Rawreceipt, Parentproof und Ledger bleiben
ausschließlich im ignorierten Runtime. stdout enthält nur Status/Zähler;
begrenzte Summary enthält drei Scores, Top1 und Marge, keine Rohidentitäten,
Prompts oder Vektoren. Noch keine Native-C1-Evidenz und keine erneute Inferenz
für Dokument-/Source-/Ergebnisprüfung. Null SQLcalls; SQL/HTTPS, Generator/RAG,
Cloud/ONNX, Antwort-/allgemeine Retrievalqualität und vollständige TSK007/008-,
QRY020-, Demo-, Modul- und Workstreamabnahme bleiben offen. Ein etwaiger weiterer
SQL-VECTOR-/Exact-Retrievalschnitt ist nicht Teil dieses Vertrags.


## Tatsächliches C1-Ergebnis

C1 lokal bestanden: vier erfolgreiche öffentliche Inferenzaufrufe, 27 gebundene
Metadatenrequests, vier vollständige 768-Vektoren/3072 endliche Koordinaten.
Der getrennte Root-Verifier bindet ausgeführte Caller-/Parent-/Oraclequellen,
sechs Labquellen, sauberen unveränderten Lab-Commit und das bestätigte eigene
Prozessende. Er berechnet alle Cosines zusätzlich mit eigener Summenformel neu;
kein weiterer Modell- oder SQLaufruf für diese Prüfung.

| Dokument | Tatsächlicher Cosine-Score |
|---|---:|
| A | 0.8031306189541002 |
| B | 0.7859511311854047 |
| C | 0.7826607701190610 |

Das vorab festgelegte Dokument A ist eindeutiges Top1; Abstand zum zweiten
Dokument 0.01717948776869549. Keine Ties, identischen Vektoren, fehlenden
Records oder UNKNOWN. Ausschließlich dieser eine synthetische englische
Dokument-/Synonymfall ist bestanden; Scores und Margin sind keine allgemeine
Relevanzschwelle oder Deutsch-/Domänen-/Antwortqualitätsabnahme. Keine SQL-
Persistenz, generative Antwort, neue Dienste oder Hoständerung. Bestehender
Modelldienst bleibt erhalten; RAM-/Cache-/Geräteeffekte nicht attestiert.
Ein Quellenkandidat verbraucht; kein Wiederholen nach PASS. Modell-/Tokenverbrauch
unbekannt. Aktuelle Head-/Main-/Tree-/FF-/Ownbranchgates folgen vor Abschluss.
TSK007/008, QRY020, Live-RAG und volle Workstreamabnahme bleiben offen.
