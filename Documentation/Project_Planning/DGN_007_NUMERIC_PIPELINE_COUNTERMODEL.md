# DGN-007 – Numerische Pipelinegegenprobe

| Merkmal | Wert |
|---|---|
| Stand / Quellenprüfung | 2026-10-07 |
| geprüfte Repositorybasis | `2787619d624b30c02cd1eb16a8c272b7f436cd45` nach PR79 |
| Status | `IMPLEMENTED_STATIC_COUNTERMODEL`; 28 synthetische Tests lokal PASS |
| Geltung | `PROJECT_SEMANTIC`; ausschließlich endliche synthetische Vergleichsdaten |
| Grenze | keine SQL-Konversionsemulation, Acquisition-, Runtime- oder Methodenattestation |

## Getrennte numerische Ebenen

Die bisherigen [Sättigungsgegenproben](DGN_007_SATURATION_COUNTERMODEL.md)
zeigen bereits, dass exakte Textgewichtung eine vorangehende Floatabweichung
nicht beseitigt. Dieser engere Schnitt ergänzt eine unabhängig vorgegebene
Individualwertpopulation und trennt die Übergänge. Er verändert weder den
vorhandenen Consumer noch G13, v1, DEC-068, SQL21/35 oder die 27 Runtimequellen.
Der [Floatregel-Kandidat](DGN_007_METHOD_DECISION_PACKAGE.md) bleibt offen.

| Ebene | Daten und Aussage |
|---|---|
| Oracle | endliche synthetische Individualwerte als exakte `Fraction`; vollständige Indexpartition |
| Fragmentmittel | exaktes Mittel der dem Fragment zugewiesenen Oraclewerte |
| deklarierter Zwischenwert | separat vorgegebene `declared_rounded_mean`; keine Rundungsfunktion oder Engineprobe |
| vorgegebener Text | separat vorgegebener `synthetic_style3_text`; keine Formatierung des Zwischenwerts |
| Consumer | exakte Countgewichtung der endlichen Decimaltexte über `Fraction` |

Das Modell erhält Zwischenwert und Text unabhängig. Eine Abweichung zwischen
ihnen ist ein auswertbarer Gegenfall, keine ungültige Eingabe. Es berechnet
die Differenzen Zwischenwert minus exaktes Fragmentmittel, Textwert minus
Zwischenwert und Consumer minus Oracle getrennt, außerdem die gewichteten
Zwischenergebnisse. Kein Ergebnis legt eine universelle Fehlertoleranz fest.
Ein gültiger Modellinput ist kein positiver QS-Stabilitätsbeleg.

Microsoft dokumentiert Style3 als eindeutige 17-stellige Darstellung einzelner
Float-/Realwerte ab SQL Server 2016. Die Garantie betrifft einzelne Werte;
eine Invarianz beliebiger aggregierter Fragmentmittel folgt daraus nicht.
`float` und `real` sind näherungsweise Datentypen. Das sind Produktgrenzen,
keine beobachtete Ursache eines historischen G13-Fehlers.
[CAST/CONVERT](https://learn.microsoft.com/en-us/sql/t-sql/functions/cast-and-convert-transact-sql?view=sql-server-ver17),
[FLOAT/REAL](https://learn.microsoft.com/en-us/sql/t-sql/data-types/float-and-real-transact-sql?view=sql-server-ver17).

## Drei konkrete Gegenproben

1. **Exakte Partition:** Oracle `1,2,3,4`, Ganzfragment `count4/mean=5/2`
   gegen zwei Fragmente `count2/mean=3/2` und `count2/mean=7/2`. Separat
   vorgegebene Texte `2.5000000000000000e+000`,
   `1.5000000000000000e+000` und `3.5000000000000000e+000` ergeben jeweils
   exakt `5/2`. Das ist ein kontrollierter Positivfall, keine allgemeine
   Enginegarantie.
2. **Deklarierte Rundungsabweichung:** Oracle `1,2,2,2`, erstes Dreierfragment
   mit exaktem Mittel `5/3`. Der separat deklarierte Zwischenwert ist
   `7505999378950827/4503599627370496`; separat vorgegebener Text ist
   `1.6666666666666667e+000`. Das letzte Einerfragment hat Wert und Text `2`.
   Das gewichtete Zwischenmittel weicht um `1/18014398509481984` vom
   Oraclemittel `7/4` ab; das Consumerergebnis um `1/40000000000000000`.
   Die beiden Abweichungen sind verschieden. Das Modell attestiert weder die
   Herkunft des Zwischenwerts noch eine reale SQL-Style3-Konversion.
3. **Nicht injektives Ergebnis:** Die unterschiedlichen Populationen
   `1,1,2,3` und `1,2,2,2` haben jeweils Count vier und Mittel `7/4`.
   Ganzfragmente mit dem vorgegebenen Text `1.7500000000000000e+000`
   ergeben dasselbe Consumerergebnis. Gleicher Count und Mittelwert belegen
   keine identische Population, Herkunft oder kohärente Acquisition.

## API, Grenzen und Validierung

[`analyze_partition`](../../Tests/Contracts/dgn007_numeric_pipeline_countermodel.py)
verwendet unveränderliche `Fragment`- und Ergebnisrecords. Die Vergleichswerte
sind kontrollseitig vorgegebene Modellprämissen. Maximal 16 Werte und 16
Fragmente, 64 Zeichen je Text und 256 Bit je rationalem Eingabebestandteil
begrenzen diesen Vorschnitt; dies sind keine freigegebenen QS-/v1-Bounds.
Typ-, Form-, Zahlen- und Textgrenzen werden vor der Rechnung geprüft.
Brüche müssen kanonisch gekürzt sein; gefälschte ungekürzte Felder werden
abgelehnt. ASCII-Textsyntax, höchstens 34 Mantissenziffern und ein expliziter
Exponent von −30 bis 20 gelten vor der Decimalkonstruktion; der erzeugte
Decimalwert muss zusätzlich Exponent mindestens −30 und adjusted höchstens
20 besitzen. Auch dies sind ausschließlich Modellgrenzen.
Indexlücken, doppelte/fremde Indizes, unzulässige Typen, nicht endliche Texte
oder Größenoverflow ergeben feste Fehler ohne Rohfehler-/Payloadexport.

Decimaltexte werden ohne Floatumweg übernommen. Exakte `Fraction`-Rechnung
ist unabhängig von der ambienten Decimalpräzision; sie stellt verlorene
Enginepräzision oder den ursprünglichen Binärwert nicht wieder her.
[Python Decimal](https://docs.python.org/3.12/library/decimal.html),
[Python Fraction](https://docs.python.org/3.12/library/fractions.html).

```powershell
python -B Tests/Static/test_dgn007_numeric_pipeline_countermodel.py
```

Die [Testdatei](../../Tests/Static/test_dgn007_numeric_pipeline_countermodel.py)
gleicht zusätzlich die Ergebnisse mit der tatsächlichen bestehenden
`_ledger`-Gewichtung und dem bestehenden Transport-`_metric` ab.
Diese Verträge werden ausschließlich mit synthetischen Records importiert;
kein SQL, Prozesslauncher oder Collector wird gestartet. Tatsächliche
Prüfung unter Python 3.12.14/Windows: alle 28 Methoden PASS, ohne SKIP.
Der unabhängige Code-/Testreview ist abgeschlossen; die CI-Abnahme am
exakten aktuellen Head/Base folgt am PR.
Der [Workflow](../../.github/workflows/dgn007-numeric-pipeline.yml) bindet die
vier eigenen Dateien und die drei direkten/transitiven Consumer-Testquellen
exakt; bestehende SQL-/Bundle-/Streamingfilter bleiben erhalten.

## Verbleibende Grenzen

`runtime_attested` und `method_approved` bleiben `false`. Der Schnitt ist
keine RunRecord-, Incident-, Ursachen-, Mitigations- oder Capstoneabnahme.
PR68 und der zurückgestellte API-Schnitt bleiben ohne Freigabe. Die
gemeinsam versionierte SQL-/Freeze-/Transport-/Record-/Evaluator-/Coordinator-
Umsetzung braucht weiterhin eine tragfähige explizite Methodenentscheidung.
Als nächste technische Offline-Voraussetzung ist die tatsächliche
Importauflösungs-/UsedBytes-Probe zuerst konkret zu entwerfen: vertrauenswürdiger
Interpreter/Stdlib, kontrollierter Suchpfad und Loader, bereits bytegebundene
Bytes, gemessene Origins, keine Nachladung, Shadowing-/Austausch-/Alias-/Replay-
Gegenfälle und eigener Cleanup. Ein Entwurf allein attestiert keine Ausführung.
