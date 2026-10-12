"""Gezielte synthetische Poolrecord-Gegenfälle; kein Runtime- oder Privatimport."""
import copy,hashlib,json,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
import con010_pool_evidence as c
TOKEN='0123456789ABCDEF';SIDS={k:hashlib.sha256(k.encode()).hexdigest()[:32].upper() for k in c.LOGINS}
CONTRACT=json.loads(c.CONTRACT_PATH.read_text(encoding='utf-8'))

def text_bytes(text):
    raw=text.encode('utf-16-le');return len(raw),raw.hex().upper()

def full_state():
    defaults={'str':'LAB','int':0,'bool':False,'NoneType':None}
    counts={'db':1,'config':41,'files':2,'schemas':2,'objects':4,'indexes':1,'index_columns':1,'columns':4,'policies':1,'predicates':1,'modules':1,'rows':2,'properties':4}
    s={k:[{field:defaults[t] for field,t in shape.items()} for _ in range(counts[k])] for k,shape in CONTRACT['state_types'].items()}
    s['db']=[{'database_id':5,'name':c.DATABASE,'compatibility_level':170,'recovery_model_desc':'SIMPLE','owner_sid':'AQ=='}]
    for n,r in enumerate(s['config'],1):r.update(configuration_id=n,name='CFG'+str(n),value_type='int',value_bytes=4,value_hex='00000000')
    for n,r in enumerate(s['files'],1):r.update(file_id=n,type=n-1,name='LAB_FILE'+str(n),guid=f'00000000-0000-0000-0000-{n:012x}',max_size=32768,size=128,growth=2048)
    s['schemas']=[{'schema_id':2,'name':'lab','principal_id':1},{'schema_id':3,'name':'sec','principal_id':1}]
    stamp='2026-10-12T01:00:00.001'
    s['objects']=[{'object_id':oid,'schema_id':schema,'parent_object_id':parent,'name':name,'type':kind,'create_date':stamp,'modify_date':stamp} for oid,schema,parent,name,kind in ((100,2,0,'Documents','U '),(101,2,100,'LAB_PK','PK'),(102,3,0,'TenantPredicate','IF'),(103,3,0,'TenantPolicy','SP'))]
    s['indexes'][0].update(object_id=100,index_id=1,name='LAB_PK',type=1,is_unique=True,is_primary_key=True)
    s['index_columns'][0].update(object_id=100,index_id=1,index_column_id=1,column_id=1,key_ordinal=1)
    for n,(r,name) in enumerate(zip(s['columns'],('Id','TenantId','Content','V')),1):r.update(object_id=100,column_id=n,name=name)
    s['columns'][3].update(vector_dimensions=3,vector_base_type=0)
    s['policies'][0].update(object_id=103,is_enabled=True,is_schema_bound=True)
    s['predicates'][0].update(object_id=103,security_predicate_id=1,target_object_id=100,predicate_definition='[sec].[TenantPredicate]([TenantId])',predicate_type=0)
    s['modules'][0].update(object_id=102,definition='Synthetische eingefrorene RLS-Definition',is_schema_bound=True)
    for n,lane in enumerate(('A','B'),1):
        size,raw=text_bytes('Synthetische Quelle '+lane)
        s['rows'][n-1]={'Id':n,'TenantId':n,'ContentBytes':size,'ContentHex':raw,'VectorJson':'[1,0,0]'}
    for r,(name,value) in zip(s['properties'],{'SQLPERF.Project':'SQL_PerformanceSchulung','SQLPERF.ContractVersion':'1.0','SQLPERF.DemoId':'CON-010','SQLPERF.RunToken':'TENANTPOOL'}.items()):
        a,b=text_bytes(name);v,h=text_bytes(value);r.update(name_bytes=a,name_hex=b,value_bytes=v,value_hex=h,base_type='nvarchar')
    p={k:[] for k in ('Logins','ServerPermissions','ServerRoles','Users','DatabasePermissions','DatabaseRoles')}
    for n,lane in enumerate(c.LOGINS,1):
        login,user=c.LOGINS[lane];nb,nh=text_bytes(login);ub,uh=text_bytes(user)
        p['Logins'].append({'principal_id':10+n,'name':login,'name_bytes':nb,'name_hex':nh,'sid':SIDS[lane],'type':'S','type_desc':'SQL_LOGIN','is_disabled':False,'create_date':stamp,'modify_date':stamp,'default_database_name':c.DATABASE,'default_language_name':'us_english','credential_id':None,'is_fixed_role':False,'is_policy_checked':False,'is_expiration_checked':False})
        p['Users'].append({'principal_id':20+n,'name':user,'name_bytes':ub,'name_hex':uh,'sid':SIDS[lane],'type':'S','authentication_type':1,'default_schema_name':'dbo','is_fixed_role':False,'create_date':stamp,'modify_date':stamp})
        for group,cls,major,kind,name,grantee in (('ServerPermissions',100,0,'COSQ','CONNECT SQL',10+n),('DatabasePermissions',0,0,'CO  ','CONNECT',20+n),('DatabasePermissions',1,100,'SL  ','SELECT',20+n)):
            b,h=text_bytes(name);r={'class':cls,'major_id':major,'grantee_principal_id':grantee,'grantor_principal_id':1,'type':kind,'permission_name':name,'permission_bytes':b,'permission_hex':h,'state':'G'}
            if group=='DatabasePermissions':r['minor_id']=0
            p[group].append(r)
    encoded=json.dumps(p,separators=(',',':')).encode('utf-16-le')
    s.update(Principals=p,PrincipalBytes=len(encoded),PrincipalHex=encoded.hex().upper());return s

def frames(data):
    text=json.dumps(data,ensure_ascii=True,separators=(',',':'));count=(len(text)+199)//200
    return ''.join(f'TENANTPOOL_PART|{n+1}|{count}|{len(text)}|'+text[n*200:(n+1)*200].encode('utf-16-le').hex().upper()+'\n' for n in range(count))+'SQLPERF_SUMMARY|PASS|OK\n'

def pooled():
    records=[]
    for ordinal,lane in enumerate(c.ORDER,1):
        n={'A':1,'B':2,'U':3}[lane];login,user=c.LOGINS[lane]
        identity={'DatabaseId':5,'DatabaseName':c.DATABASE,'SuserName':login,'OriginalLogin':login,'UserName':user,'ServerSid':SIDS[lane],'OriginalSid':SIDS[lane],'UserSid':SIDS[lane],'SessionId':50+n}
        rows=[]
        if lane!='U':
            size,h=text_bytes('Synthetische Quelle '+lane);rows=[{'Id':n,'TenantId':n,'Content':'Synthetische Quelle '+lane,'ContentBytes':size,'ContentHex':h,'VectorJson':'[1,0,0]','Dimensions':3,'BaseType':'float32','Distance':0.0}]
        before={'Identity':identity,'Rows':rows,'Context':None};after=copy.deepcopy(before);after['Context']=2 if lane=='A' else 1
        owner={'SessionId':50+n,'ConnectionId':f'00000000-0000-0000-0000-{n:012x}','ConnectTime':'2026-10-12T01:00:00.001','LoginTime':'2026-10-12T01:00:01.001','LoginName':login,'OriginalLoginName':login,'Sid':SIDS[lane],'DatabaseId':5,'ProgramName':'SQLPERF_TENANTPOOL_'+TOKEN+'_'+lane,'NetTransport':'TCP','AuthScheme':'SQL'}
        records.append({'Ordinal':ordinal,'Lane':lane,'ClientConnectionId':f'11111111-0000-0000-0000-{ordinal:012x}','ConnectionState':'Open','PoolKeySha':hashlib.sha256(lane.encode()).hexdigest().upper(),'CredentialOrdinal':n,'Before':before,'After':after,'Owner':owner})
    return {'Status':'PASS','RequestEnd':'RESPONSE_RECEIVED','PoolCleanup':'ACTUAL_CLEAR_CLOSE_AND_NEW_ABSENCE','Records':records,'RemainingConnections':[],'Token':TOKEN,'Fault':None}

def artifact(text):return {'RawText':text,'Sha256':hashlib.sha256(text.encode()).hexdigest()}
def fixture():
    sources={key:hashlib.sha256(('SYNTHETIC|'+key).encode()).hexdigest() for key in CONTRACT['source_keys']};state=full_state()
    parent={k:({'int':1,'str':'LAB','dict':{},'bool':True,'float':0.25,'NoneType':None}[t]) for k,t in c.PARENT_TYPES.items()}
    parent.update(slot='2025-tenant-pool-1',token=TOKEN,name='sqlperf-tenant-pool-'+'a'*32,image=c.IMAGE,source=sources,version='17.0.5005.3',phase='PRIVATE_THREE_POOLS_SIX_CHECKOUTS_ONLY',measurement_path='SYNTHETIC_RECORD',cid='c'*64,client_end_unknown=False,sql_absence_evidence='ACTUAL_NEW_SQL_ABSENCE',native_count=2,native_count_semantics='CLIENT_HANDLE_STARTS')
    artifacts={k:artifact(v) for k,v in {'build':'17.0.5005.3\n','pool_receipt':json.dumps(pooled()),'parent_result':json.dumps(parent),'state_before':frames(state),'state_after':frames(state),'physical_absence':'TENANTPOOL_PHYSICAL|ABSENT\n','sql_absence_probe':'TENANTPOOL_ALL|ABSENT\n','sql_absence_parent':'TENANTPOOL_ALL|ABSENT\n'}.items()}
    native=[artifact('SYNTHETIC_RESPONSE_1'),artifact('SYNTHETIC_RESPONSE_2')]
    data={'scope':'PRIVATE_THREE_POOLS_SIX_CHECKOUTS_ONLY','source_sha256':sources,'artifacts':artifacts,'native_raw':native,'capture_ends':None,'input_sha256':None}
    binding={'database_id':5,'object_id':100,'token':TOKEN,'sids':dict(SIDS),'source_sha256':sources,'raw_sha256':{k:v['Sha256'] for k,v in artifacts.items()},'native_sha256':[v['Sha256'] for v in native],'input_sha256':None,'expected_contract_sha256':hashlib.sha256(c.CONTRACT_PATH.read_bytes()).hexdigest()}
    return data,binding

def replace_raw(data,binding,key,value):
    data['artifacts'][key]=artifact(value);binding['raw_sha256'][key]=data['artifacts'][key]['Sha256']

def change_pool(data,binding,change):
    value=json.loads(data['artifacts']['pool_receipt']['RawText']);change(value);replace_raw(data,binding,'pool_receipt',json.dumps(value))

class PoolContractTests(unittest.TestCase):
    def rejected(self,changes):
        for change in changes:
            with self.subTest(change=change):
                d,b=fixture();change(d,b)
                with self.assertRaises((ValueError,TypeError,KeyError)):c.report(d,binding=b)
    def test_review_capture_shape_omits_uncaptured_operation(self):
        d,b=fixture();self.assertEqual(c.report(d,binding=b)['record_validation'],'PASS')
        changed=full_state();changed['predicates'][0]['operation']=0
        for key in ('state_before','state_after'):replace_raw(d,b,key,frames(changed))
        with self.assertRaises(ValueError):c.report(d,binding=b)
    def test_review_actual_phase_literal_and_old_literal_rejected(self):
        d,b=fixture();self.assertEqual(c.report(d,binding=b)['status'],'WARN')
        self.rejected([lambda d,b:replace_raw(d,b,'parent_result',json.dumps({**json.loads(d['artifacts']['parent_result']['RawText']),'phase':'PRIVATE_THREE_POOLS_SIX_CHECKOUTS'}))])
    def test_review_tampered_contract_with_actual_new_sha_is_rejected(self):
        mutations=[lambda v:v['claims'].update(runtime_qualification='PASS'),lambda v:v['claims'].update(RawText='forbidden'),lambda v:v['expected_counts'].update(lanes=True),lambda v:v['expected_counts'].update(checkouts=7),lambda v:v.update(RawText='forbidden'),lambda v:v['state_types']['config'].update(configuration_id='bool')]
        for mutate in mutations:
            with self.subTest(mutate=mutate),tempfile.TemporaryDirectory() as folder:
                d,b=fixture();changed=copy.deepcopy(CONTRACT);mutate(changed)
                path=Path(folder)/'fixed-contract.json';path.write_text(json.dumps(changed),encoding='utf-8');b['expected_contract_sha256']=hashlib.sha256(path.read_bytes()).hexdigest()
                with patch.object(c,'CONTRACT_PATH',path),self.assertRaises(ValueError):c.report(d,binding=b)
    def test_review_plain_builtin_identity_before_contractread(self):
        disguised_dict=type('dict',(dict,),{});disguised_str=type('str',(str,),{})
        for record,binding in ((None,{}),({},None),(disguised_dict(),{}),({},disguised_dict())):
            with patch.object(c,'CONTRACT_PATH') as path:
                path.read_bytes.side_effect=AssertionError('Vor Typabweisung wurde gelesen')
                with self.assertRaises(ValueError):c.report(record,binding=binding)
                path.read_bytes.assert_not_called()
        d,b=fixture();d['artifacts']['pool_receipt']['RawText']=disguised_str(d['artifacts']['pool_receipt']['RawText'])
        with self.assertRaises(ValueError):c.report(d,binding=b)
    def test_positive_record_is_warn_with_missing_actual_capture_gates(self):
        d,b=fixture();out=c.report(d,binding=b)
        self.assertEqual((out['checkouts'],out['physical_reuse'],out['second_checkout_resets'],out['query_source_rows']),(6,3,3,8))
        self.assertEqual(out['status'],'WARN');self.assertEqual(out['missing_capture_gates'],2)
        for key in ('runtime_qualification','complete_public_closure','public_con010_qualification','tp_con'):self.assertEqual(out[key],'NOT_ESTABLISHED')
        self.assertEqual(out['caller_provenance'],'NOT_INDEPENDENTLY_ATTESTED')
    def test_exact_population_and_bool_aliases(self):
        self.rejected([lambda d,b:change_pool(d,b,lambda p:p['Records'].pop()),lambda d,b:change_pool(d,b,lambda p:p['Records'][0].update(Ordinal=True)),lambda d,b:change_pool(d,b,lambda p:p['Records'][0]['Owner'].update(DatabaseId=True)),lambda d,b:b.update(database_id=True),lambda d,b:d.pop('capture_ends')])
    def test_physical_poolkey_reset_and_full_source(self):
        self.rejected([lambda d,b:change_pool(d,b,lambda p:p['Records'][3]['Owner'].update(ConnectTime='2026-10-12T01:00:00.002')),lambda d,b:change_pool(d,b,lambda p:p['Records'][3]['Before'].update(Context=1)),lambda d,b:change_pool(d,b,lambda p:p['Records'][0]['After'].update(Rows=[])),lambda d,b:change_pool(d,b,lambda p:p['Records'][0]['After']['Rows'][0].update(Distance=1)),lambda d,b:change_pool(d,b,lambda p:p['Records'][0]['After']['Rows'][0].update(VectorJson='[true,0,0]'))])
    def test_actual_raw_source_and_expected_bindings(self):
        self.rejected([lambda d,b:d['artifacts']['state_before'].update(RawText='truncated'),lambda d,b:b.update(expected_contract_sha256='0'*64),lambda d,b:d['source_sha256'].update(SYNTHETIC_CALLER='d'*64),lambda d,b:d['native_raw'].pop(),lambda d,b:replace_raw(d,b,'sql_absence_parent','TENANTPOOL_ALL|ABSENT\nMsg 1, Level 16')])
        self.rejected([lambda d,b:(d['source_sha256'].pop('HOST/SqlClient'),b['source_sha256'].pop('HOST/SqlClient',None)),lambda d,b:b['sids'].update(B=b['sids']['A'])])
    def test_parent_flags_never_default_absence_or_end(self):
        for key,value in (('client_end_unknown',True),('db_absent',False),('principal_absent',False),('inputs_absent',False),('closed',1),('cleanup_seconds',float('nan'))):
            self.rejected([lambda d,b,k=key,v=value:replace_raw(d,b,'parent_result',json.dumps({**json.loads(d['artifacts']['parent_result']['RawText']),k:v}))])
    def test_full_state_marker_permissions_and_continuity(self):
        changes=[lambda s:s['objects'].clear(),lambda s:s['rows'][0].update(ContentHex='00'),lambda s:s['config'][0].update(configuration_id=True),lambda s:s['properties'][0].update(class_=0),lambda s:s['Principals']['DatabasePermissions'][0].update(type='CO')]
        for change in changes:
            self.rejected([lambda d,b,f=change:replace_raw(d,b,'state_after',frames((lambda s:(f(s),s)[1])(full_state())))])
    def test_client_guids_are_metadata_not_unproved_reuse_oracle(self):
        d,b=fixture();change_pool(d,b,lambda p:[r.update(ClientConnectionId='11111111-0000-0000-0000-000000000001') for r in p['Records']]);self.assertEqual(c.report(d,binding=b)['physical_reuse'],3)
    def test_output_exports_no_raw_identity_or_source_values(self):
        d,b=fixture();out=json.dumps(c.report(d,binding=b))
        for text in (TOKEN,SIDS['A'],'Synthetische Quelle','ConnectionId','SQLPERF_TENANTPOOL','ConnectTime','RawText','SQLPERF.Project'):self.assertNotIn(text,out)
    def test_full_opaque_native_population_cannot_replace_closure_texts(self):
        self.rejected([lambda d,b:replace_raw(d,b,'physical_absence',''),lambda d,b:replace_raw(d,b,'sql_absence_probe',''),lambda d,b:change_pool(d,b,lambda p:p.update(RequestEnd='UNKNOWN')),lambda d,b:change_pool(d,b,lambda p:p.update(RemainingConnections=[{}]))])
    def test_complete_synthetic_captures_are_still_unattested(self):
        d,b=fixture();d['capture_ends']=[{'Ordinal':n,'Kind':'POOL_CHILD' if n==2 else 'SQLCMD','ReturnCode':0,'ProcessEnd':'KNOWN','RequestEnd':'RESPONSE_RECEIVED','RawSha256':d['artifacts']['pool_receipt']['Sha256'] if n==2 else d['native_raw'][n]['Sha256']} for n in range(3)]
        d['input_sha256']=[{'Ordinal':n,'Kind':'POOL_CHILD' if n==2 else 'SQLCMD','InputSha256':str(n+1)*64} for n in range(3)];b['input_sha256']=copy.deepcopy(d['input_sha256'])
        out=c.report(d,binding=b);self.assertEqual(out['missing_capture_gates'],0);self.assertEqual(out['status'],'WARN');self.assertEqual(out['individual_request_end'],'DECLARED_NOT_INDEPENDENTLY_ATTESTED')
        self.assertEqual(out['runtime_qualification'],'NOT_ESTABLISHED')
        self.rejected([lambda d,b:d.update(capture_ends=True),lambda d,b:d.update(input_sha256=[]),lambda d,b:d.update(capture_ends=[])])
if __name__=='__main__':unittest.main()
