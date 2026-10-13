"""Fiktive Layouts; keine historischen Auswertungen oder DLL-Aufrufe."""
import copy
import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import vector_client_layout_evidence as m


def fake_sha(name): return hashlib.sha256(('SYNTHETIC:'+name).encode()).hexdigest()


def fixture(nested=False):
    targets={m.APP:{'dependencies':{'Microsoft.Data.SqlClient':'6.1.4'},'runtime':{'VectorClient.dll':{}}}}
    libraries={m.APP:{'type':'project','serviceable':False,'sha512':''}}
    files=[];rt_paths={}
    for leaf, origin in m.ORIGINS.items():
        _,name,version,*bits=origin.split('/');relative='/'.join(bits)
        key=('Microsoft.Data.SqlClient' if name=='microsoft.data.sqlclient' else name)+'/'+version
        targets.setdefault(key,{})
        libraries[key]={'type':'package','serviceable':True,'sha512':'sha512-SYNTHETIC','path':name+'/'+version,'hashPath':name+'.'+version+'.nupkg.sha512'}
        if relative.startswith('runtimes/'):
            rid=relative.split('/')[1];kind='native' if '/native/' in relative else 'runtime'
            targets[key].setdefault('runtimeTargets',{})[relative]={'rid':rid,'assetType':kind,'fileVersion':'1.0.0.0'}
            rt_paths[leaf]=relative
            if kind=='runtime':
                # Der generische Fallback darf das ausgewählte Windowsasset nicht ersetzen.
                generic='/'.join(relative.split('/')[2:])
                targets[key].setdefault('runtime',{})[generic]={'fileVersion':'1.0.0.0'}
        else: targets[key].setdefault('runtime',{})[relative]={'fileVersion':'1.0.0.0'}
        files.append({'path':relative if nested and leaf in rt_paths else leaf,'bytes':256,'sha256':fake_sha(leaf)})
    targets['Microsoft.Data.SqlClient/6.1.4']['resources']=copy.deepcopy(m.RESOURCES)
    deps={'runtimeTarget':{'name':m.TARGET,'signature':''},'compilationOptions':{},'targets':{m.TARGET:targets},'libraries':libraries}
    proof={k:fake_sha(k) for k in m.PROOF_FIELDS}
    proof.update(stage='BEFORE_COMPILER_POPEN',asset_origins=dict(m.ORIGINS),copied_asset_sha256={leaf:fake_sha(leaf) for leaf in m.ORIGINS},configured_argv=['SYNTHETIC_COMPILER'],reference_sha256={'SYNTHETIC_REF':fake_sha('reference')},implementation_sha256={'SYNTHETIC_SOURCE':fake_sha('source')},source_sha256={'SYNTHETIC_INPUT':fake_sha('input')})
    binding={'consumer_sources':m.source_binding(),'artifact_sha256':{'deps':'','compiler_proof':'','app_component':fake_sha('app')},'provenance':'PUREFIXTURE_ONLY'}
    files.extend([{'path':'VectorClient.dll','bytes':512,'sha256':fake_sha('app')},{'path':'VectorClient.deps.json','bytes':1,'sha256':'0'*64},{'path':'VectorClient.runtimeconfig.json','bytes':125,'sha256':proof['runtimeconfig_sha256']}])
    return deps,proof,files,binding


def encode(d,p,f,b):
    db=json.dumps(d,separators=(',',':')).encode('utf-8');p['deps_sha256']=hashlib.sha256(db).hexdigest()
    pb=json.dumps(p,separators=(',',':')).encode('utf-8')
    b['artifact_sha256'].update(deps=hashlib.sha256(db).hexdigest(),compiler_proof=hashlib.sha256(pb).hexdigest())
    for row in f:
        if row['path']=='VectorClient.deps.json': row.update(bytes=len(db),sha256=b['artifact_sha256']['deps'])
    return db,pb,f,b


class LayoutTests(unittest.TestCase):
    def reject(self, change, code=None):
        d,p,f,b=fixture();change(d,p,f,b)
        args=encode(d,p,f,b)
        with self.assertRaises((ValueError,TypeError,UnicodeError)) as caught:m.report(*args)
        if code is not None:self.assertEqual(str(caught.exception),code)

    def test_flat_fixture_warns_about_five_literal_paths_without_loader_claim(self):
        out=m.report(*encode(*fixture()))
        self.assertEqual(out['layout'],'RELATIVE_PATHS_ABSENT_FLAT_BYTES_PRESENT')
        self.assertEqual(out['counts']['runtime_target_paths_missing'],5)
        self.assertEqual(out['counts']['flat_sha_bound_assets'],28)
        self.assertEqual(out['outcome'],'WARN');self.assertEqual(out['claims']['file_not_found_origin'],'UNPROVEN')
        self.assertEqual(out['claims']['loader'],'NOT_ESTABLISHED')
        for value in m.ORIGINS.values():self.assertNotIn(value,m.canonical(out))

    def test_relative_fixture_is_source_coherent_without_runtime_pass(self):
        out=m.report(*encode(*fixture(True)))
        self.assertEqual(out['counts']['runtime_target_paths_present'],5)
        self.assertEqual(out['counts']['flat_sha_bound_assets'],23)
        self.assertEqual(out['outcome'],'WARN');self.assertEqual(out['claims']['sql'],'NOT_ESTABLISHED')

    def test_thirteen_resource_descriptors_do_not_attest_satellite_inventory(self):
        d,p,f,b=fixture();out=m.report(*encode(d,p,f,b))
        self.assertEqual(len(d['targets'][m.TARGET]['Microsoft.Data.SqlClient/6.1.4']['resources']),13)
        self.assertEqual(out['counts']['selected_assets'],28)
        self.assertEqual(out['counts']['app_files'],31)
        self.assertFalse(any(row['path'].endswith('.resources.dll') for row in f))
        self.assertEqual(out['claims']['loader'],'NOT_ESTABLISHED')
        self.assertEqual(out['outcome'],'WARN')

    def test_resource_missing_extra_foreign_locale_and_type_fail_closed(self):
        key='Microsoft.Data.SqlClient/6.1.4';rel='lib/net9.0/de/Microsoft.Data.SqlClient.resources.dll'
        self.reject(lambda d,p,f,b:d['targets'][m.TARGET][key].pop('resources'))
        self.reject(lambda d,p,f,b:d['targets'][m.TARGET][key]['resources'].pop(rel))
        self.reject(lambda d,p,f,b:d['targets'][m.TARGET][key]['resources'].update({'lib/net9.0/foreign/Microsoft.Data.SqlClient.resources.dll':{'locale':'foreign'}}))
        for val in ('fr','DE','de ',None,True,1):
            self.reject(lambda d,p,f,b,v=val:d['targets'][m.TARGET][key]['resources'][rel].update(locale=v))
        self.reject(lambda d,p,f,b:d['targets'][m.TARGET][key]['resources'][rel].update(extra='UNEXPECTED'))
        self.reject(lambda d,p,f,b:d['targets'][m.TARGET]['azure.core/1.50.0'].update(resources=copy.deepcopy(m.RESOURCES)))
        self.reject(lambda d,p,f,b:f[0].update(path=rel))

    def test_package_population_version_dependency_and_root_are_exact(self):
        self.reject(lambda d,p,f,b:d['targets'][m.TARGET].pop('azure.core/1.50.0'))
        self.reject(lambda d,p,f,b:d['targets'][m.TARGET][m.APP]['dependencies'].update({'Microsoft.Data.SqlClient':'6.1.3'}))
        self.reject(lambda d,p,f,b:d['targets'][m.TARGET]['azure.core/1.50.0'].update(dependencies={'FOREIGN_PACKAGE':'1.0.0'}))
        self.reject(lambda d,p,f,b:d['runtimeTarget'].update(name='FOREIGN_RUNTIME'))

    def test_windows_rid_selection_native_sni_and_managed_override(self):
        self.reject(lambda d,p,f,b:d['targets'][m.TARGET]['Microsoft.Data.SqlClient/6.1.4']['runtimeTargets']['runtimes/win/lib/net9.0/Microsoft.Data.SqlClient.dll'].update(rid='linux'))
        key='microsoft.data.sqlclient.sni.runtime/6.0.2'
        self.reject(lambda d,p,f,b:d['targets'][m.TARGET][key]['runtimeTargets']['runtimes/win-x64/native/Microsoft.Data.SqlClient.SNI.dll'].update(rid='win-arm64'))
        self.reject(lambda d,p,f,b:p['asset_origins'].update({'Microsoft.Data.SqlClient.dll':'packages/microsoft.data.sqlclient/6.1.4/ref/net9.0/Microsoft.Data.SqlClient.dll'}))

    def test_path_traversal_absolute_case_alias_and_extra_inventory_rejected(self):
        for path in ('../FOREIGN.dll','/FOREIGN.dll','C:/FOREIGN.dll','runtimes//FOREIGN.dll','Microsoft.Data.Sqlclient.dll'):
            self.reject(lambda d,p,f,b,v=path:f[0].update(path=v))
        self.reject(lambda d,p,f,b:f.append(copy.deepcopy(f[0])))
        self.reject(lambda d,p,f,b:f[0].update(path='FOREIGN.dll'))
        self.reject(lambda d,p,f,b:d['targets'][m.TARGET]['azure.core/1.50.0']['runtime'].update({'../FOREIGN.dll':{}}))

    def test_selected_basename_collision_cannot_hide_second_package(self):
        self.reject(lambda d,p,f,b:d['targets'][m.TARGET]['azure.core/1.50.0']['runtime'].update({'lib/net8.0/Microsoft.Data.SqlClient.dll':{}}),'SELECTED_BASENAME_COLLISION')
        d,p,f,b=fixture(True);f[0]['path']=f[1]['path']
        with self.assertRaises(ValueError):m.report(*encode(d,p,f,b))

    def test_full_asset_sha_bootstrap_pins_and_null_bool_metadata(self):
        self.reject(lambda d,p,f,b:f[0].update(sha256='f'*64),'COMPLETE_SELECTED_ASSET_BYTES')
        self.reject(lambda d,p,f,b:p['copied_asset_sha256'].pop(next(iter(m.ORIGINS))))
        self.reject(lambda d,p,f,b:p.update(runtimeconfig_sha256=True))
        self.reject(lambda d,p,f,b:p.update(source_sha256=None))
        self.reject(lambda d,p,f,b:p['reference_sha256'].update(SYNTHETIC_REF=True))
        self.reject(lambda d,p,f,b:p.update(configured_argv=[True]))
        for val in (True,256.0,None,0):self.reject(lambda d,p,f,b,v=val:f[0].update(bytes=v))
        self.reject(lambda d,p,f,b:f[-1].update(sha256='f'*64),'FULL_APP_BOOTSTRAP_PINS')

    def test_original_json_bytes_not_canonical_or_caller_flag_are_pinned(self):
        d,p,f,b=fixture();db,pb,f,b=encode(d,p,f,b)
        with self.assertRaises(ValueError):m.report(db+b' ',pb,f,b)
        with self.assertRaises(ValueError):m.report(db,pb,f,{**b,'attested':True})
        b['artifact_sha256']['compiler_proof']='f'*64
        with self.assertRaises(ValueError):m.report(db,pb,f,b)

    def test_fixed_historical_binding_does_not_accept_synthetic_metadata_as_actual(self):
        self.reject(lambda d,p,f,b:b.update(provenance='DECLARED_PRIVATE_FILE_METADATA'),'FIXED_PR229_ARTIFACT_PINS')
        self.reject(lambda d,p,f,b:b['consumer_sources'].update(extra='f'*64))
        self.reject(lambda d,p,f,b:b.update(provenance='ATTESTED_RUNTIME_PASS'))

    def test_plain_types_duplicate_json_and_null_shapes_are_rejected(self):
        d,p,f,b=fixture();db,pb,f,b=encode(d,p,f,b)
        for bad in (None,[],type('dict',(dict,),{})(b)):
            with self.assertRaises(ValueError):m.report(db,pb,f,bad)
        self.reject(lambda d,p,f,b:d.update(libraries=None))
        self.reject(lambda d,p,f,b:d['libraries'][m.APP].update(serviceable=0), 'FIXED_PROJECT_LIBRARY')
        self.reject(lambda d,p,f,b:d['targets'][m.TARGET]['azure.core/1.50.0'].update(runtime=True))
        with self.assertRaises(ValueError):m.load(b'{"a":1,"a":2}')
        with self.assertRaises(ValueError):m.load(b'{"a":NaN}')

    def test_contract_claim_count_origin_and_raw_extra_drift_are_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/'fixture.json'
            for mutate in (lambda x:x['claims'].update(loader='PASS'),lambda x:x['profile'].update(selected_assets=True),lambda x:x.update(raw_export='FORBIDDEN'),lambda x:x['selected_origins'].pop(next(iter(m.ORIGINS)))):
                data=copy.deepcopy(m.EXPECTED);mutate(data);path.write_bytes(json.dumps(data).encode())
                with patch.object(m,'CONTRACT',path):
                    with self.assertRaisesRegex(ValueError,'FIXED_CONTRACT_DRIFT'):m.contract()

    def test_inputs_and_nested_shapes_are_bounded_before_graph_processing(self):
        for raw in (b'',b' '*100001,'{}',bytearray(b'{}')):
            with self.assertRaises(ValueError):m.load(raw)
        deep=0
        for i in range(14):deep={'x':deep}
        with self.assertRaises(ValueError):m.load(json.dumps(deep).encode())
        self.reject(lambda d,p,f,b:f[0].update(extra='UNEXPECTED'))


if __name__=='__main__':unittest.main()
