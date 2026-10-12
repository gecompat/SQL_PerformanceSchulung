"""Vollständiger nativer Source-/Index-/Readerframe; keine SQLausführung beim Import."""
import re
import dgn010_benchmark_evidence as benchmark

def evidence(output,path):
    if type(output) is not str or len(output.encode('utf-8'))>1000000 or type(path) is not int or path not in (0,1):
        raise ValueError('Begrenzter tatsächlicher Quellenframe erforderlich')
    rows=[];indexes={};reader=0;summary=0
    for line in output.splitlines():
        if not line.strip():continue
        fields=line.split('|')
        if fields==['SQLPERF_SUMMARY','PASS','OK']:summary+=1;continue
        if fields==['DGN010_READER','ROWS_10','FIXED_RIGHTS_2','NO_MODEL_CALL']:reader+=1;continue
        if len(fields)==5 and fields[0]=='DGN010_SOURCE' and all(re.fullmatch('[0-9]+',v) for v in fields[1:4]):
            rows.append([*map(int,fields[1:4]),fields[4]]);continue
        if len(fields)==5 and fields[0]=='DGN010_INDEX' and fields[1] not in indexes and all(re.fullmatch('[0-9]+',v) for v in fields[2:]):
            indexes[fields[1]]=list(map(int,fields[2:]));continue
        raise ValueError('Unbekannter oder doppelter Quellenframe')
    if reader!=1 or summary!=1:raise ValueError('Vollständiger nativer Reader-/Phasenstatus erforderlich')
    actual=[rows,indexes];benchmark.validate_source(actual,path);return actual
