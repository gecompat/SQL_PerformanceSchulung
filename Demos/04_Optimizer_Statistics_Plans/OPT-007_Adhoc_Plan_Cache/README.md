# OPT-007 – Begrenzte Ad-hoc-Cachebelegung und Planwiederverwendung

Diese Diagnoseübung zeigt, wie unterschiedliche Batchtexte eigene Einträge im
Plancache (Zwischenspeicher für Ausführungspläne) erzeugen können. Sie vergleicht
40 Batches mit eingebetteten Ganzzahlwerten mit 40 Aufrufen eines konstanten,
parameterisierten SELECT. Beide Arme liefern dieselben 40 Tupel `(k, k)`.

Der Literalwert steht in `DECLARE`, das Suchprädikat verwendet eine lokale
Variable. Das ist ein gezielter Vergleich von Batchtext-Wiederverwendung.
Lokale Variablen und gebundene Parameter liefern dem Optimierer unterschiedliche
Kompilierungsinformationen. Die Demo behauptet weder gleiche physische Pläne
noch eine allgemeine Speicherersparnis oder einen Laufzeitvorteil. Einfache
Literalprädikate können automatisch parameterisiert werden; unterschiedliche
Texte allein würden deshalb die beabsichtigte Aussage nicht belegen.

## Voraussetzungen und Grenzen

| Merkmal | Voraussetzung |
|---|---|
| Engine / Compatibility Level (Datenbank-Kompatibilitätsstufe) | 2019/150, 2022/160, 2025/170 |
| Erster Qualifikationsumfang | Developer, Linux/Docker; Prüfstand siehe Katalog |
| Sicherheitsstufe | YELLOW (gelb), ausdrücklich bestätigte eigene Wegwerfinstanz |
| Rechte | CREATE ANY DATABASE, Kontrolle über die eigene Datenbank; VIEW SERVER STATE auf 2019, VIEW SERVER PERFORMANCE STATE ab 2022 |
| Vorhandener Vollplanmodus | `optimize for ad hoc workloads = 0`, `OPTIMIZE_FOR_AD_HOC_WORKLOADS = OFF` |
| Werkzeuge | Python 3, externes Microsoft-Werkzeug `sqlcmd`; vorhandener Framework-Harness |
| Instanzprofil / Hostreserve | 2 Prozessorkerne, 3 GiB (Gibibyte) Instanzspeicher; Host mindestens 4 Kerne, 8 GiB RAM (Arbeitsspeicher), 5 GiB freier Speicher |
| Umfang | eine sequenzielle Session je Phase, 40 Datenzeilen, höchstens 80 Nutzabfragen |

Die Demo schaltet keine Ad-hoc-Option um und leert keinen Cache. Eine vorher
erkennbare ungeeignete Konfiguration ergibt `SKIP_CONFIGURATION`; ein erst nach
Neuanlage erkennbarer unerwarteter Datenbankmodus ergibt `FAIL_STATE` mit Cleanup.
Fehlende Rechte werden vor Setup als `SKIP_PERMISSION` ausgewiesen.
Windows, andere Editionen und reale Stubmodi (kleine Einträge ohne vollständigen
Plan) gehören nicht zur ersten Qualifikation.

## Schritt-für-Schritt-Anleitung

1. Im [zentralen Ausführungsleitfaden](../../../Documentation/HowTo/DEMO_EXECUTION_GUIDE.md)
   Arbeitsplatz, eigene Wegwerfinstanz und Anmeldung vorbereiten. Der dortige
   Aufrufer führt die Demo manifestbasiert aus:

   ```powershell
   Invoke-SqlPerfDemo -DemoId OPT-007 -Server $server -Authentication $authentication -Username $username -ConfirmIsolatedLab
   ```

2. Der Aufrufer führt Preflight, Setup, Baseline, Literalarm, Beobachtung,
   Parameterarm, Vergleich und Cleanup in dieser Reihenfolge aus. Jede Pflichtphase
   muss `PASS/OK` ergeben; ein Skip ist keine fachliche Abnahme.
3. In der Beobachtung die Plananzahl und Bytebelegung nach 20 und 40 Aufrufen
   ansehen. Im Vergleich stehen `OPT007_METRIC`- und `OPT007_RESULT`-Zeilen.
   Erwartet sind 20/40 Literalpläne und jeweils ein vollständiger Prepared-Plan
   (Plan für gebundene Parameter). Je Arm ergeben sich 40 Zeilen, 40 Schlüssel
   und die Payload-Summe 820. Jeder einzelne Wert wird zusätzlich exakt geprüft.
4. Die Phasen prüfen zunächst die vollständigen Metadaten und Tupel in T-SQL
   (Transact-SQL, SQL-Server-Skriptsprache). Die Versionsprüfung überführt erst
   danach die aggregierten Zahlen in den vorhandenen FWK-011-Ergebnisevaluator;
   [Erwartungsvertrag](Expected/result-contract.json). Rohe Querytexte oder
   Plan-XML (Extensible Markup Language; strukturierte Plandarstellung) werden
   nicht als Dateien exportiert.
5. Abschließend die Abwesenheit der eigenen Datenbank unabhängig prüfen, wie
   im Ausführungsleitfaden beschrieben. Bei Abbruch gilt der Recoverypfad unten.

## Ablauf und Interpretation

`dbo.CacheProbe` enthält genau `Id = Payload = 1..40`. Die beiden festen
Abfrageformen stehen in `lab.QueryText`; nur der intern erzeugte Schlüsselwert
im Literalbatch variiert. Der Kommentar mit normalisiertem Lauftoken bleibt je
Arm konstant. Der Parameterarm verwendet `sp_executesql` und stets `@Key int`.
Kein Warm-up, Recompile-Hinweis, Plan Guide oder Plan Forcing wird eingesetzt.

Die Baseline verlangt einen leeren eigenen Cacheumfang. Der Observer bindet
jedes Cacheobjekt gleichzeitig an tatsächliches `dbid` (Datenbankkennung) aus
Planattributen, Lauftoken, Arm und vollständigen exakten Batchtext. Je Handle
wird die Bytebelegung einmal gezählt. Zusätzliche Templates, Shells (Verweise
auf automatisch parameterisierte Pläne), Stubs und fehlende Metadaten scheitern.
Genau ein passender SELECT-Knoten mit physischem Planoperator ist erforderlich.
Die Engine lässt dessen abschließenden Strichpunkt weg; beim Prepared-Plan
enthält der XML-Statementtext zusätzlich die feste Parameterdeklaration. Diese
konkreten Darstellungen werden exakt geprüft, ohne allgemeine Textnormalisierung.
Die erwartete Variable `@Key` ist zulässig, zusätzliche automatische Parameter
sind es nicht. Diese kompilierten Pläne sind keine Actual Execution Plans mit
gemessenen Operatorlaufzeiten.

Der Parameterplan muss an beiden Messpunkten dasselbe Handle, dieselbe
Erstellzeit und Kompilierungsgeneration besitzen. Sein exakter SELECT-Zähler
`execution_count` muss 20 beziehungsweise 40 betragen. `usecounts` wird nicht
als Ausführungszähler verwendet. Konfiguration und Sessionkontext werden in
der eigenen Datenbank festgehalten und zwischen den Armen geprüft.

Die beobachteten Bytes beschreiben ausschließlich die eigene Cachemenge.
Größere oder kleinere Bytewerte sind beide zulässig. Keine feste Einsparquote,
Wachstumsrichtung zwischen den Armen oder Aussage über freien Instanzspeicher
ist Teil des Erfolgskriteriums. Verdrängung und Neukompilierung können die
Momentaufnahmen entwerten; dann scheitert der Pflichtnachweis sichtbar.

## Schutzgrenzen, Abbruch und Recovery

Jeder Nutztext ist auf 4096 UTF-16-Bytes (Unicode-Textkodierung), jede
Datenbankdatei auf 128 MiB (Mebibyte) begrenzt. Nach jedem Nutzaufruf wird die
gesamte eigene Cachemenge beider Arme gegen 16 MiB geprüft. Das ist eine
Abbruchschwelle und keine garantierte Spitzenspeichergrenze. Reguläre Phasen
haben zusammen höchstens 120 Sekunden, jede einzelne Phase höchstens 15
Sekunden. Cleanup besitzt separat 30 Sekunden. Überschreitungen stoppen weitere
Nutzabfragen; der Harness beendet eigene Prozesse und versucht Cleanup.

Setup und Cleanup prüfen die vollständigen vier Eigentumsmarker mit binärem
Vergleich und exakter Länge. Der Recoverypfad ist markergebunden; niemals anhand
des Namens allein löschen. Nach einem unterbrochenen Lauf zunächst den
[Recoveryabschnitt des Ausführungsleitfadens](../../../Documentation/HowTo/DEMO_EXECUTION_GUIDE.md#6-cleanup-prüfen-und-nach-abbruch-wiederherstellen)
lesen. Datenbank und bisherige Instanz erhalten, keinen Wiederholungs- oder
eigenständigen Löschaufruf starten und den Zustand klären. Der automatisch
versuchte Cleanup ist keine pauschale manuelle Recoveryfreigabe. Das allgemeine
Risiko einer gescheiterten erstmaligen
Markeranlage bleibt offen; hierfür wird keine pauschale Garantie behauptet.

Cleanup liest zuvor gebundene Handles und noch laufzugeordnete Cacheobjekte,
entfernt die eigene markierte Datenbank und prüft deren Abwesenheit sowie die
Abwesenheit der gebundenen Cacheobjekte. Restobjekte ergeben `FAIL_CLEANUP`.
Es gibt keine nachfolgende globale oder handlebasierte Cacheleerung. Der
ursprüngliche Fehler bleibt neben einem dominierenden Cleanupfehler sichtbar.

## Tests und Zuordnung

Die [Versionsprüfung](../../../Tests/Runtime/run_opt007.py) verlangt zwei
vollständige Lifecycles mit frischen Lauftokens je Zielversion und prüft
Eigentums-, Eingabe-, Ergebnis-, Kontext-, Budget- und Abbruchgegenfälle.
Der Prüfstand wird erst nach tatsächlicher Ausführung im
[Demo-Katalog](../../../Documentation/Demo_Catalog/README.md) und bei
TSK-016 (gezielte Curriculum-Ergänzungen) fortgeschrieben.

Lernziel `LO-M02-07` (Planwiederverwendung und Cachekontext), Claim `CLM-032`
(Cache-Schlüssel und zusätzliche Einträge), Demo `OPT-007`, Testprofil
`BOUNDED_FULL_PLAN`. Weitere historische OPT-007-Themen wie Compilation und
Recompilation bleiben außerhalb dieses begrenzten Schnitts. Die Quelle
LAB-PLAN-003 ist eine Ideenquelle; ihr Runner und ihre Cachebereinigung wurden
nicht übernommen.

## Primärquellen

Gelesen am 23. Oktober 2026:

- [Microsoft: Cacheobjekte, Bytes und usecounts](https://learn.microsoft.com/en-us/sql/relational-databases/system-dynamic-management-objects/sys-dm-exec-cached-plans-transact-sql?view=sql-server-ver17)
- [Microsoft: Planinhalt, Shells und flüchtige Handles](https://learn.microsoft.com/en-us/sql/relational-databases/system-dynamic-management-objects/sys-dm-exec-query-plan-transact-sql?view=sql-server-ver17)
- [Microsoft: Statementgrenzen und Ausführungszähler](https://learn.microsoft.com/en-us/sql/relational-databases/system-dynamic-management-objects/sys-dm-exec-query-stats-transact-sql?view=sql-server-ver17)
- [Microsoft: Datenbank- und Cachekontext](https://learn.microsoft.com/en-us/sql/relational-databases/system-dynamic-management-objects/sys-dm-exec-plan-attributes-transact-sql?view=sql-server-ver17)
- [Microsoft: sp_executesql und gebundene Parameter](https://learn.microsoft.com/en-us/sql/relational-databases/system-stored-procedures/sp-executesql-transact-sql?view=sql-server-ver17)
- [Microsoft: datenbankbezogener Ad-hoc-Modus](https://learn.microsoft.com/en-us/sql/t-sql/statements/alter-database-scoped-configuration-transact-sql?view=sql-server-ver17)
