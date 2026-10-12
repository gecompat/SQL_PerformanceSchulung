#!/usr/bin/env python3
"""Zwei öffentliche begrenzte Lifecycles; Versions-SKIP und Setupfault getrennt."""
import argparse,importlib.util,os,sys
from dataclasses import replace
from pathlib import Path
import execution_target as targets
ROOT=Path(__file__).resolve().parents[2]
spec=importlib.util.spec_from_file_location('res008_ci_consumer',ROOT/'Demos/09_AI_SQL_Server_2025/RES-008_Vector_Dimensions/run_profile.py')
profile=importlib.util.module_from_spec(spec);sys.modules[spec.name]=profile;spec.loader.exec_module(profile)

def validate(result,major):
    if not result.cleanup_ok or result.client_end_unknown:raise ValueError('Unbestaetigter oeffentlicher Cleanup')
    if major in (15,16):
        if (result.outcome,result.code)!=('SKIP','SKIP_VERSION') or any(p[0]=='10_Setup.sql' for p in result.phases):raise ValueError('SKIP vor Setup fehlt')
        return False
    if (result.outcome,result.code)==('SKIP','SKIP_CONFIGURATION'):
        if any(p[0]=='10_Setup.sql' for p in result.phases):raise ValueError('Build-SKIP hat Setup erreicht')
        return False
    data=result.evidence
    if (result.outcome,result.code)!=('WARN','WARN_OPTIONAL_EVIDENCE_SKIPPED') or len(data.get('windows',()))!=74 or len(data.get('plans',()))!=4 or not all(data.get(k) is True for k in ('source_config_equal','negative_source_actual','negative_query_actual')):raise ValueError('Vollstaendiger begrenzter Consumer fehlt')
    return True

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--container',required=True);parser.add_argument('--expected-major',type=int,choices=(15,16,17),required=True)
    args=parser.parse_args()
    try:
        target=targets.docker_target(container=args.container)
        targets.require_disposable_instance(target,False);major=targets.verify_engine(target,expected_major=args.expected_major)
        target=replace(target,shim=ROOT/'Tests/Runtime/res008_docker_sqlcmd_proxy.py')
        os.environ[targets.CONTAINER_VARIABLE]=target.container
        outcomes=[];qualified=[]
        for repetition in (1,2):
            result=profile.run_profile(executable=str(target.shim),server=target.server,auth=target.auth,username=target.username,confirmed=True,high_impact=True)
            qualified.append(validate(result,major));outcomes.append((result.outcome,result.code))
            print(f'RES008_CONSUMER|RUN_{repetition}|{result.outcome}|{result.code}|CLEANUP_CONFIRMED')
        if all(qualified):
            fault=profile.run_profile(executable=str(target.shim),server=target.server,auth=target.auth,username=target.username,confirmed=True,high_impact=True,fault='after_setup')
            if not profile.setup_fault_completed(fault):raise ValueError('Begrenzter tatsächlicher Setupfault fehlt')
            print('RES008_CONSUMER|EXPECTED_FAIL_AFTER_SETUP|RECOVERY_CONFIRMED')
        print('SQLPERF_SUMMARY|'+'|'.join(outcomes[-1]));return 0
    except (targets.ExecutionTargetError,ValueError,OSError,RuntimeError):
        print('SQLPERF_SUMMARY|FAIL|FAIL_RESULT_CONTRACT');return 1

if __name__=='__main__':raise SystemExit(main())
