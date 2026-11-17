# W-PRS-001 – Lehrmittelfreigabe

| Merkmal | Wert |
|---|---|
| Welle | `W-PRS-001` |
| Arbeitspakete | `PRS-012`, `PRS-013`, `TST-011`, `TST-012` |
| Status | `VALIDATED` |
| Prüfdatum | 2026-09-01 |
| Masterdeck SHA-256 | `85bd14e4fc91d148889e9ebaa7128f6e1a213366f389aa6e2053f46cc0890ad3` |
| Manifest | `Presentations/variants/presentation_variants.json`, Schema-Version 1 |

## Ergebnis

Das Masterdeck enthält 102 eindeutige SlideKeys in den Speaker Notes und genau die drei vertraglich benannten Custom Shows. Das Manifest bildet die kumulativen Profile mit 41 Folien für `BASIS`, 66 Folien für `STANDARD` und 102 Folien für `VERTIEFUNG` ab. Der read-only Validator prüft Hash, Marker, Claims, Quellen, Lernziele, Demo-IDs, Rollen, Abhängigkeiten, Paarungen, interne Links sowie Custom-Show-Mitgliedschaft und -Reihenfolge.

Der interaktive PowerPoint-Desktop-Build erzeugte alle drei eigenständigen Varianten aus einer Kopie. Ausgeschlossene Folien wurden in absteigender Reihenfolge entfernt. Der Master-Hash war vor und nach dem Build identisch.

| Profil | Folien | SHA-256 der erzeugten Variante | Render |
|---|---:|---|---:|
| `BASIS` | 41 | `ebaa6c3ce170b594031a9bdffb604b147d75d2c02440a3acd53c2f2097769744` | 41 PNG |
| `STANDARD` | 66 | `dcef462891e039d77eec7262d9f3a4cf14d3d23d9a7c67a363bc88c2937c56eb` | 66 PNG |
| `VERTIEFUNG` | 102 | `86156c1da8bc15f534841fbc6810443c86b93560adbbba612b61f236eb2ffbfd` | 102 PNG |

Zusätzlich wurden alle 102 Masterfolien mit PowerPoint Desktop auf 1280 × 720 gerendert. Die 102 Master- und `VERTIEFUNG`-Renderings sind bytegleich. Die vollständige Kontaktbogenprüfung zeigte keine abgeschnittenen Inhalte, Platzhalter, Brandingabweichungen oder Reihenfolgefehler. Der Template-Fidelity-Check meldete `PASS`; der statische Varianten-, Notes-, Metadaten-, Privacy- und Branding-Check meldete ebenfalls `PASS`.

## Reproduzierbarer Bedienpfad

- Custom Shows aktualisieren: `Tools/Set-PresentationCustomShows.ps1`.
- Eigenständige Varianten erzeugen: `Tools/Build-PresentationVariants.ps1 -Profile ALL`.
- Master und Varianten rendern: `Tools/Test-PresentationVariantRenders.ps1`.
- Statischen Mastervertrag prüfen: `Tests/Static/validate_presentation_variants.py`.
- Erzeugte Varianten und Renderumfang prüfen: `Tests/Static/validate_presentation_variant_outputs.py`.

Die `.pptx`-Varianten und PNGs bleiben reproduzierbare lokale Buildartefakte und werden nicht als unabhängig gepflegte fachliche Quellen versioniert.

## Gate V4

Die für diese Welle verlangten Notes-, Manifest-, Custom-Show-, Build-, Render-, Metadaten-, Privacy-, Branding- und Profilumfangsnachweise liegen vor. Gate V4 ist damit `VALIDATED`.

## Nachfolgender Releasebuild vom 2026-11-17

Die drei Profildecks wurden erneut aus dem aktuellen Master auf `main`
(`b2a93520ccd92b6e9f14b66b192abc3dcccc0621`) gebaut. Der Master-Hash
`17c55c8f4e6a2ff06cd1e7d81118bdc5e50021d395f157aa65ed38351054d787` stimmte
vor und nach dem Build mit dem Manifest überein.

| Profil | Folien | Releaseartefakt-SHA-256 |
|---|---:|---|
| `BASIS` | 41 | `bf46ab88964310c0f3fdc8d37ee94e856c05c12994216c3627f73256c6230a2d` |
| `STANDARD` | 66 | `d0dfba6f79d7a5868f000c05da38f7803322d69ca1a120d6fd9f93c3408b74c9` |
| `VERTIEFUNG` | 102 | `780e61e82f82ca4f67b7a7d8b237dffa3dbc9b124640eedf7a0c77132a0837dd` |

Der Master und alle drei Varianten wurden mit PowerPoint Desktop gerendert.
102/102 Masterfolien, 41/41 `BASIS`-, 66/66 `STANDARD`- und 102/102
`VERTIEFUNG`-Renderbilder stimmen bytegenau mit den jeweiligen Masterfolien
überein. Die sieben vollständigen Kontaktbögen wurden geprüft; es gab keine
auffällige Abschneidung oder Überlagerung. Build-, Manifest- und
Ausgabevalidator bestehen.

Der Datenschutzscan nur der drei neuen Decks und ihres Buildprotokolls besteht
(vier Dateien, drei PowerPoint-Pakete). Ein Scan des gesamten lokalen
Buildverzeichnisses meldet zusätzlich alte, nicht zum Release gehörende Bilder
unter `build/.review` als manuell zu prüfende Medien. Diese historischen
Reviewbilder sind nicht Teil der drei ausgelieferten Profildecks und wurden
nicht entfernt. Die menschliche Generalprobe wurde nicht ausgeführt.

Die Artefakte liegen lokal unter `Presentations/variants/build/`; Render und
maschinenlesbare Nachweise liegen unter
`Runtime/PresentationRenders/presentation-variants/`. Sie bleiben gemäß
Buildvertrag abgeleitete, nicht versionierte Releaseartefakte. Dieser Build ist
kein GitHub-Release und erteilt keine zusätzliche SQL-Lab-, Produkt- oder
Runtimefreigabe.

## Nachfolgender Releasebuild vom 2026-11-17 auf `main` `ec5c5bc7bccd46aa5e630242ae8052a8edac511f`

Nach Integration von PR #1032 wurden die drei Profildecks erneut aus dem konsistenten `main` gebaut. Der Präsentationsmaster blieb unverändert; sein SHA-256 ist `17c55c8f4e6a2ff06cd1e7d81118bdc5e50021d395f157aa65ed38351054d787`.

| Profil | Folien | Releaseartefakt-SHA-256 |
|---|---:|---|
| `BASIS` | 41 | `d1fcce19a9bb6c9468291f0f9538b7ea134313e117d65854f6c568ca6b7d76e0` |
| `STANDARD` | 66 | `c8faefc8362f86062a0ab55b3608932c9b93b62cb658d8d621dc4f195260dcbd` |
| `VERTIEFUNG` | 102 | `bd23caacc0e2efb18cd558a91fe1a1911c1cb60da667add1d11bc0e473f63cf8` |

Der PowerPoint-Desktop-Build, Renderumfang, Manifest-/Ausgabevalidator und Mastererhalt bestehen. Alle 311 Profilrenderbilder sind anhand der Manifestreihenfolge bytegleich mit ihren Masterfolien. Der Datenschutzscan nur für die drei Decks und das Buildprotokoll besteht (vier Dateien, drei PowerPoint-Pakete). Die Artefakte liegen lokal unter `Presentations/variants/build/`; Render und Buildnachweise unter `Runtime/PresentationRenders/`. Sie sind abgeleitete lokale Releaseartefakte und kein GitHub-Release. Die menschliche Generalprobe wurde nicht ausgeführt; SQL-Lab- und Produktgates werden durch diesen Lehrmittelrelease nicht geschlossen.

## Nachfolgender Releasebuild vom 2026-11-17 auf `main` `564e904451e97a54601377a78f697975bbcafbbc`

Der Releasebuild wurde auf dem sauberen, mit `origin/main` synchronen Stand
`564e904451e97a54601377a78f697975bbcafbbc` erneut ausgeführt. Der Master blieb
mit SHA-256 `17c55c8f4e6a2ff06cd1e7d81118bdc5e50021d395f157aa65ed38351054d787`
unverändert.

| Profil | Folien | Releaseartefakt-SHA-256 |
|---|---:|---|
| `BASIS` | 41 | `edd3b5b57a4529de12e15354e0319c212b5b9eceb9d8bccb515a4bc86c5d035f` |
| `STANDARD` | 66 | `865d2588e66dfb0ed0ad49360950ee1fef83eb3723f5ae682ec3e01e3539019d` |
| `VERTIEFUNG` | 102 | `7a171bdb4595df26b3e7f2b18d13b3c75ad2555173beeeaee387ab9d018f56f5` |

PowerPoint Desktop baute und renderte die drei Varianten erneut. Der Profil-
und Ausgabevalidator bestanden; 102 Masterfolien sowie 41, 66 und 102
Profilfolien wurden gerendert. Über die SlideKey-Zuordnung stimmen alle 209
Variantenrenderings bytegenau mit den jeweiligen Masterrenderings überein.
Der gezielte Datenschutzscan der drei Decks und des Buildprotokolls besteht
(vier Dateien, drei PowerPoint-Pakete). Die Masterdatei blieb unverändert.

PowerPoint setzt beim Speichern neue Office-Zeitstempel; deshalb unterscheiden
sich die Paket-Hashes von früheren Builds desselben unveränderten Decks. Die
Folieninhalte und zugeordneten Renderings stimmen überein. Die Artefakte und
Renderbelege liegen lokal unter `Presentations/variants/build/` und
`Runtime/PresentationRenders/` und bleiben abgeleitete, nicht versionierte
Builddateien. Dieser Nachweis veröffentlicht kein GitHub-Release. Die
menschliche Generalprobe wurde nicht ausgeführt. Offene SQL-Lab-, Runtime- und
Produktgates bleiben unberührt.

## Nachfolgender Releasebuild auf `main` nach PR #1040

Der Build wurde am 17. November 2026 auf dem sauberen, mit `origin/main`
synchronen Commit `15834673e79a55c25f1b7dd100beffd7d1380e2d` ausgeführt. Der
Masterhash stimmte vor und nach dem Build mit dem Variantenmanifest überein:
`17c55c8f4e6a2ff06cd1e7d81118bdc5e50021d395f157aa65ed38351054d787`.

| Profil | Folien | Releaseartefakt-SHA-256 |
|---|---:|---|
| `BASIS` | 41 | `23ad998197347347d9c74630c8876b3b2e0d3950f1699f33f6b1ffa174378313` |
| `STANDARD` | 66 | `ce885b300519f62fd7085de7638852734b2bc1711f70889b8664af9a071a2dde` |
| `VERTIEFUNG` | 102 | `e12a820480fc9fb60d8cb6abcdfef2a9fcee17b7265f94a9f6fcec1dd2c3f9d3` |

PowerPoint Desktop baute die drei Varianten und renderte 102 Masterfolien sowie
41, 66 und 102 Profilfolien. Manifest-, Ausgabe- und gezielter
Datenschutzvalidator bestanden. Der Bytevergleich jedes Profilrenderings mit
der anhand der SlideKeys zugeordneten Masterfolie ergab 209 Übereinstimmungen
und keine Abweichung. Der Datenschutzscan umfasste gezielt die drei Decks und
das Buildprotokoll (vier Dateien, drei PowerPoint-Pakete); historische
Reviewbilder im lokalen Buildordner waren nicht Bestandteil dieses Scans.

Die `.pptx`-Dateien und Renderbilder bleiben abgeleitete lokale Releaseartefakte
und sind nicht versioniert. Dieser Kursrelease ist kein GitHub-Release. Die
menschliche Generalprobe wurde nicht ausgeführt; SQL-Lab-, Produkt- und
Runtimegates bleiben unberührt.
