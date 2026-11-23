# IDX-007-Demo-Paket – Laufzeitvertrag und Prozessaufwand

Stand: 2026-11-23. Zweck: den tatsächlich eingeführten Demoaufruf, seine
Qualifikationsläufe und den Zusatzaufwand gegenüber dem vorhandenen Pilot
festhalten. Die bestehende IDX-007-Methodenprüfung bleibt auf ihren bisherigen
Scope begrenzt; die Demo wird separat buildgebunden qualifiziert.

## Ausführung und Schutzgrenzen

- Ein manifestbasierter Framework-Aufruf wählt genau einen gepinnten SQL-
  Server-Build (Major 15, 16 oder 17) und startet einen Versuch.
- Das gekapselte `idx007_container`-Verfahren ist im Runner ausschließlich für
  IDX-007 zugelassen. Es akzeptiert keine frei definierbaren Befehle und
  verlangt die bestehende gelbe Isolationsbestätigung.
- Docker führt den Container ohne Netzwerk, Ports oder persistentes Volume mit
  2 CPUs und 4 GiB aus. Datenbank- und Containerbereinigung erfolgt im Pilot-
  `finally`; nach Harness-Timeout prüft eine getrennte Recovery exakt die pro Lauf eindeutige Eigentümerkennung und
  `NetworkMode=none`, bevor sie ausschließlich diesen Wegwerfcontainer
  entfernt.
- Das Package wird je Pull Request auf allen drei Build-Digests ausgeführt.
  Die Matrix serialisiert die Containerjobs. Jeder Build erhält einen Versuch;
  CI-Abdeckung des Piloten mit mehreren Wiederholungen bleibt von dieser
  einmaligen Demoqualifikation unterschieden.

## Tatsächlicher Verarbeitungsaufwand

| Bereich | Trigger und Beobachtung | Disposition |
|---|---|---|
| Statische Prüfungen | IDX-007-Workflow führt Parser-/Lebenszyklustests (19 bestehende plus 4 neue), Demo- und Katalogvalidatoren aus. Framework-Änderungen lösen zusätzlich den vorhandenen Framework-Contract-Workflow aus. | Getrennte Fragen: bestehende XE-Methodik, neue Adapter-/Katalogbindung, gemeinsamer Frameworkvertrag. Keine wiederholte Vollqualifikation pro Build für dieselbe statische Eingabe. |
| Runtime-Qualifikation | Drei digest-gepinnte Docker Builds, maximal ein Versuch je Build im Demo-Workflow; lokale Verifikation dauerte im beobachteten Windows-/Docker-Lauf etwa 65 s (2019), 81 s (2022) und 119 s (2025). | Drei Buildprofile sind die fachliche Versionsabdeckung. Matrixjobs bleiben serialisiert und erhalten getrennte Kurzzeitlogs. |
| Logverarbeitung | Normale Demoausgabe zeigt nur Lesson-, Build-, Wait/Page-, Resultat- und Cleanupmarker. Roh-Latchereignisse erscheinen nur mit explizitem `--show-output`; CI-Artefakte verfallen nach drei Tagen. | Verhindert standardmäßige Ausgabe vieler Einzelereignisse; Rohlogs nur für nachvollziehbare Diagnose. |
| Review / Delegation | Das Paket verwendet die vorhandene methodische unabhängige Prüfung; ein zusätzlicher Methodenreview wird durch die Packagingänderung nicht erneut ausgelöst. Code, Frameworkbegrenzung und PR-Diff bleiben regulär überprüfbar. | Keine zusätzliche Modell-/Reviewkette ohne konkreten neuen Methodenbefund. Kein Subagent-Einsatz. |
| Menschlicher Ablauf | Die Aufgabe verlangt eine autonom verwendbare Demo; die menschliche Generalprobe wurde ausdrücklich ausgeschlossen. | Nicht anwendbar für die technische Runtimefreigabe; der README-Lehrpfad liefert Moderation und Recovery. |

Die CI-Walltime, Token-/Modellkosten und kontoweite Ausgaben werden hier nicht
gemessen und bleiben unbekannt. Das lokale Laufzeitbudget ist die direkte
Beobachtung dreier einzelner abgeschlossener Läufe, keine allgemeine
Laufzeitgarantie. Die Workflow-Obergrenze bleibt 20 Minuten je Job, damit
Start-, Login- und Cleanup-Varianz eingeschlossen ist.

## Offene Entscheidung

Bis alle drei gepackten Läufe im PR bestehen, bleiben Demo und Katalog bei
`IMPLEMENTED`. Bei Fehlern sind nur die betroffenen Eingaben und ihr
fachlicher Fehlerpfad erneut zu prüfen. Ein erfolgreicher Lauf qualifiziert die
Demonstration für die drei konkreten Builds; er ändert weder
`METHOD_DRAFT`-Aussagen noch begründet er eine Performance- oder
Generalgarantie.
