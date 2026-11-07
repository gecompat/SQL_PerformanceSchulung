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

## Synthetische Grenzdaten

Verwende für beide Spalten dieselbe Kalendertagsachse, aber nur Werte, die der
jeweilige Typ darstellen kann.

| Ereignis | `datetime` | `datetime2(7)` |
|---|---|---|
| `START` | `2026-03-07 00:00:00.000` | `2026-03-07 00:00:00.0000000` |
| `LATE_1` | `2026-03-07 23:59:59.990` | `2026-03-07 23:59:59.9970000` |
| `LATE_2` | `2026-03-07 23:59:59.993` | `2026-03-07 23:59:59.9999999` |
| `DATETIME_LAST_TICK` | `2026-03-07 23:59:59.997` | – |
| `NEXT_DAY` | `2026-03-08 00:00:00.000` | `2026-03-08 00:00:00.0000000` |

Die Solltupel für den 7. März sind für `datetime` `{START, LATE_1, LATE_2,
DATETIME_LAST_TICK}` und für `datetime2(7)` `{START, LATE_1, LATE_2}`. Beide
Oracles schließen `NEXT_DAY` aus.

Vor einer SQL-Implementierung ist die endgültige Fixture so zu normalisieren,
dass jede erwartete `datetime`-Zeile nach Engine-Rundung eindeutig ist und die
typenbezogenen Vergleichsgruppen dieselbe fachliche Aussage beantworten.

## Geplante Varianten und Oracles

1. **Inklusives `BETWEEN` bis Mitternacht des Folgetages.** `BETWEEN @Start AND
   @NextDay` muss `NEXT_DAY` einschließen. Das dient als gezielter negativer
   Oracle für die vermeintlich exklusive Obergrenze.
2. **Typabhängiger Tagesendpunkt.** `23:59:59.997` kann für `datetime` den
   letzten darstellbaren Tageszeitpunkt bezeichnen. Derselbe numerische
   Endwert bei `datetime2(7)` schließt Werte bis `.9999999` aus. Ein aus einer
   Zeichenfolge konvertiertes `.999` kann bei `datetime` auf Mitternacht des
   Folgetages gerundet werden.
3. **Halboffenes Intervall.** `OccurredAt >= @Start AND OccurredAt < @NextDay`
   muss für beide Typen genau die erwarteten Tupel des Zielkalendertages
   zurückgeben und `NEXT_DAY` ausschließen. `@Start` und `@NextDay` sind
   typisiert; `@NextDay` wird mit `DATEADD(day, 1, @Start)` gebildet.

Die Abnahme vergleicht die vollständigen Ereignis-IDs mit dem erwarteten Tupel
und prüft zugleich den expliziten Grenzfall `NEXT_DAY`. Zeilenanzahl allein
genügt nicht. Keine Endzeit wird aus der letzten beobachteten Millisekunde
abgeleitet.

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

- Fixturewerte für beide Typen im ausführbaren SQL gegen Engine-Rundung prüfen.
- Den exakten Ergebnisvertrag und Cleanup vor einer Manifest- oder
  Katalogänderung an den geltenden Demo-Vertrag binden.
- Plan- und Read-Beobachtung als Diagnose dokumentieren, ohne einen
  Performanceclaim zu setzen.
- Methoden- und Quellenreview für den konkreten Implementierungsumfang
  abschließen; eine Designnotiz ersetzt diese Abnahme nicht.
