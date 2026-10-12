# DGN-010: getrennte CI-Abnahme des begrenzten Kostencontrollers

Stand: 2026-10-12, TSK-013/TSK-011. Basis
`e15e821ebfe99ff23924fb2498e218f0dd1c0193`. Die [separate lokale öffentliche
Kostenqualifikation](SQL_SERVER_2025_AI_DGN010_COST_PUBLIC_REVIEW.md) aus PR210
ist begrenzte Entwicklungsevidenz. Die bisherige CI-Matrix prüfte andere DGN-010-
Scopes. Dieser Schnitt ergänzt eine tatsächliche Gateprüfung des Kostencontrollers;
keine neue SQL-Demo, Änderung von Messfenstern oder vollständige Performanceabnahme.

## Prüfung und Ausführungsgrenzen

[Neuer CI-Consumer](../../Tests/Runtime/run_dgn010_cost_profile.py) verwendet den
unveränderten öffentlichen Kostencontroller und denselben eigenen Docker-CI-Run.
Tatsächliche Engineprüfung über den bestehenden Targetvertrag vor den Profilen.
SQL2019/2022 müssen je zweimal SKIP_VERSION vor Setup liefern; SQL2025 muss je
zweimal den vollständigen begrenzten WARN-Record liefern. Ein Konfigurations-SKIP
gilt in diesem Kosten-Gate nicht als positive 2025-Qualifikation.

Jedes positive Profil bindet vier eigene CREATE-/DROP-Fenster, acht vollständige
1000-Row-Sourceaufnahmen, zehn vollständige Vollstates, echte Source-/DROP-51003-
Negativkontrollen, Record und vollständig neu berechnete Aggregate. Nach den beiden
positiven Profilen folgt genau ein kontrollierter Fehler nach tatsächlich bestandenem
Setup: erwartetes FAIL_EXECUTION, feste vollständige Recoveryphasen, frische
DB-Abwesenheit und keine verbliebenen eigenen SQLinputs. Nach erstem unzulässigem
Resultat wird kein weiteres Profil aufgenommen. Clientende UNKNOWN, Cleanupfehler
oder eigene Inputreste blockieren den Consumer.

Der bestehende DGN-010-Dockerproxy erhält ausschließlich Unterstützung für genau
ein `-y 0`: vollständige native VARCHAR-/NVARCHAR-Frames ohne Breitenkürzung.
Andere Werte oder doppelte Breitenoptionen werden vor Clientstart abgewiesen.
Primärquelle: [Microsoft sqlcmd-Optionen](https://learn.microsoft.com/en-us/sql/tools/sqlcmd/sqlcmd-utility?view=sql-server-ver15),
Abruf 2026-10-12; der eigene kontrollierte Vollframepfad bleibt separat zu prüfen.
Bestehender tatsächlicher Remote-Endframe und SQLCMDPASSWORD-only bleiben erhalten.
Keine Änderung des allgemeinen Proxys, keine neuen SQL-Secrets/Prozessargumente.
Consumerexport enthält nur geprüfte Ergebnis-/Kontrollcounts und Status, keine
Rohrecords, DB-/Requestidentitäten, Zeitstempel, Querytexte oder Modellinhalte.

## Aufwand, Tests und Integration

Ein Implementierungsverantwortlicher und ein enger unabhängiger Review der neuen
Abnahme-/Adapter-/Selektionsgrenzen. Zehn reine synthetische Consumermethoden und
elf bestehende Selector-Methoden bestanden; CLI-help/Compile startet keine Clients.
Ein zunächst falsch benannter Selector-Testpfad fand keine Datei; anschließend
tatsächlich richtige Selector-Datei geprüft. Kein Runtime-PASS aus diesen Tests.

Workflowänderung: ein zusätzlicher statischer Testschritt und ein Kostenconsumer-
Schritt innerhalb der bestehenden Drei-Versionsmatrix. Keine neuen Jobs, Dienste,
Downloads oder Provisionierungsketten. Kostenrecord-/Inputmodule sind jetzt echte
Runtimeabhängigkeiten und wählen bei ihrer Änderung verpflichtend native Gates;
reine Teständerungen bleiben statisch. Keine doppelte Privacy-/Foundationprüfung
im neuen Fachschritt. Bestehende SQL-Matrix-/Timeout-/Owncontainercleanupgates bleiben.

Je vollständiger Head- oder Main-Matrix sieben zusätzliche begrenzte Profilaufrufe:
zwei2019/zweimal2022 vorSetup-SKIPs, zweimal2025positive und ein2025Fault. Die
Consumer nutzen die ohnehin eigenen drei CI-Container seriell nach vorherigem
DB-Cleanup; keine zusätzliche Containerinstanz für den neuen Schritt. Head und
Integration bleiben eigenständige aktuelle Pflichtgates. Keine Wiederholung der
bereits grünen lokalen Nativeprofile und keine neue lokale Qualifikationsinstanz.

Sechs kohärente Quellenkandidaten maximal, Checkpoint3/hard6, höchstens sechs
Head-Matrizen plus eine finale Main-Matrix/maximal21 neue eigene CI-Container
über diesen Schnitt. Ein Retry benötigt geänderte Eingaben oder neue Evidenz;
am Hardlimit keine neue Admission. Modell-/Tokenverbrauch unbekannt. Eine grüne
Gateprüfung attestiert diesen bounded Kostenvertrag, keine volle Workerkosten-,
TP-PERF-, Nettonutzen-, Demo- oder Workstreamabnahme. WARN/PROPOSED und alte FAILs
bleiben sichtbar. Native CI-Ergebnisse sowie PR-/Head-/Main-/Tree-/FF-/Ownbranch-
Abschluss folgen vor regulärem Abschluss dieses Schnitts.

Ein konkreter P2 im engen Quellenreview betraf zu schwache Phasenbindung: ein
leeres Versions-SKIP-Tupel beziehungsweise doppelte Quellennegative konnten
deklarierte Flags ergänzen. Vor Native-Admission verlangt der Consumer jetzt
die exakt dreiteilige Versionsfolge und vollständige positive33-Phasenfolge
einschließlich der unterschiedlichen Quellen-/DROP-Negativen. Gezielte
missing/renamed/duplicate/FAIL-Gegenfälle bestanden; enge P2-Closure ohne offene
P1/P2 abgeschlossen. Reviewer führte keine Tests oder Runtime aus.
