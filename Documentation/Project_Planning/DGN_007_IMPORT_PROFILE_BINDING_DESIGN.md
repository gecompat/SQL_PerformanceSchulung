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

## 11. Separat ausgewählte vollständige Bootstrapfixture

Auf Repositorybasis `7222dd76e9a4fde6537b90d93cdb9dd170fc17ad` nach PR94
wurde am 2026-10-08 eine vollständige private Deklaration für eine bestehende
Linux-/CPython-3.12.3-Installation ausgewählt und vor der Gegenaufnahme unabhängig
geprüft. Die Auswahl gehört ausschließlich zu dieser konkreten Kontrollfixture;
sie ist keine operative Sollinventur der noch unimplementierten Workerroute.
Die Patchversion ist nicht die jeweilige GitHub-Actions-Patchversion.

### 11.1 Auswahl vor Gegenaufnahme

Die 85 öffentlichen Kandidatennamen aus §9 wurden als exakte sortierte Liste
mit SHA256 `a9e02a88ef624e791c757ab840fb652387871d4b009ed08bf5dca83aa5393d1f`
vorab festgelegt. Die Auswahl übernimmt keine früher beobachteten Kinds,
Specfelder oder Locator. Sämtliche 15 Installationsfelder und alle elf Felder
jedes der 85 Modulrecords wurden aus der separat gewählten Installation,
Builtin-/Frozen-Tabellen, vorhandenen festen Stdlib-/Extensiondateien und den
reviewten Importquellen deklariert. Zwei Dateifingerprints sind vollständig
enthalten. Alle absoluten Locator und vollständigen privaten Tabellen bleiben
außerhalb der versionierten Projektartefakte.

Der Bootstrap behält die fünf direkten Imports aus §8, die exakt zwei Controls,
gebundene Profil-Rohbytes und die Vorinitialisierung von `SOABI`/`DESTSHARED`.
Die fehlende Umgebungsvorgabe `_PYTHON_SYSCONFIGDATA_NAME` und der konkret gewählte
Sysconfig-Datenmodulname sind ausdrückliche Auswahlbedingungen. Die installierte
`sysconfig.py` ist separat gebunden; der Upstream allein ersetzt keine Prüfung
einer distributions- oder buildabhängigen Installation.

Der erste Auswahlinspektor erzeugte eine vollständige Tabelle, deren zwei
`importlib`-Cachealiases fälschlich als Source deklariert waren. Der unabhängige
Form-/Quellenreview wies diese Auswahl **vor** Gegenaufnahme und Größenmessung
ab. `_imp.is_frozen` unter einem Aliasnamen ersetzt nicht die Cachezuweisung
in `importlib.__init__`. Die korrigierte Auswahl verwendet die quellengebundenen
Frozenpartner; `collections.abc` bleibt ein eigenständiger Sourcewrapper und
erhält mit `_collections_abc` keinen erfundenen Frozenverband.
[CPython 3.12.3: Importlib](https://raw.githubusercontent.com/python/cpython/v3.12.3/Lib/importlib/__init__.py),
[Collections-Wrapper](https://raw.githubusercontent.com/python/cpython/v3.12.3/Lib/collections/abc.py),
[Sysconfig](https://raw.githubusercontent.com/python/cpython/v3.12.3/Lib/sysconfig.py),
geprüft am 2026-10-08. Die konkreten installierten Quellenbindungen bleiben
von diesen Upstreamreferenzen getrennt.

Die korrigierte Tabelle wurde exklusiv als neue private Datei materialisiert,
eingefroren und nochmals unabhängig geprüft. Die bestehende Matcher-Formprüfung
akzeptierte vollständige Installation, Inventur, Kontext und Bericht für alle
drei `PRE_IMPORT`-Selectoren. Dessen `_canonical` und Matchfunktion wurden dabei
nicht aufgerufen; Tabellenform ist kein Größen- oder Matchbeleg.

### 11.2 Vollständige Gegencharakterisierung

Erst nach diesem Tabellenreview lief eine neue getrennte Gegencharakterisierung.
Die Kontrollquelle enthält die separat geprüften vollständigen Profil-Rohbytes
und vergleicht ihre begrenzt gelesenen Bytes **vor** `compile`/`exec` mit diesem
gehaltenen Inhalt. Dazu kommt kein sechster Bootstrapimport. Ein nachträglicher
Hashvergleich allein wurde im Vorabreview abgewiesen und vor dem ersten Lauf
korrigiert. Kandidatenbytes, Matcher und Input82 werden im Kontrollbootstrap
nicht importiert oder ausgeführt.

Die tatsächliche Gegenaufnahme enthielt 85 Records: 24 Builtin-, 16 Frozen-,
41 Source-, zwei Extension- und zwei Controlrecords. Sämtliche 15
Installationsfelder, beide Dateifingerprints, Controls und alle elf Felder jedes
geordneten Modulrecords stimmten exakt mit der vorher eingefrorenen Auswahl
überein. Es wurden keine fehlenden Werte ergänzt, keine Pfade normalisiert und
kein abweichender Bericht zur neuen Erwartung gemacht. Alle drei
ausgewählten Frozenverbände und das gemischte Collections-Paar blieben erhalten.

Der private Parent verwendete ein 20-s-Zeitbudget und höchstens 64 KiB gemeinsam
akzeptierte stdout-/stderr-Bytes, begrenzte 1024-Byte-Lesestücke und feste
Ausgabelabels. Der vollständige private Ergebnisrecord blieb separat auf 64 KiB
begrenzt und wurde exklusiv geschrieben. Der tatsächliche Aufruf endete regulär
nach 5,52 s; Quellen und vorherige Auswahl blieben unverändert. Das akzeptierte
Pufferbudget ist kein harter Betriebssystem-Lese- oder Cleanupbeweis. Ein
Timeout-/EOF-/Budgetfehler hätte keinen erfolgreichen Nachweis ergeben.

Der unabhängige Nachreview bestätigte die vollständige Gleichheit. Dies ist eine
Gegencharakterisierung der gewählten Kontrollfixture, keine atomare Aufnahme,
vollständige transitive Resolverclosure oder zukünftige Workerbaseline. Die
Hookprüfung bindet Factorycode und Closurestruktur; sie attestiert keine
ursprüngliche Factoryausführung. Trust-, Runtime-, UsedBytes- und Methodenflags
bleiben false. Operative Parent-/Worker-, Kanal-, Consumption- und Cleanupreceipts
sind weiterhin offen.

| Privater geprüfter Inhalt | SHA256 / Umfang |
|---|---|
| Abgewiesene erste Auswahltabelle | `555765659e4d12eabacfff89ffb22181117cb8ab25720e2e1ab3e3c2266af10d`; 36.472 Bytes |
| Korrigierter Auswahlinspektor | `fefddc7c17a585a0200971a00621a94773291b1ba9da9a5cef6476258656271d` |
| Vorher eingefrorene vollständige Auswahl | `05109f812187e2765b544b277610f5ab2ec6f44f702884e702a859395c0bac21`; 36.409 Bytes |
| Neue vollständige Kontrollquelle | `2b2e1c89c8c7b4aac08da7875d123e2785dc91d155e494d974a625e21c13de7c` |
| Begrenzter Kontrollparent | `7fa67b5993b6d3969ef9f97a78b7f11fde447c0802b51e4d023ca26e7eb051d8` |
| Tatsächliche vollständige Gegenaufnahme | `a3c769dc7aa65d447f78957febb06baaf340a35c1cdfded6152bf03fbc874037`; 24.016 Bytes |
| Gehaltene Profil-Rohbytes | `cb6a6e4f8d96370d02dbd8bb0ba9ec63fe8819ceb188e5b9597f90a8a7e14b0d`; 26.234 Bytes |

Diese Hashes identifizieren die geprüften privaten Inhalte, keine Trustquelle.
Private Dateien oder frühere Chat-Aussagen sind keine Fortsetzungsvoraussetzung:
Eine neue Installation oder Kontrollquelle benötigt eine neue vollständige
Auswahl, deren vorherigen Freeze/Review und eine getrennte Gegenaufnahme.

### 11.3 Separater ursprünglicher Input82-Rahmen

Ein vorab unabhängig geprüfter privater Vorbereitungsschritt übernahm alle 27
Rohmember exakt aus den Gitblobs der festen Repositorybasis. Er erzeugte eine
eigene isolierte temporäre Quellkopie und rief das bestehende `prepare_input`
einschließlich Git-/AST-Vorprüfung auf. Im selben Prozess blieb das ursprüngliche
`PreparedInput` gehalten; der bestehende Encode-/Decode-Roundtrip stimmte exakt
überein. Kandidatenquellen wurden dabei weder importiert noch ausgeführt.

Der exklusiv gespeicherte DGNI001-Rahmen hat SHA256
`ac9de35b5b4e801b71c10c998813ca6f10a69a2956487d83d543fff3c451535d`:
132.986 Bytes aus 16 Header-, 2.133 Metadata- und 130.837 Bodybytes. Die vollständige
27-Member-Rohbindung lautet
`bf0288301cb2429638d94d550ceae53495f385b3c494482d1f6ad0e9f33d4a45`.
Alle neun Deskriptoren und ihre Bodyhashes/Rohbytes entsprechen den festen
Gitblobs. Der unabhängige Nachreview bestätigte Rahmung, kanonische Metadata,
ursprünglichen Kontextdigest, Rohbindung und sämtliche Zuordnungen.

Die eigene temporäre Quellkopie wurde nach vorheriger Prüfung ihrer absoluten
Grenzen regulär entfernt; zwei getrennte Nachkontrollen fanden keine zugehörigen
Tempverzeichnisse. Dieser Cleanup betrifft ausschließlich diese Quellkopie.
Er ersetzt keinen zukünftigen Worker-/Prozessgruppen-Cleanupnachweis.

Der Vorbereitungsprozess ist beendet. Eine spätere Größenrechnung darf den
unveränderten gespeicherten Rahmen begrenzt rekonstruieren, attestiert dadurch
aber weder das fortbestehende ursprüngliche Parentobjekt noch einen tatsächlichen
Workertransfer, Runtimeherkunft oder Trust. Vorbereitung und Nonce werden dafür
nicht erneut erzeugt. Die privaten Rahmenbytes und ihre Nonce bleiben außerhalb
versionierter Artefakte.

### 11.4 Vollständige reine Größenrechnung: negativ

Der getrennte reine Prüfer
[`dgn007_compact_profile_sizing.py`](../../Tests/Tools/dgn007_compact_profile_sizing.py)
prüft zunächst sämtliche DTO- und Kontextformen und zählt dann alle fünf
vollständigen Entwurfsformen aus §10 inkrementell in kanonischem ASCII-JSON.
Jede Größe enthält 16 Headerbytes, Tags und sämtliche zugehörigen tatsächlichen
Formfelder. Die gemeinsame Metadata enthält beide vollständigen Neuner-
Deskriptorarrays; Report und Kontextpräbild enthalten das Kontextarray, Installation
und Workerpräbild keine Deskriptorarrays. Er erzeugt keine Wirebytes, neuen Digests
oder Decoder und verändert den benannten Legacy-Matcher nicht. Eine Überschreitung
liefert `DESIGN_SIZING_OVERFLOW`; sämtliche fünf Größen bleiben sichtbar.
Ungültige Records liefern ausschließlich `REJECTED_DESIGN_SIZING/INVALID_RECORD`.

Nach vollständigem Source-/Testreview und Vorprüfung des privaten Messhelpers
lief genau eine konkrete Rechnung unter CPython 3.12.14 mit `-I -S -B`.
Die vorher eingefrorene vollständige Auswahl blieb unverändert. Der gespeicherte
Originalrahmen aus §11.3 wurde begrenzt rekonstruiert und exakt gegen den bestehenden
Input82-Encode-/Decode-Roundtrip geprüft; keine neue Vorbereitung oder Nonce.
Eine unabhängige benannte Feldreferenz rechnete alle 15 Größen vollständig nach.

| Ordinal / Einstieg | gemeinsame Metadata | Report | Installation-Präbild | Worker-Präbild | Kontext-Präbild |
|---|---:|---:|---:|---:|---:|
| 1 / `run_dgn007_automated_setup` | **17.127** | 15.431 | 719 | 13.893 | 1.678 |
| 2 / `docker_sqlcmd_proxy` | **17.113** | 15.424 | 719 | 13.886 | 1.671 |
| 3 / `run_demo` | **17.091** | 15.413 | 719 | 13.875 | 1.660 |

Alle Werte sind Bytes einschließlich Header. Die gemeinsame Metadata überschreitet
das unveränderte 16.384-Byte-Cap um 743, 729 beziehungsweise 707 Bytes. Die übrigen
vier Formen unterschreiten es. Damit ist der Tupelkandidat aus §10 für diese
vollständige Fixture **nicht darstellbar**. Kein erfolgreicher Codec-/Transfer-
oder operativer Workerbeleg folgt daraus. Ein passender Einzelbericht reicht nicht.
Es wurden weder Felder, Locator, Arrays oder Controls gekürzt noch Caps angehoben.

Der Messhelper hat SHA256
`520ed99058e845d5e68734430722d0c0c25b61af193dcc452fc1c673c1c85fec`;
das ausschließlich skalare Ergebnisaggregat hat SHA256
`83c5b9a227fb0e321c735cfb5e2e504675fb58f3b94101fa0bb5b77ba5b381c7`.
Der vorherige private Helperentwurf wurde wegen einer Listen-/Tupelzuordnung in
der benannten Referenz vor der Messung korrigiert; es gab keinen vorherigen
fehlgeschlagenen Messlauf. Der tatsächliche Aufruf endete nach 1,406 s regulär.
Vor-/Nachpins und unabhängiger Nachreview bleiben an diese konkreten Inhalte gebunden.

34 portable Gegenproben prüfen vollständige Feldpositionen und Schemamengen,
beide Arrays und unveränderten Input82-Kontextdigest, ASCII-/UTF-8-Ausdehnung,
gültige gemeinsame/Report-/Installations-/Workerformen genau am Cap und Cap+1,
mehrfache Überschreitungen, späte Formfehler, Foreigngetter, Aliasgruppen und
feste private Reports. Ein gültiger Kontext kann mit seinen festen Namen und
Hexbreiten das Cap nicht erreichen; dessen maximale gültige Form und getrennte
interne Zählarithmetik ersetzen kein erfundenes Kontext-Capfixture.
34/34 Tests bestanden unter CPython 3.12.14 ohne SKIP. Die unveränderten 27 Input82-
und 40 Matcher-Tests bestanden ebenfalls ohne SKIP.

Als nächster separater Schnitt ist ein expliziter verlustfreier Darstellungs-
Deltaentwurf zu prüfen, der Wiederholungen erhält und alle fünf Formen gemeinsam
betrachtet. Er darf das negative Ergebnis nicht nachträglich zum Fit umdeuten.
Erst eine separat versionierte Darstellung mit vollständiger neuer Größenprüfung
kann den eigenen Codec-/Digestpfad vorbereiten. Legacy, Input82/DGNI001, sämtliche
Inhalte, Caps und die offenen Worker-/Methodengates bleiben erhalten.

## 12. Verlustfreier Stringpoolentwurf

Dieser separate Kandidat ist `DESIGNED` auf Basis
`d0f6cce60181f7afe3cae1b271b4b8fe8fb6f49e` nach PR95. Er beschreibt eine
vollständig erhaltende Darstellung mit einem lokalen Stringpool je Form.
Der negative vollständige Größenbefund aus §11 und der bestehende §10-Sizer
bleiben unverändert. Es gibt hier keine Poolmessung, Codecimplementierung,
Digestberechnung, Migration oder tatsächliche Workeraufnahme.

### 12.1 Lokaler Pool und separate Hülle

Jede Form hat exakt die Hülle `E4=(T,role,pool,payload)` mit vier Positionen.
`T="pooled-binding-design/v1"` und die folgenden Rollen sind ausschließlich
prospektive Designwerte. Ein späterer produktiver Versionspfad muss ausdrücklich
gewählt und getestet werden; weder DGNI001 noch der heutige Matcher erkennen
diese Hülle. Auch der §10-Pfad wird nicht stillschweigend ersetzt.

`pool` ist ein exaktes Tupel mit höchstens **256** exakten Texten. Es enthält
alle und ausschließlich die unterschiedlichen semantischen Texte im jeweiligen
Payload, lexikografisch nach Unicode-Codepoints sortiert. Keine Normalisierung,
Pfadkürzung, Falländerung, Locale-Sortierung oder bevorzugte Sonderposition.
Tag und Rolle sind feste äußere Texte und gehören nicht allein deshalb zum Pool;
ein identischer Text als semantischer Payloadwert gehört trotzdem hinein.

Jede Textposition des Payloads wird durch `r:int(0..len(pool)-1)` ersetzt.
Die feste Position entscheidet zwischen Textreferenz und semantischem Integer;
es gibt kein selbstbeschreibendes Integer-/Enumcodeverfahren. `kind`, `loader`,
Finder-/Hooklabels, Hextexte, Nonce und sämtliche Locator werden als exakte ursprüngliche
Texte zurückgewonnen. `specName=null` bleibt `null`; leerer Text benötigt einen
Poolwert `""`, leere Arrays bleiben Arrays. Keine Defaults oder ausgelassenen Felder.

Alle Formen erhalten eigene vollständige Pools. Keine gemeinsame Installation-
oder Metadata-Dictionary, kein Verweis auf eine andere Nachricht oder ein anderes
Digestpräbild. Über 256 unterschiedliche Texte bedeutet feste Ablehnung; es gibt
keinen Inlinefallback, zweiten Pool, höheren Cap oder automatische andere Darstellung.

### 12.2 Vollständige Positionsschemata

Alle Positionen beginnen bei null. `r` bezeichnet ausschließlich die obige
Textreferenz, `n` einen unveränderten semantischen Integer mit dem jeweiligen
Wertebereich aus §10.2. Intern gelten exakte Tupel, `str`, `int` und ausdrücklich
erlaubtes `None`; bool, Subklassen, freie Iterables und Foreigngetter sind verboten.
Die Darstellung verwendet JSON-Arrays. Die folgende Tabelle ersetzt jede
Textposition einzeln; sie erhält sämtliche ursprünglichen Arity- und Feldbindungen:

| Record / Arity | Exakte Positionen der Poolprojektion |
|---|---|
| `Dp` / 5 | `(ordinal:n,module:r,member:r,size:n,sha256:r)` |
| `Ip` / 7 | `(protocol:r,commit:r,raw27_binding:r,source_profile:r,nonce:r,Dp[9],context_sha256:r)` |
| `Fp` / 3 | `(path:r,size:n,sha256:r)` |
| `Sp` / 15 | `(assumption:r,platform:r,implementation:r,version:n[3],executable:r,executable_target:r,prefixes:r[4],abi:r,paths:r[],roots:r[2],inert_zip:r,flags:n[6],finders:r[3],hooks:r[2],files:Fp[])` |
| `Pp` / 11 | `(name:r,moduleName:r,specName:r/null,origin:r,file:r,kind:r,locations:r[],loader:r,loaderName:r,loaderPath:r,aliasGroup:r[])` |
| `Wp` / 6 | `(ordinal:n,entry:r,phase:r,Sp,controls:r[],modules:Pp[])` |
| `Kp` / 8 | `(commit:r,raw27_binding:r,source_profile:r,nonce:r,Dp[9],ordinal:n,entry:r,phase:r)` |

| Form / Rolle | Exakter Payload / Arity |
|---|---|
| gemeinsame Metadata / `METADATA` | `(Ip,Wp,Kp)` / 3 |
| Bericht / `REPORTED` | `(Kp,Sp,controls:r[],modules:Pp[])` / 4 |
| Installation-Präbild / `pooled-installation-declaration/v1` | `(Sp,)` / 1 |
| Worker-Präbild / `pooled-worker-declaration/v1` | `(Wp,)` / 1 |
| Kontext-Präbild / `pooled-profile-binding-context/v1` | `(Kp,)` / 1 |

Die beiden vollständigen Neuner-Deskriptorarrays erscheinen physisch separat
in `Ip[5]` und `Kp[4]`: Metadata hat zwei, Bericht und Kontextpräbild jeweils
eines, Installation- und Workerpräbild keines. Poolreferenzen teilen Texte,
niemals Record-/Arraystrukturen. Beide Arrays behalten alle fünf Spalten,
Ordinalfolge, Größen und Hashes und werden vollständig gegen den gehaltenen
Input und gegeneinander geprüft. Keine Digestersetzung eines Arrayvorkommens.

Nach Referenzauflösung gelten alle semantischen Guards aus §3/§4/§10.2:
vollständige Name-/Memberbindung, Controls, PRE_IMPORT-Ausschlüsse, Version,
Flags, Roots, Loaderfelder, Specnamen und die festen Frozenverbände. Die
Modulfolge bleibt nach dem zurückgewonnenen Namen sortiert, Controls eindeutig
geordnet, Locations vollständig in ihrer ursprünglichen Folge. Gemischte
Frozen-/Sourcepartner behalten `()`, erlaubte Singletonrecords ihre feste
Namenszuordnung. Nur die Textreferenzen ändern sich, keine Wertebedeutung.

### 12.3 Kanonische Größen und getrennte Digestdomains

`C` ist kanonisches ASCII-JSON mit `ensure_ascii=True`, kompakten Separatoren,
`sort_keys=True` und `allow_nan=False`. Objekte sind hier ausgeschlossen;
kanonische Array-, Text- und Integerdarstellung bleibt dennoch verpflichtend.
Für **jede** vollständige E4-Form gilt separat `16+len(C(E4))<=16384`.
Header, Tag, Rolle, Pool, Referenzen und alle Payloadvorkommen zählen vollständig.
Das gemeinsame Ausgabecap von 64 KiB bleibt zusätzlich bestehen. Poolunterlauf
oder kleiner Wirebericht beweist keinen passenden gemeinsamen Eingang.

Die drei `pooled-*/v1`-Rollen sind neue getrennte Design-Digestdomains; ihre
vollständigen E4-Hüllen wären die späteren Präbilder. SHA256 würde `C(E4)` ohne
Header und eigenes Digestfeld hashen; die Größenrechnung enthält weiterhin
16 Headerbytes. Jede Domain erhält ihren eigenen Pool aus ihrem eigenen Payload.
Alte benannte oder §10-`compact-*`-Digests werden weder übernommen noch als
gleich umgedeutet. Der Tag ist auch in allen drei Präbildern enthalten.

Das erhaltene Input82-`context_sha256` bleibt dagegen exakt dessen bisheriger
benannter v1-Metadata-Digest mit unveränderter Kanonisierung. Commit, Raw27-Bindung,
Nonce, beide Descriptorarrays und neun Rawbodyhashes bleiben unverändert;
keine LF-Konversion. Eindeutige Positionen, Rollen und kanonischer Pool erlauben
eine injektive Darstellungsabbildung gültiger Records. Dies behauptet keine
mathematische SHA256-Kollisionsfreiheit, Signatur oder Herkunftsattestation.

### 12.4 Begrenzte Aufnahme und vollständige Rückgewinnung

Alle bisherigen Caps gelten gleichzeitig: 16 KiB einschließlich Header je Form,
1 MiB Bodygesamtgröße, 128 KiB je Pythonmember, 4096 UTF-8-Bytes je Text,
höchstens 256 Elemente je variabler Sequenz **einschließlich Pool**, acht
Arrayebenen einschließlich E4 und höchstens acht Dezimalstellen je Integer.
Auch Unicode-ASCII-Escaping zählt tatsächlich; UTF-8-Länge allein reicht nicht.

Der Caller wählt die erwartete Version und Rolle ausdrücklich vor der Aufnahme.
Ein späterer Decoder prüft Bytegrenzen, Header und Gesamtende vor Slice und Parse.
Nach begrenztem Parsing vergleicht er den tatsächlichen E4-Tag und die Rolle
gegen diese Auswahl, vor Indexauslegung und Rekonstruktion; kein Dispatch aus
unvertrauten Tags. Schema/Arity,
Tiefe, Typen, Sequenzlängen und Integerbreiten werden während der begrenzten
Aufnahme geprüft, bevor größere DTOs entstehen. Es gibt höchstens 16368 im
JSON repräsentierte Knoten; ein expliziter Aufnahme-/Traversalzähler begrenzt
sie vor Rekonstruktion. Referenzen sind exakte Integer, niemals bool, negativ,
außerhalb des Pools oder in einer nichttextuellen Position.

Der Pool wird vor Verwendung vollständig auf Textform, Reihenfolge und
Duplikatfreiheit geprüft. Die Referenztraversierung führt eine begrenzte
Used-Menge; nach vollständiger Prüfung muss sie genau alle Poolindizes enthalten.
Ungenutzte Werte, fehlende Referenzen oder alternative Pools werden abgewiesen.
Die Rekonstruktion hält gemeinsame unveränderliche Pooltexte per Referenz,
keine wiederholten expandierten String-/Bytekopien oder benannten JSONpuffer.
Sie zählt alle referenzierten Feldvorkommen innerhalb des Knotencaps und prüft
deren Rollen-/Locatorbindungen einzeln. Ein kleiner Pool legitimiert keine
unbegrenzte Expansion; Größen-/Feldprüfung erfolgt vor DTO-Pufferaufnahme.

Für gültige Records gilt `unpack(pack(record))==record` mit exakten Typen,
Werten und Folgen. Angenommene Wirebytes müssen durch kanonisches erneutes
Packen identisch werden; alternative Escapes, Leerraum oder Zahlformen sind
keine zusätzlichen akzeptierten Encodings. Sämtliche Formen werden geprüft;
ein spätes malformed Feld bleibt Fehler trotz früher gültiger Abweichung.
Öffentliche Fehler enthalten ausschließlich feste Labels, keine Locator,
Nonce, Rohtexte oder Exceptionketten. Alle Attestationsflags bleiben false.

### 12.5 Nächste Abnahme und Migration

Nächster separater Implementierungsschnitt ist ein eigener reiner Pool-Sizer:
vollständige Formprüfung, alle fünf Größen und Poolumfänge für alle drei Ordinals,
unabhängige benannte Feldreferenz und sichere Aggregate. Vollständige vorher
gewählte Inventur, beide Arrays und originale Input82-Bindung bleiben erhalten.
Pool- oder Größenüberschreitung ist ein negatives Ergebnis, kein Anlass zu
Filterung, neuen Caps oder Nachwahl. Ein tatsächlicher Fit ist derzeit offen.

Erst danach folgt ein eigener versionsgebundener Codec-/Digestpfad. Er darf
weder expandierte Legacy-`_canonical`-Fehler als Erfolg umdeuten noch durch
Auslassen ihrer Prüfung die heutige API ändern. Die neue Dispatchauswahl und
semantischen Guards werden separat getestet; kein automatischer Fallback.
Verpflichtende Gegenproben für diese späteren Schnitte sind:

| Gegenprobe | Erforderliches Ergebnis |
|---|---|
| Alle S15/P11/I7/K8/D5/F3/W6-Spalten, beide D9-Vorkommen | Exakte vollständige Rückgewinnung; unabhängige Feldreferenz und strukturelle Arrayanzahlen |
| Pool 256/257, Duplikat/ungenutzt/unsortiert, falscher Index/Typ | 256 zulässig bei erfüllten übrigen Guards/Budgets; 257 und Formfehler feste Ablehnung ohne Fallback oder Foreignoperation |
| Null/Leertext/Leerarray, Kinds, Mixedalias/Singleton, Unicode/Locator | Werte und ursprüngliche Folgen unverändert, UTF-8-/ASCII-Bounds tatsächlich geprüft |
| Frühe Abweichung plus spätes malformed, Expansion vieler Referenzen | Alle Formen geprüft; begrenzter Traversal-/DTOpfad, kein Teilmatch |
| Jede E4-Form Cap/Cap+1, Tag-/Rollen-/Headerwechsel | Fünf unabhängige volle Größenprüfungen, keine kostenlose Domain/Version |
| Schema/Position/Domain/Version vertauscht, alte/neue Crossover | Geschlossene Dispatchgrenze, keine Digestwiederverwendung oder v1-Umdeutung |
| Pack/Unpack/Repack und wiederholte Arraywerte | Eindeutige kanonische Bytes; Textsharing ersetzt keine Struktur |

Erst nach vollständigem positivem Größen- und Codecnachweis folgt die tatsächliche
Workerroute samt Kanal-, Consumption-, Replay- und unabhängigem Cleanupbeleg.
Identisches gültiges Replay bleibt heute möglich. Status dieses Abschnitts ist
ausschließlich `DESIGNED/PROJECT_SEMANTIC`; kein Fit-, Trust-, UsedBytes-, Runtime-
oder Methodenclaim. G13, v1, DEC-068, PR68 und die geschützte Capture-Arbeit bleiben
erhalten; die negativen historischen Ergebnisse werden nicht nachträglich geheilt.

## 13. Separater reiner Stringpool-Sizer

Dieser Implementierungsschnitt basiert auf
`2f6e06d433ea962feb7755b7c386d6fd9e19ca5c` nach PR96. Er setzt ausschließlich
die deklarative Größenrechnung aus §12 um. Der Tupel-Negativbefund aus §11,
Input82/DGNI001 und der bestehende Matcher bleiben unverändert. Keine
Codec-/Digestmigration, Workeraufnahme oder Methodenfreigabe folgt daraus.

### 13.1 Vollständige Formen und Aufnahmegrenzen

Der neue reine Prüfer
[`dgn007_pooled_profile_sizing.py`](../../Tests/Tools/dgn007_pooled_profile_sizing.py)
prüft zunächst vollständig Input82-, Worker- und Kontextformen. Er traversiert
dann alle fünf tatsächlichen Payloads direkt aus den geprüften Records, bevor
größere Tupelprojektionen entstehen. Jedes physische Record-/Arrayvorkommen
zählt erneut. Die E4-Hülle einschließlich Tag, Rolle und Poolcontainer sowie
sämtliche Payloadknoten und unterschiedlichen Pooltexte zählen gegen 16.368
Knoten; höchstens acht Arrayebenen einschließlich E4 sind erlaubt.

Erst nach allen Vorprüfungen entstehen je Form ein eigener vollständiger,
sortierter Pool und die positionsgebundenen Referenzen. Textwerte bleiben
gemeinsam gehalten; Integer, erlaubtes `null` und leere Arrays behalten ihre
Semantik. Sämtliche Felder und beide Neunerarrays der gemeinsamen Metadata
werden erhalten. Die fünf vollständigen ASCII-JSON-Größen enthalten jeweils
16 Headerbytes, Tag, Rolle, eigenen Pool und sämtliche Payloadvorkommen.

Reiner Byteoverflow liefert `POOL_DESIGN_SIZING_OVERFLOW` samt allen fünf Größen,
Poolanzahlen und Einzelüberschreitungen. Unterlauf liefert ausschließlich
`POOL_DESIGN_SIZING_ONLY`, keinen Herkunfts- oder Runtimeclaim. Pool257,
Knoten-/Tiefenüberschreitung oder Formfehler führen zu
`REJECTED_POOL_DESIGN_SIZING` mit festen Labels und ohne Formen. Es gibt keinen
Fallback, keine Filterung und keine höheren Caps. Alle Attestationsflags bleiben false.

### 13.2 Portable unabhängige Gegenproben

Die neue
[`Testsuite`](../../Tests/Static/test_dgn007_pooled_profile_sizing.py)
prüft eine unabhängige benannte Feldreferenz und vollständige Rückgewinnung
aller S15/P11/I7/K8/D5/F3/W6-Werte, eigene sortierte vollständige Pools und
physische Deskriptorarrays für alle drei Ordinals. Pool256 ist bei erfüllten
übrigen Guards zulässig, Pool257 wird abgewiesen. Null-/Leertext-/Leerarrayfälle,
Integer gegenüber Textreferenzen, Unicode-/UTF-8-/ASCII-Ausdehnung,
Frozen-/Mixedaliasfälle und ursprüngliche Input82-Rohbytebindung werden geprüft.

Gültige gemeinsame Metadata-, Report-, Installations- und Workerformen erreichen
jeweils exakt Cap und Cap+1. Der gültige feste Kontext bleibt unter dem Cap;
die getrennte interne Zählarithmetik wird nicht als gültige Kontextfixture
ausgegeben. Späte malformed Felder schlagen trotz früher Byte-/Poolüberschreitung
fehl. Foreigngetter, Subklassen, fehlende Records und falsche primitive Formen
werden vor fremden Operationen abgewiesen. Viele wiederholte Locations belegen
den Knotengate vor Projektion; interne Gegenproben prüfen exakt 16.368/16.369
Knoten und acht/neun Arrayebenen. Das sind Sizer- und Generatorprüfungen,
keine Gegenproben eines noch nicht vorhandenen Wiredecoders.

37/37 Methoden bestanden lokal unter CPython 3.12.14 mit `-I -S -B -X utf8`,
ohne SKIP. Zwei zunächst ungültige synthetische Poolfixtures verwendeten nicht
zulässige Installationssuchpfade; sie wurden auf erlaubte Source-Locations
korrigiert. Die Produktionsquelle blieb dabei unverändert. Der unabhängige
vollständige Quell-/Testreview bestätigte beide Freezehashes ohne Befund und
ohne Wiederholung der Tests. Die vollständige private Fixturemessung bleibt
ein separates Gate nach Vorprüfung des konkreten Messhelpers.

| Geprüfte portable Quelle | LF-SHA256 |
|---|---|
| Reiner Pool-Sizer | `0b34a15e0745a7b96bf378d0e6dd5b456a01651b45f965bfdcba6f2831f0b87e` |
| Unabhängige Testsuite | `c7d0ff7a6863749718098fc7a4789fad2d055ef9f8f1c490eeb30b47f46d0985` |

### 13.3 Vollständige reine Fixturemessung

Nach vollständigem Quell-/Testreview und zwei getrennten Vorprüfungen des
konkreten privaten Messhelpers lief genau eine reine Messung unter CPython
3.12.14 mit `-I -S -B -X utf8`. Die vollständige vorgewählte Auswahl aus §11.2
mit 85 Records und zwei Controls sowie der Originalrahmen aus §11.3 blieben
unverändert. Keine neue Bootstrapaufnahme, Vorbereitung oder Nonceerzeugung.
Der begrenzt rekonstruierte Rahmen bestand den bestehenden Input82-Roundtrip;
dies attestiert kein fortbestehendes ursprüngliches Parentobjekt oder Transfer.

Eine unabhängige benannte Feldreferenz erhielt sämtliche Werte und Folgen,
beide Deskriptorarrays und den ursprünglichen Input82-Digest. Sie prüfte die
vollständige Referenzrückgewinnung und ausschließliche Verwendung aller Poolwerte
und rechnete alle fünf Größen für alle drei Ordinals vollständig nach.

| Ordinal / Einstieg | gemeinsame Metadata | Report | Installation-Präbild | Worker-Präbild | Kontext-Präbild |
|---|---:|---:|---:|---:|---:|
| 1 / `run_dgn007_automated_setup` | 9.389 | 9.083 | 638 | 7.408 | 1.746 |
| 2 / `docker_sqlcmd_proxy` | 9.389 | 9.083 | 638 | 7.401 | 1.746 |
| 3 / `run_demo` | 9.389 | 9.083 | 638 | 7.390 | 1.746 |

Alle Werte sind Bytes einschließlich 16 Headerbytes. Die Poolanzahlen sind
bei jedem Ordinal in dieser Formfolge **204/202/17/172/32**. Sämtliche 15 Größen
unterschreiten das unveränderte 16.384-Byte-Cap, alle Poolanzahlen das 256-Cap.
Dies ist ein positiver Darstellbarkeitsnachweis für diese vollständige gewählte
Kontrollfixture und diesen Designkandidaten. Es wurden weder Felder, Locator,
Arrayvorkommen oder Controls gekürzt noch Caps angehoben. Andere Installationen
oder operative Workerbaselines werden damit nicht validiert. Der negative
Tupelbefund aus §11 bleibt erhalten; die heutige API wird nicht umgedeutet.

Der Messhelper hat RAW-SHA256
`a849e7e8b3cd5fd4f7b78c05f6002f7c4de964fcc5012549592072ce9f4f8f82`;
das sichere skalare Ergebnisaggregat hat SHA256
`222444826efec57bc5d309db17df5760efba466c3abe0b74de568b91640672f9`.
Der konkrete Aufruf endete regulär nach 0,722 s. Vor-/Nachpins der sechs
tatsächlich verwendeten RAW-Kontrollquellen und beider Eingaben bestanden.
RAW-Pins bleiben von portablen LF-Provenienzen getrennt; nach Checkout veränderte
EOL-Bytes werden nicht stillschweigend als identische Ausführungsbytes behandelt.
Private Locator, Nonce und Bodies bleiben außerhalb versionierter Artefakte.

Der zusätzliche unabhängige Nachreview bestätigte aus den unveränderten
Eingaben sämtliche 15 Größen, Poolanzahlen, Feldrückgewinnung und ursprüngliche
Inputbindung mit eigener Stdlib-Nachrechnung, ohne Helper-/Sizer-Replay.
Als nächster kleiner Schnitt folgt nach diesem vollständigen Größenbefund
ein eigener ausdrücklich versions-/rollengebundener Codec-/Digestpfad mit
begrenzt kanonischer Aufnahme und Repack. Kombinierte Bodyrahmung, tatsächliche
Parent-/Worker-Anbindung, Consumption-/Replay-/Cleanupbelege und Methodengates
bleiben getrennt offen. Kein Runtime-, Trust-, UsedBytes- oder Methodenclaim;
alle Attestationsflags bleiben false.

## 14. Separater experimenteller Formcodec und Design-Digests

Dieser kleine Schnitt basiert auf
`6e0575ee386ed2cf6666292db1c5468d9fae15a5` nach PR97. Er setzt die
positionsgebundenen E4-Formen aus §12 nach dem positiven vollständigen
Größenbeleg aus §13 um. Der neue Pfad ist ein reiner experimenteller
Formcodec mit getrennten Design-Digests. Produktive Versionsmigration,
kombinierte Bodyrahmung und tatsächliche Parent-/Worker-Anbindung bleiben
eigene spätere Gates. Input82/DGNI001, Legacy-API und die negativen älteren
Größenbefunde werden dadurch nicht verändert.

### 14.1 Explizite Auswahl und eigene Rahmung

Der Caller wählt vor jeder Aufnahme ausdrücklich
`expected_version="pooled-binding-design/v1"` und eine der fünf Rollen aus
§12. Der eigene 16-Byte-Header hat die Form `struct.Struct(">8sII")`:
Magic `b"DGNP001\0"`, Rollencode und vollständige kanonische JSON-Länge.
Rollencodes 1 bis 5 entsprechen genau der Tabellenfolge aus §12.2.
Der Header zählt gegen 16.384 Bytes; die JSON-Nutzlast hat höchstens
16.368 Bytes. Es gibt keinen zusätzlichen Rawbodyteil. Dieser experimentelle
Discriminator aktiviert keine produktive Workerroute oder Migration.

Der Decoder nimmt ausschließlich exakte `bytes` an. Bytegrenze, Magic,
Rollencode, explizite Auswahl, Längenfeld und Gesamtende werden vor Slice
und Parse geprüft. Nach begrenztem Parsing werden tatsächlicher E4-Tag und
Rolle gegen Caller und Header geprüft, bevor Referenzen interpretiert werden.
Kein Dispatch aus fremdem Tag, Legacy-Fallback oder Versionsdefault.

### 14.2 Begrenzte Aufnahme und vollständige Semantik

Ein eigener ASCII-JSON-Arrayparser zählt höchstens 16.368 repräsentierte
Knoten vor deren Aufnahme. Arraytiefe einschließlich E4 bleibt höchstens
acht, jede Sequenz einschließlich Pool höchstens 256, Integer exakt
0 bis 99.999.999 und höchstens acht Dezimalstellen. Objekte, bool, floats,
NaN und fremde Containerformen sind ausgeschlossen. Textaufnahme begrenzt
UTF-8 auf 4.096 Bytes, prüft Escapeformen und vollständige Surrogatpaare
und lehnt NUL sowie isolierte Surrogate ab. Die kanonische ASCII-Neuausgabe
muss exakt denselben Bytes entsprechen; alternative Escapes, Zahlformen
oder Leerraum werden dadurch nicht als weiteres Encoding akzeptiert.

Der gesamte Pool wird vor Referenzverwendung auf exakte Texte, Ordnung,
Eindeutigkeit und Bounds geprüft. Nur Textpositionen werden aufgelöst;
semantische Integer und das allein erlaubte `specName=null` behalten ihre
Typen. Nach vollständiger Traversierung müssen sämtliche und ausschließlich
alle Poolindizes verwendet sein. Die Rekonstruktion hält die unveränderlichen
Pooltexte gemeinsam; sie erzeugt keine wiederholten expandierten JSONpuffer.
Arity, Positionen und sämtliche ursprünglichen semantischen Guards gelten
für alle S15/P11/I7/K8/D5/F3/W6-Felder und beide physisch vorhandenen D9-Arrays.

Caller-`prepared` und `expected_worker` sind separat gehaltene Vergleichswerte,
keine Quelle für ausgelassene empfangene Felder. Erst die vollständig gültigen
empfangenen Werte werden verglichen. Ein später Formfehler dominiert eine
frühe gültige Abweichung; es gibt keinen Teilmatch. Beide Deskriptorarrays,
Original-Input82-SHA, Commit, Raw27-Bindung, Nonce und neun Rawbodyhashes bleiben
vollständig erhalten und geprüft, ohne LF-Konversion.

Die einzeln dekodierten Installation- und Workerformen enthalten keinen
Kontext oder D9-Nachweis und begründen keine Nonce-, Parent- oder
Gesamtprofilbindung. Ein vollständiger deklarativer Profilvergleich prüft
separat alle fünf tatsächlichen empfangenen Rollen. Der Singleformdecoder prüft
seine eine empfangene Rolle vollständig; er behauptet keinen vollständigen
Fünf-Formen-Match. Vor erfolgreicher Encoder-Einzelframeausgabe oder Digestberechnung
müssen bereits alle fünf vollständigen Formen sämtliche Semantik-, Pool-,
Knoten-, Tiefen- und Bytegates bestehen; eine kleine einzelne Form heilt
keine zu große gemeinsame Metadata. Die Summe aller fünf Formen einschließlich
aller fünf Header muss vor Encoder-Einzelframeausgabe, Formsetausgabe oder Digestberechnung
zusätzlich das unveränderte 64-KiB-Ausgabecap einhalten.

### 14.3 Getrennte Digestdomains und Abnahme

Die getrennten APIs des neuen
[`dgn007_pooled_profile_codec.py`](../../Tests/Tools/dgn007_pooled_profile_codec.py)
verlangen jeweils die explizite Version:

| API | Ergebnis und Grenze |
|---|---|
| `encode_declared_form(prepared, worker, *, expected_version, role)` | exakte Framebytes nach allen fünf erzeugten Formgates |
| `encode_declared_formset(prepared, worker, *, expected_version)` | fünf Frames in fester Rollenfolge nach gemeinsamem Ausgabegate |
| `decode_declared_form(frame, *, expected_version, expected_role, prepared, expected_worker)` | eigener frozen `DecodedForm` mit vollständig zurückgewonnenem Payload; S/W ohne Kontextmatch |
| `digest_declared_profile(prepared, worker, *, expected_version)` | `CHECKED_DECLARED_FORMSET` mit drei eigenen Design-Digests nach allen fünf erzeugten Formgates |
| `match_declared_formset(frames, prepared, expected_worker, *, expected_version)` | `MATCHED_DECLARED_FORMSET` mit drei eigenen Digests erst nach allen fünf tatsächlich empfangenen Formgates und vollständigem Vergleich; sonst feste Ablehnung |

Payloadrecords haben kein inhaltliches `repr`. Erfolgreiche Reports bleiben
`PROJECT_SEMANTIC` und sämtliche Attestationsflags false. Encoder und
Einzeldecoder verwenden bei Ablehnung feste `CodecRejected`-Labels ohne
Exceptionkette; Formsetvergleich liefert `REJECTED_DECLARED_FORMSET` ohne Digests.

Erst nach sämtlichen fünf Gates entstehen drei eigene SHA256-Design-Digests
über die vollständigen kanonischen E4-Hüllen ohne Header: Installation,
Worker und Profilbindungskontext verwenden jeweils ihre eigene `pooled-*/v1`-
Rolle und ihren eigenen vollständigen Pool. Alte benannte oder `compact-*`-
Digests werden nicht wiederverwendet. Der bestehende benannte Input82-Digest
bleibt unverändert. Dies attestiert weder Herkunft noch Kollisionsfreiheit.

Die Abnahme verlangt vollständige Roundtrips aller Rollen und drei Ordinals,
unabhängige Feldreferenz und Digestrechnung sowie Gegenproben für Header-,
Rollen-, Versions-, Domain- und Legacy-Crossover. Bounds, Poolfehler,
Null-/Leer-/Unicodefälle, falsche Positionstypen, späte malformed Felder,
beide D9-Vorkommen und ursprüngliche Rawbytebindung werden separat geprüft.
Ein tatsächlicher vollständiger Codecbeleg derselben privaten Kontrollfixture
bleibt bis zum Quell-/Testreview und zur Vorprüfung eines konkreten begrenzten
Helpers offen. Öffentliche Fehler enthalten ausschließlich feste Labels,
keine Payloads, Locator, Nonce oder Exceptionketten. Sämtliche Attestationsflags
bleiben false. Keine SQL-, Trust-, UsedBytes-, Replay-, Cleanup- oder
Methodenfreigabe folgt aus einem deklarativen Roundtrip.

### 14.4 Portable Gegenproben und getrennte Grenzen

Die neue
[`Testsuite`](../../Tests/Static/test_dgn007_pooled_profile_codec.py)
bestand lokal 41/41 Methoden ohne SKIP unter CPython 3.12.14 mit
`-I -S -B -X utf8` in 0,239 s. Eine unabhängige benannte Feldreferenz prüft
sämtliche Rollen und drei Ordinals, originale Input82-Bindung, beide D9-Arrays,
vollständige DTO-Werte, getrennte Digestpräbilder und kanonischen Repack.
Gültige Metadata-, Report-, Installations- und Workerrahmen erreichen jeweils
exakt 16.384 Bytes und werden aufgenommen; 16.385 Bytes werden vor Parse
abgewiesen. Der gültige feste Kontext bleibt unter dem Cap. Seine getrennte
interne Header-/Integerarithmetik ist kein gültiges Kontext-Capfixture.

Pool256 ist mit erlaubten Source-Locations zulässig; Pool257, Duplikate,
Unordnung, ungenutzte Werte und ungültige Indizes werden abgewiesen.
Null, Leertext, leere Folgen, Integer gegenüber Textreferenzen, Unicode,
Surrogatpaare und UTF-8-Grenzen bleiben positionsgebunden. Ein wiederholter
Locationtext wird unveränderlich geteilt; alle Arrayvorkommen bleiben erhalten.
Foreigngetter, Subklassen, uninitialisierte Records und verfälschte Callerwerte
werden vor fremden Operationen abgewiesen. Späte malformed Empfangsfelder
dominieren frühe gültige Abweichungen. Alte Magic-/Domain-/Versionsformen
erhalten keinen Fallback.

Knoten-, Tiefen- und gemeinsame 64-KiB-Gegenproben prüfen die interne begrenzte
Aufnahme beziehungsweise Zählarithmetik zusätzlich. Kontrollierte Zähler und
synthetische Kosteneingaben werden ausdrücklich nicht als gültige maximale
E4-Feldfixtures ausgegeben. Die tatsächliche Frame-/Längen-/Gesamtgrenze wird
auch gegen einen Parsermock vor dessen Aufruf geprüft.

Drei zunächst falsche Fixture-Erwartungen wurden nach tatsächlichen
Fehlerläufen korrigiert: Digestersatz hinterließ einen ungenutzten Poolwert,
fehlende Surrogatfortsetzung ergibt `JSON_FORM`, und die interne feste
Kontextarithmetik ergibt bei Cap `INTEGER_LIMIT`. Diese Korrekturen ersetzen
keine berichteten früheren Fehler durch nachträglichen Erfolg. Der separate
Singledecoder vergleicht seinen tatsächlichen Frame gegen semantisch gültige
Callerwerte; er fordert keine Bytefreigabe vier nicht empfangener Formen.
Alle fünf erzeugten Formen und das gemeinsame Ausgabegate bleiben dagegen
vor Encoder-Einzelframeausgabe oder Digests zwingend, alle fünf tatsächlichen
Empfangsformen vor dem vollständigen Formsetmatch.

| Geprüfte portable Quelle | LF-SHA256 |
|---|---|
| Experimenteller Formcodec | `3b351a196239247d34b198067a07a178fc3b74dd8bfc68488dd194ccbe9c7751` |
| Unabhängige Testsuite | `9752af10ce0103ad7e247baeaf72a0cc90d87f2583cc2ca67a8cee235aef104e` |

Der private vollständige Codecbeleg erfolgte erst nach unabhängigem Quell-/
Testreview und Vorprüfung des konkreten Helpers; §14.5 dokumentiert diesen
getrennten Nachweis. Keine neue Aufnahme, Nonce oder operative Baseline wird
durch die synthetischen Gegenproben gerechtfertigt.

### 14.5 Vollständiger reiner Codecbeleg der Originalfixture

Nach vollständigem unabhängigem Quell-/Testreview und zwei getrennten
Vorprüfungen des konkreten Helpers lief genau eine neue reine Codecprüfung
unter CPython 3.12.14 mit `-I -S -B -X utf8`. Sie endete regulär nach 1,024 s
mit Exitcode 0. Die vollständige separat vorgewählte Auswahl mit 85 Records
und zwei Controls aus §11.2 sowie der Originalrahmen aus §11.3 blieben
unverändert. Keine erneute Bootstrapaufnahme, Vorbereitung, Nonce oder
Ausführung eines früheren Messhelpers. Die begrenzte Rekonstruktion bestand
den bestehenden Input82-Roundtrip; ursprünglicher Parentmemory oder Transfer
werden damit nicht attestiert.

Die unabhängige benannte Feldreferenz erhielt sämtliche Felder, Typen und Folgen.
Alle fünf tatsächlichen Framebytes je Ordinal entsprachen den unabhängig
erzeugten E4-Referenzen. Die tatsächlichen Decodergebnisse wurden vollständig
gegen eigene DTO-/Feldreferenzen geprüft; beide D9-Arrays, ursprünglicher
Input82-Digest, neun Rawbodyhashes und 130.837 Bodybytes blieben erhalten.
Kanonischer Repack und vollständige Verwendung sämtlicher Poolwerte bestanden.
Alle drei eigenen Digestdomains je Ordinal stimmten mit der unabhängigen
Stdlib-Rechnung überein; Encoder-, Digest- und tatsächliche Formsetmatch-APIs
bestanden sämtliche fünf Formgates und das gemeinsame Ausgabegate.

| Ordinal | Fünf Framegrößen einschließlich aller Header | Gesamtausgabe |
|---|---|---:|
| 1 | 9.389 / 9.083 / 638 / 7.408 / 1.746 | 28.264 |
| 2 | 9.389 / 9.083 / 638 / 7.401 / 1.746 | 28.257 |
| 3 | 9.389 / 9.083 / 638 / 7.390 / 1.746 | 28.246 |

Alle Werte sind Bytes. Die Rollenfolge entspricht §12.2, die Poolanzahlen
sind bei allen Ordinals 204/202/17/172/32. Alle 15 Frames bleiben unter
16.384 Bytes, jedes vollständige Set unter 65.536 Bytes. Dies ist ein reiner
deklarativer Codecbeleg dieser vollständigen Kontrollfixture, keine operative
Sollinventur oder tatsächliche Workerbeobachtung.

Der konkrete Helper hat RAW-SHA256
`3d340c0a579fcc172f7446c400423df1506a2d881a78fd236b9497c823592aac`
und 12.472 Bytes. Das sichere Ergebnisaggregat hat SHA256
`b9c28069cb9447830e46a5bf6918e4c89fd347eb5b598e55089ff34444c0366c`.
Vor-/Nachpins aller sieben tatsächlich importierten RAW-Kontrollquellen und
beider Originaleingaben bestanden. Der bestehende Pool-Sizer hat nach Checkout
RAW-SHA256 `5671b043e5cca2eae482151ee2bf8b7a964e9ee580da750c45c46494d0f8d2ef`;
sein portabler LF-Hash aus §13.2 bleibt unverändert. RAW-Ausführungsbytes werden
nicht mit portablen LF-Provenienzen gleichgesetzt. Private Locator, Nonce,
Inventurdetails und Bodies bleiben außerhalb versionierter Artefakte.

Der zusätzliche unabhängige Nachreview rechnete aus den unveränderten Eingaben
mit eigener Stdlib-Referenz sämtliche 15 Frames, neun Domain-Digests und drei
Formset-SHA identisch nach. Vollständige Positionen, Rückgewinnung, Usedsets,
D9-Vorkommen und ursprüngliche Rawbytebindung bestanden; alle Pins unverändert.
Das sichere Aggregat hat 2.515 Bytes und ausschließlich die geprüfte Feldmenge.
Kein Helper-/Codec-/Sizer-/Prepare-/Counter-Replay. Diese Nachrechnung bestätigt
die erwarteten Bytes und Digests, ersetzt keine zweite tatsächliche Codecaufnahme.
Nächster kleiner Schnitt ist ein eigener reiner experimenteller kombinierter Metadata-/
Rawbody-Frameprototyp. Er behält die neun Originalbodies, deren Caps und sämtliche
Bindungen und aktiviert keine produktive Workerroute. Operative Baseline,
Versionsmigration, Parent-/Worker-Anbindung, tatsächliche Quellenauflösung,
Consumption-/Replay-/Cleanup- und Methodengates bleiben getrennt offen.
Alle Attestationsflags einschließlich vollständiger Runtimeinventur und
ursprünglicher Parentmemory bleiben false; keine Methoden- oder Runtimefreigabe.

## 15. Separater experimenteller kombinierter Eingangsrahmen

Dieser reine Prototyp basiert auf `0cdcdbd07a9c2cf9d1e71c2f481948546169b9c3`
nach PR 98. Er ergänzt den Formcodec aus §14 um die neun unveränderten
Rawbodies. Er führt keine Quellenbeobachtung, Vorbereitung, Nonceerzeugung,
Prozess-, Worker-, Import- oder SQL-Ausführung durch.

### 15.1 Explizites Format und gleichzeitige Grenzen

Der Caller wählt ausdrücklich
`expected_format="pooled-combined-input-design/v1"`. Es gibt keinen Default
oder Legacy-Fallback. Der eigene Header `struct.Struct(">8sII")` enthält
Magic `b"DGNC001\0"`, Metadata-JSON-Länge und Rawbodylänge. Die Metadata
ist genau die unveränderte kanonische E4-Hülle aus §12 mit deren Tag
`pooled-binding-design/v1` und fester Rolle `METADATA`. Die neun Bodies
folgen in der unveränderten Deskriptorreihenfolge.

Die gesamten Metadata einschließlich 16-Byte-Header dürfen höchstens
16.384 Bytes umfassen. Gleichzeitig gelten 131.072 Bytes je Body,
1.048.576 Bytes für sämtliche Bodies und 1.064.960 Bytes für den Gesamtframe.
Der Encoder muss vor Freigabe weiterhin alle fünf vollständigen Formgates
aus §14 einschließlich deren gemeinsamen 65.536-Byte-Ausgabegate erfüllen.
Dieses Ausgabegate beschreibt ausschließlich die fünf Metadataformen;
Rawbodies sind begrenzter interner Eingang und Bestandteil der kontrollseitigen
Framebytes, keine öffentliche Diagnose- oder Konsolenausgabe.

### 15.2 Vollständige Aufnahme vor Vergleich

Der Decoder akzeptiert ausschließlich exakte `bytes`. Er prüft Formatwahl,
Gesamtgrenze, Header, sämtliche Längen und exaktes Gesamtende vor Slice und
Parse. Anschließend prüft der bestehende private Formcodec seine tatsächlich
empfangene METADATA vollständig: E4, Pool, Positionen, sämtliche Records,
beide physischen D9 und den ursprünglichen benannten Input82-Digest.
Die Aufnahme verwendet dessen `_decode` mit fester Rolle, nicht dessen
bereits gegen Callerwerte vergleichenden öffentlichen Singledecoder.

Vor jeder Bodyaufnahme müssen alle neun Größen zusammen exakt der
deklarierten Rawbodylänge entsprechen und sämtliche Einzel-/Gesamtcaps
erfüllen. Danach werden alle tatsächlich empfangenen neun Bodyhashes und
Offsets geprüft. Erst nach vollständiger eigener Metadata- und Bodyprüfung
erfolgt der Vergleich mit separat gehaltenen semantisch gültigen Callerwerten.
Eine frühe gültige Callerabweichung darf ein späteres Bodyproblem nicht
verdecken. Kein Ergebnis enthält aus Callerwerten ergänzte Empfangsfelder.

Erfolg liefert einen eigenen privaten frozen Record ohne Inhalts-`repr` mit
vollständig zurückgewonnenen Metadata und tatsächlich empfangenen Rawbytes.
Ablehnung erfolgt atomar über feste technische Labels ohne Exceptionkette
oder Payloadausgabe. Sämtliche Attestationsflags bleiben false; ein deklarierter
Kontextmatch attestiert keine Herkunft, tatsächliche Verwendung oder Replayfreiheit.

### 15.3 Abnahme und Folgegrenzen

Die getrennte
[`Komponente`](../../Tests/Tools/dgn007_pooled_combined_input.py)
besitzt ausschließlich die folgenden explizit ausgewählten APIs:

| API | Ergebnis und Grenze |
|---|---|
| `encode_combined_input(prepared, worker, *, expected_format)` | tatsächliche kontrollseitige Framebytes nach sämtlichen fünf Formgates |
| `decode_combined_input(frame, *, expected_format, prepared, expected_worker)` | eigener `DecodedCombinedInput` mit empfangener Metadata, Worker, Kontext und neun `ReceivedSource`-Records erst nach vollständiger Prüfung |

Die getrennte
[`Testsuite`](../../Tests/Static/test_dgn007_pooled_combined_input.py)
prüft drei Ordinals, unabhängige Frame-/Feldreferenzen,
Originalbyteerhaltung einschließlich CRLF, Header-/Längenfehler, beide D9,
Mappings, Nonce-/Kontextwechsel, Einzel-/Gesamtcaps und späte Bodyfehler trotz
früherer gültiger Abweichung. Die Grenzfälle trennen gültige Feldfixtures von
internen Zählergegenproben. Kein Kandidatenbody wird importiert oder ausgeführt.

Ein vollständiger neuer Originalfixturebeleg folgt erst nach unabhängigem
Quell-/Testreview und Vorprüfung eines konkreten begrenzten privaten Helpers.
Frühere Helpers werden nicht wiederholt. Operative Versionsauswahl, tatsächlich
gewählte Workerbaseline, Parent-/Worker-Anbindung, Quellenauflösung, Consumption,
Replay und unabhängiger Cleanup bleiben getrennte nachfolgende Gates.

### 15.4 Portable Gegenproben und unabhängiger Review

Die neue Testsuite bestand im ersten tatsächlichen Lauf unter CPython 3.12.14
mit `-I -S -B -X utf8` alle 34/34 Methoden ohne SKIP in 0,122 s. Es gab keine
nachträgliche Code- oder Fixturekorrektur eines Fehlerlaufs. Ein unabhängiger
Quell-/Testreview las die vollständigen beiden Dateien einschließlich aller
34 Gegenproben ohne eigenen Testlauf und bestätigte denselben Freeze.

Drei Ordinals erhalten vollständige unabhängige Frame- und Feldreferenzen.
Beide physisch getrennten D9, der ursprüngliche benannte Input82-Digest,
neun Rawhashes und sämtliche tatsächlich zurückgegebenen Bytes bleiben erhalten.
CRLF, Leerbytes, NUL und Nicht-UTF-8-Bytes sind opake Bodywerte. Der Prototyp
interpretiert oder importiert diese Bodies nicht. Gültige abweichende Nonce-,
Commit-, Raw27- oder Ordinalwerte ergeben ausschließlich einen deklarativen
Mismatch; späte malformed Metadata oder Bodyhashfehler dominieren solche
frühen gültigen Abweichungen und treten vor jeder Calleraufnahme auf.

Gültige Metadata erreichen exakt 16.384 Bytes einschließlich Header,
gültige einzelne Bodies 131.072 Bytes und die Bodygesamtheit 1.048.576 Bytes.
Ein gültiger gemeinsamer Frame erreicht gleichzeitig 1.064.960 Bytes und wird
vollständig aufgenommen; Cap+1 wird vor dem Parser abgewiesen. Die separate
64-KiB-Gegenprobe ist ausdrücklich interne `_size`-Zählarithmetik, keine
behauptete maximale gültige Fünf-Formen-Fixture. Sämtliche tatsächlichen
Encoderformen behalten ihr gemeinsames Gate; ein Decoder behauptet nur die
eigene empfangene METADATA und deren neun Bodies.

| Geprüfte portable Quelle | LF-SHA256 |
|---|---|
| Experimenteller kombinierter Eingang | `8db9291088d21e81f8eaf7d63740ec6db3a6f24e621dfb380ce3775aba0b871e` |
| Unabhängige Testsuite | `b2bae852772830e02d7448f8dcf3eb674806d5a9c5ee0b97bbab68fb555a419d` |

Alle Ergebnisse sind frozen und ohne Inhalts-`repr`; Fehler enthalten feste
Labels ohne Cause oder Context. Identische gültige Eingaben bleiben wiederholbar.
Keine Herkunfts-, Worker-, Trust-, Consumption-, Replay-, Cleanup- oder
Methodenattestation folgt daraus. §15.5 beschreibt den anschließend getrennt
ausgeführten privaten Originalfixturebeleg.

### 15.5 Vollständiger reiner Combined-Beleg der Originalfixture

Nach dem vollständigen unabhängigen Quell-/Testreview und zwei getrennten
Vorprüfungen des konkreten neuen Helpers lief genau eine neue reine
Combined-Prüfung unter CPython 3.12.14 mit `-I -S -B -X utf8`.
Sie endete regulär nach 0,223 s mit Exitcode 0. Die vollständige vorgewählte
Originalauswahl mit 85 Records und zwei Controls sowie der Input82-Originalrahmen
aus §11 blieben unverändert. Keine frühere Messung wurde wiederholt, keine
neue Aufnahme, Vorbereitung, Nonce oder Worker-/Importausführung durchgeführt.

Alle drei tatsächlich erzeugten Frames entsprachen vollständigen unabhängigen
benannten Referenzen. Tatsächlich empfangene Inputfelder, Worker, Kontext,
beide physische D9-Arrays, ursprünglicher Input82-Digest und sämtliche neun
Rawbytes wurden vollständig verglichen. Sämtliche Poolwerte wurden verwendet,
vollständige Feldrückgewinnung und kanonischer Repack allein aus den tatsächlichen
Empfangsrecords bestanden. Ursprünglicher Parentmemory oder Transfer werden
durch die begrenzte Originalrahmen-Rekonstruktion nicht attestiert.

| Ordinal | Metadata einschließlich Header | Rawbodybytes | Gesamtframe | Fünf Metadataausgaben |
|---|---:|---:|---:|---:|
| 1 | 9.389 | 130.837 | 140.226 | 28.264 |
| 2 | 9.389 | 130.837 | 140.226 | 28.257 |
| 3 | 9.389 | 130.837 | 140.226 | 28.246 |

Alle Werte sind Bytes; Poolanzahl jeweils 204. Die vier gleichzeitigen
Eingangsgrenzen bleiben erhalten. Die letzte Spalte ist ausschließlich die
getrennte Fünf-Formen-Metadataausgabe; der größere interne Bodyframe ist keine
öffentliche Konsolenausgabe und kein Beleg für eine 64-KiB-Workerkanalübertragung.

Der neue private Helper hat RAW-SHA256
`5b57c2f5a014b68f2b89cc0f17f693dd4c15715193b9d92ac8df1e9a55cee29c`
und 12.744 Bytes. Das sichere Ergebnisaggregat hat SHA256
`8b427102154206eb625ed79a6356da6c19f93f4ddd0aa963acbe94b051566634`.
Alle acht tatsächlich importierten RAW-Kontrollquellen sowie beide Originaleingaben
bestanden Vor-/Nachpins. Der bestehende Formcodec hat nach Checkout RAW-SHA256
`88f6b55c6c7e1e8e99c731a519f65d0edf96631b1a8b562d27262ac052a7c1f9`;
sein portabler LF-Hash aus §14 bleibt unverändert. RAW-Ausführungsbytes werden
nicht mit portablen LF-Provenienzen gleichgesetzt. Private Locator, Nonce,
Inventurdetails und Bodies bleiben außerhalb versionierter Artefakte.

Der zusätzliche unabhängige Nachreview rechnete mit ausschließlich eigener
Stdlib-Referenz aus den unveränderten Originaleingaben sämtliche fünf E4-Formen
je Ordinal, alle vollständigen Felder, Usedsets, beide D9 und neun Rawhashes nach.
Die drei erwarteten Combined-Frames, deren Größen und SHA256 sowie sämtliche
Metadataausgabesummen stimmen exakt. Das sichere Aggregat hat 1.917 Bytes und
entspricht vollständig der erwarteten Feldmenge ohne Extras. Alle acht Quellen-,
Helper- und Inputpins bleiben unverändert. Kein Helper-/Combined-/Codec-/Sizer-/
Prepare-/Counter-Import oder Replay; diese Nachrechnung bestätigt erwartete
vollständige Bytes und Felder, keine zweite tatsächliche Decoderaufnahme.

Sämtliche Attestationsflags einschließlich vollständiger Runtimeinventur und
ursprünglicher Parentmemory bleiben false. Der Beleg betrifft ausschließlich
diese unveränderte vollständige Kontrollfixture. Operative Versionsauswahl,
frische tatsächlich gewählte Workerbaseline, Parent-/Worker-Anbindung,
Quellenauflösung, Consumption, Replay und unabhängiger Cleanup bleiben offen.

## 16. Konkrete operative Bootstrap- und Kanalreihenfolge

Dieser ergänzende Vertrag ist `DESIGNED` im Scope `PROJECT_SEMANTIC` auf Basis
`37b89ac523cae619b120a09db6ac0711bd5f0093` nach PR99. Er wählt die nächste
begrenzte Offlinefolge, führt sie aber nicht aus. Die Belege aus §11–15 bleiben
Belege ihrer konkreten Kontrollfixture. Die dort charakterisierten 85 Namen
werden weder als operative Baseline übernommen noch als vollständige
Importclosure einer neuen Bootstrapquelle ausgegeben.

### 16.1 Vorab gewählte Quelle, Installation und Darstellung

Der Parent wählt ausdrücklich `pooled-combined-input-design/v1` aus §15 und
`pooled-binding-design/v1` mit den festen Rollen aus §12. Es gibt keinen
Legacy-Fallback oder Dispatch anhand eines untrusted Tags. DGNC-/DGNP-Header,
E4-Felder, beide vollständigen D9 und ursprünglicher Input82-Digest bleiben
unverändert. Die folgende Kanalsteuerung ist ein gesonderter prospektiver
Vertrag; sie ist noch keine implementierte produktive Versionsmigration.

Vor jedem späteren Start stehen die absoluten Linux-CPython-3.12-Executable-
und Scriptlocator, Patch-/Buildauswahl, Kontrollquellenbytes und vollständigen
S15/P11-Erwartungen separat fest. Der geplante Scriptlocator aus §8 bleibt
**NICHT VORHANDEN**. Seine eigene Importinventur ist neu zu begründen, weil
Inlineempfang und die Kontrollquellenführung Teil dieser konkreten Quelle sind.
Parentinventur und erfolgreiche Istaufnahme ersetzen diese Auswahl nicht.
Eine getrennte Charakterisierung darf einen Kandidaten widerlegen; Abweichungen
führen zum Stop statt zum nachträglichen Ergänzen oder Filtern der Erwartung.

Die gewählte Installation enthält alle 15 Felder; jeder ausgewählte Modulrecord
enthält alle elf Felder einschließlich privater vollständiger Locator,
Package-Locations und Loadernamen/-pfade. Frozenverbände folgen §3/§8:
beide tatsächlich kohärenten Frozenpartner können einen Verband tragen;
Mixedpartner bleiben vollständig mit `()`. Sysconfig-Buildmodul und eine
ausdrücklich ungesetzte `_PYTHON_SYSCONFIGDATA_NAME`-Overrideauswahl gehören
zur konkreten Bootstrapauswahl. Ein früheres Isolationflag ersetzt diese Wahl
nicht. Physische Installationtrust bleibt eine ausdrücklich deklarierte Annahme.

Die vollständige neue Auswahl wird vor Start und Kommunikation unabhängig
reviewt und rein gerechnet: sämtliche fünf E4-Formen je Ordinal erfüllen
jeweils 16.384 Bytes einschließlich Header und zusammen 65.536 Bytes.
Pool-, Knoten-, Tiefen-, Sequenz- und Feldgrenzen gelten gleichzeitig.
Die volle gemeinsame M enthält Input82, Worker und Kontext; beide D9 bleiben
physisch erhalten. Ein kleiner Einzelreport, historische Größen oder ein
angepasster Locator belegen diesen neuen Fit nicht. Überlauf bleibt Ablehnung.

### 16.2 Importneutraler Bootstrap und tatsächlich gehaltene Kontrollbytes

§8 bleibt verbindlich: der absolute Scriptstart verwendet `-I -S -B`, die fünf
direkten Stdlibimports `importlib.util`, `sys`, `sysconfig`, `json`, `struct`
und ausschließlich die Controls `__main__`, `dgn007_import_runtime_profile`.
Receiver, geschlossene Formprüfung und Reporter werden als zu implementierende
Inlinevariante im Script gewählt. Vor PRE_IMPORT werden keine Combined-, Codec-,
Matcher-, Input82-, Bundle- oder sonstigen Projektadaptermodule importiert.
Die vorhandenen APIs dienen kontrollseitig als Konformitätsreferenz;
ihre Semantik gilt nicht automatisch als im Inlinecode umgesetzt.

Die separat reviewte Bootstrapquelle hält die vorab ausgewählten vollständigen
Rawbytes der Profilkontrollquelle als feste private Konstante. Ihr tatsächlicher
Dateiread ist auf 131.072 Bytes plus einen Sentinel begrenzt. Die gelesenen
Bytes müssen vor Specanlage und Ausführung exakt der gehaltenen Konstante
entsprechen. Erst danach erfolgen `compile(raw, logical_file,
"exec", dont_inherit=True, optimize=0)` und die gebundene Modulausführung.
Source-Spec und SourceFileLoader beschreiben Name und Locator; weder
`SourceFileLoader.get_code` noch dessen `exec_module` übernimmt die Ausführung.
Ein Loaderlabel oder nachträglicher Hash ersetzt diesen Vorabvergleich nicht.
`-B` wird weiterhin nicht als Schutz vor Bytecodecache-Lesen ausgegeben.

Die Profilquelle behält ihre bisherigen Imports. SOABI und DESTSHARED werden
vor der Inventuraufnahme initialisiert und gegen die separat gewählte Installation
gebunden. Die früh übertragenen vollständigen Erwartungsrecords erlauben danach
nur die lokale Ankerbindung ihrer vorgewählten Namen. Fehlende oder zusätzliche
Cacheeinträge scheitern; der aktuelle Cache wird nicht zur eigenen Sollbaseline.
Die bekannte FileFinder-Hookbindung und ihre kontrollruntimegebundene Struktur
werden nach §8 geprüft, ohne den Hook auszuführen oder Trust daraus abzuleiten.

### 16.3 Zwei Freigaben mit endlichem Empfangshaltepunkt

Der Parent hält vor Transfer Input82, alle neun Rawbodies, die gewählte
Workerdeklaration und den jeweiligen Kontext getrennt. Er prüft ihre vollständigen
Formen und Rawhashes, alle fünf Erzeugungsgates und die Gesamtgrenze vor der
ersten Ausgabe. Nonce, Ordinal, Einstieg und PRE_IMPORT-Phase sind damit vor
dem Workerreport gewählt; keine dieser Angaben stammt aus dessen eigener Wahl.

1. Der Parent sendet zunächst nur den 16-Byte-DGNC-Header und exakt dessen
   vollständige M-Metadata. Die deklarierte Bodylänge bleibt Teil des Headers;
   noch kein Kandidatenbody wird gesendet. Der Inlineempfang prüft Header und
   M vollständig begrenzt, einschließlich beider D9 und Originalinputdigest,
   bevor diese Erwartung für die lokale Profilaufnahme verwendet wird.
2. Der Worker nimmt sein Profil frisch auf, prüft lokale Kohärenz vor/nach
   Scalarprojektion und sendet ausschließlich die vollständige R-Form der
   tatsächlich aufgenommenen Skalare. Kein Body-/UsedBytes-Erfolg wird gemeldet.
   Der Parent dekodiert den gesamten Report und vergleicht alle empfangenen
   Felder mit seiner separat gehaltenen Auswahl und seinem Kontext.
3. Erst danach sendet der Parent `BODY_RELEASE`. Der Worker prüft dessen
   exakte Kontextbindung und nimmt genau die neun angekündigten Bodies auf.
   Alle Größen, Offsets, Einzel-/Gesamtcaps und tatsächlichen Rawhashes werden
   vor einem Gesamtvergleich oder einer Consumerfreigabe geprüft.
   Ein gebundenes `BODY_END` schließt diese Übertragung ab.
4. Erst nach vollständigem eigenen M-/Body-/Originalhashcheck und unverändertem
   frischem lokalen Profil meldet der Worker `INPUT_COMPLETE`. Eine hierfür
   erneut erforderliche Aufnahme wird innerhalb derselben Deadline geprüft;
   sämtliche tatsächlich frisch aufgenommenen Felder müssen lokal vollständig
   dem schon geprüften R entsprechen. Jede Abweichung stoppt den Versuch.
   Der Kanal trägt genau einen vollständigen PRE_IMPORT-Report, keinen zweiten
   POST-Report und keinen Digestersatz für dessen Felder. Dieser lokale Check
   ist kein zweiter vom Parent vollständig empfangener Beobachtungsbeleg.
5. Der Parent prüft dieses Abschlussrecord und sendet einmal `IMPORT_RELEASE`.
   Anschließend schließt er stdin. Der Worker verlangt das erwartete EOF ohne
   Zusatzbytes, bevor eine spätere Kandidatenoperation zulässig wird.
   EOF ist keine zusätzliche Freigabe und ersetzt keines der beiden Commands.

`BODY_RELEASE`, `BODY_END` und `IMPORT_RELEASE` sind jeweils eine kanonische
ASCII-JSON-Tupelzeile `[kind, ordinal, nonceHex, context_digest]` mit LF,
höchstens 256 Bytes und festen Kindwerten. Pro Worker sind genau diese drei
Commands erlaubt. `context_digest` ist genau der eigene §14.3-Digest über
das kanonische vollständige E4-K-Präbild mit Rolle
`pooled-profile-binding-context/v1`, ohne Header. Er bindet insbesondere
Ordinal, Einstieg und Phase. Der ursprüngliche I7-/Input82-Wert
`context_sha256` bleibt getrennt und unverändert; er wird nicht umgedeutet.
Die tatsächlich codierten Combinedbytes und alle drei
Commands müssen gemeinsam vor Start vollständig gerechnet innerhalb desselben
unveränderten Transfercaps liegen: höchstens 1.064.960 Bytes je Worker und
global höchstens 3 MiB Bodies plus 48 KiB Metadata einschließlich Steuerbytes.
Die höchstens 768 Commandbytes erhalten kein Zusatzbudget. Einzelne Metadata-
und Bodycaps sowie der reine §15-Codec bleiben unverändert. Dessen maximaler
Frame ist auf dieser Handshakeroute ohne Steuerreserve nicht startbar.
Der Worker liest nie über die gerade erlaubte Phase hinaus.

Ein vorzeitiges EOF, falscher Command, zusätzliche Nachricht, andere Nonce,
Phase oder Ordinal führt zur festen Ablehnung. Empfangene Felder werden nie
aus Callerwerten ergänzt. `INPUT_COMPLETE` bedeutet Byteaufnahme und Prüfung,
keine Ausführung. Hashgleichheit und erfolgreiche Freigaben attestieren weder
Host-, Kanal- noch Actorherkunft. Die lokale Consumptiontabelle reserviert
Nonce/Ordinal vor Start und erlaubt jede Phasentransition genau einmal.
Ein abgebrochener oder unbekannt beendeter Versuch wird nicht erneut gestartet.

### 16.4 Begrenzter Rückkanal und gemeinsame Kosten

Der Parent drainiert stdout und stderr während sämtlicher stdin-Schreibphasen
mit endlichen nichtblockierenden Schritten. Er wartet nicht zuerst auf das
Ende des Schreibens. Der Worker wartet an den beiden Haltepunkten nur auf
den nächsten erlaubten Command. Vererbte offene Pipes, Backpressure und
No-progress werden innerhalb derselben begrenzten Steuerung behandelt.

Die R-JSON wird ohne zweiten JSON-Escape-Layer in ASCII-Fragmente geteilt:
`P|ordinal|sequence|total|payload` mit LF, höchstens 896 Payloadbytes und
höchstens 32 Envelopebytes einschließlich LF. Das Payload bleibt opak bis
zur vollständigen begrenzten Zusammensetzung; nur die ersten vier Separatoren
werden ausgewertet. Kanonisches E4-JSON enthält keine physischen Zeilenumbrüche.
Maximal 16.368 JSONbytes benötigen höchstens 19 solche Records. Jeder Record
bleibt unter der allgemeinen 1.024-Byte-Zeilengrenze; keine Einzelzeile trägt
den vollständigen privaten Report.

`PROFILE_BEGIN` und `PROFILE_END` sind jeweils kanonische ASCII-Tupelzeilen
mit Ordinal, JSONlänge und Fragmentanzahl; END enthält zusätzlich den SHA256
der tatsächlich zusammengesetzten JSONbytes. Beide bleiben höchstens 256 Bytes.
Der Parent rekonstruiert nur den fest gewählten DGNP-REPORTED-Header und prüft
das tatsächliche E4, Kontext, Schema, Pool, Repack und alle Records vollständig.
Fehlende, doppelte, umgestellte oder fremde Fragmente scheitern ohne Teilreport.
Private Reportbytes bleiben ausschließlich im begrenzten Parentmemory.

Alle Envelope-, LF-, Footer- und tatsächlichen stderr-Bytes zählen vor Pufferung
oder Decode zur gemeinsamen 65.536-Byte-Kappe für sämtliche drei Workers.
Für den späteren Quellenloader werden insgesamt höchstens zwölf eigene
Modulausführungen über die drei festen Einstiegssätze und höchstens zwei
codefreie Parentmodule je Worker erwartet. BEGIN/COMPLETE tragen je höchstens 256 Bytes; sie
binden Modulordinal, Sequenz und Rawhash an den einmal festgelegten Kontext.
Ihre konkrete vollständige Form und tatsächliche Erzeugung sind Folgearbeit.

Der konservative Kanalnachweis reserviert `3*(16368+19*32) = 50928` Bytes für
R-Fragmente, 1.536 für PROFILE-BEGIN/END, 768 für INPUT_COMPLETE,
6.144 für zwölf BEGIN/COMPLETE-Paare, 3.072 für sechs Parent-Paare,
768 für drei SESSION_END und 768 für höchstens drei feste Fehlerrecords.
Damit sind höchstens 63.984 Bytes vorgesehen; 1.552 Bytes verbleiben innerhalb
derselben Kappe für weitere tatsächliche stderr-Bytes. Dies ist Budgetarithmetik,
kein tatsächlicher Kanal- oder Erfolgsbeleg. Jede spätere Änderung von Anzahl,
Feldform oder Länge benötigt denselben vollständigen Nachweis; tatsächliche
Byteüberschreitung scheitert unabhängig von dieser Reserve.

Der Parent startet höchstens drei Workers seriell in der festen Reihenfolge
Runner, Proxy, Harness und erst nach unabhängigem Cleanup des Vorgängers.
Eine gemeinsame monotone 20-Sekunden-Deadline beginnt vor der regulären
Probevorbereitung und wird für Aufnahme, Transfer, Freigaben, Import, Drain
und Abschluss nie erneuert. Daneben gelten insgesamt 4.096 I/O-Schritte
und 64 aufeinanderfolgende Schritte ohne neue Bytes, EOF oder Zustandsübergang.
Fehlgeschlagene Starts/Schritte und Wartezeiten bleiben gebuchte Kosten;
fachliche Query-Store-Polls gehören nicht zu diesem I/O-Zähler.

Cleanup hat höchstens zehn Sekunden kumulative gemessene monotone Segmente
mit nicht erneuerbarem Restbudget; die reguläre Wallclock läuft weiter.
SESSION_END bindet die endgültigen Recordzahlen und den bisherigen Kanalhash;
danach sind vollständiges stdout-/stderr-EOF und eigener Exit getrennt nötig.
Exit vor Drain, Kill oder ein Footer allein beweist keinen Cleanup.
Nur die eigene neue Linux-Prozessgruppe wird anhand ihres gehaltenen Leaders
gestoppt und unabhängig auf Kinderabsenz geprüft; keine fremde PID-/Namenssuche.
Bindungsverlust, Reap-/Restorefehler oder harte Unterbrechung bleiben dominant
und führen ohne Absenzreceipt zu unbekanntem Cleanup, nie zu Recovery-PASS.

### 16.5 Getrennte nächste Abnahmen und verbleibende Grenzen

Der nächste kleine Implementierungsschnitt ist ausschließlich die feste
Bootstrapkontrollquelle mit synthetischen Gegenproben. Er führt noch keine
operative Workerinventur oder DGN-Imports aus. Danach folgen die neue separat
gewählte Installation/volle Inventur und vollständige Fünf-Formen-Größenprüfung,
der importneutrale Empfang/Report und anschließend Parentadapter, tatsächlicher
Quellenloader, Consumption und unabhängig geprüfter Drei-Worker-Cleanup.
Jede Stufe bleibt an ihre konkreten Sources und tatsächlich ausgeführten Checks
gebunden; die implementierten Kontrollcodecs ersetzen keine Adapterabnahme.

| Gegenprobe | Verbindliches späteres Gate |
|---|---|
| Profilbytes ändern zwischen Vorpin und Read; pyc liegt daneben | tatsächliche gehaltene Bytes vor compile prüfen; keine Cache-/Loaderlabelverwendung als Bytebeleg |
| neue Projektimporte oder fehlender Sysconfigrecord vor PRE | vollständige Inventurablehnung, kein Controlausbau oder Sollrefresh |
| neue Bootstrapquelle passt nicht in eine volle Form | kein Start, kein Filter, kein Capwechsel |
| falsche/fehlende späte M-/Bodyfelder trotz frühem passenden Profil | atomare Ablehnung vor INPUT_COMPLETE und Kandidatenfreigabe |
| Schreibbackpressure bei gleichzeitig vollem stderr | beide Pipes begrenzt drainieren; keine getrennte zusätzliche Ausgabekappe |
| Teilreport, fremder Ordinal oder doppelte Freigabe | keine Zustandsfortsetzung und kein stateless Fallback |
| EOF vor IMPORT_RELEASE oder Zusatzbytes danach | feste Ablehnung; EOF heilt keine fehlende Freigabe |
| Profil-/Cache-/Hookänderung nach frühem Report | frische Aufnahme erforderlich, keine dauerhafte Validiertheit gehaltener Anker |
| Leaderexit mit geerbten offenen Pipes; fehlender Footer/Absenz | kein Erfolg aus Exit; Deadline und dominanter Cleanupfehler bleiben erhalten |

Inlinekonformität, neue vollständige Inventur, konkrete Kanalreceiptformen,
Resolver-/Stdlibtrust und tatsächliche BEGIN/COMPLETE-Bytes bleiben offen.
Auch eine frische Aufnahme liefert keine atomare oder dauerhaft gültige Runtime-
Snapshotgarantie. Alle Attestationsflags bleiben in diesem Design false.
Gewöhnliche begrenzte Offlineentwicklung liegt im bestehenden Auftrag;
SQL-/Docker-/Collector- oder materielle Methodenerweiterungen folgen daraus nicht.
G13, v1, DEC-068, historische FAILs, geschützte PR68 und die zurückgestellte
Capture-API bleiben unverändert. Dieser Abschnitt erzeugt keinen RunRecord,
keine Methodenfreigabe und keinen tatsächlichen Worker-/UsedBytesbeleg.

## 17. Reiner Generator gehaltener Kontrollbootstrapquellen

Der getrennte Vorschnitt in
[`dgn007_control_bootstrap_source.py`](../../Tests/Tools/dgn007_control_bootstrap_source.py)
erzeugt private Scriptbytes aus separat gewählten, vertrauten Kontrollbytes.
`build_control_bootstrap(profile_raw, *, logical_profile)` liest selbst keine
Datei, kompiliert oder importiert kein Profil und startet keinen Prozess.
Der eingefrorene, reprfreie `BootstrapSource` hält vollständige Script- und
Profilbytes sowie den Locator; öffentliche Größen, Hashes und feste Labels
geben keinen Quelleninhalt aus. `trust_assumed` benennt die Kontrollannahme;
Trust-, Runtime-, Import-UsedBytes- und Methodenattestationsflags bleiben false.
Dies ist kein operativer Worker und ersetzt den geplanten Scriptlocator aus §8
nicht. Die bestehende echte Profilquelle wurde in diesem Schnitt nicht geladen.

### 17.1 Gebundene Bytes und begrenzte Metadaten

Nur exakte nichtleere `bytes` bis 131.072 Bytes und ein exakter kanonischer
absoluter Linux-Locator bis 4.096 UTF-8-Bytes sind zulässig. Das erzeugte
UTF-8-Script ist einschließlich des expandierten Rawbyteliterals, des Locators
und des Templates zusätzlich auf tatsächliche 131.072 Bytes begrenzt.
Ein passendes Profil allein garantiert deshalb keinen passenden Scriptumfang.
Die fünf direkten Templateimports bleiben `importlib.util`, `sys`, `sysconfig`,
`json` und `struct`; zusätzliche Projektimporte gehören nicht zu diesem Generator.
Diese AST-Gegenprobe attestiert keine beliebigen transitiven Imports gewählter
Profilbytes oder die spätere vollständige operative Inventur.

Der einzelne gebundene Kontrollladeversuch prüft den gehaltenen Modulcache
und die beiden Kontrollnamen vor einem Read. Ein vorhandenes Profil wird nicht
übernommen oder entfernt. Cache-, Modul-, Spec-, Loader- und Factorydicts haben
höchstens 256 exakte Stringkeys mit jeweils höchstens 4.096 UTF-8-Bytes; die
Prüfung erfolgt vor fremden Getter-/Equality- oder Cachelookupoperationen.
Die erneute Main-Typprüfung erfolgt auch nach Exec vor dessen Namespacezugriff.

Ein tatsächlicher binärer Read nimmt höchstens 131.073 Bytes einschließlich
Overflow-Sentinel auf. Er muss vor Compile und Specanlage exakt den gehaltenen
Erwartungsbytes entsprechen. Genau dieses tatsächliche Readobjekt wird mit
`compile(raw, locator, "exec", dont_inherit=True, optimize=0)` kompiliert und
das gleiche Codeobjekt ausgeführt. Python 3.12 unterstützt Bytequellen und
die ausdrücklich gewählten Compileparameter. [Python-3.12-Referenz](https://docs.python.org/3.12/library/functions.html#compile), abgerufen am 2026-10-08.

Die gehaltene `SourceFileLoader`-Klasse aus `_frozen_importlib_external` dient
der Modul-/Specmetadatenanlage. Name und Pfad werden gegen den gewählten Locator
geprüft; `get_code` und `exec_module` sind keine Quellenroute. Die Factory-APIs
erzeugen Spec und Modul, während dieser Vorschnitt die Quellenausführung selbst
bindet. [Python-3.12-importlib-Referenz](https://docs.python.org/3.12/library/importlib.html#importlib.util.module_from_spec), abgerufen am 2026-10-08.
Eine danebenliegende pyc-Datei wird nicht als Kontrollbytebeleg verwendet.
Modul, Spec, Loader, Name, File, Package und Cachedfelder müssen vor und nach
Exec kohärent sein; Cachedwerte haben vor Equality die Form None oder exactstr.
Diese Checks begründen keine Herkunftsattestation für die gewählte Kontrollruntime
und sind keine Sandbox für beliebige untrusted Profilprogramme.

Fehler erhalten feste getrennte Read-/Compile-/Execlabels. Eine im Profil selbst
erzeugte OSError oder SyntaxError wird dadurch nicht als vorgelagerter Read- oder
Compilefehler ausgegeben. Der fehlgeschlagene Versuch wird nicht wiederholt.
Cleanup entfernt nur den nach Identität selbst eingesetzten Profileintrag;
fremder Ersatz, anderer Cache oder unprüfbare Keys bleiben unangetastet und
liefern `CONTROL_CLEANUP`. Die öffentliche Erzeugung unterdrückt die sichtbare
Exceptionverkettung mit `from None`; dies löscht nicht Pythons internes
`__context__` und darf nicht als solches behauptet werden.

### 17.2 Synthetische Abnahme und nächste operative Gates

Die Gegenproben in
[`test_dgn007_control_bootstrap_source.py`](../../Tests/Static/test_dgn007_control_bootstrap_source.py)
verwenden ausschließlich feste harmlose synthetische Kontrollbytes, einen
getrennten Fakecache und eigene temporäre Dateifixtures. Sie prüfen unter
anderem tatsächliche Read-/Compile-/Execobjekte, CRLF, BOM und Encodingcookie,
Rawmismatch vor Compile/Spec, pyc-/Loadergegenproben, Script- und Readcaps,
fremde Typen/Keys, Metadatenmutation, phasengenaue Fehler, eigenen Cleanup und
den abgelehnten zweiten Versuch. Windows-Fixturemetadaten sind ausdrücklich
synthetische Linuxmetadaten; sie attestieren keine echte Linux-Factoryausführung.

Der erste lokale Lauf unter CPython 3.12.14 mit `-I -S -B -X utf8` meldete
32 Methoden, 23 PASS, acht FAIL, einen ERROR und keinen SKIP. Die reale Windows-
Specfactory normalisierte den synthetischen absoluten Linux-Locator; dies
verletzte die beabsichtigte Kohärenz. Die Fixture wurde daraufhin eng korrigiert,
ohne den Linuxvertrag des Generators zu lockern. Der korrigierte Abnahmestand
wird ausschließlich an seinen erneut geprüften Source-/Testfreeze gebunden.
Der zweite lokale Lauf meldete 32 Methoden, 30 PASS, zwei FAIL, keinen ERROR
und keinen SKIP. Die beiden Body-import-sys-Mutationsfälle erforderten eine
ausdrückliche Bindung der synthetischen Modulbuiltins an den getrennten
Fixtureimportcache: beide lieferten unerwartet `LOADED_BOUND_CONTROL_SOURCE`,
statt der erwarteten `CONTROL_COHERENCY`-/`CONTROL_CLEANUP`-Ablehnungen.
Dieser Testbefund wird getrennt erhalten. Der frühere echte Cachezustand dieser
beendeten Testprozesse wurde nicht separat aufgenommen; ein damaliger
Profileintrag oder Hostcacheeffekt wird deshalb nicht behauptet.
Nach erneuter unabhängiger Sicherheitsprüfung bestand der dritte isolierte
Lauf unter CPython 3.12.14 alle 32 Methoden in 0,151 Sekunden ohne FAIL, ERROR
oder SKIP. Die explizite Body-sys-/Fakebuiltinsidentität, tatsächliche Absenz
jedes gehaltenen eigenen Tempziels sowie unveränderte reale
Profilecachemitgliedschaft, Mainobjekt und Mainname bestanden. Die Produktionsquelle blieb
bei beiden Fixturekorrekturen unverändert. Der geprüfte finale LF-Stand lautet:

| Datei | Bytes | SHA-256 |
|---|---:|---|
| Generator | 11.206 | `5df8995a778379328b501f900fcc2b10f755eca5915958784fb4bed999da937b` |
| Testsuite | 20.109 | `727bbcbe024dc9ab211c4ca5ea2ae1e20dd8f23a0830a246131575ce4f9c7763` |

Dies belegt ausschließlich den synthetischen Vorschnitt am genannten Source;
kein tatsächliches Kontrollprofil, operativer Worker oder DGN-Kandidat lief.

Als nächster zulässiger Schnitt bleiben die frische, unabhängig vorgewählte
operative Installation und vollständige S15-/P11-Inventur mit allen fünf
Darstellungen und dem gemeinsamen 64-KiB-Gate. Charakterisierung und historische
Fixture werden nicht zur operativen Baseline erklärt. Inline Receiver/Reporter,
vollständige Kanalzustände, Parentadapter, tatsächlicher DGN-Quellenloader,
Consumption/Replay und unabhängig bereinigte eigene Worker folgen getrennt.
G13, v1, DEC-068, historische FAILs, PR68 und die zurückgestellte Capture-API
bleiben erhalten; keine SQL-/Acquisition-/Capstone- oder Methodenfreigabe.

## 18. Feste Sysconfig-Vorinitialisierung gehaltener Kontrollquellen

Die nächste getrennte Quellen-Erweiterung ergänzt den reinen Generator um
`build_sysconfig_control_bootstrap(profile_raw, *, logical_profile,
expected_soabi, expected_destshared)`. Sie erzeugt weiterhin ausschließlich
private Scriptbytes. Die bestehende API `build_control_bootstrap` und deren
erzeugte Quellbytes bleiben erhalten. Alle Aussagen aus §17 sind historische
Evidenz ihres dort gebundenen Sources, keine Abnahme dieser Erweiterung.

Die beiden Erwartungswerte sind separat gewählte exakte Texte, keine Aufnahme
aus dem laufenden Modulcache. SOABI enthält keinen NUL oder ungepaarten
Surrogate und höchstens 4.096 UTF-8-Bytes; ein expliziter Leertext ist ein Wert,
kein None-Default. DESTSHARED ist ein kanonischer absoluter Linux-Locator
innerhalb derselben Feldgrenze. Beide Literale zählen einschließlich ihrer
Expansion zum unveränderten tatsächlichen 131.072-Byte-Scriptcap. Die fünf
direkten Imports und zwei Controls bleiben unverändert; keine Codec-, Input82-,
Matcher-, Observation- oder Kandidatenimporte gehören zu diesem Vorschnitt.

Die erzeugte neue Route hält die Sysconfig-Modul-, Namespace-, Funktions-,
Code-, Globals-, Spec- und Loaderanker vor dem gebundenen Profilexec aus §17.
Nach diesem Exec prüft sie innerhalb desselben Kontrolllifecycles die gehaltene
Bindung und ruft SOABI und DESTSHARED in fester Reihenfolge auf. Vor und nach
jedem Call werden die Anker und die Profilkohärenz erneut geprüft.
Beide tatsächlichen Rückgabewerte werden vollständig auf ihre
Form geprüft, bevor ihr Vergleich mit den separat gewählten Texten erfolgt.
Erst nach erneuter Modul-, Callable-, Cache- und Profilkohärenz darf der
Kontrollladeversuch erfolgreich enden. Es gibt keine Profilaufnahme und keinen
operativen Workerstart. Ein Fehler entfernt ausschließlich den selbst
eingesetzten Profileintrag; der bestehende identitätsgebundene Cleanup bleibt
dominant. Sysconfigcache, Buildmodule und fremde Einträge werden nicht
zurückgesetzt, übernommen oder nach einem Fehler repariert. Kein Retry.

Dokumentiert: `sysconfig.get_config_var` liefert für einen fehlenden Namen
`None`; ein solcher Wert ersetzt keinen gewählten Text.
[Python-3.12-Sysconfig-Referenz](https://docs.python.org/3.12/library/sysconfig.html#sysconfig.get_config_var), abgerufen am 2026-10-08.
Projektseitig bleibt der Grund aus §8/§16 maßgeblich: Die vorhandene Aufnahme
kopiert den Modulcache vor ihrem eigenen SOABI-Aufruf. Ein dort erst geladenes
Buildmodul darf keinen fehlenden Vorinitialisierungsrecord heilen. Zwei passende
Werte attestieren weder dieses Buildmodul noch die Abwesenheit eines
`_PYTHON_SYSCONFIGDATA_NAME`-Overrides oder die Herkunft der Kontrollruntime.
Diese Auswahl, die vollständigen S15-/P11-Felder und alle fünf Darstellungen
einschließlich des gemeinsamen 64-KiB-Gates bleiben getrennte nächste Abnahmen.

Der unabhängige Source-/Test-PRE und der anschließende einmalige isolierte
Ownerlauf bestanden: CPython 3.12.14 mit `-I -S -B -X utf8`, Exit 0,
53/53 PASS in 0,401 s, 0 FAIL/ERROR/SKIP. Die 32 bisherigen und 21 neuen
Testmethoden verwenden ausschließlich die gebundene Fake-Sysconfig und feste
synthetische Kontrollbytes; kein realer Sysconfigcall oder Profil-/Workerstart.
Aufrufreihenfolge, beide tatsächlichen Werte, Form vor Vergleich,
Fremdtypen, Mismatch, Mutation, Exceptionprivacy, Literal-/Scriptcap und eigener
Cleanup gehören zum selben geprüften Sourcefreeze. Die bisherigen echten
Cache-/Main-Sentinels und die eigene Tempzielabsenz bleiben erhalten.
Keine tatsächliche Installation, Workerinventur, Profilaufnahme oder DGN-Quelle
wird damit ausgeführt; Trust-, Runtime-, UsedBytes- und Methodenflags bleiben
false. G13, v1, DEC-068, historische FAILs und geschützte Arbeit bleiben erhalten.


Der ausgeführte Source/Testfreeze blieb danach unverändert (SHA-256 über
LF-normalisierte Bytes):

| Quelle | SHA-256 |
|---|---|
| Tool | `9782f6ec59a5bdd8107ef35150686aea0f32ce0eb6bab7361b20d878b42243a7` |
| Test | `2afbd7997f62e0f4decd9c025d2ca10db9fea9aa4c05d32e53811192647da894` |

Die Zweifile-Bindung ist SHA-256 über das UTF-8-kodierte kompakte JSON der
sortierten `[Pfad, LF-SHA-256]`-Paare mit `ensure_ascii=True` und
`separators=(',', ':')`:
`3e263551fcf7b863646c76352425f1b5d2d476e0ed9401ae0e394c96ddda184a`.
Die Legacy-Goldenquelle blieb 8.101 Bytes mit SHA-256
`6b6307c021e97a5c4949306b5b9ac7f7063a7f31522be70db27c14c6a79956df`.
Keine lokale Wiederholung älterer Fixture-/Helper-/Profilaufnahmen.

## 19. Private Auswahlgrundlage vor einer vollständigen operativen Inventur

Die frische vollständige Auswahl aus §8/§16 bleibt offen. Nach §18 ist der
nächste kleine Vorschnitt eine separat reviewte, begrenzte native
Installationsmetadatenabfrage. Sie ist keine Ausführung der Bootstrapquelle,
keine Profilaufnahme und keine operative S15-/P11-Baseline. Die bisherigen
historischen Kontrollcaptures werden dafür nicht wiederholt oder promoviert.

Die Quellen-/Installationsauswahl beginnt mit gezielter lesender Prüfung der
bereits vorhandenen Linux-CPython-3.12-Executable, öffentlichen Paket- und
Buildquellen sowie der direkten Stdlibquellen. Die tatsächlichen privaten
Locator und vollständigen Records bleiben unversioniert. Eine existierende
Quelldatei belegt keinen Source-Loaderkind: ein Modul kann in der gewählten
Installation Builtin oder Frozen sein. Ebenso ersetzt ein vorhandener
Sysconfigdatensymlink nicht den aus der konkret installierten Sysconfigquelle
begründeten Standardmodulnamen. Die frühere Namenwahl ist kein Fallback.

| Auswahlfeld | Zulässiger Vorschnitt | Weiterhin fehlender Nachweis |
|---|---|---|
| Implementation, Patch, Executable, vier Prefixes, gesamte Startup-Pfade, sechs Flags | begrenzte native sys-Felder der vorher gewählten Executable | tatsächliche Felder der endgültigen gehaltenen Bootstraproute |
| Builtin-Verfügbarkeit | vollständige begrenzte `sys.builtin_module_names` | tatsächliche Cachemitgliedschaft oder P11-Modul-/Spec-/Loaderrecord |
| Frozen-Verfügbarkeit | ausschließlich native Abfrage einer vorab festen quellenbegründeten Namenfolge | tatsächliche Importausführung, Frozenverbände und vollständige P11-Metadaten |
| SOABI, DESTSHARED und Sysconfigdatenmodulname | separat gelesene konkrete Build-/Sysconfigquelle als Wahlgrundlage | tatsächliche §18-Calls, explizite Override-Auswahl und passende Inventur |
| Dateiidentität und Paketstand | gebundene Rohbytes/Hashes beziehungsweise gelesene Paketmetadaten | physischer Trust oder bereits ausgeführte Bibliotheksbytes |

Dokumentiert: `sys.builtin_module_names` beschreibt die in den Interpreter
einkompilierten Module; der Modulcache beschreibt bereits importierte Module.
[Python 3.12: sys](https://docs.python.org/3.12/library/sys.html#sys.builtin_module_names),
abgerufen am 2026-10-08. Die Auswahl hält diese beiden Aussagen getrennt.
Die Isolationflags folgen der
[Python-3.12-Kommandozeilenreferenz](https://docs.python.org/3.12/using/cmdline.html#cmdoption-I);
`-B` wird weiterhin nicht als Schutz vor Bytecodecache-Lesen ausgegeben.

Die private Metadatenquelle und ihr vollständiger Aufrufplan müssen vor dem
einmaligen Versuch durch Owner, Root und unabhängigen Review eingefroren sein.
Vorgewählte Executable-/Quellenpins, feste Argumente, exakte Typ-/Feldformen,
positive Deadline und gemeinsame Ausgabegrenze vor Pufferung/Decodierung gehören
zusammen. Kein `sys.modules`-Array wird zur Sollinventur. Keine Profil-,
Sysconfig-, Bootstrap-, DGN- oder Hookausführung; kein Netzwerk, keine Installation
und keine neue Instanz. Native Verfügbarkeitsabfragen führen keine Kandidaten
aus. Keine Diagnosepayloads oder Tracebacks in öffentlicher Rückgabe.

Windows-Launcher und Linux-Kind werden getrennt behandelt. Ein Windowsprozess-
Exit oder Kill ist kein Linux-Cleanupbeleg. Die Source-/Aufrufprüfung muss den
tatsächlich eigenen Linuxprozess und ausschließlich eigene neu erzeugte
Tempziele sowie deren unabhängige Reap-/Absenzprüfung vorsehen. Fremde PID-,
Gruppen- oder Zielbereinigung bleibt verboten. Ein unklarer Abbruch bleibt
`UNKNOWN`; Timeout oder Recovery erzeugen keine erfolgreiche Auswahl. Kein Retry
ohne neue geprüfte Quelle, Eingang oder konkrete Umgebungsänderung.

Die begrenzte Abnahme dieses Vorschnitts ist in §19.1 dokumentiert. Tatsächliche Installationsrecords,
Startuparrays, Hostpfade und Umgebungswerte verbleiben privat in den vorhandenen
Ignoregrenzen. Das Repository erhält nur datenschutzgeprüfte abstrakte Methode,
öffentliche Quellenfakten und den begrenzten wahrheitsgemäßen Nachweisstatus.

Anschließend bleibt die vollständige vorab quellenbegründete S15-/P11-Auswahl
für die endgültige gehaltene Quelle erforderlich, samt aller fünf Formen und
gemeinsamem 64-KiB-Gate. Der inline Receiver/Reporter und seine konkrete
Importreihenfolge fehlen weiterhin; eine Auswahl für §18 ersetzt deren spätere
Abnahme nicht. Parent-/Worker-, Loader-, Kanal-, Consumption-, Replay- und
Cleanupgates bleiben getrennt. Keine Trust-, UsedBytes-, SQL-, Methoden- oder
Capstoneattestation; G13, v1, DEC-068 und geschützte Arbeit bleiben erhalten.


### 19.1 Einmaliger begrenzter Auswahlbeleg

Owner, Root und unabhängiger Reviewer haben die vollständige private native
Quelle und den tatsächlichen Parent vor genau einem Versuch geprüft. Die
native Quelle blieb RAW=LF SHA-256
`432fa59b01ce6e9d464e07194961f5b34490c0f0f2309f755f0564f827a98d35`
(11.158 Bytes); der abschließend geprüfte Parent blieb RAW=LF SHA-256
`0f7b352350c5b7330df11169539a94a007831cad989a8d7fbe4b38ccfdf7f677`
(17.653 Bytes). Dies sind Quellenbindungen, keine Digestveröffentlichung realer
Installationsrecords und kein Herkunfts- oder Ausführungsbytebeleg.

Der konkrete private Windows-Parent setzte den Aufrufplan mit
`Popen(shell=False)`, gehaltenen Prozessobjekten und round-robin
`PeekNamedPipe` um; eine .NET-Ausführung wird nicht behauptet. Beide Pipes
wurden in höchstens 1.024-Bytechunks aufgenommen, mit Restbudgetprüfung vor
jedem Read und gemeinsamer Buchung vor Pufferung/Decodierung. Der eine
20-Sekunden-Deadlinewert begann vor dem ersten Pinprozess. Der getrennte
Fehlercleanup hätte höchstens fünf Sekunden und denselben globalen
4.096-Schrittzähler verwendet; keine Erneuerung von Byte-/Zeitbudgets.
OS-Aufrufe und Prozessstart bleiben kein generischer Kernel-Harddeadlinebeweis.

Der einmalige Versuch endete mit Exit 0. Die native Ausgabe enthielt 20
vollständig geprüfte Felder in 1.332 ASCIIbytes: 60 Builtin-Verfügbarkeiten,
vier vorab feste Frozenfragen mit vier positiven Antworten, vier Prefixfelder,
drei Startup-Pfade und die sechs gewählten Flags. Die vollständigen Werte
bleiben ausschließlich im privaten ignorierten Ergebnis. Native Verfügbarkeit
ist keine tatsächliche Import-, Cachemitgliedschafts- oder P11-Attestation.

Alle vier gehaltenen Windows-Prozesse lieferten Exit 0, Wait und beide EOFs;
der Linux-Supervisor hielt/waitete sein eigenes Kind und lieferte die feste
Quittung. Ein separater lesender Aufruf prüfte ausschließlich beide gehaltenen
eigenen Linux-PIDs. PRE/POST-Pins und beide Kontrollquellen blieben unverändert.
Die gemeinsame tatsächliche stdout/stderr-Aufnahme einschließlich Pin- und
Absenzaufrufen betrug 2.403 Bytes; die reguläre interne Dauer 3,937 Sekunden.
Der Output wurde erst danach exklusiv in das vorher abwesende eigene private
Ergebnisziel geschrieben. Keine eigene Linux-Tempdatei wurde erzeugt.

Ein unabhängiger POST prüfte ohne Parent-/Native-/Profilreplay die vollständigen
privaten Records, exakten Formen, Bytes/Längen, Quittungen und Budgets. Die vier
eigenen Windows-PIDs und beide gehaltenen Linux-PIDs wurden erneut ausschließlich
lesend auf Abwesenheit geprüft und waren abwesend. Alle sechs Attestationsflags
blieben false. Keine Profil-/Sysconfig-/Bootstrap-/DGN-/SQL-Ausführung und kein
Runtime-, Trust-, UsedBytes-, Methoden-, Inventur- oder Workerclaim.

Nächster zulässiger kleiner Offline-Schnitt ist die reine additive Erzeugung
von Inline-Header-/E4-Syntaxcode mit kanonischer Darstellung und vollständigen
Syntax-/Pool-/Positionsgrenzen. Dieser Schnitt ersetzt keine
M/IP/S15/P11/D9-Semantik, Originaldigestprüfung oder Rawbodyfreigabe.
Anschließend müssen sämtliche fehlenden inline Teile und ihre Importreihenfolge
feststehen, bevor die endgültige gehaltene Quelle mit vollständiger separat
vorgewählter S15/P11-Inventur und dem Fünf-Formen-/64-KiB-Gate abgenommen wird.
Kein alter Capture, keine historische Namenliste und kein erfolgreicher
beobachteter Cache wird nachträglich zur operativen Sollbaseline.

## 20. Reine additive Inline-Metadata-Syntaxquelle

Der dritte reine Builder `build_inline_syntax_control_bootstrap` ergänzt
`Tests/Tools/dgn007_control_bootstrap_source.py`. Er übernimmt ausschließlich
die separat gehaltenen Kontrollinputs der Sysconfigroute und fügt feste
Inline-Syntaxdefinitionen vor deren bestehenden Dispatcher ein. Beide älteren
Generatorrouten, `_PREFIX` und `_BODY` bleiben erhalten. Keine neue direkte
Importabhängigkeit: weiterhin `importlib.util`, `sys`, `sysconfig`, `json` und
`struct`, zwei Controls. Die vollständigen erzeugten UTF-8-Scriptbytes bleiben
einschließlich Literalexpansion und neuen Definitionen auf 131.072 Bytes
begrenzt; die bisherigen Profil- und Locatorgrenzen bleiben erhalten.

Die private Funktion `_inline_metadata_syntax(header, metadata)` erhält zwei
bereits gehaltene exakte Byteobjekte. Sie nimmt keinen Stream auf. Vor dem
Parser prüft sie den 16-Byte-DGNC-Header `>8sII`, `DGNC001\0`, die exakte
Metadata-Länge und deren gemeinsames 16.384-Byte-Cap einschließlich Header.
Die deklarierte Bodylänge darf 1.048.576 Bytes, der deklarierte vollständige
Rahmen 1.064.960 Bytes nicht überschreiten. Diese deklarativen Prüfungen lesen
keine Bodies und belegen keine tatsächliche Bodygröße oder Bodyfreiheit.

Der begrenzte ASCIIparser erlaubt ausschließlich Arrays, Strings, `null` und
nichtnegative Integer mit höchstens acht Dezimalstellen. Es gelten 16.368
Knoten, Arraytiefe acht, höchstens 256 Sequenz-/Poolwerte und 4.096 UTF-8-Bytes
je Text; kein NUL, keine verwaisten Surrogates, keine zusätzlichen JSONformen.
E4-Version `pooled-binding-design/v1` und Rolle `METADATA` sind fest. Der lokale
Pool muss sortiert, eindeutig und vollständig verwendet sein. Die vollständige
Positionsprüfung erhält M=(I7,W6,K8), S15, P11, F3 und beide physischen D9;
Integer und Textreferenzen bleiben getrennt, nur die festgelegte nullable
specName-Position erlaubt `None`. Kanonischer ASCII-Repack muss mit sämtlichen
tatsächlich übergebenen Metadatabytes übereinstimmen.

Ein Syntaxerfolg liefert ausschließlich `VALID_METADATA_SYNTAX`, `NONE` und
den privaten vollständig rekonstruierten Payload. Eine Ablehnung liefert einen
festen Fehlercode und keinen Teilpayload. Das ist keine M/IP/S15/P11/D9-Semantik,
keine Installation-/Profilvalidierung, kein Originaldigest- oder Callerabgleich,
kein Bodyhash-/Consumption-/Replaynachweis und keine Body-/Importfreigabe.
Insbesondere muss eine vollständige, syntaktisch gültige Fixture mit
widersprüchlichen D9-, Commit-, Nonce- und Worker-/Kontextwerten hier akzeptiert
werden. `GENERATED_CONTROL_SOURCE_ONLY` und sämtliche false-Attestationsflags
bleiben erhalten; es gibt keinen stdin-/stdout-/Worker-/Kandidatenstart.

Die erweiterte isolierte synthetische Suite steht in
`Tests/Static/test_dgn007_control_bootstrap_source.py`. Root und unabhängiger
Review prüften den vollständigen Source-/Testfreeze vor jeder Ausführung.
Der erste isolierte Lauf unter CPython 3.12.14 endete mit Exit 1: 80 Tests in
0,628 Sekunden, 79 PASS und eine Fixture-Labelabweichung, kein ERROR oder SKIP.
Ein High-Surrogate ohne folgenden Low-Surrogate-Escape wurde korrekt abgelehnt;
die Fixture erwartete dabei `JSON_TEXT`, während die zwingende `_take`-Prüfung
wie im bestehenden Codec `JSON_FORM` lieferte. Nur diese Testerwartung wurde
nach erneutem Root-/unabhängigem Delta-PRE korrigiert; Produktionscode,
Ablehnung und fehlender Teilpayload blieben unverändert.

Der zweite geänderte isolierte Lauf mit `-I -S -B -X utf8` bestand mit Exit 0:
80/80 PASS in 0,568 Sekunden, kein FAILURE, ERROR oder SKIP. Die Suite prüft
vollständige benannte Feldrückgewinnung für alle drei Ordinals, beide getrennten
D9 einschließlich beschädigter letzter Zelle, aktuelle Codecsyntaxprojektion
unter `_semantics`-Sentinel, semantische Widersprüche, Typen vor fremdem Dispatch,
Header-/Pool-/Integer-/Sequenz-/Depth-/Text-/Metadatacaps und deren Gegenfälle,
Unicode ohne Normalisierung, kanonischen Repack, private Fehlerausgänge,
Legacy-Goldenbytes sowie das vollständige Scriptcap. Eigene Tempabsenz und
gehaltene reale Cache-/Main-Sentinels bestanden; Sysconfigcalls blieben auf
separaten Fakeglobals. Kein realer Profil-/Sysconfig-/Worker-/SQLlauf.

Die abschließenden Quellenpins nach beiden Läufen sind für das Tool RAW
`3ca52d4046cd880117bd98606e460c08519cb422b37a8561dc17558ce934f343`
und LF `3af0ab9bd6ea134d349c74aa759583c57653e57774b8d37950ef29b92e4db3fc`
(28.077 LFbytes); für den korrigierten Test RAW
`ec7f27e2f43036e750f7c8a0869ffd5483d5c7a8593d25109be7946535e4c15b`
und LF `fd9a3714aa7816527d264aed2b257550bc6229d47a769bcb0c8b171019bcf54d`
(54.685 LFbytes). Die lexikografisch nach Pfad sortierte kompakte ASCII-JSONliste
`[[path,LFsha],...]` mit Trennzeichen `(',',':')` bindet beide Dateien als
SHA-256 `cc9a4b0519044c5472fbf11ad6c36f8be9a8937821f7ae185ebc097d102ea55b`.
RAW-/LF-Pins blieben nach dem erfolgreichen Lauf unverändert. Kein alter
privater Capture oder nativer Auswahlbeleg wurde erneut ausgeführt oder als
Sollinventur verwendet.

Nächster getrennter Vorschnitt ist die vollständige inline Metadata-Semantik
einschließlich Originaldigestbindung. Anschließend folgen fehlende inline
Receiver-/Reporter- und Kanalteile. Erst die endgültige vollständige Quelle
darf mit separat vorgewählter operativer S15-/P11-Inventur und dem gemeinsamen
Fünf-Formen-/64-KiB-Gate abgenommen werden. Parent-/Worker-, Loader-, Consumption-,
Replay-, Cleanup- und G13-Methodengates bleiben offen.

## 21. Reine additive Inline-Metadata-Semantikquelle

Der vierte reine Builder `build_inline_semantics_control_bootstrap` ergänzt die
bestehende Syntaxroute um feste Definitionen und den gehaltenen Kontrollanker.
Seine Eingaben bleiben ausschließlich die separat gehaltenen Profilbytes,
der logische Locator und die vorgewählten Sysconfigtexte. Die drei älteren
Builder und deren erzeugte Bytes bleiben erhalten. Die vollständige Quelle
bleibt auf 131.072 Bytes begrenzt; weiterhin fünf direkte Scriptimports und
zwei tatsächliche Controls. Der Builder startet keine Runtime.

Die private `_inline_metadata_semantics(header, metadata)` prüft zunächst die
vollständige Syntax aus §20. Danach gelten die aktuellen deklarativen Regeln
des Profilvergleichs und Codecs: S15-Installation mit lexikalischen Pfaden,
optionale F3-Auswahl, sämtliche P11-Record-/Loader-/Root-/Aliasformen,
sortierte eindeutige Modulnamen und deklarative Controls, vollständige I7/K8-
Kontexte sowie beide getrennten D9 mit der unveränderten Neuner-Zuordnung.
Eine deklarierte Inventur wird dabei nicht zur operativen Sollinventur.
Alle Formen werden vor Digestrechnung und Bindungsvergleichen abgeschlossen.
Die angekündigte Header-Bodylänge wird nur mit den beiden vollständig
validierten Neuner-Größensummen verglichen; keine Bodies werden gelesen.

Der Original Input82-Digest bleibt SHA-256 über das unveränderte benannte
Präbild aus `protocol`, `commit`, `raw27_binding`, `source_profile`, `nonce`
und der Liste vollständiger Deskriptor-Dictionaries. Der E4-K-Digest ersetzt
ihn nicht. Der begrenzte kanonische ASCII-Encoder speist diese eigenen
Metadatabytes in den gehaltenen Provider. Erst danach folgen I/K-Gleichheit
und Worker-/K-Selectorabgleich.

Der Provider stammt ausschließlich aus dem Export `hashlib` des erfolgreich
gebundenen Profilmoduls. Modulcache, Namespaces, Specs, Loader, Constructorcode
beziehungsweise native Constructoridentität sowie HASH-Klasse und Methoden
werden vor und nach der Rechnung gehalten und geprüft, auch nach Callfehlern.
Classnamespaces erlauben höchstens 256 exakte Stringkeys; ihre Formen werden
vor gezielten Lookup-/Methodenoperationen geprüft.
Ein Bindungsverlust dominiert den Callfehler; fremde Caches werden nicht
repariert. Unterstützt ist nur der vorhandene `_hashlib`-/`HASH`-Pfad mit den
geprüften exakten Formen. Andere Provider werden ohne Fallback abgelehnt.
Der synthetische Harness nutzt einen eigenen festen Functioncode und getrennte
Providerglobals. Diese Kohärenzprüfung attestiert weder Providerherkunft noch
eine tatsächlich gewählte Installation: die deklarierte Kontrollruntime
bleibt die ausdrücklich benannte Vertrauensannahme.

Ein Erfolg liefert `VALID_METADATA_SEMANTICS`, `NONE` und ausschließlich den
privaten vollständig rekonstruierten Payload. Ablehnungen liefern feste
Fehlercodes ohne Teilpayload. Alle Attestationsflags bleiben false und der
Quellenclaim bleibt `GENERATED_CONTROL_SOURCE_ONLY`. Callerabgleich,
tatsächliche Bodyhashes, Raw27, Consumption, Replay und Freigaben folgen erst
in ihren eigenen Schritten.

Root und unabhängiger Review prüften den vollständigen Quell-/Testfreeze vor
dem ersten isolierten Lauf mit `-I -S -B -X utf8`. Unter CPython 3.12.14 endete
er mit Exit 1: 108 Tests in 1,241 Sekunden, 106 PASS und zwei Fixturefehler,
kein ERROR oder SKIP. Die frühere Syntaxfixture enthält die abweichenden
Selectorwerte `worker-entry`/`synthetic` und wurde deshalb korrekt schon mit
`CONTEXT_FORM` abgelehnt, statt des erwarteten späteren `INSTALLATION_FORM`.
Im D9-Summenfall erzeugte die Fixture
auch eine angekündigte Bodygröße über 1 MiB; korrekt folgte bereits `BODY_LIMIT`
statt des erwarteten semantischen Summenfehlers. Beide Ablehnungen lieferten
keinen Teilpayload. Produktionscode und Quellenpins blieben unverändert.
Die engen Testkorrekturen setzen die Selector-Erwartung richtig und halten
beim D9-Summenfall eine separat gültige Header-Bodygröße. Ein weiterer Lauf
folgte erst nach erneutem Root-/unabhängigem Delta-PRE. Der zweite geänderte
isolierte Lauf bestand mit Exit 0: 108/108 PASS in 0,936 Sekunden unter
CPython 3.12.14, kein FAILURE, ERROR oder SKIP. Alle drei Ordinals und
vollständigen deklarativen Formen wurden gegen die tatsächliche Referenz
geprüft; ferner ursprüngliches benanntes Digestpräbild, späte Formfehler,
beide D9, Headerankündigung, Selector-/Bindungsabweichungen und unverifizierte
deklarierte Bodyhashes. Provider-/Code-/Cache-/Class-/Methodendrift sowie
Callfehler werden ohne fremde Getter oder Teilpayload geprüft. Drei ältere
Generatorbytes, vollständiges Scriptcap und false-Claims sind erhalten.
Gehaltene reale Cache-/Main-/Sysconfig-Sentinels und eigene Tempabsenz bestanden.
Kein alter privater Capture, nativer Auswahlbeleg, Preparepfad oder Nonce wurde
erneut ausgeführt; kein realer Profil-/Sysconfig-/Worker-/SQLstart.

Abschließende Toolpins sind RAW
`87f741eb566be85ab9c3e9918f3eda8f97d88fe2c90bc12d04e11e5125f4f00f`
und LF `fda2435b5ca55ffae9870903f8e17d5a396dd664b2cf37a367aed8025487f96d`
(44.906 LFbytes). Der korrigierte Test hat RAW
`b246ea614eb376e79cb227cace12a55b37ab0e59c3d9b0454384db9ee60a5f2c`
und LF `321b56bebfce2b4a27c7c7ef7cdbbaba808c4faac6d173af4e3ad3f2e8f58093`
(82.396 LFbytes). Die nach Pfad sortierte kompakte ASCII-JSONliste
`[[path,LFsha],...]` mit Trennzeichen `(',',':')` bindet beide Dateien als
SHA-256 `3a23e4a1f33ec0e71d86f9f6c6db3b95e4ea33d020705a710c30a739145173dc`.
Toolpins blieben über beide Läufe unverändert; die zwei Testkorrekturen wurden
vollständig auf den vorherigen Freeze zurückgerechnet. Abschließende Pins
blieben nach dem erfolgreichen Lauf unverändert.

Nächster reiner Offline-Vorschnitt ist der inline Profilreporter mit begrenzter
Form-/Fragmentdarstellung. Anschließend folgen Receiver- und Kanalteile. Erst
die endgültige vollständige Quelle darf mit separat vorgewählter operativer
S15-/P11-Inventur und dem gemeinsamen Fünf-Formen-/64-KiB-Gate abgenommen werden.
Parent-/Worker-, Loader-, Consumption-, Replay-, Cleanup- und G13-Methodengates
bleiben offen.

## 22. Reiner additiver Inline-Profilreporter

Der ausschließlich synthetische Vorschnitt ergänzt die fünfte reine Builderroute
`build_inline_report_control_bootstrap` um die private
`_inline_profile_report(header, metadata, scalars)`.
Ihre Eingaben sind gehaltene Header-/Metadatabytes und die drei vollständigen
skalaren Tupel aus `_project_scalars`: Auswahl mit vier Feldern, Installation
mit zwölf Feldern und vollständige P11-Modulzeilen. Die ältere Semantikroute
bleibt erhalten. Es erfolgt keine Profilaufnahme oder Ausgabe auf einen Kanal.

Die vollständige M-Syntax und sämtliche Scalarformen müssen vor dem Original-
Input82-Digest und Bindungsvergleichen abgeschlossen sein. Die tatsächliche
S15-Installation wird ausschließlich aus der separat gegebenen Auswahl und
Installation rekonstruiert; Controls und P11 kommen aus denselben Scalarinputs.
K stammt aus der vollständig validierten gehaltenen Metadata. Ein formgültiges
abweichendes Istprofil muss als abweichender Report erhalten bleiben. Der
Reporter führt keinen Callerabgleich durch und ergänzt keine Sollworkerfelder.

Die neue Route verwendet einen vollständigen begrenzten M-Parser-/Canonical-Repack-
Durchlauf. Nach vollständiger Formprüfung folgt das unveränderte
benannte Original-Input82-Präbild mit separat gebundenem Encoder und unmittelbar
geprüftem Provider. Der SHA-256 der R-JSONbytes ist ein zweites eigenes Präbild;
er ersetzt weder den Originaldigest noch den späteren K-Domain-Digest.
Encoderklasse, unmittelbar verwendete Funktionen, Codes und Defaults sowie
die gehaltenen Namespaces werden um die tatsächlichen Calls erneut geprüft.
Die Encoderinstanz hat genau die acht kanonischen Settings; Schattenmethoden
werden vor Dispatch abgelehnt. Verwendet wird die gehaltene Klassenfunktion.
Vier zusätzliche begrenzte JSON-Kodierungen betreffen Originalpräbild, R,
BEGIN und END; daneben stehen ein M-Repack und zwei SHA-Berechnungen.
Diese wiederholten begrenzten Scans sind zusätzliche Kosten und kein Nachweis
der späteren gemeinsamen operativen 20-Sekunden-Deadline.

R erhält seine eigene vollständige E4-Hülle mit Rolle `REPORTED`, lokalem
sortiertem eindeutigem Pool und dem Payload `(K,S15,controls,P11)`.
Alle Stringvorkommen, Integer und das ausschließlich an `specName` zulässige
Null bleiben verlustfrei. Es gelten gleichzeitig höchstens 256 Poolwerte,
256 Folgeelemente, acht Ebenen, 16.368 Knoten und 4.096 UTF-8-Bytes je Text.
Der begrenzte kanonische ASCII-Encoder darf zusammen mit dem festen 16-Byte-
Header höchstens 16.384 Bytes erzeugen. Kleine Einzelreports ersetzen nicht
die spätere gemeinsame Prüfung aller fünf Formen oder des 64-KiB-Kanalbudgets.

Die private Rückgabe enthält erst nach vollständig erfolgreicher Prüfung
sämtliche gehaltenen ASCII-Records: BEGIN, höchstens 19 `P|...`-Fragmente
und END mit SHA-256 der tatsächlichen R-JSONbytes. Je Fragment gelten 896
Payloadbytes und 32 Envelopebytes einschließlich LF; die allgemeine Zeilenkappe
bleibt 1.024 Bytes. BEGIN und END bleiben jeweils höchstens 256 Bytes.
Innere Pipezeichen sind unveränderte Payloadbytes; es gibt keinen zweiten
Escape-Layer. Fehler liefern feste Codes und keinen Teilreport. Ein eigener
Provideranker wird vor und nach der Rechnung geprüft, auch bei Callfehlern;
Bindungsverlust bleibt dominant. Die Kontrollruntime bleibt eine ausdrücklich
deklarierte Vertrauensannahme, keine Herkunfts- oder Installationsattestation.

Erfolg liefert `FORMATTED_PROFILE_REPORT`, `NONE` und ausschließlich das
private unveränderliche Recordtupel; Ablehnung liefert feste Codes und None.
Providerbindungsverlust dominiert Encoderbindungsverlust, dieser den Callfehler.
Alle Attestationsflags bleiben false und der Quellenclaim bleibt
`GENERATED_CONTROL_SOURCE_ONLY`. Vier frühere Builder, sämtliche 18 bisherigen
Tooldefinitionen und die 108 bisherigen Testmethoden sind AST-identisch.
Die fünf direkten Scriptimports, zwei tatsächlichen Controls und das
131.072-Byte-Scriptcap sind erhalten.

Root und unabhängiger Review lasen die vollständige Quelle und Tests sowie
die engen Korrekturen vor Ausführung. Dispatch-/Instance-/Keyworddefault-
Bindungen und unmittelbare Provider-PREs wurden bereits im Quellreview
korrigiert; die neue Fixture unterscheidet ausdrücklich gegebenes Scalar-None
von ausgelassenen Argumenten. Der lokale Nachweis umfasst einen einzigen Lauf
ohne Fehlversuch.
Der einzige autorisierte isolierte Lauf mit `-I -S -B -X utf8` bestand unter
CPython 3.12.14 mit Exit 0: 149/149 PASS in 1,946 Sekunden, kein FAILURE,
ERROR oder SKIP. Vor- und Nachpins blieben vollständig unverändert.

Die 41 neuen Methoden prüfen sämtliche tatsächlichen Scalarfelder und alle
drei Ordinals gegen eine unabhängige benannte Referenz und den tatsächlichen
REPORTED-Codec. Ein formgültig abweichendes Profil bleibt abweichend erhalten.
Späte Primitive-/P11-/F3-Fehler gehen Originaldigest-/Bindungsvergleichen vor.
Vollständige Frozenpaare, Singletons, gemischte Source-/Frozenrecords,
Kontrollinventur, Pool 256/257, tatsächliche Metadata 16.384/16.385 einschließlich
Header, Unicode, innere Separatoren und Fragmentgrenzen 896/897 sowie 18/19
sind geprüft. Die unabhängige Testzusammensetzung verwirft fehlende, doppelte
und umgestellte Records; dies ist kein produktiver Receivernachweis.
Provider-/Encoder-/Code-/Namespace-/Defaults-/Instanzdrift und dominante
Fehler-POSTs liefern keine Teilrecords. Gehaltene reale Cache-/Main-/Sysconfig-
und JSON-/Encoder-/Functionstate-Sentinels über die gesamten neuen Tests
sowie eigene temporäre Fixtureabsenz bestanden. Alte private Captures, native
Auswahl, Prepare und Nonces wurden nicht erneut ausgeführt; kein tatsächlicher
Profil-/Sysconfig-/Worker-/SQLstart.

Abschließende Toolpins sind RAW
`e12bdc060a63ab158746737f61ce8fb4324ec62715cb6ce0865eb16a88b969db`
und LF `a11ab6729d0a30b95f2a7d3f09d011f4f4fb1bbb4a252961ae301dfa85979b34`
(59.602 LFbytes). Der Test hat RAW
`1b37aa25d594f2e5f81a547900e43c9de0024e317fb7a3e9a48bd4688b423221`
und LF `3ee9bca9102506f02fa9b5e32a9fde41caf09fe144cfe845fd3b16f11f1442e9`
(118.703 LFbytes). Die nach Pfad sortierte kompakte ASCII-JSONliste
`[[path,LFsha],...]` mit Trennzeichen `(',',':')` bindet beide Dateien als
SHA-256 `77f4c656056f691205f0333253167f77987a302b9fe4718fc89d4638a93d1437`.

Nächster reiner Offline-Schnitt sind Receiver-/Kanalteile nach §16. Separat
vorgewählte operative S15-/P11-Inventur der endgültigen Quelle, gemeinsames
Fünf-Formen-/64-KiB-Gate und Parent-/Worker-, Loader-, Consumption-, Replay-,
Cleanup- und G13-Methodengates bleiben getrennte Folgearbeit.

## 23. Reine begrenzte Inline-Header-/Metadata-Aufnahme

Der additive Vorschnitt setzt ausschließlich den ersten Aufnahmehalt
aus §16.3 für bereits gehaltene synthetische Bytes um. Der Caller wählt die
feste Darstellung `pooled-combined-input-design/v1` ausdrücklich; es gibt
keinen Dispatch anhand eines empfangenen Tags und keinen Legacy-Fallback.
Die Eingabe ist ein exakt typisiertes Tupel mit höchstens 256 exakten
Bytesstücken von jeweils höchstens 1.024 Bytes. Ihre gesamte Länge bleibt
auf 16.384 Bytes einschließlich des festen 16-Byte-DGNC-Headers begrenzt.
Alle Typen und Längen werden vor Kopien, Parser- und Hashcalls geprüft.
Leere Stücke sind zulässig und zählen gegen dieselbe 256-Stück-Grenze.
Die sechste reine Builderroute heißt `build_inline_receive_control_bootstrap`;
ihre private Funktion ist
`_inline_receive_metadata_chunks(chunks, *, expected_format)`.

Nach der begrenzten Headeraufnahme müssen Magic, Metadata-, Body- und
Combinedcaps gültig sein. Die Gesamtmenge muss exakt Header plus deklarierter
Metadata entsprechen, bevor Metadatabytes kopiert und vollständig geprüft
werden. Angehängte Body- oder Commandbytes werden abgewiesen. Beide D9 und
sämtliche deklarativen Felder sowie der unveränderte benannte Originaldigest
bleiben vollständig erhalten. Erfolg darf ausschließlich atomar die gehaltenen
Header-/Metadatabytes und den vollständig validierten Payload zurückgeben;
eine Ablehnung enthält feste Labels und keine Teilrückgabe. Erfolg liefert
`VALID_RECEIVED_METADATA`, `NONE` und das private Tupel
`(header, metadata, vollständig_validierter_payload)`. Ablehnung liefert
`REJECTED_RECEIVED_METADATA`, ein festes Fehlerlabel und None.
Formatwahl, sämtliche Elementtypen und sämtliche Stück-/Gesamtlängen werden
in dieser Reihenfolge geprüft. Die Aufnahme umfasst höchstens je 256 Typ-,
Längen- und Headeriterationen, insgesamt höchstens 16 kopierte Headerbytes,
einen Join von höchstens 16.384 Bytes und einen Metadataslice von höchstens
16.368 Bytes. Danach läuft die vorhandene vollständige M-Semantik einmal.
Die Combinedcapprüfung bleibt erhalten; bei den gleichzeitig geltenden
Einzelcaps ist sie rechnerisch redundant und kein zusätzliches Bytebudget.

Die fünf bisherigen Builderrouten bleiben erhalten. Dieser Vorschnitt umfasst
keine stdin-/Pipeaufnahme, Callbacks, Bodyaufnahme oder Freigabe, keinen
Callerabgleich und keine Profilinventur. Seine endliche Stück-/Byteprüfung
und der vollständige M-Parser-/Repack-/Originaldigestdurchlauf sind kein
Nachweis der operativen 20-Sekunden-Deadline. K-Domain-Digest, Commands,
BODY_RELEASE, BODY_END, INPUT_COMPLETE, IMPORT_RELEASE und erwartetes EOF
sowie die tatsächliche Parent-/Worker-, Consumption-, Replay- und
Cleanupbindung bleiben getrennte Folgearbeit. Alle Attestationsflags bleiben
false; historische Captures und native Auswahl werden nicht wiederholt.

Root und unabhängiger Review lasen Quelle und Tests vollständig vor der
Ausführung. Die beiden eingefrorenen Dateien bestanden anschließend genau
einen autorisierten isolierten Lauf mit `-I -S -B -X utf8` unter CPython
3.12.14: 174/174 PASS in 2,905 Sekunden, Exit 0, kein FAILURE, ERROR oder SKIP.
Es gab keinen Fehlversuch oder Rerun. Alle 149 bisherigen Testmethoden und
sämtliche bisherigen Definitionen bleiben AST-identisch; die bisherige
Toolquelle und die Abschnitte §1–22 sind LF-byteidentische Präfixe.

Die 25 neuen Methoden prüfen Headerpositionen 0–16 mit führenden, inneren
und nachlaufenden Leerchunks, Einbyteheader und übergreifende Chunkgrenzen,
256/257 Stücke, 1.024/1.025 Stückbytes und tatsächliche gültige Metadata
16.384/16.385 einschließlich Header. Vollständige Typ-/Gesamtvorläufe gehen
Headerauslegung, Parser und Provider vor. Sämtliche drei Ordinals werden mit
einer unabhängigen benannten Referenz und dem tatsächlichen Formcodec
vollständig rückgewonnen. Positive Bodyankündigung bleibt deklarativ;
Truncation, angehängte Bodies/Commands, späte Fehler in der zweiten D9,
Originaldigest-/Kontext-/Selectorfehler und dominante Provider-POSTs liefern
keine Teilbytes. Unicode und innere Separatoren bleiben unverändert.
Wiederholte reine Auswertung ist kein Consumption- oder Replaynachweis.

RAW-/LF-Pins blieben vor und nach dem Lauf unverändert. Die eigenen
temporären Fixtureabsenzprüfungen und vollständigen Realcache-/Main-/
Sysconfig-/JSON-/Encoder-/Functionstate-Sentinels bestanden ohne Reparatur.
Kein tatsächlicher Profil-, Sysconfig-, Worker- oder SQLstart und kein
erneuter historischer Capture, Prepare, Nonce oder native Auswahl.

Toolpins sind RAW
`733a2ba9bb836b88e32ef4d16f64f1926c1018be666341db394eacac73ce72be`
und LF `9baf1b288918f78aa0d4316241ca0492b9966908dd8d4f31fe4e4cf8d8998b98`
(63.197 LFbytes). Testpins sind RAW
`d2b2f27cc0577d93c04c840bd2fb1d5e1712f92c36b0119a1bd6069a73fade47`
und LF `88a55fd3752c8f0224d821185057e9d7c19a6c29d1d819e359f9014357b2e841`
(138.318 LFbytes). Die nach Pfad sortierte kompakte ASCII-JSONliste
`[[path,LFsha],...]` mit Trennzeichen `(',',':')` bindet beide Dateien als
SHA-256 `e3a6148e70a90219fb0fafd0d90f68e8ca3f9b88c68ed734250c7cc4d790f69c`.

Nächster kleiner reiner Schnitt sind K-Domain-/Commandteile nach §16.3.
Tatsächlicher Kanal, vollständiger Callerabgleich, Bodyaufnahme und Freigaben,
separat vorgewählte operative S15-/P11-Inventur, Fünf-Formen-/64-KiB-Gate
sowie Parent-/Worker-, Loader-, Consumption-, Replay-, Cleanup- und
G13-Methodengates bleiben getrennte Folgearbeit.
