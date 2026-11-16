# DGN-007: begrenzte G13-Grenzdiagnose

**Status:** implementiert; gezielter SQL-Server-2022-Lauf abgeschlossen
**Geltung:** Diagnose des exakten bestehenden G13-Prädikats; keine Methodenänderung

## Befund

Der v2-Control-Capture enthielt Fensterklammern sowie Plan- und Query-Store-Zeitwerte,
aber nicht die vollständigen aggregierten `lab.IncidentProfile`-Zeilen und die
`lab.IncidentState`-Grenzen, die G13 gemeinsam verglich. Eine nachträgliche
Query-Store-Abfrage war kein atomarer Beleg dieser ursprünglichen Auswertung.

## Implementierte Aufnahme

`35_Control_Evidence.sql` materialisiert die begrenzte Verbindung von Profil- und
Fensterwerten einmal in `#G13BoundaryRows`. Sowohl der bestehende G13-Guard als auch
der Diagnose-Reporter lesen genau diese Zeilen. Der Guard vergleicht weiterhin
`FirstExecutionTime < ExecutionStarted` oder `LastExecutionTime > ExecutionFinished`;
die Grenze bleibt exakt null. Es gibt keine zweite Query-Store-Abfrage als Ersatz.

Der Reporter kennzeichnet Beginn, Ende, Vollständigkeit und Überlauf und gibt maximal
16 skalare Gruppen aus. Er enthält Gruppen-/Plan-/Intervallidentität, Ausführungstyp,
Zählwert, UTC-Zeitwerte und vorzeichenbehaftete Deltas in 100-ns-Ticks. Kein Querytext,
Plan-XML, Credential oder Umgebungskennung wird aufgenommen. Der Runner akzeptiert
diese Diagnose ausschließlich für `control-ab`/`control-ba`, führt genau einen
isolierten Capture-Lifecycle aus und gibt die validierten Zeilen erst nach Cleanup
aus. Der Modus `--diagnose-g13-boundaries` ist nicht in CI verdrahtet.

## Noch ausstehend

Der einmalige isolierte Lauf auf SQL Server 2022 mit `control-ba` bestand: ein
Lifecycle `PASS`, unabhängiger Container-Cleanup `PASS`, Ergebnis
`DGN007_G13_BOUNDARY|NOT_OBSERVED`. G13 trat in diesem Lauf nicht auf, daher gibt es
keine Grenzwerte zu interpretieren. Das Ergebnis belegt ausschließlich diesen Lauf;
es beweist weder eine allgemeine Uhrbeziehung noch eine Ursache, Methodenänderung,
Incidentpromotion oder Qualifikation der Sechsermatrix. Die menschliche Generalprobe
bleibt ausgeschlossen.
