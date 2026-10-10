# Aktueller Ausführungsstand

| Merkmal | Wert |
|---|---|
| Status | allgemeine Entwicklung `PAUSED`; DGN-007-Reporter trotz grüner Diagnosematrix weiterhin `BLOCKED` durch ungeklärte historische SQL20-/G13-Fehler |
| Stand | 2026-10-10 |
| aktueller Integrationsnachweis | Foundation `1.21.0` und die vertragsbezogene CI-Testauswahl sind durch [PR 126](https://github.com/gecompat/SQL_PerformanceSchulung/pull/126) integriert. Die eigenständige Fehlerrohdiagnose aus [PR 130](https://github.com/gecompat/SQL_PerformanceSchulung/pull/130) ist auf `aea230fb65798afddd4643c92b84f09403819ec6` in `origin/main`; die [aktuelle PR-Matrix](https://github.com/gecompat/SQL_PerformanceSchulung/actions/runs/38048742623) bestand auf 2019/2022/2025, reproduzierte die Fehler aber nicht und erteilt keine Reporterfreigabe. |
| früherer fachlicher Basisstand | `2f04deb2fed0faf5bedf70101fea3f4b93d46678` nach PR 123; Ledgerkomponente §32.5 und Loaderrecordformen §33 bleiben im bisherigen Nachweisstand; SESSION_END und operativer Bootstrap-/Kanalvertrag bleiben pausiert/offen; SQL-Codebasis `da7b0eb…` aus Pull Request 65 unverändert |
| geprüfter Runtime-Stand | `782799e` aus Pull Request 42; `OPT-017`-Matrix vollständig grün |
| Fachliche Hauptwelle | `ADV-008` und `W-COV-001` vollständig runtimevalidiert |
| Abgeschlossene Folgepakete | `W2-002`, `ADV-009`, `ADV-010`, `LABSCN-002`, `LABSCN-004`, `INF-002`, `INF-003`, `LABINT-003` und der `CON-006`-bezogene `LABINT-004`-Schnitt `VALIDATED` |
| Szenariowelle | `CON-004`, `DGN-005` und `CON-006` – Project Adapter `0.1` und vollständiger Docker-/Podman-Lifecycle auf SQL Server 2025 validiert |
| Folgeplanung | [NEXT_DEVELOPMENT_WAVES.md](NEXT_DEVELOPMENT_WAVES.md) |
| Zweck | kanonischer operativer Einstiegspunkt für Nachweisstand, offene Gates und nächste Schnitte |

## 0. Entwicklungspause und Wiederaufnahme

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
die Prozesskorrektur gemäß `DEC-070`. Die frühere Scopeanfrage ist damit erledigt;
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
   `DEC-068` bleiben gültig; keine Toleranz- oder Metrikkorrektur ohne Entscheidung.

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
Abschnitt gegen [NEXT_DEVELOPMENT_WAVES.md](NEXT_DEVELOPMENT_WAVES.md),
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
| `OPT-015` | Plan- und Statistikevidenz, zwei vollständige Läufe auf SQL Server 2019, 2022 und 2025 | `VALIDATED` |
| `OPT-016` | Outer References, Rebinds, Rewinds und Performance Spool, zwei vollständige Läufe auf 2019, 2022 und 2025 | `VALIDATED` |
| `QRY-013` | [Actions-Lauf 30699410795](https://github.com/gecompat/SQL_PerformanceSchulung/actions/runs/30699410795): zwei Docker-basierte Läufe auf 2019, 2022 und 2025 | `VALIDATED` |
| `OPT-009` | [Actions-Lauf 30701731564](https://github.com/gecompat/SQL_PerformanceSchulung/actions/runs/30701731564): 2022/2025 erfolgreich, 2019 erwartungsgemäß `SKIP_VERSION` | `VALIDATED` |
| `OPT-010` | [Actions-Lauf 30702590969](https://github.com/gecompat/SQL_PerformanceSchulung/actions/runs/30702590969): 2025 erfolgreich, 2019/2022 erwartungsgemäß `SKIP_VERSION` | `VALIDATED` |
| `OPT-013` | Gate-B-Nachweis | `VALIDATED` |
| `QRY-001` | Framework- und Lab-Nachweis | `VALIDATED` |
| `OPT-002` | Framework- und Lab-Nachweis | `VALIDATED` |
| `CON-004` | fachliche Demo und Szenariokandidat | `VALIDATED` |
| `QRY-004` | [Actions-Lauf 33222989681](https://github.com/gecompat/SQL_PerformanceSchulung/actions/runs/33222989681): je zwei vollständige Läufe auf 2019/2022/2025; erwartete `WARN_EMPIRICAL_VARIANCE` ohne Vertrags- oder Cleanup-Fehler | `VALIDATED` |
| `DGN-003`, `DGN-005` | [Actions-Lauf 33222989682](https://github.com/gecompat/SQL_PerformanceSchulung/actions/runs/33222989682): je zwei `PASS/OK` auf 2019/2022/2025 | `VALIDATED` |
| `OPT-017` | [Actions-Lauf 33447840232](https://github.com/gecompat/SQL_PerformanceSchulung/actions/runs/33447840232): je zwei `PASS/OK` auf 2019/2022/2025 mit Actual DOP, Exchange, positiver Threadarbeit, serieller Gegenprobe und Cleanup | `VALIDATED` |
| `OPT-003`, `OPT-005` | Statistik-Sampling/Skew sowie Ascending-Key-/Pflegevertrag; je zwei lokale Docker-Läufe auf 2019/2022/2025 mit `PASS` | `VALIDATED` |
| `CON-006` | Deadlock-Zyklus, Fehler 1205, Graph und geordnete Gegenprobe; je zwei `PASS` auf 2019/2022/2025 | `VALIDATED` |
| `CON-009` | [Actions-Lauf 33222989644](https://github.com/gecompat/SQL_PerformanceSchulung/actions/runs/33222989644): TempDB-Kostenklassen auf 2019/2022/2025 jeweils zweimal `PASS/OK` | `VALIDATED` |
| `IDX-006`, `IDX-010` | Rowstore-Messkette je zweimal mit fachlich akzeptierter Warnung; klassische Columnstore-Segmente je zweimal `PASS` auf allen Zielversionen | `VALIDATED` |
| `STL-008`, `STL-009` | rote VLF-/Growth-Lane und gelber Commit-/WRITELOG-Schnitt; je zwei `PASS` auf 2019/2022/2025 | `VALIDATED` |
| `RES-007` | Task-, Request- und Instanz-Waitscope mit Gegenprobe; je zwei `PASS` auf 2019/2022/2025 | `VALIDATED` |
| `QRY-006` | Lokaler Docker-Nachweis: SQL Server 2019/150, 2022/160 und 2025/170, je zwei vollständige Manifestläufe `PASS`; siehe [QRY_006_RUNTIME_EVIDENCE.md](QRY_006_RUNTIME_EVIDENCE.md) | `IMPLEMENTED` – Runtime-Gate und SQL_Server_Lab-Szenariopromotion bleiben offen |
| `DGN-007_DATA_MODEL` | Lokaler Docker-Nachweis vom 2026-10-06: 2019/150, 2022/160 und 2025/170 je zwei vollständige Datenmodell-Lifecycles `PASS/OK`, unabhängiger Datenbankabbau nach jedem Lauf und Entfernung aller eigenen Container; siehe [DGN_007_DATA_MODEL_RUNTIME_EVIDENCE.md](DGN_007_DATA_MODEL_RUNTIME_EVIDENCE.md) | `IMPLEMENTED` – begrenzter Datenmodellvertrag; vollständige Capstone-Abnahme und Szenariopromotion bleiben offen |
| `DGN-007_QUERY_STORE_WINDOWS` | Lokaler Docker-Nachweis vom 2026-10-06: 2019/150, 2022/160 und 2025/170 je zwei vollständige Fenster-Lifecycles `PASS/OK`; disjunkte Katalogintervalle, gleiche vier Parameterklassen und je vier erfasste Suchausführungen, unabhängiger Datenbankabbau und Entfernung aller eigenen Container; siehe [DGN_007_QUERY_STORE_WINDOWS_RUNTIME_EVIDENCE.md](DGN_007_QUERY_STORE_WINDOWS_RUNTIME_EVIDENCE.md) | `IMPLEMENTED` – begrenzte Capture-Evidenz; kein Incident-, Regressions- oder Capstone-Nachweis |

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

`ADV-006` und `ADV-007` bleiben als `DESIGNED`-Verträge vollständig: Die zugehörigen LAB-VP3-/VP4-Grenzen, Feature-Skips und Diagnoseabhängigkeiten sind dokumentiert, ihre fachliche Umsetzung erfolgt erst in den jeweiligen Folgewellen.

## 5. Nächste fachliche Verarbeitung

Die verbindliche Reihenfolge und die Akzeptanzkriterien stehen in [NEXT_DEVELOPMENT_WAVES.md](NEXT_DEVELOPMENT_WAVES.md). Kurzfristig ist die Reihenfolge:

1. `DGN-007` Capstone-Planungsschnitt ist mit `TSK-002` entschieden
   (`DECIDED_PLANNING`, Stand 2026-09-14); der Detailreviewvertrag steht in
   [LABSCN_005_DGN_007_DETAIL_REVIEW.md](LABSCN_005_DGN_007_DETAIL_REVIEW.md).
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
- Der SQL-Server-2025-Delta-Review ist in `SQL_SERVER_2025_DELTA_REVIEW.md` abgeschlossen: CE Feedback für Ausdrücke und zeitgebundene XE-Sessions sind in bestehende Verträge übernommen; vier Infrastruktur-/Abhängigkeitsthemen bleiben zurückgestellt, Vector/KI außerhalb des Curriculums.
- Aktuelle Herstellerdokumentation allein ist weiterhin kein Implementierungs- oder Runtime-Nachweis.
