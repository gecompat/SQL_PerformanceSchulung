# Implementierungsschnitte nach ADV-004 und ADV-005

Die spätere Umsetzung unter `ADV-008` (Review QRY-004) erfolgt nicht als gemeinsamer Groß-PR. Verbindliche Reihenfolge und Abhängigkeiten:

1. `OPT-015` (Ausführungspläne systematisch lesen): planweite und operatorbezogene Eigenschaften; grüner Versionsmatrix-Schnitt.
2. `OPT-016` (Wiederholte Operatorausführung und Zwischenspeicherung): Rebind/Rewind/Outer References/Spools; grüner Schnitt mit planformabhängigem Skip.
3. `QRY-013` (Anwendung langsam, Verwaltungswerkzeug schnell): neutraler Clientkontext und Cacheattribute; grüner Multi-Session-Schnitt.
4. `QRY-004_CLASSIC_AND_DYNAMIC`: Catch-all, Recompile und sicher parameterisiertes dynamisches SQL.
5. `OPT-009_PSP`: PSP (Parameter Sensitive Plan Optimization; Planoptimierung für unterschiedliche Parameterwerte) einschließlich Feature- und Eligibility-Skips.
6. `OPT-010_OPPO`: OPPO (Optional Parameter Plan Optimization; Planoptimierung für optionale Parameter) einschließlich SQL-Server-2025-/CL170-Vertrag.
7. `OPT-017` (Ungleich verteilte parallele Arbeit): parallele Planbereiche und Skew; gelber Ressourcenprofil-Schnitt.
8. LAB-VP1- und LAB-VP2-Orchestrierung, Übergänge und Transferaufgaben.

`OPT-015` und das gemeinsame Datenmodell dürfen parallel zum `QRY-013`-Clientsimulator begonnen werden. PSP und OPPO setzen das deterministische Suchdatenmodell und die klassische `QRY-004` (Optionale Filter, Recompile und dynamisches SQL)-Abnahme voraus. `OPT-017` wird erst umgesetzt, wenn ein geeignetes paralleles Testprofil verfügbar und im Demo-Katalog begründet ist.
