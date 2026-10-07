# DGN-007 – Methodenentscheidungspaket

| Merkmal | Wert |
|---|---|
| Stand / Quellenprüfung | 2026-10-07 |
| geprüfte Repositorybasis | `d1c469342c1473c837d070ffef3af0c44deb821c` nach PR75 |
| Status | `PREPARED_FOR_REVIEW` – Entscheidung und Runtime weiterhin offen |
| Geltungsbereich | `PROJECT_SEMANTIC`; technische Entscheidungsvorlage |
| Abnahmegrenze | Quellen-/Codeprüfung, konkrete Kandidaten und unabhängiger Review; keine Methodenwahl, SQL-Runtime oder neue DEC |

## Ergebnis und Entscheidungsgrenze

Die kontrollierte Kollektivzuordnung ist unter getrennten Voraussetzungen
logisch tragfähig. Der vorhandene Ausführungspfad erfüllt diese Voraussetzungen
noch nicht. Die Entscheidungsvorlage benennt für jedes Gate den heutigen
Beleg, einen konkreten Kandidaten und den fehlenden Nachweis. `OPEN` bedeutet
keine positive alternative Runtimefreigabe. Es wird keine allgemeine
Unmöglichkeit einer anderen belegbaren Methode behauptet.

Grundlagen sind der [Mess-/Zuordnungsentwurf](DGN_007_CAPTURE_ASSIGNMENT_DESIGN.md),
der [Beobachtungs-/Herkunftsvertrag](DGN_007_OBSERVATION_PROVENANCE_CONTRACT_DESIGN.md),
der [Suffizienzreview](DGN_007_SATURATION_CONTINUITY_SUFFICIENCY_REVIEW.md) und das
[synthetische Gegenmodell](DGN_007_SATURATION_COUNTERMODEL.md).
Die 51 neuen und 42 bisherigen Modelltests belegen ihre Modellregeln, keine
QS-Einzelidentitäten oder vollständige tatsächliche Herkunft.

Eine spätere normative Auswahl der alternativen Beweisart, Ersatz von G13
oder Verengung der vorgeschlagenen kontinuierlichen Zustands-/Intervallgates
braucht eine ausdrückliche materielle Methodenentscheidung und einen neuen
registrierten DEC-Eintrag. DEC-068 wird dabei nicht umgedeutet. Die hier
vorbereitete Vorlage entscheidet das nicht. Ein kleiner technischer
Offline-Verifier ist innerhalb der bestehenden Entwicklungsautorisierung
zulässig; sein PASS würde die Methodenentscheidung nicht ersetzen.

## Gate-Matrix: Acquisition und Zählschluss

`DOKUMENTIERT` bezeichnet die verlinkte Primärquelle, `CODE` die geprüfte Basis,
`KANDIDAT` einen noch nicht implementierten Vorschlag. Alle Gates bleiben
`OPEN`; Teilbefunde sind keine Gesamtattestation.

| Gate | vorhandener Beleg | konkreter Kandidat / fehlender Nachweis | nächste begrenzte Maßnahme |
|---|---|---|---|
| tatsächliche Calls und geschlossenes Universum | CODE: SQL21 bindet `INSERT #Actual EXEC`, bidirektionalen Ergebnisvergleich und Requestlog; vier Priorcalls und zweimal vier Fenstercalls | KANDIDAT: quellen-/generationsgebundene tatsächliche erfolgreiche Calls, genau ein Zielstatement je Call, vollständiger Zugangsumfang. Geplante zwölf Calls und Payloadflags attestieren das nicht. | vertrauenswürdige Erzeuger und Verbraucher der Call-/Zugangsreceipts festlegen; keine weiteren Suchcalls |
| Countsemantik ohne Doppelzählung | DOKUMENTIERT: aktive Memory-/Diskzeilen gruppieren nach Plan, Intervall, Type; `runtime_stats_id` nur für vergangene Intervalle eindeutig. CODE: SQL21 filtert Type0/zwei Fenster. | KANDIDAT: Raw einmal materialisieren, jede tatsächlich materialisierte Zeile einmal übernehmen, eindeutige Plan→Query-Zuordnung; keine Fanout-Joins oder ID-Deduplikation aktiver Fragmente. NULL/negative Counts sichtbar erhalten und die Acquisition/Bilanz ablehnen; keine positive Summe nach Zeilenfilterung. Positive Types3/4 getrennt erhalten. | konkreten Join-/Materialisierungspfad mit Kardinalitätsbegründung und Gegenfällen prüfen |
| ganze Familie und kohärente Acquisition | DOKUMENTIERT: Variantenbindung versionsabhängig, Dispatcher ohne RuntimeStats. CODE: SQL35 exportiert verwendete Mitglieder plus Parentanker. | KANDIDAT: alle Parentkontexte, Varianten, Pläne, Intervalle und Types, Vor-/Nachfamilie sowie finale Rückbindung. Einmalige Rawaufnahme und gleiche Metadaten beweisen keine atomare gemeinsame Sicht aller Views. Frühere unbekannte Zero-Coverage bleibt unbekannt. | geordneten Acquire-Ablauf mit zulässigen Änderungen zwischen jedem Read konkretisieren; späte Mitglieder und Zwischenänderungen prüfen |
| Basisabschluss und Sättigung | MODELL: 4→8→12 trägt Callerfassung unter unabhängig geschlossenem Universum und injektiver kohärenter Zählung. Reale QS-Counts enthalten keine Oracle-Tokens. | KANDIDAT: vor T0 vollständiges B=4, T0-Post=8 vor T1, T1-Post/Final=12. OFF-Alternative 0→4→8 braucht separat historischen Ausschluss; Setup10 setzt kein OFF. Keine Annahme aus frischer DB oder Nullcount. | jeden Abschluss an tatsächliche Calls, vollständigen Scope und Acquisition binden; Fremdkompensation bleibt ohne Herkunft unentscheidbar |
| kollektive Bucketzuordnung | MODELL: vollständige keyweise Stageledger unterscheiden Sättigung von Ein-Bucket-Zuordnung. CODE: heutiger Capture erst nach beiden Fenstern. | KANDIDAT: tatsächlich abgeschlossener T0-Postledger vor T1; unveränderte alte Gruppen und ausschließlich vier neue reguläre Counts in I0, danach I1, final unveränderte Gesamtbilanz. Keine individuelle Parameter→Plan-Zuordnung. | Stageordnung einschließlich Captureabschluss und Rotation vor Umsetzung festlegen |
| Sichtbarkeitsabschluss | DOKUMENTIERT: Lesen vereinigt Memory/Disk, Flush persistiert Memory; keine hier dokumentierte Familienabschlussquittung. | KANDIDAT: endliche Sättigung nur unter belegten Herkunfts-/Acquisitionprämissen. Flush, Puls, gleiche Polls oder ein vergangenes Intervall allein schließen das Gate nicht. Asynchrone Persistenz ist kein Beleg verzögerter Publikation nach erfolgreichem Call. | jeden Pollausgang als bedingt vollständig, unvollständig, Overflow oder Widerspruch unterscheiden; Wiederholung heilt keine Herkunft |
| kontinuierlicher QS-/Intervallzustand | DOKUMENTIERT: tatsächlicher Zustand kann automatisch abweichen; Intervallkatalog hat ID/Start/Ende, kein Active-/Sealed-/Complete-Feld. MODELL: RO-Lücke kann mit voller Callerfassung vereinbar sein. | strengere vorgeschlagene Kontinuität bleibt erhalten. Punktcaptures, Pulsdelta und Counts erfüllen sie nicht. Keine dokumentierte vollständige automatische Übergangshistorie in den geprüften Views. | stärkeren tatsächlichen Mechanismus belegen oder später ausdrücklich den engeren retrospektiven Claim entscheiden; keine stille Verengung |
| Zeitbeziehungen und Extrema | DOKUMENTIERT: First/Last sind Ausführungs-Endzeiten. CODE: G13 verletzt in begrenzten historischen Läufen die untere SYSUTC-Klammer. | QS↔SYSUTC, QS↔Katalog und SYSUTC↔Katalog getrennt offen. Positive Extrema, All-/Zero-Extrema und deren Stabilität separat behandeln; Zero-Zeitsemantik hier nicht dokumentiert. | keine Rundung, Zeitpuffer oder Ursachenbehauptung; konkrete zeitliche Vertragsänderung erst separat entscheiden |

Codeanker: [SQL21](../../Demos/07_Query_Store_Extended_Events/DGN-007_Time_Bounded_Search_Incident/Automated/21_Controlled_Query_Store_Windows.sql)
und [SQL35](../../Demos/07_Query_Store_Extended_Events/DGN-007_Time_Bounded_Search_Incident/Automated/35_Control_Evidence.sql).
Die dokumentierten Grenzen stammen aus [RuntimeStats](https://learn.microsoft.com/en-us/sql/relational-databases/system-catalog-views/sys-query-store-runtime-stats-transact-sql?view=sql-server-ver17),
[QS-Erfassung](https://learn.microsoft.com/en-us/sql/relational-databases/performance/how-query-store-collects-data?view=sql-server-ver17),
[Varianten](https://learn.microsoft.com/en-us/sql/relational-databases/system-catalog-views/sys-query-store-query-variant?view=sql-server-ver17),
[Intervallkatalog](https://learn.microsoft.com/en-us/sql/relational-databases/system-catalog-views/sys-query-store-runtime-stats-interval-transact-sql?view=sql-server-ver17),
[Flush](https://learn.microsoft.com/en-us/sql/relational-databases/system-stored-procedures/sp-query-store-flush-db-transact-sql?view=sql-server-ver17)
und [QS-Optionen](https://learn.microsoft.com/en-us/sql/relational-databases/system-catalog-views/sys-database-query-store-options-transact-sql?view=sql-server-ver17).

## Konkreter Floatregel-Kandidat

Duration, CPU, Reads und Rows bleiben vier getrennte Metriken. KANDIDAT:
einmal übernommene begrenzte Rawmittelwerte mit Style3 serialisieren, als
endliche Decimaltexte lesen und Countgewichtung exakt über Fraction ausführen.
Frühere Gruppen müssen Counts, alle vier gewichteten Signaturen und positive
Extrema exakt erhalten. Abweichung erhält keinen positiven Stabilitätsbeleg;
es gibt kein nachträgliches Epsilon. Die bestehende v1-Rows-Toleranz wird nicht
auf dieses Gate übertragen.

Diese Regel wäre konservativ, aber **nicht fragmentierungsinvariant** und
hier nicht freigegeben. Style3 stellt einzelne Floatwerte eindeutig dar;
Floataggregation bleibt näherungsweise. Exakte Decimaltextrechnung stellt
weder verlorene Enginepräzision noch den ursprünglichen Binärwert wieder her.
CODE: SQL21 aggregiert bereits FLOAT; SQL35 vergleicht live Counts und
All-Extrema, keine vollständige Stabilität der vier Metriken.
[CAST/CONVERT](https://learn.microsoft.com/en-us/sql/t-sql/functions/cast-and-convert-transact-sql?view=sql-server-ver17),
[FLOAT](https://learn.microsoft.com/en-us/sql/t-sql/data-types/float-and-real-transact-sql?view=sql-server-ver17),
[SUM](https://learn.microsoft.com/en-us/sql/t-sql/functions/sum-transact-sql?view=sql-server-ver17).

Synthetischer Gegenfall, keine beobachtete SQL-Ursache: dieselben vier Werte
`1,2,2,2` ergeben `1.75`. Ein Fragment `count4/avgText=1.75` und die Partition
`count3/avgText=1.6666666666666667` plus `count1/avgText=2` ergeben nach exakter
Textgewichtung `1.750000000000000025`. Eine unveränderte Population kann damit
abgelehnt werden. Ein späterer begrenzter numerischer Vorschnitt kann Oracle,
gerundetes Fragmentmittel, Style3-Text und Consumergewichtung getrennt prüfen;
er entscheidet keine universelle Toleranz. Acquisitionkohärenz wird durch
exakte Signaturgleichheit ebenfalls nicht bewiesen.

## Gate-Matrix: ausführbarer Herkunftspfad

| Gate | vorhandener Beleg | konkreter Kandidat / fehlender Nachweis | nächste begrenzte Maßnahme |
|---|---|---|---|
| Quellen und Importclosure | CODE: statischer 14-SQL-/Manifesthashvertrag; Runner/Harness/Proxy lesen Live-Dateien und Imports. Getrennter [Offline-Verifier](DGN_007_SOURCE_BUNDLE_VERIFIER.md) bindet 27 Kandidatenmitglieder und deklarierte Imports; [Kantenprofil](DGN_007_EXECUTION_EDGE_VERIFIER.md) statisch implementiert. | exakter Commit und Gitblob-/Bytebindung aller tatsächlich verwendeten Mitglieder, festgelegter Einstieg und tatsächliche Importauflösung; Interpreter, Stdlib und Tools ausdrücklich vertrauenswürdig benennen. Statischer Kandidatenbundle ist noch kein ausgeführter Freeze. | Import-/Launcherentwurf PROPOSED; tatsächliche Import-/Quellen-/Toolauflösung bleibt offen |
| Launcher und Actor | CODE: eigener serieller Harness und echte Phasenfolge. | benannter vertrauenswürdiger Launcher kontrolliert die tatsächlichen Ausführungsbytes, Actoridentität und Receipts. Eigenes Signieren/Flags aus dem Payload sind keine unabhängige Attestation. Schutz während Ausführung noch offen. | Erzeuger-/Prüfergrenze und tatsächliche private Berechtigungen vor Launcherimplementierung festlegen |
| Ziel und Generation | CODE: SQL/Readiness verwenden Namen; CI prüft vollständige CID beim Abbau. | festgelegter Daemonkontext und vollständige CID durch jede SQL-/Readiness-/Recovery-/Cleanupaktion; serverseitig bestätigte neue DBgeneration und Lifecyclebindung. Namen/Labels nur Zusatzbindung. | jede Aktion auf eindeutige Zielbindung entwerfen; Alias-, Austausch- und Replay-Gegenproben |
| Zugangsumfang | CODE: keine veröffentlichten Ports/Mounts, eigene Sessionfolge. | tatsächlich beschränkter Zugang; Host-/Daemonadministratoren und dieselbe OS-Identität gehören zur benannten Vertrauensgrenze. `--network none` begrenzt Netz, verhindert keine Daemonzugriffe. | überprüfbare Verwaltungs-/Credential-/Actorgrenze festlegen; kooperatives Lock nur für eigene Teilnehmer beanspruchen |
| Host und Ressourcen | CODE: 4 CPU/8 GiB als Containerlimits, parallele Versionsmatrix mit optionalem Runner. | vorhandener Vertrag: auf gemeinsamem lokalem Host eine aktive Version; getrennte GitHub-Hosts dürfen parallel. Vorgeschlagene physische Hostexklusivität ist strenger und aktuell nicht belegt. Limits garantieren keine Zuteilung oder Störlastfreiheit. | Isolationseinheit ausdrücklich entscheiden und Ressourcen tatsächlich prüfen; VM-/Daemondomain nicht als physischer Host ausgeben |
| Cleanup und Unterbrechung | CODE: erster unabhängiger DB-Abwesenheitsfehler bleibt sticky; finale own-CID-Abwesenheit separat. | gleicher Actor/Daemon/CID-/Generationspfad bis zur ersten Abwesenheit und eigener Entfernung. Harte Host-/Daemonunterbrechung kann Cleanup unbekannt lassen. Recovery heilt ersten Fehler nicht. | begrenzte Fehlertests und unabhängige Cleanupprüfung im später autorisierten Runtimepfad |

[GitHub-Runner](https://docs.github.com/en/actions/reference/runners/github-hosted-runners)
dokumentiert eigene VMs für Standardjobs, keine hier belegte physische
Hostexklusivität. Der optionale Runner kann eine gemeinsam verwendete
Selfhost-Domain adressieren. Beibehalten der strengeren physischen Forderung
bedeutet aktuell `OPEN / NO-GO` für diese Alternative; Auswahl einer
kontrollierten VM-/Daemondomain wäre ein ausdrücklicher Methodengrenzentscheid.
[Docker-Sicherheit](https://docs.docker.com/engine/security/),
[Netzwerk none](https://docs.docker.com/engine/network/drivers/none/).

## Kostenplan und End-to-End-Grenzen

Die bestehenden Budgets bleiben SQL21 145 Sekunden, regulärer Lifecycle
180 Sekunden, Cleanup separat 60 Sekunden; vier CPU/8 GiB bleiben erhalten.
Die PR73-Bounds sind gleichzeitig geltende Höchstgrenzen, kein zugesagter
Leistungsnachweis oder Budgetreservierung:

| Kosten-/Größengate | konkreter Plan | heutige Lücke |
|---|---|---|
| Acquisitionfolge | acht Stages, höchstens zwei Aufnahmen je Stage, jede höchstens 2 s; alle Versuche erhalten, Pflichtfehler sticky | 16×2=32 s sind bereits mehr als der separate 20-s-Observercap, falls sämtliche Reads aktive Observerzeit wären. Globale Caps dominieren einzelne Maxima; kein Ausschöpfen aller Grenzen. |
| Rotation und Polls | höchstens 64 zusätzliche Puls-/Rotationspolls insgesamt, Sleep höchstens 1 s je Poll; nur ein zusätzlicher Acquireversuch bei ausdrücklich unvollständiger Sicht | 64 s Wartezeit plus Reads, zwei Rotationen, acht Fenstercalls und vier Priorcalls sind nicht vermessen. Gleiche Polls schließen keine Prämisse. |
| aktive Beobachtung | tatsächliche aktive Observer-/Pulszeit kumulativ höchstens 20 s; Pollsleep zusätzlich im SQL21-/Lifecyclebudget | Erzeuger, monotone Messung und tatsächliche Obergrenze fehlen. Observer verändert den beobachteten Ablauf. |
| skalare Payloads | je Acquire höchstens 16.384 Bytes; insgesamt 131.072 Bytes einschließlich aller Versuche, Pulse, Metadata und Coverage | 16×16 KiB=256 KiB verletzt den globalen 128-KiB-Cap. 256 Fragmente×vier Texte×64 Zeichen=64 KiB schon ohne Keys. Zeilen- und Bytecaps unabhängig prüfen, Overflow vor Speicherung ablehnen. |
| ganze Prozesskette | Grenzen von SQL-Ausgabe über SQLcmd, Proxy, Harness, Frames bis Parser, monotone nicht rücksetzbare Gesamtdeadline einschließlich Drain/Parsing; Cleanup separat | heutiger Proxy `capture_output` und Harnesshelper `communicate` puffern vor dem äußeren Collector. Dessen 256-KiB-normalisierte-UTF8-Grenze ist keine Rohpipe-/Gesamtgrenze. |
| Record-/Privacygrenze | feste skalare Formate, vollständige Bindungen, begrenzte UTF8-/CRLF-Zustände; keine Querytexte, XML, Rohfehler oder Secrets im Repository | existierendes v1-Framing unverändert; neue Version braucht gemeinsam geprüften Producer-/Transport-/Record-/Evaluatorvertrag, keine größeren Frames als Ersatz für Streaming. |

Ein künftiger Kostenbeleg muss die tatsächlich maximal erlaubte Kombination
aus Acquisition, Pollsleep, Beobachtung, Calls, Serialisierung und Drain gegen
145/180 Sekunden prüfen. Kein Deadline-Neustart je Versuch; Cleanup erhält
60 Sekunden und eigene Fehlerdominanz. Jobtimeout und nominelle Schleifen
sind keine Machbarkeitsevidenz. No-GO bei fehlendem oder widersprüchlichem
Pflichtbeleg; die spätere Zuordnung nutzt nur bestehende
[FWK-012-Codes](../../Demos/00_Framework/Contracts/FWK-012_Status_Error_Skip_Contract.md).
Passende Plattform-/Konfigurations-Preflights dürfen ihre vorhandenen SKIPs
verwenden. `SKIP_EVIDENCE_MISSING` aus DEC-068 bleibt auf vollständige gültige
Vergleichsevidenz ohne Separation begrenzt und heilt keine Methodenprämisse.

## Implementierter statischer Schnitt und Folgearbeit ohne SQL

Der [Offline-Quellenbundle-Verifier](DGN_007_SOURCE_BUNDLE_VERIFIER.md) ist
als getrennter statischer Schnitt implementiert. Er
startet keinen Collector, Launcher, Interpreter des Bundles, SQL oder Docker.
Er prüft nur eine technische statische Quellenvoraussetzung.
Die getrennte [Prozess-/Manifestkantenprüfung](DGN_007_EXECUTION_EDGE_VERIFIER.md)
ist ebenfalls statisch implementiert; Import-/Launcherentwurf PROPOSED und
tatsächliche Importumgebung offen. Die folgenden Quellenvoraussetzungen bleiben
ausdrücklich auf statische Kandidaten beschränkt:

1. Expliziten Commit, feste reviewte Mitgliederliste und Einstieg gegen
   tatsächliche Gitblobs und Kandidatenbytes prüfen; relative Pfade, Dateitypen,
   Einzel-/Gesamtgrößen und deterministische Imports festlegen. Normale lokale
   EOL-Normalisierung und tatsächlich zu startende Bundlebytes getrennt
   behandeln; ausführbare Bytes nicht durch LF-Digestgleichheit attestieren.
2. Fehlende/zusätzliche/doppelte Mitglieder, Traversal, absolute Pfade,
   Casekollisionen, externe Symlinks/Reparsepoints und Substitution geschlossen
   ablehnen. Feste AST-Importclosure und Stdlib-/Toolgrenze prüfen;
   unaufgelöste dynamische Imports bleiben offen und ergeben kein geschlossenes
   Bundle. Importauflösung darf nicht aus fremden Live-Pfaden ergänzt werden.
3. Temporäre Manipulationsfixtures für Executorbyteänderung bei unverändertem
   SQLmanifest, fremden Importpfad, fehlendes/zusätzliches/dupliziertes Mitglied,
   EOL gegen echte Inhaltsänderung, Exportattribute und Größenoverflow ausführen.
   `git archive` allein attestiert keine exakte Closure: `export-ignore` und
   `export-subst` können Mitglieder/Bytes verändern.
   [Git archive](https://git-scm.com/docs/git-archive).
4. Ergebnis ausdrücklich statisch begrenzen: Kandidatenbyte-/Pfadprüfung,
   `runtime_attested=false`; kein UsedBundle-, Actor-, CID-, DBgenerations-,
   Zugangs-, Host-, Acquisition- oder Budgetbeleg. Alias/Replay und tatsächliche
   Ausführung bleiben Folgefixtures des späteren Ziel-/Launcherpfads.

Der getrennte [synthetische Streaming-/Budgetprototyp](DGN_007_STREAMING_BUDGET_PROTOTYPE.md) ist implementiert, ohne Integration
in die neun Runtimequellen. Er attestiert keine reale Machbarkeit der
vollständigen 145/180/60-Kette. Nächster kleiner Schnitt: getrennte numerische Gegenprobe von endlicher Oraclepopulation
über ausdrücklich deklarierte Fragmentrundung und separat vorgegebenen synthetischen
Style3-Text bis zur bestehenden Consumergewichtung. Keine SQL-Konversionsemulation,
Epsilon- oder Methodenfreigabe. Die noch offenen Gates sind weiterhin gegen
tatsächliche Evidenz zu prüfen. Keine endlose Modell-/Pollingwiederholung bis PASS. Die spätere
gemeinsam versionierte Umsetzung verbindet SQL21/35, Freeze, Transport,
Records, Evaluator und Coordinator erst nach tragfähiger expliziter Entscheidung.

Der [v1-Vertrag](../../Demos/07_Query_Store_Extended_Events/DGN-007_Time_Bounded_Search_Incident/Contracts/README.md),
G13, DEC-068 und historische FAILs bleiben erhalten. PR68 erhält keine
Mergefreigabe; der lokale interne API-Schnitt bleibt zurückgestellt. Keine
OFF-/CLEAR-/Warmup-/Laständerung oder neue Runtime. Incident-, Ursachen-,
Mitigations-, Capstone-, Teilnehmer- und Szenariofreigabe bleiben offen.
