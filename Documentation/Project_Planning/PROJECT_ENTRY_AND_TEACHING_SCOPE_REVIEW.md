# Projekteinstieg und didaktischer Maßstab

Stand 20. Oktober 2026, Basis `4a8d5aa2e6252803d7773b9e075c1bbfc4d8e5df`
nach vollständig abgeschlossenem PR263. Der Mensch priorisiert eine README
als Einstieg für alle menschlichen Zugriffe und widerspricht dem Ausschluss
nützlicher SQL-Beispiele wegen fehlender eigener Performance-Messungen.

## Endlicher Umfang

Pflege vorhandener Einstiege, Projektregeln und Quellenklassifikation; keine
neue Fachdemo, Kennung oder Runtime. Ein Implementierungsowner, ein unabhängiger
fachlicher/redaktioneller Review vor Integration. Höchstens vier stabile
Quellen-/Testkandidaten, Checkpoint nach dem ersten, harte Grenze vier inklusive
Review, höchstens drei gebündelter Befundnachläufe, lokaler relevanter Checks,
aktueller PR-/Main-Gates, regulärer Integration und eigenem Branchcleanup.
Token-/Kostenverbrauch UNKNOWN. Keine Übernahme ausgeschöpfter technischer Scopes.

## Inhaltliche Korrektur

Die alten Regeln übertrugen den Messdemo-Lifecycle auf den ganzen Kurs. Der
aktuelle menschliche Auftrag korrigiert diese zu enge Auslegung. Konzepte,
SQL-Techniken, Lösungsmuster, praktische Hinweise und qualifizierte Faustregeln
sind eigenständige Lehrinhalte. Für qualitative Aussagen können nachvollziehbare
Herleitungen und Produktdokumentation ausreichen. Konkrete Zahlen und als
gemessen behauptete Wirkungen brauchen ihre tatsächliche Messgrundlage.

Bestehende ausführbare Demopakete behalten Sicherheits-, Datenschutz-,
Manifest-, Laufzeit- und Qualifikationsgates. Es gibt keine Ausführungsfreigabe
für alte Skripte, keine Änderung an SQL oder Ergebnisoracles und keine neue
empirische Behauptung. Betroffene native Projektverträge werden konsistent
angepasst; Foundation-Mindestregeln bleiben unverändert.

README, Dokumentations-, Präsentations-, Varianten- und Curriculumeinstieg
führen zu vorhandenen Inhalten und konkreten Nutzerhandlungen. Interne
Entwicklungsstände und Reviewkataloge stehen in der Projektpflege. Die
Darstellung verspricht weder unbekannte Downloads noch neue Funktionsabnahmen.

Die historische Quellenmatrix wird nicht rückwirkend umgeschrieben. Der
aktuelle Vorspann und die datierte Neubewertung von SRC-LEGACY-015 erklären,
warum fehlende A/B-Messung allein seinen Ausschluss als Lerninhalt nicht trägt.
Alle vier REMOVE-Quellen bleiben im Archiv; die Kennzeichnung beschreibt die
damalige Migration konkreter Skripte. Heutige Inhaltsauswahl folgt den aktuellen
Projektregeln. Archivbytes, Quell-IDs, Hashes und historische Zählwerte bleiben
erhalten; das ist keine Behauptung bereits neu aufbereiteter Beispiele.

## Aufwandassessment der Regelkorrektur

- Lokale Checks: einmalige relative Link-/Ankerprüfung der geänderten Markdown-
  Einstiege, Privacy vor jedem Commit, bestehende W2-001-, Framework-,
  Demo-Ausführungspfad- und Curriculumvalidatoren. Keine neuen Spiegeltests
  für Überschriften oder Prosa; keine erneuten grünen technischen Suites.
- CI: vorhandene zentrale Pflichtgates bleiben. Klassen-/Quellen-/Curriculum-
  und Demo-Vertragsdateien selektieren die bestehenden fachlichen statischen
  Workflows. Die Deckprüfungen haben überlappende unveränderte Validatoren,
  prüfen daneben eigene Deckbindungen. Begründete begrenzte Ausnahme: bestehende
  Gates je aktuellem Head/Main unverändert erfüllen; keine Selektor-/Workflow-
  oder Oracleänderung allein zur Verkürzung dieser Dokumentationswelle.
- Keine SQL-Matrix: SQL, ausführbare Werkzeuge, Mess-/Ergebnisverträge und
  vorhandene Manifestqualifikationen sind unverändert. Die neue Abgrenzung
  erlaubt passende Lehrformen; sie behauptet keine Ersatzqualifikation.
- Logs: Status und feste Resultatzusammenfassungen; nur konkrete Findings
  vertiefen. Ein unabhängiger inhaltlicher Review, gezielter Delta-Review nur
  bei geänderten Befunden; keine Reviewketten zur Bestätigung grüner Tools.
- Bestehender Heartbeat bleibt unverändert, keine zusätzliche Automation,
  kein weiterer Implementierungsowner und keine neue Ausführung durch Planung.

C1/Checkpoint1: menschliche Einstiege und maßgebliche Lehrregeln konsistent
überarbeitet. Lokale W2-001-Klassifikation23, Framework20Dateien/19Codes/
5Eigentumsmarker, Demo-Ausführungspfade32 und Curriculum84aktiveClaims/
52Lernziele PASS. Keine SQL-Ausführung und keine Wiederholung unveränderter
technischer Suites. 71 neue relative Links/Anker und Privacy16Textdateien PASS.
Unabhängiger inhaltlicher Review folgt vor Integration. Abschluss erfordert aktuelle grüne Gates, regulären
Merge, frische Main-Gates, FullTree/Sync und sichere eigene Branchbereinigung.

C1 `83b5bcd05c38adbd9faad0204579f7bf89c4538e` vollständig unabhängig geprüft:
keine P1/P2, ein P3 zu einem verbliebenen pauschalen Evidenzsatz in
PROJECT_CONTEXT. C2 begrenzt diesen Satz auf lernzielgerechte Erklärungen/
Beispiele/Nachweise; Plan-/DMV-/Query-Store-/XE-/OS-Instrumentierung ist nur
für passende Diagnose-/Messlerneinheiten vorgesehen. Der übrige Schnitt ist
freigabefähig, nach dieser engen Korrektur Freigabe für reguläre Gates und
Integration; kein weiterer Vollreview erforderlich. Zwei Kandidaten, ein
enger Befundnachlauf, harte Grenze4 unverändert, Verbrauch UNKNOWN.
