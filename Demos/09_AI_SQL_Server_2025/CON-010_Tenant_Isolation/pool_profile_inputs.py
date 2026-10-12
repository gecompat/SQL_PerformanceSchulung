"""Feste RED-isolated Poolprofileingaben; keine Clients oder freien SQL-Identifier."""
import json,re
from pathlib import Path
import pool_profile_evidence as oracle
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
    return f"SET NOCOUNT ON; IF DB_ID()<> {dbid} OR DATALENGTH(DB_NAME())<>DATALENGTH(N'SQLPERF_LAB_CON010_POOLPUBLIC') OR CONVERT(varbinary(max),DB_NAME())<>CONVERT(varbinary(max),N'SQLPERF_LAB_CON010_POOLPUBLIC') THROW 51004,'FAIL_STATE: Eigene DB-Bindung verloren.',1; IF CASE WHEN ({guard} AND (SELECT COUNT(*) FROM sys.extended_properties WHERE class=0 AND major_id=0 AND minor_id=0)={expected}) THEN 1 ELSE 0 END<>1 THROW 51004,'FAIL_STATE: Vollstaendige Gegenprobenbindung verloren.',1; "
HERE=Path(__file__).resolve().parent;DATABASE=oracle.DATABASE
MARKERS={'SQLPERF.Project':'SQL_PerformanceSchulung','SQLPERF.ContractVersion':'1.0','SQLPERF.DemoId':'CON-010','SQLPERF.RunToken':'POOLPUBLIC'}
OUTPUT="""
DECLARE @Chars int=DATALENGTH(@J)/2,@Parts int,@Part int=1;SET @Parts=(@Chars+199)/200;
IF @Chars NOT BETWEEN 1 AND 200000 THROW 51003,'FAIL_RESULT_CONTRACT: Output bound.',1;
WHILE @Part<=@Parts BEGIN PRINT CONCAT('CON010_POOL_CAPTURE_PART|',@Part,'|',@Parts,'|',@Chars,'|',CONVERT(varchar(800),CONVERT(varbinary(400),SUBSTRING(@J,(@Part-1)*200+1,200)),2));SET @Part+=1;END;
PRINT 'SQLPERF_SUMMARY|PASS|OK';
"""
SUMMARY="SELECT 'SQLPERF_SUMMARY|PASS|OK';"
def checked(value):
    if type(value) is not int or not 5<=value<=2147483647:raise ValueError('Actual DB/OID required')
    return str(value)
def bound(dbid,values=None):
    checked(dbid);values=MARKERS if values is None else values
    if set(values)!=set(MARKERS) or any(type(v) is not str for v in values.values()):raise ValueError('Full marker binding')
    text=binding(values,dbid).replace('SQLPERF_LAB_CON010_POOLPUBLIC',DATABASE)
    text+="IF (SELECT COUNT(*) FROM sys.extended_properties WHERE class=0 AND major_id=0 AND minor_id=0 AND CONVERT(varbinary(max),CONVERT(nvarchar(128),SQL_VARIANT_PROPERTY(value,'BaseType')))=CONVERT(varbinary(max),N'nvarchar'))<>4 THROW 51004,'FAIL_STATE: Marker type.',1;"
    return text
def creator():return bound(5).replace('DB_ID()<> 5','DB_ID() IS NULL')
def names():return ','.join(literal(pair[0]) for pair in oracle.LOGINS.values())
def users():return ','.join(literal(pair[1]) for pair in oracle.LOGINS.values())
PRINCIPALS="""DECLARE @P nvarchar(max)=(SELECT
JSON_QUERY(COALESCE((SELECT p.principal_id,p.name,DATALENGTH(p.name) name_bytes,CONVERT(varchar(max),CONVERT(varbinary(max),p.name),2) name_hex,CONVERT(varchar(max),p.sid,2) sid,p.type,p.type_desc,p.is_disabled,p.create_date,p.modify_date,p.default_database_name,p.default_language_name,p.credential_id,p.is_fixed_role,l.is_policy_checked,l.is_expiration_checked FROM sys.server_principals p JOIN sys.sql_logins l ON l.principal_id=p.principal_id WHERE p.name IN ($(Logins)) ORDER BY p.principal_id FOR JSON PATH,INCLUDE_NULL_VALUES),N'[]')) Logins,
JSON_QUERY(COALESCE((SELECT class,major_id,grantee_principal_id,grantor_principal_id,type,permission_name,DATALENGTH(permission_name) permission_bytes,CONVERT(varchar(max),CONVERT(varbinary(max),permission_name),2) permission_hex,state FROM sys.server_permissions WHERE grantee_principal_id IN (SELECT principal_id FROM sys.server_principals WHERE name IN ($(Logins))) ORDER BY class,major_id,grantee_principal_id,type FOR JSON PATH,INCLUDE_NULL_VALUES),N'[]')) ServerPermissions,
JSON_QUERY(COALESCE((SELECT role_principal_id,member_principal_id FROM sys.server_role_members WHERE member_principal_id IN (SELECT principal_id FROM sys.server_principals WHERE name IN ($(Logins))) ORDER BY role_principal_id,member_principal_id FOR JSON PATH),N'[]')) ServerRoles,
JSON_QUERY(COALESCE((SELECT principal_id,name,DATALENGTH(name) name_bytes,CONVERT(varchar(max),CONVERT(varbinary(max),name),2) name_hex,CONVERT(varchar(max),sid,2) sid,type,authentication_type,default_schema_name,is_fixed_role,create_date,modify_date FROM sys.database_principals WHERE name IN ($(Users)) ORDER BY principal_id FOR JSON PATH,INCLUDE_NULL_VALUES),N'[]')) Users,
JSON_QUERY(COALESCE((SELECT class,major_id,minor_id,grantee_principal_id,grantor_principal_id,type,permission_name,DATALENGTH(permission_name) permission_bytes,CONVERT(varchar(max),CONVERT(varbinary(max),permission_name),2) permission_hex,state FROM sys.database_permissions WHERE grantee_principal_id IN (SELECT principal_id FROM sys.database_principals WHERE name IN ($(Users))) ORDER BY class,major_id,minor_id,grantee_principal_id,type FOR JSON PATH,INCLUDE_NULL_VALUES),N'[]')) DatabasePermissions,
JSON_QUERY(COALESCE((SELECT role_principal_id,member_principal_id FROM sys.database_role_members WHERE member_principal_id IN (SELECT principal_id FROM sys.database_principals WHERE name IN ($(Users))) ORDER BY role_principal_id,member_principal_id FOR JSON PATH),N'[]')) DatabaseRoles
FOR JSON PATH,WITHOUT_ARRAY_WRAPPER,INCLUDE_NULL_VALUES);
""".replace('$(Logins)',names()).replace('$(Users)',users())
def absence(sids):
    for lane in oracle.LOGINS:oracle.sid(sids[lane])
    ids=','.join('0x'+sids[l] for l in oracle.LOGINS)
    return f"SET NOCOUNT ON;IF DB_ID(N'{DATABASE}') IS NOT NULL OR EXISTS(SELECT 1 FROM sys.server_principals WHERE name IN ({names()}) OR sid IN ({ids})) THROW 51004,'FAIL_STATE: Own name/SID/DB residue.',1;SELECT 'POOLPUBLIC_ALL|ABSENT';"
def setup(sids):
    return absence(sids)+f"""
IF CONVERT(nvarchar(80),SERVERPROPERTY('ProductVersion')) IS NULL OR CONVERT(nvarchar(80),SERVERPROPERTY('ProductVersion'))<>N'17.0.5005.3' OR ISNULL(CONVERT(int,SERVERPROPERTY('EngineEdition')),-1)<>3 OR ISNULL(CONVERT(int,SERVERPROPERTY('IsIntegratedSecurityOnly')),-1)<>0 OR ISNULL(IS_SRVROLEMEMBER('sysadmin'),0)<>1 THROW 51001,'FAIL_STATE: Fixed isolated SQL-auth admin build required.',1;
CREATE DATABASE {DATABASE};
GO
USE {DATABASE};
"""+''.join(f"EXEC sys.sp_addextendedproperty @name={literal(k)},@value={literal(v)};" for k,v in MARKERS.items())+creator()+f"""
ALTER DATABASE CURRENT SET COMPATIBILITY_LEVEL=170;ALTER DATABASE CURRENT SET RECOVERY SIMPLE;
ALTER DATABASE CURRENT MODIFY FILE(NAME=N'{DATABASE}',MAXSIZE=256MB,FILEGROWTH=16MB);
ALTER DATABASE CURRENT MODIFY FILE(NAME=N'{DATABASE}_log',MAXSIZE=64MB,FILEGROWTH=16MB);
EXEC(N'CREATE SCHEMA lab AUTHORIZATION dbo;');EXEC(N'CREATE SCHEMA sec AUTHORIZATION dbo;');
CREATE TABLE lab.Documents(Id int NOT NULL PRIMARY KEY,TenantId int NOT NULL,Content nvarchar(100) NOT NULL,V VECTOR(3) NOT NULL);
INSERT lab.Documents VALUES(1,1,N'Synthetische Quelle A',CONVERT(VECTOR(3),'[1,0,0]')),(2,2,N'Synthetische Quelle B',CONVERT(VECTOR(3),'[1,0,0]'));
EXEC(N'CREATE FUNCTION sec.TenantPredicate(@TenantId int) RETURNS TABLE WITH SCHEMABINDING AS RETURN SELECT 1 Allowed WHERE USER_NAME()=N''dbo'' OR (@TenantId=1 AND USER_NAME()=N''CON010_TenantA'') OR (@TenantId=2 AND USER_NAME()=N''CON010_TenantB'');');
EXEC(N'CREATE SECURITY POLICY sec.TenantPolicy ADD FILTER PREDICATE sec.TenantPredicate(TenantId) ON lab.Documents WITH(STATE=ON,SCHEMABINDING=ON);');
"""+SUMMARY
def create_logins(dbid,sids):
    text=bound(dbid)
    for lane,(login,user) in oracle.LOGINS.items():
        oracle.sid(sids[lane])
        text+=f"IF EXISTS(SELECT 1 FROM sys.server_principals WHERE name=N'{login}' OR sid=0x{sids[lane]}) OR USER_ID(N'{user}') IS NOT NULL THROW 51004,'FAIL_STATE: No principal adoption.',1;"
    for lane,(login,user) in oracle.LOGINS.items():
        guard=bound(dbid)
        text+=guard+f"CREATE LOGIN [{login}] WITH PASSWORD=N'$(TenantSecret{lane})',SID=0x{sids[lane]},DEFAULT_DATABASE=[{DATABASE}],DEFAULT_LANGUAGE=us_english,CHECK_POLICY=OFF,CHECK_EXPIRATION=OFF;"
        text+=guard+f"EXEC master.sys.sp_executesql N'GRANT CONNECT SQL TO [{login}];';"
        text+=guard+f"CREATE USER [{user}] FOR LOGIN [{login}] WITH DEFAULT_SCHEMA=dbo;"
        text+=guard+f"GRANT CONNECT TO [{user}];"
        text+=guard+f"GRANT SELECT ON OBJECT::lab.Documents TO [{user}];"
    return text+SUMMARY
IDENTITY="""(SELECT DB_ID() DatabaseId,DB_NAME() DatabaseName,SUSER_SNAME() SuserName,ORIGINAL_LOGIN() OriginalLogin,USER_NAME() UserName,CONVERT(varchar(max),SUSER_SID(),2) ServerSid,CONVERT(varchar(max),SUSER_SID(ORIGINAL_LOGIN()),2) OriginalSid,CONVERT(varchar(max),(SELECT sid FROM sys.database_principals WHERE principal_id=USER_ID()),2) UserSid,@@SPID SessionId FOR JSON PATH,WITHOUT_ARRAY_WRAPPER,INCLUDE_NULL_VALUES)"""
def authenticated(kind,lane,dbid,spoof=False):
    if lane not in oracle.LOGINS or kind not in ('ROWS','ALTER','IMPERSONATE','REVOKED_SELECT'):raise ValueError('Fixed authenticated case')
    # Tenant clients have no metadata grants; context+identity is checked in the pure oracle.
    text=f"SET NOCOUNT ON;SET XACT_ABORT ON;IF DB_ID()<>{checked(dbid)} OR CONVERT(varbinary(max),DB_NAME())<>CONVERT(varbinary(max),N'{DATABASE}') THROW 51004,'FAIL_STATE: Authenticated own DB lost.',1;DECLARE @Identity nvarchar(max)={IDENTITY};"
    if kind=='ROWS':
        if spoof:text+="EXEC sys.sp_set_session_context @key=N'CON010_TenantId',@value=2;"
        text+="DECLARE @Before int=CONVERT(int,SESSION_CONTEXT(N'CON010_TenantId'));DECLARE @Rows nvarchar(max)=(SELECT Id,TenantId,Content,DATALENGTH(Content) ContentBytes,CONVERT(varchar(max),CONVERT(varbinary(max),Content),2) ContentHex,CONVERT(varchar(max),V) VectorJson,CONVERT(int,VECTORPROPERTY(V,'Dimensions')) Dimensions,CONVERT(nvarchar(128),VECTORPROPERTY(V,'BaseType')) BaseType,VECTOR_DISTANCE('cosine',V,CONVERT(VECTOR(3),'[1,0,0]')) Distance FROM lab.Documents ORDER BY Id FOR JSON PATH,INCLUDE_NULL_VALUES);EXEC sys.sp_set_session_context @key=N'CON010_TenantId',@value=NULL;DECLARE @J nvarchar(max)=(SELECT JSON_QUERY(@Identity) [Identity],JSON_QUERY(COALESCE(@Rows,N'[]')) [Rows],@Before SessionTenantBefore,CONVERT(int,SESSION_CONTEXT(N'CON010_TenantId')) SessionTenantAfter FOR JSON PATH,WITHOUT_ARRAY_WRAPPER,INCLUDE_NULL_VALUES);"
    else:
        statement={'ALTER':'ALTER SECURITY POLICY sec.TenantPolicy WITH(STATE=OFF);','IMPERSONATE':"EXECUTE AS USER=N'CON010_TenantB';REVERT;",'REVOKED_SELECT':'SELECT Id FROM lab.Documents;'}[kind]
        text+="DECLARE @Number int,@Severity int,@State int,@Line int,@Procedure nvarchar(128),@Message nvarchar(4000);BEGIN TRY EXEC sys.sp_executesql "+literal(statement)+";END TRY BEGIN CATCH SELECT @Number=ERROR_NUMBER(),@Severity=ERROR_SEVERITY(),@State=ERROR_STATE(),@Line=ERROR_LINE(),@Procedure=ERROR_PROCEDURE(),@Message=ERROR_MESSAGE();END CATCH;IF @Number IS NULL THROW 51003,'FAIL_RESULT_CONTRACT: Denied operation succeeded.',1;"
        text+=f"DECLARE @J nvarchar(max)=(SELECT JSON_QUERY(@Identity) [Identity],N'{kind}' Kind,@Number ErrorNumber,@Severity ErrorSeverity,@State ErrorState,@Line ErrorLine,@Procedure ErrorProcedure,DATALENGTH(@Message) MessageBytes,CONVERT(varchar(max),CONVERT(varbinary(max),@Message),2) MessageHex FOR JSON PATH,WITHOUT_ARRAY_WRAPPER,INCLUDE_NULL_VALUES);"
    return text+OUTPUT
config=",name,is_value_default,\nCONVERT(nvarchar(128),SQL_VARIANT_PROPERTY(value,'BaseType')) AS value_type,\nCONVERT(int,SQL_VARIANT_PROPERTY(value,'Precision')) AS value_precision,\nCONVERT(int,SQL_VARIANT_PROPERTY(value,'Scale')) AS value_scale,\nCONVERT(int,SQL_VARIANT_PROPERTY(value,'MaxLength')) AS value_max_length,\nCONVERT(nvarchar(128),SQL_VARIANT_PROPERTY(value,'Collation')) AS value_collation,\nDATALENGTH(CONVERT(varbinary(max),value)) AS value_bytes,\nCONVERT(varchar(max),CONVERT(varbinary(max),value),2) AS value_hex,\nCONVERT(nvarchar(128),SQL_VARIANT_PROPERTY(value_for_secondary,'BaseType')) AS secondary_type,\nCONVERT(int,SQL_VARIANT_PROPERTY(value_for_secondary,'Precision')) AS secondary_precision,\nCONVERT(int,SQL_VARIANT_PROPERTY(value_for_secondary,'Scale')) AS secondary_scale,\nCONVERT(int,SQL_VARIANT_PROPERTY(value_for_secondary,'MaxLength')) AS secondary_max_length,\nCONVERT(nvarchar(128),SQL_VARIANT_PROPERTY(value_for_secondary,'Collation')) AS secondary_collation,\nDATALENGTH(CONVERT(varbinary(max),value_for_secondary)) AS secondary_bytes,\nCONVERT(varchar(max),CONVERT(varbinary(max),value_for_secondary),2) AS secondary_hex\nFROM sys.database_scoped_configurations ORDER BY configuration_id FOR JSON PATH,INCLUDE_NULL_VALUES))"
files=',name,type,size,max_size,growth,is_percent_growth,is_read_only,CONVERT(varchar(36),file_guid) AS guid FROM sys.database_files ORDER BY file_id FOR JSON PATH,INCLUDE_NULL_VALUES))'
properties=" AS name_bytes,CONVERT(varchar(max),CONVERT(varbinary(max),name),2) AS name_hex,DATALENGTH(CONVERT(nvarchar(max),value)) AS value_bytes,CONVERT(varchar(max),CONVERT(varbinary(max),CONVERT(nvarchar(max),value)),2) AS value_hex,CONVERT(nvarchar(128),SQL_VARIANT_PROPERTY(value,'BaseType')) AS base_type FROM sys.extended_properties ORDER BY class,major_id,minor_id,CONVERT(varbinary(max),name) FOR JSON PATH))"
STATE=PRINCIPALS+"""DECLARE @J nvarchar(max)=(SELECT JSON_QUERY(@P) Principals,DATALENGTH(@P) PrincipalBytes,CONVERT(varchar(max),CONVERT(varbinary(max),@P),2) PrincipalHex,
JSON_QUERY((SELECT database_id,name,compatibility_level,recovery_model_desc,owner_sid FROM sys.databases WHERE database_id=DB_ID() FOR JSON PATH)) db,
JSON_QUERY((SELECT configuration_id"""+config+""" config,JSON_QUERY((SELECT file_id"""+files+""" files,
JSON_QUERY((SELECT schema_id,name,principal_id FROM sys.schemas WHERE name IN(N'lab',N'sec') ORDER BY schema_id FOR JSON PATH)) schemas,
JSON_QUERY((SELECT object_id,schema_id,parent_object_id,name,type,create_date,modify_date FROM sys.objects WHERE schema_id IN(SCHEMA_ID(N'lab'),SCHEMA_ID(N'sec')) ORDER BY object_id FOR JSON PATH)) objects,
JSON_QUERY((SELECT object_id,index_id,name,type,is_unique,is_primary_key,is_disabled FROM sys.indexes WHERE object_id=OBJECT_ID(N'lab.Documents') ORDER BY index_id FOR JSON PATH,INCLUDE_NULL_VALUES)) indexes,
JSON_QUERY((SELECT object_id,index_id,index_column_id,column_id,key_ordinal,is_included_column FROM sys.index_columns WHERE object_id=OBJECT_ID(N'lab.Documents') ORDER BY index_id,index_column_id FOR JSON PATH)) index_columns,
JSON_QUERY((SELECT object_id,column_id,name,system_type_id,user_type_id,max_length,precision,scale,collation_name,is_nullable,vector_dimensions,vector_base_type FROM sys.columns WHERE object_id=OBJECT_ID(N'lab.Documents') ORDER BY column_id FOR JSON PATH,INCLUDE_NULL_VALUES)) columns,
JSON_QUERY((SELECT object_id,is_enabled,is_schema_bound FROM sys.security_policies WHERE schema_id=SCHEMA_ID(N'sec') ORDER BY object_id FOR JSON PATH)) policies,
JSON_QUERY((SELECT object_id,security_predicate_id,target_object_id,predicate_definition,predicate_type,operation FROM sys.security_predicates WHERE target_object_id=OBJECT_ID(N'lab.Documents') ORDER BY object_id,security_predicate_id FOR JSON PATH)) predicates,
JSON_QUERY((SELECT object_id,definition,is_schema_bound FROM sys.sql_modules WHERE object_id=OBJECT_ID(N'sec.TenantPredicate') FOR JSON PATH)) modules,
JSON_QUERY((SELECT Id,TenantId,DATALENGTH(Content) ContentBytes,CONVERT(varchar(max),CONVERT(varbinary(max),Content),2) ContentHex,CONVERT(varchar(max),V) VectorJson FROM lab.Documents ORDER BY Id FOR JSON PATH)) rows,
JSON_QUERY((SELECT class,major_id,minor_id,DATALENGTH(name)"""+properties+""" properties FOR JSON PATH,WITHOUT_ARRAY_WRAPPER,INCLUDE_NULL_VALUES);"""+OUTPUT
def state(dbid,values=None):return bound(dbid,values)+STATE
def grant(dbid,revoke=False):return bound(dbid)+('REVOKE' if revoke else 'GRANT')+' SELECT ON OBJECT::lab.Documents '+('FROM' if revoke else 'TO')+' [CON010_TenantA];'+SUMMARY
def drop_login(dbid,lane,held_hex,sids,remaining):
    if lane not in remaining or tuple(remaining)!=tuple(l for l in oracle.LOGINS if l in remaining):raise ValueError('Fixed ordered remaining login set')
    if type(held_hex) is not str or not re.fullmatch('(?:[A-F0-9]{2})+',held_hex) or len(held_hex)>200000:raise ValueError('Held complete principal bytes required')
    # Each array element is compared as its complete native JSON bytes, including timestamps/flags.
    text=bound(dbid)+PRINCIPALS+f"DECLARE @Held nvarchar(max)=CONVERT(nvarchar(max),0x{held_hex});"
    remaining_names=','.join(literal(oracle.LOGINS[l][0]) for l in remaining)
    for key in ('Logins','ServerPermissions','ServerRoles','Users','DatabasePermissions','DatabaseRoles'):
        expected="SELECT CONVERT(varbinary(max),value) v FROM OPENJSON(@Held,'$."+key+"')"
        if key=='Logins':expected+=f" WHERE JSON_VALUE(value,'$.name') IN({remaining_names})"
        elif key in ('ServerPermissions','ServerRoles'):
            field='grantee_principal_id' if key=='ServerPermissions' else 'member_principal_id'
            expected+=f" WHERE TRY_CONVERT(int,JSON_VALUE(value,'$.{field}')) IN(SELECT TRY_CONVERT(int,JSON_VALUE(value,'$.principal_id')) FROM OPENJSON(@Held,'$.Logins') WHERE JSON_VALUE(value,'$.name') IN({remaining_names}))"
        actual="SELECT CONVERT(varbinary(max),value) v FROM OPENJSON(@P,'$."+key+"')"
        text+=f"IF EXISTS({actual} EXCEPT {expected}) OR EXISTS({expected} EXCEPT {actual}) OR (SELECT COUNT(*) FROM OPENJSON(@P,'$.{key}'))<>(SELECT COUNT(*) FROM ({expected}) e) THROW 51004,'FAIL_STATE: Held full principal lease differs.',1;"
    for l,(login,user) in oracle.LOGINS.items():
        oracle.sid(sids[l])
        if l in remaining:text+=f"IF NOT EXISTS(SELECT 1 FROM sys.server_principals WHERE DATALENGTH(name)=DATALENGTH(N'{login}') AND CONVERT(varbinary(max),name)=CONVERT(varbinary(max),N'{login}') AND sid=0x{sids[l]} AND type='S') OR EXISTS(SELECT 1 FROM sys.databases WHERE owner_sid=0x{sids[l]}) THROW 51004,'FAIL_STATE: Own recorded SID/owner binding.',1;"
        else:text+=f"IF EXISTS(SELECT 1 FROM sys.server_principals WHERE name=N'{login}' OR sid=0x{sids[l]}) THROW 51004,'FAIL_STATE: Dropped principal residue.',1;"
    return text+f"DROP LOGIN [{oracle.LOGINS[lane][0]}];"+SUMMARY
def cleanup_db(dbid,sids):
    ids=','.join('0x'+oracle.sid(sids[l]) for l in oracle.LOGINS)
    return bound(dbid)+f"IF EXISTS(SELECT 1 FROM sys.server_principals WHERE name IN({names()}) OR sid IN({ids})) THROW 51004,'FAIL_STATE: Logins must be absent before DB drop.',1;USE master;ALTER DATABASE {DATABASE} SET SINGLE_USER WITH ROLLBACK IMMEDIATE;DROP DATABASE {DATABASE};"+SUMMARY

def review_sources(sids):
    # Fixed source-preview bindings, never an execution admission or actual identity.
    result={'10_Setup.sql':setup(sids),'11_Logins.sql':create_logins(5,sids),'80_State.sql':state(5),'81_Identity.sql':creator()+"DECLARE @J nvarchar(max)=(SELECT DB_ID() DatabaseId,OBJECT_ID(N'lab.Documents',N'U') ObjectId FOR JSON PATH,WITHOUT_ARRAY_WRAPPER,INCLUDE_NULL_VALUES);"+OUTPUT,'90_Cleanup.sql':cleanup_db(5,sids),'91_Absence.sql':absence(sids),'40_Revoke.sql':grant(5,True),'41_Restore.sql':grant(5)}
    for lane in oracle.LOGINS:result['20_Auth'+lane+'.sql']=authenticated('ROWS',lane,5)
    result['21_Spoof.sql']=authenticated('ROWS','A',5,True)
    for kind in ('ALTER','IMPERSONATE','REVOKED_SELECT'):result['30_'+kind+'.sql']=authenticated(kind,'A',5)
    # This held-byte placeholder is explicitly a generator/guard preview only.
    result['89_DropGuard.sql']=drop_login(5,'A','7B007D00',sids,tuple(oracle.LOGINS))
    if any(len(text.encode('utf-8'))>160000 for text in result.values()):raise ValueError('Bound preview input population')
    return result

def pool_absence(dbid,ids):
    if type(ids) is not list or len(ids)!=3 or len(set(ids))!=3:raise ValueError('Three own held physical IDs required')
    for value in ids:oracle.guid(value)
    literals=','.join("CONVERT(uniqueidentifier,'"+value+"')" for value in ids)
    return bound(dbid)+f"IF EXISTS(SELECT 1 FROM sys.dm_exec_connections WHERE connection_id IN({literals})) THROW 51003,'FAIL_STATE: Own pooled physical connection residue.',1;SELECT 'POOLPUBLIC_PHYSICAL|ABSENT';"


def source_assertion(dbid):
    return bound(dbid)+"IF (SELECT COUNT(*) FROM lab.Documents)<>2 OR NOT EXISTS(SELECT 1 FROM lab.Documents WHERE Id=1 AND TenantId=1 AND DATALENGTH(Content)=DATALENGTH(N'Synthetische Quelle A') AND CONVERT(varbinary(max),Content)=CONVERT(varbinary(max),N'Synthetische Quelle A') AND CONVERT(int,VECTORPROPERTY(V,'Dimensions'))=3 AND VECTOR_DISTANCE('cosine',V,CONVERT(VECTOR(3),'[1,0,0]'))=0) OR NOT EXISTS(SELECT 1 FROM lab.Documents WHERE Id=2 AND TenantId=2 AND DATALENGTH(Content)=DATALENGTH(N'Synthetische Quelle B') AND CONVERT(varbinary(max),Content)=CONVERT(varbinary(max),N'Synthetische Quelle B') AND CONVERT(int,VECTORPROPERTY(V,'Dimensions'))=3 AND VECTOR_DISTANCE('cosine',V,CONVERT(VECTOR(3),'[1,0,0]'))=0) THROW 51003,'FAIL_RESULT_CONTRACT: Vollstaendige Quelle fehlt.',1;"+SUMMARY

def source_delete(dbid):return bound(dbid)+"DELETE lab.Documents WHERE Id=2;IF @@ROWCOUNT<>1 THROW 51003,'FAIL_RESULT_CONTRACT: Eigene Mutation fehlt.',1;"+SUMMARY

def source_restore(dbid):return bound(dbid)+"IF (SELECT COUNT(*) FROM lab.Documents)<>1 OR EXISTS(SELECT 1 FROM lab.Documents WHERE Id=2) THROW 51004,'FAIL_STATE: Restoreziel fremd.',1;INSERT lab.Documents VALUES(2,2,N'Synthetische Quelle B',CONVERT(VECTOR(3),'[1,0,0]'));"+SUMMARY

def marker_change(dbid,key):
    if key not in MARKERS:raise ValueError('Fester Marker erforderlich')
    return bound(dbid)+f"EXEC sys.sp_updateextendedproperty @name={literal(key)},@value=N'FOREIGN';"+SUMMARY

def marker_restore(dbid,key):
    if key not in MARKERS:raise ValueError('Fester Marker erforderlich')
    invalid=MARKERS|{key:'FOREIGN'}
    return bound(dbid,invalid)+f"EXEC sys.sp_updateextendedproperty @name={literal(key)},@value={literal(MARKERS[key])};"+SUMMARY
