#!/usr/bin/env python3
"""Begrenzter eigener DGN-010-Kostencontroller; kein Provisioning beim Import."""
from __future__ import annotations
import argparse,json,math,os,re,sys,tempfile,time
from pathlib import Path

FOLDER=Path(__file__).resolve().parent;ROOT=FOLDER.parents[2]
sys.path[:0]=[str(FOLDER),str(ROOT/'Demos/00_Framework/Tools'),str(ROOT/'Tests/Static')]
import run_profile as profile
import dgn010_cost_evidence as costs,dgn010_cost_inputs as inputs

def run_cost_profile(*,executable,server,auth='sql',username='sa',confirmed,high_impact,
                     executor=profile.execute_client,clock=time.monotonic,
                     normal_deadline=None,cleanup_started=None,fault=None,input_folder=None):
    if confirmed is not True or high_impact is not True or fault not in (None,'after_setup'):raise ValueError('Lokale YELLOW-Bestaetigung und fester Fault erforderlich')
    regular=profile.Deadline(300,clock)
    if normal_deadline is not None:
        if type(normal_deadline) not in (int,float) or not math.isfinite(normal_deadline):raise ValueError('Tatsaechliche Parentdeadline erforderlich')
        regular.end=min(regular.end,normal_deadline)
    started=False;unknown=False;cleanup_ok=False;phases=[]
    captured={'qualification':'BOUNDED_COST_PROFILE_ONLY','scope':'TWO_OWN_CREATE_DROP_CYCLES_ONLY'}
    outcome,code='WARN','WARN_OPTIONAL_EVIDENCE_SKIPPED'
    owned=[];kept=[]
    folder=Path(input_folder) if input_folder is not None else ROOT/'Runtime/DGN010_COST_PROFILE'

    def invoke(command,label,*,budget=None,negative=False,summary=True):
        nonlocal unknown
        if unknown:raise profile.ClientEndUnknown('Sticky UNKNOWN sperrt weitere SQLclients')
        seconds=(budget or regular).remaining(20 if budget else 30)
        try:response=executor(command,timeout_seconds=seconds)
        except profile.ClientEndUnknown:unknown=True;raise
        output=response.stdout+'\n'+response.stderr
        if len(output.encode('utf-8'))>1000000:raise ValueError('Begrenzter nativer Output erforderlich')
        if response.timed_out:raise TimeoutError('Nativer Requesttimeout')
        if response.returncode!=0:
            if negative and profile.native_error(output,51003,'FAIL_RESULT_CONTRACT'):
                phases.append((label,'EXPECTED_REJECTION','51003'));return output
            raise profile.SqlFailure('Native Kostenphase fehlgeschlagen')
        if negative:raise ValueError('Tatsaechliche Negativkontrolle akzeptiert')
        if summary:
            matches=profile.SUMMARY.findall('\n'.join(line.strip() for line in output.splitlines()))
            if len(matches)!=1:raise ValueError('Genau ein vollstaendiger Phasensummary erforderlich')
            actual=matches[0];phases.append((label,*actual))
            if actual!=('PASS','OK'):
                if label=='00_Preflight.sql' and actual in {('SKIP','SKIP_VERSION'),('SKIP','SKIP_CONFIGURATION'),('SKIP','SKIP_PERMISSION')}:raise profile.PhaseStop(*actual)
                raise ValueError('Unerwarteter Phasenstatus')
        else:phases.append((label,'RECEIVED','UNVALIDATED'))
        return output

    def phase(filename,*,budget=None,negative=False):
        nonlocal started
        if unknown:raise profile.ClientEndUnknown('Sticky UNKNOWN sperrt weitere SQLclients')
        command=profile.command_for(executable,server,auth,username,filename)
        if filename=='10_Setup.sql':started=True
        return invoke(command,filename,budget=budget,negative=negative)

    def raw(sql,label,*,negative=False,summary=True):
        if unknown:raise profile.ClientEndUnknown('Sticky UNKNOWN sperrt SQLinputs')
        if type(sql) is not str or len(sql.encode('utf-8'))>160000:raise ValueError('Begrenzter fester SQLinput erforderlich')
        folder.mkdir(parents=True,exist_ok=True)
        descriptor,name=tempfile.mkstemp(prefix='cost-own-',suffix='.sql',dir=folder)
        path=Path(name);owned.append(path)
        try:
            with os.fdopen(descriptor,'w',encoding='utf-8',newline='') as stream:stream.write(sql)
            command=profile.build_sqlcmd_command(executable=executable,server=server,auth=auth,username=username,database=profile.DATABASE,script=path,variables={})
            command.remove('-W');at=command.index('-h');del command[at:at+2];command.extend(['-y','0'])
            command.extend(['-C','-l','2'])
            return invoke(command,label,negative=negative,summary=summary)
        finally:
            if unknown:kept.append(path)
            else:
                try:path.unlink(missing_ok=True)
                except OSError:kept.append(path);raise

    snapshots=[];states=[];records=[];present=0;dbid=None;object_id=None;held=costs.EMPTY
    def snapshot():
        actual=profile.source.evidence(phase('20_Probe.sql'),present)
        if snapshots and actual[0]!=snapshots[0][0]:raise ValueError('Vollstaendige Source veraendert')
        snapshots.append(actual)
    def state():
        actual=inputs.markers.decode(raw(inputs.state_sql(database_id=dbid,object_id=object_id),'FULL_STATE',summary=False))
        costs.full_state(actual,dbid,object_id)
        phases[-1]=('FULL_STATE','PASS','OK')
        return actual

    try:
        phase('91_Absence.sql');preflight=phase('00_Preflight.sql');phase('10_Setup.sql')
        if fault=='after_setup':
            captured['controlled_fault']='AFTER_PASS_SETUP_BEFORE_SOURCE'
            phases.append(('CONTROLLED_FAULT_AFTER_SETUP','FAIL','FAIL_EXECUTION'))
            raise profile.PhaseStop('FAIL','FAIL_EXECUTION')
        snapshot();phase('10_Setup.sql');snapshot()
        phase('21_DeleteOwnRow.sql');phase('20_Probe.sql',negative=True)
        phase('10_Setup.sql');snapshot()
        output=phase('22_Database.sql')
        attested=[s for s in output.splitlines() if s.startswith('DGN010_DBID|')]
        if len(attested)!=1 or not re.fullmatch(r'DGN010_DBID\|[0-9]+',attested[0]):raise ValueError('Unabhaengige tatsächliche DB-ID fehlt')
        dbid=costs.window.integer(int(attested[0].split('|')[1]),5)
        # Erst eigener markergebundener Katalogread; danach jeden Snapshot an dessen OID binden.
        initial=inputs.markers.decode(raw(inputs.markers.binding(inputs.markers.MARKERS,dbid)+inputs.markers.STATE_SQL,'INITIAL_STATE',summary=False))
        own=[r for r in initial['objects'] if r.get('name')=='SourceRows']
        if len(own)!=1:raise ValueError('Unabhaengige tatsächliche Source-OID fehlt')
        object_id=costs.window.integer(own[0]['object_id'],1)
        costs.full_state(initial,dbid,object_id);phases[-1]=('INITIAL_STATE','PASS','OK')
        negative_before=initial
        raw(inputs.drop_absent_sql(database_id=dbid,object_id=object_id),'DROP_ABSENT',negative=True)
        negative_after=state();snapshot()
        if json.dumps(negative_before,sort_keys=True)!=json.dumps(negative_after,sort_keys=True):raise ValueError('Vollstate nach abgewiesenem DROP veraendert')
        for ordinal,kind in enumerate(('CREATE','DROP','CREATE','DROP')):
            cycle=ordinal//2+1;before=state()
            output=raw(inputs.build_sql(database_id=dbid,object_id=object_id,kind=kind,cycle=cycle,held_lease=held),kind+'_'+str(cycle))
            data=costs.decode(output);costs.validate(data,kind,cycle,dbid,object_id,held)
            after=state();costs.transition(before,after,kind,data)
            states.append([before,after]);records.append(data);held=data['LeaseAfter'];present=int(kind=='CREATE');snapshot()
        record={'database_id':dbid,'object_id':object_id,'preflight':preflight,'records':records,'source_snapshots':snapshots,'full_states':states,'negative_states':[negative_before,negative_after],
                'source_negative_51003':True,'drop_absent_negative_51003':True,'scope':'TWO_OWN_CREATE_DROP_CYCLES_ONLY','full_worker_costs':'NOT_ESTABLISHED','index_net_benefit':'NOT_ESTABLISHED','runtime_qualification':'NOT_ESTABLISHED'}
        aggregate=costs.report(record,expected_database_id=dbid)
        captured.update(record=record,aggregate=aggregate)
    except profile.PhaseStop as stop:outcome,code=stop.outcome,stop.code
    except profile.ClientEndUnknown:outcome,code='FAIL','FAIL_CLEANUP'
    except TimeoutError:outcome,code='FAIL','FAIL_TIMEOUT'
    except KeyboardInterrupt:outcome,code='FAIL','FAIL_EXECUTION'
    except (OSError,ValueError,RuntimeError,KeyError,TypeError,json.JSONDecodeError):outcome,code='FAIL','FAIL_RESULT_CONTRACT'
    finally:
        recovery=profile.Deadline(60,clock)
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
    remaining=[path for path in owned if path.exists()]
    captured['own_input_files_preserved']=len(remaining)
    if remaining:outcome,code='FAIL','FAIL_CLEANUP';cleanup_ok=False
    return profile.Result(outcome,code,cleanup_ok,unknown,tuple(phases),captured)

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--server',required=True);parser.add_argument('--sqlcmd');parser.add_argument('--username',default='sa')
    parser.add_argument('--confirm-isolated-lab',action='store_true');parser.add_argument('--high-impact-confirmed',action='store_true')
    parser.add_argument('--summary',action='store_true',help='Nur geprüfte aggregierte Werte nach erfolgreichem begrenztem Profil ausgeben')
    args=parser.parse_args()
    try:result=run_cost_profile(executable=profile.resolve_sqlcmd(args.sqlcmd),server=args.server,username=args.username,confirmed=args.confirm_isolated_lab,high_impact=args.high_impact_confirmed)
    except FileNotFoundError:print('SQLPERF_SUMMARY|SKIP|SKIP_TOOL_MISSING');return 0
    except (ValueError,OSError):print('SQLPERF_SUMMARY|FAIL|FAIL_SAFETY');return 1
    if args.summary and result.outcome=='WARN':
        if not result.cleanup_ok or result.client_end_unknown or 'aggregate' not in result.evidence:
            print('SQLPERF_SUMMARY|FAIL|FAIL_RESULT_CONTRACT');return 1
        print('DGN010_COST_AGGREGATE|'+json.dumps(result.evidence['aggregate'],sort_keys=True,allow_nan=False))
    print('DGN010_COST_PROFILE|BOUNDED_ONLY|CLEANUP_'+str(result.cleanup_ok))
    print('SQLPERF_SUMMARY|'+result.outcome+'|'+result.code)
    return 1 if result.outcome=='FAIL' else 0

if __name__=='__main__':raise SystemExit(main())
