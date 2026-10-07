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
Zum Zeitpunkt dieser Gegenprobe stand ein erfolgreicher aktueller CI-Kandidat
noch aus; die Gegenprobe erklärt den früheren CI-Fehler nicht als behoben.

## Zweiter Actions-Kandidat: Fensterfehler auf SQL Server 2022

Die produktive Guarddiagnostik wurde im Head
`23efba041cf05c027133bcc9b9e9672fa309eda5` gegen dieselbe Base `94ed561b…`
im Integrationscommit `25046954b9ef6e0ad061902e8f9c271acf24fbfc`
geprüft. Dessen vollständiger Tree `8d957ca2781402b0217504c2f251848effbb67bf`
entspricht dem Featuretree. Der statische Linux-Job führte alle 149 Methoden
ohne SKIP erfolgreich aus.

Im [DGN-007-Lauf 37566959578](https://github.com/gecompat/SQL_PerformanceSchulung/actions/runs/37566959578)
scheiterte SQL Server 2022 im ersten `QUERY_STORE_WINDOWS`-Lifecycle mit
äußerem `FAIL_EXECUTION`, nach zwei erfolgreichen Datenmodell-Lifecycles.
Der Fensterschritt lief von 03:30:08 bis 03:32:11 UTC. Diese 123 Sekunden
beweisen weder Timeout noch eine konkrete verletzte Assertion. Der normale
Fensteraufruf liefert keinen privaten Raw-Phase-Output; sein tatsächlicher
Child-Phasen-/SQL-Code wurde vom Runner nicht diagnostisch weitergegeben.
Es liegen keine SQL-Guard-, Meldungsnummer-, Zeilen- oder Timeoutmarker vor.
Die genaue Ursache bleibt unbekannt; der Producer wurde auf dieser Version
in diesem Lauf noch nicht erreicht.

Alle drei begonnenen Datenbank-Lifecycles endeten mit erfolgreicher
unabhängiger Abwesenheitsprüfung. Der eigene 2022-Container wurde mit
Eigentumsprüfung entfernt; der erfolgreiche Cleanup-Schritt enthält
zusätzlich die explizite CID-Abwesenheitsprüfung. CI verwendete den
Registrymanifestdigest
`sha256:4402d880dd4c34bfa7d8705e56a86cd6c88da80a1f6bbbe741f999e76264a090`.
Eine tatsächlich protokollierte CI-ProductVersion ist nicht belegt.
Die 2019-/2025-Jobs wurden bis zum regulären Ende erhalten. Beide bestanden
je zwölf Lifecycles und sechs tatsächliche Decoder-Captures; 2025 zusätzlich
acht Compatibility-Gegenproben. Über alle drei DGN-007-Jobs bestanden alle
27 begonnenen Datenbankabwesenheitsprüfungen und die drei expliziten
own-CID-Abwesenheitsprüfungen. Alle neun SQL-Remove-Schritte waren SUCCESS.
Die unabhängige Abschlussprüfung bestätigte 14 abgeschlossene Workflows
und 22 Jobs: 13 Workflows und 21 Jobs SUCCESS, ausschließlich dieser
2022-Fensterjob FAILURE. Alle 22 Checkouts prüften exakt `25046954…`,
alle Checks waren an den exakten Head und Actions-App `15368` gebunden.
Die erfolgreichen erforderlichen Checks erlauben keinen Bypass dieses
fachlich ungeklärten Fehlers. Dieser zweite fehlgeschlagene
Integrationskandidat wird weder als Infrastrukturfehler noch als
vollständiger erfolgreicher Producer-Nachweis umgedeutet.

## Sichere Phasendiagnostik und getrennte 2022-Gegenprobe

Die folgende Revision ergänzt `--check-phase-diagnostics` für genau die sechs
bestehenden Scopeverträge. Sie verwendet denselben privaten, begrenzten
Capture-Reader mit 262144 Bytes UTF-8-Textausgabe über beide Pipes,
8192 Zeichen pro Zeile und 260 Sekunden äußerem Schutz. Unter Windows
normalisiert der Textreader CRLF zu LF.
Bei Fehlern werden erst nach Cleanup bekannte Phasen-/Summarycodes sowie
konkret stderr-gebundene numerische SQL-Meldungen ausgegeben. Guardkennungen
bleiben ausschließlich an fehlgeschlagene Kontroll-Evidenz gebunden.
Die Capture-Option bleibt auch bei kombinierter Optionswahl Controls-only.
Eine Captureoption auf Nicht-Control-Scopes wird auch bei gleichzeitig
gesetzter Phasendiagnostik vor Verbindung abgewiesen.
Die vorhandenen drei Datenmodell-/Fenster-/Profilaufrufe der CI erhalten
lediglich das neue Flag. SQL, Manifeste, Capturevertrag, Methodik, Last,
Lifecycles und reguläre Budgets bleiben unverändert. Die Diagnose ist keine
behauptete Fehlerbehebung.

Der Runner-Freeze vom 2026-10-07 03:41:42 UTC bindet den LF-Hash
`bedfa3344bfab19b20730f2726872c8f5143bc7aa3f494067f7d1b0dc1b5a70e`.
Alle 14 Quellen entsprechen weiterhin dem aktuellen Vertrag `abc8135b…`;
Packager, Transportdecoder und prospektiver Evaluator behalten ihre oben
gebundenen Hashes. Ein unabhängiger Code-Review ergab keine Befunde.
Die sieben DGN-007-Suites führten tatsächlich 156 Methoden aus: 155 PASS,
ein Linux-spezifischer SKIP unter Windows. Die sieben zusätzlichen
Runnerfixtures prüfen insbesondere Scope-/Kanalbindung, Optionsgrenzen,
Timeoutpriorität und Ausgabe nach Cleanup. Alle 22 betroffenen lokalen
Governance-/Projektvalidatoren bestanden, darunter die sieben DGN-007-
Verträge, Registry mit 219 Artefakten, Foundationintegrität und Privacy
mit 872 Dateien. Die 65 lokalen Markdownlinks der sieben geänderten
Dokumente und `git diff --check` waren ebenfalls erfolgreich.

Diese Quellen bestanden anschließend auf genau einer neuen eigenen
SQL-2022-Developerinstanz mit tatsächlicher ProductVersion `16.0.4295.3`
und dem exakten CI-Registrymanifestdigest `sha256:4402d880…` in der Reihenfolge
zweimal Datenmodell und zweimal Query-Store-Fenster. Alle vier Lifecycles,
vier unabhängige Datenbankabwesenheitsprüfungen, zwei zusätzliche
Gruppen-Leerheitsprüfungen und die reale SQL-Tick-/Style3-Probe bestanden.
Alle 14 Quellen sowie die vier Pythonmodule und der Vertrag blieben während
der Ausführung unverändert. Die eigene CID
`e7ac3f167b604fc980c8af182572e31a3e104660ae787180c4eeead960f94d1f`
mit exaktem Namen `sqlperf-dgn007-producer-16-50fc08e26f` wurde nach
Eigentumsprüfung entfernt; CID und Name sind unabhängig abwesend bestätigt.

Diese vier aktuellen Lifecycles sind ausschließlich ein begrenzter Nachweis
für die Phasendiagnostikrevision. Sie werden weder zur ursprünglichen
18-Kontrollmatrix noch zur späteren BA-Prüfung oder zu privaten Diagnoseläufen
addiert. Der zweite CI-Fensterfehler wurde nicht reproduziert; seine Ursache
bleibt offen. Zum Zeitpunkt dieser Gegenprobe standen erfolgreiche Actions
am neuen exakten Head und Base vor Integration noch aus.

## Erfolgreiche Integrationsabnahme und Übernahme

Der folgende aktuelle Kandidat wurde vor Merge unabhängig vollständig
abgenommen: PR65-Head `20a867e2f0ce9ffa4430e138f76479904145ba48`
gegen Base `94ed561b91d8f9958a69e08726d2a748181d3c79`,
Integrationscommit `df78cb0fb83f6b3992d1a8c2f6b55bf8b2f83598` mit
exakt diesen beiden Parents. Integrations- und Featuretree sind vollständig
`3949e7a1013db8b1d98903581d6e87a0ee992412`. Alle 14 Workflows und
22 Jobs/Checks endeten SUCCESS; alle Checkouts binden an denselben
Integrationscommit und alle Checks an Head und Actions-App `15368`.
Die erforderlichen [Registry-](https://github.com/gecompat/SQL_PerformanceSchulung/actions/runs/37568945174)
und [Governance-Prüfungen](https://github.com/gecompat/SQL_PerformanceSchulung/actions/runs/37568945226)
waren bei unverändertem, streng aktuellem Base-Gate erfolgreich.

Der [DGN-007-Lauf 37568945100](https://github.com/gecompat/SQL_PerformanceSchulung/actions/runs/37568945100)
führte alle 156 Linux-Testmethoden ohne SKIP aus. Auf jeder Zielversion
15/150, 16/160 und 17/170 bestanden zwölf Lifecycles in der bestehenden
Reihenfolge Datenmodell, Fenster, Profil, AB, BA, AA mit je zwei Runs.
Je Version bestanden sechs vollständige Producer-Decoder-Captures,
zwölf unabhängige Datenbankabwesenheitsprüfungen und sechs Scope-Summaries
mit `runs=2`. Alle Bodies enthalten zwei Fenster, acht Requests, eine
Familie und zwei Planfensterrecords; die aktive Union enthält zwei Records
unter AB/BA und einen unter AA. Auf 2025 bestanden zusätzlich die acht
Compatibility-Gegenproben. Alle neun SQL-Remove-Schritte waren SUCCESS;
die drei DGN-007-Cleanups bestätigten Eigentum über Name, Labels und CID
sowie die anschließende explizite CID-Abwesenheit. Diese vollständige neue
CI-Matrix umfasst 36 Lifecycles und 18 Producer-Captures; sie wird separat
zu den früheren lokalen und fehlgeschlagenen Kandidaten bewertet.

Root prüfte unmittelbar vor Merge erneut den unveränderten Head, Base,
alle 22 erfolgreichen Checks und `MERGEABLE/CLEAN`. [Pull Request 65](https://github.com/gecompat/SQL_PerformanceSchulung/pull/65)
wurde regulär als Squash `da7b0eb7c3bfb5238141c34520b237228ca77085`
am 2026-10-07 um 04:18:12 UTC integriert. Eine unabhängige Übernahmeprüfung
bestätigte serverseitig und lokal genau einen Parent `94ed561b…`, den
vollständigen gleichen Tree `3949e7a…`, leeren Gesamtdiff zum Featurehead,
keine zusätzlichen Branchcommits und den einzigen sauberen Worktree.
`main` wurde mit `origin/main` synchronisiert. Erst danach wurde der eigene
Branch `codex/dgn007-sql-capture-producer` remote mit einer an den geprüften
Head gebundenen Löschungs-Lease und lokal entfernt. Anschließend gab es
lokal und remote ausschließlich `main` am bestätigten Squash.

Die historischen Fehler an `a6210190…` und `23efba04…` bleiben tatsächliche
fehlgeschlagene Kandidaten mit unbekannter genauer Ursache. Die neue
vollständige erfolgreiche Abnahme hebt ihre Befunde nicht auf und behauptet
keine Behebung durch Diagnostik. Die automatisch gestartete Main-Push-CI
am Squash ist ein getrennter, zum Zeitpunkt dieser Quittung noch laufender
Nachweis; ihre Ergebnisse werden nicht vorweggenommen.

Der damals geplante Folgeschnitt war die interne verlustfreie Rückgabe von Body und
tatsächlich geprüften Phasen erst nach erfolgreichem Lifecycle, Harness-
Cleanup und erster unabhängiger Datenbankabwesenheit. Recovery macht keinen
Fehler zum erfolgreichen Capture-Beleg. Counts, CLI und Fehlerprioritäten
bleiben erhalten. Daraus folgt noch kein RunRecord, Ressourcen-/Budget-/
Reihenfolgenachweis, keine Runtimeattestation und keine Incidentbewertung.

## Getrennter Main-Push-Nachweis: tatsächlicher G13-Fehler

Die automatisch gestartete Push-CI prüfte den unveränderten Squash
`da7b0eb7c3bfb5238141c34520b237228ca77085`. Die unabhängige Abschlussprüfung
bestätigte alle 13 abgeschlossenen Workflows und 48 Jobs: 12 Workflows und
47 Jobs SUCCESS, ausschließlich der 2022-Job aus
[DGN-007-Lauf 37570814577](https://github.com/gecompat/SQL_PerformanceSchulung/actions/runs/37570814577)
FAILURE. Alle 48 Checkouts binden exakt an diesen Main-Commit, alle Checks
an den exakten Head und Actions-App `15368`. PR66 wurde separat mit sieben
erfolgreichen Checks am exakten Head/Base integriert; dessen Änderungen
betreffen ausschließlich Dokumentation.

SQL Server 2022 bestand neun Lifecycles, einschließlich BA RUN_1; BA RUN_2
scheiterte im Schritt von 04:31:02 bis 04:35:02 UTC mit äußerem
`FAIL_EXECUTION`. Die feste, kanalgebundene Diagnose lautet
`CONTROL_EVIDENCE / FAIL_RESULT_CONTRACT / G13`. Genau dieser Guard prüft
`FirstExecutionTime < ExecutionStarted OR LastExecutionTime > ExecutionFinished`
für gespeicherte IncidentProfile-Zeilen. Es fehlen skalare Zeitwerte und
SQL-Meldungsnummern; die Guard-ID belegt weder die verletzte Seite noch
Ursache, Größe oder eine zulässige Toleranz des Abstandes.

Alle zehn begonnenen 2022-Lifecycles bestanden ihre unabhängige
Datenbankabwesenheitsprüfung. AA wurde nach dem Fehler nicht ausgeführt.
Der tatsächliche CI-Pulldigest ist
`sha256:4402d880dd4c34bfa7d8705e56a86cd6c88da80a1f6bbbe741f999e76264a090`.
Der eigene Container `sqlperf-dgn007-auto-16-37570814577-1` wurde nach
Name-/Scope-/Ownerprüfung an die CID-Datei gebunden entfernt; die explizite
leere CID-Filterliste wurde erfolgreich geprüft. Der konkrete CID-Wert und
eine tatsächliche CI-ProductVersion sind nicht geloggt und werden nicht
behauptet.

2019 und 2025 liefen bis zum regulären Ende: je zwölf Lifecycles, sechs
Decoder-Captures, zwölf unabhängige Datenbankabwesenheitsprüfungen und
sechs Scope-Summaries PASS; 2025 zusätzlich acht Compatibility-Gegenproben.
Alle neun SQL-Remove-Schritte waren SUCCESS; DGN-007 prüfte für alle drei
Instanzen die explizite own-CID-Abwesenheit. Der Linux-Job führte alle 156
Methoden ohne SKIP erfolgreich aus. W-COV bestand alle 28 Jobs mit 54
äußeren Runs (48 PASS, sechs zulässige WARN); seine 27 Cleanup-Kommandos
waren SUCCESS, besitzen aber die bestehende `|| true`-Grenze und keinen
zusätzlichen unabhängigen CID-Abwesenheitsbeleg.

Dieser neue Runtime-Vertragsfehler verhindert eine vollständige Main-CI-
Freigabe. Er wird nicht als Infrastrukturfehler klassifiziert oder umgangen.
Die erfolgreiche exakte PR65-Integrationsabnahme bleibt ein getrennter
historischer Beleg. Die beiden früheren CI-Fehler behalten ihre unbekannte
Ursache; aus G13 dieses neuen Laufs wird keine rückwirkende Diagnose abgeleitet.

Der statische Review fand eine prüfbare Hypothese: SQL21 sowie SQL30/35
aggregieren MIN/ MAX über alle regulären Statistikzeilen, bevor
`HAVING SUM(count_executions)>0` positive Gruppen auswählt. Einzelne
Nullzählzeilen sind damit nicht aus den Extrema ausgeschlossen. Dass solche
Zeilen den tatsächlichen G13 verursacht haben, ist nicht belegt.
[Microsoft Learn](https://learn.microsoft.com/en-us/sql/relational-databases/system-catalog-views/sys-query-store-runtime-stats-transact-sql?view=sql-server-ver16)
beschreibt First/Last als Ausführungsendzeiten und mögliche Disk-/In-Memory-
Mehrfachzeilen mit notwendiger Aggregation (abgerufen 2026-10-07). Für
Zeitwerte bei `count_executions=0` nennt die Quelle keine Sondersemantik.

Die getrennte [SYSUTCDATETIME-Dokumentation](https://learn.microsoft.com/en-us/sql/t-sql/functions/sysutcdatetime-transact-sql?view=sql-server-ver16)
unterscheidet sieben Nachkommastellen beziehungsweise die 100-ns-Präzision
der genannten Windows-API von hardware-/Windowsabhängiger Genauigkeit
(abgerufen 2026-10-07). Daraus folgt keine tatsächliche Query-Store-Auflösung
oder Linux-Implementierung. In den geprüften Primärquellen ist keine
entsprechende gemeinsame Clock oder tickgenaue Ordnung gegenüber unmittelbar
gemessenen Requestgrenzen zugesichert. Ein gespeicherter Tickabstand darf
deshalb nicht als universelle Millisekundentoleranz oder Ursachenbeweis
umgedeutet werden.

Für die folgende private Untersuchung wurde eine skalare Probe ausschließlich
im bereits verletzten G13-Zweig gewählt. Sie trennt gespeichertes Profil und früheren Live-Snapshot von
einer einzigen späteren, exakt auf dieselben Query-/Parent-/Plan-/Intervall-
Keys begrenzten Query-Store-Sicht. Counts, UTC-100-ns-Ticks und signierte
Grenzabstände bleiben präzise; feste Caps kennzeichnen Overflow ausdrücklich
als unvollständige Stichprobe. Keine Querytexte, Plan-XML oder Payload-
Persistenz, keine zusätzlichen Suchausführungen, Flushes oder Waits; kein
Prädikat-, Budget- oder Toleranzfix. Private Kopie und Main-Runner werden
separat gebunden, kanonische Quellen bleiben unverändert. Die lokale
vorbereitete interne Capture-API bleibt ungepusht; ihre Freigabe/Integration
ist zunächst zurückgestellt. Eine Probe ist noch kein Ursachen- oder
Behebungsnachweis.

## Private G13-Probe: fehlgeschlagener synthetischer Vorcheck

Der erste private Vorcheck begann am 2026-10-07 nach dem Freeze von
04:53:34 UTC auf einer neuen eigenen SQL-2022-Developerinstanz
`16.0.4295.3` mit CI-Pullref `sha256:4402d880…`. Ref und lokale Inspect-ID
wurden vor Erzeugung separat aufgelöst; auf dieser Plattform stimmen sie
überein. Der ursprüngliche Tick-/Style3-Vorcheck bestand. Die zusätzliche
rein temporäre synthetische G13-Zweigfixture scheiterte dann mit drei
`Msg 156 / Level 15 / State 1`, vor jedem DGN-007-Lifecycle.

Der private Driver `356dad2535d231965779c475270237cea840e4455678b124a04c8d2f06e8b90d`
erzeugte die undelimitierte temporäre Spalte `LineNo`. Microsoft führt
[`LINENO` als reserviertes Schlüsselwort](https://learn.microsoft.com/en-us/sql/t-sql/language-elements/reserved-keywords-transact-sql?view=sql-server-ver16)
(abgerufen 2026-10-07); dies ist ein konkreter Syntaxdefekt der privaten
Probe, kein Beleg zur Ursache des tatsächlichen Main-G13. Die folgende
private Korrektur benennt nur diese Spalte um. Ein skalarer Subquery im
END-VALUES-Ausdruck wird vorsorglich in eine lokale Countvariable gezogen;
ein dadurch verursachter SQL-Fehler ist in diesem Versuch nicht belegt.
Guards, Last, kanonische Quellen und Budgets bleiben unverändert.

Die eigene CID
`8b86df2095a23e9badc16ac568bd575acd496ee1f19b7d92e373cc3f61a64154`
mit Name `sqlperf-dgn007-producer-16-26777b96c9` wurde nach Eigentumsprüfung
entfernt. Ein unabhängiger Agent prüfte anschließend ausschließlich diese
exakte CID und den exakten Namen: beide Abfragen Exit 0 und null Treffer.
Der Versuch ist ausdrücklich fehlgeschlagene private Validierung, keine
Kontrollcapture-, Runtime- oder Ursachenabnahme. Kein Rawoutput wurde
persistiert. Ein weiterer Versuch benötigt zuerst den neu geprüften
privaten Probe-Code und einen neuen Freeze.

Der zweite frische Vorcheck nach der privaten Syntaxkorrektur verwendete
Driver `d331fe30ac27a5cde9b8e79be7f55421406a13ebebf239e570c609e593238bf6`
und Freeze 04:56:57 UTC. Der SQL-Aufruf endete ohne Meldungsnummern mit
Exit 0; die Parent-Assertion zum exakt achtzeiligen Output scheiterte
vor jedem Lifecycle. Die CID
`37f6a3d9fa58f65d7b044437b476ce2b00156870f3ccd870ba32fc552e075f9f`
mit Name `sqlperf-dgn007-producer-16-d499c41762` wurde ownergebunden entfernt;
exakte CID und Name sind durch getrennte read-only Abfragen unabhängig
abwesend bestätigt. Dieser Versuch ist ebenfalls keine Runtimeabnahme.

Der anschließend unabhängig gelesene Parentwrapper
`e0fb1ed0c7a0d1149dc3c06c6b89d398b53c1212fc2e8b05ddfbab9a17924e21`
erlaubt nur den exakt bekannten englischen NULL-Aggregatwarntext als
höchstens zwei zusätzliche Zeilen. Acht gültige vollständige Probe-Records,
alle bisherigen Parser-/Tickasserts, null unbekannte Zeilen und null
`PROBE_ERROR` bleiben erforderlich. Der Driver und SQL bleiben unverändert.
Ein neuer Freeze vom 04:59:38 UTC bindet alle 14 kanonischen Quellen, den
Vertrag, vier Pythonmodule und beide privaten Helper: insgesamt 21 Dateien.
Auf der dritten neuen eigenen Instanz `16.0.4295.3` mit Ref/Inspect-ID
`sha256:4402d880…` bestand die tatsächliche synthetische T-SQL-Vorprüfung:
neun Ausgabezeilen, acht Probe-Records, genau eine bekannte NULL-Warnung,
kein Probe- oder unbekannter Output. Die temporäre Fixture bestätigt exakt
`First−Start=-1` und `Last−Finish=-5` UTC-100-ns-Ticks bei einer Gruppe und
null Raw-QS-Zeilen. Der dritte Vorcheck belegt die zusätzliche Warnzeile als konkrete
Verletzung der bisherigen Achtzeilenannahme; der Output des zweiten
Vorchecks wurde nicht vollständig beobachtet. Diese synthetische Probe beweist weder G13-Reproduktion
noch dessen Ursache oder Behebung. Der folgende tatsächliche CI-Präfixlauf
und sein Cleanup werden separat bewertet.

## Getrennte private CI-Präfixgegenprobe ohne G13-Reproduktion

Die dritte neue eigene Instanz führte nach dem erfolgreichen synthetischen
Vorcheck die CI-Reihenfolge bis zur fehlerhaften Stelle aus: Datenmodell,
Query-Store-Fenster, Profilvergleich, AB und BA je zwei vollständige
Lifecycles. Alle zehn Lifecycles, vier tatsächliche Kontroll-Decoder-Captures,
zehn erste unabhängige Datenbankabwesenheitsprüfungen und fünf zusätzliche
Gruppen-Leerheitsprüfungen bestanden. Je Kontrollbody: zwei Fenster, acht
Requests, eine Familie, zwei Planfensterrecords und zwei Unionrecords.
Keine G13-Verletzung und keine echten G13-Skalarrecords wurden beobachtet.
AA, vollständige CI-Matrix und prospektive Incidentbewertung waren nicht
Teil dieser begrenzten Untersuchung.

Der Main-Runner bleibt exakt der gepinnte Blob `bedfa3344…` aus `a0bc753…`.
Der private Driver `d331fe30…` erzeugt SQL35-Kopie
`5fd30b819c0f4ba0e64f02419fdda8b166016108c34568288fd674772db41d39`;
die exakte Entfernung des markierten Reporters ergibt den ganzen
kanonischen SQL35. Der Reporter läuft nur im bereits verletzten G13-Zweig;
dieser wurde hier nicht erreicht. Auch durch die neu kompilierte private
Kopie ändern sich keine Prädikate, Last, Flushes, Waits oder Budgets.
Alle 21 vorab gebundenen Dateien blieben während jeder Gruppe und im
abschließenden Freezevergleich um 05:17:01 UTC unverändert: 14 kanonische
SQL-/Manifestquellen, der Vertrag, vier Pythonmodule und beide privaten
Helper. Private Ergebnisse sind ausdrücklich `NOT_CANONICAL_EVIDENCE`;
die vorbereitete interne API war weder Runner noch Gegenstand dieses Laufs.

Die eigene CID
`5fd4a7891fe0fc97a2c3a6eac92f93ed6f2881e9c5c5b75b82ad09c625a2a88e`
mit Name `sqlperf-dgn007-producer-16-e0db740562` wurde nach exakter
Name-/Scope-/Owner-/Imageprüfung mit `rm --force --volumes` entfernt.
Parent und unabhängiger Agent bestätigten die Abwesenheit; der Agent
prüfte ausschließlich exakte CID und exakten Namen, jeweils Exit 0 und
null Treffer. Alle drei ausschließlich für diese Untersuchung erzeugten
Instanzen sind somit unabhängig als abwesend bestätigt.

Die Ursache des Main-G13 bleibt offen. Ein ausbleibender Fehler auf dem
lokalen Host belegt keine Behebung oder Main-CI-Freigabe. Nächster kleiner
Schnitt ist der vorab unabhängig als zulässig geprüfte kanonische
G13-Grenzabstandsbericht: nur gespeicherte verletzte Gruppen, maximal acht,
präzise UTC-Ticks/Abstände, feste Ausgabegrenzen und strenge Bindung an
den tatsächlichen Failure-/stderr-/Guard-/Summary-Satz. Ausgabe nach
Cleanup, unveränderte Guardlogik, Deadlines und Fehlerprioritäten.
Neue Quellenbindung, synthetische SQL-/Parserfixtures und reguläre CI
am exakten neuen Head/Base sind erforderlich. Kein neuer QS-Snapshot,
kein Toleranzfix, keine identische Wiederholung der privaten Probe.

## Integration des getrennten G13-Untersuchungsberichts

[Pull Request 67](https://github.com/gecompat/SQL_PerformanceSchulung/pull/67)
integrierte ausschließlich den Befund, die privaten Gegenproben und den
folgenden Diagnoseplan. Head `d2531b04816321ecbf6f747ccf26bb4fdd8d9754`
gegen Base `a0bc753d4c1fe492ba3c875bdefea5c00d8235b4` bestand sieben
Workflows, sieben Jobs und sieben Checks. Alle Checkouts verwendeten den
Integrationscommit `7282ffc69d0f2f4a6abccc528e65dddbb9a1e36b` mit genau
diesen Parents; Required Checks und Actions-App `15368` wurden unabhängig
geprüft. Der Squash `12b130f0df1f963a9075430745e406e8e2a38494` wurde am
2026-10-07 um 05:24:24 UTC gemergt. Er besitzt genau die Base als Parent
und denselben vollständigen Tree `fee07a99da66f3618e5c700034815fec429c6529`
wie der Featurehead. Gesamtdiff, zusätzliche Branchcommits und Worktree-
Belegung wurden unabhängig geprüft. Nach Main-Synchronisierung wurde
`codex/dgn007-g13-investigation` remote mit exakter Head-Lease und lokal
entfernt. Die fünf ausgelösten Main-Push-Workflows dieses reinen
Dokumentationssquashes bestanden ebenfalls; sie prüfen keine neue SQL-Revision.

Der getrennte lokale Branch `codex/dgn007-internal-capture-receipt` enthält
weiterhin den ungemergten API-Entwurf `83f08fb71446445e70fb6227e442ed7109637de6`.
Er wurde nicht gepusht und bleibt bis zur G13-Klärung erhalten. Aus der
Dokumentationsintegration folgt keine Behebung des Main-Runtimefehlers.

## Kanonischer gespeicherter G13-Grenzabstandsbericht

Der getrennte Diagnose-Schnitt basiert auf `12b130f…`. SQL35 ergänzt
ausschließlich den bereits verletzten G13-Zweig. Ein deterministisch
geordnetes `TOP(9)` liest gespeicherte IncidentProfile-/IncidentState-Gruppen:
höchstens acht gültige Gruppen werden vollständig berichtet, neun ergeben
ausdrücklich `OVERFLOW`. Es gibt keine weitere Query-Store-Sicht, Suche,
Flush- oder Warteoperation. Keys, positive Ausführungszahlen, genaue
UTC-100-ns-Ticks für Start/Finish/First/Last und die signierten Abstände
First−Start sowie Last−Finish bleiben skalare Diagnosewerte. Jede tatsächliche
Reporter-Message ist ASCII und höchstens 512 Zeichen lang. Ungültige Quellen
oder Diagnosefehler liefern `INSUFFICIENT`; der ursprüngliche G13-
Guard, seine angrenzende FAIL-Summary und RETURN bleiben erhalten.

Der Runner akzeptiert diese Records nur für unveränderte bekannte
Kontrollverträge, tatsächliches `CONTROL_EVIDENCE:stderr`, genau eine
fehlgeschlagene Evidenzphase und den eindeutigen angrenzenden G13-/Summary-
Abschluss. Anzahl, Reihenfolge, Keys, Counts, UTC-Bounds und signierte
Differenzen werden vollständig geprüft. Ausgabe erfolgt erst nach der
bestehenden unabhängigen Cleanup-Prüfung. Der vollständige Report erhält
atomar Platz innerhalb des unveränderten 24-Zeilen-Diagnoselimits;
strukturierte Guard-/Phasenstatus haben Vorrang vor optionalen SQL-
Meldungszahlen. Fehlende, gekürzte oder ungültige Reports werden niemals
als vollständige Gruppenmenge ausgegeben. Outcomes, Timeouts, Cleanup-
Prioritäten, Last und Budgets ändern sich nicht.

Zwei Reviewbefunde wurden vor der Runtimeprüfung korrigiert: Der neue
Parser erlaubt entsprechend dem vorhandenen G02-Vertrag gleiche
Requestgrenzen; er verschärft sie nicht auf strikt positive Zeitdauer.
Eine Fullcallerfixture mit 30 gebundenen Meldungszeilen und acht Gruppen
belegt die atomare Ausgabe aller neun Reportzeilen einschließlich Header,
zusätzlich Guard-/Phasenstatus, bei genau 24 gesamten Diagnosezeilen.

Die Quellenrevision ändert ausschließlich SQL35 innerhalb der vorhandenen
14 SQL-/Manifestquellen. Der streng gebundene Reporterblock
`148ce779f3ca9ebdd9644e9b180ad26d88fa810f757f25dad4ea40d316b0a064`
wird nur an der exakten G13-Position akzeptiert. Seine Entfernung ergibt
die gesamte vorherige SQL35-Datei mit LF-SHA `7d51b7bf…`, unabhängig
bytegenau bestätigt. Neue SQL35-LF-SHA:
`81cf1dead911564e9d80f0cdee044b72aa88d25b9821505278b6290cd8336117`;
Quellenobjektdigest `6892931b06ea1460ea1333029448f301bbd951f5bc54d348bd7a30e9458ab047`,
semantischer Vertragsdigest
`4032f80b49e67b9bb9e062c7fbd2c4a0b56f8a655410b6e73e2dde9f74ae6c90`.
Shape, Schema, Methodik, Evaluator und öffentliche CLI bleiben erhalten.

Lokal bestanden 43 Runner-Tests und 37 Producer-/Reporter-Testmethoden
(36 PASS, ein ausdrücklich Linux-spezifischer SKIP unter Windows), dazu
alle sieben DGN-007-Validatoren. Zusätzliche Phase-, Profil-, Kontroll-,
Prospektiv-, Transport- und Compatibility-Suites bestanden. Registry mit
219 Artefakten, Kennungsvertrag und Repositorykontinuität bestanden ebenfalls.
Diese synthetischen und statischen Prüfungen sind keine Incident-Abnahme.

Der einmalige frische T-SQL-Vorcheck begann am 2026-10-07 um 05:43:08 UTC
auf einer neuen eigenen SQL-Server-2022-Developerinstanz `16.0.4295.3`.
Pullref und separat vorab aufgelöste Inspect-ID waren hier jeweils
`sha256:4402d880dd4c34bfa7d8705e56a86cd6c88da80a1f6bbbe741f999e76264a090`.
Vier CPU und 8 GiB, keine Ports oder Mounts, kein Pull, Secrets ausschließlich
im temporären Prozess-Environment. Die import-sichere private Fixture
extrahiert nach dem strengen Stripnachweis den tatsächlichen kanonischen
G13-Branch; nur die beiden gespeicherten Quellen werden durch temporäre
synthetische Tabellen in `master` ersetzt. Es entstehen keine DGN-Datenbank
und keine zusätzlichen Suchausführungen.

Alle acht tatsächlichen SQL-Cases bestanden: First−Start=−1 Tick,
Last−Finish=+1 Tick, beide verletzte Grenzen, Gleichheit ohne Verletzung,
gleiche Requestgrenzen mit verletzten Profilzeiten, UTC-Offsetnormalisierung,
acht vollständig geprüfte Gruppen sowie neun Gruppen mit ausdrücklichem
Overflow. Die tatsächliche stderr-Ausgabe wurde im Speicher vom neuen
Parser geprüft; kein Rohoutput wurde persistiert. Die Instanz war vor und
nach jedem Case hinsichtlich Benutzerdatenbanken leer. Der Vorabfreeze mit
20 gebundenen Dateien blieb vor jedem Case und abschließend unverändert:
14 Quellen, Vertrag, drei geänderte Pythondateien und beide privaten Helper.
Freeze-Digest `c6c14753928f501fb2450ce1db9efc2261699ba080b889b971b61d264f7ad539`;
Runner-LF `ca6703285492820719544d6ba0c72fd6973e83c67769f64ae767d45542f14420`,
private Fixture-LF `f62f30158a407582a817c4a7e1866614395b2c3630a705dd5d04ef98f0314f54`,
Parent-LF `df2d15aa71ca8d46883b673b0bba4b6a4e3438faf48975d939ec18b86cb3be54`.

Die eigene CID
`e3ba774b14b8305a6cb8104d9ff3363b314621569b04d4be3e7f1dbfb13e368d`
mit Name `sqlperf-dgn007-boundary-16-1d4e79aa40` wurde nach exakter
Name-/Scope-/Owner-/Imageprüfung mit `rm --force --volumes` entfernt.
Der Parent bestätigte nach Entfernung die CID-Abwesenheit; der unabhängige
Agent prüfte zusätzlich genau diese CID und diesen exakten Namen jeweils
mit Exit 0 und null Treffern. Der Parent
beendete die Prüfung mit Exit 0. Das ist ein begrenzter SQL-Syntax-,
Framing-, UTC-/Abstands- und Overflow-Nachweis auf 2022; keine vollständige
Lifecycle-/Versionsmatrix und keine Reproduktion des tatsächlichen Main-G13.

Die reguläre PR-CI am exakten neuen Head gegen den aktuellen Base-Stand
bleibt vor Integration erforderlich. Die Ursache des historischen Main-
G13 ist weiterhin offen; dieser Reporter schließt eine Messlücke und
behauptet keine Behebung, Toleranzfreigabe oder Incidentpromotion.

## Verbleibende Abnahmegrenzen

Lokale Ergebnisse und spätere Actions-Ergebnisse werden getrennt
bewertet. Coordinator-, Ressourcen-, Reihenfolge- und vollständige
Lifecycleattestation sowie Incident-, Ursachen-, Mitigations-, Capstone-
und Szenariofreigabe bleiben offen.
