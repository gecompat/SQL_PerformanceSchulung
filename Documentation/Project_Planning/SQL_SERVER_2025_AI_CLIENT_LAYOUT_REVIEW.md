# TSK-004: reiner Vertrag für das erhaltene Clientlayout

PR230 vollständig geschlossen: elf erfolgreiche Head-Gates und ein bewusster
Runtime-SKIP, acht erfolgreiche Main-Workflows mit erneut bestätigtem Runtime-
SKIP, Main 9d731f55a18ec99cd4967033af62876cea3ed657, vollständiger Tree,
FF-Synchronisierung und eigene lokale/Remote-Branches entfernt. 121 private
Dateien einschließlich aller finalen öffentlichen Quelldateibytes wurden vor
der tatsächlichen Worktreearchivierung hashverifiziert gesichert.
Der [ANN-Recordvertrag](SQL_SERVER_2025_AI_IDX012_RECORD_CONTRACT_REVIEW.md)
bleibt COHERENT/WARN mit ausdrücklich fehlenden Captures; Replaypaket gestoppt.

## Unabhängige Sourcefrage

Die [native VECTOR-Welle](SQL_SERVER_2025_AI_VECTOR_NATIVE_REVIEW.md) bleibt
FAIL_HARD6_UNKNOWN; sie wird nicht wieder aufgenommen. Ihr C6-Catch enthält
FileNotFoundException ohne Dateiname oder Auflösungsursache. Eine rein statische
Einsicht der gesicherten Deps-/Compiler-/Appbytes findet eine Layoutabweichung:
28 Runtimeassets wurden flach nach app kopiert, während fünf ausgewählte
Windows-runtimeTargets in der unveränderten Depsdatei Unterpfade nennen.
Die fünf DLLs sind mit den vorhandenen SHA-Pins unter ihrem Basename vorhanden;
die relativen Unterpfade fehlen. Dies belegt eine Layoutabweichung, keinen
tatsächlichen .NET-Auflösungsfehler oder konkreten Ursprung der C6-Exception.

Der kleine öffentliche Vertrag prüft ausschließlich diesen erhaltenen Graphen:
gewählte RID-/Frameworkassets, vollständige relative Pfade, Basenamekollisionen
und tatsächliche SHAs. Eine synthetische Fixture und fokussierte Gegenfälle
trennen erwartete Pfadstruktur, Bestandskohärenz und weiterhin unbekannte
Runtimeauflösung. Die HowTo erklärt Anwender:innen, weshalb ein vorhandener
Dateiname allein den Dependencyvertrag noch nicht beantwortet. Keine DLL-
Übernahme oder Weitergabe im Repository; Lizenz-/Auditgrenzen aus SRC-116 bleiben.

## Endlicher Umfang und Gates

Ein Implementer, enger Rootreview für Pfad-/RID-/Hash-/Kollisionsbindung,
Datenschutz und Claimgrenzen; keine Reviewkette. Sechs relevante Sourcekandidaten,
Checkpoint3/hard6. Null neue dotnet-, Assemblyload-, Provider-, SQL-, Container-,
Modell-, Download- oder Hostaufrufe. Nach aktueller Source-/Test-/Expected-/
Rootadmission höchstens eine reine historische Bestandsauswertung; kein
unveränderter Retry. Native-/Loaderprobe wäre ein getrennt zu begrenzender
Folgeschnitt mit konkreter sicherer Fehlermetadatenaufnahme, kein impliziter Effekt.

Im bestehenden KI-Workflow nur neue statische Trigger und gezielte Tests;
Runtimebody und Selector unverändert, keine neue Matrix oder neue Jobs.
Aktuelle Privacy, Projekt-/Head-/Main-Gates und vollständige Tree-/FF-/Branch-/
Worktreeclosure bleiben erforderlich. Keine unveränderte Wiederholung der
alten Runtime-/Dependency-/ANNtests oder Vollanalyse.

## C1-FAIL und konkreter Sourcefolgeentscheid

Die einmalige Root-admittierte Bestandsauswertung endete mit FAIL_OFFLINE_LAYOUT:
PID (Process Identifier; Prozesskennung) 36800, final poll/Returncode 1, 0,199760 Sekunden, kein Timeout und kein
UNKNOWN. Ein Report wurde versucht, keiner abgeschlossen; Fehlercode
FIXED_PACKAGE_ASSET_SCHEMA. Alle 31 Appdateien, Compilerproof, Preparedmetadaten,
Manifest und Admission sind vor/nach identisch. Es gab keine Nativeaufrufe.

Eine anschließende rein lesende Quellenprüfung findet im ursprünglichen
SqlClient-6.1.4-Paket einen `resources`-Abschnitt mit 13 Localeeinträgen.
Die bisherige Handfixture und der Consumer hatten diesen Abschnitt nicht
abgebildet. Das ist ein Schemafehler des Prüfvertrags, kein neuer Loaderbefund.
Originaler FAIL, Rawkanäle, Quellen und Gates werden vor jeder Korrektur gesichert.

Innerhalb der bereits autorisierten sechs Sourcekandidaten folgt C2: ausschließlich
den tatsächlichen Ressourcenabschnitt explizit mit festen Pfaden und Locales
validieren, von den 28 ausgewählten Runtimeassets getrennt halten und passende
synthetische Negativkontrollen ergänzen. Keine Lockerung der bisherigen
Pfad-/RID-/Hash-/Kollisions- oder Claimgrenzen. Nach geänderten Tests und enger
Rootadmission höchstens eine neue reine Bestandsauswertung; kumulativ zwei
Prozesse und zwei Reportversuche einschließlich C1, jeweils höchstens 60 Sekunden.
Danach hält dieses Auswertungspaket unabhängig vom Ergebnis an. Das ursprüngliche
Einzelbudget wird damit sichtbar erweitert; kein unveränderter Retry oder
stilles Zurücksetzen. Laufzeitbudget bleibt null.

## C2 abgeschlossen: Sourcekohärenz mit WARN

Der geänderte Vertrag prüft genau 13 Ressourcenpfade und ihre Locales; deren
Dateibestand und Ladefähigkeit werden nicht attestiert. Zwei neue Methoden
liefen normal und optimiert erfolgreich (PID 63960/56412, bekannte Enden und
Rawkanäle). Die unveränderte Zwölfersuite wurde lokal nicht erneut ausgeführt.
Der unabhängige Rootreview bestätigt den engen Ressourcenunterschied und alle
bisherigen Grenzen. Der bestehende Workflow erhält nur drei statische Trigger
je Event und zwei Pythonprozesse; Runtimebody und Selector bleiben unverändert.
CI (Continuous Integration; automatisierte Integrationsprüfungen) führt 14 normale und vier geschützte Methoden aus. Modellverbrauch ist unbekannt.

Die tatsächlich Root-admittierte zweite und letzte Bestandsauswertung endete
bekannt: PID 62428, final poll/Returncode 0, 0,141996 Sekunden, kein Timeout und
kein UNKNOWN. Ein Report abgeschlossen, Status SOURCE_COHERENT_OVERALL_WARN,
record_validation COHERENT. 27 Pakete, 28 hashgebundene Runtimeassets und
31 Appdateien; fünf wörtliche runtimeTargets-Unterpfade fehlen, die entsprechenden
flachen DLLs sind vorhanden. Originale, Preparedmetadaten, Manifest, Admission
und alle 51 gesicherten C1-Dateien sind unverändert. Result-SHA256:
`9a31b994f725741ee3f6393094eb613ec108f39de1c48127706318a33193c80d`.
Das Paket ist STOPPED_AFTER_C2. C1-FAIL und seine Quellen bleiben erhalten;
beide Auswertungen zusammen erzeugten null Native-, SQL- oder Modellaufrufe.

Aktuell SOURCE_COHERENT_OVERALL_WARN_STOPPED_AFTER_C2. FileNotFound-Ursprung UNPROVEN, Assembly-/
Typ-/TDS-/SQL-/Provider-/Performance-/TSK-004-Abnahme NOT_ESTABLISHED;
Modell-/Tokenverbrauch UNKNOWN. Allgemeine Entwicklung und andere Workstreams
bleiben unberührt; Cloud-/ONNX-/rote Hostgrenzen gelten unverändert.
