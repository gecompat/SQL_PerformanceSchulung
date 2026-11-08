# CON-006 – Fachliche Prüfung des Offline-Graph- und Capturevertrags

| Merkmal | Wert |
|---|---|
| Prüfart | lokale Vertrags- und Quellenprüfung, nicht unabhängig |
| Geprüfte Komponente | `Tests/Static/con006_conversion_graph_contract.py` |
| Geltungsbereich | caller-gelieferter XML-Graph und Capturefelder |
| Laufstatus | keine SQL-, Lab- oder Runtimeausführung |

## Quellenbefund

`SRC-066` dokumentiert `xml_deadlock_report` als empfohlenen Erfassungsweg,
die drei Graphbereiche `victim-list`, `process-list` und `resource-list`,
Beispiele für Prozesskennungen und Ressourcen sowie Fehler 1205 für das
Deadlockopfer. `SRC-068` beschreibt die vorhandene `system_health`-Session und
ihre Erfassung von Deadlockgraphs. Das stützt die Auswahl des Graphereignisses
und die strukturelle Auswertung.

Die aktuell geprüften Herstellertexte legen kein verbindliches XML-Schema für
alle Attribute eines Deadlockgraphs fest und spezifizieren insbesondere die
genaue Semantik von `requestType="convert"` im geprüften Konversionsfall nicht.
Die Offline-Regel, beide Prozesse müssten am identischen `keylock` jeweils `S`
halten und eine `X`-Konversion anfordern, bleibt deshalb ein enger
struktureller Vertrag. Ihre konkrete Engine-Repräsentation ist empirisch
buildgebunden zu qualifizieren; aus dem synthetischen Parser-PASS folgt keine
Quell- oder Laufzeitqualifikation.

## Vertragsbefund

Der Graphprüfer bindet genau zwei Prozesse und einen Opfer an die vorgegebenen
SPIDs und Datenbank. Er verlangt genau eine passende Keylock-Ressource mit
Objekt-, Index- und optionaler HoBT-Bindung sowie beide S-Eigentümer und beide
X-Konversionsanforderungen an dieser Ressource. DTD-/Entity-Deklarationen,
ungültiges XML, falsche Bindungen, zusätzliche passende Ressourcen und
abweichende Lockmodi werden zurückgewiesen.

Der Captureprüfer bindet den gelieferten Run-Token, Eventnamen und
`system_health`-Quellstring, Datenbank, Actors, Eventanzahl, Zeitfenster,
Deadlockopfer und Actorresultate. Diese Felder sind zusammengefasste
Caller-Eingaben: Der Prüfer liest weder die Extended-Events-Quelle noch
authentifiziert er, dass Token, Zeitstempel, Graph-XML und Actorresultate aus
demselben Event beziehungsweise Lauf stammen. Die Dokumentation muss diesen
Producervertrag als separates späteres Gate erhalten. Ein statischer `PASS`
attestiert allein interne Konsistenz der übergebenen Werte.

## Grenzen und Folgegates

Die öffentliche `system_health`-Evidenz kann begrenzt sein und ist kein
dediziertes, markergebundenes Langzeitarchiv. Die Capturemethode darf aus einer
fehlenden Graphsichtbarkeit keinen Graphnachweis erzeugen; die bestehende
kontrollierte Evidenzlücke bleibt `SKIP_EVIDENCE_MISSING` beziehungsweise
`NOT_PROVEN` im jeweiligen Vertrag.

Offen bleiben die unabhängige Methoden-/Quellenfreigabe, die tatsächliche
Engine-Qualifikation des Konversionsattributs, die Herkunftsbindung eines
vollständigen Capture-Records sowie die begrenzte Capture-/Cleanupprüfung im
Zielbuild. Diese lokale Prüfung erteilt keine Runtimefreigabe und ändert den
bestehenden CON-006-Demovertrag nicht.
