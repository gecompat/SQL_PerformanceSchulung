#!/usr/bin/env python3
"""Check the offline QRY-023 draft without invoking SQL Server or its harness."""

from __future__ import annotations

import json
import hashlib
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DEMO = ROOT / "Demos/05_Query_Patterns/QRY-023_Graph_Tables"
PUBLIC_SYSTEM_SELECT_BASELINE = ROOT / "Documentation/Project_Planning/QRY023_PUBLIC_SYSTEM_OBJECT_BASELINE.json"
EXPECTED_PUBLIC_SYSTEM_SELECT_PROFILES = [
    {"product_major_version": 15, "product_version": "15.0.4500.2", "compatibility_level": 150,
     "count": 186, "sha256_utf16le": "93f1b67ac741cf1c07dc3e7dccd38101deec45fb4307ab218d9ac34c9c19dbbb"},
    {"product_major_version": 16, "product_version": "16.0.4305.5", "compatibility_level": 160,
     "count": 226, "sha256_utf16le": "f127c9c0a4c5ecfd061c536d82a3def7925176c4eddbd5980335a4453e0e405a"},
    {"product_major_version": 17, "product_version": "17.0.5035.5", "compatibility_level": 170,
     "count": 232, "sha256_utf16le": "4a3dd68e28a0d53f8041e82994a0bcfc33230873a4b7f94179b4e62486712392"},
]
EXPECTED_PUBLIC_SYSTEM_SELECT_CONTRACT = {
    "artifact": "Documentation/Project_Planning/QRY023_PUBLIC_SYSTEM_OBJECT_BASELINE.json",
    "scope": "CURRENT_USER_DATABASE_ONLY",
    "comparison": "EXACT_COUNT_AND_SHA256_UTF16LE_CANONICAL",
    "unknown_or_build_drift": "FAIL_NOT_PROVEN",
    "profiles": EXPECTED_PUBLIC_SYSTEM_SELECT_PROFILES,
}
EXPECTED_PHASES = [
    ("PREFLIGHT", "00_Preflight.sql", "master", None, "ADMIN"),
    ("SETUP", "10_Setup.sql", "master", 240, "ADMIN"),
    ("FRAMEWORK", "15_Framework.sql", "target", 180, "ADMIN"),
    ("WORKLOAD", "20_Workload.sql", "target", 300, "ADMIN"),
    ("ADMIN_PERMISSION_INVENTORY", "22_Admin_Permission_Inventory.sql", "target", None, "ADMIN"),
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
    "enforcement_status": "PROPOSED_ISOLATED_CI_CALLER_NOT_GENERAL_RUNTIME_AUTHORIZED",
    "forced_abort_residual_state": (
        "The marked target database may contain partial synthetic objects; connection-cancel completion "
        "and TempDB release are not established. Preserve the target if exact ownership checks or cleanup fail."
    ),
}
EXPECTED_READER_BASELINE_CONTRACT = {
    "instance_scope": "DEDICATED_TO_ONE_QRY023_RUN",
    "user_database_inventory_before_setup": "EMPTY_OR_EXACT_MARKED_SAME_RUN",
    "user_database_inventory_after_setup": "ONLY_EXACT_MARKED_QRY023_TARGET",
    "required_server_permissions": ["CONNECT SQL"],
    "conditionally_tolerated_public_permissions": ["VIEW ANY DATABASE"],
    "server_permission_sources": {
        "CONNECT SQL": ["READER_LOGIN"],
        "VIEW ANY DATABASE": ["public"],
    },
    "endpoint_permissions": {
        "standard_endpoints_only": True,
        "expected": ["CONNECT"],
        "permission_source_role": "public",
        "dedicated_admin_connection": "EXCLUDED",
    },
    "server_role_membership": ["public"],
    "database_role_membership": ["public"],
    "explicit_grant_deny_inventory": "ADMIN_REQUIRED",
    "unknown_or_unavailable_inventory": "NOT_PROVEN",
    "server_or_public_permission_mutation": "FORBIDDEN",
    "implementation_status": "ADMIN_INVENTORY_AND_READER_PERMISSION_SET_IMPLEMENTED_OFFLINE_NOT_ENGINE_QUALIFIED",
}
EXPECTED_SQLCMD_IDENTITY_VARIABLES = {"ReaderLogin": "READER"}
EXPECTED_READER_PERMISSION_EXPECTATION_CONTRACT = {
    "version": "1.0",
    "status": "IMPLEMENTED_OFFLINE_NOT_ENGINE_QUALIFIED",
    "evaluation_identity": "ACTUAL_READER_CONNECTION",
    "captured_classes": ["SERVER", "ENDPOINT", "DATABASE", "SCHEMA", "OBJECT"],
    "tuple_fields": ["context_class", "context_name", "permission_name"],
    "returned_entity_name": "CAPTURED_AND_REQUIRED_NON_NULL",
    "subentity_name": "MUST_BE_NULL",
    "comparison": "EXACT_SET_PER_CALLER_BOUND_CONTEXT",
    "duplicate_rows": "FAIL_CLOSED",
    "missing_null_or_unavailable_result": "NOT_PROVEN",
    "column_level_permissions": "FORBIDDEN",
    "runtime_derived_expectations": "FORBIDDEN",
    "unexpected_custom_securables": "READER_OR_PUBLIC_EXPLICIT_GRANTS_FAIL_CLOSED_BY_ADMIN_INVENTORY",
    "server_permissions": ["CONNECT SQL", "VIEW ANY DATABASE"],
    "endpoint_inventory": {
        "source": "SAME_RUN_ADMIN_MACHINE_RECORD_HANDOFF",
        "dedicated_admin_connection": "EXCLUDED",
        "expected_permissions_per_endpoint": ["CONNECT"],
        "reader_context_function_call": "REQUIRED_FOR_EACH_ADMIN_BOUND_ENDPOINT",
    },
    "database_permissions": ["CONNECT", "SHOWPLAN", "VIEW ANY COLUMN ENCRYPTION KEY DEFINITION", "VIEW ANY COLUMN MASTER KEY DEFINITION"],
    "database_public_system_object_baseline": {
        "permission": "SELECT",
        "principal": "public",
        "object_scope": "NEGATIVE_ID_SYSTEM_OBJECTS_AND_COMPATIBILITY_CATALOG_VIEWS",
        "application_objects": "FORBIDDEN",
        "artifact": "Documentation/Project_Planning/QRY023_PUBLIC_SYSTEM_OBJECT_BASELINE.json",
        "exact_default_object_inventory": "BUILD_PINNED_COUNT_AND_SHA256_CANONICAL",
        "status": "CAPTURED_FOR_PINNED_BUILDS; FULL_QRY023_ENGINE_QUALIFICATION_OPEN",
    },
    "schema_permissions": {"dbo": [], "lab": []},
    "object_permissions": {
        "dbo.Person": ["SELECT"],
        "dbo.FriendOf": ["SELECT"],
        "dbo.RelPerson": ["SELECT"],
        "dbo.RelFriend": ["SELECT"],
        "dbo.OraclePerson": ["SELECT"],
        "dbo.OracleFriendOf": ["SELECT"],
        "dbo.OracleRelPerson": ["SELECT"],
        "dbo.OracleRelFriend": ["SELECT"],
        "lab.MeasurementRun": ["SELECT"],
        "lab.MeasurementWaitSnapshot": [],
        "lab.USP_Qry023MeasureVariant": ["EXECUTE"],
        "lab.USP_BeginMeasurement": [],
        "lab.USP_EndMeasurement": [],
    },
    "admin_inventory_gates": [
        "READER_LOGIN_SID", "DATABASE_USER_SID", "SERVER_AND_DATABASE_ROLES",
        "EXPLICIT_GRANTS_AND_DENIES", "DATABASE_INVENTORY", "ENDPOINT_INVENTORY",
    ],
}
EXPECTED_ADMIN_PERMISSION_INVENTORY_CONTRACT = {
    "version": "1.0",
    "status": "ENGINE_QUALIFIED_PROPOSED_NOT_RUNTIME_AUTHORIZED",
    "phase": "ADMIN_PERMISSION_INVENTORY",
    "context": "EXACT_MARKED_TARGET_DATABASE",
    "metadata_visibility": "VERSIONED_REQUIRED_PERMISSIONS_FAIL_CLOSED",
    "reader_login_binding": "ACTIVE_SQL_LOGIN_NAME_AND_DATABASE_USER_SID_EXACT",
    "server_and_database_role_membership": "NO_EXPLICIT_MEMBERSHIP_BEYOND_IMPLICIT_PUBLIC",
    "explicit_permissions": "READER_AND_PUBLIC_ONLY; GRANT_ONLY; EXACT_DECLARED_BASELINE_SUBSET",
    "database_inventory_after_setup": "ONLY_EXACT_MARKED_QRY023_TARGET",
    "endpoint_inventory": "ALL_VISIBLE; BUILT_IN_NON_ADMIN_ENDPOINTS_ONLY; DAC_EXCLUDED",
    "explicit_database_grant_sources": [
        {"principal": "public", "permission": "CONNECT"},
        {"principal": "READER", "permission": "CONNECT"},
        {"principal": "READER", "permission": "SHOWPLAN"},
        {"principal": "public", "permission": "VIEW ANY COLUMN ENCRYPTION KEY DEFINITION"},
        {"principal": "public", "permission": "VIEW ANY COLUMN MASTER KEY DEFINITION"},
    ],
    "endpoint_inventory_handoff": {
        "format": "ENDPOINT_ID_G_NAME_HEX_H_RECORDS_UTF16LE_HEX",
        "markers": ["QRY023_ENDPOINT_INVENTORY|BEGIN|N", "QRY023_ENDPOINT|ID|HEX", "QRY023_ENDPOINT_INVENTORY|END|N"],
        "maximum_endpoints": 12,
        "consumer": "ACTUAL_READER_CONNECTION",
        "invalid_or_incomplete": "FAIL_NOT_PROVEN",
    },
    "object_inventory_handoff": {
        "format": "FIXED_EXPECTED_OBJECT_COUNT",
        "marker": "QRY023_OBJECT_INVENTORY|PASS|13",
        "consumer": "ACTUAL_READER_CONNECTION",
        "invalid_or_incomplete": "FAIL_NOT_PROVEN",
    },
    "public_system_object_select": EXPECTED_PUBLIC_SYSTEM_SELECT_CONTRACT,
    "unknown_or_unavailable_inventory": "FAIL_NOT_PROVEN",
    "permission_mutation": "FORBIDDEN",
    "runtime_authorized": False,
}
EXPECTED_AUTHORIZATION_CONTRACT = {
    "phase_privileges": {
        "SETUP": ["CREATE DATABASE", "CREATE DATABASE USER FOR ACTIVE READER SQL_LOGIN", "CREATE SCHEMA/TABLE/INDEX", "INSERT SYNTHETIC DATA"],
        "READ_AND_MEASURE": ["SELECT ON FOUR QUERY AND FOUR ORACLE TABLES", "SELECT ON lab.MeasurementRun", "EXECUTE ON lab.USP_Qry023MeasureVariant", "SHOWPLAN ON TARGET DATABASE"],
        "CLEANUP": ["DROP ONLY AFTER EXACT OWNERSHIP MARKERS"],
    },
    "current_fwk010_mode": "PHASE_SPECIFIC_SQL_AUTH_PROFILE",
    "phase_identity_enforced": True,
    "gate_status": "OPEN_UNTIL_PRODUCT_AND_GENERAL_RUNTIME_AUTHORIZATION",
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
    sqlcmd_control_line = re.compile(
        r"(?m)^[ \t]*(?::.*|!!.*|GO\b.*|(?:/\*.*?\*/[ \t]*)+GO\b.*|.*\*/[ \t]*GO\b.*)$",
        re.IGNORECASE,
    )
    direct_execute = re.compile(
        r"\bexec(?:ute)?\s+(?P<schema>\[?(?:dbo|lab)\]?)\s*\.\s*"
        r"(?P<object>\[?[a-z_][a-z0-9_$#@]*\]?)",
        re.IGNORECASE,
    )
    allowed_execute = {("lab", "usp_qry023measurevariant")}
    for script_name in reader_names:
        source = reader_scripts[script_name].removeprefix("\ufeff")
        # SQLCMD consumes control and GO batch lines before SQL Server
        # interprets T-SQL comments, so inspect the original script text here.
        for control_line in sqlcmd_control_line.finditer(source):
            directive = control_line.group(0).strip()
            if (script_name != "50_Plan_Evidence.sql"
                    or not re.fullmatch(r":setvar\s+SQLCMDMAXVARTYPEWIDTH\s+0", directive,
                                        re.IGNORECASE)):
                return False
        source = block_comment.sub(" ", source)
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


def admin_permission_inventory_is_read_only_and_fail_closed(inventory: str) -> bool:
    """Bind inventory surfaces, visibility gates, exact identity and no mutation."""
    uncommented = re.sub(r"/\*.*?\*/|--[^\r\n]*", " ", inventory, flags=re.DOTALL)
    executable = re.sub(r"n?'(?:''|[^'])*'", "''", uncommented, flags=re.IGNORECASE)
    executable = re.sub(r"\binsert\s+@publicsystemselects\s*\(", "select ", executable, flags=re.IGNORECASE)
    executable = re.sub(r"''execute''", "''", executable, flags=re.IGNORECASE)
    raw_compact = re.sub(r"\s+", "", uncommented).casefold()
    compact = re.sub(r"\s+", "", executable).casefold()
    required_surfaces = (
        "master.sys.server_principals", "sys.database_principals",
        "master.sys.server_role_members", "sys.database_role_members",
        "role_principal_id<>@publicprincipalid",
        "role_principal_id<>@publicdatabaseprincipalid",
        "master.sys.server_permissions", "sys.database_permissions",
        "master.sys.databases", "master.sys.endpoints",
        "select@publicdatabaseprincipalid=principal_idfromsys.database_principals",
        "in(@readeruserid,@publicdatabaseprincipalid)",
        "has_perms_by_name(null,null,'viewanysecuritydefinition')",
        "has_perms_by_name(null,null,'viewanydefinition')",
        "has_perms_by_name(null,null,'viewserversecuritystate')",
        "has_perms_by_name(db_name(),'database','viewsecuritydefinition')",
        "has_perms_by_name(db_name(),'database','viewdefinition')",
        "n'viewanycolumnencryptionkeydefinition'",
        "n'viewanycolumnmasterkeydefinition'",
        "p.grantee_principal_id=@publicdatabaseprincipalid",
        "p.class_desc='database'andp.grantee_principal_idin(@publicdatabaseprincipalid,@readeruserid)andp.permission_name=n'connect'",
        "@publicsystemselectexpectedcount=case@majorversion",
        "declare@publicsystemselectstable(",
        "leftjoinsys.system_objectsasoono.object_id=p.major_id",
        "object_name(p.major_id)", "objectpropertyex(p.major_id,'isview')",
        "wheregrantee.name=n'public'andp.class=1andp.major_id<0andp.permission_name=n'select'",
        "string_agg(convert(nvarchar(max)",
        "hashbytes('sha2_256'",
        "@publicsystemselectcount<>@publicsystemselectexpectedcount",
        "@publicsystemselectactualhash<>@publicsystemselectexpectedhash",
        "@publicsystemselectbaselinemismatch=0",
        "@publicsystemselectbaselinemismatch>0",
        "andexists(select1from@" + "publicsystemselectsasbaselinewherebaseline.objectid=p.major_id",
        "baseline.permissionnamecollatelatin1_general_100_bin2=p.permission_namecollatelatin1_general_100_bin2",
        "baseline.statedesccollatelatin1_general_100_bin2=n'grant'",
        "has_perms_by_name(null,null,'viewserverstate')",
        "@readersid<>@readerusersid", "@userdatabasecount<>1",
        "endpoint_id>=65536", "p.state<>'g'", "@unexpectedcount>0",
        "@readerendpointcountnotbetween1and12",
        "o.type=expected.object_type",
        "printconcat('qry023_endpoint_inventory|begin|'",
        "print'qry023_object_inventory|pass|13'",
        "joinsys.objects",
        "@observedobjectcount<>@expectedobjectcountbegin",
        "(n'dbo',n'person',n'u')", "(n'dbo',n'friendof',n'u')",
        "(n'dbo',n'relperson',n'u')", "(n'dbo',n'relfriend',n'u')",
        "(n'dbo',n'oracleperson',n'u')", "(n'dbo',n'oraclefriendof',n'u')",
        "(n'dbo',n'oraclerelperson',n'u')", "(n'dbo',n'oraclerelfriend',n'u')",
        "(n'lab',n'measurementrun',n'u')", "(n'lab',n'measurementwaitsnapshot',n'u')",
        "(n'lab',n'usp_qry023measurevariant',n'p')", "(n'lab',n'usp_beginmeasurement',n'p')",
        "(n'lab',n'usp_endmeasurement',n'p')",
        "count(distincto.object_id)",
        "printconcat('qry023_endpoint_inventory|end|'",
        "printconcat('qry023_endpoint|'",
        "convert(varchar(512),convert(varbinary(256),@endpointname),2)",
        "whereendpoint_id<65536andis_admin_endpoint=0orderbyendpoint_id",
        "print'sqlperf_summary|fail|fail_not_proven'",
        "print'sqlperf_summary|pass|ok'",
    )
    object_count_guard = re.search(
        r"if@observedobjectcount<>@expectedobjectcountbegin(.*?)end;", raw_compact
    )
    forbidden = re.compile(
        r"\b(?:insert|update|delete|merge|truncate|create|alter|drop|grant|deny|revoke|exec(?:ute)?|use|setuser|revert)\b",
        re.IGNORECASE,
    )
    return (
        all(term in raw_compact for term in required_surfaces)
        and raw_compact.count("role_principal_id<>@publicprincipalid") == 2
        and raw_compact.count("role_principal_id<>@publicdatabaseprincipalid") == 2
        and raw_compact.count("wherename=n'public'andtype='r'") == 2
        and raw_compact.count("permission_name=n'select'") >= 2
        and not forbidden.search(executable)
        and raw_compact.find("@unexpectedcount>0") < raw_compact.find("'summary'ascheckid,'pass'asoutcome")
        and object_count_guard is not None
        and "set@unexpectedcount+=1;" in object_count_guard.group(1)
        and compact.find("@visible=0") < compact.find("@readerprincipalid=")
    )


def public_system_select_baseline_is_bound(demo: Path, repository: Path) -> list[str]:
    """Validate the clean-image inventory, its canonical digest, and SQL build bindings."""
    errors: list[str] = []
    try:
        artifact = json.loads((repository / EXPECTED_PUBLIC_SYSTEM_SELECT_CONTRACT["artifact"]).read_text(encoding="utf-8"))
        inventory = (demo / "22_Admin_Permission_Inventory.sql").read_text(encoding="utf-8").casefold()
        image_lock = json.loads((demo / "container-images.proposed.json").read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return [f"Cannot load public system-object SELECT baseline evidence: {exc}"]

    require(artifact.get("status") == "CAPTURED_NOT_YET_INTEGRATED_OR_RUNTIME_QUALIFIED",
            "public system-object SELECT evidence must remain scoped as captured, not QRY-023 qualified", errors)
    profiles = artifact.get("profiles")
    require(type(profiles) is list and len(profiles) == len(EXPECTED_PUBLIC_SYSTEM_SELECT_PROFILES),
            "public system-object SELECT baseline must include exactly the three pinned engine profiles", errors)
    profile_map = {item.get("product_major_version"): item for item in profiles if type(item) is dict}
    locked_profiles = {item.get("product_major_version"): item for item in image_lock.get("profiles", [])}
    for expected in EXPECTED_PUBLIC_SYSTEM_SELECT_PROFILES:
        major = expected["product_major_version"]
        profile = profile_map.get(major)
        lock = locked_profiles.get(major)
        require(profile is not None and lock is not None,
                f"public system-object SELECT baseline is missing SQL Server {major}", errors)
        if profile is None or lock is None:
            continue
        require(profile.get("product_version") == expected["product_version"]
                and profile.get("compatibility_level") == expected["compatibility_level"]
                and profile.get("image_manifest_digest") == lock.get("manifest_digest"),
                f"public system-object SELECT evidence is not bound to the pinned SQL Server {major} profile", errors)
        records = profile.get("records")
        require(type(records) is list and len(records) == expected["count"],
                f"public system-object SELECT SQL Server {major} record count does not match its fixed baseline", errors)
        if type(records) is not list:
            continue
        record_keys = []
        for record in records:
            require(type(record) is dict
                    and set(record) == {"schema", "name", "type_desc", "state_desc", "permission_name", "minor_id"}
                    and record.get("schema") == "sys"
                    and record.get("type_desc") == "VIEW"
                    and record.get("state_desc") == "GRANT"
                    and record.get("permission_name") == "SELECT"
                    and record.get("minor_id") == 0
                    and isinstance(record.get("name"), str)
                    and record["name"].isascii(),
                    f"public system-object SELECT SQL Server {major} contains an invalid or non-default permission record", errors)
            if type(record) is dict and set(record) == {"schema", "name", "type_desc", "state_desc", "permission_name", "minor_id"}:
                record_keys.append((record["schema"], record["name"], record["type_desc"],
                                    record["state_desc"], record["permission_name"], record["minor_id"]))
        require(len(record_keys) == len(set(record_keys)),
                f"public system-object SELECT SQL Server {major} contains duplicate records", errors)
        fields = []
        for record in sorted(record_keys):
            fields.append("".join(f"{len(str(value))}:{value}" for value in record))
        canonical = "\n".join(fields) + "\n"
        digest = hashlib.sha256(canonical.encode("utf-16le")).hexdigest()
        require(profile.get("fresh_user_database_public_system_select_count") == expected["count"]
                and profile.get("fresh_user_database_canonical_sha256_utf16le") == expected["sha256_utf16le"]
                and digest == expected["sha256_utf16le"],
                f"public system-object SELECT SQL Server {major} canonical digest does not match the fixed expectation", errors)
        require(str(expected["count"]) in inventory and expected["sha256_utf16le"] in inventory,
                f"ADMIN SQL does not bind the exact SQL Server {major} count and digest", errors)
        require(f"productversion'))=n'{expected['product_version']}'" in inventory,
                f"ADMIN SQL does not bind the public system-object SELECT baseline to exact build {expected['product_version']}", errors)
    return errors
def reader_effective_permission_inventory_is_fail_closed(qualification: str) -> bool:
    """Bind the actual READER permission-set calls, expected securables, and fail gate."""
    uncommented = re.sub(r"/\*.*?\*/|--[^\r\n]*", " ", qualification, flags=re.DOTALL)
    raw = re.sub(r"\s+", "", uncommented).casefold()
    required = (
        "sys.fn_my_permissions(null,n'server')",
        "sys.fn_my_permissions(null,n'database')",
        "sys.fn_my_permissions(n'dbo',n'schema')",
        "sys.fn_my_permissions(n'lab',n'schema')",
        "sys.fn_my_permissions(@endpointname,n'endpoint')",
        "sys.fn_my_permissions(@securablename,n'object')",
        "standardendpointinventory", "endpointinput", "try_convert(varbinary(256)",
        "boundobjectinventory", "@boundobjectinventory<>13", "permissionobjectcursor",
        "(n'dbo',n'person')", "(n'dbo',n'friendof')",
        "(n'dbo',n'relperson')", "(n'dbo',n'relfriend')",
        "(n'dbo',n'oracleperson')", "(n'dbo',n'oraclefriendof')",
        "(n'dbo',n'oraclerelperson')", "(n'dbo',n'oraclerelfriend')",
        "(n'lab',n'measurementrun')", "(n'lab',n'measurementwaitsnapshot')",
        "(n'lab',n'usp_qry023measurevariant')", "(n'lab',n'usp_beginmeasurement')",
        "(n'lab',n'usp_endmeasurement')",
        "@permissionmismatchcount>0or@permissionduplicatecount>0",
        "@entitynamemissingcount>0",
        "whereentitynameisnull", "wherenullif(subentity_name,n'')isnull",
        "print'sqlperf_summary|fail|fail_not_proven'",
        "print'sqlperf_summary|pass|ok'",
    )
    return (
        all(term in raw for term in required)
        and raw.count("sys.fn_my_permissions(") == 6
        and raw.count("wherenullif(subentity_name,n'')isnull") == 4
        and raw.find("@permissionmismatchcount>0or") < raw.find("'summary'ascheckid,'pass'asoutcome")
    )


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
    require(manifest.get("reader_baseline_contract") == EXPECTED_READER_BASELINE_CONTRACT,
            "manifest must bind the isolated READER baseline, inventory, role, endpoint and no-mutation contract", errors)
    require(manifest.get("authorization_contract") == EXPECTED_AUTHORIZATION_CONTRACT,
            "manifest must bind phase-specific SQL identities and retain the server privilege qualification gate", errors)
    require(manifest.get("credential_profiles") == ["ADMIN", "READER"],
            "manifest must define exactly the two approved QRY-023 credential profiles", errors)
    require(manifest.get("sqlcmd_identity_variables") == EXPECTED_SQLCMD_IDENTITY_VARIABLES,
            "manifest must bind the ReaderLogin SQLCMD identity to the READER profile", errors)
    require(manifest.get("reader_permission_expectation_contract")
            == EXPECTED_READER_PERMISSION_EXPECTATION_CONTRACT,
            "manifest must bind the complete fail-closed READER permission expectation contract", errors)
    require(manifest.get("admin_permission_inventory_contract")
            == EXPECTED_ADMIN_PERMISSION_INVENTORY_CONTRACT,
            "manifest must bind the versioned read-only ADMIN inventory and retain its unqualified status", errors)
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
    preflight_compact = re.sub(r"\s+", "", preflight)
    require("@visibleuserdatabasesbit=casewhenhas_perms_by_name(null,null,'viewanydatabase')=1then1else0end" in preflight_compact
            and "select@userdatabasecount=count(*)fromsys.databaseswheredatabase_id>4" in preflight_compact
            and "@existingdatabaseidisnulland@userdatabasecount<>0" in preflight_compact
            and "@existingdatabaseidisnotnulland(@userdatabasecount<>1ornotexists" in preflight_compact,
            "preflight must fail closed unless the instance is empty or contains only the exact marked same-run target database", errors)
    setup = read("10_Setup.sql")
    setup_compact = re.sub(r"\s+", " ", setup).casefold()
    require("@readerlogin sysname" in setup_compact
            and "where name=@readerlogin and type='s' and is_disabled=0" in setup_compact
            and "set @sql=n'use '+quotename(@targetdatabase)+n'; if exists(select 1 from sys.database_principals where name=@loginname)" in setup_compact
            and "create user '+quotename(@readerlogin)+n' for login '+quotename(@readerlogin)" in setup_compact
            and "grant showplan to '+quotename(@readerlogin)+n';" in setup_compact,
            "setup must map only the active SQL READER login inside the exact marked target database", errors)
    require("@datadirectory+@targetdatabase+n'.mdf'" in setup_compact
            and "@logdirectory+@targetdatabase+n'_log.ldf'" in setup_compact
            and "size=8mb,maxsize=512mb,filegrowth=64mb" in setup_compact
            and "@datadirectory is null or @logdirectory is null" in setup_compact
            and "fail_resource" in setup_compact,
            "new QRY-023 databases must fail closed on missing SQL paths and cap data plus log files at 1 GiB", errors)
    workload = read("20_Workload.sql")
    workload_compact = re.sub(r"\s+", "", workload)
    required_reader_grants = (
        "grantselectonobject::dbo.personto[reader]", "grantselectonobject::dbo.friendofto[reader]",
        "grantselectonobject::dbo.relpersonto[reader]", "grantselectonobject::dbo.relfriendto[reader]",
        "grantselectonobject::dbo.oraclepersonto[reader]", "grantselectonobject::dbo.oraclefriendofto[reader]",
        "grantselectonobject::dbo.oraclerelpersonto[reader]", "grantselectonobject::dbo.oraclerelfriendto[reader]",
        "grantselectonobject::lab.measurementrunto[reader]",
        "grantexecuteonobject::lab.usp_qry023measurevariantto[reader]",
    )
    require(all(grant in workload_compact for grant in required_reader_grants),
            "workload must grant READER only the exact declared query/oracle reads and measurement wrapper execution", errors)
    qualification = read("25_Qualification_Preflight.sql")
    admin_inventory = read("22_Admin_Permission_Inventory.sql")
    correctness = read("30_Correctness.sql")
    measurement = read("40_Measurement.sql")
    plan = read("50_Plan_Evidence.sql")
    cleanup_sql = read("90_Cleanup.sql")
    readme = read("README.md")

    require(admin_permission_inventory_is_read_only_and_fail_closed(admin_inventory),
            "ADMIN permission inventory must prove metadata visibility, SID/role/grant/database/endpoint scope, and reject mutation", errors)
    errors.extend(public_system_select_baseline_is_bound(demo, repository))

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
    measurement_compact = re.sub(r"\s+", "", measurement)
    require("joinlab.measurementrunasbrunonbrun.measurementrunid=b.measurementrunid" in measurement_compact
            and "joinlab.measurementrunascrunoncrun.measurementrunid=c.measurementrunid" in measurement_compact
            and "crun.cpums-brun.cpums" in measurement_compact
            and "crun.logicalreads-brun.logicalreads" in measurement_compact,
            "QRY-023 paired metric deltas must read both persisted FWK-004 MeasurementRun rows", errors)
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
    require(reader_effective_permission_inventory_is_fail_closed(qualification),
            "READER preflight must compare exact server/database/schema/object effective permission sets before PASS", errors)
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
    require("enginequalifikation" in readme
            and "2019/2022/2025 bestanden" in readme
            and "menschliche generalprobe" in readme,
            "README must state the bounded three-engine qualification and retain the separate human Generalprobe gate", errors)
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
