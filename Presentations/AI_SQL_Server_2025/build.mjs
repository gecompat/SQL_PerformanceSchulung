import fs from 'node:fs/promises';
import path from 'node:path';
import { createRequire } from 'node:module';
import { pathToFileURL, fileURLToPath } from 'node:url';
import { execFileSync } from 'node:child_process';
import { deck } from './content.mjs';

// Runtimepfade werden vom Aufrufer übergeben. Keine privaten Pfade oder Credentials in der Quelle.
const here = path.dirname(fileURLToPath(import.meta.url));
const root = path.resolve(here, '../..');
const modules = process.env.ARTIFACT_NODE_MODULES;
const skill = process.env.PRESENTATION_SKILL_DIR;
const python = process.env.RUNTIME_PYTHON;
if (!modules || !skill || !python) throw new Error('ARTIFACT_NODE_MODULES, PRESENTATION_SKILL_DIR und RUNTIME_PYTHON sind erforderlich.');
process.env.RUNTIME_NODE_MODULES = modules;
const require = createRequire(path.join(modules, '_presentation_resolver.cjs'));
const { Presentation, PresentationFile } = await import(pathToFileURL(require.resolve('@oai/artifact-tool')).href);
const { finalizePresentation, resolvePresentationFont } = await import(pathToFileURL(path.join(skill, 'container_tools/artifact_tool_utils.mjs')).href);
const build = path.resolve(root, process.env.AI_SLIDES_BUILD_DIR ?? 'Runtime/Temp/ai-slides');
const profile = process.env.AI_SLIDES_PROFILE ?? 'full';
if (!['full', 'basis', 'standard'].includes(profile)) throw new Error('Unbekanntes Lehrprofil.');
const course = profile !== 'full' ? JSON.parse(await fs.readFile(path.join(here, `${profile}.course.json`), 'utf8')) : null;
const courseLabel = profile.toUpperCase();
const sourceNumbers = course ? course.blocks.flatMap(block => block.source_slides) : deck.slides.map((_, i) => i + 1);
if (course && (course.source_slide_count !== deck.slides.length || new Set(sourceNumbers).size !== sourceNumbers.length
    || sourceNumbers.some(n => !Number.isInteger(n) || !deck.slides[n - 1] || deck.slides[n - 1].title !== course.source_titles[String(n)]))) {
  throw new Error(`${courseLabel}-Auswahl stimmt nicht mit der Masterquelle überein.`);
}
const slides = sourceNumbers.map(n => deck.slides[n - 1]);
const output = path.resolve(root, process.env.AI_SLIDES_OUTPUT ?? (course ? course.output : 'Presentations/SQL_Server_2025_KI.pptx'));
for (const target of [build, output]) {
  const relative = path.relative(root, target);
  if (relative.startsWith('..') || path.isAbsolute(relative)) throw new Error('Build und Ausgabe müssen im Workspace liegen.');
}
const slideCount = slides.length;
await fs.mkdir(build, { recursive: true });
await fs.mkdir(path.dirname(output), { recursive: true });
const register = await fs.readFile(path.join(root, 'Documentation/Research/SOURCE_REGISTER.md'), 'utf8');
const sourceMap = new Map();
for (const line of register.split(/\r?\n/)) {
  const id = line.match(/`(SRC-\d+)`/);
  const link = line.match(/\[([^\]]+)\]\((https?:[^)]+)\)/);
  if (id && link) sourceMap.set(id[1], `${id[1]}: ${link[1]}\n${link[2]}\nAbrufdatum laut Quellenregister: ${line.match(/20\d{2}-\d{2}-\d{2}/g)?.at(-1) ?? deck.date}`);
}
const font = await resolvePresentationFont({ fontFamily: 'Arial', pythonExecutable: python });
const fontFamily = typeof font === 'string' ? font : font.fontFamily;
if (!fontFamily) throw new Error('Keine verfügbare Arial-Schrift ermittelt.');
const p = Presentation.create({ slideSize: { width: 1280, height: 720 } });
const nativeTables = [];
const colors = { ink: '#15283D', muted: '#52647A', accent: '#007A83', bg: '#FFFFFF', header: '#E8F2F2', grid: '#C8D5DE' };

function text(slide, value, left, top, width, height, size = 30, bold = false, color = colors.ink) {
  const box = slide.shapes.add({ geometry: 'textbox', name: `text-${slide.shapes.items.length}`, position: { left, top, width, height }, fill: 'none', line: { fill: 'none', width: 0 } });
  box.text = value;
  box.text.style = { typeface: fontFamily, fontSize: size, bold, color, verticalAlignment: 'top' };
  return box;
}

for (let i = 0; i < slides.length; i++) {
  const data = { ...slides[i], ...(course?.overrides?.[String(sourceNumbers[i])] ?? {}) };
  const slide = p.slides.add();
  slide.background.fill = colors.bg;
  if (data.cover) {
    text(slide, course ? `KI mit SQL Server 2025\n${courseLabel}` : data.title, 80, 155, 1120, 220, 64, true);
    text(slide, course ? (course.subtitle ?? 'Vier Stunden · Grundlagen, sichere SQL-Werte und belegbare Antworten') : data.subtitle, 80, 435, 1100, 95, 32, false, colors.muted);
    text(slide, `Schulungsunterlagen · Stand ${deck.date}`, 80, 610, 1080, 36, 24, false, colors.accent);
  } else {
    text(slide, data.title, 72, 52, 1136, 116, 44, true);
    let y = 186;
    if (data.table) {
      nativeTables.push(i + 1);
      const height = data.table.length <= 4 ? 330 : 420;
      const t = slide.tables.add({ rows: data.table.length, columns: data.table[0].length, left: 72, top: y, width: 1120, height, columnWidths: data.widths, values: data.table });
      t.borders.assign({ style: 'solid', fill: colors.grid, width: 1 });
      for (let row = 0; row < data.table.length; row++) {
        for (let col = 0; col < data.table[row].length; col++) {
          const cell = t.getCell(row, col);
          cell.fill = row === 0 ? colors.header : colors.bg;
          cell.text.style = { typeface: fontFamily, fontSize: 24, bold: row === 0, color: colors.ink };
        }
      }
      t.cells.block({ row: 0, column: 0, rowCount: data.table.length, columnCount: data.table[0].length }).assign({ margins: { left: 12, right: 12, top: 5, bottom: 5 }, anchor: 'center' });
    } else {
      if (data.code) {
        const codeHeight = Math.max(180, data.code.split('\n').length * 34);
        text(slide, data.code, 72, y, 1136, codeHeight, 28, false, colors.accent);
        y += codeHeight + 25;
      }
      const blocks = data.blocks ?? [];
      const available = data.code ? 616 - y : 405;
      const pitch = available / Math.max(1, blocks.length);
      for (const [label, body] of blocks) {
        text(slide, label, 72, y, 245, pitch - 10, 28, true, colors.accent);
        text(slide, body, 335, y, 865, pitch - 10, 30);
        y += pitch;
      }
    }
    if (data.bottom) text(slide, data.bottom, 72, 617, 1108, 60, 24, false, colors.muted);
    text(slide, course ? `${courseLabel} ${i + 1} · Quellfolie ${sourceNumbers[i]} · ${data.module}` : `${String(i + 1).padStart(2, '0')}  ${data.module}`, 72, 682, 1120, 26, 18, false, colors.muted);
  }
  const notes = [data.notes];
  if (course) notes.push(`${courseLabel}-Folie ${i + 1}, Quellfolie ${sourceNumbers[i]} des 61-Folien-Masterdecks. Ablauf und Beobachtungsbogen: ${course.guide}. Lösungen und Rubrik ausschließlich im vorhandenen Offline-Arbeitsheft. Zeitfenster sind Planwerte; SQL-Laufzeiten belegen keine Lehrzeit.`);
  if (data.demo) {
    const demoId = data.demo.slice(0, 7);
    const demoPath = `Demos/09_AI_SQL_Server_2025/${data.demo}`;
    await fs.access(path.join(root, demoPath, 'manifest.json'));
    notes.push(`Konkreter Aufruf nach Einrichtung gemäß DEMO_EXECUTION_GUIDE.md:\nInvoke-SqlPerfDemo -DemoId ${demoId} -Server $server -Authentication $authentication -Username $username\nPhasen und Abbruch: manifest.json sowie 90_Cleanup.sql. Vier vollständige Eigentumsmarker und denselben RunToken prüfen. Anschließend unabhängige Abwesenheit der eigenen DB bestätigen.\nDemoquelle: ${demoPath}/README.md\nErgebnisvertrag: ${demoPath}/Expected/result-contract.json`);
  }
  notes.push('Quellen und Gültigkeit:');
  for (const id of data.sources ?? []) {
    if (!sourceMap.has(id)) throw new Error(`Quelle fehlt: ${id}`);
    notes.push(sourceMap.get(id));
  }
  for (const ref of data.refs ?? []) { await fs.access(path.join(root, ref)); notes.push(`Projektquelle: ${ref}`); }
  notes.push(`Didaktische Zuordnung: ${data.module}. Materialstand ${deck.date}. Aktuelle Ausführungsfreigaben und Demo-Gates: Documentation/Project_Planning/CURRENT_EXECUTION_STATUS.md.`);
  slide.speakerNotes.text = notes.join('\n\n');
}
if (p.slides.items.length !== slideCount) throw new Error('Deckquelle und exportierter Folienumfang stimmen nicht überein.');
const candidate = path.join(build, 'candidate.pptx');
await (await PresentationFile.exportPptx(p)).save(candidate);
// Identitätsmetadaten und nicht benötigte automatische Vorschau entfernen.
// Native Text-/Tabellen-/Notizenobjekte bleiben vollständig im Artifact-Tool-Export erhalten.
execFileSync(python, [path.join(here, 'neutralize_package.py'), candidate], { stdio: 'inherit' });
const result = await finalizePresentation({ workspaceDir: root, candidatePath: candidate, finalPath: output, pythonExecutable: python,
  integrityValidatorPath: path.join(skill, 'container_tools/inspect_presentation_package_integrity.py'),
  layoutValidatorPath: path.join(skill, 'container_tools/inspect_presentation_layout_geometry.py'),
  layoutArgs: ['--expected-slide-size-emu', '12192000,6858000', '--validate-bullet-geometry', '--validate-heading-fit', ...nativeTables.flatMap(n => ['--require-native-table-slide', String(n)])],
  explicitTotalSlideCount: slideCount, requiredNativeTableOwnerSlides: nativeTables, requiredNativeChartOwnerSlides: [],
  fontPolicy: { basis: 'design', families: [fontFamily] }, verifyArtifactToolImport: true,
  receiptPath: path.join(build, `validation-${Date.now()}.json`) });
console.log(JSON.stringify({ finalPath: output, slideCount, nativeTables, validationStatus: result.status ?? 'completed' }));
// Nach dem Finalizer genau den finalen Packageinhalt neu importieren und vollständig rendern.
const { FileBlob } = await import(pathToFileURL(require.resolve('@oai/artifact-tool')).href);
const final = await PresentationFile.importPptx(await FileBlob.load(output));
const onlyRender = process.env.AI_SLIDES_RENDER_ONLY ? Number(process.env.AI_SLIDES_RENDER_ONLY) : null;
if (onlyRender !== null && (!Number.isInteger(onlyRender) || onlyRender < 1 || onlyRender > slideCount)) throw new Error('AI_SLIDES_RENDER_ONLY muss eine vorhandene Foliennummer sein.');
let rendered = 0;
for (const [i, slide] of final.slides.items.entries()) {
  if (onlyRender !== null && onlyRender !== i + 1) continue;
  const stem = `slide-${String(i + 1).padStart(2, '0')}`;
  const png = await final.export({ slide, format: 'png', scale: 1 });
  await fs.writeFile(path.join(build, `${stem}.png`), new Uint8Array(await png.arrayBuffer()));
  await fs.writeFile(path.join(build, `${stem}.layout.json`), await (await slide.export({ format: 'layout' })).text());
  rendered++;
}
if (onlyRender === null) await fs.writeFile(path.join(build, 'deck-montage.webp'), new Uint8Array(await (await final.export({ format: 'webp', montage: true })).arrayBuffer()));
console.log(`${rendered} finale Folien gerendert.`);
