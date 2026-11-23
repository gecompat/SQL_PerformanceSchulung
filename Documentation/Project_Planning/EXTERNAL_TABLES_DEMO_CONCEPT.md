# External Tables: Lehr- und Demoentwurf

Stand: 23. November 2026
Status: `PROPOSED`. Isolierte Komponentenprüfungen sind dokumentiert.
Die Entscheidung über den vollständigen PolyBase-Pilot steht aus.

## Lernfrage und Curriculumanschluss

Der mögliche Lehrschnitt konkretisiert den bereits vorhandenen Anker
`LO-M03-05`/`CLM-045`: Remote Pushdown ist provider-, Ausdrucks- und planabhängig
und muss im konkreten Fall belegt werden. `QRY-012` behandelt bereits Linked
Server. External Tables wären eine zweite Zugriffsform zur selben fachlichen
Frage, keine Behauptung, dass PolyBase generell schneller oder einfacher ist.
DEC-078 führt External Tables im aktuellen Curriculum als erklärende
Ergänzung. Ein ausführbarer Pfad braucht ein separates Arbeitspaket mit
eigenem Vertrag und eigener Freigabe.

Die Lernenden sollen eine externe Tabellenabfrage als Datenweg erklären,
Ergebnisgleichheit gegenüber einer lokalen Kopie prüfen und tatsächliches
Pushdown von einer bloßen Planannahme unterscheiden. Ein Laufzeitvergleich ist
für das Lernziel nicht zwingend; quantitative Aussagen benötigen jedoch
qualifizierte Messungen und dürfen nur für das festgelegte Profil gelten.

## Vorgeschlagener Zugriffsweg und Fixture

Der versionsübergreifende Entwurf verwendet persistente External Tables mit
dem `sqlserver://`-Connector und einer separaten, ausschließlich synthetischen
SQL-Server-Quellinstanz. Für eine gemeinsame SQL-Server-2019/2022/2025-Matrix
ist ein gemeinsames Windows-Profil vorgesehen. Ein Linux-Profil müsste
SQL Server 2025 separat behandeln; die dokumentierte PolyBase-Installation
für 2022 unter Linux allein belegt keinen RDBMS-Connector für diese Version.

Die Quelle enthält ein deterministisches Fakt-Fixture mit stabiler
Run-Kennung, Schlüssel, Datum, Kategorie und numerischem Wert. Pro Lauf wird
ein unveränderlicher Snapshot erzeugt. Eine lokale Tabelle erhält denselben
Snapshot mit denselben Spalten, Typen, Collations und fachlichen Constraints.
Der erste Kandidat legt die Datenmenge und die erwarteten Ergebnisse im
[isolierten Pilotprofil](#isoliertes-pilotprofil-für-sql-server-2025) fest.

Eine festgelegte Abfrage filtert ein Datumintervall, projiziert nur benötigte
Spalten und aggregiert nach Kategorie. Der Ergebnisvertrag bindet Schlüssel,
Zeilentupel, Multiplizität und Summen an ein deterministisches Oracle. Quelle,
lokale Kopie und erwartete Tupelmenge werden vor Messläufen vollständig
verglichen; ein Hash allein ersetzt weder Multiplizitäts- noch Ergebnisprüfung.

Die lokale Kopie ist ein Vergleich der Datenwege, kein kausal isolierter
External-Table-Kontrolllauf. Remoteausführung, Transport, Data Movement Service
(DMS; PolyBase-Datenbewegungsdienst), lokale Verarbeitung und lokale
Seiten-I/O unterscheiden sich systematisch. Ergebnisse werden deshalb als
beobachtetes Profil mit getrennten Kostenkomponenten berichtet, nicht als
allgemeine Rangfolge.

## Isoliertes Pilotprofil für SQL Server 2025

Der erste Kandidat nutzt zwei eigene Ubuntu-24.04-VMs (AMD64) mit SQL Server
2025 CU11 (`17.0.5065.9`), Enterprise Developer Edition und
Datenbankkompatibilitätsstufe 170. Eine VM ist der PolyBase-Abfrageknoten, die
zweite die synthetische SQL-Quelle. Die gemeinsame Windows-Matrix für
2019/2022/2025 bleibt ein eigenes Profil. Microsoft dokumentiert den
SQL-Server-Connector mit SQL-Authentifizierung und PolyBase auf Linux.
Das Profil übernimmt die dokumentierte Ubuntu-Installation und benötigt eine
vorbereitete Wegwerfvorlage für beide Rollen.

| Bereich | Vertrag für den Pilotkandidaten |
|---|---|
| Pakete | Der Microsoft-Paketindex für Ubuntu 24.04/AMD64 führt `mssql-server` und `mssql-server-polybase` jeweils als `17.0.5065.9-3`. SHA-256 laut Index: Engine `1174d93bf5384b45ef528353cc8f6829aa0ab12669700e96bfd4e2959a0de3ff`, PolyBase `302acda716e373d785dc8f1c394d762deb498010cbf96f10af679bba08b2c32a`. Engine auf beiden VMs, PolyBase samt erforderlichen Komponenten nur auf dem Abfrageknoten. Vor Einrichtung den signierten Paketindex und alle tatsächlich eingesetzten Pakete, Abhängigkeiten und Komponenten an die Vorlage binden. Vor SQL die installierten Paketstände und den Dienstzustand prüfen. |
| Netz und Transport | Ein privater virtueller Switch verbindet ausschließlich diese zwei VMs. Die VMs verwenden je eine private Schnittstelle ohne Standardroute. Eine Firewall an der Quelle erlaubt eingehendes TCP 1433 nur vom Abfrageknoten. Administration erfolgt über die VM-Konsole. Der Connector verwendet einen laufgebundenen Hostnamen von höchstens 15 Zeichen. Ein kurzlebiges Zertifikat enthält diesen Namen und wird über die nur in der Abfrage-VM hinterlegte Labor-CA geprüft. Beide Datenquellen verwenden ODBC Driver 18 und `Encrypt=Yes;TrustServerCertificate=No`. Der Preflight prüft einen erfolgreichen verschlüsselten Zugriff und die Ablehnung des Zugriffs bei abweichender Serveridentität. |
| Rollen | Die Einrichtung verbindet sich lokal mit jeder VM und erzeugt eigene markierte Testdatenbanken. Der laufgebundene Quelllogin erhält Datenbankzugriff und `SELECT` auf genau die synthetische Quelltabelle; er erhält keine zusätzlichen Serverrollen und keine DDL- oder Schreibrechte auf die Quelldatenbank. Der Abfrageprincipal erhält `SELECT` auf die beiden externen Tabellen und die lokale Referenz. Ein getrenntes Diagnoseprofil erhebt Pläne und Requestmetadaten. Rechteinventar und Gegenproben für Schreiben und Zugriff auf ein zweites eigenes Objekt laufen vor der Mechanismusprüfung. |
| Zugangsdaten | Quelllogin, Datenbank-Hauptschlüssel und Credential verwenden getrennte, zufällige Laufgeheimnisse. Die Einrichtung überträgt sie im Arbeitsspeicher zum jeweiligen SQL-Client und hält sie aus Prozessargumenten, Umgebungsinventaren, Protokollen und Artefakten heraus. Setup-Capture bleibt deaktiviert. Im Evidenzfenster sind nur normalisierte Befunde zu eigenen synthetischen Abfragen zulässig. |
| Ressourcen | Je VM 2 vCPUs, 4 GiB RAM und höchstens 24 GiB für die eigene virtuelle Platte. Je Testdatenbank höchstens 128 MiB Daten und 128 MiB Log. Ein Versuch aus vorbereiteten Vorlagen mit höchstens 600 Sekunden für VM-Start, Preflight, Setup und Abfragen, plus 120 Sekunden für Abbau. Bei Budgetüberschreitung endet die Erhebung und der Abbau beginnt. Vorlagenbereitstellung und Paketprüfung gehen dem Lauf voraus. |

Microsoft dokumentiert seit SQL Server 2025 CU4 einen Offlineweg für die
benötigten .NET-Komponenten. Die Vorlagenphase muss deshalb die Herkunft und
Prüfsumme des unterstützten .NET-Bundles sowie die installierte
Connectorversion erfassen. Der spätere Pilot läuft auf dem privaten Switch mit
den vorbereiteten Vorlagen. Eine vorhandene Hyper-V-Installation belegt
allein weder die Vorlagen noch Kapazität oder den Dienstzustand. Die
Voraussetzungen gelten für die eigenen VMs und den eigenen Lauf.

### Ressourcen auf dem Hyper-V-Host bestätigen

Vor dem ersten SQL-Aufruf liest der
[Hyper-V-Ressourcenprüfer](../../Tests/Runtime/Test-ExternalTablesHyperVResources.ps1)
die beiden VM-IDs und VHDX-Pfade aus der Erzeugungsliste. Beide VMs müssen
laufen und je zwei vCPUs sowie genau 4 GiB fest zugewiesenen Speicher
haben. Pro VM ist genau die aufgezeichnete eigenständige VHDX mit einer
virtuellen Kapazität von höchstens 24 GiB zulässig. Eine andere
Plattenkopie, eine zusätzliche Platte oder eine Differenzplatte führt zum
Abbruch des Preflights. Der Prüfer liest das lokale Inventar und meldet
das bestätigte Profil ohne Hostpfade oder IDs.
[Microsoft-Referenz zu Get-VHD](https://learn.microsoft.com/powershell/module/hyper-v/get-vhd?view=windowsserver2025-ps).

### Geprüfte Ubuntu-Basis für beide VM-Rollen

Als Basiskandidat dient das Canonical-Cloud-Image für Ubuntu Server 24.04,
AMD64, Release `20261017`, im VHD-Format. Der Stand vom 23. November 2026
prüfte Canonicals `SHA256SUMS.gpg` gegen den dokumentierten Fingerabdruck
`D2EB44626FDDC30B513D5BB71A5D6C4C7DB87C81`. Das Paketmanifest und das
843.188.381 Byte große VHD-Archiv bestanden den Abgleich mit der signierten
SHA-256-Liste. Das Archiv wurde bei der Prüfung weder gestartet noch
als VM importiert.
[Datierter Canonical-Release](https://cloud-images.ubuntu.com/releases/noble/release-20261017/)
und [Canonical-Anleitung zur Prüfsummenprüfung](https://ubuntu.com/docs/public-images/public-images-how-to/verify-image-checksum/).

Der [Basisprüfer](../../Tests/Static/verify_external_tables_ubuntu_base.py)
bindet Manifest und optionales Archiv an diese Prüfsummen. Er vergleicht die
Namen aus dem `Depends`-Feld des verifizierten Microsoft-Enginepakets mit
der nativen Paketliste. Von 21 direkten Abhängigkeiten enthält das Manifest
16. Die folgenden fünf Namen fehlen:

- `gdb`
- `libatomic1`
- `libc++1`
- `libsasl2-modules-gssapi-mit`
- `libsss-nss-idmap0`

Lade für eine Wiederholung
`ubuntu-24.04-server-cloudimg-amd64-azure.vhd.manifest` und optional das
gleichnamige `.tar.gz`-Archiv aus dem datierten Release. Prüfe die erhaltenen
Dateien mit:

```text
python Tests/Static/verify_external_tables_ubuntu_base.py MANIFEST --archive VHD-ARCHIV
```

### Aufgelöste Pakete für beide VM-Rollen

Der Paketstatus wurde am 23. November 2026 direkt aus dem Root-Dateisystem
der geprüften VHD gelesen. Alle 659 installierten Paketnamen und Versionen
stimmten mit Canonicals Manifest überein. APT 2.8.4 verwendete diesen
Paketstatus und die signierten Komponenten `main` und `universe` aus
`noble`, `noble-updates` und `noble-security`.
[Datierter Ubuntu-Snapshot](https://snapshot.ubuntu.com/ubuntu/20261123T000000Z/).

Das Abfrageprofil umfasst 21 zusätzliche APT-Pakete. Zu den zwölf
Ubuntu-Paketen sowie SQL Server und PolyBase kommen sechs
Ubuntu-Bibliotheks- und unixODBC-Pakete sowie `msodbcsql18` in der Version
`18.7.1.1-1`. Der Treiber stammt aus dem signierten Microsoft-`prod`-Index
für Ubuntu 24.04. `libgssapi-krb5-2` war im geprüften Grundabbild vorhanden.
Der Lösungslauf ergab weder Upgrades noch Entfernungen. Die sieben neuen
Paketdateien wurden heruntergeladen und mit den Größen und SHA-256-Werten
der signierten Indizes abgeglichen. Die
[APT-Paketliste](external_tables_apt_lock.json) bindet für die Abfrage-VM
zusätzlich das Linux-x86-64-Wheel für CPython 3.12 und `pyodbc 5.5.0`.
[Microsoft-Anleitung für ODBC Driver 18](https://learn.microsoft.com/en-us/sql/connect/odbc/linux-mac/installing-the-microsoft-odbc-driver-for-sql-server?view=sql-server-ver17#ubuntu).

Der [APT-Prüfer](../../Tests/Static/verify_external_tables_apt_plan.py)
erwartet die Ausgabe eines erfolgreich beendeten `apt-get -s`-Laufs.
`--payload-directory` prüft zusätzlich jede gebundene `.deb`-Datei
im angegebenen Ordner. `--python-wheel` prüft getrennt Dateiname, Größe
und Hash des Wheels.

```text
python Tests/Static/verify_external_tables_apt_plan.py APT-PLAN --role query --payload-directory PAKETVERZEICHNIS --python-wheel WHEEL-DATEI
```

Für die Quell-VM ergab der Lauf vom selben Paketstatus unverändert 13
Installationsschritte, zwölf Ubuntu-Pakete und `mssql-server`. Verwende
`--role source` für diesen Plan. Die beiden Simulationen lösen Versionen
und Abhängigkeiten auf. Installation, Dienstzustand und Connectorlauf
werden in den bereitgestellten Gästen geprüft.


### Pakete im netzgetrennten Gast installieren

Der [Installationsbaustein](../../Tests/Runtime/external_tables_guest_apt.py)
prüft den Paketstatus gegen das gepinnte Basisabbild und alle Paketdateien
der gewählten Rolle gegen die Größen und SHA-256-Werte im Lock. Die
Dateien liegen auf einem schreibgeschützten Medium. Der frisch gestartete
Gast hat während der Installation nur Loopback. Der Host hält seine
Netzadapter bis zum bestätigten Paketbestand getrennt.
Das ist erforderlich, weil die Paket-Skripte von SQL Server und PolyBase
bereits Dienste starten können.

APT verwendet absolute Pfade zu den geprüften Paketdateien und einen
leeren Satz an Paketquellen, Paketlisten und zwischengespeicherten
Archiven. Vor dem Installieren muss die Simulation genau die gesperrten
Versionsübergänge liefern. Ein geänderter Paketstatus oder ein
zusätzlicher Netzadapter verhindert die Installation. Danach muss der
tatsächliche Debian-Bestand vollständig zum Rollen-Lock passen.
Ein Teilfehler wird im selben Gast nicht durch einen neuen Versuch
überdeckt, weil inzwischen ein anderer Basiszustand vorliegen kann.
[Ubuntu-Manpage zu apt-get](https://manpages.ubuntu.com/manpages/noble/man8/apt-get.8.html).

Die Simulation auf Ubuntu 24.04 mit der Paketstatusdatei des
gebundenen Basisabbilds ergab aus den lokalen Dateien 13 Übergänge
für den Quellgast und 21 für den Abfragegast. Ein einzelnes gepinntes
`unixodbc-common`-Paket wurde über denselben Baustein in einem
netzgetrennten Linux-Wegwerfcontainer installiert und im resultierenden
Paketstatus bestätigt. Die vollständige Paketinstallation bleibt im
zugelassenen Hyper-V-Gastlauf zu prüfen.

### Installierten Paketstand vor dem SQL-Start prüfen

Erfasse `/var/lib/dpkg/status` im vorbereiteten Gast nach bestätigter
Gastidentität und abgeschlossener Paketinstallation. Übertrage die
Datei bytegetreu. Verwende als Referenz die rohe Statusdatei aus dem
festgeschriebenen Ubuntu-Abbild. Der Prüfer vergleicht zuerst deren
SHA-256 mit der Paketliste. Anschließend berechnet er aus dem
Grundbestand und den Paketübergängen den vollständigen Sollbestand
für die gewählte Rolle. Paketname, Architektur und Version müssen
unter den vollständig installierten Paketen exakt übereinstimmen.
Fehlende, zusätzliche, geänderte oder unvollständig installierte
Pakete verhindern den Nachweis.

```text
python Tests/Static/verify_external_tables_apt_plan.py --role query --base-status BASIS-STATUS --guest-status GAST-STATUS
```

Für den Quellgast verwende `--role source`. Statusdateien bleiben
außerhalb des Repositories. Die Prüfung gibt den Paketbestand nur
als Anzahl aus. Vor dem Pilot werden das CPython-Wheel, der aktive
Treiber, die Gastidentität, die Dienste und die Netzgrenzen separat
geprüft.

Im Komponententest stimmten alle 21 APT-Paketdateien und das Wheel mit
der Paketliste überein. Aus der rohen Statusdatei des geprüften Basisabbilds
und den Metadaten der Paketdateien wurden synthetische Gastbestände
gebildet. Der Prüfer bestätigte 672 installierte Pakete für die Quellrolle
und 680 für die Abfragerolle. Mit dem Abfragebestand meldete der Prüfer
für die Quellrolle acht zusätzliche Pakete. Die Erfassung des
tatsächlichen Status aus den gestarteten Gästen steht aus.


### Abgeleitetes Hyper-V-Abbild mit 24 GiB

Die Canonical-VHD hat unverändert 32.213.303.296 Byte virtuelle Größe.
Für die Profilgrenze von 24 GiB wurde aus dem geprüften Archiv eine eigene
Offlinekopie abgeleitet. Vor dem Kürzen lagen alle vier Partitionen
vollständig unterhalb der neuen Grenze und der abgeschnittene Bereich war
leer. Anschließend wurde das GPT-Ende an die neue Kapazität angepasst und
die Kopie als dynamische VHDX ausgegeben. Nach erneutem Lesen der VHDX
stimmten Kennungen, Startsektoren, Längen und SHA-256 der Nutzdaten aller
vier Partitionen mit dem Original überein. Hyper-V meldete 24 GiB und
`Test-VHD` lieferte `True`.
[Nachweis des konkreten Abbilds](external_tables_vhdx_evidence.json).

Der [Basisprüfer](../../Tests/Static/verify_external_tables_ubuntu_base.py)
kann die lokal vorgehaltene Kopie vor ihrer weiteren Verwendung erneut
an Dateigröße und SHA-256 binden:

```text
python Tests/Static/verify_external_tables_ubuntu_base.py MANIFEST --derived-vhdx VHDX
```

Der isolierte Gaststart in Hyper-V bleibt offen. Die Ausführungsumgebung
lehnte den kombinierten Befehl zum Anlegen, Starten und Entfernen der
temporären Test-VM vor Prozessbeginn ab. Eine anschließende read-only
Inventur fand keine Test-VM. Weiter geht es mit einem zugelassenen
isolierten Gaststart. Die hier belegte Dateiintegrität bleibt gültig.

### Geprüfte Microsoft-Pakete für die Vorlagen

Die [Paketprüfung](../../Tests/Static/verify_external_tables_packages.py)
prüft `InRelease` in einem temporären GnuPG-Schlüsselbund gegen den
dokumentierten Microsoft-Fingerabdruck. Sie bindet den AMD64-Index über
SHA-256 und Dateigröße an die signierte Freigabe und prüft beide Paketzeilen
gegen die festen Werte des Pilotprofils.
[Microsofts Repository-Signaturschlüssel](https://learn.microsoft.com/en-us/linux/packages#how-to-use-the-gpg-repository-signing-key).

Lege `microsoft.asc`, `InRelease` und `Packages` in ein lokales
Indexverzeichnis. Für die Bytes der beiden `.deb`-Dateien und des
SDK-Archivs ergänze ein separates Paketverzeichnis und rufe auf:

```text
python Tests/Static/verify_external_tables_packages.py INDEXVERZEICHNIS --payload-directory PAKETVERZEICHNIS
```

`microsoft.asc` stammt aus [Microsofts Schlüsselverzeichnis](https://packages.microsoft.com/keys/microsoft.asc).
`InRelease` und `main/binary-amd64/Packages` stammen aus dem
[Ubuntu-Noble-Repository für SQL Server 2025](https://packages.microsoft.com/ubuntu/24.04/mssql-server-2025/dists/noble/).
Der Index nennt die relativen Downloadpfade für
`mssql-server_17.0.5065.9-3_amd64.deb` und
`mssql-server-polybase_17.0.5065.9-3_amd64.deb`. Das benötigte
`dotnet-sdk-8.0.418-linux-x64.tar.gz` enthält laut
[Microsofts .NET-Freigabemetadaten](https://builds.dotnet.microsoft.com/dotnet/release-metadata/8.0/releases.json)
die Runtime 8.0.24. Die Prüfung vergleicht seinen SHA-512 mit dem
festgelegten Eintrag für das Linux-AMD64-SDK.

Am 23. November 2026 bestanden die Signatur, der Index und die
Prüfsummen der drei tatsächlich heruntergeladenen Dateien. Für die
Vorlagen fehlen noch die Bindung der Betriebssystemabhängigkeiten und
des ODBC-Treibers, die Installation und die Prüfung des Dienstzustands.
Der Abfrage- und Cleanup-Pilot bleibt offen.

### Tatsächlich geladenen ODBC-Treiber binden

Der eingebaute Connector `sqlserver://` verwendet laut Microsoft den mit
dem Produkt installierten ODBC Driver 18 als Standard. Den Linux-Treiber
bindet das Profil deshalb über die vom Dienst geladene Datei.
[Microsofts Beschreibung zur Treiberauswahl](https://learn.microsoft.com/en-us/sql/relational-databases/polybase/polybase-change-odbc-driver?view=sql-server-ver17).

Die geprüfte Ubuntu-Paketdatei `mssql-server-polybase_17.0.5065.9-3_amd64.deb`
enthält die Unit `mssql-ees.service`, Hilfsdateien für den Dienst und
`/opt/mssql/lib/sqlservr.polybase.sfp`. Die sichtbare Paketdateiliste liefert
keinen separat installierbaren Driver-18-Pfad. Das Dienstsetup und die
tatsächliche Ladung auf Ubuntu bleiben Prüfgegenstand.

Der [Gastprüfer](../../Tests/Static/inspect_external_tables_driver.py) ist
für die eigene Abfrage-VM vorgesehen. Er überprüft Paketversionen,
Dienstzustand, Prozesszugehörigkeit, Gerätekennung und Inode der im
Prozess eingeblendeten Driver-18-Bibliothek. Ein Wechsel des Prozesses,
ein mehrdeutiges Mapping und eine als gelöscht markierte Datei liefern
`NOT_PROVEN`. Der Bericht enthält Dienst, Version, Dateiname und SHA-256.

1. Ermittle während des späteren freigegebenen Connector-Aufrufs auf der
   Abfrage-VM den zugehörigen Prozess in `mssql-ees.service` bzw.
   `mssql-server.service`. Die Zuordnung zum Connector-Aufruf wird im
   Laufprotokoll belegt.
2. Starte auf derselben VM den Prüfer mit dem ausgewählten Dienst und der PID.
   Die erste Erhebung liefert `OBSERVED`. Der Methodenreview bindet den
   erfassten Digest an die geprüfte Vorlage.
3. Bei folgenden Läufen prüft `--expected-sha256` den geladenen Treiber
   gegen den gebundenen Digest. Ein Treffer liefert `MATCHED`.

```text
python Tests/Static/inspect_external_tables_driver.py --service mssql-ees.service --pid PID
```

Die Nachweislogik ist offline geprüft. Die tatsächlich geladene Datei,
der ausführende Dienstprozess und die Betriebssystemabhängigkeiten
sind erst im vorbereiteten Gast belegbar.

### Daten und Ergebniskontrolle

Die deterministische Quelltabelle `dbo.Facts` und die lokale Referenz
enthalten je 4.096 Zeilen mit den Spalten `FactId int`, `EventDate date`,
`CategoryId int` und `Amount int`. Verwende für jede Kombination
`d = 0..63`, `c = 0..3`, `r = 0..15` die Werte
`FactId = 64*d + 16*c + r`, Datum `2026-01-01 + d Tage`,
`CategoryId = c` und `Amount = 100*d + 10*c + r`. Prüfe den vollständigen
Tupelbestand mit Schlüsseln und Multiplizitäten vor dem Erhebungsfenster.

| Kategorie | Zeilen im Filterfenster | Erwartete Summe |
|---:|---:|---:|
| 0 | 128 | 250.560 |
| 1 | 128 | 251.840 |
| 2 | 128 | 253.120 |
| 3 | 128 | 254.400 |

Lege zwei externe Tabellen über derselben Quelle mit identischer Spaltenliste
und zwei Datenquellen mit derselben Verbindung und demselben Credential an.
Die Datenquellen unterscheiden sich durch `PUSHDOWN = ON` bzw.
`PUSHDOWN = OFF`. Verwende für beide und für die lokale Referenz dasselbe
halboffene Datumsintervall `[2026-01-17, 2026-01-25)` und dieselbe Gruppierung
nach `CategoryId` mit Anzahl und Summe. Baue die benötigten Statistiken pro
Tabelle vor der Messung symmetrisch auf und kontrolliere Änderungen im
Messfenster. Nach Setup- und Rechteproben öffnet der Reader pro Arm eine
eigene Session. Die Abfragen laufen einzeln und erhalten je ein abgegrenztes
Erhebungsfenster.

Der Datenweg ist nachgewiesen, wenn alle drei Ergebnisse dem Oracle entsprechen
und beide externen Ausführungen der eigenen Quelle zugeordnet sind. Weise
Pushdown getrennt für das Datumsprädikat aus. Die Remote-Anweisung für ON muss
das äquivalente Datumsintervall enthalten; die gebundene OFF-Gegenprobe muss
eine Remote-Anweisung ohne dieses Prädikat zeigen. Die [Nachweisbausteine](../../Tests/Runtime/external_tables_pushdown_evidence.py)
binden den aktiven Request über Datenbank, Session, Request-ID und den
laufspezifischen Statementmarker. Danach suchen sie den beobachteten
`sql_handle` in den verteilten Requests und deren `execution_id` in den
Workrecords. Pro Arm ist eine neue Reader-Verbindung und genau ein Aufruf
mit diesem Marker vorgesehen. Wiederholungen erfordern einen frischen Token.
Der Diagnoseprincipal braucht Zugriff auf die dokumentierten Systemansichten.
Die konkrete Handle-Gleichheit und die Erfassbarkeit für die kurze Abfrage
müssen auf dem festgelegten SQL-Build beobachtet werden.
[Microsoft-Referenz zu verteilten Requests](https://learn.microsoft.com/en-us/sql/relational-databases/system-dynamic-management-objects/sys-dm-exec-distributed-requests-transact-sql?view=sql-server-ver17)
und [Referenz zum Pushdown-Nachweis](https://learn.microsoft.com/en-us/sql/relational-databases/polybase/polybase-how-to-tell-pushdown-computation?view=sql-server-ver17). Bei fehlendem oder
mehrdeutigem Workrecord, nicht auflösbaren Parametern oder abgeschnittenem
Remote-Befehl bleibt der Pushdown-Befund `NOT_PROVEN`. Der Offlineprüfer
wertet ausschließlich einen abgeschlossenen Workrecord je Arm und einfache
Remote-`SELECT`-Befehle auf der vorgesehenen Tabelle aus. Der ON-Arm braucht
beide erwarteten Datumsgrenzen, der OFF-Arm einen vollständigen Befehl ohne
Prädikat. Andere Befehlsformen brauchen eine überprüfte Erweiterung. Im
Laufprotokoll werden nur die normierten Befunde gespeichert. Die lokale Referenz
belegt das Ergebnis. Eine Remoteaggregation oder Leistungswirkung erfordert
einen eigenen Befund.

### SQL-Bausteine für den isolierten Pilot

Die [SQL-Bausteine](../../Tests/Runtime/external_tables_pilot_sql.py) erzeugen
die Fixture für beide Rollen, die zwei externen Tabellen samt Datenquellen,
symmetrische Statistiken und die drei Abfragen. Sie verwenden den
festgelegten Build und getrennte Datenbanknamen. Vor Änderungen prüfen
sie vier Datenbankmarker für Projekt, Vertragsversion, Lauf und Rolle.
Der spätere Runner bindet einen achtstelligen ASCII-Lauftoken, den privaten
Quellhost `pbs-<token>` und den dazu passenden SQL-Reader. Die
Connector-Batches erwarten ein bereits eingerichtetes, laufgebundenes
Credential.

Prüfe zunächst die vollständigen Tupel der Quelle, der lokalen Referenz
und beider externer Tabellen gegen die synthetische Fixture. Baue die
Statistiken vor dem Erhebungsfenster auf. Verwende danach die drei
bereitgestellten Aggregatabfragen und vergleiche ihre vollständigen
Ergebnisse mit dem Vier-Kategorien-Oracle. Der SQL-Baustein enthält den
Offline-Prüfer für Tupel und Aggregatwerte.
[Regressionen](../../Tests/Static/test_external_tables_pilot_sql.py)
prüfen Fixture, Oracle, Routen und die Bindung vor Änderungen.
Der tatsächliche Remote-Befehl, die Gastrechte und der Cleanup müssen
im späteren Pilot beobachtet werden.

### Logins und Rechteprüfung

Die [SQL-Bausteine für Logins und Rechte](../../Tests/Runtime/external_tables_principals.py)
binden die Namen an den Laufmarker und die jeweilige Testdatenbank. Das
Setup prüft deren Eigentumsmarker, erstellt die Anmeldung in `master`
und ordnet ihr in der Testdatenbank einen Benutzer zu. Der Quellreader
erhält `SELECT` auf die Quelltabelle. Der Messreader erhält `SELECT` auf
die lokale Referenz und die zwei zuvor geprüften externen Tabellen. Nur
das Diagnosekonto erhält `VIEW SERVER PERFORMANCE STATE`. Seine
Reichweite setzt die eigene isolierte Abfrageinstanz voraus. Der
Abfrageknoten legt das quellgebundene Credential und den Datenbank-
Hauptschlüssel mit unterschiedlichen Laufgeheimnissen an. Beide
Setup-Batches bleiben außerhalb der Abfrageprotokollierung.
[Microsoft-Referenz für Serverrechte](https://learn.microsoft.com/en-us/sql/t-sql/statements/grant-server-permissions-transact-sql?view=sql-server-ver17).

Die Rechteprüfung läuft über die tatsächliche Verbindung des jeweiligen
Kontos. Sie prüft die wirksamen Rechte und erwartet die Ablehnung eines
Leseversuchs auf einer zweiten, nicht freigegebenen Testtabelle. Der
Diagnosepfad prüft zusätzlich den Zugriff auf die SQL-Request-DMVs.
Ob das Diagnosekonto im Linux-Gast auch die benötigten PolyBase-Daten
sieht, muss der Connector-Pilot zeigen. Die Anmeldung des Connectors
mit dem zugehörigen Credential, der TLS-Gegenversuch und der Abbau
der Laufobjekte gehören zum umschließenden Pilot.

### Ablauf der Messung

Die [Messsteuerung](../../Tests/Runtime/external_tables_measurement.py)
verwendet nach dem Abgleich der Daten und dem Statistikaufbau die verbleibende
Pilotfrist. Sie führt einmal die lokale Referenz und danach je einen Aufruf
mit und ohne Pushdown aus. Eine getrennte Diagnoseverbindung muss den
markierten Request während seiner Ausführung eindeutig sehen. Erst nach
erfolgreichem Ergebnisabgleich liest die Diagnose die zugehörigen Workrecords.
Mehrdeutige Handle-Zuordnungen, widersprüchliche Befunde
oder ein zu kurzer Request ohne beobachteten Handle ergeben `NOT_PROVEN`.
Ein weiterer Aufruf im selben Arm würde die Zuordnung mehrdeutig machen.

Der [ODBC-Adapter](../../Tests/Runtime/external_tables_odbc.py) gibt
Session-ID und Request-ID 0 auf einer frischen Reader-Verbindung aus.
Auf derselben Verbindung startet er anschließend genau eine Messabfrage.
Parallel sucht die getrennte Diagnoseverbindung nach Session-ID, Request-ID
und dem Marker des tatsächlich laufenden Statements. Die Identitätsabfrage
läuft separat, weil der Treiber frühe Resultate einer gemeinsamen Ausführung
gepuffert liefern kann.
Der Pilot übergibt dem Adapter eine bereits geprüfte Diagnoseverbindung
und eine Reader-Funktion mit begrenzter Anmeldefrist, ohne MARS und ohne
Connection Pooling. Die Reader-Abfrage übernimmt die verbleibende
Pilotfrist als ODBC-Timeout und verwendet dafür einen neuen Cursor auf derselben Verbindung.
Der Adapter liefert aggregierte Zeilen erst
nach der bestätigten Schließung des Reader-Cursors und der Verbindung.
Ein unbestätigter Abbau ergibt `FAIL_CLEANUP`. Der Gaststart, die
Verbindungsbereitstellung und der übrige SQL- und VM-Abbau bleiben Teil des
umschließenden Piloten.
Die [Ablauftests](../../Tests/Static/test_external_tables_measurement.py)
verwenden simulierte Antworten. Ob der Connector die erwarteten Felder
liefert und der Request lange genug für eine Live-Beobachtung sichtbar
bleibt, muss der zugelassene Pilot zeigen.

### Gastidentität für den autonomen Start

Die [Identitätsprobe](../../Tests/Runtime/external_tables_guest_identity.py)
ist ein Baustein für die Verbindung vom Host zum gestarteten Gast ohne
zusätzliche Host-Netzwerkschnittstelle. Auf Windows adressiert sie den
Hyper-V-Socket mit der VM-ID aus der Erzeugungsliste und der Dienst-ID
des VSOCK-Ports. Der Linux-Gast akzeptiert eine Verbindung vom
Elternsystem. Er gibt eine feste Antwort mit erwarteter Rolle,
Laufkennung und der aktuellen Zufallsabfrage zurück. Der Host prüft
alle Felder innerhalb der gemeinsamen Frist. Der Austausch führt keine
Gastbefehle aus.

Die Antwort enthält außerdem den SHA-256-Fingerabdruck des aktuell
gelesenen Debian-Paketbestands aus `/var/lib/dpkg/status`. Dafür werden
Paketname, Architektur und Version je installiertem Paket sortiert und
in einem festgelegten Format gehasht. Der Host berechnet seinen
Vergleichswert für die erwartete Rolle aus dem SHA-256-geprüften
Basisbestand und der gesperrten Paketliste. Ein abweichender Bestand
verhindert die Freigabe für SQL. Über den Kanal gehen weder die
Paketliste selbst noch Zugangsdaten. Das separat verifizierte
Python-Wheel des Abfragegasts ist außerhalb des Debian-Bestands.
[Microsoft-Referenz zu Hyper-V-Sockets](https://learn.microsoft.com/virtualization/hyper-v-on-windows/user-guide/make-integration-service).

Auf dem Windows-Testhost ließ sich der native Socket mit Python 3.13
öffnen. Die Paketliste des geprüften Abbilds enthält
`linux-modules-7.0.0-1017-azure` in Version `7.0.0-1017.17~24.04.1`.
Canonicals Dateiliste für dieses Paket führt `hv_sock.ko.zst` und
`vsock.ko.zst`. Für den echten Lauf bleiben das Laden der Module, die
bereits vorausgesetzte Registrierung der Dienst-ID am Host und der
Gaststart zu prüfen. Die Dienste, der Python-Treiber und die
Netzgrenzen werden separat geprüft.
[Canonical-Dateiliste](https://packages.ubuntu.com/noble-updates/amd64/linux-modules-7.0.0-1017-azure/filelist).

### Private Gastadressen und Routing nach der Anbindung

Der [Netzprüfer](../../Tests/Runtime/external_tables_guest_network.py)
bindet beide Gastrollen an zwei verschiedene IPv4-Adressen desselben
RFC-1918-Subnetzes. Er liest die Schnittstellen und sämtliche
IPv4- und IPv6-Routingtabellen mit `iproute2`. Pro Gast muss es neben
Loopback genau eine aktive Schnittstelle mit der vorgesehenen Adresse
und genau eine direkt verbundene Route für das Pilotnetz geben.
Zusätzliche Schnittstellen, Standardrouten, Gateways und Routen aus
des zugelassenen Bereichs verhindern die Bestätigung. IPv6 bleibt auf
Loopback, Link-Local und die dazugehörige Multicast-Route beschränkt.
[Ubuntu-Manpage zu ip-route](https://manpages.ubuntu.com/manpages/noble/man8/ip-route.8.html).

Der [Hyper-V-Hostprüfer](../../Tests/Runtime/Test-ExternalTablesHyperVNetwork.ps1)
verwendet die Switch-ID und die beiden VM-IDs aus der Erzeugungsliste.
Er verlangt den Switch-Typ `Private` und liest die vollständige lokale
Adapterliste einschließlich Managementadaptern. Jede Pilot-VM muss
genau einen Adapter haben, der mit dem vorgesehenen Switch verbunden
ist. Jeder weitere Teilnehmer auf dem Switch sowie ein zusätzlicher
oder getrennter Adapter einer Pilot-VM verhindern die Bestätigung.

```powershell
pwsh -NoProfile -File Tests/Runtime/Test-ExternalTablesHyperVNetwork.ps1 -SwitchId $PilotSwitchId -SourceVmId $SourceVmId -QueryVmId $QueryVmId
```

Der Hostprüfer gibt nur Typ und Anzahl der erwarteten Adapter aus.
Der Pilot ruft ihn innerhalb seiner gemeinsamen Prozessfrist auf.
Beim read-only Komponententest auf dem Hyper-V-Host wurden unbekannte
VM-IDs am vorhandenen privaten Switch abgewiesen. Der positive Fall
und die Konfliktvarianten sind mit simuliertem Inventar geprüft.
Der positive Switchnachweis für beide vorgesehenen Pilot-VMs
bleibt Teil des vorgesehenen Gastlaufs.
[Microsoft-Referenz zu Get-VMNetworkAdapter](https://learn.microsoft.com/en-us/powershell/module/hyper-v/get-vmnetworkadapter?view=windowsserver2025-ps).

Der native Komponententest verwendete Ubuntu 24.04 mit einer einzelnen
internen Schnittstelle. Der Prüfer akzeptierte ihre tatsächliche
`iproute2`-Ausgabe für die vorgesehene Adresse und wies dieselbe
Aufnahme für die Gegenrolle ab.

### Eingehendes SQL am Quellgast begrenzen

Der [Firewallbaustein](../../Tests/Runtime/external_tables_source_firewall.py)
legt vor der Netzanbindung eine eigene nftables-Tabelle an. Ihre
Input-Kette verwirft eingehenden Verkehr standardmäßig. Sie lässt
Loopback und TCP 1433 von der festgelegten Abfrageadresse zur
Quelladresse auf der Pilot-Schnittstelle zu. Der Baustein erstellt die
Tabelle in einer Transaktion und liest danach die tatsächlich aktive
Regelreihenfolge aus dem Kernel. Andere Tabellen bleiben erhalten.
Vor der ersten SQL-Verbindung wird dieselbe Kette erneut geprüft.

Ein nativer Ubuntu-24.04-Komponententest installierte die Regel im
netzgetrennten Quellcontainer und band ihn anschließend an ein internes
Testnetz an. Der lokale Client und der vorgesehene Abfrageclient
erreichten denselben TCP-Listener. Der Verbindungsversuch von einer
dritten Adresse lief in den Timeout. Eine zweite Anlage derselben
Tabelle scheiterte, die ursprüngliche Regel blieb überprüfbar. Der
Versuch verwendete einen TCP-Listener als Testgegenstelle. Die
Wiederholung mit SQL Server in den tatsächlichen Pilot-VMs steht aus.
[Ubuntu-Manpage zu nftables](https://manpages.ubuntu.com/manpages/noble/man8/nftables.8.html).

### Laufgebundenes TLS-Zertifikat erstellen

Der [TLS-Baustein](../../Tests/Runtime/external_tables_tls_material.py)
erstellt auf dem Quellgast eine einmalige Labor-CA und ein für einen
Tag gültiges RSA-Serverzertifikat. Sein einziger Subject Alternative
Name ist der vorgesehene SQL-Quellname des Laufs. OpenSSL prüft
Serverzweck, Zertifikatskette, Namen und die Übereinstimmung mit dem
privaten Schlüssel. Der CA-Schlüssel wird nach dem Signieren zusammen
mit den temporären Signierdateien entfernt. Das Blattzertifikat und
sein Schlüssel bleiben in einem privaten Verzeichnis im Quellgast.
An den Abfragegast geht nur das öffentliche CA-Zertifikat.

Die Quelldateien stehen innerhalb des Lebenszyklus des Bausteins
bereit. Die aufrufende Gaststeuerung muss sie für das SQL-Dienstkonto
lesbar halten und dieses Zertifikat in `mssql-conf` einrichten.
Das öffentliche CA-Zertifikat wird im Abfragegast für die spätere
Connectorverbindung verwendet. Die TLS-Probe prüft den tatsächlichen
Verbindungsweg vor der Messung.
[Microsoft-Referenz zu TLS-Einstellungen unter Linux](https://learn.microsoft.com/en-us/sql/linux/sql-server-linux-configure-mssql-conf#specify-tls-settings).

Im isolierten Linux-Komponententest akzeptierte eine native
TLS-Verbindung den vorgesehenen DNS-Namen. Ein anderer Laufname und
eine IP-Adresse ohne passenden SAN wurden abgewiesen. Der Test
bestätigte auch die Beseitigung der lokalen Schlüsseldateien. In einem
weiteren Komponentenlauf verwendete SQL Server 2025 Build `17.0.5065.9`
das erzeugte Blattzertifikat. Der ODBC-`sqlcmd`-Client im getrennten
Container akzeptierte das öffentliche CA-Zertifikat und den
vorgesehenen DNS-Namen. Die Gegenprobe mit falschem Zertifikatsnamen
wurde abgewiesen.
[OpenSSL-Referenz zur Zertifikatserstellung](https://docs.openssl.org/3.0/man1/openssl-req/).

### TLS-Kontrollpaar am Quellendpunkt

Vor der ersten ODBC-Verbindung lädt der Abfragegast `pyodbc` aus
seinem eigenen Installationsverzeichnis. Der
[Ladebaustein](../../Tests/Runtime/external_tables_odbc.py) prüft
Dateityp, Größe und SHA-256 der nativen Erweiterung anhand des
Wheel-Locks und lädt genau diese Datei unter CPython 3.12 auf Linux
x86-64. Er prüft die geladene Version und schaltet Pooling aus.
Derselbe Treiber wird an die TLS-Probe und den Messadapter übergeben.
Die Offlineprüfung leitet die erwarteten Erweiterungsbytes aus dem
hashgeprüften Wheel ab.
[Python-Referenz zum Wheel-Format](https://packaging.python.org/en/latest/specifications/binary-distribution-format/).

Ein netzloser Linux-Komponententest installierte das gepinnte Wheel
und lud die Erweiterung mit den aus den festgeschriebenen Ubuntu-Paketen
entnommenen unixODBC-Bibliotheken. Der Import meldete `pyodbc 5.5.0`
bei deaktiviertem Pooling. Der Importtest verwendete CPython 3.12.14.
Die Wiederholung im Abfragegast bleibt Teil des Pilot-Preflights.

Die [ODBC-Probe](../../Tests/Runtime/external_tables_odbc.py)
verwendet in der Positivprobe denselben laufgebundenen Quellhost, Port und
Reader wie der spätere Connector. Die verschlüsselte Verbindung mit
Zertifikatsprüfung muss die erwartete Datenbank und Anmeldung bestätigen.
`CONNECTIONPROPERTY` muss in dieser Verbindung die festgelegte
Quelladresse, den SQL-Port und die festgelegte Adresse des
Abfragegasts melden. Die Gegenprobe verwendet genau die bestätigte
Quelladresse. Der Abgleich beider Adressen wurde mit einem echten
SQL-Server-2025-TCP-Aufruf über ein getrenntes Linux-Containernetz geprüft.
[Microsoft-Referenz zu `CONNECTIONPROPERTY`](https://learn.microsoft.com/en-us/sql/t-sql/functions/connectionproperty-transact-sql?view=sql-server-ver17).

Beim ersten nativen Versuch akzeptierte der Linux-Treiber den Namen aus
`Server` auch mit abweichendem `HostnameInCertificate` und abgeschaltetem
Pooling. Die Gegenprobe verbindet sich deshalb über die bestätigte
numerische Adresse und denselben Port. Weder die Adresse noch der
absichtlich falsche Name in `HostnameInCertificate` steht im
Quellzertifikat. Die Probe verlangt SQLSTATE `08001` zusammen mit der
SSL-Diagnose zum Namensfehler. Die
[ODBC-Regressionen](../../Tests/Static/test_external_tables_odbc.py)
prüfen auch, dass allgemeine Login-, Timeout- und CA-Fehler den
Namensnachweis nicht ersetzen.
[Microsoft-Referenz zu `HostnameInCertificate`](https://learn.microsoft.com/en-us/sql/connect/odbc/dsn-connection-string-attribute?view=sql-server-ver17#hostnameincertificate).

Der native Komponententest lief auf Ubuntu 24.04
mit SQL Server `17.0.5065.9`, ODBC Driver `18.7.1.1`, CPython `3.12.3`
und `pyodbc 5.5.0`. Die Gegenprobe lieferte `08001` und die passende
SSL-Diagnose. Der Test verwendete eine temporäre Labor-CA, eine
markergebundene Quelldatenbank, den eigenen Reader und ausschließlich
Loopback im Wegwerfcontainer. Der SQL-Abbau und die Containerentfernung
waren erfolgreich. Das verwendete CPython-3.12-Linux-x86-64-Wheel wurde
gegen SHA-256
`4ee64db80a3cdcf87be2234d3793833b324fbd11fbe738afdaba46ca478cac13` geprüft.
Für den Pilot stehen die Gastbereitstellung mit den gebundenen Paketen und der
PolyBase-Lauf über den privaten Switch aus.
[PyPI-Dateinachweis für `pyodbc 5.5.0`](https://pypi.org/project/pyodbc/5.5.0/#files).


### Pilotablauf und Fristen

Der [Pilotablauf](../../Tests/Runtime/external_tables_pilot.py) verbindet
Gastvorbereitung, Datenbankanlage, Datenabgleich, Rechteprüfung, TLS-Probe,
Statistikaufbau, Messung und Abbau. Er verwendet eine gemeinsame Frist von
600 Sekunden für den Versuch und danach 120 Sekunden für den Abbau. Der
Gasttransport muss Eigentum, Paketstand, Isolation und Ressourcengrenzen
belegen, bevor SQL ausgeführt wird. Er speichert die Login-SIDs vor der
Erstellung. Der Ablauf reserviert den Abbau für jede Datenbank bereits
vor dem ersten Einrichtungsaufruf.

Die lokale [ODBC-Administration](../../Tests/Runtime/external_tables_odbc.py)
führt Setup und SQL-Abbau aus, liest das vollständige Fixture und
unterscheidet für den Abbau bestätigte Anwesenheit und Abwesenheit.
Die Gaststeuerung ordnet den Aufruf zuerst der geprüften VM und Rolle zu
und stellt eine frische lokale Adminverbindung bereit. Vor jedem Batch
prüft der Adapter IPv4-Loopback, Datenbankkontext, Engine-Build,
Adminberechtigung und Autocommit. Unerwartete Resultsets oder Fehler
beim Schließen der Verbindung verhindern eine Bestätigung. Der aktuelle
Paketlock liefert den gepinnten Python-ODBC-Client für den Abfragegast.
Der lokale Adminclient für die Quellvorlage und die Verbindung zur
Hoststeuerung bleiben Teil der konkreten Gastanbindung.

Ein Komponententest auf Build `17.0.5065.9` prüfte in einem lokalen
Wegwerfcontainer Einrichtung, je 4.096 Fixture-Zeilen, falsche
Datenbankkontexte und den Abbau beider markierter Datenbanken. Er
bestätigte auch die Abwesenheit des Containers.

Die [SQL-Bausteine](../../Tests/Runtime/external_tables_pilot_sql.py)
legen Daten- und Logdatei mit je 128 MiB Obergrenze an. Die Anlage in
`master` und die Konfiguration auf der neuen Datenbank laufen getrennt.
In den beiden Testdatenbanken bleiben automatische Erstellung und
Aktualisierung von Statistiken ausgeschaltet. Die Messstatistiken
entstehen ausdrücklich in der Setup-Phase.
[Microsoft-Referenz zur Datenbankanlage](https://learn.microsoft.com/en-us/sql/t-sql/statements/create-database-transact-sql?view=sql-server-ver17).

Ein Abbruch vor dem Setzen der Laufmarker kann eine noch unmarkierte
Testdatenbank hinterlassen. In diesem Fall bleibt ihr SQL-Abbau
unbestätigt. Der Gasttransport darf den eigenen Gast anhand seiner
Erzeugungsliste abbauen und meldet dessen Ergebnis getrennt. Jeder
unbestätigte Abbau verhindert einen positiven Gesamtbefund. Die
[Ablauftests](../../Tests/Static/test_external_tables_pilot.py) prüfen
diese Teilausfälle mit simulierten Gästen. Die konkrete Linux- und
Hyper-V-Anbindung muss im zugelassenen Pilot noch nachgewiesen werden.

### Abbau und Wiederaufnahme

1. Sperre weitere Demoaufrufe und beende nur eigene ausstehende Requests.
   Der SQL-Abbau beginnt erst, wenn der Transport die Schließung der
   Reader- und Connectorverbindungen bestätigt. Bei fehlender Bestätigung
   bleibt der SQL-Abbau unbestätigt und der Ablauf setzt bei Schritt 4 fort.
2. Prüfe in beiden Datenbanken den vollständigen Laufmarker. Entferne auf dem
   Abfrageknoten externe Tabellen, Datenquellen, Credential und Hauptschlüssel
   in dieser Reihenfolge und danach die eigene Datenbank und ihre Demoanmeldung.
3. Beende laut Quellinventar verbliebene Sessions des eigenen Quelllogins und
   entferne die eigene Quelldatenbank und den Quelllogin. Die
   [SQL-Abbaubatches](../../Tests/Runtime/external_tables_cleanup.py) prüfen
   Datenbankmarker und bestehende Sessions vor dem Löschen. Sie erzwingen
   keinen Verbindungsabbruch. Das Laufprogramm muss zuerst die eigenen
   Reader- und Connectorverbindungen schließen.
4. Entferne nach Abgleich mit der Erzeugungsliste die beiden VM-IDs, ihre
   eigenen Plattenkopien und den privaten Switch. Bestätige die Abwesenheit
   anhand der IDs. Bei unerreichbarer VM bleibt der SQL-Abbau unbestätigt.
   Verwende die Erzeugungsliste für den VM-Abbau und weise diesen Befund
   getrennt aus. Ein unvollständiger Cleanup verhindert `PASS`.

Der [Hyper-V-Abbauprüfer](../../Tests/Runtime/Test-ExternalTablesHyperVAbsence.ps1)
liest nach dem Abbau das Hostinventar und das lokale Laufverzeichnis.
Der Gasttransport übergibt die zwei VM-IDs, die Switch-ID und beide
absoluten VHDX-Pfade aus der ursprünglichen Erzeugungsliste. Die Plattenkopien
liegen im selben eigenen Laufverzeichnis, das bis nach der Prüfung erhalten
bleibt. Der Prüfer gibt `PASS` mit drei Nullzählungen aus, wenn alle fünf
aufgezeichneten Ressourcen fehlen. Ein Inventarfehler, ein fehlendes oder
umgeleitetes Laufverzeichnis oder ein verbliebener Eintrag verhindert den
Nachweis. Der Prüfer verändert keine Ressourcen.

Reserviere für jede Anmeldung vor der Einrichtung eine zufällige 16-Byte-SID
in der Erzeugungsliste des Laufs. Führe bei vorhandener markierter Datenbank
zuerst den Datenbankabbau aus. Der separate Loginabbau läuft danach in
`master`. Er prüft auch bei einer Wiederaufnahme ohne Datenbank den
exakten Namen und die gespeicherte SID. Unbekannte Anmeldungen oder aktive
Sessions führen zum Abbruch. Die Gastverbindungen und der VM-Abbau müssen
im Linux-Pilot noch nachgewiesen werden.

Für die Wiederaufnahme werden geprüfte Vorlagen für beide Rollen, ein
ausführbarer Vertrag mit konkreten Grants und Ressourcenoracles sowie ein
unabhängiger Methodenreview benötigt. Der Lauf bleibt nach DEC-078 ein eigenes
Arbeitspaket mit separater Freigabe. Die Lehrnotiz verweist weiterhin auf den
allgemeinen Pushdown-Befund.

Quellen zum Profil: [Build und Ubuntu-Unterstützung](https://learn.microsoft.com/en-us/troubleshoot/sql/releases/linux/release-history-2025),
[Microsoft-Paketindex für Ubuntu 24.04](https://packages.microsoft.com/ubuntu/24.04/mssql-server-2025/dists/noble/main/binary-amd64/Packages),
[PolyBase-Installation und Offlinekomponenten](https://learn.microsoft.com/en-us/sql/relational-databases/polybase/polybase-linux-setup?view=sql-server-ver17),
[SQL-Server-Connector](https://learn.microsoft.com/en-us/sql/relational-databases/polybase/polybase-configure-sql-server?view=sql-server-ver17)
[ODBC-Verschlüsselung](https://learn.microsoft.com/en-us/sql/t-sql/statements/create-external-data-source-transact-sql?view=sql-server-ver17#connection_options--key_value_pair) und [externe Workrecords](https://learn.microsoft.com/en-us/sql/relational-databases/system-dynamic-management-objects/sys-dm-exec-external-work-transact-sql?view=sql-server-ver17).

## Pushdown- und Messvertrag

`PUSHDOWN = ON` ist eine Konfiguration, kein Nachweis. Für den festgelegten
Connector und die konkrete Abfrage wären vor einem Performanceclaim mindestens
zu korrelieren:

1. Estimated Plan und dokumentierte Remote-Query-Evidenz mit Trace Flag 6408,
   soweit das gewählte Profil diese Darstellung unterstützt.
2. `sys.dm_exec_external_work.read_command` für denselben Request, soweit der
   Connector einen Wert liefert; NULL und mögliche 4.000-Zeichen-Trunkierung
   sind explizite Evidenzgrenzen.
3. Ergebnisoracle und Zeilen-/Requestbindung für dieselbe Ausführung. Ein
   abgeschnittener oder nicht korrelierbarer Remote-Befehl ergibt
   `NOT_PROVEN`, nicht `PASS`.
4. Falls `sys.dm_exec_dms_workers` als ergänzende Beobachtung verwendet wird,
   Zuordnung zu demselben Lauf und getrennte Erfassung von dokumentierten
   `bytes_processed`-, Zeit- und CPU-Feldern. `bytes_processed` wird ohne
   zusätzliche Qualifikation nicht als vollständige Netzwerkbytezahl
   bezeichnet.

Statistikzustand und Query-Form sind vor Vergleichsläufen festzulegen. Das
Erstellen externer Statistiken wird als eigene Setup-/Messphase behandelt:
SQL Server kann dafür externe Zeilen importieren und TempDB zum Sortieren
gesampelter Werte verwenden; diese Folgen sind möglich, nicht für jeden Lauf
garantiert. Ab SQL Server 2022 können fehlende Statistiken synchron und
automatisch entstehen. Ein Statistikaufbau während einer Messphase macht den
Lauf für einen direkten Vergleich ungültig.

Ein künftiger Messvertrag müsste gleiche Abfrageparameter, Warm-up-Regel,
Wiederholungen und Auswertungsmethode für beide Wege festlegen. Planform,
Remote-Query, tatsächliche Ergebnismenge, CPU, Laufzeit und Reads bleiben
unterschiedliche Evidenzarten. Es gibt noch keine belastbare Laufzeit-,
Transport- oder I/O-Schwelle; keine wird hier erfunden.

## Sicherheit, Cleanup und offene Gates

Ein ausführbarer Entwurf benötigt mindestens eine isolierte zweite Instanz,
einen nachweisbar read-only Quellprincipal, Credentialbehandlung außerhalb
von Repositorydateien, explizite Netzwerkgrenzen und ein bestätigtes
Ressourcen-/Zeitprofil. Die Credentials müssen für Connector und
Quellberechtigungen qualifiziert sein. Weder Connectorinstallation noch
Konfiguration eines PolyBase-Dienstes gehören in den unbeaufsichtigten
Standardpfad.

Für den vorgesehenen SQL-Server-Connector wird der Remotezugriff mit
SQL-Authentifizierung konfiguriert; der PolyBase-SQL-ODBC-Connector
unterstützt laut Herstellerdokumentation kein Kerberos. Das datenbankweite
Credential setzt einen Datenbank-Hauptschlüssel voraus. Der Erstellungsprincipal benötigt
kontextabhängig `CREATE TABLE`, `ALTER ANY SCHEMA`,
`ALTER ANY EXTERNAL DATA SOURCE` und `ALTER ANY EXTERNAL FILE FORMAT`;
`CONTROL DATABASE` ist für Master Key, Credential und externe Datenquelle
erforderlich. Das Credential muss auf der Remotequelle die für die Abfrage
erforderlichen Leserechte besitzen. Weil `ALTER ANY EXTERNAL DATA SOURCE` den
Zugriff auf alle datenbankweiten Credentials eröffnet, muss sein Einsatz auf eine eng
begrenzte Setupidentität beschränkt werden. Der spätere Readerprincipal,
Erstellungsprincipal und Remote-Login sind getrennt zu modellieren; aus der
SQL-Authentifizierung des Connectors folgt keine pauschale Freigabe derselben
Identität für alle drei Rollen.

Cleanup muss lokale externe Tabellen und Datenquellen sowie den
markergebundenen synthetischen Quell-Snapshot getrennt behandeln. Das Entfernen
eines External-Table-Metadatensatzes ist kein Beleg, dass externe Quellobjekte
oder Credentials entfernt wurden. Wiederherstellung nach Teilausfall,
Erreichbarkeitsverlust oder unterbrochenem Cleanup ist vor einer Ausführung
eigenständig zu qualifizieren.

Vor einem Demo-Vertrag bleiben offen:

- Nachweis der vorbereiteten Linux-VMs und der gebundenen Abhängigkeiten für
  den ersten Pilotkandidaten. Eine Windows-Matrix bleibt getrennt;
- Verfügbarkeit und Eigentum der separaten synthetischen Quellinstanz,
  Netzwerkisolation, Berechtigungen und Credential-Lifecycle;
- Durchsetzung der im Profil konkretisierten Ressourcen- und Zeitgrenzen sowie
  Abnahme des Abbruch- und Wiederherstellungspfads;
- Pushdown-Evidenzkorrelation und Aussagekraft der Transport-/DMS-Metriken im
  festgelegten Connectorprofil;
- Statistikzustand, Setup-/Messphasentrennung, vollständiger Cleanup und
  unabhängiger Methodenreview;
- Zulassung des separaten Arbeitspakets für einen vollständigen Pilot
  gemäß [DEC-078](../../.ai/DECISIONS.md).

Die integrierten Komponentenprüfungen belegen einzelne Voraussetzungen.
Dazu zählen die gebundene Paketinstallation bei getrenntem Netzwerk,
die durchgesetzte Eingangsregel und SQL-TLS mit geprüfter Zertifikatsidentität.
Die vollständige Zwei-VM-Strecke mit einer PolyBase-Abfrage gegen die
synthetische Quelle und deren Pushdown-Nachweis steht noch aus.
[Pakete](https://github.com/gecompat/SQL_PerformanceSchulung/pull/1203) ·
[Eingangsregel](https://github.com/gecompat/SQL_PerformanceSchulung/pull/1206) ·
[SQL-TLS](https://github.com/gecompat/SQL_PerformanceSchulung/pull/1207)

## Quellen und Geltungsgrenze

Die technischen Produktbefunde und ihre Einschränkungen sind an `SRC-153`
bis `SRC-157` im [Projektquellenregister](../Research/SOURCE_REGISTER.md#external-tables-und-polybase-2026-11)
und im [Quellen- und Zugriffswegreview](EXTERNAL_TABLES_SOURCE_REVIEW.md)
gebunden. Die Edition-, Compatibility-Level- und Berechtigungsgrenzen wurden
am 14. November 2026 anhand derselben Quellen erneut eingeordnet. Die
Curriculum-IDs sind bestehende Projektanker, keine neue
Registrierung. Empfehlungen zu Fixture, Prüfreihenfolge und Gates sind
Projektentwurf und keine Herstellerzusage oder Laufzeitevidenz.
