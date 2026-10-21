# DGN-007 – reine SESSION_END-Komponenten

Stand: 2026-10-20. Basis `131e19651c57a829080093cbe2b6767a0ab462d8` nach
PR256. Status: `A_B_IMPLEMENTED_REVIEWED`. Maßgeblich bleibt
[§34 des Profilbindungsentwurfs](DGN_007_IMPORT_PROFILE_BINDING_DESIGN.md#34-session_end-counts-und-kanalhashpräbild).

## Abgegrenzte Wellen und Auswahl vor Implementierung

Ein Implementierungsowner bearbeitet zuerst den Footer-Codec und nach dessen
lokalen Tests, unabhängigem Review, aktueller CI (Continuous Integration; automatisierte Integrationsprüfungen), Main-Integration und eigener
Branchbereinigung die Kanalhashfunktion. Höchstens zwei Quellenkandidaten je
Schnitt, Checkpoint nach jedem ersten Kandidaten, insgesamt vier; ein gemeinsamer
unabhängiger Auswahl-PRE und ein Implementierungsreview je Schnitt. Nur ein
gezielter Befundnachlauf bei geändertem Input. Modellverbrauch ist unbekannt.
Alte ausgeschöpfte Import-/Quell-/Generatorwellen werden nicht wieder aufgenommen.

Gewählte eigene Quelle: `Tests/Tools/dgn007_session_end.py`, außerhalb der neun
Runtimequellen und des unveränderten 27-Member-Bundles. Keine Änderung an
Bootstrapquellengenerator, Loader, Ledger, Manifests, SQL oder Runtimeprofil.
Gewählter eigener Harness: `Tests/Static/test_dgn007_session_end.py`, ausschließlich
stdlib/unittest mit synthetischen Literalen; nur Import der eigenen Hilfsquelle,
keine Imports der neun Runtimekandidaten, Aufnahme,
Worker, Prozesse, Dateien, SQL oder Provideraktionen im Prüfpfad. Lokale Prüfung
unter Python 3.12 und der verfügbaren portablen Pythonversion, anschließend CI.

Schnitt A stellt `decode_footer(line)` und `encode_footer(values)` bereit.
`line` ist exakt bytes, 1–256 Bytes mit genau einem LF; `values` ist ein exaktes
Tupel aus den zwölf unverändert vorgegebenen Feldern. Der Decoder begrenzt vor
dem JSONparser, prüft alle primitiven Typen, Form, Rollen-/Fragment-/Countsemantik,
die notwendigen Bytegrenzen und kanonischen ASCII-Repack. Er erhält die
ursprünglichen Bytes und vollständig geprüften Felder unveränderlich, ohne
Rohwerte in repr oder Fehlerketten. Der Encoder ergänzt keine Counts oder Hashes.

Die Rückgabe heißt ausschließlich `DecodedFooter`: `PROJECT_SEMANTIC`,
`full_trace_verified=False`, `context_verified=False`, `channel_verified=False`,
`runtime_attested=False` und `trust_attested=False`. Es wird weder
`MATCHED_DECLARED_SESSION_END` geliefert noch ein Ledgerübergang freigegeben.
Gleiche Footerfelder können weiterhin zu einem falschen oder fehlenden Trace
gehören. Das ist ein wiederverwendbarer Grammatik-/Countvorschnitt, kein
vollständiger §34-Matcher. Die vollständigen K8-/D9-, Profil- und §33-Paarprüfungen
sowie Provider-/Encoderbindung bleiben Pflicht des späteren vollständigen Pfads.

Schnitt B ergänzt `channel_digest(ordinal, context_digest, stdout_prefix, stderr)`.
Er begrenzt exakte Integer-/Text-/Bytetypen vor weiterer Verarbeitung und bildet
ausschließlich das binäre Präbild aus §34.2 aus übergebenen Bytes. Er liest keine
Pipes, sucht keinen Footer, attestiert keine EOFs und validiert keine K8-Herkunft.
Die Rückgabe ist ausschließlich ein Lowerhex-SHA, kein Match oder Receipt.
Alle bisherigen Caps bleiben bestehen; der Caller muss die drei Workers und
Footerbytes zusätzlich gemeinsam buchen. Keine Hash-/Encoder-/Runtimeattestation
folgt aus dem Vorliegen eines Digestwerts.

## Gegenproben und tatsächlicher Prüfaufwand

Für A: unabhängige Literalbildung aller drei Rollen/f1–19, 178-Byte-Breite,
sämtliche Feldtypen und Rollen-/Paar-/Recordcounts, Lowerhex, Grenzen,
Bool/Subclass/Foreign-Objekte vor Dispatch, fehlende/zusätzliche Felder,
Unicode/Escapes/Space/CRLF/zweites LF, überlange oder verschachtelte Eingaben,
kanonischer Repack, ursprüngliche Bytes und feste Fehler ohne private Ketten.
Gleiche deklarierte Counts dürfen nicht als Trace-/Kanalprüfung erscheinen.

Für B: unabhängige 71-Byte-Referenz, alle Ordinals, Kontext- und Kanaltausch,
LF/CRLF, Nullbytes, nicht als UTF-8 interpretierbare Bytes, leere Kanäle,
gemeinsame Grenze und Overflow, exakte Typen vor Dispatch und klar fehlende
EOF-/Trace-/Providerattestation. Keine erfundene Gesamtordnung beider Pipes.

Eine eigene kleine statische CI `dgn007-session-end.yml` erhält ausschließlich
die neuen Quell-/Test-/Dokument-/Workflowpfade. Sie führt genau diese Suite aus;
bestehende Offline-Bundle-Suites und SQL-Matrizen werden nicht erweitert oder
unterdrückt. Der zentrale Privacy-Scan und Registry-/Governance-Gates bleiben
unverändert. Dies vermeidet eine neue Abhängigkeit und zusätzliche unveränderte
Qualifikationssuiten; aktuelle PR-/Main-Gates bleiben notwendig. Es werden keine
Workflows, Scheduler, Trust- oder Providerkonfigurationen für Runtime aktiviert.

## Auswahl-PRE und erster Quellencheckpoint

Der unabhängige Auswahl-PRE bestätigt den Planstand mit SHA256
`a8af9c818687dd132ed528722697576103a73004454dcebc1911dc1d223c6287`
ohne Befunde. API (Application Programming Interface; Programmierschnittstelle), eigene Quelle und Harness sind für beide getrennten Schnitte
freigegeben. Die Pflichtprüfungen des vollständigen Matchers bleiben außerhalb
dieser reinen Komponenten bestehen; die Standardbibliothek ist ausschließlich
eine Kontrollannahme.

Schnitt A, erster Quellenkandidat: 13 Testmethoden bestehen lokal isoliert unter
Windows/Python 3.14.7 und Linux/Python 3.12.3 ohne SKIP. Enthalten sind alle 57
Rollen-/Fragmentkombinationen, tatsächliche Footerbreite im gemeinsamen
Einzelworkerlimit, Typen vor fremdem Dispatch und Fehler ohne private Ketten.
Checkpoint: Kandidat 1 von höchstens 2, keine Quellenkorrektur erforderlich.
Der unabhängige Implementierungsreview zu Base `131e196…` und Head
`aa71d354583cef894199823373f778d22b27bf38` schließt ohne offene P1/P2/P3-Befunde.
Alle acht CI-Gates dieses Stands bestehen, einschließlich der eigenen
[Komponentensuite](https://github.com/gecompat/SQL_PerformanceSchulung/actions/runs/39402165136).
Die Abschlussrevision führt ausschließlich Evidenz nach; Quelle und Suite
bleiben gegenüber dem reviewten Stand unverändert. [PR257](https://github.com/gecompat/SQL_PerformanceSchulung/pull/257)
bindet finale Head-/Base-Gates, Main-Integration und eigene Branchbereinigung;
diese bleiben vor Abschluss notwendig.
PR257 ist mit acht verschiedenen grünen finalen PR-Gates in
`5466a445574f283b1a3b43c55449cc79fb551234` integriert. Vollständiger Treevergleich
zum finalen Head `cf8ba1de695a2d709d1b5a68ae357b55456e540b` ohne Unterschied;
lokales Main synchron/sauber und beide eigenen Arbeitsbranches gelöscht.
Alle sechs Main-Workflows erfolgreich, einschließlich der
[Komponentensuite](https://github.com/gecompat/SQL_PerformanceSchulung/actions/runs/39402587807).

## Kanalhash: erster Quellencheckpoint

Schnitt B beginnt erst auf diesem integrierten Mainstand. `channel_digest`
hasht das feste Domain-/Ordinal-/Kontext-/Längenpräbild inkrementell mit den
übergebenen Rohbytes. Alle vier exakten primitiven Typen gehen Bounds und
Hashprovideraufruf voraus; die gemeinsame übergebene Rohbytezahl ist auf
65536 begrenzt. Footerbytes und drei Workers muss der Caller zusätzlich buchen.
Das Ergebnis ist nur ein exakter 64-stelliger Lowerhex-String. Eigene feste
`ChannelRejected`-Fehler behalten keine privaten Ursachen oder Kontexte.
Die gemeinsame Fehlerhülle des Footer-Codecs erhält dafür einen internen
Ausnahmetypparameter; dessen öffentliche APIs und Prüfsemantik bleiben erhalten.

22 Testmethoden bestehen isoliert unter Windows/Python 3.14.7 und
Linux/Python 3.12.3 ohne SKIP: die 13 Footer- und neun Kanalhashmethoden.
Die genaue 71-Byte-Referenz, alle Ordinals, getrennte Kanal-/Längenbindung,
unveränderte opake Rohbytes, gemeinsame Grenze und frühe Typ-/Boundsabweisung
sowie private Providerfehler sind enthalten. Ein Digest attestiert weder
Providerherkunft noch EOF (End of File; Ende eines Eingabestroms), Kontext oder tatsächliche Übertragung.
Checkpoint B: Kandidat 1 von höchstens 2, insgesamt zwei von vier verbraucht;
keine Quellenkorrektur erforderlich, Modellverbrauch unbekannt. Der unabhängige
Implementierungsreview zu Base `5466a44…` und Head
`7cd88de3fc34802a076e698e650d08484d1be9d2` schließt ohne offene P1/P2/P3-Befunde.
Alle acht CI-Gates dieses Stands bestehen, einschließlich der
[Komponentensuite](https://github.com/gecompat/SQL_PerformanceSchulung/actions/runs/39402983455).
Die Abschlussrevision ergänzt ausschließlich Evidenz; Quelle, Suite und
Workflow bleiben zum reviewten Quellenstand unverändert.
[PR258](https://github.com/gecompat/SQL_PerformanceSchulung/pull/258) bindet
finale Head-/Base-Gates, Main-Integration und eigene Branchbereinigung.
Diese bleiben vor dem vollständigen Integrationsabschluss notwendig.

## Offene vollständige Abnahme

Nach A/B bleiben vollständige §33-Loaderrecordprüfung,
vollständige Profil-/K8-/D9-Bindung, Provider-/Encoder-PRE/POST, echter Kanal,
eigener Exit, Consumption, unabhängiger Cleanup und die bisherigen Ressourcen-/
Deadlinegates offen. Erst deren gemeinsamer belegter Pfad darf den reservierten
vollständigen Matchstatus oder `SESSION_COMPLETE` verwenden.
