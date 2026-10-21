# Präsentationsvarianten

Wählen Sie den Umfang passend zu Vorwissen und verfügbarer Zeit:

| Profil | Schwerpunkt |
|---|---|
| BASIS | Grundlagen und ein verständlicher Einstieg in Abfragen, Pläne und typische Performancefragen |
| STANDARD | Der gemeinsame Praxispfad für Entwickler und Administratoren |
| VERTIEFUNG | Zusätzliche technische Zusammenhänge und anspruchsvollere Diagnose- und Entwurfsfragen |

## Direkt mit den Folien arbeiten

Öffnen Sie den [vollständigen Foliensatz](../Performance_Schulung_Chat_2026-07-23_2146_SQL_Server_Performance_Grundlagen.pptx)
in PowerPoint Desktop. Unter **Bildschirmpräsentation → Benutzerdefinierte
Bildschirmpräsentation** können Sie `SQL Performance – Basis`,
`SQL Performance – Standard` oder `SQL Performance – Vertiefung` starten.
Die vollständige Präsentation bleibt erhalten.

Wenn Sie eine eigenständige Datei je Profil benötigen, folgen Sie der
[Variantenanleitung](../../Documentation/HowTo/PRESENTATION_VARIANTS.md).
Die dort erzeugten Dateien liegen lokal unter `build/`; sie werden nicht als
fertige Downloads in diesem Verzeichnis versioniert.

Die [Themenübersicht](../../Documentation/Curriculum/README.md) hilft bei der
inhaltlichen Auswahl, die [Demo-Erklärungen](../../Documentation/HowTo/DEMO_WALKTHROUGHS.md)
bei der Vorbereitung praktischer Beispiele.

## Für Bearbeitung und Erzeugung

- Das PowerPoint-Masterdeck unter `Presentations/` ist die einzige fachlich bearbeitete Präsentationsquelle.
- [Prüfschema für das Variantenmanifest](presentation_variants.schema.json) definiert den Vertrag für das produktive Manifest [Variantenmanifest mit der Folienzuordnung](presentation_variants.json).
- Das Manifest ordnet alle 102 stabilen SlideKeys den Profilen, Rollen, Claims, Quellen, Lernzielen und Demo-IDs zu.
- Der Unterordner `build/` ist für reproduzierbar erzeugte Varianten vorgesehen. Dateien dort sind Build- beziehungsweise Releaseartefakte und dürfen nicht manuell gepflegt werden.
- Die vollständigen fachlichen und technischen Regeln stehen in [PRS-011 – Vertrag für SlideKeys und Präsentationsvarianten](../../Documentation/Standards/PRESENTATION_VARIANT_MANIFEST_CONTRACT.md).

Die Arbeitspakete zur fachlichen und technischen Freigabe der Präsentationsvarianten
(`PRS-012` bis `TST-012`) sind durch [W-PRS-001 – Lehrmittelfreigabe](../../Documentation/Project_Planning/W_PRS_001_TEACHING_RELEASE.md) validiert. Bedienung, Build und Renderprüfung beschreibt [Präsentationsprofile verwenden und erzeugen](../../Documentation/HowTo/PRESENTATION_VARIANTS.md).
