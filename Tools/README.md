# Tools

Dieser Bereich ist für wiederverwendbare Hilfswerkzeuge vorgesehen, etwa synthetische Datengeneratoren, Workload-Treiber, Metadatenprüfungen und Ergebnisvalidierung.

Ein Werkzeug muss Herkunft, Runtime, Abhängigkeiten, Lizenz, Eingaben, Ausgaben und Sicherheitswirkung dokumentieren. Drittanbieter-Tools werden klar als solche gekennzeichnet; mitgelieferte Wrapper dürfen keine Secrets oder realen Umgebungswerte enthalten.

## Vorhandene Werkzeuge

| Werkzeug | Zweck | Runtime | Abhängigkeiten | Wirkung |
|---|---|---|---|---|
| `build_adv009_slides.py` | Fügt die zehn `ADV-009`-Vertiefungsfolien additiv in das aktive Deck ein und schreibt die Fußzeilenpaginierung fort. | Python 3.12+ | ausschließlich Standardbibliothek (`zipfile`, `xml.etree.ElementTree`) | Schreibt genau eine Datei: `Presentations/Performance_Schulung_Chat_2026-07-23_2146_SQL_Server_Performance_Grundlagen.pptx`. Der Aufbau erfolgt in einer temporären Datei und wird erst danach verschoben. |

`build_adv009_slides.py` ist deterministisch: Zeitstempel neuer Archiveinträge sind festgelegt, Bezeichner werden über `uuid5` aus stabilen Namen abgeleitet. Zwei Läufe aus demselben Ausgangsdeck erzeugen byteweise identische Archive. Das Werkzeug ist idempotent und bricht gegen ein bereits erweitertes Deck kontrolliert ab; `--check` meldet diesen Zustand ohne Fehlschlag und wird in `.github/workflows/adv009-deck-integration.yml` als Dauerprüfung ausgeführt.

Jede Deckänderung erneuert die in `Tests/Static/validate_privacy_metadata.py` hinterlegte SHA-256-Freigabe. Sie ist nach `DEC-057` nur zulässig, wenn der neue Wert im selben Schnitt in `Documentation/Inventories/SLIDE_STATEMENT_REGISTER.md`, `Documentation/Inventories/SOURCE_MANIFEST.md` und `Documentation/Project_Planning/W2_007_REFINE_CLAIMS_REVIEW.md` fortgeschrieben wird.

