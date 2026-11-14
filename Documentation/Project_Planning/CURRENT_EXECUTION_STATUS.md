# Aktueller Ausführungsstand

Aktualisiert am 14. November 2026: QRY-023s vorgeschlagene CI-Route und die
konkreten ADMIN-/READER-Rechtekontrollen sind auf SQL Server 2019/2022/2025
enginequalifiziert. PRs #586–#588 ergänzten Live-Nachweise für die exakte
RunToken-, Zielnamen- und Demo-ID-Prüfung, jeweils vor Setup und ohne Erzeugung
einer Nutzerdatenbank. QRY-023 bleibt bis zu gesonderter Produkt-/Katalog-
freigabe `PROPOSED` und `runtime_authorized: false`. Die menschliche
Generalprobe bleibt ausgeschlossen.

### DGN-007 – integrierter Import-Only-Worker

Der begrenzte Importworker ist über [PR 352](https://github.com/gecompat/SQL_PerformanceSchulung/pull/352)
integriert. [PR 354](https://github.com/gecompat/SQL_PerformanceSchulung/pull/354)
ergänzte den bestehenden Linux-/CPython-3.12-Sourcejob um synthetische
Gegenproben und einen gebundenen Import-Only-Lauf der drei DGN-Einstiege;
[Run 41906197113](https://github.com/gecompat/SQL_PerformanceSchulung/actions/runs/41906197113)
bestand mit allen zwölf Importworker-Tests. Die Probe importiert ausschließlich
gebundene Pythonmodule in frischen Prozessen und führt keine DGN-Funktion, Demo
oder SQL-Anweisung aus. Die lokale Beobachtung von 8/1/3 Modulabschlüssen bleibt
an den dokumentierten 27-Member-Snapshot gebunden.

Damit ist nur der Quellkandidat mit einer begrenzten Importbeobachtung
integriert. `runtime_attested`, `import_used_bytes_attested`, `trust_attested`
und `method_approved` bleiben `false`. Operative S15-/P11-Inventur,
Fünf-Formen-/64-KiB-Gate, Profil-/Kanal-/Consumption-/Replaybindung sowie
Prozess-/Ressourcen-Cleanup und vollständige DGN-Lifecycleattestation bleiben
offen. Daraus folgen weder SQL- noch Incidentfreigabe.

### DGN-007 – nächste freigegebene Baseline-Prüfung

Die separat dokumentierte CPython-3.12.16-Imagekandidatur ist jetzt zusätzlich
gegen die OCI Registry-Blobbytes nachgerechnet: Childmanifest und Configdigest
sowie alle sieben komprimierten Layerdigests/-größen und entpackten DiffIDs
stimmen unabhängig überein. Der aktuelle `buildpack-deps:bookworm`-Tag hat
denselben vierteiligen Layer-, DiffID- und Historypräfix; seine heutige
Auflösung beweist nicht den historischen FROM-Tagdigest. Ein ohne
Interpreterstart aus OCI-Layer 6 gelesener Configure-Abgleich bindet 22
Bootstrapmodule, 79 Standardbibliotheks-/Extensionmodule sowie 27
Builtin-Inittab-Einträge; Setup, `MODBUILT_NAMES`, Inittab und 79
ABI-markierte Dateien stimmen vollständig überein. Zusätzlich stimmen 684 von
684 installierten CPython-`Lib/`-Quelldateien bytegenau mit dem verifizierten
Quellarchiv überein. Der frühere statische Vorschnitt mit 53 Quellen ließ
Klassenkörper aus. Der reproduzierbare Lexikalscan über alle AST-Knoten zählt
264 Quellkandidaten und 2.438 Importkanten; er überschreitet die
256-Recordgrenze. Der getrennte Modul-/Klassenkörper-Vorschnitt enthält 59
Quellkandidaten und 287 Kanten; er schließt unaufgerufene Funktionskörper aus,
wertete aber Plattformzweige nicht aus und erfasst keine Imports aus später
aufgerufenen Funktionen, Dekoratoren oder C-/Frozen-Aufrufen. Keiner der drei
Werte ist vollständige Importclosure oder P11-Sollinventur. Ein ergänzender
Linux-/CPython-3.12-Zielzweigfilter entscheidet zusätzlich die gebundenen
Builtin-Fakten `posix` vorhanden/`nt` abwesend: fünf sichere Bedingungen und
39 unbekannte, 58 Module/282 Kanten; `ntpath` entfällt. Der begrenzte
Modulstart-/Direktaufrufvorschnitt verfolgt direkte Calls, einfache lokale
Funktionsaliases, lokale Klassenmethoden, direkt importierte Quellfunktionen,
einfache Modulalias-Calls und mögliche Generatorausdrucks-Calls in 233 lokalen
Funktionen, 93 Quellkandidaten und 572 Kanten; vier der Erweiterungen zum
früheren 63er-Stand sind `locale`, `selectors`, `signal` und `subprocess`.
Die jüngste statische Fortsetzung folgt nun auch explizit importierte
Quellklassenmethoden und vorhandene `__init__`-Konstruktoren. Nach Korrektur
der importierten Zielpaare zählt der Kandidatenscan 92 Module/572 Kanten und
433 lokale Funktionen (22 entschiedene, 1.399 unbekannte Bedingungen; Digest
`f3edce40f628d8ef5a36e779378662e9de8e1a571c8dd0c288b70517ede68973`).
Der Scan folgt nun zusätzlich `from package import module [as alias]` und
relativen Varianten, direkte Methodenaufrufe auf frisch konstruierten
Klassenobjekten, direkte gleichscope Variablenbindungen und einfache Aliase
solcher Instanzen sowie `self.method()`-/`cls.method()`-Kanten einschließlich
direkter lokaler Closure-Helfer. Spätere Quellwellen ergänzen bekannte lokale
und importierte Basen, Aliase, `super()`-Formen sowie geerbte Konstruktoren und
Methoden auf frisch konstruierten Unterklassen. 74 synthetische Tests bestehen.
Dynamische Calls, vollständige MRO, Deskriptoren, `__new__`, C-/Frozen-Aufrufe
und modulübergreifendes Rebinding bleiben offen. Der aktuelle gebundene
Archivscan zählt 92 Module/573 Kanten/471 besuchte Funktionen, 22 entschiedene
und 1.452 unbekannte Bedingungen; Quelldigest
`f3edce40f628d8ef5a36e779378662e9de8e1a571c8dd0c288b70517ede68973`. Die
zwölf Scanwurzeln sind zusätzlich durch AST-Abgleich an die
fünf Bootstrappräfiximports, acht Profilquellenimports und den `zlib`-Einbau
gebunden; das belegt weiterhin keine tatsächlich gehaltenen Laufzeitbytes.
Die dynamische Importkandidatenanalyse erkennt nun auch f-Strings aus
Textsegmenten und direkten oder verschachtelten Stringkonstanten ohne
Formatangabe oder mit wertneutralem `:s` sowie mit semantisch identischer
`!s`-Konvertierung inline; Laufzeitausdrücke, `!r`/`!a` und andere
Formatangaben bleiben unaufgelöst. Die
fokussierte Regression besteht mit 105/105 Fällen.
Archivclosure und Modulstartscan bleiben unverändert; der Befund ist weiterhin
`CANDIDATES_ONLY`, keine vollständige P11-Inventur.
PR #610 hat den Größenfehler des
SESSION_END-Quellbuilders nach unabhängiger Prüfung und 18 grünen Headchecks
behoben und wurde als `7b756bb1fc6c124b8dbe90c261de67addd2503c5` integriert;
alle ausgelösten Main-Workflows bestanden ebenfalls. Buildherkunft und
vollständige unabhängige S15-/P11-Sollrecords sind weiter offen. `SOABI`, `DESTSHARED` und
der Sysconfigdatenmodulname sind jetzt aus der gebundenen CPython-Sysconfigquelle
vorläufig vorgewählt; die Kindumgebung muss `_PYTHON_SYSCONFIGDATA_NAME`
ausdrücklich abwesend halten, da `-I` den direkten `os.environ`-Zugriff nicht
unterbindet. Das sind Quellenwerte, keine tatsächlichen `sysconfig`-Rückgaben.
Nächster Gate ist die vollständige Vorwahl dieser Sollfelder und der endgültigen
Bootstrapbytes samt Quellen-/Aufrufreview. Das OCI-Image liefert den direkten
Executablekandidaten `/usr/local/bin/python3.12` (18.304 Bytes, Modus `0755`,
gebundener SHA-256); `/usr/local/bin/python3` ist ein Symlink darauf. Auch
dieser Dateibeleg bestimmt nicht den tatsächlichen `sys.executable`-Wert;
erst danach darf die einmalige operative Inventur mit fünf vollständigen
Darstellungen und gemeinsamem 64-KiB-Gate folgen. Es gab in diesen Schritten
keine Profilaufnahme oder Worker-/SQL-Ausführung; die Generalprobe bleibt
ausgeschlossen. Ein konkreter Größenfehler wurde zusätzlich reproduziert: Die
vollständige 44.542-Byte-Profilkontrollquelle ließ den bisherigen
SESSION_END-Builder mit 146.775 Scriptbytes am 131.072-Byte-Cap scheitern.
Ein additiver zlib-Builder hält dieselben Rohbytes in einem begrenzten Stream
und erzeugt 129.688 Scriptbytes; er ergänzt `zlib` als sechsten direkten Import.
463 gezielte Source-Tests bestehen. Die neue Route liefert weder operative
S15-/P11-Sollrecords noch ein Profil-/Workerattest. Der feste Lexikalscan samt
Grenzen steht in §19.15 des
[DGN-007-Designs](DGN_007_IMPORT_PROFILE_BINDING_DESIGN.md).

## Graph Tables – Curriculum-Lernnotiz

Die [Graph-Tables-Lernnotiz](../Curriculum/GRAPH_TABLES_LESSON.md) ergänzt
`LO-M03-06` um die Erklärung gerichteter Pfade mit `MATCH` und relationalen
Joins. Sie trennt Ergebnisgleichheit von tatsächlicher Planevidenz. Der
QRY-023-Entwurf bleibt `PROPOSED`; `DEC-079` gibt die Methodik frei und
`DEC-080` akzeptiert die acht ausführbaren T-SQL-Dateien ausschließlich für
den statischen ScriptDom-Parse der Grammatiken 150/160/170. Diese Prüfung ist
keine Enginekompilierung oder Laufzeitfreigabe. `DEC-081` bestätigt die drei
Produktbuildpins als aktuelle Linux-Servicingstände zum 12. November 2026;
`DEC-082` bestätigt die aktuellen MCR-Manifest-/Konfigurationsdigests und
Produktlabels gegen den vorgeschlagenen Lock. Der FWK-010-Caller unterstützt
jetzt getrennte SQL-Anmeldungsprofile pro Phase; QRY-023 weist Setup-/Installations-
phasen `ADMIN`, lesende Qualifikations- und Messphasen `READER` sowie Cleanup
`ADMIN` zu. Tatsächliche Serverprinzipale und Minimalrechte, Ressourcen- und
Abbruchdurchsetzung, Cleanupqualifikation, formale Harnessabnahme und sämtliche
Runtimegates bleiben unbewiesen. Der Qualifikationspreflight prüft nötige
positive Rechte; er inventarisiert keine direkten oder geerbten Zusatzrechte.
Eine bloße `sysadmin`-/`db_owner`-Mitgliedschaftsprüfung würde das nicht lösen,
da die SQL-Rollenfunktionen weder effektive Rechte auswerten noch ohne
Rollenmetadatensicht garantiert ein Ergebnis liefern. Das bleibt ein explizites
offenes Minimalrechte-Gate.

Der offline implementierte READER-Preflight verwendet `sys.fn_my_permissions`
unter der tatsächlichen READER-Identität und vergleicht effektive Rechte für
Server, Datenbank, `dbo`/`lab` und alle 13 gebundenen QRY-023-/FWK-004-Objekte
mit der vorab festgelegten Sollmenge. Zusätzliche, doppelte, spaltenbezogene
oder nicht klassifizierbare Resultate führen fail-closed zu `FAIL_NOT_PROVEN`.
Die ADMIN-Phase bestätigt unter ausreichender Metadatensicht alle 13 gebundenen
Objekte, darunter drei für READER unsichtbare interne Messobjekte, und bindet
diesen Nachweis über einen festen Marker. Der FWK-010-Caller validiert Marker
und begrenzte Endpointliste; die tatsächliche READER-Verbindung prüft `CONNECT`
je Endpoint mit `sys.fn_my_permissions`, ohne Metadatensicht zu benötigen.
Die Liste der QRY-023-eigenen Objekte inventarisiert keine anderen
Instanz-/Datenbanksecurables und schließt dortige Zusatzrechte nicht aus.
Minimalrechte und Runtime bleiben `OPEN`. `DEC-083` legt `CONNECT SQL` als
reguläres READER-Loginrecht sowie die zulässige SQL-Server-`public`-Baseline
`VIEW ANY DATABASE` und normales Endpoint-`CONNECT` ausschließlich für eine
exklusive QRY-023-Einzel-Run-Wegwerfinstanz fest; vor dem Lauf darf es keine andere
Benutzerdatenbank geben. Das ist eine normative Umgebungsgrenze, keine
Rechtevergabe oder Effektivrechtequalifikation. `manifest.proposed.json` und
Offlinevalidator binden diese Grenze jetzt statisch; die Prüfung läuft dadurch
noch nicht. Die read-only ADMIN-Rollen-/SID-/Endpoint- und explizite Rechteinventur sowie
der READER-Exact-set-Preflight sind offline implementiert, aber nicht
enginequalifiziert. Ownership Chain und alle Runtime-/Cleanupgates bleiben
offen.
PR #558 integrierte die isolierte `public`-Baseline. Die anschließende
statische Fehleranalyse fand einen konkreten Laufzeitblocker: Setup erzeugte
keinen Datenbankbenutzer für das separate READER-Login, sodass dessen
target-Datenbankverbindung ohne `guest`-Zugang scheitern würde. `DEC-084`
bindet den eng begrenzten Fix: FWK-010 übergibt den explizit zugeordneten
READER-Login als sichere SQLCMD-Identitätsvariable; Setup ordnet nur einen
aktiven SQL_LOGIN der exakt markierten QRY-023-Datenbank zu und bricht bei
Namens-/SID-Konflikten ab. Der Offlineentwurf und synthetische Gegenproben
belegen noch keine SQL-Kompilierung, reale SID-Zuordnung, Effektivrechte oder
Runtime. QRY-023 bleibt `PROPOSED`; SQL, Lab und Generalprobe bleiben aus.
PR #559 schloss den READER-Datenbankbenutzerfehler nach unabhängigem Review;
der case-insensitive FWK-010-Variablenraum ist gegen Überschreibung geschützt.
Ein weiterer Offlinekandidat bindet nun `reader_permission_expectation_contract`
`1.0`: exakte erwartete READER-Rechtemengen für Server, inventarisierte
Standardendpoints, Datenbank, `dbo`/`lab` und die 13 erwarteten
QRY-023-/FWK-004-Securables. Validator und synthetische Regressionen schützen
zusätzliche Datenbankrechte, unvollständige Objektinventur und runtimeabgeleitete
Sollwerte. Dies attestiert nicht die tatsächlichen Funktionsresultate;
SQL-Ausführung und Runtime bleiben offen; sowohl die vorgeschaltete ADMIN-
Rollen-/SID-/Endpointinventur als auch der READER-`sys.fn_my_permissions`-
Exact-set-Preflight sind inzwischen offline implementiert.
PR #560 integrierte die Sollmenge nach unabhängigem Review und acht grünen
PR-Gates. Die kontraktgeschützte Erfassung belegt weiterhin keine Live-Rechte.
Der aktuelle begrenzte Offlinepunkt implementiert die read-only ADMIN-Inventur
für READER-Login-/Datenbank-SID, Server-/Datenbankrollen, explizite
Grants/DENYs, Benutzerdatenbankbestand und Standardendpointbestand samt
synthetischen Abweichungsfällen. Vor Setup weist der Preflight fremde
Benutzerdatenbanken zurück. Unabhängiger Nachreview bestätigte, dass keine
Systemobjekt-SELECTs pauschal erlaubt werden: bis zur exakten, versionierten
Sollmenge liefert die ADMIN-Phase `FAIL_NOT_PROVEN`. Der QRY-Validator, 93
Regressionen, ScriptDom-Parse der neun eigenständigen T-SQL-Dateien unter
150/160/170, Identifier- und Continuity-Validator sowie der geänderte-Dateien-
Privacy-Scan bestanden. Die acht ausgelösten PR-Workflows waren erfolgreich;
PR #561 wurde als `eaccffcf8f306cd3b9a5c2e334e0d67e5ab80f95` integriert.
Dies belegt weder SQL-Ausführung noch vollständige Katalogsicht. Es wurden
keine Rechte geändert oder vergeben; die exakte Standard-Systemobjektmenge,
Ownership-Chain-Wirkung, SQL-Ausführung und Enginequalifikation bleiben offen.

Die freigegebene QRY-023-Fortsetzung ist offline umgesetzt: Der READER-
Exact-set-Preflight erfasst tatsächliche Rechte pro Server-, Datenbank-,
Schema-, Objekt- und Endpointkontext. ADMIN bestätigt die exakten 13 Objekt-
Namen/-Typen und übergibt einen gebundenen Marker sowie das begrenzte
Endpointinventar. Der FWK-010-Caller validiert beide Handoffs vor dem nächsten
READER-Aufruf; READER prüft danach Endpoint-`CONNECT` selbst mit
`sys.fn_my_permissions`. Der unabhängige Nachreview fand keine offenen P1/P2.
QRY-Validator, synthetische Runner-/Parserregressionen, FWK-010-Validator,
ScriptDom 150/160/170 und der geänderte-Dateien-Privacy-Scan bestehen.
DGN-007 bindet den gemeinsamen Runner zusätzlich mit einem CPython-3.12-
AST-Digest; nach Review wurde exakt dieser eine Digest erneuert. Die zwei
betroffenen DGN-Offline-Gegenprobensuiten bestanden unter CPython 3.12.14.
QRY-023 selbst wurde weiterhin weder auf SQL Server ausgeführt noch als Lab-
oder Generalprobe gestartet. Änderungen sind noch lokal; PR-Gates stehen aus.
Keine Rechtevergabe und keine Rechte- oder `public`-Mutation. Die offene
Systemobjekt-`public`-SELECT-Standardbaseline,
Ownership-Chain-Wirkung und Enginequalifikation bleiben eigenständige Gates.
PR #543 integrierte den Designvorschlag. Ein unabhängiger Review fand keine
P1/P2; der QRY-023-Validator und 49 gezielte Regressionen bestanden. Keine
SQL-, Lab- oder Runtimeausführung.
PR #544 begrenzte anschließend ausdrücklich die Aussage der Demoobjektliste:
sie schließt Zusatzrechte auf anderen Securables nicht aus. Review und sechs
PR-Checks bestanden; die vier ausgelösten Main-Workflows waren grün. Der nächste
Offlinepunkt bindet die bewusst deaktivierte optionale FWK-004-Wartezeiterfassung
an die effektive READER-Rechtematrix. QRY-023 übergibt
`@CaptureSessionWaits=0`; so wird die Wait-Stats-DMV nicht abgefragt und das auf
SQL Server 2022+ dafür notwendige `VIEW SERVER PERFORMANCE STATE` nicht
benötigt. Eine neue Negativregression schützt diesen Parameter. Das bleibt ein
Codepfad-/Quellenbeleg, keine Engine- oder vollständige Minimalrechtequalifikation.
PR #545 integrierte diese Klarstellung; der unabhängige Review fand keine
P1/P2, 50 QRY-023-Regressionen, sieben PR-Checks und fünf ausgelöste
Main-Workflows bestanden. Eine weitere Prüfung der Readerphasen fand, dass
`30_Correctness.sql` vier zusätzliche Oracle-Tabellen liest, die der
Qualifikationspreflight nicht prüfte. Der Preflight könnte daher trotz fehlendem
Oracle-`SELECT` vor der Korrektheitsphase `PASS` ausgeben. Die vier Oraclerechte
werden jetzt vorab gebunden; Laufzeit und effektive Rechte bleiben offen.
Der unabhängige Offline-Review fand keine offenen P1/P2.

Als nächster statischer Schritt wird die Rechteprüfung gegen die tatsächlichen
Reader-Skriptreferenzen synchronisiert: jede direkte `dbo`-/`lab`-Referenz
muss im Preflight abgedeckt sein; unbekannte schemaqualifizierte Verwendungen
und datenbankqualifizierte Namen sowie dynamische `EXEC`-Formen werden
zurückgewiesen; nur der bestehende Messprozeduraufruf ist erlaubt. READER-Skripte dürfen laut statischer
Textprüfung direkt erkennbare schreibende Ziele nur an lokale Tabellenvariablen
richten; erkannte persistente DML-, `SELECT INTO`-, `BULK INSERT`-, DDL- und
Rechteänderungen werden abgewiesen. Die 56 gezielten Regressionen und der
direkte Offlinevalidator bestehen; unabhängiger Review fand nach den
Gegenproben für drei- und vierteilige Objektbezüge sowie indirektes `EXEC`
keine offenen P1/P2. Das ist kein AST-/Engine-/Effektivberechtigungsnachweis.
PR #547 integrierte den Schritt mit sieben erfolgreichen PR-Checks. Der
QRY-023-Mainworkflow sowie die Framework- und Curriculum-/Privacy-Mainworkflows
bestanden ebenfalls; lokales `main` ist auf `6ef003f` synchronisiert und der
Arbeitsbranch ist entfernt. QRY-023 bleibt `PROPOSED` und ohne SQL-, Lab- oder
Runtimeausführung.

Nach diesem Checkpoint wird der statische Abgleich noch fundstellenbezogen
gehärtet: eine nicht erkannte schemaqualifizierte Verwendung darf nicht allein
deshalb als geprüft gelten, weil derselbe Objektname in einer anderen Abfrage
vorkommt. Eine synthetische Regression prüft insbesondere, dass ein
funktionsartiger `dbo`-Aufruf nach einem SELECT-Komma nicht durch einen
gleichnamigen Tabellen-`SELECT` gedeckt wird.
Die lokalen 59 gezielten Regressionen und der Offlinevalidator bestehen;
PR #548 integrierte diese Fundstellenbindung. Sechs PR-Checks und vier
betroffene Main-Workflows bestanden; `main` ist auf `9f15586` synchronisiert,
der Arbeitsbranch ist entfernt. Der unabhängige Review fand keine offenen
P1/P2. Das bleibt statische Textanalyse ohne SQL-, Lab- oder Runtimebeleg,
ohne effektive Serverrechte und ohne Generalprobe.

Der nächste lokale Schnitt erweiterte die direkte Schreibschutzprüfung auf
DDL-Varianten wie `CREATE OR ALTER`, DML-Formen wie `DELETE dbo.Tabelle` ohne
explizites `FROM` und DBCC-Befehle. PR #549 integrierte die Gegenproben mit
sechs gezielten QRY-023-Regressionsfällen und allen sieben erfolgreichen
PR-Checks; fünf betroffene Main-Workflows bestanden. `main` ist auf `ca5899c`
synchronisiert, der Arbeitsbranch entfernt. Der unabhängige Review fand nach
dem DBCC-Gegenfall keine offenen P1/P2. Kein SQL-, Lab- oder Runtimebeleg.

Der nächste lokale Schnitt band die Datenbankkontextstabilität der READER-
Phasen: `USE` in bare, geklammerte, doppelt zitierte und SQLCMD-parametrisierte
Formen wird zurückgewiesen. PR #550 integrierte den Schutz mit 64 gezielten
Tests, sieben erfolgreichen PR-Checks und fünf erfolgreichen betroffenen
Main-Workflows. `main` ist auf `5e348b5` synchronisiert; der Arbeitsbranch ist
entfernt. Engineausführung und tatsächliche Rechte bleiben offen.

Der nächste Offlinekandidat prüft SQLCMD-Steuerzeilen in READER-Skripten:
`:r`-Includes und `!!`-Shellbefehle werden fail-closed abgewiesen; die exakt
gebundene `:setvar SQLCMDMAXVARTYPEWIDTH 0`-Direktive bleibt zulässig,
damit die geprüfte Textdatei nicht zusätzlichen, im Validator unsichtbaren
Code nachlädt oder ausführt. Die lokale Implementierung entfernt ein führendes
UTF-8-BOM vor dem Control-Line-Scan. PR #551 integrierte die Regressionen mit
67 gezielten Tests, sieben erfolgreichen PR-Checks und drei erfolgreichen
betroffenen Main-Workflows; `main` ist auf `e5ecf25` synchronisiert und der
Arbeitsbranch entfernt. Unabhängiger Review fand keine offenen P1/P2.

Der nächste kleine Contracttest schützt explizit, dass ein anderer
`SQLCMDMAXVARTYPEWIDTH`-Wert als `0` in einer READER-Phase abgewiesen wird.
PR #552 integrierte diesen Test mit 68 QRY-023-Regressionen und sechs
erfolgreichen PR-Checks; vier betroffene Main-Workflows bestanden. `main` ist
auf `0481239` synchronisiert, der Arbeitsbranch entfernt. Der nächste kleine
Contracttest bindet die erlaubte `:setvar ... 0`-Direktive ausschließlich an
die Planphase, nicht an Mess- und Korrektheitsskripte. Die Regression und der
Validator bestehen lokal mit 69 Tests; Privacy-Scan der geänderten Testdatei
bestanden. Unabhängiger Review fand keine offenen P1/P2. PR #553 integrierte
den Test mit sieben erfolgreichen PR-Checks; fünf betroffene Main-Workflows
bestanden. `main` ist auf `92480d6` synchronisiert, der Arbeitsbranch entfernt.
Keine SQL-/Lab-/Runtimeausführung.

Die unabhängige vollständige Offlineabnahme des QRY-023-Proposed-Harness fand
einen P1 im READER-Controlguard: Der Validator entfernte T-SQL-Blockkommentare,
bevor er SQLCMD-Controlzeilen suchte. SQLCMD verarbeitet `:r` und `!!` bereits
vor T-SQL-Kommentaren; damit konnte eine verbotene Include- oder lokale
Shellzeile im Blockkommentar den statischen Guard umgehen. Der Validator prüft
Controlzeilen jetzt am unveränderten Skripttext; zwei Regressionen decken
`:r` und `!!` in Blockkommentaren ab. 71 gezielte Tests und der
QRY-023-Validator bestehen. Der unabhängige Nachreview fand keine weiteren
P1/P2 im Kontrollzeilenscan. Zusätzlich korrigiert die Registry den im
Gesamtreview gefundenen P2-Widerspruch: FWK-010 unterstützt phasenspezifische,
verschiedene SQL-Benutzer; offen bleiben deren reale Effektivrechte und die
Runtimegates. PR #554 integrierte beide Korrekturen mit sechs erfolgreichen
PR-Checks und fünf erfolgreichen betroffenen Main-Workflows. `main` steht
sauber auf `ee6ad0f`; lokaler Arbeitsbranch und Remote-Branch sind entfernt.
Keine SQL-/Engine-/Runtimeausführung; QRY-023 bleibt `PROPOSED`.

Als nächster freigegebener Offlinepunkt liegt der Entwurf
[QRY-023-Effektivrechtequalifikation](QRY023_EFFECTIVE_PERMISSION_DESIGN.md)
vor. Er ordnet die aktuellen READER-Rechte den Phasen zu und beschreibt einen
fail-closed Vergleich mit `sys.fn_my_permissions` für Server, markierte
Datenbank, Schemas und vollständige benutzerdefinierte Objektinventur. Der
unabhängige semantische Review fand keine offenen P1/P2 und bestätigte, dass
der Text weder eine normative Sollmenge noch eine Laufzeitqualifikation
behauptet. Ergänzt sind die offenen SQL-Server-`public`-Baselinerechte und die
versionsabhängigen Festserverrollen; `VIEW ANY DATABASE` erhält keine
stillschweigende QRY-023-Freigabe. Der unabhängige Nachreview fand auch in
dieser Baselineergänzung keine P1/P2 und bestätigte, dass keine Änderung an
Instanzrechten oder `public` freigegeben wird. QRY-023-Validator,
Dokumentationslinks und Datenschutzprüfung der fünf betroffenen Dateien
bestanden nach der Ergänzung. Keine Tests des Entwurfs und keine SQL-Ausführung.
Principal-/Effektrechte-,
Ownership-Chain- und Runtimequalifikation bleiben offen; Umsetzung erfordert
eine vollständige versionierte Sollmengenentscheidung.

Die Folgeprüfung fand einen weiteren P2 im READER-SQLCMD-Guard: `GO [count]`
kann eine Batch wiederholen und wurde nach einem führenden Kommentar auf
derselben Zeile nicht erkannt. Der Guard verwirft jetzt rohe `GO`-Zeilen auch
nach ein- und mehrzeiligen Blockkommentarpräfixen. Fünf neue Regressionen
schützen nacktes `GO`, `GO` innerhalb von Blockkommentaren sowie drei
`GO 1000000`-Formen mit inline und mehrzeiligen Kommentarpräfixen. 76 gezielte
Tests und der QRY-023-Validator bestehen. Der unabhängige Nachreview schloss
den Randfall ohne weitere P1/P2; Datenschutzprüfung und Dokumentationslinks der
sechs geänderten Dateien bestehen. Keine T-SQL-Änderung und kein SQL-/Runtime-
Lauf.

`SRC-126` wurde am 12. November 2026 erneut gegen die Microsoft-Editionsmatrizen
für 2019, 2022 und 2025 geprüft. Graph ist in den aufgeführten Editionsvarianten
verfügbar; für 2025 folgt Standard Developer der Standard-Matrix. Das bestätigt
ausschließlich dokumentierte Featureverfügbarkeit, keine tatsächliche Edition,
Enginekompilierung oder Runtimequalifikation. QRY-023 bleibt `PROPOSED`.

## External Tables – statischer Lehr- und Demoentwurf

Der [Konzeptentwurf](EXTERNAL_TABLES_DEMO_CONCEPT.md) knüpft als Vorschlag an
`LO-M03-05`/`CLM-045` an und prüft eine mögliche Ergänzung von `QRY-012`.
Er bindet den synthetischen Snapshot, Tupeloracle, Pushdown-Evidenz,
Statistikphasen und getrennte Cleanupgrenzen. Es wurde keine stabile
Demo-ID vergeben. Die sechs vom Nutzer freigegebenen Quellen-/Testkandidaten
bilden für diesen Schnitt die endliche Obergrenze; verwendet werden keine
neuen Produktquellen, da `SRC-153` bis `SRC-157` bereits aktuell geprüft sind.
Quellen- und Vertragsprüfung bleiben auf den beschriebenen Entwurf begrenzt.
Die formale Curriculumentscheidung, Methodenprüfung, Infrastruktur,
Connectorverfügbarkeit und Laufzeitqualifikation bleiben offen. Kein SQL,
Connector, Netzwerk, Dienst oder Credential wurde verwendet.

Die bestehende `CLM-045`-Traceability ergänzt `SRC-153` bis `SRC-155` als
Quellen zur allgemeinen Provider-/Ausdrucks-/Planabhängigkeit von Remote
Pushdown. Der bestehende Claimtext und die `QRY-012`-Zuordnung bleiben
unverändert; das erweitert keine External-Tables-Laufzeit- oder
Curriculumfreigabe. Der unabhängige Traceability-Review fand keine P1/P2.

Die [Curriculum-Lernnotiz](../Curriculum/EXTERNAL_TABLES_LESSON.md) ergänzt
`LO-M03-05` nun mit einer quellengebundenen Erklärung zu Datenweg, Pushdown,
Statistiken und Architekturabwägungen. Sie ist kein ausführbarer
Demo-Vertrag. Version-/Connectorprofile, Quelle, Credentials, Infrastruktur,
Methodenfreigabe und Runtimequalifikation bleiben offen.

Die registrierte [Curriculum-Scopeentscheidung](EXTERNAL_TABLES_CURRICULUM_SCOPE_REVIEW.md)
ordnet die Lernnotiz als ergänzende Erklärung zu `LO-M03-05`/`CLM-045` ein und
nimmt External Tables im aktuellen Curriculumstand nicht als ausführbare Phase
in `QRY-012` auf. Ein separater Demo-Vertrag und eigene Freigaben bleiben
offen; Infrastruktur- und Runtimegates sind unverändert.

Der unabhängige Lehrnotizreview fand einen Präzisionspunkt zur optionalen
Credentialpflicht bei anonymen Quellen; die Formulierung wurde korrigiert.
Weitere P1/P2 blieben nicht offen.

## External Tables – begrenzter Quellen- und Zugriffswegreview

Der [Offline-Review](EXTERNAL_TABLES_SOURCE_REVIEW.md) bindet die
Microsoft-Matrix für SQL Server 2019/2022/2025: identische External-Table-
Verfügbarkeit reicht nicht für einen identischen Connector-/OS-Pfad. `sqlserver://`
ist der gemeinsame RDBMS-Kandidat, für eine gemeinsame 2019/2022/2025-Matrix
aber nur auf Windows durchgängig dokumentiert; unter Linux gilt dieser
Connectorweg erst ab 2025. Datei- und ODBC-Wege unterscheiden sich zusätzlich
nach Version und Pushdown-Fähigkeit. Die Quelle empfiehlt daher nur den
Kandidaten für einen späteren Entwurf; externe SQL-Quelle, OS, Credentials,
Infrastruktur, Transportmessung, formale Methodenfreigabe und Lauf bleiben
offen. Kein Connector, SQL oder Netzwerk wurde angesprochen.

## Fortsetzung: Datenschutzscanner – fehlerhafte URL sicher klassifizieren

Bei der lokalen Pflichtprüfung stürzte `urlsplit` mit `ValueError` an einer
fehlerhaften URL in lokalem Runtime-Arbeitsmaterial ab. Der Scanner klassifiziert
solche Kandidaten jetzt als redigierten Befund `malformed_url` und setzt die
Prüfung fort; der URL-Wert wird nicht übernommen oder ausgegeben. Sechs
synthetische Scannerregressionen bestehen; die unabhängige Prüfung fand keine
P1/P2. Die lokale Vollprüfung dieses Arbeitsverzeichnisses wurde wegen der
großen ignorierten Runtime-Artefakte beendet. Der Befund bleibt fail-closed;
die unveränderten lokalen Artefakte werden nicht automatisch als sicher
eingestuft.

## Fortsetzung: QRY-023 – effektiven sqlcmd XML-Grenzwert binden

Die unabhängige Prüfung fand, dass der Strukturvalidator zwar eine
`SQLCMDMAXVARTYPEWIDTH 0`-Direktive vor `STATISTICS XML ON` verlangte, aber
eine spätere Überschreibung auf `256` nicht erkannte. Der Validator prüft nun
den letzten passenden Wert vor der XML-Aktivierung; eine Negativregression
deckt genau die Überschreibung `0` dann `256` ab. 46 gezielte Regressionen,
der QRY-023-Strukturvalidator und der Frameworkvertrag bestanden. Die
unabhängige Nachprüfung bestätigt die Schließung dieses Validator-P2 ohne
neue P1/P2. Das bindet den effektiven Skriptvertrag statisch, qualifiziert
weder sqlcmd zur Laufzeit noch T-SQL, Harness oder Demo. Sämtliche zuvor
benannten Identitäts-, Ressourcen-, Cleanup-, Methoden- und Ausführungsgates
bleiben offen.

## Fortsetzung: QRY-023 – Actual-Plan-XML ungekürzt transportieren

Die unabhängige Prüfung fand, dass `sqlcmd` XML-Datentypen standardmäßig bei
256 Zeichen begrenzt und QRY-023s Planphase ihren Erfolg trotzdem nur anhand
der SQL-Summary bewertete. `50_Plan_Evidence.sql` setzt nun vor den zwei
Diagnoseabfragen `SQLCMDMAXVARTYPEWIDTH 0`; die gezielte statische Regression
bindet die Direktive. Die Microsoft-Dokumentation warnt vor der unbeschränkten
Ausgabe bei großen Resultaten. Hier gilt sie nur für zwei `COUNT_BIG`-Pläne;
Plan-Dateien werden weiterhin nicht gespeichert. Das ist ein Skript-/Vertrags-
Nachweis, noch kein Laufzeitbeleg des eingesetzten sqlcmd-Clients. Die
unabhängige Nachprüfung des Offline-Fixes fand keine offenen P1/P2 und bestätigte
die Review-Schwelle für genau diesen Schnitt; sie erteilt keine SQL-/Runtime-
Freigabe und ersetzt nicht die offene Gesamtmethodenabnahme von QRY-023.

Die unabhängige Gesamtprüfung an `b48269a` fand zwei P2-Gates: FWK-010
verwendet für alle Phasen dieselbe Anmeldung, und der Vorschlag führte die
FWK-008-Größen-, Session- und Abbruchgrenzen nicht vollständig. Das QRY-023-
Manifest bindet diese Rollen und Grenzen jetzt explizit, kennzeichnet die
phasenbezogene Rechteausführung aber weiterhin als `OPEN`; die aktuelle
FWK-010-Funktionalität wird nicht als ausreichend dargestellt. Die 1-GiB-
Zieldatenbank-/TempDB-Werte sind nur vorgeschlagene Obergrenzen und erfordern
einen späteren Runtimecaller, der sie vor Setup tatsächlich durchsetzt.
Die Umsetzung dieser Abbruchanforderung im gemeinsamen FWK-010-Caller wurde
im PR-Check verworfen: mehrere unabhängige Sourceprofile (darunter DGN-007 und
CON-010) binden die aktuellen Dateien kryptografisch und qualifizieren
Änderungen separat. Diese QRY-023-Änderung aktualisiert oder umgeht diese
Bindungen nicht. FWK-010 bleibt unverändert; Abbruch, bestätigtes Prozessende
und Cleanup-Reihenfolge sind dort für diesen Anwendungsfall nicht qualifiziert.
Die Runtime-, Rechte- und vollständige Methodenfreigabe bleiben offen.

Die [Quellen- und Methodenprüfung](GRAPH_TABLES_METHOD_REVIEW.md) zeichnet den
unabhängigen Offline-Review vom 12. November 2026 jetzt mit seinem geprüften
Umfang und den offenen Gates nach. Die geprüften Offline-Verträge haben keine
offenen P1/P2 nach den Korrekturen; formale Harness-/T-SQL-Abnahme und
Runtimefreigabe sind davon getrennte, weiterhin offene Entscheidungen.

Der QRY-023-Registry-Scope nennt nun das bereits im `measurement_gate`
festgelegte Profil von 10.000 Pfaden, 30.000 Knoten und 20.000 Kanten, statt zu
sagen, die Last sei noch zu entwerfen. QRY-023 bleibt `PROPOSED`, nicht
katalogisiert und ungefahren. Der unabhängige Offline-Review ist dokumentiert;
formale T-SQL-/Harness-Abnahme, Ressourcen-/Runtimegates und die formale
Methodenfreigabe bleiben offen.

## Abschluss: QRY-023 – Planerfolg erst nach Cleanup ausgeben

PR #427 wählte die Absicherung der getrennten Actual-Plan-Diagnose. PR #426
integrierte die fünf gepaarten Messmetrikdeltas für CPU, Logical Reads, Reads,
Writes und Elapsed; die 16 synthetischen Regressionen und der QRY-023-
Offlinevalidator bestanden. Diese Werte sind FWK-004-Sessiondeltas
einschließlich Messprozedur-Overhead. Das Manifest bleibt `PROPOSED`, nicht
katalogisiert und ungefahren.

PR #429 integriert die Absicherung der separaten `STATISTICS XML`-Planphase:
Erfolg und `CATCH` schalten die Option ab, `THROW` erhält den Fehler. Eine
gezielte Negativregression weist den fehlenden Fehlerpfad zurück; 17
Harness-Regressionen sowie QRY-023-, Framework- und Repository-Continuity-
Validatoren bestanden. Die Prüfung belegt keine Sessionrücksetzung bei
Verbindungsabbruch und keine Engineausführung. Keine SQL-/Runtimeausführung,
keine Labänderung und keine menschliche Generalprobe. QRY-023 bleibt
`PROPOSED`/nicht katalogisiert; formale Harness-/T-SQL-Abnahme, unabhängige
Methodenfreigabe und konkrete Runtimeautorisierung bleiben offen.

Der Offline-Schnitt ergänzte Negativregressionen und Validatorbindungen
für die beiden Planabfragen: Graph-`MATCH`, relationale Joinfolge, Ergebnisform
und explizite Trennung vom Messlauf müssen mit den bereits geprüften Varianten
übereinstimmen. Die Regressionen verändern jeweils eine Queryeigenschaft und
müssen die Drift erkennen; bestehende Vollpfad- und gepaarte Messoracles bleiben
unverändert. Keine SQL-/Runtime- oder Lab-Ausführung.

PR #431 bindet die beiden `COUNT_BIG`-Planabfragen durch normalisierte
Statementvergleiche an Reihenfolge und Graph-/Relationsformen der Messprozedur.
Zwei gezielte Negativregressionen weisen abweichendes Graph-`MATCH` und einen
veränderten relationalen Zieljoin zurück. 19 QRY-023-Regressionen sowie
QRY-023-, Framework- und Repository-Continuity-Validatoren bestanden. Der
Vergleich prüft Skripttextstruktur, keine tatsächlichen Resultate oder
Enginekompilierung. Keine SQL-/Runtime- oder Lab-Ausführung; QRY-023 bleibt
`PROPOSED` und nicht katalogisiert. Formale T-SQL-Abnahme, unabhängige
Methodenfreigabe und konkrete Runtimeautorisierung bleiben offen.

Der Offline-Schnitt bindet die `PLAN_EVIDENCE`-Erfolgssummary an den
erfolgreichen Abschluss des Diagnoseblocks: beide Abfragen müssen vor dem
erfolgreichen `STATISTICS XML OFF` liegen; `SELECT`-/`PRINT`-PASS-Ausgaben
müssen nach TRY/CATCH stehen. Eine Negativregression verschiebt die
Erfolgsausgabe vor den Abschaltpunkt und muss vom Validator abgelehnt werden.
Der kumulative Rahmen wächst um ein Arbeitspaket, zwei PRs (Auswahl und
Integration) und höchstens zwei Quellenkandidaten auf 76/96/179. Keine
SQL-/Runtime-/Lab-Ausführung; keine Änderung an den Ergebnis- oder Messoracles.

PR #433 integriert die Reihenfolgeprüfung samt Negativregression: genau eine
Plan-Erfolgssummary und ein PASS-Marker müssen nach dem Try-/Catch-Block mit
erfolgreichem Cleanup stehen; ein vorgezogenes Erfolgsfragment wird abgelehnt.
20 QRY-023-Regressionen sowie QRY-023-, Framework- und Repository-Continuity-
Validatoren bestanden. Dies belegt nur die Textreihenfolge, keine Ausführung
oder Sessionwirkung. QRY-023 bleibt `PROPOSED`/nicht katalogisiert; formale
T-SQL-Abnahme, unabhängige Methodenfreigabe und Runtimeautorisierung bleiben
offen.

## Abschluss: QRY-023 – Plan-Summary-Erfolgsfelder binden

Die nächste statische Regression bindet `Phase=PLAN_EVIDENCE`,
`CheckId=SUMMARY`, `Outcome=PASS` und `Code=OK` als gemeinsame Felder der
Summaryzeile sowie den korrespondierenden `SQLPERF_SUMMARY|PASS|OK`-Print.
Ein synthetisch auf `WARN`/Fehler geänderter Outcome muss abgelehnt werden.
Der kumulative Rahmen steigt um ein Arbeitspaket, zwei PRs (Statusauswahl und
Integration) und höchstens zwei Quellenkandidaten auf 77/98/181. Keine Änderung
an SQL-Laufrechten, Korrektheitsoracles oder Performanceaussagen.

PR #435 bindet die gemeinsame Statuszeile an genau `Phase=PLAN_EVIDENCE`,
`CheckId=SUMMARY`, `Outcome=PASS`, `Code=OK` sowie den passenden PASS-Print.
Negativregressionen mit `WARN`-Outcome und fehlerhaftem Code werden abgelehnt.
22 QRY-023-Regressionen sowie QRY-023-, Framework- und Repository-Continuity-
Validatoren bestanden. Die Prüfung bleibt statische Textvalidierung; sie
beweist keine SQL-Ausführung oder Ergebniswahrheit.

## Abschluss: QRY-023 – Diagnoseabfragen ins XML-Aktivierungsfenster binden

Der Offline-Schnitt prüfte, dass beide bereits gebundenen Graph- und
Relationsabfragen innerhalb des `TRY` nach `SET STATISTICS XML ON` und vor dem
Erfolgs-`OFF` liegen. Eine Negativregression verschiebt beide Abfragen aus
diesem Fenster und muss abgelehnt werden. Der kumulative Rahmen steigt um ein
Arbeitspaket, zwei PRs und höchstens zwei Quellenkandidaten auf 78/100/183.
Keine SQL-/Runtime-/Lab-Ausführung und keine Erweiterung der Ergebnisoracles.

PR #437 ergänzt den Positionsvalidator für beide Abfragen innerhalb des
`STATISTICS XML ON/OFF`-Fensters und eine Negativregression, die sie vor
`BEGIN TRY` verschiebt. 23 QRY-023-Regressionen sowie die QRY-023-, Framework-
und Repository-Continuity-Validatoren bestanden. Die Prüfung belegt nur
Skriptpositionen, keine ausgeführten Actual-Pläne. QRY-023 bleibt `PROPOSED`;
T-SQL-/Methoden- und Runtimegates sind unverändert offen.

## Abschluss: QRY-023 – SHOWPLAN-Preflight exakt binden

Der Offline-Schnitt bindet die `SHOWPLAN`-Prüfung an `DB_NAME()` und
die Berechtigung `DATABASE/SHOWPLAN`, verlangt `SELECT` auf allen vier
Querytabellen und prüft, dass der fehlende Rechtefall vor den Diagnoseabfragen
mit `SKIP_PERMISSION` beendet wird. Negativregressionen ändern Scope und
entfernen eine Tabellenberechtigung. Kumulative Obergrenze: ein weiteres
Arbeitspaket, zwei PRs, höchstens zwei Quellenkandidaten, insgesamt 79/102/185.
Keine SQL-/Runtime-/Lab-Ausführung und keine Erweiterung der Laufrechte.

PR #439 bindet den exakten SHOWPLAN-Datenbankscope, alle vier Objekt-
`SELECT`-Rechte und den `SKIP_PERMISSION`-/`RETURN`-Pfad vor der Erfolgsausgabe.
Drei Negativregressionen verwerfen falschen Scope, fehlendes Tabellenrecht und
veränderten Skip-Code. 26 QRY-023-Regressionen sowie die QRY-023-, Framework-
und Repository-Continuity-Validatoren bestanden. Rechte werden nicht erteilt;
es bleibt ein statischer Vertragsnachweis.

## Abschluss: QRY-023 – Qualification-Preflight-Ausgaben binden

Der statische Schnitt band die beiden Qualification-Preflight-
Summaryzeilen an ihre vollständigen Tupel: `QUALIFICATION_PREFLIGHT`/
`PERMISSIONS`/`SKIP`/`SKIP_PERMISSION` und
`QUALIFICATION_PREFLIGHT`/`SUMMARY`/`PASS`/`OK`. Die jeweiligen `PRINT`-Marker
müssen übereinstimmen; je ein falsch geänderter Status ist eine
Negativregression. Die kumulative Obergrenze wuchs um ein Paket und zwei PRs
auf 80/104/187 (höchstens 187 Quellenkandidaten). Keine Ausführung oder
Rechteänderung.

PR #441 bindet die Skip-Zeile an `QUALIFICATION_PREFLIGHT/PERMISSIONS/SKIP/
SKIP_PERMISSION`, die Erfolgssummary an `QUALIFICATION_PREFLIGHT/SUMMARY/PASS/OK`
und beide an ihre jeweiligen `SQLPERF_SUMMARY`-Prints. Drei Negativregressionen
mit verändertem Skip-Outcome, Erfolgs-Outcome und Skip-Print wurden abgewiesen.
29 QRY-023-Regressionen sowie die QRY-023-, Framework- und Repository-
Continuity-Validatoren bestanden. Die Prüfung ist statisch; keine Rechte wurden
erteilt und kein SQL ausgeführt.

## Abschluss: QRY-023 – Preflight an Zielkontext binden

Der Offline-Schnitt band den Zielkontext des Qualification-Preflights:
Systemdatenbanken müssen ausgeschlossen und `DB_NAME()` mit dem manifestierten
`@TargetDatabase` verglichen werden, bevor Berechtigungen ausgewertet werden.
Eine Negativregression kehrt den Vergleich um. Die kumulative Obergrenze stieg
um ein Paket und zwei PRs auf 81/106/189 (höchstens 189 Quellenkandidaten).
Keine Datenbank-, Rechte- oder Runtimeänderung.

PR #443 bindet den Systemdatenbankausschluss und die Prüfung
`DB_NAME()<>@TargetDatabase` vor der Rechteauswertung. Zwei Negativregressionen
entfernen den Ausschluss bzw. kehren den Vergleich um. Der erste lokale Lauf
deckte einen Leerzeichenfehler in der neu ergänzten kompakten Suchbedingung auf;
nach Korrektur bestanden 31 QRY-023-Regressionen sowie QRY-023-, Framework-
und Repository-Continuity-Validatoren. Nur statische Textprüfung; keine DB-
oder Rechteänderung und kein SQL-Lauf.

## Abschluss: QRY-023 – Eigentumsmarker an Harnesswerte binden

Der Offline-Schnitt bindet Zuweisung und exakten Vergleich aller vier
Extended-Property-Marker (`SQLPERF.Project`, `ContractVersion`, `DemoId`,
`RunToken`) an Projektkonstanten bzw. die Harnesswerte, einschließlich
Binär- und Längenvergleich, bevor Rechte ausgewertet werden. Negativproben
verändern den Projektwert und die RunToken-Bindung. Kumulativ erweitert um ein
Paket und zwei PRs auf 82/108/191, höchstens 191 Quellenkandidaten. Keine
Datenbank- oder Rechteänderung.

PR #445 bindet die vier Markerzuweisungen aus `sys.extended_properties` und
ihre vollständigen, längenbewussten Vergleiche vor der Rechteauswertung. Zwei
Negativproben ändern Projektkonstante und RunToken-Gleichheit. 33 QRY-023-
Regressionen sowie QRY-023-, Framework- und Repository-Continuity-Validatoren
bestanden. Die Prüfung attestiert keine tatsächlichen Datenbankmarker und führt
keine Datenbankaktion aus.

## Abschluss: QRY-023 – Zielnamen und RunToken-Format absichern

Der nächste begrenzte Offlineschnitt bindet den im Preflight erwarteten
Datenbanknamen an `DemoId` und `RunToken` sowie die Längen- und
Zeichenmengenprüfung des RunToken an den vorgeschlagenen Harnessvertrag.
Negativregressionen müssen einen abweichenden Zielnamenspräfix, einen
umgekehrten Namensvergleich und eine gelockerte Tokenlänge zurückweisen.
Kumulative Obergrenze: ein weiteres Arbeitspaket, zwei PRs und höchstens zwei
Quellen-/Testkandidaten, insgesamt 83/110/193. PR #447 ergänzt die statische
Bindung der vollständigen Zielnamenformel und der drei RunToken-Guards sowie
drei Negativregressionen für Präfix, Vergleichsrichtung und Maximallänge.
36 QRY-023-Regressionen sowie QRY-023-, Framework- und Repository-Continuity-
Validatoren bestanden. Nur statische Textprüfung; keine SQL-/Runtime-/Lab-
Ausführung, Datenbank- oder Rechteänderung und keine menschliche Generalprobe.

## Abschluss: QRY-023 – Preflight-Guard-Verknüpfungen binden

Die nächste Offline-Regression bindet zusätzlich die boolesche Verknüpfung der
Demo-ID-, RunToken- und Zielnamenbedingungen: Jede ungültige Bedingung muss den
Vertragsfehler allein auslösen können. Eine Gegenprobe ersetzt gezielt ein
`OR` durch `AND`. Kumulative Obergrenze: ein weiteres Arbeitspaket, zwei PRs
und höchstens zwei Quellen-/Testkandidaten, insgesamt 84/112/195. PR #449 bindet
die komplette Guardklausel in Reihenfolge und Operatoren; die gezielte
`AND`-Negativprobe wird abgewiesen. 37 QRY-023-Regressionen und die betroffenen
Validatoren bestanden. Keine SQL-/Runtime-/Lab-Ausführung, Datenbank- oder
Rechteänderung und keine menschliche Generalprobe.

## Abschluss: QRY-023 – RunToken-Byteformat absichern

Microsoft dokumentiert, dass `LEN` nachgestellte Leerzeichen ausschließt und
ASCII-`LIKE` nachgestellte Leerzeichen im Suchwert ignoriert. PR #451 ergänzt im
read-only Preflight eine `DATALENGTH`-Grenze, die für das auf ASCII-Zeichen
beschränkte RunToken 1 bis 20 Bytes verlangt. Eine Negativregression lockert
die Byte-Obergrenze. Kumulative Obergrenze:
ein weiteres Arbeitspaket, zwei PRs und höchstens zwei Quellen-/Testkandidaten,
insgesamt 85/114/197. Die 38 QRY-023-Regressionen sowie die QRY-023-,
Framework- und Repository-Continuity-Validatoren bestanden. Primärquellen:
Microsoft Learn, [`LEN` (Transact-SQL)](https://learn.microsoft.com/en-us/sql/t-sql/functions/len-transact-sql?view=sql-server-ver17) und [`LIKE` (Transact-SQL)](https://learn.microsoft.com/en-us/sql/t-sql/language-elements/like-transact-sql?view=sql-server-ver17), abgerufen am 8. November 2026. Keine SQL-/Runtime-/Lab-Ausführung, Datenbank- oder Rechteänderung und keine menschliche Generalprobe.

## Abschluss: QRY-023 – SQLCMD-Eingabevertrag vor Ausführung klären

Die Manifest-Skripte verwenden SQLCMD-Variablen innerhalb von T-SQL-
Zeichenliteralen. Microsoft dokumentiert die Einsetzung von SQLCMD-
Skriptvariablen an ihren `$(Name)`-Vorkommen. Daraus folgt als
Sicherheitsinferenz: Eine T-SQL-Prüfung kann bösartige Werte nicht zuverlässig
abweisen, wenn sie bereits vor dem Parsen die SQL-Struktur verändert haben.
Der nächste Dokumentationsschnitt stellt klar, dass ein künftiger Aufrufer
Demo-ID, RunToken und Zielnamen vor SQLCMD anhand des Vertrags allowlisten
muss. Die Preflight-Prüfung gilt nicht als Schutz gegen SQLCMD-Eingabeinjektion.
Kumulative Obergrenze: ein Arbeitspaket, zwei PRs und höchstens zwei
Quellen-/Testkandidaten zusätzlich, insgesamt 86/116/199. Quelle:
Microsoft Learn, [Use sqlcmd with scripting variables](https://learn.microsoft.com/en-us/sql/tools/sqlcmd/sqlcmd-use-scripting-variables?view=sql-server-ver15), abgerufen am 8. November 2026. Kein Aufrufer wird implementiert oder ausgeführt; keine menschliche Generalprobe.
PR #452 dokumentiert die Caller-seitige Allowlist vor SQLCMD und bindet den
offenen Schutzstatus in README, Review und Offlinevalidator. Eine
Negativregression entfernt die Eingabegrenzen-Formulierung. 39 QRY-023-
Regressionen und die betroffenen Projektvalidatoren bestanden. Die SQLCMD-
Injektionseinschätzung ist eine Inferenz aus der dokumentierten Variablen-
Expansion; der vorhandene FWK-010-Caller erzwingt den Vertrag jetzt, aber
QRY-023 ist weiterhin nicht katalogisiert und wurde nicht ausgeführt.

## Abschluss: QRY-023 – SQLCMD-Eingabeanforderungen maschinenlesbar binden

Der nächste Offline-Schnitt ergänzt im vorgeschlagenen Manifest ein exaktes,
maschinenlesbares Caller-Vertragsobjekt: Demo-ID, RunToken-Zeichensatz und
Längenlimit, deterministische Zielnamenschablone sowie die Pflicht, vor dem
Start von SQLCMD zu validieren. Der Validator bindet das Objekt vollständig und
weist Abweichungen zurück. Kumulative Obergrenze: ein Arbeitspaket, zwei PRs
und höchstens zwei Quellen-/Testkandidaten zusätzlich, insgesamt 87/118/201.
PR #455 ergänzt `sqlcmd_input_validation` und zwei Negativregressionen für den
Prüfzeitpunkt und den RunToken-Zeichensatz. 41 QRY-023-Regressionen und die
betroffenen statischen Validatoren bestanden. Das Manifest ist eine
Anforderungsspezifikation; es führt keinen Aufrufer aus. Keine Runtime- oder
menschliche Generalprobe.

## Abschluss: QRY-023 – Manifestvertrag im Laufzeitcaller durchsetzen

Der nächste begrenzte Schnitt erweitert `run_demo.py`, damit der vorhandene
FWK-010-Caller ein vorhandenes `sqlcmd_input_validation`-Objekt bereits beim
Manifestladen vollständig prüft und bei Abweichungen vor `resolve_sqlcmd` und
vor jeder Prozessausführung abbricht. PR #457 integriert diese Prüfung und
synthetische Tests bestätigen den QRY-023-Manifestpfad sowie die Ablehnung eines
veränderten Vertrags und eines SQL-Injection-ähnlichen RunTokens, jeweils vor
SQLCMD-Auflösung/-Start. Kumulative Obergrenze: 88/120/203. Der Runner wurde
nicht gegen SQL Server ausgeführt; keine Datenbank- oder menschliche
Generalprobe. Zwei unabhängige DGN-007-Quellenprofilworkflows meldeten
`PYTHON_PROFILE_CHANGED`; die betroffenen DGN-Dateien gehören nicht zum
PR-Diff. QRY-023-/FWK-010- und Runtime-Matrixchecks waren erfolgreich.

## Fortsetzung: QRY-023 – RunToken-Vertrag an FWK-010 angleichen

Das maschinenlesbare `sqlcmd_input_validation` erlaubte als erstes Tokenzeichen
auch `_`, während der bestehende allgemeine FWK-010-Validator nur `A-Z` oder
`0-9` am Anfang akzeptiert. Der nächste Offline-Schnitt macht diese
Einschränkung im Vertragsobjekt und in den Lesepfaden explizit; ein synthetischer
Caller-Test weist `_LOCAL` vor SQLCMD-Auflösung und -Start zurück. Keine
Änderung an der wirksamen Tokenakzeptanz, keine SQL-Ausführung und keine
menschliche Generalprobe. Kumulative Obergrenze für Auswahl und Integration:
89 Arbeitspakete, 122 PRs und 204 Quellen-/Testkandidaten.

PR #458 integriert die Caller-Vertragsangleichung. Die vollständige, breit
ausgelöste CI ist inzwischen abgeschlossen: 20 von 22 Workflows waren
erfolgreich; zwei unabhängige DGN-007-Quellenprofilchecks scheiterten mit
`PYTHON_PROFILE_CHANGED`. Die DGN-Dateien waren nicht Teil des PR-Diffs; alle
übrigen Framework- und Runtimeläufe, einschließlich SQL Server 2025 AI, sind
beendet und bestanden.

## Fortsetzung: QRY-023 – RunToken-Negativregression ausführen

Ein Nachreview ergab, dass die `_LOCAL`-Regression zwar definiert, aber nicht
im `main()`-Ablauf des statischen Runner-Tests registriert war. Der zuvor
gemeldete grüne Testlauf hat diesen konkreten Fall daher nicht ausgeführt. PR
#459 hängt den Test explizit ein; der erneute Modultest und die fünf ausgelösten
Workflows bestanden. Der tatsächliche synthetische Lauf bestätigt den
Frühabbruch vor SQLCMD-Auflösung/-Start. Kumulative Obergrenze:
90 Arbeitspakete, 124 PRs und 205 Quellen-/Testkandidaten. Die vorherige
Zählung bezeichnete die Regression als Kandidat; PR #459 belegt ihre Ausführung.

## Fortsetzung: QRY-023 – RunToken-Grenzen im Caller abdecken

PR #460 ergänzt die ausgeführten synthetischen Caller-Grenzen: gültige
1-/20-Zeichenwerte werden geladen; leere, überlange, nicht-ASCII-,
kleingeschriebene und nachgestellte-Leerzeichen-Token scheitern vor SQLCMD-
Auflösung/-Start. Die QRY-023-, FWK-010- und Repository-Continuity-Prüfungen
bestanden; keine Engine- oder Runtimeausführung. Kumulative Obergrenze:
91 Arbeitspakete, 126 PRs und 206 Quellen-/Testkandidaten.

## Fortsetzung: QRY-023 – RunToken im Offlinevalidator binden

PR #461 bindet den konkreten `run_token`-Wert gegen den FWK-010-Zeichensatz und
die Längengrenze; vier Negativregressionen für führenden Unterstrich, Überlänge,
Nicht-ASCII und nachgestelltes Leerzeichen sowie die betroffenen Workflows
bestanden. Kumulative Obergrenze: 92 Arbeitspakete, 128 PRs und 207 Quellen-/
Testkandidaten. Keine Engine- oder Runtimeausführung.

## Fortsetzung: QRY-023 – Vertragsobjekt fail-closed prüfen

PR #462 ergänzt die Caller-Negativregressionen für unbekannte Zusatzfelder und
`true` im numerischen Byte-Limit. Beide scheitern wie ein veränderter
Validierungszeitpunkt vor SQLCMD-Auflösung/-Start; die betroffenen Workflows
bestanden. Kumulative Obergrenze: 93 Arbeitspakete, 130 PRs und 208 Quellen-/
Testkandidaten. Keine Vertragsausweitung oder Runtimeausführung.

## Fortsetzung: QRY-023 – Callerbindungen für Demo-ID und Zielvorlage

PR #463 ergänzt Gegenproben für abweichende Vertrags-Demo-ID und
Zielnamenschablone; beide werden vor SQLCMD-Auflösung/-Start abgewiesen. Alle
fünf Workflows bestanden. Kumulative Obergrenze: 94 Arbeitspakete, 132 PRs und
209 Quellen-/Testkandidaten. Keine Runtimeausführung.

## Fortsetzung: FWK-010 – QRY-023-Vertrag auf Demo-ID begrenzen

PR #464 legt den exakten QRY-023-Vertrag in ein `OPT-001`-Manifest und bestätigt
die Ablehnung vor SQLCMD-Auflösung/-Start. Die fünf betroffenen Workflows
bestanden. Kumulative Obergrenze: 95 Arbeitspakete, 134 PRs und 210 Quellen-/
Testkandidaten. Keine Runtimeausführung.

## Fortsetzung: QRY-023 – Caller- und SQL-Preflight-Grenze dokumentieren

PR #465 ordnet die alphanumerische Startzeichenregel dem FWK-010-Caller zu und
trennt davon ASCII-Zeichensatz und Bytegrenze des SQL-Preflights. Eine statische
Negativregression schützt die Zuordnung; 43 QRY-023-Tests und alle sieben
ausgelösten Workflows bestanden. Kumulative Obergrenze: 96 Arbeitspakete, 136
PRs und 211 Quellen-/Testkandidaten. Keine SQL- oder Runtimeausführung.

## Fortsetzung: FWK-010 – Demo-ID-Feld des QRY-023-Vertrags durchsetzen

PR #466 ergänzt den synthetischen Caller-Test mit `OPT-001`-Manifest und exakt
deklariertem QRY-023-Vertrag. FWK-010 weist den Scope-Konflikt vor SQLCMD-
Auflösung/-Start zurück; alle fünf Workflows bestanden. Kumulative Obergrenze:
97 Arbeitspakete, 138 PRs und 212 Quellen-/Testkandidaten. Keine Runtime-
Ausführung.

## Fortsetzung: FWK-010 – Nicht-Objekt-Vertrag fail-closed ablehnen

PR #467 prüft eine Liste statt des `sqlcmd_input_validation`-Objekts; die
Zurückweisung vor SQLCMD-Auflösung/-Start sowie die vorhandenen Manipulations-
gegenproben bestanden. Alle fünf Workflows waren grün. Kumulative Obergrenze:
98 Arbeitspakete, 140 PRs und 213 Quellen-/Testkandidaten. Keine Runtime-
Ausführung.

## Fortsetzung: FWK-010 – Callerbindung des Zielnamens prüfen

PR #468 entfernt die doppelte Definition/Registrierung des `OPT-001`-Scope-Tests
und ergänzt die synthetische Zielnamendriftprobe: ein abweichender Wert von
`target_database_name()` wird vor SQLCMD-Auflösung/-Start zurückgewiesen. Die
Runner-, QRY-023- und Continuity-Tests sowie alle fünf Workflows bestanden.
Kumulative Obergrenze: 99 Arbeitspakete, 142 PRs und 214 Quellen-/Testkandidaten.

## Fortsetzung: FWK-010 – Runner-Testregistrierung automatisch prüfen

PR #469 vergleicht die AST-definierten `test_*`-Funktionen mit den Aufrufen in
`main()` und verlangt eine eindeutige Eins-zu-eins-Registrierung. Der erneute
Runner-Test sowie alle fünf Workflows bestanden. Kumulative Obergrenze:
100 Arbeitspakete, 144 PRs und 215 Quellen-/Testkandidaten.

## Fortsetzung: FWK-010 – Testregistrierungswächter synthetisch prüfen

PR #470 führt den Wächter gegen synthetische Module mit korrekter, fehlender und
doppelter Testregistrierung sowie doppelter Funktionsdefinition aus. Der reale
Runner-Test und alle fünf Workflows bestanden. Kumulative Obergrenze:
101 Arbeitspakete, 146 PRs und 216 Quellen-/Testkandidaten.

## Fortsetzung: FWK-010 – Testeinstieg im AST-Wächter prüfen

PR #471 ergänzt synthetische Fälle mit fehlendem und doppeltem `main()` sowie
einem Aufruf eines nicht definierten `test_*`-Namens; alle Fälle werden vom
Registrierungswächter erkannt. Der Runner-Test und alle fünf Workflows
bestanden. Kumulative Obergrenze: 102 Arbeitspakete, 148 PRs und 217 Quellen-/
Testkandidaten.

## Fortsetzung: FWK-010 – AST-Registrierung auf ausführbaren Hauptpfad begrenzen

PR #472 zählt nur Aufrufe im `main()`-Funktionskörper; verschachtelte
Funktionen und Lambdas gelten nicht als Registrierung. Eine synthetische
Hilfsfunktion wird als nicht registriert erkannt. Der Runner-Test und alle
fünf Workflows bestanden. Kumulative Obergrenze: 103 Arbeitspakete, 150 PRs
und 218 Quellen-/Testkandidaten.

## Fortsetzung: FWK-010 – Testaufrufe an unbedingten Stellen verlangen

PR #473 beschränkt Registrierungen auf direkte, unbedingte Ausdrucksaufrufe im
`main()`-Ablauf und in `with`-Blöcken. Gegenproben mit `if False` und
verschachtelten Hilfsfunktionen bestehen als fehlende Registrierung. Der
Runner-Test und alle fünf Workflows bestanden. Kumulative Obergrenze:
104 Arbeitspakete, 152 PRs und 219 Quellen-/Testkandidaten.

## Fortsetzung: FWK-010 – Asynchrone Testdefinitionen fail-closed behandeln

PR #474 nimmt nur synchrone `test_*`-Definitionen in den Registrierungssatz auf;
eine asynchrone Definition mit gewöhnlichem, nicht-awaited Aufruf gilt nicht
als ausgeführt. Alle fünf ausgelösten Workflows bestanden. Die kumulative
Obergrenze von 105 Arbeitspaketen, 154 PRs und 220 Quellen-/Testkandidaten ist
erreicht.

Für den unmittelbar folgenden Schattenfall gilt eine begrenzte Erweiterung um
ein Arbeitspaket, einen PR und einen synthetischen Testkandidaten auf höchstens
106/155/221, ohne Reset. Eine gleichnamige synchrone und asynchrone
Top-Leveldefinition muss als doppelte Definition abgewiesen werden, weil die
spätere Coroutine den aufrufbaren Namen überschreibt. Keine SQL-/Runtime-
Ausführung oder menschliche Generalprobe.

PR #475 integriert diese Duplikatprüfung; alle fünf ausgelösten Workflows
bestanden. Für den ebenso eng abgegrenzten Einstiegspunkt-Schattenfall wird der
kumulative Rahmen einmalig um ein Paket, einen PR und einen synthetischen
Kandidaten auf höchstens 107/156/222 erweitert. Eine asynchrone `main()` darf
eine synchrone `main()` nicht überschreiben und dabei die eindeutige
Runner-Einstiegsprüfung passieren. Keine SQL-/Runtimeausführung oder
menschliche Generalprobe.

PR #476 integriert die Prüfung; alle fünf Workflows bestanden. Für den nächsten
kleinen Kandidaten erweitert sich der kumulative Rahmen ohne Reset um ein
Arbeitspaket, einen PR und einen Testkandidaten auf höchstens 108/157/223. Der
AST-Wächter muss den tatsächlichen `if __name__ == "__main__"`-Einstieg mit
`raise SystemExit(main())` verlangen. Eine bloße `main()`-Definition und intern
vollständige Testregistrierung startet den Testlauf noch nicht. Keine
SQL-/Runtimeausführung oder menschliche Generalprobe.

PR #477 integriert diese Einstiegsprüfung; alle fünf Workflows bestanden.
Für drei synthetische Fehlformen wird das kumulative Budget ohne Reset um ein
Arbeitspaket, einen PR und drei Testkandidaten auf höchstens 109/158/226
erweitert. Umgedrehte Guard-Bedingung, fehlende Exitcode-Weitergabe und ein
Funktionsverweis ohne Aufruf müssen fail-closed scheitern. Keine SQL-/Runtime-
Ausführung oder menschliche Generalprobe.

PR #478 integriert diese drei Fehlformen; alle fünf Workflows bestanden. Für
die Erkennung eines zusätzlichen ungeschützten Modulebenenaufrufs von `main()`
erweitert sich der kumulative Rahmen ohne Reset um ein Arbeitspaket, einen PR
und einen Testkandidaten auf höchstens 110/159/227. Doppelte Ausführung beim
Import oder vor dem geschützten Einstieg muss abgewiesen werden. Keine
SQL-/Runtimeausführung oder menschliche Generalprobe.

PR #479 integriert den Schutz vor ungeschützten `main()`-Aufrufen; alle fünf
Workflows bestanden. Für einen zweiten Aufruf innerhalb desselben
`__main__`-Guards erweitert sich der kumulative Rahmen ohne Reset um ein Paket,
einen PR und einen Testkandidaten auf höchstens 111/160/228. Der Modulstartpfad
muss genau einen `main()`-Aufruf enthalten. Keine SQL-/Runtimeausführung oder
menschliche Generalprobe.

PR #480 integriert die Einzelaufrufprüfung; alle fünf Workflows bestanden. Für
Importzeitaufrufe in Klassenbasen, Funktionsstandardwerten und Dekoratoren
erweitert sich das kumulative Budget ohne Reset um ein Arbeitspaket, einen PR
und bis zu drei Testkandidaten auf höchstens 112/161/231. Diese Ausdrücke werden
vor dem `__main__`-Guard ausgewertet und müssen als ungeschützte Aufrufe
abgewiesen werden. Keine SQL-/Runtimeausführung oder menschliche Generalprobe.

PR #481 integriert die drei Importzeitfälle; alle fünf Workflows bestanden.
Für eine Aliasreferenz wie `runner = main` erweitert sich das kumulative Budget
ohne Reset um ein Arbeitspaket, einen PR und einen Testkandidaten auf höchstens
113/162/232. Nicht geschützte Ladezugriffe auf `main` dürfen einen indirekten
Moduleinstieg nicht am Wächter vorbeiführen. Keine SQL-/Runtimeausführung oder
menschliche Generalprobe.

PR #482 integriert die Aliasgegenprobe; alle fünf Workflows bestanden. Für
zwei dynamische globale Aufrufformen wird das kumulative Budget ohne Reset um
ein Paket, einen PR und zwei Testkandidaten auf höchstens 114/163/234 erweitert.
`globals()["main"]()` und `getattr(globals(), "main")()` müssen außerhalb des
Guards als Moduleinstieg abgewiesen werden. Keine SQL-/Runtimeausführung oder
menschliche Generalprobe.

PR #483 integriert beide globalen Formen; alle fünf Workflows bestanden. Für
die entsprechenden `locals()`- und `vars()`-Mappingaufrufe erweitert sich der
kumulative Rahmen ohne Reset um ein Paket, einen PR und zwei Testkandidaten auf
höchstens 115/164/236. Auch diese direkten Mappingzugriffe auf `main` werden
außerhalb des Guards zurückgewiesen. Keine SQL-/Runtimeausführung oder
menschliche Generalprobe.

PR #484 integriert die lokalen Mappingformen; alle fünf Workflows bestanden.
Für unerreichbare Testaufrufe nach `return` und `raise` erweitert sich der
kumulative Rahmen ohne Reset um ein Paket, einen PR und zwei Testkandidaten auf
höchstens 116/165/238. Nach einem unbedingten Kontrollflussende werden spätere
Aufrufe nicht als Registrierungen gezählt. Keine SQL-/Runtimeausführung oder
menschliche Generalprobe.

PR #485 integriert die Unerreichbarkeitsprüfung für `return` und `raise`; alle
fünf Workflows bestanden. Für vier direkte Prozessendeformen erweitert sich der
kumulative Rahmen ohne Reset um ein Paket, einen PR und vier Testkandidaten auf
höchstens 117/166/242. Nach `exit()`, `quit()`, `sys.exit()` und `os._exit()`
liegende Testaufrufe gelten ebenfalls als unerreichbar. Keine SQL-/Runtime-
Ausführung oder menschliche Generalprobe.

PR #486 integriert die vier direkten Prozessendeformen; alle fünf Workflows
bestanden. Für zwei über Modul- oder Importalias erkannte `sys.exit`-Varianten
erweitert sich das kumulative Budget ohne Reset um ein Paket, einen PR und zwei
Testkandidaten auf höchstens 118/167/244. `from sys import exit as stop` und
`import sys as runtime` dürfen spätere Tests nicht ausführbar erscheinen
lassen. Keine SQL-/Runtimeausführung oder menschliche Generalprobe.

PR #487 integriert die zwei `sys.exit`-Aliasformen; alle fünf Workflows
bestanden. Für drei importierte `builtins.exit`-/`os._exit`-Varianten erweitert
sich der kumulative Rahmen ohne Reset um ein Arbeitspaket, einen PR und drei
Testkandidaten auf höchstens 119/168/247. Die Aliasauflösung muss auch für
Builtin- und OS-Endpunkte gelten. Keine SQL-/Runtimeausführung oder menschliche
Generalprobe.

PR #488 integriert die drei Aliasfälle für Builtin und OS; alle fünf Workflows
bestanden. Für einen Prozessendeaufruf als einfache Zuweisung erweitert sich
der kumulative Rahmen ohne Reset um ein Arbeitspaket, einen PR und einen
Testkandidaten auf höchstens 120/169/248. Auch `result = sys.exit()` muss
nachfolgende Testaufrufe als unerreichbar behandeln. Keine SQL-/Runtime-
Ausführung oder menschliche Generalprobe.

PR #489 integriert den Prozessendeaufruf in einfacher Zuweisung; alle fünf
Workflows bestanden. Für eine erweiterte Zuweisung wird das kumulative Budget
ohne Reset um ein Arbeitspaket, einen PR und einen Testkandidaten auf höchstens
121/170/249 erweitert. `status += sys.exit()` muss spätere Tests ebenfalls als
unerreichbar markieren. Keine SQL-/Runtimeausführung oder menschliche
Generalprobe.

PR #490 integriert die erweiterte Zuweisungsform; alle fünf Workflows
bestanden. Für die explizite Gegenprobe einer annotierten Zuweisung erweitert
sich der kumulative Rahmen ohne Reset um ein Paket, einen PR und einen
Testkandidaten auf höchstens 122/171/250. `result: int = sys.exit()` muss
nachfolgende Testaufrufe ebenfalls unerreichbar machen. Keine SQL-/Runtime-
Ausführung oder menschliche Generalprobe.

PR #491 integriert die annotierte Zuweisungsgegenprobe; alle fünf Workflows
bestanden. Für eager ausgewertete Tupel-, Listen- und Dictionary-Literale als
Zuweisungswert erweitert sich der kumulative Rahmen ohne Reset um ein Paket,
einen PR und drei Testkandidaten auf höchstens 123/172/253. Darin liegende
Prozessendeaufrufe dürfen nachfolgende Tests nicht erreichbar erscheinen
lassen. Keine SQL-/Runtimeausführung oder menschliche Generalprobe.

PR #492 integriert die drei Literalformen; alle fünf Workflows bestanden. Für
eine bedingte Exit-Auswertung in einem Zuweisungswert erweitert sich der
kumulative Rahmen ohne Reset um ein Paket, einen PR und einen Testkandidaten
auf höchstens 124/173/254. `result = sys.exit() if condition else 0` darf einen
folgenden Test nicht als unbedingt registriert bestehen lassen. Keine
SQL-/Runtimeausführung oder menschliche Generalprobe.

PR #493 integriert die bedingte Zuweisungsgegenprobe; alle fünf Workflows
bestanden. Für einen Exit in einer `if`-Verzweigung erweitert sich der
kumulative Rahmen ohne Reset um ein Arbeitspaket, einen PR und einen
Testkandidaten auf höchstens 125/174/255. Ein späterer Test nach einer
`if`-Verzweigung mit `sys.exit()` ist nicht auf allen Kontrollflusspfaden
ausführbar und muss abgewiesen werden. Keine SQL-/Runtimeausführung oder
menschliche Generalprobe.

PR #494 integriert die `if`-Gegenprobe; alle fünf Workflows bestanden. Für
Prozessende in Schleifen, `try`/`except`, `match` und `with` erweitert sich das
kumulative Budget ohne Reset um ein Arbeitspaket, einen PR und fünf
Testkandidaten auf höchstens 126/175/260. Kein Test darf trotz möglichem
Abbruchpfad in einem solchen Kontrollflussblock als unbedingt registriert
gelten. Keine SQL-/Runtimeausführung oder menschliche Generalprobe.

PR #495 integriert die fünf Kontrollflussfälle; alle fünf Workflows bestanden.
Für die Abgrenzung nicht aufgerufener Hilfsfunktionskörper erweitert sich das
kumulative Budget ohne Reset um ein Paket, einen PR und einen Testkandidaten
auf höchstens 127/176/261. Ein lediglich definierter Helper mit `sys.exit()`
beendet den äußeren `main()`-Pfad nicht. Keine SQL-/Runtimeausführung oder
menschliche Generalprobe.

PR #496 integriert diese Abgrenzung; alle fünf Workflows bestanden. Für
ausgewertete Dekoratoren und Standardwerte verschachtelter Helper erweitert
sich der kumulative Rahmen ohne Reset um ein Paket, einen PR und zwei
Testkandidaten auf höchstens 128/177/263. `@sys.exit()` und
`value=sys.exit()` beenden die Helperdefinition und damit den äußeren Testlauf.
Keine SQL-/Runtimeausführung oder menschliche Generalprobe.

PR #497 integriert diese Helper-Headerfälle; alle fünf Workflows bestanden.
Für Prozessenden im Klassenkörper und im unaufgerufenen Methodenrumpf erweitert
sich der kumulative Rahmen ohne Reset um ein Paket, einen PR und zwei
Testkandidaten auf höchstens 130/179/265. Ein Klassenkörper läuft beim
Definieren, ein Methodenrumpf erst beim Aufruf. Keine SQL-/Runtimeausführung
oder menschliche Generalprobe.

PR #498 integriert diese Klassengrenze; alle fünf Workflows bestanden. Für
Generatorausdrücke erweitert sich der kumulative Rahmen ohne Reset um ein
Arbeitspaket, einen PR und zwei Testkandidaten auf höchstens 132/181/267. Der
Generatorrumpf wird erst beim Iterieren ausgeführt, sein äußerstes Iterable
bereits beim Erzeugen ausgewertet. Keine SQL-/Runtimeausführung oder
menschliche Generalprobe.

PR #499 integriert die Generator-Auswertungsgrenze; alle fünf Workflows
bestanden. Für Generatoren, die ein unmittelbarer Eager-Verbraucher iteriert,
erweitert sich der kumulative Rahmen ohne Reset um ein Arbeitspaket, einen PR
und zwei Testkandidaten auf höchstens 134/183/270. `list`, `tuple`, `set`,
`sorted`, `sum`, `min`, `max`, `any` und `all` werten den Generatorrumpf aus.
Keine SQL-/Runtimeausführung oder menschliche Generalprobe.

PR #500 integriert den direkten Eager-Verbrauch von Generatorausdrücken; alle
fünf Workflows bestanden. Für aufgerufene `map`-/`filter`-Callbacks erweitert
sich der kumulative Rahmen ohne Reset um ein Arbeitspaket, einen PR und zwei
Testkandidaten auf höchstens 136/185/273. Die Gegenproben trennen einen
iterierten Lambda-Callback von einem noch unaufgerufenen `map`-Callback. Keine
SQL-/Runtimeausführung oder menschliche Generalprobe.

PR #501 integriert die Lambda-Callback-Auswertung; alle fünf Workflows
bestanden. Für benannte synchrone `map`-/`filter`-Callbacks erweitert sich der
kumulative Rahmen ohne Reset um ein Arbeitspaket, einen PR und zwei
Testkandidaten auf höchstens 138/187/276. Die Gegenproben trennen den
aufgerufenen Funktionsrumpf von einem lazy Iterator. Keine SQL-/Runtime-
ausführung oder menschliche Generalprobe.

PR #502 integriert benannte synchrone Callbacks; alle fünf Workflows bestanden.
Für Generatorausdrücke direkt in `for`-/`async for`-Iteratoren erweitert sich
der kumulative Rahmen ohne Reset um ein Arbeitspaket, einen PR und zwei
Testkandidaten auf höchstens 140/189/279. Die Schleife konsumiert den
Generatorrumpf. Keine SQL-/Runtimeausführung oder menschliche Generalprobe.

PR #503 integriert die Loop-Konsumierung; alle fünf Workflows bestanden. Für
Generatorfunktionen als `main` erweitert sich der kumulative Rahmen ohne Reset
um ein Arbeitspaket, einen PR und drei Testkandidaten auf höchstens 143/192/283.
Ein direktes `yield` oder eines in einem ausgewerteten Helper-Header macht
`main()` lazy; ein verschachtelter Helper-Rumpf nicht. Keine SQL-/Runtime-
ausführung oder menschliche Generalprobe.

PR #504 integriert die Prüfung von Generatorfunktionen als `main`; alle fünf
Workflows bestanden. Für die eigenständige `yield from`-Gegenprobe erweitert
sich der kumulative Rahmen ohne Reset um ein Arbeitspaket, einen PR und einen
Testkandidaten auf höchstens 144/193/285. `yield from` markiert `main` ebenso
als Generatorfunktion. Keine SQL-/Runtimeausführung oder menschliche
Generalprobe.

PR #505 integriert die `yield from`-Gegenprobe; alle fünf Workflows bestanden.
Für Prozessenden beim Modulstart erweitert sich der kumulative Rahmen ohne
Reset um ein Arbeitspaket, einen PR und zwei Testkandidaten auf höchstens
146/195/288. Direkte Importzeit-Ausführung und ein unaufgerufener Helper-Rumpf
bleiben getrennt. Keine SQL-/Runtimeausführung oder menschliche Generalprobe.

## Abschluss: STL-001 – Zeilenbreitenleiter
PR #506 integriert Prozessenden beim Modulstart; alle fünf Workflows bestanden.
Für Imports von Exit-Aliasen in `main()` erweitert sich der kumulative Rahmen
ohne Reset um ein Arbeitspaket, einen PR und zwei Testkandidaten auf höchstens
148/197/291. Lokale `sys.exit`- und `sys`-Modul-Aliase werden im Ablauf erkannt.
Keine SQL-/Runtimeausführung oder menschliche Generalprobe.

PR #507 integriert direkte lokale Exit-Imports; alle fünf Workflows bestanden.
Für Exit-Imports in bedingten `main()`-Blöcken erweitert sich der kumulative
Rahmen ohne Reset um ein Arbeitspaket, einen PR und zwei Testkandidaten auf
höchstens 150/199/294. Mögliche Zweigimporte werden erkannt, Importe in
unaufgerufenen Helpern bleiben ausgeklammert. Keine SQL-/Runtimeausführung oder
menschliche Generalprobe.

PR #508 integriert bedingte Exit-Imports; alle fünf Workflows bestanden. Für
die Abgrenzung relativer `.sys`-Imports erweitert sich der kumulative Rahmen
ohne Reset um ein Arbeitspaket, einen PR und zwei Testkandidaten auf höchstens
152/201/297. Nur absolute Imports binden das Standardmodul `sys`. Keine
SQL-/Runtimeausführung oder menschliche Generalprobe.

PR #509 integriert die Abgrenzung relativer Imports; alle fünf Workflows
bestanden. Für lokale Namensüberschreibungen von Exit-Aliasen erweitert sich
der kumulative Rahmen ohne Reset um ein Arbeitspaket, einen PR und zwei
Testkandidaten auf höchstens 154/203/300. Zuweisungen und lokale Definitionen
überschreiben erkannte Import-Aliase. Keine SQL-/Runtimeausführung oder
menschliche Generalprobe.

## Abschluss: STL-001 – Zeilenbreitenleiter

Der [STL-001-Entwurf](STL001_ROW_WIDTH_LADDER_DESIGN.md) ist über PR #416
integriert. Er legt die vollständigen Spalten- und Ergebnistupel für alle vier
Profile sowie exakte Längenverteilungen fest. Die Modellwerte bleiben von
tatsächlichen Record-/Seitenmessungen getrennt; keine Heap-Enginequalifikation
ist erfolgt.

## Abschluss: IDX-002 – Clustered-Key-Breite

Der [IDX-002-Entwurf](IDX002_CLUSTERED_KEY_WIDTH_DESIGN.md) ist über PR #414
integriert. Er definiert alle 100.000 synthetischen Zeilentupel, 100 nicht
eindeutige Clustered-Key-Werte mit je 1.000 Zeilen und das vollständige
FilterBand-37-Oracle. Modellierte Größen, reale Seitenmessungen und
Performancewirkungen bleiben getrennte Evidenzen; keine Enginequalifikation
ist erfolgt.

## Abschluss: IDX-001 – Heap- und Clustered-Row-Locators

Der [IDX-001-Entwurf](IDX001_ROW_LOCATORS_DESIGN.md) ist über PR #412
integriert. Er definiert alle 100.000 synthetischen Tupel, die exakte
Payloadformel und vollständige Punkt-/Bereichsoracles für beide Profile. Die
kanonische Sortierung dient ausschließlich dem mengengleichen Vergleich.
Enginequalifikation, tatsächliche Lookup-Pläne und jede Laufzeitwirkung bleiben
offen.

## Abschluss: IDX-004 – Treffermenge, Lookup und Abdeckung

Der [IDX-004-Entwurf](IDX004_LOOKUP_SELECTIVITY_DESIGN.md) ist über PR #410
integriert. Generatorformel und Slotintervalle definieren eine Bijektion über
100.000 RowIds; vollständige sortierte Ergebnistupeloracles für alle Bänder
vergleichen BASE, LOOKUP und COVERING. Die kanonische Sortierung gilt nur für
den mengenweisen Vergleich, nicht als Abfragereihenfolge. Enginequalifikation,
tatsächlicher Plan-/Lookup-/Read-Befund und jede Laufzeitwirkung bleiben offen.

## Abschluss: IDX-003 – Schlüsselreihenfolge und INCLUDE-Spalten

Der [IDX-003-Entwurf](IDX003_KEY_ORDER_DESIGN.md) ist über PR #408 integriert.
Enginequalifikation, tatsächliche Zugriffspfade, Indexseiten, Berechtigungen
und Laufzeitwirkungen bleiben offen.

## Abschluss: QRY-007 – Join-Kardinalität und Ergebniskörnung

Der [QRY-007-Entwurf](QRY007_JOIN_CARDINALITY_DESIGN.md) ist über PR #406
integriert. SQL-/Enginequalifikation, Demo-/Cleanupvertrag sowie jede
konkrete Plan- oder Laufzeitwirkung bleiben offen.

## Abschluss: QRY-003 – Datumsintervalle an der Mitternachtsgrenze

Der [QRY-003-Entwurf](QRY003_DATE_INTERVAL_DESIGN.md) ist über PR #405
integriert. Engine-Rundung, T-SQL-Fixture, Buildqualifikation und jede
Plan-/Laufzeitwirkung bleiben offen.

## Abschluss: STL-010 – Datenkompression: Schätzung und Ergebnis trennen

Der [STL-010-Entwurf](STL010_DATA_COMPRESSION_ESTIMATE_DESIGN.md) ist über
PR #403 integriert. Schätzabweichung, Editions-/Buildmatrix, TempDB-Verbrauch,
Rechte, tatsächliche Seitenwerte und jede Laufzeitwirkung bleiben offen.

## Abschluss: OPT-012 – Adaptive Join unter wechselnder Eingabekardinalität

Der [OPT-012-Entwurf](OPT012_ADAPTIVE_JOIN_DESIGN.md) ist über PR #402
integriert. SQL-/Planqualifikation, genaue Zielbuilds, Rechte und jede
Runtime- oder Leistungswirkung bleiben offen.

## Abschluss: IDX-005 – Missing-Index-Vorschläge fachlich bewerten

Der [IDX-005-Entwurf](IDX005_MISSING_INDEX_REVIEW_DESIGN.md) ist über PR #401
integriert. Tatsächliche Vorschläge, DMV-Rechte und DML-/Planlaufzeiten bleiben
für eine spätere qualifizierte Runtimephase offen.

## Abschluss: QRY-011 – Filtered Indexes und berechnete Indexspalte

Der [QRY-011-Entwurf](QRY011_FILTERED_INDEX_PREDICATE_DESIGN.md) ist über
PR #400 integriert. Die tatsächliche Indexwahl, Enginekompilierung,
Build-/Rechtequalifikation und Leistungswirkungen bleiben offen.

## Abschluss: STL-003 – Lebenszyklus weitergeleiteter Heapzeilen

Der [STL-003-Entwurf](STL003_FORWARDED_RECORD_LIFECYCLE_DESIGN.md) ist über
PR #399 integriert. Fixtureausführung und Enginequalifikation, tatsächliche
Fetch-Deltas, Rechte, Build sowie Laufzeit- und Leistungswirkungen bleiben
offen.

## Fortsetzung: STL-003 – Lebenszyklus weitergeleiteter Heapzeilen

PR #398 (OPT-004-Constraintvertrauen und Eindeutigkeit) ist mit
Squashcommit `db0091a8ae46b504aab793d971bd126e470a87aa` integriert. Alle fünf
PR-Gates und die drei Main-Workflows waren erfolgreich; `main` ist sauber und
synchronisiert, der Remote-Arbeitsbranch wurde durch den Merge entfernt.

Für den nächsten eigenständigen Offlineentwurf gilt eine begrenzte Erweiterung
um 1 Arbeitspaket, 1 PR und bis zu 2 Quellenkandidaten; kumulative Obergrenze
56/64/139. Umfang: eine synthetische Heapfixture, vollständige Tupeloracles,
physischer Forwarded-Record-Zähler, eng begrenzter operativer Fetch-Delta und
kontrollierter Rebuild. Keine SQL-/Runtimeausführung, keine
Leistungsbehauptung und keine menschliche Generalprobe.

Der [STL-003-Entwurf](STL003_FORWARDED_RECORD_LIFECYCLE_DESIGN.md) hält fest,
dass ein positiver `forwarded_record_count` die Struktur belegt, während
`forwarded_fetch_count` nur als flüchtiger operativer Delta-Nachweis gilt.
Fixture-Enginequalifikation, Rechte, Build, vollständiger Demo-/Cleanupvertrag
und jede Laufzeitbehauptung bleiben offen.

## Abschluss: STL-002 – Row-Overflow und LOB

Für die autonome Fortsetzung gilt eine neue, isolierte Erweiterung um 1
Arbeitspaket, 1 PR und bis zu 2 Quellenkandidaten; kumulative Obergrenze
52/60/131. Umfang: ein statischer, quellengebundener Entwurf, der In-Row,
`ROW_OVERFLOW_DATA` und `LOB_DATA` über identische fachliche Nutzdaten und
allocation-type-gebundene Oracles unterscheidet. Keine SQL-/Runtimeausführung,
keine Leistungsbehauptung und keine menschliche Generalprobe.

PR #395 ist mit Squashcommit `67dc715e7b53b0c77f79a3fa5d36413afca5b713`
integriert. Alle fünf PR-Gates und drei Main-Workflows waren erfolgreich;
lokales `main` ist synchronisiert und sauber. Der lokale Branch wurde entfernt;
der Remote-Branch war bereits gelöscht. Der statische Entwurf
[STL-002](STL002_ROW_OVERFLOW_DESIGN.md) bindet 2.000 vollständige Tupel je
Profil und drei Tabellenprofile an die Speicher-/DMV-Quellen. Allocation-Units,
DMV-Zugriffsrechte, Demo-/Cleanupvertrag und tatsächliche I/O-Werte bleiben
später zu qualifizieren. Der lokale Repository-weite Privacy-Scan konnte eine
unveränderte Datei unter `Runtime/AI_COMPLETION_ROUTE/IntegratedRun_PR240/`
nicht parsen; der Scan aller geänderten Dateien und der PR-Privacy-Workflow
bestanden.

## Fortsetzung: QRY-005 – OR-Aufteilung und Mengensemantik

Für den nächsten eigenständigen Offlineentwurf gilt eine begrenzte Erweiterung
um 1 Arbeitspaket, 1 PR und bis zu 2 Quellenkandidaten; kumulative Obergrenze
53/61/133. Der Entwurf vergleicht ein OR-Prädikat mit einer überlappenden,
naiven `UNION ALL`-Aufteilung, `UNION` und disjunkten `UNION ALL`-Zweigen. Er
prüft vollständige Tupel und Mehrfachheiten auf synthetischen Daten; keine
SQL-/Runtimeausführung, Planbehauptung, Leistungsaussage oder menschliche
Generalprobe.

PR #396 ist mit Squashcommit `cead58958474a4c69fe77be897c01cc0816f71b4`
integriert. Alle fünf PR-Gates und drei Main-Workflows waren erfolgreich;
`main` ist synchronisiert, sauber und der Arbeitsbranch entfernt. Der Entwurf
[QRY-005](QRY005_OR_UNION_DESIGN.md) bindet den vollständigen Tupelvergleich
und die 1.000 absichtlichen Mehrfachzeilen bei naivem `UNION ALL` an `SRC-142`.
SQL-Ausführung, Planwahl, Laufzeitwirkung und Cleanup bleiben offen.

## Fortsetzung: OPT-004 – Spaltenkorrelation und Mehrspaltenstatistik

Für den nächsten getrennten Offline-Teilschnitt gilt eine begrenzte Erweiterung
um 1 Arbeitspaket, 1 PR und bis zu 2 Quellenkandidaten; kumulative Obergrenze
54/62/135. Umfang: identische korrelierte synthetische Daten, dokumentierte
Einzel- und Mehrspaltenstatistikstrukturen, vollständige Ergebnisoracles und
getrennte mathematische Referenzwerte gegenüber empirischen Schätzungen. Der
Entwurf umfasst nur den Statistik-/Korrelationsanteil von OPT-004; Constraints,
Eindeutigkeit und Vertrauensstatus bleiben offen. Keine SQL-/Runtimeausführung,
keine Plan- oder Leistungsbehauptung und keine menschliche Generalprobe.

PR #397 ist mit Squashcommit `dd4614aeef5856a862047bfcf10b80cf30569e5c`
integriert. Alle fünf PR-Gates und drei Main-Workflows waren erfolgreich;
`main` ist synchronisiert, sauber und der Arbeitsbranch entfernt. Der
[Statistikentwurf](OPT004_CORRELATED_STATISTICS_DESIGN.md) fixiert 10.000
korrelierte Zeilen, vollständige Ergebnistupel und trennt die hypothetische
Unabhängigkeitsrechnung von späteren Schätzwerten.

## Fortsetzung: OPT-004 – Constraint-Vertrauen und Eindeutigkeit

Für den nächsten getrennten Offline-Teilschnitt gilt eine begrenzte Erweiterung
um 1 Arbeitspaket, 1 PR und bis zu 2 Quellenkandidaten; kumulative Obergrenze
55/63/137. Umfang: gleiche synthetische Daten mit vertrauenswürdigem und
nicht vertrauenswürdigem, aber aktiviertem `CHECK`-Constraint sowie
Eindeutigkeitskontrast mit identischen vollständigen Tupeln. Katalogzustand,
Constraint-Semantik und Ergebnisoracle werden von empirischer Schätzungs- und
Planwirkung getrennt. Keine SQL-/Runtimeausführung, kein Performanceclaim und
keine menschliche Generalprobe.

## Fortsetzung: IDX-001 – Heap- und Clustered-Row-Locators

PR #392 ist mit Squashcommit `97b1ceadad3d0b1f9179fc393dd4e55e6612b10b`
integriert. Alle fünf PR-Gates und drei betroffenen Main-Workflows waren
erfolgreich; lokales `main` ist synchronisiert, sauber und der Remote-Branch
entfernt.

Der Offlineentwurf vergleicht identische Zeilentupel auf Heap und Clustered
Table mit jeweils einem nicht abdeckenden sekundären Index. Er bindet die
unterschiedlichen Row Locator (RID gegenüber Clustered Key) an die bedingte
Showplanzuordnung von `RID Lookup` beziehungsweise `Key Lookup`; beide sind
laut `SRC-138` mit `Nested Loops` verbunden. Fixture- und Tupeloracles decken
Punkt- und Bereichszugriff ab. Die Planassertion verlangt keinen Lookup: falls
einer gewählt wird, muss er zur Tabellenstruktur passen. Kein SQL-Lauf und
keine Leistungsaussage.

Begrenzte Fortsetzungserweiterung +1 Arbeitspaket, +1 PR und bis zu 2
Quellenkandidaten; kumulative Obergrenze 49/57/125. Sie gilt ausschließlich
für Quellenabgleich, statischen IDX-001-Entwurf und Kandidatenpflege. Fixture-
Enginevalidierung, Demo-/Cleanupvertrag, Methodenreview, SQL-/Runtimeausführung
und konkrete Laufautorisierung bleiben offen; menschliche Generalprobe bleibt
ausgeschlossen. Aufwand: ein Entwurf, ein bestehender Quellenregistereintrag
präzisiert und eine Showplanquelle neu registriert; keine neue Abhängigkeit
oder Workflowprüfung.

## Nächster begrenzter Schritt: IDX-002 – Clustered-Key-Breite

PR #393 ist mit Squashcommit `5b52722b741085ffa48f80b4a79f6ad3d9401432`
integriert. Alle fünf PR-Gates und drei betroffenen Main-Workflows waren
erfolgreich; lokales `main` ist synchronisiert, sauber und der Remote-Branch
entfernt.

Für die autonome Fortsetzung gilt eine neue, isolierte Erweiterung um 1
Arbeitspaket, 1 PR und bis zu 2 Quellenkandidaten; kumulative Obergrenze
50/58/127. Umfang: aktuelle Primärquellen und ein statischer Entwurf zum
Vergleich eines schmalen eindeutigen mit einem breiten nicht eindeutigen
Clustered Key, Locatorbreite, Nonclustered-Indexseiten und Uniquifier. Keine
SQL-/Runtimeausführung, keine allgemeine Größen- oder Leistungsaussage und
keine menschliche Generalprobe.

## Fortsetzung: STL-001 – Zeilenbreitenleiter

Für die autonome Fortsetzung gilt eine neue, isolierte Erweiterung um 1
Arbeitspaket, 1 PR und bis zu 2 Quellenkandidaten; kumulative Obergrenze
51/59/129. Umfang: ein statischer, quellengebundener Entwurf einer
Zeilenbreitenleiter mit festen, variablen und nullable Spalten, Ergebnisoracle
und unterstützter Seiten-/Recordbeobachtung. Keine SQL-/Runtimeausführung,
keine allgemeine Page-Dichte- oder Leistungsaussage und keine menschliche
Generalprobe.

Der vorgeschlagene Vier-Stufen-Heapaufbau enthält 100.000 identische
Grunddatensätze sowie kumulativ einen festen 100-Byte-Block, eine Variable mit
exakten 0/25/50/100/200-Byte-Verteilungen und eine nullable Variable mit
80-Prozent-NULL-Verteilung. Das Full-Tuple- und Längenoracle ist je Profil
definiert. Abgeleitete Heapmodellwerte für Recordgröße und Zeilen pro Seite
sind ausdrücklich von `sys.dm_db_index_physical_stats`-Messwerten getrennt.
Keine Engine-Ausführung und keine Page-Density- oder Performanceaussage.

## IDX-002 – statischer Quellen- und Entwurfsstand

Der vorgeschlagene Vergleich verwendet identische 100.000-Zeilen-Fixtures mit
einem eindeutigen schmalen `int`-Clustered Key beziehungsweise einem
nicht-eindeutigen 68-Byte-Schlüssel aus `int` und `char(64)`. Der nicht eindeutige
sekundäre Index auf `FilterBand` macht den impliziten Locator und den
Uniquifier-Effekt sichtbar. Vollständige Ergebnistupel sind das Korrektoracle;
geschätzte Schlüsselbreite und gemessene Seitenzahlen bleiben getrennte
Größenarten. Keine SQL-Ausführung oder allgemeine Performancebehauptung.

## Fortsetzung: QRY-023 – FWK-004-Vertrag statisch gebunden

Der Offlineprüfer bindet die tatsächlich implementierten Parameter von
`USP_BeginMeasurement` und `USP_EndMeasurement`, die QRY-023-Aufrufwerte,
Output-ID und Ergebniszeilen sowie die für die Messabnahme verwendeten
`MeasurementRun`-Spalten. Zwei synthetische Regressionen weisen geänderte
Prozedursignatur und fehlende Ergebnisspalte zurück. Der Framework-Contracts-
Workflow führt diese Prüfungen bei Änderungen am Framework aus. Zehn
Prüffälle und der Positivlauf bestehen lokal; kein SQL-Lauf.

Begrenzte Erweiterung +1 Arbeitspaket, +1 PR und +2 Kandidaten; kumulative
Obergrenze 39/47/105. Verarbeitungskosten-/Reviewbewertung: zwei kleine,
deterministische Offlineprüfungen im vorhandenen Fünf-Minuten-Workflow; kein
zusätzliches Runtime-/Parsermatrix-Gate und keine doppelte Ausführung bei
reinen Frameworkänderungen im QRY-Workflow. Token- und Geldverbrauch bleiben
unbekannt. Weiter offen: unabhängige Methodenfreigabe, formale Harnessabnahme,
empirisches Ressourcenprofil und konkrete Laufautorisierung. QRY-023 bleibt
`PROPOSED`/`YELLOW`, nicht katalogisiert und ungefahren; menschliche
Generalprobe ist aus diesem autonomen Auftrag ausgeschlossen.

## Fortsetzung: QRY-002 – Konvertierungsrichtung didaktisch ergänzt

PR #383 ist mit Squashcommit `90d2abf85180d23556af3bff1d3fa004e7c999e5`
integriert. Alle fünf PR-Gates und drei betroffenen Main-Workflows waren
erfolgreich; lokales `main` ist synchronisiert und der Remote-Branch entfernt.

Die bestehende Lehrnotiz zeigt jetzt explizit beide Richtungen der
Typpräzedenz: `int` gegenüber `nvarchar` sowie `nvarchar` gegenüber `varchar`.
Sie trennt die dokumentierte Konvertierungsrichtung von der erst am konkreten
tatsächlichen Plan und Workload prüfbaren Zugriffswirkung. Die gelesenen
Microsoft-Primärquellen und der Geltungsbereich von `SRC-012`, `SRC-030` und
`SRC-031` sind aktualisiert. Keine Demo, keine Laufzeitmessung und keine
Performancebehauptung.

Begrenzte Erweiterung +1 Arbeitspaket, +1 PR und +2 Evidenzkandidaten;
kumulative Obergrenze 40/48/107. Aufwand: eine eng begrenzte Lehrnotiz- und
Quellenregisteraktualisierung, keine neue Abhängigkeit, kein neuer CI-Job.
QRY-002 bleibt ungefahren; eine eigenständige Demoabnahme wäre separat.

## Fortsetzung: QRY-003 – typabhängige Tagesgrenzen präzisiert

PR #384 ist mit Squashcommit `aa2e053f3875a0ff894eaa3aed02cd43bdc5cfa6`
integriert. Alle fünf PR-Gates und drei betroffenen Main-Workflows waren
erfolgreich; lokales `main` ist synchronisiert und der Remote-Branch entfernt.

Die Lehrnotiz grenzt jetzt `datetime` (letzter darstellbarer Tageszeitpunkt
`23:59:59.997`) von `datetime2(7)` (bis `23:59:59.9999999`) ab. Sie bindet
`BETWEEN`-Inklusivität, typisiertes `DATEADD` und die Aussagegrenze für
SARGability an Microsoft-Primärquellen. Der Bereichsausdruck bleibt eine
Methode, keine Seek- oder Leistungszusage. `SRC-133` wurde ergänzt und `SRC-012`
um den Indexkontext erweitert. Keine Laufzeit oder Messung.

Begrenzte Erweiterung +1 Arbeitspaket, +1 PR und +2 Evidenzkandidaten;
kumulative Obergrenze 41/49/109. Der Eingriff aktualisiert eine vorhandene
Lehrnotiz und ein Quellenregister; keine zusätzliche Abhängigkeit oder
Workflowprüfung. Als nächster Offlineinhalt folgt RES-004. Die menschliche
Generalprobe bleibt ausgeschlossen.

## Fortsetzung: RES-004 – Quellenregister an den bestehenden Lehrvertrag gebunden

PR #385 ist in `origin/main` integriert; alle fünf PR-Gates und drei
betroffenen Main-Workflows waren erfolgreich. `main` ist synchronisiert und
der Remote-Branch entfernt.

Der Quellenabgleich bestätigt die bestehenden Aussagen zu Request-/Grant-
Bindung und Pool-/Semaphore-Scope. Die vorhandenen Kennungen `SRC-010` und
`SRC-110` deckten den Lehrvertrag noch nicht ab. Beide Scopes sind ergänzt;
`SRC-134` registriert die Microsoft-Primärquellen zu Resource-Semaphore,
Grant-Diagnose und den getrennten RES-003-Prozess-/Betriebssystemsignalen.
Die Lehrnotiz verlinkt nun die stabilen Quellen-IDs. Es wurde keine DMV-Abfrage
ausgeführt.

Begrenzte Erweiterung +1 Arbeitspaket, +1 PR und +2 Evidenzkandidaten;
kumulative Obergrenze 42/50/111. Verarbeitung: vorhandene sechs Quellen
gegenprüfen, einen zusammengehörigen Quellenregistereintrag ergänzen und die
Lehrnotiz daran binden; kein neuer CI-Job, keine neue Abhängigkeit und keine
Runtime. Als nächster Schritt folgt die vollständige betroffene Lesepfadprüfung.

## Fortsetzung: QRY-003 – vorgeschlagenes Intervalltestdesign

PR #386 ist integriert; alle vier PR-Gates sowie die beiden betroffenen
Main-Workflows waren erfolgreich. `main` ist synchronisiert und sauber.

Der vollständige betroffene Lesepfad von Dokumentationseinstieg über Curriculum,
Lernziel, Lehrnotiz, Quellenregister und Präsentationsabdeckung ist geprüft.
Die vorhandenen Lernziel- und Navigationsbezüge sind konsistent. Ein neuer,
nicht freigebender Designentwurf konkretisiert Tupel-Oracles für `BETWEEN`,
typabhängige künstliche Tagesendwerte und das halboffene Intervall für
`datetime` und `datetime2(7)`. Er hält Plan-/Read-Beobachtung von
Ergebnissemantik getrennt und verweist die SARGability-Gegenprobe auf QRY-001.
Kein Manifest, Katalogeintrag oder SQL-Lauf.

Begrenzte Erweiterung +1 Arbeitspaket, +1 PR und +2 Evidenzkandidaten;
kumulative Obergrenze 43/51/113. Aufwand: ein Designentwurf und die Abstimmung
zweier bestehender Kandidaten-/Präsentationsübersichten; keine neue
Abhängigkeit, kein neuer Workflow und keine Runtime. Die Fixturenormalisierung
gegen tatsächliche Engine-Rundung bleibt vor jeder späteren SQL-Umsetzung offen.

## Fortsetzung: QRY-007 – Join-Kardinalität und `DISTINCT`

PR #387 ist mit Squashcommit `1ee4867ec415e3c85bffab42b17ecd7c79cd3621`
integriert. Fünf PR-Gates sowie die beiden betroffenen Main-Workflows waren
erfolgreich; lokales `main` ist synchronisiert und der Remote-Branch entfernt.

Der nächste priorisierte Offlinekandidat trennt die dokumentierte Semantik
passender Join-Zeilenpaare, eindeutiger `DISTINCT`-Projektionen und
`EXISTS`. Ein vorgeschlagener Eltern-/Kind-Orakelentwurf macht explizit, dass
ein One-to-many-Join Eltern-IDs vervielfacht; `DISTINCT` kann diese sichtbare
Multiplizität nur für gleiche projizierte Zeilen entfernen. `EXISTS` passt zur
Frage, ob mindestens ein passendes Kind vorliegt. Aggregation bleibt dem
eigenständigen Lernziel vorbehalten, wenn Kindfakten wie Anzahl oder Summe
verlangt sind. `SRC-135` bindet vier Microsoft-Primärseiten. Der Entwurf deckt
nicht die weiteren QRY-007-Themen `UNION`, `UNION ALL` oder `SELECT *` ab.

Der Entwurf ist nicht implementiert, nicht katalogisiert und ungefahren.
Begrenzte Erweiterung +1 Arbeitspaket, +1 PR und +2 Quellen-/Testkandidaten;
kumulative Obergrenze 44/52/115. Verarbeitung: ein Quellenbundle und ein
statischer Fixture-/Oracleentwurf mit einer Kandidatenplanpflege; kein neuer
Workflow, keine Abhängigkeit und keine Runtime. Engine-/Fixtureprüfung,
vollständiger Demo-/Cleanupvertrag, Methodenreview und konkrete Laufautorisierung
bleiben spätere getrennte Gates. Menschliche Generalprobe bleibt ausgeschlossen.

Die quellengebundene Lehrnotiz ist nun im Curriculum-Einstieg verlinkt. Sie
führt die Fixture in statischen Table-Variable-Beispielen durch Join-Paare,
Elternprojektion, `DISTINCT`, `EXISTS` und eine bedarfsgerechte Zählung; die
vollständigen Soll-IDs und Multiplikitäten sind angegeben. Es wurde kein SQL
ausgeführt und keine Lernziel-, Claim- oder Demo-ID ergänzt.

Begrenzte Erweiterung +1 Arbeitspaket, +1 PR und +2 Evidenzkandidaten;
kumulative Obergrenze 45/53/117. Verarbeitung: eine kleine Lehrnotiz plus
Curriculum-Link und begrenzte Lesepfadprüfung; keine neue Abhängigkeit und
keine Workflowprüfung. Der nächste eigenständige Offlinekandidat ist `IDX-003`
gemäß der vorhandenen Kandidatenreihenfolge; Ausführung, Planbehauptung und
menschliche Generalprobe bleiben davon unberührt.

PR #388 ist mit Squashcommit `b31f32060a9381b690a2ca8cc3c94198fee66ac2`
integriert. Alle vier PR-Gates und beide betroffenen Main-Workflows waren
erfolgreich; `main` ist synchronisiert und der Remote-Branch entfernt.

## Fortsetzung: IDX-003 – Key-Reihenfolge und INCLUDE

Der priorisierte Kandidat erhält einen Offlineentwurf mit drei sekundären
Indexprofilen und einer Baseline auf einer festen 120.000-Zeilen-Fixture.
Vier Prädikatsformen vergleichen jeweils vollständige Tupel und `RowId` gegen
dieselbe Abfragemenge. Der Entwurf hält Key-Reihenfolge, `Payload` als
Schlüssel-/INCLUDE-Spalte, Abdeckung und Seitenzahlen auseinander. `SRC-012`
bindet die Key-Reihenfolge; `SRC-136` registriert INCLUDE- und
`sys.dm_db_partition_stats`-Aussagen. Seek-/Plan-/Read-Ergebnisse bleiben
empirisch; kein Indexhint oder SQL-Lauf.

Begrenzte Erweiterung +1 Arbeitspaket, +1 PR und +2 Quellen-/Testkandidaten;
kumulative Obergrenze 46/54/119. Verarbeitung: ein Quellenbundle, ein
Abfrage-/Indexentwurf und eine bestehende Kandidatenzeile; keine Abhängigkeit,
kein neuer Workflow und keine Runtime. Die Sollzeilenzahlen müssen beim
späteren Fixture-Build verifiziert werden. Demo-/Cleanupvertrag,
Methodenreview und Ausführungsfreigabe bleiben getrennt; menschliche
Generalprobe bleibt ausgeschlossen.

PR #389 ist mit Squashcommit `63b7542e69859689cce2f92943788c16da8e8dae`
integriert. Alle fünf PR-Gates und drei betroffenen Main-Workflows waren
erfolgreich; lokales `main` ist synchronisiert und der Remote-Branch entfernt.

## Fortsetzung: IDX-004 – Lookup-Kurve über kontrollierte Selektivitäten

Der nächste Kandidat erhält eine deterministische 100.000-Zeilen-Fixture mit
elf abgestuften Treffermengen und einer Restgruppe. Dieselbe parameterisierte
Abfrage wird gegen clustered-only Baseline, nicht abdeckenden Index und
abdeckenden Index geprüft. `OPTION (RECOMPILE)` bindet jeden Fall an seinen
aktuellen Parameterwert. Vollständige Tupel und tatsächliche Trefferzahl sind
das Ergebnisoracle; Planwahl, Lookup-Ausführungszahl, Logical Reads und
Compilewerte sind getrennte Diagnostik. Ein beobachteter Planübergang gilt
nur für Fixture und Build; ein allgemeiner Prozentsatz wird nicht behauptet.
`SRC-137` bindet die Microsoft-Operator- und Recompilesemantik.

Begrenzte Erweiterung +1 Arbeitspaket, +1 PR und +2 Quellen-/Testkandidaten;
kumulative Obergrenze 47/55/121. Verarbeitung: ein Quellenbundle und ein
statischer Selektivitäts-/Oracleentwurf, aktualisierte Kandidatenzeile; keine
neue Abhängigkeit, kein Workflow und keine Runtime. Engineprüfung der
Generatorverteilung, Demo-/Cleanupvertrag, Methodenreview und konkrete
Ausführungsfreigabe bleiben getrennt. Menschliche Generalprobe bleibt
ausgeschlossen.

PR #390 ist mit Squashcommit `c1f84cb80d078fbd1afa9156a123d58e4a5a8a30`
integriert. Alle fünf PR-Gates und drei betroffenen Main-Workflows waren
erfolgreich; `main` ist synchronisiert und der Remote-Branch entfernt.

Die quellengebundene Lehrnotiz ist vom Curriculum-Einstieg aus verlinkt. Sie
erklärt die Rolle des Key Lookups, die abdeckende Gegenprobe und die getrennte
Interpretation vollständiger Ergebnisoracles, tatsächlicher Planoperatoren und
Logical Reads. Sie setzt keinen allgemeinen Kippunkt und ergänzt keine neue
Lernziel-, Claim- oder Demo-ID.

Begrenzte Erweiterung +1 Arbeitspaket, +1 PR und +2 Evidenzkandidaten;
kumulative Obergrenze 48/56/123. Verarbeitung: eine kurze Curriculum-Erklärung,
README-/Kandidatenlinks und begrenzte Lesepfadprüfung; keine neue Abhängigkeit
oder Workflowprüfung. Nächster unabhängiger Offlinekandidat ist `IDX-001` in
der vorhandenen Reihenfolge. Kein Laufgate und keine menschliche Generalprobe
werden damit erfüllt.

## Fortsetzung: QRY-023 – GDR-Tags und Digestbindung aktualisiert

Die MCR-Tagliste enthält GDR-spezifische Linux-Images für die drei Profile.
Die Tags `2019-CU32-GDR12-ubuntu-20.04` und
`2022-CU27-GDR1-ubuntu-22.04` tragen per OCI-Label `15.0.4500.2` bzw.
`16.0.4305.5`; das SQL-Server-2025-Image bleibt auf `17.0.5035.5`. Damit
stimmen jetzt alle drei Imagebuilds mit dem neuesten dokumentierten
Linux-Servicingstand überein. Lock, Preflight, Setup, README und Review binden
die neuen Tags und Manifest-/Konfigurationsdigests. Nur Registrymetadaten
wurden gelesen, keine Images gezogen oder gestartet.

Die unabhängige Tag-/Manifestprüfung erweitert die kumulative Obergrenze um 1
Arbeitspaket, 1 PR und 2 Quellenkandidaten auf höchstens 38/46/103. Offen
bleiben Runtimeverbrauch des Locks, unabhängige Methodenfreigabe, formale
Harnessabnahme, Ressourcenmessung und konkrete Laufautorisierung. QRY-023
bleibt `PROPOSED`/`YELLOW`, nicht katalogisiert und ungefahren.

## Fortsetzung: QRY-023 – Linux-Imagebuilds gebunden

Historischer Registryabgleich: Die plain-CU-Tags `2019-CU32-ubuntu-20.04` und
`2022-CU27-ubuntu-22.04` werben `15.0.4430.1` und `16.0.4295.3`; sie enthalten
nicht den veröffentlichten CU+GDR-Stand. Dieser Zwischenbefund wurde durch die
GDR-Tagprüfung im obigen Abschnitt überholt. Das 2025-CU10-Image wirbt
`17.0.5035.5` und stimmte bereits überein. Die
AMD64-Manifest- und Konfigurationsdigests sowie die Labels sind in
[GRAPH_TABLES_BUILD_EDITION_REVIEW.md](GRAPH_TABLES_BUILD_EDITION_REVIEW.md)
und `SRC-130` festgehalten. Es wurde kein Image heruntergeladen oder gestartet;
ein späterer Lauf muss Digest und `SERVERPROPERTY` erneut binden.

Der neue statische Pinabgleich erweitert die kumulative Obergrenze um 1
Arbeitspaket, 1 PR und 2 Quellenkandidaten auf höchstens 35/43/97. Weiterhin
offen: unabhängige Methodenfreigabe, formale Harnessabnahme, Ressourcenprofil
und konkrete Laufautorisierung. Die Suche nach passenden neueren Tags ist im
neuesten Statusabschnitt abgeschlossen. QRY-023
bleibt `PROPOSED`/`YELLOW`, nicht katalogisiert und ungefahren.

## Fortsetzung: QRY-023 – vorgeschlagener Image-Lock

Historischer Zwischenstand: Der erste Lock verwendete CU-only-Tags; die
GDR-spezifischen Tags und Digests im obersten Statusabschnitt haben diese Werte
ersetzt.

Die drei AMD64-Manifest- und Konfigurationsdigests stehen jetzt zusätzlich
maschinenlesbar in `container-images.proposed.json`. Der Offlinevalidator prüft
Schema, Profilanzahl, Produktmajor, Compatibility Level, Plattform, geprüften
MCR-Tag, Digestform, unveränderliche `image@sha256`-Referenz und Übereinstimmung
des Image-Produktlabels mit Preflight und Setup. Regressionen prüfen mutable
Tagverwendung und Buildabweichung. Der Lock autorisiert keinen Lauf und wird
noch von keinem Runtimeaufruf konsumiert.

Diese statische Integrationswelle erweitert den kumulativen Rahmen um 1
Arbeitspaket, 1 PR und 2 Kandidaten auf höchstens 36/44/99. Keine Container- oder
SQL-Ausführung. Offen bleiben Runtimeintegration, unabhängige Methodenfreigabe,
formale Harnessabnahme, 2019/2022-GDR-Tags, Ressourcenprofil und konkrete
Laufautorisierung.

## Fortsetzung: QRY-023 – begrenztes Ressourcenprofil

Der Demo-Vertrag verlangt Host-Mindestressourcen. Microsofts Linuxminimum ist
als `SRC-131` gebunden: zwei x64-Kerne zu 2 GHz, 2 GB RAM und 6 GB Speicher.
`SRC-132` trennt die harte Container-Cgroup-Grenze vom niedrigeren
`MSSQL_MEMORY_LIMIT_MB`. Darauf aufbauend schlägt der Image-Lock 8 GiB Host-RAM,
20 GiB freien Speicher, höchstens zwei Containerkerne, 4.096 MiB Container-RAM
und 3.072 MiB SQL-Limit vor. Der Abstand zum Herstellerminimum ist eine
Planungsannahme; es gab keine QRY-023-Messung. MCR-Layergrößen und das bestehende
900/90-Sekundenbudget sind dokumentiert. Ein künftiger Runtimeaufrufer muss
Grenzen vor Start prüfen und durchsetzen.

Die Dokumentations-/Vertragswelle erweitert die kumulative Obergrenze um 1
Arbeitspaket, 1 PR und 2 Quellenkandidaten auf höchstens 37/45/101. Offen sind
unabhängige Methodenfreigabe, formale Harnessabnahme, mögliche neuere Images,
empirische Speicher-/TempDB-/Laufzeitqualifikation, Integration der Limits in
einen Runtimeaufruf und konkrete Laufautorisierung. QRY-023 bleibt
`PROPOSED`/`YELLOW` und ungefahren.

## Fortsetzung: QRY-023 – ScriptDom-Grammatikprüfung

PR #376 ist als Squashcommit `ed75e78b7558fec94fed17aba1ad20d93d2891a9` in `origin/main` integriert; alle zehn PR-Workflows waren erfolgreich, `main` ist lokal synchronisiert und beide Branches sind entfernt. Die Editionsmatrix und zeitgebundenen Buildpins sind in `SRC-126/127` gebunden.

Der nächste Schritt ergänzt eine gesperrte Microsoft ScriptDom-Abhängigkeit `170.191.0` und prüft alle acht ausführbaren T-SQL-Dateien mit den Grammatikparsern 150, 160 und 170. Der `:r`-SQLCMD-Wrapper wird separat auf den erwarteten Include geprüft; Platzhalter werden nur im flüchtigen Parsertext synthetisch ersetzt. Alle Parserläufe bestanden lokal am 7. November 2026. Das ist kein SQL-Engine-Kompilier- oder Laufnachweis. Details und Grenzen stehen in [GRAPH_TABLES_SCRIPTDOM_PARSER_REVIEW.md](GRAPH_TABLES_SCRIPTDOM_PARSER_REVIEW.md).

Der QRY-023-CI-Trigger bleibt eng auf Demopfad, Parser, Regressionstest und Workflow beschränkt; NuGet-Restore ist gesperrt, Joblimit fünf Minuten, keine SQL-Container oder Runtime-Matrix. Die Änderung erweitert die kumulative Obergrenze um 1 Arbeitspaket, 1 PR und 2 Quellenkandidaten auf höchstens 34/42/95. Unabhängige Methodenfreigabe, formale Harness-Abnahme, Image-Digests, Ressourcenprofil und konkrete Runtimeautorisierung bleiben offen.

## Fortsetzung: QRY-023 – Editionsmatrix und Servicingpins

PR #375 ist als Squashcommit `a92ae3049c9f3f62efa2d582791e92fddb855410` integriert; der eng gefilterte statische CI-Workflow, seine vier synthetischen Regressionstests und alle betroffenen Projektworkflows waren erfolgreich. Das eigene Demo-SQL wurde nicht ausgeführt.

Historischer Stand zum Merge von PR #376: Die damaligen Produktservicingpins
`15.0.4500.2`, `16.0.4305.5` und `17.0.5035.5` wurden nach dem folgenden
MCR-Metadatenabgleich für die vorgesehenen Linux-Images durch deren tatsächlich
deklarierte Builds ersetzt. Maßgeblich für den aktuellen Vorschlag ist der
vorstehende Abschnitt `Linux-Imagebuilds gebunden`.

Diese Fortsetzung erweitert die kumulative Arbeitsobergrenze um 1 Arbeitspaket, 1 PR und 2 Quellenkandidaten auf höchstens 33/41/93. Unabhängige Methodenfreigabe, formale T-SQL-/Harness-Abnahme, Index-/Ressourcenbegründung und konkrete Ausführungsautorisierung bleiben getrennte Gates; QRY-023 bleibt `PROPOSED`/`YELLOW`, nicht katalogisiert und ungefahren.

## Fortsetzung: QRY-023 – statischer Harness-Vertrag

PR #374 ist als Squashcommit `74cd9ac303bbc1648216cdfc8268ab70e8b25d09` in `origin/main` integriert; lokales `main` stimmt damit überein, der Arbeitsbranch ist entfernt. Die neun PR-Workflows waren erfolgreich. Der allgemeine Cleanup-Eigentumstest lief in disposable SQL Server 2019/2022/2025-Containern; er prüfte das gemeinsame Cleanupframework und führte keine QRY-023-Abfragen aus.

Als nächster Offline-Schritt schützen `Tests/Static/validate_qry023_proposed_harness.py`, die gezielten synthetischen Regressionstests und ein eng gefilterter statischer CI-Workflow den Manifeststatus, die Lifecycle-/Cleanupmarker, den 30k/20k/10k-Datenvertrag, bidirektionale Ergebnisgleichheit, fünf AB/BA-Messpaare, getrennte Planabfragen und das Fehlen einer Katalogintegration. Diese Prüfung belegt strukturelle Projektverträge, keine T-SQL-Kompilierbarkeit oder Methodenfreigabe. Es wurde kein QRY-023-SQL gestartet.

Die kumulative Arbeitsobergrenze wird um 1 Arbeitspaket, 1 PR und 2 Evidenzkandidaten auf höchstens 32/40/91 erweitert. Offen bleiben formale T-SQL-/Harness-Abnahme und unabhängige Methodenfreigabe, konkrete Build-/Edition-/CU-Pins, Index- und Ressourcenbegründung sowie konkrete getrennte Ausführungsautorisierung. `PROPOSED`/`YELLOW` und der Ausschluss aus Runtimekatalog und -matrix bleiben bestehen.

## Fortsetzung: Graph Tables – deterministischer Messworkload und Traceability

Der kleine Zwei-Pfad-Aufbau bleibt das exakte Korrektheitsoracle. Für die nach `LO-M03-06`/`CLM-047` verpflichtende Plan-/Vergleichsmessung ist zusätzlich ein getrenntes synthetisches Profil vorgeschlagen: 10.000 disjunkte Zwei-Kanten-Pfade, 30.000 Knoten, 20.000 gerichtete Kanten, deterministische IDs `3*n+1..3*n+3`. Vollpfadgleichheit wird vor dem Messlauf über beidseitiges `EXCEPT`, Eindeutigkeit und Sollanzahl geprüft. Die Messabfrage zählt mit `COUNT_BIG(*)`, damit die 10.000 Ergebniszeilen nicht je Messlauf zum Client übertragen werden. Das vorgeschlagene Protokoll schließt je Variante ein Warm-up aus und misst fünf Paare mit alternierender AB/BA-Reihenfolge in derselben Session; keine Cacheleerung, keine Performance-Schwelle und keine Versionsaggregation. Details: [QRY-023-Messworkload](GRAPH_TABLES_MEASUREMENT_WORKLOAD_DESIGN.md).

Die [Traceability-Matrix](../Curriculum/TRACEABILITY_MATRIX.md) ordnet `CLM-047` jetzt `SRC-122`/`SRC-123`, der geplanten Demo `QRY-023` (`PROPOSED`) und dem Profil `TP-PERF` zu. Das ist eine geplante Zuordnung, keine implementierte Demo oder Abnahme.

Für diese begrenzte Fortsetzung beträgt die kumulative Arbeitsobergrenze 29 Arbeitspakete, 37 Pull Requests und 85 Evidenzkandidaten. Token- und Geldverbrauch bleiben unbekannt. Registry-Semantik, Kennungsregistrierung und Curriculum-Traceability wurden lokal geprüft und bestanden. Keine Codeänderung, kein SQL-, Lab- oder Runtime-Lauf.

## Fortsetzung: Graph Tables – Quellen- und Methodenpräzisierung

Das [Quellen- und Methodenreview](GRAPH_TABLES_METHOD_REVIEW.md) ergänzt den Workloaddesign-Entwurf um `MATCH` statt direkter Gleichheit von Graph-ID-Pseudospalten, begrenzt die Indizes auf Kandidaten und trennt Actual-Plan-Diagnostik von den `FWK-004`-Messwiederholungen. Die Planerfassung benötigt `SHOWPLAN`; `STATISTICS IO/TIME` laut Quellen nicht. Der tatsächliche Indexnutzen, konkrete Plan-/Messausgabe und Rechte bleiben vor einer Implementierung weiter zu qualifizieren. Die Evidenz steht in `SRC-124`/`SRC-125`.

Diese Fortsetzung erweitert die kumulative Obergrenze um 1 Arbeitspaket, 1 PR und 2 Quellenkandidaten auf höchstens 30/38/87. Das Review ist dokumentarisch, keine unabhängige Methodenfreigabe. Keine Codeänderung und kein SQL-, Lab- oder Runtime-Lauf.

## Fortsetzung: QRY-023 – initialer Harness-Codeentwurf

Ein lokaler, noch nicht katalogisierter Harness-Entwurf ergänzt jetzt Preflight, exakte Markerprüfung, eigene Wegwerfdatenbank, deterministischen Graph-/Relationsaufbau samt kleinem Oracle, Vollpfadvergleich, FWK-004-Messreihe, getrennte Actual-Plan-Diagnostik und markergebundenen Cleanup. Der Manifeststatus bleibt `YELLOW`/`PROPOSED`; dieser Branch wurde nicht ausgeführt. Die `:r`-Einbindung der kanonischen Framework-Messreferenz setzt den Harness-Aufruf aus dem Repository-Stamm voraus. Keine SQL-/Lab-/Runtimeausführung.

Die kumulative Obergrenze steigt um 1 Arbeitspaket und 1 PR auf 31/39/89; die Quellenobergrenze bleibt bei 89. Offen sind statische Harness-/SQL-Abnahme, unabhängige Methodenfreigabe, konkrete Build-/Edition-/CU-Pins, Indexbegründung, Ressourcenfreigabe und spätere konkrete Runtimeautorisierung. Die Demo bleibt aus Katalog und Runtimematrix heraus.

## Fortsetzung: Graph Tables – Framework-, Mess- und Zielmatrixreview

Der Abgleich gegen das Curriculum hat eine erforderliche Korrektur ergeben: `LO-M03-06` verlangt identische Baseline und Vergleichsmessung; `CLM-047` benennt Plan- und Messprüfung. Planbeobachtung und Messung sind daher für QRY-023 Pflicht. Das Fünf-Knoten-/Vier-Kanten-Fixture bleibt ein Korrektheitsoracle und ist kein qualifiziertes Messworkload. `FWK-004`/`FWK-005` verlangen Warm-up-Ausschluss, dokumentierte Wiederholungen, robuste Zusammenfassung samt Streuung und Plan-/Statistikevidenz. Deterministische Messlast, Wiederholungsplan und fachlich begründete Indexe sind der nächste Designschritt.

Microsoft dokumentiert Graph-NODE-/EDGE-Tabellen ab SQL Server 2017, weist aber darauf hin, dass sie keine temporären Tabellen sein können. Der Review bindet deshalb den späteren Lauf an die eigene `FWK-002`-markierte Wegwerfdatenbank. Die Projektmatrix SQL Server 2019/150, 2022/160 und 2025/170 wird als Designziel vorgeschlagen; keine konkrete QRY-023-Build-/Edition-/Runtimefreigabe folgt daraus. Details und Quellen: [Framework- und Zielmatrixprüfung](GRAPH_TABLES_FRAMEWORK_AND_MATRIX_REVIEW.md).

Für diese Fortsetzung beträgt die kumulative Arbeitsobergrenze 28 Arbeitspakete, 36 Pull Requests und 83 Quellenkandidaten. Token- und Geldverbrauch bleiben unbekannt. Es gab keine Code-, Test-, SQL-, Lab- oder Runtimeausführung.

## Fortsetzung: Graph Tables – QRY-023 registriert und statischer Vertrag

Der synthetische Vergleich ist als `QRY-023` unter Task `TSK-017` in der zentralen Registry registriert. Er ordnet sich dem bestehenden `LO-M03-06` und `CLM-047` zu; das Curriculum erhält kein neues Lernziel. Der Demo-Katalogstatus bleibt `PROPOSED`. Der [statische Vertrag](GRAPH_TABLES_DEMO_CONCEPT.md) fixiert fünf synthetische Knoten, vier gerichtete Kanten, die exakten zwei Pfadtripel, identische Ergebnisform, isolierte Testdatenbank, Rechteaufteilung, Eigentumsmarker und Cleanup-/Fehlergrenzen; Build-/CU-Pins, Editionen und Runtimezielprofile bleiben noch zu qualifizieren.

Für diese begrenzte Fortsetzung beträgt die kumulative Arbeitsobergrenze 27 Arbeitspakete, 35 Pull Requests und 81 Quellen-/Vertragskandidaten. Token- und Geldverbrauch bleiben unbekannt; die Zähler sind keine Provider-Ausgabensperre. Es gab keine SQL-, Lab- oder Runtimeausführung und keinen Performanceclaim.

Vor einer Implementierung folgen die unabhängige Methoden-/Quellenprüfung des statischen Vertrags, der Abgleich gegen aktuelle Frameworkmarker und Cleanupkonventionen sowie die Festlegung konkreter Zielbuilds, Editionen und Compatibility Levels. Erst danach kann ein ausführbares Artefakt vorbereitet werden; SQL-/Lab-Ausführung und Laufzeitqualifikation bleiben getrennte Freigabegates.

## Fortsetzung: Graph Tables – Quellen- und Abdeckungsprüfung

PR #364 ist auf `main` vollständig integriert: sieben aktuelle PR- und fünf
Main-Workflows erfolgreich, Squashcommit
`e39367d55541b27e773cfa1a1c4eeb2640bffd8a`. Der vollständige Tree
`3d0f1b7a96c4fc9a179b015296eb4fc55a3418fa` ist lokal und auf `origin/main`
identisch; der lokale und der Remote-Arbeitsbranch sind entfernt.

Die autonome Entwicklung läuft nach dem abgeschlossenen `OPTIMIZED_SP_EXECUTESQL`-
Checkpoint weiter. Die Curriculum-Suche ergab keine eigene Abdeckung für Graph
Tables, `MATCH` oder den Vergleich mit einem relationalen Kantentisch.
Microsoft dokumentiert Graphtabellen und `MATCH` ab SQL Server 2017 und ein
synthetisches Beispiel mit Setup, Abfrage und Cleanup. Die zwei Quellen sind in
der [Quellen- und Abdeckungsprüfung](GRAPH_TABLES_SOURCE_COVERAGE_REVIEW.md)
gebunden.

Graph Tables sind als erster Offline-Entwurf vor External Tables empfohlen,
weil der synthetische Graph lokal entworfen werden kann, ohne nach bisheriger
Quellenprüfung einen externen Connector oder Datendienst vorauszusetzen. Das
ist eine Planungsschlussfolgerung. Status bleibt `PROPOSED`; Owner, Lernziel,
Folien, Graph-Indizes, Versionsmatrix und Demo-Vertrag sind offen. Es gab keine
SQL-, Lab- oder Runtimeausführung und keine Performancequalifikation.

Für diesen historischen Quellenprüfungsschritt wurde das kumulative Arbeitsbudget um 1 Arbeitspaket, 1 Pull Request und 2 Quellenkandidaten auf höchstens 21/29/69 erweitert. Die damals offenen Punkte Curriculumanker, statischer Vertrag, Registrierung und Syntaxprüfung sind in den nachfolgenden Fortsetzungen abgearbeitet; Runtime bleibt ausgeschlossen.

Die zweite Graph-Table-Welle ergänzt die [Versions- und Indexprüfung](GRAPH_TABLES_VERSION_INDEX_REVIEW.md).
Zwei weitere Microsoft-Primärquellen belegen Empfehlungen zu Graph-ID- und
Kantenindizes sowie dokumentierte Graph-Erweiterungen in SQL Server 2019.
Aussagen zu 2022/2025, Editionen, Compatibility Levels und deren vollständigem
Featureumfang bleiben offen. Die kumulative Arbeitsobergrenze wurde hierfür
um ein weiteres Arbeitspaket, einen PR und zwei Quellenkandidaten auf höchstens
22/30/71 erweitert; weiterhin keine Demo- oder SQL-/Runtimefreigabe.

PR #365 ist auf `main` integriert: sieben aktuelle PR- und fünf Main-Workflows
erfolgreich, Squashcommit `0852ed11886a9a76c83ef3a4f758faa9eee7189d`.
Vollständiger Tree `c85c36c03d748a8c02e810f30f4e4d72dcbf5b55` stimmt lokal und
auf `origin/main` überein; lokaler und Remote-Branch sind bereinigt.

Als nächsten begrenzten Schritt ordnet die Curriculumprüfung den Vorschlag
`LO-M03-06`/`CLM-047` als primären bestehenden Lernzielanker zu. Die formale
Traceability-Zuordnung bleibt bis zum Demoentwurf `PROPOSED`; `LO-M02-04` und
`LO-M04-04` sind optionale Anschlussziele, keine stillschweigende Erweiterung.
Der endliche Rahmen wird dafür um 1 Arbeitspaket, 1 PR und höchstens 2 weitere
Quellenkandidaten auf 23/31/73 erweitert; dieser Schritt nutzt vorhandene
Curriculum-Dokumente und prüft keine neuen Produktquellen.

PR #366 ist auf `main` integriert: sieben aktuelle PR- und fünf Main-Workflows
erfolgreich, Squashcommit `7e09a5b557f5b5fe1c746a164d677cec205a56a1`.
Vollständiger Tree `5e6efedbbda9764d2681e1d9ab9846a848de4b7b` stimmt lokal und
auf `origin/main` überein; lokaler und Remote-Branch sind entfernt.

Die anschließende Quellenprüfung der SQL-Server-2022/2025-Releaseübersichten
fand dort keine Graph-Einträge. Sie hält ausdrücklich fest, dass die Abwesenheit
eines Eintrags keine Versionsparität belegt; für den Entwurf gilt weiterhin nur
die quellenbelegte Basis ab SQL Server 2017 plus die dokumentierten Graph-
Erweiterungen von SQL Server 2019. Dafür wurde die kumulative Arbeitsgrenze um
1 Arbeitspaket, 1 PR und bis zu 2 Quellenkandidaten auf 24/32/75 erweitert.
Zielbuilds, Editions-/Compatibility-Level-Grenzen, Demo und Runtime bleiben
offen.

PR #367 ist auf `main` integriert: sieben aktuelle PR- und fünf Main-Workflows
erfolgreich, Squashcommit `4d44ec7b9327c38a59cb39ebc6465bf267340c02`.
Vollständiger Tree `e45e6bbf7a69e1c1d1053da2b669ff94ed464099` stimmt lokal und
auf `origin/main` überein; lokaler und Remote-Branch sind entfernt.

Der nächste begrenzte Schritt entwirft statisch den festen Zwei-Kanten-Pfad,
beide äquivalenten Abfrageformen und die erwarteten Ergebnistripel. Dafür wird
die kumulative Arbeitsgrenze um 1 Arbeitspaket, 1 PR und höchstens 2 Quellen-
kandidaten auf 25/33/77 erweitert. Der Entwurf hat keine Demo-ID; ausführbares
SQL, Sicherheits-/Cleanupvertrag und Runtime bleiben spätere Gates.

PR #368 ist auf `main` integriert: sieben aktuelle PR- und fünf Main-Workflows
erfolgreich, Squashcommit `5902dbb714217c1ae9b971e770e09c931ef666ba`.
Vollständiger Tree `ada6bf79f41f49490b5c8a392263b027695a5bf3` stimmt lokal und
auf `origin/main` überein; lokaler und Remote-Branch sind entfernt.

Der nächste begrenzte Schritt prüft die konkrete `MATCH`- und Edge-INSERT-
Syntax anhand zweier Microsoft-T-SQL-Referenzen und ergänzt den statischen
Entwurf. Die kumulative Arbeitsobergrenze wird dafür um 1 Arbeitspaket, 1 PR
und bis zu 2 Quellenkandidaten auf 26/34/79 erweitert. Keine Demo-ID,
ausführbare SQL-Datei oder Laufzeitfreigabe.

## Autonomer Auftrag vom 26. Oktober 2026

Der neue menschliche Auftrag nimmt die priorisierten Entwicklungspunkte
schrittweise wieder auf. Er ersetzt frühere Pausen innerhalb dieses Umfangs;
fachliche Verträge, unabhängige Freigaben und Sicherheitsgrenzen bleiben bestehen.
Konsistente, relevant geprüfte Wellen werden regulär über einen Pull Request
(Änderungsantrag) nach `origin/main` integriert. Frühere datierte Aufträge unten
bleiben als historische Belege erhalten und erteilen keine zusätzlichen Laufrechte.

Die Reihenfolge lautet: Frameworkschutz und Abschluss, begrenzte Planerzwingung,
Lesepfade, Kerndemos, Abfragespeicherzuteilungen,
vollständiger Diagnosefall, vorhandene KI-Qualifikation, Deadlockvarianten,
Einfügungen auf der letzten Indexseite, Ressourcen, SQL-Server-2025-Ergänzungen,
Graph-/External Tables, Replay-/Providererweiterungen und gesonderte Infrastruktur.
KI bedeutet künstliche Intelligenz. Der aktive DGN-004-Plan bleibt auf
Standard-Planerzwingung und einen festen Hint-Kontrollzustand begrenzt.

Die QRY-002-Lehrnotiz zu impliziter Konvertierung, Datentyp- und
Collation-Mismatch ergänzt `LO-M03-01` mit synthetischen Beispielen. Sie
enthält kein neues Manifest oder Laufzeitclaim. Nach dem aktuellen
QRY-002-Offline-Update folgt QRY-003 zu halboffenen Datumsintervallen,
`BETWEEN`-Grenzen und Datentypgenauigkeit, anschließend RES-004 zu
konkurrierenden Abfragespeicherzuteilungen. Performanceaussagen benötigen
weiterhin passende Messung; die Lehrnotiz behauptet keinen Scan allein wegen
einer Konvertierung.

Die QRY-003-Lehrnotiz ergänzt `LO-M03-02` mit synthetischen Beispielen zu
halboffenen Intervallen und passenden Datentypgrenzen. Sie ist keine
Laufzeitqualifikation. Als nächster begrenzter Inhalt ist RES-004 vorgesehen.

Die RES-004-Lehrnotiz konkretisiert `LO-M06-07`: ein Grant-Wait muss an eine
noch nicht gewährte eigene Anforderung und den dazugehörigen aktuellen
`RESOURCE_SEMAPHORE`-Request gebunden sein. Sie ist keine neue Demo oder
Laufzeitqualifikation. Die ausführbare Konkurrenzprobe und ihr tatsächlicher
Wait-Nachweis bleiben offen; aktive Sessions allein belegen keinen Grant-Wait.

Der Offlinevertrag ergänzt nun synthetische Prüfungen für genau diese Bindung:
Session-/Request-ID, gemeinsamer Erfassungszeitpunkt, `RESOURCE_SEMAPHORE`,
`grant_time IS NULL`, positive Wartewerte und einen erteilten Grant derselben
Pool-/Semaphore-Kombination. Die gelieferten Zeilen sind unauthentifiziert;
kein Lauf, kein Kausalnachweis und keine Runtimequalifikation.

Die RES-004-Gegenprobe fand danach eine Lücke zwischen Lehrvertrag und
Offlineprüfer: Der Prüfer verlangte den wartenden Request und einen gewährten
Grant im selben Pool/Semaphore, wertete aber die dort ebenfalls geforderten
`waiter_count`-/`grantee_count`-Zähler nicht aus. Der Vertrag bindet diese
Zähler jetzt positiv an dieselbe Semaphore und denselben Erfassungszeitpunkt;
fehlende oder nicht-positive Werte bleiben `NOT_PROVEN`. 19 synthetische Tests
bestanden. Das authentifiziert keine Aufnahme und qualifiziert weder SQL noch
eine tatsächliche Konkurrenzprobe.

Für RES-001 bindet ein weiterer Offlinevertrag caller-supplied `THREADPOOL`-
Wait, passendes Run-Token und Scheduler-`work_queue_count` an einen gemeinsamen
Capturezeitpunkt innerhalb des Run-Fensters. `runnable_tasks_count` bleibt
separat sichtbar und genügt allein nicht als Worker-Nachweis. Das ist eine
statische Gegenprobe, keine bestätigte Worker-Erschöpfung oder Runtime-
Qualifikation; Laststeuerung, erfolgreicher Verbindungsabschluss und
unabhängiger Cleanup bleiben offen.

Der nächste begrenzte Ressourcenbaustein ist RES-003. Der
[Offlineprüfer](../../Tests/Static/res003_memory_signal_contract.py) bindet
ausschließlich caller-gelieferte `process_physical_memory_low`- und
`system_low_memory_signal_state`-Zustände an getrennte Vorher-, Druck- und
Erholungszeitpunkte. Buffer-Pool-Belegung, `RESOURCE_SEMAPHORE`, Kausalität und
authentische DMV-Herkunft werden dadurch nicht behauptet. Die rote RES-003-
Laufzeitprobe bleibt ohne dedizierte Wegwerfinfrastruktur,
High-Impact-Bestätigung, Kill-Switch sowie konkrete Setup-/Restore-/Cleanup-
Qualifikation gesperrt. Für diesen einen Offlinevertrag gilt seit der
Fortsetzungsanweisung vom 7. November 2026 die kumulative Planungsobergrenze
18 Arbeitspakete, 26 Pull Requests und 63 Quellen-/Testkandidaten; sie ist kein
Geld- oder Provider-Ausgabenlimit.

Die Lehrnotiz zu konkurrierenden Grants erklärt nun zusätzlich die getrennten
Scopes dieser Prozess- und Betriebssystemsignale und grenzt sie von
Buffer-Pool-Verdrängung und `RESOURCE_SEMAPHORE` ab. Das ist eine quellengebundene
Begriffsklärung; die rote Demo-, Mess- und Laufzeitqualifikation bleibt offen.
Für diesen Dokumentationsschnitt wurde am 7. November eine weitere begrenzte
Fortsetzung um ein Arbeitspaket, einen PR und zwei Quellen-/Testkandidaten
angesetzt: kumulativ höchstens 19/27/65, ohne Reset.

Die Detailprüfung von SQL Server 2025 `OPTIMIZED_SP_EXECUTESQL` ist im
[Delta-Review](SQL_SERVER_2025_DELTA_REVIEW.md) abgeschlossen. `QRY-004` qualifiziert keine parallele Compilation; die Funktion
bleibt daher für Aktivierung, Laufzeitdemo und Performanceclaim `DEFER`. Die
optionale Produktaussage kann eng abgegrenzt erklärt werden. Für diesen
quellengebundenen Dokumentationsschnitt gilt die am 7. November angesetzte
Fortsetzung um ein Arbeitspaket, einen PR und zwei Quellenkandidaten: kumulativ
höchstens 20/28/67, ohne Reset.

Die priorisierte Prüfung der CON-006-Deadlockvarianten wählt zuerst eine
Konversionsvariante als `PROPOSED`: Sie soll konkurrierende S→X-Upgrades derselben
Ressource vom vorhandenen gegenläufigen Zugriff auf zwei Ressourcen abgrenzen.
Umsetzung und tatsächlicher variantenspezifischer Konfliktgraph bleiben offen;
die Range-Variante bleibt wegen der Überschneidung mit CON-002 zurückgestellt.
Der [begrenzte Quellen- und Variantenvertrag](../../.ai/BACKLOG.md#5-con-006--conversion--und-range-deadlocks-als-optionale-varianten) führt die noch nötigen
Graph-, Opfer-, Gegenpart- und Cleanup-Nachweise auf.

Der getrennte Offline-Graphprüfer für den vorgeschlagenen Konversionsfall ist
implementiert und über den bestehenden Framework-Contracts-Workflow ausgewählt.
Elf synthetische Gegenproben bestehen. Geprüft werden caller-geliefertes
Deadlock-XML, genau zwei an Datenbank und SPIDs gebundene Prozesse, ein Opfer
und dieselbe konkrete Keylock-Ressource mit beiderseits gehaltenem `S` und
angefordertem `X`/`requestType="convert"`. Der anschließende Offline-
Capturevertrag verlangt zusätzlich übereinstimmende caller-gelieferte
Run-Token, `xml_deadlock_report`/`system_health`, genau ein Ereignis innerhalb
des expliziten Zeitfensters und einen zum Graphvictim passenden Fehler 1205
sowie Survivorstatus. Zusammen wurden 19 synthetische Testmethoden ausgeführt.
Graph, Quelle, Zeitgrenzen und Outcomes bleiben caller-geliefert und
unauthentifiziert; der Prüfer erzeugt keine Laufzeitevidenz. Die genaue
Darstellung auf beiden Zielbuilds bleibt empirisch zu prüfen; Demo-SQL,
Manifest und Runtimequalifikation wurden nicht geändert.

Der unabhängige Quellenreview fand einen P2 im Capture-Zeitparser: gültige
RFC-3339-Kleinschreibung und siebenstellige Bruchteile wurden abgelehnt,
Randzeitpunkte konnten eine ungefangene Ausnahme auslösen. Der Parser wurde
auf präzise Bruchteilvergleiche und ganzzahlige Offsetnormalisierung umgestellt;
synthetische Regressionen decken diese Fälle ab. Der unabhängige Review der
korrigierten Fassung fand keine offenen P1/P2 im Offlineumfang. Die offenen
Capture-Provenienz- und Engine-Qualifikationsgates bleiben getrennt.

Für `IDX-007` ergänzt eine kurze, quellengebundene Erläuterung den Lernpfad:
Sie trennt Last-Page-`PAGELATCH_EX` von I/O- und Transaktionssperren und
begrenzt die Aussage zu `OPTIMIZE_FOR_SEQUENTIAL_KEY`. Sie ist weder eine
Engpassdiagnose noch eine quantitative Vergleichsdemo; der faire Vergleich
und tatsächliche Wait-/Page-Nachweis bleiben offen.

Ein synthetisch geprüfter Offline-Vertrag bindet zusätzlich caller-supplied
`PAGELATCH_EX`-Waits an dieselbe Datenbank-/Datei-/Seitenadresse und denselben
Capturezeitpunkt, verlangt zwei verschiedene Sessions und Blattniveau sowie
eine separat gelieferte Rechtsaußen-Aussage. Dies ist statische
Konsistenzprüfung, keine authentifizierte SQL-Erfassung oder Qualifikation.
PR #420 ergänzt die [Vertragsprüfung](IDX007_OFFLINE_EVIDENCE_REVIEW.md),
trennt fehlenden Rechtsaußenbeleg (`NOT_PROVEN`) von einem expliziten
Gegenbeleg (`FAIL`) und bindet `sys.dm_os_waiting_tasks` sowie
`sys.dm_db_page_info` im Quellenregister. Der unabhängige Offline-Review vom
12. November 2026 fand nach der Timestamp-Korrektur keine offenen P1/P2 im
geprüften Vertrags-/Quellenumfang. Die unabhängige Seitenkettenauflösung, ein
fairer Vergleich und Laufzeitnachweise bleiben offen.

Die Teilnehmer-Generalprobe ist nicht durchgeführt. Für die neun im
[PRS-010-Plan](PRS_010_REHEARSAL_PLAN.md) ausgewählten Folien wurden Inhalt,
Notes und referenzierte Paketbestandteile am aktuellen Master byteweise mit dem
historisch geprüften Deck verglichen; die Planbindung ist aktualisiert. Das ist
keine neue PowerPoint-Render- oder Sichtprüfung am aktuellen Deck und kein
Teilnehmer- oder Lernwirksamkeitsbefund.

Der historische gemeinsame Rahmen vom 26. Oktober betrug höchstens 15
Arbeitspakete, 20 neue Pull Requests und 45 Quellenkandidaten einschließlich
Reviews, Tests und Wiederholungen; der 45er-Kandidatenstopp wurde erreicht.
Der menschliche Fortsetzungsauftrag vom 4. November erweitert additiv um höchstens
12 Kandidaten und drei Pull Requests, ohne Reset: kumulative Obergrenzen 15/23/57
(Arbeitspakete/Pull Requests/Kandidaten). Startverbrauch der Fortsetzung ist
1/19/45. Die Fortsetzung verfolgt höchstens zwei zusammenhängende Arbeitspakete
und checkpointet am dritten Kandidaten oder ersten Blocker. Token- und
Geldverbrauch sind unbekannt. Unveränderte grüne Prüfungen und Blocker lösen
keine neuen Versuche aus.
Ein stündlicher nativer Heartbeat dient ausschließlich als Leerlaufsicherung.
Bei aktiver Arbeit oder nicht handlungsfähigem Zustand beginnt er keine Arbeit.

**Erste Subwelle: vorhandene Framework-Evidenz abschließen.** PR301 ist integriert;
alle acht damaligen Main-Workflows sind erfolgreich. PR334 (Evidenzabschluss)
ist auf `bce4ec812ec5247e2e2afaa78fa74e0e5fac9ffd` in `main` integriert; die
zugehörigen eigenen Branches wurden entfernt. Der
[Eingabenachweis](FWK_002_FRAMEWORK_INPUT_REVIEW.md#nachträglicher-integrationsabschluss-vom-26-oktober-2026)
bindet die abgeschlossene Versionsmatrix. Keine erneuten SQL-Läufe oder Container
für diesen Dokumentationsschnitt.

**FWK-002-Erhaltung nach gescheiterter Erstmarkierung: begrenzt runtimequalifiziert.**
PR335 (finaler Head `7125d10`) und die integrierte Main-Version auf
`1f8c152ec9a8d8855d2eb3bee3e46842f9dc5786` bestehen die vorhandenen
Frameworkmatrizen auf SQL Server 2019, 2022 und 2025 einschließlich aller drei
eigenen Container-Cleanup- und Abwesenheitsprüfungen. Die Gegenproben decken
vollständig unmarkierten und teilmarkierten Zustand mit Sentinel ab, erhalten
Originalfehler und `FAIL_CLEANUP` und schließen mit markergeprüftem Folgeabbau.
Der erste Head-Lauf `40321050815` am Head `c28dcf1` blieb als historischer Fehler erhalten: Eine
fehlerhafte Test-Faultinjektion hatte den dynamischen Marker-SQL-String geöffnet
gelassen und verhinderte den Eintritt in den Produktions-CATCH. Die korrigierte
Headmatrix `40321858686` und Mainmatrix `40322492377` sind erfolgreich. Das
qualifiziert ausschließlich die Erhaltung in diesem Fehlerpfad. Es begründet
weder allgemeinen sicheren Wiederanlauf noch eine freigegebene manuelle
Entfernung. Die ursprüngliche Recoverygrenze bleibt bestehen. Menschliche
Teilnehmererprobung bleibt ein menschliches Gate; bei einem konkreten Blocker
wird die nächste unabhängig bearbeitbare Aufgabe verfolgt.

**DGN-004-Quellpaar- und Offline-Transportvorschnitt: statisch integriert.** Das [statische Quellpaar](../../Tests/Fixtures/DGN004_SourcePair/README.md)
überführt die freigegebenen R/H-Textvorlagen in zwei bytegenau geprüfte
SQL-Einzeiler. Reine Gegenproben prüfen Textdarstellungen, Offsets und
Hintposition. Der Offline-Transport ergänzt begrenzte Frame- und
XML-Wohlgeformtheitsprüfungen, einen caller-bound SQL-Ausschnitt und einen
direkten Runner mit beim Lesen begrenzten stdout-/stderr-Kanälen. Dies ist
kein ausführbares Demopaket und keine Build-, Plan-, Replay- oder
Laufzeitabnahme. SQL-Ausführung des Runners und die begrenzte Qualifikation auf
den beiden festgelegten Zielbuilds bleiben Folgearbeit.

PR338 ist auf Main `e5130c443eaf94f5e440208d38059d6cdb6719b5` integriert;
alle fünf Headprüfungen sowie die frischen Main-Läufe Framework `40328734818`,
Privacy `40328734514` und Cleanup `40328734569` sind erfolgreich, die eigenen
Branches entfernt. PR338 ergänzt zum bereits statischen R/H-Quellpaar und
Chunk-Decoder einen begrenzten Frame-Serializer/Parser. Der Offline-Ergebnisbinder
bindet Frames an separat erwartete Run/Rolle/Aufrufwerte, prüft wohlgeformtes
XML mit ShowPlanXML-Wurzel, validiert die engen sqlcmd-Eingaben vor Substitution
und enthält ein SQL-Transportfragment für einen caller-bound `plan_handle`.
Der DGN-Runner begrenzt beide Ausgabe-Kanäle beim Lesen; seine Prozessgegenproben
verwenden nur synthetische lokale Prozesse. SQL-Ausschnitt und Runner wurden
nicht gegen SQL Server ausgeführt. Ein Offline-Prüfer vergleicht caller-gelieferte
Identitätsrohwerte mit den registrierten M/S/T-Formen, prüft aber weder die
Vollständigkeit der Serverzeilen noch die Herkunft, Aktualität oder Zuordnung
eines `plan_handle`. Ohne diese Quellen-/Query-/Planbindung belegen die Helfer
weder die beabsichtigte aktuelle Ausführung noch Schema-/Runtimequalität oder
Engineidentität. SQL-ausgeführtes End-to-end Capture und Buildqualifikation
bleiben offen.

**DGN-004 statischer Annahmevertrag: lokal begrenzter und unabhängig geprüfter Source-only-Schnitt.** Ein reiner
Prüfer und synthetische Gegenproben bilden jetzt den aktiven
`CLASSICAL_FORCING_AND_HINT_CONTROL`-Umfang mit neun geordneten Aufrufen,
Kompilierungs-/Ausführungszuwächsen, Form-A-Tupeloracle aus den registrierten
ID-/Wertformeln, Force/Unforce-, Hint-, Identitäts- und Statusvorrang ab.
Offene Replay-Marker werden nicht als Eintritts- oder PASS-Gate verwendet.
PRs #516/#517 ergänzen die zuvor fehlenden Hint- und Identitätsgegenproben;
PR #518 behebt die unabhängigen P2-Befunde zu Force-Fehlerzählepochen und
Nullzähler nach Force. Der unabhängige Methoden-/Quellen-/Zuordnungs-/Transport-/
Messreview fand danach keine offenen P1/P2. Er belegt keine Runtime und ersetzt
nicht die noch offenen YELLOW-, Build-, Laufzeit- oder Demoqualifikationen. Alle Eingaben
des Prüfers sind caller-gelieferte Belege oder synthetische Fixturewerte; PASS
ist keine Attestation tatsächlicher Ausführung. Integrationsentscheidung und CI
sind mit dem nachstehenden Integrationsstand abgeschlossen; dieser
Statusabschnitt hält die fachlichen Aussagegrenzen fest.

PR [#355](https://github.com/gecompat/SQL_PerformanceSchulung/pull/355) wurde
am 2026-11-06 um 19:01:37 UTC gemergt. Die sechs ausgewiesenen PR-Prüfungen
`Validate ADV-006 and ADV-007`, `registry-integrity`, `contract`,
`Curriculum and repository privacy`, `validate` und `repository-governance`
bestanden; Integrationscommit ist
`f5d5aab22b2370588711da80272da3209f42f63c`. Damit ist der statische
Annahmevertrag integriert. Die unabhängige Methoden-/Quellen-/Zuordnungs-/
Transport-/Messfreigabe vor SQL war nach PR #355 noch offen; sie wurde durch
den unabhängigen Review vom 2026-11-12 abgeschlossen. PR #355 selbst enthielt
keine SQL-Ausführung, Buildqualifikation oder Demo-/Runtimefreigabe.

Der unabhängige DGN-004-Review vom 2026-11-12 ist in
[DGN_004_ACTIVE_SOURCE_REVIEW.md](DGN_004_ACTIVE_SOURCE_REVIEW.md) festgehalten.
PRs [#516](https://github.com/gecompat/SQL_PerformanceSchulung/pull/516),
[#517](https://github.com/gecompat/SQL_PerformanceSchulung/pull/517) und
[#518](https://github.com/gecompat/SQL_PerformanceSchulung/pull/518) integrieren
die Gegenproben und Fixes; alle vier Repositoryprüfungen je PR bestanden. Die
DGN-004-Statiksuite besteht unter Windows mit 67 Tests/1 POSIX-Skip und unter
Linux/WSL mit 68 Tests ohne Skip. Der Vorstartcheck fand jedoch fünf aktive,
nicht DGN-004 zugeordnete SQL-Server-Container mit gemeinsamer momentaner
Auslastung von rund 33 % CPU und 7,4 GiB Speicher. Das unabhängige Review
beurteilt die kontrollierte YELLOW-Last und Isolierung deshalb als nicht
nachgewiesen. Kein DGN-004-Container und keine Datenbank wurde gestartet oder
verändert; die übrigen Container wurden nicht berührt. Der exakte Lauf bleibt
bis zu einem belegbaren YELLOW-Preflight ausstehend.

Eine erneute rein lesende Containerinventur am 12. November 2026 fand weiterhin
fünf aktive, nicht DGN-004 zugeordnete SQL-Server-Container (2017, 2019, 2022
und zweimal 2025). Die Inventur hat keinen Container gestartet, gestoppt oder
verändert. Das YELLOW-Isolations-/Lastgate bleibt damit aktuell nicht erfüllt;
es wurde kein SQL- oder DGN-004-Lauf begonnen.

Eine Read-only-Aktualisierung am 14. November bestätigte dieselben fünf
fremden SQL-Container und den zusätzlichen Open-WebUI-Dienst. Ein einzelner
`docker stats --no-stream`-Snapshot zeigte 5,76 % CPU im 2022- und 15,06 % im
2025-Zielcontainer; weitere SQL-Container meldeten 0,78 %, 0,93 % und 1,16 %.
Das ist keine Last-/Reservequalifikation; beide Zielbuilds sind gleichzeitig
aktiv. Die vorhandenen DGN-004-Imagepins erfüllen das YELLOW-Gate nicht. Es
wurden keine Container verändert und kein DGN-004-SQL gestartet.

Der source-only-Schnitt ergänzt die vollständige DMV-Kandidatenaufzählung
nach Datenbank, Objekt, exaktem UTF-16-Modultext und registriertem Statement-
Offset, eine vollständige Frameprüfung und einen fail-closed Vorher-/Nachher-
Deltabinder. Plan- und SQL-Handles werden korrekt als 1–64 Bytes behandelt;
`varbinary(64)` ist eine Höchstlänge. Der direkte Runner und die synthetischen
Gegenproben zählen weiterhin gegen die bestehenden Obergrenzen von 100 SQL-
Batches und drei Metadatenbeobachtungen je Flush; kein Budget wird erweitert.
83 lokale DGN-004-Tests (ein POSIX-Skip), Framework-Integritätscheck,
Python-Kompilierung und ScriptDom-Syntaxparse für SQL Server 2019/2022/2025
bestanden und wurde mit PR #593 (`ee80eb2`) integriert. Der unabhängige Review
fand zunächst einen veralteten Backlogstatus (P2); nach Korrektur bestätigt er
keine weiteren P1/P2 im Quellfilter/Frame,
Handle-Längenvertrag, Runner oder Delta-Binder. Dies bleibt Source-only: kein SQL-Compile oder -Lauf, keine
Handle-Provenienz im ausgeführten Zustand und keine Runtimequalifikation.
Das YELLOW-Gate bleibt Voraussetzung für den nächsten Lauf.

**DGN-007-Import-Only-Worker: eine begrenzte lokale DGN-Importbeobachtung.**
Der [Importworker](DGN_007_IMPORT_USED_BYTES_PROBE_DESIGN.md#begrenzter-import-worker-als-quellkandidat)
verwendet das vorbereitete 27-Member-/Neuner-Eingangsprotokoll für drei frische
Linux-/CPython-3.12-Prozesse, lädt die festen Modulbytes über einen kontrollierten
MemoryFinder und bindet Import-`BEGIN`/`COMPLETE` an Member, Größe, SHA-256,
Eingang und Worker-Nonce. Elf synthetische lokale Linux-/CPython-3.12.3-Tests
prüfen die drei Sollsequenzen und gezielte falsche Imports, Bodytausch,
Reload/Alias, veraltete Receiptbindung sowie den offenen Pipe-Fall nach Leader-
Ende. stdout/stderr teilen beim Lesen 64 KiB plus höchstens ein Sentinelbyte.
Zusätzlich wurde genau ein lokaler Import-only-Lauf am 2026-11-04 gegen den
27-Member-Git-Blob-Snapshot `1587103e207897a0f3665143bd007812901950db`
ausgeführt: 3/3 Worker lieferten `OBSERVED_IMPORT_BYTES`, mit 8/1/3 Modulen.
SQL und Demoaufrufe wurden nicht ausgeführt. Die Probe lief unter Ubuntu
CPython 3.12.3; sie ist keine CI- oder DGN-Runnerabnahme. Profil-, Kanal-,
Prozessbaum-, Trust-, Cleanup-, SQL-, Acquisition- und Methodenfreigaben bleiben
offen. Alle Attestationsflags bleiben `false`.
Dieselbe begrenzte Import-only-Probe ist nun als Test im bestehenden
Ubuntu-/CPython-3.12-Harness-Source-Job enthalten: der Test bildet den
temporären 27-Member-Kandidaten aus den Git-Blobs des expliziten `HEAD` und
verwendet die vorhandenen Blob-, Gesamtbyte- und Deadlinegrenzen. Es entsteht
kein zusätzlicher Workflow oder Job; SQL- und Demoaufrufe bleiben ausgeschlossen.

## Auftrag vom 25. Oktober 2026: DGN-004 auf Standard-Planerzwingung und Hint-Kontrollzustand begrenzen

Der aktuelle Auftrag begrenzt DGN-004 (Planerzwingung) bei TSK-016
(gezielte Curriculum-Ergänzungen) auf klassische Planerzwingung über Standard-
Force/Unforce und einen festen Inline-Hint-Kontrollzustand. R ist Referenz ohne
Hint, H die getrennte Hint-Kontrolle. Nur Planung und statische CI (Continuous
Integration; automatisierte Integrationsprüfungen) im Pull-Request-Verfahren;
keine Umsetzung oder SQL-/Lab-Läufe. Übrige Verarbeitung pausiert.

Die [kanonische Registry](../../.ai/identity/registry.json) wählt bei TSK-016 für
DGN-004 über `active_plan` ausschließlich `classical_forcing_hint_control_plan`.
Die [abgeleitete aktive Planansicht](../../.ai/BACKLOG.md#aktiver-begrenzter-plan-klassische-planerzwingung-und-hint-kontrollzustand)
führt die neuen Abnahmekriterien. Klassisch bezeichnet die dokumentierte
Zwei-Argument-Standardschnittstelle und belegte Planverwendung, keine Aussage
über den internen Optimierungs-/Replay-Weg. Replay bedeutet Wiederverwendung
von Optimierungsschritten; Nutzung und Nichtnutzung werden hier nicht abgenommen.

Unverändertes R/H-Quellpaar, Form A und neun Nutzaufrufe je Build: R aufwärmen
(1/2), R-Force belegen (3), H binden (4), zweimal H-Force/Kontrollzustand (5/6),
erneut R-Force (7), H/R unforced abschließen (8/9). Kein R-Replay-Skript,
QueryCompilationReplay-Wert oder H-Nichtnutzungsmarker als Eintritts-/Erfolgsgate.
Vollständige Quellen-/Identitäts-/Plan-/Kontext-/Tupelbindung, aktuelle Erfassung,
strenger Kompilierungszuwachs +1, eigener regulärer Ausführungszuwachs und
Fehlerfreiheit bleiben Pflicht. H verlangt zusätzlich den vollständigen festen
Inline-Hint und keine fremde überschreibende Steuerung.

Ein späterer PASS (bestanden) gilt ausschließlich für
CLASSICAL_FORCING_AND_HINT_CONTROL. H bleibt CONTROL_ONLY (nur Kontrollzustand
belegt), ohne empirische Replay-Abschaltung oder isolierte kausale Hintwirkung.
Gesamt-PASS im engeren Umfang erst nach allen neun Aufrufen und sicherer
Bereinigung auf beiden Builds. Fehlende aktive Pflichtbelege bleiben Nichtabnahme;
Vertrags-/Bereinigungsfehler dürfen nicht durch die Begrenzung verdeckt werden.

Replay-Vergleich samt offenen Marker-Gates, alter Ein–Aus–Ein-/Gleichidentitäts-
vergleich, erweiterte Deaktivierungssignatur, gezielte Fehler-/Fallback-Demo,
gespeicherte Query-Store-Hints und 2019-Qualifikation sind zurückgestellt.
Frühere FAIL-/NOT_PROVEN-Befunde und Quellen-/Planstände unverändert erhalten.
Die offenen Replay-Gates blockieren diesen engeren Aussageumfang nicht und
bleiben für spätere Erweiterungen zwingend. Die [Quelleneinordnung](../Research/SOURCE_REGISTER.md#dgn-004-begrenzung-auf-standard-planerzwingung-und-hint-kontrollzustand-vom-25-oktober-2026)
trennt die Abnahmeumfänge; keine zweite Planungsliste.

Unverändert zwei eigene sequenzielle Container für 2022/16.0.4265.3 und
2025/17.0.4075.5, 900 Sekunden gemeinsames reguläres Budget plus je 60 Sekunden
Cleanup und alle bisherigen Text-/Transport-/Eigentums-/Ressourcengrenzen.
Vor Umsetzung unabhängigen Review des engeren Quellen-/Identitäts-/Transport-/
Mess-/Statusvertrags und statische Gegenfälle abschließen; diese Freigabe ist
noch offen. Danach neuer ausdrücklicher Umsetzungs-/Laufauftrag. Tatsächliche
Build-/Text-/Planqualifikation bleibt spätere Pflicht. Die folgenden älteren
Abschnitte sind historische Befunde und Pläne; ihre Replay-Abnahme wird nicht
zum Erfolg oder zur aktuellen Eintrittsbedingung umgedeutet.

## Auftrag vom 25. Oktober 2026: DGN-004-Quellenklärung aufnehmen

Der vorausgehende Quellenklärungsauftrag dokumentierte bei TSK-016 (gezielte Curriculum-Ergänzungen)
die Quellenklärung für DGN-004 (Planerzwingung). R ist Referenz ohne Hint, H die
Negativkontrolle mit festem Abschalthinweis; Replay bedeutet Wiederverwendung
von Optimierungsschritten. Nur Dokumentation und statische CI (Continuous
Integration; automatisierte Integrationsprüfungen) im Pull-Request-Verfahren;
keine Umsetzung oder SQL-/Lab-Läufe. Übrige Verarbeitung pausiert.

Die [kanonische Quellenklärung](../../.ai/identity/registry.json) steht bei TSK-016
unter `rh_marker_gate_source_clarification_result`; die [abgeleitete Detailansicht](../../.ai/BACKLOG.md#quellenklärung-der-offenen-rh-marker-gates)
und die [Quelleneinordnung](../Research/SOURCE_REGISTER.md#dgn-004-quellenklärung-der-marker-gates-vom-25-oktober-2026)
führen die technische Evidenz und deren Grenzen. Herstellerstand b6fe4934643919b28ddea54ad04c66ff1b2a82d1
erneut gebunden: allgemeiner Funktions-/Hintumfang ab 2022 einschließlich 2025
ist dokumentiert. Dies ist kein aktueller Marker-Nutzungsnachweis.

Beide Gates bleiben für 2022/16.0.4265.3 und 2025/17.0.4075.5 offen.
QueryCompilationReplay = 1 bleibt positiver Quellenkandidat. Das optionale
Ganzzahlattribut besitzt im Hersteller-Schema keine Zustandswerttabelle; für H
fehlt ein qualifizierter beobachtbarer Nichtnutzungszustand. 0, Abwesenheit,
Hint, Skriptvorhandensein, fehlender Fehler oder Kompilierungszuwachs ersetzen
die aktuelle Nutzungs-/Nichtnutzungssemantik nicht. Abwesenheit verlangt einen
eigenständigen Vollständigkeits- und Bedeutungsnachweis des Erfassungswegs.

Öffentlich geprüfte Quellen schließen diese Lücke nicht; keine Behauptung einer
vollständigen Recherche oder fehlender Featureunterstützung in 2025. Zusätzliche
Buchspur nicht im relevanten Originalvolltext zugänglich und nicht als technische
Evidenz verwendet. Keine neue empirische Beobachtung oder unabhängige Freigabe.
CONTROL_ONLY (nur Kontrollzustand belegt) bleibt Teilbefund, der Vergleich ohne
Markerabnahme NOT_PROVEN (nicht nachgewiesen), soweit kein höherer Fehlerstatus
greift. Die Aussagegrenze zur isolierten kausalen Hintwirkung bleibt erhalten.

Quellpaar, Markerprobenplan, Abnahmekriterien, Mess-/Statusvertrag und sämtliche
Budgets unverändert: neun Nutzaufrufe je Build, zwei eigene sequenzielle Container,
900 Sekunden gemeinsam plus je 60 Sekunden Cleanup. Unabhängige Marker-, Quellen-/
Identitäts-/Transport-/Mess-/Statusfreigaben und tatsächliche Buildnachweise
bleiben offen. Erst danach neuer ausdrücklicher Umsetzungs-/Laufauftrag im
gewählten Gesamtrahmen; keine alte Lauf- oder Telemetriefreigabe wird aktiviert.
Frühere Befunde und Pläne bleiben erhalten.

## Auftrag vom 25. Oktober 2026: DGN-004-Markerprobenreview dokumentieren

Der vorausgehende Dokumentationsauftrag erfasste bei TSK-016 (gezielte Curriculum-Ergänzungen)
den Prüfbefund für DGN-004 (Planerzwingung). R ist Referenz ohne Hint, H die
Negativkontrolle mit festem Abschalthinweis. Replay bezeichnet Wiederverwendung
von Optimierungsschritten. Nur Dokumentation und statische CI (Continuous
Integration; automatisierte Integrationsprüfungen) im Pull-Request-Verfahren;
keine Umsetzung oder SQL-/Lab-Läufe. Übrige Verarbeitung pausiert.

Der [kanonische Prüfbefund](../../.ai/identity/registry.json) steht bei TSK-016
unter `rh_marker_probe_review_result`; die [abgeleitete Detailansicht](../../.ai/BACKLOG.md#prüfbefund-zum-rh-markerprobenplan-und-zur-hintwirkung)
führt Ergebnis und Aussagegrenze. Im konkret geprüften Beobachtungs-/Abnahmevertrag
kein neuer konkreter Widerspruch zu den bestehenden Text-, Mess-, Status-,
Sequenz- und Budgetverträgen festgestellt. Dies ist keine unabhängige Methoden-
freigabe, Ausführungsreife oder Laufzeit-/Demoabnahme.

Ein späterer PASS (bestanden) würde die unabhängig freigegebenen beobachteten
Nutzungs-/Nichtnutzungszustände der getrennten R/H-Abfragen belegen. R/H haben
verschiedene Identitäten und eigene Zielpläne; für H ist ein gespeichertes
Replay-Skript keine Voraussetzung. Daraus folgt als methodische Aussagegrenze:
keine isolierte kausale Hintwirkung und keine reversible Abschaltung derselben
query_id nachgewiesen. Die dokumentierte Hintbedeutung bleibt quellenbasiert.
Keine zusätzliche Gegenfaktualprobe oder Kontrollreihe in den Rahmen aufnehmen.

Positive R-Markersemantik und beobachtbarer H-Nichtnutzungszustand bleiben für
2022/16.0.4265.3 und 2025/17.0.4075.5 unabhängig zu klären. Abwesenheit trägt
nur mit vorab belegter vollständiger Nutzungskennzeichnung und geklärter
Nichtnutzungsbedeutung; sonst höchstens CONTROL_ONLY (nur Kontrollzustand belegt).
Der Vergleich bleibt bei fehlender Evidenz NOT_PROVEN (nicht nachgewiesen),
soweit kein höherer Fehler-/Bereinigungsstatus greift. Die [Quelleneinordnung](../Research/SOURCE_REGISTER.md#dgn-004-markerprobenreview-und-hintwirkung-vom-25-oktober-2026)
trennt Quellenbefund und Inferenz aus dem Versuchsaufbau.

Quellpaar, rh_marker_probe_plan, übrige Pläne, Abnahmekriterien und Mess-/Status-
vertrag unverändert: neun Nutzaufrufe je Build, zwei eigene sequenzielle Container,
900 Sekunden gemeinsames reguläres Budget plus je 60 Sekunden Cleanup. Keine
neue Telemetrie, Kalibrierung oder Budgetaddition. Unabhängige Quellen-/Identitäts-/
Transport-/Mess-/Statusfreigaben und tatsächliche Buildnachweise bleiben offen.
Erst danach neuer ausdrücklicher Umsetzungs-/Laufauftrag; alte Freigaben werden
nicht wiederaufgenommen. Frühere Befunde und Pläne bleiben erhalten.

## Auftrag vom 25. Oktober 2026: Begrenzte DGN-004-Markerprobe planen

Der Planungsauftrag vom 25. Oktober 2026 plante bei TSK-016 (gezielte Curriculum-Ergänzungen) für
DGN-004 (Planerzwingung) eine begrenzte R/H-Markerprobe. R ist Referenz ohne Hint,
H die Negativkontrolle mit festem Abschalthinweis. Replay bedeutet Wiederverwendung
von Optimierungsschritten bei der Kompilierung. Nur Dokumentation und statische
CI (Continuous Integration; automatisierte Integrationsprüfungen) im bestehenden
Pull-Request-Verfahren; keine Umsetzung oder SQL-/Lab-Läufe. Die übrige
Verarbeitung bleibt pausiert, alte Laufrechte werden nicht wiederaufgenommen.

Der [kanonische Vertrag](../../.ai/identity/registry.json) steht unter
`artifacts.TSK-016.candidates[DGN-004].rh_marker_probe_plan`; die
[abgeleitete Detailansicht](../../.ai/BACKLOG.md#begrenzte-rh-markerprobe-für-nutzung-und-nichtnutzung)
führt denselben ergänzenden Beobachtungs-/Abnahmevertrag. Quellpaar, Form A und
Neun-Aufruf-Folge bleiben unverändert: R aufwärmen (1/2), R-Nutzung (3), H binden
(4), zweimal H-Nichtnutzung (5/6), erneut R-Nutzung (7), H/R unforced abschließen
(8/9). Höchstens zwei eigene Container, sequenziell einer je festgelegtem Build,
und 900 Sekunden gemeinsames reguläres Budget plus je 60 Sekunden Cleanup.
Keine zusätzliche Kalibrierungsrunde oder Addition mit alten Probenbudgets.

Abnahme getrennt für 2022/16.0.4265.3, Developer/Linux, Compatibility Level 160,
und 2025/17.0.4075.5, Enterprise Developer/Linux, Compatibility Level 170.
Aktuelle vollständige Plan-/Text-/Kontext-/Query-/Tupelbindung und strenger
Kompilierungszuwachs +1 bleiben Pflicht. Markerpräsenz, Rohwert und XML-Pfad
(XML: Extensible Markup Language; strukturiertes Planformat) bleiben je aktueller
Kompilierung erhalten; keine Umdeutung von Abwesenheit zu 0.

Vor Umsetzung unabhängig freigeben: tatsächliche erfolgreiche R-Nutzungssemantik
und beobachtbaren H-Nichtnutzungszustand je Build und Erfassungsweg. Beide Gates
bleiben offen. QueryCompilationReplay = 1 ist nur ein Kandidat; ein Muster aus
R/H-Werten allein begründet seine Bedeutung nicht. Fehlender H-Marker trägt nur
dann eine Nichtnutzungsregel, wenn vorab unabhängig nachgewiesen ist, dass dieser
Erfassungsweg jede tatsächliche Nutzung zwingend markiert und Abwesenheit am
aktuellen Zielstatement Nichtnutzung bedeutet. Solange das fehlt, höchstens
CONTROL_ONLY (nur Kontrollzustand belegt), kein empirischer Abschaltungsbeweis.

PASS (bestanden) je Build erst mit beiden positiven R- und beiden belegten
H-Gegenphasen, allen neun Aufrufen und vollständiger Bereinigung; Gesamt-PASS
nur für beide Builds. NOT_PROVEN (nicht nachgewiesen) bleibt bei fehlender
Semantik/Evidenz; FAIL (belegte Vertragsverletzung) und FAIL_CLEANUP
(Bereinigung fehlgeschlagen) haben Vorrang. Ohne Freigabegates kein Start,
Zustand nicht ausgeführt. Die [Quelleneinordnung](../Research/SOURCE_REGISTER.md#dgn-004-markerprobenplan-vom-25-oktober-2026)
begründet die offenen Grenzen. Neuer ausdrücklicher Auftrag für spätere Umsetzung
und Läufe erforderlich; dieser Plan ist keine unabhängige Freigabe oder
Laufzeit-/Demoabnahme. Bisherige Befunde und Pläne bleiben erhalten.

## Auftrag vom 24. Oktober 2026: DGN-004-Markerbefunde aufnehmen

Der Auftrag vom 24. Oktober 2026 dokumentierte bei TSK-016 die DGN-004-Quellenbefunde zur
positiven R-Markersemantik und zum beobachtbaren H-Gegenvertrag. R ist Referenz
ohne Hint, H die Negativkontrolle mit festem Abfragehinweis. Nur Dokumentation
und statische CI (Continuous Integration; automatisierte Integrationsprüfungen)
im bestehenden Pull-Request-Verfahren. Keine Umsetzung, Demotests oder SQL-/Lab-
Läufe; übrige Verarbeitung pausiert. Frühere Ausführungsfreigaben und Laufbudgets
werden nicht wiederaufgenommen.

Der [kanonische Entwurf](../../.ai/identity/registry.json) steht bei TSK-016 unter
`hint_negative_control_plan`. Die [abgeleitete Planansicht](../../.ai/BACKLOG.md#gesonderte-hint-negativkontrolle-mit-getrennten-abfrageidentitäten)
und die [Quelleneinordnung](../Research/SOURCE_REGISTER.md#dgn-004-r-markersemantik-und-h-gegenvertrag-vom-24-oktober-2026)
führen dieselben Identitäts-, Nachweis- und Ausführungsgrenzen.

Der neue [Marker-/Gegenvertragsbefund](../../.ai/BACKLOG.md#r-markersemantik-und-beobachtbarer-h-gegenvertrag)
steht kanonisch unter `rh_replay_marker_review_result`. Beide Gates bleiben für
2022/16.0.4265.3 und 2025/17.0.4075.5 offen. QueryCompilationReplay = 1 ist
weiterhin nur ein Quellenkandidat für tatsächliche Replay-Nutzung, also die
Wiederverwendung von Optimierungsschritten. Das Hersteller-Schema nennt eine
optionale Ganzzahl ohne Zustandswerttabelle; 0 oder Abwesenheit sind kein
freigegebener Aus-Zustand. Gespeichertes Skript und Erzwingungsanforderung sind
keine aktuelle Nutzungskennzeichnung.

Der feste H-Hint ist dokumentierte Abschaltkontrolle; mit frischer Kompilierung,
eigener klassischer Erzwingung und vollständigen Tupeln höchstens CONTROL_ONLY
(nur Kontrollzustand belegt). Für einen beobachteten H-Gegenbeleg fehlt weiterhin
die unabhängig geklärte Nichtnutzungssemantik. Fehler 8675 und die zusätzliche
2022-Ereignisliste zu opt_replay_exception_info betreffen gescheiterten Replay;
ausbleibende Fehler beweisen weder Nutzung noch Nichtnutzung. Keine neue
Ereignissession oder Ersatztelemetrie ist autorisiert.

Der empirische Vergleich bleibt NOT_PROVEN (nicht nachgewiesen), soweit kein
höherer Fehlerstatus greift. Quellen-/Textpläne, Abnahmekriterien, Mess-/Statusvertrag,
neun Nutzaufrufe, zwei eigene Container und sämtliche bisherigen Budgets bleiben
unverändert. Unabhängige Freigabe und tatsächliche Build-/Erfassungsnachweise
bleiben offen; dieser Review liefert keine Laufzeit- oder Demoabnahme.

Der vorausgehende [lesende Prüfbefund](../../.ai/BACKLOG.md#lesender-prüfbefund-zum-rh-quellpaar-und-textvertrag)
steht kanonisch unter `rh_source_text_review_result`. Quellpaar, endlicher Textvertrag
und Abnahmekriterien sind im konkret geprüften Umfang dokumentarisch schlüssig;
kein weiterer konkreter Widerspruch festgestellt. Quellen-/Spaltenbezüge, einziger
terminaler Hint-Unterschied und rechnerische Tupelerwartung passen zum Aufbau.
Die erwarteten Textdarstellungen stammen aus der Quelle; Erstzuordnung und
Darstellungswahl ersetzen keinen aktuellen Ausführungsnachweis oder Beleg für
wiederverwendete Optimierungsschritte. Die Sonderregel für erste
Bindungen in Aufrufen 1/4 erlaubt keinen erfundenen Null-Kompilierungszähler.

Der Review aus demselben Arbeitskontext ist keine unabhängige Freigabe. Tatsächliche
Darstellungen, Byteoffsets, Beobachtbarkeit und positive R-/beobachtete H-Replay-
Kennzeichnung (Wiederverwendung von Optimierungsschritten) auf beiden Zielbuilds
bleiben offen. Aktive Quellvorlagen/Pläne,
Abnahmekriterien, Mess-/Statusvertrag und Laufbudgets bleiben vollständig unverändert.
Kein zusätzlicher Lauf oder Ersatzablauf ist autorisiert.

Der [konkrete Quellen-/Textentwurf](../../.ai/BACKLOG.md#geplantes-vollständiges-rh-quellpaar-und-begrenzte-textzuordnung)
steht kanonisch unter `rh_source_text_plan`. Er legt zwei vollständige
CREATE-PROCEDURE-Quellwerte im eigenen Schema dgn004 fest. Beide verwenden die
unveränderte synthetische Form A; ausschließlich H erhält den terminalen Hint.
Die Vorlagen bestehen je aus einer ASCII-Zeile (7-Bit-Zeichensatz) ohne Kommentare
oder Zeilenumbrüche;
Bytepositionen und Offline-Prüfsummen binden die Quellen, keine Engine-Ausführung.

M bezeichnet den vollständigen Modultext, S dessen Nutzstatement mit Semikolon,
T nur denselben Text ohne letztes Semikolon. Modul-/Cachebatch müssen M entsprechen;
Cache-, Query-Store- und Planstatement dürfen ausschließlich S oder T entsprechen.
Die Erstzuordnung muss Quelle, eigenes Objekt, Kontext, Abfrage-/Textkennung und
aktuellen Plan gemeinsam belegen. Erst danach die je Ansicht gewählte Darstellung
versiegeln und unverändert fortführen; keine freie Normalisierung oder Neubindung.
Ein unbekanntes wohlgeformtes Engine-Format bleibt NOT_PROVEN (nicht nachgewiesen),
eine positiv belegte Vertragsverletzung FAIL; Bereinigungsfehler haben Vorrang.

Die Quellenlücke ist als Planungsvorlage geschlossen. Unabhängige fachliche Freigabe,
Überführung in ausführbare Quellen und tatsächliche M/S/T-/Offsetqualifikation auf
2022/16.0.4265.3 und 2025/17.0.4075.5 bleiben offen. Positive R-/beobachtete
H-Replay-Kennzeichnung ist weiterhin gesondert nachzuweisen. Neun Nutzaufrufe,
zwei Container, Mess-/Statusvertrag und Laufbudgets unverändert; keine Kalibrierung
oder Umsetzung durch diesen Plan autorisiert.

Der [vorausgehende Quellenbefund](../../.ai/BACKLOG.md#rh-abfrageform-und-engine-textzuordnung)
unter `rh_query_text_review_result` bleibt mit Basis PR325 erhalten. Er stellte
die damalige Quellenlücke und fehlende Erstzuordnung fest; der neue Entwurf liefert
die vollständigen Planungsvorlagen und begrenzt die Darstellungsauswahl. Der damalige
Review und die jetzige Planung ersetzen weder unabhängige Freigabe noch Buildnachweise.

Der vorherige [lesende Prüfbefund](../../.ai/BACKLOG.md#lesender-prüfbefund-zum-präzisierten-mess--und-statusvertrag)
steht bei TSK-016 unter `hint_evidence_status_review_result`. Beide vorigen
Präzisierungslücken sind dokumentarisch behoben; im geprüften Kompilierungs-/
Statusvertrag wurde kein weiterer Widerspruch festgestellt. Dieser damalige
Review änderte den Plan nicht; die aktuelle Ergänzung begrenzt
nur seine Quelltext-/Darstellungsabnahme. Messgrenzen und Ergebnisvorränge bleiben
unverändert. Diese Einordnung ist keine unabhängige Methodenfreigabe und keine
technische Qualifikation der Builds
2022/16.0.4265.3 oder 2025/17.0.4075.5. Quelltext-, Marker-/Gegenvertrags-,
Zuordnungs-/Transport- und Laufzeitgates bleiben offen; kein zusätzlicher Lauf
oder Kontroll-only-Ersatzablauf ist autorisiert.

Der vorausgehende lesende [Prüfbefund](../../.ai/BACKLOG.md#prüfbefunde-zur-gesonderten-hint-negativkontrolle)
steht kanonisch unter `hint_negative_control_review_result`. Im aktiven Plan
benennt `compilation_evidence_contract` ausdrücklich
`sys.query_store_query.count_compiles` je festgebundener eigener query_id.
Vorhermessung B0 nach bestätigtem Force, danach eigene sp_recompile-Markierung,
genau ein Nutzaufruf, vollständige Erfassung, budgetierter Flush und Nachhermessung
B1. R/H und Planstatistik getrennt; genau +1 ist eine strenge Abnahmebedingung,
keine allgemeine Herstellergarantie. Fehlende Daten oder unbekannte Zählerepoche
allein bleiben NOT_PROVEN (nicht nachgewiesen).

`outcome_precedence` trennt fehlende Evidenz von positiv belegter falscher oder
veralteter Zuordnung: Letztere ist FAIL (Vertragsverletzung). Der Schlussstatus
folgt FAIL_CLEANUP (Bereinigung fehlgeschlagen) vor FAIL vor NOT_PROVEN vor PASS;
alle Ursachen bleiben erhalten. CONTROL_ONLY bleibt Teilbefund und kann keinen
Gesamterfolg oder H-Ersatzablauf erzeugen. Beide Präzisierungen brauchen vor
Umsetzung unabhängige Freigabe; Marker-, Identitäts- und Versionsgates bleiben offen.

Referenz R ohne Hint und Kontrolle H mit dauerhaftem terminalem Inline-Hint werden
in zwei getrennten eigenen Prozeduren auf demselben synthetischen Aufbau geführt.
Jeweils eigene object_id, query_id und Force-Ziel-plan_id; kein Hintwechsel innerhalb
einer Identität und keine Querzuordnung über Hashes. Query Hints sind laut Hersteller
nicht Teil des QueryHash. Vollständige Texte, Kontext, Planrollen, Tupel und frische
Kompilierung/Ausführung bleiben deshalb gemeinsam Pflicht.

Geplant sind nur Form A mit 529 Datenzeilen und 768 vollständigen Ergebnistupeln
sowie höchstens neun Nutzaufrufe je Version: zwei R-Aufwärmaufrufe, positive R-Phase,
H-Aufwärmen, zwei H-Gegenphasen, erneut positive R-Phase und zwei unforced Abschlüsse.
Standard-Force mit zwei Argumenten; keine zusätzliche Deaktivierungsanforderung.
R/H haben unterschiedliche Identitäten; die Folge behauptet keine reversible
Abschaltung derselben query_id und ersetzt den alten Ein–Aus–Ein-Plan nicht.

Ein Quellen-/Kontrollbeleg bleibt von unabhängig beobachteter Replay-Nutzung
(Wiederverwendung von Optimierungsschritten bei Kompilierung) getrennt.
CONTROL_ONLY bedeutet nur Kontrollzustand belegt; es ist kein empirischer Replay-
Abschaltungsnachweis. Positive R-Marker und H-Gegenvertrag bleiben für
2022/16.0.4265.3 und 2025/17.0.4075.5 vor Umsetzung unabhängig zu klären.
Unbekannte QueryCompilationReplay-Werte, Abwesenheit oder Zeitunterschiede genügen
nicht. Der Quellenkonflikt und die bisherigen Reviews aus PR320/PR321 bleiben erhalten.

Späterer gesonderter Rahmen: höchstens zwei eigene Container insgesamt, sequenziell,
neun Nutzaufrufe je Version und 900 Sekunden gemeinsame reguläre Zeit plus je
60 Sekunden abschließendes Cleanup. Eigentum, Plantransport, Ergebnisse, Abbruch
und Bereinigung bleiben vollständig zu prüfen. Alter und neuer Plan dürfen nicht
automatisch nacheinander laufen oder ihre Budgets addieren. Neue Umsetzung und
Läufe erfordern nach Methodenfreigabe einen ausdrücklichen Auftrag für den gewählten
Schnitt; keine sonstige Verarbeitung oder Automation wird wiederaufgenommen.
Der [bisherige Zuordnungs-/Erfassungsplan](../../.ai/BACKLOG.md#kombinierte-planzuordnung-und-begrenzte-synthetische-replay-probe)
bleibt unverändert mit seinen eigenen offenen Gates maßgeblich.

## Erhaltene abgeschlossene Schnitte

OPT-007 (Ad-hoc-Plancache; Zwischenspeicher spontan formulierter Abfragen)
ist im begrenzten Vollplanschnitt über
[PR313](https://github.com/gecompat/SQL_PerformanceSchulung/pull/313) in Main
`4bab78cc321970c014784602f8ba068e38efd70d` integriert: 51 erfolgreiche
PR-Prüfungen und 49 erfolgreiche Main-Prüfungen; die im
[kanonischen Eintrag](../../.ai/identity/registry.json) gebundenen lokalen
Versions-/Gegenfall-/Bereinigungsnachweise bleiben erhalten. Alle drei eigenen
lokalen Prüfcontainer wurden entfernt. Das ist keine Freigabe weiterer
OPT-007-Themen. CON-005 (Schemasperren) bleibt über
[PR310](https://github.com/gecompat/SQL_PerformanceSchulung/pull/310) im
früheren begrenzten Schnitt integriert. Andere Arbeiten bleiben pausiert.

## Historische Fortsetzungen und zurückgestellte Arbeiten

Bei Eingang dieses Auftrags war PR301 (Pull Request; Änderungsantrag für die
vollständige Frameworkeingabeprüfung) bereits in Main
`a0773b7c7c07a3daea9a92ccd9c29f437717e79d` integriert und der lokale Main
synchronisiert; die vorher zugelassene frische Main-Versionswelle war bereits
ausgelöst. Ihre abschließende Ergebnisaufnahme, der vorbereitete getrennte
Dokumentationsabschluss und die Bereinigung des Branches
`codex/fwk002-input-validation` sind jetzt zurückgestellt. Laufende mutierende
Prüfungen werden nicht abgebrochen. Neue Läufe oder Wiederholungen werden nicht
gestartet. Vor einer ausdrücklich beauftragten Wiederaufnahme sind die
vorhandenen Ergebnisse und der tatsächliche Ressourcenstand zu prüfen; alte
Resultate oder vorbereitete Dokumentation gelten nicht als abgeschlossener
Arbeitsstand. Die privaten Quellen-, Ergebnis- und Ressourcenrecords bleiben
erhalten. Die folgenden Wiederaufnahmeabschnitte beschreiben den früheren Auftrag.

## Wiederaufnahme vom 22. Oktober 2026: Eigentumsprüfungen zuerst

Der menschliche Auftrag autorisiert die vollständige Korrektur aller 22
Cleanup-Eigentumskandidaten einschließlich Tests, Dokumentation und Integration
per Pull Request nach `origin/main`, danach priorisierte autonome Folgearbeit.
Der historische Stopp unten ist aufgehoben; keine Automation wurde aktiviert.

Die bestätigte Fehlerklasse in allen 22 Cleanupquellen ist über
[PR295](https://github.com/gecompat/SQL_PerformanceSchulung/pull/295) in Main
`dd733100ebc0bfd63846b39c3610b7e945715586` abgeschlossen. Cleanup bedeutet
Aufräumen; FWK-002 bezeichnet den Schutzvertrag für synthetische Testdatenbanken.
Fehlende Marker werden ausdrücklich abgewiesen, vollständige Werte binär und
mit exakter Bytelänge verglichen. DGN-005 (gezielte Ereigniserfassung) prüft
zusätzlich vor Änderungen seiner Ereignissitzung.

Unabhängiger Sicherheitsreview, neun reine Testmethoden und betroffene statische
Vertragsprüfungen sind abgeschlossen. Am Änderungsstand bestanden 82 Prüfungen,
am frischen Main 80; je 54 SQL-Matrixjobs einschließlich ihrer 54 erfolgreichen
Abbauschritte. Der neue Eigentumsworkflow bestand auf SQL Server 2019, 2022 und
2025 jeweils alle 22 Quellen zweimal: je Welle 132 Profile und 3960 Negativfälle.
Es gab keine manuellen Wiederholungen. Die vollständige Baumübernahme, lokale
Main-Synchronisation und Entfernung des eigenen lokalen sowie Remote-Branches
sind bestätigt. Eine zeitweise widersprüchliche Statusanzeige wurde bis zum
vollständig erfolgreichen Checkabschluss abgewartet.

Alle sieben eigenen lokalen Container sind unabhängig abwesend; kein ungeklärter
Ressourcenbestand. Quellenstände und Fehlversuche bleiben erhalten. C3 besitzt
eine dokumentierte Rohquellenlücke und ist kein Qualifikationsbeleg. Beim
DGN-007-Rückfall (zeitlich begrenzter Diagnosefall) klärte C9 ausschließlich eine
falsche Erwartung der Prozedurbytes: vollständig restauriertes `CREATE` statt
erwartetem `ALTER`. C10 korrigierte die exakte Sollfolge und bestand zweimal
alle 30 Negativfälle sowie positive und wiederholte Rückfälle mit Gegenproben.

An der ursprünglichen harten Grenze C8 wurde angehalten. Der Mensch genehmigte
ausdrücklich zwei weitere Quellenstände und zwei Container; kumulativ zehn
Kandidaten und sieben lokale Container, ohne Zählerreset. Je Parentlauf galten
1800 Sekunden plus einmal 90 Sekunden für den Abbau. Keine Ports, Mounts,
Downloads oder Host-SQL. Ein Verantwortlicher und ein unabhängiger Reviewer
prüften Quellen, Tests, Aufruf und Ergebnis. Modell-/Tokenverbrauch bleibt
unbekannt. Die reservierten zwei Integrationswellen mit zusammen 108 SQL-Jobs
sind vollständig verbraucht und abgeschlossen.

Die Korrektur zehn weiterer Einrichtungsskripte ist über
[PR297](https://github.com/gecompat/SQL_PerformanceSchulung/pull/297) in Main
`44f12b4797c7f492fabc5706f9bf8d03d9a739bb` integriert. Die vollständige
Eigentumsprüfung steht jetzt vor der ersten Konfigurationsänderung. Lokal auf
SQL Server 2025 bestanden zehn alte Konfigurationsverletzungen und zweimal alle
zehn korrigierten Quellen mit 620 Negativfällen, positiven Einrichtungen und
wiederholten Cleanups. Beide eigenen lokalen Container sind unabhängig abwesend;
der frühere Fehler im Testaufbau bleibt dokumentiert. Am Änderungsstand bestanden
alle 24 SQL-Jobs und ihre 24 Abbauschritte; der neue Workflow prüfte über SQL
Server 2019/2022/2025 insgesamt 54 Profile und 1674 Negativfälle. Auf frischem
Main bestanden dieselben 24 SQL-Jobs mit 24 Abbauschritten und erneut 54 Profile
mit 1674 Negativfällen. Alle 15 Main-Workflows sind erfolgreich; ihre 48
Prüfeinträge umfassen 47 Erfolge und einen fachlich nicht ausgewählten Matrixjob.
Vollständige Baumübernahme, lokale Main-Synchronisation und Entfernung des eigenen
lokalen sowie Remote-Branches sind bestätigt. Der
[abgegrenzte Setupnachweis](FWK_002_SETUP_OWNERSHIP_REVIEW.md) enthält die zehn
Demos mit Themen, Prüfverfahren und tatsächlichen Fehlversuchen.

Bei der Integration blieb ein optionaler statischer Prüfheader am Änderungsstand
ausstehend, obwohl alle seine Schritte einschließlich beider Validatoren und
Jobabschluss erfolgreich waren. Beide erforderlichen Prüfungen waren erfolgreich.
Der reguläre Merge erfolgte ohne Bypass; der damalige offene Header erhält keinen
grünen Ersatzstatus. Der entsprechende statische Main-Workflow ist frisch und
vollständig erfolgreich. Nach diesem getrennten Dokumentationsabschluss beginnt
die Framework-Ausführung.

Die Eigentumsprüfung der Frameworkreferenz ist über
[PR299](https://github.com/gecompat/SQL_PerformanceSchulung/pull/299) in Main
`6e9e485488c47d612f3e2da8622cf336f10b6f65` abgeschlossen. Lokal bestanden drei
tatsächliche alte Fehlannahmen, sechs Profile und 180 Negativfälle. Am
Änderungsstand und auf frischem Main bestanden alle drei Versionsverfahren samt
Abbau: jeweils 18 Profile und 540 Negativfälle auf SQL Server 2019/2022/2025.
Der frische Main besitzt acht erfolgreiche Workflow-Runs und 14 abgeschlossene
Prüfheader mit 13 Erfolgen und einem fachlich nicht ausgewählten Matrixjob.
Frühere widersprüchliche Head-Header bleiben als damaliger ausstehender Zustand
dokumentiert; kein Bypass oder grüner Ersatzstatus. Vollständige Baumübernahme,
Main-Synchronisation und eigene lokale sowie Remote-Branchbereinigung sind
bestätigt. Alle elf eigenen lokalen Container sind unabhängig abwesend. Der
[Frameworknachweis](FWK_002_FRAMEWORK_OWNERSHIP_REVIEW.md) erhält auch den ersten
fehlgeschlagenen Testleser und die Grenze seiner damaligen Rohtextaufnahme.

Als viertes begrenztes Produktpaket folgen vollständige Rohparameter vor der
Namens- und Aktionsableitung. Bisherige feste Typbreiten können ungültige
Eingaben vor der Prüfung kürzen; dieser bisher ausdrücklich offene Scope
benötigt eigene Gegenproben. Höchstens sechs Quellenstände und vier weitere
eigene lokale Container, Checkpoint nach drei Ständen oder dem ersten Blocker;
die bisherigen elf Container bleiben gezählt, globale Grenze weiterhin 17.
Erst nach vollständigem Abschluss dieses Dokumentationsschnitts beginnen
weitere SQL-Effekte. Recovery bei fehlgeschlagener Erstmarkierung bleibt offen.

Die Rohparameterkorrektur ist nach abgeschlossenem Dokumentationsschnitt
PR300 im Branch `codex/fwk002-input-validation` lokal geprüft. Elf neue reine
Testmethoden und die bisherigen 14 Framework-/13 Selektormethoden bestehen.
Nach unabhängigem Quellen-, Test- und Aufrufreview bestand C2 auf SQL Server 2025
neun tatsächliche alte Fehlannahmen, darunter drei Löschungen im Testaufbau,
sowie sechs korrigierte Profile mit 108 Negativfällen und allen positiven
Nachweisen. C1 wurde nach drei Quellenbefunden nicht ausgeführt. Alle zwölf
eigenen lokalen Container sind unabhängig abwesend. Versionsprüfung und
Integration stehen aus. Tatsächlicher Stand und Grenzen:
[Frameworkeingaben](FWK_002_FRAMEWORK_INPUT_REVIEW.md).

Der übergreifende Aufgabenrahmen bleibt dieser Schnitt plus höchstens drei
priorisierte Folgepakete mit eigenem endlichem Prüfrahmen; Checkpoint nach
jeder Integration. Danach zuerst verbleibende Setup-/Framework-Eigentumsprüfungen
und Recovery bei fehlgeschlagener Erstmarkierung, anschließend vollständige
menschliche Lesepfade und gezieltere Testauswahl. Recovery bedeutet
Wiederherstellung nach Fehler oder Abbruch. Teilnehmerpiloten benötigen eine
tatsächliche Durchführung. Eine begrenzte Cleanupabnahme ist keine globale
Freigabe des gesamten Ausführungspfads oder einer gemeinsam genutzten Instanz.

Details: [Eigentumsprüfung und tatsächliche Nachweise](FWK_002_CLEANUP_OWNERSHIP_REVIEW.md).

## Benutzerabschluss vom 22. Oktober 2026: keine autonome Fortsetzung

Historischer Auftrag, später durch die Wiederaufnahme vom 26. Oktober innerhalb
der priorisierten Reihenfolge abgelöst. Der laufende Status und die aktuelle
Reihenfolge stehen im Abschnitt [Autonomer Auftrag vom 26. Oktober 2026](#autonomer-auftrag-vom-26-oktober-2026) am Anfang dieses Dokuments.

Der Benutzer hat angeordnet, die aktuellen Demo-Implementierungen einschließlich
Dokumentation, Integration und Branchbereinigung abzuschließen, danach keine
neuen Implementierungen zu beginnen und diesen Chat zu beenden. Dieser Auftrag
ersetzt die frühere kontinuierliche Fortsetzung. Der zugehörige
30-Minuten-Heartbeat wurde gelöscht; er erteilt keine weiteren Fortsetzungen.

Die letzte Demo-Implementierung ist über
[PR293](https://github.com/gecompat/SQL_PerformanceSchulung/pull/293) vollständig
in Main `6407a105e656bd0669c81a1921265c292dc622cd` abgeschlossen. QRY-001
(Indexfreundliche Suchbedingungen) prüft bestehendes Datenbankeigentum vor
Konfigurations- und Tabellenänderungen. Unabhängiger Ergebnisreview ohne offene
priorisierte Befunde, lokale Gegenproben, 48 Head-, 46 Base- und 46 frische
Main-Prüfungen sind abgeschlossen und grün. Head ist der geprüfte
Pull-Request-Commit, Base dessen Main-Basis. Vollständige Baumübernahme,
saubere Main-Synchronisation und die Entfernung des eigenen lokalen und
Remote-Branches sind bestätigt. Alle vier eigenen lokalen Prüfcontainer sind
unabhängig abwesend; Fehlversuche und private Evidenz bleiben erhalten.

Dieser abschließende Dokumentationsschnitt hält ausschließlich den erreichten
Stand und das Ende des Auftrags fest. Weitere Eigentumslücken, menschliche
Lesepfade und native Kanalanbindungen bleiben im Backlog offen und werden in
diesem Chat nicht begonnen. Wiederaufnahme erfordert einen neuen menschlichen
Auftrag. Die begrenzte Demoabnahme ist keine globale Freigabe des Schutzvertrags
für Testdatenbanken oder einer gemeinsam genutzten Instanz.

Die folgenden Abschnitte sind historische Planungs- und Ausführungsstände.
Ihre früheren Fortsetzungsanweisungen sind durch diesen Benutzerabschluss
aufgehoben.

## Priorität: Setup-Eigentumsprüfung vor jeder Änderung

[PR292](https://github.com/gecompat/SQL_PerformanceSchulung/pull/292) ist in Main
`0558add5d2d030fd0b19829c5f8e4150ee05a234` vollständig abgeschlossen:
unabhängiger Review, lokale positive und negative SQL-Gegenproben, 48 grüne
Head-, 46 Base- und 46 frische Main-Prüfungen, vollständige Baumübernahme,
Synchronisation und eigene lokale sowie Remote-Branchbereinigung. Head ist
der geprüfte Pull-Request-Commit, Base dessen Main-Basis. Die vorherigen
Foundation- und Dokumentationsschnitte bleiben abgeschlossen.

Der getrennte Schnitt `codex/qry001-setup-ownership` behandelt ausschließlich
das Setup von QRY-001 (Indexfreundliche Suchbedingungen) unter FWK-002
(Schutzvertrag für Testdatenbanken). Bestehende Datenbanken müssen ihre vier
vollständigen Eigentumsmarker vor Konfigurations- oder Tabellenänderungen
nachweisen. Die normale Konfiguration und das synthetische Datenmodell bleiben
erhalten. Der alte Cleanuprahmen mit vier Quellenständen und vier lokalen
Prüfläufen ist geschlossen und wird nicht zurückgesetzt.

Ein Implementierungsverantwortlicher, derselbe unabhängige Reviewer;
Checkpoint am zweiten stabilen Kandidaten beziehungsweise ersten blockierenden
Befund, harte Grenze vier kohärente Kandidaten einschließlich Reviews, Tests,
Koordination und Integration. Höchstens vier lokale Prüfläufe, jeder in einem
eigenen neu erzeugten Dockercontainer mit gebundenem lokalem Image, zwei
Prozessorkernen und zwei GiB Arbeitsspeicher, ohne Ports oder Mounts. Je Lauf
1200 Sekunden einschließlich 90 Sekunden Cleanupreserve; eine Überschreitung
bleibt FAIL. Vor Effekten ist das unabhängige Quellen-, Test- und Aufruf-GO
erforderlich. Modell-/Koordinationsverbrauch UNKNOWN, nicht verlässlich
gemessen; tatsächliche native Zeit wird separat protokolliert.

Die alte Quelle muss die vorzeitige Konfigurationsänderung trotz anschließendem
FAIL_STATE (unzulässigem Ausgangszustand) und den tatsächlichen Ersatz eigener
Prüftabellen bei fehlenden Markern zeigen. Der korrigierte Stand muss ungültige
Marker und ein falsches Ziel ablehnen und dabei Identität, Zustand, vollständige
Markerbytes, Konfiguration, Tabellenstruktur und Prüfzeilen erhalten. Der echte
Dateiaufruf mit sqlcmd -b muss auch spätere Batchabschnitte hinter GO stoppen.
Neuanlage, zweimalige passende Wiederverwendung und zwei vollständige
Demo-Läufe bilden die Positivfälle; kanonischer Cleanup und unabhängige Absenz
bleiben Pflicht. Kein Host-SQL und kein fremder Datenbestand.

### Testauswahl und Aufwand der Setupkorrektur

Die neue Setupgegenprobe mit 27 Negativ- und zwei Positivfällen ergänzt den
bestehenden Gate-B-Dockerpfad. Die bisherige Cleanupgegenprobe und vier Piloten
mit je zwei vollständigen Läufen bleiben erhalten. Neue Datei und kleine
Oracle-Selbsttests werden in denselben Workflow aufgenommen, keine neue
Matrix oder Reviewkette. CI (Continuous Integration) bedeutet automatisierte
Integrationsprüfung. Relevante lokale Prüfungen einmal je stabilem Stand;
unveränderte grüne Tests werden nicht wiederholt. Derselbe unabhängig prüfende
Unteragent beurteilt Quellen, Aufruf und neue semantische Befunde; reine
grüne Logzählungen werden deterministisch geprüft.

Die notwendige Katalogkorrektur löst weiterhin die vorhandenen zusätzlichen
Parallelismus- und übrigen Demo-Matrizen aus: je Head/Main drei Gate-B-Jobs
mit 50 Minuten, drei Parallelismusjobs mit 60 Minuten und 27 weitere Jobs mit
90 Minuten. Zusammen 66 Matrixjobs und 5520 konfigurierte Jobminuten als
Obergrenzenschätzung, kein gemessener Verbrauch. Gates und sicherer Abbau
bleiben erhalten; die separate Effizienzkorrektur ist offen. Keine blinden
Wiederholungen, manuellen Neuauslösungen oder Abbrüche laufender Matrizen.

### Tatsächlicher lokaler Abschluss der Setupgegenproben

Der dritte Implementierungsstand hat beide konkreten Altfehler tatsächlich
nachgewiesen: Vorzeitige Konfigurationsänderung trotz anschließendem
Eigentumsfehler 51002 und Ersatz der vorhandenen Labortabellen bei vollständig
fehlenden Datenbankmarkern. Der korrigierte Stand bestand 27 Ablehnungsfälle,
zweimalige passende Wiederverwendung, Neuanlage sowie zwei vollständige
QRY-001-Demo-Läufe. Identität, Konfiguration, vollständige Markerbytes,
Tabellenstruktur und Prüfzeilen blieben bei Ablehnung erhalten. Kanonischer
Cleanup, unabhängige Datenbankabsenz und wiederholter Cleanup bestanden.

Die ersten beiden fehlgeschlagenen Prüfläufe bleiben erhalten: C1 stoppte vor
dem Altsetup an der Konfigurationsauswertung ohne unterdrückte Zeilenzahlmeldung;
C2 belegte den WrongProject-Fehler, scheiterte beim zweiten Altfall aber an
fehlenden Basisspalten der Fixturetabellen. Diese Fehler sind keine alten
Tabellenverlustnachweise. C3 korrigierte ausschließlich die Fixture und führte
den vollständigen Nachweis. Vier lokale Prüfläufe einschließlich Fehlständen
benötigten zusammen 322,672 gemessene Sekunden; alle vier eigenen Container
sind unabhängig abwesend, keine Zeitüberschreitung. Der native Rahmen ist
ausgeschöpft und geschlossen. C4 ergänzt nur diesen Dokumentationsabschluss;
die grüne SQL-Quelle wird nicht erneut ausgeführt.

Sieben neue öffentliche und vier private Oracle-Selbsttests sowie relevante
statische Demo-, Lesepfad-, Datenschutz- und Workflowprüfungen bestanden.
Unabhängige Quellen-, Test- und Aufrufreviews sind geschlossen; Ergebnisreview
und aktuelle Integrationsgates folgen. Regulärer Merge, frische Main-Gates,
vollständige Übernahme, Synchronisation und eigene Branchbereinigung bleiben
Abschlussbedingungen. Der begrenzte Dockerbeleg ist keine globale
Eigentumssicherheits-, Host- oder Produktionsfreigabe.

Andere 22 Cleanup-Textkandidaten, Recovery nach gescheiterter erstmaliger
Markierung einer neuen Datenbank und eine globale Freigabe des Schutzvertrags
bleiben offen. Weiterhin nur eigene Wegwerfinstanz; bei ungeklärtem Altzustand
Daten erhalten. Nach vollständiger Integration zuerst die übrigen
Eigentumslücken begrenzen, danach weitere menschliche Lesepfade beziehungsweise
native Kanalanbindung. Die folgenden Abschnitte sind historische Nachweise.

## Priorität: Eigentumsprüfung beim Cleanup indexfreundlicher Suchbedingungen

PR291 ist in Main `65089ac2c42a47fe961a1de7dc04d1e41da78f31` vollständig
abgeschlossen: unabhängiger Review, relevante lokale Prüfungen, 48 grüne Head-,
fünf Base- und 46 frische Main-Prüfungen, vollständige Baumübernahme,
Synchronisation sowie eigene lokale und Remote-Branchbereinigung. Head ist
der geprüfte Pull-Request-Commit, Base dessen Main-Basis. Das Foundation-Upgrade
aus PR290 bleibt abgeschlossen.

Der nächste begrenzte Schnitt auf `codex/qry001-cleanup-ownership` korrigiert
unter FWK-002 (Schutzvertrag für Testdatenbanken) ausschließlich den direkten
Cleanup von QRY-001 (Indexfreundliche Suchbedingungen). Ungekürzte Marker,
ausdrückliche NULL-Ablehnung und exakter Zeichen-/Längenvergleich schließen
den Quellenfehler. 37 Cleanupdateien wurden inventarisiert; 23 negative
Markerbedingungen sind Textkandidaten, keine vollständige Abnahme. Die anderen
22 Kandidaten und die gesonderte Setup-Lücke von QRY-001 bleiben offen.
Das Setup verändert eine vorhandene Datenbank vor der vollständigen
Markerprüfung. Eine gemeinsam genutzte Instanz bleibt ausgeschlossen.

Ein Implementierungsverantwortlicher und derselbe unabhängige Reviewer;
Checkpoint am zweiten stabilen Kandidaten oder ersten blockierenden Befund,
harte Grenze vier kohärente Kandidaten einschließlich Reviews, Tests,
Koordination, CI und Integration. CI bedeutet Continuous Integration,
automatisierte Integrationsprüfung. Verbrauch UNKNOWN, nicht verlässlich
gemessen. Vor Container-/SQL-Ausführung ist ein unabhängiges Quellen-,
Test- und Aufruf-GO erforderlich. Alte native Workerrahmen werden nicht benutzt.

Die Gegenprobe im Dockerziel muss die tatsächliche Löschung der eigenen
unmarkierten Datenbank durch die alte Quelle erkennen. Der korrigierte Stand
muss fehlende und abweichende Marker verweigern und dabei Datenbank-ID,
ONLINE-/MULTI_USER-Zustand, synthetische Prüfzeile (Sentinel) und Marker erhalten. Passende Marker,
unabhängige Absenz und idempotenter zweiter Cleanup sind Positivfälle.
Keine destruktiven Gegenproben auf dem vorhandenen Hostpfad.

### Testauswahl und Aufwand dieses Schnitts

Der bestehende Gate-B-Prüfpfad behält vier Piloten mit je zwei vollständigen
Läufen für SQL Server 2019, 2022 und 2025. Hinzu kommt ausschließlich die
QRY-001-Eigentumsgegenprobe. Ihre Datei und ihre kleinen Oracle-Selbsttests
werden in denselben Workflowselektor aufgenommen; keine zweite Matrix,
keine Gateumgehung und keine manuelle CI-Wiederholung. Die tatsächliche
SQL-Semantik einschließlich Datenerhalt lässt sich nicht durch einen
Stringvalidator ersetzen. Die relevanten lokalen Tests werden pro stabilem
Stand ausgeführt; unveränderte grüne Prüfungen werden nicht wiederholt.

Die notwendige Aktualisierung des Kataloghinweises löst nach den bestehenden
Selektoren außerdem die Parallelismus- und übrige Demo-Matrix aus. Dieser
bekannte breite Trigger bleibt für die aktuelle Integration erhalten. Eine
kleinere aus Quellenabhängigkeiten belegte Auswahl ist eine getrennte offene
Effizienzkorrektur; bis zu deren unabhängig geprüfter Umsetzung werden die
laufenden Matrixjobs bis zum eigenen Cleanup erhalten. Rohlogs und Budgetdaten
bleiben privat; Status, Hashbindung und Zählung werden deterministisch geprüft,
semantische Befunde durch denselben unabhängigen Reviewer.

Nach vollständigem Abschluss dieses Schnitts sind zuerst die gesonderte
Setup-Lücke und die weiteren Cleanupkandidaten zu begrenzen. Die operative
native Kanalanbindung folgt erst danach. Die folgenden Abschnitte sind
historische Nachweise.

## Foundation abgeschlossen; menschlicher Ausführungspfad und Cleanupbefund

[PR290](https://github.com/gecompat/SQL_PerformanceSchulung/pull/290) integriert
die aktuelle AI Repository Foundation 1.25.0 vollständig in Main
`2f4c427b3da36ae3c5f24770aeaee75ce3488ea0`: unabhängiger Review, lokale
Prüfungen, sieben grüne Head-, sechs Base- und fünf frische Main-Prüfungen,
vollständige Baumübernahme, Synchronisation und eigene lokale sowie
Remote-Branchbereinigung. Head ist der geprüfte Pull-Request-Commit, Base dessen
Main-Basis. Drei Adapter, zehn Capabilities, 114 Ziele und sämtliche bisherigen
Projektverträge bleiben erhalten; keine zusätzliche Aktivierung.
[PR289](https://github.com/gecompat/SQL_PerformanceSchulung/pull/289) und sein
alter nativer Versuchsrahmen bleiben vollständig abgeschlossen.

Der folgende TSK-015-Stand ist historisch: Der erste menschliche
Demo-Ausführungspfad für Auswahl, Vorbereitung, Ergebnisdeutung und Verhalten
nach Abbruch wurde mit [PR291](https://github.com/gecompat/SQL_PerformanceSchulung/pull/291)
integriert. Der damalige Branch `codex/human-demo-execution-path` und sein
Vier-Kandidaten-Rahmen sind abgeschlossen; sie sind kein aktueller Arbeitsauftrag.

Die echte Teilnehmer-Generalprobe bleibt getrennt offen. Ihr Ablauf und der
datensparsame Beobachtungsbogen stehen im [PRS-010-Plan](PRS_010_REHEARSAL_PLAN.md);
eine Durchführung mit Teilnehmenden und deren Ergebnisse sind nicht belegt.
Die verbleibenden menschlichen Lesepfade und die Bereinigung historischer
Planungseinstiege stehen als offene Arbeit im
[aktuellen Backlog-Auftrag vom 26. Oktober](../../.ai/BACKLOG.md#wiederaufnahme-und-reihenfolge-vom-26-oktober-2026).

Der Quellenreview hat einen konkreten Fehler im Cleanup der Demo zu
indexfreundlichen Suchbedingungen (`QRY-001`) bestätigt: Fehlende Marker
verhindern das Löschen nicht zuverlässig. Die negative SQL-Bedingung kann
`UNKNOWN` ergeben und die Ablehnung überspringen. Der Dokumentationsschnitt
stoppt deshalb die manuelle Löschanweisung und die unbelegte Marker-Garantie;
zurückgebliebene Datenbanken werden erhalten. Dies ist ein Quellenbefund,
kein ausgeführter SQL-Gegenfall oder Beleg einer bereits betroffenen Datenbank.

Die verlinkte Priorisierung ist ein historischer Stand vom 22. Oktober und
führte damals die funktionale Korrektur unter FWK-002 (Schutzvertrag für
Testdatenbanken) als nächsten Schnitt. Dieser Stand ist durch spätere
Integrationen und den Auftrag vom 26. Oktober abgelöst. Die heutige Reihenfolge
steht im [aktuellen Backlog-Auftrag](../../.ai/BACKLOG.md#wiederaufnahme-und-reihenfolge-vom-26-oktober-2026).
Neue SQL-/Prozesswirkung benötigt weiterhin ihre konkret geprüfte Auswahl,
Quellen, Gegenproben und ihr unabhängiges Aufruf-GO.

Die notwendige Korrektur der betroffenen Demo-README trifft den vorhandenen
breiten CI-Selektor für Gate B (Pilotdemo-Prüfungen). CI bedeutet Continuous
Integration, automatisierte Integrationsprüfung. Die bestehenden SQL-Matrixjobs
für 2019, 2022 und 2025 auf Head und Main bleiben erhalten; sie sind keine
Gegenprobe zum neu gefundenen Markerfehler. Keine manuelle Wiederholung oder
neue lokale SQL-Runtime wird daraus abgeleitet. Die folgenden Abschnitte sind
historische Nachweise.

## EARLY_EOF eingegrenzt; weiterer Versuchsrahmen erforderlich

Der [Diagnosecheckpoint vom 22. Oktober](DGN_007_RUNNER_PROFILE_OBSERVATION_REVIEW.md#diagnosecheckpoint-vom-22-oktober-2026)
grenzt `EARLY_EOF`, das vorzeitige Ende des Ausgabestroms, weiter ein:
Die letzte Diagnosequelle meldet alle sechs Initialisierungs-/Versiegelungs-
schritte erfolgreich. Erst der Runneraufruf, also der Aufruf der vollständigen
Ausführungssteuerung, lehnt mit `RUNNER_SOURCE_BINDING` ab. Die konkrete innere
Bindungsbedingung und ein möglicher Einfluss der Diagnoseinstrumentierung
bleiben offen. Ein vollständiger Profilreport fehlt weiterhin.

Die noch nicht integrierte Produktänderung behandelt den Dateieinstieg mit dem
eingebauten Python-Modul `builtins` und ergänzt einen kontrollierten
Ablehnungspfad. Zwei Gegenproben scheitern am alten Generator; alle 23 lokalen
Runnermodelle bestehen am korrigierten Stand. Nach unabhängig geschlossenen
Reviewbefunden bestehen zusätzlich neun reine Diagnosegegenproben, der Vergleich
des gesamten abstrakten Syntaxbaums und alle fünf Paketformen. Die Diagnosequelle
belegt damit keinen erfolgreichen nativen Produktlauf.

Der vom Implementierungsverantwortlichen gewählte und unabhängig geprüfte
endliche Rahmen ist ausgeschöpft: zwölf Quellen-/Test-/Aufrufstände, sechs
native Versuche, drei synthetische Prüfläufe mit 21 reservierten Prozessen,
18 Aufrufe des Windows Subsystem for Linux (WSL) und 1100 reservierte
Prozesssekunden. Nicht ausgeführte, im Review abgelehnte Stände zählen mit;
keine alte Zählung wurde zurückgesetzt. Modell- und Koordinationsverbrauch
bleiben UNKNOWN, also nicht verlässlich gemessen. Keine automatische Anhebung
oder weitere Implementierung und kein weiterer nativer Start in diesem Rahmen.

Der letzte Lauf endet kontrolliert mit Code 1, null Bytes auf dem regulären
Ausgabestrom und 136 Diagnosebytes auf dem Fehlerausgabestrom. Beide Datenströme,
alle eigenen Gruppen und beide Windows-Jobs sind beendet, unabhängige Absenz
und Wiederherstellung bestätigt; keine offene Besitzsperre. Die Arbeit bleibt
auf `codex/dgn007-early-eof-fix` erhalten. Noch kein Pull Request, Merge oder
Löschen des unübernommenen Branches. Die erforderliche nächste Entscheidung ist
eine neue endliche Diagnose-/Korrekturgrenze für die offene Runnerbindung;
Quellen-/Test-/Aufrufreview und grüne Integrationsprüfungen bleiben erforderlich.
Kein Body- oder Importstart, kein Runtime-, Trust-, Importbyte-, Methoden- oder
SQL-Nachweis. Die folgenden Abschnitte sind historische Abschlüsse.

## Erste Runnerprofilaufnahme: tatsächlicher Versuch abgelehnt, sicher beendet

Die [begrenzte Runnerprofilaufnahme](DGN_007_RUNNER_PROFILE_OBSERVATION_REVIEW.md#tatsächliches-ergebnis-des-dritten-standes)
hat nach unabhängigem Quellen-/Test-/Aufruf-GO einmal stattgefunden.
Runner bezeichnet die vollständige Ausführungssteuerung. Alle 19 portablen
Prüfmethoden und sechs nativen Gegenfälle bestanden ohne übersprungene Tests;
alle eigenen Prozessgruppen wurden unabhängig als abwesend nachgewiesen.

Der anschließend genau einmal gestartete unveränderte Runner lieferte keinen
Profilreport: `EARLY_EOF`, früher Abschluss des Ausgabestroms. Null stdout-
und 865 stderr-Bytes, ausschließlich Größen/Hashes gespeichert. Die konkrete
Ursache bleibt UNKNOWN, mit dieser Evidenz unbekannt. Eigener Cleanup,
beide Datenstromabschlüsse, Prozessabsenz und Wiederherstellung sind belegt;
alle vier Windows-Jobs beendet. Dies ist ein abgelehnter Lauf mit sicherem
Abschluss, kein erfolgreicher Profilvergleich oder Runtime-/SQL-Nachweis.

Drei von höchstens sechs Quellenständen, Checkpoint nach zwei, ein synthetischer
Prüflauf mit sieben Prozessen und der einzige ausgewählte Runner-Versuch sind
verbraucht. Kein Retry und keine Änderung des geschlossenen Auswahlpakets.
Weitere native Diagnose benötigt eine ausdrückliche neue Versuchsgrenze.
Der unabhängige Ergebnisreview ist ohne offene priorisierte Befunde geschlossen, die lokale Prüfung aller vier Dokumente bestanden. [PR288](https://github.com/gecompat/SQL_PerformanceSchulung/pull/288) führt ausschließlich den Dokumentationsabschluss fort; Gates, Übernahme, Synchronisation und eigene Branchbereinigung sind am aktuellen Pull Request und Gitstand zu prüfen.

## Nächster Schnitt: erste native Profilbeobachtung vorbereiten

Das Auswahlpaket ist über [PR286](https://github.com/gecompat/SQL_PerformanceSchulung/pull/286)
vollständig in Main `a714c7d578a18d2fa31fe862bc1e184ed1037444` integriert:
unabhängige Reviews, lokale positive/negative Prüfungen, sieben grüne Head-,
fünf grüne Base- und fünf frische Main-Prüfungen, vollständige Übernahme,
Synchronisation und eigene Branchbereinigung. Sein Rahmen mit acht von hart
acht Ständen ist geschlossen; keine Auswahlkorrektur oder Wiederholung.

Der kontinuierliche Auftrag führt zum [Plan für genau die erste frische
Runnerprofilaufnahme](DGN_007_NATIVE_PROFILE_OBSERVATION_PLAN.md). Runner
bezeichnet die vollständige Ausführungssteuerung. Dieser eigene Schnitt
ändert nur vier Dokumente: ein Implementierungsverantwortlicher und derselbe
unabhängige Reviewer, Checkpoint am eingefrorenen Entwurf, höchstens eine
Nacharbeit und harte Grenze zwei Entwurfsstände einschließlich Reviews,
Prüfungen und vollständiger Integration; Verbrauch UNKNOWN, nicht verlässlich
gemessen. Keine Codegenerierung, Importe oder native Aufrufe.

Die spätere Aufnahme soll das unveränderte Auswahlpaket verwenden, nur den
vollständigen PRE_IMPORT-Report vor Kandidatenimports erfassen und gegen alle
vorgewählten Felder prüfen. Keine Body-/Importfreigabe; geplanter eigener Stop
und unabhängiger Linux-Cleanup bleiben vor einem konkreten Lauf-GO zu lösen.
Der Plan erteilt dieses GO nicht. Eigenständiger endlicher Quellen-/Test- und
Aufrufrahmen erforderlich; keine Runtime-, Trust-, Importbyte- oder SQL-Abnahme.

## Achter Stand: vollständiges Auswahlpaket mit Poolvergleich bestanden

Der Mensch hat den [achten Quellen-/Teststand für Poolvergleich, Gegenproben
und offene Paketprüfungen](DGN_007_WORKER_PROFILE_SELECTION_REVIEW.md#achter-stand-poolvergleich-mit-unabhängiger-erwartung)
ausdrücklich freigegeben. Derselbe Implementierungsverantwortliche root und
derselbe unabhängige Reviewer führen den bestehenden Rahmen weiter: acht von
hart acht Ständen einschließlich Reviews, Tests, Koordination und Integration;
Verbrauch UNKNOWN, kein Neustart der Zählung. PR285 ist vollständig in Main
`0ae7cb735cc7961fffbac79c7837b4c60dae1cd5` integriert: sieben grüne Head-, fünf
grüne Base- und fünf frische grüne Main-Prüfungen, vollständige Übernahme,
Synchronisation und eigene Branchbereinigung. Die folgenden früheren
Freigabegrenzen und Stopps sind historische Evidenz.

Der Helfer verwendet den bestehenden Fünfformenvergleich mit Stringpools,
also einmal gespeicherten Texten mit gebundenen Referenzen. Die Gegenproben
ändern nur den empfangenen Report; die separat gehaltene Erwartung bleibt
unverändert. Alle bisherigen Fälle sowie je ein formal gültiger, aber falsch
gebundener Kontext müssen unter unveränderten Bytegrenzen geprüft werden:
insgesamt 40 negative Datenfälle und drei unveränderte Ganz-AST-/Fitmethoden
(AST: Abstract Syntax Tree; abstrakter Syntaxbaum). Der zusätzliche unabhängige
Testencoder ist als 22. Repositoryquelle vor Import und vor Ausgabe gepinnt.
Der unabhängige Quellen-/Testreview schloss den eingefrorenen Stand ohne offene
priorisierte Befunde und erteilte genau ein gestuftes Lauf-GO. Der einmalige
Windows-Lauf unter vorhandenem CPython 3.12 bestand vollständig: alle 40
Datengegenproben, drei Fünfformenvergleiche und drei ursprünglichen Ganz-AST-/
Fitmethoden. Beide Argumentformen wurden abgelehnt, beide Provider-Testmethoden
mit neun negativen Konfigurationen und beide Cleanup-Gegenproben bestanden;
alle vier Jobs endeten mit null aktiven Prozessen. Die 22 Quellenpins wurden
vor Import und nach den Paketprüfungen erneut bestätigt.

Die drei Scriptgrößen betragen 129807/130693/130415 Bytes unter unverändertem
131072-Byte-Limit; die fünf Formen zusammen jeweils 28192/28185/28174 Bytes
unter 65536, jeder Einzelrahmen unter 16384 Bytes. Drei private Scripts,
27 Rohdateien und der Paketbericht sind vollständig erhalten. Ergebnis bleibt
`SOURCE_SELECTED_DECLARATIONS_ONLY`, also ausschließlich quellenbegründete
Deklarationsauswahl. Keine neue Installation oder Linux-/Worker-/SQL-Ausführung;
Runtime, Trust, verwendete Importbytes und Methode sind weiterhin unbestätigt.
Der zugehörige Pull Request weist Reviewabschluss, exakte Head-/Base-/Main-Gates,
vollständige Übernahme, Synchronisation und eigene Branchbereinigung nach.
Kein neunter Stand oder Wiederholungsversuch in diesem ausgeschöpften Rahmen.

## Siebter Stand: Argumentkorrektur bestätigt, Paketvergleich zu groß

Der Mensch hat genau den siebten Stand für die
[Argumentkorrektur samt Gegenprobe und offenen Paketprüfungen](DGN_007_WORKER_PROFILE_SELECTION_REVIEW.md#aktueller-siebter-stand-bereinigte-argumentübergabe)
freigegeben. Ein Implementierungsverantwortlicher root und derselbe unabhängige
Reviewer, sieben/hartsieben einschließlich Tests, Koordination und vollständiger
Integration; Verbrauch UNKNOWN, kein neuer Scope. PR284 ist vollständig in
`4d758c1f8c52a7dce621eafc838063524fcd5a28` integriert und der eigene Branch
bereinigt; die früheren Freigabevorbehalte unten sind historische Evidenz.

Der unabhängige Delta-/Testreview erteilte ein einmaliges gestuftes Lauf-GO.
Die Startbrücke entfernt das Transportargument aus `sys.argv`
(Programargumentliste). Doppelpfad und leere Liste wurden als ungültige
Eintrittsformen abgelehnt. Beide Provider-Testmethoden bestanden ohne Fehler
oder Skip mit neun abgelehnten Providerkonfigurationen. Beide Cleanup-Gegenproben
bestanden; alle vier begonnenen Windows-Jobs endeten mit null aktiven Prozessen.

Der Pakethelfer unter vorhandenem Windows-CPython 3.12 bestand die
Eingangsprüfung. Die fünf Formen des ersten Workers erreichten die positive
Größen-/Codecprüfung, danach scheiterte der zusätzliche flache Profilvergleich
bei `POSITIVE_MATCH`. Eine rein lesende Untergrenzenanalyse begründet einen
mindestens 17156 Byte großen Datensatz gegenüber dessen 16384-Byte-Limit;
`METADATA_LIMIT` ist daraus hergeleitet, kein gespeicherter Rückgabewert.
Eine der 37 Datengegenproben erreicht, übrige 36 und alle drei Ganz-AST-/
Fitmethoden nicht ausgeführt; AST bezeichnet den abstrakten Syntaxbaum.
27 eigene Rohdateien erhalten, keine Worker-Scripts oder fertiges Paket.
Die [verbleibende Korrektur im vorhandenen Poolvergleich](DGN_007_WORKER_PROFILE_SELECTION_REVIEW.md#verbleibende-korrektur-im-bestehenden-poolverfahren)
benötigt eine neue ausdrückliche Erweiterung. Sieben/hartsieben, kein achter
Stand oder Retry ohne Entscheidung. Eigener Branch `codex/dgn007-argv-selection-fix`;
keine neue Installation oder Linux-/Worker-/SQL-Ausführung. Sicherer
Diagnoseabschluss mit unabhängigem Review und regulärer Integration.

## Interpreterkorrektur: Aufrufabbruch an der Sechsergrenze

Der Mensch hat den bestehenden Rahmen für das
[konkrete Auswahlpaket](DGN_007_WORKER_PROFILE_SELECTION_REVIEW.md#freigegebene-interpreterkorrektur-nach-dem-diagnoseabschluss)
auf höchstens sechs Quellen-/Teststände mit Checkpoint nach fünf erweitert.
Ein Owner und derselbe unabhängige Reviewer; Verbrauch UNKNOWN. Keine neue
Zählung, alte Fehler und Partialartefakte bleiben erhalten. PR283 ist vollständig
in `e0cec9842971d0ecdf3f1604cdd5f59f3109a946` integriert: sieben grüne Head-,
fünf grüne Base- und fünf frische grüne Main-Prüfungen, unabhängiger Review,
vollständige Übernahme und eigene Branchbereinigung.

Die Korrektur verlangt einen tatsächlichen isolierten Windows-Prüfinterpreter
CPython 3.12 vor weiteren Imports oder Datei-/Prozesseffekten. Die vorhandene
gebündelte Laufzeit ermöglicht die Korrektur ohne Linux-Aufruf oder
Neuinstallation. Checkpoint nach fünf: zwei unabhängige Befunde am Fehlercleanup
und an den Zeitgrenzen des Windows-Owners, kein Lauf-GO und keine Ausführung.
Der sechste Stand bündelt die Korrekturen und zwei vorgeschaltete synthetische
Fehler-/Timeout-Gegenproben mit eigenem Prozesscleanup. Danach bleiben die
Interpretergegenprobe und sämtliche noch offenen Paketprüfungen erforderlich.
Der unabhängige Delta-/Testreview schloss beide Befunde und erteilte ein
gestuftes einmaliges Lauf-GO. Deadlinefälle und beide Cleanup-Gegenproben
bestanden; alle drei begonnenen Windows-Jobs endeten mit geprüft null aktiven
Prozessen. Der dritte Job scheiterte an einem Aufruffehler der Startbrücke:
Der Zielpfad blieb in `sys.argv` und wurde von `unittest` als Testname gelesen.
Keine der beiden Provider-Testmethoden und kein Pakethelferlauf; alle
37 Paketgegenproben und Form-/Fitprüfungen sind in diesem Stand nicht ausgeführt.
Keine neuen Paket- oder Workerartefakte, kein Linux-/SQL-Lauf.
Sechs von hart sechs Ständen, kein siebter Stand oder Wiederholungsversuch.
Die [konkrete Korrektur der Argumentübergabe und Methodenzählung](DGN_007_WORKER_PROFILE_SELECTION_REVIEW.md#konkreter-vorschlag-zur-weiteren-korrektur)
bedarf einer neuen ausdrücklichen Erweiterung; der sichere Diagnoseabschluss
wird unabhängig geprüft regulär integriert.
Eigener Branch `codex/dgn007-interpreter-selection-fix`. Die bisherigen
3.12-AST-Hashes (AST: Abstract Syntax Tree; abstrakter Syntaxbaum), Originalbytes,
Oracles und Größenlimits bleiben unverändert; keine Worker- oder SQL-Freigabe.

## Auswahlpaket gestoppt: falscher AST-Prüfinterpreter

[PR281](https://github.com/gecompat/SQL_PerformanceSchulung/pull/281) ist in
`f143c968f5fec26c60fcc8b32e8baac637fdbcd1` vollständig abgeschlossen: unabhängiger
Review, lokale Windows-/Linuxmodelle, grüne PR-/Main-Prüfungen, vollständige
Baumübernahme und eigene Branchbereinigung. Der kontinuierliche menschliche
Auftrag gilt weiter; die historischen C6-/C7-/C8-Sperren unten sind überholt.

Der [Auswahlplan für frische Workerprofile](DGN_007_WORKER_PROFILE_SELECTION_PLAN.md)
ist über PR282 in Main `e4b373d679ef2f8670913239664e55623cf7caaa` vollständig
geschlossen: unabhängiger Review, lokale Dokumentationsprüfungen, sieben Head-/
drei Base-/fünf frische Main-Prüfungen grün, vollständige Übernahme,
Synchronisation und eigene Branchbereinigung.

Das [konkrete quellenbegründete Auswahlpaket](DGN_007_WORKER_PROFILE_SELECTION_REVIEW.md)
betrifft eine vorhandene Linux-Installation und drei vollständige Workerprofile,
ein Owner/ein unabhängiger Reviewer, Checkpoint eins/hart vier einschließlich
Reviews, lokaler Gegenproben, Koordination und vollständiger Integration;
Verbrauch UNKNOWN. Eigener Branch `codex/dgn007-worker-profile-selection`.
Vier/hartvier Quellen-/Teststände: der dritte ohne Lauf-GO abgelehnt, die drei
Befunde im vierten unabhängig geschlossen. Dessen einmaliger freigegebener
Windows-Lauf scheiterte bei `INPUT_PREPARATION`: Der statische Eingangsprüfer
verlangt Python 3.12 für seine AST-Hashes (AST: Abstract Syntax Tree;
abstrakter Syntaxbaum), der Helfer lief unter 3.14.7. Die Rohbytes stimmten
überein; die lesende Diagnose erklärt `BOOTSTRAP_CHANGED` durch das veränderte
AST-Ausgabeformat. Kein Prüfer-/Hashwechsel oder Wiederholungslauf.

Vier Tabellenlesertests und ein statischer Binärread bestanden; im Paketlauf
wurde nur eine der 37 geplanten negativen Datenproben erreicht. Form-/Größen-
und Ganz-AST-/Fitprüfungen sind nicht ausgeführt, das Auswahlpaket ist nicht
abgenommen. Eigene 27 Partialdateien bleiben privat erhalten; kein fertiger
Paketbericht, keine Worker-Scriptdateien, keine Linux-/WSL-, Worker- oder
SQL-Ausführung. Die Diagnose wird unabhängig geprüft regulär integriert.
Eine [begrenzte Erweiterung für Providerkorrektur und Gegenprobe](DGN_007_WORKER_PROFILE_SELECTION_REVIEW.md#erforderliche-entscheidung-zur-wiederaufnahme)
bedarf einer ausdrücklichen Entscheidung; kein fünfter Stand oder Budgetreset.

## Reentranzfehler im vollständigen Runner behoben

Der gemeinsame Kontrollcheck stoppt den normalen Ablauf nach einem reentranten
Einstieg vor weiteren Providerwirkungen. Der abschließende Diagnosecheck erhält
dabei den Vorrang verlorener Bindungen. Auch der im ersten Modelllauf erkannte
Fehlercleanup für flache Modulnamen ist korrigiert. Gegenproben beobachten das
Fehlerflag bereits im Callback und prüfen anschließend null Exec-Aufrufe,
keine weiteren Writes, strukturierte Ablehnung, eigenen Cleanup und wirkungsfreien
Retry. Die Kandidatengrenze wurde für diesen menschlich beauftragten Abschluss
aufgehoben; die darunter erhaltenen C8-Sperren sind historische Evidenz.

Quellen-/Teststand `47b07578d35467f8206cc88ed95457c9e74ae8d9`, Basis
`73c08a798f64fe2d7a36d49df740934a028fecc3`, eigener Branch
`codex/dgn007-reentrancy`: unabhängige Quellen-/Testprüfung ohne offene
priorisierte Befunde, lokal je 21 Methoden auf Windows 3.14.7 und Linux 3.12.3
mit `-I -S -B` bestanden. Vollständige Originalprofilbytes und unabhängiger
Ganz-AST-Vergleich (AST: Abstract Syntax Tree; abstrakter Syntaxbaum) bestehen
bei Windows-Zeilenenden (CRLF: Carriage Return/Line Feed) mit 129679 Bytes und
Unix-Zeilenenden (LF: Line Feed) mit 127911 Bytes unter dem unveränderten
131072-Byte-Limit.
[Konkreter Nachweis, Grenzen und Integrationsverfahren](DGN_007_RUNNER_SHARED_SOURCE_REVIEW.md#abschluss-des-funktionalen-schnitts).

Die reguläre Integration verlangt aktuelle grüne Prüfungen für den PR-Stand
(Head) und die Main-Basis (Base), anschließend
frische Main-Gates, vollständige Baumübernahme, Synchronisation und eigene
Branchbereinigung. Der zugehörige Pull-Request-Abschlussnachweis bindet die
konkreten Ergebnisse. DEC-076 bleibt maßgeblich; die synthetischen Modelle sind
kein Nachweis eines nativen Laufs, der Quellenherkunft, tatsächlich ausgeführter
Quellbytes, der Messmethode oder der Abschlussmeldung SESSION_END und keine
SQL-Freigabe. Dieser funktionale Schnitt eröffnet keine neue operative
Welle. Private Evidence und fremde Ressourcen bleiben erhalten.

## C8 abgelehnt: Folgeeffekt nach Reentranz; Vertrauensmodell entschieden

Der Mensch hat vertrauenswürdige Schulungsquellen gewählt und gezielte
Kontrollmanipulationen vom Prüfversprechen ausgeschlossen. DEC-076 dokumentiert
diese Entscheidung. Der stabile C8 `e6184befeaeda00d6ac784038a8b3b6f8b7ed119`
ist unabhängig ohne Lauf-GO abgelehnt: Bei Reentranz im Compilecallback kann
der Exec-Provider trotz gesetztem Fehlerflag noch aufgerufen werden. Die
Reentranzprobe deckt diese Folgeeffekte nicht ab. Dieser funktionale Befund
bleibt unter dem gewählten Vertrauensmodell erforderlich.
[Konkreter Befund, Vertragsgrenze und Disposition](DGN_007_RUNNER_SHARED_SOURCE_REVIEW.md#c8-unter-dec-076-abgelehnt-funktionaler-reentranzbefund).

Die gezielte Bootstrap-Feld-0-Korrektur ist im Quellenreview unter DEC-076
statisch geschlossen. Kein allgemeiner Manipulationssicherheitsclaim. Acht/
hartacht Kandidaten, sieben geänderte Nachläufe, Verbrauch UNKNOWN. Kein
Kandidatenimport, keine Generierung, AST-Analyse, Kompilierung, Ausführung,
Fit- oder Modelllauf. Die neue Runnerquelle, 20 Methoden und der Workflow sind
aus dem finalen Diff entfernt; der abgelehnte Stand ist privat in einem
vollständigen geprüften Gitbundle bewahrt. Bestehende Komponenten bleiben erhalten.

Nächste Quellenarbeit ist bis zu einer ausdrücklichen neuen begrenzten
Entscheidung zum funktionalen Fehlerabschluss und dessen Folgeeffektprobe
blockiert. Kein C9, Scope-/Budgetreset oder unveränderter automatischer Nachlauf.
Die Vertrauensfrage ist entschieden. Tatsächliche Runtime-, Trust-, Usedbytes-,
Methoden-, SESSION_END- und SQL-Gates bleiben offen.

Der reine Vertrags-/Diagnoseabschluss gehört zu
[PR280](https://github.com/gecompat/SQL_PerformanceSchulung/pull/280), eigener
Branch `codex/dgn007-trusted-sources-c8`. Der dortige Abschlussnachweis bindet die
unabhängige Disposition, lokalen Dokumentations-/Registryprüfungen, aktuellen
Head-/Base-Gates, den regulären Merge, frische Main-Gates, vollständige Übernahme,
Synchronisation und eigene lokale/Remote-Branchbereinigung an tatsächlich belegte
Ergebnisse. Private Evidence und fremde Ressourcen bleiben erhalten. Die frühere
ABI-Auswahlsperre unten ist historisch und durch DEC-076 behandelt; sie ist kein
weiterer offener Entscheidungsbedarf.

## C8 vor Umsetzung blockiert: Vertrauenswurzel am Python-Importeinstieg

Die ausdrückliche Freigabe umfasst genau einen stabilen C8 zur Bootstrap-
Korrektur. Die unabhängige Auswahlprüfung an 841b395 hat vor Umsetzung einen
konkreten [ABI-/Trustblocker und die Entscheidungsalternativen](DGN_007_RUNNER_SHARED_SOURCE_REVIEW.md#unabhängiges-auswahl-no-go-synchroner-abi-einstieg)
belegt: Der synchrone Python-Importmechanismus übergibt keine ursprünglichen
Kontrollreferenzen an das Gateway. Dessen zuvor veränderter Code könnte jede
eigene Prüfung umgehen; der äußere Nachcheck kommt erst nach möglichen
Wirkungen. Ein weiterer Python-Wrapper schließt diese Lücke nicht.

C8 ist noch nicht als Quellen-/Testkandidat verbraucht. Bisher sieben Kandidaten
und sechs geänderte Nachläufe, Verbrauch UNKNOWN; die einzelne C8-Freigabe ist
kein C9 oder Reset. Keine Implementierung, kein Quellenfreeze, keine Generierung
oder Kandidaten-/Modell-/Fitläufe. Der unveränderte DESIGNED-Vertrag bietet
bisher keine vollständig belegte Übergabekette für diesen Einstieg.

Nächste Umsetzung benötigt eine ausdrückliche Entscheidung über ein begrenztes
Manipulationsmodell für vertrauenswürdige Schulungsquellen oder eine gesonderte
vertrauenswürdige Runtimevermittlung. Das sind Vertrags-/Architekturentscheidungen,
keine routinemäßige Implementierungs- oder Mergefreigabe. Tatsächliche Runtime-,
Trust-, Usedbytes-, Methoden-, SESSION_END- und SQL-Gates bleiben offen.

Der reine Diagnoseabschluss gehört zu
[PR279](https://github.com/gecompat/SQL_PerformanceSchulung/pull/279), eigener
Branch `codex/dgn007-runner-c8`. Der dortige Abschlussnachweis bindet die
unabhängige Disposition, lokale Dokumentationsprüfung, aktuelle Head-/Base-Gates,
den regulären Merge, frische Main-Gates, vollständige Übernahme, Synchronisation
und eigene lokale/Remote-Branchbereinigung an die tatsächlich belegten Ergebnisse.
Private Evidence und fremde Ressourcen bleiben erhalten. Unveränderte Heartbeats
starten keine Wiederholungsanalyse oder Kandidaten.

## C7 abgelehnt; erweiterte harte Grenze erreicht

Der ausdrücklich freigegebene einzelne C7 ist im unabhängigen Quellen-/Test-PRE
(Prüfung vor dem Lauf) abgelehnt. Stabile Bindung 559f09cc35dd22a2fd073641401c23517114e031:
Eine 17-elementige Ersatzkopie der `_kernel`-Closure könnte vor dem ursprünglichen
Kernelcheck eine fremde Iteration auslösen. Die Gegenprobe deckt diesen Einstieg
nicht ab. Prüfung am zwingenden STOP beendet, keine vollständige Befundschließung.
[Konkreter Befund, gemeinsamer Rahmen und Disposition](DGN_007_RUNNER_SHARED_SOURCE_REVIEW.md).

Sieben/hartsieben Kandidaten, sechs geänderte Nachläufe, Verbrauch UNKNOWN.
Kein Kandidatenimport, keine Generierung, kein Fit-, Compile-/Exec- oder Modelllauf.
Die neue Runnerquelle, ihre 19 Testmethoden und der Workflow sind aus dem finalen
Diff entfernt; der verworfene Stand ist privat in einem geprüften Gitbundle
bewahrt. Bestehende Komponenten und fremde Ressourcen bleiben erhalten.

Der reine Diagnoseabschluss gehört zu
[PR278](https://github.com/gecompat/SQL_PerformanceSchulung/pull/278), eigener
Branch `codex/dgn007-runner-c7`. Der dortige Abschlussnachweis bindet die
unabhängige Disposition, lokale Dokumentationsprüfung, aktuelle Head-/Base-Gates,
den regulären Merge, frische Main-Gates, FullTree/Sync (vollständige Baumübernahme
und Synchronisation) sowie die eigene lokale/Remote-Branchbereinigung an die
tatsächlich belegten Ergebnisse.

Nächste Quellenarbeit ist bis zur ausdrücklichen neuen begrenzten Entscheidung
zur Bootstrap-Korrektur blockiert. Kein C8 oder Scope-/Budgetreset. Die frühere
kontinuierliche Fortsetzung hebt die ausdrücklich gesetzte C7-Grenze nicht auf.
Unveränderte Heartbeats starten keine neue Analyse oder Wiederholungsprüfung.
Alle tatsächlichen Runtime-, Trust-, Usedbytes-, Methoden-, SESSION_END- und
SQL-Freigaben bleiben offen. Die historische C6-Grenze unten wurde ausschließlich
für genau C7 erweitert; sie ist keine aktuelle weitere Freigabe.

## C6 im Source-/Test-PRE abgelehnt; konkrete Sourcegrenze erreicht

PR275 vollständig Main750844bbfe61f6b12c98354c034ea3441abbde91: sieben finale
Head-/sechs Base-/fünf frische Main-Gates SUCCESS, unabhängige Designschließung,
FullTree/Sync und eigene lokale/Remote-Branchabwesenheit bestätigt.
[PR275-Abschlussnachweis](https://github.com/gecompat/SQL_PerformanceSchulung/pull/275).

Der letzte stabile C6 d0470fcaf3445a9ea68ef253a08930669a69424d ist unabhängig
im Source-/Test-PRE mit drei P2 abgelehnt: `parent` vor Zuweisung, ungeprüfte
Guard-Slotinhalte vor Bootstrap und erneut gelesene veränderbare Closurezellen
im Cleanup. Keine Generierung, kein Fit oder Modelllauf; Größenersparnis
weiter unbekannt. Eigene UTF-8-Textkorruption ist als zusätzlicher Befund
benannt; Planungsdokumente aus ursprünglichen Gitbytes wiederhergestellt.
[Konkreter Befund-/Dispositions- und Entscheidungseintrag](DGN_007_RUNNER_SHARED_SOURCE_REVIEW.md).

Sechs/hartsechs Source-/Testkandidaten, fünf geänderte Nachläufe, Verbrauch
UNKNOWN. Kein stiller C7 oder Quellen-/Scope-/Budgetreset. Verworfene neue
Runnerquelle, ihre16 Tests und Workflow aus finalem Diff entfernt; bestehende
Komponenten bleiben erhalten. Der reine Dokumentationsabschluss gehört zu
[PR276](https://github.com/gecompat/SQL_PerformanceSchulung/pull/276). Dessen
Abschlussnachweis hält die tatsächlichen Review-/Head-/Base-/Main-Gates,
FullTree/Sync und eigene lokale/Remote-Branchbereinigung fest; daraus folgt
keine Sourcefreigabe.

Nächste Sourcearbeit ist blockiert, bis die im Befundeintrag konkret vorgeschlagene
Erweiterung um genau einen weiteren stabilen C7 ausdrücklich entschieden wird.
Der Vorschlag wahrt den DESIGNED-Vertrag und alle Gates, ist keine Freigabe.
Unveränderte Heartbeats starten keine Wiederholungsanalyse oder nächste Welle.
Alle realen Runtime-/Trust-/Usedbytes-/Methoden-/SESSION_END-/SQL-Gates bleiben offen.

## Architekturplan nach abgeschlossenem Diagnose-PR274

PR274 ist vollständig in Mainf30aebce18ec2902171210bdcc7f222eaa12d405 integriert:
acht finale Head-/sieben Base-/sechs frische Main-Gates SUCCESS, unabhängige
Schließung, FullTree/Sync und eigene lokale/Remote-Branchabwesenheit bestätigt.
[PR274-Abschlussnachweis](https://github.com/gecompat/SQL_PerformanceSchulung/pull/274).

Nächster endlich begrenzter Schritt ist ausschließlich der [Architekturplan
für einen gemeinsamen Rootkontrollanker](DGN_007_RUNNER_SHARED_CONTROL_DESIGN.md):
ein Owner/ein unabhängiger Reviewer, ein Entwurf/höchstens eine geänderte
Entwurfsnacharbeit einschließlich vollständigem Dokumentationsabschluss,
Verbrauch UNKNOWN. Die fünf/max6 ursprünglichen Source/Testkandidaten bleiben
verbraucht, kein Reset oder weiterer Quellenversuch. Standalone-Parentfactory
bleibt erhalten; alternative Route soll Sources/Parents durch denselben
ursprünglichen Anker prüfen, sämtliche Helfer vor Reportsnapshot erzeugen und
späte Graphaufnahme vermeiden. Tatsächliche Einsparung unbekannt. Design-PRE
ergab P2 für konkrete Dominanz-/Zwischenzustände und P3 für Methodenwortlaut.
Einzige Entwurfsnacharbeit ergänzt Pin→Prüfstelle, alle Modul-/Spec-/Record-
Unterzustände, vollständige Metadaten, finally-POSTs, Fehlerpriorität und
sicheren aktiven Fehlerabschluss. Zwei/hartzwei Entwurfsstände; unabhängiger
Delta-PRE210f8e2 schließt P2/P3 ohne offene priorisierte Designbefunde.
DESIGNED ausschließlich Architektur; PR275 inzwischen vollständig integriert,
keine Source-/Test-/Generierungs-/Lauf-/Native-/SQLfreigabe.131072Cap und vollständige
Raw-/Kontroll-/Methoden-/Trust-/Usedbytesgates bleiben unverändert.

## Runner-Quellenfit-Diagnose vom 21. Oktober 2026

Die [vollständige Runnerroute](DGN_007_RUNNER_LOADER_SOURCE_REVIEW.md) ist als
CLOSED_REJECTED_SOURCE_FIT sachlich verworfen. Fünf/max6 Kandidaten, vier
Nachläufe, Verbrauch UNKNOWN; keine behauptete Budgeterschöpfung. Letzter
zulässiger Größenbefund C4:140097Bytes,9025 über unverändertem131072Cap.
Windows-/Linux-Fits stoppten am Limit. C5 stoppte an TEMPLATE_FORM: Der für eine
Auslassung ausgewählte Parentmatcher ist bereits aus der Workerbasis ausgespart.
Diese Auswahlannahme war falsch und ist unabhängig berichtigt. Keine erfolgreiche
Ganz-AST-/Runner-Modellabnahme, übrige15 Modelle nicht gestartet.

Unabhängiges Dispositions-GO: neue Runnerquelle, ihre16 Tests und Workflow aus
finalem Diff entfernt; bestehende Komponenten unverändert. Nur begründeter
Diagnoseabschluss und belegter PR273-Abschluss werden integriert. Branch
codex/dgn007-runner-loader-source, [Diagnose-PR274](https://github.com/gecompat/SQL_PerformanceSchulung/pull/274).
Lokale Privacy1256/600 relative Markdownziele/Whitespace PASS; unabhängiger
Abschlussreview526e636 ohne offene P1/P2/P3, Integrations-GO für reinen
Dokumentationsabschluss. Aktuelle finale Head-/Base-/Main-Gates, regulärer
Merge, FullTree/Sync und eigene lokale/Remote-Bereinigung noch offen; der
PR-Abschlussnachweis hält nach erfolgter Integration die tatsächlichen IDs.

Offener Quellenarchitekturblocker: vollständige Runnerkomposition innerhalb
bestehendem Scriptlimit fehlt. Wiederaufnahme verlangt konkreten unabhängig
geprüften Architekturplan und nachvollziehbaren gemeinsamen Quellen-/Versuchsrahmen,
anschließend Source/Test-PRE und ausdrückliches Lauf-GO. Kein Scope-/Budgetreset,
keine Capanhebung oder unveränderte Wiederholungsprobe. Tatsächliche DGN-Raw-/
Native-/Trust-/Usedbytes-/Methoden-/SQL- und Gesamtgates bleiben offen.

PR273 ist vollständig in Mainb00418ca74cd6ff4a0d194f8276ca365f9558f56 integriert:
neun PR-/sieben frische Main-Gates SUCCESS, Parent12/Harness16 ohne SKIP,
unabhängige Schließung, FullTree/Sync und eigene Branchabwesenheit bestätigt.
[PR273-Abschlussbindung](https://github.com/gecompat/SQL_PerformanceSchulung/pull/273).

## Codefreie Parentregistrierung vom 20. Oktober 2026

PR272 vollständig in Main4a165c20840193e26b05a789d8e6e067c0bca7b9 integriert:
neun finale PR-/sieben frische Main-Gates SUCCESS, neue Harness16 und unveränderte
Proxy16 ohne SKIP PASS, unabhängige Befundschließung, FullTree/Sync und eigene
lokale/Remote-Branchabwesenheit bestätigt. Vier Kandidaten/drei Nachläufe
erfolgreich geschlossen; [Abschlussbindung PR272](https://github.com/gecompat/SQL_PerformanceSchulung/pull/272).

Nächster priorisierter begrenzter Schnitt: [codefreie Parentregistrierung](DGN_007_CODEFREE_PARENT_REGISTRATION_REVIEW.md)
für die noch fehlende Runnerfolge. Eigenständige vorbereitende Komponente für
Tests/Tests.Contracts, PARENT0/1 mit festen Slots6/7 und9/10, keine Compile-/Exec-
Invocation. Eigener Branch codex/dgn007-codefree-parents, ein Owner/max4/
Checkpoint1/hart4 einschließlich Review/Test/Integration/Cleanup; Verbrauch
UNKNOWN. Auswahl-PRE unabhängig freigegeben mit geschlossenen späten Kindslots
und begrenzten ursprünglichen Kwdefaults-/Closurezellwerten. C1 mit Factory und
zwölf isolierten Methoden, Checkpoint1. C1 unabhängig mit zwei P3 ohne Lauf-GO:
Klassenlimit erst nach Kopie und falscher Guard-False-Issue. C2 begrenzt rohe
Mappingproxy/Keys vor Kopie und ergänzt erreichte Klassenlimitprobe; dauerhafter
Guardfehler erwartet dominantes BINDING. Zwei/max4 Kandidaten, ein Nachlauf;
Delta-PRE geschlossen und einmaliges Lauf-GO. C2 zwölf Methoden Windows/Linux
jeweils elf PASS/ein Fixture-FAIL ohne SKIP: eigener UTF8-SIG-Dateiread lädt
Codec nach, strenge Modulcacheoracle erkennt dies. C3 ausschließlich read_bytes
für diese AST-Probe, keine neue Importbaseline/Whitelist oder Produktauswirkung.
Drei/max4 Kandidaten, zwei Nachläufe; enger Fixture-PRE ohne offene Befunde und
gezieltes Lauf-GO. Fehlgeschlagene Methode danach Windows/Linux1/1 ohne SKIP
PASS; mit unveränderten elf C2-PASSs lokale zwölf vollständig und unabhängige
Schließung belegt. CI-/Head-/Base-Gates, reguläre Integration, frisches Main,
FullTree/Sync und eigene Branchbereinigung stehen noch aus.
Tatsächliche Runner-/Kontrollanker-/I/O-Anbindung, vollständiger Scriptfit und
sämtliche realen Gesamtgates bleiben offen; keine Native-/DGN-Raw-/SQL-Freigabe.

## Verschachtelte Harness-Quellenfolge vom 20. Oktober 2026

PR271 vollständig in `3387e308c8ae4f45d1cf8eb56176666e9e9355d4` integriert:
zehn finale PR-Checks und acht frische Main-Workflows SUCCESS; neue16, bestehende
Eingangs16 und Budget12 ohne SKIP PASS. Unabhängige Befundschließung, FullTree/
Sync und Abwesenheit eigener lokaler/Remote-Branches bestätigt.
[Abschlussbindung PR271](https://github.com/gecompat/SQL_PerformanceSchulung/pull/271).
Der Sechserumfang ist geschlossen; kein weiterer Versuch oder Reset dort.

Nächster endlich gewählter Funktionsschnitt: [verschachtelte Harness-Quellenfolge](DGN_007_HARNESS_LOADER_SOURCE_REVIEW.md)
für Worker3 mit SOURCE-BEGIN3/4/5 und COMPLETE5/4/3, ohne Parents. Eigener Branch
`codex/dgn007-harness-loader-source`, ein Implementierungsowner, derselbe
unabhängige Reviewer, max6/Checkpoint2/hart6 einschließlich Reviews, Tests und
vollständigem Integrationsabschluss; Verbrauch UNKNOWN. Auswahl-PRE mit geschlossenen
Source-/Namen-/Fromlistkanten, reservierten Wirkungen und Getterfreiheit freigegeben.
C1 ergänzt additive Quelle/16 eigene Methoden. Unabhängiger PRE mit einem P2
für spätere Fremdbelegung eines noch ausstehenden Slots und einem P3 für
nicht eindeutig erreichte Typgrenzen, kein Lauf-GO. C2 prüft alle noch nicht
veröffentlichten Kandidaten-/Parentslots auf Abwesenheit; späte Slot4/5-Callbacks
und Fremdname-/Falselevel-Gegenproben mit Len-Trap. Originale Budgethalter und
abgeschlossene Sourcebindungen bleiben erhalten. Checkpoint2: zwei/max6 Kandidaten,
ein Nachlauf. C2 unabhängig geschlossen und gestuftes GO; nur Fitmethode danach
Windows/Linux jeweils SCRIPT_LIMIT, übrige15 nicht ausgeführt. Einmalige separat
freigegebene reine Größendiagnose:133517Bytes,2445über Cap; zusätzliche kurze
Locals nur geschätzt415Bytes. C3-Auswahl-PRE für genau eine private globale
Helperumbenennung unabhängig freigegeben. C3 setzt genau diese Umbenennung mit
geschlossenen Vorbedingungen und gesonderter unabhängiger Rückführung um, neue
Kollisions-/Binding-AST-Gegenproben. C3 unabhängig mit einem P3 ohne Lauf-GO:
negative ASTs wurden bereits durch fehlenden gültigen Load verdeckt. C4 ergänzt
gültige Basisloads und exakte positive Def-/Load-/Byte-Literaloracle, Produkt
unverändert. Vier/max6 Kandidaten, drei Nachläufe; C4 unabhängig ohne offene
Befunde mit gestuftem einmaligem Lauf-GO. Fit Windows/Linux PASS, tatsächliche
CRLF-/LF-Quellen130337/128569Bytes unter unverändertem131072Cap; ganze AST-/
Literal-/Alphaoracle bestanden. Danach übrige15 Methoden je Plattform ohne
SKIP PASS, damit16/16 lokal grün. Reguläre CI-/Head-/Base-Gates und Integration
einschließlich frischem Main/FullTree/Sync/Branchcleanup bleiben offen.
Nur eigene sichere Modelle nach separatem
Source/Test-PRE und explizitem Lauf-GO; neue echte Imports/Native-/DGN-Raw-/SQL-
Wirkungen und Gesamtgates bleiben offen. Proxyroute und alle älteren Scopes erhalten.

## Erste direkte Quelleninvocation nach EOF vom 20. Oktober 2026

PR270 vollständig in `20549ae4e7dbb31c2ffb4d5b051395b8033db18e` integriert:
zwölf finale PR-Checks/zehn frische Main-Workflows SUCCESS, neue12 und bestehende
Handshake12/28Native, Session16/Workerinput16 ohne SKIP PASS, unabhängiger Review,
FullTree/Sync und eigene lokale/Remote-Branchabwesenheit bestätigt.
[Abschlussbindung PR270](https://github.com/gecompat/SQL_PerformanceSchulung/pull/270).

Nächster endlicher Schnitt: [erste direkte Proxy-SOURCE-Invocation nach tatsächlichem EOF](DGN_007_PROXY_LOADER_SOURCE_REVIEW.md), eigener Branch
`codex/dgn007-proxy-loader-source`, ein Owner/max6/Checkpoint2/hart6.
Auswahl-PRE unabhängig mit präziser Handoff-/Wire-/Cacheauflage freigegeben.
C1 ergänzt additive Quelle und16eigene Modelle, nur optionale sichere Builder-
Fixtureerweiterung. Noch keine Suiteimporte oder Generierungs-/Compile-/Execproben;
C1 unabhängig mit einem P2 ohne Lauf-GO: ursprüngliche I/O-Report-used-/
Eingangsbytezählerbindung vollständig fortsetzen. C2 schließt die Prüfungen und
ergänzt sieben späte Writer-Gegenproben ohne Wire-Rücknahmebehauptung.
Checkpoint2 abgeschlossen: C2 unabhängig geschlossen und Lauf-GO erteilt;
neue16 Windows/Linux jeweils16SCRIPT_LIMIT-Fehler vor Modellsemantik.
C3 mit unabhängigem GO danach ebenfalls16SCRIPT_LIMIT auf Windows/Linux.
Einmalige freigegebene Größendiagnose:138588Bytes,7516über Cap; keine entbehrlichen
Definitionen im nötigen Umfang. C4 nach unabhängig präzisiertem Auswahl-GO:
ausschließlich nicht eingefangene lokale Körperbindungen kürzen, Schnittstellen/
Closures/Comprehensions sperren, bijektiv unabhängig rückführen und danach volle
AST-/Literal-/Operationsgleichheit. C4 unabhängig mit Lauf-GO, neue16 Linux ohne
SKIP PASS einschließlich Fit/Alpha-AST. Windows genau eine Gegenprobe wegen
eines bereits beim eigenen Splitdict-Fixtureaufbau ausgelösten EQ fehlgeschlagen.
C5 installiert dieselbe Fremdschlüsselmutation vollständig vor Erreichtmarker,
Namespaceidentität und Null-EQ-Oracle erhalten; Produkt unverändert.
C5 gezielt Linux PASS, Windows weiterhin Setup-EQ beim clear/update der Spec-
Splitdict, Erreichtmarker korrekterweise leer. C6 setzt nur beim Spec die fertige
Map bei gleicher Specinstanz/-klasse ein; Instanznamespace-Mapidentität hier
ausdrücklich geändert, übrige drei Namespaceidentitäten erhalten. Null-EQ-Oracle
und Produkt unverändert. C6 unabhängig ohne offene P1/P2/P3 mit gezieltem GO;
geänderte Methode danach Windows8.169s/Linux5.716s ohne SKIP PASS, übrige15
lokale Ergebnisse unverändert gültig. Vollständige neue16/alter Eingangsconsumer
folgen in selektierter CI (Continuous Integration; automatisierte Integrationsprüfungen). Sechs Kandidaten/hart6, fünf Nachläufe geschlossen;
kein weiterer Kandidat. Reservierter regulärer Head-/Base-/Main-Gate-, Integrations-
und Bereinigungsabschluss folgt. Additive
Quelle bindet ausschließlich Proxy2/Index2 an tatsächliche I/O-/Payload-/Writer-
Handoffs und dieselben Budgethalter, BEGIN vor gehaltenem Rawcompile, COMPLETE
nach tatsächlichem Exec und kohärenten POSTs. Keine öffentlichen Receipts als
Authority, keine neue Reserve/Globals-/Closurebaseline. Eigene synthetische
Modelle erst nach unabhängigem Source/Test-PRE mit ausdrücklichem Lauf-GO.
Keine operative Quellenwahl, DGN-Rawexecution, native Inventur oder SQL; Runner/
Harness, Parents, Footer/gesamte Importfolge und übrige Gesamtgates bleiben offen.
Verbrauch UNKNOWN; frühere Scopes abgeschlossen, kein Reset.

## Gemeinsame Child-I/O-Reserve vom 20. Oktober 2026

PR269 vollständig in `e456c535bc7a75d72d5034587657f6bcb46a27dd` integriert:
neun finale PR-Checks/sieben frische Main-Workflows SUCCESS, neue16 Windows/
Linux/Main und bestehende Report16 ohne SKIP PASS, unabhängige Befundschließung,
FullTree/Sync und eigene lokale/Remote-Branchabwesenheit bestätigt.
[Abschlussbindung PR269](https://github.com/gecompat/SQL_PerformanceSchulung/pull/269).

Nächster endlicher Schnitt: [Child-I/O-Vorbuchung aus dem gemeinsamen Parentbudget](DGN_007_CHILD_IO_RESERVATION_REVIEW.md), eigener Branch
`codex/dgn007-child-io-reservation`, ein Owner/max4/Checkpoint1/hart4.
Auswahl-PRE unabhängig freigegeben. C1 ergänzt einmalige sticky Vorbuchung,
getrennte Reportdiagnose, zwölf eigene portable Budget-/Ownerordnungsmodelle
und strengere native io_limit-Gegenprobe. Checkpoint1: ein Kandidat/max4,
keine Nachläufe; Source/Test-PRE unabhängig ohne offene Befunde mit ausdrücklichem
Lauf-GO. Danach neue12 Windows 3.14.7/Linux 3.12.3 und bestehende Linux-Handshake12
mit28Nativefällen/Session16 ohne SKIP PASS. Produkt/Suite unverändert, nur
Ergebnisstand ergänzt. Head-/Base-/Main-Gates und regulärer Abschluss folgen. Die feste
1088-je-Slot-Reserve soll vor erster nativer Wirkung aus4096Globaloperationen
gebucht werden; tatsächliche Parentoperationen separat. Keine operative Auswahl
der PR269-Quelle, keine neue Workerquelle und keine tatsächliche Inventur/SQL.
Bestehende genaue Linux-Nativefixtures erst nach unabhängigem Source/Test-PRE
mit ausdrücklichem Lauf-GO. Sämtliche übrigen offenen Gesamtlauf-/Loader-/Trust-
und Methodengates bleiben erhalten. Verbrauch UNKNOWN.

## Workerquelle für die vollständige Eingangsfolge vom 20. Oktober 2026

PR268 vollständig in `dcc5893af0c50c88aa0f848c3c908733c15dcbdc` integriert:
dreizehn finale PR-Checks/elf frische Main-Workflows SUCCESS, neue16 und alte15
ohne SKIP PASS, unabhängige Befundschließung, FullTree/Sync und eigene lokale/
Remote-Branchbereinigung bestätigt.
[Abschlussbindung PR268](https://github.com/gecompat/SQL_PerformanceSchulung/pull/268).

Nächster endlicher Schnitt: [Workerquelle für die vollständige Eingangsfolge
bis IMPORT_RELEASE und EOF (End of File; Ende eines Eingabestroms)](DGN_007_WORKER_INPUT_SOURCE_REVIEW.md), eigener
Branch `codex/dgn007-worker-input-source`, ein Owner/max6/Checkpoint2/hart6.
Auswahl-PRE unabhängig mit stabilen Haltern und vollständigen Triggerabhängigkeiten
freigegeben. C1 ergänzt vollständige Quellenfolge und16eigene I/O-Modellmethoden.
Direkter tatsächlicher Kernelhandoff vor Scriptsnapshot, keine spätere
Rebaseline oder neue Ausschlussliste. C1 unabhängig mit einem P2 ohne Lauf-GO:
OS-Namespacekeys und veränderbarer Modultyp vor Lookup/Attributzugriff schließen.
C2 ergänzt den vollständigen Schlüsselvorlauf und PRE-/Callback-POST-Gegenproben
mit externen Fremdaufruf-/Dispatchzählern. Checkpoint2: zwei Kandidaten/max6,
ein geänderter Nachlauf; C2 unabhängig geschlossen und mit Lauf-GO. Neue16
Windows/Linux danach jeweils16SCRIPT_LIMIT-Fehler vor innerer Modellsemantik,
Windows zusätzlich verzögert geladenes Stdlib-_ast_unparse im Cache-Orakel.
C3 verkürzt nur tokengeprüfte Codeeinrückung der neuen Ausgabe bei vollständigem
AST-/Literalerhalt und bereitet den neutralen Stdlibdarsteller vor Testbaseline
vor. Drei Kandidaten/max6, zwei Nachläufe; unabhängiger Delta-PRE und Lauf-GO
erteilt; C3 danach neue16 Windows3.14.7 in36.223s und Linux3.12.3 in25.617s
ohne SKIP PASS. Vollständiger Quellenfit/AST-/Literalerhalt, alle drei Rollen
und sämtliche eigenen negativen I/O-Modelle bestätigt. Produkt/Suite unverändert,
nur Ergebnisdokumentation ergänzt; aktuelle Head-/Base-/Main-Gates, Integration
und eigener Branchcleanup folgen. Keine Capänderung oder alten Routenänderungen.
Keine echten OS-I/O (Input/Output; Ein- und Ausgabezugriffe)/Main-/Worker-
ausführungen, operative Inventur oder SQL. Die geplante Child-I/O-Teilreserve
aus dem vorhandenen Globalbudget ist noch nicht im Parent gebucht; operative
Admission deshalb ausdrücklich offen. Vollständige Installations-/S15/P11-/
Fünf-Formen-/Loader-/SESSION_END-/Trust-/Methodengates bleiben offen.
Verbrauch UNKNOWN; bisherige ausgeschöpfte Scopes bleiben geschlossen.

## Empfangene Metadata und aufgenommener Workerreport vom 20. Oktober 2026

PR267 vollständig in `84272af549d1c7c1320b5b1c77a55a4b721f8d18` integriert:
zwölf finale PR-Checks/zehn frische Main-Workflows SUCCESS, neue15 Windows/Linux
und bestehende Consumer ohne SKIP PASS, unabhängige P2-Schließung,
FullTree/Sync und eigener lokaler/Remote-Branchcleanup bestätigt.
[Abschlussbindung PR267](https://github.com/gecompat/SQL_PerformanceSchulung/pull/267).

Nächster endlicher Schnitt: [vollständige Metadata mit tatsächlicher Aufnahme
und Workerreport verbinden](DGN_007_OBSERVED_WORKER_REPORT_REVIEW.md), eigener
Branch `codex/dgn007-observed-worker-report`, ein Owner/max6/Checkpoint2/hart6.
Auswahl-PRE unabhängig ohne Befunde freigegeben. C1 verbindet vollständigen
Empfang, echte Aufnahme und Reporter mit vorab gehaltenen äußeren Ankern und
einmaliger Reservierung;16neue Modellmethoden. C1 unabhängig mit zwei P2 ohne
Lauf-GO. C2 schließt Builtinslot und selbstgewählte Bindingautorität durch eine
separat versiegelte private Entryclosure und zwei Markerersatz-Gegenproben.
Checkpoint2: C2 unabhängig geschlossen und mit Lauf-GO, danach neue16 auf
Windows/Linux jeweils15SCRIPT_LIMIT-Fehler und eine negative Methode PASS;
eigentliche Reportfälle noch nicht ausgeführt. C3 entfernt nur in der neuen
Route einen unbenutzten Parentmatcher und reine Kommentar-/Leerzeilen bei
vollständigem unabhängigen AST-Erhaltcheck. Drei Kandidaten/zwei Nachläufe,
C3 unabhängig ohne offene Befunde mit Lauf-GO; danach neue16 Windows/Linux
ohne SKIP PASS einschließlich vollständigem neuen Quellenfit und AST-Erhalt.
PR268: neue16 in CI PASS, zwölf Checks SUCCESS; alte15 mit einem zu strengen
globalen Builderzählungsfehler FAIL. C4 bindet die alte Prüfung an ihren eigenen
sechzehnten Index/eindeutigen API-Namen/festen Unterbau; Produktcode und neue16
unverändert. C4 unabhängig ohne offene Befunde mit gezieltem Lauf-GO; geänderte
einzelne Methode Windows/Linux ohne SKIP PASS. Vier Kandidaten/drei Nachläufe;
frische finale Headgates und reguläre Integration folgen.
Kein Merge mit fehlerhaftem Gate und kein Capwechsel oder alter Fitretry.
Keine operative Script-/Pipeausführung, Inventur oder SQL. Alle tatsächlichen
Worker-/Import-/Trust-/Methodengates bleiben offen. Verbrauch UNKNOWN.

## Workerquelle und gebundene Profilaufnahme vom 20. Oktober 2026

PR266 vollständig in `ded09f685f747bb614c68c0fa78a6e54be7514be` integriert:
sieben finale PR-Checks/fünf Main-Workflows SUCCESS, unabhängige Einordnung,
FullTree/Sync und eigene lokale/Remote-Branchbereinigung bestätigt.
[Abschlussbindung PR266](https://github.com/gecompat/SQL_PerformanceSchulung/pull/266).
Der operative Fit der bisherigen vollständigen fünfzehnten Route bleibt FAIL;
deren ausgeschöpfter Nachweisscope wird nicht wiederholt oder neu benannt.

Nächste tatsächliche Implementierung: [Workerquelle mit gebundener
Profilaufnahme](DGN_007_WORKER_PROFILE_SOURCE_REVIEW.md), eigener Branch
`codex/dgn007-worker-profile-source`, ein Owner/max6/Checkpoint2/hart6.
Additive rollenbezogene Zusammensetzung aus bestehendem vollständigem
Workerunterbau und neuer Inline-Profilverbindung; Parentmatcher unverändert.
Auswahl-PRE unabhängig mit vollständiger Kontrollpfadbindung als Auflage
freigegeben; C1 ergänzt neue Workerroute und zwölf eigene Modellmethoden.
Source/Test-PRE C1 mit zwei P2 (3.14-Annotationträger/Keyvorlauf) ohne Lauf-GO.
C2 schließt beide, ergänzt gemeinsamen Zustandsrahmen und drei Gegenproben:
15Methoden, Checkpoint2/zwei Kandidaten/ein Nachlauf. C2 unabhängig ohne
offene P1/P2/P3 und mit einmaligem Source/Test-Lauf-GO bestätigt.
Neue15 unter Windows 3.14.7/Linux 3.12.3 ohne SKIP PASS; vollständiger neuer
Arbeitsdatei-Quellenfit innerhalb des unveränderten Caps bestätigt.
Reguläre aktuelle Head-/Base-/Main-Gates und Integration folgen.
Caps und vollständige Workerprüfungen bleiben erhalten; keine operative
Inventur, Kandidatenimporte oder SQL, Attestationsgrenzen offen. Verbrauch UNKNOWN.

## Vollständiger aktueller Kontrollquellen-Fit vom 20. Oktober 2026

PR265 vollständig in `966f2251bc301a1ac80997c591962f929a7a136c` integriert:
zehn finale PR-Checks/acht Main-Workflows SUCCESS; neue16/Binder16 unter
Windows/Linux und alte57 unter Linux ohne SKIP PASS, unabhängige P2/P3-
Schließung, FullTree/Sync und eigene lokale/Remote-Branchbereinigung bestätigt.
[Abschlussbindung PR265](https://github.com/gecompat/SQL_PerformanceSchulung/pull/265).

Nächster endlicher Schnitt: [vollständige aktuelle Profilbytes im bestehenden
Inlinegenerator prüfen](DGN_007_CURRENT_CONTROL_SOURCE_FIT_REVIEW.md).
Ein Owner/max3/Checkpoint1/hart3 einschließlich Review/Rechnung/Gates/Integration.
Auswahl-/Source-/Lauf-PRE unabhängig ohne Befunde freigegeben. Ein gebündelter
lokaler Aufruf: Tiny5Bytes erzeugt vollständige100245Bytes; Oversize131073
scheitert PROFILE_SIZE. Vollständige aktuelle Arbeitsdatei44542Bytes und
Gitblob43658Bytes scheitern beide SCRIPT_LIMIT. Konkreter operativer Fit FAIL;
keine erzeugte Gesamtlänge/-SHA für abgelehnte Inputs behauptet. Checkpoint1,
drei Dokumentationsstände/max3, kein Rerun; unabhängige Einordnung ohne offene
P1/P2/P3 bestätigt, reguläre Integration des Nachweises ausstehend. Keine neue
Arbeit in diesem ausgeschöpften Scope. Eigener Branch `codex/dgn007-control-source-fit`.
Keine generierte Ausführung, Workerinventur, SQL oder Capänderung. Verbrauch
UNKNOWN. Quellenarchitekturkorrektur ist möglicher getrennter Folgeschnitt,
hier noch nicht ausgewählt. Historische Stops und Provenienzgrenzen erhalten.

## Gewählte Profilanker und lokale Aufnahme vom 20. Oktober 2026

PR264 vollständig in `5bf9d14a46b0fba1184f6a5a6dc3772c6278cb17` integriert:
13finalePR-Checkruns und11Main-Workflows SUCCESS, unabhängige Befundschließung,
lokale relevante Vertrags-/Linkprüfungen, FullTree/Sync und eigene lokale/
Remote-Branchbereinigung bestätigt. [Abschlussbindung PR264](https://github.com/gecompat/SQL_PerformanceSchulung/pull/264).
Der menschliche Projekteinstieg und korrigierte Lehrmaßstab sind damit
abgeschlossen; Root-README erhält keine internen Streamstatusnachträge.

Nächster endlicher Schnitt: [vorgewählte Profilanker und frische lokale Aufnahme
verbinden](DGN_007_SELECTED_PROFILE_OBSERVATION_REVIEW.md), ein Owner/max6/
Checkpoint2/hart6 einschließlich Reviews/Tests/CI/Integration. Auswahl-PRE
unabhängig freigegeben; C1 unabhängig mit Runtime-POST-P2 und Hooktest-P3,
ohne Lauf-GO. C2 bündelt callbackfreien letzten Syswert-POST und Gegenproben
nach drittem Capture sowie Code-/Closure-Identitäten, weiterhin16Methoden.
Checkpoint2: zwei Kandidaten/max6, ein Nachlauf; C2 unabhängig ohne offene
P1/P2/P3 und mit Lauf-GO. Neue16/Binder16 unter Windows/Linux jeweils ohne SKIP
PASS; aktuelle PR-/Base-/Main-Gates, FullTree/Sync/Branchcleanup ausstehend.
Eigener Branch
`codex/dgn007-selected-profile-observation`. Neue Tests ausschließlich eigene
synthetische Runtime-Modellumgebung, keine operative Installation/Workerinventur.
Tatsächliche Worker-/Loader-/Importprovenienz und physische Auswahl bleiben
offen; keine Attestation aus Modell-PASS. Verbrauch UNKNOWN.

## Menschlicher Projekteinstieg und Lehrmaßstab vom 20. Oktober 2026

PR263 vollständig in `4a8d5aa2e6252803d7773b9e075c1bbfc4d8e5df` integriert:
neun PR-/sieben Main-Gates SUCCESS, neue16/alte57 unter Linux ohne SKIP,
unabhängiger Review, FullTree/Sync und eigene lokale/Remote-Branchbereinigung
bestätigt. Historischer Windows57-Fixture-FAIL bleibt im Nachweis erhalten.
[Abschlussbindung PR263](https://github.com/gecompat/SQL_PerformanceSchulung/pull/263).

Der neu priorisierte menschliche Auftrag führt zum [anwenderorientierten
Projekteinstieg und korrigierten Lehrmaßstab](PROJECT_ENTRY_AND_TEACHING_SCOPE_REVIEW.md).
Ein Owner, unabhängiger inhaltlicher Review, max4/Checkpoint1/hart4 einschließlich
aller Checks, Gates und Integration. C1 überarbeitet die menschlichen Einstiege,
grenzt Messdemos von Erklärungen/Lösungsmustern ab und klärt die erhaltenen
Archivquellen sowie die damalige REMOVE-Kennzeichnung. Keine neue SQL-/Runtime-
Ausführung, keine Gateabsenkung bestehender Demopakete und keine neue Messbehauptung.
Branch `codex/human-project-entry`; C1 unabhängig ohne P1/P2 und mit einem P3.
C2 schließt den verbliebenen pauschalen Evidenzsatz lernzielbezogen. Übriger
Schnitt freigegeben; lokale Vertragsprüfungen und71neueLinks/Anker PASS.
Zwei Kandidaten/max4, ein enger Nachlauf; reguläre aktuelle Gates folgen.
Danach bleibt die autonome technische Fortsetzung im bereits autorisierten
Rahmen möglich; zuerst diesen priorisierten Schnitt vollständig abschließen.
Verbrauch UNKNOWN, bestehender30-Minuten-Heartbeat unverändert aktiv.

## Vollständige Profilauswahl an lokale Anker vom 20. Oktober 2026

PR262 vollständig in `9938091d7de38bb95152cc06e055470e5fb8b7cc` integriert:
zehn finale PR-Gates, acht Main-Workflows SUCCESS, neue12/12, alte Kanal16/16
und pure Eingangsplan16/16 Methoden in CI/Main ohne SKIP. Unabhängiger Review,
FullTree/Sync und eigene lokale/Remote-Branchbereinigung bestätigt; ein
Quellen-/Teststand, keine Befundnachläufe. [Abschlussbindung PR262](https://github.com/gecompat/SQL_PerformanceSchulung/pull/262).

Nächster endlicher Schnitt: [vollständige separat gewählte S15-/P11-Felder an
explizite lokale Anker binden](DGN_007_SELECTED_PROFILE_ANCHORS_REVIEW.md).
Ein Owner, max6/Checkpoint2/hart6 einschließlich Review/Tests/CI; Auswahl-PRE
ausdrücklich freigegeben. C1 implementiert additive Brücke und engen gefundenen
Frozen-/Mixed-Guardfix mit15 vollständig synthetischen portablen Methoden.
Reine Brücke vor späterer frischer Aufnahme, keine Selbstbaseline oder neuen
I/O/Hash/Hook-/Observation-/Prozessaufrufe. Eigener Branch
`codex/dgn007-selected-profile-anchors`.
C1 unabhängig mit einem Keygrenzen-P2, ohne Lauf-GO; C2 bündelt dessen
Schließung mit gemeinsamer begrenzter Keyverarbeitung und16.Methoden-Gegenprobe.
Checkpoint2 erreicht: zwei Kandidaten, ein Nachlauf, hart6 unverändert. C2-
Delta-PRE ohne offene Befunde und mit ausdrücklichem Lauf-GO bestätigt:
neue16/16 unter Windows/Linux ohne SKIP PASS. Alte Windows57 FAIL (24Fehler,
fünfERROR/dreiSKIP) durch unveränderte POSIX-isabs-Fixture auf Windows3.14;
historisch erhalten, unabhängig eingeordnet und einmalige Plattformkorrektur
freigegeben. Alte57/57 unter Linux3.12 isoliert ohne SKIP PASS. Aktuelle Gates,
reguläre Integration und FullTree/Sync/Branchcleanup folgen. Anschließend priorisiert der neue
Benutzerhinweis eine anwenderorientierte README und eindeutige Archiv-/
Migrationsbegriffe und einen maßgeblichen Lehrmaßstab ohne pauschale Messpflicht;
weitere technische Aufnahme folgt erst nach diesem Einstiegsschnitt.
Operative Auswahl/Inventur, Fünf-Formen-Gate und echte Loader-/Importprovenienz
bleiben offen. Verbrauch UNKNOWN; kontinuierlicher Auftrag/30-Minuten-Heartbeat aktiv.

## Bidirektionaler Phasenowner vom 20. Oktober 2026

PR261 vollständig in `0d851dc9f87915a4952ad6fae1fe0f269f94d5e7` integriert:
acht finale PR-Gates, sechs Main-Workflows SUCCESS,16/16 neue Methoden ohne
SKIP auf Windows/Linux und Main-CI, unabhängiger Review, FullTree/Sync und
eigene lokale/Remote-Branchbereinigung bestätigt. Ein Quellen-/Teststand,
keine Befundnachläufe; [Abschlussbindung im PR261](https://github.com/gecompat/SQL_PerformanceSchulung/pull/261).

Der kontinuierliche menschliche Auftrag und bestehende30-Minuten-Heartbeat
führen nun zum [nativen bidirektionalen Phasenowner](DGN_007_BIDIRECTIONAL_HANDSHAKE_REVIEW.md).
Auswahl-PRE ohne offene Befunde freigegeben; ein Owner, maximal acht neue
Quellen-/Testkandidaten, Checkpoint2/hart8 einschließlich Reviews/Tests/CI.
Private gemeinsame Owner-/Cleanupseams erhalten die alte öffentliche API (Application Programming Interface; Programmierschnittstelle).
Metadata/Profil/BODY_RELEASE/neun Bodies/BODY_END/INPUT_COMPLETE/IMPORT_RELEASE
und stdin-Schluss werden innerhalb derselben geteilten Budgets an echte
I/O-Rückgaben und volle Caller gebunden. Kein echter DGN-Import-/Loader- oder
frischer S15/P11-Beleg; feste selbstbeendende eigene Native-Testprogramme.
C1 `83d9f325abd539b60834312abbaf7746cb529981` unabhängig vollständig ohne
offene P1/P2/P3-Befunde und mit ausdrücklichem Source/Test-Lauf-GO bestätigt.
Lokale Linux3.12.3-Läufe: neue12/12 Methoden mit28 festen Nativefällen und
alte16/16 ohne SKIP PASS. Windows3.14.7: drei/fünf portable PASS und neun/elf
native SKIP. Ein Kandidat, keine Befundnachläufe; pure Plansuite lokal nicht
wiederholt. Aktuelle Head-/Base-/Main-Gates und FullTree/Sync/Branchcleanup
folgen vor Abschluss. Eigener Branch `codex/dgn007-bidirectional-handshake`;
historische Stops bleiben erhalten. Verbrauch UNKNOWN.

## Gehaltener Handshakeeingang vom 20. Oktober 2026

PR260 ist vollständig in `256e43d6d4ca4ac7a248dadbe4c88e6923577ef4` integriert:
acht finale PR-Gates und sechs Main-Workflows SUCCESS, native Suite16/16 ohne
SKIP, unabhängiger Review einschließlich ausdrücklich genehmigtem C4, FullTree,
Main-Synchronisierung und eigene lokale/Remote-Branchbereinigung bestätigt.
Historische C3-Fixture-FAIL und ausgeschöpfte Grenzen bleiben erhalten.

Der erneut ausdrücklich autorisierte kontinuierliche Auftrag führt zum
[gehaltenen vollständigen Handshakeeingang vor Start](DGN_007_HANDSHAKE_INPUT_PLAN_REVIEW.md).
Unabhängiger Auswahl-PRE ohne offene Befunde; ein Owner, höchstens sechs neue
Quellen-/Testkandidaten, Checkpoint2/hart6 einschließlich Reviews/Tests/CI.
Primitive Caller-/Transportvorläufe aller Slots vor Encoder/SHA, vorhandener
Bodyguard je Slot, separate ganze R4-Bindung, fünf tatsächliche E4-Formen und
drei Commands gemeinsam im Transfercap. Reiner atomarer Plan, keine native
I/O-/Start-/Verbrauchs-/Importattestation. C1 `77687b1431a874863890edb6a4643c5840ab7c59`
ist unabhängig ohne offene Befunde und mit ausdrücklichem Source/Test-Lauf-GO
bestätigt. Erste lokale isolierte Suite16/16 ohne SKIP auf Windows3.14.7
und Linux3.12.3 bestanden. Ein Kandidat verbraucht; aktuelle PR-/Main-Gates,
reguläre Integration und FullTree/Sync/Branchcleanup folgen vor Abschluss.
Bestehende Builder, native Kanalquelle und Runtime-/SQLquellen unverändert.
Branch `codex/dgn007-held-handshake-input`, Basis identisch mit origin/main.
Verbrauch UNKNOWN, bestehender 30-Minuten-Heartbeat bleibt kontinuierlich aktiv.

## Operative Abschlusswelle und kontinuierlicher Auftrag vom 20. Oktober 2026

PR259 ist vollständig in `d4151093bdd4de115b660352345f3e5c47e9b650` integriert:
acht finale PR-Gates, sechs Main-Workflows, unabhängiger Review, vollständiger
Treevergleich, Main-Synchronisierung und eigene lokale/Remote-Branchbereinigung
sind bestätigt. Historische C1/C2-Befunde und das ausgeschöpfte C3-Budget bleiben
im [Matcher-Nachweis](DGN_007_SESSION_END_MATCHER_REVIEW.md) erhalten.

Der neue ausdrückliche Benutzerauftrag autorisiert die operative Kanal-/EOF-/
Exit-/Cleanup-Anbindung und anschließend kontinuierliche autonome Entwicklung.
Der [erste operative Abschlussweg](DGN_007_NATIVE_SESSION_CHANNEL_REVIEW.md)
besitzt einen eigenen endlichen Rahmen: ein Owner, höchstens drei neue Quellen-/
Teststände, Checkpoint C1 und harte Grenze C3. C1 vier P2, C2 drei geschlossen,
C3 letzter Nonce-P2 geschlossen; unabhängiges ausdrückliches Lauf-GO vorhanden.
Windows: fünf portable PASS/elf native SKIP. Linux: 16 Methoden, 15 PASS/ein
Fixture-FAIL `bad_nonce`: INPUT_COMPLETE-Suche dekodiert vorherige `P|`-Fragmente
als JSON (JavaScript Object Notation; strukturiertes Textformat) und bricht vor dessen Workerstart ab. Drei Kandidaten und zwei
gezielte Nachläufe verbraucht; historischer Stop `BLOCKED_BUDGET_AFTER_C3_TEST_FAIL`.
Der Mensch hat C4 ausdrücklich freigegeben: eine Fixturekorrektur, ein enger
unabhängiger Delta-PRE/Lauf-GO und der betroffene Linux-Test; danach aktuelle
vollständige CI/Main-Integration/Tree/Branchcleanup. C4 wählt INPUT_COMPLETE
am kanonischen Bytepräfix vor dessen JSON-Dekodierung; alle operativen Quellen
bleiben unverändert. C4 `41e188d66e62d81e483d5765784fd21ea7a5a490` ist unabhängig
ohne offene Befunde und mit ausdrücklichem Lauf-GO bestätigt; lokaler Linux-
Ziellauf mit allen fünf negativen Kanal-/Footerfällen PASS in 3,025 Sekunden.
Status `PR_GATES_PENDING`. Vollständige aktuelle CI16 und Main-Abschluss folgen;
eigener Branch `codex/dgn007-native-session-channel` bleibt bis zum Nachweis erhalten.
Die nächste priorisierte endliche Welle ist nach vollständigem Abschluss
erneut ausdrücklich autorisiert; keine Wiederholung des ausgeschöpften C3.
Native Abnahme ausschließlich mit festen selbstbeendenden eigenen Linux-
Testworkern und synthetischen vollständigen Traces, keine reale Importfreigabe.
Bestehender Heartbeat aktiv alle 30 Minuten auf denselben kontinuierlichen
Auftrag begrenzt; keine zusätzliche Automation und kein zweiter Owner.
Nach vollständiger Integration folgt genau die nächste priorisierte endlich
abgegrenzte Welle. Echte Blocker, unverbrauchte fremde Freigabegrenzen und
historische Stops bleiben wirksam. Token-/Kostenverbrauch unbekannt.

## Matcherwelle vom 20. Oktober 2026

PR258 ist in `d0c453f212523fa30c8d74ee47fcbb15f84b8b54` integriert; acht grüne
finale PR-Gates, sechs erfolgreiche Main-Workflows, vollständiger Treevergleich
und lokale/Remote-Branchbereinigung sind bestätigt. Auf neuen ausdrücklichen
Benutzerauftrag folgt der [vollständige deklarative SESSION_END-Matcher](DGN_007_SESSION_END_MATCHER_REVIEW.md).
Die API-/Source-/Harnessauswahl ist unabhängig ohne Befunde freigegeben.
Ein Owner, höchstens drei Quellenstände und Checkpoint nach dem ersten.
Der Erststand auf `codex/dgn007-session-end-matcher` ergänzt ausschließlich eine
fünfzehnte kontrollierte Quellenroute und eigene Gegenproben. C1-P2 zur
Fehlerlabellänge ist in C2 geschlossen; dessen erster Lauf scheiterte an zwei
Testhelperfällen auf beiden Plattformen. C3 korrigiert ausschließlich den
negativen Footerindex und ist unabhängig mit gezieltem Lauf-GO bestätigt.
30 neue isolierte Methoden auf Windows/Python 3.14.7 und Linux/Python 3.12.3
ohne SKIP bestanden, dazu 460 bisherige Kontrollquellenmethoden unter Windows
auf unveränderter Quelle. Keine offenen Reviewbefunde, drei Quellenstände
verbraucht, kein weiterer Implementierungsstand dieser Welle. Die Evidenzrevision
von [PR259](https://github.com/gecompat/SQL_PerformanceSchulung/pull/259) bindet
finale Head-/Base-Gates, Main-Integration und Branchbereinigung vor Abschluss.
Vollständiger deklarativer Match
ersetzt keine reale Kanalaufnahme, EOF, eigenen Exit oder Ressourcen-Cleanup.

## Fortsetzung vom 20. Oktober 2026: reine SESSION_END-Komponenten

PR256 ist mit acht verschiedenen grünen PR-Checks und sechs erfolgreichen
Main-Workflows in `131e19651c57a829080093cbe2b6767a0ab462d8` integriert;
vollständiger Treevergleich und lokale/Remote-Branchbereinigung sind bestätigt.
Der Benutzer beauftragt erneut den autonomen Abschluss des aktuellen Streams,
Merge nach lokalen Tests und die nächste priorisierte Welle.

Die [beiden reinen SESSION_END-Komponenten](DGN_007_SESSION_END_COMPONENTS.md)
sind vor der Implementierung unabhängig ausgewählt: zuerst Footer-Codec,
anschließend Kanalhashfunktion. Ein Implementierungsowner, höchstens zwei
Quellenkandidaten je Schnitt, Checkpoint jeweils nach dem ersten und ein
unabhängiger Implementierungsreview je Schnitt. Der Footer-Erststand besteht
13 lokale isolierte Testmethoden unter Windows/Python 3.14.7 und
Linux/Python 3.12.3 ohne SKIP. [PR257](https://github.com/gecompat/SQL_PerformanceSchulung/pull/257)
ist nach unabhängigem Implementierungsreview ohne Befunde und acht verschiedenen
grünen finalen PR-Gates in Main `5466a445574f283b1a3b43c55449cc79fb551234`
integriert. Vollständiger Treevergleich, alle sechs Main-Workflows und lokale/
Remote-Branchbereinigung sind bestätigt.

Darauf beginnt die Kanalhashfunktion auf `codex/dgn007-session-channel-digest`.
Ihr erster Quellenkandidat besteht mit den 13 erhaltenen Footer- und neun neuen
Kanalhashmethoden insgesamt 22 lokale isolierte Methoden unter Python 3.12/3.14
ohne SKIP. Checkpoint 1/2, insgesamt zwei von vier Quellenkandidaten;
unabhängiger Implementierungsreview zu `7cd88de…` ohne offene Befunde und alle
acht CI-Gates dieses Stands erfolgreich. Die Abschlussrevision von
[PR258](https://github.com/gecompat/SQL_PerformanceSchulung/pull/258) ergänzt nur
Evidenz und bindet finale Head-/Base-Gates, Main-Integration und Bereinigung.
Die zwei ausgewählten Implementierungsschnitte sind damit lokal geprüft und
unabhängig reviewt; der Integrationsabschluss bleibt bis zu diesen Gates offen.
Beide Schnitte liegen außerhalb der
neun Runtimequellen und liefern keinen vollständigen Trace-/Kanal-/EOF- oder
Runtime-/Trustnachweis. Keine Wiederaufnahme ausgeschöpfter Wellen und keine
zusätzliche operative Konfiguration.

## Wiederaufnahme vom 20. Oktober 2026: Capture integriert, SESSION_END-Entwurf

Der ausdrückliche Benutzerauftrag hebt die frühere allgemeine Entwicklungspause
auf. Die interne Rückgabe aus dem erhaltenen Entwurf `83f08fb…` ist nach
unabhängigem Quellenreview ohne offene Befunde und allen 14 grünen PR-Gates
über [PR255](https://github.com/gecompat/SQL_PerformanceSchulung/pull/255) in
Main `b3f023ad66f8c4aa16a7c6fe73e42615818cbd90` integriert. Vollständiger
Treevergleich, lokale Main-Synchronisierung und sichere Entfernung beider
lokalen Capture-Branches sowie des eigenen Remote-Branches sind abgeschlossen.
Der [Capture-Nachweis](DGN_007_INTERNAL_CAPTURE_RECEIPT_REVIEW.md) bindet Tests,
Review, SQL2019/2022/2025 und Cleanup. Der automatisch gestartete
[Main-Lauf](https://github.com/gecompat/SQL_PerformanceSchulung/actions/runs/39387949894)
bestand erneut mit 36 Lifecycles, unabhängigen DB-Prüfungen und vollständigem
eigenem Container-/Volumecleanup. Alle acht Main-Workflows sind erfolgreich.
DEC-072/PR132 haben die ältere G13-/Zeitquellensperre dieses Scopes abgelöst;
historische FAILs und größere offene Methodengates bleiben erhalten.

Nach diesem Abschluss ist auf `codex/dgn007-session-end-design` ausschließlich
der [SESSION_END-Vertragsentwurf §34](DGN_007_IMPORT_PROFILE_BINDING_DESIGN.md#34-session_end-counts-und-kanalhashpräbild)
aufgenommen: ein Owner, höchstens zwei Entwurfsstände, Checkpoint nach dem
ersten und ein unabhängiger Designreview. Recordform, rollengenaue Counts,
Rohbytepräbild ohne Selbstbezug und unveränderte Kanalreserve sind ausgearbeitet;
57 Literalrechnungen und eine synthetische Hashreferenz sind nachgerechnet.
Der unabhängige Designreview bestätigt den Erststand `a6ca3f5…` ohne offene
P1/P2/P3-Befunde; alle acht Dokumentationsgates dieses Stands sind grün.
Die Abschlussrevision von [PR256](https://github.com/gecompat/SQL_PerformanceSchulung/pull/256)
führt ausschließlich Evidenz-/Planungsstände nach; Footer-, Count- und
Präbildvertrag bleiben gegenüber dem reviewten Erststand unverändert.
PR256 ist der belegführende Abschluss dieser Designwelle und bindet die
aktuellen Head-/Base-Gates, Main-Übernahme und eigene Branchbereinigung.
Kein Parser-/Builder-/Kanal-/Loader-/Worker- oder SQLlauf dieser Designwelle, keine neue
Admission für frühere ausgeschöpfte Import-/Generator-/Quellwellen.
Collector, operative Provenienzarchitektur und frische prospektive
Bestätigungsläufe bleiben eigene Aufgaben mit ihren offenen Gates.
Keine neue Scheduler-/Heartbeat-/Cloud-/Modell-/Credential-/Trustkonfiguration;
laufende Lab-CI und fremde Ressourcen bleiben geschützt. Die folgenden
Pausen- und Methodenstände sind historisch, soweit dieser aktuelle Auftrag
und DEC-072 sie ausdrücklich abgelöst haben.

## QRY-017: automatisierter Volltextpfad vom 19. Oktober 2026

Der Benutzer beauftragt die Prüfung der automatisierten Lab-Unterstützung,
die darauf aufbauende Fertigstellung und die saubere Main-Integration samt
Branchbereinigung. Der [gezielte Volltextnachweis](SQL_SERVER_2025_AI_FULLTEXT_REHEARSAL.md)
ist nativ bestanden: Lab-Kandidat3560b746, tatsächliche SQL-Engine17.0.4075.5
mit installierter Komponente, zwei vollständige QRY-017-Lifecycles mit je
fünf exakten Suchfällen und vier Ergebnisassertionen,48Markergegenfälle,
Idempotenz, Ergebnisgegenfall und unabhängiger DB-/Container-/Volumecleanup.
Der native Versuch endete mit Exitcode0 und freigegebenem Runtime-Mutex.
Ein übersprungener zusätzlicher Tenant-Gegenprobezweig wurde entfernt und
wird ausdrücklich nicht als geprüft bezeichnet. Lab-PR806 muss mit grüner
finaler CI vor dem Schulungsmerge in Main liegen. Gegenüber dem getesteten
Lab-Tree ist ausschließlich die korrigierte Linux-Sperrfehlererwartung in
der statischen Testfixture zulässig; sämtliche Produkt-/SQL-Quellen müssen
unverändert sein. Der finale Git-Vergleich ist Teil der Mergeprüfung.
Die historischen Kursproben behalten ihren optionalen Full-Text-WARN.
Keine zusätzliche Kurs-, Performance- oder vollständige Streamfreigabe.
Ausdrücklich zurückgestellte Arbeit und fremde Worktrees bleiben erhalten.

Der Benutzer ordnet anschließend ausdrücklich an: Sobald diese Welle
konsistent in `origin/main` integriert und bereinigt ist, pausiert die
autonome Verarbeitung. Keine weitere Welle und keine automatische
Wiederaufnahme; Fortsetzung erst nach einem neuen Benutzerauftrag.

## VERTIEFUNG Kurswelle vom 18. Oktober 2026

Nach STANDARD/PR251 (maind851638) beauftragt der Benutzer ausdrücklich den
[VERTIEFUNG-Zweitageskurs](../HowTo/SQL_SERVER_2025_AI_VERTIEFUNG_COURSE.md) samt
technischer Generalprobe und vollständiger origin/main-Integration.
61 native Kursfolien verbinden den vollständigen STANDARD-Tag mit konkreten
Beleg-/Entwurfsaufgaben und Musterlösungen für Tag 2; je 420+60 Planminuten.
Die [neue technische und redaktionelle Probe](SQL_SERVER_2025_AI_VERTIEFUNG_REHEARSAL.md)
ist abgeschlossen: 16 tatsächliche Offline-Demoläufe, 76 erfüllte Assertions,
unabhängiger DB-/Containercleanup, reine Tag-2-Rechen-/Belegprüfung und
PowerPoint-Anwendungstest. Optionaler Full-Text-WARN bleibt erhalten.
Teilnehmerpilot und gemessene Lehrzeiten bleiben offen; Grund und Wiederaufnahme
sind im Nachweis dokumentiert. Andere technische Wellen und Automation bleiben
pausiert. Keine volle TSK-012-/TSK-014-/Runtime-/Workstreamfreigabe.

## STANDARD Kurswelle vom 18. Oktober 2026

Nach dem integrierten BASIS-Kurs (PR250, main72b41c8) beauftragt der Benutzer
die nächste sinnvolle KI-Welle mit vollständigem Abschluss in origin/main.
Gewählter Umfang ist der [STANDARD-Tageskurs](../HowTo/SQL_SERVER_2025_AI_STANDARD_COURSE.md):
45 native Folien, acht Offline-Aufgaben, 420+60 Planminuten und vollständiger
Durchführungs-/Ausfallpfad. Die [technische und redaktionelle Generalprobe](SQL_SERVER_2025_AI_STANDARD_REHEARSAL.md)
ist abgeschlossen: 16 SQL-Lifecycles, 76 erfüllte Ergebnisassertionen,
unabhängiger DB-/Containercleanup und PowerPoint-Anwendungstest.
QRY-017 und damit die SQL-Gesamtprobe behalten den vorgesehenen optionalen
Full-Text-WARN. Teilnehmerpilot und gemessene Lehrzeiten bleiben getrennt offen.
VERTIEFUNG, übrige technische Wellen und Automation bleiben pausiert;
volle TSK-012-/TSK-014-/Workstreamabnahme wird nicht behauptet.

## BASIS Kurswelle vom 18. Oktober 2026

Der neue Benutzerauftrag nimmt ausschließlich den BASIS-Kurs samt Generalprobe
und vollständigem PR-/Main-Abschluss wieder auf. Das
[Kurspaket](../HowTo/SQL_SERVER_2025_AI_BASIS_COURSE.md) und der
[Generalprobenachweis](SQL_SERVER_2025_AI_BASIS_REHEARSAL.md) sind maßgeblich:
39 native Folien, 210+30 Planminuten, QRY-014/QRY-019 praktisch und QRY-018 als
Leseaufgabe. Technische und redaktionelle Probe bestanden; sechs vollständige
SQL-Lifecycles und QRY-019-Gegenfälle einschließlich eigenem Cleanup bestanden.
Der Teilnehmerpilot mit gemessenen Unterrichtszeiten bleibt ein ausdrücklich
getrennter Human-Nachweis; Grund und Wiederaufnahmebedingung stehen im Nachweis.
Die volle TSK-012-/TSK-014-Abnahme bleibt offen. Übrige Wellen und Automation
bleiben pausiert; der folgende Benutzerabschluss vom 14. Oktober ist historisch.

## Benutzerabschluss der Entwicklungswelle: keine autonome Fortsetzung

Am 14. Oktober 2026 hat der Benutzer ausdrücklich angeordnet, die aktuelle
Entwicklungswelle vollständig abzuschließen, keine neue Welle zu starten und
nach der Integration nach origin/main den Orchestrator-Chat zu beenden.
Diese Anweisung beendet die bisherige autonome Fortsetzung. Der zugehörige
Heartbeat ist tatsächlich PAUSED; andere Automationen bleiben unverändert.

Der letzte fachliche Schnitt ist über PR248 vollständig geschlossen:
Main9ab1c2255cc0c4a8b9f3b45a094bd2863b961fc7, acht erfolgreiche Head- und
sechs erfolgreiche Main-Checks, vollständiger gleicher Tree, synchrones
sauberes Main und eigene Branches entfernt.148 private Belegdateien sind
bytegenau gesichert und nach tatsächlicher Worktreearchivierung erneut geprüft.
Der historische öffentliche V2-Record ist kohärent mit WARN; der frühere FAIL
und sämtliche offenen Qualifikationsgrenzen bleiben unverändert erhalten.

Der ausschließlich leer vorbereitete Float16-Worktree erhält keine fachliche
Implementierung oder Runtimeadmission. Er dient nur dieser abschließenden
Stoppdokumentation und wird nach deren PR-Integration vollständig bereinigt.
Keine neuen SQL-, Container-, Modell-, Provider-, Compiler- oder Hosteffekte.
Keine neue Entwicklungswelle, keine automatische Wiederaufnahme. Offene
TSK-004–TSK-014-/Release- und Humanqualifikationen bleiben im Backlog offen;
dieser Benutzerabschluss erklärt sie nicht nachträglich als bestanden.

[Letzter fachlicher Nachweis und verbleibende Grenzen](SQL_SERVER_2025_AI_IDX012_V2_REQUALIFICATION_REVIEW.md).

## C1: historischer öffentlicher V2-Record kohärent mit WARN

Der erste neue Kandidat hat den unveränderten tatsächlich gesicherten C3-Record
mit dem veröffentlichten korrigierten Consumer vollständig ausgewertet:
SOURCE_COHERENT_OVERALL_WARN, COHERENT_PUBLIC_V2, attempted1/completed1.
Driver-PID68696 und Reportchild-PID32960 endeten bestätigt mit Poll/Returncode0,
ohne Timeout oder UNKNOWN. Alle56 festen Eingangsdateien und neun Authority-
dateien blieben vor/nach bytegleich. Root hat Originalkanäle, Quellen, vollständige
Prozessenden, Ergebnisform, Ledger und STOP unabhängig geprüft.

Feste Counts: drei Profile,25 Clientcaptures, acht Rollenkontexte, zwei Kostenpaare,
zwei Rechtegegenfälle sowie vier positive und vier abgewiesene DML-Fälle.
Die unveränderten Profile wurden vollständig geprüft; keine neuen SQLergebnisse
oder Runtimecapturen erzeugt. SQLcleanup bleibt lediglich TEXTS_COHERENT,
Herkunft und Credentiallisten-Vollständigkeit bleiben deklarativ. Bei secrets=[]
bleibt NOT_CHECKED_FOR_UNAVAILABLE_SECRETS; Generation UNKNOWN und die offenen
Ownerquery-/TDS-/vollständigen DML-Error-/Parentcleanup-/Runtime-/TP-PERF-Claims
werden nicht hochgestuft. Dies ist ein begrenzter Recordnachweis.

Neue Welle: ein Quellenstand und ein erfolgreicher kohärenter Report mit WARN,
keine zusätzlichen Unit-/Syntaxproben oder Domainaufrufe. Beim ersten kohärenten
Befund tatsächlich STOP; keine weiteren Kandidaten oder Budgetausschöpfung.
Zusammen mit der früheren Welle zwei historische Versuche: der erste FAIL
V2_RECORD_BINDING bleibt unverändert mit seinem verbrauchten Max1 und STOP.
Die vor dem neuen Report abgewiesene Rootmetadatenassertion mit falsch
übertragenem Preparedhash ist separat erhalten; nach direkter Aufnahme des
vollständigen Hashs korrigiert, kein Report vor dieser Korrektur und keine
Umzählung als Runtime-/Quellen-Syntaxfehler. Ihr PID (Process Identifier; Prozesskennung) bleibt NOT_CAPTURED.

Alle56 tatsächlich verwendeten Eingangsbytes sind flach gesichert, dazu23 feste
Authority-/Ergebnis-/Raw-/Ledger-/Rootreviewdateien; bytegenau erneut verglichen.
Originalmanifest und Admission bleiben unverändert. Nach dem tatsächlichen
Report werden ausschließlich HowTo und kanonischer Dokumentstand aktualisiert;
die Dokumentdeltas werden getrennt vom unveränderten Ausführungsbeleg gebunden.
Aktuelle lokale Dokumentprüfungen, PR-/Head-/Main-Gates, origin/main-Integration,
FullTree, Synchronisierung und eigener Cleanup folgen. Modell-/Tokenverbrauch UNKNOWN.

[Konkreter Nachweis und offene Grenzen](SQL_SERVER_2025_AI_IDX012_V2_REQUALIFICATION_REVIEW.md).

## TSK-006: getrennte historische V2-Requalifikation in Vorbereitung

PR247 vollständig geschlossen: zehn Head- und acht Main-Checks erfolgreich,
je ein Runtimejob nicht ausgewählt; Main67d83316722e396624ba77db2c51d66ff43b9b93,
FullTree/Sync/Branchcleanup bestanden,876 private Dateien bytegenau erhalten,
Worktree tatsächlich archiviert. Der ursprüngliche V2-Report bleibt FAIL
V2_RECORD_BINDING, attempted1/completed0; sein Max1 und STOP bleiben erhalten.

Der veröffentlichte Source5-Consumer korrigiert den tatsächlich gefundenen
vollständigen NOT_STARTED-Vertrag. Darauf folgt eine getrennte historische
Offlinewelle: maximal sechs relevante Quellen-/Adapterstände und sechs Reports,
ActualCheckpoint3/Hard6/UNKNOWN-/erster kohärenter Stop. Weitere Versuche nur
mit verändertem Input/Source oder neuer Evidenz, keine alten grünen Wiederholungen.
Ein Implementer, enger Rootreview; Null Domain-/Modell-/Hosteffekte. Alte Counts,
Claims, V1 und Originalprofile unverändert. Zunächst keine Reportadmission.

[Konkreter Scope und aktuelle Grenzen](SQL_SERVER_2025_AI_IDX012_V2_REQUALIFICATION_REVIEW.md).

## TSK-006: V2-Rechtegegenfälle korrigiert; historischer Report bleibt FAIL

Der einmalige historische Offlinebericht scheiterte mit V2_RECORD_BINDING:
attempted1, completed0, keine Summary. Driver-PID8276 und Child-PID72048
endeten bestätigt mit Poll/Returncode1, ohne Timeout oder UNKNOWN. Alle51
festen Eingangsdateien und acht Authoritydateien blieben vor/nach bytegleich.
Root hat den Fehler und die Originalkanäle unabhängig geprüft.

Der konkrete Fehler betrifft die beiden Rechtegegenfälle: Die tatsächliche
öffentliche API liefert für das noch nicht gestartete Cleanupfenster vier
Felder, während Consumer und Fixture nur Status erwarteten. Source5 fordert
jetzt exakt Status=NOT_STARTED, Seconds als int60 sowie beide Zeitfelder=None.
Fehlende, zusätzliche und widersprüchliche Felder werden abgewiesen. Der neue
betroffene Gegenfall bestand normal PID11964 und optimiert PID16700, jeweils
Poll/Returncode0; alle31 Quellen blieben unverändert. Enger Rootreview bestanden.

Fünf geprüfte Quellenstände,21 Methodeninvokationen/19 PASS/zwei erhaltene FAIL,
zusätzlich erster Driver-SyntaxFAIL; acht bestätigte Unitprozessenden. Keine
alte grüne Suite lokal wiederholt. Der ursprüngliche historische Report bleibt
FAIL; das maximale Einzelreportbudget ist verbraucht und wird nicht zurückgesetzt.
Null Native-, SQL-, Container-, Provider- oder Modellaufrufe in diesem Schnitt.
V1, alte Evidenz und Claims unverändert; Runtime-/Herkunfts-/Credentialgrenzen
bleiben offen. Modell-/Tokenverbrauch UNKNOWN.

Dieser Schnitt wird mit aktuellem Quellen-/Dokumentfreeze, PR-/Head-/Main-Gates,
Integration nach origin/main, Synchronisierung und eigenem Cleanup geschlossen.
Erst anschließend darf eine getrennte begründete Folgewelle einen weiteren
historischen Bericht zulassen; kein Wiederholungs-PASS in dieser Welle.

[Konkrete Belege und Grenzen](SQL_SERVER_2025_AI_IDX012_PUBLIC_RECORD_V2_REVIEW.md).

## TSK-006: V2-Source4 Fixturekorrektur gezielt bestanden

Source4 ändert nur den Helperfixture-Pfadvergleich; Produktguards Source3-gleich.
Betroffener Fall1N/1O bestanden, alle Helpernegativzweige erstmals erreicht.
VierStände/19Invokationen/17PASS2FAIL plus ersterDriverSyntaxFAIL, sechs bekannte
Testenden. PrivacyN/O-BelegeSource3 unverändert, keinealte7/6-Wiederholung.
HistorischerOfflineReport/Domain0; freshRootabnahme nochvorReport erforderlich.
[Konkrete aktuelle Belege und verbleibende Grenzen](SQL_SERVER_2025_AI_IDX012_PUBLIC_RECORD_V2_REVIEW.md).

## TSK-006: V2 tatsächlicher Checkpoint3 geschlossen

Source3-Privacycluster normal/optimiert bestanden; Helperfixture beide FAIL
am Extended-/Normalpfadvergleich, negativeHelperzweige NOT_REACHED.
RootactualCP3: dreiStände/17Invokationen/15PASS2FAIL plusSource1SyntaxFAIL,
vier bekannteTestenden. Source4 ausschließlich betroffeneFixtureBytevergleich-
Korrektur mit1N/1O; keinealtegrüneSuite/Privacywiederholung. Offline-/Domain0,
keinehistorischeReportadmission. [Konkreter Checkpoint und Grenzen](SQL_SERVER_2025_AI_IDX012_PUBLIC_RECORD_V2_REVIEW.md).

## TSK-006: V2-Source2 enger Rootreview verlangt Guardkorrektur

Source1 privater Driver-SyntaxFAIL vor Child bleibt; Source2 erstmals7N/6O
bestanden,13 Methoden/2 bekannte Testenden. Root reproduzierte zwei neue reine
Privacyfindings: gemischte bekannte Hexformen und verschachtelte PART-Frames
passieren vor Digests. Zusätzlich feste vier Pure-Modulnamen vor Import begrenzen.
Source3 gezielt, kein alter7/6-Replay; tatsächlicherCP3 erst nach Source3.
Offline-/Native-/SQL-/Host-/Modelleffekte0, Originale/aktuellerDocstand vorher
gesichert. [Aktueller Befund und unveränderte Grenzen](SQL_SERVER_2025_AI_IDX012_PUBLIC_RECORD_V2_REVIEW.md).

## TSK-006: öffentliche V2-Recordauswertung als nächster Offline-Schritt

PR246 ist vollständig geschlossen: Head13/Main11 erfolgreich, Main e3d8d61e,
voller Tree, synchrones sauberes Main, eigene Branches entfernt;439 private
Originale hashgesichert und Worktree tatsächlich archiviert. PublicRole-C3 bleibt
begrenzter Teilnachweis mit WARN/offenen Owner-/TDS-/Runtime-/TP-PERF-Grenzen.
Der separate V2-Consumer nimmt die neue Public-Resultform auf; V1-CapturesNone und
historische Inputpins bleiben unverändert. Ein Implementer, enger Rootreview,
max6 Source/ActualCP3/Hard6 und höchstens ein gebundener Offline-C3-Report nach Freeze.
Neue Runtime-/SQL-/Modelleffekte0, keine Wiederaufnahme alter Native-/V1-Wellen.
[Endlicher Scope, Prüf- und Claimgrenzen](SQL_SERVER_2025_AI_IDX012_PUBLIC_RECORD_V2_REVIEW.md).

## TSK-006: öffentlicher Rollenmodus tatsächlich begrenzt bestanden

C3/insgesamt Rollenkandidat6 bestand den abgegrenzten öffentlichen APIvertrag
auf 17.0.5005.3/Engine3/Linux. 39 bestätigte SQLprozessenden, davon drei erwartete
Startupverbindungs-FAILs vor Bootstrap; 25 bekannte Namespaceprozesse, ein eigener
Container angelegt und entfernt. Zwei tatsächliche Rechteentzüge führten exakt
zu PREFLIGHT/SKIP_PERMISSION, frische DBabwesenheit und vollständiger Grantrestore.
Positiver Produktstatus bleibt WARN_OPTIONAL_EVIDENCE_SKIPPED: 23 Phasen,
acht Rollenkontexte, zwei Kostenclients, drei Storageaufnahmen und vollständiger
999-Row-Text-/Distanz-/Rebuildvergleich. Preview/MAXDOP (Maximum Degree of Parallelism; konfigurierte Grenze für den Parallelitätsgrad) zurückgesetzt, DB/Login/
CID/Name/Inputs frisch abwesend; Closedtrue/Unknownfalse. RootactualReview bestanden.
Sechs Quellenstände/28 Invokationen/26 PASS/zwei erhaltene ERROR und elf bekannte
Testenden. C1/C2-FAILs bleiben unverändert; Welle nach finalem Teilnachweis gestoppt.
Generation UNKNOWN, separater Ownerreceipt und Server-/TDS-Enden unqualifiziert;
Runtime/TP-PERF/Release offen, historische Dokumentprovenienz-WARN erhalten.
[Originalbefund, aktuelle Grenzen und Abschlussvertrag](SQL_SERVER_2025_AI_IDX012_ROLE_NATIVE_REVIEW.md).

## TSK-006: C2 geschlossen FAIL, Source6 letzter Quellenstand

C2/insgesamt Rollenkandidat5 endete vor Create bekannt FAIL und geschlossen:
drei sichere Namespaceclients bestätigt, null Container/SQL/Profile/Inputs;
eigener Name frisch abwesend, keine SQL-/Principalabwesenheitsattestation.
Die tatsächliche volle Image-ID ohne sha256-Präfix stimmt exakt mit der
freigegebenen ID überein; Source6 erlaubt ausschließlich beide vollständigen
Darstellungen derselben ID. Neuer Gegenfall normal/optimiert bestanden.
Sechs Quellenstände, 28 Invokationen, 26 PASS/zwei erhaltene ERROR, elf bekannte
Testenden. Originale und aktuelle Canonicalbytes vorher gesichert; historische
Dokumentprovenienz-WARN bleibt. C3/insgesamt6 ist nach frischer Rootadmission
der letzte Nativekandidat; kein Source7/Native4. [Nachweis und Grenzen](SQL_SERVER_2025_AI_IDX012_ROLE_NATIVE_REVIEW.md).

## TSK-006: öffentlicher Rollenlauf C1-FAIL, gezielte Source5-Korrektur

NativeC1/insgesamt Rollenkandidat4 ist bekannt FAIL vor Domainaufrufen,
null neue Container/SQLkontexte. OriginalClosedfalse und UrsacheUNPROVEN bleiben.
Eine separate spätere schreibgeschützte Prüfung bestätigt den aktuell abwesenden
eigenen Namen und schließt ausschließlich den aktuellen kontextlosen Stand;
kein ursprünglicher Cleanupfenster-/SQL-Abwesenheits-PASS und kein Zählerreset.
Source5 trennt feste Command-/SQLinputs von strikten empfangenen JSON-/Wirekanälen;
neuer Gegenfall normal/optimiert bestanden. Fünf Quellenstände, 26 Invokationen,
24 PASS/zwei erhaltene ERROR. Neue Rootadmission nach aktuellem Freeze steht aus.
Historische Dokumentprovenienz-WARN bleibt sichtbar; Originale und aktuelle
Dokumente vor Änderung gesichert. [Konkreter Nachweis](SQL_SERVER_2025_AI_IDX012_ROLE_NATIVE_REVIEW.md).

## TSK-006: öffentliche Rollenprobe nach abgeschlossenem Budget-Schnitt

Der private Caller hat vier gezielt geprüfte Quellenstände: 24 Methoden-
invokationen in sieben bekannten Testprozessen, 22 PASS und zwei erhaltene
Source1-ERROR. Der tatsächliche unabhängige Checkpoint3 verlangte eine
Namespace-Countreserve für Cleanup. Source4 reserviert sechs der insgesamt
32 Aufrufe; Normalaufrufe enden bei26 ohne Zählerreset. Die neue Gegenprobe
bestand normal und optimiert. Öffentliche API unverändert, Domainaufrufe0;
aktueller Doc-/Host-/Quellenabschluss und ausdrückliche Root-Nativeadmission
stehen vor jeder Runtimewirkung noch aus.

PR245 ist vollständig geschlossen: 13 Head- und sieben Main-Checks bestanden,
Main1fbd339f, voller Tree, synchrones sauberes Main und eigene Branches entfernt.
585 private Belegdateien sind bytegenau gesichert, der Worktree tatsächlich
archiviert. Vier Quellenstände mit 18 Methodeninvokationen in sieben Prozessen;
17 PASS und ein archivierter ursprünglicher Fixture-FAIL bleiben sichtbar.

Der [öffentliche Rollennachweis](SQL_SERVER_2025_AI_IDX012_ROLE_NATIVE_REVIEW.md) wird im neuen eigenen Worktree zunächst
als private Callergrundlage umgesetzt. Aktuelle öffentliche API einschließlich
SharedCleanupWindow unverändert; neue Quellen-/Input-/History-/Hostbindung und
unabhängiges Rootreview vor Nativeadmission. CallerSource6/Checkpoint3/Hard6,
historische drei Rollenkandidaten/vier Container plus höchstens drei neue
geänderte Kandidaten mit je einem eigenen Container. Noch keine neuen Caller-
oder Domainaufrufe; volle Runtime-/TP-PERF-Abnahme und Tokenverbrauch bleiben offen.


## TSK-006: gemeinsames öffentliches Cleanupbudget vor Runtime

Vier Quellenstände sind gezielt geprüft: 18 Methodeninvokationen in sieben
gehaltenen Prozessen, 17 PASS und ein archivierter Source1-Fixture-FAIL.
Der tatsächliche unabhängige Checkpoint3 verlangte Korrekturen für erneute
Windowinitialisierung und veränderbare Fristenkonstanten. Source4 schließt beide
mit einem neuen Gegenfall normal und optimiert; frühere grüne Suiten wurden
lokal nicht wiederholt. Domainaufrufe0. Aktuelle PR-/Head-/Main-Integration,
Synchronisierung und eigene Archivierung folgen vor neuer Calleradmission.

Der öffentliche Rollennachweis ist vor Callerumsetzung zurückgestellt: seine
20s-Recovery meldet keinen Cleanupstart, konfigurierte Windows-Nachläufe passen
nicht in eine ehrlich gekoppelte äußere60s-Uhr. Boundaryproof erhalten,
Caller/Pure/Native/Domain0, historische3Rollenkandidaten/4Container unverändert.

Aktueller unabhängiger Schnitt: [typisierte Budgetübergabe](SQL_SERVER_2025_AI_IDX012_CLEANUP_BUDGET_REVIEW.md).
Einmaliger tatsächlicher Cleanupstart, gemeinsame absolute Deadline und fester
Collector mit Kill-/Reapreserve; keine freien Callbacks oder globalen Collector-/
Hoständerungen. SOURCE_ONLY, neue6Quellenstände/Checkpoint3/Hard6; vorherige
RoleSourceHard6 unverändert gestoppt. Enger Rootreview und betroffene Gegenfälle
vor PR/Head/Main/Tree/FF/eigenem Cleanup. Danach aktuellen Caller fortsetzen,
vor Native neue Admission; Runtime-/TP-PERF-Abnahme und Tokens UNKNOWN.

## TSK-006: öffentliche Rollen-API, tatsächlicher Nachweis in Vorbereitung

PR244 geschlossen: aktueller Head13/Main7, Main3a558cf0, voller Tree/FF/
sauberes Main, eigene Branches entfernt, 327 private Dateien gesichert und
Worktree tatsächlich archiviert. SourceHard6 bleibt gestoppt; alte Syntax-,
CI-FAIL- und UNKNOWN-Records unverändert. Der historische Squash-Commit
verfehlte das Codex-Präfix; Abweichung erhalten, keine Historienumschreibung.

Aktueller Schnitt: [begrenzter öffentlicher Rollennachweis](SQL_SERVER_2025_AI_IDX012_ROLE_NATIVE_REVIEW.md).
Zunächst private Caller-/Capturevorbereitung ohne Domainaufrufe; unveränderte
öffentliche API, vollständige Credentials-/SID-/Principal-/Session-/Marker-/
Restore-/Cleanupbindung. Historische drei Rollenkandidaten/vier Container plus
höchstens drei neue Kandidaten/je einen eigenen Container = maximal6/7.
Stop nach erstem kohärenten öffentlichen API-Teilnachweis oder sofort UNKNOWN.
Sechs getrennte Callerquellenstände/Checkpoint3/Hard6; aktuelle Rootadmission
vor Native bleibt erforderlich, volle Runtime-/TP-PERF-Abnahme offen.

## TSK-006: öffentlicher IDX-012-Rollenmodus in Vorbereitung

PR243 vollständig geschlossen: 14 Head-/acht Main-Gates, Maine63cd1fc,
voller Tree, FF/sauberes Main, eigene Branches entfernt, 81 private Dateien
gesichert und Worktree tatsächlich archiviert. Poolsource Hard6 bleibt
gestoppt; alte UNKNOWNs und Ursachen UNPROVEN werden nicht geändert.

Nächster unabhängiger Schnitt: [öffentlicher Rollenmodus](SQL_SERVER_2025_AI_IDX012_ROLE_API_REVIEW.md).
Der vorhandene historische IDX-012-Rollensplit wird als ausdrücklich gewählte
öffentliche API vorbereitet: feste Credentials-/SID-/Kontextbindung, je
Kostenphase dieselbe Session, Admin nur am Build, danach gleicher Operator.
SOURCE_ONLY, sechs Quellenkandidaten/Checkpoint3/Hard6, keine Runtimezulassung
oder Rechtevergabe. Betroffene Gegenfälle und enger Rootreview vor Integration;
volle TSK-006-/Runtime-/TP-PERF-Abnahme offen, Tokenverbrauch UNKNOWN.

Aktueller Quellenstand: Labels Source1–4, insgesamt fünf tatsächlich geprüfte
Zustände einschließlich initialem Syntaxpreflight-FAIL mit abweichenden Bytes.
Die Zählung wurde korrigiert; Rootcheckpoint3 wurde tatsächlich nach vier
Zuständen und vor dem fünften geschlossen, ohne rückwirkenden Rechtzeitigkeitsclaim.
Vorherige 18 reine Methodeninvokationen/ sechs gehaltene Pythonprozesse bleiben
unverändert. Source4 schließt den konkreten Cleanup-UNKNOWN-Rückgabeverlust mit
nur einem neuen vollständigen Controllergegenfall normal und unter `-O`:
beide bestanden, insgesamt 20 Invokationen/acht gehaltene Prozesse. UNKNOWN im
Restore liefert FAIL_CLEANUP und NOT_ESTABLISHED mit vollständigen sicheren
Captures/zurückgehaltenen Inputs zurück; kein weiterer Recovery-SQLclient.
Vor der CI-Imagekorrektur waren fünf von sechs Quellenständen verbraucht; einer verblieb. Root hat Source4/overall5 semantisch und mechanisch abgeschlossen;
CLEANUP_UNKNOWN_RESULT_LOST ist geschlossen. Der Quellenstand wird über PR
integriert; Native-/Server-/TDS-Abnahme bleibt offen, Domainaufrufe bleiben null.

Der erste PR244-Headlauf blieb tatsächlich FAIL: Der SQL2025-Kostenconsumer
verwarf SKIP_CONFIGURATION; die vier vorangehenden DGN-010-Lifecycles hatten
bereits SKIP_CONFIGURATION mit bestätigtem Cleanup geliefert. Der ursprüngliche
CI-Namespacecleanup bestand. Die Logdigests belegen, dass `2025-latest` gegenüber
dem erfolgreichen Mainlauf38415812533 ein anderes Image auflöste: vorher
`sha256:2b5b581621126574f3d1f75e78d3eebe8d05aedb59ad0cfdf9aa42cb0634d726`,
im fehlgeschlagenen Headlauf38427774683 dagegen
`sha256:742481d1b1186cccc81220a1eaacef244ca8d0f7d19c8e5c70df8ae541ffbab2`.
Image-Drift ist belegt; die tatsächliche neue Build-/Editionabweichung ist
UNPROVEN, weil der SKIP keine abweichenden Werte ausgibt.

Der sechste und letzte Quellenstand CI_IMAGE_INPUT_CORRECTION pinnt nur den
SQL2025-Matrixeintrag auf den tatsächlich erfolgreichen RegistryDigest.
2019/2022, Laufskripte, Testoracles und Rollenproduktbytes bleiben unverändert;
keine SKIP- oder FAIL-Umdeutung und kein unveränderter CI-Rerun. Source4-Freeze,
Rootreview, 20 Methodeninvokationen/acht gehaltene Testprozesse sowie die beiden
Original-CI-Logs bleiben erhalten. Keine lokale Purewiederholung oder neue
Domainaufrufe. Jetzt sechs von sechs Quellenständen/Hard6, kein Reset oder
Source7. Die neue geänderte CI-Eingabe erhält aktuelle Head-/Main-Gates vor
Integration; PR244 bleibt bis dahin ungemergt. Öffentliche Rollenruntime und
vollständige Demo-/Server-/TDS-/TP-PERF-Abnahme bleiben NOT_ESTABLISHED.

## TSK-009: reiner Poolchild-Capture nach vollständigem PR242-Abschluss

PR242 geschlossen: 14 Head-/acht Main-Gates, Mainee3777fd, Tree/FF/Branches,
338 private Dateien gesichert und Worktree tatsächlich archiviert. Aktueller
Schnitt: [Poolchild-Capturevertrag](SQL_SERVER_2025_AI_POOL_CHILD_CAPTURE_REVIEW.md). Source5/6, geschlossenerSourceCP3,
hard6 ohne Reset. Sichere tatsächliche Child-Prozess-/Kanalbelege vor fehlerhafter
Klassifikation erhalten, Privacy vor Raw/Digests; unbeobachtete Werte nicht
erfinden und alte UNKNOWN-Ursache nicht rekonstruieren. Nur neue Puregegenfälle
normal/-O, keine lokale Native-/Provider-/SQL-/Container-/Modellprobe.
Gestoppte Welle bleibt bei insgesamt vier Nativeversuchen/drei Containern;
SQLcleanup/Inputs/Poolchildqualifikation offen, vorhandene Originale read-only.
Aktuelle PR-/Head-/Main-/Tree-/FF-/Branch-/Beleg-/Archivgates vollständig schließen.
Tokenverbrauch UNKNOWN.

Source5 ist rein mit vier neuen Methoden normal und vier unter `-O` bestanden.
Source6 beseitigt einen verbliebenen Source-read vor der Transportzuweisung:
der tatsächlich vor Start gehaltene öffentliche Collector-Returntyp wird verwendet.
Nur die betroffene Methode wurde normal und unter `-O` erneut geprüft; beide
Läufe bestanden. Tatsächliche Prozessenden und unveränderte Rawkanäle sind privat
gebunden. Source5-Bytes und sämtliche früheren Prüfbelege bleiben archiviert;
keine alte grüne Suite oder Runtime wurde wiederholt.

Der separate Childtransport hält bekannte Prozessfakten vor Ergebniszuordnung,
auch bei malformed Receipt, fehlgeschlagener Sourcebeobachtung oder UNKNOWN.
Unsichere Kanäle erhalten keine Rawdaten oder Digests. Unbeobachtete Werte bleiben
null; bekannte Prozessenden ersetzen weder die 57 API-Records noch Server-/TDS-
Endbelege. Der unabhängige Rootreview hat den konkreten Capture-/Privacy-/
Endtrennungsdelta ohne offenes semantisches Finding gelesen. Mechanische
Freezeprüfung und aktuelle Integrationsgates stehen noch aus.

Hard6 ist erreicht, Sourceentwicklung gestoppt; keine neue Native-, Provider-,
CLR-, Compiler-, SQL-, Container-, Modell- oder Metadatenausführung. Bestehender
Sourcecheckpoint3 bleibt geschlossen, alte UNKNOWNs und Ursache UNPROVEN bleiben
unverändert. Kumulativ weiterhin vier Nativeversuche/drei Container, keine neue
Zulassung der gestoppten Welle. Runtime-/Pooling-/TSK-009-/TP-CON-Abnahme bleibt
NOT_ESTABLISHED. CI erweitert nur den bestehenden statischen Schritt um vier
Schutzmethoden: 39 normal/18 optimiert in denselben zwei Pythonprozessen;
Runtimejob und Selector sind bytegleich, Default-CI startet kein RED-Profil.


## TSK-009: begrenzter Owner-Teilnachweis, Poolwelle bei UNKNOWN gestoppt

Aktueller Schnitt: [Poolqualifikationswelle](SQL_SERVER_2025_AI_POOL_REQUALIFICATION_REVIEW.md).
Vier Sourcezustände sind ehrlich gezählt: initial neun betroffene Methoden,
Checkpoint-Dateibindung zwei, tatsächlicher Checkpointvertrag zwei und getrennte
Setupkanäle zwei, jeweils normal/-O mit gehaltenen Enden und sicheren Raws.
Sourcecheckpoint3 geschlossen und für Source4 ausdrücklich neu gebunden;
keine alte grüne Vollsuite wiederholt. Standard-UNKNOWN-Sperre unverändert.

Native1/insgesamt3 bleibt bekannt FAIL_SETUP_SUMMARY + FAIL_SQL_CLEANUP,
UNKNOWNfalse: vier SQLcmd- und dreizehn gehaltene Namespaceenden. Frische
CID-/Namens-/Inputabwesenheit belegt Resourceclosure; SQLcleanup NOT_ESTABLISHED.
Der unabhängige verpflichtende Nativegesamtcheckpoint3 ist geschlossen.
Source4 korrigierte den konkret erfassten getrennten Setupkanal.

Native2/insgesamt4 endet UNKNOWN_STOP. 39 bekannte SQLcmd-Enden, 48 gehaltene
Namespaceenden, Setup/Logins/Baseline sowie sechs tatsächliche Owner-SQLabweisungen,
fünf vollständige Negativzustandswitnesses und sieben geordnete Controls sind
belegt. Einzelne Poolchild-/.NET-Enden, A/B/U-Checkouts, physische Poolreuse und
Ursache bleiben NOT_ESTABLISHED beziehungsweise UNPROVEN. Nach UNKNOWN kein
Folge-SQL; genau ein vollständig gebundener eigener Remove und frische leere
CID-/Namensabfragen. SQLcleanup NOT_ESTABLISHED; ein ursprünglicher Childplan
bleibt erhalten, inputsAbsentfalse und ledgerClosedfalse. Kein zweiter Remove.

Kumulativ vier Nativeversuche/drei Container einschließlich der unveränderten
PR226-Welle. Aktuelle Welle STOP; keine Native3-Zulassung trotz verbleibender
rechnerischer Slots. Kein Runtime-/TSK-009-/TP-CON-PASS. Quellen, Hostbytes,
Authorities und ursprüngliche Ausführungssnapshots bleiben erhalten;
Dokumentstatusänderungen sind getrennte DocOnly-Deltas, keine rückwirkend neuen
Ausführungspins. Head-/Main-Gates, Integration und eigener Branch-/Worktreeabschluss
folgen durch Root. Modell-/Tokenverbrauch UNKNOWN.

Nach vollständiger Integration folgt ausschließlich ein unabhängiger SOURCE_ONLY-
Capturevertrag: vollständige sichere Poolchild-Kanäle und individuelle Endrecords
vor Malformed-/UNKNOWN-Klassifikation erhalten. Keine Wiederaufnahme dieser oder
älterer UNKNOWN-Wellen, kein Native-/Ressourcenreplay und kein Ursachennachweis
allein aus neuer Source.

## TSK-009: neue eigene öffentliche Poolqualifikation nach PR241

PR241 vollständig geschlossen: sieben Head-/fünf Main-Gates, Mainaf7d3d3a,
Tree/FF/Branches, 1467 private Dateien gesichert und Worktree tatsächlich archiviert.
Aktueller Schnitt: [neue Poolqualifikationsgrundlage](SQL_SERVER_2025_AI_POOL_REQUALIFICATION_REVIEW.md).
Alte PR226-Welle bleibt STOPPED_NATIVE_UNKNOWN, zwei Nativeversuche/einContainer/
SQL0/Poolchild0; aktuelle korrigierte Sources werden an neue eigene Wave-/Input-/
Control-/Historybindungen gebunden. Kein Replay, alte UNKNOWN niemals löschen.
Zunächst SOURCE_ONLY ohne Effekte. Neue Nativeadmission nur nach aktuellem Review;
alte zwei Versuche plus höchstens vier neue Gesamtmax6, alte einContainer plus
höchstens vier neue Gesamtmax5, seriell. Erster neuer Nativeversuch verlangt
Gesamtcheckpoint3. Eigene Marker-/SID-/Credential-/Requestende-/RLS-/Cleanupfloors
und unveränderte Host-/Cloud-/ONNX-/Releasegrenzen; Tokenverbrauch UNKNOWN.


## TSK-007/008: getrennte lokale Routeignung und Gesamtcheckpoint3

Aktueller Schnitt: [beobachtbare Routeignung](SQL_SERVER_2025_AI_ROUTE_ELIGIBILITY_REVIEW.md).
PR240 vollständig geschlossen: sieben Head- und fünf Main-Gates, Main dee36a7b,
vollständiger Tree, FF-Synchronisierung und eigene Branches bereinigt;
1.534 Dateien gesichert und eigener Worktree archiviert. C2 bleibt kohärent
UNAVAILABLE, ohne Unterscheidung zwischen fehlendem Tag und Mindestversion.
Die neue Beobachtungsgrundlage trennt tatsächliche Version, Mindestversions-
entscheidung, Tag-Präsenz und Ursachen; alte Records werden nicht ergänzt.
C3 tatsächlich COHERENT_DIAGNOSTIC_ONLY/UNAVAILABLE: Runtimeversion0.40.2
ist mindestens0.11.10, version_supported=true. Exakte gemma3:1b-Tagmatches0,
tag_present=false; tag_missing=true und version_below_minimum=false.
Zwei neue bekannte HTTP200-Responses (version/tags), kumulativ vier Metadata;
Show/WhatIf/Inferenz0. Top-/Childenden bekannt, kein Timeout/UNKNOWN,
elf Quellenbindungen, vollständiger eigener Snapshot und129 historische
Dateien unverändert; kein Inventar gespeichert. Alte C2-Ursache bleibt
NOT_DISTINGUISHED, kein rückwirkender Versions- oder Tagbefund.
Pflichtcheckpoint3 anhand C1/C2/C3 unabhängig geschlossen: PASS_DIAGNOSIS_ONLY.
Gesamte Diagnosewelle STOP; keine vierte Probe oder weitere Metadaten/Inferenz
auch bei rechnerisch verbleibendem Budget. Fünf neue Puremethoden normal/-O
bestanden; keine alten grünen Suiten wiederholt. Keine Modelle, Downloads oder
Hoständerungen; Lizenzinferenz NOT_ADMITTED/Gewichte und volle Gates offen.

Nach vollständiger Integration dieses Nachweises folgt eine unabhängige
TSK-009-Poolgrundlage zunächst SOURCE_ONLY auf aktuellen korrigierten
öffentlichen Quellen. Bekannte Namespacekorrekturen nicht erneut analysieren;
Delta zum tatsächlich gestoppten PR226-Stand und neue eigene Input-/Scope-/
Rootbindungen prüfen. Alte zwei Nativeversuche/ein Container/SQL0/Poolchild0
transparent weiterzählen; alle alten UNKNOWNs und Stops erhalten. Kein C3 der
alten Welle, kein Ressourcenreplay oder Recovery. Neue Nativeeffekte erst nach
separatem aktuellen Quellen-/Sicherheitsreview und konkreter Rootadmission.

## TSK-007/008: anderer vorhandener lokaler Completionpfad nach PR239

Aktueller Schnitt: [lokaler Completionbestand](SQL_SERVER_2025_AI_COMPLETION_ROUTE_REVIEW.md).
PR239 vollständig geschlossen: neun Head-/sieben Main-Gates, Main63640639,
voller Tree/FF/Branches, 36 private Dateien gesichert/eigener Worktree archiviert.
Öffentliche VECTOR-Lesehilfen fertig; alte Qwen-Hard6-Welle bleibt gestoppt.
Aktueller öffentlicher Lab-Katalog bietet zusätzlich die lokale generation-Route
ollama-gemma3-1b-local; bisher nur Quellenbefund, keine Live-/Antwortqualifikation.
Neue gebundene read-only Bestandsprüfung, zuerst Sourcevorbereitung mit null
neuen Effekten. Nach eigener Rootadmission maximal drei Loopback-Metadata-
Requests/ein lokaler WhatIf-Plan, keine Inferenz/Downloads/Hoständerungen.
Source6/Checkpoint3/hard6, UNKNOWNStop, Lizenz-/Capability-/Livegrenzen offen.

C1-Sourcefreeze erreicht das Ausführungsgate nicht: unabhängige Root-
Byteprüfung meldet tatsächlichen Source-Drift vor Admission. Der fremde
Lab-Arbeitsstand wurde parallel weiterentwickelt; drei loadergebundene
SMTP-Quellen unterscheiden sich, aktueller fremder Arbeitsstand ist sauber.
Keine Rootadmission, keine Metadaten-/WhatIf-/Inferenzaufrufe. C1-Sourcekarte,
Raws und ursprüngliche Bindungen bleiben unverändert; ursprüngliche individuelle
PID der Root-Validierung nicht erfasst, keine Rekonstruktion.

C2 verändert ausschließlich die Abhängigkeitsbindung: eine eigene unveränderte
Kopie des ausgewählten committed Lab-Trees statt Import aus einem fremden
veränderlichen Arbeitsbaum. Read-only Git-Export in eigenes ignoriertes Runtime,
maximal30MB/2000Files, keine Fremdrepo-/Gitconfigänderung. Vor Extraktion sichere
Pfade, keine Links/Casekollisionen/zusätzlichen Dateien; vollständige Git-Blob-/
SHA-/Byte-/Datei-/Directorypopulation binden und vor jedem Domainaufruf erneut
prüfen. Öffentliche CommandInfo-/Modul-/Scriptpfade aus genau dieser eigenen
Kopie, keine Bearbeitung exportierter Bibliotheksbytes. Die ausgewählte
Commit-/Treeidentität wird bei Export belegt; eine spätere fremde HEAD-Bewegung
ändert die eingefrorene Kopie nicht. Kein nachträglicher alter Qwen-Replay.
Aktuelle relevante API-/Catalog-/Schema-/Loaderdeltas prüfen, belegte identische
Quellenanalyse wiederverwenden. Nur neue Snapshot-/Sourcebinding-Gegenfälle,
alte grüne Suiten nicht wiederholen. Source2/6, Checkpoint3/hard6; Domainbudget
höchstens drei Metadata/ein lokaler WhatIf, Inferenz0 unverändert. Neue Root-
Admission nach aktuellem Freeze/Privacy/engem Risikoreview, keine Effekte vorher.

C2 tatsächlich COHERENT_DIAGNOSTIC_ONLY/UNAVAILABLE; Stop ohne Retry.
Top48172/poll0/rc0/3,066943s und PS-Child67040/poll0/rc0/2,603143s,
kein Timeout/Collectorfehler/UNKNOWN. Zwei tatsächliche Metadatenrequests
version/tags, beide HTTP200/RESPONSE_RECEIVED; Show0/WhatIf0/Inferenz0.
SelectedIdentity und Plan null, keine vollständige Inventarpersistenz.
Die UNAVAILABLE-Verzweigung fasst fehlenden Tag und unterschrittene Mindest-
version zusammen; der Receipt unterscheidet diese Ursachen nicht. Weder
„Gemma fehlt“ noch konkrete Liveversion wird nachträglich rekonstruiert.
Lizenzinferenz NOT_ADMITTED/Gewichtsattestation offen/Tokenverbrauch UNKNOWN.
Zehn Callerquellen und gesamter eigener Snapshot1404Files/19.529.256Bytes
vor/nach identisch; C1-Drift/Originale erhalten. RootactualReview von Raws,
individuellen Antwort-/Prozessenden und aktuellen Bindungen bestanden.
Aktuelle vollständige Integration/Head-/Main-/Tree-/FF-/Branches/Belegsicherung/
Worktreearchiv folgt. Danach ausschließlich neuer beobachtbarer Versions-/
Tag-/Ursachenvertrag für gezielte Diagnose. Beide tatsächlichen alten Metadata-
Calls zählen weiter; konkrete geänderte Folgegrundlage mit maximal drei weiteren
Metadata, Gesamtmax5 statt ursprünglichemMax3 explizit vor Admission, kein
stiller Reset. Sourcekandidat3 erreicht verpflichtenden Rootcheckpoint3.
Keine alte Paketausführung oder Inferenz aus unbekannter Ursache; Download,
Lizenzinferenz und Host-/Cloud-/ONNX-/Antwortgates bleiben unverändert offen.

## TSK-004/TSK-012: öffentliche VECTOR-Clientlesehilfe nach PR238

Aktueller Schnitt: [VECTOR-Clientlesehilfe](SQL_SERVER_2025_AI_VECTOR_CLIENT_GUIDE_REVIEW.md).
PR238 vollständig geschlossen: sieben Head-/fünf Main-Gates, Maind0528ad4,
voller Tree/FF/Branches, 129 private Dateien gesichert/eigener Worktree archiviert.
Begrenzter Gesamt4-Roundtrip-PASS gestoppt, keine weiteren Proben; alte UNKNOWN
und Wire-/volle Abnahmegrenzen erhalten. Öffentliche Lesehilfe beginnt mit
Begriffen und Datenfluss, erklärt synthetische VECTOR-Zahlen, native API
gegenüber JSON, Voraussetzungen, NULL/Dimension und TLS-/Versionsgrenzen.
Bestehende Kompatibilitäts-/Sessionreadertexte an tatsächlichen neuen Beleg
anpassen, keine alte UNKNOWN-Auflösung oder pauschale Qualification.
Ein Implementer/enger Rootreview, höchstens sechs Textkandidaten/Checkpoint3,
Stop nach kohärentem Sourceabschluss; keine neuen Runtime-/Modell-/Hosteffekte.

SOURCE_ONLY abgeschlossen nach zwei Textkandidaten. Neue anwendergerechte
VECTOR-Clientlesehilfe mit Begriffen/Datenfluss und nummeriertem Offline-
Einstieg vor drei ausdrücklich gekennzeichneten APIfragmenten; drei Lese-
Entscheidungsfälle. Bestehende Kompatibilitäts-/Sessionreadertexte unterscheiden
jetzt den tatsächlich belegten API-/SQL-Roundtrip vom fehlenden unabhängigen
Wire-/TLS-/vollen TSK-004-Beleg. Ausdrückliche DB-ID-int-Projektion und heutiger
int/Int32-Befund ohne Umdeutung früherer Fehlerursachen oder UNKNOWN-Akten.
SRC-121 bindet Herstellerquellstand6.1.4/API6.1 für Mandatory/True.
49 gezielte Links/30 lokale Targets, Originale129 readonly einmal byteverifiziert;
enger unabhängiger Root-Aussage-/Code-/Versions-/TLS-/Belegreview und Privacy
aller acht öffentlichen Dateien bestanden. C1-Originale und einziges kleine
C2-Sprachdelta erhalten. Keine Textspiegeltests/alten Suiten oder neue Compiler-/
CLR-/SQL-/Container-/Provider-/Modell-/Download-/Hosteffekte. Source-STOP,
aktuelle vollständige PR-/Head-/Main-/Tree-/FF-/Branch-/Sicherungs-/Worktree-
Integration folgt. Danach schmale read-only Bestandsprüfung für einen anderen
bereits vorhandenen öffentlichen lokalen Completionpfad; alte Qwen-Hard6-
Generationswelle bleibt gestoppt. Keine Inferenz aus Katalog-/Metadatenbefund,
keine Downloads oder Cloudfallbacks; neue Admission vor späterer Inferenz.

## TSK-004: präzise OPEN-Serialisierung nach Gesamtcheckpoint3

Aktueller TSK-004-Schnitt: [präzise OPEN-Serialisierung](SQL_SERVER_2025_AI_OPEN_SERIALIZATION_REVIEW.md).
PR237 vollständig geschlossen: sieben Head-/fünf Main-Gates, Main7b9e1908,
voller Tree/FF/Branches, 128 private Dateien gesichert/eigener Worktree archiviert.
Gesamt3 bleibt UNKNOWN_STOP; Pflichtcheckpoint3 anhand tatsächlicher Originale
unabhängig geschlossen. Neue eigene V4-Grundlage korrigiert nur den erwarteten
OPEN-Encrypt-Serialisierungswert der gepinnten SqlClient6.1.4-Bytes auf True.
Herstellerquelle/6.1-Dokumentation stützen die Zuordnung; falsche/fehlende/
doppelte/zusätzliche Werte weiterhin ablehnen, TLS (Transport Layer Security; Verschlüsselungsprotokoll für Verbindungen) unverändert. Drei vorherige
Compiler/Container/Caller zählen weiter, höchstens drei zusätzliche Gesamt4–6.
Source6/Checkpoint3/hard6, zunächst null neue Effekte, getrennte Rootgates
vor Compiler/Native. Alte gestoppte Pakete/Ressourcen nie replay, UNKNOWN
bleibt sticky; volle Wire-/Runtime-/TSK-004-Abnahme offen.

Gesamt4 tatsächlich BOUNDED_ROUNDTRIP_PASS; STOP_AFTER_ROUNDTRIP_PASS,
keine fünfte oder sechste Probe. Compiler57768/poll0/rc0/0,648789s,
91.136-Byte-Artefakt und zwei erhaltene CS1701-WARNs. Top36268/poll0/rc0/
33,569191s und Child63688/poll0/rc0, kein Timeout oder UNKNOWN.
Acht tatsächliche SQL-/CLRtypfelder, 31 vollständig beendete Readerteilschritte
und zehn API-Enden; zwei Native-/JSON-FLOAT32-Vektoren vor/nach unverändert,
NULL(3) und spezifischer SQL-Dimensionsfehler42204/16/1/Line1/ProcedureNULL
mit vollständiger Nachricht. 52 bekannte SQLcmdenden/24 Vollstates,
Source-delete51003/Restore und vier vollständige bytegenaue Markercontrols:
je tatsächliche DML- und Cleanup-Abweisung51004, unveränderte Vollstates
nach Abweisung und vollständiger Restore. Echte markergebundene DB-Löschung,
frische DB-/ganze CID-/Name-/Inputabwesenheit; SQLcleanup
ACTUAL_DROP_AND_FRESH_ABSENCE, UNKNOWNfalse/Ledgerclosedtrue.
Alle 71 Quellen vor/nach identisch und unabhängiger Root-Originalreview bestanden.
Nachgelagerte reine Recordlese scheiterte an 1-MB-Grenze; dieser Befund bleibt
erhalten. Ausschließlich geänderte begrenzte 10-MB-Lese, kein neuer Nativeaufruf,
unverändertes 6.461.458-Byte-Original. Kumulativ vier Compiler/Container/Caller;
zwei ungenutzte Kandidaten werden nach dem ersten kohärenten PASS nicht verbraucht.
Alte UNKNOWN/fehlende SQLcleanups und geschlossener Pflichtcheckpoint3 bleiben.
Wire-/ausgehandelte TLS-/allgemeine Runtime-/float16-/TSK-004-Abnahme offen.
Aktuelle vollständige PR-/Head-/Main-/Tree-/FF-/Branch-/Sicherungs-/Worktree-
Integration folgt. Danach unabhängige öffentliche Lesehilfe für den tatsächlich
belegten Clientweg und seine Versions-/TLS-/Abnahmegrenzen, ohne neue Runtime.

## TSK-004: explizite DB-ID-Projektion und Gesamtcheckpoint3 nach PR236

PR236 vollständig geschlossen: acht Head-/sechs Main-Gates, Main11ec85c1,
voller Tree/FF/Branches, 125 private Dateien gesichert/eigener Worktree archiviert.
R1/Gesamt2 bleibt FAIL/UNKNOWN_STOP/SQLcleanup nicht belegt, alte Originale
und Ressourcen unverändert/kein weiterer Aufruf ihrer gestoppten Pakete.
Unmittelbar [neue eigene DB-ID-Projektion](SQL_SERVER_2025_AI_DBID_PROJECTION_REVIEW.md):
CONVERT(int,DB_ID()), eigene geänderte Input-/Receipt-/Scopebindungen,
beibehaltene tatsächliche Reader-/API-/Eigentums-/Zustands-/Cleanupfloors und
vor Native geprüfter Dimensions-TRY/CATCH-Ausführungsscope. Source6/CP3/hard6,
neue Effekte null und getrennte Root-Compiler-/Nativeadmissions vor Ausführung.
Gemeinsam prior2Compiler/Container/Caller, höchstens vier zusätzliche Gesamt3–6;
erster Gesamt3 erreicht verpflichtenden Rootcheckpoint, kein Budgetreset.
Dokumentiertes DB_ID-int und Driver-smallint/Int16 bleiben getrennt, Ursache offen.

Gesamt3 tatsächlich FAIL/UNKNOWN_STOP; Pflichtcheckpoint3 durch unabhängigen
Rootreview geschlossen. Compiler46412/poll0/rc0/0,712391s, zwei CS1701-WARNs;
Top57876/poll1/rc1/12,640812s, Child65112/poll0/rc0, kein Timeout.
Child meldet acht tatsächliche Typfelder einschließlich DB-ID-int/Int32,
31 vollständig beendete Readerteilschritte und zehn API-Enden, zwei Native-/
JSON-Vektoren vor/nach unverändert, NULL(3) und spezifische SQL-Abweisung42204
mit allen sechs Fehlerfeldern. Der Parent verwirft bereits OPEN:
tatsächliches Encrypt=True, eingefrorenes Oracle erwartet Encrypt=Mandatory.
Die isolierte In-Memory-Gegenprüfung aller übrigen Recordfloors ist kein
geänderter tatsächlicher Lauf oder Runtime-PASS; Originale/UNKNOWN bleiben.
Sechs bekannte SQLcmdenden/ein Vollstate/keine Controls, null Folge-SQL;
eine volle eigene Containment und frische ganze CID-/Namensabwesenheit.
SQLcleanup NOT_ESTABLISHED/DB- und Inputabwesenheit false/closed false.
Alle 71 Sources und Originalbytes erhalten. Kumulativ drei Compiler/Container/
Caller, drei verbleibende Gesamt4–6; kein automatischer vierter Versuch.
Aktuelle vollständige PR-/Head-/Main-/Tree-/FF-/Branch-/Sicherungs-/Worktree-
Integration folgt. Danach ausschließlich neue eigene Source-/Scopebasis mit
quellengeprüfter präziser OPEN-Auswertung, fortgeführten prior3/rest3 und
neuen Rootgates; kein Aufruf des gestoppten Pakets oder alter Ressourcen.
Volle Runtime-/Wire-/TSK-004-/Workstreamabnahme bleibt offen.

## TSK-004: eigener geänderter Caller mit Sessionreader nach PR235

PR235 vollständig geschlossen: neun Head-/sieben Main-Gates, voller Tree,
Maind5ee1864/FF/Branches, 39 private Dateien gesichert/eigener Worktree archiviert.
Reiner Readervertrag kohärent gestoppt, keine Nativefreigabe aus Source-PASS.
Unmittelbar [geänderter eigener Caller](SQL_SERVER_2025_AI_READER_TRANSPORT_REVIEW.md):
neue V2-Source-/Receiptbasis und tatsächliche acht Readerfeld-/Read-/Projektions-/
Disposeenden, alte UNKNOWN-Originale und Ressourcen unverändert/nicht wiederaufgenommen.
Gemeinsames Nativebudget zählt alten Transport-C1 weiter: höchstens fünf
zusätzliche eigene Kandidaten/Container/Compiles/Caller, Gesamtcheckpoint3/hard6.
Source6/CP3/hard6; zusätzliche Effekte zunächst null, getrennte Rootadmissions
vor Compiler/Native. Alle alten FAIL/UNKNOWN- und Qualificationgrenzen erhalten.
R1/Gesamt2 tatsächlicher FAIL/UNKNOWN_STOP: Compiler29456/0/0,637039s/zweiWARN,
Top62976/1/11,574684s/Child35344/1/kein Timeout. Acht Driver-Typmetadaten,
GetInt32(1) wirft in Readerstep21 InvalidCastException bei DB_ID-Meldung
smallint/System.Int16; DisposeStep22 endet, ServerUnknown bleibt true.
Microsoft dokumentiert int: Grenze offen, keine allgemeine Server-/Wireursache.
Sechs bekannte SQLcmdenden/ein Vollstate, null Folge-SQL; einmal volle eigene
Containment/frische CID-/Namensabwesenheit, SQLcleanup NOT_ESTABLISHED/
DB-/Inputabwesenheit false/closed false. 71 Sources und Originale erhalten,
keine typed/Controls-Qualification. Vollständige aktuelle Integration folgt;
danach geänderte eigene DB_ID-int-Projektion innerhalb vier verbleibender
Gesamt3–6-Kandidaten, nächster Gesamt3 ist Checkpoint. Alte Pakete bleiben gestoppt.

## TSK-004: unabhängiger reiner Sessionreader-/Fehlervertrag nach PR234

PR234 vollständig geschlossen: sieben Head-/fünf Main-Gates, voller Tree,
Main24478d42/FF/Branches, 122 private Dateien hashverifiziert gesichert und
eigener Worktree tatsächlich archiviert. VECTOR-C1 bleibt FAIL/UNKNOWN_STOP,
SQLcleanup NOT_ESTABLISHED/DB- und Inputabwesenheit false; kein weiterer Lauf.
Unmittelbar [reiner Sessionreader-/Fehlervertrag](SQL_SERVER_2025_AI_SESSION_READER_REVIEW.md):
acht dokumentierte SQL-Typ-/Getterbindungen, geänderte eigene C#-Source,
sichere tatsächliche Readerfehlerenden und öffentliche Lesehilfe;
sechs Sourcekandidaten/Checkpoint3/hard6 und Stop nach Sourceabschluss,
keine Compiler-/CLR-/SQL-/Container-/Provider-/Modell- oder Hosteffekte.
Source-/Purefreeze und unabhängiger Rootreview vor aktueller Integration;
ursprüngliche Exceptionursache und volle TSK-004-Abnahme offen.
C1 SOURCE_ONLY kohärent: acht Typ-/Getter-/NULLbindungen, sieben neue normale
Methoden PID61124/poll0/rc0/0,253730s und fünf geschützt unter `-O`
PID51112/poll0/rc0/0,168936s, kein Timeout/UNKNOWN. 16 Guidelinks, Originale8Pins,
privateSource/Rawbytes und enger unabhängiger Rootreview bestätigt;
kein Compiler/CLR/SQL/Container/Provider/Modell/Hosteffekt. Source-STOP nach C1,
öffentliche Privacy und vollständige PR-/Main-/Tree-/FF-/Cleanupintegration folgen.
Alter Exceptiontyp/Fehlerursache UNPROVEN, kein typed/wire/runtime-PASS.

## TSK-004: neue begrenzte VECTOR-Transportwelle nach PR233

PR233 vollständig geschlossen: acht Head-/sechs Main-Gates, voller Tree,
Main 266e7298/FF-Synchronisierung, eigene Branches entfernt, 142 private Dateien
gesichert und eigener Worktree tatsächlich archiviert. Loader-/Typmetadaten-PASS,
Checkpoint3/STOP; alte VECTOR-Hard6/UNKNOWN-Welle unverändert und nicht wieder aufgenommen.
Unmittelbar [neue Transportwelle](SQL_SERVER_2025_AI_VECTOR_TRANSPORT_REVIEW.md):
geänderte gepinnte Caller-/Assetbasis, maximal sechs Kandidaten/eigene serielle
Container, zwei VECTOR(3)/FLOAT32-Rows, NULL-/Dimensionskontrolle, vollständige
Request-/Eigentums-/Zustands-/Cleanupwitnesses. Beginn mit Sourcevorbereitung,
Compiler/Container/SQL/Caller zunächst null und Rootgates vor jedem Effekt.

C1 tatsächlich FAIL/UNKNOWN_STOP: Compiler PID40932/poll0/rc0/0,586720s,
zwei CS1701-WARNs erhalten; Top PID55512/poll1/rc1/11,305835s, Child57608/
poll1/rc1, kein Timeout. Ein Container/sechs bekannte SQLcmdenden/ein Vollstate,
OPEN API_RETURNED, Sessionreader ohne vollständiges Ende/ursprünglicher
Exceptiontyp UNKNOWN_OR_UNCLASSIFIED. Danach null SQL und genau einmal volle
eigene Namespacecontainment; frische ganze CID-/Namensabwesenheit bestätigt.
SQLcleanup NOT_ESTABLISHED/DatabaseAbsent false/InputsAbsent false/closed false,
alle 68 Sources und Originale erhalten. Keine typed/NULL/Dimensions-/Controls-
Qualification; keine weiteren C2–C6 dieser Welle. Aktuelle Integration mit
Head-/Main-/Tree-/FF-/Branch-/Sicherungs-/Worktreeclosure folgt; anschließend
nur unabhängiger quellengebundener Sessionreader-/Fehlervertrag ohne Runtime.

## TSK-004: geänderte Loader-Auflösungsgegenprobe nach PR232

PR232 vollständig geschlossen: neun Head-/sieben Main-Gates, voller Tree,
Main 6f3a116f/FF-Synchronisierung, eigene Branches entfernt, 84 private Dateien
gesichert und eigener Worktree tatsächlich archiviert; SQL-CI nicht ausgelöst.
Bekannter C1-Loader-FAIL/COHERENT_DIAGNOSIS_STOP bleibt unverändert erhalten.
Der sichtbare [Folgeentscheid](SQL_SERVER_2025_AI_LOADER_RESOLUTION_REVIEW.md)
setzt die kumulative Sechsergrenze mit C2–C6 fort, Checkpoint nach C3.
Der Schnitt begann mit C2-Sourcevorbereitung: sichere Host-/Fehlermetadaten, danach bei bekanntem
FAIL geänderte eigene Dateilayouts. Keine SQL-Verbindung oder globale Hoständerung,
sticky UNKNOWN und frühere Hardstops unverändert. Neue Rootgates vor Effekten.
C2 ist tatsächlich bekannt beendet: Compiler PID 48964/poll 0/rc 0 und
Probe PID 61144/poll 1/rc 1, kein Timeout/UNKNOWN. .NET 10.0.12, vier Hostphasen
RETURNED, LOAD_SQLCLIENT/FileNotFoundException/THREW, sicherer Name
Microsoft.Data.SqlClient/PARTIAL_DISPLAY. DLL vorhanden, TPA 201/OwnClientInTpa
false, APP_PATHS null. Keine Typ-/SQL-Qualifikation. Kumulativ zwei Compiler/zwei
Proben, C1-86-Pins aktuell. C3: neuer eigener literal Bestand mit identischer
C2-DLL, keine Kompilierung; neue Source-/Pin-/Rootgates vor einer Probe/Checkpoint3.
C3 tatsächlich PASS ausschließlich für Loader/Typmetadaten: Probe PID 58712/
poll 0/rc 0/.126375s, kein Timeout/UNKNOWN, acht individuelle Enden vollständig,
SqlClient/Assemblyversion 6.0.0.0 aus eigener literal Datei/SHA und beide Typen
bestätigt. OwnClientInTpa true bei TpaCount 201; keine flache Client-DLL.
C1-86-/C2-69-Pins aktuell, kumulativ zwei Compiler/drei Proben und Checkpoint3.
STOP_AFTER_LOADER_METADATA_PASS, C4–C6 nicht ausgeführt, SQL null;
Typed-API-/SNI-/TDS-/SQL-/volle TSK-004-Abnahme und alte C6-Ursache offen.

## TSK-004: getrennte Assembly-Ladediagnose nach PR231

PR231 vollständig geschlossen: zehn erfolgreiche Head-Gates/Runtime-SKIP,
sieben erfolgreiche Main-Workflows/bestätigter Runtime-SKIP, voller Tree,
Main ee6e0cec/FF-Synchronisierung, eigene Branches entfernt, 138 private Dateien
gesichert und eigener Worktree tatsächlich archiviert. Layout COHERENT/WARN,
STOPPED_AFTER_C2; alte FileNotFound-Ursache UNPROVEN.
Unmittelbar [getrennte lokale Assembly-Ladediagnose](SQL_SERVER_2025_AI_LOADER_DIAGNOSIS_REVIEW.md):
eigener Probehost, feste Assembly-/Typmetadaten, sechs relevante Kandidaten,
Checkpoint nach drei, keine SQL-/Container-/Modell-/Hoständerungen.
Quellen, Tests, Pins und getrennte Rootadmissions wurden vor den Prozessen geprüft.
C1 ist tatsächlich gestoppt: Compiler PID 38628/poll 0/rc 0, Probe
PID 68400/poll 1/rc 1, kein Timeout/UNKNOWN. .NET 10.0.12/Main attestiert,
LOAD_SQLCLIENT/FileNotFoundException/THREW erfasst, MissingAssembly UNKNOWN;
Typprüfungen nicht erreicht. Bekannter Loader-FAIL, COHERENT_DIAGNOSIS_STOP,
SQL null und alte C6-Ursache weiterhin UNPROVEN. Folgeschritt nur mit geänderten
relevanten Eingaben und sichtbarem eigenen Vertrag; volle TSK-004-Abnahme offen.

## TSK-004: reiner Clientlayoutvertrag nach PR230

PR230 ist vollständig geschlossen: elf erfolgreiche Head-Gates und ein
Runtime-SKIP, acht erfolgreiche Main-Workflows mit bestätigtem Runtime-SKIP,
vollständiger Tree/Main 9d731f55/FF-Synchronisierung, eigene Branches entfernt,
121 Dateien gesichert und eigener Worktree tatsächlich archiviert.
ANN-Records bleiben COHERENT/WARN, Capturelücken bleiben sichtbar,
Replaypaket STOPPED_AFTER_C2. Unmittelbar [reiner Clientlayoutvertrag](SQL_SERVER_2025_AI_CLIENT_LAYOUT_REVIEW.md)
auf unveränderten PR229-Deps-/App-/Compilerpins: fünf Unterpfadabweichungen bei
flach kopierten Assets, FileNotFound-Ursprung UNPROVEN. EinOwner/engerRootreview,
sechs Sourcekandidaten mit Checkpoint nach drei und Abbruch nach sechs;
keine dotnet-, Assemblyload-, Provider-, SQL-, Container-, Modell-, Download-
oder Hostaufrufe.
Source-/Tests-/Expected-/Privacy-/Rootgates vor einer historischen reinen
Bestandsauswertung; kein impliziter Loader-/Runtime-PASS oder Hard6-Wiederaufnahme.
C1 endete bekannt mit FAIL_OFFLINE_LAYOUT/FIXED_PACKAGE_ASSET_SCHEMA; ein
Reportversuch, kein abgeschlossener Report, Originale unverändert und FAIL gesichert.
C2 bildet ausschließlich den tatsächlichen `resources`-Abschnitt ab; sichtbarer
Folgeentscheid mit kumulativ zwei Prozessen/Reportversuchen, danach Stop.
C2 ist tatsächlich abgeschlossen: PID 62428/poll 0/Returncode 0, kein
Timeout/UNKNOWN, Source COHERENT/WARN; 31 Dateien, 28 Runtimeassets und fünf
fehlende wörtliche Unterpfade bei vorhandenen flachen DLLs. Originale und
C1-Archiv51 unverändert, STOPPED_AFTER_C2. FileNotFound-Ursprung UNPROVEN,
Loader-/Typed-API-/TDS-/SQL-/Runtimequalifikation NOT_ESTABLISHED.

## TSK-006: reiner ANN-DML-/Rollenrecordvertrag nach PR229

PR229 vollständig geschlossen: sieben Head-/fünf Main-Gates, Main d28761f2,
voller Tree, FF/Branches und 391 hashverifiziert gesicherte private Dateien.
Worktree tatsächlich archiviert; initialer App-Anhanglimitfehler erhalten.
VECTOR-Welle bleibt FAIL_HARD6_UNKNOWN/SQLcleanup NOT_ESTABLISHED, kein Retry.
Unmittelbar [reiner IDX-012-Recordvertrag](SQL_SERVER_2025_AI_IDX012_RECORD_CONTRACT_REVIEW.md):
ein Implementer/enger Rootreview,6/CP3/hard6,0 neue SQL/Container/Provider/Modelle/
Hosteffects. Vorhandene DML-/Rollenakten, feste Counts/Reihenfolge/SID-/Guard-/
Restore-/Cleanupgrenzen; Callerflags ausdrücklich nur deklariert. Source-/Tests/
Privacy vor einem gebundenen historischen Offline-Durchlauf, fehlende individuelle
Captures nicht rekonstruieren. Runtimejob/Selector unverändert; volle Abnahme offen.

C1-Offline-FAIL bekannt beendet,0 completed_reports; erste Exception und erreichte
Aufrufversuche nicht erfasst. Root-/Owner-Byteeinsicht: ursprüngliche Marker sind
Base64, Handfixture/Consumer erwarteten Hex. C2 nach explizitem kumulativem
2-Prozess/4-Reportbudget: vollständige Base64-Marker-/Dateinamenbindung, alle
anderen Oracles/Expected/Workflow unverändert;13normal/3protected-O bestanden.
C2 tatsächlich2 Reports COHERENT/WARN/PIDend0/0,2396s;80 Aktenfiles/Source5/
Prepared2/Manifest vor/nach identisch,0Native. Fehlende Captures NOT_ESTABLISHED,
kein neuer Runtime-/TP-PERF-Claim. C1-FAIL erhalten, Paket STOPPED_AFTER_C2;
aktuelle Integration und anschließender unabhängiger statischer Driver-Pfadplan.

## TSK-004: nativer VECTOR-Caller nach vollständigem PR228-Abschluss

PR228 vollständig geschlossen:8Head/6Main, vollerTree, primaryMain48d4e187,
FF/Branches/916 hashverifizierte private Dateien/tatsächlicher Worktreearchiv.
Unmittelbar folgt der [begrenzte Nativecaller](SQL_SERVER_2025_AI_VECTOR_NATIVE_REVIEW.md).
SourceC1–C3 bleiben gezählt, jetztC4–C6/hard6 ohneReset; höchstens drei zusätzliche
eigene serielle Container. Gepinnter vorhandener SqlClient6.1.4/net10-Bestand,
keine neuen Pakete/Restore/globalen Effekte. Konkreter Compilerplan und aktuelle
Source-/Input-/Oracle-/Request-/Deadline-/Test-/Rootgates vor Nativeadmission.
Zwei VECTOR(3)-Rows/typedNull/Dimensionnegative/volle Guard-/Restore-/Cleanupbelege,
300normal/eine60Cleanup. Jetzt null neueNative/Modelle; PoolUNKNOWN gestoppt,
volle TSK004 und Workstreamabnahme offen.

C4-Compile bestanden (0,5911s, zwei erhaltene CS1701-Warnungen); Root-
Partialoutput-/Requestend-/Dimensionskorrektur mit vier neuen Methoden normal/-O
belegt, ohne weiteren Compile. C4 tatsächlicher FAIL vor Create an fehlender
USERPROFILE-Konfigurationswurzel: zwei CLI-Enden bekannt,0Create/SQL/Client,
UNKNOWN=false; historischer Ledger closed=false und SQLcleanupNOT_ESTABLISHED.
Root frische eigene Namens-/Inputabwesenheit unter geändertem ENV belegt, CID
NOT_CREATED; Temp-WARN und erste zu strenge stderr-Auswertung erhalten, keine
Abfragewiederholung. C5-Sourcekorrektur und exakter No-create-Proof vor neuer
Admission, C6 letzte Reserve. Kein stiller Ledgerreset, keine Poolwiederaufnahme.

C5 tatsächlich bekannter FAIL vor typisiertem Client: ein eigener Container,
acht SQLcmd-Aufrufe, vollständiger erster State mit vier null-Kataloggruppen.
Root bestätigte Originalrecords und tatsächlichen guarded Drop, frische SQL-/
CID-/Namensabwesenheit und Inputcleanup; UNKNOWN=false, C5 closed=true.
C6 korrigiert ausschließlich Producer-Arrayfallbacks, strenges Oracle bleibt.
Zwei neue pure Methoden nach erhaltenem Fixture-Lesecapfehler bestanden;
Sourcefreeze/93 C5-Archivdateien gebunden. Native erst nach aktuellen Rootgates.
Nach C6 STOP dieses Budgets unabhängig vom Ergebnis, anschließend Integration.
Details: [Native-Nachweis](SQL_SERVER_2025_AI_VECTOR_NATIVE_REVIEW.md).

C6 tatsächlich FAIL_HARD6_UNKNOWN: korrigierter Vollstate bestanden, Child
bekannt mit rc1/FileNotFoundException beendet, individuelle Requests fehlen.
UNKNOWN sticky, kein Folge-SQL oder SQLcleanup-PASS, Nativeinput erhalten und
Ledger closed=false. Genau ein gebundener Namespaceabbau und frische ganze
CID-/Namensabwesenheit bestätigt. Welle beendet, keine weitere Probe/Fix;
gesamt zwei eigene Container/14 SQLcmd-Aufrufe/ein .NET-Child/0 neue Modelle.
Root-Abschlussprüfung bestanden; Integration dieses Fehlercheckpoints folgt.
Nächster unabhängiger Schnitt: TSK-006, gebundener reiner ANN-DML-/Rollenvertrag
auf vorhandener Evidenz, zunächst ohne Native-/Provider-/Host-/Modellaufrufe.


## TSK-004: isolierte native VECTOR-Client-Sourcevorbereitung nach PR227

PR227 vollständig geschlossen (8Head/6Main, Tree/FF/Branches/Belege/Archiv).
Der [neue begrenzte Clientpfad](SQL_SERVER_2025_AI_VECTOR_CLIENT_REVIEW.md) nutzt
vorhandenes SDK10.0.401 und projektlokal gepinntes SqlClient6.1.4 ohne globale
Installation/Hoständerung. MATERIAL-Dependency-/Lizenz-/Hash-/Lock-/Auditprüfung
und Codevorbereitung vor tatsächlichem CLRprovider-/SQL-/Containerlauf; ein
initialer Restore/max120s/40Pakete/150MB, einCompile/max90s.6/CP3/hard6,
später max6 eigene serielle Container/einer je Kandidat nur nach aktuellen
Source-/Privacy-/Tests-/Rootgates.0Native/Modelle jetzt, PoolUNKNOWN nichtresumiert,
volle Typ-/Wire-/Treiber-/TSK004-Abnahme offen; andereRepos unverändert.

Checkpoint3: C1 FAIL an der isolierten NuGet-Konfigurationswurzel; C2 erreichte
31 Pakete, überschritt jedoch150MB und bleibt FAIL. Sein SDK-Ende ist nur durch
den geprüften communicate-/wait-Quellenpfad gebunden; fehlende individuelle
PID-/Returncode-/poll-Felder werden nicht rekonstruiert. Geänderter C3 mit300MB
bestand in einem Compile ohne Restore (3,3033s, tatsächliche PID/poll0/rc0).
31 gehaltene/27 ausgewählte Pakete, Lock-/Dateihashes, Lizenzen und Auditkanäle
getrennt geprüft; vier neue reine Gegenfälle normal/-O und enger Rootreview PASS.
Die private Library wurde nicht ausgeführt. Aktuelle Privacy-/PR-/Main-/Tree-/FF-/
Branch-/Belegsicherungs-/Worktreegates vor Integration; Nativecaller und volle
TSK004-Abnahme offen. Pool-UNKNOWN wird nicht wiederaufgenommen.


## TSK-004: Engine-/CL-/Client-Lesehilfe nach vollständigem PR226-Abschluss

PR226 vollständig geschlossen (10Head/8Main/Runtime, Tree/FF/Branches, gesicherte
Belege/eigenerWorktree). Der unmittelbar folgende
[Dokumentschnitt](SQL_SERVER_2025_AI_VECTOR_COMPATIBILITY_REVIEW.md) verbessert
den Einstieg anhand dreier Grenzen und dreier Fälle. Zwei Textkandidaten,
15 lokale Links/Produktprivacy2/enger Root-Aussageabgleich PASS; abschließende
Sechs-Dateien-Privacy und aktuelle PR-/Main-/Tree-/FF-/Cleanupgates vor Integration.
Keine neuen SQL-/CLR-/Provider-/Modell-/Containerproben oder Installationen.
Native Binärbindung/float16/volleTSK004 offen; Pool-UNKNOWNwelle bleibt gestoppt.


## TSK-004: unabhaengiger Engine-/CL-/Client-Dokumentschnitt vorbereitet

Der [begrenzte Abgleich](SQL_SERVER_2025_AI_VECTOR_COMPATIBILITY_REVIEW.md)
trennt Serverbuild, Compatibility Level und Clienttransport fuer den Einstieg.
Eigener Worktree/Sourcevorbereitung waehrend PR226-CIgates, Publikation erst nach
vollstaendigem PR226-/Tree-/FF-/Cleanupabschluss. Vorhandene Primaerquellen und
bestandene enge Teilnachweise; keine neue SQL-/CLR-/Provider-/Modell-/Containerprobe
oder Treiberinstallation, kein Reset der Pool-UNKNOWNwelle. 6/CP3/hard6 reine
Textkandidaten; native binaere Treiberbindung/float16/volleTSK004 offen.


## TSK-009: korrigierter öffentlicher Pool-Sourceabschluss vor Integration

Der [öffentliche Pool-Schnitt](SQL_SERVER_2025_AI_POOL_PUBLIC_REVIEW.md) ist
SOURCE_ONLY auf aktuellen15Sources:25neueMethoden über betroffene Prüfungen,
zuletzt4normal/-O mit vollständigen Originalkanälen PASS; AST3/Privacy11/Rootreview
geschlossen. APPDATA-only Namespaceumgebung, vollständige .ID-Abfragen,
--time=0-Abbau und sticky mutatives UNKNOWN korrigiert.
C1/C2FAIL/einContainer/0SQLcmd/0Poolchildren und getrenntes RecoveryUNKNOWN
bleiben erhalten; frische ganze CID/Name/Inputs abwesend, keinC3. Native-/SQLcleanup-/
TP-CON-Qualifikation NOT_ESTABLISHED. Aktueller PR-/Head-/Main-/Tree-/FF-/
Branch-/Worktreeabschluss folgt; unabhängige autorisierte Arbeit geht weiter.


## TSK-009: öffentliche Pool-Nativewelle nach UNKNOWN angehalten

[Öffentliches opt-in RED-Poolprofil](SQL_SERVER_2025_AI_POOL_PUBLIC_REVIEW.md):
C1 FAIL vor Create, C2 FAIL nach einem eigenen Container an Podman-Feldcase,
je null SQLcmd-/Poolchild-/Modellaufrufe. Root Resourcecleanup überschreitet den
8s-Cap; Request-Ende UNKNOWN bleibt sticky. Frische tatsächliche vollständige
CID-/Namens-/Inputabwesenheit bestätigt, kein zweiter rm/keine Folge-SQL.
Nativewelle nach zwei Kandidaten/einem Container gestoppt, keine C3-Probe.
Unabhängige reine Feldcase-/FullCID-/Abbau-/UNKNOWNkorrektur, betroffene Checks
und PR-/Main-/Tree-/FF-/Cleanupintegration folgen. Öffentliche Runtimequalifikation
und ursprünglicher SQL-/Profilcleanup NOT_ESTABLISHED; volle Abnahme bleibt offen.


## TSK-009: öffentlicher Poolproducer C1 vor Create fehlgeschlagen

Der [öffentliche opt-in RED-Poolproducer](SQL_SERVER_2025_AI_POOL_PUBLIC_REVIEW.md)
hat aktuelle Source-/Privacy-/Rootgates bestanden. C1 scheitert an der ersten
Podman-Abfrage mit beschränkter CLIumgebung, vor Create/SQL/Poolchild: null neue
Container/SQLcmd-/Modellaufrufe, kein UNKNOWN, tatsächliche neue Namensabwesenheit
in separater read-only Diagnose. Historischer FAIL/kein erfundener CIDabschluss.
Gezielte eigene CLIumgebung-/No-create-Failkorrektur wird vorbereitet; Native C2
erst nach geändertem gebundenem Sourceabschluss. 6/CP3/hard6 und bestehende
Host-/Cloud-/ONNX-/Fremdrepogrenzen unverändert; voller Runtime-/TP-CON-Nachweis offen.


## TSK-009: öffentliche Poolproducer-Sourcevorbereitung nach vollständigem PR225-Abschluss

PR225 vollständig geschlossen: c7dec2b15eb521f467690e6f33290a6088f2dd82,
10 Head/8 Main einschließlich betroffener Runtime-CI PASS, voller identischer Tree,
primärer Main FF/synchron/sauber, eigener Branch lokal/remote entfernt.
Im eigenen Worktree folgt der [öffentliche opt-in RED-Poolproducer](SQL_SERVER_2025_AI_POOL_PUBLIC_REVIEW.md),
zunächst SOURCE_ONLY. Aktuelle Sources/Privacy/Tests/enges Rootreview vor lokaler
Nativeadmission. 6/CP3/hard6/max6 neue eigene serielle Container/einer jeKandidat;
keine Default-RED-/Host-/Cloud-/ONNX-/Fremdrepoeffekte. Einzelne tatsächliche Client-
Requestreceipts, Marker-/HeldSID-/Source-/State-/Negativ-/Physical-/Cleanupbindung
werden konkret umgesetzt. Öffentlicher Runtime-/TSK009-/TP-CON-Nachweis noch offen.


## TSK-009: öffentliche Poolproducer-Sourcevorbereitung während PR225-Maingates

PR225 ist auf c7dec2b15eb521f467690e6f33290a6088f2dd82 gemergt, zehn Head-Gates PASS;
acht Main-Gates/primäre Synchronisierung/Cleanup werden noch im Orchestrator gebunden.
Der eigene Worktree bereitet unabhängig den [opt-in RED-Poolproducer](SQL_SERVER_2025_AI_POOL_PUBLIC_REVIEW.md)
vor: drei eigene Logins, zwei VECTOR(3)-Rows, sechs authentifizierte Checkouts,
tatsächliche Request-/Source-/Marker-/Principal-/State-/Negativ-/Cleanupverträge.
SOURCE_ONLY: 6/CP3/hard6, ein Owner/enger Rootreview, null lokale Domainprozesse/
SQL/Container/Provider-/Modellproben. Native erst nach vollständig geschlossenem
PR225 und aktuellem gebundenem Quellenabschluss/Admission. Maximal sechs neue eigene
serielle Container, einer je Kandidat; kein Default-RED-/Host-/Cloud-/ONNX-/Fremdrepo-
Effekt. Alle tatsächlichen Runtime-/Provider-/Serverrequest-/TP-CON-Grenzen offen.


## TSK-009: öffentlicher SQLcmd-Clientadapter nach PR224

PR224 vollständig geschlossen (8 Head/6 Main, Tree/FF/Branches), Main
04e4f08a8dfc9b5121a112c1083a1622f9057ecc. Unmittelbar folgt der
[öffentliche Clientadapter](SQL_SERVER_2025_AI_POOL_CLIENT_REVIEW.md): tatsächliche
Framework-APIs, Capturebindung an dasselbe gehaltene Prozessobjekt, sticky UNKNOWN,
Privacy vor Digests und unveränderte Deadlines mit erforderlicher Cleanupreserve.
SOURCE_ONLY: 6/CP3/hard6, ein Owner/enger Rootreview, null lokale echte Prozesse/
SQL/CLR/Container/Modelle/Provider-Metadaten. Neue Kontrollfolgentests mit Fakehandles;
keine Wiederholung alter grüner Checks oder privater C3-Proben. Pfadbetroffene CI
bleibt Pflicht; kein Selector-/RED-Defaultwechsel. Voller Producer/Runtime offen.


## TSK-009: öffentliche V2-Capturevorstufe nach PR223

PR223 vollständig geschlossen (8 Head/6 Main, Tree/FF/Branches), Main
c0e40cf8945cc7e135b871ed26641e223dc29d6d. Unmittelbar folgt die
[V2-Capturevorstufe](SQL_SERVER_2025_AI_POOL_CAPTURE_REVIEW.md): ausschließlich
vorhandene öffentliche Sources und kleine Capturehelper/Vertrag/Tests; V1 bleibt
unverändert. Processende ist kein TDS-Beweis, SQLcmd-InputSHA nur vor ENV-Expansion,
Credentialprüfung vor Digests; Timeout/UNKNOWN sperren Folge-SQL. 6/CP3/hard6,
ein Owner/enger Rootreview, heute null neue Prozesse/SQL/Container/Modell-/Provider-
Metadatenaufrufe. Keine Legacy-/C3-/CLRprobe, Default-CI ohne RED und keine Workflow-/
Selectorausnahme. Öffentlicher Producer/Nativeadmission bleibt separater Folgeumfang.



## TSK-009: öffentlicher Poolrecordvertrag kohärent, Capturegrenzen WARN

PR222 ist vollständig integriert (7 Head/5 Main, Tree/FF/Branches geschlossen).
Der [öffentliche reine Poolrecordvertrag](SQL_SERVER_2025_AI_POOL_RECORD_REVIEW.md)
ist implementiert: 14 neue reine Methoden mit betroffenen PASS-Nachweisen, drei
optimierte Root-Schutzmethoden und neuer optimierter Captureshape-Gegenfall bestanden.
C1-Offline-FAIL (nicht erfasstes predicates.operation) erhalten; C2 konsumiert
unveränderten C3-Payload erfolgreich: sechs Checkouts/drei physische Reuses/Resets,
zwölf vollständige Ergebnisse, acht Queryquellrows, zwei Vollstates und komplette
Rawclosuretexte. Record-Kohärenz PASS, Gesamtstatus WARN; individuelle Request-/
Inputcaptures fehlen und bleiben NOT_ESTABLISHED, Callerprovenienz nicht unabhängig
attestiert. Zwei Quellenkandidaten/zwei Reportaufrufe, kein weiterer Replay nach PASS,
max6/CP3/hard6 ohne Reset; null neue SQL-/Container-/Modell-/Metadatenaufrufe.
Kein Demos09-/Workflow-/Selectorwechsel. Aktuelle PR-/Main-Gates/Integration/FF/
Branches folgen vor Abschluss. Öffentlicher Producer/Capture-/Admission-/Recovery-
Runtimevertrag und volle CON-010-/TSK-009-/TP-CON-Abnahme bleiben offen.

## TSK-009: private Poolkomponente in C3 bestanden

Nach vollständig integriertem PR221 bestand die
[begrenzte private Poolkomponente](SQL_SERVER_2025_AI_TENANT_POOL_REVIEW.md)
in C3: sechs tatsächliche Checkouts, drei physische Wiederverwendungen und getrennte
Poolkeys/Serververbindungen; zwölf vollständige Before-/After-Identitäts-/Row-/
Kontextergebnisse, Reset vor Reparatur, zwei identische Vollstates. Tatsächliches
OwnClearPool/Close/neue physische Abwesenheit, gehaltene Login-Drops vor DBdrop,
frische getrennte SQL-/CID-/Namens-/SQLinputabwesenheit; kein UNKNOWN.
Root schloss [Quellen- und Recordreview](SQL_SERVER_2025_AI_TENANT_POOL_SOURCE_REVIEW.md)
unabhängig. Drei eigene Container/37 SQLcmd-Handles plus drei separate Poolchildren,
C3 17 Handles; beide historischen FAILs erhalten, C1/C2 SQL-/Pool-Cleanup
NOT_ESTABLISHED. Checkpoint3 gebunden; keine weitere Probe nach PASS. Alle Aktionen
innerhalb derselben 60s-Cleanupdeadline ab vor dem höchstens 40s-Child, kein Reset.
Keine neue Dependency, Inferenz, Provider-/Cloud-/Hoständerung oder rote Standard-CI.
Private Admission-/Messrecords bleiben privat. Öffentliche Poolconsumer, weitere
Provider/Authformen, Performance, ANN (Approximate Nearest Neighbor; näherungsweise Suche nach ähnlichen Vektoren)/Seitenkanäle, Passwort-/TLSintegrität und volle
CON-010-/TSK-009-Abnahme bleiben offen. Aktuelle PR-/Main-Gates, Integration,
Synchronisierung und eigener lokaler/Remote-Branchcleanup folgen vor Abschluss.

## TSK-009: Poolvorbereitung nach vollständig geschlossenem PR220

[PR220](https://github.com/gecompat/SQL_PerformanceSchulung/pull/220) ist auf
`a0b01f4515677a546841797a00c492a8dd695826` vollständig abgeschlossen: acht aktuelle
Head-/sechs Main-Workflows PASS, vollständiger identischer Tree, main FF/sauber,
eigener lokaler und Remote-Branch entfernt. Arbeitsheft und Trainerleitfaden
enthalten drei optionale Evidenzleseaufgaben; Teilnehmer-/Generalprobe offen.

Unmittelbar folgt die [begrenzte Poolvorbereitung](SQL_SERVER_2025_AI_TENANT_POOL_REVIEW.md)
unter TSK-009/CON-010. Vorhandene öffentliche SqlClient-Oberfläche read-only
bestätigt; kein Open/SQL/Poolclear/Download. Scope-Review korrigierte vor Code
die unbelegte Client-GUID-Gleichheitsannahme: physische Wiederverwendung benötigt
tatsächliche Owner-DMVconnection_id/connect_time mit voller Session-/SID-/DB-/
ApplicationName-/Noncebindung. Reset wird vor Reparatur beobachtet; nur eigene
Pools, Credentialinstanzen und neue Login-/DB-/Containerleases.

Sechs Quellenkandidaten/maximal sechs neue serielle eigene Container, Checkpoint3/
hard6, je ein Profil mit sechs Checkouts, 300 Sekunden plus einmal60 Cleanup.
Source-/Review-/exklusive Admission vor Native offen. Private Codevorbereitung
darf ohne Native parallel zur Scopeintegration beginnen. Keine neuen Dependencies,
Modell-/KI-Provider-/Cloud-/Hoständerungen oder rote Standard-CI. C5-Authbasis bleibt
separater Teil-PASS; öffentliche WITHOUT-LOGIN-Demo und volle Pool-/TSK-009-Abnahme
bleiben offen. Andere Repositories unverändert; allgemeine Entwicklung/DGN-007 pausiert.


## TSK-012: optionale Belegleseaufgaben nach PR219

[PR219](https://github.com/gecompat/SQL_PerformanceSchulung/pull/219) ist auf
`7571af81ae3286d398e7c397b4f27840daf49e78` vollständig abgeschlossen: acht aktuelle
Head-/sechs Main-Workflows PASS, ganzer Tree identisch, main FF/synchron/sauber,
eigener lokaler und Remote-Branch entfernt. Der begrenzte private Authentifizierungs-
PASS und vier historische FAILs bleiben in ihrem jeweiligen Scope.

Unmittelbar folgt ein unabhängiger Textschnitt in
[Arbeitsheft](../HowTo/SQL_SERVER_2025_AI_OFFLINE_WORKBOOK.md) und
[Trainerleitfaden](../HowTo/SQL_SERVER_2025_AI_OFFLINE_TRAINER_GUIDE.md): drei optionale
Leseaufgaben zu tatsächlichem Embedding/SQL-Retrieval, gescheiterter Generation und
begrenzter Login-Trennung. Zweck, vorherige Erwartung, Beobachtung und Aussagegrenze
bilden den Einsteigerpfad. Lösungen und optionale Rubrik bleiben nur im Arbeitsheft;
acht Basisaufgaben/16 Punkte und RES-008 bleiben unverändert.

Ein Implementierungsverantwortlicher, ein enges Root-Fakten-/Didaktikreview, maximal
sechs zusammenhängende Textkorrekturkandidaten, Checkpoint3/hard6. Zwei Material-
und drei kanonische Steuerdateien, keine neue Kennung. Null neue Modell-, SQL-,
Container- oder Office-Ausführung. Der vorhandene 61-Folien-Artefaktnachweis wird
übernommen; Lehrzeiten, Lernwirksamkeit und Generalprobe bleiben unqualifiziert.
Aktuelle Head-/Main-Integration und eigener Cleanup sind über PR220 abgeschlossen.
Allgemeine Entwicklung und DGN-007 bleiben pausiert; GenerationHard6 bleibt FAIL.

## Tenant-Authentifizierung: begrenztes Profil bestanden

Nach vollständig geschlossenem PR218 ist die
[private Serverlogin-Komponente](SQL_SERVER_2025_AI_TENANT_LOGIN_REVIEW.md) unter
TSK-009/CON-010 nativ begrenzt bestanden: C5 mit drei tatsächlich getrennten
Login-/User-/SIDidentitäten, eigenen A/B-Quellen und authentifiziertem Unmapped,
Sessionmanipulation/Reset, drei tatsächlichen Rechtefehlern, fünf realen
Eigentumsabweisungen und 23 vollständigen Zustandsaufnahmen einschließlich Restore.
Echte drei Login-Drops vor DBdrop, getrennte frische SQL-/CID-/Namens-/Inputabwesenheit,
kein UNKNOWN. Fünf eigene Container/95 tatsächliche Clienthandles insgesamt,
davon C5 60; vier historische FAILs erhalten. C1–C3 SQL-Abwesenheit NOT_ESTABLISHED,
eigene Namespaces zerstört; C4 und C5 tatsächlicher SQL-Cleanup bestanden.
Checkpoint3 eingehalten, kein weiterer grüner Lauf und kein Budgetreset.
Null Modell-/Provider-/Cloud-/Hosteffekte. Öffentliche Demo bleibt WITHOUT LOGIN;
Passwortintegrität, Pooling, ANN und volle TSK-009-/TP-CON-Abnahme offen.
Aktuelle Head-/Main-Gates, vollständige Integration und eigener Branchcleanup
sind über PR219 abgeschlossen. Danach unmittelbar unabhängige TSK-012-Belegleseaufgaben aus vorhandener
Evidenz, ohne weitere Modell-/SQL-/Officeausführung. Allgemeine Entwicklung und
DGN-007 bleiben pausiert; Generatorwelle bleibt FAIL/Hard6.

## Lokale Generatorwelle abgeschlossen: FAIL

Sechs geschlossene Kandidaten, fünf tatsächliche Inferenz-/31 Metadatenrequests,
kein korrekter positiver Antwortfall. Kein Negativfall gestartet; keine bestandene
Enthaltung. Alle eigenen Caller und Requestenden bestätigt, kein UNKNOWN. Null
neue SQL-/Container-/Cloud-/Hoständerungen. Vollständiger unveränderter Lab-Export
nach Native erneut geprüft. Historische FAILs und ausdrückliche C6-Vorverarbeitung
bleiben sichtbar. Hard6 erreicht, keine weiteren Calls dieser Welle. Eine neue
begründete Route benötigt geänderten Vertrag/Evidenz und endliche neue Planung;
volle Live-RAG-/QRY-020-/TSK-007/008-Abnahme bleibt offen. Modell-/Tokens unbekannt.
Details: [begrenzter Generationsnachweis](SQL_SERVER_2025_AI_GENERATION_COMPONENT_REVIEW.md).
Unabhängige lokale Tenant-/Serverloginqualifikation unter TSK-009 folgt nach
vollständiger Integration; allgemeine Entwicklung und DGN-007 bleiben pausiert.


## Historischer DGN-010-Veröffentlichungscheckpoint nach PR195

PR195 vollständig abgeschlossen: Head 83333b8d69532de77ddeab8b04f290e66e619c2f,
acht Head-Workflows PASS; Squash 398fecc664419cec5332b456de60c80498045d36,
sechs Main-Workflows PASS; ganzer Tree 93a2a03e4c42552cfe6342be71064014ac195eec
exakt übernommen, main FF/sauber, eigener lokaler/Remote-Branch entfernt.
Damals unmittelbar folgende Veröffentlichung: begrenzter SELECT-/DML-Runtimeproducer
im Branch codex/sql2025-ai-dgn010-public. DGN-010 bleibt PROPOSED; vollständiger
TP-PERF-/Nettonutzen-/Insert-/Worker-/Plan-/Modulclaim bleibt offen.

Vor Admission fest: sechs kohärente Quellenkandidaten, je höchstens 14 neue eigene
serielle Container, insgesamt höchstens 84. Je Scope zwei Versions-SKIPs für
2019/2022, zwei vollständige SQL2025-Lifecycles, zusätzlich ein kontrollierter
Setupfault pro Scope. 300 Sekunden reguläres Parent-/Profilbudget und 60 Sekunden
gemeinsamer eigener SQL-/Containercleanup, vier CPU (Central Processing Unit; Prozessor)/sechs GiB, feste vorhandene
Images, SQL2025 17.0.5005.3/Developer/CL170. 1000 synthetische Source-Rows,
MAXDOP/PREVIEW_FEATURES unverändert0, keine Host-/Provider-/anderen Repositoryeffekte.
Checkpoint nach geschlossenem Kandidaten; Retry ausschließlich nach relevant
geänderten Ausführungsquellen oder neuer Evidenz, historische FAILs erhalten.
Kandidat1: acht Versions-SKIPs erfolgreich; SQL2025-SELECT1 wegen falschem alten
Edition-Anzeigenamen SKIP_CONFIGURATION statt begrenztem Profil, Qualifikation
FAIL vor Setup. Alle neun eigenen Container/DBs abwesend, Endstatus bekannt.
Kandidat2 korrigiert ausschließlich die native Preflight-Editionsbindung auf
dokumentierte EditionID -2117995310/EngineEdition3, explizite NULLabwehr und
einen tatsächlichen Versions-/Editionsframe. Der geänderte gemeinsame Preflight
benötigt die Versionsqualifikation dieses Quellenkandidaten. Kein Budgetreset.
Aktuelle Head-/Main-CI qualifiziert den öffentlichen Consumer separat auf ihren
jeweiligen wegwerfbaren Instanzen; ein lokaler PASS ersetzt diese Gates nicht.

| Merkmal | Wert |
|---|---|
| Status | allgemeine Entwicklung `PAUSED`; begrenzter DGN-007-Abschluss gemäß `DEC-072` (DGN-007: beobachtete Intervallzuordnung und diagnostische QS-SYSUTC-Zeitklammer) in [PR 132](https://github.com/gecompat/SQL_PerformanceSchulung/pull/132), dessen aktuelle CI-/Merge-Evidenz maßgeblich ist; PR 68 und PR 128 fachlich ersetzt und nicht weiterzuführen |
| Stand | 2026-10-11; KI-Workstream aktiv gemäß §0, übrige Entwicklung pausiert |
| aktueller Integrationsnachweis | Foundation `1.21.0` und die vertragsbezogene CI-Testauswahl sind durch [PR 126](https://github.com/gecompat/SQL_PerformanceSchulung/pull/126) integriert. Die eigenständige Fehlerrohdiagnose aus [PR 130](https://github.com/gecompat/SQL_PerformanceSchulung/pull/130) ist auf `aea230fb65798afddd4643c92b84f09403819ec6` in `origin/main`; die [PR-130-Matrix](https://github.com/gecompat/SQL_PerformanceSchulung/actions/runs/38048742623) bestand auf 2019/2022/2025. Der neuere [Main-Lauf](https://github.com/gecompat/SQL_PerformanceSchulung/actions/runs/38050043409) scheiterte auf SQL Server 2019 an G13; die [PR-132-Matrix](https://github.com/gecompat/SQL_PerformanceSchulung/actions/runs/38051475267) auf SQL Server 2022 ebenfalls. Keine Reporterfreigabe. |
| früherer fachlicher Basisstand | `2f04deb2fed0faf5bedf70101fea3f4b93d46678` nach PR 123; Ledgerkomponente §32.5 und Loaderrecordformen §33 bleiben im bisherigen Nachweisstand; SESSION_END und operativer Bootstrap-/Kanalvertrag bleiben pausiert/offen; SQL-Codebasis `da7b0eb…` aus Pull Request 65 unverändert |
| geprüfter Runtime-Stand | `782799e` aus Pull Request 42; `OPT-017` (Ungleich verteilte parallele Arbeit)-Matrix vollständig grün |
| Fachliche Hauptwelle | `ADV-008` (Review QRY-004) und `W-COV-001` vollständig runtimevalidiert |
| Abgeschlossene Folgepakete | `W2-002`, `ADV-009` (Folienspezifikation Modul M03, Lernziel LO-M03-07), `ADV-010` (Folienspezifikation Modul M03, Lernziel LO-M03-08, Parametersensitive Planoptimierung), `LABSCN-002`, `LABSCN-004`, `INF-002`, `INF-003`, `LABINT-003` und der `CON-006` (Zyklische Sperrkonflikte erkennen)-bezogene `LABINT-004`-Schnitt `VALIDATED` |
| Szenariowelle | `CON-004` (Blockierungsketten verfolgen), `DGN-005` (Gezielte Ereigniserfassung mit Extended Events) und `CON-006` – Project Adapter `0.1` und vollständiger Docker-/Podman-Lifecycle auf SQL Server 2025 validiert |
| Folgeplanung | [Nächste Entwicklungswellen](NEXT_DEVELOPMENT_WAVES.md) |
| Zweck | kanonischer operativer Einstiegspunkt für Nachweisstand, offene Gates und nächste Schnitte |

## 0. Entwicklungspause und Wiederaufnahme

### Autonome Umsetzung des KI-Workstreams vom 2026-10-11

Der neue Benutzerauftrag autorisiert die autonome Entwicklung des integrierten
KI-Workstreams durch den Orchestrator. Die Implementierungsgrenze des ursprünglichen
Planungsauftrags ist damit für diesen Workstream aufgehoben; allgemeine Entwicklung,
DGN-007-Folgearbeiten bleiben pausiert. Die spätere ausdrückliche Freigabe
„Ja, Heartbeat einrichten“ autorisiert ausschließlich den Heartbeat dieses
KI-Orchestrator-Chats: `sql-2025-ki-workstream-orchestrator`, alle 30 Minuten,
ACTIVE seit 2026-10-11. Er setzt zulässige Arbeit fort und meldet nur wesentliche
Änderungen, Abschluss, Fehler oder nötige Entscheidungen. Andere Automationen
werden nicht wieder aufgenommen; Cloud-/Bezahl- und ONNX-Gates bleiben bestehen.

Der endliche Gesamtumfang sind `TSK-004` (KI-Feature-, Build- und Providerqualifikation)–`TSK-014` (KI-Generalprobe und Workstreamabnahme) und die 18 registrierten Demoentwürfe.
Erster zusammenhängender Schnitt: lokale Build-/Syntaxqualifikation aus `TSK-004` und
`QRY-014` (Vektortypen und Dimensionen)–`QRY-017` (Suchverfahren vergleichen) aus `TSK-005` (KI-Lokalpfad und synthetisches Korpus), auf eigenem Branch
`codex/sql2025-ai-local-demos`, Basis `fb53157eba381d23022b9a91aaa36a359f609576`.
Ein Implementierungsverantwortlicher führt den Schnitt; ein unabhängiger Review prüft
konkrete Sicherheits-/Versions-/Ergebnisrisiken. Pro Schnitt höchstens zwei kohärente
Korrekturwellen. Checkpoints sind lokale Qualifikation, stabiler Reviewkandidat und
validierte Integration. Bei ungelöstem Fehler, fehlender exakter Effektfreigabe oder
ausgeschöpfter Korrekturgrenze wird der betroffene Schnitt mit Evidenz angehalten und
eigener Cleanup abgeschlossen. Modell-/Tokenverbrauch ist unbekannt und wird nicht
als gemessener Wert ausgegeben.

Der erste Pfad verwendet synthetische Daten, float32 und eigene markierte Testdatenbanken.
Es werden weder bestehende Instanzen noch fremde Container verändert. Preview-, Modell-,
Cloud-/Bezahl-API- und ONNX-Pfade behalten ihre konkreten Qualifikations-/Freigabegates;
der lokale Pflichtpfad kann unabhängig fortschreiten. Die Rückmeldung des Benutzers bevorzugt die vorhandene
KI-Integration von SQL_Server_Lab. Der öffentliche lokale RAG-Controller ist der
zu prüfende Anwendungspfad; der interne HTTPS-Referenzslice ist getrennt von einem
allgemeinen Gateway zu behandeln. Cloudkosten und ONNX-Hoständerungen sind weiterhin
nicht freigegeben. Der Heartbeat ist eine Wiederaufnahmeabsicherung; ein regulär
abgeschlossener Schnitt führt im selben Turn zum nächsten zulässigen Schritt.

Die erste lokale Qualifikation von QRY-014 bis QRY-017 ist mit Ergebnisverträgen,
224 Markergegenproben, fünf fachlichen Negativkontrollen und eigenem Cleanup
belegt. QRY-017 meldet bei fehlender Full-Text-Komponente ausdrücklich WARN;
2019/2022 prüfen ausschließlich die Versionsgrenze. Der
[Implementierungsnachweis](SQL_SERVER_2025_AI_LOCAL_IMPLEMENTATION_REVIEW.md)
führt Charakterisierungsfehler und Korrekturen. Die unabhängige Quellenkontrolle
schloss alle vier Befundgruppen ohne weitere Safety-Befunde; sie ist kein eigener
Runtimebeleg. Alle 51 PR-Prüfungen am Head
`7831f9293d8e4653006c23e74b008e71707cabeb` bestanden, einschließlich der
[KI-Versionsmatrix](https://github.com/gecompat/SQL_PerformanceSchulung/actions/runs/38129371244).
[PR 135](https://github.com/gecompat/SQL_PerformanceSchulung/pull/135) ist in
`87017c04c04516495a4b653134532ac993db20ca` integriert. Vollständige Tree-Identität
des Squash-Ergebnisses wurde geprüft; main synchronisiert und der eigene
Arbeitsbranch lokal/remote entfernt. Alle 13 Main-Workflows desselben Integrationscommits
bestanden, darunter die [KI-Matrix](https://github.com/gecompat/SQL_PerformanceSchulung/actions/runs/38129793884)
und die [bestehende Regression](https://github.com/gecompat/SQL_PerformanceSchulung/actions/runs/38129793842).
Die anschließende Quellenprüfung des öffentlichen Modellpfads fand
eine konkrete Secret-Grenze: SQL_Server_Lab übergibt intern das SQL-Passwort als
sqlcmd-Prozessargument, entgegen DEC-033. Der
[Modellpfad-Leitfaden](../HowTo/SQL_SERVER_2025_AI_MODEL_PATHS.md#offene-secret-grenze-vor-live-rag)
bindet Quelle, Grenze und Wiederaufnahme. Kein Live-RAG-Aufruf, kein Lab-Run,
keine Änderung des anderen Repositorys. Nächster unabhängiger zulässiger Schnitt:
Offline-RAG (Retrieval-Augmented Generation; Antworterzeugung mit zuvor ausgewählten Quellen) QRY-018 aus TSK-008; die lokale Modellintegration aus TSK-007 bleibt
bis zu einem öffentlich nutzbaren passwortfreien Frameworkpfad angehalten.

Der zweite autonome Schnitt implementiert QRY-018 als modellfreien Offline-RAG-Replay,
Branch `codex/sql2025-ai-offline-rag`, Basis `0b6743f14f855103dfa63b0b67ffc75426f1ad1f`.
Zwei lokale 17.x-Lifecycles, 80 Markergegenproben, sieben fachliche Gegenproben,
Setup-Idempotenz und unabhängiger DB-/Containercleanup bestanden. Der unabhängige
Quellenreview fand im beauftragten Risikoscope keine offenen Befunde; keine zusätzliche
Runtimeattestation. Alle 49 aktuellen Headprüfungen bestanden; PR 137 ist in
`4de76ffc9eeb23882e5b6f4c02be3b32576b8f75` integriert. Tree-Identität, Synchronisierung,
lokaler/remote Branchabbau und alle elf Main-Workflows sind belegt im
[Offline-RAG-Nachweis](SQL_SERVER_2025_AI_OFFLINE_RAG_REVIEW.md). TSK-008 ist begonnen,
aber der Gesamtworkstream und der Livepfad bleiben offen.

Unmittelbar folgt QRY-019 aus TSK-009 auf `codex/sql2025-ai-sql-input-policy`, Basis
`4de76ffc9eeb23882e5b6f4c02be3b32576b8f75`. Der kontrollierte synthetische Harness
prüft eine feste vollständige SQL-Struktur, zwei tatsächlich gebundene Werte unter
QRY019_reader WITHOUT LOGIN und drei feste Rechteverweigerungen mit Bestandsnachkontrolle.
2019/2022 bestanden je zwei SKIP_VERSION-Lifecycles vor Setup und eigenen Cleanup.
Die aktuelle lokale 17.x-Qualifikation bestand zwei Lifecycles, fünf Ergebnisassertions,
80 Markergegenproben und acht fachliche Gegenproben; ein P2-Orakelfinding ist geschlossen.
Alle 49 Headprüfungen bestanden; PR 138 ist in `25a7c0af1b377b9250deeac4cf4288224900689f`
integriert. Tree-Identität, Synchronisierung, eigener Branchabbau und alle elf Main-Workflows
sind belegt im [QRY-019-Nachweis](SQL_SERVER_2025_AI_SQL_INPUT_REVIEW.md).
TSK-009 bleibt offen für Tenant-, Datenschutz- und weitere Providerfälle.

Der nächste zulässige CON-010-Schritt ist mit einer privaten 17.x-RLS-/Identitätsvorprobe
begonnen: drei Kontextfälle und drei tatsächliche Rechteverweigerungen bestanden samt
Sessionreset und eigenem DB-/Containerabbau. Konkreter Fehler und korrigierte Vor-/Nachbindung
stehen im [Checkpoint](SQL_SERVER_2025_AI_SQL_INPUT_REVIEW.md#nächster-checkpoint-private-con-010-vorbereitung).
Der vollständige CON-010-Kandidat wurde nach drei 17.x-Fehlversuchen und zwei
Korrekturwellen mit FAIL angehalten. Die neue Metadatenprobe belegt zusätzlich erzeugte
CONNECT-Grants als verbleibende Fixtureabweichung; Code und Registrierungsänderungen
wurden zurückgenommen, eigener DB-/Containerabbau ist belegt im
[Checkpoint](SQL_SERVER_2025_AI_TENANT_REVIEW.md). CON-010 bleibt PROPOSED. Nächster
unabhängiger Schritt DGN-009 bestand eine korrigierte private 17.x-Vorprobe mit
2 retrievten Quellen, Antworten/Tools je 1/3 und tatsächlichen Rechtefehlern 4613/229.
Der enge Quellenreview fand keine konkreten Befunde. Das daraus entstandene vollständige
DGN-009-Offline-Paket ist IMPLEMENTED und lokal qualifiziert: zwei 17.x-Lifecycles,
80 Markergegenproben, zehn Resultnegative und je zwei Versions-SKIPs auf 15.x/16.x,
jeweils eigener DB-/Containerabbau. Quellenreview und Integration sind abgeschlossen:
PR 141 bestand 49 aktuelle Headprüfungen; Squash
`8d3b074ddbfb4694f1d111ef41e56514da4a0391` alle elf Main-Workflows.
Tree-Identität, main-Synchronisierung und eigener Branchabbau werden
[getrennt geführt](SQL_SERVER_2025_AI_INJECTION_REVIEW.md).
Unmittelbar folgte die private DGN-008-Metadaten-/Rechtevorbereitung: tatsächliches
CREATE EXTERNAL MODEL ohne Inferenz, positiver parametrisierter SELECT und drei
Rechteverweigerungen 262/229/229 bestanden samt DB-/Container-/Netzabbau. Der erste
Readiness-Timeout und eine kohärente Korrekturwelle bleiben im
[Nachweis](SQL_SERVER_2025_AI_EXTERNAL_MODEL_REVIEW.md) sichtbar. Ein enger Quellenreview
fand keine konkreten Befunde. Der folgende vollständige DGN-008-Offline-Slice ist
IMPLEMENTED auf `codex/sql2025-ai-model-rights`, Basis
`eb203ed7f06abd3e52be2084fbc02e562eb3ecac`: getrennte Setup-/Ingestion-/Retrievalrollen,
tatsächliches Setup-CREATE, erlaubte Readerrow/Ingestion-Writes, fünf tatsächliche
Rechteverweigerungen nach Grantreduktion und volle Modell-/Rechte-/Endpointbindung.
Nach einer dokumentierten Korrekturwelle bestanden lokal zwei 17.x-Lifecycles mit
je neun Assertions, 80 Markergegenproben und zehn Resultnegative sowie eigener
DB-/Container-/Netzabbau. 15.x/16.x bestanden je zwei Versions-SKIPs vor SETUP;
der unabhängige Quellenreview fand keine offenen P1/P2. PR 143 bestand 49 Headprüfungen,
Squash `2f1dfec5d76cad63232f0a9eb968f880324ed5cf` alle elf Main-Workflows.
Tree-Identität, Synchronisierung und eigener lokaler/remote Branchabbau sind im
[Nachweis](SQL_SERVER_2025_AI_EXTERNAL_MODEL_REVIEW.md) geschlossen; Modell-EXECUTE
bleibt ausschließlich Metadatenrecht, Inferenz und echte Credential-/Egressabnahme offen.

Unmittelbar folgte eine begrenzte Podman-QRY-014-Providerprobe unter TSK-004:
17.0.5005.3 bestand zwei Lifecycles mit je drei Assertions, 48 Markergegenproben und
Setup-Idempotenz; 15.0.4490.9/16.0.4295.3 jeweils zwei Versions-SKIPs. Eigene DB-/
Containerabwesenheit bestand. Ein P2-Adapterfinding zu Prozesszeitgrenzen wurde mit
einer Korrekturwelle und vier privaten Timeoutgegenfixtures geschlossen; keine
unveränderte SQL-Wiederholung, keine empirische OCI-Hängequalifikation. Der
[Provider-Nachweis](SQL_SERVER_2025_AI_PROVIDER_REVIEW.md) begrenzt diese Aussage auf
QRY-014, keine vollständige Podman-/360-Matrixabnahme.
Für TSK-006 ist ein [konkretes lokales Preview-Freigabepaket](SQL_SERVER_2025_AI_PREVIEW_DECISION.md)
vorbereitet und inzwischen ausdrücklich vom Benutzer mit „Ja, lokalen ANN-Slice
freigeben“ genehmigt. Die Runtimequalifikation dieses begrenzten Effekts ist noch offen.
Andere zulässige Offlinearbeit bleibt ausführbar; Gesamtworkstream und Heartbeat bleiben aktiv.

Der Provider-/Previewcheckpoint ist über PR 144 mit sieben Headprüfungen und fünf
Main-Workflows integriert in `acd88e25e15932ff42154a7c40e436d8837aaee8`; Tree-Identität,
Synchronisierung und eigener lokaler/remote Branchabbau sind abgeschlossen.
Unmittelbar bestand eine neue private DGN-010-Ergebnis-/Storageprobe auf eigenem
Podman17.0.5005.3: je zehn gleiche volle Queryrows vor/mit/nach eigenem INCLUDE-Index,
1000 unveränderte SourceRows, 17 zusätzliche tatsächliche Indexseiten und unabhängiger
DB-/Containerabbau. Ein enger Quellenreview fand keine konkreten P1/P2. DGN-010 bleibt
PROPOSED; A/B/BA/AA, tatsächliche Pläne/Reads/CPU/DMLkosten und vollständige TP-PERF-
Abnahme fehlen. [Nachweis](SQL_SERVER_2025_AI_INDEX_HYPOTHESIS_REVIEW.md).
Dieser DGN-010-Checkpoint ist über PR 145 mit sieben Headprüfungen und fünf
Main-Workflows in `63f256fcbca522fa3ed7c2fdd6fee564c83381f1` integriert; Tree
`1908eeb9e1f4a9d97ae97e840627859fd9cd9eba`, Synchronisierung und eigener lokaler/remote
Branchabbau sind geprüft. Der folgende private CL-Slice ist nach zwei Korrekturwellen
mit FAIL angehalten: Skalaroracle ohne NULL-Gegenkontrolle, ungeklärter konkreter
Chunkfehler bei 150/160; nur die volle positive CL170-Chunkfixture und unabhängiger
eigener Cleanup sind belegt. [Grenzen und Wiederaufnahme](SQL_SERVER_2025_AI_COMPATIBILITY_REVIEW.md).
Keine dritte Korrektur. Dieser CL-/Freigabecheckpoint ist über PR 146 mit sieben
Headprüfungen und fünf Main-Workflows in `3ac552998996500849dcd29c9a855c5dd7063f92`
integriert; Tree `c36517efac6bb4c8d2f9fe9b279fc09cf39021c2`, Synchronisierung und
eigener lokaler/remote Branchabbau sind geprüft.
Unmittelbar folgte der neu konkret genehmigte lokale ANN-Slice. Sein erster privater
IDX-011-Prototyp ist nach zwei Korrekturwellen FAIL: Parser/Metadaten-/Vektorkonvertierung,
SQL-Recovery und konfiguriertes Cleanupbudget noch unqualifiziert. Alle drei eigenen
Container sind nach verifiziertem gezieltem Abbau abwesend; kein Index-/Recall-/Plan-
oder SQL-Restore-PASS. [Grenzen und Wiederaufnahme](SQL_SERVER_2025_AI_ANN_PREVIEW_REVIEW.md).
Keine dritte Korrektur oder automatische Rücksetzung dieses Slice-Budgets.
Der ANN-Fehlercheckpoint ist über PR 147 in
`73316d6fa0d1c86c528457d4b01a4250fe026e8f` integriert: sieben Headprüfungen,
fünf Main-Workflows, Tree `e2be0ab1b075423595b33ad9bb12b72b6ee7c246`,
Synchronisierung und eigener lokaler/remote Branchabbau abgeschlossen.
Der betreffende Runtime-Slice bleibt angehalten; Heartbeat und autorisierte
unabhängige Arbeit bleiben aktiv. Nächster unabhängiger Scope ist proportionales
Lehrmaterial für die acht bereits qualifizierten Offline-Demos, keine Wiederholung
der gescheiterten CL-/ANN-Prototypen und keine Gesamtlehrgangsfreigabe.
Der unabhängige TSK-012-Teilentwurf wird auf
`codex/sql2025-ai-offline-workbook`, Basis `e363d7e5d8927ffb4c4ce6e01e8740b93e8bc2a8`,
als [Offline-Arbeitsheft](../HowTo/SQL_SERVER_2025_AI_OFFLINE_WORKBOOK.md) umgesetzt:
acht Aufgaben mit Trainerlösungen, Beobachtungsbogen und didaktischer Rubrik.
Ein Owner, höchstens ein enger Review der neuen Fixture-/Rechte-/Providergrenzen und
zwei Korrekturwellen begrenzen den Scope. Keine Runtimequelle oder Präsentation wird
geändert; keine neue SQL-, Windows-/Podman-, Lehrzeit- oder Teilnehmerabnahme.
Betroffene lokale Doc-/Privacychecks und aktuelle Head-/Main-Gates sind vor Abschluss
erforderlich. Modell-/Tokenverbrauch bleibt unbekannt.
Die lokalen Guide-/Pfadprüfungen bestanden mit 31 Demos, Registry mit 264 Artefakten,
INF-001 mit sechs Runnern/neun How-to-Themen, Privacy, Diff und alle 27 Workbooklinks.
Der enge unabhängige Review fand keine konkreten P1/P2 in Aufgaben/Lösungen und deren
Fixture-/Rechte-/Providergrenzen; keine eigene Runtime oder Generalprobe ausgeführt.
Keine Korrekturwelle wurde benötigt. Die ausgewählten CI-Pfade führen statische
Gates aus; unveränderte SQL-Runtime und Officeprüfungen werden nicht wiederholt.
Der Arbeitsheft-Schnitt ist über PR 149 integriert: neun Headprüfungen auf
`4abed7167a6344279f1d81f028235adfd49556e3`, sieben Main-Workflows auf
`a566e23856758b7a1047dfbdb6641ffd094c7d82` bestanden. Tree
`f3bfe7241ef938c34b8d0b15148ce6a7047ba8ad`, Synchronisierung und eigener lokaler/remote
Branchabbau sind geprüft. Unmittelbar folgt auf `codex/sql2025-ai-offline-glossary`
der begrenzte [Grundlagenbegriffe-Teilentwurf](../HowTo/SQL_SERVER_2025_AI_OFFLINE_GLOSSARY.md).
Ein Owner, maximal zwei Korrekturwellen, keine Runtime-/Präsentations-/Regeländerung;
bekannte Quellen werden gezielt geprüft, kein erneuter Review der alten Democodebasis.
Die fünf ausgewählten Primärquellen wurden aktuell geprüft; 33 lokale Links im
Glossar/Arbeitsheft, sechs mathematische Beispiele, INF-001 und Privacy bestanden.
Keine SQL-Runtime ausgeführt. Für diese reine Begriffserklärung ist kein zusätzliches
unabhängiges Sicherheitsreview erforderlich; der Arbeitsheftreview wird nicht auf
neue Inhalte umgedeutet. Keine ausgeführte Korrekturwelle.
Der Glossar-Schnitt ist über PR 150 integriert: fünf Headprüfungen auf
`d51245e628661d4042b8d19590569b48f07b9ee5`, drei Main-Workflows auf
`86b08af7b355addae497b94f9f06e536414b6dd2` bestanden. Tree
`ee31572c5087a1bd512e1ab9629dc4628c8beebf`, Synchronisierung und eigener lokaler/remote
Branchabbau sind bestätigt. Unmittelbar folgt auf
`codex/sql2025-ai-podman-metrics-chunks` eine begrenzte zusätzliche Providerqualifikation
von QRY-015/QRY-016: je zwei Lifecycles auf 17.x sowie je zwei ältere Versions-SKIPs
auf 15.x/16.x, maximal sechs neue eigene seriell betriebene Podmancontainer.
Vorhandene lokale Images, Loopback, vier CPUs/sechs GiB, Env-only-Secrets und der
vorhandene Host-/SQLCMD-/FWK-Pfad bleiben erhalten. Ein Owner, maximal zwei
Korrekturwellen; keine neue SQL-Funktion, Previewaktivierung oder Hoständerung.
Alle Ergebnis-/Marker-/Cleanupkontrollen bleiben unverändert; nur die Auswahl
des privaten Providerhelpers wird auf die zwei vorhandenen Demo-IDs begrenzt.
Die sechs frischen Providerläufe bestanden: vier positive Lifecycles auf
17.0.5005.3 mit je drei Assertions sowie acht SKIP_VERSION-Lifecycles vor Setup
auf 15.0.4490.9/16.0.4295.3. QRY-015/016 bestanden Setup-Idempotenz, 48/80 volle
Markerfälle und jeweils zwei fachliche Negativkontrollen. Unabhängige eigene
DB-Abwesenheit und sechs ownergebundene Containerabbaue sind bestätigt.
Keine Korrekturwelle; kein neuer unabhängiger Review unveränderter Grenzen.
Der [Providercheckpoint](SQL_SERVER_2025_AI_PROVIDER_REVIEW.md#erweiterung-auf-qry-015-und-qry-016)
begrenzt die Aussage. PR 151 ist mit acht Headprüfungen auf
`3427e0c9bcb60ebb822ddcab19131a3e0e0e9f91` und sechs Main-Workflows auf
`608280e0b1aaae4a64fdc20cfab7bc0569ef654c` integriert. Tree
`0da1460fde61843d72864030ea0456ed8decbabc`, Synchronisierung und eigener lokaler/remote
Branchabbau sind bestätigt. Unmittelbar folgt auf `codex/sql2025-ai-podman-search-rag`
der unabhängige QRY-017/QRY-018-Podmanschnitt mit denselben sechs seriellen eigenen
Containern als Höchstzahl, je zwei Lifecycles je Demo und 15.x/16.x/17.x sowie maximal
zwei Korrekturwellen. Unveränderte SQL-/Runner-/Marker-/Ergebnisverträge; optionales
Full-Text-WARN bleibt sichtbar. Ein Owner, keine neuen Provider-/Secret-/Cleanupgrenzen.
Der QRY-017/QRY-018-Podmanschnitt bestand die erwarteten Verträge auf allen drei
Versionen: QRY-017 zweimal WARN bei fehlender optionaler Full-Text-Evidenz mit je
drei Assertions, QRY-018 zweimal PASS mit je vier Assertions; acht ältere
SKIP_VERSION-Lifecycles vor Setup. 48/80 volle Markerfälle, Setup-Idempotenz und
ein/sieben fachliche Negativfälle bestanden; eigene DBs und sechs Container sind
unabhängig abwesend. Kein Runtimefehler, keine Korrekturwelle. PR 152 ist mit acht
Headprüfungen auf `3d11f2f5c8f12d77c47619033573cac42bbfdd4e` und sechs Main-Workflows
auf `941b11dab7dc5c4e8cb0a09a95473368714392db` integriert. Tree
`a3ad175b984436e0b98cc24e2674090468e9b3e1`, Synchronisierung und eigener lokaler/remote
Branchabbau bestätigt. Unmittelbar folgt auf `codex/sql2025-ai-podman-security`
der unabhängige Podmanumfang QRY-019/DGN-008/DGN-009, maximal neun serielle neue eigene
Container für drei Engineversionen und je zwei Lifecycles, ein Owner und maximal
zwei Korrekturwellen. Unveränderte öffentliche SQL-/Runner-/Ergebnis-/Markerquellen,
gleiche private Helpergrenzen, kein Modellaufruf und keine fremde Instanzwirkung.
Die neun Providerläufe bestanden die erwarteten Verträge: je zwei positive
17.x-Lifecycles mit fünf/neun/acht Assertions, zwölf kontrollierte ältere
Versions-SKIPs vor Setup. Je 80 vollständige Markerfälle, Setup-Idempotenz und
acht/zehn/zehn fachliche Negativfälle bestanden. Eigene DBs und alle neun eigenen
Container sind unabhängig abwesend; keine Korrekturwelle. Der konkrete Podmanpfad
deckt damit alle acht implementierten Offline-Demos ab, einschließlich des
sichtbaren QRY-017-Full-Text-WARN. Keine allgemeine Provider- oder Gesamt-TSK-Abnahme.
PR 153 ist mit acht Headprüfungen auf `c76943cc823c66c5370b7de1d682cce39d4d3ddb`
und sechs Main-Workflows auf `e4482e4d73a860a9b7c2f1b8d7204df749e1d2f5` integriert.
Tree `1fcbda32716960d9fb2dd797f5c7fdb57ca06158`, Synchronisierung und eigener
lokaler/remote Branchabbau bestätigt. Unmittelbar folgt auf
`codex/sql2025-ai-ann-resume-decision` der konkrete
[ANN-Wiederaufnahmeentwurf](SQL_SERVER_2025_AI_ANN_RESUME_DECISION.md),
PENDING_USER_DECISION: maximal zwei zusätzliche Korrekturkandidaten, vier neue
eigene Container, unveränderte Effekte. Der enge unabhängige Review prüfte allein
dieses neue Paket gegen beide ursprünglichen Autoritäten und fand keine P1/P2.
Keine neue Runtime, keine dritte ANN-Korrektur; die privaten Quellen sind unverändert.
Nach Integration dieses Entscheidungspakets bleibt ANN bis zur Benutzerantwort
angehalten. Cloud-/ONNX-/Secret- und übrige Fehlgates werden dadurch nicht geöffnet.
PR 154 ist mit sieben Headprüfungen auf `e84b18b608b22c9e3c7671ca70ef499d3a7f5ab4`
und fünf Main-Workflows auf `4f74caeb55dcbdaabd9f2176e7ced9dd77c103dc` integriert;
Tree `5d0747591b6094af1295f2cd05ae8b34238e323c`, Synchronisierung und eigener lokaler/
remote Branchabbau bestätigt. Die ausdrückliche Antwort „Ja, Zusatzpaket freigeben
(empfohlen)“ autorisiert jetzt allein das dort begrenzte neue ANN-Budget.
Wiederaufnahme auf `codex/sql2025-ai-ann-resume`, Basis dieses Integrationscommits,
maximal zwei zusätzliche kohärente Kandidaten und vier neue eigene Container.
Historische private Quellen bleiben erhalten; Kandidat 1 wird separat vorbereitet,
lokal gegen Recovery-/Deadline-/Baselinefehler geprüft und eng unabhängig reviewt,
bevor neue SQL-Runtime erfolgt. Andere Fehlbudgets bleiben angehalten.
Die begrenzte Wiederaufnahme wurde mit [FAIL abgeschlossen](SQL_SERVER_2025_AI_ANN_RESUME_REVIEW.md):
Kandidat 1 verwarf die Setupausgabe vor ANN, deren Originalinhalt nicht erhalten wurde;
Kandidat 2 erfasste Baseline 0, scheiterte aber bei dynamischer CREATE VECTOR INDEX
an Parserfehler 343 und anschließend 51003. Beide zusätzlichen Kandidaten sind
verbraucht; zwei von maximal vier Containern genutzt, keine dritte Korrektur.
Vor Runtime bestanden sieben lokale Sicherheitsfixtures und der enge unabhängige
Review mit geschlossenem Image-Tag-P2; Kandidat 2 bestand zwei betroffene Baseline-
Gegenfixtures und den Deltareview. Beide tatsächlichen Recoveries meldeten RESTORED_0
und DROP_CONFIRMED; jeweils separate SQL-DB-Abwesenheit und gebundener eigener
Containerabbau/Abwesenheit bestanden, Cleanup 12,112/12,117 Sekunden.
Keine Indexgeneration, ANN-Rows, Recall-/Plan-/Performance- oder FWK-Abnahme.
Parser-/Previewursache bleibt offen; weitere ANN-Arbeit benötigt einen konkret
vorbereiteten Nachweisumfang und neuen Budgetentscheid. Der Fehlercheckpoint wird
mit aktuellen Head-/Main-Gates integriert; unabhängige Lehrmaterialarbeit folgt.
PR 155 integrierte den wahrheitsgemäßen ANN-FAIL mit sieben Headprüfungen auf
`63a4263d6cea1c9d07a1bf4039d7b90e2d208780` und fünf Main-Workflows auf
`2ce534ab2f6d638c5fb38615c3a06ded6088aaac`. Tree
`8d1faa5eb105bb9d702c69c83c5a2c4465746244`, Synchronisierung und eigener lokaler/remote
Branchabbau bestätigt. Unmittelbar folgt auf `codex/sql2025-ai-offline-trainer`
der unabhängige TSK-012-Teilentwurf eines Trainerleitfadens für genau die acht
qualifizierten Offline-Demos: Moderation, Reihenfolge und Umgang mit tatsächlichen
Status-/Cleanupgrenzen. Lösungen/Rubrik bleiben im Arbeitsheft; keine neue SQL-,
Teilnehmer-, Masterdeck- oder Gesamtcurriculumabnahme. Ein Owner, höchstens zwei
kohärente Korrekturwellen; keine neue Runtime oder unabhängige Reviewkette für
unveränderte Demoquellen. Alle 14 lokalen Materiallinks, INF-001-Ausführungspfad,
Datenschutz-/Metadatenprüfung und git diff --check bestanden. Aktuelle Head-/Main-
Gates und Integration dieses reinen Materialschnitts folgen.
PR 156 ist mit neun Headprüfungen auf `4345ecbfddbb97120e5a679978a19ed65e7411e7`
und sieben Main-Workflows auf `5b638544621b50ad6a8db2c1051c4250861d3490` integriert.
Tree `07992392e80c446f83970ba2885af96782344d00`, Synchronisierung und eigener lokaler/
remote Branchabbau bestätigt. Unmittelbar folgt auf `codex/sql2025-ai-ann-parser-decision`
die reine Vorbereitung eines [einzelnen Parserdiagnoseentscheids](SQL_SERVER_2025_AI_ANN_PARSER_DECISION.md).
PENDING_USER_DECISION, keine neue Korrekturquelle oder SQL-Runtime: ein Kandidat/ein
Container, maximal zwei feste PARSEONLY-Aufrufe, kein Indexbuild/Search/Performance-
oder anschließender Implementierungsclaim. Drei frisch geprüfte Primärquellen sind
im Quellenregister ergänzt. SRC-106 dokumentiert den ignorierten MAXDOP-Parameter;
ein wirksamer freigegebener DOP-1-Pfad ist deshalb vor tatsächlichem Build/Search
zusätzlich erforderlich. Kein empirischer DOP-Befund und kein Konfigurationsworkaround.
Ein Owner und enger Entscheidungsreview allein der neuen Diagnose-/Effektgrenzen;
keine Wiederholung der unveränderten Runtime- oder Recoveryanalyse. Head-/Main-
Integration und eigener Cleanup dieses Entscheidungspakets sind erforderlich;
danach bleibt ANN bis zum ausdrücklichen neuen Budgetentscheid angehalten.
Der enge unabhängige Review des Diagnoseentscheids fand keine P1/P2 und schloss
das reine Entwurfs-Quellengate. Keine Ausführungsgenehmigung oder Runtime dadurch.
Die betroffene Datenschutz-/Metadatenprüfung und git diff --check bestanden.
TSK-012 bleibt insgesamt offen.
PR 157 ist mit acht Headprüfungen auf `1a85d7062f8d772e560b2eaa6f4a78dba9b053f4`
und sechs Main-Workflows auf `2f3cf94884bb4dcd0571ee8d55bfdcbbafd35c3a` integriert.
Tree `ce4ac56af199011a560b412ce07474ff0931c48e`, Synchronisierung und eigener lokaler/
remote Branchabbau bestätigt. Der Benutzer hat anschließend ausdrücklich
„Ja, Parserdiagnose freigeben (empfohlen)“ geantwortet. Auf
`codex/sql2025-ai-ann-parser-diagnosis` wird allein dieser neue Umfang umgesetzt:
ein privater Diagnosekandidat/ein Container, höchstens zwei unveränderte PARSEONLY-
Aufrufe, keine Korrekturwelle und kein anschließender Indexbuild/Search.
Die unveränderten hashgebundenen Setup-/Recovery-/Cleanuphelper wurden wiederverwendet.
Drei betroffene lokale Parser-/Snapshot-Gegenfixtures bestanden; der enge
unabhängige Review des neuen ausführbaren Deltas schloss zwei P2 vor SQL
(begrenzter JSON-Skalar und strikte 343-/Clientfehlerauswertung). Beide Reviews
übersahen die tatsächliche lokale sqlcmd-Inkompatibilität von `-h -1 -y 0`.
Der einzige Lauf ist [FAIL vor Setup](SQL_SERVER_2025_AI_ANN_PARSER_REVIEW.md):
300-Sekunden-Readinessbudget erschöpft, einzelne Readinessfehlerausgaben unbekannt;
SQL-Recovery und separate SQL-Abwesenheit tatsächlich FAIL wegen Clientoptionen.
Keine persistente Baseline oder Previewattestierung; beide PARSEONLY-Aufrufe
unausgeführt. Gebundener eigener Containerabbau und separate Abwesenheit bestanden,
Cleanup 11,989 Sekunden. Kein RESTORED-/DROP-/SQL-Abwesenheits-PASS behaupten.
Eine geänderte lokale Argumentkontrolle ohne SQL-Text/neuen Container gegen
ungültigen Loopbackport 0 erreichte ohne `-h` die erwartete Verbindungsablehnung;
keine SQL-/JSON-Runtimeabnahme. Ausgeführte private Quellen bleiben unverändert.
Ein neuer [enger Clientkorrekturentscheid](SQL_SERVER_2025_AI_ANN_PARSER_CLIENT_DECISION.md)
ist PENDING_USER_DECISION: ein zusätzlicher Kandidat/ein Container, keine
Korrekturwelle, unveränderte Parser-/Effekt-/Cleanupgrenzen. Der enge unabhängige
Review des Befunds und neuen Entwurfs fand keine P1/P2; keine Runtime dadurch.
Aktuelle Head-/Main-Gates, Integration und eigener Branchcleanup folgen;
keine neue Ausführungsfreigabe. Die alten FAIL-Checkpoints und weiteren
Build-/DOP-Gates bleiben bestehen. Der Heartbeat setzt keine dieser Grenzen zurück.
PR 158 ist mit sieben Headprüfungen auf `f119f8f172ba4107e34aabd38bb13e8d212021c1`
und fünf Main-Workflows auf `00b546416eb6e7250f10f42bff1c724dab43c4c6` integriert.
Tree `b78cbc4cd7e02c748d7ddd5374d31b2210ee7140`, Synchronisierung und eigener lokaler/
remote Branchabbau bestätigt. Anschließend bestätigte der Benutzer ausdrücklich
„Ja, Clientkorrekturpaket freigeben (empfohlen)“. Auf
`codex/sql2025-ai-ann-parser-client` wird genau dessen neuer Kandidat vorbereitet:
`-y 0 -w 65535` ohne `-h`, Optionsgegenfixture vor Containerstart und erhaltene
begrenzte redigierte Readinessfehler, sofortiger Stopp unbekannter Meldungen.
Die beiden neuen betroffenen Client-/Readinessfixtures bestanden; der enge
unabhängige Deltareview schloss gemischte Fehlerausgaben als P2 vor Runtime.
Der tatsächlich ausgeführte einzige neue Kandidat ist
[FAIL vor Setup](SQL_SERVER_2025_AI_ANN_PARSER_CLIENT_REVIEW.md): seine erhaltene
erste ODBC-TCP-Readinessmeldung enthielt eine zusätzliche Punktzeile und wurde
von der überengen Zeilenauswertung als unbekannt abgelehnt. 0 Parseraufrufe,
keine Baseline oder Previewattestierung. Tatsächlicher neuer Recoveryclient
meldete ALREADY_ABSENT, separater SQL-Client bestätigte DB-Abwesenheit; eigene
gebundene Containerentfernung und separate Abwesenheit bestanden, 13,887 Sekunden.
Die korrigierten Clientoptionen sind damit SQL-verbindungsfähig; keine Snapshot-,
Parser- oder ANN-Abnahme. Keine Änderung der ausgeführten historischen Quellen.
Der [Readinessentscheid](SQL_SERVER_2025_AI_ANN_READINESS_DECISION.md) bereitet
ausschließlich einen neuen Kandidaten/Container ohne Korrekturwelle und einen
präziseren Auswerter dieser tatsächlich erhaltenen Meldungsstruktur vor:
PENDING_USER_DECISION, keine neue ausführbare Quelle oder Runtime. Sein enger
Befund-/Entwurfsreview fand keine P1/P2; das spätere Ausführungsgate bleibt offen.
Aktuelle Head-/Main-Gates, Integration und eigener Branchcleanup folgen.
Der Heartbeat wiederholt diesen FAIL nicht automatisch.
PR 159 ist mit sieben Headprüfungen auf `80d07bc0c5a981851485c2ba182ee437e8a94ba9`
und fünf Main-Workflows auf `f0841b3652e23a3378bf535fe68caae53f3baea3` integriert.
Tree `8e5f0b43587a16284eca73e90ed686dd4d8e09b2`, Synchronisierung und eigener lokaler/
remote Branchabbau bestätigt. Der Benutzer bestätigte anschließend ausdrücklich
„Ja, Readinesspaket freigeben (empfohlen)“. Auf `codex/sql2025-ai-ann-readiness`
wird genau dessen neuer Kandidat vorbereitet: nur der Readinessmeldungsblock-
auswerter für die erhaltene TCP-/Punktzeilenstruktur wird geändert. Alle anderen
Client-/Parser-/Snapshot-/Helper-/Effekt-/Cleanupgrenzen bleiben unverändert.
Drei betroffene Readiness-/Optionsfixtures bestanden vor Containerstart;
der enge tatsächliche Delta-Quellenreview fand keine P1/P2. Der einzige neue
Kandidat bestand als [Parser-/Previewdiagnose](SQL_SERVER_2025_AI_ANN_PARSER_PASS_REVIEW.md):
tatsächliche Baseline 0, feste PARSEONLY-Probe mit Fehler 343 und unverändertem
erfasstem Zustand; nach abgeschlossenem Enable und frischem attestiertem DB-Client
Preview 1, derselbe Parsertext mit Code 0/leerer Ausgabe akzeptiert. Sieben volle
Snapshots mit je 107 Host-/41 DB-scoped-Konfigurationsrows verglichen, eigene
Fixture/Vectorindexabwesenheit vor/nach beiden Aufrufen. Ausgewählte sys.databases-
Optionsfelder erfasst, keine allgemeine Metadatenqualifikation behaupten.
Tatsächlicher RESTORED_0/DROP_CONFIRMED, separater neuer SQL-DB-Abwesenheitsclient,
gebundener eigener Containerabbau und separate Abwesenheit bestanden; Cleanup
12,715 Sekunden. Keine Indexgeneration, Suche, Recall-/Plan-/Performanceevidenz.
Historische 343-Batch-/Sessionursache nicht isoliert kausal bewiesen; alte FAILs
und Budgets bleiben erhalten. Ausgeführte Quellen unverändert, keine Wiederholung.
Unmittelbar wird ein [konkreter ANN-Build-/Suchentscheid](SQL_SERVER_2025_AI_ANN_BUILD_DECISION.md)
vorbereitet: zwei Kandidaten/vier eigene serielle Container, höchstens 1000
VECTOR(3)-Rows und zusätzlich nur eigener DB-scoped-MAXDOP-Set/Restore auf tatsächlich
gespeicherte 0. Frische Preview-/MAXDOP-Attestierung vor Build, Restore beider Werte
mit separatem neuem Attestierungs-/Dropclient. Angepasstes Cleanupcallbudget weiterhin
50 Sekunden/absolute 60; keine Host- oder zusätzlichen Providerwirkungen.
SRC-108 begründet den dokumentierten Konfigurationspfad, kein empirischer Worker-/
DOP-Befund. PENDING_USER_DECISION; enger Entwurfsreview fand keine P1/P2.
Aktuelle Head-/Main-Gates, Integration und eigener Branchcleanup folgen.
Kein automatischer ANN-Folgelauf oder neues Ausführungsgate dadurch.
PR 160 ist mit acht Headprüfungen auf `3030dc8ba5e00d7a057de0a09367e0ae4915993d`
und sechs Main-Workflows auf `443697b350c51aa153dff8a02f2d325fe78a734a` integriert.
Tree `252237a6024b22ba9bb352a7990a4d9f9381d4b0`, Synchronisierung und eigener
lokaler/remote Branchabbau bestätigt. Anschließend bestätigte der Benutzer
ausdrücklich „Ja, ANN-Build-/Suchpaket freigeben (empfohlen)“.
Auf `codex/sql2025-ai-ann-build` wird der erste neue private Kandidat vorbereitet:
beide persistente Baselines, separater Set/Attestierungsablauf und beide tatsächliche
Restores mit neuem Attestierungs-/Dropclient. Das neue Budget umfasst höchstens
zwei Kandidaten/vier serielle eigene Container; keine Wiederaufnahme alter Budgets.
Der unabhängige tatsächliche Delta-Quellenreview bleibt vor SQL erforderlich.
Dieser erforderliche erste Quellenreview und der gezielte QUOTED_IDENTIFIER-
Deltareview fanden keine P1/P2. Fünf betroffene lokale Tests bestanden.
Beide Kandidaten wurden auf je einem neuen eigenen Container ausgeführt:
[Build-/Such-FAIL](SQL_SERVER_2025_AI_ANN_BUILD_REVIEW.md). Erster Kandidat:
1934 wegen QUOTED_IDENTIFIER, kein Index-/Such-PASS. Zweiter Kandidat: tatsächliche
Sessionoption 1, eigener Index erstellt und Identitätscount 1, dann 51003 am
Generationsguard vor Metadatenausgabe und Search. Konkrete Generation/Typ-/Metric-
Rohwerte bleiben UNKNOWN; kein automatischer Generation-3-Schluss.
Beide tatsächlichen Restores 0/0, getrennte neue Attestierungs-/Dropclients,
separate SQL-DB-/Containerabwesenheit bestanden; Cleanup 12,444/12,397 Sekunden.
Zwei Kandidaten verbraucht, zwei ungenutzte Containerplätze erlauben keinen dritten.
Ausgeführte Quellen unverändert; kein neuer ANN-Lauf. Der konkrete
[einzelne Metadatenentscheid](SQL_SERVER_2025_AI_ANN_METADATA_DECISION.md) bereitet
einen neuen eigenen Kandidaten/Container ohne Search bei unveränderten lokalen
Effekten vor und bleibt PENDING_USER_DECISION. Aktuelle Head-/Main-Gates und
eigener Branchcleanup dieses begrenzten Befunds folgen vor der Benutzerfrage.
PR 161 ist mit acht Headprüfungen auf `cc62fd079ce6773880395b5b08ee1c5fe5d6f02b`
und sechs Main-Workflows auf `429d587d4b5b34bf36467c0b391afdb741b533a6` integriert.
Tree `966377ed486a6c7e09d57f9709c888f6e30d0879`, Synchronisierung und eigener
lokaler/remote Branchabbau bestätigt. Der Benutzer erteilte anschließend ausdrücklich
die Metadatenfreigabe und „auch alle weiteren Freigaben zur Durchführung dieser
Entwicklungswelle“. Diese zusätzliche Autorisierung erlaubt weitere notwendige
lokale ANN-Schritte der Welle ohne wiederholte Budgetfreigabefragen; historische
FAILs und verbrauchte Budgets bleiben erhalten. Jeder neue zusammenhängende Umfang
erhält weiterhin eine endliche Ausführungsgrenze, betroffene Tests, erforderliche
unabhängige Reviews und eigenen Cleanup. Zunächst genau die einzelne Metadatendiagnose
ohne Search auf `codex/sql2025-ai-ann-metadata`, Basis `429d587d4b5b34bf36467c0b391afdb741b533a6`.
Keine zusätzliche Host-/Cloud-/ONNX-Wirkung aus diesem lokalen Paket ableiten.
Der enge tatsächliche Metadaten-Quellenreview fand keine P1/P2, fünf betroffene
lokale Tests bestanden. Der einzige neue Kandidat bestand als
[vollständige Metadatenaufnahme](SQL_SERVER_2025_AI_ANN_METADATA_REVIEW.md):
eigener Index Typ 8/VECTOR, DiskANN/COSINE, gültige Buildparameter mit StartId/L/M/R,
Version-Schlüssel fehlt tatsächlich, beide Versionsableitungen NULL. Keine Generation
erraten; keine Search-/Recall-/Indexnutzungsevidenz. 1000 volle Quellenrows,
24 Marker-/neun Baseline-/drei Quellgegenproben und vier vollständige Snapshots
mit je 107 Host-/41 DB-scoped-Konfigurationsrows bestanden. Eigener Indexdrop,
tatsächliche Restores 0/0, neuer Attest/Dropclient, separater SQL-DB-Abwesenheitsclient
und gebundener Containerabbau/zusätzliche Abwesenheit bestanden; Cleanup 12,439 Sekunden.
Unmittelbar wird gemäß zusätzlicher ausdrücklicher Benutzerautorisierung ein
[begrenzter Legacy-Signaturversuch](SQL_SERVER_2025_AI_ANN_LEGACY_TRIAL_DECISION.md)
vorbereitet: eigener neuer Diagnoseumfang, Generation UNKNOWN bleibt erhalten,
eine feste dokumentierte TOP_N-Signatur, kein alternativer Syntaxfallback oder
volle IDX-011-Abnahme. Quellenreview und Integration der Metadatendiagnose
bleiben vor dessen SQL-Start erforderlich. Historische FAILs/Budgets unverändert.
PR 162 ist mit sieben erfolgreichen Headprüfungen auf
`b838f121e5e555d1d535991b2406452bb7ee92fb` gegen Basis
`429d587d4b5b34bf36467c0b391afdb741b533a6` integriert. Alle fünf ausgewählten
Main-Workflows auf `99657fa2c3bd29f17ee5139b96439f3b23a28e15` bestanden;
Tree-Identität `2c3b2d9491cb515fd024b699f524d0b3e6a1ef74`, Synchronisierung und
eigener lokaler/remote Branchabbau bestätigt. Unmittelbar beginnt der autorisierte
Legacy-Diagnoseumfang auf `codex/sql2025-ai-ann-legacy` an dieser Basis.
Der erforderliche Methoden-/Quellenreview des unveränderten ersten privaten
Kandidaten und seine fünf lokalen Tests sind abgeschlossen. Höchstens zwei neue
Kandidaten/vier serielle eigene Container, höchstens zwei vollständige Lifecycles
je positivem stabilem Kandidaten; keine Generation oder Indexnutzung voraussetzen.
Der erste Legacy-Kandidat stoppte am Texttyp-/Metricguard vor Search (51003),
bei ausgegebener vollständiger DiskANN/COSINE-Metadatenrow. Tatsächliche Speichertypen
noch unbekannt; beide Restores 0/0, neue Attestierung und separate DB-/Containerabwesenheit
bestanden, Cleanup 12,297 Sekunden. Seine ausgeführten Quellen bleiben unverändert.
Der zweite erlaubte Kandidat erfasst Textspeichertypen/-längen und vergleicht
die Werte ohne Case-/Whitespaceänderung in einheitlicher Unicodeform; zehn feste
Wertnegative und eine varchar-/nvarchar-Positive sind zusätzlich vor Search gebunden.
Zwei lokale Generator-Testfehler durch implizite Windows-Decodierung vor SQL wurden
im vorbereiteten Kandidaten korrigiert; der anschließende Fünf-Test-Lauf bestand.
Der enge unabhängige Review des tatsächlichen Deltas fand keine P1/P2; Quellengate
vor SQL geschlossen. Der zweite Kandidat bestand beide vorgesehenen vollständigen
[Legacy-Ergebnislifecycles](SQL_SERVER_2025_AI_ANN_LEGACY_TRIAL_REVIEW.md):
tatsächliche Texttypen nvarchar 14/12 Bytes, feste TOP_N-Signatur lieferte je fünf
distanzgeprüfte Rows und 5/5 Schnittmenge mit Exact-Oracle. Je 24 Marker-/neun
Baseline-/drei Ergebnis-/drei Quell-/zehn Textwertgegenproben und vier vollständige
107-Host-/41-DB-scoped-Snapshots bestanden. Voller Source-/Metadatenvergleich,
eigener Indexdrop, beide tatsächlichen Restores 0/0, neue Attestierung und separate
DB-/Containerabwesenheit bestanden; Cleanup 12,383/12,710 Sekunden. Generation
UNKNOWN und Indexnutzung UNPROVEN; kein Plan-/Performance-/Demo-PASS. Zwei neue
Kandidaten/drei Container verbraucht, Umfang regulär abgeschlossen; Integration folgt.
Unmittelbarer Folgeschnitt gemäß Wellenautorisierung ist die
[begrenzte tatsächliche Planausgabe](SQL_SERVER_2025_AI_ANN_PLAN_DECISION.md):
maximal zwei neue Kandidaten/zwei Container, eigener enger Plan-/Clientreview und
betroffene Tests vor SQL, keine DML-/Cloud-/ONNX-/Hostwirkung.
PR 163 ist mit sieben erfolgreichen Headprüfungen auf
`03c04a77644774df497e5514bcfe0632002d628e` gegen Basis
`99657fa2c3bd29f17ee5139b96439f3b23a28e15` integriert. Alle fünf ausgewählten
Main-Workflows auf `d4ace6614ae500329e05160e0dd4f7ad16c9b8e7` bestanden;
Tree-Identität `ff755ae9155f254508ccc8b034b7bd344eae9c1d`, main synchronisiert,
eigener Branch lokal/remote entfernt. Unmittelbar beginnt die begrenzte Plandiagnose
auf `codex/sql2025-ai-ann-plan` an dieser Basis. Fünf bestehende lokale Grenztests
und sechs neue Plan-/Manipulationstests bestanden. Der enge unabhängige Review des
tatsächlichen XML-/Statement-/Runtime-/Indexbindings fand keine P1/P2;
Quellengate vor SQL geschlossen. Der erste einzelne Plankandidat bestand die
[tatsächliche Planausgabe](SQL_SERVER_2025_AI_ANN_PLAN_REVIEW.md): vollständiges
gebundenes Actual-XML (Extensible Markup Language; Format zur strukturierten Darstellung von Daten), eigener Vector Index Seek/DiskANN mit fünf tatsächlichen
Rows, daneben Nested Loops und Clustered Index Seek. Indexnutzung für diesen
festen ungefilterten Suchaufruf beobachtet; Generation UNKNOWN. Ergebnis-/Source-/
Metadaten-/Konfigurationskontrollen bestanden, beide tatsächlichen Restores 0/0,
neue Attestierung und separate SQL-/Containerabwesenheit bestanden; Cleanup
12,583 Sekunden. Ein Kandidat/Container verbraucht, Umfang regulär abgeschlossen;
Integration folgt. Unmittelbarer Folgeschnitt gemäß Wellenautorisierung ist die
[begrenzte Filter-/Ergebnisdiagnose](SQL_SERVER_2025_AI_ANN_FILTER_DECISION.md)
mit drei vorab festen Id-Fenstern und gebundenem Exact-Oracle; eigenes Quellen-/
Testgate vor SQL. Kein gefilterter Indexnutzungs-/Performance-/voller Demo-PASS.
PR 164 ist mit sieben erfolgreichen Headprüfungen auf
`eae8ebd1a1813366fe83154041e0757b7291d06d` gegen Basis
`d4ace6614ae500329e05160e0dd4f7ad16c9b8e7` integriert. Alle fünf ausgewählten
Main-Workflows auf `b35f147632ceba3a8b433ec2ac062bfe70205301` bestanden;
Tree-Identität `7997a7995efad05d05cb88f4c9085272040a0fdf`, main synchronisiert,
eigener Branch lokal/remote entfernt. Unmittelbar beginnt die Filterdiagnose
auf `codex/sql2025-ai-ann-filter` an dieser Basis. Fünf bestehende Grenztests
und sechs neue Filter-/Coverage-/Recall-/Manipulationstests bestanden. Enger
unabhängiger Review des tatsächlichen Filter-/Oracle-/Clientdeltas fand keine P1/P2;
Quellengate vor SQL geschlossen. Ein stabiler Kandidat bestand beide vollständigen
[Filterlifecycles](SQL_SERVER_2025_AI_ANN_FILTER_REVIEW.md): breite Fenster 1–1000/
1–100 je fünf ANN-/Exact-Rows und Recall@5 1; enges Fenster 501–510 null ANN- gegen
fünf Exact-Rows, Recall@5 0 und sichtbares ROWS_BELOW_K. Vier neue Filtergegenproben
und alle bisherigen Source-/Marker-/Baseline-/Metadaten-/Konfigurationskontrollen
bestanden. Beide tatsächlichen Restores 0/0, neue Attestierung und separate SQL-/
Containerabwesenheit bestanden; Cleanup 12,354/12,552 Sekunden. Generation UNKNOWN,
gefilterte Indexnutzung UNPROVEN, kein Performance-/voller Demo-PASS. Ein Kandidat/
zwei Container, Umfang regulär abgeschlossen; Integration folgt.

Unmittelbarer Folgeschnitt aus der erteilten lokalen Wellenautorisierung ist eine
begrenzte sessionbezogene Messdiagnose am ungefilterten festen Query/Korpus:
maximal zwei neue Kandidaten/vier serielle eigene Container und zwei Lifecycles
je positivem stabilem Kandidaten. Beide Pfade geben dieselben fünf Id-/Distanz-
Spalten zurück; identische temporäre Ergebnisspeicherung. Je Pfad ein ausgeschlossener
Warm-up und fünf gemessene Batches mit je zehn Suchstatements; alternierende
Paarreihenfolge, keine Cacheleerung. Pro Lifecycle höchstens 61 Legacy-Suchaufrufe
und 61 Exact-Queries einschließlich bisherigem Query-/Oraclevorlauf. Alle Rows
und Distanz-/Recallgrenzen weiterhin tatsächlich prüfen. Session-CPU-/Read-/
Logical-Read-/Write-Deltas und UTC-Elapsed erfassen, gleiche Session/Nicht-NULL/
Nichtnegativität prüfen; Median und Min/Max aus fünf Batches je Pfad. Quantisierung,
Mess-/temporärer Speicheraufwand und ausgeschlossener Warm-up bleiben sichtbar;
kein festes Speedupversprechen, optionale Waits nicht erhoben. Generation UNKNOWN,
neue Indexnutzung UNPROVEN ohne neue Planausgabe. Unveränderte 1000-Row-/Image-/
Build-/Ressourcen-/Konfigurations-/Marker-/300-Sekunden-/60-Sekunden-Cleanupgrenzen;
keine DML-/Stale-/Host-/Cloud-/ONNX-Wirkung. Betroffene Tests und enger erforderlicher
Methoden-/Quellenreview vor SQL; Retry nur mit geändertem Input/neuer Evidenz.
Nach zwei ungelösten Kandidaten Befund integrieren, kein stilles Budgetreset.
Aktuelle Head-/Main-Gates, PR, Synchronisierung und eigener Cleanup schließen
diesen eigenen Messbefund ab. Dies ist keine vollständige FWK-/TP-PERF-/Demoabnahme.
PR 165 ist mit sieben erfolgreichen Headprüfungen auf
`8e062ec7486b81d35ee2eec679f593d274f50a8b` gegen Basis
`b35f147632ceba3a8b433ec2ac062bfe70205301` integriert. Alle fünf ausgewählten
Main-Workflows auf `777c56210e08114f9d180ae907075a50544a4be0` bestanden;
Tree-Identität `8bb954836a5d8b90e8e066067a9af59d6f67cf23`, main synchronisiert,
eigener Branch lokal/remote entfernt. Unmittelbar beginnt der Messfolgeschnitt
auf `codex/sql2025-ai-ann-measure` an dieser Basis. Fünf bestehende Grenztests und
zunächst fünf neue Mess-/Coverage-/Manipulationstests bestanden. Der unabhängige
Review fand einen P2: Minimum der Batch-Recallmittelwerte irreführend als Queryminimum
benannt. Vor SQL im unbenutzten Kandidaten auf min_batch_mean_recall_at_5 korrigiert;
eine tatsächliche 49/50-Fixture bindet 0,98 ohne Queryminimumclaim. Sechs betroffene
Mess-Gegenproben bestanden; der enge Nachreview schloss den P2 vor SQL.
Messkandidat 01 wurde einmal unverändert ausgeführt: technische Capture-/Ergebnis-/
Cleanupkontrollen PASS, sämtliche Session-CPU-/Read-/Logical-Read-/Write-Deltas null.
EXACT-Elapsed-Median null; keine Performancequalifikation: WARN ungeeignetes oder
inaktives Zählerfenster und Zeitquantisierung. Der ausgeführte Kandidat wird nicht
verändert oder ohne neue Evidenz wiederholt. Seine fünf gemessenen Batches je Pfad
enthielten tatsächlich je 50 Treffer/50 mögliche; Restore beider Baselines 0/0 und
unabhängige DB-/Containerabwesenheit bestanden in 12,385 Sekunden.
Der zweite bereits budgetierte Kandidat ändert ausschließlich die Zählerquelle auf
sys.dm_exec_requests (LIVE_REQUEST), gebunden an dieselbe Session, Request-ID,
Startzeit, Connection-ID und eigene DB-ID vor/nach jedem Batch. Keine fehlenden/nullen
oder negativen Zähler und keine wechselnde Identität; mindestens ein positives
Logical-Read-Delta je Pfad nach Warm-up-Ausschluss verlangt. Das belegt ein aktives
Fenster, keine vollständige Worker-IO: parallele Row-Mode-Requests haben laut
SRC-110 eine Koordinatorgrenze; tatsächlicher Such-DOP (Degree of Parallelism; Parallelitätsgrad einer Ausführung) bleibt UNPROVEN und
preemptive Zeit nicht erfasst. Suchzahl, Reihenfolge, Ergebnis-/Qualitätskontrollen,
Effekte und endliches Kandidaten-/Containerbudget bleiben unverändert. Betroffene
13 betroffene Gegenproben bestanden; enger unabhängiger Methoden-/Quellenreview
schloss vor SQL ohne offene P1/P2. Kandidat 02 bestand zwei unveränderte Lifecycles:
aktive CPU-/Logical-Read-Deltas, alle gemessenen Batches 50 Rows/50 Oracle-Treffer,
EXACT-Zeitnullwerte weiterhin sichtbar. Kein ANN-Vorteil am kleinen festen Korpus
belegt; keine Speedupratio aus quantisierten Kleinstmessungen. Vollständige Source-/
Metadaten-/Konfigurationskontrollen, Restores 0/0, neue Attestierung und separate
DB-/Containerabwesenheit bestanden; Cleanup 12,386/12,299 Sekunden. Zwei Kandidaten/
drei Container, Messscope abgeschlossen. Der [Messnachweis](SQL_SERVER_2025_AI_ANN_MEASUREMENT_REVIEW.md)
bewahrt Kandidat01-WARN und begrenzte Requestmetrik. PR 166 ist mit acht erfolgreichen
Headprüfungen auf `0f02c1422553d14bb143efda5b7e2a21b0177c10` gegen Basis
`777c56210e08114f9d180ae907075a50544a4be0` integriert. Alle sechs ausgewählten
Main-Workflows auf `b7fd69ce49e50a4f489b38640464e520f0329087` bestanden;
Tree-Identität `0050622ffdc09c9070bbceb73aad19ae98d0ccff`, main synchronisiert,
eigener Branch lokal/remote entfernt. Der neue DML-Diagnosebranch beginnt an
dieser Basis: `codex/sql2025-ai-ann-dml`.

Unmittelbarer nächster zulässiger eigener Schnitt nach dieser Integration:
ein fester gültiger UPDATE auf der eigenen 1000-Row-VECTOR(3)-Quelle bei aktivem
eigenem Vectorindex, innerhalb einer ausschließlich zurückgerollten Transaktion.
Höchstens zwei neue Kandidaten/vier serielle eigene Container, zwei Lifecycles
je stabilem positiven Kandidaten; kein INSERT/DELETE/MERGE und keine Staleoption.
Tatsächlichen SQL-Fehler oder Erfolg aufnehmen, keine erwartete Fehlernummer erfinden;
Erfolg ebenfalls immer zurückrollen. Vollständigen Sourcezustand nach Rollback
mit der vor DML (Data Manipulation Language; Anweisungen zum Lesen oder Ändern von Daten) gesicherten Quelle vergleichen, Own-Indexmetadaten weiter binden.
Keine Freshness-/DML-Freigabe aus einer technischen Diagnose ableiten. Alle bisherigen
Image-/Versions-/Ressourcen-/Konfigurations-/Marker-/Zeit-/Restore-/Cleanupgrenzen
gelten; betroffene Tests und enger tatsächlicher Quellen-/Methodenreview vor SQL.
Keine Host-/Cloud-/ONNX-Wirkung. Kein Reset früherer Budgets; eigener endlicher
DML-Diagnosescope aus der ausdrücklich erteilten weiteren lokalen Wellenfreigabe.
Vorprüfung der tatsächlichen vollständigen 41 DB-Konfigurationsrows des gebundenen
Builds zeigt keine ALLOW_STALE_VECTOR_INDEX-Row. Der Diagnoseguard verlangt dieses
ABSENT-Profil; keine erfundene OFF-Attestierung und kein Set. Ein neues privates
Kandidat01-Delta begrenzt genau ein parameterisiertes gültiges UPDATE auf Id 23,
vorher tatsächlich vorhandenes und abweichendes VECTOR(3)-Ziel. Nach Erfolg wird
die tatsächliche eine Row und Zielbyteform innerhalb der Transaktion gesichert;
SQL-Rejection und Fehlernummer/-State/-Text werden ohne Read-only-Klassifikation
aufgenommen. Immer Rollback und vollständiger beidseitiger Sourcebytevergleich.
Elf betroffene Grenz-/Diagnosegegenproben bestanden; erforderlicher enger Methoden-/
Quellenreview schloss vor SQL ohne offene P1/P2, kein vollständiger erneut unveränderter
Safetyreview. Kandidat 01 tatsächlich FAIL: gültiges UPDATE mit SQL 42231/State 1
verweigert, vollständige Source-/Metadaten-/Konfigurationskontrollen bestanden;
JSON meldete RolledBack=false trotz zuvor bestandenem Transaktionsguard. Dies
ist widersprüchliche Transaktionsevidenz, kein technischer DML-Diagnose-PASS.
Restores 0/0, neue Attestierung und separate DB-/Containerabwesenheit bestanden
in 12,253 Sekunden; Prozesscode 1, ausgeführte Bytes bleiben unverändert.
Der zweite bereits budgetierte Kandidat sichert tatsächlichen @@TRANCOUNT und
XACT_STATE() unmittelbar nach Rollback in Variablen, prüft beide null und gibt
diese Zahlen sowie das daraus abgeleitete RolledBack aus, statt erneut innerhalb
der JSON-SELECT auszuwerten. Parser verlangt beide tatsächlichen Zahlen null;
NULL, negativ, offen oder Boolean werden verworfen. Sieben betroffene Tests und
enger Befundnachreview schlossen vor SQL ohne offene P1/P2. Zwei unveränderte
Lifecycles bestanden: tatsächliche UPDATE-Verweigerung 42231/State 1,
TransactionCount=0/TransactionState=0, Sourcebytes/Indexmetadaten unverändert.
Vollständige Kontrollen, Restores 0/0, neue Attestierung und separate DB-/
Containerabwesenheit bestanden; Cleanup 12,391/12,323 Sekunden, Prozesscode 0.
Zwei Kandidaten/drei Container, Scope abgeschlossen; früherer FAIL bleibt erhalten.
Der [DML-Diagnosenachweis](SQL_SERVER_2025_AI_ANN_DML_REVIEW.md) begrenzt diesen
konkreten UPDATE-Befund: Freshness NOT_TESTED, allgemeine DML-Unterstützung UNPROVEN,
Generation UNKNOWN. PR 167 ist mit sieben erfolgreichen Headprüfungen auf
`1f0a81c8787ca666858236ee3e74f1ba51287096` gegen Basis
`b7fd69ce49e50a4f489b38640464e520f0329087` integriert. Alle fünf ausgewählten
Main-Workflows auf `3fea838a999c4576cc53a706567624aa280f0c3b` bestanden;
Tree-Identität `3118c61658aa883d48e11f437b29f39c6ae53370`, main synchronisiert,
eigener Branch lokal/remote entfernt. Methodenbranch `codex/sql2025-ai-ann-profile`
beginnt unmittelbar an dieser Basis.

Unmittelbarer nächster zulässiger Schritt nach Integration ist die enge fachliche
Methodenentscheidung für das beobachtete fehlende numerische Versionsfeld:
prüfen, ob IDX-011/IDX-012 für ausschließlich den festen Build 17.0.5005.3 ein
empirisch gebundenes Legacy-DiskANN/COSINE-/TOP_N-/UPDATE-Rejection-Profil mit
Generation UNKNOWN/WARN akzeptieren können. Kein Ersetzen unbekannter Werte durch
1/2/3, kein Azure-/anderer Buildtransfer und kein Wegfall von tatsächlicher
Plan-/Index-/Ergebnis-/Qualitäts-/Mess-/Versions-/Restore-/Cleanupabnahme.
Ein zusammenhängender Methodenentwurf und ein erforderlicher unabhängiger fachlicher
Review, höchstens eine kohärente Korrektur; keine neue SQL-/Provider-/Hostwirkung.
Bei fachlicher Annahme eigene stabile Entscheidung via zentraler Registry und
scopebezogene Aktualisierung der beiden Demoentwürfe; keine globale Framework-
Lockerung. Die Nutzerfreigabe umfasst notwendige weitere lokale Schritte dieser Welle.
Der konkrete [Profilentwurf](SQL_SERVER_2025_AI_ANN_PROFILE_DECISION.md) behält
Generation UNKNOWN/WARN und alle anderen Abnahmegates, keine neue Runtime.
DEC-074 ist vom zentralen Semantiktool bei leerer PR-Reservierungslage abgeleitet
und mit PR168 final integriert. Der erforderliche enge fachliche
Review schloss vor Registrierung ohne offene P1/P2: funktionale Qualifikation
benötigt keine erfundene numerische Generation, alle anderen Gates bleiben Pflicht.
Die Registry enthält den neuen vollständigen UUID-Datensatz; 265 Artefakte bestanden
zentrale Semantik-/projektbezogene Kennungsvalidierung. DECISIONS, beide Demoentwürfe
und der Workstreamplan wenden ausschließlich den begrenzten DEC-074-Pfad an.
Keine neue lokale Runtime und keine unveränderten Diagnosewiederholungen.
PR168-Head 26dee8d6b3d3fb5633e220a15cf62b27d91948ef gegen Base
3fea838a999c4576cc53a706567624aa280f0c3b bestand alle 42 gewählten Checks.
Squash 40159404acb1b20f0f69072f9e52664f2593bd86 bestand alle acht gewählten
Main-Workflows einschließlich der konservativ ausgewählten Legacy-Matrizen.
Vollständiger Tree e90913ccb9b56924b23fc51aba11327963f57301 wurde unabhängig
als identisch bestätigt; lokales main per Fast-forward synchronisiert und eigener
Arbeitsbranch lokal/remote entfernt. Keine Abnahme der pausierten Workstreams
oder der öffentlichen ANN-Demos aus diesen Integrationsprüfungen.

Unmittelbarer nächster Implementierungsschnitt nach Profilintegration ist die
öffentliche IDX-011-Demo mit dokumentiertem DEC-074-Profil, vollständigem Ergebnis-/
Qualitäts-/Filter-/Plan-/Benchmark-/Versions-/Recoveryvertrag. Höchstens zwei
kohärente Kandidaten und 16 eigene serielle Testcontainer insgesamt: je positivem
stabilem Kandidaten zweimal 2025-Happy-Path, je zweimal 2019/2022-SKIP_VERSION vor
Setup und zwei eigene 2025-Abbruch-/Recoveryproben nach Setup bzw. nach Indexbau.
Nur nachweislich verfügbare eigene lokale Images, keine Downloads/Hoständerungen.
Unveränderte 1000-Row-VECTOR(3)/K=5-/4CPU-/6GiB-/DB-Preview-/MAXDOP-/300-Sekunden-/
60-Sekunden-Cleanupgrenzen; Marker, tatsächliche duale Baselines/Restores und
separate DB-/Containerabwesenheit bleiben Pflicht. Benchmark vor SQL konkret
einfrieren: je Pfad fünf ausgeschlossene Warm-up-Requests und drei Reihenfolgeblöcke
AB/BA/AA, identische Ergebnisablage, keine Cacheleerung; fixe Batchgröße im konkreten
Implementierungsvertrag begrenzen. Active-Request- und Zeit-/Workergrenzen sichtbar,
keine unbewiesene Speedupratio oder generische Indexnutzung. Betroffene lokale Tests,
erforderlicher unabhängiger tatsächlicher Quellen-/Methodenreview und aktuelle Head-/
Main-Gates, Synchronisierung sowie eigener Cleanup schließen den Schnitt vollständig.
IDX-012-DML/Freshness und Provider-/Cloud-/ONNX-Gates bleiben eigene Schritte.

Der erste begrenzte Offline-Teil des öffentlichen IDX-011-Schnitts bereitet den
[Benchmark-Auswertungsvertrag](SQL_SERVER_2025_AI_IDX011_BENCHMARK_CONTRACT.md)
vor: fünf getrennt attestierte Warm-up-Requests je Pfad und 18 serielle Fenster
in drei AB-/BA-/AA-Blöcken mit je 100 Queries. Jede Query hat eigene vollständige
Rows-/Distanz-/Recallprüfung; AA und Warm-ups werden nicht in den A/B-Vergleich
gerechnet. Tatsächliche Counter-/UTC-Grenzen und vollständige Requestbindung,
unabhängig attestierte Ziel-DB-ID und chronologische nicht überlappende Fenster
verhindern falsche Serien- oder Qualitätsclaims. Zwölf synthetische Gegenproben
bestanden. Keine SQL-Ausführung, kein verbrauchter öffentlicher Runtimekandidat
oder Container und keine TP-PERF-/Demoabnahme. Quellen-/Plan-/Memory-/Spill-/
Buildkosten-/Versions-/Recoverygates bleiben offen; runtime_qualification ist
NOT_ESTABLISHED. Ein Owner, ein notwendiger konkreter Quellenreview und eine
kohärente Korrekturwelle für die zeitliche Serienbindung; der unabhängige enge
Quellenreview schloss ohne offene P1/P2. Demo-Ausführungspfade und zehn betroffene
Selector-Gegenproben bestanden. PR169-Head
2f8b7394eac4a8c3f2f754a8528cf8209492e072 gegen Base
40159404acb1b20f0f69072f9e52664f2593bd86 bestand 44 gewählte Checks;
der statisch ausgewählte KI-Runtimejob war SKIPPED/NOT_APPLICABLE.
Squash 87102e8fa022d4b7a870f3d824546efef2d1f341 bestand neun Main-Workflows.
Der vollständige Tree d305e6d0afc8ec8c919a48434bc8affcfbe57dc0 war identisch;
main synchronisiert, eigener Branch lokal/remote entfernt. Die konservativ
durch die Workflowdatei ausgewählten anderen CI-Matrizen sind Integrationsgates,
keine neue Abnahme pausierter Workstreams oder der ANN-Demo.
Der anschließende öffentliche Phasencontroller und seine SQL-Quellen entstehen in
[IDX-011 – Exact gegen Approximate Search](../../Demos/09_AI_SQL_Server_2025/IDX-011_Exact_Approximate_Search/README.md).
Noch keine freigegebene Demo, kein manifest.json und keine TP-PERF-Abnahme.
Der konkrete Quellen-/Sicherheitsreview und die begrenzte lokale Versions-/
Fehler-/Recoverymatrix sind im
[öffentlichen Runtimebefund](SQL_SERVER_2025_AI_IDX011_RUNTIME_REVIEW.md) belegt:
fünf P2 vor SQL geschlossen; Kandidat 1 FAIL_RESULT_CONTRACT nach vollständiger
Quellenaufnahme wegen eines falschen Python-Rundungsoracles, keine Index-/Suchphase.
Vollständiger vorhandener Output und enger unabhängiger Review bestätigten die
rationale Oraclekorrektur ohne Toleranzlockerung. Kandidat 2 erfüllte mit stabiler
Quelle alle acht seriellen Lifecycle-Erwartungen: zwei vollständige 2025-Läufe,
je zwei 2019-/2022-SKIP_VERSION vor Setup und kontrollierte Fehler nach Setup
bzw. Indexbau/vor Suche mit vollständiger Recovery. Neun eigene Container
insgesamt, alle abwesend, keine Downloads/Host-/Fremdmutation.
Je vollständigem Lauf 1810 tatsächlich einzeln geprüfte Benchmarkqueries,
minimales Recall@5 1,0; enge Filterprobe weiterhin null ANN-Rows/Recall 0.
Eigener tatsächlicher repräsentativer Indexplan und Exact-Fallback bestanden.
Beide Baselines/Restores 0/0; unabhängige Attestation vor Drop und DB-Abwesenheit.
Generations-/Memory-/Spill-/Worker-/DOP-/Rollen-/Hard-Abortgrenzen bleiben sichtbar,
keine TP-PERF- oder vollständige Demoabnahme. Betroffene Offlinegegenproben:
zwölf Controller-, zwölf Benchmark- und zehn Selectorprüfungen bestanden.
PR170-Head 159a68d849d91eaf4d2049e86ed361cef49393c4 gegen Base
87102e8fa022d4b7a870f3d824546efef2d1f341 bestand alle 48 Checks. Squash
fa17e414a75a362122a2977b39fb3d3fde577977 bestand alle zehn gewählten Main-Workflows;
vollständiger Tree f842bbb192e705d4aabf57295fa5c14d4a50d8e1 identisch.
main synchronisiert, eigener Branch lokal/remote entfernt. Der geänderte
Demo_Catalog-Pfad wählte W-COV/OPT-017 konservativ; diese Integrationsmatrizen
sind keine ANN-Abnahme und keine Wiederaufnahme pausierter Workstreams.
Unmittelbar folgt der reine Parserzusatz für fehlende Evidenz aus den beiden
neu vorhandenen tatsächlichen Plänen: eigene Statement-/Build-/Indexbindung,
rohe MemoryGrantInfo-/DOP-Attribute, fehlende Warnings/WaitStats bleiben
NOT_CAPTURED. Zwölf synthetische Gegenproben und der reine Replay beider
vollständigen Rohquellen bestanden bei unveränderten bisherigen Planassertions;
enger unabhängiger Methodenreview ohne offene P1/P2. Kein weiterer SQL- oder
Containerlauf und keine still erweiterte Runtimequalifikation. Konkrete Werte
stehen im öffentlichen Runtimebefund. PR171-Head
8991a2134e9d9966d81cdf63932aaa5e1c28fe7b gegen Base
fa17e414a75a362122a2977b39fb3d3fde577977 bestand zehn gewählte Headchecks.
Squash 8ce53d59f051ab385935ba9319fa5033f2fcb179 bestand alle vier gewählten
Main-Workflows; vollständiger Tree 0cd96e297a2f7b68ae8510b9f0a16ba7517bab4c
identisch. main synchronisiert, eigener Branch lokal/remote entfernt.

Unmittelbar folgt die eigene IDX-012-DML-Grenzenvorstufe auf
codex/sql2025-ai-dml-boundary, Basis 8ce53d59f051ab385935ba9319fa5033f2fcb179.
Sie nutzt die weitere ausdrückliche lokale Wellenfreigabe und hält bisherige
Budget-/FAIL-Historie unverändert. Neuer endlicher Umfang: höchstens zwei kohärente
Kandidaten/vier eigene serielle 2025-Container, zwei Lifecycles je positivem
stabilem Kandidaten; ein Owner und ein erforderlicher enger Quellenreview vor SQL.
17.0.5005.3, float32 VECTOR(3), vier CPUs/sechs GiB, eigene IDX-012-Marker/DB.
999 Ausgangsrows mit bisheriger Rezeptur; vier feste positive DML-Kontrollen vor
Indexbau und dieselben vier Operationen danach. UPDATE/DELETE/MERGE betreffen
Id 23, gültiger INSERT betrifft die fehlende Id 1000; höchstens 1000 Rows auch
innerhalb der Transaktion. Alle Änderungen werden zurückgerollt, vollständige
Quellbytes, tatsächlicher Transaktionssnapshot und Indexmetadaten nachkontrolliert.
Eine neue Verbindung prüft sämtliche 999 tatsächlichen Vektoren/Distanzen und
vollständige Snapshots. Erwartete feste Indexverweigerung 42231/State 1 muss
tatsächlich beobachtet werden; andere Resultate sind FAIL mit Rohbefund.
Keine zusätzliche Scoped-Option; nur eigene Preview/MAXDOP mit Originalbaselines,
300 s einschließlich Startup sowie 20 s SQL-Recovery im gemeinsamen 60-s-Cleanup.
Keine neue Benchmarkserie, kein Cloud-/Modell-/ONNX-Aufruf, kein Pull und keine
Host-/Fremdänderung. Der [konkrete DML-Grenzenbefund](SQL_SERVER_2025_AI_IDX012_DML_BOUNDARY_REVIEW.md)
belegt den unabhängig geschlossenen Quellenreview und beide vollständigen Lifecycles
des ersten unveränderten Kandidaten: CDC97E68E2114CE5 und 63AD6D8A17CE4FE9.
Je vier tatsächliche positive DML-Kontrollen ohne Index und vier Verweigerungen
42231/State 1 mit Index, vollständige 999-Row-Quellen-/Indexmetadatenprüfung,
tatsächliche Originalrestores 0/0 und separate DB-/Containerabwesenheit bestanden.
Buildwandzeiten 801,053/1130,006 ms, gesamter Cleanup 12,180/13,164 s.
Beide Admissionen geschlossen, zwei Container verbraucht, kein Runtime-FAIL.
Generation UNKNOWN/WARN, Freshness NOT_TESTED und Runtimequalifikation
NOT_ESTABLISHED; Storage-, Minimalrollen-, Versions- und Hard-Abort-Abnahme offen.
Zwölf Controller-, elf DML-Evidenz- und zehn Selector-Gegenproben bestanden;
anfängliche reine Fixture-Dateinamenfehler bleiben im Befund dokumentiert.
PR172-Head 2b31bd62333530c33d72e38ef1dafad9f842577d gegen Base
8ce53d59f051ab385935ba9319fa5033f2fcb179 bestand alle 13 Checks. Squash
a661ad0e3ac206beb66535c59bfb1512066b6c4a bestand alle sieben tatsächlich gewählten
Main-Workflows; vollständiger Tree 0e525a467777880e55d5fd4f66841d96e01464e7 identisch.
main synchronisiert, eigener Branch lokal/remote entfernt, alle Runtimegates beendet.

Unmittelbarer Folgeschritt: eigener IDX-012-Drop-/Änderungs-/Rebuildmodus auf
codex/sql2025-ai-idx012-rebuild, Basis a661ad0e3ac206beb66535c59bfb1512066b6c4a.
Neues eigenes Budget: höchstens zwei kohärente Kandidaten/vier serielle eigene
2025-Container, zwei vollständige positive Lifecycles am stabilen Kandidaten.
Die weitere ausdrückliche lokale Wellenfreigabe deckt diesen isolierten Effekt:
nach bestätigtem Indexdrop exakt Id 999 dauerhaft auf [1,0,0] ändern, tatsächlichen
Commit/übrige 998 Quellen prüfen, eigenen Index erneut bauen und dieselbe feste
Cosine-Top-5-Abfrage vor/nach anhand aller tatsächlichen Quellen kontrollieren.
Keine neue Scoped-Option, Dimension, Rowzahl, Lastserie, Images oder Hosteffekte;
4CPU/6GiB, Startup im 300-s-Budget und bisherige eigene 20-/60-s-Recoverygrenzen.
Ein Owner, ein erforderlicher unabhängiger enger Quellenreview ohne offene
Methodenbefunde; vor Admission tatsächliche Promotion-/Pfad-/Hashclosure und
betroffene Gegenproben. Der private Controllerentwurf darf nicht direkt laufen.
Freshness ausschließlich OBSERVED_AFTER_REBUILD_ONLY, Generation UNKNOWN/WARN;
keine vollständige Runtime-/TP-PERF-/Storage-/Rollen-/Hard-Abortabnahme.
Historische Budgets und FAIL bleiben erhalten, kein unveränderter Retry.
Rebuild-Kandidat 1 E2EE1E999C104A0A: FAIL_EXECUTION in 50_DropRebuild vor
Batchausführung, tatsächliche Parserfehler 156/State 1 am unquotierten RowCount-
Alias und 102/State 1 an IndexCount. Vorherige DML-Kontrollen bestanden; keine
Ausführung des neuen Drop-/Commit-/Rebuildbatches. Beide Originalrestores 0/0,
separate DB-/Containerabwesenheit und gesamter Cleanup 12,671 s bestanden.
Enge Korrektur ausschließlich SQL-Aliasquotierung [RowCount]/[IndexCount];
aktuelle konkrete Reviewclosure vor geänderter Kandidat-2-Admission erforderlich.
Diese enge Closure bestand; Kandidat 2 E095EBFA02D548F0 lieferte dennoch
FAIL_EXECUTION mit tatsächlichem 42231/State 1 am UPDATE. Der Output attestiert
keinen abgeschlossenen Commit/Rebuild und keinen tatsächlich vorher erfolgten
Drop. Beide Originalrestores 0/0, separate DB-/Containerabwesenheit und gesamter
Cleanup 12,155 s bestanden. Beide Kandidaten beendet; keine weitere Admission
im ursprünglichen Budget. [FAIL-Checkpoint und konkreter Compile-Folgeschritt](SQL_SERVER_2025_AI_IDX012_REBUILD_REVIEW.md)
bereiten getrennt genau einen Kandidaten/zwei Container ohne Korrekturwelle vor:
tatsächliche No-Index-/Transaktionsaufnahme nach Drop, erst danach festes
parametrisiertes UPDATE im unteren Compile-Scope. Frühere Hypothese zur statischen
Bindung bleibt unbewiesen; Freshness NOT_ESTABLISHED. Neue Runtime erst nach
Integration dieses Checkpoints und enger Quellen-/Pfad-/Hashclosure.
PR173 ist vollständig integriert: Head 273ed98bd3592d068dc8ddbb720772205c48617a
gegen Base a661ad0e3ac206beb66535c59bfb1512066b6c4a, alle 13 Headchecks SUCCESS;
Squash efc9d0fa820e633f1159f22d7b151ac74fc5eb06, alle sieben gewählten
Main-Workflows SUCCESS. Tree f0b03f9aebfd1ed9375b59b8c53d0094f3bd889f identisch,
main synchronisiert, eigener Branch lokal/remote entfernt.
Nach tatsächlicher öffentlicher Pfad-/Hashclosure erfüllte die getrennte
Compile-Folge ihren einzigen stabilen Kandidaten mit beiden Lifecycles:
605DA945288C4E55 und 65DAFE36C86649D3. Tatsächlicher Indexcount null nach Drop,
Commit exakt Id 999 und fünf vollständige distanzgeprüfte Suchkontrollen;
Top-5 zuvor 23/40/6/63/46, danach Exact und ANN 999/23/40/6/63, Recall@5 1.
Neue vollständige Quellen-/Metadatenaufnahme bestätigte alle 999 Rows und
unveränderte übrige 998 Vektortexte. Originalrestores 0/0 und separate DB-/
Containerabwesenheit bestanden, gesamter Cleanup 12,379/12,152 s.
Erster Build/Rebuild 756,468/895,366 und 732,222/747,841 ms; keine allgemeine
Kosten-/Qualitygarantie. Generation UNKNOWN/WARN, Freshness ausschließlich
OBSERVED_AFTER_REBUILD_ONLY und Runtimequalifikation NOT_ESTABLISHED.
Alle drei bisherigen Scopeledger bleiben geschlossen, ursprüngliche FAILs
bleiben erhalten. Folgeschnitt codex/sql2025-ai-idx012-compile integriert
ausschließlich diese tatsächlich neue Dokumentation; Code unverändert.
Bei FAIL hält der Kandidat an;
ein geänderter zweiter Kandidat braucht konkreten Befund und aktuelle Closure,
kein stiller Reset. Nach zwei ungelösten Kandidaten checkpointgebundener Stop.
Build-/Storage-/DML-Folgearbeit
bleibt konkret begrenzt und checkpointgebunden; der verbrauchte Zweikandidaten-
Controllerstand wird nicht still zurückgesetzt.
Serverlogin/Pooling und ANN sind nicht abgenommen; Live-/Cloud-/ONNX-Gates bleiben
offen, KI-Heartbeat aktiv.

### Eigenständiger KI-Planungsauftrag vom 2026-10-11

Der Benutzer hat `TSK-003` (KI (künstliche Intelligenz; Verfahren für Aufgaben wie Textverarbeitung oder Vorhersagen) mit und für Microsoft SQL Server 2025: Planungsintegration), den [KI-Workstream-Plan](SQL_SERVER_2025_AI_WORKSTREAM_PLAN.md),
zur Recherche, Planung, Registrierung, Validierung und Planungsintegration autorisiert.
Allgemeine Entwicklung bleibt **PAUSED**. `DEC-073` (Eigenständiger KI-Workstream: Curriculumerweiterung und Planungsgrenze) erweitert nur das künftige Curriculum.
`CUR-013` (KI-Grundlagen für SQL-Server-Fachleute)–`CUR-022` (Architektur, Kosten und kontrollierte Agenten), `TSK-004`–`TSK-014` und 18 Demoentwürfe sind keine begonnenen
Implementierungen und erhalten durch Registrierung keine Ausführungsfreigabe.

Planungsbasis war der saubere, mit origin/main identische Commit
`113648c4884fe788797c5f0c3788a54f74ecfc9c`; zu diesem Zeitpunkt waren keine offenen PRs vorhanden.
Eigener Branch: `codex/sql2025-ai-workstream-plan`. Aktuelle Head-/Base-, Prüf-, Review-
und Mergebelege werden im zugehörigen Planungs-PR geführt. Historische Runtimeprüfungen
werden nicht als KI-Evidenz übernommen. Bestehende DGN-007-/Pauseabschnitte und ausdrücklich
zurückgestellte Arbeiten werden durch diesen Auftrag nicht wieder aufgenommen.

Wiederaufnahme benötigt einen gesonderten Implementierungsauftrag mit gewähltem Erstumfang.
Cloud/Bezahl-API, ONNX (Open Neural Network Exchange; Austauschformat für Modelle)/Instanzänderung und Previewpfade benötigen zusätzlich die benannten
konkreten Freigaben. Der damalige Planungsauftrag erlaubte keine Automation;
die spätere ausdrücklich freigegebene Implementierung und der oben benannte
Heartbeat ersetzen diese historische Grenze ausschließlich für den KI-Workstream.

### Verbindlicher Abschlussumfang vom 2026-10-10

Der Benutzer hat die Methodenänderung ausdrücklich freigegeben und danach
einen zügigen Abschluss verlangt. `DEC-072` ersetzt für diesen begrenzten
Schulungslauf die notwendige exakte QS↔SYSUTC-Klammer durch Diagnose ohne
Puffer. Die Query-Store-Intervallauswahl verlangt tatsächliche reguläre
Erfassung des separat markierten Pollqueries. Tatsächliche Requests,
Ergebnisse, Intervall-IDs, vier reguläre Suchausführungen je Fenster,
Planfamilien, Budgets und unabhängiger Cleanup bleiben maßgeblich.
Der v2-Vertrag und Decoder erhalten die Originalzeiten; historische
v1-Evaluatorregeln werden nicht umgedeutet. Unterschiedliche Starts sind erlaubt.

Der ursprüngliche Reporter ist kein nachgewiesener Reporterfehler. Sein
Fehler-only-Pfad ist durch diese Korrektur überholt: vorhandene Rawdiagnose
und die vollständigen skalaren Capture-Zeitwerte decken den begrenzten
Diagnosebedarf ab. PR 68 wird deshalb begründet verworfen. Die nutzbare
Rawdiagnose aus PR 128 ist bereits durch PR 130 integriert; verbleibender
Reportercode wird aus demselben Grund verworfen. PR 132 enthält den finalen
Parser-/Methodenschnitt und wird nur nach aktueller relevanter CI integriert.
Anschließend werden diese drei zugehörigen Branches nach geprüftem Abgleich
beziehungsweise begründeter Verwerfung und lokaler Sicherung bereinigt.

Weitergehende Provenienz-, Collector-, SESSION_END- und Capstonearbeiten
bleiben ausdrücklich zurückgestellt. Sie sind keine Abschlussbedingung dieses
begrenzten Diagnoseschnitts. Frühere Aussagen zu unverändertem G13 oder noch
fehlender Methodenfreigabe in den folgenden historischen Abschnitten sind
durch diesen Abschnitt und `DEC-072` ersetzt. Historische FAILs bleiben gültig;
der frühere SQL20-Countfehler ist ohne eigene Fehlrohwerte nicht abschließend
erklärt und wird durch einen späteren PASS nicht rückwirkend widerlegt.

Der Benutzerauftrag vom 2026-10-09 nimmt gezielt die Prüfung und den Abschluss
der bestehenden Reporterarbeit in PR 68 wieder auf. Der
[G13-/PR-Review](DGN_007_G13_PR_REVIEW.md) trennt den nützlichen Diagnoseschnitt
von der offenen Methodenänderung und dokumentiert Ursache, Quellenprüfung,
Bestandsabgleich sowie die aktuellen Abschlussbedingungen. Integration verlangt
erfolgreiche relevante CI am aktuellen Head/Base; historische G13-Fehler bleiben
gültig. DEC-069 macht Integration und eigene Branchbereinigung zum Arbeitsabschluss.
Die neue CI am Head `f9ec582…` scheiterte auf 2022 an der SQL20-Abnahme
von vier erfassten Ausführungen je Fenster und auf 2025 an G13 (−0,8298 ms).
Beide ersten DB-Abwesenheitsprüfungen und die eigenen Containerabbauten bestanden.
Der vorherige Matrix-PASS ist keine Freigabe dieses fehlgeschlagenen Heads.
PR68 ist für die getrennte Integration von Prüfbericht und Abschlussprozess
vorübergehend geschlossen; nicht übernommener Code und Branch bleiben konkret
referenziert erhalten. Der aktuelle Benutzerauftrag autorisiert zusätzlich die
begrenzte Ursachenanalyse und Korrektur der Erfassungs-/Zeitgrenzenfehler innerhalb
der bisherigen Methode sowie das getrennte Foundation-Upgrade auf `1.20.0` und
die Prozesskorrektur gemäß `DEC-070` (Foundation 1.20.0 und scopebezogene wirtschaftliche Projektsteuerung). Die frühere Scopeanfrage ist damit erledigt;
eine materielle Methodenänderung bleibt ein eigener erläuterter Entscheid.
Kein Bypass oder Wiederholen bis grün.
Allgemeine Entwicklung, Automation, SESSION_END und die ausdrücklich
zurückgestellte interne Capture-Rückgabe bleiben pausiert.

Der begrenzte Korrekturscope ist im
[aktuellen Reviewabschnitt](DGN_007_G13_PR_REVIEW.md#begrenzter-korrekturscope-nach-foundation-1200)
abgeschlossen dokumentiert: ein lokaler `profile-comparison`-Lifecycle auf SQL
Server 2022 `16.0.4265.3` und ein `control-ba`-Lifecycle auf SQL Server 2025
`17.0.4075.5` bestanden ihre Phasen und beide ersten unabhängigen Cleanupchecks.
Sie reproduzierten die CI-Fehler nicht; es liegt **keine belegte Reparatur** vor.
640,324 s lokale Gesamtwalltime einschließlich fehlgeschlagenem Readinessvorlauf
und eigenem Cleanup; keine Unteragenten, identische Wiederholung oder zusätzliche
SQL-Matrix. Reporter-Head/Branch `f9ec582…` bleibt erhalten und `BLOCKED`.

Wiederaufnahmebedingungen: im tatsächlich fehlgeschlagenen SQL20-Pfad begrenzte
Counts-/Familien-/Rawaufnahme vor Cleanup und eine daraus abgeleitete Gegenprobe;
bei G13 positive/Zero-Rawfragmente desselben Fehlerfalls sowie belastbare
QS↔SYSUTC-Evidenz oder eine ausdrückliche neue Methodenentscheidung. Empfehlung:
G13 zunächst exakt erhalten und die fehlenden Fehlerbelege nachholen. Der Benutzer
hat diese Abnahmerichtung am 2026-10-09 ausdrücklich ausgewählt. Die Methoden-
alternative bleibt ungewählt; kein Puffer, keine Rundung und keine Capänderung
ist aktiviert. Die begrenzte Fehleraufnahme ist inzwischen in PR 130 implementiert, hat aber
noch keinen echten CI-Fehler erfasst. Erst ein belegter Fix mit erforderlichen
aktuellen Head-/Base-Checks erlaubt den Reporter-Merge.

### DGN-007-Diagnose und Abschlussgrenze vom 2026-10-10

Der erneute ausdrückliche Benutzerauftrag nahm ausschließlich DGN-007 zur
autonomen Bearbeitung wieder auf; allgemeine Entwicklung, SESSION_END, interne
Capture-Rückgabe und die pausierte Automation bleiben ausgenommen. Der erhaltene
Reporter wurde in [Draft-PR 128](https://github.com/gecompat/SQL_PerformanceSchulung/pull/128)
auf dem Branch `codex/dgn007-failure-evidence` mit einer ausschließlich im echten
SQL20- beziehungsweise G13-Fehlerzweig aktiven, auf 16 skalare Rohzeilen
begrenzten Diagnose kombiniert. Viererabnahme, G13, Requests, Polling und
Budgets sind unverändert. Nach einer korrigierten SQL-Syntaxstelle bestanden je
ein instrumentierter lokaler `profile-comparison`-Lifecycle auf SQL Server 2022
und `control-ba` auf SQL Server 2025 samt unabhängigen Cleanupprüfungen. Diese
beiden Läufe reproduzierten die Fehler nicht.

Die einzige aktuelle [PR-Matrix 38045921184](https://github.com/gecompat/SQL_PerformanceSchulung/actions/runs/38045921184)
am Head `657bbb22759cfbf27e5fbbfbf63e3660a885b3b2` gegen Base `0601361…`
bestand alle statischen Gates und die vollständigen SQL-Jobs auf 2019, 2022 und
2025. Je Version erreichte der Runner die sechs Scopes mit zwei Lifecycles;
Cleanup und Containerabbau sind im Job erfolgreich abgeschlossen. Weder der
frühere SQL20-Countfehler noch G13 trat auf. Ein aktueller PASS ist deshalb
**keine belegte Korrektur** der fehlgeschlagenen [Matrix 37892941746](https://github.com/gecompat/SQL_PerformanceSchulung/actions/runs/37892941746).
PR 128 bleibt Draft/`BLOCKED`; der Reporter-Code ist nicht in `main`.

Weiter fehlen die tatsächlichen SQL20-Ist-Counts samt Familien-/Rawzustand aus
einem fehlgeschlagenen Lauf und bei G13 die positiven/Zero-Rohfragmente derselben
fehlgeschlagenen Acquisition sowie ein belastbarer QS↔SYSUTC-Zeitquellenbeleg.
Die gewählte exakte G13-Abnahme bleibt bestehen. Wiederaufnahme braucht einen
authentischen Fehlerfall mit diesen begrenzten Belegen und eine daraus abgeleitete
Gegenprobe; eine alternative kollektive Zuordnung verlangt zuvor die ausdrückliche
Methodenentscheidung und ihre offenen Gates aus dem
[Methodenentscheidungspaket](DGN_007_METHOD_DECISION_PACKAGE.md). Keine weitere
unveränderte Matrix und keine Reporter-Integration allein aufgrund des PASS.
Der alte PR68-Branch `codex/dgn007-g13-boundary-report`, der Draft-Branch aus
PR 128 und die ausdrücklich zurückgestellte lokale interne Capturearbeit bleiben
wegen nicht übernommener Änderungen erhalten.

### Integrierter Rohdiagnoseschnitt; Reporter weiterhin blockiert

[PR 130](https://github.com/gecompat/SQL_PerformanceSchulung/pull/130) hat nur
begrenzte Rohdiagnosen in die bereits vorhandenen SQL20-/SQL21-Countfehler- und
SQL35/G13-Fehlerzweige übernommen. Die spätere Query-Store-Rohsicht ist keine
atomare Wiederholung der gespeicherten Profilaufnahme. Sie gibt höchstens
16 skalare Zeilen sowie bei SQL20 beide Fenster-Counts aus; Overflow,
Abfragefehler oder ungültige Records bleiben ausdrücklich unzureichende
Diagnose. Requests, Viererabnahme, exakter G13-Guard, Polling, Caps und
Cleanuppriorität sind unverändert. Der Grenzabstands-Reporter aus Draft-PR 128
ist nicht enthalten.

Die einzige aktuelle [PR-130-Matrix](https://github.com/gecompat/SQL_PerformanceSchulung/actions/runs/38048742623)
am Head `177b1b72341debce9dbc43432259dccffae919f1` gegen Base
`0e71067c2a86d9e866b705fdefaf7dd9f914f397` bestand auf SQL Server
2019/2022/2025 je sechs Scopes mit zwei Lifecycles (36 insgesamt). Alle
36 unabhängigen Datenbank-Cleanupchecks und die drei Containerabbauten
bestanden. Auch Privacy, Registry, Governance, Offline-Bundle und die
betroffenen statischen DGN-007-Checks waren grün. Der Squash-Merge
`aea230fb65798afddd4643c92b84f09403819ec6` hat denselben Tree wie der
geprüfte Head; lokales `main` ist mit `origin/main` synchronisiert. Der eigene
vollständig übernommene Diagnosebranch wurde lokal und remote entfernt.

Keiner der zwei alten Fehler trat in dieser Matrix auf. Tatsächliche SQL20-
Ist-Counts aus einem Fehllauf und positive/Zero-Rawfragmente des SQL-2025-
G13-Fehllaufs fehlen weiter; eine neue Query-Store-Abfrage wäre zudem kein
atomarer Beleg der ursprünglichen Profilaufnahme. Die beobachteten G13-
Grenzverletzungen und eine frühere positive Count-4-Rohzeile widerlegen eine
allgemeine Zero-Count-Erklärung, beweisen aber noch keine zulässige
Zeitquellengrenze. PR 128 bleibt Draft/`BLOCKED`, PR 68 geschlossen mit
erhaltenem Codebranch, die interne Capturearbeit pausiert. Wiederaufnahme:
authentischen fehlgeschlagenen Lauf mit Counts, Rohzeilen und Zeitwerten
gezielt auswerten, daraus eine ursachenbezogene Gegenprobe ableiten und den
exakten G13-Vertrag beibehalten. Falls dies innerhalb des Vertrags nicht
möglich ist, braucht die kollektive Zuordnung eine neue ausdrückliche
Methodenentscheidung mit den offenen Gates des Entscheidungspakets. Kein
weiterer unveränderter Matrixlauf und kein Reporter-Merge allein wegen PASS.

### Neue G13-Fehler nach der Diagnoseintegration

Der [Main-Push-Lauf 38050043409](https://github.com/gecompat/SQL_PerformanceSchulung/actions/runs/38050043409)
am Code-Merge `aea230f…` scheiterte auf SQL Server 2019 in
`CONTROL_AA / RUN_2` an G13. Der Fehlerpfad lieferte
`G13_RAW|INSUFFICIENT|MALFORMED`; die privaten Rawzeilen dieses Laufs sind
nicht rekonstruierbar. 2022 und 2025 bestanden. Alle drei Containerabbauten
und beim Fehllauf der unabhängige Datenbank-Cleanup bestanden. Eine einmalige
isolierte SQL-Server-2019-Formatprobe zeigte die tatsächliche UTC-Ausgabe von
`CONVERT(varchar(40), SWITCHOFFSET(...), 127)` mit abschließendem `Z`.
Der integrierte Decoder hatte `Z` ausgeschlossen. Die eigene Probeninstanz
wurde nach Identitätsprüfung entfernt. Dies belegt den Diagnose-Parserfehler,
nicht die Ursache der G13-Zeitverletzung.

Die darauf begrenzte UTC-Z-Parserkorrektur in
[Draft-PR 132](https://github.com/gecompat/SQL_PerformanceSchulung/pull/132)
am Head `440bfd909ef9ffe59a30ad3aa13c4d57c578b234` gegen Base `0045432…`
bestand lokal die betroffenen Tests, Privacy und das CPython-3.12-Kantenprofil.
Die einzige neue [PR-Matrix 38051475267](https://github.com/gecompat/SQL_PerformanceSchulung/actions/runs/38051475267)
bestand auf 2019 und 2025, scheiterte aber auf SQL Server 2022 in
`CONTROL_BA / RUN_1` an G13. Der korrigierte Decoder lieferte erstmals einen
vollständigen begrenzten Rohblock: Fenster 0, Parent/Query 12, Plan 16,
Intervall 2, Type 0, Count 4, First `12:32:00.2930000Z`, Last
`12:32:00.6570000Z`; Fenster 1, Parent/Query 12, Plan 2, Intervall 3,
Type 0, Count 4, First `12:33:00.8500000Z`, Last `12:33:01.2200000Z`.
Zero-Rawzeilen wurden in diesem begrenzten Block nicht gemeldet. Der
unabhängige Datenbank-Cleanup und alle drei Containerabbauten bestanden.
Der CI-FAIL sperrt PR 132 und bestätigt keine Reporterfreigabe; weder sein
Code noch der Reporter aus PR 128 sind in `main`.

Für SQL20 fehlen weiterhin die Ist-Counts und Rohdaten eines echten
Countfehlers. Für den neuen G13-Fehler fehlen die gespeicherten
`ExecutionStarted`-/`ExecutionFinished`-Werte und ein belastbarer Beleg zur
QS↔SYSUTC-Zeitquellengrenze; der spätere Raw-Read ist kein atomarer Snapshot.
Die zweimalige positive Count-4-Rohsicht schließt Zero-Counts als allgemeine
Erklärung aus. Die vom Benutzer gewählte exakte G13-Abnahme bleibt gültig.
Wiederaufnahme verlangt eine ursachenbezogene, begrenzte Gegenprobe mit
vollständigen Zeitgrenzen oder eine gesonderte materielle Methodenentscheidung
nach dem vorhandenen Entscheidungspaket. Keine weiteren unveränderten
Matrixläufe, kein Bypass und keine stillschweigende Rundung oder Pufferung.
PR 132 und sein Branch bleiben wegen nicht übernommener Parserkorrektur erhalten;
PR 128, der alte PR68-Branch und die pausierte interne Capturearbeit ebenfalls.

### Aktueller Gegenbefund zur Zeitklammer

Der neue Auftrag „weiterführen“ setzt die gezielte DGN-007-Ursachenprüfung fort.
Die [isolierte Zeitquellen-Gegenprobe](DGN_007_G13_PR_REVIEW.md#isolierte-zeitquellen-gegenprobe-vom-2026-10-10)
auf SQL Server 2022 `16.0.4265.3` erfasste 32 synthetische Abfragen genau einmal
je Query. Bei 31 lag der QS-First-Wert vor dem zuvor gemessenen SYSUTC-Start,
maximal um 7,5996 ms. Das ist ein Gegenbeleg zur exakten gemeinsamen Zeitklammer
in dieser Umgebung, keine allgemeine Clock-Erklärung und keine SQL20-Countreparatur.
Beide eigenen Probeninstanzen und Datenbanken sind unabhängig abwesend geprüft.
Der konkrete Ersatz der QS↔SYSUTC-Beweisart durch nachzuweisende Ausführungs-/
Intervallzuordnung ist zur ausdrücklichen Methodenentscheidung vorgelegt.
G13 und die Integrationssperre bleiben bis dahin unverändert. Ein zusätzlich
belegter UTC-Formatfall ohne Sekundenbruch ist im lokalen PR-132-Kandidaten
abgedeckt; kein neuer unveränderter Matrixlauf wurde gestartet.

Am 2026-10-08 hat der Benutzer angewiesen, keine neuen Aufgaben zu beginnen,
alle laufenden Arbeiten konsistent abzuschließen und anschließend diesen
Orchestrator samt Subagents zu beenden. Die bestehende Automation
`sql-performanceschulung-autonome-entwicklung` ist per App auf `PAUSED` gesetzt.
Ausschließlich der bereits vollständig entworfene und unabhängig geprüfte
Loaderrecordvertrag §33 sowie dieser Pausenstand werden in der laufenden PR-Runde
abgeschlossen. Danach folgen erfolgreiche aktuelle CI, Merge nach `origin/main`,
Main-Synchronisierung und unabhängig geprüfter Cleanup des übernommenen eigenen
Arbeitsbranches; keine neue Aufgabe und kein automatischer Chatwechsel.

Wiederaufnahme erfordert einen neuen ausdrücklichen Benutzerauftrag. Dann zuerst
die aktuelle AGENTS-Kette, relevante Regeln, Main, offene PRs, Branches und diese
kanonischen Pläne abgleichen. Erst danach ist der separate SESSION_END-DESIGN-
Vertrag der nächste geplante Schnitt; die vorbereitende Agentenanalyse wurde
beim Benutzerstopp unterbrochen und ist keine implementierte oder dauerhafte
Projektwahrheit. §33 ist ausschließlich DESIGNED: keine halbe ausführbare Demo,
keine operative Promotion und kein zusätzlicher Runtime-/Absenzbeleg. Die offene
G13-/Methodenarbeit in PR 68 und die unübernommene lokale interne Capturearbeit
bleiben aus den unten dokumentierten Gründen erhalten; sie dürfen weder blind
zusammengeführt noch als unbenötigt gelöscht werden. External-/Graph-Table-P2
bleibt im Backlog. PR- und Cleanupabschlussbelege werden im zugehörigen PR ergänzt;
der Basisstand in der Tabelle bleibt eine überprüfte Vorgängerversion.

Historie der vorherigen Wiederaufnahme (durch den aktuellen Stopp abgelöst):

Am 2026-10-07 wurde die allgemeine Verarbeitung ausdrücklich mit den bisherigen
Regeln wieder aufgenommen. Die bestehende 30-Minuten-Automation ist wieder
`ACTIVE`; es wird keine zweite Automation und kein neuer Chat erzeugt. Der
aktuelle nächste Scope bleibt die Importvorbereitung. Der getrennte
[Darstellungs- und Digestentwurf §10](DGN_007_IMPORT_PROFILE_BINDING_DESIGN.md#10-vollständig-erhaltender-darstellungs--und-digestentwurf)
beschreibt eine feste verlustfreie Positionsdarstellung samt separater künftiger
Digestbindung bei unveränderten Inhalten und Caps. Dies ist `DESIGNED`, kein
implementierter Codec und keine v1-Migration. Der separate
[vollständige Fixture-/Größennachweis §11](DGN_007_IMPORT_PROFILE_BINDING_DESIGN.md#11-separat-ausgewählte-vollständige-bootstrapfixture)
enthält 85 vorab gewählte vollständige Records und deren exakte Gegenaufnahme.
Die gemeinsame Metadata beträgt 17.127/17.113/17.091 Bytes einschließlich Header
und überschreitet das unveränderte 16.384-Byte-Cap bei allen drei Ordinals;
sämtliche anderen Formen passen. Neuer reiner Sizer mit 34/34 Gegenproben und
Legacy27/40 ohne SKIP. Dies ist ein negativer vollständiger Entwurfsnachweis,
keine operative Sollinventur, Codec-, Worker-, Trust- oder UsedBytesattestation.
Der getrennte [verlustfreie Stringpoolentwurf §12](DGN_007_IMPORT_PROFILE_BINDING_DESIGN.md#12-verlustfreier-stringpoolentwurf)
liegt als `DESIGNED` vor: eigene Hülle und lokaler Pool je Form, vollständige
Positionen, Werte und Arrayvorkommen, höchstens 256 Poolwerte und sämtliche
bisherigen Caps. Der eigene [reine Pool-Sizer und vollständige Größenbeleg §13](DGN_007_IMPORT_PROFILE_BINDING_DESIGN.md#13-separater-reiner-stringpool-sizer)
ist implementiert und unabhängig geprüft: 37/37 isolierte Gegenproben ohne SKIP,
vollständige neue 3×5-Rechnung mit derselben vorgewählten Fixture und dem
Originalrahmen. Alle 15 Formen passen einschließlich Header, maximal 9.389 Bytes;
Poolanzahlen je Ordinal 204/202/17/172/32. Unabhängige Nachrechnung und vollständige
Feldrückgewinnung bestätigt, keine neue Aufnahme oder Nonce. Dies ist ausschließlich
ein positiver Design-Größenbeleg für diese Kontrollfixture, keine operative
Workerbaseline. Der eigene experimentelle Codec-/Digestpfad steht in
[§14](DGN_007_IMPORT_PROFILE_BINDING_DESIGN.md#14-separater-experimenteller-formcodec-und-design-digests);
41/41 isolierte Gegenproben ohne SKIP, unabhängiger Quell-/Testreview und die
vollständige Originalfixture mit 3×5 Frames, vollständiger Feldrückgewinnung,
kanonischem Repack und neun eigenen Digestwerten bestanden. Die Gesamtausgabe
beträgt 28.264/28.257/28.246 Bytes. Ein unabhängiger Nachreview rechnete sämtliche
Frames und Digests aus den unveränderten Eingaben nach, ohne Codec-/Helper-Replay.
Keine neue Aufnahme oder Nonce. Der eigene reine
[kombinierte Eingangsprototyp §15](DGN_007_IMPORT_PROFILE_BINDING_DESIGN.md#15-separater-experimenteller-kombinierter-eingangsrahmen)
bestand 34/34 isolierte Gegenproben ohne SKIP und den neuen vollständigen
Originalfixturebeleg: drei Frames zu jeweils 140.226 Bytes einschließlich
9.389 Metadata-/Headerbytes und 130.837 unveränderten Rawbodybytes.
Tatsächliche vollständige Feld-/Rawbyterückgewinnung, Repack und unabhängige
Stdlib-Nachrechnung ohne Replay bestanden. Keine neue Aufnahme oder Nonce.
Die konkrete operative [Bootstrap-/Kanalreihenfolge §16](DGN_007_IMPORT_PROFILE_BINDING_DESIGN.md#16-konkrete-operative-bootstrap--und-kanalreihenfolge)
liegt als `DESIGNED` vor. Der reine [Kontrollbootstrapquellengenerator §17](DGN_007_IMPORT_PROFILE_BINDING_DESIGN.md#17-reiner-generator-gehaltener-kontrollbootstrapquellen)
bestand 32/32 ausschließlich synthetische Gegenproben ohne SKIP unter CPython 3.12.14. Die getrennte [Sysconfig-Vorinitialisierung §18](DGN_007_IMPORT_PROFILE_BINDING_DESIGN.md#18-feste-sysconfig-vorinitialisierung-gehaltener-kontrollquellen) bestand 53/53 isolierte synthetische Gegenproben ohne SKIP unter CPython 3.12.14. Die private native Auswahl nach [§19](DGN_007_IMPORT_PROFILE_BINDING_DESIGN.md#19-private-auswahlgrundlage-vor-einer-vollständigen-operativen-inventur) ist mit genau einem begrenzten Versuch und unabhängigem Prozess-/Record-POST abgeschlossen. Die additive reine [Inline-Metadata-Syntaxquelle §20](DGN_007_IMPORT_PROFILE_BINDING_DESIGN.md#20-reine-additive-inline-metadata-syntaxquelle) bestand 80/80 isolierte synthetische Gegenproben ohne SKIP unter CPython 3.12.14; der erste Fixture-Label-Fehllauf bleibt getrennt dokumentiert. Die additive reine [Inline-Metadata-Semantikquelle §21](DGN_007_IMPORT_PROFILE_BINDING_DESIGN.md#21-reine-additive-inline-metadata-semantikquelle) bestand nach zwei engen Fixturekorrekturen 108/108 isolierte synthetische Gegenproben ohne SKIP unter CPython 3.12.14; der erste 106/108-Lauf bleibt getrennt dokumentiert. Vollständige deklarative M/IP/S15/P11/D9-Semantik, unveränderter benannter Originaldigest und Providerkohärenz sind geprüft. Die additive reine [Inline-Profilreporterquelle §22](DGN_007_IMPORT_PROFILE_BINDING_DESIGN.md#22-reiner-additiver-inline-profilreporter) bestand im einzigen isolierten Lauf 149/149 synthetische Gegenproben ohne SKIP unter CPython 3.12.14. Vollständige Scalarprojektion, eigener REPORTED-Pool, atomare begrenzte Records und getrennte Original-/Reportdigests sind geprüft; vier frühere Builder bleiben erhalten. Die reine begrenzte [Inline-Header-/Metadata-Aufnahme §23](DGN_007_IMPORT_PROFILE_BINDING_DESIGN.md#23-reine-begrenzte-inline-header-metadata-aufnahme) bestand im einzigen isolierten Lauf 174/174 synthetische Gegenproben ohne SKIP unter CPython 3.12.14. Exact-Chunktype-/Größenvorläufe, vollständige deklarative M-Semantik und atomare gehaltene Rückgabe sind geprüft; fünf frühere Builder bleiben erhalten. Die additive reine [K-Domain-/Commandquelle §24](DGN_007_IMPORT_PROFILE_BINDING_DESIGN.md#24-reine-k-domain-und-deklarativ-gebundene-commands) bestand im einzigen isolierten Lauf 209/209 synthetische Gegenproben ohne SKIP unter CPython 3.12.14. Vollständiger K8-/D9-Vorlauf, eigene headerfreie E4-K-Domain und atomare kanonische Commands gegen separat gehaltene Callerwerte sind geprüft; sechs bisherige Builder und 174 alte Tests bleiben erhalten. Die additive reine [Inline-Metadata-Callerquelle §25](DGN_007_IMPORT_PROFILE_BINDING_DESIGN.md#25-vollständiger-deklarativer-inline-metadata-callerabgleich) bestand nach zwei engen Fixturekorrekturen 243/243 isolierte synthetische Gegenproben ohne SKIP unter CPython 3.12.14; der erste 241/243-Lauf mit zwei Fehlern vor Matcheraufruf bleibt getrennt dokumentiert. Beide vollständigen Formen und Semantiken, zwei eigene Originalinputdigests und vollständiger Abgleich gegen separat gehaltene I7/W6/K8 sind geprüft; sieben bisherige Builder und 209 alte Tests bleiben erhalten. Die additive reine [Inline-Rawbodyaufnahme §26](DGN_007_IMPORT_PROFILE_BINDING_DESIGN.md#26-reine-begrenzte-aufnahme-deklarierter-rawbodies) bestand nach einer engen Fixturelabelkorrektur 272/272 isolierte synthetische Gegenproben ohne SKIP unter CPython 3.12.14; der erste 271/272-Lauf bleibt getrennt dokumentiert. Vollständige Formen und Größen vor Hashes, beide tatsächlichen D9 und neun Rawhashes vor Callerabgleich sowie atomare Originalbodyrückgabe sind geprüft; acht bisherige Builder und 243 alte Tests bleiben erhalten. Die additive reine [Profilrecord-Reassemblierung §27](DGN_007_IMPORT_PROFILE_BINDING_DESIGN.md#27-reine-begrenzte-reassemblierung-gehaltener-profilrecords) bestand im einzigen isolierten synthetischen Lauf 304/304 Gegenproben ohne SKIP unter CPython 3.12.14. Vollständige begrenzte Control-/Envelopeformen, interne Konsistenz, kanonische Controls und tatsächlicher Footerhash vor Callerordinal sowie atomare Originalrecordrückgabe sind geprüft; neun bisherige Builder und 272 alte Tests bleiben erhalten. Zwei enge Fixturelabelkorrekturen wurden vor dem ersten Lauf reviewt; kein ausgeführter Fehllauf. Die additive reine [Inline-Profil-Callerquelle §28](DGN_007_IMPORT_PROFILE_BINDING_DESIGN.md#28-vollständiger-deklarativer-inline-profilabgleich) bestand im einzigen isolierten synthetischen Lauf 341/341 Gegenproben ohne SKIP unter CPython 3.12.14. Beide vollständigen R4-Formen/Semantiken, Actual-Pool-Repack und vollständiger separater Callerabgleich sind geprüft; die Matchfunktion berechnet keinen SHA. Zehn frühere Builder und 304 alte Methoden bleiben erhalten. Vorreviewkorrekturen und genaue Grenzen stehen in §28. Die additive reine R→BODY_RELEASE-Planquelle aus §29 bestand im einzigen isolierten synthetischen Lauf 378/378 Gegenproben ohne SKIP unter CPython 3.12.14; elf alte Builder und 341 alte Methoden bleiben erhalten. Die additive reine INPUT_COMPLETE-Quelle aus §30 bestand im einzigen isolierten synthetischen Lauf 413/413 Gegenproben ohne SKIP unter CPython 3.12.14; zwölf alte Builder und 378 alte Methoden bleiben erhalten. Der vollständige Record-/Footer→R-Calleradapter aus §31 ist rein additiv implementiert und im isolierten synthetischen Lauf mit 460/460 PASS ohne SKIP geprüft; dreizehn alte Builder und 413 alte Methoden bleiben erhalten. Die eigene lokale [Ledgerkomponente §32.5](DGN_007_IMPORT_PROFILE_BINDING_DESIGN.md#325-eigene-lokale-synthetische-ledgerkomponente) ist im isolierten synthetischen Lauf mit 66/66 PASS ohne SKIP geprüft. Reservierungen, ganze Slot-/Zustandsbindung, sticky Fehler und einmaliger Fakecleanup sind lokal belegt; kein tatsächlicher Kanal-/Loader-/Absenznachweis. Der vollständige [Loaderrecordvertrag §33](DGN_007_IMPORT_PROFILE_BINDING_DESIGN.md#33-vollständige-deklarative-begin-complete-loaderrecords) liegt als DESIGNED vor. Nächster kleiner Schnitt ist ausschließlich der separate SESSION_END-DESIGN-Vertrag mit exakten Counts und nicht selbstreferentiellem Kanalhashpräbild. Tatsächlicher Kanal, Loader-/Parentregistrierungsadapter, operative Inventur und Fünf-Formen-/64-KiB-Gate bleiben offen.
Frische operative Auswahl, inline Empfang und Reporting sowie tatsächliche
Parent-/Worker-, Loader-, Consumption-, Replay- und Cleanupnachweise bleiben
getrennte Gates. Die charakterisierte Fixture ist keine operative Workerbaseline.

Der separate INPUT_COMPLETE-Recordvertrag wurde über
[Pull Request 115](https://github.com/gecompat/SQL_PerformanceSchulung/pull/115)
integriert. Alle acht PR- und sechs separaten Main-Prüfungen bestanden am
jeweiligen aktuellen Stand; tatsächliche Logs und vollständige unabhängige
Übernahme aller 797 versionierten Dateien wurden geprüft. Main ist synchron,
eigener lokaler/remote Branch und Tempref sind unabhängig als abwesend geprüft.
Squash: `dcb6f032d488dfb751329a1e71a906cd1e10ac11`. Dieser abgeschlossene
Dokumentationsschnitt führte keine lokale Suite oder private Probe aus.

Der vollständige Record-/Footer→R-Caller-Vertrag nach §31 wurde über
[Pull Request 117](https://github.com/gecompat/SQL_PerformanceSchulung/pull/117)
integriert. Acht PR- und sechs separate Main-Runs/Jobs/Checks bestanden.
Tatsächliche Checkoutlogs binden Integration
`64c4841a7abfd120b05e93d1aa73816be59d3f5a` und Squash
`665de6dd4127e3f4c3fa4fe9e9ccb7a1c1dd12e7` mit identischem Tree.
Offline bestand alle elf Suiten ohne Test-SKIP, CPython 3.12.14,
zuletzt 413/413; PR 13.058 s, Main 12.623 s. Der Dokumentationsschnitt
führte keine lokale Suite oder private Probe aus. Vollständige unabhängige
Übernahme aller 797 Mode-/Blob-Einträge, Main-FF, eigener lokaler/remote
CAS-Branch-/Tempref-Cleanup und unabhängiger POSTCLEAN sind abgeschlossen.

Die additive reine Builder14-Umsetzung nach §31 wurde über
[Pull Request 118](https://github.com/gecompat/SQL_PerformanceSchulung/pull/118)
vollständig integriert. Alle neun PR- und sieben separaten Main-Runs/Jobs/Checks
bestanden am jeweiligen geprüften Stand. Tatsächliche Checkoutlogs binden
Integration `229b233aa0a14261c1daeb5b7d7ec876b1c8c034` und Squash
`f6559e084ebd660a41a503129f1a28c32be8848b` an denselben Tree
`d39472f26b698e96b8a5d4f6fbce57107b61c75e`.
Offline bestanden alle elf Suiten ohne Test-SKIP; die letzte Suite hatte
jeweils 460/460 PASS: PR unter Ubuntu/CPython 3.12.15 in 13.436 s,
Main unter Ubuntu/CPython 3.12.14 in 15.122 s. Framework bestand separat
alle fünf Befehle, vier Evaluatortests und die tatsächliche Linux-Kindsessionprobe;
PR verwendete CPython 3.12.14, Main 3.12.15. Vollständige unabhängige Übernahme
aller 797 Mode-/Blob-Einträge einschließlich der sieben Scopepins, Main-FF,
eigener lokaler/remote CAS-Branch-/Tempref-Cleanup und unabhängiger POSTCLEAN
sind abgeschlossen. Der lokale einzelne 460/460-Lauf und seine Grenzen bleiben
unverändert in §31.6 dokumentiert.

Der separate Parent-Ledgervertrag nach §32 wurde über
[Pull Request 119](https://github.com/gecompat/SQL_PerformanceSchulung/pull/119)
vollständig integriert. Acht PR- und sechs separate Main-Runs/Jobs/Checks
bestanden am jeweiligen geprüften Stand. Tatsächliche Checkoutlogs binden
Integration `41628e2b407c18e6f32ee469149c4d9b156854d3` und Squash
`6439f03627483a0c7a73a64817898fd0cf215460` an denselben Tree
`89de4120dd4d4c1870f5abc46207021ab8ab527d`.
Offline bestand alle elf Suiten ohne Test-SKIP unter Ubuntu/CPython 3.12.14,
zuletzt jeweils 460/460; PR 14.689 s, Main 12.634 s. Der Designschnitt
führte keine lokale Suite oder private Probe aus. Vollständige unabhängige
Übernahme aller 797 Mode-/Blob-Einträge, Main-FF, eigener lokaler/remote
CAS-Branch-/Tempref-Cleanup und unabhängiger POSTCLEAN sind abgeschlossen.
Die eigene lokale [Ledgerkomponente §32.5](DGN_007_IMPORT_PROFILE_BINDING_DESIGN.md#325-eigene-lokale-synthetische-ledgerkomponente)
ist mit genau einem isolierten Lauf geprüft: 66/66 PASS, 0 Failures/Errors/Skips,
CPython 3.12.14, Exit 0; Unittestzeit 0,426 s, separat gemessene Prozesswall
0,5766168 s. Die nach dem Lauf gemessene Source-/Test-Paarbindung
`91f10b0e68fd9a27f53db65b6b31c295645688d7cf302fd7d8e15cc0f636347c`
blieb unverändert. Tatsächliche Harness-Sentinels für eigene Restorepatches,
Modulcache/__main__, Klassen, Funktionen und Closureinhalte bestanden.
Keine alte Suite oder private Runtime wurde lokal wiederholt. Die Komponente wurde über
[Pull Request 120](https://github.com/gecompat/SQL_PerformanceSchulung/pull/120)
vollständig integriert: neun PR- und sieben separate Main-Runs/Jobs/Checks SUCCESS,
App 15368, Attempt 1, ohne Bypass. Tatsächliche Checkoutlogs binden Integration
`86a658b27469236b5e3bfb223a19f323cb499c35` und Squash
`99af91bc8d25312b62659f6e83f29b3fd2bbcd30` an denselben Tree
`c0f2f9d4cbd1b7403f22960ec23a53b6d455eb4d`.
Alle zwölf Offline-Suiten bestanden ohne Test-SKIP unter Ubuntu/CPython 3.12.15;
Ledger 66/66: PR 0,572 s, Main 0,753 s; Builder14 460/460: PR 11,220 s,
Main 14,963 s. [PR-Offline](https://github.com/gecompat/SQL_PerformanceSchulung/actions/runs/37786515837/job/113342548563)
und [Main-Offline](https://github.com/gecompat/SQL_PerformanceSchulung/actions/runs/37787761337/job/113346816906)
liefern getrennte Nachweise. Alle 799 Pfad-/Mode-/Blob-Einträge und acht LF-Pins
wurden unabhängig vollständig übernommen; 791 Basisdateien blieben unverändert.
Main-FF, eigener lokaler/remote CAS-Branch-/Tracking-/Konfigurations-/Tempref-Cleanup
und unabhängiger POSTCLEAN sind abgeschlossen. Die Gesamtgates bleiben offen.

Der vollständige [Loaderrecordvertrag §33](DGN_007_IMPORT_PROFILE_BINDING_DESIGN.md#33-vollständige-deklarative-begin-complete-loaderrecords) liegt als DESIGNED vor. Nächster kleiner Schnitt ist ausschließlich der separate SESSION_END-DESIGN-Vertrag mit exakten Counts und nicht selbstreferentiellem Kanalhashpräbild. Tatsächlicher Kanal, Loader-/Parentregistrierungsadapter, operative Inventur und Fünf-Formen-/64-KiB-Gate bleiben offen.

Die neue reine additive INPUT_COMPLETE-Quelle nach §30 ist lokal im einzigen
isolierten Versuch mit 413/413 PASS ohne SKIP geprüft. Root und unabhängiger
Reviewer lasen vorher die vollständigen finalen Source-/Testdeltas sowie
tatsächliches Run.execute und delegierten Reporter-tearDown. Die Umsetzung
attestiert keine tatsächliche Eingangsprüfung, Senderherkunft oder Consumption.
Die Umsetzung wurde über
[Pull Request 116](https://github.com/gecompat/SQL_PerformanceSchulung/pull/116)
integriert. Alle neun PR- und sieben separaten Main-Runs/Jobs/Checks bestanden;
sämtliche tatsächlichen Checkoutlogs binden die PR-Integration
`d3ec83010fdd69c923f24c4363b333534c712d30` beziehungsweise den tatsächlichen
Squash `f19e05ad51534cbd9ec4b53fd055317c8d9b9973`. Offline bestand in beiden
CI-Läufen alle elf Suiten mit 413/413 zuletzt und ohne Test-SKIP, CPython 3.12.15;
die letzte Suite dauerte im PR 12.931 s, auf Main 9.812 s. Framework prüfte
jeweils alle fünf Befehle samt vier Evaluatortests und tatsächlicher
Linux-Kindsessionprobe; PR verwendete 3.12.14, Main 3.12.15.
Vollständige unabhängige Übernahme aller 797 Mode-/Blob-Einträge, Main-FF und
eigener lokaler/remote CAS-Branch-/Tempref-Cleanup samt unabhängiger POSTCLEAN-
Prüfung sind abgeschlossen. Dieser neue Dokumentationsschnitt wiederholt
keine lokale Suite oder private Probe.

Die additive reine R→BODY_RELEASE-Planquelle wurde über
[Pull Request 114](https://github.com/gecompat/SQL_PerformanceSchulung/pull/114)
integriert. Alle neun PR- und sieben Main-Prüfungen bestanden am jeweiligen
aktuellen Head. Vollständige unabhängige Squashübernahme aller 797 versionierten
Dateien, Main-Synchronisierung und eigener lokaler/remote Branch- sowie
Tempref-Cleanup einschließlich unabhängiger POSTCLEAN-Prüfung sind bestätigt.
Der Squash ist `94e06d48aecc3940e861f80b488e3423ece4cef1`.
Der lokale isolierte Einzelversuch bestand 378/378 synthetische Methoden
ohne SKIP. Dieser abgeschlossene PR 114 enthielt noch keinen INPUT_COMPLETE-
Matcher; die getrennte spätere Umsetzung und ihre Evidenz stehen in §30.

Der deklarative R→BODY_RELEASE-Vertrag wurde über
[Pull Request 113](https://github.com/gecompat/SQL_PerformanceSchulung/pull/113)
integriert. Alle acht PR- und sechs Main-Prüfungen bestanden am jeweiligen
aktuellen Head. Vollständige unabhängige Squashübernahme, Main-Synchronisierung
und eigener lokaler/remote Branch- sowie Tempref-Cleanup sind bestätigt.
Der Squash ist `7519d0b7e1c4321faafa43ef27efb8629d72cd18`.
Diese Integration änderte ausschließlich fünf kanonische Markdowndateien;
es wurde keine lokale Suite oder private Probe erneut ausgeführt.

Der vollständige deklarative Inline-Profilabgleich wurde über
[Pull Request 112](https://github.com/gecompat/SQL_PerformanceSchulung/pull/112)
integriert. Alle neun PR- und sieben Main-Prüfungen bestanden am jeweiligen
aktuellen Head. Vollständige unabhängige Squashübernahme, Main-Synchronisierung
und eigener lokaler/remote Branch- sowie Tempref-Cleanup sind bestätigt.
Der Squash ist `1d3b73c5d593d8d04514abc259ee4c18727c2126`.
341/341 Methoden bestanden lokal und in beiden CI-Läufen ohne SKIP;
lokal und PR verwendeten CPython 3.12.14, Main 3.12.15.
Der präzisierte finale Reviewnachweis steht in §28.

Die reine begrenzte Profilrecord-Reassemblierung wurde über
[Pull Request 111](https://github.com/gecompat/SQL_PerformanceSchulung/pull/111)
integriert. Alle neun PR- und sieben Main-Prüfungen bestanden am jeweiligen
aktuellen Head. Vollständige unabhängige Squashübernahme, Main-Synchronisierung
und eigener lokaler/remote Branch- sowie Tempref-Cleanup sind bestätigt.
Der Squash ist `a2cd96220973b54172b59a637f4b81276715189a`.
Die Offline-Suite bestand lokal und in beiden CI-Läufen mit 304/304 Methoden
unter CPython 3.12.14; die CI-Frameworkprüfungen verwendeten 3.12.15.
§27 hält den einzigen lokalen Versuch und seine Grenzen fest.

Die reine begrenzte deklarative Inline-Rawbodyaufnahme wurde über
[Pull Request 110](https://github.com/gecompat/SQL_PerformanceSchulung/pull/110)
integriert. Alle neun PR- und sieben Main-Prüfungen bestanden am jeweiligen
aktuellen Head; vollständige Squashübernahme, FF-only-Main-Synchronisierung
und eigener lokaler/remote Branch- sowie Tempref-Cleanup sind unabhängig bestätigt.
Der Squash ist `ac1228537a3de1dcc9126569cf6eec0ef37df810`.
Lokaler und PR-Lauf verwendeten CPython 3.12.14, der separate Main-Lauf 3.12.15.
272/272 Methoden bestanden; der frühere 271/272-Fehllauf und die enge
Fixturelabelkorrektur bleiben in §26 getrennt erhalten. Dieser Beleg ist
ausschließlich synthetisch; operative Kanal-, Worker- und Methodengates bleiben offen.

Der vollständige deklarative Inline-Metadata-Callerabgleich wurde über
[Pull Request 109](https://github.com/gecompat/SQL_PerformanceSchulung/pull/109)
integriert. Alle neun PR- und sieben Main-Prüfungen bestanden am jeweiligen
aktuellen Head. Vollständige unabhängige Squashübernahme, Main-Synchronisierung,
eigener lokaler/remote Branch- und Tempref-Cleanup sowie unabhängige POSTCLEAN-
Nachprüfung sind abgeschlossen. Beide lokalen Fixtureversuche bleiben in §25
erhalten. Die Abnahme belegt vollständigen deklarativen Metadata-Abgleich;
Bodyaufnahme, tatsächlicher Kanal und Freigaben bleiben eigene nächste Schritte.

Die reine additive K-Domain-/Commandquelle wurde über
[Pull Request 108](https://github.com/gecompat/SQL_PerformanceSchulung/pull/108)
integriert. Alle neun PR- und sieben Main-Prüfungen bestanden am jeweiligen
aktuellen Head. Vollständige unabhängige Squashübernahme, Main-Synchronisierung,
eigener lokaler/remote Branch- und Tempref-Cleanup sowie unabhängige POSTCLEAN-
Nachprüfung sind abgeschlossen. Der einzige lokale Lauf bleibt in §24
festgehalten. Die Abnahme belegt K-Digestbildung und deklarativ gebundene
Commandbytes; tatsächlicher Kanal, vollständiger Metadata-Callerabgleich,
Bodyaufnahme und Freigaben bleiben offen.

Die reine begrenzte Inline-Header-/Metadata-Aufnahme wurde über
[Pull Request 107](https://github.com/gecompat/SQL_PerformanceSchulung/pull/107)
integriert. Alle neun PR- und sieben Main-Prüfungen bestanden am jeweiligen
aktuellen Head. Vollständige unabhängige Squashübernahme, Main-Synchronisierung,
eigener lokaler/remote Branch- und Tempref-Cleanup sowie unabhängige POSTCLEAN-
Nachprüfung sind abgeschlossen. Der einzige lokale Lauf bleibt in §23
festgehalten. Die Abnahme belegt begrenzte Aufnahme gegebener Header-/Metadata-
Chunks; tatsächlicher Kanal, Callerabgleich, Bodyaufnahme und Freigaben
bleiben offen.

Der reine additive Inline-Profilreporter wurde über
[Pull Request 106](https://github.com/gecompat/SQL_PerformanceSchulung/pull/106)
integriert. Alle neun PR- und sieben Main-Prüfungen bestanden am jeweiligen
aktuellen Head. Vollständige unabhängige Squashübernahme, Main-Synchronisierung,
eigener lokaler/remote Branch- und Tempref-Cleanup sowie unabhängige POSTCLEAN-
Nachprüfung sind abgeschlossen. Der einzige lokale Lauf bleibt in §22
festgehalten. Die Abnahme belegt die reine Reporterfunktion für gegebene
Scalarinputs; operative Inventur, Receiver, Caller-/Bodyprüfung und
Workerfreigabe bleiben offen.

Die reine additive Inline-Metadata-Semantikquelle wurde über
[Pull Request 105](https://github.com/gecompat/SQL_PerformanceSchulung/pull/105)
integriert. Alle neun PR- und sieben Main-Prüfungen bestanden am jeweiligen
aktuellen Head. Vollständige unabhängige Squashübernahme, Main-Synchronisierung,
eigener lokaler/remote Branch- und Tempref-Cleanup sowie unabhängige POSTCLEAN-
Nachprüfung sind abgeschlossen. Beide lokalen Fixtureversuche bleiben in §21
erhalten. Die Abnahme belegt deklarative Metadata-Semantik und Providerkohärenz;
operative Inventur, Caller-/Bodyprüfung und Workerfreigabe bleiben offen.

Die reine additive Inline-Metadata-Syntaxquelle wurde über
[Pull Request 104](https://github.com/gecompat/SQL_PerformanceSchulung/pull/104)
integriert. Alle neun PR- und sieben Main-Prüfungen bestanden am jeweiligen
aktuellen Head. Vollständige unabhängige Squashübernahme, Main-Synchronisierung,
eigener lokaler/remote Branch- und Tempref-Cleanup sowie unabhängige POSTCLEAN-
Nachprüfung sind abgeschlossen. Beide lokalen Fixtureversuche bleiben in §20
erhalten. Die Abnahme belegt Syntax allein; Metadata-Semantik, Digest-/Body-/
Callerprüfung und Workerfreigabe bleiben eigene nächste Schritte.

Die private begrenzte Auswahlgrundlage wurde über
[Pull Request 103](https://github.com/gecompat/SQL_PerformanceSchulung/pull/103)
integriert. Alle acht PR- und sechs Main-Prüfungen bestanden am jeweiligen
aktuellen Head. Vollständige unabhängige Squashübernahme, Main-Synchronisierung,
eigener lokaler/remote Branch- und Tempref-Cleanup sowie unabhängige POSTCLEAN-
Nachprüfung sind abgeschlossen. Der einmalige native Nachweis ist keine
operative S15-/P11-Inventur oder Workerfreigabe.

Die getrennte feste Sysconfig-Vorinitialisierung wurde über
[Pull Request 102](https://github.com/gecompat/SQL_PerformanceSchulung/pull/102)
integriert. Alle neun PR- und sieben Main-Prüfungen bestanden am jeweils
aktuellen Head. Vollständige unabhängige Squashübernahme, Main-Synchronisierung,
eigener lokaler/remote Branch- und Tempref-Cleanup sowie unabhängige POSTCLEAN-
Nachprüfung sind abgeschlossen. Der 53/53-PASS bleibt auf feste Synthetik
begrenzt; kein realer Sysconfigcall, Profil- oder Workerstart.

Der reine Kontrollbootstrapquellengenerator wurde über
[Pull Request 101](https://github.com/gecompat/SQL_PerformanceSchulung/pull/101)
integriert. Alle neun PR- und sieben Main-Prüfungen bestanden am jeweiligen
aktuellen Head; unabhängige vollständige Squash-Übernahme, Main-Synchronisierung
und eigene lokale/remote Branch- und Tempref-Bereinigung samt unabhängiger
Nachprüfung sind abgeschlossen. Die beiden lokalen Fixture-Fehlläufe bleiben
in §17 getrennt vom korrigierten 32/32-PASS dokumentiert.

Der konkrete operative Bootstrap-/Kanalvertrag wurde über
[Pull Request 100](https://github.com/gecompat/SQL_PerformanceSchulung/pull/100)
integriert. Alle acht PR- und sechs Main-Prüfungen bestanden am jeweiligen
aktuellen Head. Vollständige unabhängige Squash-Übernahme, Main-Synchronisierung
und eigener lokaler/remote Branch- und Tempref-Cleanup einschließlich
unabhängiger Nachprüfung sind abgeschlossen. Die übrigen Implementierungsgates
bleiben offen.

Der vollständige reine kombinierte Eingangsprototyp wurde über
[Pull Request 99](https://github.com/gecompat/SQL_PerformanceSchulung/pull/99)
integriert. Alle neun PR- und sieben Main-Prüfungen bestanden am jeweiligen
aktuellen Head; vollständige Squash-Übernahme, Main-Synchronisierung und lokale/
remote Bereinigung des eigenen Arbeitsbranches wurden unabhängig bestätigt.

Der vollständige experimentelle Formcodec-/Digestbeleg wurde über
[Pull Request 98](https://github.com/gecompat/SQL_PerformanceSchulung/pull/98)
integriert. Alle neun PR- und sieben Main-Prüfungen bestanden am jeweiligen
aktuellen Head; vollständige Squash-Übernahme, Main-Synchronisierung und lokale/
remote Bereinigung des eigenen Arbeitsbranches wurden unabhängig bestätigt.

Der vollständige Stringpool-Größenbeleg wurde über
[Pull Request 97](https://github.com/gecompat/SQL_PerformanceSchulung/pull/97)
integriert. Alle neun PR- und sieben Main-Prüfungen bestanden am jeweiligen
aktuellen Head; vollständige Squash-Übernahme, Main-Synchronisierung und lokale/
remote Bereinigung des eigenen Arbeitsbranches wurden unabhängig bestätigt.

Der separate Stringpoolentwurf wurde über
[Pull Request 96](https://github.com/gecompat/SQL_PerformanceSchulung/pull/96)
integriert. Alle acht PR- und sechs Main-Prüfungen bestanden am jeweiligen
aktuellen Head; vollständige Squash-Übernahme, Main-Synchronisierung und lokale/
remote Bereinigung des eigenen Arbeitsbranches wurden unabhängig bestätigt.

Der vollständige Größenprüfschnitt wurde über
[Pull Request 95](https://github.com/gecompat/SQL_PerformanceSchulung/pull/95)
integriert. Alle neun PR- und sieben Main-Prüfungen bestanden am jeweiligen
aktuellen Head; vollständige Squash-Übernahme, Main-Synchronisierung und lokale/
remote Bereinigung des eigenen Arbeitsbranches wurden unabhängig bestätigt.

Der vorige Designschnitt wurde über
[Pull Request 94](https://github.com/gecompat/SQL_PerformanceSchulung/pull/94)
integriert. Alle acht PR- und sechs Main-Prüfungen bestanden am jeweiligen
aktuellen Head; vollständige Squash-Übernahme, Main-Synchronisierung und lokale/
remote Bereinigung des eigenen Arbeitsbranches wurden unabhängig bestätigt.

Am 2026-10-07 wurde nach der abgeschlossenen Entwicklungsrunde eine Pause
beauftragt. Der letzte integrierte Implementierungs-/Nachweisschnitt ist
[Pull Request 91](https://github.com/gecompat/SQL_PerformanceSchulung/pull/91):
Die getrennte Charakterisierung umfasst 85 Bootstrapnamen; die vollständige
verkleinerte Modularray-Untergrenze beträgt 16.449 Bytes und die gemeinsame
Metadata mit Header mindestens 21.108 bis 21.144 Bytes. Dies schließt nur die
heutige benannte JSON-Darstellung dieses charakterisierten Umfangs aus und
liefert keine operative Sollinventur oder Worker-, Trust- oder UsedBytesattestation.
40 Matcher-Tests bestanden lokal und in Linux-CI. Alle neun PR- und sieben
Main-Prüfungen waren erfolgreich; vollständige Squash-Übernahme, synchronisiertes
Main und lokale/remote Bereinigung des eigenen Arbeitsbranches wurden unabhängig
bestätigt. Die Nachweise und Grenzen stehen im
[Profilbindungsentwurf §9](DGN_007_IMPORT_PROFILE_BINDING_DESIGN.md#9-charakterisierte-bootstraproute-und-größenuntergrenze).

Die damalige Pause wurde einschließlich Wiederaufnahmeverfahren über
[Pull Request 92](https://github.com/gecompat/SQL_PerformanceSchulung/pull/92)
integriert und die Automation pausiert. Erst der spätere ausdrückliche
Fortsetzungsauftrag hebt diese Pause auf. Das Gesamtprojekt und die offenen
fachlichen Gates sind nicht abgeschlossen.

### Geordnete offene Schritte

Der ausdrückliche Auftrag vom 2026-10-07 zur Demo-Orientierung und Vorbereitung der Schulungsabnahme ist ein begrenzter Dokumentationsschnitt. Der [Demo-Katalog](../Demo_Catalog/README.md) ordnet historische Nachweise ein; der [Generalprobenplan](PRS_010_REHEARSAL_PLAN.md) enthält die vorbereitete Auswahl und eine getrennte Folien-/Notes-Prüfung. Eine Teilnehmer-Generalprobe wurde nicht durchgeführt; zur Aufarbeitung der Nachweise wurde keine lokale oder manuell angestoßene SQL-Runtime ausgeführt. Automatisch durch den Pull Request ausgelöste bestehende CI-Prüfungen bleiben an ihren eigenen Run-Commit gebunden und ersetzen keine Teilnehmerabnahme. Dieser frühere Auftrag allein reaktivierte die allgemeine Entwicklung nicht; die spätere ausdrückliche Fortsetzung ist oben getrennt festgehalten. Offene DGN-007-Gates bleiben bestehen.

1. Der vollständig erhaltende Darstellungs- und Digestentwurf liegt als
   getrennter Designschnitt in §10 vor und ist unabhängig zu reviewen.
   Gemeinsame Metadata, Berichte und alle kanonischen Digestpräbilder müssen
   zusammen betrachtet werden: Nur den Transport zu verkleinern reicht bei
   anschließender Expansion in die heutige benannte JSON-Form nicht aus.
   Input82/DGNI001, sämtliche Felder, beide vollständigen Neuner-Deskriptorarrays
   und die bestehenden Caps bleiben erhalten. Keine stillschweigende Filterung,
   Capanhebung oder Digestersetzung; ein Codec ist damit noch nicht implementiert.
2. Die separat vorgewählte vollständige Kontrollfixture und alle fünf Größen sind
   in §11 geprüft. Der §10-Tupelkandidat überschreitet die gemeinsame Grenze.
   Der separate Stringpoolentwurf in §12 erhält alle Inhalte, Arrays, Locator
   und Caps. Der eigene reine Pool-Sizer und alle fünf Formen für alle drei
   Ordinals sind in §13 vollständig geprüft: sämtliche Größen passen, maximal
   9.389 Bytes und 204 Poolwerte; 37 Gegenproben ohne SKIP und unabhängige
   vollständige Nachrechnung. Kein Codec-, Transfer- oder Legacy-Fitclaim.
   Die gewählte Kontrollfixture ist keine zukünftige Workerbaseline.
3. Der eigene experimentelle Formcodec-/Digestpfad in §14 und der reine
   kombinierte Metadata-/Rawbody-Eingang in §15 sind vollständig getrennt
   implementiert und geprüft. Die konkrete operative Bootstrap-/Kanalreihenfolge
   liegt in §16 als `DESIGNED` vor. Der reine Kontrollbootstrapquellengenerator
   in §17 ist ausschließlich synthetisch implementiert und geprüft:
   `Tests/Tools/dgn007_control_bootstrap_source.py` und
   `Tests/Static/test_dgn007_control_bootstrap_source.py`. Seine privaten
   Scriptbytes sind keine operative Workerroute; der §8-Workerlocator bleibt
   Folgearbeit. §8 bleibt importneutral;
   vor PRE_IMPORT keine Combined-/Codec-/Input82-/Matcherimports und keine
   Übernahme der charakterisierten Fixture als operative Baseline. Die reine
   Inline-Syntax, deklarative Metadata-Semantik und der Profilreporter sind
   in §20–22 implementiert und synthetisch geprüft. Die reine begrenzte
   Header-/Metadata-Aufnahme aus gehaltenen Chunks ist nach §23 implementiert
   und synthetisch geprüft. Die reine K-Domain-/Commandquelle nach §24 ist
   mit 209/209 isolierten synthetischen Gegenproben implementiert und geprüft.
   Der vollständige deklarative Header-/Metadata-Callerabgleich nach §25
   ist nach zwei engen Fixturekorrekturen mit 243/243 isolierten synthetischen
   Gegenproben implementiert und geprüft; der erste Fixturefehllauf bleibt
   erhalten. Die reine Bodyaufnahme nach §26 ist nach einer Fixturelabelkorrektur
   mit 272/272 isolierten Gegenproben geprüft; der erste Fehllauf bleibt erhalten.
   Die reine Reassemblierung nach §27 ist im einzigen isolierten Lauf mit
   304/304 Gegenproben geprüft; zwei neue Fixturelabels wurden vor dem Lauf
   korrigiert. Der vollständige deklarative R-Abgleich nach §28 ist im einzigen
   isolierten Lauf mit 341/341 Gegenproben geprüft; zehn frühere Builder und
   304 alte Methoden bleiben erhalten. Die additive reine R→BODY_RELEASE-Planquelle nach §29
   ist im einzigen isolierten Lauf mit 378/378 Gegenproben synthetisch geprüft;
   elf alte Builder und 341 Methoden bleiben erhalten. Der separate
   [INPUT_COMPLETE-Recordvertrag §30](DGN_007_IMPORT_PROFILE_BINDING_DESIGN.md#30-deklarativer-input_complete-rückkanalrecord)
   ist als reine additive Quelle im einzigen isolierten Lauf mit 413/413 PASS
   ohne SKIP geprüft; zwölf alte Builder und 378 alte Methoden bleiben erhalten.
   Der vollständige
   [Record-/Footer→R-Calleradapter §31](DGN_007_IMPORT_PROFILE_BINDING_DESIGN.md#31-vollständiger-deklarativer-profilrecord-callerabgleich)
   ist rein additiv implementiert und mit 460/460 synthetischen Methoden
   ohne SKIP geprüft; dreizehn alte Builder und 413 alte Methoden bleiben erhalten.
   Die eigene lokale Ledgerkomponente nach §32.5 ist isoliert synthetisch geprüft.
   Vollständige Loaderrecordformen nach §33 liegen als DESIGNED vor.
   Nächster kleiner Schnitt: separater SESSION_END-DESIGN-Vertrag mit exakten
   Counts und nicht selbstreferentiellem Kanalhashpräbild.
   Tatsächlicher Kanal und Freigaben folgen getrennt.
   Anschließend operative Auswahl samt Fünf-Formen-/64-KiB-Gate für die
   endgültige Quelle vor jeder tatsächlichen Workerfreigabe sowie
   tatsächliche Parent-/Worker-, Quellen-, Kanal-, Kontext-, Consumption- und
   Replaybindung in kleinen getrennten Schnitten umsetzen und validieren.
4. Anschließend den begrenzten Linux-/Python-3.12-Import-Only-Prototyp mit
   tatsächlicher DGN-Loaderverwendung, Importabschluss und unabhängigem Cleanup
   eigener Worker belegen. Dies ist weiterhin keine vollständige UsedBundle-,
   SQL-, Acquisition-, Methoden- oder Capstoneattestation.
5. G13-/Messvertragsklärung und ausdrückliche Methodenentscheidung bleiben eigene
   Gates. Erst danach die zurückgestellte interne Capture-Rückgabe integrieren,
   Coordinator-Freeze, Ressourcen, serielle Reihenfolge und Budgets belegen und
   frische prospektive Bestätigungsläufe ausführen. Historische Fehler, v1 und
   `DEC-068` (Prospektive Duration- und Kontrollseparation für DGN-007 festlegen) bleiben gültig; keine Toleranz- oder Metrikkorrektur ohne Entscheidung.

### Erhaltene Arbeit und Startverfahren

Die Reporterarbeit in [Pull Request 68](https://github.com/gecompat/SQL_PerformanceSchulung/pull/68)
wurde seit dem gezielten Auftrag vom 2026-10-09 gegen den aktuellen Main-Stand
erneut validiert. Der aktuelle Head `f9ec582…` ist wegen der beiden im
Abschlussreview belegten Runtimefehler technisch blockiert; PR68 wurde für den
getrennten Dokumentationsabschluss vorübergehend geschlossen. Der Code bleibt
auf seinem konkret benannten Branch erhalten. Nach Klärung/Korrektur der
Erfassung und des G13-/Methodengates folgen Quellenreview, erfolgreiche aktuelle
CI, Integration und eigene Branchbereinigung.
Der [Abschlussreview](DGN_007_G13_PR_REVIEW.md) ist für diesen Schnitt maßgeblich.
Der ursprüngliche Reporter-Head war
`27a9b5ce81347beaa6d6bfd8788c62965495f0ca`; die folgenden Befunde beschreiben
den historischen HOLD-Stand, keine abgeschlossene aktuelle Revalidierung.
Der erneute vollständige Branchabgleich am 2026-10-08 gegen Main
`e8dc3a0f37e64ecef8f69cc0afb7dd5912341eac` und sein unabhängiger Review
bestätigen: SQL35, Runner, Producer-Test und -Validator, VertragsJSON sowie
`SQL_CAPTURE_PRODUCER.md` stehen auf Main weiterhin auf PR68-Base
`12b130f0df1f963a9075430745e406e8e2a38494`; die Reporteränderungen fehlen.
Die fünf Kanonik-/Evidenzdokumente wurden dagegen separat übernommen
beziehungsweise fortgeschrieben. Der Branch ist daher weiterhin benötigt
und wurde nicht als redundant gelöscht. PR68 war ausdrücklich als HOLD
ohne Mergefreigabe gekennzeichnet; 20/22 abgeschlossene Checks SUCCESS,
2019 AA1 und 2022 BA1 weiterhin G13 FAIL. Vor einer Integration sind
Methodengate, aktueller Quellenreview und erfolgreiche head-/basegebundene
CI erforderlich; alte Planungsstände dürfen nicht zurückgesetzt werden.
Dieser Statusabgleich änderte keinen G13-Code und startete keine SQL-Runtime.

Der unveröffentlichte lokale Branch `codex/dgn007-internal-capture-receipt`
bei `83f08fb71446445e70fb6227e442ed7109637de6` bleibt erhalten; seine Veröffentlichung
ist zurückgestellt. Beide sind keine freigegebenen Integrationen. Private
Review-/Runtime-Dateien, Chat-Verlauf und lokale Cache-Records sind keine
Voraussetzung oder dauerhafte Projektwahrheit. In dem damaligen Pausenschnitt wurde
keine SQL-Runtime gestartet und keine bestehende SQL- oder Containerressource verändert.

Bei späterer Fortsetzung die native AGENTS-Anweisungskette und die Lesereihenfolge
aus [`.ai/README.md`](../../.ai/README.md) erneut erschließen, den dann aktuellen
`origin/main` samt offenen PRs, Branches und laufender Arbeit prüfen und diesen
Abschnitt gegen [Nächste Entwicklungswellen](NEXT_DEVELOPMENT_WAVES.md),
[Masterplan §19](MASTER_IMPLEMENTATION_PLAN.md#19-wiederaufnahmeprotokoll) und
[Backlog](../../.ai/BACKLOG.md) abgleichen. Den nächsten Scope genau einem
Implementierungsowner zuweisen und unabhängig reviewen. SQL-Runtime bleibt auf
ausdrücklich bestätigte neue isolierte Wegwerfinstanzen begrenzt. Die Automation
nur nach ausdrücklicher Fortsetzung wieder aktivieren; keine automatische
Chat-/Sessionrotation. External Tables und Graph Tables bleiben im Backlog als
nachgeordnetes `P2`-Thema ohne Implementierungs- oder Runtimefreigabe.

## 1. Verifizierter Repository-Stand

Der Repository-Basisstand war zu Beginn der Verarbeitung sauber. Für den korrigierten `OPT-017`-Stand liefen die betroffenen statischen Validatoren, Runner-Selbsttests, `git diff --check` und der Privacy-Scan erfolgreich; letzterer meldete `PASS (files=632; text=621; office=1; archives=0; approved_immutable=1)`.

Die bestehenden CI-Nachweise stammen aus den verlinkten GitHub-Actions-Läufen; ergänzende lokale Nachweise sind in der Tabelle ausdrücklich gekennzeichnet. Die Läufe 33222989681, 33222989682 und 33222989644 prüfen den in `origin/main` enthaltenen Commit `6fd2b1d5170f7658cf0b86ee05314f2ab543adc7`. Pull Request 42 prüft `OPT-017` auf dem unveränderlichen Head `782799e`.

## 2. Runtime-Nachweisstand der produktiven Demos

| Demo | Ergebnis | Status |
|---|---|---|
| `OPT-015` (Ausführungspläne systematisch lesen) | Plan- und Statistikevidenz, zwei vollständige Läufe auf SQL Server 2019, 2022 und 2025 | `VALIDATED` |
| `OPT-016` (Wiederholte Operatorausführung und Zwischenspeicherung) | Outer References, Rebinds, Rewinds und Performance Spool, zwei vollständige Läufe auf 2019, 2022 und 2025 | `VALIDATED` |
| `QRY-013` (Anwendung langsam, Verwaltungswerkzeug schnell) | [Actions-Lauf 30699410795](https://github.com/gecompat/SQL_PerformanceSchulung/actions/runs/30699410795): zwei Docker-basierte Läufe auf 2019, 2022 und 2025 | `VALIDATED` |
| `OPT-009` (Parametersensitive Planoptimierung) | [Actions-Lauf 30701731564](https://github.com/gecompat/SQL_PerformanceSchulung/actions/runs/30701731564): 2022/2025 erfolgreich, 2019 erwartungsgemäß `SKIP_VERSION` | `VALIDATED` |
| `OPT-010` (Planoptimierung für optionale Parameter) | [Actions-Lauf 30702590969](https://github.com/gecompat/SQL_PerformanceSchulung/actions/runs/30702590969): 2025 erfolgreich, 2019/2022 erwartungsgemäß `SKIP_VERSION` | `VALIDATED` |
| `OPT-013` (Sortieren mit zu wenig Arbeitsspeicher) | Gate-B-Nachweis | `VALIDATED` |
| `QRY-001` (Indexfreundliche Suchbedingungen) | Framework- und Lab-Nachweis | `VALIDATED` |
| `OPT-002` (Statistiken lesen) | Framework- und Lab-Nachweis | `VALIDATED` |
| `CON-004` | fachliche Demo und Szenariokandidat | `VALIDATED` |
| `QRY-004` (Optionale Filter, Recompile und dynamisches SQL) | [Actions-Lauf 33222989681](https://github.com/gecompat/SQL_PerformanceSchulung/actions/runs/33222989681): je zwei vollständige Läufe auf 2019/2022/2025; erwartete `WARN_EMPIRICAL_VARIANCE` ohne Vertrags- oder Cleanup-Fehler | `VALIDATED` |
| `DGN-003` (Abfragehistorie mit Query Store), `DGN-005` | [Actions-Lauf 33222989682](https://github.com/gecompat/SQL_PerformanceSchulung/actions/runs/33222989682): je zwei `PASS/OK` auf 2019/2022/2025 | `VALIDATED` |
| `OPT-017` | [Actions-Lauf 33447840232](https://github.com/gecompat/SQL_PerformanceSchulung/actions/runs/33447840232): je zwei `PASS/OK` auf 2019/2022/2025 mit Actual DOP, Exchange, positiver Threadarbeit, serieller Gegenprobe und Cleanup | `VALIDATED` |
| `OPT-003` (Stichproben und ungleiche Datenverteilung), `OPT-005` (Wachsende Schlüssel und Statistikpflege) | Statistik-Sampling/Skew sowie Ascending-Key-/Pflegevertrag; je zwei lokale Docker-Läufe auf 2019/2022/2025 mit `PASS` | `VALIDATED` |
| `CON-006` | Deadlock-Zyklus, Fehler 1205, Graph und geordnete Gegenprobe; je zwei `PASS` auf 2019/2022/2025 | `VALIDATED` |
| `CON-009` (Kosten in tempdb unterscheiden) | [Actions-Lauf 33222989644](https://github.com/gecompat/SQL_PerformanceSchulung/actions/runs/33222989644): TempDB-Kostenklassen auf 2019/2022/2025 jeweils zweimal `PASS/OK` | `VALIDATED` |
| `IDX-006` (Seitenaufteilungen und Seitenbelegung), `IDX-010` (Columnstore-Segmente gezielt überspringen) | Rowstore-Messkette je zweimal mit fachlich akzeptierter Warnung; klassische Columnstore-Segmente je zweimal `PASS` auf allen Zielversionen | `VALIDATED` |
| `STL-008` (Transaktionslog und Dateiwachstum), `STL-009` (Mehrere Änderungen gemeinsam bestätigen) | rote VLF-/Growth-Lane und gelber Commit-/WRITELOG-Schnitt; je zwei `PASS` auf 2019/2022/2025 | `VALIDATED` |
| `RES-007` (Wartezeiten im richtigen Messbereich) | Task-, Request- und Instanz-Waitscope mit Gegenprobe; je zwei `PASS` auf 2019/2022/2025 | `VALIDATED` |
| `QRY-006` (NULL bei NOT IN und NOT EXISTS) | Lokaler Docker-Nachweis: SQL Server 2019/150, 2022/160 und 2025/170, je zwei vollständige Manifestläufe `PASS`; siehe [QRY-006 – lokaler Runtime-Nachweis](QRY_006_RUNTIME_EVIDENCE.md) | `IMPLEMENTED` – Runtime-Gate und SQL_Server_Lab-Szenariopromotion bleiben offen |
| `DGN-007_DATA_MODEL` | Lokaler Docker-Nachweis vom 2026-10-06: 2019/150, 2022/160 und 2025/170 je zwei vollständige Datenmodell-Lifecycles `PASS/OK`, unabhängiger Datenbankabbau nach jedem Lauf und Entfernung aller eigenen Container; siehe [DGN-007 – lokaler Runtime-Nachweis des Datenmodells](DGN_007_DATA_MODEL_RUNTIME_EVIDENCE.md) | `IMPLEMENTED` – begrenzter Datenmodellvertrag; vollständige Capstone-Abnahme und Szenariopromotion bleiben offen |
| `DGN-007_QUERY_STORE_WINDOWS` | Lokaler Docker-Nachweis vom 2026-10-06: 2019/150, 2022/160 und 2025/170 je zwei vollständige Fenster-Lifecycles `PASS/OK`; disjunkte Katalogintervalle, gleiche vier Parameterklassen und je vier erfasste Suchausführungen, unabhängiger Datenbankabbau und Entfernung aller eigenen Container; siehe [DGN-007 – Runtime-Nachweis der Query-Store-Fenster](DGN_007_QUERY_STORE_WINDOWS_RUNTIME_EVIDENCE.md) | `IMPLEMENTED` – begrenzte Capture-Evidenz; kein Incident-, Regressions- oder Capstone-Nachweis |

`QRY-004` bleibt fachlich bewusst warnungsfähig. `WARN_EMPIRICAL_VARIANCE` behauptet keinen nicht gemessenen Performancevorteil und verhindert die Runtimefreigabe nicht, sofern die Matrix vollständig läuft und Ergebnis-, Sicherheits-, Wiederverwendungs- und Cleanup-Verträge erfüllt sind. Genau diesen Zustand belegt Lauf 33222989681.

## 3. Lab-Integration und Szenarien

`LABSCN-001` und `DEC-044` bleiben verbindlich:

- `SQL_Server_Lab` provisioniert die technische Umgebung; dieses Repository beschreibt Lernziel, Setup, synthetische Daten, Benutzeraktionen, Beobachtungen und Reset.
- Ein interaktives Szenario endet nach der Vorbereitung in `READY_FOR_USER`; Reset und Entfernen sind getrennte, bewusste Benutzeraktionen.
- Die automatisierte Matrix ist ein Qualitätssicherungsinstrument und kein Ersatz für den Benutzerworkflow.
- Änderungen an `SQL_Server_Lab` benötigen eine konkret nachgewiesene fehlende Fähigkeit und ausdrückliche Freigabe.

`LABSCN-002` inventarisiert alle 22 produktiven Demos vollständig und wird
gegen den aktiven Demo-Katalog validiert. `LABSCN-003` setzt `CON-004` als
ersten vollständigen Vertical Slice um; `LABSCN-005` ergänzt `DGN-005` und
`CON-006` als zweiten und dritten freigegebenen Slice. Alle drei versionierten
Project Adapter `0.1` begrenzen ihren interaktiven Pfad auf SQL Server 2025 Linux in einer isolierten
Docker- oder Podman-Wegwerfumgebung und besitzen getrennte Preflight-, Install-,
Validate- und Cleanup-Entrypoints.

```text
Auswahl -> Provisionierung -> fachliche Vorbereitung -> READY_FOR_USER
        -> interaktive Durchführung -> Reset -> Remove
```

Die lokalen Nachweise vom 2026-08-30 bestätigten denselben vollständigen
Lifecycle auf Docker (RunId `30b69f0b-b140-47e6-8c90-c05e38bd7c99`) und Podman
(RunId `f80f7d82-934b-4c7c-9d2a-a80e975d92d5`): Start und Reset endeten
jeweils als `READY_FOR_USER`; der anschließende markergebundene Datenbank-,
Container- und Volume-Abbau einschließlich Abschluss des aktiven
Szenario-States endete als `REMOVED`. Der Lab-Core behält ausschließlich den
nicht aktiven Auditdatensatz des entfernten Runs. Der Podman-Cleanup ließ eine
bereits vorhandene, nicht zum Run gehörende Ressource unverändert gesund.

Der `DGN-005`-Folgeslice bestand am 2026-09-01 denselben Lifecycle auf Docker
(RunId `d5143f2a-9f18-49fa-8e9f-b91604993252`) und Podman (RunId
`82791985-b76a-4594-a5be-bab014907f7d`). Beide Provider führten Demonstration,
Observation, Mitigation und Comparison mit `PASS/OK` aus und erreichten nach
dem Reset erneut `READY_FOR_USER`; die markergefilterte, speicherbegrenzte
Extended-Events-Session sowie Datenbank, Container und Volume wurden danach
vollständig entfernt.

Der `CON-006`-Folgeslice bestand am 2026-09-01 den vollständigen Lifecycle auf
Docker (RunId `76cff6ed-a714-44e6-beda-6b916600cb98`) und Podman (RunId
`6d2d0a51-1915-4e65-a380-baec715fc676`). Beide Provider belegten genau ein
Opfer mit Fehler 1205, genau einen Survivor, einen Deadlock-Graph sowie zwei
erfolgreiche Akteure in der geordneten Gegenprobe. Start und Reset endeten als
`READY_FOR_USER`; Cleanup und Infrastrukturabbau endeten als `REMOVED`. Der
Podman-Lauf nutzte wegen einer fremden aktiven Altressource ein isoliertes
Ausweichnetz und ließ die fremde Ressource unverändert.

## 4. Gate-Status

- Gate V0 – Quellenfreigabe: `VALIDATED`.
- Gate V1 – Curriculumfreigabe: `VALIDATED`.
- Gate V2 – Designfreigabe: `VALIDATED`.
- Gate V3 – Runtimefreigabe: `VALIDATED`; alle freigegebenen `ADV-008`- und `W-COV-001`-Demos besitzen den zutreffenden Matrixnachweis.
- Gate V4 – Lehrmittelfreigabe: `VALIDATED`; Masterdeck und Profile bestanden Notes-, Manifest-, Custom-Show-, Build-, Render-, Metadaten-, Privacy- und Branding-Abnahme.
- `LABSCN-001`: `DECIDED` und im Repository verankert.
- `LABSCN-002`: `VALIDATED`; 22 von 22 produktiven Demos besitzen den vollständigen Inventarvertrag.
- `LABSCN-003`: `VALIDATED` für den vollständigen SQL-Server-2025-Lifecycle auf Docker und Podman.
- `LABSCN-004`: `VALIDATED`; Auswahl, Start, Übergabe, Reset und Remove sind standardisiert dokumentiert und statisch abgesichert.
- `LABSCN-005/DGN-005`: `VALIDATED` als zweiter interaktiver SQL-Server-2025-Slice auf Docker und Podman.
- `LABSCN-005/CON-006`: `VALIDATED` als dritter interaktiver SQL-Server-2025-Slice auf Docker und Podman.
- `LABSCN-005/DGN-007`: `IMPLEMENTED_STATIC_SLICE_B` mit praktischer Adapter-Lifecycle-Abnahme vom 2026-09-14: Docker-Run `9ac100f8-f24f-420e-949c-943e35b9bcda` und Podman-Run `e06e9ec9-d239-4cd0-b9a7-0050dc574180` bestanden jeweils Start -> `READY_FOR_USER`, Reset -> `READY_FOR_USER` und Remove -> `REMOVED` auf SQL Server 2025. Die aktuelle Fassung bestand am 2026-09-19 zusätzlich vollständig auf frischen SQL-Server-2025/Linux-Runs: Docker (`ea802c20-4820-4007-a441-43a74a89c8fc`) und Podman (`fba84720-5f0b-4537-bc98-75bbad37a85b`). Jeweils endeten Adapter-Install/Validate, Preflight, Baseline, Evidenz, reversible Mitigation, Vergleich, Teilnehmer-Cleanup, Adapter-Cleanup und Lab-Remove mit `PASS` beziehungsweise `REMOVED`. Als kontrollierter Negativtest des 2025-only-Vertrags liefen auf Docker außerdem SQL Server 2019 (`5a12e48a-46df-471a-a266-4646ba3a02e2`) und SQL Server 2022 (`139c68d8-8a22-42fb-ba19-b51059f21f2b`): kanonisch `ADAPTER_UNSUPPORTED_SQL_VERSION`, tatsächlicher Lab-Core-Status `ADAPTER_UNSUPPORTED_CONTRACT`, keine DGN-Datenbank und abschließend `REMOVED`. Diese Läufe belegen ausdrücklich keine fachliche Unterstützung von 2019/2022 und keine Promotion; sie bestätigen nur den kontrollierten Skip-/Cleanup-Pfad. Die positive Evidenz belegt die aktuelle Linux-Providerparität, aber weder eine vollständige Lifecycle-Matrix noch eine Szenariopromotion. Teilnehmerorchestrierung als interaktives Szenario und `scenario.json` bleiben offen.
- `LABINT-001`: `VALIDATED` als nachgeordneter Testkatalog.
- `LABINT-002`: `VALIDATED` für Start, `READY_FOR_USER`, Reset und Remove von `CON-004` auf Docker.
- `LABINT-003`: `VALIDATED` für die freigegebenen Slices `QRY-001`, `CON-004` und `DGN-005`; Docker-/Podman-Parität ist praktisch belegt.
- `LABINT-004`: `VALIDATED` für die vollständige freigegebene SQL-Server-2025-/Docker-/Podman-Matrix des gelben `CON-006`-Slices einschließlich fachlicher Gegenprobe und Cleanup.
- `INF-002`/`INF-003`: `VALIDATED`; beide Provider-Preflights melden `RESOURCE_OK`, Quickstart und Recovery sind dokumentiert.

`ADV-006` (Design LAB-VP3 und LAB-VP4) und `ADV-007` (Design LAB-VP5 und DGN-007) bleiben als `DESIGNED`-Verträge vollständig: Die zugehörigen LAB-VP3-/VP4-Grenzen, Feature-Skips und Diagnoseabhängigkeiten sind dokumentiert, ihre fachliche Umsetzung erfolgt erst in den jeweiligen Folgewellen.

## 5. Nächste fachliche Verarbeitung

Die verbindliche Reihenfolge und die Akzeptanzkriterien stehen in [Nächste Entwicklungswellen](NEXT_DEVELOPMENT_WAVES.md). Kurzfristig ist die Reihenfolge:

1. `DGN-007` (Zeitabhängige Regression eines Suchworkloads) Capstone-Planungsschnitt ist mit `TSK-002` (Detailreview LABSCN-005/DGN-007: Capstone-Planungsschnitt mit Incident-, Hypothesen-, Zeitfenster-, Reset- und Teilnehmeruebergabevertrag) entschieden
   (`DECIDED_PLANNING`, Stand 2026-09-14); der Detailreviewvertrag steht in
   [LABSCN-005 – Detailreview DGN-007 (Planungsschnitt)](LABSCN_005_DGN_007_DETAIL_REVIEW.md).
2. Implementierungsschnitt A ist umgesetzt und adapterseitig abgenommen:
   Project Adapter `0.1` mit Datenaufbau, Query-Store-Zeitfenstern und
   Incident-Erzeugung ohne Mitigationsmarker; die Docker-/Podman-Lifecycle-Abnahme
   bestand am 2026-09-14 mit RunId `9ac100f8-…` (Docker) und `e06e9ec9-…`
   (Podman) jeweils über Start, Reset und Remove bis `REMOVED`.
3. Implementierungsschnitt B besitzt einen nicht-promotenden statischen
   Teilnehmerablauf und ist auf frischen SQL-Server-2025/Linux-Läufen mit Docker
   und Podman praktisch belegt. Der Ablauf endet nach Cleanup mit
   `REMOVED`; er erzeugt keine interaktive `READY_FOR_USER`-Übergabe. Offen
   bleiben die vollständige Lifecycle-/Versionsmatrix sowie die für eine
   Promotion erforderlichen `scenario.json`-, Manifest- und Inventareinträge.
   Der getrennte Datenmodellvertrag ist am 2026-10-06 auf Docker für alle drei
   Zielversionen je zweimal praktisch belegt. Der getrennte Query-Store-
   Fenstervertrag bestand anschließend ebenfalls je zweimal auf allen drei
   Versionen. Der neutrale `DGN-007_PROFILE_COMPARISON`-Vertrag bestand am
   2026-10-07 ebenfalls je zweimal auf allen drei Versionen. Die vollständige
   Reihenfolge ergab 18 erfolgreiche lokale Lifecycles, vier zusätzliche
   Ausgabekontrollen bestanden auf 2019/2022. Datenbankabwesenheit je Lauf und
   Abbau aller fünf eigenen Container wurden unabhängig bestätigt. Der
   [Profilnachweis](DGN_007_PROFILE_COMPARISON_RUNTIME_EVIDENCE.md) dokumentiert
   gewichtete CPU-/Duration-/Reads-/Rows-Metriken ohne Incidentpromotion.
   Die anschließend getrennten neutralen AB-/BA-/AA-Kontrollcaptures bestanden
   am 2026-10-07 auf allen drei Versionen je zweimal. Die vollständige neue
   Reihenfolge ergab 36 erfolgreiche lokale Lifecycles und unabhängigen Abbau
   aller drei eigenen Container. Der
   [Kontrollnachweis](DGN_007_CONTROL_CAPTURE_RUNTIME_EVIDENCE.md) dokumentiert
   tatsächliche Requestfolge, aktive Plan-ID-/Hash-Union und Metrikvariation.
   Auf 2019 überlappt eine AA-Schwankung einen BA-Duration-Kontrast.
   Der getrennte [prospektive Prüfvertrag](../../Demos/07_Query_Store_Extended_Events/DGN-007_Time_Bounded_Search_Incident/Contracts/README.md)
   liegt jetzt als `STATIC_PROSPECTIVE_CONTRACT` vor (`DEC-068`): reine
   Recordprüfung, gerichtete Duration-Separation gegenüber AA und globaler
   Planfingerprint- oder Reads-Zweig. 34 synthetische Tests und der Validator
   für 14 gebundene SQL-/Manifestquellen bestanden lokal. Das ist ausschließlich
   `PROJECT_SEMANTIC`, keine SQL-Runtime-Abnahme. Der getrennte
   [skalare Collector-Transport](../../Demos/07_Query_Store_Extended_Events/DGN-007_Time_Bounded_Search_Incident/Contracts/COLLECTOR_TRANSPORT.md)
   ist jetzt als `STATIC_COLLECTOR_TRANSPORT` implementiert: reiner begrenzter
   JSON-Decoder, genaue Decimal-/100-ns-Übertragung und gebundene Records.
   19 Transporttests und beide Validatoren bestanden lokal, ebenso die
   34 Prospektivtests. Fehlende Ergebniszeilen je Request bleiben ausdrücklich
   `NOT_CAPTURED`/`None`; auch `MEASURED` ist nur eine Eingabedeklaration.
   Dieser reine Decoder bildet keinen vollständigen RunRecord. Der getrennte
   [SQL-Producer](../../Demos/07_Query_Store_Extended_Events/DGN-007_Time_Bounded_Search_Incident/Contracts/SQL_CAPTURE_PRODUCER.md)
   erfasst jetzt tatsächlich gezählte Ergebniszeilen je Request und stellt
   die vollständige skalare Projektion vor Cleanup bereit. Die neue lokale
   Matrix bestand am 2026-10-07 auf 2019/150, 2022/160 und 2025/170 je zweimal
   AB/BA/AA: insgesamt 18 vollständige Lifecycles mit tatsächlichem Decoder
   und unabhängiger Datenbankabwesenheit. Alle drei eigenen Container sind
   unabhängig abwesend bestätigt. Quellenfreeze, genaue Versions-/Imagebindung
   und getrennte frühere Fehlversuche stehen im
   [Producernachweis](DGN_007_SQL_CAPTURE_PRODUCER_RUNTIME_EVIDENCE.md).
   156 lokale Testmethoden der Phasendiagnostikrevision ergaben 155 PASS und einen ausdrücklich
   Linux-spezifischen SKIP unter Windows. Die Producer-Integration über
   [Pull Request 65](https://github.com/gecompat/SQL_PerformanceSchulung/pull/65)
   ist abgeschlossen: Head `20a867e…` gegen Base `94ed561b…`, geprüfter
   Integrationscommit `df78cb0…`, 14 Workflows und alle 22 Jobs SUCCESS.
   Linux führte alle 156 Methoden ohne SKIP aus. Je Version bestanden zwölf
   Lifecycles, sechs Decoder-Captures und zwölf unabhängige Datenbank-
   abwesenheitsprüfungen; die drei DGN-007-CIDs sind explizit abwesend bestätigt.
   Der Squash `da7b0eb…` wurde am 2026-10-07 um 04:18:12 UTC integriert;
   vollständige Tree-Gleichheit, Main-Synchronisierung und lokale/remote
   Bereinigung des eigenen Arbeitsbranches sind unabhängig bestätigt.
   Die zwei historischen CI-Fehler bleiben im Producernachweis getrennt
   dokumentiert; ihre Ursache ist unbekannt. Die Diagnostik ändert weder
   SQL-Prädikate noch Budgets und behauptet keine Fehlerbehebung.
   Die anschließend getrennte Main-Push-CI am Squash `da7b0eb…` ist vollständig
   beendet: 12 von 13 Workflows und 47 von 48 Jobs SUCCESS. Im
   [DGN-007-Lauf 37570814577](https://github.com/gecompat/SQL_PerformanceSchulung/actions/runs/37570814577)
   scheiterte SQL Server 2022 im zweiten BA-Lifecycle mit
   `CONTROL_EVIDENCE / FAIL_RESULT_CONTRACT / G13`; dieser Guard prüft
   gespeicherte Query-Store-Zeiten gegen `ExecutionStarted/ExecutionFinished`.
   Alle zehn begonnenen 2022-Datenbankabwesenheitsprüfungen und der eigene
   Containerabbau einschließlich expliziter CID-Abwesenheit bestanden.
   2019/2025 bestanden jeweils zwölf Lifecycles und sechs Decoder-Captures.
   Das ist ein neuer tatsächlicher Runtime-Vertragsfehler, keine vollständige
   Main-CI-Freigabe und keine Aufhebung der erfolgreichen PR65-Abnahme.
   Welche Grenze verletzt wurde und weshalb, ist noch nicht belegt.
   Die getrennte private 2022-Gegenprobe bestand anschließend den CI-Präfix
   Datenmodell, Fenster, Profil, AB und BA je zweimal: zehn Lifecycles,
   vier Decoder-Captures, zehn Abwesenheitsprüfungen und fünf zusätzliche
   Gruppen-Leerheitsprüfungen PASS. Die eigene Instanz ist unabhängig abwesend;
   alle 21 Freeze-Dateien blieben gleich. G13 wurde nicht reproduziert und
   es liegen keine tatsächlichen G13-Zeitwerte vor. Zwei vorherige synthetische
   Probe-Vorchecks scheiterten vor jedem Lifecycle; ihre Defekte und ihr
   unabhängig bestätigter Cleanup stehen im Producernachweis getrennt.
   Nächster Schnitt ist der begrenzte kanonische G13-Grenzabstandsbericht,
   ausschließlich im bereits verletzten Fehlerzweig, mit strenger Kanalbindung
   und Ausgabe erst nach Cleanup. Guards, Last und Budgets bleiben gleich.
   Dieser begrenzte kanonische Reporter ist jetzt lokal implementiert und
   unabhängig geprüft. 43 Runner-Tests, 37 Producer-/Reporter-Methoden
   (36 PASS, ein Linux-spezifischer SKIP unter Windows) und sieben
   DGN-007-Validatoren bestanden. Acht tatsächliche temporäre SQL-Branchfixtures
   bestanden auf einer neuen eigenen 2022-Instanz `16.0.4295.3`:
   beide Ein-Tick-Verletzungen, beide Seiten, Gleichheit, gleiche Requestgrenzen,
   UTC-Offset, acht Gruppen und ausdrücklicher Overflow bei neun.
   Quellenfreeze unverändert; eigene CID und Name nach Entfernung unabhängig
   abwesend bestätigt. Der ganze vorherige SQL35 ergibt sich nach exakt
   validierter Reporterentfernung unverändert. Der Report bleibt atomar
   innerhalb 24 Diagnosezeilen und wird erst nach Cleanup ausgegeben.
   Die reguläre CI von [Pull Request 68](https://github.com/gecompat/SQL_PerformanceSchulung/pull/68)
   am Head `27a9b5c…` gegen Base `12b130f…`, Integration `55877a5…`, ist
   vollständig beendet: 13/14 Workflows und 20/22 Jobs SUCCESS. 2019 AA1
   und 2022 BA1 scheiterten an G13; 2025 bestand zwölf Lifecycles und sechs
   Captures. Der Reporter erfasste jeweils genau eine vollständige verletzte
   Gruppe: First−Start beträgt −4.263 beziehungsweise −9.510 100-ns-Ticks,
   entsprechend −0,4263 beziehungsweise −0,951 ms; nur die untere Grenze
   ist verletzt. Alle 32 begonnenen Lifecycles bestanden die erste unabhängige
   Datenbankabwesenheitsprüfung, alle neun SQL-Containerabbauten bestanden;
   DGN-007 mit expliziter eigener CID-Abwesenheit. Linux 163 Methoden PASS.
   Der PR bleibt ohne Mergefreigabe offen. Beide QS-Zeitwerte liegen in diesen
   zwei Beobachtungen auf einem Millisekundenraster; daraus folgt keine
   allgemeine Auflösung, Clockursache oder Toleranzfreigabe. Die getrennte private
   Originalmaterialisierungsprobe reproduzierte G13 auf einer neuen eigenen
   2022-Instanz in AB1: First−Start −0,2609 ms. Die verletzte Gruppe enthält im
   tatsächlich übernommenen Captureversuch und im Live-SELECT jeweils eine
   positive Zeile mit Count vier, keine Zero-/NULL-/Negative-Zeilen. Ein
   Zero-Extremum erklärt diese lokale Verletzung nicht. Elf temporäre SQL-
   Fixtures bestanden; sechs Präfix-Lifecycles PASS, AB1 FAIL, sofortiger Stop.
   Alle sieben ersten DB-Abwesenheitsprüfungen und unabhängiger eigener
   Containerabbau bestanden; Freeze mit 27 Dateien unverändert. Kein AB2/BA/AA
   und kein erfolgreicher AB-Capture. Die Messvertragsgrenze zwischen QS-Endzeit
   und SYSUTC-Requestklammer bleibt ungeklärt. Der quellenbasierte
   [Mess-/Zuordnungsgegenentwurf](DGN_007_CAPTURE_ASSIGNMENT_DESIGN.md) liegt
   jetzt als `PROPOSED` vor: exakter Einschluss und kontrollierte
   Kollektivzuordnung sind getrennte Alternativen. Der Kandidat verlangt
   eine belegte Familienbasis B, sequenziellen T0-Capture vor T1,
   vollständige Bilanz B→B+4→B+8 und vertrauenswürdig attestierten
   Ausführungsumfang. Vorabrequests erfolgen vor der expliziten QS-
   Konfiguration; eine frische Datenbank garantiert kein QS-OFF oder
   Nullbaseline. Konkrete Baseline-/Intervall- und Herkunftsbelege bleiben
   offen. Das getrennte [deklarative Voraussetzungenmodell](DGN_007_ASSIGNMENT_PREREQUISITES_MODEL.md)
   prüft jetzt synthetische Gegenbeispiele und bedingte Konsistenz, ohne
   SQL-/v1-Änderung oder Runtimeattestation. Passende Counts allein belegen
   keine Herkunft; fehlende Annahmen und Widersprüche bleiben getrennt.
   Die getrennte [Quellen-/Ausführungspfadprüfung](DGN_007_PREMISE_SOURCE_REVIEW.md)
   ist abgeschlossen: Procedure-Queries werden auch unter AUTO erfasst;
   asynchrone Persistenz ist keine belegte Publikationsverzögerung. Eigene
   Calls, Ergebnismessung und erster Cleanupabschluss sind nutzbar, aber
   kontinuierlicher QS-Zustand, vollständiger Basisabschluss, interne
   Intervallaktivierung und geschlossene Coordinatorherkunft bleiben offen.
   Der konkrete [Beobachtungs-/Herkunftsvertrag](DGN_007_OBSERVATION_PROVENANCE_CONTRACT_DESIGN.md)
   liegt jetzt als `PROPOSED` vor: acht Stages, vollständige Raw-/Gruppen-/
   Coveragebindung, zwölf tatsächliche Calls, getrennte Pulsgrenze,
   Coordinator-Vertrauensquelle und endliche Größen-/Poll-/Kostenlimits.
   Diese Obergrenzen sind vorgeschlagen, nicht runtimevalidiert; Sättigung
   bleibt bedingt, punktweise States belegen keine Kontinuität. Die äußere
   256-KiB-Grenze belegt heute keine Gesamtgrenze im vorher puffernden Proxy.
   Der [Suffizienzreview](DGN_007_SATURATION_CONTINUITY_SUFFICIENCY_REVIEW.md) ist abgeschlossen: unter unabhängig
   geschlossenem Callumfang und injektiver kohärenter Zählung trägt Sättigung
   Callerfassung; vollständige keyweise Stageledger tragen kollektiv I0/I1.
   Durchgängiges RW/ALL ist ein getrenntes konservatives Methodengate,
   aus Counts nicht bewiesen und hier nicht aufgehoben. Der heutige Pfad
   liest Live-Dateien und adressiert Namen; Bundle-/Zugangs-/Hostgrenze,
   Acquisition-/Floatregel und Kostenmachbarkeit bleiben tatsächlich offen.
   Das getrennte [Sättigungs-/Acquisition-Gegenmodell](DGN_007_SATURATION_COUNTERMODEL.md)
   prüft jetzt den Zählschluss mit synthetischen Ausführungstokens und getrennten
   Claims für Callerfassung, Bucketzuordnung und QS-Zustand. Die alte 42-Test-
   Voraussetzungssuite bleibt erhalten. Keine reale QS-Einzelidentität oder
   Runtime-/Methodenfreigabe. Das konkrete
   [Methodenentscheidungspaket](DGN_007_METHOD_DECISION_PACKAGE.md) ist vorbereitet:
   Acquisition-/Count- und Floatkandidat, ausführbare Freeze-/Actor-/CID-/
   Host-/Zugangsgrenzen sowie gleichzeitige Streaming-/Poll-/Kostenlimits.
   Alle Methodengates bleiben offen; normative Auswahl braucht eine ausdrückliche
   neue Entscheidung. Der [Offline-Quellenbundle-Verifier](DGN_007_SOURCE_BUNDLE_VERIFIER.md)
   ist statisch implementiert: feste 27 Mitglieder, originale Gitblobs,
   getrennte Rohbyte-/LF-Bindung und deklarierte AST-Imports mit Manipulationsfixtures.
   Keine SQL-/Launcher-Runtime oder tatsächliche Ausführungsattestation.
   Die getrennte [Prozess-/Manifestkantenprüfung](DGN_007_EXECUTION_EDGE_VERIFIER.md)
   ist statisch implementiert: Python-3.12-Ganz-AST-Profil, sechs SQL-only-Manifeste,
   14 Quellenhashes und SQLCMD-Gegenproben. Import-/Launcherentwurf PROPOSED,
   tatsächliche Importumgebung und verwendete Runtimebytes offen. Der getrennte
   [synthetische Streaming-/Budgetprototyp](DGN_007_STREAMING_BUDGET_PROTOTYPE.md) ist implementiert:
   portable Budgetgegenproben und feste eigene Linux-Kindfälle, ohne Integration
   in Runtimequellen oder Methoden-/Runtimeattestation. Die getrennte [numerische Pipelinegegenprobe](DGN_007_NUMERIC_PIPELINE_COUNTERMODEL.md) ist implementiert: 28 synthetische Tests trennen Oracle, deklarierte Fragmentrundung, vorgegebenen Text und bestehende Consumergewichtung. Keine SQL-Konversionsemulation, Epsilon- oder Methodenfreigabe. Der konkrete [Import-/UsedBytes-Entwurf](DGN_007_IMPORT_USED_BYTES_PROBE_DESIGN.md) liegt als `DESIGNED` vor: feste Import-Only-Einstiege, kontrollierter Rohbyte-Loader, vertrauenswürdiges Interpreter-/Stdlibprofil, getrennte Receipts und begrenzter eigener Cleanup. Der erste Implementierungsteil ist das getrennte [Eingangsprotokoll](DGN_007_IMPORT_PROBE_INPUT_PROTOCOL.md): unveränderter 27-Member-Git-/Kantenvorcheck, eingefrorene neun Python-Rohbytes und begrenzte binäre Rahmung mit Kontext- und Manipulationsgegenproben. Keine Worker- oder Kandidatenimportausführung und kein UsedBytes-Claim. Die getrennte [synthetische Memory-Loader-Komponente](DGN_007_MEMORY_LOADER_FIXTURE.md) ist implementiert: ausschließlich feste Fixturebytes, tatsächliches Compile/Exec und objektgebundene Beginn-/Abschlussreceipts. Kein DGN-Import oder Importauflösungsnachweis; DGN-Attestationsflags bleiben false. Der getrennte [Interpreter-/Stdlib-Profilvorschnitt](DGN_007_IMPORT_RUNTIME_PROFILE.md) ist implementiert: begrenzte aktuelle Bootstrapmetadaten und Vergleich gegen separat deklarierte Baseline. Keine Trust- oder bereits ausgeführte Bibliotheksbyteattestation; die gewählte Kontrollruntime bleibt eine ausdrücklich benannte Annahme. Der [skalare Parent-/Worker-Profilbindungsvertrag](DGN_007_IMPORT_PROFILE_BINDING_DESIGN.md) liegt als `DESIGNED` vor. Der getrennte [reine Profilvergleich](DGN_007_IMPORT_PROFILE_BINDING_MATCHER.md) ist implementiert: 38 synthetische Tests prüfen exakte deklarierte Installation und Workerinventur, eingefrorenen Eingangs-/Ordinal-/Phasenkontext sowie gemeinsame Metadatengrenzen. Sein Match attestiert keine tatsächliche Workerbeobachtung, Herkunft oder Consumption. Die tatsächliche Prozessanbindung bleibt unimplementiert. Die getrennte lokale Record-Rückgabe des Profilvorschnitts ist jetzt implementiert: `observe_current_interpreter_records` liefert ausschließlich die tatsächlich aufgenommene und vollständig geprüfte Abschlussaufnahme, bei Ablehnung keine Records. Gehaltene Liveanker sind kein dauerhaft gültiger Zustand des Modulcaches; spätere aktuelle Runtimeverwendung braucht eine frische Aufnahme. Legacyreports, Bootstrapimports und Grenzen bleiben erhalten. Die konkrete Bootstraproute ist jetzt im [Profilbindungsentwurf §8](DGN_007_IMPORT_PROFILE_BINDING_DESIGN.md#8-konkreter-bootstrap--und-projektionsvorschnitt) festgelegt: geplante Scriptquelle als `__main__`, unveränderter Profilmodulname, benannte direkte Stdlibimports und Vorinitialisierung der Sysconfigwerte ohne zusätzliche Projektimports. Feldherkunft, frische Aufnahme, erneute Livekohärenz und engere Scalarformen sind getrennt beschrieben. Die getrennte importneutrale skalare Projektion ist jetzt im bestehenden Profilmodul implementiert: frische Aufnahme, vollständige private primitive Tupel, erneute Livekohärenz vor und nach Projektion sowie zusätzliche separat gewählte und gegen Factorycode/Closure geprüfte FileFinder-Hookbindung; bei Ablehnung keine Skalare. Dies attestiert keine unabhängige Factoryherkunft oder tatsächlichen Worker. Eine getrennte lokale Bootstrap-Charakterisierung unter CPython 3.12.3 erfasste 85 Modulnamen mit genau zwei Controls; dies ist keine operative Sollinventur. Der [konservative Größenbeleg](DGN_007_IMPORT_PROFILE_BINDING_DESIGN.md#9-charakterisierte-bootstraproute-und-größenuntergrenze) zeigt bereits mindestens 16.449 Bytes für das vollständige Modularray und 21.108 bis 21.144 Bytes für die gemeinsame Metadata einschließlich Header, unverändertem Input82 und Kontext. Die heutige benannte JSON-Form ist damit für diesen vollständigen charakterisierten Namenumfang nicht darstellbar; andere Routen und Installationen sind dadurch nicht ausgeschlossen. Keine Capanhebung, Filterung oder Digestersetzung ist freigegeben. Der vollständige Linux-/Python-3.12-Import-Only-Prototyp bleibt offen; der getrennte Darstellungs- und Digestentwurf aus Profilbindungsentwurf §10 liegt als DESIGNED vor. Die separat vorgewählte vollständige Kontrollfixture und reine Größenprüfung in §11 belegen gemeinsame Metadata von 17.127/17.113/17.091 Bytes; der §10-Tupelkandidat überschreitet das unveränderte 16.384-Byte-Cap. Neuer Sizer34/34 und Legacy27/40 ohne SKIP. Der getrennte verlustfreie Stringpoolentwurf in §12 liegt als DESIGNED vor, mit eigenen lokalen Pools je Form und unveränderten Inhalten/Caps einschließlich höchstens 256 Poolwerten. Der eigene reine Pool-Sizer in §13 bestand 37/37 isolierte Gegenproben ohne SKIP und die vollständige neue 3×5-Rechnung: maximal 9.389 Bytes einschließlich Header und 204 Poolwerte, vollständig unabhängig nachgerechnet und rückgewonnen. Der getrennte experimentelle Formcodec in §14 bestand 41/41 isolierte Gegenproben ohne SKIP; die vollständige Originalfixture bestand alle 3×5 Frames, Feldrückgewinnung, kanonischen Repack und drei eigene Digestdomains je Ordinal. Das gesamte Fünf-Formen-Set umfasst 28.264/28.257/28.246 Bytes. Originalauswahl und Inputrahmen bleiben unverändert, keine neue Aufnahme oder Nonce. Der unabhängige Nachreview bestätigte sämtliche Frames, Feldrückgewinnung und Digests aus den unveränderten Originaleingaben ohne Codec-/Helper-Replay. Der eigene reine kombinierte Eingangsprototyp in §15 bestand 34/34 isolierte Gegenproben ohne SKIP und die neue vollständige Originalfixtureprüfung: drei Frames mit jeweils 9.389 Metadata-/Headerbytes und 130.837 unveränderten Bodybytes, insgesamt 140.226 Bytes. Tatsächliche vollständige Feld-/Rawbyterückgewinnung und Repack sowie unabhängige Stdlib-Nachrechnung ohne Replay bestanden. Alle gleichzeitig geltenden Caps bleiben erhalten; 64 KiB begrenzen ausschließlich die fünf Metadataausgaben. Die konkrete operative Bootstrap-/Kanalreihenfolge in §16 liegt als DESIGNED vor: importneutraler PRE-Vorschnitt, vollständiger Profilvergleich vor Bodyfreigabe und vollständige Eingangsprüfung vor Importfreigabe, unveränderte gemeinsame Caps und gehaltene Kontrollquellenführung. Der reine Kontrollbootstrapquellengenerator in §17 bestand 32/32 ausschließlich synthetische Gegenproben ohne SKIP unter CPython 3.12.14; er ist keine operative Workerroute. Die getrennte [Sysconfig-Vorinitialisierung §18](DGN_007_IMPORT_PROFILE_BINDING_DESIGN.md#18-feste-sysconfig-vorinitialisierung-gehaltener-kontrollquellen) bestand 53/53 isolierte synthetische Gegenproben ohne SKIP unter CPython 3.12.14. Die private native Auswahl nach [§19](DGN_007_IMPORT_PROFILE_BINDING_DESIGN.md#19-private-auswahlgrundlage-vor-einer-vollständigen-operativen-inventur) ist mit genau einem begrenzten Versuch und unabhängigem Prozess-/Record-POST abgeschlossen. Die additive reine [Inline-Metadata-Syntaxquelle §20](DGN_007_IMPORT_PROFILE_BINDING_DESIGN.md#20-reine-additive-inline-metadata-syntaxquelle) bestand 80/80 isolierte synthetische Gegenproben ohne SKIP unter CPython 3.12.14; der erste Fixture-Label-Fehllauf bleibt getrennt dokumentiert. Die additive reine [Inline-Metadata-Semantikquelle §21](DGN_007_IMPORT_PROFILE_BINDING_DESIGN.md#21-reine-additive-inline-metadata-semantikquelle) bestand nach zwei engen Fixturekorrekturen 108/108 isolierte synthetische Gegenproben ohne SKIP unter CPython 3.12.14; der erste 106/108-Lauf bleibt getrennt dokumentiert. Vollständige deklarative M/IP/S15/P11/D9-Semantik, unveränderter benannter Originaldigest und Providerkohärenz sind geprüft. Die additive reine [Inline-Profilreporterquelle §22](DGN_007_IMPORT_PROFILE_BINDING_DESIGN.md#22-reiner-additiver-inline-profilreporter) bestand im einzigen isolierten Lauf 149/149 synthetische Gegenproben ohne SKIP unter CPython 3.12.14. Vollständige Scalarprojektion, eigener REPORTED-Pool, atomare begrenzte Records und getrennte Original-/Reportdigests sind geprüft; vier frühere Builder bleiben erhalten. Die reine begrenzte [Inline-Header-/Metadata-Aufnahme §23](DGN_007_IMPORT_PROFILE_BINDING_DESIGN.md#23-reine-begrenzte-inline-header-metadata-aufnahme) bestand im einzigen isolierten Lauf 174/174 synthetische Gegenproben ohne SKIP unter CPython 3.12.14. Exact-Chunktype-/Größenvorläufe, vollständige deklarative M-Semantik und atomare gehaltene Rückgabe sind geprüft; fünf frühere Builder bleiben erhalten. Die additive reine [K-Domain-/Commandquelle §24](DGN_007_IMPORT_PROFILE_BINDING_DESIGN.md#24-reine-k-domain-und-deklarativ-gebundene-commands) bestand im einzigen isolierten Lauf 209/209 synthetische Gegenproben ohne SKIP unter CPython 3.12.14. Vollständiger K8-/D9-Vorlauf, eigene headerfreie E4-K-Domain und atomare kanonische Commands gegen separat gehaltene Callerwerte sind geprüft; sechs bisherige Builder und 174 alte Tests bleiben erhalten. Die additive reine [Inline-Metadata-Callerquelle §25](DGN_007_IMPORT_PROFILE_BINDING_DESIGN.md#25-vollständiger-deklarativer-inline-metadata-callerabgleich) bestand nach zwei engen Fixturekorrekturen 243/243 isolierte synthetische Gegenproben ohne SKIP unter CPython 3.12.14; der erste 241/243-Lauf mit zwei Fehlern vor Matcheraufruf bleibt getrennt dokumentiert. Beide vollständigen Formen und Semantiken, zwei eigene Originalinputdigests und vollständiger Abgleich gegen separat gehaltene I7/W6/K8 sind geprüft; sieben bisherige Builder und 209 alte Tests bleiben erhalten. Die additive reine [Inline-Rawbodyaufnahme §26](DGN_007_IMPORT_PROFILE_BINDING_DESIGN.md#26-reine-begrenzte-aufnahme-deklarierter-rawbodies) bestand nach einer engen Fixturelabelkorrektur 272/272 isolierte synthetische Gegenproben ohne SKIP unter CPython 3.12.14; der erste 271/272-Lauf bleibt getrennt dokumentiert. Vollständige Formen und Größen vor Hashes, beide tatsächlichen D9 und neun Rawhashes vor Callerabgleich sowie atomare Originalbodyrückgabe sind geprüft; acht bisherige Builder und 243 alte Tests bleiben erhalten. Die additive reine [Profilrecord-Reassemblierung §27](DGN_007_IMPORT_PROFILE_BINDING_DESIGN.md#27-reine-begrenzte-reassemblierung-gehaltener-profilrecords) bestand im einzigen isolierten synthetischen Lauf 304/304 Gegenproben ohne SKIP unter CPython 3.12.14. Vollständige begrenzte Control-/Envelopeformen, interne Konsistenz, kanonische Controls und tatsächlicher Footerhash vor Callerordinal sowie atomare Originalrecordrückgabe sind geprüft; neun bisherige Builder und 272 alte Tests bleiben erhalten. Zwei enge Fixturelabelkorrekturen wurden vor dem ersten Lauf reviewt; kein ausgeführter Fehllauf. Die additive reine [Inline-Profil-Callerquelle §28](DGN_007_IMPORT_PROFILE_BINDING_DESIGN.md#28-vollständiger-deklarativer-inline-profilabgleich) bestand im einzigen isolierten synthetischen Lauf 341/341 Gegenproben ohne SKIP unter CPython 3.12.14. Beide vollständigen R4-Formen/Semantiken, Actual-Pool-Repack und vollständiger separater Callerabgleich sind geprüft; die Matchfunktion berechnet keinen SHA. Zehn frühere Builder und 304 alte Methoden bleiben erhalten. Vorreviewkorrekturen und genaue Grenzen stehen in §28. Die additive reine R→BODY_RELEASE-Planquelle aus §29 bestand im einzigen isolierten synthetischen Lauf 378/378 Gegenproben ohne SKIP unter CPython 3.12.14; elf alte Builder und 341 alte Methoden bleiben erhalten. Die additive reine INPUT_COMPLETE-Quelle aus §30 bestand im einzigen isolierten synthetischen Lauf 413/413 Gegenproben ohne SKIP unter CPython 3.12.14; zwölf alte Builder und 378 alte Methoden bleiben erhalten. Der vollständige Record-/Footer→R-Calleradapter aus §31 ist rein additiv implementiert und im isolierten synthetischen Lauf mit 460/460 PASS ohne SKIP geprüft; dreizehn alte Builder und 413 alte Methoden bleiben erhalten. Die eigene lokale [Ledgerkomponente §32.5](DGN_007_IMPORT_PROFILE_BINDING_DESIGN.md#325-eigene-lokale-synthetische-ledgerkomponente) ist im isolierten synthetischen Lauf mit 66/66 PASS ohne SKIP geprüft. Reservierungen, ganze Slot-/Zustandsbindung, sticky Fehler und einmaliger Fakecleanup sind lokal belegt; kein tatsächlicher Kanal-/Loader-/Absenznachweis. Der vollständige [Loaderrecordvertrag §33](DGN_007_IMPORT_PROFILE_BINDING_DESIGN.md#33-vollständige-deklarative-begin-complete-loaderrecords) liegt als DESIGNED vor. Nächster kleiner Schnitt ist ausschließlich der separate SESSION_END-DESIGN-Vertrag mit exakten Counts und nicht selbstreferentiellem Kanalhashpräbild. Tatsächlicher Kanal, Loader-/Parentregistrierungsadapter, operative Inventur und Fünf-Formen-/64-KiB-Gate bleiben offen. Frische operative Auswahl, inline Empfang/Reporting, tatsächliche Parent-/Worker-Anbindung, feste Quellenauflösung, tatsächliche DGN-Loaderverwendung und Importabschluss sowie begrenzte eigene Worker mit unabhängigem Cleanup bleiben getrennte Gates. Die charakterisierte Kontrollfixture ist keine operative Workerbaseline; Migration bleibt offen. Sein Claim bleibt auf tatsächlich abgeschlossene Top-Level-Imports begrenzt; keine vollständige UsedBundle-, SQL-, Acquisition- oder Methodenattestation.
   Erst nach
   tragfähiger Methodenentscheidung gemeinsam versionierte Umsetzung.
   Keine implizite OFF-/CLEAR-/Laständerung.
   Bestehende Guards, Fehler und DEC-068 bleiben erhalten;
   Ursache und Behebung offen.
   Einzelheiten stehen im
   [Producernachweis](DGN_007_SQL_CAPTURE_PRODUCER_RUNTIME_EVIDENCE.md).
   Keine identische Wiederholung oder Toleranzkorrektur ohne neue Evidenz.
   Die interne Capture-Rückgabe ist lokal vorbereitet und unabhängig
   geprüft, ihre Veröffentlichung und Integration sind zunächst zurückgestellt.
   Nach der G13-Klärung folgt die interne verlustfreie Capture-Rückgabe:
   den vollständigen Body und tatsächlich geprüfte Phasen übernehmen,
   Rückgabe erst nach erfolgreichem Harness-Cleanup und erstem erfolgreichen
   unabhängigen Abwesenheitscheck. Counts, CLI und Fehlerprioritäten bleiben
   gleich; Recovery liefert niemals einen erfolgreichen Capture-Beleg.
   Dies erzeugt keine RunRecords oder Runtimeattestation. Danach folgen
   Coordinator-Freeze, Ressourcen, tatsächliche serielle Reihenfolge und
   präzise Budgets; erst danach frische prospektive Bestätigungsläufe.
   Die bisherigen Captures belegen keine Regression, Ursache, Mitigation oder
   Capstone-Freigabe.
   Der Compatibility-Vorfix ersetzt im älteren Teilnehmerpfad die ungültige
   Property-Abfrage durch den Katalogwert und lehnt NULL oder Werte ungleich
   170 vor der Evidenzausgabe ab. Die Adaptervalidierung besitzt denselben
   NULL-Schutz. Die Plan- oder Laufzeitprofilbedingung bleibt Folgearbeit.
   Die acht statischen Compatibility-Tests bestanden. Am 2026-10-06 bestanden
   zusätzlich acht T-SQL-Guard-Fixtures (170, 160, NULL und fehlende Zeile je
   SQL-Quelle), die echte Abfrage eines fehlenden Zielnamens sowie die
   Kontextprojektion mit synthetischen Query-Store-Optionen und echtem
   `master`-Katalogwert auf SQL Server 2025 Developer `17.0.4075.5`.
   Aufruf: `python Tests/Static/test_dgn007_compatibility.py --container NAME
   --confirm-disposable-instance`. Die frische eigene Instanz war vor und
   nach den lesenden Prüfungen leer und wurde anschließend nach
   Eigentumsprüfung entfernt; ihre Abwesenheit wurde unabhängig bestätigt.
   Die ersten Versuche scheiterten an der fehlenden Query-Store-Optionszeile
   in `master` und zählen nicht als erfolgreiche Evidenz. Der Nachweis gilt
   nur für Katalogzugriff, Guard- und Projektionsfixtures; er enthält keine
   echte Compatibility-Änderung und keinen vollständigen Teilnehmerlauf.
4. Eine weitere `LABINT-004`-Matrixaussage erst aktivieren, wenn ein zusätzlicher gelber Slice samt Safety- und Szenariofreigabe sie benötigt.
5. Docker-/Podman-Ressourcen-, Netzwerk-, Hyper-V- oder gemischte Topologien nur bei einer konkret nachgewiesenen fachlichen Abhängigkeit bearbeiten.
6. Änderungen an `SQL_Server_Lab` bleiben ohne konkrete Fähigkeitslücke und ausdrückliche Freigabe gesperrt.

## 6. Sicherheits-, Datenschutz- und Quellenstatus

- Szenariodefinitionen enthalten nur synthetische Daten, relative Projektpfade, öffentliche Versionsbezeichnungen und generische Rollen.
- Gelbe und rote Szenarien behalten ihre bestehenden Safety-Gates; `RES-003` benötigt zusätzlich dedizierte Wegwerfinfrastruktur, High-Impact-Bestätigung, Kill-Switch und Laufzeitbudget.
- `DGN-007` setzt validierte Query-Store- und Extended-Events-Evidenz voraus.
- Der SQL-Server-2025-Delta-Review ist in `SQL_SERVER_2025_DELTA_REVIEW.md` abgeschlossen: CE (Cardinality Estimation; Schätzung der Zeilenanzahl) Feedback für Ausdrücke und zeitgebundene XE-Sessions sind in bestehende Verträge übernommen; vier Infrastruktur-/Abhängigkeitsthemen bleiben zurückgestellt, Vector/KI außerhalb des Curriculums.
- Aktuelle Herstellerdokumentation allein ist weiterhin kein Implementierungs- oder Runtime-Nachweis.

### IDX-012: Speicherfolge nach vollständig abgeschlossener PR174-Integration

PR174-Head d1b3395810461bb849409efc93af0a9daf8f3694 gegen Basis efc9d0fa820e633f1159f22d7b151ac74fc5eb06 bestand alle 13 Headchecks. Squash 2d8a6005a9300094af573ae05e30b9dea69192e6 bestand alle sieben ausgewählten Main-Workflows einschließlich KI-Matrix und Cleanup. Vollständiger Tree f03f807aadbf3e52d7ba221a2861de444e5896fc identisch; main/origin/main synchronisiert, eigener Compile-Branch lokal und remote entfernt. Der [Rebuildnachweis](SQL_SERVER_2025_AI_IDX012_REBUILD_REVIEW.md) belegt die beiden positiven Lifecycles unter Erhalt der historischen FAILs.

Unmittelbar folgt der [begrenzte DB-Speichernachweis](SQL_SERVER_2025_AI_IDX012_STORAGE_REVIEW.md) auf codex/sql2025-ai-idx012-storage, Basis 2d8a6005a9300094af573ae05e30b9dea69192e6. Die ausdrückliche weitere lokale Wellenfreigabe gilt; neues endliches Budget genau ein stabiler Kandidat/höchstens zwei eigene serielle Container, keine Korrekturwelle. Drei vollständige read-only DB-Katalogaufnahmen ergänzen den festen Drop-/Commit-/Rebuildpfad. Effektgrenzen bleiben eigene Preview/MAXDOP/999–1000 Rows/300 s einschließlich Startup/20 s SQL-Recovery innerhalb 60 s gesamtem Cleanup. Unabhängiger Quellenreview und tatsächliche Runtime vor Ergebnisclaim erforderlich. Kein isolierter Indexkosten-, TempDB-, Writes-, Worker- oder TP-PERF-Claim; alte geschlossene Budgets werden nicht wiederverwendet. Gesamtworkstream und Heartbeat bleiben aktiv.

Der erste Storage-Lauf 0B6514D624F84921 scheiterte vor Indexbau am SQL-Guard (51003/State1/Zeile59); vollständige Storageaufnahme fehlt, tatsächliche abweichende Guardgröße UNKNOWN. Restore Preview/MAXDOP0/0, unabhängige DB-/eigene CID-/Namensabwesenheit und gesamter Cleanup12,353s bestanden; LedgergeschlossenFAIL, kein zweiter Lauf/keineKorrekturwelle. Eine getrennte Capturefolge mit getrennt vor Subqueries erfasstem Transaktionsstatus und ausgegebenen tatsächlichen Guardwerten ist im [Speichercheckpoint](SQL_SERVER_2025_AI_IDX012_STORAGE_REVIEW.md) vorbereitet. Das frühere Budget wird nicht zurückgesetzt. Neue Admission erst nach enger unabhängiger Quellenclosure und vollständiger PR-Integration dieses Checkpoints; weitere lokale Wellenfreigabe gilt. Gesamtworkstream und Heartbeat bleiben aktiv.

PR175 ist vollständig abgeschlossen: Head 7a27ba984834a8d75f5d3d7a39db178c6f2fb29b gegen Base 2d8a6005a9300094af573ae05e30b9dea69192e6 mit 13 SUCCESS; Squash 36c2d7aacd4a27185968128f72ae4a8164e120b1 mit sieben ausgewählten Main-SUCCESS. Vollständiger Tree ee6fb8ab17ed0e1de9cc017d95523af66f2a9617 identisch, main synchronisiert und eigener Branch lokal/remote bereinigt. Die Capturefolge auf codex/sql2025-ai-idx012-storage-capture scheiterte erneut vor Indexbau, nun mit tatsächlichen Guardwerten: Token DCC9B668B1234055, 999 Rows, Indexcount 0, Transaktion 0/0, zwei Dateien, 43 interne Tabellen und 199 Partitionen. Limit 128 ist zu klein; der erste FAIL ohne Counts bleibt einzeln ungeklärt. Restores 0/0, unabhängige DB-/CID-/Namensabwesenheit und gesamter Cleanup 12,658 s bestanden; Captureledger geschlossen FAIL, kein zweiter Lauf.

Die neue [begrenzte Katalogfolge](SQL_SERVER_2025_AI_IDX012_STORAGE_REVIEW.md#tatsächliche-capturefolge-und-neue-kataloggrenze) nutzt die weitere lokale Wellenfreigabe: vollständige Aufnahme bis 512 Partitionen/unverändert 120000 UTF-16-Bytes; übrige Guards, DB-/Dateimaxima, Optionen, 999–1000 Rows, 300 s einschließlich Startup und 20 s SQL-Recovery innerhalb 60 s Cleanup bleiben unverändert. Neuer unabhängiger Parent/Ledger: genau ein stabiler Kandidat/maximal zwei serielle eigene Container, keine Korrekturwelle; die beiden alten FAIL-Budgets bleiben geschlossen. Admission erst nach engem Quellenreview und öffentlichem Pfad-/Hashschluss; vollständiger PR-/Integrationsabschluss dieses zusammenhängenden Capture-/Grenzenschnitts bleibt Pflicht. Gesamtworkstream und Heartbeat bleiben aktiv.

Die Katalogfolge bestand danach beide vollständigen eigenen Lifecycles: Tokens 2D00C5B617964E25/B249FF1FEB194EC3, tatsächlicher Build 17.0.5005.3, WARN_OPTIONAL_EVIDENCE_SKIPPED. Drei vollständige Storageaufnahmen je Lauf mit 199/203/203 Partitionen und 43/45/45 internen Tabellen; alle Scalars 102438/104908/104908 UTF-16-Bytes ohne Trunkierung. Tatsächliche Originalrestores 0/0, unabhängige DB-/CID-/Namensabwesenheit und gesamter Cleanup 12,686/12,624 s bestanden. Beide Admissionen des stabilen Kandidaten sind geschlossen, Budget ausgeschöpft ohne Korrekturwelle. Alle bisherigen DML-/Quellen-/Drop-/Commit-/Rebuild-/Recallkontrollen bestanden. [Ergebnisse und Grenzen](SQL_SERVER_2025_AI_IDX012_STORAGE_REVIEW.md#katalogfolge-zwei-vollständige-positive-lifecycles); Generation UNKNOWN, Freshness OBSERVED_AFTER_REBUILD_ONLY, isolierte Kosten und vollständige Runtimequalifikation offen. Beide alten FAIL-Ledger bleiben erhalten. Der konsistente Ergebnisstand wird jetzt über PR integriert; anschließend nächster zulässiger Schritt tatsächliche, getrennt interpretierte Session-/TempDB-/DB-Dateikostenpunkte, keine reine Indexkostenbehauptung. Gesamtworkstream und Heartbeat bleiben aktiv.

### IDX-012: Kostenfolge nach vollständig abgeschlossener PR176-Integration

[PR 176](https://github.com/gecompat/SQL_PerformanceSchulung/pull/176) ist nach
13 erfolgreichen Headchecks auf cd28bf5ccf11ba6865c410b3c7e3a4f8c1384606 in
018c678f55660a559bfd2acc4eb3f56675bce8eb integriert. Vollständiger Tree
f68328b2943b93a306874dbee76c015e36e6fdfa identisch; alle sieben ausgewählten
Main-Workflows bestanden: 38174402097/38174402166/38174402101/38174402066/
38174402139/38174402067/38174402085. main synchron, sauber; eigener
Storage-Capture-Branch lokal/remote entfernt, keine eigenen Container verblieben.

Der [Phasenkostenschnitt](SQL_SERVER_2025_AI_IDX012_COST_REVIEW.md) auf
codex/sql2025-ai-idx012-costs, Basis 018c678f55660a559bfd2acc4eb3f56675bce8eb,
ist nach zwei Kandidaten mit FAIL angehalten. Die weitere lokale Wellenfreigabe
gilt; der neue eigene Parent/Ledger erlaubte maximal zwei stabile Kandidaten/
vier serielle eigene Container und verlangte zwei positive Lifecycles desselben
Kandidaten. Effekte unverändert: eigene Preview/MAXDOP, 999–1000 Rows,
300 s einschließlich Startup, 20 s SQL-Recovery innerhalb 60 s gesamtem Cleanup.
Keine isolierten Indexbau- oder vollständigen Worker-Kosten. Admissionen erst
nach öffentlicher Quellenbindung und engem unabhängigem Review.

C1 448381C255F044D1: native Windows-ODBC-sqlcmd verwirft die neuen unquotierten
-v-Drivepfade vor Kosten-SQL/erstem Indexbau. Setup/Enable/Source-/Storagebaseline
bestanden; beide tatsächlichen Restores 0/0 und unabhängige DB-/eigene Namens-/
vollständige CID-Abwesenheit belegt. Gesamter Cleanup 13,2039358 s;
closed=true/FAIL, keine zweite C1-Admission. C2 änderte ausschließlich die
feste Include-Pfadübergabe auf Prozess-ENV. Der enge ENV-Review fand vor
Admission einen Windows-Case-P2; alle reservierten Schreibvarianten werden
entfernt. Unabhängige Closure, 22 Controllergegenproben PASS; keine zusätzliche
Runtime durch diese vorbereitende Korrektur.

C2 C7273FFC05C04F70: NativeClient meldet wörtlich '$(CostFrameFile)': Invalid
filename beim ersten :r vor Kosten-SQL/Indexbau. Ursache über die unverarbeitete
Dateinamenvariable hinaus UNKNOWN, kein Kostenclaim. Beide tatsächlichen
Originalrestores 0/0, neue Attestation, markergebundener Drop, DB-Abwesenheit
und unabhängige eigene Namens-/CID-Abwesenheit PASS; Cleanup 13,5870011 s.
Zwei Kandidaten/zwei Admissionen geschlossen, Budget regulär beendet;
unbenutzte Slots sind keine weitere Korrekturwelle. Öffentlicher Kostenmodus
jetzt mit FAIL_CLIENT_INCLUDE vor jedem SQL/Setup gesperrt. 23 Controller-
gegenproben PASS; unveränderte Kosten-/Selektortests nicht erneut ausgeführt.

Die bekannten DML-/Rebuild-/Storagemodi bleiben verfügbar. Writes/TempDB/Worker,
vollständige IDX-012-Abnahme, Minimalrollen und Hard-Abort bleiben offen.
Checkpoint über PR integrieren; anschließend nächster unabhängiger zulässiger
Schritt: tatsächliche IDX-012-Versions-SKIPs auf 2019/2022 vor Setup. Eine
Kostenwiederaufnahme benötigt einen getrennten endlichen Clientvertrag,
geänderte Eingaben und Quellenclosure nach vollständiger Checkpointintegration;
keine unveränderte Probe, keine stille Budgetrücksetzung. Gesamtworkstream und
Heartbeat aktiv; übrige Provider-/Cloud-/ONNX-Gates bleiben unverändert.

### IDX-012: Benutzererweiterung nach vollständiger PR177-Integration

[PR 177](https://github.com/gecompat/SQL_PerformanceSchulung/pull/177) ist
vollständig abgeschlossen: Head 5a80dbdb6c3cbe7af4928fd843ec97bdd0a6f823 gegen
Base 018c678f55660a559bfd2acc4eb3f56675bce8eb mit 13 SUCCESS;
Squash 4dc956df3f66c21c672e9add30405853bc1e4ca8 mit sieben ausgewählten
Main-SUCCESS (38176790631/38176790669/38176790632/38176790662/38176790708/
38176790645/38176790629). Vollständiger Tree
63adece444541ba2913e7ee33d207a40e2c17ed7 identisch; main/origin/main sauber
synchronisiert, eigener Kostenbranch lokal/remote entfernt. Keine eigenen
Container verblieben. C1/C2 bleiben geschlossene FAILs ohne Kostenframes.

Der Benutzer verlangt jetzt ausdrücklich mehr als zwei Testzyklen. Die
lokale Entwicklungswelle erhält sechs kohärente Test-/Korrekturkandidaten je
Schnitt. Die Kostenfolge verwendet denselben Ledger: C1/C2 zählen mit,
maximal sechs Kandidaten/zwölf serielle eigene Container. Kein unveränderter
Retry nach FAIL; Quellenänderung und gezielte Risiko-Closure erforderlich.
Keine Wiederöffnung alter Ledger und keine Änderung von Provider-/Cloud-/
ONNX-/roten Hostgrenzen. Unbekannter Modell-/Tokenverbrauch bleibt unbekannt.

Unmittelbar läuft die [C3-Clientkorrektur](SQL_SERVER_2025_AI_IDX012_COST_REVIEW.md#benutzererweiterung-und-dritter-kandidat)
auf codex/sql2025-ai-idx012-cost-bundle, Basis 4dc956df3f66c21c672e9add30405853bc1e4ca8.
Feste öffentliche Quellen werden mit vier Batchgrenzen in genau einer
eigenen temporären SQL-Datei bis 160000 UTF-8-Bytes zusammengefügt;
Startupskriptvererbung ist ausgeschlossen. Aufnahme und eigener Cleanup
werden eng unabhängig geprüft; Admission erst danach. SQL-Effekte,
Countersemantik, Originalrestore und 300 s einschließlich Startup/20 s
SQL-Recovery innerhalb 60 s gesamtem Cleanup bleiben unverändert.
28 betroffene Controllergegenproben bestanden. Quellenreview-P2 vor
Admission korrigiert: Die neue Input-Lease verlangt bestätigtes Prozessende
vor Dateientfernung; sonst FAIL_CLEANUP ohne konkurrierende SQL-Recovery.
Unabhängige Closure ohne weitere Befunde erteilt; aktuelle Controllerbindung
5D7964A85FE8041726901A66BA4629633119BDB97491972E25F82F41CF685705 und
Parent EBF13336594B74558567F331E5A7A7BD87C128D47B6388946461067B5E47BB36.
Kein C3-Runtimeclaim vor
tatsächlicher Ausführung. Zwei positive Lifecycles desselben stabilen
Kandidaten erforderlich. Danach konsistenter PR-/Main-/Sync-/Cleanupabschluss
und unmittelbar nächster zulässiger Schritt Versions-SKIPs 2019/2022.
Gesamtworkstream und Heartbeat bleiben aktiv.


C3 bestand anschließend beide vollständigen Kostenlifecycles, Tokens
3E2901DC14FA4A4E/064EB3DBC5FC4B54, tatsächlicher Build 17.0.5005.3 und
WARN_OPTIONAL_EVIDENCE_SKIPPED. Beide Phasen je Lauf liefern vollständige
BEFORE/AFTER-Kostenframes in derselben Session; Session-/TempDB-/eigene
DB-Dateideltas sind tatsächlich erfasst, reine Index-/vollständige
Workerkosten bleiben NOT_ESTABLISHED. Alle DML-/Quellen-/Drop-/Commit-/
Rebuild-/Recall-/Storagekontrollen bestanden. Tatsächliche Originalrestores
und unabhängige Attestation 0/0, markergebundener Drop, neue DB-Abwesenheit,
eigene vollständige CID-/Namensabwesenheit und temporäre Dateiabwesenheit
bestanden; Cleanup 13,7552919/13,3577670 s. Beide C3-Admissionen geschlossen
ohne failure. Kostenfolge nach drei Kandidaten/vier Admissionen beendet;
die freien Zyklen werden nicht ohne neue Frage verbraucht. Historische
C1/C2-FAILs erhalten. [Tatsächliche Werte und Grenzen](SQL_SERVER_2025_AI_IDX012_COST_REVIEW.md#c3-zwei-vollständige-tatsächliche-kostenlifecycles).
Dieser konsistente Stand wird über PR integriert; danach unmittelbar
tatsächliche Versions-SKIPs 2019/2022. Gesamtworkstream und Heartbeat aktiv.


### IDX-012: Versionsfolge nach vollständig abgeschlossener PR178-Integration

[PR 178](https://github.com/gecompat/SQL_PerformanceSchulung/pull/178):
Head 528e770d237e1ac59738fd7712bbf99f4f1b8af7 gegen
Base 4dc956df3f66c21c672e9add30405853bc1e4ca8, alle 13 Headchecks SUCCESS.
Squash 1aead3c727e90d907bf20048e2feebca41642b68, vollständiger Tree
b3e6a389fd9373d4d8180fd6adf73ea3cf533d01 identisch. Alle sieben ausgewählten
Main-Workflows SUCCESS: 38179207709/38179207543/38179207514/38179207439/
38179207560/38179207542/38179207525. main/origin/main sauber synchronisiert;
eigener Kostenbranch lokal und remote entfernt, keine eigenen Container
oder temporären Kosteninputs verblieben.

Unmittelbar folgt der [IDX-012-Versionsnachweis](SQL_SERVER_2025_AI_IDX012_VERSION_REVIEW.md)
auf codex/sql2025-ai-idx012-versions, Basis
1aead3c727e90d907bf20048e2feebca41642b68. Ein stabiler Kandidat muss je zwei
tatsächliche 2019-/2022-SKIPs vor Setup erfüllen. Ausdrücklich erweiterte
lokale Wellenfreigabe: maximal sechs Kandidaten/24 serielle eigene Container;
ein FAIL hält an, Folgekandidat nur bei geändertem Ausführungsinput und
geschlossenem vorherigem Lifecycle. Nach vollständigem Vier-Slot-Nachweis
kein unnötiger Verbrauch weiterer Kandidaten. Vorhandene ursprüngliche
Ledger anderer Schnitte bleiben geschlossen.

Unveränderter öffentlicher Preflight, Controllerdefault ohne Storage-,
Rebuild- oder Kostenflags. Genau eine PREFLIGHT/SKIP/SKIP_VERSION-Phase,
OriginalPreview=None und cleanup_ok=false sind erforderlich; dieses Feld
ist keine SQL-Recovery. Neue read-only DB-Abwesenheit und unabhängige eigene
vollständige CID-/Namensabwesenheit nötig. Kein Preview/MAXDOP/Setup/DDL (Data Definition Language; Anweisungen zum Definieren und Ändern von Datenbankobjekten).
Eigene lokale unveränderliche 2019-/2022-Images, vier CPUs/sechs GiB,
300 s einschließlich Startup und 60 s tatsächlichem eigenen Cleanup.
Secret nur ENV, geerbtes SQLCMDINI entfernt; keine Pulls oder Fremdeffekte.

Enge ursprüngliche Guardclosure und aktuelle Controller-/Parent-/Ledger-
Delta-Closure ohne offene P1/P2 vorhanden, keine Runtime durch den Reviewer.
Nach main-Sync unveränderte SHA256: Preflight C9B56105FF001C49D5C2453D2214105C5BEE569E5976D28DCC1EEC344CE30CD3,
Controller 5D7964A85FE8041726901A66BA4629633119BDB97491972E25F82F41CF685705,
Parent 92D9C91D2F830F7B8DC8D82D2B83979BAF5F4A8FABC135F031E450C65D3F5F2D.
Keine unveränderten Tests/Reviews wiederholen. 28 Controllergegenproben
am selben Quellstand bereits PASS; tatsächliche Versionsruntime erst nach
dieser kanonischen Scopebindung. PR-/Head-/Main-/Tree-/Sync-/eigener Cleanup-
Abschluss erforderlich. Minimalrollen, Hard-Abort und vollständige Abnahme
bleiben Folgearbeit. Gesamtworkstream und Heartbeat aktiv.


Die Versionsfolge bestand alle vier eigenen seriellen Lifecycles desselben
stabilen Kandidaten: zweimal tatsächliches 15.0.4490.9 und zweimal
16.0.4295.3; Tokens D95D67B29CBB4BBA/3BFE11AA071F43BC/
D0D5543990174020/F588C8C09C0941AE. Je genau PREFLIGHT/SKIP/SKIP_VERSION,
keine weitere Phase/kein Setup. OriginalPreview=None und cleanup_ok=false
sind kein SQL-Recoveryclaim. Neuer unabhängiger read-only Client bestätigt
jeweils DB-Abwesenheit; eigene vollständige CID und Name unabhängig abwesend.
Cleanup 11,3410314/10,6015398/12,7354592/12,4055188 s; vier Admissionen
closed=true ohne failure. Quellen und Parent innerhalb C1 bytegleich.
Alle Kandidaten bleiben endlich begrenzt; nach diesem vollständigen Nachweis
keine unnötigen weiteren grünen Proben. [Details](SQL_SERVER_2025_AI_IDX012_VERSION_REVIEW.md#tatsächliche-vier-versionslifecycles).
Konsistenten Stand jetzt über PR/aktuelle Head-/Main-Gates/Tree-/Sync-/
eigene Branchbereinigung abschließen. Unmittelbar danach kontrollierte
IDX-012-Fehler-/Recoveryfälle; Minimalrollen, Hard-Abort und vollständige
Runtime-/TP-PERF-Abnahme bleiben zusätzlich offen. Gesamtworkstream und
Heartbeat aktiv.

### IDX-012: kontrollierte Recovery nach vollständiger PR179-Integration

[PR 179](https://github.com/gecompat/SQL_PerformanceSchulung/pull/179):
Head 7152584274b9037db1e210eb50505f9771ef2f8f gegen
Base 1aead3c727e90d907bf20048e2feebca41642b68, sieben Head-SUCCESS;
Squash 99b8df923f144f6e915ff3718addf24582de7224, voller Tree
8f3b19b9f76f60cfd3e8955708f0af28f1819873 identisch. Alle fünf ausgewählten
Main-Workflows SUCCESS: 38180208984/38180209017/38180208983/38180209019/
38180209001. main/origin/main sauber synchronisiert; eigener Versionsbranch
lokal/remote entfernt, keine eigenen Container verblieben.

Unmittelbar folgt die [kontrollierte IDX-012-Recovery](SQL_SERVER_2025_AI_IDX012_RECOVERY_REVIEW.md)
auf codex/sql2025-ai-idx012-recovery, Basis
99b8df923f144f6e915ff3718addf24582de7224. Ausdrücklich erweiterte lokale
Welle: maximal sechs Kandidaten/24 serielle eigene Container; je stabiler
Kandidat zwei Fehler nach Setup und zwei nach qualifiziertem Indexbau samt
vollständiger unabhängiger Sourceprüfung. Kontrollierter FAIL_EXECUTION
bleibt im Ergebnis FAIL; der Parent attestiert ausschließlich dessen
tatsächlich erwartete Auslösung und vollständige Recovery. Frühere Fehler,
Timeout, ungeklärtes Clientende oder FAIL_CLEANUP erfüllen den Fall nicht.
Vier abgeschlossene stabile Fälle nötig; keine unnötigen weiteren Zyklen.
SQL-Effekte, Originalrestores, 999–1000 Rows, 300 s einschließlich Startup,
20 s SQL-Recovery innerhalb 60 s gesamtem Cleanup bleiben unverändert.
30 betroffene Controllergegenproben PASS. Neuer Fehlerpunkt und Parent
vor Admission eng unabhängig ohne neue P1/P2 geschlossen; aktuelle Bindung
Controller DFBC01CAE5428F279BCE1DF8363ECFF0BCD692A507842A0DD2625DBC5F13D6F1,
Parent F9EB8B93AC5AB947EF2F7B09D3F21E916A5A2A3623B56129735748333C1B2A8D.
Die anschließende tatsächliche Runtime bestand alle vier festen Fälle desselben
C1 auf 17.0.5005.3: Setup-Tokens 0D5DA53FBF6B43CE/D86B5FF43CC246A5,
Build-Tokens 3C04F622FC6D4E14/47C9D7AA36DF4A74. Öffentlich je erwartetes
FAIL/FAIL_EXECUTION mit passendem kontrolliertem Fehlercheckpoint; Parent-PASS
nur für diesen Fall samt tatsächlicher Recovery. Alle Originalrestores/
Attestationen 0/0, neue DB-Abwesenheit und eigene vollständige CID-/
Namensabwesenheit belegt; Cleanup 12,6183559/13,0445620/12,7929698/
12,8262864 s, alle Admissionen geschlossen ohne failure. Nach Build je
vier positive/vier tatsächliche 42231-DML-Kontrollen, voller 999-Row-
Quellen-/Distanzabgleich und vollständige eigene Indexmetadaten vorhanden.
Alle Ausführungsquellen samt Parent innerhalb C1 bytegleich; kein Rebuild.
[Ergebnisdetails](SQL_SERVER_2025_AI_IDX012_RECOVERY_REVIEW.md#tatsächliche-vier-fehler--und-recoverylifecycles).
Kosten-/Versionsledger bleiben geschlossen. Hard-Abort, Minimalrollen und
vollständige Runtime-/TP-PERF-Abnahme bleiben offen. Keine Änderung anderer
Repositories/Provider-/Cloud-/ONNX-/roter Hostgrenzen. Gesamtworkstream und
Heartbeat aktiv; regulärer PR-/Integrations-/Sync-/Cleanupabschluss nötig.


### IDX-012: Rollenfolge nach vollständiger PR180-Integration

[PR 180](https://github.com/gecompat/SQL_PerformanceSchulung/pull/180):
Head d29d3ac2e0f64b4c72fa09af7484031c6bc8d8b3 gegen
Base 99b8df923f144f6e915ff3718addf24582de7224, alle 13 Head-SUCCESS;
Squash 6a8c6ca3835f1f88ae63d6588685f19a675dcb7c, voller Tree
055be4f7410f802376be02f47f8c324affb41120 identisch.
Alle sieben ausgewählten Main-Workflows SUCCESS: 38181778703/38181778718/
38181778753/38181778713/38181778747/38181778711/38181778695.
main/origin/main sauber synchronisiert; eigener Recoverybranch lokal/remote
entfernt, keine eigenen Container verblieben.

Unmittelbar folgt der [eingeschränkte IDX-012-Ausführungskontext](SQL_SERVER_2025_AI_IDX012_ROLE_REVIEW.md)
auf codex/sql2025-ai-idx012-roles, Basis
6a8c6ca3835f1f88ae63d6588685f19a675dcb7c. Ausdrücklich erweiterte lokale
Welle: sechs Kandidaten/zwölf serielle eigene Container, zwei stabile
Rollenlifecycles nach engen tatsächlichen Grant-/Revoke-Gegenproben.
Eigenes Login/SID im eigenen Container, nur CREATE ANY DATABASE und
VIEW SERVER PERFORMANCE STATE, keine feste Serverrolle; eigene DB-Owner-
Bindung und vollständige öffentliche DML-/Rebuild-/Storage-/Kostenfolge.
Admin nur für Fixture und dessen Cleanup, keine sa-Demophase. Neues
SKIP_PERMISSION-Gate vor Host-DMV (Dynamic Management View; dynamische Verwaltungssicht für Diagnoseinformationen)/Setup, übriger Controller unverändert.
Secret nur ENV; tatsächlich gebundener eigener Login-Drop erst nach DB-
Abwesenheit und mit neuem unabhängigem Principal-/SID-Abwesenheitsclient.
300 s inklusive Startup/20 s SQL-Recovery innerhalb 60 s Gesamtcleanup
einschließlich Login-/Containercleanup; keine Fremd-/Host-/Provideränderung.
Noch keine Rollenruntime dieses Scopes. Kein absoluter Minimalitätsclaim,
kein Hard-Abort oder vollständiger Runtime-/TP-PERF-Claim. Vor Admission
enge Quellenclosure und betroffene Gegenproben; regulärer PR-/Integrations-/
Sync-/eigener Cleanupabschluss erforderlich. Workstream und Heartbeat aktiv.

Vor der ersten Rollenadmission enge unabhängige Quellenclosure ohne weitere
P1/P2; zwei P2 zum Phasentupel und konkurrierenden Principal-SQL-Cleanup bei
unbestätigtem Clientende vor Runtime korrigiert. 31 Controllergegenproben und
eine enge rein synthetische Parent-Gegenprobe für genau diesen Unknown-Guard
PASS. Keine Runtime durch den Reviewer. Aktuelle Quellenbindung: Preflight
7FC2A900E2419CDF10590145270F3A06377CBB6A8A49E6E6836860EEE36DB684,
Controller unverändert DFBC01CAE5428F279BCE1DF8363ECFF0BCD692A507842A0DD2625DBC5F13D6F1,
Parent 59B6EF00AFF65FF42B8FD6BFE6EE84AB475E8223BCC32594739B1F9C02C81736.

Tatsächlicher C1-Rollenlauf 803B41BD338040B1 geschlossen FAIL: Rechteentzug-
Gegenproben/Grantrestore, Setup/Owner/Baseline/Storage/Kosten-BEFORE und vier
NO_INDEX-DML-Kontrollen bestanden; Indexbau verweigert internen DBCC TRACEON
mit 2571/State 3, anschließend 42234/State 1. Kein Rollen-/Index-/Rebuild-PASS.
Originalrestores/Attestation 0/0, neue DB-Abwesenheit, tatsächlicher eigener
Login-Drop/neue Principal-/SID-Abwesenheit und voller CID-/Namenscleanup
bestanden (13,0928537 s). Ein tatsächlicher Versuch verbraucht, kein zweiter
unveränderter Lauf. [FAIL und Quellenabgleich](SQL_SERVER_2025_AI_IDX012_ROLE_REVIEW.md#tatsächlicher-erster-fail-und-begrenzte-kontexttrennung).
Innerhalb desselben Sechskandidatenledgers folgt C2 mit geändertem festen
Parent/privater Kontextquelle: nur die beiden vorhandenen Indexbuilds unter
sa, kontrollierte DML/Beobachtung vor/nach jeweils unter tatsächlichem
Operator mit vier geordneten Kontext-/SID-Records pro Kostenphase. Kein
sa-Fallback, keine zusätzlichen Operatorgrants; kein öffentlicher unveränderter
Einzel-Login- oder vollständiger Nicht-sysadmin-Buildclaim. Native Quellen-
bytes/Hashes privat aufnehmen; drei betroffene synthetische Gegenproben PASS,
enge Delta-Closure vor Admission erforderlich. Alle alten FAILs/Grenzen und
gesamte Deadline/ClientEndUnknown-Eigentumsfloors bleiben erhalten.

Enge unabhängige C2-Closure vor Admission ohne P1/P2 zur konkret neuen
Identitäts-/Native-Input-Grenze erteilt. Aktueller Parent
F0341668E58E5FD6C0E00E09DA21579F5B694D8F6C2E44A0944C77E20FA0451A,
feste Kontextquelle E320B1D61E1599C6A63017D15D40575D19D1548FFB5DA0DF42F61272979E3E76.
Privilegierter Kontext nur der exakt erkannte einzelne Index-DDL je Phase;
geordnete Operatorrückkehr, Secret-/Token-/SID-/Lease-/Größenfloors bestätigt.
Keine Runtime oder Tests durch den Reviewer; Closure vor C2-Admission.

C2/A16779D9D401423E geschlossen FAIL_EXECUTION: Msg 156 am unquotierten
reservierten Alias Checkpoint in der ersten nativen Kontextquelle, keine
tatsächlichen Kontext-/Index-/DML-/Rebuild-Ergebnisse. Beide Rechtegegenproben,
Grantrestores und DB-Ownerbindung bestanden; Originalrestores/Attestation 0/0,
neue DB-Abwesenheit, eigener Login-Drop mit neuer Principal-/SID-Abwesenheit
und volle CID-/Namensabwesenheit bestanden (13,0965515 s Gesamtcleanup).
Zwei geschlossene Fehlkandidaten bleiben im selben Sechskandidatenledger.
C3 korrigiert ausschließlich [Checkpoint], Kontextquelle
F78446CF632378D3A2CE31357D2E75879765B75AC9459C8C9161878D3C4B89D0,
Parent unverändert. Drei betroffene synthetische Gegenproben PASS; enge
unabhängige Syntaxdelta-Closure vor Admission erteilt, ursprüngliche C2-
Identitäts-/Privileg-/Lease-/Cleanupsemantik unverändert. Kein neuer
Benutzerfreigabezyklus innerhalb der ausdrücklich erweiterten lokalen Welle.


IDX-012-Rollensplit C3 tatsächlich mit zwei stabilen vollständigen Lifecycles
bestanden: F2BED8B1B7FB4008/CA7DFACE4C9F47D3 auf 17.0.5005.3, sämtliche
Ausführungsquellen und native Eingabebytes gleich. Je beide einzeln entzogenen
Rechte vor Setup SKIP_PERMISSION, tatsächliche Grantrestores/DB-Ownerbindung;
acht geordnete Kontext-/SID-Records, Admin nur für beide Indexbuilds,
DML/Beobachtung/Drop/Commit/Kosten unter Operator; vier positive/vier 42231-
DML-Kontrollen, vollständige 999-Row-Quellenkontrolle, fünf Rebuild-Suchen mit
Recall@5 1 und übrige 998 Texte gleich. Drei Speicherpunkte/zwei Kostenfolgen
mit unveränderten Grenzen; öffentliche Ergebnisse WARN, Generation UNKNOWN,
runtime_qualification NOT_ESTABLISHED. Tatsächliche Restores/Attestation 0/0,
neue DB-Abwesenheit, eigener Login-Drop und neue Principal-/SID-Abwesenheit,
volle eigene CID-/Namensabwesenheit bestanden; Cleanup 13,4958547/13,7201669 s.
C1/C2 FAIL bleiben im selben Ledger; vier eigene Container entfernt. Keine
weitere identische grüne Admission. [Teilnachweis](SQL_SERVER_2025_AI_IDX012_ROLE_REVIEW.md#tatsächliche-zwei-stabile-rollenlifecycles-c3).
Öffentliche Multi-Login-API/absolute Minimalrollen/Hard-Abort und Gesamt-/
TP-PERF-Abnahme bleiben offen. Nächster Schritt: reguläre PR-Integration
gegen aktuelle Basis, alle Head-/Main-Gates, Tree-/Sync-/eigener Branchcleanup;
danach unmittelbar nächster zulässiger lokaler Schnitt. Workstream aktiv.

PR 181 vollständig geschlossen: Head fa74265781803fd41a8310d41b5e7f38f8cbfe59
gegen Basis 6a8c6ca3835f1f88ae63d6588685f19a675dcb7c, alle 13 Head-Checks SUCCESS;
Squash 7acf4c27868285ad08872f3e954c19347f0f7c6d, vollständiger Tree
b0f0144b8fd8e98dd90cd0d2ed9a0e4ea43e9f9d exakt identisch. Alle sieben Main-
Workflows SUCCESS: 38184152108/38184152119/38184152145/38184152159/38184152171/
38184152093/38184152149. main/origin/main per FF sauber synchronisiert;
eigener Rollenbranch lokal/remote entfernt, keine eigenen Container verblieben.

Unmittelbar folgt der [begrenzte eigene Containerabbruch](SQL_SERVER_2025_AI_IDX012_HARD_ABORT_REVIEW.md)
auf codex/sql2025-ai-idx012-hard-abort, Basis 7acf4c27868285ad08872f3e954c19347f0f7c6d.
Nur idle Container-SIGKILL nach qualifiziertem fertiggestelltem Index-/Source-/
Snapshotcheckpoint und beendetem Client; gleicher vollständig gebundener CID
und tatsächlicher neuer Wiederanlauf, danach neue read-only Snapshot-/Source-
Kontrollen und unveränderte Originalrestores/markergebundener Cleanup.
Sechs Kandidaten/zwölf serielle eigene Container, zwei stabile Lifecycles,
gesamter Cleanup 60 s bereits vor Kill ohne Reset; öffentlicher SQL-Recovery-
Vertrag 20 s bleibt erhalten. Keine aktive DDL-/vollständige Hard-Abortabnahme.
Noch keine Admission; enge Quellenclosure für Signal-/Restart-/Deadline-/
ClientEndUnknown-Grenze vor Runtime erforderlich. Workstream/Heartbeat aktiv.

Vor Admission enge unabhängige Quellenclosure erteilt ohne weitere P1/P2.
Collector-/Pollausnahmen mit unbestätigtem Ende verwenden ClientEndUnknown;
Review-P2 vor Runtime geschlossen, neun betroffene rein synthetische
Gegenproben PASS (fünf Restart-, vier tatsächliche ClientEnd-/Recoveryfälle).
Parent 2A7DF31DB4C573248B3B51C5E5D56762FDD0A13E1CAB56F49D1C86BED4503454,
Restarthelper 27858DFD1D2050E3E4A1DD8E4D27765E29B9C84EE7DF7316E69734C144C52D9B;
öffentlicher Controller DFBC unverändert. Kein SQL/Container durch Reviewer.


IDX-012 eigener idle Container-SIGKILL tatsächlich zweimal auf stabilen C1-
Quellen bestanden: F92CEAC8A7614EAB/3EF8E51FAD3B4BE8. Vor Kill jeweils
qualifizierter Index-/vollständiger 999-Row-Source-/Snapshotcheckpoint und
bestätigt beendeter Arbeitsclient. Tatsächlicher Exit 137 ohne OOM, neuer
Start desselben gebundenen CID/neue Readiness, neue vollständig identische
Snapshot-/Source-/Indexrecords samt Originalbaseline 0/0 und aktuellem 1/1.
Öffentlich je kontrolliertes FAIL_EXECUTION; tatsächliche Originalrestores/
Attestation 0/0, neuer DB-Abwesenheitsclient und eigene volle CID-/
Namensabwesenheit bestanden. Gesamtes Cleanup ab vor Kill einschließlich
Restart/read-only/SQL-Restore/Containerabbau 19.4342235/19.3921410 s,
keine Deadline zurückgesetzt; beide eigenen Container entfernt.
[Begrenzter Teilnachweis](SQL_SERVER_2025_AI_IDX012_HARD_ABORT_REVIEW.md#tatsächliche-zwei-stabile-containerabbruch-lifecycles).
Aktive Build-/DML-/Rebuild-Unterbrechung und vollständige Hard-Abort-/Runtime-/
TP-PERF-Abnahme bleiben offen. Nächster Schritt: aktuelle Head-/Main-Gates,
PR-Integration/Tree-/FF-Sync-/eigener Branchcleanup, danach nächster
zulässiger lokaler Schnitt. Workstream und Heartbeat aktiv.


## CON-010-Wiederaufnahme nach Erweiterung der Testzyklen

Unmittelbar nach vollständigem PR-182-Abschluss folgt der begrenzte private
TSK-009-/CUR-018-Schnitt CON-010 auf codex/sql2025-ai-con010-resume,
Basis 9a9c0e957a1444d79f936c8cc1bcb9b83839435a. PR 182 hatte 13 aktuelle
Head- und sieben Main-Gates erfolgreich; vollständiger Tree
35ef8a41a67180fc8cc1543c5585910cab4201de, lokales main synchronisiert,
eigener lokaler/Remote-Branch entfernt. Idle-SIGKILL bleibt Teilnachweis;
Abbruch während aktiver DDL aus TSK-006 weiterhin offen.

Benutzerfreigabe erweitert auf sechs kohärente Test-/Korrekturkandidaten.
Drei historische vollständige CON-010-FAILs und zwei Metadatenproben werden
weitergezählt. C4 korrigierte die vollständige Rechtefixture, scheiterte
jedoch nativ in Setup mit Kollationsfehler 468; actual Cleanup/DB/CID/Name
PASS. C5 korrigiert ausschließlich Statebytes und bestand zwei vollständige
Lifecycles mit je zwei Setups und sechs Resultassertions. Alle sechs
CONNECT-/SELECT-Grants einschließlich Klassen, Ziel, Grantor, Zustand und
vollständigen Bytes sind exakt gebunden; RLS (Row-Level Security; zeilenbezogene Zugriffskontrolle)/Funktions-/Quellen-/Vektoren-
oracles sowie drei tatsächliche Rechteverweigerungen und Reset bestanden.
Cleanup und unabhängige DB-/CID-/Namensabwesenheit unter derselben 60-s-
Deadline PASS. Quellen-/Test-/Review-/Verbrauchsgrenzen im
[begrenzten Wiederaufnahmenachweis](SQL_SERVER_2025_AI_TENANT_RESUME_REVIEW.md).

Die alte Abbruchgrenze wird ausschließlich durch die neue menschliche
Wellenautorität übersteuert; kein stilles Zurücksetzen, kein C6 nach grünen
Pflichtwiederholungen. Enger unabhängiger Quellenreview, konkreter P2 vor
Admission geschlossen, C5-Statebyte-Delta geschlossen. Sechs rein synthetische
Endstatus-/Recoverytests PASS, kein wiederholter grüner Altcheck.
CON-010 bleibt PROPOSED. Nächster zulässiger Schnitt nach diesem PR-/Main-/
Sync-/Cleanupabschluss: öffentliche Demoeinbindung mit vollständigen
Marker-/Fixturegegenproben und 2019-/2022-Versionsgrenzen; Pooling/echte
Logins/ANN bleiben getrennt. Provider-/Cloud-/ONNX-/rote Hostgrenzen bleiben.


## CON-010: öffentliche Demo und tatsächliche Gegenproben

Nach vollständigem PR-183-Abschluss unmittelbar nächster TSK-009-Schnitt auf
codex/sql2025-ai-con010-public, Basis d43a1c0303ad18e26cecc63a9c944f5b7ca8bf16.
PR 183: sieben aktuelle Head-/fünf Main-Gates erfolgreich, vollständiger Tree
f6f1480bd96ab29adbdb754b45cbb2e31b1d682b, lokales main FF-synchronisiert,
eigener lokaler/Remote-Branch entfernt. Historische CON-010-FAILs unverändert.

Neuer öffentlicher Consumer mit sechs Kandidaten/maximal 30 seriellen eigenen
Containern. C1: vier Versions-SKIPs und 192 Markerabweisungen bestanden; FAIL
an wirkungslosem zusätzlichem Spalten-SELECT unter Tabellen-SELECT. Tatsächlicher
Cleanup/neue DB-/vollständige CID-/Namensabwesenheit bestanden. C2 änderte nur
Spalten-DENY und verlangt vollständige Snapshotänderung vor jeder Mutation.
Alle 16 tatsächlichen Source-/Policy-/Rechte-/Rollenmanipulationen mit exakt
51003/FAIL_RESULT_CONTRACT gegen Baseline und Comparison abgewiesen; alle
192 Markerproben mit exakt 51004/FAIL_STATE über acht Phasen abgewiesen,
vollständige Snapshots unverändert und tatsächliche markergebundene Reparatur.
Setup zweimal semantisch gleich; je zweimal echte 2019-/2022-SKIPs vor Setup.
Alle zehn eigenen Container vollständig geschlossen, DB/CID/Name neu abwesend;
Cleanup jeweils unter gemeinsamer 60-s-Deadline. Keine rohe Diagnose veröffentlicht.

CON-010 jetzt IMPLEMENTED unter vorhandener Registryidentität; neunte lokale
KI-Demo. 32 Demos/372 Runs bleiben geplanter Providerkatalog, keine Vollausführung.
Neue Consumerabhängigkeit in beiden Workflowpathsets, mutierende CI unverändert
cancel-in-progress=false. Ein Owner/enger Risiko- und Deltaquellenreview; zwei
P2 vor Admission geschlossen, wirkungslose native Probe wahrheitsgemäß FAIL.
Sechs synthetische Endstatus-/neun öffentliche Runnermethoden und betroffene
Framework-/Guide-/Katalog-/Selektorgates PASS. Modell-/Tokenverbrauch unbekannt.

[Gebundener öffentlicher Nachweis](SQL_SERVER_2025_AI_TENANT_IMPLEMENTATION_REVIEW.md).
Aktuelle Head-/Main-Gates, PR-Merge, vollständige Treeübernahme/FF-Sync und eigener
Branchcleanup sind vor Schnittabschluss erforderlich. Pooling, authentifizierte
Serverlogins, mehrere Sessions, ANN/Postfilter, Seitenkanäle und TSK-009-Gesamtabnahme
bleiben offen. Nächster unabhängiger lokaler Schnitt nach vollständiger Integration:
RES-008-Quellen-/Dimensions-/Storagevorbereitung aus TSK-010, mit begrenztem
synthetischem float32-Profil; keine Cloud-/ONNX-/rote Hostwirkung oder Wiederaufnahme
anderer Workstreams. Heartbeat bleibt Wiederaufnahmeabsicherung des aktiven Auftrags.


### CON-010 C3: korrigierter öffentlicher Ausgabekanal

PR 184 ist noch offen. Head 4c28f5d2f0c10efd1cc1af80bc1ea4a35a677a7c:
SQL-AI-CI 38188982540 FAIL nach zwei positiven regulären CON-010-Lifecycles,
vor Setup des Gegenprobenconsumers; PRINT war durch -r 1 nach stderr geroutet,
API lieferte stdout. Eigener CI-Container bereinigt, kein Merge dieses Heads.
Andere zwölf ausgewählte Head-Workflows abgeschlossen erfolgreich.
C3 korrigiert optionalen API-Diagnostikkanal/gezielte Consumer-Summaries und
strukturierten ValueError-FAIL. Alle fünf festen C3-Slots unter tatsächlichen
öffentlichen Ausgabeoptionen bestanden: 192 Marker-/32 Resultabweisungen,
16 tatsächliche Mutationen, Setupidempotenz und je zwei 2019-/2022-SKIPs.
Alle 15 eigenen Container samt DB/CID/Name neu abwesend, Endstatus bekannt;
alle historischen FAILs bleiben im gemeinsamen sechs-Kandidaten-Ledger.
Enger C3-Deltaquellenreview vor Admission geschlossen, sieben synthetische
Endstatus-/elf öffentliche Runnermethoden PASS. Keine geänderten SQLoracles.
Aktuelle korrigierte Head-/Main-Gates, Integration/FF-Sync/eigener Branchcleanup
folgen vollständig; nächster unabhängiger Schnitt weiterhin RES-008. Keine
TSK-009-/Provider-/Pooling-/Gesamtabnahme, Modell-/Tokenverbrauch unbekannt.


### CON-010 C4: gemeinsame API wiederhergestellt

C3 lokal PASS, anschließend Head c720508 im Offline-CI 38190655438
FAIL/PYTHON_PROFILE_CHANGED an eingefrorener gemeinsamer API-Abhängigkeit;
kein Merge. C4 stellt gemeinsame API exakt auf Baseline zurück und projiziert
ausschließlich die feste positive CON-010-Consumersummary per SELECT auf stdout.
Keine Migration pausierter Workstreams/Profiles; reguläre Demo-SQLbytes und
SQL-/RLS-/Grant-/Fehleroracles unverändert. Alle fünf C4-Slots bestanden:
192 Marker-/32 Resultabweisungen, 16 tatsächliche Mutationen, Setupidempotenz,
je zwei 2019-/2022-SKIPs vor Setup. Alle 20 eigenen Container samt DB/CID/Name
neu abwesend, Endstatus bekannt, Cleanup unter derselben 60-s-Deadline.
Alle historischen nativen-/CI-FAILs im selben sechs-Kandidaten-Ledger erhalten,
keine weitere unveränderte grüne Wiederholung. Enger C4-Review geschlossen,
elf öffentliche Runner-/sieben private Endstatustests PASS. Aktuelle C4-
Head-/Main-Gates/Integration/FF-Sync/eigener Branchcleanup erforderlich; danach
unmittelbar RES-008-Vorschnitt. Kein TSK-009-/Pooling-/Provider-Gesamtabschluss.


## RES-008: private Dimensions- und Storagevorbereitung

PR 184 vollständig abgeschlossen: Head 7f37469c0b83ae36618cd26b5b12133930b8c78b
mit 49 erfolgreichen Checks/13 ausgewählten Workflows, Squash
84aef7016cc86194281805adc29ae9bc15fcec2f mit elf erfolgreichen Main-Workflows.
Vollständiger Tree 1418d4f9f9786dba176759d499ed53a19db11423 gleich übernommen;
lokales main FF-synchronisiert, sauber, eigener lokaler/Remote-Branch entfernt.
Die vorstehenden C2-/C3-CI-FAILs bleiben historische Befunde ihrer Heads.

Unmittelbar folgte codex/sql2025-ai-res008-preparation auf dieser Main-Basis.
TSK-010/CUR-020, RES-008 weiterhin PROPOSED. Sechs Kandidaten/maximal zwölf
eigene serielle Container; ein Owner, enger unabhängiger Quellenreview und
C2-Deltaclosure vor Admission. C1 nach Setup FAIL/8124 an äußerer Referenz in
Komponentenaggregat, tatsächlicher SQL-/DB-/Containercleanup bestanden.
C2 änderte nur vier Oracleprüfstellen; zwei vollständige Lifecycles bestanden.
Je drei vollständige Aufnahmen aller 400 Rows in vier float32-Dimensionen,
Storage/Metadaten/vier Suchkontrollen, Setupidempotenz, tatsächliche DELETE-
Quellengegenprobe mit exakt 51003 und vollständiger Restore bestanden.
DB-Optionen 0/0 erhalten; Cleanup aller drei DBs/Container unabhängig belegt,
bekanntes natives Ende und dieselbe 60-s-Deadline ohne Reset. Private Ledger,
Sourcebytes und Rohlogs bleiben ignoriert; keine weitere grüne Wiederholung.

[Gebundener Teilnachweis](SQL_SERVER_2025_AI_RESOURCE_DIMENSION_REVIEW.md).
Aktuelle Head-/Main-Gates, PR-Merge, vollständige Treeübernahme, FF-Sync und
eigener Branchcleanup folgen vor Abschluss. CPU/Elapsed/Memory/Plans, AB/BA/AA,
Loader/Modellqualität, ältere Engines und öffentliche Demo-/TP-PERF-Abnahme
bleiben offen. Nächster zulässiger lokaler Schritt nach vollständiger Integration:
RES-008-Messmethodenerweiterung. Kein Workstream-Gesamtabschluss; Heartbeat aktiv,
Cloud-/ONNX-/rote Hostgrenzen unverändert, Modell-/Tokenverbrauch unbekannt.


## RES-008: begrenzte private Messfenster

PR185 vollständig abgeschlossen: Head 4f29e564d2602fa38cafcf0ae5a89775425ec07b
mit sieben Head-Workflows, Squash a3bfb66fb032c292b604fa939d27a211ded19ecb
mit fünf Main-Workflows PASS. Vollständiger Tree f7ce3e181fdfdba2c916e828061bdda2db76a8cd
gleich übernommen; lokales main FF-synchronisiert und sauber, eigener lokaler/Remote-Branch entfernt.
Unmittelbar codex/sql2025-ai-res008-measurement gestartet, TSK-010/CUR-020.

Neue konkrete Messfrage mit sechs Kandidaten/maximal zwölf eigenen seriellen
Containern; C1 FAIL am groben DMV-/feinen Fensterzeitvergleich erhalten,
tatsächlicher eigener SQL-/DB-/CID-/Namenscleanup PASS. C2 ändert nur diesen
unbegründeten Cross-Type-Vergleich, rohe Requestidentity und tatsächliche
Counter-/UTCdeltas/Nichtüberlappung voll erhalten. Zwei vollständige stabile
Lifecycles mit je 20 Warmups, 54 AB-/BA-/AA-Fenstern und 5420 einzelnen Queryoracles
bestanden; alle Fenster gegen unabhängig attestierte eigene DB-ID und volle
native Chunkframes gebunden. Tatsächliche SourceDELETE-/Querymutationsnegative
mit exakt 51003, acht vollständige 400-Row-/Config-Aufnahmen und Restore gleich.
Eigener Cleanup aller drei Container/DBs unter unveränderter 60-Sekunden-Deadline.

[Gebundener Teilnachweis](SQL_SERVER_2025_AI_RESOURCE_MEASUREMENT_REVIEW.md).
Ein Owner, enger Source- und C2-Delta-Review geschlossen, 18 betroffene synthetische
Cases PASS. Keine weitere grüne Wiederholung; Runtime-/Sourcebytes privat ignoriert.
Aktuelle Head-/Main-Gates, PR/Integration/Treeübernahme/FF-Sync/eigener Branchcleanup
folgen vor Abschluss. Danach unmittelbar begrenzte Plan-/Memoryaufnahme für RES-008.
RES-008 PROPOSED, TSK-010/TP-PERF/Worker-/Provider-/Gesamtabnahme offen. Kein
Cloud-/ONNX-/roter Hosteffekt, Modell-/Tokenverbrauch unbekannt, Heartbeat aktiv.

## RES-008: repräsentative tatsächliche Pläne

PR186 vollständig abgeschlossen: Head 78f9747209ca0aea52508bcb6a584ff431816841
mit sieben aktuellen Head-Workflows, Squash e8fb5d801464e5e2acb37fdeef5f7d203c048cb3
mit fünf aktuellen Main-Workflows PASS. Vollständiger Tree
e0ab4de7a0cca55a92bdc91909dfebdc469cc47f gleich übernommen, lokales main
FF-synchronisiert und sauber, eigener lokaler/Remote-Branch entfernt.
Unmittelbar codex/sql2025-ai-res008-plans gestartet, TSK-010/CUR-020.

Neue konkrete Planfrage mit sechs Kandidaten/maximal zwölf eigenen seriellen
Containern. C1 FAIL am fehlenden tatsächlichen Ergebnisrootzähler erhalten;
eigener SQL-/DB-/CID-/Namenscleanup bestanden. C2 ändert nur direkte Id-/Distanz-
projektion und deren exakte Statement-/Rowauswertung; Root-/Scan-/Threadguards
erhalten. Enge unabhängige P2-Closure und 24 synthetische Gegenfälle bestanden.
Zwei vollständige stabile Lifecycles mit je vier tatsächlichen Exact-Plänen,
eigener Scan mit 100 Rows, Ergebnisroot mit einer Row und Id 1/Distanz 0,
acht Raw-/Recordbindungen und elf vollständige 400-Row-Aufnahmen über alle drei
Lifecycles bestanden. Tatsächliche DELETE-Gegenprobe mit 51003 und Restore, idempotentes zweites
Setup, volle Source-/Configgleichheit und unabhängiger eigener Cleanup.

[Gebundener Teilnachweis](SQL_SERVER_2025_AI_RESOURCE_PLAN_REVIEW.md).
Tatsächliche Memoryattribute veröffentlicht; Compute-Scalar-RuntimeRows und
Waits/Warnings NOT_CAPTURED, Roh-DOP 0 ohne Umdeutung. Keine Aussage über alle
früheren Messfenster oder fehlende Spills/Waits; Zeit-WARNs bleiben sichtbar.
Keine weitere grüne Wiederholung; Runtime-/Sourcebytes privat ignoriert.
Aktuelle Head-/Main-Gates, PR/Integration/Treeübernahme/FF-Sync/eigener Cleanup
folgen vor Abschluss. Danach unmittelbar öffentliche RES-008-Demoqualifikation
unter getrennten Performancegrenzen. RES-008 PROPOSED, TSK-010/TP-PERF/
Worker-/Provider-/Gesamtabnahme offen. Kein Cloud-/ONNX-/roter Hosteffekt,
Modell-/Tokenverbrauch unbekannt; Heartbeat aktiv.

## RES-008: öffentlicher begrenzter Consumer

PR187 vollständig abgeschlossen: Head 334f91f743081c7c73ff1d823715e011227dec6c
mit sieben aktuellen Head-Workflows, Squash 1891b35d81dcdc61274a4a738994c3b25aa09dd4
mit fünf aktuellen Main-Workflows PASS. Ganzer Tree d516ca9e6fc919c5c05bc8bf4a83fe32e5871b04
gleich übernommen, lokales main per FF sauber, eigener lokaler/Remote-Branch entfernt.
Unmittelbar codex/sql2025-ai-res008-public gestartet, TSK-010/CUR-020.

Öffentlicher Controller mit sechs Kandidaten/maximal 42 eigenen seriellen
Containern für sieben feste Slots. C1 alle sieben lokal bestanden: vier tatsächliche
2019-/2022-SKIPs vor Setup, zwei vollständige SQL-17.0.5005.3-Profile mit je
20 Warmups, 54 AB-/BA-/AA-Fenstern, 5420 einzelnen Queryoracles und vier Actual-
Plänen; tatsächlicher eindeutig attestierter Fault nach PASS-Setup mit Recovery.
Zehn vollständige 400-Row-Aufnahmen gleich, Source-/Querynegative exakt 51003,
Restore, Setupidempotenz, DB-Konfiguration 0/0 und unabhängiger eigener Cleanup.
148 native Fenster und acht native Pläne exakt gegen vollständige Records gebunden.

[Öffentlicher Teilnachweis](SQL_SERVER_2025_AI_RESOURCE_PUBLIC_REVIEW.md).
15 Controller-/24 Plan-/18 Messgegenfälle und enger unabhängiger Abschluss
dreier konkreter P2 vor Admission bestanden. Private Launcherimportkollision
vor Admission korrigiert, kein damaliger Container-/SQL-Effekt; historische
Source-/Mess-/Plan-FAILs bleiben erhalten. Keine unveränderte grüne Wiederholung.
Öffentliche gemeinsame API unverändert; neue CI prüft den öffentlichen
Consumer-/Shim-/Prozesspfad, Pflicht-SKIPs und WARNs sowie eigenen Cleanup.

CI-C1 (Head ba65cf386e028cb2e8e2b5efcc91142b146d1726, Run 38199574328)
FAIL am bisherigen Containerproxy: zusätzliche RES-008-Optionen nicht akzeptiert,
2019/2022 mit unabhängiger Containerentfernung, öffentliche SQL-Abwesenheit
dabei nicht qualifiziert. CI-C2 ändert nur den eigenen Adapter und dessen Auswahl
im neuen Runner; gemeinsame API/Proxy und SQL-/Controllerbytes unverändert.
Drei neue Argument-/ENV-/stdin-/Exitcodegegenfälle bestanden. Beide CI-Kandidaten
werden im erweiterten Sechskandidatenbudget erhalten; aktueller CI-Nachweis folgt.

Aktuelle Head-/Main-Gates, PR/Integration/Treeübernahme/FF-Sync/eigener Branchcleanup
folgen vor Abschluss. Danach unmittelbar begrenzte öffentliche Aggregation/
Ergebnisinterpretation aus den bereits vollständigen Records ohne erneute
unveränderte SQL-Läufe. RES-008 PROPOSED, neun lokale Demopakete IMPLEMENTED;
vollständige FWK-011-/Demo-/TP-PERF-/TSK-010-/Modul-/Workstreamabnahme offen.
Keine Cloud-/Modell-/ONNX-/rote Hostwirkung, kein anderes Repository verändert;
Modell-/Tokenverbrauch unbekannt, Heartbeat aktiv.


## RES-008: begrenzte öffentliche Aggregation

PR188 vollständig abgeschlossen: Head b2c55911994db6460a15e27e2b5b3ca32390ac0b,
zwölf aktuelle Head-Workflows; Squash 192fcd945d1408bf6509263600af7beb2bb83c4d,
zehn aktuelle Main-Workflows PASS. Ganzer Tree 151bd6af448e7b6153b23c5a7b69f63d9f7353d6
gleich übernommen, main FF-synchronisiert/sauber und eigener lokaler/Remote-Branch
entfernt. CI-C1 auf allen drei Versionen FAIL am Proxy erhalten, Containercleanup
bestanden; eigener CI-C2-Adapter mit aktuellem Public-PASS/SKIP/WARN/Recoverypfad.
Unmittelbar codex/sql2025-ai-res008-aggregation begonnen, TSK-010/CUR-020.

[Gebundene Aggregation](SQL_SERVER_2025_AI_RESOURCE_AGGREGATION_REVIEW.md):
exakte 20-Warmup-/54-Fensterpopulation, sechs A/B-Batchfenster je Pfad/Paar, AA
separat; nullbedingtes N/A, Nullzählungen und Ausreißer sichtbar. 148 vorhandene
Raw-Windowframes und acht Raw-Pläne exakt gebunden, zwei begrenzte Auswertungen
mit je 30 numerischen FWK-011-Invarianten bestanden, keine neuen lokalen SQL-Läufe.
25 reine Populations-/Counter-/Oracle-/Plan-/Privacy-/FWK-Gegenfälle und drei
öffentliche CLI-Fälle bestanden. Konkreter unabhängiger Assertionbinding-P2
geschlossen; keine Reviewer-Tests/-Runtime oder Reviewkette. Gesamt-WARN,
PROPOSED und offene volle Worker-/TP-PERF-/TSK-010-/Modulabnahme erhalten.

CLI --summary optional nach positivem bekanntem Controllerabschluss, keine
Rawdiagnosepersistierung; CI bewertet die neue Aggregation am öffentlichen
nativen Consumer und erhält vollständigen eigenen Cleanup. Aktuelle Head-/Main-
Gates, PR/Integration/Treeübernahme/FF-Sync/eigener Branchcleanup folgen vor
Abschluss. Danach begrenzte Teilnehmer-/Traineraufgabe zu diesem Teilprofil
unter TSK-012 ohne SQL-Retry/volle didaktische Abnahme. Keine Cloud-/Modell-/ONNX-/
roten Hosteffekte oder andere Repositoryänderung; Verbrauch unbekannt,
Heartbeat aktiv; sechs kohärente Kandidaten je lokalem Schnitt bleiben autorisiert.


## RES-008: begrenztes Teilnehmer- und Trainermaterial

[PR189](https://github.com/gecompat/SQL_PerformanceSchulung/pull/189) vollständig
abgeschlossen: Head 88a9d60f640fc9984c61cdb7a9be0703ba6b1d37, neun aktuelle Head-Workflows PASS;
Squash eab09f6e8de580e9087f214e07bdaf62283a9690, sieben aktuelle Main-Workflows PASS.
Ganzer Tree 2418eb0933d76903d98644f7ffef392aa67d68bb exakt übernommen, main FF-synchronisiert/sauber;
eigener lokaler/Remote-Branch entfernt. Öffentliche 2025-Aggregation in Head/Main
je zweimal mit 30 numerischen FWK-PASSs bei Gesamt-WARN, tatsächlicher Setupfault-
Recovery und eigenem Cleanup; Versions-SKIPs vor Setup erhalten. Abschließende
Dokumentpräzisierung trennt UTC-Schleifenzeit von umgebenden Request-Countergrenzen.
Unmittelbar codex/sql2025-ai-res008-teaching begonnen, TSK-012/CUR-020.

Das bestehende [Arbeitsheft](../HowTo/SQL_SERVER_2025_AI_OFFLINE_WORKBOOK.md#ergänzende-ergebnisleseaufgabe-res-008)
und der [Trainerleitfaden](../HowTo/SQL_SERVER_2025_AI_OFFLINE_TRAINER_GUIDE.md#getrennte-ergänzung-res-008-ergebnisse-lesen)
enthalten eine getrennte Ergebnisleseaufgabe aus den bereits gebundenen Beobachtungen:
20 Warmups, 54 Messfenster, 74 Requests, 5420 Querykontrollen; sechs A/B-Fenster
je Pfad/Paar, AA separat. Batch-/Counter-/UTC-Grenzen, N/A/Nullwerte/Ausreißer,
beschränkte FWK-Invarianten und fehlende Modellqualität sind Aufgaben und Lösung.
Die einzige Lösung/Rubrik bleibt im Arbeitsheft; acht Basisübungen maximal 16 Punkte,
getrennte optionale Ergänzung 0–2 Punkte. Keine neuen SQL-Läufe oder didaktischen
Istwerte; tatsächliche Teilnehmererprobung, Lehrzeiten, Masterdeck/Notes/Render und
Generalprobe offen. Historische FAILs und aktuelle ANN-Teilqualifikation unterschieden.

Quellen-, Link-, Sprach-, Privacy- und Diffprüfung für diese Dokumentänderung;
aktuelle Head-/Main-Gates, PR/Integration/Treeübernahme/FF-Sync/eigener Branchcleanup
folgen vor Abschluss. RES-008 PROPOSED/Gesamt-WARN und volle TP-PERF-/Modulabnahme
bleiben offen. Danach unmittelbar nächste unabhängige kanonische Teilaufgabe;
allgemeine Entwicklung/DGN-007 bleiben pausiert. Keine Cloud-/Modell-/ONNX-/roten
Hosteffekte, kein anderes Repository verändert. Sechs kohärente Kandidaten je
lokalem Schnitt autorisiert; Modell-/Tokenverbrauch unbekannt, Heartbeat aktiv.


## DGN-010: begrenzte private Actual-Planqualifikation

PR190 vollständig abgeschlossen: acht aktuelle Head-/sechs Main-Workflows PASS;
Head 71aa155ad6e86fdd4490534e22969ddaf92f2089, Squash e7c407fe957245bcc83052ce266748fc19b1aa62,
ganzer Tree 95c407b5d74cf93fd7db942731385732dcc9b738 exakt übernommen;
main FF/sauber und eigener lokaler/Remote-Branch entfernt. Unmittelbar TSK-011/
CUR-021 im Branch codex/sql2025-ai-dgn010-plans fortgesetzt.

[Gebundener DGN-010-Ownerplannachweis](SQL_SERVER_2025_AI_INDEX_PLAN_REVIEW.md):
C1 zweimal auf eigener fester 2025-Instanz bestanden, je acht vollständige 1000-Row-
Sourceaufnahmen, tatsächliche DELETE-51003-Gegenprobe/Restore, feste Readerrechte
und eigene Indexbuild-/Dropfolge. Sechs native Actual-Pläne/16000 Source-Rows exakt
gegen private Records gebunden. Je drei vollständige zehn-Row-Ownerqueryresultate;
Clustered Index Seek → eigener Candidate-Index Seek → Clustered Index Seek.
17 zusätzliche used pages, keine Performancewiderlegung. Roher DOP0/erfasste echte
Memorynullen getrennt von fehlenden Attributen, Waits/Warnings NOT_CAPTURED.

Zwei konkrete P2 vor Admission geschlossen, fünf reine Methoden mit elf/neun/neun
Gegenfällen bestanden; anfängliche reine Testtreiberfehler erhalten. Kein Reviewer-
Test-/Runtime oder Reviewkette. Je 21 dokumentierte native Phasencalls und Marker-
Cleanup mit unabhängiger DB-/Namens-/CID-Abwesenheit innerhalb 60 Sekunden bestanden.
Ownerpläne qualifizieren keine Readerpläne/Minimalrollen; Reads/CPU/Elapsed, DMLkosten,
AB/BA/AA/Effektseparation, ältere Engines, öffentliches Paket und volle TP-PERF-/
TSK-011-/Modulabnahme offen. DGN-010 PROPOSED.

Aktuelle Head-/Main-Gates, PR/Integration/Treeübernahme/FF-Sync/eigener Branchcleanup
folgen vor Abschluss. Danach nächste begrenzte kanonische DGN-010-Messaufgabe;
keine unveränderte Wiederholung dieser grünen Pläne. Allgemeine Entwicklung/DGN-007
pausiert; keine Cloud-/Modell-/ONNX-/roten Hosteffekte oder andere Repositoryänderung.
Sechs kohärente Kandidaten je lokalem Schnitt autorisiert, Verbrauch unbekannt,
Heartbeat aktiv.


## DGN-010: begrenzte private Reader-Zugriffspfadmessung

PR191 vollständig abgeschlossen: Head 4065d6a36dd45e04b261c0164ba153badd975de3, sieben Head-Workflows PASS;
Squash 27ef0a118fb25a8ad00353ebd347fb1ad258db4c, fünf Main-Workflows PASS; ganzer Tree ab91c69b0de0d9f8c94fcccf0822518dd14a745d exakt übernommen,
main FF/sauber und eigener lokaler/Remote-Branch entfernt. Unmittelbar TSK-011/
CUR-021 im Branch codex/sql2025-ai-dgn010-measurement fortgesetzt.

[Gebundene feste Readerbatchmessung](SQL_SERVER_2025_AI_INDEX_MEASUREMENT_REVIEW.md):
C1 Counter-FAIL erhalten, C2 mit zwei vollständigen Lifecycles bestanden. Je zehn
Warmups/18 serielle AB-/BA-/AA-Fenster, 1810 vollständige Queryoracles, zusätzliche
positive/negative Kontrolle; beide eigenen Indizes während aller Messphasen vorhanden.
AB/BA sechs Samples je erzwungenem PK-/Candidatepfad, drei AA-Paare separat.
CPU/I/O eigene Requestdeltas einschließlich Grenzen, UTC-Elapsed enthält
Impersonation/Query-/Buffer-/Transfer-/Delete-/REVERT-Aufwand; keine identischen
Messgrenzen, individuelle Querylatenz oder Nettonutzenbehauptung.

22000 Source-Rows, vier neue tatsächliche Ownerpläne, 58 positive Fensterframes
inklusive zwei separater Kontrollen und vier native Negative vollständig gebunden.
Quelle/Config/Readerrechte unverändert; SourceDELETE/Restore/Setupidempotenz,
Indexbuild/Drop und markergebundener SQL-/DB-/CID-/Namenscleanup bestanden.
Enger unabhängiger P2-/Sourceabschluss, acht reine Methoden PASS; ursprünglicher
reiner Fixturefehler erhalten. Reviewer ohne Tests/Runtime, keine Reviewkette.
Sechs kohärente Kandidaten je Schnitt autorisiert, bisherige FAILs erhalten.

Aktuelle Head-/Main-Gates, PR/Integration/Treeübernahme/FF-Sync/eigener Branchcleanup
folgen vor Abschluss. Danach nächste begrenzte DGN-010-DML-/Effektseparationsfrage.
Isolierte Index-/Query-/vollständige Worker-/DMLkosten, ältere Engines, öffentliches
Paket und vollständige TP-PERF-/TSK-011-/Modulabnahme offen; DGN-010 PROPOSED.
Allgemeine Entwicklung/DGN-007 pausiert; keine Cloud-/Modell-/ONNX-/roten
Hosteffekte oder andere Repositoryänderung. Verbrauch unbekannt, Heartbeat aktiv.


## DGN-010: begrenzte private DML-Effektseparation

PR192 vollständig abgeschlossen: Head 003bad4017233091f560752e93d2420b00c2f764, sieben Head-Workflows PASS;
Squash 2bef37419d9399cb5fc49658592de351b16815e5, fünf Main-Workflows PASS; ganzer Tree a6dc9110a041c9c8be37c64aa9f41959e5efec81 exakt übernommen,
main FF/sauber und eigener lokaler/Remote-Branch entfernt. Unmittelbar TSK-011/
CUR-021 im Branch codex/sql2025-ai-dgn010-dml fortgesetzt.

[Gebundene Owner-DML-Batchmessung](SQL_SERVER_2025_AI_INDEX_DML_REVIEW.md):
C1 zweimal mit je zehn Warmups/18 seriellen AB-/BA-/AA-Fenstern und 1810 tatsächlichen
UPDATEs/18100 vollständigen OUTPUT-Rowkontrollen bestanden. A ohne/B mit Candidateindex;
vier Build-/Dropzyklen je Profil außerhalb Messfenster, 46 vollständige Source-/
Config-/Reader-/Indexaufnahmen. Value=Id×3+Ordinal während eigener Transaktion,
tatsächlicher Rollback und voller unveränderter Source-Nachbestand; Source-/OUTPUT-
51003-Gegenproben/Restore/Idempotenz und vollständiger eigener Cleanup bestanden.

92000 Source-Rows/58 positive Fensterframes/vier native Negative exakt gebunden.
Sechs AB/BA-Samples pro Indexzustand, drei AA-Paare separat. Requestdeltas und
UTC-Batchgrenzen einschließlich OUTPUT-/Transaktions-/Rollbackaufwand sichtbar;
keine isolierten Index-/Commit-/vollständigen Workerkosten. Enger unabhängiger
Quellenabschluss ohne offene P1/P2, acht reine Methoden PASS; Reviewer ohne
Tests/Runtime, keine Reviewkette oder Wiederholung früherer grüner Nativeruns.

Aktuelle Head-/Main-Gates, PR/Integration/Treeübernahme/FF-Sync/eigener Branchcleanup
folgen vor Abschluss. Danach begrenzter ungezwungener SELECTvergleich ohne/mit Index.
Nettonutzen, weitere Kosten, öffentliche FWK-/Versions-/Recoveryqualifikation und
vollständige TP-PERF-/TSK-011-/Modulabnahme offen; DGN-010 PROPOSED.
Sechs kohärente Kandidaten je Schnitt autorisiert, historische FAILs erhalten.
Allgemeine Entwicklung/DGN-007 pausiert; keine Cloud-/Modell-/ONNX-/roten
Hosteffekte oder andere Repositoryänderung. Verbrauch unbekannt, Heartbeat aktiv.


## DGN-010: begrenzter ungezwungener SELECTvergleich ohne/mit Index

PR193 vollständig abgeschlossen: Head 12b0716293a8607994b80804e0402768b18997f5, sieben Head-Workflows PASS;
Squash f1984f36a91c67161a0acf66f22e3d373089edc6, fünf Main-Workflows PASS; ganzer Tree fc9d81e3cb7c81063f65694fefb97bf3bc4300c5 exakt übernommen,
main FF/sauber und eigener lokaler/Remote-Branch entfernt. Unmittelbar TSK-011/
CUR-021 im Branch codex/sql2025-ai-dgn010-select fortgesetzt.

[Gebundener ungezwungener Readerbatchvergleich](SQL_SERVER_2025_AI_INDEX_SELECT_REVIEW.md):
C1 zweimal je zehn Warmups/18 AB-/BA-/AA-Fenster und 1810 vollständige Queryoracles
bestanden. A ohne/B mit Candidateindex, identische SELECT ohne INDEX-Hints, feste
Readerrechte; vier Build-/Dropzyklen je Profil außerhalb Messfenster. AB/BA sechs
Samples je Zustand, drei AA-Paare separat. UTC-/Requestgrenzen enthalten Buffer-/
Impersonationaufwand, keine individuelle Querylatenz/isolierte Indexkosten.

92000 vollständige Source-Rows/58 positive Fensterframes/vier native Negative
exakt gebunden; Source/config/Readerrechte gleich, Source-/Querynegative/Restore/
Idempotenz und eigener markergebundener SQL-/DB-/CID-/Namenscleanup bestanden.
Enger unabhängiger Quellenabschluss ohne offene P1/P2, grüne Readerparseranalyse
nach tatsächlichem LF-normalisiertem Vergleich wiederverwendet. Neue positive/
zwei fremde Scopepräfixfälle bestanden; anfängliche reine Fixture-/Bytevergleichs-
Fehler erhalten, keine Runtimewirkung. Keine alte grüne Suitewiederholung.

Aktuelle Head-/Main-Gates, PR/Integration/Treeübernahme/FF-Sync/eigener Branchcleanup
folgen vor Abschluss. Danach begrenzte Vorbereitung des öffentlichen DGN-010-Pakets.
Keine aktuellen Readerpläne/Indexnutzungs-/Nettonutzen-/vollständigen Workerkosten-
oder vollen TP-PERF-/TSK-011-/Modulclaims; ältere Engines/Recoveryqualifikation und
öffentlicher Consumer offen. DGN-010 PROPOSED. Sechs kohärente Kandidaten je Schnitt
autorisiert, historische FAILs erhalten; allgemeine Entwicklung/DGN-007 pausiert,
keine Provider-/roten Hosteffekte oder andere Repositoryänderung. Verbrauch
unbekannt, Heartbeat aktiv.


## DGN-010: öffentlicher reiner Benchmarkauswertungsvertrag

PR194 vollständig abgeschlossen: Head f30021a308bbd1bc6571ccd0d375330daabb839b, sieben aktuelle Head-
Workflows PASS; Squash abd392c63d7b89421df91f27626261f942ebe494, fünf Main-Workflows PASS; ganzer Tree
32d8d00dca6f1f7d49ed6b3967ac3cc745edea26 exakt übernommen, main FF/sauber und eigener lokaler/Remote-
Branch entfernt. Unmittelbar TSK-011/CUR-021 im Branch
codex/sql2025-ai-dgn010-contract fortgesetzt.

[Öffentlicher reiner Auswertungsvertrag](SQL_SERVER_2025_AI_DGN010_BENCHMARK_CONTRACT.md)
mit festen SELECT-/DML-Scopes, 46 vollständigen Quellenzuständen, 29 eindeutigen
positiven Fenstern inklusive separater Kontrolle, zehn Warmups/18 AB-/BA-/AA-
Messfenstern, 1810 Statementoracles und 18100 Rowkontrollen. Vollständige Source-/
Payload-/Request-/DB-/Counter-/UTC-/DML-Ordinal-/Rollbackdepthbindung; Warmups und
AA separat, alle Samples/Nullen/Ausreißer/exakte große Dezimalmediane erhalten.
Keine Identitäts-/UTC-/Source-/Plan-Rawausgabe. Zwei feste FWK-011-Verträge mit je
zwölf vollständig gebundenen Pflichtinvarianten; numerischer PASS ist kein Runtime-PASS.

20 reine Methoden bestanden, enger unabhängiger Quellenabschluss ohne offene
P1/P2; Reviewer ohne Tests/Runtime, keine Reviewkette. Vier bereits gebundene
Native-Records erneut rein geprüft: 48 FWK-PASSs und exakt gleiche Samples/Mediane,
null weitere SQL-/Containerläufe. Vorhandene Nativequellen/Recordhashes und
unabhängiger DB-ID-Frame gebunden. Keine neue Runtime-/Herkunfts-/Versionsattestation.

Statische KI-CI um neue Tests/Quellen erweitert, Runtimejob/Gemeinsam-API unverändert.
Aktuelle Head-/Main-Gates einschließlich tatsächlicher statischer Selection,
PR/Integration/Treeübernahme/FF-Sync/eigener Branchcleanup folgen vor Abschluss.
Danach öffentlicher bounded DGN-010-Runtimeproducer mit getrennten SELECT-/DML-
Messscopes und Versions-/Marker-/Fehler-/Recoveryqualifikation. DGN-010 PROPOSED,
vollständige TP-PERF-/TSK-011-/Modulabnahme/Indexnettonutzen/weitere Kosten offen.
Sechs kohärente Kandidaten je lokalem Schnitt autorisiert, historische FAILs erhalten;
allgemeine Entwicklung/DGN-007/andere Automationen pausiert, keine Provider-/roten
Hosteffekte oder andere Repositoryänderung. Verbrauch unbekannt, Heartbeat aktiv.


## Öffentlicher DGN-010-Consumer: gebundener Kandidat2

[Teilnachweis](SQL_SERVER_2025_AI_DGN010_PUBLIC_REVIEW.md).

## Tatsächlicher begrenzter öffentlicher Nachweis

Kandidat2 vollständig geschlossen: acht tatsächliche Versions-SKIPs vor Setup
(je Scope zweimal 2019/2022), SELECT und DML jeweils zweimal vollständig SQL2025,
zwei kontrollierte Fehler nach PASS-Setup mit anschließender eigener Recovery.
14 neue eigene Container dieses Kandidaten, alle DB-/CID-/Namensabwesenheiten
unabhängig bestätigt, kein unbekannter Clientendstatus. Einschließlich C1 sind
23 Container geschlossen; der Editions-FAIL bleibt erhalten, vier Kandidaten
des gemeinsamen Sechserbudgets verbleiben, kein Budgetreset.

Vier vollständige öffentliche Profile an tatsächliche Nativeframes gebunden:
184000 Source-Rows in 184 Vollsnapshots, 116 positive Fensterframes einschließlich
vier separater Kontrollen, acht echte 51003-Negativframes, 32 Indexübergänge,
7240 vollständige Statementoracles/72400 Rowkontrollen und 48 numerische FWK-PASSs.
Jeder tatsächliche Versions-/Editionsframe ist 17/17.0.5005.3/3/-2117995310;
unabhängige DB-ID, komplette Rawhashes und ausgewählte Ausführungsquellen gebunden.
Source-/Querynegative/Restore/Idempotenz, Config-/Readerrechte, eigener Rollback
und markergebundener regulärer SQLcleanup bestanden. Zehn Warmups/18 Messfenster
je Profil; sechs AB-/BA-Samples je Zustand, drei AA-Paare separat. Alle Samples,
Nullen/Ausreißer/exakte Mediantexte erhalten. Kein Rawausgabeclaim aus CLI/Repository.

Öffentlicher Gesamtstatus WARN_OPTIONAL_EVIDENCE_SKIPPED; reine Recordvalidierung
und numerische FWK-Invarianten PASS, Runtime-/TP-PERF-Abnahme NOT_ESTABLISHED und
aktuelle Indexnutzung NOT_CAPTURED. Keine vollen Worker-/Indexnettonutzen-/Modulclaims.
Separate vollständige Marker-Manipulationsgegenproben, harte DML-/Buildunterbrechung,
Readerpläne, Insert-/Commit-/Buildkosten und vollständige TP-PERF-Abnahme offen.

Aktuelle Head-/Main-Gates mit tatsächlicher Consumer-Matrix, PR/Integration,
ganze Treeübernahme/FF-Synchronisierung/eigener lokaler und Remote-Branchcleanup
folgen vor Abschluss. Danach native Marker-Manipulationsqualifikation desselben
öffentlichen Pakets. Allgemeine Entwicklung/DGN-007/andere Automationen pausiert;
keine Provider-/roten Hosteffekte oder andere Repositoryänderung, Verbrauch unbekannt,
Heartbeat aktiv.


## DGN-010: PR196 geschlossen, begrenzte Markerqualifikation

Stand: 2026-10-12, TSK-011/CUR-021; DGN-010 bleibt PROPOSED.
Der [öffentliche Producer](SQL_SERVER_2025_AI_DGN010_PUBLIC_REVIEW.md) ist über
[PR 196](https://github.com/gecompat/SQL_PerformanceSchulung/pull/196) vollständig
integriert. Zehn Head- und acht Main-Workflows bestanden einschließlich tatsächlicher
Consumer-Matrix auf drei Engineversionen. Head 6d9ac26f69ac76f46ade8a094acb8225ce64e7b1,
Main 324c8ba21df182dddeb30c76e4947a793b84b022, ganzer Tree
224dce4178d6d28340657dbdab41c9aa9ffefb88 exakt übernommen; FF-Synchronisierung,
eigener lokaler und Remote-Branchcleanup abgeschlossen. Historischer C1-Editions-FAIL,
Gesamt-WARN und NOT_ESTABLISHED bleiben erhalten.


Vor Admission gilt der [kanonische Markerschnitt](SQL_SERVER_2025_AI_DGN010_MARKER_REVIEW.md): sechs Quellenkandidaten/maximal zwölf eigene lokale Container, zwei stabile vollständige Lifecycles, je 192 Nativeabweisungen/24 Restores und volle Source-/Metadatenvergleiche. Enger Review und neun reine Gegenfallmethoden abgeschlossen; noch kein nativer Marker-PASS. 300+60-Sekundenfloors, sticky UNKNOWN, CI-Aufwandgrenze und dreier Wave-Checkpoint im Teilvertrag. Danach tatsächliche Readerplan-/Indexnutzungsfrage. Workstream/Heartbeat aktiv; alle alten FAIL-/Provider-/TP-PERF-Grenzen bleiben sichtbar.

C1 der Markerqualifikation ist nach tatsächlichem PASS-Setup vor Markerprobe mit
FAIL geschlossen: die Auswertung wies den einzelnen normalen USE-Infoframe ab.
Eigenes SQLcleanup und neue DB-/CID-/Namensabwesenheit tatsächlich bestanden,
kein UNKNOWN; geschlossener Fehler bleibt im selben Sechserledger. C2 erlaubt
nur den exakten positiven Setupinfoframe, elf reine Methoden einschließlich
gemischter Fehlermeldungsabwehr PASS; enger Deltaabschluss und danach neue
native Admission gemäß [Teilnachweis](SQL_SERVER_2025_AI_DGN010_MARKER_REVIEW.md#tatsächlicher-c1-fail-und-gebundener-c2).

C2 der Markerqualifikation ist bei der ersten vollständigen Snapshotabfrage mit
Msg 8114 geschlossen FAIL: pauschale bigint-Konvertierung eines tatsächlichen
nvarchar-Konfigwerts. Source-/Readerprobe sowie eigener SQLcleanup und neue
DB-/CID-/Namensabwesenheiten bestanden; keine Markerprobe/kein UNKNOWN. C3 erhält
Typ und vollständige primäre/sekundäre Konfigbytes statt Zahlannahme, neuer reiner
Typ-/Byte-/NULLgegenfall PASS, alte grüne Fälle nicht wiederholt. Enger Deltaabschluss
und neue NativeAdmission, danach dreier Wave-Checkpoint gemäß
[Teilnachweis](SQL_SERVER_2025_AI_DGN010_MARKER_REVIEW.md#tatsächlicher-c2-fail-und-gebundener-c3).

Dreier Wave-Checkpoint: C3-FAIL nach tatsächlichem vollständigem Snapshot mit
1000 Rows/41 Configs, fehlender Key für die tatsächlich leere Rollenliste.
Alle drei Kandidaten einschließlich eigener DB/CID/Name vollständig geschlossen,
kein UNKNOWN; Fehlerhistorie bleibt erhalten. C4 erhält [] ausdrücklich und
transportiert vollständige Snapshotbytes als begrenzte UTF-16-Hexframes. 13 reine
Codec-/Controllerfälle bestanden wegen geändertem Codec, enger Capture-Deltaabschluss
vor neuer NativeAdmission. Drei weitere Quellenkandidaten bleiben autorisiert,
kein Reset; [Checkpoint](SQL_SERVER_2025_AI_DGN010_MARKER_REVIEW.md#dreier-wave-checkpoint-c3-fail-und-gebundener-c4).


## DGN-010: C4-Markerqualifikation tatsächlich bestanden

[Teilnachweis](SQL_SERVER_2025_AI_DGN010_MARKER_REVIEW.md#tatsächlicher-c4-nachweis-und-wave-checkpoint).

Der stabile C4 bestand zwei neue eigene vollständige SQL-17.0.5005.3-Lifecycles,
Tokens 51335850D04844FA/02B1C9C49BF649B8. 982 tatsächliche Nativecalls; je 192 einzelne echte vollständige
51004/FAIL_STATE-Abweisungen über vier Marker/sechs Abweichungen/acht Phasen,
24 an die tatsächliche Abweichung gebundene vollständige Restores und eigene
Source-/Readerprobe vor/nach der Matrix. Keine akzeptierte fremde Fixture.

384 tatsächliche Negativframes, 482 vollständige Stateaufnahmen mit 482000
Id/Value/Payload-Rows und 4000 weitere Source-Proberows aus vier Nativeproben an
Originalframes und ausgewählte Sourcehashes gebunden. Die vollständigen State-
Aufnahmen erhalten alle DB-/Datei-/Config-/Objekt-/Index-/Spalten-/Reader-/Rechte-/
Rollen-/Propertywerte; alle 192 Vergleiche je Profil unverändert, 24 vollständige
Originalbaseline-Restores. Tatsächliche Text-Variantwerte inklusive vollständiger
Bytes/Typ/NULL und tatsächlich leere Rollenliste aufgenommen. Keine Trunkierung,
Byte-/Präfixverkürzung oder angenommene Defaults. Frisch unabhängige DB-ID und
Versions-/Editionsframe attestiert. Regular 300/Gesamtrecovery 60 Sekunden erhalten.

Alle fünf eigenen lokalen Container dieser Wave geschlossen, eigenes guarded
SQLcleanup sowie neue DB-/CID-/Namensabwesenheiten bestanden; kein UNKNOWN.
Die drei historischen C1/C2/C3-FAILs bleiben im selben Sechserledger erhalten.
Vier von sechs Quellenkandidaten verwendet; zwei verbleiben, kein Reset und
keine weiteren lokalen grünen Wiederholungen ohne neue Eingaben. Dreier-FAIL-
Checkpoint und nun vollständiger C4-Ergebnischeckpoint dokumentiert.

13 reine Codec-/Controllergegenfälle PASS; enger unabhängiger Marker-/Parent-/
CI-/Captureabschluss jeweils nur für neue konkrete Risiken, keine Reviewkette.
Echte native Markerqualifikation PASS als separater Sicherheitsclaim; öffentlicher
SELECT-/DML-Producer bleibt Gesamt-WARN, volle Runtime-/TP-PERF-/Indexnettonutzen-
Qualifikation NOT_ESTABLISHED, aktuelle Readerpläne/Indexnutzung weiterhin offen.
Modell-/Tokenverbrauch unbekannt; keine Provider-/Host-/anderen Repositoryeffekte.

Aktuelle Head-/Main-Gates mit tatsächlichem neuen Markerconsumer, PR/Integration,
ganze Treeübernahme, FF-Synchronisierung und eigener lokaler/Remote-Branchcleanup
folgen vor Abschluss. Danach separate tatsächliche Readerplan-/Indexnutzungsfrage;
Workstream und Heartbeat bleiben aktiv.


## DGN-010: Marker integriert, begrenzte Indexnutzung registriert

PR 197 tatsächlich abgeschlossen: Head9/Main7 einschließlich nativer Marker-
Dreierversionenmatrix PASS, Squash 4c7c7382041143c06be76bb18aa4124322a6f0e5, ganzer Tree
87f31d31e55658f16f49a1413a91feffca21b533 exakt, FF-main synchron und eigener lokaler/
Remotebranch abwesend. Historische drei FAILs und Producer-WARN erhalten.

Unmittelbare Folge ist [drei tatsächliche einzelne Reader-Indexnutzungsfenster](SQL_SERVER_2025_AI_DGN010_USAGE_REVIEW.md)
mit vollem Source-/Rechte-/Config-Orakel; Budget sechs neue Korrekturkandidaten/
zwölf serielle eigene Container, Checkpoint3/hard6, zwei stabile positive
Lifecycles erforderlich. Neue konkrete Source-/Cleanup-P2 vor Native geschlossen,
elf reine DMVgegenfälle und ein Cleanupfehlerpfad PASS. Admission noch offen;
kein Readerplan-/Nettonutzen-/voller Runtimeclaim, öffentliche Producer unverändert.
Modell-/Tokenverbrauch unbekannt. Workstream/Heartbeat aktiv.


## Tatsächlicher Native-C1-Nachweis

Der stabile erste Kandidat bestand zwei neue eigene vollständige SQL-17.0.5005.3-
Lifecycles, Tokens EC61C42B0BEF4CB3/F4D8F54238FF4633. Je 31 tatsächliche Nativecalls,
drei einzelne ungezwungene Readerqueries mit vollständigem Zehnrow-/Payload-
Digest; insgesamt sechs Queryfenster/60 Queryrows, 18 Sourceproben/18000 Rows,
zwölf vollständige Stateaufnahmen/12000 Rows und vier echte vollständige
51003/FAIL_RESULT_CONTRACT-Negativframes. Alle ursprünglichen Nativeframes und
die tatsächlich verwendeten Sourcehashes lokal gebunden und unabhängig vom
In-memory-Ergebnis rein geprüft, keine neue SQL-Ausführung dabei.

In beiden Profilen tatsächliche UserSeeks-Differenz 1 am PK (Primary Key; Primärschlüssel) ohne Candidate,
1 am Candidate bei vorhandenem Candidate und 1 am PK nach Candidateabbau.
Im mittleren Fenster PK-Differenz 0; alle beobachteten UserScan-/Lookup-/Update-
und Systemcounterdifferenzen 0. Keine INDEX-Hints. Alle relevanten DMVrows waren
vor/nach tatsächlich vorhanden; der fehlende-/neue-Rowpfad wurde hier nicht
nativ erreicht und bleibt nur rein gegengeprüft. Nullwerte sind hier tatsächliche
Differenzen vorhandener Rows, keine Ergänzung fehlender Baselines.

Tatsächliche DB-ID, vollständiger Request, gleicher Startup, exakter fester
SQLtextdigest und tatsächliche Source-/Indexidentität gebunden. Jede vollständige
Statepaarung unverändert, zwei kontrollierte Candidate-DDL-Transitions außerhalb
der jeweiligen Queryintervalle; vollständiger Source-Restore nach Negativprobe.
Guarded SQLcleanup 90/91, frisch unabhängige DB-Abwesenheit und voller eigener
CID-/Namenscleanup bestanden; beide eigenen Container abwesend, kein UNKNOWN.
Ein von sechs Kandidaten verwendet; keine weiteren unveränderten grünen Läufe.

Dies ist ein PASS der begrenzten privaten tatsächlichen Nutzungsbeobachtung,
keine zusätzliche öffentliche Producer-Funktion. Öffentlicher Producer weiterhin
Gesamt-WARN; runtime_qualification und index_net_benefit NOT_ESTABLISHED,
actual_reader_plan NOT_CAPTURED. Keine allgemeine Performanceempfehlung aus drei
Singlequeries. Modell-/Tokenverbrauch unbekannt.

Aktuelle selektierte Head-/Main-Gates, PR/Integration, ganzer Tree, FF-main und
eigener lokaler/Remote-Branchcleanup folgen. Danach nächste zulässige begrenzte
DGN-010-Kostenfrage: Owner-INSERT mit tatsächlichem Rollbackrestore ohne/mit
Candidate. Commit-/Build-/Worker-/volle Readerpläne und vollständige TP-PERF-/
Modul-/Lehrmaterialabnahme bleiben offen; Workstream/Heartbeat aktiv.


## DGN-010: Indexnutzung integriert, Owner-INSERT-/Rollback registriert

PR198 mit aktuellen Head7/Main5 PASS abgeschlossen, Squashd6e0efe9e5d6fd7a0e403fa610176ebbd68cb44b,
ganzer Treee5eaf5d57ac42e8ab99f7db34b5bd5690c4b2fb6 exakt, FF-main synchron/Ownbranches abwesend.
Nächste [private INSERT-/per-Statement-Rollbackfrage](SQL_SERVER_2025_AI_DGN010_INSERT_REVIEW.md)
mit1000Originalrows/max1010kurzzeitig, 10Warmups/18ABBAAA/Control1/46Sources/
29vollständigen Statepaaren: sechsKandidaten/max12eigeneContainer, Checkpoint3/
hard6/zwei stabilevolleLifecycles. Acht neue reine Oraclegegenfälle bestanden;
NativeAdmission erst nach engem Sourceabschluss. Kein Commit-/Build-/Worker-/
Readerplan-/Nettonutzen-/vollerRuntimeclaim; Workstream/Heartbeat aktiv.


## Tatsächlicher Native-C1-Nachweis

Der stabile erste Kandidat bestand zwei neue eigene vollständige SQL-17.0.5005.3-
Lifecycles, Tokens FBFF95626B5D4922/9A106CC3A62A44FE. Je 153 tatsächliche
Nativecalls; insgesamt 58 positive Fenster, 3620 Warmup-/Mess-INSERTs plus zwei
separate positive Einzelcontrols. 36200 vollständige Benchmark-OUTPUT-Roworacles
plus 20 separate Controlrows, 3622 tatsächlich geprüfte positive Rollbacks.
92 volle Sourceproben/92000 Rows und 116 vollständige Stateaufnahmen/116000 Rows;
58 vollständige unveränderte Vorher-/Nachherpaare inklusive aller DB-/Datei-/
Config-Variantbytes/NULL/Metadata/Reader-/Rechte-/Rollen-/Property-/Sourcewerte.
Alle ursprünglichen Nativeframes an tatsächliche Sourcehashes und komplette
transportierte Ergebnisse rein gebunden; keine neue SQL-Ausführung für diese
Recordprüfung. Vier echte vollständige 51003/FAIL_RESULT_CONTRACT-Gegenframes,
Source-/OUTPUT-Negative tatsächlich abgewiesen und ursprüngliche Source erhalten.

Je Profil zehn Warmups, 18 AB/BA/AA-Fenster zu hundert INSERTs, sechs Baseline-/
sechs Vergleichssamples und drei AA-Paare. Mediane pro Hundert-INSERT-Fenster,
Warmups/AA ausgeschlossen; sämtliche Originalsamples/Range/Nullwerte/AA lokal
erhalten. Kein Durchschnitt über die beiden Profile und keine Signifikanzbehauptung.

| Profil | CPU ohne/mit (ms) | Logical Reads ohne/mit | Elapsed ohne/mit (µs) |
| --- | --- | --- | --- |
| 1 | 23.5 / 30.5 | 8958 / 15155.5 | 24686.5 / 36995.5 |
| 2 | 23 / 32 | 8957 / 15152.5 | 22608.5 / 39136 |

In diesen beiden begrenzten Profilen liegen die Candidate-Mediane für CPU,
Logical Reads und Elapsed höher. Das beobachtet INSERT-/OUTPUT-/Rowprüf-/
BEGIN-/ROLLBACK-Batchkosten unter den festgelegten Bedingungen. Keine reine
INSERTcpu, Commit-/Builddauer, gesamte Worker-/Log-I/O oder Gesamt-Nettonutzen-
qualifikation. Ergebnisse anderer Workloads, Datenumfänge und tatsächlicher
Readerpläne sind damit nicht attestiert; ein Seek allein belegt keinen Lesegewinn.

Originalsource1000 nach jedem Statement wiederhergestellt, kurzzeitig nur zehn
zusätzliche synthetische Rows; kein Commit. Acht kontrollierte Create-/Drop-
transitions außerhalb der Messfenster je Profil, Source-/Readerrechte unverändert.
Guarded90/91 sowie frisch unabhängige DB-Abwesenheit, voller eigener CID-/Name-
Cleanup bestanden; beide eigenen Container abwesend, kein UNKNOWN. Ein von sechs
Kandidaten verwendet, keine weiteren unveränderten grünen Wiederholungen.
Acht reine neue Gegenfälle und enger unabhängiger Review ohne offene P1/P2
bestanden; Modell-/Tokenverbrauch unbekannt, keine anderen Repositories verändert.

Dies ist PASS der begrenzten privaten INSERT-/Rollbackbeobachtung; öffentliche
Producer unverändert Gesamt-WARN, Runtime/TP-PERF/Indexnettonutzen NOT_ESTABLISHED.
Tatsächliche Readerpläne, Commit-/Build-/volle Workerkosten, vollständige Modul-/
Lehrmaterial-/Workstreamabnahme bleiben offen. Aktuelle selektierte Head-/Main-
Gates, PR/Integration, ganzer Tree/FF-main und eigener lokaler/Remotebranchcleanup
folgen. Danach unmittelbar nächste zulässige begrenzte Kosten-/Planfrage;
Workstream/Heartbeat bleiben aktiv.


## DGN-010: INSERT integriert, tatsächliche Readerpläne registriert

PR199 vollständig abgeschlossen: Head7/Main5 PASS, Main 83d28cd59ae1f8a34028518e4904e44800236e81,
ganzer Tree a84484ab10f07518decb402972a9a4af10a59a93 exakt, FF-main und eigene Branches bereinigt.
Nächster [begrenzter Readerplanschnitt](SQL_SERVER_2025_AI_DGN010_READER_PLANS_REVIEW.md):
sechs Kandidaten/max12 serielle eigene Container, Checkpoint3/hard6 und zwei
stabile Lifecycles. Drei Originalqueries/volle Source-Statepaare, kurzlebige
gebundene XE-Sitzung nur im eigenen Container; noch keine Nativeadmission.
Commit-/Build-/volle Worker-/Nettonutzen-/vollständige Abnahme offen.


Readerplan-C1 FAIL nach 17 Nativecalls: Lightweight-XML ohne StatementText,
strikte ursprüngliche Zuordnung deshalb nicht bestanden. Eigene DB/CID/Name
vollständig abwesend, kein UNKNOWN. Gebundene Formatkorrektur C2 mit nativer
sql_text-Aktion und tatsächlichen Runtimeparametern im
[Readerplannachweis](SQL_SERVER_2025_AI_DGN010_READER_PLANS_REVIEW.md); zehn reine
Gegenfälle bestanden. Enger Deltaabschluss vor C2-Admission, Budget sechs unverändert.


Readerplan-Checkpoint3: C1/C2 fehlgeschlagene Formatzuordnung, C3 SQL1934
(QUOTED_IDENTIFIER für XML). Alle drei eigenen DB-/CID-/Namenslifecycles
sicher geschlossen, kein UNKNOWN. Drei von sechs Kandidaten verbraucht,
C4 setzt ausschließlich QUOTED_IDENTIFIER ON in der eigenen temporären
Nativeverbindung; Stack-/Source-/Reader-/Cleanupfloors unverändert.
[Gebundene Befunde und Korrektur](SQL_SERVER_2025_AI_DGN010_READER_PLANS_REVIEW.md).


## C6: geschlossener FAIL-Checkpoint der ersten Readerplanwelle

C6 (9577FCB01FA0466E) endet nach 17 Nativecalls mit FAIL: Die tatsächliche
XE-Ereigniszeit 2026-10-12T09:15:54.768Z besteht den bisherigen Vergleich mit dem
Readerintervall 2026-10-12T09:15:54.7684718 bis 2026-10-12T09:15:54.7684718 nicht.
Die vorliegenden Zeitfelder haben unterschiedliche Nachkommastellen; noch kein
akzeptierter tatsächlicher Originalreaderplannachweis und keine stabile
Zweiprofilqualifikation. Die vorangehenden vollständigen Source-/Request-/
Prepared-Text-/Stackoffsetkontrollen wurden tatsächlich erreicht.

Guarded90/91, frische unabhängige DB-Abwesenheit und voller eigener CID-/
Namensabbau sind bestätigt. Cleanup 13.46 Sekunden, kein
UNKNOWN. Alle sechs Kandidaten dieser Welle sind fehlgeschlagen, alle sechs
Container sicher abwesend; harte Sechsergrenze erreicht. Kein C7 in dieser
Welle, keine unveränderte Wiederholung und kein stilles Zurücksetzen.
Vierzehn betroffene reine Tests und enge unabhängige Quellenreviews ohne
offene P1/P2 ersetzen keinen Native-PASS. Modell-/Tokenverbrauch unbekannt.

Dieser konsistente FAIL-Checkpoint wird über PR integriert. Öffentliche
Producer weiterhin Gesamt-WARN, DGN-010 PROPOSED, vollständige TP-PERF-/
Nettonutzen-/Lehrmaterialabnahme NOT_ESTABLISHED. Aktuelle Head-/Main-Gates,
Integration, ganze Treeübernahme, FF-Synchronisierung und eigener lokaler/
Remote-Branchcleanup folgen. Danach unabhängige autorisierte Folienarbeit und
weitere konkrete Sourcekorrekturen ausschließlich mit sichtbarem Folgecheckpoint.

## Readerplan-Folgewelle C7–C12 registriert

PR200 ist vollständig geschlossen: sieben aktuelle Head-/fünf Main-Gates,
ganzer Tree/FF-main/eigener lokaler und Remote-Branchcleanup bestanden.
[UTC-Folgewelle](SQL_SERVER_2025_AI_DGN010_READER_CLOCK_REVIEW.md): tatsächlich
beobachtete Native-Millisekundenauflösung statt falscher genauerer Zeitannahme;
vollständige Originalsource-/Preparedtext-/Request-/Runtime-/Cleanupbindung
unverändert. Explizite fortgeltende Freigabe der weiteren lokalen Entwicklung;
keine erneute gewöhnliche Budgetfrage. Alte sechs FAILs erhalten, kumulativ
C7–C12/max18 Container einschließlich alter sechs; Zwischencheckpoint C9/hard C12.
Fünfzehn reine Methoden bestanden; zwei stabile tatsächliche Lifecycles fehlen.
Parallele KI-Schulungsfolien im eigenen Worktree werden erstellt.


## Tatsächlicher Native-C7-Nachweis und Checkpoint

Kandidat 7 bestand zwei neue eigene vollständige SQL-17.0.5005.3-Lifecycles,
Tokens 102F335BC31343C9/8E457B5AFF5B48FA. Nativecalls je Profil:
32/32. Insgesamt sechs ursprüngliche
ungezwungene Reader-Abfragen mit 60 vollständigen Rowdigests, 18 Sourceproben/
18000 Rows und zwölf vollständige Stateaufnahmen/12000 Rows. Vier echte vollständige
51003/FAIL_RESULT_CONTRACT-Negativframes; ursprüngliche Source tatsächlich erhalten.

| Profil | Ohne Candidate | Mit Candidate | Nach Abbau |
| --- | --- | --- | --- |
| 1 | Clustered Index Seek / [DGN010_OwnPK] | Index Seek / [DGN010_OwnCandidate] | Clustered Index Seek / [DGN010_OwnPK] |
| 2 | Clustered Index Seek / [DGN010_OwnPK] | Index Seek / [DGN010_OwnCandidate] | Clustered Index Seek / [DGN010_OwnPK] |

Jeder passende Actualplan hat tatsächlichen Ergebnisroot10 und Source10,
jeweils genau einen Thread0/eine Ausführung; int-Runtimeparameter101/110.
Vollständiger tatsächlicher Batchtext, Event-Session-/DB-ID, fünfteiliger Request,
Native Stackhandle/Byteoffsets und genau passender vollständiger StatementText
gebunden. Native UTC-Ereignisse auf ihrer tatsächlich gelieferten Millisekunden-
auflösung dem ursprünglichen Readerintervall zugeordnet; kein Querydauerclaim.
Vollständiger Preparedtext-SHA mit Parameterdeklaration und originalem Semikolon,
Native-Statementoffsets ohne ausschließlich terminales Semikolon gebunden.
Kein geschätzter Cacheplan als Actualplan ausgegeben. Original-
ShowplanXML und vollständige tatsächlich ausgeführte/importierte Sourcehashes
privat erhalten und rein erneut an die Records gebunden, keine neue SQL-Ausführung
für diese Recordprüfung. Alle Ringpopulationen vollständig, keine Verdrängung/
Trunkierung/Dropcounter; eigene Sitzungsdefinition vor Abbau vollständig gleich.

Alle Source-/Statepaare einschließlich Config-Variant-/Datei-/Objekt-/Reader-/
Rechte-/Rollen-/Markerbytes vollständig unverändert. Zwei Candidate-DDL-
Transitions außerhalb der Queryaufnahme je Profil. Sechs eigene XE-Sitzungen
nativ abgebaut, je Profil zusätzlich frisch unabhängige Abwesenheit aller drei
Sitzungen. Guarded90/91, neue unabhängige DB-Abwesenheit und voller eigener
CID-/Namensabbau PASS. Alle 8 eigenen Container abwesend, kein UNKNOWN.
6 historische FAIL-Lifecycles bleiben sichtbar. Kumulativ C7; 1 von sechs
Kandidaten der Folgewelle verwendet. Erste Sechserwelle unverändert FAIL erhalten;
positiver Schnitt sicher geschlossen, kein Reset
und keine weiteren unveränderten grünen Wiederholungen. Fünfzehn reine Gegenfälle
und enge unabhängige Source-/Deltareviews ohne offene P1/P2 bestanden. Reviewer
attestierte keine Nativeausführung. Modell-/Tokenverbrauch unbekannt.

PASS der begrenzten privaten tatsächlichen Originalreaderplanbeobachtung.
Öffentliche Producer weiterhin Gesamt-WARN; volle Runtime/TP-PERF und
Indexnettonutzen NOT_ESTABLISHED. Die zusätzliche Instrumentierung ist getrennt
von den bisherigen Performance-Messungen. Ein Index Seek belegt für sich keinen
Nettonutzen. Commit-/Build-/volle Worker-/Modul-/Lehrmaterialabnahme bleiben offen.
Aktuelle selektierte Head-/Main-Gates, PR/Integration, ganze Treeübernahme,
FF-main und eigener lokaler/Remote-Branchcleanup folgen. Danach unmittelbar
nächste zulässige begrenzte Buildkostenfrage; Workstream/Heartbeat bleiben aktiv.

## TSK-012: Eigenständiger KI-Foliensatz vom 2026-10-12

Der ausdrücklich parallel autorisierte Schulungsschnitt enthält
[34 editierbare PowerPoint-Folien](../../Presentations/SQL_Server_2025_KI.pptx)
für CUR-013 bis CUR-022 mit 34 vollständigen Sprechernotizen, Quellen und
konkreten manifestbasierten Demoaufträgen. Alle 18 registrierten Demoentwürfe
sind als neun IMPLEMENTED- und neun PROPOSED-Demos abgedeckt.
[Reproduzierbare Masterquelle und Trainerhinweis](../../Presentations/AI_SQL_Server_2025/README.md)
verlinken die bestehenden Ausführungsverträge, Lösungen und Rubrik. Neue
SlideKeys und eigene KI-Tiefenprofile sind nicht als abgenommen registriert.

Der Quellenstand des Decks ist main 83d28cd59ae1f8a34028518e4904e44800236e81.
Der neue konkrete Reviewbefund erforderte eine eng begrenzte Korrektur von
Folie 31: zwei private Original-Readerplanprofile sind jetzt ausdrücklich
auf der Folie und in den Notizen mit dem kanonischen Clock-Nachweis gebunden.
Quellenstand dieser Aussage ist main 4bfb191; die allgemeine Recherchebindung
an main 83d28cd bleibt dokumentiert.
PR 201 ist auf main 4bfb1914623c3c49fcc287ee8079013a0fad6ddb mit sieben Head-/
fünf Main-Workflows, exakter Treeübernahme, FF-main und eigenem Branchcleanup
abgeschlossen. Öffentliche Producer, volle Runtime-/TP-PERF- und
Indexnettonutzengates bleiben weiterhin getrennt und offen.

Erster Export in PR 202: 147514 Bytes, SHA-256
726398beff736cb9b51818b4596e65c0895a66f568de021ebd3cc3af19202fcd.
34/34 Folien vollständig gerendert und einzeln auf Inhalt, Umbruch,
Lesbarkeit und Privacy geprüft. 13 native Tabellen, 34 Notizen und alle
18 Demo-IDs bestätigt. Paket-, Geometrie-, Arial- und First-Party-Importprüfung
bestanden; ein konservativer Tabellenhöhenhinweis auf Folie 5 zeigt im
tatsächlichen Render keinen Überlauf. Identitätsmetadaten neutralisiert,
keine Medien, Logos, eingebetteten Objekte, Credentials oder privaten Pfade.
Die betroffenen Dateien bestanden die bestehende Privacyprüfung vor Commit.
Beim ersten Export kein editierender PowerPoint-Anwendungstest, keine neue SQL- oder
Provider-/Cloud-/ONNX-/Hostausführung. Rawrender und Prüfrecords bleiben unter
ignoriertem Runtime. Sechs endliche Authoring-/Korrekturkandidaten verbraucht,
Checkpoint3 eingehalten. Der zusätzliche konkrete Reviewbefund zur inzwischen
überholten Readerplanaussage autorisierte einen sichtbaren C7-Folgecheckpoint
ohne Reset der alten Kandidaten. C7 korrigierte nur Folie 31 und ihre Quellen-
notizen; geänderte Folie neu gerendert und einzeln geprüft, notwendige finale
Paket-/Metadaten-/Geometrie-/Importbindung am vollständigen Deck bestanden.
Unveränderte Einzelprüfungen wiederverwendet; kein zusätzlicher Native-Lauf.
Der fachliche Folienumfang ist geschlossen.

PR 202 ist auf main 1a514f92a88e2c4034dfa333026784e496456676 mit acht Head-/
sechs Main-Workflows, exakter Treeübernahme, FF-main und eigenem Branch-/
Worktreecleanup abgeschlossen. Die anschließende Benutzerprobe in PowerPoint
schlug trotz der Paket-/Renderprüfungen fehl: Die Metadatenneutralisierung
benannte den Namespacepräfix um, ließ aber `xsi:type="dcterms:W3CDTF"` mit
ungebundenem `dcterms` stehen. Dieser Fehler bleibt als ursprünglicher FAIL
sichtbar; er betrifft die Office-Lesbarkeit und keine SQL-Demo.

Der ausdrücklich angeforderte Reparaturschnitt auf
`codex/sql2025-ai-pptx-office-repair` erhält den Datumspräfix und ergänzt drei
Regressionen einschließlich der ursprünglichen negativen Kontrolle im
bestehenden Presentation-Workflow. Genau ein korrigiertes Paket wurde in
PowerPoint 16.0 tatsächlich geöffnet: 34 Folien, 13 native Tabellen; Text,
Tabellenzelle und Sprechernotiz bearbeitet, private Kopie gespeichert und erneut
geöffnet, jeweils PASS. Repariertes PPTX in PR 203: 147868 Bytes, SHA-256
f7ac0e74cc41333bff3f0c38ab0f472b1e47cb2b2f7f796c795f0868b1f6f97c.
Alle Folien- und Notizenparts bleiben bytegleich. Keine SQL-, Provider-, Cloud-,
ONNX- oder Hostausführung. Office-Testkopie und ursprünglicher Export bleiben
privat. Head-/Main-Gates, PR-Integration, Synchronisierung und eigenes
Branchcleanup schlossen diesen Reparaturschnitt ab: PR 203 integriert auf
main b17113bd479bef0f8a644d6e6246b53ac0814338, acht Head-/sechs Main-Workflows
PASS, exakter Tree, FF-main sauber und eigener lokaler/Remote-Branch entfernt.

TSK-012 bleibt offen: tatsächliche Teilnehmererprobung, gemessene Lehrzeiten,
vollständige Teaching Paths und Generalprobe fehlen. Der Workstream und sein
Heartbeat bleiben aktiv.

### Erweiterte Einführung für Anwender:innen ohne KI-Erfahrung

Der anschließende Benutzerauftrag verlangt einen umfangreicheren Einstieg vor
den Fachdetails. Der Schnitt `codex/sql2025-ai-beginner-introduction` erweitert
TSK-012 auf 61 Folien: 27 neue Einführungsfolien vor den bisherigen 34 Fachfolien.
Ein durchgehender synthetischer MOD_A-Wissensbasisfall erklärt Quelle/Fassung,
KI/ML, Modell, Training/Inferenz, Sprachmodell, Tokens, Rollen und Anwendungsfälle.
Server/Client/CL, vorbereitete Labverbindung, Rechte und späterer Modellzugang
erhalten verständliche Voraussetzungen und nächste Schritte. Cloudkonto,
ChatGPT, Copilot, Modellservice, Preview und neue Datenbankobjekte sind für den
ersten geometrischen DECLARE-/VALUES-/SELECT-Versuch nicht erforderlich.
Vorhersage, vollständiger Code und besprochene Sollwerte 0/1/2 sind getrennt;
die Werte sind mathematisch hergeleitet, kein neuer SQL-Runtimebefund und keine
gemessene Sprachsemantik. Quellen-/Nichtantwortfälle schließen den Einstieg ab.

Der reproduzierbare Export leitet Folienzahl und native Tabellen aus der
Masterquelle ab und erlaubt getrennte private Build-/Ausgabepfade. C1 hielt
an der Eingangsprüfung des Finalizers an, weil Receipt und finaler Ausgabeordner nicht getrennt
waren. Dieser FAIL bleibt privat erhalten. C2 mit getrennten Ordnern bestand
Paket, Geometrie, Arial und finalen First-Party-Import. Alle 61 Folien wurden
neu gerendert und einzeln visuell geprüft. Ein konservativer Tabellenhöhenhinweis
auf Folie 32 zeigte im konkreten Render keinen Überlauf. PowerPoint 16.0 öffnete
61 Folien mit 23 nativen Tabellen und 61 Sprechernotizen. Text, Tabellenzelle
und Notiz bearbeiten sowie private Kopie speichern/erneut öffnen jeweils PASS.
Aktuelles neutrales PPTX: 245680 Bytes, SHA-256
72275f2fa0156799e4346b35fb3436fe420b113f0ae38dea0b94cd3a10b62a99.
Alle 18 Demo-IDs, neun IMPLEMENTED/neun PROPOSED und ihre offenen Gates bleiben
erhalten. Arbeitsheftlösungen und Rubrik bleiben unverändert. Trainerleitfaden,
Backlog und Workstreamplan sind mit dem neuen gemeinsamen Einstieg abgeglichen.

Keine SQL-, Provider-, Cloud- oder ONNX-Ausführung und keine roten Hoständerungen. Office-Testkopien,
Renderdaten und Prüfnachweise bleiben privat. Head-/Main-Gates, PR-Integration,
Synchronisierung und eigenes Branchcleanup bilden den Integrationsabschluss.
Lehrzeiten, Teilnehmererprobung, vollständige Teaching Paths und Generalprobe
bleiben offen; die alten Zeitplanwerte belegen keine Dauer dieses größeren Decks.

## Fortsetzung: begrenzte DGN-010-Build-/Dropkosten

PR 204 ist vollständig abgeschlossen: main 7a68bb7261ffbdb21b6cf7ece4d1d88cc1d5bee6,
neun Head-/sieben Main-Workflows PASS, ganzer Tree/FF-main sauber und eigener
lokaler/Remote-Branch entfernt. Der nächste zulässige SQL-Schritt ist auf
`codex/sql2025-ai-dgn010-build-costs` begonnen: [getrennte Build-/Dropfenster](SQL_SERVER_2025_AI_DGN010_BUILD_COST_REVIEW.md)
unter TSK-011/CUR-021. Sechs Kandidaten/max12 eigene serielle Container,
Checkpoint3/hard6; zwei vollständige stabile positive Profile. Bestehende
Reader-/INSERT-/Folienfehler bleiben erhalten. Unbekannter Modell-/Tokenverbrauch
bleibt unbekannt, keine weitere gewöhnliche Budgetfreigabe erforderlich.

Private feste Quellen und sieben reine Gegenproben/CLI-help vorhanden; enger
unabhängiger DDL-/Lease-/Request-/Counter-/Vollstate-/Cleanupquellenreview ohne
offene P1/P2. Noch keine neue Nativeausführung. Messbereiche getrennt von
bestehenden Reader-/Rollbackfenstern, vollständige 13-Key-States, echte Source-
und DROP-ohne-Indexnegative, gleiche bytegenaue Eigentumsmarker und KnownEnd-
300/60-Sekunden-/CID-Cleanupfloors. Öffentliche Producer weiterhin WARN,
DGN-010 PROPOSED; vollständige Runtime/TP-PERF/Nettonutzen bleiben offen.

### Native Buildkosten-C1 zweimal bestanden

Zwei stabile neue vollständige Profile, je 34 Nativecalls: vier Builds/vier
Abbaue, 16000 Source-Rows, 20000 Vollstate-Rows und vier tatsächliche
51003-Negativen/Source-Restore. Native Request-/DDL-/Counter-/UTC-/gehaltene
Index-/Spalten-Lease und unabhängige Vollstatebindung bestanden. Alle acht
Zahlen im [Buildkostennachweis](SQL_SERVER_2025_AI_DGN010_BUILD_COST_REVIEW.md)
erhalten; keine isolierten Worker-/Log-/Commit-/vollen Lifecyclezeiten daraus
ableiten. Writes 0 bei DROP bleibt eine begrenzte tatsächliche Requestbeobachtung.

Beide SQL-90/91-/frischen DB-Abwesenheits-/vollständigen CID-/Namens-/zusätzlichen
Ownerlabel-Abwesenheitskontrollen PASS, kein UNKNOWN und keine eigene Restinstanz.
Ein Kandidat/zwei Container verbraucht; keine unveränderte grüne Wiederholung.
Sieben reine Gegenproben und enger unabhängiger Quellenabschluss bestanden;
Vollrecords anschließend an tatsächliche unveränderte Ausführungsquellen rein
gebunden, kein zusätzlicher SQL-Lauf. Private Inputs/Logs/Records bleiben privat.
Aktuelle Head-/Main-/PR-/Tree-/FF-/Ownbranchgates folgen. Danach unmittelbar
bereits erhobene Indexseiten rein aufbereiten; Nettonutzen/volle Abnahme offen.

## DGN-010: reine Folgeaufbereitung vorhandener Indexseiten

PR 205 ist auf main 6079f7a50f3ab0a61d1e21ec9d79a9d2d19e2e16 mit sieben
Head-/fünf Main-Workflows PASS, ganzer Tree/FF-main sauber und eigenem lokalem/
Remote-Branchcleanup abgeschlossen. Beide eigenen Testinstanzen abwesend,
kein UNKNOWN. Unmittelbare Folge auf `codex/sql2025-ai-dgn010-index-pages`:
[vorhandene native Indexseiten](SQL_SERVER_2025_AI_DGN010_INDEX_PAGES_REVIEW.md)
aus denselben exakt hashgebundenen Vollrecords und unveränderten Quellen.

Je Profil fünf feste A/B/A/B/A-Aufnahmen. Originaler PK durchgängig 18 Used/
33 Reserved Pages, Candidate in B 17 Used/33 Reserved Pages; ausgewählte
Indexsumme 18/33 gegen 35/66. Candidate in A tatsächlich abwesend, kein
fehlender Wert als gemessene Null. Rowcount-1000-Katalogaufnahme und die
vollständige tatsächliche Source-Rowqualifikation bleiben getrennt.
Alle zehn Beobachtungen erhalten, drei reine Gegenproben bestanden,
null zusätzliche SQLcalls oder Container, keine unveränderte grüne Wiederholung.

Used/Reserved sind Partitionallokationen einschließlich Verwaltungsaufwand,
keine vollständige Datei-/RAM-/Log-/Nutzdatenmessung oder Nettonutzenqualifikation.
Quelle/Record/DDL-/Cleanupbelege unverändert; kein weiteres Review derselben
geprüften Nativequellen. Aktuelle PR-/Head-/Main-/Tree-/FF-/Ownbranchgates folgen,
danach öffentlicher getrennt begrenzter Kostenrecord-/Aggregationsvertrag.

## DGN-010: öffentlicher reiner Kostenrecordvertrag

PR206 ist vollständig abgeschlossen: main 5c5c2596f54db93b33229fe3c99bf98881500a4b,
sieben Head-/fünf Main-Workflows PASS, ganzer Tree gleich, FF-main sauber und
eigener lokaler/Remote-Branch entfernt. Unmittelbare Folge auf
`codex/sql2025-ai-dgn010-cost-records`: [öffentlicher numerischer Vertrag](SQL_SERVER_2025_AI_DGN010_COST_CONTRACT.md),
sechs Kandidaten/Checkpoint3/hard6, keine neuen SQLcalls oder Container.

15 synthetische Gegenproben bestanden. Enger unabhängiger Review meldete drei P2,
anschließend geschlossen: siebte datetime2(7)-Stelle, nullable Typbindung und volle
Statekontinuität zwischen Fenstern. Zwei vorhandene exakt hashgebundene Native-
Vollrecords mit separat gebundenen Caller-DBID-Frames rein neu geprüft: acht
DDL-Fenster, 16000 Source-/20000 State-Rows. Nativequellen und frühere tatsächliche
Negativ-/Cleanupbelege bleiben unverändert; keine unveränderte grüne Wiederholung.

Alle beiden Samples/Nullen/exakte Mediane und fünf A/B/A/B/A-Allokationen je Profil
erhalten. Numerischer PASS attestiert keine bloßen Controllerflags; öffentliche
Producer WARN/DGN-010 PROPOSED, Runtime/TP-PERF/Worker/Nettonutzen NOT_ESTABLISHED.
Nur zwei neue Workflowtrigger/ein reiner statischer Schritt, Runtimeauswahl am
tatsächlichen Head/Main False erforderlich. Aktuelle PR-/Head-/Main-/Tree-/FF-/
Ownbranchgates folgen; danach öffentliche begrenzte Producerintegration.

## DGN-010: öffentliche feste Kostenproducer-Eingaben

PR207 ist vollständig abgeschlossen: main f8b212f1e25370cda958892a53c75890a3e7367a,
acht Head-/sechs Main-Workflows PASS, Runtimeauswahl False (Runtimejob SKIPPED,
kein Runtime-PASS), ganzer Tree gleich, FF-main sauber und eigener Branch lokal/
remote entfernt. Unmittelbare erste Produceranbindung auf
`codex/sql2025-ai-dgn010-cost-inputs`: [feste öffentliche SQLeingaben](SQL_SERVER_2025_AI_DGN010_COST_INPUT_REVIEW.md).
Sechs Quellenkandidaten/Checkpoint3/hard6, keine neuen SQLcalls/Container.

Sechs reine Gegenproben und enger unabhängiger Kompositionsreview ohne offene
P1/P2 bestanden. Vorhandene feste DDL-/Statequellen übernommen, nur Source-NULL-
Guard enger. Vollständige DB-/Marker-/Source-/gehaltene Leasebindung vor DDL;
alle acht vorhandenen tatsächlichen DDL-Leases rein angebunden. Kein Prozessstart
oder SQLaufruf; kein ausführbarer Kostencontroller und keine neue Nativeabnahme.

Zwei neue Trigger/ein statischer Schritt, Runtimejob unverändert. Aktuelle
PR-/Head-/Main-/Tree-/FF-/Ownbranchgates folgen. Danach tatsächlichen öffentlichen
Kostencontroller vorbereiten; Producer WARN/DGN-010 PROPOSED und volle Runtime/
TP-PERF/Worker/Nettonutzen NOT_ESTABLISHED bleiben erhalten.

## DGN-010: öffentliche Kostencontroller-Vorbereitung

PR208 vollständig abgeschlossen: main 40d56069f28e4add5e2380fd2c3cd2ec93853afe,
acht Head-/sechs Main-Workflows PASS, tatsächliche Runtimeauswahl False/Job SKIPPED,
ganzer Tree gleich, FF-main sauber und eigener lokaler/Remote-Branch entfernt.
Unmittelbare Fortsetzung auf `codex/sql2025-ai-dgn010-cost-controller`:
[öffentlicher begrenzter Kostencontroller](SQL_SERVER_2025_AI_DGN010_COST_CONTROLLER_REVIEW.md),
sechs Quellenkandidaten/Checkpoint3/hard6, noch keine lokale Controller-Nativequalifikation.

Elf synthetische Controller- und sieben Eingabemethoden PASS, CLI-help ohneClient;
enger unabhängiger neuer Ablauf-/KnownEnd-/Negativ-/Input-/Cleanupreview ohne
offene P1/P2. Vier DDL-Fenster, acht Source-/zehn Vollstateaufnahmen, feste echte
Source-/DROP-Abwesenheitsnegative, volle Zwischenfensterkontinuität und einmalige
Parent300/60-Deadlines. UNKNOWN sperrt SQL und erhält Inputs; Unlinkfehler bleiben
FAIL_CLEANUP. CLI nur geprüfte Aggregate bei WARN und vollständigem Cleanup.

Neue Demosource erfordert tatsächliche bestehende CI-Runtimeauswahl True,
vorhandene isolierte Versionsmatrix inklusive eigenem CI-Cleanup. Diese Matrix
prüft bisherige Scopes, keine neue Kostencontroller-Nativequalifikation.
Aktuelle PR-/Head-/Main-/Tree-/FF-/Ownbranchgates folgen; danach separat budgetierte
Nativequalifikation des neuen Controllers. Producer WARN/DGN-010 PROPOSED,
Runtime/TP-PERF/Worker/Nettonutzen NOT_ESTABLISHED; alle historischen FAILs erhalten.

## DGN-010: separate native öffentliche Kostenqualifikation

PR209 vollständig abgeschlossen: main bf206ccbb1b0892773b9b0ef785b85e80b1ba9d0,
neun Head-/sieben Main-Workflows PASS, tatsächliche bestehende Versionsmatrix
inklusive eigenem CI-Cleanup an Head/Main bestanden, ganzer Tree gleich,
FF-main sauber und eigener lokaler/Remote-Branch entfernt. Unmittelbare Folge
auf `codex/sql2025-ai-dgn010-cost-qualification`: [separate neue Nativewelle](SQL_SERVER_2025_AI_DGN010_COST_PUBLIC_REVIEW.md).

Vor erster Admission sechs kohärente Quellenkandidaten/max12 neue eigene serielle
Container, Checkpoint3/hard6. Zwei2025positive, je zwei2019/22-SKIPs vorSetup und
ein2025Setupfault/Recovery; insgesamt sieben feste Slots. Vollständige aktuelle
Publicquellenbindung nach alleiniger EOL-Normalisierung, ausgeführte Rohbytes
jeAdmission zusätzlich. Enger unabhängiger neuer Input-/Adapter-/Budgetreview
ohne offene P1/P2; bestehende Endstatus-/Containerfloors unverändert.

Native noch offen. 300 Sekunden regulär/einmal60gesamtCleanup einschließlich
frischer DB-Abwesenheit und voll gebundenem CID-/Namensabbau. UNKNOWN sperrt SQL
und erhält Inputs, keine ungebundene Rettung oder Ledgerreset. Provider-/Cloud-/
ONNX-/Hostgrenzen unverändert. DGN-010 PROPOSED/Producer WARN; volle Runtime/
TP-PERF/Worker/Commit/Nettonutzen/Modulabnahme bleibt NOT_ESTABLISHED.

### Öffentliche Kosten-C1 vollständig nativ bestanden

Alle sieben festen eigenen Slots bestanden: zwei2025positive/WARN, je zwei
2019/22-SKIP_VERSION vorSetup, ein tatsächlicher erwarteter FAIL_EXECUTION nach
PASS-Setup mit vollständiger Recovery. 97 protokollierte Nativephasen ohne
Readiness-/separate Engineversionqueries; acht DDL-Fenster, 16000 Source-/20000
Vollstate-Rows, vier echte51003-Abweisungen/Source-Restore. Alle sieben DB-/
CID-/Namenslifecycles geschlossen, eigene Ownerlabel-Inventur leer, Inputs
abwesend/keinUNKNOWN. C1/sieben Container verbraucht, keine Nativekorrekturwelle.

Alle Native-Vollframes/Records/negativen Fehlerframes/Source-/State-/DDL-/
Caller-DB-/OID-/Aggregate-/Cleanupbelege rein an tatsächliche ausgeführte Quellen
gebunden; null zusätzlicher SQLaufruf dafür. Sämtliche acht Zahlen einschließlich
CREATE49211us/Cpu46 aus Profil1 bleiben erhalten und jeProfil getrennt.

Ein zusätzlicher reiner EOL-Bindungshelfer war zunächst zu eng; erste Admission
startete nach dessen FAIL. Scope/Budget/Safety bereits kanonisch registriert und
im Adapter durchgesetzt. Danach raw- oder ausschließlichEOL-identische Review-
Quellen korrekt gebunden, keine Codeänderung/Nativewiederholung. Privater Receipt
erst danach erstellt; Ablaufbefund bleibt im konkreten Nachweis sichtbar.

Begrenzte öffentliche Kosten-/Versions-/Setuprecoveryqualifikation PASS; tatsächlicher
Producer WARN/DGN-010 PROPOSED. Runtime/TP-PERF/Worker/Commit/Nettonutzen/Lehrpfade/
Modulabnahme bleiben offen. Aktuelle Head-/Main-/PR-/Tree-/FF-/Ownbranchgates folgen;
danach nächste unabhängige offene Kosten-/Lehrpfadfrage, keine grünen Wiederholungen.

## TSK-012: konkrete Teaching Paths zum erweiterten Einsteigerdeck

PR210 vollständig abgeschlossen: main 658ed3be28e8c349e5270a0a2c98cc32cfaaf264,
sieben Head-/fünf Main-Workflows PASS, tatsächliche Runtimeauswahl False, ganzer
Tree gleich, FF-main sauber und eigener lokaler/Remote-Branch entfernt. Alle
sieben eigenen Cost-Nativecontainer/Inputs abwesend. Unmittelbare unabhängige
Fortsetzung auf `codex/sql2025-ai-beginner-teaching-paths`:
[konkrete Teaching Paths](../HowTo/SQL_SERVER_2025_AI_TEACHING_PATHS.md) für61Folien.

Gemeinsamer90-Minuten-Einstieg: bekannte Quelle/SELECT, einzelne KI-Begriffe,
Version/Client/CL/Lab/Rechte, geometrische Vorhersage/SQL/Ergebnis, echte Modell-
hürden und Quelle/Antwort/Nichtantwort. BASIS240brutto/210netto/30Pause,
STANDARD480/420/60 mit allen acht Offlineaufgaben, VERTIEFUNG960/840/120 über
zwei Tage mit abgegrenzten Beleglese-/Entwurfsaufgaben. Aktuelle kanonische
Fenster ersetzen alte150/390/640 als neue Unterrichtsplanung; historische
Modulgewichte bleiben erhalten. Foliennummern aus tatsächlicher Masterquelle.

Alle Zeiten ungemessene Planwerte, keine tatsächliche Teilnehmer-/Generalprobe.
Lösungen/Rubrik ausschließlich im bestehenden Arbeitsheft, keine neue Bewertung
oder Liveausführungsfreigabe. Kein neues PPTX/Render/Office-/SQL-/Providerprofil.
Lehrpfad-Praxis/Freigaben/volle TP-PERF-/Modulabnahme und TSK012/014 bleiben offen.
Kleine reine Planung: ein Owner, keine zusätzliche Reviewkette; aktuelle lokale
Summen-/Link-/Material-/Privacy- und Head-/Main-/PR-/Tree-/FF-/Ownbranchgates folgen.

## TSK-004: neue begrenzte CL-Istwertqualifikation

PR211 vollständig abgeschlossen: main 3675a8c3663155519da548de5560fdecc1dc0d95,
neun Head-/sieben Main-Workflows PASS, RuntimeauswahlFalse, ganzerTreegleich,
FF-main sauber/eigener lokaler undRemoteBranchentfernt. TeachingPaths geplant,
keine Teilnehmer-/Zeit-/Generalprobenabnahme; PPTXunverändert. UnmittelbareFolge
auf `codex/sql2025-ai-cl-result-qualification`: [neue CL-Istwertwelle](SQL_SERVER_2025_AI_CL_RESULT_REVIEW.md).

VorAdmission sechs neuekohärenteKandidaten/max12 zusätzlicheeigeneContainer,
Checkpoint3/hard6/zwei stabilevollständigeProfile. Alte dreiContainer/FAILs und
fehlende frühereSQL-Abwesenheitsbelege bleiben erhalten, keinLedgerreset.
NativeCL150/160/170: tatsächlicheSkalare/normalisierteKoordinaten, explizite
NULL-Gates/24 erwarteteNativeNULL-Rejections jeProfil, volleChunkrows oder
volleErrorNumber/Severity/State/Line/Procedure/Messagebytes. Keine erzwungene
LowCL-Denialannahme, dokumentierteGrenze vonbeobachtetemBuildresultat trennen.

Acht reineMethoden/CLIhelp undengerunabhängigerQuellenabschluss nachgeschlossener
Dependency-P2 bestanden. Neue eigeneCL-DB/Marker, gleicherKnownEnd/300-60-/
vollgebundenerCID-/Namenscleanupfloor; tatsächlicherCL170BaselineRestore.
Native zunächst offen; keineLockerungöffentlicherCL170Demos oderProvider-/
Cloud-/ONNX-/Hosteffekte. TSK004/volleDemo-/Curriculum-/Workstreamabnahme offen.

### Neue CL-Istwert-C1 zweimal nativ bestanden

Je48 protokolliertePhasen ohneReadiness-/Versionbootstrap, sechs vollständige
Skalarrecords/48 nativeNULL-Abweisungen/sechs volleChunkrecords/16Vollstates und
zwei vollständigeCL170BaselineRestores. BeideeigeneDB-/CID-/Namenslifecycles
geschlossen, Ownerlabelinventurleer, Inputsabwesend/keinUNKNOWN; einneuer
Ausführungskandidat/zweiContainer, alte dreiFAIL-Container unverändert erhalten.

TatsächlicheSkalare beiCL150/160/170: Dimensions3/float32, Norm5,
UnitNorm1.000000023841858, Euc0/Dot-25/Cos0 undalle drei normalisierten
Koordinaten. Vorabfixierte1e-5-Toleranz, keinebitgenaue1 behaupten.
BeiCL150/160 tatsächlicherChunkError102/Severity15/State38/Line3/ProcedureNULL
mitvollenMessagebytes „Incorrect syntax near '='.“; kein208 undkeinekorrekten
Chunkrows. DeralteDenialoracle-FAIL ist erklärt; OBSERVED_OTHER_ERROR_NO_AVAILABILITY_CLAIM,
keine generelleLowCL-Funktionsfreigabe. CL170vollständigezweiFixtureRows.

AlleNative-Skalar-/NULL-Fehler-/Chunk-/State-/Caller-/Source-/Restore-/
Abwesenheitsframes rein gebunden, null weitereSQLcalls dafür. Begrenzte
Istwert-/Oracle-/Fehleraufbewahrungs-/Restore-/CleanupqualifikationPASS;
öffentlicheCL170Profile/alteFAILs erhalten, volleTSK004-/Provider-/Demo-/
Curriculum-/Workstreamabnahme offen. AktuelleHead-/Main-/PR-/Tree-/FF-/
Ownbranchgates folgen; danach nächste unabhängigeoffeneQualifikationsfrage.

## TSK-007: aktuelle öffentliche Providerverträge

PR212 vollständig abgeschlossen: sieben Head-/fünf Main-Workflows bestanden,
Squash187ecae23d20c724e4a060ae909f6f237ff2ce60, vollständiger Tree
5d24a814a996795517a3a64c8e5f429ac8857a6b exakt übernommen; main synchronisiert,
sauber und eigener lokaler/Remote-Branch abgebaut. Danach den aktuellen lokalen
Modellpfad quellengebunden geprüft.

[Aktueller Modellpfadbefund](../HowTo/SQL_SERVER_2025_AI_MODEL_PATHS.md#aktualisierte-öffentliche-verträge-am-2026-10-12)
am sauberen Lab-Commit f4c9fcd30c397e25c95e57d7aeecc98dc194063e:
RAG weiterhin BLOCKED_DEC033, tatsächliches sqlcmd-Passwortargument und kein
öffentlicher alternativer Executor. Neue öffentliche Shared-Gateway-Sitzungs-
APIs sind vorhanden, Backendvertrag Llama.cpp/OVMS, keine allgemeine Ollama-
Bridge. Lokaler Ollama-Probe/Katalog erfolgreich; kein Modell aufgerufen und
keine Capability-/Digest-/Qualitätsabnahme daraus abgeleitet. Sieben betroffene
Labquellen bytegebunden, null SQL/Inferenz, andere Repositories unverändert.
TSK007/Live-RAG/volle Abnahme offen, alte FAILs und Cloud-/ONNX-/Hostgrenzen
erhalten. Aktuelle PR-/Head-/Main-/Tree-/FF-/Ownbranchgates folgen; anschließend
unmittelbar unabhängige Kostencontrollerqualifikation aus TSK013.

## TSK-013: getrennte Kostencontroller-Gateprüfung

PR213 abgeschlossen: acht Head-/sechs Main-Workflows PASS, Squash
e15e821ebfe99ff23924fb2498e218f0dd1c0193, voller identischer Tree, main FF/sauber,
eigener lokaler/Remote-Branch entfernt. RAG-Secretblocker bleibt sichtbar. Danach
unmittelbar [Kosten-CI-Consumer](SQL_SERVER_2025_AI_DGN010_COST_CI_REVIEW.md)
vorbereitet: zehn synthetische Consumermethoden/elf Selector-Methoden PASS,
volle bounded Record-/Aggregate-/Negativ-/Cleanupbindung und fail-closed2025Gate.
-y0-Adapter ermöglicht Vollframes bei unverändertem Remote-End-/Envsecretvertrag.
Keine lokale SQLwiederholung. Sechs Quellenkandidaten/Checkpoint3/hard6, maximal21
eigene CI-Container einschließlich Integration. Die bestehende Mainmatrix lief
nach PR333 auf `ec4907c32c1f40506d70b90558d8c2ea448e69bd` erfolgreich
(Workflow 40171366457); alle drei Versionsjobs waren grün und die gebundenen
Kostenquellen, der Consumer sowie der Workflow sind seitdem unverändert.
Der Kosten-Consumer meldete auf 2019 und 2022 je zwei `SKIP_VERSION` mit
bestätigtem Cleanup; auf 2025 zwei begrenzte `WARN`-Profile mit Cleanup sowie
den vorgesehenen Setupfehler mit bestätigter Recovery. Damit ist nur dieses
Kosten-CI-Gate begrenzt qualifiziert. DGN010 bleibt `PROPOSED/WARN`; volle
TP-PERF-/Workstreamabnahme bleibt offen, historische FAILs bleiben erhalten.

## TSK-007: lokale öffentliche Modellkomponente

PR214 vollständig abgeschlossen: zehn aktuelle Head-/acht Main-Workflows PASS,
Squash1f4b0f8f9435631977918122d62c337a6665afcd, voller identischer Tree, main FF/
sauber, eigener lokaler/Remote-Branch entfernt. Beide aktuellen nativen Matrizen
separat gebunden: vier2025positive bounded WARN-Profile, acht Versions-SKIPs
vorSetup und zwei erwartete Setupfaults/Recovery; alle sechs eigenen CI-Container
als abwesend belegt. Keine erneute lokale SQLqualifikation, volle Abnahme offen.

Unmittelbar [öffentliche lokale AiModel-Komponente](SQL_SERVER_2025_AI_MODEL_COMPONENT_REVIEW.md)
vorbereitet: ohne SQL/RAG, Nomic768/local, zwei feste synthetische Inferenzaufrufe,
Metadaten vor/nach jedem Call, vollständige numerische Vektoren im privaten
Nachweis und eigenes150s-/5s-Prozessbudget. Drei konkrete P2-Gruppen einschließlich
Recovery-Restpunkt vor Native geschlossen; zwei positive/neun negative reine
Binding-/Vektorfälle und sieben Parentmethoden Normal/-O bestanden. Budget sechs
Quellenkandidaten/max12 Model-/max90Metadatacalls, Checkpoint3/hard6; UNKNOWN
sperrt neue Inferenzadmission. C1-Native-/Integrations-/Cleanupresultate offen,
TSK007/RAG/SQLHTTPS/QRY020/volle Workstreamabnahme offen. Andere Repositories
unverändert, keine Cloud-/ONNX-/rote Hosteffekte, Modell-/Tokenverbrauch unbekannt.

Die getrennte AiModel-C1-Komponente ist inzwischen lokal nativ bestanden: zwei
vollständige768-Vektoren/1536 endliche Koordinaten, wiederholter Input mit
Koordinatendifferenz0 und tatsächlicher gleicher Modell-/Digest-/Versionsbindung;
Vollrecords/Normen/ausgeführte Quellen rein neu gebunden. Eigener Prozess beendet,
keine SQL-/Labänderung oder UNKNOWN. Zwei Inferenzaufrufe, keine Wiederholung
für die Ergebnisprüfung. Begrenzte Entwicklungsevidenz, keine volle TSK007-/
RAG-/SQLHTTPS-/QRY020-Abnahme. Aktuelle Integrationsgates folgen.


## TSK-008/007: fester lokaler Dokument-/Fragekorpus

Frische geschlossene Vorgrenze PR215: 9 aktuelle Head-/7 Main-Workflows PASS,
Squash1ed895bb8bbebef286aeb46cffd4c1c97cdf6d2b, voller identischer Tree
3b38543fbefe0584f5da57326ba9840669cacba1, main FF/synchron/sauber, eigener
lokaler und Remote-Branch entfernt. Die zuvor offenen Integrationsgates sind
geschlossen; die zwei tatsächlichen öffentlichen lokalen Vektorrückgaben
bleiben reine Komponentenevidenz, keine Korpus- oder volle Workstreamabnahme.

Root hat den neuen [privaten Vier-Input-Korpus](SQL_SERVER_2025_AI_MODEL_CORPUS_REVIEW.md)
unabhängig ohne offene P1/P2 geprüft: drei feste englische Dokumente A/red,
B/blue, C/green plus eine feste crimson-Frage, Dokument-/Fragepräfixe explizit,
Fullvector768/finite/Norm und vorab eingefrorenes Cosine-Top1=A. Alle Ties,
identischen Vektoren, fehlende/falsche Input-/Record-/Counterbindungen sind FAIL.
13 reine Pythonmethoden plus PS-Input-/Counterselftest PASS, nur Mock-Popen,
keine Modell-/Metadata-/SQLcalls in der Vorbereitung. Bekannte schmale API-/
CommandInfo-/LabSource-/LocalBinding-/UNKNOWN-Floors wiederverwendet.

Genau sechs kohärente Kandidaten, ein Profil je Kandidat, max24 Inferenz-/162
Metadatenrequests kumulativ, Checkpoint3/hard6. C1 reserviert4+27, Retry0,
30s je Inferenz/5s je Metadata, Parent300s einschließlich Startup plus eine
gemeinsame5s-Reapingdeadline. UNKNOWN sperrt jede Folgeinferenz; historische
FAILs bleiben im Ledger. Rawvectors/Receipt ausschließlich ignoriertesRuntime,
stdout nur Status/Zähler. Quellen-/Lab-/Proof-/Dokumentgates vor exklusiveC1-
Admission; C1-Native-Ergebnis noch offen. Kein SQL-/Cloud-/Generator-/RAG-/HTTPS-
Effekt, keine allgemeine Qualität oder TSK007/008-/QRY020-/Gesamtabnahme.
Modell-/Tokenverbrauch unbekannt; SRC112/113 wiederverwendet, kein Source-ID-Neueintrag.

C1 des festen Dokument-/Fragekorpus lokal bestanden: vier tatsächliche öffentliche
Inferenzcalls/27 Metadatenrequests, vier vollständige768-Vektoren/3072 endliche
Koordinaten, vorabTop1A beobachtet (CosineA0.8031306189541002,
B0.7859511311854047, C0.7826607701190610; Margin0.01717948776869549).
Root hat die Vollrecords und Cosines unabhängig neu berechnet; eigener Prozess
bestätigt beendet, Labquellen/-checkout unverändert, keine SQLcalls/UNKNOWN.
Ein Kandidat verbraucht, keine Wiederholung nach PASS. Dieser einzelne
synthetische Fall ersetzt keine allgemeine Retrieval-/Sprach-/Antwortqualität
oder Live-RAG-/SQLHTTPS-/TSK007/008-Abnahme. Aktuelle Integration folgt.


## TSK-008: SQL-Persistenz des tatsächlichen Modellkorpus

PR216 vollständig abgeschlossen: acht aktuelle Head-/sechs Main-Workflows
PASS, Squash914f8b72f61ab3d538c3898c2b56db4c8dbc4cf8, voller identischer
Tree, main FF/synchron/sauber, eigener lokaler/Remote-Branch entfernt.
Unmittelbar [getrennten SQL-Korpuskomponentenschnitt](SQL_SERVER_2025_AI_CORPUS_SQL_REVIEW.md)
aufgenommen: vorhandener tatsächlicher Vier-Inputreceipt, null neue Inferenz,
VECTOR768/float32 und vollständiges Exact-Retrieval-/Cosineoracle, eigene
Frameworkmarker und tatsächliche Negativ-/Restore-/Abwesenheitskontrollen.
Sechs Kandidaten/maxsechs serielle eigene Container, Checkpoint3/hard6,
300snormal/ein60sCleanup; Quellenreview/Admission/Native noch offen.
Keine Umdeutung von Offline-QRY018, keine Live-RAG-/SQLHTTPS-/Generator-/
allgemeine Qualitäts- oder TSK007/008-Abnahme. Andere Repositories unverändert,
keine Cloud-/ONNX-/Hostkonfiguration, Modell-/Tokenverbrauch unbekannt.

Die getrennte SQL-Korpus-C1 ist anschließend tatsächlich bestanden: ein neuer
eigener SQL17.0.5005.3-Container/CL170,69Nativephasen ohneBootstrap/29Vollstates,
vier vollständige768-float32-Records und unabhängiges Top1A-/Cosine-/Koordinaten-
oracle. Drei tatsächliche51003-Resultatgegenproben,16 tatsächliche51004-
Ownershipabweisungen und4Vollstaterestores. Eigentumsgebundener echterDrop,
Probe-/Parent-DB-Abwesenheit und frischeOwnCID-/Namensabsence, Inputdateien0/
UNKNOWNfalse. EinKandidat/einContainer,0 neueModellaufrufe, keine Runtime-
wiederholung für reinen Vollrecordabschluss; ModeltokensUNKNOWN. Einzelner
synthetischer Suchfall, keine volle Live-RAG-/SQLHTTPS-/Generator-/TSK007/008-
Abnahme; aktuelle Integration folgt.


## TSK-008/007: lokale Generation am geprüften SQL-Snapshot

PR217 vollständig geschlossen:8 aktuelleHead/6Main PASS,
Squash1101a14499e8ee3d6cb009f69c3c7ad09ad7f3fe, vollerTree/FF/synchron/sauber,
eigenerlokaler/Remote-Branch entfernt. SQL-Korpus-C1/OwnDB-/Container-/
Inputcleanup abgeschlossen, keinUNKNOWN. Unmittelbar [lokale Generatorkomponente](SQL_SERVER_2025_AI_GENERATION_COMPONENT_REVIEW.md)
aufgenommen. Begrenzte Discovery3Metadata+1WhatIf,0Inference/SQL, vorhandener
lokaler öffentlicherQwenkey/completion/remoteFieldsnull; keineAntwortabnahme.
PositiveQuelle aus tatsächlich geprüftem unverändertem SQL-Snapshot; drei feste
JSONcases ANSWER/A/red beziehungsweise zweimalABSTAIN/null/null, fail-first
vorFolgecall und unabhängiges Wholeoracle. Max6Kandidaten/18Inference/126Metadata,
CP3/hard6, C1 3+21/300+ein5. Sourceprep/Review/Admission/Native noch offen.
KeineModelldownloads/Neustarts/Cloud-/ONNX-/Hoständerung, ModelltokensUNKNOWN.
Kein vollständigerLive-End-to-End-RAG-/SQLHTTPS-/QRY020-/TSK007/008-Abschluss.

Die lokale Generation C1 ist FAIL_RESULT_CONTRACT: ein Inferenz- und sechs
Metadatenrequests. Der positive Case liefert eine Nichtantwort im Markdown-
Codeblock statt des festgelegten JSONobjekts ANSWER/A/red. Case2 und Case3
wurden nicht aufgerufen; kein ABSTAIN-PASS. Fail-first greift tatsächlich.
Requestenden bekannt, eigener Caller beendet, kein UNKNOWN und keine SQL-/
Hoständerung. C1 bleibt FAIL. C2 ändert ausschließlich den Prompt: festes
crimson=red-Übungsglossar und rohe JSONbeispiele. Quellen-/Fragebytes und alle
Ergebnisoracles bleiben unverändert; keine Codefenceentfernung oder Anpassung
des Solls an das beobachtete Ergebnis. Budget sechs Kandidaten, 18 Inferenz-/
126 Metadatenrequests unverändert; neue Quellenprüfung und Admission vor Calls.

C2 der lokalen Generation ist vor API-Aufrufen mit FAIL beendet: null neue
Inferenz-/Metadatenrequests, keine Records, eigener Caller beendet und kein
UNKNOWN. Nachfolgend festgestellte parallele Lab-Änderungen bleiben unangetastet;
der Receipt enthält keinen konkreten Fehlercode. C3 bereitet einen unveränderten
vollständigen Export des geprüften Lab-Commits in eigenes Runtime mit voller
Tree-/Blob-/SHA-/Populationbindung vor. C2-Prompts und Ergebnisoracles bleiben
unverändert. Beide historischen FAILs bleiben erhalten; bisher insgesamt ein
Inferenz- und sechs Metadatenrequests. Quellenreview und Admission vor C3 offen,
Budget sechs Kandidaten mit Dreiercheckpoint unverändert. Details und Grenzen:
[Generationsnachweis](SQL_SERVER_2025_AI_GENERATION_COMPONENT_REVIEW.md).

Die Generation C3 ist semantisch FAIL: ein Inferenz-/sechs Metadatenrequests,
gültiges rohes JSON mit Nichtantwort im positiven Fall. Weitere Cases wurden
nicht gestartet; eigener Caller beendet, bekannte Requestenden, kein UNKNOWN.
Dreiercheckpoint gebunden; drei FAIL-Kandidaten erhalten, insgesamt zwei
Inferenz-/zwölf Metadatenrequests. C4 ändert ausschließlich die Promptstruktur
und entfernt konkrete Antwortbeispiele; tatsächliche SQL-Quellen, Frage und
Ergebnisoracles unverändert. Hard6 und übrige Effekte unverändert. Quellenreview
und Admission vor weiteren Calls offen; keine allgemeine Qualitätsabnahme.

Generation C4 ist ebenfalls FAIL (ein Inferenz-/sechs Metadatenrequests,
Nichtantwort mit Codeblock im positiven Fall). Eigener Caller beendet,
Requestenden bekannt, kein UNKNOWN; weitere Cases nicht gestartet. Eine
einzelne anschließende read-only Vorlagendiagnose liefert keinen belegten
Enthaltungszwang. C4 inklusive Diagnose sieben Metadatenrequests innerhalb
seiner Reservation21; global tatsächlich drei Inferenz-/19 Metadatenrequests.
Vier historische FAIL-Kandidaten erhalten. C5 wird als kürzere generische
Fallentscheidung bei unveränderten Quellen und Oracles vorbereitet; keine
unveränderte Wiederholung. Hard6 bleibt, neue Review-/Admissiongates offen.

Generation C5 semantisch FAIL: gültiges JSON mit Nichtantwort im positiven Fall,
ein Inferenz-/sechs Metadatenrequests. Eigener Caller beendet, Requestenden
bekannt, kein UNKNOWN. Fünf FAIL-Kandidaten archiviert; global tatsächlich vier
Inferenz-/25 Metadatenrequests. Letzter C6-Kandidat ergänzt separat deklarierte
deterministische Glossarnormalisierung zur erhaltenen Originalfrage. Tatsächliche
SQL-Quelle und Oracles unverändert; Pipelineänderung und eingeschränkter Claim
ausdrücklich sichtbar. Review/Admission offen; nach C6 Hardstop dieser Welle.

Am 2026-11-11 hat der Nutzer sechs zusätzliche Generationskandidaten und die
Änderung im separaten Repository `SQL_Server_Lab` ausdrücklich freigegeben.
C1–C6 bleiben abgeschlossen und unverändert; C7–C12 bilden eine Folgewelle mit
eigenem Ledger, sechs Kandidaten, höchstens 18 Inferenz- und 126
Kandidatenmetadatenrequests, checkpoint C9 und Hardstop C12. Die vollständigen
ursprünglichen Eingaben und Receipts wurden im ignorierten privaten Runtimebereich
gefunden und lokal gebunden.

Für den vorhandenen lokalen Tag `gemma4:26b` wurde der öffentliche Schlüssel
`ollama-gemma4-26b-local` im Lab-Worktree registriert. Betroffene statische
Szenarioprüfung PASS; lokale WhatIf-Planung und read-only Liveidentitätsbindung
PASS, drei Metadatenrequests plus ein WhatIf, null Inferenz. Der Code liegt im separaten Lab-Worktree auf Commit
`f03676acf9aebceaacfa050454520d566c4d45ce`; die Integration ist offen. C7
wurde mit identischen Promptbytes und Oracles unter der neuen Route gestartet.
Der Prozess endete bekannt, aber der Modellrequest-Endstatus ist `UNKNOWN` nach
sechs erfolgreich abgeschlossenen Metadatenrequests und einem gestarteten
Inferenzaufruf. Kein SQL-Aufruf; Modelloutput und Tokens unbekannt. Die
Caller-Diagnose hat den bereinigten API-Fehlercode verworfen; der 56,13-Sekunden-
Lauf bei 45 Sekunden Requesttimeout deutet auf Timeout, belegt ihn aber nicht.
C7 bleibt UNKNOWN. C8 bestätigte `AI_ENDPOINT_TIMEOUT` bei 45 Sekunden,
66,65 Sekunden Gesamtlaufzeit. C9 startete keine Inferenz: der lokale Ollama-
Dienst war beendet, der erste Metadatenrequest erhielt anschließend
`ConnectionRefused`. Der vorhandene Dienst wurde ohne Konfigurationsänderung
neu gestartet. Er meldet jetzt Version `0.40.16`; Gemma-Digest und Completion-
Fähigkeit blieben gleich. Die Caller-Erfassung sanitisiert nun API- und
Metadatenfehlercodes. C10 bestätigte `AI_ENDPOINT_TIMEOUT` auch bei 90 Sekunden;
die Runtime blieb aktiv und das Modell resident, jedoch ohne CPU-Aktivität im
kurzen Nachcheck. C11 erhielt nach 180 Sekunden eine HTTP-Antwort ohne
Generierungstext (`AI_ENDPOINT_GENERATION_RESPONSE_INVALID`), Requests beendet,
bekannter FAIL. C12 erhielt mit 96 Outputtokens nach 19,07 Sekunden denselben
bekannten Fehler. Damit ist die Vermutung widerlegt, nur das 48-Token-Limit habe
den leeren Text verursacht. C7–C10 bleiben UNKNOWN/unverändert; C11 und C12 sind
bekannte FAILs. Alle sechs Kandidaten sind verbraucht, null SQL-Aufrufe und keine
brauchbare Modellantwort. Die Callerdiagnose und der öffentliche Endpointvertrag
wurden lokal nachgebessert: Gemma 4 ist im separaten Lab-Branch an `/api/chat`,
`think: false` und `message.content` gebunden; sanitisiertes Fehlerverhalten und
synthetische Transporttests sind ergänzt. Der gezielte KI-Vertragstest besteht.
Das ist noch kein Laufzeitnachweis am Modell. PR #890 ist inzwischen gemergt;
der API-Fix und seine Integrationsgates stehen im nachfolgenden Checkpoint.
Es wurden keine weiteren Inferenzaufrufe ausgeführt. Details:
[Generationsnachweis](SQL_SERVER_2025_AI_GENERATION_COMPONENT_REVIEW.md).

## Integration des Gemma-4-API-Fixes am 2026-11-12

PR [#890](https://github.com/gecompat/SQL_Server_Lab/pull/890) wurde am
2026-11-12 um 12:35:47 UTC per Squash gemergt. Integrationscommit:
`d7009af9712bc0fd6ac34b2ff0d052e9d673a17d`. Der PR-Run
[43102351575](https://github.com/gecompat/SQL_Server_Lab/actions/runs/43102351575)
bestand mit Classify, Ubuntu-/Windows-Static-Checks, Adapter-, Docker-, Podman-,
Mixed- und Hyper-V-Gates sowie PR Gate. Foundation integrity und der nicht
betroffene Podman-Recovery-Job wurden übersprungen. Das Lab-Worktree steht
sauber auf `main`; der eigene lokale und Remote-Branch sind entfernt.

Der Fix ergänzt im lokalen öffentlichen Ollama-Vertrag die modellbezogene
Auswahl von `/api/chat`, `think: false` und `message.content` sowie
sanitisierte Fehlerbehandlung und synthetische Transporttests. Das behebt die
belegte Vertragslücke des bisherigen Catalog-Pfads. Ob diese Lücke den leeren
Text in C11/C12 konkret verursacht hat, bleibt mangels gespeichertem Rohbody
unbewiesen. C7–C10 bleiben UNKNOWN, C11/C12 FAIL; alle sechs Kandidaten der
Folgewelle sind verbraucht. Es gab keinen weiteren Modell- oder SQL-Aufruf.
Gemma-4-Antwortqualität, erneute Generationsqualifikation und vollständige
TSK-007/008-/Live-RAG-Abnahme bleiben offen und benötigen eine neue endliche
Wellenentscheidung. Der nächste getrennte Entwicklungsbereich ist TSK-009;
seine eigenen Budget- und Qualifikationsgrenzen bleiben maßgeblich.

## TSK-009: SOURCE_ONLY-Poolproducer nach PR226 integriert

Der unabhängige SOURCE_ONLY-Korrekturschnitt des öffentlichen opt-in Poolproducers
wurde über PR [#226](https://github.com/gecompat/SQL_PerformanceSchulung/pull/226)
vollständig integriert. Der PR wurde am 2026-10-12 gemergt. Head
`dec87b692081171538db7e26039fc5ccd1a64ded`, Integrationsstand
`69abfb34e10bd2538190c2759109ab2da827810a`; der vollständige Tree
`6c2f8396baee84dff8546f26885e8fe78bc62505` ist übernommen. Zehn Head- und acht
Main-Gates bestanden, Fast-Forward-Synchronisierung sauber, eigener lokaler und
Remote-Branch entfernt; der isolierte Worktree ist archiviert.

Integriert wurden ausschließlich die gebundenen Quellkorrekturen und ihre
betroffenen statischen Prüfungen: vollständige Podman-ID-Abfragen,
`--time=0`-Namespaceabbau, sticky UNKNOWN für unbeendete mutative Removal und
der geschlossene C1/C2-FAIL-/Recovery-UNKNOWN-Befund. Die vorherige Native-Welle
bleibt nach C2 gestoppt: ein eigener Container, null SQLcmd-/Poolchild-Aufrufe,
C1/C2 FAIL und Cleanup-Request-Ende UNKNOWN. Frische read-only CID-/Namens- und
Inputabwesenheit ist belegt, aber SQLcleanup bleibt NOT_ESTABLISHED. C3 ist nicht
zugelassen; der Merge belegt SOURCE_ONLY, keine öffentliche Pool-/CON-010-/TSK-009-
oder TP-CON-Runtimequalifikation. Eine neue native Frage braucht eine eigene
geänderte Quellen-/Recoveryentscheidung, unabhängigen Review und frische Admission.


## Fortsetzung: QRY-023 – automatisierte Enginequalifikation abgeschlossen

Der korrigierte Proposed-Harness wurde mit den unveränderten, digestgebundenen Linux/amd64-Images und Ressourcenlimits (2 CPU, 4 GiB Container, 3 GiB SQL-Server-Speicher) vollständig auf SQL Server 2019 Build 15.0.4500.2, SQL Server 2022 Build 16.0.4305.5 und SQL Server 2025 Build 17.0.5035.5 ausgeführt. Auf allen drei Versionen bestanden PREFLIGHT, SETUP, FRAMEWORK, WORKLOAD, ADMIN_PERMISSION_INVENTORY, QUALIFICATION_PREFLIGHT, CORRECTNESS, MEASUREMENT, PLAN_EVIDENCE und CLEANUP. Die Datenbank wurde jeweils markergebunden entfernt. Der menschliche Generalprobengate blieb ausdrücklich unberührt.

Die Engineläufe fanden und beseitigten Implementierungsfehler: SQL-2019-`HAS_PERMS_BY_NAME` verlangt für diese Abfragen die NULL-Securable-Klasse statt `SERVER`; der READER-Datenbankbenutzer musste im expliziten Zieldatenbankkontext erstellt werden; Katalogvergleiche benötigen explizite binäre Kollationen; SQLCMD-Variablen akzeptierten den vorherigen Endpunktdatensatz wegen Sonderzeichen nicht; `varchar(8191)` ist unzulässig; leere `subentity_name`-Werte mussten normalisiert werden; Workloadrechte mussten tatsächlich an READER vergeben werden; Messdeltas mussten aus den persistierten `MeasurementRun`-Zeilen gelesen werden. Die Systemobjektbaseline wurde um Kompatibilitätsviews ergänzt und beträgt 186/226/232 Grants mit digestgebundenen vollständigen Datensätzen.

Messung: je Engine fünf gepaarte AB/BA-Läufe mit 10.000 Ergebnissen pro Variante, Warm-up ausgeschlossen. Diese winzige synthetische Labormessung zeigt keine robuste Leistungsrangfolge; CPU-, Lese- und Schreibdeltas waren häufig null. Es wird keine Performanceaussage daraus abgeleitet. Der Code bleibt `PROPOSED`, ist nicht katalogisiert und noch nicht in einen allgemeinen Runtimeworkflow integriert. Offen bleiben Produkt-/Katalogabnahme, eine dauerhaft durchsetzbare Runner-Ressourcenhülle sowie die menschliche Generalprobe (ausdrücklich ausgeschlossen). Der direkte isolierte Einzelaufruf ist kein Ersatz für diese Integration.

Dazu legt der Aufrufer vorab den benötigten `READER`-SQL-Login ausschließlich in der frischen Wegwerfinstanz an. Das getrennte Passwort wird über SQLCMD-stdin provisioniert; das SA-Startpasswort liegt nur in einer kurzlebigen, geschützten Docker-Env-Datei. Die drei Enginejobs laufen jeweils auf einer isolierten GitHub-Hosted-VM und bestehen vor jeder Datenbankänderung einen authentifizierten `SELECT 1`-Logincheck. Der vorgeschlagene Runtimeaufrufer nutzt digestgebundene Images, 2 CPU, 4 GiB Container- und 3 GiB SQL-Speicher. Für die tatsächliche TempDB-Dateizahl verlangt er genau eine Logdatei und 1–15 Datendateien, verteilt ein rechnerisches Maximalbudget von höchstens 1 GiB auf alle Dateien und setzt je Datei 64 MiB Wachstum. Vor Setup werden eine frische Instanz ohne Benutzerdatenbanken und die effektiv gesetzten Dateigrenzen verlangt. Nach einem QRY-023-SQL-Timeout unterdrückt `run_demo.py` das SQL-Cleanup und meldet `FAIL_CLEANUP`, weil serverseitiges Ende und TempDB-Freigabe nicht bewiesen sind. Die äußere CI-Bereinigung entfernt den markierten Wegwerfcontainer nur nach nachgewiesenem SQL-Cleanup; andernfalls bleibt er als Diagnosezustand erhalten. Das bleibt eine vorgeschlagene Einzelrun-Qualifikation, keine allgemeine Runtimefreigabe; `runtime_authorized` bleibt `false`.

Lokal bestanden: sechs neue Caller-/Provisionierungs-/Timeout-Regressionen, 110 QRY-023-Regressionen, Proposed-Vertragsvalidator, FWK-010-Orchestrierungsregressionen und DGN-007-CPython-3.12.14-Profil (26/26 gegen den vorherigen Git-Snapshot). Die drei Enginejobs und das erforderliche unabhängige Methoden-/Code-Nachreview sind für den neuen Kandidaten-Commit offen. Produkt-/Katalogabnahme bleibt getrennt; die menschliche Generalprobe bleibt ausdrücklich ausgeschlossen.


## Fortsetzung: DGN-007 – gemeinsames Runner-AST nach SQLCMD-Handoff neu gebunden

Nach der Änderung der QRY-023-Endpunktübergabe auf `IDGHEXH` meldeten zwei gebundene DGN-007-Offlineprofile `PYTHON_PROFILE_CHANGED`. Der Hash wurde unter CPython 3.12.14 aus dem vollständigen AST von `run_demo.py` berechnet und ausschließlich an dieser Stelle auf `9d1df02d34d74d761aaa496c1490fcbd86fd8abb62ad6cbce99150eb90e5213d` aktualisiert. Fehlerursache bestätigt; keine DGN-SQL-Quelle oder DGN-Methodik wurde geändert. Die bisher fehlgeschlagenen CI-Jobs müssen auf dem neuen Commit erneut grün werden.

Der QRY-023-Timeoutschutz änderte diesen Runner-AST erneut. Unter CPython 3.12.14 aus den Working-Tree-Bytes berechnet und ausschließlich für `run_demo.py` auf `eca5512a16aac7d25fd22eba88348aa2f48f91754a14ef932e197b6802d003b0` neu gebunden. Die acht übrigen AST-Digests und alle DGN-Methoden-/Runtimegrenzen bleiben unverändert. Der commitgebundene Offlineprofil-Lauf bestätigte den Digest in PR #563.

## Fortsetzung: QRY-023 – isolierter Ressourcenaufrufer integriert

PR #563 wurde nach 69 erfolgreichen PR-Checks am 13.11.2026 als Commit `69a6c33915d70ea393fcf6bf6b06526b3cecc51b` integriert. Der vorgeschlagene CI-Aufrufer bestand den vollständigen Zehnphasenlauf auf den digestgebundenen SQL-Server-Builds 2019/15.0.4500.2, 2022/16.0.4305.5 und 2025/17.0.5035.5; darunter waren authentifizierte Bereitschaft, TempDB-Grenzen, READER-Provisionierung, Korrektheit, fünf gepaarte AB/BA-Messungen, getrennte Planevidenz und markergebundenes Cleanup. Die Messwerte begründen weiterhin keine Leistungsrangfolge.

Die erste Runtimewelle fand zwei echte Fehler im vorgeschlagenen Caller: Der TempDB-Guard verglich die Zahl fehlerhafter Dateien mit der Gesamtdateizahl und scheiterte dadurch trotz korrekt gesetzter Limits; nach Korrektur bestand der Guard. Anschließend löste der Container-SQLCMD-Proxy den SQLCMD-`:r`-Include nicht auf, weil der Container keinen Repositorycheckout besitzt. Der Proxy löst nun begrenzt Repository-Includes auf und sendet den Inhalt über stdin; eine Regression schützt Repository-Containment. Beide Fehler wurden vor dem grünen Drei-Engine-Lauf behoben.

Der unabhängige Methoden-/Code-Nachreview des finalen Proxy-Heads fand keine offenen P1/P2. Die QRY-023-Harness- und isolierten Runtime-Workflows auf `main` bestanden ebenfalls. Die integrierte Ausführung bleibt ein vorgeschlagener, isolierter CI-Aufrufer: `PROPOSED`, `runtime_authorized: false`, keine Produkt-/Katalogfreigabe und keine menschliche Generalprobe. Als nächster Schritt werden nur noch belegte Dokumentations-/Registrierungswidersprüche abgeglichen; allgemeine Runtime-, Produkt- und Kataloggates bleiben offen.

## Fortsetzung: QRY-023 – Live-Negativfälle für READER-Inventar

PRs #566–#571 ergänzten die isolierte CI-Matrix um konkrete fail-closed Gegenproben auf den drei gepinnten Builds. Das ADMIN-Inventar wies vor Korrektheit und Messung jeweils genau die erwartete Kategorie ab: direkter zusätzlicher Objekt-`SELECT` plus `db_datareader`-Mitgliedschaft (`DATABASE_PERMISSION`/`DATABASE_ROLE`, PR #566), explizites Objekt-`DENY` (#567), `dbcreator`-Serverrolle (`SERVER_ROLE`, #568), fehlendes erwartetes Tabellenobjekt (`OBJECT_INVENTORY`, #569), serverweiter `VIEW SERVER STATE`-Grant (#570) und explizites serverweites `DENY VIEW SERVER STATE` (#571), beide `SERVER_PERMISSION`. Cleanup bestand jeweils; temporäre Serverrechte wurden unter owner-geprüftem Wegwerfcontainer separat widerrufen und verifiziert. Auf die Negativfälle folgte in jedem Matrixjob ein vollständiger positiver Zehnphasenlauf.

Der erste #570-Kandidat scheiterte auf allen Engines vor der Inventur, weil der serverweite Grant im Ziel- statt im `master`-Kontext ausgeführt wurde. Der Harness-Cleanup bestand. Der Proxy gibt den begrenzten SQLCMD-Fehler nun aus; die Korrektur bindet nur serverweite Modi an `master`. Der finale #570-Lauf bestand. PR #571 bestand nach unabhängigem Review ohne P1/P2 und allen PR-Gates; Mergecommit `ed271d4e3befcbdb8f3f335ed76a82451a478b24`.

Der Dokumentationsabgleich ist für README, Effektivrechte-Design und Status erfolgt. QRY-023 bleibt `PROPOSED`, nicht katalogisiert und `runtime_authorized: false`; Produkt-/Katalogabnahme sowie allgemeine Runtimefreigabe bleiben offen. Nicht ausgeführt wurden absichtlich beschädigte SQL-Kataloge und der menschliche Generalprobengate. PRs #572/#573 prüften datenbankweites `GRANT VIEW DEFINITION` und das entsprechende explizite `DENY`; beide wurden auf den drei Enginebuilds als alleinige `DATABASE_PERMISSION`-Abweichung vor den Queryphasen abgewiesen, mit erfolgreichem Cleanup und positivem Zehnphasenlauf. PRs #574/#575 prüften `CONNECT`-Grant und `DENY` auf `TSQL Default TCP`, jeweils als alleinige `SERVER_PERMISSION`-Abweichung; owner-geprüfter Revoke und Verifikation sowie positive Läufe bestanden. Die ersten 2025-Läufe #572/#574 scheiterten vor dem Harness am `sa`-Login im TempDB-Guard, gezielte frische Wiederholungen bestanden. Mergecommit #575: `1d5217acdd624469cd13940497a6117f17d24e1a`.

PR #576 integrierte die Gegenprobe für einen unregistrierten `STOPPED`-TSQL-Endpoint; die ADMIN-Inventur wies sie auf SQL Server 2019/2022/2025 als `CUSTOM_ENDPOINT` ab und der owner-gebundene Drop bestand. Der erste Lauf scheiterte danach beim READER-Login im positiven Preflight auf allen drei Builds. Nach Verschiebung der globalen Endpoint-DDL hinter den vollständigen positiven Zehnphasenlauf bestanden alle drei Enginejobs und sämtliche übrigen PR-Gates. Mergecommit #576: `18f25931e714505d9128b11e50ce8e8ec14936387`. Eine kontrollierte Wiederholung des positiven Lebenszyklus nach Endpoint-Drop reproduzierte 18456/State 149 (`Login lacks connect endpoint permission`) auf allen Engines. Die begrenzte ADMIN-Diagnose zeigte nach dem Custom-Endpoint-Fall, dass explizites `public CONNECT` nur noch auf den Standardendpoints 2, 3 und 5 vorhanden war; der Eintrag für `TSQL Default TCP` (Endpoint 4) fehlte. DEC-083 verbietet dem Harness, `public`- oder Endpointrechte zu verändern. PR #577 entfernt deshalb den Wiederholungslauf: die Custom-Endpoint-Gegenprobe bleibt nach dem positiven Lauf als letzte Mutation in ihrer owner-markierten Wegwerfinstanz; danach löscht der bestätigende Cleanup die ganze Instanz, ohne Rechtebaseline nachzuschreiben. Die vorherige direkte READER-Anmeldung in `master` war ungeeignet, weil der Login dort nicht provisioniert ist.

PR #578 qualifizierte den direkten `GRANT VIEW ANY DATABASE` an `READER` auf allen drei Builds als alleinige `SERVER_PERMISSION`-Abweichung; der owner-gebundene `REVOKE` und Abwesenheitsnachweis sowie der nachfolgende positive Zehnphasenlauf bestanden. Mergecommit #578: `44c7714bfbb0319ff45d605b0db64641f2b8242e`.

PR #579 qualifizierte den direkten `DENY VIEW ANY DATABASE` an `READER` auf allen drei Builds als alleinige `SERVER_PERMISSION`-Abweichung; der owner-gebundene `REVOKE`, Abwesenheitsnachweis und positive Zehnphasenlauf bestanden. Mergecommit #579: `39b517d4f393b2238620d1052f009237fbb18416`.

PR #580 integrierte die direkte `DENY CONNECT SQL`-Gegenprobe. Der erste Drei-Engine-Lauf klassifizierte den DENY korrekt, aber der Restore entfernte auch das bestehende erlaubte `GRANT CONNECT SQL`; der folgende Reader-Preflight scheiterte. Der Injektor bindet jetzt den ursprünglichen GRANT als Vorbedingung, und der Restore widerruft nur den DENY, stellt bei Bedarf den GRANT wieder her und verifiziert beides. Der korrigierte Drei-Engine-Lauf und alle vorgeschriebenen PR-Gates bestanden; Mergecommit `232b3c583f5aa25d1b8a9c9be2012b1116fa174c`.

PR #581 integrierte die direkte Mitgliedschaft von `READER` in der Serverrolle `securityadmin` als zusätzliche Inventargegenprobe. Auf SQL Server 2019/2022/2025 wurde sie als alleinige `SERVER_ROLE`-Abweichung vor Queryphasen abgewiesen; Cleanup und der anschließende positive Zehnphasenlauf bestanden. Die Injektion verlangte einen bekannten Nichtmitglied-Ausgangszustand; der owner-geprüfte Restore lief nur nach bestätigtem Injektionsmarker. Der erste frische 2025-Job scheiterte vor Setup im TempDB-Growth-Guard, weil zwei Dateien noch `MAXSIZE = UNLIMITED` meldeten; der gezielte Wiederholungslauf bestand vollständig. Mergecommit `f2d36454d03d256f1d762284fdcc6fd4604c5043`. QRY-023 bleibt `PROPOSED`, nicht katalogisiert und `runtime_authorized: false`.


## QRY-023 TempDB-Guard – bounded file-set convergence (PR #583)

Der SQL-2025-Fehler in PR #581 zeigte anhand der Diagnose: Der Guard berechnete das Limit zunächst mit drei beobachteten Dateien (341 MiB je Datei), während TempDB bis zum Nachcheck auf fünf Dateien anwuchs; die beiden neuen Dateien behielten `MAXSIZE = UNLIMITED`. PR #583 ersetzt den Einzelversuch durch maximal 16 begrenzte Konfigurationsdurchläufe und verlangt zwei aufeinanderfolgende stabile, vollständig gedeckelte Dateisatzbeobachtungen. Der Guard bleibt vor jedem Datenbank-Setup fail-closed. PR #583 bestand Review, statische Prüfung und die Drei-Engine-Qualifikation.

## QRY-023 RunToken- und Zielnamen-Randfälle

PR #586 ergänzte den T-SQL-Preflight um den Vergleich von `DATALENGTH` und
`LEN`, da `LEN` nachgestellte Leerzeichen ausschließt und ASCII-`LIKE` sie
ignoriert. Die live injizierte RunToken-Gegenprobe wurde auf SQL Server
2019/2022/2025 vor Setup mit `FAIL_CONTRACT` abgewiesen; unabhängige
Containerabfragen belegten jeweils keine Nutzerdatenbank, und die owner-
geprüfte Containerbereinigung bestand. PR #586 ist in `main` integriert.

PR #587 ergänzte danach den binären Namensvergleich und Bytelängenvergleich
für `TargetDatabase`; die Gegenprobe für ein nachgestelltes Leerzeichen wurde
auf allen drei Engines vor Setup abgewiesen, ohne eine Nutzerdatenbank
anzulegen.

PR #588 verbreiterte die Demo-ID-Variable, sodass vorzeitige Kürzung nicht mehr
eine ungültige Eingabe kaschiert, und fordert exakt sieben Bytes sowie den
BIN2-Wert `QRY-023`. Die Live-Gegenproben für ein angehängtes Leerzeichen und
eine kleingeschriebene Demo-ID mit konsistent abgeleitetem Zielnamen wurden auf
allen drei Engines vor Setup abgewiesen; Nutzerdatenbanken blieben aus und der
Cleanup-Marker bestand. Damit sind die drei benannten SQLCMD-Identitätsgrenzen
getrennt live qualifiziert. QRY-023 bleibt `PROPOSED`, nicht katalogisiert und
`runtime_authorized: false`; die
allgemeine Produkt-/Katalogfreigabe und die ausdrücklich ausgeschlossene
menschliche Generalprobe bleiben getrennte Grenzen.

## Fortsetzung: QRY-023 – Timeout unterdrückt SQL-Cleanup (PR #590)

Die isolierte Workflow-Gegenprobe prüft mit einer synthetischen 30-Sekunden-
`WAITFOR`-Planphase und einem 5-Sekunden-Phasenbudget, dass `run_demo.py` den
Timeout als `FAIL_TIMEOUT` meldet, den SQL-Cleanup unterdrückt und wegen
unbewiesenem Serverende mit `FAIL_CLEANUP` endet. Auf SQL Server 2019, 2022 und
2025 bestanden die Markerprüfung für die erhaltene Zieldatenbank und die
begrenzte Kontrolle, dass die SQL-Anfrage beendet ist. Die CI führt erst danach
einen getrennten Recovery-Cleanup mit dem vorhandenen exakten Eigentumsvertrag
aus; Containerentfernung folgt nur nach dessen Bestätigung. Der Nachweis zeigt
nicht, ob die Anfrage serverseitig abgebrochen oder bis zum natürlichen Ende
der `WAITFOR`-Dauer ausgeführt wurde. Allgemeine Prozessbaum- und
Serverabbruchsemantik bleiben offen. Die PR-Gates bestanden; der unabhängige
Methoden-/Code-Nachreview bestätigte den Fix der abschließenden Logauswahl ohne
neue P1/P2. PR #590 wurde am 2026-11-13 per Squash als
`7e9653fed06b5ae1e53cffdeef64edbb43340f12` integriert; `main` ist mit
`origin/main` synchron und der Arbeitsbaum sauber. QRY-023 bleibt `PROPOSED`,
nicht katalogisiert und `runtime_authorized: false`. Die Produkt-/Katalogabnahme
bleibt getrennt; die menschliche Generalprobe bleibt ausdrücklich
ausgeschlossen.

## DGN-004 – begrenzter Entwurf zur plan_handle-Provenienz

Der integrierte Capture-Transport erhält weiterhin nur einen vom Aufrufer
gelieferten `plan_handle`; die Offline-Identitätsprüfung authentifiziert weder
Serverzeilen noch aktuelle Ausführung. Der neue
[Provenienzentwurf](DGN_004_PLAN_HANDLE_PROVENANCE_DESIGN.md) schlägt vor, alle
exakt objekt-, quellen- und offsetgebundenen Cachezeilen vor und nach genau
einem eigenen Aufruf vollständig zu erfassen. Ein Handle dürfte erst bei genau
einem Kandidaten mit einer Ausführungsdifferenz von eins freigegeben werden;
fehlende, zusätzliche oder mehrdeutige Zeilen bleiben `NOT_PROVEN`. Der
Quellkandidat ist mit vollständiger DMV-Abfrage, strengem Framevalidator,
variablen 1–64-Byte-Handles, bounded Runner und Delta-Binder implementiert und
über PR #593 als `ee80eb2` integriert. Der unabhängige Review bestätigte nach
Korrektur eines veralteten Backlogstatus keine weiteren P1/P2. 83 lokale
DGN-004-Tests (ein POSIX-Skip), Framework-Validator und ScriptDom-Syntaxparse
150/160/170 bestanden. Nicht SQL-kompiliert oder ausgeführt. Die kontrollierte
Ein-Writer-Zuordnung bleibt eine begrenzte Inferenz. Ein erneuter read-only
Hostcheck am 2026-11-13 fand weiterhin fünf fremde, aktive SQL-Server-Container
(seit rund 23 Stunden aktiv); deren gemeinsamer Snapshot lag bei rund 5,6 GiB
und 30 % CPU. Das belegt keine kontrollierte Optimiererlast. Die fremden
Container blieben unverändert; das YELLOW-Vorstartgate bleibt offen.

## TSK-015 – historische Priorität von aktueller Steuerung getrennt

Die menschliche Lesepfadprüfung führte vom Root-README über die
Dokumentationsübersicht zu Backlog, Ausführungsstand und Masterplan. Der
Pausenauftrag vom 22. Oktober bleibt als historischer Snapshot mit seinen
damaligen Kennungen und Nachweisen erhalten; aktuelle Verweise führen zur
Wiederaufnahme vom 26. Oktober. Der aktive DGN-004-Plan nennt nun den
integrierten Source-only-Stand PR #593 und die weiterhin bindenden YELLOW- und
Vorstartgates. PRs [#595](https://github.com/gecompat/SQL_PerformanceSchulung/pull/595)
und [#596](https://github.com/gecompat/SQL_PerformanceSchulung/pull/596) sind
integriert; unabhängiger Review fand nach Korrektur der Links keine offenen
P1/P2. Der benannte Lesepfadbefund ist behoben. Das ist keine pauschale
Altbestandskonformität; nicht geänderte Lern-/Präsentationspfade wurden nicht
global neu bewertet. Die menschliche Generalprobe bleibt ausgeschlossen.

## Fortsetzung: DGN-007 – operative Profilquelle bleibt unselektiert

Die offizielle Hosted-Runnerroute wurde am 13. November geprüft und als
Sollprofilquelle verworfen: `ubuntu-24.04` zeigt auf ein rollendes Image; die
dokumentierte OS-Pythonversion und die über ein bewegliches Toolcache-Manifest
verfügbaren Python-Versionen sind verschiedene Installationen und liefern
keinen unveränderlichen vollständigen S15-/P11-Erwartungssatz. Der Befund und
die erforderliche Quell-/Build-/Modulbindung stehen in
[§19.2](DGN_007_IMPORT_PROFILE_BINDING_DESIGN.md#192-abgewiesene-auswahl-über-das-rollende-hosted-runner-image).
Es gab keine Installation, Runnerausführung oder Profilaufnahme. Das operative
Inventurgate und das gemeinsame Fünf-Formen-/64-KiB-Gate bleiben offen; weiter
geht es mit einer unabhängig gebundenen, vollständigen CPython-/OS-Auswahl vor
jeder Beobachtung.

## Fortsetzung: DGN-007 – deklarative Ein-Record-Abbildung

Der skalare Capture-Body kann jetzt über einen separaten Mapper als einzelner
prospektiver `RunRecord` strukturiert werden. Der Mapper bindet den erwarteten
Major, Scope, Block/Slot und Contract-/Source-Digests, fordert alle acht
erfolgreichen Phasen sowie Cleanup/Abwesenheit und prüft die vollständigen
Records erneut gegen `_run_valid`. Sieben synthetische Gegenproben, die bestehenden
Transporttests und der Transport-CI-Vertragsvalidator bestanden lokal; die
unabhängige Quellensichtung fand keine P1/P2/P3-Befunde.

Die Phasen-/Cleanupwerte bleiben Callerangaben. Der Mapper belegt weder ihre
Herkunft noch integrierten Freeze, tatsächliche Quellenverwendung, Zielinstanz,
Ressourcen, reale Reihenfolge oder Budgets und führt keine SQL-Runtime aus. Der
verlustfreie vertrauensgebundene Coordinator ist weiterhin offen; die
Incidentbewertung und Methodenfreigabe bleiben unverändert.

Der Backlogstatus zur früheren G13-Reporterarbeit war veraltet. Die Remoteprüfung
bestätigte PR 68 als geschlossen und nicht gemergt; der Fehler-only-Reporter
wurde nach DEC-072 verworfen. PR 130 (begrenzte Rawdiagnose) und PR 132 (finaler
Parser-/Methodenschnitt) sind gemergt. Die offene Coordinatorarbeit ist davon
getrennt und bleibt offen.

## Fortsetzung: DGN-007 – CPython-Profilquelle als Kandidat eingegrenzt

Nach Ablehnung des rollenden Hosted-Runner-Labels wurde ein aktueller, exakter
Quell-/Imagekandidat geprüft: CPython 3.12.16 mit offiziellem Quellarchivdigest
und Python-Official-Image-Manifestdigest. Der fest gebundene Dockerfile-Commit
verwendet den signierten Python-Quellrelease; `apt-get update` und weitere
Build-/Hostparameter verhindern jedoch, den Container allein als unabhängige
Buildattestation zu verwenden. Das Linux/amd64-Childmanifest, seine Config und
sieben Layerdigests sind festgehalten. Der digestgebundene Pull und eine
begrenzte CPython-3.12.16-Probe ohne Netzwerk und mit read-only RootFS liegen
vor. `docker image inspect` meldete die Repository-Digestreferenz des
linux/amd64-Childmanifests; die sieben Engine-/Config-DiffIDs stimmen überein.
Das ist keine unabhängige Buildattestation oder Profilaufnahme. Vollständige
S15-/P11-Sollrecords, gebundene Bootstrap-/Profilbytes, Quellenherkunft und das
Fünf-Formen-/64-KiB-Gate bleiben offen. [Detail und Quellen](DGN_007_IMPORT_PROFILE_BINDING_DESIGN.md#193-offizieller-cpython-quellrelease-mit-digestgebundenem-oci-kandidaten).

Ergänzend wurde das offizielle CPython-3.12.16-Quellarchiv heruntergeladen,
seine veröffentlichte SHA-256-Summe lokal bestätigt und seine GnuPG-Signatur
mit dem gegen Python.org und den gepinnten Dockerfile abgeglichenen
Release-Fingerprint verifiziert. Das belegt den signierten Quellrelease,
nicht dessen tatsächliche Verwendung im Container-Build. Die erste
quellbezogene Sichtung benennt `getpath.py`, `sysconfig.py`, `Setup.stdlib.in`
und `frozen.c`; buildabhängige Auswahl und komplette S15-/P11-Sollrecords sind
weiterhin offen. Keine Quelle wurde ins Repository übernommen oder kompiliert.
[Signatur- und Quellenbefund](DGN_007_IMPORT_PROFILE_BINDING_DESIGN.md#195-separat-verifizierter-cpython-quellrelease).

## Fortsetzung: DGN-007 – importierte Klassenmethoden statisch verfolgt

Der CPython-3.12.16-Offlinekandidat folgt jetzt zusätzlich Aufrufen importierter
Quellklassenmethoden über direkte Klassenaliase und Modulaliase sowie Konstruktoren
mit vorhandenem `__init__`. Vier neue synthetische Regressionen prüfen diese Pfade
und stellen sicher, dass nicht aufgerufene Methoden geschlossen bleiben. Der isolierte
Static-Test besteht mit 32/32. Die signaturgeprüfte Archivmessung bleibt
`CANDIDATES_ONLY`: 92 Module, 568 Kanten, 225 verfolgte lokale Funktionen,
22 entschiedene und 605 unbekannte Bedingungen, Digest
`f3edce40f628d8ef5a36e779378662e9de8e1a571c8dd0c288b70517ede68973`.
Die Zählkorrektur und Grenzen sind in §19.15 des
[DGN-007-Designs](DGN_007_IMPORT_PROFILE_BINDING_DESIGN.md#1915-lexikalische-cpython-quellkandidaten-und-importgrenze)
dokumentiert. Keine Interpreter-, Profil-, Worker-, SQL- oder Generalproben-Ausführung;
operative S15-/P11-Inventur und Fünf-Formen-/64-KiB-Gate bleiben offen.

## Fortsetzung: DGN-007 – Modulaliase aus `from ... import ...`

Der statische CPython-3.12.16-Kandidatenpfad bildet nun auch Modulaliase ab,
die mit `from package import module [as alias]` und relativen Varianten
importiert werden. Vier neue Regressionen prüfen importierte Quellfunktionen,
Klassenmethoden, Konstruktoren sowie die Begrenzung unaufgerufener Funktionen.
Der isolierte Testlauf besteht mit 36/36. Der archivgebundene Lauf bleibt
`CANDIDATES_ONLY`: 92 Module/572 Kanten/274 lokale Funktionen, 22 entschiedene
und 973 unbekannte Bedingungen. Der Quelldigest bleibt unverändert, da keine
neuen Quelldateien hinzukommen. Die vollständige Aufrufclosure, S15-/P11-
Sollinventur und das Fünf-Formen-/64-KiB-Gate sind weiterhin offen; es gab
keine Zielinterpreter-, Profil-, Worker-, SQL- oder Generalproben-Ausführung.

## Fortsetzung: DGN-007 – direkte Methodenaufrufe auf Konstruktorergebnissen

Der Offline-Kandidatenpfad folgt jetzt zusätzlich `Klasse().Methode()` für
lokale Klassen, importierte Klassenaliase und Quellmodulealiase. Vorhandene
`__init__`-Bodies werden mitverfolgt. Eine Negativregression bestätigt, dass
`make().run()` keinen spekulativen Rückgabetyp erhält. 40/40 synthetische
Static-Tests bestehen. Der CPython-3.12.16-Archivscan bleibt
`CANDIDATES_ONLY`: 92 Module, 572 Kanten, 331 besuchte lokale Funktionen,
22 entschiedene und 1.061 unbekannte Bedingungen; Digest unverändert.
Beliebige Instanzvariablen, Factory-Rückgaben und dynamische Bindung bleiben
offen. Es gab keine Zielruntime-, Profil-, Worker-, SQL- oder Generalprobe.

## Fortsetzung: DGN-007 – Methoden über direkte Instanzbindungen

Der Kandidatenscan löst nun außerdem einfache gleichscope Zuweisungen aus
direkten bekannten Konstruktoren auf und verfolgt danach Methodenaufrufe auf
diesem Variablennamen. Drei positive Regressionen decken lokale Klassen,
Klassenaliase und Modulaliase ab; ein Factory-Rückgabewert wird ausdrücklich
nicht typisiert. 43/43 synthetische Tests bestehen. Die gebundene
CPython-Archivmessung bleibt `CANDIDATES_ONLY`: 92 Module, 572 Kanten, 351
besuchte lokale Funktionen, 22 entschiedene und 1.126 unbekannte Bedingungen;
Quelldigest unverändert. Rebinding kann überzählen; beliebige Factory-,
Instanz-, Vererbungs- und Laufzeitbindungen bleiben offen.

## Fortsetzung: DGN-007 – einfache Instanzaliase

Eine einfache Zuweisung `anderer_name = worker` übernimmt jetzt die bekannte
direkte Klassenbindung innerhalb desselben Scopes. Zwei neue Regressionen
decken lokale und importierte Klasseninstanzen ab; eine Factory-Rückgabe wird
auch durch Aliaszuweisung nicht geraten. 45/45 synthetische Tests bestehen.
Der Archivscan bleibt `CANDIDATES_ONLY`: 92 Module/572 Kanten/352 besuchte
Funktionen, 22 entschiedene und 1.127 unbekannte Bedingungen; Quelldigest
unverändert. Unbekanntes Rebinding hebt frühere Kandidatenzuordnungen nicht
auf und kann daher weiterhin überzählen.

## Fortsetzung: DGN-007 – gebundene `self`-/`cls`-Methodenaufrufe

Innerhalb eines bereits aufgerufenen Klassenmethodenbodys verfolgt der Scanner
jetzt direkte Methodenaufrufe über den ersten Positionsparameter. Explizite
`@staticmethod`-Methoden werden als ungebunden behandelt; `super()`, Vererbung
und MRO bleiben offen. Drei Regressionen prüfen die beiden gebundenen Formen
und den statischen Negativfall. 48/48 synthetische Tests bestehen. Der
archivgebundene Kandidat zählt 92 Module, 572 Kanten und 431 besuchte Funktionen
bei 22 entschiedenen und 1.387 unbekannten Bedingungen. Digest unverändert;
keine vollständige Closure oder P11-Aussage.

## Fortsetzung: DGN-007 – Receivercontext und Decoratorgrenze

Der gebundene `self`-/`cls`-Methodenkontext wird jetzt an direkt verschachtelte
lokale Helfer weitergereicht, wenn deren Zugriff den äußeren Receiver nicht
überschattet. Das direkte Dekoratorwort `@staticmethod` wird nur dann als
ungebundener Builtinmarker verwendet, wenn keine mögliche Neubelegung des
Namens im Modul-AST gefunden wird; qualifizierte unbekannte Decorators bleiben
konservativ im Kandidatengraph. Fünf Regressionen prüfen Closure, Schatten-
Parameter, benutzerdefinierten Decorator, gewöhnliches Builtin-Shadowing und
Capture-Binding durch `match {**staticmethod}`. 53/53 synthetische Tests bestehen.
Der Archivlauf bleibt `CANDIDATES_ONLY`: 92 Module, 572 Kanten, 433 Funktionen,
22 entschiedene und 1.399 unbekannte Bedingungen; Quelldigest unverändert.

## Fortsetzung: DGN-007 – direkte lokale `super()`-Methoden

Der Offline-Kandidat verfolgt `super().methode()` aus bereits erreichten
Methoden, sofern die Basisklasse direkt lokal benannt und die Zielmethode
quellseitig vorhanden ist. Eine synthetische Regression führt vom
Unterklassen-Entry bis zum Import im Basismethodenrumpf. Exakte gebundene
`super(Klasse, self/cls)`-Formen werden ebenfalls erkannt; Mismatches bleiben
ausgeschlossen. Alternative lokale Klassendefinitionen unter unbekannten
Bedingungen bewahren alle direkt benannten Basen. 58/58 fokussierte Tests
bestehen. Importierte/unbekannte Basen, dynamische explizite Argumente und
vollständige MRO-Auswertung bleiben offen; kein P11-Soll oder vollständige
Aufrufclosure.

## Fortsetzung: DGN-007 – geerbte Receiveraufrufe

Erreichte Methoden verfolgen außerdem `self.methode()` und `cls.methode()`
in direkt benannten lokalen Basisklassen. Zwei Regressionen decken Instanz-
und Klassenmethoden mit ihren Importkanten ab. Die Vereinigungsauflösung über
alternative Basen kann überschreibende Methoden und MRO-Fälle überzählen;
unbekannte/importierte Basen bleiben offen. 56/56 fokussierte Tests bestehen.

## Fortsetzung: DGN-007 – transitive lokale Basismethoden

Der Kandidat löst geerbte Methoden nun über direkte lokale Basen und deren
bekannte lokale Vorfahren auf. `self.method()` und `super().method()` erreichen
eine Methode in der Großelternklasse, auch wenn die Zwischenklasse sie nicht
deklariert. Die Vereinigung der Vorfahren behauptet keine konkrete MRO und kann
bei Overrides Kandidaten überzählen. 59/59 fokussierte Tests bestehen;
unbekannte Basen und vollständige MRO bleiben offen.

## Fortsetzung: DGN-007 – importierte Quellbasen

Direkt auflösbare Basen aus `from package import Base` und gebundenen
Modulaliasen wie `source.Base` speisen nun ebenfalls die geerbten Receiver-
und `super()`-Kandidaten. Zwei synthetische Varianten prüfen die Quellmethoden-
und Importkanten. 60/60 fokussierte Tests bestehen. Externe oder dynamische
Basen und vollständige MRO bleiben offen; Status bleibt `CANDIDATES_ONLY`.

## Fortsetzung: DGN-007 – einfache Basisklassenaliase

Aliaszuweisungen wie `BaseAlias = Base` beziehungsweise
`BaseAlias = source.Base` werden jetzt vor der Basisklassenauflösung verfolgt,
auch für direkt importierte Quellklassen. Drei synthetische Fixtures prüfen
lokale und beide importierten Aliasformen. Eine zusätzliche Verzweigungsfixture
prüft Aliasverkettung und die Erhaltung beider möglicher Basen samt Imports.
62/62 fokussierte Tests bestehen. Mehrfachzuweisungen können Kandidaten
überzählen. Eine Negativprobe bestätigt, dass ein Factory-Rückgabewert nicht
als Klassenbasis geraten wird. 63/63 Tests bestehen. Externe Basen und
vollständige MRO bleiben offen. Eine Gegenprobe mit gegenseitig zyklischen
Aliasnamen terminiert ebenfalls ohne erfundene Basismethode; 64/64 Tests
bestehen.

## Gebundener Archivscan nach Alias- und Basiserweiterungen

Der erneute CPython-3.12.16-Archivlauf verwendet den Quellhash
`b5796915dc45ff745cfb4e990a7e7c93d6f546328a102ce31448d69ebc37575c`.
Der Aufrufkandidatenpfad zählt 92 Module, 573 Kanten und 473 besuchte
Funktionen; 22 Bedingungen sind entschieden und 1.453 unbekannt. Der
Modul-/Quelldigest lautet
`f3edce40f628d8ef5a36e779378662e9de8e1a571c8dd0c288b70517ede68973`. Der
Status bleibt `CANDIDATES_ONLY`; dies ist keine vollständige Importclosure oder
P11-Sollinventur.

## Fortsetzung: geerbte Konstruktoren und konstruierte Unterklassenmethoden

Bei direkt bekannten lokalen Klassen verfolgt der statische Kandidatenfolger
jetzt auch geerbte `__init__`-Aufrufe durch `Worker()` und geerbte Methoden auf
frisch konstruierten Objekten (`Worker().load()` oder eine gleichscope
gebundene Instanz). Das umfasst direkt importierte Quellbasen und bekannte
transitive Vorfahren. Drei neue synthetische Tests prüfen lokalen geerbten
Konstruktor, lokale geerbte Methode sowie importierte Basis mit geerbtem
Konstruktor und Methode; 67/67 fokussierte Tests bestehen. Der Quellscan bleibt
bei 92 Modulen/573 Kanten und unverändertem Quelldigest; 473 Funktionen werden
besucht und 1.453 Bedingungen bleiben unbekannt. Die Vereinigungsauflösung kann
bei Overrides überzählen; dynamische Basen und vollständige MRO bleiben offen.
Kein Interpreter, Profil, Worker, SQL oder Generalprobe wurde ausgeführt.

## Fortsetzung: importierte Unterklassen im Quellmodul

Importierte Quellklassen berücksichtigen jetzt zusätzlich Methoden und
Konstruktoren lokal bekannter Basisklassen im selben Quelldateimodul. Die
Zuordnung verweist auf die tatsächliche deklarierende Basismethode und deckt
sowohl `from package import Worker` als auch `source.Worker()` ab. Zwei positive
Regressionen prüfen geerbten `__init__`- und Methodenpfad über beide
Importformen; eine Negativprobe verhindert das Erraten dynamischer Basen. 70/70
fokussierte Tests bestehen. Der CPython-Archivscan zählt 92 Module/573 Kanten,
471 besuchte Funktionen sowie 22 entschiedene und 1.452 unbekannte Bedingungen;
der Quelldigest bleibt unverändert. Die Basenvereinigung kann Override-/MRO-
Kandidaten überzählen; importierte Basen aus anderen Quelldateien, dynamische
Basen und vollständige MRO bleiben offen. Kein Runtime-, P11-, SQL- oder
Generalprobenachweis.

## Fortsetzung: Basen aus anderen Quellmodulen

Der importierte Unterklassen-Dispatch folgt jetzt auch direkt auflösbare
Basisklassen aus einem anderen bereits erreichbaren Quellmodul. Unterstützt
sind `from .base import Base` und ein gebundener Modulalias wie
`source.Base`; geerbte Konstruktoren und Methoden werden auf die tatsächlichen
Basismethoden im Quellmodul geroutet. Eine synthetische Fixture prüft beide
Importformen. 71/71 fokussierte Tests bestehen. Die CPython-Archivwerte bleiben
bei 92 Modulen/573 Kanten/471 besuchten Funktionen, 22 entschiedenen und 1.452
unbekannten Bedingungen; Quelldigest unverändert. Mehrfach- und alternative
Basen bleiben Kandidatenvereinigung, unbekannte dynamische Basen und vollständige
MRO bleiben ungelöst. Kein Zielinterpreter, Profil, Worker, SQL oder
Generalprobe wurde ausgeführt.

## Fortsetzung: Aliase importierter Quellklassen

Einfache gleichscope Zuweisungen importierter Klassennamen werden nun für
Konstruktor- und Methodenaufrufe verfolgt, einschließlich verketteter Aliase
und möglicher Alternativen aus unbekannten Modulzweigen. Drei Regressionen
prüfen Aliasverkettung, Erhaltung beider Zweigziele sowie Terminierung von
Aliaszyklen und den Ausschluss dynamischer Factory-Rückgaben. 74/74 fokussierte
Tests bestehen. Aliasauflösung bleibt auf statische Modul-/Kontrollblocknamen
beschränkt; Rebinding kann Kandidaten überzählen. Der gebundene CPython-Scan
bleibt bei 92 Modulen/573 Kanten/471 Funktionen und 1.452 unbekannten
Bedingungen; Quelldigest unverändert. Kein Interpreter, Profil, Worker, SQL
oder Generalprobe wurde ausgeführt.

## Fortsetzung: DGN-007 – Frozen-Quelltabellen und Aliase

Der SHA-gebundene CPython-3.12.16-Scanner bindet zusätzlich
`Python/frozen.c` mit Dateidigest
`ff2d5e301f1725c013788f30882fd48127a9ecfe891bfaa592cc08c284d4f79f`. Der
Parser trennt drei Bootstrapnamen, 15 Stdlibnamen und elf Testnamen; neun
Aliaszeilen werden separat kanonisiert. Die Namensdigests lauten
`cf465d8760d226c854cb90bfcd332fc637242d0eaba1aa831583800d687c6190`,
`d181303a2f9c0f98d142655d3848044edfe7a5f5b6a0811902b107b9deccbf49` und
`abf532872c0cc627b52797fd17ec5c19305f91b3173db543e0359288b1921c37`; der
Aliasdigest ist `cdfccf4b85b455cbd42da046901b125a9a92716413decb8e134b37bd7deb420f`.
Alle Bootstrap- und Stdlibwurzeln liegen in den gebundenen 301 statischen
Stdlibnamen; die Testtabelle ist davon getrennt.

Das ist ausschließlich ein Quelltabellenbefund. Er belegt weder den Build oder
Einsatz dieser Tabellen im Zielimage noch geladene Frozenmodule, beobachtete
Aliase oder P11-Records. Der fokussierte Scannertestsatz besteht 90/90; der
Archivscan bleibt `CANDIDATES_ONLY` mit 93 Modulen, 578 Kanten, 534 Funktionen
und unverändertem Kandidatenzeilendigest
`84f92a01cb9807b1bf35fe37cd1a231642aabf6134fdee82e7fc35dc0df7c091`. Alle 15
S15-Felder, P11-Records, operative Inventur und das gemeinsame
Fünf-Formen-/64-KiB-Gate bleiben offen. Es erfolgte kein Interpreter-, Profil-,
Worker-, SQL- oder Generalprobenlauf.

## Fortsetzung: DGN-007 – strikte Frozen-Tabellenzeilen

Der Parser für `Python/frozen.c` fordert die benannten Sentinels der drei
Frozen-Modultabellen und der Alias-Tabelle; jede andere nichtleere
Nichtkommentarzeile muss vollständig parsebar sein. Dadurch werden fehlende
Sentinels und defekte Aliaszeilen als Fehler gemeldet statt still aus dem
Inventar zu verschwinden. Die synthetischen Parsergegenproben decken fehlende
Sentinels, doppelte Modulnamen und fehlerhafte Aliaszeilen ab; der fokussierte
Satz besteht 92/92.

Der gebundene CPython-3.12.16-Archivscan bleibt `CANDIDATES_ONLY` mit 93
Modulen, 578 Kanten, 534 Funktionen und unverändertem Kandidatenzeilendigest
`84f92a01cb9807b1bf35fe37cd1a231642aabf6134fdee82e7fc35dc0df7c091`. Kein
S15-/P11-, Zielimage-, Laufzeit-, Profil-, Worker-, SQL- oder Generalprobenclaim
ändert sich.

## DGN-007-Profilfixtures: POSIX-Pfade auf Windows-Hosttests

Der synthetische breite Profiltestsatz bildet deklarierte Linuxpfade jetzt mit
`posixpath.isabs` ab, auch wenn der Testhost Windows verwendet. Zuvor wählte
`os.path.isabs` auf diesem Host `ntpath` und wies Linux-Fixtures vor den
eigentlichen Assertions als `ROOT_MISMATCH` zurück. Der vollständige lokale
Satz besteht jetzt mit 57/57 (drei umgebungsbedingt übersprungene Fälle). Es
wurde keine Produktions-Runtimegrenze geändert; dies ist keine CPython-
Zielprofil- oder Profilqualifikation.

## Fortsetzung: DGN-007 – qualifizierte Aliase importierter Klassen

Der statische Kandidatenfolger löst jetzt auch `Alias = worker.Worker` und
`Alias = package.worker.Worker` für gebundene Quellmodule auf, einschließlich
Aliasverkettung. Ein Regressionstest deckt außerdem den zuvor verdeckten
Namenskonflikt bei der Methodenzielsammlung ab: die Aliasliste durfte den
separaten Entry eines importierten Hilfsmoduls nicht ersetzen. 76/76 fokussierte
Tests bestehen. Der SHA-gebundene CPython-3.12.16-Scan bleibt ausdrücklich
`CANDIDATES_ONLY` und zählt nach Korrektur der Entry-Übergabe 93 Module,
578 Kanten, 533 Funktionen, 22 entschiedene und 1.605 unbekannte Bedingungen;
der Quelldigest lautet
`84f92a01cb9807b1bf35fe37cd1a231642aabf6134fdee82e7fc35dc0df7c091`.
Die synthetischen qualifizierten Aliasformen ändern die Archivmenge nicht.
Keine Zielinterpreter-, Profil-, Worker-, SQL- oder Generalproben-Ausführung;
operative S15-/P11-Inventur und Fünf-Formen-/64-KiB-Gate bleiben offen.

## Fortsetzung: DGN-007 – lokale Klassenaliase

Modulweite einfache Klassenzuweisungen wie `WorkerAlias = Worker` und
Aliasverkettungen werden jetzt auch bei `WorkerAlias()` und
`WorkerAlias().run()` aufgelöst. Bekannte Klassen aus alternativen unbekannten
Zuweisungszweigen bleiben Kandidaten. Factory-Rückgaben und Aliaszyklen werden
nicht als Klassen geraten; Aliase in Funktions- und Klassenscope bleiben offen.
Vier neue Regressionen prüfen Konstruktor/Methode, Zweigalternativen,
Negativgrenzen und die Erhaltung importierter Ziele bei lokalem Rebinding;
79/79 fokussierte Tests bestehen. Der gebundene CPython-3.12.16-
Scan bleibt bei 93 Modulen/578 Kanten/534 Funktionen, 22 entschiedenen und
1.605 unbekannten Bedingungen, Digest
`84f92a01cb9807b1bf35fe37cd1a231642aabf6134fdee82e7fc35dc0df7c091`.
`CANDIDATES_ONLY`; keine Zielinterpreter-, Profil-, Worker-, SQL- oder
Generalproben-Ausführung. S15-/P11-Inventur und Fünf-Formen-/64-KiB-Gate bleiben
offen.

## Fortsetzung: DGN-007 – Funktionsscope-Aliase importierter Klassen

Der statische CPython-Kandidatenfolger verfolgt nun auch direkte Aliasnamen
bereits bekannter importierter Klassen in aufgerufenen Funktionen, etwa
`LocalWorker = Worker; LocalWorker().run()`, einschließlich einfacher Ketten.
Factory-Rückgaben, Aliase über verschachtelte Scopes und Klassenscope-Aliase
bleiben offen. Zwei neue synthetische Regressionen ergänzen den fokussierten
Satz auf 81/81 PASS. Der erneute Scan des SHA-256-gebundenen CPython-3.12.16-
Archivs bleibt bei 93 Modulen, 578 Kanten, 534 Funktionen, 22 entschiedenen und
1.605 unbekannten Bedingungen; der Zeilendigest bleibt
`84f92a01cb9807b1bf35fe37cd1a231642aabf6134fdee82e7fc35dc0df7c091`.
`CANDIDATES_ONLY`: keine vollständige Closure/P11-Inventur und keine
Interpreter-, Profil-, Worker-, SQL- oder Generalproben-Ausführung. S15-/P11-
Sollinventur und Fünf-Formen-/64-KiB-Gate bleiben offen.

## Fortsetzung: DGN-007 – Klassenscope-Aliase importierter Klassen

Der statische Kandidatenfolger berücksichtigt jetzt auch direkte Aliase bereits
bekannter importierter Klassen im unmittelbar ausgeführten Klassenkörper samt
einfachen Aliasverkettungen. Zwei neue synthetische Regressionen erweitern den
fokussierten Satz auf 83/83 PASS. Der SHA-gebundene CPython-3.12.16-Scan bleibt
bei 93 Modulen, 578 Kanten, 534 Funktionen, 22 entschiedenen und 1.605
unbekannten Bedingungen; der Zeilendigest bleibt
`84f92a01cb9807b1bf35fe37cd1a231642aabf6134fdee82e7fc35dc0df7c091`.
`CANDIDATES_ONLY`: kein vollständiger Aufrufgraph oder P11-Soll. Verschachtelte
Scopeübertritte, Factory-Rückgaben, Zielruntime, Profil, Worker und SQL bleiben
ungeprüft; die Generalprobe bleibt ausgeschlossen. Operative S15-/P11-
Sollinventur und Fünf-Formen-/64-KiB-Gate sind weiterhin offen.

## Fortsetzung: DGN-007 – ältere Beobachtung und LOCAL-Parameterlast

Der ältere Teilnehmeradapter führt T0 jetzt mit `8/3, 1/3, 5/3, 1/1` und T1
mit `1/3, 8/3, 5/3, 1/1` aus; beide Phasen haben exakt vier erfolgreiche
Suchrequests. `40_Observation.sql` bezieht seine Abschlusszählung nur noch aus
erfolgreichen T0/T1-Profileinträgen, die an die markierte Parent-/Variantmenge,
die gespeicherten Phasen und ihre tatsächlichen Query-Store-Intervalle gebunden
sind. Historische oder ungenutzte Katalogpläne und eine absolute
Mindestplanzahl entscheiden nicht länger über den Beobachtungsausgang. Das
Summary beschreibt die verfügbare Evidenz und behauptet keinen Incident oder
eine Ursache.

Statische Intervall-/Last-/Profil-Fixtures: 9/9 PASS; Compatibility-
Gegenproben: 8/8 PASS; statischer Teilnehmer- und LABSCN-005-Validator PASS.
Der frische nicht-promotende Docker-Teilnehmerlauf auf SQL Server 2025 bestand
Precheck, Zeitfenster, Evidenz, Referenzänderung, Vergleich, Recovery,
Adapter-Cleanup und Lab-Entfernung: RunId
`73c0b191-66e1-4891-b9f2-4ab3a4513571`, Status
`COMPLETED_WITHOUT_PROMOTION`/`REMOVED` (2026-11-13). Dies qualifiziert nur
diesen 2025-Teilnehmerpfad; vollständiger Incidentnachweis, Ursachenbeleg,
Versionsmatrix und Capstone bleiben offen. Die menschliche Generalprobe bleibt
ausgeschlossen.

## Fortsetzung: DGN-007 – Klassenaliase über aufgerufene Nested-Function-Closures

Bereits bekannte importierte Klassenaliase werden jetzt als lexikalische
Kandidaten an aufgerufene innere Funktionen weitergereicht. Verkettete Aliase
wie `LocalWorker = Worker; ChainedWorker = LocalWorker` werden im aufgerufenen
Closure verfolgt. Nicht aufgerufene innere Funktionen fügen keine Imports
hinzu; Klassennamespace-Namen werden nicht fälschlich als Methoden-Closure
behandelt. Drei synthetische Regressionen prüfen diese Grenzen; der fokussierte
Scannerlauf besteht 86/86.

Der erneute SHA-gebundene CPython-3.12.16-Scan bleibt `CANDIDATES_ONLY` mit 93
Modulen, 578 Kanten, 534 Funktionen, 22 entschiedenen und 1.605 unbekannten
Bedingungen sowie unverändertem Zeilendigest
`84f92a01cb9807b1bf35fe37cd1a231642aabf6134fdee82e7fc35dc0df7c091`. Die neue
Form ändert die gebundene Archivmenge nicht. Der lokale breite
`test_dgn007_import_runtime_profile`-Satz scheitert vor diesen Scannerfixtures
an Linux-Profilpfaden, die Windows-Python bei `os.path.isabs` als
`ROOT_MISMATCH` abweist; damit liefert er hier keine Profilqualifikation.
Vollständige Aufrufclosure, S15-/P11-Inventur und Fünf-Formen-/64-KiB-Gate
bleiben offen. Keine Zielinterpreter-, Profil-, Worker-, SQL- oder
Generalproben-Ausführung; die Generalprobe bleibt ausgeschlossen.

## Fortsetzung: DGN-007 – statische `stdlib_module_names`-Quelle gebunden

Der SHA-gebundene CPython-3.12.16-Archivscanner liest jetzt zusätzlich den
generierten `Python/stdlib_module_names.h`-Header. Sein Dateidigest ist
`450581463358b2ffaeca45b261c2e59a41cd6546b487445ed5ff9e0a2b4163a6`; der
Parser zählt 301 sortierte, eindeutige Top-Level-Namen mit kanonischem
Zeilendigest
`8c9e3210ccf408b365cbecd391b5a7bf01fd9f1ec4a22b1993f7cc03693cc7b0`. Alle 93
Wurzeln der bisherigen Modulstart-Quellkandidaten liegen in dieser statischen
Namensmenge.

Dies ist keine beobachtete Eigenschaft `sys.stdlib_module_names` und keine
Build-/Laufzeitattestation. Der gebundene Scan bleibt `CANDIDATES_ONLY` bei 93
Modulen, 578 Kanten und 534 Funktionen; der Kandidatenzeilendigest bleibt
`84f92a01cb9807b1bf35fe37cd1a231642aabf6134fdee82e7fc35dc0df7c091`.
Synthetische Archiv-/Parsergegenproben und der fokussierte Satz bestehen 88/88.
Die vollständigen 15 S15-Felder, P11-Records, operative Inventur und das
Fünf-Formen-/64-KiB-Gate bleiben offen; kein Interpreter, Profil, Worker, SQL
oder Generalprobe wurde ausgeführt.

## Fortsetzung: DGN-007 – gebundene Bootstrap-Setup-Vorlage

Der Scanner bindet `Modules/Setup.bootstrap.in` mit dem bereits geprüften
CPython-3.12.16-Quellarchiv und Dateidigest
`d7a4c34c97f414585c7e8480c106a0f85075fb166d4c82a91c5b0b00df455271`. Die
statische Vorlage enthält 22 eindeutige Modulzeilen, eine davon bedingt:
`pwd` unter `MODULE_PWD_TRUE`. Der kanonische Zeilendigest ist
`c7a4aee7afafc66564299cc149649e936153956c20e75f314f02cd696531e42f`.
Zwei synthetische Gegenproben prüfen bedingte Auswahl und die Zurückweisung
defekter/duplizierter Zeilen; der fokussierte Satz besteht 94/94.

Die Vorlage ist keine Configure-/Build-/Imageattestation und belegt keine
tatsächlich aktivierten Module oder P11-Records. Der CPython-Archivscan bleibt
`CANDIDATES_ONLY` mit unveränderten 93 Modulen, 578 Kanten, 534 Funktionen und
unverändertem Kandidatenzeilendigest
`84f92a01cb9807b1bf35fe37cd1a231642aabf6134fdee82e7fc35dc0df7c091`.

## Fortsetzung: DGN-007 – bedingte Stdlib-Setup-Vorlage

`Modules/Setup.stdlib.in` ist nun separat an den digestgeprüften CPython-3.12.16-
Quellrelease gebunden. Die Vorlage zählt 68 eindeutige Modulzeilen vor dem
Testabschnitt sowie zwölf Testmodulzeilen; alle 80 Zeilen tragen eine
Configure-Bedingung, bei 79 unterschiedlichen Bedingungen. Die vollständigen
Zeilen- und Abschnittsdigests stehen im [Designnachweis](DGN_007_IMPORT_PROFILE_BINDING_DESIGN.md).
Zwei synthetische Gegenproben prüfen Abschnittstrennung und Fehlerablehnung;
der fokussierte Scannertestsatz besteht 96/96.

Das ist keine Configure-, Build-, Image- oder Laufzeitattestation. Aktivierte
Module, konkrete Extension-/Loader-Records, die vollständige P11-Inventur und
alle 15 S15-Felder bleiben offen. Der Offlinekandidatenscan bleibt
`CANDIDATES_ONLY` bei 93 Modulen, 578 Kanten, 534 Funktionen und unverändertem
Zeilendigest `84f92a01cb9807b1bf35fe37cd1a231642aabf6134fdee82e7fc35dc0df7c091`.

## Fortsetzung: DGN-007 – Pfad- und Sysconfig-Quellen gebunden

Die bestehenden Quellpins für `Modules/getpath.py` und `Lib/sysconfig.py`
werden jetzt getrennt syntaktisch ausgewertet. `getpath.py` benennt 14
Pfadvariablen und 20 statisch verwendete `config`-Schlüssel; `sysconfig.py`
enthält fünf literal auswertbare Installationsschemas mit acht Pfadschlüsseln.
Quell- und kanonische Digests stehen im [Designnachweis](DGN_007_IMPORT_PROFILE_BINDING_DESIGN.md).
Der fokussierte Scanner besteht 98/98; der Kandidatenscan bleibt
`CANDIDATES_ONLY` mit unveränderten 93 Modulen, 578 Kanten, 534 Funktionen und
Zeilendigest `84f92a01cb9807b1bf35fe37cd1a231642aabf6134fdee82e7fc35dc0df7c091`.

Die AST-/Literalprüfung startet keinen Interpreter und bestimmt keine
Zielprefixe, Suchpfade, aktiven Installationsschemas oder Loaderwerte. S15-/P11-
Sollfelder, operative Auswahl und das Fünf-Formen-/64-KiB-Gate bleiben offen.

## Fortsetzung: DGN-007 Import-Spec- und Loaderstruktur

Die beiden gepinnten importlib-Quellen sind rein syntaktisch auf acht direkte `ModuleSpec`-Initialisierungsfelder, zwei Builtin-/Frozen-Importer, sechs Datei-/Namespace-/Pfad-Finder-/Loaderklassen und vier zentrale Bootstrap-Aufrufanker abgebildet. Eine synthetische Gegenprobe deckt diese Struktur ab; der fokussierte Satz besteht 99/99. Der CPython-Archivscan bleibt `CANDIDATES_ONLY` mit 93 Modulen, 578 Kanten und 534 Funktionen bei unverändertem Digest. Tatsächliche Zielimage-Specs/Loader, vollständige P11-Records, operative Inventur und das gemeinsame Fünf-Formen-/64-KiB-Gate bleiben offen.

## Fortsetzung: DGN-007 öffentliche Importlib-API

Die gepinnten `machinery.py`-/`util.py`-Quellen binden 28 direkte öffentliche Namen an ihre Quellmodule oder lokale Definitionen (16/12); Zeilendigest `f40ad3be9b2550b9be5e55ed8c3073ea9f64d20eced5afafe8a794d34a2c1f51`. Der fokussierte Satz besteht 100/100, der Archivscan bleibt unverändert `CANDIDATES_ONLY` mit 93/578/534. Die API-Zuordnung belegt keine Zielimage-Installation, Importauswahl oder vollständigen P11-Records. S15, P11, operative Inventur und Fünf-Formen-/64-KiB-Gate bleiben offen.

## Fortsetzung: DGN-007 Builtin-/Configure-Vorlagen

`Modules/config.c.in` und `configure.ac` sind zusätzlich digestgebunden und strukturell geprüft: zwei Inittab-Marker, neun feste Basiseinträge sowie 14 kanonische `MODULE_BLOCK`-/`MODULE_BUILDTYPE`-Zeilen. Eine synthetische Gegenprobe; fokussiert 101/101 PASS. Der Archivscan bleibt `CANDIDATES_ONLY` (93/578/534, Digest unverändert). Kein Configure-/Buildlauf und keine Aktivierungs- oder vollständige P11-Attestation. Die vollständige S15-/P11-Auswahl und das Fünf-Formen-/64-KiB-Gate bleiben offen.

## Fortsetzung: DGN-007 dynamische Importkandidaten

Die statische Quellclosure bezieht verfügbare Paketeltern und konstante Modulnamen in `__import__`-/`importlib.import_module`-Aufrufen ein. Vier Kandidaten kommen hinzu (`concurrent`, `pydoc_data`, `xml`, `xmlrpc`); 268 Module/2.438 Kanten, Closurehash `700ace82b2c5630fc6ac039bb5bed0d788a46f6f8bcd1efba3fc0afb97068b6d`. Der fokussierte Satz besteht 102/102. Berechnete und relative dynamische Namen bleiben ungeklärt. Dies ist weiterhin keine vollständige P11-Importclosure; der getrennte Modulstartscan bleibt 93/578/534.

## Fortsetzung: DGN-007 direkte Factory-Rückgaben

Der Importfolger verfolgt eine einzige direkte Top-Level-Form: abschließendes `return Klasse(...)` nach Importen/Docstring, einschließlich einfacher Aliasbindung und Methodenaufruf. Bedingte/dynamische Rückgaben bleiben unaufgelöst. Zwei synthetische Gegenproben; fokussiert 103/103 PASS. Der CPython-Archivscan bleibt 268/2.438 in der Quellclosure und 93/578/534 im Modulstartfolger mit unveränderten jeweiligen Digests. Keine vollständige P11- oder Runtimeattestation.

## Fortsetzung: DGN-007 einfache bedingte Factoryrückgaben

Direkte Klassenreturns in eng begrenzten `if`-/`else`-Pfaden werden jetzt beidseitig als Kandidaten verfolgt. Komplexere oder dynamische Kontrollflüsse bleiben offen. Fokussiert 103/103 PASS; Archivscan unverändert 268 Quellmodule und 93/578/534 Modulstartkandidaten mit den bestehenden Digests.

## Fortsetzung: DGN-007 Factory-Instanzzuweisung

Factorymethoden mit lokaler direkter Klasseninstanzzuweisung und einfachem `return` werden jetzt ebenfalls verfolgt. Rebinding und komplexe Statements bleiben ausgeschlossen. Fokussiert 104/104 PASS; der CPython-Archivscan bleibt 268 Quellmodule und 93/578/534 Modulstartkandidaten mit unveränderten Digests.

Die Quellclosure verfolgt konstante dynamische Imports nun auch über direkte
Aliase von `importlib.import_module`, `builtins.__import__` sowie die Modul-
Aliase `importlib` und `builtins`. Vier Aliasformen sind synthetisch geprüft;
Variablennamen bleiben unaufgelöst. Fokussiert 105/105 PASS. Archivclosure
unverändert 268/2.438, Digest
`700ace82b2c5630fc6ac039bb5bed0d788a46f6f8bcd1efba3fc0afb97068b6d`;
Modulstartfolger 93/578/534, Digest
`84f92a01cb9807b1bf35fe37cd1a231642aabf6134fdee82e7fc35dc0df7c091`.
Statische Kandidaten begründen keine vollständige P11- oder Runtimeaussage.

Dieselbe Aliasregel verfolgt zusätzlich einfache Funktionszuweisungen und
Aliasverkettungen aus `Assign`-/`AnnAssign`-Statements. Gegenproben für
`importlib.import_module`, `builtins.__import__` und eine zweistufige
Funktionsaliaskette bestehen; berechnete Namen bleiben außen vor. Der AST-weite
Kandidatenscan attestiert keine Scope-/Rebinding- oder Ausführungssemantik.
Fokussiert 105/105; CPython-Closure 268/2.438 und Modulstartfolger 93/578/534,
jeweils unverändert mit den oben genannten Digests.

Konstante dynamische Importargumente werden zusätzlich aus einfachen
Stringkonstanten in Namenszuweisungen gebunden. Relative Stringwerte und
berechnete Namen bleiben unaufgelöst; die AST-weite Regel bewertet weder Scope
noch Kontrollfluss oder Rebinding. Die synthetische Gegenprobe besteht,
fokussiert 105/105, Archivwerte und Digests unverändert.

Die gleiche begrenzte Regel löst jetzt direkte Konkatenation zweier
Stringkonstanten auf, inline oder in einer Namenszuweisung. Relative Resultate
und sonstige Ausdrücke bleiben offen; synthetisch geprüft, fokussiert 105/105,
Archivwerte und Digests unverändert.

## Fortsetzung: DGN-007 dynamische Sysconfigdatenkante

Der gebundene Quellscanner prüft nun die vollständige AST-Form von
`_get_sysconfigdata_name()` und deren Aufruf in `_init_posix()`: Overridekey,
Fallbacktemplate, `__import__`-Argument und `build_time_vars`-Zugriff sind
fest gebunden. Zusammen mit den separat abgeleiteten CPython-3.12.16-
Buildwerten ergibt sich `_sysconfigdata__linux_x86_64-linux-gnu` als zusätzlicher
externer Namenskandidat für die P11-Auswahl. Der synthetische Quellvertragssatz
besteht 106/106. Archivclosure und Modulstartfolger bleiben unverändert bei
268/2.438 und 93/578/534 mit den bestehenden Digests. Das ist kein tatsächlicher
Importrecord, keine Environment-Absenzprüfung und kein Byte-/Runtimebeleg;
vollständige operative S15-/P11-Inventur und das Fünf-Formen-/64-KiB-Gate
bleiben offen.


## Fortsetzung: gemeinsamer Fünf-Formen-Größenbericht

Der DGN-007-Sizer berichtet jetzt die fünf vollständigen Größen einschließlich Header und deren Gesamtsumme. Einzelgrenzen von je 16.384 Bytes und gemeinsame Obergrenze von 65.536 Bytes stammen aus gemeinsam genutzten Konstanten von Sizer und Codec. Exakt 65.536 Bytes werden akzeptiert, 65.537 Bytes abgewiesen, jeweils ohne Einzelüberschreitung. Die fokussierten Sizer-/Codec-Tests bestehen 79/79 unter Python 3.13.17. Operative S15-/P11-Inventur, Worker-/Channel- und Runtime-Gates bleiben offen.


## Fortsetzung: einzeln gebundene CPython-Quellkandidaten

Der statische DGN-007-Modulstartbericht gibt nun alle 93 Quellkandidaten einzeln als Modulname, relativen CPython-Archivpfad und Quelldatei-SHA-256 aus. Die Ausgabe verlangt sortierte eindeutige Namen und vollständige Quellenauflösung. Am signaturgeprüften CPython-3.12.16-Archiv blieb der Kandidatenscan CANDIDATES_ONLY bei 93 Modulen, 578 Kanten, 534 Funktionen und Digest 84f92a01cb9807b1bf35fe37cd1a231642aabf6134fdee82e7fc35dc0df7c091; alle 93 Ausgaberows sind geordnet, eindeutig und quellgebunden. Der fokussierte Scannertestsatz besteht 108/108 unter Python 3.13.17. Die Itemisierung erleichtert die weitere quellengebundene Reduktion, ist keine P11-Sollinventur oder Runtimebeobachtung. Vollständige S15-/P11-Auswahl und fünf Formen bleiben offen.


## Fortsetzung: Linux-gefilterte CPython-Quellkandidaten

Zusätzlich werden die 58 Kandidaten des engeren Modul-/Klassenkörper-Scans als Modulname, relativer Archivpfad und Quelldateihash ausgegeben. Die fest gebundenen Linux-/CPython-3.12-Prädikate entscheiden fünf Bedingungen, 39 unbekannte bleiben erhalten; 282 Kanten und der bisherige Digest bleiben unverändert. Der Linux-Zweig schließt `ntpath` aus. Der Scope schließt Funktionskörper aus und bleibt `CANDIDATES_ONLY`, kein P11-Soll. Zusammen mit den 93 Modulstartrows unterstützt die Ausgabe die schrittweise Quellenreduktion; vollständige Auswahl und Runtimeinventur bleiben offen.


## Fortsetzung: Frozen-Quellnamen gegen Kandidaten abgeglichen

Der Scanner gibt jetzt die quellgebundenen Bootstrap-/Stdlib-Frozen-Namen samt Aliaszeilen einzeln aus und berichtet die Namensüberschneidung mit beiden Kandidatenscans. Im 58er Linux-Modulkörpervorschnitt liegen elf exakte Quelltabellenüberschneidungen; im 93er Modulstartscan zwölf; die neun Aliaszeilen überschneiden keine Kandidaten. Das belegt nur Quelltabellenbeziehungen, nicht die gebaute Image-Tabelle, Cachemitgliedschaft oder Loader. Builtin-/Extensionauswahl, vollständige S15-/P11-Erwartungsrecords und operative Inventur bleiben offen.


## Fortsetzung: vollständige statische CPython-Builtin-Mitgliedschaft

Der Linux-/CPython-3.12.16-Quellvorschnitt verwendet jetzt alle 31 eindeutigen
Modulnamen aus dem digestgebundenen OCI-Layer-`config.c`/`_PyImport_Inittab`.
Die 27 `PyInit_*`-Zeilen und vier Sonderzeilen (`marshal`, `_warnings`,
`builtins`, `sys`) sind in der Designquelle getrennt erklärt. `nt` ist für
dieses Linux-Ziel als nicht enthalten gebunden; nicht gelistete Namen bleiben
unbekannt. Der Bericht gibt die geordnete Namensliste und `config.c`- sowie
Layer-Digests aus. Der signaturgeprüfte Archivscan bleibt `CANDIDATES_ONLY`:
58 Linux-Modulkörperkandidaten, 282 Kanten, Digest
`478ca51898448040d8da49f3edb6620d96a58b89857e352d88ffd2d7c75395fb`, fünf
aufgelöste und 39 unbekannte Bedingungen. Der fokussierte Scannertestsatz
besteht 108/108. Diese statische Ableitung ist keine Runtime-`sys.builtin_module_names`-
Beobachtung oder P11-Attestation; vollständige S15-/P11-Auswahl, operative
Inventur und das Fünf-Formen-/64-KiB-Gate bleiben offen.

Der betroffene DGN-007-Offline-CI-Workflow lief vollständig im digestgebundenen
CPython-3.12.16-Image: 14 Testmodule, 1.027 Tests ausgeführt, zwei bestehende
Plattform-Skips, alle übrigen bestanden. Der Archivscan unter derselben Runtime
bestätigte die oben genannten Zähler und Digests. Es gab weiterhin keinen
Interpreter-Profilstart, Worker-, SQL- oder Generalprobebetrieb.


## Fortsetzung: importierte Modulnamen in `__main__`-Wachen

Der Zielvorschnitt erkennt `__name__ == "__main__"` und `!=` als importierte
Modulwachen, sofern der Quellbaum keine Bindung, Löschung oder erkannte
dynamische Namespaceoperation enthält. Nach `import *` wird die Annahme
verworfen; andere Vergleiche bleiben unbekannt. Eine Bedingung wird zusätzlich
aufgelöst, weitere Wachen bleiben wegen Star-Imports oder dynamischer
Namespaceoperationen offen.
Der CPython-3.12.16-Archivscan bleibt bei 58 Modulkörperkandidaten, 282 Kanten
und Digest
`478ca51898448040d8da49f3edb6620d96a58b89857e352d88ffd2d7c75395fb`; sechs
Bedingungen sind aufgelöst, 38 unbekannt. Der getrennte Modulstartscan bleibt
93/578/534 mit unverändertem Digest. Der fokussierte Scannertestsatz besteht
109/109. Vollständige S15-/P11-Auswahl, operative Inventur und
Fünf-Formen-/64-KiB-Gate bleiben offen.


## Fortsetzung: Alias `_false = 0` im CPython-Quellbaum

Der Zielvorschnitt wertet einen direkten einmaligen Modulalias `_false = 0`
als false aus, sofern kein früherer Lesezugriff, Rebinding oder erkannter
dynamischer Namespacezugriff dagegen spricht. Ein Star-Import verwirft ältere
Fakten; eine nachfolgende direkte Bindung ist zulässig, ein späterer Star-Import
verwirft sie wieder. Gegenproben bestehen für diese Reihenfolge und die
Unsicherheitsfälle. Im signaturgeprüften CPython-3.12.16-Archivscan sinkt der
Linux-Modulkörpervorschnitt auf 56 Kandidaten und 278 Kanten mit Digest
`9a9abd790787099fbc05b319619f3d849ee04d01997c47c1fa8cddba128367dc`; sieben
Bedingungen sind entschieden und 36 unbekannt. Der getrennte Modulstartscan
bleibt 93/578/534 mit Digest
`84f92a01cb9807b1bf35fe37cd1a231642aabf6134fdee82e7fc35dc0df7c091`. Der
fokussierte Satz besteht 112/112 lokal; vollständige gebundene CI folgt für
diesen Slice. S15-/P11-Auswahl, operative Inventur und Fünf-Formen-/64-KiB-
Gate bleiben offen.

## Fortsetzung: `sys._getframe` im Logging-Modul

Der `logging`-Guard `hasattr(sys, '_getframe')` wird über den gebundenen
CPython-Quellpfad belegt: `sys` ist im Ziel-Inittab enthalten, `logging` bindet
`sys` und `hasattr` nicht neu, und das `sys`-Modulregister enthält den in der
Clinic-Quelle exakt definierten `_getframe`-Eintrag. Die Moduldefinition
verwendet dieses Methodenregister. Die Quellen `Lib/logging/__init__.py`,
`Python/sysmodule.c` und `Python/clinic/sysmodule.c.h` sind digestgebunden.
Damit sinkt der unbekannte Bestand um eine Bedingung. Der gebundene Scan bleibt
`CANDIDATES_ONLY` mit 56 Kandidaten, 278 Kanten und Zeilendigest
`9a9abd790787099fbc05b319619f3d849ee04d01997c47c1fa8cddba128367dc`; 17
Bedingungen sind entschieden, 26 unbekannt. Der Inventardigest lautet
`7948e7655fefd9db9d7c1c595993ed75fb05fb0d932fdf8821a9c61ebd835fdd`. Der
fokussierte Satz besteht 119/119 lokal. Vollständige Offline-CI folgt im
Pull Request. Laufzeit-/P11-Auswahl und operative Inventur bleiben offen.

## Fortsetzung: Importlib-Windows-Selector

Die fünf `_MS_WINDOWS`-Wachen in `_bootstrap_external.py` werden über die
digestgebundene Importlib-Quelle ausgewertet. Voraussetzung sind der direkte,
unveränderte `sys`-Import, genau eine Zuweisung `_MS_WINDOWS =
(sys.platform == 'win32')`, kein Rebinding und eine Zuweisung vor allen
betroffenen Wachen. Für das gebundene Linux-Ziel sind damit fünf weitere
Bedingungen entschieden. Der Scan bleibt `CANDIDATES_ONLY` bei 56 Kandidaten,
278 Kanten und Zeilendigest
`9a9abd790787099fbc05b319619f3d849ee04d01997c47c1fa8cddba128367dc`; 16
Bedingungen sind entschieden, 27 unbekannt. Der Inventardigest der unbekannten
Bedingungen ist `de49880f178dc6716ba2755cd71da449d5185ef5a7daadb3dc8c212d7cd7b898`.
Der fokussierte Satz besteht 118/118 lokal. Vollständige Offline-CI folgt im
Pull Request. Laufzeit-/P11-Auswahl, operative Inventur und das
Fünf-Formen-/64-KiB-Gate bleiben offen.

Der vollständige DGN-007-Offline-CI-Workflow bestand im digestgebundenen
CPython-3.12.16-Image: 14 Testmodule, 1.028 Tests ausgeführt, zwei bestehende
Plattform-Skips, alle übrigen bestanden. Der unabhängige Nachreview schloss
den P2 zu dynamischen Namespaceänderungen ohne offene P1/P2.


## Fortsetzung: Byteordnung des linux/amd64-Ziels

Das statische Zielprädikat bindet `sys.byteorder` für das in §19.4 des
DGN-007-Entwurfs digestgebundene `linux/amd64`-Childmanifest an `little`.
Gleichheits-/Ungleichheitszweige werden gemäß dem bestehenden Prädikatsvertrag
ausgewertet; Identitätsprüfungen bleiben unbekannt. Die synthetische Gegenprobe
prüft `little`, `big`, Identitätsausschluss und die Zweigauswahl. Das bezieht
sich nur auf das konkret festgelegte Zielimage, nicht auf andere Architekturen
oder CPython-Builds. Der signaturgeprüfte CPython-3.12.16-Archivscan bleibt bei
58 Kandidaten, 282 Kanten und Digest
`478ca51898448040d8da49f3edb6620d96a58b89857e352d88ffd2d7c75395fb`; sieben
Bedingungen sind entschieden, 37 unbekannt. Der getrennte Modulstartscan bleibt
93/578/534 mit Digest
`84f92a01cb9807b1bf35fe37cd1a231642aabf6134fdee82e7fc35dc0df7c091`. Der
fokussierte Scannertestsatz besteht 110/110 lokal; die gebundene Offline-CI
folgt im Pull Request. S15-/P11-Auswahl, operative Inventur und
Fünf-Formen-/64-KiB-Gate bleiben offen.


## Fortsetzung: offene Zielwachen vollständig ausgeben

Der Scannerbericht enthält jetzt alle offenen Ziel-If-Bedingungen mit Modul,
relativem Quellpfad, Quellzeile und Ausdruck sowie einem SHA-256 über die
kanonisch sortierten JSON-Records. Der CPython-3.12.16-Linuxvorschnitt enthält
36 solche Records; ihr Digest ist
`424a62f6bcf9bc7a4e676e2c2bd6a667f9c50efb9d4d9ef23ba820e7c6b286bf`. Der
Bestand macht die nächsten statischen Untersuchungen konkreter, ohne aktive
Runtimemodule, vollständige Closure oder P11 zu behaupten. Kandidatenmenge und
Modulstartscan bleiben unverändert; der fokussierte Inventory-Test und die
vollständige DGN-007-Offline-CI laufen im Pull Request. S15-/P11-Auswahl,
operative Inventur und Fünf-Formen-/64-KiB-Gate bleiben offen.


## Fortsetzung: Deskriptortypnamen in `types.py`

Zwei `inspect.py`-Guards werden nun über die exakten gepinnten CPython-3.12.16-
Quellen `Lib/types.py` und `Lib/inspect.py` geprüft. `MemberDescriptorType`
und `GetSetDescriptorType` besitzen je eine direkte Modulzuweisung mit `type()`;
`inspect.py` importiert `types` unverändert und bindet `hasattr` nicht neu.
Nur die beiden exakten `hasattr(types, ...)`-Prädikate werden auf true gesetzt.
Der Linux-Modulkörpervorschnitt bleibt bei 56 Kandidaten, 278 Kanten und Digest
`9a9abd790787099fbc05b319619f3d849ee04d01997c47c1fa8cddba128367dc`; neun
Bedingungen sind entschieden und 34 unbekannt. Der sortierte Unbekannt-
Inventardigest ist jetzt
`f8b00ee5ac8769b34cec1750068fd48294864a9fdc214550a84afed17b57e682`. Die
Modulstartclosure bleibt 93/578/534 mit unverändertem Digest. Der fokussierte
Satz besteht 115/115 lokal; vollständige Offline-CI folgt im Pull Request.
Runtime-/P11-Auswahl, operative Inventur und Fünf-Formen-/64-KiB-Gate bleiben
offen.

## Fortsetzung: AST-Kompatibilitätsattribute aus generierten Typquellen

Die zwei historischen `ast.py`-Guards für `Constant.n` und `Tuple.dims` werden
jetzt gegen die digestgebundenen CPython-Quellen `Parser/Python.asdl`,
`Python/Python-ast.c` und `Lib/ast.py` geprüft. Das ASDL legt die beiden
Konstruktorfelder fest; die generierte C-Quelle bindet die konkreten AST-Typen
mit genau `value`/`kind` beziehungsweise `elts`/`ctx`. Zusammen mit dem
unveränderten `from _ast import *`-Import und den exakten negierten Guards
belegt dies das Fehlen der Legacy-Attribute. Der gebundene Archivscan bleibt
`CANDIDATES_ONLY`: 56 Kandidaten, 278 Kanten und unveränderter Digest
`9a9abd790787099fbc05b319619f3d849ee04d01997c47c1fa8cddba128367dc`; elf
Bedingungen sind entschieden, 32 unbekannt. Der Unbekannt-Inventardigest ist
`9018e5407b5fff1fc6383e7ab808f6b23de04eee1728bb46e07800a28cf952c7`. Der
fokussierte Satz besteht 117/117 lokal. Vollständige Offline-CI folgt im
Pull Request. S15-/P11-Auswahl, operative Inventur und Fünf-Formen-/64-KiB-
Gate bleiben offen.

## Fortsetzung: C-Warnbackend im `warnings`-Modul

Der gebundene CPython-Scan belegt, dass `warnings.py` sein `_warnings`-
Backend aus dem Ziel-Builtin importiert: Die erforderlichen Attribute sind
über das digestgebundene C-Modulmethodenregister und dessen Clinic-Definition
registriert; der Modul-Exec initialisiert `filters`, `_onceregistry` und
`_defaultaction`. Damit wird `_warnings_defaults` im erfolgreichen Importzweig
wahr. Der äußere Fallback-Guard wird falsch und sein innerer
`sys.gettotalrefcount`-Guard wird nicht mehr betreten. Der Scope bleibt
`CANDIDATES_ONLY` bei 56 Kandidaten und 278 Kanten mit unverändertem
Zeilendigest `9a9abd790787099fbc05b319619f3d849ee04d01997c47c1fa8cddba128367dc`;
18 Bedingungen sind entschieden, 24 unbekannt. Der neue Inventardigest lautet
`8ae75b218c78d994f42921d69f4914c4ee8cc5028588e8576cca5f155cf65209`. Der
fokussierte Satz besteht 120/120 lokal. Vollständige Offline-CI folgt im
Pull Request. Runtime-/P11-Auswahl und operative Inventur bleiben offen.

## Fortsetzung: `__main__`-Wachen über feste Star-Exports

Die Importnamen-Analyse erhält `__name__` jetzt nur über digestgebundene
Star-Exports hinweg, wenn der Quellpfad des importierenden Moduls genau einen
direkten Star-Import besitzt und das Exportmodul genau eine statische
`__all__`-Liste ohne `__name__` definiert. Für `dis`/`opcode` und
`tokenize`/`token` erfüllen die CPython-3.12.16-Quellen diese Bedingungen.
Damit werden ihre beiden `__main__`-Wachen falsch. Entsprechende Wachen in
`ast` und `inspect` bleiben wegen weiterer dynamischer Namespacezugriffe
unbekannt. Der Archivscan bleibt `CANDIDATES_ONLY` bei 56 Kandidaten, 278
Kanten und Zeilendigest
`9a9abd790787099fbc05b319619f3d849ee04d01997c47c1fa8cddba128367dc`; 20
Bedingungen sind entschieden, 22 unbekannt. Der neue Unbekannt-Inventardigest
ist `6dea737c0357e5b52ad958d31d8d1a2f86f95bdeb8c7ac0f5197a258329ea033`.
Der fokussierte Satz besteht 121/121 lokal. Vollständige Offline-CI folgt im
Pull Request. Runtime-/P11-Auswahl und operative Inventur bleiben offen.
