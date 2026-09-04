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
| `.foundation-rule-cache/` | lokale, unversionierte Foundation-Fingerprints und Abhängigkeitsmetadaten gemäß `DEC-064` |

Secrets, Kennwörter, reale Endpunkte und produktive Diagnosedaten dürfen auch innerhalb dieses Verzeichnisses nicht dauerhaft gespeichert werden. Werkzeuge sollen nach Möglichkeit betriebssystemseitige Temp-Verzeichnisse verwenden. `Runtime/` ist nur für Daten vorgesehen, die während eines lokalen Ablaufs gezielt im Repositoryarbeitsbaum verfügbar sein müssen.

CI-Workflows verwenden weiterhin `${RUNNER_TEMP}` und GitHub-Artefaktspeicher. Diese Daten werden nicht in `Runtime/` kopiert.

## Rule Context Cache

Die optionale Foundation-Capability verwendet ausschließlich `Runtime/.foundation-rule-cache/` für lokale Cache-Records. Der vorhandene Runtime-Ignore-Vertrag schließt den vollständigen Pfad aus der Versionsverwaltung aus. Cache-Records sind weder Projektquelle noch Validierungsevidenz und dürfen keine Regeltexte, semantischen Zusammenfassungen, Prompts, Secrets oder absoluten Hostpfade enthalten.

Nach einer vollständigen Regelanalyse wird der analysierte Zustand explizit aufgezeichnet:

```powershell
python .ai/foundation/rule_context_cache/rule_context_cache.py record `
  --repository . --cwd . --cache-dir Runtime/.foundation-rule-cache --json
```

Vor einer späteren Änderungswelle wird der Zustand rein lesend geprüft:

```powershell
python .ai/foundation/rule_context_cache/rule_context_cache.py check `
  --repository . --cwd . --cache-dir Runtime/.foundation-rule-cache --json
```

Nur `CACHE_HIT` mit einer in der aktuellen Session tatsächlich vorhandenen Analyse unter dem exakten `analysis_key` erlaubt Wiederverwendung. `PARTIAL_INVALIDATION` verlangt das erneute Lesen der gemeldeten Quellen und ihrer transitiven Abhängigkeiten; `CACHE_MISS` oder Unsicherheit verlangt die vollständige Discovery und Analyse.
