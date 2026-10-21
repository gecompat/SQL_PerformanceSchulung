# TSK-006: reiner IDX-012-DML-/Rollenrecordvertrag

PR229 vollständig abgeschlossen: sieben aktuelle Head- und fünf Main-Gates,
Main d28761f2990018a5e8e5a768b6ebc2643e0eb993, vollständiger identischer Tree,
FF-Synchronisierung und eigene lokale/Remote-Branches entfernt. 391 private
Dateien einschließlich des erhaltenen Nativeinputs sind vor der tatsächlichen
Worktreearchivierung hashverifiziert gesichert. Der erste App-Archivversuch blieb
wegen des Chat-Anhanglimits queued; nach Entfernen abgeschlossener alter PR-
Verknüpfungen sind tatsächliche Pfad-/Git-Worktreeabwesenheit und Archiv bestätigt.
Der [VECTOR-Fehlercheckpoint](SQL_SERVER_2025_AI_VECTOR_NATIVE_REVIEW.md) bleibt
FAIL_HARD6_UNKNOWN mit SQLcleanup NOT_ESTABLISHED; keine Wiederaufnahme.

## Kleiner unabhängiger Umfang

Dieser Schnitt macht die vorhandenen IDX-012-DML-/Rollenrecordgrenzen als reinen
öffentlichen Vertrag prüfbar. Ein Implementer, ein enger Rootreview für tatsächliche
Evidenz, Rechte-/SID-/Ownershipbindung und Cleanup; keine weitere Reviewkette.
Sechs relevante Quellenkandidaten, Checkpoint3/hard6. Null neue SQL-, Container-,
Provider-, Modell- oder Hostaufrufe; keine Producer-/Runtimejob-/Selectoränderung.
Nach Sourceabschluss höchstens ein gebundener Offline-Auswertungsdurchlauf der
beiden unveränderten historischen Rollen-C3-Akten. Ein fehlender Nachweis wird
nicht rekonstruiert; kein unveränderter Wiederholungsdurchlauf.

Vorhandene Autoritäten: [ANN-Profilentscheid](SQL_SERVER_2025_AI_ANN_PROFILE_DECISION.md),
[DML-Teilnachweis](SQL_SERVER_2025_AI_IDX012_DML_BOUNDARY_REVIEW.md) und
[Rollen-Teilnachweis](SQL_SERVER_2025_AI_IDX012_ROLE_REVIEW.md).
Nur 17.0.5005.3/Linux/Developer/CL170, Generation UNKNOWN. Herstellerangaben zu
anderen Builds ändern diese konkreten empirischen Grenzen nicht.

Der Vertrag benötigt exakte UPDATE-/DELETE-/INSERT-/MERGE-Reihenfolge,
998/999/1000 Zwischenpopulation, ursprüngliche 999-Row-Quelle und Rollbackwerte
0/0. Zwei einzelne Rechteentzüge halten mit SKIP_PERMISSION vor Setup an;
Grantrestore und eigene Owner-SID bleiben gebunden. Je Kostenphase sind
ROLE_START, ADMIN_BUILD, ROLE_RESTORED und ROLE_END geordnet zu erfassen.
Admin ausschließlich beim jeweiligen Indexbuild; kein behaupteter Nicht-sysadmin-
Build oder allgemeines Minimalrollenprofil.

Vollständige Marker-/Index-/Principal-/SIDbindung, ursprüngliche Preview-/MAXDOP-
Restores und DB-/Principal-/SID-/CID-/Namensabwesenheit müssen ihren tatsächlichen
Captureumfang behalten. Callerflags bleiben DECLARED_NOT_INDEPENDENTLY_ATTESTED.
Dokumentation oder true-Felder ersetzen keine individuellen Client-/Input-/
Serverrequest-Endbelege. Export ausschließlich begrenzter Counts und Statuswerte,
keine vollständigen lokalen Identitäten, Secrets oder realen Diagnosekanäle.

Die vorhandenen DMLrecords enthalten Fehlernummer, State und Meldung, aber keine
Severity oder Zeilennummer. SourceRestored und IndexMetadataUnchanged stammen
aus SQL-Guardlogik; sie sind keine unabhängigen Vollcaptures jeder Operation.
Acht DML-/acht Kontextrecords, fünf Principal-Audits und zwei Rechte-SKIPs werden
von vollständigen Quellen-, Marker- und Snapshotrecords getrennt geprüft.
Fehlende individuelle Input-/End-/Namespacewitnesses bleiben NOT_ESTABLISHED;
ein konsistenter historischer Recordexport kann deshalb weiterhin WARN melden.

## Umsetzung und Aufwand

Geplant sind ein reiner Pythonrecordvertrag, gezielte Gegenproben, eine synthetische
Fixture und eine kurze HowTo-Anleitung. Im bestehenden KI-Workflow nur neue statische
Trigger/Testschritte; Runtimejob, Versionsmatrix und Selector bleiben unverändert.
Lokale Tests beschränken sich auf neue Vertragseigenschaften; historische native
DML-/Rollen-/Cleanupprüfungen werden nicht wiederholt. Source-/Expectedpins und
Privacy vor Commit sowie aktuelle Head-/Main-/Tree-/Sync-/eigene Cleanupgates.

Aktuell SOURCE_PREPARATION_ONLY. Synthetische Gegenfälle sind kein Native-PASS;
öffentliche Multi-Login-Producerqualifikation, vollständige individuelle Capture-
bindung, aktive Hard-Aborts, Minimalrollen und TP-PERF bleiben NOT_ESTABLISHED.
Volle TSK-006- und Workstreamabnahme offen; Modell-/Tokenverbrauch UNKNOWN.

## C1: eingefrorener Sourceabschluss

Consumer, zwölf gezielte Gegenproben, fester Expected-Vertrag und HowTo sind
vorbereitet. Zwölf Methoden normal und vier Schutzmethoden unter -O bestanden
mit Originalkanälen, gehaltenen PID (Process Identifier; Prozesskennung)/poll0/rc0 und aktuellen Quellenpins. Kein
historischer Report oder neuer Nativeaufruf. Ein früher Workflow-LF-Splitfehler
vor dem Schreibzugriff ist als Sourcefinding erhalten; initialer Rawkanal fehlt.
Die korrigierte Bearbeitung behält CRLF und den vollständigen Runtimebody bei.

Root hat die gesamte neue Source für Schema, Reihenfolge, numerische Oracles,
SID-/Grant-/Markerbindung, Rollback, begrenzten Export und fehlende Captures eng
geprüft. Aktuelle Privacy der neun geänderten Dateien bestanden. Eine eigene
mechanische Root-Selectorprüfung verwendete zunächst CRLF-decode statt des
tatsächlichen read_text-Vertrags und scheiterte; nach dieser Readerkorrektur ist
die Auswahl ohne Test- oder Runtimewiederholung bestätigt. RawRuntimebody
bytegleich, Selector unverändert, tatsächliche Runtimeauswahl=false.

Verarbeitungsaufwand: zwei neue Pythonprozesse je bestehendem Staticjob (12
normal/4 optimiert), drei neue Triggerpfade je PR-/Push-Event, keine neuen Jobs
oder Matrixläufe. Bereits bestehende statische Jobgates bleiben erhalten.
Der öffentliche Verbraucher akzeptiert nur InMemory-Records und seinen festen
Expectedread; Caller-/SQLguardflags werden nicht zu unabhängiger Attestierung.
Genau ein gebundener historischer Offline-Durchlauf folgt erst nach konkretem
Akten-/Input-/Adapter-/Rootabschluss. Alle Qualifikationsgrenzen bleiben offen.

## C1: tatsächlicher Offline-FAIL und geänderter C2-Folgeentscheid

Der einmalige C1-Durchlauf endete bekannt mit rc1, ohne Timeout oder UNKNOWN,
in 0,1562s. Keine erfolgreich abgeschlossene Reportauswertung; die konkrete
erste Exception und Anzahl erreichter Aufrufversuche wurden vom Adapter nicht
erhalten und werden nicht nachträglich erfunden. Alle 80 historischen Dateien,
fünf öffentlichen Sources und beide Preparedrecords sind vor/nach bytegleich.
Null neue SQL-/Container-/Provider-/Modell-/Hostaufrufe, kein Rawaktenrewrite.

Eine anschließende reine Source-/Byteeinsicht findet einen konkreten Schemafehler:
SQL FOR JSON (JavaScript Object Notation; strukturiertes Textformat) hat varbinary-Markerwerte als Base64 erfasst; der Consumer und seine
Handfixture erwarten Hextexte. Der vorhandene Snapshot kann diese Markerprüfung
daher nicht bestehen. Das ist kein Nachweis der verloren gegangenen ersten Exception.
Die gelesenen Koordinaten liefern keinen Korrekturgrund für das numerische Oracle.

Innerhalb desselben Sechskandidatenbudgets folgt genau ein geänderter C2:
kanonische Base64-Darstellung der vollständigen erwarteten UTF16LE-Markerbytes,
ByteLength weiterhin exakt; zusätzlich vollständige eigene Datei-Namensbytes.
Keine Rawaktennormalisierung, keine Koordinaten-/Distanz-/Rollen-/Rollback-
Toleranzlockerung. Der Adapter hält künftig feste Fehlercodes und tatsächlich
erreichte Reportschritte. C1-Sources, Originalresultat, Admission, Scope, Rawkanäle
und fehlende Felder bleiben als historischer Checkpoint erhalten.

Explizite begrenzte Budgeterweiterung: höchstens zwei Offlineprozesse und vier
Reportaufrufe kumulativ, einschließlich der verbrauchten C1-Reservation. C2 genau
ein weiterer Prozess mit höchstens zwei fail-first Reports/max60s und gehaltenem
End-/Wallclockbeleg. Keine stille Erneuerung des ursprünglichen Einmalbudgets,
kein unveränderter Retry. Source-/Akten-/Expected-/Privacy-/enger Rootabschluss
und neue aktuelle Admission vor C2; nach C2 keine weitere Offlinewiederholung
dieses Pakets. Modell-/Tokenverbrauch UNKNOWN; volle TSK-006-Abnahme offen.

Primärquelle SRC-117: [FOR JSON Datentypkonvertierung](https://learn.microsoft.com/en-us/sql/relational-databases/json/how-for-json-converts-sql-server-data-types-to-json-data-types-sql-server?view=sql-server-ver17),
Abruf 2026-10-13. Sie beschreibt Base64 für Binärtypen; eigene konkrete Record-
und Cleanupqualifikation bleibt davon getrennt.

## C2: beide historische Records kohärent, Gesamt-WARN

Der geänderte Consumer bindet vollständige kanonische Base64-UTF16LE-Markerbytes
und eigene Datei-Namensbytes. Alle anderen Oracles sind zum C1-AST identisch;
Expected und Workflow unverändert. 13 betroffene reine Methoden normal und drei
gezielte Schutzmethoden unter -O bestanden mit Originalkanälen und gehaltenen
Prozessenden. Root schloss den engen Source-/Byte-/Export-/Budgetreview und die
aktuelle Privacy aller zehn geänderten Dateien vor Admission.

Der einmalige C2-Durchlauf endete tatsächlich mit gehaltenem PID/poll0/rc0,
ohne Timeout oder UNKNOWN, in 0,2396s. Zwei Reports versucht und abgeschlossen,
reached_stage=COMPLETE, Errorcode NULL. Beide Originalakten sind COHERENT/WARN:
je vier positive und vier verweigerte DML (Data Manipulation Language; Anweisungen zum Lesen oder Ändern von Daten), acht Kontextrecords, fünf Principal-
Audits, zwei Rechtegegenproben und vollständige 999-Row-Aufnahmen vor/nach.
Originale kombinierte Kanäle bleiben kombiniert. Alle 80 historischen Dateien,
fünf Produktquellen, beide Preparedrecords und Manifest sind vor/nach bytegleich.

Keine neuen SQL-/Container-/Provider-/Modell-/Hostaufrufe. Individuelle Input-/
Client-/Serverrequestenden, volle DMLerror- und Namespacecaptures bleiben
NOT_ESTABLISHED; Caller-/SQLguardflags nur deklariert. Kein neuer Native-/
Runtime-/Minimalrollen-/TP-PERF-PASS. C1-FAIL und verlorene Exceptionfelder bleiben
erhalten. Zwei kumulative Offlineprozesse/vier reservierte Reports verbraucht;
Paket STOPPED_AFTER_C2, keine weitere Auswertung oder Korrektur dieses Pakets.
Aktuelle PR-/Main-Gates, voller Tree, Synchronisierung und eigener Cleanup folgen.
