# Sprachstil und Übersetzungsregeln

| Merkmal | Wert |
|---|---|
| Status | `VERBINDLICH` |
| Stand | 2026-07-28 |
| Geltungsbereich | Dokumentation, Kommentare, Commit Messages, Pull Requests, AI-Metadaten, Entwicklerdokumentation und sonstige Projekttexte |
| Ergänzender Standard | [`TERMINOLOGY_AND_STYLE_STANDARD.md`](TERMINOLOGY_AND_STYLE_STANDARD.md) |

## 1. Grundsatz

Alle Projekttexte verwenden einen einheitlichen Sprachstil. Bestehende, fachlich präzisere Projektkonventionen haben Vorrang. Neue Texte orientieren sich an der vorhandenen hochwertigen Dokumentation und fügen sich ohne erkennbaren Stilbruch ein.

Projekt- und Dokumentationssprache ist grundsätzlich Deutsch. Ein Dokument verwendet nur eine Hauptsprache, sofern nicht eine ausdrücklich gepflegte Sprachfassung oder ein technisch notwendiger Originaltext vorliegt.

## 2. Technische Originalbegriffe

Technische Fachbegriffe, Produktnamen, Programmiersprachen, SQL-Befehle, API-Namen, Dateinamen, Parameter, Klassen-, Methoden- und Funktionsnamen werden nicht übersetzt. Dies gilt insbesondere für Bezeichnungen wie `SQL Server`, `Docker`, `Podman`, `Hyper-V`, `PowerShell`, `Pull Request`, `Commit`, `README.md` und `Invoke-SmokeTest`.

Code, Befehle, Konfigurationswerte und Beispiele müssen der tatsächlichen Implementierung exakt entsprechen. Bezeichner dürfen weder sinngemäß angepasst noch übersetzt werden.

## 3. Etablierte englische IT-Begriffe

Etablierte englische IT-Begriffe bleiben auch in deutschsprachigen Texten erhalten, wenn eine deutsche Übersetzung ungebräuchlich, künstlich oder missverständlich wäre. Bevorzugt werden insbesondere `Pull Request`, `Repository`, `Branch`, `Commit`, `Workflow`, `Provider`, `Runtime`, `Setup` und `Cleanup`.

Künstliche Ersatzbegriffe wie „Zusammenführungsanfrage“, „Versionsverwaltungseinreichung“ oder „Quelltextverwahrungsort“ sind nicht zu verwenden.

Existiert für einen Fachbegriff keine etablierte deutsche Übersetzung, bleibt der Originalbegriff erhalten. Neue Fachbegriffe dürfen nicht erfunden werden.

## 4. Übersetzungen

Vorhandene Dokumentation wird nicht allein zur sprachlichen Vereinheitlichung übersetzt. Eine Übersetzung ist nur vorzunehmen, wenn sie ausdrücklich verlangt wird, die Dokumentation dadurch nachweisbar konsistenter wird oder mehrere Sprachversionen offiziell und dauerhaft gepflegt werden.

Eine Übersetzung darf technische Bedeutung, Gültigkeitsgrenzen, Bezeichner, Code, Befehle oder Beispiele nicht verändern. Bei mehreren offiziellen Sprachfassungen müssen fachliche Änderungen in allen gepflegten Fassungen konsistent nachgezogen werden.

## 5. Stil

Texte sind sachlich, eindeutig, technisch präzise, gut lesbar und möglichst zeitlos zu formulieren. Marketing-Sprache, übertriebene Werbung, unnötige Füllwörter, emotionale Formulierungen, Spekulationen und unbegründete Wertungen sind unzulässig.

Technische Aussagen müssen nachvollziehbar zwischen dokumentierten Fakten, empirischen Beobachtungen, Methoden, Inferenzen und Vermutungen unterscheiden. Ergänzend gelten die Aussageklassen und Fachterminologie aus [`TERMINOLOGY_AND_STYLE_STANDARD.md`](TERMINOLOGY_AND_STYLE_STANDARD.md).

Nach Möglichkeit ist aktiv zu formulieren, sofern dadurch Verantwortlichkeit und Ablauf klarer werden. Beispielsweise ist „The provider validates the manifest.“ der passiven Form „The manifest is validated by the provider.“ vorzuziehen. Passivkonstruktionen bleiben zulässig, wenn der Handelnde unbekannt, unerheblich oder die passive Form fachlich präziser ist.

## 6. Terminologische Konsistenz

Gleiche Konzepte werden im gesamten Projekt gleich bezeichnet. Synonyme mit wechselnder Sprache sind zu vermeiden. Insbesondere werden nicht parallel `Provider` und „Anbieter“, `Branch` und „Zweig“ oder `Commit` und „Einspielung“ für dasselbe technische Konzept verwendet.

Die verbindlichen SQL-Server-Begriffe sind in [`TERMINOLOGY_AND_STYLE_STANDARD.md`](TERMINOLOGY_AND_STYLE_STANDARD.md) festgelegt. Bei einem Konflikt zwischen allgemeiner Sprachregel und fachlich definierter Terminologie hat der fachlich spezifischere Standard Vorrang.

## 7. Commit Messages und Pull Requests

Commit Messages und Pull Requests verwenden denselben sachlichen und technisch präzisen Stil wie die Projektdokumentation. Commit Messages bleiben kurz, eindeutig und fachlich korrekt. Die Regeln für KI-generierte Commit Messages in [`CONTRIBUTING.md`](../../CONTRIBUTING.md) und [`.ai/PROJECT_RULES.md`](../../.ai/PROJECT_RULES.md) bleiben unverändert verbindlich.

Technische Originalbegriffe werden auch in Commit Messages und Pull Requests nicht übersetzt. Ein englischer Commit-Satz ist zulässig, wenn dies der etablierten Commit-Praxis des Projekts entspricht; innerhalb derselben Commit Message ist unnötige Mischsprache zu vermeiden.

## 8. KI-Verhalten

KI-gestützte Änderungen müssen vor dem Schreiben die vorhandenen Projektregeln, den Terminologie- und Schreibstandard sowie den sprachlichen Kontext der betroffenen Datei prüfen. Bestehende projektspezifische Regeln haben Vorrang vor allgemeinen Modellkonventionen.

Neue Texte müssen sich sprachlich und terminologisch in den vorhandenen Kontext einfügen. Die KI darf vorhandene Dokumente nicht ohne fachlichen oder ausdrücklich beauftragten Grund vollständig übersetzen oder sprachlich umgestalten.

## 9. Prüfung

Bei jeder Änderung ist zu prüfen, ob Hauptsprache, Fachbegriffe, Bezeichner, Beispiele und Terminologie konsistent bleiben. Stilbereinigungen dürfen keine fachlichen Aussagen, Versionsgrenzen, Sicherheitsregeln oder technischen Verträge verändern.
