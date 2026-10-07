# DGN-007 – Reiner Vergleich deklarierter Workerprofile

| Merkmal | Wert |
|---|---|
| Stand | 2026-10-07 |
| Repositorybasis | `e350fda8eb2cbcdbf36be450d7a8e4c6b965445e` nach PR86 |
| Status | `IMPLEMENTED_SCALAR_MATCHER`; lokale Validierung siehe unten |
| Begrenzter Claim | `MATCHED_REPORTED_DECLARATION` |
| Geltung | `PROJECT_SEMANTIC`; portable synthetische Vertragsgegenproben |
| Grenze | keine tatsächliche Workerbeobachtung, Trust-, Import-, Cleanup-, SQL- oder Methodenattestation |

Der Schnitt setzt ausschließlich die skalaren Formen und Größenrechnungen des
[Parent-/Worker-Profilbindungsvertrags](DGN_007_IMPORT_PROFILE_BINDING_DESIGN.md)
um. Erwartete Installation und vollständige Bootstrapinventur werden weiterhin
separat vom Kontrollaufrufer gewählt. Gleiche Texte oder Digests liefern keine
Identität eines gestarteten Workers oder tatsächlich verwendeter Bibliotheksbytes.
Der [Profilvorschnitt](DGN_007_IMPORT_RUNTIME_PROFILE.md) und das unveränderte
[Eingangsprotokoll](DGN_007_IMPORT_PROBE_INPUT_PROTOCOL.md) bleiben getrennte Komponenten.

## API und feste Formen

Die Implementierung liegt in
[`dgn007_import_profile_binding.py`](../../Tests/Tools/dgn007_import_profile_binding.py).
`derive_binding_context(prepared, ordinal)` prüft den originalen
`PreparedInput` einschließlich der neun unveränderten Rohbytehashes und übernimmt
Commit, Raw27-Bindung, Quellenprofil, Nonce und feste Memberzuordnung unverändert.
Ordinal 1/2/3 benennt unverändert Runner/Proxy/Harness; die Phase ist `PRE_IMPORT`.
Dies bestätigt die Form der gehaltenen Daten, keine frühere Quellenverifikation.

`match_reported_profile(expected, reported, context)` vergleicht ausschließlich skalare
DTOs. Sämtliche Formen und internen Zusammenhänge werden vor dem
Soll-/Berichtsvergleich geprüft; eine frühe gültige Abweichung darf einen später
ungültigen Record nicht verdecken. Exakte DTO- und primitive Typen werden vor
fremden Gettern, Vergleichen oder Iteration geprüft. Freie Mappings, Subklassen,
bool als Zahl und fehlende Pflichtfelder sind kein alternativer Eingang.

Die Auswahl ist Linux/CPython 3.12 mit exakter deklarierter Patchversion,
vier Prefixen, zwei Roots, sechs festen Flags und festen Finder-/Hooklabels.
Source-/Extensionpfade müssen lexikalisch innerhalb der gewählten Roots liegen;
eine ähnliche Zeichenfolge genügt nicht. Source-/Extensionloadername und -pfad
müssen mit dem Modulrecord übereinstimmen. Es gibt keine physische Pfadauflösung
oder Existenzprüfung. `CONTROL` wird separat vollständig gewählt und konsistent
geprüft; eigene DGN-Namen und `Tests`/`Tests.Contracts` bleiben in `PRE_IMPORT`
auch bei identisch kontaminiertem Soll und Bericht ausgeschlossen.

Die vier festen Frozen-Aliaspaare behalten ihre festen Modul-/Specnamen. Ein
nichtleerer deklarierter Verband benötigt beide Cachekeys mit demselben Verband;
ein einzeln vorhandener erlaubter Frozenrecord trägt ausschließlich `aliasGroup=()`.
Diese Prüfung belegt keine gemeinsame Liveobjektidentität.

## Gemeinsame Grenzen und Ergebnis

Die vollständige unveränderte Input82-Metadata einschließlich `context_sha256`,
Workerdeklaration und Bindungskontext zählen gemeinsam:
`16 + len(C({"input": input, "worker": worker, "context": context})) <= 16384`.
Doppelt dargestellte Felder zählen
tatsächlich. Der Bericht besitzt ebenfalls `16 + len(C(reported)) <= 16384`;
es gibt keinen zusätzlichen Profil- oder Ausgabebudgetanspruch.
`C` verwendet sortierte Schlüssel, ASCII-Escaping, kompakte Separatoren und
`allow_nan=False`. Die Prüfung muss eine große Gesamtdarstellung vor vollständiger
Pufferaufnahme abweisen. 256 Records und 4096 UTF-8-Bytes je Textfeld gelten
gleichzeitig; gültige Einzelcaps garantieren kein gültiges Gesamtbudget.

Die neun Rohbodies behalten 128 KiB je Member und 1 MiB insgesamt. Der Matcher
baut keinen Frame und verändert weder `DGNI001` noch die v1-Metadatafeldmenge.
Installation, Workerdeklaration und Bindungskontext erhalten getrennte feste
Digestdomains. Diese Digests binden deklarierte Inhalte, keine Herkunft.

Ein erfolgreicher öffentlicher Report darf nur `MATCHED_REPORTED_DECLARATION`
ausweisen, mit festen Fehlerlabels beziehungsweise kontrollseitigem Kontextdigest
und ausdrücklich benannter Kontrollannahme. Absolute Locator, Nonce, Rohfehler
und Quellen bleiben privat. `trust_attested`, `runtime_attested`,
`import_used_bytes_attested` und `method_approved` bleiben false.
Dieselbe gültige Nachricht kann unter demselben Kontext erneut passen;
Consumption und Replayabwehr werden damit ausdrücklich nicht attestiert.

## Validierung und verbleibender Umfang

Die synthetischen Gegenproben liegen in
[`test_dgn007_import_profile_binding.py`](../../Tests/Static/test_dgn007_import_profile_binding.py).
Lokal bestanden unter Python 3.12.14 alle 38 Testmethoden ohne SKIP
(0.092 s). Unabhängiger Review, Projektvalidatoren und CI werden vor Integration
am finalen Stand getrennt geprüft; ihre konkreten Ergebnisse werden im Pull Request dokumentiert.

```powershell
python -I -S -B Tests/Static/test_dgn007_import_profile_binding.py
```

Die Offline-CI ergänzt diesen Aufruf als sechste Suite; die bisherigen fünf
Bundle-, Edge-, Input-, Loader- und Profilbefehle bleiben unverändert. Die echte
Linux-Bootstrapbeobachtung bleibt ein separater Prozess im vorhandenen Profiltest.

Der spätere Adapter benötigt weiterhin eine konkret benannte Workerbootstrapquelle
mit vollständigem Importumfang und passende separat gewählte Inventuren. Geprüfte
lokale Observationrecords, kombinierter Codec, tatsächlicher Workerstart, eigener
Kanal, vollständiger Empfang und Nonce-/Ordinal-Consumption bleiben offen.
Anschließend folgen Quellenauflösung, tatsächliche DGN-Loaderverwendung und
Importabschluss sowie begrenzte eigene Worker mit unabhängig geprüftem Cleanup.
Die gemeinsamen 20-s-Proben- und kumulativ 10-s-Cleanupgrenzen sind dadurch
noch nicht ausgeführt oder belegt. G13, v1, DEC-068, historische FAILs, offene
PR68 und die zurückgestellte Capture-API bleiben unverändert.

Primärquellen, geprüft am 2026-10-07: Python 3.12
[JSONEncoder und kanonische Darstellungsparameter](https://docs.python.org/3.12/library/json.html#json.JSONEncoder.iterencode)
und [Dataclasses](https://docs.python.org/3.12/library/dataclasses.html#frozen-instances).
`iterencode` liefert Teiltexte; eine feste Byteobergrenze ist zusätzlich vom
Projekt durchzusetzen. `frozen=True` ersetzt weder vollständige Formprüfung
noch einen Schutz gegen privilegierte Mutation im Kontrollprozess.
