"""Neutralisiert nur Identitätsmetadaten und automatisch erzeugte Vorschaubilder."""
from pathlib import Path
import sys
from zipfile import ZipFile, ZIP_DEFLATED
from xml.etree import ElementTree as ET


def neutralize(target: Path) -> None:
    with ZipFile(target) as archive:
        contents = {item.filename: archive.read(item) for item in archive.infolist()}
    removed = {name for name in contents if name.lower().startswith('docprops/thumbnail.')}
    for name in removed:
        del contents[name]
    for name in ('docProps/core.xml', 'docProps/app.xml'):
        if name not in contents:
            continue
        tree = ET.fromstring(contents[name])
        for element in tree.iter():
            if element.tag.rsplit('}', 1)[-1].lower() in {'creator', 'lastmodifiedby', 'company', 'manager', 'hyperlinkbase'}:
                element.text = ''
        contents[name] = ET.tostring(tree, encoding='utf-8', xml_declaration=True)
    for name in ('_rels/.rels', '[Content_Types].xml'):
        tree = ET.fromstring(contents[name])
        ET.register_namespace('', tree.tag.split('}')[0].lstrip('{'))
        for item in list(tree):
            target_name = item.attrib.get('Target', item.attrib.get('PartName', '')).lstrip('/')
            if target_name in removed:
                tree.remove(item)
        contents[name] = ET.tostring(tree, encoding='utf-8', xml_declaration=True)
    temporary = target.with_suffix('.neutralized.pptx')
    with ZipFile(temporary, 'w', ZIP_DEFLATED) as archive:
        for name, value in contents.items():
            archive.writestr(name, value)
    temporary.replace(target)


if __name__ == '__main__':
    neutralize(Path(sys.argv[1]))
