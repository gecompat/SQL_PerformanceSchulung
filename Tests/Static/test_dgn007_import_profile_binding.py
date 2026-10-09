"""Synthetische Gegenproben des reinen Profilbindungsvergleichs."""
from dataclasses import FrozenInstanceError, fields, replace
import ast
import hashlib
import json
from pathlib import Path
import sys
import unittest

TOOLS = Path(__file__).resolve().parents[1] / "Tools"
sys.path.insert(0, str(TOOLS))
import dgn007_import_profile_binding as b
import dgn007_import_probe_input as i


def prepared():
    rows = tuple(i.SourceBytes(name, member, hashlib.sha256(body).hexdigest(), body)
                 for name, member in i.MODULES for body in (b"# synthetic raw\r\n",))
    return i.PreparedInput("a" * 40, "b" * 64, "dgn007-docker-sql-only/v1", b"n" * 32, rows)


def installation():
    return b.InstallationDeclaration(b.ASSUMPTION, "linux", "cpython", (3, 12, 14),
        "/synthetic/python", "/synthetic/python-target", ("/synthetic",) * 4,
        "synthetic-abi", ("/synthetic/lib", "/synthetic/lib/lib-dynload", "/synthetic/python312.zip"),
        ("/synthetic/lib", "/synthetic/lib/lib-dynload"), "/synthetic/python312.zip",
        (1, 1, 1, 1, 1, 0), ("BUILTIN", "FROZEN", "PATH"), ("ZIPIMPORTER", "FILEFINDER"))


def control():
    return b.ModuleDeclaration("__main__", "__main__", None, "", "/synthetic/control.py", "CONTROL", (), "NONE")


def builtin(name="sys"):
    return b.ModuleDeclaration(name, name, name, "built-in", "", "BUILTIN", (), "BUILTIN")


def source(name="synthetic_stdlib", path="/synthetic/lib/synthetic_stdlib.py", kind="SOURCE"):
    return b.ModuleDeclaration(name, name, name, path, path, kind, (), kind, name, path)


def frozen(name="_frozen_importlib", group=()):
    mn, sn = b.FROZEN_NAMES.get(name, (name, name))
    return b.ModuleDeclaration(name, mn, sn, "frozen", "", "FROZEN", (), "FROZEN", aliasGroup=group)


def fixture(ordinal=1, modules=None, inst=None):
    context = b.derive_binding_context(prepared(), ordinal)
    modules = tuple(sorted(modules or (control(), frozen(), source(), builtin()), key=lambda r: r.name))
    worker = b.WorkerDeclaration(ordinal, b.ENTRIES[ordinal-1], "PRE_IMPORT", inst or installation(),
                                tuple(r.name for r in modules if r.kind == "CONTROL"), modules)
    report = b.ReportedProfile(context, worker.installation, worker.controls, worker.modules)
    return worker, report, context


def both(worker, report, **changes):
    return replace(worker, **changes), replace(report, **changes)


def canonical(v):
    return json.dumps(v, sort_keys=True, ensure_ascii=True, separators=(",", ":"), allow_nan=False).encode("ascii")


def size(worker, context):
    # Unabhängige Rechnung gegen vollständige unveränderte Input82-Metadata.
    return 16 + len(canonical(dict(input=i._metadata(prepared()), worker=b._value(worker), context=b._value(context))))


def at_size(target):
    w, r, c = fixture()
    remaining = target - size(w, c)
    prefixes = list(w.installation.prefixes)
    for index in range(4):
        delta = min(remaining, 4096 - len(prefixes[index]))
        prefixes[index] += "x" * delta
        remaining -= delta
    if remaining:
        raise AssertionError("synthetic fixture capacity")
    inst = replace(w.installation, prefixes=tuple(prefixes))
    return replace(w, installation=inst), replace(r, installation=inst), c


# Namensumfang einer privaten Linux-3.12.3-Charakterisierung, keine Sollinventur.
# Labels, private Locator und Liveobjekte werden ausdrücklich nicht übernommen.
CHARACTERIZED_NAMES = (
    "__main__", "_abc", "_ast", "_blake2", "_codecs", "_collections", "_collections_abc",
    "_frozen_importlib", "_frozen_importlib_external", "_functools", "_hashlib", "_imp", "_io",
    "_json", "_opcode", "_operator", "_signal", "_sre", "_stat", "_struct",
    "_sysconfigdata__x86_64-linux-gnu", "_thread", "_tokenize", "_warnings", "_weakref", "_weakrefset",
    "abc", "ast", "builtins", "codecs", "collections", "collections.abc", "contextlib", "copy",
    "copyreg", "dataclasses", "dgn007_import_runtime_profile", "dis", "encodings", "encodings.aliases",
    "encodings.utf_8", "enum", "functools", "genericpath", "hashlib", "importlib", "importlib._abc",
    "importlib._bootstrap", "importlib._bootstrap_external", "importlib.machinery", "importlib.util",
    "inspect", "io", "itertools", "json", "json.decoder", "json.encoder", "json.scanner", "keyword",
    "linecache", "marshal", "opcode", "operator", "os", "os.path", "posix", "posixpath", "re",
    "re._casefix", "re._compiler", "re._constants", "re._parser", "reprlib", "stat", "struct", "sys",
    "sysconfig", "threading", "time", "token", "tokenize", "types", "warnings", "weakref", "zipimport",
)


def relaxed_kind_rows(name):
    # Alle Kindmöglichkeiten; leere Pfade/Locations/Aliase schwächen die Form.
    # Diese Dicts sind Rechenuntergrenzen, ausdrücklich keine gültigen DTOs.
    rows = []
    for kind, loader, origin in (("BUILTIN", "BUILTIN", "built-in"), ("FROZEN", "FROZEN", "frozen"),
                                ("SOURCE", "SOURCE", ""), ("EXTENSION", "EXTENSION", "")):
        mn, sn = b.FROZEN_NAMES.get(name, (name, name)) if kind == "FROZEN" else (name, name)
        rows.append(dict(name=name, moduleName=mn, specName=sn, origin=origin, file="", kind=kind,
                         locations=(), loader=loader, loaderName=name if kind in ("SOURCE", "EXTENSION") else "",
                         loaderPath="", aliasGroup=()))
    if name in ("__main__", "dgn007_import_runtime_profile"):
        for loader in ("NONE", "SOURCE"):
            rows.append(dict(name=name, moduleName=name, specName=None, origin="", file="", kind="CONTROL",
                             locations=(), loader=loader, loaderName=name if loader == "SOURCE" else "",
                             loaderPath="", aliasGroup=()))
    return rows


def relaxed_shared_metadata(ordinal):
    # Formgeprüfter Input82 mit echten Hashes leerer synthetischer Bodies.
    # Größe 0 und unveränderliche Hexbreiten unterapproximieren alle echten Inputs.
    parent = prepared()
    parent = replace(parent, sources=tuple(replace(row, body=b"", sha256=hashlib.sha256(b"").hexdigest())
                                           for row in parent.sources))
    context = b.derive_binding_context(parent, ordinal)
    inst = b._value(installation())
    for key in ("executable", "executable_target", "abi", "inert_zip"):
        inst[key] = ""
    inst.update(prefixes=("",) * 4, roots=("",) * 2, paths=(), files=(), version=(3, 12, 0))
    modules = tuple(min(relaxed_kind_rows(name), key=lambda row: len(canonical(row)))
                    for name in CHARACTERIZED_NAMES)
    worker = dict(ordinal=ordinal, entry=b.ENTRIES[ordinal - 1], phase="PRE_IMPORT", installation=inst,
                  controls=("__main__", "dgn007_import_runtime_profile"), modules=modules)
    return dict(input=i._metadata(parent), worker=worker, context=b._value(context))


class Foreign:
    def __getattribute__(self, _):
        raise RuntimeError("synthetic-private-getter")
    def __eq__(self, _):
        raise RuntimeError("synthetic-private-equality")
    def __iter__(self):
        raise RuntimeError("synthetic-private-iteration")


class MatcherTests(unittest.TestCase):
    def test_characterized_names_shared_metadata_conservative_lower_bound(self):
        self.assertEqual(CHARACTERIZED_NAMES, tuple(sorted(set(CHARACTERIZED_NAMES))))
        self.assertEqual(len(CHARACTERIZED_NAMES), 85)
        names_lf = ("\n".join(CHARACTERIZED_NAMES) + "\n").encode("ascii")
        self.assertEqual(len(names_lf.splitlines()), 85)
        self.assertEqual(hashlib.sha256(names_lf).hexdigest(),
                         "a9e02a88ef624e791c757ab840fb652387871d4b009ed08bf5dca83aa5393d1f")
        keys = {f.name for f in fields(b.ModuleDeclaration)}
        self.assertEqual(len(keys), 11)
        for name in CHARACTERIZED_NAMES:
            choices = relaxed_kind_rows(name)
            self.assertEqual({r["kind"] for r in choices},
                             {"BUILTIN", "FROZEN", "SOURCE", "EXTENSION"} |
                             ({"CONTROL"} if name in ("__main__", "dgn007_import_runtime_profile") else set()))
            for row in choices:
                self.assertEqual(set(row), keys)
        # Feldweise Lockerung und Minimum über alle Kinds können eine gültige
        # Darstellung nur verkürzen. Selbst diese Untergrenze überschreitet den Cap.
        for ordinal in (1, 2, 3):
            metadata = relaxed_shared_metadata(ordinal)
            self.assertEqual(set(metadata), {"input", "worker", "context"})
            self.assertIn("context_sha256", metadata["input"])
            self.assertEqual(len(metadata["input"]["modules"]), 9)
            self.assertEqual(len(metadata["context"]["modules"]), 9)
            self.assertEqual(len(metadata["worker"]["modules"]), 85)
            modules = metadata["worker"]["modules"]
            self.assertEqual(sum(len(canonical(row)) for row in modules), 16363)
            self.assertEqual(len(canonical(modules)), 16449)
            self.assertEqual(len(canonical(metadata["worker"]["installation"])), 342)
            self.assertEqual(len(canonical(metadata["input"]["modules"])), 1714)
            self.assertEqual(len(canonical(metadata["context"]["modules"])), 1714)
            lower = 16 + len(canonical(metadata))
            self.assertEqual(lower, (21144, 21130, 21108)[ordinal - 1])
            self.assertGreater(lower, b.MAX_METADATA)
            relaxed_report = dict(context=metadata["context"],
                                  installation=metadata["worker"]["installation"],
                                  controls=metadata["worker"]["controls"], modules=modules)
            self.assertEqual(16 + len(canonical(relaxed_report)), (18953, 18946, 18935)[ordinal - 1])
            with self.assertRaises(b.BindingRejected) as cm:
                b._canonical(metadata)
            self.assertEqual(str(cm.exception), "METADATA_LIMIT")

    def test_complete_synthetic_name_extent_rejected_only_by_shared_cap(self):
        # Eigene synthetische Kindwahl, keine tatsächliche Installation/Workerbaseline.
        modules = tuple(b.ModuleDeclaration(name, name, None, "", "/synthetic/control.py", "CONTROL", (), "NONE")
                        if name in ("__main__", "dgn007_import_runtime_profile") else builtin(name)
                        for name in CHARACTERIZED_NAMES)
        w, r, c = fixture(modules=modules, inst=replace(installation(), version=(3, 12, 3)))
        b._worker(w)
        b._reported(r)
        b._context(c)
        self.assertEqual(tuple(row.name for row in w.modules), CHARACTERIZED_NAMES)
        self.assertEqual(len(w.modules), 85)
        self.assertLess(len(w.modules), b.MAX_RECORDS)
        self.assertLess(max(len(value.encode("utf-8")) for row in w.modules
                            for value in (row.name, row.moduleName, row.origin, row.file)), b.MAX_FIELD)
        self.assertEqual(size(w, c), 21815)
        self.assertEqual(16 + len(canonical(b._value(r))), 19615)
        self.assertGreater(size(w, c), b.MAX_METADATA)
        self.reject(w, r, c, "METADATA_LIMIT")

    def reject(self, w, r, c, issue=None):
        out = b.match_reported_profile(w, r, c)
        self.assertEqual(out.status, "REJECTED_REPORTED_PROFILE")
        if issue:
            self.assertEqual(out.issue, issue)
        self.assertNotIn("/synthetic", repr(out))
        self.assertNotIn("synthetic-private", repr(out))
        for flag in (out.trust_attested, out.runtime_attested, out.import_used_bytes_attested, out.method_approved):
            self.assertIs(flag, False)
        return out

    def test_positive_three_declared_ordinals(self):
        for n in (1, 2, 3):
            out = b.match_reported_profile(*fixture(n))
            self.assertEqual(out.status, "MATCHED_REPORTED_DECLARATION")
            self.assertEqual(out.assumption, b.ASSUMPTION)
            self.assertEqual(out.validation_scope, "PROJECT_SEMANTIC")
            self.assertEqual(len(out.context_digest), 64)
            self.assertIs(out.runtime_attested, False)
            self.assertIs(out.trust_attested, False)
            self.assertIs(out.import_used_bytes_attested, False)
            self.assertIs(out.method_approved, False)

    def test_digest_domains_and_canonical_size(self):
        w, r, c = fixture()
        out = b.match_reported_profile(w, r, c)
        for domain, value, actual in (("installation-declaration", w.installation, out.installation_digest),
                                      ("worker-declaration", w, out.worker_digest),
                                      ("profile-binding-context", c, out.context_digest)):
            self.assertEqual(actual, hashlib.sha256(canonical([domain, b._value(value)])).hexdigest())
        self.assertEqual(b._input_metadata(c), i._metadata(prepared()))

    def test_same_valid_report_replay_is_only_scalar_match(self):
        args = fixture()
        self.assertEqual(b.match_reported_profile(*args), b.match_reported_profile(*args))
        self.assertIs(b.match_reported_profile(*args).import_used_bytes_attested, False)

    def test_frozen_records_no_private_repr(self):
        for item in fixture() + (installation(), control(), prepared()):
            if type(item) is not i.PreparedInput:
                self.assertNotIn("/synthetic", repr(item))
            with self.assertRaises((FrozenInstanceError, TypeError)):
                item.extra = 7
        w, r, c = fixture()
        self.assertNotIn("nnnn", repr(c))

    def test_version_abi_prefix_target_drift(self):
        for key, value in (("version", (3, 12, 15)), ("abi", "other-abi"),
                            ("prefixes", ("/other",)*4), ("executable_target", "/other/python")):
            w, r, c = fixture()
            self.reject(w, replace(r, installation=replace(r.installation, **{key:value})), c, "PROFILE_MISMATCH")

    def test_four_prefixes_six_flags_required(self):
        for key, value in (("prefixes", ("/synthetic",)*2), ("flags", (1,1,1)),
                           ("flags", (1,1,1,1,1,1)), ("flags", (True,1,1,1,1,0))):
            w,r,c=fixture()
            w,r=both(w,r,installation=replace(w.installation,**{key:value}))
            self.reject(w,r,c)

    def test_declared_context_changes(self):
        w,r,c=fixture()
        for key,value in (("commit","c"*40),("raw27_binding","d"*64),("nonce",b"o"*32)):
            self.reject(w,replace(r,context=replace(c,**{key:value})),c,"CONTEXT_MISMATCH")
        row=replace(c.modules[0],sha256="e"*64)
        self.reject(w,replace(r,context=replace(c,modules=(row,)+c.modules[1:])),c,"CONTEXT_MISMATCH")

    def test_ordinal_entry_phase_are_fixed(self):
        w,r,c=fixture()
        for change in ({"ordinal":0},{"ordinal":True},{"entry":"run_demo"},{"phase":"POST_IMPORT"}):
            self.reject(w,r,replace(c,**change))
        c2=b.derive_binding_context(prepared(),2)
        self.reject(w,replace(r,context=c2),c2,"CONTEXT_MISMATCH")

    def test_parent_baseline_not_selected_by_report(self):
        w,r,c=fixture()
        self.reject(replace(w,installation=replace(w.installation,abi="other")),r,c,"PROFILE_MISMATCH")

    def test_inventory_order_missing_duplicate_extra_controls(self):
        w,r,c=fixture()
        for mods in (tuple(reversed(r.modules)), r.modules[:-1], r.modules+(r.modules[-1],)):
            self.reject(w,replace(r,modules=mods),c)
        for controls in ((),("__main__","extra"),("__main__","__main__")):
            self.reject(w,replace(r,controls=controls),c,"CONTROL_FORM")

    def test_extra_valid_report_module_does_not_match(self):
        w,r,c=fixture()
        mods=tuple(sorted(r.modules+(builtin("extra"),),key=lambda row:row.name))
        self.reject(w,replace(r,modules=mods),c,"PROFILE_MISMATCH")

    def test_own_names_contaminating_both_sides(self):
        for name in sorted(b.OWN_NAMES):
            for row in (builtin(name),source(name),replace(control(),name=name,moduleName=name)):
                w,r,c=fixture(modules=(row,))
                self.reject(w,r,c,"OWN_MODULE_CACHED")

    def test_source_root_escape_on_both_sides(self):
        for path in ("/foreign/module.py", "/synthetic/library/x.py", "/synthetic/lib/../foreign.py", "/synthetic//lib/x.py"):
            w,r,c=fixture(modules=(source(path=path),))
            self.reject(w,r,c,"PATH_FORM")

    def test_locations_escape_and_paths_inert_zip(self):
        w,r,c=fixture(modules=(replace(source(),locations=("/foreign",)),))
        self.reject(w,r,c,"PATH_FORM")
        w,r,c=fixture(inst=replace(installation(),paths=("/foreign",)))
        self.reject(w,r,c,"PATH_FORM")

    def test_no_silent_origin_file_loader_fix(self):
        for change in ({"file":"/synthetic/lib/other.py"},{"origin":"/synthetic/lib/other.py"},
                       {"loaderName":"other"},{"loaderPath":"/synthetic/lib/other.py"},
                       {"loader":"LAZY"},{"kind":"BUILTIN"}):
            w,r,c=fixture(modules=(replace(source(),**change),))
            self.reject(w,r,c,"MODULE_FORM")

    def test_source_extension_positive_and_filename_equal(self):
        for kind in ("SOURCE","EXTENSION"):
            self.assertEqual(b.match_reported_profile(*fixture(modules=(source(kind=kind),))).status,
                             "MATCHED_REPORTED_DECLARATION")

    def test_missing_spec_control_only(self):
        for row in (replace(source(),specName=None), replace(control(),origin="/synthetic/control.py"),
                    replace(control(),locations=("/synthetic",))):
            self.reject(*fixture(modules=(row,)),"MODULE_FORM")
        self.assertEqual(b.match_reported_profile(*fixture(modules=(control(),))).status,
                         "MATCHED_REPORTED_DECLARATION")

    def test_alias_pair_singleton_and_empty_relation(self):
        for pair in b.ALIAS_PAIRS:
            for rows in ((frozen(pair[0]),), tuple(frozen(n) for n in pair), tuple(frozen(n,pair) for n in pair)):
                self.assertEqual(b.match_reported_profile(*fixture(modules=rows)).status,"MATCHED_REPORTED_DECLARATION")

    def test_nonempty_alias_missing_partner_mismatch(self):
        pair=b.ALIAS_PAIRS[0]
        for rows in ((frozen(pair[0],pair),), (frozen(pair[0],pair),frozen(pair[1])),
                     (replace(frozen(pair[0],pair),specName="wrong"),frozen(pair[1],pair))):
            self.reject(*fixture(modules=rows))

    def test_no_free_alias_or_object_address(self):
        for group in (("a","b"),(1,2),("_frozen_importlib",)):
            self.reject(*fixture(modules=(replace(frozen(),aliasGroup=group),)))

    def test_frozen_and_builtin_locator_form_not_new_root_trust(self):
        for row in (replace(frozen(),file="relative.py"),replace(frozen(),locations=("relative",)),
                    replace(frozen(),file="/synthetic/../other.py"),replace(builtin(),file="relative.py")):
            self.reject(*fixture(modules=(row,)),"PATH_FORM")
        self.assertEqual(b.match_reported_profile(*fixture(modules=(replace(frozen(),file="/other/frozen.py"),))).status,
                         "MATCHED_REPORTED_DECLARATION")

    def test_file_fingerprints_are_declarations_only(self):
        inst=installation()
        files=(b.FileFingerprint(inst.executable_target,32,"a"*64), b.FileFingerprint("/synthetic/lib/a.py",64,"b"*64))
        out=b.match_reported_profile(*fixture(inst=replace(inst,files=files)))
        self.assertEqual(out.status,"MATCHED_REPORTED_DECLARATION")
        self.assertIs(out.import_used_bytes_attested,False)
        for changed in (files+(files[1],), (files[1],), (files[0],replace(files[1],path="/foreign/a.py"))):
            self.reject(*fixture(inst=replace(inst,files=changed)),"FILE_FORM")

    def test_combined_exact_limit_plus_one(self):
        w,r,c=at_size(16384)
        self.assertEqual(size(w,c),16384)
        self.assertEqual(b.match_reported_profile(w,r,c).status,"MATCHED_REPORTED_DECLARATION")
        w,r,c=at_size(16385)
        self.assertEqual(size(w,c),16385)
        self.reject(w,r,c,"METADATA_LIMIT")

    def test_report_has_independent_cap(self):
        w,r,c=fixture()
        inst=replace(r.installation,prefixes=("/"+"x"*4095,)*4)
        self.reject(w,replace(r,installation=inst),c,"METADATA_LIMIT")

    def test_report_exact_limit_and_plus_one_before_mismatch(self):
        w,r,c=fixture()
        base=16+len(canonical(b._value(r)))
        for target,issue in ((16384,"PROFILE_MISMATCH"),(16385,"METADATA_LIMIT")):
            remaining=target-base
            prefixes=list(r.installation.prefixes)
            for index in range(4):
                delta=min(remaining,4096-len(prefixes[index]))
                prefixes[index]+="x"*delta
                remaining-=delta
            self.assertEqual(remaining,0)
            changed=replace(r,installation=replace(r.installation,prefixes=tuple(prefixes)))
            self.assertEqual(16+len(canonical(b._value(changed))),target)
            self.reject(w,changed,c,issue)

    def test_ascii_escape_size_counts(self):
        w,r,c=fixture()
        # 4000 UTF8-Bytes zulässig, 12000 ASCII-JSON-Zeichen je Feld.
        inst=replace(w.installation,abi="ä"*2000,prefixes=("/"+"ä"*1000,)*4)
        w,r=both(w,r,installation=inst)
        self.reject(w,r,c,"METADATA_LIMIT")

    def test_individual_field_and_record_limits(self):
        for value in ("x"*4097,"ä"*2049,"bad\0text","\ud800"):
            w,r,c=fixture()
            self.reject(w,replace(r,installation=replace(r.installation,abi=value)),c)
        self.reject(*fixture(modules=tuple(builtin("m%03d"%n) for n in range(257))))

    def test_many_valid_locations_bounded_before_full_dump(self):
        locations=("/synthetic/lib/"+"x"*4000,)*256
        self.reject(*fixture(modules=(replace(source(),locations=locations),)),"METADATA_LIMIT")

    def test_all_shapes_before_early_mismatch(self):
        w,r,c=fixture()
        w=replace(w,installation=replace(w.installation,abi="early-other"))
        r=replace(r,modules=r.modules[:-1]+(replace(r.modules[-1],loaderPath=Foreign()),))
        self.reject(w,r,c,"INVALID_RECORD")

    def test_foreign_exact_types_guard_all_fields(self):
        w,r,c=fixture()
        for obj in (w,r,c,w.installation,w.modules[0],c.modules[0],b.FileFingerprint("/synthetic/python-target",1,"a"*64)):
            for f in fields(type(obj)):
                wrong=replace(obj,**{f.name:Foreign()})
                if type(obj) is b.WorkerDeclaration:
                    args=(wrong,r,c)
                elif type(obj) is b.ReportedProfile:
                    args=(w,wrong,c)
                elif type(obj) is b.BindingContext:
                    args=(w,r,wrong)
                elif type(obj) is b.InstallationDeclaration:
                    args=(w,replace(r,installation=wrong),c)
                elif type(obj) is b.ModuleDeclaration:
                    args=(w,replace(r,modules=(wrong,)+r.modules[1:]),c)
                elif type(obj) is b.SourceDescriptor:
                    args=(w,r,replace(c,modules=(wrong,)+c.modules[1:]))
                else:
                    args=(w,replace(r,installation=replace(r.installation,files=(wrong,))),c)
                self.reject(*args)

    def test_foreign_containers_objects_and_uninitialized_records(self):
        w,r,c=fixture()
        for value in (Foreign(),None,{},True):
            self.reject(value,r,c)
            self.reject(w,value,c)
            self.reject(w,r,value)
        for cls in (b.WorkerDeclaration,b.ReportedProfile,b.BindingContext,b.InstallationDeclaration,
                    b.ModuleDeclaration,b.SourceDescriptor,b.FileFingerprint):
            blank=cls.__new__(cls)
            if cls is b.WorkerDeclaration:self.reject(blank,r,c)
            elif cls is b.ReportedProfile:self.reject(w,blank,c)
            elif cls is b.BindingContext:self.reject(w,r,blank)
            elif cls is b.InstallationDeclaration:self.reject(w,replace(r,installation=blank),c)
            elif cls is b.ModuleDeclaration:self.reject(w,replace(r,modules=(blank,)),c)
            elif cls is b.SourceDescriptor:self.reject(w,r,replace(c,modules=(blank,)+c.modules[1:]))
            else:self.reject(w,replace(r,installation=replace(r.installation,files=(blank,))),c)

    def test_no_tuples_or_primitives_subclasses(self):
        class String(str):pass
        class Tuple(tuple):pass
        w,r,c=fixture()
        self.reject(w,r,replace(c,commit=String(c.commit)))
        self.reject(w,r,replace(c,modules=Tuple(c.modules)))
        self.reject(w,replace(r,installation=replace(r.installation,version=(3,12,True))),c)

    def test_context_derivation_preserves_crlf_and_actual_hash(self):
        p=prepared()
        c=b.derive_binding_context(p,1)
        self.assertEqual(c.modules[0].sha256,hashlib.sha256(p.sources[0].body).hexdigest())
        self.assertNotEqual(c.modules[0].sha256,hashlib.sha256(p.sources[0].body.replace(b"\r\n",b"\n")).hexdigest())
        self.assertEqual(c.nonce,p.nonce)

    def test_descriptor_mapping_order_types_and_body_bounds(self):
        w,r,c=fixture()
        first=c.modules[0]
        for change in ({"ordinal":True},{"ordinal":1},{"module":"wrong"},{"member":"wrong"},
                       {"sha256":"A"*64},{"size":131073},{"size":-1},{"size":True}):
            self.reject(w,r,replace(c,modules=(replace(first,**change),)+c.modules[1:]))
        self.reject(w,r,replace(c,modules=tuple(reversed(c.modules))))
        self.reject(w,r,replace(c,modules=c.modules[:-1]))
        self.reject(w,r,replace(c,modules=tuple(replace(row,size=131072) for row in c.modules)))

    def test_late_invalid_context_beats_early_profile_mismatch(self):
        w,r,c=fixture()
        w=replace(w,installation=replace(w.installation,abi="other-valid"))
        bad=replace(c.modules[-1],sha256=Foreign())
        self.reject(w,r,replace(c,modules=c.modules[:-1]+(bad,)),"INVALID_RECORD")

    def test_null_boolean_digest_and_nonce_forms(self):
        w,r,c=fixture()
        for change in ({"commit":None},{"raw27_binding":True},{"nonce":True},{"nonce":b"n"*31},
                       {"source_profile":"installation-declaration"}):
            self.reject(w,r,replace(c,**change))

    def test_derivation_rechecks_input_rawbytes_and_forms(self):
        p=prepared()
        invalid=(replace(p,nonce=b"short"), replace(p,sources=(replace(p.sources[0],body=b"changed"),)+p.sources[1:]),
                 replace(p,sources=(replace(p.sources[0],module="wrong"),)+p.sources[1:]), Foreign(),
                 i.PreparedInput.__new__(i.PreparedInput),replace(p,sources=(Foreign(),)+p.sources[1:]))
        for bad in invalid:
            with self.assertRaises(b.BindingRejected) as cm:b.derive_binding_context(bad,1)
            self.assertIsNone(cm.exception.__context__)
            self.assertIsNone(cm.exception.__cause__)
            self.assertIn(str(cm.exception),("PARENT_INPUT_INVALID","INVALID_RECORD"))
            self.assertNotIn("changed",str(cm.exception))

    def test_pure_module_ast_boundary(self):
        tree=ast.parse((TOOLS/"dgn007_import_profile_binding.py").read_text(encoding="utf-8"))
        allowed={"dataclasses","hashlib","json","dgn007_import_probe_input"}
        for node in ast.walk(tree):
            if isinstance(node,ast.Import):self.assertTrue(all(n.name in allowed for n in node.names))
            if isinstance(node,ast.ImportFrom):self.assertIn(node.module,allowed)
            if isinstance(node,ast.Call) and isinstance(node.func,ast.Name):
                self.assertNotIn(node.func.id,{"open","exec","eval","compile","print","__import__"})
            if isinstance(node,ast.Attribute):
                self.assertNotIn(node.attr,{"prepare_input","verify_bundle","_validate_edges","observe_current_interpreter","Popen"})


if __name__ == "__main__":
    unittest.main()
