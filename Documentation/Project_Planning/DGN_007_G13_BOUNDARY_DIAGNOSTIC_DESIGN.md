# DGN-007: Entwurf für eine begrenzte G13-Grenzdiagnose

**Status:** PROPOSED, Entwurf ohne Runtimefreigabe  
**Geltung:** Diagnose des exakten bestehenden G13-Prädikats; keine Methodenänderung

## Befund

Der aktuelle v2-Control-Capture enthält Fensterklammern sowie Plan- und Query-Store-Zeitwerte. Er enthält nicht die vollständigen aggregierten `lab.IncidentProfile`-Zeilen und die exakten `lab.IncidentState`-Grenzen, die der G13-Guard in derselben Auswertung verglichen hat. Eine nachträgliche Query-Store-Abfrage ist kein atomarer Beleg dieser ursprünglichen Auswertung. Der bestehende Reporter im fehlgeschlagenen G13-Zweig bleibt für seine begrenzte spätere Raw-Sicht erhalten.

## Vorgeschlagene Aufnahme

Ein künftiger, ausdrücklich freigegebener isolierter Diagnoselauf ergänzt für genau die bereits ausgewerteten G13-Gruppen eine begrenzte skalare Fehleraufnahme am Guard. Sie erfasst gemeinsam:

- die exakten `ExecutionStarted`- und `ExecutionFinished`-Werte aus `lab.IncidentState`;
- alle verglichenen `FirstExecutionTime`- und `LastExecutionTime`-Werte aus `lab.IncidentProfile`, einschließlich Gruppenidentität, Ausführungstyp und Zählwert;
- vollständige Einheiten und verlustfreie Rohrepräsentation der Zeitwerte sowie die Quellspalte;
- exakte signed Deltas `FirstExecutionTime - ExecutionStarted` und `LastExecutionTime - ExecutionFinished`, ohne Rundung;
- eine feste Zeilenobergrenze, explizite Vollständigkeits-/Überlaufkennzeichnung und stabile neutrale Fehlercodes.

Die Aufnahme muss dieselben materialisierten Zeilen benutzen, die der Guard prüft. Sie darf keine zweite Query-Store-Aufnahme als Ersatz verwenden. Ausgabe bleibt innerhalb des isolierten autorisierten Laufs und wird nicht in öffentliche CI-Logs oder das Repository geschrieben. Querytext, Plan-XML, Zugangsdaten und Umgebungskennungen werden nicht ausgegeben.

## Unveränderte Grenze

Die Vergleichsgrenze bleibt exakt null. Dieser Entwurf genehmigt weder Toleranz, Rundung, Puffer, Guardentfernung noch alternative Zeitzuordnung. Er verändert keine SQL-Datei und startet keinen SQL-Lauf. Erst ein separater Auftrag, der den isolierten Diagnosecode und dessen konkreten Lauf freigibt, darf diese Aufnahme umsetzen und ausführen.

Ein einzelner Datensatz würde nur die tatsächlich verglichenen Werte dieses Laufs belegen. Er bewiese weder eine allgemeine Uhrbeziehung noch eine Ursache, einen Methodenwechsel, Incidentpromotion oder die Qualifikation der sechs-Lifecycle-Matrix. Menschliche Generalprobe ist nicht Teil dieses Vorschlags.
