"""Öffentliche feste DDL-/Snapshot-Eingaben, rein synthetisch ohne Client."""
import json,sys,unittest
from unittest.mock import patch
import dgn010_cost_inputs as inputs
from test_dgn010_cost_evidence import lease

class FixedInputTests(unittest.TestCase):
    def build(self,**changes):
        return inputs.build_sql(**({'database_id':7,'object_id':100,'kind':'CREATE','cycle':1,'held_lease':inputs.costs.EMPTY}|changes))

    def test_fixed_create_drop_and_no_unbound_values(self):
        for kind,held in (('CREATE',inputs.costs.EMPTY),('DROP',lease())):
            sql=self.build(kind=kind,held_lease=held)
            self.assertNotIn('$(',sql)
            self.assertIn("@RawKind nvarchar(max)=N'"+kind+"'",sql)
            self.assertIn("IF ISNULL(OBJECT_ID(N'lab.SourceRows'),-1)<>100",sql)
            self.assertIn("@Cycle int=1",sql)
            self.assertLess(sql.index('Vollstaendige Gegenprobenbindung verloren'),sql.index('EXEC sys.sp_executesql @Ddl'))
            self.assertIn("WITH(MAXDOP=1)",sql)
            self.assertIn("DGN010_BUILDPART|",sql)
            self.assertIn("@Ended<@Started",sql)

    def test_all_four_complete_marker_guards_precede_mutation(self):
        sql=self.build()
        for name,value in inputs.markers.MARKERS.items():
            self.assertIn(inputs.markers.match(name,value),sql)
        self.assertIn("DB_ID()<> 7",sql)
        self.assertIn("DATALENGTH(DB_NAME())",sql)
        self.assertIn("minor_id=0)=4",sql)
        self.assertIn("DATALENGTH(@LeaseBefore)<>DATALENGTH(@Held)",sql)
        self.assertLess(sql.index('Full held own index catalog differs'),sql.index('SET @Started=SYSUTCDATETIME()'))

    def test_ids_cycle_and_kind_reject_aliases_and_sql_input(self):
        for changes in ({'database_id':True},{'database_id':4},{'object_id':0},{'object_id':2147483648},{'cycle':True},{'cycle':3},{'kind':'CREATE '},{'kind':"DROP';SELECT 1;--"},{'database_id':'7;SELECT 1'}):
            with self.subTest(changes=changes),self.assertRaises(ValueError):self.build(**changes)

    def test_native_lease_population_and_foreign_input_rejected(self):
        invalid=json.loads(lease());invalid['indexes'][0]['name']="DGN010_OwnCandidate';SELECT 1;--"
        for kind,held in (('DROP',inputs.costs.EMPTY),('CREATE',lease()),('DROP',json.dumps(invalid)),('DROP','{}'),('CREATE',inputs.costs.EMPTY+' ')):
            with self.subTest(kind=kind,held=held),self.assertRaises(ValueError):self.build(kind=kind,held_lease=held)

    def test_snapshot_full_shape_and_source_binding(self):
        sql=inputs.state_sql(database_id=7,object_id=100)
        self.assertTrue(sql.endswith(inputs.markers.STATE_SQL))
        self.assertIn("IF ISNULL(OBJECT_ID(N'lab.SourceRows'),-1)<>100",sql)
        for part in inputs.costs.STATE_KEYS:self.assertIn('AS '+part,sql)
        self.assertIn('Snapshotgroesse',sql)
        with self.assertRaises(ValueError):inputs.state_sql(database_id=7,object_id=True)

    def test_building_inputs_never_starts_process(self):
        with patch('subprocess.Popen',side_effect=AssertionError('No native client permitted')):
            self.build();inputs.state_sql(database_id=7,object_id=100)

if __name__=='__main__':unittest.main()
