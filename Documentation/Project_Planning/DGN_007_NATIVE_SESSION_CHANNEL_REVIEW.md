# DGN-007 – operative Kanal-, EOF-, Exit- und Cleanup-Anbindung

Stand: 2026-10-20, Basis `d4151093bdd4de115b660352345f3e5c47e9b650` nach
abgeschlossenem PR259. Status `SOURCE_TEST_PRE_PENDING`. Der Benutzer beauftragt
die operative Folgewelle und kontinuierliche autonome Weiterentwicklung mit
unabhängigem Review, lokalen Tests, aktuellen grünen Gates, Main-Integration
und Branchbereinigung. Alte geschlossene oder ausgeschöpfte Wellen werden
nicht durch Zurücksetzen ihrer Budgets wiederholt.

## Endlicher erster operativer Schnitt

Ein Implementierungsowner, höchstens drei stabile Quellen-/Teststände,
Checkpoint nach C1, harte Grenze C3. Ein Auswahl-PRE und ein Quellen-/Test-PRE
mit ausdrücklichem Lauf-GO vor dem ersten neuen Suitelauf; höchstens zwei
gezielte geänderte Befundnachläufe innerhalb derselben drei Stände. Tatsächliche
Token-/Kostenmessung ist unbekannt. Nach erfolgreicher Integration wird eine
neue priorisierte Folgearbeit separat mit endlichem Rahmen ausgewählt;
kontinuierliche Entwicklung ist kein unbegrenzter einzelner Versuch.

Gewählte eigene Quelle: `Tests/Tools/dgn007_session_channel.py`. Gewählter
Harness: `Tests/Static/test_dgn007_session_channel.py`. Der vorhandene Matcher,
alle fünfzehn Bootstrapbuilder, neun Runtimequellen, SQL, Manifeste und das
synthetische Parent-Ledger bleiben unverändert. Der neue Owner bindet zunächst
den Abschlussweg ab der gehaltenen Workerwahl; er ersetzt keine vollständige
Start-/Metadata-/Body-/Command-/Import- oder S15/P11-Inventur.

Die neue kontrollseitige API ist
`run_session_channels(control_namespace, selections, *, limits=ChannelLimits())`.
Eine Auswahl enthält exakte gehaltene `program: bytes`, vollständiges
`reported: tuple` und separat vollständiges `context: tuple`. Ein bis drei
Slots sind genau das Präfix Runner/Proxy/Harness mit gemeinsamer vollständiger
Commit-/Raw27-/Sourceprofil-/Nonce-/D9-Bindung. Alle Typen, Formen, semantischen
K8/D9/R4 und die gesamte Callerbindung werden vor Start geprüft. Gewählte
Programme sind vertrauenswürdig geprüfte, nicht ausbrechende Pythonprogramme;
keine Programm-/Host-/Sandbox- oder tatsächliche UsedBytesattestation folgt
aus dieser Callerwahl. Quellbytes bleiben höchstens 131072, keine Shell.

Der Source-/API-Schnitt gilt zunächst nur in einem frischen exklusiven
isolierten Linux-/CPython-3.12-Testworker mit `-I -S -B`, einem Thread,
SIGCHLD-Default und ohne vorhandene Kinder. Die Native-Abnahme verwendet nur
feste harmlose eigene Workerprogramme mit synthetischen vollständigen Traces.
Windows erhält portable Ablehnungs-/Form-/Budgetprüfungen; die Linuxfälle
laufen lokal unter WSL und nativ in der Linux-CI. Windows-Pipe- oder SQL-
Qualifikation wird nicht beansprucht.

## Tatsächliche Beobachtung und einmaliger Abschluss

Ein Parent besitzt alle gestarteten Popen-Objekte und ihre neu erzeugten
Prozessgruppen. Vor jedem Start wird dessen einmalige Reservierung gehalten;
unklarer Start ohne gehaltenen Handle bleibt UNKNOWN. stdin ist für diesen
Abschlussschnitt vorgegeben geschlossen. stdout/stderr sind getrennte echte
nichtblockierende Pipes. Vor Retention/Framing werden sämtliche tatsächlich
gelesenen Rohbytes gemeinsam gebucht; höchstens 65536 über alle drei Slots.
Nach Cap+1 keine Retention oder weitere reguläre Aufnahme. stdout bleibt als
Originalzeilen erhalten, maximal 43 je Slot und 1024 Bytes je Zeile, letzter
unvollständiger Record wird abgewiesen. stderr bleibt opak und privat.

Launcher: dasselbe `sys.executable`, feste Argumente `-I -S -B -u -c`,
`stdin=DEVNULL`, `stdout=PIPE`, `stderr=PIPE`, `bufsize=0`, `shell=False`,
`start_new_session=True`; Environment ausschließlich `LANG=C` und `LC_ALL=C`.
Der gehaltene Handle folgt unmittelbar auf Popen, ohne Kontextmanager,
poll/wait/communicate vor dem gebundenen Gruppenstop. Alle festen Programme
setzen einen eigenen Drei-Sekunden-Alarm, auch jedes Forkkind separat.

EOF wird ausschließlich aus tatsächlichem `os.read(...) == b""` für die
jeweilige gehaltene Pipe abgeleitet. Root-Exit wird mit `waitid`/WNOWAIT
beobachtet und nicht vor Cleanup gereapt. Ein Exit oder Footer ersetzt weder
zweites EOF noch Drain. Nach beiden EOFs und beobachtetem Exit0 wird der
gehaltene vollständige Matcher direkt mit den tatsächlichen Zeilen und stderr
aufgerufen. Der Owner hält äußere Encoder-/Provideranker vor Start bis nach
Matcher/Exit/Cleanup; innere Anker heilen keinen Drift. Kontrollnamespace,
gehaltene Funktionen und eigene Parserklassen werden auf Identität/Codezustand
geprüft. Die Kontrollruntime und ausgewählte Stdlib sind explizite Annahmen,
keine Abwehr beliebiger Host- oder Pythonmanipulation.

Eine gemeinsame reguläre 20-s-Deadline, 4096 technische I/O-Schritte und
64 No-progress-Schritte werden weder je Slot noch nach Exit erneuert. Kürzere
Testlimits sind möglich. Erneute Exitbeobachtung ist kein Fortschritt.
Cleanup hat insgesamt höchstens zehn Sekunden; eigener Gruppenstop, Reap,
geschlossene Pipes, unabhängige frische Gruppen-/Kinderabsenz und Restore
sind getrennt nötig. Popen-Erzeugung und Kernelscheduling sind kein harter
OS-Zeitbound. Der äußere Testworker erhält deshalb einen eigenen Timeout;
fehlender Abschluss bleibt UNKNOWN und liefert keinen Cleanup-PASS.

Nur der private neue Testworker aktiviert prozesslokal Subreaper, sichert den
Vorwert und restauriert ihn mit Readback. Der eigene Leader bleibt bis zum
genau zugeordneten Gruppenstop unreaped, damit sein PID/PGID-Anker erhalten
bleibt. Nach dem Reap erfolgen nur noch Absenzprüfungen, keine weiteren
Gruppensignale. Nur eigene adoptierte Kinder derselben Gruppe werden gereapt;
keine Namens-/PID-Suche und keine fremden Prozesse. Die festen Testkinder
verlassen ihre Gruppe nicht; beliebige ausbrechende Programme sind nicht
qualifiziert. Es gibt keine Wiederholung eines Starts oder Cleanupversuchs.
Späterer Absenz-/Recoveryerfolg heilt keinen ersten Cleanupfehler.

Der nächste Slot startet erst nach tatsächlichem Match, beiden EOFs, eigenem
Exit0 und erfolgreichem unabhängigem Cleanup des Vorgängers. Öffentliche
Reports sind private-freie Diagnosen mit festen Issues/Countern und höchstens
privat gehaltenen Matchresultaten, keine Ledger-/Replay-Authority. Status
`CLOSED_SESSION_CHANNELS` bestätigt nur diesen eigenen Abschlussweg.
`runtime_attested`, `trust_attested`, `import_used_bytes_attested` und
`method_approved` bleiben false. Fehler sind sticky; Abschlusspriorität bleibt
Cleanup/UNKNOWN vor Providerverlust vor Encoderverlust vor erster Ursache.

## Konkrete Gegenproben und Restore

Die neue Suite verwendet die tatsächlich gelesenen bestehenden Session-
Fixture-/R4-/K-/Traceoracles ausschließlich als Harnessmethoden, ohne alte
Testmethoden zu erben. Ein eigener äußerer frischer Testworker besitzt alle
inneren Kinder. Realcache, Encoder einschließlich `_make_iterencode`, vollständige
synthetische Providernamespaces und eigene Factoryzustände werden nach jedem
Fall tatsächlich verglichen. Temporäre Fixtures und Subreaper werden überprüft.

Erforderlich: alle drei Rollen seriell positiv; fragmentierte stdout-Reads,
opakes stderr nach Footer, volle Rohbyte-/Record-/Zeilengrenzen, geerbte Pipes
nach Root-Exit, beide EOFs vor Exit, Exit!=0, fehlender/zusätzlicher Footer,
Kanalbytes-/Hash-/Noncefehler, No-progress/Deadline/IO-Grenzen ohne Reset,
kein Folgestart nach Fehler, Provider-/Encoder-/Ownerdrift über den ganzen
Abschlussweg, sichere private Fehler und nicht geheilter erster Cleanupfehler.
Native Fehlerfälle müssen ihre tatsächlichen eigenen Prozesse vollständig
abbauen; der äußere Test prüft festen privaten-freien Bericht und Exitstatus.

## Prüfaufwand und kontinuierliche Fortsetzung

Ein eigener Workflow `dgn007-session-channel.yml` prüft genau den neuen Harness
auf Ubuntu/Python3.12. Selector: eigene Quelle/Test/Dokument/Workflow sowie die
tatsächlichen Matcher-/Harnessabhängigkeiten. Die alte Offline-Suite wird nicht
zusätzlich auf unveränderte Quellen getriggert; zentrale Privacy, Registry und
Governance bleiben erhalten. Native Prozesse erhalten `cancel-in-progress:false`,
regulären Cleanup und einen Jobtimeout. Geprüfte unveränderte Suiten werden
lokal nicht nochmals ausgeführt; aktuelle PR-/Main-Gates sind weiterhin nötig.
Das ist die begründete Aufwandsauswahl für diese neue Prozessgrenze.

Der bestehende 30-Minuten-Heartbeat wird auf den ausdrücklichen kontinuierlichen
Auftrag aktualisiert: laufende eigene Arbeit fortsetzen, nach Abschluss genau
die nächste priorisierte, freigegebene und endlich abgegrenzte Welle auswählen;
bei unverändertem Blocker still bleiben. Kein zweiter Owner, keine blinden
Retries oder Budgetresets und keine Umgehung echter Entscheidungsgrenzen.

## Nachweis

Auswahl-PRE durch den unabhängigen Reviewer auf Basis `d4151093bdd4de115b660352345f3e5c47e9b650`
und Plan-SHA256 `166f2869cecd0d9e230984fb6303a06cb6edb82162908eac2a665fb95de2b2ed`
freigegeben. Seine Bindungen sind in C1 umgesetzt: WNOWAIT/PID-/PGID-Anker,
getrennte echte EOF/Exitbeobachtung, kumulative Budgets, eigene Selbstbeendigung,
Subreaper-Restore und getrennte Absenz-/Pipebeweise. Der konkrete Quellen-/Test-
PRE mit ausdrücklichem Lauf-GO steht aus. Keine neue Suite oder native Probe
ausgeführt. C1 ist der erste neue Quellen-/Testkandidat; Kosten/Token unbekannt.

C1 `a6152d6827c28cebfda2172a376c8e7d3efd1dfc` erhielt vier P2, kein Lauf-GO:
letzte POST-Deadline fehlte, Noncegegenprobe änderte stattdessen eine Länge,
äußere Workerfehlermeldung enthielt rohes stderr und sechs transitive
Harnessimporte fehlten im Workflowselector. C2 bündelt die Korrekturen und
eine native letzte-POST-Zeitgegenprobe nach realem Lauf und Cleanup mit
kontrolliert um 21 Sekunden fortgerückter Uhr. Kein unveränderter Test wurde
wiederholt; weiterhin vor erstem Lauf. Gezielt unabhängiger C2-Delta-PRE nötig.
Produktions-Worker, Start-/Command-/Bodyintegration, tatsächliche Import-/Loader-
Provenienz, Fünf-Formen-/operative Inventur und SQL-/Incidentmethoden bleiben
Folgearbeit mit ihren eigenen Abnahmegates.

Primärquellen, geprüft am 20. Oktober 2026:
[CPython 3.12 waitid/WNOWAIT](https://docs.python.org/3.12/library/os.html#os.waitid),
[Popen](https://docs.python.org/3.12/library/subprocess.html#subprocess.Popen),
[Linux PR_SET_CHILD_SUBREAPER](https://man7.org/linux/man-pages/man2/PR_SET_CHILD_SUBREAPER.2const.html).
