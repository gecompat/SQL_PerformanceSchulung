# DGN-007 – begrenzter SQL-Capture-Producer-Nachweis

| Merkmal | Wert |
|---|---|
| Stand | 2026-10-07 UTC / Europe/Vienna |
| Status | 18 lokale Producer-Lifecycles im ursprünglichen Freeze PASS; Producer-Integration nach SQL-2025-CI-Fehler offen |
| Repository-Basis | `94ed561b91d8f9958a69e08726d2a748181d3c79` (Pull Request 64) mit den Änderungen dieses PR |
| Umfang | SQL-Producer und tatsächlicher skalarer Decoder für AB, BA und AA |
| Abnahmegrenze | kein vollständiger Coordinator, RunRecord oder Incidentnachweis |

## Ausführung und Quellenbindung

Der additive Modus `--check-capture-projection` führt je Kontrollscope zwei
bestehende vollständige Lifecycles aus. Acht Phasen, die vier Parameterpaare
je Fenster sowie die regulären 180-/Cleanup-60-Sekunden-Budgets bleiben
erhalten. `lab.RequestResultCapture` enthält tatsächlich gezählte Zeilen
aus `#Actual`, gebunden an den jeweiligen Request. Die spätere Projektion
wird vor Cleanup über private begrenzte Pipes an den tatsächlichen Packager
und Decoder übergeben. Der Runner meldet feste Status- und Recordcounts;
im Fehlerfall ergänzt er bekannte Phasen und begrenzte numerische SQL-Fehlerdetails.
Er ruft keine prospektive Incidentbewertung auf.

Die neue lokale Prüfung verwendet ausschließlich neu erzeugte eigene Linux-
Docker-Developerinstanzen: höchstens eine gleichzeitig, vier CPU-Kerne,
8 GB Containerlimit, die reguläre Docker-Bridge wie in CI, keine veröffentlichten Ports und keine
Hostvolumes. Die Ressourcenlimits belegen keine vollständige Ressourcen-
attestation. Die bestätigenden Optionen `--confirm-disposable-instance` und
`--confirm-isolated-lab` werden ausschließlich für diese frischen Ziele gesetzt.
Passwörter bleiben in Prozessumgebungen; Rohoutput wird weder als Report
ausgegeben noch als Projektartefakt persistiert.

Der private Prüfaufruf entspricht je Major und Scope:

```text
python Tests/Runtime/run_dgn007_automated_setup.py --scope control-ab|control-ba|control-aa
  --check-capture-projection --target docker --container <eigene-neue-Instanz>
  --expected-major 15|16|17 --confirm-disposable-instance --confirm-isolated-lab
```

Die drei Kontrollgruppen laufen seriell. Vor und nach jeder Gruppe werden
alle 14 gebundenen SQL-/Manifestquellen, der Vertrag und die ausführenden
Pythonmodule gegen dieselben normalisierten SHA-256-Werte verglichen.
Nach jedem Lifecycle prüft der Runner die Datenbankabwesenheit unabhängig;
nach jeder Gruppe folgt zusätzlich eine Prüfung gegen `master` auf keinerlei
Benutzerdatenbanken. Der Containerabbau prüft ursprüngliche CID, eigenen Namen,
UUID-Label und Image-ID und entfernt nur diese eigene Instanz einschließlich
ihrer anonymen Volumes. Ein unabhängiger Agent prüft anschließend CID- und
Namensabwesenheit erneut. Fremde Ressourcen sind keine Testziele.

Die folgenden Hashes binden die ursprünglichen 18 erfolgreichen lokalen
Producer-Lifecycles vor Ergänzung der festen SQL-Guardkennungen. Die spätere
Diagnostikrevision erhält einen eigenen Freeze; diese Ergebnisse werden ihr
nicht nachträglich als tatsächlich ausgeführte Läufe zugeschrieben.

| Eingefrorene Quelle | SHA-256, UTF-8 mit LF |
|---|---|
| `21_Controlled_Query_Store_Windows.sql` | `bcc48a59b197024c0440481b0abc032b6571b1499d05124322fd784532b4a133` |
| `35_Control_Evidence.sql` | `6da79c2a6e368e90cb51c3108854cf293d5743522bd13f4c0084e6ffb0e21732` |
| Vertragsdatei | `d099a77b2fe2fcf79fdc472f50bd56b18bdb8bce70f400234c00e2b6f1a2e2da` |
| Runtime-Runner | `91d6b5f962d9fe047323013f4560fee66eda11b52043261822771351c50a7699` |
| Frame-Packager | `72064f93a15bda108e70a30827d0d2f3cfb9c64c5cd74978c6fb43b07248792b` |
| bestehender Decoder | `7a2191ee3a977ec9931a15254aa4b9b2459dafaac3869a187985e60e544a4301` |
| prospektiver Evaluator | `834bab973bf5cf921e682b4d695458158bbf13a1549d681e73ea61e1ef891881` |

Der semantische Vertragsdigest lautet
`46bb69a0e85e3f683bf2d41c84a1cc52284094e439bdbded6d96da9643eb7c44`,
der Quellenobjektdigest
`7cf61cd40f552e6909bc1c2474883b9bd2bfab2bea276fbbb069c4e1bca8fc07`.
Nur die zwei geänderten SQL-Hashes wurden in der unveränderten v1-Quellenliste
erneuert. Das ist eine konkrete Integritätsbindung dieser lokalen Prüfung;
die ergänzten Bodydigests allein attestieren weder Collectorherkunft noch
einen vollständigen Coordinatorfreeze. Ältere Runtime-Nachweise behalten
ihre historischen Commit-/Freeze-Bezüge.

## SQL-Darstellungsprobe

Eine zusätzliche eigene Session verwendet den tatsächlichen markierten
`CAPTURE_TIME_ROWS`-Block aus SQL35 mit ausschließlich auf temporäre Fixtures
ersetzten Datenquellen. Sie prüft UTC-Offsetgleichheit, genau einen 100-ns-Tick,
Epochwert null und den maximalen `datetime2(7)`-Wert. Beide tatsächlichen
Window-/Planformeln werden verwendet. Der tatsächliche Style-3-Ausdruck aus
SQL35 wird zusätzlich an sechs festen SQL-Floats auf Roundtrip und zwei
unterscheidbare Nachbarwerte geprüft. Die Session verändert weder eigene
Labtabellen noch Query-Store-Konfiguration.

Diese Probe belegt SQL-Darstellung. Die sechs Floatfixtures gelten nicht als
Decoder-Abnahme; der unveränderte v1-Decoder kann besonders kleine
Representationsexponenten absichtlich ablehnen. Der vollständige CaptureBody
wird getrennt in den regulären Kontrolllifecycles geprüft.

## Vorversuch und Cleanup

Der erste eigene 2019-Vorversuch scheiterte vor Probe und Lifecycle an der
240-Sekunden-Readinessgrenze: die authentifizierte `localhost`-Verbindung
lief im `--network none`-Namespace in einen Timeout. Auf derselben eigenen
Instanz bestand die separate IPv4-Loginprobe. Dieser Versuch zählt als
Infrastruktur-FAIL, ohne Producer-PASS. Container
`175f37a7f2d7afb4cb04d665c5f0f7fc2eccf6a5ad301e6718cde4a045792e1c`,
Name `sqlperf-dgn007-producer-15-b05786ee3f`, wurde nach Eigentumsprüfung
entfernt; CID und exakter Name sind unabhängig als abwesend bestätigt.
Ein zweiter neuer Vorversuch deaktivierte IPv6 ausschließlich im eigenen
Network Namespace über `net.ipv6.conf.all.disable_ipv6=1`; zusätzlich wurde
die IPv6-Loopbackzeile nur in dessen eigener `/etc/hosts` entfernt. Auch
dieser Vorversuch scheiterte vor Probe und Lifecycle am Readinesstimeout.
CID `7a34ec87d17f1af4fbf66d757faab3dca27174f5f285f2bb0137b5183ab9af70`,
Name `sqlperf-dgn007-producer-15-3bdc72fa48`, wurde regulär entfernt; CID und exakter Name sind unabhängig als abwesend bestätigt.
Die Ursache ist nicht abschließend bestimmt.

Ein dritter neuer Versuch mit regulärer CI-Bridge bestand die authentifizierte
Readiness, scheiterte aber in der zusätzlichen privaten SQL-Fixture. Der
`RowCount`-Alias im privaten Prüfquery wurde anschließend mit eckigen
Klammern quotiert; eingefrorener Projektcode blieb unverändert. CID
`aa4cc6605e6e9fde7a77e21169397da87520121457ff2266abcbd96ba0ce058c`, Name
`sqlperf-dgn007-producer-15-31e6aabe34`, wurde regulär entfernt; CID und exakter Name sind unabhängig als abwesend bestätigt. Der folgende
frische Bridge-Versuch bestand die korrigierte Darstellungsprobe. Auch der
dritte Vorversuch zählt nicht als erfolgreicher Producer-Lifecycle.

Projektproxy und SQL bleiben für alle Vorversuche unverändert.
Fremdinventurbewegungen sind keine eigenen
Cleanupaktionen und werden nicht als unveränderter Gesamtbestand behauptet.


## Abgeschnittene Producerübertragung und Wirekorrektur

Der vierte eigene Versuch bestand die SQL-Darstellungsprobe, aber AB-RUN1
endete als `FAIL_CONTRACT`. Die getrennte fünfte Diagnose bestätigte acht
SQL-Phasen `PASS/OK`, den äußeren Harness `PASS`, keine falsche Kanal-/
Phasenzuordnung und genau einen nur 970 Zeichen langen Frame. Der tatsächliche
Packager wies die Abweichung von deklarierter zu empfangener Payloadlänge ab.
Beide fehlgeschlagenen Producer-RUN1 bleiben Fehlversuche; Cleanup erfolgte.

| Versuch | eigene CID | eigener Name | Ergebnis |
|---|---|---|---|
| AB-RUN1 | `388990fe26022d9346c016c5ff8aa254bc3b39d28a8611b585fa8781c0f5ef12` | `sqlperf-dgn007-producer-15-49c10fd9cf` | `FAIL_CONTRACT`, CID/Name unabhängig abwesend |
| AB-RUN1-Diagnose | `4b91d13f8d4652d423274467b67b06a4863304d6e8fedc49ba57fff70311a826` | `sqlperf-dgn007-producer-15-646f098f0b` | `FAIL_CONTRACT`, CID/Name unabhängig abwesend |
| direkte Lengthprobe | `04bdb7fc452ed967f3dc58f936b54203e609b4258ad33dc4ce76206753500d9f` | `sqlperf-dgn007-producer-15-bf493dde39` | ausschließlich Darstellungsprobe, CID/Name unabhängig abwesend |

Diese Fehlversuche prüften die ursprüngliche 4000-Zeichen-Revision mit SQL35-
Hash `af36cb4a3a58437691c648aa6e4ed249b4a83d5e618c45a3f93170fa659d6554`
und Packagerhash `4fe360789ea7196698e525bc7a4f70fe60faef8ef525c8db07f4434736bc7260`.
Sie bestätigen die korrigierte Revision in der oberen Hashtabelle nicht.

Die direkte Lengthprobe transportierte 512, 768 und 900 Payloadzeichen
vollständig; 1024 und 4000 wurden jeweils auf 954 Zeichen nach ihrem
Fixtureheader gekürzt. Acht nachgestellte Leerzeichen blieben erhalten.
Dies belegt die empirische Kürzung in der konkreten Übertragungskette;
die verursachende Schicht wird nicht als nachgewiesen behauptet. Die reine
SQL-PRINT-Grenze von 8000 Zeichen garantiert keine ebenso große empfangene
Clientnachricht. Die anschließenden Proben über denselben Dockerproxy mit
`-r 1 -w 65535` bestanden auf allen drei Zielversionen mit denselben
Längen- und Leerzeichenergebnissen. Sie prüfen dessen tatsächlichen stderr-Pfad
separat; auch diese Proben sind keine Producer-Lifecycles.

| Proxypfadprobe | eigene CID | eigener Name | ProductVersion |
|---|---|---|---|
| 2019 | `2ee0021b588a68626a7ea44d02ab86d22befb8b556ec326f3d9f60631a65ef1e` | `sqlperf-dgn007-producer-15-11f750b0be` | `15.0.4480.2` |
| 2022 | `7e86a6e57b08695b51a95029994e6a1be30f73f2a878bb1306d735ff0a1e86f9` | `sqlperf-dgn007-producer-16-b3d82f2db1` | `16.0.4265.3` |
| 2025 | `00c2ec49e2e13a77ebe1723bfdc2d95670799bac3ac857027a6ca78043387087` | `sqlperf-dgn007-producer-17-37745c2b4d` | `17.0.4075.5` |

Alle drei Probe-CIDs und exakten Namen sind unabhängig als abwesend bestätigt.

Die minimale Wirekorrektur verwendet 512-Zeichen-Stücke bei unveränderten
32000 maximalen JSON-Zeichen. Damit entstehen höchstens 63 Frames; die
zusätzliche 64-Frame-Schutzgrenze erlaubt keinen 64. gültigen Frame. Der
bestehende Decoder, Body-v1 und die prospektive Methode bleiben unverändert.
Die strenge Längenprüfung bleibt erhalten; gekürzte Daten werden abgelehnt.

## Erste 512-Teilmatrix und begrenzte Fehlerdiagnose

Der erste 2019-Matrixversuch wurde nach zwei erfolgreichen AB-
Lifecycles und einem erfolgreichen BA-Lifecycle abgebrochen. BA-RUN2 endete
als `FAIL_EXECUTION`, Cleanup bestand. AA wurde nicht gestartet. Eigene CID
`43c7e9d37820aa79091b1b109e75c7a50e004085f348a2b21e00f5d19aac22d3`,
Name `sqlperf-dgn007-producer-15-cfc64ad532`, ist nach regulärem Abbau
unabhängig als abwesend bestätigt. Diese Teilmatrix gilt insgesamt als FAIL.

Zwei zusätzliche frische BA-Diagnoselifecycles auf eigener CID
`a1a91d3479015c4c84a5e62cad05098abd3ce53e7cb498cdf7c56ff866dc420d`,
Name `sqlperf-dgn007-producer-15-73d2657a72`, bestanden alle acht SQL-Phasen,
Harness, tatsächlichen Decoder und Cleanup. Jeweils sieben ungekürzte Frames
wurden akzeptiert; Datenbankabwesenheit und anschließend CID-/Namensabwesenheit
sind unabhängig bestätigt. Das reproduziert den früheren Fehler nicht und
beweist keine Ursache oder garantierte Verfügbarkeit. Die erfolglosen und
zusätzlichen Diagnoseversuche ersetzen keine vollständige neue Matrix.
Der Runtime-Runner dieser Versuche hatte SHA-256
`6e769a3daee5b44a0abe953d0a2ee4b2dd22741d5762e9ce90862abbf52d6ad9`.

Für folgende Fehlerfälle ist der Runner nur im Producer-Modus um eine
begrenzte Anzeige bekannter Phasen und numerischer SQL-Fehlerdetails ergänzt worden.
Kein Rohtext, Querytext oder Body wird ausgegeben. Outcome, Cleanup-/Timeout-
Priorität und Budgets bleiben unverändert; es gibt keine automatische
Wiederholung oder Umwertung eines Fehlers. Die folgende vollständige
18-Lifecycle-Matrix wurde nach neuem Codefreeze auf frischen Instanzen ausgeführt.

## Neue Matrix am abschließenden Codefreeze

Die neue vollständige Prüfung beginnt mit dem oben gebundenen Runner-
Hash `91d6b5f9…`; sie verwendet keine privaten Diagnosehooks. Auf SQL Server
2019/150 bestanden am 2026-10-07 zwischen etwa 01:43 und 01:56 UTC alle sechs
Lifecycles: AB zweimal, BA zweimal und AA zweimal. Jeder Capture enthielt
zwei Fenster, acht gemessene Requestrecords, eine Queryfamilie und zwei
Planrecords. Die beiden Planrecords gehören zu den zwei Fenstern; sie
bedeuten nicht zwei unterschiedliche Pläne. Die aktive Planunion betrug
bei AB und BA jeweils zwei, bei AA jeweils eins. Die echte SQL-
Darstellungsprobe, Decoderprüfung, alle Phasen und Cleanup bestanden.

Die eigene Instanz verwendete ProductVersion `15.0.4480.2`, Image-ID
`sha256:46f719fd3457d4e7e8e5845fe00c35c20e7bae7ff1e8b9fe595f2a81029f5ba8`,
CID `d553a8f67430700572bb804a41d9382a3e7fe178d234df8cae22470bc38f4175`
und Name `sqlperf-dgn007-producer-15-e4ffeed242`. Sie wurde nach
Eigentumsprüfung entfernt; CID und exakter Name sind unabhängig als
abwesend bestätigt. Diese konkrete Image-ID ist keine Behauptung über
den aktuell neuesten CU-Stand.

Auf SQL Server 2022/160 bestanden anschließend zwischen etwa 01:57 und
02:09 UTC dieselben sechs Lifecycles mit identischen Recordcounts und
Planuniongrößen je Scope. SQL-Darstellungsprobe, Decoder, Phasen, Cleanup,
sechs unabhängige Datenbankabwesenheitsprüfungen und drei zusätzliche
Leerheitsprüfungen nach den Gruppen bestanden. Alle gebundenen Quellen
blieben während der Prüfung unverändert. ProductVersion war `16.0.4265.3`,
Image-ID
`sha256:ba4c8329f48fb8f02e1416be6a930ebfd71268caee78aa985f3af4315e457c89`,
CID `7973d0e9535e66622e81b6c5af12ce7ee3813d674294b0c32937c6c3a1dc7a64`,
Name `sqlperf-dgn007-producer-16-5542a6a287`. Der Abbau nach Eigentumsprüfung
und die unabhängige CID-/Namensabwesenheitsprüfung bestanden.

Auf SQL Server 2025/170 bestanden anschließend zwischen etwa 02:09 und
02:21 UTC dieselben sechs Lifecycles, einschließlich echter SQL-
Darstellungsprobe, vollständiger Decoderübernahme, Phasen und Cleanup.
Recordcounts und Planuniongrößen je Scope entsprachen den anderen Versionen.
ProductVersion war `17.0.4075.5`, Image-ID
`sha256:4bab24f36c1ecd48e85f7d37df26e6bf301641d84c3fe652f9a0dcc947d512e1`,
CID `5e4b4375d998e21b440d7bd2dd4813801e1abfeb783de427355e60f449ece660`,
Name `sqlperf-dgn007-producer-17-f905f998a6`. Quellenbindung, sechs
Datenbankabwesenheitsprüfungen und drei Gruppen-Leerheitsprüfungen bestanden.
Die eigene Instanz wurde nach Eigentumsprüfung entfernt; CID und exakter
Name sind unabhängig als abwesend bestätigt.

| Version / Compatibility | AB | BA | AA | tatsächlicher Decoder | Datenbank-Cleanup |
|---|---|---|---|---|---|
| 2019 / 150 | 2 PASS | 2 PASS | 2 PASS | 6 PASS | 6 unabhängig PASS |
| 2022 / 160 | 2 PASS | 2 PASS | 2 PASS | 6 PASS | 6 unabhängig PASS |
| 2025 / 170 | 2 PASS | 2 PASS | 2 PASS | 6 PASS | 6 unabhängig PASS |

Die neue lokale Matrix enthält genau 18 erfolgreiche vollständige
Producer-Lifecycles. Frühere Fehlversuche, zusätzliche Diagnoselifecycles
und reine Darstellungsproben sind darin nicht enthalten. Alle 14 Quellen,
Vertrag und ausführenden Module blieben zwischen Freeze und Ende der
jeweiligen Kontrollgruppen unverändert. Je Version bestanden zusätzlich
drei Leerheitsprüfungen nach den Gruppen. Die ursprüngliche BA-RUN2-
Fehlerursache bleibt unbekannt; dieser begrenzte aktuelle Nachweis ist keine
Garantie für allgemeine Verfügbarkeit.

## Actions-Kandidat und offener Integrationsfehler

[Pull Request 65](https://github.com/gecompat/SQL_PerformanceSchulung/pull/65)
prüfte den Head `a621019036c53f91d32d5183278dd129b56b027b` gegen Base
`94ed561b91d8f9958a69e08726d2a748181d3c79`. Alle 22 Jobcheckouts wurden
auf den Integrationscommit `b1d871799352924df0a81e8efd813ffa426f3105`
bezogen geprüft; dessen vollständiger Baum entspricht dem Featurestand.
Die 14 Workflows endeten mit 21 erfolgreichen Jobs und einem Fehler.
Das ist keine erfolgreiche Gesamtvalidierung und erlaubt keinen Merge.

Im [DGN-007-Lauf 37561792652](https://github.com/gecompat/SQL_PerformanceSchulung/actions/runs/37561792652)
bestanden auf SQL Server 2019 und 2022 jeweils alle zwölf vorgesehenen
Datenmodell-, Fenster-, Profil- und Kontroll-Lifecycles. Die sechs
Producerübernahmen je Version bestanden ebenfalls. Auf SQL Server 2025
bestanden Datenmodell, Fenster, Profilvergleich und AB jeweils zweimal.
Der folgende erste BA-Lifecycle scheiterte in `CONTROL_EVIDENCE` mit
`FAIL_RESULT_CONTRACT`. Der äußere Runner meldete wegen des nicht nullwertigen
Child-Exitcodes `FAIL_EXECUTION`; seine begrenzten Diagnosen erhalten den
tatsächlichen SQL-Resultcode. Die bestehende PRINT-/RETURN-Verzweigung
lieferte keine SQL-Meldungsnummer oder Zeile. Welche Assertion scheiterte,
ist unbekannt. BA-RUN2, AA und die spätere Compatibility-Prüfung wurden
auf dieser Version nicht ausgeführt.

Alle 33 gestarteten DGN-007-Datenbank-Cleanups bestanden, einschließlich
unabhängiger Abwesenheitsprüfung. Die drei DGN-007-Container-Cleanup-Schritte
einschließlich expliziter CID-Abwesenheitsprüfung bestanden. Der statische
Ubuntu-Job führte alle 146 Testmethoden ohne SKIP erfolgreich aus.
Diese Ergebnisse beseitigen den fachlichen Fehler im 2025-BA-Lifecycle nicht.

CI verwendete für SQL Server 2025 den unveränderlichen Image-Digest
`sha256:2b5b581621126574f3d1f75e78d3eebe8d05aedb59ad0cfdf9aa42cb0634d726`.
Ein tatsächlicher CI-`ProductVersion`-Wert wurde nicht protokolliert und bleibt
unbekannt. Die erfolgreiche ursprüngliche lokale Matrix verwendete dagegen
die oben genannte lokale Docker-Image-ID `4bab24…` und `17.0.4075.5`.

## Private Gegenproben nach dem CI-Fehler

Zwei separat neu erzeugte eigene Instanzen führten je zwei BA-Lifecycles
mit einer privaten Diagnosekopie von SQL35 aus. Diese ergänzt ausschließlich
in den 17 bereits betretenen `FAIL_RESULT_CONTRACT`-Verzweigungen feste
Kennungen `G01` bis `G17`. Prädikate, RETURN, Last, Phasenreihenfolge, Flushes
und Budgets blieben erhalten. Die SQL35-Diagnosekopie hat den normalisierten
SHA-256 `0c55730a0b8a44e95460053843950ccab18a86f66f0869c41000356eede170e4`.
Sie ist ausdrücklich `NOT_CANONICAL_EVIDENCE` und gehört nicht zu den
18 ursprünglichen Producer-Lifecycles.

| Gegenprobe | tatsächliche ProductVersion | Imagebindung | Ergebnis |
|---|---|---|---|
| bisherige lokale 2025-Revision | `17.0.4075.5` | lokale Docker-Image-ID `sha256:4bab24f36c1ecd48e85f7d37df26e6bf301641d84c3fe652f9a0dcc947d512e1` | zwei BA PASS, kein Failuremarker |
| exakte CI-Image-Revision | `17.0.5005.3` | Registrymanifestdigest `sha256:2b5b581621126574f3d1f75e78d3eebe8d05aedb59ad0cfdf9aa42cb0634d726` | zwei BA PASS, kein Failuremarker |

Die eigenen CIDs
`8efd72fc0c214f26cb5b996a65634c744af71032bf68b35fa2cb361542ce9141`
und `2acf4f44aabcc041d8ffe83460c9e72d3ffe96a0c8d7ee2c7eee88ce51c7f9e9`
wurden nach Eigentumsprüfung entfernt. Ein unabhängiger Agent bestätigte
für beide CID und exakten Namen die Abwesenheit. Die kanonischen Quellen
blieben unverändert. Diese begrenzten Gegenproben reproduzierten den Fehler
nicht; sie beweisen weder seine Ursache noch seine Behebung. Die tatsächliche
Version der zweiten eigenen Instanz attestiert nicht den fehlenden
Versionswert des früheren CI-Containers.

Eine weitere einzige Gegenprobe führte auf einer dritten frischen eigenen
Instanz derselben CI-Revision die vollständige CI-Reihenfolge aus:
`Datenmodell ×2 → Fenster ×2 → Profilvergleich ×2 → AB ×2 → BA ×2 → AA ×2`.
Alle zwölf privaten Diagnose-Lifecycles bestanden, ebenso die sechs
Kontroll-Decoderübernahmen, zwölf Datenbankabwesenheitsprüfungen und sechs
zusätzlichen Gruppen-Leerheitsprüfungen. Kein Guardmarker wurde beobachtet.
Der Plan sah einen Stopp beim ersten FAIL vor; dieser trat nicht ein.
ProductVersion war `17.0.5005.3`, Registrymanifestdigest `2b5b5816…` wie oben.
Die kanonischen Quellen blieben vor und nach allen Gruppen unverändert;
SQL35 verwendete dieselbe private Marker-only-Kopie `0c55730a…`.
Die eigene CID
`0662782943d679ec7b3a40458c440f04a16d0601c84df354eea0f17926080af8`
mit Namen `sqlperf-dgn007-producer-17-629822294e` wurde nach Eigentumsprüfung
entfernt; ein unabhängiger Agent bestätigte CID und exakten Namen als abwesend.
Auch diese vollständige lokale Gegenprobe ist `NOT_CANONICAL_EVIDENCE` und
beweist keine Ursache oder Behebung des früheren CI-Fehlers.

## Produktive feste Guarddiagnostik

Die anschließende Revision ergänzt ausschließlich konstante ASCII-PRINTs
`DGN007_CONTROL_GUARD|G01` bis `G17` unmittelbar vor den bestehenden 17
`FAIL_RESULT_CONTRACT`-Summaries und RETURNs. Ein unabhängiger Review
bestätigt: Nach Entfernung genau dieser 17 PRINTs ist der vollständige
normalisierte SQL35-Text identisch mit dem ursprünglichen Head `a6210190…`.
Prädikate, Last, Flushes, Deadline, Summary, RETURN und Cleanup bleiben
unverändert. Im JSON wurde ausschließlich der SQL35-Quellenhash erneuert;
die übrigen 13 Quellen und der gesamte Methodenvertrag bleiben identisch.

Der Runner veröffentlicht eine feste Guard-ID nur aus dem tatsächlichen
`CONTROL_EVIDENCE:stderr`-Kanal einer fehlgeschlagenen Evidenzphase,
unmittelbar gebunden an `SQLPERF_SUMMARY|FAIL|FAIL_RESULT_CONTRACT`.
Unbekannte, doppelte, verschobene oder falsch gebundene Marker liefern
keinen Guardbericht. Die bestehenden Outputgrenzen und Fehlerprioritäten
bleiben erhalten. Die validierte Kanonisierung der statischen Prüfungen
entfernt ausschließlich diese 17 festen Literale; sämtliche bisherigen
Prädikat- und Common-Code-Prüfungen bleiben bestehen. Diese Revision
verbessert nur die Lokalisierung und ist keine behauptete Fehlerbehebung.

| Quelle der Diagnostikrevision | SHA-256, UTF-8 mit LF |
|---|---|
| SQL35 | `7d51b7bf3f444683ca2360595df24abf0214512c8794c50bcf5432f5fceae29f` |
| Vertragsdatei | `abc8135b0d648f21be597448d11d3693f57707c9801fb624670c281e422be20a` |
| Runtime-Runner | `6127b2107b096c27c45a104e4ddb9e7516308c38d26995d44a577d7a932918b7` |

Der neue semantische Vertragsdigest ist
`d10e97f14a30d89034c44ed35dcf9adf4173141599228c62595dad686d60575d`,
der Quellenobjektdigest
`7e26db9f85122f1c4eb43851231694090890c5869e484b4abd0e1295cbf35a43`.
SQL21, Frame-Packager, Transportdecoder und prospektiver Evaluator behalten
ihre oben genannten ursprünglichen Hashes. Die neue Runtime-/CI-Prüfung
wird getrennt zu diesem Freeze bewertet.

Auf den tatsächlichen Quellen dieser Diagnostikrevision wurden 149 lokale
Testmethoden ausgeführt: 148 PASS und derselbe Linux-spezifische SKIP unter
Windows. Alle sieben DGN-007-Validatoren und 15 weitere betroffene
Governance-/Projektvalidatoren bestanden. Die drei zusätzlichen Testmethoden
prüfen sämtliche Guard-IDs, falsche Bindungen und Literal-Kanonisierung;
die bestehenden Prädikat-, Decoder-, Cleanup- und Timeoutprüfungen bleiben
erhalten. Diese lokalen Ergebnisse attestieren kein neues CI-Ergebnis.

Die neue kanonische Diagnostikrevision bestand anschließend auf einer frischen
eigenen SQL-2025-Developerinstanz mit tatsächlicher ProductVersion
`17.0.5005.3` und dem exakten CI-Registrymanifestdigest `2b5b5816…` zweimal
vollständig BA. Der unveränderte tatsächliche Packager/Decoder übernahm je
zwei Fenster, acht Requests, eine Familie, zwei Planfensterrecords und zwei
Planunionrecords. Alle acht Phasen, zwei unabhängige Datenbankabwesenheits-
prüfungen und eine zusätzliche Gruppen-Leerheitsprüfung bestanden. Die
gesonderte reale SQL-Tick-/Style3-Probe bestand ebenfalls. Alle 14 Quellen,
der aktuelle Vertrag und die vier gebundenen Pythonmodule blieben vor und
nach der Gruppe unverändert. Die eigene CID
`6cb3cec515e329fef1fefd7d17dcc4aa9d22922f5dfb36a22778ee9a36db0e0a`
mit Namen `sqlperf-dgn007-producer-17-2ef635167e` wurde nach Eigentumsprüfung
entfernt; CID und exakter Name sind unabhängig als abwesend bestätigt.
Diese zwei aktuellen BA-Lifecycles sind ein neuer begrenzter Entwicklungs-
nachweis zu dieser Revision. Sie werden weder in die ursprüngliche
18-Matrix noch in die zwölf privaten Diagnoselifecycles hineingerechnet.
Ein erfolgreicher aktueller CI-Kandidat steht weiterhin aus; der frühere
CI-Fehler ist dadurch nicht als behoben erklärt.

## Verbleibende Abnahmegrenzen

Lokale Ergebnisse und spätere Actions-Ergebnisse werden getrennt
bewertet. Coordinator-, Ressourcen-, Reihenfolge- und vollständige
Lifecycleattestation sowie Incident-, Ursachen-, Mitigations-, Capstone-
und Szenariofreigabe bleiben offen.
