# DGN-007 – Empfangene Metadata und tatsächlich aufgenommener Workerreport

Stand: 20. Oktober 2026. Basis
`84272af549d1c7c1320b5b1c77a55a4b721f8d18` nach vollständig geschlossenem PR267.
Status `C2_DELTA_PRE_PENDING`.

## Priorität und endlicher Rahmen

PR267 ist regulär integriert: zwölf finale PR-Checks/zehn frische Main-Workflows
SUCCESS, neue15 Windows/Linux und bestehende Consumer ohne SKIP PASS;
FullTree/Sync sowie eigener lokaler/Remote-Branchcleanup bestätigt.
[Abschlussbindung PR267](https://github.com/gecompat/SQL_PerformanceSchulung/pull/267).
Die neue Workerquelle passt mit vollständigen aktuellen Profilbytes. Ihr
Receiver und Reporter sind noch nicht mit der tatsächlichen Aufnahme verbunden.
§16.3 Schritte1/2 verlangen genau diese Verbindung vor einer späteren Pipephase.

Ein Implementierungsowner und derselbe unabhängige Reviewer. Höchstens sechs
stabile Source/Testkandidaten, Checkpoint2, harte Grenze6 einschließlich Auswahl-
und Source/Test-PRE, ausdrücklichem Lauf-GO, höchstens fünf gebündelter geänderter
Befundnachläufe, lokaler Tests, aktueller Gates, regulärer Integration und eigener
Branchbereinigung. Verbrauch UNKNOWN. Kein Reset des ausgeschöpften PR266-Scopes,
keine Wiederholung der dort abgelehnten Route oder unveränderter grüner Tests.

## Konkrete Auswahl

Additive siebzehnte API `build_inline_worker_report_control_bootstrap` im
vorhandenen Generator, gleiche vier Argumente wie die sechzehnte Workerroute.
Die bisherigen sechzehn Builder und ihre Bytes bleiben unverändert. Neues
festes Inlinefragment mit einmaliger privater Initialisierung unmittelbar nach
Kontrollladen und Workerprofilbindung, vor Metadataannahme. Die neue private
`_inline_observed_worker_report(metadata_chunks, *, token,
separately_known_filefinder_hook)` nimmt vollständige gehaltene Header-/Metadata-
Chunks an; keine I/O-Callbacks oder fremden Scalar-/Reportparameter.

Der bestehende vollständige Receiver prüft DGNC und M einschließlich beider D9,
I7/K8/W6, Originaldigest und sämtliche Formen. Erst aus dem vollständigen privaten
Empfangsergebnis wird exakt dessen W6 an die tatsächliche PR267-Aufnahme gereicht.
Nur deren private vollständige Scalars gehen an den bestehenden Inline-Reporter.
Die erzeugten vollständigen Records und die gehaltenen Aufnahme-/Empfangsobjekte
werden zusammen privat zurückgegeben; keine Körperaufnahme oder Freigabe.

Eine vor Metadata einmalige Bindung hält den eigenen generierten Namespace und
alle darin definierten Funktionen samt Code/Globals/Defaults/Keyworddefaults/
Closure-/Annotationzuständen sowie eigene Klassenwerte. Die vorhandenen begrenzten
Statehelfer und ein gemeinsames16368-Zustandslimit werden wiederverwendet. Nur
ausdrücklich benannte private Zustandszellen werden vom Namespacevergleich
ausgenommen; keine frei übergebene Ausschlussliste. Die alte private Kontroll-
bindung bleibt über Receiver, Aufnahme und Reporter dieselbe und wird auch nach
Fehlern dominant geschlossen. Provider-/Encoderanker über die gesamte Verbindung
halten; ein innerer neuer Anker heilt keinen äußeren Verlust. Keine Baseline aus
dem aktuellen Callbackzustand, keine Ersatzscalars oder öffentliche Receiptautorität.

Die neue Reportaufnahme reserviert ihren einmaligen Versuch vor der ersten
Aufnahmeoperation. Zweiter Aufruf, Reentranz oder Initialisierungswiederholung
scheitern dauerhaft; ein misslungener erster Versuch erlaubt keinen Retry.
Nach Formfehlern keine fremden Getter/Iteratoren/Vergleiche. Alle Fehler sind
feste Labels ohne Rohdaten oder Teilresultat; dominante Bindungsverluste bleiben
sichtbar. Die eigene private Reportbindung wird nach Fehler verworfen.

## Tests, CI und Grenze

Eigene portable Suite mit höchstens16Methoden; die sichere kleine PR267-Modell-
Fixture darf wiederverwendet werden, alte57-/Bootstrap-/Nativeharness werden
nicht importiert. Eigene synthetische Sys-/Cache-/Module-/Spec-/Loaderdaten,
eigene kopierte JSON-/Hashprovidernamespaces und eigene Encoderfunktionen;
keine Änderungen echter Stdlibmodule oder geteilter Methoden. Native Hash-
Typen dürfen als ausdrücklich angenommene Provider im eigenen Modell verwendet
werden, kein neuer physischer Profilread oder Kandidatenimport. Eigenes I7/D9/K8
und unabhängiger JSON-/E4-Oracle; keine Sollfüllung aus dem geprüften Reporter.

Positive tatsächliche Aufnahme samt vollständig rekonstruiertem R4 und allen
drei Rollen. Negative späte M-/I7-/W6-/P11-Formen, Chunk-/Metadata-/Quellencaps,
frühe Bindungsabweichung, gefälschte/fehlende Reportwerte, Code-/Defaults-/Closure-
und Klassendrift, Provider-/Encoderverlust in später Phase oder nach Fehler,
einmaliger Versuch/Reentranz und kein unzulässiger Callback. Mutationspunkte und
Zähler außerhalb fester Fehlerhüllen nachweisen; reale Cachemitgliedschaft und
alle fixtureeigenen Änderungen restaurieren. Tatsächlicher vollständiger neuer
Quellenfit innerhalb131072 und Rawliteralgleichheit, fünf direkte Imports,
kein neuer Parentmatcher/Projektimport, alte sechzehn Quellen unverändert.

Erst nach unabhängigem Source/Test-PRE samt ausdrücklichem Lauf-GO neue Suite
Windows3.14.7/Linux3.12.3; reguläre CI mit bestehenden betroffenen Consumern.
Eigene Modell-Compile-/Execpfade nur ohne generierte Imports/Main. Keine echte
Scriptausführung, operative Installation/volle Inventur, Pipe-/Workerstart,
Kandidaten-/DGN-Imports oder SQL. Die neue Quelle bleibt vor der tatsächlichen
stdin/stdout-Anbindung; Installation/S15/P11/Fünf-Formen-Fit und konkrete
Scriptlocatorwahl sind spätere eigenständige Gates. Worker-/Loader-/Import-/
UsedBytes-/Trust-/Methodenclaims bleiben offen. Alle Attestationsflags false.

Neuer eng ausgewählter Workflow nur für Generator/Profil/sichere Fixtures/neue
Suite/konkreten Plan/sich selbst. Vorhandene Consumer-Gates erhalten. Kein
SQLworkflow, Scanner-Selbsttest oder zusätzliches Reviewmodell ausgewählt;
grüne Logs nur als Status/Counts. Keine zusätzliche Automation.

## C1 und unabhängige Auswahl

Auswahl-GO auf Basis und Plan-SHA256
`d480d501fd7b5278d33be8c70b247a559dfb8e4e5177f7e72f1b34e580ef6c2e`,
ohne offene Auswahlbefunde. C1 setzt die neue siebzehnte Route um. Die private
Initialisierung hält Script/Kontrolle/Provider/Encoder vor Metadata. Genau drei
benannte eigene Zustandszellen sind ausgenommen; ihre exakten Werte werden
getrennt geschlossen. Der Aufruf reserviert auch malformed/reentrante Versuche.
Ein lokal gehaltenes Checkobjekt wird vor jedem Aufruf auf denselben Code und
Namespace geprüft; keine spätere Helferauswahl. Main ruft die Initialisierung
als Expression auf, damit danach kein weiterer globaler Resultateintrag die
gehaltene Scriptnamespace verändert.

Sechzehn neue Modellmethoden mit unabhängiger vollständiger R4-Byteoracle für
alle drei Rollen, eigenen JSON-/Hashprovidernamespaces und eigenen Encoder-
Funktionsobjekten. Die kleine PR267-Fixture erhält nur einen optionalen Builder-
Parameter; bisherige Defaultauswahl unverändert. Neuer eng ausgewählter Workflow;
bestehende Consumer bleiben erhalten. AST3/Methodenzählung16, unveränderter
gesamter alter16-Generatorpräfix und diff-check PASS; noch keine neuen Suite-
importe, Compile-/Execproben oder Tests. Unabhängiger Source/Test-PRE und
ausdrückliches Lauf-GO ausstehend. Ein Source/Testkandidat/max6, kein Nachlauf,
Verbrauch UNKNOWN; operative Grenzen unverändert.

## C2: Builtin-Klassen und separat versiegelte Entryautorität

C1 `7a8140f92db33312f9491fc828e6b0887121a0f9` unabhängig mit zwei P2,
ohne Lauf-GO: fehlender eigener `__module__`-Slot von `PyModule_Type` und eine
ersetzbare Globalzelle, die ihre eigene Checkautorität bestimmt. Keine weiteren
offenen P1/P2/P3. Primärgrundlagen für den Builtinfall sind CPython
[3.12.3](https://raw.githubusercontent.com/python/cpython/v3.12.3/Objects/moduleobject.c)
und [3.14.7](https://raw.githubusercontent.com/python/cpython/v3.14.7/Objects/moduleobject.c).

C2 überspringt ausschließlich Klassen ohne eigenen `__module__`-Slot; vorhandene
Slots werden weiterhin vor Vergleich exakt typisiert. Eigene Scriptklassen
bleiben vollständig gebunden und ihre späteren Namespaceänderungen scheitern.

Einmalige Initialisierung erzeugt nun eine private Entryclosure und versiegelt
darin die ursprünglichen Kontroll-/Provider-/Encoder-/Scriptanker sowie die
ursprüngliche Markeridentität. Der lokale Sealer wird nicht veröffentlicht.
Ein eigener einmalig gefüllter privater Scripthalter erlaubt den Selbstbezug
der vollständig geprüften Entryclosure; er wird vor Zugriff exakt typisiert,
nicht aus der Globalzelle übernommen und nicht in deren Marker veröffentlicht.
Die Globalzelle ist ausschließlich ein identitätsgeprüfter Marker, keine
Dispatchautorität. Ein neuer sechsteiliger Marker mit sämtlichen ursprünglichen
Checkobjekten scheitert ebenso vor Feld-/Attributzugriff und Receiver wie ein
Marker mit fremdem Checkgetter. Der Closure-Runner hält ursprüngliches Code- und
Globalsobjekt; kein späterer globaler Runneraustausch wird ausgeführt.

Die bestehende Gegenprobe enthält beide Markerersatzfälle mit extern geprüften
null Getter-/Call-/Profilreadzählern sowie zusätzliche Runner-/Factoryersatzfälle.
Weiterhin16Methoden, keine Test-/Compile-/Execausführung. Checkpoint2 erreicht:
zwei Source/Testkandidaten/max6, ein gebündelter Befundnachlauf. Delta-PRE und
ausdrückliches Lauf-GO ausstehend. Verbrauch UNKNOWN; operative Grenzen erhalten.
