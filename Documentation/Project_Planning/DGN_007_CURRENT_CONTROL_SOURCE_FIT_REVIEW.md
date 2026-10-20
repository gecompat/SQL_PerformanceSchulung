# DGN-007 – vollständige aktuelle Kontrollquelle vor einem Workerstart

Stand: 20. Oktober 2026. Basis
`966f2251bc301a1ac80997c591962f929a7a136c`, PR265 vollständig abgeschlossen.
Status `SELECTION_RUN_PRE_PENDING`.

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
