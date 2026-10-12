"""DGN-010: feste Markergegenproben auf einer neuen eigenen Fixture."""
import hashlib,json,math,os,tempfile,time
from pathlib import Path

MARKERS={'SQLPERF.Project':'SQL_PerformanceSchulung','SQLPERF.ContractVersion':'1.0','SQLPERF.DemoId':'DGN-010','SQLPERF.RunToken':'LOCAL'}
PHASES=('10_Setup.sql','20_Probe.sql','21_DeleteOwnRow.sql','22_Database.sql','24_Candidate.sql','40_SelectWindow.sql','50_DmlWindow.sql','90_Cleanup.sql')

def literal(value):return "N'"+value.replace("'","''")+"'"
def match(name,value):
    name_sql=f"DATALENGTH(name)=DATALENGTH({literal(name)}) AND CONVERT(varbinary(max),name)=CONVERT(varbinary(max),{literal(name)})"
    where='class=0 AND major_id=0 AND minor_id=0 AND '+name_sql
    if value is None:return f'NOT EXISTS(SELECT 1 FROM sys.extended_properties WHERE {where})'
    where+=f" AND DATALENGTH(CONVERT(nvarchar(max),value))=DATALENGTH({literal(value)}) AND CONVERT(varbinary(max),CONVERT(nvarchar(max),value))=CONVERT(varbinary(max),{literal(value)})"
    return f'(SELECT COUNT(*) FROM sys.extended_properties WHERE {where})=1'
def binding(markers,dbid):
    expected=sum(v is not None for v in markers.values())
    guard=' AND '.join(match(k,v) for k,v in markers.items())
    return f"SET NOCOUNT ON; IF DB_ID()<> {dbid} OR DATALENGTH(DB_NAME())<>DATALENGTH(N'SQLPERF_LAB_DGN010_LOCAL') OR CONVERT(varbinary(max),DB_NAME())<>CONVERT(varbinary(max),N'SQLPERF_LAB_DGN010_LOCAL') THROW 51004,'FAIL_STATE: Eigene DB-Bindung verloren.',1; IF CASE WHEN ({guard} AND (SELECT COUNT(*) FROM sys.extended_properties WHERE class=0 AND major_id=0 AND minor_id=0)={expected}) THEN 1 ELSE 0 END<>1 THROW 51004,'FAIL_STATE: Vollstaendige Gegenprobenbindung verloren.',1; "
def cases():
    for marker,value in MARKERS.items():
        for name,invalid in ((marker,None),(marker,'FOREIGN'),(marker,value+' '),(marker,value+'X'*256),(marker.lower(),value),(marker+' ',value)):
            yield marker,value,name,invalid

STATE_SQL="""
DECLARE @J nvarchar(max)=(SELECT
JSON_QUERY((SELECT database_id,name,compatibility_level,recovery_model_desc,is_auto_close_on,is_auto_shrink_on,is_read_only,state_desc FROM sys.databases WHERE database_id=DB_ID() FOR JSON PATH)) AS db,
JSON_QUERY((SELECT configuration_id,name,is_value_default,
CONVERT(nvarchar(128),SQL_VARIANT_PROPERTY(value,'BaseType')) AS value_type,
CONVERT(int,SQL_VARIANT_PROPERTY(value,'Precision')) AS value_precision,
CONVERT(int,SQL_VARIANT_PROPERTY(value,'Scale')) AS value_scale,
CONVERT(int,SQL_VARIANT_PROPERTY(value,'MaxLength')) AS value_max_length,
CONVERT(nvarchar(128),SQL_VARIANT_PROPERTY(value,'Collation')) AS value_collation,
DATALENGTH(CONVERT(varbinary(max),value)) AS value_bytes,
CONVERT(varchar(max),CONVERT(varbinary(max),value),2) AS value_hex,
CONVERT(nvarchar(128),SQL_VARIANT_PROPERTY(value_for_secondary,'BaseType')) AS secondary_type,
CONVERT(int,SQL_VARIANT_PROPERTY(value_for_secondary,'Precision')) AS secondary_precision,
CONVERT(int,SQL_VARIANT_PROPERTY(value_for_secondary,'Scale')) AS secondary_scale,
CONVERT(int,SQL_VARIANT_PROPERTY(value_for_secondary,'MaxLength')) AS secondary_max_length,
CONVERT(nvarchar(128),SQL_VARIANT_PROPERTY(value_for_secondary,'Collation')) AS secondary_collation,
DATALENGTH(CONVERT(varbinary(max),value_for_secondary)) AS secondary_bytes,
CONVERT(varchar(max),CONVERT(varbinary(max),value_for_secondary),2) AS secondary_hex
FROM sys.database_scoped_configurations ORDER BY configuration_id FOR JSON PATH,INCLUDE_NULL_VALUES)) AS config,
JSON_QUERY((SELECT file_id,name,type,size,max_size,growth,is_percent_growth,is_read_only,CONVERT(varchar(36),file_guid) AS guid FROM sys.database_files ORDER BY file_id FOR JSON PATH,INCLUDE_NULL_VALUES)) AS files,
JSON_QUERY((SELECT schema_id,name,principal_id FROM sys.schemas WHERE name=N'lab' ORDER BY schema_id FOR JSON PATH)) AS schemas,
JSON_QUERY((SELECT object_id,schema_id,name,type,create_date,modify_date FROM sys.objects WHERE schema_id=SCHEMA_ID(N'lab') ORDER BY object_id FOR JSON PATH)) AS objects,
JSON_QUERY((SELECT object_id,index_id,name,type,is_unique,is_primary_key,is_disabled,has_filter,filter_definition FROM sys.indexes WHERE object_id=OBJECT_ID(N'lab.SourceRows') ORDER BY index_id FOR JSON PATH,INCLUDE_NULL_VALUES)) AS indexes,
JSON_QUERY((SELECT object_id,index_id,index_column_id,column_id,key_ordinal,is_descending_key,is_included_column FROM sys.index_columns WHERE object_id=OBJECT_ID(N'lab.SourceRows') ORDER BY index_id,index_column_id FOR JSON PATH)) AS index_columns,
JSON_QUERY((SELECT object_id,column_id,name,system_type_id,user_type_id,max_length,precision,scale,collation_name,is_nullable,is_identity,is_computed,default_object_id FROM sys.columns WHERE object_id=OBJECT_ID(N'lab.SourceRows') ORDER BY column_id FOR JSON PATH,INCLUDE_NULL_VALUES)) AS columns,
JSON_QUERY((SELECT principal_id,name,CONVERT(varchar(max),sid,2) AS sid,type,authentication_type,default_schema_name,is_fixed_role FROM sys.database_principals WHERE name=N'DGN010_reader' FOR JSON PATH,INCLUDE_NULL_VALUES)) AS reader,
JSON_QUERY((SELECT class,major_id,minor_id,grantee_principal_id,grantor_principal_id,type,state FROM sys.database_permissions WHERE grantee_principal_id=USER_ID(N'DGN010_reader') ORDER BY class,major_id,minor_id,type FOR JSON PATH)) AS permissions,
JSON_QUERY(COALESCE((SELECT role_principal_id,member_principal_id FROM sys.database_role_members WHERE member_principal_id=USER_ID(N'DGN010_reader') ORDER BY role_principal_id FOR JSON PATH),N'[]')) AS roles,
JSON_QUERY((SELECT Id,Value,Payload,DATALENGTH(Payload) AS payload_bytes FROM lab.SourceRows ORDER BY Id FOR JSON PATH)) AS rows,
JSON_QUERY((SELECT class,major_id,minor_id,DATALENGTH(name) AS name_bytes,CONVERT(varchar(max),CONVERT(varbinary(max),name),2) AS name_hex,DATALENGTH(CONVERT(nvarchar(max),value)) AS value_bytes,CONVERT(varchar(max),CONVERT(varbinary(max),CONVERT(nvarchar(max),value)),2) AS value_hex,CONVERT(nvarchar(128),SQL_VARIANT_PROPERTY(value,'BaseType')) AS base_type FROM sys.extended_properties ORDER BY class,major_id,minor_id,CONVERT(varbinary(max),name) FOR JSON PATH)) AS properties
FOR JSON PATH,WITHOUT_ARRAY_WRAPPER);
DECLARE @Chars int=DATALENGTH(@J)/2,@N int,@Part int=1; SET @N=(@Chars+199)/200;
IF @Chars NOT BETWEEN 1 AND 200000 THROW 51003,'FAIL_RESULT_CONTRACT: Snapshotgroesse.',1;
WHILE @Part<=@N BEGIN SELECT CONCAT('DGN010_STATEPART|',@Part,'|',@N,'|',@Chars,'|',CONVERT(varchar(800),CONVERT(varbinary(400),SUBSTRING(@J,(@Part-1)*200+1,200)),2)); SET @Part+=1; END;
"""

def decode(output):
    lines=[s.strip() for s in output.splitlines() if s.strip()]
    frames=[s.split('|',4) for s in lines]
    if not frames or any(len(f)!=5 or f[0]!='DGN010_STATEPART' for f in frames):raise ValueError('Vollstaendige Snapshotframes fehlen')
    n,chars=int(frames[0][2]),int(frames[0][3]);encoded=''.join(f[4] for f in frames)
    if not 1<=chars<=200000 or n!=(chars+199)//200 or len(frames)!=n or len(encoded)!=chars*4 or any(c not in '0123456789ABCDEF' for c in encoded):raise ValueError('Snapshottrunkierung')
    if any(f[1:4]!=[str(i),str(n),str(chars)] or len(f[4])!=min(200,chars-(i-1)*200)*4 for i,f in enumerate(frames,1)):raise ValueError('Snapshotordinalbindung')
    text=bytes.fromhex(encoded).decode('utf-16-le')
    def unique(pairs):
        result={}
        for key,value in pairs:
            if key in result:raise ValueError('Doppelter Snapshotkey')
            result[key]=value
        return result
    data=json.loads(text,object_pairs_hook=unique)
    if set(data)!={'db','config','files','schemas','objects','indexes','index_columns','columns','reader','permissions','roles','rows','properties'} or len(data['rows'])!=1000:raise ValueError('Vollstaendiger Snapshotshape fehlt')
    return data

def digest(data):return hashlib.sha256(json.dumps(data,sort_keys=True,separators=(',',':'),ensure_ascii=True).encode()).hexdigest()

def run(profile,*,executable,server,confirmed,high_impact,executor=None,clock=time.monotonic,normal_deadline=None,cleanup_started=None):
    if confirmed is not True or high_impact is not True:raise ValueError('Lokale Bestaetigung fehlt')
    executor=executor or profile.execute_client
    normal=profile.Deadline(300,clock)
    if normal_deadline is not None:
        if type(normal_deadline) not in (int,float) or not math.isfinite(normal_deadline):raise ValueError('Tatsaechliche Parentdeadline fehlt')
        normal.end=min(normal.end,normal_deadline)
    started=False;unknown=False;cleanup_ok=False;phases=[];evidence={'qualification':'MARKER_CONTROLS_ONLY'};outcome,code='PASS','OK';count=0
    def invoke(command,budget=None,negative=False):
        nonlocal unknown
        if unknown:raise profile.ClientEndUnknown('Sticky UNKNOWN sperrt SQL')
        try:response=executor(command,timeout_seconds=(budget or normal).remaining(20 if budget else 30))
        except profile.ClientEndUnknown:unknown=True;raise
        output=response.stdout+'\n'+response.stderr
        if len(output.encode('utf-8'))>1000000:raise ValueError('Begrenzte Ausgabe fehlt')
        if response.timed_out:raise TimeoutError('Native Timeout')
        if negative:
            if response.returncode==0 or not profile.native_error(output,51004,'FAIL_STATE'):raise ValueError('Exakte tatsaechliche Markerabweisung fehlt')
            return output
        if response.returncode!=0:raise profile.SqlFailure('Native Markerphase fehlgeschlagen')
        if response.stderr.strip():
            # USE erzeugt beim festen Setup einen echten nativen Infoframe.
            # Nur diese einzelne bekannte Meldung zulassen, keine Zusatzfehler.
            filename=Path(command[command.index('-i')+1]).name
            if filename!='10_Setup.sql' or response.stderr.strip()!="Changed database context to 'SQLPERF_LAB_DGN010_LOCAL'.":
                raise ValueError('Unbekannte native Zusatzdiagnose')
        return response.stdout
    def phase(filename,budget=None,negative=False):
        nonlocal started
        variables={'Path':'0'} if filename=='24_Candidate.sql' else {'Path':'0','Label':'CONTROL_0','Statements':'1','Negative':'0'} if filename in ('40_SelectWindow.sql','50_DmlWindow.sql') else {}
        command=profile.command_for(executable,server,'sql','sa',filename,variables=variables)
        if filename=='10_Setup.sql':started=True
        output=invoke(command,budget,negative)
        if negative:phases.append((filename,'EXPECTED_REJECTION','51004'));return output
        matches=profile.SUMMARY.findall('\n'.join(s.strip() for s in output.splitlines()))
        if len(matches)!=1:raise ValueError('Ein tatsaechlicher Phasensummary erforderlich')
        phases.append((filename,*matches[0]))
        if filename=='00_Preflight.sql' and matches[0] in (('SKIP','SKIP_VERSION'),('SKIP','SKIP_CONFIGURATION'),('SKIP','SKIP_PERMISSION')):raise profile.PhaseStop(*matches[0])
        if matches[0]!=('PASS','OK'):raise ValueError('Unerwarteter Phasenstatus')
        return output
    def sql(text,budget=None):
        scratch=profile.ROOT/'Runtime';scratch.mkdir(exist_ok=True)
        fd,path=tempfile.mkstemp(prefix='dgn010-marker-',suffix='.sql',dir=scratch);path=Path(path).resolve()
        if path.parent!=scratch.resolve() or not path.name.startswith('dgn010-marker-'):raise ValueError('Eigene Scratchbindung fehlt')
        try:
            with os.fdopen(fd,'w',encoding='utf-8',newline='\n') as stream:stream.write(text)
            command=profile.command_for(executable,server,'sql','sa','91_Absence.sql');command[command.index('-i')+1]=str(path);command[command.index('-d')+1]=profile.DATABASE
            return invoke(command,budget)
        finally:
            if not unknown:path.unlink()
    checks=[];recovery=None
    def begin_recovery():
        nonlocal recovery,unknown
        if recovery is None:
            recovery=profile.Deadline(60,clock)
            if cleanup_started is not None:
                parent=cleanup_started()
                if type(parent) not in (int,float) or not math.isfinite(parent):unknown=True;raise profile.ClientEndUnknown('Cleanupdeadline unbekannt')
                recovery.end=min(recovery.end,parent)
        return recovery
    try:
        phase('91_Absence.sql');phase('00_Preflight.sql');phase('10_Setup.sql');probe=phase('20_Probe.sql');profile.source.evidence(probe,0)
        attested=[s for s in phase('22_Database.sql').splitlines() if s.startswith('DGN010_DBID|')]
        if len(attested)!=1:raise ValueError('Unabhaengige DB-ID fehlt')
        dbid=int(attested[0].split('|')[1]);profile.measurement.integer(dbid,5)
        baseline=decode(sql(binding(MARKERS,dbid)+STATE_SQL));original=digest(baseline)
        for marker,value,name,invalid in cases():
            changed={k:v for k,v in MARKERS.items() if k!=marker};changed[name]=invalid
            if name!=marker:mutation=f"EXEC sys.sp_dropextendedproperty @name={literal(marker)}; EXEC sys.sp_addextendedproperty @name={literal(name)},@value={literal(invalid)};"
            elif invalid is None:mutation=f"EXEC sys.sp_dropextendedproperty @name={literal(marker)};"
            else:mutation=f"EXEC sys.sp_updateextendedproperty @name={literal(marker)},@value={literal(invalid)};"
            sql(binding(MARKERS,dbid)+mutation)
            try:
                before=decode(sql(binding(changed,dbid)+STATE_SQL))
                if before['properties']==baseline['properties'] or any(before[k]!=baseline[k] for k in baseline if k!='properties'):raise ValueError('Tatsaechliche exklusive Markermutation fehlt')
                for filename in PHASES:
                    phase(filename,negative=True);count+=1
                    after=decode(sql(binding(changed,dbid)+STATE_SQL))
                    if after!=before:raise ValueError('Abgewiesene Phase hat Fixture veraendert')
                    checks.append({'marker':marker,'name':name,'value':invalid,'phase':filename,'before':digest(before),'after':digest(after)})
            except BaseException:
                begin_recovery();raise
            finally:
                if not unknown:
                    if name!=marker:repair=f"EXEC sys.sp_dropextendedproperty @name={literal(name)}; EXEC sys.sp_addextendedproperty @name={literal(marker)},@value={literal(value)};"
                    else:repair=f"EXEC sys.{'sp_addextendedproperty' if invalid is None else 'sp_updateextendedproperty'} @name={literal(marker)},@value={literal(value)};"
                    sql(binding(changed,dbid)+repair,budget=recovery)
                    restored=decode(sql(binding(MARKERS,dbid)+STATE_SQL,budget=recovery))
                    if restored!=baseline:raise ValueError('Vollstaendiger eigener Markerrestore fehlt')
        profile.source.evidence(phase('20_Probe.sql'),0)
        if count!=192 or len(checks)!=192:raise ValueError('Vollstaendige feste Markerabnahme fehlt')
        evidence.update(database_id=dbid,baseline_digest=original,controls=checks,negative_count=count,restored_cases=24,runtime_qualification='NOT_ESTABLISHED')
    except profile.PhaseStop as stop:outcome,code=stop.outcome,stop.code
    except profile.ClientEndUnknown:outcome,code='FAIL','FAIL_CLEANUP'
    except TimeoutError:outcome,code='FAIL','FAIL_TIMEOUT'
    except (Exception,KeyboardInterrupt) as error:outcome,code='FAIL','FAIL_RESULT_CONTRACT';evidence['failure_type']=type(error).__name__
    finally:
        begin_recovery()
        if not unknown:
            try:
                if started:phase('90_Cleanup.sql',budget=recovery)
                output=phase('91_Absence.sql',budget=recovery);cleanup_ok=output.splitlines().count('DGN010_DB|ABSENT')==1 and clock()<=recovery.end
            except (Exception,KeyboardInterrupt):cleanup_ok=False
        if not cleanup_ok:outcome,code='FAIL','FAIL_CLEANUP'
    evidence['completed_negative_count']=count
    return profile.Result(outcome,code,cleanup_ok,unknown,tuple(phases),evidence)
