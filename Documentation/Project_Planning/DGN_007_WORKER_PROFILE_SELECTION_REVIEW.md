# DGN-007 – quellenbegründete Auswahl frischer Workerprofile

## Auftrag und gemeinsamer Rahmen

DGN-007 bezeichnet die Diagnose-Demo mit getrenntem Quellen- und Laufnachweis.
Der [Auswahlplan aus PR282](DGN_007_WORKER_PROFILE_SELECTION_PLAN.md) ist in
`e4b373d679ef2f8670913239664e55623cf7caaa` vollständig integriert. Sieben grüne
Prüfungen des PR-Stands, drei der Main-Basis und fünf frische Main-Prüfungen,
unabhängiger Review, vollständige Baumübernahme, Synchronisation und eigene
Branchbereinigung sind im [PR282-Abschlussnachweis](https://github.com/gecompat/SQL_PerformanceSchulung/pull/282)
gebunden. Der kontinuierliche menschliche Auftrag führt jetzt zum konkreten
privaten Auswahlpaket für genau eine vorhandene Linux-Installation von CPython
3.12 und drei vollständige Workerdeklarationen.

Ein Implementierungsverantwortlicher root und derselbe unabhängige Reviewer
führen den Schnitt. Gemeinsame Einheit sind stabile Paket-/Quellen-Teststände:
Checkpoint nach dem ersten, harte Grenze vier einschließlich Rootarbeit,
Reviews, Korrekturen, lokaler Prüfungen, Koordination und vollständigem
Integrationsabschluss. Verbrauch UNKNOWN, nicht verlässlich gemessen. Ein alter
Runnerkandidat oder der historische native Metadatenversuch wird nicht unter
neuem Namen wiederholt. Quellenroute, Originalbytes und Größenlimits bleiben
unverändert. Eigener Branch: `codex/dgn007-worker-profile-selection`.

Das Paket wählt S15 (15 skalare Installationsfelder) und P11 (elf Felder je Modul,
etwa Name, Herkunft und Loader) vollständig vor. Ein Loader ist die zum Laden
eines Moduls gebundene Instanz. Private Locator, vollständige Werte, Rohdaten und
Quellenpins bleiben unversioniert; diese Dokumentation beschreibt Methode,
Prüfstatus und Grenzen.

## Ergebnis: Paketlauf am falschen Prüfinterpreter gestoppt

Der unabhängig freigegebene vierte Stand wurde genau einmal unter Windows mit
CPython 3.14.7 aufgerufen. Er brach bei `INPUT_PREPARATION` ab. Eine anschließende
rein lesende Diagnose mit dem bestehenden Eingangsprüfer meldete
`BOOTSTRAP_CHANGED`, obwohl die Git-Rohbytes vollständig übereinstimmten.
Der [Vertrag des statischen Eingangsprüfers](DGN_007_EXECUTION_EDGE_VERIFIER.md)
verlangt ausdrücklich Python 3.12 für die eingefrorenen Ganzdatei-AST-Hashes
(AST: Abstract Syntax Tree; abstrakter Syntaxbaum). Der Windows-Pakethelfer
hatte diese Interpretervoraussetzung nicht abgesichert. Das ist ein Fehler der
gewählten Prüfumgebung, kein nachgewiesener Bootstrap-Quellenwechsel.

Die rein lesende Ursachenprüfung reproduzierte für beide betroffenen
Bootstrapgruppen die gespeicherten Hashes ausschließlich mit
`ast.dump(show_empty=True)`; die Standardausgabe unter 3.14 wich ab. Die
[Python-Dokumentation zu ast.dump](https://docs.python.org/3.14/library/ast.html#ast.dump)
erläutert die inzwischen standardmäßig ausgelassenen optionalen leeren Listen.
Diese Übereinstimmung erklärt den konkreten Befund; sie ersetzt weder den
vorgeschriebenen 3.12-Prüfer noch belegt sie allgemeine AST-Gleichwertigkeit
zwischen Pythonversionen. Kein Hash, Prüfer oder AST-Verhalten wurde verändert;
kein erneuter Paketlauf.

Erreicht wurden die vier erfolgreichen Tabellenlesertests, der eine statische
Binärread und im Paketlauf eine negative Kontrollbyte-Pinprobe. Die übrigen
36 geplanten negativen Fälle, sämtliche Form-/Größenprüfungen und alle drei
Ganz-AST-/Fitmethoden wurden nicht ausgeführt. Die 27 eigenen Git-Rohdateien
bleiben als Partialartefakte erhalten. Kein fertiger Paketbericht und keine der
drei Worker-Scriptdateien entstanden. Es gibt keinen Paket-PASS und keine
native Ausführung.

Vier von hart vier Quellen-/Testständen sind verbraucht, Verbrauch UNKNOWN.
Der sichere Abschluss umfasst Diagnose, unabhängigen Befundreview und deren
Dokumentationsintegration. Das Auswahlpaket selbst bleibt unvollständig.
Kein fünfter Stand, Wiederholungsversuch oder Scopewechsel ohne ausdrückliche
begrenzte Erweiterung.

## Statische Tabellenfrage vor der Paketerzeugung

Die historische 85-Modul-Auswahl liefert nur Hinweise für Namen und Locator.
Sie ist keine neue Sollbaseline und wird vom neuen Pakethelfer nicht geladen.
Aktuelle Installations- und Bibliotheksdateien werden ausschließlich lesend
geprüft. Es gibt keinen Linux-/WSL-Aufruf (WSL: Windows Subsystem for Linux;
Linux-Umgebung unter Windows), keinen Probe- oder Workerstart.

Die offene Tabellenfrage wird mit einem begrenzten Windows-Helfer für ELF
(Executable and Linkable Format; Format der gewählten Linux-Executable)
beantwortet. Er unterstützt ausschließlich das geprüfte 64-Bit-Profil mit
kleiner Byteordnung und fester Executableform. Größengrenzen, eindeutige dateigedeckte
Adressbereiche, Symbolformen, Namen und endliche Tabellen mit Abschlussmarken
werden vor einer Rückgabe geprüft. Höchstens 16 MiB Bilddaten; keine Ausführung
oder Rekonstruktion von Pythoncode aus dem Binary.

Die Tabellenformen folgen den CPython-3.12.3-Primärquellen
[Importstrukturen](https://raw.githubusercontent.com/python/cpython/v3.12.3/Include/cpython/import.h)
und [Frozen-Tabellen](https://raw.githubusercontent.com/python/cpython/v3.12.3/Python/frozen.c),
gelesen am 21. Oktober 2026. Tabellenmitgliedschaft wird ausdrücklich von
aktivierter Frozen-Verfügbarkeit, tatsächlicher Cachemitgliedschaft und
ausgeführten Bytes getrennt.

Zwei eingefrorene Helferstände: Vor Ausführung wurde die explizite lokale
Importauflösung des isolierten Testharness ergänzt. Die unabhängige Prüfung
schloss priorisierte Befunde und erlaubte gestuft zunächst vier synthetische
Gegenproben, anschließend genau einen Read des separat gepinnten Byteobjekts.
Die vier Methoden bestanden ohne Fehler oder Skip. Erst danach erfolgte der
begrenzte Read mit exakter Längen- und Hashprüfung desselben Byteobjekts.
Ergebnis ausschließlich statisch: 60 Builtin-, drei Bootstrap-Frozen- und
15 weitere Frozen-Tabelleneinträge. Kein Wiederholungslauf.

## Paketprüfung und gebündelte Korrektur

Der dritte eingefrorene Quellen-/Teststand wurde unabhängig vor Ausführung mit
drei Befunden abgelehnt: vollständige Quellenpins vor Projektimport fehlten,
die Runnerroute wurde fälschlich auch für Proxy und Harness gewählt, und die
Gegenproben erfassten noch keine veränderten Kontrollbytes oder Form-/Bytegrenzen.
Kein Lauf oder Generierungsversuch dieses Standes. Der vierte Stand bündelt
diese Korrekturen. Seine unabhängige Delta-Prüfung schloss die drei Befunde und
erteilte genau ein Lauf-GO (Freigabe für den geprüften Windows-Aufruf). Der
freigegebene Lauf scheiterte anschließend wie oben beschrieben. Vier/hartvier
Stände, Verbrauch UNKNOWN; kein weiterer Stand unter einem neuen Namen.

Der Entwurf liest feste Installationsmember bis gemeinsam 32 MiB, bindet die
statischen Tabellen an dasselbe gepinnte Executablebild und prüft die konkrete
Sysconfig-Datenquelle. Paketmetadaten begründen eine deklarierte Version;
sie werden nicht als gemessene Runtimeversion ausgegeben. Die vollständige
85-Namen-Folge wird getrennt vorgewählt und gegen aktuelle Quellen begründet.
Weder ein beobachteter Cache noch ein erfolgreicher Bericht wird zum Soll.
Ein separat eingefrorenes Manifest bindet alle 21 lokalen Generator-/Codec-/
Oracle-/Fixturequellen an die Base und ihre tatsächlichen Arbeitsdateibytes
vor dem ersten Projektimport. Diese Quellenpinprüfung hat eine eigene
4-MiB-Grenze und wird vor Artefaktschreiben nochmals abgeschlossen.

Alle drei Workerdeklarationen verwenden dieselbe Installation, aber getrennte
Ordinal-/Einstiegs-/Kontrollkontexte und vorgewählte Scriptlocator. Die beiden
Kontrollrollen und fünf direkten Scriptimporte bleiben erhalten. Die bekannte
FileFinder-Hookbindung folgt der geprüften Kontroll-/Importlibquelle; daraus
folgt kein Nachweis eines tatsächlich gehaltenen Workerhooks.

Das geplante Verfahren kopiert exakt die 27 gebundenen Gitmember in ein neues
eigenes privates Ziel und verwendet den bestehenden statischen Bundle-/
Eingangsprüfer. Kein Kandidatenbody wird importiert oder ausgeführt. Pro Worker
werden sämtliche fünf Formen und ihr gemeinsames 65536-Byte-Limit vor
Encoderfreigabe geprüft; geplante Gegenproben prüfen fehlende/zusätzliche
Module, Versions-/Kontextabweichung, falsche Origins, Loadernamen, Aliase und
unvollständige Felder. Hinzu kommen geänderte aktuelle Kontrollbytes gegen den
eingefrorenen Pin, unvollständige Formsets, die Einzel- und Gesamtbytegrenzen
sowie semantisch gültige synthetische Langlocator-Auswahlen mit Größenoverflow
und Encoderablehnung. Geplant sind insgesamt 37 negative Datenfälle;
Langlocator-Auswahlen werden ausschließlich im Speicher verwendet.

Für den tatsächlichen neuen Profillocator bleibt das 131072-Byte-Scriptlimit
maßgeblich. Die vorhandene unabhängige Ganz-AST-Oracle (AST: Abstract Syntax
Tree; abstrakter Syntaxbaum) soll mit den neu gewählten Eingaben die gesamte
Quelle und unveränderte Originalprofilbytes prüfen. Runner und Harness prüfen
zusätzlich Unix-Zeilenenden (LF: Line Feed); die vorhandene Proxy-Methode prüft
nur die aktuelle Rohform.
Runner, Proxy und Harness erhalten jeweils den passenden vorhandenen Builder
und dessen eigene Fit-/Ganz-AST-Methode. Bestehende Assertions bleiben erhalten.
Erst nach Erfolg aller drei Routen und dem Quellenpin-Nachcheck dürfen die drei
vorher abwesenden eigenen Scriptdateien erzeugt werden. Eine reine Generierung
startet diese Dateien nicht.

## Claimgrenze und Abschluss

Das Paket ist **nicht vollständig validiert**; sein einziger Lauf ist vor den
Form-/Fitprüfungen fehlgeschlagen. Auch ein späterer reiner Paket-PASS belegt weder
frische Workeraufnahme noch verwendete Quellenbytes, SESSION_END
(Abschlussmeldung mit Counts und Kanalhash), nativen Exit/Cleanup oder die
Messmethode. DEC-076 (vertrauenswürdige Schulungsquellen ohne
Manipulationsisolation) bleibt maßgeblich. Keine Produktions- oder SQL-Freigabe.

Vor einem späteren nativen Lauf bleibt ein separat geprüfter konkreter
Prozess-/Kanalplan mit gemeinsamem Zeit-, Byte- und Schrittbudget sowie
gehaltenen eigenen Windows-/Linuxprozessen und unabhängiger Absenzprüfung
erforderlich. Ein Paketbericht oder Windows-Launcherexit ersetzt diese Gates
nicht. Fehler und Partialartefakte bleiben privat erhalten; kein blinder Retry,
keine fremde Bereinigung oder Budgeterneuerung.

Die öffentliche Diagnoseintegration erfolgt nach unabhängiger Befundschließung und lokalen
Dokumentations-/Datenschutzprüfungen über aktuelle grüne PR-/Base-Gates,
regulären Merge, frische Main-Gates, vollständige Übernahme, Synchronisation und
sichere eigene lokale/Remote-Branchbereinigung. Unveränderte grüne Runnermodelle
werden nicht erneut ausgeführt. Private Evidence und fremde Ressourcen bleiben
erhalten.

## Erforderliche Entscheidung zur Wiederaufnahme

Vorgeschlagen ist eine ausdrückliche begrenzte Erweiterung für die Korrektur
der AST-Providerwahl, eine Gegenprobe zur Ablehnung des falschen Interpreters
vor weiteren Wirkungen und nötige unabhängige Reviewkorrekturen: denselben
Rahmen von vier auf höchstens sechs stabile Quellen-/Teststände erweitern,
mit Checkpoint nach Stand fünf. Dabei bleiben
die bisherigen Fehlversuche erhalten, die 3.12-Hashes und Bytegrenzen
unverändert. Die noch unerledigten Paketprüfungen benötigen erneut eine
konkrete Quellen-/Testprüfung vor Ausführung und ein passendes Lauf-GO.
Eine notwendige native 3.12-Prüferinvocation wäre vorher mit eigenem endlichen
Prozessplan zu prüfen; daraus folgt keine Worker-, Demo- oder SQL-Freigabe.

Dieser Vorschlag ist keine bereits erteilte Freigabe. Die
[gemeinsame Wellenbudgetregel](../../.ai/foundation/PROCESSING_EFFICIENCY_POLICY.md#shared-wave-budget)
verlangt an der harten Grenze: „admit no new work or agent“. Der kontinuierliche
menschliche Auftrag bleibt bestehen; er erneuert diesen ausgeschöpften
konkreten Rahmen nicht automatisch. Bis zur Entscheidung sind nur der sichere
Diagnoseabschluss und dessen reguläre Integration zulässig.

Der unabhängige Diagnose-/Dispositionsreview des Dokumentationsstands
`a683d743376f2bb25e39d9893acf08241492dd14` meldete keine offenen priorisierten
Befunde und bestätigte das Integrations-GO ausschließlich für diesen
Dokumentationsabschluss. Auch die Präzisierung auf höchstens sechs Stände mit
Checkpoint nach fünf wurde nur als noch nicht freigegebener
Entscheidungsvorschlag bestätigt.
