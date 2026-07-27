# Laufzeitverzeichnisse

Dieses Verzeichnis ist der einzige vorgesehene repositorylokale Ablagebereich für flüchtige Daten, die durch Szenariosteuerung, Tests, Diagnosewerkzeuge oder lokale Entwicklungsabläufe entstehen.

Die Verzeichnisstruktur und ihre Dokumentation werden versioniert. Sämtliche erzeugten Inhalte werden durch die jeweiligen `.gitignore`-Dateien ausgeschlossen. Laufzeitdaten dürfen weder als Quellartefakte noch als dauerhafte Testevidenz behandelt werden.

| Verzeichnis | Inhalt |
|---|---|
| `Artifacts/` | exportierbare, aber flüchtige Diagnose- und Testartefakte |
| `Logs/` | lokale Prozess-, Runner- und Szenarioprotokolle |
| `Results/` | strukturierte Lauf- und Verifikationsergebnisse |
| `State/` | lokaler Szenario-, Lab- und Prozesszustand |
| `Temp/` | kurzlebige Arbeitsdateien und Zwischenprodukte |

Secrets, Kennwörter, reale Endpunkte und produktive Diagnosedaten dürfen auch innerhalb dieses Verzeichnisses nicht dauerhaft gespeichert werden. Werkzeuge sollen nach Möglichkeit betriebssystemseitige Temp-Verzeichnisse verwenden. `Runtime/` ist nur für Daten vorgesehen, die während eines lokalen Ablaufs gezielt im Repositoryarbeitsbaum verfügbar sein müssen.

CI-Workflows verwenden weiterhin `${RUNNER_TEMP}` und GitHub-Artefaktspeicher. Diese Daten werden nicht in `Runtime/` kopiert.
