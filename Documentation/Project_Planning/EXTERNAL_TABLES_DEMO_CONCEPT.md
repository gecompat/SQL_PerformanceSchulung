# External Tables: statischer Lehr- und Demoentwurf

Stand: 12. November 2026  
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
Der Entwurf sieht noch keine Zeilenanzahl oder Lastgröße vor: diese Werte
benötigen ein bestätigtes Ressourcenprofil.

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

Cleanup muss lokale externe Tabellen und Datenquellen sowie den
markergebundenen synthetischen Quell-Snapshot getrennt behandeln. Das Entfernen
eines External-Table-Metadatensatzes ist kein Beleg, dass externe Quellobjekte
oder Credentials entfernt wurden. Wiederherstellung nach Teilausfall,
Erreichbarkeitsverlust oder unterbrochenem Cleanup ist vor einer Ausführung
eigenständig zu qualifizieren.

Vor einem Demo-Vertrag bleiben offen:

- Entscheidung über gemeinsames Windows-Profil oder explizite
  Windows-/Linux-Teilprofile und konkrete Builds, CUs, Editionen sowie
  Compatibility Levels;
- Verfügbarkeit und Eigentum der separaten synthetischen Quellinstanz,
  Netzwerkisolation, Berechtigungen und Credential-Lifecycle;
- konkrete Fixturegröße, Ressourcenlimits, Zeitbudget und Abbruch-/Recoverypfad;
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
gebunden. Die Curriculum-IDs sind bestehende Projektanker, keine neue
Registrierung. Empfehlungen zu Fixture, Prüfreihenfolge und Gates sind
Projektentwurf und keine Herstellerzusage oder Laufzeitevidenz.
