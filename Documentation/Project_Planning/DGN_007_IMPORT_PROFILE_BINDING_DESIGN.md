# DGN-007 – Entwurf der Parent-/Worker-Profilbindung

| Merkmal | Wert |
|---|---|
| Stand | 2026-10-07 |
| Repositorybasis | `e75baeb811c1a9973198200c94aa37a795d64b1a` nach PR85 |
| Status | `DESIGNED`; Matcher, lokale Record-Rückgabe und skalare Projektion separat implementiert, Bootstraproute entworfen |
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
enthält `ObservationResult` keine Observation. Diese Record-Rückgabe attestiert keine
Workerbeobachtung oder spätere aktuelle Cachemitgliedschaft. Die getrennte
aktuelle Scalarprojektion ist inzwischen im Profilmodul implementiert;
sie ist keine Worker-/Trustattestation.
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
Zwei benannte Cachekeys allein bilden keinen Frozenverband: ein separat
kohärenter Sourcewrapper und ein Frozenrecord bleiben eigenständige Records
mit `aliasGroup=()`. Der lokale Projektionsguard verlangt weiterhin gemeinsame
Modul-/Specidentität, wenn beide Records als Frozenpartner vorliegen.
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
Scalarprojektion ist inzwischen als getrennter lokaler Vorschnitt implementiert. Eine erneute reine `validate_profile`-Prüfung
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

## 8. Konkreter Bootstrap- und Projektionsvorschnitt

Dieser ergänzende Designstand beruht auf `54b043dc30bb3afd522742203d8c260a9fa8235f`
nach PR88. Er wählt eine spätere Bootstraproute; deren Quelle, operative
Inventur und Codec sind noch nicht implementiert oder ausgeführt. Die getrennte
importneutrale Projektion ist inzwischen im bestehenden Profilmodul implementiert.
Die vorhandenen Linux-Profiltests sind Tests ihres eigenen Scriptbootstraps,
keine Inventur oder Abnahme des hier gewählten Workers.

### 8.1 Quelle und geschlossene Importreihenfolge

Geplanter Locator, **NICHT VORHANDEN**:
`Tests/Tools/dgn007_import_worker_bootstrap.py`. Der vertrauenswürdige Parent
wählt und prüft diese Kontrollquelle und die bestehende Profilquelle vor
einem späteren Start separat. Beide sind Kontrollprogramm, keine der neun
Kandidatenquellen und kein neuer Bestandteil der Raw27-Bindung. Ihr Review und
ihre Bytebindung attestieren weder Installationtrust noch ausgeführte Bytes.

Die gewählte Route startet ausschließlich den absoluten Scriptlocator mit
der separat gewählten absoluten CPython-3.12-Executable auf Linux und
`-I -S -B`. Der Scriptcode läuft als `__main__`; kein `-m`, PATH-Fallback oder
Scriptdirectory-Eintrag wird ergänzt. Der Bootstrap benennt vor seiner Aufnahme
als direkte Stdlibimports `importlib.util`, `sys`, `sysconfig`, `json` und `struct`.
JSON-/Rahmungsarbeit liegt später im Scriptcode, nicht in zusätzlich importierten
Projektmodulen. Die Auswahl dieser Imports legt noch keine Codecversion fest.

Die bestehende Datei `Tests/Tools/dgn007_import_runtime_profile.py` wird unter
genau `dgn007_import_runtime_profile` über einen separat gewählten absoluten
Locator und einen ausdrücklich gebundenen Source-Spec/Loader geladen. Diese
Kontrollquellenroute sucht kein Projektmodul über `sys.path` und verwendet
keinen Kandidatenlocator. Der weitere konkrete Kontrollquellenlese-/Execpfad
muss vor Ausführung geprüft werden; das bloße Loaderlabel belegt keine
tatsächlich gelesenen oder ausgeführten Kontrollbytes. Insbesondere verhindert
`-B` das Schreiben von Bytecodecache, nicht dessen Lesen.

Die direkten Imports des unveränderten Profilmoduls bleiben erhalten:
`dataclasses`, `hashlib`, `importlib.machinery`, `os`, `sys`, `sysconfig`,
`types` und `zipimport`. Ihre vollständigen transitiven Module sind vor dem
Profilabgleich ausdrücklich auszuwählen. Der Worker importiert vor dieser
Aufnahme weder Matcher, Input82, Bundle, Edges noch einen zusätzlichen
Projektionsadapter. Die Controlnamen bleiben exakt `__main__` und
`dgn007_import_runtime_profile`; keine Allowlist- oder Rooterweiterung.

Vor der ersten Aufnahme werden die ausgewählten Stdlibroots einschließlich
`DESTSHARED` sowie der separate ABI-Wert `SOABI` vollständig ermittelt und
gegen die separat gewählte Installation geprüft. Diese Initialisierung muss abgeschlossen sein, weil
`_capture` heute den Modulcache vor seinem eigenen `SOABI`-Aufruf kopiert.
Ein dadurch erst nach der Kopie geladener Sysconfig-Datenmodulrecord darf
nicht unbemerkt aus der Anfangsinventur fehlen. Die vorhandene Linux-Testfixture
initialisiert diese Werte bereits vor ihrer separaten Aufnahme; daraus folgt
keine automatische Vorinitialisierung einer neuen Bootstrapquelle.

Die Workerauswahl enthält vollständig geordnete Namen, Spec-/Loaderformen,
Origins, Locations und die benannten Frozenverbände für die konkrete
Installation und Bootstrapquelle. Sie steht separat vor der erfolgreichen
Aufnahme fest. Erst danach dürfen die zu diesen vorgewählten Namen gehörenden
lokalen Liveanker gebunden werden. Der Worker übernimmt weder seinen gesamten
beobachteten Cache als Soll noch eine erfolgreiche Aufnahme als eigene
Baseline. Parentinventur, heutige Testinventur und bloße Stdlibnamenslisten
ersetzen diese Workerauswahl nicht. Die vollständige ausführbare Auswahl
bleibt bis zur konkreten Fixture und ihrem unabhängigen Review offen.

### 8.2 Herkunft der skalaren Felder

Die getrennt implementierte Projektion liegt im vorhandenen Profilmodul und fügt keine
Bootstrapimports hinzu. Ihre private Rückgabe besteht ausschließlich aus
exakten primitiven Werten und begrenzten Tupeln; eine spätere Parentdekodierung
erstellt daraus die vorhandenen Matcher-DTOs. Keine neuen Livepointer-DTOs,
Callables, freien Wire-Mappings oder Imports des Matchers im Worker.
Die ausführbare Rückgabe-API lautet inzwischen
`observe_current_interpreter_scalars(expected, separately_known_filefinder_hook)`;
`ScalarObservationResult` enthält den festen Report und private primitive Tupel
oder bei Ablehnung `scalars=None`. Der kombinierte Codec bleibt Folgearbeit.
Die konkrete Tupleform und Validierung sind im
[Profilnachweis](DGN_007_IMPORT_RUNTIME_PROFILE.md) beschrieben.

| Feldgruppe | Ausschließliche Herkunft |
|---|---|
| `assumption,roots,inert_zip,controls` | separat gewählte `DeclaredProfile`; diese Werte fehlen in `Observation` und bleiben deklarative Auswahl |
| `platform,implementation,version,executable,executable_target,prefixes,abi,flags,paths,files` | vollständig geprüfte aktuelle Abschlussaufnahme; keine Ergänzung fehlender Messwerte aus dem Soll |
| `name,origin,file,kind,locations` je Modul | tatsächliche geprüfte Modulrecords, vollständig und in ihrer vorhandenen Reihenfolge |
| `moduleName,specName,loaderName,loaderPath` | geprüfte gehaltene Module-/Spec-/Loaderobjekte; kein Erfinden aus Cachekey oder Kindlabel |
| Finder-/Hooklabels | Finder aus geprüften festen Klassen; Hooklabel `FILEFINDER` zusätzlich aus einer separat gewählten bekannten FileFinder-Hookbindung, nicht aus `FunctionType` allein; Labels attestieren keine Herkunft |
| `aliasGroup` | ausschließlich benannte Frozenpaare mit beiden vorhandenen Cachekeys und geprüfter gemeinsamer Modul-/Specidentität; Singleton `()` |
| Commit, Raw27, Quellenprofil, Nonce, Modulzuordnungen, Ordinal/Einstieg/Phase | separat gehaltener ursprünglicher Eingang und Workerauswahl; kein aus einem PASS rekonstruierter Kontext |

Die Projektion folgt einer frischen erfolgreichen
`observe_current_interpreter_records`-Aufnahme, bevor weitere Imports oder
Kandidatenoperationen erfolgen. Vor dem Lesen der skalaren Objektfelder wird
die lokale Kohärenz erneut geprüft und nach der Projektion nochmals bestätigt.
Erst nach vollständiger Formprüfung und Abschlusskohärenz
darf die private skalare Rückgabe entstehen; jede reguläre Ablehnung liefert
keine Projektion. Ein früherer `ProfileReport` oder manuell konstruierter
`ObservationResult` ist kein Ausführungs- oder Herkunftsbeleg.

Auch dieser Ablauf behauptet keine atomare Snapshotgarantie oder dauerhafte
Cachemitgliedschaft. Der reine Validator kann nur gehaltene Anker prüfen.
Eine spätere aktuelle Runtimeverwendung benötigt erneut die tatsächliche
Aufnahme; eine zwischenzeitliche Cacheersetzung mit gleichen Texten darf
nicht durch Wiederverwendung eines früheren Reports als geprüft gelten.
Unbekannte oder konkurrierend veränderte Zustände ergeben keine Attestation.

Der heutige Profilvalidator prüft den zweiten Hook ausschließlich als exakten
`FunctionType` und auf Identität gegen die gewählte Baseline. Das identifiziert
nicht jede solche Funktion als `FileFinder.path_hook`-Ergebnis. Vor einer
Projektion als `FILEFINDER` muss deshalb die bekannte FileFinder-Hookbindung
separat aus der gewählten Kontrollbootstrapquelle feststehen. Fehlt diese
Bindung, folgt keine automatische Kategorienprojektion; gleiche fremde
Funktionen in Soll und Ist ersetzen sie nicht. Diese zusätzliche Auswahl
bleibt deklarativ und ist keine unabhängige Herkunftsattestation.

### 8.3 Formen, gemeinsame Grenzen und Abnahme

Alle projizierten Werte müssen zusätzlich die engere skalare Form aus §3
erfüllen: exakte Typen, keine bool-Zahlen/Subklassen, NUL oder ungepaarten
Surrogate; sämtliche nichtleeren File-/Locationlocator auch für Frozen und
Control absolut und ohne Normalisierung. Specfreier Control bleibt ausdrücklich
`specName=null`, `origin=""`, `locations=()`. Loaderlabels und leere
Loadernamen/-pfade folgen exakt dem Matcher; Textgleichheit ersetzt keine
Livekohärenz. Unbekannte Loader, freie Aliase oder fehlende Partner werden
nicht umgedeutet. Identisch ungültige Soll-/Istwerte bleiben ungültig.

Die vollständige Inventur wird weder gefiltert, gekürzt noch durch einen
Digest ersetzt. Ihre Darstellbarkeit wird mit der vollständigen unveränderten
Input82-Metadata, Workerdeklaration und Kontext gegen §5 geprüft:
`16 + len(C(metadata)) <= 16384`. Ein isolierter Projektionsgrößentest reicht
nicht. Ebenso bleibt die Berichtsgrenze erhalten. Passt die konkrete Auswahl
nicht, folgt ein fester Größenfehler; dieser Entwurf erhöht keinen Cap und
komprimiert keine bestehende Form. Eine andere Darstellung ist eine getrennte
zu prüfende Protokolländerung. Die tatsächliche Darstellbarkeit ist offen.

| Gegenprobe | Vorgesehene Abnahme |
|---|---|
| Bootstrap importiert Matcher/Input82 oder weiteres Projektmodul | vollständige Profilablehnung, keine Control-/Rootfreigabe oder Cachefilterung |
| Inventur entsteht erst aus erfolgreichem Istbericht | keine gültige unabhängig gewählte Workerdeklaration |
| Modul/Spec/Loader oder Frozenpartner wird nach Aufnahme verändert | keine erfolgreiche Projektion aus alten Ankern/Labels |
| Sysconfigdaten fehlen vor Aufnahme oder Anker ändern sich während Projektion | feste Ablehnung ohne unvollständige Inventur oder teilweise Rückgabe |
| Cachekey zeigt inzwischen auf ein anderes Objekt bei gleichen Texten | neue Aufnahme nötig; reine gehaltene Kohärenz allein genügt nicht |
| fehlendes beobachtetes Feld, fremder Typ, ungültiger Locator oder Alias | feste Ablehnung ohne ergänzte/normalisierte Projektionswerte |
| fremde harmlose Funktion identisch als zweiter Hook in Soll/Ist | kein automatisch identifiziertes `FILEFINDER`; bekannte separate Hookbindung erforderlich |
| volle gemeinsame Metadata genau am Cap und ein Byte darüber | nur genau zulässige vollständige Form; darüber Größenfehler, kein Teilmatch oder neues Zusatzbudget |
| passende skalare Rückgabe ohne tatsächlichen Worker/Kanal | ausschließlich deklarativer Inhalt, keine Worker-/Consumptionattestation |

Die importneutrale Projektion ist als getrennter lokaler Vorschnitt implementiert.
Die getrennte Charakterisierung und konservative Untergrenze in §9 schließen die
heutige Darstellung für deren gesamten Namenumfang aus. Als nächster kleiner
Schnitt folgt ein separat reviewter Darstellungsentwurf bei unveränderten
Inhalten und Caps. Danach folgen die konkret reviewte Bootstrapfixture samt
vorab separater vollständiger Sollinventur, voller Größenprüfung und kombiniertem Codec. Erst deren Abnahme
ermöglicht die tatsächliche Parent-/Workerroute aus §7. Die neun Runtimequellen,
DGNI001, alle bestehenden Bounds und false-Attestationsflags bleiben erhalten.
Kein Workerstart, DGN-Import, SQL-Lauf oder Cleanupnachweis wurde hier ausgeführt.

Quellen, geprüft am 2026-10-07: [Python 3.12: Scriptstart und Isolationflags](https://docs.python.org/3.12/using/cmdline.html),
[Importcache und Importablauf](https://docs.python.org/3.12/reference/import.html)
und [ModuleSpec](https://docs.python.org/3.12/library/importlib.html#importlib.machinery.ModuleSpec).
Für die Hookfactory gilt zusätzlich [FileFinder.path_hook](https://docs.python.org/3.12/library/importlib.html#importlib.machinery.FileFinder.path_hook).
Die engere Bootstrap-/Projektionsauswahl ist Projektentwurf, keine aus diesen
Dokumentationsseiten abgeleitete Runtimegarantie.

Die zusätzliche lokale Hookprüfung verlangt neben der separat gewählten
Funktionsreferenz passende gehaltene Factorycode- und Closurebindungen der
gewählten CPython-3.12-Kontrollruntime. Eine beliebige harmlose Funktion
wird auch bei identischer Soll-/Istbindung nicht als `FILEFINDER` projiziert.
Kein Hook/Finder wird dafür ausgeführt. Die prüfbare Struktur ist enger als
`FunctionType`; unabhängige ursprüngliche Factoryausführung oder unveränderte
Stdlibbytes werden dadurch weiterhin nicht attestiert. Die operativ separat
gewählte Workerbaseline und deren spätere Ausführungsbindung bleiben offen.

## 9. Charakterisierte Bootstraproute und Größenuntergrenze

Auf Repositorybasis `2d0ef5c08adff5117eebd11b076cd6745314a94e` nach PR90
wurde am 2026-10-07 eine getrennte private Offline-Charakterisierung unter
Linux/CPython 3.12.3 mit `-I -S -B` ausgeführt. Sie verwendete die fünf
Stdlibimports aus §8 und genau die beiden dort gewählten Kontrollrollen.
Die bestehende Profilquelle wurde über einen einmaligen begrenzten Rohread
mit 128-KiB-Cap plus Sentinel und direkte `compile`-/`exec`-Ausführung geladen.
Spec und SourceFileLoader blieben ausdrücklich gebundene Kontrollmetadaten;
`exec_module` und `get_code` wurden nicht aufgerufen. `SOABI` und `DESTSHARED`
wurden vor der Inventur initialisiert. Kein Matcher, Input82, Bundle, Edges
oder Kandidatenmodul wurde in diesem Bootstrap importiert. Absolute Locator
und Rohfehler bleiben privat.

Die erste Fassung wurde tatsächlich mit
`REJECTED_CHARACTERIZATION/OBSERVATION_FAILED` abgewiesen und lieferte keine
Modulrecords. Eine getrennte Gegenprobe zeigte: Nach den fünf gewählten Imports
ist `importlib.machinery` noch nicht als Attribut vorhanden, die bereits
geladene Frozen-Bootstrapnamespace enthält jedoch `SourceFileLoader`.
Die eng korrigierte Fassung bindet diese gehaltene Klasse vor der Profilquelle
und prüft danach ihre Identität mit deren `SourceFileLoader`. Sie fügt keinen
zusätzlichen Import hinzu. Nur dieser geänderte Input wurde erneut ausgeführt.
Der erste Fehler bleibt ein Fehlversuch, keine erfolgreiche Kalibrierung.

Die korrigierte Fassung lieferte ausschließlich `CHARACTERIZATION_ONLY`:
85 geordnete Namen, 2 Controls, 24 Builtin-, 16 Frozen-, 41 Source- und
2 Extensionrecords. Beide Quellbindungen waren vor und nach der Ausführung
unverändert. Die Profilquelle hatte 26.234 Rohbytes; dies attestiert keine
bereits ausgeführten Stdlibbytes. Die private Explorerquelle hatte SHA256
`bb71b434aa3b6486604d5cf3720473cc156eaf7be1d98e2b5dc3a7189aca48dc`,
die erste fehlgeschlagene Fassung
`7980de0198f42c1d70d21e1dc83f426b6ba3edab48d665b64662a63e70ac6398`.
Die Profilquelle blieb roh an
`cb6a6e4f8d96370d02dbd8bb0ba9ec63fe8819ceb188e5b9597f90a8a7e14b0d`
gebunden; ihre separate LF-Bindung lautet
`76ca85015d81a743097d665f56c1d626e31e82c704e5b341e39d2d521e153c7a`.
Diese Hashes identifizieren geprüfte Inhalte, keine Installationtrustquelle.
Die Ausgabe war vor Übernahme auf höchstens 1024 Bytes je Zeile und 64 KiB
insgesamt begrenzt; der private Parent verwendete nochmals engere 32-KiB-
Grenzen je stdout/stderr. Ein Abbruch ohne gesicherten Abschluss hätte keinen
Cleanupbeleg erzeugt. Dies war kein Start des geplanten operativen Workers.

Die vollständigen öffentlichen Modulnamen dienen ausschließlich als Input
der portablen Größengegenprobe in
[`test_dgn007_import_profile_binding.py`](../../Tests/Static/test_dgn007_import_profile_binding.py).
Sie sind keine unabhängig ausgewählte operative Sollinventur. Die Probe
verwendet keine tatsächlichen Hostlocator oder ausgeführten Stdlibquellen.
Für jeden Namen werden alle erlaubten Kindformen mit sämtlichen elf
Pflichtfeldern gerechnet und die jeweils kleinste kanonische Darstellung
gewählt. Die festen Frozen-Modul-/Specnamen bleiben erhalten;
Source-/Extensionloadernamen zählen weiterhin mit. Nur die zwei Controls
dürfen einen Nullspec als kleinsten Kontrollfall führen. Pfadtexte,
Locations und Aliasverbände werden bewusst verkleinert. Auch Installationlocator,
ABI und Suchpfade werden verkleinert; alle Installationskeys bleiben vorhanden.
Diese unterapproximierten Formen sind **keine gültigen Nachrichten**.

Die vollständige unveränderte Input82-Metadata einschließlich
`context_sha256` und der vollständige Bindungskontext zählen getrennt mit
allen neun Deskriptoren. Größe null je synthetischem Body ist eine zusätzliche
konservative Verkleinerung; reale Größen erhöhen oder erhalten die Länge.
Die Rechnung verwendet unverändert §5 und zählt den 16-Byte-Header hinzu.

| Untergrenze | ASCII-Bytes |
|---|---:|
| Summe aller 85 vollständigen Modulobjekte | 16.363 |
| Vollständiges Modularray einschließlich 84 Kommata und zwei Klammern | 16.449 |
| Gelockerte vollständige Installation | 342 |
| Je vollständiges neunfaches Deskriptorarray | 1.714 |
| Gemeinsame Metadata und Header, Ordinal 1 / Runner | 21.144 |
| Gemeinsame Metadata und Header, Ordinal 2 / Proxy | 21.130 |
| Gemeinsame Metadata und Header, Ordinal 3 / Harness | 21.108 |

Bereits das Modularray allein überschreitet 16.384 Bytes. Die kleinste
gemeinsame Untergrenze liegt 4.724 Bytes darüber. Deshalb passt jede vollständige
Deklaration dieses charakterisierten Namenumfangs unter der heutigen benannten
JSON-Form nicht in den gemeinsamen Cap. Die Minima der Rechenformen sind
2 Control-, 23 Source- und 60 Frozenformen; diese Zahlen beschreiben die
Verkleinerung und **nicht** die tatsächlichen beobachteten Kinds.
Eine zweite vollständig formgültige synthetische 85er-Deklaration erreicht
bei kleinen Einzelwerten unverändert `REJECTED_REPORTED_PROFILE/METADATA_LIMIT`.
Der Produktionsmatcher, seine 38 bestehenden Gegenproben und alle Caps bleiben
unverändert; lokal bestanden jetzt 40 Methoden unter CPython 3.12.14 ohne SKIP.

Dies schließt nur den vollständigen charakterisierten Umfang unter dieser
Darstellung aus. Es beweist keine Linux-universelle Inventur, Herkunft,
Installationtrust-, Worker-, UsedBytes-, Consumption-, Codec-, SQL- oder
Methodenattestation. Eine kleinere Teilinventur wäre kein Darstellbarkeitsbeleg
der vollständigen Route. Keine Filterung, Kürzung, Capanhebung, Kompression
oder Digestersetzung wird hier freigegeben. Ein anderer vollständig erhaltender
Darstellungsentwurf ist der getrennte nächste Review; danach bleiben konkret
vorab gewählte operative Inventur, volle Größenprüfung, kombinierter Codec,
Parent-/Workerbindung, tatsächliche Imports und unabhängiger Cleanup offen.
DGNI001, die neun Runtimequellen, G13, v1, DEC-068, PR68 und die zurückgestellte
Capture-API bleiben unverändert.

## 10. Vollständig erhaltender Darstellungs- und Digestentwurf

Dieser Abschnitt ist `DESIGNED` auf Basis
`43b6d29012e77ad6de3f3f24259c91fdfde0263e` nach der integrierten Runde PR91
und der dokumentierten Pause. Die ausdrücklich wieder aufgenommene Entwicklung
bearbeitet zunächst nur diesen Entwurf. Keine Produktionsfunktion, Testdatei,
Codecversion oder Workerroute wird hier geändert oder ausgeführt.
Die Größen aus §9 bleiben Belege der bisherigen benannten JSON-Form.

### 10.1 Getrennter Darstellungsweg und vollständige Inhalte

Der Kandidat verwendet feste Tupelpositionen ohne Indextabelle, gemeinsame
Stringtabelle, Kompression oder abgeleitete Ersatzfelder. Jeder vorhandene Wert
bleibt ausdrücklich enthalten, auch wiederholte Pfadtexte und beide vollständigen
neunfachen Deskriptorarrays. Die semantischen DTOs und sämtliche Formregeln aus
§3/§4 bleiben der Maßstab. Absolute Locator werden weder verkürzt noch normalisiert;
leere Texte, erlaubtes `null`, leere Tupel und feste Labeltexte bleiben getrennt.
Namen, Reihenfolgen, Frozenverbände, Controls, Flags und alle Hashes bleiben erhalten.

Die nachfolgend benannte kompakte Form ist eine mögliche neue private Darstellung,
keine neue Interpretation von `DGNI001`. Dessen Magic, Header, sieben exakte
Metadatafelder, `context_sha256`, Rohbytes und Prüfregeln bleiben unverändert.
Eine spätere kombinierte Rahmung und ihr eigener Versionsdiscriminator sind
gesondert zu implementieren und freizugeben. Es gibt keine automatische Erkennung,
Fallbackannahme oder erfolgreiche v1-Dekodierung zusätzlicher Profilfelder.

### 10.2 Geschlossene Positionen und Typen

Alle Positionen beginnen bei null. Ein Record hat exakt die angegebene Arity;
keine Spalte ist optional oder wird bei einem leeren Wert weggelassen. Intern
sind Records und Sequenzen exakte Tupel, Texte exakte `str`, Zahlen exakte `int`;
bool, Subklassen, fremde Getter und freie Iterables sind ausgeschlossen.
Die Darstellung überträgt Tupel als JSON-Arrays, keine freien Objekte.
`Text` hat höchstens 4096 UTF-8-Bytes, enthält weder NUL noch ungepaarte Surrogate.
`Hex(n)` ist ein solcher Text aus genau `n` kleinen Hexzeichen. Nur die unten
benannte `specName`-Position erlaubt `null`; sonst sind fehlende Werte Formfehler.

| Form / Arity | Positionen und vollständige Werte |
|---|---|
| Deskriptor `D` / 5 | `0 ordinal:int(0..8), 1 module:Text, 2 member:Text, 3 size:int(0..131072), 4 sha256:Hex(64)` |
| Inputprojektion `I` / 7 | `0 protocol:Text, 1 commit:Hex(40), 2 raw27_binding:Hex(64), 3 source_profile:Text, 4 nonce:Hex(64), 5 modules:D[9], 6 context_sha256:Hex(64)` |
| Dateifingerprint `F` / 3 | `0 path:Text, 1 size:int(0..33554432), 2 sha256:Hex(64)` |
| Installation `S` / 15 | `0 assumption:Text, 1 platform:Text, 2 implementation:Text, 3 version:int[3], 4 executable:Text, 5 executable_target:Text, 6 prefixes:Text[4], 7 abi:Text, 8 paths:Text[], 9 roots:Text[2], 10 inert_zip:Text, 11 flags:int[6], 12 finders:Text[3], 13 hooks:Text[2], 14 files:F[]` |
| Modul `P` / 11 | `0 name:Text, 1 moduleName:Text, 2 specName:Text/null, 3 origin:Text, 4 file:Text, 5 kind:Text, 6 locations:Text[], 7 loader:Text, 8 loaderName:Text, 9 loaderPath:Text, 10 aliasGroup:Text[]` |
| Workerdeklaration `W` / 6 | `0 ordinal:int(1..3), 1 entry:Text, 2 phase:Text, 3 installation:S, 4 controls:Text[], 5 modules:P[]` |
| Bindungskontext `K` / 8 | `0 commit:Hex(40), 1 raw27_binding:Hex(64), 2 source_profile:Text, 3 nonce:Hex(64), 4 modules:D[9], 5 ordinal:int(1..3), 6 entry:Text, 7 phase:Text` |

Jede variable Sequenz bleibt auf höchstens 256 Elemente begrenzt; `P[]` enthält
mindestens einen Record. `files` hat höchstens zwei Records und insgesamt höchstens
67108864 Dateibytes. Die Version ist exakt `(3,12,patch)` mit `patch` 0..999,
die sechs Flags sind `(1,1,1,1,1,0)`, Finderlabels `BUILTIN,FROZEN,PATH`, Hooklabels
`ZIPIMPORTER,FILEFINDER`. `platform="linux"`, `implementation="cpython"` und
die Annahme aus §2 bleiben feste Werte. Zwei unterschiedliche Roots, vier Prefixe,
Suchpfad-/Fingerprintfolge und die bestehenden Locatorguards bleiben verpflichtend.

`kind` bleibt genau `BUILTIN,FROZEN,SOURCE,EXTENSION,CONTROL`, `loader` genau
`NONE,BUILTIN,FROZEN,SOURCE,EXTENSION`; keine Integercodes ersetzen diese Texte.
Alle Kind-/Spec-/Loader-/Rootbindungen und das PRE_IMPORT-Verbot eigener DGN-Namen
einschließlich `Tests`/`Tests.Contracts` gelten unverändert. Modulrecords sind
eindeutig nach `name` sortiert. Controls sind geordnet, eindeutig und genau an die
CONTROL-Records gebunden. Locations behalten ihre vollständige deklarierte Folge;
es gibt keine zusätzliche Sortierung oder Deduplizierung. Aliasverbände sind
`()` oder eines der festen sortierten Paare aus §3 mit den dortigen Partnerregeln.
Gemischte Frozen-/Sourcepartner bleiben eigenständige Records mit `()`.

Beide `D[9]`-Arrays erscheinen tatsächlich, einmal in `I[5]`, einmal in `K[4]`.
Jede Zeile folgt ordinalweise dem unveränderten Input82-Name-/Membermapping;
alle fünf Felder stimmen zwischen beiden Arrays und mit dem gehaltenen Eingang
überein. Die Summe der neun Größen ist höchstens 1048576. Die neun Bodies selbst
behalten ihre Rawhashes und den bisherigen separaten Bodycap ohne LF-Konversion.
`I[0]="dgn007-import-input/v1"`, beide Quellenprofilwerte bleiben exakt
`dgn007-docker-sql-only/v1`. Die Noncehextexte repräsentieren dieselben gehaltenen
32 Bytes. Ordinal, Einstieg und `PRE_IMPORT` entsprechen der festen Tabelle in §4.

### 10.3 Gemeinsame Rechnung, Bericht und Digestpräbilder

Der feste Darstellungstag `T="compact-binding-design"` ist ein **Entwurfswert**,
keine registrierte oder bereits akzeptierte Codecversion. Er und die Rollentexte
werden vollständig serialisiert. Eine spätere produktive Auswahl braucht einen
expliziten Versions- und Migrationsvertrag; dessen tatsächliche Tags und Header
müssen erneut mitgezählt und geprüft werden, nicht als kostenlose Zusätze gelten.
Der Kandidat hat diese geschlossenen äußeren Formen; die semantischen vier
Berichtsfelder bleiben vollständig enthalten, die äußeren zwei Tags kommen hinzu:

| Form / Arity | Exakte Positionen |
|---|---|
| Gemeinsame Metadata `M` / 5 | `(T,"METADATA",I,W,K)` |
| Bericht `R` / 6 | `(T,"REPORTED",K,S,controls,P[])` |
| Installation-Digestpräbild / 3 | `(T,"compact-installation-declaration",S)` |
| Worker-Digestpräbild / 3 | `(T,"compact-worker-declaration",W)` |
| Kontext-Digestpräbild / 3 | `(T,"compact-profile-binding-context",K)` |

`C` bleibt die kanonische ASCII-JSON-Darstellung aus §5 mit `ensure_ascii=True`,
kompakten Separatoren und `allow_nan=False`. Für **jede** der fünf Formen gilt
separat `16 + len(C(form)) <= 16384`; Tags, Rollentexte und sämtliche wiederholten
Inhalte zählen mit. Der 16-Byte-Header bleibt Budgetbestandteil auch bei den drei
Digestpräbildern, wie bei der heutigen `_canonical`-Regel. SHA256 hasht jeweils
`C(Digestpräbild)` ohne Header und ohne eigenes Digestfeld; die Budgetprüfung
ist davon getrennt. Die Body-, Feld-, Record- und gemeinsamen Ausgabecaps aus §5
bleiben zusätzlich bestehen. Ein kleiner Bericht ersetzt keine passende gemeinsame
Metadata, ein kleiner Wireframe keine passenden Digestpräbilder.

Die `compact-*`-Domains sind ausschließlich Designwerte und vom bisherigen
`installation-declaration/worker-declaration/profile-binding-context`-Weg getrennt.
Gleiche semantische Records können andere neue Digests erhalten; alte Digests
dürfen nicht unter einer neuen Domain wiederverwendet oder als gleich umgedeutet
werden. Positionsfolge, JSON-Typen und Rollentags machen die kanonischen Präbilder
eindeutig unterscheidbar. Dies behauptet keine mathematische Kollisionsfreiheit
von SHA256, keine Signatur und keine Herkunfts- oder Replayattestation.

`I[6]` bleibt dagegen exakt der bisherige Input82-`context_sha256`: Er wird aus
der vollständig zurückgewonnenen **benannten** v1-Metadata ohne ihr eigenes
Digestfeld mit unveränderter Input82-Kanonisierung berechnet. Die Tupelprojektion
ändert weder diesen Digest noch Commit, Raw27-Bindung oder einen Sourcehash.
Beide Descriptorarrays und sämtliche doppelt vorkommenden Kontextwerte werden
vor Vergleich gegen den separat gehaltenen Parent geprüft, nicht zusammengelegt.

### 10.4 Begrenzter Roundtrip und geschlossene Fehlergrenze

Ein späterer Decoder begrenzt den vollständigen Byteeingang vor Slice, Decode,
Parse und Rekonstruktion. Metadata hat höchstens 16368 Bytes plus 16 Headerbytes;
Bericht und Digestpräbilder haben denselben Budgetabzug. Künftige Headerwerte
werden vor Vertrauen in deklarierte Längen auf exakte Form, Gesamtgröße und
vollständiges Ende geprüft. Zusatzpayload und abgeschnittene Eingänge sind Fehler.
Kein heutiger DGNI001-Decoder wird dafür erweitert oder als Fallback verwendet.

Die neue JSON-Grammatik erlaubt nur die obigen Arrayformen, Texte, erlaubtes
`null` und nichtnegative Integer mit höchstens acht Dezimalstellen. Objekte,
bool, Floats, NaN/Infinity und zusätzliche Verschachtelungen sind ausgeschlossen.
Maximale Verschachtelung ist acht Arrayebenen; Arity und Sequenzcaps gelten vor
dem Aufbau größerer DTOs. Ein späterer Parser muss diese Grenzen tatsächlich
während der Aufnahme durchsetzen. UTF-8-Feldgrößen und ASCII-Escapingausdehnung
werden beide geprüft. Die kanonische Gesamtgröße wird abbrechend mitgezählt,
bevor vollständige große String-/JSONpuffer entstehen; kein unbegrenztes
`json.dumps` über noch ungeprüfte verschachtelte Recordmengen.

Für gültige DTOs muss Entpacken nach Packen exakt dieselben Felder, Typen,
Tuplefolgen und Bytes zurückgeben. Für angenommene Wirebytes muss erneutes
kanonisches Packen exakt dieselben Bytes ergeben; alternative Leerraum-, Zahl-
oder Escapedarstellungen werden im neuen Weg geschlossen abgewiesen. Dies
ändert nicht die heutige v1-Akzeptanzregel. Alle Formen werden geprüft, auch
wenn zuvor eine gültige Abweichung festgestellt wurde. Fehlende Werte werden
weder aus dem Soll ergänzt noch aus einer Gleichheit erfunden.

Öffentliche Fehler sind feste Labels ohne Rohtexte, private Locator, Nonce oder
Exceptioncontext. Der Teilclaim bleibt ausschließlich deklarativer Match unter
der ausdrücklich gewählten Annahme, sämtliche Attestationsflags bleiben false.
Consumption und identisches gültiges Replay bleiben bis zum tatsächlichen
Lifecycle offen. Ein Tupel oder Digest attestiert keine erfolgreiche Aufnahme.

### 10.5 Migration, nächste Abnahme und offene Machbarkeit

Der heutige Matcher bleibt auf dem benannten Weg aus §5. Er berechnet vor einem
Match und vor den drei Digests weiterhin dessen Größen. Rückexpansion einer
kompakten Nachricht in diese DTOs umgeht `_canonical` nicht; ein dortiges
`METADATA_LIMIT` wird niemals als Erfolg umgedeutet. Ein zukünftiger kompakter
Prüfweg braucht eigene explizite Versionsauswahl, die obigen Größenregeln und
vollständig getestete semantische Guards. Kein stiller Ersatz der Legacy-API,
kein Abfangen ihres Grenzfehlers als Wahl eines leichteren Prüfers.

Die nächste kleine Abnahme ist die konkrete Bootstrapfixture mit einer vorab
separat gewählten vollständigen Inventur und voller Größenrechnung. Sie darf
reine Berechnungen der geplanten Form verwenden, implementiert aber noch keinen
Decoder oder Worker. Danach folgt der eigene versionierte Codec-/Digestpfad mit
vollständigen Roundtrip- und Gegenproben. Dessen spätere Abnahme muss insbesondere
diese Prüfungen tragen, bevor die tatsächliche Workerroute beginnt:

| Gegenprobe | Erforderlicher Nachweis |
|---|---|
| Alle Formen, Kindfälle, Null-/Leerfälle, Frozenpaare und Locations | Exakter vollständiger Roundtrip ohne Feldverlust, Normalisierung oder implizite Defaults |
| Jedes einzelne Feld verändert, gleiche Werte unter anderer Rolle/Domain | Unterschiedliche kanonische Präbilder; kein Domainaustausch oder wiederverwendeter alter Digest |
| Beide vollständigen Descriptorarrays, geänderte Ordinals/Hashes/Größen/Nonce | Eigene Arrayvorkommen und vollständige Parent-/Kontextbindung; alte Input82-Digests unverändert |
| Falsche Arity/Position/Enum, bool/Subklasse/Foreigngetter, Zusatzpayload | Feste Formfehler vor fremder Operation oder unbeschränkter Rekonstruktion |
| Spätes malformed Feld nach früher gültiger Abweichung | Formfehler bleibt sichtbar; kein frühzeitiger Teilmatch |
| Gemeinsame Form, Bericht und jedes Digestpräbild genau am Cap/Cap+1 | Alle fünf Budgetprüfungen; ASCII-/UTF-8-Ausdehnung, Tags und Header tatsächlich mitgerechnet |
| Kompakter Wire passt, expandierte Legacyform oder neuer Worker-Digest nicht | Kein Erfolg durch alten Matcher oder Auslassen einer Größenprüfung |
| Bestehende DGNI001-/Matchergegenproben und Quellenbindings | Legacyverhalten und Rawbytes bleiben unverändert; keine v1-Umdeutung |

Dieser Tupelentwurf ist ein kleiner deterministischer Kandidat, kein Fitbeleg.
Weniger Keys sparen Darstellungskosten, vollständige echte Locator und die
konkret gewählte Inventur sind jedoch noch nicht eingesetzt. Ein Unterlauf
einer gelockerten Teilrechnung erlaubt weder die operative Auswahl noch einen
erfolgreichen Transfer. Falls die vollständige spätere Sizingfixture bei einer
der fünf Formen überschreitet, folgt ein fester Fehler, keine Filterung,
Digestersetzung, Capanhebung oder spontane neue Darstellung.

Nach diesem Review bleiben separat vorgewählte vollständige operative Sollinventur,
vollständige Größenprüfung, Codec-/Versionsmigration, Worker-/Kanal-/Consumption-
bindung, tatsächliche Imports und unabhängiger Cleanup offen. Die 85 Namen aus §9
werden keine erfolgreiche Baseline. G13, v1, DEC-068, PR68, die geschützte interne
Capture-Arbeit und sämtliche SQL-/Acquisition-/Methodengates bleiben erhalten.
