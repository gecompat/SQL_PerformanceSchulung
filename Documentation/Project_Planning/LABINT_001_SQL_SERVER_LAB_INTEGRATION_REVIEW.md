# Review – LABINT-001 SQL_Server_Lab-Testautomation

| Merkmal | Wert |
|---|---|
| Status | `VALIDATED` |
| Stand | 2026-07-27 |
| Pull Request | `#21` |
| Schulungs-Ausgangscommit | `091fa8606491d6f5fff2f3cd483d11868ce7d5e7` |
| geprüfter Lab-Commit | `08fcc9525b9bbc29a5dd9a2ef08de23bd7ef650e` |
| Änderungen in SQL_Server_Lab | keine |
| Runtime-Provisionierung ausgeführt | nein |

## 1. Prüfumfang

Geprüft wurden die exportierten Lab-Commands, Docker- und Podman-Provider, das aktuelle Lab-Manifestschema, Versionen- und Ressourcenprofile, State- und Cleanup-Lifecycle, der Integrationstest des Lab-Repositories sowie der dokumentierte Project-Adapter-/Lab-Package-Vertrag.

Im Schulungsrepository wurden die sechs aktuell produktiven Demo-Manifeste, der gemeinsame Demo-Harness, die vorhandenen Runtime-Matrizen und die Safety-Verträge ausgewertet.

## 2. Technische Bewertung

Die bestehende Lab-Implementierung ist für einen ersten externen Schulungsrunner ausreichend. `New-SqlServerLab` kann Docker oder Podman provisionieren und liefert den gebundenen SQL-Endpunkt zurück. Der vorhandene Schulungs-Harness bleibt für Demo-Phasen, Assertions und fachlichen Cleanup verantwortlich. `Remove-SqlServerLab -Force` entfernt anschließend die scopegebundene Infrastruktur.

Eine native Package-Ausführung im Lab ist noch nicht möglich. Der Project-Adapter-/Lab-Package-Vertrag ist dokumentiert, aber die aktuelle Runtime verarbeitet nur das einfachere Instanz-/Datenbank-/Post-Provision-Manifest.

## 3. Erzeugte Artefakte

- `Documentation/Architecture/SQL_SERVER_LAB_TEST_AUTOMATION.md`;
- `Tests/Lab/performance-lab-matrix.json`;
- `Tests/Lab/performance-lab-matrix.schema.json`;
- `Tests/Lab/README.md`;
- `Tests/Static/validate_sql_server_lab_test_catalog.py`;
- `.github/workflows/sql-server-lab-test-catalog.yml`;
- synchronisierte Infrastruktur-, Test-, Backlog- und Statusdokumentation.

## 4. Aktueller Katalog

Der Katalog umfasst:

- `QRY-001`;
- `OPT-002`;
- `CON-004`;
- `OPT-013`;
- `OPT-015`;
- `OPT-016`.

Die vollständige Container-Matrix umfasst zwei Provider, drei SQL-Server-Versionen, sechs Demos und zwei Wiederholungen. Daraus entstehen aktuell 72 vollständige Demoläufe.

## 5. Statische Abnahme

Die neue Prüfung validiert:

- exakte Übereinstimmung zwischen produktiven Demo-Manifests und Katalog;
- Demo-ID, Pfad und Sicherheitsstufe;
- Docker-/Podman- und Versionszuordnung;
- Ressourcenprofil und Environment-Isolation;
- Multi-Session-Capability;
- Safety-Bestätigungen für gelbe und rote Lanes;
- Demo-Cleanup-Vertrag;
- Verbot von Secret-, Host- und absoluten Pfadangaben;
- Dokumentations- und Backlogkonsistenz;
- vollständigen Repository-Privacy-Scan.

Erfolgreich abgeschlossen wurden:

- `SQL Server Lab integration contract`, Lauf `30241515448`;
- `Framework contracts`, Lauf `30241515399`;
- `Curriculum and privacy validation`, Lauf `30241515405`;
- `Advanced lab design contracts`, Lauf `30241515387`;
- `Advanced lab design contracts VP3-VP5`, Lauf `30241515443`;
- `W2-001 legacy example classification`, Lauf `30241515410`.

## 6. Keine Lab-Änderung in dieser Welle

Im Repository `gecompat/SQL_Server_Lab` wurden weder Dateien noch Issues, Branches oder Pull Requests angelegt oder verändert.

## 7. Separat abzustimmende Lab-Erweiterungen

Für die endgültige native Integration werden im Lab-Repository benötigt:

1. implementierte Project-Adapter-/Lab-Package-Engine;
2. implementierte öffentliche Commands `Invoke-LabCleanup` und `Invoke-LabRecovery`;
3. providerneutraler Orphan-Cleanup für Docker und Podman;
4. öffentlicher Capability-, Build- und Image-Digest-Nachweis;
5. Ressourcenübersteuerung mit sichtbarem Defizit statt vollständigem `SkipAssessment`;
6. strukturierter nichtinteraktiver Event-, Result- und Exitcode-Vertrag.

Diese Punkte werden nur nach ausdrücklicher Freigabe im Lab-Repository umgesetzt.

## 8. Nicht durchgeführte Prüfungen

Es wurde keine Docker- oder Podman-Umgebung über `SQL_Server_Lab` provisioniert. Der Grund ist die bewusst begrenzte Welle `LABINT-001`: Zunächst werden Discovery, Katalog, Sicherheitsgrenzen und Abhängigkeiten verbindlich gemacht. Der reale Runner und seine Runtime-Abnahme folgen unter `LABINT-002`.

## 9. Statusgrenze

`LABINT-001` ist als Architektur-, Katalog- und statischer Prüfvertrag `VALIDATED`. Diese Freigabe bestätigt keine reale Provider-, Provisionierungs- oder Demolaufprüfung über `SQL_Server_Lab`.

## 10. Nächster Schritt

`LABINT-002` implementiert die grünen Lanes `SMOKE` und `CORE`. Erst nach erfolgreichem End-to-End-Cleanup folgen `PROVIDER_PARITY`, gelbe Demos und die vollständige Container-Matrix.
