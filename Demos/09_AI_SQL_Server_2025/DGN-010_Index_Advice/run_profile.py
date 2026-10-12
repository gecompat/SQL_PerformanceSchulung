#!/usr/bin/env python3
"""Begrenzter DGN-010-Consumer; Import führt keine SQL-Calls oder Provisionierung aus."""
from __future__ import annotations
import argparse,json,math,os,re,sys,time
from dataclasses import dataclass,replace
from pathlib import Path

FOLDER=Path(__file__).resolve().parent;ROOT=FOLDER.parents[2]
sys.path[:0]=[str(FOLDER),str(ROOT/'Demos/00_Framework/Tools'),str(ROOT/'Tests/Static')]
import dgn010_source as source
import dgn010_window_evidence as measurement,dgn010_benchmark_evidence as benchmark
from sqlcmd_process import build_sqlcmd_command,collect_process,resolve_sqlcmd,start_sqlcmd

DATABASE='SQLPERF_LAB_DGN010_LOCAL'
SUMMARY=re.compile(r'^SQLPERF_SUMMARY\|(PASS|WARN|SKIP|FAIL)\|([A-Z][A-Z0-9_]*)$',re.M)
LABELS={'CONTROL_0','NEGATIVE_0'}|{f'WARMUP_{p}_{i}' for p in (0,1) for i in range(5)}|{f'{o}_{b}_{s}_{p}' for b,o,s,p in measurement.slots()}
SCRIPTS={'00_Preflight.sql','10_Setup.sql','20_Probe.sql','21_DeleteOwnRow.sql','22_Database.sql','24_Candidate.sql','40_SelectWindow.sql','50_DmlWindow.sql','90_Cleanup.sql','91_Absence.sql'}

class ClientEndUnknown(RuntimeError):pass
class SqlFailure(RuntimeError):pass
class PhaseStop(RuntimeError):
    def __init__(self,outcome,code):self.outcome,self.code=outcome,code

@dataclass(frozen=True)
class Result:
    outcome:str
    code:str
    cleanup_ok:bool
    client_end_unknown:bool
    phases:tuple
    evidence:dict

def setup_fault_completed(result):
    expected=(('91_Absence.sql','PASS','OK'),('00_Preflight.sql','PASS','OK'),
              ('10_Setup.sql','PASS','OK'),('CONTROLLED_FAULT_AFTER_SETUP','FAIL','FAIL_EXECUTION'),
              ('90_Cleanup.sql','PASS','OK'),('91_Absence.sql','PASS','OK'))
    return ((result.outcome,result.code)==('FAIL','FAIL_EXECUTION') and result.cleanup_ok
            and not result.client_end_unknown and result.phases==expected
            and result.evidence.get('controlled_fault')=='AFTER_PASS_SETUP_BEFORE_SOURCE'
            and 'record' not in result.evidence and 'aggregate' not in result.evidence)

class Deadline:
    def __init__(self,seconds,clock):self.clock,self.end=clock,clock()+seconds
    def remaining(self,cap):
        remaining=min(cap,self.end-self.clock())
        if remaining<=0:raise TimeoutError('Gemeinsames Zeitbudget verbraucht')
        return remaining

def client_end(process):
    try:status=process.poll()
    except BaseException as error:raise ClientEndUnknown('Native Pollauswertung unbekannt') from error
    if type(status) is not int:raise ClientEndUnknown('Native Clientende unbekannt')
    return status

def execute_client(command,*,timeout_seconds):
    process=None;attempted=False
    proxies=[Path(a).resolve() for a in command if str(a).lower().endswith('.py')]
    remote=bool(proxies)
    if remote and proxies!=[(ROOT/'Tests/Runtime/dgn010_docker_sqlcmd_proxy.py').resolve()]:
        raise ClientEndUnknown('Unbekannter Pythontransport ohne Remote-Endvertrag')
    try:
        env={k:v for k,v in os.environ.items() if k.casefold()!='sqlcmdini'}
        attempted=True;process=start_sqlcmd(command,environment=env)
        try:response=collect_process(process,command,timeout_seconds=timeout_seconds)
        except BaseException as error:
            if remote:raise ClientEndUnknown('Remote-Ende nach Collectorabbruch unbekannt') from error
            raise
        if client_end(process)!=response.returncode:raise ClientEndUnknown('Native Endstatusbindung fehlt')
        if remote:response=remote_end(response)
        return response
    finally:
        if process is not None:client_end(process)
        elif attempted:raise ClientEndUnknown('Native Clientende unbekannt')

def remote_end(response):
    if response.timed_out:raise ClientEndUnknown('Remote-Ende nach Timeout unbekannt')
    lines=response.stderr.splitlines();frames=[(i,line) for i,line in enumerate(lines) if line.startswith('DGN010_REMOTE_END|')]
    if len(frames)!=1:raise ClientEndUnknown('Genau ein tatsächlicher Remote-Endframe erforderlich')
    index,frame=frames[0];match=re.fullmatch(r'DGN010_REMOTE_END\|([0-9]+)',frame)
    if not match or type(response.returncode) is not int or int(match[1])!=response.returncode or any(line.strip() for line in lines[index+1:]):
        raise ClientEndUnknown('Remote-/Transportendstatus inkohärent')
    # Nur das feste Shell-Waitattest entfernen; sämtliche native Fehler bleiben.
    return replace(response,stderr='\n'.join(lines[:index]))

def command_for(executable,server,auth,username,filename,*,variables=None,full_scalar=False):
    if filename not in SCRIPTS:raise ValueError('Feste SQL-Phase erforderlich')
    permitted={'Path':{'0','1'},'Statements':{'1','100'},'Negative':{'0','1'},'Label':LABELS}
    variables=variables or {}
    if any(k not in permitted or v not in permitted[k] for k,v in variables.items()):raise ValueError('Freie SQL-Variable abgewiesen')
    values={'DemoId':'DGN-010','RunToken':'LOCAL','TargetDatabase':DATABASE,'ConfirmIsolatedLab':'1','HighImpactConfirmed':'1',**variables}
    database='master' if filename in {'00_Preflight.sql','10_Setup.sql','90_Cleanup.sql','91_Absence.sql'} else DATABASE
    command=build_sqlcmd_command(executable=executable,server=server,auth=auth,username=username,database=database,script=FOLDER/filename,variables=values)
    command.extend(['-C','-l','2'])
    if full_scalar:
        command.remove('-W');at=command.index('-h');del command[at:at+2];command.extend(['-y','0'])
    return command

def native_error(output,code,detail):
    frame='\n'.join(line.strip() for line in output.splitlines() if line.strip())
    return re.fullmatch(r'Msg '+re.escape(str(code))+r', Level [0-9]+, State [0-9]+(?:, [^\r\n]*)?\n'+re.escape(detail)+r':[^\r\n]*',frame) is not None

def run_profile(*,executable,server,auth='sql',username='sa',confirmed,high_impact,
                scope,executor=execute_client,clock=time.monotonic,normal_deadline=None,cleanup_started=None,fault=None):
    if confirmed is not True or high_impact is not True or fault not in (None,'after_setup'):raise ValueError('Lokale YELLOW-Bestaetigung und fester Fault erforderlich')
    measurement.scope_prefix(scope)
    regular=Deadline(300,clock)
    if normal_deadline is not None:
        if type(normal_deadline) not in (int,float) or not math.isfinite(normal_deadline):raise ValueError('Tatsaechliche Parentdeadline erforderlich')
        regular.end=min(regular.end,normal_deadline)
    started=False;unknown=False;cleanup_ok=False;phases=[];captured={'qualification':'BOUNDED_PROFILE_ONLY','scope':scope}
    outcome,code='WARN','WARN_OPTIONAL_EVIDENCE_SKIPPED'
    def phase(filename,*,variables=None,budget=None,full_scalar=False,negative=False):
        nonlocal started,unknown
        if unknown:raise ClientEndUnknown('Keine weitere SQL-Ausfuehrung nach UNKNOWN')
        command=command_for(executable,server,auth,username,filename,variables=variables,full_scalar=full_scalar)
        seconds=(budget or regular).remaining(20 if budget else 30)
        if filename=='10_Setup.sql':started=True
        try:response=executor(command,timeout_seconds=seconds)
        except ClientEndUnknown:unknown=True;raise
        output=response.stdout+'\n'+response.stderr
        if len(output.encode('utf-8'))>1000000:raise ValueError('Bounded native output required')
        if response.timed_out:raise TimeoutError('Native Requesttimeout')
        if response.returncode!=0:
            if negative and native_error(output,51003,'FAIL_RESULT_CONTRACT'):
                phases.append((filename,'EXPECTED_REJECTION','51003'));return output
            raise SqlFailure('Native Phase fehlgeschlagen')
        if negative:raise ValueError('Tatsaechliche Negativkontrolle akzeptiert')
        matches=SUMMARY.findall('\n'.join(line.strip() for line in output.splitlines()))
        if len(matches)!=1:raise ValueError('Ein vollstaendiger Phasensummary erforderlich')
        actual=matches[0];phases.append((filename,*actual))
        if actual!=('PASS','OK'):
            if filename=='00_Preflight.sql' and actual in {('SKIP','SKIP_VERSION'),('SKIP','SKIP_CONFIGURATION'),('SKIP','SKIP_PERMISSION')}:raise PhaseStop(*actual)
            raise ValueError('Unerwarteter Phasenstatus')
        return output
    snapshots=[];records=[];identities=set();previous=None;present=False;changes=[]
    def snapshot():
        data=source.evidence(phase('20_Probe.sql'),int(present))
        if snapshots and data[0]!=snapshots[0][0]:raise ValueError('Vollständige Source verändert')
        snapshots.append(data)
    def candidate(path):
        nonlocal present
        if bool(path)!=present:
            output=phase('24_Candidate.sql',variables={'Path':str(path)})
            if [s for s in output.splitlines() if s.startswith('DGN010_CANDIDATE|')]!=['DGN010_CANDIDATE|STATE_'+str(path)]:raise ValueError('Native Indexzustandsbindung fehlt')
            present=bool(path);changes.append(path)
        snapshot()
    def window(path,label,statements,negative=False):
        nonlocal previous
        name='40_SelectWindow.sql' if scope=='SELECT' else '50_DmlWindow.sql'
        output=phase(name,variables={'Path':str(path),'Label':label,'Statements':str(statements),'Negative':str(int(negative))},negative=negative)
        if negative:return None
        data=measurement.decode(output,scope);identity=measurement.validate(data,path,label,statements,dbid,scope)
        if identity in identities or (previous is not None and measurement.stamp(data['StartedUtc'])<previous):raise ValueError('Eindeutige serielle Fensterbindung fehlt')
        identities.add(identity);previous=measurement.stamp(data['EndedUtc']);return data
    try:
        phase('91_Absence.sql');phase('00_Preflight.sql');phase('10_Setup.sql')
        if fault=='after_setup':
            captured['controlled_fault']='AFTER_PASS_SETUP_BEFORE_SOURCE'
            phases.append(('CONTROLLED_FAULT_AFTER_SETUP','FAIL','FAIL_EXECUTION'))
            raise PhaseStop('FAIL','FAIL_EXECUTION')
        snapshot();phase('10_Setup.sql');snapshot()
        phase('21_DeleteOwnRow.sql');phase('20_Probe.sql',negative=True)
        phase('10_Setup.sql');snapshot()
        output=phase('22_Database.sql')
        attested=[s for s in output.splitlines() if s.startswith('DGN010_DBID|')]
        if len(attested)!=1 or not re.fullmatch(r'DGN010_DBID\|[0-9]+',attested[0]):raise ValueError('Unabhängige eigene DB-ID fehlt')
        dbid=measurement.integer(int(attested[0].split('|')[1]),5)
        window(0,'NEGATIVE_0',1,True);snapshot();control=window(0,'CONTROL_0',1);snapshot()
        for path in (0,1):
            candidate(path)
            for index in range(5):
                label=f'WARMUP_{path}_{index}'
                records.append({'kind':'WARMUP','path':path,'label':label,'data':window(path,label,1)})
            snapshot()
        for block,order,slot,path in measurement.slots():
            candidate(path);label=f'{order}_{block}_{slot}_{path}'
            records.append({'kind':'MEASURED','block':block,'order':order,'slot':slot,'path':path,'label':label,'data':window(path,label,100)})
            snapshot()
        candidate(0)
        record={'database_id':dbid,'records':records,'query_control':control,'source_snapshots':snapshots,'candidate_transitions':changes,
                'source_negative_51003':True,'query_negative_51003':True,'source_config_equal':True,'reader_rights_unchanged':True,'coverage':benchmark.SCOPES[scope]}
        aggregate=benchmark.validate_benchmark(record,scope=scope,expected_database_id=dbid)
        contract=json.loads((ROOT/'Tests/Static/Fixtures/dgn010'/('DGN010_'+scope+'.result-contract.json')).read_text(encoding='utf-8'))
        fwk=benchmark.evaluate_invariants(aggregate,contract)
        captured.update(record=record,aggregate=aggregate,fwk011=fwk)
    except PhaseStop as stop:outcome,code=stop.outcome,stop.code
    except ClientEndUnknown:outcome,code='FAIL','FAIL_CLEANUP'
    except TimeoutError:outcome,code='FAIL','FAIL_TIMEOUT'
    except KeyboardInterrupt:outcome,code='FAIL','FAIL_EXECUTION'
    except (OSError,ValueError,RuntimeError,KeyError,TypeError,json.JSONDecodeError):outcome,code='FAIL','FAIL_RESULT_CONTRACT'
    finally:
        recovery=Deadline(60,clock)
        if cleanup_started is not None:
            parent_end=cleanup_started()
            if type(parent_end) not in (int,float) or not math.isfinite(parent_end):unknown=True
            else:recovery.end=min(recovery.end,parent_end)
        if not unknown:
            try:
                if started:phase('90_Cleanup.sql',budget=recovery)
                absent=phase('91_Absence.sql',budget=recovery)
                cleanup_ok=absent.splitlines().count('DGN010_DB|ABSENT')==1 and clock()<=recovery.end
            except (OSError,ValueError,RuntimeError,TimeoutError,KeyboardInterrupt):cleanup_ok=False
        if not cleanup_ok:outcome,code='FAIL','FAIL_CLEANUP'
    return Result(outcome,code,cleanup_ok,unknown,tuple(phases),captured)

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--server',required=True);parser.add_argument('--sqlcmd');parser.add_argument('--username',default='sa')
    parser.add_argument('--confirm-isolated-lab',action='store_true');parser.add_argument('--high-impact-confirmed',action='store_true')
    parser.add_argument('--summary',action='store_true',help='Nur geprüfte aggregierte Werte nach erfolgreichem begrenztem Profil ausgeben')
    parser.add_argument('--scope',choices=('SELECT','DML'),required=True)
    args=parser.parse_args()
    try:result=run_profile(executable=resolve_sqlcmd(args.sqlcmd),server=args.server,username=args.username,scope=args.scope,confirmed=args.confirm_isolated_lab,high_impact=args.high_impact_confirmed)
    except FileNotFoundError:print('SQLPERF_SUMMARY|SKIP|SKIP_TOOL_MISSING');return 0
    except (ValueError,OSError):print('SQLPERF_SUMMARY|FAIL|FAIL_SAFETY');return 1
    if args.summary and result.outcome=='WARN':
        if not result.cleanup_ok or result.client_end_unknown or 'aggregate' not in result.evidence:
            print('SQLPERF_SUMMARY|FAIL|FAIL_RESULT_CONTRACT');return 1
        print('DGN010_AGGREGATE|'+json.dumps(result.evidence['aggregate'],sort_keys=True,allow_nan=False))
    print('DGN010_PROFILE|'+args.scope+'|BOUNDED_ONLY|CLEANUP_'+str(result.cleanup_ok))
    print('SQLPERF_SUMMARY|'+result.outcome+'|'+result.code)
    return 1 if result.outcome=='FAIL' else 0

if __name__=='__main__':raise SystemExit(main())
