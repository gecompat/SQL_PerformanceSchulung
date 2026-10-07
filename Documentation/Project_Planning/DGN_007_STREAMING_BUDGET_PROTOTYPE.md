# DGN-007 – Synthetischer Streaming- und Budgetprototyp

| Merkmal | Wert |
|---|---|
| Stand | 2026-10-07 |
| Status | `IMPLEMENTED_SYNTHETIC`; lokale portable Prüfungen bestanden, Linux-Abnahme im eigenen CI-Job |
| Geltung | portabler Budgetkern und feste eigene Linux-Testprozesse |
| Grenze | keine Integration in die neun Runtimequellen oder das Quellenbundle |
| Methodengates | weiterhin offen; [Entscheidungspaket](DGN_007_METHOD_DECISION_PACKAGE.md) |

## Zweck und Aussagegrenze

Der heutige SQL-/Proxy-/Harnesspfad puffert vor der äußeren Collectorgrenze.
Der getrennte Prototyp untersucht Aufnahmegrenzen und gemeinsame Budgets an
synthetischen Daten. Er ändert keine SQLquellen, Manifeste, v1-Records, G13 oder
DEC-068 und startet keinen Bundle-Launcher, SQL oder Docker. Ein synthetischer
PASS attestiert keine tatsächliche Acquisition, Herkunft, Importclosure,
Actor-/CID-/Zugangs-/Hostgrenze oder Machbarkeit des vollständigen Incidentpfads.

[`dgn007_streaming_budget_prototype.py`](../../Tests/Tools/dgn007_streaming_budget_prototype.py)
enthält einen portablen Budgetkern und einen eng festgelegten Linux-Kindadapter. Der Adapter akzeptiert ausschließlich reviewte synthetische Szenarien,
keine freien Programme, Kandidatenargv, Imports oder Live-Targets. Seine
Prozessbeobachtungen betreffen nur die tatsächlich ausgeführten Testfälle.

## Budgetkern und gleichzeitige Obergrenzen

`run_budget(adapter, clock, input_bytes, limits)` verwendet unveränderliche
`Limits`, `Step`, `CleanupReceipt` und `Report`-Objekte. Der Adapter und die Uhr
sind ausdrücklich kontrollseitige Modellprämissen. Ein dauerhaft blockierender
unkooperativer Adapter lässt sich durch Nachprüfen seiner Rückgabe nicht hart
unterbrechen; Fakeclock-Tests sind kein OS-Deadlinebeleg.

| Grenze | erforderliche Behandlung im Prototyp |
|---|---|
| Input | Bytes/Form/Länge vor Start und vor Weitergabe prüfen |
| Output | stdout und stderr gemeinsam als Rohbytes vor Decode und Retention zählen |
| Teil-/Gesamtcaps | höchstens 16 KiB je technischem Read bzw. atomarem deklarativem Acquire-Step und 128 KiB gemeinsam; auch Fehlversuche zählen |
| Acquisition | acht Stages, höchstens zwei Versuche je Stage; Einzelzeit höchstens 2 s |
| Observer | aktive Kosten kumulativ höchstens 20 s; Schlaf separat im Gesamtelapsed |
| fachliche Polls | höchstens 64 Puls-/Rotationspolls; keine zusätzlichen Suchcalls |
| technische I/O | eigener endlicher Schritt-/No-progress-Cap, keine Gleichsetzung mit fachlichen Polls |
| reguläre Zeit | ein nicht erneuerter 145-/180-Sekunden-Pfad, einschließlich Parse und Drain |
| Cleanup | eigenes begrenztes Budget bis 60 s; erster Cleanupfehler bleibt dominant |

Dies sind Prüfkandidaten aus dem Methodenpaket, keine gemessenen SQL-Kosten oder
Budgetreservierungen. 16×16 KiB passen nicht in 128 KiB; 16×2 s passen nicht in
20 s aktive Beobachtung. Alle Teil- und Gesamtcaps gelten gleichzeitig.
Ein Retry darf weder Bytes noch Kosten oder Deadlines zurücksetzen. Auch vor
einer Exception verbrauchte Start-/Step-/Pausezeit wird vor dem separaten
Cleanup gebucht; ein Fehler verhindert keine abschließende Budgetprüfung.
Das Modell muss Grenzgleichheit, Overflow und widersprüchliche Uhren getrennt
prüfen. Integer-Nanosekunden vermeiden Floatzeitakkumulation; die monotone Uhr
belegt keine tatsächliche Ausführung oder Störlastfreiheit.
[Python monotonic_ns](https://docs.python.org/3.12/library/time.html#time.monotonic_ns).

Rohbyteaufnahme, kumulative Decodezulassung (`retained_bytes`), aktive
Observerkosten, gemessene Dauer expliziter Pausenbereiche und Gesamtdauer sind getrennte Berichtswerte.
Decodeausgaben werden verworfen; der Counter ist kein gemessener RSS-/Kernel-
oder aktueller Speichercap. Die UTF-8-Zustände und rohe Zeilenlängen bleiben
begrenzt. Eine gültige Schlusszeile ohne LF ist zulässig; unvollständige UTF-8-
Sequenzen am EOF werden abgelehnt. Dies prüft keine v1-/Recordsyntax. Ein erfolgreicher Root-Exit genügt nicht: Inputabschluss, beide EOFs,
verbleibender Drain und Cleanup brauchen eigene positive Belege. Bereits
bekannter Rootexit und Inputabschluss erneuern den No-progress-Zähler nicht.
Acquisitions sind hier atomare deklarative Steps; es gibt keine Integration
oder Kostenattestation einer tatsächlichen mehrschrittigen QS-Acquisition.
Ausgabe besteht ausschließlich aus festen Issues und synthetischen Countern;
keine Payloads, Rohfehler, Querytexte oder Secrets werden persistiert.
`runtime_attested` und `method_approved` bleiben `false`.

## Fester Linux-Adapter und eigener Cleanup

Der reale Adapter läuft ausschließlich in einem frischen synthetischen
Python-Testworker. Nur dieser Worker darf vorübergehend seine prozesslokale
Subreaper-Einstellung ändern; er sichert den Vorwert, restauriert ihn nach
eigenem Cleanup und prüft den restaurierten Wert durch Readback. App, Shell, Host und andere Prozesse werden nicht umgestellt.
Vorhandene fremde Kinder oder unklare Isolation sind ein Ablehnungsgrund vor
dem Start. Der Worker erzeugt ausschließlich eigene neue Prozessgruppen mit
festen Skripten und begrenzten synthetischen Bytes. Für die Backpressure-
Gegenprobe wird ausschließlich die eigene neue stdin-Pipe auf 4096 Bytes
angefordert begrenzt; die tatsächlich zurückgemeldete Kapazität muss kleiner
als der validierte synthetische Input von 16384 Bytes sein. Andernfalls wird
der Adapter mit eigenem Cleanup abgelehnt. Das Kind liest den Input nicht. Wartende feste Kinder enden außerdem nach drei Sekunden selbst.

Der eigene Leader bleibt bis zum Gruppenstop unreaped; `waitid` mit `WNOWAIT`
bewahrt diesen Zustand. Erst nach eigenem Stop werden Leader und übernommene
eigene Nachfahren der genauen neuen Gruppe gereapt. Fremde PID-/Namenssuchen
und fremde Prozessbeendigungen sind ausgeschlossen. Ein erfolgreiches Signal
ersetzt keine unabhängige Abwesenheitsprüfung; Reap-/Restorefehler bleiben
Cleanupfehler und werden durch spätere Recovery nicht geheilt.
Die festen Nachfahren dürfen die eigene Gruppe nicht verlassen; dies ist eine
Prämisse dieser Testskripte, kein Schutz gegen beliebige Programme.
[Linux Subreaper](https://man7.org/linux/man-pages/man2/PR_SET_CHILD_SUBREAPER.2const.html),
[Linux waitid/WNOWAIT](https://man7.org/linux/man-pages/man2/waitpid.2.html).

Nichtblockierende Pipezugriffe begrenzen die Aufnahme in den kontrollseitigen
Userspace. Sie begrenzen weder alle Kernelpuffer noch den Speicherverbrauch
beliebiger Erzeuger oder des Betriebssystems. Auch Prozesscreation ist auf
manchen Plattformen nicht durch eine Python-Timeoutprüfung unterbrechbar.
Ein Timeout oder eine CI-Cancellation ist deshalb kein allgemeiner harter
Gesamtprozesskettenbound und kein Cleanupbeleg. Der äußere Testworker hat
einen achtsekündigen Timeout und erwartet einen festen Report bis 4096 Bytes.
Fehlt dieser nach äußerer Unterbrechung, ist eigener innerer Cleanup unbekannt;
`cleanup_complete=true` wird nur aus vollständigem innerem Cleanup abgeleitet.
[Python subprocess](https://docs.python.org/3.12/library/subprocess.html).

Der echte Kindadapter ist Linux-spezifisch. Windows führt die portable
Budgetprüfung aus und kennzeichnet die Linux-Kindfälle vor jedem Start als
SKIP. `selectors` unterstützt Windows-Pipes nicht; dieser Schnitt behauptet
keine Windows-Prozesskettenabnahme.
[Python selectors](https://docs.python.org/3.12/library/selectors.html).

## Prüfverfahren und verbleibende Arbeit

```powershell
python -B Tests/Static/test_dgn007_streaming_budget_prototype.py
```

Die [Testdatei](../../Tests/Static/test_dgn007_streaming_budget_prototype.py)
verbindet Budgetgegenproben mit tatsächlichen eigenen Linux-Kindfällen:
cap/cap+1, Crosschannel-Overflow, UTF-8-/CRLF-Splits, Input-Backpressure,
geerbte Pipes nach Root-Exit, EOF/Drain, No-progress, nicht erneuerte Retrycaps
und Cleanupfehlerpriorität. Portable Mocks prüfen unter anderem Stop vor Reap,
verlorenen Leaderanker, Gruppenabweichung, vorhandene fremde Kinder, Restore-
Readback und unabhängige Absenz. Diese Mocks attestieren keine Linux-Syscalls.
Die tatsächliche lokale Prüfung unter Python 3.12.14/Windows bestand mit
59 PASS und sechs ausdrücklich Linux-spezifischen SKIPs (65 Methoden).
Der genaue CI-Head muss anschließend alle tatsächlichen Linuxfälle ohne SKIP
bestehen; CI-Abnahme wird am PR dokumentiert. Der [Workflow](../../.github/workflows/dgn007-streaming-budget.yml)
ist auf die vier eigenen Tool-/Test-/Doc-/Workflowpfade begrenzt; die bestehenden
Bundle-/Edge- und SQL-Workflowfilter bleiben erhalten.

Durchgängiges Streaming der heutigen SQL-/SQLcmd-/Proxy-/Harnesskette und ihre
tatsächlichen Kosten bleiben offen. Der Import-/Launcherentwurf bleibt
`PROPOSED`; PR68 und der zurückgestellte interne API-Schnitt erhalten keine
Freigabe. Nächster kleiner Schnitt ist die numerische Pipelinegegenprobe:
endliche Oraclepopulation → ausdrücklich deklarierte Fragmentrundung →
separat vorgegebener synthetischer Style3-Text → bestehende Consumergewichtung.
Exakte Partition, Rundungsabweichung und nicht injektives Consumerergebnis
werden getrennt geprüft; keine SQL-Konversionsemulation, kein Epsilon und
keine Methodenfreigabe. Bestehende Fraction-/Sättigungsgegenproben werden
gezielt wiederverwendet, ohne einen zweiten allgemeinen Evaluator zu bauen. Die spätere gemeinsam versionierte Umsetzung und neue
SQL-Runtime bleiben an tragfähige explizite Methoden-/Umgebungsentscheidungen
gebunden. Keine Incident-, Ursachen-, Mitigations- oder Capstonepromotion.
