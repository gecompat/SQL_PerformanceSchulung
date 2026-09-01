# W-SQL25-001 – SQL-Server-2025-Delta-Review

| Merkmal | Wert |
|---|---|
| Status | `COMPLETED` |
| Stand | 2026-08-28 |
| Quellen | `SRC-058` bis `SRC-065` |
| Umfang | Quellen-, Claim- und Entscheidungsgrundlage; keine neue Featuredemo |

## 1. Entscheidungsregel

`ADOPT` übernimmt eine belegte Aussage in einen bestehenden Curriculum- oder Demokontext. `DEFER` hält die Funktion zurück, bis Abhängigkeiten, Safety oder Infrastruktur belegt sind. `OUT_OF_SCOPE` dokumentiert die Abgrenzung zum aktuellen Performance-Curriculum. Keine Entscheidung hebt einen Demo- oder Gate-Status ohne Runtime-Evidenz an.

## 2. Entscheidungsmatrix

| Funktion | Quellen | bestehender Bezug | Entscheidung | Begründung und nächste Bedingung |
|---|---|---|---|---|
| CE Feedback für Ausdrücke | `SRC-058`, `SRC-061` | `OPT-006`, `ADV-CLM-033` | `ADOPT` | SQL Server 2025, CL 160+, Datenbankkonfiguration, wiederkehrende Ausdrucksmuster und tatsächliche Feedbackevidenz. Keine neue Demo; ein späterer `OPT-006`-Schnitt prüft Showplan-, XE- oder Cacheevidenz und Regression Protection. |
| Optimiertes `sp_executesql` | `SRC-058`, `SRC-059` | `QRY-004`, `ADV-CLM-018` | `DEFER` | Die Option ist standardmäßig aus und adressiert konkurrierende Compilation identischer Batches. `QRY-004` ist inzwischen runtimevalidiert; ein eigener Concurrent-Compile-Designschnitt darf nun bewertet werden, bleibt aber bis zu dieser Detailanalyse zurückgestellt. |
| Zeitgebundene XE-Sessions | `SRC-058`, `SRC-060` | `DGN-005`, `ADV-CLM-036` | `ADOPT` | `MAX_DURATION` wird als optionaler, auf Engine 17 begrenzter Schutzpfad an `DGN-005` gebunden. Der Basispfad behält explizites Stoppen, `STARTUP_STATE = OFF`, Ring-Buffer-Limit und Cleanup. |
| TempDB Space Resource Governance | `SRC-058`, `SRC-062` | `CON-009`, `RES-004`, `ADV-CLM-027` | `DEFER` | Resource Governor verändert Instanzzustand und kann Requests mit Fehler 1138 abbrechen. Erforderlich sind Editionstest, rotes Safety-Design, dedizierte Wegwerfinstanz, Recovery und getrennte Behandlung von Datenfiles, Log und Version Store. |
| Ordered nonclustered Columnstore | `SRC-058`, `SRC-063` | `IDX-010` | `DEFER` | Nutzen hängt von Segmentüberlappung, Datenverteilung, DOP, Online-/Offline-Build, TempDB-Platz und Edition ab. Erst nach einem gelben Detaildesign mit `sys.column_store_segments` übernehmen. |
| Query Store auf lesbaren Secondary Replicas | `SRC-058`, `SRC-064` | kein unmittelbarer Slice | `DEFER` | Das Feature bleibt Preview und benötigt eine Always-On-Availability-Group-Topologie. Es wird weder `DGN-003` noch `DGN-007` zugeschlagen, solange Mehrinstanz-Infrastruktur und Preview-Freigabe fehlen. |
| Vector- und KI-Funktionen | `SRC-058`, `SRC-065` | kein bestehendes Lernziel | `OUT_OF_SCOPE` | Datentyp, Suche, Modelle und externe KI-Integration bilden einen eigenen Lehrstrang. Keine Featuredemo und kein neues Modul. |

## 3. Claim-Fortschreibung

- `ADV-CLM-033` nennt CE Feedback für Ausdrücke ausdrücklich als SQL-Server-2025-Variante mit eigener Eligibility und Evidenz.
- `ADV-CLM-036` erlaubt ab SQL Server 2025 `MAX_DURATION` als zusätzlichen Schutz, ersetzt aber nie das explizite Stop-/Cleanup-Protokoll.
- `ADV-CLM-018` bleibt unverändert: sichere Parametrisierung ist unabhängig von `OPTIMIZED_SP_EXECUTESQL`; die Option ist keine allgemeine Aussage zur Queryqualität.
- `ADV-CLM-027` bleibt eine Ursachenabgrenzung. TempDB-Governance wird nicht als Mitigation übernommen, bevor der instanzweite Safety-Vertrag vorliegt.

## 4. Stop-Regeln

- Kein optimiertes `sp_executesql` ohne eigenen Concurrent-Compile-Designschnitt; die dafür vorausgesetzte `QRY-004`-Runtimefreigabe liegt vor.
- Keine Resource-Governor- oder Columnstore-Featuredemo ohne Edition-/Versionsprüfung, Safety-Klasse, Zeitbudget, Kill-Switch und Cleanup.
- Kein Query-Store-Secondary-Schnitt während Preview und ohne freigegebene Mehrinstanztopologie.
- Vector-/KI-Themen nur nach einer ausdrücklichen Curriculumentscheidung.

## 5. Ergebnis

Der Delta-Review übernimmt zwei Aussagen, stellt vier Funktionen zurück und klassifiziert Vector-/KI-Funktionen außerhalb des Curriculums. Er erzeugt keine neue Demo-ID und verändert die Entwicklungsreihenfolge nicht.
