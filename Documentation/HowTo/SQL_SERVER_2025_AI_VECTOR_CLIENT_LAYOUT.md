# Clientdateien und Dependency-Pfade offline vergleichen

Ein .NET-Client besteht aus seiner eigenen DLL und weiteren Bibliotheken.
Die Datei `*.deps.json` beschreibt den zugehörigen Paketgraphen. Ein Runtime
Identifier (RID (Row Identifier; physischer Zeilenverweis)) wie `win-x64` bezeichnet eine Plattformvariante. Die Prüfung
hier vergleicht einen festen Windowsgraphen mit bereitgestellten Dateimetadaten.
Sie lädt keine DLL und öffnet keine SQL-Verbindung.

## Kleiner Entscheidungsfall

Ein Deps-Eintrag nennt beispielsweise
`runtimes/win-x64/native/Microsoft.Data.SqlClient.SNI.dll`. Im Appbestand liegt
nur `Microsoft.Data.SqlClient.SNI.dll`, mit dem gleichen vollständig gebundenen
SHA256. Das ist ein Unterschied zwischen dem wörtlichen Unterpfad und dem
flachen Bestand. Ob der .NET-Host die Datei trotzdem findet, ist damit noch
nicht beantwortet. Ein generischer `lib/...`-Paketpfad wird nicht pauschal als
verpflichtender App-Unterordner interpretiert.

Für den festen Graphen werden 27 Pakete und 28 ausgewählte Windowsassets geprüft.
Fünf davon stammen aus `runtimeTargets`. Zusätzlich prüft der feste Graph 13
Ressourcenbeschreibungen mit ihren genauen Pfaden und Locales. Diese Einträge
zählen nicht zu den 28 Runtimeassets. Der Vertrag behauptet weder vorhandene
Satelliten-DLLs noch, dass sie optional oder unnötig seien; ihre Ladefähigkeit
bleibt NOT_ESTABLISHED. Fehlende oder zusätzliche Assets,
falsche SHA256, unsichere relative Pfade und gleichnamige Dateien aus mehreren
Quellen werden abgewiesen. Die vollständigen Deps- und Compilerproofbytes sind
getrennt gebunden; eine nachträglich neu formatierte JSON-Datei hat einen
anderen Hash.

## Prüfung im Speicher

```python
from vector_client_layout_evidence import report

# Originalbytes und vollständige Dateimetadaten aus einer bereitgestellten Akte:
# deps_bytes, compiler_proof_bytes, files, binding
summary = report(deps_bytes, compiler_proof_bytes, files, binding)
print(summary)
```

`Tests/Static` kann im Pythonpfad liegen. Das Modul liest nur seinen festen
eigenen Expected-Vertrag. Es akzeptiert keinen frei wählbaren Rohdateipfad.
`source_binding()` bindet Consumer und Expecteddatei. Die Callerdateimetadaten
bleiben deklariert; ihre Herkunft wird durch diese reine Prüfung nicht
unabhängig attestiert. Die historische Variante ist auf die erhaltenen
PR229-Artefaktpins begrenzt. Die mitgelieferte Handfixture ist fiktiv und
`PUREFIXTURE_ONLY`; sie enthält keine DLLs.

Die reinen Gegenfälle benötigen ausschließlich Python:

```powershell
python Tests/Static/test_vector_client_layout_evidence.py
```

## Was das Ergebnis bedeutet

Die Ausgabe enthält feste Statuswerte und begrenzte Counts. Sie enthält keine
Hostpfade, Paketgraphen, GUIDs, Rohbytes oder privaten Quellen.
`RELATIVE_PATHS_ABSENT_FLAT_BYTES_PRESENT` beschreibt nur den erfassten
Layoutunterschied. `SELECTED_RUNTIME_TARGET_PATHS_PRESENT` bedeutet, dass die
fünf wörtlichen Pfade in den übergebenen Metadaten stehen. Beide Ergebnisse
bleiben WARN.

Loader, Typed API (Application Programming Interface; Programmierschnittstelle), TDS (Tabular Data Stream; Übertragungsprotokoll zwischen SQL-Client und Server), SQL und Runtimequalifikation bleiben
NOT_ESTABLISHED: dieser konkrete Ausführungspfad ist dadurch noch nicht
geprüft. Der Ursprung der historischen `FileNotFoundException` bleibt
UNPROVEN. Die Ausnahme bezeichnet allein noch nicht die fehlende Datei.
Kein Ergebnis erlaubt das Fortsetzen einer bereits gestoppten UNKNOWN-Welle.

Zum fachlichen Unterschied zwischen Treiberdokumentation und tatsächlichem
Transportnachweis siehe den [VECTOR-Kompatibilitätsguide](SQL_SERVER_2025_AI_VECTOR_COMPATIBILITY.md).
Für diesen Lese- und Prüfungsschritt ist keine Installation, Providerprobe,
Modellabfrage oder SQL-Ausführung erforderlich.
