"""Evaluator for the condition strings in config/rules.yaml (classification cascade).

Grammar (precedence: not > and > or):

    expr       := or_expr
    or_expr    := and_expr ("or" and_expr)*
    and_expr   := not_expr ("and" not_expr)*
    not_expr   := "not" not_expr | comparison
    comparison := operand (("<" | "<=" | ">" | ">=" | "==" | "!=") value | "in" list)?
    operand    := feature | threshold_ref | number | "(" expr ")"
    value      := operand | word            (a bare word after ==/!= is a text literal, e.g. high)
    list       := "[" word ("," word)* "]"
    threshold_ref := thresholds.<name> | required_width.<name>

Missing values use three-valued (Kleene) logic, rule C-MISS-01: a comparison with a missing value is
unknown (None); `a or b` is true if one side is true, `a and b` is false if one side is false.

Every result carries a confidence level (rule C-CONF-01). Only inputs that determine the result count:
- missing input on which the result depends -> LOW
- numeric comparison with a threshold reference within ±near_threshold of the threshold -> LOW
- input from a fallback source (or a default for a missing value) -> MEDIUM
- `or` that is true takes the best true operand; `and` that is false takes the best false operand;
  otherwise the worst operand counts.
"""

import math
import re
from dataclasses import dataclass, field
from typing import Any, Callable

import numpy as np
import pandas as pd

LOW, MEDIUM, HIGH = 0, 1, 2
CONFIDENCE_LABELS = {LOW: "niedrig", MEDIUM: "mittel", HIGH: "hoch"}

_TOKEN = re.compile(r"\s*(?:(<=|>=|==|!=|<|>|\[|\]|\(|\)|,)|(-?\d+(?:\.\d+)?)|([A-Za-z_][A-Za-z0-9_.]*))")
_REF_SECTIONS = ("thresholds", "required_width")


class ExprError(ValueError):
    pass


@dataclass
class Result:
    value: Any                      # True / False / None (unknown) or a number/text for operands
    confidence: int = HIGH
    reasons: list[str] = field(default_factory=list)


@dataclass
class Context:
    """Inputs for one evaluation."""
    values: dict[str, Any]                      # feature values; None = missing
    resolve_ref: Callable[[str], float]          # thresholds.x / required_width.x -> number
    near_threshold: float                        # relative distance counted as "near" (0.1 = ±10 %)
    fallback: set[str] = field(default_factory=set)   # features from a fallback source or default
    used: dict[str, Any] = field(default_factory=dict)  # filled during evaluation (trace inputs)


# --- AST ------------------------------------------------------------------------------------


@dataclass(frozen=True)
class Feature:
    name: str


@dataclass(frozen=True)
class Ref:
    name: str  # e.g. thresholds.conn_gow


@dataclass(frozen=True)
class Literal:
    value: Any


@dataclass(frozen=True)
class Compare:
    op: str
    left: Any
    right: Any


@dataclass(frozen=True)
class InList:
    item: Any
    options: tuple


@dataclass(frozen=True)
class Not:
    operand: Any


@dataclass(frozen=True)
class BoolOp:
    op: str  # and | or
    operands: tuple


def _tokenize(text: str) -> list[str]:
    tokens, pos = [], 0
    text = text.rstrip()
    while pos < len(text):
        m = _TOKEN.match(text, pos)
        if not m or m.end() == pos:
            raise ExprError(f"cannot parse {text!r} at position {pos}")
        tokens.append(next(g for g in m.groups() if g is not None))
        pos = m.end()
    return tokens


class _Parser:
    def __init__(self, text: str):
        self.text = text
        self.tokens = _tokenize(text)
        self.i = 0

    def peek(self) -> str | None:
        return self.tokens[self.i] if self.i < len(self.tokens) else None

    def take(self, expected: str | None = None) -> str:
        tok = self.peek()
        if tok is None or (expected is not None and tok != expected):
            raise ExprError(f"{self.text!r}: expected {expected or 'token'}, got {tok!r}")
        self.i += 1
        return tok

    def parse(self):
        node = self.or_expr()
        if self.peek() is not None:
            raise ExprError(f"{self.text!r}: unexpected {self.peek()!r}")
        return node

    def or_expr(self):
        parts = [self.and_expr()]
        while self.peek() == "or":
            self.take()
            parts.append(self.and_expr())
        return parts[0] if len(parts) == 1 else BoolOp("or", tuple(parts))

    def and_expr(self):
        parts = [self.not_expr()]
        while self.peek() == "and":
            self.take()
            parts.append(self.not_expr())
        return parts[0] if len(parts) == 1 else BoolOp("and", tuple(parts))

    def not_expr(self):
        if self.peek() == "not":
            self.take()
            return Not(self.not_expr())
        return self.comparison()

    def comparison(self):
        left = self.operand()
        tok = self.peek()
        if tok in ("<", "<=", ">", ">=", "==", "!="):
            self.take()
            right = self.operand(word_is_literal=tok in ("==", "!="))
            return Compare(tok, left, right)
        if tok == "in":
            self.take()
            self.take("[")
            options = [self.take()]
            while self.peek() == ",":
                self.take()
                options.append(self.take())
            self.take("]")
            return InList(left, tuple(options))
        return left

    def operand(self, word_is_literal: bool = False):
        tok = self.take()
        if tok == "(":
            node = self.or_expr()
            self.take(")")
            return node
        if re.fullmatch(r"-?\d+(?:\.\d+)?", tok):
            return Literal(float(tok))
        if tok in ("and", "or", "not", "in") or not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_.]*", tok):
            raise ExprError(f"{self.text!r}: unexpected {tok!r}")
        if "." in tok:
            if tok.split(".", 1)[0] not in _REF_SECTIONS:
                raise ExprError(f"{self.text!r}: unknown reference {tok!r}")
            return Ref(tok)
        if tok in ("true", "false"):
            return Literal(tok == "true")
        return Literal(tok) if word_is_literal else Feature(tok)


def parse(text: str):
    """Parse a condition into an AST (raises ExprError)."""
    return _Parser(text).parse()


def features_in(node) -> set[str]:
    if isinstance(node, Feature):
        return {node.name}
    if isinstance(node, Compare):
        return features_in(node.left) | features_in(node.right)
    if isinstance(node, InList):
        return features_in(node.item)
    if isinstance(node, Not):
        return features_in(node.operand)
    if isinstance(node, BoolOp):
        return set().union(*(features_in(o) for o in node.operands))
    return set()


# --- evaluation -----------------------------------------------------------------------------


def is_missing(v: Any) -> bool:
    """None, NaN, pd.NA or a missing numpy/pandas scalar."""
    if v is None or v is pd.NA:
        return True
    if isinstance(v, float):
        return math.isnan(v)
    if isinstance(v, np.generic):
        return bool(pd.isna(v))
    return False


def _leaf(node, ctx: Context) -> Result:
    if isinstance(node, Literal):
        return Result(node.value)
    if isinstance(node, Ref):
        return Result(float(ctx.resolve_ref(node.name)))
    name = node.name
    v = ctx.values.get(name)
    if is_missing(v):
        ctx.used[name] = None
        return Result(None, LOW, [f"fehlt:{name}"])
    ctx.used[name] = v
    if name in ctx.fallback:
        return Result(v, MEDIUM, [f"fallback:{name}"])
    return Result(v)


def _merge(results: list[Result]) -> tuple[int, list[str]]:
    conf = min(r.confidence for r in results)
    reasons = [x for r in results for x in r.reasons]
    return conf, list(dict.fromkeys(reasons))


def _compare(op: str, a: Any, b: Any) -> bool:
    if op == "==":
        return a == b
    if op == "!=":
        return a != b
    a, b = float(a), float(b)
    return {"<": a < b, "<=": a <= b, ">": a > b, ">=": a >= b}[op]


def evaluate(node, ctx: Context) -> Result:
    if isinstance(node, (Literal, Ref, Feature)):
        return _leaf(node, ctx)

    if isinstance(node, Compare):
        left, right = evaluate(node.left, ctx), evaluate(node.right, ctx)
        conf, reasons = _merge([left, right])
        if left.value is None or right.value is None:
            return Result(None, LOW, reasons)
        value = _compare(node.op, left.value, right.value)
        # C-CONF-01: value within ±near_threshold of a threshold reference.
        for side, other in ((node.left, node.right), (node.right, node.left)):
            if isinstance(side, Ref) and isinstance(other, Feature):
                t = float(ctx.resolve_ref(side.name))
                x = float(ctx.values[other.name])
                if t != 0 and abs(x - t) <= ctx.near_threshold * abs(t) + 1e-12:
                    conf = LOW
                    reasons.append(f"nahe_schwelle:{other.name}~{side.name}")
        return Result(value, conf, reasons)

    if isinstance(node, InList):
        item = evaluate(node.item, ctx)
        if item.value is None:
            return Result(None, LOW, item.reasons)
        return Result(str(item.value) in node.options, item.confidence, item.reasons)

    if isinstance(node, Not):
        r = evaluate(node.operand, ctx)
        return Result(None if r.value is None else not bool(r.value), r.confidence, r.reasons)

    if isinstance(node, BoolOp):
        results = [evaluate(o, ctx) for o in node.operands]
        return combine(node.op, results)

    raise ExprError(f"unknown node {node!r}")


def combine(op: str, results: list[Result]) -> Result:
    """Kleene and/or; confidence from the operands that determine the result."""
    values = [None if r.value is None else bool(r.value) for r in results]
    decisive = op == "or"  # True decides an or, False decides an and
    deciding = [r for r, v in zip(results, values) if v is decisive]
    if deciding:
        best = max(deciding, key=lambda r: r.confidence)
        return Result(decisive, best.confidence, list(best.reasons))
    conf, reasons = _merge(results)
    if any(v is None for v in values):
        return Result(None, LOW, reasons)
    return Result(not decisive, conf, reasons)


def label(conf: int) -> str:
    return CONFIDENCE_LABELS[conf]


def clean_value(v: Any) -> Any:
    """JSON-friendly value for rule_trace (numpy/pandas scalars, rounded floats, None for missing)."""
    if is_missing(v):
        return None
    if hasattr(v, "item"):
        v = v.item()
    if isinstance(v, float):
        return round(v, 4) if math.isfinite(v) else None
    return v
