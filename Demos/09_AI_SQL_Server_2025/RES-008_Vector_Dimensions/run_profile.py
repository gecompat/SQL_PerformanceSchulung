#!/usr/bin/env python3
"""Begrenzter RES-008-Consumer; Import führt keine SQL-Calls oder Provisionierung aus."""
from __future__ import annotations
import argparse,json,math,os,re,sys,time
from dataclasses import dataclass
from pathlib import Path

FOLDER=Path(__file__).resolve().parent;ROOT=FOLDER.parents[2]
sys.path[:0]=[str(FOLDER),str(ROOT/'Demos/00_Framework/Tools')]
import res008_source as source,res008_measurement as measurement,res008_plans as plans
import res008_summary as summary
from sqlcmd_process import build_sqlcmd_command,collect_process,resolve_sqlcmd,start_sqlcmd

DATABASE='SQLPERF_LAB_RES008_LOCAL'
SUMMARY=re.compile(r'^SQLPERF_SUMMARY\|(PASS|WARN|SKIP|FAIL)\|([A-Z][A-Z0-9_]*)$',re.M)
SCRIPTS={'00_Preflight.sql','10_Setup.sql','20_Probe.sql','21_DeleteOwnRow.sql','22_Database.sql','30_Window.sql','40_Plan.sql','90_Cleanup.sql','91_Absence.sql'}

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
            and not result.evidence.get('windows') and not result.evidence.get('plans'))

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
    try:
        env={k:v for k,v in os.environ.items() if k.casefold()!='sqlcmdini'}
        attempted=True;process=start_sqlcmd(command,environment=env)
        response=collect_process(process,command,timeout_seconds=timeout_seconds)
        if client_end(process)!=response.returncode:raise ClientEndUnknown('Native Endstatusbindung fehlt')
        return response
    finally:
        if process is not None:client_end(process)
        elif attempted:raise ClientEndUnknown('Native Clientende unbekannt')

def command_for(executable,server,auth,username,filename,*,variables=None,full_scalar=False):
    if filename not in SCRIPTS:raise ValueError('Feste SQL-Phase erforderlich')
    permitted={'Dimension':{str(d) for d in source.DIMS},'Statements':{'1','100'},'Negative':{'0','1'}}
    variables=variables or {}
    if any(k not in permitted or v not in permitted[k] for k,v in variables.items()):raise ValueError('Freie SQL-Variable abgewiesen')
    values={'DemoId':'RES-008','RunToken':'LOCAL','TargetDatabase':DATABASE,'ConfirmIsolatedLab':'1','HighImpactConfirmed':'1',**variables}
    database='master' if filename in {'00_Preflight.sql','10_Setup.sql','90_Cleanup.sql','91_Absence.sql'} else DATABASE
    command=build_sqlcmd_command(executable=executable,server=server,auth=auth,username=username,database=database,script=FOLDER/filename,variables=values)
    command.extend(['-C','-l','2'])
    if full_scalar:
        command.remove('-W');at=command.index('-h');del command[at:at+2];command.extend(['-y','0'])
    return command

def native_error(output,code,detail):
    headers=list(re.finditer(r'^Msg ([0-9]+), Level [0-9]+, State [0-9]+(?:, [^\r\n]*)?\r?\n([^\r\n]+)',output,re.M))
    return len(headers)==len(re.findall(r'^Msg [0-9]+\b',output,re.M))==1 and int(headers[0].group(1))==code and re.fullmatch(re.escape(detail)+r':[^\r\n]*',headers[0].group(2).strip()) is not None

def run_profile(*,executable,server,auth='sql',username='sa',confirmed,high_impact,
                executor=execute_client,clock=time.monotonic,normal_deadline=None,cleanup_started=None,fault=None):
    if confirmed is not True or high_impact is not True or fault not in (None,'after_setup'):raise ValueError('Lokale YELLOW-Bestaetigung und fester Fault erforderlich')
    regular=Deadline(300,clock)
    if normal_deadline is not None:
        if type(normal_deadline) not in (int,float) or not math.isfinite(normal_deadline):raise ValueError('Tatsaechliche Parentdeadline erforderlich')
        regular.end=min(regular.end,normal_deadline)
    started=False;unknown=False;cleanup_ok=False;phases=[];captured={'qualification':'BOUNDED_PROFILE_ONLY'}
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
    def capture_source():return source.evidence(phase('20_Probe.sql'))
    def same(before,after):
        if before[0]!=after[0] or before[3]!=after[3]:raise ValueError('Vollstaendige Quellen oder Konfiguration veraendert')
    try:
        phase('91_Absence.sql');phase('00_Preflight.sql');phase('10_Setup.sql')
        if fault=='after_setup':
            captured['controlled_fault']='AFTER_PASS_SETUP_BEFORE_SOURCE'
            phases.append(('CONTROLLED_FAULT_AFTER_SETUP','FAIL','FAIL_EXECUTION'))
            raise PhaseStop('FAIL','FAIL_EXECUTION')
        baseline=capture_source();phase('10_Setup.sql');same(baseline,capture_source())
        phase('21_DeleteOwnRow.sql');phase('20_Probe.sql',negative=True)
        phase('10_Setup.sql');same(baseline,capture_source())
        output=phase('22_Database.sql')
        attested=[s.strip() for s in output.splitlines() if s.strip().startswith('RES008_ATTEST_DB|')]
        if len(attested)!=1 or not re.fullmatch(r'RES008_ATTEST_DB\|[0-9]+',attested[0]):raise ValueError('Unabhaengige eigene DB-ID fehlt')
        database_id=measurement.integer(int(attested[0].split('|')[1]),5)
        collected=[];identities=set();previous=None
        def window(d,statements,labels):
            nonlocal previous
            output=phase('30_Window.sql',variables={'Dimension':str(d),'Statements':str(statements),'Negative':'0'})
            actual=measurement.decode(output)
            identity=measurement.validate(actual,d,statements,database_id)
            if identity in identities or (previous is not None and measurement.stamp(actual['StartedUtc'])<previous):raise ValueError('Eindeutige serielle Requestbindung fehlt')
            identities.add(identity);previous=measurement.stamp(actual['EndedUtc']);collected.append({'labels':labels,'actual':actual})
        for d in source.DIMS:
            for ordinal in range(1,6):window(d,1,{'kind':'WARMUP','dimension':d,'ordinal':ordinal})
        for pair,block,order,slot,d in measurement.slots():window(d,100,{'kind':'MEASURED','pair':pair,'block':block,'order':order,'slot':slot})
        phase('30_Window.sql',variables={'Dimension':'32','Statements':'1','Negative':'1'},negative=True)
        same(baseline,capture_source());captured['windows']=collected
        actual_plans=[plans.capture(phase('40_Plan.sql',variables={'Dimension':str(d)},full_scalar=True),d) for d in source.DIMS]
        same(baseline,capture_source());captured['plans']=actual_plans
        captured.update(source_config_equal=True,negative_source_actual=True,negative_query_actual=True,storage=baseline[1],database_id=database_id)
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
                cleanup_ok=absent.splitlines().count('RES008_DB|ABSENT')==1 and clock()<=recovery.end
            except (OSError,ValueError,RuntimeError,TimeoutError,KeyboardInterrupt):cleanup_ok=False
        if not cleanup_ok:outcome,code='FAIL','FAIL_CLEANUP'
    return Result(outcome,code,cleanup_ok,unknown,tuple(phases),captured)

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--server',required=True);parser.add_argument('--sqlcmd');parser.add_argument('--username',default='sa')
    parser.add_argument('--confirm-isolated-lab',action='store_true');parser.add_argument('--high-impact-confirmed',action='store_true')
    parser.add_argument('--summary',action='store_true',help='Nur geprüfte aggregierte Werte nach erfolgreichem begrenztem Profil ausgeben')
    args=parser.parse_args()
    try:result=run_profile(executable=resolve_sqlcmd(args.sqlcmd),server=args.server,username=args.username,confirmed=args.confirm_isolated_lab,high_impact=args.high_impact_confirmed)
    except FileNotFoundError:print('SQLPERF_SUMMARY|SKIP|SKIP_TOOL_MISSING');return 0
    except (ValueError,OSError):print('SQLPERF_SUMMARY|FAIL|FAIL_SAFETY');return 1
    if args.summary and result.outcome=='WARN':
        try:aggregate=summary.summarize_result(result)
        except (OSError,ValueError,TypeError,KeyError):print('SQLPERF_SUMMARY|FAIL|FAIL_RESULT_CONTRACT');return 1
        print('RES008_AGGREGATE|'+json.dumps(aggregate,sort_keys=True,allow_nan=False))
    print('RES008_PROFILE|BOUNDED_ONLY|WINDOWS_'+str(len(result.evidence.get('windows',())))+'|PLANS_'+str(len(result.evidence.get('plans',())))+'|CLEANUP_'+str(result.cleanup_ok))
    print('SQLPERF_SUMMARY|'+result.outcome+'|'+result.code)
    return 1 if result.outcome=='FAIL' else 0

if __name__=='__main__':raise SystemExit(main())
