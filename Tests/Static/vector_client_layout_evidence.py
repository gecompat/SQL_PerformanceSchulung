"""Fester reiner Windows-Clientlayoutvertrag; keine Loader-/Clientaufrufe."""
from pathlib import Path
import hashlib
import json
import re

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
CONTRACT = HERE / 'Fixtures/vector_client_layout/VECTOR_CLIENT_LAYOUT.result-contract.json'
PROFILE = {'app_library': 'VectorClient/1.0.0',
 'managed_fallback': 'win',
 'packages': 27,
 'rid': 'win-x64',
 'runtime_target': '.NETCoreApp,Version=v10.0',
 'selected_assets': 28,
 'selected_runtime_targets': 5}
ORIGINS = {'Azure.Core.dll': 'packages/azure.core/1.50.0/lib/net8.0/Azure.Core.dll',
 'Azure.Identity.dll': 'packages/azure.identity/1.17.1/lib/net8.0/Azure.Identity.dll',
 'Microsoft.Bcl.AsyncInterfaces.dll': 'packages/microsoft.bcl.asyncinterfaces/8.0.0/lib/netstandard2.1/Microsoft.Bcl.AsyncInterfaces.dll',
 'Microsoft.Data.SqlClient.SNI.dll': 'packages/microsoft.data.sqlclient.sni.runtime/6.0.2/runtimes/win-x64/native/Microsoft.Data.SqlClient.SNI.dll',
 'Microsoft.Data.SqlClient.dll': 'packages/microsoft.data.sqlclient/6.1.4/runtimes/win/lib/net9.0/Microsoft.Data.SqlClient.dll',
 'Microsoft.Extensions.Caching.Abstractions.dll': 'packages/microsoft.extensions.caching.abstractions/9.0.11/lib/net9.0/Microsoft.Extensions.Caching.Abstractions.dll',
 'Microsoft.Extensions.Caching.Memory.dll': 'packages/microsoft.extensions.caching.memory/9.0.11/lib/net9.0/Microsoft.Extensions.Caching.Memory.dll',
 'Microsoft.Extensions.DependencyInjection.Abstractions.dll': 'packages/microsoft.extensions.dependencyinjection.abstractions/9.0.11/lib/net9.0/Microsoft.Extensions.DependencyInjection.Abstractions.dll',
 'Microsoft.Extensions.Logging.Abstractions.dll': 'packages/microsoft.extensions.logging.abstractions/9.0.11/lib/net9.0/Microsoft.Extensions.Logging.Abstractions.dll',
 'Microsoft.Extensions.Options.dll': 'packages/microsoft.extensions.options/9.0.11/lib/net9.0/Microsoft.Extensions.Options.dll',
 'Microsoft.Extensions.Primitives.dll': 'packages/microsoft.extensions.primitives/9.0.11/lib/net9.0/Microsoft.Extensions.Primitives.dll',
 'Microsoft.Identity.Client.Extensions.Msal.dll': 'packages/microsoft.identity.client.extensions.msal/4.78.0/lib/net8.0/Microsoft.Identity.Client.Extensions.Msal.dll',
 'Microsoft.Identity.Client.dll': 'packages/microsoft.identity.client/4.80.0/lib/net8.0/Microsoft.Identity.Client.dll',
 'Microsoft.IdentityModel.Abstractions.dll': 'packages/microsoft.identitymodel.abstractions/8.14.0/lib/net9.0/Microsoft.IdentityModel.Abstractions.dll',
 'Microsoft.IdentityModel.JsonWebTokens.dll': 'packages/microsoft.identitymodel.jsonwebtokens/7.7.1/lib/net8.0/Microsoft.IdentityModel.JsonWebTokens.dll',
 'Microsoft.IdentityModel.Logging.dll': 'packages/microsoft.identitymodel.logging/7.7.1/lib/net8.0/Microsoft.IdentityModel.Logging.dll',
 'Microsoft.IdentityModel.Protocols.OpenIdConnect.dll': 'packages/microsoft.identitymodel.protocols.openidconnect/7.7.1/lib/net8.0/Microsoft.IdentityModel.Protocols.OpenIdConnect.dll',
 'Microsoft.IdentityModel.Protocols.dll': 'packages/microsoft.identitymodel.protocols/7.7.1/lib/net8.0/Microsoft.IdentityModel.Protocols.dll',
 'Microsoft.IdentityModel.Tokens.dll': 'packages/microsoft.identitymodel.tokens/7.7.1/lib/net8.0/Microsoft.IdentityModel.Tokens.dll',
 'Microsoft.SqlServer.Server.dll': 'packages/microsoft.sqlserver.server/1.0.0/lib/netstandard2.0/Microsoft.SqlServer.Server.dll',
 'System.ClientModel.dll': 'packages/system.clientmodel/1.8.0/lib/net9.0/System.ClientModel.dll',
 'System.Configuration.ConfigurationManager.dll': 'packages/system.configuration.configurationmanager/9.0.11/lib/net9.0/System.Configuration.ConfigurationManager.dll',
 'System.Diagnostics.EventLog.Messages.dll': 'packages/system.diagnostics.eventlog/9.0.11/runtimes/win/lib/net9.0/System.Diagnostics.EventLog.Messages.dll',
 'System.Diagnostics.EventLog.dll': 'packages/system.diagnostics.eventlog/9.0.11/runtimes/win/lib/net9.0/System.Diagnostics.EventLog.dll',
 'System.IdentityModel.Tokens.Jwt.dll': 'packages/system.identitymodel.tokens.jwt/7.7.1/lib/net8.0/System.IdentityModel.Tokens.Jwt.dll',
 'System.Memory.Data.dll': 'packages/system.memory.data/8.0.1/lib/net8.0/System.Memory.Data.dll',
 'System.Security.Cryptography.Pkcs.dll': 'packages/system.security.cryptography.pkcs/9.0.11/runtimes/win/lib/net9.0/System.Security.Cryptography.Pkcs.dll',
 'System.Security.Cryptography.ProtectedData.dll': 'packages/system.security.cryptography.protecteddata/9.0.11/lib/net9.0/System.Security.Cryptography.ProtectedData.dll'}
CLAIMS = {'caller_file_metadata': 'DECLARED_NOT_INDEPENDENTLY_ATTESTED',
 'file_not_found_origin': 'UNPROVEN',
 'loader': 'NOT_ESTABLISHED',
 'runtime_qualification': 'NOT_ESTABLISHED',
 'sql': 'NOT_ESTABLISHED',
 'tds': 'NOT_ESTABLISHED',
 'tp_perf': 'NOT_ESTABLISHED',
 'typed_api': 'NOT_ESTABLISHED'}
RESOURCES = {'lib/net9.0/cs/Microsoft.Data.SqlClient.resources.dll': {'locale': 'cs'},
 'lib/net9.0/de/Microsoft.Data.SqlClient.resources.dll': {'locale': 'de'},
 'lib/net9.0/es/Microsoft.Data.SqlClient.resources.dll': {'locale': 'es'},
 'lib/net9.0/fr/Microsoft.Data.SqlClient.resources.dll': {'locale': 'fr'},
 'lib/net9.0/it/Microsoft.Data.SqlClient.resources.dll': {'locale': 'it'},
 'lib/net9.0/ja/Microsoft.Data.SqlClient.resources.dll': {'locale': 'ja'},
 'lib/net9.0/ko/Microsoft.Data.SqlClient.resources.dll': {'locale': 'ko'},
 'lib/net9.0/pl/Microsoft.Data.SqlClient.resources.dll': {'locale': 'pl'},
 'lib/net9.0/pt-BR/Microsoft.Data.SqlClient.resources.dll': {'locale': 'pt-BR'},
 'lib/net9.0/ru/Microsoft.Data.SqlClient.resources.dll': {'locale': 'ru'},
 'lib/net9.0/tr/Microsoft.Data.SqlClient.resources.dll': {'locale': 'tr'},
 'lib/net9.0/zh-Hans/Microsoft.Data.SqlClient.resources.dll': {'locale': 'zh-Hans'},
 'lib/net9.0/zh-Hant/Microsoft.Data.SqlClient.resources.dll': {'locale': 'zh-Hant'}}
EXPECTED = {'contract': 'VECTOR_CLIENT_FIXED_LAYOUT_V1', 'profile': PROFILE,
            'selected_origins': ORIGINS, 'resource_metadata': RESOURCES, 'claims': CLAIMS, 'fixture_provenance': 'PUREFIXTURE_ONLY'}
TARGET = PROFILE['runtime_target']
APP = PROFILE['app_library']
PROOF_FIELDS = set('asset_origins assets_sha256 compiler_sha256 configured_argv copied_asset_sha256 deps_sha256 dotnet_sha256 implementation_sha256 lock_sha256 origin_card_sha256 reference_sha256 response_sha256 runtimeconfig_sha256 scope_sha256 source_sha256 stage'.split())
HISTORICAL_PINS = {'deps': '6c17524f05bf45eb03dff1f438685f56c765fc1f9dc01538f0e85a9f646c166f',
 'compiler_proof': '3812b09b12f2b101f274823b67a6729ab640cc7ec8e6770f008936d339838da1',
 'app_component': '38c9e0dd693c3c1e534929ca3335e26d299802a22a92b5d05c6a7326c4fe656d'}


def fail(code): raise ValueError(code)


def exact(value, keys):
    if type(value) is not dict or set(value) != set(keys): fail('EXACT_PLAIN_SCHEMA')


def integer(value, low=0, high=300000000):
    if type(value) is not int or not low <= value <= high: fail('BOUNDED_PLAIN_INTEGER')


def sha(value):
    if type(value) is not str or re.fullmatch('[a-f0-9]{64}', value) is None: fail('FULL_SHA256')
    return value


def path(value):
    if type(value) is not str or len(value) > 220 or re.fullmatch('[A-Za-z0-9_.-]+(?:/[A-Za-z0-9_.-]+)*', value) is None or any(x in ('.','..') for x in value.split('/')):
        fail('FIXED_RELATIVE_ASCII_PATH')
    return value


def canonical(value):
    return json.dumps(value, ensure_ascii=True, allow_nan=False, sort_keys=True, separators=(',', ':'))


def unique(pairs):
    result = {}
    for key, val in pairs:
        if key in result: fail('DUPLICATE_JSON_KEY')
        result[key] = val
    return result


def plain(value, depth=0):
    if depth > 12: fail('BOUNDED_JSON_DEPTH')
    if type(value) is dict:
        if len(value)>1000 or any(type(k) is not str for k in value): fail('PLAIN_BOUNDED_KEYS')
        for v in value.values(): plain(v, depth+1)
    elif type(value) is list:
        if len(value)>1000: fail('BOUNDED_JSON_LIST')
        for v in value: plain(v, depth+1)
    elif type(value) is str:
        if len(value)>10000: fail('BOUNDED_JSON_STRING')
    elif type(value) not in (int,bool,type(None)): fail('PLAIN_JSON_SCALARS')


def load(raw, cap=100000):
    if type(raw) is not bytes or not 1 <= len(raw) <= cap: fail('BOUNDED_ORIGINAL_BYTES')
    data = json.loads(raw.decode('utf-8'), object_pairs_hook=unique,
                      parse_constant=lambda _: fail('NONFINITE_JSON'))
    plain(data)
    return data


def source_binding():
    return {p.relative_to(ROOT).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in (Path(__file__).resolve(), CONTRACT)}


def contract():
    data = load(CONTRACT.read_bytes(), 15000)
    if canonical(data) != canonical(EXPECTED): fail('FIXED_CONTRACT_DRIFT')
    return data


def select(deps):
    exact(deps, ['runtimeTarget','compilationOptions','targets','libraries'])
    exact(deps['runtimeTarget'], ['name','signature'])
    if deps['runtimeTarget'] != {'name': TARGET, 'signature': ''} or deps['compilationOptions'] != {}: fail('FIXED_RUNTIME_TARGET')
    exact(deps['targets'], [TARGET]); target = deps['targets'][TARGET]
    package_ids = {p.split('/')[1]+'/'+p.split('/')[2] for p in ORIGINS.values()}
    # Das Compilerproof benutzt kleingeschriebene NuGetordner; Deps bewahrt Paketnamen.
    if type(target) is not dict or len(target) != 28 or APP not in target or {k.lower() for k in target if k != APP} != package_ids: fail('EXACT_FIXED_PACKAGE_POPULATION')
    exact(deps['libraries'], target)
    exact(target[APP], ['dependencies','runtime'])
    if target[APP] != {'dependencies': {'Microsoft.Data.SqlClient':'6.1.4'}, 'runtime': {'VectorClient.dll': {}}}: fail('FIXED_APP_LIBRARY')
    selected = {}
    for library, item in target.items():
        if library == APP:
            if type(deps['libraries'][library]) is not dict or type(deps['libraries'][library].get('serviceable')) is not bool or deps['libraries'][library] != {'type':'project','serviceable':False,'sha512':''}: fail('FIXED_PROJECT_LIBRARY')
            continue
        path(library)
        if type(item) is not dict or set(item)-({'dependencies','runtime','runtimeTargets','resources'} if library == 'Microsoft.Data.SqlClient/6.1.4' else {'dependencies','runtime','runtimeTargets'}): fail('FIXED_PACKAGE_ASSET_SCHEMA')
        if library == 'Microsoft.Data.SqlClient/6.1.4':
            resources=item.get('resources')
            exact(resources, RESOURCES)
            for rel, meta in resources.items():
                path(rel); exact(meta, ['locale'])
                if type(meta['locale']) is not str or meta['locale'] != RESOURCES[rel]['locale']: fail('FIXED_RESOURCE_PATH_LOCALE')
        lib = deps['libraries'][library]
        exact(lib, ['type','serviceable','sha512','path','hashPath'])
        name, version = library.split('/')
        if lib['type'] != 'package' or lib['serviceable'] is not True or lib['path'] != library.lower() or lib['hashPath'] != name.lower()+'.'+version+'.nupkg.sha512' or type(lib['sha512']) is not str or not lib['sha512'].startswith('sha512-'): fail('FULL_PACKAGE_METADATA')
        dependencies=item.get('dependencies', {})
        if type(dependencies) is not dict or any(type(v) is not str for v in dependencies.values()): fail('TYPED_DEPENDENCY_GRAPH')
        for dep, version in dependencies.items():
            if dep+'/'+version not in target: fail('COMPLETE_DEPENDENCY_GRAPH')
        runtime=item.get('runtime', {}); rt=item.get('runtimeTargets', {})
        if type(runtime) is not dict or type(rt) is not dict: fail('PLAIN_RUNTIME_ASSETS')
        for rel, meta in runtime.items():
            path(rel)
            if type(meta) is not dict or set(meta)-{'assemblyVersion','fileVersion'} or any(type(v) is not str for v in meta.values()): fail('TYPED_RUNTIME_METADATA')
        for rel, meta in rt.items():
            path(rel)
            if type(meta) is not dict or not {'rid','assetType'} <= set(meta) or set(meta)-{'rid','assetType','assemblyVersion','fileVersion'} or any(type(v) is not str for v in meta.values()) or meta['assetType'] not in ('runtime','native'): fail('TYPED_RID_METADATA')
        win = {rel:meta for rel,meta in rt.items() if meta['assetType']=='runtime' and meta['rid']=='win'}
        win_leaf = {rel.rsplit('/',1)[-1].casefold() for rel in win}
        chosen = [(rel, None) for rel in runtime if rel.rsplit('/',1)[-1].casefold() not in win_leaf]
        chosen += [(rel,'win') for rel in win]
        chosen += [(rel,'win-x64') for rel,meta in rt.items() if meta['assetType']=='native' and meta['rid']=='win-x64']
        for rel,rid in chosen:
            if rel.endswith('/_._'): continue
            if not rel.endswith('.dll'): fail('FIXED_DLL_ASSETS')
            leaf = rel.rsplit('/',1)[-1]
            if leaf.casefold() in {x.casefold() for x in selected}: fail('SELECTED_BASENAME_COLLISION')
            selected[leaf] = {'origin': 'packages/'+library.lower()+'/'+rel, 'runtime_target_path': rel if rid is not None else None}
    if len(selected)!=28 or {k:v['origin'] for k,v in selected.items()} != ORIGINS or sum(v['runtime_target_path'] is not None for v in selected.values())!=5: fail('EXACT_SELECTED_WINDOWS_ASSETS')
    return selected


def report(deps_bytes, compiler_proof_bytes, files, binding):
    """Nur Source-/Metadatenkohärenz; keine Aussage über tatsächliches Hostprobing."""
    exact(binding, ['consumer_sources','artifact_sha256','provenance'])
    plain(binding); plain(files); contract()
    if binding['consumer_sources'] != source_binding(): fail('CONSUMER_EXPECTED_BINDING')
    exact(binding['artifact_sha256'], ['deps','compiler_proof','app_component'])
    for v in binding['artifact_sha256'].values(): sha(v)
    if binding['provenance'] not in ('PUREFIXTURE_ONLY','DECLARED_PRIVATE_FILE_METADATA'): fail('EXPLICIT_PROVENANCE')
    if binding['provenance']=='DECLARED_PRIVATE_FILE_METADATA' and binding['artifact_sha256'] != HISTORICAL_PINS: fail('FIXED_PR229_ARTIFACT_PINS')
    deps = load(deps_bytes); proof = load(compiler_proof_bytes)
    if hashlib.sha256(deps_bytes).hexdigest()!=binding['artifact_sha256']['deps'] or hashlib.sha256(compiler_proof_bytes).hexdigest()!=binding['artifact_sha256']['compiler_proof']: fail('ACTUAL_ORIGINAL_JSON_BYTE_PINS')
    exact(proof, PROOF_FIELDS)
    if proof['stage']!='BEFORE_COMPILER_POPEN' or proof['asset_origins']!=ORIGINS or proof['deps_sha256']!=binding['artifact_sha256']['deps']: fail('ACTUAL_COMPILER_SOURCE_GRAPH')
    for k in ('assets_sha256','compiler_sha256','dotnet_sha256','lock_sha256','origin_card_sha256','response_sha256','runtimeconfig_sha256','scope_sha256'): sha(proof[k])
    if type(proof['configured_argv']) is not list or not proof['configured_argv'] or any(type(v) is not str or not v for v in proof['configured_argv']): fail('TYPED_COMPILER_ARGUMENT_METADATA')
    for key in ('implementation_sha256','reference_sha256','source_sha256'):
        values = proof[key]
        if type(values) is not dict or not values or any(type(k) is not str or not k for k in values): fail('FULL_COMPILER_PIN_MAP')
        for value in values.values(): sha(value)
    exact(proof['copied_asset_sha256'], ORIGINS)
    for value in proof['copied_asset_sha256'].values(): sha(value)
    selected = select(deps)
    if type(files) is not list or len(files)!=31: fail('FULL_FIXED_APP_INVENTORY')
    by_path={};by_leaf={}
    allowed=set(ORIGINS)|{'VectorClient.dll','VectorClient.deps.json','VectorClient.runtimeconfig.json'}|{v['runtime_target_path'] for v in selected.values() if v['runtime_target_path'] is not None}
    for row in files:
        exact(row, ['path','bytes','sha256']); name=path(row['path']);integer(row['bytes'],1);sha(row['sha256'])
        leaf=name.rsplit('/',1)[-1].casefold()
        if name not in allowed or name in by_path or leaf in by_leaf: fail('NO_EXTRA_FILE_OR_CASE_BASENAME_ALIAS')
        by_path[name]=row;by_leaf[leaf]=row
    for name, pin in [('VectorClient.dll', binding['artifact_sha256']['app_component']),('VectorClient.deps.json',binding['artifact_sha256']['deps']),('VectorClient.runtimeconfig.json',proof['runtimeconfig_sha256'])]:
        if name not in by_path or by_path[name]['sha256']!=pin: fail('FULL_APP_BOOTSTRAP_PINS')
    if by_path['VectorClient.deps.json']['bytes']!=len(deps_bytes): fail('ORIGINAL_DEPS_LENGTH')
    present=missing=flat=0
    for leaf,item in selected.items():
        row=by_leaf.get(leaf.casefold())
        if row is None or row['sha256']!=proof['copied_asset_sha256'][leaf]: fail('COMPLETE_SELECTED_ASSET_BYTES')
        if row['path']==leaf: flat+=1
        relative=item['runtime_target_path']
        if relative is not None:
            if row['path']==relative: present+=1
            elif row['path']==leaf: missing+=1
            else: fail('EXACT_SELECTED_ASSET_LOCATION')
        elif row['path']!=leaf: fail('FIXED_GENERIC_FLAT_LOCATION')
    return {'outcome':'WARN','record_validation':'COHERENT',
        'layout':'RELATIVE_PATHS_ABSENT_FLAT_BYTES_PRESENT' if missing else 'SELECTED_RUNTIME_TARGET_PATHS_PRESENT',
        'counts':{'packages':27,'selected_assets':28,'runtime_targets':5,'app_files':31,
                  'runtime_target_paths_present':present,'runtime_target_paths_missing':missing,'flat_sha_bound_assets':flat},
        'claims':dict(CLAIMS),'fixture_provenance':binding['provenance']}
