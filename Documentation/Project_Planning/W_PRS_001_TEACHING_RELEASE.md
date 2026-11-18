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

## Releasebuild auf `main` nach PR #1042

Am 17. November 2026 wurde der Release auf dem sauberen, mit `origin/main`
synchronen Commit `d0d9857d9494ab4848758918451b5c9258eae1d7` gebaut. Der
Präsentationsmaster blieb unverändert; SHA-256:
`17c55c8f4e6a2ff06cd1e7d81118bdc5e50021d395f157aa65ed38351054d787`.

| Profil | Folien | Releaseartefakt-SHA-256 |
|---|---:|---|
| `BASIS` | 41 | `afbb531eca283d29db427f9631b84aa0bece8b97c46118bc65f1bc8258adbaac` |
| `STANDARD` | 66 | `0e87d235d48f4e3acf3655004273ec35503387aacb2784e82d1e6b18751a26d6` |
| `VERTIEFUNG` | 102 | `84a8a52d5ce58a61e1a52c3221b28a7ef1769104691c13427708c24161415688` |

PowerPoint Desktop baute die drei Varianten und renderte 102 Masterfolien
sowie 41, 66 und 102 Profilfolien. Manifest-, Ausgabe- und gezielte
Datenschutzprüfungen bestanden. Der SlideKey-/Manifest-gebundene Bytevergleich
ergab 209 übereinstimmende Renderings und keine Abweichung. Der Datenschutzscan
umfasste ausschließlich die drei Decks und das Buildprotokoll (vier Dateien,
drei PowerPoint-Pakete).

Die Artefakte und Renderbelege liegen lokal unter
`Presentations/variants/build/` und `Runtime/PresentationRenders/`; sie sind
abgeleitet und nicht versioniert. Dieser Kursrelease ist kein GitHub-Release.
Die menschliche Generalprobe wurde nicht ausgeführt. SQL-Lab-, Produkt- und
Runtimegates bleiben unberührt.

## Releasebuild auf `main` `a1b5d312` nach PR #1077

Am 18. November 2026 wurde der Release auf dem sauberen, mit `origin/main`
synchronen Commit `a1b5d312b8057b32e51dd89466ffcbd6a75deb16` gebaut. Der
Master blieb unverändert; sein SHA-256 ist
`17c55c8f4e6a2ff06cd1e7d81118bdc5e50021d395f157aa65ed38351054d787`.

| Profil | Folien | Releaseartefakt-SHA-256 |
|---|---:|---|
| `BASIS` | 41 | `3dd6095a97ade5851b1dff2c2533a51da84b86dbf34f3a7b5ec778afb70fda14` |
| `STANDARD` | 66 | `41ae63d5ce98cd0309a06b3cc4889d86a111f1f3ec72288d3c52a5aeb1016128` |
| `VERTIEFUNG` | 102 | `aff2d3828d42701536924584fab0b042d6f44fd75d957828ee25f73b7c9efead` |

PowerPoint Desktop baute alle drei Profile und renderte 102 Masterfolien sowie
41, 66 und 102 Profilfolien. Manifest- und Ausgabevertrag bestanden; der
SlideKey-gebundene Vergleich ergab 209 bytegleiche Profil-/Masterrenderings.
Der Datenschutzscan für die drei Decks und das Buildprotokoll bestand
(vier Dateien, drei PowerPoint-Pakete). Der Masterhash vor und nach dem Build
war identisch.

Die Artefakte und Renderbelege liegen lokal unter
`Presentations/variants/build/` und
`Runtime/PresentationRenders/presentation-variants/`; sie sind abgeleitet und
nicht versioniert. Dieser Kursrelease ist kein GitHub-Release. Die menschliche
Generalprobe wurde nicht ausgeführt. SQL-Lab-, Produkt- und Runtimegates
bleiben unberührt.


## Releasebuild auf `main` `b4239247` nach PR #1079

Am 18. November 2026 wurde der Kursrelease auf dem sauberen, mit
`origin/main` synchronen Stand `b42392478ab5113df858ff7cffe0e656eaa113ad`
gebaut. Der Master blieb unverändert; sein SHA-256 ist
`17c55c8f4e6a2ff06cd1e7d81118bdc5e50021d395f157aa65ed38351054d787`.

| Profil | Folien | Releaseartefakt-SHA-256 |
|---|---:|---|
| `BASIS` | 41 | `f4027015d71753d660043af7fc80a35b9ac3f056b96cd7f6e9fd9e0073880917` |
| `STANDARD` | 66 | `ac1863edc5915bd19122b25df74de18947ea1a2472781a4e03cfce6935c1f60b` |
| `VERTIEFUNG` | 102 | `c4a62d3908c3b2496403fb08ec4f1789e2a0d798044e05829032e417a1a0ce10` |

PowerPoint Desktop baute alle Profile und renderte 102 Masterfolien sowie
41/66/102 Profilfolien. Manifest- und Ausgabevalidatoren bestanden; der
SlideKey-gebundene Rendervergleich ergab 209 bytegleiche Profil-/Masterbilder.
Der gezielte Datenschutzscan über die drei Decks und das Buildprotokoll
bestand (vier Dateien, drei PowerPoint-Pakete). Ein erster Scan direkt auf dem
Buildordner erfasste zusätzlich bereits vorhandene `.review`-Renderbilder;
die isolierte Releaseprüfung grenzt sich auf die vorgesehenen vier Dateien ein.

Die Artefakte und Renderbelege liegen lokal unter
`Presentations/variants/build/` und
`Runtime/PresentationRenders/presentation-variants/`; sie sind abgeleitet und
nicht versioniert. Dieser Kursrelease ist kein GitHub-Release. Die menschliche
Generalprobe wurde nicht ausgeführt. SQL-Lab-, Produkt- und Runtimegates
bleiben offen. Die Verarbeitungswelle wurde nach diesem Release auf
Nutzerwunsch angehalten.

## Releasebuild auf `main` `89ccc0a1` nach PR #1084

Am 18. November 2026 wurde der Kursrelease auf dem sauberen, mit
`origin/main` synchronen Commit `89ccc0a109be6d059dc3b3f77fcdf7335196ae56`
gebaut. Der Präsentationsmaster blieb unverändert; sein SHA-256 ist
`17c55c8f4e6a2ff06cd1e7d81118bdc5e50021d395f157aa65ed38351054d787`.

| Profil | Folien | Releaseartefakt-SHA-256 |
|---|---:|---|
| `BASIS` | 41 | `f9ce317746162685c8821c6e87b648ebf8f88e184f97b5d59bc3bb0bff7ac76e` |
| `STANDARD` | 66 | `5cb66d455925759cc7538a0e6b79c49d26e90ae098b10b2d1dc2e778db2e70bd` |
| `VERTIEFUNG` | 102 | `20916c37a38d9988273f8e4ec07987bcc57e4c21690c45fbe839d07a9e97b955` |

PowerPoint Desktop baute die drei Profile und renderte alle 102 Masterfolien
sowie 41, 66 und 102 Profilfolien. Manifest- und Ausgabevalidatoren bestanden;
der Masterhash vor und nach dem Build war identisch. Der SlideKey-gebundene
Bytevergleich ergab 209 übereinstimmende Profil-/Masterrenderings. Der gezielte
Datenschutzscan über die drei Decks und das Buildprotokoll bestand (vier
Dateien, drei PowerPoint-Pakete).

Die Decks liegen lokal unter `Presentations/variants/build/`; Render und
Nachweise unter `Runtime/PresentationRenders/`. Sie sind abgeleitete,
nicht versionierte Buildartefakte. Dieser Kursrelease ist kein GitHub-Release.
Die menschliche Generalprobe wurde nicht ausgeführt; SQL-Lab-, Produkt- und
Runtimegates bleiben offen. Die Verarbeitungswelle wurde nach diesem Release
auf Nutzerwunsch angehalten.
