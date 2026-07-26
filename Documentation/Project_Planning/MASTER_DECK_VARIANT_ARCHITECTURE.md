# Architekturplan – Masterdeck und abgeleitete Präsentationsvarianten

| Merkmal | Wert |
|---|---|
| Arbeitspakete | `PRS-009`, `PRS-011`, `PRS-012`, `TST-011` |
| Status | `PLANNED` |
| Planversion | 1.0 |
| Stand | 2026-07-26 |
| Kanonisches Artefakt | vollständiges PowerPoint-Masterdeck |
| Abgeleitete Tiefenprofile | `BASIS`, `STANDARD`, `VERTIEFUNG` |
| Primärer Präsentationsmechanismus | PowerPoint Custom Shows im Masterdeck |
| Eigenständige Dateien | reproduzierbar erzeugte Kopien, keine manuell gepflegten Zweitdecks |

## 1. Entscheidung

Das bestehende Masterdeck wird als einzige fachlich und gestalterisch verbindliche Präsentationsquelle erweitert. Unterschiedliche Schulungstiefen werden aus diesem Masterdeck abgeleitet. Eine eigenständige zweite Präsentationslinie mit separat gepflegten Folien ist nicht zulässig, weil dadurch Aussagen, Quellen, Speaker Notes, Demo-Zuordnungen und Korrekturen auseinanderlaufen könnten.

Die Ableitung erfolgt zweistufig:

1. Das Masterdeck enthält für die unmittelbare Durchführung native PowerPoint Custom Shows. Eine Custom Show ist eine benannte Teilmenge der Folien derselben Präsentation und ist daher für unterschiedliche Zielgruppen oder Tiefenstufen unmittelbar geeignet.
2. Wenn eine eigenständige `.pptx`-Datei benötigt wird, wird sie aus einer Kopie des Masterdecks erzeugt. Nicht zum Profil gehörende Folien werden in der Kopie entfernt. Das Masterdeck selbst wird dabei nicht verändert.

Microsoft dokumentiert Custom Shows ausdrücklich als Möglichkeit, Teilmengen einer Präsentation für unterschiedliche Zielgruppen zu verwenden. Das PowerPoint-Objektmodell stellt benannte Custom Shows, stabile `SlideID`-Werte innerhalb einer Präsentation, das Speichern einer Kopie sowie das Entfernen von Slide-Ranges bereit. Eine unbeaufsichtigte serverseitige Office-Automation wird von Microsoft dagegen nicht empfohlen oder unterstützt. Die Erzeugung eigenständiger `.pptx`-Varianten wird deshalb nicht als zwingender GitHub-Hosted-CI-Schritt geplant, sondern als kontrollierter, interaktiver Build auf einem Windows-Client mit installiertem PowerPoint. Statische Prüfungen des Open-XML-Pakets bleiben CI-fähig.

## 2. Variantenmodell

Die inhaltliche Tiefe ist von der konkreten Veranstaltungsdauer zu trennen. Ein Tiefenprofil legt fest, welche fachlichen Voraussetzungen und Internals enthalten sind. Ein späterer Zeitplan legt fest, welche optionalen Beispiele oder Übungen innerhalb dieses Profils tatsächlich durchgeführt werden.

| Profil | Inhalt | Ziel |
|---|---|---|
| `BASIS` | gemeinsamer Kernpfad, notwendige Begriffe, sichere Kerndemos und Diagnosemethode | SQL-Server-Developer und Analysten ohne tiefe Internals-Kenntnisse |
| `STANDARD` | `BASIS` plus ausgewählte Plan-, Statistik-, Index-, Concurrency- und Diagnosevertiefungen | reguläre Performance-Schulung mit technischer Herleitung |
| `VERTIEFUNG` | vollständiger freigegebener Bestand einschließlich Query-Optimizer-Internals, IQP, Memory Grants, Parallelität und Capstone-LABs | fortgeschrittene Schulung und Performance Engineering |

Die Profile sind kumulativ: `STANDARD` enthält grundsätzlich `BASIS`; `VERTIEFUNG` enthält grundsätzlich `STANDARD`. Bewusste Ausnahmen müssen im Variantenmanifest begründet werden. LAB-Folien werden zusätzlich über eine unabhängige Rolle gekennzeichnet, damit beispielsweise ein Vortrag und ein Workshop dieselbe fachliche Tiefe mit unterschiedlichem Übungsanteil verwenden können.

## 3. Stabile Folienidentität

Foliennummern sind nicht stabil, weil neue Folien eingefügt oder Abschnitte verschoben werden können. Jede Folie erhält deshalb eine unveränderliche `SlideKey` im Format `SLD-<MODUL>-<NUMMER>`, beispielsweise `SLD-M02-015`.

Die `SlideKey` wird in den Speaker Notes in maschinenlesbarer Form abgelegt:

```text
[SLIDE-ID: SLD-M02-015]
```

Zusätzlich werden Claim-IDs, Quellen-IDs, Demo-IDs und Lernziele im bestehenden Aussagen- und Traceability-Modell geführt. Die native PowerPoint-`SlideID` kann zur Laufzeit für Custom Shows verwendet werden, ist jedoch nicht die projektweite Identität. Das Variantenmanifest ordnet die projektweite `SlideKey` der im jeweiligen Masterdeck gefundenen Folie zu.

## 4. Variantenmanifest

Die fachliche Auswahl wird nicht ausschließlich in der Binärdatei verborgen. Ein versioniertes, diffbares Manifest wird unter `Presentations/variants/presentation_variants.json` vorgesehen. Es enthält mindestens:

```json
{
  "schema_version": 1,
  "master_deck": "Presentations/<Masterdeck>.pptx",
  "profiles": {
    "BASIS": {
      "custom_show": "SQL Performance – Basis",
      "include_depth": ["BASIS"]
    },
    "STANDARD": {
      "custom_show": "SQL Performance – Standard",
      "include_depth": ["BASIS", "STANDARD"]
    },
    "VERTIEFUNG": {
      "custom_show": "SQL Performance – Vertiefung",
      "include_depth": ["BASIS", "STANDARD", "VERTIEFUNG"]
    }
  },
  "slides": {
    "SLD-M02-015": {
      "depth": "VERTIEFUNG",
      "role": "THEORY",
      "module": "M02",
      "requires": ["SLD-M02-003"],
      "claims": ["CLM-XXX"],
      "sources": ["SRC-XXX"],
      "demos": ["OPT-015"]
    }
  }
}
```

Das konkrete Schema wird in `PRS-011` festgelegt. JSON wird bevorzugt, weil es ohne zusätzliche Bibliothek validiert werden kann. Das Manifest darf keine personenbezogenen oder umgebungsbezogenen Daten enthalten.

## 5. Ableitungsverfahren

### 5.1 Custom Shows im Masterdeck

Aus dem Manifest werden die drei benannten Custom Shows im Masterdeck erzeugt oder geprüft. Sie verwenden die Reihenfolge des Masterdecks. Eine abweichende Reihenfolge ist nur zulässig, wenn sie im Manifest ausdrücklich festgelegt und auf Übergänge sowie Voraussetzungen geprüft wurde.

Custom Shows sind der primäre Weg für Trainer, weil sie keine zweite Datei erzeugen, alle Notes und eingebetteten Inhalte unverändert nutzen und weiterhin den vollständigen Foliensatz als Rückgriff verfügbar halten.

### 5.2 Eigenständige `.pptx`-Varianten

Eine eigenständige Datei wird nur bei einem konkreten Bedarf erzeugt, beispielsweise für Teilnehmerbereitstellung, Versand oder eine klar abgegrenzte Veranstaltung. Der Build arbeitet auf einer durch PowerPoint erzeugten Kopie des Masterdecks. Anschließend werden alle nicht enthaltenen Folien in absteigender Folienreihenfolge entfernt. Das Verfahren kopiert keine einzelnen Folien in ein leeres Deck und vermeidet dadurch unnötige Risiken bei Notes, Layouts, Medien, Diagrammen, Beziehungen und eingebetteten Objekten.

Vorgesehene Dateinamen:

```text
Performance_Schulung_SQL_Server_Basis.pptx
Performance_Schulung_SQL_Server_Standard.pptx
Performance_Schulung_SQL_Server_Vertiefung.pptx
```

Die Dateien sind Build- oder Releaseartefakte. Sie werden nicht unabhängig bearbeitet. Jede Änderung erfolgt im Masterdeck und wird anschließend erneut abgeleitet.

### 5.3 Ausführungsumgebung

PowerPoint Desktop und das Office-COM-Objektmodell sind externe Microsoft-Tools. Die eigentliche `.pptx`-Ableitung wird auf einem interaktiven Windows-Client mit installiertem und lizenziertem PowerPoint ausgeführt. Sie wird nicht als unbeaufsichtigter Windows-Dienst und nicht als zwingender GitHub-Hosted-Runner-Schritt entworfen.

Ein user-defined Python-Validator darf das Open-XML-Paket statisch prüfen, Custom-Show-Definitionen und Notes-Marker lesen sowie Manifest, Quellen, Demo-IDs und Profilmitgliedschaft vergleichen. Der Validator darf die PowerPoint-Datei nicht stillschweigend neu serialisieren.

## 6. Abhängigkeiten und Übergänge

Jede Folie kann fachliche Abhängigkeiten deklarieren. Die Ableitung muss mindestens prüfen:

- jede referenzierte Voraussetzung ist im gleichen Profil enthalten;
- eine Kapitel- oder Abschnittsfolie bleibt nicht ohne zugehörigen Inhalt zurück;
- interne Hyperlinks und Custom-Show-Verknüpfungen zeigen nicht auf entfernte Ziele;
- Demo-Ankündigung, Demo-Durchführung und Take-away werden gemeinsam ein- oder ausgeschlossen;
- Quellen- und Versionshinweise bleiben bei der zugehörigen Aussage;
- ein ausgelassener Vertiefungsblock erzeugt einen fachlich verständlichen Übergang zwischen den verbleibenden Folien.

Wo ein direkter Übergang nicht verständlich ist, wird eine neutrale Brückenfolie im Masterdeck vorgesehen. Profilabhängige Sonderfolien außerhalb des Masterdecks sind nicht zulässig.

## 7. Qualitäts- und Abnahmekriterien

Für das Masterdeck und jede freigegebene Variante gelten folgende Prüfungen:

1. Jede Folie besitzt genau eine gültige `SlideKey`.
2. Jede `SlideKey` ist im Manifest genau einmal vorhanden.
3. Die Custom Shows im Masterdeck entsprechen der erwarteten Profilmitgliedschaft und Reihenfolge.
4. Die eigenständige Variante enthält genau die erwarteten `SlideKey`-Werte.
5. Notes, Quellen-IDs, Demo-IDs und Lernziele sind für alle enthaltenen Folien vorhanden und konsistent.
6. Interne Links, Abschnittsübergänge und Demo-Sequenzen besitzen keine entfernten Ziele.
7. Das Masterdeck bleibt nach der Ableitung byteweise unverändert.
8. Die Variante besteht ZIP-/Open-XML-, Render-, Font-, Alt-Text-, Notes-, Metadaten-, Privacy- und Branding-Prüfung.
9. Folienzahl und Laufzeit werden als Build-Ergebnis dokumentiert und nicht manuell im Plan festgeschrieben.
10. Eine Variante ist nur dann `RELEASED`, wenn sie aus dem dokumentierten Masterdeck-Hash erzeugt wurde.

## 8. Arbeitspakete

| ID | Größe | Status | Arbeit | Abschlusskriterium |
|---|---:|---|---|---|
| `PRS-011` | M | `PROPOSED` | SlideKey- und Variantenmanifest-Vertrag definieren | Schema, Tiefenprofile, Rollen, Abhängigkeiten und Validierungsregeln sind festgelegt |
| `PRS-012` | M | `PROPOSED` | Masterdeck mit SlideKeys und Custom Shows ausstatten | alle Folien sind stabil identifiziert; `BASIS`, `STANDARD` und `VERTIEFUNG` sind im Deck vorhanden |
| `PRS-013` | M | `PROPOSED` | kontrollierten interaktiven Varianten-Build erstellen | Kopie, Ausschluss, Save, Fehlerbehandlung und unverändertes Masterdeck sind nachgewiesen |
| `TST-011` | M | `PROPOSED` | statischen Variantenvalidator implementieren | Manifest, SlideKeys, Custom Shows, Abhängigkeiten, Links und Quellen werden ohne Office-Start geprüft |
| `TST-012` | M | `PROPOSED` | Render- und Vergleichsabnahme je Variante ergänzen | visuelle Integrität, Notes, Metadaten und Profilumfang sind nachvollziehbar geprüft |

## 9. Reihenfolge

Die praktische Umsetzung beginnt nicht mit dem Löschen oder Kopieren von Folien. Zuerst werden in `PRS-011` das Manifest und die Selektionsregeln festgelegt. Danach erhält das Masterdeck in `PRS-012` stabile SlideKeys und Custom Shows. Erst wenn diese statisch validiert sind, wird in `PRS-013` die optionale Erzeugung eigenständiger `.pptx`-Dateien umgesetzt.

Die fachliche Erweiterung des Masterdecks durch `ADV-009` verwendet von Beginn an die festgelegten Tiefenprofile. Neue Vertiefungsfolien werden daher nicht nachträglich aussortiert, sondern bei ihrer Anlage mit `SlideKey`, Profil, Quelle, Lernziel und Demo-Zuordnung registriert.

## 10. Quellen

- `SRC-052`: [Microsoft Support – Create and present a custom show](https://support.microsoft.com/en-us/powerpoint/create-and-present-a-custom-show)
- `SRC-053`: [Microsoft Learn – SlideShowSettings.NamedSlideShows property](https://learn.microsoft.com/en-us/office/vba/api/powerpoint.slideshowsettings.namedslideshows)
- `SRC-054`: [Microsoft Learn – NamedSlideShow.SlideIDs property](https://learn.microsoft.com/en-us/office/vba/api/powerpoint.namedslideshow.slideids)
- `SRC-055`: [Microsoft Learn – Presentation.SaveCopyAs method](https://learn.microsoft.com/en-us/office/vba/api/powerpoint.presentation.savecopyas)
- `SRC-056`: [Microsoft Learn – SlideRange.Delete method](https://learn.microsoft.com/en-us/office/vba/api/powerpoint.sliderange.delete)
- `SRC-057`: [Microsoft Support – Considerations for server-side Automation of Office](https://support.microsoft.com/en-us/visio/considerations-for-server-side-automation-of-office)
