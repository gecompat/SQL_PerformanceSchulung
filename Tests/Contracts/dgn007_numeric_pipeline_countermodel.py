"""Reine skalare numerische Gegenprobe; ausschließlich PROJECT_SEMANTIC.

Oraclewerte, deklarierte gerundete Fragmentmittel und synthetische Style3-Texte
sind unabhängige GIVEN-Eingaben. Keine SQL-/Floatkonversion wird emuliert oder
attestiert. Indices bezeichnen nur Modellwerte, keine QS-Ausführungsidentitäten.
Fraction rechnet den gegebenen Decimaltext exakt, rekonstruiert aber keine
verlorene Enginepräzision. Die Grenzen 16/64/256 sind technische Modellgrenzen,
keine v1-/SQL-Bounds. Kein Epsilon, Methodenentscheid oder Herkunftsnachweis.
"""

from dataclasses import dataclass, field
from decimal import Decimal
from enum import Enum
from fractions import Fraction
from math import gcd
import re


MAX_VALUES = 16
MAX_FRAGMENTS = 16
MAX_TEXT = 64
MAX_RATIONAL_BITS = 256
_TEXT = re.compile(r"(?:0|[1-9][0-9]*)(?:\.[0-9]+)?(?:[eE]([+-]?[0-9]{1,3}))?", re.ASCII)


class Issue(Enum):
    INVALID_RECORD = "INVALID_RECORD"
    INVALID_TEXT = "INVALID_TEXT"
    INVALID_PARTITION = "INVALID_PARTITION"


@dataclass(frozen=True)
class Fragment:
    indices: tuple[int, ...]
    declared_rounded_mean: Fraction
    synthetic_style3_text: str


@dataclass(frozen=True)
class FragmentResult:
    indices: tuple[int, ...]
    count: int
    oracle_mean: Fraction
    declared_rounded_mean: Fraction
    given_text_mean: Fraction
    rounded_minus_oracle: Fraction
    text_minus_rounded: Fraction
    text_minus_oracle: Fraction


@dataclass(frozen=True)
class Report:
    valid_model: bool
    issues: tuple[Issue, ...]
    count: int | None = None
    oracle_mean: Fraction | None = None
    rounded_weighted_mean: Fraction | None = None
    consumer_weighted_mean: Fraction | None = None
    rounded_minus_oracle: Fraction | None = None
    text_minus_rounded: Fraction | None = None
    consumer_minus_oracle: Fraction | None = None
    oracle_matches_consumer: bool | None = None
    fragments: tuple[FragmentResult, ...] = ()
    scope: str = field(default="PROJECT_SEMANTIC", init=False)
    text_origin: str = field(default="GIVEN_SYNTHETIC", init=False)
    runtime_attested: bool = field(default=False, init=False)
    method_approved: bool = field(default=False, init=False)
    sql_conversion_emulated: bool = field(default=False, init=False)


def _rational(value):
    if type(value) is not Fraction:
        return False
    numerator = getattr(value, "numerator", None)
    denominator = getattr(value, "denominator", None)
    return (type(numerator) is int and type(denominator) is int
            and numerator >= 0 and denominator > 0
            and numerator.bit_length() <= MAX_RATIONAL_BITS
            and denominator.bit_length() <= MAX_RATIONAL_BITS
            and gcd(numerator, denominator) == 1)


def _given_text(value):
    # Bound text and exponent BEFORE Decimal/Fraction construction; no float path.
    if type(value) is not str or not 0 < len(value) <= MAX_TEXT:
        return None
    match = _TEXT.fullmatch(value)
    if match is None or (match.group(1) is not None and not -30 <= int(match.group(1)) <= 20):
        return None
    mantissa = re.split("[eE]", value)[0]
    if sum(char.isdigit() for char in mantissa) > 34:
        return None
    parsed = Decimal(value)
    representation = parsed.as_tuple()
    if (not parsed.is_finite() or parsed < 0 or representation.exponent < -30
            or parsed.adjusted() > 20):
        return None
    result = Fraction(parsed)
    return result if _rational(result) else None


def analyze_partition(oracle_values, fragments) -> Report:
    """Eine vollständige endliche Partition prüfen, dann alle Ebenen vergleichen.

    valid_model bezeichnet nur wohlgeformte synthetische Eingaben, keine positive
    SQL-Stabilitätsregel. Abweichungen sind gültige Ergebnisse dieser Gegenprobe.
    Ein Text muss nicht dem deklarierten gerundeten Mittel entsprechen; dessen
    Unterschied bleibt als eigenes Delta erhalten. Keine Eingabedaten ergänzen.
    """
    if (type(oracle_values) is not tuple or not 1 <= len(oracle_values) <= MAX_VALUES
            or not all(_rational(value) for value in oracle_values)
            or type(fragments) is not tuple or not 1 <= len(fragments) <= MAX_FRAGMENTS):
        return Report(False, (Issue.INVALID_RECORD,))
    for fragment in fragments:
        if (type(fragment) is not Fragment or set(vars(fragment)) != set(Fragment.__dataclass_fields__)
                or type(fragment.indices) is not tuple or not 1 <= len(fragment.indices) <= MAX_VALUES
                or not all(type(index) is int for index in fragment.indices)
                or not _rational(fragment.declared_rounded_mean)):
            return Report(False, (Issue.INVALID_RECORD,))
    # Reject unbounded foreign integer indices before hashing or indexing them.
    if any(not 0 <= index < len(oracle_values) for fragment in fragments for index in fragment.indices):
        return Report(False, (Issue.INVALID_PARTITION,))
    texts = tuple(_given_text(fragment.synthetic_style3_text) for fragment in fragments)
    if any(text is None for text in texts):
        return Report(False, (Issue.INVALID_TEXT,))
    indices = tuple(index for fragment in fragments for index in fragment.indices)
    if (len(indices) != len(oracle_values) or len(set(indices)) != len(indices)
            or set(indices) != set(range(len(oracle_values)))):
        return Report(False, (Issue.INVALID_PARTITION,))
    count = len(oracle_values)
    oracle = sum(oracle_values, Fraction(0)) / count
    rounded = sum((fragment.declared_rounded_mean * len(fragment.indices)
                   for fragment in fragments), Fraction(0)) / count
    consumer = sum((text * len(fragment.indices) for text, fragment in zip(texts, fragments)), Fraction(0)) / count
    results = []
    for fragment, text in zip(fragments, texts):
        local_oracle = sum((oracle_values[index] for index in fragment.indices), Fraction(0)) / len(fragment.indices)
        results.append(FragmentResult(fragment.indices, len(fragment.indices), local_oracle,
                                      fragment.declared_rounded_mean, text,
                                      fragment.declared_rounded_mean - local_oracle,
                                      text - fragment.declared_rounded_mean, text - local_oracle))
    return Report(True, (), count, oracle, rounded, consumer, rounded - oracle,
                  consumer - rounded, consumer - oracle, oracle == consumer, tuple(results))
