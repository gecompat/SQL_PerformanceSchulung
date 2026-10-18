"""Regression für PowerPoint-lesbare Datumsmetadaten nach Neutralisierung."""
import importlib.util
from io import BytesIO
from pathlib import Path
import tempfile
import unittest
from xml.etree import ElementTree as ET
from zipfile import ZipFile

ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location(
    'ai_neutralizer', ROOT / 'Presentations/AI_SQL_Server_2025/neutralize_package.py')
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)
DCTERMS = 'http://purl.org/dc/terms/'
XSI = 'http://www.w3.org/2001/XMLSchema-instance'
CORE = b'''<cp:coreProperties
 xmlns:cp="http://schemas.openxmlformats.org/package/2006/metadata/core-properties"
 xmlns:dc="http://purl.org/dc/elements/1.1/"
 xmlns:dcterms="http://purl.org/dc/terms/"
 xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
 <dc:creator>LAB_AUTHOR</dc:creator><cp:lastModifiedBy>LAB_EDITOR</cp:lastModifiedBy>
 <dcterms:created xsi:type="dcterms:W3CDTF">2026-10-12T00:00:00Z</dcterms:created>
 <dcterms:modified xsi:type="dcterms:W3CDTF">2026-10-12T00:00:00Z</dcterms:modified>
</cp:coreProperties>'''


def assert_date_types(test, xml):
    """XML-Parser akzeptieren auch nicht auflösbare QNames in Attributwerten."""
    bindings = dict(value for event, value in ET.iterparse(
        BytesIO(xml), events=('start-ns',)))
    tree = ET.fromstring(xml)
    for field in ('created', 'modified'):
        element = tree.find(f'{{{DCTERMS}}}{field}')
        test.assertIsNotNone(element)
        prefix, local = element.attrib[f'{{{XSI}}}type'].split(':', 1)
        test.assertEqual(bindings.get(prefix), DCTERMS)
        test.assertEqual(local, 'W3CDTF')


class PresentationPackageTests(unittest.TestCase):
    def test_undeclared_date_type_prefix_is_rejected(self):
        broken = CORE.replace(b'xmlns:dcterms=', b'xmlns:ns2=').replace(
            b'<dcterms:', b'<ns2:').replace(b'</dcterms:', b'</ns2:')
        ET.fromstring(broken)  # Wohlgeformtes XML allein reicht nicht.
        with self.assertRaises(AssertionError):
            assert_date_types(self, broken)

    def test_neutralization_preserves_resolvable_dates_and_slide_bytes(self):
        rels = b'''<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
          <Relationship Id="thumb" Target="docProps/thumbnail.jpeg" Type="thumbnail"/>
          <Relationship Id="deck" Target="ppt/presentation.xml" Type="officeDocument"/>
        </Relationships>'''
        types = b'''<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
          <Override PartName="/docProps/thumbnail.jpeg" ContentType="image/jpeg"/>
          <Override PartName="/ppt/presentation.xml" ContentType="presentation"/>
        </Types>'''
        slide = b'<slide>LAB_SLIDE</slide>'
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / 'deck.pptx'
            with ZipFile(target, 'w') as archive:
                for name, value in {'docProps/core.xml': CORE, '_rels/.rels': rels,
                                    '[Content_Types].xml': types,
                                    'docProps/thumbnail.jpeg': b'LAB_THUMBNAIL',
                                    'ppt/slides/slide1.xml': slide}.items():
                    archive.writestr(name, value)
            MODULE.neutralize(target)
            with ZipFile(target) as archive:
                xml = archive.read('docProps/core.xml')
                assert_date_types(self, xml)
                tree = ET.fromstring(xml)
                for element in tree:
                    if element.tag.rsplit('}', 1)[-1] in ('creator', 'lastModifiedBy'):
                        self.assertFalse(element.text)
                self.assertNotIn('docProps/thumbnail.jpeg', archive.namelist())
                self.assertNotIn(b'thumbnail', archive.read('_rels/.rels'))
                self.assertNotIn(b'thumbnail', archive.read('[Content_Types].xml'))
                self.assertEqual(archive.read('ppt/slides/slide1.xml'), slide)

    def test_published_deck_has_resolvable_date_types(self):
        for filename in ('SQL_Server_2025_KI.pptx', 'SQL_Server_2025_KI_BASIS.pptx'):
            with self.subTest(filename=filename), ZipFile(ROOT / 'Presentations' / filename) as archive:
                assert_date_types(self, archive.read('docProps/core.xml'))


if __name__ == '__main__':
    unittest.main()
