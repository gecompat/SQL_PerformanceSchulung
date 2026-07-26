# PRS-011 – Vertrag für SlideKeys und Präsentationsvarianten

| Merkmal | Wert |
|---|---|
| Arbeitspaket | `PRS-011` |
| Status | `VALIDATED` |
| Stand | 2026-07-26 |
| Kanonisches Artefakt | PowerPoint-Masterdeck |
| Manifestpfad | `Presentations/variants/presentation_variants.json` |
| Schema | `Presentations/variants/presentation_variants.schema.json` |
| Folgearbeit | `PRS-012`, `TST-011`, danach `PRS-013` |

## 1. Zweck

Der Vertrag definiert die stabile Folienidentität, die kumulativen Tiefenprofile und die maschinenlesbare Auswahl für Custom Shows sowie abgeleitete `.pptx`-Varianten. Er verhindert, dass Foliennummern, manuell gepflegte Zweitdecks oder ausschließlich in der Binärdatei gespeicherte Auswahlentscheidungen zur fachlichen Quelle werden.

## 2. Grundregeln

1. Das Masterdeck ist die einzige bearbeitete Präsentationsquelle.
2. Jede Folie besitzt genau eine unveränderliche `SlideKey`.
3. Foliennummer und native PowerPoint-`SlideID` sind technische Zustände, keine projektweite Identität.
4. Das JSON-Manifest ist die diffbare Sollbeschreibung für Profile, Rollen und Abhängigkeiten.
5. Custom Shows im Masterdeck müssen dem Manifest entsprechen.
6. Eigenständige Varianten werden ausschließlich aus einer Kopie des Masterdecks erzeugt.
7. Änderungen an einer abgeleiteten Variante werden verworfen und nicht zurück in das Masterdeck übernommen.
8. Das Manifest enthält keine personenbezogenen, umgebungsbezogenen oder proprietären Informationen.

## 3. SlideKey

### 3.1 Format

```text
SLD-M<MODUL>-<NUMMER>
```

Für die bestehenden Module M00 bis M07 gilt beispielsweise:

```text
SLD-M02-015
```

Die Nummer ist eine dreistellige, innerhalb des Moduls nie wiederverwendete Kennung. Sie beschreibt nicht zwingend die aktuelle Folienposition.

### 3.2 Speicherung im Masterdeck

Die Speaker Notes enthalten genau einen maschinenlesbaren Marker:

```text
[SLIDE-ID: SLD-M02-015]
```

Ein Marker darf weder in sichtbarem Folientext noch mehrfach in den Notes auftreten. Beim Aufteilen einer Folie bleibt die ursprüngliche `SlideKey` bei der fachlich primären Nachfolgefolie; neue Folien erhalten neue Kennungen. Beim Entfernen einer Folie wird ihre Kennung nicht wiederverwendet.

## 4. Tiefenprofile

| Profil | Enthaltene Tiefe | Custom Show |
|---|---|---|
| `BASIS` | `BASIS` | `SQL Performance – Basis` |
| `STANDARD` | `BASIS`, `STANDARD` | `SQL Performance – Standard` |
| `VERTIEFUNG` | `BASIS`, `STANDARD`, `VERTIEFUNG` | `SQL Performance – Vertiefung` |

Die Profile sind grundsätzlich kumulativ. Eine Ausnahme ist nur über `profile_overrides` mit Begründung zulässig. Eine Begründung darf ausschließlich didaktische oder technische Abhängigkeiten nennen.

Die Tiefe wird von der Veranstaltungsform getrennt. Folienrollen steuern, ob dieselbe fachliche Tiefe als Vortrag, Demonstration oder Workshop verwendet wird.

## 5. Folienrollen

Zulässige Rollen sind:

| Rolle | Bedeutung |
|---|---|
| `INTRO` | Modul- oder Abschnittseinführung |
| `THEORY` | fachliche Herleitung oder Mechanismus |
| `DEMO_INTRO` | Ausgangslage und Beobachtungsauftrag |
| `DEMO_EXECUTION` | Durchführungsschritte oder Live-Cue |
| `DEMO_RESULT` | Evidenz, Vergleich und Take-away |
| `LAB` | praktische Aufgabe oder Arbeitsauftrag |
| `EXERCISE` | kurze Verständnis- oder Transferaufgabe |
| `SOLUTION` | Musterbeobachtung oder Lösung |
| `SUMMARY` | Zusammenfassung eines Abschnitts |
| `TRANSITION` | fachlicher Übergang zwischen Blöcken |
| `REFERENCE` | Quellen-, Glossar- oder Nachschlagefolie |

Eine Folie kann mehrere Rollen besitzen. `DEMO_INTRO`, `DEMO_EXECUTION` und `DEMO_RESULT` einer Demo bilden grundsätzlich eine gemeinsame Sequenz und müssen über `paired_with` verbunden werden.

## 6. Manifestfelder

### 6.1 Wurzelobjekt

| Feld | Pflicht | Bedeutung |
|---|---:|---|
| `schema_version` | ja | aktuell exakt `1` |
| `master_deck` | ja | relativer Repositorypfad zum Masterdeck |
| `master_sha256` | ja | Hash des Decks, für das das Manifest gilt |
| `profiles` | ja | genau `BASIS`, `STANDARD`, `VERTIEFUNG` |
| `slides` | ja | Objekt, indiziert über `SlideKey` |
| `build` | ja | Ausgabe- und Dateinamensregeln |

### 6.2 Folieneintrag

| Feld | Pflicht | Bedeutung |
|---|---:|---|
| `order` | ja | erwartete Position im Masterdeck |
| `module` | ja | `M00` bis `M07` |
| `depth` | ja | minimale fachliche Tiefe |
| `roles` | ja | mindestens eine zulässige Folienrolle |
| `title` | ja | neutraler, kurzer Kontrolltitel; nicht als Ersatz für Folientext |
| `claims` | bedingt | mindestens eine Claim-ID bei technischen Aussagen |
| `sources` | bedingt | mindestens eine Quellen-ID bei technischen Aussagen |
| `learning_objectives` | bedingt | Lernziel-IDs für Lehrfolien |
| `demos` | bedingt | kanonische Demo-IDs für Demo-/LAB-Folien |
| `requires` | nein | fachliche Voraussetzungen als SlideKeys |
| `paired_with` | nein | zusammengehörige Demo-, Aufgaben- oder Lösungsfolien |
| `links_to` | nein | erwartete interne Hyperlinkziele |
| `profile_overrides` | nein | begründete Abweichung vom kumulativen Profilmodell |
| `notes_required` | ja | ob Speaker Notes für die Rolle zwingend sind |

Technische Claims ohne Quellen sind unzulässig. Rein didaktische Übergangs- oder Abschnittsfolien dürfen leere `claims`, `sources` und `demos` besitzen.

## 7. Abhängigkeitsregeln

1. Jede `requires`-Referenz muss auf eine vorhandene `SlideKey` zeigen.
2. Eine erforderliche Folie muss in jedem Profil enthalten sein, das die abhängige Folie enthält.
3. Zyklen in `requires` sind unzulässig.
4. `paired_with` muss symmetrisch sein.
5. Demo-Ankündigung, Durchführung und Ergebnis dürfen nur gemeinsam ausgelassen werden, sofern der verbleibende Übergang ausdrücklich validiert ist.
6. `SOLUTION` benötigt mindestens eine zugehörige `EXERCISE`- oder `LAB`-Folie.
7. Interne Links dürfen in keiner erzeugten Variante auf entfernte Folien zeigen.
8. Eine Modul-Einführung darf nicht ohne mindestens eine nachfolgende Inhaltsfolie im Profil verbleiben.

## 8. Custom-Show-Regeln

- Die Namen sind fest: `SQL Performance – Basis`, `SQL Performance – Standard`, `SQL Performance – Vertiefung`.
- Die Reihenfolge entspricht standardmäßig `order` im Manifest.
- Jede erwartete `SlideKey` kommt in der jeweiligen Custom Show genau einmal vor.
- Nicht erwartete Folien dürfen nicht enthalten sein.
- Das Masterdeck bleibt vollständig; Custom Shows entfernen keine Folien.
- Eine abweichende Reihenfolge benötigt eine explizite, validierbare Manifestangabe.

## 9. Build-Regeln für eigenständige Varianten

Der Build arbeitet auf einer PowerPoint-Kopie des Masterdecks. Er muss:

1. den Masterdeck-Hash gegen `master_sha256` prüfen;
2. eine Kopie über PowerPoint Desktop erzeugen;
3. nicht enthaltene Folien in absteigender Positionsreihenfolge aus der Kopie entfernen;
4. interne Links und Custom Shows auf verbliebene Ziele prüfen;
5. die Ausgabe unter einem deterministischen Dateinamen speichern;
6. den Masterdeck-Hash nach dem Build erneut prüfen;
7. ein Buildprotokoll mit Profil, Master-Hash, Ausgabedatei, Folienzahl und Prüfergebnis erzeugen;
8. bei jedem Fehler die Ausgabe verwerfen.

Abgeleitete Dateien sind Releaseartefakte. Sie dürfen keine eigene fachliche Versionsgeschichte erhalten.

## 10. Dateinamenskonvention

```text
SQL_PerformanceSchulung_<Profil>_<MasterKurzHash>.pptx
```

Beispiel:

```text
SQL_PerformanceSchulung_STANDARD_3ad528c2.pptx
```

Der konkrete Releaseprozess kann einen Releasebezeichner ergänzen. Ein Zeitstempel allein ersetzt weder Master-Hash noch Releaseversion.

## 11. Validierungsregeln für TST-011

Der spätere statische Validator prüft mindestens:

- JSON-Syntax und Schema;
- eindeutige SlideKeys und Notes-Marker;
- Modul-, Tiefen- und Rollenwerte;
- kumulative Profile und begründete Overrides;
- referenzielle Integrität von Claims, Quellen, Lernzielen und Demo-IDs;
- azyklische `requires`-Beziehungen;
- symmetrische `paired_with`-Beziehungen;
- vollständige Demo- und Aufgabenfolgen;
- Custom-Show-Mitgliedschaft und Reihenfolge im Open-XML-Paket;
- interne Links und entfernte Ziele;
- Übereinstimmung von `master_sha256` und Masterdeck.

TST-011 darf das PowerPoint-Paket nur lesen und nicht neu serialisieren.

## 12. Abnahme PRS-011

`PRS-011` ist abgeschlossen, wenn dieser Vertrag und das maschinenlesbare JSON Schema vorliegen, Tiefenprofile und Rollen vollständig definiert sind, die Abhängigkeits- und Buildregeln eindeutig sind und `PRS-012` sowie `TST-011` ohne weitere Grundsatzentscheidung beginnen können. Diese Kriterien sind erfüllt.
