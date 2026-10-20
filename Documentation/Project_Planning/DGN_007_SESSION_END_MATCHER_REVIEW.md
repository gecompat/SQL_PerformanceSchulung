# DGN-007 – vollständiger deklarativer SESSION_END-Matcher

Stand: 2026-10-20. Basis `d0c453f212523fa30c8d74ee47fcbb15f84b8b54` nach
PR258; Status `C1_SOURCE_TEST_PRE_PENDING`. Maßgeblich sind
[§31, §33 und §34](DGN_007_IMPORT_PROFILE_BINDING_DESIGN.md#34-session_end-counts-und-kanalhashpräbild).
Der Benutzer beauftragt die vollständige Matcherwelle mit unabhängigem Review,
lokalen Tests, grünen aktuellen Gates, Main-Integration und Branchbereinigung.

## Endlicher Umfang und Auswahl vor Sourceänderung

Ein Implementierungsowner, höchstens drei stabile Quellenkandidaten,
Checkpoint nach dem ersten, harte Grenze nach dem dritten. Ein unabhängiger
Auswahl-PRE, ein Quellen-/Test-POST und höchstens ein gezielter Befundnachlauf
bei geändertem Input. Verbrauchsmessung ist nicht verfügbar; Modellverbrauch
bleibt unbekannt. Alte ausgeschöpfte Import-/Quell-/Generatorversuche werden
nicht fortgesetzt. Diese neue additive Route hat einen eigenen Quellenrahmen.

Gewählte Quelle: `Tests/Tools/dgn007_control_bootstrap_source.py`, ausschließlich
ein neuer Inlineblock und eine fünfzehnte additive Builderroute
`build_inline_session_end_control_bootstrap`. Alle vierzehn bisherigen Builder
und ihre erzeugten Quellen bleiben unverändert. Scriptcap 131072 Bytes,
Profilcap, fünf vorhandene Imports und Runtimebundle bleiben unverändert.
Die reinen Footer-/Hashprimitiven aus PR257/258 bleiben unverändert; sie ersetzen
im vollständigen Pfad keine gehaltenen Provider-/Encoderanker.

Gewählte API der erzeugten Quelle:

```python
_inline_match_session_end(records, stderr, *, expected_format,
                         expected_phase, expected_reported, expected_context)
```

`records` ist das vollständige exakte Tupel erhaltener stdout-Zeilen einschließlich
Profil, INPUT_COMPLETE, Loaderrecords und genau einem Footer; `stderr` sind die
separat gehaltenen vollständigen opaken Bytes. Callerformat ist ausschließlich
`pooled-combined-input-design/v1`, Planphase `AWAIT_SESSION_END`. Separates
vollständiges R4 und K8 sind Callerannahmen; kein Callerfeld wird aus Records
abgeleitet oder ergänzt. K.phase bleibt `PRE_IMPORT`.

Erfolg liefert ausschließlich
`("MATCHED_DECLARED_SESSION_END", "NONE", (original_footer, actual_fields))`.
Ablehnung liefert `("REJECTED_SESSION_END", fixed_issue, None)` ohne private
Exceptionwerte. Dies ist `PROJECT_SEMANTIC`: keine reale Pipeaufnahme,
EOF-/Exit-/Cleanup-/Consumption-/Runtime-/Trust-/UsedBytesattestation und kein
Ledgerübergang. Die zukünftige Kanal-/Ownerintegration muss EOFs und Ressourcen
separat binden; dieser Matcher konsumiert keine Ledger-/Replayberechtigung.

## Geschlossene Prüfphasen

Vor Parser/Kopie: exaktes äußeres Tupel, höchstens 43 Zeilen, sämtliche exakten
Bytes und vollständige Caller-R4-/K8-/D9-Primitive; je Zeile 1–1024 Bytes,
Controls/Loader/Footer höchstens 256, insgesamt stdout einschließlich Footer
plus stderr höchstens 65536. Keine Erhöhung der gemeinsamen Drei-Worker-Kappe;
der übergeordnete Owner muss alle drei Aufrufe zusätzlich gemeinsam buchen.

Danach sämtliche begrenzten Recordformen, Profilfragmentprimitive und der
vollständige rekonstruierte Actual-R4. Beide vollständigen R4- und das separate
K8 werden semantisch geprüft. Loader-/Footer-/INPUT_COMPLETE-Felder, Lowerhex,
Rollen, Counts und sämtliche Fehlformen werden vor Callercompare, Encoding
oder SHA vollständig geprüft. Ein früher gültiger Callerunterschied verdeckt
keinen späten Form-, Semantik- oder fehlenden Abschlussfehler.

Der vollständige Profilblock muss zuerst geschlossen sein, danach genau
INPUT_COMPLETE, dann die genaue vollständige §33-Loaderfolge, zuletzt genau
SESSION_END. Ein begrenzter Stack prüft verschachtelte SOURCE-Paare und vor
SOURCE6 geschlossene codefreie Parents. BEGIN/COMPLETE stimmen in allen übrigen
acht Feldern überein; Rolle, Sequenz, Mengen, Quellen und feste Begin-/Endfolge
stimmen. SOURCE-Rawhash ist der vollständige D5-Hash; PARENT hat nur null.
Die Prüfung liegt geschlossen innerhalb des Matchers; kein neuer operativer
Loader oder unabhängiger öffentlicher Loaderadapter wird eingeführt.

Gehaltene äußere Encoder-/Provideranker gelten vom ersten Repack bis zur letzten
Prüfung. Kanonische Profil-/Control-/Loader-/Footerbytes, Profil-SHA, vollständiger
eigener E4-K-Digest und inkrementeller Kanal-SHA verwenden diese Anker mit
unmittelbaren PREs und dominanten POSTs auch nach Fehlern. Providerverlust
dominiert Encoderverlust und sonstige Issues; kein inneres Rebaselining über
die bisherigen öffentlichen Matcher. Der Kanalhash verwendet exakt stdout vor
dem Footer und sämtliche übergebenen stderr-Bytes ohne Normalisierung.
Erst nach vollständiger intrinsischer Prüfung folgen R4-/K8-, Kontext-,
Rawhash-, Slot-, Count-, Byte- und Kanalhashbindungen.

## Eigener Harness und Abnahme

Eigener Einstieg `Tests/Static/test_dgn007_session_match.py`, isoliert mit
`python -I -S -B`. Aus der tatsächlich gelesenen bestehenden Testdatei werden
ausschließlich `Run`, semantische Fixture-/R4-Oracles und der synthetische
Provider-/Encoder-Setup-/tearDown-Pfad wiederverwendet. Der bisherige
Profilmatcher-Builder wird im Setup nur durch die vorab gebaute neue Route
ersetzt; keine geerbten alten Testmethoden oder Runtimekandidaten werden
ausgeführt. Eigene temporäre Fixturedateien werden durch `Run` geschlossen;
Realcache, Main, Sysconfig, Encoderklassen/-funktionen und Provider werden
tatsächlich nach jeder Gegenprobe geprüft und restauriert.

Eigene benannte K-/D5-/R4-, explizite Loaderereignis- und binäre Hashoracles:
alle drei vollständigen Traces; alle Feldgruppen, falsche gleiche Counts,
offene/doppelte/vertauschte Paare, fremde Parents/Rawhash/Slots, spätes D9/P11,
separater falscher K, Nonce-/Domain-/Kontextfehler, fehlende/doppelte/frühe
Footer, stdout nach Footer, begrenztes nicht-UTF8-stderr, Kanaltausch,
Trunkierung/zusätzliche Bytes, exakte Typen vor Fremddispatch, Kanonizität,
gemeinsame Bounds und Stack; tatsächlicher Encoder-/Providerdrift vor und
während JSON/SHA, dominante Fehler-POSTs, sichere private Fehler und Restores.
Wiederholung bleibt deklarativ; keine Consumptionbehauptung.

Lokal: neue Suite auf Python 3.12/Linux und vorhandener Pythonversion/Windows,
betroffene bisherige Kontrollquellensuite, Privacy jeder geänderten Datei,
Diff-/Kontinuitäts-/Registry-/Kennungsprüfungen. Die neue Suite wird einmal in
den vorhandenen Offline-Workflow `dgn007-source-bundle.yml` aufgenommen. Dessen
Selector erhält nur den neuen Test-/Nachweispfad; die Quelle und ihr vorhandener
Harness sind schon Abhängigkeiten. Keine parallele zweite Ausführung dieser
Suite in `dgn007-session-end.yml`. Bestehende Offline-Gates bleiben erhalten;
SQL wird durch diese reine Kontrollquellenänderung nicht berührt. Zentrale
Privacy und Registry-/Governance-Gates bleiben unverändert. Diese Auswahl
begrenzt zusätzlichen CI-/Logaufwand auf die neue Suite und ihre tatsächlichen
Abhängigkeiten; vorhandene breite Offline-Gates bleiben als konservative
Projektqualifikation bestehen. Keine zusätzliche Reviewkette oder Automation.

## Nachweis und offene operative Gates

Der unabhängige Auswahl-PRE zum Plan-SHA256
`1ae3413c3f98ad382d2910741563565d884c53206e921362ac1591071f8cfa1c`
ist ohne offene P1/P2/P3-Befunde freigegeben. Er bestätigt die vollständige
deklarative API-/Source-/Claimgrenze. Die neue Suite ergänzt gegenüber dem
bisherigen Harness eigene Baselines und tatsächliche Abschlussvergleiche für
`_make_iterencode`, dessen Funktionszustand und den vollständigen synthetischen
Provider-/Native-Namespace samt Factoryzustand; nur der geprüfte Aufrufzähler
darf variieren. Fehlergegenproben restaurieren ihre eigenen Mutationen in
`finally` oder begrenzten Patchkontexten, vor den Abschlussvergleichen.

Der Erststand enthält Source und eigene Gegenproben. Es wurde noch keine neue
Suite ausgeführt. Der bereits budgetierte unabhängige Quellen-/Testreview
erfüllt vor dem ersten Lauf zugleich den Source/Test-PRE aus §31.4; sein
ausdrückliches einmaliges Lauf-GO bleibt vor Testausführung und CI erforderlich.
Checkpoint: erster Quellenstand von höchstens drei; relevante alte Quellen und
neue Syntax werden zunächst rein statisch geprüft.

Echter Kanal, Loader-/Parentregistrierungsadapter, EOF/eigener Exit, Consumption,
unabhängiger Ressourcen-Cleanup, operative Inventur, Fünf-Formen-/64-KiB-Gate
und gemeinsame 20-s-/10-s-/I/O-/No-progress-Budgets bleiben separat nachzuweisen.
