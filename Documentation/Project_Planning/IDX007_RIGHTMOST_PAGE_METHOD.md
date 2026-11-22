# IDX-007 – Methodenentwurf zur rechten Blattseite

| Merkmal | Wert |
|---|---|
| Status | `METHOD_DRAFT` – keine SQL-, Demo- oder Laufzeitfreigabe |
| Lernziel | Eine wartende `PAGELATCH_EX`-Seite nur dann als letzte Blattseite eines bestimmten Indexes einordnen, wenn die Seitenmetadaten diese Zuordnung tragen |
| Lehrpfad | Vorhandene [IDX-007-Lehrnotiz](../Curriculum/LAST_PAGE_INSERT_CONTENTION_LESSON.md); kein neues Lernziel |
| Vertrag | [Offline-Prüfer](../../Tests/Static/idx007_last_page_contract.py) bleibt ein Konsistenzfilter für caller-gelieferte Werte |
| Quellen | `SRC-168`–`SRC-172` |

## Aussage, die geprüft werden soll

Ein Last-Page-Befund benötigt mindestens zwei eigene Sessions, die im engen
Messfenster wegen `PAGELATCH_EX` auf derselben Datenbank-/Datei-/Seitenadresse
warten. Die Seite muss zum synthetischen Zielobjekt, Index und Partition
gehören und Blattebene haben. Zusätzlich muss eine unabhängige aktuelle
Seitenkettenaufnahme zeigen, dass die Zielseite die rechte Kante der Blattkette
bildet. Ein sequentieller Schlüssel, `leaf_insert_count`, Indexoption oder
`page_level = 0` allein reicht nicht.

`sys.fn_PageResCracker` kann `page_resource` in Datenbank-, Datei- und
Seitennummer zerlegen. `sys.dm_db_page_info` liefert für genau eine Seite
Headerinformationen einschließlich Objekt, Index, Partition, Blattebene und
Vor-/Nachfolgeradressen. Diese Quellen bilden einen Startpunkt, aber keine
atomare Mehrseitenaufnahme. Zwischen zwei Funktionsaufrufen können Einfügungen,
Splits oder andere Strukturänderungen Blattlinks ändern. Eine Momentaufnahme
beweist keinen stabilen Zustand außerhalb ihres kurzen Erfassungsfensters.

## Vorgeschlagene Seitenkettenprüfung

1. **Wait-Ressource binden:** Für jede beobachtete eigene wartende Session die
   aktuelle Request-/Task-ID, `PAGELATCH_EX`, `wait_duration_ms`, den UTC-
   Capturebereich und die per `page_resource` entschlüsselte
   Datenbank-/Datei-/Seitenadresse erfassen. `PAGEIOLATCH_EX`, fehlende
   `page_resource` oder eine nicht zur eigenen Session gebundene Adresse sind
   kein Treffer.
2. **Zielseite prüfen:** `sys.dm_db_page_info` im vorgesehenen Zielkontext auf
   genau diese Adresse anwenden. Datenbank, Objekt, Index, Partition und
   `page_level = 0` müssen zum markergebundenen synthetischen Ziel passen.
   Nicht-Blattseiten, Heapseiten und systemfremde Objekte widerlegen den
   Last-Page-Claim.
3. **Vorwärtskette verfolgen:** Ab der Wait-Seite die `next_page_file_id`-/
   `next_page_page_id`-Adresse schrittweise lesen, bis ein vom Review
   bestätigter Terminalzustand erreicht wird. Jede Seite muss zum selben
   Datenbank-/Objekt-/Index-/Partitions- und Blattseitenkontext gehören. Der
   vorwärts gelesene Link und der Rücklink des Nachfolgers müssen zueinander
   passen. Eine Seitenadresse darf nicht zyklisch wiederkehren.
4. **Begrenzen:** Vor dem ersten Nachfolgeraufruf eine feste maximale Zahl
   gelesener Seiten festlegen. Eine unabhängige Seitenanzahl derselben
   Indexpartition kann als Plausibilitätsgrenze dienen, muss aber im
   Methodenreview gegen Inserts und Seiten-Splits abgeglichen werden. Wird
   irgendeine Grenze erreicht, ohne den bestätigten Terminalzustand zu finden,
   folgt `NOT_PROVEN`; die Schleife darf nicht stillschweigend weiterwachsen.
5. **Wait erneut binden:** Nach dem Kettenlauf die eigene Wait-Gruppe erneut
   lesen. Die gleiche Wait-Adresse und der gleiche Zielkontext müssen innerhalb
   des engen Capturefensters wieder vorkommen. Die beiden Aufnahmen werden als
   begrenzte Klammer um die Kettenlesung berichtet, nicht als atomare DMV-
   Transaktion oder exakter gemeinsamer Enginezeitpunkt.
6. **Ergebnis begrenzen:** Nur wenn beide Wait-Ränder dieselbe Zielseite
   melden, der einzelne dazwischenliegende Kettenlauf auf dieser Seite
   konsistent am bestätigten Ende ankommt und alle Seitenmetadaten vollständig
   sind, darf das Ergebnis höchstens lauten: „Die Wait-Seite war bei den
   umschließenden Wait-Aufnahmen identisch; der dazwischenliegende
   Seitenkettenlauf ordnete sie als rechte Blattseite der geprüften
   Indexpartition ein.“ Die Kettenmetadaten wurden dabei nicht an beiden
   Wait-Rändern erneut gelesen. Ein historischer, späterer oder allgemeiner
   Dauerzustand folgt daraus nicht.

Der konkrete Terminalwert für nicht vorhandene Nachfolger, die Verfügbarkeit
der Seitenanzahlquelle und eine sichere Reaktion auf einen parallelen Split
sind noch nicht enginequalifiziert. Der spätere Prüfer muss diese Fälle
`NOT_PROVEN` zuordnen, bis der unabhängige Methodenreview ihre genaue
Darstellung bestätigt. Er darf weder `NULL` noch eine Nulladresse als
Terminalwert voraussetzen, bevor diese Semantik belegt ist.

## Ergebniszustände

| Befund | Ergebnis |
|---|---|
| Vollständige, widerspruchsfreie Wait-/Ziel-/Kettenbindung auf beiden Capture-Rändern | begrenzter Kandidat für `PASS`; noch keine Performancequalifikation |
| Kein gleichzeitiger eigener `PAGELATCH_EX`-Wait, fehlende Seite, unbestätigter Terminalwert, geänderte Kette oder erreichter Seiten-Cap | `NOT_PROVEN` beziehungsweise kontrollierter Skip |
| Wait-Adresse gehört nachweislich zu anderer Datenbank, anderem Index/Objekt/Partition, nicht zur Blattseite oder explizit zu einer nicht rechten Blattseite | `FAIL` für diesen Last-Page-Claim |
| Zeit-, Request- oder Ressourcenmarker widersprechen einander | Vertragsfehler; Cleanup hat weiterhin Vorrang |

`PASS` einer späteren Kettenprüfung wäre nur eine Aussage über die konkrete
Aufnahme. Er beweist weder hohe Konkurrenz über längere Zeit noch Durchsatz,
Ursache eines Produktionsengpasses oder einen Vorteil von
`OPTIMIZE_FOR_SEQUENTIAL_KEY`.

## Geltungsgrenzen und Gates

- Erste spätere Pilotierung nur auf einem eigenen, kurzlebigen SQL-Server-
  Developer-Wegwerfziel mit markierter Testdatenbank. Kein Zugriff auf eine
  geteilte Instanz; keine Änderung von Host-/Instanzkonfiguration.
- Die DMV-/Funktionsrechte, exakten Feldwerte für Blatt-Terminalseiten und
  Ressourcenkosten aller Einzelaufrufe sind buildgebunden vorab zu bestätigen.
- Der Capturepfad benötigt feste Obergrenzen für Wait-Rows, Seitenschritte,
  Laufzeit und Gesamtausgabe. Fehlende oder widersprüchliche Evidenz endet
  ohne Ausweitung der Abfrage oder Last.
- Ein unabhängiger Methoden-/Quellenreview muss insbesondere
  Terminaldarstellung, Nachfolger-/Rücklinksemantik, Seiten-Cap, Änderungen
  während eines Splits sowie die Aussagekraft der beiden Capture-Ränder
  bestätigen.
- Ein davon getrennter Offline-Checker darf caller-gelieferte Kettenrecords nur
  intern auf Seitenidentität, Blattniveau, Zyklen, Vorwärts-/Rücklinks,
  Startseite, expliziten Endmarker und Seiten-Cap prüfen. Er darf keine
  SQL-Abfrage oder Enginesemantik ableiten.
- Erst nach diesem Review dürfen eine ausführbare read-only Seitenkettenprobe
  und ein konkreter Cleanup-/Runtimevertrag vorbereitet werden. Der faire
  OFF/ON-Lastvergleich bleibt ein getrenntes Gate und wird nicht durch
  Seitenkettenbelege freigegeben.

Die geltenden Herstellerquellen beschreiben Seiteneigenschaften und
Nachfolgerfelder, aber keinen atomaren Traversalvertrag für eine während
konkurrierender Inserts veränderliche B-Baum-Blattkette. Dieses Verhalten und
die vorgeschlagene Klammerung bleiben deshalb ein offenes empirisches Gate.

`evaluate_last_page_contention` verlangt nun neben den beiden Waits auch die
caller-gelieferten `PageLink`-Records, einen expliziten Endmarker und ein
begrenztes Seitenbudget. Es ruft den Kettenprüfer mit der Wait-Zielseite als
Startadresse und der Ziel-Datenbank, dem Objekt, Index und der Partition auf.
Ein Wait-PASS ohne passende Kette ist `NOT_PROVEN`; eine Kette mit abweichender
Startseite oder Identität kann keinen Wait-PASS erzeugen. Die getrennte
Kettenprüfung bleibt verfügbar, authentifiziert aber ebenfalls keine
DMV-/Seitenaufnahme und entscheidet nicht, welcher Marker in einem
SQL-Server-Build tatsächlich das Kettenende darstellt. Die unabhängige
Methodenprüfung bleibt Voraussetzung für eine ausführbare Probe.

### Ergänzung des Offline-Waitvertrags

Der Offline-Waitchecker bindet jeden caller-gelieferten `PAGELATCH_EX`-Datensatz
jetzt zusätzlich an eine erwartete Actor-/Session-/Request-ID und eine
Taskausführung (`exec_context_id`). Beide erwarteten Actors müssen mit ihrer
gebundenen Request-ID auf derselben Zielseite warten. Mehrere eindeutige Tasks
derselben erwarteten Request-ID bleiben zulässig; wiederholte Taskrecords,
fehlende Identitäten und fremde Requests werden abgewiesen. Dies erfüllt die
statische Request-/Taskform des Methodenentwurfs, authentifiziert aber weder
DMV-Herkunft noch Actorzuordnung oder Waitüberlappung. Der Offlinevertrag bleibt
ein Konsistenzfilter und erteilt keine Enginefreigabe.
