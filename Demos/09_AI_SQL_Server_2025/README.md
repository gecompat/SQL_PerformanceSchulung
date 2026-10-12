# KI mit und für SQL Server 2025

[DGN-010](DGN-010_Index_Advice/README.md) ergänzt öffentliche begrenzte ungezwungene
SELECT- und Owner-UPDATE/Rollback-Profile ohne/mit Candidateindex. Numerische
Invarianten sind von Runtime-/TP-PERF-Abnahme getrennt; der Gesamtstatus bleibt
WARN, DGN-010 PROPOSED. Aktuelle Indexnutzung, vollständige Kosten und Nettonutzen
sind offen. Keine Modell-/Cloudaufrufe oder automatische Übernahme von Indexrat.

Lokale, synthetische T-SQL-Demos ohne Modell- oder Cloudzugriff. Die Umsetzung umfasst QRY-014 bis QRY-019, DGN-008/009 und CON-010; QRY-018 ist ein Offline-RAG-Replay, QRY-019 prüft feste SQL-Struktur und gebundene Werte. Die Ordnernummer bezeichnet nur die Ablage. Lernmodule, geplante Folgeschritte und Evidenzgrenzen stehen im [Workstream-Plan](../../Documentation/Project_Planning/SQL_SERVER_2025_AI_WORKSTREAM_PLAN.md).

[RES-008](RES-008_Vector_Dimensions/README.md) ergänzt einen öffentlich ausführbaren
begrenzten float32-Consumer mit tatsächlichen Quellen, Messfenstern, Plänen und
Recovery. Sein [Teilnachweis](../../Documentation/Project_Planning/SQL_SERVER_2025_AI_RESOURCE_PUBLIC_REVIEW.md)
führt Versions-SKIPs und Beobachtungs-WARNs sichtbar. RES-008 bleibt PROPOSED;
vollständige Ergebnisaggregation, Demo-/TP-PERF- und Modulabnahme sind offen.
