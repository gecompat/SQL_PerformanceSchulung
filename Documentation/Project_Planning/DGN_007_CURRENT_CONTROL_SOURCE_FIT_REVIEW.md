# DGN-007 – vollständige aktuelle Kontrollquelle vor einem Workerstart

Stand: 20. Oktober 2026. Basis
`966f2251bc301a1ac80997c591962f929a7a136c`, PR265 vollständig abgeschlossen.
Status `CURRENT_FULL_SOURCE_SCRIPT_LIMIT`.

## Gewählter endlicher Schnitt

Vor einer neuen operativen Bootstrapquelle ist deren bestehendes Scriptcap
von 131.072 Bytes relevant. Die fünfzehnte vollständige Inlinequelle wurde
bisher mit begrenzten synthetischen Profilquellen geprüft. Die aktuelle
vollständige Profilkontrollquelle enthält nun auch die unabhängig geprüfte
Auswahl-/Aufnahmeverbindung. Ein synthetischer Größenbeleg ersetzt den
vollständigen aktuellen Rawliteral-Fit nicht.

Ein Implementierungsowner, derselbe unabhängige Reviewer, höchstens drei
stabile Eingabe-/Dokumentationsstände, Checkpoint nach dem ersten, harte Grenze
drei einschließlich Auswahl-/Source-/Versuchsreview, einer gebündelten
geänderten Befundkorrektur, lokaler Rechnung, erforderlichen Gates, regulärer
Integration, FullTree/Sync und eigener Branchbereinigung. Verbrauch UNKNOWN.
Keine Wiederaufnahme eines ausgeschöpften historischen Scopes. Dieser Schnitt
betrifft neu die tatsächlichen vollständigen PR265-Profilbytes als Generator-
Input; er erweitert weder das Scriptcap noch die operative Ausführungsfreigabe.

## Konkreter Versuch und Vorabgrenzen

Nach unabhängiger Auswahl-/Source-PRE samt ausdrücklichem einmaligem Lauf-GO
den vorhandenen reinen Generator `build_inline_session_end_control_bootstrap`
einmal je separat identifizierter Darstellung aufrufen: tatsächliche Rawbytes
der aktuellen Arbeitsdatei sowie kanonischer Gitblob derselben Quelle.
Beide Bindungen mit Länge und SHA256 festhalten; identische Bytes deduplizieren.
Kontrollmodul: `Tests/Tools/dgn007_import_runtime_profile.py`.

Feste rein synthetische Locator-/Configinputs:
`/synthetic/control.py`, `cpython-312`, `/synthetic/stdlib/lib-dynload`.
Der Locator ist keine ausgewählte operative Installation. Nur den vorhandenen
Generator importieren; keine generierte Quelle kompilieren oder ausführen,
keine Profilquelle importieren, keine Stdlibmodule patchen, keine Worker,
Installationinventur, zusätzlichen Runtime-/Kandidatenprozesse, SQL oder
physische Runtimebeobachtung starten. Übliche Git-Leseaufrufe für den exakten
kanonischen Blob und die reine Python-Operatorausführung sind eingeschlossen.
Ein kurzer vorhandene APIs aufrufender lokaler Pythonaufruf genügt; kein neues
Auswertetool, keine neue Testsuite oder Reviewkette.

Positive/negative Einordnung: Der kleine synthetische Kontrollinput muss
weiterhin eine vollständige fünfzehnte Quelle innerhalb des Caps erzeugen.
Ein Profilinput oberhalb 131.072 Bytes muss vor Erzeugung mit `PROFILE_SIZE`
scheitern. Der konkrete vollständige Input darf entweder tatsächlich passend
erzeugt werden oder fest `SCRIPT_LIMIT` melden; eine Ablehnung ist kein PASS
für den operativen Fit. Größen und feste Fehler werden protokolliert, keine
Quellenbytes oder privaten Locator ausgeben. Bei `SCRIPT_LIMIT` keine weitere
Generatorwiederholung am selben Input, kein Filtern, Kürzen, Capwechsel oder
neuer nativer Start. Die unabhängig prüfbare Ablehnung wird als konkretes
Hindernis für die Folgequelle festgehalten. Eine Architekturkorrektur benötigt
anschließend einen eigenen endlich gewählten tatsächlichen Änderungsscope.

## Claim und Abschluss

Dieser Schnitt liefert ausschließlich den aktuellen Sourcegrößenbefund.
Selbst ein passender Scriptinput belegt keine vollständigen S15/P11-Erwartungen,
keinen Fünf-Formen-/64KiB-Fit, keinen konkreten operativen Scriptlocator und
keine Worker-/Loader-/Import-/UsedBytes-/Trust-/Methodenqualifikation.
Alle entsprechenden Abnahmen bleiben offen. Root-README unverändert.

Nur Planungs-/Nachweisdocs werden versioniert. Nach dem lokalen Versuch
unabhängige Einordnung des kompakten Resultats, danach aktuelle reguläre
Pflichtgates und Main-Abschluss. Kein erneuter Lauf unveränderter grüner
Profil-/Kanaltests; keine neue CI-Runtimesuite für reine Nachweisdocs.

## Tatsächlicher Größenbefund

Unabhängige Auswahl-/Source-/Versuchs-PRE auf Plan-SHA256
`390c55bc32d6b0b72cdd625cd0dad9c882c8cb5b0f1370bde30a066f6b0e8bde`,
Dokumentationsstand `a15713781722a051fa7535c6a40b9894b4ec9b27`:
keine offenen P1/P2/P3, ausdrückliches einmaliges Lauf-GO. Der gelesene
Generatorpfad verarbeitet Bytes und Templates, enthaltenes compile/exec bleibt
erzeugter Text. Keine eigenen Versuche des Reviewers.

Ein lokaler Python3.14.7-Aufruf am20.Oktober2026, bestehende API (Application Programming Interface; Programmierschnittstelle),
unveränderte Generator-/Profilquelle von Basis966f225, feste oben ausgewählte
synthetische Locator-/Configinputs:

| Input | Profilbytes | Tatsächliches Ergebnis |
|---|---:|---|
| Tiny `pass` plus LF |5 |BUILT; vollständige Quelle100245Bytes, innerhalb131072 |
| Größe131073 |131073 |REJECTED / PROFILE_SIZE |
| Arbeitsdatei mit CRLF |44542 |REJECTED / SCRIPT_LIMIT |
| Kanonischer Gitblob mit LF |43658 |REJECTED / SCRIPT_LIMIT |

Gebundene SHA256:

- Tinyprofil: `9f56e761d79bfdb34304a012586cb04d16b435ef6130091a97702e559260a2f2`.
- Tatsächlich erzeugte Tinyquelle: `9b93712dfdd65bb96df690609f63c94ba2d44ed30cbb91802721509a439ed7f7`.
- Oversizeprofil: `0c5c5c759aa8164f9fb53c471ff060903c99edcb520fb7d9cb4bf7a45755f1c2`.
- Arbeitsdateiprofil: `c920bd0fff6376ad23eba75a0589962f876fbf0a47bcb2bc5a917229f1f9a760`.
- Gitblobprofil: `612d5dc648deb43d7f9993a0b6bde4d50d0cc1276231833f2d336488bb61e8f7`.

Die beiden vollständigen Darstellungen sind byteverschieden und wurden je
genau einmal geprüft; keine Normalisierung oder nachträgliche Auswahlkorrektur.
Die beiden konkreten Fitergebnisse sind FAIL für eine operative Folgequelle.
Der Prozess beendet seine Größen-/Ablehnungsprüfung regulär mit Exit0; das ist
kein operativer PASS. Bereits eine Zwischenstufe kann abgelehnt haben, daher
werden für diese Inputs weder Gesamtlänge noch erzeugte Quellen-SHA behauptet.
Keine Profilquelle oder generierte Quelle importiert/kompiliert/ausgeführt,
keine Worker, neue Installation oder SQL-Ressourcen angelegt.

Checkpoint1 nach dem ersten gebündelten Versuch erreicht. Nun zwei stabile
Dokumentationsstände/max3, kein geänderter Eingabeversuch oder Rerun. Verbrauch
UNKNOWN. Die unabhängige semantische Einordnung des neuen Fit-FAIL ist
bestätigt; die reguläre Integration dieses begrenzten Nachweises steht aus. Nächste mögliche
technische Arbeit ist eine endlich gewählte Quellenarchitekturkorrektur bei
unverändertem Cap; sie wird hier weder implementiert noch vorab freigegeben.

Unabhängiger Dokumentationsdelta-Review auf
`c607d09669aa14fb64070a198686c15d74816cf5`: Nachweis konsistent, keine offenen
P1/P2/P3, reguläre Gates/Integration freigegeben. Keine Versuche wiederholt.
Der reine Nachweisschnitt ist sachlich geschlossen; die operative Route bleibt
wegen des belegten Fit-FAIL offen. Dritter reiner Abschlussdokumentationsstand,
max3 erreicht, kein neuer Input oder Versuch; nur noch reservierter regulärer
Gate-/Integrations-/Cleanupabschluss dieses Scopes. Keine grüne Profil-/
Kanalsuite wird deshalb lokal wiederholt.
