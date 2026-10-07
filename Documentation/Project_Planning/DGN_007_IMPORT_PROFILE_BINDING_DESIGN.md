# DGN-007 – Entwurf der Parent-/Worker-Profilbindung

| Merkmal | Wert |
|---|---|
| Stand | 2026-10-07 |
| Repositorybasis | `e75baeb811c1a9973198200c94aa37a795d64b1a` nach PR85 |
| Status | `DESIGNED`; reiner Matcher separat implementiert, Workerroute offen |
| Vorgesehener Teilclaim | `MATCHED_REPORTED_DECLARATION` |
| Geltung | `PROJECT_SEMANTIC`; deklarierter skalarer Vergleich |
| Grenze | keine Trust-, Worker-, UsedBytes-, Cleanup-, SQL- oder Methodenattestation |

Dieser Entwurf verbindet das unveränderte
[Eingangsprotokoll](DGN_007_IMPORT_PROBE_INPUT_PROTOCOL.md) mit dem getrennten
[Profilvorschnitt](DGN_007_IMPORT_RUNTIME_PROFILE.md). Er konkretisiert die
nächste Vorbereitung des [Importentwurfs](DGN_007_IMPORT_USED_BYTES_PROBE_DESIGN.md).
Die neun DGN-Quellen und alle 27 Bundlemember bleiben unverändert.
Der getrennte [reine Matcher](DGN_007_IMPORT_PROFILE_BINDING_MATCHER.md) prüft
ausschließlich skalare Deklarationen und Berichte; er startet keinen Worker
und importiert keine Kandidatenquellen.

## 1. Bestehende Grenzen und dokumentierte Fakten

Der Profilvorschnitt hält tatsächliche Module-, Spec-, Loader-, Finder- und
Hookobjekte innerhalb eines Kontrollinterpreters. Diese Liveanker sind keine
zwischen Prozessen übertragbaren Identitäten. Python beschreibt `id` als während
der Objektlebenszeit eindeutige Identität; spätere Objekte können denselben Wert
erhalten. Daraus folgt keine prozessübergreifende Objektbindung.
[Python 3.12: id](https://docs.python.org/3.12/library/functions.html#id),
geprüft am 2026-10-07; Seitenkopf aktuell 3.12.15.

`ModuleSpec` beschreibt Importmetadaten. Insbesondere sind `origin` und
`__file__` nicht automatisch synchronisiert. Ein übereinstimmender Text ist
deshalb kein Beleg tatsächlich verwendeter Bytes oder ursprünglicher
Objektidentität.
[Python 3.12: ModuleSpec](https://docs.python.org/3.12/library/importlib.html#importlib.machinery.ModuleSpec),
geprüft am 2026-10-07. Die folgenden engeren Bindungsregeln sind Projektentwurf.

Die bisherige Profil-API gibt weiterhin ausschließlich `ProfileReport` zurück.
Die getrennte Erweiterung `observe_current_interpreter_records` liefert jetzt
zusätzlich ihre vollständig geprüfte lokale Abschlussaufnahme; bei Ablehnung
enthält `ObservationResult` keine Observation. Diese Rückgabe attestiert keine
Workerbeobachtung, Scalarprojektion oder spätere aktuelle Cachemitgliedschaft.
Die heutige Auswahl erlaubt genau die Kontrollnamen `__main__` und
`dgn007_import_runtime_profile`. Input82 importiert dagegen auch Bundle und
Edges. Eine vollständige Parentinventur passt daher nicht unverändert als
Workerinventur; zusätzliche Controlmodule dürfen nicht pauschal freigegeben werden.

## 2. Kontrollauswahl vor Transfer

Der vertrauenswürdige Parent hält seine erwartete Installation, drei getrennte
Workerdeklarationen und den ursprünglichen `PreparedInput` vor jedem Transfer
unveränderlich im Speicher. Die gewählte Kontrollruntime bleibt ausdrücklich
`DECLARED_SETUP_PYTHON_CONTROL_RUNTIME`: eine Annahme des Kontrollaufrufers,
keine aus dem Workerbericht abgeleitete Herkunft oder Rechteerteilung.

Die gemeinsame Installationsauswahl benennt CPython, exakte 3.12-Patchversion,
Executablelocator und getrennten Executabletarget, ABI, Prefixe, zwei
Bibliotheksroots, Suchpfade, Isolationflags und den ausdrücklich nicht
verwendeten fehlenden Zip-Suchpfadeintrag. Directory-/Extensionauswahl,
Builtin/Frozen und höchstens zwei optional benannte Dateifingerprints bleiben
getrennt. Dateihashes bestätigen keine bereits ausgeführten Bibliotheksbytes.

Jeder Worker erhält eine vorher vollständig gewählte Bootstrapinventur seiner
Kontroll- und Stdlibmodule. Seine Controlrollen und deren genaue Modulnamen,
Origins und Loaderformen werden separat benannt. Der Parent kopiert weder seine
gesamte Inventur noch wählt der Worker seine eigene erfolgreiche Baseline.
Die konkrete ausführbare Bootstrapquelle und ihr notwendiger Importumfang sind
vor dem späteren Adapter zu entscheiden und gegen das bestehende Profil abzugleichen.

Absolute Origins, Dateipfade und Installationlocator bleiben private Daten.
Der Vergleich verwendet deren exakt deklarierte Texte. Er ersetzt keine Roots,
normalisiert keine Pfade stillschweigend und interpretiert Alias-/Symlinktexte
nicht als Gleichheit. Eine spätere physische Pfadprüfung gehört zum Adapter.
Builtin/Frozen-Origins sowie ein fehlender Spec im ausdrücklich gewählten
Kontrollfall erhalten feste eigene Repräsentationen; fehlende Pflichtfelder
dürfen daraus nicht nachträglich ergänzt werden.

## 3. Vorgesehene skalare DTOs und API

Die folgenden skalaren Formen sind im getrennten reinen Matcher umgesetzt. DTOs
sind frozen Records aus exakten primitiven Typen, begrenzten Tupeln und Bytes;
keine Livepointer, Callables, freien Mappings oder ausführbaren Quellen.

| DTO | Pflichtinhalt |
|---|---|
| `InstallationDeclaration` | explizite Annahme und sämtliche oben gewählten Installations-/Flag-/Pfad-/Fingerprintfelder |
| `WorkerDeclaration` | Ordinal, fester Einstieg, `PRE_IMPORT`, gemeinsam gewählte Installation und vollständige geordnete Bootstrapinventur einschließlich Controlrollen |
| `BindingContext` | Commit, Raw27-Bindung, Quellenprofil, Nonce und neun geordnete Name/Member/Hash-Zuordnungen aus dem separat gehaltenen `PreparedInput`; Ordinal/Einstieg/Phase aus der Kontrollauswahl |
| `ReportedProfile` | berichteter Kontext und vollständige skalare Installations-/Inventurfelder; keine vom Sender auswählbare erwartete Deklaration |

Die implementierte reine Funktion lautet
`match_reported_profile(expected, reported, context)`.
Sie prüft zuerst jede Form und alle Grenzen, dann interne Konsistenz und
Gleichheit gegen die separat gehaltenen Erwartungen. Ein später ungültiger
Record darf nicht durch eine frühe Abweichung verdeckt werden.
Sie liest keine Datei, fragt keine Runtime ab und startet keinen Prozess.

Ein Modulrecord enthält `name` als Cachekey, `moduleName`, `specName`,
`origin`, `file`, `kind`, `locations` und feste Loaderlabels. Reihenfolge,
fehlende beziehungsweise zusätzliche Namen und jede Pflichtfeldabweichung
werden geschlossen abgewiesen. Kind, Loaderlabel, Origins und Locations müssen
konsistent sein: kein Source-Origin durch ein behauptetes Builtinlabel umgehen.
Site-, Namespace-, Lazy- und freie Ziploader bleiben außerhalb dieser Auswahl.
Finder-/Hooklabels beschreiben ausschließlich berichtete Kategorien; sie
attestieren keine tatsächlich installierten oder ausgeführten Objekte.

Die bereits fest enumerierten Frozen-Bootstrapaliases können einen berichteten
Gleichheitsverband führen. Nur vorher benannte Paare und konsistente Modul-/
Specnamen sind zulässig. Dieser Verband ist skalare Deklaration, keine Prüfung
gleicher Liveobjekte im Worker und keine allgemeine DGN-Aliasfreigabe.
Numerische Objektadressen, `id`-Werte oder deren Hashes werden nicht übertragen.

Die skalare Form wird für den nächsten reinen Codeschnitt festgelegt:

| Record | Exakte Feldmenge und Darstellung |
|---|---|
| Installation | `assumption,platform,implementation,version,executable,executable_target,prefixes,abi,paths,roots,inert_zip,flags,finders,hooks,files`; `platform="linux"`, `implementation="cpython"`, `version=(3,12,patch)`, `patch` ganzzahlig 0..999; `prefixes=(prefix,exec_prefix,base_prefix,base_exec_prefix)` vier Texte und `roots` zwei Texte; Flags `(isolated,no_site,dont_write_bytecode,ignore_environment,safe_path,optimize)=(1,1,1,1,1,0)`; Finderlabels exakt `BUILTIN,FROZEN,PATH`, Hooklabels exakt `ZIPIMPORTER,FILEFINDER` |
| Dateifingerprint | `path,size,sha256`; höchstens zwei Records, falls vorhanden zuerst Executabletarget, zweiter nur unter gewählten Roots; `size` 0..33554432, Summe höchstens 67108864, SHA256 64 kleine Hexzeichen |
| Workerdeklaration | `ordinal,entry,phase,installation,controls,modules`; Controls geordnete eindeutige Namen mit genau zugehörigen `CONTROL`-Records; Module eindeutig nach `name` sortiert |
| Modul | `name,moduleName,specName,origin,file,kind,locations,loader,loaderName,loaderPath,aliasGroup`; `specName=null` ausschließlich bei ausdrücklich gewähltem `CONTROL` ohne Spec, dann `origin=""`, `locations=()`; fehlendes `file` wird ausdrücklich als `""` deklariert; Loaderlabels `NONE,BUILTIN,FROZEN,SOURCE,EXTENSION` mit passendem Kind; bei Source-/Extensionloadern `loaderName=name` und `loaderPath=file`, sonst beide Texte `""` |
| Kontext | `commit,raw27_binding,source_profile,nonce,modules,ordinal,entry,phase`; neun Modulzeilen exakt mit Input82-Feldern `ordinal,module,member,size,sha256`; Nonce intern Bytes, kanonisch 64 kleine Hexzeichen |
| Bericht | `context,installation,controls,modules`; vollständige skalare Werte, keine Liveanker oder eigenen Sollwerte |

`aliasGroup` ist exakt `()` oder ein vorher gewähltes sortiertes Zweierpaar aus
`_frozen_importlib/importlib._bootstrap`, `_frozen_importlib_external/importlib._bootstrap_external`,
`_collections_abc/collections.abc`, `os.path/posixpath`. Ein nichtleerer Verband
erfordert beide Cachekeys in der vollständigen Inventur, denselben Verband in
beiden Records und jeweils die festen Modul-/Specnamen des Profilvorschnitts.
Fehlender oder widersprüchlicher Partner ist ein fester Formfehler. Ein einzeln
vorhandener erlaubter Frozenrecord darf ausschließlich `aliasGroup=()` tragen.
Diese Konsistenzprüfung attestiert keine gemeinsame Liveidentität.
Exakte `str/int/tuple/bytes` werden vor Vergleich geprüft; bool und Subklassen
sind keine Zahlenrecords. Kein Text enthält NUL oder ungepaarte Surrogate.
`kind` ist genau `BUILTIN,FROZEN,SOURCE,EXTENSION,CONTROL`; Listenlängen bleiben
höchstens 256, Controls sind eine Teilmenge der vollständigen Inventur.
Absolute POSIX-Locator haben keine `.`-/`..`-Komponenten oder doppelten Slashes;
abweichende Texte werden abgelehnt statt umgeschrieben. Physische Auflösung
und Existenz bleiben Adapteraufgaben. Bei `SOURCE`/`EXTENSION` müssen `origin`,
`file` und jede Location lexikalisch innerhalb der gewählten Roots liegen;
Containment ist Rootgleichheit oder Roottext plus `/`, keine rohe Prefixähnlichkeit.
Installationssuchpfade sind ausschließlich gewählte Roots oder exakt `inert_zip`.
`CONTROL` bleibt separat ausdrücklich benannt, ohne generischen Rootbypass für
andere Records. Für Namen außerhalb der festen Frozen-Namenszuordnung entsprechen
`moduleName` und `specName` dem Cachekey `name`; die festen Frozen-Modul-/Specnamen
gelten auch bei `aliasGroup=()`. Nur der benannte specfreie Kontrollfall hat `specName=null`.
Diese Regeln gelten auch bei identisch kontaminiertem Soll und Bericht.
Modulordinal ist 0..8, Membergröße
0..131072 und Bodygesamtgröße höchstens 1048576; Workerordinal ist 1..3.
In `PRE_IMPORT` darf keiner der neun eigenen DGN-Modulnamen aus dem festen
Mapping und keiner der Elternnamen `Tests` oder `Tests.Contracts` in der
berichteten Cacheinventur vorkommen, weder als `CONTROL` noch als `SOURCE`
oder anderes Kind. Auch eine identisch kontaminierte Erwartung ist ungültig;
Übereinstimmung hebt diesen eigenen geschlossenen Formschutz nicht auf.

## 4. Kontextbindung an den unveränderten Eingang

`BindingContext` wird kontrollseitig aus einem vollständig formgeprüften
ursprünglichen `PreparedInput` abgeleitet. Commit hat 40 und Raw27-Bindung 64
kleine Hexzeichen. `source_profile` ist exakt `dgn007-docker-sql-only/v1`.
Die Nonce enthält genau 32 Bytes. Alle neun Modul-/Memberzuordnungen folgen
dem unveränderten festen Mapping; jeder SHA256 bleibt an dieselben gehaltenen
Rohbytes gebunden, ohne LF-Konversion. Ein früherer `prepare_input`-Erfolg oder
die tatsächliche Herkunft wird dadurch nicht unabhängig attestiert.

| Workerordinal | Fester Einstieg | Phase |
|---|---|---|
| 1 | `run_dgn007_automated_setup` | `PRE_IMPORT` |
| 2 | `docker_sqlcmd_proxy` | `PRE_IMPORT` |
| 3 | `run_demo` | `PRE_IMPORT` |

Ordinal und Einstieg sind Kontrollmetadaten, keine Identität eines tatsächlich
gestarteten Prozesses. Nonce und Kontextdigest binden Inhalte an die Erwartung;
sie sind keine Signatur. Eine erneut vorgelegte vollständig gültige Nachricht
kann beim reinen Matcher erneut übereinstimmen. Einmalige Consumption,
Worker-/Kanalbindung und Replayabwehr bleiben Aufgabe des späteren Lifecycles.

## 5. Gemeinsame Bounds und Ergebnisgrenze

Der vorgesehene private Record erhält je Worker höchstens **16 KiB gemeinsam**:
sämtliche Header, Input82-Metadata, Profildeklaration und Bindungsmetadata zählen
in dieses eine Budget. Es gibt keine zusätzlichen 16 KiB für das Profil.
Die neun Bodies behalten ihren bisherigen separaten 1-MiB-Gesamtcap und
128-KiB-Membercap. Das bestehende Input82-Protokoll wird hier nicht geändert.

Zusätzlich gelten höchstens 256 Stdlib-/Kontrollrecords und höchstens 4096
UTF-8-Bytes je Textfeld. Diese Grenzen gelten gleichzeitig. Eine vollständige
Inventur darf trotz gültiger Einzelwerte das Gesamtbudget überschreiten;
dann folgt ein fester Fehler, kein Filtern, Abschneiden oder schwächerer Match.
Für die reine Größenrechnung ist `C(x)` ASCII-Encoding von
`json.dumps(x,sort_keys=True,ensure_ascii=True,separators=(",",":"),allow_nan=False)`;
Tupel werden JSON-Arrays, nur die ausdrücklich erlaubten Nullfelder werden null.
Die vorgeschlagene gemeinsame Metadataform hat exakt `input,worker,context`:
`input` ist die vollständige unveränderte Input82-Metadata einschließlich
`context_sha256`, `worker` die vollständige Workerdeklaration, `context` der
vollständige Bindungskontext. Es gilt **16 + len(C(metadata)) <= 16384**;
auch doppelt dargestellte Felder zählen tatsächlich. Ein Bericht wird mit
`16 + len(C(reported)) <= 16384` zusätzlich begrenzt, ohne Zusatzbudget.
Der reine Matcher prüft diese deklarativen Größen; er baut keinen Wireframe.
DGNI001 verlangt heute eine exakte Metadatafeldmenge. Die kombinierte Form ist
deshalb explizite spätere Protokollarbeit, keine optionale v1-Anreicherung oder
hier eingeführte Codecversion. Darstellbarkeit einer künftigen Inventur ist offen.

SHA256-Digests verwenden dieselbe Darstellung und getrennte feste Domains:
`installation-declaration`, `worker-declaration`, `profile-binding-context`, jeweils
als `C([domain,record])` ohne eigenes Digestfeld. Input82-`source_profile` bleibt
das Edge-AST-Profil und bezeichnet keine Interpreterinstallation. Digests binden
deklarierte Inhalte; sie attestieren keine Beobachtung oder unabhängige Herkunft.

Alle drei Workers und stdout/stderr behalten zusammen höchstens 64 KiB Ausgabe
mit höchstens 1024 Bytes je Scalarzeile. Der spätere Reader begrenzt vor Decode
und Pufferung. Der reine Matcher bekommt begrenzte Records, keinen Stream.
Die gemeinsame 20-s-Probenzeit und kumulativ 10-s-Cleanupgrenze bleiben im
vollständigen Importentwurf; dieser Slice liefert keine Zeit-/Cleanupreceipts.

Ein Match lautet ausschließlich `MATCHED_REPORTED_DECLARATION`.
Öffentliche Reports enthalten feste Labels, gegebenenfalls den kontrollseitig
berechneten Kontextdigest, und ausdrücklich benannte Annahmeflags.
Sie enthalten keine absoluten Pfade, Rohfehler, Quelltexte oder Noncewerte.
`trust_attested`, `runtime_attested`, `import_used_bytes_attested` und
`method_approved` bleiben false. Unbekannte oder malformed Pflichtangaben
erzeugen feste Fehler; bloße JSON-/Bool-/Digestangaben liefern keinen Runtimebeleg.

## 6. Gegenprobenmatrix und reiner Codeschnitt

| Gegenprobe | Erforderliche Aussage |
|---|---|
| vollständig passende getrennte Deklaration/Bericht/Kontext | nur skalarer Match unter ausdrücklich gewählter Annahme |
| andere Patchversion, ABI, Executabletarget, Root, Prefix oder Flags | fester Fehler; keine automatische Profilauswahl |
| Parentinventur als Workerinventur, fehlender oder zusätzlicher Controlname | fester Fehler; kein Kopieren oder Allowlistausbau |
| Bericht enthält passende eigene Erwartung, separat gehaltene Erwartung weicht ab | fester Fehler; Bericht ist keine Trustquelle |
| alter Nonce/Commit/Raw27-/Quellenprofilwert oder veränderter Memberhash | fester Kontextfehler |
| anderer Ordinal/Einstieg oder Phase nach Import | fester Fehler; kein Scopekanonisieren |
| geänderte Origin/File/Locations, Source als Builtin, unbekannter Loader | fester Konsistenzfehler |
| identisch fremder Source-/Extensionpfad in Soll und Bericht oder Root-Prefixähnlichkeit | fester Formfehler; deklarative Gleichheit ersetzt kein lexikalisches Containment |
| Source-/Extensionloader mit anderem `loaderName` oder `loaderPath` | fester Konsistenzfehler vor Vergleich gegen die Erwartung |
| eigener DGN-Name oder `Tests`/`Tests.Contracts` bereits im PRE_IMPORT-Cache, auch identisch im Soll | fester Fehler; keine Control-/Sourcefreigabe durch Übereinstimmung |
| freier Alias, widersprüchlicher Frozenverband oder numerischer Pointer als Beleg | fester Fehler; keine Liveidentitätsbehauptung |
| nichtleerer Frozenverband mit fehlendem Partner oder anderem Verband/Modul-/Specnamen | fester Formfehler; ein einzelner erlaubter Frozenrecord hat ausschließlich `aliasGroup=()` |
| identische Texte bei unterschiedlichen tatsächlichen Modulobjekten | Matcher beweist deren Identität ausdrücklich nicht |
| fremde Typen, bool als Zahl, fehlende/duplizierte/zusätzliche Felder | geschlossen vor fremden Gettern, Vergleichen oder Iteration abweisen |
| 257 Records, Feld größer 4096 Bytes, gemeinsamer Record größer 16 KiB | fester Fehler vor unbeschränkter Verarbeitung; kein Teilmatch |
| gültige Nachricht erneut unter demselben Kontext | skalarer Match kann erneut gelingen; keine Consumption-/Replayattestation |
| passend berichtete Werte ohne tatsächlichen Worker oder als manipulierte Nachricht | kein Worker-/Kanal-/Beobachtungsbeleg |

Die feste Form aus §3 und Rechnung aus §5 sind die verbindliche Grundlage des
reinen DTO-Matchers. Erwartete Workerinventuren werden vom Kontrollaufrufer
vor dem Bericht gewählt; die Tests verwenden synthetische private Locator und vollständige
positive/negative Records. Keine neue Runtime oder Produktionsdatenaufnahme.
Die getrennte Implementierung liegt in
[`dgn007_import_profile_binding.py`](../../Tests/Tools/dgn007_import_profile_binding.py)
und [`test_dgn007_import_profile_binding.py`](../../Tests/Static/test_dgn007_import_profile_binding.py).
Validierung und verbleibende Grenzen stehen im [Matcher-Nachweis](DGN_007_IMPORT_PROFILE_BINDING_MATCHER.md).

## 7. Getrennter späterer Adapter und verbleibende Gates

Der tatsächliche Adapter braucht zuerst eine vollständig benannte Bootstrapquelle
und deren eigene Importkanten. Die lokale Record-Rückgabe des Profilvorschnitts ist inzwischen getrennt
implementiert; ein `ProfileReport` allein genügt weiterhin nicht. Die
Scalarprojektion bleibt offen. Eine erneute reine `validate_profile`-Prüfung
kontrolliert gehaltene Modul-/Spec-/Loaderobjekte, aber nicht deren aktuelle
`sys.modules`-Mitgliedschaft oder heutige Suchpfad-/Finder-/Hookzustände.
Spätere aktuelle Runtimeverwendung braucht deshalb eine frische Aufnahme;
lokale Objektkohärenz muss vor Projektion geprüft und von der übertragenen
Deklaration getrennt gehalten werden.
Keine künstlichen Recordwerte oder erfolgreiche Observation aus einem Flag ergänzen.

Danach werden tatsächlicher Workerstart, eigener Kanal, Nonce/Ordinal-Consumption,
vollständiger Empfang, gemeinsamer Budgetverbrauch und unabhängiger Cleanup
gebunden. Harte Unterbrechung ohne Receipt bleibt unbekannt; Kill oder Exit
ersetzt keinen Abwesenheitsbeleg. Linux-/Python-3.12-Worker, kontrollierter
Resolver, tatsächliche DGN-Loaderverwendung und Importabschluss sind weitere
separate Schritte. Diese Dokumentation startet sie nicht und erweitert keine
SQL-/Docker-/Collectorautorität. Gewöhnliche begrenzte Offlineentwicklung bleibt
im bestehenden Entwicklungsauftrag; materielle Methodengrenzen bleiben erhalten.

G13, v1, DEC-068, historische FAILs, offene PR68 und die zurückgestellte
Capture-API bleiben unverändert. Kein RunRecord, Incidentvergleich, Ursache,
Toleranz, Mitigation oder Capstone-/Methodenfreigabe folgt aus diesem Entwurf.
