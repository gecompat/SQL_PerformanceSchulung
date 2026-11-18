# Nächste Entwicklungswellen

## Releasecheckpoint vom 18. November 2026 und Fortsetzung der Welle

Nach PR #1084 wurde der W-PRS-001-Kursrelease auf dem sauberen `main`-Commit
`89ccc0a109be6d059dc3b3f77fcdf7335196ae56` gebaut. Die Welle wurde danach
auf Nutzerwunsch angehalten; mit dem späteren Auftrag, das übergeordnete
Entwicklungsziel weiterzuverfolgen, ist sie auf dem sauberen `main`-Stand
`ede7851bf7df223106100841dd3845c84030875f` wieder aktiv. Build,
Vollständigrender, 209 SlideKey-gebundene Bytevergleiche und gezielter
Datenschutzscan bestanden. Details stehen im
[Releaseprotokoll](W_PRS_001_TEACHING_RELEASE.md#releasebuild-auf-main-89ccc0a1-nach-pr-1084).
Die nachfolgenden Abschnitte führen offene Entwicklungs- und Qualifikations-
Gates. Die menschliche Generalprobe bleibt ausgeschlossen; SQL-Lab-, Produkt-
und Runtimegates bleiben offen.

### Abgeschlossener DGN-007-Folgeschnitt: native `Pattern.groupindex`-Quellbindung

PR #1086 integrierte den digestgebundenen CPython-3.12.16-Offlinecandidate vom
`re/_parser.py`-Gruppennamenpfad bis zur nativen `Pattern.groupindex`-Ansicht.
Alle sieben PR-Checks und die vier Main-Push-Workflows bestanden; der Stand ist
als Snapshot [`snapshot-2026-11-18-4`](https://github.com/gecompat/SQL_PerformanceSchulung/releases/tag/snapshot-2026-11-18-4)
auf Commit `d86a13e4` veröffentlicht. Der Kandidat führt keine Parser-, Regex-
oder Runtimeausführung aus.

### DGN-007-Folgeschnitt: Capture-Gruppenzahl bis `Pattern.groups` binden

Der nächste Offlinezuschnitt verknüpft `State.groups` und
`p.state.groups - 1` mit der nativen Speicherung in `self->groups` sowie der
schreibgeschützten `Pattern.groups`-Mitgliedseigenschaft. Der bereits gepinnte
CPython-3.12.16-Quellstand liefert dafür `sre.c` und `sre.h`; der kombinierte
Quellfluss bleibt `CANDIDATES_ONLY`. Der vollständige Archiv-Analyzerlauf
liefert den gebundenen Kandidaten; 308 fokussierte Regressionen bestehen lokal.
Keine Parser-/Regexausführung,
kein CPython-Build und keine Laufzeitqualifikation. DGN-004 bleibt separat am
YELLOW-Isolationsgate blockiert, solange fremde SQL-Server-Container aktiv sind.

## Aktuelle autonome Fortsetzungsplanung vom 8. November 2026
### SQL Server 2025 `OPTIMIZED_SP_EXECUTESQL`: Methodenentwurf

Der eigenständige [Concurrent-Compile-Methodenentwurf](OPTIMIZED_SP_EXECUTESQL_CONCURRENT_COMPILE_DESIGN.md) konkretisiert den nächsten Entwicklungsschritt. Offen bleiben die unabhängige Methodenprüfung und eine verifizierte Build-/XE-Ereignis- und Feldzuordnung für dynamische Batches. Bis diese Gates erfüllt sind, erfolgen keine Aktivierung, SQL-Ausführung, Demo-ID-Vergabe oder Performanceaussage. `QRY-004` bleibt unverändert; die menschliche Generalprobe ist ausgeschlossen.

### IDX-010 – Methodenentwurf für geordnete NCCI (17. November 2026)

Innerhalb der laufenden Freigabe von sechs Kandidaten ist ein Offlinepaket mit
höchstens einem Arbeitspaket, einem Pull Request und einem neuen gebündelten
Quellenkandidaten vorgesehen; kein Budgetreset. Der [Methodenentwurf für
geordnete nicht gruppierte Columnstore-Indizes](IDX010_ORDERED_NCCI_METHOD.md)
vergleicht denselben synthetischen Rowstore-Bestand mit ungeordnetem und
`ORDER (EventDate)`-NCCI. `SRC-063` wurde aktuell abgerufen; `SRC-165` bindet
die CREATE-Syntax, Segmentmetadaten, SQL-Server-2025-Verfügbarkeit und das
Microsoft Order-Quality-Skript. Der Methodenkandidat fixiert jetzt beide
Builds auf offline und `MAXDOP = 1`, damit die Parallelität kontrolliert ist;
die Methode behauptet damit keine vollständige Ordnung für NCCI. Das Zeitbudget
muss den potenziell längeren geordneten Build beider Arme enthalten. Keine
SQL-/Lab-/Runtimeausführung, keine
Demoerweiterung und keine menschliche Generalprobe. Nach dem Dokumentations-
checkpoint bleiben unabhängiger Methodenreview, exakter Image-/Build-/Edition-
Nachweis, numerische Ressourcenobergrenzen und ein separat autorisierter
isolierter Pilot offen. Das bestehende IDX-010 mit gruppiertem Columnstore
bleibt unverändert.

PR #1009 integrierte die kontrollierte Offline-Buildbedingung `MAXDOP = 1`
für beide NCCI-Arme; vollständige Sortierung, unabhängiger Methodenreview und
Pilot bleiben offen. PR #1010 integrierte danach die dokumentierte Abfrage der
Indexgeneration aus `sys.vector_indexes` samt ScriptDom-Prüfung für den
SQL-Server-2025-Vektor-Lesepfad. Der Zusatz dokumentiert weiterhin keine
Projektbuild- oder Suchqualifikation.

Der nächste Offlinepunkt hat den Build-/Editionskandidaten anhand von `SRC-083`
und `SRC-165` quellengebunden eingegrenzt. PR #941 erfasste Build
`17.0.5065.9`, Digest
`sha256:05644dad1266ca3d445d1e8f6d2ebb9a6a03df9a39376e0f7b48917356dca9d9`
und `MSSQL_PID=Developer`; die damalige Ausgabe enthält jedoch keine
`SERVERPROPERTY('Edition')`-Auswertung und kein NCCI-`ORDER`-Verhalten. Die
Microsoft-Quellen belegen `ORDER` für NCCI ab SQL Server 2025 und Columnstore
in Enterprise, Standard und Express. Sie führen `ORDER` nicht separat pro
Edition auf; da die Methode Offlinebuilds vorsieht, wird keine Onlineoperation
vorausgesetzt. Der Digest bleibt historische Kandidatenevidenz, kein
unveränderlicher Pilot-Lock oder Projektqualifikation.

Umfang dieser Offlinewelle: ein Arbeitspaket, ein PR und höchstens zwei bereits
registrierte Quellen-/Vertragskandidaten. Der nächste anschlussfähige Schritt
ist der unabhängige Methodenreview; danach können numerische Ressourcen- und
Zeitobergrenzen sowie ein unveränderlicher Pilot-Lock festgelegt werden. Kein
Image-Pull, Containerstart, SQL-/Lab-Lauf, keine neue Demo-ID, Such-/NCCI-
Qualifikation oder menschliche Generalprobe. Der separat autorisierte
isolierte Pilot bleibt ein eigenes Gate. Es gibt keinen Budgetreset;
Token- und Geldverbrauch sind nicht verlässlich gemessen.

### RES-004 – finale Ausgabe der Grant-Wartezeit absichern (17. November 2026)

Dieser freigegebene Offlinepunkt bindet die von der Lehrnotiz und dem
Methodenentwurf geforderte Grant-Wartezeit `mg.wait_time_ms` an die finale
Diagnoseprojektion. Zwei synthetische Negativfälle schützen gegen einen Wert,
der nur in einem CTE vorkommt, und gegen einen konstanten Ersatz mit gleichem
Alias. Die Curriculum-Erklärung trennt die positive Grant-Wartezeit vom
unabhängigen Requestfeld `r.wait_time`. 31 Lehrabfrage- und 24
Offlinevertragstests sowie die Struktur- und Curriculumvalidatoren bestehen;
die T-SQL-Beispiele parsen weiterhin unter SQL Server 2019, 2022 und 2025.
Umfang: ein Arbeitspaket, ein PR, keine neue Quelle, keine SQL-/Lab-/Runtime-
Ausführung und keine menschliche Generalprobe. Methodenreview, echte DMV-
Herkunft, numerische Ressourcen- und Zeitgrenzen sowie isolierter Pilot bleiben
offen.

### IDX-007 – finale Warteaggregate der Seitendiagnose binden (17. November 2026)

Dieser freigegebene Offlinepunkt bindet `waiting_sessions`,
`shortest_wait_time_ms` und `longest_wait_time_ms` an die finale Projektion der
letzten-Indexseite-Lehrabfrage. Eine reproduzierte Decoy-Gegenprobe zeigte, dass
die bisherigen Textprüfungen korrekte Aggregate in verschachtelten
Unterabfragen akzeptierten, obwohl die tatsächliche Ergebnisausgabe andere
Werte trug. Die Prüfer verlangen jetzt die drei Aggregate als echte
Endausgabespalten. 30 Lehrabfragetests und der Validator bestehen. Umfang: ein
Arbeitspaket, ein PR, keine neue Quelle und keine SQL-/Runtimeausführung. Die
fehlende Terminaldarstellung, Seiten-/Zeitobergrenzen, Splitverhalten und
isolierter Enginepilot bleiben offen.

### Begrenzung der Fortsetzung vom 12. November 2026

Der Nutzer hat die Bearbeitung aller restlichen freigegebenen Themen fortgesetzt
und sechs weitere Quellen-/Testkandidaten freigegeben. Für diese begrenzte
Fortsetzung gelten höchstens zwei Arbeitspakete, zwei Pull Requests und sechs
neue Quellen-/Vertragskandidaten. Das erste Paket, der External-Tables-
Konzeptentwurf, ist integriert; es verwendete keine neue Produktquelle und
zwei lokale Vertrags-/Lesepfadprüfungen. Die bestehenden `SRC-153` bis
`SRC-157` werden wiederverwendet und nicht als neue Quellenkandidaten gezählt.
Das zweite Paket beschränkt sich auf den Quellenabgleich der bestehenden
`CLM-045`-Traceability. Checkpoint ist spätestens die zweite PR-Integration.
SQL, Connector, Netzwerk, Dienst, Credential und menschliche Generalprobe sind
nicht Teil dieses Rahmens. Token- und Geldverbrauch sind nicht verlässlich
gemessen. Die Fortsetzung setzt die kumulative Budgethistorie nicht zurück;
der letzte ältere Summenstand ersetzt keine aktuelle Verbrauchsprüfung.

Die Fortsetzung nach PR #530 ergänzte `LO-M03-05` durch die
[External-Tables-Lernnotiz](../Curriculum/EXTERNAL_TABLES_LESSON.md); PR #531
integrierte sie mit sieben erfolgreichen CI-Checks. Sie bleibt erklärender
Inhalt ohne Demo-ID oder Lauf-/Messclaim.

Nach dem Checkpoint durch PR #531 setzt die ausdrückliche Anweisung des
Nutzers zur autonomen Bearbeitung aller übrigen freigegebenen Themen den
Auftrag fort. Für den nächsten eigenständigen Graph-Tables-Lehrnotizschnitt
gilt eine weitere begrenzte Fortsetzung von höchstens einem Arbeitspaket,
einem Pull Request und zwei Quellen-/Vertragskandidaten. Die vorhandenen
`SRC-122` und `SRC-124` sowie der abgeschlossene T-SQL-Syntaxreview bilden die
Quellenbasis; neue Produktquellen werden nicht benötigt. Checkpoint ist die
PR-Integration. Keine SQL-, Lab- oder Runtimeausführung und keine menschliche
Generalprobe. Kein Budgetreset und keine monetäre/tokenbasierte
Verbrauchsbehauptung.

Das Arbeitspaket ergänzt `LO-M03-06`/`CLM-047` mit einer quellengebundenen
Erklärung des Graph-gegen-relationalen Zwei-Kanten-Pfads und führt sie im
Curriculum-Lesepfad auf. Es übernimmt keine Performanceaussage des
PROPOSED-Demoentwurfs.

Nach PR #532 ist diese Graph-Notiz integriert. Die ausdrückliche Fortsetzung
aller übrigen freigegebenen Themen eröffnet eine neue, endliche Welle für die
Curriculum-Scopeentscheidung zu External Tables: höchstens ein Arbeitspaket,
ein PR und zwei lokale Vertrags-/Curriculumkandidaten; keine neuen
Produktquellen. Der Checkpoint ist die PR-Integration, die harte Grenze ein
Paket/ein PR/zwei Kandidaten. Verlässliche Token- und Geldmessung fehlt; die
Grenze wird daher über Arbeitspaket, PR und Kandidaten geprüft, nicht als
Provider-Ausgabenlimit ausgegeben. Ziel ist eine quellengebundene Empfehlung,
ob die vorhandene External-Tables-Lernnotiz QRY-012 als ausführbare Phase
erweitern sollte. SQL, Runtime, Connector, Netzwerk, Dienst, Credential und
menschliche Generalprobe bleiben ausgeschlossen.

Die [Scopeempfehlung](EXTERNAL_TABLES_CURRICULUM_SCOPE_REVIEW.md) ist erstellt:
External Tables bleiben eine ergänzende Erklärung zu `LO-M03-05`/`CLM-045`;
eine weitere ausführbare Phase in `QRY-012` wird bis zu einer registrierten
Projektentscheidung und einem eigenen Infrastruktur-/Methodenvertrag nicht
empfohlen. Zwei lokale Curriculum-/Vertragskandidaten wurden gegengeprüft; es
wurden keine neuen Produktquellen verwendet. Das Paket bleibt innerhalb des
1/1/2-Rahmens; der PR-Checkpoint ist noch offen. Die formale Entscheidung,
Demo-ID, Methoden- und Runtimefreigabe bleiben offen.

Der Nutzer hat anschließend die verbleibenden offenen Themen ausdrücklich
freigegeben. Für die formale Registrierung der bereits geprüften
Curriculumentscheidung gilt eine weitere endliche Welle von höchstens einem
Arbeitspaket, einem PR und zwei lokalen Entscheidungs-/Vertragskandidaten;
keine neuen Produktquellen. Der PR-Merge ist der Checkpoint, die Grenze ist
1/1/2 ohne Reset. Token- und Geldverbrauch bleiben unbekannt. Scope: DEC-078
bindet den erklärenden External-Tables-Lehrpfad an `LO-M03-05`/`CLM-045` und
entscheidet gegen eine ausführbare External-Tables-Phase in `QRY-012` im
aktuellen Curriculumstand. Keine Demo-ID, SQL-, Infrastruktur- oder
Runtimefreigabe. DEC-078 und der Registrydatensatz sind angelegt; lokale
Registry- und Projektchecks sowie der PR-/Integrationsabschluss sind mit PR
#534 abgeschlossen. Der Main-Stand ist `9aaa1b1`.

### Graph Tables: formale Freigabe der statischen Methodik

Die ausdrückliche Freigabe aller verbleibenden offenen Themen eröffnet für
QRY-023 ein begrenztes Offline-Arbeitspaket: höchstens ein Paket, ein PR und
zwei lokale Entscheidungs-/Vertragskandidaten; keine neuen Produktquellen.
Der Checkpoint ist die PR-Integration. Token- und Geldverbrauch bleiben
unbekannt; der Rahmen wird über Paket/PR/Kandidaten begrenzt und ist kein
Provider-Ausgabenlimit. Die bestehende Methodik aus Quellen-/Methodenreview,
Messworkload und Framework-/Matrixreview wird für die weitere statische
Vertragsimplementierung genehmigt und als `DEC-079` registriert. QRY-023 bleibt
`PROPOSED`. Keine SQL-/Lab-/Runtime-Ausführung, Rechteänderung, Infrastruktur,
neue Performanceaussage oder menschliche Generalprobe.

PR #535 integrierte `DEC-079` am Commit `6bbc09e`; der getestete Baum wurde
unverändert übernommen und `main` synchronisiert. Die nächste autonome Welle
begrenzt sich auf ein Arbeitspaket, einen PR und zwei Quellen-/Vertragskandidaten.
Sie registriert `DEC-080` für die statische ScriptDom-Syntaxakzeptanz der acht
ausführbaren QRY-023-T-SQL-Dateien unter 150/160/170 und synchronisiert die
betroffenen Lesepfade. Keine neuen Produktquellen, kein SQL-/Lab-/Runtimelauf,
keine menschliche Generalprobe. Token- und Geldverbrauch bleiben unbekannt;
Paket/PR/Kandidaten begrenzen den Umfang, nicht Providerkosten.

Nach lokaler gesperrter Parserprüfung und Projektvalidierung ist PR-Integration
der Checkpoint. Formale Harnessabnahme, phasenspezifische Identität,
Build-/Image-, Ressourcen-, Cleanup- und Runtimegates bleiben offen.

PR #536 integrierte `DEC-080` am Commit `73ef23a`; alle zehn CI-Checks waren
erfolgreich, der getestete Baum wurde übernommen, `main` synchronisiert und
der lokale sowie Remote-Arbeitsbranch entfernt. Für den nächsten offenen
Offlinepunkt gilt ein Paket, ein PR und zwei Quellen-/Vertragskandidaten. Der
bestehende `SRC-127`-Servicingeintrag wird neu geprüft; keine neue Produktquelle,
kein Container-/Imageabruf, kein SQL-/Lab-/Runtimelauf und keine menschliche
Generalprobe. Der Quellencheck bestätigt allein, dass die vorhandenen drei
Designpins weiterhin den neuesten Microsoft-Linux-Servicingbuilds entsprechen.
Die bisherigen OCI-Digests bleiben auf ihrem Quellenstand 7. November datiert.
Token- und Geldverbrauch bleiben unbekannt; Umfang ist über Paket/PR/Kandidaten
begrenzt, nicht monetär.

PR #537 integrierte `DEC-081` am Commit `9274937`; elf Checks waren erfolgreich,
`main` ist synchronisiert und der lokale/Remote-Branch entfernt. Der nächste
Offlinepunkt prüft innerhalb eines Pakets, eines PRs und höchstens zwei
Quellen-/Vertragskandidaten read-only die aktuellen MCR-Manifest- und
Konfigurationsdigests der drei bereits vorgeschlagenen Tags gegen den Lock.
Kein Image-Layerdownload, Build, Containerstart, SQL, Runtime oder menschliche
Generalprobe. `SRC-130` wird aktualisiert; Runtimecallerintegration bleibt ein
separates Gate. Verbrauch in Tokens/Geld ist nicht verlässlich messbar.

PR #538 integrierte `DEC-082` am Commit `ffaa196`; elf Checks waren erfolgreich,
`main` ist synchronisiert und der lokale/Remote-Branch entfernt. Der nächste
begrenzte Offlinepunkt aktualisiert innerhalb eines Arbeitspakets, eines PRs und
höchstens zwei bestehenden Quellen-/Vertragskandidaten die Editionsmatrix
`SRC-126` und den zugehörigen QRY-023-Review anhand der drei offiziellen
Microsoft-Editionsseiten. Keine neue Produktquelle, Engineabfrage, Imageaktion,
SQL-/Lab-/Runtimeausführung oder menschliche Generalprobe. Das belegt allein
die dokumentierte Verfügbarkeit, keine tatsächliche Edition oder Qualifikation.
Token- und Geldverbrauch bleiben unbekannt; Paket/PR/Kandidaten begrenzen den
Umfang, nicht Providerkosten.

PR #539 aktualisierte `SRC-126`; PR #540 erfasste den weiterhin offenen
DGN-004-Isolationsblocker. Beide sind integriert. Für den nächsten Offlinepunkt
gilt ein Arbeitspaket und ein PR mit höchstens drei Vertragskandidaten: FWK-010
erweitert den Caller um optionale SQL-Anmeldungsprofile je Phase; QRY-023 ordnet
das vorhandene Rechteprofil ADMIN beziehungsweise READER den Phasen zu; die
DGN-007-Prozesskantenprüfung bindet den angepassten `run_demo.py`-AST weiter
exakt. `sqlcmd_process.py` bleibt unverändert, damit der unabhängige CON-010-
Collectorvertrag unverändert gilt. Keine neue Produktquelle, keine
Loginerstellung, Rechteänderung, SQL-, Lab- oder Runtimeausführung und keine
menschliche Generalprobe. DGN-007-Quellenbundle-, Kanten- und Harnessloader-
prüfungen bleiben gebundene Verbraucher. Der Client-Identitätswechsel schließt
keine Serverrechte-, Ressourcen-, Abbruch-, Cleanup- oder Runtimequalifikation.
Token- und Geldverbrauch sind unbekannt; Umfangsgrenze ist 1/1/3 aus den sechs
freigegebenen Kandidaten, ohne Reset.

PR #541 integrierte die phasenspezifischen SQL-Anmeldungsprofile über Squash
`e430cde`; 77 PR-Checks und die ausgelösten Main-Workflows bestanden. Main ist
synchronisiert, der lokale und Remote-Branch sind entfernt. Der folgende
begrenzte Offlinepunkt klärt die Grenze zwischen positiven `READER`-
Rechteprüfungen und dem weiterhin offenen Nachweis fehlender Zusatzrechte.
Microsofts Rollenfunktionen prüfen Mitgliedschaft, nicht effektive Rechte, und
benötigen Rollenmetadatensicht. Die QRY-023-Dokumentation hält deshalb fest,
warum sie allein kein Minimalrechte-Gate bilden. Keine Änderung an
Serverprinzipalen oder Grants, kein SQL-/Runtime-/Lab-Lauf und keine
menschliche Generalprobe. Umfang: ein Arbeitspaket, ein PR, zwei
Dokumentationskandidaten; verbleibende SQL-, Rechte-, Ressourcen-, Abbruch-,
Cleanup- und Runtimegates bleiben offen.

PR #542 integrierte diese Rollenfunktionsgrenze. Der nächste Offlinepunkt
konkretisiert den Soll-Ist-Prüfansatz, ohne bereits eine Rechteprüfung oder
Runtimefreigabe zu behaupten: `sys.fn_my_permissions` wird als möglicher
Abgleich effektiver Rechte im tatsächlichen `READER`-Kontext dokumentiert.
README und Harnessreview müssen Server-, Datenbank-, Schema- und Objektkontexte,
eine vorab festgelegte phasengenaue Sollmenge, fail-closed Verhalten sowie die
Grenzen zu anderen Principals und Ownership Chain gemeinsam abbilden. Grenze:
ein Arbeitspaket, ein PR, zwei bestehende Dokumentationskandidaten; innerhalb
der sechs freigegebenen Kandidaten, ohne Reset. Keine neue Produktquelle, keine
Serverprinzipal-/Grantänderung, kein SQL-/Lab-/Runtime-Lauf und keine
menschliche Generalprobe. Der verbleibende Lauf- und Minimalrechtenachweis
bleibt offen.

PR #543 integrierte den dokumentierten `sys.fn_my_permissions`-Ansatz. Die
anschließende Scopeprüfung fand eine weitere Grenze: Eine Prüfung nur der
QRY-023-Objekte schließt zusätzliche Grants auf anderen Instanz-, Datenbank-
oder Spalten-Securables nicht aus. Der folgende begrenzte Offlinepunkt macht
diese Beweisgrenze in README und Harnessreview ausdrücklich. Ein vollständiger
Minimalrechtnachweis muss später eine vollständige relevante Inventur oder eine
qualifizierte dedizierte Instanz mit gebundenem Objektbestand verwenden. Umfang:
ein Arbeitspaket, ein PR und zwei bestehende Dokumentationskandidaten innerhalb
der sechs freigegebenen Kandidaten; kein Reset und keine neue Produktquelle.
Keine Principals/Grants, kein SQL-/Lab-/Runtime-Lauf und keine menschliche
Generalprobe. Implementierung und tatsächliche Rechtequalifikation bleiben
Folgearbeit.

PR #544 integrierte diese vollständige Aussagegrenze am Commit `c0707b3`.
Der nächste Offlinepunkt prüft die von QRY-023 tatsächlich aufgerufene
FWK-004-Variante: `@CaptureSessionWaits=0` muss fest bleiben, weil ein Wechsel
auf `1` bei SQL Server 2022/2025 den Zugriff auf
`sys.dm_exec_session_wait_stats` und damit `VIEW SERVER PERFORMANCE STATE`
erfordert. Die `sys.dm_exec_sessions`-Abfrage bleibt auf die eigene Session
beschränkt. Die vorhandene Vertragsprüfung bindet den Wert bereits; eine
Negativregression und quellengebundene Klarstellung schützen diesen
Least-Privilege-Codepfad. Begrenzung: ein Arbeitspaket, ein PR, höchstens drei
Quellen-/Vertragskandidaten; keine neue SQL-Ausführung, keine Serverrechte oder
Credentials, keine menschliche Generalprobe. Die restliche effektive
Rechteinventur und Runtimequalifikation bleiben offen.

PR #545 integrierte die Wait-Statistikgrenze am Commit `78521f0`; 50 gezielte
QRY-023-Regressionen und sieben PR-Checks bestanden. Die anschließende
Quellinventur fand eine echte Lücke im positiven Preflight: `30_Correctness.sql`
liest neben den vier Graph-/Relations-Tabellen vier Oracle-Tabellen. Der
Preflight prüfte deren `SELECT`-Rechte nicht und hätte trotz fehlender Oracle-
Leseerlaubnis `PASS` melden können. Der nächste begrenzte Schnitt ergänzt alle
acht Objektprüfungen, bindet dieselbe Liste im Proposed-Manifest und schützt
die Auslassung einer Oracleberechtigung mit einer Negativregression.
Begrenzung: ein Arbeitspaket, ein PR und höchstens drei Quellen-/Vertrags-
kandidaten (Korrektheitsskript, Preflight/Manifestvertrag, Validator mit
Regressionstest); keine neue Produktquelle, kein Grant, kein SQL-/Lab-/Runtime-
Lauf und keine menschliche Generalprobe. Die vollständige effektive
Rechteinventur und die übrigen Runtimegates bleiben offen.

Nach der Integration dieser Vier-Oracle-Prüfungen folgt ein begrenzter lokaler
Vertragsschnitt: READER-Phasen werden statisch gegen ihre direkten
`dbo`-/`lab`-Objektreferenzen im Preflight abgeglichen; nicht zuordenbare oder
datenbankqualifizierte Namen, indirekte `EXEC`-Formen und erkannte direkte
persistent schreibende Anweisungen werden zurückgewiesen. Die bereits
vorhandene QRY-023-Testsuite prüft die positiven Skripte und die synthetischen
Negativfälle. Grenze dieses Schnitts: ein Arbeitspaket, ein PR und keine neuen
Produktquellen. Kein SQL-, Lab- oder Runtime-Lauf. Der Merge ist der
Checkpoint; tatsächliche Effektivrechte, vollständige Methodenabnahme und
Runtimegates bleiben davon getrennt offen.

Als nächster eigenständiger statischer Kandidat wird jede schemaqualifizierte
Fundstelle an genau ihren T-SQL-Textkontext gebunden, statt nur Objektname und
Berechtigungsart global zu vergleichen. Eine Negativregression schützt einen
funktionsartigen SELECT-Ausdruck mit vorangestelltem Komma neben einem
gleichnamigen Tabellenzugriff. Grenze:
ein Validator-/Testpaket, ein PR, keine neuen Produktquellen und kein
SQL-/Lab-/Runtime-Lauf. Auch ein bestandener Fundstellencheck bleibt
Textanalyse und belegt keine Engineauflösung oder Effektivrechte.

PR #548 integrierte den Fundstellenabgleich mit sechs PR-Checks und vier
erfolgreichen betroffenen Main-Workflows. Der nächste offline begrenzte
Validator-/Regressionstest-Schnitt ergänzt erkannte `CREATE OR ALTER`-/DROP-
DDL-, `DELETE`-Formen ohne `FROM` und zustandsändernde DBCC-Befehle; ein PR, keine Produktquellen, keine
SQL-/Lab-/Runtimeausführung. Die statische Textprüfung bleibt kein
Engine-/Rechtebeleg.

PR #549 integrierte den direkten Schreibschutz mit sieben erfolgreichen
PR-Checks und fünf betroffenen Main-Workflows. Der nächste isolierte
QRY-023-Validator-/Regressionstest-Schritt prüft, dass READER-Phasen ihren
geprüften Datenbankkontext nicht über `USE` (einschließlich SQLCMD-Varianten)
oder einen vergleichbaren Kontextwechsel verlassen. Ein Arbeitspaket und PR, keine neuen Produktquellen,
kein SQL-/Lab-/Runtime-Lauf. Der statische Befund belegt keine Engine- oder
Effektivberechtigungsqualifikation.

PR #550 integrierte den Reader-Kontextschutz mit sieben erfolgreichen
PR-Checks und fünf betroffenen Main-Workflows. Der nächste Validator-/Regressionstest-
Schnitt weist SQLCMD-`:r`-Includes und `!!`-Shellbefehle in READER-Skripten
zurück. Ein Arbeitspaket/ein PR, keine Produktquellen und keine SQL-, Lab- oder
Runtimeausführung; die Kontrolle über SQLCMD-Imports und Hostprozesse ist damit
nicht allgemein runtimequalifiziert.

PR #551 integrierte den SQLCMD-Controlguard mit sieben erfolgreichen
PR-Checks, drei betroffenen Main-Workflows und 67 QRY-023-Regressionen. Ein
anschließender lokaler Regressionstest bindet den Ausschluss eines abweichenden
`SQLCMDMAXVARTYPEWIDTH`-Werts für READER-Phasen. Ein Test-/Dokumentations-PR,
keine neue Produktquelle und kein SQL-/Lab-/Runtime-Lauf.

PR #552 integrierte diesen Ausschlusstest mit sechs PR-Checks und vier
erfolgreichen betroffenen Main-Workflows. Als enger Follow-up wird die erlaubte
`:setvar SQLCMDMAXVARTYPEWIDTH 0`-Zeile auf `50_Plan_Evidence.sql` beschränkt;
Mess- und Korrektheitsphasen müssen sie ablehnen. Ein Validator-/Regressionstest-
PR, keine neue Produktquelle und kein SQL-/Lab-/Runtime-Lauf.

PR #553 integrierte die phasenspezifische Direktivenbindung mit sieben
erfolgreichen PR-Checks und fünf betroffenen Main-Workflows. Die unabhängige
Offlinequellenabnahme fand danach einen P1 im SQLCMD-Controlguard: `:r` und
`!!` in T-SQL-Blockkommentaren wurden nach deren Entfernung nicht mehr erkannt,
obwohl SQLCMD Controlzeilen vor T-SQL verarbeitet. Ein Validator-/Testfix prüft
jetzt den Rohtext und schützt beide Formen mit Regressionen. 71 gezielte Tests,
der QRY-023-Validator und unabhängiger Nachreview bestehen. Der Full-scope
Review fand außerdem den aktiven Registry-Widerspruch zu FWK-010s bereits
implementierter Phasenidentität; die Registry ist korrigiert und benennt nun
die weiterhin offenen realen Effektivrechte und Runtimegates. PR #554
integrierte beide Korrekturen mit sechs PR-Checks und fünf erfolgreichen
betroffenen Main-Workflows. Als nächster freigegebener Offlinepunkt wurde
[QRY023_EFFECTIVE_PERMISSION_DESIGN.md](QRY023_EFFECTIVE_PERMISSION_DESIGN.md)
erstellt: Phasen-/Securablematrix, fail-closed Mengengrenzen und geplante
Gegenproben für `sys.fn_my_permissions`. Eine anschließende Quellenprüfung
ergänzte SQL-Server-`public`-Baselinerechte und versionsabhängige
Festserverrollen; insbesondere wird `VIEW ANY DATABASE` nicht als erforderliche
QRY-023-Rechte freigegeben. Unabhängiger Review fand keine P1/P2 und bestätigte,
dass keine Instanzrechte oder `public`-Änderung freigegeben wird; QRY-023-
Validator, Dokumentationslinks und Datenschutzscan bestanden. Die konkrete
Effektivrechte-Sollmenge war an diesem Zwischenstand noch offen. Sie ist durch
die spätere `DEC-083` inzwischen für die `public`-Baseline und ihre isolierte
Laufgrenze entschieden; tatsächliche Sollmengenprüfung und Laufqualifikation
bleiben offen. Keine neue Produktquelle und kein SQL-/Lab-/Runtime-Lauf.

Die anschließende SQLCMD-Quellenprüfung fand einen weiteren P2: `GO [count]`
ist ein Utility-Batchtrenner und wiederholt seine vorherige Batch. Der Guard
verwirft jetzt rohe `GO`-Zeilen, auch hinter führenden ein- und mehrzeiligen
Blockkommentaren. Fünf neue Regressionen prüfen nacktes `GO`, `GO` innerhalb
von Blockkommentaren und drei `GO 1000000`-Kommentarpräfixe; die Testsuite (76),
der QRY-023-Validator, Datenschutzprüfung und Dokumentationslinks bestehen.
Der unabhängige Nachreview schloss den P2 ohne weitere P1/P2. Als nächstes
folgen PR- und Integrationsgates. Keine Produktquelle und kein
SQL-/Lab-/Runtime-Lauf.

### QRY-023: READER-Baseline verbindlich begrenzen

Nach Verbrauch der vorherigen sechs Vertragskandidaten hat der Nutzer am
12. November 2026 die verbleibenden offenen Themen erneut ausdrücklich
freigegeben. Für den nächsten QRY-023-Schnitt gilt ein neues, endliches Paket:
höchstens ein Arbeitspaket, ein Pull Request und zwei Entscheidungs-/Vertrags-
kandidaten. Der erste Kandidat legt die bereits quellenbelegte
`public`-Baseline normativ fest; der zweite synchronisiert den Effektivrechte-
Vertrag, das Proposed-Manifest, den Offlinevalidator samt Gegenproben und die
betroffenen README-/Statuspfade. Bereits verwendete Microsoft-Primärquellen
wurden als `SRC-158` zusammengeführt; es gibt keine neue Produktquelle.
Token- und Geldverbrauch sind unbekannt; die Grenze
wird durch Paket/PR/Kandidaten und nicht als Providerkostenlimit geprüft.

`DEC-083` akzeptiert `CONNECT SQL` als reguläres Loginrecht sowie
`VIEW ANY DATABASE` und normales Endpoint-`CONNECT` aus `public` ausschließlich
auf einer für einen einzelnen QRY-023-Run exklusiv reservierten SQL-Server-
Wegwerfinstanz. Das Datenbankinventar ist vor Setup
leer (oder enthält nur die vollständig markierte Wiederaufnahme desselben
Runs) und danach auf die gebundene QRY-023-Datenbank begrenzt. Der Harness
ändert weder `public` noch Serverrechte. Der Offlinevertrag fordert zusätzlich
eine echte READER-Effektivrechteprüfung und vollständige Rollen-/SID-/Endpoint-
Inventur. Keine SQL-/Lab-/Runtimeausführung und keine menschliche Generalprobe.
Der PR-Merge ist der Checkpoint; die Implementierung und alle Laufzeitgates
bleiben für eine spätere getrennte Phase offen.

PR #558 integrierte diese Baseline. Die anschließende Fehleranalyse fand, dass
die separate READER-Anmeldung mangels Datenbankbenutzerzuordnung nicht in die
QRY-023-Zieldatenbank verbinden kann. Dafür ist ein einzelnes Folgepaket mit
maximal einem PR und `DEC-084` begrenzt: explizite FWK-010-Identitätsvariable,
strikte SQLCMD-sichere Loginform, fail-closed SQL_LOGIN-/SID-Zuordnung in der
exakt markierten Datenbank, Manifest-/Validator-/Regression-/Dokumentations-
abgleich. Es gibt keine Serverrechte-/`public`-Änderung und keinen SQL-, Lab-,
Runtime- oder Generalprobenlauf. Der Merge ist Checkpoint; T-SQL-Kompilierung,
reale Rechte-/SID-Qualifikation, Ressourcen-/Cleanupdurchsetzung und sämtliche
Runtimegates bleiben offen.

PR #559 ist am 12. November 2026 nach erfolgreichem unabhängigen Review
integriert. Die direkte QRY-023- und Framework-SQL-Matrix einschließlich
SQL Server 2019/2022/2025 sowie die erforderlichen Registry-/Governance-Gates
waren auf dem finalen Head grün. Zwei nicht betroffene DGN-007-Profilchecks
meldeten `PYTHON_PROFILE_CHANGED`; ihre Fehler wurden diagnostisch geprüft,
nicht umgangen. Ein nicht betroffener SQL-2025-AI-Job war beim Checkpoint noch
in Arbeit.

Als nächstes folgt ein einzelnes QRY-023-Offlinesegment mit maximal einem
Arbeitspaket, einem PR und drei Vertrags-/Test-/Quellenkandidaten: eine
begrenzte Erweiterung des bestehenden Primärquellenpakets `SRC-158` plus die vollständige,
versionierte Sollmenge effektiver Rechte pro Server, Standardendpoint,
Datenbank, Schema und inventarisiertem QRY-023-Securable als deklarativer
Vertrag, dazu synthetische Abweichungs- und Vollständigkeitsgegenproben.
Vorhandene `DEC-083`-Baselines und die Effektivrechtequalifikation bleiben
maßgeblich. PR #560 integrierte die Sollmenge nach unabhängigem Review und acht
grünen PR-Gates. Der aktuelle Schnitt umfasst höchstens ein Arbeitspaket,
einen PR und drei Kandidaten: Quellenregistereintrag `SRC-159` sowie die
read-only ADMIN-Inventurimplementierung und ihre Tests für
READER-Login-/Datenbank-SID, Server-/Datenbankrollen, explizite Grants/DENYs,
Benutzerdatenbankbestand und Standardendpointbestand samt Offlinevalidator und
synthetischen Abweichungsgegenproben. QRY-Validator, 93 Offline-Regressionen und
ScriptDom-Parse unter 150/160/170 bestanden; der unabhängige Nachreview fand
keine offenen P1/P2. Weil Microsofts Beschreibung „Systemobjekt“ keine exakte
Allowlist der `public`-SELECT-Standardmenge liefert, sperrt die Inventur solche
expliziten Grants bis zu einer versionsgebundenen Sollmenge mit
`FAIL_NOT_PROVEN`; ein PASS wird nicht vorgegeben. PR #561 integrierte den
Schnitt nach acht erfolgreichen PR-Workflows als
`eaccffcf8f306cd3b9a5c2e334e0d67e5ab80f95`.

Die aktuelle Fortsetzung bleibt auf ein Arbeitspaket, einen PR und höchstens
drei kohärente Implementierungs-/Regressionkandidaten begrenzt; `SRC-158` und
`SRC-159` werden wiederverwendet. Die READER-Rechteprüfung erfasst Server,
Datenbank, beide Projekt-Schemas, 13 gebundene Demo-/Frameworkobjekte sowie
jeden ADMIN-inventarisierten Standardendpoint. ADMIN bestätigt außerdem die
Existenz aller 13 gebundenen Objekte, einschließlich dreier für READER
unsichtbarer interner Messobjekte. Der Caller verlangt den festen Objektmarker
und validiert den ADMIN-Endpointhandoff vor Übergabe als SQLCMD-Variablen; die
READER-Verbindung fragt selbst
`sys.fn_my_permissions` je Endpoint ab. Exact-set-Abweichungen,
Duplikate, Spaltenrechte, fehlende Entitynamen oder ein ungültiger Handoff
blockieren PASS beziehungsweise den Folgeaufruf. Offlinevalidator und
synthetische Runner-/Parserregressionen bestehen; der gebundene DGN-007-
Runner-AST-Digest wurde nach Prüfung ebenfalls für diesen gemeinsamen
Runnerstand aktualisiert. QRY-023 selbst bleibt ohne SQL-/Lab-/Runtime-
Ausführung und ohne Generalprobe. Keine Rechtevergabe und keine Rechte- oder
`public`-Mutation. Exakte Systemobjekt-Standardmenge, Ownership-Chain-Wirkung und
Enginequalifikation bleiben offen.

Diese Planung konkretisiert den aktiven Auftrag in
[`CURRENT_EXECUTION_STATUS.md`](CURRENT_EXECUTION_STATUS.md). Sie ersetzt die
überholten Statusangaben der nachfolgenden historischen Planung, insbesondere
die dort genannten Pausen bis zum 20. Oktober. Sie setzt weder neue fachliche
Freigaben noch Laufrechte oder Budgets. Reihenfolge, Umfang und Status werden
vor jedem neuen Arbeitspaket gegen den aktuellen kanonischen Ausführungsstand,
die betroffenen Verträge und den verbleibenden Gesamtbudgetstand abgeglichen.

### Arbeitsfolge

| Schritt | Arbeit und Abschlusskriterium | Grenze / Folgeentscheidung |
|---|---|---|
| 1. DGN-004 statische Annahmeprüfung | Der reine Neun-Aufruf-/Statusprüfer und seine synthetischen Gegenfälle sind integriert. Der unabhängige Methoden-/Quellen-/Zuordnungs-/Transport-/Messreview vom 2026-11-12 fand nach PR #518 keine offenen P1/P2. Eine Read-only-Inventur vom 14.11.2026 fand fünf aktive, nicht DGN-004 zugeordnete SQL-Server-Container; Momentaufnahme: 2022 mit 5,76 % CPU und 2025 mit 15,06 %, beide Zielinstanzen aktiv. | Das YELLOW-Isolations-/Lastgate ist weiterhin nicht erfüllt. Keine SQL-/Lab-Ausführung, bis eine kontrollierte Wegwerfumgebung und Last belegbar sind. Die Momentaufnahme qualifiziert keine Reserve. Danach gelten unverändert Zielbuilds 2022/16.0.4265.3 und 2025/17.0.4075.5, neun Aufrufe je Build, zwei eigene sequenzielle Container, 900 Sekunden gemeinsames Laufbudget plus je 60 Sekunden Cleanup. |
| 2. QRY-002 Lehrnotiz | PR #383 integrierte die quellengebundene Erklärung beider Konvertierungsrichtungen und trennt Typauflösung von konkreter Zugriffswirkung. | Menschliche Generalprobe bleibt ausgeschlossen. Kein Scan-/Seek- oder Leistungsclaim ohne konkrete Plan- und Messbelege. |
| 3. Lesepfade und Kerninhalte | QRY-003/RES-004-Pfade sowie QRY-007 und IDX-003/004/001/002 sind quellengebunden integriert. PR #394 integrierte STL-001, PR #395 STL-002, PR #396 QRY-005, PR #397/#398 OPT-004, PR #399 STL-003, PR #400 QRY-011, PR #401 IDX-005, PR #402 OPT-012, PR #403 STL-010, PR #405 QRY-003, PR #406 QRY-007, PR #408 IDX-003, PR #410 IDX-004, PR #412 IDX-001, PR #414 IDX-002, PR #416 STL-001 und PR #418 STL-002. STL-002 bindet vollständige Nutzdaten- und Padding-Formeln sowie Mengentupeloracles für alle drei Speicherprofile. | Keine SQL-/Runtimefreigabe. STL-001/002 enthalten synthetische Entwurfsoracles; reale Record-/Seiten- und Allocation-Unit-Evidenz sowie Lese-I/O bleiben offen. |
| 4. Diagnose- und vorhandene KI-Qualifikation | Jeweils nur den im aktiven Status ausgewählten, unabhängig prüfbaren Schnitt vorbereiten; Verträge, synthetische Prüfungen und erforderliche Reviews vor jeder Runtimephase abschließen. | Kein SQL-/Provider-/Netzwerk-/Lab-Effekt aus statischer Evidenz ableiten. Lauf-, Provider- und Datenfreigaben gelten pro konkretem Schnitt. |
| 5. CON-006- und IDX-007-Varianten | Der synthetisch geprüfte CON-006-Offline-Graph- und Capturevertrag sowie der IDX-007-Offlinevertrag für caller-supplied `PAGELATCH_EX`-Waits sind im Framework-Contracts-Workflow enthalten. PR #420 ergänzt die IDX-007-Prüfung: fehlender Rechtsaußenbeleg ist `NOT_PROVEN`, expliziter Gegenbeleg `FAIL`. PR #422 prüft den CON-006-Graph-/Capturevertrag lokal. Die unabhängigen Offline-Methoden-/Quellenreviews vom 12.11.2026 fanden nach Timestamp-Korrekturen keine offenen P1/P2 im geprüften Parser-/Quellenumfang. Die aktuellen Herstellertexte spezifizieren das genaue `requestType="convert"`-Schema nicht; Herkunftsbindung der Capturefelder, dessen Engine-Qualifikation und IDX-007-Seitenkettenauflösung bleiben offen. Die Curriculumnotiz ergänzt jetzt für IDX-007 einen gepaarten OFF/ON-Mindestvertrag samt kontrolliertem Skip bei fehlender Konkurrenz; empirische Messung und tatsächlicher Wait-/Page-Nachweis bleiben offen. | Graph, Zeitfenster, Marker, Eventquelle, Actorresultate, Waits und Seitenfelder sind caller-geliefert und unauthentifiziert. Der statische `PASS` und der Vergleichsvertrag sind kein Laufzeit- oder Engpassnachweis. Range bleibt zurückgestellt. Kein SQL-/Lab-Lauf ohne konkreten Demo-Vertrag, Methodenfreigabe und Safety-/Cleanup-Gates. |
| 6. Nachgelagerte Erweiterungen | Der statische RES-001-Offlineschnitt und RES-003-Offlinevertrag samt quellengebundener Lehrnotiz sind integriert. Die Detailprüfung zu SQL Server 2025 `OPTIMIZED_SP_EXECUTESQL` ist abgeschlossen; Aktivierung, Demo und Performanceclaim bleiben `DEFER`, weil die bestehende QRY-004-Abnahme keine zeitgleiche Kompilierung prüft. Für Graph Tables sind die quellengebundene Lernnotiz, Methodikfreigabe (`DEC-079`), ScriptDom-Akzeptanz (`DEC-080`), Produktbuild-/Digestbindung (`DEC-081`/`DEC-082`) und der unabhängige Harnessreview abgeschlossen. Der isolierte QRY-023-Harness bestand auf SQL Server 2019/2022/2025; PR #716 bindet die Runtime-Matrix direkt an den Proposed Image-Lock. QRY-023 bleibt dennoch `PROPOSED`, nicht katalogisiert und `runtime_authorized: false`; allgemeine Runtime-/Produkt-/Katalogfreigabe, empirische Ressourcencharakterisierung und menschliche Generalprobe bleiben getrennte Gates, wobei die Generalprobe ausgeschlossen ist. Details stehen in [Demoentwurf und Vertrag](GRAPH_TABLES_DEMO_CONCEPT.md), [Messworkload](GRAPH_TABLES_MEASUREMENT_WORKLOAD_DESIGN.md), [Harnessreview](QRY023_PROPOSED_HARNESS_REVIEW.md) und im [aktuellen Ausführungsstand](CURRENT_EXECUTION_STATUS.md). Für External Tables sind die quellengebundene Lernnotiz, der [statische Lehr- und Demoentwurf](EXTERNAL_TABLES_DEMO_CONCEPT.md) und die formale Curriculumentscheidung `DEC-078` integriert: ergänzende Erklärung zu `LO-M03-05`/`CLM-045`, keine ausführbare Erweiterung von `QRY-012`. Eine spätere eigenständige External-Tables-Demo benötigt weiterhin Infrastruktur-, Methoden-, Rechte-, Cleanup- und Runtimevertrag. | RES-003 bleibt ein roter, nicht ausführbarer Druckversuch; `OPTIMIZED_SP_EXECUTESQL` erhält keine Runtimefreigabe. Graph Tables bleiben `PROPOSED`; die isolierte Enginequalifikation ist keine allgemeine Laufzeit- oder Produktfreigabe und behauptet keine Leistungsrangfolge. External Tables besitzen keine eigene Demo-ID und keine Runtimequalifikation; sie behaupten weder eine allgemeine Rangfolge noch tatsächliches Pushdown ohne korrelierte Evidenz. Statische und quellengebundene Erklärung ersetzt weder authentische Runtime-Evidenz noch Kausalitätsnachweis. Weitere Ressourcen und Infrastruktur nur mit eigenem Methoden-, Versions-, Sicherheits- und Cleanupvertrag. |

PR #424 bindet beim QRY-023-Proposed-Harness Phasenscript, Zieldatenbank,
Zeitlimits, Cleanup und Gesamtbudgets. PR #426 ergänzt `Reads` und `Writes` als
Pflichtfelder und gepaarte Statistikmetriken neben CPU, Logical Reads und
Elapsed; Zähler bleiben Sessiondeltas einschließlich Messprozedur-Overhead.
PR #429 schützt das Abschalten von `STATISTICS XML` bei Erfolg und fangbaren
Fehlern in der separaten Actual-Plan-Phase nach dem FWK-005-Cleanupmuster. Der
Validator und eine Negativregression binden den Fehlerpfad; Verbindungsabbruch
und tatsächliche Sessionwirkung bleiben unbelegt. PR #431 bindet beide
`COUNT_BIG`-Planabfragen per normalisiertem Statementvergleich an die Graph-
und Relationsvarianten der Messprozedur; zwei Negativregressionen schützen
Graph-`MATCH` und den relationalen Zieljoin. 19 QRY-023-Regressionen sowie die
statischen QRY-023-, Framework- und Repository-Continuity-Prüfungen bestanden.
Das bleibt eine Textstrukturprüfung ohne SQL-/Runtime- oder Lab-Ausführung.
QRY-023 bleibt `PROPOSED`; formale T-SQL-Abnahme, unabhängige
Methodenfreigabe und Runtimegates bleiben offen.
PR #433 schützt die Reihenfolge von erfolgreicher Plan-Summary und
`STATISTICS XML OFF` einschließlich TRY/CATCH-Grenze. Die gezielte
Negativregression weist vorgezogenes PASS zurück; 20 QRY-023-Regressionen und
die statischen QRY-023-, Framework- und Repository-Continuity-Prüfungen
bestanden. Dies belegt nur Textreihenfolge, keine SQL-/Runtimeausführung oder
Sessionwirkung. QRY-023 bleibt `PROPOSED`; formale T-SQL-Abnahme, unabhängige
Methodenfreigabe und Runtimegates bleiben offen.
PR #435 bindet die Summaryfelder `Phase=PLAN_EVIDENCE`, `CheckId=SUMMARY`,
`Outcome=PASS`, `Code=OK` und den korrespondierenden PASS-Print. Die
Negativregressionen mit WARN-Outcome und Fehlercode werden abgewiesen.
22 QRY-023-Regressionen und die zugehörigen statischen Projektprüfungen
bestanden. Dies belegt keine SQL-Ausführung oder Ergebniswahrheit; QRY-023
bleibt `PROPOSED` und alle formalen sowie Runtimegates bleiben offen.
PR #437 bindet beide Planabfragen statisch innerhalb des
`STATISTICS XML ON/OFF`-Fensters; eine Negativregression verschiebt sie vor
`BEGIN TRY` und wird abgewiesen. 23 QRY-023-Regressionen und die statischen
QRY-023-, Framework- und Repository-Continuity-Prüfungen bestanden. Keine
SQL-/Runtimeausführung; die formalen T-SQL-, Methoden- und Runtimegates bleiben
offen.
PR #439 bindet `SHOWPLAN` an `DB_NAME()`/`DATABASE` und `SELECT` an alle vier
Querytabellen. Scope-, Tabellenrecht- und Skip-Code-Negativfälle werden
abgewiesen; 26 QRY-023-Regressionen sowie die statischen Projektvalidatoren
bestanden. Es wurde kein Recht erteilt oder SQL ausgeführt. Formale T-SQL-,
Methoden- und Runtimegates bleiben offen.
PR #441 bindet beide Qualification-Preflight-Statuszeilen und ihre PRINT-Marker.
Drei Negativregressionen für Skip-Outcome, Erfolgs-Outcome und Skip-Print werden
abgewiesen; 29 QRY-023-Regressionen und die statischen Projektvalidatoren
bestanden. Keine Rechteänderung oder SQL-Ausführung.
PR #443 bindet Systemdatenbankausschluss und den `DB_NAME()`/
`@TargetDatabase`-Abgleich vor der Rechteprüfung. Zwei Negativfälle werden
abgewiesen; 31 QRY-023-Regressionen und die statischen Projektvalidatoren
bestanden nach Korrektur eines lokalen Validatorfehlers. Keine Datenbank- oder
Rechteänderung und kein SQL-Lauf.
PR #445 bindet die vier Ownership-Markerzuweisungen und vollständigen Vergleiche
vor der Rechteprüfung; Projektwert- und RunToken-Negativproben werden
abgewiesen. 33 QRY-023-Regressionen und die statischen Projektvalidatoren
bestanden. Tatsächliche Datenbankmarker wurden nicht gelesen oder verändert.
Der nächste ausgewählte Offline-Schnitt bindet im read-only Preflight den
erwarteten Ziel-Datenbanknamen an Demo-ID und RunToken und schützt die
Längen-/Zeichenmengenprüfung des Tokens durch Negativregressionen. Er erweitert
den kumulativen Rahmen um 1 Arbeitspaket, 2 PRs und höchstens 2
Quellen-/Testkandidaten auf 83/110/193. SQL-/Runtime-/Lab-Ausführung,
Rechteänderungen und menschliche Generalprobe bleiben ausgeschlossen.
PR #447 ergänzt die statische Bindung und drei Gegenproben; 36
QRY-023-Regressionen und die betroffenen Validatoren bestanden. Damit bleibt
der Datenbank- und Runtimezustand unberührt.
Als nächstes bindet ein eigenständiger Offline-Schnitt die boolesche
`OR`-Verknüpfung aller Vertragsguards, damit jede einzelne ungültige Eingabe
zum Abbruch führt. Er erhöht den kumulativen Rahmen um 1 Arbeitspaket, 2 PRs
und höchstens 2 Quellen-/Testkandidaten auf 84/112/195. Keine SQL-/Runtime-/
Lab-Ausführung oder menschliche Generalprobe.
PR #449 bindet die vollständige Guardklausel und weist die `AND`-Gegenprobe ab;
37 QRY-023-Regressionen und die betroffenen statischen Validatoren bestanden.
Die nächste begrenzte Prüfung ergänzt eine `DATALENGTH`-Grenze für das
RunToken, weil `LEN` und ASCII-`LIKE` laut Microsoft-Dokumentation trailing
spaces auslassen. Eine Negativprobe lockert die Byteobergrenze. Kumulativ
85/114/197; Quellen: Microsoft Learn zu [`LEN`](https://learn.microsoft.com/en-us/sql/t-sql/functions/len-transact-sql?view=sql-server-ver17) und [`LIKE`](https://learn.microsoft.com/en-us/sql/t-sql/language-elements/like-transact-sql?view=sql-server-ver17), abgerufen am 8. November 2026. Keine Engineausführung.
PR #451 bindet `DATALENGTH(@RunToken) NOT BETWEEN 1 AND 20`; eine gelockerte
Byteobergrenze wird durch die statische Negativregression abgewiesen. 38
QRY-023-Regressionen und die betroffenen Validatoren bestanden. Es wurde kein
SQL ausgeführt.
Als nächstes dokumentiert ein begrenzter Schnitt die SQLCMD-Eingabegrenze:
Aufrufer müssen Demo-ID, RunToken und Zielnamen vor SQLCMD allowlisten, da die
T-SQL-Guards erst nach Skriptvariablen-Einsetzung greifen. Dies folgt als
Sicherheitsinferenz aus den Microsoft-Beispielen zur SQLCMD-Skriptvariablen-
Einsetzung. Kumulativ 86/116/199; keine Runtimeautorisierung oder Ausführung.
PR #452 dokumentiert den ausstehenden Caller-Schutz und prüft, dass die
SQLCMD-Eingabegrenze im Demo-Lesepfad genannt bleibt. Eine Negativregression
entfernt die Schutzformulierung; 39 QRY-023-Regressionen und betroffene
Validatoren bestanden. Die Eingabeinjektionsbewertung bleibt eine
quellenbasierte Inferenz, keine Laufbeobachtung.

Der nächste Offline-Schnitt überführt diesen Schutz in ein maschinenlesbares
Manifestobjekt mit exakter Demo-ID, RunToken-Muster, Zielnamenschablone und
Validierungszeitpunkt vor SQLCMD. Der Offlinevalidator bindet die vollständigen
Werte. Kumulativ 87/118/201; kein SQLCMD-Aufruf und keine Runtime- oder
menschliche Generalprobe.
PR #455 integriert `sqlcmd_input_validation`; Gegenproben ändern Prüfzeitpunkt
und Tokenzeichensatz und werden abgewiesen. 41 QRY-023-Regressionen sowie die
betroffenen Projektvalidatoren bestanden. Das Feld bleibt eine Vorgabe für
einen späteren Caller.

PR #457 integriert die optionale Vertragsprüfung vor `resolve_sqlcmd`; die
synthetischen Tests lehnen geänderten Vertrag und bösartigen Token vor jedem
SQLCMD-Prozess ab. Der QRY-023-Manifestentwurf bleibt dennoch nicht
katalogisiert und ungeprüft gegen SQL Server.

PR #458 integriert die RunToken-Vertragsangleichung. Die vollständige CI
endete mit 20/22 erfolgreichen Workflows; zwei unabhängige DGN-007-
Quellenprofilchecks meldeten `PYTHON_PROFILE_CHANGED`. Alle übrigen
Framework-/Runtimeworkflows, einschließlich SQL Server 2025 AI, waren nach
regulärem Abschluss erfolgreich. Kumulativ höchstens 89 Arbeitspakete, 122
PRs und 204 Quellen-/Testkandidaten.

Nachreview zeigte, dass diese Negativregression noch nicht aus der
Testmodul-`main()`-Funktion aufgerufen wurde; der grüne Modultest belegte den
Einzelfall somit nicht. PR #459 registriert und führt `_LOCAL` explizit aus;
der erneute Modultest und alle fünf ausgelösten Workflows bestanden. Die
Ablehnung geschieht vor SQLCMD-Auflösung und -Start. Kumulativ höchstens 90
Arbeitspakete, 124 PRs und 205 Quellen-/Testkandidaten. Keine SQL- oder
Runtimeausführung.

PR #460 ergänzt die ausgeführten synthetischen Caller-Grenzen: gültige
1-/20-Zeichenwerte werden geladen; leere, überlange, nicht-ASCII-,
kleingeschriebene und nachgestellte-Leerzeichen-Token scheitern vor SQLCMD-
Auflösung/-Start. Die QRY-023-, FWK-010- und Repository-Continuity-Prüfungen
bestanden. Kumulativ höchstens 91 Arbeitspakete, 126 PRs und 206 Quellen-/
Testkandidaten. Keine Engine- oder Runtimeausführung.

PR #461 prüft den konkreten `run_token`-Wert im vorgeschlagenen Manifest gegen
dieselbe ASCII-/Zeichen-/Längengrenze, die das maschinelle Caller-Vertragsobjekt
deklariert. Vier Negativproben für Unterstrich am Anfang, Länge, ASCII und
nachgestelltes Leerzeichen bestanden. Kumulativ höchstens 92 Arbeitspakete,
128 PRs und 207 Quellen-/Testkandidaten. Keine Engine- oder Runtimeausführung.

PR #462 ergänzt Negativregressionen für unbekannte Zusatzfelder im exakten
Vertragsobjekt und einen booleschen Wert im Byte-Limit. Beide werden vor
SQLCMD-Auflösung und -Start abgewiesen; alle sechs direkten CI-Workflows waren
grün. Kumulativ höchstens 93 Arbeitspakete, 130 PRs und 208 Quellen-/
Testkandidaten. Keine Vertragsausweitung, Engine- oder Runtimeausführung.

PR #463 pinnt synthetisch die exakte Vertrags-Demo-ID und Zielnamenschablone;
beide veränderten Werte scheitern vor SQLCMD-Auflösung und -Start. Alle fünf
Workflows bestanden. Kumulativ höchstens 94 Arbeitspakete, 132 PRs und 209
Quellen-/Testkandidaten. Keine Runtimeausführung.

PR #464 legt den QRY-023-Vertrag in ein `OPT-001`-Manifest; der Demo-Scope
wird vor SQLCMD-Auflösung und -Start fail-closed durchgesetzt. Alle fünf
Workflows bestanden. Kumulativ höchstens 95 Arbeitspakete, 134 PRs und 210
Quellen-/Testkandidaten. Keine Runtimeausführung.

PR #465 trennt die vom FWK-010-Caller erzwungene alphanumerische
Startzeichenregel von Zeichensatz- und Bytegrenze des vorgeschlagenen
SQL-Preflights. Die Negativregression, 43 QRY-023-Tests und alle sieben
ausgelösten Workflows bestanden. Kumulativ höchstens 96 Arbeitspakete, 136 PRs
und 211 Quellen-/Testkandidaten. Keine SQL- oder Runtimeausführung.

PR #466 setzt den exakten QRY-023-Vertrag in ein `OPT-001`-Manifest; der
Demo-ID-Scopekonflikt wird vor SQLCMD-Auflösung und -Start abgewiesen. Alle
fünf Workflows bestanden. Kumulativ höchstens 97 Arbeitspakete, 138 PRs und
212 Quellen-/Testkandidaten. Keine Runtimeausführung.

PR #467 ersetzt `sqlcmd_input_validation` synthetisch durch eine Liste; die
Zurückweisung vor SQLCMD-Auflösung und Prozessstart sowie die übrigen
Manipulationsgegenproben bestanden. Alle fünf Workflows waren grün. Kumulativ
höchstens 98 Arbeitspakete, 140 PRs und 213 Quellen-/Testkandidaten. Keine
Runtimeausführung.

PR #468 entfernt die doppelte Definition/Registrierung des `OPT-001`-Scope-
Tests und ergänzt eine Driftprobe für `target_database_name()`. Ein vom
Manifesttemplate abweichender Zielname wird vor SQLCMD abgewiesen; alle fünf
Workflows bestanden. Kumulativ höchstens 99 Arbeitspakete, 142 PRs und 214
Quellen-/Testkandidaten.

PR #469 vergleicht die per AST gefundenen `test_*`-Definitionen mit den
Aufrufen in `main()` und verlangt eine exakte Eins-zu-eins-Registrierung. Der
Runner-Test und alle fünf Workflows bestanden. Kumulativ höchstens 100
Arbeitspakete, 144 PRs und 215 Quellen-/Testkandidaten.

PR #470 führt denselben AST-Wächter gegen synthetische Fälle mit korrekter,
fehlender und doppelter Registrierung sowie doppelter Definition aus. Der
Runner-Test und alle fünf Workflows bestanden. Kumulativ höchstens 101
Arbeitspakete, 146 PRs und 216 Quellen-/Testkandidaten.

PR #471 ergänzt Fälle mit fehlendem und doppeltem `main()` und einem Aufruf
eines nicht definierten Testnamens; die Gegenproben wurden erkannt. Der
Runner-Test und alle fünf Workflows bestanden. Kumulativ höchstens 102
Arbeitspakete, 148 PRs und 217 Quellen-/Testkandidaten.

PR #472 ignoriert Testaufrufe in verschachtelten Funktionen und Lambdas; ein
solcher Hilfsaufruf verdeckt keine fehlende `main()`-Registrierung. Der
Runner-Test und alle fünf Workflows bestanden. Kumulativ höchstens 103
Arbeitspakete, 150 PRs und 218 Quellen-/Testkandidaten.

PR #473 zählt nur direkte, unbedingte Testaufrufe in `main()` und dessen
`with`-Blöcken. Eine `if False`-Gegenprobe kaschiert keine fehlende
Registrierung. Der Runner-Test und alle fünf Workflows bestanden. Kumulativ
höchstens 104 Arbeitspakete, 152 PRs und 219 Quellen-/Testkandidaten.

PR #474 berücksichtigt nur synchrone `test_*`-Definitionen als Registrierung;
ein nicht-awaited Aufruf einer Coroutine wird als fehlende Registrierung
abgewiesen. Alle fünf ausgelösten Workflows bestanden. Die bisherige
Obergrenze 105/154/220 ist erreicht. Für den Schattenfall einer gleichnamigen
`def`-/`async def`-Definition erweitert die autonome Fortsetzung den
kumulativen Rahmen einmalig um ein Arbeitspaket, einen PR und einen
synthetischen Kandidaten auf höchstens 106/155/221. Der Wächter muss die
überschreibende asynchrone Definition als Namensduplikat zurückweisen. Keine
SQL-/Runtimeausführung oder menschliche Generalprobe.

PR #475 integriert die eindeutige Erkennung gleichnamiger synchroner und
asynchroner `test_*`-Definitionen; alle fünf Workflows bestanden. Als nächste
Fortsetzung wird der Rahmen ohne Reset einmalig um ein Paket, einen PR und
einen synthetischen Testkandidaten auf höchstens 107/156/222 erweitert. Die
Gegenprobe definiert erst eine synchrone `main()` und überschreibt sie danach
mit `async def main()`; der AST-Wächter muss den Einstiegspunkt fail-closed
ablehnen. Keine SQL-/Runtimeausführung oder menschliche Generalprobe.

PR #476 integriert die Zurückweisung der asynchronen `main()`-Überschreibung;
alle fünf Workflows bestanden. Die Fortsetzung erweitert den Rahmen ohne Reset
um ein Arbeitspaket, einen PR und einen Testkandidaten auf höchstens 108/157/223.
Der Wächter prüft nun auch den direkten Modulaufruf unter dem
`__main__`-Guard und die Weitergabe des Rückgabecodes über
`raise SystemExit(main())`. Keine SQL-/Runtimeausführung oder menschliche
Generalprobe.

PR #477 bindet die Modulstartbedingung und die Weitergabe des `main()`-
Rückgabecodes. Alle fünf Workflows bestanden. Der kumulative Rahmen wird für
die drei synthetischen Gegenproben ohne Reset um ein Arbeitspaket, einen PR
und bis zu drei Testkandidaten auf höchstens 109/158/226 erweitert: umgedrehte
`__name__`-Bedingung, direkter Aufruf ohne `SystemExit` und Funktionsreferenz
statt Funktionsaufruf. Keine SQL-/Runtimeausführung oder menschliche
Generalprobe.

PR #478 integriert alle drei negativen Guardformen; alle fünf Workflows
bestanden. Die autonome Fortsetzung erweitert das kumulative Budget ohne Reset
um ein Arbeitspaket, einen PR und einen Testkandidaten auf höchstens
110/159/227. Ein zusätzliches ungeschütztes `main()` auf Modulebene darf keinen
zweiten oder vorzeitigen Testrun auslösen. Keine SQL-/Runtimeausführung oder
menschliche Generalprobe.

PR #479 integriert den Schutz vor ungeschützten Aufrufen; alle fünf Workflows
bestanden. Der nächste einzelne Kandidat erweitert den kumulativen Rahmen ohne
Reset um ein Paket, einen PR und einen Test auf höchstens 111/160/228. Auch
innerhalb des einzigen `__main__`-Guards darf `main()` genau einmal aufgerufen
werden. Keine SQL-/Runtimeausführung oder menschliche Generalprobe.

PR #480 integriert die Prüfung auf genau einen Guard-Aufruf; alle fünf
Workflows bestanden. Der nächste Schnitt erweitert das Budget ohne Reset um
ein Paket, einen PR und bis zu drei Testkandidaten auf höchstens 112/161/231.
Ungeschützte `main()`-Aufrufe in Klassenbasen, Funktionsstandardwerten und
Dekoratoren müssen als Importzeitaufrufe erkannt werden. Keine SQL-/Runtime-
Ausführung oder menschliche Generalprobe.

PR #481 integriert die Prüfung der Importzeit-Auswertungsstellen; alle fünf
Workflows bestanden. Für ungeschützte Aliasreferenzen auf `main` erweitert sich
der kumulative Rahmen ohne Reset um ein Arbeitspaket, einen PR und einen
Testkandidaten auf höchstens 113/162/232. Der Test nutzt die Aliaszuweisung
`runner = main`. Keine SQL-/Runtimeausführung oder menschliche Generalprobe.

PR #482 integriert die Aliasprüfung; alle fünf Workflows bestanden. Der nächste
Schnitt erweitert das Budget ohne Reset um ein Arbeitspaket, einen PR und zwei
synthetische Gegenproben auf höchstens 114/163/234. Dynamische Aufrufe über
`globals()["main"]()` und `getattr(globals(), "main")()` werden außerhalb des
Guards zurückgewiesen. Keine SQL-/Runtimeausführung oder menschliche
Generalprobe.

PR #483 integriert diese beiden Formen; alle fünf Workflows bestanden. Zwei
weitere synthetische Gegenproben für `locals()["main"]()` und `vars()["main"]()`
erweitern den Rahmen ohne Reset um ein Paket, einen PR und zwei Testkandidaten
auf höchstens 115/164/236. Keine SQL-/Runtimeausführung oder menschliche
Generalprobe.

PR #484 integriert die lokalen Mappingformen; alle fünf Workflows bestanden.
Der nächste Schnitt erweitert den Rahmen ohne Reset um ein Arbeitspaket, einen
PR und zwei Testkandidaten auf höchstens 116/165/238. Direkte Testaufrufe nach
`return` oder `raise` im `main()`-Ablauf gelten als unerreichbar und dürfen die
Vollständigkeitsprüfung nicht bestehen. Keine SQL-/Runtimeausführung oder
menschliche Generalprobe.

PR #485 integriert die beiden Kontrollflussenden; alle fünf Workflows
bestanden. Für vier direkte Prozessendeaufrufe erweitert sich der Rahmen ohne
Reset um ein Paket, einen PR und vier synthetische Testkandidaten auf höchstens
117/166/242. `exit()`, `quit()`, `sys.exit()` und `os._exit()` dürfen danach
liegende Testaufrufe nicht als ausgeführt zählen lassen. Keine SQL-/Runtime-
Ausführung oder menschliche Generalprobe.

PR #486 integriert die vier direkten Exitformen; alle fünf Workflows bestanden.
Der nächste Schritt erweitert den kumulativen Rahmen ohne Reset um ein Paket,
einen PR und zwei Testkandidaten auf höchstens 118/167/244. Importierte oder
umbenannte `sys.exit`-Aufrufe beenden den Kontrollfluss ebenfalls. Keine
SQL-/Runtimeausführung oder menschliche Generalprobe.

PR #487 integriert beide `sys.exit`-Aliasfälle; alle fünf Workflows bestanden.
Für drei weitere Aliasfälle erweitert sich das Budget ohne Reset um ein
Arbeitspaket, einen PR und drei Testkandidaten auf höchstens 119/168/247:
`builtins.exit`, `os._exit` und ein `os`-Modulalias. Keine SQL-/Runtime-
Ausführung oder menschliche Generalprobe.

PR #488 integriert alle drei Aliase; alle fünf Workflows bestanden. Der nächste
Schnitt erweitert den Rahmen ohne Reset um ein Paket, einen PR und einen
Testkandidaten auf höchstens 120/169/248. Ein `sys.exit()` als einfache
Zuweisung beendet den Kontrollfluss ebenfalls; folgende Tests gelten als
unerreichbar. Keine SQL-/Runtimeausführung oder menschliche Generalprobe.

PR #489 integriert die einfache Zuweisungsform; alle fünf Workflows bestanden.
Der nächste Schnitt erweitert den Rahmen ohne Reset um ein Paket, einen PR und
einen Testkandidaten auf höchstens 121/170/249. Ein Prozessende in einer
erweiterten Zuweisung wie `status += sys.exit()` muss ebenfalls als Ende erkannt
werden. Keine SQL-/Runtimeausführung oder menschliche Generalprobe.

PR #490 integriert die erweiterte Zuweisung; alle fünf Workflows bestanden.
Der nächste Schnitt erweitert den Rahmen ohne Reset um ein Paket, einen PR und
einen Testkandidaten auf höchstens 122/171/250. Die annotierte Zuweisung
`result: int = sys.exit()` erhält eine eigene synthetische Gegenprobe. Keine
SQL-/Runtimeausführung oder menschliche Generalprobe.

PR #491 integriert die annotierte Zuweisung; alle fünf Workflows bestanden.
Der nächste Schnitt erweitert den Rahmen ohne Reset um ein Paket, einen PR und
drei Testkandidaten auf höchstens 123/172/253. Prozessendeaufrufe innerhalb von
Tupel-, Listen- und Dictionary-Literalen müssen als eager ausgewertet erkannt
werden. Keine SQL-/Runtimeausführung oder menschliche Generalprobe.

PR #492 integriert die drei eager Literalformen; alle fünf Workflows bestanden.
Der nächste Schnitt erweitert den Rahmen ohne Reset um ein Paket, einen PR und
einen Testkandidaten auf höchstens 124/173/254. Eine bedingte Exit-Auswertung
innerhalb eines Zuweisungswerts darf einen nachfolgenden Test nicht als
unbedingt erreichbar ausweisen. Keine SQL-/Runtimeausführung oder menschliche
Generalprobe.

PR #493 integriert den bedingten Zuweisungsfall; alle fünf Workflows bestanden.
Der nächste Schnitt erweitert den Rahmen ohne Reset um ein Paket, einen PR und
einen Testkandidaten auf höchstens 125/174/255. Ein Prozessende in einer
`if`-Verzweigung darf einen späteren Test nicht als auf allen Pfaden
ausführbaren Aufruf bestehen lassen. Keine SQL-/Runtimeausführung oder
menschliche Generalprobe.

PR #494 integriert den `if`-Abbruchpfad; alle fünf Workflows bestanden. Für
Schleifen, `try`/`except`, `match` und `with` erweitert sich der Rahmen ohne
Reset um ein Arbeitspaket, einen PR und fünf Testkandidaten auf höchstens
126/175/260. Mögliche Prozessenden innerhalb dieser Kontrollflussblöcke dürfen
spätere Tests nicht als unbedingt ausführbar bestehen lassen. Keine
SQL-/Runtimeausführung oder menschliche Generalprobe.

PR #495 integriert die fünf Pfadfälle; alle fünf Workflows bestanden. Der
nächste Schnitt erweitert den Rahmen ohne Reset um ein Paket, einen PR und
einen Testkandidaten auf höchstens 127/176/261. Nicht aufgerufene verschachtelte
Funktionskörper werden bei der Prozessende-Pfadanalyse ignoriert; ihre
Dekoratoren, Defaults und Annotationen bleiben als beim Definieren ausgewertete
Ausdrücke berücksichtigt. Keine SQL-/Runtimeausführung oder menschliche
Generalprobe.

PR #496 integriert das Überspringen unaufgerufener Funktionskörper; alle fünf
Workflows bestanden. Für Prozessenden in ausgeführten Helper-Dekoratoren oder
Defaults erweitert sich der Rahmen ohne Reset um ein Paket, einen PR und zwei
Testkandidaten auf höchstens 128/177/263. Diese Ausdrücke laufen bereits bei
der Definition des Helpers. Keine SQL-/Runtimeausführung oder menschliche
Generalprobe.

PR #497 integriert die ausgeführten Helper-Header; alle fünf Workflows
bestanden. Für Klassenkörper und unaufgerufene Methoden erweitert sich der
Rahmen ohne Reset um ein Paket, einen PR und zwei Testkandidaten auf höchstens
130/179/265. Die Gegenproben trennen den ausgeführten Klassenkörper vom erst
bei Aufruf ausgeführten Methodenrumpf. Keine SQL-/Runtimeausführung oder
menschliche Generalprobe.

PR #498 integriert diese Auswertungsgrenze; alle fünf Workflows bestanden. Für
Generatorausdrücke erweitert sich der Rahmen ohne Reset um ein Arbeitspaket,
einen PR und zwei Testkandidaten auf höchstens 132/181/267. Der Generatorrumpf
ist aufgeschoben, das äußerste Iterable läuft beim Erzeugen. Keine
SQL-/Runtimeausführung oder menschliche Generalprobe.

PR #499 integriert die lazy Auswertungsgrenze; alle fünf Workflows bestanden.
Für Generatoren unter direktem Eager-Verbrauch erweitert sich der Rahmen ohne
Reset um ein Arbeitspaket, einen PR und zwei Testkandidaten auf höchstens
134/183/270. `list`, `tuple`, `set`, `sorted`, `sum`, `min`, `max`, `any` und
`all` führen den Generatorrumpf aus. Keine SQL-/Runtimeausführung oder
menschliche Generalprobe.

PR #500 integriert den Generatorverbrauch durch diese eingebauten Funktionen;
alle fünf Workflows bestanden. Für ausgeführte `map`-/`filter`-Callbacks
erweitert sich der Rahmen ohne Reset um ein Arbeitspaket, einen PR und zwei
Testkandidaten auf höchstens 136/185/273. Die Gegenproben unterscheiden einen
Callback bei Eager-Verbrauch von einem lazy `map` ohne Iteration. Keine
SQL-/Runtimeausführung oder menschliche Generalprobe.

PR #501 integriert die ausgeführten Lambda-Callbacks; alle fünf Workflows
bestanden. Für benannte synchrone `map`-/`filter`-Callbacks erweitert sich der
Rahmen ohne Reset um ein Arbeitspaket, einen PR und zwei Testkandidaten auf
höchstens 138/187/276. Eine benannte synchrone Funktion wird nur beim Eager-
Verbrauch ihres Iterators aufgerufen. Keine SQL-/Runtimeausführung oder
menschliche Generalprobe.

PR #502 integriert benannte synchrone Callbacks; alle fünf Workflows bestanden.
Für Generatoren direkt in `for`-/`async for`-Iteratoren erweitert sich der
Rahmen ohne Reset um ein Arbeitspaket, einen PR und zwei Testkandidaten auf
höchstens 140/189/279. Die Schleife konsumiert den Generator. Keine
SQL-/Runtimeausführung oder menschliche Generalprobe.

PR #503 integriert die Loop-Konsumierung; alle fünf Workflows bestanden. Für
Generatorfunktionen als `main` erweitert sich der Rahmen ohne Reset um ein
Arbeitspaket, einen PR und drei Testkandidaten auf höchstens 143/192/283.
`yield` im ausgeführten `main`-Pfad oder Helper-Header macht `main()` lazy;
ein verschachtelter Helper-Rumpf ändert das nicht. Keine SQL-/Runtimeausführung
oder menschliche Generalprobe.

PR #504 integriert die Prüfung von Generatorfunktionen als `main`; alle fünf
Workflows bestanden. Für die `yield from`-Gegenprobe erweitert sich der Rahmen
ohne Reset um ein Arbeitspaket, einen PR und einen Testkandidaten auf höchstens
144/193/285. `yield from` macht `main` lazy. Keine SQL-/Runtimeausführung oder
menschliche Generalprobe.

PR #505 integriert die `yield from`-Gegenprobe; alle fünf Workflows bestanden.
Für Modulstart-Prozessenden erweitert sich der Rahmen ohne Reset um ein
Arbeitspaket, einen PR und zwei Testkandidaten auf höchstens 146/195/288. Die
Gegenproben trennen direkte Importzeit-Ausführung von einem unaufgerufenen
Helper-Rumpf. Keine SQL-/Runtimeausführung oder menschliche Generalprobe.

PR #506 integriert Prozessenden beim Modulstart; alle fünf Workflows bestanden.
Für lokale Exit-Alias-Imports in `main()` erweitert sich der Rahmen ohne Reset
um ein Arbeitspaket, einen PR und zwei Testkandidaten auf höchstens 148/197/291.
`from sys import exit as stop` und `import sys as runtime` werden erkannt.
Keine SQL-/Runtimeausführung oder menschliche Generalprobe.

PR #507 integriert direkte lokale Exit-Imports; alle fünf Workflows bestanden.
Für bedingte Imports in `main()` erweitert sich der Rahmen ohne Reset um ein
Arbeitspaket, einen PR und zwei Testkandidaten auf höchstens 150/199/294.
Mögliche Exit-Imports in Kontrollflusszweigen werden erkannt; unaufgerufene
Helper-Rümpfe bleiben ausgenommen. Keine SQL-/Runtimeausführung oder
menschliche Generalprobe.

PR #508 integriert bedingte lokale Exit-Imports; alle fünf Workflows bestanden.
Für relative `.sys`-Imports erweitert sich der Rahmen ohne Reset um ein
Arbeitspaket, einen PR und zwei Testkandidaten auf höchstens 152/201/297. Nur
absolute Imports werden als Standardmodul `sys` erkannt. Keine
SQL-/Runtimeausführung oder menschliche Generalprobe.

PR #509 integriert die Abgrenzung relativer Imports; alle fünf Workflows
bestanden. Für lokale Überschreibungen von Exit-Aliasen erweitert sich der
Rahmen ohne Reset um ein Arbeitspaket, einen PR und zwei Testkandidaten auf
höchstens 154/203/300. Zuweisungen und lokale Definitionen ersetzen die
vorherige Aliasbindung. Keine SQL-/Runtimeausführung oder menschliche
Generalprobe.

### DGN-007 getrenntes Qualifikationsband

Der am 4. November integrierte Import-only-Worker ist begrenzte lokale
Komponentenevidenz. Ein nächster DGN-007-Schritt darf nur aus dem aktiven
kanonischen Status gewählt und auf einen einzelnen, statisch prüfbaren
Quell-/Vertragsschnitt begrenzt werden. Loader-/Parentregistrierung,
SESSION_END, tatsächlicher Kanal, operative Inventur, UsedBytes, Trust,
Consumption, Replay, unabhängiger Worker-Cleanup, SQL und Methodenfreigabe
bleiben getrennte Gates. Jeder PASS einer Komponente ist ausschließlich für
deren festgelegten Scope gültig; keine Komponente aktiviert automatisch den
nächsten Lauf.

Der aktuelle Offline-Schnitt verfolgt bereits erkannte importierte
Klassenaliase auch durch tatsächlich aufgerufene verschachtelte
Funktions-Closures. Der Folgeabgleich bindet den generierten
CPython-`stdlib_module_names.h`-Header digestgebunden: 301 statische Namen,
alle 93 Kandidatenwurzeln liegen darin. Das ist keine beobachtete
Laufzeiteigenschaft. `Python/frozen.c` ist nun ebenfalls digestgebunden und
liefert getrennte Tabellen für 3 Bootstrap-, 15 Stdlib- und 11 Testnamen sowie
neun Aliaszeilen. Auch dies sind nur deklarierte Quellwerte, keine Build- oder
Laufzeitbelege. Der Parser verlangt die C-Sentinels und weist nicht parsebare
Tabellenzeilen zurück; 92 synthetische Gegenproben bestehen. Zusätzlich ist
`Modules/Setup.bootstrap.in` gebunden: 22 eindeutige Zeilen, darunter das
bedingte `pwd` unter `MODULE_PWD_TRUE`; das ist keine Configure- oder
Buildfreigabe. `Modules/Setup.stdlib.in` ergänzt 68 reguläre und zwölf
getrennte Testmodulzeilen, alle 80 mit Configure-Bedingungen; diese sind keine
Aktivierungsbelege. `Modules/getpath.py` und `Lib/sysconfig.py` binden nun
zusätzlich Pfadvariablen/Configure-Schlüssel und fünf statische
Installationsschemas mit acht Pfadschlüsseln. Auch dies sind keine tatsächlichen
Prefix-, Pfad- oder Schemewerte. Der fokussierte Satz besteht nun 98/98. Als
nächste getrennte Offlinearbeit bleiben die übrigen 15
S15-Felder und P11-Recordquellen sowie danach das gemeinsame
Fünf-Formen-/64-KiB-Gate maßgeblich. Sie sind keine Laufzeitfreigabe und dürfen
nicht aus dem Kandidatenscan abgeleitet werden. Details und lokale Grenze
stehen im [aktuellen Ausführungsstand](CURRENT_EXECUTION_STATUS.md).

Die zwei gepinnten CPython-Importquellen `_bootstrap.py` und
`_bootstrap_external.py` sind inzwischen zusätzlich statisch auf acht
`ModuleSpec`-Initialisierungsfelder, Builtin-/Frozen-Importer sowie Datei-,
Namespace- und Pfad-Finder-/Loaderklassen abgebildet. Das ist Strukturwissen,
keine tatsächliche Spec-/Loaderinstanz und keine vollständige P11-Inventur.
Der fokussierte Satz besteht 99/99; der Kandidatenscan bleibt unverändert.
Die Quellen `Lib/importlib/machinery.py` und `Lib/importlib/util.py` binden nun
28 öffentliche API-Namen an ihre direkten Bootstrap-/External-Bootstrap-
Quellen oder lokale Definitionen; 100/100 fokussierte Tests bestehen. Auch
diese Zuordnung ist keine Zielimage-Installation oder P11-Recordinventur.
Die vorgepinnten `Modules/config.c.in`-/`configure.ac`-Vorlagen binden zusätzlich
neun feste Inittab-Basiseinträge und 14 Configure-Modulblock-Anker; 101/101
fokussierte Tests bestehen. Das belegt weder einen Configure-Lauf noch die
konkrete Builtin-/Extension-Aktivierung.
Die allgemeine Quellclosure verfolgt jetzt außerdem vorhandene Paketeltern und
konstante `__import__`-/`importlib.import_module`-Namen. Vier Quellenmodule
kommen hinzu (`concurrent`, `pydoc_data`, `xml`, `xmlrpc`); der neue
Closurehash lautet `700ace82b2c5630fc6ac039bb5bed0d788a46f6f8bcd1efba3fc0afb97068b6d`.
Berechnete und relative dynamische Namen bleiben offen; keine P11-Vollständigkeit.

### Gemeinsame Autonomie- und Stopregeln

- Ein Owner, höchstens zwei zusammenhängende Arbeitspakete je Fortsetzung und
  Checkpoint spätestens am dritten Quellenkandidaten oder beim ersten Blocker.
- Die bisherigen kumulativen Obergrenzen von 15 Arbeitspaketen, 23 Pull
  Requests und 57 Quellenkandidaten bleiben als Verbrauchsbasis erhalten.
  Der Nutzer autorisierte am 2026-11-06 zwei begrenzte Fortsetzungserweiterungen
  für die autonome Entwicklung, jeweils um ein Arbeitspaket, einen Pull Request
  und zwei Quellen-/Testkandidaten. Die kumulative Obergrenze beträgt nun
  17/25/61; kein Reset. Diese aktuelle Erweiterung gilt für den RES-001-Schnitt
  und wird am PR-/Integrationscheckpoint gegen den Stand geprüft.
  Mit der Fortsetzungsanweisung vom 2026-11-07 gilt für den nächsten
  eigenständigen RES-003-Offlineschnitt eine begrenzte Erweiterung um ein
  Arbeitspaket, einen Pull Request und zwei Quellen-/Testkandidaten. Die
  kumulative Obergrenze beträgt 18/26/63; kein Reset. Sie gilt ausschließlich
  für diesen Offlinevertrag und wird am Integrationscheckpoint abgeglichen.
  Die Fortsetzungsanweisung vom 2026-11-07 autorisiert am nächsten Checkpoint
  einen zusätzlichen, eigenständigen Dokumentationsschnitt mit weiteren
  1/1/2 Einheiten; die kumulative Obergrenze beträgt nun 19/27/65. Diese
  Erweiterung gilt für die quellengebundene RES-003-Lehrergänzung.
  Für die anschließende Detailprüfung des SQL-Server-2025-`OPTIMIZED_SP_EXECUTESQL`
  gilt nach der Fortsetzungsanweisung vom 2026-11-07 eine weitere klar begrenzte
  Erweiterung um ein Arbeitspaket, einen PR und zwei Quellenkandidaten; kumulativ
  höchstens 20/28/67, kein Reset. Sie deckt nur Quellenprüfung und dokumentarische
  Entscheidung ab, keine Featureaktivierung oder Runtime.
  Die nächste autonome Fortsetzung erweitert den begrenzten Rahmen um genau ein
  Arbeitspaket, einen Pull Request und zwei Quellenkandidaten; kumulativ höchstens
  21/29/69, ohne Reset. Diese Erweiterung gilt für die Offline-Quellen- und
  Abdeckungsprüfung zu Graph Tables. Sie autorisiert weder SQL-/Lab-Ausführung
  noch Demo-Implementierung oder Performanceaussage.
  Für die anschließende getrennte Graph-Table-Versions- und Indexprüfung galt
  eine begrenzte Erweiterung um 1 Arbeitspaket, 1 Pull Request und
  2 Quellenkandidaten; kumulativ höchstens 22/30/71, kein Reset. Sie erfasste
  zwei weitere Microsoft-Primärquellen und eine Offline-Dokumentation, ohne
  SQL-/Runtimefreigabe. Der Schnitt ist über PR #365 vollständig integriert.
  Die Curriculum-Zuordnung erweiterte den Rahmen um ein Arbeitspaket,
  einen Pull Request und bis zu zwei Quellenkandidaten auf kumulativ 23/31/73.
  Sie verwendete bestehende Projektquellen und begründete keine neue Lernziel-ID.
  Der Schnitt ist über PR #366 vollständig integriert.
  Für die Quellenprüfung der 2022/2025-Releaseübersichten gilt die nächste
  begrenzte Erweiterung um 1 Arbeitspaket, 1 Pull Request und 2 Quellenkandidaten;
  kumulativ höchstens 24/32/75. Sie bewertet nur die beiden Versionsübersichten
  und erteilte keine Kompatibilitäts- oder Laufzeitfreigabe. Der Schnitt ist
  über PR #367 integriert.
  Der statische Graph-Demoentwurf erweitert den Rahmen um ein Arbeitspaket,
  einen Pull Request und bis zu zwei Quellenkandidaten auf kumulativ 25/33/77.
  Er erstellt keine Demo-ID und erteilt keine SQL-/Runtimefreigabe.
  Der Syntaxreview für `MATCH` und Edge-INSERT erweitert den endlichen Rahmen
  um 1 Arbeitspaket, 1 PR und 2 Quellenkandidaten; kumulativ höchstens 26/34/79.
  Er bleibt auf Primärquellen und statische Dokumentation begrenzt.
  Die Fortsetzung nach der Syntaxprüfung erweitert den endlichen Rahmen um 1 Arbeitspaket, 1 PR und 2 Quellen-/Vertragskandidaten auf höchstens 27/35/81. Sie gilt für die Registrierung von `QRY-023` und den vollständigen statischen Vertrag; keine SQL-/Lab-Ausführung.
  Das Framework-/Curriculumreview setzt die autonome Fortsetzung um 1 Arbeitspaket, 1 PR und 2 Quellenkandidaten auf höchstens 28/36/83 fort. Es bindet die Projektprofile 2019/150, 2022/160, 2025/170 als Designziele und macht Plan-/Baseline-/Vergleichsmessung verpflichtend; keine Laufzeitfreigabe.
  Der Entwurf des deterministischen QRY-023-Messworkloads und die formale CLM-047-Traceabilityzuordnung erweitern die Obergrenze um 1 Arbeitspaket, 1 PR und 2 Kandidaten auf höchstens 29/37/85. Die Designprofile und Messmethodik sind weiterhin keine Graph-Runtimefreigabe.
  Das Quellen-/Methodenreview zu MATCH, Kandidatenindizes und getrennter Planevidenz erweitert die Obergrenze um 1 Arbeitspaket, 1 PR und 2 Kandidaten auf höchstens 30/38/87. Die unabhängige Methodenfreigabe bleibt ausdrücklich offen.
  Der initiale QRY-023-Harness-Codeentwurf erweitert die Obergrenze um 1 Arbeitspaket und 1 PR auf höchstens 31/39/89. Er bleibt nicht katalogisiert und ungefahren; statische Abnahme, unabhängige Methodenfreigabe und konkrete Runtimefreigabe sind getrennte weitere Gates.
  PR #374 integriert den QRY-023-Codeentwurf nach erfolgreichen Projektworkflows. Der statische allgemeine Cleanup-Eigentumstest lief in disposable SQL-Server-Containern für 2019, 2022 und 2025; QRY-023 selbst wurde nicht ausgeführt. Die nächste Welle ergänzt einen gezielten Offlinevertrag mit Regressionstests und eigenem nur statischen CI-Workflow. Die kumulative Obergrenze steigt um 1 Arbeitspaket, 1 PR und 2 Evidenzkandidaten auf 32/40/91. Diese Strukturprüfung schließt weder T-SQL-Kompilierbarkeit noch unabhängige Methodenfreigabe.
  PR #375 integriert den Offlinevalidator und seine Regressionstests; sämtliche PR-Gates waren grün. Die Editions-/Servicingprüfung für QRY-023 ergibt graphfähige Projekteditionen und bindet die zum 7.11.2026 neuesten dokumentierten Servicingbuilds als zeitgebundene Designpins ein. Preflight und Setup prüfen sie vor Mutation. Diese Fortsetzung erweitert den Rahmen um 1 Arbeitspaket, 1 PR und 2 Quellenkandidaten auf höchstens 33/41/93. Image-Digests, unabhängige Methodenfreigabe und Ausführung bleiben offen.
  PR #376 integriert das Editions-/Buildreview und die vor Setup erzwungenen ProductVersion-Pins. Der nächste Offline-Schnitt ergänzt ScriptDom `170.191.0` mit Lockfile und grammatikgebundenem Parse der ausführbaren QRY-023-Dateien für SQL Server 2019/2022/2025. Er schließt keine Engine-Kompilierung und keinen Runtimegate. Obergrenze: 34 Arbeitspakete, 42 PRs und 95 Quellenkandidaten.
  Der read-only MCR-Abgleich bindet die tatsächlichen Buildlabels und Manifestdigests der vorgesehenen Linux/AMD64-Images. Er ersetzt zwei Produktservicingpins in Preflight/Setup durch die dazu passenden CU-Imagebuilds und dokumentiert, dass diese 2019/2022 nicht die separat veröffentlichten GDR-Builds enthalten. Für den statischen Abgleich gilt eine begrenzte Erweiterung um 1 Arbeitspaket, 1 PR und 2 Quellenkandidaten; kumulativ höchstens 35/43/97. Kein Image wurde heruntergeladen oder gestartet.
  Der maschinenlesbare `container-images.proposed.json`-Lock und seine synthetischen Positiv-/Negativprüfungen erweitern den begrenzten Rahmen um weitere 1/1/2 Einheiten auf 36/44/99. Er bindet Profile, Labels und Digest-Referenzen statisch, ist noch nicht in einen Runtimeaufruf integriert und erteilt keine Laufberechtigung.
  Das vorgeschlagene Ressourcenprofil ergänzt Hersteller-Minimum, Hostreserve, harte Containergrenzen, SQL-Speicherlimit und bestehendes Zeit-/Cleanupbudget. Die zwei Microsoft-Quellen sowie die MCR-Layergrößen sind gebunden; die zusätzlichen 8/20-GiB-Host- und 4/3-GiB-Containerwerte bleiben ungemessene Projektannahmen. Begrenzte Erweiterung +1/1/2 auf kumulativ 37/45/101; kein Runtime- oder Ressourcenlauf.
  Der MCR-Tagabgleich findet GDR-spezifische Tags für 2019 und 2022, deren Image-Labels zu den neuesten Linux-CU+GDR-Builds passen. Lock und Preflight/Setup werden auf diese Tags und ihre neuen AMD64-Manifestdigests umgestellt; dies ist Registrymetadaten-, keine Engineevidenz. Begrenzte Erweiterung +1/1/2 auf kumulativ 38/46/103.
  PR #382 bindet QRY-023-Aufrufe, FWK-004-Prozedursignaturen und Messergebnis-Spalten mit zwei gezielten Offline-Regressionen an den bestehenden Framework-Contracts-Workflow. Alle zehn PR- und sieben relevanten Main-Workflows waren erfolgreich; kein QRY-023-SQL-Lauf. Begrenzte Erweiterung +1/1/2 auf 39/47/105.
  PR #383 integriert QRY-002-Lehrnotiz und Quellenregister nach fünf erfolgreichen PR-Gates und drei erfolgreichen Main-Workflows. Die Lehre trennt beide Konvertierungsrichtungen von konkreter Plan-/Zugriffswirkung. Begrenzte Erweiterung +1/1/2 auf 40/48/107.
  Der folgende QRY-003-Schnitt präzisiert `datetime`- und `datetime2(7)`-Tagesgrenzen, `BETWEEN`-Inklusivität, typed `DATEADD` und die empirische SARGability-Grenze; `SRC-133` wird ergänzt. Kein SQL-Lauf. Begrenzte Erweiterung +1/1/2 auf 41/49/109.
  PR #384 ist integriert; fünf PR-Gates und drei Main-Workflows waren erfolgreich. Der folgende RES-004-Quellenabgleich bindet Lehrnotiz, `SRC-010`, `SRC-110` und die neue `SRC-134` ohne DMV-Lauf zusammen. Begrenzte Erweiterung +1/1/2 auf 42/50/111.
  PR #385 integriert die RES-004-Quellenregisterpflege nach fünf erfolgreichen PR-Gates und drei erfolgreichen Main-Workflows. Der vollständige Lesepfad zeigt konsistente Lernziel-/Navigationsbezüge; der nächste Offlineentwurf konkretisiert QRY-003-Grenztupel und Ergebnisoracles. Begrenzte Erweiterung +1/1/2 auf 43/51/113.
  PR #386 integriert den QRY-003-Intervallentwurf nach vier erfolgreichen PR-Gates und zwei erfolgreichen Main-Workflows. Der nächste priorisierte Offlinekandidat ist QRY-007: Join-Kardinalität, `DISTINCT` und `EXISTS`, gebunden an `SRC-135`. Begrenzte Erweiterung +1/1/2 auf höchstens 44/52/115.
  PR #387 integriert QRY-007-Quellenbundle und Join-Kardinalitätsentwurf nach fünf erfolgreichen PR-Gates und zwei erfolgreichen Main-Workflows. PR #388 ergänzt die quellengebundene Lehrnotiz mit Fixture, Ergebnis-/Multiplizitätsoracle und Curriculum-Navigation; vier PR-Gates und zwei Main-Workflows waren erfolgreich. Begrenzte Erweiterung +1/1/2 auf 45/53/117.
  Für den nächsten priorisierten IDX-003-Schnitt gilt eine begrenzte Erweiterung +1 Arbeitspaket, +1 PR und +2 Quellen-/Testkandidaten auf höchstens 46/54/119. Sie gilt für Key-Reihenfolge, INCLUDE, vier Ergebnisoracles und eine Seitengrößengegenprobe; keine Plan- oder Performancefreigabe.
  PR #389 integriert den IDX-003-Entwurf nach fünf erfolgreichen PR-Gates und drei betroffenen Main-Workflows. Der nächste priorisierte Schnitt ist die `IDX-004`-Lookup-Kurve mit abgestufter Trefferzahl, nicht abdeckendem/abdeckendem Index, vollständigem Tupeloracle und ohne allgemeine Prozentgrenze. Begrenzte Erweiterung +1/1/2 auf höchstens 47/55/121.
  PR #390 integriert das IDX-004-Quellenbundle und den Selektivitäts-/Oracleentwurf; fünf PR-Gates und drei Main-Workflows waren erfolgreich. Der folgende Schritt bindet die Lookup-Erklärung in den Curriculum-Lesepfad, ohne einen Kippunkt oder Performancevorteil zu behaupten. Begrenzte Erweiterung +1/1/2 auf höchstens 48/56/123.
  Der Nutzer hat die autonome Fortsetzung ausdrücklich angeordnet und darauf hingewiesen, dass begrenzte Budgets bei kontinuierlicher Entwicklung fortgeschrieben werden müssen. Für den folgenden klar isolierten IDX-001-Offlineentwurf gilt deshalb eine neue, begrenzte Erweiterung um 1 Arbeitspaket, 1 Pull Request und höchstens 2 Quellenkandidaten auf kumulativ 49/57/125. Sie autorisiert keine SQL-/Runtimeausführung oder menschliche Generalprobe.
  PR #392 integriert den IDX-001-Entwurf nach fünf erfolgreichen PR-Gates und drei erfolgreichen Main-Workflows. Die fortlaufende autonome Entwicklung erhält für IDX-002 eine weitere begrenzte Erweiterung um 1 Arbeitspaket, 1 PR und höchstens 2 Quellenkandidaten auf kumulativ 50/58/127. Diese gilt ausschließlich für den statischen Quellen-/Designschnitt zur Clustered-Key-Breite und erteilt keine SQL-/Runtimefreigabe.
  PR #393 integriert IDX-002 mit fünf erfolgreichen PR-Gates und drei erfolgreichen Main-Workflows. Der folgende begrenzte Offlineentwurf STL-001 erweitert den fortlaufenden Auftrag um 1 Arbeitspaket, 1 PR und höchstens 2 Quellenkandidaten auf kumulativ 51/59/129. Es gibt keine SQL-/Runtimefreigabe oder Generalprobe.
  PR #394 integrierte STL-001 mit fünf erfolgreichen PR-Gates und drei erfolgreichen Main-Workflows. Für STL-002 galt eine weitere begrenzte Erweiterung um 1 Arbeitspaket, 1 PR und höchstens 2 Quellenkandidaten auf kumulativ 52/60/131; PR #395 ist mit fünf erfolgreichen PR-Gates und drei Main-Workflows integriert.
  PR #395 schloss den STL-002-Schnitt ab. Für QRY-005 galt eine Fortsetzungserweiterung um 1/1/2 auf kumulativ 53/61/133; PR #396 ist mit fünf erfolgreichen PR-Gates und drei Main-Workflows integriert. Der nächste OPT-004-Teilschnitt erweitert den Rahmen um 1/1/2 auf kumulativ 54/62/135. Er gilt ausschließlich für die Korrelations-/Mehrspaltenstatistikfrage und keine SQL-/Runtimeausführung.
  PR #396 schloss den QRY-005-Offlineentwurf ab. Für den begrenzten OPT-004-Korrelationsschnitt galt eine Fortsetzungserweiterung um 1 Arbeitspaket, 1 PR und höchstens 2 Quellenkandidaten auf kumulativ 54/62/135; PR #397 ist mit fünf erfolgreichen PR-Gates und drei Main-Workflows integriert.
  PR #397 schloss den OPT-004-Korrelations-/Mehrspaltenstatistikentwurf ab. Der noch offene Constraint-Vertrauens- und Eindeutigkeitsschnitt erweitert den fortlaufenden Rahmen um 1/1/2 auf kumulativ 55/63/137. Runtime, Cleanupqualifikation und menschliche Generalprobe bleiben ausgeschlossen.
  PR #398 integriert den getrennten OPT-004-Constraint-/Eindeutigkeitsschnitt nach fünf erfolgreichen PR-Gates und drei erfolgreichen Main-Workflows. Die Fortsetzung zu STL-003 erweitert den fortlaufenden Rahmen um 1/1/2 auf kumulativ 56/64/139. Sie umfasst ausschließlich Quellen- und Offlineentwurf zum Forwarded-Record-Lifecycle; keine SQL-/Runtimeausführung oder menschliche Generalprobe.
  PR #399 integriert STL-003 nach fünf erfolgreichen PR-Gates und drei erfolgreichen Main-Workflows. QRY-011 erhält eine weitere begrenzte Erweiterung um 1/1/2 auf kumulativ 57/65/141; Scope sind Quellenprüfung, synthetische vollständige Ergebnisoracles und ein statischer Entwurf zu Filtered Indexes, berechneter Spalte und einer SET-Option-Gegenprobe. Keine SQL-/Runtimeausführung, Planfreigabe oder menschliche Generalprobe.
  PR #400 integriert QRY-011 nach fünf erfolgreichen PR-Gates und drei erfolgreichen Main-Workflows. IDX-005 erhält eine weitere begrenzte Erweiterung um 1/1/2 auf kumulativ 58/66/143; Scope sind aktuelle Primärquellen und ein statischer Entwurf zur Prüfung zweier überlappender Missing-Index-Vorschläge, Indexkonsolidierung und DML-Trade-offs. Keine SQL-/Runtimeausführung, Indeximplementierung oder menschliche Generalprobe.
  PR #401 integriert IDX-005 nach fünf erfolgreichen PR-Gates und drei erfolgreichen Main-Workflows. OPT-012 erhält eine weitere begrenzte Erweiterung um 1/1/2 auf kumulativ 59/67/145; Scope ist ein quellengebundener Offlineentwurf zu Eligibility, Wiederverwendung desselben Plans, kleinem/großem Build-Input und Actual-Plan-Nachweisen. Keine SQL-/Runtimeausführung, adaptive Planformgarantie, Leistungsbehauptung oder menschliche Generalprobe.
  PR #402 integriert OPT-012 nach fünf erfolgreichen PR-Gates und drei erfolgreichen Main-Workflows. STL-010 erhält eine weitere begrenzte Erweiterung um 1/1/2 auf kumulativ 60/68/147; Scope sind aktuelle Primärquellen und ein statischer Entwurf zum Abgleich synthetischer Kompressionsprofile, Schätzungen in `tempdb` und tatsächlicher Seitenbelegung. Keine SQL-/Runtimeausführung, pauschale Editionsannahme, Leistungsrangfolge oder menschliche Generalprobe.
  PR #403 integriert STL-010 nach fünf erfolgreichen PR-Gates und drei erfolgreichen Main-Workflows. Der nächste begrenzte QRY-003-Schnitt erweitert die kumulative Obergrenze um 1/1/2 auf 61/69/149; er prüft vorhandene Datumsquellen und vervollständigt bei Bedarf den statischen Entwurf samt Ergebnistupeln für `datetime` und `datetime2(7)`. Keine SQL-/Runtimeausführung, Plan-/Leistungsbehauptung oder menschliche Generalprobe.
  PR #405 integriert QRY-003 nach vier erfolgreichen PR-Gates und zwei erfolgreichen Main-Workflows. QRY-007 erweitert den fortlaufenden Rahmen um 1/1/2 auf kumulativ 62/70/151; Umfang sind Quellenprüfung und vollständige statische Tupeloracles für One-to-many-Join, `DISTINCT`, `EXISTS` und angeforderte Kindaggregation. Keine SQL-/Runtimeausführung, pauschale `DISTINCT`-Empfehlung, Plan-/Leistungsbehauptung oder menschliche Generalprobe.
  PR #406 integriert QRY-007 nach fünf erfolgreichen PR-Gates und drei erfolgreichen Main-Workflows. IDX-003 erhält eine begrenzte Fortsetzungserweiterung um 1/1/2 auf kumulativ 63/71/153; Scope sind Quellenabgleich, Prüfung der statischen Fixturezählwerte und vollständige Tupeloracles für Key-Reihenfolge-/INCLUDE-Profile. Keine SQL-/Runtimeausführung, Seek-Garantie, Leistungsbehauptung oder menschliche Generalprobe.
  PR #408 integriert IDX-003 nach vier erfolgreichen PR-Gates und zwei erfolgreichen Main-Workflows. IDX-004 erhält eine begrenzte Erweiterung um 1/1/2 auf kumulativ 64/72/155; Scope sind Quellenprüfung, deterministische Fixtureformeln und vollständige Tupeloracles für die Lookup-Treffermengen auf BASE-, LOOKUP- und COVERING-Profilen. Kein SQL-/Runtimelauf, garantierter Lookup-/Scan-Übergang, Leistungsclaim oder menschliche Generalprobe.
  PR #410 integriert IDX-004 nach vier erfolgreichen PR-Gates und zwei erfolgreichen Main-Workflows. Die vollständige Fixtureformel, Bandintervalle und sortierten Tupeloracles sind gebunden; Plan-/Lookup-/Read-Befunde bleiben empirisch. IDX-001 erhält für die autonome Fortsetzung eine begrenzte Erweiterung um 1 Arbeitspaket, 2 PRs (Statusübergang und Entwurfsintegration) und bis zu 2 Quellenkandidaten auf kumulativ 65/74/157. Scope: aktuelle Quellenprüfung und vollständige Punkt-/Bereichsoracles für HEAP und CLUSTERED. Kein SQL-/Runtimelauf, keine Planformgarantie, Leistungsbehauptung oder menschliche Generalprobe.
  PR #412 integriert IDX-001 nach vier erfolgreichen PR-Gates und zwei erfolgreichen Main-Workflows. Die vollständigen Punkt-/Bereichsoracles sind für beide Row-Locator-Profile gebunden; Enginequalifikation und Planwahl bleiben offen. IDX-002 erhält für die autonome Fortsetzung eine begrenzte Erweiterung um 1 Arbeitspaket, 2 PRs (Statusübergang und Entwurfsintegration) und bis zu 2 Quellenkandidaten auf kumulativ 66/76/159. Scope: aktuelle Quellenprüfung, exakte Fixtureformeln und vollständige Ergebnistupeloracles für `NARROW_UNIQUE` und `WIDE_NONUNIQUE`. Keine SQL-/Runtimeausführung, Größen-/Leistungsbehauptung oder menschliche Generalprobe.
  PR #414 integriert IDX-002 nach vier erfolgreichen PR-Gates und zwei erfolgreichen Main-Workflows. Die vollständigen Fixtureformeln und Band-37-Tupeloracles sind gebunden; Größenmodell und gemessene Seiten bleiben getrennt. STL-001 erhält für die autonome Fortsetzung eine begrenzte Erweiterung um 1 Arbeitspaket, 2 PRs (Statusübergang und Entwurfsintegration) und bis zu 2 Quellenkandidaten auf kumulativ 67/78/161. Scope: aktuelle Quellenprüfung, vollständige Tupeloracles der vier kumulativen Heapprofile und Nachrechnung des Größenmodells. Keine SQL-/Runtimeausführung, Page-Density- oder Leistungsbehauptung oder menschliche Generalprobe.
  PR #416 integriert STL-001 nach vier erfolgreichen PR-Gates und zwei erfolgreichen Main-Workflows. Vollständige Ergebnistupeloracles, Verteilungen und Modellrechnungen sind gebunden; Heapseiten bleiben empirisch. STL-002 erhält eine begrenzte Erweiterung um 1 Arbeitspaket, 2 PRs (Statusübergang und Entwurfsintegration) und bis zu 2 Quellenkandidaten auf kumulativ 68/80/163. Scope: Quellenabgleich sowie exaktes Payload-/Padding-Oracle und kanonischer Tupelvergleich für INROW, ROW_OVERFLOW und LOB. Keine SQL-/Runtimeausführung, keine Allocation-Unit- oder Leistungsbehauptung und keine menschliche Generalprobe.
  Vor dem nächsten Start muss der Verbrauch anhand des aktuellen Status und
  der Integrationshistorie verifiziert werden; der zuletzt dokumentierte
  Startverbrauch 1/19/45 ist kein Nachweis des heutigen Restbudgets.
- Token- und Geldverbrauch bleiben unbekannt. Die endlichen Kandidaten-/PR-
  Obergrenzen begrenzen die Arbeit, sind aber keine behauptete Kostenmessung
  oder Provider-Ausgabensperre.
- Aufwand für den RES-003-Offlineschnitt: ein Prüfer und eine gezielte
  Testdatei wurden lokal einmal ausgeführt und im passenden PR- und
  Main-Workflow erneut geprüft; kein SQL-Lab-Trigger. Für die aktuelle
  Lehrergänzung werden die zwei direkt betroffenen Markdown-Lesepfade und ihre
  Microsoft-Quellen geprüft; keine Code- oder SQL-Ausführung.
  Für die `OPTIMIZED_SP_EXECUTESQL`-Detailprüfung wurden zwei Microsoft-
  Quellenstellen geprüft und die vorhandene `QRY-004`-Abnahme als Curriculum-
  Verbraucher abgeglichen; keine Code-, SQL- oder Runtimeausführung.
  Für den Graph-Table-Schnitt wurden die aktuelle Curriculum-Abdeckung und zwei
  Microsoft-Primärquellen geprüft; ein Planungsdokument und zwei bestehende
  Index-/Statuspfade wurden angepasst. Keine Code-, SQL- oder Runtimeausführung.
  Für die getrennte Graph-Versions-/Indexwelle wurden zwei Microsoft-Quellen,
  Review- und Statusnotiz sowie Backlog-/Planungspfade geprüft; kein Code-,
  SQL- oder Runtimeaufruf.
  Die Curriculum-Zuordnung glich `CURRICULUM_ARCHITECTURE.md`,
  `TRACEABILITY_MATRIX.md`, `SLIDE_STATEMENT_REGISTER.md` und den
  Masterimplementierungsplan ab; keine neuen Produktquellen, Code- oder
  SQL-Ausführung.
  Die 2022/2025-Übersichten werden auf Graph-Einträge geprüft; Abwesenheit in
  der Änderungsübersicht wird nicht als Abwesenheits- oder Paritätsbeweis
  ausgelegt. Keine Code- oder SQL-Ausführung.
  Der Graph-Demoentwurf wird an den zwei vorhandenen Microsoft-Einstiegsquellen
  und am Framework-Demovertrag abgeglichen; keine SQL-/Runtimeausführung und
  kein zusätzlicher Testlauf.
  Fehlende/fehlgeschlagene
  Evidenz wird lokal nur bei neuem Befund weiter untersucht. Ein Owner, keine
  zusätzliche Reviewkette und keine Subagenten; reale Token-/Geldmessung bleibt
  unbekannt.
- Nach jedem kohärenten Schnitt: relevante lokale Prüfungen und erforderliche
  unabhängige Prüfung, PR- und Main-Gates gemäß Projektregeln, Integration,
  Main-Synchronisierung und Branchbereinigung. Begonnene Arbeit nicht als
  abgeschlossen melden, solange diese Integrationsschritte offen sind.
- Bei FAIL, fehlender Evidenz, unbekanntem Zustand, veraltetem Quellenbinder,
  verbrauchter Obergrenze oder nicht erfülltem Gate: keine Folgeausführung.
  Fehler nicht weginterpretieren und unveränderte Kandidaten nicht wiederholen.
  Den Blocker mit Wiederaufnahmebedingung im kanonischen Ausführungsstand
  vermerken.

Die Umsetzung dieser Planung selbst ist keine Aufforderung, nach Abschluss
dieses Planungsdokuments autonom mit Arbeitspaket 1 fortzufahren. Eine spätere
Fortsetzung muss am dann aktuellen Status und der dort wirksamen Autorisierung
ansetzen.

## Historischer Planungsstand vom 20. Oktober 2026

Der damalige Benutzerauftrag nahm nach Bestandsprüfung die
allgemeine Entwicklung wieder auf. Der interne Capture-Vorschnitt war nach
[unabhängigem Review und aktueller CI](DGN_007_INTERNAL_CAPTURE_RECEIPT_REVIEW.md)
über PR255 integriert und vollständig bereinigt. Danach ist ausschließlich der
[SESSION_END-Entwurf §34](DGN_007_IMPORT_PROFILE_BINDING_DESIGN.md#34-session_end-counts-und-kanalhashpräbild)
aufgenommen: maximal zwei Entwurfsstände, Checkpoint nach dem ersten,
ein unabhängiger Designreview und aktuelle Dokumentationsgates. Frühere
ausgeschöpfte Quell-/Import-/Generatorwellen erhalten keine neuen Versuche.
Der Erststand `a6ca3f5…` ist unabhängig ohne Befunde geprüft, alle acht
Dokumentationsgates sind grün. PR256 führt den endgültigen Head-/Base- und
Main-Abschluss; der nächste Implementierungskandidat wäre erst danach ein
separat gewählter reiner Footer-/Trace-Matcher mit eigenen Quellen- und Testgates.
Die folgenden älteren Pausen-/G13-Planungsstände sind insoweit historisch.
Keine Automationaktivierung und keine operative Kanal-/Loader-/Worker- oder
SQLimplementierung in dieser Designwelle.

| Merkmal | Wert |
|---|---|
| Historischer Status zum damaligen Planungsstand | allgemeine Entwicklung `PAUSED`; PR68-Code `BLOCKED` durch damalige Runtimefehler; Prüfbericht und Abschlussprozess getrennt |
| Historischer Bezugsstand | 2026-10-08 |
| Ausgangsstand | Produktive Runtimeevidenz bis Pull Request 42; begrenzte DGN-007-Kontrollcaptures bis Pull Request 62 und prospektiver Prüfvertrag aus Pull Request 63 und skalarer Transport aus Pull Request 64 sowie begrenzter SQL-Producer aus Pull Request 65; Detailstand in `CURRENT_EXECUTION_STATUS.md` |
| Bezug | [Aktueller Ausführungsstand](CURRENT_EXECUTION_STATUS.md), `.ai/BACKLOG.md`, `MASTER_IMPLEMENTATION_PLAN.md` |
| Zweck | priorisierte, kleine Folgepakete; keine Aussage, dass die beschriebenen Inhalte bereits umgesetzt sind |

## 1. Planungsgrundlagen

Der gezielte Benutzerauftrag vom 2026-10-09 betrifft Prüfung und Abschluss von
PR 68 sowie DEC-069; der [G13-/PR-Review](DGN_007_G13_PR_REVIEW.md) führt diesen
isolierten Diagnoseschnitt. Er verlangt erfolgreiche relevante aktuelle CI (Continuous Integration; automatisierte Integrationsprüfungen),
ohne G13 oder die offene Methodenentscheidung zu ändern. Die nachfolgende
allgemeine Folgeplanung und die interne Capture-Rückgabe bleiben ausdrücklich
zurückgestellt.
Der aktuelle Reporter-Head `f9ec582…` scheiterte auf 2022 an SQL20 und auf
2025 an G13. Deshalb wird nur der geprüfte Befund und Abschlussprozess getrennt
integriert; der Code-PR ist vorübergehend geschlossen und sein Branch wegen
nicht übernommener Änderungen erhalten. Zusätzlicher Scopeentscheid angefragt;
kein Bypass und kein Wiederholen unveränderter Kandidaten bis grün.

Die Entwicklung wurde am 2026-10-07 nach der über PR 92 dokumentierten Pause
ausdrücklich mit den bisherigen Regeln wieder aufgenommen. Seit dem Benutzerstopp
vom 2026-10-08 gilt `PAUSED`: nur den bereits laufenden §33-DESIGN-/PR-Schnitt
vollständig integrieren und seinen eigenen Branch unabhängig bereinigen; danach
Orchestrator und Subagents beenden. Alle hier genannten Folgepakete einschließlich
SESSION_END sind bis zu einer neuen ausdrücklichen Wiederaufnahme zurückgestellt.
Der vollständige Einstieg samt offener Reihenfolge und geschützter ungemergter
Arbeit steht in [CURRENT_EXECUTION_STATUS.md §0](CURRENT_EXECUTION_STATUS.md#0-entwicklungspause-und-wiederaufnahme).
Der getrennte [Darstellungs- und Digestentwurf §10](DGN_007_IMPORT_PROFILE_BINDING_DESIGN.md#10-vollständig-erhaltender-darstellungs--und-digestentwurf)
liegt als `DESIGNED` vor. Die separat vorgewählte vollständige Kontrollfixture
und reine Größenprüfung in [§11](DGN_007_IMPORT_PROFILE_BINDING_DESIGN.md#11-separat-ausgewählte-vollständige-bootstrapfixture)
belegen 85 Records und gemeinsame Metadata von 17.127/17.113/17.091 Bytes:
Der Tupelkandidat überschreitet das unveränderte 16.384-Byte-Cap bei allen Ordinals.
Der separate [Stringpoolentwurf §12](DGN_007_IMPORT_PROFILE_BINDING_DESIGN.md#12-verlustfreier-stringpoolentwurf)
liegt als `DESIGNED` vor, mit eigenen lokalen Pools, vollständigen Formfeldern und
unveränderten Caps einschließlich höchstens 256 Poolwerten. Der eigene
[reine Pool-Sizer §13](DGN_007_IMPORT_PROFILE_BINDING_DESIGN.md#13-separater-reiner-stringpool-sizer)
bestand 37/37 isolierte Gegenproben ohne SKIP und die vollständige neue
3×5-Größenprüfung: maximal 9.389 Bytes einschließlich Header und 204 Poolwerte.
Unabhängige vollständige Nachrechnung und Feldrückgewinnung bestätigt; keine
erneute Aufnahme oder Nonce. Der getrennte experimentelle Codec-/Digestpfad im
[Vertrag §14](DGN_007_IMPORT_PROFILE_BINDING_DESIGN.md#14-separater-experimenteller-formcodec-und-design-digests)
bestand 41/41 isolierte Gegenproben ohne SKIP, unabhängigen Quell-/Testreview
und die vollständige Originalfixture: alle 3×5 Frames, Feldrückgewinnung,
kanonischer Repack und neun eigene Digestwerte. Gesamtausgabe
28.264/28.257/28.246 Bytes; unabhängig aus unveränderten Eingaben nachgerechnet,
ohne Codec-/Helper-Replay. Der eigene reine
[kombinierte Eingangsprototyp §15](DGN_007_IMPORT_PROFILE_BINDING_DESIGN.md#15-separater-experimenteller-kombinierter-eingangsrahmen)
bestand 34/34 isolierte Gegenproben ohne SKIP und die vollständige Originalfixture
mit drei Frames zu jeweils 140.226 Bytes: 9.389 Metadata einschließlich Header,
130.837 unveränderte Rawbodybytes. Vollständige tatsächliche Rückgewinnung,
Repack und unabhängige Stdlib-Nachrechnung ohne Replay bestanden.
Die konkrete operative [Bootstrap-/Kanalreihenfolge §16](DGN_007_IMPORT_PROFILE_BINDING_DESIGN.md#16-konkrete-operative-bootstrap--und-kanalreihenfolge)
liegt als `DESIGNED` vor. Der reine [Kontrollbootstrapquellengenerator §17](DGN_007_IMPORT_PROFILE_BINDING_DESIGN.md#17-reiner-generator-gehaltener-kontrollbootstrapquellen)
bestand 32/32 ausschließlich synthetische Gegenproben ohne SKIP unter CPython 3.12.14. Die getrennte [Sysconfig-Vorinitialisierung §18](DGN_007_IMPORT_PROFILE_BINDING_DESIGN.md#18-feste-sysconfig-vorinitialisierung-gehaltener-kontrollquellen) bestand 53/53 isolierte synthetische Gegenproben ohne SKIP unter CPython 3.12.14. Die private native Auswahl nach [§19](DGN_007_IMPORT_PROFILE_BINDING_DESIGN.md#19-private-auswahlgrundlage-vor-einer-vollständigen-operativen-inventur) ist mit genau einem begrenzten Versuch und unabhängigem Prozess-/Record-POST abgeschlossen. Die additive reine [Inline-Metadata-Syntaxquelle §20](DGN_007_IMPORT_PROFILE_BINDING_DESIGN.md#20-reine-additive-inline-metadata-syntaxquelle) bestand 80/80 isolierte synthetische Gegenproben ohne SKIP unter CPython 3.12.14; der erste Fixture-Label-Fehllauf bleibt getrennt dokumentiert. Die additive reine [Inline-Metadata-Semantikquelle §21](DGN_007_IMPORT_PROFILE_BINDING_DESIGN.md#21-reine-additive-inline-metadata-semantikquelle) bestand nach zwei engen Fixturekorrekturen 108/108 isolierte synthetische Gegenproben ohne SKIP unter CPython 3.12.14; der erste 106/108-Lauf bleibt getrennt dokumentiert. Vollständige deklarative M/IP/S15/P11/D9-Semantik, unveränderter benannter Originaldigest und Providerkohärenz sind geprüft. Die additive reine [Inline-Profilreporterquelle §22](DGN_007_IMPORT_PROFILE_BINDING_DESIGN.md#22-reiner-additiver-inline-profilreporter) bestand im einzigen isolierten Lauf 149/149 synthetische Gegenproben ohne SKIP unter CPython 3.12.14. Vollständige Scalarprojektion, eigener REPORTED-Pool, atomare begrenzte Records und getrennte Original-/Reportdigests sind geprüft; vier frühere Builder bleiben erhalten. Die reine begrenzte [Inline-Header-/Metadata-Aufnahme §23](DGN_007_IMPORT_PROFILE_BINDING_DESIGN.md#23-reine-begrenzte-inline-header-metadata-aufnahme) bestand im einzigen isolierten Lauf 174/174 synthetische Gegenproben ohne SKIP unter CPython 3.12.14. Exact-Chunktype-/Größenvorläufe, vollständige deklarative M-Semantik und atomare gehaltene Rückgabe sind geprüft; fünf frühere Builder bleiben erhalten. Die additive reine [K-Domain-/Commandquelle §24](DGN_007_IMPORT_PROFILE_BINDING_DESIGN.md#24-reine-k-domain-und-deklarativ-gebundene-commands) bestand im einzigen isolierten Lauf 209/209 synthetische Gegenproben ohne SKIP unter CPython 3.12.14. Vollständiger K8-/D9-Vorlauf, eigene headerfreie E4-K-Domain und atomare kanonische Commands gegen separat gehaltene Callerwerte sind geprüft; sechs bisherige Builder und 174 alte Tests bleiben erhalten. Die additive reine [Inline-Metadata-Callerquelle §25](DGN_007_IMPORT_PROFILE_BINDING_DESIGN.md#25-vollständiger-deklarativer-inline-metadata-callerabgleich) bestand nach zwei engen Fixturekorrekturen 243/243 isolierte synthetische Gegenproben ohne SKIP unter CPython 3.12.14; der erste 241/243-Lauf mit zwei Fehlern vor Matcheraufruf bleibt getrennt dokumentiert. Beide vollständigen Formen und Semantiken, zwei eigene Originalinputdigests und vollständiger Abgleich gegen separat gehaltene I7/W6/K8 sind geprüft; sieben bisherige Builder und 209 alte Tests bleiben erhalten. Die additive reine [Inline-Rawbodyaufnahme §26](DGN_007_IMPORT_PROFILE_BINDING_DESIGN.md#26-reine-begrenzte-aufnahme-deklarierter-rawbodies) bestand nach einer engen Fixturelabelkorrektur 272/272 isolierte synthetische Gegenproben ohne SKIP unter CPython 3.12.14; der erste 271/272-Lauf bleibt getrennt dokumentiert. Vollständige Formen und Größen vor Hashes, beide tatsächlichen D9 und neun Rawhashes vor Callerabgleich sowie atomare Originalbodyrückgabe sind geprüft; acht bisherige Builder und 243 alte Tests bleiben erhalten. Die additive reine [Profilrecord-Reassemblierung §27](DGN_007_IMPORT_PROFILE_BINDING_DESIGN.md#27-reine-begrenzte-reassemblierung-gehaltener-profilrecords) bestand im einzigen isolierten synthetischen Lauf 304/304 Gegenproben ohne SKIP unter CPython 3.12.14. Vollständige begrenzte Control-/Envelopeformen, interne Konsistenz, kanonische Controls und tatsächlicher Footerhash vor Callerordinal sowie atomare Originalrecordrückgabe sind geprüft; neun bisherige Builder und 272 alte Tests bleiben erhalten. Zwei enge Fixturelabelkorrekturen wurden vor dem ersten Lauf reviewt; kein ausgeführter Fehllauf. Die additive reine [Inline-Profil-Callerquelle §28](DGN_007_IMPORT_PROFILE_BINDING_DESIGN.md#28-vollständiger-deklarativer-inline-profilabgleich) bestand im einzigen isolierten synthetischen Lauf 341/341 Gegenproben ohne SKIP unter CPython 3.12.14. Beide vollständigen R4-Formen/Semantiken, Actual-Pool-Repack und vollständiger separater Callerabgleich sind geprüft; die Matchfunktion berechnet keinen SHA. Zehn frühere Builder und 304 alte Methoden bleiben erhalten. Vorreviewkorrekturen und genaue Grenzen stehen in §28. Die additive reine R→BODY_RELEASE-Planquelle aus §29 bestand im einzigen isolierten synthetischen Lauf 378/378 Gegenproben ohne SKIP unter CPython 3.12.14; elf alte Builder und 341 alte Methoden bleiben erhalten. Die additive reine INPUT_COMPLETE-Quelle aus §30 bestand im einzigen isolierten synthetischen Lauf 413/413 Gegenproben ohne SKIP unter CPython 3.12.14; zwölf alte Builder und 378 alte Methoden bleiben erhalten. Der vollständige Record-/Footer→R-Calleradapter aus §31 ist rein additiv implementiert und im isolierten synthetischen Lauf mit 460/460 PASS ohne SKIP geprüft; dreizehn alte Builder und 413 alte Methoden bleiben erhalten. Die eigene lokale [Ledgerkomponente §32.5](DGN_007_IMPORT_PROFILE_BINDING_DESIGN.md#325-eigene-lokale-synthetische-ledgerkomponente) ist im isolierten synthetischen Lauf mit 66/66 PASS ohne SKIP geprüft. Reservierungen, ganze Slot-/Zustandsbindung, sticky Fehler und einmaliger Fakecleanup sind lokal belegt; kein tatsächlicher Kanal-/Loader-/Absenznachweis. Der vollständige [Loaderrecordvertrag §33](DGN_007_IMPORT_PROFILE_BINDING_DESIGN.md#33-vollständige-deklarative-begin-complete-loaderrecords) liegt als DESIGNED vor. Nächster kleiner Schnitt ist ausschließlich der separate SESSION_END-DESIGN-Vertrag mit exakten Counts und nicht selbstreferentiellem Kanalhashpräbild. Tatsächlicher Kanal, Loader-/Parentregistrierungsadapter, operative Inventur und Fünf-Formen-/64-KiB-Gate bleiben offen.
Frische operative Auswahl, inline Empfang und Reporting, Parent-/Worker-Anbindung,
Loader, Consumption, Replay und unabhängig bereinigte eigene Worker bleiben
getrennte Gates; die charakterisierte Fixture ist keine operative Workerbaseline.
Die Wiederaufnahme ändert keine fachliche Freigabe oder offenen Methodengates.

- `QRY-004` (Optionale Filter, Recompile und dynamisches SQL), `DGN-003` (Abfragehistorie mit Query Store), `DGN-005` (Gezielte Ereigniserfassung mit Extended Events), `OPT-017` (Ungleich verteilte parallele Arbeit) und alle neun Demos aus `W-COV-001` besitzen aktuelle Matrixnachweise aus GitHub Actions.
- `WARN_EMPIRICAL_VARIANCE` ist nur dort als Freigabeausgang zulässig, wo der Demo-Vertrag die empirische Abweichung ausdrücklich beschreibt und alle invarianten Ergebnis-, Sicherheits- und Cleanup-Verträge erfüllt sind.
- Die Curriculum-Analyse verlangt kein neues Hauptmodul. Neue Arbeit erweitert deshalb nur bestehende Lernziele und Demo-IDs.
- Jede Welle ist ein eigenständiger, kleiner Pull Request mit klarer Runtime-, Quellen- und Safety-Grenze. Öffentliche Herstellerdokumentation wird erst nach dem Source-Register-Delta-Review zu Lehrinhalt.

Der reine begrenzte Header-/Metadata-Vorschnitt aus gehaltenen Chunks nach
[§23](DGN_007_IMPORT_PROFILE_BINDING_DESIGN.md#23-reine-begrenzte-inline-header-metadata-aufnahme)
ist implementiert und unabhängig geprüft: einziger isolierter Lauf mit
174/174 PASS ohne SKIP; fünf bisherige Builder und 149 alte Tests erhalten.
Die reine [K-Domain-/Commandquelle §24](DGN_007_IMPORT_PROFILE_BINDING_DESIGN.md#24-reine-k-domain-und-deklarativ-gebundene-commands)
ist im einzigen isolierten Lauf mit 209/209 PASS ohne SKIP geprüft;
sechs bisherige Builder und 174 alte Tests bleiben erhalten.
Die reine [Inline-Metadata-Callerquelle §25](DGN_007_IMPORT_PROFILE_BINDING_DESIGN.md#25-vollständiger-deklarativer-inline-metadata-callerabgleich)
ist nach zwei engen Fixturekorrekturen mit 243/243 PASS ohne SKIP geprüft;
sieben bisherige Builder und 209 alte Tests bleiben erhalten.
Die reine [Inline-Rawbodyaufnahme §26](DGN_007_IMPORT_PROFILE_BINDING_DESIGN.md#26-reine-begrenzte-aufnahme-deklarierter-rawbodies)
ist nach einer Fixturelabelkorrektur mit 272/272 PASS ohne SKIP geprüft;
acht bisherige Builder und 243 alte Tests bleiben erhalten.
Die reine [Profilrecord-Reassemblierung §27](DGN_007_IMPORT_PROFILE_BINDING_DESIGN.md#27-reine-begrenzte-reassemblierung-gehaltener-profilrecords)
ist im einzigen isolierten Lauf mit 304/304 PASS ohne SKIP geprüft;
neun bisherige Builder und 272 alte Tests bleiben erhalten. Zwei neue
Fixturelabelkorrekturen wurden vor dem ersten Lauf geprüft.
Die reine [Inline-Profil-Callerquelle §28](DGN_007_IMPORT_PROFILE_BINDING_DESIGN.md#28-vollständiger-deklarativer-inline-profilabgleich)
ist im einzigen isolierten Lauf mit 341/341 PASS ohne SKIP geprüft;
zehn bisherige Builder und 304 alte Tests bleiben erhalten.
Die additive reine [R→BODY_RELEASE-Planquelle §29](DGN_007_IMPORT_PROFILE_BINDING_DESIGN.md#29-deklarativer-rbody_release-plan)
ist im einzigen isolierten Lauf mit 378/378 PASS ohne SKIP synthetisch geprüft:
vollständige Actual-/Caller-R4- und unabhängige K8-Bindung vor Command-SHA,
gehaltene äußere Anker und atomare reine Rückgabe; elf alte Builder und
341 alte Methoden bleiben erhalten. Phasenlabels attestieren weder vorherige
Übergänge noch Einmalverbrauch. Der separate
[INPUT_COMPLETE-Recordvertrag §30](DGN_007_IMPORT_PROFILE_BINDING_DESIGN.md#30-deklarativer-input_complete-rückkanalrecord)
ist als reine additive Quelle implementiert und im einzigen isolierten Lauf mit
413/413 PASS ohne SKIP geprüft: vollständige Caller-/Receivedformen und Semantik,
kanonische Actualbytes, eigene vollständige K-Domainbindung und dominante POSTs.
Zwölf alte Builder und 378 alte Methoden bleiben erhalten. Der vollständige
[Record-/Footer→R-Calleradapter §31](DGN_007_IMPORT_PROFILE_BINDING_DESIGN.md#31-vollständiger-deklarativer-profilrecord-callerabgleich)
ist rein additiv implementiert und im isolierten synthetischen Lauf mit
460/460 PASS ohne SKIP geprüft; dreizehn alte Builder und 413 alte Methoden
bleiben erhalten. PR 118 ist vollständig integriert; geprüfte Basis ist
`f6559e084ebd660a41a503129f1a28c32be8848b`. Die getrennten CI-/Übernahme-/Cleanupbelege
stehen in [CURRENT_EXECUTION_STATUS.md §0](CURRENT_EXECUTION_STATUS.md#0-entwicklungspause-und-wiederaufnahme).
Die eigene lokale [Ledgerkomponente §32.5](DGN_007_IMPORT_PROFILE_BINDING_DESIGN.md#325-eigene-lokale-synthetische-ledgerkomponente)
ist mit 66/66 isolierten synthetischen Methoden ohne SKIP geprüft.
Der vollständige [Loaderrecordvertrag §33](DGN_007_IMPORT_PROFILE_BINDING_DESIGN.md#33-vollständige-deklarative-begin-complete-loaderrecords) liegt als DESIGNED vor. Nächster kleiner Schnitt ist ausschließlich der separate SESSION_END-DESIGN-Vertrag mit exakten Counts und nicht selbstreferentiellem Kanalhashpräbild. Tatsächlicher Kanal, Loader-/Parentregistrierungsadapter, operative Inventur und Fünf-Formen-/64-KiB-Gate bleiben offen.
Operativer Workerbetrieb und Ressourcen-Cleanup bleiben getrennte Gates.

## 2. Priorisierte Wellen

| Reihenfolge | Welle | Ziel und abgegrenzter Umfang | Akzeptanzkriterium |
|---:|---|---|---|
| 1 | `LABSCN-005/DGN-007` | Capstone erst als eigenen Schnitt planen, nachdem Query-Store-/XE-Pilot und `CON-006` (Zyklische Sperrkonflikte erkennen) praktisch wiederverwendbare Evidenz- und Mehrsession-Verträge liefern. | Incident, Alternativhypothesen, Zeitfenster, Reset, Quellen und Teilnehmerübergabe sind vollständig; keine versteckte Lösung in Teilnehmerartefakten. |
| 2 | nächster `LABSCN-005`-Einzelslice | Nur einen Kandidaten mit eigenem Quellen-, Safety- und Detailreview auswählen; keine pauschale Infrastrukturwelle. | Lernmehrwert, Providerbedarf, Reset, Cleanup und versionsgebundene Aussage sind vor Implementierung eindeutig. |
| 3 | weitere `LABINT-004`-Matrix | Nur für einen neu freigegebenen gelben Szenarioslice aktivieren. | Matrix und Cleanup prüfen ausschließlich die neue freigegebene Aussage. |

## 2.1 Umsetzungsstand der Wellen

| Welle | Status | Evidenzgrenze |
|---|---|---|
| `TSK-002` (Detailreview LABSCN-005/DGN-007: Capstone-Planungsschnitt mit Incident-, Hypothesen-, Zeitfenster-, Reset- und Teilnehmeruebergabevertrag) | `DECIDED_PLANNING` | Detailreview [LABSCN-005 – Detailreview DGN-007 (Planungsschnitt)](LABSCN_005_DGN_007_DETAIL_REVIEW.md) entscheidet den Capstone-Planungsschnitt; daraus folgt kein Implementierungsauftrag und kein Runtimestatus. |
|---|---|---|
| `W-STA-001` | `VALIDATED` | Lauf 33222989681 belegt die vollständige Matrix einschließlich der erwarteten empirischen Warnungen. |
| `W-DGN-001` | `VALIDATED` | Lauf 33222989682 belegt alle zwölf Query-Store-/XE-Pilotläufe mit `PASS/OK`. |
| `W-SCN-001` | `VALIDATED` | Project Adapter `0.1` und vollständiger SQL-Server-2025-Lifecycle sind auf Docker und Podman praktisch validiert. |
| `W-ADV-017` | `VALIDATED` | Lauf 33447840232 belegt Actual DOP (Degree of Parallelism; Parallelitätsgrad einer Ausführung), Exchange, positive Threadarbeit und Cleanup auf allen drei Zielversionen. |
| `W-SQL25-001` | `VALIDATED` | Quellen-, Claim- und Entscheidungsgrundlage ist abgeschlossen; daraus folgt keine neue Featuredemo. |
| `W-PRS-001` | `VALIDATED` | 102 SlideKeys, drei Custom Shows, Build 41/66/102 und vollständige Master-/Profilrender liegen vor. |
| `W-COV-001` | `VALIDATED` | Lauf 33222989644 belegt alle neun Demos; `CON-009` (Kosten in tempdb unterscheiden) endet auch auf SQL Server 2019 zweimal mit `PASS/OK`. |
| `W2-002` | `VALIDATED` | Neun `W2-A`-Altquellen sind nicht ausführbar; vier aktive Ersatzdemos und alle künftigen Neuaufbauten sind an synthetische, neutrale Datenverträge gebunden. |
| `ADV-009` (Folienspezifikation Modul M03, Lernziel LO-M03-07) | `VALIDATED` | Runtimewarnung, Masterdeck, Notes, Hashbindung, vollständiger Render und Privacy-Freigabe sind synchron. |
| `ADV-010` (Folienspezifikation Modul M03, Lernziel LO-M03-08, Parametersensitive Planoptimierung) | `VALIDATED` | Fachliche, didaktische und technische Endabnahme grenzt verbleibende Designs ausdrücklich als Folgearbeit ab. |
| `LABSCN-002` | `VALIDATED` | 22 produktive Demos sind vollständig mit Lifecycle, Provider, Ressourcen, Versionen, Reset und Evidenz inventarisiert. |
| `LABSCN-004` | `VALIDATED` | Der generische Benutzerablauf für Auswahl, Start, Übergabe, Reset und Remove ist dokumentiert und statisch geprüft. |
| `INF-002`/`INF-003` | `VALIDATED` | Docker und Podman melden `RESOURCE_OK`; der kompakte SQL-Server-2025-Lifecycle und Recovery-Pfad sind dokumentiert. |
| `LABINT-003` | `VALIDATED` | Provider-Parität ist für `QRY-001` (Indexfreundliche Suchbedingungen), `CON-004` (Blockierungsketten verfolgen) und `DGN-005` praktisch belegt. |
| `LABSCN-005/DGN-005` | `VALIDATED` | Project Adapter `0.1`; Docker-Run `d5143f2a-…` und Podman-Run `82791985-…` führten die Teilnehmerphasen aus und endeten nach Start und Reset vollständig als `REMOVED`. |
| `LABSCN-005/CON-006` | `VALIDATED` | Project Adapter `0.1`; Docker-Run `76cff6ed-…` und Podman-Run `6d2d0a51-…` belegten Opfer 1205, Survivor, Deadlock-Graph, geordnete Gegenprobe, Reset und `REMOVED`. |
| `LABSCN-005/DGN-007` | `IMPLEMENTED_STATIC_SLICE_B` | Der nicht-promotende statische Teilnehmerfluss bestand am 2026-09-19 auf SQL Server 2025/Linux mit Docker (`ea802c20-…`) und Podman (`fba84720-…`): Adapter-Preflight, Install/Validate, alle sechs Teilnehmerstufen, Cleanup und Lab-Remove (`PASS`/`REMOVED`). Kontrollierte Negativtests auf Docker mit SQL Server 2019 (`5a12e48a-46df-471a-a266-4646ba3a02e2`) und 2022 (`139c68d8-8a22-42fb-ba19-b51059f21f2b`) ergaben kanonisch `ADAPTER_UNSUPPORTED_SQL_VERSION`, im Lab-Core `ADAPTER_UNSUPPORTED_CONTRACT`, keine DGN-Datenbank und `REMOVED`. Das ist keine 2019/2022-Fachunterstützung und keine Promotion, sondern ausschließlich der erwartete 2025-only-Skip-/Cleanup-Nachweis. Weiterhin keine `READY_FOR_USER`-Übergabe, keine Szenariopromotion und kein Nachweis für `scenario.json`, Manifest, Inventar oder vollständige Lifecycle-/Versionsmatrix. |
| `LABINT-004/CON-006` | `VALIDATED` | Die vollständige freigegebene Matrix SQL Server 2025 × Docker/Podman ist praktisch belegt und prüft ausschließlich den neuen gelben Slice. |
| `DGN-007_DATA_MODEL` | `IMPLEMENTED` mit lokalem Runtime-Nachweis | Am 2026-10-06 bestanden je zwei vollständige Docker-Lifecycles auf 2019/150, 2022/160 und 2025/170; unabhängiger Datenbankabbau und eigene Container entfernt. [Nachweis](DGN_007_DATA_MODEL_RUNTIME_EVIDENCE.md). Der Datenmodell-Scope bleibt begrenzt und unverändert als Default. |
| `DGN-007_QUERY_STORE_WINDOWS` | `IMPLEMENTED` mit lokalem Runtime-Nachweis | Am 2026-10-06 bestanden je zwei vollständige Docker-Lifecycles auf 2019/150, 2022/160 und 2025/170; zwei disjunkte Katalogintervalle, gleiche Parameterlast, je vier Suchausführungen und unabhängiger Cleanup. [Nachweis](DGN_007_QUERY_STORE_WINDOWS_RUNTIME_EVIDENCE.md). Runner und CI prüfen diesen Scope getrennt; kein Incident- oder Regressionsnachweis. |
| `DGN-007_PROFILE_COMPARISON` | `IMPLEMENTED` mit lokalem Runtime-Nachweis | Am 2026-10-07 bestanden gewichtete T0/T1-Metrikvergleiche auf allen drei Versionen je zweimal, einschließlich unabhängigem Cleanup. [Nachweis](DGN_007_PROFILE_COMPARISON_RUNTIME_EVIDENCE.md). Ohne Richtungsgate oder Incidentpromotion. |
| `DGN-007_CONTROL_AB` / `BA` / `AA` | `IMPLEMENTED` mit lokalem Runtime-Nachweis | Am 2026-10-07 bestanden alle drei neutralen Kontrollfolgen auf jeder Version je zweimal; vollständige neue Reihenfolge mit 36 Lifecycles und unabhängigem Abbau aller drei eigenen Instanzen. Tatsächliche Requestfolge, aktive Plan-ID-/Hash-Union und Variation im [Nachweis](DGN_007_CONTROL_CAPTURE_RUNTIME_EVIDENCE.md). Ein 2019-BA-Duration-Kontrast liegt innerhalb beobachteter AA-Variation; keine Incidentfreigabe. |
| prospektiver `DGN-007` (Zeitabhängige Regression eines Suchworkloads)-Prüfvertrag | `STATIC_PROSPECTIVE_CONTRACT` | `DEC-068` (Prospektive Duration- und Kontrollseparation für DGN-007 festlegen), reine Record-/Separationsprüfung, 34 synthetische Tests und Quellenvalidator lokal PASS. [Vertrag](../../Demos/07_Query_Store_Extended_Events/DGN-007_Time_Bounded_Search_Incident/Contracts/README.md). Keine SQL-Runtime-Abnahme; Collector und frische Bestätigungsläufe bleiben offen. |
| skalarer `DGN-007`-Collector-Transport | `STATIC_COLLECTOR_TRANSPORT` | Reiner JSON-Decoder mit genauer Decimal-/100-ns-Darstellung, 19 Transporttests und beide Validatoren lokal PASS; 34 Prospektivtests bleiben grün. [Transportgrenze](../../Demos/07_Query_Store_Extended_Events/DGN-007_Time_Bounded_Search_Incident/Contracts/COLLECTOR_TRANSPORT.md). Keine SQL-Erfassung oder vollständigen RunRecords; fehlende Request-Ergebniszeilen bleiben `NOT_CAPTURED`/`None`. |

## 3. SQL-Server-2025-Delta: abgeschlossene Entscheidungen

Der abgeschlossene Delta-Review dokumentiert folgende Zuordnung:

| Herstellerfunktion | bestehende Anknüpfung | Entscheidung |
|---|---|---|
| Cardinality Estimation Feedback für Ausdrücke | `OPT-006` | `ADOPT`; keine neue Demo, spätere Evidenz im bestehenden Schnitt |
| Optimiertes `sp_executesql` | `QRY-004`, `OPT-007` | `DEFER`; eine spätere Concurrent-Compile-Detailanalyse ist nach der nun belegten `QRY-004`-Freigabe zulässig |
| zeitgebundene Extended-Events-Sessions | `DGN-005` | `ADOPT`; optionaler Engine-17-Schutzpfad |
| TempDB Space Resource Governance | `CON-009`, `RES-004` | `DEFER`; roter Safety- und Infrastrukturvertrag erforderlich |
| Ordered nonclustered Columnstore | `IDX-010` (Columnstore-Segmente gezielt überspringen) | `DEFER`; gelbes Detaildesign erforderlich |
| Query Store auf lesbaren Secondary Replicas | kein unmittelbarer Slice | `DEFER`; Preview- und Mehrinstanzabhängigkeit |

Vector- und KI-Funktionen liegen außerhalb des derzeitigen Curriculumzuschnitts. Der Review verwendet als Ausgangspunkt die offiziellen Microsoft-Dokumentationen zu [SQL Server 2025](https://learn.microsoft.com/sql/sql-server/what-s-new-in-sql-server-2025?view=sql-server-ver17), [Extended Events](https://learn.microsoft.com/sql/relational-databases/extended-events/sql-server-extended-events-sessions?view=sql-server-ver17) und [Query Store auf Secondary Replicas](https://learn.microsoft.com/sql/relational-databases/performance/query-store-for-secondary-replicas?view=sql-server-ver17); vor einer Inhaltsübernahme muss der Projekt-Quellenregisterprozess durchlaufen werden.

## 4. Abhängigkeits- und Stop-Regeln

```text
LABSCN-002 + LABSCN-004 -> DGN-005 + CON-006 validiert -> weiterer Kandidat nur nach Einzelreview
Query Store/XE-Pilot + Mehrsession-Vertrag validiert -> DGN-007 als eigener Folgeschnitt zulässig
```

- Kein `DGN-007` ohne validierten Query-Store-/XE-Pilot.
- Keine rote oder gelbe Lastdemo ohne bestehende Safety-Gates, Wegwerfinfrastruktur, Kill-Switch und Laufzeitbudget.
- Keine Änderung an `SQL_Server_Lab` ohne dokumentierte Fähigkeitslücke und ausdrückliche Freigabe.
- Keine Statusanhebung aus statischem Testbestand allein; Runtime-Status benötigt einen konkreten Laufnachweis.

## 5. Nächster belegpflichtiger Schritt

Der eigenständige automatisierte Datenmodellvertrag ist auf Docker für alle
drei Zielversionen jeweils zweimal praktisch belegt. Seine Prüfungen enthalten
keine Incident-, Query-Store-, XE-, Hypothesen-, Mitigations- oder interaktive
Teilnehmerabnahme. Der anschließend getrennt implementierte
`DGN-007_QUERY_STORE_WINDOWS`-Vertrag ist auf allen drei Versionen je zweimal
praktisch belegt. Er prüft ausschließlich disjunkte T0/T1-Capture-Fenster mit
gleicher Parameterlast. Der getrennte neutrale `DGN-007_PROFILE_COMPARISON`-
Vertrag bestand am 2026-10-07 ebenfalls je zweimal auf allen drei Versionen:
gewichtete Mittelwerte, T1-T0-Deltas und tatsächlich ausgeführte Plananzahl;
kein Richtungs- oder Mindestplangate. Die NULL-Ratio bei Null-Baseline wurde
gesondert mit numerischer Fixture geprüft. Lokale Matrix,
skalare Messwerte und unabhängiger Cleanup stehen im
[Profilnachweis](DGN_007_PROFILE_COMPARISON_RUNTIME_EVIDENCE.md).
Die zusätzlichen neutralen AB-/BA-/AA-Kontrollcaptures sind auf jeder Version
je zweimal praktisch belegt. Sie prüfen denselben Vierermix in fester tatsächlicher
Reihenfolge und unterscheiden ausgeführte Planmengen über beide Fenster.
AB/BA zeigten zwei aktive Plan-IDs/Hashes, AA dieselbe Plan-ID in beiden Fenstern.
Die vollständige neue Reihenfolge mit 36 Lifecycles und unabhängigem Cleanup
steht im [Kontrollnachweis](DGN_007_CONTROL_CAPTURE_RUNTIME_EVIDENCE.md).
Ein 2019-BA-Duration-Kontrast liegt innerhalb beobachteter AA-Variation;
positives Vorzeichen allein trägt deshalb keine versionsübergreifende
Separation. Diese Captures sind explorative Voraussetzungen, keine
prospektiven Bestätigungsläufe einer Incidentregel. Der getrennte reine
[Prüfvertrag](../../Demos/07_Query_Store_Extended_Events/DGN-007_Time_Bounded_Search_Incident/Contracts/README.md)
legt diese Regel jetzt vorab fest (`DEC-068`): gewichtete Statement-Duration
als primäre zeitbezogene Metrik, alle vier B-A-Kontraste unter AB/BA strikt
positiv und oberhalb beider absoluter AA-Drifts; zusätzlich global entweder
vier unterschiedliche aktive Hashmengen oder einheitlich gerichtete Reads-
Kontraste oberhalb beider absoluter AA-Reads-Drifts. 34 synthetische Tests und
der Quellenvalidator bestanden lokal. Der Status ist ausschließlich
`STATIC_PROSPECTIVE_CONTRACT`, keine Runtime-Abnahme. Der getrennte
[Transport-Vorschnitt](../../Demos/07_Query_Store_Extended_Events/DGN-007_Time_Bounded_Search_Incident/Contracts/COLLECTOR_TRANSPORT.md)
ist jetzt als `STATIC_COLLECTOR_TRANSPORT` implementiert: 19 tatsächliche
Decoderfixtures, beide Validatoren und die 34 Prospektivtests lokal PASS.
Decimal-Text und UTC-100-ns-Integer bleiben präzise. Fehlende Request-
Ergebniszeilen bleiben `NOT_CAPTURED`/`None`; deklarierte `MEASURED`-Werte
attestieren keine Herkunft. Der Body enthält keine erfundenen Phasen-,
Cleanup-, Lifecycle- oder Ressourcenangaben. Der getrennte SQL-Producer
speichert jetzt tatsächlich gezählte Ergebniszeilen je Request und stellt
die vollständige skalare Projektion vor Cleanup bereit. Seine neue lokale
2019/150-, 2022/160- und 2025/170-Matrix bestand je zweimal AB/BA/AA,
insgesamt 18 vollständige Lifecycles mit tatsächlichem Decoder und unabhängigem
Cleanup. Alle drei eigenen Container sind unabhängig abwesend bestätigt.
Der [Producernachweis](DGN_007_SQL_CAPTURE_PRODUCER_RUNTIME_EVIDENCE.md)
bindet konkrete Versionen, Images und Quellenfreeze und hält frühere
Fehlversuche getrennt fest. 156 lokale Testmethoden der Phasendiagnostikrevision ergaben 155 PASS und
einen Linux-spezifischen SKIP unter Windows. Die Producer-Integration über
[Pull Request 65](https://github.com/gecompat/SQL_PerformanceSchulung/pull/65)
ist abgeschlossen: 14 Workflows und alle 22 Jobs SUCCESS am Head
`20a867e…` gegen Base `94ed561b…`, Integration `df78cb0…`.
Je Version bestanden zwölf Lifecycles mit sechs tatsächlichen Decoder-
Captures und unabhängigem Cleanup; Linux führte alle 156 Methoden ohne
SKIP aus. Der Squash `da7b0eb…`, vollständige Übernahme, synchronisiertes
Main und lokale/remote Bereinigung des eigenen Branches sind bestätigt.
Die zwei historischen CI-Fehler bleiben getrennt dokumentiert, ohne
behauptete Ursache oder Behebung. SQL-Prädikate und Budgets bleiben gleich.

Die getrennte Main-Push-CI am Squash `da7b0eb…` ist danach vollständig
beendet: 12/13 Workflows und 47/48 Jobs SUCCESS, ausschließlich SQL Server
2022 im zweiten BA-Lifecycle `CONTROL_EVIDENCE / FAIL_RESULT_CONTRACT / G13`.
Alle zehn begonnenen 2022-Abwesenheitsprüfungen und der ownergebundene
Containerabbau einschließlich expliziter CID-Abwesenheit bestanden.
2019/2025 bestanden je zwölf Lifecycles und sechs Captures. Der neue Fehler
ist von der erfolgreichen PR65-Integration und den zwei historischen
CI-Fehlern getrennt zu bewerten; seine skalare Ursache ist offen.

Die private skalare Probe ist als begrenzte Gegenprobe abgeschlossen: auf
neuer eigener 2022-Instanz mit CI-Imagebindung und tatsächlicher Version
`16.0.4295.3` bestanden Datenmodell, Fenster, Profil, AB und BA jeweils zweimal,
insgesamt zehn Lifecycles und vier Decoder-Captures. Zehn unabhängige
Datenbankabwesenheitsprüfungen, fünf Gruppen-Leerheitsprüfungen, Quellenfreeze
mit 21 Dateien und unabhängiger own-CID-/Namensabbau bestanden. G13 wurde
nicht reproduziert; es liegen keine tatsächlichen verletzten Grenzabstände vor.
Zwei frühere private synthetische Vorchecks scheiterten vor jedem Lifecycle;
Defekte und unabhängiger Cleanup bleiben im Producernachweis getrennt.
Kein Main-, Incident- oder Behebungsnachweis; AA wurde nicht ausgeführt.

Nächster belegpflichtiger Schnitt ist ein eigener kanonischer Diagnosebericht,
keine identische Wiederholung: maximal acht gespeicherte verletzte
Profilgruppen, exakte UTC-Ticks und Grenzabstände ausschließlich im bereits
ausgelösten G13-Fehlerzweig. Der Runner bindet diese Metadaten an tatsächliches
stderr, die eindeutige fehlgeschlagene Kontroll-Evidenzphase und den
unveränderten Guard-/Summary-Abschluss; Ausgabe erst nach Cleanup.
Keine zusätzliche Query-Store-Sicht, keine Prädikat-, Last-, Zeitbudget- oder
Outcomeänderung. Der Reporter ist inzwischen lokal implementiert und
unabhängig geprüft: exakt validiertes Entfernen ergibt den ganzen bisherigen
SQL35, Quellenbindung ist erneuert, 43 Runner- und 37 Producer-/Reporter-
Methoden (ein Linux-spezifischer Windows-SKIP) sowie sieben Validatoren
bestanden. Acht tatsächliche temporäre SQL-Branchfixtures auf einer neuen
eigenen 2022-Instanz bestanden, einschließlich Ein-Tick-Abständen, gleicher
Requestgrenzen, UTC-Offset, acht Gruppen und ausdrücklichem Overflow.
Unveränderter Freeze und eigener Containerabbau sind unabhängig bestätigt.
Der ganze Report bleibt atomar innerhalb 24 Diagnosezeilen. Als nächster
Schritt wurde die reguläre CI von [Pull Request 68](https://github.com/gecompat/SQL_PerformanceSchulung/pull/68)
am Head `27a9b5c…` gegen Base `12b130f…`, Integration `55877a5…`, vollständig
beendet: 13/14 Workflows und 20/22 Jobs SUCCESS. 2019 AA1 und 2022 BA1
scheiterten an G13. First−Start beträgt −0,4263 beziehungsweise −0,951 ms;
Last liegt jeweils innerhalb der oberen Grenze. 2025 bestand zwölf Lifecycles
und sechs Captures. Alle 32 ersten Datenbankabwesenheitsprüfungen und neun
SQL-Containerabbauten bestanden; Linux 163 Methoden PASS. Der PR bleibt
unmerged und ohne CI-Freigabe. Der Reporter schließt die Messlücke, belegt
aber keine Ursache oder Behebung. Das beobachtete Millisekundenraster ist
keine zugesagte QS-Auflösung oder Toleranz.

Die einmalige private Originalmaterialisierungsprobe auf neuer eigener 2022-
Instanz reproduzierte G13 bereits in AB1: First−Start −0,2609 ms. Die verletzte
Gruppe enthält in Captureversuch 1 und im getrennten Live-SELECT jeweils genau
eine positive Raw-Zeile mit Count vier, keine Zero-/NULL-/Negative-Zeilen.
Ein Zero-Extremum erklärt diesen lokalen Fehler nicht. Elf temporäre SQL-
Fixtures PASS; sechs Präfix-Lifecycles PASS, AB1 FAIL mit sofortigem Stop,
keine AB2/BA/AA oder erfolgreiche AB-Capture. Sieben erste DB-Abwesenheits-
prüfungen, vier Gruppen-Leerheitsprüfungen und eigener Containerabbau PASS;
CID/Name unabhängig abwesend, Freeze mit 27 Dateien unverändert. Zusätzliche
Projektion/DML (Data Manipulation Language; Anweisungen zum Lesen oder Ändern von Daten) sind Beobachterinstrumentierung, keine identische kanonische
Timingprüfung und kein historischer CI-Ursachenbeweis.

Der quellenbasierte [Mess-/Zuordnungsgegenentwurf](DGN_007_CAPTURE_ASSIGNMENT_DESIGN.md)
liegt jetzt als `PROPOSED` vor. Er trennt exakten zeitlichen Einschluss und
kontrollierte Kollektivzuordnung. Der ausgearbeitete Kandidat benötigt eine
belegte vollständige Familienbasis B, T0-Capture vor T1, Bilanz B→B+4→B+8
über alle Familien-/Intervallgruppen sowie vertrauenswürdig attestierten
Ausführungsumfang. Die vier Vorabrequests laufen vor der expliziten QS-
Konfiguration; frische Datenbank und beobachtete Nullcounts beweisen keine
QS-OFF-Basis oder fehlende nachlaufende Statistik. Konkrete Baseline-,
Intervallaktivierungs- und Herkunftsbelege bleiben offen. Die Vergleichbarkeit
von QS-Endzeiten und SYSUTC-Requestklammer auf exakten 100-ns-Grenzen bleibt
ungeklärt. Das getrennte [deklarative Voraussetzungenmodell](DGN_007_ASSIGNMENT_PREREQUISITES_MODEL.md)
prüft die vorab festgehaltenen synthetischen Gegenbeispiele und bedingte
Konsistenz; keine Prozesse im Modell, SQL-/v1-Änderung oder Runtimeattestation.
Die Prüfung ersetzt insbesondere keine tatsächliche Herkunft trotz passender
Counts. Die [Quellen-/Ausführungspfadprüfung](DGN_007_PREMISE_SOURCE_REVIEW.md)
ist abgeschlossen: Procedure-Queries unter AUTO werden erfasst; dokumentierte
asynchrone Persistenz belegt keine verzögerte Publikation. Der tatsächliche
Pfad prüft eigene Calls und Ergebnisse, attestiert aber weder vollständigen
Basisabschluss noch interne Aktivierung, kontinuierlichen Zustand oder
geschlossene Coordinatorherkunft. Der konkrete
[Beobachtungs-/Herkunftsvertrag](DGN_007_OBSERVATION_PROVENANCE_CONTRACT_DESIGN.md)
liegt als PROPOSED vor: acht Acquisitionstages, vollständige Raw-/Gruppen-/
Coveragebindung, zwölf tatsächliche Calls, getrennte Pulsgrenze, überprüfte
Coordinator-Vertrauensquelle und endliche Größen-/Poll-/Observerkosten.
Bounds und deren Durchführbarkeit sind noch nicht runtimevalidiert.
Punktweise QSStates beweisen keine Kontinuität; Sättigung bleibt bedingt.
Die äußere Pipegrenze begrenzt heute nicht das Vorpuffern im Proxy.
Der [Suffizienzreview](DGN_007_SATURATION_CONTINUITY_SUFFICIENCY_REVIEW.md) ist abgeschlossen: injektive kohärente
Zählung aus einem unabhängig geschlossenen tatsächlichen Calluniversum kann
Callerfassung tragen; vollständige keyweise Stageledger zusätzlich kollektive
QS-Buckets. Counts beweisen kein kontinuierliches RW/ALL; dieses gesonderte
konservative Methodengate bleibt vorgeschlagen. Heutige Live-Dateizugriffe
und Zielnamen binden keinen vollständigen unveränderlichen Ausführungspfad.
Das getrennte [Sättigungs-/Acquisition-Gegenmodell](DGN_007_SATURATION_COUNTERMODEL.md)
implementiert die synthetischen Gegenproben mit getrennten Teilclaims.
Kein Token ist eine reale QS-Einzelidentität. Das konkrete
[Methodenentscheidungspaket](DGN_007_METHOD_DECISION_PACKAGE.md) ist vorbereitet:
Gate-Matrix mit Acquisition-/Count- und konservativem Floatkandidaten, tatsächlicher
Freeze-/Actor-/CID-/Host-/Zugangsgrenze und Kostenplan innerhalb 145/180/60 Sekunden
und 4 CPU (Central Processing Unit; Prozessor)/8 GiB. Alle Methodengates bleiben offen; Einzelmaxima sind keine
gemeinsame Machbarkeitsevidenz. Der [Offline-Quellenbundle-Verifier](DGN_007_SOURCE_BUNDLE_VERIFIER.md)
ist statisch implementiert: feste 27 Mitglieder, Gitblob-/Rohbytebindung,
separate LF-Äquivalenz und deklarierte AST-Imports samt Manipulationsfixtures.
Statischer Kandidaten-PASS attestiert keine verwendeten Runtimebytes.
Die getrennte [Prozess-/Manifestkantenprüfung](DGN_007_EXECUTION_EDGE_VERIFIER.md)
ist statisch implementiert: Python-3.12-Ganz-AST-Profil, sechs SQL-only-Manifeste,
14 Quellenhashes und SQLCMD-Gegenproben. Import-/Launcherentwurf PROPOSED,
tatsächliche Importumgebung und verwendete Runtimebytes offen. Der getrennte
[synthetische Streaming-/Budgetprototyp](DGN_007_STREAMING_BUDGET_PROTOTYPE.md) ist implementiert:
portable Budgetgegenproben und feste eigene Linux-Kindfälle; keine Integration
in die neun Runtimequellen oder reale Laufzeitmachbarkeit. Die getrennte [numerische Pipelinegegenprobe](DGN_007_NUMERIC_PIPELINE_COUNTERMODEL.md) ist implementiert: 28 synthetische Tests trennen Oracle, deklarierte Fragmentrundung, vorgegebenen Text und bestehende Consumergewichtung. Keine SQL-Konversionsemulation, Epsilon- oder Methodenfreigabe. Der konkrete [Import-/UsedBytes-Entwurf](DGN_007_IMPORT_USED_BYTES_PROBE_DESIGN.md) liegt als `DESIGNED` vor: feste Import-Only-Einstiege, kontrollierter Rohbyte-Loader, vertrauenswürdiges Interpreter-/Stdlibprofil, getrennte Receipts und begrenzter eigener Cleanup. Der erste Implementierungsteil ist das getrennte [Eingangsprotokoll](DGN_007_IMPORT_PROBE_INPUT_PROTOCOL.md): unveränderter 27-Member-Git-/Kantenvorcheck, eingefrorene neun Python-Rohbytes und begrenzte binäre Rahmung mit Kontext- und Manipulationsgegenproben. Keine Worker- oder Kandidatenimportausführung und kein UsedBytes-Claim. Die getrennte [synthetische Memory-Loader-Komponente](DGN_007_MEMORY_LOADER_FIXTURE.md) ist implementiert: ausschließlich feste Fixturebytes, tatsächliches Compile/Exec und objektgebundene Beginn-/Abschlussreceipts. Kein DGN-Import oder Importauflösungsnachweis; DGN-Attestationsflags bleiben false. Der getrennte [Interpreter-/Stdlib-Profilvorschnitt](DGN_007_IMPORT_RUNTIME_PROFILE.md) ist implementiert: begrenzte aktuelle Bootstrapmetadaten und Vergleich gegen separat deklarierte Baseline. Keine Trust- oder bereits ausgeführte Bibliotheksbyteattestation; die gewählte Kontrollruntime bleibt eine ausdrücklich benannte Annahme. Der [skalare Parent-/Worker-Profilbindungsvertrag](DGN_007_IMPORT_PROFILE_BINDING_DESIGN.md) liegt als `DESIGNED` vor. Der getrennte [reine Profilvergleich](DGN_007_IMPORT_PROFILE_BINDING_MATCHER.md) ist implementiert: 38 synthetische Tests prüfen exakte deklarierte Installation und Workerinventur, eingefrorenen Eingangs-/Ordinal-/Phasenkontext sowie gemeinsame Metadatengrenzen. Sein Match attestiert keine tatsächliche Workerbeobachtung, Herkunft oder Consumption. Die tatsächliche Prozessanbindung bleibt unimplementiert. Die getrennte lokale Record-Rückgabe des Profilvorschnitts ist jetzt implementiert: `observe_current_interpreter_records` liefert ausschließlich die tatsächlich aufgenommene und vollständig geprüfte Abschlussaufnahme, bei Ablehnung keine Records. Gehaltene Liveanker sind kein dauerhaft gültiger Zustand des Modulcaches; spätere aktuelle Runtimeverwendung braucht eine frische Aufnahme. Legacyreports, Bootstrapimports und Grenzen bleiben erhalten. Die konkrete Bootstraproute ist jetzt im [Profilbindungsentwurf §8](DGN_007_IMPORT_PROFILE_BINDING_DESIGN.md#8-konkreter-bootstrap--und-projektionsvorschnitt) festgelegt: geplante Scriptquelle als `__main__`, unveränderter Profilmodulname, benannte direkte Stdlibimports und Vorinitialisierung der Sysconfigwerte ohne zusätzliche Projektimports. Feldherkunft, frische Aufnahme, erneute Livekohärenz und engere Scalarformen sind getrennt beschrieben. Die getrennte importneutrale skalare Projektion ist jetzt im bestehenden Profilmodul implementiert: frische Aufnahme, vollständige private primitive Tupel, erneute Livekohärenz vor und nach Projektion sowie zusätzliche separat gewählte und gegen Factorycode/Closure geprüfte FileFinder-Hookbindung; bei Ablehnung keine Skalare. Dies attestiert keine unabhängige Factoryherkunft oder tatsächlichen Worker. Eine getrennte lokale Bootstrap-Charakterisierung unter CPython 3.12.3 erfasste 85 Modulnamen mit genau zwei Controls; dies ist keine operative Sollinventur. Der [konservative Größenbeleg](DGN_007_IMPORT_PROFILE_BINDING_DESIGN.md#9-charakterisierte-bootstraproute-und-größenuntergrenze) zeigt bereits mindestens 16.449 Bytes für das vollständige Modularray und 21.108 bis 21.144 Bytes für die gemeinsame Metadata einschließlich Header, unverändertem Input82 und Kontext. Die heutige benannte JSON-Form ist damit für diesen vollständigen charakterisierten Namenumfang nicht darstellbar; andere Routen und Installationen sind dadurch nicht ausgeschlossen. Keine Capanhebung, Filterung oder Digestersetzung ist freigegeben. Der vollständige Linux-/Python-3.12-Import-Only-Prototyp bleibt offen; der getrennte Darstellungs- und Digestentwurf aus Profilbindungsentwurf §10 liegt als DESIGNED vor. Die separat vorgewählte vollständige Kontrollfixture und reine Größenprüfung in §11 belegen gemeinsame Metadata von 17.127/17.113/17.091 Bytes; der §10-Tupelkandidat überschreitet das unveränderte 16.384-Byte-Cap. Neuer Sizer34/34 und Legacy27/40 ohne SKIP. Der getrennte verlustfreie Stringpoolentwurf in §12 liegt als DESIGNED vor, mit eigenen lokalen Pools je Form und unveränderten Inhalten/Caps einschließlich höchstens 256 Poolwerten. Der eigene reine Pool-Sizer in §13 bestand 37/37 isolierte Gegenproben ohne SKIP und die vollständige neue 3×5-Rechnung: maximal 9.389 Bytes einschließlich Header und 204 Poolwerte, vollständig unabhängig nachgerechnet und rückgewonnen. Der getrennte experimentelle Formcodec in §14 bestand 41/41 isolierte Gegenproben ohne SKIP; die vollständige Originalfixture bestand alle 3×5 Frames, Feldrückgewinnung, kanonischen Repack und drei eigene Digestdomains je Ordinal. Das gesamte Fünf-Formen-Set umfasst 28.264/28.257/28.246 Bytes. Originalauswahl und Inputrahmen bleiben unverändert, keine neue Aufnahme oder Nonce. Der unabhängige Nachreview bestätigte sämtliche Frames, Feldrückgewinnung und Digests aus den unveränderten Originaleingaben ohne Codec-/Helper-Replay. Der eigene reine kombinierte Eingangsprototyp in §15 bestand 34/34 isolierte Gegenproben ohne SKIP und die neue vollständige Originalfixtureprüfung: drei Frames mit jeweils 9.389 Metadata-/Headerbytes und 130.837 unveränderten Bodybytes, insgesamt 140.226 Bytes. Tatsächliche vollständige Feld-/Rawbyterückgewinnung und Repack sowie unabhängige Stdlib-Nachrechnung ohne Replay bestanden. Alle gleichzeitig geltenden Caps bleiben erhalten; 64 KiB begrenzen ausschließlich die fünf Metadataausgaben. Die konkrete operative Bootstrap-/Kanalreihenfolge in §16 liegt als DESIGNED vor: importneutraler PRE-Vorschnitt, vollständiger Profilvergleich vor Bodyfreigabe und vollständige Eingangsprüfung vor Importfreigabe, unveränderte gemeinsame Caps und gehaltene Kontrollquellenführung. Der reine Kontrollbootstrapquellengenerator in §17 bestand 32/32 ausschließlich synthetische Gegenproben ohne SKIP unter CPython 3.12.14; er ist keine operative Workerroute. Die getrennte [Sysconfig-Vorinitialisierung §18](DGN_007_IMPORT_PROFILE_BINDING_DESIGN.md#18-feste-sysconfig-vorinitialisierung-gehaltener-kontrollquellen) bestand 53/53 isolierte synthetische Gegenproben ohne SKIP unter CPython 3.12.14. Die private native Auswahl nach [§19](DGN_007_IMPORT_PROFILE_BINDING_DESIGN.md#19-private-auswahlgrundlage-vor-einer-vollständigen-operativen-inventur) ist mit genau einem begrenzten Versuch und unabhängigem Prozess-/Record-POST abgeschlossen. Die additive reine [Inline-Metadata-Syntaxquelle §20](DGN_007_IMPORT_PROFILE_BINDING_DESIGN.md#20-reine-additive-inline-metadata-syntaxquelle) bestand 80/80 isolierte synthetische Gegenproben ohne SKIP unter CPython 3.12.14; der erste Fixture-Label-Fehllauf bleibt getrennt dokumentiert. Die additive reine [Inline-Metadata-Semantikquelle §21](DGN_007_IMPORT_PROFILE_BINDING_DESIGN.md#21-reine-additive-inline-metadata-semantikquelle) bestand nach zwei engen Fixturekorrekturen 108/108 isolierte synthetische Gegenproben ohne SKIP unter CPython 3.12.14; der erste 106/108-Lauf bleibt getrennt dokumentiert. Vollständige deklarative M/IP/S15/P11/D9-Semantik, unveränderter benannter Originaldigest und Providerkohärenz sind geprüft. Die additive reine [Inline-Profilreporterquelle §22](DGN_007_IMPORT_PROFILE_BINDING_DESIGN.md#22-reiner-additiver-inline-profilreporter) bestand im einzigen isolierten Lauf 149/149 synthetische Gegenproben ohne SKIP unter CPython 3.12.14. Vollständige Scalarprojektion, eigener REPORTED-Pool, atomare begrenzte Records und getrennte Original-/Reportdigests sind geprüft; vier frühere Builder bleiben erhalten. Die reine begrenzte [Inline-Header-/Metadata-Aufnahme §23](DGN_007_IMPORT_PROFILE_BINDING_DESIGN.md#23-reine-begrenzte-inline-header-metadata-aufnahme) bestand im einzigen isolierten Lauf 174/174 synthetische Gegenproben ohne SKIP unter CPython 3.12.14. Exact-Chunktype-/Größenvorläufe, vollständige deklarative M-Semantik und atomare gehaltene Rückgabe sind geprüft; fünf frühere Builder bleiben erhalten. Die additive reine [K-Domain-/Commandquelle §24](DGN_007_IMPORT_PROFILE_BINDING_DESIGN.md#24-reine-k-domain-und-deklarativ-gebundene-commands) bestand im einzigen isolierten Lauf 209/209 synthetische Gegenproben ohne SKIP unter CPython 3.12.14. Vollständiger K8-/D9-Vorlauf, eigene headerfreie E4-K-Domain und atomare kanonische Commands gegen separat gehaltene Callerwerte sind geprüft; sechs bisherige Builder und 174 alte Tests bleiben erhalten. Die additive reine [Inline-Metadata-Callerquelle §25](DGN_007_IMPORT_PROFILE_BINDING_DESIGN.md#25-vollständiger-deklarativer-inline-metadata-callerabgleich) bestand nach zwei engen Fixturekorrekturen 243/243 isolierte synthetische Gegenproben ohne SKIP unter CPython 3.12.14; der erste 241/243-Lauf mit zwei Fehlern vor Matcheraufruf bleibt getrennt dokumentiert. Beide vollständigen Formen und Semantiken, zwei eigene Originalinputdigests und vollständiger Abgleich gegen separat gehaltene I7/W6/K8 sind geprüft; sieben bisherige Builder und 209 alte Tests bleiben erhalten. Die additive reine [Inline-Rawbodyaufnahme §26](DGN_007_IMPORT_PROFILE_BINDING_DESIGN.md#26-reine-begrenzte-aufnahme-deklarierter-rawbodies) bestand nach einer engen Fixturelabelkorrektur 272/272 isolierte synthetische Gegenproben ohne SKIP unter CPython 3.12.14; der erste 271/272-Lauf bleibt getrennt dokumentiert. Vollständige Formen und Größen vor Hashes, beide tatsächlichen D9 und neun Rawhashes vor Callerabgleich sowie atomare Originalbodyrückgabe sind geprüft; acht bisherige Builder und 243 alte Tests bleiben erhalten. Die additive reine [Profilrecord-Reassemblierung §27](DGN_007_IMPORT_PROFILE_BINDING_DESIGN.md#27-reine-begrenzte-reassemblierung-gehaltener-profilrecords) bestand im einzigen isolierten synthetischen Lauf 304/304 Gegenproben ohne SKIP unter CPython 3.12.14. Vollständige begrenzte Control-/Envelopeformen, interne Konsistenz, kanonische Controls und tatsächlicher Footerhash vor Callerordinal sowie atomare Originalrecordrückgabe sind geprüft; neun bisherige Builder und 272 alte Tests bleiben erhalten. Zwei enge Fixturelabelkorrekturen wurden vor dem ersten Lauf reviewt; kein ausgeführter Fehllauf. Die additive reine [Inline-Profil-Callerquelle §28](DGN_007_IMPORT_PROFILE_BINDING_DESIGN.md#28-vollständiger-deklarativer-inline-profilabgleich) bestand im einzigen isolierten synthetischen Lauf 341/341 Gegenproben ohne SKIP unter CPython 3.12.14. Beide vollständigen R4-Formen/Semantiken, Actual-Pool-Repack und vollständiger separater Callerabgleich sind geprüft; die Matchfunktion berechnet keinen SHA. Zehn frühere Builder und 304 alte Methoden bleiben erhalten. Vorreviewkorrekturen und genaue Grenzen stehen in §28. Die additive reine R→BODY_RELEASE-Planquelle aus §29 bestand im einzigen isolierten synthetischen Lauf 378/378 Gegenproben ohne SKIP unter CPython 3.12.14; elf alte Builder und 341 alte Methoden bleiben erhalten. Die additive reine INPUT_COMPLETE-Quelle aus §30 bestand im einzigen isolierten synthetischen Lauf 413/413 Gegenproben ohne SKIP unter CPython 3.12.14; zwölf alte Builder und 378 alte Methoden bleiben erhalten. Der vollständige Record-/Footer→R-Calleradapter aus §31 ist rein additiv implementiert und im isolierten synthetischen Lauf mit 460/460 PASS ohne SKIP geprüft; dreizehn alte Builder und 413 alte Methoden bleiben erhalten. Die eigene lokale [Ledgerkomponente §32.5](DGN_007_IMPORT_PROFILE_BINDING_DESIGN.md#325-eigene-lokale-synthetische-ledgerkomponente) ist im isolierten synthetischen Lauf mit 66/66 PASS ohne SKIP geprüft. Reservierungen, ganze Slot-/Zustandsbindung, sticky Fehler und einmaliger Fakecleanup sind lokal belegt; kein tatsächlicher Kanal-/Loader-/Absenznachweis. Der vollständige [Loaderrecordvertrag §33](DGN_007_IMPORT_PROFILE_BINDING_DESIGN.md#33-vollständige-deklarative-begin-complete-loaderrecords) liegt als DESIGNED vor. Nächster kleiner Schnitt ist ausschließlich der separate SESSION_END-DESIGN-Vertrag mit exakten Counts und nicht selbstreferentiellem Kanalhashpräbild. Tatsächlicher Kanal, Loader-/Parentregistrierungsadapter, operative Inventur und Fünf-Formen-/64-KiB-Gate bleiben offen. Frische operative Auswahl, inline Empfang/Reporting, tatsächliche Parent-/Worker-Anbindung, feste Quellenauflösung, tatsächliche DGN-Loaderverwendung und Importabschluss sowie begrenzte eigene Worker mit unabhängigem Cleanup bleiben getrennte Gates. Die charakterisierte Kontrollfixture ist keine operative Workerbaseline; Migration bleibt offen. Sein Claim bleibt auf tatsächlich abgeschlossene Top-Level-Imports begrenzt; keine vollständige UsedBundle-, SQL-, Acquisition- oder Methodenattestation.
Normative Methoden-/Grenzänderungen brauchen eine ausdrückliche neue Entscheidung.
Keine implizite OFF-/CLEAR-/Laständerung. Erst eine tragfähige explizite
Methodenentscheidung erlaubt gemeinsam versionierte
SQL-/Transport-/Record-/Evaluator-/Coordinator-Umsetzung. Bestehende Guards,
Fehlerklassifikation, DEC-068, Last und Budgets bleiben erhalten; keine
pauschale 1-ms-Toleranz, Abrundung oder Wiederholen bis grün. Die alternative
Methode ist weder entschieden noch implementiert oder abgenommen. Der frühere Acht-Fixture-Vorcheck enthält keine vollständige
Lifecycle-/Versionsmatrix oder Reproduktion des Main-G13.

Die interne verlustfreie Capture-Rückgabe ist lokal vorbereitet und geprüft;
Veröffentlichung und Integration sind bis zur G13-Klärung zurückgestellt.
Danach folgt der geplante API-Schnitt:
Body, tatsächlich geprüfte Phasen und erfolgreiche erste unabhängige
Datenbankabwesenheit über denselben Harness erhalten. Rückgabe erfolgt
nur nach erfolgreichem Lifecycle und Cleanup; erfolgreiche Recovery
ändert einen ersten Abwesenheitsfehler nicht in PASS. Der direkte Helper
akzeptiert ausschließlich unveränderte bekannte Kontrollverträge.
Counts-/CLI-Ausgabe und Fehlerprioritäten bleiben erhalten; keine
RunRecords, Incidentbewertung oder `runtime_attested=True`.
Danach muss der Collector-Coordinator den integrierten Freeze und Quellen,
Ressourcen, präzise Budgets und tatsächliche serielle Reihenfolge attestieren
und Cleanup unabhängig bestätigen. Die interne Capture-Rückgabe allein
ist kein vollständiger RunRecord oder Coordinator-Nachweis.
Erst danach folgen frische Bestätigungsläufe unter
der festgelegten Regel. CPU bleibt ergänzend, ohne Fallback. Keine
nachträglich ausgewählte Ratio oder statistische Signifikanzbehauptung;
fehlende tragfähige Evidenz bleibt `SKIP_EVIDENCE_MISSING`.
Plan- beziehungsweise klar unterscheidbare Runtimeprofile sind zusätzlich
gegen den Designvertrag zu begründen; Planunterschiede ersetzen kein Symptom
und isolieren keine Kompilierungsursache. Unterschiedliche Parameterlast
allein ist kein Regressionsnachweis. Als begrenzte Voraussetzung verwendet der
ältere Teilnehmerpfad jetzt `sys.databases.compatibility_level` mit NULL-Guard
und prüft vor der Evidenzausgabe den bestehenden 2025-/170-Vertrag; auch die
Adaptervalidierung lehnt fehlende Compatibility-Werte ab. Die ältere Beobachtung
ist nun an erfolgreich erfasste T0/T1-Profile samt Query-Store-Intervallen
gebunden; historische oder ungenutzte Katalogpläne werden nicht gezählt und
die absolute Planzahl ist kein Gate. Der Teilnehmeradapter verwendet in beiden
Phasen denselben Viererparameter-Mix in festgelegter Reihenfolge (A: `8/3,
1/3, 5/3, 1/1`; B: `1/3, 8/3, 5/3, 1/1`). Der nicht-promotende
Docker-Teilnehmerlauf auf SQL Server 2025 bestand alle sechs SQL-Stufen und
unabhängigen Cleanup (RunId `73c0b191-66e1-4891-b9f2-4ab3a4513571`, 2026-11-13).
Das belegt weder Incident noch vollständige Teilnehmerabnahme. Live-Mittelwerte
dürfen keine nachträglichen Zusatzrequests enthalten; Plan-/Profilunterscheidbarkeit
und Verschlechterung sind getrennt zu begründen. Die zuvor gemessenen
unterschiedlichen Richtungen für CPU und Reads erfüllen allein keine
Incidentfreigabe.
Danach folgen die vollständige Capstone-Matrix und die
interaktive Docker-/Podman-Abnahme; deren offene Gates bleiben bestehen.

Der Capstone-Planungsschnitt ist mit `TSK-002` entschieden
(`DECIDED_PLANNING`, Detailreview
[LABSCN-005 – Detailreview DGN-007 (Planungsschnitt)](LABSCN_005_DGN_007_DETAIL_REVIEW.md)).
Implementierungsschnitt A (Project Adapter `0.1` mit Datenaufbau,
Query-Store-Zeitfenstern und Incident-Erzeugung ohne Mitigationsmarker) besitzt
seit dem 2026-09-14 die praktische Docker-/Podman-Lifecycle-Abnahme: Docker-Run
`9ac100f8-f24f-420e-949c-943e35b9bcda` und Podman-Run
`e06e9ec9-d239-4cd0-b9a7-0050dc574180` bestanden jeweils Start -> `READY_FOR_USER`,
Reset -> `READY_FOR_USER` und Remove -> `REMOVED` auf SQL Server 2025. Die
verbleibende Gesamtabnahme umfasst den vollständigen Lifecycle dieser
Schnitt-B-Fassung und die begrenzte Provider-/Versionsmatrix. Der manuelle Teilnehmerablauf sowie
die Evidenz-, Hypothesen- und Mitigationsartefakte sind statisch geprüft.
Frische SQL-Server-2025/Linux-Runs bestanden am 2026-09-19 auf Docker
(`ea802c20-4820-4007-a441-43a74a89c8fc`) und Podman
(`fba84720-5f0b-4537-bc98-75bbad37a85b`) Adapter-Install/Validate, alle sechs
Demo-Stufen, Teilnehmer- und Adapter-Cleanup sowie Lab-Remove. Das belegt die
aktuelle Linux-Providerparität, ist aber keine Szenariopromotion und keine
vollständige Lifecycle-/Versionsmatrix. Ressourcen-, Netzwerk-, Hyper-V- und
gemischte Topologien bleiben ohne konkreten fachlichen Bedarf gestoppt.


### QRY-023 – Enginequalifikation und nächste Integrationsschritte

Der vollständige automatisierte Harnesslauf ist auf den festgeschriebenen SQL-Server-Builds 2019/15.0.4500.2, 2022/16.0.4305.5 und 2025/17.0.5035.5 bestanden. Alle zehn Phasen (einschließlich Cleanup und Planevidenz) waren erfolgreich. Fehler aus den realen Läufen wurden in SQL, Runner-Übergabe und Regressionen behoben; die `public`-Systemobjektbaseline wurde vervollständigt. Die Laufdaten begründen keine Leistungsrangfolge. QRY-023 bleibt `PROPOSED` und außerhalb des Runtimekatalogs.

Der Ressourcen-/TempDB-Schnitt ist als eigener vorgeschlagener CI-Aufrufer in `.github/workflows/qry023-proposed-runtime.yml` umgesetzt. Er verwendet ausschließlich drei digestgebundene Wegwerfinstanzen auf isolierten GitHub-Hosted-VMs, prüft authentifizierte Loginbereitschaft vor Mutationen, provisioniert vorab den erforderlichen `READER`-SQL-Login über SQLCMD-stdin, verteilt ein Gesamtmaximum von 1 GiB auf das tatsächliche TempDB-Layout und erhält die Produktmanifest-/Kataloggrenze (`PROPOSED`, `runtime_authorized: false`). Das SA-Startpasswort wird über eine geschützte kurzlebige Env-Datei übergeben. SQL-Timeouts nach Setup unterdrücken SQL-Cleanup fail-closed; die äußere Jobbereinigung entfernt den markierten Ein-Run-Container nur nach bestätigtem SQL-Cleanup und erhält ihn sonst als Diagnosezustand. Der erste Drei-Engine-Lauf deckte eine verkehrte TempDB-Fehlerzählung und einen nicht aufgelösten SQLCMD-`:r`-Include auf; beide Fehler wurden korrigiert und durch Regressionen gebunden. Der finale Lauf auf den festgebundenen Builds 2019/15.0.4500.2, 2022/16.0.4305.5 und 2025/17.0.5035.5 bestand alle zehn Phasen. Der unabhängige Methoden-/Code-Nachreview fand keine offenen P1/P2.

PR #563 integrierte den vorgeschlagenen Aufrufer am Commit `69a6c33915d70ea393fcf6bf6b06526b3cecc51b`; 69 PR-Checks sowie die QRY-023-Harness- und Runtimeworkflows auf `main` bestanden. Der nächste Schritt ist der dokumentierte Abgleich belegter Dokumentations-/Registrierungswidersprüche. Katalogpromotion und menschliche Generalprobe sind nicht Teil dieser Welle; die Generalprobe bleibt ausdrücklich ausgeschlossen.

### QRY-023 – Live-Negativfälle für READER-Inventar (Fortsetzung 13.11.2026)

PR #566 erweiterte die kontrollierte Gegenprobe um direkten Objekt-`SELECT` und
`db_datareader`; #567 ergänzte Objekt-`DENY`, #568 die temporäre
`dbcreator`-Mitgliedschaft, #569 ein fehlendes erwartetes Tabellenobjekt,
#570 serverweites `VIEW SERVER STATE`-`GRANT` und #571 dessen explizites
`DENY`. Die Fälle liefen in owner-markierten Wegwerfcontainern auf den
festgeschriebenen SQL-Server-2019/2022/2025-Builds. Sie verlangten jeweils die
exakte Abweichungskategorie, `FAIL_NOT_PROVEN`, Cleanup und keinen Eintritt in
Queryphasen; nach jeder Matrixsequenz bestand der positive Zehnphasenlauf.
PR #571 ist in Commit `ed271d4e3befcbdb8f3f335ed76a82451a478b24` integriert;
README und Effektivrechte-Design sind abgeglichen. Der Stand bleibt
`PROPOSED`, nicht katalogisiert und `runtime_authorized: false`.

PR #572 ergänzte datenbankweites `GRANT VIEW DEFINITION`; #573 prüfte das
entsprechende `DENY`. Auf allen drei Builds erkannte die ADMIN-Inventur beide
als alleinige `DATABASE_PERMISSION`-Abweichung, brach vor Queryphasen ab und
entfernte die markierte Datenbank. Die positiven Zehnphasenläufe bestanden.
PR #573 ist als `ebea12bad95fe38f8ebe97d928665258437cfd08` integriert.

PR #574 erteilte `READER` auf dem inventarisierten Standardendpoint
`TSQL Default TCP` einen direkten `CONNECT`-Grant. Die ADMIN-Inventur wies ihn
auf allen drei Builds als alleinige `SERVER_PERMISSION`-Abweichung ab; der
owner-markierte Restore widerrief ihn und verifizierte die Abwesenheit. Der
positive Zehnphasenlauf bestand. Ein anfänglicher SQL-2025-Loginfehler trat vor
der Gegenprobe im TempDB-Guard auf; nur dieser Enginejob wurde frisch
wiederholt und bestand. Integration: `0b307a0dda2ac6eb481e3ac891d8dd418c93b649`.

PR #575 ergänzte `DENY CONNECT` auf demselben inventarisierten Standardendpoint.
Die drei Enginejobs wiesen den Eintrag als `SERVER_PERMISSION` ab, widerriefen
ihn nach Owner-Label-Prüfung und verifizierten den leeren Ausgangszustand; der
positive Zehnphasenlauf bestand. Integration: `1d5217acdd624469cd13940497a6117f17d24e1a`.

Die nächste endliche Gegenprobe erstellt im frischen Wegwerfcontainer genau
einen benutzerdefinierten `TSQL`-Endpoint in `STOPPED`-Zustand, erwartet
`CUSTOM_ENDPOINT` und entfernt ihn nach erkannter Injektion, selbst wenn eine
spätere Assertion fehlschlägt. `STOPPED` bedeutet laut [Microsoft CREATE
ENDPOINT (Transact-SQL)](https://learn.microsoft.com/en-us/sql/t-sql/statements/create-endpoint-transact-sql?view=sql-server-ver17),
dass der Endpoint nicht auf seinem Port lauscht; Port 25032 liegt im
dokumentierten Bereich. Dies ist eine explizite DDL-Änderung im ausschließlich
owner-markierten Wegwerfinstanzcontainer, keine Beschädigung eines Systemkatalogs.
Allgemeine Runtime-/Produkt-/Katalogfreigabe und menschliche Generalprobe
gehören nicht zu diesem Schritt.

Im ersten PR-Lauf wurden Injektion, erwartete `CUSTOM_ENDPOINT`-Abweisung und
Endpoint-Drop auf allen drei Builds erreicht. Der danach folgende positive
Reader-Preflight scheiterte jedoch auf allen Builds mit SQL-Loginfehler; damit
ist die Ursache noch nicht bewiesen. Zur Isolation läuft die globale Endpoint-
DDL-Gegenprobe künftig erst nach dem vollständigen positiven Zehnphasenlauf.
Die positive Qualifikation wird so vor dieser zusätzlichen Instanzmutation
gemessen. Eine gezielte Wiederholung des vollen positiven Laufs nach dem
Endpoint-Drop scheiterte auf allen drei Builds im `QUALIFICATION_PREFLIGHT` mit
18456/State 149 (`Login lacks connect endpoint permission`). Die begrenzte
ADMIN-Diagnose zeigte, dass danach explizites `public CONNECT` auf den
Standardendpoints 2, 3 und 5 vorlag, aber auf `TSQL Default TCP`/Endpoint 4
fehlte. DEC-083 untersagt dem Harness, `public`- oder Endpointrechte zu ändern.
Darum wird der globale Endpoint-Fall nach dem positiven Lauf als letzte Mutation
in seiner owner-markierten Wegwerfinstanz ausgeführt; nach bestätigtem Endpoint-
Drop wird die ganze Instanz entfernt und nicht für weitere Reader-Verbindungen
wiederverwendet.

PR #578 ergänzte das direkte `GRANT VIEW ANY DATABASE` an `READER`. DEC-083
erlaubt dieses Recht nur aus `public`; die zusätzliche Principal-Zuweisung wurde
auf allen drei Builds als alleinige `SERVER_PERMISSION`-Abweichung vor den
Queryphasen abgewiesen und im owner-markierten Wegwerfinstanzcontainer
widerrufen/verifiziert. Als Nächstes prüft PR #579 die komplementäre direkte
`DENY VIEW ANY DATABASE`-Zuweisung mit demselben fail-closed und Restorevertrag.

PR #579 bestand auf SQL Server 2019/2022/2025: der direkte `DENY VIEW ANY
DATABASE` wurde als alleinige `SERVER_PERMISSION`-Abweichung abgewiesen,
owner-gebunden widerrufen und verifiziert; danach bestand der positive
Zehnphasenlauf. PR #580 qualifizierte `DENY CONNECT SQL` auf allen drei Builds.
Der erste Lauf zeigte, dass ein bedingungsloser Restore auch den bestehenden
GRANT löschte; die Korrektur bindet die Injektion an die GRANT-Baseline und
stellt nur bei bestätigtem DENY den ursprünglichen GRANT wieder her. Nach
Korrektur bestanden alle drei Enginejobs und PR-Gates; Integration:
`232b3c583f5aa25d1b8a9c9be2012b1116fa174c`.

PR #581 qualifizierte die zusätzliche direkte Mitgliedschaft von `READER` in
`securityadmin` auf SQL Server 2019/2022/2025 als alleinige fail-closed
`SERVER_ROLE`-Abweichung vor Queryphasen. Die Injektion verlangte einen
bekannten Nichtmitglied-Ausgangszustand; markergebundener Restore im
owner-geprüften Wegwerfcontainer, Verifikation und anschließender positiver
Zehnphasenlauf bestanden. Der erste 2025-Lauf scheiterte vor Setup am TempDB-
Growth-Guard mit zwei noch unbegrenzten Dateien; die gezielte frische
Wiederholung bestand. Integration: `f2d36454d03d256f1d762284fdcc6fd4604c5043`.


### QRY-023 TempDB-Guard – begrenzte Dateisatzkonvergenz (PR #583)

Der erste frische SQL-2025-Job von PR #581 zeigte im TempDB-Guard drei anfänglich
gesehene Dateien, danach aber zwei weitere Dateien mit `MAXSIZE = UNLIMITED`.
PR #583 konfiguriert nun den vollständigen jeweils sichtbaren Dateisatz erneut
und verlangt innerhalb von höchstens 16 Durchläufen zwei stabile, vollständig
begrenzte Beobachtungen. Der Abbruch bleibt vor dem Setup. Die drei Enginejobs
und unabhängige Review stehen aus.

Die SQLCMD-sichere Endpunktübergabe änderte anschließend erneut den gemeinsamen `run_demo.py`-AST. Zwei DGN-007-Offlineprofile meldeten deshalb `PYTHON_PROFILE_CHANGED`; der ausschließlich zugehörige CPython-3.12-AST-Digest wurde auf `9d1df02d34d74d761aaa496c1490fcbd86fd8abb62ad6cbce99150eb90e5213d` aktualisiert. Die gebundene DGN-007-Profilregression bestand lokal mit CPython 3.12.14 (26/26); andere Runtimequellen, Manifeste und Methodengates blieben unangetastet.
Direkte lokale Factory-Rückgaben sind jetzt zusätzlich in einer engen Top-Level-Form abgedeckt; bedingte/dynamische Rückgaben bleiben offen. 103/103 fokussierte Tests bestehen, die 93/578/534 Startkandidaten bleiben unverändert.
Einfache `if`-/`else`-Factoryzweige mit ausschließlich direkten Klassenreturns werden jetzt ebenfalls konservativ beidseitig verfolgt; komplexe Kontrollflüsse bleiben offen. 103/103 fokussierte Tests, 93/578/534 Archivscan unverändert.
Einfache Factoryrückgaben über eine lokale direkte Instanzzuweisung werden ebenfalls verfolgt; Rebinding und komplexe Statements bleiben ausgeschlossen. 104/104 fokussierte Tests; der Archivscan bleibt unverändert.

Konstante dynamische Importnamen werden zusätzlich über direkte `importlib`-
und `builtins`-Importaliase verfolgt. Vier synthetische Aliasformen bestehen;
berechnete Namen bleiben ausgeschlossen. Fokussiert 105/105, Archivclosure
268/2.438 und Modulstartkandidaten 93/578/534 mit unveränderten Digests.

Einfache Zuweisungsaliase und Namensketten zu diesen Importfunktionen sind
ebenfalls statisch gebunden. 105/105 fokussierte Tests, Archivkennzahlen
unverändert; Scope und Rebinding bleiben unbewertet.

Direkte Stringkonstanten in Namenszuweisungen können nun ebenfalls ein
dynamisches Importargument binden; relative und berechnete Namen bleiben
ausgeschlossen. 105/105 fokussierte Tests, Archivkennzahlen unverändert.

Direkte Konkatenation zweier Stringkonstanten wird inline und in einer
Zuweisung statisch erkannt; relative und sonstige Ausdrücke bleiben offen.
105/105 fokussiert, Archivkennzahlen unverändert.

### Begrenzte Fortsetzung: `sysconfig.is_python_build` (14. November 2026)

Die ausdrückliche Freigabe aller noch offenen Themen setzt die autonome
Fortsetzung fort. Der nächste begrenzte Checkpoint umfasst höchstens ein
Arbeitspaket, einen Pull Request und zwei lokale Quellen-/Vertragskandidaten:
den zeilengebundenen CPython-Quellfact und seine synthetischen Gegenproben.
Die verifizierte CPython-3.12.16-Quelle wird wiederverwendet; es kommt keine
neue Produktquelle hinzu. SQL, Lab, Runtime, operative Inventur und menschliche
Generalprobe sind nicht Teil des Pakets. Verbrauch in Tokens/Geld ist unbekannt;
die Grenze gilt für Paket, PR und Kandidaten, nicht als Providerkostenlimit.

Der Fact entscheidet `sysconfig.py:223` nur für die vollständig geprüfte
produktive `Lib`-Quellmenge, in der der Selbstaufruf und die drei `venv`-Aufrufe
argumentlos sind. Testquellen sind nicht Teil dieses Beweises. Alias- und
dynamische Callerformen verwerfen den Fact. Der PR-Merge ist der Checkpoint;
danach wird der kanonische Status aktualisiert und die nächste offene,
freigegebene statische Aufgabe anhand des dann aktuellen Status ausgewählt.

PR #736 integrierte diesen ersten Kandidaten als Commit
`7a45cc32a501558e209c9e7178119e48c3cc7753`; fünf PR-Gates waren erfolgreich,
`main` ist synchronisiert und lokale/Remote-Arbeitsbranches wurden entfernt.

### Abgeschlossen: sysconfig-Build-Tree-Guard (14. November 2026)

Der Nutzerauftrag setzt die autonome Bearbeitung der weiteren freigegebenen
Themen fort. Für den nächsten begrenzten Checkpoint gilt höchstens ein
Arbeitspaket, ein Pull Request und zwei lokale Quellen-/Vertragskandidaten:
die OCI-Elternpfadprüfung für `Modules/Setup` und der zeilengebundene
`is_python_build`-Fact mit synthetischen Regressionen. Quellarchiv, Image und
Konfiguration werden aus den bestehenden digestgebundenen Eingaben
wiederverwendet. Kein Interpreter-, Worker-, Profil-, SQL-, Lab- oder
Generalprobenlauf. PR #737 integrierte den Fact als Commit
`448ba8ae77ffc64a93e98bbd63dd0c08782077cc`; fünf PR-Gates waren erfolgreich,
`main` ist synchronisiert und lokale/Remote-Arbeitsbranches wurden entfernt.
Token-/Geldverbrauch bleibt unbekannt; die Begrenzung galt für Arbeitspaket,
PR und Kandidaten, nicht als Providerkostenlimit.

### Abgeschlossen: `string.Template`-Pattern-Guard (14. November 2026)

Der Fact für `string.py:71` wurde gegen den vollständigen AST-Verweisbestand
der gepinnten Produktionsbibliothek und synthetische Gegenproben validiert.
PR #738 integrierte ihn als Commit `223bf0f6a4082367ecc2e22fab45b8df38189430`;
alle fünf PR-Gates bestanden, `main` ist synchronisiert und die lokalen sowie
Remote-Arbeitsbranches wurden entfernt. Der Lauf blieb statisch und
`CANDIDATES_ONLY`; keine Runtime-, SQL-, Profil- oder Generalprobenattestation.

### Abgeschlossen: `_weakrefset.WeakSet`-Leerkonstruktion (14. November 2026)

Der Fact für `_weakrefset.py:50` bindet alle Produktionsverweise und die
zwölf argumentlosen Konstruktionen an den vollständigen gepinnten
Quellbestand. PR #739 integrierte ihn als Commit
`6f8731d0a8b70dfd591d7a1821c82e0e42714f87`; alle fünf PR-Gates bestanden,
`main` ist synchronisiert und die Arbeitsbranches sind entfernt. Der Lauf blieb
statisch und `CANDIDATES_ONLY`.

### Abgeschlossen: `copyreg.pickle`-Callable-Guard (14. November 2026)

Der Fact für `copyreg.py:13` bindet alle fünf produktiven Aufrufstellen und
deren Funktionsargumente an den gepinnten Quellenbestand. PR #740 integrierte
ihn als Commit `84ac87aa755864e7cb69ebc94d5e2b75ab675e6d`; PR #741 ergänzte
eine Aliasimport-Gegenprobe als Commit `b67c22cee8d882df93b375df86ab4958695d1d6e`.
Alle erforderlichen Gates bestanden und die Branches wurden entfernt. Der
Lauf blieb statisch und `CANDIDATES_ONLY`.

### Abgeschlossen: `logging`-Lock-Präsenz (14. November 2026)

Die Facts für `logging/__init__.py:240` und `:247` binden die
Lock-Präsenzprüfungen an die gepinnten Python- und C-Quellen. PR #742 integrierte sie als
Commit `188ea2d696b427d085886f010d1ffd95f5f96f9`; alle fünf Gates bestanden,
`main` ist synchronisiert und die Arbeitsbranches sind entfernt. Der Lauf blieb
statisch und `CANDIDATES_ONLY`.

### Abgeschlossen: `copyreg.constructor`-Callable-Guard (14. November 2026)

Der Fact für `copyreg.py:23` folgt alle fünf `pickle`-Registrierungen und deren
optionale Konstruktorargumente. PR #743 integrierte ihn als Commit
`348d5b27b749c9004ad9c04ae840508073959ee5`; alle fünf PR-Gates bestanden und
die Branches wurden entfernt. Der Lauf blieb statisch und `CANDIDATES_ONLY`.

### Begrenzte Fortsetzung: `collections.namedtuple`-Rename-Guard (14. November 2026)

Der nächste Checkpoint umfasst höchstens ein Arbeitspaket, einen Pull Request
und zwei lokale Kandidaten: den Fact für `collections/__init__.py:386` sowie
synthetische Gegenproben. Der bestehende signaturgeprüfte CPython-3.12.16-
Quellstand und die Zielimageeingaben werden wiederverwendet. Kein Interpreter-,
Profil-, Worker-, SQL-, Lab-, operativer Inventur- oder Generalprobenlauf.
Token-/Geldverbrauch bleibt unbekannt; die Grenze gilt für Paket, PR und
Kandidaten, nicht als Providerkostenlimit. Der PR-Merge ist der Checkpoint;
danach wird die nächste offene freigegebene Aufgabe anhand des dann aktuellen
Status ausgewählt.

### Abgeschlossen: Argumentbindung bei lokalen Aufrufen (14. November 2026)

Nach PR #744 umfasst der nächste Checkpoint höchstens ein Arbeitspaket, einen
Pull Request und zwei lokale Kandidaten: die fail-closed Argumentbindung für
direkte lokale Aufrufkontexte und ihre synthetischen Gegenproben. Verwendet
werden der vorhandene signaturgeprüfte CPython-3.12.16-Quellstand, das
digestgebundene Zielimage und die bestehende Workerroute; neue Produktquellen
sind nicht erforderlich. Token- und Geldverbrauch bleiben unbekannt; die Grenze
ist 1/1/2 und kein Provider-Ausgabenlimit.

Der Scanner verfolgt primitive Literalargumente und Standardwerte, höchstens
acht Kontexte je Funktion und danach einen unbekannten Fallback, der beide
Zweige erhält. Dekorierte oder variadische Funktionen, dynamische/
Sternargumente sowie Argumentweitergabe über Modulgrenzen bleiben offen. Die
Quellkanten werden über eindeutige Importfundstellen gezählt. Der gebundene
Zielscan reduziert die unbekannten Bedingungen von 502 auf 497; 60 Module, 316
Kanten, 166 Funktionen und der Zeilendigest bleiben unverändert. Fünf konkrete
Bedingungen sind zusätzlich entschieden. Ein konservativer Rebinding-Guard
nimmt drei zuvor abgeleitete Importlib-Entscheidungen wieder zurück. Die
Regressionen decken Funktions- und Methoden-Rebinding ab.

Die fokussierte Regression besteht lokal mit 176 Fällen. Die lokalen
Python-3.13/3.14-Bundleläufe endeten mit `BOOTSTRAP_CHANGED`; der gepinnte
Python-3.12-DGN-007-Offlineworkflow bestand im PR. Alle fünf PR-Gates waren
erfolgreich. PR #745 integrierte die Änderung als `8d3bbf8244ead67412a044026c891ce980efd549`;
`main` ist synchronisiert und lokale/Remote-Branches sind entfernt. Kein
Interpreter-, Profil-, Worker-, SQL-, Lab- oder Generalprobenlauf.

### Abgeschlossen: boolesche Negation in lokalen Aufrufargumenten (14. November 2026)

Der nächste Checkpoint umfasst höchstens ein Arbeitspaket, einen Pull Request
und zwei synthetische Regressionen. Der lokale Aufrufbinder wertet reines `not`
über bereits unterstützten primitiven Literalen und Literal-Tupeln aus; dynamische
Operanden bleiben unbekannt. Verwendet werden der signaturgeprüfte
CPython-3.12.16-Quellstand, das gebundene Zielimage und die bestehende
Workerroute. Keine neue Produktquelle und keine Runtime-, SQL-, Lab- oder
Generalprobenausführung. Token-/Geldverbrauch bleiben unbekannt; die Grenze ist
1/1/2 und kein Provider-Ausgabenlimit.

Die fokussierte Suite besteht lokal mit 178 Fällen. Der gebundene Zielscan bleibt
`CANDIDATES_ONLY` bei 60 Modulen, 316 Kanten, 166 Funktionen und 70/497
entschiedenen/unbekannten Bedingungen; Zeilen- und Bedingungsdigests bleiben
unverändert. Alle fünf PR-Gates bestanden. PR #746 integrierte die Änderung als
`e573cd6559787c5d2eacdd31cb39b8a0eabf5ef5`; `main` ist synchronisiert und
lokale/Remote-Branches sind entfernt. Die nächste offene, freigegebene Aufgabe
wird anhand des dann aktuellen Status ausgewählt.

### Begrenzte Fortsetzung: primitive Gleichheit in lokalen Aufrufargumenten (14. November 2026)

Der nächste Checkpoint umfasst höchstens ein Arbeitspaket, einen Pull Request
und zwei synthetische Regressionen. Der lokale Literalbinder erkennt einzelne
`==`-/`!=`-Vergleiche über bereits unterstützte primitive Literale und
Literal-Tupel. Vergleichsketten und dynamische Operanden bleiben unbekannt;
keine benutzerdefinierten Vergleichsoperatoren werden ausgeführt. Verwendet
werden der signaturgeprüfte CPython-3.12.16-Quellstand, das gebundene Zielimage
und die bestehende Workerroute. Keine neue Produktquelle und keine Runtime-,
SQL-, Lab- oder Generalprobenausführung. Token-/Geldverbrauch bleiben
unbekannt; die Grenze ist 1/1/2 und kein Provider-Ausgabenlimit.

Die fokussierte Suite besteht lokal mit 180 Fällen. Der gebundene Zielscan bleibt
`CANDIDATES_ONLY` bei 60 Modulen, 316 Kanten, 166 Funktionen und 70/497
entschiedenen/unbekannten Bedingungen; Zeilen- und Bedingungsdigests sind
unverändert. Der PR-Merge ist der Checkpoint; danach folgt die nächste offene,
freigegebene Aufgabe anhand des dann aktuellen Status.

### Begrenzte Fortsetzung: boolesche Kurzschlussargumente (14. November 2026)

Der nächste Checkpoint umfasst höchstens ein Arbeitspaket, einen Pull Request
und zwei synthetische Regressionen. Der lokale Literalbinder wertet `and`-/`or`-
Ausdrücke nur entlang vollständig bekannter primitiver Operanden aus und wahrt
die Python-Kurzschlussreihenfolge. Ein dynamischer linker Operand bleibt
unbekannt; übersprungene Operanden werden nicht analysiert oder ausgeführt.
Verwendet werden der signaturgeprüfte CPython-3.12.16-Quellstand, das gebundene
Zielimage und die bestehende Workerroute. Keine neue Produktquelle und keine
Runtime-, SQL-, Lab- oder Generalprobenausführung. Token-/Geldverbrauch bleiben
unbekannt; die Grenze ist 1/1/2 und kein Provider-Ausgabenlimit.

Die fokussierte Suite besteht lokal mit 182 Fällen. Der gebundene Zielscan bleibt
`CANDIDATES_ONLY` bei 60 Modulen, 316 Kanten, 166 Funktionen und 70/497
entschiedenen/unbekannten Bedingungen; Zeilen- und Bedingungsdigests bleiben
unverändert. Der PR-Merge ist der Checkpoint; danach folgt die nächste offene,
freigegebene Aufgabe anhand des dann aktuellen Status.

### Abgeschlossen: unäre numerische Argumentliterale (14. November 2026)

Der nächste Checkpoint umfasst höchstens ein Arbeitspaket, einen Pull Request
und zwei synthetische Regressionen. Der lokale Literalbinder wertet unäre
`+`-/`-`-Ausdrücke ausschließlich über exakte Integer- und Bool-Literale aus.
Unbekannte Operanden und andere Zahlentypen bleiben offen; es werden keine
benutzerdefinierten Operationen aufgerufen. Verwendet werden die bestehende
signaturgeprüfte CPython-3.12.16-Quelle, das gebundene Zielimage und die feste
Workerroute. Keine neue Produktquelle und keine Interpreter-, Profil-, Worker-,
SQL-, Lab- oder Generalprobenausführung. Token-/Geldverbrauch bleiben
unbekannt; die Grenze ist 1/1/2 und kein Provider-Ausgabenlimit. PR-Integration
ist der Checkpoint; danach wird anhand des aktuellen Status weitergearbeitet.

Die zwei synthetischen Regressionen und die fokussierte Suite bestehen lokal
mit 184 Tests unter Python 3.14. Alle fünf PR-Gates, einschließlich des
gepinnten CPython-3.12.16-Offlineworkflows, bestanden. PR #749 integrierte den
Schnitt als `35c323c02206e47837ce380b979074c0ae7b4b14`; `main` ist
synchronisiert und lokale/Remote-Branches sind entfernt. Kein Interpreter-,
Profil-, Worker-, SQL-, Lab- oder Generalprobenlauf.

### Abgeschlossen: Singleton-Identitätsargumente (14. November 2026)

Der nächste Checkpoint umfasst höchstens ein Arbeitspaket, einen Pull Request
und zwei synthetische Regressionen. Der lokale Literalbinder wertet `is` und
`is not` ausschließlich für exakte `None`- und Bool-Singletons aus. Tupel- oder
sonstige Objektidentität und dynamische Operanden bleiben unbekannt. Verwendet
werden die bestehende signaturgeprüfte CPython-3.12.16-Quelle, das gebundene
Zielimage und die feste Workerroute. Keine neue Produktquelle und keine
Interpreter-, Profil-, Worker-, SQL-, Lab- oder Generalprobenausführung.
Token-/Geldverbrauch bleiben unbekannt; die Grenze ist 1/1/2 und kein
Provider-Ausgabenlimit. PR-Integration ist der Checkpoint; danach wird anhand
des aktuellen Status weitergearbeitet.

Die zwei synthetischen Regressionen und die fokussierte Suite bestehen lokal
mit 186 Tests unter Python 3.14. Alle fünf PR-Gates einschließlich der
gepinnten CPython-3.12.16-Offlineprüfung bestanden. PR #750 integrierte den
Schnitt als `1678bec2c3c1961cd0275123c4253bbf65d7cd49`; `main` ist
synchronisiert und lokale/Remote-Branches sind entfernt. Der Workflow enthält
keinen separaten Zielscanbericht. Kein Interpreter-, Profil-, Worker-, SQL-,
Lab- oder Generalprobenlauf.

### Abgeschlossen: Tupel-Mitgliedschaft in Literalargumenten (14. November 2026)

Der nächste Checkpoint umfasst höchstens ein Arbeitspaket, einen Pull Request
und zwei synthetische Regressionen. Der lokale Argumentbinder wertet einzelne
`in`-/`not in`-Vergleiche über unterstützte primitive Werte und
Literal-Tupel aus, wenn die rechte Seite ein Literal-Tupel ist. Dynamische
Operanden und Sammlungen bleiben unbekannt; es werden keine benutzerdefinierten
Vergleichs- oder Containeroperationen ausgeführt. Verwendet werden die
bestehende signaturgeprüfte CPython-3.12.16-Quelle, das gebundene Zielimage und
die feste Workerroute. Keine neue Produktquelle und keine Interpreter-, Profil-,
Worker-, SQL-, Lab- oder Generalprobenausführung. Token-/Geldverbrauch bleiben
unbekannt; die Grenze ist 1/1/2 und kein Provider-Ausgabenlimit. PR-Integration
ist der Checkpoint; danach wird anhand des aktuellen Status weitergearbeitet.

Die zwei synthetischen Regressionen und die fokussierte Suite bestehen lokal
mit 188 Tests unter Python 3.14. Alle fünf PR-Gates einschließlich der
gepinnten CPython-3.12.16-Offlineprüfung bestanden. PR #751 integrierte den
Schnitt als `4422e10bcb1abaec63f1f6497b63462dd880d692`; `main` ist
synchronisiert und lokale/Remote-Branches sind entfernt. Kein Interpreter-,
Profil-, Worker-, SQL-, Lab- oder Generalprobenlauf.

### Abgeschlossen: bedingte Literalargumente (14. November 2026)

Der nächste Checkpoint umfasst höchstens ein Arbeitspaket, einen Pull Request
und zwei synthetische Regressionen. Der lokale Argumentbinder wertet einen
`IfExp` nur aus, wenn sein Test ein bekannter primitiver Wert oder ein
Literal-Tupel ist. Er wertet ausschließlich den gewählten Zweig aus; dynamische
Tests und gewählte dynamische Ergebnisse bleiben unbekannt. Verwendet werden
die bestehende signaturgeprüfte CPython-3.12.16-Quelle, das gebundene Zielimage
und die feste Workerroute. Keine neue Produktquelle und keine Interpreter-,
Profil-, Worker-, SQL-, Lab- oder Generalprobenausführung. Token-/Geldverbrauch
bleiben unbekannt; die Grenze ist 1/1/2 und kein Provider-Ausgabenlimit.
PR-Integration ist der Checkpoint; danach wird anhand des aktuellen Status
weitergearbeitet.

Die zwei synthetischen Regressionen und die fokussierte Suite bestehen lokal
mit 190 Tests unter Python 3.14. Alle fünf PR-Gates einschließlich der
gepinnten CPython-3.12.16-Offlineprüfung bestanden. PR #752 integrierte den
Schnitt als `a028a4dd360b5147c0fc9933ec063ef40a59a269`; `main` ist
synchronisiert und lokale/Remote-Branches sind entfernt. Kein Interpreter-,
Profil-, Worker-, SQL-, Lab- oder Generalprobenlauf.

### Abgeschlossen: kurze Literal-Vergleichsketten (14. November 2026)

Der nächste Checkpoint umfasst höchstens ein Arbeitspaket, einen Pull Request
und zwei synthetische Regressionen. Der lokale Literalbinder wertet unterstützte
Vergleichsketten links nach rechts aus und bildet Python-Kurzschluss bei einem
falschen Teilergebnis nach. Ein erreichter dynamischer Operand oder eine nicht
unterstützte Vergleichsform bleibt unbekannt. Verwendet werden die bestehende
signaturgeprüfte CPython-3.12.16-Quelle, das gebundene Zielimage und die feste
Workerroute. Keine neue Produktquelle und keine Interpreter-, Profil-, Worker-,
SQL-, Lab- oder Generalprobenausführung. Token-/Geldverbrauch bleiben
unbekannt; die Grenze ist 1/1/2 und kein Provider-Ausgabenlimit. PR-Integration
ist der Checkpoint; danach wird anhand des aktuellen Status weitergearbeitet.

Die zwei synthetischen Regressionen und die fokussierte Suite bestehen lokal
mit 192 Tests unter Python 3.14. Alle fünf PR-Gates einschließlich der
gepinnten CPython-3.12.16-Offlineprüfung bestanden. PR #753 integrierte den
Schnitt als `b84b259ea88945a48e86f5da5daf36e0a6018cdf`; `main` ist
synchronisiert und lokale/Remote-Branches sind entfernt. Kein Interpreter-,
Profil-, Worker-, SQL-, Lab- oder Generalprobenlauf.

### Abgeschlossen: `sys.version_info` mit konstantem Index (14. November 2026)

Der nächste Checkpoint umfasst höchstens ein Arbeitspaket, einen Pull Request
und zwei synthetische Regressionen. Die Zielbedingungsauswertung indexiert
ausschließlich das bereits gepinnte `sys.version_info`-Tupel mit einer nicht-
negativen konstanten Ganzzahl. Dynamische, negative, Bool- und ungültige
Indizes bleiben unbekannt. Keine neue Produktquelle und keine Interpreter-,
Profil-, Worker-, SQL-, Lab- oder Generalprobenausführung. Token-/Geldverbrauch
bleiben unbekannt; der Umfang beträgt ein Paket, einen PR und zwei Kandidaten,
kein Provider-Ausgabenlimit. PR-Integration ist der Checkpoint; danach wird
anhand des aktuellen Status weitergearbeitet.

Die zwei synthetischen Regressionen und die fokussierte Suite bestehen lokal
mit 194 Tests unter Python 3.14. Alle fünf PR-Gates einschließlich der
gepinnten CPython-3.12.16-Offlineprüfung bestanden. PR #754 integrierte den
Schnitt als `a0784f4460c583521c0d8d29cdfea140685b3583`; `main` ist
synchronisiert und lokale/Remote-Branches sind entfernt. Kein Interpreter-,
Profil-, Worker-, SQL-, Lab- oder Generalprobenlauf.

### Abgeschlossen: konstante `sys.version_info`-Slices (14. November 2026)

Der nächste Checkpoint umfasst höchstens ein Arbeitspaket, einen Pull Request
und zwei synthetische Regressionen. Die Zielbedingungsauswertung wertet Slices
des gebundenen `sys.version_info`-Tupels nur mit nichtnegativen konstanten
Ganzzahlgrenzen und Schrittweiten aus. Dynamische oder negative Grenzen oder
Schrittweiten sowie Schrittweite null bleiben unbekannt. Keine
neue Produktquelle und keine Interpreter-, Profil-, Worker-, SQL-, Lab- oder
Generalprobenausführung. Token-/Geldverbrauch bleiben unbekannt; der Umfang
beträgt ein Paket, einen PR und zwei Kandidaten, kein Provider-Ausgabenlimit.
PR-Integration ist der Checkpoint; danach wird anhand des aktuellen Status
weitergearbeitet.

Die zwei synthetischen Regressionen und die fokussierte Suite bestehen lokal
mit 196 Tests unter Python 3.14. Alle fünf PR-Gates einschließlich der
gepinnten CPython-3.12.16-Offlineprüfung bestanden. PR #755 integrierte den
Schnitt als `7623d5afef2b1173686e49998af4c8ae5a90882d`; `main` ist
synchronisiert und lokale/Remote-Branches sind entfernt. Kein Interpreter-,
Profil-, Worker-, SQL-, Lab- oder Generalprobenlauf.

### Abgeschlossen: negative `sys.version_info`-Indizes und Grenzen (14. November 2026)

Der nächste Checkpoint umfasst höchstens ein Arbeitspaket, einen Pull Request
und zwei synthetische Regressionen. Für das gebundene `sys.version_info`-Tupel
werden negative konstante Ganzzahlindizes sowie negative Slicegrenzen und
Schrittweiten ergänzt. Außerhalb liegende Einzelindizes, Bool-Indizes,
dynamische Grenzen und Schrittweite null bleiben unbekannt. Keine neue
Produktquelle und keine Interpreter-, Profil-, Worker-, SQL-, Lab- oder
Generalprobenausführung. Token-/Geldverbrauch bleiben unbekannt; der Umfang
beträgt ein Paket, einen PR und zwei Kandidaten, kein Provider-Ausgabenlimit.
PR-Integration ist der Checkpoint; danach wird anhand des aktuellen Status
weitergearbeitet.

Die fokussierte Suite besteht lokal mit 196 Tests unter Python 3.14. PR-Gates
standen vor Integration aus. Alle fünf PR-Gates einschließlich der gepinnten
CPython-3.12.16-Offlineprüfung bestanden. PR #756 integrierte den Schnitt als
`b28ba4254d845b24cead260486a75ddd28c1692a`; `main` ist synchronisiert und
lokale/Remote-Branches sind entfernt. Kein Interpreter-, Profil-, Worker-,
SQL-, Lab- oder Generalprobenlauf.

### Abgeschlossen: Compilemodus-gebundenes `__debug__` (14. November 2026)

Der nächste Checkpoint umfasst höchstens ein Arbeitspaket, einen Pull Request
und zwei synthetische Regressionen. `__debug__` wird nur dann als wahr gebunden,
wenn der bereits gepinnte CPython-3.12.16-Quellen-/argv-Nachweis
`sys.flags.optimize == 0` vorliegt. Ohne diesen Fact bleibt die Bedingung
unbekannt. Keine neue Produktquelle und keine Interpreter-, Profil-, Worker-,
SQL-, Lab- oder Generalprobenausführung. Token-/Geldverbrauch bleiben
unbekannt; die Grenze ist ein Paket, ein PR und zwei Kandidaten, kein
Provider-Ausgabenlimit. PR-Integration ist der Checkpoint; danach wird anhand
des aktuellen Status weitergearbeitet.

Zwei synthetische Regressionen und die fokussierte Suite bestehen lokal mit 198
Tests unter Python 3.14. Alle fünf PR-Gates einschließlich der gepinnten
CPython-3.12.16-Offlineprüfung bestanden. PR #757 integrierte den Schnitt als
`aa182abe50858b62b290e82dcacfe82c6abd031b`; `main` ist synchronisiert und
lokale/Remote-Branches sind entfernt. Kein Interpreter-, Profil-, Worker-,
SQL-, Lab- oder Generalprobenlauf.

### Abgeschlossen: gebundene Plattformzeichenfolgen indexieren (14. November 2026)

Der nächste Checkpoint umfasst höchstens ein Arbeitspaket, einen Pull Request
und zwei synthetische Regressionen. Die bestehende Zielbedingungsauswertung
indexiert bereits gepinnte Plattformzeichenfolgen und wertet konstante Slices
aus. Dynamische Indizes/Grenzen und außerhalb liegende Einzelindizes bleiben
unbekannt. Keine neue Produktquelle und keine Interpreter-, Profil-, Worker-,
SQL-, Lab- oder Generalprobenausführung. Token-/Geldverbrauch bleiben
unbekannt; die Grenze ist ein Paket, ein PR und zwei Kandidaten, kein
Provider-Ausgabenlimit. PR-Integration ist der Checkpoint; danach wird anhand
des aktuellen Status weitergearbeitet.

Zwei synthetische Regressionen und die fokussierte Suite bestehen lokal mit 200
Tests unter Python 3.14. Alle fünf PR-Gates einschließlich der gepinnten
CPython-3.12.16-Offlineprüfung bestanden. PR #758 integrierte den Schnitt als
`e2bc5c1ba26413d1fd55b5153c85f9e69d2075ad`; `main` ist synchronisiert und
lokale/Remote-Branches sind entfernt. Kein Interpreter-, Profil-, Worker-,
SQL-, Lab- oder Generalprobenlauf.

### Abgeschlossen: vollständige Listliterale indexieren (14. November 2026)

Der nächste Checkpoint umfasst höchstens ein Arbeitspaket, einen Pull Request
und zwei synthetische Regressionen. Die Zielbedingungsauswertung indexiert und
slice't vollständig bekannte Listliterale. Dynamische Container/Indizes und
außerhalb liegende Einzelindizes bleiben unbekannt. Keine neue Produktquelle und
keine Interpreter-, Profil-, Worker-, SQL-, Lab- oder Generalprobenausführung.
Token-/Geldverbrauch bleiben unbekannt; der Umfang beträgt ein Paket, einen PR
und zwei Kandidaten, kein Provider-Ausgabenlimit. PR-Integration ist der
Checkpoint; danach wird anhand des aktuellen Status weitergearbeitet.

Zwei synthetische Regressionen und die fokussierte Suite bestehen lokal mit 202
Tests unter Python 3.14. Alle fünf PR-Gates einschließlich der gepinnten
CPython-3.12.16-Offlineprüfung bestanden. PR #759 integrierte den Schnitt als
`bd7035da2bbcce19c91011597f3849584ecaf08d`; `main` ist synchronisiert und
lokale/Remote-Branches sind entfernt. Kein Interpreter-, Profil-, Worker-,
SQL-, Lab- oder Generalprobenlauf.

### Abgeschlossen: benannte `sys.version_info`-Felder (14. November 2026)

Der nächste Checkpoint umfasst höchstens ein Arbeitspaket, einen Pull Request
und zwei synthetische Regressionen. Die fünf benannten Felder `major`, `minor`,
`micro`, `releaselevel` und `serial` werden aus dem gepinnten
CPython-`sys.version_info`-Wert ausgewertet. Andere Felder bleiben unbekannt.
Keine neue Produktquelle und keine Interpreter-, Profil-, Worker-, SQL-, Lab-
oder Generalprobenausführung. Token-/Geldverbrauch bleiben unbekannt; der
Umfang ist ein Paket, ein PR und zwei Kandidaten, kein Provider-Ausgabenlimit.
PR-Integration ist der Checkpoint; danach wird anhand des aktuellen Status
weitergearbeitet.

Zwei synthetische Regressionen und die fokussierte Suite bestehen lokal mit 204
Tests unter Python 3.14. Alle fünf PR-Gates einschließlich der gepinnten
CPython-3.12.16-Offlineprüfung bestanden. PR #760 integrierte den Schnitt als
`790db3bda0ca7b52a77cdd29240d002c11090350`; `main` ist synchronisiert und
lokale/Remote-Branches sind entfernt. Kein Interpreter-, Profil-, Worker-,
SQL-, Lab- oder Generalprobenlauf.

### Abgeschlossen: konstante Dictionary-Literale (14. November 2026)

Der nächste Checkpoint umfasst höchstens ein Arbeitspaket, einen Pull Request
und zwei synthetische Regressionen. Vollständig bekannte Dictionary-Literale
werden nur mit hashbaren Schlüsseln ausgewertet; dynamische Expansion, Schlüssel
und fehlende Einträge bleiben unbekannt. Unhashbare Set-Elemente liefern
ebenfalls unbekannt statt einer Ausnahme. Keine neue Produktquelle und keine
Interpreter-, Profil-, Worker-, SQL-, Lab- oder Generalprobenausführung.
Token-/Geldverbrauch bleiben unbekannt; der Umfang ist ein Paket, ein PR und
zwei Kandidaten, kein Provider-Ausgabenlimit. PR-Integration ist der Checkpoint;
danach wird anhand des aktuellen Status weitergearbeitet.


Zwei synthetische Regressionen und die fokussierte Suite bestehen lokal mit 206
Tests unter Python 3.14. Alle fünf PR-Gates einschließlich der gepinnten
CPython-3.12.16-Offlineprüfung bestanden. PR #761 integrierte den Schnitt als
`2ed3677c68daea5237ac37cb460db204a570821c`; `main` ist synchronisiert und
lokale/Remote-Branches sind entfernt. Kein Interpreter-, Profil-, Worker-,
SQL-, Lab- oder Generalprobenlauf.

### Abgeschlossen: `get()` auf Dictionary-Literalen (14. November 2026)

Der nächste Checkpoint umfasst höchstens ein Arbeitspaket, einen Pull Request
und zwei synthetische Regressionen. `get()` wird nur mit einem oder zwei
vollständig bekannten Positionsargumenten auf einem vollständig bekannten
Dictionary-Literal ausgewertet. Dynamische Schlüssel/Defaults und
Schlüsselwortargumente bleiben unbekannt. Keine neue Produktquelle und keine
Interpreter-, Profil-, Worker-, SQL-, Lab- oder Generalprobenausführung.
Token-/Geldverbrauch bleiben unbekannt; ein Paket, ein PR und zwei Kandidaten
sind Arbeitsumfang, kein Provider-Ausgabenlimit. PR-Integration ist der
Checkpoint; danach wird anhand des aktuellen Status weitergearbeitet.

Zwei synthetische Regressionen und die fokussierte Suite bestehen lokal mit 208
Tests unter Python 3.14. Alle fünf PR-Gates einschließlich der gepinnten
CPython-3.12.16-Offlineprüfung bestanden. PR #762 integrierte den Schnitt als
`e21856f0c1738fd650b37e22de350dc7b40836d6`; `main` ist synchronisiert und
lokale/Remote-Branches sind entfernt. Kein Interpreter-, Profil-, Worker-,
SQL-, Lab- oder Generalprobenlauf.

### Abgeschlossen: `startswith()` auf Plattformstrings (15. November 2026)

Der nächste Checkpoint umfasst höchstens ein Arbeitspaket, einen Pull Request
und zwei synthetische Regressionen. `startswith()` wird nur mit einem bekannten
String oder vollständig bekannten String-Tupel auf einer gebundenen
Plattformzeichenfolge ausgewertet. Dynamische Präfixe und weitere
Argumentformen bleiben unbekannt. Der Ausdruck kommt konkret im gemeinsamen
`Demos/00_Framework/Tools/sqlcmd_process.py` vor. Keine neue Produktquelle und
keine Interpreter-, Profil-, Worker-, SQL-, Lab- oder Generalprobenausführung.
Token-/Geldverbrauch bleiben unbekannt; ein Paket, ein PR und zwei Kandidaten
sind Arbeitsumfang, kein Provider-Ausgabenlimit. PR-Integration ist der
Checkpoint; danach wird anhand des aktuellen Status weitergearbeitet.

Zwei synthetische Regressionen und die fokussierte Suite bestehen lokal mit 210
Tests unter Python 3.14. Alle fünf PR-Gates einschließlich der gepinnten
CPython-3.12.16-Offlineprüfung bestanden. PR #763 integrierte den Schnitt als
`7cb558344532d3dc4fe27ec91b390367df57bc66`; `main` ist synchronisiert und
lokale/Remote-Branches sind entfernt. Kein Interpreter-, Profil-, Worker-,
SQL-, Lab- oder Generalprobenlauf.

### Abgeschlossen: S15-Startupflags aus der festen Workerroute
(15. November 2026)

Der nächste Checkpoint umfasst höchstens ein Arbeitspaket, einen Pull Request
und zwei synthetische Regressionen. Die sechs S15-Startupflags werden nur aus
der exakt gepinnten Worker-argv, `preconfig.c`, `initconfig.c` und der
`sys.flags`-/`sys.dont_write_bytecode`-Abbildung aus `sysmodule.c` abgeleitet.
Geänderte Quellen, argv oder `env` verwerfen die Facts. Native Boolwerte und
die normalisierte S15-Intdarstellung bleiben unterschieden; es entstehen weder
Profilaufnahme noch vollständige S15-Records. Keine Runtime-, Profil-, Worker-,
SQL-, Lab- oder Generalprobenausführung. Token-/Geldverbrauch bleiben
unbekannt; ein Paket, ein PR und zwei Kandidaten sind Arbeitsumfang, kein
Provider-Ausgabenlimit. PR-Integration ist der Checkpoint; danach wird anhand
des aktuellen Status weitergearbeitet.

Zwei synthetische Regressionen und die fokussierte Suite bestehen lokal mit 212
Tests unter Python 3.14. Alle fünf PR-Gates einschließlich der gepinnten
CPython-3.12.16-Offlineprüfung bestanden. PR #764 integrierte den Schnitt als
`1ef59b533545ac29ddd7ef31e22224f84b0d50c7`; `main` ist synchronisiert und
lokale/Remote-Branches sind entfernt. Kein Interpreter-, Profil-, Worker-,
SQL-, Lab- oder Generalprobenlauf.

### Abgeschlossen: `sys.implementation.version` quellenbinden
(15. November 2026)

Der nächste Checkpoint umfasst höchstens ein Arbeitspaket, einen Pull Request
und zwei synthetische Regressionen. Der Wert wird nur aus dem gepinnten
CPython-`sysmodule.c` abgeleitet, wenn `make_impl_info(version_info)` nachweislich
denselben zuvor erzeugten und `sys.version_info` zugewiesenen Wert erhält.
Abweichende Objektzuweisungen bleiben unbekannt. Keine neue Produktquelle und
keine Runtime-, Profil-, Worker-, SQL-, Lab- oder Generalprobenausführung.
Token-/Geldverbrauch bleiben unbekannt; ein Paket, ein PR und zwei Kandidaten
sind Arbeitsumfang, kein Provider-Ausgabenlimit. PR-Integration ist der
Checkpoint; danach wird anhand des aktuellen Status weitergearbeitet.

Zwei synthetische Regressionen und die fokussierte Suite bestehen lokal mit 214
Tests unter Python 3.14. Alle fünf PR-Gates einschließlich der gepinnten
CPython-3.12.16-Offlineprüfung bestanden. PR #765 integrierte den Schnitt als
`ab5240ed62662e0edffebd020df6ba3ddad14728`; `main` ist synchronisiert und
lokale/Remote-Branches sind entfernt. Kein Interpreter-, Profil-, Worker-,
SQL-, Lab- oder Generalprobenlauf.

### Abgeschlossen: `sys.implementation.name` quellenbinden
(15. November 2026)

Der nächste Checkpoint umfasst höchstens ein Arbeitspaket, einen Pull Request
und zwei synthetische Regressionen. Der Resolver übernimmt `cpython` nur bei
passendem CPython-3.12.16-`sysmodule.c`-Digest, festem
`_PySys_ImplName`-Wert und nachgewiesener Nutzung beim Aufbau von
`sys.implementation.name`. Änderungen oder unvollständige Quellstruktur
verwerfen den Fact. Keine Produktquelle und keine Runtime-, Profil-, Worker-,
SQL-, Lab- oder Generalprobenausführung. Token-/Geldverbrauch bleiben
unbekannt; ein Paket, ein PR und zwei Kandidaten begrenzen den Arbeitsumfang,
nicht Providerkosten. PR-Integration ist der Checkpoint.

Zwei synthetische Regressionen und die fokussierte Suite bestehen lokal mit 216
Tests unter Python 3.14. Alle fünf PR-Gates einschließlich der gepinnten
CPython-3.12.16-Offlineprüfung bestanden. PR #767 integrierte den Schnitt als
`cf567c274867f515f9a7dd4b6048bb70ffeb9c69`; `main` ist synchronisiert und
lokale/Remote-Branches sind entfernt. Kein Interpreter-, Profil-, Worker-,
SQL-, Lab- oder Generalprobenlauf.

### Abgeschlossen: `sys.implementation.cache_tag` quellenbinden
(15. November 2026)

Der nächste Checkpoint umfasst höchstens ein Arbeitspaket, einen Pull Request
und zwei synthetische Regressionen. `cpython-312` wird ausschließlich aus den
gepinnten `sysmodule.c`-Makros und dem bereits quellengebundenen Versionsfact
3.12.16 abgeleitet; geänderte Makros, Versionen oder Feldzuweisungen verwerfen
den Fact. Keine Produktquelle und keine Runtime-, Profil-, Worker-, SQL-, Lab-
oder Generalprobenausführung. Token-/Geldverbrauch bleiben unbekannt; ein
Paket, ein PR und zwei Kandidaten sind Umfangsgrenzen, kein Providerlimit.
PR-Integration ist der Checkpoint.

Zwei synthetische Regressionen und die fokussierte Suite bestehen lokal mit 218
Tests unter Python 3.14. Alle fünf PR-Gates einschließlich der gepinnten
CPython-3.12.16-Offlineprüfung bestanden. PR #768 integrierte den Schnitt als
`ce1ba20de3186e9c589374c63d6795b4a12c4ec2`; `main` ist synchronisiert und
lokale/Remote-Branches sind entfernt. Kein Interpreter-, Profil-, Worker-,
SQL-, Lab- oder Generalprobenlauf.

### Abgeschlossen: Implementierungsnamensfact wirksam erzwingen
(15. November 2026)

Ein Arbeitspaket und ein PR entfernen den unbedingten `cpython`-Zielwert für
`sys.implementation.name`, damit ausschließlich der gepinnte Quellfact die
Bedingung auflösen kann. Die synthetische Regression prüft unknown ohne Fact
und eine Auflösung mit gültigem Fact. Keine neue Produktquelle und keine
Runtime-, Profil-, Worker-, SQL-, Lab- oder Generalprobenausführung.
Token-/Geldverbrauch bleiben unbekannt; PR-Integration ist der Checkpoint.

Die fokussierte Suite besteht lokal mit 218 Tests unter Python 3.14. Alle fünf
PR-Gates einschließlich der gepinnten CPython-3.12.16-Offlineprüfung bestanden.
PR #769 integrierte den Schnitt als `87dbd9a8e3bde1d8db57a60518a0808cf3896da1`;
`main` ist synchronisiert und lokale/Remote-Branches sind entfernt.

### Begrenzte Fortsetzung: CPython-Implementierungsfacts an echter Quelle
(15. November 2026)

Ein Arbeitspaket und ein PR korrigieren die synthetisch angenommene
Funktionsgrenze in `sysmodule.c` anhand des vorhandenen gepinnten
CPython-3.12.16-Quellarchivs. Zwei Regressionen decken die echte Deklarations-
und Präprozessorgrenze sowie die bisherige falsche Grenze ab. Der Lauf muss die
Versions-, Namens- und Cache-Tag-Facts tatsächlich aus dem Archiv emittieren.
Keine Runtime-, Profil-, Worker-, SQL-, Lab- oder Generalprobenausführung.
Token-/Geldverbrauch bleiben unbekannt; PR-Integration ist der Checkpoint.

### Begrenzte Fortsetzung: Zielimage-Dateiidentitäten ausweisen
(15. November 2026)

Ein Arbeitspaket und ein PR erweitern die bereits digest- und DiffID-geprüfte
OCI-Pfadprüfung um explizite Ausgabefelder für den Executable-SHA-256, das
Symlinkziel `/usr/local/bin/python3` und den `_pickle`-Extension-SHA-256.
Zwei Regressionen müssen die Werte aus den gehashten Layerbytes prüfen. Diese
Felder verbessern die spätere S15-Dateiauswahl; sie belegen weder
`sys.executable` noch die vollständige Dateiauswahl oder P11-Records. Keine
Runtime-, Profil-, Worker-, SQL-, Lab- oder Generalprobenausführung.
Token-/Geldverbrauch bleiben unbekannt; der Checkpoint umfasst ein Paket und
einen PR. PR-Integration ist der Checkpoint; danach wird anhand des aktuellen
Status weitergearbeitet.

Die Dateiidentitäten sind mit 218 fokussierten Tests und allen fünf PR-Gates
bestanden. PR #772 integrierte den Schritt als
`659574ac6dae8fa360c3ea09568e4cde7794bd69`; `main` ist synchronisiert,
lokale und Remote-Branches sind entfernt.

### Begrenzte Fortsetzung: Zielimage-Sysconfigwerte für S15-ABI binden
(15. November 2026)

Ein Arbeitspaket und ein PR prüfen die aus der gepinnten OCI-Layerdatei
`_sysconfigdata__linux_x86_64-linux-gnu.py` gelesenen Literalwerte für
`SOABI`, `DESTSHARED`, `EXT_SUFFIX` und `MULTIARCH`. Zwei Regressionen decken
die Image-Layerbindung und die Zurückweisung einer ungebundenen oder nicht
literal interpretierbaren Datei ab. Das liefert statische Sollwertkandidaten
für `abi` und den Extensionroot; keine Runtime-Sysconfigaufnahme,
P11-Inventur, Profil- oder Workerattestation. Keine SQL-, Lab- oder
Generalprobenausführung. Token-/Geldverbrauch bleiben unbekannt; der
Checkpoint umfasst ein Paket und einen PR. PR-Integration ist der Checkpoint;
danach wird anhand des aktuellen Status weitergearbeitet.

Der Sysconfigdata-Fact ist mit 219 fokussierten Tests und allen fünf PR-Gates
bestanden. PR #773 integrierte ihn als
`a5ecf1486b20757f90c40cabe14c12b4be0d88b1`; `main` ist synchronisiert,
lokale und Remote-Branches sind entfernt.

### Begrenzte Fortsetzung: fehlenden POSIX-ZIP-Landmark-Kandidaten binden
(15. November 2026)

Ein Arbeitspaket und ein PR binden die exakte `ZIP_LANDMARK`-Vorlage aus dem
gepinten `Modules/getpath.py` und prüfen die Abwesenheit des ausgewählten
`/usr/local/lib/python312.zip`-Pfads über alle sieben digest-/DiffID-geprüften
OCI-Layer. Zwei Regressionen decken die Quellvorlage, die fehlende Zieldatei
und das fail-closed-Verhalten bei vorhandener Datei ab. Das belegt weder die
Runtime-`sys.path`-Mitgliedschaft noch eine vollständige `inert_zip`-Auswahl.
Keine Runtime-, Profil-, Worker-, SQL-, Lab- oder Generalprobenausführung.
Token-/Geldverbrauch bleiben unbekannt; der Checkpoint umfasst ein Paket und
einen PR. PR-Integration ist der Checkpoint; danach wird anhand des aktuellen
Status weitergearbeitet.

Der ZIP-Landmark-Kandidat ist mit 221 fokussierten Tests und allen fünf PR-Gates
bestanden. PR #774 integrierte ihn als
`d899c971b1658aa219466531dc2755a83a86efcc`; `main` ist synchronisiert,
lokale und Remote-Branches sind entfernt.

### Begrenzte Fortsetzung: Prefix-Landmarks im Zielimage binden
(15. November 2026)

Ein Arbeitspaket und ein PR prüfen die gepinnten `getpath.py`-Landmarks für
`os.py` und `lib-dynload` gegen die OCI-Layer, binden `os.py` bytegenau an das
Quellarchiv und weisen die Abwesenheit der beiden möglichen `pyvenv.cfg`-Dateien
sowie des `pybuilddir.txt`-Buildmarkers nach. Zwei Regressionen decken die
Landmark-Auswahl und die fail-closed-Gegenprobe bei vorhandenem Venvmarker ab.
Das liefert nur Prefix-/Exec-Prefix-Kandidaten unter der festen Route, keine
Zielruntimewerte und keine vollständige S15-Auswahl. Keine Runtime-, Profil-,
Worker-, SQL-, Lab- oder Generalprobenausführung. Token-/Geldverbrauch bleiben
unbekannt; der Checkpoint umfasst ein Paket und einen PR. PR-Integration ist
der Checkpoint; danach wird anhand des aktuellen Status weitergearbeitet.

Die Prefix-Landmark-Kandidaten sind mit 221 fokussierten Tests und allen fünf
PR-Gates bestanden. PR #775 integrierte sie als
`a6af304b9b3a6a5478327cfabab1800200a078db`; `main` ist synchronisiert,
lokale und Remote-Branches sind entfernt.

### Begrenzte Fortsetzung: geordnete `sys.path`-Kandidaten binden
(15. November 2026)

Ein Arbeitspaket und ein PR erweitern die gepinnten `getpath.py`-Landmarks um
ihre POSIX-Anfügereihenfolge und verbinden sie mit den digestgebundenen
Sysconfig-Buildwerten und den verifizierten Zielimage-Pfaden. Zwei Regressionen
decken die Kandidatenfolge und die fail-closed-Ablehnung bei einer zusätzlichen
kompilierten `PYTHONPATH`-Angabe ab. Die ausgegebene Liste bleibt eine
Sollwertkandidatur; unbekannte Startup-Overrides, die vollständige operative
Auswahl und eine tatsächliche `sys.path`-Aufnahme bleiben offen. Keine Runtime-,
Profil-, Worker-, SQL-, Lab- oder Generalprobenausführung. Token-/Geldverbrauch
bleiben unbekannt; der Checkpoint umfasst ein Paket und einen PR.
PR-Integration ist der Checkpoint; danach wird anhand des aktuellen Status
weitergearbeitet.

Die `sys.path`-Sollwertkandidaten sind mit 222 fokussierten Tests und allen fünf
PR-Gates bestanden. PR #776 integrierte sie als
`710ff0089f9507624b620627d1b4f7d1adebb151`; `main` ist synchronisiert,
lokale und Remote-Branches sind entfernt.

### Begrenzte Fortsetzung: `._pth`-Overrides für den Suchpfad ausschließen
(15. November 2026)

Ein Arbeitspaket und ein PR binden den `._pth`-Overridezweig im gepinnten
`getpath.py` und prüfen die drei durch Executable, Library-Namen und verifizierte
Sysconfigwerte festgelegten Markerorte in allen OCI-Layern. Zwei Regressionen
decken die Abwesenheit im positiven Imagefall und die Ablehnung bei einem
vorhandenen Marker ab. Das schließt nur diesen konkreten Suchpfad-Override aus;
keine Runtime-`sys.path`-Aufnahme, vollständige Overrideinventur oder S15-
Attestation. Keine Runtime-, Profil-, Worker-, SQL-, Lab- oder
Generalprobenausführung. Token-/Geldverbrauch bleiben unbekannt; der
Checkpoint umfasst ein Paket und einen PR. PR-Integration ist der Checkpoint;
danach wird anhand des aktuellen Status weitergearbeitet.

### Begrenzte Fortsetzung: direkten Sysconfig-Umgebungsoverride entfernen
(15. November 2026)

Die `sysconfig`-Quelle liest `_PYTHON_SYSCONFIGDATA_NAME` unmittelbar über
`os.environ`; das isolierte Startupflag `-I` schützt diesen direkten Zugriff
nicht. Ein Arbeitspaket und ein PR ergänzen deshalb den vorhandenen
Import-Only-Caller um eine Kindumgebungskopie, aus der genau diese Variable vor
`Popen` entfernt wird. Der quellengebundene Resolver akzeptiert das Routenfact
nur bei exakter CPython-Quell-, argv- und Filterbindung. Zwei Regressionen
prüfen die positive/negative statische Routenbindung und die tatsächliche
Entfernung aus der synthetisch gesetzten Elternumgebung. Andere Variablen
bleiben erhalten; daraus folgt keine Hostisolation, Zielruntime- oder
Sysconfigaufnahme. Keine vollständige Importclosure, P11-Inventur,
Profilattestation, SQL-/Lab-Ausführung oder menschliche Generalprobe.
Token-/Geldverbrauch bleiben unbekannt; die harte Umfangsgrenze ist ein Paket,
ein PR und zwei Regressionen, kein Provider-Ausgabenlimit. PR-Integration ist
der Checkpoint; anschließend wird autonom mit dem nächsten offenen Thema
fortgefahren.

### Begrenzte Fortsetzung: `sys.implementation._multiarch` quellenbinden
(15. November 2026)

Ein Arbeitspaket und ein PR binden das von `sysconfig` genutzte
`sys.implementation._multiarch` an die digestgeprüfte CPython-3.12.16-
`sysmodule.c`-Zuweisung aus `MULTIARCH` und den gepinnten Zielimagewert
`x86_64-linux-gnu`. Der Fact wird nur bei passendem Imagepfad und
Sysconfigdatenhash ausgegeben; Abweichungen bleiben unbekannt. Eine Regression
prüft Quell-/Imagebindung und Weitergabe an die Bedingungsauswertung. Der echte
Archiv-/OCI-Kandidatenscan muss den Wert ausgeben. Das ist weder eine
Runtimebeobachtung noch eine vollständige Sysconfigmodul-, Importclosure- oder
P11-Bindung. Keine SQL-, Lab- oder menschliche Generalprobenausführung.
Token-/Geldverbrauch bleiben unbekannt; die Umfangsgrenze ist ein Paket, ein
PR und höchstens zwei Regressionen, kein Provider-Ausgabenlimit.
PR-Integration ist der Checkpoint; danach wird autonom anhand des dann offenen
Status weitergearbeitet.

### Begrenzte Fortsetzung: `sys.abiflags` quellenbinden
(15. November 2026)

Ein Arbeitspaket und ein PR binden `sys.abiflags` an die gepinnte
CPython-3.12.16-`sysmodule.c`-Abbildung von `ABIFLAGS` und den leeren
Sysconfigdaten-Literalwert. Eine Regression prüft den positiven Fact, seine
Nutzung durch die Bedingungsauswertung und die Ablehnung geänderter Quelle oder
Imagefacts. Die Imagefixture wird um den vorhandenen Literalwert ergänzt. Der
echte Archiv-/OCI-Kandidatenscan muss den Fact ausgeben. Keine Runtime- oder
Sysconfigaufnahme, vollständige Importclosure, P11-Inventur, SQL-/Lab- oder
menschliche Generalprobenfreigabe. Token-/Geldverbrauch bleiben unbekannt; der
Umfang ist ein Paket, ein PR und höchstens zwei Regressionen, kein
Provider-Ausgabenlimit. PR-Integration ist der Checkpoint.

### Begrenzte Fortsetzung: `sys.platform` aus Quelle und Zielimage binden
(15. November 2026)

Ein Arbeitspaket und ein PR ersetzen den unbedingten Linux-Wert des
Bedingungsresolvers durch einen Fact, der die CPython-Zuweisung über
`Py_GetPlatform()`, dessen Implementierung, die Buildregel für `PLATFORM` und
`MACHDEP=linux` im verifizierten Zielimage gemeinsam bindet. Eine Regression
prüft die positive Quellen-/Imagekette, Abweichungen und den unbekannten
Resolverzustand ohne Fact. Der echte Archiv-/OCI-Lauf muss den Fact ausgeben.
Der Ergebnisumfang bleibt eine statische Kandidatenanalyse, keine
Runtimeaufnahme, vollständige Importclosure, P11-Attestation oder menschliche
Generalprobe. Token-/Geldverbrauch bleiben unbekannt; harte Grenze: ein Paket,
ein PR, höchstens zwei Regressionen. PR-Integration ist der Checkpoint; danach
wird anhand des dann offenen Status autonom weitergearbeitet.

### Begrenzte Fortsetzung: Sysconfigdaten-Modulnamen zusammensetzen
(15. November 2026)

Ein Arbeitspaket und ein PR ergänzen den festen `sysconfig.py`-Fallbacknamen
aus `sys.abiflags`, `sys.platform` und `sys.implementation._multiarch`. Die
Ausgabe erfordert zusätzlich den quellengebundenen Workerfact, dass
`_PYTHON_SYSCONFIGDATA_NAME` aus der Kindumgebung entfernt wird. Eine
Regression deckt den positiven Fall und Änderungen an Template, Komponenten
oder Route ab; der echte Archiv-/OCI-Lauf muss
`_sysconfigdata__linux_x86_64-linux-gnu` liefern. Das ist nur ein statischer
Namenskandidat, kein Datei-, Import- oder Runtimebeleg. Token-/Geldverbrauch
bleiben unbekannt; harte Grenze: ein Paket, ein PR, höchstens zwei
Regressionen. PR-Integration ist der Checkpoint; danach wird autonom anhand des
aktuellen offenen Status fortgesetzt.

### Begrenzte Fortsetzung: Sysconfigdaten-Modulpfad an Image-Datei binden
(15. November 2026)

Ein Arbeitspaket und ein PR verbinden den zusammengesetzten Modulnamen mit dem
konkreten Zielimage-Mitglied nur, wenn Basisname, Pfad und SHA-256 mit dem
gepinnten Filefact übereinstimmen. Eine Regression deckt Übereinstimmung und
Abweichungen ab; der echte OCI-Lauf muss Pfad und Digest bestätigen. Das bleibt
statische Dateiidentität ohne Import oder Interpreterlauf. Token-/Geldverbrauch
bleiben unbekannt; harte Grenze: ein Paket, ein PR und höchstens zwei
Regressionen. PR-Integration ist der Checkpoint; danach wird autonom anhand
des offenen Status weitergearbeitet.

### Begrenzte Fortsetzung: Sysconfigdaten-Importziel zusammenführen
(15. November 2026)

Ein Arbeitspaket und ein PR verbinden die geprüfte `sysconfig.py`-Importform
`__import__(name, ..., ['build_time_vars'], 0)` mit dem aufgelösten Namensfact
und dem digestgebundenen Image-Dateikandidaten. Eine Regression prüft Route,
Attribut, Pfad und fail-closed-Abweichungen; der echte OCI-Lauf muss das
Importziel ausgeben. Das ist ein statischer Importzielkandidat ohne Funktions-
oder Interpreterausführung. Token-/Geldverbrauch bleiben unbekannt; harte
Grenze: ein Paket, ein PR und höchstens zwei Regressionen. PR-Integration ist
der Checkpoint; danach wird autonom anhand des offenen Status fortgesetzt.

### Begrenzte Fortsetzung: `os.name` aus Posix-Quelle und Zielimage ableiten
(15. November 2026)

Ein Arbeitspaket und ein PR entfernen den unbedingten `os.name='posix'`-Wert
aus dem Resolver. Der Fact hängt an `os.py`, den Posix-Quellen und der
Builtinmodulregistrierung des festgelegten Zielimages; ohne diese Kette bleibt
der Wert unbekannt. Eine Regression deckt Fact und Unbekannt-Fall ab, der echte
Archiv-/OCI-Scan muss ihn weiterhin entscheiden. Keine Runtime-, Profil-, P11-,
SQL-, Lab- oder Generalprobenattestation. Token-/Geldverbrauch bleiben
unbekannt; harte Grenze: ein Paket, ein PR, höchstens zwei Regressionen.
PR-Integration ist der Checkpoint; anschließend wird autonom fortgesetzt.

### Begrenzte Fortsetzung: quellengebundener `_init_posix`-Aufruf
(15. November 2026)

Ein Arbeitspaket und ein PR geben die Zeile `_init_posix(_CONFIG_VARS)` in
`sysconfig._init_config_vars` nur bei passendem CPython-Quellhash, exakter
Guardform und bereits belegtem `os.name='posix'` frei. Eine Regression prüft
die Call-Closure-Auswahl und Quellenabweichung; der echte Archiv-/OCI-Lauf
bindet den Aufruf an CPython-Zeile 676. Das ist statische Call-Closure-Evidenz,
keine Funktionsausführung oder Runtimeattestation. Token-/Geldverbrauch bleiben
unbekannt; harte Grenze: ein Paket, ein PR, höchstens zwei Regressionen.
PR-Integration ist der Checkpoint; danach wird anhand des offenen Status
autonom weitergearbeitet.

### Begrenzte Fortsetzung: bedingte Sysconfig-Importroute zusammenführen
(15. November 2026)

Ein Arbeitspaket und ein PR verbinden den quellengebundenen `_init_posix`-
Aufruf, den Sysconfigdaten-Modulnamen, das digestgebundene Image-Mitglied und
den `build_time_vars`-Consumer zu einem `STATIC_CONDITIONAL_IMPORT_ROUTE_CANDIDATE`.
Eine Regression prüft die Voraussetzungen der Zusammenführung; der echte
Archiv-/OCI-Lauf muss die Route ausgeben. Der Datensatz belegt keinen
Initializeraufruf oder Import. Token-/Geldverbrauch bleiben unbekannt; harte
Grenze: ein Paket, ein PR, höchstens zwei Regressionen. PR-Integration ist der
Checkpoint; danach wird autonom anhand des offenen Status fortgesetzt.

Für die anschließende DGN-007-Fortsetzung gilt ein einzelnes Paket mit einem
PR und höchstens zwei Regressionen. Es verbindet den bereits digestgeprüften
`build_time_vars`-Literal-Dictionary-Fact aus der OCI-Datei mit der statischen
Sysconfig-Importroute. Der Scanner bleibt `CANDIDATES_ONLY`; keine Datei- oder
Interpreterausführung, vollständige Importclosure, P11-, SQL-/Lab- oder
menschliche Generalprobenattestation. PR-Integration ist der Checkpoint; der
autonome Auftrag setzt danach mit dem dann offenen Punkt fort.

Die nächste einzelne DGN-007-Fortsetzung bindet im bestehenden Rahmen von
höchstens einem Arbeitspaket, einem PR und zwei Regressionen den statisch
geprüften `vars.update(build_time_vars)`-Schritt an den Aufrufparameter
`_CONFIG_VARS`. Der Kandidat dokumentiert Quell-/Image-Datenfluss, nicht die
Ausführung der Mutation. Weiterhin ausgeschlossen sind vollständige
Importclosure, P11, SQL/Lab und menschliche Generalprobe.

Die nächste DGN-007-Welle bleibt auf ein Paket, einen PR und höchstens zwei
Regressionen begrenzt. Sie bindet den gepinnten `get_config_vars()`-Erstaufruf
von `_init_config_vars()` an den initialen Config-Variablenzustand, Lock und
Null-Recheck und führt ihn mit der bereits statischen POSIX-Importroute
zusammen. Keine Behauptung eines tatsächlichen Getter-/Initializerlaufs,
Runtimeprofils, P11, SQL/Lab oder menschlicher Generalprobe.

Der nächste DGN-007-Punkt bleibt auf ein Paket, einen PR und höchstens zwei
Regressionen begrenzt. Er ordnet die 14 festgelegten Werte des
`build_time_vars`-Image-Literals dem statischen `vars.update`-Datenfluss und
`_CONFIG_VARS` als Zielmapping zu. Es entstehen keine Runtimewerte und keine
Import-, P11-, SQL-/Lab- oder Generalprobenfreigabe.

Der nächste DGN-007-Schnitt bleibt auf ein Paket, einen PR und höchstens zwei
Regressionen begrenzt. Er bindet die geprüften Rückgabepfade von
`get_config_vars()` und `get_config_var()` an den statischen
`_CONFIG_VARS`-Datenfluss. Der Status bleibt `CANDIDATES_ONLY`; keine
Zielruntime-, P11-, SQL-/Lab- oder Generalprobenattestation.

Der nächste DGN-007-Punkt bleibt auf ein Paket, einen PR und höchstens zwei
Regressionen begrenzt. Er verbindet die 14 post-initialisierten
`_CONFIG_VARS`-Eintragskandidaten mit den bereits geprüften Rückgabepfaden der
öffentlichen Sysconfig-APIs. Die Resultate bleiben statische Kandidaten, keine
beobachteten Runtimewerte oder vollständige Profilattestation.

Der folgende DGN-007-Punkt bleibt auf ein Paket, einen PR und höchstens zwei
Regressionen beschränkt. Er verbindet die 14 post-initialisierten
`_CONFIG_VARS`-Wertekandidaten mit den statischen Rückgabeformen der öffentlichen
Sysconfig-APIs und macht die Annahme keiner intervenierenden Mutation
explizit. Keine Zielruntime- oder Profilattestation.

Die nächste DGN-007-Fortsetzung bleibt auf ein Paket, einen PR und höchstens
zwei Regressionen beschränkt. Sie bindet `_CONFIG_VARS_INITIALIZED=True` ans
Ende des POSIX-Initialisierungspfads und führt diese Abschlussmarke mit dem
bereits geprüften Erstaufruf-/API-Kandidaten zusammen. Keine Ausführungs- oder
Runtimeattestation.

## Abgeschlossen: Import-Finder-Registrierungsstellen binden

PR #801 bindet die drei digestgeprüften `sys.meta_path.append`-Stellen für
`BuiltinImporter`, `FrozenImporter` und `PathFinder` sowie die
`FileFinder.path_hook`-Registrierung an die geprüften `_install`-Funktionen.
Der echte CPython-3.12.16-Quellarchivlauf und 239 fokussierte Regressionen
bestanden. Zusätzliche Meta-Path-Aufrufe und eine geänderte Hook-Registrierung
werden fail-closed verworfen. Endgültige Runtimelisten und ihre vollständige
Reihenfolge bleiben unbelegt.

## Abgeschlossen: bedingte Zipimport-Hookquelle binden

PR #802 bindet die digestgeprüften Funktionen `init_zipimport()` und
`_PyImport_InitExternal()` aus `Python/import.c`. Der Kandidat prüft die
bedingte Auflösung von `zipimport.zipimporter`, die Einfügung an Position 0,
den fehlenden Attribut- und Einfügefehlerpfad sowie die Reihenfolge nach
erfolgreicher Importlib-External-Initialisierung. Der Archivlauf und 240
fokussierte Regressionen bestanden. Runtimelisten oder tatsächliche
Listenänderungen sind damit nicht belegt.

## Abgeschlossen: FileFinder-Hookfactory binden

PR #803 bindet `_get_supported_file_loaders()` und `FileFinder.path_hook()`
an die digestgeprüfte Importlib-Quelle. Der Kandidat weist die deklarative
Loaderreihenfolge, Hook-Closure, Verzeichnisguard und den `ImportError`-Pfad
aus. Der echte Archivlauf und 241 fokussierte Regressionen bestanden; die
Gegenproben verwerfen eine geänderte Loaderreihenfolge oder einen geänderten
Guard. Installierte Runtimeloader und eine erzeugte Hookinstanz bleiben
unbelegt.

## Abgeschlossen: Zipimporter-Attributquelle binden

PR #804 bindet den C-seitig angeforderten Attributnamen `zipimport.zipimporter`
an die digestgeprüfte Top-Level-Klasse, den deklarierten Basistyp und den
Literalexport `__all__`. Der echte Archivlauf und 242 fokussierte Regressionen
bestanden; Klassenumbenennung und Exportänderung werden fail-closed verworfen.
Ein erfolgreicher Modulimport oder Runtimewert ist damit nicht belegt.

## Abgeschlossen: Zipimporter-Attributquelle binden

PR #804 bindet den C-seitig angeforderten Attributnamen `zipimport.zipimporter`
an die digestgeprüfte Top-Level-Klasse, den deklarierten Basistyp und den
Literalexport `__all__`. Der echte Archivlauf und 242 fokussierte Regressionen
bestanden; Klassenumbenennung und Exportänderung werden fail-closed verworfen.
Ein erfolgreicher Modulimport oder Runtimewert ist damit nicht belegt.

## Abgeschlossen: Meta-Path-Finderklassen binden

Der nächste S15-Schnitt ordnet die registrierten Labels `BuiltinImporter`,
`FrozenImporter` und `PathFinder` den eindeutigen Top-Level-Klassen in den
gepinnten Bootstrapquellen zu und prüft die jeweiligen `find_spec`-
Klassenmethoden. PR #805 ist integriert; Archivlauf und 243 fokussierte
Regressionen bestanden. Klassenumbenennung und fehlender Klassenmethoden-
Descriptor werden fail-closed verworfen. Das sind Quellfakten, keine
Runtimeinstanzen oder Auswahlbeobachtungen.

## Abgeschlossen: `inert_zip`-Feld an Pfadkandidaten binden

PR #806 verbindet den als abwesend belegten `ZIP_LANDMARK`-Imagepfad mit dem
ersten Wert der geordneten `sys.path`-Sollwertkandidatur und weist denselben
Wert als `inert_zip`-Feldkandidat aus. 244 fokussierte Regressionen und alle
fünf PR-Gates bestanden. Für diesen Schritt lag lokal kein verifiziertes
Docker-save-Zielimage vor; die Layer-/Pfadbindung ist durch synthetische
Imagefixtures geprüft. Eine Runtimeaufnahme oder ein vollständiger S15-Record
ist damit nicht belegt.

## Abgeschlossen: Bibliotheksroots binden

PR #807 bindet den Standardbibliotheksroot an den zweiten geordneten
`sys.path`-Pfadkandidaten und den Extensionroot an `DESTSHARED`. Der Kandidat
verlangt die Übereinstimmung mit dem dritten Pfadkandidaten und dem geprüften
`_pickle`-Extensionfakt. 244 fokussierte Regressionen und alle fünf PR-Gates
bestanden. Für diesen Schnitt lag lokal kein verifiziertes Docker-save-
Zielimage vor; die feste Pfadbindung wurde mit synthetischen OCI-Layern
geprüft. Runtime-Roots bleiben unbelegt.

## Abgeschlossen: ausgewählte Dateifingerprints binden

PR #808 bildet höchstens zwei `files`-Einträge: das geprüfte Executabletarget
und die `_pickle`-Datei innerhalb des ausgewählten Extensionroots. Größen,
SHA-256 sowie Einzel- und Gesamtkappen sind gebunden; eine vollständige
Dateiliste ist nicht behauptet. 244 fokussierte Regressionen und alle fünf
PR-Gates bestanden. Das lokale Image-Evidence nutzt synthetische OCI-Layer;
ein verifiziertes Docker-save-Zielimage lag nicht vor.

## Abgeschlossen: ABI-Feldkandidat binden

PR #809 bindet `abi` an `SOABI` aus der digestgeprüften Zielimage-
`_sysconfigdata`-Datei. 244 fokussierte Regressionen und alle fünf PR-Gates
bestanden. Das belegt keine Runtime-ABI oder vollständige S15-Auswahl.

## Abgeschlossen: Platform-Feldkandidat binden

PR #810 verbindet `sys.platform` aus dem geprüften `Py_GetPlatform`-Pfad mit
`MACHDEP=linux` der digestgeprüften Zielimage-`_sysconfigdata`-Datei. 244
fokussierte Regressionen und alle fünf PR-Gates bestanden; die Ausgabe bleibt
statisch.

## Abgeschlossen: Implementation-Feldkandidat binden

PR #811 bindet `implementation` an `sys.implementation.name` aus der
digestgeprüften CPython-`sysmodule.c`-Quelle. 244 fokussierte Regressionen und
alle fünf PR-Gates bestanden; der Kandidat bleibt statisch.

## Abgeschlossen: Versionsfeld binden

PR #812 leitet `(3, 12, 16)` aus `sys.implementation.version` ab und bindet
den Quellfakt an dasselbe deklarierte `version_info`-Objekt wie
`sys.version_info`. 244 fokussierte Regressionen und alle fünf PR-Gates
bestanden; der Kandidat behauptet keine Runtimeversion.

## Abgeschlossen: Executable-Feld binden

PR #813 bindet `executable` und `executable_target` an denselben regulären,
nicht-symlinkten Image-Member `/usr/local/bin/python3.12` samt Digest. 244
fokussierte Regressionen und alle fünf PR-Gates bestanden; Runtimewerte wurden
nicht beobachtet.

## Abgeschlossen: Prefix-Feldkandidat binden

PR #814 bindet alle vier Prefixwerte an Zielimage-Landmarks, digestgeprüfte
Sysconfigdaten, leere `PyConfig`-Defaults und geprüfte GetPath-Fallbacks. 245
fokussierte Regressionen und alle fünf PR-Gates bestanden; es entsteht keine
Runtimeaufnahme.

## Abgeschlossen: Finder-Feldkandidat binden

PR #815 verbindet die drei Meta-Path-Registrierungen mit den geprüften
`BuiltinImporter`-, `FrozenImporter`- und `PathFinder`-Klassendeklarationen.
245 fokussierte Regressionen und alle fünf PR-Gates bestanden; es entsteht
keine Runtime-Finderliste.

## Abgeschlossen: Hook-Feldkandidat binden

PR #816 verbindet die bedingte Zipimporter-Einfügung an Position null mit der
zuvor ausgeführten FileFinder-Registrierung und den digestgeprüften Hook- und
Klassendeklarationen. 246 fokussierte Regressionen und alle fünf PR-Gates
bestanden; Runtime-Hookobjekte bleiben unbelegt.

## Abgeschlossen: S15-Assumption-Feldkandidat

PR #817 bindet den festen `ASSUMPTION`-Text an genau eine
Top-Level-Literaldefinition und den verifizierten Modulhash. Der Kandidat ist
deklarativ und keine Trustattestation.

## Abgeschlossen: S15-Flags-Feldkandidat

PR #818 verbindet die sechs geordneten Flags mit den quell- und
Worker-routengebundenen CPython-Facts und prüft `sys.dont_write_bytecode` als
zusätzliche Routenbindung. Das Ergebnis bleibt statisch und ist keine
Runtimeaufnahme.

## Abgeschlossen: S15-Paths-Feldkandidat

PR #819 verbindet den geordneten Pfadkandidaten mit `inert_zip` und den
Bibliotheksroots. Der statische Kandidat behauptet keine Runtime-`sys.path`.

## Abgeschlossen: S15-Roots-Feldkandidat

PR #820 gibt das verifizierte Standardbibliotheks- und Extensionroot-Paar als
eigenes Feld aus; die Werte bleiben statische Sollwertkandidaten.

## Abgeschlossen: S15-Inert-ZIP-Feldkandidat

PR #821 stellt die an Image-Abwesenheit und Pfadposition null gebundene
ZIP-Landmark-Aussage als eigenes Feld bereit; Runtime-Pfadmitgliedschaft wird
nicht behauptet.

## Abgeschlossen: S15-Files-Feldkandidat

PR #822 bündelt die gehashten Executable- und `_pickle`-Dateikandidaten unter
den Einzel- und Gesamtkappen. Die Dateiliste bleibt ausdrücklich unvollständig.

## Abgeschlossen: S15-Installationstupel

PR #823 ordnet die 15 statischen Feldkandidaten in ein Installationstupel ein.
Runtimeaufnahme, Profilselektion und vollständige Dateiliste werden nicht
behauptet.

## Abgeschlossen: S15-Installationstupel an Profilschema binden

PR #824 bindet die Schemaordnung an die kanonisch gehashte
`_selected_shapes`-Quelle. LF und CRLF liefern denselben Quellenfingerprint;
Runtime- oder Profilvalidierung wird nicht behauptet.

## Abgeschlossen: Controls-Auswahlvertrag

PR #825 bindet erlaubte Namen, Höchstzahl, Eindeutigkeit und
`CONTROL`-Record-Zuordnung an die Runtime-Profilquelle. Die tatsächlich
gewählte Menge bleibt unbekannt.

## Abgeschlossen: Auswahl-Eingaben zusammensetzen

PR #826 verbindet die festen Auswahlwerte mit der quellgebundenen
`selection`-Tupelordnung und dem Controls-Vertrag. Der statische Vertrag
behauptet keine gewählte Control-Menge oder validierte Profilauswahl.

## Abgeschlossen: Skalarprojektion-Schema binden

PR #827 band die drei Rückgaben `selection`, `installation` und Modulzeilen
statisch. PR #828 korrigierte die Feldzuordnung: Das
Installationsprojektionstupel hat zwölf Felder und bleibt vom 15-Feld-
Profilrecord getrennt. Es werden keine projizierten Werte, Runtimeaufnahme
oder Profilauswahl behauptet.

## Abgeschlossen: Auswahlform statisch binden

PR #829 bindet die Grenzen aus `_selected_shapes`: Installations- und
Modulzeilenlänge, Tokenlänge, Controls-Obergrenze und Eindeutigkeit sowie
sortierte eindeutige Modulnamen und Control-Record-Zuordnung. Es werden keine
tatsächlich ausgewählten Werte behauptet.

## Abgeschlossen: Profilbinder-Ablauf statisch binden

PR #830 bindet die vorgelagerte Formprüfung, Fehlerabbildungen und
Erfolgsrückgabe des Profilbinders. Die tatsächliche Profilbindung bleibt offen.

## Abgeschlossen: Ankerbindung des Profilbinders binden

PR #831 bindet Cachekopie, Modulzeilenabbildung, wiederholte Form- und
Projektionsprüfungen sowie Cacheanker-Identität. Keine Ankeraufnahme oder
Runtimebeobachtung wird behauptet.

## Abgeschlossen: ausgewählte Beobachtungsfolge statisch binden

PR #832 bindet Reihenfolge, Projektion, Schlussaufnahme, Hook-/POST-Prüfungen
und Ergebnisreports des ausgewählten Beobachters. Keine Runtimeattestation.

## Abgeschlossen: aktuelle Skalaraufnahme statisch binden

PR #833 bindet Recordaufnahme, Profilvergleiche, FileFinder-Hookaufnahmen,
Skalarprojektion und Fehlerreport des inneren Beobachters. Keine Runtimeaufnahme
wird behauptet.

## Abgeschlossen: frischen Record-Capture-Ablauf binden

PR #834 bindet Vorher-/Nachher-Capture, begrenzte Dateihashreads, Caps,
Profilvergleiche und success-only Recordrückgabe an die Profilquelle. Keine
Runtime- oder Trustattestation.

## Abgeschlossen: Capture-Observation-Schema binden

PR #835 bindet begrenzte Modul-/Pfadsnapshots, sortierte Modulnamen und die
Feldreihenfolge des `Observation`-Konstruktors. Keine ausgeführte Aufnahme.

## Abgeschlossen: Modulrecord-Builder binden

PR #836 bindet Modul-/Spec-Identität, Frozen-Aliase, Loaderklassifikation,
Ablehnung unbekannter Loader und die `ModuleRecord`-Feldordnung. Beobachtete
Module werden nicht behauptet.

## Abgeschlossen: Profilvergleichsvertrag binden

PR #837 bindet Interpreter-/Plattform-/Flagvergleiche, Modulanker,
Projektausschluss, Control-/Rootzuordnung und Pfadbeschränkung in `_compare`.
Der Vergleich begründet kein Vertrauen.

## Abgeschlossen: Validierungsreports binden

PR #838 bindet `validate_profile` an Vertragsablehnung, ungültigen Record und
Matchreport mit `trust_assumed` ausschließlich beim Match. Keine Attestation.

## Begrenzte Fortsetzung: Profil- und Observation-Formvertrag binden

PR #840 bindet `_shape` an die getrennten Deklarations- und Observationformen,
gemeinsame Feldgrenzen, Finder-/Hookinstanzen, Recordvalidator-Delegation und
die jeweils branch-spezifischen Annahme-/Root-/Control-/Fingerprint- bzw.
Plattform-/Flagbedingungen. Es wird keine validierte Eingabe behauptet.

## Abgeschlossen: Profil- und Observation-Formvertrag binden

PR #840 bindet `_shape` an die getrennten Deklarations- und Observationformen
einschließlich ihrer gemeinsamen und branch-spezifischen Feldbedingungen.
Keine validierte Eingabe oder Runtimeaufnahme.

## Abgeschlossen: Modul- und Datei-Recordvalidatoren binden

PR #841 bindet `_records` und `_files`: Modul-/Spec-/Loaderkohärenz, sortierte
eindeutige Namen, Frozen-Aliasanker, Dateidigestform sowie Größen- und
Pfadkappen. Es entsteht keine tatsächliche Recordvalidierung oder Aufnahme.

## Abgeschlossen: absolute und eingeschränkte Pfade binden

PR #842 bindet `_absolute` und `_under` an kanonische
absolute Pfade ohne Traversal sowie Root-Containment. Zwei Gegenproben lockern
je eine Bedingung; es gibt keine Runtime-/Hostattestation.

## Abgeschlossen: primitive Profilvalidatoren binden

PR #843 bindet `_text` und `_strings`: exakter String-/Tupletyp, Zeichen- und
UTF-8-Bytegrenze, maximale Tuplelänge und Textprüfung jedes Elements. Zwei
Gegenproben lockern je eine Grenze. Es wird keine Profilvalidierung behauptet.

## Abgeschlossen: fail-closed Profilfehler binden

PR #844 bindet `_Failure` und `_need`: Fehlerklasse als `ValueError`-Unterklasse,
Standardcode `INVALID_RECORD` und Ablehnung falscher Bedingungen unter Erhalt
des Fehlercodes. Zwei Gegenproben lockern je eine Bedingung. Keine
Profilvalidierung wird behauptet.

## Abgeschlossen: Profilreport-Schema binden

PR #845 bindet die Felder von `ProfileReport`, insbesondere die
nicht initialisierbaren Attestierungs-/Freigabefelder mit Standardwert `False`.
Eine Gegenprobe setzt `runtime_attested` auf `True`; das muss den Kandidaten
verwerfen. Es wird kein Bericht erzeugt oder Vertrauen attestiert.

## Abgeschlossen: Profilmodelle binden

PR #846 bindet die eingefrorenen Dataclass-Feldlayouts von `DeclaredProfile`
und `Observation` in exakter Reihenfolge. Gegenproben ändern ein Feld bzw.
entfernen `frozen=True`. Es wird keine Profilinstanz validiert oder aufgenommen.

## Abgeschlossen: Record-Dataclassschemas binden

PR #847 bindet die eingefrorenen Feldlayouts von `ModuleRecord` und
`FileDigest` in exakter Reihenfolge. Gegenproben ändern ein Feld bzw. entfernen
`frozen=True`. Es werden keine Records validiert oder beobachtet.

## Abgeschlossen: Observation-Ergebnisformen binden

PR #848 bindet die eingefrorenen Feldlayouts von `ObservationResult` und
`ScalarObservationResult`. Gegenproben ändern ein Feld bzw. entfernen
`frozen=True`. Es werden keine Beobachtungen ausgeführt.

## Abgeschlossen: ausgewählte Profil-Ergebnisformen binden

PR #849 bindet `BoundProfileResult` und `SelectedScalarObservationResult`,
einschließlich privater frozen/slotted Form und festem Scope
`PROJECT_SEMANTIC`. Gegenproben lockern Scope bzw. Repräsentationsgrenze. Es
wird keine Runtimeaufnahme behauptet.

## Abgeschlossen: vollständigen Record-Aufnahmepfad binden

PR #850 bindet den geordneten Guard-, Vorher-/Nachheraufnahme-, Datei-Hash-
und Ablehnungspfad von `observe_current_interpreter_records` quellgebunden.
Gegenproben lockern Symlinkschutz und Vorhervergleich. Es wird keine Aufnahme
ausgeführt oder attestiert.

## Abgeschlossen: ausgewählte POST-Verträge binden

PR #851 bindet `_selected_runtime_post` und `_selected_post`: Sollwerte,
Typ-/Bereichsgrenzen und Identität der Runtimeprovider, Container, Finder,
Hooks und Modulanker. Gegenproben lockern Flagsollwerte bzw. Provideridentität.
Es wird keine POST-Prüfung ausgeführt.

## Abgeschlossen: Hook-POST-Vertrag binden

PR #852 bindet Vorher-/Nachheridentität der Hookobjekte sowie die drei
FileFinder-Hookfelder an `_selected_hook_post`. Eine Gegenprobe entfernt den
Wertvergleich des Pfadfelds. Es wird kein Hook beobachtet.

## Abgeschlossen: FileFinder-Hookvertrag binden

PR #853 bindet `_filefinder_hook` an Frozen-Modul-/Klassen-/Descriptor- und
Closureanker sowie Loaderdetail- und Suffixlistenreihenfolge. Gegenproben
lockern die Closureform und vertauschen Loaderdetails. Es wird kein Hook
beobachtet.

## Abgeschlossen: Skalarprojektion binden

PR #854 bindet `_scalar_text` und `_project_scalars`: NUL-Ausschluss,
Kontroll-/Rootprüfungen, Loader-/Aliasanker sowie die geordneten Selection-,
Installation- und Modulzeilenprojektionen. Gegenproben lockern NUL- bzw.
Aliasidentitätsprüfung. Es wird keine Projektion ausgeführt.

## Abgeschlossen: ausgewählte Formprimitiven binden

PR #855 bindet `_selected_tree`, `_selected_tuple` und `_selected_int` an
Knoten-/Tiefen-/Tupelgrenzen und exakte Blatt-/Zahlentypen. Gegenproben lockern
die Tiefengrenze bzw. den exakten Tupletyp. Es werden keine Werte traversiert.

## Abgeschlossen: ausgewählte Namespaces binden

PR #856 bindet `_selected_keys` und `_selected_namespace`: exakter
Dictionary-/Stringtyp, gemeinsame 16.368-Ankerkappe, Budgetzählung und
Skalarprüfung. Gegenproben lockern die Kappe bzw. den exakten Keytyp. Es werden
keine Namespaces gelesen.

## Begrenzte Fortsetzung: lokale Modulanker binden

PR #857 bindet `_selected_local` und `_selected_cache`: exakte Modul-, Spec-
und Loaderformen, Submodulpfadkappen sowie die exakte sortierte Cache-Namensmenge.
Gegenproben lockern Loaderform bzw. Cachemengengleichheit. Es werden keine
Modulanker gelesen.

## Abgeschlossen: ausgewählte Runtime-Container binden

PR #858 bindet `_selected_containers` an den exakten
Runtime-Modultyp, den durch `MAX_RECORDS` begrenzten exakten Dictionary-Cache
sowie Finder- und Hook-Container mit exakt drei bzw. zwei Elementen. Die
Gegenproben lockern den Runtimetyp und die Hooklängengrenze. Es wird kein
Runtimezustand gelesen oder attestiert; 279 Regressionen und alle fünf Gates
bestanden.

## Abgeschlossen: skalare lokale Ankervalidierung absichern

PR #859 schließt die Gegenprobenlücke bei der skalaren Textprüfung von Modul-,
Spec-, Suchpfad- und Loaderankern. 279 fokussierte Regressionen und alle fünf
Pflichtprüfungen bestanden; die Quellen blieben unbeobachtet.

## Abgeschlossen: Runtime-Profiltexte explizit binden

PR #860 schützt die Skalarprüfung der Pfade und sechs Plattformtexte in
`_selected_runtime_post` durch explizite Quellanforderungen und Gegenproben.
279 fokussierte Regressionen und alle fünf Gates bestanden; Runtimewerte blieben
unbeobachtet.

## Abgeschlossen: Runtime-POST-Projektionen absichern

PR #861 bindet Versionprojektion, Startflagbereiche, die geordnete
Pfadprojektion und die Skalartextprüfungen. 279 fokussierte Regressionen und
alle fünf Gates bestanden; Runtimewerte blieben unbeobachtet.

## Abgeschlossen: Runtime-POST-Reihenfolge absichern

PR #862 sichert, dass `_selected_post` die Provideridentität prüft, bevor es
Runtime-Container liest. Die Gegenprobe vertauscht die Schritte; 279
Regressionen und alle fünf Gates bestanden. Runtimewerte blieben unbeobachtet.

## Abgeschlossen: vollständige ausgewählte Beobachtungsfolge binden

PR #863 bindet alle drei POST-Prüfungen, den einzigen Erfolgsausgang und den
Ausschluss vorzeitiger Rückgaben. Gegenproben entfernen die Schlussprüfung und
fügen eine frühe Rückgabe ein; 279 fokussierte Regressionen bestehen. Es wird
keine Runtimebeobachtung ausgeführt.

## Abgeschlossen: Profilbinder-Rückgaben absichern

PR #864 bindet die exakte Zahl der Fehler- und Erfolgsausgänge von
`bind_selected_profile`; eine synthetische frühe Rückgabe am Beginn des
Try-Blocks wird verworfen. 279 fokussierte Regressionen bestehen. Es wird keine
Profilbindung ausgeführt.

## Abgeschlossen: internen Profilbinder-Rückgabepfad absichern

PR #865 bindet den einzigen Rückgabepunkt von `_bind_selected` nach den Cache-,
Shape- und Projektionsprüfungen. Eine Gegenprobe fügt eine frühe Rückgabe ein;
279 fokussierte Regressionen bestehen. Es werden keine Anker gelesen.

## Abgeschlossen: Skalarbeobachter gegen frühe Rückgabe absichern

PR #866 bindet die vier vorgesehenen Rückgaben von
`observe_current_interpreter_scalars` und verwirft einen zusätzlichen Ausstieg
vor den Hook- und Projektionsprüfungen. 279 fokussierte Regressionen und alle
fünf Gates bestanden. Es wurde keine Beobachtung ausgeführt.

## Abgeschlossen: frische Recordaufnahme gegen frühe Rückgabe absichern

PR #867 bindet die fünf vorgesehenen Rückgaben von
`observe_current_interpreter_records` und verwirft einen zusätzlichen Ausstieg
vor Nachheraufnahme und Hashvergleich. 279 fokussierte Regressionen und alle
fünf Gates bestanden. Es wurde keine Aufnahme ausgeführt.

## Abgeschlossen: Capture-Schema gegen frühe Rückgabe absichern

PR #868 bindet den einzigen Rückgabepunkt von `_capture` nach Modul-/Pfad-
validierung und sortierter Modulprojektion. Eine Gegenprobe fügt eine frühe
Rückgabe ein; 279 fokussierte Regressionen und alle fünf Gates bestanden. Es
wurde kein Snapshot aufgenommen.

## Abgeschlossen: Profilvergleich gegen frühe Rückgabe absichern

Der statische Kandidat für `_compare` verwirft jetzt jeden Rückgabepunkt im
Vergleichskörper. Eine Mutation fügt vor der ersten Shape-Prüfung `return None`
ein und wird abgewiesen. Der fokussierte Satz besteht 279/279; es wird kein
Profilvergleich ausgeführt.

## Abgeschlossen: Profilvalidierungsbericht gegen frühe Rückgabe absichern

Der Quellvertrag bindet `validate_profile` nun an genau drei Ausgänge: zwei
Fehlerberichte und den abschließenden Erfolg. Eine Mutation mit vorgezogener
Rückgabe vor dem Vergleich wird abgewiesen. Der fokussierte Satz besteht
279/279; es werden keine Profile validiert.

## Abgeschlossen: Profilform-Validator gegen frühe Rückgabe absichern

Der statische `_shape`-Vertrag verwirft jetzt Rückgaben innerhalb des
Validierungskörpers. Eine Mutation mit Rückgabe vor der ersten Formprüfung
wird abgewiesen. Der fokussierte Satz besteht 279/279; es werden keine Profile
verarbeitet.

## Abgeschlossen: Record-Validatoren gegen frühe Rückgabe absichern

Die statischen Verträge für `_records` und `_files` verwerfen jetzt Rückgaben
innerhalb der Validierungskörper. Zwei getrennte Mutationen fügen je eine frühe
Rückgabe ein und werden abgewiesen. Der fokussierte Satz besteht 279/279; es
werden keine Records verarbeitet.

## Abgeschlossen: absoluten Pfadvalidator gegen frühe Rückgabe absichern

Der statische `_absolute`-Vertrag verwirft jetzt eine frühe Rückgabe vor den
Pfadprüfungen. Der fokussierte Satz besteht 279/279; es werden keine
Hostpfade geprüft.

## Abgeschlossen: primitive Textvalidatoren gegen frühe Rückgabe absichern

Die statischen Verträge für `_text` und `_strings` verwerfen jetzt jeweils
frühe Rückgaben. Drei Mutationen werden abgewiesen; 279 fokussierte Tests
bestehen. Es werden keine Profilwerte verarbeitet.

## Abgeschlossen: zentralen Ablehnungshelfer absichern

Der primitive Quellvertrag bindet `_need` jetzt an die Ablehnung falscher
Bedingungen durch `_Failure` und verwirft zusätzliche Rückgaben. Eine Mutation
mit vorgezogener Rückgabe wird abgewiesen; 279 fokussierte Tests bestehen.
Keine Profilwerte wurden verarbeitet.

## Abgeschlossen: Profilkandidatenkette und parallele Zweige verbinden

Der neue Kettentest bindet in `analyze()` die parallelen skalaren und frischen
Recordzweige sowie den Capture-/Modulrecord-/Vergleichs-/Berichtspfad mit
Shape-, Record-, Pfad- und Primitiveverträgen, Profilmodellen und
Record-Beobachtungsfluss. Er prüft die Vorgängerargumente und alle 18
Kandidatenausgaben im Resultat. Vier Gegenproben brechen zwei Übergabekanten
und entfernen zwei Ergebniseinträge; alle werden erkannt. Der gesamte
fokussierte Satz besteht 280/280. Es läuft keine Analyse und keine
Runtimebeobachtung.

## Abgeschlossen: Kandidatenstatus beim CLI-Ausgang erhalten

Eine zusätzliche Regression bindet den erfolgreichen CLI-Ausgang an
`CANDIDATES_ONLY`, den Eingabefehler an `NOT_PROVEN` und den Erfolgscode 0.
Eine Mutation, die den Erfolg als `PROFILE_VALIDATED` ausgibt, wird verworfen.
280 fokussierte Tests bestehen; der Analyzer wurde nicht gestartet.

## Begrenzte Fortsetzung: DGN-007-Quellclosure verkleinern

Als Nächstes wird der dokumentierte Rest von unbekannten CPython-Quellpfaden
und deren Bedingungen anhand der gepinnten Quellen reduziert. Das Ergebnis
bleibt `CANDIDATES_ONLY`; daraus folgt keine P11- oder Runtimeattestation.

Der erste Quellschritt bindet alle fünf produktiven `copyreg.pickle`-Aufrufe
und begrenzt `copyreg.py:19` auf `{False, True}`. PR #882 integrierte ihn als
Commit `339d5dc2f18991c706fedb3bbb057c5e9db5b0e7`; alle fünf PR-Gates
bestanden. Der nächste Fact bindet die elf produktiven `opcode.pseudo_op`-
Registrierungen sowie deren Funktionskörper und begrenzt `opcode.py:72` auf
`{False, True}`. PR #883 integrierte ihn als Commit
`94b2b2d1226ab4cb1c28dd70e6b3d287b4728868`; alle fünf PR-Gates bestanden.
Ein weiterer lokaler Fact bindet `JSONEncoder` an die vollständige
Produktionsquellmenge und wertet die drei Importzeit-Argumentguards für
`separators`, `indent` und `default` als falsch aus. Der Scan zählt nun 519
unbekannte und 66 aufgelöste Bedingungen, bei unverändert 60 Modulen, 318
Kanten und Kandidatenhash `33f55d7c…`. PR #884 integrierte den Fact mit allen
fünf bestandenen PR-Gates. Ein digest- und DiffID-geprüfter OCI-Export des
lokalen Zielimages aktiviert nun zusätzlich die bestehenden `_pickle`- und
Plattformfacts, ohne einen Interpreter zu starten. Der neue `hashlib`-Fact
bindet acht Algorithmusguards an die vollständige Quelltabelle; die beiden
dynamischen Cacheguards bleiben offen. Der aktuelle Scan umfasst 60 Module,
316 Kanten, 82 aufgelöste und 485 unbekannte Bedingungen; Unknown-Digest
`4431f8023aaf2af7b202882d29ac025fe5250ec09cd52e9faa16969d0ef6f3c7`.
284/284 fokussierte Tests bestehen. Nächster Arbeitsschritt: verbleibende
Bedingungen anhand der gepinnten Quelle auf sichere vollständige Facts prüfen;
dynamische Fälle bleiben ohne statisch belegte Ausführungsbedingungen
unbekannt. Kein Interpreterstart, keine P11-/Runtimeattestation.

Die Zielimage-Inventur bindet ergänzend `_blake2`, `_sha1`, `_sha2` und `_sha3`
an exakte Datei-Hashes, reguläre Dateitypen, Modus und Größenbegrenzung. Eine
Digest-Gegenprobe wird zurückgewiesen. Im gepinnten CPython-Quelltext fängt
`hashlib.py` `ImportError` ab; deshalb belegen Image-Dateien für sich genommen
keinen erfolgreichen Konstruktorimport. Die Cacheguards bleiben offen. Der
Scan steht weiterhin bei 60 Modulen, 316 Kanten, 82 aufgelösten und 485
unbekannten Bedingungen; 284 fokussierte Tests bestehen.

Als nächster Fact wurde `functools.py:509` (`maxsize < 0`) an den
quellgebundenen `lru_cache`-Funktionskörper und den vollständigen Satz von 20
Standardbibliotheksaufrufen gebunden. Die nachweisbaren ganzzahligen Größen
sind nicht negativ; `None` und bare Funktionsdekorationen erreichen den
negativen Größenvergleich nicht. Eine negative Größenmutation verletzt den
Callsite-Digest. Der Scan steht nun bei 60 Modulen, 316 Kanten, 83 aufgelösten
und 484 unbekannten Bedingungen; Unknown-Digest
`69540e632b066aaa37ac80498a564d814358e480bdcc47213068a121f8136904`.
285 fokussierte Tests bestehen; keine Runtime- oder P11-Attestation.

Eine Erweiterung desselben Facts bindet nun zusätzlich alle sechs
`lru_cache`-Guards in `functools.py` (Zeilen 507, 509, 511, 517, 543 und 552)
an die vollständigen 20 Call-Sites, 40 relevanten quellgehashten Dateien und
beide Funktionskörper. Die Outcomes sind pro Guard vollständig abgedeckt;
`maxsize < 0`, `maxsize == 0` und `maxsize is not None` fallen falsch aus.
Der Scan zählt nun 88 aufgelöste und 479 unbekannte Bedingungen bei 60 Modulen
und 316 Kanten. Unknown-Digest:
`604bb985511cb3037bdd61ed94114f96a1a04304854aa5878a1b8af5f19fee5d`.
285 fokussierte Tests bestehen; `CANDIDATES_ONLY`, ohne Runtime- oder
P11-Attestation.

Beim anschließenden Lauf zeigte sich ein Integrationsfehler im bereits
vorhandenen `sysconfig.is_python_build`-Fact: Ein exakter Vergleich der
gesamten Image-Faktenmap scheiterte, sobald zusätzliche verifizierte Felder
hinzukamen. Der Guard vergleicht nun die vier benötigten Felder einzeln und
akzeptiert additive Facts; Mutationen an den erforderlichen Feldern bleiben
abgewiesen. Der Scan löst `sysconfig.py:235` als falsch auf: 89 aufgelöste,
478 unbekannte Bedingungen, Unknown-Digest
`2679f8d8756361e27b356bb8c73056df0136b5876716b5bc43f975f26fe6d9d3`.
285 fokussierte Tests bestehen; kein Runtime-/P11-Nachweis.

Ein ergänzender `sysconfig.py:112`-Fact setzt ausdrücklich die
`--target-no-pythonuserbase-override`-Routenannahme voraus und prüft zugleich,
dass die gepinnte Image-Config `PYTHONUSERBASE` nicht setzt. Zusätzlich gelten
`-S` und das Fehlen weiterer Standardbibliotheksquellen mit einem literalen
Verweis auf die Variable. Ohne diese Voraussetzungen bleibt die Bedingung
unbekannt. Mit der Annahme
zählt der Offline-Scan 90 aufgelöste und 477 unbekannte Bedingungen bei 60
Modulen und 316 Kanten; Unknown-Digest
`be3628b5dc4aafc50a093de1cf73651cd2f341dce374a94b7678b596200ef172`.
286 fokussierte Tests bestehen. Keine Laufzeit- oder P11-Attestation.

Der folgende `sysconfig.py:310`-Fact schließt den Venv-Vergleich ausschließlich
mit dem quellgebundenen S15-Präfixkandidaten: `prefix` und `base_prefix`
stimmen überein, und der Candidate beansprucht keine Laufzeitpräfixe. Der
Fact verwirft abweichende Präfixe oder eine Laufzeitbehauptung. Aktueller Scan:
91 aufgelöste und 476 unbekannte Bedingungen, 60 Module, 316 Kanten;
Unknown-Digest `e8bb2ad85abe5748480716051afe9eda61f0676a9d7f35d6bab952f6418e8579`.
287 fokussierte Tests bestehen. Runtime-/P11-Attestation bleibt aus.

`sysconfig.py:313` ist zusätzlich gegen die literal geparsten Scheme-Tabellen
gebunden. Der Fact nimmt die bedingten User-Schemes nur bei belegtem
`_HAS_USER_BASE=True` auf und löst die Membership-Prüfung auf falsch auf.
Aktueller Scan: 92 aufgelöste und 475 unbekannte Bedingungen bei 60 Modulen,
316 Kanten; Unknown-Digest
`94bfdb97e293122ad9f7978a8c09d86d9cc3c84df05ffaa9634336214e65cca1`.
288 fokussierte Tests bestehen; weiterhin keine Runtime-/P11-Attestation.

Ein quellgebundener Importfact deckt die drei Guards in `Thread.__init__`
für die einzige importzeitige `_MainThread()`-Konstruktion ab: Name ist
gesetzt, `daemon` ist nicht `None`, und der konkrete Wert `False` short-circuited
den Daemon-Check. Der Scan zählt 93 aufgelöste und 472 unbekannte Bedingungen
bei 60 Modulen und 316 Kanten; Unknown-Digest
`255dba30d8c9248fe7391aac6024a79f0f5e1bb74adaea3daa2e677911733117`.
289 fokussierte Tests bestehen; kein Runtime-/P11-Nachweis.

Der nächste quellgebundene Fact nutzt die zwingende `str(...)`-Normalisierung
im gepinnten `collections.namedtuple`-Körper, um `collections/__init__.py:397`
als falsch zu belegen. Eine Mutation der Feldnormalisierung wird abgewiesen.
Der vollständige Archiv-/OCI-Scan zählt 60 Module, 316 Kanten, 94
aufgelöste und 471 unbekannte Bedingungen; Unknown-Digest
`bca4b7390cb584e14732193fe148ea1cb35288e77b1fd5da2dc93e5434af1472`.
290 fokussierte Tests bestehen. Die weiteren `namedtuple`-Guards hängen von
variablen Argumenten und bleiben offen; `CANDIDATES_ONLY`, kein
Runtime-/P11-Nachweis.

Der anschließende Fact bindet den letzten `collections.namedtuple`-Modulguard
an die im CPython-Ziel exportierte `_getframemodulename`-Methode und den
`'__main__'`-Fallback. Änderungen am Builtinpfad oder Überschreibungen in
Standardbibliotheksquellen verwerfen den Fact. Der Guard an Zeile 523 ist
wahr; die Zielclosure zählt 95 aufgelöste und 470 unbekannte Bedingungen,
60 Module und 316 Kanten. Unknown-Digest:
`6eefb65fb9ebaba0806610fb6beefeaa2ae055f78af74c078726aabf7ea008fe`.
291 fokussierte Tests bestehen. `CANDIDATES_ONLY`; keine Runtime-/P11-
Attestation.

### Begrenzte Fortsetzung: `collections.namedtuple`-Feldnamen (15. November 2026)

Der nächste Offline-Schnitt bindet den Guard `collections/__init__.py:381`
über den vollständigen Produktionsaufrufbestand im vorhandenen
CPython-3.12.16-Archiv. Der Digest umfasst 55 Aufrufe und 50 quellgehashte
Module; alle Argumente sind statisch als String oder Sequenz klassifiziert.
Die zwei dynamisch gebildeten Sequenzwerte werden nur unter den geprüften
`inspect.py`- und `typing.py`-Strukturen akzeptiert. Eine Regression für eine
zusätzliche unbekannte Argumentform bleibt fail-closed. Der verfügbare
Zielquellscan ergibt 60 Module, 318 Aufrufkanten, 86 entschiedene und 497
unbekannte Bedingungen, Unknown-Digest
`44ceb05a5a18fbc9268439d1ca02fd43add3349ae9134d4c47074af42326a975`;
`CANDIDATES_ONLY`, 292 fokussierte Tests. Das lokale Docker-Save-Archiv fehlt,
deshalb ist die direkte `python3.12`-Image-Routenannahme nicht Bestandteil
dieses Nachweises. Diese Fortsetzung ist auf den Quellenfact und einen
Integrations-PR begrenzt; keine Runtime-/P11- oder SQL-Ausführung und keine
menschliche Generalprobe.

### Begrenzte Fortsetzung: `collections.namedtuple`-Defaults (15. November 2026)

Ein weiteres Offlinepaket prüft innerhalb eines PRs die beiden
`defaults is not None`-Guards am gebundenen vollständigen Aufrufbestand. Die
Default-Signatur `None`, ausgelassene Argumente sowie zwei explizite Listen
belegen beide Outcomes. Der dynamische Wert aus `typing.py` bleibt unbewertet.
Das vorhandene CPython-3.12.16-Archiv und die bereits registrierten
Quellkandidaten genügen; es werden keine neuen Produktquellen benötigt. Die
Regression verwirft eine nicht abgedeckte Defaults-Expression. Der Scan zählt
60 Module, 318 Kanten, 88 entschiedene und 495 unbekannte Bedingungen,
Unknown-Digest
`b7e22c5b83fee44f8b73beff4a9442004ebe491fc114a2dc197a924ac66ad105`;
292 fokussierte Tests. `CANDIDATES_ONLY`; keine direkte Image-Route, Runtime,
P11, SQL-Ausführung oder menschliche Generalprobe.

### Begrenzte Fortsetzung: `collections.namedtuple`-Modulguard (15. November 2026)

Ein weiteres Offlinepaket bindet `collections/__init__.py:515` (`module is
None`) an denselben vollständigen Aufrufbestand. Aufrufe ohne explizites
`module`-Argument und `_pydecimal.py` mit einem Stringliteral belegen beide
Outcomes; der dynamische `typing.py`-Wert bleibt unbekannt. Unbekannte
Argumentformen verwerfen den Fact. Der Zielquellscan zählt 60 Module, 318
Kanten, 89 entschiedene und 494 unbekannte Bedingungen; Unknown-Digest
`f97338e9f4e8fc5f4d0f76356f4992ab212d7e74c698aa430177c61b4d8f1279`.
293 fokussierte Tests. `CANDIDATES_ONLY`; keine direkte Image-Route,
Runtime-/P11- oder SQL-Ausführung und keine menschliche Generalprobe.

### Begrenzte Fortsetzung: `threading.Thread`-Daemon-Guard (15. November 2026)

Der importzeitliche `_MainThread`-Pfad belegt `threading.py:1053`
(`if not self.daemon`) als wahr: `Thread.__init__` erhält explizit
`daemon=False`, setzt `_daemonic`, und der `daemon`-Getter liest diesen Wert,
bevor `_MainThread.__init__` `_set_tstate_lock()` aufruft. Die vollständige
gehashte Standardbibliotheksquelle wird nach direkten modulweiten
`Thread()`-Aufrufen durchsucht; ein passender Aufruf über `threading.Thread`,
`from threading import Thread` oder Sternimport lässt den Fact scheitern.
Die Aussage gilt nur für diese Importinitialisierung, nicht für spätere
Thread-Konstruktionen. Der Zielscan zählt 60 Module, 318 Kanten, 95
entschiedene und 486 unbekannte Bedingungen; Unknown-Digest
`7f00cc302dba6f1fe3536a99bccb26360bbf42ff25ef1debf0984bfb5a25a24b`.
294 fokussierte Regressionen bestehen. `CANDIDATES_ONLY`; keine direkte
Image-Route, Runtime-/P11- oder SQL-Ausführung und keine menschliche
Generalprobe.

### Begrenzte Fortsetzung: `logging`-Levelguard (15. November 2026)

Ein quellgebundener Fact löst `logging/__init__.py:209`
(`isinstance(level, int)`) für die importzeitliche Standardinitialisierung
auf. Er bindet die Konstruktorpfade von `Handler`, `RootLogger` und `Manager`,
die Level-Konstanten und sämtliche modulweiten Standardbibliotheksaufrufe
von `logging.getLogger`; dynamische Laufzeitkonfiguration bleibt unbekannt.
Der Digest des vollständigen Aufrufinventars ist
`537ede4580d6934dc4ef812f20ee175f3123abc3f4cc774db15f5f1b0ba15213`.
Der Zielquellscan zählt 60 Module, 318 Kanten, 90 entschiedene und 493
unbekannte Bedingungen, Unknown-Digest
`76512c36e8e69992470da060eaf2daaa92ad264fde75366d9a492c55a71e0146`.
293 fokussierte Tests bestehen. `CANDIDATES_ONLY`; keine direkte Image-Route,
Runtime-/P11- oder SQL-Ausführung und keine menschliche Generalprobe.

### Begrenzte Fortsetzung: `threading.Condition`-Lockargument (15. November 2026)

Der importzeitliche Hauptthreadpfad belegt die vier Guards `threading.py:278`,
`:287`, `:289` und `:291` als falsch: `_MainThread` delegiert an
`Thread.__init__`, das ein `Event` erzeugt; dieses übergibt `Lock()` an
`Condition`. Die `Lock`-Aliasbindung führt zu `_thread.allocate_lock`; die
gehashte C-Quelle liefert ein natives Lock-Objekt oder meldet einen Fehler.
Der Typ besitzt kein Instanzwörterbuch und stellt die drei von Condition
geprüften privaten Methoden nicht bereit. Die Aussage gilt nur für diese
Importinitialisierung. Der Zielquellscan zählt 60 Module, 318 Kanten, 94
entschiedene und 487 unbekannte Bedingungen, Unknown-Digest
`e5431241726d7054aadb72aa9c042f91a677322dcbf7575ae0e2ea19b8d3cb9a`.
294 fokussierte Tests bestehen. `CANDIDATES_ONLY`; keine direkte Image-Route,
Runtime-/P11- oder SQL-Ausführung und keine menschliche Generalprobe.

### Begrenzte Fortsetzung: `threading.excepthook`-Importguard (15. November 2026)

Der importzeitliche Aufruf von `_make_invoke_excepthook()` während
`Thread.__init__` bindet den Guard `threading.py:1363`
(`old_excepthook is None`) an falsch. Der Quellpfad akzeptiert den
hashgeprüften nativen `_thread._excepthook`-Export oder die definierte
Python-Fallbackfunktion im `ImportError`-Zweig. Mutationen der Modulbindung
und ein fehlender nativer Export verwerfen den Fact. Der benachbarte Guard
`sys.excepthook is None` an Zeile 1365 bleibt offen, weil seine
Interpreterinitialisierung eine eigene Quellenbindung erfordert. Der Zielscan
zählt 60 Module, 318 Kanten, 96 entschiedene und 485 unbekannte Bedingungen;
Unknown-Digest `f19e6a388944dbedb4ff0973011d5b60c384a8e568c103b64017ad151d0ed69a`.
294 fokussierte Regressionen bestehen. `CANDIDATES_ONLY`; keine direkte
Image-Route, Runtime-/P11- oder SQL-Ausführung und keine menschliche
Generalprobe.

### Begrenzte Fortsetzung: `collections.namedtuple`-Identifierguard (15. November 2026)

Der Fact löst `collections/__init__.py:399` (`not name.isidentifier()`) für
importzeitliche Standardbibliotheksaufrufe als falsch auf. Die vollständige
gehashte Aufrufinventur enthält 42 modulweit ausgeführte Aufrufe mit statischen
ASCII-Identifiern; `_FrameInfo` wird über die gebundene `_Traceback`-
Felddefinition ausgewertet. Dynamische Funktionsaufrufe bleiben unbekannt;
eine Mutation mit ungültigem Typnamen oder unbekannten Modulargumenten
verwirft den Fact. Der Zielscan zählt 60 Module, 318 Kanten, 97 entschiedene
und 484 unbekannte Bedingungen; Unknown-Digest
`415f5546523f6a8ddaa1223db9549dc7bb7f55936c2ffc7ee313bc94fd750c77`.
294 fokussierte Regressionen bestehen. `CANDIDATES_ONLY`; keine direkte
Image-Route, Runtime-/P11- oder SQL-Ausführung und keine menschliche
Generalprobe.

### Begrenzte Fortsetzung: `collections.namedtuple`-Keywordguard (15. November 2026)

Der Fact löst `collections/__init__.py:402` (`_iskeyword(name)`) für die
importzeitlichen Aufrufe als falsch auf. `collections` bindet den geprüften
`keyword.iskeyword`-Import; `keyword.py` bindet seine gehashte Literal-
`kwlist` an `frozenset(kwlist).__contains__`. Keiner der 42 modulweit
ausgeführten Typ- oder Feld-Identifier ist ein Keyword. Ein veränderter
Keywordbestand oder Keyword-Aufruf lässt den Fact scheitern. Der Zielscan
zählt 60 Module, 318 Kanten, 98 entschiedene und 483 unbekannte Bedingungen;
Unknown-Digest `5a134d577ec00b2518f47f6df325fac976395d8b604ec30da1c0594d456b9ba9`.
294 fokussierte Regressionen bestehen. `CANDIDATES_ONLY`; keine direkte
Image-Route, Runtime-/P11- oder SQL-Ausführung und keine menschliche
Generalprobe.

### Begrenzte Fortsetzung: `collections.namedtuple`-Feldformguards (15. November 2026)

Die Facts binden `collections/__init__.py:408` (`name.startswith('_') and not rename`)
und `:411` (`name in seen`) für den importzeitlichen Aufrufbestand an falsch.
Alle 42 statischen Feldlisten haben keine führenden Unterstriche und keine
Duplikate; ein `_field`- oder `x x`-Aufruf verwirft die gesamte Bindung. Der
vollständige Aufruf- und Quellhash bleibt Voraussetzung. Der Zielscan zählt 60
Module, 318 Kanten, 100 entschiedene und 481 unbekannte Bedingungen;
Unknown-Digest `d8d485d993f0426d8f5e5e38e15bed6e08e195548de5de3b6b71ed0568345750`.
294 fokussierte Regressionen bestehen. `CANDIDATES_ONLY`; keine direkte
Image-Route, Runtime-/P11- oder SQL-Ausführung und keine menschliche
Generalprobe.

### Begrenzte Fortsetzung: `collections.namedtuple`-Defaultanzahl und Einzelfeldformat (15. November 2026)

Die Facts binden `collections/__init__.py:418` (`len(defaults) > len(field_names)`) und `:427` (`num_fields == 1`) an denselben vollständigen statischen Aufruf- und Quellhash. Unter 42 Modulstartaufrufen übersteigt keine nicht-`None`-Defaultliste die Feldanzahl; keine Feldliste hat genau ein Element. Die Auswertung bindet `tuple(defaults)`, die längenerhaltende Feldtransformation und `num_fields = len(field_names)`. Eine Mutation mit mehr Defaults als Feldern sowie geänderte Konvertierungs-/Zählquellen verwerfen die Fact-Bindung; synthetische Einzelfeldaufrufe erhalten beide Guardzweige.

294 fokussierte Regressionen bestehen. Der Zielscan zählt 60 Module, 318 Kanten, 102 entschiedene und 479 unbekannte Bedingungen; Unknown-Digest `d6e8825262bc833a2a9e1c439e787dc1f1ee1ca8b3b031b3f9a2bd594cc01c66`. `CANDIDATES_ONLY`; keine direkte Image-Route, Runtime-/P11- oder SQL-Ausführung und keine menschliche Generalprobe.

### Begrenzte Fortsetzung: Worker-Verbose-Fact im Offline-Kandidatenscan (15. November 2026)

Die Analyse wendet den bereits quellengebundenen `_verbose_message`-Fact jetzt auch ohne Image-Save-Eingang an. Sie prüft die Workerdatei anhand ihres Pins, die festgelegte `-I -S -B -c`-Route und die gepinnten CPython-Startquellen; damit ist `importlib/_bootstrap.py:493` falsch und `:494` wegen des unerreichbaren Elternzweigs nicht mehr unbekannt. Das ändert keine Runtime- oder Imagebehauptung.

294 fokussierte Regressionen, ADV-003 und der Datenschutzscan der geänderten Dateien bestehen. Der vollständige Scan bleibt `CANDIDATES_ONLY` bei 60 Modulen und 318 Kanten, mit 103 entschiedenen und 477 unbekannten Bedingungen; Unknown-Digest `c1b618975dda22e7355f41b30d12b2d921f6fa3a452f6cecac4281c7a4a30a72`. Keine Image-Erfassung, Interpreter-, Runtime-/P11- oder SQL-Ausführung und keine menschliche Generalprobe.

### Begrenzte Fortsetzung: Warning-Optionen-Iterator im Offline-Kandidatenscan (15. November 2026)

Der vorhandene Worker-Fact beweist aus der gepinnten `-I -S -B -c`-Route und den CPython-Startquellen, dass `warnings._processoptions(args)` keine Einträge erhält: `-I` verhindert Umgebungsoptionen, und die feste Route enthält kein `-W`. Die Analyse wendet den Fact nun im `CANDIDATES_ONLY`-Scan unabhängig von Image-Save-Eingaben an. Ein Strukturtest sichert, dass die Anwendung vor der Image-Save-Bedingung bleibt; insgesamt bestehen 295 fokussierte Regressionen. Der vollständige Scan zählt 60 Module, 316 Kanten, 103 entschiedene und 460 unbekannte Bedingungen; Unknown-Digest `b961030b249654b8ceb91b95de9939476705142011047b4f57ed05feedf807fa`. Der lokale Repository-Privacylauf meldet 6148 Funde im gesamten Arbeitsbaum; die vier geänderten Dateien bestehen den gezielten Privacy-Scan. Keine Image-Erfassung, Interpreter-, Runtime-/P11- oder SQL-Ausführung und keine menschliche Generalprobe.

### Begrenzte Fortsetzung: isolierte Worker-Startfakten im Offline-Kandidatenscan (15. November 2026)

Die gepinnten Startquellen und die feste `-I -S -B -c`-Workerroute reichen auch ohne Image-Save-Eingabe zur Berechnung der bestehenden Fakten für `sys.flags.optimize == 0`, die Entfernung von `_PYTHON_SYSCONFIGDATA_NAME` aus der Kindumgebung und die abgefragten Worker-Flags. Im aktuellen Profil sind die beiden ersten Fakten belegt; die sechs Flags werden wegen nicht passender Quellenbindung als leer verworfen. Das Unknown-Inventar ändert sich in diesem Schnitt nicht: 60 Module, 316 Kanten, 103 entschiedene und 460 unbekannte Bedingungen, Digest `b961030b249654b8ceb91b95de9939476705142011047b4f57ed05feedf807fa`. 296 fokussierte Regressionen bestehen. Keine Image-Erfassung, Interpreter-, Runtime-/P11- oder SQL-Ausführung und keine menschliche Generalprobe.

### Begrenzte Fortsetzung: `sys.flags`-Fact an der CPython-Setterfunktion korrigiert (15. November 2026)

Die bisherige Quellenprüfung suchte `sys.dont_write_bytecode` fälschlich in `set_flags_from_config`; CPython 3.12.16 setzt das Attribut in `_PySys_UpdateConfig` nach dem Aufruf des Flags-Setters. Die Prüfung bindet jetzt den eindeutigen Funktionskörper, Setterreihenfolge und Flagfelder getrennt. Der echte gepinnte Quellbestand liefert nun alle sieben Fakten (`isolated`, `no_site`, `dont_write_bytecode`, `ignore_environment`, `safe_path`, `optimize` und `sys.dont_write_bytecode`). Regressionen verwerfen einen fehlenden Setter und doppelte Update-Funktionen. Das Candidate-Unknown-Inventar bleibt in diesem Profil unverändert: 60 Module, 316 Kanten, 103 entschiedene und 460 unbekannte Bedingungen, Digest `b961030b249654b8ceb91b95de9939476705142011047b4f57ed05feedf807fa`. 296 fokussierte Tests bestehen; keine Image-Erfassung, Interpreter-, Runtime-/P11- oder SQL-Ausführung.

### Begrenzte Fortsetzung: `sys.flags.no_user_site` aus `-I` ableiten (15. November 2026)

Der gepinnte CPython-Startcode setzt im `config->isolated`-Zweig `user_site_directory=0`; `set_flags_from_config` bildet den negierten Wert auf das geordnete Feld `no_user_site` ab. Zusammen mit der exakt gebundenen `-I -S -B -c`-Route ergibt sich `sys.flags.no_user_site == 1`. Beide C-Quellstellen sind Teil der Fact-Prüfung; der S15-Kandidat bindet die zusätzliche Fact mit. Der Offline-Scan weist jetzt acht Worker-Fakten aus, ohne das Unknown-Inventar weiter zu reduzieren: 60 Module, 316 Kanten, 103 entschiedene und 460 unbekannte Bedingungen, Digest `b961030b249654b8ceb91b95de9939476705142011047b4f57ed05feedf807fa`. 296 fokussierte Regressionen bestehen. Keine Image-Erfassung, Interpreter-, Runtime-/P11- oder SQL-Ausführung.

### Begrenzte Fortsetzung: Standardwerte für sechs `sys.flags`-Felder binden (15. November 2026)

Für die fest gepinnte Workerroute sind `debug`, `inspect`, `interactive`, `verbose`, `bytes_warning` und `quiet` jeweils 0. Die Fact-Prüfung bindet die CPython-Defaultzuweisungen, die passenden `-d`/`-i`/`-v`/`-b`/`-q`-Parserwirkungen, die `set_flags_from_config`-Abbildung und den exakten argv ohne diese Optionen. Die isolierte Route deaktiviert Umgebungsüberschreibungen. Mutationen an `parser_debug` oder ein zusätzliches `-v` verwerfen die gesamte Factbindung. Der Offline-Scan weist nun 14 Worker-Fakten aus; das Modulstartinventar bleibt bei 60 Modulen, 316 Kanten, 103 entschiedenen und 460 unbekannten Bedingungen, Digest `b961030b249654b8ceb91b95de9939476705142011047b4f57ed05feedf807fa`. 296 fokussierte Regressionen bestehen. Keine Image-Erfassung, Interpreter-, Runtime-/P11- oder SQL-Ausführung.

### Begrenzte Fortsetzung: `sys.flags.hash_randomization` binden (15. November 2026)

Der CPython-Startcode normalisiert den ungesetzten Seed auf `use_hash_seed=0` und `hash_seed=0`; der gepinnte `sys.flags`-Setter bildet `use_hash_seed == 0 or hash_seed != 0` auf `hash_randomization` ab. Zusammen mit `-I` ist damit der Flagwert 1 quellgebunden, ohne einen konkreten Zufallsseed oder Runtimezustand zu behaupten. Eine Seedmutation verwirft die Fact. Der Offline-Scan weist 15 Worker-Fakten aus; die unbekannte Modulstartmenge bleibt 460 (60 Module, 316 Kanten, 103 entschieden), Digest `b961030b249654b8ceb91b95de9939476705142011047b4f57ed05feedf807fa`. 296 fokussierte Regressionen bestehen. Keine Image-Erfassung, Interpreter-, Runtime-/P11- oder SQL-Ausführung.

### Begrenzte Fortsetzung: `sys.flags.dev_mode` an Preconfig binden (15. November 2026)

Der Worker verwendet exakt `-I -S -B -c`. Der gepinnte Preconfig-Code setzt dadurch `use_environment=0`; ohne `-X dev` und ohne wirksame `PYTHONDEVMODE` normalisiert `_PyPreCmdline_Read` `dev_mode` auf 0. `_PyPreCmdline_SetConfig` überträgt das Feld, und der gepinnte Sysmodule-Code bildet es als Bool in `sys.flags.dev_mode` ab. Ein abweichender Null-Setter verwirft die Worker-Fakten. Der Offline-Scan weist 16 Worker-Fakten aus; die Modulstart-Unknowns bleiben bei 460 (60 Module, 316 Kanten, 103 entschieden), Digest `b961030b249654b8ceb91b95de9939476705142011047b4f57ed05feedf807fa`. 296 fokussierte Regressionen bestehen. Keine Image-Erfassung, Interpreter-, Runtime-/P11- oder SQL-Ausführung.
### Begrenzte Fortsetzung: `sys.flags.warn_default_encoding` binden (15. November 2026)

Der gepinnte `_PyPreCmdline`-Header weist `warn_default_encoding` nicht im Initializer aus; dessen dokumentierte Nullinitialisierung ergibt 0. `_PyPreCmdline_Read` setzt den Wert nur bei `-X warn_default_encoding` oder `PYTHONWARNDEFAULTENCODING`. Der Worker startet fest mit `-I -S -B -c`, sodass beide Aktivierungswege ausgeschlossen sind. Header-Initialisierung, Preconfig-Handler, `COPY_ATTR`-Transfer und Sysmodule-Setter werden geprüft; Regressionen verwerfen einen expliziten Eins-Default und einen fehlenden Transfer. Der Scan liefert 17 Worker-Fakten bei unverändertem Unknown-Inventar (60 Module, 316 Kanten, 103 entschieden, 460 unbekannt; Digest `b961030b249654b8ceb91b95de9939476705142011047b4f57ed05feedf807fa`). Keine Image-, Interpreter-, Runtime-/P11- oder SQL-Ausführung.
### Begrenzte Fortsetzung: `sys.flags.int_max_str_digits` binden (15. November 2026)

Der CPython-3.12.16-Header pinnt `_PY_LONG_DEFAULT_MAX_STR_DIGITS` auf 4300. Die Startkonfiguration liest zwar `PYTHONINTMAXSTRDIGITS` und `-X int_max_str_digits`, fällt bei negativem Wert aber auf diese Konstante zurück; die isolierte Workerroute startet ohne diese `-X`-Option und deaktiviert Umgebungswerte. Der Worker-Fact verlangt außerdem den negativen-Feld-Aufrufpfad sowie die `sys.flags`-Abbildung. Gegenproben mit geänderter Headerkonstante und verändertem Fallback verwerfen nur diesen Fact. Der Scan liefert 18 Worker-Fakten, aber keine zusätzliche Unknown-Auflösung: 60 Module, 316 Kanten, 460 unbekannte Bedingungen, Digest `b961030b249654b8ceb91b95de9939476705142011047b4f57ed05feedf807fa`. Keine Runtime- oder Imagebehauptung.


### DGN-007 – nächste statische Fortsetzung: `os._add`-Funktionsverfügbarkeit (17. November 2026)

Der CPython-3.12.16-Linux-Quell-/Buildfact für `os._add` ist quellengebunden ergänzt; seine eine Bedingung ist aufgelöst, während 449 weitere unbekannt bleiben. Die statische Testsuite besteht mit 298 Tests. Der vollständige Zielscan bleibt `CANDIDATES_ONLY` (60 Module, 316 Kanten, 163 Funktionen; 114 aufgelöst; Unknown-Digest `7efbc98f828aa129992f682c178527b5e87cd4990841c6e9520cb5aa78d9b24d`). Nächste Kandidaten sind einzeln gegen dieselben gepinnten Quellen zu prüfen. Offene operative Gates – insbesondere echte Kanal-/Loader-/Parentanbindung, vollständige Inventur und Fünf-Formen-/64-KiB-Qualifikation – werden dadurch nicht erfüllt. SESSION_END-Design und deklarativer Matcher (§34, PR259) sind bereits integriert; ihre frühere Nennung als nächster Designschritt ist überholt.


### DGN-007 – Logging-Stilvalidierung statisch abbilden (17. November 2026)

Die zwei öffentlichen Logging-Stilguards sind nun gegen den gepinnten CPython-Quelltext gebunden. Gültige Stile und frei übergebene ungültige Werte bleiben beide im konservativen Kontrollfluss erhalten. Die Testsuite besteht mit 299 Tests. Zielscan: 60 Module, 316 Kanten, 163 Funktionen, 116 aufgelöst und 447 unbekannt; Digest `742614875c7d689dd14338bfc603928908a298a5c1253c10d36fecd705ea7f95`. Nächste statische Kandidaten sind weiterhin einzeln am Quellenstand zu prüfen. Das ersetzt keine Runtime-/P11-Qualifikation, tatsächliche Kanal-/Loader-/Parentanbindung, vollständige Inventur oder das Fünf-Formen-/64-KiB-Gate.


### RES-004 – Grant-/Wait-Filter an den tatsächlichen `OwnWaits`-CTE binden (17. November 2026)

Eine reproduzierte Negativprobe entfernte `mg.grant_time IS NULL` und den `RESOURCE_SEMAPHORE`-Filter aus dem `OwnWaits`-CTE und setzte denselben Text stattdessen in die spätere `LEFT JOIN`-Bedingung. Der bisherige globale Fragmentvergleich akzeptierte diese Abfrage, obwohl sie eigene Requests auch ohne Grant-Wait als zugeordnet markieren konnte.

Der Validator extrahiert nun den genau einmal vorkommenden, balancierten `OwnWaits AS (...)`-CTE unter Beachtung von Kommentaren, Strings und geklammerten Bezeichnern und verlangt beide Filter samt passendem Wait-Literal in dessen `WHERE`-Bedingung. Die neue Regression bestätigt die Ablehnung der verschobenen Filter. Die RES-004-Testsuite besteht mit 14 Tests; der Abfragevertragvalidator besteht. Das ist weiterhin ein statischer Strukturcheck ohne T-SQL-Parser, DMV-Authentifizierung oder Runtime-/Grant-Wait-Nachweis.


### IDX-007 – Waitfilter im `PageWaits`-CTE verankern (17. November 2026)

Eine Negativprobe setzte `WHERE 1 = 1` ein und beließ `r.wait_type = N'PAGELATCH_EX'` nur in einem wirkungslosen `CASE`-Ausdruck. Der Lehrabfragevalidator akzeptierte den Querytext, obwohl damit auch andere Request-Waittypen in die Seitenauswertung gelangen konnten.

Ein gemeinsamer T-SQL-Helfer extrahiert jetzt genau einen benannten, balancierten CTE und ignoriert String-/Bezeichnertexte bei der Erkennung. IDX-007 verlangt den tatsächlichen Waittypfilter und die Ressourcen-/Datenbankgrenzen innerhalb des `PageWaits`-CTE und weist eine OR-Aufweichung zurück. RES-004 verwendet denselben CTE-Scanner für seine eigenen Grant-/Waitfilter. Die IDX-007-Suite besteht mit 15 Tests, die RES-004-Abfragevertragssuite ebenfalls mit 15 Tests, der RES-004-Offlinedatenvertrag mit 24 Tests; beide Quellenvalidatoren bestehen. Der Prüfer bleibt ein statischer Strukturvergleich ohne T-SQL-Parser, DMV-Herkunft oder Engine-Nachweis.


### RES-001 – Scheduler-Scope an das tatsächliche `WHERE` binden (17. November 2026)

Eine Negativprobe entfernte `scheduler_id < 255` und `is_online = 1` aus dem Abfragefilter, beließ beide Ausdrücke aber in einem wirkungslosen `CASE`. Der bisherige globale Fragmentvergleich akzeptierte dadurch eine Query, die auch verborgene oder offline Scheduler zurückgeben konnte.

Der statische Lehrvalidator verlangt nun die zusammenhängende Scheduler-Scope-Bedingung im aktiven `WHERE` vor der Sortierung. Eine Regression schützt den reproduzierten Gegenfall. Neun Lehrvalidator-Tests, der Validator und 16 Tests der getrennten Worker-Queue-Evidenzsuite bestehen. Es entsteht kein Scheduler-Runtime- oder Worker-Erschöpfungsnachweis.

### RES-004 – zusätzliche Filter dürfen Wait-Kandidaten nicht unterdrücken (17. November 2026)

Eine Negativprobe ergänzte `AND 1 = 0` nach den geforderten Grant- und Waitfiltern im `OwnWaits`-CTE. Der Validator akzeptierte damit eine Abfrage, die garantiert keine eigenen Wait-Zeilen liefern konnte. Der statische Vertrag verlangt jetzt, dass die aktive `WHERE`-Bedingung exakt die zwei vereinbarten Filter enthält; zusätzliche Prädikate werden abgewiesen. Die Regression sichert den unterdrückenden Zusatzfilter. 26 Lehrabfragetests, der Abfragevalidator und 24 Offlinevertragstests bestehen. Es bleibt eine lexikalische Quellstrukturprüfung ohne T-SQL-Parser, authentische DMV-Aufnahme oder Engine-Nachweis.

### IDX-007 – zusätzliche Filter dürfen Seiten-Waits nicht unterdrücken (17. November 2026)

Eine Negativprobe setzte `AND 1 = 0` nach den vorgesehenen Filtern des `PageWaits`-CTE. Der bisherige Validator akzeptierte damit eine garantiert leere Request-Seitenabfrage. Der Vertrag bindet jetzt die vollständige `WHERE`-Bedingung an Waittyp, Request-Seitenressource und dieselbe Zieldatenbank; zusätzliche Prädikate werden abgewiesen. Eine Regression deckt den unterdrückenden Filter ab. 23 Lehrabfragetests, 13 Offlinevertragstests, Validatoren, Curriculumprüfung und Diff-Whitespaceprüfung bestehen. Es folgt daraus keine authentische DMV-Aufnahme oder Laufzeitqualifikation.

### RES-001 – zusätzliche Filter dürfen Scheduler nicht ausblenden (17. November 2026)

Eine Negativprobe ergänzte `AND 1 = 0` hinter den Scheduler-Scope-Filtern. Der Lehrvalidator akzeptierte damit eine garantiert leere Scheduleraufnahme. Der Vertrag bindet jetzt den vollständigen Filterabschnitt exakt an `scheduler_id < 255` und `is_online = 1` vor der Sortierung; zusätzliche Prädikate werden abgewiesen. 15 Lehrabfragetests, 16 Offlinevertragstests, Validator und Curriculumprüfung bestehen. Das qualifiziert keine Scheduler- oder Worker-Runtimewerte.

### IDX-007 – Terminaldarstellung erneut quellengeprüft (17. November 2026)

Die Microsoft-Learn-Seite `sys.dm_db_page_info` wurde am aktuellen Stand erneut geprüft: Sie führt die Nachbarseitenfelder auf, dokumentiert an dieser Stelle aber keinen Terminal-Sentinel. `SRC-172` trägt das aktuelle Abrufdatum. Der Quellencheck entscheidet den Terminalwert nicht; unabhängiger Review, isolierter Enginepilot, Seiten-Cap und Splitverhalten bleiben als Gates bestehen. Kein SQL wurde ausgeführt.

### IDX-007 – Blattseitenfilter und Konkurrenzschwelle an die Ergebnisabfrage binden (17. November 2026)

Eine Negativprobe zeigte, dass die IDX-007-Prüfung die erforderlichen Blattfilter nur irgendwo im SQL-Text fand und deshalb einen wirkungslosen `CASE` statt des finalen Filters akzeptierte. Die Schlussklausel ist jetzt exakt an Blattindexfilter, Gruppierung sämtlicher Seitenkettenfelder und eine Mindestgruppe von zwei wartenden Sessions gebunden. Zwei Regressionen decken einen Decoy-Filter und eine abgesenkte `HAVING`-Schwelle ab. Die statischen Lehr- und Offlineverträge bestehen. Umfang: ein Arbeitspaket, ein PR, keine neue Quelle und keine SQL-/Runtimeausführung. Unabhängiger Methodenreview, bestätigter Terminalwert, Seiten-/Zeitgrenzen, Splitverhalten und isolierter Enginepilot bleiben offen.

### IDX-007 – zusätzliche Resultsets vor der Seitendiagnose abweisen (17. November 2026)

Eine Negativprobe fügte nach der Zeitmarker-Deklaration und vor dem
`PageWaits`-CTE ein zusätzliches `SELECT` ein. Der Lehrvalidator akzeptierte
dadurch ein fremdes Resultset vor der Seitendiagnose. Die Quellformprüfung
verlangt jetzt die erwartete Deklaration unmittelbar vor dem CTE; eine
Regression deckt das zusätzliche Resultset ab. Dies bleibt ein statischer
Quellcheck ohne authentische DMV-Aufnahme oder Engine-Nachweis.

### DGN-004 – vollständige Quellfixture-Syntax in der CI absichern (17. November 2026)

Der DGN-004-ScriptDom-Check erfasste nur die Kandidatensnapshot-Abfrage. Er bindet jetzt genau alle vier SQL-Fixtures – Plantransport, R-Prozedur, H-Kontrollprozedur und Kandidatensnapshot – und parst sie mit den SQL-Server-Grammatiken 2019, 2022 und 2025. Der Workflow wird bei Änderungen an jeder Fixturedatei ausgelöst. Lokaler Parserlauf und DGN-004-Quelltests bestehen; der Syntaxnachweis behauptet keine Serverkompilierung oder Engineausführung. Umfang: ein Arbeitspaket, ein PR, keine neue Quelle und keine SQL-/Runtimeausführung. Quellen-/Ergebnisreview, vollständige Kandidatenerfassung, Plan-/Handleidentität, Windows-Prozessbaumabbruch und Versions-/Runtimegates bleiben offen.


### RES-004 – Semaphoreauswahl fail-closed an `OwnWaits` binden (17. November 2026)

Der RES-004-Abfragevalidator akzeptierte einen CTE, der alle Semaphorezeilen durch `WHERE 1 = 0` entfernte, weil er die erwartete `SELECT DISTINCT`-Form nur global im SQL-Text suchte. Er verlangt jetzt den exakt einmaligen `ObservedSemaphores`-CTE mit ausschließlich den distinct Pool-/Semaphore-Schlüsseln aus `OwnWaits`. Zwei synthetische Regressionen sichern den Leerausgabefilter und eine fremde Quell-DMV. 33 Lehrabfragetests, der Validator und 24 Offlinevertragstests bestehen. Umfang: ein Arbeitspaket, ein PR, keine neue Quelle und keine SQL-/Runtimeausführung. Authentische Request-/DMV-Herkunft, Methodenreview und isolierter Grant-Wait-Pilot bleiben offen.

### RES-004 – zusätzliche Resultsets vor der Grant-Wait-Diagnose abweisen (17. November 2026)

Eine Negativprobe stellte vor die eigentliche Abfrage ein zusätzliches
`SELECT`. Der Lehrvalidator akzeptierte dieses fremde Resultset. Die
Quellformprüfung weist jetzt zusätzliche ausführbare Resultset-, DML- und
EXEC-Statements vor dem `OwnWaits`-CTE zurück und maskiert Stringliterale bei
der Erkennung. Eine Regression deckt den Zusatz ab. Das ist nur ein statischer
Vertragscheck ohne authentische DMV-Aufnahme oder Engine-Nachweis.

### RES-001 – zusätzliche Resultsets vor der Scheduleraufnahme abweisen (17. November 2026)

Eine Negativprobe stellte vor die Scheduler-Momentaufnahme ein zusätzliches
`SELECT`. Die Quellprüfung verlangt jetzt, dass auf die UTC-Marker-Deklaration
unmittelbar die vorgesehene Schedulerabfrage folgt. Eine Regression deckt das
fremde Resultset ab. Das ist ein statischer Lehrabfragecheck ohne authentische
Schedulerwerte oder Laufzeitqualifikation.

### DGN-007 – feste Ressourcenlimits im Koordinator durchsetzen (17. November 2026)

Der Koordinator ließ bisher höhere CPU- und Speicherlimits als die festgelegten
Vergleichswerte 4 CPU/8 GiB durch. Koordinator und Capture-Receipt verlangen
jetzt exakt diese Konfiguration; synthetische Regressionen weisen größere
Werte zurück. 66 fokussierte Tests bestehen. Hostkapazität, Hostexklusivität,
Incidentherkunft und SQL-Runtime bleiben davon unbewiesen. Das geschlossene
Python-3.12-AST-Profil wurde für den geänderten Runner neu gebunden; dadurch
wird keine Ausführung attestiert.

### RES-004 – Request-Wartezeit an die finale Ausgabe binden (17. November 2026)

Der Abfragevalidator akzeptierte `r.wait_time AS request_wait_time_ms` als
Decoy im `OwnWaits`-CTE, obwohl die finale Ausgabe das Feld nicht mehr enthielt.
Er verlangt nun den direkten Request-DMV-Wert in der Schlussprojektion;
`mg.wait_time_ms` bleibt separat. Eine synthetische Regression deckt den
verschobenen Ausdruck ab. 37 Lehrabfragetests und der Validator bestehen lokal.
Keine authentische DMV-Aufnahme oder Runtimeprüfung.
### IDX-007 – aggregierte Waitdauer an die Requestquelle binden (17. November 2026)

Der Lehrvalidator ließ bisher einen konstanten `wait_time`-Decoy in der
`PageWaits`-Projektion zu, solange `r.wait_time` unter einem anderen Alias
irgendwo im CTE vorkam. Er verlangt den direkten Request-DMV-Ausdruck nun in
der Projektion, die von den Aggregaten verwendet wird. Eine Regression sichert
den Fall; 35 fokussierte Tests und der Validator bestehen. Kein Laufzeitbeleg.

### RES-004 – verschachtelte Statements im Abfragevorlauf zurückweisen (17. November 2026)

Der Präfixvalidator erkannte zusätzliche ausführbare Statements nur an
Statementgrenzen. Eine bedingte Ausgabe (`IF ... SELECT`), ein Blockwrapper
(`BEGIN ... END`) und die Sessionzustandsänderung `SET NOEXEC ON` konnten die
Prüfung umgehen. Der Validator untersucht den vollständigen maskierten Vorlauf
und weist diese Formen zurück; Regressionen erhalten zugleich die Behandlung
von Kommentaren und Stringliteralen. 40 fokussierte Tests und der
RES-004-Quellvalidator bestehen. Die Prüfung bleibt statisch und qualifiziert
weder T-SQL-Laufzeit noch DMV-Herkunft oder einen tatsächlichen Grant-Wait.

### RES-001 – ausführbare Statements vor der Scheduler-Abfrage abweisen (17. November 2026)

Der Lehrquery-Validator verlangte den Capture-Marker am Anfang und genau ein
sichtbares `SELECT`, stellte aber nicht sicher, dass unmittelbar danach die
Scheduler-Abfrage folgt. Eine eingeschobene Sessionänderung wie `SET NOEXEC ON`
konnte daher akzeptiert werden. Der Validator verlangt jetzt nach Maskierung von
Kommentaren und Literalen direkt das Scheduler-`SELECT`; Regressionen decken
zusätzlich `IF ... SELECT` und `BEGIN ... END` ab. 21 fokussierte RES-001-Tests
und der Quellenvalidator bestehen lokal. Das bleibt ein statischer Strukturcheck
ohne T-SQL-Runtime- oder DMV-Herkunftsnachweis.

### DGN-007 – `_md5` in die native Fallback-Dateiinventur aufnehmen (17. November 2026)

Der gebundene CPython-3.12.16-Zielimageexport enthält neben `_blake2`, `_sha1`,
`_sha2` und `_sha3` auch `_md5`; der bisherige Dateivertrag ließ dieses
Fallbackmodul aus. Der Offline-Scanner bindet nun den festen Pfad, exakten
SHA-256 und die größenbegrenzte reguläre Datei in dieselbe geprüfte
Imageinventur ein. Eine gezielte Regression verlangt den `_md5`-Pfad und
Digest. Der Vollscan bestätigt die zusätzliche Imagekandidatur, lässt aber
beide Cachebedingungen in `hashlib.py` unbekannt, weil Dateipräsenz keinen
Import belegt. Das Ergebnis bleibt `CANDIDATES_ONLY`, ohne Interpreterstart,
P11- oder Runtimeattestation. Umfang: ein Paket, ein PR, eine neue gezielte
Regression; keine neue Produktquelle, kein Container-/SQL-/Lab-Lauf und keine
menschliche Generalprobe. Danach wird mit dem nächsten einzeln belegbaren
statischen Quellkandidaten fortgesetzt.

### DGN-007 – Hashlib-Fallbackzweige den Image-Dateikandidaten zuordnen (17. November 2026)

Innerhalb des nächsten abgegrenzten Offlinepakets verbindet der Scanner die
sieben quellgeprüften `__get_builtin_constructor()`-Zweige mit den fünf
digest- und größenbegrenzten Extensiondateien des gepinnten Zielimages. Eine
Regression prüft die vollständigen Kandidaten und verwirft eine unvollständige
Imageinventur. Der vollständige Scan bleibt `CANDIDATES_ONLY` mit 447
unbekannten Bedingungen; insbesondere sind die dynamischen Cache-Guards kein
Import- oder Konstruktorerfolgsnachweis. Umfang: ein Paket, ein PR, eine
gezielte Regression; keine neue Produktquelle, kein Interpreter-/Container-/
SQL-/Lab-Lauf und keine menschliche Generalprobe. Mit dem nächsten einzeln
belegbaren Quellenkandidaten autonom fortfahren.

### DGN-007 – Modulstart-Eingaben direkter Regex-Compiles inventarisieren (17. November 2026)

Der Scanner bindet jetzt direkte `re.compile`-Quellaufrufe aus dem statischen
Modulstartpfad an Modul, Datei-Hash, Zeile und Argumentform. Der frische
CPython-3.12.16-Quell-/Image-Scan findet 13 Kandidaten (elf String-, zwei
Byte-Literale); Aufruf und Parse bleiben unbeobachtet. 301 fokussierte
Regressionen bestehen. Die Closure steht weiter bei 60 Modulen und 316 Kanten;
447 Bedingungen bleiben unbekannt. Dieser enge Kandidatenschnitt umfasst weder
indirekte oder spätere Aufrufe noch die Regex-Parsepfade und ändert kein
Runtime-/P11-Gate. Umfang: ein Paket, ein PR, eine gezielte Regression; keine
neue Produktquelle, kein Interpreter-/Container-/SQL-/Lab-Lauf und keine
menschliche Generalprobe. Mit dem nächsten einzeln belegbaren Quellenkandidaten
fortfahren.

### DGN-007 – Regex-Literaltypen bis zum Tokenizerpfad binden (17. November 2026)

Ein weiterer statischer Fact bindet die drei gepinnten CPython-Quellmodule für
`re.compile` → `re._compiler.compile`/`isstring` → `re._parser.parse` →
`Tokenizer.__init__`. Für die 13 direkten Quellkandidaten folgt bedingt darauf,
dass das Muster ausgewertet und der Parser erreicht wird: elf Stringliterale
setzen `istext` auf `True`, zwei Byte-Literale auf `False`. Die 302 fokussierten
Regressionen und der vollständige Zielscan bestehen. Der Scan bleibt
`CANDIDATES_ONLY` mit 60 Modulen, 316 Kanten und 447 unbekannten Bedingungen;
Parserzugang, Standardbindung der `re.compile`-Aufrufe sowie tatsächliche
Ausführung bleiben unbeobachtet; ein Regexcachetreffer kann den Parserpfad
überspringen. Umfang: ein Paket, ein PR, eine gezielte Regression; keine neue
Produktquelle, kein Interpreter-/Container-/SQL-/Lab-Lauf und keine menschliche
Generalprobe. Mit dem nächsten einzeln belegbaren Quellenkandidaten fortfahren.

### DGN-007 – Compile-Flags der Regex-Quellkandidaten auflösen (17. November 2026)

Der Regex-Quellvorschnitt ordnet jetzt auch die Compile-Flags der 13 direkten
Literal-Kandidaten zu. Fünf Aufrufe lassen `flags` weg und verwenden bedingt
auf die gepinnte `re.compile`-Signatur den Standard `0`. Acht benannte
`RegexFlag`-Ausdrücke werden über die gebundene Enum- und Konstantenquelle zu
`88` (vier Aufrufe), `8` (zwei) beziehungsweise `256` (zwei) ausgewertet. 302
Regressionen und der Vollscan bestehen; 447 Bedingungen bleiben unbekannt.
Weder Aufruf, Standardbindung noch Parserzugang sind beobachtet, und ein
Regexcachetreffer kann den Parse vermeiden. Umfang: ein Paket, ein PR, eine
gezielte Regression; keine neue Produktquelle, kein Interpreter-/Container-/
SQL-/Lab-Lauf und keine menschliche Generalprobe. Mit dem nächsten einzeln
belegbaren Quellenkandidaten autonom fortfahren.

### DGN-007 – initialen Parser-VERBOSE-Modus quellenbinden (17. November 2026)

Für die 13 direkten Regexliteral-Kandidaten wird jetzt auch die anfängliche
`_parse_sub`-Flagsmaske aus dem gebundenen `re._parser.parse`-Quellpfad
abgeleitet: `flags & SRE_FLAG_VERBOSE` ist für vier Kandidaten gesetzt und für
neun nicht gesetzt, jeweils nur falls der Compile-Aufruf den Parser erreicht.
Inline-Flags können den späteren Modus ändern; Aufruf und Parse bleiben
unbeobachtet. 302 Regressionen und der Vollscan bestehen, weiterhin
`CANDIDATES_ONLY` mit 447 unbekannten Bedingungen. Umfang: ein Paket, ein PR,
eine gezielte Regression; keine neue Produktquelle, kein Interpreter-/Container-/
SQL-/Lab-Lauf und keine menschliche Generalprobe. Danach mit dem nächsten
einzeln belegbaren Kandidaten der freigegebenen Folge fortfahren.

### DGN-007 – Inline-VERBOSE und ignorierte Regexliteralsyntax geprüft (17. November 2026)

Der Offline-Quellscan bindet alle 13 direkten Regexliteral-Kandidaten. Er findet
weder Inline-Flaggruppen mit `x` noch Leerraum-/Kommentarzeichenkandidaten in
Mustern mit anfänglich gesetztem VERBOSE-Modus. Ein Literal in `tokenize.py:39`
enthält einen lexikalischen `#`-Marker, aber sein anfänglicher VERBOSE-Modus ist
nicht gesetzt. Neben `WHITESPACE` ist jetzt der gepinnte `_parse`-AST-Zweig
gebunden, der Leerraum nur unter `verbose` überspringt und den Kommentar bis
`None` oder `\n` liest. Parserzugang oder spätere Moduswirkung sind damit nicht
belegt. 304 fokussierte Regressionen bestehen. Umfang: ein Offlinepaket, eine
Regression, keine neue Produktquelle und keine Interpreter-/Container-/SQL-/
Lab-Ausführung oder menschliche Generalprobe. Der Befund bleibt
`CANDIDATES_ONLY`; weitere freigegebene Entwicklungsbereiche werden unabhängig
davon fortgesetzt.

### DGN-007 – Cachelookup vor dem Regexparser binden (17. November 2026)

Die Fortsetzung nach PR #1045 ist auf ein Offlinepaket, einen PR und einen
bereits gepinnten CPython-Quellkandidaten begrenzt; keine neue Produktquelle,
kein Image-/Container-/SQL-/Runtime-Lauf und keine menschliche Generalprobe.
Der Paketinhalt bindet die Reihenfolge `_cache2` → `_cache` und den gemeinsamen
Pattern-/Flags-Schlüssel an `re._compile`, ohne einen aktuellen Cachezustand oder
Parseraufruf zu behaupten. Nach diesem Checkpoint ist als nächster separater
Kandidat die Byte-zu-Text- und Escapezeichenbehandlung von `Tokenizer` gegen die
bereits gepinnte `re/_parser.py`-Quelle zu prüfen. Die Kandidaten bleiben
statische Quellbefunde und schließen weder P11- noch Runtimegates.

### DGN-007 – Tokenizer-Byteabbildung und Escapes binden (17. November 2026)

Nach dem integrierten Cachepfad ist der nächste Offlineumfang auf ein Paket,
einen PR und einen bereits gepinnten CPython-Quellkandidaten begrenzt. Er bindet
die Latin-1-Abbildung von Byte-Mustern sowie die Tokenizerbehandlung von
Backslash/Folgezeichen an `re/_parser.py`. Es gibt keine neue Produktquelle und
keinen Interpreter-, Container-, SQL-, Lab- oder Runtime-Lauf; menschliche
Generalprobe bleibt ausgeschlossen. Nach diesem Checkpoint wird als nächster
Quellfact die Zuweisung `sourceget = source.get` in `_parse` und ihr Aufrufpfad
zu `Tokenizer.get` geprüft. Statische Kandidatenbefunde ersetzen keine
Tokenizerausführung oder P11-Qualifikation.

Checkpoint 17. November 2026: Der `sourceget`-Alias ist an die gepinnte
`Tokenizer.get`-Methode gebunden; der vollständige Archivscan fand zehn
syntaktische Alias-Aufrufstellen bei weiterhin 13 Regexliteral-Kandidaten und
`CANDIDATES_ONLY`. Als nächster begrenzter statischer Kandidat wird der
Aufrufpfad von `_parse_sub` zu `_parse` geprüft. Es bleibt bei einem Paket und
einem PR je Welle; Interpreter-, Container-, SQL-, Lab-, Runtime- und
Generalprobenläufe sind davon nicht umfasst.

Checkpoint 17. November 2026: `_parse_sub` ist jetzt statisch an genau einen
Aufruf von `_parse` gebunden, der mit `itemsappend` verkettet ist und die
verschachtelten Argumente aus der gepinnten CPython-Quelle erhält. Die
Gegenprobe ändert den Verschachtelungswert und muss den Kandidaten ablehnen.
Als nächstes werden Rückkehr- und Alternationsbedingungen derselben Funktion
als begrenzte Kandidatenbindung betrachtet. Weiterhin keine Interpreter- oder
Runtimeausführung, P11-Qualifikation oder menschliche Generalprobe.

Checkpoint 17. November 2026: Die Quelle bindet jetzt zusätzlich die
Alternationsschleife, den Wurzelgruppen-Refresh des `VERBOSE`-Flags und die
Ein-Alternative-Rückgabe. Die Gegenprobe ändert das Alternationszeichen und
verwirft den Kandidaten. Als nächstes folgt die statische Rückgabebehandlung
für mehrere Alternativen und der Aufbau des Subpatterns.

Checkpoint 17. November 2026: Die Rückgaben für eine oder mehrere Alternativen
sind jetzt an `items[0]`, `SubPattern`, `IN`-Zeichensatz und allgemeinen
`BRANCH`-Zweig gebunden. Die Mutationsgegenprobe vertauscht den Branch-Op und
muss den Kandidaten ablehnen. Nächster begrenzter Checkpoint: Voraussetzungen
des Zeichensatz-Kurzpfads statisch binden, ohne seine Auswahl oder Ausführung
zu behaupten.
Checkpoint 18. November 2026: Die Voraussetzungen des Zeichensatz-Kurzpfads
sind an genau-ein-Element-Alternativen, `LITERAL` und nicht-negierte `IN`
gebunden. Die Schleifen-`else`-Kante führt zum `IN`-Subpattern. Eine Mutation
der Elementart wird verworfen. Nächster statischer Kandidat: Erkennung und
Extraktion gemeinsamer Präfixe der Alternativen.
Checkpoint 18. November 2026: Der gemeinsame Präfix wird jetzt über das gleiche
erste Element erkannt, bei Abweichung gestoppt, aus den Alternativen entfernt
und in das Subpattern verschoben. Der synthetische Negativfall kehrt den
Vergleich um und wird abgelehnt. Nächster Schritt ist die statische Einordnung
der Übergänge von dieser Präfixschleife zum Zeichensatz- oder Branch-Pfad.
Checkpoint 18. November 2026: Die Reihenfolge der Einzelalternative,
Präfixextraktion, Zeichensatzverkürzung und allgemeinen Branch-Rückgabe ist als
eine statische Struktur gebunden. Eine Gegenprobe verschiebt den Branch vor den
Zeichensatzpfad und wird abgelehnt. Als nächstes wird `_uniq` im gepinnten
Parser separat an seine konkrete Deduplizierungsoperation gebunden.
Checkpoint 18. November 2026: `_uniq(items)` ist an die gepinnte Operation
`list(dict.fromkeys(items))` gebunden; eine Mutation auf `set(items)` verwirft
den Befund. Dadurch ist die konkrete quellseitige Deduplizierungsoperation des
Zeichensatzpfads geprüft. Nächster Kandidat: die statische Form des
`BRANCH`-Operators und der zugehörigen Subpattern-Elemente.

Checkpoint 18. November 2026: Das Parserergebnis `(BRANCH, (None, items))`
ist an den gleichnamigen Compilerzweig gebunden. Alternativenkompilierung,
`JUMP`-Offsets, `FAILURE`-Marker und Offset-Patching sind statische
Quellbefunde. Der Compiler wurde nicht ausgeführt. Nächster Schritt ist die
Shape- und Übergabebindung zwischen Parserausgabe, Compilerargument und
Bytecode-Container.

Checkpoint 18. November 2026: `_code` bindet die geordnete Erzeugung und
Rückgabe des Listencontainers; `compile()` übergibt ihn zusammen mit den
Flags `flags | p.state.flags` sowie `p.state.groups - 1`, `groupindex` und
`tuple(indexgroup)` an `_sre.compile`. Die Gruppenabbildung wird aus
`p.state.groupdict` aufgebaut; die synthetische Metadatenmutation wird
verworfen. Das ist ein statischer Quellenbefund und keine Laufzeitqualifikation.

Ergänzender Checkpoint 18. November 2026: Der optionale Debugpfad ist an
`flags & SRE_FLAG_DEBUG` und `dis(code)` gebunden. Er liegt nach der
Codeerzeugung und vor Gruppenmetadaten sowie nativer Kompilierung. Die
synthetische Mutation des Disassemblierungsarguments wird abgelehnt. Es gibt
keinen Nachweis eines konkreten Debugaufrufs oder einer Compilerlaufzeit.

Ergänzender Checkpoint 18. November 2026: `compile()` behält für String-/Byte-
Eingaben das Original als `pattern` und ruft den Parser auf; für bereits
geparste Eingaben setzt die Quelle `pattern = None`. Beide Pfade führen
anschließend `p` an `_code(p, flags)` weiter. Eine Mutation der `None`-Übergabe
wird abgelehnt. Dies belegt keine tatsächliche Verwendung des internen
SubPattern-Pfads.

Ergänzender Checkpoint 18. November 2026: `State.groups` leitet die Zahl der
Gruppen aus `groupwidths` ab; `opengroup` nutzt sie für den nächsten Index und
ordnet einen benannten Gruppenwert nach Duplikatprüfung in `groupdict` zu.
Gruppe 0 ist in der Breitenliste initial vorhanden. Eine Mutation der
Namenszuordnung wird abgelehnt. Das bleibt ein statischer Parserquellenbefund.

Checkpoint 18. November 2026: Die Gruppen-State-Bindung enthält zusätzlich
`closegroup(gid, p)`, das die Breite aus `p.getwidth()` am Gruppenindex
speichert, sowie `checkgroup(gid)`, das den Index und eine gesetzte Breite
prüft. Die synthetische Mutation der Breitenzuweisung wird fail-closed
zurückgewiesen. 305 fokussierte Regressionen bestehen. Weiterhin keine
Parserausführung, Compilerqualifikation oder Regexlaufzeit. Nächster Schritt:
die quellgebundenen Parseraufrufe zu `opengroup`, `closegroup` und
`checkgroup` mit diesen State-Methoden verbinden.

Checkpoint 18. November 2026: `_parse` ist nun an den geordneten
Capturegruppenpfad gebunden: `opengroup(name)`, Gruppeninhalt über `_parse_sub`,
Prüfung der schließenden Klammer und anschließend `closegroup(group, p)`.
Zusätzlich sind die `checkgroup`-Aufrufstellen für benannte und numerische
Gruppenreferenzen gebunden. Eine Mutation des `closegroup`-Arguments wird
zurückgewiesen. 305 fokussierte Regressionen und alle PR-Gates einschließlich
des vollständigen gepinnten CPython-3.12.16-Offlineworkflows bestanden für PR
#1063. Der Befund bleibt statisch. Nächster Kandidat: Registrierung einer
vorwärts gerichteten numerischen Gruppenbedingung und spätere Bereichsprüfung
in `parse()` binden.

Checkpoint 18. November 2026: Die bedingte numerische Gruppenreferenz wird
statisch an die spätere Prüfung gebunden. `_parse` wandelt `condname` in eine
Zahl um, prüft `MAXGROUPS` und speichert bei fehlender Gruppe deren Quellposition
in `state.grouprefpos`. Nach dem Parsen prüft `parse()` die gespeicherten
Nummern gegen `p.state.groups` und erzeugt den Fehler mit der gebundenen
Quellposition. Eine Positionsmutation wird zurückgewiesen. 305 fokussierte
Regressionen bestehen lokal; die gepinnte Archivprüfung folgt als PR-Gate.
Keine beobachtete Vorwärtsreferenz oder Runtimeausführung. Nächster Kandidat:
die Lookbehind-Gruppenmarke an ihre Schutzprüfungen binden.

Checkpoint 18. November 2026: `checklookbehindgroup` ist an die aktive
Lookbehind-Grenze gebunden. Bei gesetzter Grenze prüft es zuerst die
Gruppenabgeschlossenheit und verwirft danach Indizes ab der Grenzgruppenzahl.
`_parse` setzt die Grenze auf `state.groups` und stellt sie nur dann zurück,
wenn keine vorherige Grenze aktiv war. Aufrufstellen für numerische, benannte
und bedingte Referenzen sind gebunden. Eine Mutation von `>=` auf `>` wird
zurückgewiesen. 305 fokussierte Regressionen bestehen lokal; der vollständige
CPython-3.12.16-Archivworkflow und alle PR-Gates bestanden für PR #1065. Kein
Laufzeitnachweis. Nächster Kandidat: Breitenberechnung für Gruppenreferenzen
und bedingte Gruppenreferenzen binden.

Checkpoint 18. November 2026: `SubPattern.getwidth()` bindet die gespeicherte
Breite für `GROUPREF` und die minimale sowie maximale Zweigbreite für
`GROUPREF_EXISTS`. Ohne Else-Zweig ist die minimale Breite null. Eine Mutation
von `min(i, l)` zu `max(i, l)` wird zurückgewiesen. 305 fokussierte
Regressionen und alle PR-Gates einschließlich des vollständigen
CPython-3.12.16-Archivworkflows bestanden für PR #1066. Keine konkreten
Gruppenbreiten oder Laufzeitmessung.

Checkpoint 18. November 2026: Parserausgaben `GROUPREF` und `GROUPREF_EXISTS`
sind an `_compile` gebunden. Der Rückverweis wählt den Opcode nach den
Ignore-Case-Flags und verschiebt den Gruppenindex von einsbasiert auf
nullbasiert. Die bedingte Referenz kompiliert beide Zweige und patcht die
Sprungoffsets. Eine Mutation von `av - 1` wird verworfen. 305 fokussierte
Regressionen und der vollständige Offline-Archivworkflow bestanden; PR #1067
und die vier Main-Push-Workflows sind auf `64a17cdb` integriert. Kein
Bytecode- oder Laufzeitnachweis.

Checkpoint 18. November 2026: Der gepinnte CPython-3.12.16-Parser bindet nun
auch die Klassifizierung numerischer Escapes: führende Null mit bis zu zwei
Oktalziffern, dreistellige Oktalliterale mit dem Grenzwert `0o377` und sonstige
Ziffernpräfixe als dezimale Gruppenreferenz, einschließlich Gruppenstatus- und
Lookbehind-Prüfung. Die Mutation der Oktalbedingung wird verworfen. 305
fokussierte Regressionen, PR #1068 und alle vier Main-Push-Workflows bestanden
auf `79abac80`. Dies bleibt ein statischer Quellenbefund, ohne Parserausführung
oder Laufzeitqualifikation.

Der lokale Offlinekandidat bindet die benannte Rückreferenz `(?P=name)` an
Namensvalidierung, `groupdict`-Auflösung, Fehler für unbekannte oder offene
Gruppen, Lookbehind-Grenze und `GROUPREF`-Parserausgabe. Eine Mutation des
Lookup-Ausdrucks wird verworfen; 305 fokussierte Regressionen bestehen lokal.
PR #1069 und alle vier Main-Push-Workflows bestanden auf `86812041`. Keine
Parserausführung oder Runtimeaussage.

Der nächste lokale Kandidat bindet den benannten Zweig bedingter
Gruppenreferenzen über `state.groupdict`, einschließlich Namensvalidierung und
Ablehnung unbekannter Namen. Der bestehende Zahlenzweig und seine spätere
Vorwärtsreferenzprüfung bleiben unverändert. PR #1070 und alle vier
Main-Push-Workflows bestanden auf `38b580af`.

Der lokale Folgeschnitt bindet die Ja-/Nein-Parsearme der bedingten
Gruppenreferenz, das optionale `None` des Nein-Arms, die Ablehnung eines dritten
Arms und die schließende Klammer vor Ausgabe als `GROUPREF_EXISTS`. Die Mutation
der zusätzlichen Armprüfung wird verworfen; 305 fokussierte Regressionen
bestehen. PR #1071 und alle vier Main-Push-Workflows bestanden auf `63786aae`.

`Tokenizer.checkgroupname` ist im gepinnten CPython-3.12.16-Quellstand an
die Namensregeln gebunden: Byte-Muster verlangen ASCII-Gruppennamen;
anschließend müssen Gruppennamen `str.isidentifier()` erfüllen. Beide
Ablehnungszweige verwenden den angegebenen Quelloffset. Eine synthetische
Mutation der Identifierprüfung wird verworfen. PR #1072 integrierte den Schnitt
in Commit `d0f7382d`; 305 fokussierte Tests, sämtliche PR-Gates einschließlich
des vollständigen Offline-Quellenbundles und alle vier Main-Push-Workflows
bestanden. Der statische Befund belegt weder konkrete akzeptierte Namen noch
Parser- oder Regexlaufzeit.

Der lokale Folgekandidat verbindet diese Namensregel nun mit benannten
Capturegruppen: `source.getuntil('>', 'group name')` liest den Namen,
`source.checkgroupname(name, 1)` prüft ihn vor `state.opengroup(name)`. Eine
synthetische Mutation, die den Check entfernt, wird verworfen. Die Quellform
stimmt mit dem offiziellen
[CPython-3.12.16-Parser](https://github.com/python/cpython/blob/v3.12.16/Lib/re/_parser.py#L694-L698)
überein; der fokussierte Satz besteht mit 305 Tests. PR #1074 integrierte den
Schnitt als `7b0c6509`; alle PR-Gates und vier Main-Push-Workflows bestanden.
Es gibt weiterhin keinen Parserlaufzeitnachweis.

Der nächste lokale Folgeschnitt bindet den Fehlerpfad nach der Registrierung:
Eine `error` aus `state.opengroup(name)` wird mit
`source.error(err.msg, len(name) + 1) from None` auf den Gruppennamenoffset
abgebildet. Eine synthetische Offsetmutation wird verworfen; der fokussierte
Satz besteht mit 305 Tests. PR #1075 integrierte den Schnitt als `93303d10`;
alle PR-Gates und vier Main-Push-Workflows bestanden. Das belegt weder einen
tatsächlich doppelten Namen noch Parserlaufzeit.

Der aktuelle lokale Folgeschnitt bindet `Tokenizer.getuntil`: einen leeren
Namen am Terminator mit Offset 1, ein Musterende vor jedem Namenszeichen an
der aktuellen Position und ein Musterende nach Teilname mit dem
Teilnamenoffset `len(result)`. Namen werden erst nach erkanntem Terminator
zurückgegeben. Eine Offsetmutation wird verworfen; 305 fokussierte Tests
bestehen. Der Quellpfad ist im offiziellen
[CPython-3.12.16-Parser](https://github.com/python/cpython/blob/v3.12.16/Lib/re/_parser.py#L263-L278)
digestgebunden. PR #1076 integrierte den Schnitt als `8372b5e8`; alle PR-Gates
und vier Main-Push-Workflows bestanden. Es gibt keinen Parserlaufzeitnachweis.

Der aktuelle lokale Folgekandidat bindet nun `Tokenizer.tell()` und
`Tokenizer.error()`: Die Position der nächsten ungelesenen Einheit ist
`self.index - len(self.next or '')`; `error` verwendet `self.tell() - offset`.
Bytefehlermeldungen werden mit ASCII und `backslashreplace` aufbereitet. Eine
Mutation auf `self.index - offset` wird verworfen; 305 fokussierte Tests
bestehen. Die Bindung stützt sich auf den gepinnten CPython-3.12.16-Quelltext,
ohne Tokenizer- oder Parserlaufzeit. Als nächster Schritt folgt die Prüfung,
dass die Capture- und Rückverweiscallsites dieselben `getuntil`-Offsets wie die
Tokenizerfehlerkonvertierung verwenden.

Checkpoint 18. November 2026: Die Capturegruppe liest mit
`getuntil('>', 'group name')`, validiert mit Offset 1 und bindet den
Registrierungsfehler an `len(name) + 1`. Der benannte Rückverweis liest mit
`getuntil(')', 'group name')` und bindet unbekannte sowie offene Gruppen an
denselben Namenoffset. Beide Pfade verwenden den gepinnten `getuntil`-Vertrag;
`Tokenizer.error` bildet ihn über `tell() - offset` auf die Quellposition ab.
Drei synthetische Änderungen an Captureoffset, Rückverweisoffset und
Tokenizerposition werden verworfen; 305 fokussierte Regressionen bestehen
lokal. PR #1079 integrierte den Kandidaten auf `main` (`b4239247`); alle sieben
PR-Gates einschließlich Offlinebundle und Katalogprobe sowie die vier
Main-Push-Workflows bestanden. Dies bleibt statische Quellbindung ohne
Regex-/Tokenizerlauf, Parserfehlerbeobachtung oder Runtimequalifikation.

### DGN-007 – benannte Gruppennamen bis zur Compiler-Metadatenübergabe verbinden (18. November 2026)

Der neue Offlinecandidate verbindet den Namen- und Capturepfad aus
`re/_parser.py` mit der späteren Übergabe in `re/_compiler.py`: `State`
registriert `groupdict[name] = gid`, benannte Capturegruppen rufen
`state.opengroup(name)` erst nach der Namensvalidierung auf, und der
String-Eingabepfad führt über `_parser.parse` zu Compiler-Metadaten aus
`p.state.groupdict`, die an `_sre.compile` weitergereicht werden. Beide
Quelldateien bleiben digestgebunden. Synthetische Mutationen der Registrierung
und des Compiler-Metadatenursprungs werden abgewiesen; 305 fokussierte
Regressionstests bestehen. Das ist eine statische Quellflussbindung, kein
Parser-, Regex-, Compiler- oder Runtime-Nachweis.
