# CON-010: unabhängiger Quellenabschluss des privaten Pooltests

## Zweck und Grenze

TSK-009 prüft nach der echten Serverlogin-Komponente drei getrennte eigene Pools
mit sechs Checkouts. Die vorhandene private Assembly bleibt unverändert. Kein
neuer Provider, keine Installation und kein allgemeiner TDS-/Supportnachweis.
Die [kanonische Poolgrenze](SQL_SERVER_2025_AI_TENANT_POOL_REVIEW.md) bleibt maßgeblich.

## Geschlossene Befunde

Root prüfte unabhängig vom Implementierungsverantwortlichen die neuen Grenzen:

- Physische Wiederverwendung benötigt tatsächliche Serverconnection-ID und
  connect_time samt Session-, SID-, DB- und Appbindung. ClientGUID-Gleichheit
  wird weder gefordert noch als physischer Beweis verwendet.
- Dieselbe Credentialinstanz und derselbe Poolkey bleiben je Lane erhalten;
  drei tatsächlich verschiedene Poolkeys und physische Serververbindungen sind Pflicht.
- Reset wird vor jeder Reparatur beobachtet; manipulierte Kontextwerte dürfen
  die vollständigen eigenen Quellen nicht verändern. Unmapped muss positiv
  authentifiziert sein und null Rows erhalten.
- Tatsächliche Poolreferenzen bleiben bis OwnClearPool/Close und frischer
  physischer Abwesenheit erhalten; Dispose folgt danach. Kein ClearAllPools.
- Vollständige bekannte Receipts bleiben vor semantischer Auswertung erhalten.
  Falsche Ergebnisse bleiben FAIL; malformed, Timeout und unbewiesene Enden UNKNOWN.
- PowerShell erhält SQL-Datumstrings ausdrücklich ohne automatische Umwandlung.
- Retry berücksichtigt .py/.sql/.ps1; reine Planänderung genügt nicht.
- Die einmalige 60-Sekunden-Cleanupdeadline beginnt vor dem höchstens
  40-Sekunden-Child. Alle folgenden Drops und der eigene Abbau teilen diese Uhr.

## Tatsächliche reine Prüfungen

Elf gezielte Pythonmethoden und drei AST-extrahierte tatsächliche
PowerShell-Helpergruppen PASS. Es wurde kein vollständiger Caller ausgeführt,
keine Assemblyverbindung geöffnet und kein SQL/Poolclear/Container gestartet.
Root prüfte zusätzlich drei Admission-/Effektgruppen sowie drei relevante
Deadline-/Cleanup-/Retrymethoden unter python -O. Geschützte Gates bleiben explizit.
Ein erster reiner Cleanupmock verwendete den reservierten Parameter $Args;
nach Änderung auf $Items bestanden. Roots erste optimierte Methodenauswahl
enthielt einen falschen Methodennamen; der korrigierte Einzelaufruf bestand.
Keine Nativekandidaten wurden durch diese reinen Fehler verbraucht.

Quellenkarte: 42 Bindungen einschließlich fünf bytegleicher qualifizierter Basen,
16 fester SQL-Reviewquellen sowie zwei unveränderter vorhandener Hostbinärdateien.
Alle nichtbinären Quellen werden privat als tatsächliche Bytes archiviert;
Hostartefakte werden ausschließlich per SHA und vorhandener Metadatenbindung
referenziert. Vier exklusive Rootgates binden Review, Quelle, Budget und Kandidat.
Unbekannter Modell-/Reasoningtokenverbrauch bleibt UNKNOWN; null neue Modellaufrufe.

## Runtime und Integration

Die erste Runtimequalifikation folgt erst auf den gebundenen Quellenabschluss.
Noch kein Reuse-/Reset-/Cleanup-PASS; tatsächlicher Befund wird hier ergänzt.
Die rote Login-DDL (Data Definition Language; Anweisungen zum Definieren und Ändern von Datenbankobjekten) bleibt ausschließlich im neuen eigenen isolierten Testcontainer.
Keine Standard-CI (Continuous Integration; automatisierte Integrationsprüfungen) mit roten Effekten, keine anderen Repositoryänderungen.


## Kandidat 1: bekanntes FAIL vor Checkoutnachweisen

Der neue eigene SQL-17.0.5005.3-Testcontainer erreichte Setup, drei Loginzuordnungen
und einen vollständigen Quellen-/Rechtezustand. Der separate PowerShell-Child
lieferte ein vollständiges credential-geprüftes FAIL-Receipt mit bekanntem Ende,
aber null Checkoutrecords und unbewiesenem Poolcleanup. Seine erste Fehlerbehandlung
erhielt keine konkrete Ursache; daraus folgt ausdrücklich kein Provider-/TDSbefund.
Zehn tatsächliche SQLcmd-Handles plus ein separater Poolchild; kein UNKNOWN.

Keine Login-/DB-Adoption bei fehlendem Poolcleanupleasing. Der vollständige eigene
Namespace ohne Mounts wurde innerhalb derselben Deadline entfernt. Root prüfte
die tatsächlichen Quellenbytes, den vollständigen Zustand, das Receipt und neue
CID-/Namens-/SQLinputabwesenheit unabhängig. SQL-Abwesenheit bleibt NOT_ESTABLISHED,
Poolreuse/Reset/Pool-Cleanup bleiben NOT_ESTABLISHED. Historisches FAIL bleibt erhalten.

Nächster zulässiger Kandidat ergänzt ausschließlich begrenzte credential-geprüfte
Fehlerdiagnose im Receipt. Er benötigt geänderte Quellen, neuen engen Sourceschluss
und kandidatbezogene Rootadmission; das gemeinsame Sechserbudget bleibt erhalten.


## Geänderter Diagnostikkandidat 2 (SOURCE_ONLY)

Ein neuer eng begrenzter Receiptbefund erhält ausschließlich feste Phase, höchstens
sechs typisierte Exceptionklassennamen und optionale eigene Fehlercodes aus einer
Whitelist. Keine Rohmeldungen, Stacks, ENV, Secrets oder Verbindungsstrings.
Parent und Oracle prüfen die komplette Diagnoseform; positive Receipts verlangen
Fault=null. Credentialprüfung bleibt vor privater Persistenz. Geänderte reine
Receipt-/Diagnosegegenfälle und eine tatsächliche AST-Failure-Helpergruppe PASS;
keine Wiederholung unveränderter grüner Vollsuites. Root schließt diesen kleinen
Delta unabhängig und bindet die nächste Admission auf dieselbe Sechserwelle.


## Kandidat 2: Konstruktion vor Open fehlgeschlagen

Der korrigierte Diagnosecaller liefert ein bekanntes FAIL-Receipt mit
Phase OWNER_CONNECTION und Typ System.ArgumentException; null Checkoutrecords.
Das grenzt den Fehler auf die Verbindungskonstruktion ein, ohne Rohmeldungen oder
Secrets zu exportieren. Kein Provider-/TDS-/Authfehlernachweis. Wieder zehn
SQLcmd-Handles plus ein separater Child, ein vollständiger Zustand; Root prüfte
Quellen, Receipt und frische eigene CID-/Namens-/SQLinputabwesenheit unabhängig.
SQL-/Pool-Cleanup bleibt NOT_ESTABLISHED, kein UNKNOWN. Beide historische FAILs
bleiben erhalten. Eine geschlossene lokale Constructorgegenprobe mit synthetischen
Credentials und ohne Open/SQL/ClearPool soll die konkrete Clientkorrektur vor dem
nächsten eigenen Container prüfen. Dieselbe Sechserwelle bleibt maßgeblich.


## Clientkorrektur vor Kandidat 3

Die tatsächliche geschlossene Gegenprobe belegt das ungültige Keyword DataSource:
PowerShell dispatchte die Propertysyntax des Builders als Dictionaryzugriff.
Die Korrektur setzt und liest ausschließlich feste öffentliche Properties über
PropertyInfo. Fünf tatsächliche Konstruktionen (Owner/A/B/U/A) bleiben Closed,
prüfen sämtliche Optionen, unveränderte Credentialinstanz, drei verschiedene
LaneKeys und denselben A-Key; unmittelbar Dispose. Open/SQL/ClearPool/Container
jeweils null. Root prüfte das enge Quelldelta sowie konkrete Records unabhängig.
Geänderte Quellen sind auf denselben Sechserledger gebunden; kein neues Budget.


## Kandidat 3: begrenzte private Poolkomponente PASS

Der korrigierte Caller bestand im neuen eigenen SQL-17.0.5005.3-Testcontainer
sechs Checkouts in A/B/U/A/B/U-Reihenfolge. Tatsächliche Owner-DMVconnection_ids
und connect_time belegen drei physische Wiederverwendungen innerhalb der Lanes;
die drei tatsächlichen Poolkeys und Serververbindungen sind zwischen Lanes getrennt.
ClientGUIDs bleiben typisierte Metadaten ohne Gleichheits-/Differenzoracle.

Zwölf vollständige Before-/After-Ergebnisse erhalten die tatsächlichen
Login-/User-/SID-/DBbindungen: A/B jeweils eigene komplette Quelle samt VECTOR(3),
positiv authentifiziertes Unmapped null Rows. Sechs manipulierte Kontextwerte
wechseln keinen Tenant; der zweite Checkout beobachtet NULL vor jeder Reparatur.
Zwei vollständige Quellen-/RLS-/Principal-/Rechte-/Configzustände sind identisch.
Die früheren grünen Policy-/Impersonation-/REVOKE-Negativtests wurden nicht wiederholt.

Tatsächliches OwnClearPool für drei gehaltene Referenzen, Close und neue physische
Abwesenheit im Child; eine zusätzliche frische Parentabfrage bestätigt den Abbau.
Erst danach gehaltene eigene Login-Drops vor DBdrop, neue getrennte SQL-Abwesenheiten,
eigener Containerabbau und frische CID-/Namens-/SQLinputabwesenheit. Bekannte
Request-/Childenden, kein UNKNOWN. Alle Aktionen blieben innerhalb derselben
60-Sekunden-Cleanupdeadline, die bereits vor dem höchstens 40-Sekunden-Child begann.

Root prüfte unabhängig tatsächliche Receipts, vollständige Rawstates und deren
Gleichheit mit dem Messrecord, alle archivierten Effektquellen sowie neue eigene
Namespace-/Inputabwesenheit. Checkpoint3 ist auf den abgeschlossenen Ledger gebunden.
Drei eigene Container, insgesamt 37 SQLcmd-Handles und drei separate Poolchildren;
C3 allein 17 SQLcmd-Handles. Beide historische FAILs erhalten, C1/C2 SQL-/Pool-Cleanup
NOT_ESTABLISHED; ihre bestätigte eigene Namespaceabwesenheit bleibt getrennt.
Keine weiteren Kandidaten nach erreichtem PASS und keine neue Modellinferenz.

Der PASS gilt ausschließlich für diesen privaten Caller, diese vorhandene
Assembly-/Host-/Enginekombination, drei synthetische Lanes und die feste serielle
Population. Allgemeine Provider-/OS-/Authformen, Performance, ANN (Approximate Nearest Neighbor; näherungsweise Suche nach ähnlichen Vektoren)/Tenantseitenkanäle,
Passwort-/TLSintegrität, öffentliche Poolconsumer und volle CON-010-/TSK-009-/TP-CON-
Abnahme bleiben offen. Andere Repositories unverändert; allgemeine Entwicklung
und DGN-007 bleiben pausiert. Aktuelle Head-/Main-Gates, PRintegration, Synchronisierung
und eigener Branchcleanup sind vor Schnittabschluss erforderlich.
