"""CON-010-Gegenproben ausschließlich auf einer frisch erzeugten eigenen Fixture."""
from pathlib import Path
import re
import time
import execution_target as targets

MARKERS={'SQLPERF.Project':'SQL_PerformanceSchulung','SQLPERF.ContractVersion':'1.0',
         'SQLPERF.DemoId':'CON-010','SQLPERF.RunToken':'LOCAL'}
PHASES=('00_Preflight.sql','10_Setup.sql','20_Baseline.sql','30_Demonstration.sql',
        '40_Observation.sql','50_Mitigation.sql','60_Comparison.sql','90_Cleanup.sql')

def literal(text):return "N'"+text.replace("'","''")+"'"

def match(name,value):
    """Ein vollständiger Unicode-Name/Wert, exakt eine DB-Eigenschaft."""
    condition=f"DATALENGTH(name)=DATALENGTH({literal(name)}) AND CONVERT(varbinary(max),name)=CONVERT(varbinary(max),{literal(name)})"
    if value is None:
        return f"NOT EXISTS(SELECT 1 FROM sys.extended_properties WHERE class=0 AND major_id=0 AND minor_id=0 AND {condition})"
    condition+=f" AND DATALENGTH(CONVERT(nvarchar(max),value))=DATALENGTH({literal(value)}) AND CONVERT(varbinary(max),CONVERT(nvarchar(max),value))=CONVERT(varbinary(max),{literal(value)})"
    return f"(SELECT COUNT(*) FROM sys.extended_properties WHERE class=0 AND major_id=0 AND minor_id=0 AND {condition})=1"

def binding(markers=MARKERS):
    return "IF CASE WHEN ("+' AND '.join(match(k,v) for k,v in markers.items())+") THEN 1 ELSE 0 END<>1 THROW 51004,'FAIL_STATE: Vollstaendige Fixturebindung verloren.',1; "

def snapshot(stable_setup=False):
    """Vollständige semantische Daten/Metadaten; Hashes stets mit voller Länge."""
    # Recreated object/principal IDs and create times may change across Setup.
    # Marker probes additionally retain these volatile bindings.
    ids="" if stable_setup else "; SELECT object_id,name,type,create_date,modify_date FROM sys.objects WHERE schema_id IN(SCHEMA_ID(N'lab'),SCHEMA_ID(N'sec')) ORDER BY object_id; SELECT principal_id,sid FROM sys.database_principals WHERE name IN(N'CON010_TenantA',N'CON010_TenantB',N'CON010_Unmapped') ORDER BY name"
    return """SET NOCOUNT ON;
SELECT Id,TenantId,DATALENGTH(Content),CONVERT(varchar(64),HASHBYTES('SHA2_256',CONVERT(varbinary(max),Content)),2),CONVERT(varchar(200),V) FROM lab.Documents ORDER BY Id;
SELECT p.name,p.is_enabled,p.is_schema_bound,f.name,pr.predicate_type,pr.operation,DATALENGTH(pr.predicate_definition),CONVERT(varchar(64),HASHBYTES('SHA2_256',CONVERT(varbinary(max),pr.predicate_definition)),2)
FROM sys.security_policies p JOIN sys.security_predicates pr ON pr.object_id=p.object_id JOIN sys.objects f ON f.object_id=OBJECT_ID(N'sec.TenantPredicate') ORDER BY p.name;
SELECT DATALENGTH(OBJECT_DEFINITION(OBJECT_ID(N'sec.TenantPredicate'))),CONVERT(varchar(64),HASHBYTES('SHA2_256',CONVERT(varbinary(max),OBJECT_DEFINITION(OBJECT_ID(N'sec.TenantPredicate')))),2);
SELECT DATALENGTH(name),CONVERT(varchar(512),CONVERT(varbinary(256),name),2),type,authentication_type FROM sys.database_principals WHERE name IN(N'CON010_TenantA',N'CON010_TenantB',N'CON010_Unmapped') ORDER BY name;
SELECT USER_NAME(grantee_principal_id),USER_NAME(grantor_principal_id),class,CASE WHEN class=1 THEN OBJECT_SCHEMA_NAME(major_id)+N'.'+OBJECT_NAME(major_id) ELSE CONVERT(nvarchar(20),major_id) END,minor_id,permission_name,state FROM sys.database_permissions WHERE grantee_principal_id IN(USER_ID(N'CON010_TenantA'),USER_ID(N'CON010_TenantB'),USER_ID(N'CON010_Unmapped')) ORDER BY USER_NAME(grantee_principal_id),class,major_id,minor_id,permission_name;
SELECT USER_NAME(role_principal_id),USER_NAME(member_principal_id) FROM sys.database_role_members WHERE member_principal_id IN(USER_ID(N'CON010_TenantA'),USER_ID(N'CON010_TenantB'),USER_ID(N'CON010_Unmapped')) ORDER BY role_principal_id,member_principal_id;
SELECT compatibility_level,recovery_model_desc,is_auto_close_on,is_auto_shrink_on FROM sys.databases WHERE database_id=DB_ID();
SELECT file_id,size,max_size,growth FROM sys.database_files ORDER BY file_id;
"""+ids+';'

MUTATIONS=(
    'DELETE FROM lab.Documents;',
    "UPDATE lab.Documents SET Content=Content+N' ' WHERE Id=1;",
    'UPDATE lab.Documents SET TenantId=2 WHERE Id=1;',
    "UPDATE lab.Documents SET V='[0,1,0]' WHERE Id=1;",
    'ALTER SECURITY POLICY sec.TenantPolicy WITH(STATE=OFF);',
    'DROP SECURITY POLICY sec.TenantPolicy;',
    "DROP SECURITY POLICY sec.TenantPolicy; EXEC(N'ALTER FUNCTION sec.TenantPredicate(@TenantId int) RETURNS TABLE WITH SCHEMABINDING AS RETURN SELECT 1 AS Allowed;'); EXEC(N'CREATE SECURITY POLICY sec.TenantPolicy ADD FILTER PREDICATE sec.TenantPredicate(TenantId) ON lab.Documents WITH(STATE=ON,SCHEMABINDING=ON);');",
    'REVOKE CONNECT FROM [CON010_TenantA];',
    'DENY CONNECT TO [CON010_TenantB];',
    'GRANT SELECT ON OBJECT::lab.Documents TO [CON010_TenantA] WITH GRANT OPTION;',
    'GRANT UPDATE ON OBJECT::lab.Documents TO [CON010_TenantA];',
    'REVOKE SELECT ON OBJECT::lab.Documents FROM [CON010_TenantA];',
    'GRANT CONTROL TO [CON010_TenantB];',
    'ALTER ROLE db_owner ADD MEMBER [CON010_TenantA];',
    'DENY SELECT ON OBJECT::lab.Documents(Id) TO [CON010_TenantA];',
    'GRANT IMPERSONATE ON USER::[CON010_TenantB] TO [CON010_TenantA];',
)

def expected_native_error(text,code,detail):
    """Eine exakte sqlcmd-Fehlernummer mit ihrer unmittelbar folgenden Nachricht."""
    prefix=r'(?:sqlcmd failed in database (?:master|SQLPERF_LAB_CON010_LOCAL): )?'
    headers=list(re.finditer('^'+prefix+r'Msg ([0-9]+), Level [0-9]+, State [0-9]+(?:, [^\r\n]*)?\r?\n([^\r\n]+)',text,re.MULTILINE))
    all_headers=re.findall('^'+prefix+r'Msg [0-9]+\b',text,re.MULTILINE)
    return (len(all_headers)==len(headers)==1 and int(headers[0].group(1))==code
            and re.fullmatch(re.escape(detail)+r':[^\r\n]*',headers[0].group(2).strip()) is not None)

def run(target,directory:Path,*,cleanup_started=None):
    name='SQLPERF_LAB_CON010_LOCAL';end=time.monotonic()+900;cleanup_end=None
    def sql(text,database=name,cap=30,cleanup=False):
        budget=cleanup_end if cleanup else end
        remaining=min(cap,budget-time.monotonic())
        if remaining<=0:raise TimeoutError('CON-010 Gegenprobenbudget verbraucht')
        return targets.run_sql(target,database=database,sql_text=text,timeout_seconds=remaining)
    def absent(cleanup=False):
        output=sql(f"SET NOCOUNT ON; IF DB_ID(N'{name}') IS NOT NULL THROW 51003,'DB residue',1; PRINT 'CON010_DB|ABSENT';",database='master',cap=4,cleanup=cleanup)
        if output.strip()!='CON010_DB|ABSENT':raise ValueError('Neue unabhängige CON-010-DB-Abwesenheit fehlt')
    def phase(filename,cleanup=False):
        text=(directory/filename).read_text(encoding='utf-8')
        for k,v in {'DemoId':'CON-010','RunToken':'LOCAL','TargetDatabase':name}.items():text=text.replace('$('+k+')',v)
        output=sql(text,database='master' if filename[:2] in ('00','10','90') else name,cap=20 if cleanup else 60,cleanup=cleanup)
        if 'SQLPERF_SUMMARY|PASS|OK' not in output:raise ValueError('CON-010-Phasensummary fehlt')
        return output
    def rejected(filename,code,detail):
        try:phase(filename)
        except targets.ExecutionTargetError as error:
            if not expected_native_error(str(error),code,detail):raise ValueError('Gegenprobe scheiterte an anderem Fehler') from error
        else:raise ValueError('Verletzte CON-010-Fixture wurde akzeptiert')
    absent();started=False;marker_count=0
    try:
        started=True;phase('10_Setup.sql');before=sql(snapshot(True));phase('10_Setup.sql')
        if sql(snapshot(True))!=before:raise ValueError('CON-010 Setup nicht semantisch idempotent')
        before=sql(snapshot())
        for marker,value in MARKERS.items():
            cases=[(marker,None),(marker,'FOREIGN'),(marker,value+' '),(marker,value+'X'*256),
                   (marker.lower(),value),(marker+' ',value)]
            for altered,invalid in cases:
                other={k:v for k,v in MARKERS.items() if k!=marker}
                if altered!=marker:
                    mutation=f"EXEC sys.sp_dropextendedproperty @name={literal(marker)}; EXEC sys.sp_addextendedproperty @name={literal(altered)},@value={literal(invalid)};"
                elif invalid is None:mutation=f"EXEC sys.sp_dropextendedproperty @name={literal(marker)};"
                else:mutation=f"EXEC sys.sp_updateextendedproperty @name={literal(marker)},@value={literal(invalid)};"
                sql(binding()+mutation)
                try:
                    # Attest the actual invalid name/value before evaluating the guard.
                    sql(binding(other)+"IF CASE WHEN ("+match(altered,invalid)+") THEN 1 ELSE 0 END<>1 THROW 51004,'FAIL_STATE: Gegenprobe nicht tatsaechlich erzeugt.',1;")
                    for filename in PHASES:
                        rejected(filename,51004,'FAIL_STATE');marker_count+=1
                        if sql(snapshot())!=before:raise ValueError('Marker-Gegenprobe veränderte Fixture/Konfiguration')
                finally:
                    repair=binding(other)+"IF CASE WHEN ("+match(altered,invalid)+") THEN 1 ELSE 0 END<>1 THROW 51004,'FAIL_STATE: Reparaturbindung verloren.',1; "
                    if altered!=marker:repair+=f"EXEC sys.sp_dropextendedproperty @name={literal(altered)}; EXEC sys.sp_addextendedproperty @name={literal(marker)},@value={literal(value)};"
                    else:
                        proc='sp_addextendedproperty' if invalid is None else 'sp_updateextendedproperty'
                        repair+=f"EXEC sys.{proc} @name={literal(marker)},@value={literal(value)};"
                    sql(repair);sql(binding())
        for mutation in MUTATIONS:
            phase('10_Setup.sql');phase('60_Comparison.sql')
            before_mutation=sql(snapshot())
            sql(binding()+mutation)
            if sql(snapshot())==before_mutation:raise ValueError('CON-010-Manipulation ohne tatsaechliche Fixtureaenderung')
            for filename in ('20_Baseline.sql','60_Comparison.sql'):rejected(filename,51003,'FAIL_RESULT_CONTRACT')
        print(f'AI_LOCAL|CON-010|RESULT_NEGATIVE_{len(MUTATIONS)}|PASS')
    finally:
        cleanup_end=cleanup_started() if cleanup_started is not None else time.monotonic()+60
        if started:phase('90_Cleanup.sql',cleanup=True)
        absent(cleanup=True)
    print(f'AI_LOCAL|CON-010|OWNERSHIP_NEGATIVE_{marker_count}|IDEMPOTENCE|PASS|CLEANUP_ABSENT')
