"""Gezielte XML-/Ergebnis-/Kontextnegative; keine tatsächliche SQL-Evidenz."""
import sys,unittest,xml.etree.ElementTree as ET
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'Demos/09_AI_SQL_Server_2025/RES-008_Vector_Dimensions'))
import res008_plans as plans

def fixture(*,database=plans.DATABASE,rows=100,result=1,build='17.0.5005.3',statement=None):
    ns='{'+plans.NS['p']+'}'
    ET.register_namespace('',plans.NS['p'])
    root=ET.Element(ns+'ShowPlanXML',Build=build)
    stmt=ET.SubElement(root,ns+'StmtSimple',StatementText=statement or plans.statement(32))
    query=ET.SubElement(stmt,ns+'QueryPlan',DegreeOfParallelism='0')
    top=ET.SubElement(query,ns+'RelOp',NodeId='0',PhysicalOp='Top',LogicalOp='Top')
    runtime=ET.SubElement(top,ns+'RunTimeInformation');ET.SubElement(runtime,ns+'RunTimeCountersPerThread',ActualRows='1',Thread='0')
    scan=ET.SubElement(top,ns+'RelOp',NodeId='1',PhysicalOp='Clustered Index Scan',LogicalOp='Clustered Index Scan')
    runtime=ET.SubElement(scan,ns+'RunTimeInformation');ET.SubElement(runtime,ns+'RunTimeCountersPerThread',ActualRows=str(rows),Thread='0')
    ET.SubElement(scan,ns+'Object',Database=database,Schema='lab',Table='V32',Index='OwnSyntheticPK')
    return f'{result}|0.0\n'+ET.tostring(root,encoding='unicode')

class NegativeEvidence(unittest.TestCase):
    def reject(self,value):
        with self.assertRaises((ValueError,RuntimeError,ET.ParseError)):plans.capture(value,32)
    def test_complete_synthetic_positive_missing_memory_visible(self):
        data=plans.capture(fixture(),32)
        self.assertEqual(data['statement_metrics']['memory_grant'],{'state':'NOT_CAPTURED','attributes':None})
    def test_foreign_database(self):self.reject(fixture(database='OTHER_SYNTHETIC_DB'))
    def test_missing_source_row(self):self.reject(fixture(rows=99))
    def test_wrong_actual_result(self):self.reject(fixture(result=2))
    def test_wrong_build(self):self.reject(fixture(build='17.0.0.0'))
    def test_wrong_statement(self):self.reject(fixture(statement='SELECT 1;'))
    def test_missing_runtime(self):self.reject(fixture().replace('ActualRows="100"','EstimatedRows="100"'))
    def test_duplicate_plan(self):self.reject(fixture()+fixture().split('\n',1)[1])
    def test_xml_entity(self):self.reject('<!DOCTYPE x [<!ENTITY test "synthetic">]>'+fixture())
    def test_truncated_plan(self):self.reject(fixture()[:-12])
    def test_missing_result(self):self.reject(fixture().split('\n',1)[1])
    def test_actual_padded_native_row(self):plans.capture(fixture().replace('1|0.0\n','Id        |DistanceValue\n----------|-------------\n         1|   0.0\n'),32)
    def test_duplicate_actual_result(self):self.reject('1|0.0\n'+fixture())
    def test_additional_null_distance(self):self.reject('2|NULL\n'+fixture())
    def test_additional_null_identity(self):self.reject(fixture()+'\nNULL|0.0')
    def test_additional_malformed_distance(self):self.reject(fixture()+'\n2|BAD')
    def test_additional_three_column_frame(self):self.reject(fixture()+'\n1|0.0|extra')
    def test_header_after_result(self):self.reject(fixture()+'\nId|DistanceValue')
    def test_unbound_separator(self):self.reject('----------|-------------\n'+fixture())
    def test_known_summary(self):plans.capture(fixture()+'\nSQLPERF_SUMMARY|PASS|OK',32)
    def test_duplicate_thread_source_sum(self):
        value=fixture().replace('ActualRows="100" Thread="0"','ActualRows="50" Thread="0"')
        needle='<RunTimeCountersPerThread ActualRows="50" Thread="0" />'
        self.assertIn(needle,value);self.reject(value.replace(needle,needle+needle))
    def test_missing_thread_identity(self):self.reject(fixture().replace(' Thread="0"',''))
    def test_inner_one_cannot_replace_result_root(self):
        value=fixture().replace('ActualRows="1" Thread="0"','ActualRows="2" Thread="0"',1)
        needle='</QueryPlan>'
        # An unrelated inner one-row operator cannot attest the actual root.
        inner='<RelOp NodeId="2"><RunTimeInformation><RunTimeCountersPerThread ActualRows="1" Thread="0" /></RunTimeInformation></RelOp>'
        self.reject(value.replace('</RelOp></QueryPlan>',inner+'</RelOp></QueryPlan>'))
    def test_missing_root_runtime_with_inner_one(self):
        value=fixture().replace('<RunTimeInformation><RunTimeCountersPerThread ActualRows="1" Thread="0" /></RunTimeInformation>','',1)
        inner='<RelOp NodeId="2"><RunTimeInformation><RunTimeCountersPerThread ActualRows="1" Thread="0" /></RunTimeInformation></RelOp>'
        self.reject(value.replace('</RelOp></QueryPlan>',inner+'</RelOp></QueryPlan>'))

if __name__=='__main__':unittest.main()
