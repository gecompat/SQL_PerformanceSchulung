# CON-010: eigenes opt-in RED-Poolprofil

Status: NATIVE_PARTIAL_UNKNOWN_STOP. Der neue Producer ist teilweise ausgeführt;
eine vollständige native Poolqualifikation ist NOT_ESTABLISHED. Das bestehende GREEN-/LOCAL-Manifest, V1/private42 und Default-CI
führen ihn nicht aus. Kein allgemeiner Provider-, Passwort-, Seitenkanal-,
Performance-, TSK-009-, CON-010- oder TP-CON-Abnahmeclaim.

## Wirkungsgrenze

Nur ein ausdrücklich zugelassener neuer eigener Wegwerfcontainer je Kandidat:
SQL17.0.5005.3, vorhandenes Image mit voller ID
`78eb6a93ef20501bd754282cc216188a0acee1cfa6119c33eef0b21599c1f726`,
vier CPUs/sechs GiB, eigener zufälliger Loopbackport, keine Mounts oder fremden
Namespaces. Kein Download, kein Hosttrustwechsel, keine Cloud-/ONNX-/Modellroute.
CREATE/DROP LOGIN ist instanzweites RED-DDL innerhalb genau dieses Containers.
Drei neue Logins mit vorher festgelegten verschiedenen 16-Byte-SIDs; ausschließlich
CONNECT SQL und die beiden eigenen DBrechte CONNECT/Objekt-SELECT. Zwei
synthetische Rows mit VECTOR(3), feste RLS-/Quellen- und volle Principalmetadaten.
PASSWORD_HASH bleibt NOT_CAPTURED und ist kein Integritätsoracle.

Windows mit den bereits vorhandenen SHA-gebundenen PowerShell-/SqlClientdateien
ist Voraussetzung. Fehlende Fähigkeit ergibt SKIP vor Wirkungen; kein Install
oder Fallback. Dateien/SHAs werden geprüft, eine DLL-Datei allein attestiert
keinen erfolgreichen Transport. Das native Profil muss diesen tatsächlich zeigen.
Die Assembly ist nur dieser begrenzte Caller, keine Providerempfehlung.

`SQLPERF_LAB_CON010_POOLPUBLIC` ist fest; vier vollständige Unicode-/Längen-/
Klassen-/Typ-/Byte-Marker binden Projekt SQL_PerformanceSchulung, Contract1.0,
Demo CON-010 und RunToken POOLPUBLIC. Der separate 16-stellige Inputtoken ist
keine Umdeutung des Framework-RunTokens. DB-/Login-/SID-Abwesenheit vor Setup,
keine Namensadoption und volle gehaltene Leases vor Drop sind Pflicht.

## Ausführbarer Einstieg nach Rootadmission

Root registriert vor jeder lokalen Admission die tatsächlichen Source-/Review-/
Budget-/Canonicalbytes unter Runtime/AI_POOL_PUBLIC; sechs geänderte relevante
Kandidaten, höchstens ein serieller Container je Kandidat, Checkpoint3/hard6.
Ein bekannter früherer FAIL und tatsächlich geschlossener Namespace sind für
Retry Pflicht. UNKNOWN oder ungeklärte Inputs sperren weitere Admissions.
Diese Dateien sind explizite lokale Autorität; eine Callerboolean allein ist
kein unabhängiger Sicherheitsnachweis.

```powershell
python Demos/09_AI_SQL_Server_2025/CON-010_Tenant_Isolation/run_pool_profile.py --source-manifest
# Erst nach vollständig geschlossenen Vorgänger-/Source-/Reviewgates:
python Demos/09_AI_SQL_Server_2025/CON-010_Tenant_Isolation/run_pool_profile.py --allow-red --confirm-isolated-lab --candidate 1
```

Der erste Befehl liest nur die feste öffentliche Quellenkarte. Der zweite ist
absichtlich vom normalen Manifestaufruf getrennt. Ohne konkrete Rootadmission
oder RED-/Labbestätigung startet kein Profileinsatz.

## Ergebnis und Cleanup

Sechs authentifizierte Checkouts A/B/U/A/B/U in drei eigenen Pools, je Lane
stabile SqlCredentialinstanz und readonly SecureString aus privater ENV. Keine
Passwörter im ConnectionString, argv oder öffentlichen Output. A/B lesen ihre
vollständige eigene Quelle, U authentifiziert sich und liest null Rows.
CON010_TenantId wird absichtlich gespooft; die erste Abfrage nach Recheckout
muss bereits zurückgesetzt sein, bevor eine explizite Reparatur erfolgt.

Jeder Open-/Scalar-/Close-Return bekommt einen tatsächlichen einzelnen Record;
57 geordnete Operationen. Scalartext-SHAs binden ausschließlich die tatsächlichen
festen öffentlichen PowerShell-SQLtextformen. ClientConnectionId wird erfasst,
seine Gleichheit ist kein Oracle. Physische Wiederverwendung erfordert gehaltene
Owner-DMVconnection_id/connect_time plus volle Identität/SID/DB/ApplicationName/
Nonce; zwischen Lanes verschiedene physische IDs. APIreturns und Childprozessende
sind getrennte Grenzen und keine unabhängige TDSattestierung.

V2-SQLcmdcapturing verwendet bestehende öffentliche APIs und exakt LF/CRLF-
gebundene Collectorquellen. Inputbytes werden vor ENV-Expansion erfasst;
Outputbytes sind vom Collector dekodiert und erneut UTF-8-kodiert. Der eigene
PowerShell-Child wird ausdrücklich nicht als SQLcmd-Capture umdeklariert.
Privacy vor jedem Digest/Callerreturn umfasst Klartext, UTF-8-/UTF-16-Hex und
vollständig dekodierte gebundene Outerframes/innere Hexfelder. Inspect fragt
nur FullCID/Image/Owner/Mounts/Ports/CPU/RAM ab, niemals Config.Env.

300s absolute Normaluhr und einmal60s Cleanup ab vor Child, kein Reset. 40s ist
höchstens ein Phasenendpunkt: 26 konfigurierte Collector-Nachlaufsekunden zählen
innerhalb dieses Fensters. Konkrete eigene Namespacecaps sind Lookup3/Inspect3/
Remove8/CID3/Name3=20s; OS-/Schedulingoverhead ist keine Wallclockgarantie.
Popenzeit verbraucht denselben primären Wait. Zu wenig Restbudget sperrt den
Client, statt die Uhr zu verlängern. Tatsächliche Deadlineüberschreitung,
Timeout, Signal, Rc/Poll-Inkohärenz, inneres UNKNOWN oder unklarer Childpoll
sperren jedes folgende SQL, auch SQLcleanup. Nur vollständig gebundener eigener
Namespaceabbau bleibt dann zulässig; er ist kein SQLdrop-/SQLabsence-PASS.

Eigene ClearPool-Referenzen bleiben bis Close und neuer physischer Abwesenheit
gehalten; erst danach Dispose. Neue Owner-Abwesenheitsquery und volle State-
kontinuität sind Pflicht. Gehaltene Login-Drops erfolgen vor dem markergebundenen
DB-Drop, anschließend frische SQL- und vollständige CID-/Namens-/Inputabwesenheit.
Fehlendes Leasing erlaubt keine Adoption. Der Caller erhält privat vollständige
sichere Originalinput-/Kanal-/Capture-/Negativ-/Restore-/Closurewitnesses auch bei
FAIL; die CLI persistiert nichts davon und exportiert nur Status/Counts.
Bekannte semantische Fehler und UNKNOWN werden getrennt; ursprünglicher Fehler,
SQLcleanup- und Namespacecleanupfehler bleiben separat sichtbar.

Ein positives begrenztes Ergebnis bleibt WARN mit record_validation PASS;
Runtimegeneralisation und TP-CON bleiben NOT_ESTABLISHED. Quellen-/Marker-/
HeldSID-Negativen sind tatsächliche Owner-Kontrollen; ihre begrenzte Ausführung
belegt keine authentifizierten Poolcheckouts.
Reine Tests verwenden Fakehandles und synthetische Records und ersetzen keine
Nativequalifikation, keinen echten Pooltransport oder Providerprobe.


## Abgeschlossener erster Nativeversuch der öffentlichen Welle

Die Sourceimplementierung bleibt SOURCE_PREPARATION_ONLY; Runtimequalification
ist NOT_ESTABLISHED. C1 scheiterte vor Create/SQL an fehlendem APPDATA in der
Podman-ENV. Read-only Diagnose belegte APPDATA als notwendige Konfigurationswurzel;
SQLclient-ENV blieb unverändert. C2 erzeugte einen eigenen Container, erreichte
aber wegen Podman-Feldcase .Id statt .ID keine SQL-/Poolphase. Container-Inspect
und alle ps-Abfragen verwenden künftig .ID, ps zusätzlich --no-trunc; die bereits
funktionierende Image-Inspect-Form .Id bleibt bestehen.

Der unabhängige Root-Recoveryversuch mit vollständig gebundener eigener CID
überschritt den 8s-Remove-Cap. Podman rm --help belegt 10s Standardwartezeit und
die unterstützte Option --time=0; diese setzt der neue Sourcecode bei unverändertem
8s-Cap. Der unbestätigte frühere Remove bleibt UNKNOWN. Nachfolgende ausschließlich
read-only CID-/Namensabfragen und Inputprüfung belegten ResourceABSENT, niemals
RequestEnd oder SQLcleanup-PASS. Kein zweiter Remove, kein Folge-SQL und keine
Uhrverlängerung. C1/C2-FAILs bleiben unverändert; die Welle ist STOPPED_NO_C3_AFTER_UNKNOWN.
In dieser ersten Welle wurde der korrigierte Sourcecode nicht nativ ausgeführt. Eine bestehende UNKNOWN-
Wellenakte blockiert weitere Nativeadmission; es gibt kein Recovery-Supplement
als C3-Zulassung. Öffentliche Pool-Runtime-/TP-CON-Abnahme bleibt offen.

## Getrennte neue Qualifikationsgrundlage

Eine neue Welle ist ausdrücklich mit `--wave requalification` auswählbar.
Sie verwendet einen eigenen festen Controlbereich `Runtime/AI_POOL_REQUALIFICATION`
und verlangt gebundene Input-, History-, Quellen-, Budget- und Rootreviewdateien.
Die gewöhnliche Auswahl und ihre alte UNKNOWN-Sperre bleiben bestehen. Ein leeres
Controlverzeichnis oder eine umbenannte alte Akte genügt nicht. Die neue Auswahl
endete nach einer begrenzten Teilausführung bei UNKNOWN; eine vollständige
Poolqualifikation ist weiterhin NOT_ESTABLISHED.

Die unveränderten PR226-Originale, ihr Resourceabschluss und das unbestätigte
Remove-Ende bleiben read-only gebunden. Zwei alte Nativeversuche/ein Container,
SQL0/Poolchild0 zählen weiter: höchstens vier zusätzliche Versuche/Container,
insgesamt sechs Versuche/fünf Container. Vor dem zweiten neuen Versuch muss der
tatsächliche Gesamtcheckpoint3 geschlossen sein. PASS oder neues UNKNOWN stoppt;
ein weiterer bekannter FAIL verlangt relevante geänderte Quellen und neue Zulassung.
Keine Aktionen gegen die alten Ressourcen, kein C3 der gestoppten alten Welle.

Neue Namespacecalls halten dasselbe eigene Prozessobjekt bis zum tatsächlichen
PID/poll/rc-Endrecord. Initiales Warten und einmaliges Reaping teilen denselben
absoluten Cap und das verbleibende Profilbudget. Timeout/Signal/unklares Ende
bleiben bereits vor Privacy- oder Capturefehlern UNKNOWN; zweiter Remove und
Folge-SQL sind dann gesperrt. Sourcepins vor/nach und sichere tatsächliche Kanäle
werden privat erhalten. Alte `SUBPROCESS_RUN_RETURNED`-Records werden nicht
nachträglich zu individuell gehaltenen Endbelegen umgedeutet.

Provider-/Lab-/RED-Zulassung sowie alle fachlichen Eigentums-, Rollen-, State-,
Reset- und Cleanupgates bleiben erforderlich. Die Rootdateien deklarieren eine
eng freigegebene lokale Welle, kein allgemeines Attestierungs- oder Rechte-System.
GREEN/LOCAL und Default-CI starten diesen RED-Pfad nicht.

## Was die aktuelle Teilausführung zeigt

Die getrennte [Poolqualifikationswelle](../Project_Planning/SQL_SERVER_2025_AI_POOL_REQUALIFICATION_REVIEW.md)
endet mit UNKNOWN_STOP. Der erste neue Versuch scheiterte an der erfassten
Setupkanalreihenfolge; eine gezielte Korrektur akzeptiert nun die beiden bekannten
Erfolgsmarker und genau die bekannte separate Kontextmeldung, keine beliebigen
Diagnosen. Im zweiten Versuch sind Setup, Logins, Baseline und sechs tatsächliche
Owner-Abweisungen für Quelle, gehaltene SID und vier Eigentumsmarker samt Restores
belegt. Fünf vollständige Zustandsvergleiche sichern diese Ownerkontrollen.

Für die sechs authentifizierten A/B/U-Checkouts, einzelne .NET-Enden und physische
Poolreuse fehlt ein vollständiger Childnachweis. Die ursprüngliche Ursache ist
unbewiesen. Ein bekannter eigener Prozessabschluss hebt inneres UNKNOWN nicht auf.
Nach UNKNOWN wurde kein weiteres SQL ausgeführt. Der eigene Container ist nach
einem gebundenen Remove und frischen CID-/Namensabfragen abwesend; SQLcleanup ist
NOT_ESTABLISHED, ein Childplan bleibt privat erhalten. Deshalb ist die Welle
gestoppt und liefert keinen vollständigen Pool-Runtime- oder TP-CON-PASS.

Diese Dokumentergänzung beschreibt vorhandene Belege. Ursprüngliche Source- und
Ausführungspins bleiben unverändert; die bisherigen Zustände werden nicht erneut
ausgeführt. Der aktuelle Quellenstand erhält einen separaten Childtransport vor der
Ergebniszuordnung. Er enthält tatsächlich beobachtete Prozessmetadaten und
sichere getrennte Ausgabekanäle auch bei einem ungültigen Receipt. Unbeobachtete
Werte bleiben null. Credentialausgaben werden vor Rawdaten und Digests abgewiesen;
nur sichere Metadaten und feste Fehlercodes bleiben erhalten. Ein bekanntes
Prozessende belegt weder einzelne .NET-Enden noch das Server-/TDS-Ende. Die
geprüften 57 API-Records bleiben ein eigener Nachweis. Diese Änderung ist rein
mit synthetischen Fakehandles geprüft; sie erklärt oder qualifiziert die
gestoppte Teilausführung nicht nachträglich.
