# DGN-007 – gemeinsame Child-I/O-Reserve vor Parentstart

Stand: 20. Oktober 2026. Basis
`e456c535bc7a75d72d5034587657f6bcb46a27dd`, PR269 vollständig geschlossen.
Status `C1_LOCAL_PASS_HEAD_GATES_PENDING`.

## Priorität und endlicher gemeinsamer Rahmen

PR269: neun finale PR-Checks/sieben frische Main-Workflows SUCCESS, neue16
Windows/Linux/Main und bestehende Report16 ohne SKIP PASS, unabhängiger Review,
vollständiger Treevergleich, sauberer Main-/origin-Sync und eigene lokale/Remote-
Branchabwesenheit bestätigt. [Abschlussbindung](https://github.com/gecompat/SQL_PerformanceSchulung/pull/269).
Die Worker-Eingangsquelle besitzt1088 syscallnahe Operationen als harte eigene
Grenze. Ihre Parentvorbuchung aus dem gemeinsamen4096-Rahmen ist ausdrücklich
offen. Diese Kostenbindung ist der nächste eng ausführbare vorbereitende Schnitt.

Ein Implementierungsowner root, ein wiederverwendeter unabhängiger Reviewer,
höchstens vier stabile Source/Testkandidaten, Checkpoint1, harte Grenze4 mit
höchstens drei gebündelten geänderten Nachläufen einschließlich Auswahl-/Source-/
Testreview, Lauf-GO, lokaler Tests, CI, regulärem Merge, frischen Main-Gates und
eigener Branchbereinigung. Verbrauch UNKNOWN. Keine alten ausgeschöpften Scopes,
keine Wiederholung unveränderter grüner Tests, kein zweiter Owner.

## Konkrete Sources und Verhalten

`Tests/Tools/dgn007_session_channel.py`: bestehender privater `_Budget` erhält
eine einmalige feste Reserve für1088 Operationen je Slot, nur für ein bis drei
vollständig vorgeprüfte Handshakeslots. Exakte Integer vor Rechnung, Reservierung
vor Plattformprüfung, erster Reaper-/Launcher-/Selector-/Pipewirkung. Gesamter
Kohortbetrag vor dem ersten Start, keine slotweise Nachbewilligung. Unzureichender
Rahmen scheitert vor jedem Start; gescheiterte/erneute Reserveversuche sind im
selben Budget sticky. Keine Freigabe, Rückerstattung oder Wiederverwendung nach
Fehler/Exit/Cleanup. Der bestehende reine Sessionweg bleibt ohne diese zusätzliche
Handshake-Teilreserve und behält seine bisherige Zählung.

Jeder vorhandene Parent-I/O-Schritt prüft weiterhin seine ursprüngliche Deadline
und zusätzlich `actual_parent_io + reserved_child_io < limits.io_steps`, bevor
der Schritt gebucht wird. Das Gesamtcap bleibt4096; drei Slots reservieren3264,
höchstens832 Schritte verbleiben dem Parent. Kleine Callerlimits dürfen früher
ablehnen und erhöhen kein Budget. `io_steps` bleibt der tatsächliche Parent-
Zähler; ein zusätzliches rein diagnostisches `child_io_reserved` wird separat
im Channelreport ausgegeben. Keine Reservierung wird als gemessene Worker-I/O
oder erfolgreicher Childabschluss bezeichnet.

`Tests/Tools/dgn007_handshake_channel.py`: der bestehende eigene `_Driver`
veranlasst nach vollständigem vorhandenen Input-/Transferplan und vor irgendeiner
nativen Wirkung diese einmalige gesamte Kohortreserve am ursprünglichen Budget.
Keine frei wählbare Childcap/Receiptautorität und keine erneute Baseline. Alle
bestehenden Phasen/Bytes/Binding-/Cleanupprüfungen bleiben unverändert.

Die1088-Grenze gilt für die geprüfte Eingangsquelle aus PR269. Diese Änderung
verbindet ausschließlich die Parentkostenrechnung. Sie wählt die neue Quelle
nicht operativ aus und beweist nicht, dass beliebige Callerprogramme ihren
Childrahmen einhalten. Vor späteren Loader-/Footer-/weiteren I/O-Operationen
muss derselbe gemeinsame vollständige Kostennachweis bestehen. Vollständige
Worker-/Runtime-/SourceLoader-/Import-/UsedBytes-/Trust-/Methodenattestation,
separater Scriptlocator, unabhängig gewählte Installation/S15/P11, Fünf-Formen-
Fit und natives Gesamtlauf-GO bleiben offen. Keine Produktions- oder SQLfreigabe.

## Konkrete Test- und Reviewgrenzen

Neue portable Suite `Tests/Static/test_dgn007_child_io_reservation.py`, höchstens
zwölf Methoden. Eigene feste Budget-/Driver-/Controlmodelle und externe Zähler
ohne physische Prozesse, Pipes, Reaper, Signale oder echte OS-I/O. Unabhängige
Grenzarithmetik1/2/3Slots, genaue Restschritte, kumulativer Verbrauch ohne Reset,
exakte Bool-/Subclass-/Fremdformen vor Vergleich/Rechnung, zu kleiner Rahmen,
fehlgeschlagene/doppelte/verspätete Reservierung und dominante ursprüngliche
Deadline-/Ownerfehler. Öffentliche Parentaufnahme zeigt Vorbuchung vor Start
und vollständigen späteren Slotvorlauf. Statischer AST-Literalabgleich gegen
den festen1088-Wert der Workerquelle; keine Generator-/Suiteimporte dafür.

Bestehende zwölf Handshakemethoden/28 eigene Linux-Nativefälle und sechzehn
Sessionmethoden bleiben betroffene Runtimeconsumer. Nur ihr bereits ausgewählter
isolierter CPython3.12-Linux-Harness mit eigenen alarmbegrenzt nicht ausbrechenden
Testprogrammen, eigenen Prozessgruppen/Pipes, WNOWAIT/Reap/Absenz/Restore und
unveränderten20s-/10s-/4096-/64-/65536-Grenzen kommt als Regression infrage.
Keine neue Nativequelle und kein generiertes Main/PR269-Worker wird gestartet.
Falls die bisherige io_limit-Gegenprobe mit einem Schritt jetzt vor Start
scheitert, muss ihr Erwartungsnachweis die strengere Vorablehnung explizit
prüfen; keine andere Oraclelockerung. Neue Suite Windows/Linux, bestehende
Nativeconsumer Linux einmal nach ausdrücklichem Source/Test-Lauf-GO. Windows-
Native-SKIPs sind kein Linuxersatz und werden nicht als Abnahme gezählt.

Neuer enger Workflow für eigene Tests/Quellen, feste Workergrenzenquelle, eigenes
Planungsdokument und sich selbst; bestehende betroffene Workflows bleiben aktiv.
Erforderliche Registry-/Governance-/Privacy-/Projektchecks unverändert. Kein
SQL-/Dockerlauf, keine inventarisierte Installation, kein echter DGN-/Loader-
oder operativer Profilworker. Kein zusätzliches Modell, keine Voll-Logs.

Auswahl-PRE vor Implementierung, danach stabiler Source/Test-PRE mit ausdrücklichem
einmaligem Lauf-GO für genaue lokale/CI-Pfade. Lokale Befunde vor CI bündeln.
Erst nach unabhängiger Befundschließung und aktuellen grünen Head-/Base-Gates
regulär integrieren; danach Main-Gates, FullTree/Sync und eigene Branchbereinigung.
Keine Auto-/Admin-/Force-/Break-glass-Integration und kein Capwechsel.

## Auswahl und C1/Checkpoint1

Auswahl unabhängig ohne offene Befunde auf Basis und Plan-SHA256
`baea0d4417c5629731e7dff749224444dd44ce673f7e49b7abe82b5257557b17`
freigegeben. Implementierung ausschließlich innerhalb dieses Scopes.

C1 ergänzt am ursprünglichen Budget einmalige gesamte Childreserve und sticky
Fehlerzustand. Parentstep zählt tatsächliche eigene Schritte, prüft vor Buchung
deren Summe mit der Reserve gegen das unveränderte Limit. Gescheiterte Reserve
sperrt check/step/book/progress und jeden erneuten Reserveversuch; ursprünglicher
Timeoutcheck hat weiterhin Vorrang. Der tatsächliche eigene Driver reserviert
erst nach vollständigem prepare. Vor/nach Reserve prüft der ursprüngliche Owner
seine Bindung/Deadline, bevor Plattform und irgendeine native Wirkung folgen.
Channelreport ergänzt separate Diagnose, unveränderter reiner Sessionweg null.

Zwölf neue portable Methoden mit rein eigenen Budget-/Phasen-/Control-/Reaper-
und Launcher-Modellen prüfen Arithmetik, Stickyfehler und tatsächliche öffentliche
Ownerreihenfolge. Phasenstub ist nur Ordnungsnachweis; vollständige Inputsemantik
bleibt bei vorhandenen tatsächlichen Parentregressionen. Keine echten nativen
Funktionen oder Stdlib-Timeprovider werden gepatcht; eigenes Clockobjekt für
Deadlinegegenprobe. Native Handshakepositivfälle prüfen zusätzlich Reserve und
Gesamtsumme, io_limit prüft tatsächliche Vorablehnung ohne Start/Verbrauch.
Neue Workflowtrigger enthalten sämtliche tatsächlichen lokalen Quellabhängigkeiten
und statisch gelesene Childcapquelle; bestehende Nativeconsumer bleiben aktiv.

Checkpoint1: ein stabiler Source/Testkandidat/max4, keine Nachläufe, Verbrauch
UNKNOWN. Rahmen und Claims unverändert; noch keine neuen Suiteimporte/Compile-/
Exec-/nativen Proben. Unabhängiger Source/Test-PRE und ausdrückliches genaues
Lauf-GO für neue12 Windows/Linux, alte Handshake12/28Native und Session16 unter
Linux3.12 sowie entsprechende selektierte CI ausstehend. Keine neue Workerquelle,
operative PR269-Auswahl, Installation/Inventur, generiertes Main oder SQL.

C1 `ff290853d736bc6eea0d7a2fded1a5a3bb8905e2` unabhängig vollständig ohne
offene P1/P2/P3 und mit ausdrücklichem einmaligem genauem Lauf-GO. Neue12
Windows3.14.7 in0.008s und Linux3.12.3 in0.022s PASS; bestehende Handshake12
mit allen28 festen Nativefällen Linux3.12 in25.993s und Session16 in20.578s
PASS, jeweils ohne SKIP. Vollständige Kohortvorbuchung, Nullstart bei zu kleinem
Budget, getrennte Parentzählung und bisherige tatsächliche Cleanup-/Absenz-/
Restoregegenproben bestätigt. Keine operative PR269-Quelle oder neue Nativequelle.

Ein Sourcekandidat/keine Nachläufe; Produkt/Suite unverändert. Nur Ergebnisstand
ergänzt. Aktuelle Head-/Base-Gates, regulärer Merge, frische Main-Gates,
FullTree/Sync und eigene Branchbereinigung folgen. Verbrauch UNKNOWN. Keine
unveränderte Lokalwiederholung oder pauschale Runtime-/SQLfreigabe.
