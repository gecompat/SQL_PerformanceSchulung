#!/usr/bin/env python3
"""DGN-010-Adapter mit tatsächlichem Remote-Waitframe; gemeinsame API unverändert."""
import os,subprocess,sys
import docker_sqlcmd_proxy as proxy
proxy.BOOLEAN_FLAGS=proxy.BOOLEAN_FLAGS|{'-C'}
proxy.VALUE_FLAGS=proxy.VALUE_FLAGS|{'-l','-y'}

# Fester Code, argv über "$@"; kein dynamisches Shellquoting und kein Passwortargument.
# Der Frame entsteht erst nach dem tatsächlichen Ende des nativen sqlcmd im Container.
REMOTE_WAIT='"$@"; result=$?; printf "\\nDGN010_REMOTE_END|%s\\n" "$result" >&2; exit "$result"'

def main():
    try:
        database,script,username,variables,passthrough=proxy._parse_args(sys.argv[1:])
        widths=[passthrough[index+1] for index,value in enumerate(passthrough) if value == '-y']
        if widths and widths != ['0']:
            raise ValueError('DGN-010-Vollframes benoetigen -y 0')
        container=os.environ.get('SQLPERF_SQL_CONTAINER')
        if not container or not os.environ.get('SQLCMDPASSWORD'):raise ValueError('Eigener Container und SQLCMDPASSWORD erforderlich')
        command=['docker','exec','-i','-e','SQLCMDPASSWORD',container,'sh','-c',REMOTE_WAIT,
                 'dgn010-remote-wait',proxy._sqlcmd_path(container),'-S','localhost','-d',database,'-U',username,'-C',*passthrough]
        if variables:command.extend(['-v',*variables])
        result=subprocess.run(command,input=script.read_text(encoding='utf-8'),check=False,capture_output=True,text=True,encoding='utf-8',errors='replace',env=os.environ.copy())
        sys.stdout.write(result.stdout);sys.stderr.write(result.stderr);return result.returncode
    except (FileNotFoundError,OSError,ValueError):
        print('dgn010-docker-proxy: Clientstart oder Transport fehlgeschlagen',file=sys.stderr);return 1

if __name__=='__main__':raise SystemExit(main())
