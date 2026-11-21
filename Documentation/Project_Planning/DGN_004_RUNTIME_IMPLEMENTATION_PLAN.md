# DGN-004: Runtime-Implementierung und Qualifikation

Stand: 2026-11-21. Dieses Dokument hält den Entwicklungsplan und seinen
aktuellen Abschlussstand für den aktiven, begrenzten DGN-004-Aussageumfang
fest. Die Umsetzung und Runtimequalifikation sind innerhalb der freigegebenen
Grenzen abgeschlossen; die Integration steht noch aus. Der Umfang
bleibt `CLASSICAL_FORCING_AND_HINT_CONTROL`: Standard-Force/Unforce und H als
feste Hint-Kontrolle `CONTROL_ONLY`. Replay-Nutzung, Performancegewinn,
Kausalwirkung des Hints, gezielter Force-Fehler und SQL Server 2019 sind nicht
Teil dieses Vorhabens.

## Aktueller Stand

Die freigegebene Umsetzung ist vorhanden und die End-to-end-Qualifikation
wurde auf den beiden gepinnten SQL-Server-Builds bestanden. Jeder Lauf führte
alle neun R/H-Aufrufe, neun Query-Store-Flushes und 84 SQL-Batches innerhalb
der festgelegten Einzelbudgets aus; beide eigenen Container wurden nach dem
Cleanup entfernt. 2022 endete mit `PASS` nach 83,904 Sekunden, 2025 mit `PASS`
nach 71,735 Sekunden. Die Werte beschreiben ausschließlich die Laufdauer und
sind kein Leistungsnachweis. Der Abschluss gilt nur für
`CLASSICAL_FORCING_AND_HINT_CONTROL`.

Zur Erreichung des PASS wurden erkannte Integrationsfehler an SQLCMD-
Quelltransport und -Ausgabeformat, Kandidaten-Binder-Feldern, Showplan-
Statementtext, Query-Store-Chunktransport und der getrennten Bewertung von
Planidentität und `UsePlan` behoben. Die DGN-004-Statiksuite mit 120 Tests
(ein plattformbedingter Skip), ScriptDom, Registry, Foundation und der
Datenschutzscan geänderter Dateien sind bestanden. Die vorgeschriebene
unabhängige Sichtung der Runtime-/Cleanupsemantik und die Integration nach
`origin/main` stehen noch aus. Ein paketiertes Unterrichtsrelease und die unten
benannten zurückgestellten Erweiterungen sind nicht Bestandteil dieses
Runtime-PASS.

Die bisherige Forderung nach Abwesenheit fremder Hostlast ist für diesen
Aussageumfang kein notwendiges Gate: Es wird keine Zeit- oder
Leistungsmessung behauptet. Die beiden Zielversionen laufen jeweils sequenziell
in einem eigenen, digestgebundenen Container mit den festgelegten Ressourcen-
und Zeitlimits. Fremde Container oder Dienste werden weder geprüft noch
verändert. Die vorhandene Docker-Image-Identität, Edition, Build und
Kompatibilitätsstufe bleiben harte Vorstartprüfungen.

## Geplante Arbeitspakete

1. **Laufvertrag und Eintrittsprüfung präzisieren.** Den veralteten
   hostweiten Lastbezug im aktiven `classical_forcing_hint_control_plan` der
   kanonischen Registry als überholt markieren. Es gibt keinen Renderer für
   diese ausführliche DGN-004-Ansicht; der Registry-WI-Renderer erzeugt nur
   eine separate kompakte Arbeitstabelle. Deshalb bleibt `.ai/BACKLOG.md`
   unangetastet und der aktive Vertrag wird über die kanonische Registry und
   den aktuellen Ausführungsstand nachvollziehbar gehalten. Die Vorstartprüfung
   bindet Isolation an die kontrollierte Wegwerfinstanz, das exakte Image,
   eigene Ressourcen, sichere Eigentumsmarker und begrenzte Ausführung. R/H-
   Quellen, neun Aufrufe, Aussagegrenzen und Budgets bleiben unverändert.
2. **Datenbankaufbau und Recovery bereitstellen.** Ein ausführbares Setup
   erzeugt nur im eigenen Container die markierte DGN-004-Datenbank, das Schema,
   genau zehn Tabellen, 529 synthetische Zeilen, neun sekundäre Indizes und die
   beiden unveränderten Module. Es sichert die veränderlichen Datenbankoptionen,
   setzt Query Store und `LAST_QUERY_PLAN_STATS` nur in dieser Datenbank und
   protokolliert den rekonstruierbaren Ausgangszustand. Setup und Cleanup prüfen
   vor jeder Änderung bzw. Entfernung alle vier Eigentumsmarker exakt.
3. **Laufsteuerung implementieren.** Ein eng begrenzter Runtime-Runner
   orchestriert je Build exakt die festgelegte R/H-Folge. Er bindet jede Phase
   an einen Vorher-/Nachher-Kandidatensnapshot, den eigenen Aufruf, die
   Query-Store-Identität, Force-Ziel, tatsächlichen Plan, vollständigen
   Showplan-Transport und alle 768 Form-A-Tupel. Force-Fehlerzähler-Epochen,
   frische Kompilierung, eigener Ausführungszuwachs, H-Hintzustand und
   ausdrückliches Unforce werden je Aufruf erfasst. Mehrdeutigkeit, fehlende
   Daten, unerwartete Ausführungen und Transportfehler brechen fail-closed ab;
   es gibt keine Wiederholung und keinen alternativen Capturepfad.
4. **Ergebnis und Cleanup zusammenführen.** Der Runner liefert ein
   maschinenlesbares Ergebnis an den bestehenden Annahmeprüfer. Nach jedem
   begonnenen Setup wird Cleanup unabhängig vom Laufresultat versucht: beide
   Force-Zustände aufheben, ursprüngliche Datenbankoptionen wiederherstellen,
   nur die vierfach markierte eigene Datenbank entfernen und deren Abwesenheit
   unabhängig bestätigen. Cleanupfehler haben Vorrang als `FAIL_CLEANUP`.
5. **Statische und syntaktische Qualifikation ergänzen.** Synthetische Tests
   prüfen Aufruffolge, Budget- und Batchzähler, SQL-Variablenbindung,
   Abbruchpunkte, jede Pflichtbeobachtung, Statusvorrang, Fremdmarker, Fehler,
   Timeout und Cleanup-Faults. Alle DGN-004-SQL-Fixtures werden mit den
   bestehenden ScriptDom-Grammatiken auf Syntaxannahme für 2019/2022/2025
   geprüft; dies ersetzt keine Laufzeitqualifikation.
6. **Runtime-Qualifikation durchführen und belegen.** Die gepinnten Profile
   wurden sequenziell mit den registrierten Ressourcen-, SQL-, Prozess-,
   Ausgabe- und Cleanupbudgets ausgeführt. SQL Server 2022
   (`16.0.4265.3`, Developer/Linux, Kompatibilitätsstufe 160) und SQL Server
   2025 (`17.0.4075.5`, Enterprise Developer/Linux, Kompatibilitätsstufe 170)
   bestanden jeweils alle neun Aufrufe und den aktiven Annahmevertrag mit
   `PASS`; je Lauf wurden neun Flushes und 84 SQL-Batches beobachtet und der
   eigene Container vollständig entfernt. Vorangegangene fehlgeschlagene
   Diagnoseversuche wurden nicht als Evidenz gewertet. Runtime-PASS schließt
   Replay-, Performance-, Kausalitäts-, 2019- oder Fehler-/Fallbackaussagen
   nicht ein.
7. **Dokumentieren und integrieren.** Bei bestandenem Lauf die tatsächlich
   belegte Aussage, Buildprofile, Voraussetzungen, Ablauf, Resultate,
   Grenzen und Cleanup in den passenden DGN-004-Lesepfad übernehmen. Den
   aktuellen Ausführungsstand aktualisieren, erforderliche Reviews und
   Repository-Gates durchlaufen und die konsistente Änderung per Pull Request
   nach `origin/main` integrieren. Der Unterrichtsrelease bleibt ein separates
   Gate, falls die nötige Kursanleitung oder Releaseentscheidung noch fehlt.

## Vorgesehene Änderungsbereiche

- `Tests/Fixtures/DGN004_SourcePair/`: markiertes Datenbanksetup, synthetische
  Tabellen-/Daten-/Indexanlage und ausschließlich lokal notwendige Beobachtungs-
  und Cleanup-Skripte.
- `Tests/Runtime/`: begrenzter Container-Lifecycle und sequenzieller
  Neun-Aufruf-Orchestrator; Wiederverwendung der vorhandenen Kandidaten-,
  Capture- und Akzeptanzkomponenten statt paralleler Ersatzimplementierungen.
- `Tests/Static/`: synthetische Fehler-, Abbruch-, Eigentums- und
  Cleanup-Gegenproben sowie gezielte Verträge für den neuen Runner.
- `Documentation/Project_Planning/`: diesen Plan nach Freigabe in den
  tatsächlichen Ausführungsstatus überführen; bei Runtime-PASS die
  DGN-004-Anleitung mit Ablauf, Interpretation, Grenzen und Recovery ergänzen.
- `.ai/identity/registry.json`: nur den aktiven Container-/Last-Vorstarttext
  korrigieren; keine historischen Replay-Befunde, Kennungen, Budgets oder
  übrigen Kandidaten ändern. `.ai/BACKLOG.md` bleibt unverändert, da für diese
  DGN-004-Detailansicht kein Renderer existiert.

## Prüf- und Integrationsreihenfolge

1. Registry-Schema/Renderer und gezielte DGN-004-Text-/SQL-Quellenprüfungen.
2. Neue und bestehende DGN-004-Statiktests einschließlich synthetischer
   Fehler- und Cleanupfälle.
3. ScriptDom-Parsing der betroffenen SQL-Fixtures in den bereits verwendeten
   Grammatiken.
4. Gezielter Framework-, Registry-, Datenschutz- und Dokumentationscheck nach
   der tatsächlichen Änderung; gleiche Prüfeingaben nicht doppelt validieren.
5. Je Zielbuild begrenzte Runtimequalifikation nach den registrierten Budgets;
   nach Änderungen wurden nur die betroffenen Läufe wiederholt, bis beide
   Profile den aktiven Vertrag bestanden.
6. Vollständige Projektgates, unabhängige Sichtung der Runtime-/Cleanupsemantik,
   Pull Request und bestätigte Integration in `origin/main`. Das paketierte
   Unterrichtsrelease bleibt ein getrenntes Gate.

## Abnahmekriterien

- Vor dem ersten SQL-Änderungsschritt sind Image-Digest, Enginebuild, Edition,
  Compatibility Level, Ressourcenlimits, Berechtigungen, Datenbankoptionen,
  RunToken und alle vier Eigentumsmarker eindeutig geprüft.
- Jeder Build erfüllt exakt die neun registrierten Aufrufe in der Reihenfolge
  R/R/R-forced/H/H-forced/H-forced/R-forced/H/R. Es gibt höchstens neun
  Nutzaufrufe, neun Flushes, 100 reguläre SQL-Batches und drei begrenzte
  Metadatenbeobachtungen je Flush.
- Jeder Nutzaufruf liefert genau die 768 Solltupel (384 verschiedene Tupel,
  jedes zweimal) und eine vollständige, aktuelle und eindeutig zugeordnete
  Identitäts-/Plan-/Kontext-/Transportkette. Für forcierte Phasen stimmen
  angeforderter und tatsächlich ausgeführter Zielplan überein; UsePlan,
  Kompilierungsdelta +1, genau ein Ausführungsdelta, Null neue Force-Fehler
  und erfolgreiches Unforce sind belegt.
- Beide Builds bestehen den aktiven Vertrag und die sichere Bereinigung.
  Gesamtergebnis ist nur dann `PASS`, wenn beide Buildresultate `PASS` sind.
  `NOT_PROVEN`, `FAIL`, `FAIL_CLEANUP` und zurückgestellte Replay-Gates bleiben
  unterscheidbar; es gibt keine Performance- oder Replaybehauptung.
- Sämtliche Nachweise stammen aus den eigenen isolierten Containern. Kein
  Hostweiter Cache wird geleert, keine Fremdinstanz wird berührt, kein
  Hostport veröffentlicht und keine Laufzeitmessung als Leistungsnachweis
  interpretiert.

## Budgets und Schutzgrenzen

Die bestehenden DGN-004-Grenzen werden nicht erweitert: höchstens zwei eigene
Container insgesamt, sequenziell einer je Zielbuild, höchstens zwei eigene
SQL-Sessions, 2 CPU-Kerne, 3 GiB Container-RAM und 2048 MiB SQL-Server-
Speicherlimit. Es gelten unverändert 900 Sekunden reguläre Gesamtlaufzeit,
separate Cleanup-Budgets, höchstens 15 Sekunden je SQL-Aufruf und 20 Sekunden
je äußerem Prozess. Bestehende Grenzen für Text, Showplan, Prozessausgaben,
Datenbankdateien, Query Store und TempDB bleiben bindend. Kein globales Cache-
Leeren, kein Query-Store-CLEAR, keine Fremdcontaineraktion und kein zweiter
Versuch nach einem unbekannten Pflichtzustand.

## Risiken und Reaktion

Der tatsächliche DMV-Kandidatensatz, Planhandle und Plan können auf einem der
Zielbuilds fehlen, mehrdeutig oder nicht vollständig transportierbar sein.
Dann ist dieser Build `NOT_PROVEN` oder bei belegter Vertragsverletzung `FAIL`;
der Runner darf keinen anderen Kandidaten wählen. Falls die kontrollierten
Containergrenzen den festen Aufruf- oder Gesamtzeitrahmen überschreiten,
beendet der Runner geordnet, bereinigt und meldet den tatsächlichen Status;
Budgets werden nicht erhöht. Fehler beim Wiederherstellen oder Entfernen
führen zu `FAIL_CLEANUP` und stoppen jede weitere Version, bis der Zustand
geklärt ist. Eine inhaltliche Änderung der Abfrageform, des Lernclaims oder der
R/H-Folge erfordert eine gesonderte Vertragsänderung statt einer stillen
Anpassung während der Implementierung.

## Freigabe

Für genau den oben beschriebenen Runtime-Schnitt liegt die Entwicklungsfreigabe
vor:
Setup, Runner, Ergebnis-/Cleanupintegration, gezielte Tests, anschließende
einmalige 2022/2025-Qualifikation und erforderliche Projektdokumentation.
Die Präzisierung der aktiven Registry ist eingeschlossen. Zurückgestellte
Replay-/Fehler-/2019-Umfänge bleiben ausgeschlossen. Die Freigabe wurde am
21. November 2026 im aktuellen Arbeitsauftrag erteilt.
