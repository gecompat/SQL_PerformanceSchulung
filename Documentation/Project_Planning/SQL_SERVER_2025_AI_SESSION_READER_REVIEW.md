# TSK-004: unabhängiger Sessionreader-/Fehlervertrag nach PR234

PR234 vollständig geschlossen: sieben erfolgreiche Head-Gates/fünf erfolgreiche
Main-Workflows, Main 24478d42e674e9a99bd79add9d430f0155d82c82, vollständiger
Tree/FF-Synchronisierung, eigene Branches entfernt, 122 private Dateien
hashverifiziert gesichert und eigener Worktree tatsächlich archiviert.
Die VECTOR-Transportwelle bleibt nach C1 FAIL/UNKNOWN_STOP; kein weiterer
C2–C6-Lauf und keine weitere SQL-/Cleanupaktion gegen ihre alten Ressourcen.

## Reiner endlicher Folgeumfang

Ein Implementierungsverantwortlicher und enge unabhängige Rootprüfung.
Sechs relevante Sourcekandidaten, Checkpoint nach drei, Abbruch nach sechs;
nach erstem kohärent geprüftem Sourceabschluss Stop dieses Schnitts.
Nur öffentliche Primärquellen, vorhandene unveränderte C1-Akten und neue
eigene private Source-/Fixturedateien. Keine Kompilierung, CLR-/Driverprobe,
SQL-/Container-/Provider-/Modellaufrufe, Downloads, Restore oder Hosteffekte.
Andere Repositories unverändert. Kein impliziter Nativeentscheid.

Der eingefrorene Caller liest `SELECT @@SPID` mit `GetInt32(0)`. Dokumentierter
SQL-Rückgabetyp und strikter Gettervertrag werden für alle acht Sessionfelder
getrennt geprüft. Eine explizite passende SQL-Projektion oder Getterwahl
behebt den Sourcevertrag; Fixture-/Quellenkohärenz ist keine tatsächlich
gemessene Server- oder Driver-Typattestierung und rekonstruiert nicht die
ursprüngliche UNKNOWN_OR_UNCLASSIFIED-Exception.

Zusätzlich wird die Beobachtbarkeit von Fehlern innerhalb eines bereits
zurückgekehrten Readers geprüft: tatsächliche API-/Read-/Projektions-/Dispose-
Enden, sichere Exceptiontypen und volle begrenzte SqlErrorfelder müssen
getrennt bleiben. Kein Endzeitpunkt aus bloßen Flags; keine beliebige Exception
als Dimensionsbeleg. Server-/Transport-UNKNOWN bleibt sticky und sperrt
Folge-SQL; Originalrequest und alte Scope-/Budget-/Admitfiles bleiben readonly.

Eine verständliche öffentliche Reader-Lesehilfe trennt dokumentierte Typen,
konfigurierte Projektion/Getter, tatsächliche spätere Beobachtung und offene
Runtime. Private geänderte C#-Source und gezielte positive/negative Puretests
normal/geschützt unter `-O` werden vor Rootprüfung eingefroren; unveränderte
historische grüne Suiten werden nicht wiederholt. Privacy aller öffentlichen
Änderungen, aktuelle Head-/Main-/Tree-/FF-/Branch-/Sicherungs-/Worktreeclosure
bleiben erforderlich. Typisierte VECTOR-/NULL-/Dimensions-, SNI-/TDS-/SQL-,
volle TSK-004-/Workstreamabnahme und ursprüngliche Fehlerursache bleiben offen.
Der Schnitt begann SOURCE_PREPARATION_ONLY mit null neuen Runtimeeffekten;
Modell-/Tokenverbrauch UNKNOWN. Ein späterer nativer Schritt benötigt einen eigenen sichtbaren
geänderten Vertrag und aktuelle Source-/Compiler-/Nativegates; dieser reine
Schnitt erteilt keinen solchen Entscheid.

## C1: kohärenter SOURCE_ONLY-Abschluss

Die [öffentliche Reader-Lesehilfe](../HowTo/SQL_SERVER_2025_AI_SESSION_READER.md)
und `SRC-120` dokumentieren alle acht Projektionen/Getters samt NULL-Regel.
`CONVERT(int,@@SPID)` behebt den dokumentierten `smallint`-/`GetInt32`-
Sourcevertrag. Konfigurierte `nvarchar`-Längen bleiben getrennt von späteren
Driver-Basistypmetadaten; es gibt keine tatsächliche Größenattestierung.
Der ursprüngliche Exceptiontyp und die alte Fehlerursache bleiben UNPROVEN.

Ein neuer privater C#-Sourceentwurf ohne Main, Connection- oder Commanderstellung
erfasst Read-/Projektions-/Dispose-Schritte und Primary-/Disposefehler getrennt.
Ein Fehler hält ServerUnknown auch nach erfolgreichem Dispose; sichere
InvalidCast-/SqlExceptionfelder und expliziter Fehlercap verhindern eine
scheinbar vollständige Fehlermessung. Vier bytegenaue Guards bleiben unverändert.
Keine Kompilierung, CLR-/SQL-/Container-/Provider-/Modell- oder Hosteffekte.

Sieben neue Puremethoden normal, tatsächlicher PID 61124/poll 0/rc 0 in
0,253730 Sekunden; fünf geschützte Methoden unter `-O`, PID 51112/poll 0/rc 0
in 0,168936 Sekunden. Kein Timeout/End-UNKNOWN, ursprüngliche Rawkanäle und
getestete Sourcebytes erhalten. Acht ursprüngliche Akten-/Source-/Stop-Pins
unverändert; kein historischer Replay und keine alte grüne Suite wiederholt.
16 Guidelinks geprüft, kein fehlendes Ziel. Die enge unabhängige Rootprüfung
des Quellen-/Getter-/NULL-/Fehler-/UNKNOWN-/Guard-/Privacyumfangs bestätigt
ausschließlich SOURCE_ONLY-Kohärenz; reine Fixtures führen den C#-Reader nicht aus.

STOP_AFTER_COHERENT_SOURCE_ONLY_PASS nach C1, keine weiteren Sourcekandidaten
erforderlich. Aktuelle öffentliche Privacy und vollständige Integration folgen.
Typisierte VECTOR-/NULL-/Dimensions-, SNI-/TDS-/SQL- und volle TSK-004-/
Workstreamabnahme bleiben NOT_ESTABLISHED. Nach vollständigem Schnittabschluss
folgt die konkrete Sourcevorbereitung eines eigenen geänderten Callers;
dieser Reader-Schnitt allein erteilt weiterhin keinen Nativeentscheid.
