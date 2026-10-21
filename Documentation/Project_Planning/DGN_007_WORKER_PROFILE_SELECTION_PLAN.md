# DGN-007 – Auswahlplan für frische Workerprofile

## Ausgangspunkt und Ziel

DGN-007 bezeichnet die Diagnose-Demo mit getrenntem Quellen- und Laufnachweis.
[PR281](https://github.com/gecompat/SQL_PerformanceSchulung/pull/281) ist in
`f143c968f5fec26c60fcc8b32e8baac637fdbcd1` vollständig integriert. Der
[Runnernachweis](DGN_007_RUNNER_SHARED_SOURCE_REVIEW.md#abschluss-des-funktionalen-schnitts)
belegt die vollständige synthetische Quellenfolge und den behobenen
Reentranzfehler. Er belegt keine tatsächlich ausgewählte Workerinstallation.

Der kontinuierliche menschliche Auftrag umfasst die weitere operative
Anbindung. Der nächste vorbereitende Schnitt bestimmt deshalb die Auswahl und
die noch fehlenden Nachweise für frische Workerprofile. Dieser Plan ist keine
erneute Runnerkorrektur und setzt historische Versuche nicht zurück.

Die Profilfelder heißen im bestehenden Vertrag S15 (15 skalare Felder der
Installation) und P11 (elf Felder je Modul, etwa Name, Herkunft und Loader).
Ihre vollständigen Formen und die Trennung von Vorwahl und Beobachtung folgen
dem [Profilbindungsvertrag, insbesondere §8 und §16](DGN_007_IMPORT_PROFILE_BINDING_DESIGN.md#8-konkreter-bootstrap--und-projektionsvorschnitt).
Ein Loader ist hier die für das Laden eines Moduls gebundene Instanz.

## Endlicher Umfang dieses Plans

Ein Implementierungsverantwortlicher root und ein unabhängiger Reviewer führen
einen Planentwurf und höchstens eine zusammenhängende Entwurfsnacharbeit. Der
Checkpoint ist der eingefrorene Entwurf vor unabhängiger Prüfung; die harte
Grenze sind zwei Entwurfsstände einschließlich Review, lokaler
Dokumentationsprüfungen, Integrationsprüfungen, Merge und eigener
Branchbereinigung. Verbrauch UNKNOWN: es liegt keine verlässliche Messung vor.

Dieser Schnitt ändert ausschließlich diesen Plan und seine Einstiege in
Ausführungsstand, Backlog und Masterplan. Er erzeugt oder startet keine
Probequelle, keinen Worker und keinen SQL-Lauf. Er wiederholt weder die
abgeschlossenen Runnermodelle noch den historischen nativen Metadatenversuch.
Die unabhängige Prüfung beurteilt Vollständigkeit, Reihenfolge, Autorisierung,
Datenschutz und die nachfolgend genannten Ablehnungsbedingungen.

## Auswahlpaket vor einem späteren Probeaufruf

Das nachfolgende konkrete Auswahlpaket muss zusammenhängend diese Fragen lösen:

1. **Eine Installation festlegen.** Genau eine vorhandene Linux-Installation
   von CPython 3.12 wählen. Patchversion, Executablelocator und aufgelöstes Ziel,
   Prefixe, Bibliotheksroots, Suchpfade, Isolationflags sowie SOABI (Kennung der
   binären Python-Schnittstelle) und DESTSHARED (Verzeichnis der
   Erweiterungsmodule) separat begründen. Historische private Werte sind
   Hinweise, keine aktuelle Auswahl oder Messergebnisse.
2. **Die tatsächlich vorgesehene Quelle binden.** Den integrierten
   `build_runner_loader_control_bootstrap` und sämtliche Generatorabhängigkeiten
   an einen konkreten Repository-Stand binden. Die vollständigen Originalbytes
   der Profilkontrollquelle, gewählte Parameter und daraus entstehende gesamte
   Scriptbytes festhalten. Weder ein gekürzter Bootstrap noch eine synthetische
   Testquelle wird als endgültige Workerquelle ausgegeben.
3. **Die Importinventur aus Quellen begründen.** Direkte und transitive Imports,
   notwendige Sysconfig-Vorinitialisierung, Builtin-/Frozen-Verfügbarkeit,
   Loaderformen und feste Aliasverbände anhand der konkreten Installations-,
   Build- und Kontrollquellen ableiten. Verfügbarkeit ist von tatsächlicher
   Cachemitgliedschaft zu trennen. Keine beobachtete erfolgreiche Modulliste
   nachträglich als Soll übernehmen; fehlende oder zusätzliche Module ablehnen.
4. **Alle drei Workerdeklarationen vollständig vorwählen.** Dieselbe
   Installation darf verwendet werden; pro Ordinal bleiben Kontrollnamen,
   Origins, Locations, vollständige S15-/P11-Werte und Kontexte explizit.
   Kontrollrollen bleiben `__main__` und `dgn007_import_runtime_profile`, direkte
   Scriptimporte `importlib.util`, `sys`, `sysconfig`, `json` und `struct`.
   Die bekannte FileFinder-Hookbindung vor dem Vergleich separat begründen;
   gleiche Texte oder ein Bericht ersetzen keine gehaltenen lokalen Identitäten.
5. **Darstellbarkeit vollständig prüfen.** Vor Encoder-/Digestfreigabe die
   vollständigen fünf Vertragsformen und das gemeinsame 65536-Byte-Gate prüfen.
   Für die konkrete spätere Runnerquelle zusätzlich den vollständigen
   Quellenfit bei unverändertem 131072-Byte-Limit nachweisen. Die bekannten
   129679/127911 Bytes aus PR281 gelten nur für dessen Profilfixture.
   Kein Weglassen von Rawbytes (unveränderten Originalbytes), Feldern oder
   Modulen und kein Erhöhen von Grenzen, um die neue Auswahl passend zu machen.
6. **Probe und Aufnahme unterscheiden.** Falls native Fragen nach der
   Quellenprüfung offenbleiben, einen eigenen konkreten Quellen-/Aufrufplan
   vorlegen. Er benennt exakt, welche Verfügbarkeits- oder Beobachtungsfrage der
   Probeaufruf beantwortet und welche nicht. Eine Teilbootstrapaufnahme kann
   keine Abnahme des vollständigen Workers ersetzen. Liveanker werden erst an
   die separat vorgewählten Namen gebunden; Abweichungen erzeugen kein neues Soll.

Das vollständige private Paket enthält Locator, Quellenpins, deklarierte Werte
und ihre Begründung. Es bleibt unter den vorhandenen Ignoregrenzen. Öffentliche
Dokumentation erhält nur Methode, bereinigte Quellenverweise, Prüfstatus und
Grenzen; keine Hostpfade, Installationsrecords oder privaten Ausgaben.

## Prüfung und Übergang zur Ausführung

Vor jeder Generierung, jedem Import einer neuen Probequelle oder jedem nativen
Start benötigt das konkrete Paket eine unabhängige Auswahl- sowie Quellen-/
Testprüfung mit ausdrücklichem Lauf-GO (Freigabe für den genau benannten Lauf).
Dieser Plan erteilt dieses GO nicht. Routinemäßige Implementierung und reguläre
Integration innerhalb des menschlichen Auftrags brauchen keine erneute
menschliche Erlaubnis; ungelöste fachliche oder Wirkungsgrenzen bleiben offen.

Ein späterer nativer Aufrufplan muss vor dem Start eine gemeinsame endliche
Zeit-, Byte- und Schrittgrenze einschließlich Auswahl-, Pin-, Prüf- und
Cleanupaufrufen festlegen. Windows-Launcher und eigenes Linux-Kind getrennt
halten, warten und auf Abwesenheit prüfen. Ein Launcherexit allein belegt keinen
Kindcleanup. Nur vorher abwesende eigene Tempziele verwenden; fremde Prozesse,
Dateien, Worktrees und private Evidence bleiben erhalten. Unklarer Ausgang
bleibt UNKNOWN und rechtfertigt keinen blinden Retry. Dieser Plan legt noch
keine aktuellen privaten Ziele oder ausführbaren Kommandos fest.

Die Gegenproben des konkreten Pakets müssen mindestens fehlende/zusätzliche
Module, falsche Origins/Loader/Aliase, späte Sysconfigimporte, veränderte
Kontrollbytes, unvollständige Formen und Grenzüberschreitung erkennen. Ablehnung
vor Folgeeffekten, keine Fortschreibung nach Fehler und sicherer eigener
Cleanup gehören zur späteren Abnahme. Bis dahin ist der Status **geplant**,
nicht ausgeführt oder runtimevalidiert.

Nach vollständiger Integration dieses Plans ist genau das konkrete
quellenbegründete Auswahlpaket der nächste Schritt; sein eigener endlicher
Quellen-/Versuchsrahmen wird vor Umsetzung festgelegt. Die vollständige
operative Aufnahme, echte Quellenloader-/Importprovenienz, tatsächlich
ausgeführte Bytes, SESSION_END (Abschlussmeldung mit Counts und Kanalhash),
nativer Exit/Cleanup und die Messmethode bleiben getrennte Nachweise. DEC-076
(vertrauenswürdige Schulungsquellen ohne Manipulationsisolation) gilt weiter;
keine Sandbox-, Produktions- oder SQL-Freigabe aus einem synthetischen PASS.

## Abschlussprüfung dieses Dokumentationsschnitts

Lokale Prüfung: UTF-8 und relative Markdownziele aller vier geänderten Dateien,
Datenschutz vor jedem Commit und `git diff --check`. Die unabhängige Prüfung
schließt inhaltliche Befunde. Danach aktuelle grüne Prüfungen für PR-Stand und
Main-Basis, regulärer Merge, frische Main-Prüfungen, vollständige Baumübernahme,
Synchronisation und ausschließlich eigene lokale/Remote-Branchbereinigung.
Der Pull-Request-Abschlussnachweis bindet die tatsächlich erreichten Ergebnisse.
Keine zusätzliche Test-, Workflow- oder Reviewkette für unveränderte Quellen.
