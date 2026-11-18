"""Konservative Quelltextkandidaten, keine CPython-P11-Importinventur."""
import argparse
import ast
import gzip
import hashlib
import io
import json
from pathlib import Path
import re
import tarfile


ARCHIVE_SHA256 = "b5796915dc45ff745cfb4e990a7e7c93d6f546328a102ce31448d69ebc37575c"
ARCHIVE_ROOT = "Python-3.12.16/Lib/"
STDLIB_MODULE_NAMES_MEMBER = "Python-3.12.16/Python/stdlib_module_names.h"
STDLIB_MODULE_NAMES_SHA256 = "450581463358b2ffaeca45b261c2e59a41cd6546b487445ed5ff9e0a2b4163a6"
FROZEN_SOURCE_MEMBER = "Python-3.12.16/Python/frozen.c"
FROZEN_SOURCE_SHA256 = "ff2d5e301f1725c013788f30882fd48127a9ecfe891bfaa592cc08c284d4f79f"
BOOTSTRAP_SETUP_MEMBER = "Python-3.12.16/Modules/Setup.bootstrap.in"
BOOTSTRAP_SETUP_SHA256 = "d7a4c34c97f414585c7e8480c106a0f85075fb166d4c82a91c5b0b00df455271"
STDLIB_SETUP_MEMBER = "Python-3.12.16/Modules/Setup.stdlib.in"
STDLIB_SETUP_SHA256 = "d78ae3af2718df36ac5a80531fe21831c0117a26534a977bbf4e7843c2ee6524"
CONFIG_C_TEMPLATE_MEMBER = "Python-3.12.16/Modules/config.c.in"
CONFIG_C_TEMPLATE_SHA256 = "5c76ef60a799f420b09b047dc1087728e5ed08ba82f6c7664c4d4f1d1d715b21"
CONFIGURE_SOURCE_MEMBER = "Python-3.12.16/configure.ac"
CONFIGURE_SOURCE_SHA256 = "4f5345c8d648693030493bdd4a499ae453d477c81a26f61af149d5c70e74d088"
AST_ASDL_MEMBER = "Python-3.12.16/Parser/Python.asdl"
AST_ASDL_SHA256 = "ecc26bc2818ebddec685f96663c811de8915beaa74a7cb1ace6eea3920679ac7"
AST_C_MEMBER = "Python-3.12.16/Python/Python-ast.c"
AST_C_SHA256 = "07983b321fa333242448efc0eb9990f64823532a4a95b01eccf672f69c8c3b4e"
SYS_MODULE_C_MEMBER = "Python-3.12.16/Python/sysmodule.c"
SYS_MODULE_C_SHA256 = "6ac1dffffac870e8a7fbe7578ad6a93ff5f6afb4f501ac3ffd1b5e00f17630ff"
SYS_MODULE_CLINIC_MEMBER = "Python-3.12.16/Python/clinic/sysmodule.c.h"
SYS_MODULE_CLINIC_SHA256 = "957a480449ebdd284eae78bf27ef663b0f964ef595eb49208a82f8cb17a93833"
PRECONFIG_C_MEMBER = "Python-3.12.16/Python/preconfig.c"
PRECONFIG_C_SHA256 = "837e6e39347c4ded7d053c7f23d3ac751614a8dc135332748af7a4b0fcd46cab"
PRECONFIG_HEADER_MEMBER = "Python-3.12.16/Include/internal/pycore_initconfig.h"
PRECONFIG_HEADER_SHA256 = "caf13e2c290ae8375636d0e1f3b1851a90396b3747da650d058c282b8743b558"
INITCONFIG_C_MEMBER = "Python-3.12.16/Python/initconfig.c"
INITCONFIG_C_SHA256 = "a50ff760d49e9d1da8a5a998bcedc8c377f12628d7d0426fc4dab89c1abfeff7"
LONG_HEADER_MEMBER = "Python-3.12.16/Include/internal/pycore_long.h"
LONG_HEADER_SHA256 = "84c0c7bd7ba0c2fbbfb106561e32328e478d8350afe756af6a4862c95d921a06"
LOGGING_SOURCE_SHA256 = "43f86bbc08fdd5c7b6e697abffe1381f534a92bb32e1f1aee8360d6a142592a1"
LOGGING_LEVEL_CALLS_SHA256 = "537ede4580d6934dc4ef812f20ee175f3123abc3f4cc774db15f5f1b0ba15213"
WEAKREFSET_SOURCE_SHA256 = "91895a451d06e9f521a1171b31b9b19bc9740f35af00d4fa106338ab7167c9ac"
COPYREG_SOURCE_SHA256 = "c8eda41f05c6bf95a4da4726a530409d2485ae060b8d019b3a8034389a15d3e9"
TYPING_SOURCE_SHA256 = "be92d60fb8382bb29ead21c128825d7c96d0e8c915b44f840791e49f5a8d554c"
RE_SOURCE_SHA256 = "8ff3c37c63b917fcf8dc8d50993a502292a3dc159e41de4f4018c72a53d1c07b"
COLLECTIONS_SOURCE_SHA256 = "7fdb04dd248ab37909f46d2085bfee56b32d7e91e49ad3a2fad99c453295659b"
INSPECT_SOURCE_SHA256 = "5c54ebf0bfdc25397750e5d0f63800751650ee50e65325ff3ea4069c9bfa5f75"
WARNINGS_SOURCE_SHA256 = "6405e281882932205eae641b2d31fba7776f94517a206d289465a1caffbf310e"
WARNINGS_C_MEMBER = "Python-3.12.16/Python/_warnings.c"
WARNINGS_C_SHA256 = "5567817b35e387b6cc5c37074fdcbf0a3978242564a95460ccdc3fe5d6f08019"
WARNINGS_CLINIC_MEMBER = "Python-3.12.16/Python/clinic/_warnings.c.h"
WARNINGS_CLINIC_SHA256 = "8ec95ee20132c6ccd71b56070cd5028e0db877a745b215cc5e3ddff8d675b5f0"
DIS_SOURCE_SHA256 = "44c0b389c96124d8fb5cb0bc41c7a2aa7a6848ef4001b4000dcbd858efa4a1a2"
TOKENIZE_SOURCE_SHA256 = "026f566ac63e60d69c8185a3880831b657accc5eac984fadf271fc99a5e5825d"
OPCODE_SOURCE_SHA256 = "192f6008508f28d3273bff42eaea9b01c8394dab1607cd36aea778bdd166c3a6"
JSON_ENCODER_SOURCE_SHA256 = "52bfb1b66029cc70fa3bd7fe11df9f2e03922d413407a341b387a22c987f24f8"
JSON_PACKAGE_SOURCE_SHA256 = "d5d41e2c29049515d295d81a6d40b4890fbec8d8482cfb401630f8ef2f77e4d5"
HASHLIB_SOURCE_SHA256 = "6dbdebf270868b391080e21dc9687eddfaf321c965ad979f68d3f5c423c613ab"
RE_INIT_SOURCE_SHA256 = "8ff3c37c63b917fcf8dc8d50993a502292a3dc159e41de4f4018c72a53d1c07b"
RE_COMPILER_SOURCE_SHA256 = "c75620761098a70ed75b9accef63ef2881d8abb6d4e5cbfd10074bd165eefe4d"
RE_PARSER_SOURCE_SHA256 = "a51a85b37cf3f44ba7ff25754da5f31306e4ccfa6eb3c017f9d37bdf4e770840"
RE_CONSTANTS_SOURCE_SHA256 = "fa4fdb200f238f9e7817b63892b0d69833d8165134801e775e10cc113348a375"
FUNCTOOLS_SOURCE_SHA256 = "de4a1d37c795e2a065124b5c49357893433bc6bb111b41277ccc9930ef08d4c9"
FUNCTOOLS_LRU_CACHE_CALLS_SHA256 = "a9e9c4c387f449547755b88929b8bf482c94b8b77431e336f90b8d91d2420391"
COLLECTIONS_NAMEDTUPLE_CALLS_SHA256 = "4a9dcf2bf498fe0d68ca0a0b80269d9556d6e47c9b509a5f3df7465596c954bf"
KEYWORD_SOURCE_SHA256 = "18c2be738c04ad20ad375f6a71db34b3823c7f40b0340f5294d0e89f3c9b093b"
TOKEN_SOURCE_SHA256 = "1a4d994ce9744f4bfe2d964fc24d112a1e76796a08c2e45a2d73c82a8587f922"
OS_SOURCE_SHA256 = "6f3888d1a5bd4f1333116dd75ca8f1d2d951e38c8c8426179417aea097a1eef0"
POSIX_MODULE_C_MEMBER = "Python-3.12.16/Modules/posixmodule.c"
POSIX_MODULE_C_SHA256 = "a8f1410ad95326648a473672ee3bf8158a5f744b7c032c0142327fb252688ab4"
PICKLE_MODULE_C_MEMBER = "Python-3.12.16/Modules/_pickle.c"
PICKLE_MODULE_C_SHA256 = "c3ec3ad77fbb84d902bc7366f9b7cd76f17f9c106cb984ef3e99894cf0f9698b"
PYTHON_IMPORT_C_MEMBER = "Python-3.12.16/Python/import.c"
PYTHON_IMPORT_C_SHA256 = "1cf484fe5a261c742f2da95a720f5d0eb92b10649bf186ca55eedf4557f1b9d0"
PICKLE_EXTENSION_PATH = "usr/local/lib/python3.12/lib-dynload/_pickle.cpython-312-x86_64-linux-gnu.so"
PICKLE_EXTENSION_SHA256 = "f6cdd4a784089665d18243b944051052b8a9452f3b1e40be88bdf685b2afb83d"
HASHLIB_EXTENSION_FACTS = {
    "usr/local/lib/python3.12/lib-dynload/_md5.cpython-312-x86_64-linux-gnu.so": "de8d5205ffce91532652500af1142d00366924b3fb2512989099ecf363358035",
    "usr/local/lib/python3.12/lib-dynload/_blake2.cpython-312-x86_64-linux-gnu.so": "f1731133a22c04dfe02d89cf385cc3cfa408e0996b98956149d319737d576ab3",
    "usr/local/lib/python3.12/lib-dynload/_sha1.cpython-312-x86_64-linux-gnu.so": "31759cc61e6dec07e895840be99bd960aa0cf62a7e05659b93b80a75a76409eb",
    "usr/local/lib/python3.12/lib-dynload/_sha2.cpython-312-x86_64-linux-gnu.so": "6dfdfdcd99c8a57a7218fd7f30f50d9b66c143af9793ac5b02aacd11ecb39cb7",
    "usr/local/lib/python3.12/lib-dynload/_sha3.cpython-312-x86_64-linux-gnu.so": "1cd34c41f43f6f8d93abf79e6d8d2d940062824e57ff778913a1e7bf9b4450f7",
}
HASHLIB_BUILTIN_FALLBACK_BRANCHES = (
    (88, "name in {'SHA1', 'sha1'}", ("SHA1", "sha1"), "_sha1",
     "usr/local/lib/python3.12/lib-dynload/_sha1.cpython-312-x86_64-linux-gnu.so",
     ("import _sha1", "cache['SHA1'] = cache['sha1'] = _sha1.sha1")),
    (91, "name in {'MD5', 'md5'}", ("MD5", "md5"), "_md5",
     "usr/local/lib/python3.12/lib-dynload/_md5.cpython-312-x86_64-linux-gnu.so",
     ("import _md5", "cache['MD5'] = cache['md5'] = _md5.md5")),
    (94, "name in {'SHA256', 'sha256', 'SHA224', 'sha224'}",
     ("SHA224", "sha224", "SHA256", "sha256"), "_sha2",
     "usr/local/lib/python3.12/lib-dynload/_sha2.cpython-312-x86_64-linux-gnu.so",
     ("import _sha2", "cache['SHA224'] = cache['sha224'] = _sha2.sha224",
      "cache['SHA256'] = cache['sha256'] = _sha2.sha256")),
    (98, "name in {'SHA512', 'sha512', 'SHA384', 'sha384'}",
     ("SHA384", "sha384", "SHA512", "sha512"), "_sha2",
     "usr/local/lib/python3.12/lib-dynload/_sha2.cpython-312-x86_64-linux-gnu.so",
     ("import _sha2", "cache['SHA384'] = cache['sha384'] = _sha2.sha384",
      "cache['SHA512'] = cache['sha512'] = _sha2.sha512")),
    (102, "name in {'blake2b', 'blake2s'}", ("blake2b", "blake2s"), "_blake2",
     "usr/local/lib/python3.12/lib-dynload/_blake2.cpython-312-x86_64-linux-gnu.so",
     ("import _blake2", "cache['blake2b'] = _blake2.blake2b",
      "cache['blake2s'] = _blake2.blake2s")),
    (106, "name in {'sha3_224', 'sha3_256', 'sha3_384', 'sha3_512'}",
     ("sha3_224", "sha3_256", "sha3_384", "sha3_512"), "_sha3",
     "usr/local/lib/python3.12/lib-dynload/_sha3.cpython-312-x86_64-linux-gnu.so",
     ("import _sha3", "cache['sha3_224'] = _sha3.sha3_224",
      "cache['sha3_256'] = _sha3.sha3_256",
      "cache['sha3_384'] = _sha3.sha3_384",
      "cache['sha3_512'] = _sha3.sha3_512")),
    (112, "name in {'shake_128', 'shake_256'}",
     ("shake_128", "shake_256"), "_sha3",
     "usr/local/lib/python3.12/lib-dynload/_sha3.cpython-312-x86_64-linux-gnu.so",
     ("import _sha3", "cache['shake_128'] = _sha3.shake_128",
      "cache['shake_256'] = _sha3.shake_256")),
)
MAX_RE_COMPILE_INPUT_CANDIDATES = 4096
PICKLE_SOURCE_SHA256 = "7e3447b6d993a6306a7893fd2fba916010ed79f8e09ceb56158a550fa8099a14"
POSIX_MODULE_CLINIC_MEMBER = "Python-3.12.16/Modules/clinic/posixmodule.c.h"
POSIX_MODULE_CLINIC_SHA256 = "dd89b7a30073abfad8f082966f135a343ca4e1b7b856e3ba696a6e9c27870747"
TARGET_PYCONFIG_SHA256 = "22a6bfe20214fb395e546edd499f826d9d4be7b7b1289b0d391255145a207ed5"
TARGET_IMAGE_MANIFEST_SHA256 = "3c3ba8ad4c85eb63b7568f806434f14e33370056985da7fdf2673621cb1d7e93"
TARGET_IMAGE_CONFIG_SHA256 = "28d30c15b9e9c3b1d557441aad9592226e852f7716451d6c8df5b4f0c3ce3d1b"
TARGET_IMAGE_CONFIG_LAYER_SHA256 = "7f0ea382d75a163999c21529b19913d158821816106eed6f02039f8fdf346779"
TARGET_IMAGE_LAYER_NAMES = (
    "69245854ad5855991d16224f6abf55855d2d73922785206adea9c5c5988434a0",
    "338554e9113fa6731ba588cb8f45e85b3e3fe7ada531ee7d7b0bc9291d616727",
    "d6c30932f8d3f5798b438cce12cdf6cebb1717b52f51e22ff010b4d86667031d",
    "9bab93d346cda15207e5a5000093cee7256ec1092fb689ec3d2997faf31b9a16",
    "c3bb8894691e757a336b94388048f0557392a3e6d6e0a515f0b690a9cbfba3a1",
    "7f0ea382d75a163999c21529b19913d158821816106eed6f02039f8fdf346779",
    "7d0909af463852965fc4e328a11b968cf56707fd15258498d0a43b4c6a1b0953",
)
TARGET_EXECUTABLE_PATH = "usr/local/bin/python3.12"
TARGET_EXECUTABLE_SHA256 = "837a48d7afd08447fb43e28b282026fadb59368620072e57e01f66d12977e5ce"
TARGET_SYSCONFIGDATA_PATH = "usr/local/lib/python3.12/_sysconfigdata__linux_x86_64-linux-gnu.py"
TARGET_SYSCONFIGDATA_SHA256 = "3ed04335c07aa6311958a3514a807ce1ef5b623cea3f29507c3f20b1330c8187"
TARGET_SYSCONFIGDATA_EXPECTED_VALUES = {
    "SOABI": "cpython-312-x86_64-linux-gnu",
    "DESTSHARED": "/usr/local/lib/python3.12/lib-dynload",
    "EXT_SUFFIX": ".cpython-312-x86_64-linux-gnu.so",
    "MULTIARCH": "x86_64-linux-gnu",
    "ABIFLAGS": "",
    "MACHDEP": "linux",
    "prefix": "/usr/local",
    "exec_prefix": "/usr/local",
    "PLATLIBDIR": "lib",
    "PYTHONPATH": "",
    "LIBDIR": "/usr/local/lib",
    "LDLIBRARY": "libpython3.12.so",
    "INSTSONAME": "libpython3.12.so.1.0",
    "Py_ENABLE_SHARED": 1,
}
TARGET_SYSCONFIGDATA_FACT_FIELDS = {
    "SOABI": "soabi",
    "DESTSHARED": "destshared",
    "EXT_SUFFIX": "extension_suffix",
    "MULTIARCH": "multiarch",
    "ABIFLAGS": "abiflags",
    "MACHDEP": "machdep",
    "prefix": "prefix",
    "exec_prefix": "exec_prefix",
    "PLATLIBDIR": "platlibdir",
    "PYTHONPATH": "compiled_pythonpath",
    "LIBDIR": "library_dir",
    "LDLIBRARY": "library_name",
    "INSTSONAME": "library_soname",
    "Py_ENABLE_SHARED": "shared_library_enabled",
}
MAX_TARGET_SYSCONFIGDATA_BYTES = 128 * 1024
TARGET_INERT_ZIP_PATH = "usr/local/lib/python312.zip"
TARGET_PREFIX_STDLIB_LANDMARK = "usr/local/lib/python3.12/os.py"
TARGET_EXEC_PREFIX_LANDMARK = "usr/local/lib/python3.12/lib-dynload"
TARGET_PREFIX_PARENT_DIRECTORIES = (
    "usr/local/lib",
    "usr/local/lib/python3.12",
)
TARGET_PREFIX_VENV_MARKERS = (
    "usr/local/pyvenv.cfg",
    "usr/local/bin/pyvenv.cfg",
)
TARGET_BUILD_MARKER = "usr/local/bin/pybuilddir.txt"
GETPLATFORM_SOURCE_MEMBER = "Python-3.12.16/Python/getplatform.c"
GETPLATFORM_SOURCE_SHA256 = "9a35aa63fba4355a90a2cdc78c3472afa1b9969a48a8bc7413e00c4fed68bbee"
MAX_GETPLATFORM_SOURCE_BYTES = 16 * 1024
MAKEFILE_PRE_MEMBER = "Python-3.12.16/Makefile.pre.in"
MAKEFILE_PRE_SHA256 = "6057ec109daebf752e125e9045d1a3fe0ce4bd284a063724bf2a6e1c5fac9dcd"
MAX_MAKEFILE_PRE_BYTES = 256 * 1024
TARGET_PTH_OVERRIDE_PATHS = (
    "usr/local/bin/python3.12._pth",
    "usr/local/lib/libpython3.12.so.1.0._pth",
    "usr/local/lib/libpython3.12.so._pth",
)
THREADING_SOURCE_SHA256 = "846f450ae794e4aab823a163f8c71d27751148af33e91dd3de886686a4e8ebfb"
THREAD_NATIVE_ID_HEADER_MEMBER = "Python-3.12.16/Include/pythread.h"
THREAD_NATIVE_ID_HEADER_SHA256 = "cd063073710988ea21b54588473542e5f3b2be06f637dc5a028aefd5a7949144"
THREAD_NATIVE_ID_MODULE_MEMBER = "Python-3.12.16/Modules/_threadmodule.c"
THREAD_NATIVE_ID_MODULE_SHA256 = "277217c4a704bc84f9b7caf79123eaed8a45288c3023747e457df5d817cc8bc1"
THREAD_NATIVE_ID_PTHREAD_MEMBER = "Python-3.12.16/Python/thread_pthread.h"
THREAD_NATIVE_ID_PTHREAD_SHA256 = "467f48143ba6bd2dc8f139934d46fdaefe48b11ddf19e476a71ad156996f9195"
IMPORT_USED_BYTES_PROBE_SHA256 = "e4ce3a86f4baedd358ccca148e1dc651b1ca90499b60df0e0159e95acd4ff1cc"
GETPATH_SOURCE_MEMBER = "Python-3.12.16/Modules/getpath.py"
GETPATH_SOURCE_SHA256 = "46901bf54c780960d0ced5ac12a2f8e0db545518b54d6008a10fcefa903f7be2"
SYSCONFIG_SOURCE_SHA256 = "ce56212ba89be181fb90fe62496e6d2e436befaf2dffd10e87ce37d1685271a8"
STRING_SOURCE_SHA256 = "24aeae1f0526250f442022022bf98df9a823b1cb330543ee79e70e44907462e9"
PIPES_SOURCE_SHA256 = "153f2d249d954b5536c6a049202617ff43ba2f9b109c426e06676c577ddedc61"
SITE_SOURCE_SHA256 = "b39ab288cc7a6d0cb3bb2655179221411340b22418e4efdee4c20175537a5fa2"
IMPORTLIB_BOOTSTRAP_SOURCE_SHA256 = "d112d54b7831cf4a818d4841d5ff8003b54df220a6dabafa61f67d7c7a5603f7"
IMPORTLIB_EXTERNAL_SOURCE_SHA256 = "e6ad72f3f0f9b65c99ab52598cd02ab748511dcdce1dd51f18dace9be9a680c6"
IMPORTLIB_MACHINERY_SOURCE_SHA256 = "d045cd7ecf2a12b6ecbfbef79eb114e87ef2ebd756f5b705f73e6f3266e3dede"
IMPORTLIB_UTIL_SOURCE_SHA256 = "671f2995653f673f6d5056a1089debef473bc28ae7114f7a8db71475733d6876"
ZIPIMPORT_SOURCE_SHA256 = "a96f1d7a7b6aaf421a3cf382b94b1422f4f0ad452fdd0bb61d635b560d7a4e91"
DGN007_RUNTIME_PROFILE_SOURCE_SHA256 = "612d5dc648deb43d7f9993a0b6bde4d50d0cc1276231833f2d336488bb61e8f7"
MAX_DGN007_RUNTIME_PROFILE_SOURCE_BYTES = 512 * 1024
MAX_ARCHIVE_BYTES = 64 * 1024 * 1024
MAX_SOURCE_BYTES = 64 * 1024 * 1024
MAX_SOURCE_FILES = 2048
MAX_STDLIB_MODULE_NAMES_BYTES = 64 * 1024
MAX_FROZEN_SOURCE_BYTES = 64 * 1024
MAX_BOOTSTRAP_SETUP_BYTES = 64 * 1024
MAX_STDLIB_SETUP_BYTES = 64 * 1024
MAX_GETPATH_SOURCE_BYTES = 64 * 1024
MAX_CONFIG_C_TEMPLATE_BYTES = 64 * 1024
MAX_CONFIGURE_SOURCE_BYTES = 512 * 1024
MAX_AST_ASDL_BYTES = 64 * 1024
MAX_AST_C_BYTES = 512 * 1024
MAX_SYS_MODULE_C_BYTES = 256 * 1024
MAX_SYS_MODULE_CLINIC_BYTES = 64 * 1024
MAX_PRECONFIG_C_BYTES = 64 * 1024
MAX_PRECONFIG_HEADER_BYTES = 16 * 1024
MAX_LONG_HEADER_BYTES = 16 * 1024
MAX_INITCONFIG_C_BYTES = 128 * 1024
MAX_WORKER_CONTROL_SOURCE_BYTES = 256 * 1024
MAX_WARNINGS_C_BYTES = 64 * 1024
MAX_WARNINGS_CLINIC_BYTES = 16 * 1024
MAX_POSIX_MODULE_C_BYTES = 512 * 1024
MAX_PYTHON_IMPORT_C_BYTES = 256 * 1024
MAX_POSIX_MODULE_CLINIC_BYTES = 384 * 1024
MAX_TARGET_PYCONFIG_BYTES = 64 * 1024
MAX_TARGET_IMAGE_CONFIG_BYTES = 16 * 1024
MAX_TARGET_IMAGE_SAVE_BYTES = 1024 * 1024 * 1024
MAX_S15_FILE_BYTES = 32 * 1024 * 1024
MAX_S15_FILE_TOTAL_BYTES = 64 * 1024 * 1024
ROOTS = (
    "dataclasses", "hashlib", "importlib.machinery", "importlib.util", "json",
    "os", "struct", "sys", "sysconfig", "types", "zipimport", "zlib",
)


def _archive_bytes(archive_path):
    path = Path(archive_path)
    with path.open("rb") as raw:
        archive_bytes = raw.read(MAX_ARCHIVE_BYTES + 1)
    if len(archive_bytes) > MAX_ARCHIVE_BYTES:
        raise ValueError("SOURCE_ARCHIVE_LIMIT")
    if hashlib.sha256(archive_bytes).hexdigest() != ARCHIVE_SHA256:
        raise ValueError("SOURCE_ARCHIVE_MISMATCH")
    return archive_bytes


def _source_archive_data(archive_bytes):
    files = {}
    stdlib_header = None
    frozen_source = None
    bootstrap_setup = None
    stdlib_setup = None
    getpath_source = None
    config_c_template = None
    configure_source = None
    ast_asdl = None
    ast_c_source = None
    sys_module_c_source = None
    sys_module_clinic_source = None
    preconfig_c_source = None
    initconfig_c_source = None
    platform_sources = {
        GETPLATFORM_SOURCE_MEMBER: ("getplatform", GETPLATFORM_SOURCE_SHA256,
                                   MAX_GETPLATFORM_SOURCE_BYTES),
        MAKEFILE_PRE_MEMBER: ("makefile_pre", MAKEFILE_PRE_SHA256,
                              MAX_MAKEFILE_PRE_BYTES),
    }
    platform_source_data = {name: None for name, _, _ in platform_sources.values()}
    warnings_c_source = None
    warnings_clinic_source = None
    posix_module_c_source = None
    posix_module_clinic_source = None
    pickle_module_c_source = None
    python_import_c_source = None
    thread_native_id_header = None
    preconfig_header_source = None
    long_header_source = None
    thread_native_id_module = None
    thread_native_id_pthread = None
    thread_source_members = {
        THREAD_NATIVE_ID_HEADER_MEMBER: "header",
        THREAD_NATIVE_ID_MODULE_MEMBER: "module",
        THREAD_NATIVE_ID_PTHREAD_MEMBER: "pthread",
    }
    total = 0
    with tarfile.open(fileobj=io.BytesIO(archive_bytes), mode="r:xz") as source:
        for member in source:
            if member.name == FROZEN_SOURCE_MEMBER:
                if not member.isfile() or frozen_source is not None \
                        or member.size > MAX_FROZEN_SOURCE_BYTES:
                    raise ValueError("FROZEN_SOURCE_MEMBER")
                stream = source.extractfile(member)
                if stream is None:
                    raise ValueError("FROZEN_SOURCE_MEMBER")
                frozen_source = stream.read(member.size + 1)
                if (len(frozen_source) != member.size
                        or hashlib.sha256(frozen_source).hexdigest()
                        != FROZEN_SOURCE_SHA256):
                    raise ValueError("FROZEN_SOURCE_DIGEST")
                continue
            if member.name == BOOTSTRAP_SETUP_MEMBER:
                if not member.isfile() or bootstrap_setup is not None \
                        or member.size > MAX_BOOTSTRAP_SETUP_BYTES:
                    raise ValueError("BOOTSTRAP_SETUP_MEMBER")
                stream = source.extractfile(member)
                if stream is None:
                    raise ValueError("BOOTSTRAP_SETUP_MEMBER")
                bootstrap_setup = stream.read(member.size + 1)
                if (len(bootstrap_setup) != member.size
                        or hashlib.sha256(bootstrap_setup).hexdigest()
                        != BOOTSTRAP_SETUP_SHA256):
                    raise ValueError("BOOTSTRAP_SETUP_DIGEST")
                continue
            if member.name == STDLIB_SETUP_MEMBER:
                if not member.isfile() or stdlib_setup is not None \
                        or member.size > MAX_STDLIB_SETUP_BYTES:
                    raise ValueError("STDLIB_SETUP_MEMBER")
                stream = source.extractfile(member)
                if stream is None:
                    raise ValueError("STDLIB_SETUP_MEMBER")
                stdlib_setup = stream.read(member.size + 1)
                if (len(stdlib_setup) != member.size
                        or hashlib.sha256(stdlib_setup).hexdigest()
                        != STDLIB_SETUP_SHA256):
                    raise ValueError("STDLIB_SETUP_DIGEST")
                continue
            if member.name == GETPATH_SOURCE_MEMBER:
                if not member.isfile() or getpath_source is not None \
                        or member.size > MAX_GETPATH_SOURCE_BYTES:
                    raise ValueError("GETPATH_SOURCE_MEMBER")
                stream = source.extractfile(member)
                if stream is None:
                    raise ValueError("GETPATH_SOURCE_MEMBER")
                getpath_source = stream.read(member.size + 1)
                if (len(getpath_source) != member.size
                        or hashlib.sha256(getpath_source).hexdigest()
                        != GETPATH_SOURCE_SHA256):
                    raise ValueError("GETPATH_SOURCE_DIGEST")
                continue
            if member.name in (CONFIG_C_TEMPLATE_MEMBER, CONFIGURE_SOURCE_MEMBER):
                is_template = member.name == CONFIG_C_TEMPLATE_MEMBER
                current = config_c_template if is_template else configure_source
                limit = MAX_CONFIG_C_TEMPLATE_BYTES if is_template else MAX_CONFIGURE_SOURCE_BYTES
                if not member.isfile() or current is not None or member.size > limit:
                    raise ValueError("CONFIGURE_SOURCE_MEMBER")
                stream = source.extractfile(member)
                if stream is None:
                    raise ValueError("CONFIGURE_SOURCE_MEMBER")
                body = stream.read(member.size + 1)
                expected = CONFIG_C_TEMPLATE_SHA256 if is_template else CONFIGURE_SOURCE_SHA256
                if len(body) != member.size or hashlib.sha256(body).hexdigest() != expected:
                    raise ValueError("CONFIGURE_SOURCE_DIGEST")
                if is_template:
                    config_c_template = body
                else:
                    configure_source = body
                continue
            if member.name in (AST_ASDL_MEMBER, AST_C_MEMBER):
                is_asdl = member.name == AST_ASDL_MEMBER
                current = ast_asdl if is_asdl else ast_c_source
                limit = MAX_AST_ASDL_BYTES if is_asdl else MAX_AST_C_BYTES
                expected = AST_ASDL_SHA256 if is_asdl else AST_C_SHA256
                if not member.isfile() or current is not None or member.size > limit:
                    raise ValueError("AST_SOURCE_MEMBER")
                stream = source.extractfile(member)
                if stream is None:
                    raise ValueError("AST_SOURCE_MEMBER")
                body = stream.read(member.size + 1)
                if len(body) != member.size or hashlib.sha256(body).hexdigest() != expected:
                    raise ValueError("AST_SOURCE_DIGEST")
                if is_asdl:
                    ast_asdl = body
                else:
                    ast_c_source = body
                continue
            if member.name in (SYS_MODULE_C_MEMBER, SYS_MODULE_CLINIC_MEMBER):
                is_module = member.name == SYS_MODULE_C_MEMBER
                current = sys_module_c_source if is_module else sys_module_clinic_source
                limit = MAX_SYS_MODULE_C_BYTES if is_module else MAX_SYS_MODULE_CLINIC_BYTES
                expected = SYS_MODULE_C_SHA256 if is_module else SYS_MODULE_CLINIC_SHA256
                if not member.isfile() or current is not None or member.size > limit:
                    raise ValueError("SYS_MODULE_SOURCE_MEMBER")
                stream = source.extractfile(member)
                if stream is None:
                    raise ValueError("SYS_MODULE_SOURCE_MEMBER")
                body = stream.read(member.size + 1)
                if len(body) != member.size or hashlib.sha256(body).hexdigest() != expected:
                    raise ValueError("SYS_MODULE_SOURCE_DIGEST")
                if is_module:
                    sys_module_c_source = body
                else:
                    sys_module_clinic_source = body
                continue
            if member.name in (PRECONFIG_C_MEMBER, INITCONFIG_C_MEMBER):
                is_preconfig = member.name == PRECONFIG_C_MEMBER
                current = preconfig_c_source if is_preconfig else initconfig_c_source
                limit = MAX_PRECONFIG_C_BYTES if is_preconfig else MAX_INITCONFIG_C_BYTES
                expected = PRECONFIG_C_SHA256 if is_preconfig else INITCONFIG_C_SHA256
                if not member.isfile() or current is not None or member.size > limit:
                    raise ValueError("PYTHON_CONFIG_SOURCE_MEMBER")
                stream = source.extractfile(member)
                if stream is None:
                    raise ValueError("PYTHON_CONFIG_SOURCE_MEMBER")
                body = stream.read(member.size + 1)
                if len(body) != member.size or hashlib.sha256(body).hexdigest() != expected:
                    raise ValueError("PYTHON_CONFIG_SOURCE_DIGEST")
                if is_preconfig:
                    preconfig_c_source = body
                else:
                    initconfig_c_source = body
                continue
            if member.name == PRECONFIG_HEADER_MEMBER:
                if (not member.isfile() or preconfig_header_source is not None
                        or member.size > MAX_PRECONFIG_HEADER_BYTES):
                    raise ValueError("PRECONFIG_HEADER_MEMBER")
                stream = source.extractfile(member)
                if stream is None:
                    raise ValueError("PRECONFIG_HEADER_MEMBER")
                preconfig_header_source = stream.read(member.size + 1)
                if (len(preconfig_header_source) != member.size
                        or hashlib.sha256(preconfig_header_source).hexdigest()
                        != PRECONFIG_HEADER_SHA256):
                    raise ValueError("PRECONFIG_HEADER_DIGEST")
                continue
            if member.name == LONG_HEADER_MEMBER:
                if (not member.isfile() or long_header_source is not None
                        or member.size > MAX_LONG_HEADER_BYTES):
                    raise ValueError("LONG_HEADER_MEMBER")
                stream = source.extractfile(member)
                if stream is None:
                    raise ValueError("LONG_HEADER_MEMBER")
                long_header_source = stream.read(member.size + 1)
                if (len(long_header_source) != member.size
                        or hashlib.sha256(long_header_source).hexdigest()
                        != LONG_HEADER_SHA256):
                    raise ValueError("LONG_HEADER_DIGEST")
                continue
            if member.name in platform_sources:
                source_name, expected, limit = platform_sources[member.name]
                if (not member.isfile() or platform_source_data[source_name] is not None
                        or member.size > limit):
                    raise ValueError("PLATFORM_SOURCE_MEMBER")
                stream = source.extractfile(member)
                if stream is None:
                    raise ValueError("PLATFORM_SOURCE_MEMBER")
                body = stream.read(member.size + 1)
                if len(body) != member.size or hashlib.sha256(body).hexdigest() != expected:
                    raise ValueError("PLATFORM_SOURCE_DIGEST")
                platform_source_data[source_name] = body
                continue
            if member.name in (WARNINGS_C_MEMBER, WARNINGS_CLINIC_MEMBER):
                is_module = member.name == WARNINGS_C_MEMBER
                current = warnings_c_source if is_module else warnings_clinic_source
                limit = MAX_WARNINGS_C_BYTES if is_module else MAX_WARNINGS_CLINIC_BYTES
                expected = WARNINGS_C_SHA256 if is_module else WARNINGS_CLINIC_SHA256
                if not member.isfile() or current is not None or member.size > limit:
                    raise ValueError("WARNINGS_SOURCE_MEMBER")
                stream = source.extractfile(member)
                if stream is None:
                    raise ValueError("WARNINGS_SOURCE_MEMBER")
                body = stream.read(member.size + 1)
                if len(body) != member.size or hashlib.sha256(body).hexdigest() != expected:
                    raise ValueError("WARNINGS_SOURCE_DIGEST")
                if is_module:
                    warnings_c_source = body
                else:
                    warnings_clinic_source = body
                continue
            if member.name in (POSIX_MODULE_C_MEMBER, POSIX_MODULE_CLINIC_MEMBER):
                is_module = member.name == POSIX_MODULE_C_MEMBER
                current = posix_module_c_source if is_module else posix_module_clinic_source
                limit = MAX_POSIX_MODULE_C_BYTES if is_module else MAX_POSIX_MODULE_CLINIC_BYTES
                expected = POSIX_MODULE_C_SHA256 if is_module else POSIX_MODULE_CLINIC_SHA256
                if not member.isfile() or current is not None or member.size > limit:
                    raise ValueError("POSIX_MODULE_SOURCE_MEMBER")
                stream = source.extractfile(member)
                if stream is None:
                    raise ValueError("POSIX_MODULE_SOURCE_MEMBER")
                body = stream.read(member.size + 1)
                if len(body) != member.size or hashlib.sha256(body).hexdigest() != expected:
                    raise ValueError("POSIX_MODULE_SOURCE_DIGEST")
                if is_module:
                    posix_module_c_source = body
                else:
                    posix_module_clinic_source = body
                continue
            if member.name == PICKLE_MODULE_C_MEMBER:
                if (not member.isfile() or pickle_module_c_source is not None
                        or member.size > MAX_POSIX_MODULE_C_BYTES):
                    raise ValueError("PICKLE_MODULE_SOURCE_MEMBER")
                stream = source.extractfile(member)
                if stream is None:
                    raise ValueError("PICKLE_MODULE_SOURCE_MEMBER")
                pickle_module_c_source = stream.read(member.size + 1)
                if (len(pickle_module_c_source) != member.size
                        or hashlib.sha256(pickle_module_c_source).hexdigest()
                        != PICKLE_MODULE_C_SHA256):
                    raise ValueError("PICKLE_MODULE_SOURCE_DIGEST")
                continue
            if member.name == PYTHON_IMPORT_C_MEMBER:
                if (not member.isfile() or python_import_c_source is not None
                        or member.size > MAX_PYTHON_IMPORT_C_BYTES):
                    raise ValueError("PYTHON_IMPORT_SOURCE_MEMBER")
                stream = source.extractfile(member)
                if stream is None:
                    raise ValueError("PYTHON_IMPORT_SOURCE_MEMBER")
                python_import_c_source = stream.read(member.size + 1)
                if (len(python_import_c_source) != member.size
                        or hashlib.sha256(python_import_c_source).hexdigest()
                        != PYTHON_IMPORT_C_SHA256):
                    raise ValueError("PYTHON_IMPORT_SOURCE_DIGEST")
                continue
            if member.name in thread_source_members:
                source_key = thread_source_members[member.name]
                current = {
                    "header": thread_native_id_header,
                    "module": thread_native_id_module,
                    "pthread": thread_native_id_pthread,
                }[source_key]
                expected = {
                    "header": THREAD_NATIVE_ID_HEADER_SHA256,
                    "module": THREAD_NATIVE_ID_MODULE_SHA256,
                    "pthread": THREAD_NATIVE_ID_PTHREAD_SHA256,
                }[source_key]
                if not member.isfile() or current is not None or member.size > MAX_AST_C_BYTES:
                    raise ValueError("THREAD_NATIVE_ID_SOURCE_MEMBER")
                stream = source.extractfile(member)
                if stream is None:
                    raise ValueError("THREAD_NATIVE_ID_SOURCE_MEMBER")
                body = stream.read(member.size + 1)
                if len(body) != member.size or hashlib.sha256(body).hexdigest() != expected:
                    raise ValueError("THREAD_NATIVE_ID_SOURCE_DIGEST")
                if source_key == "header":
                    thread_native_id_header = body
                elif source_key == "module":
                    thread_native_id_module = body
                else:
                    thread_native_id_pthread = body
                continue
            if member.name == STDLIB_MODULE_NAMES_MEMBER:
                if not member.isfile() or stdlib_header is not None \
                        or member.size > MAX_STDLIB_MODULE_NAMES_BYTES:
                    raise ValueError("STDLIB_MODULE_NAMES_MEMBER")
                stream = source.extractfile(member)
                if stream is None:
                    raise ValueError("STDLIB_MODULE_NAMES_MEMBER")
                stdlib_header = stream.read(member.size + 1)
                if (len(stdlib_header) != member.size
                        or hashlib.sha256(stdlib_header).hexdigest()
                        != STDLIB_MODULE_NAMES_SHA256):
                    raise ValueError("STDLIB_MODULE_NAMES_DIGEST")
                continue
            if not member.isfile() or not member.name.startswith(ARCHIVE_ROOT):
                continue
            relative = member.name[len(ARCHIVE_ROOT):]
            if not relative.endswith(".py"):
                continue
            if (not relative or "\\" in relative or relative.startswith("/")
                    or any(part in ("", ".", "..") for part in relative.split("/"))
                    or relative in files):
                raise ValueError("SOURCE_ARCHIVE_MEMBER")
            if len(files) >= MAX_SOURCE_FILES or member.size > MAX_SOURCE_BYTES - total:
                raise ValueError("SOURCE_ARCHIVE_LIMIT")
            stream = source.extractfile(member)
            if stream is None:
                raise ValueError("SOURCE_ARCHIVE_MEMBER")
            body = stream.read(member.size + 1)
            if len(body) != member.size:
                raise ValueError("SOURCE_ARCHIVE_MEMBER")
            total += len(body)
            files[relative] = body
    return (files, stdlib_header, frozen_source, bootstrap_setup, stdlib_setup,
            getpath_source, config_c_template, configure_source, ast_asdl, ast_c_source,
            sys_module_c_source, sys_module_clinic_source, warnings_c_source,
            warnings_clinic_source, posix_module_c_source, posix_module_clinic_source,
            pickle_module_c_source,
            thread_native_id_header, thread_native_id_module, thread_native_id_pthread,
            platform_source_data["getplatform"], platform_source_data["makefile_pre"],
            python_import_c_source, preconfig_header_source, long_header_source,
            preconfig_c_source,
            initconfig_c_source)


def _source_files(archive_path):
    return _source_archive_data(_archive_bytes(archive_path))[0]


def _stdlib_module_names(header):
    if (type(header) is not bytes or not header
            or len(header) > MAX_STDLIB_MODULE_NAMES_BYTES
            or hashlib.sha256(header).hexdigest() != STDLIB_MODULE_NAMES_SHA256):
        raise ValueError("STDLIB_MODULE_NAMES_DIGEST")
    text = header.decode("ascii")
    blocks = re.findall(
        r"(?m)^static const char\* _Py_stdlib_module_names\[\] = \{\n"
        r"((?:\"[A-Za-z_][A-Za-z0-9_]*\",\n)+)\};$",
        text,
    )
    if len(blocks) != 1:
        raise ValueError("STDLIB_MODULE_NAMES_FORMAT")
    names = tuple(re.findall(r'^"([A-Za-z_][A-Za-z0-9_]*)",$', blocks[0], re.M))
    if not names or names != tuple(sorted(set(names))):
        raise ValueError("STDLIB_MODULE_NAMES_ORDER")
    canonical = "".join(name + "\n" for name in names).encode("ascii")
    return names, hashlib.sha256(canonical).hexdigest()


def _frozen_module_inventory(source_bytes):
    if (type(source_bytes) is not bytes or not source_bytes
            or len(source_bytes) > MAX_FROZEN_SOURCE_BYTES
            or hashlib.sha256(source_bytes).hexdigest() != FROZEN_SOURCE_SHA256):
        raise ValueError("FROZEN_SOURCE_DIGEST")
    text = source_bytes.decode("utf-8")
    tables = {}
    for table in ("bootstrap_modules", "stdlib_modules", "test_modules"):
        blocks = re.findall(
            rf"(?ms)^static const struct _frozen {table}\[\] = \{{\n(.*?)^\}};?$",
            text,
        )
        if len(blocks) != 1:
            raise ValueError("FROZEN_TABLE_FORMAT")
        names = []
        rows = [
            line for line in blocks[0].splitlines()
            if line.strip() and not re.fullmatch(r"\s*/\*.*\*/\s*", line)
        ]
        sentinel = f"{table.removesuffix('_modules')} sentinel"
        if not rows or not re.fullmatch(
                rf"\s*\{{0,\s*0,\s*0\}}\s*/\* {sentinel} \*/\s*", rows[-1]):
            raise ValueError("FROZEN_TABLE_SENTINEL")
        for row in rows[:-1]:
            match = re.fullmatch(r'\s*\{"([^"\\]+)",.*\},?\s*', row)
            if match is None:
                raise ValueError("FROZEN_TABLE_ROW")
            names.append(match.group(1))
        names = tuple(names)
        if not names or len(names) != len(set(names)):
            raise ValueError("FROZEN_TABLE_NAMES")
        tables[table] = tuple(sorted(names))
    alias_blocks = re.findall(
        r"(?ms)^static const struct _module_alias aliases\[\] = \{\n(.*?)^\};$",
        text,
    )
    if len(alias_blocks) != 1:
        raise ValueError("FROZEN_ALIAS_FORMAT")
    alias_rows = [line for line in alias_blocks[0].splitlines() if line.strip()]
    if not alias_rows or not re.fullmatch(
            r"\s*\{0,\s*0\}\s*/\* aliases sentinel \*/\s*", alias_rows[-1]):
        raise ValueError("FROZEN_ALIAS_SENTINEL")
    aliases = []
    for row in alias_rows[:-1]:
        match = re.fullmatch(
            r'\s*\{"([^"\\]+)",\s*(?:"([^"\\]+)"|NULL)\},\s*', row
        )
        if match is None:
            raise ValueError("FROZEN_ALIAS_ROW")
        aliases.append((match.group(1), match.group(2) or ""))
    aliases = tuple(aliases)
    if not aliases or len(aliases) != len({alias for alias, _ in aliases}):
        raise ValueError("FROZEN_ALIAS_NAMES")

    def digest_rows(rows):
        return hashlib.sha256(
            "".join("\t".join(row) + "\n" for row in rows).encode("utf-8")
        ).hexdigest()

    return {
        "bootstrap_names": tables["bootstrap_modules"],
        "stdlib_names": tables["stdlib_modules"],
        "test_names": tables["test_modules"],
        "aliases": tuple(sorted(aliases)),
        "bootstrap_sha256": digest_rows(tuple((name,) for name in tables["bootstrap_modules"])),
        "stdlib_sha256": digest_rows(tuple((name,) for name in tables["stdlib_modules"])),
        "test_sha256": digest_rows(tuple((name,) for name in tables["test_modules"])),
        "aliases_sha256": digest_rows(tuple(sorted(aliases))),
    }


def _bootstrap_setup_inventory(source_bytes):
    if (type(source_bytes) is not bytes or not source_bytes
            or len(source_bytes) > MAX_BOOTSTRAP_SETUP_BYTES
            or hashlib.sha256(source_bytes).hexdigest() != BOOTSTRAP_SETUP_SHA256):
        raise ValueError("BOOTSTRAP_SETUP_DIGEST")
    text = source_bytes.decode("utf-8")
    names = []
    rows = []
    static_count = 0
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if stripped == "*static*":
            static_count += 1
            continue
        match = re.fullmatch(
            r"(?:@MODULE_([A-Z0-9_]+)_TRUE@\s*)?"
            r"([A-Za-z_][A-Za-z0-9_]*)\s+(.+)", stripped
        )
        if match is None:
            raise ValueError("BOOTSTRAP_SETUP_ROW")
        condition, name, sources = match.groups()
        source_paths = sources.split()
        if not source_paths or any(not path.endswith(".c") for path in source_paths):
            raise ValueError("BOOTSTRAP_SETUP_SOURCES")
        names.append(name)
        rows.append((name, condition or ""))
    if static_count != 1:
        raise ValueError("BOOTSTRAP_SETUP_STATIC")
    if len(names) != len(set(names)):
        raise ValueError("BOOTSTRAP_SETUP_NAMES")
    canonical = "".join("\t".join(row) + "\n" for row in sorted(rows)).encode("ascii")
    return {
        "name_count": len(names),
        "conditional_name_count": sum(bool(condition) for _, condition in rows),
        "source_sha256": BOOTSTRAP_SETUP_SHA256,
        "rows_sha256": hashlib.sha256(canonical).hexdigest(),
        "conditional_names": tuple(sorted(
            (name, condition) for name, condition in rows if condition
        )),
    }


def _stdlib_setup_inventory(source_bytes):
    if (type(source_bytes) is not bytes or not source_bytes
            or len(source_bytes) > MAX_STDLIB_SETUP_BYTES
            or hashlib.sha256(source_bytes).hexdigest() != STDLIB_SETUP_SHA256):
        raise ValueError("STDLIB_SETUP_DIGEST")
    text = source_bytes.decode("utf-8")
    entries = []
    test_section = False
    directives = []
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.startswith("#"):
            if stripped == "# Test modules":
                test_section = True
            continue
        if stripped in ("*shared*", "*static*", "*@MODULE_BUILDTYPE@*"):
            directives.append(stripped)
            continue
        match = re.fullmatch(
            r"@MODULE_([A-Z0-9_]+)_TRUE@([A-Za-z_][A-Za-z0-9_]*)\s+(.+)",
            stripped,
        )
        if match is None:
            raise ValueError("STDLIB_SETUP_ROW")
        condition, name, source_list = match.groups()
        source_paths = source_list.split()
        if not source_paths or any(
                not (path.endswith((".c", ".a")) or path.startswith("-")
                     or path.startswith("@") or path.startswith("$("))
                for path in source_paths):
            raise ValueError("STDLIB_SETUP_SOURCES")
        entries.append((name, condition, "test" if test_section else "stdlib"))

    names = tuple(entry[0] for entry in entries)
    if not entries or len(names) != len(set(names)):
        raise ValueError("STDLIB_SETUP_NAMES")
    if directives != ["*@MODULE_BUILDTYPE@*", "*shared*"]:
        raise ValueError("STDLIB_SETUP_DIRECTIVES")
    runtime_rows = tuple(sorted(entry for entry in entries if entry[2] == "stdlib"))
    test_rows = tuple(sorted(entry for entry in entries if entry[2] == "test"))
    canonical = "".join("\t".join(entry) + "\n" for entry in sorted(entries))
    return {
        "stdlib_entry_count": len(runtime_rows),
        "test_entry_count": len(test_rows),
        "condition_count": len({entry[1] for entry in entries}),
        "source_sha256": STDLIB_SETUP_SHA256,
        "rows_sha256": hashlib.sha256(canonical.encode("ascii")).hexdigest(),
        "stdlib_names_sha256": hashlib.sha256(
            "".join(entry[0] + "\n" for entry in runtime_rows).encode("ascii")
        ).hexdigest(),
        "test_names_sha256": hashlib.sha256(
            "".join(entry[0] + "\n" for entry in test_rows).encode("ascii")
        ).hexdigest(),
    }


def _top_level_names(tree):
    assignments = set()
    functions = set()
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            functions.add(node.name)
        elif isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    assignments.add(target.id)
        elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
            assignments.add(node.target.id)
    return assignments, functions


def _getpath_source_inventory(source_bytes):
    if (type(source_bytes) is not bytes or not source_bytes
            or len(source_bytes) > MAX_GETPATH_SOURCE_BYTES
            or hashlib.sha256(source_bytes).hexdigest() != GETPATH_SOURCE_SHA256):
        raise ValueError("GETPATH_SOURCE_DIGEST")
    tree = ast.parse(source_bytes.decode("utf-8"))
    posix_tests = [node for node in tree.body if isinstance(node, ast.If)
                   and ast.unparse(node.test)
                   == "os_name == 'posix' or os_name == 'darwin'"]
    if len(posix_tests) != 1:
        raise ValueError("GETPATH_ZIP_LANDMARK_BRANCH")
    zip_assignments = [node for node in posix_tests[0].body
                       if isinstance(node, ast.Assign)
                       and any(isinstance(target, ast.Name)
                               and target.id == "ZIP_LANDMARK"
                               for target in node.targets)]
    if (len(zip_assignments) != 1 or len(zip_assignments[0].targets) != 1
            or ast.unparse(zip_assignments[0].value)
            != "f'{platlibdir}/python{VERSION_MAJOR}{VERSION_MINOR}.zip'"):
        raise ValueError("GETPATH_ZIP_LANDMARK")
    source_text = source_bytes.decode("utf-8")
    path_branch = source_text.rfind("\n    if os_name == 'nt':")
    path_else = source_text.find("\n    else:", path_branch)
    zip_append = source_text.find(
        "pythonpath.append(joinpath(prefix, ZIP_LANDMARK))"
    )
    stdlib_append = source_text.find("pythonpath.append(stdlib_dir)", path_else)
    platstdlib_append = source_text.find(
        "pythonpath.append(platstdlib_dir)", stdlib_append
    )
    if (path_branch < 0 or path_else < 0 or zip_append < 0
            or not zip_append < path_branch < path_else < stdlib_append < platstdlib_append):
        raise ValueError("GETPATH_DEFAULT_PATH_ORDER")
    pth_override_guard = all(fragment in source_text for fragment in (
        "if not py_setpath and not home_was_set:",
        "for p in [library, executable, real_executable]:",
        "p += '._pth'",
        "pth = readlines(p)",
        "if pth_dir:",
    ))
    if not pth_override_guard:
        raise ValueError("GETPATH_PTH_OVERRIDE_GUARD")
    posix_assignments = {
        target.id: node.value
        for node in posix_tests[0].body if isinstance(node, ast.Assign)
        for target in node.targets if isinstance(target, ast.Name)
    }
    expected_landmarks = {
        "STDLIB_SUBDIR": "f'{platlibdir}/python{VERSION_MAJOR}.{VERSION_MINOR}'",
        "STDLIB_LANDMARKS": (
            "[f'{STDLIB_SUBDIR}/os.py', f'{STDLIB_SUBDIR}/os.pyc']"
        ),
        "PLATSTDLIB_LANDMARK": (
            "f'{platlibdir}/python{VERSION_MAJOR}.{VERSION_MINOR}/lib-dynload'"
        ),
    }
    if any(name not in posix_assignments
           or ast.unparse(posix_assignments[name]) != expression
           for name, expression in expected_landmarks.items()):
        raise ValueError("GETPATH_PREFIX_LANDMARKS")
    assignments, functions = _top_level_names(tree)
    path_variables = (
        "base_exec_prefix", "base_executable", "base_prefix", "exec_prefix",
        "executable", "home", "platlibdir", "platstdlib_dir", "prefix",
        "program_name", "pythonpath", "real_executable_dir", "stdlib_dir",
        "venv_prefix",
    )
    if not set(path_variables).issubset(assignments) or "search_up" not in functions:
        raise ValueError("GETPATH_SOURCE_SYMBOLS")
    config_keys = set()
    for node in ast.walk(tree):
        if (isinstance(node, ast.Subscript) and isinstance(node.value, ast.Name)
                and node.value.id == "config" and isinstance(node.slice, ast.Constant)
                and type(node.slice.value) is str):
            config_keys.add(node.slice.value)
        elif (isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
              and node.func.attr == "get" and isinstance(node.func.value, ast.Name)
              and node.func.value.id == "config" and node.args
              and isinstance(node.args[0], ast.Constant)
              and type(node.args[0].value) is str):
            config_keys.add(node.args[0].value)
    if "pythonpath_env" not in config_keys:
        raise ValueError("GETPATH_SOURCE_CONFIG_KEYS")
    canonical = "".join(name + "\n" for name in path_variables).encode("ascii")
    config_canonical = "".join(name + "\n" for name in sorted(config_keys)).encode("ascii")
    prefix_reads = (
        "base_prefix = config.get('base_prefix')",
        "base_exec_prefix = config.get('base_exec_prefix')",
    )
    prefix_fallbacks = (
        "config['base_prefix'] = base_prefix or prefix",
        "config['base_exec_prefix'] = base_exec_prefix or exec_prefix",
    )
    if (any(source_text.count(line) != 1 for line in prefix_reads + prefix_fallbacks)):
        raise ValueError("GETPATH_BASE_PREFIX_BINDING")
    return {
        "source_sha256": GETPATH_SOURCE_SHA256,
        "source_bytes": len(source_bytes),
        "path_variable_count": len(path_variables),
        "path_variables": path_variables,
        "posix_zip_landmark_template": ast.unparse(zip_assignments[0].value),
        "posix_default_path_append_order": (
            "ZIP_LANDMARK", "stdlib_dir", "platstdlib_dir",
        ),
        "pth_override_guard": True,
        "base_prefix_config_read": True,
        "base_prefix_fallback_bound": True,
        "posix_stdlib_landmark_template": ast.unparse(
            posix_assignments["STDLIB_LANDMARKS"]
        ),
        "posix_platstdlib_landmark_template": ast.unparse(
            posix_assignments["PLATSTDLIB_LANDMARK"]
        ),
        "path_variables_sha256": hashlib.sha256(canonical).hexdigest(),
        "config_key_count": len(config_keys),
        "config_keys": tuple(sorted(config_keys)),
        "config_keys_sha256": hashlib.sha256(config_canonical).hexdigest(),
    }


def _sysconfig_source_inventory(source_bytes):
    if (type(source_bytes) is not bytes or not source_bytes
            or hashlib.sha256(source_bytes).hexdigest() != SYSCONFIG_SOURCE_SHA256):
        raise ValueError("SYSCONFIG_SOURCE_DIGEST")
    tree = ast.parse(source_bytes.decode("utf-8"))
    assignments, functions = _top_level_names(tree)
    required_functions = (
        "_get_sysconfigdata_name", "get_config_var", "get_config_vars",
        "get_path", "get_path_names", "get_paths",
    )
    if "_INSTALL_SCHEMES" not in assignments \
            or not set(required_functions).issubset(functions):
        raise ValueError("SYSCONFIG_SOURCE_SYMBOLS")
    function_nodes = {
        node.name: node for node in tree.body
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
    }

    def function_without_docstring(function):
        body = list(function.body)
        if (body and isinstance(body[0], ast.Expr)
                and isinstance(body[0].value, ast.Constant)
                and type(body[0].value.value) is str):
            body.pop(0)
        fields = {name: getattr(function, name) for name in function._fields}
        fields["body"] = body
        normalized = type(function)(**fields)
        return ast.dump(normalized, include_attributes=False)

    expected_name_builder = ast.parse(
        "def _get_sysconfigdata_name():\n"
        "    multiarch = getattr(sys.implementation, '_multiarch', '')\n"
        "    return os.environ.get('_PYTHON_SYSCONFIGDATA_NAME', "
        "f'_sysconfigdata_{sys.abiflags}_{sys.platform}_{multiarch}')\n"
    ).body[0]
    expected_posix_init = ast.parse(
        "def _init_posix(vars):\n"
        "    name = _get_sysconfigdata_name()\n"
        "    _temp = __import__(name, globals(), locals(), ['build_time_vars'], 0)\n"
        "    build_time_vars = _temp.build_time_vars\n"
        "    vars.update(build_time_vars)\n"
    ).body[0]
    name_builder = function_nodes.get("_get_sysconfigdata_name")
    posix_init = function_nodes.get("_init_posix")
    if (name_builder is None or posix_init is None
            or function_without_docstring(name_builder)
            != function_without_docstring(expected_name_builder)):
        raise ValueError("SYSCONFIGDATA_NAME_SOURCE")
    if function_without_docstring(posix_init) != function_without_docstring(expected_posix_init):
        raise ValueError("SYSCONFIGDATA_IMPORT_SOURCE")
    scheme_assignment = next((node for node in tree.body
                              if isinstance(node, ast.Assign)
                              and any(isinstance(target, ast.Name)
                                      and target.id == "_INSTALL_SCHEMES"
                                      for target in node.targets)), None)
    if scheme_assignment is None:
        raise ValueError("SYSCONFIG_SCHEME_SOURCE")
    try:
        schemes = ast.literal_eval(scheme_assignment.value)
    except (ValueError, TypeError, SyntaxError) as error:
        raise ValueError("SYSCONFIG_SCHEME_LITERAL") from error
    if (type(schemes) is not dict or not schemes
            or any(type(name) is not str for name in schemes)
            or any(type(value) is not dict for value in schemes.values())):
        raise ValueError("SYSCONFIG_SCHEME_SHAPE")
    if any(type(key) is not str or type(value) is not str
           for scheme in schemes.values() for key, value in scheme.items()):
        raise ValueError("SYSCONFIG_SCHEME_PATHS")
    scheme_names = tuple(sorted(schemes))
    path_keys = tuple(sorted({key for value in schemes.values() for key in value}))
    template_rows = tuple(sorted(
        (scheme_name, key, template)
        for scheme_name, scheme in schemes.items()
        for key, template in scheme.items()
    ))
    scheme_digest = hashlib.sha256(
        "".join(name + "\n" for name in scheme_names).encode("ascii")
    ).hexdigest()
    path_digest = hashlib.sha256(
        "".join(name + "\n" for name in path_keys).encode("ascii")
    ).hexdigest()
    return {
        "source_sha256": SYSCONFIG_SOURCE_SHA256,
        "source_bytes": len(source_bytes),
        "scheme_count": len(scheme_names),
        "scheme_names": scheme_names,
        "scheme_names_sha256": scheme_digest,
        "path_key_count": len(path_keys),
        "path_keys": path_keys,
        "path_keys_sha256": path_digest,
        "path_template_row_count": len(template_rows),
        "path_templates_sha256": hashlib.sha256(
            "".join("\t".join(row) + "\n" for row in template_rows).encode("ascii")
        ).hexdigest(),
        "required_function_count": len(required_functions),
        "required_functions_sha256": hashlib.sha256(
            "".join(name + "\n" for name in required_functions).encode("ascii")
        ).hexdigest(),
        "sysconfigdata_override_key": "_PYTHON_SYSCONFIGDATA_NAME",
        "sysconfigdata_name_template": "_sysconfigdata_{sys.abiflags}_{sys.platform}_{multiarch}",
        "sysconfigdata_importer": "__import__",
        "sysconfigdata_imported_attribute": "build_time_vars",
        "sysconfigdata_initializer_parameter": "vars",
        "sysconfigdata_initializer_update_receiver": "vars",
        "sysconfigdata_initializer_update_value": "build_time_vars",
    }


def _class_method_names(tree):
    classes = {}
    for node in tree.body:
        if isinstance(node, ast.ClassDef):
            classes[node.name] = tuple(
                child.name for child in node.body
                if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef))
            )
    return classes


def _importlib_source_inventory(bootstrap_bytes, external_bytes):
    sources = (
        (bootstrap_bytes, IMPORTLIB_BOOTSTRAP_SOURCE_SHA256),
        (external_bytes, IMPORTLIB_EXTERNAL_SOURCE_SHA256),
    )
    trees = []
    for body, expected in sources:
        if (type(body) is not bytes or not body
                or len(body) > MAX_SOURCE_BYTES
                or hashlib.sha256(body).hexdigest() != expected):
            raise ValueError("IMPORTLIB_SOURCE_DIGEST")
        trees.append(ast.parse(body.decode("utf-8")))
    bootstrap_tree, external_tree = trees
    bootstrap_classes = _class_method_names(bootstrap_tree)
    external_classes = _class_method_names(external_tree)
    spec = next((node for node in bootstrap_tree.body
                 if isinstance(node, ast.ClassDef) and node.name == "ModuleSpec"), None)
    init = next((node for node in spec.body
                 if isinstance(node, ast.FunctionDef) and node.name == "__init__"), None) if spec else None
    if init is None:
        raise ValueError("IMPORTLIB_MODULE_SPEC_INIT")
    spec_fields = set()
    for node in ast.walk(init):
        if isinstance(node, ast.Assign):
            targets = node.targets
        elif isinstance(node, ast.AnnAssign):
            targets = (node.target,)
        else:
            continue
        for target in targets:
            if (isinstance(target, ast.Attribute) and isinstance(target.value, ast.Name)
                    and target.value.id == "self"):
                spec_fields.add(target.attr)
    required_spec_fields = {
        "name", "loader", "origin", "loader_state", "submodule_search_locations",
        "_uninitialized_submodules", "_set_fileattr", "_cached",
    }


    if spec_fields != required_spec_fields:
        raise ValueError("IMPORTLIB_MODULE_SPEC_FIELDS")
    required_bootstrap = {
        "BuiltinImporter", "FrozenImporter", "ModuleSpec",
    }
    required_external = {
        "SourceFileLoader", "SourcelessFileLoader", "ExtensionFileLoader",
        "NamespaceLoader", "PathFinder", "FileFinder",
    }
    if not required_bootstrap.issubset(bootstrap_classes) or not required_external.issubset(external_classes):
        raise ValueError("IMPORTLIB_FINDER_LOADER_CLASSES")
    required_methods = {
        "_find_spec", "_find_and_load", "_load_unlocked", "_init_module_attrs",
    }
    bootstrap_functions = {
        node.name for node in bootstrap_tree.body
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
    }
    if not required_methods.issubset(bootstrap_functions):
        raise ValueError("IMPORTLIB_BOOTSTRAP_METHODS")
    bootstrap_rows = tuple(sorted(
        (name, method) for name, methods in bootstrap_classes.items()
        for method in methods if name in required_bootstrap
    ))
    external_rows = tuple(sorted(
        (name, method) for name, methods in external_classes.items()
        for method in methods if name in required_external
    ))
    field_rows = tuple(sorted(spec_fields))
    canonical = lambda rows: "".join("\t".join(row) + "\n" if isinstance(row, tuple) else row + "\n" for row in rows).encode("ascii")
    return {
        "source_sha256": tuple(expected for _, expected in sources),
        "module_spec_field_count": len(field_rows),
        "module_spec_fields": field_rows,
        "module_spec_fields_sha256": hashlib.sha256(canonical(field_rows)).hexdigest(),
        "builtin_frozen_importer_count": len(required_bootstrap - {"ModuleSpec"}),
        "loader_finder_class_count": len(required_external),
        "bootstrap_method_count": len(required_methods),
        "bootstrap_methods_sha256": hashlib.sha256(canonical(tuple(sorted(required_methods)))).hexdigest(),
        "builtin_frozen_methods_sha256": hashlib.sha256(canonical(bootstrap_rows)).hexdigest(),
        "loader_finder_methods_sha256": hashlib.sha256(canonical(external_rows)).hexdigest(),
    }


def _importlib_public_api_inventory(machinery_bytes, util_bytes):
    sources = (
        ("machinery.py", machinery_bytes, IMPORTLIB_MACHINERY_SOURCE_SHA256),
        ("util.py", util_bytes, IMPORTLIB_UTIL_SOURCE_SHA256),
    )
    rows = []
    for filename, body, expected in sources:
        if (type(body) is not bytes or not body
                or hashlib.sha256(body).hexdigest() != expected):
            raise ValueError("IMPORTLIB_PUBLIC_API_DIGEST")
        tree = ast.parse(body.decode("utf-8"))
        for node in tree.body:
            if isinstance(node, ast.ImportFrom) and node.module:
                for item in node.names:
                    exported = item.asname or item.name
                    if not exported.startswith("_"):
                        rows.append((filename, exported, node.module, item.name))
            elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                if not node.name.startswith("_"):
                    rows.append((filename, node.name, "<local>", node.name))
    canonical_rows = tuple(sorted(rows))
    machinery_names = {row[1] for row in canonical_rows if row[0] == "machinery.py"}
    util_names = {row[1] for row in canonical_rows if row[0] == "util.py"}
    required_machinery = {
        "ModuleSpec", "BuiltinImporter", "FrozenImporter", "PathFinder",
        "FileFinder", "SourceFileLoader", "SourcelessFileLoader",
        "ExtensionFileLoader", "NamespaceLoader",
    }

    required_util = {
        "module_from_spec", "spec_from_loader", "find_spec",
        "spec_from_file_location", "LazyLoader",
    }
    if not required_machinery.issubset(machinery_names) or not required_util.issubset(util_names):
        raise ValueError("IMPORTLIB_PUBLIC_API_SYMBOLS")
    encoded = "".join("\t".join(row) + "\n" for row in canonical_rows).encode("ascii")
    return {
        "source_sha256": tuple(expected for _, _, expected in sources),
        "row_count": len(canonical_rows),
        "rows_sha256": hashlib.sha256(encoded).hexdigest(),
        "machinery_export_count": len(machinery_names),
        "util_export_count": len(util_names),
    }


def _target_importlib_finder_registration_candidate(files):
    """Bind importlib finder-registration sites, not the final runtime lists."""
    if type(files) is not dict:
        return None
    source_rows = (
        ("importlib/_bootstrap.py", IMPORTLIB_BOOTSTRAP_SOURCE_SHA256),
        ("importlib/_bootstrap_external.py", IMPORTLIB_EXTERNAL_SOURCE_SHA256),
    )
    trees = {}
    for path, digest in source_rows:
        source = files.get(path)
        if (type(source) is not bytes or not source
                or len(source) > MAX_SOURCE_BYTES
                or hashlib.sha256(source).hexdigest() != digest):
            return None
        try:
            trees[path] = ast.parse(source.decode("utf-8"), filename=path)
        except (UnicodeError, SyntaxError):
            return None

    def function(module_path, name):
        functions = [node for node in trees[module_path].body
                     if isinstance(node, ast.FunctionDef) and node.name == name]
        if len(functions) != 1:
            return None
        candidate = functions[0]
        if (candidate.body and isinstance(candidate.body[0], ast.Expr)
                and isinstance(candidate.body[0].value, ast.Constant)
                and type(candidate.body[0].value.value) is str):
            candidate.body = candidate.body[1:]
        return candidate

    expected_functions = {
        "importlib/_bootstrap.py": ast.parse(
            "def _install(sys_module, _imp_module):\n"
            "    _setup(sys_module, _imp_module)\n"
            "    sys.meta_path.append(BuiltinImporter)\n"
            "    sys.meta_path.append(FrozenImporter)\n"
        ).body[0],
        "importlib/_bootstrap_external.py": ast.parse(
            "def _install(_bootstrap_module):\n"
            "    _set_bootstrap_module(_bootstrap_module)\n"
            "    supported_loaders = _get_supported_file_loaders()\n"
            "    sys.path_hooks.extend([FileFinder.path_hook(*supported_loaders)])\n"
            "    sys.meta_path.append(PathFinder)\n"
        ).body[0],
    }
    module_order = {path: index for index, (path, _) in enumerate(source_rows)}
    observed_meta_path_calls = []
    for path, tree in trees.items():
        for node in ast.walk(tree):
            if (isinstance(node, ast.Call)
                    and isinstance(node.func, ast.Attribute)
                    and ast.unparse(node.func.value) == "sys.meta_path"):
                observed_meta_path_calls.append((
                    module_order[path], node.lineno, path, ast.unparse(node),
                ))
    observed_meta_path_calls = [
        (path, expression) for _, _, path, expression
        in sorted(observed_meta_path_calls)
    ]
    expected_meta_path_calls = [
        ("importlib/_bootstrap.py", "sys.meta_path.append(BuiltinImporter)"),
        ("importlib/_bootstrap.py", "sys.meta_path.append(FrozenImporter)"),
        ("importlib/_bootstrap_external.py", "sys.meta_path.append(PathFinder)"),
    ]
    actual_functions = {
        path: function(path, "_install") for path in expected_functions
    }
    if (observed_meta_path_calls != expected_meta_path_calls
            or any(actual_functions[path] is None
                   or ast.dump(actual_functions[path], include_attributes=False)
                   != ast.dump(expected, include_attributes=False)
                   for path, expected in expected_functions.items())):
        return None
    return {
        "source_sha256": [digest for _, digest in source_rows],
        "sys_meta_path_registration_sites": [
            ["importlib._bootstrap._install", "BuiltinImporter"],
            ["importlib._bootstrap._install", "FrozenImporter"],
            ["importlib._bootstrap_external._install", "PathFinder"],
        ],
        "file_path_hook_registration_site": [
            "importlib._bootstrap_external._install", "FileFinder.path_hook",
        ],
        "final_sys_meta_path_claimed": False,
        "final_sys_path_hooks_claimed": False,
        "evidence_scope": "STATIC_IMPORTLIB_REGISTRATION_SITES_CANDIDATE",
    }


def _target_meta_path_finder_class_candidate(files):
    """Bind meta_path labels to their declared classes and find_spec methods."""
    source_rows = (
        ("importlib/_bootstrap.py", IMPORTLIB_BOOTSTRAP_SOURCE_SHA256,
         ("BuiltinImporter", "FrozenImporter")),
        ("importlib/_bootstrap_external.py", IMPORTLIB_EXTERNAL_SOURCE_SHA256,
         ("PathFinder",)),
    )
    if type(files) is not dict:
        return None
    finders = []
    for path, digest, class_names in source_rows:
        source = files.get(path)
        if (type(source) is not bytes or not source or len(source) > MAX_SOURCE_BYTES
                or hashlib.sha256(source).hexdigest() != digest):
            return None
        try:
            tree = ast.parse(source.decode("utf-8"), filename=path)
        except (UnicodeError, SyntaxError):
            return None
        for class_name in class_names:
            classes = [
                node for node in tree.body
                if isinstance(node, ast.ClassDef) and node.name == class_name
            ]
            if len(classes) != 1 or classes[0].bases or classes[0].decorator_list:
                return None
            find_spec_methods = [
                node for node in classes[0].body
                if isinstance(node, ast.FunctionDef) and node.name == "find_spec"
            ]
            if (len(find_spec_methods) != 1
                    or len(find_spec_methods[0].decorator_list) != 1
                    or ast.unparse(find_spec_methods[0].decorator_list[0])
                    != "classmethod"):
                return None
            finders.append({
                "module": path.removesuffix(".py").replace("/", "."),
                "class": class_name,
                "method": "find_spec",
                "method_kind": "classmethod",
            })
    return {
        "source_sha256": [digest for _, digest, _ in source_rows],
        "registered_finder_declarations": finders,
        "runtime_instances_claimed": False,
        "selection_claimed": False,
        "evidence_scope": "STATIC_META_PATH_FINDER_CLASS_CANDIDATE",
    }


def _target_s15_finders_field_candidate(registration_candidate, class_candidate):
    """Join fixed finder registration sites to their declared class sources."""
    expected_sites = [
        ["importlib._bootstrap._install", "BuiltinImporter"],
        ["importlib._bootstrap._install", "FrozenImporter"],
        ["importlib._bootstrap_external._install", "PathFinder"],
    ]
    expected_declarations = [
        {"module": "importlib._bootstrap", "class": "BuiltinImporter",
         "method": "find_spec", "method_kind": "classmethod"},
        {"module": "importlib._bootstrap", "class": "FrozenImporter",
         "method": "find_spec", "method_kind": "classmethod"},
        {"module": "importlib._bootstrap_external", "class": "PathFinder",
         "method": "find_spec", "method_kind": "classmethod"},
    ]
    if (type(registration_candidate) is not dict
            or type(class_candidate) is not dict
            or registration_candidate.get("sys_meta_path_registration_sites")
            != expected_sites
            or registration_candidate.get("final_sys_meta_path_claimed") is not False
            or registration_candidate.get("evidence_scope")
            != "STATIC_IMPORTLIB_REGISTRATION_SITES_CANDIDATE"
            or type(registration_candidate.get("source_sha256")) is not list
            or registration_candidate.get("source_sha256")
            != class_candidate.get("source_sha256")
            or len(registration_candidate["source_sha256"]) != 2
            or class_candidate.get("registered_finder_declarations")
            != expected_declarations
            or class_candidate.get("runtime_instances_claimed") is not False
            or class_candidate.get("selection_claimed") is not False):
        return None
    return {
        "values": ("BUILTIN", "FROZEN", "PATH"),
        "registration_sites": expected_sites,
        "class_declarations": expected_declarations,
        "source_sha256": registration_candidate["source_sha256"],
        "runtime_finder_instances_claimed": False,
        "runtime_selection_claimed": False,
        "evidence_scope": "STATIC_S15_FINDERS_FIELD_CANDIDATE",
    }


def _target_zipimport_hook_registration_candidate(source_bytes):
    """Bind CPython's conditional zipimport hook insertion source route."""
    if (type(source_bytes) is not bytes or not source_bytes
            or len(source_bytes) > MAX_PYTHON_IMPORT_C_BYTES
            or hashlib.sha256(source_bytes).hexdigest() != PYTHON_IMPORT_C_SHA256):
        return None
    try:
        source = source_bytes.decode("utf-8")
    except UnicodeError:
        return None

    function_sources = (
        (
            "init_zipimport",
            re.compile(
                r"(?ms)^static int\ninit_zipimport\(PyThreadState \*tstate, "
                r"int verbose\)\n\{.*?^\}"
            ),
            """static int
init_zipimport(PyThreadState *tstate, int verbose)
{
    PyObject *path_hooks = _PySys_GetRequiredAttrString("path_hooks");
    if (path_hooks == NULL) {
        return -1;
    }

    if (verbose) {
        PySys_WriteStderr("# installing zipimport hook\\n");
    }

    PyObject *zipimporter = _PyImport_GetModuleAttrString("zipimport", "zipimporter");
    if (zipimporter == NULL) {
        _PyErr_Clear(tstate); /* No zipimporter object -- okay */
        if (verbose) {
            PySys_WriteStderr("# can't import zipimport.zipimporter\\n");
        }
    }
    else {
        /* sys.path_hooks.insert(0, zipimporter) */
        int err = PyList_Insert(path_hooks, 0, zipimporter);
        Py_DECREF(zipimporter);
        if (err < 0) {
            Py_DECREF(path_hooks);
            return -1;
        }
        if (verbose) {
            PySys_WriteStderr("# installed zipimport hook\\n");
        }
    }
    Py_DECREF(path_hooks);

    return 0;
}""",
        ),
        (
            "_PyImport_InitExternal",
            re.compile(
                r"(?ms)^PyStatus\n_PyImport_InitExternal\(PyThreadState \*tstate\)"
                r"\n\{.*?^\}"
            ),
            """PyStatus
_PyImport_InitExternal(PyThreadState *tstate)
{
    int verbose = _PyInterpreterState_GetConfig(tstate->interp)->verbose;

    // XXX Initialize here: sys.path_hooks and sys.path_importer_cache.

    if (init_importlib_external(tstate->interp) != 0) {
        _PyErr_Print(tstate);
        return _PyStatus_ERR("external importer setup failed");
    }

    if (init_zipimport(tstate, verbose) != 0) {
        PyErr_Print();
        return _PyStatus_ERR("initializing zipimport failed");
    }

    return _PyStatus_OK();
}""",
        ),
    )
    for _, pattern, expected in function_sources:
        matches = pattern.findall(source)
        if len(matches) != 1 or matches[0] != expected:
            return None
    return {
        "source_sha256": PYTHON_IMPORT_C_SHA256,
        "zipimporter_attribute_source": (
            "_PyImport_GetModuleAttrString(zipimport, zipimporter)"
        ),
        "registration_operation": "PyList_Insert(path_hooks, 0, zipimporter)",
        "registration_conditional_on_attribute": True,
        "missing_attribute_skips_registration": True,
        "insertion_error_returns_failure": True,
        "external_importlib_setup_precedes_zipimport_attempt": True,
        "final_sys_path_hooks_claimed": False,
        "evidence_scope": "STATIC_CONDITIONAL_ZIPIMPORT_HOOK_CANDIDATE",
    }


def _target_filefinder_hook_factory_candidate(files):
    """Bind FileFinder's declared loader tuple and directory-hook factory."""
    path = "importlib/_bootstrap_external.py"
    source = files.get(path) if type(files) is dict else None
    if (type(source) is not bytes or not source or len(source) > MAX_SOURCE_BYTES
            or hashlib.sha256(source).hexdigest()
            != IMPORTLIB_EXTERNAL_SOURCE_SHA256):
        return None
    try:
        tree = ast.parse(source.decode("utf-8"), filename=path)
    except (UnicodeError, SyntaxError):
        return None

    def without_docstring(function_node):
        if (function_node.body and isinstance(function_node.body[0], ast.Expr)
                and isinstance(function_node.body[0].value, ast.Constant)
                and type(function_node.body[0].value.value) is str):
            function_node.body = function_node.body[1:]
        return function_node

    supported_functions = [
        node for node in tree.body
        if isinstance(node, ast.FunctionDef)
        and node.name == "_get_supported_file_loaders"
    ]
    finder_classes = [
        node for node in tree.body
        if isinstance(node, ast.ClassDef) and node.name == "FileFinder"
    ]
    path_hook_methods = [
        node for node in finder_classes[0].body
        if isinstance(node, ast.FunctionDef) and node.name == "path_hook"
    ] if len(finder_classes) == 1 else []
    if len(supported_functions) != 1 or len(path_hook_methods) != 1:
        return None

    expected_supported = ast.parse(
        "def _get_supported_file_loaders():\n"
        "    extensions = ExtensionFileLoader, _imp.extension_suffixes()\n"
        "    source = SourceFileLoader, SOURCE_SUFFIXES\n"
        "    bytecode = SourcelessFileLoader, BYTECODE_SUFFIXES\n"
        "    return [extensions, source, bytecode]\n"
    ).body[0]
    expected_path_hook = ast.parse(
        "class FileFinder:\n"
        "    @classmethod\n"
        "    def path_hook(cls, *loader_details):\n"
        "        def path_hook_for_FileFinder(path):\n"
        "            'Path hook for importlib.machinery.FileFinder.'\n"
        "            if not _path_isdir(path):\n"
        "                raise ImportError('only directories are supported', path=path)\n"
        "            return cls(path, *loader_details)\n"
        "        return path_hook_for_FileFinder\n"
    ).body[0].body[0]
    if (ast.dump(without_docstring(supported_functions[0]), include_attributes=False)
            != ast.dump(expected_supported, include_attributes=False)
            or ast.dump(without_docstring(path_hook_methods[0]), include_attributes=False)
            != ast.dump(expected_path_hook, include_attributes=False)):
        return None
    return {
        "source_sha256": IMPORTLIB_EXTERNAL_SOURCE_SHA256,
        "path_hook_factory": "FileFinder.path_hook",
        "path_hook_classmethod": True,
        "supported_loader_detail_order": [
            "ExtensionFileLoader", "SourceFileLoader", "SourcelessFileLoader",
        ],
        "returned_hook": "path_hook_for_FileFinder",
        "directory_guard": "_path_isdir(path)",
        "non_directory_result": "ImportError(path=path)",
        "finder_constructor": "FileFinder(path, *loader_details)",
        "evidence_scope": "STATIC_FILEFINDER_HOOK_FACTORY_CANDIDATE",
    }


def _target_zipimporter_class_source_candidate(files):
    """Bind zipimport.zipimporter to its digest-checked class declaration."""
    source = files.get("zipimport.py") if type(files) is dict else None
    if (type(source) is not bytes or not source or len(source) > MAX_SOURCE_BYTES
            or hashlib.sha256(source).hexdigest() != ZIPIMPORT_SOURCE_SHA256):
        return None
    try:
        tree = ast.parse(source.decode("utf-8"), filename="zipimport.py")
    except (UnicodeError, SyntaxError):
        return None
    classes = [
        node for node in tree.body
        if isinstance(node, ast.ClassDef) and node.name == "zipimporter"
    ]
    exports = [
        node.value for node in tree.body
        if isinstance(node, ast.Assign)
        and any(isinstance(target, ast.Name) and target.id == "__all__"
                for target in node.targets)
    ]
    if (len(classes) != 1 or len(exports) != 1
            or len(classes[0].bases) != 1
            or ast.unparse(classes[0].bases[0])
            != "_bootstrap_external._LoaderBasics"
            or classes[0].decorator_list
            or not isinstance(exports[0], ast.List)
            or any(not isinstance(item, ast.Constant)
                   or type(item.value) is not str for item in exports[0].elts)
            or [item.value for item in exports[0].elts]
            != ["ZipImportError", "zipimporter"]):
        return None
    return {
        "source_sha256": ZIPIMPORT_SOURCE_SHA256,
        "module": "zipimport",
        "requested_attribute": "zipimporter",
        "class_base": "_bootstrap_external._LoaderBasics",
        "listed_in_all": True,
        "runtime_imported": False,
        "evidence_scope": "STATIC_ZIPIMPORTER_CLASS_DECLARATION_CANDIDATE",
    }


def _target_s15_hooks_field_candidate(
        importlib_registration, zipimport_registration,
        filefinder_factory, zipimporter_class):
    """Join hook registration and factory/class sources into an S15 candidate."""
    if (type(importlib_registration) is not dict
            or importlib_registration.get("file_path_hook_registration_site")
            != ["importlib._bootstrap_external._install", "FileFinder.path_hook"]
            or importlib_registration.get("final_sys_path_hooks_claimed") is not False
            or importlib_registration.get("source_sha256") != [
                IMPORTLIB_BOOTSTRAP_SOURCE_SHA256,
                IMPORTLIB_EXTERNAL_SOURCE_SHA256,
            ]
            or type(zipimport_registration) is not dict
            or zipimport_registration.get("registration_operation")
            != "PyList_Insert(path_hooks, 0, zipimporter)"
            or zipimport_registration.get("registration_conditional_on_attribute")
            is not True
            or zipimport_registration.get("missing_attribute_skips_registration")
            is not True
            or zipimport_registration.get("external_importlib_setup_precedes_zipimport_attempt")
            is not True
            or zipimport_registration.get("final_sys_path_hooks_claimed") is not False
            or zipimport_registration.get("source_sha256") != PYTHON_IMPORT_C_SHA256
            or type(filefinder_factory) is not dict
            or filefinder_factory.get("source_sha256")
            != IMPORTLIB_EXTERNAL_SOURCE_SHA256
            or filefinder_factory.get("path_hook_factory") != "FileFinder.path_hook"
            or filefinder_factory.get("returned_hook") != "path_hook_for_FileFinder"
            or filefinder_factory.get("supported_loader_detail_order") != [
                "ExtensionFileLoader", "SourceFileLoader", "SourcelessFileLoader",
            ]
            or filefinder_factory.get("evidence_scope")
            != "STATIC_FILEFINDER_HOOK_FACTORY_CANDIDATE"
            or type(zipimporter_class) is not dict
            or zipimporter_class.get("source_sha256") != ZIPIMPORT_SOURCE_SHA256
            or zipimporter_class.get("module") != "zipimport"
            or zipimporter_class.get("requested_attribute") != "zipimporter"
            or zipimporter_class.get("listed_in_all") is not True
            or zipimporter_class.get("runtime_imported") is not False
            or zipimporter_class.get("evidence_scope")
            != "STATIC_ZIPIMPORTER_CLASS_DECLARATION_CANDIDATE"):
        return None
    return {
        "values": ("ZIPIMPORTER", "FILEFINDER"),
        "registration_order_basis": (
            "FileFinder appended during external importlib setup",
            "zipimporter inserted at index zero after that setup",
        ),
        "registration_source_sha256": {
            "importlib": importlib_registration["source_sha256"],
            "zipimport": zipimport_registration["source_sha256"],
        },
        "factory_source_sha256": filefinder_factory["source_sha256"],
        "class_source_sha256": zipimporter_class["source_sha256"],
        "runtime_hook_objects_claimed": False,
        "final_sys_path_hooks_claimed": False,
        "evidence_scope": "STATIC_S15_HOOKS_FIELD_CANDIDATE",
    }


def _target_s15_assumption_field_candidate(source_bytes):
    """Bind the fixed S15 assumption text without claiming attestation."""
    if (type(source_bytes) is not bytes or not source_bytes
            or len(source_bytes) > MAX_DGN007_RUNTIME_PROFILE_SOURCE_BYTES
            or _normalized_profile_source_sha256(source_bytes)
            != DGN007_RUNTIME_PROFILE_SOURCE_SHA256):
        return None
    try:
        tree = ast.parse(source_bytes.decode("utf-8"))
    except (UnicodeError, SyntaxError):
        return None
    assignments = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            assignments.extend(
                target for target in node.targets
                if isinstance(target, ast.Name) and target.id == "ASSUMPTION"
            )
        elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
            if node.target.id == "ASSUMPTION":
                assignments.append(node.target)
    top_level = [
        node for node in tree.body if isinstance(node, ast.Assign)
        and any(isinstance(target, ast.Name) and target.id == "ASSUMPTION"
                for target in node.targets)
    ]
    if (len(assignments) != 1 or len(top_level) != 1
            or len(top_level[0].targets) != 1
            or not isinstance(top_level[0].value, ast.Constant)
            or type(top_level[0].value.value) is not str
            or top_level[0].value.value != "DECLARED_SETUP_PYTHON_CONTROL_RUNTIME"):
        return None
    return {
        "value": top_level[0].value.value,
        "source_path": "Tests/Tools/dgn007_import_runtime_profile.py",
        "source_sha256": DGN007_RUNTIME_PROFILE_SOURCE_SHA256,
        "runtime_assumption_attested": False,
        "evidence_scope": "STATIC_S15_ASSUMPTION_FIELD_CANDIDATE",
    }


def _target_s15_installation_schema_candidate(source_bytes):
    """Bind S15 field order to the pinned runtime profile shape validator."""
    if (type(source_bytes) is not bytes or not source_bytes
            or len(source_bytes) > MAX_DGN007_RUNTIME_PROFILE_SOURCE_BYTES
            or _normalized_profile_source_sha256(source_bytes)
            != DGN007_RUNTIME_PROFILE_SOURCE_SHA256):
        return None
    functions = re.findall(
        rb"(?ms)^def _selected_shapes\([^\n]*\):\r?\n(?P<body>.*?)(?=^def |\Z)",
        source_bytes,
    )
    expected_fields = (
        "assumption", "platform", "implementation", "version", "exe",
        "target", "prefixes", "abi", "paths", "roots", "inert", "flags",
        "finders", "hooks", "files",
    )
    if len(functions) != 1:
        return None
    assignments = re.findall(
        rb"(?m)^\s*([a-z_]+(?:\s*,\s*[a-z_]+){14})\s*=\s*installation\s*$",
        functions[0],
    )
    tuple_checks = re.findall(
        rb"_selected_tuple\(\s*installation\s*,\s*15\s*\)", functions[0],
    )
    actual_fields = tuple(
        item.strip().decode("ascii") for item in assignments[0].split(b",")
    ) if len(assignments) == 1 else ()
    if actual_fields != expected_fields or len(tuple_checks) != 1:
        return None
    return {
        "field_order": (
            "assumption", "platform", "implementation", "version",
            "executable", "executable_target", "prefixes", "abi", "paths",
            "roots", "inert_zip", "flags", "finders", "hooks", "files",
        ),
        "tuple_length": 15,
        "source_path": "Tests/Tools/dgn007_import_runtime_profile.py",
        "source_sha256": DGN007_RUNTIME_PROFILE_SOURCE_SHA256,
        "runtime_schema_claimed": False,
        "evidence_scope": "STATIC_S15_INSTALLATION_SCHEMA_CANDIDATE",
    }


def _normalized_profile_source_sha256(source_bytes):
    """Hash source text with Git-independent LF line endings."""
    return hashlib.sha256(source_bytes.replace(b"\r\n", b"\n")).hexdigest()


def _target_controls_selection_contract_candidate(source_bytes):
    """Bind allowed control names and module-row correspondence to source."""
    if (type(source_bytes) is not bytes or not source_bytes
            or len(source_bytes) > MAX_DGN007_RUNTIME_PROFILE_SOURCE_BYTES
            or _normalized_profile_source_sha256(source_bytes)
            != DGN007_RUNTIME_PROFILE_SOURCE_SHA256):
        return None
    bodies = re.findall(
        rb"(?ms)^def _selected_shapes\([^\n]*\):\r?\n(?P<body>.*?)(?=^def |\Z)",
        source_bytes,
    )
    if len(bodies) != 1:
        return None
    normalized = re.sub(rb"\s+", b" ", bodies[0])
    required_fragments = (
        b"len(controls) <= 2 and len(set(controls)) == len(controls)",
        b'all(name in ("__main__", "dgn007_import_runtime_profile") '
        b"for name in controls)",
        b'set(controls) == {row[0] for row in modules '
        b'if row[5] == "CONTROL"}',
    )
    if any(normalized.count(fragment) != 1 for fragment in required_fragments):
        return None
    return {
        "allowed_names": ("__main__", "dgn007_import_runtime_profile"),
        "maximum_count": 2,
        "unique_names_required": True,
        "must_equal_control_module_rows": True,
        "source_path": "Tests/Tools/dgn007_import_runtime_profile.py",
        "source_sha256": DGN007_RUNTIME_PROFILE_SOURCE_SHA256,
        "selected_controls_claimed": False,
        "evidence_scope": "STATIC_PROFILE_CONTROLS_SELECTION_CONTRACT_CANDIDATE",
    }


def _target_profile_selection_inputs_candidate(
        source_bytes, assumption, roots, inert_zip, controls_contract):
    """Join fixed selection fields and control constraints without a selection."""
    if (type(source_bytes) is not bytes or not source_bytes
            or len(source_bytes) > MAX_DGN007_RUNTIME_PROFILE_SOURCE_BYTES
            or _normalized_profile_source_sha256(source_bytes)
            != DGN007_RUNTIME_PROFILE_SOURCE_SHA256
            or type(assumption) is not dict
            or assumption.get("value") != "DECLARED_SETUP_PYTHON_CONTROL_RUNTIME"
            or assumption.get("source_sha256") != DGN007_RUNTIME_PROFILE_SOURCE_SHA256
            or assumption.get("runtime_assumption_attested") is not False
            or type(roots) is not dict
            or roots.get("value") != (
                "/usr/local/lib/python3.12",
                "/usr/local/lib/python3.12/lib-dynload",
            )
            or roots.get("runtime_roots_claimed") is not False
            or type(inert_zip) is not dict
            or inert_zip.get("value") != "/usr/local/lib/python312.zip"
            or inert_zip.get("runtime_membership_claimed") is not False
            or type(controls_contract) is not dict
            or controls_contract.get("source_sha256")
            != DGN007_RUNTIME_PROFILE_SOURCE_SHA256
            or controls_contract.get("selected_controls_claimed") is not False
            or controls_contract.get("allowed_names")
            != ("__main__", "dgn007_import_runtime_profile")):
        return None
    bodies = re.findall(
        rb"(?ms)^def _project_scalars\([^\n]*\):\r?\n(?P<body>.*?)(?=^def |\Z)",
        source_bytes,
    )
    if len(bodies) != 1:
        return None
    normalized = re.sub(rb"\s+", b" ", bodies[0])
    assignment = (
        b"selection = (expected.assumption, expected.roots, "
        b"expected.inert_zip, expected.controls)"
    )
    if normalized.count(assignment) != 1:
        return None
    return {
        "field_order": ("assumption", "roots", "inert_zip", "controls"),
        "fixed_values": (assumption["value"], roots["value"], inert_zip["value"]),
        "controls_contract": controls_contract["allowed_names"],
        "controls_maximum_count": controls_contract["maximum_count"],
        "controls_must_equal_control_module_rows": (
            controls_contract["must_equal_control_module_rows"]
        ),
        "source_path": "Tests/Tools/dgn007_import_runtime_profile.py",
        "source_sha256": DGN007_RUNTIME_PROFILE_SOURCE_SHA256,
        "selection_tuple_claimed": False,
        "selected_controls_claimed": False,
        "evidence_scope": "STATIC_PROFILE_SELECTION_INPUT_CONTRACT_CANDIDATE",
    }


def _target_profile_scalar_projection_schema_candidate(
        source_bytes, selection_inputs, installation_tuple):
    """Bind the three ordered scalar-projection outputs to existing candidates."""
    if (type(source_bytes) is not bytes or not source_bytes
            or len(source_bytes) > MAX_DGN007_RUNTIME_PROFILE_SOURCE_BYTES
            or _normalized_profile_source_sha256(source_bytes)
            != DGN007_RUNTIME_PROFILE_SOURCE_SHA256
            or type(selection_inputs) is not dict
            or selection_inputs.get("field_order")
            != ("assumption", "roots", "inert_zip", "controls")
            or selection_inputs.get("selection_tuple_claimed") is not False
            or type(installation_tuple) is not dict
            or installation_tuple.get("field_order") is None
            or installation_tuple.get("runtime_record_claimed") is not False):
        return None
    bodies = re.findall(
        rb"(?ms)^def _project_scalars\([^\n]*\):\r?\n(?P<body>.*?)(?=^def |\Z)",
        source_bytes,
    )
    if len(bodies) != 1:
        return None
    normalized = re.sub(rb"\s+", b" ", bodies[0])
    required = (
        b"selection = (expected.assumption, expected.roots, expected.inert_zip, expected.controls)",
        b"installation = (observation.platform, observation.implementation, observation.version, observation.executable, observation.executable_target, observation.prefixes, observation.abi, observation.flags, observation.paths, (\"BUILTIN\", \"FROZEN\", \"PATH\"), (\"ZIPIMPORTER\", \"FILEFINDER\"), tuple((r.path, r.size, r.sha256) for r in observation.files))",
        b"modules.append((row.name, module_name, spec_name, row.origin, row.file, row.kind, row.locations, loader, loader_name, loader_path, aliases))",
        b"return selection, installation, tuple(modules)",
    )
    if any(normalized.count(fragment) != 1 for fragment in required):
        return None
    return {
        "output_order": ("selection", "installation", "modules"),
        "selection_field_order": selection_inputs["field_order"],
        "declared_profile_installation_field_order": installation_tuple["field_order"],
        "installation_projection_field_order": (
            "platform", "implementation", "version", "executable",
            "executable_target", "prefixes", "abi", "flags", "paths",
            "finders", "hooks", "files",
        ),
        "module_row_field_order": (
            "name", "module_name", "spec_name", "origin", "file", "kind",
            "locations", "loader", "loader_name", "loader_path", "aliases",
        ),
        "source_path": "Tests/Tools/dgn007_import_runtime_profile.py",
        "source_sha256": DGN007_RUNTIME_PROFILE_SOURCE_SHA256,
        "projected_values_claimed": False,
        "runtime_projection_claimed": False,
        "evidence_scope": "STATIC_PROFILE_SCALAR_PROJECTION_SCHEMA_CANDIDATE",
    }


def _target_selected_profile_shape_contract_candidate(
        source_bytes, installation_schema, controls_contract):
    """Bind bounded selected-profile shape checks without claiming a selection."""
    if (type(source_bytes) is not bytes or not source_bytes
            or len(source_bytes) > MAX_DGN007_RUNTIME_PROFILE_SOURCE_BYTES
            or _normalized_profile_source_sha256(source_bytes)
            != DGN007_RUNTIME_PROFILE_SOURCE_SHA256
            or type(installation_schema) is not dict
            or installation_schema.get("tuple_length") != 15
            or installation_schema.get("runtime_schema_claimed") is not False
            or type(controls_contract) is not dict
            or controls_contract.get("maximum_count") != 2
            or controls_contract.get("selected_controls_claimed") is not False):
        return None
    bodies = re.findall(
        rb"(?ms)^def _selected_shapes\([^\n]*\):\r?\n(?P<body>.*?)(?=^def |\Z)",
        source_bytes,
    )
    if len(bodies) != 1:
        return None
    normalized = re.sub(rb"\s+", b" ", bodies[0])
    required = (
        b"_selected_tree((installation, controls, modules))",
        b"_need(type(token) is bytes and len(token) == 32, \"SELECTION_FORM\")",
        b"_selected_tuple(installation, 15)",
        b"_selected_tuple(row, 11)",
        b"len(controls) <= 2 and len(set(controls)) == len(controls)",
        b"names == tuple(sorted(set(names)))",
        b"set(controls) == {row[0] for row in modules if row[5] == \"CONTROL\"}",
    )
    if any(normalized.count(fragment) != 1 for fragment in required):
        return None
    if not (normalized.index(required[0]) < normalized.index(required[1])
            < normalized.index(required[2])):
        return None
    return {
        "installation_arity": 15,
        "module_row_arity": 11,
        "token_bytes": 32,
        "maximum_controls": controls_contract["maximum_count"],
        "control_names_unique": True,
        "module_names_sorted_unique": True,
        "controls_equal_control_rows": True,
        "source_path": "Tests/Tools/dgn007_import_runtime_profile.py",
        "source_sha256": DGN007_RUNTIME_PROFILE_SOURCE_SHA256,
        "selected_values_claimed": False,
        "profile_bound_claimed": False,
        "evidence_scope": "STATIC_SELECTED_PROFILE_SHAPE_CONTRACT_CANDIDATE",
    }


def _target_selected_profile_binder_flow_candidate(source_bytes, shape_contract):
    """Bind the shape-first selected-profile binder flow and report mapping."""
    if (type(source_bytes) is not bytes or not source_bytes
            or len(source_bytes) > MAX_DGN007_RUNTIME_PROFILE_SOURCE_BYTES
            or _normalized_profile_source_sha256(source_bytes)
            != DGN007_RUNTIME_PROFILE_SOURCE_SHA256
            or type(shape_contract) is not dict
            or shape_contract.get("profile_bound_claimed") is not False):
        return None
    bodies = re.findall(
        rb"(?ms)^def bind_selected_profile\([^\n]*\):\r?\n(?P<body>.*?)(?=^@dataclass|^def |\Z)",
        source_bytes,
    )
    if len(bodies) != 1:
        return None
    normalized = re.sub(rb"\s+", b" ", bodies[0])
    required = (
        b"fingerprints = _selected_shapes(installation, controls, modules, token)",
        b"expected, _ = _bind_selected(installation, controls, modules, token, cache, finders, hooks, fingerprints, [0])",
        b"except _Failure as error: return BoundProfileResult(ProfileReport(\"REJECTED_SELECTED_PROFILE\", str(error)))",
        b"except (AttributeError, TypeError, ValueError, UnicodeError): return BoundProfileResult(ProfileReport(\"REJECTED_SELECTED_PROFILE\", \"PROFILE_BINDING_FAILED\"))",
        b"return BoundProfileResult(ProfileReport(\"BOUND_SELECTED_PROFILE\", \"NONE\", True), expected)",
    )
    if (any(normalized.count(fragment) != 1 for fragment in required)
            or len(re.findall(rb"\breturn\b", normalized)) != 3):
        return None
    if not (normalized.index(required[0]) < normalized.index(required[1])
            < normalized.index(required[2]) < normalized.index(required[3])
            < normalized.index(required[4])):
        return None
    if any(token in normalized for token in (
            b"observe_current_interpreter", b"open(", b"subprocess", b"Popen(")):
        return None
    return {
        "validation_order": ("selected_shapes", "bind_selected"),
        "failure_reports": ("REJECTED_SELECTED_PROFILE", "PROFILE_BINDING_FAILED"),
        "success_report": "BOUND_SELECTED_PROFILE",
        "success_requires_expected_profile": True,
        "source_path": "Tests/Tools/dgn007_import_runtime_profile.py",
        "source_sha256": DGN007_RUNTIME_PROFILE_SOURCE_SHA256,
        "profile_binding_claimed": False,
        "runtime_observation_claimed": False,
        "evidence_scope": "STATIC_SELECTED_PROFILE_BINDER_FLOW_CANDIDATE",
    }


def _target_selected_profile_anchor_binding_candidate(source_bytes, binder_flow):
    """Bind module-row projection and repeated local-anchor checks in binder."""
    if (type(source_bytes) is not bytes or not source_bytes
            or len(source_bytes) > MAX_DGN007_RUNTIME_PROFILE_SOURCE_BYTES
            or _normalized_profile_source_sha256(source_bytes)
            != DGN007_RUNTIME_PROFILE_SOURCE_SHA256
            or type(binder_flow) is not dict
            or binder_flow.get("profile_binding_claimed") is not False):
        return None
    bodies = re.findall(
        rb"(?ms)^def _bind_selected\(.*?\):\r?\n(?P<body>.*?)(?=^def |\Z)",
        source_bytes,
    )
    if len(bodies) != 1:
        return None
    normalized = re.sub(rb"\s+", b" ", bodies[0])
    required = (
        b"_selected_cache(cache, names, keys)",
        b"held, rows = cache.copy(), []",
        b"rows.append(ModuleRecord(row[0], row[3], row[4], row[5], row[6], module, spec, loader))",
        b"expected = DeclaredProfile(s[0], token, s[2], s[3], s[4], s[5], s[6], s[7], s[8], s[9], s[10], controls, finders, hooks, tuple(rows), fingerprints)",
        b"_shape(expected, True)",
        b"_need(_project_scalars(expected, observation)[2] == modules, \"MODULE_MISMATCH\")",
        b"_need(all(cache[name] is held[name] for name in names), \"CACHE_MISMATCH\")",
        b"return expected, observation",
    )
    if (any(normalized.count(fragment) != (
                2 if fragment in (required[0], required[4], required[5]) else 1)
            for fragment in required)
            or len(re.findall(rb"\breturn\b", normalized)) != 1):
        return None
    if normalized.index(required[0]) > normalized.index(required[1]):
        return None
    if not (normalized.index(required[2]) < normalized.index(required[3])
            < normalized.index(required[4]) < normalized.index(required[5])
            < normalized.index(required[6]) < normalized.index(required[7])):
        return None
    return {
        "cache_copy_before_module_rows": True,
        "module_row_anchor_fields": (
            "name", "origin", "file", "kind", "locations", "module", "spec", "loader",
        ),
        "module_projection_equality_checks": 2,
        "profile_shape_checks": 2,
        "cache_anchor_identity_rechecked": True,
        "source_path": "Tests/Tools/dgn007_import_runtime_profile.py",
        "source_sha256": DGN007_RUNTIME_PROFILE_SOURCE_SHA256,
        "anchor_binding_claimed": False,
        "runtime_observation_claimed": False,
        "evidence_scope": "STATIC_SELECTED_PROFILE_ANCHOR_BINDING_CANDIDATE",
    }


def _target_selected_profile_observation_flow_candidate(source_bytes, anchor_binding):
    """Bind selected observation ordering and reports without making a runtime claim."""
    if (type(source_bytes) is not bytes or not source_bytes
            or len(source_bytes) > MAX_DGN007_RUNTIME_PROFILE_SOURCE_BYTES
            or _normalized_profile_source_sha256(source_bytes)
            != DGN007_RUNTIME_PROFILE_SOURCE_SHA256
            or type(anchor_binding) is not dict
            or anchor_binding.get("anchor_binding_claimed") is not False):
        return None
    bodies = re.findall(
        rb"(?ms)^def observe_selected_profile_scalars\(.*?\):\r?\n(?P<body>.*?)(?=^def |\Z)",
        source_bytes,
    )
    if len(bodies) != 1:
        return None
    normalized = re.sub(rb"\s+", b" ", bodies[0])
    required = (
        b"fingerprints = _selected_shapes(installation, controls, modules, token)",
        b"expected, held = _bind_selected(installation, controls, modules, token, cache, tuple(finders), tuple(hooks), fingerprints, keys)",
        b"_selected_post(expected, runtime, cache, finders, hooks, providers)",
        b"actual = observe_current_interpreter_scalars(expected, separately_known_filefinder_hook)",
        b"selected = ((s[0], s[9], s[10], controls), (s[1], s[2], s[3], s[4], s[5], s[6], s[7], s[11], s[8], s[12], s[13], s[14]), modules)",
        b"_need(actual.scalars == selected, \"PROFILE_MISMATCH\")",
        b"_selected_post(expected, runtime, cache, finders, hooks, providers)",
        b"final = _capture(expected, expected.files)",
        b"_need(_project_scalars(expected, final) == selected, \"PROFILE_MISMATCH\")",
        b"_selected_hook_post(hook, _filefinder_hook(final, separately_known_filefinder_hook))",
        b"_selected_post(expected, runtime, cache, finders, hooks, providers)",
        b"return SelectedScalarObservationResult( ProfileReport(\"MATCHED_SELECTED_PROFILE\", \"NONE\", True), expected, actual.scalars)",
        b"except Exception:",
        b"return SelectedScalarObservationResult( ProfileReport(\"REJECTED_SELECTED_OBSERVATION\", \"SELECTED_OBSERVATION_FAILED\"))",
    )
    post_check = required[2]
    if (any(normalized.count(fragment) != 1 for fragment in required if fragment != post_check)
            or normalized.count(post_check) != 3
            or len(re.findall(rb"\breturn\b", normalized)) != 2):
        return None
    positions = []
    cursor = 0
    for fragment in required[:12]:
        position = normalized.find(fragment, cursor)
        if position < 0:
            return None
        positions.append(position)
        cursor = position + len(fragment)
    if positions != sorted(positions):
        return None
    if normalized.index(required[12]) > normalized.index(required[13]):
        return None
    return {
        "validation_order": (
            "selected_shapes", "bind_selected", "observe_current_scalars",
            "compare_selected_projection", "capture_and_compare_final",
            "recheck_hooks", "recheck_selected_postconditions",
        ),
        "matched_report": "MATCHED_SELECTED_PROFILE",
        "rejected_report": "REJECTED_SELECTED_OBSERVATION",
        "selected_profile_observation_claimed": False,
        "runtime_observation_claimed": False,
        "source_path": "Tests/Tools/dgn007_import_runtime_profile.py",
        "source_sha256": DGN007_RUNTIME_PROFILE_SOURCE_SHA256,
        "evidence_scope": "STATIC_SELECTED_PROFILE_OBSERVATION_FLOW_CANDIDATE",
    }


def _target_current_scalar_observation_flow_candidate(source_bytes, projection_schema):
    """Bind the current scalar observer's record, hook, projection and report flow."""
    if (type(source_bytes) is not bytes or not source_bytes
            or len(source_bytes) > MAX_DGN007_RUNTIME_PROFILE_SOURCE_BYTES
            or _normalized_profile_source_sha256(source_bytes)
            != DGN007_RUNTIME_PROFILE_SOURCE_SHA256
            or type(projection_schema) is not dict
            or projection_schema.get("runtime_projection_claimed") is not False):
        return None
    bodies = re.findall(
        rb"(?ms)^def observe_current_interpreter_scalars\([^\n]*,\r?\n[^\n]*\)[^\n]*:\r?\n(?P<body>.*?)(?=^@dataclass|^def |\Z)",
        source_bytes,
    )
    if len(bodies) != 1:
        return None
    normalized = re.sub(rb"\s+", b" ", bodies[0])
    required = (
        b"records = observe_current_interpreter_records(expected)",
        b"if records.observation is None: return ScalarObservationResult(records.report)",
        b"_compare(expected, observation)",
        b"hook = _filefinder_hook(observation, separately_known_filefinder_hook)",
        b"scalars = _project_scalars(expected, observation)",
        b"after_hook = _filefinder_hook(observation, separately_known_filefinder_hook)",
        b"return ScalarObservationResult(records.report, scalars)",
    )
    if any(normalized.count(fragment) != (2 if fragment in (required[2], required[3]) else 1)
           for fragment in required):
        return None
    if len(re.findall(rb"\breturn\b", normalized)) != 4:
        return None
    if not (normalized.index(required[0]) < normalized.index(required[1])
            < normalized.index(required[2]) < normalized.index(required[3])
            < normalized.index(required[4]) < normalized.rindex(required[2])
            < normalized.index(required[5]) < normalized.index(required[6])):
        return None
    if b"except _Failure as error: return ScalarObservationResult(ProfileReport(\"REJECTED_PROFILE\", str(error)))" not in normalized:
        return None
    return {
        "fresh_records_required": True,
        "profile_comparisons": 2,
        "filefinder_hook_observations": 2,
        "scalar_projection_returned_only_after_checks": True,
        "rejected_status": "REJECTED_PROFILE",
        "source_path": "Tests/Tools/dgn007_import_runtime_profile.py",
        "source_sha256": DGN007_RUNTIME_PROFILE_SOURCE_SHA256,
        "runtime_observation_claimed": False,
        "evidence_scope": "STATIC_CURRENT_SCALAR_OBSERVATION_FLOW_CANDIDATE",
    }


def _target_fresh_record_capture_flow_candidate(source_bytes):
    """Bind current record capture bracketing, bounded hashing and success-only return."""
    if (type(source_bytes) is not bytes or not source_bytes
            or len(source_bytes) > MAX_DGN007_RUNTIME_PROFILE_SOURCE_BYTES
            or _normalized_profile_source_sha256(source_bytes)
            != DGN007_RUNTIME_PROFILE_SOURCE_SHA256):
        return None
    bodies = re.findall(
        rb"(?ms)^def observe_current_interpreter_records\([^\n]*\)[^\n]*:\r?\n(?P<body>.*?)(?=^def |\Z)",
        source_bytes,
    )
    if len(bodies) != 1:
        return None
    normalized = re.sub(rb"\s+", b" ", bodies[0])
    required = (
        b"before = _capture(expected, expected.files)",
        b"_compare(expected, before)",
        b"for item in expected.files:",
        b"stream.read(min(65536, MAX_FILE - size + 1, MAX_TOTAL - total + 1))",
        b"after = _capture(expected, tuple(rows))",
        b"_compare(expected, after)",
        b"except _Failure as error: return ObservationResult(ProfileReport(\"REJECTED_PROFILE\", str(error)))",
        b"except (OSError, AttributeError, TypeError, ValueError, UnicodeError): return ObservationResult(ProfileReport(\"REJECTED_PROFILE\", \"OBSERVATION_FAILED\"))",
        b"return ObservationResult(ProfileReport(\"MATCHED_DECLARED_BASELINE\", \"NONE\", True), after)",
    )
    if any(normalized.count(fragment) != 1 for fragment in required):
        return None
    if len(re.findall(rb"\breturn\b", normalized)) != 5:
        return None
    if not all(normalized.index(left) < normalized.index(right)
               for left, right in zip(required[:6], required[1:6])):
        return None
    if not (normalized.index(required[5]) < normalized.index(required[6])
            < normalized.index(required[7]) < normalized.index(required[8])):
        return None
    return {
        "capture_order": ("before_files", "after_files"),
        "bounded_read_chunk_bytes": 65536,
        "file_and_total_caps_required": True,
        "failure_returns_observation": False,
        "success_report": "MATCHED_DECLARED_BASELINE",
        "source_path": "Tests/Tools/dgn007_import_runtime_profile.py",
        "source_sha256": DGN007_RUNTIME_PROFILE_SOURCE_SHA256,
        "runtime_capture_claimed": False,
        "trust_attested_claimed": False,
        "evidence_scope": "STATIC_FRESH_RECORD_CAPTURE_FLOW_CANDIDATE",
    }


def _target_profile_capture_schema_candidate(source_bytes):
    """Bind bounded module/path snapshots and Observation constructor order."""
    if (type(source_bytes) is not bytes or not source_bytes
            or len(source_bytes) > MAX_DGN007_RUNTIME_PROFILE_SOURCE_BYTES
            or _normalized_profile_source_sha256(source_bytes)
            != DGN007_RUNTIME_PROFILE_SOURCE_SHA256):
        return None
    bodies = re.findall(
        rb"(?ms)^def _capture\([^\n]*\):\r?\n(?P<body>.*?)(?=^@dataclass|^def |\Z)",
        source_bytes,
    )
    if len(bodies) != 1:
        return None
    normalized = re.sub(rb"\s+", b" ", bodies[0])
    required = (
        b"_need(type(sys.modules) is dict and len(sys.modules) <= MAX_RECORDS, \"RECORD_LIMIT\")",
        b"snapshot = sys.modules.copy()",
        b"_need(len(snapshot) <= MAX_RECORDS, \"RECORD_LIMIT\")",
        b"for name in snapshot: _text(name)",
        b"for sequence in (sys.path, sys.meta_path, sys.path_hooks): _need(type(sequence) in (list, tuple) and len(sequence) <= MAX_RECORDS)",
        b"for path in sys.path: _text(path)",
        b"modules = tuple(_module(n, m, expected.controls) for n, m in sorted(snapshot.items()))",
        b"return Observation(expected.token, sys.platform, sys.implementation.name, tuple(sys.version_info[:3]), sys.executable, os.path.realpath(sys.executable), (sys.prefix, sys.exec_prefix, sys.base_prefix, sys.base_exec_prefix), sysconfig.get_config_var(\"SOABI\") or \"\", (sys.flags.isolated, sys.flags.no_site, int(sys.dont_write_bytecode), sys.flags.ignore_environment, int(sys.flags.safe_path), sys.flags.optimize), tuple(sys.path), tuple(sys.meta_path), tuple(sys.path_hooks), modules, files)",
    )
    if any(normalized.count(fragment) != 1 for fragment in required):
        return None
    if len(re.findall(rb"\breturn\b", normalized)) != 1:
        return None
    if not all(normalized.index(left) < normalized.index(right)
               for left, right in zip(required[:7], required[1:7])):
        return None
    return {
        "observation_field_order": (
            "token", "platform", "implementation", "version", "executable",
            "executable_target", "prefixes", "abi", "flags", "paths",
            "finders", "hooks", "modules", "files",
        ),
        "module_snapshot_sorted": True,
        "module_and_path_counts_bounded": True,
        "module_rows_delegate_to_module_builder": True,
        "source_path": "Tests/Tools/dgn007_import_runtime_profile.py",
        "source_sha256": DGN007_RUNTIME_PROFILE_SOURCE_SHA256,
        "runtime_observation_claimed": False,
        "evidence_scope": "STATIC_PROFILE_CAPTURE_SCHEMA_CANDIDATE",
    }


def _target_profile_module_record_builder_candidate(source_bytes, capture_schema):
    """Bind module identity, loader classification and record construction."""
    if (type(source_bytes) is not bytes or not source_bytes
            or len(source_bytes) > MAX_DGN007_RUNTIME_PROFILE_SOURCE_BYTES
            or _normalized_profile_source_sha256(source_bytes)
            != DGN007_RUNTIME_PROFILE_SOURCE_SHA256
            or type(capture_schema) is not dict
            or capture_schema.get("module_rows_delegate_to_module_builder") is not True):
        return None
    bodies = re.findall(
        rb"(?ms)^def _module\([^\n]*\):\r?\n(?P<body>.*?)(?=^def |\Z)",
        source_bytes,
    )
    if len(bodies) != 1:
        return None
    normalized = re.sub(rb"\s+", b" ", bodies[0])
    required = (
        b"_need(type(name) is str and type(module) is ModuleType)",
        b"d = module.__dict__",
        b"_need(spec is None or type(spec) is ModuleSpec)",
        b"module_name, spec_name = FROZEN_NAMES.get(name, (name, name)) if loader is FrozenImporter else (name, name)",
        b"_need(d.get(\"__name__\") == module_name and (spec is None or (spec.name == spec_name and spec.loader is loader)), \"MODULE_COHERENCY\")",
        b"raw_locations = None if spec is None else spec.submodule_search_locations",
        b"if name in controls: kind = \"CONTROL\"",
        b"elif loader is BuiltinImporter: kind = \"BUILTIN\"",
        b"elif loader is FrozenImporter: kind = \"FROZEN\"",
        b"elif type(loader) is SourceFileLoader: kind = \"SOURCE\"",
        b"elif type(loader) is ExtensionFileLoader: kind = \"EXTENSION\"",
        b"else: raise _Failure(\"UNKNOWN_LOADER\")",
        b"return ModuleRecord(name, origin, file, kind, locations, module, spec, loader)",
    )
    if any(normalized.count(fragment) != 1 for fragment in required):
        return None
    if len(re.findall(rb"\breturn\b", normalized)) != 1:
        return None
    if not all(normalized.index(left) < normalized.index(right)
               for left, right in zip(required[:6], required[1:6])):
        return None
    if not all(normalized.index(left) < normalized.index(right)
               for left, right in zip(required[6:], required[7:])):
        return None
    return {
        "accepted_module_type": "ModuleType",
        "module_name_and_spec_identity_checked": True,
        "frozen_name_aliases_bound": True,
        "loader_kinds": ("CONTROL", "BUILTIN", "FROZEN", "SOURCE", "EXTENSION"),
        "unknown_loader_rejected": True,
        "record_field_order": (
            "name", "origin", "file", "kind", "locations", "module", "spec", "loader",
        ),
        "source_path": "Tests/Tools/dgn007_import_runtime_profile.py",
        "source_sha256": DGN007_RUNTIME_PROFILE_SOURCE_SHA256,
        "runtime_modules_claimed": False,
        "evidence_scope": "STATIC_PROFILE_MODULE_RECORD_BUILDER_CANDIDATE",
    }


def _target_profile_compare_contract_candidate(source_bytes, module_builder):
    """Bind the declared-profile versus observation comparison obligations."""
    if (type(source_bytes) is not bytes or not source_bytes
            or len(source_bytes) > MAX_DGN007_RUNTIME_PROFILE_SOURCE_BYTES
            or _normalized_profile_source_sha256(source_bytes)
            != DGN007_RUNTIME_PROFILE_SOURCE_SHA256
            or type(module_builder) is not dict
            or module_builder.get("runtime_modules_claimed") is not False):
        return None
    bodies = re.findall(
        rb"(?ms)^def _compare\([^\n]*\):\r?\n(?P<body>.*?)(?=^def |\Z)",
        source_bytes,
    )
    if len(bodies) != 1:
        return None
    normalized = re.sub(rb"\s+", b" ", bodies[0])
    if re.search(rb"\breturn\b", normalized) is not None:
        return None
    required = (
        b"_shape(expected, True)",
        b"_shape(obs, False)",
        b"_need(obs.platform == \"linux\", \"UNSUPPORTED_PLATFORM\")",
        b"_need(expected.implementation == obs.implementation == \"cpython\" and expected.version == obs.version and expected.version[:2] == (3, 12), \"INTERPRETER_MISMATCH\")",
        b"_need(obs.flags == (1, 1, 1, 1, 1, 0), \"FLAGS_MISMATCH\")",
        b"for name in (\"token\", \"executable\", \"executable_target\", \"prefixes\", \"abi\", \"paths\", \"files\"): _need(getattr(expected, name) == getattr(obs, name), \"PROFILE_MISMATCH\")",
        b"_need(all(a is b for a, b in zip(expected.finders, obs.finders)) and all(a is b for a, b in zip(expected.hooks, obs.hooks)), \"HOOK_MISMATCH\")",
        b"_need(len(expected.modules) == len(obs.modules), \"MODULE_MISMATCH\")",
        b"for a, b in zip(expected.modules, obs.modules):",
        b"_need((a.name, a.origin, a.file, a.kind, a.locations) == (b.name, b.origin, b.file, b.kind, b.locations) and a.module is b.module and a.spec is b.spec and a.loader is b.loader, \"MODULE_MISMATCH\")",
        b"b.name == \"Tests\" or b.name.startswith(\"Tests.\")",
        b"run_dgn007_automated_setup", b"execution_target", b"docker_sqlcmd_proxy",
        b"run_demo", b"orchestrate_sessions", b"sqlcmd_process",
        b"if b.kind == \"CONTROL\":",
        b"_need(b.name in expected.controls, \"CONTROL_MISMATCH\")",
        b"elif b.kind in (\"SOURCE\", \"EXTENSION\"):",
        b"_need(_under(b.origin, expected.roots) and _under(b.file, expected.roots) and all(_under(p, expected.roots) for p in b.locations), \"ORIGIN_MISMATCH\")",
        b"_need(all(p in expected.roots or p == expected.inert_zip for p in obs.paths), \"PATH_MISMATCH\")",
    )
    if any(normalized.count(fragment) != 1 for fragment in required):
        return None
    if not all(normalized.index(left) < normalized.index(right)
               for left, right in zip(required, required[1:])):
        return None
    return {
        "interpreter_platform_version_flags_checked": True,
        "expected_observation_fields_compared": (
            "token", "executable", "executable_target", "prefixes", "abi", "paths", "files",
        ),
        "finder_and_hook_identity_checked": True,
        "module_row_values_and_anchor_identity_checked": True,
        "owned_modules_rejected": True,
        "control_and_source_roots_checked": True,
        "observation_paths_restricted": True,
        "source_path": "Tests/Tools/dgn007_import_runtime_profile.py",
        "source_sha256": DGN007_RUNTIME_PROFILE_SOURCE_SHA256,
        "trust_established": False,
        "evidence_scope": "STATIC_PROFILE_COMPARE_CONTRACT_CANDIDATE",
    }


def _target_profile_validation_report_flow_candidate(source_bytes, compare_contract):
    """Bind validate_profile report outcomes to compare success and failures."""
    if (type(source_bytes) is not bytes or not source_bytes
            or len(source_bytes) > MAX_DGN007_RUNTIME_PROFILE_SOURCE_BYTES
            or _normalized_profile_source_sha256(source_bytes)
            != DGN007_RUNTIME_PROFILE_SOURCE_SHA256
            or type(compare_contract) is not dict
            or compare_contract.get("trust_established") is not False):
        return None
    bodies = re.findall(
        rb"(?ms)^def validate_profile\([^\n]*\)[^\n]*:\r?\n(?P<body>.*?)(?=^def |\Z)",
        source_bytes,
    )
    if len(bodies) != 1:
        return None
    normalized = re.sub(rb"\s+", b" ", bodies[0])
    if len(re.findall(rb"\breturn\b", normalized)) != 3:
        return None
    required = (
        b"_compare(expected, observation)",
        b"except _Failure as error: return ProfileReport(\"REJECTED_PROFILE\", str(error))",
        b"except (AttributeError, TypeError, ValueError, UnicodeError): return ProfileReport(\"REJECTED_PROFILE\", \"INVALID_RECORD\")",
        b"return ProfileReport(\"MATCHED_DECLARED_BASELINE\", \"NONE\", True)",
    )
    if any(normalized.count(fragment) != 1 for fragment in required):
        return None
    if not all(normalized.index(left) < normalized.index(right)
               for left, right in zip(required, required[1:])):
        return None
    return {
        "compare_attempts": 1,
        "comparison_failure_status": "REJECTED_PROFILE",
        "malformed_record_issue": "INVALID_RECORD",
        "matched_status": "MATCHED_DECLARED_BASELINE",
        "trust_assumed_only_on_match": True,
        "trust_attested": False,
        "source_path": "Tests/Tools/dgn007_import_runtime_profile.py",
        "source_sha256": DGN007_RUNTIME_PROFILE_SOURCE_SHA256,
        "evidence_scope": "STATIC_PROFILE_VALIDATION_REPORT_FLOW_CANDIDATE",
    }


def _target_profile_shape_contract_candidate(
        source_bytes, compare_contract, capture_schema):
    """Bind shared and branch-specific DeclaredProfile/Observation shape checks."""
    if (type(source_bytes) is not bytes or not source_bytes
            or len(source_bytes) > MAX_DGN007_RUNTIME_PROFILE_SOURCE_BYTES
            or _normalized_profile_source_sha256(source_bytes)
            != DGN007_RUNTIME_PROFILE_SOURCE_SHA256
            or type(compare_contract) is not dict
            or compare_contract.get("trust_established") is not False
            or type(capture_schema) is not dict
            or capture_schema.get("runtime_observation_claimed") is not False):
        return None
    bodies = re.findall(
        rb"(?ms)^def _shape\([^\n]*\):\r?\n(?P<body>.*?)(?=^def |\Z)",
        source_bytes,
    )
    if len(bodies) != 1:
        return None
    normalized = re.sub(rb"\s+", b" ", bodies[0])
    if re.search(rb"\breturn\b", normalized) is not None:
        return None
    required = (
        b"_need(type(value) is (DeclaredProfile if expected else Observation))",
        b"_need(type(value.token) is bytes and len(value.token) == 32)",
        b"for item in (value.implementation, value.executable, value.abi): _text(item)",
        b"_need(type(value.version) is tuple and len(value.version) == 3 and all(type(n) is int and 0 <= n <= 999 for n in value.version))",
        b"_strings(value.prefixes)",
        b"_need(value.abi != \"\", \"INTERPRETER_MISMATCH\")",
        b"_need(len(value.prefixes) == 4)",
        b"_strings(value.paths)",
        b"_absolute(value.executable)",
        b"_absolute(value.executable_target)",
        b"for p in value.paths + value.prefixes: _absolute(p)",
        b"_need(type(value.finders) is tuple and len(value.finders) == 3 and all(a is b for a, b in zip(value.finders, (BuiltinImporter, FrozenImporter, PathFinder))))",
        b"_need(type(value.hooks) is tuple and len(value.hooks) == 2 and value.hooks[0] is zipimporter and type(value.hooks[1]) is FunctionType)",
        b"_records(value.modules)",
        b"_files(value.files)",
        b"if expected:",
        b"_need(value.assumption == ASSUMPTION, \"TRUST_UNDECLARED\")",
        b"_strings(value.roots)",
        b"_strings(value.controls)",
        b"_need(len(value.controls) <= 2 and all(n in (\"__main__\", \"dgn007_import_runtime_profile\") for n in value.controls) and len(value.controls) == len(set(value.controls)), \"CONTROL_MISMATCH\")",
        b"_text(value.inert_zip)",
        b"_need(len(value.roots) == 2 and len(set(value.roots)) == 2)",
        b"for p in value.roots + (value.inert_zip,): _absolute(p)",
        b"_need(not value.files or value.files[0].path == value.executable_target, \"HASH_PATH_MISMATCH\")",
        b"_need(len(value.files) < 2 or _under(value.files[1].path, value.roots), \"HASH_PATH_MISMATCH\")",
        b"else:",
        b"_text(value.platform)",
        b"_need(type(value.flags) is tuple and len(value.flags) == 6 and all(type(n) is int and 0 <= n <= 1 for n in value.flags))",
    )
    if any(normalized.count(fragment) != 1 for fragment in required):
        return None
    if not all(normalized.index(left) < normalized.index(right)
               for left, right in zip(required, required[1:])):
        return None
    return {
        "accepted_value_types": ("DeclaredProfile", "Observation"),
        "shared_field_contracts": (
            "token_32_bytes", "text_fields", "version_3_ints_0_to_999",
            "prefixes_4_absolute_paths", "absolute_executable_targets",
            "three_known_finders", "two_known_hooks", "module_records", "file_records",
        ),
        "declared_only_contracts": (
            "fixed_assumption", "two_unique_roots", "bounded_control_names",
            "absolute_inert_zip", "file_paths_bound_to_target_or_roots",
        ),
        "observation_only_contracts": ("text_platform", "six_binary_flags"),
        "source_path": "Tests/Tools/dgn007_import_runtime_profile.py",
        "source_sha256": DGN007_RUNTIME_PROFILE_SOURCE_SHA256,
        "input_validation_claimed": False,
        "runtime_observation_claimed": False,
        "evidence_scope": "STATIC_PROFILE_SHAPE_CONTRACT_CANDIDATE",
    }


def _target_profile_record_validators_candidate(source_bytes, shape_contract):
    """Bind module and file record invariants delegated by the profile shape check."""
    if (type(source_bytes) is not bytes or not source_bytes
            or len(source_bytes) > MAX_DGN007_RUNTIME_PROFILE_SOURCE_BYTES
            or _normalized_profile_source_sha256(source_bytes)
            != DGN007_RUNTIME_PROFILE_SOURCE_SHA256
            or type(shape_contract) is not dict
            or shape_contract.get("input_validation_claimed") is not False):
        return None
    records_bodies = re.findall(
        rb"(?ms)^def _records\([^\n]*\):\r?\n(?P<body>.*?)(?=^def |\Z)",
        source_bytes,
    )
    files_bodies = re.findall(
        rb"(?ms)^def _files\([^\n]*\):\r?\n(?P<body>.*?)(?=^def |\Z)",
        source_bytes,
    )
    if len(records_bodies) != 1 or len(files_bodies) != 1:
        return None
    records = re.sub(rb"\s+", b" ", records_bodies[0])
    files = re.sub(rb"\s+", b" ", files_bodies[0])
    if (re.search(rb"\breturn\b", records) is not None
            or re.search(rb"\breturn\b", files) is not None):
        return None
    record_requirements = (
        b"_need(type(value) is tuple and 0 < len(value) <= MAX_RECORDS)",
        b"_need(type(row) is ModuleRecord)",
        b"for item in (row.name, row.origin, row.file, row.kind): _text(item)",
        b"_strings(row.locations)",
        b"_need(type(row.module) is ModuleType and (row.spec is None or type(row.spec) is ModuleSpec))",
        b"_need(row.loader is None or row.loader is BuiltinImporter or row.loader is FrozenImporter or type(row.loader) in (SourceFileLoader, ExtensionFileLoader))",
        b"_need(row.kind in (\"BUILTIN\", \"FROZEN\", \"SOURCE\", \"EXTENSION\", \"CONTROL\"))",
        b"_need(type(row.loader.name) is str and row.loader.name == row.name and type(row.loader.path) is str and row.loader.path == row.file, \"MODULE_COHERENCY\")",
        b"_need(type(d.get(\"__name__\")) is str and d[\"__name__\"] == module_name and d.get(\"__spec__\") is row.spec and d.get(\"__loader__\") is row.loader and type(d.get(\"__file__\", \"\")) is str and d.get(\"__file__\", \"\") == row.file, \"MODULE_COHERENCY\")",
        b"_need(type(row.spec.name) is str and row.spec.name == spec_name and type(row.spec.origin) is str and row.spec.origin == row.origin and row.spec.loader is row.loader, \"MODULE_COHERENCY\")",
        b"_need(row.name in (\"__main__\", \"dgn007_import_runtime_profile\") and (row.loader is None or type(row.loader) is SourceFileLoader), \"CONTROL_MISMATCH\")",
        b"_need(row.loader is BuiltinImporter and row.origin == \"built-in\" and row.locations == (), \"MODULE_COHERENCY\")",
        b"_need(row.loader is FrozenImporter and row.origin == \"frozen\", \"MODULE_COHERENCY\")",
        b"_need(type(row.loader) is (SourceFileLoader if row.kind == \"SOURCE\" else ExtensionFileLoader) and row.origin == row.file, \"MODULE_COHERENCY\")",
        b"_need(names == sorted(set(names)))",
        b"_need(row.module is by_name[companion].module and row.spec is by_name[companion].spec, \"MODULE_COHERENCY\")",
    )
    file_requirements = (
        b"_need(type(value) is tuple and len(value) <= 2)",
        b"_need(type(row) is FileDigest)",
        b"_text(row.path)",
        b"_absolute(row.path)",
        b"_need(type(row.size) is int and 0 <= row.size <= MAX_FILE)",
        b"_need(type(row.sha256) is str and len(row.sha256) == 64 and all(c in \"0123456789abcdef\" for c in row.sha256))",
        b"_need(total <= MAX_TOTAL and len(paths) == len(set(paths)))",
    )
    if (any(records.count(fragment) != 1 for fragment in record_requirements)
            or any(files.count(fragment) != 1 for fragment in file_requirements)):
        return None
    if not all(records.index(left) < records.index(right)
               for left, right in zip(record_requirements, record_requirements[1:])):
        return None
    if not all(files.index(left) < files.index(right)
               for left, right in zip(file_requirements, file_requirements[1:])):
        return None
    return {
        "module_record_invariants": (
            "typed_module_and_spec", "loader_kind_and_coherence", "module_namespace_identity",
            "control_name_constraints", "sorted_unique_names", "frozen_companion_identity",
        ),
        "file_record_invariants": (
            "maximum_two_records", "absolute_unique_paths", "bounded_file_and_total_size",
            "lowercase_sha256_hex_64",
        ),
        "source_path": "Tests/Tools/dgn007_import_runtime_profile.py",
        "source_sha256": DGN007_RUNTIME_PROFILE_SOURCE_SHA256,
        "records_validated_claimed": False,
        "runtime_inventory_claimed": False,
        "evidence_scope": "STATIC_PROFILE_RECORD_VALIDATORS_CANDIDATE",
    }


def _target_profile_path_contract_candidate(source_bytes, record_contract):
    """Bind canonical absolute paths and declared-root containment checks."""
    if (type(source_bytes) is not bytes or not source_bytes
            or len(source_bytes) > MAX_DGN007_RUNTIME_PROFILE_SOURCE_BYTES
            or _normalized_profile_source_sha256(source_bytes)
            != DGN007_RUNTIME_PROFILE_SOURCE_SHA256
            or type(record_contract) is not dict
            or record_contract.get("records_validated_claimed") is not False):
        return None
    absolute_bodies = re.findall(
        rb"(?ms)^def _absolute\([^\n]*\):\r?\n(?P<body>.*?)(?=^def |\Z)",
        source_bytes,
    )
    under_bodies = re.findall(
        rb"(?ms)^def _under\([^\n]*\):\r?\n(?P<body>.*?)(?=^def |\Z)",
        source_bytes,
    )
    if len(absolute_bodies) != 1 or len(under_bodies) != 1:
        return None
    absolute = re.sub(rb"\s+", b" ", absolute_bodies[0])
    under = re.sub(rb"\s+", b" ", under_bodies[0])
    if re.search(rb"\breturn\b", absolute) is not None:
        return None
    absolute_requirements = (
        b"_text(value)",
        b"value.startswith(\"/\")",
        b'"//" not in value',
        b'"\\x00" not in value',
        b'(value == "/" or not value.endswith("/"))',
        b"all(p not in (\".\", \"..\") for p in value.split(\"/\"))",
        b'"PATH_MISMATCH"',
    )
    under_requirements = (
        b"path.startswith(\"/\")",
        b"all(part not in (\".\", \"..\") for part in path.split(\"/\"))",
        b"any(path == root or path.startswith(root.rstrip(\"/\") + \"/\") for root in roots)",
    )
    if (any(absolute.count(fragment) != 1 for fragment in absolute_requirements)
            or any(under.count(fragment) != 1 for fragment in under_requirements)):
        return None
    return {
        "absolute_path_invariants": (
            "bounded_text", "leading_slash", "no_double_slash", "no_nul",
            "no_trailing_slash_except_root", "no_dot_segments", "path_mismatch",
        ),
        "root_containment_invariants": (
            "absolute_path", "no_dot_segments", "component_boundary_containment",
        ),
        "source_path": "Tests/Tools/dgn007_import_runtime_profile.py",
        "source_sha256": DGN007_RUNTIME_PROFILE_SOURCE_SHA256,
        "path_validation_claimed": False,
        "host_attestation_claimed": False,
        "evidence_scope": "STATIC_PROFILE_PATH_CONTRACT_CANDIDATE",
    }


def _target_profile_primitive_validators_candidate(source_bytes, path_contract):
    """Bind bounded text and tuple-of-string validators used by the profile."""
    if (type(source_bytes) is not bytes or not source_bytes
            or len(source_bytes) > MAX_DGN007_RUNTIME_PROFILE_SOURCE_BYTES
            or _normalized_profile_source_sha256(source_bytes)
            != DGN007_RUNTIME_PROFILE_SOURCE_SHA256
            or type(path_contract) is not dict
            or path_contract.get("path_validation_claimed") is not False):
        return None
    text_bodies = re.findall(
        rb"(?ms)^def _text\([^\n]*\):\r?\n(?P<body>.*?)(?=^def |\Z)",
        source_bytes,
    )
    strings_bodies = re.findall(
        rb"(?ms)^def _strings\([^\n]*\):\r?\n(?P<body>.*?)(?=^def |\Z)",
        source_bytes,
    )
    need_bodies = re.findall(
        rb"(?ms)^def _need\([^\n]*\):\r?\n(?P<body>.*?)(?=^def |\Z)",
        source_bytes,
    )
    if len(text_bodies) != 1 or len(strings_bodies) != 1 or len(need_bodies) != 1:
        return None
    text_body = re.sub(rb"\s+", b" ", text_bodies[0])
    strings_body = re.sub(rb"\s+", b" ", strings_bodies[0])
    need_body = re.sub(rb"\s+", b" ", need_bodies[0])
    if (re.search(rb"\breturn\b", text_body) is not None
            or re.search(rb"\breturn\b", strings_body) is not None
            or re.search(rb"\breturn\b", need_body) is not None):
        return None
    if (need_body.count(b"if not condition:") != 1
            or need_body.count(b"raise _Failure(issue)") != 1
            or need_body.index(b"if not condition:") > need_body.index(b"raise _Failure(issue)")):
        return None
    text_requirements = (
        b"_need(type(value) is str and len(value) <= MAX_FIELD)",
        b"_need(len(value.encode(\"utf-8\")) <= MAX_FIELD)",
    )
    strings_requirements = (
        b"_need(type(value) is tuple and len(value) <= MAX_RECORDS)",
        b"for item in value: _text(item)",
    )
    if (any(text_body.count(fragment) != 1 for fragment in text_requirements)
            or any(strings_body.count(fragment) != 1 for fragment in strings_requirements)):
        return None
    return {
        "text_invariants": (
            "exact_str_type", "character_length_cap", "utf8_byte_length_cap",
        ),
        "string_tuple_invariants": (
            "exact_tuple_type", "record_count_cap", "each_item_text_validated",
        ),
        "failure_helper_invariants": ("invalid_condition_raises_failure",),
        "source_path": "Tests/Tools/dgn007_import_runtime_profile.py",
        "source_sha256": DGN007_RUNTIME_PROFILE_SOURCE_SHA256,
        "primitive_validation_claimed": False,
        "profile_input_validation_claimed": False,
        "evidence_scope": "STATIC_PROFILE_PRIMITIVE_VALIDATORS_CANDIDATE",
    }


def _target_profile_failure_primitive_candidate(source_bytes, primitive_contract):
    """Bind the profile's false-condition rejection and typed failure class."""
    if (type(source_bytes) is not bytes or not source_bytes
            or len(source_bytes) > MAX_DGN007_RUNTIME_PROFILE_SOURCE_BYTES
            or _normalized_profile_source_sha256(source_bytes)
            != DGN007_RUNTIME_PROFILE_SOURCE_SHA256
            or type(primitive_contract) is not dict
            or primitive_contract.get("profile_input_validation_claimed") is not False):
        return None
    failure_defs = re.findall(
        rb"(?m)^class _Failure\(([^)]+)\):\s*\r?\n\s+pass\s*$",
        source_bytes,
    )
    need_defs = re.findall(
        rb"(?ms)^def _need\(condition, issue=([^)]*)\):\r?\n(?P<body>.*?)(?=^def |\Z)",
        source_bytes,
    )
    if len(failure_defs) != 1 or len(need_defs) != 1:
        return None
    default_issue = re.sub(rb"\s+", b"", need_defs[0][0])
    need_body = re.sub(rb"\s+", b" ", need_defs[0][1])
    if (failure_defs[0] != b"ValueError"
            or default_issue != b'"INVALID_RECORD"'
            or need_body.count(b"if not condition:") != 1
            or need_body.count(b"raise _Failure(issue)") != 1):
        return None
    return {
        "failure_class": "_Failure_subclass_of_ValueError",
        "default_issue": "INVALID_RECORD",
        "false_condition_behavior": "raise_failure_with_issue",
        "input_validation_claimed": False,
        "source_path": "Tests/Tools/dgn007_import_runtime_profile.py",
        "source_sha256": DGN007_RUNTIME_PROFILE_SOURCE_SHA256,
        "evidence_scope": "STATIC_PROFILE_FAILURE_PRIMITIVE_CANDIDATE",
    }


def _target_profile_report_schema_candidate(source_bytes, failure_contract):
    """Bind report fields and the profile's false-attestation defaults."""
    if (type(source_bytes) is not bytes or not source_bytes
            or len(source_bytes) > MAX_DGN007_RUNTIME_PROFILE_SOURCE_BYTES
            or _normalized_profile_source_sha256(source_bytes)
            != DGN007_RUNTIME_PROFILE_SOURCE_SHA256
            or type(failure_contract) is not dict
            or failure_contract.get("input_validation_claimed") is not False):
        return None
    bodies = re.findall(
        rb"(?ms)^@dataclass\(frozen=True\)\r?\nclass ProfileReport:\r?\n(?P<body>.*?)(?=^class |^def |\Z)",
        source_bytes,
    )
    if len(bodies) != 1:
        return None
    normalized = re.sub(rb"\s+", b" ", bodies[0])
    required = (
        b"status: str",
        b"issue: str",
        b"trust_assumed: bool = False",
        b"trust_attested: bool = field(default=False, init=False)",
        b"runtime_attested: bool = field(default=False, init=False)",
        b"import_used_bytes_attested: bool = field(default=False, init=False)",
        b"method_approved: bool = field(default=False, init=False)",
    )
    if any(normalized.count(fragment) != 1 for fragment in required):
        return None
    return {
        "report_fields": (
            "status", "issue", "trust_assumed", "trust_attested",
            "runtime_attested", "import_used_bytes_attested", "method_approved",
        ),
        "attestation_and_approval_defaults_false": True,
        "attestation_fields_not_init_parameters": True,
        "profile_validation_claimed": False,
        "source_path": "Tests/Tools/dgn007_import_runtime_profile.py",
        "source_sha256": DGN007_RUNTIME_PROFILE_SOURCE_SHA256,
        "evidence_scope": "STATIC_PROFILE_REPORT_SCHEMA_CANDIDATE",
    }


def _target_profile_model_schemas_candidate(source_bytes, report_schema):
    """Bind frozen DeclaredProfile and Observation field layouts."""
    if (type(source_bytes) is not bytes or not source_bytes
            or len(source_bytes) > MAX_DGN007_RUNTIME_PROFILE_SOURCE_BYTES
            or _normalized_profile_source_sha256(source_bytes)
            != DGN007_RUNTIME_PROFILE_SOURCE_SHA256
            or type(report_schema) is not dict
            or report_schema.get("profile_validation_claimed") is not False):
        return None
    expected_fields = {
        "DeclaredProfile": (
            "assumption", "token", "implementation", "version", "executable",
            "executable_target", "prefixes", "abi", "paths", "roots",
            "inert_zip", "controls", "finders", "hooks", "modules", "files",
        ),
        "Observation": (
            "token", "platform", "implementation", "version", "executable",
            "executable_target", "prefixes", "abi", "flags", "paths",
            "finders", "hooks", "modules", "files",
        ),
    }
    actual_fields = {}
    for name in expected_fields:
        bodies = re.findall(
            rb"(?ms)^@dataclass\(frozen=True\)\r?\nclass "
            + name.encode("ascii")
            + rb":\r?\n(?P<body>.*?)(?=^class |^def |\Z)",
            source_bytes,
        )
        if len(bodies) != 1:
            return None
        fields = re.findall(rb"(?m)^    ([A-Za-z_][A-Za-z0-9_]*):", bodies[0])
        actual_fields[name] = tuple(item.decode("ascii") for item in fields)
        if actual_fields[name] != expected_fields[name]:
            return None
    return {
        "declared_profile_fields": actual_fields["DeclaredProfile"],
        "observation_fields": actual_fields["Observation"],
        "both_dataclasses_frozen": True,
        "profile_validation_claimed": False,
        "source_path": "Tests/Tools/dgn007_import_runtime_profile.py",
        "source_sha256": DGN007_RUNTIME_PROFILE_SOURCE_SHA256,
        "evidence_scope": "STATIC_PROFILE_MODEL_SCHEMAS_CANDIDATE",
    }


def _target_profile_record_model_schemas_candidate(source_bytes, model_schema):
    """Bind frozen ModuleRecord and FileDigest data layouts."""
    if (type(source_bytes) is not bytes or not source_bytes
            or len(source_bytes) > MAX_DGN007_RUNTIME_PROFILE_SOURCE_BYTES
            or _normalized_profile_source_sha256(source_bytes)
            != DGN007_RUNTIME_PROFILE_SOURCE_SHA256
            or type(model_schema) is not dict
            or model_schema.get("profile_validation_claimed") is not False):
        return None
    expected_fields = {
        "ModuleRecord": (
            "name", "origin", "file", "kind", "locations", "module", "spec", "loader",
        ),
        "FileDigest": ("path", "size", "sha256"),
    }
    actual_fields = {}
    for name, expected in expected_fields.items():
        bodies = re.findall(
            rb"(?ms)^@dataclass\(frozen=True\)\r?\nclass "
            + name.encode("ascii")
            + rb":\r?\n(?P<body>.*?)(?=^class |^def |\Z)",
            source_bytes,
        )
        if len(bodies) != 1:
            return None
        fields = re.findall(rb"(?m)^    ([A-Za-z_][A-Za-z0-9_]*):", bodies[0])
        actual_fields[name] = tuple(item.decode("ascii") for item in fields)
        if actual_fields[name] != expected:
            return None
    return {
        "module_record_fields": actual_fields["ModuleRecord"],
        "file_digest_fields": actual_fields["FileDigest"],
        "both_dataclasses_frozen": True,
        "record_validation_claimed": False,
        "source_path": "Tests/Tools/dgn007_import_runtime_profile.py",
        "source_sha256": DGN007_RUNTIME_PROFILE_SOURCE_SHA256,
        "evidence_scope": "STATIC_PROFILE_RECORD_MODEL_SCHEMAS_CANDIDATE",
    }


def _target_profile_result_model_schemas_candidate(source_bytes, record_model_schema):
    """Bind frozen full-record and scalar observation result wrappers."""
    if (type(source_bytes) is not bytes or not source_bytes
            or len(source_bytes) > MAX_DGN007_RUNTIME_PROFILE_SOURCE_BYTES
            or _normalized_profile_source_sha256(source_bytes)
            != DGN007_RUNTIME_PROFILE_SOURCE_SHA256
            or type(record_model_schema) is not dict
            or record_model_schema.get("record_validation_claimed") is not False):
        return None
    expected_fields = {
        "ObservationResult": ("report", "observation"),
        "ScalarObservationResult": ("report", "scalars"),
    }
    actual_fields = {}
    for name, expected in expected_fields.items():
        bodies = re.findall(
            rb"(?ms)^@dataclass\(frozen=True\)\r?\nclass "
            + name.encode("ascii")
            + rb":\r?\n(?P<body>.*?)(?=^class |^def |\Z)",
            source_bytes,
        )
        if len(bodies) != 1:
            return None
        fields = re.findall(rb"(?m)^    ([A-Za-z_][A-Za-z0-9_]*):", bodies[0])
        actual_fields[name] = tuple(item.decode("ascii") for item in fields)
        if actual_fields[name] != expected:
            return None
    return {
        "observation_result_fields": actual_fields["ObservationResult"],
        "scalar_observation_result_fields": actual_fields["ScalarObservationResult"],
        "both_dataclasses_frozen": True,
        "observation_claimed": False,
        "source_path": "Tests/Tools/dgn007_import_runtime_profile.py",
        "source_sha256": DGN007_RUNTIME_PROFILE_SOURCE_SHA256,
        "evidence_scope": "STATIC_PROFILE_RESULT_MODEL_SCHEMAS_CANDIDATE",
    }


def _target_selected_profile_result_schemas_candidate(source_bytes, result_model_schema):
    """Bind frozen private selected-profile result layouts and scopes."""
    if (type(source_bytes) is not bytes or not source_bytes
            or len(source_bytes) > MAX_DGN007_RUNTIME_PROFILE_SOURCE_BYTES
            or _normalized_profile_source_sha256(source_bytes)
            != DGN007_RUNTIME_PROFILE_SOURCE_SHA256
            or type(result_model_schema) is not dict
            or result_model_schema.get("observation_claimed") is not False):
        return None
    expected_fields = {
        "BoundProfileResult": ("report", "profile", "validation_scope"),
        "SelectedScalarObservationResult": (
            "report", "profile", "scalars", "validation_scope",
        ),
    }
    actual_fields = {}
    for name, expected in expected_fields.items():
        bodies = re.findall(
            rb"(?ms)^@dataclass\(frozen=True, slots=True, repr=False\)\r?\nclass "
            + name.encode("ascii")
            + rb":\r?\n(?P<body>.*?)(?=^class |^def |\Z)",
            source_bytes,
        )
        if len(bodies) != 1:
            return None
        normalized = re.sub(rb"\s+", b" ", bodies[0])
        fields = re.findall(rb"(?m)^    ([A-Za-z_][A-Za-z0-9_]*):", bodies[0])
        actual_fields[name] = tuple(item.decode("ascii") for item in fields)
        if (actual_fields[name] != expected
                or normalized.count(b'validation_scope: str = field(default="PROJECT_SEMANTIC", init=False)') != 1):
            return None
    return {
        "bound_profile_result_fields": actual_fields["BoundProfileResult"],
        "selected_scalar_observation_result_fields": actual_fields["SelectedScalarObservationResult"],
        "private_dataclasses_frozen_slotted_repr_hidden": True,
        "validation_scope": "PROJECT_SEMANTIC",
        "runtime_observation_claimed": False,
        "source_path": "Tests/Tools/dgn007_import_runtime_profile.py",
        "source_sha256": DGN007_RUNTIME_PROFILE_SOURCE_SHA256,
        "evidence_scope": "STATIC_SELECTED_PROFILE_RESULT_SCHEMAS_CANDIDATE",
    }


def _target_profile_record_observation_flow_candidate(source_bytes, result_schema):
    """Bind the ordered guarded file-capture workflow without claiming a run."""
    if (type(source_bytes) is not bytes or not source_bytes
            or len(source_bytes) > MAX_DGN007_RUNTIME_PROFILE_SOURCE_BYTES
            or _normalized_profile_source_sha256(source_bytes)
            != DGN007_RUNTIME_PROFILE_SOURCE_SHA256
            or type(result_schema) is not dict
            or result_schema.get("observation_claimed") is not False):
        return None
    bodies = re.findall(
        rb"(?ms)^def observe_current_interpreter_records\([^\n]*\)[^\n]*:\r?\n"
        rb"(?P<body>.*?)(?=^def |\Z)",
        source_bytes,
    )
    if len(bodies) != 1:
        return None
    body = re.sub(rb"\s+", b" ", bodies[0])
    required = (
        b"if type(sys.platform) is not str:",
        b"if sys.platform != \"linux\":",
        b"_shape(expected, True)",
        b"_need(all(os.path.isabs(p) and os.path.isdir(p) for p in expected.roots), \"ROOT_MISMATCH\")",
        b"_need(all(os.path.realpath(p) == p for p in expected.roots), \"ROOT_MISMATCH\")",
        b"_need(os.path.isabs(expected.executable) and os.path.isfile(expected.executable), \"INTERPRETER_MISMATCH\")",
        b"_need(os.path.realpath(expected.executable) == expected.executable_target, \"INTERPRETER_MISMATCH\")",
        b"_need(os.path.isabs(expected.inert_zip) and not os.path.lexists(expected.inert_zip), \"ZIP_MISMATCH\")",
        b"before = _capture(expected, expected.files)",
        b"_compare(expected, before)",
        b"for item in expected.files:",
        b"item.path == expected.executable_target or _under(item.path, expected.roots)",
        b"not os.path.islink(item.path) and os.path.isfile(item.path)",
        b"os.path.realpath(item.path) == item.path",
        b"with open(item.path, \"rb\") as stream:",
        b"_need(size <= MAX_FILE and total <= MAX_TOTAL, \"FILE_LIMIT\")",
        b"rows.append(FileDigest(item.path, size, digest.hexdigest()))",
        b"after = _capture(expected, tuple(rows))",
        b"_compare(expected, after)",
        b"except _Failure as error:",
        b"except (OSError, AttributeError, TypeError, ValueError, UnicodeError):",
        b"return ObservationResult(ProfileReport(\"MATCHED_DECLARED_BASELINE\", \"NONE\", True), after)",
    )
    if any(body.count(fragment) != 1 for fragment in required):
        return None
    if not all(body.index(left) < body.index(right)
               for left, right in zip(required, required[1:])):
        return None
    return {
        "capture_guards_and_order": (
            "linux_platform", "profile_shape", "root_and_executable_identity",
            "inert_zip_absence", "pre_capture_and_compare", "bounded_regular_file_hashes",
            "post_capture_and_compare", "fail_closed_reports",
        ),
        "source_path": "Tests/Tools/dgn007_import_runtime_profile.py",
        "source_sha256": DGN007_RUNTIME_PROFILE_SOURCE_SHA256,
        "runtime_observation_claimed": False,
        "trust_attested": False,
        "evidence_scope": "STATIC_PROFILE_RECORD_OBSERVATION_FLOW_CANDIDATE",
    }


def _target_selected_profile_post_contract_candidate(source_bytes, observation_flow):
    """Bind selected-runtime POST values and object anchors without running them."""
    if (type(source_bytes) is not bytes or not source_bytes
            or len(source_bytes) > MAX_DGN007_RUNTIME_PROFILE_SOURCE_BYTES
            or _normalized_profile_source_sha256(source_bytes)
            != DGN007_RUNTIME_PROFILE_SOURCE_SHA256
            or type(observation_flow) is not dict
            or observation_flow.get("runtime_observation_claimed") is not False):
        return None
    runtime_bodies = re.findall(
        rb"(?ms)^def _selected_runtime_post\([^\n]*\):\r?\n(?P<body>.*?)(?=^def |\Z)",
        source_bytes,
    )
    post_bodies = re.findall(
        rb"(?ms)^def _selected_post\([^\n]*\):\r?\n(?P<body>.*?)(?=^def |\Z)",
        source_bytes,
    )
    if len(runtime_bodies) != 1 or len(post_bodies) != 1:
        return None
    runtime = re.sub(rb"\s+", b" ", runtime_bodies[0])
    post = re.sub(rb"\s+", b" ", post_bodies[0])
    runtime_requirements = (
        b"type(implementation) is SimpleNamespace",
        b"implementation = _selected_namespace(implementation, keys).get(\"name\")",
        b"_scalar_text(implementation)",
        b"type(version) is tuple and len(version) == 3",
        b"type(version) is _NATIVE_VERSION_INFO_TYPE and len(version) == 5",
        b"version = tuple(version[:3])",
        b"all(type(number) is int and 0 <= number <= 999 for number in version)",
        b'("isolated", "no_site", "ignore_environment", "safe_path", "optimize")',
        b"type(flags) is _NATIVE_FLAGS_TYPE",
        b"type(values[3]) in (int, bool)",
        b"all(type(number) is int for number in values[:3] + values[4:])",
        b"all(0 <= number <= 1 for number in values)",
        b"type(bytecode) in (int, bool) and 0 <= bytecode <= 1",
        b"flags = (values[0], values[1], int(bytecode), values[2], int(values[3]), values[4])",
        b"type(paths) in (list, tuple) and len(paths) <= MAX_RECORDS",
        b"for path in paths: _scalar_text(path)",
        b"paths = tuple(paths)",
        b'("platform", "executable", "prefix", "exec_prefix", "base_prefix", "base_exec_prefix")',
        b"for value in values: _scalar_text(value)",
        b'("linux", expected.implementation, expected.version, expected.executable, expected.prefixes, (1, 1, 1, 1, 1, 0), expected.paths)',
    )
    post_requirements = (
        b"sys is runtime and os is providers[0] and sysconfig is providers[1]",
        b"current = _selected_containers(runtime, keys)",
        b"_selected_runtime_post(runtime, expected, keys)",
        b"all(a is b for a, b in zip(current, (cache, finders, hooks)))",
        b"all(a is b for a, b in zip(finders, expected.finders))",
        b"all(a is b for a, b in zip(hooks, expected.hooks))",
        b"_selected_cache(cache, names, keys)",
        b"all(cache[row.name] is row.module for row in expected.modules)",
        b"_selected_local(row.module, keys)",
        b"_shape(expected, True)",
    )
    if (any(runtime.count(fragment) != 1 for fragment in runtime_requirements)
            or any(post.count(fragment) != 1 for fragment in post_requirements)):
        return None
    if not all(post.index(left) < post.index(right)
               for left, right in zip(post_requirements, post_requirements[1:])):
        return None
    return {
        "runtime_post_checks": (
            "implementation_namespace", "version_shape_and_range", "startup_flag_types_and_values",
            "bytecode_flag", "bounded_paths", "linux_profile_tuple_match",
        ),
        "selected_post_anchor_checks": (
            "provider_identity", "runtime_values", "container_identity", "finder_and_hook_identity",
            "module_cache_identity", "local_module_shape", "profile_shape",
        ),
        "post_observation_claimed": False,
        "runtime_attested": False,
        "source_path": "Tests/Tools/dgn007_import_runtime_profile.py",
        "source_sha256": DGN007_RUNTIME_PROFILE_SOURCE_SHA256,
        "evidence_scope": "STATIC_SELECTED_PROFILE_POST_CONTRACT_CANDIDATE",
    }


def _target_selected_hook_post_contract_candidate(source_bytes, observation_flow):
    """Bind before/after hook identity and record equality checks."""
    if (type(source_bytes) is not bytes or not source_bytes
            or len(source_bytes) > MAX_DGN007_RUNTIME_PROFILE_SOURCE_BYTES
            or _normalized_profile_source_sha256(source_bytes)
            != DGN007_RUNTIME_PROFILE_SOURCE_SHA256
            or type(observation_flow) is not dict
            or observation_flow.get("runtime_observation_claimed") is not False):
        return None
    bodies = re.findall(
        rb"(?ms)^def _selected_hook_post\([^\n]*\):\r?\n(?P<body>.*?)(?=^def |\Z)",
        source_bytes,
    )
    if len(bodies) != 1:
        return None
    body = re.sub(rb"\s+", b" ", bodies[0])
    required = (
        b"all(a is b for a, b in zip(before[:7], after[:7]))",
        b"all(a[0] is b[0] and a[1] is b[1] and a[2] == b[2] for a, b in zip(before[7], after[7]))",
        b'"FILEFINDER_BINDING"',
    )
    if any(body.count(fragment) != 1 for fragment in required):
        return None
    return {
        "hook_identity_fields": ("finder", "loader", "path"),
        "hook_record_field_comparison": ("identity", "identity", "value"),
        "hook_mutation_rejected": True,
        "runtime_hook_observation_claimed": False,
        "source_path": "Tests/Tools/dgn007_import_runtime_profile.py",
        "source_sha256": DGN007_RUNTIME_PROFILE_SOURCE_SHA256,
        "evidence_scope": "STATIC_SELECTED_HOOK_POST_CONTRACT_CANDIDATE",
    }


def _target_filefinder_hook_contract_candidate(source_bytes, observation_flow):
    """Bind the FileFinder hook factory, closure anchors and loader suffix rows."""
    if (type(source_bytes) is not bytes or not source_bytes
            or len(source_bytes) > MAX_DGN007_RUNTIME_PROFILE_SOURCE_BYTES
            or _normalized_profile_source_sha256(source_bytes)
            != DGN007_RUNTIME_PROFILE_SOURCE_SHA256
            or type(observation_flow) is not dict
            or observation_flow.get("runtime_observation_claimed") is not False):
        return None
    bodies = re.findall(
        rb"(?ms)^def _filefinder_hook\([^\n]*\):\r?\n(?P<body>.*?)(?=^def |\Z)",
        source_bytes,
    )
    if len(bodies) != 1:
        return None
    body = re.sub(rb"\s+", b" ", bodies[0])
    required = (
        b"type(known) is FunctionType and observation.hooks[1] is known",
        b'r.name == "_frozen_importlib_external"',
        b"len(rows) == 1 and rows[0].kind == \"FROZEN\" and rows[0].loader is FrozenImporter",
        b'finder = namespace.get("FileFinder")',
        b'descriptor = finder.__dict__.get("path_hook")',
        b"type(descriptor) is classmethod and type(descriptor.__func__) is FunctionType",
        b"len(constants) <= MAX_RECORDS and any(known.__code__ is c for c in constants)",
        b'known.__code__.co_freevars == ("cls", "loader_details")',
        b"type(known.__closure__) is tuple and len(known.__closure__) == 2",
        b"cls is finder and type(details) is tuple and len(details) == 3",
        b'("ExtensionFileLoader", "SourceFileLoader", "SourcelessFileLoader")',
        b'("EXTENSION_SUFFIXES", "SOURCE_SUFFIXES", "BYTECODE_SUFFIXES")',
        b"suffixes == configured",
        b"return (finder, descriptor, factory, factory.__code__, known.__code__, cls, details, tuple((r[0], r[1], tuple(r[1])) for r in details))",
    )
    if any(body.count(fragment) != 1 for fragment in required):
        return None
    if not all(body.index(left) < body.index(right)
               for left, right in zip(required, required[1:])):
        return None
    return {
        "finder_hook_anchors": (
            "frozen_importlib_external_module", "FileFinder_class", "classmethod_path_hook",
            "factory_code_constant", "known_hook_globals_and_closure",
        ),
        "loader_detail_order": (
            "ExtensionFileLoader", "SourceFileLoader", "SourcelessFileLoader",
        ),
        "suffix_lists_bound": (
            "EXTENSION_SUFFIXES", "SOURCE_SUFFIXES", "BYTECODE_SUFFIXES",
        ),
        "runtime_hook_claimed": False,
        "trust_attested": False,
        "source_path": "Tests/Tools/dgn007_import_runtime_profile.py",
        "source_sha256": DGN007_RUNTIME_PROFILE_SOURCE_SHA256,
        "evidence_scope": "STATIC_FILEFINDER_HOOK_CONTRACT_CANDIDATE",
    }


def _target_profile_scalar_projection_contract_candidate(source_bytes, filefinder_contract):
    """Bind scalar NUL rejection and the profile's three projection records."""
    if (type(source_bytes) is not bytes or not source_bytes
            or len(source_bytes) > MAX_DGN007_RUNTIME_PROFILE_SOURCE_BYTES
            or _normalized_profile_source_sha256(source_bytes)
            != DGN007_RUNTIME_PROFILE_SOURCE_SHA256
            or type(filefinder_contract) is not dict
            or filefinder_contract.get("runtime_hook_claimed") is not False):
        return None
    scalar_bodies = re.findall(
        rb"(?ms)^def _scalar_text\([^\n]*\):\r?\n(?P<body>.*?)(?=^def |\Z)",
        source_bytes,
    )
    projection_bodies = re.findall(
        rb"(?ms)^def _project_scalars\([^\n]*\):\r?\n(?P<body>.*?)(?=^def |\Z)",
        source_bytes,
    )
    if len(scalar_bodies) != 1 or len(projection_bodies) != 1:
        return None
    scalar = re.sub(rb"\s+", b" ", scalar_bodies[0])
    projection = re.sub(rb"\s+", b" ", projection_bodies[0])
    scalar_requirements = (
        b"_text(value)", b'"\\x00" not in value', b'"SCALAR_FORM"',
    )
    projection_requirements = (
        b"_scalar_text(value)",
        b"_absolute(value)",
        b"set(expected.controls) == {r.name for r in observation.modules if r.kind == \"CONTROL\"}",
        b"by_name = {r.name: r for r in observation.modules}",
        b"_need(all(_under(p, expected.roots) for p in (row.origin, row.file) + row.locations), \"PATH_MISMATCH\")",
        b"_need(a.module is b.module and a.spec is b.spec, \"MODULE_COHERENCY\")",
        b"aliases = tuple(sorted(pair))",
        b"modules.append((row.name, module_name, spec_name, row.origin, row.file, row.kind, row.locations, loader, loader_name, loader_path, aliases))",
        b"selection = (expected.assumption, expected.roots, expected.inert_zip, expected.controls)",
        b'("BUILTIN", "FROZEN", "PATH"), ("ZIPIMPORTER", "FILEFINDER")',
        b"return selection, installation, tuple(modules)",
    )
    if (any(scalar.count(fragment) != 1 for fragment in scalar_requirements)
            or any(projection.count(fragment) < 1 for fragment in projection_requirements)):
        return None
    if not all(projection.index(left) < projection.index(right)
               for left, right in zip(projection_requirements, projection_requirements[1:])):
        return None
    return {
        "scalar_form": ("bounded_text", "no_nul"),
        "projection_sections": ("selection", "installation", "module_rows"),
        "control_and_root_checks": True,
        "loader_and_alias_identity_checks": True,
        "module_row_field_count": 11,
        "runtime_projection_claimed": False,
        "source_path": "Tests/Tools/dgn007_import_runtime_profile.py",
        "source_sha256": DGN007_RUNTIME_PROFILE_SOURCE_SHA256,
        "evidence_scope": "STATIC_PROFILE_SCALAR_PROJECTION_CONTRACT_CANDIDATE",
    }


def _target_selected_shape_primitives_candidate(source_bytes, selected_shape_contract):
    """Bind recursive primitive traversal and exact tuple/integer validators."""
    if (type(source_bytes) is not bytes or not source_bytes
            or len(source_bytes) > MAX_DGN007_RUNTIME_PROFILE_SOURCE_BYTES
            or _normalized_profile_source_sha256(source_bytes)
            != DGN007_RUNTIME_PROFILE_SOURCE_SHA256
            or type(selected_shape_contract) is not dict
            or selected_shape_contract.get("selected_values_claimed") is not False):
        return None
    bodies = {}
    for name in ("_selected_tree", "_selected_tuple", "_selected_int"):
        matches = re.findall(
            rb"(?ms)^def " + name.encode("ascii")
            + rb"\([^\n]*\):\r?\n(?P<body>.*?)(?=^def |\Z)",
            source_bytes,
        )
        if len(matches) != 1:
            return None
        bodies[name] = re.sub(rb"\s+", b" ", matches[0])
    tree_requirements = (
        b"pending, count = [(value, 0)], 0",
        b"while pending:",
        b"count += 1",
        b"count <= 16368 and depth <= 8",
        b"type(item) is tuple",
        b"len(item) <= MAX_RECORDS",
        b"pending.extend((child, depth + 1) for child in item)",
        b"type(item) is str",
        b"_scalar_text(item)",
        b"item is None or type(item) is int",
    )
    tuple_requirements = (
        b"type(value) is tuple and len(value) <= MAX_RECORDS",
        b"size is None or len(value) == size",
        b'"SELECTION_FORM"',
    )
    int_requirements = (
        b"type(value) is int and 0 <= value <= maximum",
        b'"SELECTION_FORM"',
    )
    if (any(bodies["_selected_tree"].count(fragment) != 1
            for fragment in tree_requirements)
            or any(bodies["_selected_tuple"].count(fragment) != 1
                   for fragment in tuple_requirements)
            or any(bodies["_selected_int"].count(fragment) != 1
                   for fragment in int_requirements)):
        return None
    if not all(bodies["_selected_tree"].index(left)
               < bodies["_selected_tree"].index(right)
               for left, right in zip(tree_requirements, tree_requirements[1:])):
        return None
    return {
        "tree_limits": {"nodes": 16368, "depth": 8, "tuple_items": "MAX_RECORDS"},
        "accepted_leaf_types": ("str", "NoneType", "int_exact"),
        "tuple_type": "exact_tuple_with_optional_exact_size",
        "integer_type": "exact_int_inclusive_range",
        "selected_shape_validation_claimed": False,
        "source_path": "Tests/Tools/dgn007_import_runtime_profile.py",
        "source_sha256": DGN007_RUNTIME_PROFILE_SOURCE_SHA256,
        "evidence_scope": "STATIC_SELECTED_SHAPE_PRIMITIVES_CANDIDATE",
    }


def _target_selected_namespace_contract_candidate(source_bytes, shape_primitives):
    """Bind namespace size/key budgets and exact dictionary/key types."""
    if (type(source_bytes) is not bytes or not source_bytes
            or len(source_bytes) > MAX_DGN007_RUNTIME_PROFILE_SOURCE_BYTES
            or _normalized_profile_source_sha256(source_bytes)
            != DGN007_RUNTIME_PROFILE_SOURCE_SHA256
            or type(shape_primitives) is not dict
            or shape_primitives.get("selected_shape_validation_claimed") is not False):
        return None
    bodies = {}
    for name in ("_selected_keys", "_selected_namespace"):
        matches = re.findall(
            rb"(?ms)^def " + name.encode("ascii")
            + rb"\([^\n]*\):\r?\n(?P<body>.*?)(?=^def |\Z)",
            source_bytes,
        )
        if len(matches) != 1:
            return None
        bodies[name] = re.sub(rb"\s+", b" ", matches[0])
    key_requirements = (
        b"budget[0] + len(namespace) <= 16368",
        b"for key in namespace:",
        b"budget[0] += 1",
        b"type(key) is str",
        b"_scalar_text(key)",
    )
    namespace_requirements = (
        b"namespace = value.__dict__",
        b"type(namespace) is dict and len(namespace) <= 16368",
        b"_selected_keys(namespace, budget)",
        b"return namespace",
    )
    if (any(bodies["_selected_keys"].count(fragment) != 1
            for fragment in key_requirements)
            or any(bodies["_selected_namespace"].count(fragment) != 1
                   for fragment in namespace_requirements)):
        return None
    return {
        "namespace_type": "exact_dict",
        "namespace_and_key_budget": 16368,
        "key_type": "exact_str",
        "shared_budget_increment_per_key": True,
        "scalar_key_validation": True,
        "selected_namespace_validation_claimed": False,
        "source_path": "Tests/Tools/dgn007_import_runtime_profile.py",
        "source_sha256": DGN007_RUNTIME_PROFILE_SOURCE_SHA256,
        "evidence_scope": "STATIC_SELECTED_NAMESPACE_CONTRACT_CANDIDATE",
    }


def _target_selected_anchor_contract_candidate(source_bytes, namespace_contract):
    """Bind local module/spec/loader validation and exact module-cache anchors."""
    if (type(source_bytes) is not bytes or not source_bytes
            or len(source_bytes) > MAX_DGN007_RUNTIME_PROFILE_SOURCE_BYTES
            or _normalized_profile_source_sha256(source_bytes)
            != DGN007_RUNTIME_PROFILE_SOURCE_SHA256
            or type(namespace_contract) is not dict
            or namespace_contract.get("selected_namespace_validation_claimed") is not False):
        return None
    bodies = {}
    for name in ("_selected_local", "_selected_cache"):
        matches = re.findall(
            rb"(?ms)^def " + name.encode("ascii")
            + rb"\([^\n]*\):\r?\n(?P<body>.*?)(?=^def |\Z)",
            source_bytes,
        )
        if len(matches) != 1:
            return None
        bodies[name] = re.sub(rb"\s+", b" ", matches[0])
    local_requirements = (
        b"type(module) is ModuleType",
        b"namespace = _selected_namespace(module, budget)",
        b'for key in ("__name__", "__file__")',
        b"_scalar_text(namespace.get(key, \"\"))",
        b"spec is None or type(spec) is ModuleSpec",
        b"selected = _selected_namespace(spec, budget)",
        b"_scalar_text(selected.get(\"name\")); _scalar_text(selected.get(\"origin\"))",
        b"type(locations) in (tuple, list) and len(locations) <= MAX_RECORDS",
        b"for path in locations: _scalar_text(path)",
        b"loader is None or loader is BuiltinImporter or loader is FrozenImporter",
        b"type(loader) in (SourceFileLoader, ExtensionFileLoader)",
        b"selected = _selected_namespace(loader, budget)",
        b"_scalar_text(selected.get(\"name\")); _scalar_text(selected.get(\"path\"))",
        b"return spec, loader",
    )
    cache_requirements = (
        b"type(cache) is dict and len(cache) == len(names)",
        b"_selected_keys(cache, budget)",
        b"tuple(sorted(cache)) == names",
        b'"CACHE_MISMATCH"',
    )
    if (any(bodies["_selected_local"].count(fragment) != (
                2 if fragment == b"type(loader) in (SourceFileLoader, ExtensionFileLoader)" else 1
            ) for fragment in local_requirements)
            or any(bodies["_selected_cache"].count(fragment) != 1
                   for fragment in cache_requirements)):
        return None
    if not all(bodies["_selected_local"].index(left)
               < bodies["_selected_local"].index(right)
               for left, right in zip(local_requirements, local_requirements[1:])):
        return None
    return {
        "module_type": "exact_ModuleType",
        "spec_type": "exact_ModuleSpec_or_none",
        "loader_types": ("BuiltinImporter", "FrozenImporter", "SourceFileLoader", "ExtensionFileLoader", "none"),
        "module_cache": "exact_dict_with_sorted_exact_name_set",
        "namespace_budget_shared": True,
        "selected_anchor_validation_claimed": False,
        "source_path": "Tests/Tools/dgn007_import_runtime_profile.py",
        "source_sha256": DGN007_RUNTIME_PROFILE_SOURCE_SHA256,
        "evidence_scope": "STATIC_SELECTED_ANCHOR_CONTRACT_CANDIDATE",
    }


def _target_selected_container_contract_candidate(source_bytes, anchor_contract):
    """Bind the selected runtime module's bounded cache/finder/hook containers."""
    if (type(source_bytes) is not bytes or not source_bytes
            or len(source_bytes) > MAX_DGN007_RUNTIME_PROFILE_SOURCE_BYTES
            or _normalized_profile_source_sha256(source_bytes)
            != DGN007_RUNTIME_PROFILE_SOURCE_SHA256
            or type(anchor_contract) is not dict
            or anchor_contract.get("selected_anchor_validation_claimed") is not False):
        return None
    bodies = re.findall(
        rb"(?ms)^def _selected_containers\([^\n]*\):\r?\n(?P<body>.*?)(?=^def |\Z)",
        source_bytes,
    )
    if len(bodies) != 1:
        return None
    normalized = re.sub(rb"\s+", b" ", bodies[0])
    required = (
        b"_need(type(runtime) is ModuleType, \"ANCHOR_FORM\")",
        b"namespace = _selected_namespace(runtime, keys)",
        b'cache = namespace.get("modules")',
        b'finders, hooks = namespace.get("meta_path"), namespace.get("path_hooks")',
        b"_need(type(cache) is dict and len(cache) <= MAX_RECORDS, \"ANCHOR_FORM\")",
        b"_need(type(finders) in (tuple, list) and len(finders) == 3 and type(hooks) in (tuple, list) and len(hooks) == 2, \"ANCHOR_FORM\")",
        b"return cache, finders, hooks",
    )
    if any(normalized.count(fragment) != 1 for fragment in required):
        return None
    if not all(normalized.index(left) < normalized.index(right)
               for left, right in zip(required, required[1:])):
        return None
    return {
        "runtime_module_type": "exact_ModuleType",
        "module_cache_type": "exact_dict_bounded_by_MAX_RECORDS",
        "finder_container": "exact_tuple_or_list_length_3",
        "hook_container": "exact_tuple_or_list_length_2",
        "selected_container_validation_claimed": False,
        "source_path": "Tests/Tools/dgn007_import_runtime_profile.py",
        "source_sha256": DGN007_RUNTIME_PROFILE_SOURCE_SHA256,
        "evidence_scope": "STATIC_SELECTED_CONTAINER_CONTRACT_CANDIDATE",
    }


def _target_s15_flags_field_candidate(worker_sys_flag_facts):
    """Join the fixed startup-flag facts into a static S15 field candidate."""
    expected = (
        ("sys.flags.isolated", 1),
        ("sys.flags.no_site", 1),
        ("sys.flags.dont_write_bytecode", 1),
        ("sys.flags.ignore_environment", 1),
        ("sys.flags.safe_path", True),
        ("sys.flags.optimize", 0),
        ("sys.dont_write_bytecode", True),
        ("sys.flags.no_user_site", 1),
        ("sys.flags.debug", 0),
        ("sys.flags.inspect", 0),
        ("sys.flags.interactive", 0),
        ("sys.flags.verbose", 0),
        ("sys.flags.bytes_warning", 0),
        ("sys.flags.quiet", 0),
        ("sys.flags.hash_randomization", 1),
        ("sys.flags.dev_mode", False),
        ("sys.flags.utf8_mode", 1),
        ("sys.flags.warn_default_encoding", False),
        ("sys.flags.int_max_str_digits", 4300),
    )
    if (type(worker_sys_flag_facts) is not tuple
            or len(worker_sys_flag_facts) != len(expected)
            or any(type(actual) is not tuple or len(actual) != 2
                   or actual[0] != wanted[0]
                   or type(actual[1]) is not type(wanted[1])
                   or actual[1] != wanted[1]
                   for actual, wanted in zip(worker_sys_flag_facts, expected))):
        return None
    return {
        "value": (1, 1, 1, 1, 1, 0),
        "source_fact_names": tuple(name for name, _ in expected[:6]),
        "worker_route_fact_count": len(expected),
        "runtime_flags_claimed": False,
        "evidence_scope": "STATIC_S15_FLAGS_FIELD_CANDIDATE",
    }


def _target_s15_paths_field_candidate(path_candidate):
    """Bind the ordered S15 paths to their inert-zip and root candidates."""
    expected_paths = (
        "/usr/local/lib/python312.zip",
        "/usr/local/lib/python3.12",
        "/usr/local/lib/python3.12/lib-dynload",
    )
    roots = (
        path_candidate.get("roots_field_candidate")
        if type(path_candidate) is dict else None
    )
    inert_zip = (
        path_candidate.get("inert_zip_field_candidate")
        if type(path_candidate) is dict else None
    )
    if (type(path_candidate) is not dict
            or path_candidate.get("sys_path_candidate") != list(expected_paths)
            or type(roots) is not dict
            or roots.get("values") != [expected_paths[1], expected_paths[2]]
            or roots.get("stdlib_root") != expected_paths[1]
            or roots.get("extension_root") != expected_paths[2]
            or roots.get("extension_file_verified") is not True
            or roots.get("runtime_roots_claimed") is not False
            or type(inert_zip) is not dict
            or inert_zip.get("value") != expected_paths[0]
            or inert_zip.get("path_role") != "ZIP_LANDMARK"
            or type(inert_zip.get("sys_path_candidate_index")) is not int
            or inert_zip.get("sys_path_candidate_index") != 0
            or inert_zip.get("image_member_absent") is not True
            or inert_zip.get("runtime_membership_claimed") is not False):
        return None
    return {
        "value": expected_paths,
        "inert_zip_candidate_bound": True,
        "roots_candidate_bound": True,
        "runtime_sys_path_claimed": False,
        "evidence_scope": "STATIC_S15_PATHS_FIELD_CANDIDATE",
    }


def _target_s15_roots_field_candidate(path_candidate):
    """Expose the verified standard-library roots as an explicit S15 field."""
    expected = (
        "/usr/local/lib/python3.12",
        "/usr/local/lib/python3.12/lib-dynload",
    )
    roots = (
        path_candidate.get("roots_field_candidate")
        if type(path_candidate) is dict else None
    )
    if (type(roots) is not dict
            or roots.get("values") != list(expected)
            or roots.get("stdlib_root") != expected[0]
            or roots.get("extension_root") != expected[1]
            or roots.get("extension_file_verified") is not True
            or roots.get("runtime_roots_claimed") is not False):
        return None
    return {
        "value": expected,
        "extension_file_verified": True,
        "runtime_roots_claimed": False,
        "evidence_scope": "STATIC_S15_ROOTS_FIELD_CANDIDATE",
    }


def _target_s15_inert_zip_field_candidate(path_candidate):
    """Expose the absent ZIP landmark as a static S15 field candidate."""
    expected_path = "/usr/local/lib/python312.zip"
    inert_zip = (
        path_candidate.get("inert_zip_field_candidate")
        if type(path_candidate) is dict else None
    )
    if (type(inert_zip) is not dict
            or inert_zip.get("value") != expected_path
            or inert_zip.get("path_role") != "ZIP_LANDMARK"
            or type(inert_zip.get("sys_path_candidate_index")) is not int
            or inert_zip.get("sys_path_candidate_index") != 0
            or inert_zip.get("image_member_absent") is not True
            or inert_zip.get("runtime_membership_claimed") is not False):
        return None
    return {
        "value": expected_path,
        "image_member_absent": True,
        "runtime_membership_claimed": False,
        "evidence_scope": "STATIC_S15_INERT_ZIP_FIELD_CANDIDATE",
    }


def _target_s15_files_field_candidate(path_candidate):
    """Expose the two bounded image-file candidates without claiming closure."""
    files = (
        path_candidate.get("files_field_candidate")
        if type(path_candidate) is dict else None
    )
    expected = (
        ("/usr/local/bin/python3.12", TARGET_EXECUTABLE_SHA256),
        ("/" + PICKLE_EXTENSION_PATH, PICKLE_EXTENSION_SHA256),
    )
    if type(files) is not list or len(files) != len(expected):
        return None
    rows = []
    for record, (expected_path, expected_digest) in zip(files, expected):
        if (type(record) is not dict
                or record.get("path") != expected_path
                or type(record.get("size")) is not int
                or not 0 <= record["size"] <= MAX_S15_FILE_BYTES
                or type(record.get("sha256")) is not str
                or record["sha256"] != expected_digest):
            return None
        rows.append((expected_path, record["size"], expected_digest))
    if sum(row[1] for row in rows) > MAX_S15_FILE_TOTAL_BYTES:
        return None
    return {
        "value": tuple(rows),
        "file_count": len(rows),
        "complete_file_list_claimed": False,
        "runtime_file_selection_claimed": False,
        "evidence_scope": "STATIC_S15_FILES_FIELD_CANDIDATE",
    }


def _target_s15_installation_tuple_candidate(candidates):
    """Join all fifteen static S15 field candidates in schema order."""
    expected_keys = {
        "assumption", "platform", "implementation", "version", "image_paths",
        "prefixes", "paths", "roots", "inert_zip", "flags", "finders",
        "hooks", "files", "schema",
    }
    if type(candidates) is not dict or set(candidates) != expected_keys:
        return None
    assumption = candidates["assumption"]
    platform = candidates["platform"]
    implementation = candidates["implementation"]
    version = candidates["version"]
    image_paths = candidates["image_paths"]
    prefixes = candidates["prefixes"]
    paths = candidates["paths"]
    roots = candidates["roots"]
    inert_zip = candidates["inert_zip"]
    flags = candidates["flags"]
    finders = candidates["finders"]
    hooks = candidates["hooks"]
    files = candidates["files"]
    schema = candidates["schema"]
    if any(type(candidate) is not dict for candidate in (
            assumption, platform, implementation, version, image_paths,
            prefixes, paths, roots, inert_zip, flags, finders, hooks, files,
            schema)):
        return None
    expected_field_order = (
        "assumption", "platform", "implementation", "version", "executable",
        "executable_target", "prefixes", "abi", "paths", "roots", "inert_zip",
        "flags", "finders", "hooks", "files",
    )
    if (schema.get("field_order") != expected_field_order
            or schema.get("tuple_length") != 15
            or schema.get("source_sha256") != DGN007_RUNTIME_PROFILE_SOURCE_SHA256
            or assumption.get("source_sha256") != schema.get("source_sha256")
            or schema.get("runtime_schema_claimed") is not False):
        return None
    executable = image_paths.get("executable_field_candidate")
    abi = image_paths.get("abi_field_candidate")
    executable_target = image_paths.get("executable_target_candidate")
    if (type(executable) is not dict or type(abi) is not dict
            or assumption.get("value") != "DECLARED_SETUP_PYTHON_CONTROL_RUNTIME"
            or assumption.get("runtime_assumption_attested") is not False
            or platform.get("value") != "linux"
            or platform.get("runtime_platform_claimed") is not False
            or implementation.get("value") != "cpython"
            or implementation.get("runtime_implementation_claimed") is not False
            or version.get("value") != (3, 12, 16)
            or version.get("runtime_version_claimed") is not False
            or executable.get("value") != "/usr/local/bin/python3.12"
            or executable.get("target") != executable_target
            or executable.get("direct_regular_file") is not True
            or executable.get("runtime_executable_claimed") is not False
            or abi.get("value") != TARGET_SYSCONFIGDATA_EXPECTED_VALUES["SOABI"]
            or abi.get("runtime_abi_claimed") is not False
            or prefixes.get("values") != ("/usr/local",) * 4
            or prefixes.get("runtime_prefixes_claimed") is not False
            or paths.get("value") != (
                "/usr/local/lib/python312.zip",
                "/usr/local/lib/python3.12",
                "/usr/local/lib/python3.12/lib-dynload",
            )
            or paths.get("runtime_sys_path_claimed") is not False
            or roots.get("value") != (
                "/usr/local/lib/python3.12",
                "/usr/local/lib/python3.12/lib-dynload",
            )
            or roots.get("runtime_roots_claimed") is not False
            or inert_zip.get("value") != "/usr/local/lib/python312.zip"
            or inert_zip.get("runtime_membership_claimed") is not False
            or flags.get("value") != (1, 1, 1, 1, 1, 0)
            or flags.get("runtime_flags_claimed") is not False
            or finders.get("values") != ("BUILTIN", "FROZEN", "PATH")
            or finders.get("runtime_finder_instances_claimed") is not False
            or hooks.get("values") != ("ZIPIMPORTER", "FILEFINDER")
            or hooks.get("runtime_hook_objects_claimed") is not False
            or files.get("file_count") != 2
            or files.get("complete_file_list_claimed") is not False
            or files.get("runtime_file_selection_claimed") is not False
            or type(files.get("value")) is not tuple
            or len(files["value"]) != 2):
        return None
    file_rows = files["value"]
    if any(type(row) is not tuple or len(row) != 3
           or type(row[0]) is not str
           or type(row[1]) is not int
           or not 0 <= row[1] <= MAX_S15_FILE_BYTES
           or type(row[2]) is not str
           for row in file_rows):
        return None
    if (file_rows[0][0] != executable_target
            or file_rows[0][2] != TARGET_EXECUTABLE_SHA256
            or file_rows[1][0] != "/" + PICKLE_EXTENSION_PATH
            or file_rows[1][2] != PICKLE_EXTENSION_SHA256
            or sum(row[1] for row in file_rows) > MAX_S15_FILE_TOTAL_BYTES):
        return None
    value = (
        assumption["value"], platform["value"], implementation["value"],
        version["value"], executable["value"], executable_target,
        prefixes["values"], abi["value"], paths["value"], roots["value"],
        inert_zip["value"], flags["value"], finders["values"],
        hooks["values"], file_rows,
    )
    return {
        "value": value,
        "field_order": schema["field_order"],
        "schema_source_sha256": schema["source_sha256"],
        "complete_file_list_claimed": False,
        "runtime_record_claimed": False,
        "profile_selection_claimed": False,
        "evidence_scope": "STATIC_S15_INSTALLATION_TUPLE_CANDIDATE",
    }


def _configure_template_inventory(config_template, configure_source):
    if (type(config_template) is not bytes or not config_template
            or len(config_template) > MAX_CONFIG_C_TEMPLATE_BYTES
            or hashlib.sha256(config_template).hexdigest() != CONFIG_C_TEMPLATE_SHA256):
        raise ValueError("CONFIG_C_TEMPLATE_DIGEST")
    if (type(configure_source) is not bytes or not configure_source
            or len(configure_source) > MAX_CONFIGURE_SOURCE_BYTES
            or hashlib.sha256(configure_source).hexdigest() != CONFIGURE_SOURCE_SHA256):
        raise ValueError("CONFIGURE_SOURCE_DIGEST")
    c_text = config_template.decode("utf-8")
    if (c_text.count("/* -- ADDMODULE MARKER 1 -- */") != 1
            or c_text.count("/* -- ADDMODULE MARKER 2 -- */") != 1
            or c_text.count("struct _inittab _PyImport_Inittab[] = {") != 1):
        raise ValueError("CONFIG_C_TEMPLATE_MARKERS")
    rows = tuple(re.findall(
        r'^\s*\{"([A-Za-z_][A-Za-z0-9_]*)",\s*([A-Za-z_][A-Za-z0-9_]*|NULL)\},?\s*$',
        c_text, re.M,
    ))
    if len(rows) != 9 or len({name for name, _ in rows}) != len(rows):
        raise ValueError("CONFIG_C_TEMPLATE_ROWS")
    if not {"builtins", "sys", "marshal", "_imp"}.issubset({name for name, _ in rows}):
        raise ValueError("CONFIG_C_TEMPLATE_REQUIRED_ROWS")
    config_c_rows_sha256 = hashlib.sha256(
        "".join("\t".join(row) + "\n" for row in rows).encode("ascii")
    ).hexdigest()
    configure_text = configure_source.decode("utf-8")
    configure_lines = tuple(
        line.strip() for line in configure_text.splitlines()
        if "MODULE_BLOCK" in line or "MODULE_BUILDTYPE" in line
    )
    required_anchors = (
        "AC_DEFUN([_MODULE_BLOCK_ADD]",
        "AC_SUBST([MODULE_BLOCK])",
        "AC_SUBST([MODULE_BUILDTYPE])",
        "MODULE_BLOCK=",
    )
    if any(anchor not in configure_text for anchor in required_anchors):
        raise ValueError("CONFIGURE_MODULE_BLOCK_ANCHORS")
    configure_rows_sha256 = hashlib.sha256(
        "".join(line + "\n" for line in configure_lines).encode("utf-8")
    ).hexdigest()
    return {
        "config_c_source_sha256": CONFIG_C_TEMPLATE_SHA256,
        "config_c_source_bytes": len(config_template),
        "config_c_row_count": len(rows),
        "config_c_rows_sha256": config_c_rows_sha256,
        "configure_source_sha256": CONFIGURE_SOURCE_SHA256,
        "configure_source_bytes": len(configure_source),
        "configure_module_anchor_count": len(configure_lines),
        "configure_module_anchors_sha256": configure_rows_sha256,
    }


def _module_path(module, files):
    relative = module.replace(".", "/")
    package = relative + "/__init__.py"
    return package if package in files else relative + ".py" if relative + ".py" in files else None


def _module_source_rows(files, modules):
    """Return the ordered name/path/hash evidence for source candidates only."""
    if (type(modules) is not tuple or len(modules) > MAX_SOURCE_FILES
            or any(type(name) is not str or not name
                   or any(not part.isidentifier() for part in name.split("."))
                   for name in modules)):
        raise ValueError("CANDIDATE_MODULES")
    if modules != tuple(sorted(set(modules))):
        raise ValueError("CANDIDATE_MODULES")
    rows = []
    for module in modules:
        path = _module_path(module, files)
        if path is None or path not in files:
            raise ValueError("CANDIDATE_SOURCE_MISSING")
        rows.append({
            "module": module,
            "source_path": path,
            "source_sha256": hashlib.sha256(files[path]).hexdigest(),
        })
    return rows


def _import_names(tree, module, path):
    package = module if path.endswith("/__init__.py") else module.rpartition(".")[0]

    def literal_string(node):
        if isinstance(node, ast.Constant) and type(node.value) is str:
            return node.value
        if isinstance(node, ast.JoinedStr):
            parts = []
            for value in node.values:
                if isinstance(value, ast.Constant) and type(value.value) is str:
                    parts.append(value.value)
                elif (isinstance(value, ast.FormattedValue)
                      and value.conversion in (-1, ord("s"))
                      and isinstance(value.value, (ast.Constant, ast.JoinedStr))):
                    formatted_value = literal_string(value.value)
                    format_spec = (literal_string(value.format_spec)
                                   if value.format_spec is not None else None)
                    if (formatted_value is None
                            or (value.format_spec is not None and format_spec != "s")):
                        return None
                    parts.append(formatted_value)
                else:
                    return None
            return "".join(parts)
        if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Add):
            left, right = literal_string(node.left), literal_string(node.right)
            if left is not None and right is not None:
                return left + right

    literal_name_aliases = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            targets = node.targets
        elif isinstance(node, ast.AnnAssign):
            targets = (node.target,)
        else:
            continue
        literal_value = literal_string(node.value)
        if literal_value is None:
            continue
        if not literal_value or literal_value.startswith("."):
            continue
        for target in targets:
            if isinstance(target, ast.Name):
                literal_name_aliases.setdefault(target.id, set()).add(literal_value)

    importlib_module_aliases = {"importlib"}
    import_module_aliases = set()
    builtins_module_aliases = {"builtins"}
    builtin_import_aliases = {"__import__"}
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                binding = alias.asname or alias.name.partition(".")[0]
                if alias.name == "importlib":
                    importlib_module_aliases.add(binding)
                elif alias.name == "builtins":
                    builtins_module_aliases.add(binding)
                elif alias.name == "importlib.import_module":
                    import_module_aliases.add(binding)
                elif alias.name == "builtins.__import__":
                    builtin_import_aliases.add(binding)
        elif isinstance(node, ast.ImportFrom):
            for alias in node.names:
                binding = alias.asname or alias.name
                if node.module == "importlib" and alias.name == "import_module":
                    import_module_aliases.add(binding)
                elif node.module == "builtins" and alias.name == "__import__":
                    builtin_import_aliases.add(binding)

    changed = True
    while changed:
        changed = False
        for node in ast.walk(tree):
            if isinstance(node, ast.Assign):
                targets = node.targets
            elif isinstance(node, ast.AnnAssign):
                targets = (node.target,)
            else:
                continue
            names = tuple(target.id for target in targets if isinstance(target, ast.Name))
            value = node.value
            if isinstance(value, ast.Name):
                if value.id in import_module_aliases:
                    aliases, source = import_module_aliases, value.id
                elif value.id in builtin_import_aliases:
                    aliases, source = builtin_import_aliases, value.id
                else:
                    continue
            elif (isinstance(value, ast.Attribute)
                  and isinstance(value.value, ast.Name)
                  and value.attr == "import_module"
                  and value.value.id in importlib_module_aliases):
                aliases, source = import_module_aliases, value.attr
            elif (isinstance(value, ast.Attribute)
                  and isinstance(value.value, ast.Name)
                  and value.attr == "__import__"
                  and value.value.id in builtins_module_aliases):
                aliases, source = builtin_import_aliases, value.attr
            else:
                continue
            for name in names:
                if name not in aliases:
                    aliases.add(name)
                    changed = True

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                yield alias.name
        elif isinstance(node, ast.ImportFrom):
            base = node.module or ""
            if node.level:
                parts = package.split(".") if package else []
                keep = max(0, len(parts) - node.level + 1)
                base = ".".join(parts[:keep] + ([base] if base else []))
            if base:
                yield base
                for alias in node.names:
                    if alias.name != "*":
                        yield base + "." + alias.name
        elif isinstance(node, ast.Call) and node.args:
            direct_literal = literal_string(node.args[0])
            if (direct_literal and not direct_literal.startswith(".")):
                import_names = (direct_literal,)
            elif isinstance(node.args[0], ast.Name):
                import_names = tuple(sorted(literal_name_aliases.get(node.args[0].id, ())))
            else:
                import_names = ()
            if not import_names:
                continue
            if isinstance(node.func, ast.Name) and node.func.id in builtin_import_aliases:
                yield from import_names
            elif (isinstance(node.func, ast.Attribute)
                  and node.func.attr == "import_module"
                  and isinstance(node.func.value, ast.Name)
                  and node.func.value.id in importlib_module_aliases):
                yield from import_names
            elif (isinstance(node.func, ast.Name)
                  and node.func.id in import_module_aliases):
                yield from import_names
            elif (isinstance(node.func, ast.Attribute)
                  and node.func.attr == "__import__"
                  and isinstance(node.func.value, ast.Name)
                  and node.func.value.id in builtins_module_aliases):
                yield from import_names


_KNOWN_BUILTIN_NAMES = object()
_IMPORTED_MODULE_NAME = object()
_STATIC_FALSE_LITERAL = object()
# Bounded from the digest-pinned linux/amd64 CPython 3.12.16 config.c/Inittab.
_TARGET_BUILTIN_MODULE_NAMES = (
    "_abc", "_ast", "_codecs", "_collections", "_functools", "_imp",
    "_io", "_locale", "_operator", "_signal", "_sre", "_stat",
    "_string", "_symtable", "_thread", "_tokenize", "_tracemalloc",
    "_typing", "_warnings", "_weakref", "atexit", "builtins", "errno",
    "faulthandler", "gc", "itertools", "marshal", "posix", "pwd", "sys",
    "time",
)
_TARGET_BUILTIN_MEMBERSHIP = {
    **dict.fromkeys(_TARGET_BUILTIN_MODULE_NAMES, True),
    "nt": False,
}
_TARGET_BUILTIN_CONFIG_C_SHA256 = (
    "30d353782cbaf8de2fed2ba82b1040940386e316b7f41604c49f8f3d6f16bb31"
)
_TARGET_BUILTIN_LAYER_SHA256 = (
    "7f0ea382d75a163999c21529b19913d158821816106eed6f02039f8fdf346779"
)
_TYPES_SOURCE_SHA256 = (
    "345474ef027a1273f353da9bdc1f7c18f65335e72e681bcc0376774cc51f2405"
)
_INSPECT_SOURCE_SHA256 = (
    "5c54ebf0bfdc25397750e5d0f63800751650ee50e65325ff3ea4069c9bfa5f75"
)
_AST_SOURCE_SHA256 = "b515c23dbbc459329d3b802a3aac742cc456d7472e66f7ed6e9dc97e40596d7d"
_TARGET_TYPES_DESCRIPTOR_ATTRIBUTES = (
    "GetSetDescriptorType", "MemberDescriptorType",
)


def _target_types_descriptor_call_facts(files):
    """Bind two `types` names only to their digest-pinned direct source definitions."""
    types_source = files.get("types.py")
    inspect_source = files.get("inspect.py")
    if (type(types_source) is not bytes or type(inspect_source) is not bytes
            or hashlib.sha256(types_source).hexdigest() != _TYPES_SOURCE_SHA256
            or hashlib.sha256(inspect_source).hexdigest() != _INSPECT_SOURCE_SHA256):
        return ()

    types_tree = ast.parse(types_source, filename="types.py")
    inspect_tree = ast.parse(inspect_source, filename="inspect.py")
    for name in _TARGET_TYPES_DESCRIPTOR_ATTRIBUTES:
        assignments = [
            statement for statement in types_tree.body
            if isinstance(statement, ast.Assign)
            and any(isinstance(target, ast.Name) and target.id == name
                    for target in statement.targets)
        ]
        stores = [
            node for node in ast.walk(types_tree)
            if isinstance(node, ast.Name) and node.id == name
            and isinstance(node.ctx, (ast.Store, ast.Del))
        ]
        if (len(assignments) != 1 or len(stores) != 1
                or not isinstance(assignments[0].value, ast.Call)
                or not isinstance(assignments[0].value.func, ast.Name)
                or assignments[0].value.func.id != "type"):
            return ()

    imports_types = [
        alias for statement in inspect_tree.body if isinstance(statement, ast.Import)
        for alias in statement.names if alias.name == "types"
    ]
    if (len(imports_types) != 1 or imports_types[0].asname is not None
            or any(isinstance(node, ast.Name) and node.id in {"types", "hasattr"}
                   and isinstance(node.ctx, (ast.Store, ast.Del))
                   for node in ast.walk(inspect_tree))):
        return ()

    facts = []
    for name in _TARGET_TYPES_DESCRIPTOR_ATTRIBUTES:
        expression = f"hasattr(types, {name!r})"
        if not any(isinstance(node, ast.If) and ast.unparse(node.test) == expression
                   for node in inspect_tree.body):
            return ()
        facts.append(expression)
    return tuple((expression, True) for expression in sorted(facts))


def _target_ast_compatibility_call_facts(files, asdl_source, c_source):
    """Bind two legacy AST attribute absences to the pinned generated types."""
    ast_source = files.get("ast.py")
    if (type(ast_source) is not bytes
            or hashlib.sha256(ast_source).hexdigest() != _AST_SOURCE_SHA256
            or type(asdl_source) is not bytes
            or hashlib.sha256(asdl_source).hexdigest() != AST_ASDL_SHA256
            or type(c_source) is not bytes
            or hashlib.sha256(c_source).hexdigest() != AST_C_SHA256):
        return ()

    asdl_text = asdl_source.decode("utf-8")
    c_text = c_source.decode("utf-8")
    ast_tree = ast.parse(ast_source, filename="ast.py")
    if not any(
            isinstance(statement, ast.ImportFrom)
            and statement.module == "_ast"
            and any(alias.name == "*" for alias in statement.names)
            for statement in ast_tree.body):
        return ()
    if any(isinstance(node, ast.Name) and node.id in {"Constant", "Tuple", "hasattr"}
           and isinstance(node.ctx, (ast.Store, ast.Del)) for node in ast.walk(ast_tree)):
        return ()
    if not re.search(
            r'PyObject_SetAttrString\(state->AST_type, "_fields", empty_tuple\) < 0'
            r'.*?PyObject_SetAttrString\(state->AST_type, "_attributes", empty_tuple\) < 0',
            c_text, re.DOTALL):
        return ()
    if not re.search(
            r'state->expr_type\s*=\s*make_type\(state, "expr", state->AST_type, NULL, 0,',
            c_text):
        return ()

    definitions = (
        ("Constant", "constant value, string? kind", ("value", "kind"), "n"),
        ("Tuple", "expr* elts, expr_context ctx", ("elts", "ctx"), "dims"),
    )
    facts = []
    for name, asdl_fields, c_fields, absent_attribute in definitions:
        if (asdl_fields not in asdl_text
                or not re.search(
                    rf"\b{re.escape(name)}_fields\s*\[\s*\]\s*=\s*\{{([^}}]*)\}}\s*;",
                    c_text,
                )):
            return ()
        field_match = re.search(
            rf"\b{re.escape(name)}_fields\s*\[\s*\]\s*=\s*\{{([^}}]*)\}}\s*;", c_text
        )
        field_names = tuple(re.findall(r'"([^"\\]+)"', field_match.group(1)))
        if field_names != c_fields or absent_attribute in field_names:
            return ()
        make_type_pattern = (
            rf'state->{name}_type\s*=\s*make_type\(state,\s*"{name}",\s*'
            rf'state->expr_type,\s*{name}_fields,\s*{len(c_fields)},'
        )
        if not re.search(make_type_pattern, c_text):
            return ()
        expression = f"hasattr({name}, {absent_attribute!r})"
        expected_if = f"not {expression}"
        if not any(isinstance(node, ast.If) and ast.unparse(node.test) == expected_if
                   for node in ast.walk(ast_tree)):
            return ()
        facts.append((expression, False))
    return tuple(sorted(facts))


def _target_importlib_windows_name_facts(files):
    """Resolve the pinned importlib Windows selector from its direct sys binding."""
    source = files.get("importlib/_bootstrap_external.py")
    if (type(source) is not bytes
            or hashlib.sha256(source).hexdigest() != IMPORTLIB_EXTERNAL_SOURCE_SHA256):
        return {}
    tree = ast.parse(source, filename="importlib/_bootstrap_external.py")
    sys_imports = [
        alias for statement in tree.body if isinstance(statement, ast.Import)
        for alias in statement.names if alias.name == "sys"
    ]
    sys_stores = [
        node for node in ast.walk(tree)
        if isinstance(node, ast.Name) and node.id == "sys"
        and isinstance(node.ctx, (ast.Store, ast.Del))
    ]
    assignments = [
        statement for statement in tree.body if isinstance(statement, ast.Assign)
        and any(isinstance(target, ast.Name) and target.id == "_MS_WINDOWS"
                for target in statement.targets)
    ]
    windows_stores = [
        node for node in ast.walk(tree)
        if isinstance(node, ast.Name) and node.id == "_MS_WINDOWS"
        and isinstance(node.ctx, (ast.Store, ast.Del))
    ]
    windows_guards = [
        node for node in ast.walk(tree)
        if isinstance(node, ast.If) and ast.unparse(node.test) == "_MS_WINDOWS"
    ]
    expected = "sys.platform == 'win32'"
    if (len(sys_imports) != 1 or sys_imports[0].asname is not None or sys_stores
            or len(assignments) != 1 or len(windows_stores) != 1
            or not windows_guards
            or ast.unparse(assignments[0].value) != expected
            or assignments[0].lineno >= min(
                node.lineno for node in windows_guards
            )):
        return {}
    return {"_MS_WINDOWS": False}


def _target_sys_getframe_call_facts(files, sys_module_source, clinic_source):
    """Bind logging's sys._getframe probe to the pinned builtin method table."""
    logging_source = files.get("logging/__init__.py")
    if (type(logging_source) is not bytes
            or hashlib.sha256(logging_source).hexdigest() != LOGGING_SOURCE_SHA256
            or type(sys_module_source) is not bytes
            or hashlib.sha256(sys_module_source).hexdigest() != SYS_MODULE_C_SHA256
            or type(clinic_source) is not bytes
            or hashlib.sha256(clinic_source).hexdigest() != SYS_MODULE_CLINIC_SHA256
            or _TARGET_BUILTIN_MEMBERSHIP.get("sys") is not True):
        return ()
    logging_tree = ast.parse(logging_source, filename="logging/__init__.py")
    c_text = sys_module_source.decode("utf-8")
    clinic_text = clinic_source.decode("utf-8")
    imports_sys = [
        alias for statement in logging_tree.body if isinstance(statement, ast.Import)
        for alias in statement.names if alias.name == "sys"
    ]
    if (len(imports_sys) != 1 or imports_sys[0].asname is not None
            or any(isinstance(node, ast.Name) and node.id in {"sys", "hasattr"}
                   and isinstance(node.ctx, (ast.Store, ast.Del))
                   for node in ast.walk(logging_tree))
            or not any(isinstance(node, ast.If)
                       and ast.unparse(node.test) == "hasattr(sys, '_getframe')"
                       for node in logging_tree.body)):
        return ()
    clinic_lines = clinic_text.splitlines()
    methoddef_index = next((index for index, line in enumerate(clinic_lines)
                            if line.startswith("#define SYS__GETFRAME_METHODDEF")), None)
    if (methoddef_index is None or methoddef_index + 1 >= len(clinic_lines)
            or '"_getframe"' not in clinic_lines[methoddef_index + 1]
            or '#include "clinic/sysmodule.c.h"' not in c_text
            or not re.search(r"(?m)^static PyMethodDef sys_methods\[\] = \{", c_text)
            or not re.search(r"(?m)^\s*SYS__GETFRAME_METHODDEF$", c_text)
            or not re.search(r"(?m)^static struct PyModuleDef sysmodule = \{", c_text)
            or not re.search(r"(?s)static struct PyModuleDef sysmodule = \{.*?\n\s*sys_methods,", c_text)
            ):
        return ()
    return (("hasattr(sys, '_getframe')", True),)


def _target_warnings_default_call_facts(files, c_source, clinic_source):
    """Prove the C warnings backend is selected by the pinned builtin import."""
    source = files.get("warnings.py")
    if (type(source) is not bytes
            or hashlib.sha256(source).hexdigest() != WARNINGS_SOURCE_SHA256
            or type(c_source) is not bytes
            or hashlib.sha256(c_source).hexdigest() != WARNINGS_C_SHA256
            or type(clinic_source) is not bytes
            or hashlib.sha256(clinic_source).hexdigest() != WARNINGS_CLINIC_SHA256
            or _TARGET_BUILTIN_MEMBERSHIP.get("_warnings") is not True):
        return {}
    tree = ast.parse(source, filename="warnings.py")
    backend_imports = [
        statement for statement in ast.walk(tree)
        if isinstance(statement, ast.ImportFrom) and statement.module == "_warnings"
    ]
    expected_names = {
        "filters", "_defaultaction", "_onceregistry", "warn", "warn_explicit",
        "_filters_mutated",
    }
    if (len(backend_imports) != 1
            or {alias.name for alias in backend_imports[0].names} != expected_names
            or not any(
                isinstance(node, ast.If) and ast.unparse(node.test) == "not _warnings_defaults"
                for node in tree.body
            )):
        return {}
    c_text = c_source.decode("utf-8")
    clinic_text = clinic_source.decode("utf-8")
    required_methods = (
        ("WARNINGS_WARN_METHODDEF", '"warn"'),
        ("WARNINGS_WARN_EXPLICIT_METHODDEF", '"warn_explicit"'),
        ("WARNINGS_FILTERS_MUTATED_METHODDEF", '"_filters_mutated"'),
    )
    clinic_lines = clinic_text.splitlines()
    for macro, method_name in required_methods:
        index = next((i for i, line in enumerate(clinic_lines)
                      if line.startswith(f"#define {macro}")), None)
        if (index is None or index + 1 >= len(clinic_lines)
                or method_name not in clinic_lines[index + 1]):
            return {}
    required_source_patterns = (
        r'#include "clinic/_warnings\.c\.h"',
        r"static PyMethodDef warnings_functions\[\] = \{",
        r"WARNINGS_WARN_METHODDEF",
        r"WARNINGS_WARN_EXPLICIT_METHODDEF",
        r"WARNINGS_FILTERS_MUTATED_METHODDEF",
        r'PyModule_AddObjectRef\(module, "filters", st->filters\)',
        r'PyModule_AddObjectRef\(module, "_onceregistry", st->once_registry\)',
        r'PyModule_AddObjectRef\(module, "_defaultaction", st->default_action\)',
        r"\.m_methods = warnings_functions",
        r"\.m_slots = warnings_slots",
        r"\{Py_mod_exec, warnings_module_exec\}",
    )
    if any(not re.search(pattern, c_text) for pattern in required_source_patterns):
        return {}
    return {"_warnings_defaults": True}


def _target_isolated_worker_route_valid(
        preconfig_source, initconfig_source, worker_source):
    """Validate the one digest-pinned isolated child route shared by route facts."""
    sources = (
        (preconfig_source, PRECONFIG_C_SHA256, MAX_PRECONFIG_C_BYTES),
        (initconfig_source, INITCONFIG_C_SHA256, MAX_INITCONFIG_C_BYTES),
        (worker_source, IMPORT_USED_BYTES_PROBE_SHA256,
         MAX_WORKER_CONTROL_SOURCE_BYTES),
    )
    if any(type(source) is not bytes or not source or len(source) > limit
           or hashlib.sha256(source).hexdigest() != digest
           for source, digest, limit in sources):
        return False
    preconfig_text = preconfig_source.decode("utf-8")
    initconfig_text = initconfig_source.decode("utf-8")
    if (not re.search(
            r"case 'I':\s*cmdline->isolated\s*=\s*1;", preconfig_text
            )
            or not re.search(
                r"if \(config->isolated\)\s*\{[^}]*config->use_environment\s*=\s*0;",
                initconfig_text,
            )):
        return False
    try:
        worker_tree = ast.parse(worker_source, filename="dgn007_import_used_bytes_probe.py")
    except SyntaxError:
        return False
    run_functions = [node for node in worker_tree.body
                     if isinstance(node, ast.FunctionDef)
                     and node.name == "run_import_only"]
    collector_functions = [node for node in worker_tree.body
                           if isinstance(node, ast.FunctionDef)
                           and node.name == "_collect_process"]
    if len(run_functions) != 1 or len(collector_functions) != 1:
        return False
    command_assignments = [
        node for node in ast.walk(run_functions[0])
        if isinstance(node, ast.Assign)
        and any(isinstance(target, ast.Name) and target.id == "command"
                for target in node.targets)
    ]
    expected_command = (
        "[sys.executable, '-I', '-S', '-B', '-X', 'utf8=1', '-c', "
        "_worker_source(ordinal, worker_nonce)]"
    )
    popen_calls = [
        node for node in ast.walk(collector_functions[0])
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
        and ast.unparse(node.func) == "subprocess.Popen"
    ]
    collector = collector_functions[0] if len(collector_functions) == 1 else None
    env_copy = ast.parse("child_env = os.environ.copy()").body[0]
    env_filter = ast.parse(
        "child_env.pop('_PYTHON_SYSCONFIGDATA_NAME', None)"
    ).body[0]
    ordered_environment = False
    if collector is not None:
        body = collector.body
        copy_indexes = [index for index, node in enumerate(body)
                        if ast.dump(node, include_attributes=False)
                        == ast.dump(env_copy, include_attributes=False)]
        filter_indexes = [index for index, node in enumerate(body)
                          if ast.dump(node, include_attributes=False)
                          == ast.dump(env_filter, include_attributes=False)]
        popen_statement_indexes = [
            index for index, node in enumerate(body)
            if isinstance(node, ast.Try)
            and any(isinstance(call, ast.Call)
                    and isinstance(call.func, ast.Attribute)
                    and ast.unparse(call.func) == "subprocess.Popen"
                    for call in ast.walk(node))
        ]
        ordered_environment = (
            len(copy_indexes) == 1 and len(filter_indexes) == 1
            and len(popen_statement_indexes) == 1
            and copy_indexes[0] < filter_indexes[0] < popen_statement_indexes[0]
        )
    return (len(command_assignments) == 1
            and ast.unparse(command_assignments[0].value) == expected_command
            and len(popen_calls) == 1 and bool(popen_calls[0].args)
            and isinstance(popen_calls[0].args[0], ast.Name)
            and popen_calls[0].args[0].id == "command"
            and sum(keyword.arg == "env" for keyword in popen_calls[0].keywords) == 1
            and any(keyword.arg == "env" and isinstance(keyword.value, ast.Name)
                    and keyword.value.id == "child_env"
                    for keyword in popen_calls[0].keywords)
            and ordered_environment)


def _target_worker_sysconfigdata_environment_fact(
        preconfig_source, initconfig_source, worker_source):
    """Bind removal of the direct sysconfig environment override in the child."""
    if (type(worker_source) is not bytes or not worker_source
            or len(worker_source) > MAX_WORKER_CONTROL_SOURCE_BYTES
            or hashlib.sha256(worker_source).hexdigest()
            != IMPORT_USED_BYTES_PROBE_SHA256):
        return ()
    try:
        tree = ast.parse(worker_source)
    except SyntaxError:
        return ()
    collectors = [node for node in tree.body
                  if isinstance(node, ast.FunctionDef)
                  and node.name == "_collect_process"]
    if (len(collectors) != 1 or not _target_isolated_worker_route_valid(
            preconfig_source, initconfig_source, worker_source)):
        return ()
    return (("_PYTHON_SYSCONFIGDATA_NAME", "absent_from_child_environment"),)


def _target_worker_warn_default_encoding_disabled(
        preconfig_header_source, preconfig_source, initconfig_source,
        worker_source):
    """Bind the default-false preconfig field to the exact isolated worker route."""
    sources = (
        (preconfig_header_source, PRECONFIG_HEADER_SHA256,
         MAX_PRECONFIG_HEADER_BYTES),
        (preconfig_source, PRECONFIG_C_SHA256, MAX_PRECONFIG_C_BYTES),
        (initconfig_source, INITCONFIG_C_SHA256, MAX_INITCONFIG_C_BYTES),
        (worker_source, IMPORT_USED_BYTES_PROBE_SHA256,
         MAX_WORKER_CONTROL_SOURCE_BYTES),
    )
    if (any(type(source) is not bytes or not source or len(source) > limit
            or hashlib.sha256(source).hexdigest() != digest
            for source, digest, limit in sources)
            or not _target_isolated_worker_route_valid(
                preconfig_source, initconfig_source, worker_source,
            )):
        return False
    header_text = preconfig_header_source.decode("utf-8")
    preconfig_text = preconfig_source.decode("utf-8")
    structures = re.findall(
        r"typedef struct\s*\{(.*?)\}\s*_PyPreCmdline;",
        header_text, re.DOTALL,
    )
    initializers = re.findall(
        r"#define _PyPreCmdline_INIT\s*\\\s*"
        r"\(_PyPreCmdline\)\s*\{(.*?)\}",
        header_text, re.DOTALL,
    )
    reads = re.findall(
        r"PyStatus\s+_PyPreCmdline_Read\(_PyPreCmdline \*cmdline,\s*"
        r"const PyPreConfig \*preconfig\)\s*\{(.*?)\n\}",
        preconfig_text, re.DOTALL,
    )
    set_configs = re.findall(
        r"PyStatus\s+_PyPreCmdline_SetConfig\(const _PyPreCmdline \*cmdline,\s*"
        r"PyConfig \*config\)\s*\{(.*?)\n\}",
        preconfig_text, re.DOTALL,
    )
    if (len(structures) != 1 or len(initializers) != 1
            or len(reads) != 1 or len(set_configs) != 1
            or not re.search(r"int\s+warn_default_encoding\s*;", structures[0])
            or re.search(r"warn_default_encoding", initializers[0])
            or not re.search(
                r"_PyPreCmdline_INIT sets other fields to 0/NULL",
                header_text,
            )
            or not re.search(
                r"if\s*\(\s*_Py_get_xoption\(&cmdline->xoptions,\s*"
                r"L\"warn_default_encoding\"\)\s*\|\|\s*"
                r"_Py_GetEnv\(cmdline->use_environment,\s*"
                r"\"PYTHONWARNDEFAULTENCODING\"\)\s*\)\s*\{\s*"
                r"cmdline->warn_default_encoding\s*=\s*1\s*;",
                reads[0],
            )
            or not re.search(r"COPY_ATTR\(warn_default_encoding\);", set_configs[0])):
        return False
    return True


def _target_worker_int_max_str_digits_default(
        long_header_source, preconfig_source, initconfig_source,
        sys_module_source, worker_source):
    """Bind the default int/string digit limit to the exact isolated worker."""
    sources = (
        (long_header_source, LONG_HEADER_SHA256, MAX_LONG_HEADER_BYTES),
        (preconfig_source, PRECONFIG_C_SHA256, MAX_PRECONFIG_C_BYTES),
        (initconfig_source, INITCONFIG_C_SHA256, MAX_INITCONFIG_C_BYTES),
        (sys_module_source, SYS_MODULE_C_SHA256, MAX_SYS_MODULE_C_BYTES),
        (worker_source, IMPORT_USED_BYTES_PROBE_SHA256,
         MAX_WORKER_CONTROL_SOURCE_BYTES),
    )
    if (any(type(source) is not bytes or not source or len(source) > limit
            or hashlib.sha256(source).hexdigest() != digest
            for source, digest, limit in sources)
            or not _target_isolated_worker_route_valid(
                preconfig_source, initconfig_source, worker_source,
            )):
        return False
    long_header_text = long_header_source.decode("utf-8")
    initconfig_text = initconfig_source.decode("utf-8")
    sys_module_text = sys_module_source.decode("utf-8")
    digit_init = re.findall(
        r"static PyStatus\s+config_init_int_max_str_digits"
        r"\(PyConfig \*config\)\s*\{(.*?)\n\}",
        initconfig_text, re.DOTALL,
    )
    if (len(re.findall(
            r"^#define _PY_LONG_DEFAULT_MAX_STR_DIGITS (\d+)$",
            long_header_text, re.MULTILINE,
    )) != 1
            or not re.search(
                r"^#define _PY_LONG_DEFAULT_MAX_STR_DIGITS 4300$",
                long_header_text, re.MULTILINE,
            )
            or len(digit_init) != 1
            or not re.search(
                r"config_get_env\(config, \"PYTHONINTMAXSTRDIGITS\"\)",
                digit_init[0],
            )
            or not re.search(
                r"config_get_xoption\(config, L\"int_max_str_digits\"\)",
                digit_init[0],
            )
            or not re.search(
                r"if \(config->int_max_str_digits < 0\)\s*\{\s*"
                r"config->int_max_str_digits = _PY_LONG_DEFAULT_MAX_STR_DIGITS;",
                digit_init[0],
            )
            or not re.search(
                r"if \(config->int_max_str_digits < 0\)\s*\{\s*"
                r"status = config_init_int_max_str_digits\(config\);",
                initconfig_text,
            )
            or not re.search(
                r"static int\s+set_flags_from_config\(.*?"
                r"SetFlag\(config->int_max_str_digits\);",
                sys_module_text, re.DOTALL,
            )):
        return False
    return True


def _target_worker_sys_flag_facts(
        preconfig_header_source, long_header_source, preconfig_source,
        initconfig_source,
        sys_module_source, worker_source):
    """Derive source-bound startup flags from the exact isolated worker route."""
    if (type(sys_module_source) is not bytes or not sys_module_source
            or len(sys_module_source) > MAX_SYS_MODULE_C_BYTES
            or hashlib.sha256(sys_module_source).hexdigest() != SYS_MODULE_C_SHA256
            or not _target_isolated_worker_route_valid(
                preconfig_source, initconfig_source, worker_source,
            )):
        return ()
    initconfig_text = initconfig_source.decode("utf-8")
    preconfig_text = preconfig_source.decode("utf-8")
    sys_module_text = sys_module_source.decode("utf-8")
    precmdline_reads = re.findall(
        r"PyStatus\s+_PyPreCmdline_Read\(_PyPreCmdline \*cmdline,\s*"
        r"const PyPreConfig \*preconfig\)\s*\{(.*?)\n\}",
        preconfig_text, re.DOTALL,
    )
    precmdline_set_configs = re.findall(
        r"PyStatus\s+_PyPreCmdline_SetConfig\(const _PyPreCmdline \*cmdline,\s*"
        r"PyConfig \*config\)\s*\{(.*?)\n\}",
        preconfig_text, re.DOTALL,
    )
    defaults = re.search(
        r"static void\s+config_init_defaults\(PyConfig \*config\)\s*\{(.*?)\n\}",
        initconfig_text, re.DOTALL,
    )
    fields = re.search(
        r"static PyStructSequence_Field flags_fields\[\] = \{(.*?)\n\};",
        sys_module_text, re.DOTALL,
    )
    expected_fields = (
        "debug", "inspect", "interactive", "optimize", "dont_write_bytecode",
        "no_user_site", "no_site", "ignore_environment", "verbose",
        "bytes_warning", "quiet", "hash_randomization", "isolated", "dev_mode",
        "utf8_mode", "warn_default_encoding", "safe_path", "int_max_str_digits",
    )
    actual_fields = tuple(re.findall(
        r'\{\s*"([a-z0-9_]+)"\s*,', fields.group(1),
    )) if fields else ()
    set_flags = re.search(
        r"static int\s+set_flags_from_config\(.*?\n\s*return 0;\n\}",
        sys_module_text, re.DOTALL,
    )
    update_configs = re.findall(
        r"int\s+_PySys_UpdateConfig\(PyThreadState \*tstate\)\s*\{(.*?)\n\}",
        sys_module_text, re.DOTALL,
    )
    update_config = update_configs[0] if len(update_configs) == 1 else None
    if (defaults is None or fields is None or actual_fields != expected_fields
            or set_flags is None or update_config is None
            or not re.search(r"config->optimization_level\s*=\s*0\s*;", defaults.group(1))
            or not re.search(
                r"case 'B':\s*config->write_bytecode\s*=\s*0\s*;",
                initconfig_text,
            )
            or not re.search(
                r"case 'S':\s*config->site_import\s*=\s*0\s*;",
                initconfig_text,
            )
            or not re.search(
                r"case 'O':\s*config->optimization_level\+\+\s*;",
                initconfig_text,
            )
            or not re.search(
                r"if \(config->isolated\)\s*\{\s*config->safe_path\s*=\s*1\s*;"
                r"\s*config->use_environment\s*=\s*0\s*;"
                r"\s*config->user_site_directory\s*=\s*0\s*;",
                initconfig_text,
            )
            or any(not re.search(pattern, defaults.group(1)) for pattern in (
                r"config->parser_debug\s*=\s*0\s*;",
                r"config->inspect\s*=\s*0\s*;",
                r"config->interactive\s*=\s*0\s*;",
                r"config->verbose\s*=\s*0\s*;",
                r"config->bytes_warning\s*=\s*0\s*;",
                r"config->quiet\s*=\s*0\s*;",
            ))
            or any(not re.search(pattern, initconfig_text) for pattern in (
                r"case 'd':\s*config->parser_debug\+\+\s*;",
                r"case 'i':\s*config->inspect\+\+\s*;\s*"
                r"config->interactive\+\+\s*;",
                r"case 'b':\s*config->bytes_warning\+\+\s*;",
                r"case 'v':\s*config->verbose\+\+\s*;",
                r"case 'q':\s*config->quiet\+\+\s*;",
            ))
            or not re.search(
                r"if\s*\(config->use_hash_seed\s*<\s*0\)\s*\{\s*"
                r"config->use_hash_seed\s*=\s*0\s*;\s*"
                r"config->hash_seed\s*=\s*0\s*;\s*\}",
                initconfig_text,
            )
            or not re.search(
                r"static const char\s*\*\s*config_get_env\("
                r"const PyConfig \*config, const char \*name\)\s*\{\s*"
                r"return _Py_GetEnv\(config->use_environment, name\);\s*\}",
                initconfig_text,
            )
            or not re.search(
                r"static PyStatus\s+config_init_hash_seed\(PyConfig \*config\)\s*"
                r"\{.*?const char \*seed_text = config_get_env\(config, "
                r'"PYTHONHASHSEED"\);.*?else\s*\{\s*'
                r"/\* Use a random hash \*/\s*"
                r"config->use_hash_seed\s*=\s*0\s*;\s*"
                r"config->hash_seed\s*=\s*0\s*;",
                initconfig_text, re.DOTALL,
            )
            or len(precmdline_reads) != 1
            or len(precmdline_set_configs) != 1
            or not re.search(
                r"if\s*\(cmdline->isolated\s*>\s*0\)\s*\{\s*"
                r"cmdline->use_environment\s*=\s*0\s*;\s*\}",
                precmdline_reads[0],
            )
            or not re.search(
                r"if\s*\(\s*\(cmdline->dev_mode\s*<\s*0\)\s*&&\s*"
                r"\(_Py_get_xoption\(&cmdline->xoptions,\s*L\"dev\"\)\s*\|\|\s*"
                r"_Py_GetEnv\(cmdline->use_environment,\s*\"PYTHONDEVMODE\"\)\)\s*\)\s*\{\s*"
                r"cmdline->dev_mode\s*=\s*1\s*;",
                precmdline_reads[0],
            )
            or not re.search(
                r"if\s*\(cmdline->dev_mode\s*<\s*0\)\s*\{\s*"
                r"cmdline->dev_mode\s*=\s*0\s*;\s*\}",
                precmdline_reads[0],
            )
            or not re.search(
                r"COPY_ATTR\(dev_mode\);",
                precmdline_set_configs[0],
            )):
        return ()
    flag_body = set_flags.group(0)
    update_body = update_config
    flags_update = re.search(
        r"if\s*\(set_flags_from_config\(interp,\s*flags\)\s*<\s*0\)\s*\{",
        update_body,
    )
    dont_write_bytecode = list(re.finditer(
        r'SET_SYS\("dont_write_bytecode",\s*'
        r"PyBool_FromLong\(!config->write_bytecode\)\);",
        update_body,
    ))
    if (flags_update is None or len(dont_write_bytecode) != 1
            or flags_update.start() >= dont_write_bytecode[0].start()):
        return ()
    required_bindings = (
        r"SetFlag\(config->optimization_level\);\s*"
        r"SetFlag\(!config->write_bytecode\);\s*"
        r"SetFlag\(!config->user_site_directory\);\s*"
        r"SetFlag\(!config->site_import\);\s*"
        r"SetFlag\(!config->use_environment\);",
        r"SetFlag\(config->isolated\);",
        r"SetFlagObj\(PyBool_FromLong\(config->safe_path\)\);",
        r"SetFlag\(config->parser_debug\);",
        r"SetFlag\(config->inspect\);",
        r"SetFlag\(config->interactive\);",
        r"SetFlag\(config->verbose\);",
        r"SetFlag\(config->bytes_warning\);",
        r"SetFlag\(config->quiet\);",
        r"SetFlag\(config->use_hash_seed\s*==\s*0\s*\|\|\s*"
        r"config->hash_seed\s*!=\s*0\);",
        r"SetFlagObj\(PyBool_FromLong\(config->dev_mode\)\);",
        r"SetFlag\(config->warn_default_encoding\);",
        r"SetFlag\(preconfig->utf8_mode\);",
    )
    if any(not re.search(pattern, flag_body) for pattern in required_bindings):
        return ()
    facts = (
        ("sys.flags.isolated", 1),
        ("sys.flags.no_site", 1),
        ("sys.flags.dont_write_bytecode", 1),
        ("sys.flags.ignore_environment", 1),
        ("sys.flags.safe_path", True),
        ("sys.flags.optimize", 0),
        ("sys.dont_write_bytecode", True),
        ("sys.flags.no_user_site", 1),
        ("sys.flags.debug", 0),
        ("sys.flags.inspect", 0),
        ("sys.flags.interactive", 0),
        ("sys.flags.verbose", 0),
        ("sys.flags.bytes_warning", 0),
        ("sys.flags.quiet", 0),
        ("sys.flags.hash_randomization", 1),
        ("sys.flags.dev_mode", False),
        ("sys.flags.utf8_mode", 1),
    )
    if _target_worker_warn_default_encoding_disabled(
            preconfig_header_source, preconfig_source, initconfig_source,
            worker_source):
        facts += (("sys.flags.warn_default_encoding", False),)
    if _target_worker_int_max_str_digits_default(
            long_header_source, preconfig_source, initconfig_source,
            sys_module_source, worker_source):
        facts += (("sys.flags.int_max_str_digits", 4300),)
    return facts


def _condition_fact_value_supported(value):
    if type(value) in (str, bool, int, type(None)):
        return True
    return (type(value) is tuple and len(value) <= 16
            and all(type(item) in (str, bool, int, type(None)) for item in value))


def _target_sys_implementation_info_body(sys_module_source):
    if (type(sys_module_source) is not bytes or not sys_module_source
            or len(sys_module_source) > MAX_SYS_MODULE_C_BYTES
            or hashlib.sha256(sys_module_source).hexdigest() != SYS_MODULE_C_SHA256):
        return None
    implementation = re.search(
        r"static PyObject\s*\*\s*make_impl_info\(PyObject \*version_info\)(.*?)"
        r"(?=\n#ifdef __EMSCRIPTEN__)",
        sys_module_source.decode("utf-8"), re.DOTALL,
    )
    return implementation.group(1) if implementation is not None else None


def _target_sys_implementation_version_fact(sys_module_source):
    """Bind CPython's implementation.version to the shared version_info object."""
    body = _target_sys_implementation_info_body(sys_module_source)
    if (body is None
            or not re.search(
                r'PyDict_SetItemString\(impl_info,\s*"version",\s*version_info\)',
                body,
            )
            or not re.search(
                r"version_info\s*=\s*make_version_info\(tstate\);.*?"
                r'SET_SYS\("version_info",\s*version_info\);.*?'
                r'SET_SYS\("implementation",\s*make_impl_info\(version_info\)\);',
                sys_module_source.decode("utf-8"), re.DOTALL,
            )):
        return ()
    return (("sys.implementation.version", (3, 12, 16, "final", 0)),)


def _target_s15_version_field_candidate(sys_module_source, version_fact):
    """Derive the three-part S15 version from pinned CPython version_info."""
    if (type(sys_module_source) is not bytes
            or version_fact != (
                ("sys.implementation.version", (3, 12, 16, "final", 0)),
            )
            or _target_sys_implementation_version_fact(sys_module_source)
            != version_fact):
        return {}
    return {
        "value": (3, 12, 16),
        "source_fact": "sys.implementation.version",
        "source_sha256": SYS_MODULE_C_SHA256,
        "version_info_object_shared": True,
        "runtime_version_claimed": False,
    }


def _target_sys_implementation_name_fact(sys_module_source):
    """Bind CPython's implementation.name to its pinned implementation constant."""
    body = _target_sys_implementation_info_body(sys_module_source)
    if (body is None
            or not re.search(
                r'#define NAME "cpython"\s+'
                r'const char \*_PySys_ImplName\s*=\s*NAME;',
                sys_module_source.decode("utf-8"),
            )
            or not re.search(
                r'PyUnicode_FromString\(_PySys_ImplName\).*?'
                r'PyDict_SetItemString\(impl_info,\s*"name",\s*value\)',
                body, re.DOTALL,
            )):
        return ()
    return (("sys.implementation.name", "cpython"),)


def _target_s15_implementation_field_candidate(sys_module_source, name_fact):
    """Bind the S15 implementation field to the pinned CPython source fact."""
    if (type(sys_module_source) is not bytes
            or name_fact != (("sys.implementation.name", "cpython"),)
            or _target_sys_implementation_name_fact(sys_module_source) != name_fact):
        return {}
    return {
        "value": "cpython",
        "source_fact": "sys.implementation.name",
        "source_sha256": SYS_MODULE_C_SHA256,
        "runtime_implementation_claimed": False,
    }


def _target_sys_implementation_cache_tag_fact(sys_module_source, version_fact):
    """Bind CPython's cache tag from its pinned macros and target version fact."""
    body = _target_sys_implementation_info_body(sys_module_source)
    if (version_fact != (("sys.implementation.version", (3, 12, 16, "final", 0)),)
            or body is None):
        return ()
    source = sys_module_source.decode("utf-8")
    macros = (
        r'#define NAME "cpython"\s+'
        r'const char \*_PySys_ImplName\s*=\s*NAME;\s+'
        r'#define MAJOR Py_STRINGIFY\(PY_MAJOR_VERSION\)\s+'
        r'#define MINOR Py_STRINGIFY\(PY_MINOR_VERSION\)\s+'
        r'#define TAG NAME "-" MAJOR MINOR\s+'
        r'const char \*_PySys_ImplCacheTag\s*=\s*TAG;'
    )
    if (not re.search(macros, source)
            or not re.search(
                r'PyUnicode_FromString\(_PySys_ImplCacheTag\).*?'
                r'PyDict_SetItemString\(impl_info,\s*"cache_tag",\s*value\)',
                body, re.DOTALL,
            )):
        return ()
    return (("sys.implementation.cache_tag", "cpython-312"),)


def _target_sys_implementation_multiarch_fact(sys_module_source, image_facts):
    """Bind sys.implementation._multiarch to the pinned image build value."""
    body = _target_sys_implementation_info_body(sys_module_source)
    if (body is None or type(image_facts) is not dict
            or image_facts.get("sysconfigdata_path") != TARGET_SYSCONFIGDATA_PATH
            or image_facts.get("sysconfigdata_sha256") != TARGET_SYSCONFIGDATA_SHA256
            or image_facts.get("multiarch") != "x86_64-linux-gnu"
            or not re.search(
                r"#ifdef MULTIARCH\s+"
                r"value = PyUnicode_FromString\(MULTIARCH\);\s+"
                r"if \(value == NULL\)\s+goto error;\s+"
                r"res = PyDict_SetItemString\(impl_info, \"_multiarch\", value\);\s+"
                r"Py_DECREF\(value\);\s+"
                r"if \(res < 0\)\s+goto error;\s+"
                r"#endif",
                body,
            )):
        return ()
    return (("sys.implementation._multiarch", image_facts["multiarch"]),)


def _target_sys_abiflags_fact(sys_module_source, image_facts):
    """Bind sys.abiflags to the pinned image's generated build variable."""
    if (type(sys_module_source) is not bytes or not sys_module_source
            or len(sys_module_source) > MAX_SYS_MODULE_C_BYTES
            or hashlib.sha256(sys_module_source).hexdigest() != SYS_MODULE_C_SHA256
            or type(image_facts) is not dict
            or image_facts.get("sysconfigdata_path") != TARGET_SYSCONFIGDATA_PATH
            or image_facts.get("sysconfigdata_sha256") != TARGET_SYSCONFIGDATA_SHA256
            or image_facts.get("abiflags") != ""):
        return ()
    source = sys_module_source.decode("utf-8")
    assignment = re.compile(
                r"#ifdef ABIFLAGS\s+"
                r'SET_SYS_FROM_STRING\("abiflags", ABIFLAGS\);\s+'
                r"#endif",
    )
    if len(assignment.findall(source)) != 1:
        return ()
    return (("sys.abiflags", image_facts["abiflags"]),)


def _target_sys_platform_fact(
        sys_module_source, getplatform_source, makefile_pre_source, image_facts):
    """Bind sys.platform through Py_GetPlatform and the target build rule."""
    sources = (
        (sys_module_source, SYS_MODULE_C_SHA256, MAX_SYS_MODULE_C_BYTES),
        (getplatform_source, GETPLATFORM_SOURCE_SHA256,
         MAX_GETPLATFORM_SOURCE_BYTES),
        (makefile_pre_source, MAKEFILE_PRE_SHA256, MAX_MAKEFILE_PRE_BYTES),
    )
    if (any(type(source) is not bytes or not source or len(source) > limit
            or hashlib.sha256(source).hexdigest() != digest
            for source, digest, limit in sources)
            or type(image_facts) is not dict
            or image_facts.get("sysconfigdata_path") != TARGET_SYSCONFIGDATA_PATH
            or image_facts.get("sysconfigdata_sha256") != TARGET_SYSCONFIGDATA_SHA256
            or image_facts.get("machdep") != "linux"):
        return ()
    sys_module_text = sys_module_source.decode("utf-8")
    getplatform_text = getplatform_source.decode("utf-8")
    makefile_text = makefile_pre_source.decode("utf-8")
    platform_call = 'SET_SYS_FROM_STRING("platform", Py_GetPlatform());'
    platform_rule = (
        "$(CC) -c $(PY_CORE_CFLAGS) -DPLATFORM='\"$(MACHDEP)\"' "
        "-o $@ $(srcdir)/Python/getplatform.c"
    )
    if (sys_module_text.count(platform_call) != 1
            or not re.search(
                r'#ifndef PLATFORM\s+#define PLATFORM "unknown"\s+#endif\s+'
                r"const char \*\s*Py_GetPlatform\(void\)\s*\{\s*return PLATFORM;\s*\}",
                getplatform_text,
            )
            or makefile_text.count(platform_rule) != 1):
        return ()
    return (("sys.platform", image_facts["machdep"]),)


def _target_s15_platform_field_candidate(platform_fact, image_facts):
    """Bind the S15 platform value to checked target build/source facts."""
    if (platform_fact != (("sys.platform", "linux"),)
            or type(image_facts) is not dict
            or image_facts.get("sysconfigdata_path") != TARGET_SYSCONFIGDATA_PATH
            or image_facts.get("sysconfigdata_sha256") != TARGET_SYSCONFIGDATA_SHA256
            or image_facts.get("machdep") != "linux"):
        return {}
    return {
        "value": "linux",
        "sys_platform_fact": "sys.platform",
        "build_value_key": "MACHDEP",
        "sysconfigdata_path": TARGET_SYSCONFIGDATA_PATH,
        "sysconfigdata_sha256": TARGET_SYSCONFIGDATA_SHA256,
        "sys_module_c_sha256": SYS_MODULE_C_SHA256,
        "getplatform_source_sha256": GETPLATFORM_SOURCE_SHA256,
        "makefile_pre_sha256": MAKEFILE_PRE_SHA256,
        "runtime_platform_claimed": False,
    }


def _target_sysconfigdata_module_name_fact(
        sysconfig_inventory, abiflags_fact, platform_fact, multiarch_fact,
        worker_environment_fact):
    """Compose the fixed sysconfigdata fallback name from bound target facts."""
    expected_template = "_sysconfigdata_{sys.abiflags}_{sys.platform}_{multiarch}"
    if (type(sysconfig_inventory) is not dict
            or sysconfig_inventory.get("source_sha256") != SYSCONFIG_SOURCE_SHA256
            or sysconfig_inventory.get("sysconfigdata_name_template")
            != expected_template):
        return ()
    facts = (abiflags_fact, platform_fact, multiarch_fact)
    expected_keys = (
        "sys.abiflags", "sys.platform", "sys.implementation._multiarch",
    )
    if any(type(fact) is not tuple or len(fact) != 1
           or type(fact[0]) is not tuple or len(fact[0]) != 2
           or fact[0][0] != key or type(fact[0][1]) is not str
           for fact, key in zip(facts, expected_keys)):
        return ()
    if (type(worker_environment_fact) is not tuple
            or worker_environment_fact != (
                ("_PYTHON_SYSCONFIGDATA_NAME", "absent_from_child_environment"),
            )):
        return ()
    abiflags, platform, multiarch = (fact[0][1] for fact in facts)
    name = "_sysconfigdata_{}_{}_{}".format(abiflags, platform, multiarch)
    return (("sysconfigdata.module_name", name),)


def _target_sysconfigdata_image_file_fact(module_name_fact, image_facts):
    """Match the composed module candidate to the digest-bound image member."""
    if (type(module_name_fact) is not tuple or len(module_name_fact) != 1
            or type(module_name_fact[0]) is not tuple
            or len(module_name_fact[0]) != 2
            or module_name_fact[0][0] != "sysconfigdata.module_name"
            or type(module_name_fact[0][1]) is not str
            or type(image_facts) is not dict
            or image_facts.get("sysconfigdata_path") != TARGET_SYSCONFIGDATA_PATH
            or image_facts.get("sysconfigdata_sha256") != TARGET_SYSCONFIGDATA_SHA256):
        return ()
    module_name = module_name_fact[0][1]
    image_basename = TARGET_SYSCONFIGDATA_PATH.rsplit("/", 1)[-1]
    if (not module_name.startswith("_sysconfigdata_")
            or "/" in module_name or "\\" in module_name or "." in module_name
            or image_basename != module_name + ".py"):
        return ()
    return (("sysconfigdata.image_file_path", TARGET_SYSCONFIGDATA_PATH),)


def _target_sysconfigdata_import_target_candidate(
        sysconfig_inventory, module_name_fact, image_file_fact):
    """Join the pinned dynamic import route to its matching image file candidate."""
    expected_template = "_sysconfigdata_{sys.abiflags}_{sys.platform}_{multiarch}"
    if (type(sysconfig_inventory) is not dict
            or sysconfig_inventory.get("source_sha256") != SYSCONFIG_SOURCE_SHA256
            or sysconfig_inventory.get("sysconfigdata_name_template")
            != expected_template
            or sysconfig_inventory.get("sysconfigdata_importer") != "__import__"
            or sysconfig_inventory.get("sysconfigdata_imported_attribute")
            != "build_time_vars"):
        return None
    if (type(module_name_fact) is not tuple or len(module_name_fact) != 1
            or type(module_name_fact[0]) is not tuple or len(module_name_fact[0]) != 2
            or module_name_fact[0][0] != "sysconfigdata.module_name"
            or type(module_name_fact[0][1]) is not str
            or type(image_file_fact) is not tuple or len(image_file_fact) != 1
            or type(image_file_fact[0]) is not tuple or len(image_file_fact[0]) != 2
            or image_file_fact[0][0] != "sysconfigdata.image_file_path"
            or image_file_fact[0][1] != TARGET_SYSCONFIGDATA_PATH
            or TARGET_SYSCONFIGDATA_PATH.rsplit("/", 1)[-1]
            != module_name_fact[0][1] + ".py"):
        return None
    return {
        "module_name": module_name_fact[0][1],
        "image_file_path": image_file_fact[0][1],
        "importer": "__import__",
        "imported_attribute": "build_time_vars",
        "evidence_scope": "STATIC_IMPORT_TARGET_CANDIDATE",
    }


def _target_sysconfigdata_initialization_route_candidate(
        sysconfig_inventory, lazy_initialization_call_candidate,
        reinitialization_candidate, public_config_value_flow_candidate,
        post_update_entries_candidate, initialization_complete_flag_candidate,
        posix_init_line_facts,
        import_target_candidate, image_facts):
    """Join the guarded POSIX initializer to its verified sysconfigdata file."""
    if (type(sysconfig_inventory) is not dict
            or sysconfig_inventory.get("source_sha256") != SYSCONFIG_SOURCE_SHA256
            or sysconfig_inventory.get("sysconfigdata_name_template")
            != "_sysconfigdata_{sys.abiflags}_{sys.platform}_{multiarch}"
            or sysconfig_inventory.get("sysconfigdata_importer") != "__import__"
            or sysconfig_inventory.get("sysconfigdata_imported_attribute")
            != "build_time_vars"
            or sysconfig_inventory.get("sysconfigdata_initializer_parameter")
            != "vars"
            or sysconfig_inventory.get("sysconfigdata_initializer_update_receiver")
            != "vars"
            or sysconfig_inventory.get("sysconfigdata_initializer_update_value")
            != "build_time_vars"
            or lazy_initialization_call_candidate != {
                "getter": "get_config_vars",
                "initial_config_vars": None,
                "initialization_flag": False,
                "outer_guard": "not _CONFIG_VARS_INITIALIZED",
                "lock": "_CONFIG_VARS_LOCK",
                "recheck_guard": "_CONFIG_VARS is None",
                "selected_call": "_init_config_vars()",
                "evidence_scope": "STATIC_LAZY_INITIALIZER_CALL_CANDIDATE",
            }
            or reinitialization_candidate != {
                "getter": "get_config_vars",
                "initialization_flag_initial_value": False,
                "first_call_guard": "not _CONFIG_VARS_INITIALIZED",
                "reinitialization_guard": (
                    "_CONFIG_VARS['base'] != os.path.normpath(sys.prefix)"
                ),
                "reinitialization_guard_is_runtime_dependent": True,
                "lock": "_CONFIG_VARS_LOCK",
                "actions_if_reinitialization_guard_true": [
                    "_CONFIG_VARS_INITIALIZED = False",
                    "_init_config_vars()",
                ],
                "evidence_scope": "STATIC_CONFIG_REINITIALIZATION_CANDIDATE",
            }
            or public_config_value_flow_candidate != {
                "public_mapping_api": "get_config_vars",
                "no_arguments_return": "_CONFIG_VARS",
                "arguments_return": "[_CONFIG_VARS.get(name) for name in args]",
                "single_value_api": "get_config_var",
                "single_value_return": "get_config_vars().get(name)",
                "evidence_scope": "STATIC_CONFIG_API_VALUE_FLOW_CANDIDATE",
            }
            or post_update_entries_candidate != {
                "mapping": "_CONFIG_VARS",
                "post_update_direct_overwrites": [],
                "post_update_customizer": "_osx_support.customize_config_vars",
                "customizer_guard": "sys.platform == 'darwin'",
                "customizer_selected": False,
                "entry_values": TARGET_SYSCONFIGDATA_EXPECTED_VALUES,
                "evidence_scope": "STATIC_POST_INIT_MAPPING_ENTRY_CANDIDATE",
            }
            or initialization_complete_flag_candidate != {
                "initializer": "sysconfig._init_config_vars",
                "flag": "_CONFIG_VARS_INITIALIZED",
                "initial_value": False,
                "completion_assignment": "_CONFIG_VARS_INITIALIZED = True",
                "assignment_is_final_statement": True,
                "evidence_scope": "STATIC_CONFIG_INITIALIZED_FLAG_CANDIDATE",
            }
            or type(posix_init_line_facts) is not dict
            or len(posix_init_line_facts) != 1
            or any(type(line) is not int or type(value) is not bool or not value
                   for line, value in posix_init_line_facts.items())
            or import_target_candidate != {
                "module_name": "_sysconfigdata__linux_x86_64-linux-gnu",
                "image_file_path": TARGET_SYSCONFIGDATA_PATH,
                "importer": "__import__",
                "imported_attribute": "build_time_vars",
                "evidence_scope": "STATIC_IMPORT_TARGET_CANDIDATE",
            }
            or type(image_facts) is not dict
            or image_facts.get("sysconfigdata_path") != TARGET_SYSCONFIGDATA_PATH
            or image_facts.get("sysconfigdata_sha256")
            != TARGET_SYSCONFIGDATA_SHA256
            or image_facts.get("build_time_vars_literal_dict") is not True
            or type(image_facts.get("build_time_vars_entry_count")) is not int
            or image_facts["build_time_vars_entry_count"] <= 0
            or any(image_facts.get(TARGET_SYSCONFIGDATA_FACT_FIELDS[key]) != value
                   for key, value in TARGET_SYSCONFIGDATA_EXPECTED_VALUES.items())):
        return None
    line = next(iter(posix_init_line_facts))
    return {
        "public_initializer_call_candidate": lazy_initialization_call_candidate,
        "reinitialization_candidate": reinitialization_candidate,
        "public_config_value_flow_candidate": public_config_value_flow_candidate,
        "post_update_entries_candidate": post_update_entries_candidate,
        "initialization_complete_flag_candidate": (
            initialization_complete_flag_candidate
        ),
        "public_config_api_entry_candidate": {
            "mapping": "_CONFIG_VARS",
            "get_config_vars_no_arguments_result": "_CONFIG_VARS",
            "get_config_var_lookup": "_CONFIG_VARS.get(name)",
            "known_entry_values": post_update_entries_candidate["entry_values"],
            "requires_no_intervening_mapping_mutation": True,
            "evidence_scope": "STATIC_CONFIG_API_ENTRY_VALUE_CANDIDATE",
        },
        "initializer": "sysconfig._init_config_vars",
        "guard": "os.name == 'posix'",
        "guard_source_line": line,
        "selected_call": "_init_posix(_CONFIG_VARS)",
        "importer": "__import__",
        "module_name": import_target_candidate["module_name"],
        "image_file_path": import_target_candidate["image_file_path"],
        "image_file_sha256": image_facts["sysconfigdata_sha256"],
        "image_attribute_candidate": {
            "attribute": "build_time_vars",
            "value_kind": "literal_dict",
            "entry_count": image_facts["build_time_vars_entry_count"],
            "evidence_scope": "STATIC_IMAGE_ATTRIBUTE_CANDIDATE",
        },
        "config_vars_update_candidate": {
            "source_attribute": "build_time_vars",
            "local_value_name": "build_time_vars",
            "initializer_parameter": "vars",
            "initializer_argument": "_CONFIG_VARS",
            "update_receiver": "vars",
            "target_mapping": "_CONFIG_VARS",
            "known_entry_values": {
                key: image_facts[TARGET_SYSCONFIGDATA_FACT_FIELDS[key]]
                for key in TARGET_SYSCONFIGDATA_EXPECTED_VALUES
            },
            "evidence_scope": "STATIC_CONFIG_MAPPING_UPDATE_CANDIDATE",
        },
        "imported_attribute": "build_time_vars",
        "value_consumer": "vars.update(build_time_vars)",
        "evidence_scope": "STATIC_CONDITIONAL_IMPORT_ROUTE_CANDIDATE",
    }


def _target_importlib_verbose_line_facts(
        files, preconfig_source, initconfig_source, worker_source):
    """Bind importlib's verbose guard across every pinned source call site."""
    source_bindings = (
        ("importlib/_bootstrap.py", IMPORTLIB_BOOTSTRAP_SOURCE_SHA256),
        ("importlib/_bootstrap_external.py", IMPORTLIB_EXTERNAL_SOURCE_SHA256),
        ("zipimport.py", ZIPIMPORT_SOURCE_SHA256),
    )
    if type(files) is not dict:
        return {}
    sources = {path: files.get(path) for path, _ in source_bindings}
    if (any(type(sources[path]) is not bytes
            or not sources[path] or len(sources[path]) > MAX_SOURCE_BYTES
            or hashlib.sha256(sources[path]).hexdigest() != digest
            for path, digest in source_bindings)
            or not _target_isolated_worker_route_valid(
                preconfig_source, initconfig_source, worker_source,
            )):
        return {}
    initconfig_text = initconfig_source.decode("utf-8")
    if (not re.search(r"config->verbose\s*=\s*0;", initconfig_text)
            or not re.search(r"case 'v':\s*config->verbose\+\+;", initconfig_text)
            or not re.search(
                r"config_read_env_vars\(PyConfig \*config\).*?"
                r"int use_env = config->use_environment;.*?"
                r"_Py_get_env_flag\(use_env, &config->verbose,\s*"
                r"\"PYTHONVERBOSE\"\);", initconfig_text, re.DOTALL,
            )):
        return {}
    reference_paths = {
        path for path, candidate in files.items()
        if type(candidate) is bytes and b"_verbose_message" in candidate
    }
    if reference_paths != {path for path, _ in source_bindings}:
        return {}
    trees = {}
    for path in reference_paths:
        try:
            trees[path] = ast.parse(sources[path], filename=path)
        except SyntaxError:
            return {}
    calls_by_path = {}
    for path, tree in trees.items():
        parents = {child: node for node in ast.walk(tree)
                   for child in ast.iter_child_nodes(node)}
        references = [
            node for node in ast.walk(tree)
            if (isinstance(node, ast.Name) and node.id == "_verbose_message")
            or (isinstance(node, ast.Attribute) and node.attr == "_verbose_message")
        ]
        for node in references:
            parent = parents.get(node)
            if not isinstance(parent, ast.Call) or parent.func is not node:
                return {}
        expected_name = (
            "_verbose_message" if path == "importlib/_bootstrap.py"
            else "_bootstrap._verbose_message"
        )
        calls = [node for node in ast.walk(tree)
                 if isinstance(node, ast.Call)
                 and ast.unparse(node.func) == expected_name]
        if not calls:
            return {}
        for call in calls:
            verbosity_keywords = [keyword for keyword in call.keywords
                                  if keyword.arg == "verbosity"]
            if (any(keyword.arg is None for keyword in call.keywords)
                    or len(verbosity_keywords) > 1
                    or any(keyword.arg not in ("verbosity",)
                           for keyword in call.keywords)):
                return {}
            if verbosity_keywords:
                value = verbosity_keywords[0].value
                if (not isinstance(value, ast.Constant)
                        or type(value.value) is not int or value.value < 1):
                    return {}
        calls_by_path[path] = calls
    bootstrap_tree = trees["importlib/_bootstrap.py"]
    functions = [node for node in bootstrap_tree.body
                 if isinstance(node, ast.FunctionDef)
                 and node.name == "_verbose_message"]
    guards = [node for node in ast.walk(functions[0])
              if isinstance(node, ast.If)
              and ast.unparse(node.test) == "sys.flags.verbose >= verbosity"] if len(functions) == 1 else []
    if (len(functions) != 1
            or len(calls_by_path["importlib/_bootstrap.py"]) != 1
            or len(calls_by_path["importlib/_bootstrap_external.py"]) != 14
            or len(calls_by_path["zipimport.py"]) != 7
            or len(calls_by_path["importlib/_bootstrap.py"][0].args) != 3
            or calls_by_path["importlib/_bootstrap.py"][0].keywords
            or len(functions[0].args.kwonlyargs) != 1
            or functions[0].args.kwonlyargs[0].arg != "verbosity"
            or len(functions[0].args.kw_defaults) != 1
            or not isinstance(functions[0].args.kw_defaults[0], ast.Constant)
            or type(functions[0].args.kw_defaults[0].value) is not int
            or functions[0].args.kw_defaults[0].value < 1):
        return {}
    if len(guards) != 1:
        return {}
    return {guards[0].lineno: False}


def _target_warning_options_empty_for_facts(
        files, preconfig_source, initconfig_source, worker_source):
    """Bind an empty warnings option loop to the pinned isolated worker argv."""
    warnings_source = files.get("warnings.py")
    if (type(warnings_source) is not bytes
            or len(warnings_source) > MAX_SOURCE_BYTES
            or hashlib.sha256(warnings_source).hexdigest() != WARNINGS_SOURCE_SHA256
            or not _target_isolated_worker_route_valid(
                preconfig_source, initconfig_source, worker_source,
            )):
        return {}
    initconfig_text = initconfig_source.decode("utf-8")
    if (not re.search(
            r"if \(config->use_environment\)\s*\{\s*status\s*=\s*"
            r"config_init_env_warnoptions\(config,\s*&env_warnoptions\);",
            initconfig_text,
        )
            or not re.search(
                r"case 'W':\s*status\s*=\s*PyWideStringList_Append\(warnoptions,\s*"
                r"_PyOS_optarg\);",
                initconfig_text,
            )):
        return {}
    try:
        warnings_tree = ast.parse(warnings_source, filename="warnings.py")
    except SyntaxError:
        return {}
    process_calls = [
        node for node in warnings_tree.body
        if isinstance(node, ast.Expr) and isinstance(node.value, ast.Call)
        and ast.unparse(node.value) == "_processoptions(sys.warnoptions)"
    ]
    process_functions = [
        node for node in warnings_tree.body
        if isinstance(node, ast.FunctionDef) and node.name == "_processoptions"
    ]
    if len(process_calls) != 1 or len(process_functions) != 1:
        return {}
    loops = [node for node in ast.walk(process_functions[0])
             if isinstance(node, ast.For) and ast.unparse(node.iter) == "args"]
    if len(loops) != 1:
        return {}
    return {"warnings": {loops[0].lineno: "args"}}


def _target_importlib_optimize_line_facts(
        files, preconfig_source, initconfig_source, worker_source):
    """Bind optimize==0 to the pinned isolated child argv and CPython defaults."""
    external_source = files.get("importlib/_bootstrap_external.py")
    sources = (
        (preconfig_source, PRECONFIG_C_SHA256, MAX_PRECONFIG_C_BYTES),
        (initconfig_source, INITCONFIG_C_SHA256, MAX_INITCONFIG_C_BYTES),
        (worker_source, IMPORT_USED_BYTES_PROBE_SHA256,
         MAX_WORKER_CONTROL_SOURCE_BYTES),
        (external_source, IMPORTLIB_EXTERNAL_SOURCE_SHA256, MAX_SOURCE_BYTES),
    )
    if any(type(source) is not bytes or not source or len(source) > limit
           or hashlib.sha256(source).hexdigest() != digest
           for source, digest, limit in sources):
        return {}
    if not _target_isolated_worker_route_valid(
            preconfig_source, initconfig_source, worker_source):
        return {}
    preconfig_text = preconfig_source.decode("utf-8")
    initconfig_text = initconfig_source.decode("utf-8")
    if (not re.search(
            r"case 'I':\s*cmdline->isolated\s*=\s*1;", preconfig_text
            )
            or not re.search(
                r"if \(config->isolated\)\s*\{[^}]*config->use_environment\s*=\s*0;",
                initconfig_text,
            )
            or not re.search(
                r"config->optimization_level\s*=\s*0;", initconfig_text,
            )
            or not re.search(
                r"case 'O':\s*config->optimization_level\+\+;", initconfig_text,
            )
            or not re.search(
                r"config_read_env_vars\(PyConfig \*config\).*?"
                r"int use_env = config->use_environment;.*?"
                r"_Py_get_env_flag\(use_env, &config->optimization_level,\s*"
                r"\"PYTHONOPTIMIZE\"\);", initconfig_text, re.DOTALL,
            )):
        return {}
    try:
        external_tree = ast.parse(external_source, filename="importlib/_bootstrap_external.py")
    except SyntaxError:
        return {}
    guards = [node for node in ast.walk(external_tree)
              if isinstance(node, ast.If)
              and ast.unparse(node.test) == "sys.flags.optimize == 0"]
    if len(guards) != 1:
        return {}
    return {guards[0].lineno: True}


def _target_importlib_debug_call_facts(optimize_line_facts):
    """Bind __debug__ only after the fixed route proves optimization is off."""
    if (type(optimize_line_facts) is not dict or not optimize_line_facts
            or any(type(line) is not int or line < 1 or type(value) is not bool
                   or not value for line, value in optimize_line_facts.items())):
        return ()
    return (("__debug__", True),)


def _target_imported_name_star_imports_safe(files, module):
    """Keep imported __name__ only across pinned star exports that exclude it."""
    bindings = {
        "dis": (DIS_SOURCE_SHA256, "opcode", OPCODE_SOURCE_SHA256),
        "tokenize": (TOKENIZE_SOURCE_SHA256, "token", TOKEN_SOURCE_SHA256),
    }
    binding = bindings.get(module)
    if binding is None:
        return False
    importer_digest, exporter_name, exporter_digest = binding
    importer_path = module + ".py"
    exporter_path = exporter_name + ".py"
    importer = files.get(importer_path)
    exporter = files.get(exporter_path)
    if (type(importer) is not bytes or hashlib.sha256(importer).hexdigest() != importer_digest
            or type(exporter) is not bytes
            or hashlib.sha256(exporter).hexdigest() != exporter_digest):
        return False
    importer_tree = ast.parse(importer, filename=importer_path)
    star_imports = [
        statement for statement in importer_tree.body
        if isinstance(statement, ast.ImportFrom)
        and any(alias.name == "*" for alias in statement.names)
    ]
    if (len(star_imports) != 1 or star_imports[0].module != exporter_name
            or star_imports[0].level != 0):
        return False
    exporter_tree = ast.parse(exporter, filename=exporter_path)
    exports = [
        statement for statement in exporter_tree.body if isinstance(statement, ast.Assign)
        and any(isinstance(target, ast.Name) and target.id == "__all__"
                for target in statement.targets)
    ]
    stores = [
        node for node in ast.walk(exporter_tree)
        if isinstance(node, ast.Name) and node.id == "__all__"
        and isinstance(node.ctx, (ast.Store, ast.Del))
    ]
    if len(exports) != 1 or len(stores) != 1:
        return False
    try:
        exported_names = ast.literal_eval(exports[0].value)
    except (ValueError, TypeError):
        return False
    return (type(exported_names) is list
            and all(type(name) is str for name in exported_names)
            and "__name__" not in exported_names)


_TARGET_PLAIN_MAIN_GUARD_SOURCE_DIGESTS = {
    "difflib": "3eb2d371b4a171b063921de6bbf115108bc39de8bf72866315868ce2599213b7",
    "getopt": "0ce875700c8798193b8e2748f7a27fc542cc4d525a1e6fc403767450ec92be99",
    "heapq": "6d43277e5c76fc0f073cd388fcff852d14d068f6bb6d4886c340f8b75a1229a9",
    "pickle": "7e3447b6d993a6306a7893fd2fba916010ed79f8e09ceb56158a550fa8099a14",
    "textwrap": "62867e40cdea6669b361f72af4d7daf0359f207c92cbeddfc7c7506397c1f31c",
}


def _target_plain_main_guard_name_safe(files, module):
    """Prove pinned, simple stdlib modules do not rebind their import name."""
    expected = _TARGET_PLAIN_MAIN_GUARD_SOURCE_DIGESTS.get(module)
    source = files.get(module + ".py")
    if (expected is None or type(source) is not bytes
            or hashlib.sha256(source).hexdigest() != expected):
        return False
    tree = ast.parse(source, filename=module + ".py")
    for node in ast.walk(tree):
        if isinstance(node, ast.Name) and node.id == "__name__":
            if isinstance(node.ctx, (ast.Store, ast.Del)):
                return False
        if (isinstance(node, ast.Name)
                and node.id in {"globals", "locals", "vars", "exec", "eval"}):
            return False
        if (isinstance(node, ast.Attribute)
                and node.attr in {"globals", "locals", "vars", "exec", "eval"}):
            return False
    return True


def _target_ast_imported_name_star_import_safe(files, ast_c_source):
    """Prove `_ast`'s default star exports cannot replace ast.__name__."""
    importer = files.get("ast.py")
    if (type(importer) is not bytes
            or hashlib.sha256(importer).hexdigest() != _AST_SOURCE_SHA256
            or type(ast_c_source) is not bytes
            or hashlib.sha256(ast_c_source).hexdigest() != AST_C_SHA256
            or b"__all__" in ast_c_source):
        return False
    tree = ast.parse(importer, filename="ast.py")
    star_imports = [
        statement for statement in tree.body if isinstance(statement, ast.ImportFrom)
        and any(alias.name == "*" for alias in statement.names)
    ]
    if (len(star_imports) != 1 or star_imports[0].module != "_ast"
            or star_imports[0].level != 0
            or any(isinstance(node, ast.Name) and node.id == "__name__"
                   and isinstance(node.ctx, (ast.Store, ast.Del))
                   for node in ast.walk(tree))):
        return False
    parents = {}
    for parent in ast.walk(tree):
        for child in ast.iter_child_nodes(parent):
            parents[child] = parent
    for node in ast.walk(tree):
        if (isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
                and node.func.id in {"exec", "eval", "locals", "vars"}):
            return False
        if not (isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
                and node.func.id == "globals"):
            continue
        ancestor = node
        function_scope = False
        comprehension = None
        while ancestor in parents:
            ancestor = parents[ancestor]
            if isinstance(ancestor, (ast.FunctionDef, ast.AsyncFunctionDef)):
                function_scope = True
                break
            if isinstance(ancestor, ast.DictComp):
                comprehension = ancestor
                break
        if function_scope:
            continue
        attr_call = parents.get(parents.get(node))
        if (comprehension is None or not isinstance(attr_call, ast.Call)
                or not isinstance(attr_call.func, ast.Attribute)
                or attr_call.func.attr != "pop" or attr_call.func.value is not node
                or len(attr_call.args) != 1
                or not isinstance(attr_call.args[0], ast.Name)
                or attr_call.args[0].id != "name"):
            return False
        if not isinstance(comprehension, ast.DictComp) or not isinstance(
                comprehension.generators[0].iter, (ast.Tuple, ast.List)):
            return False
        try:
            names = ast.literal_eval(comprehension.generators[0].iter)
        except (ValueError, TypeError):
            return False
        if (type(names) not in (tuple, list)
                or any(type(name) is not str for name in names)
                or "__name__" in names):
            return False
    return True


def _target_inspect_imported_name_safe(files):
    """Prove inspect's module-level globals access cannot replace __name__."""
    source = files.get("inspect.py")
    if (type(source) is not bytes
            or hashlib.sha256(source).hexdigest() != _INSPECT_SOURCE_SHA256):
        return False
    tree = ast.parse(source, filename="inspect.py")
    if any(isinstance(node, ast.Name) and node.id == "__name__"
           and isinstance(node.ctx, (ast.Store, ast.Del)) for node in ast.walk(tree)):
        return False
    parents = {}
    for parent in ast.walk(tree):
        for child in ast.iter_child_nodes(parent):
            parents[child] = parent
    module_globals_calls = []
    for node in ast.walk(tree):
        if not (isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
                and node.func.id in {"exec", "eval", "globals", "locals", "vars"}):
            continue
        ancestor = node
        in_function = False
        while ancestor in parents:
            ancestor = parents[ancestor]
            if isinstance(ancestor, (ast.FunctionDef, ast.AsyncFunctionDef)):
                in_function = True
                break
        if in_function:
            continue
        if node.func.id != "globals":
            return False
        module_globals_calls.append(node)
    if len(module_globals_calls) != 1:
        return False
    call = module_globals_calls[0]
    assignment = parents.get(call)
    if (not isinstance(assignment, ast.Assign) or len(assignment.targets) != 1
            or not isinstance(assignment.targets[0], ast.Name)
            or assignment.targets[0].id != "mod_dict"):
        return False
    module_name_writes = [
        node for node in ast.walk(tree)
        if isinstance(node, ast.Subscript) and isinstance(node.ctx, ast.Store)
        and isinstance(node.value, ast.Name) and node.value.id == "mod_dict"
        and isinstance(node.slice, ast.Constant) and node.slice.value == "__name__"
    ]
    if module_name_writes:
        return False
    compiler_flags_loop = [
        node for node in tree.body if isinstance(node, ast.For)
        and ast.unparse(node) == (
            "for k, v in dis.COMPILER_FLAG_NAMES.items():\n"
            "    mod_dict['CO_' + v] = k"
        )
    ]
    return len(compiler_flags_loop) == 1


def _target_sysconfig_imported_name_safe(files):
    """Resolve sysconfig's imported module name when dynamic access is deferred."""
    source = files.get("sysconfig.py")
    if (type(source) is not bytes
            or hashlib.sha256(source).hexdigest() != SYSCONFIG_SOURCE_SHA256):
        return False
    tree = ast.parse(source, filename="sysconfig.py")
    if any(isinstance(node, ast.Name) and node.id == "__name__"
           and isinstance(node.ctx, (ast.Store, ast.Del)) for node in ast.walk(tree)):
        return False
    guards = [node for node in tree.body if isinstance(node, ast.If)
              and ast.unparse(node.test) == "__name__ == '__main__'"]
    if len(guards) != 1:
        return False
    parents = {child: parent for parent in ast.walk(tree)
               for child in ast.iter_child_nodes(parent)}
    dynamic_functions = set()
    for node in ast.walk(tree):
        if not (isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
                and node.func.id in {"exec", "eval", "globals", "locals", "vars"}):
            continue
        ancestor = node
        while ancestor in parents and not isinstance(
                parents[ancestor], (ast.FunctionDef, ast.AsyncFunctionDef)):
            ancestor = parents[ancestor]
        if (ancestor not in parents or not isinstance(
                parents[ancestor], (ast.FunctionDef, ast.AsyncFunctionDef))):
            return False
        dynamic_functions.add(parents[ancestor].name)
    guard_line = guards[0].lineno
    for node in ast.walk(tree):
        if (isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
                and node.func.id in dynamic_functions and node.lineno < guard_line):
            ancestor = node
            while ancestor in parents and not isinstance(
                    parents[ancestor], (ast.FunctionDef, ast.AsyncFunctionDef)):
                ancestor = parents[ancestor]
            if (ancestor not in parents or not isinstance(
                    parents[ancestor], (ast.FunctionDef, ast.AsyncFunctionDef))):
                return False
    return True


def _target_os_posix_name_facts(files, posix_source, clinic_source):
    """Bind os.name only when the pinned posix star export cannot replace it."""
    source = files.get("os.py")
    if (type(source) is not bytes
            or hashlib.sha256(source).hexdigest() != OS_SOURCE_SHA256
            or type(posix_source) is not bytes
            or hashlib.sha256(posix_source).hexdigest() != POSIX_MODULE_C_SHA256
            or type(clinic_source) is not bytes
            or hashlib.sha256(clinic_source).hexdigest() != POSIX_MODULE_CLINIC_SHA256
            or _TARGET_BUILTIN_MEMBERSHIP.get("posix") is not True
            or _TARGET_BUILTIN_MEMBERSHIP.get("nt") is not False):
        return {}
    tree = ast.parse(source, filename="os.py")
    sys_imports = [
        alias for statement in tree.body if isinstance(statement, ast.Import)
        for alias in statement.names if alias.name == "sys"
    ]
    if (len(sys_imports) != 1 or sys_imports[0].asname is not None
            or any(isinstance(node, ast.Name) and node.id == "sys"
                   and isinstance(node.ctx, (ast.Store, ast.Del))
                   for node in ast.walk(tree))):
        return {}
    names_assignments = [
        statement for statement in tree.body if isinstance(statement, ast.Assign)
        and any(isinstance(target, ast.Name) and target.id == "_names"
                for target in statement.targets)
    ]
    selector = next((statement for statement in tree.body if isinstance(statement, ast.If)
                     and ast.unparse(statement.test) == "'posix' in _names"), None)
    alternate = selector.orelse[0] if selector and selector.orelse else None
    if (len(names_assignments) != 1
            or ast.unparse(names_assignments[0].value) != "sys.builtin_module_names"
            or not isinstance(alternate, ast.If)
            or ast.unparse(alternate.test) != "'nt' in _names"):
        return {}
    name_assignments = [
        node for node in ast.walk(tree)
        if isinstance(node, ast.Name) and node.id == "name"
        and isinstance(node.ctx, ast.Store)
    ]
    parents = {child: parent for parent in ast.walk(tree)
               for child in ast.iter_child_nodes(parent)}
    module_name_assignments = []
    for node in name_assignments:
        ancestor = node
        while ancestor in parents and not isinstance(
                parents[ancestor], (ast.FunctionDef, ast.AsyncFunctionDef)):
            ancestor = parents[ancestor]
        if not (ancestor in parents and isinstance(
                parents[ancestor], (ast.FunctionDef, ast.AsyncFunctionDef))):
            module_name_assignments.append(node)
    if len(module_name_assignments) != 2:
        return {}

    def assignment_value(block, expected):
        return any(isinstance(statement, ast.Assign)
                   and any(isinstance(target, ast.Name) and target.id == "name"
                           for target in statement.targets)
                   and isinstance(statement.value, ast.Constant)
                   and statement.value.value == expected
                   for statement in block)

    star_imports = [
        statement for statement in selector.body if isinstance(statement, ast.ImportFrom)
        and any(alias.name == "*" for alias in statement.names)
    ]
    if (not assignment_value(selector.body, "posix")
            or not assignment_value(alternate.body, "nt")
            or len(star_imports) != 1 or star_imports[0].module != "posix"
            or star_imports[0].level != 0):
        return {}
    posix_text = posix_source.decode("utf-8")
    clinic_text = clinic_source.decode("utf-8")
    if ("__all__" in posix_text or "__all__" in clinic_text
            or posix_text.count('"name"') != 1
            or not re.search(
                r'static PyMemberDef DirEntry_members\[\] = \{\s*\{"name",',
                posix_text,
            )
            or clinic_text.count('"name"') != 2
            or not re.search(
                r'static const char \* const _keywords\[\] = \{"name", "flags", NULL\};'
                r'\s*static _PyArg_Parser _parser = \{\s*\.keywords = _keywords,\s*'
                r'\.fname = "memfd_create"',
                clinic_text,
            )
            or not re.search(
                r'static const char \* const _keywords\[\] = \{"path", "name", NULL\};'
                r'\s*static _PyArg_Parser _parser = \{\s*\.keywords = _keywords,\s*'
                r'\.fname = "pathconf"',
                clinic_text,
            )
            or not re.search(r"static PyMethodDef posix_methods\[\] = \{", posix_text)
            or not re.search(r"\.m_methods = posix_methods", posix_text)):
        return {}
    return {"name": "posix"}


def _target_os_fspath_call_facts(files, posix_source, clinic_source):
    """Prove the Linux posix star export leaves os.fspath for the Python fallback."""
    source = files.get("os.py")
    if (not _target_os_posix_name_facts(files, posix_source, clinic_source)
            or type(source) is not bytes):
        return ()
    tree = ast.parse(source, filename="os.py")
    guard = [node for node in tree.body if isinstance(node, ast.If)
             and ast.unparse(node.test) == "not _exists('fspath')"]
    exists_functions = [node for node in tree.body
                        if isinstance(node, ast.FunctionDef) and node.name == "_exists"]
    if (len(guard) != 1 or len(exists_functions) != 1
            or ast.unparse(exists_functions[0].body[0]) != "return name in globals()"
            or any(isinstance(node, ast.Name) and node.id == "_exists"
                   and isinstance(node.ctx, (ast.Store, ast.Del))
                   for node in ast.walk(tree))):
        return ()
    if any(isinstance(node, ast.Name) and node.id == "fspath"
           and isinstance(node.ctx, ast.Store) and node.lineno < guard[0].lineno
           for node in ast.walk(tree)):
        return ()
    posix_text = posix_source.decode("utf-8")
    clinic_text = clinic_source.decode("utf-8")
    method_macro = "OS_FSPATH_METHODDEF"
    clinic_lines = clinic_text.splitlines()
    method_index = next((i for i, line in enumerate(clinic_lines)
                         if line.startswith(f"#define {method_macro}")), None)
    if (method_index is None or method_index + 1 >= len(clinic_lines)
            or '"fspath"' not in clinic_lines[method_index + 1]
            or not re.search(r"(?m)^\s*OS_FSPATH_METHODDEF$", posix_text)
            or not re.search(r"(?m)^static PyMethodDef posix_methods\[\] = \{", posix_text)
            or not re.search(r"\.m_methods = posix_methods", posix_text)):
        return ()
    return (("_exists('fspath')", True),)


def _target_os_posix_boolean_assignment_facts(files, posix_source, clinic_source):
    """Propagate a digest-bound os.name expression into its next guard."""
    source = files.get("os.py")
    if (not _target_os_posix_name_facts(files, posix_source, clinic_source)
            or type(source) is not bytes):
        return {}
    tree = ast.parse(source, filename="os.py")
    assignments = [
        node for node in tree.body
        if isinstance(node, ast.Assign)
        and any(isinstance(target, ast.Name)
                and target.id == "supports_bytes_environ"
                for target in node.targets)
    ]
    if (len(assignments) != 1
            or ast.unparse(assignments[0].value) != "name != 'nt'"
            or not any(isinstance(node, ast.If)
                       and ast.unparse(node.test) == "supports_bytes_environ"
                       and node.lineno > assignments[0].lineno
                       for node in tree.body)
            or any(isinstance(node, ast.Name)
                   and node.id == "supports_bytes_environ"
                   and isinstance(node.ctx, (ast.Store, ast.Del))
                   and node.lineno > assignments[0].lineno
                   for node in ast.walk(tree))):
        return {}
    return {"supports_bytes_environ": True}


def _target_os_function_name_facts_safe(files, facts):
    """Keep the post-star bytes-environ assignment through pinned functions."""
    if facts != {"supports_bytes_environ": True}:
        return False
    source = files.get("os.py")
    if (type(source) is not bytes
            or hashlib.sha256(source).hexdigest() != OS_SOURCE_SHA256):
        return False
    tree = ast.parse(source, filename="os.py")
    parents = {child: parent for parent in ast.walk(tree)
               for child in ast.iter_child_nodes(parent)}
    stores = [node for node in ast.walk(tree)
              if isinstance(node, ast.Name) and node.id == "supports_bytes_environ"
              and isinstance(node.ctx, (ast.Store, ast.Del))]
    if len(stores) != 1:
        return False
    ancestor = stores[0]
    while ancestor in parents:
        ancestor = parents[ancestor]
        if isinstance(ancestor, (ast.FunctionDef, ast.AsyncFunctionDef)):
            return False
    for node in ast.walk(tree):
        if isinstance(node, ast.arg) and node.arg == "supports_bytes_environ":
            return False
        if (isinstance(node, (ast.Global, ast.Nonlocal))
                and "supports_bytes_environ" in node.names):
            return False
        if ((isinstance(node, ast.Name) and node.id in {
                "exec", "eval", "locals", "vars"})
                or (isinstance(node, ast.Attribute) and node.attr in {
                    "exec", "eval", "locals", "vars"})):
            return False
    globals_calls = [node for node in ast.walk(tree)
                     if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
                     and node.func.id == "globals"]
    if len(globals_calls) != 2:
        return False
    exists = [node for node in tree.body if isinstance(node, ast.FunctionDef)
              and node.name == "_exists"]
    global_assignments = [node for node in ast.walk(tree) if isinstance(node, ast.Assign)
                          and any(isinstance(target, ast.Name)
                                  and target.id == "_globals"
                                  for target in node.targets)]
    if (len(exists) != 1 or ast.unparse(exists[0].body[0])
            != "return name in globals()" or len(global_assignments) != 1
            or ast.unparse(global_assignments[0].value) != "globals()"):
        return False
    for node in ast.walk(tree):
        if isinstance(node, ast.Name) and node.id == "_globals":
            if isinstance(node.ctx, ast.Store) and node is not global_assignments[0].targets[0]:
                return False
            if isinstance(node.ctx, ast.Del):
                ancestor = node
                while ancestor in parents:
                    ancestor = parents[ancestor]
                    if isinstance(ancestor, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        return False
                if node.lineno < global_assignments[0].lineno:
                    return False
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
            if isinstance(node.func.value, ast.Name) and node.func.value.id == "_globals":
                return False
        if isinstance(node, ast.Subscript) and isinstance(node.ctx, (ast.Store, ast.Del)):
            if isinstance(node.value, ast.Name) and node.value.id == "_globals":
                return False
    return True


def _target_os_createenviron_line_facts(files, facts):
    """Bind only os._createenviron's non-shadowed target-name comparison."""
    source = files.get("os.py")
    if (not isinstance(facts, dict) or facts.get("name") != "posix"
            or type(source) is not bytes
            or hashlib.sha256(source).hexdigest() != OS_SOURCE_SHA256):
        return {}
    tree = ast.parse(source, filename="os.py")
    functions = [node for node in tree.body if isinstance(node, ast.FunctionDef)
                 and node.name == "_createenviron"]
    if len(functions) != 1:
        return {}
    function = functions[0]
    arguments = (*function.args.posonlyargs, *function.args.args,
                 *function.args.kwonlyargs)
    if (arguments or function.args.vararg is not None or function.args.kwarg is not None
            or any(isinstance(node, ast.Name) and node.id == "name"
                   and isinstance(node.ctx, (ast.Store, ast.Del))
                   for node in ast.walk(function))
            or any(isinstance(node, (ast.Global, ast.Nonlocal)) and "name" in node.names
                   for node in ast.walk(function))):
        return {}
    guards = [node for node in function.body if isinstance(node, ast.If)
              and ast.unparse(node.test) == "name == 'nt'"]
    return {guards[0].lineno: False} if len(guards) == 1 else {}


_CODECS_SOURCE_SHA256 = (
    "7b7839e53a77961153240aecfe11edc8054d05b1dedd83894450dae21ec05785"
)


def _target_codecs_false_guard_line_facts(files):
    """Bind codecs' dead encodings import after its fixed `_false = 0` assignment."""
    source = files.get("codecs.py")
    if (type(source) is not bytes
            or hashlib.sha256(source).hexdigest() != _CODECS_SOURCE_SHA256):
        return {}
    tree = ast.parse(source, filename="codecs.py")
    star_imports = [node for node in ast.walk(tree)
                    if isinstance(node, ast.ImportFrom)
                    and any(alias.name == "*" for alias in node.names)]
    assignments = [node for node in tree.body if isinstance(node, ast.Assign)
                   and any(isinstance(target, ast.Name) and target.id == "_false"
                           for target in node.targets)]
    guards = [node for node in tree.body if isinstance(node, ast.If)
              and ast.unparse(node.test) == "_false"]
    stores = [node for node in ast.walk(tree)
              if isinstance(node, ast.Name) and node.id == "_false"
              and isinstance(node.ctx, (ast.Store, ast.Del))]
    if (len(star_imports) != 1 or star_imports[0].module != "_codecs"
            or star_imports[0].level != 0 or len(assignments) != 1
            or not isinstance(assignments[0].value, ast.Constant)
            or type(assignments[0].value.value) is not int
            or assignments[0].value.value != 0 or len(guards) != 1
            or len(stores) != 1 or guards[0].lineno <= assignments[0].lineno
            or guards[0].orelse or len(guards[0].body) != 1
            or not isinstance(guards[0].body[0], ast.Import)
            or [alias.name for alias in guards[0].body[0].names] != ["encodings"]):
        return {}
    return {guards[0].lineno: False}


def _target_pickle_buffer_line_facts(files, pickle_module_c_source,
                                     target_image_facts):
    """Bind pickle's feature guard to the exact source and present target extension."""
    source = files.get("pickle.py")
    if (type(source) is not bytes
            or hashlib.sha256(source).hexdigest() != PICKLE_SOURCE_SHA256
            or type(pickle_module_c_source) is not bytes
            or hashlib.sha256(pickle_module_c_source).hexdigest()
            != PICKLE_MODULE_C_SHA256
            or target_image_facts.get("_pickle_extension") is not True):
        return {}
    c_text = pickle_module_c_source.decode("utf-8")
    if ("/* Add types */\n    if (PyModule_AddType(m, &PyPickleBuffer_Type) < 0) {"
            not in c_text):
        return {}
    tree = ast.parse(source, filename="pickle.py")
    guards = [node for node in ast.walk(tree) if isinstance(node, ast.If)
              and ast.unparse(node.test) == "_HAVE_PICKLE_BUFFER"]
    import_guards = [node for node in tree.body if isinstance(node, ast.Try)
                     and any(isinstance(item, ast.ImportFrom)
                             and item.module == "_pickle"
                             and [alias.name for alias in item.names] == ["PickleBuffer"]
                             for item in node.body)]
    guard_classes = [node for node in ast.walk(tree)
                     if isinstance(node, ast.ClassDef) and guards
                     and guards[0] in node.body]
    if (len(guards) != 1 or len(import_guards) != 1 or len(guard_classes) != 1
            or not any(isinstance(node, ast.Assign)
                       and any(isinstance(target, ast.Name)
                               and target.id == "_HAVE_PICKLE_BUFFER"
                               for target in node.targets)
                       and isinstance(node.value, ast.Constant)
                       and node.value.value is True
                       for node in import_guards[0].body)
            or not any(isinstance(handler, ast.ExceptHandler)
                       and handler.type is not None
                       and ast.unparse(handler.type) == "ImportError"
                       and any(isinstance(node, ast.Assign)
                               and any(isinstance(target, ast.Name)
                                       and target.id == "_HAVE_PICKLE_BUFFER"
                                       for target in node.targets)
                               and isinstance(node.value, ast.Constant)
                               and node.value.value is False
                               for node in handler.body)
                       for handler in import_guards[0].handlers)):
        return {}
    return {guards[0].lineno: True}


def _target_importlib_case_platform_facts(files):
    """Resolve the two pinned case-sensitivity checks for the Linux target."""
    source = files.get("importlib/_bootstrap_external.py")
    if (type(source) is not bytes
            or hashlib.sha256(source).hexdigest() != IMPORTLIB_EXTERNAL_SOURCE_SHA256):
        return ()
    tree = ast.parse(source, filename="importlib/_bootstrap_external.py")
    expected = {
        "_CASE_INSENSITIVE_PLATFORMS_STR_KEY": ("win",),
        "_CASE_INSENSITIVE_PLATFORMS_BYTES_KEY": ("cygwin", "darwin"),
    }
    tracked_names = {*expected, "_CASE_INSENSITIVE_PLATFORMS"}
    assignments = {}
    for node in tree.body:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id in tracked_names:
                    assignments.setdefault(target.id, []).append(node.value)
    for name, value in expected.items():
        if len(assignments.get(name, ())) != 1:
            return ()
        try:
            if ast.literal_eval(assignments[name][0]) != value:
                return ()
        except (ValueError, TypeError):
            return ()
    combined = assignments.get("_CASE_INSENSITIVE_PLATFORMS", ())
    if (len(combined) != 1 or ast.unparse(combined[0])
            != "_CASE_INSENSITIVE_PLATFORMS_BYTES_KEY + _CASE_INSENSITIVE_PLATFORMS_STR_KEY"):
        return ()
    functions = [node for node in tree.body if isinstance(node, ast.FunctionDef)
                 and node.name == "_make_relax_case"]
    calls = ({ast.unparse(node.test) for node in ast.walk(functions[0])
              if isinstance(node, ast.If)} if len(functions) == 1 else set())
    facts = (
        ("sys.platform.startswith(_CASE_INSENSITIVE_PLATFORMS)", False),
        ("sys.platform.startswith(_CASE_INSENSITIVE_PLATFORMS_STR_KEY)", False),
    )
    return facts if {item[0] for item in facts} <= calls else ()


def _target_os_have_functions_call_facts(files, posix_source, clinic_source):
    """Prove posixmodule_exec always publishes os.py's feature inventory."""
    source = files.get("os.py")
    if (not _target_os_posix_name_facts(files, posix_source, clinic_source)
            or type(source) is not bytes):
        return ()
    tree = ast.parse(source, filename="os.py")
    imports = [
        node for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom) and node.module == "posix"
        and any(alias.name == "_have_functions" and alias.asname is None
                for alias in node.names)
    ]
    if (len(imports) != 1
            or not any(isinstance(node, ast.If)
                       and ast.unparse(node.test) == "_exists('_have_functions')"
                       for node in tree.body)
            or not any(isinstance(node, ast.FunctionDef) and node.name == "_exists"
                       and ast.unparse(node.body[0]) == "return name in globals()"
                       for node in tree.body)):
        return ()
    posix_text = posix_source.decode("utf-8")
    if (not re.search(
            r"(?s)static int\s+posixmodule_exec\(PyObject \*m\)\s*\{.*?"
            r'return _PyModule_Add\(m, "_have_functions", list\);\s*\}',
            posix_text,
        )
            or not re.search(r"\{Py_mod_exec, posixmodule_exec\}", posix_text)
            or not re.search(r"\.m_slots = posixmodile_slots", posix_text)):
        return ()
    return (("_exists('_have_functions')", True),)


def _target_os_feature_add_condition_facts(
        files, posix_source, clinic_source, pyconfig_source):
    """Bound both possible outcomes of os.py's fixed POSIX feature-add calls."""
    source = files.get("os.py") if type(files) is dict else None
    if (type(source) is not bytes
            or hashlib.sha256(source).hexdigest() != OS_SOURCE_SHA256
            or type(posix_source) is not bytes
            or hashlib.sha256(posix_source).hexdigest() != POSIX_MODULE_C_SHA256
            or type(clinic_source) is not bytes
            or hashlib.sha256(clinic_source).hexdigest() != POSIX_MODULE_CLINIC_SHA256
            or type(pyconfig_source) is not bytes
            or len(pyconfig_source) > MAX_TARGET_PYCONFIG_BYTES
            or hashlib.sha256(pyconfig_source).hexdigest() != TARGET_PYCONFIG_SHA256
            or _target_os_have_functions_call_facts(
                files, posix_source, clinic_source
            ) != (("_exists('_have_functions')", True),)):
        return {}
    try:
        tree = ast.parse(source, filename="os.py")
    except SyntaxError:
        return {}
    imports = [node for node in ast.walk(tree) if isinstance(node, ast.ImportFrom)
               and node.module == "posix" and len(node.names) == 1
               and node.names[0].name == "*" and node.names[0].asname is None]
    globals_assignments = [node for node in ast.walk(tree) if isinstance(node, ast.Assign)
                           and any(isinstance(target, ast.Name)
                                   and target.id == "_globals" for target in node.targets)]
    helpers = [node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)
               and node.name == "_add"]
    if (len(imports) != 1 or len(globals_assignments) != 1
            or ast.unparse(globals_assignments[0]) != "_globals = globals()"
            or len(helpers) != 1
            or [arg.arg for arg in helpers[0].args.args] != ["str", "fn"]):
        return {}
    guards = [node for node in ast.walk(helpers[0])
              if isinstance(node, ast.If)
              and ast.unparse(node.test) == "fn in _globals and str in _have_functions"]
    if len(guards) != 1:
        return {}
    calls = [node for node in ast.walk(tree) if isinstance(node, ast.Call)
             and isinstance(node.func, ast.Name) and node.func.id == "_add"]
    call_pairs = []
    for node in calls:
        if (len(node.args) != 2
                or not all(isinstance(arg, ast.Constant) and type(arg.value) is str
                           for arg in node.args)):
            continue
        call_pairs.append(tuple(arg.value for arg in node.args))
    if (call_pairs.count(("HAVE_FCHMOD", "chmod")) != 1
            or call_pairs.count(("HAVE_LCHFLAGS", "chflags")) != 1):
        return {}

    config_text = pyconfig_source.decode("ascii")
    if (len(re.findall(r"(?m)^#define HAVE_FCHMOD 1$", config_text)) != 1
            or re.search(r"(?m)^#\s*define\s+HAVE_LCHFLAGS\b", config_text)):
        return {}
    c_text = posix_source.decode("utf-8")
    clinic_text = clinic_source.decode("utf-8")
    table = re.search(
        r"(?s)static const struct have_function\s*\{.*?\}\s*have_functions\[\]\s*=\s*\{(.*?)\n\};",
        c_text,
    )
    methods = re.search(
        r"(?s)static PyMethodDef posix_methods\[\]\s*=\s*\{(.*?)\n\};",
        c_text,
    )
    chmod_rows = re.findall(
        r'(?s)#ifdef HAVE_FCHMOD\s*(\{\s*"HAVE_FCHMOD"\s*,\s*NULL\s*\})\s*,?\s*#endif',
        table.group(1) if table else "",
    )
    lchflags_rows = re.findall(
        r'(?s)#ifdef HAVE_LCHFLAGS\s*(\{\s*"HAVE_LCHFLAGS"\s*,\s*NULL\s*\})\s*,?\s*#endif',
        table.group(1) if table else "",
    )
    chmod_definition = re.findall(
        r'(?m)^#define OS_CHMOD_METHODDEF[^\n]*\\\r?\n\s*\{"chmod"\s*,',
        clinic_text,
    )
    normalize_c = lambda value: re.sub(r"\s+", "", value)
    if (table is None or methods is None or len(chmod_rows) != 1
            or normalize_c(chmod_rows[0]) != '{"HAVE_FCHMOD",NULL}'
            or len(lchflags_rows) != 1
            or normalize_c(lchflags_rows[0]) != '{"HAVE_LCHFLAGS",NULL}'
            or methods.group(1).split().count("OS_CHMOD_METHODDEF") != 1
            or len(chmod_definition) != 1
            or not re.search(r"\.m_methods\s*=\s*posix_methods", c_text)):
        return {}
    return {("os", "os.py", guards[0].lineno): (False, True)}


def _target_posix_build_call_facts(files, posix_source, clinic_source,
                                  pyconfig_source):
    """Bind compile-time posix methods to the selected image's pyconfig.h."""
    if (type(pyconfig_source) is not bytes
            or len(pyconfig_source) > MAX_TARGET_PYCONFIG_BYTES
            or hashlib.sha256(pyconfig_source).hexdigest() != TARGET_PYCONFIG_SHA256
            or type(posix_source) is not bytes
            or hashlib.sha256(posix_source).hexdigest() != POSIX_MODULE_C_SHA256
            or type(clinic_source) is not bytes
            or hashlib.sha256(clinic_source).hexdigest() != POSIX_MODULE_CLINIC_SHA256
            or _target_os_have_functions_call_facts(
                files, posix_source, clinic_source
            ) != (("_exists('_have_functions')", True),)):
        return ()
    config_text = pyconfig_source.decode("ascii")
    config = set(re.findall(r"(?m)^#define (HAVE_[A-Z0-9_]+) 1$", config_text))
    c_text = posix_source.decode("utf-8")
    clinic_text = clinic_source.decode("utf-8")
    method_table = re.search(
        r"(?s)static PyMethodDef posix_methods\[\] = \{(.*?)\n\};",
        c_text,
    )
    if (method_table is None
            or not re.search(r"\.m_methods = posix_methods", c_text)):
        return ()
    table = method_table.group(1)

    def guarded_method(feature_condition, macro, exported_name):
        return bool(
            re.search(
                r"(?s)#if " + feature_condition + r".*?#define " + macro
                + r"\s+\\\s*\{\s*\"" + re.escape(exported_name) + r"\"",
                clinic_text,
            )
            and re.search(r"(?m)^\s*" + macro + r"\s*$", table)
        )

    facts = []
    have_statvfs = (
        "HAVE_STATVFS" in config and "HAVE_SYS_STATVFS_H" in config
        and guarded_method(
            r"\(defined\(HAVE_STATVFS\) && defined\(HAVE_SYS_STATVFS_H\)\)",
            "OS_STATVFS_METHODDEF", "statvfs",
        )
    )
    have_fstatvfs = (
        "HAVE_FSTATVFS" in config and "HAVE_SYS_STATVFS_H" in config
        and guarded_method(
            r"\(defined\(HAVE_FSTATVFS\) && defined\(HAVE_SYS_STATVFS_H\)\)",
            "OS_FSTATVFS_METHODDEF", "fstatvfs",
        )
    )
    have_lchown = (
        "HAVE_LCHOWN" in config
        and guarded_method(r"defined\(HAVE_LCHOWN\)",
                           "OS_LCHOWN_METHODDEF", "lchown")
    )
    have_fork = (
        "HAVE_FORK" in config
        and guarded_method(r"defined\(HAVE_FORK\)",
                           "OS_REGISTER_AT_FORK_METHODDEF", "register_at_fork")
        and guarded_method(r"defined\(HAVE_FORK\)",
                           "OS_FORK_METHODDEF", "fork")
    )
    have_execv = (
        "HAVE_EXECV" in config
        and guarded_method(r"defined\(HAVE_EXECV\)",
                           "OS_EXECV_METHODDEF", "execv")
    )
    spawnv_features = {"HAVE_SPAWNV", "HAVE_WSPAWNV", "HAVE_RTPSPAWN"}
    spawnv_enabled = bool(config & spawnv_features)
    spawnv_method_guarded = guarded_method(
        r"\(defined\(HAVE_SPAWNV\) \|\| defined\(HAVE_WSPAWNV\) \|\| "
        r"defined\(HAVE_RTPSPAWN\)\)", "OS_SPAWNV_METHODDEF", "spawnv"
    )
    have_spawnv = spawnv_enabled and spawnv_method_guarded
    if have_statvfs and have_fstatvfs:
        facts.append(("_exists('statvfs') and _exists('fstatvfs')", True))
    if have_lchown:
        facts.append(("_exists('lchown')", True))
    if have_fork:
        facts.extend((
            ("hasattr(os, 'register_at_fork')", True),
            ("_exists('fork')", True),
        ))
    if have_execv:
        facts.append(("_exists('execv')", True))
    if not spawnv_enabled and spawnv_method_guarded:
        facts.append(("_exists('spawnv')", False))
    if (b"spawnvp" not in posix_source
            and b"spawnvp" not in clinic_source):
        facts.append(("_exists('spawnvp')", False))
    if have_fork and not have_spawnv and have_execv:
        facts.append((
            "_exists('fork') and (not _exists('spawnv')) and _exists('execv')",
            True,
        ))
    return tuple(sorted(facts))


def _target_os_descriptor_support_facts(files, posix_source, clinic_source,
                                        pyconfig_source):
    """Resolve os.fwalk's descriptor guard from the pinned Linux build inputs."""
    source = files.get("os.py")
    if (type(source) is not bytes
            or hashlib.sha256(source).hexdigest() != OS_SOURCE_SHA256
            or type(pyconfig_source) is not bytes
            or len(pyconfig_source) > MAX_TARGET_PYCONFIG_BYTES
            or hashlib.sha256(pyconfig_source).hexdigest() != TARGET_PYCONFIG_SHA256
            or type(posix_source) is not bytes
            or hashlib.sha256(posix_source).hexdigest() != POSIX_MODULE_C_SHA256
            or type(clinic_source) is not bytes
            or hashlib.sha256(clinic_source).hexdigest() != POSIX_MODULE_CLINIC_SHA256
            or _target_os_have_functions_call_facts(
                files, posix_source, clinic_source
            ) != (("_exists('_have_functions')", True),)):
        return ()

    tree = ast.parse(source, filename="os.py")
    guard = [node for node in tree.body if isinstance(node, ast.If)
             and ast.unparse(node.test)
             == "{open, stat} <= supports_dir_fd and {scandir, stat} <= supports_fd"]
    if len(guard) != 1:
        return ()

    required_os_facts = {
        "_add('HAVE_OPENAT', 'open')",
        "_add('HAVE_FSTATAT', 'stat')",
        "_add('HAVE_FDOPENDIR', 'scandir')",
        "_set.add(stat)",
        "supports_dir_fd = _set",
        "supports_fd = _set",
    }
    observed_os_facts = {
        ast.unparse(node) for node in ast.walk(tree)
        if isinstance(node, (ast.Expr, ast.Assign))
    }
    if not required_os_facts <= observed_os_facts:
        return ()

    config_text = pyconfig_source.decode("ascii")
    config = set(re.findall(r"(?m)^#define (HAVE_[A-Z0-9_]+) 1$", config_text))
    required_config = {"HAVE_OPENAT", "HAVE_FSTATAT", "HAVE_FDOPENDIR"}
    if not required_config <= config:
        return ()

    c_text = posix_source.decode("utf-8")
    clinic_text = clinic_source.decode("utf-8")
    method_table = re.search(
        r"(?s)static PyMethodDef posix_methods\[\] = \{(.*?)\n\};", c_text
    )
    if method_table is None or not re.search(r"\.m_methods = posix_methods", c_text):
        return ()
    table = method_table.group(1)
    if any(not re.search(r"(?m)^\s*" + macro + r"\s*$", table)
           for macro in ("OS_OPEN_METHODDEF", "OS_STAT_METHODDEF", "OS_SCANDIR_METHODDEF")):
        return ()
    if any(macro not in clinic_text or '{"' + name + '"' not in clinic_text
           for macro, name in (("OS_OPEN_METHODDEF", "open"),
                               ("OS_STAT_METHODDEF", "stat"),
                               ("OS_SCANDIR_METHODDEF", "scandir"))):
        return ()

    if not re.search(
            r"(?s)#else\s+#  define HAVE_FSTATAT_RUNTIME 1.*?"
            r"#  define HAVE_FDOPENDIR_RUNTIME 1.*?"
            r"#  define HAVE_OPENAT_RUNTIME 1.*?#endif",
            c_text):
        return ()
    probes = (
        ('"HAVE_OPENAT", probe_openat', "HAVE_OPENAT_RUNTIME"),
        ('"HAVE_FSTATAT", probe_fstatat', "HAVE_FSTATAT_RUNTIME"),
        ('"HAVE_FDOPENDIR", probe_fdopendir', "HAVE_FDOPENDIR_RUNTIME"),
    )
    for row, probe in probes:
        if row not in c_text or probe not in c_text:
            return ()
    return (("{open, stat} <= supports_dir_fd and {scandir, stat} <= supports_fd", True),)


def _target_threading_os_alias_facts(files):
    """Carry the proven os.register_at_fork method through threading's alias."""
    source = files.get("threading.py")
    if (type(source) is not bytes
            or hashlib.sha256(source).hexdigest() != THREADING_SOURCE_SHA256):
        return ()
    tree = ast.parse(source, filename="threading.py")
    aliases = [alias for node in tree.body if isinstance(node, ast.Import)
               for alias in node.names if alias.name == "os" and alias.asname == "_os"]
    if (len(aliases) != 1
            or any(isinstance(node, ast.Name) and node.id == "_os"
                   and isinstance(node.ctx, (ast.Store, ast.Del))
                   for node in ast.walk(tree))):
        return ()
    return (("hasattr(_os, 'register_at_fork')", True),)


def _target_threading_main_constructor_line_facts(files):
    """Bind Thread.__init__ argument guards to threading's import-time main thread."""
    source = files.get("threading.py") if type(files) is dict else None
    if (type(source) is not bytes
            or hashlib.sha256(source).hexdigest() != THREADING_SOURCE_SHA256):
        return {}
    try:
        tree = ast.parse(source, filename="threading.py")
    except SyntaxError:
        return {}
    main_assignments = [node for node in tree.body if isinstance(node, ast.Assign)
                        and any(isinstance(target, ast.Name)
                                and target.id == "_main_thread"
                                for target in node.targets)
                        and ast.unparse(node.value) == "_MainThread()"]
    thread_classes = [node for node in tree.body if isinstance(node, ast.ClassDef)
                      and node.name == "Thread"]
    main_classes = [node for node in tree.body if isinstance(node, ast.ClassDef)
                    and node.name == "_MainThread"]
    if len(main_assignments) != 1 or len(thread_classes) != 1 or len(main_classes) != 1:
        return {}
    if [ast.unparse(base) for base in main_classes[0].bases] != ["Thread"]:
        return {}
    thread_initializers = [node for node in thread_classes[0].body
                           if isinstance(node, ast.FunctionDef)
                           and node.name == "__init__"]
    main_initializers = [node for node in main_classes[0].body
                         if isinstance(node, ast.FunctionDef)
                         and node.name == "__init__"]
    if len(thread_initializers) != 1 or len(main_initializers) != 1:
        return {}
    calls = [node for node in ast.walk(main_initializers[0])
             if isinstance(node, ast.Call)
             and ast.unparse(node) == "Thread.__init__(self, name='MainThread', daemon=False)"]
    guards = {
        node.lineno: ast.unparse(node.test)
        for node in ast.walk(thread_initializers[0])
        if isinstance(node, ast.If) and node.lineno in (910, 925, 926)
    }
    if (len(calls) != 1
            or guards != {
                910: "name", 925: "daemon is not None",
                926: "daemon and (not _daemon_threads_allowed())",
            }):
        return {}
    return {910: True, 925: True, 926: False}


def _target_threading_condition_lock_line_facts(files, module_source):
    """Bind the import-time Condition lock argument through main-thread setup."""
    source = files.get("threading.py") if type(files) is dict else None
    if (type(source) is not bytes
            or hashlib.sha256(source).hexdigest() != THREADING_SOURCE_SHA256
            or _target_threading_main_constructor_line_facts(files)
            != {910: True, 925: True, 926: False}
            or type(module_source) is not bytes
            or hashlib.sha256(module_source).hexdigest()
            != THREAD_NATIVE_ID_MODULE_SHA256
            or _TARGET_BUILTIN_MEMBERSHIP.get("_thread") is not True):
        return {}
    try:
        tree = ast.parse(source, filename="threading.py")
    except SyntaxError:
        return {}
    classes = {
        name: [node for node in tree.body if isinstance(node, ast.ClassDef)
               and node.name == name]
        for name in ("Condition", "Event", "Thread", "_MainThread")
    }
    if any(len(nodes) != 1 for nodes in classes.values()):
        return {}

    def method(owner, name):
        matches = [node for node in classes[owner][0].body
                   if isinstance(node, ast.FunctionDef) and node.name == name]
        return matches[0] if len(matches) == 1 else None

    condition_init = method("Condition", "__init__")
    event_init = method("Event", "__init__")
    thread_init = method("Thread", "__init__")
    main_init = method("_MainThread", "__init__")
    set_tstate_lock = method("Thread", "_set_tstate_lock")
    excepthook_bindings = [node for node in tree.body
                           if isinstance(node, ast.Try)
                           and any(isinstance(handler.type, ast.Name)
                                   and handler.type.id == "ImportError"
                                   for handler in node.handlers)
                           and any(isinstance(import_node, ast.ImportFrom)
                                   and import_node.module == "_thread"
                                   and any(alias.name == "_excepthook"
                                           and alias.asname == "excepthook"
                                           for alias in import_node.names)
                                   for import_node in ast.walk(node))]
    invoke_hook_functions = [node for node in tree.body
                             if isinstance(node, ast.FunctionDef)
                             and node.name == "_make_invoke_excepthook"]
    daemon_property = [node for node in classes["Thread"][0].body
                       if isinstance(node, ast.FunctionDef)
                       and node.name == "daemon"
                       and any(ast.unparse(item) == "property"
                               for item in node.decorator_list)]
    if any(node is None for node in (
            condition_init, event_init, thread_init, main_init, set_tstate_lock)) \
            or len(daemon_property) != 1 \
            or len(excepthook_bindings) != 1 \
            or len(invoke_hook_functions) != 1:
        return {}
    hook_binding = excepthook_bindings[0]
    thread_hook_imports = [node for node in ast.walk(hook_binding)
                           if isinstance(node, ast.ImportFrom)
                           and node.module == "_thread"
                           and any(alias.name == "_excepthook"
                                   and alias.asname == "excepthook"
                                   for alias in node.names)]
    fallback_hook_defs = [node for handler in hook_binding.handlers
                          if isinstance(handler.type, ast.Name)
                          and handler.type.id == "ImportError"
                          for node in ast.walk(handler)
                          if isinstance(node, ast.FunctionDef)
                          and node.name == "excepthook"]
    condition_guards = {
        node.lineno: ast.unparse(node.test)
        for node in ast.walk(condition_init)
        if isinstance(node, ast.If) and node.lineno in (278, 287, 289, 291)
    }
    lock_aliases = [node for node in tree.body if isinstance(node, ast.Assign)
                    and len(node.targets) == 1
                    and isinstance(node.targets[0], ast.Name)
                    and node.targets[0].id == "Lock"]
    allocator_aliases = [node for node in tree.body if isinstance(node, ast.Assign)
                         and len(node.targets) == 1
                         and isinstance(node.targets[0], ast.Name)
                         and node.targets[0].id == "_allocate_lock"]
    event_condition_calls = [node for node in ast.walk(event_init)
                             if isinstance(node, ast.Call)
                             and ast.unparse(node) == "Condition(Lock())"]
    thread_event_calls = [node for node in ast.walk(thread_init)
                          if isinstance(node, ast.Call)
                          and ast.unparse(node) == "Event()"]
    main_thread_calls = [node for node in ast.walk(main_init)
                         if isinstance(node, ast.Call)
                         and ast.unparse(node)
                         == "Thread.__init__(self, name='MainThread', daemon=False)"]
    main_thread_assignments = [node for node in tree.body
                               if isinstance(node, ast.Assign)
                               and any(isinstance(target, ast.Name)
                                       and target.id == "_main_thread"
                                       for target in node.targets)
                               and ast.unparse(node.value) == "_MainThread()"]
    tstate_guards = [node for node in ast.walk(set_tstate_lock)
                     if isinstance(node, ast.If) and node.lineno == 1053
                     and ast.unparse(node.test) == "not self.daemon"]
    daemon_returns = [node for node in ast.walk(daemon_property[0])
                      if isinstance(node, ast.Return)
                      and ast.unparse(node.value) == "self._daemonic"]
    daemon_assignments = [node for node in ast.walk(thread_init)
                          if isinstance(node, ast.Assign)
                          and ast.unparse(node) == "self._daemonic = daemon"]
    main_tstate_calls = [node for node in ast.walk(main_init)
                         if isinstance(node, ast.Call)
                         and ast.unparse(node) == "self._set_tstate_lock()"]
    invoke_hook_guards = [node for node in ast.walk(invoke_hook_functions[0])
                          if isinstance(node, ast.If) and node.lineno == 1363
                          and ast.unparse(node.test) == "old_excepthook is None"]
    old_hook_assignments = [node for node in ast.walk(invoke_hook_functions[0])
                            if isinstance(node, ast.Assign)
                            and ast.unparse(node) == "old_excepthook = excepthook"]
    thread_hook_calls = [node for node in ast.walk(thread_init)
                         if isinstance(node, ast.Call)
                         and ast.unparse(node) == "_make_invoke_excepthook()"]
    module_hook_assignments = [node for node in tree.body
                               if isinstance(node, (ast.Assign, ast.AnnAssign,
                                                    ast.AugAssign))
                               and any(isinstance(target, ast.Name)
                                       and target.id == "excepthook"
                                       for target in (
                                           node.targets if isinstance(node, ast.Assign)
                                           else [node.target]))]
    if (condition_guards != {
                278: "lock is None",
                287: "hasattr(lock, '_release_save')",
                289: "hasattr(lock, '_acquire_restore')",
                291: "hasattr(lock, '_is_owned')",
            }
            or [arg.arg for arg in condition_init.args.args] != ["self", "lock"]
            or [ast.unparse(value) for value in condition_init.args.defaults] != ["None"]
            or len(lock_aliases) != 1
            or ast.unparse(lock_aliases[0].value) != "_allocate_lock"
            or len(allocator_aliases) != 1
            or ast.unparse(allocator_aliases[0].value) != "_thread.allocate_lock"
            or len(event_condition_calls) != 1
            or event_condition_calls[0].lineno != 589
            or len(thread_event_calls) != 1
            or thread_event_calls[0].lineno != 935
            or len(main_thread_calls) != 1
            or len(main_thread_assignments) != 1
            or len(tstate_guards) != 1
            or len(daemon_returns) != 1
            or len(daemon_assignments) != 1
            or len(main_tstate_calls) != 1
            or len(invoke_hook_guards) != 1
            or len(old_hook_assignments) != 1
            or len(thread_hook_calls) != 1
            or thread_hook_calls[0].lineno != 940
            or len(thread_hook_imports) != 1
            or len(fallback_hook_defs) != 1
            or module_hook_assignments
            or hook_binding.end_lineno >= invoke_hook_functions[0].lineno
            or invoke_hook_functions[0].end_lineno >= main_thread_assignments[0].lineno):
        return {}
    for path, data in files.items():
        if (path == "threading.py" or type(data) is not bytes
                or not path.endswith(".py") or "test" in path.split("/")):
            continue
        try:
            other_tree = ast.parse(data, filename=path)
        except SyntaxError:
            return {}
        parents = {child: parent for parent in ast.walk(other_tree)
                   for child in ast.iter_child_nodes(parent)}
        threading_aliases = {
            "Thread" if alias.name == "*" else alias.asname or alias.name
            for node in ast.walk(other_tree)
            if isinstance(node, ast.ImportFrom) and node.module == "threading"
            for alias in node.names if alias.name in ("Thread", "*")
        }
        threading_modules = {
            alias.asname or alias.name.split(".")[0]
            for node in ast.walk(other_tree) if isinstance(node, ast.Import)
            for alias in node.names if alias.name == "threading"
        }
        for node in ast.walk(other_tree):
            if not isinstance(node, ast.Call):
                continue
            is_thread_constructor = (
                isinstance(node.func, ast.Name)
                and node.func.id in threading_aliases
                or isinstance(node.func, ast.Attribute)
                and node.func.attr == "Thread"
                and isinstance(node.func.value, ast.Name)
                and node.func.value.id in threading_modules
            )
            current = node
            child = node
            module_scope = True
            while current in parents:
                child = current
                current = parents[current]
                if isinstance(current, (ast.FunctionDef, ast.AsyncFunctionDef,
                                         ast.Lambda)):
                    body = getattr(current, "body", None)
                    if isinstance(body, list) and child in body:
                        module_scope = False
                        break
                    if isinstance(current, ast.Lambda) and child is current.body:
                        module_scope = False
                        break
            if is_thread_constructor and module_scope:
                return {}
    c_text = module_source.decode("utf-8")
    if (not re.search(
            r'\{"_excepthook",\s*thread_excepthook,', c_text)
            or not re.search(
            r"(?s)thread_PyThread_allocate_lock\(PyObject \*module,.*?"
            r"return \(PyObject \*\) newlockobject\(module\);", c_text)
            or not re.search(
                r'\{"allocate_lock",\s*thread_PyThread_allocate_lock,', c_text)
            or not re.search(
                r"(?s)static PyType_Slot lock_type_slots\[\] = \{.*?"
                r"\{Py_tp_methods, lock_methods\},.*?\{0, 0\}\s*\};",
                c_text,
            )
            or not re.search(
                r"(?s)static PyType_Spec lock_type_spec = \{.*?"
                r"\.name = \"_thread\.lock\".*?\.slots = lock_type_slots,\s*\};",
                c_text,
            )
            or not re.search(
                r"(?s)static PyMethodDef lock_methods\[\] = \{(.*?)\n\};",
                c_text,
            )
            or any(name in re.search(
                r"(?s)static PyMethodDef lock_methods\[\] = \{(.*?)\n\};",
                c_text,
            ).group(1) for name in (
                '"_release_save"', '"_acquire_restore"', '"_is_owned"',
            ))
            or not re.search(
                r"(?s)static PyMemberDef lock_type_members\[\] = \{.*?"
                r"\{NULL,?\s*\},?\s*\};", c_text)
            or not re.search(
                r"(?s)newlockobject\(PyObject \*module\)\s*\{.*?"
                r"if \(self == NULL\) \{\s*return NULL;\s*\}.*?"
                r"if \(self->lock_lock == NULL\) \{.*?return NULL;\s*\}"
                r"\s*return self;", c_text)):
        return {}
    return {
        278: False, 287: False, 289: False, 291: False,
        1053: True, 1363: False,
    }


def _target_threading_sys_excepthook_line_facts(
        files, source_modules, thread_line_facts, sys_module_source,
        sys_module_clinic_source):
    """Bind the import-time sys.excepthook non-None guard to CPython's sys API."""
    if (type(files) is not dict or type(source_modules) is not tuple
            or not source_modules or any(type(module) is not str for module in source_modules)
            or type(thread_line_facts) is not dict
            or thread_line_facts.get(1363) is not False
            or _TARGET_BUILTIN_MEMBERSHIP.get("sys") is not True):
        return {}
    threading_source = files.get("threading.py")
    if (type(threading_source) is not bytes
            or hashlib.sha256(threading_source).hexdigest() != THREADING_SOURCE_SHA256
            or "threading" not in source_modules):
        return {}
    try:
        threading_tree = ast.parse(threading_source, filename="threading.py")
    except SyntaxError:
        return {}
    hook_functions = [node for node in threading_tree.body
                      if isinstance(node, ast.FunctionDef)
                      and node.name == "_make_invoke_excepthook"]
    if (len(hook_functions) != 1
            or sum(1 for node in ast.walk(hook_functions[0])
                   if isinstance(node, ast.Assign)
                   and ast.unparse(node) == "old_sys_excepthook = _sys.excepthook") != 1
            or sum(1 for node in ast.walk(hook_functions[0])
                   if isinstance(node, ast.If) and node.lineno == 1365
                   and ast.unparse(node.test) == "old_sys_excepthook is None") != 1):
        return {}
    sources = (
        (sys_module_source, SYS_MODULE_C_SHA256),
        (sys_module_clinic_source, SYS_MODULE_CLINIC_SHA256),
    )
    if any(type(source) is not bytes or hashlib.sha256(source).hexdigest() != expected
           for source, expected in sources):
        return {}
    c_text = sys_module_source.decode("utf-8")
    clinic_text = sys_module_clinic_source.decode("utf-8")
    methods = re.search(r"(?s)static PyMethodDef sys_methods\[\] = \{(.*?)\n\};", c_text)
    module_definition = re.search(
        r'(?s)static\s+struct\s+PyModuleDef\s+sysmodule\s*=\s*\{'
        r'\s*PyModuleDef_HEAD_INIT\s*,\s*"sys"\s*,\s*sys_doc\s*,\s*-1\s*,'
        r'(?:\s*/\*.*?\*/)?\s*'
        r'sys_methods\s*,',
        c_text,
    )
    if (methods is None or methods.group(1).count("SYS_EXCEPTHOOK_METHODDEF") != 1
            or module_definition is None
            or not re.search(
                r"(?s)#define SYS_EXCEPTHOOK_METHODDEF\s*\\\s*"
                r'\{"excepthook",\s*_PyCFunction_CAST\(sys_excepthook\),',
                clinic_text,
            )):
        return {}

    for module in source_modules:
        path = _module_path(module, files)
        source = files.get(path) if path is not None else None
        if source is None:
            continue
        try:
            tree = ast.parse(source, filename=path)
        except (SyntaxError, TypeError):
            return {}
        sys_aliases = {"sys"}
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                sys_aliases.update(
                    alias.asname or alias.name.split(".", 1)[0]
                    for alias in node.names if alias.name == "sys"
                )
        changed = True
        while changed:
            changed = False
            for node in ast.walk(tree):
                if (isinstance(node, ast.Assign)
                        and isinstance(node.value, ast.Name)
                        and node.value.id in sys_aliases):
                    for target in node.targets:
                        if isinstance(target, ast.Name) and target.id not in sys_aliases:
                            sys_aliases.add(target.id)
                            changed = True
        for node in ast.walk(tree):
            targets = []
            if isinstance(node, ast.Assign):
                targets = node.targets
            elif isinstance(node, (ast.AnnAssign, ast.AugAssign)):
                targets = [node.target]
            elif isinstance(node, ast.Delete):
                targets = node.targets
            if any(
                (isinstance(target, ast.Attribute) and target.attr == "excepthook"
                 and isinstance(target.value, ast.Name)
                 and target.value.id in sys_aliases)
                or (isinstance(target, ast.Subscript)
                    and isinstance(target.value, ast.Attribute)
                    and target.value.attr == "__dict__"
                    and isinstance(target.value.value, ast.Name)
                    and target.value.value.id in sys_aliases
                    and isinstance(target.slice, ast.Constant)
                    and target.slice.value == "excepthook")
                for root in targets for target in ast.walk(root)
            ):
                return {}
            if (isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
                    and node.func.id == "setattr" and len(node.args) >= 2
                    and isinstance(node.args[0], ast.Name)
                    and node.args[0].id in sys_aliases
                    and isinstance(node.args[1], ast.Constant)
                    and node.args[1].value == "excepthook"):
                return {}
            if (isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
                    and node.func.attr == "update"
                    and isinstance(node.func.value, ast.Attribute)
                    and node.func.value.attr == "__dict__"
                    and isinstance(node.func.value.value, ast.Name)
                    and node.func.value.value.id in sys_aliases
                    and any(isinstance(arg, ast.Dict) and any(
                        isinstance(key, ast.Constant) and key.value == "excepthook"
                        for key in arg.keys
                    ) for arg in node.args)):
                return {}
    return {1365: False}


def _target_threading_native_id_name_facts(
        files, header_source, module_source, pthread_source, pyconfig_source):
    """Bind threading's native-id flag to the pinned Linux CPython build path."""
    if (_TARGET_BUILTIN_MEMBERSHIP.get("_thread") is not True
            or type(pyconfig_source) is not bytes
            or hashlib.sha256(pyconfig_source).hexdigest() != TARGET_PYCONFIG_SHA256):
        return {}
    sources = (
        (header_source, THREAD_NATIVE_ID_HEADER_SHA256),
        (module_source, THREAD_NATIVE_ID_MODULE_SHA256),
        (pthread_source, THREAD_NATIVE_ID_PTHREAD_SHA256),
    )
    if any(type(source) is not bytes or hashlib.sha256(source).hexdigest() != expected
           for source, expected in sources):
        return {}
    header = header_source.decode("utf-8")
    module = module_source.decode("utf-8")
    pthread = pthread_source.decode("utf-8")
    threading_source = files.get("threading.py")
    if (type(threading_source) is not bytes
            or hashlib.sha256(threading_source).hexdigest() != THREADING_SOURCE_SHA256
            or not re.search(
                r"(?s)#if \(defined\(__APPLE__\) \|\| defined\(__linux__\).*?"
                r"#define PY_HAVE_THREAD_NATIVE_ID",
                header,
            )
            or not re.search(
                r"(?s)#ifdef PY_HAVE_THREAD_NATIVE_ID.*?thread_get_native_id.*?"
                r"#endif",
                module,
            )
            or not re.search(
                r"(?s)#ifdef PY_HAVE_THREAD_NATIVE_ID\s*\{\"get_native_id\",\s*"
                r"thread_get_native_id,.*?#endif",
                module,
            )
            or "PyThread_get_thread_native_id" not in pthread):
        return {}
    tree = ast.parse(threading_source, filename="threading.py")
    native_id_tries = [node for node in tree.body if isinstance(node, ast.Try)
                       and any(isinstance(statement, ast.Assign)
                               and any(isinstance(target, ast.Name)
                                       and target.id == "get_native_id"
                                       for target in statement.targets)
                               for statement in node.body)]
    if (len(native_id_tries) != 1
            or not any(isinstance(statement, ast.Assign)
                       and any(isinstance(target, ast.Name)
                               and target.id == "_HAVE_THREAD_NATIVE_ID"
                               for target in statement.targets)
                       and isinstance(statement.value, ast.Constant)
                       and statement.value.value is True
                       for statement in native_id_tries[0].body)
            or not any(isinstance(handler.type, ast.Name)
                       and handler.type.id == "AttributeError"
                       and any(isinstance(statement, ast.Assign)
                               and any(isinstance(target, ast.Name)
                                       and target.id == "_HAVE_THREAD_NATIVE_ID"
                                       for target in statement.targets)
                               and isinstance(statement.value, ast.Constant)
                               and statement.value.value is False
                               for statement in handler.body)
                       for handler in native_id_tries[0].handlers)):
        return {}
    return {"_HAVE_THREAD_NATIVE_ID": True}


def _target_threading_crlock_name_fact(files, module_source, pyconfig_source):
    """Bind `_CRLock` to a non-None marker only on the pinned built-in RLock path."""
    source = files.get("threading.py")
    if (_TARGET_BUILTIN_MEMBERSHIP.get("_thread") is not True
            or type(source) is not bytes
            or hashlib.sha256(source).hexdigest() != THREADING_SOURCE_SHA256
            or type(module_source) is not bytes
            or hashlib.sha256(module_source).hexdigest() != THREAD_NATIVE_ID_MODULE_SHA256
            or type(pyconfig_source) is not bytes
            or hashlib.sha256(pyconfig_source).hexdigest() != TARGET_PYCONFIG_SHA256):
        return {}
    c_text = module_source.decode("utf-8")
    start = c_text.find("thread_module_exec(PyObject *module)")
    end = c_text.find("thread_module_traverse", start + 1) if start >= 0 else -1
    if (start < 0 or end < 0
            or not re.search(r'static PyType_Spec rlock_type_spec\s*=\s*\{'
                             r'(?:(?!\};).)*\.name\s*=\s*"_thread\.RLock"',
                             c_text, re.S)
            or "PyType_FromSpec(&rlock_type_spec)" not in c_text[start:end]
            or "PyModule_AddType(module, rlock_type)" not in c_text[start:end]
            or any(line.lstrip().startswith(("#if", "#else", "#elif"))
                   for line in c_text[start:end].splitlines())):
        return {}
    tree = ast.parse(source, filename="threading.py")
    crlock_tries = [node for node in tree.body if isinstance(node, ast.Try)
                    and any(isinstance(statement, ast.Assign)
                            and any(isinstance(target, ast.Name)
                                    and target.id == "_CRLock"
                                    for target in statement.targets)
                            for statement in node.body)]
    if len(crlock_tries) != 1:
        return {}
    initializer = next((statement for statement in crlock_tries[0].body
                        if isinstance(statement, ast.Assign)
                        and any(isinstance(target, ast.Name)
                                and target.id == "_CRLock"
                                for target in statement.targets)), None)
    fallback = next((statement for handler in crlock_tries[0].handlers
                     if isinstance(handler.type, ast.Name)
                     and handler.type.id == "AttributeError"
                     for statement in handler.body
                     if isinstance(statement, ast.Assign)
                     and any(isinstance(target, ast.Name)
                             and target.id == "_CRLock"
                             for target in statement.targets)), None)
    if (initializer is None or ast.unparse(initializer.value) != "_thread.RLock"
            or fallback is None or not isinstance(fallback.value, ast.Constant)
            or fallback.value.value is not None):
        return {}
    stores = [node for node in ast.walk(tree)
              if isinstance(node, ast.Name) and node.id == "_CRLock"
              and isinstance(node.ctx, (ast.Store, ast.Del))]
    if len(stores) != 2:
        return {}
    return {"_CRLock": True}


def _target_threading_native_id_function_fact_safe(files, facts):
    """Allow only the pinned module-level native-id flag inside its functions."""
    source = files.get("threading.py")
    if (facts not in (
            {"_HAVE_THREAD_NATIVE_ID": True},
            {"_HAVE_THREAD_NATIVE_ID": True, "_CRLock": True},
    )
            or type(source) is not bytes
            or hashlib.sha256(source).hexdigest() != THREADING_SOURCE_SHA256):
        return False
    tree = ast.parse(source, filename="threading.py")
    parents = {child: parent for parent in ast.walk(tree)
               for child in ast.iter_child_nodes(parent)}
    tries = [node for node in tree.body if isinstance(node, ast.Try)
             and any(isinstance(statement, ast.Assign)
                     and any(isinstance(target, ast.Name)
                             and target.id == "get_native_id"
                             for target in statement.targets)
                     for statement in node.body)]
    if len(tries) != 1:
        return False
    stores = [node for node in ast.walk(tree)
              if isinstance(node, ast.Name) and node.id == "_HAVE_THREAD_NATIVE_ID"
              and isinstance(node.ctx, (ast.Store, ast.Del))]
    if len(stores) != 2:
        return False
    for node in stores:
        ancestor = node
        while ancestor in parents and parents[ancestor] is not tries[0]:
            ancestor = parents[ancestor]
        if ancestor not in parents or parents[ancestor] is not tries[0]:
            return False
    if "_CRLock" in facts:
        crlock_tries = [node for node in tree.body if isinstance(node, ast.Try)
                        and any(isinstance(statement, ast.Assign)
                                and any(isinstance(target, ast.Name)
                                        and target.id == "_CRLock"
                                        for target in statement.targets)
                                for statement in node.body)]
        crlock_stores = [node for node in ast.walk(tree)
                         if isinstance(node, ast.Name) and node.id == "_CRLock"
                         and isinstance(node.ctx, (ast.Store, ast.Del))]
        if len(crlock_tries) != 1 or len(crlock_stores) != 2:
            return False
        for node in crlock_stores:
            ancestor = node
            while ancestor in parents and parents[ancestor] is not crlock_tries[0]:
                ancestor = parents[ancestor]
            if ancestor not in parents or parents[ancestor] is not crlock_tries[0]:
                return False
    for node in ast.walk(tree):
        if isinstance(node, ast.arg) and node.arg in facts:
            return False
        if isinstance(node, (ast.Global, ast.Nonlocal)) and set(node.names) & set(facts):
            return False
        if ((isinstance(node, ast.Name) and node.id in {
                "exec", "eval", "globals", "locals", "vars"})
                or (isinstance(node, ast.Attribute) and node.attr in {
                    "exec", "eval", "globals", "locals", "vars"})):
            return False
    return True


def _target_sysconfig_user_base_name_facts(files):
    """Prove `_HAS_USER_BASE` for the pinned Linux source branch."""
    source = files.get("sysconfig.py")
    if (type(source) is not bytes
            or hashlib.sha256(source).hexdigest() != SYSCONFIG_SOURCE_SHA256):
        return {}
    tree = ast.parse(source, filename="sysconfig.py")
    functions = [node for node in tree.body
                 if isinstance(node, ast.FunctionDef) and node.name == "_getuserbase"]
    assignments = [node for node in tree.body if isinstance(node, ast.Assign)
                   and any(isinstance(target, ast.Name)
                           and target.id == "_HAS_USER_BASE"
                           for target in node.targets)]
    if len(functions) != 1 or len(assignments) != 1:
        return {}
    function = functions[0]
    platform_exclusions = [node for node in ast.walk(function)
                           if isinstance(node, ast.If)
                           and ast.unparse(node.test)
                           == "sys.platform in {'emscripten', 'vxworks', 'wasi'}"]
    nested_joiners = [node for node in function.body
                      if isinstance(node, ast.FunctionDef) and node.name == "joinuser"]
    final_userbase_returns = [node for node in function.body
                              if isinstance(node, ast.Return)
                              and isinstance(node.value, ast.Call)
                              and isinstance(node.value.func, ast.Name)
                              and node.value.func.id == "joinuser"
                              and [ast.literal_eval(arg) for arg in node.value.args
                                   if isinstance(arg, ast.Constant)] == ["~", ".local"]]
    if (len(platform_exclusions) != 1 or len(nested_joiners) != 1
            or len(final_userbase_returns) != 1
            or ast.unparse(nested_joiners[0].body[0].value)
            != "os.path.expanduser(os.path.join(*args))"
            or ast.unparse(assignments[0].value)
            != "_getuserbase() is not None"
            or not any(isinstance(node, ast.Return)
                       and isinstance(node.value, ast.Constant)
                       and node.value.value is None
                       for node in platform_exclusions[0].body)):
        return {}
    return {"_HAS_USER_BASE": True}


def _target_sysconfig_no_site_facts(files, sys_module_c_source, no_site):
    """Resolve the venv-only sys._home branch under the explicit -S assumption."""
    source = files.get("sysconfig.py")
    site_source = files.get("site.py")
    if (no_site is not True
            or type(source) is not bytes
            or hashlib.sha256(source).hexdigest() != SYSCONFIG_SOURCE_SHA256
            or type(site_source) is not bytes
            or hashlib.sha256(site_source).hexdigest() != SITE_SOURCE_SHA256
            or type(sys_module_c_source) is not bytes
            or hashlib.sha256(sys_module_c_source).hexdigest() != SYS_MODULE_C_SHA256):
        return {}

    sysconfig_tree = ast.parse(source, filename="sysconfig.py")
    home_reads = [node for node in sysconfig_tree.body if isinstance(node, ast.Assign)
                  and any(isinstance(target, ast.Name) and target.id == "_sys_home"
                          for target in node.targets)]
    home_guards = [node for node in sysconfig_tree.body if isinstance(node, ast.If)
                   and ast.unparse(node.test) == "_sys_home"]
    if (len(home_reads) != 1 or len(home_guards) != 1
            or ast.unparse(home_reads[0].value) != "getattr(sys, '_home', None)"
            or not any(isinstance(node, ast.Assign)
                       and any(isinstance(target, ast.Name)
                               and target.id == "_PROJECT_BASE"
                               for target in node.targets)
                       for node in home_guards[0].body)):
        return {}

    # Under -S, site.py is not imported. Fail closed if another library source
    # mentions the private field or the sys C module exposes the name.
    sys_home_forms = (b"sys._home", b"setattr(sys, '_home'",
                      b'setattr(sys, "_home"')
    for name, data in files.items():
        if (name not in ("site.py", "sysconfig.py")
                and any(form in data for form in sys_home_forms)):
            return {}
    if b"_home" in sys_module_c_source:
        return {}
    site_tree = ast.parse(site_source, filename="site.py")
    home_writes = [node for node in ast.walk(site_tree)
                   if isinstance(node, ast.Attribute) and node.attr == "_home"
                   and isinstance(node.ctx, ast.Store)]
    if (len(home_writes) != 2
            or any(not isinstance(node.value, ast.Name) or node.value.id != "sys"
                   for node in home_writes)):
        return {}
    return {"_sys_home": False}


def _target_sysconfig_is_python_build_line_facts(files):
    """Resolve the deprecated check_home guard for pinned stdlib callers only."""
    source = files.get("sysconfig.py") if type(files) is dict else None
    if (type(source) is not bytes
            or hashlib.sha256(source).hexdigest() != SYSCONFIG_SOURCE_SHA256):
        return {}
    try:
        tree = ast.parse(source, filename="sysconfig.py")
    except SyntaxError:
        return {}
    functions = [node for node in tree.body
                 if isinstance(node, ast.FunctionDef)
                 and node.name == "is_python_build"]
    if len(functions) != 1:
        return {}
    function = functions[0]
    args = function.args
    if (len(args.posonlyargs) != 0 or len(args.args) != 1
            or args.args[0].arg != "check_home" or args.vararg is not None
            or args.kwonlyargs or args.kwarg is not None
            or len(args.defaults) != 1
            or not isinstance(args.defaults[0], ast.Constant)
            or args.defaults[0].value is not None):
        return {}
    guards = [node for node in ast.walk(function)
              if isinstance(node, ast.If)
              and ast.unparse(node.test) == "check_home is not None"]
    if (len(guards) != 1
            or not any(isinstance(node, ast.Import)
                       and len(node.names) == 1
                       and node.names[0].name == "warnings"
                       for node in guards[0].body)):
        return {}
    if any(isinstance(node, ast.Name) and node.id == "check_home"
           and isinstance(node.ctx, (ast.Store, ast.Del))
           for node in ast.walk(function)):
        return {}

    expected_callers = {"sysconfig.py": 1, "venv/__init__.py": 3}
    observed_callers = {}
    for path, candidate in files.items():
        if type(candidate) is not bytes or not path.endswith(".py"):
            return {}
        path_parts = path.split("/")
        if "test" in path_parts:
            continue
        if b"is_python_build" not in candidate:
            continue
        try:
            caller_tree = tree if path == "sysconfig.py" else ast.parse(
                candidate, filename=path,
            )
        except SyntaxError:
            return {}
        if any(isinstance(node, ast.ImportFrom)
               and any(alias.name == "is_python_build" for alias in node.names)
               for node in ast.walk(caller_tree)):
            return {}
        if any(isinstance(node, ast.Constant) and node.value == "is_python_build"
               for node in ast.walk(caller_tree)):
            return {}
        parents = {child: node for node in ast.walk(caller_tree)
                   for child in ast.iter_child_nodes(node)}
        references = [
            node for node in ast.walk(caller_tree)
            if (isinstance(node, ast.Name) and node.id == "is_python_build")
            or (isinstance(node, ast.Attribute) and node.attr == "is_python_build")
        ]
        for reference in references:
            parent = parents.get(reference)
            if (not isinstance(parent, ast.Call) or parent.func is not reference
                    or parent.args or parent.keywords):
                return {}
            if path == "sysconfig.py":
                if not isinstance(reference, ast.Name):
                    return {}
            elif (not isinstance(reference, ast.Attribute)
                  or not isinstance(reference.value, ast.Name)
                  or reference.value.id != "sysconfig"):
                return {}
        if references:
            observed_callers[path] = len(references)
    if observed_callers != expected_callers:
        return {}
    return {guards[0].lineno: False}


def _target_string_template_pattern_guard_line_facts(files):
    """Resolve Template's pinned self-hook before its pattern is initialized."""
    if type(files) is not dict:
        return {}
    expected_hashes = {
        "string.py": STRING_SOURCE_SHA256,
        "pipes.py": PIPES_SOURCE_SHA256,
        "logging/__init__.py": LOGGING_SOURCE_SHA256,
    }
    if any(type(files.get(path)) is not bytes
           or hashlib.sha256(files[path]).hexdigest() != digest
           for path, digest in expected_hashes.items()):
        return {}
    try:
        trees = {
            path: ast.parse(source, filename=path)
            for path, source in files.items()
            if type(source) is bytes and path.endswith(".py")
            and "test" not in path.split("/")
        }
    except SyntaxError:
        return {}
    template_refs = []
    template_imports = []
    subclasses = []
    for path, tree in trees.items():
        for node in ast.walk(tree):
            if isinstance(node, ast.Name) and node.id == "Template":
                template_refs.append((path, node.lineno, "name"))
            elif isinstance(node, ast.Attribute) and node.attr == "Template":
                template_refs.append((path, node.lineno, "attribute"))
            if (isinstance(node, ast.ImportFrom) and node.module == "string"
                    and any(alias.name == "Template" for alias in node.names)):
                template_imports.append((path, node.lineno))
            if isinstance(node, ast.ClassDef):
                if any((isinstance(base, ast.Name) and base.id == "Template")
                       or (isinstance(base, ast.Attribute)
                           and base.attr == "Template") for base in node.bases):
                    subclasses.append((path, node.lineno))
    expected_refs = {
        ("pipes.py", 104, "name"),
        ("string.py", 175, "name"),
        ("logging/__init__.py", 510, "name"),
        ("logging/__init__.py", 517, "name"),
    }
    if (set(template_refs) != expected_refs
            or template_imports != [("logging/__init__.py", 29)]
            or subclasses):
        return {}
    source = files["string.py"]
    try:
        tree = ast.parse(source, filename="string.py")
    except SyntaxError:
        return {}
    classes = [node for node in tree.body
               if isinstance(node, ast.ClassDef) and node.name == "Template"]
    if len(classes) != 1:
        return {}
    methods = [node for node in classes[0].body
               if isinstance(node, ast.FunctionDef)
               and node.name == "__init_subclass__"]
    if len(methods) != 1:
        return {}
    guards = [node for node in ast.walk(methods[0])
              if isinstance(node, ast.If)
              and ast.unparse(node.test) == "'pattern' in cls.__dict__"]
    if len(guards) != 1:
        return {}
    invocations = [node for node in ast.walk(tree)
                   if isinstance(node, ast.Call)
                   and ast.unparse(node.func) == "Template.__init_subclass__"
                   and not node.args and not node.keywords]
    if len(invocations) != 1 or invocations[0].lineno <= guards[0].lineno:
        return {}
    if any(isinstance(node, (ast.Assign, ast.AnnAssign, ast.NamedExpr))
           and any((isinstance(target, ast.Name) and target.id == "pattern")
                   or (isinstance(target, ast.Attribute)
                       and target.attr == "pattern")
                   for target in (node.targets if isinstance(node, ast.Assign)
                                  else [node.target]))
           for node in classes[0].body):
        return {}
    return {guards[0].lineno: False}


def _target_weakrefset_empty_init_line_facts(files):
    """Resolve WeakSet's optional-data guard for pinned production callers."""
    source = files.get("_weakrefset.py") if type(files) is dict else None
    if (type(source) is not bytes
            or hashlib.sha256(source).hexdigest() != WEAKREFSET_SOURCE_SHA256):
        return {}
    try:
        trees = {
            path: ast.parse(candidate, filename=path)
            for path, candidate in files.items()
            if type(candidate) is bytes and path.endswith(".py")
            and "test" not in path.split("/")
        }
    except SyntaxError:
        return {}
    references = []
    imports = []
    subclasses = []
    expected_imports = {
        ("threading.py", 9), ("weakref.py", 22),
        ("_py_abc.py", 1), ("multiprocessing/process.py", 22),
    }
    for path, tree in trees.items():
        parents = {child: node for node in ast.walk(tree)
                   for child in ast.iter_child_nodes(node)}
        for node in ast.walk(tree):
            if isinstance(node, (ast.Name, ast.Attribute)) and (
                    (isinstance(node, ast.Name) and node.id == "WeakSet")
                    or (isinstance(node, ast.Attribute)
                        and node.attr == "WeakSet")):
                kind = "name" if isinstance(node, ast.Name) else "attribute"
                references.append((path, node.lineno, kind))
                parent = parents.get(node)
                if isinstance(parent, ast.Call) and parent.func is node:
                    if parent.args or parent.keywords:
                        return {}
            if (isinstance(node, ast.ImportFrom)
                    and node.module in ("weakref", "_weakrefset")
                    and any(alias.name == "WeakSet" for alias in node.names)):
                imports.append((path, node.lineno))
            if isinstance(node, ast.ClassDef) and any(
                    (isinstance(base, ast.Name) and base.id == "WeakSet")
                    or (isinstance(base, ast.Attribute)
                        and base.attr == "WeakSet") for base in node.bases):
                subclasses.append((path, node.lineno))
    expected_references = {
        ("threading.py", 849, "name"),
        ("weakref.py", 36, "name"),
        ("_py_abc.py", 48, "name"), ("_py_abc.py", 49, "name"),
        ("_py_abc.py", 50, "name"), ("_py_abc.py", 79, "name"),
        ("_py_abc.py", 118, "name"),
        ("asyncio/base_events.py", 434, "attribute"),
        ("asyncio/tasks.py", 986, "attribute"),
        ("asyncio/windows_events.py", 254, "attribute"),
        ("asyncio/windows_events.py", 425, "attribute"),
        ("asyncio/windows_events.py", 427, "attribute"),
        ("logging/__init__.py", 260, "attribute"),
        ("multiprocessing/process.py", 439, "name"),
    }
    if (set(references) != expected_references
            or set(imports) != expected_imports or subclasses):
        return {}
    try:
        tree = ast.parse(source, filename="_weakrefset.py")
    except SyntaxError:
        return {}
    classes = [node for node in tree.body
               if isinstance(node, ast.ClassDef) and node.name == "WeakSet"]
    if len(classes) != 1:
        return {}
    inits = [node for node in classes[0].body
             if isinstance(node, ast.FunctionDef) and node.name == "__init__"]
    if len(inits) != 1:
        return {}
    args = inits[0].args
    guards = [node for node in ast.walk(inits[0])
              if isinstance(node, ast.If)
              and ast.unparse(node.test) == "data is not None"]
    if (len(args.args) != 2 or args.args[0].arg != "self"
            or args.args[1].arg != "data" or len(args.defaults) != 1
            or not isinstance(args.defaults[0], ast.Constant)
            or args.defaults[0].value is not None
            or len(args.posonlyargs) != 0
            or args.vararg is not None or args.kwonlyargs or args.kwarg is not None
            or len(guards) != 1
            or any(isinstance(node, ast.Name) and node.id == "data"
                   and isinstance(node.ctx, (ast.Store, ast.Del))
                   for node in ast.walk(inits[0]))):
        return {}
    return {guards[0].lineno: False}


def _target_copyreg_pickle_callable_line_facts(files):
    """Resolve copyreg's argument guard for every pinned production caller."""
    if type(files) is not dict:
        return {}
    expected_hashes = {
        "copyreg.py": COPYREG_SOURCE_SHA256,
        "typing.py": TYPING_SOURCE_SHA256,
        "re/__init__.py": RE_SOURCE_SHA256,
    }
    if any(type(files.get(path)) is not bytes
           or hashlib.sha256(files[path]).hexdigest() != digest
           for path, digest in expected_hashes.items()):
        return {}
    try:
        trees = {
            path: ast.parse(source, filename=path)
            for path, source in files.items()
            if type(source) is bytes and path.endswith(".py")
            and "test" not in path.split("/")
        }
    except SyntaxError:
        return {}
    expected_imports = {
        ("typing.py", 26), ("idlelib/rpc.py", 30),
        ("multiprocessing/reduction.py", 11), ("re/__init__.py", 338),
    }
    expected_calls = {
        ("copyreg.py", 31, "pickle(complex, pickle_complex, complex)"),
        ("copyreg.py", 37, "pickle(type(int | str), pickle_union)"),
        ("typing.py", 1842,
         "copyreg.pickle(ParamSpecArgs, _pickle_psargs)"),
        ("typing.py", 1847,
         "copyreg.pickle(ParamSpecKwargs, _pickle_pskwargs)"),
        ("re/__init__.py", 343,
         "copyreg.pickle(Pattern, _pickle, _compile)"),
    }
    expected_module_refs = {
        ("typing.py", 1842), ("typing.py", 1847),
        ("idlelib/rpc.py", 67), ("multiprocessing/reduction.py", 36),
        ("re/__init__.py", 343),
    }
    imports = []
    calls = []
    constructor_calls = []
    module_refs = []
    for path, tree in trees.items():
        parents = {child: node for node in ast.walk(tree)
                   for child in ast.iter_child_nodes(node)}
        dynamic_import_aliases = {
            alias.asname or alias.name
            for node in ast.walk(tree)
            if isinstance(node, ast.ImportFrom)
            and node.module in ("builtins", "importlib")
            for alias in node.names
            if ((node.module == "builtins" and alias.name == "__import__")
                or (node.module == "importlib" and alias.name == "import_module"))
        }
        for node in ast.walk(tree):
            if isinstance(node, ast.Import) and any(
                    alias.name == "copyreg" for alias in node.names):
                if any(alias.name == "copyreg" and alias.asname is not None
                       for alias in node.names):
                    return {}
                imports.append((path, node.lineno))
            if isinstance(node, ast.Name) and node.id == "copyreg":
                module_refs.append((path, node.lineno))
            if (isinstance(node, ast.ImportFrom) and node.module == "copyreg"
                    and (any(alias.name in ("pickle", "constructor", "*")
                             for alias in node.names))):
                return {}
            if (isinstance(node, ast.ImportFrom)
                    and node.module in ("builtins", "importlib")
                    and any(alias.name == "*" for alias in node.names)):
                return {}
            if (isinstance(node, ast.Call)
                    and isinstance(node.func, ast.Name)
                    and (node.func.id == "__import__"
                         or node.func.id in dynamic_import_aliases)
                    and node.args and isinstance(node.args[0], ast.Constant)
                    and node.args[0].value == "copyreg"):
                return {}
            if (isinstance(node, ast.Call)
                    and isinstance(node.func, ast.Attribute)
                    and node.func.attr in ("__import__", "import_module")
                    and node.args and isinstance(node.args[0], ast.Constant)
                    and node.args[0].value == "copyreg"):
                return {}
            if (isinstance(node, ast.Attribute) and node.attr == "pickle"
                    and isinstance(node.value, ast.Name)
                    and node.value.id == "copyreg"):
                parent = parents.get(node)
                if not isinstance(parent, ast.Call) or parent.func is not node:
                    return {}
                calls.append((path, node.lineno, ast.unparse(parent)))
                if (parent.keywords or len(parent.args) not in (2, 3)
                        or not isinstance(parent.args[1], ast.Name)):
                    return {}
            if (path == "copyreg.py" and isinstance(node, ast.Call)
                    and isinstance(node.func, ast.Name)
                    and node.func.id == "pickle"):
                calls.append((path, node.lineno, ast.unparse(node)))
                if (node.keywords or len(node.args) not in (2, 3)
                        or not isinstance(node.args[1], ast.Name)):
                    return {}
            if isinstance(node, ast.Call) and (
                    (isinstance(node.func, ast.Name)
                     and node.func.id == "constructor")
                    or (isinstance(node.func, ast.Attribute)
                        and node.func.attr == "constructor")):
                constructor_calls.append((path, node.lineno, ast.unparse(node)))
    if (set(imports) != expected_imports or set(calls) != expected_calls
            or set(module_refs) != expected_module_refs):
        return {}
    for path, _, expression in expected_calls:
        tree = trees[path]
        call = next((node for node in ast.walk(tree)
                     if isinstance(node, ast.Call)
                     and ast.unparse(node) == expression), None)
        if call is None:
            return {}
        function_name = call.args[1].id
        defining_tree = trees["copyreg.py"] if path == "copyreg.py" else tree
        if not any(isinstance(node, ast.FunctionDef)
                   and node.name == function_name
                   for node in defining_tree.body):
            return {}
    source = files["copyreg.py"]
    try:
        tree = ast.parse(source, filename="copyreg.py")
    except SyntaxError:
        return {}
    functions = [node for node in tree.body
                 if isinstance(node, ast.FunctionDef) and node.name == "pickle"]
    if len(functions) != 1:
        return {}
    function = functions[0]
    guards = [node for node in ast.walk(function)
              if isinstance(node, ast.If)
              and ast.unparse(node.test) == "not callable(pickle_function)"]
    if len(guards) != 1:
        return {}
    args = function.args
    if (len(args.args) != 3
            or [arg.arg for arg in args.args]
            != ["ob_type", "pickle_function", "constructor_ob"]
            or len(args.defaults) != 1
            or not isinstance(args.defaults[0], ast.Constant)
            or args.defaults[0].value is not None):
        return {}
    constructor_functions = [node for node in tree.body
                             if isinstance(node, ast.FunctionDef)
                             and node.name == "constructor"]
    if len(constructor_functions) != 1:
        return {}
    constructor_function = constructor_functions[0]
    constructor_guards = [node for node in ast.walk(constructor_function)
                          if isinstance(node, ast.If)
                          and ast.unparse(node.test) == "not callable(object)"]
    if (len(constructor_guards) != 1
            or len(constructor_function.args.args) != 1
            or constructor_function.args.args[0].arg != "object"
            or constructor_calls != [(
                "copyreg.py", 20, "constructor(constructor_ob)",
            )]):
        return {}
    constructor_guard = [node for node in ast.walk(function)
                         if isinstance(node, ast.If)
                         and ast.unparse(node.test) == "constructor_ob is not None"]
    if (len(constructor_guard) != 1
            or not any(isinstance(node, ast.Call)
                       and ast.unparse(node.func) == "constructor"
                       and len(node.args) == 1
                       and isinstance(node.args[0], ast.Name)
                       and node.args[0].id == "constructor_ob"
                       for node in ast.walk(constructor_guard[0]))):
        return {}
    explicit_constructor_args = set()
    for path, _, expression in expected_calls:
        tree_for_call = trees[path]
        call = next((node for node in ast.walk(tree_for_call)
                     if isinstance(node, ast.Call)
                     and ast.unparse(node) == expression), None)
        if call is not None and len(call.args) == 3:
            explicit_constructor_args.add(
                (path, call.lineno, ast.unparse(call.args[2]))
            )
    if explicit_constructor_args != {
            ("copyreg.py", 31, "complex"),
            ("re/__init__.py", 343, "_compile"),
    }:
        return {}
    re_tree = trees["re/__init__.py"]
    if not any(isinstance(node, ast.FunctionDef) and node.name == "_compile"
               for node in re_tree.body):
        return {}
    if any(isinstance(node, ast.Name) and node.id == "complex"
           and isinstance(node.ctx, (ast.Store, ast.Del))
           for node in tree.body):
        return {}
    return {guards[0].lineno: False,
            constructor_guards[0].lineno: False}


def _target_copyreg_constructor_observation_facts(files):
    """Bound all source-visible constructor_ob outcomes at copyreg.pickle calls."""
    callable_facts = _target_copyreg_pickle_callable_line_facts(files)
    if (type(callable_facts) is not dict or len(callable_facts) != 2
            or any(type(line) is not int or type(value) is not bool or value
                   for line, value in callable_facts.items())):
        return {}
    expected_calls = (
        ("copyreg.py", "pickle(complex, pickle_complex, complex)", True),
        ("copyreg.py", "pickle(type(int | str), pickle_union)", False),
        ("typing.py", "copyreg.pickle(ParamSpecArgs, _pickle_psargs)", False),
        ("typing.py", "copyreg.pickle(ParamSpecKwargs, _pickle_pskwargs)", False),
        ("re/__init__.py", "copyreg.pickle(Pattern, _pickle, _compile)", True),
    )
    for path, _, _ in expected_calls:
        source = files.get(path) if type(files) is dict else None
        if type(source) is not bytes:
            return {}
    try:
        trees = {
            path: ast.parse(files[path], filename=path)
            for path in {row[0] for row in expected_calls}
        }
    except SyntaxError:
        return {}
    copyreg_tree = trees.get("copyreg.py")
    if copyreg_tree is None or not any(
            isinstance(node, ast.If) and node.lineno == 19
            and ast.unparse(node.test) == "constructor_ob is not None"
            for node in ast.walk(copyreg_tree)):
        return {}
    observations = []
    for path, expression, expected_non_none in expected_calls:
        matches = [node for node in ast.walk(trees[path])
                   if isinstance(node, ast.Call) and ast.unparse(node) == expression]
        if len(matches) != 1:
            return {}
        call = matches[0]
        non_none = len(call.args) == 3
        if (call.keywords or non_none != expected_non_none
                or (non_none and (not isinstance(call.args[2], ast.Name)
                                  or call.args[2].id not in ("complex", "_compile")))):
            return {}
        observations.append(non_none)
    if tuple(observations) != (True, False, False, False, True):
        return {}
    return {("copyreg", "copyreg.py", 19): (False, True)}


def _target_opcode_pseudo_op_condition_facts(files):
    """Bound pseudo_op's any(res) outcomes to all pinned registrations."""
    source = files.get("opcode.py") if type(files) is dict else None
    if (type(source) is not bytes
            or hashlib.sha256(source).hexdigest() != OPCODE_SOURCE_SHA256):
        return {}
    try:
        tree = ast.parse(source, filename="opcode.py")
    except SyntaxError:
        return {}
    expected_calls = {
        (262, "pseudo_op('SETUP_FINALLY', 256, ['NOP'])"),
        (264, "pseudo_op('SETUP_CLEANUP', 257, ['NOP'])"),
        (266, "pseudo_op('SETUP_WITH', 258, ['NOP'])"),
        (268, "pseudo_op('POP_BLOCK', 259, ['NOP'])"),
        (270, "pseudo_op('JUMP', 260, ['JUMP_FORWARD', 'JUMP_BACKWARD'])"),
        (271, "pseudo_op('JUMP_NO_INTERRUPT', 261, "
              "['JUMP_FORWARD', 'JUMP_BACKWARD_NO_INTERRUPT'])"),
        (273, "pseudo_op('LOAD_METHOD', 262, ['LOAD_ATTR'])"),
        (274, "pseudo_op('LOAD_SUPER_METHOD', 263, ['LOAD_SUPER_ATTR'])"),
        (275, "pseudo_op('LOAD_ZERO_SUPER_METHOD', 264, ['LOAD_SUPER_ATTR'])"),
        (276, "pseudo_op('LOAD_ZERO_SUPER_ATTR', 265, ['LOAD_SUPER_ATTR'])"),
        (278, "pseudo_op('STORE_FAST_MAYBE_NULL', 266, ['STORE_FAST'])"),
    }
    actual_calls = {
        (node.lineno, ast.unparse(node))
        for node in ast.walk(tree)
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
        and node.func.id == "pseudo_op"
    }
    pseudo_functions = [node for node in tree.body
                        if isinstance(node, ast.FunctionDef)
                        and node.name == "pseudo_op"]
    expected_function = ast.parse(
        "def pseudo_op(name, op, real_ops):\n"
        "    def_op(name, op)\n"
        "    _pseudo_ops[name] = real_ops\n"
        "    for oplist in oplists:\n"
        "        res = [opmap[rop] in oplist for rop in real_ops]\n"
        "        if any(res):\n"
        "            assert all(res)\n"
        "            oplist.append(op)\n"
    ).body[0]
    opcode_list_assignments = [node for node in tree.body
                               if isinstance(node, ast.Assign)
                               and any(isinstance(target, ast.Name)
                                       and target.id == "oplists"
                                       for target in node.targets)]
    guards = [node for node in ast.walk(tree)
              if isinstance(node, ast.If) and node.lineno == 72
              and ast.unparse(node.test) == "any(res)"]
    if (actual_calls != expected_calls or len(pseudo_functions) != 1
            or ast.dump(pseudo_functions[0], include_attributes=False)
            != ast.dump(expected_function, include_attributes=False)
            or len(opcode_list_assignments) != 1 or len(guards) != 1
            or ast.unparse(opcode_list_assignments[0])
            != "oplists = [hasarg, hasconst, hasname, hasjrel, hasjabs, "
               "haslocal, hascompare, hasfree, hasexc]"):
        return {}
    return {("opcode", "opcode.py", 72): (False, True)}


def _target_json_encoder_argument_condition_facts(files):
    """Bind JSONEncoder's import-time separators, indent, and default guards."""
    if type(files) is not dict:
        return {}
    expected_hashes = {
        "json/encoder.py": JSON_ENCODER_SOURCE_SHA256,
        "json/__init__.py": JSON_PACKAGE_SOURCE_SHA256,
    }
    if any(type(files.get(path)) is not bytes
           or hashlib.sha256(files[path]).hexdigest() != digest
           for path, digest in expected_hashes.items()):
        return {}
    try:
        trees = {
            path: ast.parse(source, filename=path)
            for path, source in files.items()
            if type(source) is bytes and path.endswith(".py")
            and "test" not in path.split("/")
        }
    except SyntaxError:
        return {}
    imports = []
    references = []
    classes = []
    constructors = []
    for path, tree in trees.items():
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom) and any(
                    alias.name == "JSONEncoder" for alias in node.names):
                imports.append((path, node.lineno, node.level, node.module,
                                tuple((alias.name, alias.asname)
                                      for alias in node.names)))
            if isinstance(node, ast.Name) and node.id == "JSONEncoder":
                references.append((path, node.lineno, type(node.ctx)))
            if isinstance(node, ast.Attribute) and node.attr == "JSONEncoder":
                references.append((path, node.lineno, ast.Load))
            if isinstance(node, ast.ClassDef) and node.name == "JSONEncoder":
                classes.append((path, node))
            if (isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
                    and node.func.id == "JSONEncoder"):
                constructors.append((path, node.lineno, ast.unparse(node)))
            if (isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
                    and node.func.attr == "JSONEncoder"):
                constructors.append((path, node.lineno, ast.unparse(node)))
    if (imports != [("json/__init__.py", 107, 1, "encoder",
                     (("JSONEncoder", None),))]
            or {path for path, _, _ in references}
            != {"json/__init__.py"}
            or len(classes) != 1 or classes[0][0] != "json/encoder.py"
            or len(classes[0][1].bases) != 1
            or not isinstance(classes[0][1].bases[0], ast.Name)
            or classes[0][1].bases[0].id != "object"
            or len(constructors) != 1
            or constructors[0][0] != "json/__init__.py"
            or constructors[0][1] != 110
            or constructors[0][2] != (
                "JSONEncoder(skipkeys=False, ensure_ascii=True, "
                "check_circular=True, allow_nan=True, indent=None, "
                "separators=None, default=None)")):
        return {}
    constructor = ast.parse(constructors[0][2], mode="eval").body
    expected_keywords = {
        "skipkeys": False, "ensure_ascii": True,
        "check_circular": True, "allow_nan": True,
        "indent": None, "separators": None, "default": None,
    }
    if (constructor.args
            or any(keyword.arg is None for keyword in constructor.keywords)
            or len(constructor.keywords) != len(expected_keywords)
            or {keyword.arg: ast.unparse(keyword.value)
                for keyword in constructor.keywords} != {
                    name: repr(value) if type(value) is not bool else str(value)
                    for name, value in expected_keywords.items()}):
        return {}
    encoder_class = classes[0][1]
    initializers = [node for node in encoder_class.body
                    if isinstance(node, ast.FunctionDef)
                    and node.name == "__init__"]
    if len(initializers) != 1:
        return {}
    initializer = initializers[0]
    positional_names = [argument.arg for argument in initializer.args.args]
    keyword_names = [argument.arg for argument in initializer.args.kwonlyargs]
    if (positional_names != ["self"]
            or keyword_names != ["skipkeys", "ensure_ascii", "check_circular",
                                 "allow_nan", "sort_keys", "indent", "separators",
                                 "default"]
            or len(initializer.args.kw_defaults) != 8
            or any(not isinstance(value, ast.Constant)
                   for value in initializer.args.kw_defaults)
            or [value.value for value in initializer.args.kw_defaults]
            != [False, True, True, True, False, None, None, None]):
        return {}
    guard_lines = {node.lineno: ast.unparse(node.test)
                   for node in ast.walk(initializer)
                   if isinstance(node, ast.If)}
    if guard_lines != {
            154: "separators is not None", 156: "indent is not None",
            158: "default is not None"}:
        return {}
    return {
        ("json.encoder", "json/encoder.py", line): (False,)
        for line in (154, 156, 158)
    }


def _target_hashlib_name_condition_facts(files):
    """Bind hashlib's name guards to its module-init algorithm tuple."""
    source = files.get("hashlib.py") if type(files) is dict else None
    if (type(source) is not bytes
            or hashlib.sha256(source).hexdigest() != HASHLIB_SOURCE_SHA256):
        return {}
    try:
        trees = {
            path: ast.parse(data, filename=path)
            for path, data in files.items()
            if type(data) is bytes and path.endswith(".py")
            and "test" not in path.split("/")
        }
    except SyntaxError:
        return {}
    tree = trees.get("hashlib.py")
    if tree is None:
        return {}
    supported = (
        "md5", "sha1", "sha224", "sha256", "sha384", "sha512",
        "blake2b", "blake2s", "sha3_224", "sha3_256", "sha3_384",
        "sha3_512", "shake_128", "shake_256",
    )
    assignments = {}
    for node in tree.body:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id in (
                        "__always_supported", "__block_openssl_constructor"):
                    assignments.setdefault(target.id, []).append(node.value)
    if (set(assignments) != {"__always_supported", "__block_openssl_constructor"}
            or any(len(values) != 1 for values in assignments.values())):
        return {}
    try:
        if (ast.literal_eval(assignments["__always_supported"][0]) != supported
                or ast.literal_eval(assignments["__block_openssl_constructor"][0])
                != {"blake2b", "blake2s"}):
            return {}
    except (ValueError, TypeError):
        return {}
    builtin_functions = [node for node in tree.body
                         if isinstance(node, ast.FunctionDef)
                         and node.name == "__get_builtin_constructor"]
    openssl_functions = [node for node in tree.body
                         if isinstance(node, ast.FunctionDef)
                         and node.name == "__get_openssl_constructor"]
    loops = [node for node in tree.body if isinstance(node, ast.For)
             and ast.unparse(node.target) == "__func_name"
             and ast.unparse(node.iter) == "__always_supported"]
    if (len(builtin_functions) != 1 or len(openssl_functions) != 1
            or len(loops) != 1
            or [arg.arg for arg in builtin_functions[0].args.args] != ["name"]
            or [arg.arg for arg in openssl_functions[0].args.args] != ["name"]):
        return {}
    loop_calls = [node for node in ast.walk(loops[0])
                  if isinstance(node, ast.Call)
                  and isinstance(node.func, ast.Name)
                  and node.func.id == "__get_hash"]
    if (len(loop_calls) != 1
            or ast.unparse(loop_calls[0]) != "__get_hash(__func_name)"):
        return {}
    expected_guards = {
        ("__get_builtin_constructor", 88): "name in {'SHA1', 'sha1'}",
        ("__get_builtin_constructor", 91): "name in {'MD5', 'md5'}",
        ("__get_builtin_constructor", 94):
            "name in {'SHA256', 'sha256', 'SHA224', 'sha224'}",
        ("__get_builtin_constructor", 98):
            "name in {'SHA512', 'sha512', 'SHA384', 'sha384'}",
        ("__get_builtin_constructor", 102): "name in {'blake2b', 'blake2s'}",
        ("__get_builtin_constructor", 106):
            "name in {'sha3_224', 'sha3_256', 'sha3_384', 'sha3_512'}",
        ("__get_builtin_constructor", 112): "name in {'shake_128', 'shake_256'}",
        ("__get_openssl_constructor", 127):
            "name in __block_openssl_constructor",
    }

    actual_guards = {
        (function.name, node.lineno): ast.unparse(node.test)
        for function in (builtin_functions[0], openssl_functions[0])
        for node in ast.walk(function)
        if isinstance(node, ast.If)
        and (function.name, node.lineno) in expected_guards
    }
    if actual_guards != expected_guards:
        return {}
    private_names = {
        "__get_builtin_constructor", "__get_openssl_constructor", "__get_hash",
        "__always_supported", "__block_openssl_constructor",
    }
    for path, other_tree in trees.items():
        if path == "hashlib.py":
            continue
        for node in ast.walk(other_tree):
            if (isinstance(node, ast.ImportFrom) and node.module == "hashlib"
                    and any(alias.name in private_names for alias in node.names)):
                return {}
            if (isinstance(node, ast.Attribute) and node.attr in private_names
                    or isinstance(node, ast.Name) and node.id in private_names):
                return {}
        module_aliases = {
            alias.asname or alias.name
            for node in ast.walk(other_tree) if isinstance(node, ast.Import)
            for alias in node.names if alias.name == "hashlib"
        }
        new_aliases = {
            alias.asname or alias.name
            for node in ast.walk(other_tree)
            if isinstance(node, ast.ImportFrom) and node.module == "hashlib"
            for alias in node.names if alias.name == "new"
        }
        parents = {child: parent for parent in ast.walk(other_tree)
                   for child in ast.iter_child_nodes(parent)}
        for node in ast.walk(other_tree):
            if not isinstance(node, ast.Call):
                continue
            parent = parents.get(node)
            inside_function = False
            while parent is not None:
                if isinstance(parent, (ast.FunctionDef, ast.AsyncFunctionDef, ast.Lambda)):
                    inside_function = True
                    break
                parent = parents.get(parent)
            if inside_function:
                continue
            if (isinstance(node.func, ast.Name) and node.func.id in new_aliases
                    or isinstance(node.func, ast.Attribute)
                    and node.func.attr == "new"
                    and isinstance(node.func.value, ast.Name)
                    and node.func.value.id in module_aliases):
                return {}
    return {
        ("hashlib", "hashlib.py", line): (False, True)
        for _, line in expected_guards
    }


def _target_hashlib_builtin_fallback_file_candidates(
        files, condition_facts, target_image_facts):
    """Join pinned hashlib fallback branches to target-image file candidates."""
    if (type(files) is not dict or type(condition_facts) is not dict
            or type(target_image_facts) is not dict):
        return []
    source = files.get("hashlib.py")
    if (type(source) is not bytes
            or hashlib.sha256(source).hexdigest() != HASHLIB_SOURCE_SHA256):
        return []
    try:
        tree = ast.parse(source, filename="hashlib.py")
    except SyntaxError:
        return []
    functions = [node for node in tree.body
                 if isinstance(node, ast.FunctionDef)
                 and node.name == "__get_builtin_constructor"]
    if len(functions) != 1:
        return []
    expected_lines = {row[0] for row in HASHLIB_BUILTIN_FALLBACK_BRANCHES}
    branch_nodes = {
        node.lineno: node for node in ast.walk(functions[0])
        if isinstance(node, ast.If) and node.lineno in expected_lines
    }
    if set(branch_nodes) != expected_lines:
        return []

    image_extensions = target_image_facts.get("hashlib_extension_facts")
    if type(image_extensions) is not dict:
        return []
    candidates = []
    for line, condition, names, module, image_path, body in (
            HASHLIB_BUILTIN_FALLBACK_BRANCHES):
        node = branch_nodes.get(line)
        image_fact = image_extensions.get(image_path)
        expected_digest = HASHLIB_EXTENSION_FACTS.get(image_path)
        if (node is None or ast.unparse(node.test) != condition
                or tuple(ast.unparse(statement) for statement in node.body) != body
                or condition_facts.get(("hashlib", "hashlib.py", line))
                != (False, True)
                or type(image_fact) is not dict
                or image_fact.get("sha256") != expected_digest
                or type(image_fact.get("size")) is not int
                or not 0 <= image_fact["size"] <= MAX_S15_FILE_BYTES):
            return []
        candidates.append({
            "source_path": "hashlib.py",
            "guard_line": line,
            "algorithm_names": list(names),
            "fallback_module": module,
            "image_path": image_path,
            "sha256": expected_digest,
            "size": image_fact["size"],
            "evidence_scope": "STATIC_BUILTIN_FALLBACK_FILE_CANDIDATE",
            "import_attempt_observed": False,
            "constructor_success_observed": False,
        })
    return candidates


def _target_re_compile_input_candidates(files, modules):
    """List direct module-body re.compile argument shapes in source candidates."""
    if type(files) is not dict or type(modules) is not tuple:
        return []
    try:
        source_rows = _module_source_rows(files, modules)
    except (TypeError, ValueError):
        return []
    candidates = []
    for row in source_rows:
        path = row["source_path"]
        source = files.get(path)
        if type(source) is not bytes:
            return []
        try:
            tree = ast.parse(source.decode("utf-8"), filename=path)
        except (UnicodeError, SyntaxError):
            return []

        module_alias_lines = {}
        imported_compile_lines = {}
        rebound_lines = {}
        compile_attribute_rebound_lines = {}
        module_nodes = []

        class ModuleBodyVisitor(ast.NodeVisitor):
            def visit_FunctionDef(self, node):
                for decorator in node.decorator_list:
                    self.visit(decorator)
                self.visit(node.args)
                if node.returns is not None:
                    self.visit(node.returns)

            visit_AsyncFunctionDef = visit_FunctionDef

            def visit_Lambda(self, node):
                self.visit(node.args)

            def visit_ClassDef(self, node):
                for decorator in node.decorator_list:
                    self.visit(decorator)

            def visit_Name(self, node):
                if isinstance(node.ctx, (ast.Store, ast.Del)):
                    rebound_lines.setdefault(node.id, []).append(
                        (node.lineno, node.col_offset)
                    )

            def visit_Attribute(self, node):
                if (node.attr == "compile"
                        and isinstance(node.value, ast.Name)
                        and isinstance(node.ctx, (ast.Store, ast.Del))):
                    compile_attribute_rebound_lines.setdefault(
                        node.value.id, []
                    ).append((node.lineno, node.col_offset))
                self.generic_visit(node)

            def visit_Import(self, node):
                for imported in node.names:
                    if imported.name == "re":
                        module_alias_lines.setdefault(
                            imported.asname or "re", []
                        ).append((node.end_lineno, node.end_col_offset))

            def visit_ImportFrom(self, node):
                if node.module == "re":
                    for imported in node.names:
                        if imported.name == "compile":
                            imported_compile_lines.setdefault(
                                imported.asname or imported.name, []
                            ).append((node.end_lineno, node.end_col_offset))

            def visit_Call(self, node):
                module_nodes.append(node)
                self.generic_visit(node)

        visitor = ModuleBodyVisitor()
        for node in tree.body:
            visitor.visit(node)

        for call in module_nodes:
            if not call.args:
                continue
            api_form = None
            function = call.func
            alias_lines = ()
            if (isinstance(function, ast.Attribute)
                    and function.attr == "compile"
                    and isinstance(function.value, ast.Name)
                    and function.value.id in module_alias_lines):
                api_form = "re_module_compile_attribute"
                alias_lines = module_alias_lines[function.value.id]
            elif (isinstance(function, ast.Name)
                    and function.id in imported_compile_lines):
                api_form = "re_imported_compile_name"
                alias_lines = imported_compile_lines[function.id]
            if api_form is not None:
                call_position = (call.lineno, call.col_offset)
                rebound_name = (function.value.id
                                if isinstance(function, ast.Attribute)
                                else function.id)
                alias_lines = tuple(
                    import_line for import_line in alias_lines
                    if import_line <= call_position
                    and not any(
                        import_line < store_line < call_position
                        for store_line in rebound_lines.get(rebound_name, ())
                    )
                    and (not isinstance(function, ast.Attribute)
                         or not any(
                             import_line < store_line < call_position
                             for store_line in compile_attribute_rebound_lines.get(
                                 rebound_name, ()
                             )
                         ))
                )
                if not alias_lines:
                    api_form = None
            if api_form is None:
                continue

            argument = call.args[0]
            argument_sha256 = None
            try:
                literal = ast.literal_eval(argument)
            except (ValueError, TypeError, SyntaxError):
                literal = None
            if type(literal) is str:
                argument_kind = "STRING_LITERAL"
                argument_sha256 = hashlib.sha256(
                    literal.encode("utf-8")
                ).hexdigest()
            elif type(literal) is bytes:
                argument_kind = "BYTES_LITERAL"
                argument_sha256 = hashlib.sha256(literal).hexdigest()
            elif (isinstance(argument, ast.BinOp)
                    and isinstance(argument.op, ast.Mod)
                    and isinstance(argument.left, ast.Constant)
                    and type(argument.left.value) is str):
                argument_kind = "STRING_FORMAT_EXPRESSION"
            else:
                argument_kind = "UNRESOLVED_EXPRESSION"
            expanded_keywords = any(keyword.arg is None for keyword in call.keywords)
            flag_keywords = [keyword.value for keyword in call.keywords
                             if keyword.arg == "flags"]
            if (len(call.args) == 1 and not flag_keywords
                    and not expanded_keywords):
                flags_argument_kind = "OMITTED"
                flags_literal_value = None
                flags_argument_expression = None
            elif (len(call.args) == 2 and not flag_keywords
                    and not expanded_keywords):
                flags_argument = call.args[1]
                flags_argument_expression = ast.unparse(flags_argument)
                flags_argument_kind = "UNRESOLVED_EXPRESSION"
                flags_literal_value = None
                try:
                    flags_literal = ast.literal_eval(flags_argument)
                except (ValueError, TypeError, SyntaxError):
                    flags_literal = None
                if type(flags_literal) is int:
                    flags_argument_kind = "INT_LITERAL"
                    flags_literal_value = flags_literal
            elif (len(call.args) == 1 and len(flag_keywords) == 1
                    and not expanded_keywords):
                flags_argument_expression = ast.unparse(flag_keywords[0])
                flags_argument_kind = "UNRESOLVED_EXPRESSION"
                flags_literal_value = None
                try:
                    flags_literal = ast.literal_eval(flag_keywords[0])
                except (ValueError, TypeError, SyntaxError):
                    flags_literal = None
                if type(flags_literal) is int:
                    flags_argument_kind = "INT_LITERAL"
                    flags_literal_value = flags_literal
            else:
                flags_argument_kind = "UNRESOLVED_EXPRESSION"
                flags_literal_value = None
                flags_argument_expression = None
            candidates.append({
                "module": row["module"],
                "source_path": path,
                "source_sha256": row["source_sha256"],
                "line": call.lineno,
                "api_form": api_form,
                "argument_kind": argument_kind,
                "argument_sha256": argument_sha256,
                "flags_argument_kind": flags_argument_kind,
                "flags_literal_value": flags_literal_value,
                "flags_argument_expression": flags_argument_expression,
                "evidence_scope": "MODULE_BODY_RE_COMPILE_ARGUMENT_CANDIDATE",
                "compile_call_observed": False,
                "pattern_parse_observed": False,
            })
            if len(candidates) > MAX_RE_COMPILE_INPUT_CANDIDATES:
                return []
    return candidates


def _regex_inline_flag_directive_candidates(pattern):
    """Find lexical inline-flag group prefixes without claiming regex parsing."""
    if type(pattern) is bytes:
        text = pattern.decode("latin-1")
    elif type(pattern) is str:
        text = pattern
    else:
        return None

    candidates = []
    in_character_class = False
    class_first_character = False
    index = 0
    while index < len(text):
        character = text[index]
        if character == "\\":
            index += 2
            continue
        if in_character_class:
            if character == "]" and not class_first_character:
                in_character_class = False
            elif character != "^" or not class_first_character:
                class_first_character = False
            index += 1
            continue
        if character == "[":
            in_character_class = True
            class_first_character = True
            index += 1
            continue
        if (character != "(" or index + 2 >= len(text)
                or text[index + 1] != "?"):
            index += 1
            continue

        cursor = index + 2
        enabled = []
        disabled = []
        target = enabled
        if text[cursor] == "-":
            target = disabled
            cursor += 1
        while cursor < len(text) and text[cursor] in "aiLmsux":
            target.append(text[cursor])
            cursor += 1
            if cursor < len(text) and text[cursor] == "-" and target is enabled:
                target = disabled
                cursor += 1
        if ((enabled or disabled) and cursor < len(text)
                and text[cursor] in ":)" and "x" in enabled + disabled):
            candidates.append({
                "offset": index,
                "scope": "GLOBAL" if text[cursor] == ")" else "SCOPED",
                "enabled_flags": "".join(enabled),
                "disabled_flags": "".join(disabled),
                "evidence_scope": "LEXICAL_INLINE_REGEX_FLAG_CANDIDATE",
            })
            index = cursor + 1
        else:
            index += 1
    return candidates


def _regex_verbose_ignored_syntax_candidates(pattern, whitespace):
    """Locate lexical VERBOSE whitespace/comments without parsing patterns."""
    if type(pattern) is bytes:
        text = pattern.decode("latin-1")
    elif type(pattern) is str:
        text = pattern
    else:
        return None
    if (type(whitespace) is not frozenset
            or any(type(character) is not str or len(character) != 1
                   for character in whitespace)):
        return None

    candidates = []
    in_character_class = False
    class_first_character = False
    index = 0
    while index < len(text):
        character = text[index]
        if character == "\\":
            index += 2
            continue
        if in_character_class:
            if character == "]" and not class_first_character:
                in_character_class = False
            elif character != "^" or not class_first_character:
                class_first_character = False
            index += 1
            continue
        if character == "[":
            in_character_class = True
            class_first_character = True
            index += 1
            continue
        if character in whitespace:
            candidates.append({"offset": index, "kind": "WHITESPACE"})
            index += 1
            continue
        if character == "#":
            candidates.append({"offset": index, "kind": "COMMENT_MARKER"})
            newline = text.find("\n", index + 1)
            index = len(text) if newline < 0 else newline + 1
            continue
        index += 1
    return candidates


def _target_re_compile_cache_path_candidate(files):
    """Bind the pinned cache-before-parser path without claiming a cache hit."""
    source = files.get("re/__init__.py") if type(files) is dict else None
    if (type(source) is not bytes
            or hashlib.sha256(source).hexdigest() != RE_INIT_SOURCE_SHA256):
        return None
    try:
        tree = ast.parse(source.decode("utf-8"), filename="re/__init__.py")
    except (UnicodeError, SyntaxError):
        return None
    functions = [node for node in tree.body
                 if isinstance(node, ast.FunctionDef) and node.name == "_compile"]
    if len(functions) != 1:
        return None
    body = list(functions[0].body)
    if (body and isinstance(body[0], ast.Expr)
            and isinstance(body[0].value, ast.Constant)
            and type(body[0].value.value) is str):
        body.pop(0)
    if (len(body) < 6
            or not isinstance(body[0], ast.If)
            or len(body[0].body) != 1
            or ast.unparse(body[0].test) != "isinstance(flags, RegexFlag)"
            or ast.unparse(body[0].body[0]) != "flags = flags.value"
            or not isinstance(body[1], ast.Try)
            or len(body[1].body) != 1
            or ast.unparse(body[1].body[0])
            != "return _cache2[type(pattern), pattern, flags]"
            or len(body[1].handlers) != 1
            or not isinstance(body[1].handlers[0].type, ast.Name)
            or ast.unparse(body[1].handlers[0].type) != "KeyError"
            or len(body[1].handlers[0].body) != 1
            or not isinstance(body[1].handlers[0].body[0], ast.Pass)
            or ast.unparse(body[2])
            != "key = (type(pattern), pattern, flags)"
            or ast.unparse(body[3]) != "p = _cache.pop(key, None)"
            or not isinstance(body[4], ast.If)
            or ast.unparse(body[4].test) != "p is None"):
        return None
    compile_calls = [node for node in ast.walk(body[4])
                     if isinstance(node, ast.Call)
                     and ast.unparse(node.func) == "_compiler.compile"
                     and [ast.unparse(arg) for arg in node.args]
                     == ["pattern", "flags"]]
    if (len(compile_calls) != 1
            or ast.unparse(body[-1]) != "return p"):
        return None
    return {
        "source_path": "re/__init__.py",
        "source_sha256": RE_INIT_SOURCE_SHA256,
        "flags_normalization_before_cache_lookup": (
            "RegexFlag.value when isinstance(flags, RegexFlag)"
        ),
        "cache_lookup_order": ["_cache2", "_cache"],
        "cache_key_expression": "(type(pattern), pattern, flags)",
        "parser_compile_call_on_both_cache_misses_candidate": True,
        "cache_state_observed": False,
        "cache_lookup_observed": False,
        "parser_entry_observed": False,
        "evidence_scope": "PINNED_RE_COMPILE_CACHE_PATH_CANDIDATE",
    }


def _target_re_tokenizer_access_candidate(files):
    """Bind byte decoding and escaped-character access in the pinned tokenizer."""
    source = files.get("re/_parser.py") if type(files) is dict else None
    if (type(source) is not bytes
            or hashlib.sha256(source).hexdigest() != RE_PARSER_SOURCE_SHA256):
        return None
    try:
        tree = ast.parse(source.decode("utf-8"), filename="re/_parser.py")
    except (UnicodeError, SyntaxError):
        return None
    tokenizers = [node for node in tree.body
                  if isinstance(node, ast.ClassDef) and node.name == "Tokenizer"]
    if len(tokenizers) != 1:
        return None
    class_methods = [node for node in tokenizers[0].body
                     if isinstance(node, ast.FunctionDef)]
    methods = {node.name: node for node in class_methods}
    if (any(name not in methods for name in ("__init__", "__next", "get"))
            or any(sum(node.name == name for node in class_methods) != 1
                   for name in ("__init__", "__next", "get"))):
        return None

    init_body = methods["__init__"].body
    expected_init_prefix = (
        "self.istext = isinstance(string, str)",
        "self.string = string",
    )
    if (len(init_body) != 7
            or tuple(ast.unparse(node) for node in init_body[:2])
            != expected_init_prefix
            or not isinstance(init_body[2], ast.If)
            or ast.unparse(init_body[2].test) != "not self.istext"
            or len(init_body[2].body) != 1
            or ast.unparse(init_body[2].body[0])
            != "string = str(string, 'latin1')"
            or tuple(ast.unparse(node) for node in init_body[3:])
            != ("self.decoded_string = string", "self.index = 0",
                "self.next = None", "self.__next()")):
        return None

    next_body = methods["__next"].body
    if (len(next_body) != 5
            or ast.unparse(next_body[0]) != "index = self.index"
            or not isinstance(next_body[1], ast.Try)
            or len(next_body[1].body) != 1
            or ast.unparse(next_body[1].body[0])
            != "char = self.decoded_string[index]"
            or len(next_body[1].handlers) != 1
            or not isinstance(next_body[1].handlers[0].type, ast.Name)
            or next_body[1].handlers[0].type.id != "IndexError"
            or tuple(ast.unparse(node) for node in next_body[1].handlers[0].body)
            != ("self.next = None", "return")
            or not isinstance(next_body[2], ast.If)):
        return None
    escape_test = next_body[2].test
    if (not isinstance(escape_test, ast.Compare)
            or not isinstance(escape_test.left, ast.Name)
            or escape_test.left.id != "char"
            or len(escape_test.ops) != 1
            or not isinstance(escape_test.ops[0], ast.Eq)
            or len(escape_test.comparators) != 1
            or not isinstance(escape_test.comparators[0], ast.Constant)
            or escape_test.comparators[0].value != "\\"):
        return None
    escape_body = next_body[2].body
    if (len(escape_body) != 2
            or ast.unparse(escape_body[0]) != "index += 1"
            or not isinstance(escape_body[1], ast.Try)
            or len(escape_body[1].body) != 1
            or ast.unparse(escape_body[1].body[0])
            != "char += self.decoded_string[index]"
            or len(escape_body[1].handlers) != 1
            or not isinstance(escape_body[1].handlers[0].type, ast.Name)
            or escape_body[1].handlers[0].type.id != "IndexError"
            or len(escape_body[1].handlers[0].body) != 1
            or not isinstance(escape_body[1].handlers[0].body[0], ast.Raise)
            or ast.unparse(escape_body[1].handlers[0].body[0].cause) != "None"
            or ast.unparse(next_body[3]) != "self.index = index + 1"
            or ast.unparse(next_body[4]) != "self.next = char"):
        return None
    if (not isinstance(escape_body[1].handlers[0].body[0].exc, ast.Call)
            or ast.unparse(escape_body[1].handlers[0].body[0].exc.func) != "error"
            or len(escape_body[1].handlers[0].body[0].exc.args) < 1
            or not isinstance(escape_body[1].handlers[0].body[0].exc.args[0], ast.Constant)
            or escape_body[1].handlers[0].body[0].exc.args[0].value
            != "bad escape (end of pattern)"):
        return None

    get_body = methods["get"].body
    if (len(get_body) != 3
            or ast.unparse(get_body[0]) != "this = self.next"
            or ast.unparse(get_body[1]) != "self.__next()"
            or ast.unparse(get_body[2]) != "return this"):
        return None
    return {
        "source_path": "re/_parser.py",
        "source_sha256": RE_PARSER_SOURCE_SHA256,
        "bytes_to_text_expression": "str(string, 'latin1')",
        "escaped_character_access": "backslash plus following character",
        "trailing_backslash_behavior": "parser error candidate",
        "get_advances_after_returning_current_character": True,
        "tokenizer_execution_observed": False,
        "pattern_parse_observed": False,
        "evidence_scope": "PINNED_RE_TOKENIZER_CHARACTER_ACCESS_CANDIDATE",
    }


def _target_re_parser_sourceget_candidate(files):
    """Bind the parser's local sourceget alias to Tokenizer.get statically."""
    source = files.get("re/_parser.py") if type(files) is dict else None
    if (type(source) is not bytes
            or hashlib.sha256(source).hexdigest() != RE_PARSER_SOURCE_SHA256):
        return None
    try:
        tree = ast.parse(source.decode("utf-8"), filename="re/_parser.py")
    except (UnicodeError, SyntaxError):
        return None
    parsers = [node for node in tree.body
               if isinstance(node, ast.FunctionDef) and node.name == "_parse"]
    tokenizers = [node for node in tree.body
                  if isinstance(node, ast.ClassDef) and node.name == "Tokenizer"]
    if len(parsers) != 1 or len(tokenizers) != 1:
        return None
    assignments = [node for node in ast.walk(parsers[0])
                   if isinstance(node, ast.Assign)
                   and any(isinstance(target, ast.Name)
                           and target.id == "sourceget" for target in node.targets)]
    get_methods = [node for node in tokenizers[0].body
                   if isinstance(node, ast.FunctionDef) and node.name == "get"]
    calls = [node for node in ast.walk(parsers[0])
             if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
             and node.func.id == "sourceget"]
    if (len(assignments) != 1 or len(get_methods) != 1
            or len(get_methods[0].body) != 3
            or not calls
            or ast.unparse(assignments[0]) != "sourceget = source.get"
            or assignments[0].lineno >= min(
                node.lineno for node in calls
            )
            or ast.unparse(get_methods[0].body[0]) != "this = self.next"
            or ast.unparse(get_methods[0].body[1]) != "self.__next()"
            or ast.unparse(get_methods[0].body[2]) != "return this"):
        return None
    return {
        "source_path": "re/_parser.py",
        "source_sha256": RE_PARSER_SOURCE_SHA256,
        "_parse_alias_assignment": "sourceget = source.get",
        "tokenizer_get_returns_current_then_advances": True,
        "sourceget_call_sites_in_pinned_parse_function": len(calls),
        "alias_call_execution_observed": False,
        "pattern_parse_observed": False,
        "evidence_scope": "PINNED_RE_PARSER_SOURCEGET_ALIAS_CANDIDATE",
    }


def _target_re_parser_sub_dispatch_candidate(files):
    """Bind the _parse_sub-to-_parse dispatch in the pinned regex parser."""
    source = files.get("re/_parser.py") if type(files) is dict else None
    if (type(source) is not bytes
            or hashlib.sha256(source).hexdigest() != RE_PARSER_SOURCE_SHA256):
        return None
    try:
        tree = ast.parse(source.decode("utf-8"), filename="re/_parser.py")
    except (UnicodeError, SyntaxError):
        return None
    functions = [node for node in tree.body
                 if isinstance(node, ast.FunctionDef)
                 and node.name in {"_parse_sub", "_parse"}]
    parse_sub = [node for node in functions if node.name == "_parse_sub"]
    parse = [node for node in functions if node.name == "_parse"]
    if (len(functions) != 2 or len(parse_sub) != 1 or len(parse) != 1
            or [arg.arg for arg in parse_sub[0].args.args]
            != ["source", "state", "verbose", "nested"]
            or [arg.arg for arg in parse[0].args.args]
            != ["source", "state", "verbose", "nested", "first"]):
        return None
    calls = [node for node in ast.walk(parse_sub[0])
             if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
             and node.func.id == "_parse"]
    if (len(calls) != 1
            or [ast.unparse(arg) for arg in calls[0].args]
            != ["source", "state", "verbose", "nested + 1",
                "not nested and (not items)"]):
        return None
    parents = [node for node in ast.walk(parse_sub[0])
               if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
               and node.func.id == "itemsappend" and calls[0] in node.args]
    if len(parents) != 1:
        return None
    return {
        "source_path": "re/_parser.py",
        "source_sha256": RE_PARSER_SOURCE_SHA256,
        "dispatch_function": "_parse_sub",
        "target_function": "_parse",
        "dispatch_arguments": [
            "source", "state", "verbose", "nested + 1",
            "not nested and (not items)",
        ],
        "dispatch_is_wrapped_by": "itemsappend",
        "dispatch_call_sites": 1,
        "parser_execution_observed": False,
        "evidence_scope": "PINNED_RE_PARSER_SUB_DISPATCH_CANDIDATE",
    }


def _target_re_parser_alternation_candidate(files):
    """Bind alternative termination and root VERBOSE propagation statically."""
    source = files.get("re/_parser.py") if type(files) is dict else None
    if (type(source) is not bytes
            or hashlib.sha256(source).hexdigest() != RE_PARSER_SOURCE_SHA256):
        return None
    try:
        tree = ast.parse(source.decode("utf-8"), filename="re/_parser.py")
    except (UnicodeError, SyntaxError):
        return None
    functions = [node for node in tree.body
                 if isinstance(node, ast.FunctionDef)
                 and node.name == "_parse_sub"]
    if len(functions) != 1:
        return None
    parse_sub = functions[0]
    aliases = [node for node in ast.walk(parse_sub)
               if isinstance(node, ast.Assign)
               and any(isinstance(target, ast.Name)
                       and target.id == "sourcematch" for target in node.targets)]
    loops = [node for node in parse_sub.body if isinstance(node, ast.While)]
    if (len(aliases) != 1 or ast.unparse(aliases[0]) != "sourcematch = source.match"
            or not loops or len(loops[0].body) != 3
            or ast.unparse(loops[0].test) != "True"
            or not isinstance(loops[0].body[1], ast.If)
            or ast.unparse(loops[0].body[1])
            != "if not sourcematch('|'):\n    break"
            or not isinstance(loops[0].body[2], ast.If)
            or ast.unparse(loops[0].body[2])
            != "if not nested:\n    verbose = state.flags & SRE_FLAG_VERBOSE"):
        return None
    singleton_branches = [node for node in ast.walk(parse_sub)
                          if isinstance(node, ast.If)
                          and ast.unparse(node.test) == "len(items) == 1"]
    if (len(singleton_branches) != 1
            or len(singleton_branches[0].body) != 1
            or ast.unparse(singleton_branches[0].body[0]) != "return items[0]"):
        return None
    return {
        "source_path": "re/_parser.py",
        "source_sha256": RE_PARSER_SOURCE_SHA256,
        "alternation_match_alias": "sourcematch = source.match",
        "loop_continues_while_alternation_matches": "|",
        "root_group_verbose_refresh": "state.flags & SRE_FLAG_VERBOSE",
        "single_alternative_return": "items[0]",
        "parser_execution_observed": False,
        "evidence_scope": "PINNED_RE_PARSER_ALTERNATION_CANDIDATE",
    }


def _target_re_parser_multi_alternative_return_candidate(files):
    """Bind the static IN optimization and general BRANCH return shapes."""
    source = files.get("re/_parser.py") if type(files) is dict else None
    if (type(source) is not bytes
            or hashlib.sha256(source).hexdigest() != RE_PARSER_SOURCE_SHA256):
        return None
    try:
        tree = ast.parse(source.decode("utf-8"), filename="re/_parser.py")
    except (UnicodeError, SyntaxError):
        return None
    parsers = [node for node in tree.body
               if isinstance(node, ast.FunctionDef) and node.name == "_parse_sub"]
    if len(parsers) != 1:
        return None
    parse_sub = parsers[0]
    singleton = [node for node in ast.walk(parse_sub)
                 if isinstance(node, ast.If)
                 and ast.unparse(node.test) == "len(items) == 1"]
    subpattern_bindings = [node for node in ast.walk(parse_sub)
                           if isinstance(node, ast.Assign)
                           and any(isinstance(target, ast.Name)
                                   and target.id == "subpattern"
                                   for target in node.targets)]
    appends = [node for node in ast.walk(parse_sub)
               if isinstance(node, ast.Call)
               and ast.unparse(node.func) == "subpattern.append"]
    append_shapes = {ast.unparse(node) for node in appends}
    if (len(singleton) != 1 or len(singleton[0].body) != 1
            or ast.unparse(singleton[0].body[0]) != "return items[0]"
            or len(subpattern_bindings) != 1
            or ast.unparse(subpattern_bindings[0]) != "subpattern = SubPattern(state)"
            or append_shapes != {
                "subpattern.append(prefix)",
                "subpattern.append((IN, _uniq(set)))",
                "subpattern.append((BRANCH, (None, items)))",
            }):
        return None
    returns = [node for node in ast.walk(parse_sub)
               if isinstance(node, ast.Return)
               and ast.unparse(node.value) == "subpattern"]
    if len(returns) != 2:
        return None
    return {
        "source_path": "re/_parser.py",
        "source_sha256": RE_PARSER_SOURCE_SHA256,
        "single_alternative_result": "items[0]",
        "multiple_alternatives_container": "SubPattern(state)",
        "common_prefix_append": "subpattern.append(prefix)",
        "character_set_optimization_append": "subpattern.append((IN, _uniq(set)))",
        "general_branch_append": "subpattern.append((BRANCH, (None, items)))",
        "subpattern_return_sites": len(returns),
        "parser_execution_observed": False,
        "evidence_scope": "PINNED_RE_PARSER_MULTI_ALTERNATIVE_RETURN_CANDIDATE",
    }


def _target_re_parser_charset_shortcut_candidate(files):
    """Bind the syntactic guards for the parser's character-set shortcut."""
    source = files.get("re/_parser.py") if type(files) is dict else None
    if (type(source) is not bytes
            or hashlib.sha256(source).hexdigest() != RE_PARSER_SOURCE_SHA256):
        return None
    try:
        tree = ast.parse(source.decode("utf-8"), filename="re/_parser.py")
    except (UnicodeError, SyntaxError):
        return None
    parsers = [node for node in tree.body
               if isinstance(node, ast.FunctionDef) and node.name == "_parse_sub"]
    if len(parsers) != 1:
        return None
    loops = [node for node in ast.walk(parsers[0])
             if isinstance(node, ast.For)
             and isinstance(node.target, ast.Name) and node.target.id == "item"
             and isinstance(node.iter, ast.Name) and node.iter.id == "items"
             and node.orelse and node.body and isinstance(node.body[0], ast.If)
             and ast.unparse(node.body[0].test) == "len(item) != 1"]
    if len(loops) != 1:
        return None
    loop = loops[0]
    expected_kind_dispatch = (
        "if op is LITERAL:\n"
        "    set.append((op, av))\n"
        "elif op is IN and av[0][0] is not NEGATE:\n"
        "    set.extend(av)\n"
        "else:\n"
        "    break"
    )
    if (len(loop.body) != 3
            or len(loop.body[0].body) != 1
            or not isinstance(loop.body[0].body[0], ast.Break)
            or ast.unparse(loop.body[1]) != "op, av = item[0]"
            or ast.unparse(loop.body[2]) != expected_kind_dispatch
            or len(loop.orelse) != 2
            or ast.unparse(loop.orelse[0])
            != "subpattern.append((IN, _uniq(set)))"
            or ast.unparse(loop.orelse[1]) != "return subpattern"):
        return None
    return {
        "source_path": "re/_parser.py",
        "source_sha256": RE_PARSER_SOURCE_SHA256,
        "each_alternative_must_have_one_item": "len(item) != 1 breaks shortcut",
        "accepted_item_kinds": ["LITERAL", "non-NEGATE IN"],
        "literal_items_added_as": "set.append((op, av))",
        "positive_character_set_items_added_as": "set.extend(av)",
        "shortcut_on_full_loop_completion": "subpattern.append((IN, _uniq(set)))",
        "parser_execution_observed": False,
        "evidence_scope": "PINNED_RE_PARSER_CHARACTER_SET_SHORTCUT_CANDIDATE",
    }


def _target_re_parser_common_prefix_candidate(files):
    """Bind common-prefix recognition and extraction in the pinned parser."""
    source = files.get("re/_parser.py") if type(files) is dict else None
    if (type(source) is not bytes
            or hashlib.sha256(source).hexdigest() != RE_PARSER_SOURCE_SHA256):
        return None
    try:
        tree = ast.parse(source.decode("utf-8"), filename="re/_parser.py")
    except (UnicodeError, SyntaxError):
        return None
    parsers = [node for node in tree.body
               if isinstance(node, ast.FunctionDef) and node.name == "_parse_sub"]
    if len(parsers) != 1:
        return None
    expected_prefix_scan = (
        "for item in items:\n"
        "    if not item:\n"
        "        break\n"
        "    if prefix is None:\n"
        "        prefix = item[0]\n"
        "    elif item[0] != prefix:\n"
        "        break\n"
        "else:\n"
        "    for item in items:\n"
        "        del item[0]\n"
        "    subpattern.append(prefix)\n"
        "    continue"
    )
    candidates = [node for node in parsers[0].body
                  if isinstance(node, ast.While)
                  and isinstance(node.test, ast.Constant)
                  and node.test.value is True
                  and len(node.body) == 3
                  and isinstance(node.body[0], ast.Assign)
                  and ast.unparse(node.body[0]) == "prefix = None"
                  and isinstance(node.body[1], ast.For)
                  and ast.unparse(node.body[1]) == expected_prefix_scan
                  and isinstance(node.body[2], ast.Break)]
    if len(candidates) != 1:
        return None
    return {
        "source_path": "re/_parser.py",
        "source_sha256": RE_PARSER_SOURCE_SHA256,
        "prefix_initial_value": None,
        "prefix_comparison": "item[0] == prefix",
        "empty_alternative_stops_prefix_scan": True,
        "mismatch_stops_prefix_scan": True,
        "common_prefix_removed_from_each_alternative": "del item[0]",
        "common_prefix_added_to_subpattern": "subpattern.append(prefix)",
        "scan_repeats_after_prefix_extraction": True,
        "parser_execution_observed": False,
        "evidence_scope": "PINNED_RE_PARSER_COMMON_PREFIX_CANDIDATE",
    }


def _target_re_parser_subpattern_branch_order_candidate(files):
    """Bind ordering of prefix, character-set, and general branch paths."""
    source = files.get("re/_parser.py") if type(files) is dict else None
    if (type(source) is not bytes
            or hashlib.sha256(source).hexdigest() != RE_PARSER_SOURCE_SHA256):
        return None
    try:
        tree = ast.parse(source.decode("utf-8"), filename="re/_parser.py")
    except (UnicodeError, SyntaxError):
        return None
    parsers = [node for node in tree.body
               if isinstance(node, ast.FunctionDef) and node.name == "_parse_sub"]
    if len(parsers) != 1:
        return None
    body = parsers[0].body
    singleton = [i for i, node in enumerate(body)
                 if isinstance(node, ast.If)
                 and ast.unparse(node.test) == "len(items) == 1"]
    prefix_candidate = _target_re_parser_common_prefix_candidate(files)
    charset_candidate = _target_re_parser_charset_shortcut_candidate(files)
    if prefix_candidate is None or charset_candidate is None or len(singleton) != 1:
        return None
    prefix_loops = [i for i, node in enumerate(body)
                    if isinstance(node, ast.While)
                    and isinstance(node.test, ast.Constant) and node.test.value is True
                    and len(node.body) == 3
                    and isinstance(node.body[0], ast.Assign)
                    and ast.unparse(node.body[0]) == "prefix = None"
                    and isinstance(node.body[1], ast.For)
                    and "subpattern.append(prefix)" in ast.unparse(node.body[1])]
    set_assignments = [i for i, node in enumerate(body)
                       if isinstance(node, ast.Assign)
                       and ast.unparse(node) == "set = []"]
    charset_loops = [i for i, node in enumerate(body)
                     if isinstance(node, ast.For)
                     and isinstance(node.target, ast.Name)
                     and node.target.id == "item"
                     and isinstance(node.iter, ast.Name)
                     and node.iter.id == "items"
                     and node.orelse and node.body
                     and isinstance(node.body[0], ast.If)
                     and ast.unparse(node.body[0].test) == "len(item) != 1"]
    branch_appends = [i for i, node in enumerate(body)
                      if isinstance(node, ast.Expr)
                      and isinstance(node.value, ast.Call)
                      and ast.unparse(node.value)
                      == "subpattern.append((BRANCH, (None, items)))"]
    final_returns = [i for i, node in enumerate(body)
                     if isinstance(node, ast.Return)
                     and ast.unparse(node.value) == "subpattern"]
    if (len(prefix_loops) != 1 or len(set_assignments) != 1
            or len(charset_loops) != 1 or len(branch_appends) != 1
            or not final_returns):
        return None
    order = [singleton[0], prefix_loops[0], set_assignments[0],
             charset_loops[0], branch_appends[0], final_returns[-1]]
    if order != sorted(order) or len(set(order)) != len(order):
        return None
    return {
        "source_path": "re/_parser.py",
        "source_sha256": RE_PARSER_SOURCE_SHA256,
        "subpattern_paths_in_source_order": [
            "single alternative returns item",
            "extract shared prefix",
            "try character-set shortcut",
            "append general BRANCH",
        ],
        "character_set_success_returns_before_general_branch": True,
        "general_branch_is_fallback_after_shortcut_loop": True,
        "parser_execution_observed": False,
        "evidence_scope": "PINNED_RE_PARSER_SUBPATTERN_PATH_ORDER_CANDIDATE",
    }


def _target_re_parser_uniq_candidate(files):
    """Bind the pinned parser's ordered deduplication helper statically."""
    source = files.get("re/_parser.py") if type(files) is dict else None
    if (type(source) is not bytes
            or hashlib.sha256(source).hexdigest() != RE_PARSER_SOURCE_SHA256):
        return None
    try:
        tree = ast.parse(source.decode("utf-8"), filename="re/_parser.py")
    except (UnicodeError, SyntaxError):
        return None
    functions = [node for node in tree.body
                 if isinstance(node, ast.FunctionDef) and node.name == "_uniq"]
    if (len(functions) != 1 or len(functions[0].args.args) != 1
            or functions[0].args.args[0].arg != "items"
            or len(functions[0].body) != 1
            or ast.unparse(functions[0].body[0])
            != "return list(dict.fromkeys(items))"):
        return None
    return {
        "source_path": "re/_parser.py",
        "source_sha256": RE_PARSER_SOURCE_SHA256,
        "function_arguments": ["items"],
        "deduplication_expression": "list(dict.fromkeys(items))",
        "preserves_first_occurrence_order_candidate": True,
        "helper_execution_observed": False,
        "evidence_scope": "PINNED_RE_PARSER_ORDERED_UNIQ_CANDIDATE",
    }


def _target_re_parser_group_state_candidate(files):
    """Bind the parser's source for group counts and named-group indexes."""
    source = files.get("re/_parser.py") if type(files) is dict else None
    if (type(source) is not bytes
            or hashlib.sha256(source).hexdigest() != RE_PARSER_SOURCE_SHA256):
        return None
    try:
        tree = ast.parse(source.decode("utf-8"), filename="re/_parser.py")
    except (UnicodeError, SyntaxError):
        return None
    states = [node for node in tree.body
              if isinstance(node, ast.ClassDef) and node.name == "State"]
    if len(states) != 1:
        return None
    methods = {node.name: node for node in states[0].body
               if isinstance(node, ast.FunctionDef)
               and node.name in {"__init__", "groups", "opengroup",
                                 "closegroup", "checkgroup"}}
    if len(methods) != 5:
        return None
    init_body = [ast.unparse(node) for node in methods["__init__"].body]
    groups = methods["groups"]
    open_group = methods["opengroup"]
    open_body = [ast.unparse(node) for node in open_group.body]
    close_body = [ast.unparse(node) for node in methods["closegroup"].body]
    check_body = [ast.unparse(node) for node in methods["checkgroup"].body]
    named_group = [node for node in open_group.body
                   if isinstance(node, ast.If)
                   and ast.unparse(node.test) == "name is not None"]
    if (init_body != ["self.flags = 0", "self.groupdict = {}",
                      "self.groupwidths = [None]",
                      "self.lookbehindgroups = None", "self.grouprefpos = {}"]
            or [ast.unparse(node) for node in groups.decorator_list]
            != ["property"]
            or ast.unparse(groups.body[0])
            != "return len(self.groupwidths)"
            or len(open_body) != 5
            or open_body[0:2] != ["gid = self.groups",
                                  "self.groupwidths.append(None)"]
            or open_body[-1] != "return gid"
            or len(named_group) != 1
            or len(named_group[0].body) != 3
            or ast.unparse(named_group[0].body[0])
            != "ogid = self.groupdict.get(name, None)"
            or not isinstance(named_group[0].body[1], ast.If)
            or ast.unparse(named_group[0].body[2])
            != "self.groupdict[name] = gid"
            or len(methods["closegroup"].args.args) != 3
            or [arg.arg for arg in methods["closegroup"].args.args]
            != ["self", "gid", "p"]
            or close_body != ["self.groupwidths[gid] = p.getwidth()"]
            or len(methods["checkgroup"].args.args) != 2
            or [arg.arg for arg in methods["checkgroup"].args.args]
            != ["self", "gid"]
            or check_body != [
                "return gid < self.groups and self.groupwidths[gid] is not None"
            ]):
        return None
    return {
        "source_path": "re/_parser.py",
        "source_sha256": RE_PARSER_SOURCE_SHA256,
        "group_zero_width_initializer": "self.groupwidths = [None]",
        "group_count_source": "len(self.groupwidths)",
        "new_group_index_source": "gid = self.groups",
        "named_group_mapping": "self.groupdict[name] = gid",
        "duplicate_name_guard": "self.groupdict.get(name, None)",
        "closed_group_width_assignment": "self.groupwidths[gid] = p.getwidth()",
        "completed_group_check":
            "gid < self.groups and self.groupwidths[gid] is not None",
        "parser_execution_observed": False,
        "evidence_scope": "PINNED_RE_PARSER_GROUP_STATE_CANDIDATE",
    }


def _target_re_parser_group_call_candidate(files):
    """Bind capture-group parser call sites to the pinned State lifecycle."""
    source = files.get("re/_parser.py") if type(files) is dict else None
    if (type(source) is not bytes
            or hashlib.sha256(source).hexdigest() != RE_PARSER_SOURCE_SHA256):
        return None
    try:
        tree = ast.parse(source.decode("utf-8"), filename="re/_parser.py")
    except (UnicodeError, SyntaxError):
        return None
    functions = {node.name: node for node in tree.body
                 if isinstance(node, ast.FunctionDef)
                 and node.name in {"_parse", "_escape"}}
    if len(functions) != 2:
        return None

    def state_calls(function, method):
        return [node for node in ast.walk(function)
                if isinstance(node, ast.Call)
                and isinstance(node.func, ast.Attribute)
                and isinstance(node.func.value, ast.Name)
                and node.func.value.id == "state"
                and node.func.attr == method]

    open_calls = state_calls(functions["_parse"], "opengroup")
    close_calls = state_calls(functions["_parse"], "closegroup")
    parse_sub_calls = [node for node in ast.walk(functions["_parse"])
                       if isinstance(node, ast.Call)
                       and isinstance(node.func, ast.Name)
                       and node.func.id == "_parse_sub"
                       and [ast.unparse(arg) for arg in node.args]
                       == ["source", "state", "sub_verbose", "nested + 1"]]
    closing_match_calls = [node for node in ast.walk(functions["_parse"])
                           if isinstance(node, ast.Call)
                           and isinstance(node.func, ast.Attribute)
                           and isinstance(node.func.value, ast.Name)
                           and node.func.value.id == "source"
                           and node.func.attr == "match"
                           and [ast.unparse(arg) for arg in node.args] == ["')'"]]
    parser_group_checks = state_calls(functions["_parse"], "checkgroup")
    escape_group_checks = state_calls(functions["_escape"], "checkgroup")
    capture_guards = [node for node in ast.walk(functions["_parse"])
                      if isinstance(node, ast.If)
                      and ast.unparse(node.test) == "capture"
                      and any(open_calls and call is open_calls[0]
                              for statement in node.body
                              for call in ast.walk(statement))
                      and [ast.unparse(statement) for statement in node.orelse]
                      == ["group = None"]]
    close_guards = [node for node in ast.walk(functions["_parse"])
                    if isinstance(node, ast.If)
                    and ast.unparse(node.test) == "group is not None"
                    and [ast.unparse(statement) for statement in node.body]
                    == ["state.closegroup(group, p)"]]
    if (len(open_calls) != 1
            or [ast.unparse(arg) for arg in open_calls[0].args] != ["name"]
            or len(close_calls) != 1
            or [ast.unparse(arg) for arg in close_calls[0].args]
            != ["group", "p"]
            or len(parse_sub_calls) != 1
            or len(closing_match_calls) < 1
            or len(parser_group_checks) != 2
            or any([ast.unparse(arg) for arg in call.args] != ["gid"]
                   for call in parser_group_checks)
            or len(escape_group_checks) != 1
            or [ast.unparse(arg) for arg in escape_group_checks[0].args]
            != ["group"]
            or len(capture_guards) != 1
            or len(close_guards) != 1):
        return None

    close_match = max(
        (call for call in closing_match_calls
         if parse_sub_calls[0].lineno < call.lineno < close_calls[0].lineno),
        key=lambda call: call.lineno,
        default=None,
    )
    if (close_match is None
            or not (open_calls[0].lineno < parse_sub_calls[0].lineno
                    < close_match.lineno < close_calls[0].lineno)):
        return None

    return {
        "source_path": "re/_parser.py",
        "source_sha256": RE_PARSER_SOURCE_SHA256,
        "capture_group_open_call": "state.opengroup(name)",
        "capture_group_body_call":
            "_parse_sub(source, state, sub_verbose, nested + 1)",
        "capture_group_close_guard": "source.match(')') succeeds",
        "capture_group_close_call": "state.closegroup(group, p)",
        "group_width_lifecycle_order": [
            "allocate group index", "parse group body", "match closing parenthesis",
            "store parsed group width",
        ],
        "parser_group_check_call": "state.checkgroup(gid)",
        "parser_group_check_call_sites": 2,
        "escape_group_check_call": "state.checkgroup(group)",
        "parser_execution_observed": False,
        "evidence_scope": "PINNED_RE_PARSER_GROUP_CALL_CANDIDATE",
    }


def _target_re_forward_group_reference_candidate(files):
    """Bind deferred numeric conditional-group reference validation."""
    source = files.get("re/_parser.py") if type(files) is dict else None
    if (type(source) is not bytes
            or hashlib.sha256(source).hexdigest() != RE_PARSER_SOURCE_SHA256):
        return None
    try:
        tree = ast.parse(source.decode("utf-8"), filename="re/_parser.py")
    except (UnicodeError, SyntaxError):
        return None
    functions = {node.name: node for node in tree.body
                 if isinstance(node, ast.FunctionDef)
                 and node.name in {"_parse", "parse"}}
    if len(functions) != 2:
        return None
    parser = functions["_parse"]
    parse_entry = functions["parse"]

    named_condition_branches = [
        node for node in ast.walk(parser)
        if isinstance(node, ast.If)
        and ast.unparse(node.test)
        == "not (condname.isdecimal() and condname.isascii())"
        and any(isinstance(call, ast.Call)
                and ast.unparse(call.func) == "state.groupdict.get"
                and [ast.unparse(arg) for arg in call.args] == ["condname"]
                for call in ast.walk(node))
    ]
    named_condition_source = (
        "if not (condname.isdecimal() and condname.isascii()):\n"
        "    source.checkgroupname(condname, 1)\n"
        "    condgroup = state.groupdict.get(condname)\n"
        "    if condgroup is None:\n"
        "        msg = 'unknown group name %r' % condname\n"
        "        raise source.error(msg, len(condname) + 1)\n"
        "else:\n"
        "    condgroup = int(condname)\n"
        "    if not condgroup:\n"
        "        raise source.error('bad group number', len(condname) + 1)\n"
        "    if condgroup >= MAXGROUPS:\n"
        "        msg = 'invalid group reference %d' % condgroup\n"
        "        raise source.error(msg, len(condname) + 1)\n"
        "    if condgroup not in state.grouprefpos:\n"
        "        state.grouprefpos[condgroup] = source.tell() - len(condname) - 1\n"
        "    if not (condname.isdecimal() and condname.isascii()):\n"
        "        import warnings\n"
        "        warnings.warn('bad character in group name %s at position %d' % (repr(condname) if source.istext else ascii(condname), source.tell() - len(condname) - 1), DeprecationWarning, stacklevel=nested + 6)"
    )

    numeric_conversions = [node for node in ast.walk(parser)
                           if isinstance(node, ast.Assign)
                           and [ast.unparse(target) for target in node.targets]
                           == ["condgroup"]
                           and ast.unparse(node.value) == "int(condname)"]
    max_group_guards = [node for node in ast.walk(parser)
                        if isinstance(node, ast.If)
                        and ast.unparse(node.test) == "condgroup >= MAXGROUPS"]
    deferred_registry = [node for node in ast.walk(parser)
                         if isinstance(node, ast.Assign)
                         and [ast.unparse(target) for target in node.targets]
                         == ["state.grouprefpos[condgroup]"]
                         and ast.unparse(node.value)
                         == "source.tell() - len(condname) - 1"]
    registry_guards = [node for node in ast.walk(parser)
                       if isinstance(node, ast.If)
                       and ast.unparse(node.test)
                       == "condgroup not in state.grouprefpos"
                       and len(node.body) == 1
                       and deferred_registry
                       and node.body[0] is deferred_registry[0]]

    final_loops = [node for node in ast.walk(parse_entry)
                   if isinstance(node, ast.For)
                   and ast.unparse(node.target) == "g"
                   and ast.unparse(node.iter) == "p.state.grouprefpos"]
    final_group_guards = [node for node in ast.walk(parse_entry)
                          if isinstance(node, ast.If)
                          and ast.unparse(node.test) == "g >= p.state.groups"]
    invalid_reference_messages = [node for node in ast.walk(parse_entry)
                                  if isinstance(node, ast.Assign)
                                  and [ast.unparse(target) for target in node.targets]
                                  == ["msg"]
                                  and ast.unparse(node.value)
                                  == "'invalid group reference %d' % g"]
    invalid_reference_raises = [node for node in ast.walk(parse_entry)
                                if isinstance(node, ast.Call)
                                and isinstance(node.func, ast.Name)
                                and node.func.id == "error"
                                and [ast.unparse(arg) for arg in node.args]
                                == ["msg", "str", "p.state.grouprefpos[g]"]]
    parse_sub_calls = [node for node in ast.walk(parse_entry)
                       if isinstance(node, ast.Call)
                       and isinstance(node.func, ast.Name)
                       and node.func.id == "_parse_sub"]
    if (len(named_condition_branches) != 1
            or ast.unparse(named_condition_branches[0])
            != named_condition_source
            or len(numeric_conversions) != 1
            or len(max_group_guards) != 1
            or len(deferred_registry) != 1
            or len(registry_guards) != 1
            or len(final_loops) != 1
            or len(final_group_guards) != 1
            or len(invalid_reference_messages) != 1
            or len(invalid_reference_raises) != 1
            or len(parse_sub_calls) != 1
            or not (parse_sub_calls[0].lineno < final_loops[0].lineno
                    < final_group_guards[0].lineno
                    < invalid_reference_raises[0].lineno)):
        return None

    return {
        "source_path": "re/_parser.py",
        "source_sha256": RE_PARSER_SOURCE_SHA256,
        "named_conditional_group_resolution": [
            "name validated by source.checkgroupname",
            "condgroup = state.groupdict.get(condname)",
            "unknown group name rejected",
        ],
        "conditional_group_number_conversion": "condgroup = int(condname)",
        "maximum_group_guard": "condgroup >= MAXGROUPS",
        "deferred_group_position_assignment":
            "state.grouprefpos[condgroup] = source.tell() - len(condname) - 1",
        "post_parse_registry_iteration": "for g in p.state.grouprefpos",
        "final_group_count_guard": "g >= p.state.groups",
        "invalid_reference_error":
            "error(msg, str, p.state.grouprefpos[g])",
        "validation_after_pattern_parse": True,
        "forward_reference_execution_observed": False,
        "evidence_scope": "PINNED_RE_PARSER_DEFERRED_GROUP_REFERENCE_CANDIDATE",
    }


def _target_re_lookbehind_group_candidate(files):
    """Bind the parser's lookbehind boundary and group-reference guards."""
    source = files.get("re/_parser.py") if type(files) is dict else None
    if (type(source) is not bytes
            or hashlib.sha256(source).hexdigest() != RE_PARSER_SOURCE_SHA256):
        return None
    try:
        tree = ast.parse(source.decode("utf-8"), filename="re/_parser.py")
    except (UnicodeError, SyntaxError):
        return None
    classes = [node for node in tree.body
               if isinstance(node, ast.ClassDef) and node.name == "State"]
    functions = {node.name: node for node in tree.body
                 if isinstance(node, ast.FunctionDef)
                 and node.name in {"_parse", "_escape"}}
    if len(classes) != 1 or len(functions) != 2:
        return None
    state_methods = [node for node in classes[0].body
                     if isinstance(node, ast.FunctionDef)
                     and node.name == "checklookbehindgroup"]
    if len(state_methods) != 1:
        return None
    method = state_methods[0]
    method_body = method.body
    if (len(method.args.args) != 3
            or [arg.arg for arg in method.args.args]
            != ["self", "gid", "source"]
            or len(method_body) != 1
            or not isinstance(method_body[0], ast.If)
            or ast.unparse(method_body[0].test)
            != "self.lookbehindgroups is not None"
            or len(method_body[0].body) != 2):
        return None
    open_group_guard, lookbehind_index_guard = method_body[0].body
    if (not isinstance(open_group_guard, ast.If)
            or ast.unparse(open_group_guard.test) != "not self.checkgroup(gid)"
            or len(open_group_guard.body) != 1
            or ast.unparse(open_group_guard.body[0])
            != "raise source.error('cannot refer to an open group')"
            or not isinstance(lookbehind_index_guard, ast.If)
            or ast.unparse(lookbehind_index_guard.test)
            != "gid >= self.lookbehindgroups"
            or len(lookbehind_index_guard.body) != 1
            or ast.unparse(lookbehind_index_guard.body[0])
            != "raise source.error('cannot refer to group defined in the same lookbehind subpattern')"):
        return None

    parser = functions["_parse"]
    initial_boundary = [node for node in ast.walk(parser)
                        if isinstance(node, ast.Assign)
                        and [ast.unparse(target) for target in node.targets]
                        == ["lookbehindgroups"]
                        and ast.unparse(node.value) == "state.lookbehindgroups"]
    boundary_guards = [node for node in ast.walk(parser)
                       if isinstance(node, ast.If)
                       and ast.unparse(node.test) == "lookbehindgroups is None"
                       and any(ast.unparse(statement)
                               == "state.lookbehindgroups = state.groups"
                               for statement in node.body)]
    negative_direction_guards = [node for node in ast.walk(parser)
                                 if isinstance(node, ast.If)
                                 and ast.unparse(node.test) == "dir < 0"]
    if len(negative_direction_guards) != 1:
        return None
    reset_guards = [node for node in ast.walk(negative_direction_guards[0])
                    if isinstance(node, ast.If)
                    and ast.unparse(node.test) == "lookbehindgroups is None"
                    and any(ast.unparse(statement)
                            == "state.lookbehindgroups = None"
                            for statement in node.body)]

    def lookbehind_calls(function):
        return [node for node in ast.walk(function)
                if isinstance(node, ast.Call)
                and isinstance(node.func, ast.Attribute)
                and isinstance(node.func.value, ast.Name)
                and node.func.value.id == "state"
                and node.func.attr == "checklookbehindgroup"]

    parser_calls = lookbehind_calls(parser)
    escape_calls = lookbehind_calls(functions["_escape"])
    if (len(initial_boundary) != 1
            or len(boundary_guards) != 1
            or len(reset_guards) != 1
            or len(parser_calls) != 3
            or sorted(tuple(ast.unparse(arg) for arg in call.args)
                      for call in parser_calls)
            != [("condgroup", "source"), ("gid", "source"),
                ("gid", "source")]
            or len(escape_calls) != 1
            or [ast.unparse(arg) for arg in escape_calls[0].args]
            != ["group", "source"]):
        return None

    return {
        "source_path": "re/_parser.py",
        "source_sha256": RE_PARSER_SOURCE_SHA256,
        "lookbehind_boundary_source": "state.lookbehindgroups = state.groups",
        "lookbehind_boundary_reset":
            "state.lookbehindgroups = None when no prior boundary existed",
        "open_group_guard": "not self.checkgroup(gid)",
        "same_lookbehind_group_guard": "gid >= self.lookbehindgroups",
        "parser_reference_calls": [
            "state.checklookbehindgroup(gid, source)",
            "state.checklookbehindgroup(gid, source)",
            "state.checklookbehindgroup(condgroup, source)",
        ],
        "escape_reference_call": "state.checklookbehindgroup(group, source)",
        "lookbehind_execution_observed": False,
        "evidence_scope": "PINNED_RE_PARSER_LOOKBEHIND_GROUP_CANDIDATE",
    }


def _target_re_group_reference_width_candidate(files):
    """Bind width propagation for group references and conditional branches."""
    source = files.get("re/_parser.py") if type(files) is dict else None
    if (type(source) is not bytes
            or hashlib.sha256(source).hexdigest() != RE_PARSER_SOURCE_SHA256):
        return None
    try:
        tree = ast.parse(source.decode("utf-8"), filename="re/_parser.py")
    except (UnicodeError, SyntaxError):
        return None
    subpatterns = [node for node in tree.body
                   if isinstance(node, ast.ClassDef)
                   and node.name == "SubPattern"]
    if len(subpatterns) != 1:
        return None
    methods = [node for node in subpatterns[0].body
               if isinstance(node, ast.FunctionDef) and node.name == "getwidth"]
    if len(methods) != 1:
        return None
    group_refs = [node for node in ast.walk(methods[0])
                  if isinstance(node, ast.If)
                  and ast.unparse(node.test) == "op is GROUPREF"]
    conditional_refs = [node for node in ast.walk(methods[0])
                        if isinstance(node, ast.If)
                        and ast.unparse(node.test) == "op is GROUPREF_EXISTS"]
    if (len(group_refs) != 1 or len(group_refs[0].body) != 3
            or [ast.unparse(node) for node in group_refs[0].body]
            != ["i, j = self.state.groupwidths[av]", "lo = lo + i",
                "hi = hi + j"]
            or len(conditional_refs) != 1
            or len(conditional_refs[0].body) != 4):
        return None
    conditional_body = conditional_refs[0].body
    if ([ast.unparse(node) for node in conditional_body[0:1]]
            != ["i, j = av[1].getwidth()"]
            or not isinstance(conditional_body[1], ast.If)
            or ast.unparse(conditional_body[1].test) != "av[2] is not None"
            or [ast.unparse(node) for node in conditional_body[1].body]
            != ["l, h = av[2].getwidth()", "i = min(i, l)",
                "j = max(j, h)"]
            or [ast.unparse(node) for node in conditional_body[1].orelse]
            != ["i = 0"]
            or [ast.unparse(node) for node in conditional_body[2:]]
            != ["lo = lo + i", "hi = hi + j"]):
        return None
    return {
        "source_path": "re/_parser.py",
        "source_sha256": RE_PARSER_SOURCE_SHA256,
        "group_reference_width_source": "self.state.groupwidths[av]",
        "group_reference_minimum_update": "lo = lo + i",
        "group_reference_maximum_update": "hi = hi + j",
        "conditional_yes_width": "av[1].getwidth()",
        "conditional_no_width": "av[2].getwidth()",
        "conditional_minimum": "min(i, l)",
        "conditional_maximum": "max(j, h)",
        "conditional_without_else_minimum": "i = 0",
        "width_execution_observed": False,
        "evidence_scope": "PINNED_RE_PARSER_GROUP_REFERENCE_WIDTH_CANDIDATE",
    }


def _target_re_group_reference_compiler_candidate(files):
    """Bind parser group-reference forms to compiler lowering paths."""
    parser_source = files.get("re/_parser.py") if type(files) is dict else None
    compiler_source = files.get("re/_compiler.py") if type(files) is dict else None
    if (type(parser_source) is not bytes
            or hashlib.sha256(parser_source).hexdigest()
            != RE_PARSER_SOURCE_SHA256
            or type(compiler_source) is not bytes
            or hashlib.sha256(compiler_source).hexdigest()
            != RE_COMPILER_SOURCE_SHA256):
        return None
    try:
        parser_tree = ast.parse(parser_source.decode("utf-8"),
                                filename="re/_parser.py")
        compiler_tree = ast.parse(compiler_source.decode("utf-8"),
                                  filename="re/_compiler.py")
    except (UnicodeError, SyntaxError):
        return None
    parser_functions = {node.name: node for node in parser_tree.body
                        if isinstance(node, ast.FunctionDef)
                        and node.name in {"_parse", "_escape"}}
    compiler_functions = [node for node in compiler_tree.body
                          if isinstance(node, ast.FunctionDef)
                          and node.name == "_compile"]
    if len(parser_functions) != 2 or len(compiler_functions) != 1:
        return None

    escape_returns = [node for node in ast.walk(parser_functions["_escape"])
                      if isinstance(node, ast.Return)
                      and ast.unparse(node.value) == "(GROUPREF, group)"]
    numeric_escape_branches = [
        node for node in ast.walk(parser_functions["_escape"])
        if isinstance(node, ast.If)
        and ast.unparse(node.test) == "c == '0'"
    ]
    named_reference_branches = [
        node for node in ast.walk(parser_functions["_parse"])
        if isinstance(node, ast.If)
        and ast.unparse(node.test) == "sourcematch('=')"
    ]
    parser_calls = [node for node in ast.walk(parser_functions["_parse"])
                    if isinstance(node, ast.Call)
                    and isinstance(node.func, ast.Name)
                    and node.func.id == "subpatternappend"]
    groupref_outputs = [node for node in parser_calls
                       if ast.unparse(node.args[0]) == "(GROUPREF, gid)"]
    conditional_outputs = [node for node in parser_calls
                           if ast.unparse(node.args[0])
                           == "(GROUPREF_EXISTS, (condgroup, item_yes, item_no))"]

    compile_function = compiler_functions[0]
    groupref_branches = [node for node in ast.walk(compile_function)
                         if isinstance(node, ast.If)
                         and ast.unparse(node.test) == "op is GROUPREF"]
    conditional_branches = [node for node in ast.walk(compile_function)
                            if isinstance(node, ast.If)
                            and ast.unparse(node.test) == "op is GROUPREF_EXISTS"]
    numeric_escape_source = (
        "if c == '0':\n"
        "    escape += source.getwhile(2, OCTDIGITS)\n"
        "    return (LITERAL, int(escape[1:], 8))\n"
        "elif c in DIGITS:\n"
        "    if source.next in DIGITS:\n"
        "        escape += source.get()\n"
        "        if escape[1] in OCTDIGITS and escape[2] in OCTDIGITS and (source.next in OCTDIGITS):\n"
        "            escape += source.get()\n"
        "            c = int(escape[1:], 8)\n"
        "            if c > 255:\n"
        "                raise source.error('octal escape value %s outside of range 0-0o377' % escape, len(escape))\n"
        "            return (LITERAL, c)\n"
        "    group = int(escape[1:])\n"
        "    if group < state.groups:\n"
        "        if not state.checkgroup(group):\n"
        "            raise source.error('cannot refer to an open group', len(escape))\n"
        "        state.checklookbehindgroup(group, source)\n"
        "        return (GROUPREF, group)\n"
        "    raise source.error('invalid group reference %d' % group, len(escape) - 1)"
    )
    named_reference_source = (
        "if sourcematch('='):\n"
        "    name = source.getuntil(')', 'group name')\n"
        "    source.checkgroupname(name, 1)\n"
        "    gid = state.groupdict.get(name)\n"
        "    if gid is None:\n"
        "        msg = 'unknown group name %r' % name\n"
        "        raise source.error(msg, len(name) + 1)\n"
        "    if not state.checkgroup(gid):\n"
        "        raise source.error('cannot refer to an open group', len(name) + 1)\n"
        "    state.checklookbehindgroup(gid, source)\n"
        "    subpatternappend((GROUPREF, gid))\n"
        "    continue\n"
        "else:\n"
        "    char = sourceget()\n"
        "    if char is None:\n"
        "        raise source.error('unexpected end of pattern')\n"
        "    raise source.error('unknown extension ?P' + char, len(char) + 2)"
    )
    if (len(escape_returns) != 1
            or len(numeric_escape_branches) != 1
            or ast.unparse(numeric_escape_branches[0]) != numeric_escape_source
            or len(named_reference_branches) != 1
            or ast.unparse(named_reference_branches[0]) != named_reference_source
            or len(groupref_outputs) != 1
            or len(conditional_outputs) != 1
            or len(groupref_branches) != 1
            or len(conditional_branches) != 1
            or len(groupref_branches[0].body) != 2
            or not isinstance(groupref_branches[0].body[0], ast.If)
            or ast.unparse(groupref_branches[0].body[0])
            != "if not flags & SRE_FLAG_IGNORECASE:\n    emit(op)\nelif flags & SRE_FLAG_LOCALE:\n    emit(GROUPREF_LOC_IGNORE)\nelif not fixes:\n    emit(GROUPREF_IGNORE)\nelse:\n    emit(GROUPREF_UNI_IGNORE)"
            or ast.unparse(groupref_branches[0].body[1]) != "emit(av - 1)"):
        return None

    conditional_body = conditional_branches[0].body
    if (len(conditional_body) != 6
            or [ast.unparse(node) for node in conditional_body[:3]]
            != ["emit(op)", "emit(av[0] - 1)", "skipyes = _len(code)"]
            or ast.unparse(conditional_body[3]) != "emit(0)"
            or ast.unparse(conditional_body[4]) != "_compile(code, av[1], flags)"
            or not isinstance(conditional_body[5], ast.If)
            or ast.unparse(conditional_body[5].test) != "av[2]"
            or [ast.unparse(node) for node in conditional_body[5].body]
            != ["emit(JUMP)", "skipno = _len(code)", "emit(0)",
                "code[skipyes] = _len(code) - skipyes + 1",
                "_compile(code, av[2], flags)",
                "code[skipno] = _len(code) - skipno"]
            or [ast.unparse(node) for node in conditional_body[5].orelse]
            != ["code[skipyes] = _len(code) - skipyes + 1"]
            or not groupref_branches[0].lineno
            < conditional_branches[0].lineno):
        return None

    return {
        "parser_source_sha256": RE_PARSER_SOURCE_SHA256,
        "compiler_source_sha256": RE_COMPILER_SOURCE_SHA256,
        "numeric_reference_parser_output": "(GROUPREF, group)",
        "numeric_escape_classification": [
            "leading-zero octal consumes up to two following octal digits",
            "exactly three octal digits are an octal literal",
            "octal literal value must be at most 0o377",
            "remaining digit escape prefix is parsed as a decimal group reference",
        ],
        "numeric_escape_group_guards": [
            "group < state.groups",
            "state.checkgroup(group)",
            "state.checklookbehindgroup(group, source)",
        ],
        "named_reference_resolution": [
            "state.groupdict.get(name)",
            "unknown group name rejected",
            "state.checkgroup(gid)",
            "state.checklookbehindgroup(gid, source)",
            "subpatternappend((GROUPREF, gid))",
        ],
        "named_reference_parser_output": "(GROUPREF, gid)",
        "conditional_reference_parser_output":
            "(GROUPREF_EXISTS, (condgroup, item_yes, item_no))",
        "group_reference_ignore_case_lowering": [
            "GROUPREF", "GROUPREF_LOC_IGNORE", "GROUPREF_IGNORE",
            "GROUPREF_UNI_IGNORE",
        ],
        "compiled_group_reference_index": "emit(av - 1)",
        "conditional_group_index": "emit(av[0] - 1)",
        "conditional_yes_branch": "_compile(code, av[1], flags)",
        "conditional_no_branch": "_compile(code, av[2], flags) when av[2]",
        "conditional_jump_offsets_patched": True,
        "parser_or_compiler_execution_observed": False,
        "evidence_scope": "PINNED_RE_GROUP_REFERENCE_COMPILER_CANDIDATE",
    }


def _target_re_compiler_branch_candidate(files):
    """Bind how the pinned compiler lowers a general BRANCH subpattern."""
    source = files.get("re/_compiler.py") if type(files) is dict else None
    if (type(source) is not bytes
            or hashlib.sha256(source).hexdigest() != RE_COMPILER_SOURCE_SHA256):
        return None
    try:
        tree = ast.parse(source.decode("utf-8"), filename="re/_compiler.py")
    except (UnicodeError, SyntaxError):
        return None
    functions = [node for node in tree.body
                 if isinstance(node, ast.FunctionDef) and node.name == "_compile"]
    if len(functions) != 1:
        return None
    branches = [node for node in ast.walk(functions[0])
                if isinstance(node, ast.If)
                and ast.unparse(node.test) == "op is BRANCH"]
    if len(branches) != 1:
        return None
    body = branches[0].body
    if (len(body) != 6 or ast.unparse(body[0]) != "emit(op)"
            or ast.unparse(body[1]) != "tail = []"
            or ast.unparse(body[2]) != "tailappend = tail.append"
            or not isinstance(body[3], ast.For)
            or ast.unparse(body[3].target) != "av"
            or ast.unparse(body[3].iter) != "av[1]"
            or [ast.unparse(node) for node in body[3].body] != [
                "skip = _len(code)", "emit(0)", "_compile(code, av, flags)",
                "emit(JUMP)", "tailappend(_len(code))", "emit(0)",
                "code[skip] = _len(code) - skip",
            ]
            or ast.unparse(body[4]) != "emit(FAILURE)"
            or not isinstance(body[5], ast.For)
            or ast.unparse(body[5].target) != "tail"
            or ast.unparse(body[5].iter) != "tail"
            or len(body[5].body) != 1
            or ast.unparse(body[5].body[0])
            != "code[tail] = _len(code) - tail"):
        return None
    return {
        "source_path": "re/_compiler.py",
        "source_sha256": RE_COMPILER_SOURCE_SHA256,
        "compiler_branch_operator": "BRANCH",
        "alternative_container_expression": "av[1]",
        "alternative_compile_call": "_compile(code, av, flags)",
        "branch_end_marker": "FAILURE",
        "branch_join_operator": "JUMP",
        "tail_offsets_patched_after_alternatives": True,
        "compiler_execution_observed": False,
        "evidence_scope": "PINNED_RE_COMPILER_BRANCH_LOWERING_CANDIDATE",
    }


def _target_re_compiler_code_container_candidate(files):
    """Bind parsed SubPattern input through the compiler's list code container."""
    source = files.get("re/_compiler.py") if type(files) is dict else None
    if (type(source) is not bytes
            or hashlib.sha256(source).hexdigest() != RE_COMPILER_SOURCE_SHA256):
        return None
    try:
        tree = ast.parse(source.decode("utf-8"), filename="re/_compiler.py")
    except (UnicodeError, SyntaxError):
        return None
    functions = {node.name: node for node in tree.body
                 if isinstance(node, ast.FunctionDef)
                 and node.name in {"_code", "compile"}}
    if len(functions) != 2:
        return None
    code_body = functions["_code"].body
    if [ast.unparse(node) for node in code_body] != [
            "flags = p.state.flags | flags", "code = []",
            "_compile_info(code, p, flags)", "_compile(code, p.data, flags)",
            "code.append(SUCCESS)", "return code"]:
        return None
    code_bindings = [node for node in ast.walk(functions["compile"])
                     if isinstance(node, ast.Assign)
                     and any(isinstance(target, ast.Name) and target.id == "code"
                             for target in node.targets)
                     and ast.unparse(node) == "code = _code(p, flags)"]
    sre_calls = [node for node in ast.walk(functions["compile"])
                 if isinstance(node, ast.Call)
                 and ast.unparse(node.func) == "_sre.compile"]
    if (len(code_bindings) != 1 or len(sre_calls) != 1
            or [ast.unparse(arg) for arg in sre_calls[0].args]
            != ["pattern", "flags | p.state.flags", "code",
                "p.state.groups - 1", "groupindex", "tuple(indexgroup)"]):
        return None
    return {
        "source_path": "re/_compiler.py",
        "source_sha256": RE_COMPILER_SOURCE_SHA256,
        "code_container_initializer": "code = []",
        "parsed_pattern_input": "p.data",
        "compiled_success_terminator": "code.append(SUCCESS)",
        "code_returned_to_compile": "code = _code(p, flags)",
        "code_passed_to_sre_compile": True,
        "compiler_execution_observed": False,
        "evidence_scope": "PINNED_RE_COMPILER_CODE_CONTAINER_CANDIDATE",
    }


def _target_re_compiler_group_metadata_candidate(files):
    """Bind group count and named-group metadata passed to _sre.compile."""
    source = files.get("re/_compiler.py") if type(files) is dict else None
    if (type(source) is not bytes
            or hashlib.sha256(source).hexdigest() != RE_COMPILER_SOURCE_SHA256):
        return None
    try:
        tree = ast.parse(source.decode("utf-8"), filename="re/_compiler.py")
    except (UnicodeError, SyntaxError):
        return None
    functions = [node for node in tree.body
                 if isinstance(node, ast.FunctionDef) and node.name == "compile"]
    if len(functions) != 1:
        return None
    body = functions[0].body
    assignments = [ast.unparse(node) for node in body if isinstance(node, ast.Assign)]
    group_mapping = [node for node in body if isinstance(node, ast.For)
                     and ast.unparse(node.target) == "(k, i)"
                     and ast.unparse(node.iter) == "groupindex.items()"]
    calls = [node for node in ast.walk(functions[0])
             if isinstance(node, ast.Call)
             and ast.unparse(node.func) == "_sre.compile"]
    if ("groupindex = p.state.groupdict" not in assignments
            or "indexgroup = [None] * p.state.groups" not in assignments
            or len(group_mapping) != 1
            or len(group_mapping[0].body) != 1
            or ast.unparse(group_mapping[0].body[0]) != "indexgroup[i] = k"
            or len(calls) != 1
            or [ast.unparse(arg) for arg in calls[0].args]
            != ["pattern", "flags | p.state.flags", "code",
                "p.state.groups - 1", "groupindex", "tuple(indexgroup)"]):
        return None
    return {
        "source_path": "re/_compiler.py",
        "source_sha256": RE_COMPILER_SOURCE_SHA256,
        "groupindex_source": "p.state.groupdict",
        "indexgroup_length": "p.state.groups",
        "indexgroup_population": "indexgroup[i] = k",
        "compiled_group_count": "p.state.groups - 1",
        "compile_flags_expression": "flags | p.state.flags",
        "metadata_passed_to_sre_compile": [
            "groupindex", "tuple(indexgroup)",
        ],
        "compiler_execution_observed": False,
        "evidence_scope": "PINNED_RE_COMPILER_GROUP_METADATA_CANDIDATE",
    }


def _target_re_compiler_debug_disassembly_candidate(files):
    """Bind the optional debug disassembly branch before native compilation."""
    source = files.get("re/_compiler.py") if type(files) is dict else None
    if (type(source) is not bytes
            or hashlib.sha256(source).hexdigest() != RE_COMPILER_SOURCE_SHA256):
        return None
    try:
        tree = ast.parse(source.decode("utf-8"), filename="re/_compiler.py")
    except (UnicodeError, SyntaxError):
        return None
    functions = [node for node in tree.body
                 if isinstance(node, ast.FunctionDef) and node.name == "compile"]
    if len(functions) != 1:
        return None
    body = functions[0].body
    debug_paths = [node for node in body if isinstance(node, ast.If)
                   and ast.unparse(node.test) == "flags & SRE_FLAG_DEBUG"]
    code_assignments = [index for index, node in enumerate(body)
                        if isinstance(node, ast.Assign)
                        and ast.unparse(node) == "code = _code(p, flags)"]
    metadata_assignments = [index for index, node in enumerate(body)
                            if isinstance(node, ast.Assign)
                            and ast.unparse(node)
                            == "groupindex = p.state.groupdict"]
    sre_returns = [index for index, node in enumerate(body)
                   if isinstance(node, ast.Return)
                   and any(isinstance(child, ast.Call)
                           and ast.unparse(child.func) == "_sre.compile"
                           for child in ast.walk(node))]
    if (len(debug_paths) != 1 or len(code_assignments) != 1
            or len(metadata_assignments) != 1 or len(sre_returns) != 1
            or [ast.unparse(node) for node in debug_paths[0].body]
            != ["print()", "dis(code)"]
            or not code_assignments[0] < body.index(debug_paths[0])
            or not body.index(debug_paths[0]) < metadata_assignments[0]
            or body.index(debug_paths[0]) >= sre_returns[0]):
        return None
    return {
        "source_path": "re/_compiler.py",
        "source_sha256": RE_COMPILER_SOURCE_SHA256,
        "debug_flag_condition": "flags & SRE_FLAG_DEBUG",
        "disassembled_value": "code",
        "order": "after_code_generation_before_group_metadata_and_native_compile",
        "compiler_execution_observed": False,
        "evidence_scope": "PINNED_RE_COMPILER_DEBUG_DISASSEMBLY_CANDIDATE",
    }


def _target_re_compiler_parsed_pattern_input_candidate(files):
    """Bind string parsing versus an already parsed SubPattern input."""
    source = files.get("re/_compiler.py") if type(files) is dict else None
    if (type(source) is not bytes
            or hashlib.sha256(source).hexdigest() != RE_COMPILER_SOURCE_SHA256):
        return None
    try:
        tree = ast.parse(source.decode("utf-8"), filename="re/_compiler.py")
    except (UnicodeError, SyntaxError):
        return None
    functions = [node for node in tree.body
                 if isinstance(node, ast.FunctionDef) and node.name == "compile"]
    if len(functions) != 1:
        return None
    body = functions[0].body
    branches = [node for node in body if isinstance(node, ast.If)
                and ast.unparse(node.test) == "isstring(p)"]
    code_assignments = [index for index, node in enumerate(body)
                        if isinstance(node, ast.Assign)
                        and ast.unparse(node) == "code = _code(p, flags)"]
    if (len(branches) != 1 or len(branches[0].orelse) != 1
            or [ast.unparse(node) for node in branches[0].body]
            != ["pattern = p", "p = _parser.parse(p, flags)"]
            or ast.unparse(branches[0].orelse[0]) != "pattern = None"
            or len(code_assignments) != 1
            or body.index(branches[0]) >= code_assignments[0]):
        return None
    return {
        "source_path": "re/_compiler.py",
        "source_sha256": RE_COMPILER_SOURCE_SHA256,
        "string_input_branch": "pattern = p; p = _parser.parse(p, flags)",
        "preparsed_input_branch": "pattern = None",
        "code_generation_after_input_selection": "code = _code(p, flags)",
        "compiler_execution_observed": False,
        "evidence_scope": "PINNED_RE_COMPILER_PARSED_PATTERN_INPUT_CANDIDATE",
    }


def _target_re_compile_tokenizer_input_type_candidates(files, modules):
    """Bind literal compile-input types to the pinned parser entry path."""
    if type(files) is not dict or type(modules) is not tuple:
        return []
    source_specs = (
        ("re/__init__.py", RE_INIT_SOURCE_SHA256),
        ("re/_compiler.py", RE_COMPILER_SOURCE_SHA256),
        ("re/_parser.py", RE_PARSER_SOURCE_SHA256),
    )
    source_trees = {}
    for path, digest in source_specs:
        source = files.get(path)
        if (type(source) is not bytes or hashlib.sha256(source).hexdigest() != digest):
            return []
        try:
            source_trees[path] = ast.parse(source.decode("utf-8"), filename=path)
        except (UnicodeError, SyntaxError):
            return []
    constants_source = files.get("re/_constants.py")
    if (type(constants_source) is not bytes
            or hashlib.sha256(constants_source).hexdigest()
            != RE_CONSTANTS_SOURCE_SHA256):
        return []
    cache_path_candidate = _target_re_compile_cache_path_candidate(files)
    tokenizer_access_candidate = _target_re_tokenizer_access_candidate(files)
    parser_sourceget_candidate = _target_re_parser_sourceget_candidate(files)
    parser_sub_dispatch_candidate = _target_re_parser_sub_dispatch_candidate(files)
    parser_alternation_candidate = _target_re_parser_alternation_candidate(files)
    parser_multi_alternative_candidate = (
        _target_re_parser_multi_alternative_return_candidate(files)
    )
    parser_charset_candidate = _target_re_parser_charset_shortcut_candidate(files)
    parser_prefix_candidate = _target_re_parser_common_prefix_candidate(files)
    parser_subpattern_order_candidate = (
        _target_re_parser_subpattern_branch_order_candidate(files)
    )
    parser_uniq_candidate = _target_re_parser_uniq_candidate(files)
    parser_group_state_candidate = _target_re_parser_group_state_candidate(files)
    parser_group_call_candidate = _target_re_parser_group_call_candidate(files)
    parser_forward_group_candidate = (
        _target_re_forward_group_reference_candidate(files)
    )
    parser_lookbehind_candidate = _target_re_lookbehind_group_candidate(files)
    parser_group_width_candidate = (
        _target_re_group_reference_width_candidate(files)
    )
    parser_group_compiler_candidate = (
        _target_re_group_reference_compiler_candidate(files)
    )
    compiler_branch_candidate = _target_re_compiler_branch_candidate(files)
    compiler_code_candidate = _target_re_compiler_code_container_candidate(files)
    compiler_group_candidate = _target_re_compiler_group_metadata_candidate(files)
    compiler_debug_candidate = (
        _target_re_compiler_debug_disassembly_candidate(files)
    )
    compiler_input_candidate = (
        _target_re_compiler_parsed_pattern_input_candidate(files)
    )
    if (cache_path_candidate is None or tokenizer_access_candidate is None
            or parser_sourceget_candidate is None
            or parser_sub_dispatch_candidate is None
            or parser_alternation_candidate is None
            or parser_multi_alternative_candidate is None
            or parser_charset_candidate is None
            or parser_prefix_candidate is None
            or parser_subpattern_order_candidate is None
            or parser_uniq_candidate is None
            or parser_group_state_candidate is None
            or parser_group_call_candidate is None
            or parser_forward_group_candidate is None
            or parser_lookbehind_candidate is None
            or parser_group_width_candidate is None
            or parser_group_compiler_candidate is None
            or compiler_branch_candidate is None
            or compiler_code_candidate is None
            or compiler_group_candidate is None
            or compiler_debug_candidate is None
            or compiler_input_candidate is None):
        return []
    try:
        constants_tree = ast.parse(constants_source.decode("utf-8"),
                                   filename="re/_constants.py")
    except (UnicodeError, SyntaxError):
        return []

    def functions(tree, name):
        return [node for node in tree.body
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
                and node.name == name]

    re_tree = source_trees["re/__init__.py"]
    compiler_tree = source_trees["re/_compiler.py"]
    parser_tree = source_trees["re/_parser.py"]
    public_compile = functions(re_tree, "compile")
    re_compile = functions(re_tree, "_compile")
    isstring = functions(compiler_tree, "isstring")
    compiler_compile = functions(compiler_tree, "compile")
    parser_parse = functions(parser_tree, "parse")
    regex_parser_functions = functions(parser_tree, "_parse")
    tokenizers = [node for node in parser_tree.body
                  if isinstance(node, ast.ClassDef) and node.name == "Tokenizer"]
    tokenizer_init = ([node for node in tokenizers[0].body
                       if isinstance(node, ast.FunctionDef)
                       and node.name == "__init__"]
                      if len(tokenizers) == 1 else [])
    if (len(public_compile) != 1 or len(re_compile) != 1
            or len(isstring) != 1 or len(compiler_compile) != 1
            or len(parser_parse) != 1 or len(tokenizer_init) != 1
            or len(regex_parser_functions) != 1):
        return []

    verbose_parser_branches = [
        node for node in ast.walk(regex_parser_functions[0])
        if isinstance(node, ast.If) and isinstance(node.test, ast.Name)
        and node.test.id == "verbose"
    ]
    expected_verbose_parser_branch = (
        "if verbose:\n"
        "    if this in WHITESPACE:\n"
        "        continue\n"
        "    if this == '#':\n"
        "        while True:\n"
        "            this = sourceget()\n"
        "            if this is None or this == '\\n':\n"
        "                break\n"
        "        continue"
    )
    if (len(verbose_parser_branches) != 1
            or ast.unparse(verbose_parser_branches[0])
            != expected_verbose_parser_branch):
        return []

    whitespace_assignments = [
        node for node in parser_tree.body
        if isinstance(node, ast.Assign)
        and any(isinstance(target, ast.Name) and target.id == "WHITESPACE"
                for target in node.targets)
    ]
    if (len(whitespace_assignments) != 1
            or not isinstance(whitespace_assignments[0].value, ast.Call)
            or not isinstance(whitespace_assignments[0].value.func, ast.Name)
            or whitespace_assignments[0].value.func.id != "frozenset"
            or len(whitespace_assignments[0].value.args) != 1
            or whitespace_assignments[0].value.keywords):
        return []
    try:
        whitespace_literal = ast.literal_eval(
            whitespace_assignments[0].value.args[0],
        )
    except (ValueError, TypeError, SyntaxError):
        return []
    if (type(whitespace_literal) is not str or not whitespace_literal
            or any(len(character) != 1 for character in whitespace_literal)):
        return []
    verbose_whitespace = frozenset(whitespace_literal)

    public_body = list(public_compile[0].body)
    if (public_body and isinstance(public_body[0], ast.Expr)
            and isinstance(public_body[0].value, ast.Constant)
            and type(public_body[0].value.value) is str):
        public_body.pop(0)
    if (len(public_body) != 1 or not isinstance(public_body[0], ast.Return)
            or ast.unparse(public_body[0].value) != "_compile(pattern, flags)"):
        return []

    def default_flags_zero(function, pattern_name):
        return (
            [argument.arg for argument in function.args.args]
            == [pattern_name, "flags"]
            and len(function.args.defaults) == 1
            and ast.unparse(function.args.defaults[0]) == "0"
        )

    if (not default_flags_zero(public_compile[0], "pattern")
            or [argument.arg for argument in re_compile[0].args.args]
            != ["pattern", "flags"]
            or re_compile[0].args.defaults
            or not default_flags_zero(compiler_compile[0], "p")):
        return []
    isstring_body = isstring[0].body
    if (len(isstring_body) != 1 or not isinstance(isstring_body[0], ast.Return)
            or ast.unparse(isstring_body[0].value)
            != "isinstance(obj, (str, bytes))"):
        return []
    compile_if = [node for node in ast.walk(compiler_compile[0])
                  if isinstance(node, ast.If)
                  and ast.unparse(node.test) == "isstring(p)"]
    if (len(compile_if) != 1 or len(compile_if[0].body) < 2
            or ast.unparse(compile_if[0].body[1])
            != "p = _parser.parse(p, flags)"):
        return []
    if (not any(isinstance(node, ast.Call)
                and ast.unparse(node.func) == "_compiler.compile"
                and [ast.unparse(arg) for arg in node.args]
                == ["pattern", "flags"]
                for node in ast.walk(re_compile[0]))):
        return []
    if (len(parser_parse[0].body) < 1
            or ast.unparse(parser_parse[0].body[0]) != "source = Tokenizer(str)"):
        return []
    parse_sub_calls = [
        node for node in ast.walk(parser_parse[0])
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
        and node.func.id == "_parse_sub"
    ]
    if (len(parse_sub_calls) != 1
            or [ast.unparse(argument) for argument in parse_sub_calls[0].args]
            != ["source", "state", "flags & SRE_FLAG_VERBOSE", "0"]):
        return []
    init_body = tokenizer_init[0].body
    if (not init_body or ast.unparse(init_body[0])
            != "self.istext = isinstance(string, str)"):
        return []

    compiler_constants_imports = [
        node for node in compiler_tree.body
        if isinstance(node, ast.ImportFrom) and node.level == 1
        and node.module == "_constants"
        and any(alias.name == "*" for alias in node.names)
    ]
    regex_flags = [node for node in re_tree.body
                   if isinstance(node, ast.ClassDef) and node.name == "RegexFlag"]
    if (len(compiler_constants_imports) != 1 or len(regex_flags) != 1
            or "enum.global_enum" not in
            [ast.unparse(decorator) for decorator in regex_flags[0].decorator_list]
            or "enum._simple_enum(enum.IntFlag, boundary=enum.KEEP)" not in
            [ast.unparse(decorator) for decorator in regex_flags[0].decorator_list]
            or regex_flags[0].bases):
        return []
    sre_flag_values = {}
    for node in constants_tree.body:
        if isinstance(node, ast.Assign) and len(node.targets) == 1:
            target = node.targets[0]
            if (isinstance(target, ast.Name)
                    and target.id.startswith("SRE_FLAG_")
                    and isinstance(node.value, ast.Constant)
                    and type(node.value.value) is int):
                sre_flag_values[target.id] = node.value.value
    re_flag_values = {}
    for node in regex_flags[0].body:
        if not isinstance(node, ast.Assign):
            continue
        value = None
        if (isinstance(node.value, ast.Attribute)
                and isinstance(node.value.value, ast.Name)
                and node.value.value.id == "_compiler"):
            value = sre_flag_values.get(node.value.attr)
        elif (isinstance(node.value, ast.Constant)
                and type(node.value.value) is int):
            value = node.value.value
        if value is not None:
            for target in node.targets:
                if isinstance(target, ast.Name):
                    re_flag_values[target.id] = value
    if not {"ASCII", "MULTILINE", "DOTALL", "VERBOSE"}.issubset(re_flag_values):
        return []

    def evaluate_flag_expression(expression, tree, use_line):
        if type(expression) is not str:
            return None
        try:
            root = ast.parse(expression, mode="eval").body
        except SyntaxError:
            return None

        def evaluate(node, line, depth=0):
            if depth > 12:
                return None
            if (isinstance(node, ast.Constant)
                    and type(node.value) is int):
                return node.value
            if (isinstance(node, ast.Attribute)
                    and isinstance(node.value, ast.Name)
                    and node.value.id == "re"):
                imports = [
                    statement for statement in tree.body
                    if isinstance(statement, ast.Import)
                    and statement.lineno < line
                    and any(alias.name == "re"
                            and (alias.asname or "re") == "re"
                            for alias in statement.names)
                ]
                if (len(imports) != 1
                        or any(isinstance(candidate, ast.Name)
                               and candidate.id == "re"
                               and isinstance(candidate.ctx, (ast.Store, ast.Del))
                               and candidate.lineno < line
                               for candidate in ast.walk(tree))):
                    return None
                return re_flag_values.get(node.attr)
            if isinstance(node, ast.Name):
                assignments = []
                for statement in tree.body:
                    if statement.lineno >= line:
                        continue
                    if (isinstance(statement, ast.Assign)
                            and len(statement.targets) == 1
                            and isinstance(statement.targets[0], ast.Name)
                            and statement.targets[0].id == node.id):
                        assignments.append((statement.value, statement.lineno))
                    elif (isinstance(statement, ast.AnnAssign)
                            and isinstance(statement.target, ast.Name)
                            and statement.target.id == node.id
                            and statement.value is not None):
                        assignments.append((statement.value, statement.lineno))
                if len(assignments) != 1:
                    return None
                value, assigned_line = assignments[0]
                return evaluate(value, assigned_line, depth + 1)
            if (isinstance(node, ast.BinOp) and isinstance(node.op, ast.BitOr)):
                left = evaluate(node.left, line, depth + 1)
                right = evaluate(node.right, line, depth + 1)
                return left | right if left is not None and right is not None else None
            return None

        return evaluate(root, use_line)

    candidates = _target_re_compile_input_candidates(files, modules)
    output = []
    chain_hashes = {path: hashlib.sha256(files[path]).hexdigest()
                    for path, _ in source_specs}
    for candidate in candidates:
        kind = candidate["argument_kind"]
        if kind not in ("STRING_LITERAL", "BYTES_LITERAL"):
            continue
        source = files.get(candidate["source_path"])
        pattern_literals = []
        if (type(source) is bytes
                and hashlib.sha256(source).hexdigest() == candidate["source_sha256"]):
            try:
                caller_tree = ast.parse(
                    source.decode("utf-8"), filename=candidate["source_path"],
                )
            except (UnicodeError, SyntaxError):
                caller_tree = None
            if caller_tree is not None:
                for node in ast.walk(caller_tree):
                    if (not isinstance(node, ast.Call)
                            or node.lineno != candidate["line"]
                            or not node.args):
                        continue
                    try:
                        literal = ast.literal_eval(node.args[0])
                    except (ValueError, TypeError, SyntaxError):
                        continue
                    if type(literal) is str:
                        literal_digest = hashlib.sha256(
                            literal.encode("utf-8")
                        ).hexdigest()
                    elif type(literal) is bytes:
                        literal_digest = hashlib.sha256(literal).hexdigest()
                    else:
                        continue
                    if literal_digest == candidate["argument_sha256"]:
                        pattern_literals.append(literal)
        inline_verbose_candidates = (
            _regex_inline_flag_directive_candidates(pattern_literals[0])
            if len(pattern_literals) == 1 else None
        )
        verbose_ignored_syntax_candidates = (
            _regex_verbose_ignored_syntax_candidates(
                pattern_literals[0], verbose_whitespace,
            )
            if len(pattern_literals) == 1 else None
        )
        flags_value = None
        flags_resolution = "UNRESOLVED"
        if candidate["flags_argument_kind"] == "OMITTED":
            flags_value = 0
            flags_resolution = "PINNED_DEFAULT_ZERO"
        elif candidate["flags_argument_kind"] == "INT_LITERAL":
            flags_value = candidate["flags_literal_value"]
            flags_resolution = "INTEGER_LITERAL"
        else:
            caller_source = files.get(candidate["source_path"])
            if (type(caller_source) is bytes
                    and hashlib.sha256(caller_source).hexdigest()
                    == candidate["source_sha256"]):
                try:
                    caller_tree = ast.parse(
                        caller_source.decode("utf-8"),
                        filename=candidate["source_path"],
                    )
                except (UnicodeError, SyntaxError):
                    caller_tree = None
                if caller_tree is not None:
                    flags_value = evaluate_flag_expression(
                        candidate["flags_argument_expression"],
                        caller_tree, candidate["line"],
                    )
                    if flags_value is not None:
                        flags_resolution = "PINNED_REGEXFLAG_EXPRESSION"
        verbose_flag = sre_flag_values.get("SRE_FLAG_VERBOSE")
        output.append({
            **candidate,
            "pattern_type_if_call_evaluates": (
                "str" if kind == "STRING_LITERAL" else "bytes"
            ),
            "tokenizer_istext_if_parser_entry_reached": (
                kind == "STRING_LITERAL"
            ),
            "flags_value_if_call_evaluates": flags_value,
            "verbose_mode_if_parser_entry_reached": (
                bool(flags_value & verbose_flag)
                if flags_value is not None and type(verbose_flag) is int else None
            ),
            "inline_verbose_flag_group_candidates_if_literal_bound": (
                inline_verbose_candidates
            ),
            "inline_verbose_flag_scan_bound": len(pattern_literals) == 1,
            "verbose_ignored_syntax_candidates_if_verbose_and_literal_bound": (
                verbose_ignored_syntax_candidates
            ),
            "flags_resolution": flags_resolution,
            "re_flag_constants_source_sha256": (
                RE_CONSTANTS_SOURCE_SHA256
                if flags_resolution == "PINNED_REGEXFLAG_EXPRESSION" else None
            ),
            "standard_re_flag_binding_observed": False,
            "parser_entry_observed": False,
            "standard_re_compile_binding_observed": False,
            "cache_path_candidate": cache_path_candidate,
            "tokenizer_access_candidate": tokenizer_access_candidate,
            "parser_sourceget_candidate": parser_sourceget_candidate,
            "parser_sub_dispatch_candidate": parser_sub_dispatch_candidate,
            "parser_alternation_candidate": parser_alternation_candidate,
            "parser_multi_alternative_candidate": parser_multi_alternative_candidate,
            "parser_charset_candidate": parser_charset_candidate,
            "parser_prefix_candidate": parser_prefix_candidate,
            "parser_subpattern_order_candidate": parser_subpattern_order_candidate,
            "parser_uniq_candidate": parser_uniq_candidate,
            "parser_group_state_candidate": parser_group_state_candidate,
            "parser_group_call_candidate": parser_group_call_candidate,
            "parser_forward_group_candidate": parser_forward_group_candidate,
            "parser_lookbehind_candidate": parser_lookbehind_candidate,
            "parser_group_width_candidate": parser_group_width_candidate,
            "parser_group_compiler_candidate": parser_group_compiler_candidate,
            "compiler_branch_candidate": compiler_branch_candidate,
            "compiler_code_candidate": compiler_code_candidate,
            "compiler_group_candidate": compiler_group_candidate,
            "compiler_debug_candidate": compiler_debug_candidate,
            "compiler_input_candidate": compiler_input_candidate,
            "parser_source_sha256": chain_hashes,
            "evidence_scope": "PINNED_RE_COMPILE_TO_TOKENIZER_TYPE_CANDIDATE",
        })
    return output


def _target_functools_lru_cache_condition_facts(files):
    """Resolve the negative-size guard across pinned stdlib call sites."""
    if type(files) is not dict:
        return {}
    source = files.get("functools.py")
    if (type(source) is not bytes
            or hashlib.sha256(source).hexdigest() != FUNCTOOLS_SOURCE_SHA256):
        return {}
    try:
        trees = {
            path: ast.parse(data, filename=path)
            for path, data in files.items()
            if type(data) is bytes and path.endswith(".py")
            and "test" not in path.split("/")
        }
    except SyntaxError:
        return {}
    tree = trees.get("functools.py")
    functions = [node for node in tree.body if isinstance(node, ast.FunctionDef)
                 and node.name in {"lru_cache", "_lru_cache_wrapper"}
                 ] if tree else []
    if len(functions) != 2:
        return {}
    function = next((node for node in functions if node.name == "lru_cache"), None)
    wrapper = next((node for node in functions
                    if node.name == "_lru_cache_wrapper"), None)
    if function is None or wrapper is None:
        return {}
    expected = {
        507: "isinstance(maxsize, int)",
        509: "maxsize < 0",
        511: "callable(maxsize) and isinstance(typed, bool)",
        517: "maxsize is not None",
    }
    guards = {node.lineno: ast.unparse(node.test) for node in ast.walk(function)
              if isinstance(node, ast.If) and node.lineno in expected}
    wrapper_guards = {
        node.lineno: ast.unparse(node.test) for node in ast.walk(wrapper)
        if isinstance(node, ast.If) and node.lineno in (543, 552)
    }
    if (guards != expected
            or wrapper_guards != {543: "maxsize == 0", 552: "maxsize is None"}
            or [arg.arg for arg in function.args.args] != ["maxsize", "typed"]
            or [ast.unparse(value) for value in function.args.defaults]
            != ["128", "False"]):
        return {}
    callsite_rows = []
    caller_source_rows = []
    for path, other_tree in trees.items():
        if any(isinstance(node, ast.ImportFrom) and node.module == "functools"
               and any(alias.name == "*" for alias in node.names)
               for node in ast.walk(other_tree)):
            return {}
        aliases = {"lru_cache"} if path == "functools.py" else {
            alias.asname or alias.name
            for node in ast.walk(other_tree)
            if isinstance(node, ast.ImportFrom) and node.module == "functools"
            for alias in node.names if alias.name == "lru_cache"
        }
        module_aliases = {
            alias.asname or alias.name.split(".")[0]
            for node in ast.walk(other_tree) if isinstance(node, ast.Import)
            for alias in node.names if alias.name == "functools"
        }
        if aliases or module_aliases:
            caller_source_rows.append([
                path, hashlib.sha256(files[path]).hexdigest(),
            ])
        def is_lru_cache(expression):
            return (
                isinstance(expression, ast.Name) and expression.id in aliases
                or isinstance(expression, ast.Attribute)
                and expression.attr == "lru_cache"
                and isinstance(expression.value, ast.Name)
                and expression.value.id in module_aliases
            )
        for node in ast.walk(other_tree):
            if isinstance(node, ast.Call) and is_lru_cache(node.func):
                callsite_rows.append([path, node.lineno, "call", ast.unparse(node)])
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                for decorator in node.decorator_list:
                    if is_lru_cache(decorator) and not isinstance(decorator, ast.Call):
                        callsite_rows.append([
                            path, decorator.lineno, "bare", ast.unparse(decorator),
                        ])
    callsite_rows.sort()
    caller_source_rows.sort()
    callsite_digest = hashlib.sha256(json.dumps(
        [callsite_rows, caller_source_rows], separators=(",", ":"),
    ).encode()).hexdigest()
    if callsite_digest != FUNCTOOLS_LRU_CACHE_CALLS_SHA256:
        return {}
    return {
        ("functools", "functools.py", 507): (False, True),
        ("functools", "functools.py", 509): (False,),
        ("functools", "functools.py", 511): (False, True),
        ("functools", "functools.py", 517): (False,),
        ("functools", "functools.py", 543): (False,),
        ("functools", "functools.py", 552): (False, True),
    }


def _target_logging_lock_line_facts(files, thread_module_source):
    """Resolve logging's lock-presence guards for the pinned import route."""
    logging_source = files.get("logging/__init__.py") if type(files) is dict else None
    threading_source = files.get("threading.py") if type(files) is dict else None
    if (type(logging_source) is not bytes or type(threading_source) is not bytes
            or type(thread_module_source) is not bytes
            or hashlib.sha256(logging_source).hexdigest() != LOGGING_SOURCE_SHA256
            or hashlib.sha256(threading_source).hexdigest()
            != THREADING_SOURCE_SHA256
            or hashlib.sha256(thread_module_source).hexdigest()
            != THREAD_NATIVE_ID_MODULE_SHA256):
        return {}
    try:
        logging_tree = ast.parse(logging_source, filename="logging/__init__.py")
        threading_tree = ast.parse(threading_source, filename="threading.py")
    except SyntaxError:
        return {}
    lock_assignments = [node for node in ast.walk(logging_tree)
                        if isinstance(node, ast.Assign)
                        and any(isinstance(target, ast.Name)
                                and target.id == "_lock"
                                for target in node.targets)]
    if (len(lock_assignments) != 1
            or ast.unparse(lock_assignments[0].value) != "threading.RLock()"):
        return {}
    lock_writes = [node for node in ast.walk(logging_tree)
                   if isinstance(node, ast.Name) and node.id == "_lock"
                   and isinstance(node.ctx, (ast.Store, ast.Del))]
    if len(lock_writes) != 1:
        return {}
    functions = {node.name: node for node in logging_tree.body
                 if isinstance(node, ast.FunctionDef)
                 and node.name in ("_acquireLock", "_releaseLock")}
    if set(functions) != {"_acquireLock", "_releaseLock"}:
        return {}
    expected_methods = {"_acquireLock": "acquire", "_releaseLock": "release"}
    facts = {}
    for name, method_name in expected_methods.items():
        guards = [node for node in ast.walk(functions[name])
                  if isinstance(node, ast.If)
                  and isinstance(node.test, ast.Name)
                  and node.test.id == "_lock"]
        if len(guards) != 1:
            return {}
        calls = [node for node in ast.walk(guards[0])
                 if isinstance(node, ast.Call)
                 and ast.unparse(node.func) == f"_lock.{method_name}"]
        if len(calls) != 1:
            return {}
        facts[guards[0].lineno] = False

    rlock_factories = [node for node in threading_tree.body
                       if isinstance(node, ast.FunctionDef)
                       and node.name == "RLock"]
    python_rlock_classes = [node for node in threading_tree.body
                            if isinstance(node, ast.ClassDef)
                            and node.name == "_RLock"]
    if len(rlock_factories) != 1 or len(python_rlock_classes) != 1:
        return {}
    factory_returns = [node for node in ast.walk(rlock_factories[0])
                       if isinstance(node, ast.Return)]
    if ({ast.unparse(node.value) for node in factory_returns
         if node.value is not None} != {"_PyRLock(*args, **kwargs)",
                                         "_CRLock(*args, **kwargs)"}):
        return {}
    if any(isinstance(node, ast.FunctionDef)
           and node.name in ("__bool__", "__len__")
           for node in ast.walk(python_rlock_classes[0])):
        return {}
    c_source = thread_module_source.decode("utf-8", errors="strict")
    slots_start = c_source.find("static PyType_Slot rlock_type_slots[] = {")
    slots_end = c_source.find("};", slots_start) if slots_start >= 0 else -1
    if slots_end <= slots_start:
        return {}
    rlock_slots = c_source[slots_start:slots_end]
    if ("Py_nb_bool" in rlock_slots or "Py_sq_length" in rlock_slots
            or "Py_tp_bool" in rlock_slots or "Py_mp_length" in rlock_slots):
        return {}
    if ("{Py_tp_new, rlock_new}" not in rlock_slots
            or "{Py_tp_methods, rlock_methods}" not in rlock_slots):
        return {}

    # The production archive is hash-pinned. Also fail closed if it adds a
    # source-level import or module-attribute route for mutating logging._lock.
    for path, candidate in files.items():
        if type(candidate) is not bytes or not path.endswith(".py"):
            continue
        if "test" in path.split("/"):
            continue
        try:
            tree = logging_tree if path == "logging/__init__.py" else ast.parse(
                candidate, filename=path,
            )
        except SyntaxError:
            return {}
        logging_aliases = {
            alias.asname or "logging"
            for node in ast.walk(tree) if isinstance(node, ast.Import)
            for alias in node.names if alias.name == "logging"
        }
        for node in ast.walk(tree):
            if (isinstance(node, ast.ImportFrom) and node.module == "logging"
                    and any(alias.name == "_lock" for alias in node.names)):
                return {}
            if (isinstance(node, ast.Attribute) and node.attr == "_lock"
                    and isinstance(node.value, ast.Name)
                    and node.value.id in logging_aliases
                    and isinstance(node.ctx, (ast.Store, ast.Del))):
                return {}
    return facts


def _target_logging_level_line_facts(files):
    """Resolve the import-time logging level type from pinned constructors."""
    if type(files) is not dict:
        return {}
    source = files.get("logging/__init__.py")
    if (type(source) is not bytes
            or hashlib.sha256(source).hexdigest() != LOGGING_SOURCE_SHA256):
        return {}
    try:
        trees = {
            path: ast.parse(data, filename=path)
            for path, data in files.items()
            if type(data) is bytes and path.endswith(".py")
            and "test" not in path.split("/")
        }
    except SyntaxError:
        return {}
    tree = trees.get("logging/__init__.py")
    if tree is None:
        return {}

    def class_node(name):
        matches = [node for node in tree.body if isinstance(node, ast.ClassDef)
                   and node.name == name]
        return matches[0] if len(matches) == 1 else None

    def method(owner, name):
        matches = [node for node in owner.body if isinstance(node, ast.FunctionDef)
                   and node.name == name] if owner else []
        return matches[0] if len(matches) == 1 else None

    level_functions = [node for node in ast.walk(tree)
                       if isinstance(node, ast.FunctionDef)
                       and node.name == "_checkLevel"]
    if len(level_functions) != 1:
        return {}
    level_function = level_functions[0]
    guards = [node for node in ast.walk(level_function)
              if isinstance(node, ast.If)
              and ast.unparse(node.test) == "isinstance(level, int)"]
    if (len(guards) != 1 or [arg.arg for arg in level_function.args.args]
            != ["level"]
            or any(isinstance(node, ast.Name) and node.id == "int"
                   and isinstance(node.ctx, (ast.Store, ast.Del))
                   for node in ast.walk(tree))):
        return {}
    check_calls = {node.lineno: ast.unparse(node)
                   for node in ast.walk(tree)
                   if isinstance(node, ast.Call)
                   and isinstance(node.func, ast.Name)
                   and node.func.id == "_checkLevel"}
    if check_calls != {
            935: "_checkLevel(level)",
            986: "_checkLevel(level)",
            1375: "_checkLevel(value)",
            1503: "_checkLevel(level)",
            1514: "_checkLevel(level)",
    }:
        return {}

    handler = class_node("Handler")
    stream_handler = class_node("StreamHandler")
    stderr_handler = class_node("_StderrHandler")
    manager = class_node("Manager")
    logger = class_node("Logger")
    root_logger = class_node("RootLogger")
    if any(node is None for node in (
            handler, stream_handler, stderr_handler, manager, logger, root_logger)):
        return {}
    if ([ast.unparse(base) for base in stream_handler.bases] != ["Handler"]
            or [ast.unparse(base) for base in stderr_handler.bases]
            != ["StreamHandler"]
            or [ast.unparse(base) for base in root_logger.bases] != ["Logger"]):
        return {}
    handler_init = method(handler, "__init__")
    stderr_init = method(stderr_handler, "__init__")
    manager_init = method(manager, "__init__")
    manager_get_logger = method(manager, "getLogger")
    logger_init = method(logger, "__init__")
    root_init = method(root_logger, "__init__")
    if any(node is None for node in (
            handler_init, stderr_init, manager_init, manager_get_logger,
            logger_init, root_init)):
        return {}
    if ([ast.unparse(value) for value in handler_init.args.defaults] != ["NOTSET"]
            or [ast.unparse(value) for value in logger_init.args.defaults]
            != ["NOTSET"]
            or not any(isinstance(node, ast.Call)
                       and ast.unparse(node) == "Handler.__init__(self, level)"
                       for node in ast.walk(stderr_init))
            or not any(isinstance(node, ast.Call)
                       and ast.unparse(node)
                       == "Logger.__init__(self, 'root', level)"
                       for node in ast.walk(root_init))
            or not any(isinstance(node, ast.Call)
                       and ast.unparse(node.func)
                       == "self.loggerClass or _loggerClass"
                       and len(node.args) == 1
                       and ast.unparse(node.args[0]) == "name"
                       for node in ast.walk(manager_get_logger))):
        return {}
    manager_disable_writes = [
        node for node in ast.walk(manager_init)
        if isinstance(node, ast.Assign)
        and any(isinstance(target, ast.Attribute)
                and ast.unparse(target) == "self.disable"
                for target in node.targets)
    ]
    disable_setters = [node for node in manager.body
                       if isinstance(node, ast.FunctionDef)
                       and node.name == "disable"
                       and any(ast.unparse(decorator) == "disable.setter"
                               for decorator in node.decorator_list)]
    if (len(manager_disable_writes) != 1
            or ast.unparse(manager_disable_writes[0].value) != "0"
            or len(disable_setters) != 1
            or not any(isinstance(node, ast.Call)
                       and ast.unparse(node) == "_checkLevel(value)"
                       for node in ast.walk(disable_setters[0]))):
        return {}

    constants = {}
    for node in tree.body:
        if isinstance(node, ast.Assign) and len(node.targets) == 1 \
                and isinstance(node.targets[0], ast.Name):
            constants[node.targets[0].id] = ast.unparse(node.value)
    if constants.get("NOTSET") != "0" or constants.get("WARNING") != "30":
        return {}
    logger_class_assignments = [node for node in tree.body
                                if isinstance(node, ast.Assign)
                                and any(isinstance(target, ast.Name)
                                        and target.id == "_loggerClass"
                                        for target in node.targets)]
    if (len(logger_class_assignments) != 1
            or ast.unparse(logger_class_assignments[0].value) != "Logger"):
        return {}
    manager_logger_class_assignments = [
        node for node in ast.walk(manager_init)
        if isinstance(node, ast.Assign)
        and any(isinstance(target, ast.Attribute)
                and ast.unparse(target) == "self.loggerClass"
                for target in node.targets)
    ]
    if (len(manager_logger_class_assignments) != 1
            or not isinstance(manager_logger_class_assignments[0].value, ast.Constant)
            or manager_logger_class_assignments[0].value.value is not None):
        return {}
    root_assignments = [
        node for node in tree.body if isinstance(node, ast.Assign)
        and any(isinstance(target, ast.Name) and target.id == "root"
                for target in node.targets)
        and isinstance(node.value, ast.Call)
        and ast.unparse(node.value) == "RootLogger(WARNING)"
    ]
    manager_assignments = [
        node for node in tree.body if isinstance(node, ast.Assign)
        and any(isinstance(target, ast.Attribute)
                and ast.unparse(target) == "Logger.manager"
                for target in node.targets)
        and isinstance(node.value, ast.Call)
        and ast.unparse(node.value) == "Manager(Logger.root)"
    ]
    stderr_assignments = [
        node for node in tree.body if isinstance(node, ast.Assign)
        and isinstance(node.value, ast.Call)
        and ast.unparse(node.value) == "_StderrHandler(WARNING)"
    ]
    root_bindings = [node for node in tree.body if isinstance(node, ast.Assign)
                     and any(isinstance(target, ast.Attribute)
                             and ast.unparse(target) == "Logger.root"
                             for target in node.targets)
                     and ast.unparse(node.value) == "root"]
    if (len(root_assignments) != 1 or len(manager_assignments) != 1
            or len(stderr_assignments) != 1 or len(root_bindings) != 1
            or not root_assignments[0].lineno < root_bindings[0].lineno
            or not root_bindings[0].lineno < manager_assignments[0].lineno):
        return {}

    module_scope_calls = []
    caller_source_rows = []
    module_level_logger_api = {"Logger", "RootLogger", "Manager", "Handler",
                               "basicConfig", "setLevel", "setLoggerClass"}
    for path, other_tree in trees.items():
        parents = {child: parent for parent in ast.walk(other_tree)
                   for child in ast.iter_child_nodes(parent)}

        def is_module_scope(node):
            current = node
            while current in parents:
                current = parents[current]
                if isinstance(current, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    return False
            return True

        logging_aliases = {
            alias.asname or alias.name.split(".")[0]
            for node in ast.walk(other_tree) if isinstance(node, ast.Import)
            for alias in node.names if alias.name == "logging"
        }
        imported_api = {
            alias.asname or alias.name: alias.name
            for node in ast.walk(other_tree)
            if isinstance(node, ast.ImportFrom) and node.module == "logging"
            for alias in node.names
        }
        if any(alias.name == "*" for node in ast.walk(other_tree)
               if isinstance(node, ast.ImportFrom) and node.module == "logging"
               for alias in node.names):
            return {}
        if logging_aliases or imported_api:
            caller_source_rows.append(
                [path, hashlib.sha256(files[path]).hexdigest()]
            )
        for node in ast.walk(other_tree):
            if (isinstance(node, ast.Attribute)
                    and isinstance(node.ctx, (ast.Store, ast.Del))
                    and isinstance(node.value, ast.Name)
                    and node.value.id in logging_aliases
                    and node.attr in {"root", "manager", "_loggerClass"}):
                return {}
            if not isinstance(node, ast.Call) or not is_module_scope(node):
                continue
            if isinstance(node.func, ast.Attribute) and isinstance(
                    node.func.value, ast.Name) and node.func.value.id in logging_aliases:
                if node.func.attr == "_checkLevel":
                    return {}
                if node.func.attr in module_level_logger_api:
                    return {}
                if node.func.attr == "getLogger":
                    module_scope_calls.append([path, node.lineno, ast.unparse(node)])
            elif isinstance(node.func, ast.Name) and node.func.id in imported_api:
                if imported_api[node.func.id] == "_checkLevel":
                    return {}
                if imported_api[node.func.id] in module_level_logger_api:
                    return {}
                if imported_api[node.func.id] == "getLogger":
                    module_scope_calls.append([path, node.lineno, ast.unparse(node)])
            elif isinstance(node.func, ast.Attribute) and node.func.attr == "setLevel":
                return {}
            elif isinstance(node.func, ast.Attribute) \
                    and node.func.attr == "setLoggerClass":
                return {}
    module_scope_calls.sort()
    caller_source_rows.sort()
    digest = hashlib.sha256(json.dumps(
        [module_scope_calls, caller_source_rows], separators=(",", ":"),
    ).encode()).hexdigest()
    if digest != LOGGING_LEVEL_CALLS_SHA256:
        return {}
    expected_calls = {
        ("asyncio/log.py", 7, "logging.getLogger(__package__)"),
        ("concurrent/futures/_base.py", 43,
         "logging.getLogger('concurrent.futures')"),
        ("venv/__init__.py", 18, "logging.getLogger(__name__)"),
    }
    if {tuple(row) for row in module_scope_calls} != expected_calls:
        return {}

    return {guards[0].lineno: True}


def _target_collections_namedtuple_rename_line_facts(files):
    """Resolve namedtuple's rename guard when all production callers omit it."""
    source = (files.get("collections/__init__.py")
              if type(files) is dict else None)
    if (type(source) is not bytes
            or hashlib.sha256(source).hexdigest()
            != COLLECTIONS_SOURCE_SHA256):
        return {}
    try:
        trees = {
            path: ast.parse(candidate, filename=path)
            for path, candidate in files.items()
            if type(candidate) is bytes and path.endswith(".py")
            and "test" not in path.split("/")
        }
    except SyntaxError:
        return {}
    calls = []
    for path, tree in trees.items():
        parents = {child: node for node in ast.walk(tree)
                   for child in ast.iter_child_nodes(node)}
        namedtuple_aliases = set()
        collections_aliases = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom):
                for alias in node.names:
                    if alias.name == "namedtuple":
                        if node.module != "collections":
                            return {}
                        namedtuple_aliases.add(alias.asname or alias.name)
            elif isinstance(node, ast.Import):
                for alias in node.names:
                    if (alias.name == "collections"
                            or (alias.name.startswith("collections.")
                                and alias.asname is None)):
                        collections_aliases.add(alias.asname or "collections")
        for node in ast.walk(tree):
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                if node.func.id in namedtuple_aliases:
                    calls.append((path, node))
            elif isinstance(node, ast.Attribute) and node.attr == "namedtuple":
                parent = parents.get(node)
                if (not isinstance(parent, ast.Call) or parent.func is not node
                        or not isinstance(node.value, ast.Name)
                        or node.value.id not in collections_aliases):
                    return {}
                calls.append((path, parent))
            if isinstance(node, ast.Name) and node.id in namedtuple_aliases:
                parent = parents.get(node)
                if not isinstance(parent, ast.Call) or parent.func is not node:
                    return {}
        for node in ast.walk(tree):
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                if (node.func.id == "getattr" and len(node.args) > 1
                        and isinstance(node.args[1], ast.Constant)
                        and node.args[1].value == "namedtuple"):
                    return {}
    if not calls:
        return {}
    for _, call in calls:
        if len(call.args) > 2:
            return {}
        for keyword in call.keywords:
            if keyword.arg is None:
                return {}
            if keyword.arg == "rename" and not (
                    isinstance(keyword.value, ast.Constant)
                    and keyword.value.value is False):
                return {}

    try:
        tree = ast.parse(source, filename="collections/__init__.py")
    except SyntaxError:
        return {}
    functions = [node for node in tree.body
                 if isinstance(node, ast.FunctionDef)
                 and node.name == "namedtuple"]
    if len(functions) != 1:
        return {}
    function = functions[0]
    guards = [node for node in ast.walk(function)
              if isinstance(node, ast.If)
              and isinstance(node.test, ast.Name)
              and node.test.id == "rename"]
    args = function.args
    if (len(guards) != 1 or len(args.args) != 2
            or [arg.arg for arg in args.args] != ["typename", "field_names"]
            or [arg.arg for arg in args.kwonlyargs]
            != ["rename", "defaults", "module"]
            or len(args.kw_defaults) != 3
            or not isinstance(args.kw_defaults[0], ast.Constant)
            or args.kw_defaults[0].value is not False
            or any(isinstance(node, ast.Name) and node.id == "rename"
                   and isinstance(node.ctx, (ast.Store, ast.Del))
                   for node in ast.walk(function))):
        return {}
    return {guards[0].lineno: False}


def _target_collections_namedtuple_string_type_line_facts(files):
    """Resolve namedtuple's type guard after its string normalization."""
    source = (files.get("collections/__init__.py")
              if type(files) is dict else None)
    if (type(source) is not bytes
            or hashlib.sha256(source).hexdigest()
            != COLLECTIONS_SOURCE_SHA256):
        return {}
    try:
        tree = ast.parse(source, filename="collections/__init__.py")
    except SyntaxError:
        return {}
    functions = [node for node in tree.body
                 if isinstance(node, ast.FunctionDef)
                 and node.name == "namedtuple"]
    if len(functions) != 1:
        return {}
    function = functions[0]
    assignments = [node for node in function.body
                   if isinstance(node, ast.Assign)]
    field_normalizations = [node for node in assignments
                            if any(isinstance(target, ast.Name)
                                   and target.id == "field_names"
                                   for target in node.targets)
                            and ast.unparse(node.value)
                            == "list(map(str, field_names))"]
    typename_normalizations = [node for node in assignments
                               if any(isinstance(target, ast.Name)
                                      and target.id == "typename"
                                      for target in node.targets)
                               and ast.unparse(node.value)
                               == "_sys.intern(str(typename))"]
    loops = [node for node in function.body
             if isinstance(node, ast.For)
             and isinstance(node.target, ast.Name)
             and node.target.id == "name"
             and ast.unparse(node.iter) == "[typename] + field_names"]
    if (len(field_normalizations) != 1
            or len(typename_normalizations) != 1 or len(loops) != 1
            or field_normalizations[0].lineno >= loops[0].lineno
            or typename_normalizations[0].lineno >= loops[0].lineno):
        return {}
    guards = [node for node in ast.walk(loops[0])
              if isinstance(node, ast.If)
              and ast.unparse(node.test) == "type(name) is not str"]
    if len(guards) != 1:
        return {}
    if any(isinstance(node, ast.Name) and node.id in ("str", "type")
           and isinstance(node.ctx, (ast.Store, ast.Del))
           for node in ast.walk(tree)):
        return {}
    if not any(isinstance(node, ast.Raise)
               and isinstance(node.exc, ast.Call)
               and ast.unparse(node.exc.func) == "TypeError"
               for node in ast.walk(guards[0])):
        return {}
    return {guards[0].lineno: False}


def _target_collections_namedtuple_module_line_facts(
        files, sys_module_source, sys_clinic_source):
    """Resolve namedtuple's final module guard on the pinned CPython route."""
    source = (files.get("collections/__init__.py")
              if type(files) is dict else None)
    if (type(source) is not bytes
            or hashlib.sha256(source).hexdigest()
            != COLLECTIONS_SOURCE_SHA256
            or type(sys_module_source) is not bytes
            or hashlib.sha256(sys_module_source).hexdigest()
            != SYS_MODULE_C_SHA256
            or type(sys_clinic_source) is not bytes
            or hashlib.sha256(sys_clinic_source).hexdigest()
            != SYS_MODULE_CLINIC_SHA256
            or _TARGET_BUILTIN_MEMBERSHIP.get("sys") is not True):
        return {}
    try:
        tree = ast.parse(source, filename="collections/__init__.py")
    except SyntaxError:
        return {}
    sys_aliases = [alias.asname or alias.name
                   for node in tree.body if isinstance(node, ast.Import)
                   for alias in node.names if alias.name == "sys"]
    if (len(sys_aliases) != 1
            or any(isinstance(node, ast.Name) and node.id == sys_aliases[0]
                   and isinstance(node.ctx, (ast.Store, ast.Del))
                   for node in ast.walk(tree))):
        return {}
    function_nodes = [node for node in tree.body
                      if isinstance(node, ast.FunctionDef)
                      and node.name == "namedtuple"]
    if len(function_nodes) != 1:
        return {}
    function = function_nodes[0]
    fallback_guards = [node for node in function.body
                       if isinstance(node, ast.If)
                       and ast.unparse(node.test) == "module is None"]
    final_guards = [node for node in function.body
                    if isinstance(node, ast.If)
                    and ast.unparse(node.test) == "module is not None"]
    if len(fallback_guards) != 1 or len(final_guards) != 1:
        return {}
    fallback = fallback_guards[0]
    fallback_calls = [node for node in ast.walk(fallback)
                      if isinstance(node, ast.Call)
                      and ast.unparse(node)
                      == f"{sys_aliases[0]}._getframemodulename(1)"]
    default_assignments = [node for node in ast.walk(fallback)
                           if isinstance(node, ast.Assign)
                           and any(isinstance(target, ast.Name)
                                   and target.id == "module"
                                   for target in node.targets)
                           and ast.unparse(node.value)
                           == f"{sys_aliases[0]}._getframemodulename(1) or '__main__'"]
    if len(fallback_calls) != 1 or len(default_assignments) != 1:
        return {}
    clinic_text = sys_clinic_source.decode("utf-8", errors="strict")
    c_text = sys_module_source.decode("utf-8", errors="strict")
    method_macro = "SYS__GETFRAMEMODULENAME_METHODDEF"
    clinic_lines = clinic_text.splitlines()
    clinic_index = next((index for index, line in enumerate(clinic_lines)
                         if line.startswith(f"#define {method_macro}")), None)
    methods_start = c_text.find("static PyMethodDef sys_methods[] = {")
    methods_end = c_text.find("};", methods_start) if methods_start >= 0 else -1
    module_start = c_text.find("static struct PyModuleDef sysmodule = {")
    module_end = c_text.find("};", module_start) if module_start >= 0 else -1
    if (clinic_index is None or clinic_index + 1 >= len(clinic_lines)
            or '"_getframemodulename"' not in clinic_lines[clinic_index + 1]
            or "sys__getframemodulename" not in clinic_lines[clinic_index + 1]
            or '#include "clinic/sysmodule.c.h"' not in c_text
            or methods_end <= methods_start
            or method_macro not in c_text[methods_start:methods_end]
            or module_end <= module_start
            or "sys_methods," not in c_text[module_start:module_end]
            or "sys__getframemodulename_impl" not in c_text
            or "PyFunction_GetModule" not in c_text
            or "Py_RETURN_NONE" not in c_text):
        return {}
    for path, candidate in files.items():
        if (type(candidate) is not bytes or not path.endswith(".py")
                or "test" in path.split("/")):
            continue
        try:
            caller_tree = tree if path == "collections/__init__.py" else ast.parse(
                candidate, filename=path,
            )
        except SyntaxError:
            return {}
        caller_sys_aliases = {
            alias.asname or alias.name
            for node in ast.walk(caller_tree) if isinstance(node, ast.Import)
            for alias in node.names if alias.name == "sys"
        }
        if any(isinstance(node, ast.Attribute)
               and node.attr == "_getframemodulename"
               and isinstance(node.ctx, (ast.Store, ast.Del))
               and isinstance(node.value, ast.Name)
               and node.value.id in caller_sys_aliases
               for node in ast.walk(caller_tree)):
            return {}
        if any(isinstance(node, ast.Call)
               and isinstance(node.func, ast.Name)
               and node.func.id == "setattr" and len(node.args) >= 2
               and isinstance(node.args[0], ast.Name)
               and node.args[0].id in caller_sys_aliases
               and isinstance(node.args[1], ast.Constant)
               and node.args[1].value == "_getframemodulename"
               for node in ast.walk(caller_tree)):
            return {}
    return {final_guards[0].lineno: True}


def _target_collections_namedtuple_call_condition_facts(files):
    """Bind field-name and defaults guard outcomes to all stdlib callers."""
    if type(files) is not dict:
        return {}
    source = files.get("collections/__init__.py")
    inspect_source = files.get("inspect.py")
    typing_source = files.get("typing.py")
    keyword_source = files.get("keyword.py")
    if (type(source) is not bytes
            or hashlib.sha256(source).hexdigest() != COLLECTIONS_SOURCE_SHA256
            or type(inspect_source) is not bytes
            or hashlib.sha256(inspect_source).hexdigest()
            != INSPECT_SOURCE_SHA256
            or type(typing_source) is not bytes
            or hashlib.sha256(typing_source).hexdigest() != TYPING_SOURCE_SHA256):
        return {}
    if (type(keyword_source) is not bytes
            or hashlib.sha256(keyword_source).hexdigest()
            != KEYWORD_SOURCE_SHA256):
        return {}
    try:
        trees = {
            path: ast.parse(data, filename=path)
            for path, data in files.items()
            if type(data) is bytes and path.endswith(".py")
            and "test" not in path.split("/")
        }
    except SyntaxError:
        return {}
    source_tree = trees.get("collections/__init__.py")
    function = next((node for node in source_tree.body
                     if isinstance(node, ast.FunctionDef)
                     and node.name == "namedtuple"), None) if source_tree else None
    guards = [node for node in ast.walk(function)
              if isinstance(node, ast.If)
              and ast.unparse(node.test) == "isinstance(field_names, str)"] if function else []
    defaults_guards = [node for node in ast.walk(function)
                       if isinstance(node, ast.If)
                       and ast.unparse(node.test) == "defaults is not None"] if function else []
    module_guards = [node for node in ast.walk(function)
                     if isinstance(node, ast.If)
                     and ast.unparse(node.test) == "module is None"] if function else []
    identifier_guards = [node for node in ast.walk(function)
                         if isinstance(node, ast.If)
                         and ast.unparse(node.test) == "not name.isidentifier()"] if function else []
    keyword_guards = [node for node in ast.walk(function)
                      if isinstance(node, ast.If)
                      and ast.unparse(node.test) == "_iskeyword(name)"] if function else []
    private_field_guards = [node for node in ast.walk(function)
                            if isinstance(node, ast.If)
                            and ast.unparse(node.test)
                            == "name.startswith('_') and (not rename)"] if function else []
    duplicate_field_guards = [node for node in ast.walk(function)
                              if isinstance(node, ast.If)
                              and ast.unparse(node.test) == "name in seen"] if function else []
    defaults_length_guards = [node for node in ast.walk(function)
                              if isinstance(node, ast.If)
                              and ast.unparse(node.test)
                              == "len(defaults) > len(field_names)"] if function else []
    one_field_guards = [node for node in ast.walk(function)
                        if isinstance(node, ast.If)
                        and ast.unparse(node.test) == "num_fields == 1"] if function else []
    defaults_tuple_assignments = [node for node in ast.walk(function)
                                  if isinstance(node, ast.Assign)
                                  and any(isinstance(target, ast.Name)
                                          and target.id == "defaults"
                                          for target in node.targets)
                                  and ast.unparse(node.value) == "tuple(defaults)"] if function else []
    field_names_tuple_assignments = [node for node in ast.walk(function)
                                     if isinstance(node, ast.Assign)
                                     and any(isinstance(target, ast.Name)
                                             and target.id == "field_names"
                                             for target in node.targets)
                                     and ast.unparse(node.value)
                                     == "tuple(map(_sys.intern, field_names))"] if function else []
    num_fields_assignments = [node for node in ast.walk(function)
                              if isinstance(node, ast.Assign)
                              and any(isinstance(target, ast.Name)
                                      and target.id == "num_fields"
                                      for target in node.targets)
                              and ast.unparse(node.value) == "len(field_names)"] if function else []
    signature = function.args if function else None
    if (signature is None
            or [arg.arg for arg in signature.args] != ["typename", "field_names"]
            or [arg.arg for arg in signature.kwonlyargs]
            != ["rename", "defaults", "module"]
            or [ast.unparse(value) for value in signature.kw_defaults]
            != ["False", "None", "None"]):
        return {}
    namespace_assignments = [
        node for node in ast.walk(function)
        if isinstance(node, ast.Assign)
        and any(isinstance(target, ast.Name)
                and target.id == "class_namespace" for target in node.targets)
        and isinstance(node.value, ast.Dict)
    ] if function else []
    type_calls = [node for node in ast.walk(function)
                  if isinstance(node, ast.Call)
                  and ast.unparse(node.func) == "type"
                  and len(node.args) == 3
                  and ast.unparse(node.args[2]) == "class_namespace"] if function else []
    fields_entries = [
        value for assignment in namespace_assignments
        for key, value in zip(assignment.value.keys, assignment.value.values)
        if isinstance(key, ast.Constant) and key.value == "_fields"
    ]
    if (len(guards) != 1 or len(defaults_guards) != 2
            or len(module_guards) != 1 or len(identifier_guards) != 1
            or len(keyword_guards) != 1
            or len(private_field_guards) != 1
            or len(duplicate_field_guards) != 1
            or len(defaults_length_guards) != 1
            or len(one_field_guards) != 1
            or len(defaults_tuple_assignments) != 1
            or len(field_names_tuple_assignments) != 1
            or len(num_fields_assignments) != 1
            or defaults_tuple_assignments[0].lineno >= defaults_length_guards[0].lineno
            or field_names_tuple_assignments[0].lineno >= num_fields_assignments[0].lineno
            or num_fields_assignments[0].lineno >= one_field_guards[0].lineno
            or len(namespace_assignments) != 1
            or len(fields_entries) != 1
            or ast.unparse(fields_entries[0]) != "field_names"
            or len(type_calls) != 1):
        return {}
    defaults_conversion_guard = next((guard for guard in defaults_guards
                                      if any(node is defaults_tuple_assignments[0]
                                             for node in ast.walk(guard))
                                      and any(node is defaults_length_guards[0]
                                              for node in ast.walk(guard))), None)
    if (defaults_conversion_guard is None
            or defaults_tuple_assignments[0].lineno
            >= defaults_length_guards[0].lineno):
        return {}

    inspect_tree = trees.get("inspect.py")
    if inspect_tree is None:
        return {}
    expected_assignments = {
        "_Traceback": "namedtuple('_Traceback', 'filename lineno function code_context index')",
        "_FrameInfo": "namedtuple('_FrameInfo', ('frame',) + Traceback._fields)",
    }
    inspect_assignments = {
        target.id: ast.unparse(node.value)
        for node in inspect_tree.body if isinstance(node, ast.Assign)
        for target in node.targets if isinstance(target, ast.Name)
        and target.id in expected_assignments
    }
    traceback_classes = [node for node in inspect_tree.body
                         if isinstance(node, ast.ClassDef)
                         and node.name == "Traceback"]
    if (inspect_assignments != expected_assignments
            or len(traceback_classes) != 1
            or not any(isinstance(base, ast.Name) and base.id == "_Traceback"
                       for base in traceback_classes[0].bases)):
        return {}
    for node in ast.walk(inspect_tree):
        if (isinstance(node, ast.Attribute) and node.attr == "_fields"
                and isinstance(node.ctx, (ast.Store, ast.Del))):
            return {}

    keyword_tree = trees.get("keyword.py")
    keyword_lists = [node.value for node in keyword_tree.body
                     if isinstance(node, ast.Assign)
                     and any(isinstance(target, ast.Name)
                             and target.id == "kwlist" for target in node.targets)
                     and isinstance(node.value, ast.List)] if keyword_tree else []
    keyword_bindings = [node.value for node in keyword_tree.body
                        if isinstance(node, ast.Assign)
                        and any(isinstance(target, ast.Name)
                                and target.id == "iskeyword" for target in node.targets)] if keyword_tree else []
    collections_keyword_imports = [node for node in source_tree.body
                                   if isinstance(node, ast.ImportFrom)
                                   and node.module == "keyword"
                                   and any(alias.name == "iskeyword"
                                           and alias.asname == "_iskeyword"
                                           for alias in node.names)] if source_tree else []
    if (len(keyword_lists) != 1
            or any(not isinstance(value, ast.Constant)
                   or type(value.value) is not str
                   for value in keyword_lists[0].elts)
            or len(keyword_bindings) != 1
            or ast.unparse(keyword_bindings[0])
            != "frozenset(kwlist).__contains__"
            or len(collections_keyword_imports) != 1):
        return {}
    keyword_values = {value.value for value in keyword_lists[0].elts}

    typing_tree = trees.get("typing.py")
    nmtuple_functions = [node for node in typing_tree.body
                         if isinstance(node, ast.FunctionDef)
                         and node.name == "_make_nmtuple"] if typing_tree else []
    if len(nmtuple_functions) != 1:
        return {}
    nmtuple_body = nmtuple_functions[0].body
    field_lists = [index for index, node in enumerate(nmtuple_body)
                   if isinstance(node, ast.Assign)
                   and any(isinstance(target, ast.Name) and target.id == "fields"
                           for target in node.targets)
                   and ast.unparse(node.value) == "[n for n, t in types]"]
    nmtuple_calls = [index for index, node in enumerate(nmtuple_body)
                     if isinstance(node, ast.Assign)
                     and ast.unparse(node.value)
                     == "collections.namedtuple(name, fields, defaults=defaults, module=module)"]
    if (len(field_lists) != 1 or len(nmtuple_calls) != 1
            or field_lists[0] >= nmtuple_calls[0]
            or any(isinstance(node, (ast.Assign, ast.AnnAssign, ast.AugAssign))
                   and any(isinstance(target, ast.Name) and target.id == "fields"
                           for target in (node.targets if isinstance(node, ast.Assign)
                                          else [node.target]))
                   for node in nmtuple_body[field_lists[0] + 1:nmtuple_calls[0]])):
        return {}

    callsite_rows = []
    caller_source_rows = []
    outcomes = set()
    identifier_outcomes = set()
    keyword_outcomes = set()
    private_field_outcomes = set()
    duplicate_field_outcomes = set()
    defaults_length_outcomes = set()
    one_field_outcomes = set()
    defaults_outcomes = set()
    module_outcomes = set()
    for path, tree in trees.items():
        parents = {child: parent for parent in ast.walk(tree)
                   for child in ast.iter_child_nodes(parent)}
        if any(isinstance(node, ast.ImportFrom) and node.module == "collections"
               and any(alias.name == "*" for alias in node.names)
               for node in ast.walk(tree)):
            return {}
        aliases = {
            alias.asname or alias.name
            for node in ast.walk(tree) if isinstance(node, ast.ImportFrom)
            and node.module == "collections" for alias in node.names
            if alias.name == "namedtuple"
        }
        module_aliases = {
            alias.asname or alias.name.split(".")[0]
            for node in ast.walk(tree) if isinstance(node, ast.Import)
            for alias in node.names if alias.name == "collections"
        }
        if aliases or module_aliases:
            caller_source_rows.append(
                [path, hashlib.sha256(files[path]).hexdigest()]
            )

        def is_namedtuple(expression):
            return (
                isinstance(expression, ast.Name) and expression.id in aliases
                or isinstance(expression, ast.Attribute)
                and expression.attr == "namedtuple"
                and isinstance(expression.value, ast.Name)
                and expression.value.id in module_aliases
            )

        for node in ast.walk(tree):
            if not isinstance(node, ast.Call) or not is_namedtuple(node.func):
                continue
            callsite_rows.append([path, node.lineno, ast.unparse(node)])
            if len(node.args) > 2:
                return {}
            explicit_defaults = [keyword.value for keyword in node.keywords
                                 if keyword.arg == "defaults"]
            if len(explicit_defaults) > 1:
                return {}
            if not explicit_defaults:
                defaults_outcomes.add(False)
            elif isinstance(explicit_defaults[0], (ast.List, ast.Tuple)):
                defaults_outcomes.add(True)
            elif (path == "dis.py"
                  and ast.unparse(explicit_defaults[0]) == "[None] * 4"):
                defaults_outcomes.add(True)
            elif (isinstance(explicit_defaults[0], ast.Constant)
                  and explicit_defaults[0].value is None):
                defaults_outcomes.add(False)
            elif (path == "typing.py"
                  and isinstance(explicit_defaults[0], ast.Name)
                  and explicit_defaults[0].id == "defaults"):
                pass
            else:
                return {}
            explicit_module = [keyword.value for keyword in node.keywords
                               if keyword.arg == "module"]
            if len(explicit_module) > 1:
                return {}
            if not explicit_module:
                module_outcomes.add(True)
            elif (isinstance(explicit_module[0], ast.Constant)
                  and explicit_module[0].value is None):
                module_outcomes.add(True)
            elif (isinstance(explicit_module[0], ast.Constant)
                  and type(explicit_module[0].value) is str):
                module_outcomes.add(False)
            elif (path == "typing.py"
                  and isinstance(explicit_module[0], ast.Name)
                  and explicit_module[0].id == "module"):
                pass
            else:
                return {}
            value = (node.args[1] if len(node.args) > 1 else next(
                (keyword.value for keyword in node.keywords
                 if keyword.arg == "field_names"), None,
            ))
            if isinstance(value, ast.Constant) and type(value.value) is str:
                outcomes.add(True)
            elif isinstance(value, (ast.List, ast.Tuple)):
                outcomes.add(False)
            elif (path == "inspect.py" and isinstance(value, ast.BinOp)
                  and ast.unparse(value) == "('frame',) + Traceback._fields"):
                outcomes.add(False)
            elif (path == "typing.py" and isinstance(value, ast.Name)
                  and value.id == "fields"):
                outcomes.add(False)
            else:
                return {}
            current = node
            child = node
            module_scope = True
            while current in parents:
                child = current
                current = parents[current]
                if isinstance(current, (ast.FunctionDef, ast.AsyncFunctionDef)) \
                        and child in current.body:
                    module_scope = False
                    break
                if isinstance(current, ast.Lambda) and child is current.body:
                    module_scope = False
                    break
            if not module_scope:
                continue
            if (node.args and not any(keyword.arg == "typename"
                                      for keyword in node.keywords)):
                typename_value = node.args[0]
            else:
                typename_values = [keyword.value for keyword in node.keywords
                                   if keyword.arg == "typename"]
                if len(typename_values) != 1:
                    return {}
                typename_value = typename_values[0]
            if (isinstance(typename_value, ast.Constant)
                    and type(typename_value.value) is str):
                type_names = [typename_value.value]
            else:
                return {}
            if isinstance(value, ast.Constant) and type(value.value) is str:
                field_values = value.value.replace(",", " ").split()
            elif isinstance(value, (ast.List, ast.Tuple)):
                if any(not isinstance(item, ast.Constant)
                       or type(item.value) is not str for item in value.elts):
                    return {}
                field_values = [item.value for item in value.elts]
            elif (path == "inspect.py"
                  and ast.unparse(value) == "('frame',) + Traceback._fields"):
                traceback_fields = next((item.value.args[1]
                                         for item in inspect_tree.body
                                         if isinstance(item, ast.Assign)
                                         and any(isinstance(target, ast.Name)
                                                 and target.id == "_Traceback"
                                                 for target in item.targets)
                                         and isinstance(item.value, ast.Call)
                                         and ast.unparse(item.value.func) == "namedtuple"
                                         and len(item.value.args) == 2
                                         and isinstance(item.value.args[1], ast.Constant)
                                         and type(item.value.args[1].value) is str), None)
                if traceback_fields is None:
                    return {}
                field_values = ["frame"] + traceback_fields.value.split()
            else:
                return {}
            if any(not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", name)
                   for name in type_names + field_values):
                return {}
            if any(name in keyword_values for name in type_names + field_values):
                return {}
            if any(name.startswith("_") for name in field_values):
                return {}
            if len(field_values) != len(set(field_values)):
                return {}
            identifier_outcomes.add(False)
            keyword_outcomes.add(False)
            private_field_outcomes.add(False)
            duplicate_field_outcomes.add(False)
            default_count = 0
            defaults_is_none = not explicit_defaults
            if explicit_defaults:
                default_value = explicit_defaults[0]
                if isinstance(default_value, (ast.List, ast.Tuple)):
                    if any(isinstance(item, ast.Starred)
                           for item in default_value.elts):
                        return {}
                    default_count = len(default_value.elts)
                    defaults_is_none = False
                elif (path == "dis.py"
                      and ast.unparse(default_value) == "[None] * 4"):
                    default_count = 4
                    defaults_is_none = False
                elif (isinstance(default_value, ast.Constant)
                      and default_value.value is None):
                    default_count = 0
                    defaults_is_none = True
                else:
                    return {}
            if not defaults_is_none:
                defaults_length_outcomes.add(default_count > len(field_values))
            one_field_outcomes.add(len(field_values) == 1)
    callsite_rows.sort()
    caller_source_rows.sort()
    digest = hashlib.sha256(json.dumps(
        [callsite_rows, caller_source_rows], separators=(",", ":"),
    ).encode()).hexdigest()
    if (digest != COLLECTIONS_NAMEDTUPLE_CALLS_SHA256
            or outcomes != {False, True}
            or identifier_outcomes != {False}
            or keyword_outcomes != {False}
            or private_field_outcomes != {False}
            or duplicate_field_outcomes != {False}
            or defaults_length_outcomes != {False}
            or not one_field_outcomes
            or defaults_outcomes != {False, True}
            or module_outcomes != {False, True}):
        return {}
    facts = {
        ("collections", "collections/__init__.py", guards[0].lineno):
        tuple(sorted(outcomes)),
        ("collections", "collections/__init__.py", identifier_guards[0].lineno):
        tuple(sorted(identifier_outcomes)),
        ("collections", "collections/__init__.py", keyword_guards[0].lineno):
        tuple(sorted(keyword_outcomes)),
        ("collections", "collections/__init__.py", private_field_guards[0].lineno):
        tuple(sorted(private_field_outcomes)),
        ("collections", "collections/__init__.py", duplicate_field_guards[0].lineno):
        tuple(sorted(duplicate_field_outcomes)),
        ("collections", "collections/__init__.py", defaults_length_guards[0].lineno):
        tuple(sorted(defaults_length_outcomes)),
        ("collections", "collections/__init__.py", one_field_guards[0].lineno):
        tuple(sorted(one_field_outcomes)),
    }
    facts.update({
        ("collections", "collections/__init__.py", guard.lineno):
        tuple(sorted(defaults_outcomes))
        for guard in defaults_guards
    })
    facts[("collections", "collections/__init__.py", module_guards[0].lineno)] = (
        tuple(sorted(module_outcomes))
    )
    return facts


def _target_logging_style_line_facts(files):
    """Resolve both outcomes of the two source-bound public style guards."""
    source = files.get("logging/__init__.py") if type(files) is dict else None
    if (type(source) is not bytes
            or hashlib.sha256(source).hexdigest() != LOGGING_SOURCE_SHA256):
        return {}
    try:
        tree = ast.parse(source, filename="logging/__init__.py")
    except SyntaxError:
        return {}
    styles = [node for node in tree.body if isinstance(node, ast.Assign)
              and any(isinstance(target, ast.Name) and target.id == "_STYLES"
                      for target in node.targets)]
    formatter = [node for node in tree.body if isinstance(node, ast.ClassDef)
                 and node.name == "Formatter"]
    basic_config = [node for node in tree.body if isinstance(node, ast.FunctionDef)
                    and node.name == "basicConfig"]
    if len(styles) != 1 or len(formatter) != 1 or len(basic_config) != 1:
        return {}
    value = styles[0].value
    if not isinstance(value, ast.Dict):
        return {}
    try:
        style_keys = tuple(ast.literal_eval(key) for key in value.keys)
    except (TypeError, ValueError):
        return {}
    if style_keys != ("%", "{", "$"):
        return {}
    init = [node for node in formatter[0].body if isinstance(node, ast.FunctionDef)
            and node.name == "__init__"]
    if len(init) != 1:
        return {}
    init_style = [arg for arg, default in zip(init[0].args.args[-len(init[0].args.defaults):],
                                               init[0].args.defaults)
                  if arg.arg == "style" and isinstance(default, ast.Constant)
                  and default.value == "%"]
    guards = {
        "Formatter": [node for node in ast.walk(init[0]) if isinstance(node, ast.If)
                      and ast.unparse(node.test) == "style not in _STYLES"],
        "basicConfig": [node for node in ast.walk(basic_config[0]) if isinstance(node, ast.If)
                        and ast.unparse(node.test) == "style not in _STYLES"],
    }
    calls = [node for node in ast.walk(basic_config[0]) if isinstance(node, ast.Call)
             and isinstance(node.func, ast.Name) and node.func.id == "Formatter"
             and len(node.args) == 3 and isinstance(node.args[2], ast.Name)
             and node.args[2].id == "style"]
    style_sources = [node for node in ast.walk(basic_config[0])
                     if isinstance(node, ast.Assign)
                     and len(node.targets) == 1
                     and isinstance(node.targets[0], ast.Name)
                     and node.targets[0].id == "style"
                     and ast.unparse(node.value) == "kwargs.pop('style', '%')"]
    if (len(init_style) != 1 or any(len(rows) != 1 for rows in guards.values())
            or len(calls) != 1 or len(style_sources) != 1):
        return {}
    return {
        ("logging", "logging/__init__.py", guards["Formatter"][0].lineno):
            (False, True),
        ("logging", "logging/__init__.py", guards["basicConfig"][0].lineno):
            (False, True),
    }


def _target_sysconfig_build_setup_guard_line_facts(
        files, image_path_facts, sysconfig_name_facts,
        project_base_env_facts, no_site, no_project_base_override,
        direct_python312):
    """Bind the build-tree file probes to the exact image and worker assumptions."""
    source = files.get("sysconfig.py") if type(files) is dict else None
    expected_image_facts = {
        "executable_path_candidate": "/usr/local/bin/python3.12",
        "_PYTHON_BUILD": False,
        "setup_parent_paths_verified": True,
        "_pickle_extension": True,
    }
    if (type(source) is not bytes
            or hashlib.sha256(source).hexdigest() != SYSCONFIG_SOURCE_SHA256
            or type(image_path_facts) is not dict
            or any(image_path_facts.get(key) != value
                   for key, value in expected_image_facts.items())
            or type(sysconfig_name_facts) is not dict
            or sysconfig_name_facts.get("_sys_home") is not False
            or project_base_env_facts != (
                ("'_PYTHON_PROJECT_BASE' in os.environ", False),
            )
            or no_site is not True or no_project_base_override is not True
            or direct_python312 is not True):
        return {}
    try:
        tree = ast.parse(source, filename="sysconfig.py")
    except SyntaxError:
        return {}
    executable_guards = [node for node in tree.body
                         if isinstance(node, ast.If)
                         and ast.unparse(node.test) == "sys.executable"]
    project_assignments = [node for node in executable_guards[0].body
                           if isinstance(node, ast.Assign)
                           and any(isinstance(target, ast.Name)
                                   and target.id == "_PROJECT_BASE"
                                   for target in node.targets)] if len(executable_guards) == 1 else []
    if (len(executable_guards) != 1 or len(project_assignments) != 1
            or ast.unparse(project_assignments[0].value)
            != "os.path.dirname(_safe_realpath(sys.executable))"):
        return {}
    functions = [node for node in tree.body
                 if isinstance(node, ast.FunctionDef)
                 and node.name == "is_python_build"]
    if len(functions) != 1:
        return {}
    function = functions[0]
    loops = [node for node in function.body if isinstance(node, ast.For)]
    guards = [node for node in ast.walk(function)
              if isinstance(node, ast.If)
              and ast.unparse(node.test)
              == "os.path.isfile(os.path.join(_PROJECT_BASE, 'Modules', fn))"]
    final_false_returns = [node for node in function.body
                           if isinstance(node, ast.Return)
                           and isinstance(node.value, ast.Constant)
                           and node.value.value is False]
    if (len(loops) != 1 or ast.unparse(loops[0].iter)
            != "('Setup', 'Setup.local')"
            or len(guards) != 1
            or len(final_false_returns) != 1
            or not any(isinstance(node, ast.Return)
                       and isinstance(node.value, ast.Constant)
                       and node.value.value is True
                       for node in guards[0].body)):
        return {}
    return {guards[0].lineno: False}


def _target_sysconfig_venv_prefix_guard_line_facts(
        files, target_prefix_candidate):
    """Resolve the venv comparison only when candidate prefixes are identical."""
    source = files.get("sysconfig.py") if type(files) is dict else None
    expected_prefixes = {
        "values": ("/usr/local", "/usr/local", "/usr/local", "/usr/local"),
        "field_order": ("prefix", "exec_prefix", "base_prefix", "base_exec_prefix"),
        "runtime_prefixes_claimed": False,
    }
    if (type(source) is not bytes
            or hashlib.sha256(source).hexdigest() != SYSCONFIG_SOURCE_SHA256
            or type(target_prefix_candidate) is not dict
            or any(target_prefix_candidate.get(key) != value
                   for key, value in expected_prefixes.items())):
        return {}
    try:
        tree = ast.parse(source, filename="sysconfig.py")
    except SyntaxError:
        return {}
    functions = [node for node in tree.body if isinstance(node, ast.FunctionDef)
                 and node.name == "get_preferred_scheme"]
    if len(functions) != 1:
        return {}
    guards = [node for node in ast.walk(functions[0])
              if isinstance(node, ast.If)
              and ast.unparse(node.test)
              == "key == 'prefix' and sys.prefix != sys.base_prefix"]
    if len(guards) != 1:
        return {}
    return {guards[0].lineno: False}


def _target_sysconfig_preferred_scheme_membership_line_facts(
        files, sysconfig_name_facts):
    """Resolve preferred-scheme membership from literal mappings and target facts."""
    source = files.get("sysconfig.py") if type(files) is dict else None
    if (type(source) is not bytes
            or hashlib.sha256(source).hexdigest() != SYSCONFIG_SOURCE_SHA256
            or type(sysconfig_name_facts) is not dict
            or sysconfig_name_facts.get("_HAS_USER_BASE") is not True):
        return {}
    try:
        tree = ast.parse(source, filename="sysconfig.py")
    except SyntaxError:
        return {}
    initial = [node.value for node in tree.body if isinstance(node, ast.Assign)
               and any(isinstance(target, ast.Name)
                       and target.id == "_INSTALL_SCHEMES"
                       for target in node.targets)]
    if len(initial) != 1:
        return {}
    try:
        scheme_names = set(ast.literal_eval(initial[0]))
    except (ValueError, TypeError):
        return {}
    updates = [node for node in ast.walk(tree)
               if isinstance(node, ast.AugAssign)
               and isinstance(node.target, ast.Name)
               and node.target.id == "_INSTALL_SCHEMES"
               and isinstance(node.op, ast.BitOr)]
    update_guards = [node for node in tree.body if isinstance(node, ast.If)
                     and ast.unparse(node.test) == "_HAS_USER_BASE"]
    if len(updates) != 1 or len(update_guards) != 1 or updates[0] not in ast.walk(update_guards[0]):
        return {}
    try:
        scheme_names.update(ast.literal_eval(updates[0].value))
    except (ValueError, TypeError):
        return {}
    preferred_functions = [node for node in tree.body
                           if isinstance(node, ast.FunctionDef)
                           and node.name == "_get_preferred_schemes"]
    public_functions = [node for node in tree.body
                        if isinstance(node, ast.FunctionDef)
                        and node.name == "get_preferred_scheme"]
    if len(preferred_functions) != 1 or len(public_functions) != 1:
        return {}
    preferred_values = []
    for node in ast.walk(preferred_functions[0]):
        if isinstance(node, ast.Return):
            try:
                value = ast.literal_eval(node.value)
            except (ValueError, TypeError):
                return {}
            if type(value) is not dict or any(type(item) is not str for item in value.values()):
                return {}
            preferred_values.extend(value.values())
    guards = [node for node in ast.walk(public_functions[0])
              if isinstance(node, ast.If)
              and ast.unparse(node.test) == "scheme not in _INSTALL_SCHEMES"]
    if (not preferred_values or not set(preferred_values).issubset(scheme_names)
            or len(guards) != 1):
        return {}
    return {guards[0].lineno: False}


def _target_sysconfig_posix_init_line_facts(files, os_name_call_facts):
    """Select sysconfig's POSIX initializer only from the bound os.name fact."""
    source = files.get("sysconfig.py") if type(files) is dict else None
    if (type(source) is not bytes
            or hashlib.sha256(source).hexdigest() != SYSCONFIG_SOURCE_SHA256
            or os_name_call_facts != (("os.name", "posix"),)):
        return {}
    try:
        tree = ast.parse(source, filename="sysconfig.py")
    except SyntaxError:
        return {}
    initializers = [node for node in tree.body
                    if isinstance(node, ast.FunctionDef)
                    and node.name == "_init_config_vars"]
    if len(initializers) != 1:
        return {}
    guards = [node for node in initializers[0].body
              if isinstance(node, ast.If)
              and ast.unparse(node.test) == "os.name == 'posix'"
              and not node.orelse and len(node.body) == 1
              and isinstance(node.body[0], ast.Expr)
              and isinstance(node.body[0].value, ast.Call)
              and ast.unparse(node.body[0].value) == "_init_posix(_CONFIG_VARS)"]
    if len(guards) != 1:
        return {}
    return {guards[0].lineno: True}


def _target_sysconfig_lazy_initialization_call_candidate(files):
    """Bind get_config_vars' first-call guard to its initializer edge."""
    source = files.get("sysconfig.py") if type(files) is dict else None
    if (type(source) is not bytes
            or hashlib.sha256(source).hexdigest() != SYSCONFIG_SOURCE_SHA256):
        return None
    try:
        tree = ast.parse(source, filename="sysconfig.py")
    except SyntaxError:
        return None

    initial_values = {}
    for node in tree.body:
        if (not isinstance(node, ast.Assign) or len(node.targets) != 1
                or not isinstance(node.targets[0], ast.Name)
                or node.targets[0].id not in {
                    "_CONFIG_VARS", "_CONFIG_VARS_INITIALIZED",
                }):
            continue
        name = node.targets[0].id
        if name in initial_values:
            return None
        try:
            initial_values[name] = ast.literal_eval(node.value)
        except (ValueError, TypeError, SyntaxError):
            return None
    if initial_values != {
            "_CONFIG_VARS": None,
            "_CONFIG_VARS_INITIALIZED": False,
    }:
        return None

    getters = [node for node in tree.body
               if isinstance(node, ast.FunctionDef)
               and node.name == "get_config_vars"]
    if len(getters) != 1:
        return None
    global_declarations = [node for node in getters[0].body
                          if isinstance(node, ast.Global)
                          and "_CONFIG_VARS_INITIALIZED" in node.names]
    if (len(global_declarations) != 1
            or global_declarations[0].names != ["_CONFIG_VARS_INITIALIZED"]):
        return None
    outer_guards = [node for node in getters[0].body
                    if isinstance(node, ast.If)
                    and ast.unparse(node.test) == "not _CONFIG_VARS_INITIALIZED"]
    if (len(outer_guards) != 1 or len(outer_guards[0].body) != 1
            or getters[0].body.index(global_declarations[0])
            > getters[0].body.index(outer_guards[0])):
        return None
    lock_blocks = outer_guards[0].body
    if not isinstance(lock_blocks[0], ast.With) or len(lock_blocks[0].items) != 1:
        return None
    lock = lock_blocks[0].items[0]
    if (ast.unparse(lock.context_expr) != "_CONFIG_VARS_LOCK"
            or lock.optional_vars is not None or len(lock_blocks[0].body) != 1
            or not isinstance(lock_blocks[0].body[0], ast.If)):
        return None
    config_vars_guard = lock_blocks[0].body[0]
    if (ast.unparse(config_vars_guard.test) != "_CONFIG_VARS is None"
            or config_vars_guard.orelse or len(config_vars_guard.body) != 1
            or not isinstance(config_vars_guard.body[0], ast.Expr)
            or not isinstance(config_vars_guard.body[0].value, ast.Call)
            or ast.unparse(config_vars_guard.body[0].value) != "_init_config_vars()"):
        return None
    return {
        "getter": "get_config_vars",
        "initial_config_vars": None,
        "initialization_flag": False,
        "outer_guard": "not _CONFIG_VARS_INITIALIZED",
        "lock": "_CONFIG_VARS_LOCK",
        "recheck_guard": "_CONFIG_VARS is None",
        "selected_call": "_init_config_vars()",
        "evidence_scope": "STATIC_LAZY_INITIALIZER_CALL_CANDIDATE",
    }


def _target_sysconfig_reinitialization_candidate(files):
    """Bind the guarded sysconfig reinitialization branch without evaluating it."""
    source = files.get("sysconfig.py") if type(files) is dict else None
    if (type(source) is not bytes
            or hashlib.sha256(source).hexdigest() != SYSCONFIG_SOURCE_SHA256
            or _target_sysconfig_lazy_initialization_call_candidate(files) is None):
        return None
    try:
        tree = ast.parse(source, filename="sysconfig.py")
    except SyntaxError:
        return None
    getters = [node for node in tree.body
               if isinstance(node, ast.FunctionDef)
               and node.name == "get_config_vars"]
    if len(getters) != 1:
        return None
    guards = [node for node in ast.walk(getters[0])
              if isinstance(node, ast.If)
              and ast.unparse(node.test) == "not _CONFIG_VARS_INITIALIZED"]
    if len(guards) != 1:
        return None
    expected = ast.parse(
        "if not _CONFIG_VARS_INITIALIZED:\n"
        "    with _CONFIG_VARS_LOCK:\n"
        "        if _CONFIG_VARS is None:\n"
        "            _init_config_vars()\n"
        "elif _CONFIG_VARS['base'] != os.path.normpath(sys.prefix):\n"
        "    with _CONFIG_VARS_LOCK:\n"
        "        _CONFIG_VARS_INITIALIZED = False\n"
        "        _init_config_vars()\n"
    ).body[0]
    if ast.dump(guards[0], include_attributes=False) != ast.dump(
            expected, include_attributes=False):
        return None
    return {
        "getter": "get_config_vars",
        "initialization_flag_initial_value": False,
        "first_call_guard": "not _CONFIG_VARS_INITIALIZED",
        "reinitialization_guard": (
            "_CONFIG_VARS['base'] != os.path.normpath(sys.prefix)"
        ),
        "reinitialization_guard_is_runtime_dependent": True,
        "lock": "_CONFIG_VARS_LOCK",
        "actions_if_reinitialization_guard_true": [
            "_CONFIG_VARS_INITIALIZED = False",
            "_init_config_vars()",
        ],
        "evidence_scope": "STATIC_CONFIG_REINITIALIZATION_CANDIDATE",
    }


def _target_sysconfig_public_config_value_flow_candidate(files):
    """Bind sysconfig's public configuration-value return forms."""
    source = files.get("sysconfig.py") if type(files) is dict else None
    if (type(source) is not bytes
            or hashlib.sha256(source).hexdigest() != SYSCONFIG_SOURCE_SHA256):
        return None
    try:
        tree = ast.parse(source, filename="sysconfig.py")
    except SyntaxError:
        return None
    functions = {
        node.name: node for node in tree.body
        if isinstance(node, ast.FunctionDef)
    }
    if (len([node for node in tree.body
             if isinstance(node, ast.FunctionDef)
             and node.name == "get_config_vars"]) != 1
            or len([node for node in tree.body
                    if isinstance(node, ast.FunctionDef)
                    and node.name == "get_config_var"]) != 1):
        return None

    get_config_vars = functions.get("get_config_vars")
    get_config_var = functions.get("get_config_var")
    if get_config_vars is None or get_config_var is None:
        return None
    getter_body = list(get_config_vars.body)
    if (getter_body and isinstance(getter_body[0], ast.Expr)
            and isinstance(getter_body[0].value, ast.Constant)
            and type(getter_body[0].value.value) is str):
        getter_body.pop(0)
    wrapper_body = list(get_config_var.body)
    if (wrapper_body and isinstance(wrapper_body[0], ast.Expr)
            and isinstance(wrapper_body[0].value, ast.Constant)
            and type(wrapper_body[0].value.value) is str):
        wrapper_body.pop(0)
    expected_return_block = ast.parse(
        "def get_config_vars(*args):\n"
        "    if args:\n"
        "        vals = []\n"
        "        for name in args:\n"
        "            vals.append(_CONFIG_VARS.get(name))\n"
        "        return vals\n"
        "    else:\n"
        "        return _CONFIG_VARS\n"
    ).body[0].body[0]
    if (not getter_body or not isinstance(getter_body[-1], ast.If)
            or ast.dump(getter_body[-1], include_attributes=False)
            != ast.dump(expected_return_block, include_attributes=False)):
        return None
    expected_wrapper = ast.parse(
        "def get_config_var(name):\n"
        "    return get_config_vars().get(name)\n"
    ).body[0]
    if (len(get_config_var.args.args) != 1
            or get_config_var.args.args[0].arg != "name"
            or len(wrapper_body) != 1
            or ast.dump(wrapper_body[0], include_attributes=False)
            != ast.dump(expected_wrapper.body[0], include_attributes=False)):
        return None
    return {
        "public_mapping_api": "get_config_vars",
        "no_arguments_return": "_CONFIG_VARS",
        "arguments_return": "[_CONFIG_VARS.get(name) for name in args]",
        "single_value_api": "get_config_var",
        "single_value_return": "get_config_vars().get(name)",
        "evidence_scope": "STATIC_CONFIG_API_VALUE_FLOW_CANDIDATE",
    }


def _target_sysconfig_post_update_entries_candidate(
        files, posix_init_line_facts, sys_platform_facts, image_facts):
    """Bind known sysconfigdata keys to the post-update initializer state."""
    source = files.get("sysconfig.py") if type(files) is dict else None
    if (type(source) is not bytes
            or hashlib.sha256(source).hexdigest() != SYSCONFIG_SOURCE_SHA256
            or type(posix_init_line_facts) is not dict
            or len(posix_init_line_facts) != 1
            or any(type(line) is not int or value is not True
                   for line, value in posix_init_line_facts.items())
            or sys_platform_facts != (("sys.platform", "linux"),)
            or type(image_facts) is not dict
            or image_facts.get("sysconfigdata_path") != TARGET_SYSCONFIGDATA_PATH
            or image_facts.get("sysconfigdata_sha256")
            != TARGET_SYSCONFIGDATA_SHA256
            or image_facts.get("machdep") != "linux"
            or any(image_facts.get(TARGET_SYSCONFIGDATA_FACT_FIELDS[key]) != value
                   for key, value in TARGET_SYSCONFIGDATA_EXPECTED_VALUES.items())):
        return None
    try:
        tree = ast.parse(source, filename="sysconfig.py")
    except SyntaxError:
        return None
    initializers = [node for node in tree.body
                    if isinstance(node, ast.FunctionDef)
                    and node.name == "_init_config_vars"]
    if len(initializers) != 1:
        return None
    initializer = initializers[0]
    selected_line = next(iter(posix_init_line_facts))
    selected_guards = [node for node in ast.walk(initializer)
                       if isinstance(node, ast.If)
                       and node.lineno == selected_line
                       and ast.unparse(node.test) == "os.name == 'posix'"
                       and len(node.body) == 1
                       and isinstance(node.body[0], ast.Expr)
                       and isinstance(node.body[0].value, ast.Call)
                       and ast.unparse(node.body[0].value)
                       == "_init_posix(_CONFIG_VARS)"]
    if len(selected_guards) != 1:
        return None
    selected_call_line = selected_guards[0].body[0].value.lineno

    written_keys = set()
    for node in ast.walk(initializer):
        if not isinstance(node, (ast.Assign, ast.AnnAssign, ast.AugAssign)):
            continue
        if node.lineno <= selected_call_line:
            continue
        targets = node.targets if isinstance(node, ast.Assign) else [node.target]
        for target in targets:
            for child in ast.walk(target):
                if (isinstance(child, ast.Subscript)
                        and isinstance(child.value, ast.Name)
                        and child.value.id == "_CONFIG_VARS"
                        and isinstance(child.slice, ast.Constant)
                        and type(child.slice.value) is str):
                    written_keys.add(child.slice.value)
    if written_keys.intersection(TARGET_SYSCONFIGDATA_EXPECTED_VALUES):
        return None
    later_mapping_methods = [node for node in ast.walk(initializer)
                             if isinstance(node, ast.Call)
                             and getattr(node, "lineno", -1) > selected_call_line
                             and isinstance(node.func, ast.Attribute)
                             and isinstance(node.func.value, ast.Name)
                             and node.func.value.id == "_CONFIG_VARS"
                             and ast.unparse(node)
                             != "_CONFIG_VARS.get('srcdir', _PROJECT_BASE)"]
    def target_rebinds_config_vars(target):
        if isinstance(target, ast.Name):
            return target.id == "_CONFIG_VARS"
        if isinstance(target, (ast.Tuple, ast.List)):
            return any(target_rebinds_config_vars(element) for element in target.elts)
        return False

    later_mapping_rebindings = [node for node in ast.walk(initializer)
                                if getattr(node, "lineno", -1) > selected_call_line
                                and isinstance(node, (ast.Assign, ast.AnnAssign,
                                                     ast.AugAssign, ast.Delete))
                                and any(target_rebinds_config_vars(target)
                                        for target in (
                                            node.targets if isinstance(node, (ast.Assign,
                                                                              ast.Delete))
                                            else [node.target]
                                        ))]
    if later_mapping_methods or later_mapping_rebindings:
        return None

    darwin_guards = [node for node in ast.walk(initializer)
                     if isinstance(node, ast.If)
                     and ast.unparse(node.test) == "sys.platform == 'darwin'"]
    if (len(darwin_guards) != 1 or darwin_guards[0].orelse
            or darwin_guards[0].lineno <= selected_call_line
            or len(darwin_guards[0].body) != 2
            or not isinstance(darwin_guards[0].body[0], ast.Import)
            or ast.unparse(darwin_guards[0].body[1])
            != "_osx_support.customize_config_vars(_CONFIG_VARS)"):
        return None
    later_mapping_calls = [node for node in ast.walk(initializer)
                           if isinstance(node, ast.Call)
                           and node.lineno > selected_call_line
                           and any(isinstance(argument, ast.Name)
                                   and argument.id == "_CONFIG_VARS"
                                   for argument in node.args)]
    if (len(later_mapping_calls) != 1
            or ast.unparse(later_mapping_calls[0])
            != "_osx_support.customize_config_vars(_CONFIG_VARS)"):
        return None
    return {
        "mapping": "_CONFIG_VARS",
        "post_update_direct_overwrites": [],
        "post_update_customizer": "_osx_support.customize_config_vars",
        "customizer_guard": "sys.platform == 'darwin'",
        "customizer_selected": False,
        "entry_values": {
            key: image_facts[TARGET_SYSCONFIGDATA_FACT_FIELDS[key]]
            for key in TARGET_SYSCONFIGDATA_EXPECTED_VALUES
        },
        "evidence_scope": "STATIC_POST_INIT_MAPPING_ENTRY_CANDIDATE",
    }


def _target_sysconfig_initialization_complete_flag_candidate(
        files, posix_init_line_facts):
    """Bind the config-initialized flag assignment to initializer completion."""
    source = files.get("sysconfig.py") if type(files) is dict else None
    if (type(source) is not bytes
            or hashlib.sha256(source).hexdigest() != SYSCONFIG_SOURCE_SHA256
            or type(posix_init_line_facts) is not dict
            or len(posix_init_line_facts) != 1
            or any(type(line) is not int or value is not True
                   for line, value in posix_init_line_facts.items())):
        return None
    try:
        tree = ast.parse(source, filename="sysconfig.py")
    except SyntaxError:
        return None
    initializers = [node for node in tree.body
                    if isinstance(node, ast.FunctionDef)
                    and node.name == "_init_config_vars"]
    if len(initializers) != 1:
        return None
    body = initializers[0].body
    if (len(body) < 3 or not isinstance(body[-2], ast.Global)
            or body[-2].names != ["_CONFIG_VARS_INITIALIZED"]
            or not isinstance(body[-1], ast.Assign)
            or len(body[-1].targets) != 1
            or not isinstance(body[-1].targets[0], ast.Name)
            or body[-1].targets[0].id != "_CONFIG_VARS_INITIALIZED"
            or not isinstance(body[-1].value, ast.Constant)
            or body[-1].value.value is not True):
        return None
    selected_line = next(iter(posix_init_line_facts))
    selected_guards = [node for node in ast.walk(initializers[0])
                       if isinstance(node, ast.If)
                       and node.lineno == selected_line
                       and ast.unparse(node.test) == "os.name == 'posix'"
                       and len(node.body) == 1
                       and isinstance(node.body[0], ast.Expr)
                       and isinstance(node.body[0].value, ast.Call)
                       and ast.unparse(node.body[0].value)
                       == "_init_posix(_CONFIG_VARS)"]
    if (len(selected_guards) != 1
            or selected_guards[0].body[0].value.lineno >= body[-1].lineno):
        return None
    return {
        "initializer": "sysconfig._init_config_vars",
        "flag": "_CONFIG_VARS_INITIALIZED",
        "initial_value": False,
        "completion_assignment": "_CONFIG_VARS_INITIALIZED = True",
        "assignment_is_final_statement": True,
        "evidence_scope": "STATIC_CONFIG_INITIALIZED_FLAG_CANDIDATE",
    }


def _target_sysconfig_project_base_env_facts(files, image_config_source,
                                             no_project_base_override):
    """Bind the direct os.environ guard to the pinned image ENV and call assumption."""
    source = files.get("sysconfig.py")
    if (no_project_base_override is not True
            or type(source) is not bytes
            or hashlib.sha256(source).hexdigest() != SYSCONFIG_SOURCE_SHA256
            or type(image_config_source) is not bytes
            or len(image_config_source) > MAX_TARGET_IMAGE_CONFIG_BYTES
            or hashlib.sha256(image_config_source).hexdigest()
            != TARGET_IMAGE_CONFIG_SHA256):
        return ()
    tree = ast.parse(source, filename="sysconfig.py")
    guards = [node for node in tree.body if isinstance(node, ast.If)
              and ast.unparse(node.test)
              == "'_PYTHON_PROJECT_BASE' in os.environ"]
    if len(guards) != 1:
        return ()
    config = json.loads(image_config_source)
    if (type(config) is not dict or config.get("os") != "linux"
            or config.get("architecture") != "amd64"):
        return ()
    runtime_config = config.get("config")
    env = runtime_config.get("Env") if type(runtime_config) is dict else None
    if (type(env) is not list or any(type(item) is not str for item in env)
            or any(item.partition("=")[0] == "_PYTHON_PROJECT_BASE" for item in env)):
        return ()
    return (("'_PYTHON_PROJECT_BASE' in os.environ", False),)


def _target_sysconfig_userbase_env_condition_facts(
        files, image_config_source, no_site, no_pythonuserbase_override):
    """Resolve PYTHONUSERBASE lookup only under the explicit clean-env assumption."""
    source = files.get("sysconfig.py") if type(files) is dict else None
    if (no_site is not True or no_pythonuserbase_override is not True
            or type(source) is not bytes
            or hashlib.sha256(source).hexdigest() != SYSCONFIG_SOURCE_SHA256
            or type(image_config_source) is not bytes
            or len(image_config_source) > MAX_TARGET_IMAGE_CONFIG_BYTES
            or hashlib.sha256(image_config_source).hexdigest()
            != TARGET_IMAGE_CONFIG_SHA256):
        return {}
    try:
        tree = ast.parse(source, filename="sysconfig.py")
        config = json.loads(image_config_source)
    except (SyntaxError, json.JSONDecodeError):
        return {}
    runtime_config = config.get("config") if type(config) is dict else None
    env = runtime_config.get("Env") if type(runtime_config) is dict else None
    if (type(config) is not dict or config.get("os") != "linux"
            or config.get("architecture") != "amd64"
            or type(env) is not list or any(type(item) is not str for item in env)
            or any(item.partition("=")[0] == "PYTHONUSERBASE" for item in env)):
        return {}
    if any(
            name not in ("site.py", "sysconfig.py")
            and "test" not in name.split("/")
            and b"PYTHONUSERBASE" in data
            for name, data in files.items() if type(data) is bytes):
        return {}
    functions = [node for node in tree.body if isinstance(node, ast.FunctionDef)
                 and node.name == "_getuserbase"]
    if len(functions) != 1:
        return {}
    function = functions[0]
    env_reads = [node for node in ast.walk(function)
                 if isinstance(node, ast.Call)
                 and ast.unparse(node) == "os.environ.get('PYTHONUSERBASE', None)"]
    guards = [node for node in ast.walk(function)
              if isinstance(node, ast.If) and ast.unparse(node.test) == "env_base"]
    module_init = [node for node in tree.body if isinstance(node, ast.Assign)
                   and any(isinstance(target, ast.Name)
                           and target.id == "_HAS_USER_BASE"
                           for target in node.targets)]
    if (len(env_reads) != 1 or len(guards) != 1 or len(module_init) != 1
            or ast.unparse(module_init[0].value)
            != "_getuserbase() is not None"):
        return {}
    return {("sysconfig", "sysconfig.py", guards[0].lineno): (False,)}


class _DigestReader:
    """Hash a sequential tar stream without buffering the image layer."""

    def __init__(self, source):
        self.source = source
        self.digest = hashlib.sha256()

    def read(self, size=-1):
        data = self.source.read(size)
        self.digest.update(data)
        return data


def _target_image_save_facts(image_save_path, image_config_source):
    """Verify the pinned Docker-save layers and inspect the final executable paths."""
    if image_config_source is None:
        raise ValueError("TARGET_IMAGE_CONFIG_REQUIRED")
    path = Path(image_save_path)
    if path.stat().st_size > MAX_TARGET_IMAGE_SAVE_BYTES:
        raise ValueError("TARGET_IMAGE_SAVE_LIMIT")
    try:
        with tarfile.open(path, "r:") as outer:
            manifest_info = outer.getmember("manifest.json")
            if manifest_info.size > MAX_TARGET_IMAGE_CONFIG_BYTES:
                raise ValueError("TARGET_IMAGE_SAVE_MANIFEST_LIMIT")
            manifest_member = outer.extractfile(manifest_info)
            manifest_bytes = manifest_member.read(MAX_TARGET_IMAGE_CONFIG_BYTES + 1)
            manifest = json.loads(manifest_bytes)
            if (type(manifest) is not list or len(manifest) != 1
                    or type(manifest[0]) is not dict):
                raise ValueError("TARGET_IMAGE_SAVE_MANIFEST")
            entry = manifest[0]
            config_name = entry.get("Config")
            layers = entry.get("Layers")
            if (config_name != "blobs/sha256/" + TARGET_IMAGE_CONFIG_SHA256
                    or type(layers) is not list or len(layers) != len(TARGET_IMAGE_LAYER_NAMES)
                    or any(layer != "blobs/sha256/" + digest
                           for layer, digest in zip(layers, TARGET_IMAGE_LAYER_NAMES))):
                raise ValueError("TARGET_IMAGE_SAVE_BINDING")
            index_info = outer.getmember("index.json")
            if index_info.size > MAX_TARGET_IMAGE_CONFIG_BYTES:
                raise ValueError("TARGET_IMAGE_SAVE_INDEX_LIMIT")
            index = json.loads(outer.extractfile(index_info).read(
                MAX_TARGET_IMAGE_CONFIG_BYTES + 1
            ))
            descriptors = index.get("manifests") if type(index) is dict else None
            expected_manifest_digest = "sha256:" + TARGET_IMAGE_MANIFEST_SHA256
            if (type(descriptors) is not list or len(descriptors) != 1
                    or type(descriptors[0]) is not dict
                    or descriptors[0].get("digest") != expected_manifest_digest):
                raise ValueError("TARGET_IMAGE_SAVE_INDEX_BINDING")
            image_manifest_name = "blobs/sha256/" + TARGET_IMAGE_MANIFEST_SHA256
            image_manifest_info = outer.getmember(image_manifest_name)
            if (image_manifest_info.size > MAX_TARGET_IMAGE_CONFIG_BYTES * 4
                    or image_manifest_info.size != descriptors[0].get("size")):
                raise ValueError("TARGET_IMAGE_SAVE_MANIFEST_LIMIT")
            image_manifest_bytes = outer.extractfile(image_manifest_info).read(
                MAX_TARGET_IMAGE_CONFIG_BYTES * 4 + 1
            )
            if hashlib.sha256(image_manifest_bytes).hexdigest() != TARGET_IMAGE_MANIFEST_SHA256:
                raise ValueError("TARGET_IMAGE_SAVE_MANIFEST_DIGEST")
            image_manifest = json.loads(image_manifest_bytes)
            config_descriptor = image_manifest.get("config")
            layer_descriptors = image_manifest.get("layers")
            if (type(config_descriptor) is not dict
                    or config_descriptor.get("digest")
                    != "sha256:" + TARGET_IMAGE_CONFIG_SHA256
                    or type(layer_descriptors) is not list
                    or len(layer_descriptors) != len(TARGET_IMAGE_LAYER_NAMES)
                    or any(type(descriptor) is not dict
                           or descriptor.get("digest") != "sha256:" + expected
                           or descriptor.get("mediaType")
                           != "application/vnd.oci.image.layer.v1.tar+gzip"
                           or descriptor.get("size") != outer.getmember(layer_name).size
                           for descriptor, expected, layer_name in zip(
                               layer_descriptors, TARGET_IMAGE_LAYER_NAMES, layers
                           ))):
                raise ValueError("TARGET_IMAGE_SAVE_OCI_MANIFEST_BINDING")
            config_info = outer.getmember(config_name)
            if config_info.size > MAX_TARGET_IMAGE_CONFIG_BYTES:
                raise ValueError("TARGET_IMAGE_SAVE_CONFIG_LIMIT")
            config_member = outer.extractfile(config_info)
            config_bytes = config_member.read(MAX_TARGET_IMAGE_CONFIG_BYTES + 1)
            if (len(config_bytes) > MAX_TARGET_IMAGE_CONFIG_BYTES
                    or hashlib.sha256(config_bytes).hexdigest() != TARGET_IMAGE_CONFIG_SHA256
                    or config_bytes != image_config_source):
                raise ValueError("TARGET_IMAGE_SAVE_CONFIG_MISMATCH")
            config = json.loads(config_bytes)
            rootfs = config.get("rootfs") if type(config) is dict else None
            diff_ids = rootfs.get("diff_ids") if type(rootfs) is dict else None
            if (type(diff_ids) is not list or len(diff_ids) != len(layers)
                    or any(type(item) is not str or not re.fullmatch(r"sha256:[0-9a-f]{64}", item)
                           for item in diff_ids)):
                raise ValueError("TARGET_IMAGE_SAVE_DIFF_IDS")

            tracked = {
                "usr": None,
                "usr/local": None,
                "usr/local/bin": None,
                "usr/local/bin/Modules": None,
                TARGET_EXECUTABLE_PATH: None,
                TARGET_SYSCONFIGDATA_PATH: None,
                TARGET_INERT_ZIP_PATH: None,
                TARGET_PREFIX_STDLIB_LANDMARK: None,
                TARGET_EXEC_PREFIX_LANDMARK: None,
                **{path: None for path in TARGET_PREFIX_PARENT_DIRECTORIES},
                **{path: None for path in TARGET_PREFIX_VENV_MARKERS},
                TARGET_BUILD_MARKER: None,
                **{path: None for path in TARGET_PTH_OVERRIDE_PATHS},
                PICKLE_EXTENSION_PATH: None,
                **{path: None for path in HASHLIB_EXTENSION_FACTS},
                "usr/local/bin/python3": None,
                "usr/local/bin/Modules/Setup": None,
                "usr/local/bin/Modules/Setup.local": None,
            }
            for layer_name, expected_diff_id in zip(layers, diff_ids):
                compressed_reader = _DigestReader(outer.extractfile(layer_name))
                uncompressed_reader = _DigestReader(gzip.GzipFile(fileobj=compressed_reader))
                whiteouts = []
                additions = []
                with tarfile.open(fileobj=uncompressed_reader, mode="r|") as layer:
                    for member in layer:
                        name = member.name.lstrip("./").rstrip("/")
                        if not name:
                            continue
                        parent, _, basename = name.rpartition("/")
                        if basename == ".wh..wh..opq":
                            whiteouts.append((parent, True))
                        elif basename.startswith(".wh."):
                            whiteouts.append((parent + "/" + basename[4:], False))
                        elif name in tracked:
                            content_sha256 = None
                            content_bytes = None
                            if member.isfile() and name in (
                                    TARGET_EXECUTABLE_PATH, PICKLE_EXTENSION_PATH,
                                    *HASHLIB_EXTENSION_FACTS,
                                    TARGET_SYSCONFIGDATA_PATH,
                                    TARGET_PREFIX_STDLIB_LANDMARK):
                                if (name in (TARGET_EXECUTABLE_PATH, PICKLE_EXTENSION_PATH,
                                             *HASHLIB_EXTENSION_FACTS)
                                        and member.size > MAX_S15_FILE_BYTES):
                                    raise ValueError("TARGET_IMAGE_FILE_FINGERPRINT_LIMIT")
                                if (name == TARGET_SYSCONFIGDATA_PATH
                                        and member.size > MAX_TARGET_SYSCONFIGDATA_BYTES):
                                    raise ValueError("TARGET_SYSCONFIGDATA_LIMIT")
                                stream = layer.extractfile(member)
                                content_digest = hashlib.sha256()
                                content_parts = []
                                content_size = 0
                                while True:
                                    chunk = stream.read(1024 * 1024)
                                    if not chunk:
                                        break
                                    content_digest.update(chunk)
                                    if name == TARGET_SYSCONFIGDATA_PATH:
                                        content_size += len(chunk)
                                        if content_size > MAX_TARGET_SYSCONFIGDATA_BYTES:
                                            raise ValueError("TARGET_SYSCONFIGDATA_LIMIT")
                                        content_parts.append(chunk)
                                content_sha256 = content_digest.hexdigest()
                                if name == TARGET_SYSCONFIGDATA_PATH:
                                    content_bytes = b"".join(content_parts)
                            facts = {
                                "file": member.isfile(), "directory": member.isdir(),
                                "symlink": member.issym(),
                                "linkname": member.linkname if member.issym() else None,
                                "mode": member.mode & 0o777,
                                "sha256": content_sha256,
                            }
                            if name in (TARGET_EXECUTABLE_PATH, PICKLE_EXTENSION_PATH,
                                        *HASHLIB_EXTENSION_FACTS):
                                facts["size"] = member.size
                            if name == TARGET_SYSCONFIGDATA_PATH:
                                facts["content"] = content_bytes
                            additions.append((name, facts))
                if ("sha256:" + compressed_reader.digest.hexdigest()
                        != "sha256:" + layer_name.rsplit("/", 1)[-1]
                        or "sha256:" + uncompressed_reader.digest.hexdigest()
                        != expected_diff_id):
                    raise ValueError("TARGET_IMAGE_SAVE_LAYER_DIFF_ID")
                for target in tracked:
                    parts = target.split("/")
                    ancestors = ["/".join(parts[:index]) for index in range(1, len(parts))]
                    removed = False
                    for parent, opaque in whiteouts:
                        if (opaque and parent in ancestors
                                or not opaque and (parent == target
                                    or target.startswith(parent + "/"))):
                            removed = True
                            break
                    if removed:
                        tracked[target] = None
                for name, facts in additions:
                    tracked[name] = facts
            if not _target_image_setup_paths_safe(tracked):
                raise ValueError("TARGET_IMAGE_SAVE_SETUP_PATHS")
            executable = tracked[TARGET_EXECUTABLE_PATH]
            executable_shape = {
                "file": True, "directory": False, "symlink": False,
                "linkname": None, "mode": 0o755,
                "sha256": TARGET_EXECUTABLE_SHA256,
            }
            if (type(executable) is not dict
                    or any(executable.get(key) != value
                           for key, value in executable_shape.items())
                    or type(executable.get("size")) is not int
                    or not 0 <= executable["size"] <= MAX_S15_FILE_BYTES
                    or tracked["usr/local/bin/python3"] != {
                        "file": False, "directory": False, "symlink": True,
                        "linkname": "python3.12",
                        "mode": 0o777, "sha256": None,
                    }
                    or tracked["usr/local/bin/Modules/Setup"] is not None
                    or tracked["usr/local/bin/Modules/Setup.local"] is not None):
                raise ValueError("TARGET_IMAGE_SAVE_PATH_FACTS")
            pickle_extension = tracked[PICKLE_EXTENSION_PATH]
            pickle_shape = {
                "file": True, "directory": False, "symlink": False,
                "linkname": None, "mode": 0o755,
                "sha256": PICKLE_EXTENSION_SHA256,
            }
            if (type(pickle_extension) is not dict
                    or any(pickle_extension.get(key) != value
                           for key, value in pickle_shape.items())
                    or type(pickle_extension.get("size")) is not int
                    or not 0 <= pickle_extension["size"] <= MAX_S15_FILE_BYTES
                    or executable["size"] + pickle_extension["size"]
                    > MAX_S15_FILE_TOTAL_BYTES):
                raise ValueError("TARGET_IMAGE_PICKLE_EXTENSION_FACT")
            hashlib_extension_facts = {}
            hashlib_extension_total = 0
            for extension_path, expected_sha256 in HASHLIB_EXTENSION_FACTS.items():
                extension = tracked[extension_path]
                extension_shape = {
                    "file": True, "directory": False, "symlink": False,
                    "linkname": None, "mode": 0o755, "sha256": expected_sha256,
                }
                if (type(extension) is not dict
                        or any(extension.get(key) != value
                               for key, value in extension_shape.items())
                        or type(extension.get("size")) is not int
                        or not 0 <= extension["size"] <= MAX_S15_FILE_BYTES):
                    raise ValueError("TARGET_IMAGE_HASHLIB_EXTENSION_FACT")
                hashlib_extension_total += extension["size"]
                if hashlib_extension_total > MAX_S15_FILE_TOTAL_BYTES:
                    raise ValueError("TARGET_IMAGE_HASHLIB_EXTENSION_TOTAL_LIMIT")
                hashlib_extension_facts[extension_path] = {
                    "sha256": expected_sha256, "size": extension["size"],
                }
            sysconfigdata = tracked[TARGET_SYSCONFIGDATA_PATH]
            if (type(sysconfigdata) is not dict or sysconfigdata.get("file") is not True
                    or sysconfigdata.get("symlink") is not False
                    or sysconfigdata.get("mode") != 0o644
                    or sysconfigdata.get("sha256") != TARGET_SYSCONFIGDATA_SHA256
                    or type(sysconfigdata.get("content")) is not bytes):
                raise ValueError("TARGET_IMAGE_SYSCONFIGDATA_FACT")
            sysconfig_facts = _target_image_sysconfigdata_facts(
                sysconfigdata["content"]
            )
            inert_zip_fact = _target_image_inert_zip_fact(tracked)
            prefix_landmark_facts = _target_image_prefix_landmark_facts(tracked)
            pth_override_facts = _target_image_pth_override_facts(tracked)
    except (tarfile.TarError, KeyError, TypeError, json.JSONDecodeError) as error:
        raise ValueError("TARGET_IMAGE_SAVE_INVALID") from error
    return {
        "executable_path_candidate": "/usr/local/bin/python3.12",
        "executable_sha256": executable["sha256"],
        "executable_size": executable["size"],
        "python3_symlink_target": tracked["usr/local/bin/python3"]["linkname"],
        "pickle_extension_sha256": tracked[PICKLE_EXTENSION_PATH]["sha256"],
        "pickle_extension_size": tracked[PICKLE_EXTENSION_PATH]["size"],
        "hashlib_extension_facts": hashlib_extension_facts,
        "sysconfigdata_path": TARGET_SYSCONFIGDATA_PATH,
        "sysconfigdata_sha256": TARGET_SYSCONFIGDATA_SHA256,
        **sysconfig_facts,
        **inert_zip_fact,
        **prefix_landmark_facts,
        **pth_override_facts,
        "_PYTHON_BUILD": False,
        "setup_parent_paths_verified": True,
        "_pickle_extension": True,
    }


def _target_image_inert_zip_fact(tracked):
    """Select the pinned route's absent ZIP landmark without starting Python."""
    if type(tracked) is not dict or tracked.get(TARGET_INERT_ZIP_PATH) is not None:
        raise ValueError("TARGET_IMAGE_INERT_ZIP_PRESENT")
    return {"inert_zip_candidate": "/usr/local/lib/python312.zip"}


def _target_image_prefix_landmark_facts(tracked):
    """Report filesystem landmark candidates without claiming runtime prefixes."""
    stdlib = tracked.get(TARGET_PREFIX_STDLIB_LANDMARK) if type(tracked) is dict else None
    platstdlib = tracked.get(TARGET_EXEC_PREFIX_LANDMARK) if type(tracked) is dict else None
    if (stdlib != {"file": True, "directory": False, "symlink": False,
                   "linkname": None, "mode": 0o644, "sha256": OS_SOURCE_SHA256}
            or platstdlib != {"file": False, "directory": True, "symlink": False,
                              "linkname": None, "mode": 0o755, "sha256": None}
            or any(tracked.get(path) != {
                "file": False, "directory": True, "symlink": False,
                "linkname": None, "mode": 0o755, "sha256": None,
            } for path in TARGET_PREFIX_PARENT_DIRECTORIES)
            or any(tracked.get(path) is not None for path in TARGET_PREFIX_VENV_MARKERS)
            or tracked.get(TARGET_BUILD_MARKER) is not None):
        raise ValueError("TARGET_IMAGE_PREFIX_LANDMARKS")
    return {
        "prefix_landmark_candidate": "/usr/local",
        "exec_prefix_landmark_candidate": "/usr/local",
        "prefix_venv_markers_absent": list(TARGET_PREFIX_VENV_MARKERS),
        "build_marker_absent": TARGET_BUILD_MARKER,
    }


def _target_image_sys_path_candidate(image_facts, getpath_inventory,
                                    no_site, direct_python312,
                                    no_project_base_override):
    """Derive a fixed-route path candidate from pinned source and image facts."""
    if not image_facts:
        return {}
    if (not no_site or not direct_python312 or not no_project_base_override
            or type(getpath_inventory) is not dict
            or getpath_inventory.get("posix_default_path_append_order") != (
                "ZIP_LANDMARK", "stdlib_dir", "platstdlib_dir",
            )
            or getpath_inventory.get("pth_override_guard") is not True
            or image_facts.get("prefix") != "/usr/local"
            or image_facts.get("exec_prefix") != "/usr/local"
            or image_facts.get("platlibdir") != "lib"
            or image_facts.get("compiled_pythonpath") != ""
            or image_facts.get("pth_override_files_absent")
            != list(TARGET_PTH_OVERRIDE_PATHS)
            or image_facts.get("prefix_landmark_candidate") != "/usr/local"
            or image_facts.get("exec_prefix_landmark_candidate") != "/usr/local"):
        raise ValueError("TARGET_IMAGE_SYS_PATH_CANDIDATE")
    paths = [
        "/usr/local/lib/python312.zip",
        "/usr/local/lib/python3.12",
        "/usr/local/lib/python3.12/lib-dynload",
    ]
    if (paths[0] != "/" + TARGET_INERT_ZIP_PATH
            or image_facts.get("inert_zip_candidate") != paths[0]):
        raise ValueError("TARGET_IMAGE_SYS_PATH_ZIP_BINDING")
    if (image_facts.get("destshared") != paths[2]
            or image_facts.get("_pickle_extension") is not True):
        raise ValueError("TARGET_IMAGE_SYS_PATH_ROOT_BINDING")
    executable_path = image_facts.get("executable_path_candidate")
    executable_size = image_facts.get("executable_size")
    pickle_size = image_facts.get("pickle_extension_size")
    extension_path = "/" + PICKLE_EXTENSION_PATH
    if (executable_path != "/usr/local/bin/python3.12"
            or image_facts.get("executable_sha256") != TARGET_EXECUTABLE_SHA256
            or type(executable_size) is not int
            or not 0 <= executable_size <= MAX_S15_FILE_BYTES
            or image_facts.get("pickle_extension_sha256") != PICKLE_EXTENSION_SHA256
            or type(pickle_size) is not int
            or not 0 <= pickle_size <= MAX_S15_FILE_BYTES
            or executable_size + pickle_size > MAX_S15_FILE_TOTAL_BYTES
            or not extension_path.startswith(image_facts["destshared"].rstrip("/") + "/")):
        raise ValueError("TARGET_IMAGE_S15_FILE_CANDIDATES")
    if (image_facts.get("sysconfigdata_path") != TARGET_SYSCONFIGDATA_PATH
            or image_facts.get("sysconfigdata_sha256")
            != TARGET_SYSCONFIGDATA_SHA256
            or image_facts.get("soabi")
            != TARGET_SYSCONFIGDATA_EXPECTED_VALUES["SOABI"]):
        raise ValueError("TARGET_IMAGE_S15_ABI_CANDIDATE")
    return {
        "sys_path_candidate": paths,
        "executable_field_candidate": {
            "value": executable_path,
            "target": executable_path,
            "target_sha256": image_facts["executable_sha256"],
            "direct_regular_file": True,
            "runtime_executable_claimed": False,
        },
        "executable_target_candidate": executable_path,
        "abi_field_candidate": {
            "value": image_facts["soabi"],
            "source_path": TARGET_SYSCONFIGDATA_PATH,
            "source_sha256": TARGET_SYSCONFIGDATA_SHA256,
            "source_key": "SOABI",
            "runtime_abi_claimed": False,
        },
        "files_field_candidate": [
            {
                "path": executable_path,
                "size": executable_size,
                "sha256": image_facts["executable_sha256"],
            },
            {
                "path": extension_path,
                "size": pickle_size,
                "sha256": image_facts["pickle_extension_sha256"],
            },
        ],
        "roots_field_candidate": {
            "values": [paths[1], image_facts["destshared"]],
            "stdlib_root": paths[1],
            "extension_root": image_facts["destshared"],
            "extension_file_verified": True,
            "runtime_roots_claimed": False,
        },
        "inert_zip_field_candidate": {
            "value": paths[0],
            "path_role": "ZIP_LANDMARK",
            "sys_path_candidate_index": 0,
            "image_member_absent": True,
            "runtime_membership_claimed": False,
        },
    }


def _target_s15_prefixes_field_candidate(
        image_facts, getpath_inventory, sys_path_candidate,
        initconfig_source, no_site, direct_python312,
        no_project_base_override):
    """Bind four S15 prefixes using pinned config, source, and image facts."""
    expected_path = [
        "/usr/local/lib/python312.zip",
        "/usr/local/lib/python3.12",
        "/usr/local/lib/python3.12/lib-dynload",
    ]
    if (not no_site or not direct_python312 or not no_project_base_override
            or type(image_facts) is not dict
            or image_facts.get("sysconfigdata_path") != TARGET_SYSCONFIGDATA_PATH
            or image_facts.get("sysconfigdata_sha256") != TARGET_SYSCONFIGDATA_SHA256
            or image_facts.get("prefix") != "/usr/local"
            or image_facts.get("exec_prefix") != "/usr/local"
            or image_facts.get("prefix_landmark_candidate") != "/usr/local"
            or image_facts.get("exec_prefix_landmark_candidate") != "/usr/local"
            or image_facts.get("prefix_venv_markers_absent")
            != list(TARGET_PREFIX_VENV_MARKERS)
            or image_facts.get("build_marker_absent") != TARGET_BUILD_MARKER
            or image_facts.get("_PYTHON_BUILD") is not False
            or image_facts.get("setup_parent_paths_verified") is not True
            or image_facts.get("pth_override_files_absent")
            != list(TARGET_PTH_OVERRIDE_PATHS)
            or type(getpath_inventory) is not dict
            or getpath_inventory.get("source_sha256") != GETPATH_SOURCE_SHA256
            or getpath_inventory.get("base_prefix_config_read") is not True
            or getpath_inventory.get("base_prefix_fallback_bound") is not True
            or type(sys_path_candidate) is not dict
            or sys_path_candidate.get("sys_path_candidate") != expected_path):
        return {}
    if (type(initconfig_source) is not bytes or not initconfig_source
            or len(initconfig_source) > MAX_INITCONFIG_C_BYTES
            or hashlib.sha256(initconfig_source).hexdigest() != INITCONFIG_C_SHA256):
        return {}
    source = initconfig_source.decode("utf-8")

    def function_body(name):
        match = re.search(
            r"\bvoid\s+" + re.escape(name)
            + r"\s*\([^)]*\)\s*\{(?P<body>.*?)^\}",
            source, re.DOTALL | re.MULTILINE,
        )
        return match.group("body") if match is not None else None

    compat = function_body("_PyConfig_InitCompatConfig")
    defaults = function_body("config_init_defaults")
    python_config = function_body("PyConfig_InitPythonConfig")
    prefix_fields = ("prefix", "base_prefix", "exec_prefix", "base_exec_prefix")
    if (compat is None or defaults is None or python_config is None
            or not re.search(r"memset\(config,\s*0,\s*sizeof\(\*config\)\);", compat)
            or "_PyConfig_InitCompatConfig(config);" not in defaults
            or "config_init_defaults(config);" not in python_config
            or any(re.search(r"\bconfig->" + field + r"\s*=", defaults)
                   for field in prefix_fields)):
        return {}
    return {
        "values": ("/usr/local", "/usr/local", "/usr/local", "/usr/local"),
        "field_order": ("prefix", "exec_prefix", "base_prefix", "base_exec_prefix"),
        "prefix_source": "getpath POSIX landmarks and verified sysconfig defaults",
        "base_prefix_source": "empty PyConfig defaults and getpath fallback",
        "getpath_source_sha256": GETPATH_SOURCE_SHA256,
        "initconfig_source_sha256": INITCONFIG_C_SHA256,
        "sysconfigdata_path": TARGET_SYSCONFIGDATA_PATH,
        "sysconfigdata_sha256": TARGET_SYSCONFIGDATA_SHA256,
        "runtime_prefixes_claimed": False,
    }


def _target_image_pth_override_facts(tracked):
    """Reject image-level `._pth` overrides for the fixed direct route."""
    if (type(tracked) is not dict
            or any(tracked.get(path) is not None for path in TARGET_PTH_OVERRIDE_PATHS)):
        raise ValueError("TARGET_IMAGE_PTH_OVERRIDE_PRESENT")
    return {"pth_override_files_absent": list(TARGET_PTH_OVERRIDE_PATHS)}


def _target_image_sysconfigdata_facts(source):
    """Read fixed ABI and extension-root values from pinned literal build data."""
    if (type(source) is not bytes or len(source) > MAX_TARGET_SYSCONFIGDATA_BYTES
            or hashlib.sha256(source).hexdigest() != TARGET_SYSCONFIGDATA_SHA256):
        raise ValueError("TARGET_SYSCONFIGDATA_DIGEST")
    try:
        tree = ast.parse(source)
        assignments = [node for node in tree.body if isinstance(node, ast.Assign)
                       and any(isinstance(target, ast.Name)
                               and target.id == "build_time_vars"
                               for target in node.targets)]
        if len(assignments) != 1 or len(assignments[0].targets) != 1:
            raise ValueError("TARGET_SYSCONFIGDATA_ASSIGNMENT")
        value_node = assignments[0].value
        if not isinstance(value_node, ast.Dict):
            raise ValueError("TARGET_SYSCONFIGDATA_MAPPING")
        keys = [ast.literal_eval(key) for key in value_node.keys]
        if len(keys) != len(set(keys)):
            raise ValueError("TARGET_SYSCONFIGDATA_DUPLICATE_KEY")
        values = ast.literal_eval(value_node)
    except (SyntaxError, TypeError, ValueError) as error:
        raise ValueError("TARGET_SYSCONFIGDATA_LITERAL") from error
    if type(values) is not dict:
        raise ValueError("TARGET_SYSCONFIGDATA_MAPPING")
    if any(values.get(key) != value
           for key, value in TARGET_SYSCONFIGDATA_EXPECTED_VALUES.items()):
        raise ValueError("TARGET_SYSCONFIGDATA_VALUES")
    return {
        "build_time_vars_literal_dict": True,
        "build_time_vars_entry_count": len(values),
        "soabi": values["SOABI"],
        "destshared": values["DESTSHARED"],
        "extension_suffix": values["EXT_SUFFIX"],
        "multiarch": values["MULTIARCH"],
        "abiflags": values["ABIFLAGS"],
        "machdep": values["MACHDEP"],
        "prefix": values["prefix"],
        "exec_prefix": values["exec_prefix"],
        "platlibdir": values["PLATLIBDIR"],
        "compiled_pythonpath": values["PYTHONPATH"],
        "library_dir": values["LIBDIR"],
        "library_name": values["LDLIBRARY"],
        "library_soname": values["INSTSONAME"],
        "shared_library_enabled": values["Py_ENABLE_SHARED"],
    }


def _target_image_setup_paths_safe(tracked):
    """Reject symlinked parents that could redirect the pinned Setup probes."""
    if type(tracked) is not dict:
        return False
    for path in ("usr", "usr/local", "usr/local/bin"):
        facts = tracked.get(path)
        if (type(facts) is not dict or facts.get("directory") is not True
                or facts.get("symlink") is not False):
            return False
    modules = tracked.get("usr/local/bin/Modules")
    if (modules is not None
            and (type(modules) is not dict or modules.get("directory") is not True
                 or modules.get("symlink") is not False)):
        return False
    return (tracked.get("usr/local/bin/Modules/Setup") is None
            and tracked.get("usr/local/bin/Modules/Setup.local") is None)


def _target_condition(node, known_names=None, known_call_facts=None):
    """Resolve only fixed, side-effect-free target platform predicates."""
    target = {
        "sys.version_info": (3, 12, 16, "final", 0),
        "sys.version_info.major": 3,
        "sys.version_info.minor": 12,
        "sys.version_info.micro": 16,
        "sys.version_info.releaselevel": "final",
        "sys.version_info.serial": 0,
        "sys.byteorder": "little",
        "sys.builtin_module_names": _KNOWN_BUILTIN_NAMES,
    }
    known_names = known_names or {}
    known_call_facts = known_call_facts or ()
    expression = ast.unparse(node)
    for fact_expression, fact_value in known_call_facts:
        if expression == fact_expression:
            return fact_value if type(fact_value) is bool else None

    def hashable_literal(item):
        if type(item) in (str, int, bool, type(None)):
            return True
        return (type(item) is tuple
                and all(hashable_literal(element) for element in item))

    def value(expr):
        expression = ast.unparse(expr)
        for fact_expression, fact_value in known_call_facts:
            if expression == fact_expression:
                return fact_value
        if isinstance(expr, ast.Call):
            if (isinstance(expr.func, ast.Attribute)
                    and expr.func.attr == "get" and not expr.keywords
                    and len(expr.args) in (1, 2)):
                container = value(expr.func.value)
                key = value(expr.args[0])
                default = value(expr.args[1]) if len(expr.args) == 2 else None
                if (type(container) is dict and key is not _UNKNOWN
                        and default is not _UNKNOWN
                        and hashable_literal(key)):
                    if key in container:
                        return container[key]
                    return default
            if (isinstance(expr.func, ast.Attribute)
                    and expr.func.attr == "startswith" and not expr.keywords
                    and len(expr.args) == 1):
                receiver = value(expr.func.value)
                prefix = value(expr.args[0])
                if (type(receiver) is str
                        and (type(prefix) is str
                             or (type(prefix) is tuple
                                 and all(type(item) is str for item in prefix)))):
                    return receiver.startswith(prefix)
        if isinstance(expr, ast.Constant) and type(expr.value) in (str, int, bool, type(None)):
            return expr.value
        if isinstance(expr, ast.Tuple):
            items = [value(item) for item in expr.elts]
            return tuple(items) if all(item is not _UNKNOWN for item in items) else _UNKNOWN
        if isinstance(expr, ast.Dict):
            result = {}
            for key_expr, value_expr in zip(expr.keys, expr.values):
                if key_expr is None:
                    return _UNKNOWN
                key = value(key_expr)
                item = value(value_expr)
                if (key is _UNKNOWN or item is _UNKNOWN
                        or not hashable_literal(key)):
                    return _UNKNOWN
                result[key] = item
            return result
        if isinstance(expr, ast.Subscript):
            container = value(expr.value)
            if type(container) is dict:
                if isinstance(expr.slice, ast.Slice):
                    return _UNKNOWN
                index = value(expr.slice)
                if index is _UNKNOWN or not hashable_literal(index):
                    return _UNKNOWN
                try:
                    return container[index]
                except KeyError:
                    return _UNKNOWN
            if type(container) not in (tuple, list, str):
                return _UNKNOWN
            if isinstance(expr.slice, ast.Slice):
                bounds = []
                for bound in (expr.slice.lower, expr.slice.upper, expr.slice.step):
                    if bound is None:
                        bounds.append(None)
                        continue
                    resolved = value(bound)
                    if type(resolved) is not int:
                        return _UNKNOWN
                    bounds.append(resolved)
                if bounds[2] == 0:
                    return _UNKNOWN
                return container[slice(*bounds)]
            index = value(expr.slice)
            if type(index) is int:
                try:
                    return container[index]
                except IndexError:
                    return _UNKNOWN
            return _UNKNOWN
        if isinstance(expr, ast.List):
            items = [value(item) for item in expr.elts]
            return list(items) if all(item is not _UNKNOWN for item in items) else _UNKNOWN
        if isinstance(expr, ast.Set):
            items = [value(item) for item in expr.elts]
            if (all(item is not _UNKNOWN for item in items)
                    and all(hashable_literal(item) for item in items)):
                return set(items)
            return _UNKNOWN
        if isinstance(expr, ast.Attribute):
            name = ast.unparse(expr)
            return target.get(name, _UNKNOWN)
        if isinstance(expr, ast.Name):
            known = known_names.get(expr.id, _UNKNOWN)
            if (type(known) is tuple and len(known) == 2
                    and known[0] is _STATIC_FALSE_LITERAL):
                return False
            return known
        if isinstance(expr, ast.UnaryOp) and isinstance(expr.op, ast.Not):
            item = value(expr.operand)
            return not item if item is not _UNKNOWN else _UNKNOWN
        if (isinstance(expr, ast.UnaryOp)
                and isinstance(expr.op, (ast.UAdd, ast.USub))):
            item = value(expr.operand)
            if type(item) is int:
                return item if isinstance(expr.op, ast.UAdd) else -item
        if isinstance(expr, ast.BoolOp):
            items = [value(item) for item in expr.values]
            if isinstance(expr.op, ast.And):
                return False if False in items else (all(items) if _UNKNOWN not in items else _UNKNOWN)
            if isinstance(expr.op, ast.Or):
                return True if True in items else (any(items) if _UNKNOWN not in items else _UNKNOWN)
        if isinstance(expr, ast.Compare):
            left = value(expr.left)
            rights = [value(item) for item in expr.comparators]
            if left is _UNKNOWN or any(item is _UNKNOWN for item in rights):
                return _UNKNOWN
            current = left
            try:
                for op, right in zip(expr.ops, rights):
                    if isinstance(op, ast.Eq):
                        if (current is _IMPORTED_MODULE_NAME
                                or right is _IMPORTED_MODULE_NAME):
                            other = right if current is _IMPORTED_MODULE_NAME else current
                            if type(other) is not str or other != "__main__":
                                return _UNKNOWN
                            matched = False
                        elif current is _KNOWN_BUILTIN_NAMES or right is _KNOWN_BUILTIN_NAMES:
                            return _UNKNOWN
                        else:
                            matched = current == right
                    elif isinstance(op, ast.Is):
                        if (current is _KNOWN_BUILTIN_NAMES or right is _KNOWN_BUILTIN_NAMES
                                or current is _IMPORTED_MODULE_NAME
                                or right is _IMPORTED_MODULE_NAME):
                            return _UNKNOWN
                        if (current is not None and type(current) is not bool
                                or right is not None and type(right) is not bool):
                            return _UNKNOWN
                        matched = current is right
                    elif isinstance(op, ast.NotEq):
                        if (current is _IMPORTED_MODULE_NAME
                                or right is _IMPORTED_MODULE_NAME):
                            other = right if current is _IMPORTED_MODULE_NAME else current
                            if type(other) is not str or other != "__main__":
                                return _UNKNOWN
                            matched = True
                        elif current is _KNOWN_BUILTIN_NAMES or right is _KNOWN_BUILTIN_NAMES:
                            return _UNKNOWN
                        else:
                            matched = current != right
                    elif isinstance(op, ast.IsNot):
                        if (current is _KNOWN_BUILTIN_NAMES or right is _KNOWN_BUILTIN_NAMES
                                or current is _IMPORTED_MODULE_NAME
                                or right is _IMPORTED_MODULE_NAME):
                            return _UNKNOWN
                        if (current is not None and type(current) is not bool
                                or right is not None and type(right) is not bool):
                            return _UNKNOWN
                        matched = current is not right
                    elif isinstance(op, ast.In):
                        if right is _KNOWN_BUILTIN_NAMES:
                            if type(current) is not str or current not in _TARGET_BUILTIN_MEMBERSHIP:
                                return _UNKNOWN
                            matched = _TARGET_BUILTIN_MEMBERSHIP[current]
                        else:
                            matched = current in right
                    elif isinstance(op, ast.NotIn):
                        if right is _KNOWN_BUILTIN_NAMES:
                            if type(current) is not str or current not in _TARGET_BUILTIN_MEMBERSHIP:
                                return _UNKNOWN
                            matched = not _TARGET_BUILTIN_MEMBERSHIP[current]
                        else:
                            matched = current not in right
                    elif isinstance(op, ast.Lt):
                        if current is _KNOWN_BUILTIN_NAMES or right is _KNOWN_BUILTIN_NAMES:
                            return _UNKNOWN
                        matched = current < right
                    elif isinstance(op, ast.LtE):
                        if current is _KNOWN_BUILTIN_NAMES or right is _KNOWN_BUILTIN_NAMES:
                            return _UNKNOWN
                        matched = current <= right
                    elif isinstance(op, ast.Gt):
                        if current is _KNOWN_BUILTIN_NAMES or right is _KNOWN_BUILTIN_NAMES:
                            return _UNKNOWN
                        matched = current > right
                    elif isinstance(op, ast.GtE):
                        if current is _KNOWN_BUILTIN_NAMES or right is _KNOWN_BUILTIN_NAMES:
                            return _UNKNOWN
                        matched = current >= right
                    else:
                        return _UNKNOWN
                    if not matched:
                        return False
                    current = right
                return True
            except (TypeError, ValueError):
                return _UNKNOWN
        return _UNKNOWN

    result = value(node)
    return result if type(result) is bool else None


_UNKNOWN = object()


def _target_name_aliases(tree, *, imported_module_name=False):
    bindings = {}

    def bind(name):
        if type(name) is str:
            bindings[name] = bindings.get(name, 0) + 1

    for node in ast.walk(tree):
        if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Store):
            bind(node.id)
        elif isinstance(node, ast.arg):
            bind(node.arg)
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            bind(node.name)
        elif isinstance(node, ast.alias):
            bind(node.asname or node.name.split(".")[0])
        elif isinstance(node, ast.ExceptHandler):
            bind(node.name)
        elif isinstance(node, ast.Global):
            for name in node.names:
                bind(name)
        elif isinstance(node, ast.Nonlocal):
            for name in node.names:
                bind(name)
        elif isinstance(node, ast.MatchAs):
            bind(node.name)
        elif isinstance(node, ast.MatchStar):
            bind(node.name)
        elif isinstance(node, ast.MatchMapping):
            bind(node.rest)
    known = {}
    module_name_aliases = {"__name__"} if imported_module_name else set()
    literal_false_aliases = set()
    first_load = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load):
            position = (node.lineno, node.col_offset)
            first_load[node.id] = min(first_load.get(node.id, position), position)
    deletes_module_name = any(
        isinstance(node, ast.Name) and node.id == "__name__"
        and isinstance(node.ctx, ast.Del)
        for node in ast.walk(tree)
    )
    dynamic_namespace_access = any(
        (isinstance(node, ast.Name) and node.id in {
            "exec", "eval", "globals", "locals", "vars",
        })
        or (isinstance(node, ast.alias) and node.name in {
            "exec", "eval", "globals", "locals", "vars",
        })
        or (isinstance(node, ast.Attribute) and node.attr in {
            "exec", "eval", "globals", "locals", "vars",
        })
        for node in ast.walk(tree)
    )
    if (imported_module_name and bindings.get("__name__", 0) == 0
            and not deletes_module_name and not dynamic_namespace_access):
        known["__name__"] = _IMPORTED_MODULE_NAME
    for statement in tree.body:
        if isinstance(statement, ast.Assign):
            value = statement.value
            mapped = (_KNOWN_BUILTIN_NAMES
                      if isinstance(value, ast.Attribute)
                      and ast.unparse(value) == "sys.builtin_module_names"
                      else False if isinstance(value, ast.Constant)
                      and type(value.value) is int and value.value == 0
                      else known.get(value.id, _UNKNOWN) if isinstance(value, ast.Name) else _UNKNOWN)
            for target in statement.targets:
                if isinstance(target, ast.Name):
                    if (target.id == "__name__"
                            or isinstance(value, ast.Name)
                            and value.id in module_name_aliases):
                        module_name_aliases.add(target.id)
                    else:
                        module_name_aliases.discard(target.id)
                    if mapped is _UNKNOWN:
                        known.pop(target.id, None)
                    else:
                        if (mapped is False and target.id != "_false"
                                or target.id == "_false"
                                and first_load.get(target.id, (float("inf"), 0))
                                < (statement.lineno, statement.col_offset)):
                            known.pop(target.id, None)
                        else:
                            known[target.id] = (
                                (_STATIC_FALSE_LITERAL, statement.lineno)
                                if target.id == "_false" and mapped is False
                                else mapped
                            )
                            if target.id == "_false" and mapped is False:
                                literal_false_aliases.add(target.id)
        elif isinstance(statement, ast.AnnAssign) and isinstance(statement.target, ast.Name):
            value = statement.value
            if (statement.target.id == "__name__"
                    or isinstance(value, ast.Name)
                    and value.id in module_name_aliases):
                module_name_aliases.add(statement.target.id)
            else:
                module_name_aliases.discard(statement.target.id)
            mapped = (_KNOWN_BUILTIN_NAMES
                      if isinstance(value, ast.Attribute)
                      and ast.unparse(value) == "sys.builtin_module_names"
                      else known.get(value.id, _UNKNOWN) if isinstance(value, ast.Name) else _UNKNOWN)
            if mapped is _UNKNOWN:
                known.pop(statement.target.id, None)
            else:
                known[statement.target.id] = mapped
    if dynamic_namespace_access:
        for name in module_name_aliases:
            known.pop(name, None)
        for name in literal_false_aliases:
            known.pop(name, None)
    return {
        name: value for name, value in known.items()
        if bindings.get(name) == 1
        or (name == "__name__" and value is _IMPORTED_MODULE_NAME
            and bindings.get(name, 0) == 0)
    }


def _module_body_import_names(
        tree, module, path, target_platform=False, condition_stats=None, known_names=None,
        unknown_conditions=None, known_call_facts=None, preserve_imported_name=False,
        preserve_name_facts=False):
    """Include module/class bodies, optionally pruning known target if-branches."""
    package = module if path.endswith("/__init__.py") else module.rpartition(".")[0]

    def visit(node):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            return
        if isinstance(node, ast.ClassDef):
            for statement in node.body:
                yield from visit(statement)
            return
        if isinstance(node, ast.Import):
            for alias in node.names:
                yield alias.name
            return
        if isinstance(node, ast.ImportFrom):
            if target_platform and known_names is not None and any(
                    alias.name == "*" for alias in node.names):
                after_star_false = {
                    name: value for name, value in known_names.items()
                    if (type(value) is tuple and len(value) == 2
                        and value[0] is _STATIC_FALSE_LITERAL
                        and value[1] > node.lineno)
                }
                if (preserve_imported_name
                        and known_names.get("__name__") is _IMPORTED_MODULE_NAME):
                    after_star_false["__name__"] = _IMPORTED_MODULE_NAME
                if (preserve_name_facts
                        and known_names.get("name") == "posix"):
                    after_star_false["name"] = "posix"
                if (module == "os"
                        and known_names.get("supports_bytes_environ") is True):
                    after_star_false["supports_bytes_environ"] = True
                known_names.clear()
                known_names.update(after_star_false)
            base = node.module or ""
            if node.level:
                parts = package.split(".") if package else []
                keep = max(0, len(parts) - node.level + 1)
                base = ".".join(parts[:keep] + ([base] if base else []))
            if base:
                yield base
                for alias in node.names:
                    if alias.name != "*":
                        yield base + "." + alias.name
            return
        if target_platform and isinstance(node, ast.If):
            decision = _target_condition(node.test, known_names, known_call_facts)
            if condition_stats is not None:
                key = "resolved" if decision is not None else "unknown"
                condition_stats[key] += 1
            if decision is None and unknown_conditions is not None:
                unknown_conditions.append({
                    "module": module,
                    "source_path": path,
                    "line": node.lineno,
                    "expression": ast.unparse(node.test),
                })
            selected = node.body if decision is True else node.orelse if decision is False else None
            if selected is not None:
                for statement in selected:
                    yield from visit(statement)
                return
        for child in ast.iter_child_nodes(node):
            if isinstance(child, ast.stmt):
                yield from visit(child)
            elif isinstance(child, (ast.ExceptHandler, ast.match_case)):
                for statement in child.body:
                    yield from visit(statement)

    for statement in tree.body:
        yield from visit(statement)


def _candidate_closure(files, roots=ROOTS):
    if type(files) is not dict or type(roots) is not tuple:
        raise ValueError("SOURCE_INPUT_TYPE")
    if any(type(name) is not str for name in roots) or len(set(roots)) != len(roots):
        raise ValueError("SOURCE_ROOTS")
    reached = set()
    pending = list(roots)
    edges = 0
    while pending:
        module = pending.pop()
        if module in reached:
            continue
        path = _module_path(module, files)
        if path is None:
            continue
        reached.add(module)
        tree = ast.parse(files[path], filename=path)
        for name in _import_names(tree, module, path):
            parts = name.split(".")
            candidates = []
            for index in range(1, len(parts) + 1):
                candidate = ".".join(parts[:index])
                if _module_path(candidate, files) is not None:
                    candidates.append(candidate)
            if candidates:
                edges += 1
                pending.extend(candidate for candidate in candidates if candidate not in reached)
    rows = []
    for module in sorted(reached):
        path = _module_path(module, files)
        rows.append((module + "\t" + hashlib.sha256(files[path]).hexdigest() + "\n").encode("ascii"))
    return tuple(sorted(reached)), edges, hashlib.sha256(b"".join(rows)).hexdigest()


def _module_body_candidate_closure(files, roots=ROOTS):
    if type(files) is not dict or type(roots) is not tuple:
        raise ValueError("SOURCE_INPUT_TYPE")
    if any(type(name) is not str for name in roots) or len(set(roots)) != len(roots):
        raise ValueError("SOURCE_ROOTS")
    reached = set()
    pending = list(roots)
    edges = 0
    while pending:
        module = pending.pop()
        if module in reached:
            continue
        path = _module_path(module, files)
        if path is None:
            continue
        reached.add(module)
        tree = ast.parse(files[path], filename=path)
        for name in _module_body_import_names(tree, module, path):
            parts = name.split(".")
            candidates = []
            for index in range(1, len(parts) + 1):
                candidate = ".".join(parts[:index])
                if _module_path(candidate, files) is not None:
                    candidates.append(candidate)
            if candidates:
                edges += 1
                pending.extend(candidate for candidate in candidates if candidate not in reached)
    rows = []
    for module in sorted(reached):
        path = _module_path(module, files)
        rows.append((module + "\t" + hashlib.sha256(files[path]).hexdigest() + "\n").encode("ascii"))
    return tuple(sorted(reached)), edges, hashlib.sha256(b"".join(rows)).hexdigest()


def _target_platform_candidate_closure(
        files, roots=ROOTS, unknown_conditions=None, known_call_facts=None,
        known_name_facts=None, preserve_imported_name_modules=()):
    if type(files) is not dict or type(roots) is not tuple:
        raise ValueError("SOURCE_INPUT_TYPE")
    if unknown_conditions is not None and type(unknown_conditions) is not list:
        raise ValueError("CONDITION_INVENTORY_TYPE")
    if (known_call_facts is not None and (
            type(known_call_facts) is not tuple
            or any(type(fact) is not tuple or len(fact) != 2
                   or type(fact[0]) is not str
                   or not _condition_fact_value_supported(fact[1])
                   for fact in known_call_facts))):
        raise ValueError("CONDITION_FACTS_TYPE")
    if (known_name_facts is not None and (
            type(known_name_facts) is not dict
            or any(type(module) is not str or type(facts) is not dict
                   or any(type(name) is not str or type(value) not in (str, bool, int)
                          for name, value in facts.items())
                   for module, facts in known_name_facts.items()))):
        raise ValueError("CONDITION_NAME_FACTS_TYPE")
    if (type(preserve_imported_name_modules) is not tuple
            or any(type(module) is not str for module in preserve_imported_name_modules)):
        raise ValueError("CONDITION_MODULE_NAME_FACTS_TYPE")
    reached = set()
    pending = list(roots)
    edges = 0
    condition_stats = {"resolved": 0, "unknown": 0}
    while pending:
        module = pending.pop()
        if module in reached:
            continue
        path = _module_path(module, files)
        if path is None:
            continue
        reached.add(module)
        tree = ast.parse(files[path], filename=path)
        aliases = _target_name_aliases(tree, imported_module_name=True)
        if module == "importlib._bootstrap_external":
            aliases.update(_target_importlib_windows_name_facts(files))
        elif module == "warnings":
            aliases.update((known_name_facts or {}).get(module, {}))
        elif module == "os":
            aliases.update((known_name_facts or {}).get(module, {}))
        elif module == "threading":
            aliases.update((known_name_facts or {}).get(module, {}))
        elif module == "sysconfig":
            aliases.update((known_name_facts or {}).get(module, {}))
        preserve_imported_name = (
            module in preserve_imported_name_modules
            or _target_imported_name_star_imports_safe(files, module)
        )
        if (preserve_imported_name and module in {"ast", "inspect", "sysconfig"}
                and aliases.get("__name__") is not _IMPORTED_MODULE_NAME):
            aliases["__name__"] = _IMPORTED_MODULE_NAME
        for name in _module_body_import_names(
                tree, module, path, target_platform=True, condition_stats=condition_stats,
                known_names=aliases, unknown_conditions=unknown_conditions,
                known_call_facts=known_call_facts,
                preserve_imported_name=preserve_imported_name,
                preserve_name_facts=(module in preserve_imported_name_modules)):
            parts = name.split(".")
            candidate = next(
                (".".join(parts[:index]) for index in range(len(parts), 0, -1)
                 if _module_path(".".join(parts[:index]), files) is not None),
                None,
            )
            if candidate is not None:
                edges += 1
                if candidate not in reached:
                    pending.append(candidate)
    rows = []
    for module in sorted(reached):
        path = _module_path(module, files)
        rows.append((module + "\t" + hashlib.sha256(files[path]).hexdigest() + "\n").encode("ascii"))
    if unknown_conditions is not None:
        unknown_conditions.sort(
            key=lambda row: (
                row["module"], row["source_path"], row["line"], row["expression"]
            )
        )
    return tuple(sorted(reached)), edges, hashlib.sha256(b"".join(rows)).hexdigest(), condition_stats


def _top_level_function_index(tree):
    result = {}

    def collect(node):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            result.setdefault(node.name, []).append(node)
            return
        if isinstance(node, ast.ClassDef):
            return
        for child in ast.iter_child_nodes(node):
            if isinstance(child, ast.stmt):
                collect(child)
            elif isinstance(child, (ast.ExceptHandler, ast.match_case)):
                for statement in child.body:
                    collect(statement)

    for statement in tree.body:
        collect(statement)
    return result


def _top_level_class_method_index(tree):
    result = {}

    def collect_class(node):
        methods = {}

        def collect_member(member):
            if isinstance(member, (ast.FunctionDef, ast.AsyncFunctionDef)):
                methods.setdefault(member.name, []).append(member)
                return
            if isinstance(member, ast.ClassDef):
                return
            for child in ast.iter_child_nodes(member):
                if isinstance(child, ast.stmt):
                    collect_member(child)
                elif isinstance(child, (ast.ExceptHandler, ast.match_case)):
                    for statement in child.body:
                        collect_member(statement)

        for statement in node.body:
            collect_member(statement)
        known = result.setdefault(node.name, {})
        for method_name, functions in methods.items():
            existing = known.setdefault(method_name, [])
            existing_ids = {id(function) for function in existing}
            for function in functions:
                if id(function) not in existing_ids:
                    existing.append(function)
                    existing_ids.add(id(function))

    def collect(node):
        if isinstance(node, ast.ClassDef):
            collect_class(node)
            return
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            return
        for child in ast.iter_child_nodes(node):
            if isinstance(child, ast.stmt):
                collect(child)
            elif isinstance(child, (ast.ExceptHandler, ast.match_case)):
                for statement in child.body:
                    collect(statement)

    for statement in tree.body:
        collect(statement)
    return result


def _top_level_class_base_index(tree):
    """Keep direct local base names for bounded zero-argument super() calls."""
    result = {}
    aliases = {}

    def collect_aliases(node):
        if isinstance(node, ast.ClassDef):
            return
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.Lambda)):
            return
        if isinstance(node, (ast.Assign, ast.AnnAssign)):
            value = node.value
            if isinstance(value, (ast.Name, ast.Attribute)):
                targets = node.targets if isinstance(node, ast.Assign) else [node.target]
                for target in targets:
                    if isinstance(target, ast.Name):
                        aliases.setdefault(target.id, []).append(value)
        for child in ast.iter_child_nodes(node):
            if isinstance(child, ast.stmt):
                collect_aliases(child)
            elif isinstance(child, (ast.ExceptHandler, ast.match_case)):
                for statement in child.body:
                    collect_aliases(statement)

    def resolve_base(expression, active=()):
        if isinstance(expression, ast.Name):
            if expression.id in active:
                return (expression.id,)
            candidates = aliases.get(expression.id)
            if candidates:
                resolved = []
                for candidate in candidates:
                    for value in resolve_base(candidate, (*active, expression.id)):
                        if value not in resolved:
                            resolved.append(value)
                return tuple(resolved)
            return (expression.id,)
        if isinstance(expression, ast.Attribute):
            return tuple(
                value + "." + expression.attr
                for value in resolve_base(expression.value, active)
            )
        return ()

    def collect(node):
        if isinstance(node, ast.ClassDef):
            bases = result.setdefault(node.name, [])
            for base in node.bases:
                if isinstance(base, (ast.Name, ast.Attribute)):
                    for base_name in resolve_base(base):
                        if base_name not in bases:
                            bases.append(base_name)
            return
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.Lambda)):
            return
        for child in ast.iter_child_nodes(node):
            if isinstance(child, ast.stmt):
                collect(child)
            elif isinstance(child, (ast.ExceptHandler, ast.match_case)):
                for statement in child.body:
                    collect(statement)

    for statement in tree.body:
        collect_aliases(statement)
    for statement in tree.body:
        collect(statement)
    return {name: tuple(bases) for name, bases in result.items()}


def _top_level_factory_constructor_index(tree):
    factories = {}

    def simple_return_call(statement):
        if not isinstance(statement, ast.Return):
            return None
        returned = statement.value
        if (not isinstance(returned, ast.Call) or returned.keywords
                or not isinstance(returned.func, (ast.Name, ast.Attribute))):
            return None
        return ast.unparse(returned.func)

    def inert_prefix(statement):
        return (isinstance(statement, (ast.Import, ast.ImportFrom))
                or (isinstance(statement, ast.Expr)
                    and isinstance(statement.value, ast.Constant)
                    and type(statement.value.value) is str))

    def imported_bindings(statement):
        if isinstance(statement, ast.Import):
            return tuple(alias.asname or alias.name.partition(".")[0]
                         for alias in statement.names)
        if isinstance(statement, ast.ImportFrom):
            return tuple(alias.asname or alias.name for alias in statement.names)
        return ()

    def constructor_bindings(statements):
        bindings = {}
        for statement in statements:
            if inert_prefix(statement):
                for name in imported_bindings(statement):
                    bindings.pop(name, None)
                continue
            if not isinstance(statement, (ast.Assign, ast.AnnAssign)):
                return None
            targets = statement.targets if isinstance(statement, ast.Assign) else [statement.target]
            value = statement.value
            if len(targets) != 1 or not isinstance(targets[0], ast.Name):
                return None
            target = targets[0].id
            if isinstance(value, ast.Call) and not value.keywords \
                    and isinstance(value.func, (ast.Name, ast.Attribute)):
                bindings[target] = ast.unparse(value.func)
            elif isinstance(value, ast.Name) and value.id in bindings:
                bindings[target] = bindings[value.id]
            else:
                bindings.pop(target, None)
        return bindings

    for node in tree.body:
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        if not node.body:
            continue
        returns = []
        prefix = node.body[:-1]
        if isinstance(node.body[-1], ast.Return):
            terminal = simple_return_call(node.body[-1])
            if terminal is not None:
                returns.append(terminal)
                for statement in prefix:
                    if inert_prefix(statement):
                        continue
                    if (isinstance(statement, ast.If) and not statement.orelse
                            and len(statement.body) == 1):
                        branch = simple_return_call(statement.body[0])
                        if branch is None:
                            returns = []
                            break
                        returns.append(branch)
                        continue
                    returns = []
                    break
            elif isinstance(node.body[-1].value, ast.Name):
                bindings = constructor_bindings(prefix)
                target = node.body[-1].value.id
                if bindings is not None and target in bindings:
                    returns.append(bindings[target])
            else:
                continue
        elif isinstance(node.body[-1], ast.If) and node.body[-1].orelse:
            branch = node.body[-1]
            if any(not inert_prefix(statement) for statement in prefix):
                continue
            if len(branch.body) != 1 or len(branch.orelse) != 1:
                continue
            body_return = simple_return_call(branch.body[0])
            else_return = simple_return_call(branch.orelse[0])
            if body_return is None or else_return is None:
                continue
            returns.extend((body_return, else_return))
        else:
            continue
        if not returns:
            continue
        factories[node.name] = tuple(dict.fromkeys(returns))
    return factories


def _top_level_local_class_alias_index(tree, class_index):
    """Resolve simple module-scope aliases to locally declared classes."""
    aliases = {}

    def collect(node):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef, ast.Lambda)):
            return
        if isinstance(node, (ast.Assign, ast.AnnAssign)) and isinstance(node.value, ast.Name):
            targets = node.targets if isinstance(node, ast.Assign) else [node.target]
            for target in targets:
                if isinstance(target, ast.Name):
                    candidates = aliases.setdefault(target.id, [])
                    if node.value.id not in candidates:
                        candidates.append(node.value.id)
        for child in ast.iter_child_nodes(node):
            if isinstance(child, ast.stmt):
                collect(child)
            elif isinstance(child, (ast.ExceptHandler, ast.match_case)):
                for statement in child.body:
                    collect(statement)

    def resolve(name, active=()):
        if name in active:
            return ()
        if name in class_index:
            return (name,)
        result = []
        for source in aliases.get(name, ()):
            for target in resolve(source, (*active, name)):
                if target not in result:
                    result.append(target)
        return tuple(result)

    for statement in tree.body:
        collect(statement)
    return {name: resolve(name) for name in aliases}


def _has_possible_staticmethod_rebinding(tree):
    for node in ast.walk(tree):
        if isinstance(node, ast.Name) and node.id == "staticmethod" \
                and not isinstance(node.ctx, ast.Load):
            return True
        if isinstance(node, ast.arg) and node.arg == "staticmethod":
            return True
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)) \
                and node.name == "staticmethod":
            return True
        if isinstance(node, ast.ExceptHandler) and node.name == "staticmethod":
            return True
        if isinstance(node, (ast.Global, ast.Nonlocal)) and "staticmethod" in node.names:
            return True
        if isinstance(node, ast.Import) and any(
                (alias.asname or alias.name.partition(".")[0]) == "staticmethod"
                for alias in node.names):
            return True
        if isinstance(node, ast.ImportFrom):
            if any(alias.name == "*" or (alias.asname or alias.name) == "staticmethod"
                   for alias in node.names):
                return True
        if isinstance(node, ast.MatchAs) and node.name == "staticmethod":
            return True
        if isinstance(node, ast.MatchStar) and node.name == "staticmethod":
            return True
        if isinstance(node, ast.MatchMapping) and node.rest == "staticmethod":
            return True
    return False


def _imported_function_aliases(tree, module, path, function_index):
    package = module if path.endswith("/__init__.py") else module.rpartition(".")[0]
    result = {}
    for node in ast.walk(tree):
        if not isinstance(node, ast.ImportFrom) or node.module == "__future__":
            continue
        base = node.module or ""
        if node.level:
            parts = package.split(".") if package else []
            keep = max(0, len(parts) - node.level + 1)
            base = ".".join(parts[:keep] + ([base] if base else []))
        if not base:
            continue
        for imported in node.names:
            if imported.name == "*" or imported.name not in function_index.get(base, {}):
                continue
            alias = imported.asname or imported.name
            targets = result.setdefault(alias, [])
            target = (base, imported.name)
            if target not in targets:
                targets.append(target)
    return {name: tuple(dict.fromkeys(targets)) for name, targets in result.items()}


def _imported_class_aliases(tree, module, path, class_index):
    package = module if path.endswith("/__init__.py") else module.rpartition(".")[0]
    result = {}
    local_aliases = {}
    module_aliases = _imported_module_aliases(tree, module, path, class_index)

    def add_class_target(alias, target):
        targets = result.setdefault(alias, [])
        if target not in targets:
            targets.append(target)

    for node in ast.walk(tree):
        if not isinstance(node, ast.ImportFrom) or node.module == "__future__":
            continue
        base = node.module or ""
        if node.level:
            parts = package.split(".") if package else []
            keep = max(0, len(parts) - node.level + 1)
            base = ".".join(parts[:keep] + ([base] if base else []))
        for imported in node.names:
            if imported.name not in class_index.get(base, {}):
                continue
            alias = imported.asname or imported.name
            add_class_target(alias, (base, imported.name))

    def collect_aliases(node):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef, ast.Lambda)):
            return
        if isinstance(node, (ast.Assign, ast.AnnAssign)):
            value = node.value
            targets = node.targets if isinstance(node, ast.Assign) else [node.target]
            if isinstance(value, (ast.Name, ast.Attribute)):
                for target in targets:
                    if isinstance(target, ast.Name):
                        sources = local_aliases.setdefault(target.id, [])
                        if not any(ast.dump(value) == ast.dump(source) for source in sources):
                            sources.append(value)
        for child in ast.iter_child_nodes(node):
            if isinstance(child, ast.stmt):
                collect_aliases(child)
            elif isinstance(child, (ast.ExceptHandler, ast.match_case)):
                for statement in child.body:
                    collect_aliases(statement)

    def resolve(alias, active=()):
        if alias in active:
            return ()
        targets = list(result.get(alias, ()))
        for expression in local_aliases.get(alias, ()):
            if isinstance(expression, ast.Name):
                source_targets = resolve(expression.id, (*active, alias))
            elif isinstance(expression, ast.Attribute):
                receiver = ast.unparse(expression.value)
                source_targets = tuple(
                    (target_module, expression.attr)
                    for target_module in module_aliases.get(receiver, ())
                    if expression.attr in class_index.get(target_module, {})
                )
            else:
                source_targets = ()
            for target in source_targets:
                if target not in targets:
                    targets.append(target)
        return tuple(targets)

    for statement in tree.body:
        collect_aliases(statement)
    for alias in local_aliases:
        for target in resolve(alias):
            add_class_target(alias, target)
    return {name: tuple(targets) for name, targets in result.items()}


def _imported_module_aliases(tree, module, path, module_index):
    result = {}

    def add(expression, target_module):
        if not expression or target_module not in module_index:
            return
        targets = result.setdefault(expression, [])
        if target_module not in targets:
            targets.append(target_module)

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for imported in node.names:
                if imported.asname:
                    add(imported.asname, imported.name)
                else:
                    add(imported.name, imported.name)
                    root = imported.name.partition(".")[0]
                    if root != imported.name:
                        add(root, root)
        elif isinstance(node, ast.ImportFrom) and node.module != "__future__":
            package = module if path.endswith("/__init__.py") else module.rpartition(".")[0]
            base = node.module or ""
            if node.level:
                parts = package.split(".") if package else []
                keep = max(0, len(parts) - node.level + 1)
                base = ".".join(parts[:keep] + ([base] if base else []))
            for imported in node.names:
                if imported.name == "*":
                    continue
                target_module = base + ("." if base else "") + imported.name
                add(imported.asname or imported.name, target_module)
    return {expression: tuple(targets) for expression, targets in result.items()}


def _lexical_import_statements(statements):
    """Return normalized import declarations lexically nested in AST nodes."""
    rows = []
    for statement in statements:
        for node in ast.walk(statement):
            if isinstance(node, ast.Import):
                rows.append({
                    "kind": "import",
                    "line": node.lineno,
                    "names": sorted([
                        {"name": alias.name, "asname": alias.asname}
                        for alias in node.names
                    ], key=lambda item: (item["name"], item["asname"] or "")),
                })
            elif isinstance(node, ast.ImportFrom):
                rows.append({
                    "kind": "from",
                    "line": node.lineno,
                    "level": node.level,
                    "module": node.module or "",
                    "names": sorted([
                        {"name": alias.name, "asname": alias.asname}
                        for alias in node.names
                    ], key=lambda item: (item["name"], item["asname"] or "")),
                })
    return sorted(rows, key=lambda row: (
        row["line"], json.dumps(row, sort_keys=True, separators=(",", ":"))
    ))


def _lexical_call_sites(statements):
    """Return lexical calls with AST line and zero-based UTF-8 byte offset."""
    rows = [
        {
            "line": node.lineno,
            "column": node.col_offset,
            "expression": ast.unparse(node),
        }
        for statement in statements
        for node in ast.walk(statement)
        if isinstance(node, ast.Call)
    ]
    return sorted(rows, key=lambda row: (
        row["line"], row["column"], row["expression"]
    ))


def _imported_module_function_aliases(
        module_aliases, function_index, class_dispatch_index):
    result = {}
    for expression, imported_modules in module_aliases.items():
        aliases = result.setdefault(expression, {})
        for module in imported_modules:
            for function_name in function_index.get(module, {}):
                target = (module, function_name)
                targets = aliases.setdefault(function_name, [])
                if target not in targets:
                    targets.append(target)
            for class_name, methods in class_dispatch_index.get(module, {}).items():
                constructors = methods.get("__init__", ())
                if not constructors:
                    continue
                targets = aliases.setdefault(class_name, [])
                for constructor in constructors:
                    target = constructor
                    if target not in targets:
                        targets.append(target)
    return {expression: {name: tuple(targets) for name, targets in functions.items()}
            for expression, functions in result.items()}


def _imported_module_class_method_aliases(module_aliases, class_dispatch_index):
    result = {}

    for expression, imported_modules in module_aliases.items():
        for module in imported_modules:
            for class_name, methods in class_dispatch_index.get(module, {}).items():
                receiver = expression + "." + class_name
                aliases = result.setdefault(receiver, {})
                for method_name, owners in methods.items():
                    targets = aliases.setdefault(method_name, [])
                    for owner in owners:
                        target = owner
                        if target not in targets:
                            targets.append(target)
    return {expression: {name: tuple(targets) for name, targets in methods.items()}
            for expression, methods in result.items()}


def _module_init_call_import_names(tree, module, path, condition_stats=None,
                                   imported_functions=None, imported_modules=None,
                                   imported_class_methods=None,
                                   imported_module_class_methods=None,
                                   entry_functions=(),
                                   run_module=True, visited_global=None,
                                   known_call_facts=(), known_name_facts=None,
                                   trusted_function_name_facts=None,
                                   preserve_name_facts_after_star=(),
                                   trusted_line_facts=None,
                                   trusted_empty_for_facts=None,
                                   condition_observations=None,
                                   emitted_import_sites=None,
                                   unknown_conditions=None):
    """Follow direct and simply aliased local calls from initialization."""
    package = module if path.endswith("/__init__.py") else module.rpartition(".")[0]
    postponed_annotations = any(
        isinstance(statement, ast.ImportFrom) and statement.module == "__future__"
        and any(alias.name == "annotations" for alias in statement.names)
        for statement in tree.body
    )
    known_names = _target_name_aliases(tree)
    source_name_facts = known_name_facts or {}
    trusted_function_name_facts = trusted_function_name_facts or {}
    preserve_name_facts_after_star = frozenset(preserve_name_facts_after_star)
    trusted_line_facts = trusted_line_facts or {}
    if type(trusted_empty_for_facts) is not dict:
        raise ValueError("UNTRUSTED_EMPTY_FOR_FACT")
    trusted_empty_for_facts = trusted_empty_for_facts or {}
    if condition_observations is not None and type(condition_observations) is not dict:
        raise ValueError("CONDITION_OBSERVATIONS_TYPE")
    if emitted_import_sites is not None and type(emitted_import_sites) is not set:
        raise ValueError("IMPORT_SITE_OBSERVATIONS_TYPE")
    local_condition_observations = {}
    local_import_sites = set()
    import_sites = emitted_import_sites if emitted_import_sites is not None else local_import_sites
    if any(source_name_facts.get(name, _UNKNOWN) != value
           for name, value in trusted_function_name_facts.items()):
        raise ValueError("UNTRUSTED_FUNCTION_NAME_FACT")
    if not preserve_name_facts_after_star.issubset(source_name_facts):
        raise ValueError("UNTRUSTED_STAR_IMPORT_NAME_FACT")
    if (any(type(line) is not int or type(value) is not bool
            for line, value in trusted_line_facts.items())):
        raise ValueError("UNTRUSTED_LINE_FACT")
    for line, iterator in trusted_empty_for_facts.items():
        matching = [node for node in ast.walk(tree)
                    if isinstance(node, ast.For) and node.lineno == line]
        if (type(line) is not int or type(iterator) is not str
                or len(matching) != 1 or ast.unparse(matching[0].iter) != iterator):
            raise ValueError("UNTRUSTED_EMPTY_FOR_FACT")
    known_names.update(source_name_facts)

    def decide_condition(node, facts, in_function=False):
        if node.lineno in trusted_line_facts:
            return trusted_line_facts[node.lineno]
        if in_function and source_name_facts:
            facts = dict(facts)
            facts.update({name: _UNKNOWN for name in source_name_facts})
            facts.update(trusted_function_name_facts)
        return _target_condition(node, facts, known_call_facts)

    def scope_condition_names(allow_source_name_facts):
        facts = dict(known_names)
        if not allow_source_name_facts and source_name_facts:
            facts.update({name: _UNKNOWN for name in source_name_facts})
            facts.update(trusted_function_name_facts)
        return facts

    def scope_functions(statements, allow_source_name_facts=True):
        result = {}
        conditions = scope_condition_names(allow_source_name_facts)

        def collect(node):
            if isinstance(node, ast.FunctionDef):
                result.setdefault(node.name, []).append(node)
                return
            if isinstance(node, (ast.AsyncFunctionDef, ast.ClassDef)):
                return
            if isinstance(node, ast.ImportFrom) and any(alias.name == "*" for alias in node.names):
                conditions.clear()
                return
            if isinstance(node, ast.If):
                decision = decide_condition(node.test, conditions)
                selected = node.body if decision is True else node.orelse if decision is False else None
                for statement in selected if selected is not None else (*node.body, *node.orelse):
                    collect(statement)
                return
            for child in ast.iter_child_nodes(node):
                if isinstance(child, ast.stmt):
                    collect(child)
                elif isinstance(child, (ast.ExceptHandler, ast.match_case)):
                    for statement in child.body:
                        collect(statement)

        for statement in statements:
            collect(statement)
        return result


    def scope_function_aliases(statements, functions, allow_source_name_facts=True):
        """Conservatively add simple same-scope ``alias = function`` names."""
        result = {name: list(nodes) for name, nodes in functions.items()}
        conditions = scope_condition_names(allow_source_name_facts)

        def add_alias(node):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                return
            if isinstance(node, ast.ImportFrom) and any(alias.name == "*" for alias in node.names):
                conditions.clear()
                return
            if isinstance(node, ast.If):
                decision = decide_condition(node.test, conditions)
                selected = node.body if decision is True else node.orelse if decision is False else None
                for statement in selected if selected is not None else (*node.body, *node.orelse):
                    add_alias(statement)
                return
            value = node.value if isinstance(node, (ast.Assign, ast.AnnAssign)) else None
            targets = node.targets if isinstance(node, ast.Assign) else [node.target] if isinstance(node, ast.AnnAssign) else []
            if isinstance(value, ast.Name) and value.id in result:
                for target in targets:
                    if isinstance(target, ast.Name):
                        known = result.setdefault(target.id, [])
                        known_ids = {id(function) for function in known}
                        known.extend(function for function in result[value.id]
                                     if id(function) not in known_ids)
                        known_ids.update(id(function) for function in known)
            for child in ast.iter_child_nodes(node):
                if isinstance(child, ast.stmt):
                    add_alias(child)
                elif isinstance(child, (ast.ExceptHandler, ast.match_case)):
                    for statement in child.body:
                        add_alias(statement)

        for statement in statements:
            add_alias(statement)
        return result

    def class_scope_functions(statements, outer_functions,
                              allow_source_name_facts=False):
        """Resolve class-body function aliases against ordered class bindings."""
        result = {name: list(nodes) for name, nodes in outer_functions.items()}
        conditions = scope_condition_names(allow_source_name_facts)

        def copy_scope(scope):
            return {name: list(nodes) for name, nodes in scope.items()}

        def merge_scopes(left, right):
            merged = {}
            for name in left.keys() | right.keys():
                nodes = []
                seen = set()
                for node in (*left.get(name, []), *right.get(name, [])):
                    if id(node) not in seen:
                        seen.add(id(node))
                        nodes.append(node)
                merged[name] = nodes
            return merged

        def bind(node, scope, facts):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                scope[node.name] = [node]
                return
            if isinstance(node, ast.ClassDef):
                return
            if isinstance(node, ast.ImportFrom) and any(alias.name == "*" for alias in node.names):
                facts.clear()
                return
            if isinstance(node, ast.If):
                decision = decide_condition(node.test, facts)
                selected = node.body if decision is True else node.orelse if decision is False else None
                if selected is not None:
                    for statement in selected:
                        bind(statement, scope, facts)
                else:
                    left, right = copy_scope(scope), copy_scope(scope)
                    left_facts, right_facts = dict(facts), dict(facts)
                    for statement in node.body:
                        bind(statement, left, left_facts)
                    for statement in node.orelse:
                        bind(statement, right, right_facts)
                    scope.clear()
                    scope.update(merge_scopes(left, right))
                    facts.clear()
                    facts.update({name: value for name, value in left_facts.items()
                                  if right_facts.get(name, _UNKNOWN) == value})
                return
            value = node.value if isinstance(node, (ast.Assign, ast.AnnAssign)) else None
            targets = node.targets if isinstance(node, ast.Assign) else [node.target] if isinstance(node, ast.AnnAssign) else []
            if isinstance(value, ast.Name) and value.id in scope:
                for target in targets:
                    if isinstance(target, ast.Name):
                        scope[target.id] = list(scope[value.id])
            for child in ast.iter_child_nodes(node):
                if isinstance(child, ast.stmt):
                    bind(child, scope, facts)
                elif isinstance(child, (ast.ExceptHandler, ast.match_case)):
                    for statement in child.body:
                        bind(statement, scope, facts)

        for statement in statements:
            bind(statement, result, conditions)
        return result

    def scope_class_methods(statements):
        """Index methods declared by local classes, preserving alternatives."""
        result = {}
        conditions = scope_condition_names(False)

        def collect_class(node):
            methods = {}

            def collect_member(member):
                if isinstance(member, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    methods.setdefault(member.name, []).append(member)
                    return
                if isinstance(member, ast.ClassDef):
                    return
                if isinstance(member, ast.ImportFrom) and any(alias.name == "*" for alias in member.names):
                    conditions.clear()
                    return
                if isinstance(member, ast.If):
                    decision = decide_condition(member.test, conditions)
                    selected = member.body if decision is True else member.orelse if decision is False else None
                    for statement in selected if selected is not None else (*member.body, *member.orelse):
                        collect_member(statement)
                    return
                for child in ast.iter_child_nodes(member):
                    if isinstance(child, ast.stmt):
                        collect_member(child)
                    elif isinstance(child, (ast.ExceptHandler, ast.match_case)):
                        for statement in child.body:
                            collect_member(statement)

            for statement in node.body:
                collect_member(statement)
            known = result.setdefault(node.name, {})
            for method_name, functions in methods.items():
                existing = known.setdefault(method_name, [])
                existing_ids = {id(function) for function in existing}
                for function in functions:
                    if id(function) not in existing_ids:
                        existing.append(function)
                        existing_ids.add(id(function))

        def collect(node):
            if isinstance(node, ast.ClassDef):
                collect_class(node)
                return
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                return
            if isinstance(node, ast.ImportFrom) and any(alias.name == "*" for alias in node.names):
                conditions.clear()
                return
            if isinstance(node, ast.If):
                decision = decide_condition(node.test, conditions)
                selected = node.body if decision is True else node.orelse if decision is False else None
                for statement in selected if selected is not None else (*node.body, *node.orelse):
                    collect(statement)
                return
            for child in ast.iter_child_nodes(node):
                if isinstance(child, ast.stmt):
                    collect(child)
                elif isinstance(child, (ast.ExceptHandler, ast.match_case)):
                    for statement in child.body:
                        collect(statement)

        for statement in statements:
            collect(statement)
        return result

    module_functions = scope_function_aliases(tree.body, scope_functions(tree.body))
    factory_constructors = _top_level_factory_constructor_index(tree)
    module_class_methods = scope_class_methods(tree.body)
    module_class_bases = _top_level_class_base_index(tree)
    module_class_aliases = _top_level_local_class_alias_index(
        tree, module_class_methods
    )

    def local_base_classes(class_name):
        """Return known local ancestors without imposing a linear MRO order."""
        pending_bases = list(module_class_bases.get(class_name, ()))
        seen = set()
        ancestors = []
        while pending_bases:
            base_name = pending_bases.pop()
            if base_name in seen:
                continue
            seen.add(base_name)
            ancestors.append(base_name)
            pending_bases.extend(module_class_bases.get(base_name, ()))
        return tuple(ancestors)

    def known_class_method_targets(class_name, method_name):
        """Return methods on a known class and its known local ancestors."""
        local_targets = []
        imported_targets = set()
        class_candidates = tuple(dict.fromkeys((
            class_name, *module_class_aliases.get(class_name, ()),
            *factory_constructors.get(class_name, ()),
        )))
        for local_class in class_candidates:
            for candidate in (local_class, *local_base_classes(local_class)):
                for function in module_class_methods.get(candidate, {}).get(method_name, ()):
                    if function not in local_targets:
                        local_targets.append(function)
                imported_targets.update(
                    (imported_class_methods or {}).get(candidate, {}).get(method_name, ())
                )
                imported_targets.update(
                    (imported_module_class_methods or {}).get(candidate, {}).get(method_name, ())
                )
        return tuple(local_targets), tuple(sorted(imported_targets))

    def add_base_method_calls(class_name, method_name, function_scope, call=None):
        for base_name in local_base_classes(class_name):
            for function in module_class_methods.get(base_name, {}).get(method_name, ()):
                enqueue_local(
                    function, function_scope, call, bound_method=True,
                )
            imported_targets = (imported_class_methods or {}).get(base_name, {}).get(
                method_name, ()
            )
            imported_module_targets = (imported_module_class_methods or {}).get(
                base_name, {}
            ).get(method_name, ())
            imported_calls.update(imported_targets)
            imported_calls.update(imported_module_targets)

    staticmethod_rebinding_possible = _has_possible_staticmethod_rebinding(tree)
    method_receiver_context = {}
    for class_name, methods in module_class_methods.items():
        for functions in methods.values():
            for function in functions:
                decorators = {decorator.id for decorator in function.decorator_list
                              if isinstance(decorator, ast.Name)}
                if "staticmethod" in decorators and not staticmethod_rebinding_possible:
                    continue
                positional = (*function.args.posonlyargs, *function.args.args)
                if positional:
                    method_receiver_context[id(function)] = (class_name, positional[0].arg)

    def constructed_instance_methods(statements):
        """Resolve only same-scope names assigned a direct known class call."""
        result = {}

        def bind_constructor(target_name, constructor):
            if isinstance(constructor, ast.Name):
                local_methods = module_class_methods.get(constructor.id, {})
                imported_methods = (imported_class_methods or {}).get(constructor.id, {})
                method_names = set(local_methods) | set(imported_methods)
                for factory_class in factory_constructors.get(constructor.id, ()):
                    method_names.update(module_class_methods.get(factory_class, {}))
                    method_names.update((imported_class_methods or {}).get(factory_class, {}))
                    method_names.update((imported_module_class_methods or {}).get(factory_class, {}))
                method_names.update(
                    name
                    for base_name in local_base_classes(constructor.id)
                    for name in (
                        set(module_class_methods.get(base_name, {}))
                        | set((imported_class_methods or {}).get(base_name, {}))
                        | set((imported_module_class_methods or {}).get(base_name, {}))
                    )
                )
                resolved_methods = {
                    name: known_class_method_targets(constructor.id, name)
                    for name in method_names
                }
            elif isinstance(constructor, ast.Attribute):
                receiver = ast.unparse(constructor.value) + "." + constructor.attr
                local_methods = {}
                imported_methods = (imported_module_class_methods or {}).get(receiver, {})
                resolved_methods = {
                    name: ((), tuple(targets))
                    for name, targets in imported_methods.items()
                }
            else:
                return
            bound = result.setdefault(target_name, {})
            for method_name, (functions, targets) in resolved_methods.items():
                local = bound.setdefault(method_name, {"local": [], "imported": []})["local"]
                for function in functions:
                    if function not in local:
                        local.append(function)
                external = bound.setdefault(method_name, {"local": [], "imported": []})["imported"]
                for target in targets:
                    if target not in external:
                        external.append(target)

        def bind_alias(target_name, source_name):
            source = result.get(source_name)
            if source is None:
                return
            target = result.setdefault(target_name, {})
            for method_name, entries in source.items():
                bound = target.setdefault(method_name, {"local": [], "imported": []})
                for kind in ("local", "imported"):
                    for entry in entries[kind]:
                        if entry not in bound[kind]:
                            bound[kind].append(entry)

        def collect(node):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef, ast.Lambda)):
                return
            if isinstance(node, (ast.Assign, ast.AnnAssign)):
                value = node.value
                targets = node.targets if isinstance(node, ast.Assign) else [node.target]
                for target in targets:
                    if not isinstance(target, ast.Name):
                        continue
                    if isinstance(value, ast.Call):
                        bind_constructor(target.id, value.func)
                    elif isinstance(value, ast.Name):
                        bind_alias(target.id, value.id)
            for child in ast.iter_child_nodes(node):
                if isinstance(child, ast.stmt):
                    collect(child)
                elif isinstance(child, (ast.ExceptHandler, ast.match_case)):
                    for statement in child.body:
                        collect(statement)

        for statement in statements:
            collect(statement)
        return result

    active_instance_methods = constructed_instance_methods(tree.body)
    active_method_context = None
    pending = []
    imported_calls = set()
    function_closures = {}
    function_imported_class_closures = {}
    class_method_closure_bases = []
    active_function_name_facts = {}
    scheduled_contexts = {}
    overflowed_contexts = set()
    max_contexts_per_function = 8
    call_name_writes = {
        node.id for node in ast.walk(tree)
        if isinstance(node, ast.Name) and isinstance(node.ctx, (ast.Store, ast.Del))
    }
    call_name_definitions = {}
    call_attribute_writes = set()
    dynamic_binding_call = False
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            call_name_definitions[node.name] = call_name_definitions.get(node.name, 0) + 1
        elif isinstance(node, ast.Import):
            call_name_writes.update(
                alias.asname or alias.name.partition(".")[0] for alias in node.names
            )
        elif isinstance(node, ast.ImportFrom):
            call_name_writes.update(
                alias.asname or alias.name for alias in node.names
                if alias.name != "*"
            )
        elif isinstance(node, (ast.Global, ast.Nonlocal)):
            call_name_writes.update(node.names)
        elif isinstance(node, ast.ExceptHandler) and node.name:
            call_name_writes.add(node.name)
        elif (isinstance(node, ast.Attribute)
              and isinstance(node.ctx, (ast.Store, ast.Del))):
            call_attribute_writes.add(node.attr)
        elif isinstance(node, ast.Call):
            if (isinstance(node.func, ast.Name)
                    and node.func.id in {"exec", "eval", "globals", "setattr", "delattr"}):
                dynamic_binding_call = True
            elif (isinstance(node.func, ast.Attribute)
                    and node.func.attr in {"exec", "eval", "globals", "setattr", "delattr"}):
                dynamic_binding_call = True

    def stable_call_binding(call):
        if dynamic_binding_call or not isinstance(call, ast.Call):
            return False
        if isinstance(call.func, ast.Name):
            name = call.func.id
            return (name not in call_name_writes
                    and call_name_definitions.get(name, 0) <= 1)
        if isinstance(call.func, ast.Attribute):
            if call.func.attr in call_attribute_writes:
                return False
            receiver = call.func.value
            if isinstance(receiver, ast.Name):
                return (receiver.id not in call_name_writes
                        and call_name_definitions.get(receiver.id, 0) <= 1)
            if (isinstance(receiver, ast.Call)
                    and isinstance(receiver.func, ast.Name)):
                name = receiver.func.id
                return (name not in call_name_writes
                        and call_name_definitions.get(name, 0) == 1)
        return False

    def schedule_local(function, function_scope, facts):
        function_id = id(function)
        closure = function_closures.get(function_id, function_scope)
        known = scheduled_contexts.setdefault(function_id, set())
        key = tuple(sorted(facts.items()))
        if function_id in overflowed_contexts:
            return
        if key in known:
            return
        if len(known) >= max_contexts_per_function:
            overflowed_contexts.add(function_id)
            facts = {name: _UNKNOWN for name, _ in facts.items()}
            key = tuple(sorted(facts.items()))
            if key in known:
                return
        known.add(key)
        pending.append((function, closure, facts))

    def enqueue_local(function, function_scope, call=None, *, bound_method=False):
        if not stable_call_binding(call):
            call = None
        facts = dict(_static_literal_call_facts(
            function, call, active_function_name_facts,
            bound_method=bound_method,
        ))
        schedule_local(function, function_scope, facts)

    def emit_import(node, imported_name):
        key = (module, path, node.lineno, imported_name)
        if key in import_sites:
            return False
        import_sites.add(key)
        return True

    def captures_method_receiver(function, receiver):
        args = (*function.args.posonlyargs, *function.args.args, *function.args.kwonlyargs)
        if (any(arg.arg == receiver for arg in args)
                or (function.args.vararg is not None and function.args.vararg.arg == receiver)
                or (function.args.kwarg is not None and function.args.kwarg.arg == receiver)):
            return False
        has_load = False
        has_local_binding = False

        def scan(node, root=False):
            nonlocal has_load, has_local_binding
            if not root and isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef,
                                              ast.ClassDef, ast.Lambda)):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)) \
                        and node.name == receiver:
                    has_local_binding = True
                return
            if isinstance(node, ast.Name) and node.id == receiver:
                if isinstance(node.ctx, ast.Load):
                    has_load = True
                else:
                    has_local_binding = True
            elif isinstance(node, ast.Import):
                if any((alias.asname or alias.name.partition(".")[0]) == receiver
                       for alias in node.names):
                    has_local_binding = True
            elif isinstance(node, ast.ImportFrom):
                if any((alias.asname or alias.name) == receiver for alias in node.names):
                    has_local_binding = True
            elif isinstance(node, ast.ExceptHandler) and node.name == receiver:
                has_local_binding = True
            elif isinstance(node, (ast.Global, ast.Nonlocal)) and receiver in node.names:
                has_local_binding = True
            for child in ast.iter_child_nodes(node):
                scan(child)

        scan(function, root=True)
        return has_load and not has_local_binding

    def visit(node, active_functions, in_function=False, function_scope=None):
        nonlocal imported_class_methods
        if function_scope is None:
            function_scope = module_functions
        if isinstance(node, ast.Lambda):
            for expression in (*node.args.defaults, *node.args.kw_defaults):
                if expression is not None:
                    yield from visit(expression, active_functions, in_function, function_scope)
            return
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            function_closures.setdefault(id(node), function_scope)
            function_imported_class_closures.setdefault(
                id(node), dict(
                    class_method_closure_bases[-1]
                    if class_method_closure_bases else imported_class_methods or {}
                )
            )
            if (active_method_context is not None
                    and captures_method_receiver(node, active_method_context[1])):
                method_receiver_context.setdefault(id(node), active_method_context)
            expressions = [*node.decorator_list, *node.args.defaults, *node.args.kw_defaults]
            if not postponed_annotations:
                args = (*node.args.posonlyargs, *node.args.args, *node.args.kwonlyargs)
                if node.args.vararg is not None:
                    args += (node.args.vararg,)
                if node.args.kwarg is not None:
                    args += (node.args.kwarg,)
                expressions.extend(arg.annotation for arg in args)
                expressions.append(node.returns)
            for expression in expressions:
                if expression is not None:
                    yield from visit(expression, active_functions, in_function, function_scope)
            return
        if isinstance(node, ast.ClassDef):
            class_scope = class_scope_functions(node.body, active_functions)
            for expression in (*node.decorator_list, *node.bases, *(kw.value for kw in node.keywords)):
                yield from visit(expression, active_functions, in_function, function_scope)
            scoped_alias_tree = ast.Module(body=node.body, type_ignores=[])
            scoped_class_aliases = _top_level_local_class_alias_index(
                scoped_alias_tree, imported_class_methods or {}
            )
            scoped_method_aliases = {}
            for alias, sources in scoped_class_aliases.items():
                targets = {}
                for source_name in sources:
                    for method_name, entries in (imported_class_methods or {}).get(
                        source_name, {}
                    ).items():
                        bucket = targets.setdefault(method_name, [])
                        for entry in entries:
                            if entry not in bucket:
                                bucket.append(entry)
                if targets:
                    scoped_method_aliases[alias] = {
                        name: tuple(entries) for name, entries in targets.items()
                    }
            original_imported_class_methods = imported_class_methods
            class_method_closure_bases.append(original_imported_class_methods or {})
            if scoped_method_aliases:
                imported_class_methods = {
                    **(original_imported_class_methods or {}),
                    **scoped_method_aliases,
                }
            for statement in node.body:
                yield from visit(statement, class_scope, False, function_scope)
            class_method_closure_bases.pop()
            imported_class_methods = original_imported_class_methods
            return
        if isinstance(node, ast.GeneratorExp):
            # A generator may be consumed during initialization (for example
            # by tuple(), any(), or a constructor). Keep every local call in
            # its lazy body as a candidate; proving consumption is outside
            # this bounded source analysis.
            for generator in node.generators:
                yield from visit(generator.iter, active_functions, in_function, function_scope)
                yield from visit(generator.target, active_functions, in_function, function_scope)
                for condition in generator.ifs:
                    yield from visit(condition, active_functions, in_function, function_scope)
            yield from visit(node.elt, active_functions, in_function, function_scope)
            return
        if isinstance(node, ast.AnnAssign):
            yield from visit(node.target, active_functions, in_function, function_scope)
            if not postponed_annotations and not in_function:
                yield from visit(node.annotation, active_functions, in_function, function_scope)
            if node.value is not None:
                yield from visit(node.value, active_functions, in_function, function_scope)
            return
        if isinstance(node, ast.Import):
            for alias in node.names:
                if emit_import(node, alias.name):
                    yield alias.name
            return
        if isinstance(node, ast.ImportFrom):
            if node.module == "__future__":
                return
            if any(alias.name == "*" for alias in node.names):
                imported_module_name = (
                    known_names.get("__name__") is _IMPORTED_MODULE_NAME
                )
                preserved_source_names = {
                    name: source_name_facts[name]
                    for name in preserve_name_facts_after_star
                }
                known_names.clear()
                known_names.update(preserved_source_names)
                if imported_module_name:
                    known_names["__name__"] = _IMPORTED_MODULE_NAME
            base = node.module or ""
            if node.level:
                parts = package.split(".") if package else []
                keep = max(0, len(parts) - node.level + 1)
                base = ".".join(parts[:keep] + ([base] if base else []))
            if base:
                if emit_import(node, base):
                    yield base
                for alias in node.names:
                    if alias.name != "*":
                        imported_name = base + "." + alias.name
                        if emit_import(node, imported_name):
                            yield imported_name
            return
        if (isinstance(node, ast.For)
                and trusted_empty_for_facts.get(node.lineno) == ast.unparse(node.iter)):
            for statement in node.orelse:
                yield from visit(statement, active_functions, in_function, function_scope)
            return
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
            for function in active_functions.get(node.func.id, ()):
                enqueue_local(function, function_scope, node)
            constructor_targets, imported_constructor_targets = known_class_method_targets(
                node.func.id, "__init__"
            )
            for function in constructor_targets:
                enqueue_local(
                    function, function_scope, node, bound_method=True,
                )
            imported_calls.update(imported_constructor_targets)
        elif isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
            constructor_targets = known_class_method_targets(
                ast.unparse(node.func), "__init__"
            )
            imported_calls.update(constructor_targets[1])
            if (isinstance(node.func.value, ast.Call)
                    and isinstance(node.func.value.func, ast.Name)
                    and node.func.value.func.id == "super"
                    and not node.func.value.keywords
                    and active_method_context is not None):
                class_name = active_method_context[0]
                receiver_name = active_method_context[1]
                super_args = node.func.value.args
                valid_super = not super_args or (
                    len(super_args) == 2
                    and isinstance(super_args[0], ast.Name)
                    and super_args[0].id == class_name
                    and isinstance(super_args[1], ast.Name)
                    and super_args[1].id == receiver_name
                )
                if valid_super:
                    add_base_method_calls(
                        class_name, node.func.attr, function_scope, node,
                    )
            if isinstance(node.func.value, ast.Call):
                constructor = node.func.value.func
                if isinstance(constructor, ast.Name):
                    local_targets, imported_targets = known_class_method_targets(
                        constructor.id, node.func.attr
                    )
                    for function in local_targets:
                        enqueue_local(
                            function, function_scope, node, bound_method=True,
                        )
                    imported_calls.update(imported_targets)
                elif isinstance(constructor, ast.Attribute):
                    receiver = ast.unparse(constructor.value) + "." + constructor.attr
                    imported_targets = (imported_module_class_methods or {}).get(
                        receiver, {}
                    ).get(node.func.attr, ())
                    imported_calls.update(imported_targets)
            if isinstance(node.func.value, ast.Name):
                if (active_method_context is not None
                        and node.func.value.id == active_method_context[1]):
                    class_name = active_method_context[0]
                    for function in module_class_methods.get(class_name, {}).get(node.func.attr, ()):
                        enqueue_local(
                            function, function_scope, node, bound_method=True,
                        )
                    add_base_method_calls(
                        class_name, node.func.attr, function_scope, node,
                    )
                instance_targets = active_instance_methods.get(node.func.value.id, {}).get(
                    node.func.attr, {"local": (), "imported": ()}
                )
                for function in instance_targets["local"]:
                    enqueue_local(
                        function, function_scope, node, bound_method=True,
                    )
                imported_calls.update(instance_targets["imported"])
                methods = module_class_methods.get(node.func.value.id, {})
                for function in methods.get(node.func.attr, ()):
                    enqueue_local(
                        function, function_scope, node,
                    )
            receiver = ast.unparse(node.func.value)
            imported_targets = (imported_modules or {}).get(receiver, {}).get(node.func.attr, ())
            imported_calls.update(imported_targets)
            class_targets = (imported_class_methods or {}).get(receiver, {}).get(node.func.attr, ())
            imported_calls.update(class_targets)
            module_class_targets = (imported_module_class_methods or {}).get(receiver, {}).get(node.func.attr, ())
            imported_calls.update(module_class_targets)
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
            imported_calls.update((target_module, target_function)
                                  for target_module, target_function
                                  in (imported_functions or {}).get(node.func.id, ()))
        if isinstance(node, ast.If):
            condition_names = dict(known_names)
            condition_names.update(active_function_name_facts)
            decision = decide_condition(node.test, condition_names, in_function)
            observation_store = (condition_observations if condition_observations is not None
                                 else local_condition_observations)
            observation_key = (module, path, node.lineno)
            observation = observation_store.setdefault(observation_key, {
                "node": node, "decisions": set(),
            })
            observation["decisions"].add(decision)
            selected = node.body if decision is True else node.orelse if decision is False else None
            if selected is not None:
                for statement in selected:
                    yield from visit(statement, active_functions, in_function, function_scope)
                return
        for child in ast.iter_child_nodes(node):
            yield from visit(child, active_functions, in_function, function_scope)

    imports = []
    if run_module:
        for statement in tree.body:
            imports.extend(visit(statement, module_functions))
    else:
        for name in entry_functions:
            if "." in name:
                class_name, method_name = name.split(".", 1)
                candidates = module_class_methods.get(class_name, {}).get(method_name, ())
            else:
                candidates = module_functions.get(name, ())
            for function in candidates:
                function_closures.setdefault(id(function), module_functions)
                enqueue_local(function, module_functions)
    visited = visited_global if visited_global is not None else set()
    visited_before = len(visited)
    while pending:
        function, closure_scope, parameter_facts = pending.pop()
        visited.add(id(function))
        active_function_name_facts = parameter_facts
        enclosing_imported_class_methods = imported_class_methods
        closure_class_methods = function_imported_class_closures.get(id(function), {})
        if closure_class_methods:
            imported_class_methods = {
                **(imported_class_methods or {}),
                **closure_class_methods,
            }
        active_instance_methods = constructed_instance_methods(function.body)
        active_method_context = method_receiver_context.get(id(function))
        # Track direct same-function aliases of established class candidates.
        # Called nested functions inherit this snapshot as a lexical closure;
        # Conditional/compound factory results and dynamic rebinding remain unresolved.
        scoped_alias_tree = ast.Module(body=function.body, type_ignores=[])
        scoped_class_aliases = _top_level_local_class_alias_index(
            scoped_alias_tree, imported_class_methods or {}
        )
        scoped_method_aliases = {}
        for alias, sources in scoped_class_aliases.items():
            targets = {}
            for source_name in sources:
                for method_name, entries in (imported_class_methods or {}).get(
                    source_name, {}
                ).items():
                    bucket = targets.setdefault(method_name, [])
                    for entry in entries:
                        if entry not in bucket:
                            bucket.append(entry)
            if targets:
                scoped_method_aliases[alias] = {
                    name: tuple(entries) for name, entries in targets.items()
                }
        original_imported_class_methods = imported_class_methods
        if scoped_method_aliases:
            imported_class_methods = {
                **(original_imported_class_methods or {}),
                **scoped_method_aliases,
            }
        visible_functions = dict(closure_scope)
        visible_functions.update(scope_functions(
            function.body, allow_source_name_facts=False
        ))
        visible_functions = scope_function_aliases(
            function.body, visible_functions, allow_source_name_facts=False
        )
        for statement in function.body:
            imports.extend(visit(statement, visible_functions, True, visible_functions))
        imported_class_methods = enclosing_imported_class_methods
    if condition_observations is None:
        for observation in local_condition_observations.values():
            node = observation["node"]
            decisions = observation["decisions"]
            if condition_stats is not None:
                key = "unknown" if None in decisions else "resolved"
                condition_stats[key] += 1
            if None in decisions and unknown_conditions is not None:
                unknown_conditions.append({
                    "module": module,
                    "source_path": path,
                    "line": node.lineno,
                    "expression": ast.unparse(node.test),
                    "body_imports": _lexical_import_statements(node.body),
                    "else_imports": _lexical_import_statements(node.orelse),
                    "body_calls": _lexical_call_sites(node.body),
                    "else_calls": _lexical_call_sites(node.orelse),
                })
    return tuple(imports), len(visited) - visited_before, tuple(sorted(imported_calls))


def _static_literal_call_facts(function, call, name_facts=(), *,
                               bound_method=False):
    """Bind only primitive literal arguments for one statically selected call."""
    if not isinstance(function, (ast.FunctionDef, ast.AsyncFunctionDef)):
        return ()
    all_positional = [*function.args.posonlyargs, *function.args.args]
    positional = list(all_positional)
    keyword_only = list(function.args.kwonlyargs)
    parameters = positional + keyword_only
    if function.args.vararg is not None:
        parameters.append(function.args.vararg)
    if function.args.kwarg is not None:
        parameters.append(function.args.kwarg)
    if function.decorator_list:
        return tuple((item.arg, _UNKNOWN) for item in parameters)
    if bound_method:
        if not positional:
            return tuple((item.arg, _UNKNOWN) for item in parameters)
        parameters = positional[1:] + keyword_only
        positional = positional[1:]

    if call is None or not isinstance(call, ast.Call):
        return tuple((item.arg, _UNKNOWN) for item in parameters)
    if function.args.vararg is not None or function.args.kwarg is not None:
        return tuple((item.arg, _UNKNOWN) for item in parameters)

    values = {item.arg: _UNKNOWN for item in parameters}
    invalid = any(isinstance(argument, ast.Starred) for argument in call.args)
    invalid = invalid or any(keyword.arg is None for keyword in call.keywords)
    if invalid:
        return tuple((item.arg, _UNKNOWN) for item in parameters)

    source_names = dict(name_facts)

    def compare_literals(operator, left, right):
        if left is _UNKNOWN or right is _UNKNOWN:
            return _UNKNOWN
        if isinstance(operator, ast.Eq):
            return left == right
        if isinstance(operator, ast.NotEq):
            return left != right
        if isinstance(operator, (ast.Is, ast.IsNot)):
            if (type(left) not in (bool, type(None))
                    or type(right) not in (bool, type(None))):
                return _UNKNOWN
            if isinstance(operator, ast.Is):
                return left is right
            return left is not right
        if (isinstance(operator, (ast.In, ast.NotIn))
                and type(right) is tuple
                and type(left) in (str, int, bool, type(None), tuple)):
            matched = left in right
            return not matched if isinstance(operator, ast.NotIn) else matched
        return _UNKNOWN

    def literal(node):
        if isinstance(node, ast.Constant) and type(node.value) in (
                str, int, bool, type(None)):
            return node.value
        if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.Not):
            value = literal(node.operand)
            if value is not _UNKNOWN:
                return not value
        if (isinstance(node, ast.UnaryOp)
                and isinstance(node.op, (ast.UAdd, ast.USub))):
            value = literal(node.operand)
            if type(value) in (int, bool):
                return +value if isinstance(node.op, ast.UAdd) else -value
        if isinstance(node, ast.BoolOp) and node.values:
            is_and = isinstance(node.op, ast.And)
            value = literal(node.values[0])
            if value is _UNKNOWN:
                return _UNKNOWN
            for operand in node.values[1:]:
                if is_and and not value:
                    return value
                if not is_and and value:
                    return value
                value = literal(operand)
                if value is _UNKNOWN:
                    return _UNKNOWN
            return value
        if isinstance(node, ast.IfExp):
            test = literal(node.test)
            if test is _UNKNOWN or type(test) not in (
                    str, int, bool, type(None), tuple):
                return _UNKNOWN
            return literal(node.body if test else node.orelse)
        if (isinstance(node, ast.Compare) and node.ops
                and len(node.ops) == len(node.comparators)):
            left = literal(node.left)
            if left is _UNKNOWN:
                return _UNKNOWN
            for operator, expression in zip(node.ops, node.comparators):
                right = literal(expression)
                matched = compare_literals(operator, left, right)
                if matched is _UNKNOWN or not matched:
                    return matched
                left = right
            return True
        if isinstance(node, ast.Name):
            return source_names.get(node.id, _UNKNOWN)
        if isinstance(node, ast.Tuple):
            items = tuple(literal(item) for item in node.elts)
            return items if all(item is not _UNKNOWN for item in items) else _UNKNOWN
        return _UNKNOWN

    assigned = set()
    if len(call.args) > len(positional):
        invalid = True
    else:
        for parameter, argument in zip(positional, call.args):
            values[parameter.arg] = literal(argument)
            assigned.add(parameter.arg)

    legal_keyword_names = {
        item.arg for item in function.args.args
    } | {item.arg for item in keyword_only}
    if bound_method and function.args.args and parameters:
        # A receiver is positional-only for this binding operation and must not
        # be treated as an explicit user keyword.
        legal_keyword_names.discard(function.args.args[0].arg)
    for keyword in call.keywords:
        if (keyword.arg in values and keyword.arg in legal_keyword_names
                and keyword.arg not in assigned):
            values[keyword.arg] = literal(keyword.value)
            assigned.add(keyword.arg)
        else:
            invalid = True

    positional_defaults = function.args.defaults
    default_start = len(all_positional) - len(positional_defaults)
    for index, default in enumerate(positional_defaults, default_start):
        name = all_positional[index].arg
        if name in values and name not in assigned:
            values[name] = literal(default)
    for parameter, default in zip(keyword_only, function.args.kw_defaults):
        if parameter.arg not in assigned and default is not None:
            values[parameter.arg] = literal(default)

    # Unsupported call shapes never retain guessed values.
    if invalid:
        values = {item.arg: _UNKNOWN for item in parameters}
    return tuple((item.arg, values[item.arg]) for item in parameters)


def _module_init_call_candidate_closure(files, roots=ROOTS, *,
                                        known_call_facts=(), known_name_facts=None,
                                        trusted_function_name_facts=None,
                                        preserve_name_facts_after_star=None,
                                        trusted_line_facts=None,
                                        trusted_condition_observations=None,
                                        trusted_empty_for_facts=None,
                                        unknown_conditions=None,
                                        resolved_conditions=None):
    if type(files) is not dict or type(roots) is not tuple:
        raise ValueError("SOURCE_INPUT_TYPE")
    if (trusted_empty_for_facts is not None
            and (type(trusted_empty_for_facts) is not dict
                 or any(type(module) is not str or type(facts) is not dict
                        for module, facts in trusted_empty_for_facts.items()))):
        raise ValueError("UNTRUSTED_EMPTY_FOR_FACT")
    if (trusted_condition_observations is not None
            and (type(trusted_condition_observations) is not dict
                 or any(type(key) is not tuple or len(key) != 3
                        or type(key[0]) is not str or type(key[1]) is not str
                        or type(key[2]) is not int or type(values) is not tuple
                        or not values or any(type(value) is not bool for value in values)
                        or len(set(values)) != len(values)
                        for key, values in trusted_condition_observations.items()))):
        raise ValueError("UNTRUSTED_CONDITION_OBSERVATION")
    if any(type(name) is not str for name in roots) or len(set(roots)) != len(roots):
        raise ValueError("SOURCE_ROOTS")
    lexical_modules, _, _ = _candidate_closure(files, roots)
    module_sources = {}
    function_index = {}
    class_index = {}
    source_class_bases = {}
    class_dispatch_index = {}
    for source_module in lexical_modules:
        source_path = _module_path(source_module, files)
        if source_path is None:
            continue
        source_tree = ast.parse(files[source_path], filename=source_path)
        module_sources[source_module] = (source_path, source_tree)
        function_index[source_module] = _top_level_function_index(source_tree)
        class_index[source_module] = _top_level_class_method_index(source_tree)
    for source_module, (source_path, source_tree) in module_sources.items():
        class_bases = _top_level_class_base_index(source_tree)
        imported_classes = _imported_class_aliases(
            source_tree, source_module, source_path, class_index
        )
        imported_modules = _imported_module_aliases(
            source_tree, source_module, source_path, function_index
        )
        module_bases = {}
        for class_name, base_names in class_bases.items():
            resolved = []
            for base_name in base_names:
                candidates = []
                if base_name in class_index[source_module]:
                    candidates.append((source_module, base_name))
                candidates.extend(imported_classes.get(base_name, ()))
                if "." in base_name:
                    receiver, _, imported_name = base_name.rpartition(".")
                    candidates.extend(
                        (target_module, imported_name)
                        for target_module in imported_modules.get(receiver, ())
                        if imported_name in class_index.get(target_module, {})
                    )
                for candidate in candidates:
                    if candidate not in resolved:
                        resolved.append(candidate)
            module_bases[class_name] = tuple(resolved)
        source_class_bases[source_module] = module_bases

    for source_module, classes in class_index.items():
        module_dispatch = {}
        for class_name in classes:
            pending_classes = [(source_module, class_name)]
            seen_classes = set()
            methods = {}
            while pending_classes:
                candidate_module, candidate_class = pending_classes.pop()
                candidate = (candidate_module, candidate_class)
                if candidate in seen_classes:
                    continue
                seen_classes.add(candidate)
                for method_name in class_index.get(candidate_module, {}).get(
                    candidate_class, {}
                ):
                    owners = methods.setdefault(method_name, [])
                    owner = (candidate_module, candidate_class + "." + method_name)
                    if owner not in owners:
                        owners.append(owner)
                pending_classes.extend(
                    source_class_bases.get(candidate_module, {}).get(candidate_class, ())
                )
            module_dispatch[class_name] = {
                name: tuple(sorted(owners)) for name, owners in methods.items()
            }
        class_dispatch_index[source_module] = module_dispatch

    reached = set()
    initialized = set()
    processed_entries = set()
    pending = [(module, None) for module in roots]
    edges = 0
    functions = 0
    conditions = {"resolved": 0, "unknown": 0}
    call_condition_observations = {}
    emitted_call_import_sites = set()
    visited_functions = set()
    while pending:
        module, entry_function = pending.pop()
        source = module_sources.get(module)
        if source is None:
            continue
        path, tree = source
        if entry_function is None:
            if module in initialized:
                continue
            initialized.add(module)
            reached.add(module)
            run_module = True
            entries = ()
        else:
            entry = (module, entry_function)
            if entry in processed_entries:
                continue
            if module not in initialized:
                pending.append((module, entry_function))
                pending.append((module, None))
                continue
            processed_entries.add(entry)
            run_module = False
            entries = (entry_function,)
        imported_functions = _imported_function_aliases(tree, module, path, function_index)
        imported_classes = _imported_class_aliases(tree, module, path, class_index)
        for alias, targets in imported_classes.items():
            for target_module, class_name in targets:
                constructors = class_dispatch_index.get(target_module, {}).get(
                    class_name, {}
                ).get("__init__", ())
                if constructors:
                    existing = list(imported_functions.get(alias, ()))
                    for constructor in constructors:
                        target = constructor
                        if target not in existing:
                            existing.append(target)
                    imported_functions[alias] = tuple(existing)
        imported_class_methods = {}
        for alias, targets in imported_classes.items():
            methods = imported_class_methods.setdefault(alias, {})
            for target_module, class_name in targets:
                for method_name, owners in class_dispatch_index.get(
                    target_module, {}
                ).get(class_name, {}).items():
                    method_targets = methods.setdefault(method_name, [])
                    for owner in owners:
                        target = owner
                        if target not in method_targets:
                            method_targets.append(target)
        imported_class_methods = {
            alias: {name: tuple(targets) for name, targets in methods.items()}
            for alias, methods in imported_class_methods.items()
        }
        module_aliases = _imported_module_aliases(tree, module, path, function_index)
        imported_modules = _imported_module_function_aliases(
            module_aliases, function_index, class_dispatch_index
        )
        imported_module_class_methods = _imported_module_class_method_aliases(
            module_aliases, class_dispatch_index
        )
        names, visited_count, imported_calls = _module_init_call_import_names(
            tree, module, path, conditions,
            imported_functions=imported_functions,
            imported_modules=imported_modules,
            imported_class_methods=imported_class_methods,
            imported_module_class_methods=imported_module_class_methods,
            entry_functions=entries,
            run_module=run_module,
            visited_global=visited_functions,
            known_call_facts=known_call_facts,
            known_name_facts=(known_name_facts or {}).get(module, {}),
            trusted_function_name_facts=(trusted_function_name_facts or {}).get(module, {}),
            preserve_name_facts_after_star=(
                (preserve_name_facts_after_star or {}).get(module, ())
            ),
            trusted_line_facts=(trusted_line_facts or {}).get(module, {}),
            trusted_empty_for_facts=(trusted_empty_for_facts or {}).get(module, {}),
            condition_observations=call_condition_observations,
            emitted_import_sites=emitted_call_import_sites,
            unknown_conditions=unknown_conditions,
        )
        functions += visited_count
        for name in names:
            parts = name.split(".")
            candidate = next(
                (".".join(parts[:index]) for index in range(len(parts), 0, -1)
                 if ".".join(parts[:index]) in module_sources),
                None,
            )
            if candidate is not None:
                edges += 1
                if candidate not in initialized:
                    pending.append((candidate, None))
        for target_module, target_function in imported_calls:
            is_function = target_function in function_index.get(target_module, {})
            class_name, separator, method_name = target_function.partition(".")
            is_method = bool(separator) and method_name in class_index.get(target_module, {}).get(class_name, {})
            if is_function or is_method:
                if target_module not in initialized:
                    pending.append((target_module, target_function))
                    pending.append((target_module, None))
                else:
                    pending.append((target_module, target_function))
    conditions = {"resolved": 0, "unknown": 0}
    for (condition_module, condition_path, _), observation in (
            call_condition_observations.items()):
        node = observation["node"]
        decisions = observation["decisions"]
        key = (condition_module, condition_path, node.lineno)
        trusted = (trusted_condition_observations or {}).get(key)
        if trusted is not None and None in decisions:
            trusted_set = set(trusted)
            observed_values = decisions - {None}
            if observed_values.issubset(trusted_set):
                decisions = trusted_set
        is_unknown = None in decisions
        conditions["unknown" if is_unknown else "resolved"] += 1
        if not is_unknown and resolved_conditions is not None:
            resolved_conditions.append({
                "module": condition_module,
                "source_path": condition_path,
                "line": node.lineno,
                "expression": ast.unparse(node.test),
                "decisions": sorted(decisions),
            })
        if is_unknown and unknown_conditions is not None:
            unknown_conditions.append({
                "module": condition_module,
                "source_path": condition_path,
                "line": node.lineno,
                "expression": ast.unparse(node.test),
                "body_imports": _lexical_import_statements(node.body),
                "else_imports": _lexical_import_statements(node.orelse),
                "body_calls": _lexical_call_sites(node.body),
                "else_calls": _lexical_call_sites(node.orelse),
            })
    if resolved_conditions is not None:
        resolved_conditions.sort(key=lambda row: (
            row["module"], row["source_path"], row["line"], row["expression"],
        ))
    rows = []
    for module in sorted(reached):
        path = _module_path(module, files)
        rows.append((module + "\t" + hashlib.sha256(files[path]).hexdigest() + "\n").encode("ascii"))
    return tuple(sorted(reached)), edges, functions, hashlib.sha256(b"".join(rows)).hexdigest(), conditions


def analyze(archive_path, target_pyconfig_path=None, target_no_site=False,
            target_image_config_path=None, target_no_project_base_override=False,
            target_image_save_path=None, target_direct_python312=False,
            target_no_pythonuserbase_override=False):
    (
        files, stdlib_header, frozen_source, bootstrap_setup, stdlib_setup,
        getpath_source, config_c_template, configure_source, ast_asdl,
        ast_c_source, sys_module_c_source, sys_module_clinic_source,
        warnings_c_source, warnings_clinic_source, posix_module_c_source,
        posix_module_clinic_source, pickle_module_c_source,
        thread_native_id_header, thread_native_id_module,
        thread_native_id_pthread, getplatform_source, makefile_pre_source,
        python_import_c_source, preconfig_header_source, long_header_source,
        preconfig_c_source,
        initconfig_c_source,
    ) = _source_archive_data(_archive_bytes(archive_path))
    if stdlib_header is None:
        raise ValueError("STDLIB_MODULE_NAMES_MISSING")
    if frozen_source is None:
        raise ValueError("FROZEN_SOURCE_MISSING")
    if bootstrap_setup is None:
        raise ValueError("BOOTSTRAP_SETUP_MISSING")
    if stdlib_setup is None:
        raise ValueError("STDLIB_SETUP_MISSING")
    if python_import_c_source is None:
        raise ValueError("PYTHON_IMPORT_SOURCE_MISSING")
    zipimport_hook_registration_candidate = (
        _target_zipimport_hook_registration_candidate(python_import_c_source)
    )
    if getpath_source is None:
        raise ValueError("GETPATH_SOURCE_MISSING")
    stdlib_names, stdlib_names_sha256 = _stdlib_module_names(stdlib_header)
    frozen = _frozen_module_inventory(frozen_source)
    bootstrap_setup_inventory = _bootstrap_setup_inventory(bootstrap_setup)
    stdlib_setup_inventory = _stdlib_setup_inventory(stdlib_setup)
    getpath_inventory = _getpath_source_inventory(getpath_source)
    sysconfig_source = files.get("sysconfig.py")
    if sysconfig_source is None:
        raise ValueError("SYSCONFIG_SOURCE_MISSING")
    sysconfig_inventory = _sysconfig_source_inventory(sysconfig_source)
    sysconfig_name_facts = _target_sysconfig_user_base_name_facts(files)
    sysconfig_name_facts.update(_target_sysconfig_no_site_facts(
        files, sys_module_c_source, target_no_site,
    ))
    target_sysconfig_preferred_scheme_membership_line_facts = (
        _target_sysconfig_preferred_scheme_membership_line_facts(
            files, sysconfig_name_facts,
        )
    )
    target_sysconfig_is_python_build_line_facts = (
        _target_sysconfig_is_python_build_line_facts(files)
    )
    target_string_template_pattern_guard_line_facts = (
        _target_string_template_pattern_guard_line_facts(files)
    )
    target_weakrefset_empty_init_line_facts = (
        _target_weakrefset_empty_init_line_facts(files)
    )
    target_copyreg_pickle_callable_line_facts = (
        _target_copyreg_pickle_callable_line_facts(files)
    )
    target_copyreg_constructor_observation_facts = (
        _target_copyreg_constructor_observation_facts(files)
    )
    target_opcode_pseudo_op_condition_facts = (
        _target_opcode_pseudo_op_condition_facts(files)
    )
    target_json_encoder_argument_condition_facts = (
        _target_json_encoder_argument_condition_facts(files)
    )
    target_hashlib_name_condition_facts = (
        _target_hashlib_name_condition_facts(files)
    )
    target_functools_lru_cache_condition_facts = (
        _target_functools_lru_cache_condition_facts(files)
    )
    target_logging_lock_line_facts = _target_logging_lock_line_facts(
        files, thread_native_id_module,
    )
    target_logging_level_line_facts = _target_logging_level_line_facts(files)
    target_logging_style_line_facts = _target_logging_style_line_facts(files)
    target_collections_namedtuple_rename_line_facts = (
        _target_collections_namedtuple_rename_line_facts(files)
    )
    target_collections_namedtuple_string_type_line_facts = (
        _target_collections_namedtuple_string_type_line_facts(files)
    )
    target_collections_namedtuple_call_condition_facts = (
        _target_collections_namedtuple_call_condition_facts(files)
    )
    target_image_config_source = None
    if target_image_config_path is not None:
        with Path(target_image_config_path).open("rb") as stream:
            target_image_config_source = stream.read(MAX_TARGET_IMAGE_CONFIG_BYTES + 1)
        if (len(target_image_config_source) > MAX_TARGET_IMAGE_CONFIG_BYTES
                or hashlib.sha256(target_image_config_source).hexdigest()
                != TARGET_IMAGE_CONFIG_SHA256):
            raise ValueError("TARGET_IMAGE_CONFIG_MISMATCH")
    if target_no_project_base_override and target_image_config_source is None:
        raise ValueError("TARGET_IMAGE_CONFIG_REQUIRED")
    target_image_path_facts = {}
    target_sys_path_candidate_facts = {}
    target_s15_prefixes_field_candidate = {}
    target_s15_paths_field_candidate = None
    target_s15_roots_field_candidate = None
    target_s15_inert_zip_field_candidate = None
    target_s15_files_field_candidate = None
    target_warning_options_empty_for_facts = {}
    target_importlib_optimize_line_facts = {}
    target_worker_sys_flag_facts = ()
    target_s15_flags_field_candidate = None
    target_worker_sysconfigdata_environment_fact = ()
    target_importlib_verbose_line_facts = {}
    worker_source_path = (
        Path(__file__).resolve().parents[2]
        / "Tests" / "Tools" / "dgn007_import_used_bytes_probe.py"
    )
    with worker_source_path.open("rb") as stream:
        worker_source = stream.read(MAX_WORKER_CONTROL_SOURCE_BYTES + 1)
    if len(worker_source) <= MAX_WORKER_CONTROL_SOURCE_BYTES:
        target_importlib_verbose_line_facts = (
            _target_importlib_verbose_line_facts(
                files, preconfig_c_source, initconfig_c_source, worker_source,
            )
        )
        target_warning_options_empty_for_facts = (
            _target_warning_options_empty_for_facts(
                files, preconfig_c_source, initconfig_c_source, worker_source,
            )
        )
        target_worker_sysconfigdata_environment_fact = (
            _target_worker_sysconfigdata_environment_fact(
                preconfig_c_source, initconfig_c_source, worker_source,
            )
        )
        target_worker_sys_flag_facts = _target_worker_sys_flag_facts(
            preconfig_header_source, long_header_source, preconfig_c_source,
            initconfig_c_source,
            sys_module_c_source, worker_source,
        )
        target_s15_flags_field_candidate = (
            _target_s15_flags_field_candidate(target_worker_sys_flag_facts)
        )
        target_importlib_optimize_line_facts = (
            _target_importlib_optimize_line_facts(
                files, preconfig_c_source, initconfig_c_source, worker_source,
            )
        )
    if target_image_save_path is not None:
        if (not target_direct_python312 or not target_no_site
                or not target_no_project_base_override
                or target_image_config_source is None):
            raise ValueError("TARGET_IMAGE_PATH_ASSUMPTIONS_REQUIRED")
        target_image_path_facts = _target_image_save_facts(
            target_image_save_path, target_image_config_source,
        )
        target_sys_path_candidate_facts = _target_image_sys_path_candidate(
            target_image_path_facts, getpath_inventory,
            target_no_site, target_direct_python312,
            target_no_project_base_override,
        )
        target_s15_paths_field_candidate = _target_s15_paths_field_candidate(
            target_sys_path_candidate_facts
        )
        target_s15_roots_field_candidate = _target_s15_roots_field_candidate(
            target_sys_path_candidate_facts
        )
        target_s15_inert_zip_field_candidate = (
            _target_s15_inert_zip_field_candidate(target_sys_path_candidate_facts)
        )
        target_s15_files_field_candidate = _target_s15_files_field_candidate(
            target_sys_path_candidate_facts
        )
        target_s15_prefixes_field_candidate = (
            _target_s15_prefixes_field_candidate(
                target_image_path_facts, getpath_inventory,
                target_sys_path_candidate_facts, initconfig_c_source,
                target_no_site, target_direct_python312,
                target_no_project_base_override,
            )
        )
        sysconfig_name_facts.update({
            "_PYTHON_BUILD": target_image_path_facts["_PYTHON_BUILD"],
        })
    target_hashlib_builtin_fallback_file_candidates = (
        _target_hashlib_builtin_fallback_file_candidates(
            files, target_hashlib_name_condition_facts,
            target_image_path_facts,
        )
    )
    sysconfig_project_base_env_facts = _target_sysconfig_project_base_env_facts(
        files, target_image_config_source, target_no_project_base_override,
    ) if target_image_config_source is not None else ()
    target_sysconfig_userbase_env_condition_facts = (
        _target_sysconfig_userbase_env_condition_facts(
            files, target_image_config_source, target_no_site,
            target_no_pythonuserbase_override,
        ) if target_image_config_source is not None else {}
    )
    target_sysconfig_build_setup_guard_line_facts = (
        _target_sysconfig_build_setup_guard_line_facts(
            files, target_image_path_facts, sysconfig_name_facts,
            sysconfig_project_base_env_facts, target_no_site,
            target_no_project_base_override, target_direct_python312,
        )
    )
    target_sysconfig_venv_prefix_guard_line_facts = (
        _target_sysconfig_venv_prefix_guard_line_facts(
            files, target_s15_prefixes_field_candidate,
        )
    )
    importlib_bootstrap = files.get("importlib/_bootstrap.py")
    importlib_external = files.get("importlib/_bootstrap_external.py")
    if importlib_bootstrap is None or importlib_external is None:
        raise ValueError("IMPORTLIB_SOURCE_MISSING")
    importlib_inventory = _importlib_source_inventory(
        importlib_bootstrap, importlib_external
    )
    machinery_source = files.get("importlib/machinery.py")
    util_source = files.get("importlib/util.py")
    if machinery_source is None or util_source is None:
        raise ValueError("IMPORTLIB_PUBLIC_API_SOURCE_MISSING")
    importlib_api_inventory = _importlib_public_api_inventory(
        machinery_source, util_source
    )
    importlib_finder_registration_candidate = (
        _target_importlib_finder_registration_candidate(files)
    )
    meta_path_finder_class_candidate = (
        _target_meta_path_finder_class_candidate(files)
    )
    target_s15_finders_field_candidate = _target_s15_finders_field_candidate(
        importlib_finder_registration_candidate,
        meta_path_finder_class_candidate,
    )
    filefinder_hook_factory_candidate = (
        _target_filefinder_hook_factory_candidate(files)
    )
    zipimporter_class_source_candidate = (
        _target_zipimporter_class_source_candidate(files)
    )
    target_s15_hooks_field_candidate = _target_s15_hooks_field_candidate(
        importlib_finder_registration_candidate,
        zipimport_hook_registration_candidate,
        filefinder_hook_factory_candidate,
        zipimporter_class_source_candidate,
    )
    runtime_profile_source_path = (
        Path(__file__).resolve().parents[2]
        / "Tests" / "Tools" / "dgn007_import_runtime_profile.py"
    )
    try:
        with runtime_profile_source_path.open("rb") as stream:
            runtime_profile_source = stream.read(
                MAX_DGN007_RUNTIME_PROFILE_SOURCE_BYTES + 1
            )
    except OSError:
        runtime_profile_source = None
    target_s15_assumption_field_candidate = (
        _target_s15_assumption_field_candidate(runtime_profile_source)
    )
    target_s15_installation_schema_candidate = (
        _target_s15_installation_schema_candidate(runtime_profile_source)
    )
    target_controls_selection_contract_candidate = (
        _target_controls_selection_contract_candidate(runtime_profile_source)
    )
    target_selected_profile_shape_contract_candidate = (
        _target_selected_profile_shape_contract_candidate(
            runtime_profile_source,
            target_s15_installation_schema_candidate,
            target_controls_selection_contract_candidate,
        )
    )
    target_selected_shape_primitives_candidate = (
        _target_selected_shape_primitives_candidate(
            runtime_profile_source,
            target_selected_profile_shape_contract_candidate,
        )
    )
    target_selected_namespace_contract_candidate = (
        _target_selected_namespace_contract_candidate(
            runtime_profile_source,
            target_selected_shape_primitives_candidate,
        )
    )
    target_selected_anchor_contract_candidate = (
        _target_selected_anchor_contract_candidate(
            runtime_profile_source,
            target_selected_namespace_contract_candidate,
        )
    )
    target_selected_container_contract_candidate = (
        _target_selected_container_contract_candidate(
            runtime_profile_source,
            target_selected_anchor_contract_candidate,
        )
    )
    target_selected_profile_binder_flow_candidate = (
        _target_selected_profile_binder_flow_candidate(
            runtime_profile_source,
            target_selected_profile_shape_contract_candidate,
        )
    )
    target_selected_profile_anchor_binding_candidate = (
        _target_selected_profile_anchor_binding_candidate(
            runtime_profile_source,
            target_selected_profile_binder_flow_candidate,
        )
    )
    target_selected_profile_observation_flow_candidate = (
        _target_selected_profile_observation_flow_candidate(
            runtime_profile_source,
            target_selected_profile_anchor_binding_candidate,
        )
    )
    target_selected_profile_post_contract_candidate = (
        _target_selected_profile_post_contract_candidate(
            runtime_profile_source,
            target_selected_profile_observation_flow_candidate,
        )
    )
    target_selected_hook_post_contract_candidate = (
        _target_selected_hook_post_contract_candidate(
            runtime_profile_source,
            target_selected_profile_observation_flow_candidate,
        )
    )
    target_filefinder_hook_contract_candidate = (
        _target_filefinder_hook_contract_candidate(
            runtime_profile_source,
            target_selected_profile_observation_flow_candidate,
        )
    )
    target_profile_scalar_projection_contract_candidate = (
        _target_profile_scalar_projection_contract_candidate(
            runtime_profile_source,
            target_filefinder_hook_contract_candidate,
        )
    )
    target_profile_selection_inputs_candidate = (
        _target_profile_selection_inputs_candidate(
            runtime_profile_source,
            target_s15_assumption_field_candidate,
            target_s15_roots_field_candidate,
            target_s15_inert_zip_field_candidate,
            target_controls_selection_contract_candidate,
        )
    )
    target_s15_installation_tuple_candidate = None
    configure_inventory = _configure_template_inventory(
        config_c_template, configure_source
    )
    types_descriptor_call_facts = _target_types_descriptor_call_facts(files)
    ast_compatibility_call_facts = _target_ast_compatibility_call_facts(
        files, ast_asdl, ast_c_source
    )
    sys_getframe_call_facts = _target_sys_getframe_call_facts(
        files, sys_module_c_source, sys_module_clinic_source
    )
    target_collections_namedtuple_module_line_facts = (
        _target_collections_namedtuple_module_line_facts(
            files, sys_module_c_source, sys_module_clinic_source,
        )
    )
    sys_implementation_version_fact = (
        _target_sys_implementation_version_fact(sys_module_c_source)
    )
    target_s15_version_field_candidate = _target_s15_version_field_candidate(
        sys_module_c_source, sys_implementation_version_fact,
    )
    sys_implementation_name_fact = (
        _target_sys_implementation_name_fact(sys_module_c_source)
    )
    target_s15_implementation_field_candidate = (
        _target_s15_implementation_field_candidate(
            sys_module_c_source, sys_implementation_name_fact,
        )
    )
    sys_implementation_cache_tag_fact = (
        _target_sys_implementation_cache_tag_fact(
            sys_module_c_source, sys_implementation_version_fact,
        )
    )
    sys_implementation_multiarch_fact = (
        _target_sys_implementation_multiarch_fact(
            sys_module_c_source, target_image_path_facts,
        )
    )
    sys_abiflags_fact = _target_sys_abiflags_fact(
        sys_module_c_source, target_image_path_facts,
    )
    sys_platform_fact = _target_sys_platform_fact(
        sys_module_c_source, getplatform_source, makefile_pre_source,
        target_image_path_facts,
    )
    target_s15_platform_field_candidate = _target_s15_platform_field_candidate(
        sys_platform_fact, target_image_path_facts,
    )
    target_s15_installation_tuple_candidate = (
        _target_s15_installation_tuple_candidate({
            "assumption": target_s15_assumption_field_candidate,
            "platform": target_s15_platform_field_candidate,
            "implementation": target_s15_implementation_field_candidate,
            "version": target_s15_version_field_candidate,
            "image_paths": target_sys_path_candidate_facts,
            "prefixes": target_s15_prefixes_field_candidate,
            "paths": target_s15_paths_field_candidate,
            "roots": target_s15_roots_field_candidate,
            "inert_zip": target_s15_inert_zip_field_candidate,
            "flags": target_s15_flags_field_candidate,
            "finders": target_s15_finders_field_candidate,
            "hooks": target_s15_hooks_field_candidate,
            "files": target_s15_files_field_candidate,
            "schema": target_s15_installation_schema_candidate,
        })
    )
    target_profile_scalar_projection_schema_candidate = (
        _target_profile_scalar_projection_schema_candidate(
            runtime_profile_source,
            target_profile_selection_inputs_candidate,
            target_s15_installation_tuple_candidate,
        )
    )
    target_current_scalar_observation_flow_candidate = (
        _target_current_scalar_observation_flow_candidate(
            runtime_profile_source,
            target_profile_scalar_projection_schema_candidate,
        )
    )
    target_fresh_record_capture_flow_candidate = (
        _target_fresh_record_capture_flow_candidate(runtime_profile_source)
    )
    target_profile_capture_schema_candidate = (
        _target_profile_capture_schema_candidate(runtime_profile_source)
    )
    target_profile_module_record_builder_candidate = (
        _target_profile_module_record_builder_candidate(
            runtime_profile_source,
            target_profile_capture_schema_candidate,
        )
    )
    target_profile_compare_contract_candidate = (
        _target_profile_compare_contract_candidate(
            runtime_profile_source,
            target_profile_module_record_builder_candidate,
        )
    )
    target_profile_validation_report_flow_candidate = (
        _target_profile_validation_report_flow_candidate(
            runtime_profile_source,
            target_profile_compare_contract_candidate,
        )
    )
    target_profile_shape_contract_candidate = (
        _target_profile_shape_contract_candidate(
            runtime_profile_source,
            target_profile_compare_contract_candidate,
            target_profile_capture_schema_candidate,
        )
    )
    target_profile_record_validators_candidate = (
        _target_profile_record_validators_candidate(
            runtime_profile_source,
            target_profile_shape_contract_candidate,
        )
    )
    target_profile_path_contract_candidate = (
        _target_profile_path_contract_candidate(
            runtime_profile_source,
            target_profile_record_validators_candidate,
        )
    )
    target_profile_primitive_validators_candidate = (
        _target_profile_primitive_validators_candidate(
            runtime_profile_source,
            target_profile_path_contract_candidate,
        )
    )
    target_profile_failure_primitive_candidate = (
        _target_profile_failure_primitive_candidate(
            runtime_profile_source,
            target_profile_primitive_validators_candidate,
        )
    )
    target_profile_report_schema_candidate = (
        _target_profile_report_schema_candidate(
            runtime_profile_source,
            target_profile_failure_primitive_candidate,
        )
    )
    target_profile_model_schemas_candidate = (
        _target_profile_model_schemas_candidate(
            runtime_profile_source,
            target_profile_report_schema_candidate,
        )
    )
    target_profile_record_model_schemas_candidate = (
        _target_profile_record_model_schemas_candidate(
            runtime_profile_source,
            target_profile_model_schemas_candidate,
        )
    )
    target_profile_result_model_schemas_candidate = (
        _target_profile_result_model_schemas_candidate(
            runtime_profile_source,
            target_profile_record_model_schemas_candidate,
        )
    )
    target_selected_profile_result_schemas_candidate = (
        _target_selected_profile_result_schemas_candidate(
            runtime_profile_source,
            target_profile_result_model_schemas_candidate,
        )
    )
    target_profile_record_observation_flow_candidate = (
        _target_profile_record_observation_flow_candidate(
            runtime_profile_source,
            target_profile_result_model_schemas_candidate,
        )
    )
    sysconfigdata_module_name_fact = _target_sysconfigdata_module_name_fact(
        sysconfig_inventory, sys_abiflags_fact, sys_platform_fact,
        sys_implementation_multiarch_fact,
        target_worker_sysconfigdata_environment_fact,
    )
    sysconfigdata_image_file_fact = _target_sysconfigdata_image_file_fact(
        sysconfigdata_module_name_fact, target_image_path_facts,
    )
    sysconfigdata_import_target_candidate = (
        _target_sysconfigdata_import_target_candidate(
            sysconfig_inventory, sysconfigdata_module_name_fact,
            sysconfigdata_image_file_fact,
        )
    )
    warnings_default_call_facts = _target_warnings_default_call_facts(
        files, warnings_c_source, warnings_clinic_source
    )
    os_name_facts = _target_os_posix_name_facts(
        files, posix_module_c_source, posix_module_clinic_source
    )
    os_name_facts.update(_target_os_posix_boolean_assignment_facts(
        files, posix_module_c_source, posix_module_clinic_source
    ))
    os_name_call_facts = (
        (("os.name", os_name_facts["name"]),)
        if type(os_name_facts.get("name")) is str else ()
    )
    target_sysconfig_posix_init_line_facts = (
        _target_sysconfig_posix_init_line_facts(files, os_name_call_facts)
    )
    target_sysconfig_lazy_initialization_call_candidate = (
        _target_sysconfig_lazy_initialization_call_candidate(files)
    )
    target_sysconfig_reinitialization_candidate = (
        _target_sysconfig_reinitialization_candidate(files)
    )
    target_sysconfig_public_config_value_flow_candidate = (
        _target_sysconfig_public_config_value_flow_candidate(files)
    )
    target_sysconfig_post_update_entries_candidate = (
        _target_sysconfig_post_update_entries_candidate(
            files, target_sysconfig_posix_init_line_facts,
            sys_platform_fact, target_image_path_facts,
        )
    )
    target_sysconfig_initialization_complete_flag_candidate = (
        _target_sysconfig_initialization_complete_flag_candidate(
            files, target_sysconfig_posix_init_line_facts,
        )
    )
    sysconfigdata_initialization_route_candidate = (
        _target_sysconfigdata_initialization_route_candidate(
            sysconfig_inventory,
            target_sysconfig_lazy_initialization_call_candidate,
            target_sysconfig_reinitialization_candidate,
            target_sysconfig_public_config_value_flow_candidate,
            target_sysconfig_post_update_entries_candidate,
            target_sysconfig_initialization_complete_flag_candidate,
            target_sysconfig_posix_init_line_facts,
            sysconfigdata_import_target_candidate, target_image_path_facts,
        )
    )
    os_function_name_facts = (
        {"supports_bytes_environ": True}
        if os_name_facts.get("supports_bytes_environ") is True
        and _target_os_function_name_facts_safe(
            files, {"supports_bytes_environ": True}
        ) else {}
    )
    os_createenviron_line_facts = _target_os_createenviron_line_facts(
        files, os_name_facts,
    ) if os_name_facts else {}
    codecs_false_guard_line_facts = _target_codecs_false_guard_line_facts(files)
    pickle_buffer_line_facts = _target_pickle_buffer_line_facts(
        files, pickle_module_c_source, target_image_path_facts,
    ) if target_image_path_facts else {}
    os_fspath_call_facts = _target_os_fspath_call_facts(
        files, posix_module_c_source, posix_module_clinic_source
    )
    os_have_functions_call_facts = _target_os_have_functions_call_facts(
        files, posix_module_c_source, posix_module_clinic_source
    )
    target_pyconfig_source = None
    if target_pyconfig_path is not None:
        with Path(target_pyconfig_path).open("rb") as stream:
            target_pyconfig_source = stream.read(MAX_TARGET_PYCONFIG_BYTES + 1)
        if (len(target_pyconfig_source) > MAX_TARGET_PYCONFIG_BYTES
                or hashlib.sha256(target_pyconfig_source).hexdigest()
                != TARGET_PYCONFIG_SHA256):
            raise ValueError("TARGET_PYCONFIG_MISMATCH")
    posix_build_call_facts = _target_posix_build_call_facts(
        files, posix_module_c_source, posix_module_clinic_source,
        target_pyconfig_source,
    ) if target_pyconfig_source is not None else ()
    target_os_feature_add_condition_facts = (
        _target_os_feature_add_condition_facts(
            files, posix_module_c_source, posix_module_clinic_source,
            target_pyconfig_source,
        ) if target_pyconfig_source is not None else {}
    )
    os_descriptor_support_facts = _target_os_descriptor_support_facts(
        files, posix_module_c_source, posix_module_clinic_source,
        target_pyconfig_source,
    ) if target_pyconfig_source is not None else ()
    threading_os_alias_call_facts = _target_threading_os_alias_facts(files)
    if not any(fact[0] == "hasattr(os, 'register_at_fork')"
               for fact in posix_build_call_facts):
        threading_os_alias_call_facts = ()
    threading_native_id_facts = (
        _target_threading_native_id_name_facts(
            files, thread_native_id_header, thread_native_id_module,
            thread_native_id_pthread, target_pyconfig_source,
        ) if target_pyconfig_source is not None else {}
    )
    threading_crlock_facts = _target_threading_crlock_name_fact(
        files, thread_native_id_module, target_pyconfig_source,
    ) if target_pyconfig_source is not None else {}
    threading_call_name_facts = dict(threading_native_id_facts)
    threading_call_name_facts.update(threading_crlock_facts)
    threading_function_name_facts = (
        threading_call_name_facts
        if _target_threading_native_id_function_fact_safe(
            files, threading_call_name_facts
        ) else {}
    )
    threading_main_constructor_line_facts = (
        _target_threading_main_constructor_line_facts(files)
    )
    threading_condition_lock_line_facts = (
        _target_threading_condition_lock_line_facts(
            files, thread_native_id_module,
        )
    )
    target_imported_name_safe_modules = tuple(sorted(
        module for module in ("ast", "dis", "difflib", "getopt", "heapq",
                              "inspect", "os", "pickle", "sysconfig",
                              "textwrap", "tokenize")
        if (_target_imported_name_star_imports_safe(files, module)
            or module == "ast" and _target_ast_imported_name_star_import_safe(
                files, ast_c_source
            )
            or module == "inspect" and _target_inspect_imported_name_safe(files)
            or module == "sysconfig" and _target_sysconfig_imported_name_safe(files)
            or _target_plain_main_guard_name_safe(files, module)
            or module == "os" and bool(os_name_facts))
    ))
    target_call_facts = tuple(sorted(
        types_descriptor_call_facts + ast_compatibility_call_facts
        + sys_getframe_call_facts + tuple(warnings_default_call_facts.items())
        + sys_implementation_version_fact
        + sys_implementation_name_fact
        + sys_implementation_cache_tag_fact
        + sys_implementation_multiarch_fact
        + sys_abiflags_fact
        + sys_platform_fact
        + target_worker_sys_flag_facts
        + os_fspath_call_facts + os_have_functions_call_facts
        + posix_build_call_facts + os_descriptor_support_facts
        + threading_os_alias_call_facts + sysconfig_project_base_env_facts
        + os_name_call_facts
        + _target_importlib_case_platform_facts(files)
    ))
    if target_image_path_facts:
        target_call_facts += (("sys.executable", True),)
    if target_importlib_optimize_line_facts:
        target_call_facts += (("sys.flags.optimize == 0", True),)
        target_call_facts += _target_importlib_debug_call_facts(
            target_importlib_optimize_line_facts,
        )
    modules, edges, rows_sha256 = _candidate_closure(files)
    module_body, module_body_edges, module_body_sha256 = _module_body_candidate_closure(files)
    target_unknown_conditions = []
    target_name_facts = {
        "warnings": warnings_default_call_facts,
        "os": os_name_facts,
        "threading": threading_call_name_facts,
        "sysconfig": sysconfig_name_facts,
    }
    target_call_name_facts = {
        module: dict(facts) for module, facts in target_name_facts.items()
    }
    for module in target_imported_name_safe_modules:
        target_call_name_facts.setdefault(module, {})[
            "__name__"
        ] = _IMPORTED_MODULE_NAME
    importlib_windows_name_facts = _target_importlib_windows_name_facts(files)
    if importlib_windows_name_facts:
        target_call_name_facts.setdefault("importlib._bootstrap_external", {}).update(
            importlib_windows_name_facts
        )
    target_platform, target_edges, target_sha256, target_conditions = (
        _target_platform_candidate_closure(
            files, unknown_conditions=target_unknown_conditions,
            known_call_facts=target_call_facts,
            known_name_facts=target_name_facts,
            preserve_imported_name_modules=target_imported_name_safe_modules,
        )
    )
    target_unknown_conditions_sha256 = hashlib.sha256(
        json.dumps(
            target_unknown_conditions, ensure_ascii=False, sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
    ).hexdigest()
    call_modules, call_edges, call_functions, call_sha256, call_conditions = (
        _module_init_call_candidate_closure(files)
    )
    target_threading_sys_excepthook_line_facts = (
        _target_threading_sys_excepthook_line_facts(
            files, call_modules, threading_condition_lock_line_facts,
            sys_module_c_source, sys_module_clinic_source,
        )
    )
    target_call_unknown_conditions = []
    target_call_resolved_conditions = []
    (target_call_modules, target_call_edges, target_call_functions,
     target_call_sha256, target_call_conditions) = _module_init_call_candidate_closure(
        files, known_call_facts=target_call_facts,
        known_name_facts=target_call_name_facts,
        trusted_function_name_facts={module: facts for module, facts in {
            "threading": threading_function_name_facts,
            "os": os_function_name_facts,
        }.items() if facts},
        preserve_name_facts_after_star={
            "os": tuple(os_name_facts),
        } if os_name_facts else {},
        trusted_line_facts={
            "os": os_createenviron_line_facts,
            "codecs": codecs_false_guard_line_facts,
            "pickle": pickle_buffer_line_facts,
            "threading": {
                **threading_main_constructor_line_facts,
                **threading_condition_lock_line_facts,
                **target_threading_sys_excepthook_line_facts,
            },
            "sysconfig": {
                **target_sysconfig_is_python_build_line_facts,
                **target_sysconfig_build_setup_guard_line_facts,
                **target_sysconfig_venv_prefix_guard_line_facts,
                **target_sysconfig_preferred_scheme_membership_line_facts,
                **target_sysconfig_posix_init_line_facts,
            },
            "string": target_string_template_pattern_guard_line_facts,
            "_weakrefset": target_weakrefset_empty_init_line_facts,
            "copyreg": target_copyreg_pickle_callable_line_facts,
            "logging": {
                **target_logging_lock_line_facts,
                **target_logging_level_line_facts,
            },
            "collections": {
                **target_collections_namedtuple_rename_line_facts,
                **target_collections_namedtuple_string_type_line_facts,
                **target_collections_namedtuple_module_line_facts,
            },
            "importlib._bootstrap_external": target_importlib_optimize_line_facts,
            "importlib._bootstrap": target_importlib_verbose_line_facts,
        } if (os_createenviron_line_facts or codecs_false_guard_line_facts
              or pickle_buffer_line_facts
              or threading_main_constructor_line_facts
              or target_sysconfig_is_python_build_line_facts
              or target_sysconfig_posix_init_line_facts
              or target_string_template_pattern_guard_line_facts
              or target_weakrefset_empty_init_line_facts
              or target_copyreg_pickle_callable_line_facts
              or target_logging_lock_line_facts
              or target_logging_level_line_facts
              or threading_condition_lock_line_facts
              or target_threading_sys_excepthook_line_facts
              or target_collections_namedtuple_rename_line_facts
              or target_collections_namedtuple_string_type_line_facts
              or target_collections_namedtuple_module_line_facts
              or target_sysconfig_build_setup_guard_line_facts
              or target_sysconfig_venv_prefix_guard_line_facts
              or target_sysconfig_preferred_scheme_membership_line_facts
              or target_importlib_optimize_line_facts
              or target_importlib_verbose_line_facts) else {},
        trusted_condition_observations={
            **target_copyreg_constructor_observation_facts,
            **target_opcode_pseudo_op_condition_facts,
            **target_json_encoder_argument_condition_facts,
            **target_hashlib_name_condition_facts,
            **target_functools_lru_cache_condition_facts,
            **target_collections_namedtuple_call_condition_facts,
            **target_sysconfig_userbase_env_condition_facts,
            **target_os_feature_add_condition_facts,
            **target_logging_style_line_facts,
        },
        trusted_empty_for_facts={
            "warnings": target_warning_options_empty_for_facts.get("warnings", {}),
        } if target_warning_options_empty_for_facts else {},
        unknown_conditions=target_call_unknown_conditions,
        resolved_conditions=target_call_resolved_conditions,
    )
    target_call_unknown_conditions.sort(
        key=lambda row: (row["module"], row["source_path"], row["line"], row["expression"])
    )
    target_call_unknown_conditions_sha256 = hashlib.sha256(json.dumps(
        target_call_unknown_conditions, ensure_ascii=False, sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")).hexdigest()
    target_re_compile_input_candidates = _target_re_compile_input_candidates(
        files, target_call_modules,
    )
    target_re_compile_tokenizer_input_type_candidates = (
        _target_re_compile_tokenizer_input_type_candidates(
            files, target_call_modules,
        )
    )
    call_roots = {name.partition(".")[0] for name in call_modules}
    call_roots_outside_stdlib = tuple(sorted(call_roots - set(stdlib_names)))
    frozen_roots = {
        name.partition(".")[0]
        for name in (*frozen["bootstrap_names"], *frozen["stdlib_names"])
    }
    frozen_roots_outside_stdlib = tuple(sorted(frozen_roots - set(stdlib_names)))
    return {
        "archive_sha256": ARCHIVE_SHA256,
        "source_stdlib_module_names_count": len(stdlib_names),
        "source_stdlib_module_names_sha256": stdlib_names_sha256,
        "frozen_source_sha256": FROZEN_SOURCE_SHA256,
        "frozen_bootstrap_name_count": len(frozen["bootstrap_names"]),
        "frozen_bootstrap_names": list(frozen["bootstrap_names"]),
        "frozen_bootstrap_names_sha256": frozen["bootstrap_sha256"],
        "frozen_stdlib_name_count": len(frozen["stdlib_names"]),
        "frozen_stdlib_names": list(frozen["stdlib_names"]),
        "frozen_stdlib_names_sha256": frozen["stdlib_sha256"],
        "frozen_test_name_count": len(frozen["test_names"]),
        "frozen_test_names_sha256": frozen["test_sha256"],
        "frozen_alias_count": len(frozen["aliases"]),
        "frozen_alias_rows": [list(row) for row in frozen["aliases"]],
        "frozen_aliases_sha256": frozen["aliases_sha256"],
        "target_platform_frozen_name_candidates": sorted(
            set(target_platform) & set(frozen["bootstrap_names"] + frozen["stdlib_names"])
        ),
        "module_init_call_frozen_name_candidates": sorted(
            set(call_modules) & set(frozen["bootstrap_names"] + frozen["stdlib_names"])
        ),
        "frozen_runtime_roots_outside_source_stdlib_names": list(
            frozen_roots_outside_stdlib
        ),
        "bootstrap_setup_name_count": bootstrap_setup_inventory["name_count"],
        "bootstrap_setup_conditional_name_count": bootstrap_setup_inventory[
            "conditional_name_count"
        ],
        "bootstrap_setup_source_sha256": bootstrap_setup_inventory["source_sha256"],
        "bootstrap_setup_rows_sha256": bootstrap_setup_inventory["rows_sha256"],
        "bootstrap_setup_conditional_names": [
            list(row) for row in bootstrap_setup_inventory["conditional_names"]
        ],
        "stdlib_setup_entry_count": stdlib_setup_inventory["stdlib_entry_count"],
        "stdlib_setup_test_entry_count": stdlib_setup_inventory["test_entry_count"],
        "stdlib_setup_condition_count": stdlib_setup_inventory["condition_count"],
        "stdlib_setup_source_sha256": stdlib_setup_inventory["source_sha256"],
        "stdlib_setup_rows_sha256": stdlib_setup_inventory["rows_sha256"],
        "stdlib_setup_names_sha256": stdlib_setup_inventory["stdlib_names_sha256"],
        "stdlib_setup_test_names_sha256": stdlib_setup_inventory[
            "test_names_sha256"
        ],
        "getpath_source_sha256": getpath_inventory["source_sha256"],
        "getpath_source_bytes": getpath_inventory["source_bytes"],
        "getpath_path_variable_count": getpath_inventory["path_variable_count"],
        "getpath_path_variables": list(getpath_inventory["path_variables"]),
        "getpath_posix_zip_landmark_template": getpath_inventory[
            "posix_zip_landmark_template"
        ],
        "getpath_posix_stdlib_landmark_template": getpath_inventory[
            "posix_stdlib_landmark_template"
        ],
        "getpath_posix_platstdlib_landmark_template": getpath_inventory[
            "posix_platstdlib_landmark_template"
        ],
        "getpath_posix_default_path_append_order": list(
            getpath_inventory["posix_default_path_append_order"]
        ),
        "getpath_path_variables_sha256": getpath_inventory[
            "path_variables_sha256"
        ],
        "getpath_config_key_count": getpath_inventory["config_key_count"],
        "getpath_config_keys": list(getpath_inventory["config_keys"]),
        "getpath_config_keys_sha256": getpath_inventory[
            "config_keys_sha256"
        ],
        "sysconfig_source_sha256": sysconfig_inventory["source_sha256"],
        "sysconfig_source_bytes": sysconfig_inventory["source_bytes"],
        "sysconfig_install_scheme_count": sysconfig_inventory["scheme_count"],
        "sysconfig_install_scheme_names": list(
            sysconfig_inventory["scheme_names"]
        ),
        "sysconfig_scheme_names_sha256": sysconfig_inventory[
            "scheme_names_sha256"
        ],
        "sysconfig_path_key_count": sysconfig_inventory["path_key_count"],
        "sysconfig_path_keys": list(sysconfig_inventory["path_keys"]),
        "sysconfig_path_keys_sha256": sysconfig_inventory["path_keys_sha256"],
        "sysconfig_path_template_row_count": sysconfig_inventory[
            "path_template_row_count"
        ],
        "sysconfig_path_templates_sha256": sysconfig_inventory[
            "path_templates_sha256"
        ],
        "sysconfig_required_function_count": sysconfig_inventory[
            "required_function_count"
        ],
        "sysconfig_required_functions_sha256": sysconfig_inventory[
            "required_functions_sha256"
        ],
        "sysconfigdata_override_key": sysconfig_inventory[
            "sysconfigdata_override_key"
        ],
        "sysconfigdata_name_template": sysconfig_inventory[
            "sysconfigdata_name_template"
        ],
        "target_platform_sysconfigdata_module_name_fact": list(
            sysconfigdata_module_name_fact
        ),
        "target_platform_sysconfigdata_image_file_fact": list(
            sysconfigdata_image_file_fact
        ),
        "target_platform_sysconfigdata_import_target_candidate": (
            sysconfigdata_import_target_candidate
        ),
        "target_platform_sysconfigdata_initialization_route_candidate": (
            sysconfigdata_initialization_route_candidate
        ),
        "target_platform_sysconfigdata_lazy_initialization_call_candidate": (
            target_sysconfig_lazy_initialization_call_candidate
        ),
        "target_platform_sysconfigdata_reinitialization_candidate": (
            target_sysconfig_reinitialization_candidate
        ),
        "target_platform_sysconfigdata_public_config_value_flow_candidate": (
            target_sysconfig_public_config_value_flow_candidate
        ),
        "target_platform_sysconfigdata_post_update_entries_candidate": (
            target_sysconfig_post_update_entries_candidate
        ),
        "target_platform_sysconfigdata_initialization_complete_flag_candidate": (
            target_sysconfig_initialization_complete_flag_candidate
        ),
        "sysconfigdata_importer": sysconfig_inventory["sysconfigdata_importer"],
        "sysconfigdata_imported_attribute": sysconfig_inventory[
            "sysconfigdata_imported_attribute"
        ],
        "importlib_module_spec_field_count": importlib_inventory[
            "module_spec_field_count"
        ],
        "importlib_module_spec_fields": list(importlib_inventory[
            "module_spec_fields"
        ]),
        "importlib_module_spec_fields_sha256": importlib_inventory[
            "module_spec_fields_sha256"
        ],
        "importlib_builtin_frozen_importer_count": importlib_inventory[
            "builtin_frozen_importer_count"
        ],
        "importlib_loader_finder_class_count": importlib_inventory[
            "loader_finder_class_count"
        ],
        "importlib_bootstrap_method_count": importlib_inventory[
            "bootstrap_method_count"
        ],
        "importlib_bootstrap_methods_sha256": importlib_inventory[
            "bootstrap_methods_sha256"
        ],
        "importlib_builtin_frozen_methods_sha256": importlib_inventory[
            "builtin_frozen_methods_sha256"
        ],
        "importlib_loader_finder_methods_sha256": importlib_inventory[
            "loader_finder_methods_sha256"
        ],
        "importlib_public_api_row_count": importlib_api_inventory["row_count"],
        "importlib_public_api_rows_sha256": importlib_api_inventory[
            "rows_sha256"
        ],
        "importlib_machinery_export_count": importlib_api_inventory[
            "machinery_export_count"
        ],
        "importlib_util_export_count": importlib_api_inventory[
            "util_export_count"
        ],
        "target_importlib_finder_registration_candidate": (
            importlib_finder_registration_candidate
        ),
        "target_meta_path_finder_class_candidate": (
            meta_path_finder_class_candidate
        ),
        "target_s15_finders_field_candidate": (
            target_s15_finders_field_candidate
        ),
        "target_filefinder_hook_factory_candidate": (
            filefinder_hook_factory_candidate
        ),
        "target_zipimporter_class_source_candidate": (
            zipimporter_class_source_candidate
        ),
        "target_zipimport_hook_registration_candidate": (
            zipimport_hook_registration_candidate
        ),
        "target_s15_hooks_field_candidate": target_s15_hooks_field_candidate,
        "target_s15_assumption_field_candidate": (
            target_s15_assumption_field_candidate
        ),
        "target_s15_installation_schema_candidate": (
            target_s15_installation_schema_candidate
        ),
        "target_controls_selection_contract_candidate": (
            target_controls_selection_contract_candidate
        ),
        "target_selected_profile_shape_contract_candidate": (
            target_selected_profile_shape_contract_candidate
        ),
        "target_selected_shape_primitives_candidate": (
            target_selected_shape_primitives_candidate
        ),
        "target_selected_namespace_contract_candidate": (
            target_selected_namespace_contract_candidate
        ),
        "target_selected_anchor_contract_candidate": (
            target_selected_anchor_contract_candidate
        ),
        "target_selected_container_contract_candidate": (
            target_selected_container_contract_candidate
        ),
        "target_selected_profile_binder_flow_candidate": (
            target_selected_profile_binder_flow_candidate
        ),
        "target_selected_profile_anchor_binding_candidate": (
            target_selected_profile_anchor_binding_candidate
        ),
        "target_selected_profile_observation_flow_candidate": (
            target_selected_profile_observation_flow_candidate
        ),
        "target_selected_profile_post_contract_candidate": (
            target_selected_profile_post_contract_candidate
        ),
        "target_selected_hook_post_contract_candidate": (
            target_selected_hook_post_contract_candidate
        ),
        "target_filefinder_hook_contract_candidate": (
            target_filefinder_hook_contract_candidate
        ),
        "target_profile_scalar_projection_contract_candidate": (
            target_profile_scalar_projection_contract_candidate
        ),
        "target_profile_selection_inputs_candidate": (
            target_profile_selection_inputs_candidate
        ),
        "target_profile_scalar_projection_schema_candidate": (
            target_profile_scalar_projection_schema_candidate
        ),
        "target_current_scalar_observation_flow_candidate": (
            target_current_scalar_observation_flow_candidate
        ),
        "target_fresh_record_capture_flow_candidate": (
            target_fresh_record_capture_flow_candidate
        ),
        "target_profile_capture_schema_candidate": (
            target_profile_capture_schema_candidate
        ),
        "target_profile_module_record_builder_candidate": (
            target_profile_module_record_builder_candidate
        ),
        "target_profile_compare_contract_candidate": (
            target_profile_compare_contract_candidate
        ),
        "target_profile_validation_report_flow_candidate": (
            target_profile_validation_report_flow_candidate
        ),
        "target_profile_shape_contract_candidate": (
            target_profile_shape_contract_candidate
        ),
        "target_profile_record_validators_candidate": (
            target_profile_record_validators_candidate
        ),
        "target_profile_path_contract_candidate": (
            target_profile_path_contract_candidate
        ),
        "target_profile_primitive_validators_candidate": (
            target_profile_primitive_validators_candidate
        ),
        "target_profile_failure_primitive_candidate": (
            target_profile_failure_primitive_candidate
        ),
        "target_profile_report_schema_candidate": (
            target_profile_report_schema_candidate
        ),
        "target_profile_model_schemas_candidate": (
            target_profile_model_schemas_candidate
        ),
        "target_profile_record_model_schemas_candidate": (
            target_profile_record_model_schemas_candidate
        ),
        "target_profile_result_model_schemas_candidate": (
            target_profile_result_model_schemas_candidate
        ),
        "target_selected_profile_result_schemas_candidate": (
            target_selected_profile_result_schemas_candidate
        ),
        "target_profile_record_observation_flow_candidate": (
            target_profile_record_observation_flow_candidate
        ),
        "target_s15_flags_field_candidate": target_s15_flags_field_candidate,
        **configure_inventory,
        "edge_count": edges,
        "module_count": len(modules),
        "module_rows_sha256": rows_sha256,
        "module_body_candidate_count": len(module_body),
        "module_body_edge_count": module_body_edges,
        "module_body_scope": "MODULE_AND_CLASS_BODIES_ONLY",
        "module_body_rows_sha256": module_body_sha256,
        "target_platform_candidate_count": len(target_platform),
        "target_platform_source_candidates": _module_source_rows(files, target_platform),
        "target_platform_edge_count": target_edges,
        "target_platform_scope": "MODULE_CLASS_AND_KNOWN_LINUX_CPYTHON312_IF_BUILTIN_AND_IMPORTED_MODULE_NAME_BRANCHES",
        "target_platform_rows_sha256": target_sha256,
        "target_platform_resolved_if_count": target_conditions["resolved"],
        "target_platform_unknown_if_count": target_conditions["unknown"],
        "target_platform_unknown_if_conditions": target_unknown_conditions,
        "target_platform_unknown_if_conditions_sha256": target_unknown_conditions_sha256,
        "target_platform_types_descriptor_call_facts": list(
            types_descriptor_call_facts
        ),
        "target_platform_ast_compatibility_call_facts": list(
            ast_compatibility_call_facts
        ),
        "target_platform_ast_source_sha256": _AST_SOURCE_SHA256,
        "target_platform_ast_asdl_sha256": AST_ASDL_SHA256,
        "target_platform_ast_c_sha256": AST_C_SHA256,
        "target_platform_sys_getframe_call_facts": list(sys_getframe_call_facts),
        "target_platform_sys_module_c_sha256": SYS_MODULE_C_SHA256,
        "target_platform_sys_implementation_version_fact": list(
            sys_implementation_version_fact
        ),
        "target_s15_version_field_candidate": (
            target_s15_version_field_candidate
        ),
        "target_platform_sys_implementation_name_fact": list(
            sys_implementation_name_fact
        ),
        "target_s15_implementation_field_candidate": (
            target_s15_implementation_field_candidate
        ),
        "target_platform_sys_implementation_cache_tag_fact": list(
            sys_implementation_cache_tag_fact
        ),
        "target_platform_sys_implementation_multiarch_fact": list(
            sys_implementation_multiarch_fact
        ),
        "target_platform_sys_abiflags_fact": list(sys_abiflags_fact),
        "target_platform_sys_platform_fact": list(sys_platform_fact),
        "target_s15_platform_field_candidate": (
            target_s15_platform_field_candidate
        ),
        "target_s15_installation_tuple_candidate": (
            target_s15_installation_tuple_candidate
        ),
        "target_platform_sys_module_clinic_sha256": SYS_MODULE_CLINIC_SHA256,
        "target_platform_warnings_default_call_facts": list(
            warnings_default_call_facts.items()
        ),
        "target_platform_source_name_fact_modules": list(
            target_imported_name_safe_modules
        ),
        "target_platform_os_name_fact": list(os_name_facts.items()),
        "target_platform_os_function_line_facts": list(
            os_createenviron_line_facts.items()
        ),
        "target_platform_codecs_false_guard_line_facts": list(
            codecs_false_guard_line_facts.items()
        ),
        "target_platform_pickle_buffer_line_facts": list(
            pickle_buffer_line_facts.items()
        ),
        "target_platform_importlib_optimize_line_facts": list(
            target_importlib_optimize_line_facts.items()
        ),
        "target_platform_worker_sys_flag_facts": list(
            target_worker_sys_flag_facts
        ),
        "target_platform_worker_sysconfigdata_environment_fact": list(
            target_worker_sysconfigdata_environment_fact
        ),
        "target_platform_importlib_verbose_line_facts": list(
            target_importlib_verbose_line_facts.items()
        ),
        "target_platform_sysconfig_is_python_build_line_facts": list(
            target_sysconfig_is_python_build_line_facts.items()
        ),
        "target_platform_sysconfig_build_setup_guard_line_facts": list(
            target_sysconfig_build_setup_guard_line_facts.items()
        ),
        "target_platform_sysconfig_venv_prefix_guard_line_facts": list(
            target_sysconfig_venv_prefix_guard_line_facts.items()
        ),
        "target_platform_sysconfig_preferred_scheme_membership_line_facts": list(
            target_sysconfig_preferred_scheme_membership_line_facts.items()
        ),
        "target_platform_sysconfig_posix_init_line_facts": list(
            target_sysconfig_posix_init_line_facts.items()
        ),
        "target_platform_string_template_pattern_guard_line_facts": list(
            target_string_template_pattern_guard_line_facts.items()
        ),
        "target_platform_weakrefset_empty_init_line_facts": list(
            target_weakrefset_empty_init_line_facts.items()
        ),
        "target_platform_copyreg_pickle_callable_line_facts": list(
            target_copyreg_pickle_callable_line_facts.items()
        ),
        "target_platform_copyreg_constructor_observation_facts": [
            {"module": module, "source_path": path, "line": line,
             "decisions": list(decisions),
             "evidence_scope": "STATIC_CPYTHON_CALL_ARGUMENT_FACT",
             "runtime_observation_claimed": False}
            for (module, path, line), decisions
            in target_copyreg_constructor_observation_facts.items()
        ],
        "target_platform_opcode_pseudo_op_condition_facts": [
            {"module": module, "source_path": path, "line": line,
             "decisions": list(decisions),
             "evidence_scope": "STATIC_CPYTHON_CALLSITE_INVENTORY",
             "runtime_observation_claimed": False}
            for (module, path, line), decisions
            in target_opcode_pseudo_op_condition_facts.items()
        ],
        "target_platform_json_encoder_argument_condition_facts": [
            {"module": module, "source_path": path, "line": line,
             "decisions": list(decisions),
             "evidence_scope": "STATIC_IMPORT_CALL_ARGUMENT_FACT",
             "runtime_observation_claimed": False}
            for (module, path, line), decisions
            in target_json_encoder_argument_condition_facts.items()
        ],
        "target_platform_hashlib_name_condition_facts": [
            {"module": module, "source_path": path, "line": line,
             "decisions": list(decisions),
             "evidence_scope": "STATIC_MODULE_INIT_ARGUMENT_DOMAIN",
             "runtime_observation_claimed": False}
            for (module, path, line), decisions
            in target_hashlib_name_condition_facts.items()
        ],
        "target_platform_hashlib_builtin_fallback_file_candidates":
            target_hashlib_builtin_fallback_file_candidates,
        "target_module_init_re_compile_input_candidates":
            target_re_compile_input_candidates,
        "target_module_init_re_compile_tokenizer_input_type_candidates":
            target_re_compile_tokenizer_input_type_candidates,
        "target_platform_functools_lru_cache_condition_facts": [
            {"module": module, "source_path": source_path, "line": line,
             "outcomes": list(outcomes)}
            for (module, source_path, line), outcomes
            in target_functools_lru_cache_condition_facts.items()
        ],
        "target_platform_collections_namedtuple_call_condition_facts": [
            {"module": module, "source_path": source_path, "line": line,
             "outcomes": list(outcomes)}
            for (module, source_path, line), outcomes
            in target_collections_namedtuple_call_condition_facts.items()
        ],
        "target_platform_logging_lock_line_facts": list(
            target_logging_lock_line_facts.items()
        ),
        "target_platform_logging_level_line_facts": list(
            target_logging_level_line_facts.items()
        ),
        "target_platform_collections_namedtuple_rename_line_facts": list(
            target_collections_namedtuple_rename_line_facts.items()
        ),
        "target_platform_collections_namedtuple_string_type_line_facts": list(
            target_collections_namedtuple_string_type_line_facts.items()
        ),
        "target_platform_collections_namedtuple_module_line_facts": list(
            target_collections_namedtuple_module_line_facts.items()
        ),
        "target_platform_os_source_sha256": OS_SOURCE_SHA256,
        "target_platform_posix_module_c_sha256": POSIX_MODULE_C_SHA256,
        "target_platform_posix_module_clinic_sha256": POSIX_MODULE_CLINIC_SHA256,
        "target_platform_os_fspath_call_facts": list(os_fspath_call_facts),
        "target_platform_os_have_functions_call_facts": list(os_have_functions_call_facts),
        "target_platform_posix_build_call_facts": list(posix_build_call_facts),
        "target_platform_threading_os_alias_call_facts": list(
            threading_os_alias_call_facts
        ),
        "target_platform_threading_native_id_name_facts": list(
            threading_native_id_facts.items()
        ),
        "target_platform_threading_crlock_name_facts": list(
            threading_crlock_facts.items()
        ),
        "target_platform_threading_main_constructor_line_facts": list(
            threading_main_constructor_line_facts.items()
        ),
        "target_platform_threading_condition_lock_line_facts": list(
            threading_condition_lock_line_facts.items()
        ),
        "target_platform_threading_sys_excepthook_line_facts": list(
            target_threading_sys_excepthook_line_facts.items()
        ),
        "target_platform_sysconfig_name_facts": list(sysconfig_name_facts.items()),
        "target_profile_no_site_assumption": target_no_site,
        "target_platform_sysconfig_project_base_env_fact": list(
            sysconfig_project_base_env_facts
        ),
        "target_platform_sysconfig_userbase_env_condition_facts": [
            {"module": module, "source_path": source_path, "line": line,
             "outcomes": list(outcomes)}
            for (module, source_path, line), outcomes
            in target_sysconfig_userbase_env_condition_facts.items()
        ],
        "target_platform_importlib_case_platform_facts": list(
            _target_importlib_case_platform_facts(files)
        ),
        "target_profile_no_project_base_override_assumption": (
            target_no_project_base_override
        ),
        "target_profile_no_pythonuserbase_override_assumption": (
            target_no_pythonuserbase_override
        ),
        "target_profile_direct_python312_executable_assumption": (
            target_direct_python312
        ),
        "target_platform_image_save_path_facts": target_image_path_facts,
        "target_platform_sys_path_candidate_facts": target_sys_path_candidate_facts,
        "target_s15_paths_field_candidate": target_s15_paths_field_candidate,
        "target_s15_roots_field_candidate": target_s15_roots_field_candidate,
        "target_s15_inert_zip_field_candidate": (
            target_s15_inert_zip_field_candidate
        ),
        "target_s15_files_field_candidate": target_s15_files_field_candidate,
        "target_s15_prefixes_field_candidate": (
            target_s15_prefixes_field_candidate
        ),
        "target_platform_thread_native_id_source_sha256": {
            "header": THREAD_NATIVE_ID_HEADER_SHA256,
            "module": THREAD_NATIVE_ID_MODULE_SHA256,
            "pthread": THREAD_NATIVE_ID_PTHREAD_SHA256,
        },
        "target_platform_pyconfig_sha256": (
            hashlib.sha256(target_pyconfig_source).hexdigest()
            if target_pyconfig_source is not None else None
        ),
        "target_platform_image_config_sha256": (
            hashlib.sha256(target_image_config_source).hexdigest()
            if target_image_config_source is not None else None
        ),
        "target_platform_image_manifest_sha256": (
            TARGET_IMAGE_MANIFEST_SHA256
            if target_pyconfig_source is not None else None
        ),
        "target_platform_pyconfig_layer_sha256": (
            TARGET_IMAGE_CONFIG_LAYER_SHA256
            if target_pyconfig_source is not None else None
        ),
        "target_platform_types_source_sha256": _TYPES_SOURCE_SHA256,
        "target_platform_inspect_source_sha256": _INSPECT_SOURCE_SHA256,
        "target_platform_builtin_membership": _TARGET_BUILTIN_MEMBERSHIP,
        "target_platform_builtin_module_names": list(_TARGET_BUILTIN_MODULE_NAMES),
        "target_platform_builtin_config_c_sha256": _TARGET_BUILTIN_CONFIG_C_SHA256,
        "target_platform_builtin_layer_sha256": _TARGET_BUILTIN_LAYER_SHA256,
        "module_init_call_candidate_count": len(call_modules),
        "module_init_call_source_candidates": _module_source_rows(files, call_modules),
        "module_init_call_edge_count": call_edges,
        "module_init_call_function_count": call_functions,
        "module_init_call_roots_outside_source_stdlib_names": list(
            call_roots_outside_stdlib
        ),
        "module_init_call_scope": "MODULE_CLASS_CALLS_SIMPLE_ALIASES_GENERATORS_IMPORTED_FUNCTIONS_MODULE_ALIASES_FROM_IMPORT_IMPORTED_CLASS_METHODS_DIRECT_CONSTRUCTED_METHODS_SAME_SCOPE_INSTANCE_BINDINGS_INSTANCE_ALIASES_BOUND_RECEIVER_METHODS_NESTED_RECEIVER_CLOSURES_INHERITED_RECEIVER_METHODS_AND_TRANSITIVE_LOCAL_BASES_AND_IMPORTED_SOURCE_BASES_AND_BASE_ALIASES_AND_ZERO_ARG_AND_EXPLICIT_LOCAL_SUPER_METHODS_AND_INHERITED_CONSTRUCTORS_AND_CONSTRUCTED_INHERITED_METHODS_AND_IMPORTED_SOURCE_SUBCLASS_DISPATCH_SAME_MODULE_AND_IMPORTED_SOURCE_BASE_DISPATCH_AND_SIMPLE_IMPORTED_CLASS_ALIASES_AND_QUALIFIED_IMPORTED_CLASS_ALIASES_AND_LOCAL_CLASS_ALIASES_AND_DIRECT_FUNCTION_AND_CLASS_SCOPE_IMPORTED_CLASS_ALIASES_AND_CALLED_NESTED_FUNCTION_CLASS_ALIAS_CLOSURES_AND_DIRECT_TOP_LEVEL_FACTORY_RETURNS_AFTER_IMPORTS_AND_DOCSTRINGS_AND_SIMPLE_LOCAL_INSTANCE_ASSIGNMENTS",
        "module_init_call_rows_sha256": call_sha256,
        "module_init_call_resolved_if_count": call_conditions["resolved"],
        "module_init_call_unknown_if_count": call_conditions["unknown"],
        "target_module_init_call_candidate_count": len(target_call_modules),
        "target_module_init_call_source_candidates": _module_source_rows(
            files, target_call_modules
        ),
        "target_module_init_call_edge_count": target_call_edges,
        "target_module_init_call_function_count": target_call_functions,
        "target_module_init_call_rows_sha256": target_call_sha256,
        "target_module_init_call_resolved_if_count": target_call_conditions["resolved"],
        "target_module_init_call_resolved_if_conditions": target_call_resolved_conditions,
        "target_module_init_call_resolved_if_conditions_sha256": hashlib.sha256(
            json.dumps(
                target_call_resolved_conditions, ensure_ascii=False, sort_keys=True,
                separators=(",", ":"),
            ).encode("utf-8")
        ).hexdigest(),
        "target_module_init_call_unknown_if_count": target_call_conditions["unknown"],
        "target_module_init_call_unknown_if_conditions": target_call_unknown_conditions,
        "target_module_init_call_unknown_if_conditions_sha256": (
            target_call_unknown_conditions_sha256
        ),
        "target_module_init_call_empty_for_facts": [
            {"module": module, "line": line, "iterator": iterator}
            for module, facts in sorted(target_warning_options_empty_for_facts.items())
            for line, iterator in sorted(facts.items())
        ],
        "roots": list(ROOTS),
        "scope": "LEXICAL_SOURCE_CANDIDATES_ONLY",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("archive", type=Path, help="signaturgeprüftes CPython-3.12.16-Quellarchiv")
    parser.add_argument(
        "--target-pyconfig", type=Path,
        help="Digest-geprüfte pyconfig.h aus dem ausgewählten CPython-Zielimage",
    )
    parser.add_argument(
        "--target-no-site", action="store_true",
        help="Annahme für die feste Zielroute: CPython wird mit -S gestartet",
    )
    parser.add_argument(
        "--target-image-config", type=Path,
        help="Digest-geprüfte OCI-Config des ausgewählten CPython-Zielimages",
    )
    parser.add_argument(
        "--target-no-project-base-override", action="store_true",
        help="Annahme für die feste Zielroute: kein Override für _PYTHON_PROJECT_BASE",
    )
    parser.add_argument(
        "--target-no-pythonuserbase-override", action="store_true",
        help="Annahme für die feste Zielroute: PYTHONUSERBASE ist nicht gesetzt",
    )
    parser.add_argument(
        "--target-image-save", type=Path,
        help="Digest- und DiffID-geprüfter Docker-save-Tarball des Zielimages",
    )
    parser.add_argument(
        "--target-direct-python312", action="store_true",
        help="Aufrufannahme: sys.executable verweist auf /usr/local/bin/python3.12",
    )
    args = parser.parse_args()
    if args.target_no_site and args.target_pyconfig is None:
        parser.error("--target-no-site requires --target-pyconfig")
    if args.target_no_project_base_override and args.target_image_config is None:
        parser.error("--target-no-project-base-override requires --target-image-config")
    if args.target_no_pythonuserbase_override and args.target_image_config is None:
        parser.error("--target-no-pythonuserbase-override requires --target-image-config")
    if args.target_direct_python312 and args.target_image_save is None:
        parser.error("--target-direct-python312 requires --target-image-save")
    try:
        result = analyze(args.archive, args.target_pyconfig, args.target_no_site,
                         args.target_image_config,
                         args.target_no_project_base_override,
                         args.target_image_save,
                         args.target_direct_python312,
                         args.target_no_pythonuserbase_override)
    except (OSError, tarfile.TarError, UnicodeError, SyntaxError, ValueError):
        print(json.dumps({"status": "NOT_PROVEN", "issue": "SOURCE_INPUT_REJECTED"},
                         separators=(",", ":")))
        return 1
    print(json.dumps({"status": "CANDIDATES_ONLY", **result}, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
