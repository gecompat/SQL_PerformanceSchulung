# DGN-007 – Skalarer Collector-Transport

| Merkmal | Wert |
|---|---|
| Status | `STATIC_COLLECTOR_TRANSPORT` |
| Format | `dgn007-capture-body/v1` |
| Implementierung | [reiner Decoder](../../../../Tests/Contracts/dgn007_collector_transport.py) |
| Methodenbezug | [prospektiver Prüfvertrag](README.md), `DEC-068` |
| Abnahmegrenze | synthetischer JSON-Transport und deklarierte Recordbindungen; keine SQL-Runtime-Abnahme |

Der Decoder ist ein begrenzter Teil des noch offenen Collectors. Er nimmt
genau ein JSON-Textdokument und einen bereits validierten
`AcceptanceContract` entgegen. Er liefert einen unveränderlichen `CaptureBody`
mit skalaren Fenster-, Request-, Familien-, Plan- und Union-Records. Er öffnet
keine Dateien oder Verbindungen und startet keine Prozesse. Die vorhandenen
SQL-Batches, der Statusrunner und der prospektive v1-Vertrag bleiben unverändert.

## Öffentliche API und Format

Der Caller stellt `contract_mapping` und `payload_text` bereit. Dieses
API-Beispiel führt keine SQL-Ausführung oder Dateiabfrage aus:

```python
from Tests.Contracts.dgn007_prospective_acceptance import contract_from_mapping
from Tests.Contracts.dgn007_collector_transport import decode_capture

contract = contract_from_mapping(contract_mapping)
body = decode_capture(payload_text, contract)
```

Die Headerfelder sind `schema`, `major`, `compatibility`, `scope`,
`contract_digest`, `source_digest` und `parent_object_id`. Erlaubt sind die
Paare `15/150`, `16/160`, `17/170` und ausschließlich die Kontrollscopes
`DGN-007_CONTROL_AB`, `DGN-007_CONTROL_BA`, `DGN-007_CONTROL_AA`. Beide Digests
müssen dem übergebenen Akzeptanzvertrag entsprechen. Das bindet deklarierte
Inputs; es attestiert weder einen tatsächlichen Vorabfreeze noch die Herkunft
aus einer bestimmten SQL-Instanz.

Der JSON-Body enthält genau diese Arrays. Ihre Feldnamen entsprechen exakt
den genannten Recordklassen; unbekannte oder fehlende Felder sind Fehler.

| Array | Anzahl | Recordtyp und Grenze |
|---|---:|---|
| `windows` | 2 | `WindowRecord`, chronologisch WindowId 0 und 1; Bedingungen gemäß AB/BA/AA |
| `requests` | 8 | eigener `RequestCapture`; je vier feste Parameterpaare, Ordinals und gebundene IDs |
| `families` | 1–12 | `QueryFamilyRecord`; gebundene Parent-/Variant-Familien der festen Suchprozedur |
| `plans` | 1–8 | `ActivePlanRecord`; positive reguläre Ausführungen innerhalb der gebundenen Fenster |
| `plan_union` | 1–8 | `PlanUnionRecord`; exakt dieselbe aktive Menge mit T0-/T1-Flags |

Die bestehenden Recordklassen stehen im
[prospektiven Evaluator](../../../../Tests/Contracts/dgn007_prospective_acceptance.py).
Der Decoder prüft Requestfolge, IDs, Counts, feste Parameterklassen,
Fenstergrenzen, Parent-/Variant-Bindung, Planidentität und Union-Konsistenz.
Ungenutzte historische Planzeilen, Plan XML und freie Querytexte gehören
nicht zum Transportformat. Die festen Objekt- und Statementmarker grenzen
den erlaubten synthetischen Suchscope ein.

## Präzision und Parsergrenzen

Das Textdokument ist auf 32.768 UTF-8-Bytes und JSON-Tiefe 8 begrenzt. Die
Grenzen werden vor der JSON-Decodierung geprüft. Integer-Tokens enthalten
höchstens 19 Ziffern; fachliche IDs und Counts besitzen zusätzliche Grenzen.
Doppelte Schlüssel werden auch innerhalb verschachtelter Records abgelehnt.
Abgeschnittene Dokumente, zusätzliche JSON-Dokumente, unbekannte Felder,
JSON-Floats, NaN und Infinity werden nicht stillschweigend übernommen.

Die fünf Fenstermetriken werden ausschließlich als Decimal-Text übertragen,
auch in wissenschaftlicher Schreibweise. Der Decoder verwendet unmittelbar
`Decimal(text)`, ohne einen Python-Float oder Druckrundung dazwischen.
Die bestehenden technischen Grenzen bleiben 34 signifikante Ziffern,
Exponent mindestens −30 und `adjusted()` höchstens 20; der einzelne Text ist
auf 64 Zeichen begrenzt. Nur endliche nichtnegative Werte sind zulässig.
Die Rows-Invarianten werden exakt über `Fraction` mit der bestehenden
Toleranz `0.000001` geprüft. Der globale Decimal-Kontext verändert die
übertragenen Werte oder diese Vergleiche nicht.

UTC-Zeitwerte bleiben ganzzahlige 100-ns-Ticks ab
`0001-01-01T00:00:00Z`, im Bereich `0..3155378975999999999`.
Eine Python-Datetime- oder Float-Zwischenrepräsentation wird nicht verwendet.
Planhashes besitzen genau 16 Hexzeichen ohne `0x`; Groß- und Kleinschreibung
sind zulässig. Der Record enthält anschließend exakt acht Bytes.

Diese Prüfung erhält die zulässige gelieferte Darstellung. Sie beweist keine
verlustfreie Erfassung in SQL und beseitigt keine Rundung, die bereits bei
der Query-Store-Aggregation oder vor Übergabe des Texts entstanden ist.

## Fehlende Ergebniszeilen ausdrücklich erhalten

`RequestCapture` enthält `window_id`, `ordinal`, `request_log_id`, `group_key`,
`status_code`, `returned_rows` und `row_evidence`.

| `row_evidence` | `returned_rows` | Bedeutung |
|---|---|---|
| `NOT_CAPTURED` | JSON `null` / Python `None` | Ergebniszeilen je Request wurden nicht geliefert; der Body bleibt in dieser Hinsicht unvollständig |
| `MEASURED` | Integer | Der Caller deklariert einen Messwert; der Decoder prüft ihn gegen den festen Ergebnisvertrag |

Der heutige [Setupvertrag](../Automated/10_Setup.sql) speichert im
`CaseRequestLog` ID, Parameter und Zeit, aber keine Ergebniszeilen.
[CONTROL_WINDOWS](../Automated/21_Controlled_Query_Store_Windows.sql) prüft
Ergebniscount und Ergebnisgleichheit während der Ausführung, persistiert den
Count jedoch nicht je Request. Der Decoder ergänzt deshalb niemals die
bekannten Erwartungszahlen als angeblich gemessene Werte.

`row_evidence_complete` bedeutet ausschließlich, dass alle acht gelieferten
Requests `MEASURED` deklarieren. Dieses Flag attestiert keine Messherkunft.
Auch ein solcher Body hat immer `runtime_attested=False` und
`validation_scope=PROJECT_SEMANTIC`. Es gibt keine Incidentbewertung und keine
automatische Umwandlung in einen vollständigen `RunRecord`. Phasenstatus,
Cleanup, Datenbankabwesenheit, Lifecycle-ID, Blockreihenfolge, Ressourcen und
Budgets werden weder ergänzt noch als bestätigt ausgegeben.

## Fehler und Prüfung

`TransportError` enthält ausschließlich `FAIL_CONTRACT` oder
`FAIL_RESULT_CONTRACT` aus
[`FWK-012`](../../../00_Framework/Contracts/FWK-012_Status_Error_Skip_Contract.md).
Schema-, Typ-, Parser- und Digestfehler ergeben `FAIL_CONTRACT`; ungültige
Werte oder Recordbindungen ergeben `FAIL_RESULT_CONTRACT`. Fehler geben
weder Payloadteile noch rohe Parserfehlerketten zurück. Der Transport hat
keinen eigenen Cleanup-/Timeoutpfad; die Fehlerpriorität des späteren
Coordinators bleibt ein eigener Vertrag.

```powershell
python Tests/Static/validate_dgn007_collector_transport.py
python Tests/Static/test_dgn007_collector_transport.py
python Tests/Static/validate_dgn007_prospective_acceptance.py
python Tests/Static/test_dgn007_prospective_acceptance.py
```

19 Transporttests mit parametrisierten Gegenproben und die bestehenden
34 Prospektivtests bestanden lokal, ebenso beide Validatoren. Der eigene
fünfminütige Statikworkflow prüft diese Grenze im temporären GitHub-Checkout.
Es wurden keine SQL-Instanzen gestartet und keine SQL-Läufe dieses
Transportformats ausgeführt; Producer und Coordinator fehlen noch.

## Nächster ausführbarer Schnitt

Der SQL-Producer muss Ergebniszeilen je Request tatsächlich erfassen und
die vollständige skalare Projektion nach der Evidenzphase und vor Cleanup
bereitstellen. Der bestehende Framework-Harness hält derzeit nur
Phasenresultate, keine Resultsets. Die Übernahme muss deshalb innerhalb des
Lifecycles erfolgen. Danach muss der Coordinator den integrierten Freeze,
Quellen, Zielinstanz, Ressourcen, tatsächliche serielle Reihenfolge und
Zeitbudgets prüfen sowie Cleanup und Datenbankabwesenheit unabhängig
bestätigen. Erst dann dürfen frische Bestätigungsläufe den prospektiven
Evaluator erreichen. Incident-, Ursachen-, Mitigations-, Capstone- und
Szenariofreigabe bleiben offen.

Technische Primärquellen, geprüft am 2026-10-07:
[Python Decimal](https://docs.python.org/3/library/decimal.html),
[Python JSON](https://docs.python.org/3/library/json.html).
Die Transportgrenzen und Evidenzdeklarationen sind Projektmethoden; die
Herstellerdokumentation belegt keine erfolgreiche SQL-Anbindung.
