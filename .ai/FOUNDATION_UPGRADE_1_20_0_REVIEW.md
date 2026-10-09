# Foundation 1.20.0 – Integration und Prozessaufwand

Stand: 2026-10-09. Geltungsbereich: `FOUNDATION_INTEGRITY` und betroffene
Projektsteuerung. Keine SQL-/Reporterfreigabe.

Die Quelle `gecompat/AI_Repository_Foundation` wurde einmal über `origin/main`
aufgelöst und auf `39ae5c534bb0cf78046485754ed1be7867bf9534` gepinnt. Manifest
und Feature-Katalog dieses Commits bestimmen Version und Delta. Der portable
Manifesthash ist `d707d9dfe5cbcf7d323260891ec5d535493715d1413d7b6e421b2691aa1149d5`.
Alle ausgewählten Exportquellen wurden unabhängig gegen die gepinnten Gitblobs
unter der erlaubten LF-/CRLF-Normalisierung geprüft. Die Provenienz bindet 107
Dateien; ausschließlich `AGENTS.md` bewahrt eine begründete Projektsektion als
`INTENTIONAL_OVERRIDE`. Projektlizenz und vollständiger Foundation-MIT-Hinweis
bleiben erhalten.

Das vollständige [Assessment](FOUNDATION_UPGRADE_1_20_0_ASSESSMENT.json) umfasst
21 Features: ein neues Feature und 20 materielle Änderungen. Die Empfehlung
`bounded-processing-efficiency` ist mit dem ausdrücklichen Benutzerauftrag und
`DEC-070` umgesetzt. Keine offene Upgradeentscheidung oder Konfliktklassifikation.
Alle zehn ausgewählten Capabilities und drei dünnen Adapter bleiben erhalten;
ihre Verfügbarkeit aktiviert keine Runtime, Provider, Credentials, Modelle,
Sessionwechsel oder Automation. Bestehende Identitäten und Registrierungsautorität
bleiben erhalten. CI-Supersession und Sessionoptionen bleiben gemäß `DEC-067`.

## Tatsächlicher Prozessbefund

`.ai/README.md` verlangte neun Dokumente vor einer Änderung. Zusätzlich verlangte
der Masterplan eine eigene sieben Dokumente umfassende Folge vor jeder Bearbeitung.
`PROJECT_RULES.md` band diese Pflicht ausdrücklich; sein Modell-/Kostenabschnitt
wiederholte auf mehr als 200 Zeilen allgemeine Arbeitsregeln. Der persistente
Cachepfad war als einziger Wiederverwendungspfad dargestellt. Die Adapter enthalten
bereits nur Discovery; dort ist keine einzigartige Governance zu entfernen.
Der deterministische Foundation-Auditor meldete die breite Lektüre im Masterplan;
die neun Dokumente umfassende indirekte Pflicht erkannte erst die semantische
Prüfung. Ein leerer heuristischer Report allein wäre deshalb kein Abschlussbeleg.

Die Änderung ersetzt beide Pflichtfolgen durch den kanonischen Scope-Router,
verdichtet die Kostenregeln und ergänzt Sessionwiederverwendung ohne persistenten
Record. Die bestehende persistente Capability und ihr strenger Missvertrag bleiben
unverändert verfügbar. Registry-/Identitätsregeln werden bei entsprechenden
Änderungen gelesen; sie lösen keine vollständige Planungslektüre aus. Neue Reviews
benötigen ein konkretes offenes Risiko und Abnahmekriterien. Bestehende unabhängige
Pflichtreviews und Tests werden dadurch nicht aufgehoben.

Eine lokale Rechnung mit UTF-8-Quellen aus dem unveränderten Ausgangscommit
`5ea6a35` ergab für die neun Pflichtdokumente plus alten AGENTS-/Foundation-Einstieg
249.663 Bytes. Der neue gemeinsame Einstieg einschließlich README, Projektkontext,
Projektregeln und CONTRIBUTING beträgt im vorbereiteten Stand 35.799 Bytes
(rund 86 % weniger). PROJECT_RULES sank von 325 auf 137 Zeilen. Dies ist eine
gemessene Kontextmenge, keine behauptete Token-, Modellkosten- oder Laufzeitmessung.
Scopeabhängige Fachquellen kommen weiterhin hinzu. Die gezielten sieben
Foundation-Gegenproben für Sessionbindung, Änderung/Abhängigkeiten und gemeinsame
Budgets bestanden lokal; aktuelle Bytes werden weiterhin deterministisch gelesen.
Unbekannte effektive native Discovery-Konfiguration erlaubt keinen tatsächlichen
Cache-/Session-Hit. Fehlende Konfiguration wird einmal benannt statt wiederholt
diagnostiziert. Kein persistenter Record oder nachträglich erfundener Analyse-Hit
wurde als Arbeitsevidenz verwendet.

Ein einzelner aktueller lokaler Rawbyte-SHA256-Lauf über die sechs neuen
Einstiegsquellen dauerte 0,498 ms (`perf_counter`, Windows/Python 3.14.7).
Das ist der tatsächlich gemessene kleine Fingerprintaufwand, keine repräsentative
End-to-End-Latenz oder Attestation eines Analyse-Hits. Der frühere Aufwand von
Modelllektüre und semantischer Wiederanalyse ist nicht separat messbar und wird
nicht aus Bytes in Sekunden oder Geld umgerechnet. Die Änderung spart diese
breite Pflichtverarbeitung, ohne lokale Quellenprüfungen zu vermeiden.

## Erhaltene strengere Regeln und Begründung

- Synthetische Daten, pfadgebundene Lizenz-Ausnahme und Privacyprüfung vor Commit
  schützen veröffentlichte Schulungsartefakte. Office-/Bild-/Log-Prüfung bleibt
  wegen möglicher nichttextueller Informationen erforderlich.
- Historische Kennungen, eine Registry und semantischer Merge verhindern Verlust
  von Traceability und parallele Wiedervergabe. Nur die neu registrierte
  Prozessentscheidung ergänzt den Bestand.
- Demo-/Messverträge, exakte Oracles, Cleanup, Versionsmatrix und Methodenentscheid
  erhalten den fachlichen Claim. Ein günstiger Prozess darf keine fehlende
  SQL-Evidenz als bestanden ausgeben.
- Pflicht-CI, PR-Pfad und keine Cancellation laufender SQL-Mutationen schützen
  Integrationsbindung und Cleanup. Ein substantieller Fehler bleibt nicht umgehbar.
- `DEC-066`/`DEC-069` verlangen tatsächliche Integration und ausschließlich sicher
  übernommene eigene Branchbereinigung; das verhindert verwaiste halbfertige Arbeit.

Die Foundation-Ergänzungen klassifizieren diese Grenzen als kompatible strengere
oder ergänzende Projektregeln. Ein pauschaler Vollreview aller Nachweis-/Planungs-
dokumente und Reviewketten ohne offene Frage werden nicht verlangt. Die begrenzte
DGN-Ursachenprüfung läuft getrennt; allgemeine Welle, SESSION_END und Automation
bleiben pausiert.

## Validierung

Der Source-Foundation-Validator im Profil `full` bestand mit 107 Installations-
Hashes, null Warnungen/Fehlern/Blockern. Die Projektprüfungen für Foundation-
Integration, Kennungen/Registry, Kontinuität und SQL-Readiness bestanden lokal.
Die Privacyprüfung des gesamten Arbeitsbaums meldete zunächst ausschließlich
unversionierte Source-Export-/Testfixtures unter Runtime, die nie Transferziele
sind. Das ist ein fehlgeschlagener Ganzarbeitsbaumscan und kein grüner Nachweis.
Der vollständige veröffentlichbare Indexkandidat bestand die separate Privacy-
Prüfung: 805 Dateien, 793 Textdateien, ein Officepaket, ein erlaubtes unverändertes
historisches Artefakt. `git diff --check` bestand. Die Pflicht-CI wird im zugehörigen
PR an den aktuellen Head gebunden.
SQL-Runtime bleibt ein getrennter, gegebenenfalls weiterhin blockierter Nachweis.
