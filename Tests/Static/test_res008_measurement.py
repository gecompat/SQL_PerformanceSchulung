"""Gezielte negative Evidenzfälle; kein SQL- oder Runtimeersatz."""
import copy,json,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'Demos/09_AI_SQL_Server_2025/RES-008_Vector_Dimensions'))
import res008_measurement as m

def fixture():
    identity={'SessionId':57,'RequestId':0,'RequestStartTime':'2026-10-12T01:00:00.000','ConnectionId':'00000000-0000-0000-0000-000000000001','DatabaseId':5}
    before=dict(identity,CpuMs=100,Reads=10,LogicalReads=50,Writes=0)
    after=dict(identity,CpuMs=102,Reads=11,LogicalReads=80,Writes=0)
    return dict(identity,Dimension=32,Statements=1,CpuMs=2,Reads=1,LogicalReads=30,Writes=0,ElapsedUs=100000,StartedUtc='2026-10-12T01:00:01.0000000',EndedUtc='2026-10-12T01:00:01.1000000',CountersBefore=before,CountersAfter=after,Queries=[{'Ordinal':1,'Id':1,'DistanceValue':0.0}])

class EvidenceCases(unittest.TestCase):
    def check(self,value):return m.validate(value,32,1,5)
    def test_actual_positive(self):self.check(fixture())
    def test_foreign_snapshot_connection(self):
        v=fixture();v['CountersAfter']['ConnectionId']='00000000-0000-0000-0000-000000000002'
        with self.assertRaises(ValueError):self.check(v)

    def make(self):
        text=json.dumps(fixture(),separators=(',',':'));parts=[text[n:n+200] for n in range(0,len(text),200)]
        return [f'RES008_WINDOWPART|{n}|{len(parts)}|{len(text)}|{part}' for n,part in enumerate(parts,1)]
    def test_long_actual_transport(self):self.assertEqual(m.decode('\n'.join(self.make())),fixture())
    def test_missing_part(self):
        with self.assertRaises(ValueError):m.decode('\n'.join(self.make()[:-1]))
    def test_truncated_part(self):
        lines=self.make();lines[1]=lines[1][:-1]
        with self.assertRaises(ValueError):m.decode('\n'.join(lines))
    def test_reordered_parts(self):
        lines=self.make();lines[0],lines[1]=lines[1],lines[0]
        with self.assertRaises(ValueError):m.decode('\n'.join(lines))
    def test_duplicate_part(self):
        lines=self.make();lines.insert(1,lines[0])
        with self.assertRaises(ValueError):m.decode('\n'.join(lines))
    def test_internally_consistent_foreign_db(self):
        v=fixture();v['DatabaseId']=6
        for k in ('CountersBefore','CountersAfter'):v[k]['DatabaseId']=6
        with self.assertRaises(ValueError):self.check(v)
    def test_falling_counter(self):
        v=fixture();v['CountersAfter']['CpuMs']=99;v['CpuMs']=-1
        with self.assertRaises(ValueError):self.check(v)
    def test_fabricated_delta(self):
        v=fixture();v['LogicalReads']=0
        with self.assertRaises(ValueError):self.check(v)
    def test_reversed_time(self):
        v=fixture();v['EndedUtc']='2026-10-12T01:00:00';v['ElapsedUs']=0
        with self.assertRaises(ValueError):self.check(v)
    def test_fabricated_elapsed(self):
        v=fixture();v['ElapsedUs']=100001
        with self.assertRaises(ValueError):self.check(v)
    def test_missing_query(self):
        v=fixture();v['Queries']=[]
        with self.assertRaises(ValueError):self.check(v)
    def test_wrong_actual_row(self):
        v=fixture();v['Queries'][0]['Id']=2
        with self.assertRaises(ValueError):self.check(v)
    def test_nonfinite_distance(self):
        v=fixture();v['Queries'][0]['DistanceValue']=float('nan')
        with self.assertRaises(ValueError):self.check(v)
    def test_boolean_counter(self):
        v=fixture();v['CountersBefore']['Writes']=False
        with self.assertRaises(ValueError):self.check(v)
    def test_boolean_snapshot_request_identity(self):
        v=fixture();v['CountersAfter']['RequestId']=False
        with self.assertRaises(ValueError):self.check(v)
    def test_actual_rounded_request_identity(self):
        v=fixture();v['RequestStartTime']='2026-10-12T02:02:42.750'
        for k in ('CountersBefore','CountersAfter'):v[k]['RequestStartTime']=v['RequestStartTime']
        v.update(StartedUtc='2026-10-12T02:02:42.7493218',EndedUtc='2026-10-12T02:02:42.7575834',ElapsedUs=8262)
        self.check(v)

if __name__=='__main__':unittest.main()
