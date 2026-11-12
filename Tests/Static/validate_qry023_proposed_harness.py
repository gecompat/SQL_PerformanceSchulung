#!/usr/bin/env python3
"""Check the offline QRY-023 draft without invoking SQL Server or its harness."""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DEMO = ROOT / "Demos/05_Query_Patterns/QRY-023_Graph_Tables"
EXPECTED_PHASES = [
    ("PREFLIGHT", "00_Preflight.sql", "master", None, "ADMIN"),
    ("SETUP", "10_Setup.sql", "master", 240, "ADMIN"),
    ("FRAMEWORK", "15_Framework.sql", "target", 180, "ADMIN"),
    ("WORKLOAD", "20_Workload.sql", "target", 300, "ADMIN"),
    ("QUALIFICATION_PREFLIGHT", "25_Qualification_Preflight.sql", "target", None, "READER"),
    ("CORRECTNESS", "30_Correctness.sql", "target", 180, "READER"),
    ("MEASUREMENT", "40_Measurement.sql", "target", 300, "READER"),
    ("PLAN_EVIDENCE", "50_Plan_Evidence.sql", "target", 120, "READER"),
]
EXPECTED_SQLCMD_INPUT_VALIDATION = {
    "must_validate_before": "SQLCMD_EXPANSION",
    "reject_invalid": True,
    "demo_id": {"mode": "EXACT", "value": "QRY-023"},
    "run_token": {
        "encoding": "ASCII",
        "allowed_characters": "A-Z0-9_",
        "first_character": "A-Z0-9",
        "min_bytes": 1,
        "max_bytes": 20,
    },
    "target_database": {
        "template": "SQLPERF_LAB_{DEMO_ID_WITHOUT_HYPHEN}_{RUN_TOKEN}"
    },
}
EXPECTED_EXECUTION_SAFETY_CONTRACT = {
    "expected_target_database_size_mib": 1024,
    "expected_tempdb_growth_mib": 1024,
    "maximum_concurrent_sql_sessions": 1,
    "abort_signals": ["CTRL_C", "PHASE_TIMEOUT", "GLOBAL_TIMEOUT"],
    "abort_action": "TERMINATE_SQLCMD_PROCESS_TREE",
    "cleanup_after_setup_started": "ONLY_AFTER_PROCESS_EXIT_CONFIRMED",
    "early_stop_triggers": [
        "RESOURCE_PROFILE_MISMATCH_BEFORE_SETUP",
        "TARGET_DATABASE_SIZE_LIMIT",
        "TEMPDB_GROWTH_LIMIT",
        "PHASE_OR_GLOBAL_TIMEOUT",
        "CTRL_C",
    ],
    "enforcement_status": "PROPOSED_RUNTIME_CALLER_REQUIRED",
    "forced_abort_residual_state": (
        "The marked target database may contain partial synthetic objects; connection-cancel completion "
        "and TempDB release are not established. Preserve the target if exact ownership checks or cleanup fail."
    ),
}
EXPECTED_AUTHORIZATION_CONTRACT = {
    "phase_privileges": {
        "SETUP": ["CREATE DATABASE", "CREATE SCHEMA/TABLE/INDEX", "INSERT SYNTHETIC DATA"],
        "READ_AND_MEASURE": ["SELECT ON FOUR QUERY AND FOUR ORACLE TABLES", "SELECT ON lab.MeasurementRun", "EXECUTE ON lab.USP_Qry023MeasureVariant", "SHOWPLAN ON TARGET DATABASE"],
        "CLEANUP": ["DROP ONLY AFTER EXACT OWNERSHIP MARKERS"],
    },
    "current_fwk010_mode": "PHASE_SPECIFIC_SQL_AUTH_PROFILE",
    "phase_identity_enforced": True,
    "gate_status": "OPEN_UNTIL_SQL_SERVER_PRINCIPAL_AND_PRIVILEGE_QUALIFICATION",
}
RUN_TOKEN_PATTERN = re.compile(r"[A-Z0-9][A-Z0-9_]{0,19}")
COUNT_BIG_QUERY_PATTERN = re.compile(
    r"\bselect\s+@?pathcount\s*=\s*count_big\s*\(\s*\*\s*\).*?;",
    re.IGNORECASE | re.DOTALL,
)


def profile_counts(path_count: int) -> tuple[int, int, int]:
    """Return (nodes, directed edges, two-hop paths) for the disjoint profile."""
    return path_count * 3, path_count * 2, path_count


def paired_order(pair_number: int) -> tuple[str, str]:
    """Return the two variants in alternating AB/BA order, starting with AB."""
    if pair_number < 1:
        raise ValueError("pair_number must be positive")
    return ("GRAPH", "RELATIONAL") if pair_number % 2 else ("RELATIONAL", "GRAPH")


def require(condition: bool, message: str, errors: list[str]) -> None:
    if not condition:
        errors.append(message)


def count_big_queries(sql: str) -> list[str]:
    """Return normalized PathCount COUNT_BIG statements for query-shape comparison."""
    queries = []
    for match in COUNT_BIG_QUERY_PATTERN.finditer(sql):
        normalized = re.sub(r"\s+", "", match.group(0)).casefold()
        normalized = re.sub(
            r"^select@?pathcount=count_big\(\*\)",
            "selectresult=count_big(*)",
            normalized,
            count=1,
        )
        queries.append(normalized)
    return queries


def plan_queries_inside_statistics_window(plan: str) -> bool:
    """Require both diagnostic queries between the successful XML ON/OFF statements."""
    xml_on = plan.find("set statistics xml on")
    xml_off = plan.find("set statistics xml off", xml_on + 1)
    queries = list(COUNT_BIG_QUERY_PATTERN.finditer(plan))
    return (
        xml_on >= 0
        and xml_off > xml_on
        and len(queries) == 2
        and all(xml_on < query.start() < query.end() < xml_off for query in queries)
    )


def plan_xml_output_is_untruncated(plan: str) -> bool:
    """Require the effective sqlcmd XML-width value before XML output to be unlimited."""
    directives = list(re.finditer(
        r"^\s*:setvar\s+SQLCMDMAXVARTYPEWIDTH\s+(\S+)\s*$",
        plan,
        re.IGNORECASE | re.MULTILINE,
    ))
    xml_on = plan.lower().find("set statistics xml on")
    prior_values = [match.group(1) for match in directives if match.start() < xml_on]
    return xml_on >= 0 and bool(prior_values) and prior_values[-1] == "0"


def plan_summary_follows_cleanup(plan: str) -> bool:
    """Require success output after both option resets and the rethrowing CATCH."""
    markers = {
        "try": plan.find("begin try"),
        "xml_on": plan.find("set statistics xml on"),
        "success_off": plan.find("set statistics xml off", plan.find("set statistics xml on") + 1),
    }
    markers["end_try"] = plan.find("end try", markers["success_off"] + 1)
    markers["catch"] = plan.find("begin catch", markers["end_try"] + 1)
    markers["catch_off"] = plan.find("set statistics xml off", markers["catch"] + 1)
    markers["throw"] = plan.find("throw;", markers["catch_off"] + 1)
    markers["end_catch"] = plan.find("end catch", markers["throw"] + 1)
    summary_selects = list(re.finditer(
        r"\bselect\s+1\s+as\s+sequence\s*,\s*'plan_evidence'\s+as\s+phase\s*,"
        r"\s*'summary'\s+as\s+checkid\s*,\s*'pass'\s+as\s+outcome\s*,"
        r"\s*'ok'\s+as\s+code\b", plan
    ))
    summary_prints = list(re.finditer(r"\bprint\s+'sqlperf_summary\|pass\|ok'", plan))
    return (
        all(position >= 0 for position in markers.values())
        and markers["try"] < markers["xml_on"] < markers["success_off"] < markers["end_try"]
        < markers["catch"] < markers["catch_off"] < markers["throw"] < markers["end_catch"]
        and len(summary_selects) == 1
        and summary_selects[0].start() > markers["end_catch"]
        and len(summary_prints) == 1
        and summary_prints[0].start() > markers["end_catch"]
    )


def qualification_permission_gate_valid(qualification: str) -> bool:
    """Bind target SHOWPLAN, query reads, and measurement permissions to early skip."""
    compact = re.sub(r"\s+", "", qualification).casefold()
    showplan_check = (
        "declare@hasshowplanbit=casewhenhas_perms_by_name(db_name(),'database','showplan')=1then1else0end;"
    )
    select_match = re.search(r"declare@hasselectbit=casewhen(.*?)then1else0end;", compact)
    expected_selects = (
        "has_perms_by_name(n'dbo.person','object','select')=1and"
        "has_perms_by_name(n'dbo.friendof','object','select')=1and"
        "has_perms_by_name(n'dbo.relperson','object','select')=1and"
        "has_perms_by_name(n'dbo.relfriend','object','select')=1and"
        "has_perms_by_name(n'dbo.oracleperson','object','select')=1and"
        "has_perms_by_name(n'dbo.oraclefriendof','object','select')=1and"
        "has_perms_by_name(n'dbo.oraclerelperson','object','select')=1and"
        "has_perms_by_name(n'dbo.oraclerelfriend','object','select')=1"
    )
    measurement_check = (
        "declare@hasmeasurementbit=casewhenhas_perms_by_name(n'lab.measurementrun','object','select')=1"
        "andhas_perms_by_name(n'lab.usp_qry023measurevariant','object','execute')=1then1else0end;"
    )
    guard = compact.find("if@hasshowplan=0or@hasselect=0or@hasmeasurement=0begin")
    if guard < 0:
        return False
    skip_outcome = compact.find("'skip'asoutcome", guard)
    skip_code = compact.find("'skip_permission'ascode", guard)
    skip_print = compact.find("print'sqlperf_summary|skip|skip_permission'", guard)
    skip_return = compact.find("return;", guard)
    guard_end = compact.find("end;", skip_return)
    pass_output = compact.find("'pass'asoutcome", guard_end)
    return (
        compact.count(showplan_check) == 1
        and select_match is not None
        and select_match.group(1) == expected_selects
        and compact.count(measurement_check) == 1
        and 0 <= skip_outcome < skip_code < skip_print < skip_return < guard_end
        and pass_output > guard_end
    )


def reader_object_dependencies_covered(
    manifest: dict[str, object], reader_scripts: dict[str, str], qualification: str
) -> bool:
    """Require every direct user-object read/call in READER phases to be preflighted."""
    phases = manifest.get("phases")
    if not isinstance(phases, list):
        return False
    reader_names = {
        phase.get("script")
        for phase in phases
        if isinstance(phase, dict) and phase.get("credential_profile") == "READER"
    }
    if not reader_names or not reader_names.issubset(reader_scripts):
        return False

    referenced: set[tuple[str, str, str]] = set()
    object_pattern = re.compile(
        r"(?:\bfrom\b|\bjoin\b)\s*(?P<schema>\[?(?:dbo|lab)\]?)\s*\.\s*"
        r"(?P<object>\[?[a-z_][a-z0-9_$#@]*\]?)",
        re.IGNORECASE,
    )
    from_list_pattern = re.compile(
        r"\bfrom\b(?P<body>.*?)(?=\bjoin\b|\bwhere\b|\bgroup\b|\border\b|\bhaving\b|;|$)",
        re.IGNORECASE | re.DOTALL,
    )
    comma_object_pattern = re.compile(
        r",\s*(?P<schema>\[?(?:dbo|lab)\]?)\s*\.\s*"
        r"(?P<object>\[?[a-z_][a-z0-9_$#@]*\]?)",
        re.IGNORECASE,
    )
    execute_pattern = re.compile(
        r"\bexec(?:ute)?\s+(?P<schema>\[?(?:dbo|lab)\]?)\s*\.\s*"
        r"(?P<object>\[?[a-z_][a-z0-9_$#@]*\]?)",
        re.IGNORECASE,
    )
    three_part_reference_pattern = re.compile(
        r"\b(?:from|join|exec(?:ute)?)\s+(?:(?:\[[^]]+\]|[a-z_][a-z0-9_$#@]*)\s*\.\s*){1,2}"
        r"\[?(?:dbo|lab)\]?\s*\.\s*\[?[a-z_][a-z0-9_$#@]*\]?",
        re.IGNORECASE,
    )
    qualified_pattern = re.compile(
        r"(?P<schema>\[?(?:dbo|lab)\]?)\s*\.\s*(?P<object>\[?[a-z_][a-z0-9_$#@]*\]?)",
        re.IGNORECASE,
    )
    block_comment = re.compile(r"/\*.*?\*/", re.DOTALL)
    line_comment = re.compile(r"--[^\r\n]*")
    for script_name in reader_names:
        source = reader_scripts[script_name]
        source = block_comment.sub(" ", source)
        source = line_comment.sub(" ", source)
        source = re.sub(r"n?'(?:''|[^'])*'", "''", source, flags=re.IGNORECASE)
        if three_part_reference_pattern.search(source):
            return False
        object_matches = list(object_pattern.finditer(source))
        from_list_matches = []
        for from_match in from_list_pattern.finditer(source):
            body_start = from_match.start("body")
            for match in comma_object_pattern.finditer(from_match.group("body")):
                from_list_matches.append((match, body_start))
        execute_matches = list(execute_pattern.finditer(source))
        def add_select_reference(match: re.Match[str]) -> None:
            schema = match.group("schema").strip("[]").casefold()
            name = match.group("object").strip("[]").casefold()
            referenced.add((schema, name, "SELECT"))

        for match in object_matches:
            add_select_reference(match)
        for match, _ in from_list_matches:
            add_select_reference(match)
        for match in execute_matches:
            schema = match.group("schema").strip("[]").casefold()
            name = match.group("object").strip("[]").casefold()
            referenced.add((schema, name, "EXECUTE"))
        recognized_spans = [
            (match.start(), match.end())
            for match in (*object_matches, *execute_matches)
        ]
        recognized_spans.extend(
            (offset + match.start(), offset + match.end())
            for match, offset in from_list_matches
        )
        for match in qualified_pattern.finditer(source):
            if not any(start <= match.start() and match.end() <= end
                       for start, end in recognized_spans):
                return False

    checked = {
        (match.group("schema").strip("[]").casefold(),
         match.group("object").strip("[]").casefold(),
         match.group("permission").upper())
        for match in re.finditer(
            r"has_perms_by_name\s*\(\s*n?'(?P<schema>\[?(?:dbo|lab)\]?)\s*\.\s*"
            r"(?P<object>\[?[a-z_][a-z0-9_$#@]*\]?)'\s*,\s*'object'\s*,\s*"
            r"'(?P<permission>select|execute)'\s*\)",
            qualification,
            re.IGNORECASE,
        )
    }
    return referenced.issubset(checked)


def reader_phase_scripts_are_read_only(
    manifest: dict[str, object], reader_scripts: dict[str, str]
) -> bool:
    """Allow local table-variable writes, but reject persistent DML/DDL in READER phases."""
    phases = manifest.get("phases")
    if not isinstance(phases, list):
        return False
    reader_names = {
        phase.get("script")
        for phase in phases
        if isinstance(phase, dict) and phase.get("credential_profile") == "READER"
    }
    if not reader_names or not reader_names.issubset(reader_scripts):
        return False
    block_comment = re.compile(r"/\*.*?\*/", re.DOTALL)
    line_comment = re.compile(r"--[^\r\n]*")
    dml_target = re.compile(
        r"\b(?:insert(?:\s+into)?|update|delete(?:\s+top\s*\([^)]*\))?(?:\s+from)?|"
        r"merge\s+into|truncate\s+table|set\s+identity_insert|(?:write|updatetext))\s+"
        r"(?P<target>@?[a-z_][a-z0-9_$#@]*|\[[^]]+\])",
        re.IGNORECASE,
    )
    select_into_target = re.compile(
        r"\bselect\b(?:(?!;).)*?\binto\s+(?P<target>@?[a-z_][a-z0-9_$#@]*|\[[^]]+\])",
        re.IGNORECASE | re.DOTALL,
    )
    bulk_insert_target = re.compile(
        r"\bbulk\s+insert\s+(?P<target>@?[a-z_][a-z0-9_$#@]*|\[[^]]+\])",
        re.IGNORECASE,
    )
    ddl_or_security = re.compile(r"\b(?:create|alter|drop|grant|deny|revoke|dbcc)\b", re.IGNORECASE)
    context_switch = re.compile(r"\b(?:use|setuser|revert)\b", re.IGNORECASE)
    direct_execute = re.compile(
        r"\bexec(?:ute)?\s+(?P<schema>\[?(?:dbo|lab)\]?)\s*\.\s*"
        r"(?P<object>\[?[a-z_][a-z0-9_$#@]*\]?)",
        re.IGNORECASE,
    )
    allowed_execute = {("lab", "usp_qry023measurevariant")}
    for script_name in reader_names:
        source = block_comment.sub(" ", reader_scripts[script_name])
        source = line_comment.sub(" ", source)
        executable_source = re.sub(r"n?'(?:''|[^'])*'", "''", source, flags=re.IGNORECASE)
        if ddl_or_security.search(executable_source) or context_switch.search(executable_source):
            return False
        for match in re.finditer(r"\bexec(?:ute)?\b", executable_source, re.IGNORECASE):
            call = direct_execute.match(executable_source, match.start())
            if call is None:
                return False
            target = (call.group("schema").strip("[]").casefold(),
                      call.group("object").strip("[]").casefold())
            if target not in allowed_execute:
                return False
        for match in (*dml_target.finditer(executable_source),
                      *select_into_target.finditer(executable_source),
                      *bulk_insert_target.finditer(executable_source)):
            if not match.group("target").startswith("@"):
                return False
    return True


def qualification_summaries_valid(qualification: str) -> bool:
    """Require the permission skip and success rows to match their PRINT markers."""
    skip_row_pattern = (
        r"\bselect\s+1\s+as\s+sequence\s*,\s*'qualification_preflight'\s+as\s+phase\s*,"
        r"\s*'permissions'\s+as\s+checkid\s*,\s*'skip'\s+as\s+outcome\s*,"
        r"\s*'skip_permission'\s+as\s+code\b"
    )
    pass_row_pattern = (
        r"\bselect\s+1\s+as\s+sequence\s*,\s*'qualification_preflight'\s+as\s+phase\s*,"
        r"\s*'summary'\s+as\s+checkid\s*,\s*'pass'\s+as\s+outcome\s*,\s*'ok'\s+as\s+code\b"
    )
    skip_rows = list(re.finditer(skip_row_pattern, qualification))
    pass_rows = list(re.finditer(pass_row_pattern, qualification))
    skip_prints = list(re.finditer(r"\bprint\s+'sqlperf_summary\|skip\|skip_permission'", qualification))
    pass_prints = list(re.finditer(r"\bprint\s+'sqlperf_summary\|pass\|ok'", qualification))
    skip_return = qualification.find("return;", skip_prints[0].end()) if skip_prints else -1
    return (
        len(skip_rows) == len(pass_rows) == len(skip_prints) == len(pass_prints) == 1
        and skip_rows[0].start() < skip_prints[0].start() < skip_return
        < pass_rows[0].start() < pass_prints[0].start()
    )


def qualification_target_context_valid(qualification: str) -> bool:
    """Require the target and non-system database guard before permission checks."""
    compact = re.sub(r"\s+", "", qualification).casefold()
    context = compact.find("ifdb_id()<=4or@demoid<>'qry-023'ordb_name()<>@targetdatabaseor")
    guard_throw = compact.find("throw51001,", context) if context >= 0 else -1
    permission_check = compact.find("declare@hasshowplan")
    return context >= 0 and context < guard_throw < permission_check


def qualification_ownership_markers_valid(qualification: str) -> bool:
    """Bind marker assignments and exact, length-aware values before permission checks."""
    compact = re.sub(r"\s+", "", qualification).casefold()
    assignments = (
        "@project=max(casewhenname=n'sqlperf.project'thenconvert(nvarchar(max),value)end)",
        "@contract=max(casewhenname=n'sqlperf.contractversion'thenconvert(nvarchar(max),value)end)",
        "@markerdemo=max(casewhenname=n'sqlperf.demoid'thenconvert(nvarchar(max),value)end)",
        "@markerrun=max(casewhenname=n'sqlperf.runtoken'thenconvert(nvarchar(max),value)end)",
    )
    comparisons = (
        "@projectcollatelatin1_general_100_bin2<>n'sql_performanceschulung'ordatalength(@project)<>datalength(n'sql_performanceschulung')",
        "@contractcollatelatin1_general_100_bin2<>n'1.0'ordatalength(@contract)<>datalength(n'1.0')",
        "@markerdemocollatelatin1_general_100_bin2<>n'qry-023'ordatalength(@markerdemo)<>datalength(n'qry-023')",
        "@markerruncollatelatin1_general_100_bin2<>convert(nvarchar(max),@runtoken)ordatalength(@markerrun)<>datalength(convert(nvarchar(max),@runtoken))",
    )
    select_from = compact.find("fromsys.extended_propertieswhereclass=0andmajor_id=0andminor_id=0;")
    guard = compact.find("ifdb_id()<=4")
    guard_throw = compact.find("throw51001,", guard)
    permission_check = compact.find("declare@hasshowplan")
    return (
        select_from >= 0
        and guard > select_from
        and all(compact.count(item) == 1 and compact.find(item) < guard for item in assignments)
        and all(compact.count(item) == 1 and guard < compact.find(item) < guard_throw for item in comparisons)
        and guard < guard_throw < permission_check
    )


def preflight_target_derivation_valid(preflight: str) -> bool:
    """Bind target derivation, input rules, and fail-closed guard operators."""
    compact = re.sub(r"\s+", "", preflight).casefold()
    declarations = (
        "declare@demoidvarchar(7)='$(demoid)';",
        "declare@runtokenvarchar(20)='$(runtoken)';",
        "declare@targetdatabasesysname=n'$(targetdatabase)';",
        "declare@expecteddatabasesysname=convert(sysname,n'sqlperf_lab_'+replace(@demoid,'-','')+n'_'+@runtoken);",
    )
    guard = (
        "if@demoid<>'qry-023'or@runtokenisnullorlen(@runtoken)notbetween1and20"
        "ordatalength(@runtoken)notbetween1and20"
        "or@runtokencollatelatin1_general_100_bin2like'%[^a-z0-9_]%'"
        "or@targetdatabase<>@expecteddatabase"
    )
    guard_start = compact.find(guard)
    guard_throw = compact.find("throw51000,", guard_start) if guard_start >= 0 else -1
    return (
        all(compact.count(item) == 1 and compact.find(item) < guard_start for item in declarations)
        and compact.count(guard) == 1
        and guard_start >= 0
        and guard_throw > guard_start
    )


def validate(demo: Path = DEMO, repository: Path = ROOT) -> list[str]:
    errors: list[str] = []
    proposed_manifest = demo / "manifest.proposed.json"
    catalog_manifest = demo / "manifest.json"
    try:
        manifest = json.loads(proposed_manifest.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return [f"Cannot load proposed manifest: {exc}"]
    if type(manifest) is not dict:
        return ["proposed manifest root must be an object"]

    require(not catalog_manifest.exists(), "QRY-023 must not have a catalog manifest.json", errors)
    require(manifest.get("demo_id") == "QRY-023", "proposed manifest must identify QRY-023", errors)
    require(manifest.get("contract_version") == "1.0", "proposed manifest contract version must be 1.0", errors)
    require(manifest.get("safety_level") == "YELLOW", "proposed manifest must retain YELLOW", errors)
    require(manifest.get("execution_safety_contract") == EXPECTED_EXECUTION_SAFETY_CONTRACT,
            "manifest must bind the proposed size, session, abort, residual-state and caller-enforcement limits", errors)
    require(manifest.get("authorization_contract") == EXPECTED_AUTHORIZATION_CONTRACT,
            "manifest must bind phase-specific SQL identities and retain the server privilege qualification gate", errors)
    require(manifest.get("credential_profiles") == ["ADMIN", "READER"],
            "manifest must define exactly the two approved QRY-023 credential profiles", errors)
    require(manifest.get("sqlcmd_input_validation") == EXPECTED_SQLCMD_INPUT_VALIDATION,
            "manifest must bind the exact caller-side SQLCMD input validation contract before expansion", errors)
    run_token = manifest.get("run_token")
    require(isinstance(run_token, str) and run_token.isascii() and RUN_TOKEN_PATTERN.fullmatch(run_token) is not None,
            "manifest run_token must satisfy the FWK-010 ASCII caller contract", errors)
    phases = manifest.get("phases")
    require(isinstance(phases, list), "proposed manifest phases must be a list", errors)
    if isinstance(phases, list):
        records_valid = all(type(phase) is dict for phase in phases)
        require(records_valid, "each proposed manifest phase must be an object", errors)
        if records_valid:
            observed_bindings = [
                (phase.get("id"), phase.get("script"), phase.get("database"),
                 phase.get("timeout_seconds"), phase.get("credential_profile"))
                for phase in phases
            ]
            require(observed_bindings == EXPECTED_PHASES,
                    "phase IDs/order, scripts, databases, timeouts, and credential profiles must match the proposed QRY-023 lifecycle", errors)
        for phase in phases:
            if type(phase) is not dict:
                continue
            script = phase.get("script", "")
            require(phase.get("kind") == "sql", f"phase {phase.get('id')} must be SQL", errors)
            require(phase.get("required") is True, f"phase {phase.get('id')} must be required", errors)
            require(phase.get("require_summary") is True, f"phase {phase.get('id')} must require a summary", errors)
            require(type(script) is str and (demo / script).is_file(),
                    f"phase script is missing or invalid: {script}", errors)
    cleanup = manifest.get("cleanup")
    require(type(cleanup) is dict, "manifest cleanup must be an object", errors)
    if type(cleanup) is dict:
        require((cleanup.get("id"), cleanup.get("kind"), cleanup.get("script"),
                 cleanup.get("database"), cleanup.get("timeout_seconds"),
                 cleanup.get("credential_profile"))
                == ("CLEANUP", "sql", "90_Cleanup.sql", "master", 90, "ADMIN"),
                "manifest must bind SQL cleanup to the ADMIN identity and 90_Cleanup.sql in master with a 90-second timeout", errors)
        require(cleanup.get("required") is True and cleanup.get("require_summary") is True,
                "cleanup must be required and summary-checked", errors)
        cleanup_script = cleanup.get("script")
        require(type(cleanup_script) is str and (demo / cleanup_script).is_file(),
                "cleanup script is missing or invalid", errors)
    require(manifest.get("timeout_seconds") == 900
            and manifest.get("cleanup_timeout_seconds") == 90,
            "manifest must retain the 900-second run and 90-second cleanup limits", errors)

    def read(name: str) -> str:
        try:
            return (demo / name).read_text(encoding="utf-8").casefold()
        except OSError as exc:
            errors.append(f"Cannot read {name}: {exc}")
            return ""

    preflight = read("00_Preflight.sql")
    setup = read("10_Setup.sql")
    workload = read("20_Workload.sql")
    qualification = read("25_Qualification_Preflight.sql")
    correctness = read("30_Correctness.sql")
    measurement = read("40_Measurement.sql")
    plan = read("50_Plan_Evidence.sql")
    cleanup_sql = read("90_Cleanup.sql")
    readme = read("README.md")

    framework_measurement_path = repository / "Demos/00_Framework/Sql/FWK_Measurement.sql"
    try:
        framework_measurement = framework_measurement_path.read_text(encoding="utf-8").casefold()
    except OSError as exc:
        framework_measurement = ""
        errors.append(f"Cannot read FWK-004 implementation: {exc}")

    begin_signature = re.search(
        r"create\s+or\s+alter\s+procedure\s+lab\.usp_beginmeasurement(?P<body>.*?)\bas\s+begin",
        framework_measurement, re.DOTALL)
    end_signature = re.search(
        r"create\s+or\s+alter\s+procedure\s+lab\.usp_endmeasurement(?P<body>.*?)\bas\s+begin",
        framework_measurement, re.DOTALL)
    require(begin_signature is not None, "FWK-004 must declare USP_BeginMeasurement", errors)
    require(end_signature is not None, "FWK-004 must declare USP_EndMeasurement", errors)
    if begin_signature:
        begin = re.sub(r"\s+", " ", begin_signature.group("body"))
        for parameter in ("@demoid varchar(7)", "@runtoken varchar(20)", "@phase varchar(16)",
                          "@iteration int", "@capturesessionwaits bit = 1",
                          "@measurementrunid uniqueidentifier output"):
            require(parameter in begin, f"FWK-004 Begin signature must retain {parameter}", errors)
    if end_signature:
        end = re.sub(r"\s+", " ", end_signature.group("body"))
        for parameter in ("@demoid varchar(7)", "@runtoken varchar(20)",
                          "@measurementrunid uniqueidentifier", "@resultrows bigint = null"):
            require(parameter in end, f"FWK-004 End signature must retain {parameter}", errors)

    workload_compact = re.sub(r"\s+", "", workload)
    require("execlab.usp_beginmeasurement@demoid='qry-023',@runtoken=@runtoken,@phase=@phase,@iteration=@iteration,@capturesessionwaits=0,@measurementrunid=@measurementrunidoutput;"
            in workload_compact,
            "QRY-023 must bind its Begin call to FWK-004 parameters and capture the output ID", errors)
    require("execlab.usp_endmeasurement@demoid='qry-023',@runtoken=@runtoken,@measurementrunid=@measurementrunid,@resultrows=@pathcount;"
            in workload_compact,
            "QRY-023 must bind its End call and result count to FWK-004 parameters", errors)
    for column in ("measurementrunid", "endedatutc", "overalloutcome", "cpums",
                   "logicalreads", "reads", "writes", "elapsedms"):
        require(re.search(rf"^\s*{column}\s+(?:uniqueidentifier|datetime2\(3\)|varchar\(8\)|bigint)(?=\s)",
                          framework_measurement, re.MULTILINE) is not None,
                f"FWK-004 MeasurementRun must expose {column}", errors)
    require(all(f"m.{column} is null" in measurement or f"m.{column}<>'pass'" in measurement
                for column in ("endedatutc", "cpums", "logicalreads", "reads", "writes", "elapsedms"))
            and "m.overalloutcome<>'pass'" in measurement,
            "QRY-023 must reject incomplete or unsuccessful FWK-004 result rows", errors)

    image_lock_path = demo / "container-images.proposed.json"
    try:
        image_lock = json.loads(image_lock_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        image_lock = {}
        errors.append(f"Cannot load proposed container image lock: {exc}")

    require(image_lock.get("contract_version") == "1.0",
            "proposed image lock contract version must be 1.0", errors)
    require(image_lock.get("status") == "PROPOSED" and image_lock.get("runtime_authorized") is False,
            "image lock must remain proposed and must not authorize runtime", errors)
    require(image_lock.get("registry") == "mcr.microsoft.com/mssql/server",
            "image lock must use the declared Microsoft registry", errors)
    resources = image_lock.get("resources", {})
    host_resources = resources.get("host", {})
    container_resources = resources.get("container", {})
    require(resources.get("status") == "PROPOSED_NOT_EMPIRICAL",
            "resource profile must remain an unqualified proposal", errors)
    require(host_resources == {
        "architecture": "x86_64", "cpu_cores": 2, "cpu_frequency_ghz": 2,
        "memory_gib": 8, "free_disk_gib": 20,
    }, "host resource proposal must retain its reviewed values", errors)
    require(container_resources.get("cpu_cores") == 2
            and container_resources.get("memory_mib") == 4096,
            "container proposal must retain its reviewed CPU and memory limits", errors)
    require(2048 <= container_resources.get("sql_memory_limit_mib", 0)
            < container_resources.get("memory_mib", 0)
            and container_resources.get("sql_memory_limit_mib") == 3072,
            "SQL memory limit must cover startup minimum and remain below container memory", errors)
    require(container_resources.get("timeout_seconds") == manifest.get("timeout_seconds")
            and container_resources.get("cleanup_timeout_seconds") == manifest.get("cleanup_timeout_seconds"),
            "resource profile time budgets must match the proposed harness manifest", errors)
    image_profiles = image_lock.get("profiles")
    expected_tags = {
        15: (150, "2019-CU32-GDR12-ubuntu-20.04"),
        16: (160, "2022-CU27-GDR1-ubuntu-22.04"),
        17: (170, "2025-CU10-ubuntu-22.04"),
    }
    require(isinstance(image_profiles, list) and len(image_profiles) == 3,
            "image lock must declare exactly three product profiles", errors)
    image_builds: dict[int, str] = {}
    if isinstance(image_profiles, list):
        for profile in image_profiles:
            major = profile.get("product_major_version")
            require(major in expected_tags, f"unsupported image product major version: {major}", errors)
            if major not in expected_tags:
                continue
            level, tag = expected_tags[major]
            digest = profile.get("manifest_digest", "")
            config_digest = profile.get("config_digest", "")
            require(profile.get("compatibility_level") == level,
                    f"product {major} image lock has the wrong compatibility level", errors)
            require(profile.get("platform") == "linux/amd64",
                    f"product {major} image must remain linux/amd64", errors)
            require(profile.get("source_tag") == tag,
                    f"product {major} must retain its reviewed MCR source tag", errors)
            require(re.fullmatch(r"sha256:[0-9a-f]{64}", digest) is not None,
                    f"product {major} must have a valid manifest digest", errors)
            require(re.fullmatch(r"sha256:[0-9a-f]{64}", config_digest) is not None,
                    f"product {major} must have a valid config digest", errors)
            require(profile.get("image") == f"mcr.microsoft.com/mssql/server@{digest}",
                    f"product {major} image reference must use its immutable manifest digest", errors)
            build = profile.get("product_version_label", "")
            require(build.startswith(f"{major}."),
                    f"product {major} image label must match its major version", errors)
            image_builds[major] = build
    for major, build in image_builds.items():
        expected_sql = f"when {major} then n'{build.casefold()}'"
        require(expected_sql in preflight and expected_sql in setup,
                f"product {major} image label must match preflight and setup build pins", errors)
    build_review = repository / "Documentation/Project_Planning/GRAPH_TABLES_BUILD_EDITION_REVIEW.md"
    try:
        review_text = build_review.read_text(encoding="utf-8").casefold()
    except OSError as exc:
        review_text = ""
        errors.append(f"Cannot read image build review: {exc}")
    if isinstance(image_profiles, list):
        for profile in image_profiles:
            for field in ("manifest_digest", "config_digest"):
                digest = profile.get(field, "").casefold()
                require(bool(digest) and digest in review_text,
                        f"image review must document {field} for product {profile.get('product_major_version')}",
                        errors)

    for label, source in (("preflight", preflight), ("setup", setup), ("workload", workload),
                          ("qualification preflight", qualification), ("cleanup", cleanup_sql)):
        for marker in ("sqlperf.project", "sqlperf.contractversion", "sqlperf.demoid", "sqlperf.runtoken"):
            require(marker in source, f"{label} must bind the {marker} ownership marker", errors)
    require("has_perms_by_name" in preflight and "create database" in preflight,
            "read-only preflight must check database creation permission", errors)
    require(preflight_target_derivation_valid(preflight),
            "read-only preflight must bind the deterministic target database name and exact RunToken format before contract failure", errors)
    build_pins = ("15.0.4500.2", "16.0.4305.5", "17.0.5035.5")
    for build in build_pins:
        require(build in preflight and build in setup,
                f"preflight and setup must pin the proposed engine build {build}", errors)
    require("serverproperty('productversion')" in preflight and "'engine_build'" in preflight,
            "preflight must skip before setup when ProductVersion misses its pin", errors)
    require("showplan" in qualification and "has_perms_by_name" in qualification,
            "qualification preflight must check SHOWPLAN before query execution", errors)
    require(qualification_permission_gate_valid(qualification),
            "qualification preflight must check target DATABASE/SHOWPLAN, SELECT on all query and oracle tables and MeasurementRun, and EXECUTE on the measurement procedure before SKIP_PERMISSION/RETURN", errors)
    require(reader_object_dependencies_covered(
                manifest,
                {
                    "25_Qualification_Preflight.sql": qualification,
                    "30_Correctness.sql": correctness,
                    "40_Measurement.sql": measurement,
                    "50_Plan_Evidence.sql": plan,
                },
                qualification,
            ),
            "every direct dbo/lab object reference in READER phase scripts must have a matching preflight permission check", errors)
    require(reader_phase_scripts_are_read_only(
                manifest,
                {
                    "25_Qualification_Preflight.sql": qualification,
                    "30_Correctness.sql": correctness,
                    "40_Measurement.sql": measurement,
                    "50_Plan_Evidence.sql": plan,
                },
            ),
            "READER script text must not contain persistent writes, DDL/DBCC/security changes, indirect execution, or database-context switching", errors)
    require(qualification_target_context_valid(qualification),
            "qualification preflight must reject system databases and mismatched DB_NAME()/@TargetDatabase before permission checks", errors)
    require(qualification_ownership_markers_valid(qualification),
            "qualification preflight must bind all four exact, length-aware ownership markers before permission checks", errors)
    require(qualification_summaries_valid(qualification),
            "qualification preflight summary rows and PRINT markers must match the exact permission-skip and success statuses", errors)
    require("create table dbo.person" in workload and "as node" in workload,
            "workload must create a Graph NODE table", errors)
    require("create table dbo.friendof as edge" in workload,
            "workload must create a Graph EDGE table", errors)
    require("create index ix_qry023_friendof_from_to on dbo.friendof($from_id,$to_id)" in workload,
            "candidate edge index must remain explicit", errors)
    require(profile_counts(10_000) == (30_000, 20_000, 10_000),
            "deterministic workload arithmetic must remain 30k/20k/10k", errors)
    compact_workload = re.sub(r"\s+", "", workload)
    require("personid=3*p.n+v.roleoffset" in compact_workload,
            "synthetic node IDs must use the three-role path generator", errors)
    require("personid+1" in compact_workload and "personid%3in(1,2)" in compact_workload,
            "synthetic directed edges must connect consecutive roles only", errors)
    require("where match(p1-(e1)->p2-(e2)->p3)" in workload,
            "measurement wrapper must use the declared two-hop MATCH", errors)
    require("where match(p1-(e1)->p2-(e2)->p3)" in correctness,
            "correctness phase must exercise the two-hop MATCH", errors)
    require(correctness.count(" except ") >= 4,
            "correctness must compare expected and actual tuples in both directions", errors)
    require("count_big(*)" in correctness and "<>10000" in correctness,
            "full-path oracle must enforce the 10,000-result cardinality", errors)
    require("'warmup'" in measurement and "while @pair<=5" in measurement,
            "measurement must exclude warm-ups and retain five pairs", errors)
    for metric in ("cpu_ms", "logical_reads", "reads", "writes", "elapsed_ms"):
        require(f"'{metric}'" in measurement,
                f"paired metric summary must retain {metric}", errors)
    require("@pair%2=1" in measurement and "@pair%2=0" in measurement,
            "measurement must alternate AB/BA order", errors)
    compact_measurement = re.sub(r"\s+", "", measurement)
    require("@variant=casewhen(@pair%2=1and@order=1)or(@pair%2=0and@order=2)then'graph'else'relational'end"
            in compact_measurement,
            "measurement must implement the declared alternating order", errors)
    require([paired_order(n) for n in range(1, 6)] == [
        ("GRAPH", "RELATIONAL"), ("RELATIONAL", "GRAPH"),
        ("GRAPH", "RELATIONAL"), ("RELATIONAL", "GRAPH"),
        ("GRAPH", "RELATIONAL"),
    ], "paired-order rule must alternate across five pairs", errors)
    require("statistics xml on" in plan and plan.count("statistics xml off") >= 2
            and "begin try" in plan and "begin catch" in plan and "throw;" in plan,
            "plan evidence must reset STATISTICS XML on success and error in a separate, bounded Actual Plan diagnostic", errors)
    require(plan_summary_follows_cleanup(plan),
            "plan evidence success summaries must occur once after successful STATISTICS XML cleanup and use the expected PASS/OK phase and check fields", errors)
    require(len(count_big_queries(workload)) == 2
            and count_big_queries(plan) == count_big_queries(workload),
            "plan evidence must preserve the measured Graph and relational COUNT_BIG query shapes and order",
            errors)
    require(plan_queries_inside_statistics_window(plan),
            "both plan queries must execute inside the STATISTICS XML ON/OFF window", errors)
    require(plan_xml_output_is_untruncated(plan),
            "plan evidence must set SQLCMDMAXVARTYPEWIDTH to unlimited before requesting XML", errors)
    require("measurement" not in plan, "plan diagnostic must not write measured phase records", errors)
    require("drop database" in cleanup_sql and "single_user" in cleanup_sql,
            "cleanup must remove only the owned disposable database", errors)
    require("sqlperf.project" in cleanup_sql and "sqlperf.contractversion" in cleanup_sql
            and "sqlperf.demoid" in cleanup_sql and "sqlperf.runtoken" in cleanup_sql,
            "database removal must verify all exact ownership markers", errors)
    require("proposed" in readme and "not" in readme and "katalog" in readme,
            "README must explain non-catalogued proposed status", errors)
    require("not executed" in readme or "nicht ausgeführt" in readme,
            "README must state that QRY-023 has not been executed", errors)
    require("vor dem sqlcmd-aufruf" in readme and "sqlcmd-eingabeinjektion" in readme,
            "proposed harness README must state the caller-side SQLCMD input-validation gate", errors)
    require("der fwk-010-caller begrenzt das runtoken" in readme
            and "separat prüft der vorgeschlagene" in readme,
            "README must distinguish caller-only start-character validation from the SQL preflight", errors)
    require(all(build in readme for build in build_pins),
            "README must document all time-bound engine build pins", errors)
    require("container-images.proposed.json" in readme,
            "README must link the proposed immutable image lock", errors)
    require("graph" in readme and "editionsmatrizen" in readme,
            "README must state the sourced Graph edition scope", errors)

    for relative in (
        "Documentation/Demo_Catalog/demo_execution_paths.json",
        "Tests/Lab/performance-lab-matrix.json",
    ):
        path = repository / relative
        try:
            text = path.read_text(encoding="utf-8").casefold()
        except OSError as exc:
            errors.append(f"Cannot read runtime catalog {relative}: {exc}")
            continue
        require('"qry-023"' not in text, f"QRY-023 must not be registered in {relative}", errors)
    return errors


def main() -> int:
    errors = validate()
    if errors:
        for error in errors:
            print(f"FAIL QRY-023: {error}")
        return 1
    print("PASS QRY-023 proposed harness static contract (no SQL execution)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
