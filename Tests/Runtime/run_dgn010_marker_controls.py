#!/usr/bin/env python3
"""Feste DGN-010-Markerabnahme auf der bestehenden eigenen CI-Instanz."""
import argparse,os
from dataclasses import replace
import execution_target as targets
import run_dgn010_profile as producer
import dgn010_marker_controls as markers
profile=producer.profile

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--container',required=True);parser.add_argument('--expected-major',type=int,choices=(15,16,17),required=True)
    args=parser.parse_args()
    try:
        target=targets.docker_target(container=args.container);targets.require_disposable_instance(target,False)
        major=targets.verify_engine(target,expected_major=args.expected_major)
        target=replace(target,shim=profile.ROOT/'Tests/Runtime/dgn010_docker_sqlcmd_proxy.py');os.environ[targets.CONTAINER_VARIABLE]=target.container
        result=markers.run(profile,executable=str(target.shim),server=target.server,confirmed=True,high_impact=True)
        if not result.cleanup_ok or result.client_end_unknown:raise ValueError('Markercleanup unbestaetigt')
        if major in (15,16):
            if (result.outcome,result.code)!=('SKIP','SKIP_VERSION') or any(p[0]=='10_Setup.sql' for p in result.phases):raise ValueError('Versions-SKIP erreichte Setup')
            print('DGN010_MARKERS|SKIP_VERSION|BEFORE_SETUP|CLEANUP_CONFIRMED')
        else:
            if (result.outcome,result.code)!=('PASS','OK') or result.evidence.get('negative_count')!=192 or result.evidence.get('restored_cases')!=24 or len(result.evidence.get('controls',[]))!=192:raise ValueError('Vollstaendige feste Markerqualifikation fehlt')
            if any(c['before']!=c['after'] for c in result.evidence['controls']):raise ValueError('Tatsaechlicher vollständiger Statevergleich fehlt')
            print('DGN010_MARKERS|NEGATIVE_192|RESTORED_24|FULL_STATE_UNCHANGED|PASS|CLEANUP_CONFIRMED')
        print('SQLPERF_SUMMARY|'+'|'.join((result.outcome,result.code)));return 0
    except (Exception,KeyboardInterrupt):print('SQLPERF_SUMMARY|FAIL|FAIL_RESULT_CONTRACT');return 1
if __name__=='__main__':raise SystemExit(main())
