# Validierungsgrenzen ADV-004 und ADV-005

Die statische Designabnahme bestätigt Vollständigkeit und Konsistenz von Lernzielen, Claims, Quellen, Datenmodell, Phasen, Risiken, Ressourcen, Versionen, Evidenzfeldern und Skip-Codes. Sie bestätigt nicht, dass SQL Server in jeder Version eine konkrete optionale Planform erzeugt.

Für Spools, Row Goals, Parallelität, PSP und OPPO gilt deshalb:

- dokumentierte Produktvoraussetzungen werden als Primärgrenze geprüft,
- konkrete Optimizerentscheidungen benötigen spätere Runtime-Evidenz,
- nicht erzeugte optionale Planformen führen bei geeignetem Setup zu einem begründeten Skip,
- ein Skip darf weder als Erfolg der Kernaussage noch als Produktfehler umgedeutet werden,
- Runtimefreigabe erfolgt ausschließlich in `ADV-008` und Gate V3.
