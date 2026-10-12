#!/usr/bin/env python3
"""Getrennte CI-Abnahme des begrenzten Kostenprofils, ohne allgemeinen Performanceclaim."""
import argparse
import importlib.util
import json
import os
import sys
from dataclasses import replace
from pathlib import Path

import execution_target as targets

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location(
    'dgn010_ci_cost', ROOT/'Demos/09_AI_SQL_Server_2025/DGN-010_Index_Advice/run_cost_profile.py')
cost = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cost)

VERSION_PHASES = (('91_Absence.sql', 'PASS', 'OK'),
                  ('00_Preflight.sql', 'SKIP', 'SKIP_VERSION'),
                  ('91_Absence.sql', 'PASS', 'OK'))
POSITIVE_PHASES = tuple((label, 'PASS', 'OK') if label not in ('SOURCE_NEGATIVE', 'DROP_ABSENT')
                        else ('20_Probe.sql' if label == 'SOURCE_NEGATIVE' else label,
                              'EXPECTED_REJECTION', '51003') for label in (
    '91_Absence.sql', '00_Preflight.sql', '10_Setup.sql', '20_Probe.sql',
    '10_Setup.sql', '20_Probe.sql', '21_DeleteOwnRow.sql', 'SOURCE_NEGATIVE',
    '10_Setup.sql', '20_Probe.sql', '22_Database.sql', 'INITIAL_STATE',
    'DROP_ABSENT', 'FULL_STATE', '20_Probe.sql',
    'FULL_STATE', 'CREATE_1', 'FULL_STATE', '20_Probe.sql',
    'FULL_STATE', 'DROP_1', 'FULL_STATE', '20_Probe.sql',
    'FULL_STATE', 'CREATE_2', 'FULL_STATE', '20_Probe.sql',
    'FULL_STATE', 'DROP_2', 'FULL_STATE', '20_Probe.sql',
    '90_Cleanup.sql', '91_Absence.sql'))


def validate(result, major):
    if result.cleanup_ok is not True or result.client_end_unknown is not False:
        raise ValueError('Kostenprofil-Cleanup oder Clientende unbestaetigt')
    if type(result.evidence.get('own_input_files_preserved')) is not int or result.evidence['own_input_files_preserved'] != 0:
        raise ValueError('Eigene SQLinputs nicht vollstaendig abgebaut')
    if major in (15, 16):
        if (result.outcome, result.code) != ('SKIP', 'SKIP_VERSION') or result.phases != VERSION_PHASES:
            raise ValueError('Kosten-Versionsgrenze vor Setup fehlt')
        return False
    if major != 17:
        raise ValueError('Kostenprofilversion nicht gebunden')
    if (result.outcome, result.code) != ('WARN', 'WARN_OPTIONAL_EVIDENCE_SKIPPED'):
        raise ValueError('SQL2025-Kostenqualifikation fehlt')
    record = result.evidence['record']
    actual = cost.costs.report(record, expected_database_id=record['database_id'])
    if json.dumps(actual, sort_keys=True, allow_nan=False) != json.dumps(
            result.evidence['aggregate'], sort_keys=True, allow_nan=False):
        raise ValueError('Vollstaendiger Kostenrecord und Aggregate weichen ab')
    if result.evidence.get('scope') != 'TWO_OWN_CREATE_DROP_CYCLES_ONLY':
        raise ValueError('Begrenzter Scope fehlt')
    if result.phases != POSITIVE_PHASES:
        raise ValueError('Vollstaendige positive/native Negativ-/Cleanuphasefolge fehlt')
    return True


def validate_fault(result):
    if (not cost.profile.setup_fault_completed(result)
            or type(result.evidence.get('own_input_files_preserved')) is not int
            or result.evidence['own_input_files_preserved'] != 0):
        raise ValueError('Kosten-Setupfault oder vollstaendige Recovery fehlt')


def qualify(target, major, runner=cost.run_cost_profile):
    accepted = []
    for repetition in (1, 2):
        result = runner(executable=str(target.shim), server=target.server, auth=target.auth,
                        username=target.username, confirmed=True, high_impact=True)
        accepted.append(validate(result, major))
        print(f'DGN010_COST_CONSUMER|RUN_{repetition}|{result.outcome}|{result.code}|CLEANUP_CONFIRMED')
        if accepted[-1]:
            print(f'DGN010_COST_CONSUMER|RUN_{repetition}|DDL_4|SOURCE_8000|STATE_10000|NEGATIVE_2|BOUNDED_ONLY')
    if all(accepted):
        fault = runner(executable=str(target.shim), server=target.server, auth=target.auth,
                       username=target.username, confirmed=True, high_impact=True, fault='after_setup')
        validate_fault(fault)
        print('DGN010_COST_CONSUMER|EXPECTED_FAIL_AFTER_SETUP|RECOVERY_CONFIRMED')
    print('SQLPERF_SUMMARY|' + result.outcome + '|' + result.code)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--container', required=True)
    parser.add_argument('--expected-major', type=int, choices=(15, 16, 17), required=True)
    args = parser.parse_args()
    try:
        target = targets.docker_target(container=args.container)
        targets.require_disposable_instance(target, False)
        major = targets.verify_engine(target, expected_major=args.expected_major)
        target = replace(target, shim=ROOT/'Tests/Runtime/dgn010_docker_sqlcmd_proxy.py')
        os.environ[targets.CONTAINER_VARIABLE] = target.container
        qualify(target, major)
        return 0
    except (Exception, KeyboardInterrupt):
        print('SQLPERF_SUMMARY|FAIL|FAIL_RESULT_CONTRACT')
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
