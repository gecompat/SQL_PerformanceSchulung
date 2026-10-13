# TSK-006: öffentlicher fester IDX-012-Rollenmodus

PR243 ist vollständig geschlossen: 14 Head-/acht Main-Gates, Main
e63cd1fc92cbce3ab85e1b3f146e29d915c6c1c0, vollständiger Tree, synchrones sauberes
Main und eigene lokale/Remote-Branches entfernt. 81 private Dateien sind
hashverifiziert gesichert; der eigene Worktree ist tatsächlich archiviert.
Poolsource Hard6 sowie sämtliche alten UNKNOWN-/FAIL-/Providergrenzen bleiben.

Der [historische IDX-012-Rollennachweis](SQL_SERVER_2025_AI_IDX012_ROLE_REVIEW.md)
belegt zwei begrenzte C3-Lifecycles, hält jedoch die öffentliche Multi-Login-API
offen. Dieser unabhängige Schnitt adressiert diese vorhandene TSK-006-Abnahme.
Keine Wiederaufnahme gestoppter Pool-, VECTOR-, Parser- oder Generationswellen.

## Fester öffentlicher Quellenvertrag

Ein ausdrücklich gewählter Rollenmodus bindet den vorhandenen öffentlichen
IDX-012-Controller an gehaltene eigene Operator-/Adminidentitäten und private
ENV-Credentials. Keine automatische Rechtevergabe, Loginanlage, freie SQL- oder
Executorübergabe für diesen Modus, kein stiller sa-Fallback. Vollständiger eigener
Operatorname und 16-Byte-SID, RunToken, DB-/Ownerbindung und tatsächliche Rechte-
und Kontextrecords bleiben Pflicht. Ältere Engines halten vor Setup an.
Der bestehende Ein-Kontext-Pfad darf durch die neue Auswahl nicht still verändert
werden; fehlende oder widersprüchliche Rollenargumente werden abgewiesen.

Die beiden Kostenphasen bleiben je ein SQLcmd-Prozess und eine Session:
Operator für BEFORE, DML und AFTER; Admin ausschließlich am festen Indexbuild;
danach derselbe Operator. Kein zusätzlicher Client am Build, kein Verlust von
#IDX012CostContext oder Änderung der vorhandenen Session-/DML-/Kostenoracles.
Übrige Phasen authentifizieren direkt als Operator. Ein fest gebundener öffentlicher
Composer übernimmt die belegte Kontextform; kein beliebiger Impersonationsinput.
Fehlender/doppelter Build, fremdes EXECUTE AS/REVERT, zusätzliche Adminarbeit,
falsche SID, fehlende Rückkehr oder Context-/Kosten-/Sourceabweichung werden
abgewiesen. Genau vier geordnete Kontextrecords je Phase, insgesamt acht,
mit tatsächlicher Login-/SID-/OriginalLogin-/Privileg-/Session-/DBbindung.

Vollständige eigene Marker, Source-/DML-/Distanz-/Rebuild-/Restore-/Cleanuporacles
bleiben unverändert erforderlich. Zwei fehlende Rechte müssen vor Setup stoppen;
reine Fixtures sind kein tatsächlicher Rechteentzug. Kein SQL-Principalcleanup
nach unbestätigtem Clientende. Credentials und credentialhaltige Eingaben dürfen
nicht in Logs, Digests, Git oder Kommandoargumente gelangen. Eigene feste
SQL-Eingaben und deren Pfade dürfen nach konkreter Privacyprüfung gebunden
werden; tatsächliche private Rohbelege bleiben außerhalb von Git. Bekannte Prozessenden
ersetzen keine Server-/TDS-Enden. UNKNOWN und unverbrauchte Gates bleiben sichtbar.

Kosten bleiben instrumentierte Gesamtphasen einschließlich Kontextwechsel und
Attestation; Buildzeit enthält den Wrapper. Keine isolierte DDL-/Workerzeit,
absoluten Minimalrollen oder volle Runtime-/TP-PERF-/Demoabnahme behaupten.
Historische private Rollenquellen sind ausschließlich read-only Referenz mit
tatsächlicher Hashbindung; historische PASS-/FAIL-Records werden nicht ergänzt.

## Endlicher Entwicklungsschnitt

Zunächst ausschließlich SOURCE_ONLY: keine Native-, SQL-, Principal-, Provider-,
Container-, Compiler-, Modell-, Download- oder Hosteffekte. Keine Ausführung
historischer Rollenpakete. Der neue unabhängige Quellenumfang erhält höchstens
sechs tatsächlich getestete Quellenkandidaten, verpflichtenden Checkpoint3 und
Hard6; kein Reset. Ein Implementierungsowner; enger unabhängiger Rootreview nur
für neue Credential-/SID-/Kontext-/Session-/Cleanupgrenzen. Nur betroffene reine
Gegenfälle normal/-O; unveränderte alte grüne Suiten nicht lokal wiederholen.
Notwendige neue Fälle in bestehende CI-Prozesse integrieren, Runtime-/Default-
RED-Selektion nicht erweitern. Tatsächliche Testenden, Input-/Sourcebindungen
und sichere Rawkanäle privat erhalten; Modell-/Tokenverbrauch UNKNOWN.

Quellenabschluss umfasst Privacy, relevante Tests, PR, aktuelle Head-/Main-Gates,
vollständige Übernahme nach origin/main, FF-Synchronisierung, eigene Branches,
private Belegsicherung und tatsächliche Worktreearchivierung. Ein späterer neuer
eigener Nativenachweis braucht erst einen konkret geprüften Ausführungsvertrag
und aktuelle Admission; dieser Quellenschnitt erteilt sie nicht. Danach folgt
der nächste zulässige offene Schritt im kanonischen Workstream.

## Tatsächlicher Quellencheckpoint und begrenzte Cleanupkorrektur

Aktueller Quellenstand: Labels Source1–4, insgesamt fünf tatsächlich geprüfte
Zustände einschließlich initialem Syntaxpreflight-FAIL mit abweichenden Bytes.
Die Zählung wurde korrigiert; Rootcheckpoint3 wurde tatsächlich nach vier
Zuständen und vor dem fünften geschlossen, ohne rückwirkenden Rechtzeitigkeitsclaim.
Vorherige 18 reine Methodeninvokationen/ sechs gehaltene Pythonprozesse bleiben
unverändert. Source4 schließt den konkreten Cleanup-UNKNOWN-Rückgabeverlust mit
nur einem neuen vollständigen Controllergegenfall normal und unter `-O`:
beide bestanden, insgesamt 20 Invokationen/acht gehaltene Prozesse. UNKNOWN im
Restore liefert FAIL_CLEANUP und NOT_ESTABLISHED mit vollständigen sicheren
Captures/zurückgehaltenen Inputs zurück; kein weiterer Recovery-SQLclient.
Vor der CI-Imagekorrektur waren fünf von sechs Quellenständen verbraucht; einer verblieb. Root hat Source4/overall5 semantisch und mechanisch abgeschlossen;
CLEANUP_UNKNOWN_RESULT_LOST ist geschlossen. Der Quellenstand wird über PR
integriert; Native-/Server-/TDS-Abnahme bleibt offen, Domainaufrufe bleiben null.

Die ursprünglichen Labels, Syntax-FAIL-Bytes, Rawkanäle und Rootcheckpoint3 bleiben privat bytegleich erhalten. Bei der Archivierung trat zunächst ein Windows-Pfadlängenfehler vor Produktänderungen auf; die Kopie wurde anschließend über eigene ExtendedPaths bytegleich vervollständigt, ohne Domainaufrufe. Runtime-/Server-/TDS-Abnahme bleibt NOT_ESTABLISHED.

Der unabhängige Rootreview hat die vollständige Rückgabe nach Cleanup-UNKNOWN,
beide neuen gehaltenen Pureenden, aktuelle Quellen-/Raw-/Privacybindungen sowie
die CI-Auswahl derselben Methode unter `-O` geprüft. Keine offene semantische
oder mechanische Source4-Finding; der tatsächliche Checkpoint wurde nach vier
geprüften Zuständen geschlossen. Diese Abschlussprosa ändert ausschließlich
die vier kanonischen Dokumente. Der ausgeführte Source4-Code, Test und Workflow
sowie ursprünglicher Freeze/Rootcheckpoint bleiben unverändert gebunden.

## Tatsächlicher CI-Image-Drift und sechster Quellenstand

Der erste PR244-Headlauf blieb tatsächlich FAIL: Der SQL2025-Kostenconsumer
verwarf SKIP_CONFIGURATION; die vier vorangehenden DGN-010-Lifecycles hatten
bereits SKIP_CONFIGURATION mit bestätigtem Cleanup geliefert. Der ursprüngliche
CI-Namespacecleanup bestand. Die Logdigests belegen, dass `2025-latest` gegenüber
dem erfolgreichen Mainlauf38415812533 ein anderes Image auflöste: vorher
`sha256:2b5b581621126574f3d1f75e78d3eebe8d05aedb59ad0cfdf9aa42cb0634d726`,
im fehlgeschlagenen Headlauf38427774683 dagegen
`sha256:742481d1b1186cccc81220a1eaacef244ca8d0f7d19c8e5c70df8ae541ffbab2`.
Image-Drift ist belegt; die tatsächliche neue Build-/Editionabweichung ist
UNPROVEN, weil der SKIP keine abweichenden Werte ausgibt.

Der sechste und letzte Quellenstand CI_IMAGE_INPUT_CORRECTION pinnt nur den
SQL2025-Matrixeintrag auf den tatsächlich erfolgreichen RegistryDigest.
2019/2022, Laufskripte, Testoracles und Rollenproduktbytes bleiben unverändert;
keine SKIP- oder FAIL-Umdeutung und kein unveränderter CI-Rerun. Source4-Freeze,
Rootreview, 20 Methodeninvokationen/acht gehaltene Testprozesse sowie die beiden
Original-CI-Logs bleiben erhalten. Keine lokale Purewiederholung oder neue
Domainaufrufe. Jetzt sechs von sechs Quellenständen/Hard6, kein Reset oder
Source7. Die neue geänderte CI-Eingabe erhält aktuelle Head-/Main-Gates vor
Integration; PR244 bleibt bis dahin ungemergt. Öffentliche Rollenruntime und
vollständige Demo-/Server-/TDS-/TP-PERF-Abnahme bleiben NOT_ESTABLISHED.
