# External Tables: statischer Lehr- und Demoentwurf

Stand: 23. November 2026
Status: `PROPOSED`; Konzept auf Basis des Quellenreviews, keine registrierte Demo,
kein ausgeführter Connector und keine Laufzeitfreigabe

## Lernfrage und Curriculumanschluss

Der mögliche Lehrschnitt konkretisiert den bereits vorhandenen Anker
`LO-M03-05`/`CLM-045`: Remote Pushdown ist provider-, Ausdrucks- und planabhängig
und muss im konkreten Fall belegt werden. `QRY-012` behandelt bereits Linked
Server. External Tables wären eine zweite Zugriffsform zur selben fachlichen
Frage, keine Behauptung, dass PolyBase generell schneller oder einfacher ist.
Ob das Thema in `QRY-012` integriert oder später als eigenes Arbeitspaket
geführt wird, bleibt bis zur vollständigen Konzept- und Methodenabnahme offen.
Es wird keine neue stabile Demo-ID vergeben.

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

### Aufgelöste Ubuntu-Pakete für beide VM-Rollen

Der Paketstatus wurde am 23. November 2026 direkt aus dem Root-Dateisystem
der geprüften VHD gelesen. Alle 659 installierten Paketnamen und Versionen
stimmten mit Canonicals Manifest überein. APT 2.8.4 verwendete diesen
Paketstatus, die beiden geprüften Microsoft-`.deb`-Dateien und die
signierten Ubuntu-Quellen `noble`, `noble-updates` und `noble-security`
aus dem [datierten Ubuntu-Archiv](https://snapshot.ubuntu.com/ubuntu/20261123T000000Z/).
Die Simulation mit `--no-install-recommends` ergab zwölf zusätzliche
Ubuntu-Pakete und zwei SQL-Pakete, ohne Upgrades oder Entfernungen.
Die Versionen, Pfade, Größen und SHA-256-Werte stehen in der
[APT-Paketliste](external_tables_apt_lock.json). Alle zwölf Ubuntu-Payloads
wurden aus dem Snapshot geladen und gegen diese Prüfsummen geprüft.

Der [APT-Prüfer](../../Tests/Static/verify_external_tables_apt_plan.py)
erwartet die Ausgabe eines erfolgreich beendeten `apt-get -s`-Laufs.
Er prüft die Paketnamen und Versionsübergänge. Optional prüft er die
Dateien aller 14 Pakete in demselben Verzeichnis.

```text
python Tests/Static/verify_external_tables_apt_plan.py APT-PLAN --role query --payload-directory PAKETVERZEICHNIS
```

Ein separater Lauf vom selben Paketstatus mit ausschließlich dem
Engine-Paket ergab für die Quell-VM die zwölf bereits gebundenen
Ubuntu-Pakete plus `mssql-server`. Die 13 Installationsschritte enthalten
dieselben Versionen wie das Abfrageprofil und keine Upgrades oder
Entfernungen. Verwende `--role source` für diesen Plan. Die Simulation
installiert weder SQL Server noch PolyBase. Installationsskripte,
Dienstzustand und der Connectorlauf bleiben im Gast zu prüfen.

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

Der nächste Lauf prüft den isolierten Start einer frischen Kopie in
Hyper-V. Die hier geprüfte Dateiintegrität belegt weder einen erfolgreichen
Gaststart noch eine installierte Rolle.

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
eine Remote-Anweisung ohne dieses Prädikat zeigen. Verknüpfe Workrecords über
`execution_id`, die erwartete Tabellenadresse und die Session des Arms mit
der jeweiligen Ausführung. Die konkrete Zuordnung des lokalen Requests zur
PolyBase-Ausführung ist Gegenstand des Methodenreviews. Bei fehlendem oder
mehrdeutigem Workrecord, nicht auflösbaren Parametern oder abgeschnittenem
Remote-Befehl bleibt der Pushdown-Befund `NOT_PROVEN`. Die lokale Referenz
belegt das Ergebnis. Eine Remoteaggregation oder Leistungswirkung erfordert
einen eigenen Befund.

### Abbau und Wiederaufnahme

1. Sperre weitere Demoaufrufe und beende nur eigene ausstehende Requests.
2. Prüfe in beiden Datenbanken den vollständigen Laufmarker. Entferne auf dem
   Abfrageknoten externe Tabellen, Datenquellen, Credential und Hauptschlüssel
   in dieser Reihenfolge und danach die eigene Datenbank und ihre Demoanmeldung.
3. Beende laut Quellinventar verbliebene Sessions des eigenen Quelllogins und
   entferne die eigene Quelldatenbank und den Quelllogin. Kontrolliere auf
   beiden VMs die Abwesenheit aller Laufobjekte.
4. Entferne nach Abgleich mit der Erzeugungsliste die beiden VM-IDs, ihre
   eigenen Plattenkopien und den privaten Switch. Bestätige die Abwesenheit
   anhand der IDs. Bei unerreichbarer VM bleibt der SQL-Abbau unbestätigt.
   Verwende die Erzeugungsliste für den VM-Abbau und weise diesen Befund
   getrennt aus. Ein unvollständiger Cleanup verhindert `PASS`.

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
- formale Curriculum-Scopeentscheidung. `DEC-078` nimmt im aktuellen Stand
  keine ausführbare External-Tables-Phase in `QRY-012` auf; ein späterer
  separater Demo-Vertrag und seine Freigaben bleiben offen.

Bis diese Gates geschlossen sind, bleibt dies ein statischer Lehrentwurf.
Es wurde kein SQL, Connector, Netzwerk, Dienst oder Credential verwendet.

## Quellen und Geltungsgrenze

Die technischen Produktbefunde und ihre Einschränkungen sind an `SRC-153`
bis `SRC-157` im [Projektquellenregister](../Research/SOURCE_REGISTER.md#external-tables-und-polybase-2026-11)
und im [Quellen- und Zugriffswegreview](EXTERNAL_TABLES_SOURCE_REVIEW.md)
gebunden. Die Edition-, Compatibility-Level- und Berechtigungsgrenzen wurden
am 14. November 2026 anhand derselben Quellen erneut eingeordnet. Die
Curriculum-IDs sind bestehende Projektanker, keine neue
Registrierung. Empfehlungen zu Fixture, Prüfreihenfolge und Gates sind
Projektentwurf und keine Herstellerzusage oder Laufzeitevidenz.
