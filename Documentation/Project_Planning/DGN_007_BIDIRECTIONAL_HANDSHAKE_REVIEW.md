# DGN-007 – nativer bidirektionaler Phasenowner

Stand20.Oktober2026, Basis `0d851dc9f87915a4952ad6fae1fe0f269f94d5e7` nach
vollständig abgeschlossenem PR261. Status `LOCAL_PASS_PR_GATES_PENDING`.
Der menschliche kontinuierliche Auftrag autorisiert diese nächste eigene
endliche operative Welle; frühere geschlossene oder ausgeschöpfte Scopes
bleiben erhalten. PR261: acht finale PR-Gates und sechs Main-Workflows SUCCESS,
16/16 neue Methoden ohne SKIP, FullTree/Sync/eigener Branchcleanup bestätigt.

## Rahmen

Ein Implementierungsowner, höchstens acht stabile Quellen-/Testkandidaten,
Checkpoint nach zwei, harte Grenze acht. Enthalten: Auswahl-PRE, Source/Test-
PRE mit ausdrücklichem Lauf-GO vor neuen Suites/Nativeproben, höchstens sieben
gezielte geänderte Befundnachläufe, lokale betroffene Regressionen und neue
positive/negative Gegenproben, aktuelle PR-/Main-Gates und regulärer Abschluss.
Kein unveränderter grüner Wiederholungslauf oder alter Budgetreset. Höchstens
28 feste Nativefälle im neuen Harness; zusätzliche Ausführungen nur bei
geändertem relevanten Input/Finding oder fehlendem Gate innerhalb des Rahmens.
Token-/Kostenverbrauch UNKNOWN, keine monetäre Durchsetzung behauptet.

Neue Quelle `Tests/Tools/dgn007_handshake_channel.py`, neuer eigener Harness
`Tests/Static/test_dgn007_handshake_channel.py`. Gemeinsame neue private Seams
in `dgn007_session_channel.py` erhalten den vorhandenen öffentlichen Abschluss-
API und dessen Defaultpfad. Bestehende 15 Builder, pure Eingangsplanquelle,
SQL, neun Runtimequellen und synthetisches Ledger bleiben unverändert.

## Gehaltener privater Ausführungspfad

`run_handshake_channels(namespace, selections, *, limits=ChannelLimits())` hält
exakte eingefrorene Auswahlen aus Programmbytes und vollständiger separater
HandshakeInputSelection. Ein bis drei Slots in fester Runner/Proxy/Harness-
Präfixfolge; gemeinsame ganze I7/K8/D9-Bindung. Der bestehende pure Planner
prüft tatsächliche Metadata/neun Rawbodies, alle fünf E4-Formen und drei
Commandkosten vollständig innerhalb der gemeinsamen Transfercaps vor Start.
Äußere Kontroll-/Encoder-/Provideranker bleiben über diesen inneren Planner
und den ganzen Kanalweg gehalten; inneres Neubaselining heilt keinen Drift.
Alle tatsächlich benötigten Namespacehelper sind eigene gepinnte Funktionen.

Ein gemeinsamer privater Owner ersetzt keine öffentliche Callback-/Adapter-
API. Die alten öffentlichen Auswahlen/Reports bleiben kompatibel. Ausschließlich
der neue interne Driver liefert Vorbereitung und Phasensteuerung; fremde
Ereignistupel, Boolbelege oder öffentliche Reports erzeugen keine Transition.
Eine prozesslokale gemeinsame native Ownersperre umfasst Vorbereitung bis
nach Cleanup; Reentranz/zweiter nativer Call weist ohne neue Sideeffects ab
und markiert den aktiven Versuch sticky. Kein allgemeiner Host-/Thread-/
Sandboxschutz; frischer eigener isolierter Worker bleibt Voraussetzung.

Launcher wie PR260: gehaltenes Popen, gleiche Executable, feste
`-I -S -B -u -c`, keine Shell, frische eigene Prozessgruppe, nur LANG/LC_ALL C.
Neu ausschließlich eigene stdin-PIPE statt DEVNULL. stdin/stdout/stderr werden
nichtblockierend durch denselben Selector bedient. Vollständiger Gruppenstop,
WNOWAIT-Leaderanker, Reap, tatsächliche Pipeabschlüsse, frische Absenz und
Subreaper-Restore bleiben aus dem gemeinsamen Owner erhalten. stdin-Schluss
gehört zusätzlich zum Pipeabschlussbeweis. Unklarer Start bleibt UNKNOWN.

## Einmalige tatsächliche Phasen

Auswahl-PRE auf Basis `0d851dc9f87915a4952ad6fae1fe0f269f94d5e7` und Plan-SHA256
`1eca4712c7d684e8d595d5abb37acac2542a3aa9906eb68b9a251d310fbc7619` ohne offene
Befunde freigegeben. Gelesene Chunks einschließlich unvollständiger Zeilen
bleiben an ihrer beobachteten Phase gebunden; kein späterer Write darf frühe
Restbytes als zulässige Folgephase wiederverwenden. Unbeobachtbare Sender-
chronologie über getrennte Pipes wird nicht behauptet. §29 erhält ausdrücklich
die tatsächlichen DGNP-/R-Bytes aus §31, nicht die DGNC-Metadata des Inputplans.
Die Ownersperre greift vor vorbereitenden Callbacks; ein abgewiesener innerer
Aufruf löst ausschließlich seine eigene Rückgabe aus und hält den äußeren Stop.

1. Vor Start einmalige Reservierung; ausschließlich Header+vollständige M
   übertragen, gleichzeitig stdout/stderr drainieren. Jeder Schreibversuch
   zählt zum bestehenden I/O-Budget; nur tatsächlich bestätigte Bytezahlen
   zählen als Fortschritt. Teilwrites behalten ihren endlichen Offset.
2. Nach vollständiger M-Übertragung warten auf genau die Profilrecordfolge.
   P-Fragmente bleiben opak. Erst der vollständige bestehende §31-Matcher
   gegen separat gehaltenes R4 und der §29-BODY_RELEASE-Plan gegen ganzes K8
   erlauben die einmalige Reservierung des gehaltenen BODY_RELEASE vor Write.
   Ausgesendete Commandbytes müssen dem vorab geprüften Eingangsplan entsprechen.
3. Nach vollständig bestätigtem BODY_RELEASE genau die neun Rawbodies seriell
   ohne Normalisierung schreiben. Erst danach BODY_END vor Schreiben reservieren;
   nach dessen tatsächlichem vollständigem Write auf INPUT_COMPLETE warten.
4. Den tatsächlichen gehaltenen INPUT_COMPLETE vollständig mit bestehendem
   §30-Matcher gegen ganzes K8 prüfen. Erst danach IMPORT_RELEASE vor Write
   reservieren; nach vollständig bestätigtem Write stdin tatsächlich schließen.
5. Vollständige deklarative Loader-/SESSION_END-Folge, beide tatsächlichen
   stdout-/stderr-EOFs und eigener Exit0 bleiben getrennte Voraussetzungen.
   Vollmatcher bindet alle tatsächlichen stdout/stderr-Bytes. Erst erfolgreicher
   Gruppenabbau/Absenz/Restore und dominante letzte POSTs schließen den Slot;
   erst danach nächster Slot. Keine Heilung früherer Fehler oder Reservierungen.

Vorzeitige/duplizierte/falsche Phase oder Commandreihenfolge stoppt den ganzen
Versuch. Kein vorzeitiger Body-/Importversand, kein zweiter Start/Commandcommit,
kein Retry nach Teilübertragung oder unklarem Abschluss. No-progress, Exit,
EOF und Fehlversuche erneuern keine Budgets. Jede Eingangsphase hält private
volle Slot-/K8-/Quellenobjekte; neue Reports bleiben private-freie Diagnosen.
Der vorhandene synthetische Ledger wird nicht durch einen Native-Bool ersetzt
und erhält keine neuen operativen Receipts oder Replayauthority.

## Gemeinsame Grenzen und Gegenproben

Reguläre20s beginnen vor Vorbereitung, bleiben über Planner, Writes, Reads,
Matches, Exit und Cleanup unverändert. Cleanup höchstens10s kumulativ, während
reguläre Wallclock weiterläuft. Gemeinsam4096I/O-Schritte,64No-progress-Schritte,
65536 tatsächliche Ausgabe-/stderr-/Footerbytes,43stdoutzeilen je Slot und
1024Bytes je Zeile bleiben erhalten. Eingangsbytes und alle drei Commands
höchstens1064960 je Slot und3194880 global, ohne zusätzliches Commandbudget.
Writechunks höchstens4096, tatsächliche Writebytes werden zusätzlich gebucht.
Fehlerpriorität Cleanup/UNKNOWN vor Provider vor Encoder vor erster Ursache.

Native Abnahme ausschließlich auf Linux/CPython3.12 in frischem exklusivem
isoliertem `-I -S -B`-Worker, ein Thread, SIGCHLD Default, ohne bestehende Kinder.
Alle festen Testprogramme und etwaige Forkkinder sind alarmbegrenzt und
verlassen ihre Gruppe nicht. Private äußere Worker haben eigenen endlichen
Timeout; fehlender Bericht ist UNKNOWN, kein Cleanup-PASS. Jeder Bericht
wird gegen frische unabhängige Kinderabsenz und Subreaper-Readback gebunden;
keine Rohstderr-/Payloadausgabe auf Fehlerpfaden. Realcache, Provider,
Factoryzustand und vier Encoderfunktionen werden tatsächlich restauriert.

Feste Fälle: alle drei Rollen seriell, Null-/binäre/CRLF-Bodies, begrenzte
Teilwrites mit echtem os.write, Backpressure vor Metadataaufnahme bei gleichzeitig
offenen Ausgabepipes, kein vorzeitiger Body-/Importversand, falscher Profil-
caller/INPUT_COMPLETE-Nonce, doppelte/vorzeitige Phasen, früher stdin-Schluss,
fehlender Rückkanalfortschritt, IO-/Byte-/Zeitgrenzen ohne Reset, geerbte
Ausgabepipes nach Exit, beide EOFs vor Exit, nichtzero Exit, Reentranz vor
Start und nach Start, Bindungsdrift vor Commands, sticky Cleanupfehler und
kein Folgestart. Erfolg und feste Counter müssen den tatsächlichen Prozess-
und Byteweg belegen; synthetische Traces sind keine reale Loaderprovenienz.

## Aufwand und verbleibende Grenzen

Eigener nativer Workflow, cancel-in-progress:false, endlicher Jobtimeout und
vollständige Importclosure. Die geänderte gemeinsame Kanalquelle benötigt
auch die vorhandene16-Methoden-Kanalsuite lokal und in aktueller CI. Neue Suite
ebenfalls Windows portable/Linux native, explizite Plattform-SKIPs nur unter
Windows. Pure Planquelle unverändert: keine lokale grüne Wiederholung; deren
aktueller CI-Selector reagiert bereits auf die gemeinsame Quelle. Alte Offline-
und SQL-Selektoren bleiben unverändert; zentrale Safety-/Registry-/Governance-
Gates bleiben. Lokale Logs nur feste Zusammenfassungen/gezielte Fehlerstellen.

Kein realer DGN-Worker-, frischer S15/P11-, Quellenloader-/UsedBytes-, SQL-,
Trust- oder Methodenbeleg. Alle Attestationsflags bleiben false, Scope bleibt
PROJECT_SEMANTIC mit ausschließlich eigenen nativen Kanalbeobachtungen.
Tatsächlich aufgenommene Workerprofile und echte Loaderanbindung bleiben
nachfolgende separat ausgewählte Wellen. Auswahl-PRE ist ohne offene Befunde
freigegeben; C1 ergänzt gemeinsame private Seams/Ownersperre, eigenen Phasen-
driver und12Methoden mit28festen Nativefällen. Die Fixture begrenzt eigene
Pipepuffer erst nach gehaltenem Popen-Handle; eine erste gelesene Metadatabyte
verhindert dabei die Race zur anfänglichen stderr-Ausgabe. Ganze Eingänge,
Commands, Bodies und wirkliches Worker-stdin-EOF werden separat verglichen.
C1 `83d9f325abd539b60834312abbaf7746cb529981` gegen obige Basis ist unabhängig
vollständig ohne offene P1/P2/P3-Befunde geprüft und mit ausdrücklichem
einmaligem Source/Test-Lauf-GO bestätigt. Ein Quellen-/Testkandidat verbraucht,
keine Befundnachläufe. Die freigegebenen lokalen Läufe sind abgeschlossen:
Windows3.14.7 neue Suite drei portable PASS/neun native SKIP in0,345s und
alte Kanalsuite fünf portable PASS/elf native SKIP in0,204s; Linux3.12.3 neue
12/12 Methoden mit28 festen Nativefällen ohne SKIP in31,450s und alte16/16
ohne SKIP in22,584s PASS. Unveränderte pure Plansuite lokal nicht wiederholt.
Aktuelle finale Head-/Base-Gates, reguläre Integration, frische Main-Gates,
FullTree/Sync und eigene Branchbereinigung folgen vor vollständigem Abschluss.

Primärquellen, geprüft20.Oktober2026:
[CPython3.12 os.write](https://docs.python.org/3.12/library/os.html#os.write),
[Selectors](https://docs.python.org/3.12/library/selectors.html#selectors.BaseSelector.register),
[Popen/Pipes](https://docs.python.org/3.12/library/subprocess.html#subprocess.Popen).
Eigenes nichtblockierendes Multiplexing erhält den gehaltenen Leader bis zum
Cleanup und vermeidet den dokumentierten Pipe-Backpressurestillstand.
