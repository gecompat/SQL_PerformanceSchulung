"""Vorbereitende codefreie Parentkomponente; keine operative Workerattestation."""
from importlib.machinery import ModuleSpec
from types import MappingProxyType, ModuleType


def make_codefree_parent_registry(*, module_type, spec_type, cache,
                                 context_digest, guard, write):
    """Halte Provider einmal; liefere genau einen argumentlosen Versuch.

    Mutable Inhalte hinter Providerobjekten sind vertrauensabhängig. Der
    Caller muss später Kontrollanker, aktiven Runnerframe und I/O nachweisen.
    """
    function_type = type(make_codefree_parent_registry)
    namespace = globals()
    factory = make_codefree_parent_registry
    factory_code = factory.__code__
    state = [False, False, False]
    made = []
    names = ("Tests", "Tests.Contracts")

    def need(ok):
        if not ok:
            raise ValueError("PARENT_REGISTRATION_BINDING")

    def dictionary(value, limit=256):
        need(type(value) is dict and len(value) <= limit)
        for key in value:
            need(type(key) is str and len(key) <= 4096 and "\0" not in key)
            need(len(key.encode("utf-8", "strict")) <= 4096)
        return value

    def function(value):
        need(type(value) is function_type)
        dictionary(value.__globals__)
        defaults, kw, cells = value.__defaults__, value.__kwdefaults__, value.__closure__
        need(defaults is None or (type(defaults) is tuple and len(defaults) <= 32))
        need(cells is None or (type(cells) is tuple and len(cells) <= 32))
        if kw is not None:
            dictionary(kw, 32)
        contents = () if cells is None else tuple((cell, cell.cell_contents) for cell in cells)
        return (value, value.__code__, value.__globals__, defaults,
                () if defaults is None else tuple(defaults), kw,
                () if kw is None else tuple(kw.items()), cells, contents)

    def same_function(held):
        current = function(held[0])
        need(all(current[i] is held[i] for i in (0, 1, 2, 3, 5, 7)))
        need(len(current[4]) == len(held[4])
             and all(a is b for a, b in zip(current[4], held[4])))
        need(len(current[6]) == len(held[6]) and all(a[0] == b[0] and a[1] is b[1]
             for a, b in zip(current[6], held[6])))
        need(len(current[8]) == len(held[8]) and all(a[0] is b[0] and a[1] is b[1]
             for a, b in zip(current[8], held[8])))

    def class_state(cls):
        need(type(cls) is type)
        view = type.__getattribute__(cls, "__dict__")
        need(type(view) is MappingProxyType and len(view) <= 128)
        for key in view:
            need(type(key) is str and len(key) <= 4096 and "\0" not in key)
            need(len(key.encode("utf-8", "strict")) <= 4096)
        raw = dict(view)
        return (cls.__bases__, cls.__mro__, tuple(raw.items()),
                tuple(function(value) for value in raw.values() if type(value) is function_type))

    need(module_type is ModuleType and spec_type is ModuleSpec)
    dictionary(cache)
    need(type(context_digest) is str and len(context_digest) == 64
         and all(c in "0123456789abcdef" for c in context_digest))
    providers = tuple(function(f) for f in (guard, write))
    classes = tuple(class_state(cls) for cls in (module_type, spec_type))
    own_globals = tuple(dictionary(namespace).items())

    def check():
        need(state[0] is True and state[1] is False and state[2] is False)
        current = tuple(dictionary(namespace).items())
        need(factory.__code__ is factory_code and factory.__globals__ is namespace
             and len(current) == len(own_globals) and all(a[0] == b[0] and a[1] is b[1]
             for a, b in zip(current, own_globals)))
        for held in providers:
            same_function(held)
        for cls, held in zip((module_type, spec_type), classes):
            current = class_state(cls)
            need(current[0] is held[0] and current[1] is held[1]
                 and len(current[2]) == len(held[2]) and all(a[0] == b[0] and a[1] is b[1]
                 for a, b in zip(current[2], held[2])))
            need(len(current[3]) == len(held[3]))
            for fn in held[3]:
                same_function(fn)
        dictionary(cache)
        for index, name in enumerate(names):
            if index >= len(made) or made[index][3] is False:
                need(name not in cache)
        for index, v in enumerate(made):
            m, spec, locations, published, linked, md, sd = v
            need(type(m) is module_type and type(spec) is spec_type)
            need(m.__dict__ is md and spec.__dict__ is sd)
            dictionary(md)
            dictionary(sd)
            need(type(locations) is list and len(locations) == 0)
            for actual, expected in ((md.get("__name__"), names[index]),
                    (md.get("__package__"), names[index]), (sd.get("name"), names[index])):
                need(type(actual) is str and actual == expected)
            need(md.get("__spec__") is spec and md.get("__loader__") is None
                 and md.get("__path__") is locations and "__file__" not in md
                 and "__cached__" not in md and sd.get("origin") is None
                 and sd.get("loader") is None and sd.get("loader_state") is None
                 and sd.get("_set_fileattr") is False
                 and sd.get("submodule_search_locations") is locations)
            if published:
                need(cache.get(names[index]) is m)
        if made:
            parent = made[0][5]
            if len(made) == 2 and made[1][4] is True:
                need(parent.get("Contracts") is made[1][0])
            else:
                need("Contracts" not in parent)

    def callback(fn, *args, **kwargs):
        check()
        state[1] = True
        try:
            result = fn(*args, **kwargs)
        finally:
            state[1] = False
            check()
        return result

    def close():
        need(callback(guard) is None)

    def cleanup():
        if made and len(made) == 2:
            md = made[0][5]
            try:
                dictionary(md)
                if md.get("Contracts") is made[1][0]:
                    del md["Contracts"]
            except BaseException:
                pass
        try:
            dictionary(cache)
        except BaseException:
            return
        for index in range(len(made) - 1, -1, -1):
            if cache.get(names[index]) is made[index][0]:
                del cache[names[index]]

    def run():
        if state[0] is not False or state[2] is not False:
            state[2] = True
            return ("REJECTED_CODEFREE_PARENTS", "PARENT_REGISTRATION_BINDING", None)
        state[0] = True
        result, issue = None, "PARENT_REGISTRATION_REJECTED"
        try:
            close()
            for index, name in enumerate(names):
                m = callback(module_type, name)
                close()
                spec = callback(spec_type, name, None, origin=None, is_package=True)
                close()
                need(type(m) is module_type and type(spec) is spec_type)
                md, sd = dictionary(m.__dict__), dictionary(spec.__dict__)
                locations = []
                sd["submodule_search_locations"] = locations
                md.update(__name__=name, __package__=name, __spec__=spec,
                          __loader__=None, __path__=locations)
                v = [m, spec, locations, False, False, md, sd]
                made.append(v)
                close()
                cache[name] = m
                v[3] = True
                if index == 1:
                    made[0][5]["Contracts"] = m
                    v[4] = True
                close()
                for tag in ("BEGIN", "COMPLETE"):
                    row = ('["' + tag + '",1,' + str(index + 6) + ',"PARENT",'
                           + str(index) + ',"' + context_digest + '",null,'
                           + str(index + 9) + ',' + str(index + 6) + ']\n').encode("ascii")
                    need(len(row) <= 256)
                    close()
                    need(callback(write, row) is None)
                    close()
            close()
            result = tuple((v[0], v[1], v[2]) for v in made)
        except BaseException:
            pass
        try:
            close()
        except BaseException:
            result, issue = None, "PARENT_REGISTRATION_BINDING"
        if result is None:
            state[2] = True
            cleanup()
            return ("REJECTED_CODEFREE_PARENTS", issue, None)
        return ("REGISTERED_CODEFREE_PARENTS", "NONE", result)
    return run
