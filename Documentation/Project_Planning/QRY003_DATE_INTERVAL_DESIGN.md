# QRY-003 – Entwurf für halboffene Datumsintervalle

| Merkmal | Wert |
|---|---|
| Status | `PROPOSED_DESIGN` |
| Lernziel | `LO-M03-02` – halboffene Datumsintervalle und passende Datentypen |
| Nachbarkontrakt | `QRY-001` bleibt Eigentümer der Funktion-auf-Spalte-/SARGability-Gegenprobe |
| Laufstatus | nicht implementiert, nicht katalogisiert, nicht ausgeführt |

## Ziel und Grenze

Der Entwurf isoliert die Semantik einer Tagesgrenze: `BETWEEN` schließt beide
Endpunkte ein, während `>= @Start AND < @NextDay` den Folgetag ausschließt.
Künstliche inklusive Tagesendwerte werden für `datetime` und `datetime2(7)`
getrennt betrachtet. Der Entwurf ist ein Korrektheits- und Typpräzisionsbeispiel;
er sagt keinen Performancegewinn voraus.

Der bereits validierte `QRY-001`-Schnitt bleibt für eine gezielte
SARGability-Gegenprobe zuständig. `QRY-003` darf einen tatsächlichen Plan und
Logical Reads zur Einordnung anzeigen, aber weder einen Index Seek noch einen
Read- oder Laufzeitvorteil als feste Erwartung erzwingen.

## Quellenbasis

- [`SRC-133`](../Research/SOURCE_REGISTER.md): inklusive Grenzen von
  `BETWEEN`, Präzision und Rundung von `datetime` und `datetime2`, sowie
  Rückgabetyp von `DATEADD` bei typisiertem Datumseingang.
- [`SRC-012`](../Research/SOURCE_REGISTER.md): allgemeiner Index- und
  Suchargumentkontext; konkreter Zugriff bleibt eine empirische Eigenschaft
  von Daten, Index und Plan.
- [Lehrnotiz zu halboffenen Datumsintervallen](../Curriculum/HALF_OPEN_DATE_INTERVAL_LESSON.md)
  erklärt die Grundlagen. Diese Designnotiz ergänzt sie um eine mögliche
  Demoabfolge.

## Zielmatrix

| Engine | Compatibility Level | Typen |
|---|---:|---|
| SQL Server 2019 | 150 | `datetime`, `datetime2(7)` |
| SQL Server 2022 | 160 | `datetime`, `datetime2(7)` |
| SQL Server 2025 | 170 | `datetime`, `datetime2(7)` |

Die behauptete Semantik ist versionsübergreifend dokumentiert. Die Matrix
qualifiziert keine Builds, Editionen, Plattformen oder tatsächlichen Pläne.

## Synthetische Grenzdaten und vollständige Tupeloracles

Zwei getrennte Fixturevarianten verwenden jeweils eine Primärschlüsselspalte
`EventId int` und eine Spalte `OccurredAt`, einmal `datetime` und einmal
`datetime2(7)`. Die folgenden ISO-8601-Zeitpunkte sind die gespeicherten
Sollwerte. Für `datetime` werden ausschließlich darstellbare Millisekunden
verwendet; die Werte werden bei der Fixtureerzeugung nicht aus höherer
Präzision gerundet.

| `EventId` | Rolle | Solltupel `datetime` (`EventId`, `OccurredAt`) | Solltupel `datetime2(7)` (`EventId`, `OccurredAt`) |
|---:|---|---|---|
| 1 | Tagesbeginn | `(1, 2026-03-07T00:00:00.000)` | `(1, 2026-03-07T00:00:00.0000000)` |
| 2 | Tagesende, früher | `(2, 2026-03-07T23:59:59.990)` | `(2, 2026-03-07T23:59:59.9900000)` |
| 3 | Tagesende, später | `(3, 2026-03-07T23:59:59.993)` | `(3, 2026-03-07T23:59:59.9930000)` |
| 4 | letzter `datetime`-Tick | `(4, 2026-03-07T23:59:59.997)` | `(4, 2026-03-07T23:59:59.9970000)` |
| 5 | letzte `datetime2(7)`-Fraktion | – | `(5, 2026-03-07T23:59:59.9999999)` |
| 6 | Folgetagesbeginn | `(6, 2026-03-08T00:00:00.000)` | `(6, 2026-03-08T00:00:00.0000000)` |
| 7 | Folgetag, nächster Typ-Tick | `(7, 2026-03-08T00:00:00.003)` | `(7, 2026-03-08T00:00:00.0000001)` |

Die vollständigen Tupeloracles für das Zielintervall 7. März sind damit:

- `datetime`: `[(1, 2026-03-07T00:00:00.000), (2, 2026-03-07T23:59:59.990), (3, 2026-03-07T23:59:59.993), (4, 2026-03-07T23:59:59.997)]`;
- `datetime2(7)`: `[(1, 2026-03-07T00:00:00.0000000), (2, 2026-03-07T23:59:59.9900000), (3, 2026-03-07T23:59:59.9930000), (4, 2026-03-07T23:59:59.9970000), (5, 2026-03-07T23:59:59.9999999)]`.

Die getrennten Fixtures tragen denselben fachlichen Tag und Grenzfall, aber
die Typoracles unterscheiden sich bei der letzten darstellbaren Tagesfraktion.
Die `EventId`- und `OccurredAt`-Paare sind der vollständige projizierte
Ergebnisvertrag; ein späterer ausführbarer Vergleich muss jede Spalte und
Reihenfolge dagegen prüfen.

## Geplante Varianten und Oracles

1. **Inklusives `BETWEEN` bis Mitternacht des Folgetages.** Für `datetime`
   liefert `OccurredAt BETWEEN @Start AND @NextDay` die Tupel mit IDs
   `{1, 2, 3, 4, 6}`; ID 6 liegt exakt auf der inklusiven Obergrenze. Für
   `datetime2(7)` gilt dasselbe ID-Oracle. ID 7 bleibt in beiden Fällen
   außerhalb.
2. **Künstlicher Tagesendpunkt.** Mit `@End datetime =
   '2026-03-07T23:59:59.997'` liefert `BETWEEN @Start AND @End` für
   `datetime` IDs `{1, 2, 3, 4}`. Mit `@End datetime2(7) =
   '2026-03-07T23:59:59.997'` liefert dieselbe numerische Grenze ebenfalls
   `{1, 2, 3, 4}`, schließt aber den zusätzlichen gültigen Tageswert mit ID 5
   aus. Ein an `datetime` gebundener Endwert
   `@End = '2026-03-07T23:59:59.999'` wird auf
   `2026-03-08T00:00:00.000` gerundet und schließt ID 6 mit ein.
3. **Halboffenes Intervall.** `OccurredAt >= @Start AND OccurredAt < @NextDay`
   liefert für `datetime` exakt IDs `{1, 2, 3, 4}` und für `datetime2(7)`
   `{1, 2, 3, 4, 5}`. `@Start` und `@NextDay` sind jeweils explizit vom
   Spaltentyp; `@NextDay` wird als `DATEADD(day, 1, @Start)` gebildet. ID 6
   liegt gleich der exklusiven Obergrenze und wird ausgeschlossen.

Die Abnahme vergleicht die vollständigen `(EventId, OccurredAt)`-Tupel in
aufsteigender `EventId`-Reihenfolge mit den oben festgelegten Oracles. Sie
prüft `NEXT_DAY` (ID 6) und den nächsten repräsentierbaren Folgetagestick
(ID 7) getrennt. Zeilenanzahl allein genügt. Keine Endzeit wird aus der
letzten beobachteten Millisekunde abgeleitet.

## Diagnose und Aussagegrenzen

Falls ein ausführbarer Entwurf erstellt wird, bleiben Ergebnisoracle und
Leistungsdiagnose getrennt. Ein Index auf dem Zeitstempel ist nur ein
kontrollierter Zugriffskandidat. Die Abfragen dürfen mit tatsächlichem Plan
und statementbezogenen Logical Reads beobachtet werden; Planform und Reads
werden dokumentiert statt als versionsübergreifende Sollwerte festgeschrieben.
Es gibt keine feste Laufzeitschwelle und keinen Seek-/Scan-Hardcode.

Die Lehrdemo benötigt für eine spätere Implementierung einen eigenen markierten
Wegwerfkontext, typisierte Parameter, vollständiges Ergebnisoracle sowie
einen eigenen Setup-/Cleanupvertrag. Dieses Dokument erteilt keine
Ausführungsfreigabe und führt keine Datenbank-, SQL-, Container- oder
Teilnehmer-Generalprobe durch. Die menschliche Generalprobe bleibt aus dem
autonomen Auftrag ausgeschlossen.

## Offene Arbeit vor einer möglichen Implementierung

- Die festgelegten Fixturewerte für beide Typen im ausführbaren SQL gegen
  Engine-Rundung qualifizieren; die statischen Oracles sind hier vollständig.
- Den exakten Ergebnisvertrag und Cleanup vor einer Manifest- oder
  Katalogänderung an den geltenden Demo-Vertrag binden.
- Plan- und Read-Beobachtung als Diagnose dokumentieren, ohne einen
  Performanceclaim zu setzen.
- Methoden- und Quellenreview für den konkreten Implementierungsumfang
  abschließen; eine Designnotiz ersetzt diese Abnahme nicht.
