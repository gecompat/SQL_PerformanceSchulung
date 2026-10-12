#!/usr/bin/env python3
"""Getrennte öffentliche SELECT-/DML-Lifecycles und begrenzte Setup-Recovery."""
import argparse,importlib.util,os,sys
from dataclasses import replace
from pathlib import Path
import execution_target as targets
ROOT=Path(__file__).resolve().parents[2]
spec=importlib.util.spec_from_file_location('dgn010_ci_consumer',ROOT/'Demos/09_AI_SQL_Server_2025/DGN-010_Index_Advice/run_profile.py')
profile=importlib.util.module_from_spec(spec);sys.modules[spec.name]=profile;spec.loader.exec_module(profile)

def validate(result,major,scope):
    if not result.cleanup_ok or result.client_end_unknown:raise ValueError('Öffentlicher Cleanup unbestätigt')
    if major in (15,16):
        if (result.outcome,result.code)!=('SKIP','SKIP_VERSION') or any(p[0]=='10_Setup.sql' for p in result.phases):raise ValueError('Versions-SKIP vor Setup fehlt')
        return False
    if (result.outcome,result.code)==('SKIP','SKIP_CONFIGURATION'):
        if any(p[0]=='10_Setup.sql' for p in result.phases):raise ValueError('Konfigurations-SKIP erreichte Setup')
        return False
    if (result.outcome,result.code)!=('WARN','WARN_OPTIONAL_EVIDENCE_SKIPPED') or result.evidence.get('scope')!=scope:
        raise ValueError('Begrenzter öffentlicher Scope fehlt')
    data=result.evidence
    if data['aggregate']['counts']!=profile.benchmark.INVARIANTS or data['aggregate']['runtime_qualification']!='NOT_ESTABLISHED' or data['fwk011']['result']['outcome']!='PASS' or len(data['fwk011']['assertions'])!=12:
        raise ValueError('Vollständige bounded Auswertung/FWK-011 fehlt')
    return True

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--container',required=True);parser.add_argument('--expected-major',type=int,choices=(15,16,17),required=True)
    args=parser.parse_args()
    try:
        target=targets.docker_target(container=args.container)
        targets.require_disposable_instance(target,False);major=targets.verify_engine(target,expected_major=args.expected_major)
        target=replace(target,shim=ROOT/'Tests/Runtime/dgn010_docker_sqlcmd_proxy.py')
        os.environ[targets.CONTAINER_VARIABLE]=target.container
        outcome=None
        for scope in ('SELECT','DML'):
            qualified=[]
            for repetition in (1,2):
                result=profile.run_profile(executable=str(target.shim),server=target.server,auth=target.auth,username=target.username,scope=scope,confirmed=True,high_impact=True)
                accepted=validate(result,major,scope);qualified.append(accepted);outcome=(result.outcome,result.code)
                if accepted:print(f'DGN010_AGGREGATE|{scope}|RUN_{repetition}|FWK011_12_PASS|OVERALL_WARN')
                print(f'DGN010_CONSUMER|{scope}|RUN_{repetition}|{result.outcome}|{result.code}|CLEANUP_CONFIRMED')
            if all(qualified):
                fault=profile.run_profile(executable=str(target.shim),server=target.server,auth=target.auth,username=target.username,scope=scope,confirmed=True,high_impact=True,fault='after_setup')
                if not profile.setup_fault_completed(fault):raise ValueError('Tatsächlicher Setupfault fehlt')
                print(f'DGN010_CONSUMER|{scope}|EXPECTED_FAIL_AFTER_SETUP|RECOVERY_CONFIRMED')
        print('SQLPERF_SUMMARY|'+'|'.join(outcome));return 0
    except (targets.ExecutionTargetError,ValueError,OSError,RuntimeError,KeyError,TypeError):
        print('SQLPERF_SUMMARY|FAIL|FAIL_RESULT_CONTRACT');return 1
if __name__=='__main__':raise SystemExit(main())
