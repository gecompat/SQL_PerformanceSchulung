/** Targeted Open XML repair. JSZip is supplied by the artifact runtime.
 * Keeps masters, relationships, SlideKeys, Custom Shows and untouched parts.
 * Usage: node repair_presentation_diagrams.mjs --node-modules <directory>
 *        --source <master.pptx> --output <candidate.pptx>
 */
import fs from 'node:fs/promises';
import path from 'node:path';
import {createRequire} from 'node:module';
const args = Object.fromEntries(process.argv.slice(2).reduce((a,v,i,s) => {
  if(i % 2 === 0) a.push([v.replace(/^--/,''),s[i+1]]); return a;
},[]));
if (!args['node-modules'] || !args.source || !args.output) throw new Error('Required: --node-modules, --source, --output');
const require = createRequire(path.join(path.resolve(args['node-modules']),'package.json'));
const JSZip = require('jszip');
const zip = await JSZip.loadAsync(await fs.readFile(args.source));
const setPart=(part,xml)=> {const old=zip.file(part);zip.file(part,xml,{date:old.date,comment:old.comment,unixPermissions:old.unixPermissions,dosPermissions:old.dosPermissions,createFolders:false});};
const changes=[];
const escape = t => t.replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('>','&gt;');
const replace = (xml,old,value) => {
  if (!xml.includes(old)) throw new Error(`Missing expected fragment: ${old}`);
  return xml.replace(old,value);
};
function shape(xml,name,fn) {
  let matched=false;
  xml=xml.replace(/<p:(sp|cxnSp)>[\s\S]*?<\/p:\1>/g, block => {
    if (!block.includes(`name="${name}"`)) return block;
    if (matched) throw new Error(`Duplicate shape ${name}`);
    matched=true;return fn(block);
  });
  if (!matched) throw new Error(`Missing shape ${name}`);
  return xml;
}
function frame(block,x,y,w,h) {
  return block.replace(/<a:xfrm[^>]*>[\s\S]*?<\/a:xfrm>/,
    `<a:xfrm><a:off x="${x}" y="${y}"/><a:ext cx="${w}" cy="${h}"/></a:xfrm>`);
}
function text(xml,name,values) {
  return shape(xml,name,b => {
    let index=0;
    b=b.replace(/<a:t>[\s\S]*?<\/a:t>/g,() => `<a:t>${escape(values[index++] ?? '')}</a:t>`);
    if(index!==values.length) throw new Error(`Text run count ${name}: ${index}/${values.length}`);
    return b;
  });
}
function label(xml,template,name,id,value,x,y,w,h,size=1500,color='526777') {
  let source;
  shape(xml,template,b=>{source=b;return b;});
  source=source.replace(/<p:cNvPr[\s\S]*?<\/p:cNvPr>|<p:cNvPr[^>]*\/>/,
    `<p:cNvPr id="${id}" name="${name}"/>`);
  source=frame(source,x,y,w,h);
  let first=true;
  source=source.replace(/<a:t>[\s\S]*?<\/a:t>/g,()=>`<a:t>${first?(first=false,escape(value)):''}</a:t>`)
    .replace(/sz="\d+"/g,`sz="${size}"`).replace(/<a:srgbClr val="[A-Fa-f0-9]+"\/>/g,`<a:srgbClr val="${color}"/>`);
  return xml.replace('</p:spTree>',source+'</p:spTree>');
}
function connection(xml,id,startId,endId,sx,sy,ex,ey,startIdx=1,endIdx=3) {
  let found=false;
  xml=xml.replace(/<p:cxnSp>[\s\S]*?<\/p:cxnSp>/g,b=>{
    if(!b.includes(`<p:cNvPr id="${id}"`))return b;
    found=true;
    b=b.replace(/<a:stCxn[^>]*\/>/,`<a:stCxn id="${startId}" idx="${startIdx}"/>`)
      .replace(/<a:endCxn[^>]*\/>/,`<a:endCxn id="${endId}" idx="${endIdx}"/>`);
    const flips=`${ex<sx?' flipH="1"':''}${ey<sy?' flipV="1"':''}`;
    return b.replace(/<a:xfrm[^>]*>[\s\S]*?<\/a:xfrm>/,
      `<a:xfrm${flips}><a:off x="${Math.min(sx,ex)}" y="${Math.min(sy,ey)}"/><a:ext cx="${Math.abs(ex-sx)}" cy="${Math.abs(ey-sy)}"/></a:xfrm>`);
  });
  if(!found)throw new Error(`Missing connector ${id}`);return xml;
}
const reverseSlides=[4,14,16,20,22,27,29,31,50,51,59,78];
for(const n of reverseSlides) {
  const part=`ppt/slides/slide${n}.xml`;
  let xml=await zip.file(part).async('string');
  let count=0;
  xml=xml.replace(/<a:headEnd type="arrow"([^>]*)\/>/g,(_,attrs)=>{count++;return `<a:tailEnd type="arrow"${attrs}/>`;});
  if(!count)throw new Error(`No arrowheads on slide ${n}`);
  changes.push({slide:n,arrowheads:count});
  if(n===14) {
    xml=text(xml,'physical-label',['Physical Read','lädt Page in Cache']);
    xml=text(xml,'logical-label',['Logical Read','nutzt Page im Cache']);
    // Three lines need enough height to avoid PowerPoint shrinking the label on save.
    xml=shape(xml,'logical-label',b=>b.replace('cy="571500"','cy="800000"'));
  }
  if(n===16) {
    const positions=[609600,3324225,6038850,8753475];
    for(let i=1;i<=4;i++) {
      xml=shape(xml,`flow-${i}`,b=>frame(b,positions[i-1],2609850,2500000,1428750));
      xml=shape(xml,`flow-${i}-text`,b=>frame(b,positions[i-1]+133350,2724150,2233300,1200150));
    }
    for(let i=0;i<3;i++)xml=connection(xml,132+i,6+i*2,8+i*2,positions[i]+2500000,3324225,positions[i+1],3324225,3,1);
    xml=xml.replace(/<p:cxnSp>[\s\S]*?<\/p:cxnSp>/g,b=>b.includes('<p:cNvPr id="135"')?'':b);
    xml=text(xml,'flow-2-text',['Log Buffer','nimmt Records auf']);
    xml=text(xml,'flow-5-text',['Separat: Checkpoint','schreibt Dirty Pages']);
    xml=shape(xml,'flow-5',b=>frame(b,3950000,4380000,4200000,800000));
    xml=shape(xml,'flow-5-text',b=>frame(b,4083350,4494300,3933300,571400));
    xml=shape(xml,'conclusion-bg',b=>frame(b,1000000,5490000,10100000,819150));
    xml=shape(xml,'conclusion',b=>frame(b,1247650,5661450,9604700,457200));
    xml=text(xml,'conclusion',['Commit wartet bei vollständiger Durability auf Log Flush, nicht auf Checkpoint.']);
    xml=label(xml,'conclusion','durability-label',201,'Commit-Pfad bei vollständiger Durability',1000000,2130000,10100000,300000);
  }
  if(n===27) {
    for(const [name,x,y] of [['plan-scan',8286750,2514600],['plan-lookup',8286750,4229100],['plan-loops',4000500,3371850],['plan-select',1028700,3371850]]) {
      xml=shape(xml,name,b=>frame(b,x,y,2000250,1066800));
      xml=shape(xml,name+'-text',b=>frame(b,x+133350,y+114300,1733550,838200));
    }
    xml=text(xml,'plan-scan-text',['Index Seek','Outer: 100 Rows']);
    xml=text(xml,'plan-lookup-text',['Key Lookup','Inner: 100 ×']);
    xml=connection(xml,111,6,10,8286750,3048000,6000750,3905250);
    xml=connection(xml,112,8,10,8286750,4762500,6000750,3905250);
    xml=connection(xml,113,10,12,4000500,3905250,3028950,3905250);
    xml=shape(xml,'plan-caption',b=>frame(b,1000000,5570000,10100000,457200));
    xml=text(xml,'plan-caption',['Datenfluss rechts → links. Outer Rows steuern die Inner-Aufrufe.']);
  }
  if(n===29) {
    xml=text(xml,'grant-run-text',['Used Memory','Spill prüfen']);
    xml=text(xml,'grant-caption',['Undergrant erhöht Spill-Risiko. Overgrant bindet Workspace.']);
  }
  if(n===50)xml=label(xml,'footer-left','navigation-caption',201,'Pfeile zeigen die Navigation vom Root zum Leaf Level.',1800000,5650000,8500000,350000,1800);
  if(n===51) {
    xml=label(xml,'rl-caption','rid-lookup-label',201,'RID Lookup',1600000,3840000,2600000,300000,1650,'F2994A');
    xml=label(xml,'rl-caption','key-lookup-label',202,'Key Lookup',7900000,3840000,2600000,300000,1650,'007C83');
  }
  if(n===78)xml=text(xml,'conclusion',['Hohe geschätzte Operatorkosten allein belegen keine Ursache.']);
  setPart(part,xml);
}
for(const n of [17,39,54,66]) {
  const part=`ppt/slides/slide${n}.xml`;let xml=await zip.file(part).async('string');
  if(n===17)xml=replace(xml,'Instant File Initialization beschleunigt Data-File-Wachstum, nicht Log-Wachstum',escape('IFI: Data Files unter Voraussetzungen. Log-Autogrowth bis 64 MB ab SQL Server 2022.'));
  if(n===39)xml=text(xml,'good-code',['WHERE EventTime >= @Date','  AND EventTime <  DATEADD(day, 1, @Date)']);
  if(n===54) {
    xml=label(xml,'tip-x-label','tip-y-label',201,'Relative Zugriffskosten (Schema)',1400000,2120000,5300000,300000,1500);
    xml=text(xml,'tip-x-label',['Trefferzahl steigt']);
  }
  if(n===66)xml=label(xml,'block-caption','wait-direction-legend',201,'Pfeil bedeutet: Session wartet auf die Session an der Pfeilspitze.',1000000,2030000,10100000,350000,1800);
  setPart(part,xml);changes.push({slide:n,clarification:true});
}
const notes={
  14:'Diagramm: Pfeile zeigen den Lesepfad von Data Files über den Buffer Pool zu den Query-Operatoren. Physical Read lädt eine Page in den Cache. Logical Read zählt den Page-Zugriff über den Cache und ist kein zusätzlicher physischer Read. Read-ahead bleibt separat zu interpretieren.',
  16:'Diagramm: Der gezeigte Commit-Pfad gilt für vollständige Durability. Ein Log Flush wartet nicht darauf, dass der Log Buffer voll ist. Checkpoint ist ein separater Vorgang und schreibt Dirty Pages unter Einhaltung von WAL, auch unabhängig von einer Commit-Bestätigung. Quelle: https://learn.microsoft.com/en-us/sql/relational-databases/logs/control-transaction-durability?view=sql-server-ver17 und https://learn.microsoft.com/en-us/sql/relational-databases/sql-server-transaction-log-architecture-and-management-guide?view=sql-server-ver17. Geprüft am 2026-10-05.',
  17:'Korrektur: SQL Server 2019 bietet keine IFI für das Log. Seit SQL Server 2022 können Log-Autogrowth-Ereignisse bis einschließlich 64 MB von IFI profitieren. Größere Log-Wachstumsschritte profitieren nicht. Dies ist keine Empfehlung für häufiges kleines Autogrowth. Data-File-IFI besitzt gesonderte Sicherheits-, Plattform- und TDE-Voraussetzungen. Quelle SRC-034: https://learn.microsoft.com/en-us/sql/relational-databases/databases/database-instant-file-initialization?view=sql-server-ver17. Geprüft am 2026-10-05.',
  27:'Diagramm: Vereinfachtes Lookup-Muster mit zwei Eingängen für Nested Loops. Der Nonclustered Index Seek liefert den Outer Input. Key Lookup ist der Inner Input und wird hier 100-mal aufgerufen. Beide Zeilenströme führen zum Nested-Loops-Operator und von dort zu SELECT. Die Pfeile zeigen Datenfluss. Die Pull-Aufrufe erfolgen vom Parent zu den Inputs in Gegenrichtung. Quelle: https://learn.microsoft.com/en-us/sql/relational-databases/performance/joins?view=sql-server-ver17. Geprüft am 2026-10-05.',
  29:'Diagramm: Granted Memory und Used Memory unterscheiden sich. Spill ist eine mögliche Laufzeitfolge unzureichenden Workspace und kein alternativer Messwert zu Used Memory. Overgrant bindet Workspace und kann konkurrierende Grants begrenzen. Quellen SRC-009 und SRC-010.',
  39:'Beispielvoraussetzung: @Date ist vom Typ date oder enthält bei einem datetime-Typ exakt den Tagesbeginn. Beide Intervallgrenzen beziehen sich auf denselben Parameter. Das halboffene Intervall enthält alle Zeitpräzisionen des Tages.',
  50:'Diagramm: Die Pfeile stellen Child-Page-Verweise und den Suchpfad vom Root über Intermediate zum Leaf Level dar. Sie zeigen keinen Execution-Plan-Datenfluss.',
  51:'Diagramm: Lookup-Navigation vom Nonclustered Index zum jeweiligen Basisobjekt. Heap verwendet RID Lookup, eine Clustered Table Key Lookup. Die beiden Zielobjekte sind Alternativen.',
  54:'Diagramm: Schematische relative Zugriffskosten, keine gemessenen Zeiten und keine universelle Trefferschwelle. Die horizontale Achse zeigt steigende Trefferzahl. Indexbreite, Coverage, Page-Anzahl, Cache und Kostenmodell beeinflussen den Tipping Point.',
  66:'Diagramm: Wartekanten sind von der wartenden Session auf die blockierende Session gerichtet. Session 62 und 73 warten auf 51, Session 84 wartet auf 62. Die vorhandene Pfeilrichtung ist korrekt und wurde bewusst erhalten.',
};
for(const [n,note] of Object.entries(notes)) {
  const part=`ppt/notesSlides/notesSlide${n}.xml`;let xml=await zip.file(part).async('string');
  let found=false;
  xml=xml.replace(/<p:sp>[\s\S]*?<\/p:sp>/g,b=>{
    if(!b.includes('<p:ph type="body"'))return b;
    found=true;return b.replace('</p:txBody>',`<a:p><a:r><a:t>${escape(note)}</a:t></a:r></a:p></p:txBody>`);
  });
  if(!found)throw new Error(`Missing notes body ${n}`);setPart(part,xml);
}
await fs.mkdir(path.dirname(path.resolve(args.output)),{recursive:true});
const bytes=await zip.generateAsync({type:'nodebuffer',compression:'DEFLATE',compressionOptions:{level:6}});
await fs.writeFile(args.output,bytes);
console.log(JSON.stringify({output:args.output,changes}));
