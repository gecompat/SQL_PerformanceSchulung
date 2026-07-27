# Laufzeitzustand

Dieses Verzeichnis ist für lokalen Szenario-, Lab- und Prozesszustand vorgesehen. Dazu gehören beispielsweise Run-IDs, Status-Snapshots, PID-Informationen oder lokale Lifecycle-Metadaten.

Der Inhalt ist installations- und laufabhängig und wird vollständig von Git ausgeschlossen. Dateien in diesem Verzeichnis dürfen keine Secrets enthalten und sind nach kontrolliertem Stop, Reset oder Remove zu löschen. Ein Lauf darf nicht allein aufgrund vorhandener State-Dateien als aktiv oder erfolgreich gelten.
